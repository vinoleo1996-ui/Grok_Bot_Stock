# a18_s53_driver_v2_dest_monthly.py — §5.3 guide-baseline driver
# Side draft (audit pack). dest-side year_sorted_content_col_hashes isomorphic
# with ref_build_year monthly accumulate (judge 6466c490). live=false.
# A9: baseline written ONLY when reconcile ok. Bans unchanged.
from __future__ import annotations
import hashlib, json, os, sys, time
from pathlib import Path

ROOT = Path("/workspace/QuantLab")
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / "scripts/acquire"))
# side-draft helper from audit pack (NOT production incr)
_AUDIT = ROOT / "docs/v2/audit/daily_basic_a18_20261026"
sys.path.insert(0, str(_AUDIT))

import pyarrow as pa
import pyarrow.parquet as pq
import daily_basic_incremental as dbi
from a18_s53_year_sorted_content_col_hashes_helper import (
    year_sorted_content_col_hashes_from_sorted_df,
)

DEST = ROOT / "data/v2/valuation/daily_basic_full_tushare.parquet"
MAN = ROOT / "data/v2/valuation/daily_basic_full_tushare_manifest.json"
BASE = ROOT / "data/v2/valuation/daily_basic_full_tushare_build_baseline.json"
RAW = ROOT / "data/v2/tushare_raw/daily_basic"
END = "20261016"
YEARS = list(range(2014, 2027))  # 2014..2026
Y0 = YEARS[0]
DEST_PIN = "f6bbf9e51af78dfab2c021fa8809c58ad0d36df7293f8a488200b9dd5ceaf948"
MAN_PIN = "8c2c978b384e8d3206da0876686fa214d7960353f472e81151a7acc3b0c74ac8"
INCR_PIN = "a7ac54b3ecdf33d338710df5c96f447fbec51affdcfbf167fb3e00648f678dd8"
TRANSFORM_PIN = "308b5054c39801116fd0eb19b4e4bd10bdccd4b4d40bfb67dd06a58fa67ab974"
A13_LIMIT_KB = 1_000_000


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def abort(msg: str, code: int = 2) -> None:
    print("ABORT:", msg, file=sys.stderr)
    sys.exit(code)


