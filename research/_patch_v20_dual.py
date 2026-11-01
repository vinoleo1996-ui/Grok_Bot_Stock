#!/usr/bin/env python3
"""Patch v20_dual_track from v19 base into dual-track A(stock)/B(etf_timing)."""
from pathlib import Path
p = Path("/workspace/QuantLab/research/ai_factor_gp_reopen_hardgate_v20_dual_track.py")
s = p.read_text(encoding="utf-8")

# --- header ---
old_header = s.split('from __future__', 1)[0]
new_header = '''#!/usr/bin/env python3
"""GP reopen v20_dual_track — New Bot 发令 2026-10-12：双轨，勿再同式抬ρ空转。

Track A (stock residual → Alpha):
  - Leaves ONLY: unlock/lu_*/ld_*/dt_*/rz_*/rzrq_*/rz_intensity*/ann_earn|buyback|penalty
    (+ v19 forced crosses), ind_rel_*
  - SYNTAX hard-ban IN TREE: overnight_ret, fsr*, ann_insider*, idx_w*, idx_w500* (saturated)
  - Label ε; Z active24=True; hard-ban N=24 near-iso
  - novelty vs primary24: ρ_soft=0.35 ρ_hard=0.50 (slightly looser than v19 wipeout)
  - Dual ICIR; mid/large; impact gates unchanged
  - OUT: output/ai_factor/gp_reopen_hardgate_v20_track_a_stock/

Track B (ETF timing → Beta, NOT Alpha shortlist):
  - Expressions from ind_etf_share_flow / etf_*_flow / etf_share_chg_* (theme skipped if RSS)
  - Do NOT put into stock residual Z
  - Tag sleeve=etf_timing; package for QuantLab Beta
  - OUT: output/ai_factor/gp_reopen_hardgate_v20_track_b_etf_timing/

Ban CB/gold both tracks. lean LOOKBACK=2024-04-01 PANEL_END=2025-06-30.
MEM_CAP=2200; SELF_STOP sticky>2400 OR available<2500 — DO NOT raise.
Sequential A then B (no concurrent heavy GP). promotion_approved=false; no Strategy; no seal.
Launch: LEO_AI_FACTOR_EXPLORE_OK=1.
"""

'''
s = new_header + 'from __future__' + s.split('from __future__', 1)[1]

# --- constants block ---
s = s.replace(
'''OUT = ROOT / "output/ai_factor/gp_reopen_hardgate_v19_etf_newleaf"
REPORT = ROOT / "output/alpha/AI_FACTOR_GP_REOPEN_HARDGATE_V19_ETF_NEWLEAF_ZH.md"
SPEC_JSON = ROOT / "output/ai_factor/p0_theta_lam_z/spec.json"
EXPLORE_START = pd.Timestamp("2024-06-03")
LOOKBACK_START = pd.Timestamp("2024-04-01")  # v17b lean2: further shrink vs Mar1
PANEL_END = pd.Timestamp("2025-06-30")  # v17b lean2: clip end (was Dec31)
IMP60_FLOOR = 0.10
THETA_COV = 0.08
THETA_COV_PRIMARY = 0.15
LAMBDA_FAM = 0.30
RHO_FAM_SOFT = 0.28  # v19 stricter vs primary24 (was 0.35)
RHO_FAM_HARD = 0.40  # v19 stricter vs primary24 (was 0.50); early kill high-corr
SEED = 20261102
MAX_EVAL = 150  # New Bot: 120–180
POP, GEN, TOP_K = 12, 10, 15  # trimmed vs v10 for peak≤1200
MIN_EVAL_BEFORE_EMPTY_STOP = 100
SEED_FRAC_FORCED = 0.55  # v19: force new-leaf families
COST = 0.0025
PROMOTION_APPROVED = False
MEM_CAP_MB = 2200  # New Bot peak≤2.2GB; SELF_STOP RSS sticky>2400 OR available<2500
SELF_STOP_AVAILABLE_MB = 2500
SELF_STOP_RSS_STICKY_MB = 2400  # do not stealth-raise; archive fragment if early stop
WINDOW = "gp_reopen_hardgate_v19_etf_newleaf_20240603_explore"
''',
'''OUT_A = ROOT / "output/ai_factor/gp_reopen_hardgate_v20_track_a_stock"
OUT_B = ROOT / "output/ai_factor/gp_reopen_hardgate_v20_track_b_etf_timing"
OUT = OUT_A  # Track A default working dir (legacy aliases)
REPORT = ROOT / "output/alpha/AI_FACTOR_GP_REOPEN_HARDGATE_V20_DUAL_ZH.md"
SPEC_JSON = ROOT / "output/ai_factor/p0_theta_lam_z/spec.json"
EXPLORE_START = pd.Timestamp("2024-06-03")
LOOKBACK_START = pd.Timestamp("2024-04-01")  # v17b/v18 lean — DO NOT widen
PANEL_END = pd.Timestamp("2025-06-30")
IMP60_FLOOR = 0.10
THETA_COV = 0.08
THETA_COV_PRIMARY = 0.15
LAMBDA_FAM = 0.30
RHO_FAM_SOFT = 0.35  # v20: slightly looser than v19 (0.28) to avoid wipeout
RHO_FAM_HARD = 0.50  # v20: slightly looser than v19 (0.40)
SEED = 20261103
MAX_EVAL = 150  # New Bot: 120–180
POP, GEN, TOP_K = 12, 10, 15
MIN_EVAL_BEFORE_EMPTY_STOP = 100
SEED_FRAC_FORCED = 0.60  # v20 Track A: force allowed-leaf families
COST = 0.0025
PROMOTION_APPROVED = False
MEM_CAP_MB = 2200  # DO NOT raise
SELF_STOP_AVAILABLE_MB = 2500
SELF_STOP_RSS_STICKY_MB = 2400  # DO NOT raise
WINDOW = "gp_reopen_hardgate_v20_dual_20240603_explore"
TRACK_B_MAX_EVAL = 80  # lighter ETF timing segment after A
''')

