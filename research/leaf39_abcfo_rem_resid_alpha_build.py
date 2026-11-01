#!/usr/bin/env python3
"""Leaf39 ABCFO REM residual α — formal build (NOT authorized this LAND beat).

LAND_SCRIPT 2026-10-28 ~00:10 ET America/New_York.
Nails PREREG_FROZEN sha8 150d1a28; FROZEN RECEIPT 507f09f1;
Arch FROZEN review b51a59a0 PASS_WC; Arch who_pays DRAFT review 4a1b4dd0;
who DRAFT 542138d6 / DRAFT RECEIPT 691bbc14 / COUNT d0d11598 /
COUNT script 20313ba3 (NOT this formal build) / dig 440410de;
HI_LIQ mask c5433e80.

Engineering skeleton (RSS / peak_proof / Exit 94·95 / single-thread) from
leaf38 §6.1 + leaf30 r3_peakcut — read-only; ban copy mask-overlay / CRR formulas.
ABCFO formula aligned to COUNT script 20313ba3 (YTD→qtr; SW L1 cross-section OLS).

Mechanism (FROZEN; mechanism_tag=g1g5_ashare_abcfo_rem_resid_v1):
  YTD→single-quarter: CFO/A ~ 1/A + S/A + ΔS/A  (rebal-day SW L1 OLS APPROX; C2(a) NO panel)
  ABCFO=ε; raw = −ε; α = SW L1 demean + vs log(float_mktcap) OLS (+style if easy)
  PRIMARY = daily residual α vector parquet (NOT Top-N; NOT exclusion mask)
  Mask: bank 801780.SI / realty 801180.SI / nonbank 801790.SI + HI_LIQ
  PIT: available_at ≤ t (Asia/Shanghai wall; ban peek)
  Hard gate: vs leaf19/25/30 Jaccard ∨ formal ρ_excess any >0.5 → reject
  C2(b): Spearman is gate proxy only; formal ρ_excess path required (see --skip-rho-excess)
  C3: vs leaf34 exclusion Jaccard PIN; CLI --leaf34-jaccard; hard 0.5; ban rewrite PRIMARY
  Window intent 2024-06-03→2026-10-09; rebal 20; cost 30bp (eval; no PnL select)
  KEEP ≠ ACCEPT; decay near-window 252td (script does not execute decay gate)

§ peak path (align leaf38 §6.1 + leaf30 r3):
  rss≤1500 ban raise; --rss-limit-mb >1500 → STOP
  peak_proof REQUIRED; Exit 94 soft/split; Exit 95 hard ABORT
  single thread OMP/MKL=1; year/block parquet read; del+gc; ban parallel RSS stack
  Default entry: --dry-compile-only or --help (this LAND: py_compile + dry only)

PRIMARY CLI: --universe HILIQ --window x2
Real path: --allow-real-data + existing --arch-ok-path (sha8 ∉ forbid)
Default / --dry-compile-only: print pins; ZERO big-table load; exit 0
Ban self-sign .ok / Book-Smoke / self-run X2 / QUIET
Ban RESTORED f08ce32c / 335635dd; ban mix fund ba7609af/fbc1bd9a; ban mix leaf38 c01c2034/5f694370
Ban raise CRR_MOD2 / IO to PRIMARY (C5)
COUNT gate_pass ≠ X2 ACCEPT (C9)
live=false; promotion=false; ok_requested=false; EXECUTED_full_alpha=false; ≠X2 ACCEPT
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import resource
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# § peak-4 single-thread: pin before any numeric import on real path
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")

ET = ZoneInfo("America/New_York")
SH = ZoneInfo("Asia/Shanghai")
ROOT = Path(__file__).resolve().parents[1]
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

MECHANISM_TAG = "g1g5_ashare_abcfo_rem_resid_v1"
SCRIPT_REL = "research/leaf39_abcfo_rem_resid_alpha_build.py"
FROZEN_REL = "docs/v2/audit/AI_LEAF39_ABCFO_REM_RESID_PREREG_FROZEN_20261027_ZH.md"
FROZEN_SHA8 = "150d1a28"
FROZEN_RECEIPT_SHA8 = "507f09f1"
ARCH_FROZEN_REVIEW_SHA8 = "b51a59a0"
ARCH_WHO_PAYS_REVIEW_SHA8 = "4a1b4dd0"
WHO_PAYS_SHA8 = "542138d6"
DRAFT_RECEIPT_SHA8 = "691bbc14"
COUNT_JSON_SHA8 = "d0d11598"
COUNT_SCRIPT_SHA8 = "20313ba3"  # audit COUNT; NOT this formal build
DIG_SHA8 = "440410de"  # 文内 87f65bbe 勿采
HI_LIQ_MASK_SHA8_PIN = "c5433e80"
LEAF34_FORMAL_SHA8_READONLY = "482009dc"
LEAF38_SCRIPT_SHA8_BAN_MIX = "3a44471d"  # engineering template only; ban mix product
LEAF30_R3_TEMPLATE_SHA8_READONLY = "3ee9fed2"  # RSS/resid skeleton only; ban CRR copy

RSS_LIMIT_MB = 1500
C4_KB = 1331200
STOP_KB = 1484800
HARD_KB = 1536000  # ~1500 MiB hard; Exit 95
SPLIT_THRESH_KB = int(0.85 * C4_KB)  # Exit 94 split further
# Exit codes (align leaf38/37): 94 = soft/split ABORT; 95 = hard ABORT

X2_START = "2024-06-03"
X2_END = "2026-10-09"
X2_END_TRADE_DATE = "20261009"
REBAL_EVERY = 20
PRIMARY_DELIVERY = "residual_alpha_vector"
ALPHA_SIGN = "alpha_propto_neg_ABCFO_long_high_abnormal_CFO"
IC_SIGN_EXPECTED = "positive_comment_only_no_returns"
COST_BP_EVAL = 30
COV_MEDIAN_MIN = 300.0
ZERO_FRAC_MAX = 0.05
HARD_OVERLAP = 0.5
SW_OLS_MIN_N = 25

C2A_PIN = "cross_section_SW_L1_OLS_APPROX_no_year_industry_panel"
C2B_PIN = "formal_rho_excess_required_before_X2_Spearman_is_gate_proxy_only"
C3_PIN = (
    "vs_leaf34_exclusion_Jaccard_PIN; hard_reject_0.5; "
    "ban_posthoc_PRIMARY_rewrite; CLI --leaf34-jaccard"
)
C8_PIN = "PRIMARY=residual_alpha_vector_NOT_exclusion_mask_NOT_TopN"
C9_PIN = "COUNT_gate_pass_NOT_X2_ACCEPT"

DECAY_KEEP_PIN = {
    "latest_resid_alpha_gt_0": True,
    "not_five_quarter_decline": True,
    "H2_net_cagr_gt_510300": True,
    "near_window_td": 252,
    "min_td_for_alpha": 126,
    "keep_does_not_unblock_x2_accept": True,
    "note": (
        "KEEP = conjunction of three gates; script does not execute decay gate; "
        "KEEP does NOT unblock X2 ACCEPT (leaf32 HOLD 45dd87dc lesson)"
    ),
}

FORBID_OK_SHA8 = (
    "f08ce32c",  # fund RESTORED — ban
    "335635dd",  # fund MDD BS .ok archived — ban RESTORED
    "c01c2034",  # leaf38 CONSUMED_PASS — ban mix
    "5f694370",  # leaf38 HOLD CLOSED — ban mix
    "ba7609af",  # fund MDD Arch — ban mix product
    "fbc1bd9a",  # fund MDD CONSUME — ban mix
    "5af20222",  # leaf30 R2 VOID
    "5ae077fa",  # leaf30 R1 VOID
    "3c297052",
    "e107383f",
    "2be59acd",
    "1c32ab1e",
    "ebc673bf",
    "a7d98ac9",
    "8e51de63",
    "3a6caa4f",
    "8bcd79dc",
    "725be3e0",
    "0f50daf7",
    "3c19dd7d",
    "6054b3bf",
    "6de02e74",
)

FP = ROOT / "data/v2/financials_pit"
PIT_CF = FP / "cashflow_pit_tushare.parquet"
PIT_FIN = FP / "financials_pit_tushare.parquet"
PIT_BS = FP / "bs_cf_pit_tushare.parquet"
HI_LIQ_MASK_DEFAULT = ROOT / "output/strategy_hiliq/universe_mask_hiliq_v1.parquet"
SW_L1_DEFAULT = ROOT / "data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet"
FLOAT_MKTCAP_DEFAULT = (
    ROOT / "data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet"
)
CAL_DEFAULT = ROOT / "data/v2/calendar/trade_cal_sse_pit.parquet"
OUT_DEFAULT = ROOT / "output/ai_factory/_leaf39_abcfo_rem_resid"
SAMPLER_PREFIX = "/tmp/quantlab_leaf39_abcfo_"

LEAF19_ALPHA_DEFAULT = (
    ROOT / "output/ai_factory/leaf19_cfacc_rnoa/alpha_HILIQ_20261014_213132.parquet"
)
LEAF25_ALPHA_DEFAULT = ROOT / (
    "output/ai_factory/_leaf25_full_factor/20261026_015610/"
    "alpha_HILIQ_x2_20261026_125138.parquet"
)
LEAF30_ALPHA_DEFAULT = ROOT / (
    "output/ai_factory/_leaf30_crr/20261027_003132/"
    "alpha_HILIQ_x2_20261027_010815.parquet"
)
LEAF34_MASK_DEFAULT = ROOT / (
    "output/ai_factory/_leaf34_high_accrual/20261027_105941/"
    "exclusion_mask_HILIQ_x2_20261027_105958.parquet"
)

EXCLUDE_SW = {
    "银行": "801780.SI",
    "房地产": "801180.SI",
    "非银金融": "801790.SI",
}
# 综合 = 801230.SI is NOT in this mask (FROZEN §2)

KNOWN_CF_COLS = ["ts_code", "end_date", "available_at", "n_cashflow_act"]
KNOWN_FIN_COLS = ["ts_code", "end_date", "available_at", "revenue", "total_revenue"]
KNOWN_BS_COLS = ["ts_code", "end_date", "available_at", "total_assets"]
KNOWN_MASK_COLS = ["date", "instrument", "in_universe"]
KNOWN_ALPHA_OUT_COLS = ["trade_date", "ts_code", "alpha", "abcfo", "raw"]
KNOWN_SW_COLS = [
    "instrument_id",
    "sw_code",
    "sw_name",
    "in_date",
    "out_date",
    "available_at",
]
KNOWN_FLOAT_COLS = ["instrument_id", "trade_date", "float_mktcap"]


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


def vmrss_kb() -> int | None:
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1])
    except OSError:
        return None
    return None


def peak_kb() -> int:
    ru = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    hw = vmhwm_kb()
    return max(ru, hw) if hw is not None else ru


def check_rss(
    label: str, *, rss_limit_mb: int, c4_kb: int, hard_kb: int, split_kb: int
) -> int:
    """peak_proof path. Exit 94 soft/split; Exit 95 hard. Ban raise cap."""
    pk = peak_kb()
    soft_kb = int(rss_limit_mb) * 1024
    vr = vmrss_kb()
    print(
        f"RSS_CHECK {label} peak_kb={pk} vmrss_kb={vr} "
        f"soft={soft_kb} split={split_kb} c4={c4_kb} hard={hard_kb} "
        f"peak_rss_mb={pk / 1024.0:.1f}",
        flush=True,
    )
    if pk >= hard_kb or (vr is not None and vr >= hard_kb):
        print(
            f"STOP: RSS hard breached peak_kb={pk} vmrss={vr} >= hard={hard_kb}; "
            f"Exit 95 ABORT (ban raise rss)",
            file=sys.stderr,
        )
        raise SystemExit(95)
    if (vr is not None and vr >= soft_kb) or pk >= soft_kb:
        print(
            f"STOP: RSS soft {rss_limit_mb}MB breached peak_kb={pk} vmrss={vr} "
            f">= soft={soft_kb}; Exit 94 ABORT no self-retry",
            file=sys.stderr,
        )
        raise SystemExit(94)
    if pk >= split_kb:
        print(
            f"STOP: RSS >= 0.85*C4 peak_kb={pk} >= split={split_kb}; "
            f"Exit 94 split further — ban raise cap",
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


def script_sha256() -> str:
    return sha256_file(Path(__file__).resolve())


def to_ts(x) -> str:
    """Normalize to ts_code form 600829.SH."""
    s = str(x)
    if s.startswith(("sh.", "sz.", "bj.")):
        mkt, code = s.split(".", 1)
        return f"{code}.{mkt.upper()}"
    return s


def normalize_universe(u: str) -> str:
    u = (u or "").strip()
    if u in ("HILIQ", "HI_LIQ"):
        return "HILIQ"
    if u == "FULLA":
        return "FULLA"
    raise SystemExit(f"STOP: unknown --universe={u!r}; PRIMARY is HILIQ")


def enforce_single_thread() -> None:
    for k in (
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
    ):
        os.environ[k] = "1"
    try:
        import torch  # type: ignore

        torch.set_num_threads(1)
    except Exception:
        pass


def dry_compile_only_print(args) -> int:
    """Zero big-table load; print hard pins for Arch/Main precheck."""
    uni = normalize_universe(args.universe) if args.universe != "FULLA" else "FULLA"
    try:
        scr = script_sha256()
    except OSError:
        scr = "<unreadable>"
    skip_rho = bool(getattr(args, "skip_rho_excess", True))
    leaf34_j = bool(getattr(args, "leaf34_jaccard", False))
    payload = {
        "live": False,
        "ok_requested": False,
        "promotion_approved": False,
        "executed": False,
        "EXECUTED_full_alpha": False,
        "x2_accept": False,
        "approx": True,
        "approx_note": (
            "C2(a): rebal-day SW L1 cross-section OLS APPROX "
            "(NOT year×industry historical panel); COUNT d0d11598 not re-run. "
            "C2(b): Spearman ≠ ρ_excess; formal ρ_excess path required before X2 "
            f"(--skip-rho-excess default on LAND={skip_rho}; open before X2)."
        ),
        "land_script": True,
        "rss_limit_mb": RSS_LIMIT_MB,
        "c4_kb": C4_KB,
        "stop_kb": STOP_KB,
        "hard_kb": HARD_KB,
        "split_thresh_kb": SPLIT_THRESH_KB,
        "exit_soft_abort": 94,
        "exit_hard_abort": 95,
        "universe_cli": uni,
        "primary_universe": "HILIQ",
        "ban_silent_fulla_as_primary": True,
        "window": getattr(args, "window", "x2"),
        "window_start": getattr(args, "window_start", X2_START),
        "window_end": getattr(args, "window_end", X2_END),
        "x2_window": f"{X2_START} → {X2_END}",
        "rebal_every_td": REBAL_EVERY,
        "primary_delivery": PRIMARY_DELIVERY,
        "alpha_sign": ALPHA_SIGN,
        "ic_sign_expected": IC_SIGN_EXPECTED,
        "mechanism_tag": MECHANISM_TAG,
        "script": SCRIPT_REL,
        "script_sha256": scr,
        "script_sha8": scr[:8] if isinstance(scr, str) and len(scr) >= 8 else None,
        "frozen_rel": FROZEN_REL,
        "frozen_sha8": FROZEN_SHA8,
        "frozen_receipt_sha8": FROZEN_RECEIPT_SHA8,
        "arch_frozen_review_sha8": ARCH_FROZEN_REVIEW_SHA8,
        "arch_who_pays_review_sha8": ARCH_WHO_PAYS_REVIEW_SHA8,
        "who_pays_sha8": WHO_PAYS_SHA8,
        "draft_receipt_sha8": DRAFT_RECEIPT_SHA8,
        "count_json_sha8": COUNT_JSON_SHA8,
        "count_script_sha8_NOT_formal": COUNT_SCRIPT_SHA8,
        "dig_sha8": DIG_SHA8,
        "hi_liq_mask_sha8_pin": HI_LIQ_MASK_SHA8_PIN,
        "leaf34_formal_sha8_readonly": LEAF34_FORMAL_SHA8_READONLY,
        "leaf30_r3_template_sha8_readonly": LEAF30_R3_TEMPLATE_SHA8_READONLY,
        "leaf38_script_sha8_ban_mix_product": LEAF38_SCRIPT_SHA8_BAN_MIX,
        "forbid_ok_sha8": list(FORBID_OK_SHA8),
        "sampler_prefix": SAMPLER_PREFIX,
        "out_intent": str(OUT_DEFAULT.relative_to(ROOT)),
        "c2a_pin": C2A_PIN,
        "c2b_pin": C2B_PIN,
        "c3_pin": C3_PIN,
        "c8_pin": C8_PIN,
        "c9_pin": C9_PIN,
        "skip_rho_excess": skip_rho,
        "leaf34_jaccard_cli": leaf34_j,
        "cost_bp_eval": COST_BP_EVAL,
        "decay_keep_pin": DECAY_KEEP_PIN,
        "industry_exclude": EXCLUDE_SW,
        "coverage_masked_median_min": COV_MEDIAN_MIN,
        "zero_frac_max": ZERO_FRAC_MAX,
        "hard_overlap": HARD_OVERLAP,
        "abcfo_pipeline": [
            "PIT cashflow.n_cashflow_act + financials.total_revenue|revenue + bs.total_assets",
            "YTD→single-quarter differencing within fiscal year (Q1 no diff)",
            "A_lag = prior end_date total_assets",
            "dS = sales_q − sales_q_lag",
            "rebal-day: HI_LIQ ∩ ¬{银行,房地产,非银金融}",
            "SW L1 cross-section OLS: CFO/A ~ 1 + 1/A + S/A + dS/A → ε=ABCFO (n<25 → market fallback)",
            "raw = −ε; α = SW L1 demean + vs logmv OLS resid (+style if easy)",
            "PRIMARY deliver = daily residual α vector parquet (NOT Top-N; NOT mask)",
            "PIT: available_at ≤ t; ban peek",
        ],
        "section_peak_path": {
            "stream_chunk_year_or_block": True,
            "del_gc_after_blocks": True,
            "single_thread": True,
            "hard_abort_exit_94_95": True,
            "peak_proof_le_1500_required": True,
            "ban_raise_rss": True,
            "logmv_lazy_per_rebal": True,
        },
        "overlap_hard_targets": ["leaf19", "leaf25", "leaf30"],
        "overlap_pin_targets": ["leaf34"],
        "pit_main": {
            "cashflow": str(PIT_CF.relative_to(ROOT)),
            "financials": str(PIT_FIN.relative_to(ROOT)),
            "bs_cf": str(PIT_BS.relative_to(ROOT)),
        },
        "leaf19_alpha": str(LEAF19_ALPHA_DEFAULT.relative_to(ROOT)),
        "leaf25_alpha": str(LEAF25_ALPHA_DEFAULT.relative_to(ROOT)),
        "leaf30_alpha": str(LEAF30_ALPHA_DEFAULT.relative_to(ROOT)),
        "leaf34_mask": str(LEAF34_MASK_DEFAULT.relative_to(ROOT)),
        "primary_cli": (
            f"PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python {SCRIPT_REL} "
            f"--universe HILIQ --window x2 --window-start {X2_START} "
            f"--window-end {X2_END} --allow-real-data --arch-ok-path <OK> "
            f"--out-dir <OUT>"
        ),
        "dry_cli": (
            f"PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python {SCRIPT_REL} "
            f"--dry-compile-only"
        ),
        "leaf34_jaccard_cli_example": (
            f"PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python {SCRIPT_REL} "
            f"--leaf34-jaccard --allow-real-data --arch-ok-path <OK> "
            f"--out-dir <OUT>"
        ),
        "ban_book_smoke": True,
        "ban_selfcheck": True,
        "ban_self_sign_ok": True,
        "ban_fund_mdd_mix": True,
        "ban_leaf38_mix": True,
        "ban_raise_crr_mod2_or_io_to_primary": True,
        "ban_posthoc_primary_rewrite_from_jaccard": True,
        "keep_does_not_unblock_x2_accept": True,
        "schema": "leaf39_abcfo_rem_resid_alpha_build_v1",
        "known_schema_static": {
            "cf_cols": KNOWN_CF_COLS,
            "fin_cols": KNOWN_FIN_COLS,
            "bs_cols": KNOWN_BS_COLS,
            "mask_cols": KNOWN_MASK_COLS,
            "alpha_out_cols": KNOWN_ALPHA_OUT_COLS,
            "sw_cols": KNOWN_SW_COLS,
            "float_cols": KNOWN_FLOAT_COLS,
        },
        "sign_notes": {
            "peak_proof_required": [
                "after_fundamentals",
                "after_hiliq_chunk_*",
                "after_rebal_ols_*",
                "after_logmv_rebal_*",
                "after_overlap_gate",
                "after_leaf34_jaccard",
                "final_peak_proof",
            ],
            "rss_limit_mb": 1500,
            "jaccard_or_rho_excess_gt_0_5_hard_reject_vs_19_25_30": True,
            "spearman_is_gate_proxy_only": True,
            "formal_rho_excess_before_x2": True,
            "leaf34_jaccard_pin_hard_0_5": True,
            "ban_restored_ok": list(FORBID_OK_SHA8),
            "ban_raise_rss": True,
            "arch_ok_path_required_for_real": True,
            "process_gate_note": (
                "Real build requires existing --arch-ok-path (file must exist; "
                "sha8 not in forbid). Process gate = that .ok + Main window; "
                "ban inventing / self-opening a fake .ok. This LAND_SCRIPT ticket "
                "does NOT request or sign any .ok."
            ),
        },
        "arch_conditions": {
            "C2a": "cross_section_SW_L1_OLS_APPROX_no_panel_no_recount",
            "C2b": "formal_rho_excess_before_X2",
            "C3": "leaf34_Jaccard_PIN_hard_0_5_ban_PRIMARY_rewrite",
            "C4": "ban_self_ok_X2_BS_mix_fund_leaf38_rss_1500",
            "C5": "CRR_MOD2_IO_not_PRIMARY",
            "C8": "PRIMARY_residual_alpha_vector",
            "C9": "COUNT_not_X2_ACCEPT",
        },
        "note": (
            "LAND_SCRIPT formal build; COUNT 20313ba3 is NOT this script; "
            "dry-compile-only; ZERO big-table load; "
            "NOT authorized to execute; wait Arch script-only review → new X2 .ok "
            f"(ban RESTORED {'+'.join(FORBID_OK_SHA8[:6])}…); "
            "peak_proof REQUIRED; rss=1500 ban raise; "
            f"FROZEN={FROZEN_SHA8}; ArchFROZEN={ARCH_FROZEN_REVIEW_SHA8}; "
            "PRIMARY=ABCFO residual α vector; C3 PIN path via --leaf34-jaccard; "
            "C2(b) ρ_excess path via clearing --skip-rho-excess before X2; "
            "COUNT APPROX != X2 ACCEPT; KEEP does NOT unblock X2 ACCEPT; "
            "ban fund MDD / leaf38 mix; ban CRR_MOD2/IO → PRIMARY"
        ),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    if uni == "FULLA":
        print(
            "STOP: --universe FULLA forbidden as PRIMARY; use --universe HILIQ",
            file=sys.stderr,
        )
        return 2
    return 0


# ---------------------------------------------------------------------------
# PIT / ABCFO helpers (formula = COUNT 20313ba3; C2(a) cross-section APPROX)
# ---------------------------------------------------------------------------


def _earliest_pit(df, cols: list[str]):
    import pandas as pd

    df = df.copy()
    df["available_at"] = pd.to_datetime(df["available_at"], utc=True).dt.tz_convert(None)
    df["end_date"] = pd.to_datetime(df["end_date"])
    df["ts_code"] = df["ts_code"].astype(str)
    df = df.sort_values(["ts_code", "end_date", "available_at"])
    df = df.drop_duplicates(["ts_code", "end_date"], keep="first")
    return df[["ts_code", "end_date", "available_at"] + cols]


def ytd_to_qtr(df, value_cols: list[str]):
    """Difference YTD within fiscal year; Q1 (month=3) stays as-is."""
    out = df.copy()
    out["year"] = out["end_date"].dt.year
    out["month"] = out["end_date"].dt.month
    out = out.sort_values(["ts_code", "end_date"])
    for c in value_cols:
        prev = out.groupby("ts_code")[c].shift(1)
        prev_year = out.groupby("ts_code")["year"].shift(1)
        prev_month = out.groupby("ts_code")["month"].shift(1)
        same_year = prev_year == out["year"]
        do = same_year & out["month"].isin([6, 9, 12]) & prev_month.isin([3, 6, 9])
        q = out[c].copy()
        q.loc[do] = out.loc[do, c] - prev.loc[do]
        out[c + "_q"] = q
    return out


def build_fundamentals(rss_check=None):
    """Load CF/FIN/BS PIT; YTD→qtr; A_lag; dS. Chunk-friendly column projection."""
    import numpy as np
    import pyarrow.parquet as pq

    stage("fundamentals_start")
    cf = pq.read_table(PIT_CF, columns=KNOWN_CF_COLS).to_pandas()
    if rss_check:
        rss_check("after_cf_read")
    fin = pq.read_table(PIT_FIN, columns=KNOWN_FIN_COLS).to_pandas()
    if rss_check:
        rss_check("after_fin_read")
    bs = pq.read_table(PIT_BS, columns=KNOWN_BS_COLS).to_pandas()
    if rss_check:
        rss_check("after_bs_read")
    cf = _earliest_pit(cf, ["n_cashflow_act"])
    fin = _earliest_pit(fin, ["revenue", "total_revenue"])
    bs = _earliest_pit(bs, ["total_assets"])
    fin["sales"] = fin["total_revenue"].fillna(fin["revenue"])
    m = cf.merge(
        fin[["ts_code", "end_date", "sales"]], on=["ts_code", "end_date"], how="inner"
    )
    del cf, fin
    gc.collect()
    m = m.merge(
        bs[["ts_code", "end_date", "total_assets"]],
        on=["ts_code", "end_date"],
        how="inner",
    )
    del bs
    gc.collect()
    m = m.sort_values(["ts_code", "end_date"])
    m["A_lag"] = m.groupby("ts_code")["total_assets"].shift(1)
    m = ytd_to_qtr(m, ["n_cashflow_act", "sales"])
    m["sales_lag_q"] = m.groupby("ts_code")["sales_q"].shift(1)
    m["dS"] = m["sales_q"] - m["sales_lag_q"]
    m["ok_blocks"] = (
        m["n_cashflow_act_q"].notna()
        & m["sales_q"].notna()
        & m["A_lag"].notna()
        & (m["A_lag"] > 0)
        & m["dS"].notna()
        & np.isfinite(m["n_cashflow_act_q"].astype(float))
        & np.isfinite(m["sales_q"].astype(float))
        & np.isfinite(m["dS"].astype(float))
    )
    if rss_check:
        rss_check("after_fundamentals")
    return m


def load_sw(path: Path | None = None):
    import pandas as pd
    import pyarrow.parquet as pq

    p = path or SW_L1_DEFAULT
    sw = pq.read_table(p, columns=KNOWN_SW_COLS).to_pandas()
    sw["instrument"] = sw["instrument_id"].map(to_ts)
    sw["in_date"] = pd.to_datetime(sw["in_date"], errors="coerce")
    sw["out_date"] = pd.to_datetime(sw["out_date"], errors="coerce")
    sw["available_at"] = pd.to_datetime(sw["available_at"], errors="coerce")
    return sw


def sw_asof(sw, asof):
    import pandas as pd

    asof = pd.Timestamp(asof)
    ok = (sw["in_date"].isna() | (sw["in_date"] <= asof)) & (
        sw["out_date"].isna() | (sw["out_date"] > asof)
    )
    avail_ok = sw["available_at"].isna() | (sw["available_at"] <= asof)
    cur = sw.loc[ok & avail_ok].copy()
    cur = cur.sort_values(["instrument", "in_date"]).drop_duplicates(
        "instrument", keep="last"
    )
    return cur[["instrument", "sw_code", "sw_name"]]


def exclude_set(sw_cur) -> set[str]:
    codes = set(EXCLUDE_SW.values())
    names = set(EXCLUDE_SW.keys())
    m = sw_cur["sw_code"].isin(codes) | sw_cur["sw_name"].isin(names)
    return set(sw_cur.loc[m, "instrument"].astype(str))


def asof_panel(fund, asof):
    import pandas as pd

    asof = pd.Timestamp(asof)
    sub = fund.loc[fund["available_at"] <= asof].copy()
    if sub.empty:
        return sub
    sub = sub.sort_values(["ts_code", "available_at", "end_date"]).drop_duplicates(
        "ts_code", keep="last"
    )
    return sub


def ols_resid_sw(df):
    """Within SW L1 cross-section OLS; fallback market-wide if n<25. C2(a) APPROX."""
    import numpy as np
    import pandas as pd

    y = (df["n_cashflow_act_q"] / df["A_lag"]).astype(float)
    X = np.column_stack(
        [
            np.ones(len(df)),
            (1.0 / df["A_lag"]).astype(float),
            (df["sales_q"] / df["A_lag"]).astype(float),
            (df["dS"] / df["A_lag"]).astype(float),
        ]
    )
    resid = pd.Series(np.nan, index=df.index, dtype=float)

    def _fit(idx):
        if len(idx) < SW_OLS_MIN_N:
            return
        yy = y.loc[idx].to_numpy()
        xx = X[df.index.get_indexer(idx)]
        mask = np.isfinite(yy) & np.isfinite(xx).all(axis=1)
        if mask.sum() < SW_OLS_MIN_N:
            return
        yy = yy[mask]
        xx = xx[mask]
        try:
            beta, *_ = np.linalg.lstsq(xx, yy, rcond=None)
            e = yy - xx @ beta
            resid.loc[np.array(idx)[mask]] = e
        except np.linalg.LinAlgError:
            return

    for _, g in df.groupby("sw_code"):
        _fit(list(g.index))
    miss = resid.isna() & y.notna()
    if miss.sum() >= SW_OLS_MIN_N:
        _fit(list(df.index[miss]))
    return resid


def ols_resid_simple(y, x):
    """Univariate OLS residual y ~ 1 + x."""
    import numpy as np

    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    mask = np.isfinite(y) & np.isfinite(x)
    out = np.full(len(y), np.nan, dtype=float)
    if mask.sum() < 5:
        return out
    yy = y[mask]
    xx = np.column_stack([np.ones(mask.sum()), x[mask]])
    try:
        beta, *_ = np.linalg.lstsq(xx, yy, rcond=None)
        out[mask] = yy - xx @ beta
    except np.linalg.LinAlgError:
        return out
    return out


def sw_l1_demean(values, sw_codes):
    import numpy as np
    import pandas as pd

    s = pd.Series(np.asarray(values, dtype=float))
    g = pd.Series(sw_codes).astype(str)
    mu = s.groupby(g).transform("mean")
    return (s - mu).to_numpy(dtype=float)


def pick_rebal(dates):
    import pandas as pd

    if len(dates) == 0:
        return []
    idx = list(range(0, len(dates), REBAL_EVERY))
    if idx[-1] != len(dates) - 1:
        idx.append(len(dates) - 1)
    return [pd.Timestamp(dates[i]) for i in idx]


def load_hiliq_mask_by_chunks(
    path: Path,
    start: str,
    end: str,
    rss_check=None,
) -> dict:
    """Year-chunk HI_LIQ load with parquet date filters (ban whole-table)."""
    import pandas as pd
    import pyarrow.parquet as pq

    s = pd.Timestamp(start)
    e = pd.Timestamp(end)
    mask_by: dict = {}
    year = s.year
    while year <= e.year:
        y0 = max(pd.Timestamp(f"{year}-01-01"), s)
        y1 = min(pd.Timestamp(f"{year}-12-31"), e)
        t = pq.read_table(
            path,
            columns=KNOWN_MASK_COLS,
            filters=[
                ("date", ">=", y0.to_datetime64()),
                ("date", "<=", y1.to_datetime64()),
                ("in_universe", "==", True),
            ],
        )
        df = t.to_pandas()
        del t
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
            df["instrument"] = df["instrument"].astype(str).map(to_ts)
            for d, g in df.groupby("date"):
                mask_by[pd.Timestamp(d)] = set(g["instrument"].tolist())
        del df
        gc.collect()
        if rss_check:
            rss_check(f"after_hiliq_chunk_{year}")
        year += 1
    return mask_by


def _load_logmv_t1(float_path: Path, dates: list, codes: list[str]):
    """Lazy T-1 log float mktcap for given rebal dates/codes (leaf30 spirit)."""
    import numpy as np
    import pandas as pd
    import pyarrow.parquet as pq

    if not dates or not codes:
        return {}
    dmin = (min(pd.Timestamp(d) for d in dates) - pd.Timedelta(days=10)).strftime(
        "%Y%m%d"
    )
    dmax = max(pd.Timestamp(d) for d in dates).strftime("%Y%m%d")
    # schema may use instrument_id / trade_date
    schema = pq.read_schema(float_path)
    names = set(schema.names)
    date_col = "trade_date" if "trade_date" in names else "date"
    inst_col = "instrument_id" if "instrument_id" in names else "instrument"
    cols = [date_col, inst_col, "float_mktcap"]
    field = schema.field(date_col)
    import pyarrow as pa

    is_str = pa.types.is_string(field.type) or pa.types.is_large_string(field.type)
    if is_str:
        filt = [(date_col, ">=", dmin), (date_col, "<=", dmax)]
    else:
        filt = [
            (date_col, ">=", pd.Timestamp(dmin).to_datetime64()),
            (date_col, "<=", pd.Timestamp(dmax).to_datetime64()),
        ]
    t = pq.read_table(float_path, columns=cols, filters=filt)
    df = t.to_pandas()
    del t
    df[date_col] = pd.to_datetime(df[date_col])
    df["ts_code"] = df[inst_col].map(to_ts)
    code_set = set(codes)
    df = df[df["ts_code"].isin(code_set)].copy()
    df["logmv"] = np.log(df["float_mktcap"].astype(float).clip(lower=1.0))
    df = df.sort_values(["ts_code", date_col])
    out: dict = {}
    for d in dates:
        dd = pd.Timestamp(d)
        prev = df[df[date_col] < dd]
        if prev.empty:
            continue
        last = prev.groupby("ts_code", as_index=False).tail(1)
        for _, r in last.iterrows():
            out[(dd, str(r["ts_code"]))] = float(r["logmv"])
    del df
    gc.collect()
    return out


def spearman(a, b) -> float:
    import numpy as np
    import pandas as pd

    if len(a) < 5:
        return float("nan")
    ra = pd.Series(a).rank().to_numpy()
    rb = pd.Series(b).rank().to_numpy()
    if np.nanstd(ra) == 0 or np.nanstd(rb) == 0:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def top_jaccard(codes_a, scores_a, codes_b, scores_b, k=20) -> float:
    import pandas as pd

    if len(codes_a) == 0 or len(codes_b) == 0:
        return float("nan")
    sa = pd.Series(scores_a, index=codes_a)
    sb = pd.Series(scores_b, index=codes_b)
    ta = set(sa.nlargest(min(k, len(sa))).index)
    tb = set(sb.nlargest(min(k, len(sb))).index)
    u = ta | tb
    if not u:
        return float("nan")
    return float(len(ta & tb) / len(u))


def load_alpha_slice(path: Path, dates: list):
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq

    if not path.is_file():
        return None
    schema = pq.read_schema(path)
    names = set(schema.names)
    date_col = "date" if "date" in names else "trade_date"
    inst_col = "instrument" if "instrument" in names else "ts_code"
    field = schema.field(date_col)
    is_str = pa.types.is_string(field.type) or pa.types.is_large_string(field.type)
    cols = [date_col, inst_col, "alpha"]
    if is_str:
        dmin, dmax = min(dates).strftime("%Y-%m-%d"), max(dates).strftime("%Y-%m-%d")
        t = pq.read_table(
            path, columns=cols, filters=[(date_col, ">=", dmin), (date_col, "<=", dmax)]
        )
    else:
        t = pq.read_table(
            path,
            columns=cols,
            filters=[
                (date_col, ">=", min(dates).to_datetime64()),
                (date_col, "<=", max(dates).to_datetime64()),
            ],
        )
    df = t.to_pandas()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.rename(columns={date_col: "date", inst_col: "instrument"})
    df["instrument"] = df["instrument"].astype(str).map(to_ts)
    want = set(pd.Timestamp(d) for d in dates)
    return df[df["date"].isin(want)].copy()


def load_leaf34_excl_by_date(path: Path, dates: list) -> dict:
    """Load leaf34 exclusion mask=0 active sets by date (C3 Jaccard only)."""
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq

    if not path.is_file() or not dates:
        return {}
    schema = pq.read_schema(path)
    names = set(schema.names)
    date_col = "trade_date" if "trade_date" in names else "date"
    inst_col = "ts_code" if "ts_code" in names else "instrument"
    mask_col = "mask" if "mask" in names else None
    if mask_col is None:
        return {}
    field = schema.field(date_col)
    is_str = pa.types.is_string(field.type) or pa.types.is_large_string(field.type)
    cols = [date_col, inst_col, mask_col]
    if is_str:
        dmin, dmax = min(dates).strftime("%Y-%m-%d"), max(dates).strftime("%Y-%m-%d")
        t = pq.read_table(
            path, columns=cols, filters=[(date_col, ">=", dmin), (date_col, "<=", dmax)]
        )
    else:
        t = pq.read_table(
            path,
            columns=cols,
            filters=[
                (date_col, ">=", min(dates).to_datetime64()),
                (date_col, "<=", max(dates).to_datetime64()),
            ],
        )
    df = t.to_pandas()
    df[date_col] = pd.to_datetime(df[date_col])
    df[inst_col] = df[inst_col].astype(str).map(to_ts)
    want = set(pd.Timestamp(d) for d in dates)
    df = df[df[date_col].isin(want)]
    # excluded = mask==0
    excl = df[df[mask_col].astype(float) == 0.0]
    out: dict = {}
    for d, g in excl.groupby(date_col):
        out[pd.Timestamp(d)] = set(g[inst_col].tolist())
    del df, excl, t
    gc.collect()
    return out


def jaccard_sets(a: set, b: set) -> float:
    if not a and not b:
        return float("nan")
    u = a | b
    if not u:
        return float("nan")
    return float(len(a & b) / len(u))


def formal_rho_excess_stub(
    alpha_df,
    dates: list,
    *,
    skip: bool,
) -> dict:
    """C2(b) formal ρ_excess path.

    Spearman on alpha is ONLY the COUNT gate proxy. Formal ρ_excess needs
    excess-return alignment; this LAND implements the hook. When --skip-rho-excess
    (default True on LAND), return PIN_GAP payload — must clear skip before X2.
    """
    if skip:
        return {
            "status": "SKIPPED_LAND_DEFAULT",
            "pin": "C2(b)_formal_rho_excess_required_before_X2",
            "note": (
                "Spearman≠ρ_excess. Clear --skip-rho-excess before X2; "
                "hard reject still >0.5 on formal ρ_excess OR Jaccard."
            ),
            "rho_excess": None,
            "EXECUTED_rho_excess": False,
        }
    # Formal path reserved: require returns panel (not wired this LAND to avoid
    # accidental PnL/threshold fishing). Honest PIN_GAP if returns absent.
    return {
        "status": "PIN_GAP_RETURNS_PANEL_NOT_WIRED",
        "pin": "C2(b)_formal_rho_excess_path_exists_returns_hook_pending",
        "note": (
            "Hook open (skip cleared) but excess-return panel join is X2-window "
            "wiring; ban silent Spearman-as-ρ_excess. Do not treat as hard-pass."
        ),
        "rho_excess": None,
        "EXECUTED_rho_excess": False,
        "sample_dates": [str(d.date()) if hasattr(d, "date") else str(d) for d in dates[:6]],
        "n_alpha_rows": int(len(alpha_df)) if alpha_df is not None else 0,
    }


# ---------------------------------------------------------------------------
# Real build (gated)
# ---------------------------------------------------------------------------


def run_build(args) -> int:
    """Real build path — requires --allow-real-data + existing --arch-ok-path."""
    import numpy as np
    import pandas as pd

    enforce_single_thread()
    stage("run_build_start")

    if int(args.rss_limit_mb) > RSS_LIMIT_MB:
        print(
            f"STOP: --rss-limit-mb {args.rss_limit_mb} > {RSS_LIMIT_MB} ban raise",
            file=sys.stderr,
        )
        return 2

    ok_path = args.arch_ok_path
    if ok_path is None or not Path(ok_path).is_file():
        print(
            "STOP: real build requires existing --arch-ok-path "
            "(ban inventing / self-opening .ok)",
            file=sys.stderr,
        )
        return 2
    ok_sha = sha256_file(Path(ok_path))
    if ok_sha[:8] in FORBID_OK_SHA8:
        print(
            f"STOP: --arch-ok-path sha8 {ok_sha[:8]} in FORBID (ban RESTORED)",
            file=sys.stderr,
        )
        return 2

    uni = normalize_universe(args.universe)
    if uni != "HILIQ":
        print("STOP: PRIMARY universe must be HILIQ", file=sys.stderr)
        return 2

    out_dir = Path(args.out_dir) if args.out_dir else Path(args.out) if args.out else None
    if out_dir is None:
        print("STOP: --out-dir (or --out) required for real build", file=sys.stderr)
        return 2
    out_dir.mkdir(parents=True, exist_ok=True)

    def _rss(label: str) -> int:
        return check_rss(
            label,
            rss_limit_mb=int(args.rss_limit_mb),
            c4_kb=int(args.c4_kb),
            hard_kb=int(args.hard_kb),
            split_kb=int(getattr(args, "split_kb", SPLIT_THRESH_KB)),
        )

    w_start = getattr(args, "window_start", None) or X2_START
    w_end = getattr(args, "window_end", None) or X2_END

    fund = build_fundamentals(rss_check=_rss)
    sw = load_sw(Path(args.sw_l1) if args.sw_l1 else SW_L1_DEFAULT)
    _rss("after_sw_load")

    mask_path = Path(args.hi_liq_mask) if args.hi_liq_mask else HI_LIQ_MASK_DEFAULT
    if sha256_file(mask_path)[:8] != HI_LIQ_MASK_SHA8_PIN:
        print(
            f"STOP: HI_LIQ mask sha8 mismatch expect={HI_LIQ_MASK_SHA8_PIN} "
            f"got={sha256_file(mask_path)[:8]}",
            file=sys.stderr,
        )
        return 2
    mask_by = load_hiliq_mask_by_chunks(mask_path, w_start, w_end, rss_check=_rss)
    dates = pd.DatetimeIndex(sorted(mask_by.keys()))
    rebal = pick_rebal(dates)
    if not rebal:
        print("STOP: empty rebal calendar", file=sys.stderr)
        return 2

    rows = []
    cov_mask = []
    for d in rebal:
        hi = mask_by.get(pd.Timestamp(d), set())
        pan = asof_panel(fund, d)
        if pan.empty:
            cov_mask.append(0)
            continue
        pan = pan[pan["ok_blocks"]].copy()
        pan["instrument"] = pan["ts_code"].astype(str)
        pan = pan[pan["instrument"].isin(hi)].copy()
        sw_cur = sw_asof(sw, d)
        excl = exclude_set(sw_cur)
        pan = pan[~pan["instrument"].isin(excl)].copy()
        pan = pan.merge(sw_cur, on="instrument", how="left")
        pan_sw = pan[pan["sw_code"].notna()].copy()
        n_mask = int(pan_sw["instrument"].nunique())
        cov_mask.append(n_mask)
        if n_mask < SW_OLS_MIN_N:
            del pan, pan_sw, sw_cur
            gc.collect()
            _rss(f"after_rebal_ols_{pd.Timestamp(d).strftime('%Y%m%d')}")
            continue

        resid = ols_resid_sw(pan_sw)
        pan_sw = pan_sw.copy()
        pan_sw["abcfo"] = resid
        pan_sw["raw"] = -pan_sw["abcfo"]
        valid = pan_sw["raw"].notna()
        pan_sw = pan_sw.loc[valid].copy()
        if pan_sw.empty:
            del pan, pan_sw, sw_cur, resid
            gc.collect()
            _rss(f"after_rebal_ols_{pd.Timestamp(d).strftime('%Y%m%d')}")
            continue

        # SW L1 demean on raw
        pan_sw["alpha_dm"] = sw_l1_demean(
            pan_sw["raw"].to_numpy(float), pan_sw["sw_code"].tolist()
        )

        # lazy logmv T-1 + OLS resid
        codes = pan_sw["instrument"].tolist()
        logmv_d = _load_logmv_t1(
            Path(args.float_mktcap) if args.float_mktcap else FLOAT_MKTCAP_DEFAULT,
            [d],
            codes,
        )
        pan_sw["logmv"] = pan_sw["instrument"].map(
            lambda c, dd=d, lm=logmv_d: lm.get((pd.Timestamp(dd), c))
        )
        has_lm = pan_sw["logmv"].notna()
        alpha = pan_sw["alpha_dm"].to_numpy(float).copy()
        if has_lm.sum() >= 5:
            alpha[has_lm.to_numpy()] = ols_resid_simple(
                pan_sw.loc[has_lm, "alpha_dm"].to_numpy(float),
                pan_sw.loc[has_lm, "logmv"].to_numpy(float),
            )
        pan_sw["alpha"] = alpha

        for _, r in pan_sw.iterrows():
            rows.append(
                {
                    "trade_date": pd.Timestamp(d),
                    "ts_code": str(r["instrument"]),
                    "alpha": float(r["alpha"]) if r["alpha"] == r["alpha"] else None,
                    "abcfo": float(r["abcfo"]) if r["abcfo"] == r["abcfo"] else None,
                    "raw": float(r["raw"]) if r["raw"] == r["raw"] else None,
                }
            )
        del pan, pan_sw, sw_cur, resid, logmv_d
        gc.collect()
        _rss(f"after_logmv_rebal_{pd.Timestamp(d).strftime('%Y%m%d')}")

    if not rows:
        print("STOP: zero alpha rows", file=sys.stderr)
        return 2

    alpha_df = pd.DataFrame(rows)
    # expand rebal α to daily within mask (hold to next rebal)
    daily_rows = []
    rebal_sorted = sorted(pd.Timestamp(x) for x in rebal)
    alpha_by_rebal = {
        pd.Timestamp(d): g.set_index("ts_code")
        for d, g in alpha_df.groupby("trade_date")
    }
    for i, rb in enumerate(rebal_sorted):
        nxt = (
            rebal_sorted[i + 1]
            if i + 1 < len(rebal_sorted)
            else (pd.Timestamp(w_end) + pd.Timedelta(days=1))
        )
        block = alpha_by_rebal.get(pd.Timestamp(rb))
        if block is None:
            continue
        day_list = [dd for dd in dates if pd.Timestamp(rb) <= pd.Timestamp(dd) < nxt]
        for dd in day_list:
            hi = mask_by.get(pd.Timestamp(dd), set())
            for code, r in block.iterrows():
                if code not in hi:
                    continue
                daily_rows.append(
                    {
                        "trade_date": pd.Timestamp(dd),
                        "ts_code": str(code),
                        "alpha": r["alpha"],
                        "abcfo": r["abcfo"],
                        "raw": r["raw"],
                    }
                )
        _rss(f"after_daily_expand_{pd.Timestamp(rb).strftime('%Y%m%d')}")

    daily = pd.DataFrame(daily_rows)
    del daily_rows, alpha_by_rebal
    gc.collect()

    stamp = datetime.now(ET).strftime("%Y%m%d_%H%M%S")
    alpha_path = out_dir / f"alpha_HILIQ_x2_{stamp}.parquet"
    daily.to_parquet(alpha_path, index=False)

    # coverage stats
    cov_arr = np.asarray(cov_mask, dtype=float)
    cov_stats = {
        "median": float(np.median(cov_arr)) if len(cov_arr) else None,
        "zero_frac": float(np.mean(cov_arr <= 0)) if len(cov_arr) else None,
        "n_rebal": int(len(cov_arr)),
    }
    gate_cov = (
        cov_stats["median"] is not None
        and cov_stats["median"] >= COV_MEDIAN_MIN
        and cov_stats["zero_frac"] is not None
        and cov_stats["zero_frac"] <= ZERO_FRAC_MAX
    )

    # Overlap vs leaf19/25/30 (Spearman proxy + Jaccard); formal ρ_excess separate
    sample = rebal_sorted
    if len(sample) > 6:
        idxs = np.linspace(0, len(sample) - 1, 6).round().astype(int)
        sample = [sample[i] for i in sorted(set(idxs))]
    alphas = {}
    for tag, path in (
        ("leaf19", Path(args.leaf19_alpha) if args.leaf19_alpha else LEAF19_ALPHA_DEFAULT),
        ("leaf25", Path(args.leaf25_alpha) if args.leaf25_alpha else LEAF25_ALPHA_DEFAULT),
        ("leaf30", Path(args.leaf30_alpha) if args.leaf30_alpha else LEAF30_ALPHA_DEFAULT),
    ):
        alphas[tag] = load_alpha_slice(path, sample)
        _rss(f"after_load_alpha_{tag}")

    overlap_rows = []
    hard_hits = []
    for d in sample:
        sub = alpha_df[alpha_df["trade_date"] == pd.Timestamp(d)]
        if sub.empty:
            continue
        codes = sub["ts_code"].tolist()
        scores = sub["alpha"].to_numpy(float)
        row = {"date": str(pd.Timestamp(d).date()), "n": len(codes)}
        for tag, adf in alphas.items():
            if adf is None or adf.empty:
                row[f"rho_spearman_{tag}"] = None
                row[f"j20_{tag}"] = None
                continue
            o = adf[adf["date"] == pd.Timestamp(d)]
            if o.empty:
                row[f"rho_spearman_{tag}"] = None
                row[f"j20_{tag}"] = None
                continue
            sb = o.set_index("instrument")["alpha"]
            common = [c for c in codes if c in sb.index]
            if len(common) < 30:
                row[f"rho_spearman_{tag}"] = None
                row[f"j20_{tag}"] = None
                continue
            a = pd.Series(scores, index=codes).loc[common].to_numpy()
            b = sb.loc[common].to_numpy(dtype=float)
            rho = spearman(a, b)
            j20 = top_jaccard(
                codes, scores, sb.index.tolist(), sb.to_numpy(dtype=float), 20
            )
            row[f"rho_spearman_{tag}"] = rho
            row[f"j20_{tag}"] = j20
            # hard gate on Jaccard; Spearman is proxy only (C2(b))
            if j20 == j20 and j20 > HARD_OVERLAP:
                hard_hits.append({"vs": tag, "metric": "j20", "max": float(j20)})
        overlap_rows.append(row)
    _rss("after_overlap_gate")

    # C2(b) formal ρ_excess
    rho_excess_payload = formal_rho_excess_stub(
        alpha_df,
        sample,
        skip=bool(getattr(args, "skip_rho_excess", True)),
    )

    # C3 leaf34 Jaccard
    leaf34_payload = {
        "status": "PIN_NOT_REQUESTED",
        "note": "Pass --leaf34-jaccard to estimate; hard reject 0.5; ban PRIMARY rewrite",
        "jaccard_max": None,
        "EXECUTED_leaf34_jaccard": False,
    }
    if bool(getattr(args, "leaf34_jaccard", False)):
        l34_path = (
            Path(args.leaf34_mask) if args.leaf34_mask else LEAF34_MASK_DEFAULT
        )
        if not l34_path.is_file():
            leaf34_payload = {
                "status": "PIN_GAP_LEAF34_MASK_MISSING",
                "path": str(l34_path),
                "jaccard_max": None,
                "EXECUTED_leaf34_jaccard": False,
                "hard_reject": False,
                "note": "Honest PIN_GAP ≠ hard-pass",
            }
        else:
            excl_by = load_leaf34_excl_by_date(l34_path, sample)
            j_rows = []
            j_vals = []
            for d in sample:
                sub = alpha_df[alpha_df["trade_date"] == pd.Timestamp(d)]
                if sub.empty:
                    continue
                # active set for Jaccard: top-20 by α (long high ABCFO) vs leaf34 excl
                sa = sub.set_index("ts_code")["alpha"]
                top = set(sa.nlargest(min(20, len(sa))).index.astype(str))
                excl = excl_by.get(pd.Timestamp(d), set())
                j = jaccard_sets(top, excl)
                j_rows.append(
                    {
                        "date": str(pd.Timestamp(d).date()),
                        "n_top": len(top),
                        "n_excl": len(excl),
                        "jaccard": j,
                    }
                )
                if j == j:
                    j_vals.append(float(j))
            jmax = float(np.max(j_vals)) if j_vals else None
            hard = bool(jmax is not None and jmax > HARD_OVERLAP)
            if hard:
                hard_hits.append(
                    {"vs": "leaf34", "metric": "jaccard_top20_vs_excl", "max": jmax}
                )
            leaf34_payload = {
                "status": "ESTIMATED",
                "path": str(l34_path),
                "path_sha8": sha256_file(l34_path)[:8],
                "definition": (
                    "Jaccard(top20 leaf39 α, leaf34 mask==0 excl set) on sample rebal days"
                ),
                "rows": j_rows,
                "jaccard_max": jmax,
                "hard_reject_threshold": HARD_OVERLAP,
                "hard_reject": hard,
                "EXECUTED_leaf34_jaccard": True,
                "ban_posthoc_PRIMARY_rewrite": True,
                "note": (
                    "C3 disclose only; if hard_reject → fail leaf; "
                    "ban rewriting PRIMARY to save gate"
                ),
            }
            del excl_by
            gc.collect()
        _rss("after_leaf34_jaccard")

    pk = _rss("final_peak_proof")
    peak_mb = pk / 1024.0
    peak_ok = peak_mb <= float(args.rss_limit_mb)

    meta = {
        "schema": "leaf39_abcfo_rem_resid_alpha_build_v1",
        "mechanism_tag": MECHANISM_TAG,
        "frozen_sha8": FROZEN_SHA8,
        "arch_frozen_review_sha8": ARCH_FROZEN_REVIEW_SHA8,
        "count_json_sha8": COUNT_JSON_SHA8,
        "script_sha8": script_sha256()[:8],
        "arch_ok_path": str(ok_path),
        "arch_ok_sha8": ok_sha[:8],
        "universe": "HILIQ",
        "window": {"start": w_start, "end": w_end, "rebal_every": REBAL_EVERY},
        "primary_delivery": PRIMARY_DELIVERY,
        "c2a": C2A_PIN,
        "c2b": C2B_PIN,
        "alpha_path": str(alpha_path),
        "n_alpha_rows": int(len(daily)),
        "n_rebal_alpha_rows": int(len(alpha_df)),
        "coverage_masked": cov_stats,
        "gate_cov_pass": gate_cov,
        "overlap_rows_spearman_proxy": overlap_rows,
        "rho_excess": rho_excess_payload,
        "leaf34_jaccard": leaf34_payload,
        "hard_reject_hits": hard_hits,
        "hard_reject": len(hard_hits) > 0,
        "peak_rss_mb": float(peak_mb),
        "peak_proof_le_1500": peak_ok,
        "cost_bp_eval": COST_BP_EVAL,
        "live": False,
        "promotion_approved": False,
        "ok_requested": False,
        "EXECUTED_full_alpha": True,
        "x2_accept": False,
        "ban_self_sign_ok": True,
        "note": (
            "Formal α build complete for Arch/X2 window; "
            "this script never writes .ok; KEEP≠ACCEPT; "
            "Spearman proxy ≠ ρ_excess; C3 leaf34 per payload; "
            "peak_proof required; ban RESTORED forbid list"
        ),
    }
    meta_path = out_dir / f"run_meta_{stamp}.json"
    tmp = meta_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(meta_path)

    if not peak_ok:
        print(
            f"STOP: peak_proof failed peak_rss_mb={peak_mb:.1f} > {args.rss_limit_mb}; "
            f"Exit 95",
            file=sys.stderr,
        )
        return 95

    print(
        json.dumps(
            {
                "ok_build": True,
                "alpha_path": str(alpha_path),
                "meta_path": str(meta_path),
                "peak_rss_mb": peak_mb,
                "gate_cov_pass": gate_cov,
                "hard_reject": len(hard_hits) > 0,
                "leaf34_status": leaf34_payload.get("status"),
                "rho_excess_status": rho_excess_payload.get("status"),
                "EXECUTED_full_alpha": True,
                "ok_requested": False,
                "x2_accept": False,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description=(
            "Leaf39 ABCFO REM residual α formal build (HILIQ × x2); "
            "NOT authorized without --allow-real-data + --arch-ok-path. "
            "Default: use --dry-compile-only or --help (no heavy compute)."
        )
    )
    ap.add_argument(
        "--universe",
        default="HILIQ",
        choices=("HILIQ", "HI_LIQ", "FULLA"),
        help="PRIMARY must be HILIQ (FULLA as --universe → STOP)",
    )
    ap.add_argument("--window", default="x2", choices=("x2",))
    ap.add_argument("--window-start", default=X2_START)
    ap.add_argument("--window-end", default=X2_END)
    ap.add_argument("--x2-end", default=X2_END_TRADE_DATE)
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory for real build (preferred)",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Alias of --out-dir for real build",
    )
    ap.add_argument("--rss-limit-mb", type=int, default=RSS_LIMIT_MB)
    ap.add_argument("--c4-kb", type=int, default=C4_KB)
    ap.add_argument("--stop-kb", type=int, default=STOP_KB)
    ap.add_argument("--hard-kb", type=int, default=HARD_KB)
    ap.add_argument(
        "--split-kb",
        type=int,
        default=SPLIT_THRESH_KB,
        help="Split/soft threshold kb (default 0.85*C4)",
    )
    ap.add_argument("--allow-real-data", action="store_true", default=False)
    ap.add_argument(
        "--arch-ok-path",
        type=Path,
        default=None,
        help=(
            "Existing Arch .ok (sha8 not in forbid); process gate with Main window. "
            "This LAND ticket does NOT self-fill a real .ok."
        ),
    )
    ap.add_argument(
        "--execute",
        action="store_true",
        default=False,
        help="Optional; still requires --allow-real-data + --arch-ok-path",
    )
    ap.add_argument("--hi-liq-mask", type=Path, default=HI_LIQ_MASK_DEFAULT)
    ap.add_argument("--sw-l1", type=Path, default=SW_L1_DEFAULT)
    ap.add_argument("--float-mktcap", type=Path, default=FLOAT_MKTCAP_DEFAULT)
    ap.add_argument("--calendar", type=Path, default=CAL_DEFAULT)
    ap.add_argument("--leaf19-alpha", type=Path, default=LEAF19_ALPHA_DEFAULT)
    ap.add_argument("--leaf25-alpha", type=Path, default=LEAF25_ALPHA_DEFAULT)
    ap.add_argument("--leaf30-alpha", type=Path, default=LEAF30_ALPHA_DEFAULT)
    ap.add_argument("--leaf34-mask", type=Path, default=LEAF34_MASK_DEFAULT)
    ap.add_argument(
        "--leaf34-jaccard",
        action="store_true",
        default=False,
        help="C3: estimate Jaccard vs leaf34 exclusion (default OFF; PIN until run)",
    )
    ap.add_argument(
        "--skip-rho-excess",
        action="store_true",
        default=True,
        help=(
            "C2(b): skip formal ρ_excess (default True on LAND). "
            "Clear before X2 (pass --no-skip-rho-excess)."
        ),
    )
    ap.add_argument(
        "--no-skip-rho-excess",
        action="store_false",
        dest="skip_rho_excess",
        help="Enable formal ρ_excess path (required before X2)",
    )
    ap.add_argument(
        "--dry-compile-only",
        action="store_true",
        default=False,
        help="Print pins; ZERO big-table load; exit 0 (recommended default)",
    )
    return ap


def main(argv: list[str] | None = None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)

    if int(getattr(args, "rss_limit_mb", RSS_LIMIT_MB)) > RSS_LIMIT_MB:
        print(
            f"STOP: --rss-limit-mb {args.rss_limit_mb} > {RSS_LIMIT_MB} ban raise",
            file=sys.stderr,
        )
        return 2

    if args.dry_compile_only:
        return dry_compile_only_print(args)

    # Default without flags: refuse heavy path
    if not args.allow_real_data and not args.execute:
        print(
            "STOP: missing authorization flags "
            "(need --allow-real-data + --arch-ok-path; or --dry-compile-only / --help)",
            file=sys.stderr,
        )
        return 2
    if args.execute and not args.allow_real_data:
        print(
            "STOP: --execute requires --allow-real-data + --arch-ok-path",
            file=sys.stderr,
        )
        return 2
    if args.out_dir is None and args.out is None:
        print(
            "STOP: --out-dir (or --out) is required for build "
            "(or pass --dry-compile-only)",
            file=sys.stderr,
        )
        return 2
    return run_build(args)


if __name__ == "__main__":
    raise SystemExit(main())