def main() -> int:
    hhmm = int(time.strftime("%H%M"))
    if 1615 <= hhmm < 1745:
        abort("inside leaf25 selfcheck window 16:15-17:45 ET")
    if BASE.exists():
        abort("baseline already exists; refuse overwrite")
    for label, path, exp in [
        ("dest", DEST, DEST_PIN),
        ("man", MAN, MAN_PIN),
        ("incr", ROOT / "scripts/acquire/daily_basic_incremental.py", INCR_PIN),
    ]:
        got = sha256_file(path)
        if got != exp:
            abort(f"{label} sha mismatch got={got}", 3)
    man = json.loads(MAN.read_text(encoding="utf-8"))
    if "build" in man:
        abort("manifest unexpectedly has build")
    if man.get("date_max") != "2026-10-16":
        abort(f"date_max drift: {man.get('date_max')}")

    tsha = dbi.compute_transform_sha()
    if tsha != TRANSFORM_PIN:
        abort(f"transform_sha drift: {tsha}", 3)
    rt = dbi.runtime_versions()

    out_tmp = Path(
        os.environ.get("OUT_TMP")
        or f"/tmp/a18_s53_v2_{time.strftime('%Y%m%dT%H%M%S')}_{os.getpid()}"
    )
    out_tmp.mkdir(parents=True, exist_ok=True)

    ref_by_year = {}
    peak_all = 0
    for y in YEARS:
        print(f"REF_BUILD_YEAR_BEGIN {y}", flush=True)
        r = dbi.ref_build_year(y, RAW, END)
        ref_by_year[str(y)] = r
        peak_all = max(peak_all, int(r.get("peak_vmhwm_kb") or 0))
        (out_tmp / f"ref_year_{y}.json").write_text(
            json.dumps(r, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(
            f"REF_BUILD_YEAR_END {y} rows={r.get('rows')} peak_kb={r.get('peak_vmhwm_kb')}",
            flush=True,
        )

    md = pq.read_metadata(DEST)
    pf = pq.ParquetFile(DEST)
    dest_rows_by_year = {}
    dest_ysch = {}
    dest_stub = {}
    dest_rg_by_year = {}
    schema_names = list(md.schema.names)
    try:
        col_idx = schema_names.index("trade_date")
    except ValueError:
        abort("trade_date missing in schema")

    for rg_idx in range(md.num_row_groups):
        rg = md.row_group(rg_idx)
        stats = rg.column(col_idx).statistics
        if stats is None or not stats.has_min_max:
            abort(f"row_group {rg_idx} missing trade_date stats")
        dmin = str(stats.min)[:10]
        dmax = str(stats.max)[:10]
        y0, y1 = int(dmin[:4]), int(dmax[:4])
        if y0 != y1:
            abort(f"row_group {rg_idx} spans years {y0}-{y1}")
        dest_rg_by_year.setdefault(str(y0), []).append(
            {"rg": rg_idx, "num_rows": rg.num_rows, "dmin": dmin, "dmax": dmax}
        )

    out_cols = list(dbi.TRANSFORM_CONSTANTS["out_cols"])
    for y in YEARS:
        ys = str(y)
        rgs = dest_rg_by_year.get(ys) or []
        tables = [pf.read_row_group(info["rg"]) for info in rgs]
        if not tables:
            dest_rows_by_year[ys] = 0
            dest_ysch[ys] = {}
            dest_stub[ys] = None
            continue
        tbl = pa.concat_tables(tables)
        df = tbl.to_pandas()
        df = df.drop_duplicates(["ts_code", "trade_date"], keep="last")
        df = df.sort_values(["trade_date", "ts_code"]).reset_index(drop=True)
        # FIX (v2 / judge 6466c490): monthly accumulate isomorphic with ref_build_year
        # OLD (buggy): header-once + ONE _row_group_physical_col_hashes(full year tbl2)
        ysch, stub, nrows = year_sorted_content_col_hashes_from_sorted_df(
            df, out_cols, dbi._row_group_physical_col_hashes
        )
        dest_rows_by_year[ys] = int(nrows)
        dest_ysch[ys] = ysch
        dest_stub[ys] = stub
        del df, tbl, tables

    diffs = []
    for y in YEARS:
        ys = str(y)
        rr = ref_by_year.get(ys) or {}
        r_rows = int(rr.get("rows") or 0)
        d_rows = int(dest_rows_by_year.get(ys) or 0)
        if r_rows != d_rows:
            diffs.append({"year": y, "kind": "rows", "ref": r_rows, "dest": d_rows})
        r_h = rr.get("year_sorted_content_col_hashes") or {}
        d_h = dest_ysch.get(ys) or {}
        for c in sorted(set(r_h) | set(d_h)):
            if r_h.get(c) != d_h.get(c):
                diffs.append(
                    {
                        "year": y,
                        "kind": "year_sorted_content_col_hashes",
                        "col": c,
                        "ref": r_h.get(c),
                        "dest": d_h.get(c),
                    }
                )
        r_stub = rr.get("year_sorted_content_col_hashes_stub")
        d_stub = dest_stub.get(ys)
        if r_stub and d_stub and r_stub != d_stub:
            diffs.append(
                {
                    "year": y,
                    "kind": "year_sorted_content_col_hashes_stub",
                    "ref": r_stub,
                    "dest": d_stub,
                }
            )

    inv = {}
    for p in sorted(RAW.glob("????????.parquet")):
        stem = p.stem
        if stem < f"{Y0}0101" or stem > END:
            continue
        inv[stem] = sha256_file(p)
    inv_blob = json.dumps(inv, sort_keys=True, separators=(",", ":")).encode()
    raw_inventory_sha = hashlib.sha256(inv_blob).hexdigest()
    (out_tmp / "raw_inventory.json").write_bytes(inv_blob + b"\n")

    reconcile = {
        "ok": len(diffs) == 0,
        "diff_count": len(diffs),
        "diffs_sample": diffs[:100],
        "peak_vmhwm_kb_all_years": peak_all,
        "a13_limit_kb": A13_LIMIT_KB,
        "a13_ok": peak_all <= A13_LIMIT_KB,
        "end": END,
        "years": YEARS,
        "dest_hash_caliber": "monthly_accumulate_isomorphic_ref_build_year_v2",
        "judge_sha8": "6466c490",
    }
    (out_tmp / "reconcile.json").write_text(
        json.dumps(reconcile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    product_sha = sha256_file(DEST)
    baseline_obj = {
        "format": "daily_basic_build_baseline_v1",
        "product_path": str(DEST.relative_to(ROOT)),
        "product_sha256": product_sha,
        "rows": int(sum(dest_rows_by_year.values())),
        "rows_by_year": dest_rows_by_year,
        "row_groups_by_year": {
            k: [x["num_rows"] for x in v] for k, v in dest_rg_by_year.items()
        },
        "year_sorted_content_col_hashes": dest_ysch,
        "schema_names": schema_names,
        "transform_sha": tsha,
        "runtime_versions": rt,
        "raw_inventory_sha256": raw_inventory_sha,
        "raw_inventory_end": END,
        "ref_build": {
            "end": END,
            "years": YEARS,
            "by_year": {
                ys: {
                    "rows": ref_by_year[ys].get("rows"),
                    "peak_vmhwm_kb": ref_by_year[ys].get("peak_vmhwm_kb"),
                    "year_sorted_content_col_hashes": ref_by_year[ys].get(
                        "year_sorted_content_col_hashes"
                    ),
                    "year_sorted_content_col_hashes_stub": ref_by_year[ys].get(
                        "year_sorted_content_col_hashes_stub"
                    ),
                }
                for ys in ref_by_year
            },
            "reconcile_ok": reconcile["ok"],
            "peak_vmhwm_kb_all_years": peak_all,
        },
        "design_sha256": "5c6a3a1dcc0fdcba279cafbbacf64c829fc50ee9ed3faf0d8095b6dc4b8c17fc",
        "section": "5.3",
        "note": "scheme_A_step_section_5_3;A9_no_write_on_mismatch;not_manifest_seed;not_allow_run;dest_monthly_isomorph_v2",
        "built_at_et": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }

    # A9
    if not reconcile["ok"]:
        (out_tmp / "DIFFS.json").write_text(
            json.dumps(diffs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print("RECONCILE_FAIL diff_count=", len(diffs), "baseline_NOT_written A9")
        print("OUT_TMP", out_tmp)
        return 9

    tmp_base = out_tmp / "build_baseline.json"
    tmp_base.write_text(
        json.dumps(baseline_obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    os.replace(tmp_base, BASE)
    print("BASELINE_WRITTEN", BASE, "sha8", sha256_file(BASE)[:8])
    print("OUT_TMP", out_tmp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