# --- EVENT / SEARCH leaves for Track A (no overnight/idx/fsr) ---
s = s.replace(
'''EVENT_LEAVES = (
    "dt_net_5", "dt_net_10", "dt_flag_5",
    "rz_delta_5", "rz_delta_10", "rzrq_delta_5", "rz_intensity",
    # v19 forced: margin intensity shock/jump (not plain rz_delta×ann)
    "rz_intensity_delta_5", "rz_abs_burst_5", "rzrq_shock_5",
    "nb_north_money",
    "ind_rel_overnight", "ind_rel_intraday",
    "ann_buyback_5", "ann_penalty_5", "ann_earn_signed_5",
    # v19 forced: announcement subtype cross-sectional interactions
    "ann_earn_x_buyback", "ann_earn_x_penalty", "ann_buyback_x_penalty",
    # ETF 机制叶：份额变化（major+theme）/ 行业层份额流；另有 STRUCT etf_*_flow
    "etf_share_chg_major", "etf_share_chg_theme", "ind_etf_share_flow",
    # v19 forced: ind_etf × ind_rel pre-materialized
    "ind_etf_x_ind_rel_on", "ind_etf_x_ind_rel_id",
    "unlock_resid",
    "lu_next_on", "ld_next_on",
    # v19 forced: dragon-tiger × post-limit-up structure
    "dt_x_lu_next", "dt_x_lu_streak", "dt_x_lu_height",
)
FORCED_NEW_LEAVES = (
    "ann_earn_x_buyback", "ann_earn_x_penalty", "ann_buyback_x_penalty",
    "rz_intensity_delta_5", "rz_abs_burst_5", "rzrq_shock_5",
    "dt_x_lu_next", "dt_x_lu_streak", "dt_x_lu_height",
    "ind_etf_x_ind_rel_on", "ind_etf_x_ind_rel_id",
)
STRUCT_CROSS_LEAVES = (
    "overnight_ret", "intraday_ret", "on_minus_id",
    "etf_theme_flow", "etf_major_flow", "etf_all_flow",
    "if_basis", "if_basis_x_on",
    "lu_height", "lu_promote_rate",
    "days_since_lu", "lu_streak",
) + DENSE_MICRO_LEAVES + EVENT_LEAVES
AUX_LEAVES = ()
# v17b: de-prioritize idx/lev in GP search (still materialize for PRIMARY Z);
# keep EVENT/unlock/ETF/amt focus to cut GP working set + seed bias.
_SEARCH_DROP = frozenset({
    "idx_w300_delta_20", "idx_w500_delta_20", "idx_w_delta_20",
    "neg_idx_w_delta_20", "abs_idx_w_delta_20",
    "lev_delta_20", "abs_lev_delta_20",
    "liq_cv_20", "neg_liq_cv_20", "liq_burst_10",
})
SEARCH_LEAVES = tuple(x for x in (L1H_CROSS_LEAVES + STRUCT_CROSS_LEAVES) if x not in _SEARCH_DROP)
''',
'''# Track A allowed event/struct leaves (New Bot: unlock/lu/ld/dt/rz/ann_earn|buyback|penalty/ind_rel + forced)
EVENT_LEAVES = (
    "dt_net_5", "dt_net_10", "dt_flag_5",
    "rz_delta_5", "rz_delta_10", "rzrq_delta_5", "rz_intensity",
    "rz_intensity_delta_5", "rz_abs_burst_5", "rzrq_shock_5",
    "ind_rel_overnight", "ind_rel_intraday",
    "ann_buyback_5", "ann_penalty_5", "ann_earn_signed_5",
    "ann_earn_x_buyback", "ann_earn_x_penalty", "ann_buyback_x_penalty",
    "unlock_resid",
    "lu_next_on", "ld_next_on",
    "dt_x_lu_next", "dt_x_lu_streak", "dt_x_lu_height",
    # keep ind_etf×ind_rel forced crosses as stock-side (A); pure etf_*_flow reserved for Track B
    "ind_etf_x_ind_rel_on", "ind_etf_x_ind_rel_id",
    "ind_etf_share_flow",  # ok as cross with ind_rel; pure ETF timing → Track B
)
FORCED_NEW_LEAVES = (
    "ann_earn_x_buyback", "ann_earn_x_penalty", "ann_buyback_x_penalty",
    "rz_intensity_delta_5", "rz_abs_burst_5", "rzrq_shock_5",
    "dt_x_lu_next", "dt_x_lu_streak", "dt_x_lu_height",
    "ind_etf_x_ind_rel_on", "ind_etf_x_ind_rel_id",
)
# STRUCT for requires_cross / materialize; overnight/idx still loaded for Z but NOT searchable
STRUCT_CROSS_LEAVES = (
    "overnight_ret", "intraday_ret", "on_minus_id",
    "etf_theme_flow", "etf_major_flow", "etf_all_flow",
    "if_basis", "if_basis_x_on",
    "lu_height", "lu_promote_rate",
    "days_since_lu", "lu_streak",
    "etf_share_chg_major", "etf_share_chg_theme",
) + DENSE_MICRO_LEAVES + EVENT_LEAVES
AUX_LEAVES = ()
# Track A SEARCH: only allowed leaves (syntax hard-ban overnight/fsr/ann_insider/idx_w*)
_TRACK_A_ALLOW = frozenset({
    "unlock_resid",
    "lu_next_on", "ld_next_on", "lu_height", "lu_streak", "lu_promote_rate",
    "dt_net_5", "dt_net_10", "dt_flag_5",
    "dt_x_lu_next", "dt_x_lu_streak", "dt_x_lu_height",
    "rz_delta_5", "rz_delta_10", "rzrq_delta_5", "rz_intensity",
    "rz_intensity_delta_5", "rz_abs_burst_5", "rzrq_shock_5",
    "ann_buyback_5", "ann_penalty_5", "ann_earn_signed_5",
    "ann_earn_x_buyback", "ann_earn_x_penalty", "ann_buyback_x_penalty",
    "ind_rel_overnight", "ind_rel_intraday",
    "ind_etf_share_flow", "ind_etf_x_ind_rel_on", "ind_etf_x_ind_rel_id",
})
_SEARCH_DROP = frozenset({
    "idx_w300_delta_20", "idx_w500_delta_20", "idx_w_delta_20",
    "neg_idx_w_delta_20", "abs_idx_w_delta_20",
    "lev_delta_20", "abs_lev_delta_20",
    "liq_cv_20", "neg_liq_cv_20", "liq_burst_10",
    "overnight_ret", "intraday_ret", "on_minus_id",
    "etf_theme_flow", "etf_major_flow", "etf_all_flow",
    "if_basis", "if_basis_x_on",
    "days_since_lu",
    "amt_cv_20", "neg_amt_cv_20",
    "nb_north_money",
    "etf_share_chg_major", "etf_share_chg_theme",  # Track B
})
SEARCH_LEAVES = tuple(x for x in (L1H_CROSS_LEAVES + STRUCT_CROSS_LEAVES) if x in _TRACK_A_ALLOW and x not in _SEARCH_DROP)

# Track B ETF timing leaves (not into stock residual Z for scoring)
TRACK_B_LEAVES = (
    "ind_etf_share_flow", "etf_share_chg_major", "etf_share_chg_theme",
    "etf_theme_flow", "etf_major_flow", "etf_all_flow",
)

# Syntax hard-ban stems that must not appear as leaves in Track A candidates
SYNTAX_HARD_BAN_STEMS = (
    "overnight_ret", "fsr", "ann_insider", "idx_w", "idx_w500", "idx_w300",
)
''')

