#!/usr/bin/env python3
"""Leaf33 A1 — read-only n_unlock_pool diagnostic probe v1.

DIAGNOSTIC ONLY — NOT the formal alpha build.
Does NOT modify research/leaf33_share_unlock_pressure_resid_alpha_build.py.
Does NOT change COVERAGE_MEDIAN_* / PRESSURE_MIN_VALID.
Does NOT decide theta (theta in 0.5-0.8 awaits Main).
Does NOT claim X2 ACCEPT. live=false; promotion_approved=false.

Metric pins (LOCKED for this probe):
  W = PRESSURE_W = 20 trading days
  rebal_every_td = 20 (same as formal leaf33)
  tz_align_mode = naive_calendar_day (same as formal afbbe7e7)
  n_unlock_pool[d] = | HI_LIQ ∩ {codes with >=1 PIT-visible share_float unlock event in W=20 window ending at rebal day d} |
  n_alpha[d]      = count of non-null pressure_resid / alpha at rebal day d
                    (formal coverage_rebal.n; or recompute on real path)
  ratio[d]        = n_alpha[d] / n_unlock_pool[d]  (denom 0 -> NaN; never fill 0)

HARD RULES:
  - Default --dry-run: print pins / plan / intended output schema; exit 0;
    do NOT read bars / share_float / HI_LIQ mask tables.
  - Real path requires BOTH --allow-real-data AND an existing --arch-ok-path;
    missing either -> STOP exit 2. No CLI-fabricated default --arch-ok-path.
  - Ban import/rewrite/overwrite of formal leaf33 alpha build script.
  - Forbid RESTORED ok sha8s include 245df63f / c5ed13df / 5774bb6e + twenty.
  - Sampler / sample-dir: /tmp/quantlab_* only.
  - Output may summarize distributions; MUST NOT self-decide theta or write
    "建议 theta=…通过".

Upstream pins (documentation; verified by caller ticket):
  VOID 6826c01d / RUN a1b426f5 / recon DRAFT b84496fe / Arch review 29166bf7
  alpha ea17e173 / formal script afbbe7e7 UNCHANGED / FROZEN 8ed43721
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
ROOT = Path(__file__).resolve().parents[1]

# --- locked metric constants (align formal leaf33 afbbe7e7) ---
PRESSURE_W = 20
REBAL_EVERY = 20
PRESSURE_MIN_VALID = 15  # formal α gate; NOT used to redefine n_unlock_pool (>=1 event)
TZ_ALIGN_MODE = "naive_calendar_day"
X2_START = "2024-06-03"
X2_END = "2026-10-09"
COVERAGE_MEDIAN_HILIQ_READONLY = 300  # DO NOT CHANGE; probe never lowers gate
FORMAL_SCRIPT_SHA8_PIN = "afbbe7e7"
FORMAL_SCRIPT_REL = "research/leaf33_share_unlock_pressure_resid_alpha_build.py"

UPSTREAM_PINS = {
    "arch_void_sha8": "6826c01d",
    "ai_run_abort_sha8": "a1b426f5",
    "recon_draft_sha8": "b84496fe",
    "arch_recon_review_sha8": "29166bf7",
    "alpha_sha8": "ea17e173",
    "overlap_sha8": "473b339e",
    "run_meta_sha8": "f4702783",
    "frozen_sha8": "8ed43721",
    "pin_sha8": "4e17ccfc",
    "frozen_review_sha8": "bf5234a9",
    "formal_script_sha8": FORMAL_SCRIPT_SHA8_PIN,
}

# Named RESTORED bans (leaf33 VOID ok + prior + FROZEN forbid set head)
FORBID_OK_SHA8 = frozenset(
    {
        "245df63f",  # leaf33 X2 tz-align VOID.ABORT_COVERAGE_GATE — ban RESTORED
        "c5ed13df",  # prior leaf33 ban (Main named)
        "5774bb6e",
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
)

DEFAULT_OUT_DIR = ROOT / "output/ai_factory/_leaf33_share_unlock/diag_n_unlock_pool_v1"
ALPHA_DEFAULT = ROOT / (
    "output/ai_factory/_leaf33_share_unlock/20261027_072135/"
    "alpha_HILIQ_x2_20261027_072552.parquet"
)
RUN_META_DEFAULT = ROOT / (
    "output/ai_factory/_leaf33_share_unlock/20261027_072135/run_meta.json"
)
HI_LIQ_MASK_DEFAULT = ROOT / "output/strategy_hiliq/universe_mask_hiliq_v1.parquet"
SHARE_FLOAT_DEFAULT = ROOT / "data/v2/share_float/share_float_pit.parquet"
CAL_DEFAULT = ROOT / "data/v2/calendar/trade_cal_sse_pit.parquet"
SAMPLER_PREFIX = "/tmp/quantlab_leaf33_n_unlock_pool_diag_"

INTENDED_SCHEMA = {
    "per_rebal_row": [
        "date",
        "n_unlock_pool",
        "n_alpha",
        "ratio",
    ],
    "summary_keys": [
        "n_unlock_pool_median_p10_p25_p75_p90_min_max",
        "n_alpha_median_p10_p25_p75_p90_min_max",
        "ratio_median_p10_p25_p75_p90_min_max",
        "upstream_pins",
        "theta_undecided",
        "live",
        "promotion_approved",
        "x2_accept",
        "executed",
    ],
    "notes": (
        "ratio = n_alpha / n_unlock_pool; denom 0 -> NaN; "
        "theta NOT decided here; gate 300 NOT changed"
    ),
}


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def assert_tmp_quantlab(p: Path, label: str) -> None:
    s = str(p.resolve())
    if not s.startswith("/tmp/quantlab_"):
        print(f"STOP: {label} must be under /tmp/quantlab_* got={s}", file=sys.stderr)
        raise SystemExit(2)


def verify_formal_script_unchanged() -> str:
    p = ROOT / FORMAL_SCRIPT_REL
    if not p.is_file():
        print(f"STOP: formal script missing: {p}", file=sys.stderr)
        raise SystemExit(2)
    got = sha256_file(p)[:8]
    if got != FORMAL_SCRIPT_SHA8_PIN:
        print(
            f"STOP: formal script sha8 drift expected={FORMAL_SCRIPT_SHA8_PIN} got={got}",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return got


def dist_stats(vals: list[float]) -> dict:
    import numpy as np

    if not vals:
        return {
            "n": 0,
            "median": None,
            "p10": None,
            "p25": None,
            "p75": None,
            "p90": None,
            "min": None,
            "max": None,
        }
    a = np.asarray(vals, dtype=float)
    # drop NaN for ratio stats
    a = a[~np.isnan(a)]
    if a.size == 0:
        return {
            "n": 0,
            "median": None,
            "p10": None,
            "p25": None,
            "p75": None,
            "p90": None,
            "min": None,
            "max": None,
        }
    return {
        "n": int(a.size),
        "median": float(np.median(a)),
        "p10": float(np.percentile(a, 10)),
        "p25": float(np.percentile(a, 25)),
        "p75": float(np.percentile(a, 75)),
        "p90": float(np.percentile(a, 90)),
        "min": float(a.min()),
        "max": float(a.max()),
    }


def dry_run_print(args: argparse.Namespace) -> int:
    formal_sha8 = verify_formal_script_unchanged()
    plan = {
        "role": "leaf33_A1_n_unlock_pool_diag_probe_v1",
        "kind": "DIAGNOSTIC_PROBE_NOT_FORMAL_ALPHA",
        "mode": "dry-run",
        "executed": False,
        "live": False,
        "promotion_approved": False,
        "x2_accept": False,
        "ok_requested": False,
        "theta_undecided": True,
        "theta_discussion_range": [0.5, 0.8],
        "theta_self_decided": False,
        "coverage_median_hiliq_readonly": COVERAGE_MEDIAN_HILIQ_READONLY,
        "gate_change_forbidden": True,
        "formal_script": FORMAL_SCRIPT_REL,
        "formal_script_sha8": formal_sha8,
        "formal_script_import_forbidden": True,
        "metric_pins": {
            "pressure_W": PRESSURE_W,
            "rebal_every_td": REBAL_EVERY,
            "tz_align_mode": TZ_ALIGN_MODE,
            "x2_start": X2_START,
            "x2_end": X2_END,
            "n_unlock_pool_def": (
                "HI_LIQ ∩ (>=1 PIT-visible share_float unlock event in W=20 "
                "trading-day window); available_at via naive_calendar_day"
            ),
            "n_alpha_def": (
                "count non-null pressure_resid/alpha on rebal day "
                "(= formal coverage_rebal.n when sourced from run_meta)"
            ),
            "ratio_def": "n_alpha / n_unlock_pool; denom0->NaN",
            "rebal_day_set": (
                "trade calendar days[::REBAL_EVERY] inside X2 window, "
                "aligned with formal leaf33 / FROZEN / run_meta coverage_rebal dates"
            ),
        },
        "upstream_pins": UPSTREAM_PINS,
        "forbid_ok_sha8_head": sorted(list(FORBID_OK_SHA8))[:8],
        "forbid_ok_sha8_n": len(FORBID_OK_SHA8),
        "intended_out_dir": str(args.out or DEFAULT_OUT_DIR),
        "intended_outputs": [
            "per_rebal_n_unlock_pool_diag.json",
            "summary_n_unlock_pool_diag.json",
        ],
        "intended_schema": INTENDED_SCHEMA,
        "real_path_gate": {
            "requires_allow_real_data": True,
            "requires_existing_arch_ok_path": True,
            "no_default_arch_ok_path": True,
            "ban_restored_ok": True,
        },
        "reads_on_real_path_only": [
            "trade calendar",
            "HI_LIQ universe mask",
            "share_float PIT (available_at)",
            "optional: landed alpha / run_meta for n_alpha cross-check",
        ],
        "reads_forbidden_on_dry": [
            "share_float",
            "daily bars",
            "HI_LIQ mask (full table)",
        ],
        "note_zh": (
            "本脚本=诊断探针，≠正式α构建，≠降门补丁；"
            "θ∈0.5–0.8等主钉；本拍默认 dry 不实跑"
        ),
        "created_et": datetime.now(ET).isoformat(timespec="seconds"),
    }
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    print(
        "DRY_RUN_OK formal_script_sha8=%s gate_readonly=%s theta_undecided=true"
        % (formal_sha8, COVERAGE_MEDIAN_HILIQ_READONLY),
        flush=True,
    )
    return 0


def run_real(args: argparse.Namespace) -> int:
    """Real diagnostic path — NOT invoked by this ticket (EXECUTED=false)."""
    # Gate
    if not args.allow_real_data:
        print(
            "STOP: real path requires --allow-real-data + --arch-ok-path",
            file=sys.stderr,
        )
        return 2
    if args.arch_ok_path is None or not Path(args.arch_ok_path).is_file():
        print(
            "STOP: --allow-real-data requires existing --arch-ok-path",
            file=sys.stderr,
        )
        return 2
    ok_sha_full = sha256_file(Path(args.arch_ok_path))
    ok_sha8 = ok_sha_full[:8]
    if ok_sha8 in FORBID_OK_SHA8 or ok_sha_full in FORBID_OK_SHA8:
        print(f"STOP: ban RESTORED/forbid .ok sha8={ok_sha8}", file=sys.stderr)
        return 2

    formal_sha8 = verify_formal_script_unchanged()

    if args.sample_dir is not None:
        assert_tmp_quantlab(Path(args.sample_dir), "sample-dir")

    # Lazy imports only on real path
    try:
        import numpy as np
        import pyarrow.parquet as pq
        import pandas as pd
    except ImportError as e:
        print(f"STOP: missing dep for real path: {e}", file=sys.stderr)
        return 2

    cal_p = Path(args.calendar)
    mask_p = Path(args.hi_liq_mask)
    sf_p = Path(args.share_float)
    for label, p in (
        ("calendar", cal_p),
        ("hi_liq_mask", mask_p),
        ("share_float", sf_p),
    ):
        if not p.is_file():
            print(f"STOP: missing {label}: {p}", file=sys.stderr)
            return 2

    # --- calendar / rebal days (align formal: days[::REBAL_EVERY] in X2) ---
    cal = pq.read_table(cal_p).to_pandas()
    # tolerate common col names
    date_col = None
    for c in ("cal_date", "trade_date", "date"):
        if c in cal.columns:
            date_col = c
            break
    if date_col is None:
        print(f"STOP: calendar missing date col cols={list(cal.columns)}", file=sys.stderr)
        return 2
    open_col = None
    for c in ("is_open", "open"):
        if c in cal.columns:
            open_col = c
            break
    dser = cal[date_col].astype(str).str.replace("-", "").str.slice(0, 8)
    if open_col is not None:
        opens = cal[open_col].astype(int) == 1
        dser = dser[opens]
    # normalize to YYYY-MM-DD
    days_all = sorted(
        {
            f"{d[:4]}-{d[4:6]}-{d[6:8]}"
            for d in dser.tolist()
            if len(d) == 8 and d.isdigit()
        }
    )
    days = [d for d in days_all if X2_START <= d <= X2_END]
    if len(days) < REBAL_EVERY:
        print(f"STOP: too few x2 trade days n={len(days)}", file=sys.stderr)
        return 2
    rebal_days = days[::REBAL_EVERY]
    day_index = {d: i for i, d in enumerate(days)}

    # --- HI_LIQ membership by date ---
    mask = pq.read_table(mask_p).to_pandas()
    # expect date / instrument / in_universe (formal KNOWN_MASK_COLS)
    m_date = "date" if "date" in mask.columns else ("trade_date" if "trade_date" in mask.columns else None)
    m_inst = (
        "instrument"
        if "instrument" in mask.columns
        else ("ts_code" if "ts_code" in mask.columns else None)
    )
    m_in = "in_universe" if "in_universe" in mask.columns else None
    if m_date is None or m_inst is None or m_in is None:
        print(
            f"STOP: HI_LIQ mask schema unexpected cols={list(mask.columns)}",
            file=sys.stderr,
        )
        return 2
    mask = mask[mask[m_in].astype(bool)].copy()
    mask["_d"] = mask[m_date].astype(str).str.replace("/", "-").str.slice(0, 10)
    # normalize YYYYMMDD -> YYYY-MM-DD
    def _norm_d(s: str) -> str:
        s = str(s).replace("-", "").replace("/", "")[:8]
        if len(s) == 8 and s.isdigit():
            return f"{s[:4]}-{s[4:6]}-{s[6:8]}"
        return str(s)[:10]

    mask["_d"] = mask[m_date].map(_norm_d)
    mask["_c"] = mask[m_inst].astype(str)
    hiliq_by_day: dict[str, set[str]] = {}
    for d, g in mask.groupby("_d", sort=False):
        if d in day_index or d in set(rebal_days):
            hiliq_by_day[d] = set(g["_c"].tolist())

    # --- share_float PIT events (naive_calendar_day on available_at) ---
    sf = pq.read_table(sf_p).to_pandas()
    need = {"ts_code", "available_at"}
    # float_date optional for event identity
    if not need.issubset(set(sf.columns)):
        print(
            f"STOP: share_float missing cols need={need} got={list(sf.columns)}",
            file=sys.stderr,
        )
        return 2
    sf = sf.copy()
    sf["_code"] = sf["ts_code"].astype(str)
    # tz_align_mode=naive_calendar_day: take calendar date of available_at as-is
    aa = sf["available_at"]
    if hasattr(aa.dtype, "tz") and aa.dtype.tz is not None:
        # still take calendar date in naive sense after drop tz? formal: naive_calendar_day
        aa = aa.dt.tz_localize(None) if aa.dt.tz is not None else aa
    # pandas Timestamp / string
    sf["_avail_d"] = pd.to_datetime(aa, errors="coerce").dt.strftime("%Y-%m-%d")
    sf = sf.dropna(subset=["_avail_d"])
    # map avail day -> nearest trade day index (event visible from avail trade day onward)
    # For pool: event counts in W window of rebal day if avail trade-day index in (i_rebal-W+1 .. i_rebal]
    # Align formal pressure window semantics: W trading days ending at rebal day.
    avail_to_td_idx = {}
    # precompute for unique avail days
    for ad in sorted(sf["_avail_d"].unique()):
        # first trade day >= avail calendar day
        # linear scan via days list
        # binary search
        import bisect

        j = bisect.bisect_left(days, ad)
        if j < len(days):
            avail_to_td_idx[ad] = j
    sf["_td_i"] = sf["_avail_d"].map(avail_to_td_idx)
    sf = sf.dropna(subset=["_td_i"])
    sf["_td_i"] = sf["_td_i"].astype(int)

    # index events by trade-day index for fast window queries
    # build code sets per trade day index that have >=1 event becoming visible that day
    from collections import defaultdict

    events_by_tdi: dict[int, set[str]] = defaultdict(set)
    for tdi, code in zip(sf["_td_i"].tolist(), sf["_code"].tolist()):
        events_by_tdi[int(tdi)].add(code)

    # optional n_alpha from run_meta or alpha
    n_alpha_map: dict[str, int] = {}
    if Path(args.run_meta).is_file():
        meta_obj = json.loads(Path(args.run_meta).read_text(encoding="utf-8"))
        for row in meta_obj.get("coverage_rebal", []):
            n_alpha_map[str(row["date"])] = int(row["n"])
    elif Path(args.alpha).is_file():
        adf = pq.read_table(Path(args.alpha)).to_pandas()
        g = (
            adf.groupby(adf["trade_date"].astype(str))["alpha"]
            .apply(lambda s: int(s.notna().sum()))
            .to_dict()
        )
        n_alpha_map = {str(k): int(v) for k, v in g.items()}

    rows = []
    for d in rebal_days:
        i = day_index[d]
        lo = i - PRESSURE_W + 1
        if lo < 0:
            lo = 0
        # codes with >=1 event whose visible trade-day index in [lo, i]
        pool: set[str] = set()
        for tdi in range(lo, i + 1):
            pool |= events_by_tdi.get(tdi, set())
        hiliq = hiliq_by_day.get(d, set())
        unlock_pool = pool & hiliq
        n_pool = int(len(unlock_pool))
        n_a = n_alpha_map.get(d)
        if n_a is None:
            ratio = float("nan")
        elif n_pool == 0:
            ratio = float("nan")
        else:
            ratio = float(n_a) / float(n_pool)
        rows.append(
            {
                "date": d,
                "n_unlock_pool": n_pool,
                "n_alpha": n_a,
                "ratio": (None if (isinstance(ratio, float) and math.isnan(ratio)) else ratio),
            }
        )

    pool_vals = [float(r["n_unlock_pool"]) for r in rows]
    alpha_vals = [float(r["n_alpha"]) for r in rows if r["n_alpha"] is not None]
    ratio_vals = []
    for r in rows:
        if r["n_alpha"] is None:
            continue
        if r["n_unlock_pool"] == 0:
            ratio_vals.append(float("nan"))
        else:
            ratio_vals.append(float(r["n_alpha"]) / float(r["n_unlock_pool"]))

    summary = {
        "role": "leaf33_A1_n_unlock_pool_diag_probe_v1",
        "kind": "DIAGNOSTIC_PROBE_NOT_FORMAL_ALPHA",
        "executed": True,
        "live": False,
        "promotion_approved": False,
        "x2_accept": False,
        "ok_requested": False,
        "theta_undecided": True,
        "theta_discussion_range": [0.5, 0.8],
        "theta_self_decided": False,
        "forbid_theta_recommendation_in_output": True,
        "coverage_median_hiliq_readonly": COVERAGE_MEDIAN_HILIQ_READONLY,
        "gate_changed": False,
        "formal_script_sha8": formal_sha8,
        "arch_ok_sha8": ok_sha8,
        "arch_ok_path": str(args.arch_ok_path),
        "metric_pins": {
            "pressure_W": PRESSURE_W,
            "rebal_every_td": REBAL_EVERY,
            "tz_align_mode": TZ_ALIGN_MODE,
            "x2_start": X2_START,
            "x2_end": X2_END,
            "n_rebal_days": len(rebal_days),
        },
        "upstream_pins": UPSTREAM_PINS,
        "n_unlock_pool_dist": dist_stats(pool_vals),
        "n_alpha_dist": dist_stats(alpha_vals),
        "ratio_dist": dist_stats(ratio_vals),
        "per_rebal_n": len(rows),
        "created_et": datetime.now(ET).isoformat(timespec="seconds"),
        "note_zh": (
            "诊断探针实跑汇总；θ未自决；≠正式α；≠降门；≠X2 ACCEPT"
        ),
    }

    out_dir = Path(args.out) if args.out else DEFAULT_OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    per_path = out_dir / "per_rebal_n_unlock_pool_diag.json"
    sum_path = out_dir / "summary_n_unlock_pool_diag.json"
    per_path.write_text(
        json.dumps({"rows": rows, "upstream_pins": UPSTREAM_PINS}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    sum_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"wrote": [str(per_path), str(sum_path)], "summary": summary}, ensure_ascii=False, indent=2))
    # re-verify formal unchanged at end
    verify_formal_script_unchanged()
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Leaf33 A1 n_unlock_pool diagnostic probe v1 "
            "(NOT formal alpha; default dry-run)"
        )
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Default: print pins/plan/schema only; no real tables",
    )
    ap.add_argument(
        "--allow-real-data",
        action="store_true",
        default=False,
        help="Required for real diagnostic path (needs existing --arch-ok-path)",
    )
    ap.add_argument(
        "--no-dry-run",
        action="store_true",
        help="Disable dry-run (still requires --allow-real-data)",
    )
    ap.add_argument(
        "--arch-ok-path",
        type=Path,
        default=None,
        help="Path to Arch diagnostic .ok (required with --allow-real-data; no default)",
    )
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--sample-dir", type=Path, default=None)
    ap.add_argument("--hi-liq-mask", type=Path, default=HI_LIQ_MASK_DEFAULT)
    ap.add_argument("--share-float", type=Path, default=SHARE_FLOAT_DEFAULT)
    ap.add_argument("--calendar", type=Path, default=CAL_DEFAULT)
    ap.add_argument("--alpha", type=Path, default=ALPHA_DEFAULT)
    ap.add_argument("--run-meta", type=Path, default=RUN_META_DEFAULT)
    args = ap.parse_args(argv)

    if args.allow_real_data:
        dry = False
    elif args.no_dry_run:
        print("STOP: --no-dry-run requires --allow-real-data", file=sys.stderr)
        return 2
    else:
        dry = True

    if dry:
        return dry_run_print(args)
    return run_real(args)


if __name__ == "__main__":
    raise SystemExit(main())
