#!/usr/bin/env python3
"""Partition Leo's five OOM-prone tables into hive-style monthly dirs.

Default: **dry-run** (plan only). Writes ONLY under data/v2_partitioned/ — never
overwrites the source flat parquet. Does not touch promotion_approved.

Usage:
  python3 scripts/partition_oom_tables_to_hive.py              # dry-run all five
  python3 scripts/partition_oom_tables_to_hive.py --apply --only daily_basic_full
  python3 scripts/partition_oom_tables_to_hive.py --apply --sample-months 1  # tiny smoke

Requires free disk ≈ source size. Safe to interrupt; resumes by skipping existing month dirs
unless --force.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.dataset as ds
import pyarrow.parquet as pq

ROOT = Path("/workspace/QuantLab")
OUT_ROOT = ROOT / "data" / "v2_partitioned"

TABLES = {
    "daily_basic_full": {
        "src": ROOT / "data/v2/valuation/daily_basic_full_tushare.parquet",
        "date_col": "trade_date",
        "out": OUT_ROOT / "daily_basic_full",
    },
    "float_mktcap": {
        "src": ROOT / "data/v2/float_mktcap/float_mktcap_daily_tushare.parquet",
        "date_col": "trade_date",
        "out": OUT_ROOT / "float_mktcap",
    },
    "ep_pit_daily": {
        "src": ROOT / "data/v2/ep/ep_pit_daily_tushare.parquet",
        "date_col": "trade_date",
        "out": OUT_ROOT / "ep_pit_daily",
    },
    "margin_detail": {
        "src": ROOT / "data/v2/margin/margin_detail_daily_2018plus.parquet",
        "date_col": "trade_date",
        "out": OUT_ROOT / "margin_detail",
    },
    "share_float_pit": {
        "src": ROOT / "data/v2/share_float/share_float_pit.parquet",
        "date_col": "float_date",
        "out": OUT_ROOT / "share_float_pit",
    },
}


def _ymd_series(col: pa.Array) -> pa.Array:
    """Normalize date-like column to YYYYMMDD large_string."""
    t = col.type
    if pa.types.is_timestamp(t) or pa.types.is_date(t):
        # strftime via pandas is heavy; use compute for date32-like
        # Cast timestamp -> date32 then format manually with compute
        if pa.types.is_timestamp(t):
            # extract y/m/d
            # pyarrow  doesn't have strftime on all builds; use pandas on the *filtered month batch* only
            return None  # signal caller to use pandas path for month key
        return None
    # string / int
    if pa.types.is_integer(t):
        return pc.utf8_slice_codeunits(pc.cast(col, pa.string()), 0, 8)
    # string
    s = pc.cast(col, pa.string()) if not pa.types.is_string(t) and not pa.types.is_large_string(t) else col
    # strip non-digits lightly: assume already YYYYMMDD or YYYY-MM-DD
    return s


def _month_keys_via_pandas(table: pa.Table, date_col: str) -> list[str]:
    import pandas as pd

    s = table.column(date_col).to_pandas()
    if pd.api.types.is_datetime64_any_dtype(s):
        return sorted({ts.strftime("%Y%m") for ts in s.dropna().unique()})
    out = set()
    for v in s.dropna().unique():
        digits = "".join(ch for ch in str(v) if ch.isdigit())
        if len(digits) >= 6:
            out.add(digits[:6])
    return sorted(out)


def _filter_month(dataset: ds.Dataset, date_col: str, yyyymm: str) -> pa.Table:
    """Read one calendar month with pyarrow filter (type-aware)."""
    schema = dataset.schema
    arrow_type = schema.field(date_col).type
    y, m = int(yyyymm[:4]), int(yyyymm[4:6])
    if m == 12:
        y2, m2 = y + 1, 1
    else:
        y2, m2 = y, m + 1

    field = ds.field(date_col)
    if pa.types.is_timestamp(arrow_type):
        lo = datetime(y, m, 1)
        hi = datetime(y2, m2, 1)
        unit = arrow_type.unit
        tz = arrow_type.tz
        filt = (field >= pa.scalar(lo, type=pa.timestamp(unit, tz=tz))) & (
            field < pa.scalar(hi, type=pa.timestamp(unit, tz=tz))
        )
    elif pa.types.is_integer(arrow_type):
        lo = y * 10000 + m * 100 + 1
        hi = y2 * 10000 + m2 * 100 + 1
        filt = (field >= lo) & (field < hi)
    else:
        # string YYYYMMDD
        lo = f"{yyyymm}01"
        hi = f"{y2:04d}{m2:02d}01"
        filt = (field >= lo) & (field < hi)
    return dataset.to_table(filter=filt)


def plan_one(name: str, cfg: dict) -> dict:
    src: Path = cfg["src"]
    if not src.exists():
        return {"id": name, "ok": False, "error": f"missing {src}"}
    pf = pq.ParquetFile(src)
    size = src.stat().st_size
    # Discover months without full pandas: sample row-group stats when possible
    months: list[str] = []
    date_col = cfg["date_col"]
    # Fast path: scan unique months via dataset + chunked unique (memory heavy on huge)
    # Instead: use row group min/max if statistics present, else one lightweight pass
    md = pf.metadata
    mins, maxs = [], []
    for i in range(md.num_row_groups):
        rg = md.row_group(i)
        for j in range(rg.num_columns):
            col = rg.column(j)
            if col.path_in_schema == date_col and col.statistics and col.statistics.has_min_max:
                mins.append(col.statistics.min)
                maxs.append(col.statistics.max)
    month_set = set()
    if mins and maxs:
        # expand from global min/max only → list all months in range (safe for contiguous calendars)
        import pandas as pd

        def to_period(v):
            if hasattr(v, "strftime"):
                return pd.Timestamp(v).to_period("M")
            digits = "".join(ch for ch in str(v) if ch.isdigit())
            return pd.Period(digits[:6], freq="M")

        p0 = to_period(min(mins))
        p1 = to_period(max(maxs))
        cur = p0
        while cur <= p1:
            month_set.add(str(cur).replace("-", ""))
            cur += 1
        months = sorted(month_set)
        month_discovery = "row_group_stats_range"
    else:
        # fallback under low memory: expand from known catalog-ish bounds via file name / first last row group
        # read only first & last row-group date column
        import pandas as pd
        def rg_extreme(rg_i, which):
            rg = md.row_group(rg_i)
            # find col index
            for j in range(rg.num_columns):
                if rg.column(j).path_in_schema == date_col:
                    # read that column only via dataset slice is hard; use pq read_row_group
                    tbl = pf.read_row_group(rg_i, columns=[date_col])
                    s = tbl.column(0).to_pandas().dropna()
                    if s.empty:
                        return None
                    return s.min() if which == "min" else s.max()
            return None
        vmin = rg_extreme(0, "min")
        vmax = rg_extreme(md.num_row_groups - 1, "max")
        if vmin is None or vmax is None:
            return {"id": name, "ok": False, "error": "cannot discover months (no stats)"}
        def to_period(v):
            if hasattr(v, "strftime"):
                return pd.Timestamp(v).to_period("M")
            digits = "".join(ch for ch in str(v) if ch.isdigit())
            return pd.Period(digits[:6], freq="M")
        p0, p1 = to_period(vmin), to_period(vmax)
        cur = p0
        while cur <= p1:
            month_set.add(str(cur).replace("-", ""))
            cur += 1
        months = sorted(month_set)
        month_discovery = "first_last_row_group"

    return {
        "id": name,
        "ok": True,
        "src": str(src),
        "out": str(cfg["out"]),
        "date_col": date_col,
        "rows": pf.metadata.num_rows,
        "bytes": size,
        "n_months": len(months),
        "months_head": months[:3],
        "months_tail": months[-3:],
        "months": months,
        "month_discovery": month_discovery,
        "hive_example": f"{cfg['out'].name}/ym={months[-1] if months else 'YYYYMM'}/part-0.parquet",
        "partition_dirname": "ym",
    }


def apply_one(name: str, cfg: dict, months: list[str], *, force: bool, sample_months: int | None) -> dict:
    src = cfg["src"]
    out: Path = cfg["out"]
    date_col = cfg["date_col"]
    dataset = ds.dataset(str(src), format="parquet")
    if sample_months:
        months = months[-sample_months:]
    out.mkdir(parents=True, exist_ok=True)
    written = []
    skipped = []
    t0 = time.time()
    for yyyymm in months:
        part_dir = out / f"ym={yyyymm}"
        part_file = part_dir / "part-0.parquet"
        if part_file.exists() and not force:
            skipped.append(yyyymm)
            continue
        table = _filter_month(dataset, date_col, yyyymm)
        if table.num_rows == 0:
            skipped.append(yyyymm)
            continue
        part_dir.mkdir(parents=True, exist_ok=True)
        tmp = part_dir / "part-0.parquet.tmp"
        pq.write_table(table, tmp, compression="zstd")
        os.replace(tmp, part_file)
        written.append({"month": yyyymm, "rows": table.num_rows, "bytes": part_file.stat().st_size})
        print(f"  WRITE {name} {yyyymm} rows={table.num_rows}", flush=True)
    # manifest
    man = {
        "id": name,
        "source": str(src),
        "partition_key": date_col,
        "partition_dirname": "ym",
        "granularity": "YYYYMM",
        "written": written,
        "skipped_existing_or_empty": skipped,
        "elapsed_sec": round(time.time() - t0, 2),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "note": "Source flat parquet untouched. Point catalog partitioned_path here when complete.",
    }
    (out / "_partition_manifest.json").write_text(json.dumps(man, ensure_ascii=False, indent=2))
    return man


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="actually write partitioned files (default dry-run)")
    ap.add_argument("--only", nargs="*", default=None, help="subset of table ids")
    ap.add_argument("--force", action="store_true", help="overwrite existing month parts")
    ap.add_argument("--sample-months", type=int, default=None, help="only last N months (smoke)")
    ap.add_argument("--json-out", default=str(ROOT / "output/partition_oom_plan.json"))
    args = ap.parse_args(argv)

    ids = args.only or list(TABLES.keys())
    plans = []
    for name in ids:
        if name not in TABLES:
            print("unknown", name, file=sys.stderr)
            continue
        print("PLAN", name, flush=True)
        plans.append(plan_one(name, TABLES[name]))

    report = {
        "mode": "apply" if args.apply else "dry-run",
        "tables": plans,
        "out_root": str(OUT_ROOT),
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    if args.apply:
        applies = []
        for pl in plans:
            if not pl.get("ok"):
                continue
            name = pl["id"]
            print("APPLY", name, "months", pl["n_months"], flush=True)
            applies.append(
                apply_one(
                    name,
                    TABLES[name],
                    pl["months"],
                    force=args.force,
                    sample_months=args.sample_months,
                )
            )
        report["applies"] = applies

    outp = Path(args.json_out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    # shrink months list in saved plan for readability
    slim = json.loads(json.dumps(report))
    for t in slim.get("tables", []):
        if "months" in t and len(t["months"]) > 12:
            t["months_omitted"] = len(t["months"]) - 6
            t["months"] = t["months"][:3] + ["..."] + t["months"][-3:]
    outp.write_text(json.dumps(slim, ensure_ascii=False, indent=2))
    print(json.dumps({k: slim[k] for k in ("mode", "out_root", "created_at")}, indent=2))
    print("wrote", outp)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