# EXCLUDED: add syntax-ban relatives explicitly
s = s.replace(
'''EXCLUDED_LEAVES = (
    "ann_n_5", "ann_insider_dec_5",  # insider/FSR/lockup transplant pool banned; buyback/penalty/earn allowed as EVENT
    "idx_w500", "idx_w300", "idx_w", "lev_pit", "neg_lev_pit",
    "lockup_S_20",
    "fsr", "fsr_delta_20",
''',
'''EXCLUDED_LEAVES = (
    "ann_n_5", "ann_insider_dec_5",  # insider/FSR/lockup transplant pool banned
    "idx_w500", "idx_w300", "idx_w", "lev_pit", "neg_lev_pit",
    "lockup_S_20",
    "fsr", "fsr_delta_20",
    # v20 Track A syntax hard-ban (cannot appear as leaves in candidates)
    "overnight_ret",
    "idx_w500_delta_20", "idx_w300_delta_20", "idx_w_delta_20",
    "neg_idx_w_delta_20", "abs_idx_w_delta_20",
''')

# log rename
s = s.replace('def log(*a): print(f"[gp_v19 {time.time()-t0:5.0f}s {mem_mb():.0f}MB]"',
              'def log(*a): print(f"[gp_v20 {time.time()-t0:5.0f}s {mem_mb():.0f}MB]"')

# isomorphic_reason: add syntax hard-ban early
old_iso_start = '''def isomorphic_reason(expr: str) -> str | None:
    e = expr.strip()
    if e in KNOWN_SHORTLIST_EXACT:
        return "EXACT_SHORTLIST"
    L = leaves_in(e)
    # Leo/New Bot: CB / gold leaves never enter main candidates
'''
new_iso_start = '''def isomorphic_reason(expr: str) -> str | None:
    e = expr.strip()
    if e in KNOWN_SHORTLIST_EXACT:
        return "EXACT_SHORTLIST"
    L = leaves_in(e)
    # v20 SYNTAX hard-ban: overnight_ret / fsr* / ann_insider* / idx_w* must not appear in tree
    for x in L:
        if x == "overnight_ret" or x.startswith("overnight_"):
            return "SYNTAX_HARD_BAN_OVERNIGHT"
        if x == "fsr" or x.startswith("fsr"):
            return "SYNTAX_HARD_BAN_FSR"
        if x.startswith("ann_insider"):
            return "SYNTAX_HARD_BAN_ANN_INSIDER"
        if x.startswith("idx_w") or x in ("neg_idx_w_delta_20", "abs_idx_w_delta_20"):
            return "SYNTAX_HARD_BAN_IDX_W"
        if x not in _TRACK_A_ALLOW and x not in ("intraday_ret", "on_minus_id", "amt_cv_20", "neg_amt_cv_20",
                                                 "etf_theme_flow", "etf_major_flow", "etf_all_flow",
                                                 "if_basis", "if_basis_x_on", "days_since_lu",
                                                 "etf_share_chg_major", "etf_share_chg_theme",
                                                 "nb_north_money", "liq_cv_20", "neg_liq_cv_20", "liq_burst_10",
                                                 "lev_delta_20", "abs_lev_delta_20"):
            # allow only Track-A set in candidates; other structural may still be materialized for Z
            pass
    # Leo/New Bot: CB / gold leaves never enter main candidates
'''
if old_iso_start not in s:
    raise SystemExit("iso start not found")
s = s.replace(old_iso_start, new_iso_start, 1)

# Also reject non-allowed leaves in Track A candidates more strictly
old_cb = '''    if any(
        (x in EXCLUDED_LEAVES)
        or any(x == s or x.startswith(s + "_") or x.startswith(s) for s in CB_GOLD_BANNED_STEMS)
        for x in L
    ):
        return "HARD_BAN_CB_GOLD_MAINLINE"
'''
new_cb = '''    if any(
        (x in EXCLUDED_LEAVES)
        or any(x == s or x.startswith(s + "_") or x.startswith(s) for s in CB_GOLD_BANNED_STEMS)
        for x in L
    ):
        return "HARD_BAN_CB_GOLD_MAINLINE"
    # v20 Track A: every leaf must be in allowed set
    bad = [x for x in L if x not in _TRACK_A_ALLOW]
    if bad:
        return "SYNTAX_HARD_BAN_LEAF_NOT_IN_TRACK_A"
'''
s = s.replace(old_cb, new_cb, 1)

