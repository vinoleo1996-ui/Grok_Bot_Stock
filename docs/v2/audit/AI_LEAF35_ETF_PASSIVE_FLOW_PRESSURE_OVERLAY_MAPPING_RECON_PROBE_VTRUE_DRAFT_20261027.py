#!/usr/bin/env python3
"""Leaf35 mapping recon PROBE VTRUE DRAFT — truth-value read-only diagnostic.

Option A follow-on to skeleton c2f2ca94 (UNCHANGED) + recon DRAFT 350ed22b.
Lives under docs/v2/audit/ (NOT research/).
Does NOT modify research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py
(must stay 25ae4572). Does NOT write alpha/mask/overlap products.

CLI:
  --dry-compile-only     pins only; ZERO big tables; executed_probe=false; rc=0
  (no --allow-real-data) STOP rc!=0  (unless --dry-compile-only)
  --allow-real-data --arch-ok-path <ok>
                         requires existing .ok; sha8 not in FORBIDDEN; else STOP
                         real per-rebal diag only (JSON/tsv); ban alpha/mask

This byte implements the real path; EXECUTED_PROBE for the ticket that lands
this DRAFT is false until Arch review + Main signs a NEW read-only probe .ok
(ban RESTORED 10927bd9+legacy). ≠X2 ACCEPT; ≠leaf36; live=false.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import resource
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if not (ROOT / "research").is_dir():
    cand = Path("/workspace/QuantLab")
    if (cand / "research").is_dir():
        ROOT = cand

SCRIPT_REL = (
    "docs/v2/audit/"
    "AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_VTRUE_DRAFT_20261027.py"
)
SKELETON_REL = (
    "docs/v2/audit/"
    "AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_DRAFT_20261027.py"
)
FORMAL_SCRIPT_REL = "research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py"
FORMAL_SHA8_PIN = "25ae4572"
SKELETON_SHA8_PIN = "c2f2ca94"
PIN_SHA8 = "dd17044a"
VOID_SHA8 = "dfafff28"
ARCH_RECON_SHA8 = "cb3ca975"
COUNT_JSON_SHA8 = "a17b75fb"
COUNT_SCRIPT_SHA8 = "4e964d40"
LEAF33_SHA8_PIN = "afbbe7e7"
RECON_DRAFT_SHA8 = "350ed22b"

X2_START = "2024-06-03"
X2_END = "2026-10-09"
X2_END_TRADE_DATE = "20261009"
REBAL_EVERY = 20
RSS_LIMIT_MB = 1500
HARD_KB = 1536000

ETF_INDEX_MAP = {
    "510300.SH": "000300.SH",
    "510500.SH": "000905.SH",
    "512100.SH": "000852.SH",
}

ETF_SHARE_DEFAULT = ROOT / "data/v2/etf/share_pit/etf_share_flow_pit_major.parquet"
IDX_WEIGHT_DEFAULT = (
    ROOT / "data/v2/index_members/index_weight_csi300_500_1000.parquet"
)
HI_LIQ_MASK_DEFAULT = ROOT / "output/strategy_hiliq/universe_mask_hiliq_v1.parquet"
CAL_DEFAULT = ROOT / "data/v2/calendar/trade_cal_sse_pit.parquet"

# Formal FORBID_OK_SHA8 (26) + VOID ok 10927bd9
FORBIDDEN_OK = {
    "10927bd9",
    "178e90e9",
    "c1b71e64",
    "245df63f",
    "c5ed13df",
    "5774bb6e",
    "81521fb5",
    "02426b73",
    "4bb141c9",
    "fdbaa512",
    "aa25e989",
    "7e239487",
    "5af20222",
    "5ae077fa",
    "3c297052",
    "e107383f",
    "2be59acd",
    "a7d98ac9",
    "8e51de63",
    "3a6caa4f",
    "8bcd79dc",
    "725be3e0",
    "0f50daf7",
    "3c19dd7d",
    "1c32ab1e",
    "6054b3bf",
    "6de02e74",
}

# Arch C2 pinned columns
PROBE_COLS_PINNED = [
    "rebal_date",
    "n_share_rows",
    "n_share_rows_avail_le_tts",
    "n_weight_rows_schemeA",
    "n_mapped",
    "n_pressure_nonnull",
    "n_hiliq_intersect",
    "empty_reason",
]
# Extra (do not replace pinned)
PROBE_COLS_EXTRA = [
    "n_share_rows_pin13_avail_only",
    "n_share_rows_count_approx_style",
    "empty_reason_detail",
]

EMPTY_REASON_ENUM = [
    "share_pit_empty_dual_filter",
    "share_avail_late",
    "weight_schemeA_empty",
    "map_fail",
    "hiliq_intersect_empty",
    "pressure_all_null",
    "ok",
    "share_trade_date_empty",
    "PIN_GAP_needs_ok_window",
]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def peak_kb() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def stage(name: str) -> None:
    print(f"STAGE {name} ru_maxrss={peak_kb()}", file=sys.stderr, flush=True)


def check_rss(label: str) -> None:
    pk = peak_kb()
    soft_kb = RSS_LIMIT_MB * 1024
    print(
        f"RSS_CHECK {label} peak_kb={pk} soft={soft_kb} hard={HARD_KB}",
        file=sys.stderr,
        flush=True,
    )
    if pk >= HARD_KB:
        raise SystemExit(
            f"STOP: RSS hard breached peak_kb={pk} >= hard={HARD_KB} (ban raise rss)"
        )
    if pk >= soft_kb:
        raise SystemExit(
            f"STOP: RSS soft 1500MB breached peak_kb={pk} >= soft={soft_kb}; ban raise"
        )


def load_formal_module():
    """Import formal leaf35 build read-only (ban modifying its file)."""
    formal_path = ROOT / FORMAL_SCRIPT_REL
    if not formal_path.is_file():
        raise SystemExit(f"STOP: formal script missing {formal_path}")
    sha8 = sha256_file(formal_path)[:8]
    if sha8 != FORMAL_SHA8_PIN:
        raise SystemExit(
            f"STOP: formal script sha8 drifted observed={sha8} pin={FORMAL_SHA8_PIN}"
        )
    spec = importlib.util.spec_from_file_location(
        "leaf35_etf_passive_flow_pressure_overlay_alpha_build_readonly",
        formal_path,
    )
    if spec is None or spec.loader is None:
        raise SystemExit("STOP: cannot import formal module")
    mod = importlib.util.module_from_spec(spec)
    # Avoid executing formal main; loader exec_module runs top-level only (OK)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod, sha8


def dry_compile_only() -> int:
    formal = ROOT / FORMAL_SCRIPT_REL
    skeleton = ROOT / SKELETON_REL
    leaf33 = ROOT / "research/leaf33_share_unlock_pressure_resid_alpha_build.py"
    formal_sha8 = sha256_file(formal)[:8] if formal.is_file() else "MISSING"
    skel_sha8 = sha256_file(skeleton)[:8] if skeleton.is_file() else "MISSING"
    leaf33_sha8 = sha256_file(leaf33)[:8] if leaf33.is_file() else "MISSING"
    payload = {
        "role": "leaf35_mapping_recon_probe_vtrue_draft",
        "option": "A",
        "arch_recon_review_sha8": ARCH_RECON_SHA8,
        "recon_draft_sha8": RECON_DRAFT_SHA8,
        "skeleton_probe_sha8_pin": SKELETON_SHA8_PIN,
        "skeleton_probe_sha8_observed": skel_sha8,
        "skeleton_unchanged_required": skel_sha8 == SKELETON_SHA8_PIN,
        "dry_compile_only": True,
        "executed_probe": False,
        "allow_real_data": False,
        "x2_accept": False,
        "leaf36": False,
        "not_leaf36": True,
        "live": False,
        "leo_notify": False,
        "formal_script": FORMAL_SCRIPT_REL,
        "formal_sha8_observed": formal_sha8,
        "formal_sha8_pin": FORMAL_SHA8_PIN,
        "formal_unchanged_required": formal_sha8 == FORMAL_SHA8_PIN,
        "leaf33_sha8_observed": leaf33_sha8,
        "leaf33_sha8_pin": LEAF33_SHA8_PIN,
        "leaf33_unchanged_required": leaf33_sha8 == LEAF33_SHA8_PIN,
        "pin_sha8": PIN_SHA8,
        "void_sha8": VOID_SHA8,
        "count_json_sha8_ref": COUNT_JSON_SHA8,
        "count_script_sha8_ref": COUNT_SCRIPT_SHA8,
        "etf_index_map": dict(ETF_INDEX_MAP),
        "x2_window": f"{X2_START} → {X2_END}",
        "x2_end_trade_date": X2_END_TRADE_DATE,
        "rebal_every_td": REBAL_EVERY,
        "rss_limit_mb": RSS_LIMIT_MB,
        "ban_raise_rss": True,
        "peak_proof_required": True,
        "probe_output_columns_pinned": list(PROBE_COLS_PINNED),
        "probe_output_columns_extra": list(PROBE_COLS_EXTRA),
        "empty_reason_enum": list(EMPTY_REASON_ENUM),
        "share_pit_contrast": {
            "formal_A": "trade_date==rebal AND available_at_clock<=t_ts(15:00 Asia/Shanghai)",
            "count_approx": "trade_date==rebal; NO available_at filter (a17b75fb / 4e964d40)",
            "pin_1_3": "available_at<=t_ts ONLY (no trade_date==rebal requirement)",
        },
        "weight_scheme_A": (
            "month-end -> next-month first trade day 09:00 Asia/Shanghai "
            "= weight_available_at; weight_available_at<=t_ts"
        ),
        "data_paths": {
            "etf_share": str(ETF_SHARE_DEFAULT.relative_to(ROOT)),
            "idx_weight": str(IDX_WEIGHT_DEFAULT.relative_to(ROOT)),
            "hiliq_mask": str(HI_LIQ_MASK_DEFAULT.relative_to(ROOT)),
            "calendar": str(CAL_DEFAULT.relative_to(ROOT)),
        },
        "forbidden_ok_sha8": sorted(FORBIDDEN_OK),
        "ban_restored_10927bd9": True,
        "ban_write_alpha_mask_overlap": True,
        "ban_modify_formal_25ae4572": True,
        "notes": [
            "VTRUE implements real per-rebal counts under NEW .ok; this dry path loads ZERO big tables",
            "Skeleton c2f2ca94 kept UNCHANGED; this is a NEW file",
            "EXECUTED_PROBE=false until Arch review + Main probe window + NEW .ok",
            "≠X2 ACCEPT; ≠leaf36",
        ],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if formal_sha8 != FORMAL_SHA8_PIN:
        print("STOP: formal script sha8 drifted; refuse probe framing", file=sys.stderr)
        return 2
    if skel_sha8 != SKELETON_SHA8_PIN:
        print("STOP: skeleton probe sha8 drifted; refuse overwrite framing", file=sys.stderr)
        return 2
    return 0


def _classify_empty(
    *,
    n_share_rows: int,
    n_share_avail: int,
    n_weight: int,
    n_mapped: int,
    n_pressure: int,
    n_hiliq: int,
) -> tuple[str, str]:
    if n_share_rows == 0:
        return "share_trade_date_empty", "no share rows with trade_date==rebal"
    if n_share_avail == 0 and n_share_rows > 0:
        return (
            "share_avail_late",
            "same-day share rows exist but all available_at_clock > t_ts(15:00)",
        )
    if n_share_avail == 0:
        return "share_pit_empty_dual_filter", "dual filter emptied share pit"
    if n_weight == 0:
        return "weight_schemeA_empty", "no scheme-A weight rows with avail<=t_ts"
    if n_mapped == 0:
        return "map_fail", "ETF×index map produced zero mappable names"
    if n_pressure == 0:
        return "pressure_all_null", "pressure panel empty/all-null after combine"
    if n_hiliq == 0:
        return "hiliq_intersect_empty", "pressure names ∩ HI_LIQ empty"
    return "ok", "nonempty pressure ∩ HI_LIQ"


def run_real_probe(args) -> int:
    import pandas as pd

    ok_path = Path(args.arch_ok_path)
    if not ok_path.is_file():
        print(
            "STOP: --allow-real-data requires existing --arch-ok-path",
            file=sys.stderr,
        )
        return 4
    ok_sha = sha256_file(ok_path)
    ok_sha8 = ok_sha[:8]
    if ok_sha8 in FORBIDDEN_OK:
        print(
            f"STOP: ban RESTORED/forbid .ok sha8={ok_sha8} (full={ok_sha})",
            file=sys.stderr,
        )
        return 5

    stage("vtrue_probe_start")
    check_rss("vtrue_probe_start")

    mod, formal_sha8 = load_formal_module()
    stage("after_import_formal")
    check_rss("after_import_formal")

    # Rebal calendar from HI_LIQ mask days (same as formal build_mask_for_window)
    by_day, _codes, mask_meta = mod._load_mask_members(
        Path(args.hi_liq_mask), X2_START, X2_END, label="HILIQ"
    )
    stage("after_mask")
    check_rss("after_mask")

    w_idx, avail_map, weight_meta = mod._load_weight_pin_scheme_a(
        Path(args.idx_weight), Path(args.calendar)
    )
    stage("after_weight_pin")
    check_rss("after_weight_pin")

    all_days = sorted(by_day.keys())
    rebal_idx = list(range(0, len(all_days), REBAL_EVERY))
    if rebal_idx and rebal_idx[-1] != len(all_days) - 1:
        rebal_idx.append(len(all_days) - 1)
    rebal_days = [all_days[i] for i in rebal_idx]

    # Formal window load (trade_date in rebal set); PIT applied per day later
    etf_df = mod._load_etf_flows_window(Path(args.etf_share), rebal_days)
    stage("after_etf_share_window")
    check_rss("after_etf_share_window")

    # Broader share load for PIN §1.3 contrast (no trade_date==rebal prefilter)
    import pyarrow.parquet as pq

    share_path = Path(args.etf_share)
    t_all = pq.read_table(
        share_path,
        columns=[
            "ts_code",
            "trade_date",
            "d_share_wan",
            "flow_est_wan_yuan",
            "available_at",
        ],
    )
    share_all = t_all.to_pandas()
    share_all = share_all[share_all["ts_code"].isin(list(ETF_INDEX_MAP.keys()))].copy()
    share_all["trade_date"] = pd.to_datetime(share_all["trade_date"]).dt.normalize()
    share_all["available_at"] = pd.to_datetime(share_all["available_at"], utc=False)

    def _to_naive_sh(x):
        ts = pd.Timestamp(x)
        if pd.isna(ts):
            return pd.NaT
        if ts.tzinfo is not None:
            return ts.tz_convert("Asia/Shanghai").tz_localize(None)
        return ts

    share_all["available_at_clock"] = share_all["available_at"].map(_to_naive_sh)
    stage("after_share_all_for_pin13")
    check_rss("after_share_all_for_pin13")

    rows = []
    for d in rebal_days:
        d = pd.Timestamp(d).normalize()
        t_ts = mod._t_ts_1500(d)
        members = set(by_day.get(d, []))

        day_same = etf_df[etf_df["trade_date"] == d]
        n_share_rows = int(len(day_same))
        n_share_count_style = n_share_rows  # COUNT: same-day, no avail filter
        day_avail = day_same[
            day_same["available_at_clock"].notna()
            & (day_same["available_at_clock"] <= t_ts)
        ]
        n_share_avail = int(len(day_avail))

        pin13 = share_all[
            share_all["available_at_clock"].notna()
            & (share_all["available_at_clock"] <= t_ts)
        ]
        n_pin13 = int(len(pin13))

        # scheme A weight rows: union of asof series across 3 indices
        n_weight = 0
        weight_codes: set[str] = set()
        for _etf, index_code in ETF_INDEX_MAP.items():
            wser = mod._asof_weight_scheme_a(w_idx, avail_map, index_code, t_ts)
            if wser is None or getattr(wser, "empty", True):
                continue
            n_weight += int(len(wser))
            for con in wser.index:
                weight_codes.add(mod.to_ts(con))

        # Formal pressure (dual filter + scheme A + HI_LIQ members)
        press = mod._pressure_on_day(d, members, etf_df, w_idx, avail_map)
        stage(f"after_pressure_rebal_{d.strftime('%Y%m%d')}")
        check_rss(f"after_pressure_rebal_{d.strftime('%Y%m%d')}")

        if press is None or press.empty:
            n_mapped = 0
            n_pressure = 0
            n_hiliq = 0
        else:
            n_mapped = int(press["ts_code"].nunique())
            n_pressure = int(
                press["pressure_raw"].notna().sum()
                if "pressure_raw" in press.columns
                else len(press)
            )
            press_codes = set(press["ts_code"].astype(str).tolist())
            n_hiliq = int(len(press_codes & members))

        empty_reason, detail = _classify_empty(
            n_share_rows=n_share_rows,
            n_share_avail=n_share_avail,
            n_weight=n_weight,
            n_mapped=n_mapped,
            n_pressure=n_pressure,
            n_hiliq=n_hiliq,
        )
        # refine: dual filter empty when same-day exists but avail cleared
        if n_share_rows > 0 and n_share_avail == 0 and empty_reason == "share_avail_late":
            pass
        elif n_share_rows == 0 and n_pin13 > 0:
            detail = (
                detail
                + f"; pin13_avail_only={n_pin13} (PIN§1.3 would see rows; formal trade_date==rebal empty)"
            )

        rows.append(
            {
                "rebal_date": str(d.date()),
                "n_share_rows": n_share_rows,
                "n_share_rows_avail_le_tts": n_share_avail,
                "n_weight_rows_schemeA": n_weight,
                "n_mapped": n_mapped,
                "n_pressure_nonnull": n_pressure,
                "n_hiliq_intersect": n_hiliq,
                "empty_reason": empty_reason,
                "n_share_rows_pin13_avail_only": n_pin13,
                "n_share_rows_count_approx_style": n_share_count_style,
                "empty_reason_detail": detail,
                "n_hiliq_members": int(len(members)),
                "n_weight_codes_union": int(len(weight_codes)),
            }
        )

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    # Ban alpha/mask filenames
    banned_names = {"alpha", "mask", "overlap", "exclusion_mask"}
    for bn in banned_names:
        if any(bn in p.name.lower() for p in out_dir.glob("*")):
            pass  # only ban writing; we write diag only

    json_path = out_dir / "mapping_recon_vtrue_per_rebal.json"
    tsv_path = out_dir / "mapping_recon_vtrue_per_rebal.tsv"

    payload = {
        "role": "leaf35_mapping_recon_probe_vtrue",
        "executed_probe": True,
        "option": "A",
        "arch_recon_review_sha8": ARCH_RECON_SHA8,
        "formal_sha8": formal_sha8,
        "formal_sha8_pin": FORMAL_SHA8_PIN,
        "pin_sha8": PIN_SHA8,
        "void_sha8": VOID_SHA8,
        "count_json_sha8_ref": COUNT_JSON_SHA8,
        "arch_ok_path": str(ok_path),
        "arch_ok_sha256": ok_sha,
        "arch_ok_sha8": ok_sha8,
        "x2_window": f"{X2_START} → {X2_END}",
        "rebal_every_td": REBAL_EVERY,
        "n_rebal": len(rows),
        "rss_limit_mb": RSS_LIMIT_MB,
        "peak_kb": peak_kb(),
        "mask_meta": mask_meta,
        "weight_meta": {
            k: weight_meta[k]
            for k in (
                "weight_unit",
                "scheme",
                "n_month_end_points",
                "n_avail_mapped",
                "weight_sha8_pin",
            )
            if k in weight_meta
        },
        "probe_output_columns_pinned": list(PROBE_COLS_PINNED),
        "probe_output_columns_extra": list(PROBE_COLS_EXTRA),
        "rows": rows,
        "x2_accept": False,
        "leaf36": False,
        "not_leaf36": True,
        "live": False,
        "leo_notify": False,
        "ban_write_alpha_mask_overlap": True,
        "ban_modify_formal": True,
    }
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    cols = PROBE_COLS_PINNED + PROBE_COLS_EXTRA
    with tsv_path.open("w", encoding="utf-8") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(str(r.get(c, "")) for c in cols) + "\n")

    stage("after_daily_concat")  # peak_proof marker (diag only; no alpha)
    check_rss("after_daily_concat")

    summary = {
        "ok": True,
        "executed_probe": True,
        "json": str(json_path),
        "tsv": str(tsv_path),
        "n_rebal": len(rows),
        "empty_reason_counts": {},
        "formal_sha8": formal_sha8,
        "arch_ok_sha8": ok_sha8,
        "peak_kb": peak_kb(),
        "x2_accept": False,
    }
    from collections import Counter

    summary["empty_reason_counts"] = dict(Counter(r["empty_reason"] for r in rows))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Leaf35 mapping recon PROBE VTRUE DRAFT (Option A)"
    )
    ap.add_argument(
        "--dry-compile-only",
        action="store_true",
        help="pins only; ZERO big tables; executed_probe=false",
    )
    ap.add_argument(
        "--allow-real-data",
        action="store_true",
        help="requires NEW arch-ok; ban RESTORED 10927bd9+forbid",
    )
    ap.add_argument(
        "--arch-ok-path",
        default="",
        help="NEW .ok path (sha8 not in FORBIDDEN)",
    )
    ap.add_argument("--universe", default="HILIQ", choices=("HILIQ", "HI_LIQ"))
    ap.add_argument("--window", default="x2", choices=("x2",))
    ap.add_argument("--x2-end", default=X2_END_TRADE_DATE)
    ap.add_argument("--etf-share", default=str(ETF_SHARE_DEFAULT))
    ap.add_argument("--idx-weight", default=str(IDX_WEIGHT_DEFAULT))
    ap.add_argument("--hi-liq-mask", default=str(HI_LIQ_MASK_DEFAULT))
    ap.add_argument("--calendar", default=str(CAL_DEFAULT))
    ap.add_argument(
        "--rss-limit-mb",
        type=int,
        default=RSS_LIMIT_MB,
        help="soft cap MB; ban raise above 1500",
    )
    ap.add_argument(
        "--out",
        default="",
        help="diag out dir (JSON/tsv only; ban alpha/mask)",
    )
    ap.add_argument(
        "--force",
        action="store_true",
        help="FORBIDDEN; always STOP if set",
    )
    args = ap.parse_args(argv)

    if args.force:
        print("STOP: --force forbidden on mapping recon vtrue probe", file=sys.stderr)
        return 9
    if int(args.rss_limit_mb) > RSS_LIMIT_MB:
        print(
            f"STOP: ban raise rss; got {args.rss_limit_mb} > pin {RSS_LIMIT_MB}",
            file=sys.stderr,
        )
        return 9
    if args.x2_end != X2_END_TRADE_DATE:
        print(
            f"STOP: --x2-end must be {X2_END_TRADE_DATE} this ticket (got {args.x2_end})",
            file=sys.stderr,
        )
        return 9

    if args.dry_compile_only:
        return dry_compile_only()

    if not args.allow_real_data:
        print(
            "STOP: real vtrue probe requires --allow-real-data + --arch-ok-path "
            "(or use --dry-compile-only). EXECUTED_PROBE gate closed. "
            "ban RESTORED 10927bd9. ≠X2 ACCEPT",
            file=sys.stderr,
        )
        return 3

    if not args.out:
        print(
            "STOP: --allow-real-data requires --out diag directory "
            "(JSON/tsv only; ban alpha/mask)",
            file=sys.stderr,
        )
        return 4

    return run_real_probe(args)


if __name__ == "__main__":
    raise SystemExit(main())
