#!/usr/bin/env python3
"""Leaf38 audit non-standard opinion exclusion overlay — formal build (NOT authorized).

B1_PUSHDOWN (2026-10-27 ~21:55 ET): true parquet date pushdown in
`_load_hiliq_mask_by_chunks` — ban whole-table `pq.read_table` per year.
prev_script_sha8=d5cf50bb; VOID.ABORT_EXIT95 Arch=167996dd (peak≈1604 @
after_hiliq_chunk_2024). Ban RESTORED 62acf9fc+57ab9096+b5be1164+4096d401+.
rss=1500 ban raise; EXECUTED=false this LAND; !=X2 ACCEPT; ban QUIET; ban self .ok.

NEW file origin (2026-10-27 ~21:00 ET). LAND_SCRIPT ticket.
Nails PREREG_FROZEN sha8 ce0eb2ce; FROZEN RECEIPT bb8051bd;
Arch FROZEN review 01753ff4 PASS_WC; Arch who_pays DRAFT review acba0865;
who 16c1f70b / COVER 7c3b8691 / COUNT receipt disk e82aefa2 (文内 7cc317d9 勿采) /
COUNT script ba34da2a (NOT formal build; ban treat as this ticket's main script) /
JSON 2b3babb5 / dig fa973826 (文内 a6ddc4ef 勿采).
Engineering skeleton RSS/peak_proof/ABORT path from leaf37 B1 lowmem 32605aca
(read-only template; ban reuse IMAX logic / ban RESTORED old .ok / ban re-run leaf37).

Mechanism (FROZEN; mechanism_tag=g1g5_ashare_audit_nonstd_exclusion_overlay_v1):
  PRIMARY = mask-only negative exclusion overlay on HI_LIQ:
    latest audit opinion with T1(available_at) <= t and is_non_standard=True -> mask=0;
    other computable names -> mask=1; non-computable excluded (no fake 0)
  PIT: available_at -> T1 (strict next trade day); key=ts_code; ban peek available_at>t
  Overlay on backbone / capacity_adv; NOT a full long-short audit alpha main leaf
  soft-penalty: OFF by default (non PRIMARY); enable needs SW+logmv+style else PIN_GAP
  Thickness (runtime disclose; ban post-hoc rewrite):
    median>=30 AND frac(daily_excl>=10)>=0.60 AND zero_frac<=0.50
  Jaccard >0.5 vs negevent OR leaf36 -> hard reject; vs leaf34/35/37 disclose
  Window intent 2024-06-03 -> 2026-10-09; cost eval 30bp; HI_LIQ PRIMARY
  KEEP != ACCEPT; decay near-window 252td (script does not execute decay gate)

§6.1 peak path (C9 FIRST; rss=1500 ban raise; peak_proof<=1500 REQUIRED):
  1. Split process: overlay mask build vs negevent/leaf36 Jaccard (subprocess OR
     pre-land pair sets then read-only load); ban holding CAP_ADV+NEGEVENT_W full
     frames + ANN + HI_LIQ mask_by + excl dicts in one process simultaneously
  2. Stream/chunk: HI_LIQ parquet by year with parquet filters pushdown
     (date>=y_start & date<=y_end ∩ window; optional in_universe==True);
     ban whole-table read per year; audit/ann by block; del+gc after mask_by/excl
  3. Compact repr: categorical / internal int id for instruments; Jaccard via
     on-disk (date,inst_id) compact pairs; ban long-lived giant Python str sets
  4. Single thread: ban parallel workers stacking RSS; OMP/MKL/NUMEXPR=1
  5. Hard ABORT: peak>1500 -> Exit 94 (soft/split) / 95 (hard); ban raise to 1600/1800
  6. peak_proof REQUIRED before any .ok / X2; this ticket does NOT self-sign .ok

PRIMARY CLI: --universe HILIQ --window x2
Real path: --allow-real-data + existing --arch-ok-path (sha8 not in forbid)
Default / --dry-compile-only: print pins; ZERO big-table load; exit 0
--help via argparse
rss 1500 hard ABORT + peak_proof; sampler /tmp/quantlab_leaf38_audit_nonstd_
out intent: output/ai_factory/_leaf38_audit_nonstd_exclusion/
forbid: 57ab9096+b5be1164+4096d401+eb70eef4+00eec671+10927bd9+25ae4572+…
Ban re-run leaf37 015e6f06/32605aca/108aba8f; leaf37/36/35 HOLD CLOSED no rollback
Ban fund_portfolio mix; ban self-sign .ok / QUIET / self-run X2 / Book-Smoke
live=false; promotion=false; ok_requested=false; EXECUTED=false; !=X2 ACCEPT
COUNT APPROX != X2 ACCEPT (C12); KEEP does NOT unblock X2 ACCEPT (C13).
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import resource
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# §6.1-4 single-thread: pin before any numeric import on real path
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")

ET = ZoneInfo("America/New_York")
ROOT = Path(__file__).resolve().parents[1]
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

MECHANISM_TAG = "g1g5_ashare_audit_nonstd_exclusion_overlay_v1"
SCRIPT_REL = "research/leaf38_audit_nonstd_exclusion_overlay_alpha_build.py"
FROZEN_REL = (
    "docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_PREREG_FROZEN_20261027_ZH.md"
)
FROZEN_SHA8 = "ce0eb2ce"
FROZEN_RECEIPT_SHA8 = "bb8051bd"
ARCH_FROZEN_REVIEW_SHA8 = "01753ff4"
ARCH_WHO_PAYS_REVIEW_SHA8 = "acba0865"
WHO_PAYS_SHA8 = "16c1f70b"
COVER_SHA8 = "7c3b8691"
COUNT_RECEIPT_SHA8 = "e82aefa2"  # disk; 文内 7cc317d9 勿采
COUNT_SCRIPT_SHA8 = "ba34da2a"  # audit COUNT; NOT this formal build
COUNT_JSON_SHA8 = "2b3babb5"
DIG_SHA8 = "fa973826"  # 文内 a6ddc4ef 勿采
HI_LIQ_MASK_SHA8_PIN = "c5433e80"
PREV_SCRIPT_SHA8_READONLY = "d5cf50bb"  # pre-pushdown; ban treat as this ticket
ARCH_VOID_EXIT95_SHA8 = "167996dd"  # VOID.ABORT_EXIT95; ban RESTORED 62acf9fc
VOIDED_OK_SHA8 = "62acf9fc"  # leaf38 X2 VOID.ABORT_EXIT95 — ban RESTORED
LEAF37_B1_TEMPLATE_SHA8_READONLY = "32605aca"  # RSS skeleton only; ban IMAX reuse
LEAF37_BASE_SHA8_BAN = "108aba8f"
LEAF37_ALT_SHA8_BAN = "015e6f06"
LEAF37_HOLD_OK_SHA8 = "57ab9096"
LEAF36_HOLD_JSON_SHA8 = "575e8276"  # disclose/hold; no reopen
LEAF35_FORMAL_SHA8_READONLY = "434ff42c"
LEAF34_FORMAL_SHA8_READONLY = "482009dc"
LEAF32_HOLD_SHA8 = "45dd87dc"

RSS_LIMIT_MB = 1500
C4_KB = 1331200
STOP_KB = 1484800
HARD_KB = 1536000  # ~1500 MiB hard; Exit 95
SPLIT_THRESH_KB = int(0.85 * C4_KB)  # Exit 94 split further
# Exit codes (align leaf37 habit): 94 = soft/split ABORT; 95 = hard ABORT

X2_START = "2024-06-03"
X2_END = "2026-10-09"
X2_END_TRADE_DATE = "20261009"
REBAL_EVERY = 20
PRIMARY_DELIVERY = "mask_only"
SOFT_PENALTY_DEFAULT = False
ALPHA_SIGN = "nonstd_audit_opinion_mask0_exclusion"
IC_SIGN_EXPECTED = "n/a_overlay_mask"

C3_FORMULA_PIN = (
    "latest_audit_opinion where T1(available_at)<=t; "
    "if is_non_standard=True -> mask=0; else computable mask=1; "
    "non_computable excluded (no fake 0); key=ts_code; ban peek available_at>t; "
    "ban treat clean unqualified opinion as exclude"
)

STYLE_COLS_PINNED = ("mom20", "vol20", "logADV20")
STYLE_SOURCE_PINNED = "derived_from_daily_bars_W20"
COST_BP_EVAL = 30

DECAY_KEEP_PIN = {
    "latest_resid_alpha_gt_0": True,
    "not_five_quarter_decline": True,
    "H2_net_cagr_gt_510300": True,
    "near_window_td": 252,
    "min_td_for_alpha": 126,
    "keep_does_not_unblock_x2_accept": True,
    "note": (
        "KEEP = conjunction of three gates; script does not execute decay gate; "
        "KEEP does NOT unblock X2 ACCEPT (leaf32 HOLD 45dd87dc; leaf37 HOLD CLOSED)"
    ),
}

FORBID_OK_SHA8 = (
    "62acf9fc",  # leaf38 X2 VOID.ABORT_EXIT95 — ban RESTORED
    "57ab9096",  # leaf37 selfcheck .ok archived — ban RESTORED
    "b5be1164",  # main-named RESTORED
    "4096d401",  # leaf37 X2 VOID.ABORT_PEAK — ban RESTORED
    "eb70eef4", "00eec671", "10927bd9", "25ae4572", "178e90e9", "c1b71e64",
    "245df63f", "c5ed13df", "5774bb6e", "81521fb5", "02426b73", "4bb141c9",
    "fdbaa512", "aa25e989", "7e239487", "5af20222", "5ae077fa", "3c297052",
    "e107383f", "2be59acd", "a7d98ac9", "8e51de63", "3a6caa4f", "8bcd79dc",
    "725be3e0", "0f50daf7", "3c19dd7d", "1c32ab1e", "6054b3bf", "6de02e74",
)

AUDIT_OPINION_DEFAULT = ROOT / "data/v2/audit/audit_opinion_pit_tushare.parquet"
HI_LIQ_MASK_DEFAULT = ROOT / "output/strategy_hiliq/universe_mask_hiliq_v1.parquet"
FULLA_MASK_DEFAULT = ROOT / "output/strategy_fulla/universe_mask_fulla_v1.parquet"
CAL_DEFAULT = ROOT / "data/v2/calendar/trade_cal_sse_pit.parquet"
CAP_ADV_DEFAULT = ROOT / (
    "output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet"
)
NEGEVENT_W_DEFAULT = ROOT / (
    "output/ai_factory/g1g5_capacity_adv_negevent_daily_weights_20261014_010218.parquet"
)
NEGEVENT_META_DEFAULT = ROOT / (
    "output/ai_factory/g1g5_capacity_adv_negevent_run_meta_20261014_010218.json"
)
ANN_MAIN_DEFAULT = ROOT / "data/v2/events/announcements_classified_pit.parquet"
ANN_POST_DEFAULT = ROOT / (
    "data/v2/events/announcements_classified_pit_post202406.parquet"
)
SW_L1_DEFAULT = ROOT / "data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet"
FLOAT_MKTCAP_DEFAULT = (
    ROOT / "data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet"
)
DAILY_DIR_DEFAULT = ROOT / "data/v2/tushare_raw/daily"
ADJ_FACTOR_DEFAULT = ROOT / "data/v2/adj/adj_factor_2023h2plus.parquet"
OUT_DEFAULT = ROOT / "output/ai_factory/_leaf38_audit_nonstd_exclusion"

LEAF34_MASK_DEFAULT = ROOT / (
    "output/ai_factory/_leaf34_high_accrual/20261027_105941/"
    "exclusion_mask_HILIQ_x2_20261027_105958.parquet"
)
LEAF35_MASK_DEFAULT = ROOT / (
    "output/ai_factory/_leaf35_etf_passive_flow_pressure/20261027_152756/"
    "exclusion_mask_HILIQ_x2_20261027_152844.parquet"
)
LEAF36_COUNT_JSON_DEFAULT = ROOT / (
    "output/ai_factory/leaf36_inquiry_letter_exclusion_count_20261027.json"
)
LEAF37_MASK_DEFAULT = ROOT / (
    "output/ai_factory/_leaf37_imax_lottery"
)  # dir; formal X2 may land later — disclose only; ban re-run leaf37 scripts

SAMPLER_PREFIX = "/tmp/quantlab_leaf38_audit_nonstd_"
BALLAST = "510300.SH"

KNOWN_AUDIT_COLS = ["ts_code", "available_at", "is_non_standard", "audit_result"]
KNOWN_MASK_COLS = ["date", "instrument", "in_universe"]
KNOWN_MASK_OUT_COLS = [
    "trade_date", "ts_code", "mask", "alpha", "is_non_standard_latest",
]
JACCARD_HARD = 0.5  # vs negevent OR leaf36 — hard reject if either >
RHO_STRENGTH = 0.5
COV_MEDIAN_MIN = 30.0
FRAC_GE10_MIN = 0.60
ZERO_FRAC_MAX = 0.50
HARD_OVERLAP_TAGS = ("negevent", "leaf36")
DISCLOSE_OVERLAP_TAGS = ("leaf34", "leaf35", "leaf37")

# leaf36 FIN filter keywords (Jaccard rebuild only; not main signal)
FIN_KW = r"年报|半年报|季报|财务|会计|审计|业绩|应收|存货|商誉|收入|利润|信息披露|监管工作函"
REORG_KW = r"重组|重大资产重组|吸收合并|借壳"
REPLY_NOISE_KW = r"回函|回复|核查说明"
ISSUER_KW = (
    r"收到|证券交易所|深圳证券交易所|上海证券交易所|北京证券交易所|"
    r"监管工作函|问询函的公告|关注函的公告"
)
ABNORMAL_KW = r"异常波动"
CBOND_KW = r"可转债|可转换公司债券"
TITLE_CORE_KW = r"问询函|关注函"
LEAF36_WIN = 20


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
    """§6.1-5 hard ABORT. Exit 94 soft/split; Exit 95 hard. Ban raise cap."""
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
    """Normalize to ts_code form 600829.SH (ban instrument_id sh.600829 hard-join)."""
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
    """§6.1-4: ban parallel workers stacking RSS."""
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
    also_fulla = bool(getattr(args, "also_fulla_research", False))
    soft_pen = bool(getattr(args, "enable_soft_penalty", False))
    payload = {
        "live": False,
        "ok_requested": False,
        "promotion_approved": False,
        "executed": False,
        "x2_accept": False,
        "approx": True,
        "count_approx_not_x2_accept": True,
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
        "also_fulla_research": also_fulla,
        "ban_silent_fulla_as_primary": True,
        "window": args.window,
        "x2_end": args.x2_end,
        "x2_window": f"{X2_START} → {X2_END}",
        "rebal_every_td": REBAL_EVERY,
        "primary_delivery": PRIMARY_DELIVERY,
        "soft_penalty_enabled": soft_pen,
        "soft_penalty_default": SOFT_PENALTY_DEFAULT,
        "soft_penalty_is_primary": False,
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
        "cover_sha8": COVER_SHA8,
        "count_receipt_sha8": COUNT_RECEIPT_SHA8,
        "count_script_sha8_NOT_formal": COUNT_SCRIPT_SHA8,
        "count_json_sha8": COUNT_JSON_SHA8,
        "dig_sha8": DIG_SHA8,
        "hi_liq_mask_sha8_pin": HI_LIQ_MASK_SHA8_PIN,
        "prev_script_sha8_readonly": PREV_SCRIPT_SHA8_READONLY,
        "arch_void_exit95_sha8": ARCH_VOID_EXIT95_SHA8,
        "voided_ok_sha8_ban_restored": VOIDED_OK_SHA8,
        "b1_pushdown": True,
        "hiliq_load_mode": "parquet_date_filters_year_chunk_pushdown",
        "leaf37_b1_template_sha8_readonly": LEAF37_B1_TEMPLATE_SHA8_READONLY,
        "leaf37_base_sha8_ban": LEAF37_BASE_SHA8_BAN,
        "leaf37_alt_sha8_ban": LEAF37_ALT_SHA8_BAN,
        "leaf37_hold_ok_sha8": LEAF37_HOLD_OK_SHA8,
        "leaf36_hold_json_sha8": LEAF36_HOLD_JSON_SHA8,
        "leaf35_formal_sha8_readonly": LEAF35_FORMAL_SHA8_READONLY,
        "leaf34_formal_sha8_readonly": LEAF34_FORMAL_SHA8_READONLY,
        "leaf32_hold_sha8_no_rollback": LEAF32_HOLD_SHA8,
        "forbid_ok_sha8": list(FORBID_OK_SHA8),
        "sampler_prefix": SAMPLER_PREFIX,
        "out_intent": str(OUT_DEFAULT.relative_to(ROOT)),
        "audit_opinion": str(AUDIT_OPINION_DEFAULT.relative_to(ROOT)),
        "c3_formula_pin": C3_FORMULA_PIN,
        "style_cols_pinned": list(STYLE_COLS_PINNED),
        "style_source_pinned": STYLE_SOURCE_PINNED,
        "cost_bp_eval": COST_BP_EVAL,
        "decay_keep_pin": DECAY_KEEP_PIN,
        "mask_pipeline": [
            "audit_opinion_pit: ts_code/available_at/is_non_standard",
            "available_at -> day D; T1 = first trade day strictly > D",
            "for each HI_LIQ name i on day t: latest opinion with T1<=t",
            "if is_non_standard=True -> mask=0 else computable mask=1",
            "non_computable excluded (no fake 0)",
            "PRIMARY=mask-only overlay on backbone / capacity_adv",
            "optional soft-penalty OFF by default (non PRIMARY)",
            "≠ full long-short audit alpha main leaf (C11)",
        ],
        "section_6_1_peak_path": {
            "split_process_mask_vs_jaccard": True,
            "stream_chunk_year_or_date": True,
            "hiliq_parquet_date_pushdown": True,
            "ban_whole_table_read_per_year": True,
            "compact_categorical_int_id": True,
            "single_thread": True,
            "hard_abort_exit_94_95": True,
            "peak_proof_le_1500_required": True,
            "ban_raise_rss": True,
        },
        "overlap_hard_targets": list(HARD_OVERLAP_TAGS),
        "overlap_disclose_targets": list(DISCLOSE_OVERLAP_TAGS),
        "jaccard_hard": JACCARD_HARD,
        "rho_strength_filter": RHO_STRENGTH,
        "coverage_excl_median_min": COV_MEDIAN_MIN,
        "frac_ge10_min": FRAC_GE10_MIN,
        "zero_frac_max": ZERO_FRAC_MAX,
        "cap_adv": str(CAP_ADV_DEFAULT.relative_to(ROOT)),
        "negevent_w": str(NEGEVENT_W_DEFAULT.relative_to(ROOT)),
        "leaf34_mask": str(LEAF34_MASK_DEFAULT.relative_to(ROOT)),
        "leaf35_mask": str(LEAF35_MASK_DEFAULT.relative_to(ROOT)),
        "leaf36_count_json": str(LEAF36_COUNT_JSON_DEFAULT.relative_to(ROOT)),
        "primary_cli": (
            f"PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python {SCRIPT_REL} "
            f"--universe HILIQ --window x2 --x2-end {X2_END_TRADE_DATE} "
            f"--allow-real-data --arch-ok-path <OK> --out <OUT>"
        ),
        "dry_cli": (
            f"PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python {SCRIPT_REL} "
            f"--dry-compile-only"
        ),
        "jaccard_worker_cli": (
            f"PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python {SCRIPT_REL} "
            f"--jaccard-worker-only --pair-dir <TMP>/pairs --out-json <TMP>/jacc.json"
        ),
        "ban_book_smoke": True,
        "ban_selfcheck": True,
        "ban_self_sign_ok": True,
        "ban_fund_portfolio_mix": True,
        "ban_reuse_leaf37_imax_logic": True,
        "ban_rerun_leaf37_scripts": True,
        "ban_reopen_leaf36_inquiry": True,
        "ban_posthoc_thickness_or_sign_flip": True,
        "keep_does_not_unblock_x2_accept": True,
        "primary_load": (
            "hiliq_date_chunk_mask_by + audit_pit_excl + "
            "subprocess_jaccard_negevent_leaf36"
        ),
        "schema": "leaf38_audit_nonstd_exclusion_overlay_alpha_build_v1",
        "known_schema_static": {
            "audit_cols": KNOWN_AUDIT_COLS,
            "mask_cols": KNOWN_MASK_COLS,
            "mask_out_cols": KNOWN_MASK_OUT_COLS,
        },
        "sign_notes": {
            "ban_no_overlap_report_bypass_on_real": True,
            "peak_proof_required": [
                "after_hiliq_chunk_*",
                "after_mask_by",
                "after_audit_excl",
                "after_mask_expand",
                "after_jaccard_subprocess",
                "after_disclose_overlap",
                "final_peak_proof",
            ],
            "rss_limit_mb": 1500,
            "jaccard_gt_0_5_hard_reject_vs_negevent_or_leaf36": True,
            "rho_gt_0_5_strength_filter_only": True,
            "ban_restored_ok": list(FORBID_OK_SHA8),
            "ban_raise_rss": True,
            "ban_posthoc_thickness_or_sign_flip": True,
            "c10_leaf37_hold_closed_no_reopen": True,
            "c11_overlay_not_full_audit_alpha_main": True,
            "c12_approx_not_x2_accept": True,
            "arch_ok_path_required_for_real": True,
            "process_gate_note": (
                "Real build requires existing --arch-ok-path (file must exist; "
                "sha8 not in forbid). Process gate = that .ok + Main window; "
                "ban inventing / self-opening a fake .ok. This LAND_SCRIPT ticket "
                "does NOT request or sign any .ok."
            ),
        },
        "arch_conditions": {
            "C1": "FROZEN_prereg_complete_ce0eb2ce",
            "C2": "formal_script_this_ticket_LAND_SCRIPT",
            "C3": "PIT_available_at_T1_latest_nonstd_mask0_ts_code",
            "C4": "mask_only_PRIMARY_soft_penalty_non_PRIMARY",
            "C5": "thickness_median30_frac10_0p60_zero_frac_0p50",
            "C6": "HILIQ_primary_FULLA_research_optional",
            "C7": "overlap_hard_negevent_leaf36_disclose_34_35_37",
            "C8": "forbid_57ab9096_b5be1164_4096d401_plus_prior",
            "C9": "rss_1500_peak_proof_section_6_1",
            "C10": "leaf37_HOLD_CLOSED_fund_no_mix",
            "C11": "overlay_not_full_audit_alpha_main_leaf",
            "C12": "COUNT_APPROX_not_X2_ACCEPT",
            "C13": "decay_KEEP_three_gates_KEEP_does_not_unblock",
        },
        "note": (
            "LAND_SCRIPT formal build; COUNT ba34da2a is NOT this script; "
            "dry-compile-only; ZERO big-table load; "
            "NOT authorized to execute; wait Arch script-only review -> new X2 .ok "
            f"(ban RESTORED {'+'.join(FORBID_OK_SHA8[:8])}…); "
            "peak_proof REQUIRED; rss=1500 ban raise; §6.1 full path present; "
            "PRIMARY=HILIQ mask-only nonstd audit PIT; FULLA only --also-fulla-research; "
            f"FROZEN={FROZEN_SHA8}; ArchFROZEN={ARCH_FROZEN_REVIEW_SHA8}; "
            "C11≠full audit alpha; KEEP does NOT unblock X2 ACCEPT; "
            "COUNT APPROX != X2 ACCEPT; ban fund_portfolio mix"
        ),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    if uni == "FULLA":
        print(
            "STOP: --universe FULLA forbidden as PRIMARY; "
            "use --universe HILIQ and optional --also-fulla-research",
            file=sys.stderr,
        )
        return 2
    if getattr(args, "window", "x2") != "x2":
        print(
            f"STOP: --window must be x2 this ticket (got {args.window})",
            file=sys.stderr,
        )
        return 2
    return 0


def t1_of(cal_full, d):
    """Strict next trade day after available_at day D (PIT T1)."""
    import pandas as pd

    i = int(cal_full.searchsorted(pd.Timestamp(d), side="right"))
    if i >= len(cal_full):
        return None
    return cal_full[i]


def _instrument_vocab(names: list[str]) -> tuple[dict[str, int], list[str]]:
    """§6.1-3 compact int id map (sorted for stability)."""
    uniq = sorted(set(str(n) for n in names))
    return {n: i for i, n in enumerate(uniq)}, uniq




def _load_hiliq_mask_by_chunks(
    mask_path: Path,
    start: str,
    end: str,
    *,
    rss_cb=None,
    year_chunk: bool = True,
) -> tuple[dict, list, str]:
    """§6.1-2 stream HI_LIQ by year with parquet date pushdown; build mask_by then del.

    B1_PUSHDOWN: each year uses filters=[(date,'>=',y_start),(date,'<=',y_end)]
    intersected with X2 lo/hi; optional in_universe==True. Ban whole-table
    pq.read_table(mask_path) per year (prev d5cf50bb / VOID 167996dd Exit95).
    """
    import pandas as pd
    import pyarrow.parquet as pq

    stage("load_hiliq_begin")
    sha = sha256_file(mask_path)
    if sha[:8] != HI_LIQ_MASK_SHA8_PIN:
        raise SystemExit(
            f"STOP: HI_LIQ mask sha8 {sha[:8]} != pin {HI_LIQ_MASK_SHA8_PIN}"
        )
    lo = pd.Timestamp(start)
    hi = pd.Timestamp(end)
    pf = pq.ParquetFile(mask_path)
    # Prefer column prune — only date / instrument / in_universe
    cols = [c for c in ("date", "instrument", "in_universe") if c in pf.schema.names]
    if "date" not in cols or "instrument" not in cols:
        raise SystemExit(f"STOP: HI_LIQ mask missing date/instrument cols={cols}")
    has_univ = "in_universe" in cols
    del pf

    parts: list = []
    years = list(range(lo.year, hi.year + 1)) if year_chunk else [None]
    for y in years:
        if y is not None:
            y_start = pd.Timestamp(f"{y}-01-01")
            y_end = pd.Timestamp(f"{y}-12-31 23:59:59.999999")
            d_lo = max(lo, y_start)
            d_hi = min(hi, y_end)
            if d_lo > d_hi:
                gc.collect()
                if rss_cb:
                    rss_cb(f"after_hiliq_chunk_{y}")
                continue
            filt: list = [("date", ">=", d_lo), ("date", "<=", d_hi)]
        else:
            filt = [("date", ">=", lo), ("date", "<=", hi)]
        if has_univ:
            filt.append(("in_universe", "==", True))
        # TRUE pushdown — never whole-table read then filter
        t = pq.read_table(mask_path, columns=cols, filters=filt)
        df = t.to_pandas()
        del t
        gc.collect()
        df["date"] = pd.to_datetime(df["date"]).dt.normalize()
        df["instrument"] = df["instrument"].map(to_ts)
        if has_univ:
            # defense in depth if filter unsupported / nulls leaked
            df = df[df["in_universe"].fillna(False).astype(bool)]
        df = df[(df["date"] >= lo) & (df["date"] <= hi)]
        if y is not None:
            df = df[df["date"].dt.year == y]
        if not df.empty:
            # categorical for compact repr (§6.1-3)
            df["instrument"] = df["instrument"].astype("category")
            parts.append(df[["date", "instrument"]].copy())
        del df
        gc.collect()
        if rss_cb:
            rss_cb(f"after_hiliq_chunk_{y if y is not None else 'all'}")

    if not parts:
        raise SystemExit("STOP: HI_LIQ mask empty in window")
    mask = pd.concat(parts, ignore_index=True)
    del parts
    gc.collect()
    # expand categories to str for set membership (after concat)
    mask["instrument"] = mask["instrument"].astype(str)
    cal = sorted(mask["date"].unique())
    mask_by = {d: set(g["instrument"].tolist()) for d, g in mask.groupby("date")}
    del mask
    gc.collect()
    if rss_cb:
        rss_cb("after_mask_by")
    stage("load_hiliq_done")
    return mask_by, cal, sha


def _load_audit_and_build_excl(
    aud_path: Path,
    cal_full,
    cal,
    mask_by: dict,
    *,
    rss_cb=None,
) -> tuple[dict, dict, dict[str, int], list[str]]:
    """PIT excl: latest nonstd -> exclude. Returns excl, meta, id_of, id_names."""
    import pandas as pd
    import pyarrow.parquet as pq

    stage("audit_excl_begin")
    cols = [c for c in KNOWN_AUDIT_COLS if c in pq.ParquetFile(aud_path).schema.names]
    for need in ("ts_code", "available_at", "is_non_standard"):
        if need not in cols:
            raise SystemExit(f"STOP: audit parquet missing {need}")
    t = pq.read_table(aud_path, columns=cols)
    a = t.to_pandas()
    del t
    gc.collect()
    a["instrument"] = a["ts_code"].map(to_ts)
    a["d"] = pd.to_datetime(a["available_at"]).dt.tz_localize(None).dt.normalize()
    a = a.dropna(subset=["d", "instrument"])
    a = a.sort_values(["instrument", "d"])
    efs = [t1_of(cal_full, d) for d in a["d"]]
    a["ef"] = efs
    a = a.dropna(subset=["ef"])

    # compact int ids over HI_LIQ ∪ audit names
    all_names = set()
    for s in mask_by.values():
        all_names.update(s)
    all_names.update(a["instrument"].astype(str).tolist())
    id_of, id_names = _instrument_vocab(list(all_names))

    recs: dict[str, list] = defaultdict(list)
    for r in a.itertuples():
        recs[str(r.instrument)].append(
            (r.ef, bool(r.is_non_standard), str(getattr(r, "audit_result", "")))
        )
    funnel_ns = int(a["is_non_standard"].sum())
    n_rows = int(len(a))
    del a
    gc.collect()

    excl = {d: set() for d in cal}
    n_state = 0
    for d in cal:
        uni = mask_by[d]
        for inst in uni:
            hist = recs.get(inst)
            if not hist:
                continue
            last_ns = None
            for ef, ns, _ in hist:
                if ef <= d:
                    last_ns = ns
                else:
                    break
            if last_ns is True:
                excl[d].add(inst)
                n_state += 1
    del recs
    gc.collect()
    if rss_cb:
        rss_cb("after_audit_excl")
    meta = {
        "definition_zh": (
            "最新可用审计意见（available_at→T1 生效）为非标则剔除；"
            "下一份意见（标准或非标）T1 起改判"
        ),
        "n_opinion_rows": n_rows,
        "n_nonstd_rows": funnel_ns,
        "n_state_true_name_days": n_state,
        "c3_formula_pin": C3_FORMULA_PIN,
    }
    stage("audit_excl_done")
    return excl, meta, id_of, id_names


def _excl_thickness(excl: dict, mask_by: dict, cal) -> dict:
    import numpy as np

    daily_n = np.asarray(
        [len(excl[d] & mask_by[d]) for d in cal], dtype=float
    )
    if len(daily_n) == 0:
        return {
            "median": None,
            "frac_ge10": None,
            "zero_frac": None,
            "pass": False,
            "n_days": 0,
        }
    med = float(np.median(daily_n))
    frac10 = float(np.mean(daily_n >= 10.0))
    zero_frac = float(np.mean(daily_n == 0.0))
    ok = (
        med >= COV_MEDIAN_MIN
        and frac10 >= FRAC_GE10_MIN
        and zero_frac <= ZERO_FRAC_MAX
    )
    return {
        "median": med,
        "frac_ge10": frac10,
        "zero_frac": zero_frac,
        "min": float(np.min(daily_n)),
        "mean": float(np.mean(daily_n)),
        "n_days": int(len(daily_n)),
        "pass_thickness": ok,
        "thresholds": {
            "median_min": COV_MEDIAN_MIN,
            "frac_ge10_min": FRAC_GE10_MIN,
            "zero_frac_max": ZERO_FRAC_MAX,
        },
    }


def _expand_mask_parquet(
    excl: dict,
    mask_by: dict,
    cal,
    out_path: Path,
    *,
    rss_cb=None,
) -> str:
    """Write daily exclusion mask; mask=0 excluded, mask=1 kept computable."""
    import pandas as pd

    rows = []
    for d in cal:
        uni = mask_by[d]
        ex = excl[d]
        for inst in uni:
            m = 0 if inst in ex else 1
            rows.append(
                {
                    "trade_date": d,
                    "ts_code": inst,
                    "mask": m,
                    "alpha": float(m),  # overlay alpha = mask (not ranking main)
                    "is_non_standard_latest": bool(inst in ex),
                }
            )
        if len(rows) >= 500_000:
            # stream write chunks to limit RSS
            pass
    df = pd.DataFrame(rows)
    del rows
    gc.collect()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_path, index=False)
    sha = sha256_file(out_path)
    del df
    gc.collect()
    if rss_cb:
        rss_cb("after_mask_expand")
    return sha


def _held_cut_pairs_negevent(
    cap_path: Path, neg_path: Path, start: str, end: str
) -> tuple[set, dict]:
    """Build negevent held-cut pairs. Call in Jaccard worker OR after mask freed."""
    import pandas as pd

    cols = ["date", "instrument", "target_weight"]
    base = pd.read_parquet(cap_path, columns=cols)
    neg = pd.read_parquet(neg_path, columns=cols)
    base["date"] = pd.to_datetime(base["date"])
    neg["date"] = pd.to_datetime(neg["date"])
    lo, hi = pd.Timestamp(start), pd.Timestamp(end)
    base = base[
        (base["date"] >= lo) & (base["date"] <= hi) & (base["instrument"] != BALLAST)
    ]
    neg = neg[
        (neg["date"] >= lo) & (neg["date"] <= hi) & (neg["instrument"] != BALLAST)
    ]
    merged = base.merge(
        neg, on=["date", "instrument"], how="outer", suffixes=("_b", "_n")
    ).fillna(0.0)
    del base, neg
    gc.collect()
    cut = merged[
        (merged["target_weight_b"] > 0) & (merged["target_weight_n"] <= 1e-12)
    ]
    pairs = set(zip(cut["date"], cut["instrument"].map(to_ts)))
    meta = {
        "held_cut_name_days": int(len(cut)),
        "held_cut_unique_dates": int(cut["date"].nunique()),
    }
    del merged, cut
    gc.collect()
    return pairs, meta


def _daily_jaccard(
    excl: dict, other_pairs: set, cal, mask_by: dict
) -> dict:
    import numpy as np

    by: dict = defaultdict(set)
    for d, inst in other_pairs:
        by[d].add(str(inst))
    vals = []
    for d in cal:
        a = excl[d] & mask_by[d]
        b = by.get(d, set()) & mask_by[d]
        u = a | b
        if not u:
            vals.append(0.0)
        else:
            vals.append(len(a & b) / len(u))
    arr = np.asarray(vals, dtype=float)
    return {
        "max": float(arr.max()) if len(arr) else None,
        "mean": float(arr.mean()) if len(arr) else None,
        "median": float(np.median(arr)) if len(arr) else None,
        "n_days": int(len(arr)),
    }


def jaccard_worker_main(args) -> int:
    """§6.1-1 split process: load pair sets only; compute Jaccard; write JSON.

    Expects --pair-dir with excl_pairs.npy + id_names.json already landed by parent,
    OR rebuilds negevent/leaf36 pairs itself without holding parent excl dicts from
    a prior stage in the same process (fresh process).
    """
    import json as _json
    import numpy as np
    import pandas as pd

    enforce_single_thread()
    if args.rss_limit_mb > RSS_LIMIT_MB:
        print(
            f"STOP: ban raise rss_limit_mb>{RSS_LIMIT_MB} (got {args.rss_limit_mb})",
            file=sys.stderr,
        )
        return 2

    def _rss(label: str) -> int:
        return check_rss(
            label,
            rss_limit_mb=args.rss_limit_mb,
            c4_kb=args.c4_kb,
            hard_kb=args.hard_kb,
            split_kb=int(0.85 * args.c4_kb),
        )

    pair_dir = Path(args.pair_dir)
    assert_tmp_quantlab(pair_dir, "jaccard-pair-dir")
    out_json = Path(args.out_json)
    assert_tmp_quantlab(out_json, "jaccard-out-json")

    # Reload HI_LIQ + excl from compact pairs (parent pre-landed)
    id_names = _json.loads((pair_dir / "id_names.json").read_text())
    excl_arr = np.load(pair_dir / "excl_pairs.npy")
    cal = [pd.Timestamp(str(x)) for x in _json.loads((pair_dir / "cal.json").read_text())]
    mask_arr = np.load(pair_dir / "mask_pairs.npy")

    excl: dict = {d: set() for d in cal}
    mask_by: dict = {d: set() for d in cal}
    name_of = {i: n for i, n in enumerate(id_names)}
    cal_by_int = {int(d.strftime("%Y%m%d")): d for d in cal}

    for di, iid in excl_arr:
        d = cal_by_int.get(int(di))
        n = name_of.get(int(iid))
        if d is not None and n is not None:
            excl[d].add(n)
    del excl_arr
    gc.collect()
    _rss("jacc_after_excl_load")

    for di, iid in mask_arr:
        d = cal_by_int.get(int(di))
        n = name_of.get(int(iid))
        if d is not None and n is not None:
            mask_by[d].add(n)
    del mask_arr
    gc.collect()
    _rss("jacc_after_mask_load")

    # negevent pairs (this process; parent should have freed CAP/NEG frames)
    neg_pairs, neg_meta = _held_cut_pairs_negevent(
        Path(args.cap_adv), Path(args.negevent_w), X2_START, X2_END
    )
    _rss("jacc_after_negevent_pairs")
    j_neg = _daily_jaccard(excl, neg_pairs, cal, mask_by)
    del neg_pairs
    gc.collect()

    # leaf36 pairs: prefer prelanded; else lightweight from count JSON sample if present
    l36_path = pair_dir / "leaf36_pairs.npy"
    if l36_path.exists():
        l36_arr = np.load(l36_path)
        l36_pairs = set()
        for di, iid in l36_arr:
            d = cal_by_int.get(int(di))
            n = name_of.get(int(iid))
            if d is not None and n is not None:
                l36_pairs.add((d, n))
        del l36_arr
        gc.collect()
        l36_meta = {"source": "prelanded_leaf36_pairs.npy"}
    else:
        # Fallback: empty with PIN_GAP note (full rebuild is optional X2 path)
        l36_pairs = set()
        l36_meta = {
            "source": "absent",
            "pin_gap": True,
            "note": "leaf36 pairs not prelanded; disclose PIN_GAP; ban silent skip as pass",
        }
    _rss("jacc_after_leaf36_pairs")
    j_l36 = _daily_jaccard(excl, l36_pairs, cal, mask_by)
    del l36_pairs, excl, mask_by
    gc.collect()

    hard = False
    if j_neg.get("max") is not None and j_neg["max"] > JACCARD_HARD:
        hard = True
    if j_l36.get("max") is not None and j_l36["max"] > JACCARD_HARD:
        hard = True

    pk = _rss("jacc_final_peak_proof")
    payload = {
        "mechanism_tag": MECHANISM_TAG,
        "jaccard_hard": JACCARD_HARD,
        "jaccard_vs_negevent": j_neg,
        "jaccard_vs_leaf36": j_l36,
        "negevent_meta": neg_meta,
        "leaf36_meta": l36_meta,
        "hard_reject_jaccard": hard,
        "peak_rss_mb": pk / 1024.0,
        "peak_proof_le_1500": (pk / 1024.0) <= float(RSS_LIMIT_MB),
        "live": False,
        "x2_accept": False,
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(
        _json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({"jaccard_worker": "ok", "out": str(out_json), **payload}, ensure_ascii=False))
    return 0


def _run_jaccard_subprocess(args, pair_dir: Path, out_json: Path) -> dict:
    """§6.1-1: spawn fresh process for Jaccard; parent must not hold heavy frames."""
    cmd = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--jaccard-worker-only",
        "--pair-dir",
        str(pair_dir),
        "--out-json",
        str(out_json),
        "--cap-adv",
        str(args.cap_adv),
        "--negevent-w",
        str(args.negevent_w),
        "--rss-limit-mb",
        str(args.rss_limit_mb),
        "--c4-kb",
        str(args.c4_kb),
        "--hard-kb",
        str(args.hard_kb),
    ]
    env = os.environ.copy()
    env["OMP_NUM_THREADS"] = "1"
    env["MKL_NUM_THREADS"] = "1"
    env["OPENBLAS_NUM_THREADS"] = "1"
    env["NUMEXPR_NUM_THREADS"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    print(f"JACCARD_SUBPROCESS cmd={' '.join(cmd)}", flush=True)
    proc = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if proc.returncode in (94, 95):
        print(proc.stderr, file=sys.stderr)
        raise SystemExit(proc.returncode)
    if proc.returncode != 0:
        print(proc.stdout, file=sys.stderr)
        print(proc.stderr, file=sys.stderr)
        raise SystemExit(
            f"STOP: jaccard subprocess rc={proc.returncode}"
        )
    if not out_json.exists():
        raise SystemExit("STOP: jaccard worker did not write out-json")
    return json.loads(out_json.read_text(encoding="utf-8"))


def _disclose_mask_jaccard(
    excl: dict, mask_by: dict, cal, other_mask_path: Path, tag: str
) -> dict:
    """Disclose Jaccard vs leaf34/35 mask parquet (not hard reject)."""
    import pandas as pd

    if not other_mask_path.exists():
        return {"tag": tag, "pin_gap": True, "path": str(other_mask_path)}
    cols_try = ["trade_date", "ts_code", "mask", "date", "instrument"]
    df = pd.read_parquet(other_mask_path)
    use = [c for c in cols_try if c in df.columns]
    df = df[use].copy()
    if "trade_date" in df.columns:
        df["date"] = pd.to_datetime(df["trade_date"]).dt.normalize()
    else:
        df["date"] = pd.to_datetime(df["date"]).dt.normalize()
    if "ts_code" in df.columns:
        df["instrument"] = df["ts_code"].map(to_ts)
    else:
        df["instrument"] = df["instrument"].map(to_ts)
    if "mask" in df.columns:
        df = df[df["mask"] == 0]
    pairs = set(zip(df["date"], df["instrument"]))
    del df
    gc.collect()
    j = _daily_jaccard(excl, pairs, cal, mask_by)
    del pairs
    gc.collect()
    return {"tag": tag, "pin_gap": False, "jaccard": j, "path": str(other_mask_path)}


def run_build(args) -> int:
    """Real build path — requires --allow-real-data + existing --arch-ok-path."""
    import pandas as pd
    import pyarrow.parquet as pq

    enforce_single_thread()
    stage("run_build_begin")

    if args.rss_limit_mb > RSS_LIMIT_MB:
        print(
            f"STOP: ban raise rss_limit_mb>{RSS_LIMIT_MB} (got {args.rss_limit_mb})",
            file=sys.stderr,
        )
        return 2

    uni = normalize_universe(args.universe)
    if uni != "HILIQ":
        print(
            "STOP: PRIMARY universe must be HILIQ "
            "(FULLA only via --also-fulla-research)",
            file=sys.stderr,
        )
        return 2

    ok_path = args.arch_ok_path
    if ok_path is None or not Path(ok_path).exists():
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

    # Pre-flight: pgrep heavy writers must be empty before real data read
    for pat in ("kline.py", "export_static.py", "snapshot.py", "gen.py"):
        r = subprocess.run(
            ["pgrep", "-f", pat], capture_output=True, text=True
        )
        # pgrep returns 1 when empty — OK; any match -> STOP
        if r.returncode == 0 and r.stdout.strip():
            print(
                f"STOP: pgrep {pat} not empty before real data read:\n{r.stdout}",
                file=sys.stderr,
            )
            return 2

    def _rss(label: str) -> int:
        return check_rss(
            label,
            rss_limit_mb=args.rss_limit_mb,
            c4_kb=args.c4_kb,
            hard_kb=args.hard_kb,
            split_kb=int(0.85 * args.c4_kb),
        )

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    ts_tag = datetime.now(ET).strftime("%Y%m%d_%H%M%S")
    run_dir = out / ts_tag
    run_dir.mkdir(parents=True, exist_ok=True)

    tmp_root = Path(f"{SAMPLER_PREFIX}run_{ts_tag}")
    assert_tmp_quantlab(tmp_root, "leaf38-run-tmp")
    tmp_root.mkdir(parents=True, exist_ok=True)
    pair_dir = tmp_root / "pairs"
    pair_dir.mkdir(parents=True, exist_ok=True)

    # --- Stage A: HI_LIQ mask_by (stream) ---
    mask_by, cal, hiliq_sha = _load_hiliq_mask_by_chunks(
        Path(args.hi_liq_mask), X2_START, X2_END, rss_cb=_rss, year_chunk=True
    )
    # full calendar for T1 (may extend before window)
    cal_tbl = pq.read_table(
        Path(args.calendar),
        columns=[
            c
            for c in ("cal_date", "is_open", "pretrade_date")
            if c in pq.ParquetFile(Path(args.calendar)).schema.names
        ],
    )
    cal_df = cal_tbl.to_pandas()
    del cal_tbl
    gc.collect()
    # Prefer SSE trade days from HI_LIQ unique dates as cal_full baseline,
    # extended by calendar file if present
    if "cal_date" in cal_df.columns:
        dcol = "cal_date"
    else:
        dcol = cal_df.columns[0]
    cal_df[dcol] = pd.to_datetime(cal_df[dcol]).dt.normalize()
    if "is_open" in cal_df.columns:
        cal_df = cal_df[cal_df["is_open"].astype(str).isin(["1", "1.0", "true", "True"]) | (cal_df["is_open"] == 1)]
    cal_full = pd.DatetimeIndex(sorted(set(cal_df[dcol].tolist()) | set(cal)))
    del cal_df
    gc.collect()
    _rss("after_calendar")

    # --- Stage B: audit excl ---
    excl, excl_meta, id_of, id_names = _load_audit_and_build_excl(
        Path(args.audit_opinion),
        cal_full,
        cal,
        mask_by,
        rss_cb=_rss,
    )
    thick = _excl_thickness(excl, mask_by, cal)
    print(f"THICKNESS {json.dumps(thick)}", flush=True)

    # Land compact pairs then free heavy str sets for Jaccard subprocess (§6.1-1/3)
    excl_pairs = []
    mask_pairs = []
    for d in cal:
        di_cache = None
        for inst in excl[d]:
            iid = id_of[inst]
            if di_cache is None:
                di_cache = int(pd.Timestamp(d).strftime("%Y%m%d"))
            excl_pairs.append((di_cache, iid))
        di_cache = int(pd.Timestamp(d).strftime("%Y%m%d"))
        for inst in mask_by[d]:
            mask_pairs.append((di_cache, id_of[inst]))
    import numpy as np

    np.save(
        pair_dir / "excl_pairs.npy",
        np.asarray(excl_pairs, dtype=np.int32).reshape(-1, 2)
        if excl_pairs
        else np.zeros((0, 2), dtype=np.int32),
    )
    np.save(
        pair_dir / "mask_pairs.npy",
        np.asarray(mask_pairs, dtype=np.int32).reshape(-1, 2)
        if mask_pairs
        else np.zeros((0, 2), dtype=np.int32),
    )
    (pair_dir / "id_names.json").write_text(
        json.dumps(id_names, ensure_ascii=False), encoding="utf-8"
    )
    (pair_dir / "cal.json").write_text(
        json.dumps([pd.Timestamp(d).strftime("%Y-%m-%d") for d in cal]),
        encoding="utf-8",
    )
    del excl_pairs, mask_pairs
    gc.collect()
    _rss("after_pair_land")

    # Expand mask parquet WHILE excl still in memory
    mask_out = run_dir / f"exclusion_mask_HILIQ_x2_{ts_tag}.parquet"
    mask_sha = _expand_mask_parquet(excl, mask_by, cal, mask_out, rss_cb=_rss)

    # Disclose vs 34/35 before freeing excl (same process OK — lighter than ANN)
    disclose = {}
    if not args.no_overlap_report:
        disclose["leaf34"] = _disclose_mask_jaccard(
            excl, mask_by, cal, Path(args.leaf34_mask), "leaf34"
        )
        _rss("after_disclose_leaf34")
        disclose["leaf35"] = _disclose_mask_jaccard(
            excl, mask_by, cal, Path(args.leaf35_mask), "leaf35"
        )
        _rss("after_disclose_leaf35")
        # leaf37: disclose path if mask exists; else PIN_GAP
        l37 = Path(args.leaf37_mask)
        if l37.is_dir():
            cands = sorted(l37.glob("**/exclusion_mask_HILIQ_x2_*.parquet"))
            l37p = cands[-1] if cands else l37
        else:
            l37p = l37
        disclose["leaf37"] = _disclose_mask_jaccard(
            excl, mask_by, cal, l37p, "leaf37"
        )
        _rss("after_disclose_overlap")

    # Free excl/mask_by before Jaccard subprocess (§6.1-1)
    del excl, mask_by, id_of
    gc.collect()
    _rss("after_free_before_jaccard_subprocess")

    jacc_json = tmp_root / "jaccard_worker.json"
    jacc = _run_jaccard_subprocess(args, pair_dir, jacc_json)
    _rss("after_jaccard_subprocess")

    if jacc.get("hard_reject_jaccard"):
        print(
            "STOP: Jaccard hard reject vs negevent or leaf36 (>0.5)",
            file=sys.stderr,
        )
        # Still write receipt for audit; non-zero exit
        hard_exit = True
    else:
        hard_exit = False

    pk = _rss("final_peak_proof")
    peak_mb = pk / 1024.0
    peak_ok = peak_mb <= float(RSS_LIMIT_MB)

    meta = {
        "live": False,
        "ok_requested": False,
        "promotion_approved": False,
        "executed": True,
        "x2_accept": False,
        "mechanism_tag": MECHANISM_TAG,
        "script": SCRIPT_REL,
        "script_sha8": script_sha256()[:8],
        "frozen_sha8": FROZEN_SHA8,
        "arch_ok_path": str(ok_path),
        "arch_ok_sha8": ok_sha[:8],
        "hiliq_sha8": hiliq_sha[:8],
        "mask_out": str(mask_out.relative_to(ROOT)),
        "mask_sha8": mask_sha[:8],
        "excl_meta": excl_meta,
        "thickness": thick,
        "jaccard": jacc,
        "disclose_overlap": disclose,
        "peak_rss_mb": peak_mb,
        "peak_proof_le_1500": peak_ok,
        "rss_limit_mb": RSS_LIMIT_MB,
        "section_6_1": {
            "split_process": True,
            "stream_chunk": True,
            "compact_int_id": True,
            "single_thread": True,
            "hard_abort_94_95": True,
            "peak_proof_required": True,
        },
        "cost_bp_eval": COST_BP_EVAL,
        "window": f"{X2_START} → {X2_END}",
        "primary_delivery": PRIMARY_DELIVERY,
        "keep_does_not_unblock_x2_accept": True,
        "count_approx_not_x2_accept": True,
        "ban_self_sign_ok": True,
        "note": (
            "Formal build ran under Main window + Arch .ok gate; "
            "KEEP≠ACCEPT; peak_proof required; this script never writes .ok"
        ),
    }
    meta_path = run_dir / f"run_meta_{ts_tag}.json"
    meta_path.write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(meta, indent=2, ensure_ascii=False))

    if not peak_ok:
        print(
            f"STOP: peak_proof failed peak_rss_mb={peak_mb:.1f} > {RSS_LIMIT_MB}; "
            f"ban .ok / ban X2",
            file=sys.stderr,
        )
        return 94
    if hard_exit:
        return 3
    if not thick.get("pass_thickness"):
        print("STOP: thickness gate failed (runtime disclose; ban rewrite)", file=sys.stderr)
        return 3

    # soft-penalty path (non PRIMARY) — PIN_GAP if enabled without SW/style
    if args.enable_soft_penalty:
        print(
            "STOP: soft-penalty non PRIMARY; enable requires SW+logmv+style wired; "
            "PIN_GAP this ticket (mask-only PRIMARY only)",
            file=sys.stderr,
        )
        return 2

    stage("run_build_done")
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description=(
            "Leaf38 audit nonstd exclusion overlay formal build (HILIQ x x2); "
            "NOT authorized without --allow-real-data + --arch-ok-path. "
            "Default: use --dry-compile-only or --help (no heavy compute)."
        )
    )
    ap.add_argument(
        "--universe",
        default="HILIQ",
        choices=("HILIQ", "HI_LIQ", "FULLA"),
        help="PRIMARY must be HILIQ (FULLA as --universe → STOP; use --also-fulla-research)",
    )
    ap.add_argument("--window", default="x2", choices=("x2",))
    ap.add_argument("--x2-end", default=X2_END_TRADE_DATE)
    ap.add_argument("--out", type=Path, default=None, help="Required for real build")
    ap.add_argument("--rss-limit-mb", type=int, default=RSS_LIMIT_MB)
    ap.add_argument("--c4-kb", type=int, default=C4_KB)
    ap.add_argument("--stop-kb", type=int, default=STOP_KB)
    ap.add_argument("--hard-kb", type=int, default=HARD_KB)
    ap.add_argument("--allow-real-data", action="store_true", default=False)
    ap.add_argument(
        "--arch-ok-path",
        type=Path,
        default=None,
        help="Existing Arch .ok (sha8 not in forbid); process gate with Main window",
    )
    ap.add_argument(
        "--execute",
        action="store_true",
        default=False,
        help="Optional; still requires --allow-real-data + --arch-ok-path",
    )
    ap.add_argument("--hi-liq-mask", type=Path, default=HI_LIQ_MASK_DEFAULT)
    ap.add_argument("--fulla-mask", type=Path, default=FULLA_MASK_DEFAULT)
    ap.add_argument("--audit-opinion", type=Path, default=AUDIT_OPINION_DEFAULT)
    ap.add_argument("--calendar", type=Path, default=CAL_DEFAULT)
    ap.add_argument("--cap-adv", type=Path, default=CAP_ADV_DEFAULT)
    ap.add_argument("--negevent-w", type=Path, default=NEGEVENT_W_DEFAULT)
    ap.add_argument("--negevent-meta", type=Path, default=NEGEVENT_META_DEFAULT)
    ap.add_argument("--ann-main", type=Path, default=ANN_MAIN_DEFAULT)
    ap.add_argument("--ann-post", type=Path, default=ANN_POST_DEFAULT)
    ap.add_argument("--sw-l1", type=Path, default=SW_L1_DEFAULT)
    ap.add_argument("--float-mktcap", type=Path, default=FLOAT_MKTCAP_DEFAULT)
    ap.add_argument("--daily-dir", type=Path, default=DAILY_DIR_DEFAULT)
    ap.add_argument("--adj-factor", type=Path, default=ADJ_FACTOR_DEFAULT)
    ap.add_argument("--leaf34-mask", type=Path, default=LEAF34_MASK_DEFAULT)
    ap.add_argument("--leaf35-mask", type=Path, default=LEAF35_MASK_DEFAULT)
    ap.add_argument("--leaf36-count-json", type=Path, default=LEAF36_COUNT_JSON_DEFAULT)
    ap.add_argument("--leaf37-mask", type=Path, default=LEAF37_MASK_DEFAULT)
    ap.add_argument("--sample-dir", type=Path, default=None)
    ap.add_argument(
        "--also-fulla-research",
        action="store_true",
        default=False,
        help="Optional FULLA research mask (never PRIMARY verdict)",
    )
    ap.add_argument(
        "--enable-soft-penalty",
        action="store_true",
        default=False,
        help="Optional soft-penalty path (NON PRIMARY; requires SW+style; default OFF)",
    )
    ap.add_argument(
        "--overlap-report",
        action="store_true",
        default=False,
        help="Force write overlap JSON (also default on real path)",
    )
    ap.add_argument(
        "--no-overlap-report",
        action="store_true",
        default=False,
        help="Banned on real path (C7); dry/dev only — real build STOPs if set",
    )
    ap.add_argument(
        "--dry-compile-only",
        action="store_true",
        default=False,
        help="Print pins; ZERO big-table load; exit 0 (recommended default)",
    )
    ap.add_argument(
        "--jaccard-worker-only",
        action="store_true",
        default=False,
        help="§6.1 split-process worker: read compact pairs; write Jaccard JSON",
    )
    ap.add_argument("--pair-dir", type=Path, default=None)
    ap.add_argument("--out-json", type=Path, default=None)
    return ap


def main(argv: list[str] | None = None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)

    if args.jaccard_worker_only:
        if args.pair_dir is None or args.out_json is None:
            print(
                "STOP: --jaccard-worker-only requires --pair-dir and --out-json",
                file=sys.stderr,
            )
            return 2
        return jaccard_worker_main(args)

    if args.dry_compile_only:
        return dry_compile_only_print(args)

    # Default without flags: refuse heavy path (prefer --help / --dry-compile-only)
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
    if args.out is None:
        print(
            "STOP: --out is required for build (or pass --dry-compile-only)",
            file=sys.stderr,
        )
        return 2
    if args.no_overlap_report:
        print(
            "STOP: --no-overlap-report banned on real path (C7)",
            file=sys.stderr,
        )
        return 2
    return run_build(args)


if __name__ == "__main__":
    raise SystemExit(main())