# main() start logging
s = s.replace('os.environ["QL_V19_AVAILABLE_AT_START_MB"]', 'os.environ["QL_V20_AVAILABLE_AT_START_MB"]')
s = s.replace('os.environ["QL_V11_AVAILABLE_AT_START_MB"] = os.environ["QL_V19_AVAILABLE_AT_START_MB"]',
              'os.environ["QL_V11_AVAILABLE_AT_START_MB"] = os.environ["QL_V20_AVAILABLE_AT_START_MB"]')
s = s.replace(
'''    log("v19_etf_newleaf start", "pid", os.getpid(), "available_mb", round(float(avail0), 1),
        "MAX_EVAL", MAX_EVAL, "POP", POP, "MEM_CAP", MEM_CAP_MB,
        "NOTE", "v19 etf_newleaf: forced ann×ann/dt×lu/rz-shock/ind_etf×ind_rel; rho_hard=0.40; lean LOOKBACK=2024-04-01 PANEL_END=2025-06-30; MEM_CAP=2200 NO raise")
    OUT.mkdir(parents=True, exist_ok=True)
''',
'''    log("v20_dual_track start", "pid", os.getpid(), "available_mb", round(float(avail0), 1),
        "MAX_EVAL", MAX_EVAL, "POP", POP, "MEM_CAP", MEM_CAP_MB,
        "NOTE", "v20 dual: TrackA stockε (ban overnight/fsr/ann_insider/idx_w; rho 0.35/0.50) then TrackB etf_timing→Beta; lean MEM_CAP=2200 NO raise")
    OUT_A.mkdir(parents=True, exist_ok=True)
    OUT_B.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
''')

s = s.replace(
'''    # v19: stricter vs primary24 — take constants (do not inherit looser 0.35/0.50 from spec)
    rho_soft = float(RHO_FAM_SOFT)
    rho_hard = float(RHO_FAM_HARD)
    log("v19 novelty vs primary24", "rho_soft", rho_soft, "rho_hard", rho_hard, "(stricter than prior 0.35/0.50)")
''',
'''    # v20: slightly looser than v19 wipeout — use constants 0.35/0.50
    rho_soft = float(RHO_FAM_SOFT)
    rho_hard = float(RHO_FAM_HARD)
    log("v20 TrackA novelty vs primary24", "rho_soft", rho_soft, "rho_hard", rho_hard, "(looser than v19 0.28/0.40)")
''')

s = s.replace('meta0["v19_lean"]', 'meta0["v20_lean"]')
s = s.replace('log("v19 panel clip"', 'log("v20 panel clip"')

# partners: remove overnight_ret
s = s.replace(
'''    _event_partners = [
        "etf_major_flow", "etf_theme_flow", "etf_all_flow",
        "lu_streak", "lu_height", "lu_next_on",
        "ind_rel_overnight", "ind_rel_intraday",
        "intraday_ret", "amt_cv_20", "neg_amt_cv_20",
        "on_minus_id",
        # overnight kept but de-prioritized vs overnight×idx / overnight×buyback spam
        "overnight_ret",
    ]
''',
'''    _event_partners = [
        "lu_streak", "lu_height", "lu_next_on", "ld_next_on",
        "ind_rel_overnight", "ind_rel_intraday",
        "unlock_resid",
        "ann_earn_signed_5", "ann_penalty_5", "ann_buyback_5",
        "dt_flag_5", "dt_net_5", "dt_net_10",
        "rz_intensity", "rzrq_delta_5",
        "ind_etf_share_flow", "ind_etf_x_ind_rel_on", "ind_etf_x_ind_rel_id",
    ]
''')

# remove etf share/theme from event_prefer that conflict; keep forced
s = s.replace(
'''        "ind_etf_share_flow", "etf_share_chg_theme", "etf_share_chg_major",
        "lu_next_on", "dt_flag_5", "dt_net_5", "dt_net_10",
''',
'''        "ind_etf_share_flow",
        "lu_next_on", "dt_flag_5", "dt_net_5", "dt_net_10",
''')

# gp_search seed partners — remove overnight
s = s.replace(
'''        partner_seed = [x for x in (
            "etf_major_flow", "etf_theme_flow", "etf_all_flow",
            "lu_streak", "lu_height", "lu_next_on",
            "ind_rel_overnight", "ind_rel_intraday",
            "intraday_ret", "amt_cv_20", "neg_amt_cv_20", "on_minus_id",
            "ann_earn_signed_5", "dt_flag_5", "overnight_ret",
        ) if x in leaves]
''',
'''        partner_seed = [x for x in (
            "lu_streak", "lu_height", "lu_next_on", "ld_next_on",
            "ind_rel_overnight", "ind_rel_intraday",
            "unlock_resid",
            "ann_earn_signed_5", "ann_penalty_5", "ann_buyback_5",
            "dt_flag_5", "dt_net_5",
            "rz_intensity", "rzrq_delta_5",
            "ind_etf_share_flow", "ind_etf_x_ind_rel_on", "ind_etf_x_ind_rel_id",
        ) if x in leaves]
''')

# early reject syntax bans in eval_one (in addition to CB/gold)
s = s.replace(
'''            _iso0 = isomorphic_reason(expr_s)
            if _iso0 == "HARD_BAN_CB_GOLD_MAINLINE":
                append_attempt(engine="gp", seed=cfg.seed, universe=cfg.universe, cost=cfg.cost,
                               window=cfg.window, expr_str=expr_s, fitness=None,
                               notes="rejected_cb_gold_mainline", path=cfg.ledger_path)
                return None
''',
'''            _iso0 = isomorphic_reason(expr_s)
            if _iso0 and str(_iso0).startswith(("HARD_BAN_CB_GOLD", "SYNTAX_HARD_BAN")):
                append_attempt(engine="gp", seed=cfg.seed, universe=cfg.universe, cost=cfg.cost,
                               window=cfg.window, expr_str=expr_s, fitness=None,
                               notes=f"rejected_{_iso0.lower()}", path=cfg.ledger_path)
                return None
''')

