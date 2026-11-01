#!/usr/bin/env python3
"""Leaf25 full-factor mem_probe r3 — PIT end_date filter type fix (timestamp).

SUPERSEDES r2 real-path for calibrated peak measurement after r2 FAIL.
r2 FAIL receipt sha8 d01f95c0 (ArrowNotImplementedError: greater_equal
timestamp[us] vs string YYYYMMDD in _read_pit_projected). Main order:
docs/v2/audit/MAIN_LEAF25_MEM_PROBE_R2_FAIL_R3_ORDER_20261025_ZH.md.
Reuses leaf25_full_factor_chunk_plan_r1; does NOT modify r5 / r1 / r2 file.
Ban reuse r2 .ok cd230f9c… and step_m1 .ok 1c32ab1e….

HARD RULES:
  - Default --dry-run. Real PIT path requires --allow-real-data + existing --arch-ok-path.
  - Ban reuse step_m1 .ok 1c32ab1e… and r2 probe .ok cd230f9c….
  - C4/stop/hard: 1331200 / 1484800 / 1536000 kB; ban raise; >=0.85*C4 exit 94; >=hard exit 95.
  - Sampler / sample-dir: /tmp/quantlab_* only.
  - Ban whole-window densify; HI_LIQ single chunk; missing HI_LIQ mask → STOP (no silent FULLA).
  - Alpha here is a crude accrual/zscore proxy for MEM peak only — NOT full-leaf CFACC.
  - live=false; promotion_approved=false. Do not apply for X2 .ok from this package alone.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import resource
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

try:
    import leaf25_full_factor_chunk_plan_r1 as chunk_plan_mod
except ImportError:  # pragma: no cover
    chunk_plan_mod = None  # type: ignore

ET = ZoneInfo("America/New_York")
SH = ZoneInfo("Asia/Shanghai")
ROOT = Path(__file__).resolve().parents[1]

C4_KB = 1331200
STOP_KB = 1484800
HARD_KB = 1536000
SPLIT_THRESH_KB = int(0.85 * C4_KB)  # 1131520
BANNED_OK_SHA = "1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0"
# r2 single_use .ok (FAIL receipt d01f95c0…) — VOID pending; ban reuse for r3
BANNED_OK_SHA_R2 = "cd230f9c2aa9fc8de7fc538fb1f04ded8d9c20463f24b88b6c0f76950ec34279"
BANNED_OK_SHAS = frozenset({BANNED_OK_SHA, BANNED_OK_SHA_R2})

FP = ROOT / "data/v2/financials_pit"
PIT_INPUTS = {
    "income": (
        FP / "financials_pit_tushare.parquet",
        "bc0f4c3d3cd70a11d17f44496861e21268806509656247400c64be2d3ae7fab3",
    ),
    "cashflow": (
        FP / "cashflow_pit_tushare.parquet",
        "71d5c3d39fbf2de05064ce7f21334e15c9b1d977c64494ffe699f7eeb0b95d79",
    ),
    "balance": (
        FP / "balancesheet_pit_tushare.parquet",
        "9ca054962e850cad7305262e978758c9e9f36613c4cca025efdd99276de8dbb5",
    ),
}
CAL_REL = "data/v2/calendar/trade_cal_sse_pit.parquet"
CAL_SHA_PIN = "fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41"
HI_LIQ_MASK_DEFAULT = ROOT / "output/strategy_hiliq/universe_mask_hiliq_v1.parquet"

# Minimal column projection (aligned with leaf25_ttm_recon_step_m1_r5 KEY1+VAL; do not densify)
KEY1 = ["ts_code", "end_date", "available_at", "update_flag", "report_type"]
VAL = {"income": ["n_income"], "cashflow": ["n_cashflow_act"], "balance": ["total_assets"]}
NULL = "<NULL>"

# ---------------------------------------------------------------------------
# FORMAL PEAK PATH GATE:
#   Real PIT + HI_LIQ CS peak path ONLY after Arch signs independent probe .ok
#   (NOT X2, NOT step_m1 1c32ab1e…) AND Main schedules short window AND CLI
#   passes --allow-real-data + --arch-ok-path. Until then: --dry-run only.
# ---------------------------------------------------------------------------


def stage(name: str) -> None:
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(f"STAGE {name} ru_maxrss={rss}", file=sys.stderr, flush=True)


def vmhwm_kb() -> int | None:
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmHWM:"):
                    return int(line.split()[1])
    except OSError:
        return None
    return None


def peak_kb() -> int:
    ru = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    hw = vmhwm_kb()
    return max(ru, hw) if hw is not None else ru


def check_rss(label: str, c4_kb: int, hard_kb: int, split_kb: int) -> int:
    pk = peak_kb()
    print(
        f"RSS_CHECK {label} peak_kb={pk} split={split_kb} c4={c4_kb} hard={hard_kb}",
        flush=True,
    )
    if pk >= hard_kb:
        print(
            f"STOP: RSS hard breached peak_kb={pk} >= hard={hard_kb}",
            file=sys.stderr,
        )
        raise SystemExit(95)
    if pk >= split_kb:
        print(
            f"STOP: RSS >= 0.85*C4 peak_kb={pk} >= split={split_kb}; "
            f"split further — ban raise cap",
            file=sys.stderr,
        )
        raise SystemExit(94)
    return pk


def assert_tmp_quantlab(path: Path, what: str) -> None:
    resolved = path.resolve()
    parts = resolved.parts
    ok = False
    if len(parts) >= 3 and parts[1] == "tmp":
        name = parts[2]
        if name.startswith("quantlab"):
            ok = True
    if not ok:
        raise SystemExit(f"STOP: {what} must be under /tmp/quantlab_* got={resolved}")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def pick_chunk(plan: dict, chunk_id: int | None) -> dict:
    chunks = plan["chunks"]
    if not chunks:
        raise SystemExit("STOP: empty chunk plan")
    if chunk_id is None:
        return chunks[0]
    for c in chunks:
        if c["chunk_id"] == chunk_id:
            return c
    raise SystemExit(f"STOP: chunk_id={chunk_id} not in plan")


def dry_peak_path(chunk: dict, out_part: Path, universe: str) -> dict:
    """Simulate read PIT → CS alpha → write part → gc without touching big tables."""
    stage("dry_begin")
    n_names = 32
    rows = [
        {
            "trade_date": chunk["start"].replace("-", ""),
            "ts_code": f"{i:06d}.SZ",
            "universe": universe,
            "alpha": float(i % 7) * 0.01,
            "chunk_id": chunk["chunk_id"],
        }
        for i in range(n_names)
    ]
    stage("dry_cs_alpha")
    out_part.parent.mkdir(parents=True, exist_ok=True)
    part_meta = {
        "format": "dry_json_part",
        "not_real_data": True,
        "n_names": n_names,
        "chunk": chunk,
        "rows_sample": rows[:3],
    }
    tmp = out_part.with_suffix(out_part.suffix + ".tmp")
    tmp.write_text(json.dumps(part_meta, indent=2) + "\n", encoding="utf-8")
    tmp.replace(out_part)
    del rows
    gc.collect()
    stage("dry_after_gc")
    return {
        "path": "dry",
        "n_names": n_names,
        "n_days": chunk.get("n_rebaldays") or chunk.get("n_open_days") or 1,
        "densify": False,
        "float32": False,
        "part_path": str(out_part),
    }


def _norm_pit(df):
    """Normalize PIT keys for asof.

    Disk end_date / available_at are timestamp[us] (available_at tz=Asia/Shanghai).
    Pandas to_datetime promotes us→datetime64[ns]; asof compares day-normalized
    naive Timestamps on both sides (avail_sh_date vs trade day d; end_s sort key).
    Avoid feeding YYYYMMDD strings into pyarrow filters (r2 FAIL); string
    roundtrip here is fallback only when native parse fails.
    """
    import pandas as pd

    df = df.copy()
    df["ts_code"] = df["ts_code"].astype(str)
    # Native parse first (timestamp[us] → datetime64[ns]); day-normalize.
    end_dt = pd.to_datetime(df["end_date"], errors="coerce")
    if end_dt.isna().all() and df["end_date"].notna().any():
        # string / YYYYMMDD schema fallback only
        end_dt = pd.to_datetime(
            df["end_date"].astype(str).str.replace("-", "").str[:8],
            format="%Y%m%d",
            errors="coerce",
        )
    df["end_s"] = end_dt.dt.normalize()
    for c in ("report_type", "update_flag"):
        df[c] = df[c].astype(object).where(df[c].notna(), NULL).astype(str).str.strip()
    # available_at: timestamp[us, tz=Asia/Shanghai] → UTC → SH calendar date (naive)
    av = pd.to_datetime(df["available_at"], errors="coerce", utc=True)
    df["avail_sh_date"] = (
        av.dt.tz_convert(SH).dt.tz_localize(None).dt.normalize()
    )
    return df


def _end_date_filter_value(end_type, end_lo: str):
    """Build parquet filter RHS for end_date matching on-disk Arrow type.

    Disk financials_pit / cashflow_pit / balancesheet_pit store end_date as
    timestamp[us] (r2 FAIL d01f95c0… / Arch 6ef34f99…: string YYYYMMDD →
    ArrowNotImplementedError greater_equal(timestamp[us], string)).
    For timestamp/date: return pd.Timestamp (Arrow compares vs datetime64[us]).
    Ban feeding YYYYMMDD string into pyarrow filters against timestamp columns.
    YYYYMMDD string RHS only if schema itself is string/large_string.
    Same pattern as _load_hiliq_chunk_members date filters.
    """
    import pandas as pd
    import pyarrow as pa

    if pa.types.is_timestamp(end_type) or pa.types.is_date(end_type):
        return pd.Timestamp(end_lo)
    if pa.types.is_string(end_type) or pa.types.is_large_string(end_type):
        return end_lo.replace("-", "")[:8]
    raise SystemExit(
        f"STOP: unsupported end_date Arrow type {end_type!s}; "
        f"expected timestamp/date or string (r3 filter fix)"
    )


def _read_pit_projected(name: str, codes: list[str], end_lo: str, pin_sha: bool):
    """Column-project one PIT table; filter by codes + end_date lower bound. No densify."""
    import pyarrow.parquet as pq

    path, expect = PIT_INPUTS[name]
    if not path.is_file():
        raise SystemExit(f"STOP: PIT missing {path}")
    if pin_sha:
        actual = sha256_file(path)
        if actual != expect:
            raise SystemExit(
                f"STOP: {name} sha mismatch actual={actual} pinned={expect}"
            )
    cols = KEY1 + VAL[name]
    schema = pq.read_schema(path)
    have = set(schema.names)
    miss = [c for c in cols if c not in have]
    if miss:
        raise SystemExit(f"STOP: {name} missing columns {miss}")
    # Schema-aware: disk end_date is timestamp[us] (not YYYYMMDD string).
    # r2 used string filter → ArrowNotImplementedError (receipt d01f95c0…).
    end_lo_v = _end_date_filter_value(schema.field("end_date").type, end_lo)
    filt = [
        ("ts_code", "in", codes),
        ("end_date", ">=", end_lo_v),
    ]
    df = pq.read_table(path, columns=cols, filters=filt).to_pandas()
    return _norm_pit(df)


def _load_hiliq_chunk_members(mask_path: Path, start: str, end: str):
    """Date-filtered HI_LIQ members for chunk. Missing mask → STOP (no FULLA fallback)."""
    import pandas as pd
    import pyarrow.parquet as pq

    if not mask_path.is_file():
        raise SystemExit(
            f"STOP: HI_LIQ mask missing at {mask_path}; "
            f"refuse silent FULLA / empty-universe degradation"
        )
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    tab = pq.read_table(
        mask_path,
        columns=["date", "instrument", "in_universe"],
        filters=[
            ("date", ">=", start_ts),
            ("date", "<=", end_ts),
            ("in_universe", "==", True),
        ],
    )
    df = tab.to_pandas()
    if df.empty:
        raise SystemExit(
            f"STOP: HI_LIQ mask empty for chunk [{start}, {end}] at {mask_path}"
        )
    df["date"] = pd.to_datetime(df["date"]).dt.normalize()
    df["instrument"] = df["instrument"].astype(str)
    by_day: dict = {}
    for d, g in df.groupby("date", sort=True):
        by_day[pd.Timestamp(d)] = sorted(set(g["instrument"].tolist()))
    codes = sorted({c for v in by_day.values() for c in v})
    return by_day, codes, {
        "mask_path": str(mask_path.relative_to(ROOT) if mask_path.is_relative_to(ROOT) else mask_path),
        "mask_sha256": sha256_file(mask_path),
        "n_codes_union": len(codes),
        "n_days_with_members": len(by_day),
    }


def _chunk_trade_dates(chunk: dict) -> list:
    import pandas as pd

    if chunk.get("rebal_dates"):
        return [pd.Timestamp(x) for x in chunk["rebal_dates"]]
    # month mode: use open day head/tail span via synthetic bdates inside [start,end]
    # Prefer open_dates if present; else bdate_range (calendar pin optional elsewhere)
    if chunk.get("open_dates"):
        return [pd.Timestamp(x) for x in chunk["open_dates"]]
    # fall back: all weekdays in [start, end] — real path also intersects HI_LIQ days
    return list(pd.bdate_range(start=chunk["start"], end=chunk["end"], freq="C"))


def _asof_value(df, code: str, d, col: str):
    """Latest report_type=1 row with avail_sh_date < d for (code); return col or None."""
    g = df[
        (df["ts_code"] == code)
        & (df["report_type"] == "1")
        & df["avail_sh_date"].notna()
        & (df["avail_sh_date"] < d)
        & df[col].notna()
    ]
    if g.empty:
        return None
    top = g.sort_values(["avail_sh_date", "end_s"], ascending=[False, False]).iloc[0]
    try:
        return float(top[col])
    except (TypeError, ValueError):
        return None


def _cs_zscore(vals: list[float]) -> list[float]:
    import math

    n = len(vals)
    if n == 0:
        return []
    mu = sum(vals) / n
    var = sum((x - mu) ** 2 for x in vals) / n
    sd = math.sqrt(var) if var > 0 else 0.0
    if sd == 0.0:
        return [0.0] * n
    return [(x - mu) / sd for x in vals]


def real_peak_path(
    chunk: dict,
    out_part: Path,
    universe: str,
    *,
    hi_liq_mask: Path,
    pin_sha: bool,
    c4_kb: int,
    hard_kb: int,
    split_kb: int,
) -> dict:
    """PIT (col-proj) → HI_LIQ CS crude-accrual zscore → float32 part parquet → gc.

    Minimal mem-probe peak path. Does NOT claim full-leaf CFACC / TTM completion.
    Ban densify: long-format rows only; one trade_date at a time.
    """
    import numpy as np
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq

    if universe != "HI_LIQ":
        raise SystemExit(
            f"STOP: real_peak_path r3 probe prioritizes HI_LIQ; got universe={universe} "
            f"(FULLA not authorized for this probe package)"
        )

    stage("real_begin")
    check_rss("real_begin", c4_kb, hard_kb, split_kb)

    by_day, codes, mask_meta = _load_hiliq_chunk_members(
        hi_liq_mask, chunk["start"], chunk["end"]
    )
    stage("hiliq_members_loaded")
    check_rss("hiliq_members_loaded", c4_kb, hard_kb, split_kb)

    # Lookback for end_date filter (~2y before chunk start) — avoid full history densify
    end_lo = (pd.Timestamp(chunk["start"]) - pd.Timedelta(days=800)).strftime("%Y-%m-%d")

    pit = {}
    for name in ("income", "cashflow", "balance"):
        pit[name] = _read_pit_projected(name, codes, end_lo, pin_sha=pin_sha)
        stage(f"pit_{name}_loaded")
        check_rss(f"pit_{name}_loaded", c4_kb, hard_kb, split_kb)

    trade_dates = _chunk_trade_dates(chunk)
    # Intersect with days that have HI_LIQ members
    trade_dates = [d for d in trade_dates if d in by_day]
    if not trade_dates:
        # month mode without rebal_dates: use HI_LIQ mask days directly
        trade_dates = sorted(by_day.keys())
    if not trade_dates:
        raise SystemExit("STOP: no trade dates with HI_LIQ members in chunk")

    rows_td: list[str] = []
    rows_code: list[str] = []
    rows_alpha: list[float] = []
    n_valid_days = 0

    for d in trade_dates:
        members = by_day.get(d) or []
        raw: list[tuple[str, float]] = []
        for code in members:
            ni = _asof_value(pit["income"], code, d, "n_income")
            cf = _asof_value(pit["cashflow"], code, d, "n_cashflow_act")
            ta = _asof_value(pit["balance"], code, d, "total_assets")
            if ni is None or cf is None or ta is None or ta == 0.0:
                continue
            # Crude accrual proxy (NOT full CFACC / TTM): (NI - OCF) / TA
            raw.append((code, (ni - cf) / ta))
        if not raw:
            continue
        zs = _cs_zscore([v for _, v in raw])
        td = d.strftime("%Y%m%d")
        for (code, _), z in zip(raw, zs):
            rows_td.append(td)
            rows_code.append(code)
            rows_alpha.append(float(z))
        n_valid_days += 1
        del raw, zs
        # light GC each day to keep peak honest
        if n_valid_days % 5 == 0:
            gc.collect()
            check_rss(f"cs_day_{td}", c4_kb, hard_kb, split_kb)

    stage("cs_alpha_done")
    check_rss("cs_alpha_done", c4_kb, hard_kb, split_kb)

    if not rows_alpha:
        raise SystemExit(
            "STOP: real_peak_path produced zero alpha rows "
            "(check PIT pins / HI_LIQ overlap)"
        )

    out_part.parent.mkdir(parents=True, exist_ok=True)
    table = pa.table(
        {
            "trade_date": pa.array(rows_td, type=pa.string()),
            "ts_code": pa.array(rows_code, type=pa.string()),
            "alpha": pa.array(np.asarray(rows_alpha, dtype=np.float32), type=pa.float32()),
            "chunk_id": pa.array(
                [int(chunk["chunk_id"])] * len(rows_alpha), type=pa.int32()
            ),
            "universe": pa.array(["HI_LIQ"] * len(rows_alpha), type=pa.string()),
        }
    )
    tmp = out_part.with_suffix(out_part.suffix + ".tmp")
    pq.write_table(table, tmp, compression="zstd")
    tmp.replace(out_part)

    n_names = len(set(rows_code))
    n_rows = len(rows_alpha)
    del table, rows_td, rows_code, rows_alpha, pit, by_day, codes
    gc.collect()
    stage("real_after_gc")
    pk = check_rss("real_after_gc", c4_kb, hard_kb, split_kb)

    return {
        "path": "real_peak",
        "n_names": n_names,
        "n_days": n_valid_days,
        "n_rows": n_rows,
        "densify": False,
        "float32": True,
        "alpha_kind": "crude_accrual_cs_zscore_probe_only",
        "claims_full_cfacc": False,
        "part_path": str(out_part),
        "peak_kb_after_gc": pk,
        "hi_liq": mask_meta,
        "pit_end_date_lo": end_lo,
        "pit_inputs": {k: str(v[0].relative_to(ROOT)) for k, v in PIT_INPUTS.items()},
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Leaf25 full-factor mem_probe r3")
    ap.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Default: synthetic peak-path structure only (no big tables)",
    )
    ap.add_argument(
        "--allow-real-data",
        action="store_true",
        default=False,
        help="Required to run real PIT peak path (needs --arch-ok-path)",
    )
    ap.add_argument(
        "--no-dry-run",
        action="store_true",
        help="Disable dry-run (still needs --allow-real-data)",
    )
    ap.add_argument("--universe", default="HI_LIQ", choices=("HI_LIQ", "FULLA"))
    ap.add_argument("--start", default="2024-06-03")
    ap.add_argument("--end", default="2026-10-09")
    ap.add_argument(
        "--mode",
        choices=("rebal_days", "month"),
        default="month",
        help="Default month ≈ 1 natural month (Arch probe suggestion)",
    )
    ap.add_argument("--max-rebaldays", type=int, default=20)
    ap.add_argument(
        "--chunk-id", type=int, default=None, help="Which chunk to probe (default first)"
    )
    ap.add_argument(
        "--chunk-plan-json",
        type=Path,
        default=None,
        help="Existing plan JSON; else build via chunk_plan module",
    )
    ap.add_argument(
        "--synthetic-calendar",
        action="store_true",
        help="Pass through to chunk_plan (no calendar parquet)",
    )
    ap.add_argument("--out", type=Path, required=True, help="Probe out dir (meta + part)")
    ap.add_argument(
        "--sample-dir",
        type=Path,
        default=None,
        help="Optional RSS sample dir; must be /tmp/quantlab_*",
    )
    ap.add_argument("--c4-kb", type=int, default=C4_KB)
    ap.add_argument("--stop-kb", type=int, default=STOP_KB)
    ap.add_argument("--hard-kb", type=int, default=HARD_KB)
    ap.add_argument(
        "--arch-ok-path",
        type=Path,
        default=None,
        help="Path to Arch probe .ok (required with --allow-real-data)",
    )
    ap.add_argument(
        "--hi-liq-mask",
        type=Path,
        default=HI_LIQ_MASK_DEFAULT,
        help="HI_LIQ universe mask parquet (default strategy_hiliq v1)",
    )
    ap.add_argument(
        "--no-pin-sha",
        action="store_true",
        help="Skip PIT/calendar sha pins (not for formal probe)",
    )
    args = ap.parse_args(argv)

    if args.allow_real_data:
        dry = False
    elif args.no_dry_run:
        print("STOP: --no-dry-run requires --allow-real-data", file=sys.stderr)
        return 2
    else:
        dry = True

    if args.c4_kb != C4_KB or args.stop_kb != STOP_KB or args.hard_kb != HARD_KB:
        if args.c4_kb > C4_KB or args.stop_kb > STOP_KB or args.hard_kb > HARD_KB:
            print(
                "STOP: ban raise RSS cap above 1331200/1484800/1536000",
                file=sys.stderr,
            )
            return 2

    split_kb = int(0.85 * args.c4_kb)

    if args.sample_dir is not None:
        assert_tmp_quantlab(args.sample_dir, "sample-dir")
        args.sample_dir.mkdir(parents=True, exist_ok=True)

    ok_sha = None
    if not dry:
        if args.arch_ok_path is None or not args.arch_ok_path.is_file():
            print(
                "STOP: --allow-real-data requires existing --arch-ok-path",
                file=sys.stderr,
            )
            return 2
        ok_sha = sha256_file(args.arch_ok_path)
        if ok_sha in BANNED_OK_SHAS:
            print(
                f"STOP: ban reuse consumed/VOID .ok {ok_sha} "
                f"(step_m1 1c32ab1e… / r2 probe cd230f9c…)",
                file=sys.stderr,
            )
            return 2

    stage("start")
    check_rss("start", args.c4_kb, args.hard_kb, split_kb)

    if args.chunk_plan_json is not None:
        plan = json.loads(args.chunk_plan_json.read_text(encoding="utf-8"))
    else:
        if chunk_plan_mod is None:
            print("STOP: chunk_plan module missing", file=sys.stderr)
            return 2
        plan = chunk_plan_mod.build_plan(
            start=args.start,
            end=args.end,
            mode=args.mode,
            max_rebaldays=args.max_rebaldays,
            cal_path=None,
            synthetic=args.synthetic_calendar or dry,
            pin_sha=not (args.synthetic_calendar or dry or args.no_pin_sha),
        )

    chunk = pick_chunk(plan, args.chunk_id)
    if args.universe == "FULLA" and dry:
        print(
            "NOTE: dry-run FULLA allowed for structure; probe priority remains HI_LIQ",
            flush=True,
        )

    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    if dry:
        part_path = (
            out
            / f"alpha_parts/{args.universe}/part_"
            f"{chunk['start'].replace('-', '')}_{chunk['end'].replace('-', '')}.json"
        )
        path_meta = dry_peak_path(chunk, part_path, args.universe)
    else:
        part_path = out / f"alpha_parts/chunk_{int(chunk['chunk_id']):04d}.parquet"
        path_meta = real_peak_path(
            chunk,
            part_path,
            args.universe,
            hi_liq_mask=args.hi_liq_mask,
            pin_sha=not args.no_pin_sha,
            c4_kb=args.c4_kb,
            hard_kb=args.hard_kb,
            split_kb=split_kb,
        )

    pk = check_rss("after_chunk", args.c4_kb, args.hard_kb, split_kb)

    meta = {
        "schema": "leaf25_full_factor_mem_probe_r3",
        "supersedes_r2_end_date_filter": True,
        "r2_fail_receipt_sha8": "d01f95c0",
        "supersedes_r1_real_path": True,
        "r1_dry_still_valid": True,
        "live": False,
        "promotion_approved": False,
        "dry_run": dry,
        "allow_real_data": bool(args.allow_real_data),
        "arch_ok_path": str(args.arch_ok_path) if args.arch_ok_path else None,
        "arch_ok_sha256": ok_sha,
        "universe": args.universe,
        "chunk": chunk,
        "n_chunks_in_plan": plan.get("n_chunks"),
        "path": path_meta,
        "rss": {
            "peak_kb": pk,
            "c4_kb": args.c4_kb,
            "stop_kb": args.stop_kb,
            "hard_kb": args.hard_kb,
            "split_threshold_kb": split_kb,
            "vmhwm_kb": vmhwm_kb(),
            "ru_maxrss_kb": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
        },
        "sampler_policy": "/tmp/quantlab_* only",
        "sample_dir": str(args.sample_dir) if args.sample_dir else None,
        "banned_ok_shas": sorted(BANNED_OK_SHAS),
        "created_et": datetime.now(ET).strftime("%Y-%m-%dT%H:%M:%S%z"),
        "notes": [
            "r3: schema-aware end_date timestamp filter (fix r2 FAIL d01f95c0…)",
            "r3 real_peak_path: col-proj PIT → HI_LIQ CS crude accrual zscore → float32 part → gc",
            "NOT full-leaf CFACC; densify=false; ban raise RSS; peak>=0.85*C4 → exit 94",
            "Ban reuse cd230f9c… / 1c32ab1e…; await Arch NEW probe .ok + Main window",
        ],
    }
    meta_path = out / "run_meta.json"
    tmp = meta_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(meta_path)

    plan_path = out / "chunk_plan_used.json"
    plan_path.write_text(
        json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(
        f"OK mem_probe_r3 dry={dry} universe={args.universe} chunk_id={chunk['chunk_id']} "
        f"peak_kb={pk} meta={meta_path}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