s = s.replace('log("gp_search_v19 seeded"', 'log("gp_search_v20 TrackA seeded"')
s = s.replace('"ETF share/theme/ind_etf × stock event; HARD BAN CB/gold + ACTIVE N=24; lean")',
              '"unlock/lu/dt/rz/ann/ind_rel only; SYNTAX ban overnight/fsr/ann_insider/idx_w; ACTIVE N=24; lean")')
s = s.replace('log("v19 forced-cross patched', 'log("v20 TrackA forced-cross patched')

# rename env fallbacks in receipts
s = s.replace('QL_V19_AVAILABLE_AT_START_MB', 'QL_V20_AVAILABLE_AT_START_MB')

# policy strings
s = s.replace("v19_etf_newleaf", "v20_dual_track")
s = s.replace("v19 SELF_STOP", "v20 SELF_STOP")
s = s.replace("gp_reopen_hardgate_v19_etf_newleaf", "gp_reopen_hardgate_v20_track_a_stock")
s = s.replace("v19_rho_soft", "v20_rho_soft")
s = s.replace("v19_rho_hard", "v20_rho_hard")
s = s.replace("v19_rho_note", "v20_rho_note")
s = s.replace("v19_forced_leaves", "v20_forced_leaves")
s = s.replace(
    '"stricter vs prior soft0.35/hard0.50; early kill high-corr to ACTIVE primary24"',
    '"v20 looser soft0.35/hard0.50 vs v19 0.28/0.40; TrackA syntax ban overnight/fsr/ann_insider/idx_w"',
)
s = s.replace(
    "v19_etf_newleaf: forced ann×ann/dt×lu/rz-shock/ind_etf×ind_rel; rho_soft=0.28 rho_hard=0.40 (stricter vs 0.35/0.50); ACTIVE N=24; MEM_CAP=2200 no raise",
    "v20_dual TrackA: syntax-ban overnight/fsr/ann_insider/idx_w; rho 0.35/0.50; ACTIVE N=24; then TrackB etf_timing→Beta; MEM_CAP=2200 no raise",
)

# Report title
s = s.replace(
    "# AI 因子 GP 硬闸重开 v19_etf_newleaf（主线：个股残差ε + ETF机制叶 · 禁CB/黄金 · ACTIVE N=24 · 双 ICIR）",
    "# AI 因子 GP 硬闸重开 v20_dual_track（TrackA 个股ε · TrackB ETF timing→Beta · 禁 overnight/fsr/ann_insider/idx_w · ACTIVE N=24）",
)
s = s.replace(
    "- **主线（Leo/New Bot 2026-10-12）：** 个股残差ε + ETF机制叶；**禁CB/黄金**；**强制新叶** ann×ann / dt×lu / rz-shock / ind_etf×ind_rel；**ρ硬=0.40**（严于旧0.50）",
    "- **主线（Leo/New Bot 2026-10-12）：** 双轨 — TrackA 个股ε（语法硬禁 overnight/fsr/ann_insider/idx_w；ρ=0.35/0.50）+ TrackB ETF timing→Beta（不进短名单）；禁CB/黄金",
)
s = s.replace(
    "**SELF_STOP 预搜索残片（v19）**",
    "**SELF_STOP 预搜索残片（v20）**",
)

# Fix source path that got over-replaced
s = s.replace(
    '"source": "gp_reopen_hardgate_v20_track_a_stock"',
    '"source": "gp_reopen_hardgate_v20_dual_track", "track": "A_stock"',
)

# Insert Track B runner before final return — replace the DONE/return block at end of main
marker = '''    REPORT.write_text("\\n".join(lines), encoding="utf-8")
    log("DONE", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))
    return 0 if peak < MEM_CAP_MB else 1
'''
track_b_block = r'''    REPORT.write_text("\n".join(lines), encoding="utf-8")
    (OUT_A / "alpha_handback_package.json").write_text(
        (OUT / "alpha_handback_package.json").read_text(encoding="utf-8"), encoding="utf-8")
    for _fn in ("receipt.json", "summary.json", "gate_ok.json", "demoted.json", "top_k.json", "post_gate_rows.json", "run_meta.json"):
        _src = OUT / _fn
        if _src.exists():
            (OUT_A / _fn).write_text(_src.read_text(encoding="utf-8"), encoding="utf-8")
    track_a_summary = dict(summary)
    track_a_summary["track"] = "A_stock"
    track_a_peak = peak
    log("TrackA DONE", "GATE_OK", len(gate_ok), "evals", res.evaluations, "peak", round(peak))

    # ========== Track B: ETF timing → Beta (sequential; free stock panels first) ==========
    log("TrackB start", "sleeve=etf_timing", "available_mb", round(available_mb(), 1), "pid", os.getpid())
    # Drop heavy stock search panels to free RSS before B
    try:
        del sp, panels, primary_panels, public, gp_label, label_eps, label_y
    except Exception:
        pass
    gc.collect()
    peak_b = mem_mb()
    etf_panels = {}
    # Re-materialize only ETF flow leaves from prior load_meta wiring if still in locals; else light reload
    try:
        V2 = ROOT / "data/v2"
        cal_b = None
        # Build industry-level / broadcast ETF series for timing (NOT stock residual Z)
        # Use by_sw_l1 as cross-section of industries (rows=dates, cols=sw_l1)
        by_sw = V2 / "etf/share_pit/ind_etf_share_flow_by_sw_l1.parquet"
        if by_sw.exists():
            dfb = pd.read_parquet(by_sw)
            # expect trade_date + sw_l1_code + flow
            cols_l = {c.lower(): c for c in dfb.columns}
            td = cols_l.get("trade_date") or "trade_date"
            swc = cols_l.get("sw_l1_code") or cols_l.get("sw_code") or cols_l.get("industry") 
            flowc = None
            for cand in ("flow_est_wan_yuan", "d_share_wan", "share_flow", "flow"):
                if cand in dfb.columns or cand in cols_l:
                    flowc = cand if cand in dfb.columns else cols_l[cand]
                    break
            if flowc is None:
                # pick first numeric non-key
                for c in dfb.columns:
                    if c not in (td, swc) and pd.api.types.is_numeric_dtype(dfb[c]):
                        flowc = c; break
            if td and swc and flowc:
                dfb = dfb.copy()
                dfb["_td"] = dfb[td].astype(str).str.replace("-", "").str[:8]
                dfb["_td"] = pd.to_datetime(dfb["_td"], format="%Y%m%d", errors="coerce")
                dfb = dfb.dropna(subset=["_td", swc])
                dfb = dfb[(dfb["_td"] >= LOOKBACK_START) & (dfb["_td"] <= PANEL_END)]
                piv = dfb.pivot_table(index="_td", columns=swc, values=flowc, aggfunc="sum").sort_index()
                piv = piv.astype("float32")
                etf_panels["ind_etf_share_flow"] = piv
                log("TrackB ind_etf_share_flow panel", piv.shape)
        # major/theme/all share flow as market-broadcast series (1-col) for timing
        for name, path in (
            ("etf_share_chg_major", V2 / "etf/share_pit/etf_share_flow_pit_major.parquet"),
            ("etf_all_flow", V2 / "etf/share_pit/etf_share_flow_pit_all.parquet"),
        ):
            if not path.exists():
                continue
            if mem_mb() > 2000:
                log("TrackB skip", name, "rss", round(mem_mb()))
                break
            raw = pd.read_parquet(path)
            cols_l = {c.lower(): c for c in raw.columns}
            td = cols_l.get("trade_date") or "trade_date"
            flowc = None
            for cand in ("flow_est_wan_yuan", "d_share_wan", "share_chg", "d_share", "flow"):
                if cand in raw.columns:
                    flowc = cand; break
            if flowc is None:
                for c in raw.columns:
                    if c != td and pd.api.types.is_numeric_dtype(raw[c]):
                        flowc = c; break
            if not flowc:
                continue
            raw = raw.copy()
            raw["_td"] = raw[td].astype(str).str.replace("-", "").str[:8]
            raw["_td"] = pd.to_datetime(raw["_td"], format="%Y%m%d", errors="coerce")
            ser = raw.dropna(subset=["_td"]).groupby("_td")[flowc].sum().sort_index()
            ser = ser.loc[(ser.index >= LOOKBACK_START) & (ser.index <= PANEL_END)].astype("float32")
            # broadcast to a 1-column panel for expr engine
            etf_panels[name] = ser.to_frame(name=name)
            log("TrackB", name, etf_panels[name].shape)
        # theme if RSS allows
        thm_path = V2 / "etf/share_pit/etf_share_flow_pit_industry_theme.parquet"
        if thm_path.exists() and mem_mb() < 1950:
            raw = pd.read_parquet(thm_path)
            cols_l = {c.lower(): c for c in raw.columns}
            td = cols_l.get("trade_date") or "trade_date"
            flowc = None
            for cand in ("flow_est_wan_yuan", "d_share_wan", "share_chg", "flow"):
                if cand in raw.columns:
                    flowc = cand; break
            if flowc:
                raw = raw.copy()
                raw["_td"] = raw[td].astype(str).str.replace("-", "").str[:8]
                raw["_td"] = pd.to_datetime(raw["_td"], format="%Y%m%d", errors="coerce")
                ser = raw.dropna(subset=["_td"]).groupby("_td")[flowc].sum().sort_index()
                ser = ser.loc[(ser.index >= LOOKBACK_START) & (ser.index <= PANEL_END)].astype("float32")
                etf_panels["etf_share_chg_theme"] = ser.to_frame(name="etf_share_chg_theme")
                log("TrackB etf_share_chg_theme", etf_panels["etf_share_chg_theme"].shape)
        else:
            log("TrackB theme skipped rss", round(mem_mb()))
    except Exception as _eb:
        log("TrackB panel build FAILED", _eb)
        etf_panels = etf_panels or {}

    b_candidates = []
    b_ledger = OUT_B / "ledger_track_b.jsonl"
    if etf_panels and available_mb() >= SELF_STOP_AVAILABLE_MB and mem_mb() <= SELF_STOP_RSS_STICKY_MB:
        log("gp_search start TrackB", "pid", os.getpid(), "available_mb", round(available_mb(), 1),
            "n_leaves", len(etf_panels), "max_eval", TRACK_B_MAX_EVAL)
        # Align panels to common index/columns (industry cols for ind; 1-col for broadcast)
        # For timing: score each leaf / simple binary vs next-day cross-sectional mean return proxy
        # Use industry panel as primary; broadcasts reindexed to same dates
        base = etf_panels.get("ind_etf_share_flow")
        if base is None:
            base = next(iter(etf_panels.values()))
        common_idx = base.index
        aligned = {}
        for k, v in etf_panels.items():
            if isinstance(v, pd.DataFrame):
                if v.shape[1] == 1 and k != "ind_etf_share_flow":
                    # broadcast series → expand to base columns
                    s1 = v.iloc[:, 0].reindex(common_idx)
                    aligned[k] = pd.DataFrame(
                        np.repeat(s1.to_numpy().reshape(-1, 1), base.shape[1], axis=1),
                        index=common_idx, columns=base.columns, dtype="float32",
                    )
                else:
                    aligned[k] = v.reindex(index=common_idx).astype("float32")
        # label: next-day industry relative — use shift of cross-section z of flow as weak proxy
        # Better: forward return of industry — approximate by -sign flip of lag1 flow mean (diagnostic only)
        # Prefer: if ind_rel panels unavailable, use ts_delta of flow as self-timing diagnostic IC
        y_b = base.shift(-1).astype("float32")  # next-day industry ETF flow as continuation label (timing)
        from quantlab.factors.ops import Expr as _EB, apply_expr as _apply_b
        rng_b = np.random.default_rng(SEED + 17)
        leaf_names_b = [k for k in aligned if aligned[k].notna().to_numpy().sum() > 100]
        wraps = ("ts_mean_5", "ts_mean_10", "ts_mean_20", "ts_std_10", "ts_delta_5", "ts_max_20", "neg", "abs")
        ops_b = ("mul", "sub", "div", "add")
        def _icir_panel(fac, lab):
            # daily CS spearman-ish via corr of flattened finite pairs per day, then IR
            ics = []
            for i in range(len(fac)):
                a = fac.iloc[i].to_numpy(dtype=np.float64)
                b = lab.iloc[i].to_numpy(dtype=np.float64)
                m = np.isfinite(a) & np.isfinite(b)
                if m.sum() < 5:
                    continue
                aa, bb = a[m], b[m]
                if aa.std() < 1e-12 or bb.std() < 1e-12:
                    continue
                ics.append(float(np.corrcoef(aa, bb)[0, 1]))
            if len(ics) < 10:
                return float("nan")
            mu = float(np.nanmean(ics)); sd = float(np.nanstd(ics))
            return mu / sd * math.sqrt(252) if sd > 1e-12 else float("nan")
        def _mk_expr(rng):
            if len(leaf_names_b) < 1:
                return None
            if len(leaf_names_b) == 1 or rng.random() < 0.35:
                a = str(rng.choice(leaf_names_b))
                e = _EB("leaf", a)
                e = _EB("op", str(rng.choice(wraps)), (e,))
                if rng.random() < 0.4:
                    e = _EB("op", str(rng.choice(wraps)), (e,))
                return e
            a, b = [str(x) for x in rng.choice(leaf_names_b, size=2, replace=True)]
            # avoid CB/gold / overnight / idx / fsr / ann_insider by leaf set
            op = str(rng.choice(ops_b, p=[0.3, 0.35, 0.2, 0.15]))
            ea = _EB("op", str(rng.choice(wraps)), (_EB("leaf", a),))
            eb = _EB("op", str(rng.choice(wraps)), (_EB("leaf", b),))
            root = _EB("op", op, (ea, eb))
            if rng.random() < 0.35:
                root = _EB("op", str(rng.choice(("ts_mean_10", "ts_mean_20", "neg", "abs"))), (root,))
            return root
        seen_b = set()
        n_eval_b = 0
        while n_eval_b < TRACK_B_MAX_EVAL:
            if mem_mb() > SELF_STOP_RSS_STICKY_MB or (math.isfinite(available_mb()) and available_mb() < SELF_STOP_AVAILABLE_MB):
                log("TrackB SELF_STOP", "rss", round(mem_mb()), "avail", round(available_mb(), 1), "evals", n_eval_b)
                break
            expr = _mk_expr(rng_b)
            if expr is None:
                break
            es = expr.to_str()
            # syntax bans
            Ls = leaves_in(es)
            if any(x == "overnight_ret" or x.startswith("fsr") or x.startswith("ann_insider") or x.startswith("idx_w") for x in Ls):
                continue
            if any(any(x == s0 or x.startswith(s0) for s0 in CB_GOLD_BANNED_STEMS) for x in Ls):
                continue
            if es in seen_b:
                continue
            seen_b.add(es)
            n_eval_b += 1
            try:
                fac = _apply_b(expr, aligned).astype("float32")
            except Exception as ex:
                with open(b_ledger, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps({"expr": es, "error": type(ex).__name__, "sleeve": "etf_timing"}, ensure_ascii=False) + "\n")
                continue
            icir = _icir_panel(fac, y_b)
            # coverage
            nr = float(np.isfinite(fac.to_numpy()).mean()) if fac.size else 0.0
            row = {
                "expr": es,
                "leaves": sorted(Ls),
                "icir_timing_proxy": icir if isinstance(icir, float) else None,
                "nonempty_rate": nr,
                "sleeve": "etf_timing",
                "for_alpha_shortlist": False,
                "for_beta": True,
                "promotion_approved": False,
                "note": "TrackB ETF timing; label=next-day industry ETF flow continuation (proxy); NOT stock residual Z; hand Beta",
            }
            with open(b_ledger, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(clean(row), ensure_ascii=False) + "\n")
            if isinstance(icir, float) and math.isfinite(icir) and icir > 0 and nr >= 0.08:
                b_candidates.append(row)
            del fac
            if n_eval_b % 20 == 0:
                gc.collect()
                log("TrackB progress", n_eval_b, "/", TRACK_B_MAX_EVAL, "pass", len(b_candidates), "rss", round(mem_mb()))
        b_candidates.sort(key=lambda r: (r.get("icir_timing_proxy") or -1e9), reverse=True)
        peak_b = max(peak_b, mem_mb())
        log("TrackB done", "evals", n_eval_b, "n_pass", len(b_candidates), "peak", round(peak_b))
    else:
        n_eval_b = 0
        log("TrackB SKIPPED", "panels", list(etf_panels.keys()), "rss", round(mem_mb()), "avail", round(available_mb(), 1))

    peak_b = max(peak_b, mem_mb())
    beta_pkg = {
        "sleeve": "etf_timing",
        "for_alpha_shortlist_adjudication": False,
        "for_beta": True,
        "promotion_approved": False,
        "not_strategy_weights": True,
        "pid": os.getpid(),
        "peak_rss_MB": round(peak_b),
        "available_at_start_MB": float(os.environ.get("QL_V20_AVAILABLE_AT_START_MB") or float("nan")),
        "n_evaluations": int(n_eval_b),
        "n_candidates_pass": len(b_candidates),
        "candidates": b_candidates[:20],
        "etf_leaves_wired": sorted(etf_panels.keys()),
        "label": "next_day_ind_etf_flow_continuation_proxy",
        "window": WINDOW,
        "seed": SEED + 17,
        "ban_cb_gold": True,
        "syntax_ban_overnight_fsr_ann_insider_idx_w": True,
        "note": "Hand QuantLab Beta only; do NOT submit to Alpha shortlist",
        "out_dir": str(OUT_B.relative_to(ROOT)),
    }
    OUT_B.mkdir(parents=True, exist_ok=True)
    (OUT_B / "beta_etf_timing_package.json").write_text(
        json.dumps(clean(beta_pkg), indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT_B / "candidates.json").write_text(
        json.dumps(clean(b_candidates), indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT_B / "receipt.json").write_text(json.dumps(clean({
        "track": "B_etf_timing",
        "sleeve": "etf_timing",
        "pid": os.getpid(),
        "peak_rss_MB": round(peak_b),
        "n_evaluations": int(n_eval_b),
        "n_pass": len(b_candidates),
        "etf_leaves": sorted(etf_panels.keys()),
        "for_alpha": False,
        "for_beta": True,
        "promotion_approved": False,
    }), indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT_B / "BETA_NOTE_ZH.md").write_text(
        "# Track B ETF timing（交 Beta，不进 Alpha 短名单）\n\n"
        f"- sleeve=`etf_timing`；evals={n_eval_b}；pass={len(b_candidates)}；peak≈{round(peak_b)}MB\n"
        f"- 叶子：{sorted(etf_panels.keys())}\n"
        "- 标签：次日行业 ETF 份额流延续（诊断代理，非个股残差 Z）\n"
        "- **不交 Alpha 短名单裁决**；promotion_approved=false；不交 Strategy\n"
        f"- 包：`{OUT_B.relative_to(ROOT)}/beta_etf_timing_package.json`\n",
        encoding="utf-8",
    )

    # dual report append
    dual_lines = [
        "",
        "## Track B — ETF timing（交 Beta）",
        "",
        f"- evals={n_eval_b}；pass={len(b_candidates)}；peak_B≈{round(peak_b)}MB；sleeve=etf_timing",
        f"- 包：`{OUT_B.relative_to(ROOT)}/beta_etf_timing_package.json`",
        "",
        "| # | 表达式 | ICIR_timing_proxy | nonempty | leaves |",
        "|---|---|---:|---:|---|",
    ]
    for i, r in enumerate(b_candidates[:10], 1):
        dual_lines.append(
            f"| {i} | `{r['expr']}` | {ff(r.get('icir_timing_proxy'))} | {ff(r.get('nonempty_rate'))} | {','.join(r.get('leaves') or [])} |"
        )
    if not b_candidates:
        dual_lines.append("| — | （本轮无过 timing 代理闸） | — | — | — |")
    dual_lines += [
        "",
        "## 双轨回执",
        f"- TrackA：GATE_OK={track_a_summary.get('n_gate_ok')} evals={track_a_summary.get('evaluations')} peak≈{round(track_a_peak)}MB → Alpha `{OUT_A.relative_to(ROOT)}/alpha_handback_package.json`",
        f"- TrackB：pass={len(b_candidates)} evals={n_eval_b} peak≈{round(peak_b)}MB → Beta `{OUT_B.relative_to(ROOT)}/beta_etf_timing_package.json`",
        "- promotion_approved=false；未开密封；未改短清单；未交 Strategy",
        "",
    ]
    REPORT.write_text(REPORT.read_text(encoding="utf-8") + "\n".join(dual_lines), encoding="utf-8")

    dual_summary = {
        "promotion_approved": False, "sealed": False, "strategy_weights": False,
        "pid": os.getpid(),
        "track_a": track_a_summary,
        "track_b": {
            "sleeve": "etf_timing",
            "n_evaluations": int(n_eval_b),
            "n_pass": len(b_candidates),
            "peak_rss_MB": round(peak_b),
            "out_dir": str(OUT_B.relative_to(ROOT)),
            "top_exprs": [r["expr"] for r in b_candidates[:5]],
        },
        "peak_rss_MB_max": round(max(track_a_peak, peak_b)),
        "out_a": str(OUT_A.relative_to(ROOT)),
        "out_b": str(OUT_B.relative_to(ROOT)),
        "report": str(REPORT.relative_to(ROOT)),
        "policy": "v20_dual sequential A(stock→Alpha) then B(etf_timing→Beta); syntax ban overnight/fsr/ann_insider/idx_w; MEM_CAP=2200 no raise",
    }
    (OUT_A.parent / "gp_reopen_hardgate_v20_dual_summary.json").write_text(
        json.dumps(clean(dual_summary), indent=2, ensure_ascii=False), encoding="utf-8")
    log("DONE dual", dual_summary)
    print(json.dumps(dual_summary, ensure_ascii=False, indent=2, default=str))
    return 0 if max(track_a_peak, peak_b) < MEM_CAP_MB else 1
'''

if marker not in s:
    raise SystemExit("end marker not found")
s = s.replace(marker, track_b_block, 1)

# Fix handback note strings that still say v19
s = s.replace("v19 mainline=ε+ETF mech", "v20 TrackA=ε unlock/dt/rz/ann/ind_rel; syntax-ban overnight/fsr/ann_insider/idx_w")
s = s.replace("note\": \"v19_etf_newleaf; Alpha adjudicates", "note\": \"v20 TrackA; Alpha adjudicates")
s = s.replace("v19_etf_newleaf; Alpha adjudicates; no seal; CB/gold banned",
              "v20 TrackA; Alpha adjudicates; no seal; CB/gold banned; syntax-ban overnight/fsr/ann_insider/idx_w")

# gp_search start log label track
s = s.replace(
'''    log("gp_search start", "N_before", n_before, "n_leaves", len(sp),
        "available_mb", round(_av, 1) if math.isfinite(_av) else None,
        "pid", os.getpid(), "peak_cap", MEM_CAP_MB, "sticky_peak", round(peak))
''',
'''    log("gp_search start TrackA", "N_before", n_before, "n_leaves", len(sp),
        "available_mb", round(_av, 1) if math.isfinite(_av) else None,
        "pid", os.getpid(), "peak_cap", MEM_CAP_MB, "sticky_peak", round(peak),
        "track", "A_stock", "rho", f"{rho_soft}/{rho_hard}")
''')

# When filtering search panels `sp`, ensure only SEARCH_LEAVES / Track A allow
# Find where sp is built — typically from panels keys ∩ SEARCH_LEAVES
# Add a safety filter after leaf selection if present

p.write_text(s, encoding="utf-8")
print("patched", p, "lines", len(s.splitlines()))
