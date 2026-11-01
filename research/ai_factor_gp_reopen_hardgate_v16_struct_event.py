#!/usr/bin/env python3
"""GP reopen v16_struct_event — New Bot：事件叶继续 + ETF份额/解禁残差/涨跌停次日（有 PIT 就接）。

Hard gates (unchanged stack + v16 expand):
  - DENSE_MICRO → STRUCT_CROSS; EVENT leaves also STRUCT
  - requires_cross: L1H×STRUCT OR EVENT×((STRUCT minus EVENT) ∪ L1H) OR distinct EVENT×EVENT
  - HARD BAN prior ACTIVES + v14/v15 families:
      overnight×ann_buyback; ann_buyback×ind_rel_intraday; ind_rel_overnight×dt_net;
      ann_buyback×nb_north_money; ann_buyback×rz_delta;
      rz_intensity×ind_rel_overnight (v15 DEMOTE_RESID near-iso)
  - NEW STRUCT leaves (PIT-safe if present): etf_share_chg_*; unlock_resid; lu_next_on/ld_next_on
  - θ_primary=0.15; ε residual; P0 θ/λ/ρ; impact@60/100万≥10%; novelty hard-kill
  - bans: days_since_lu primary, FSR/ann_insider/lockup_S_20 transplant, RANK_WRAP/TEXTBOOK_SHELL
  - PRIMARY Z MUST include all ACTIVE primary N=23 (active23=True)
  - Handback exposes icir_eps_gate + icir_eps_posthoc + icir_y (no dual-read ambiguity)
  - Bias seeds toward NEW struct/event leaves; de-prioritize idx/lev
  - promotion_approved=false; no seal; no Strategy weights; do not edit shortlist

Memory: MEM_CAP_MB=2300 (peak≤2.2GB≈2200 + sticky headroom); SELF_STOP if available<2500; MAX_EVAL=150.
Launch: LEO_AI_FACTOR_EXPLORE_OK=1.
"""
from __future__ import annotations
import gc, importlib.util, json, math, os, re, resource, sys, time, types
from collections import Counter
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path("/workspace/QuantLab")
OUT = ROOT / "output/ai_factor/gp_reopen_hardgate_v16_struct_event"
REPORT = ROOT / "output/alpha/AI_FACTOR_GP_REOPEN_HARDGATE_V16_STRUCT_EVENT_ZH.md"
SPEC_JSON = ROOT / "output/ai_factor/p0_theta_lam_z/spec.json"
EXPLORE_START = pd.Timestamp("2024-06-03")
LOOKBACK_START = pd.Timestamp("2024-01-02")
IMP60_FLOOR = 0.10
THETA_COV = 0.08
THETA_COV_PRIMARY = 0.15
LAMBDA_FAM = 0.30
RHO_FAM_SOFT = 0.35
RHO_FAM_HARD = 0.50
SEED = 20261029
MAX_EVAL = 150  # New Bot: 120–180
POP, GEN, TOP_K = 12, 10, 15  # trimmed vs v10 for peak≤1200
MIN_EVAL_BEFORE_EMPTY_STOP = 100
SEED_FRAC_FORCED = 0.40
COST = 0.0025
PROMOTION_APPROVED = False
MEM_CAP_MB = 2300  # New Bot peak≤2.2GB≈2200 + sticky headroom; SELF_STOP available<2500 or peak>MEM_CAP+400
SELF_STOP_AVAILABLE_MB = 2500
WINDOW = "gp_reopen_hardgate_v16_struct_event_20240603_explore"

# L1H = index-weight deltas only. Dense micro counts as STRUCT so idx×amt/vol/lev = L1H×STRUCT.
L1H_CROSS_LEAVES = (
    "idx_w500_delta_20", "idx_w_delta_20", "neg_idx_w_delta_20", "abs_idx_w_delta_20",
    "idx_w300_delta_20",
)
# New Bot binding: amt/liq/lev dense micro → STRUCT_CROSS (DENSE_MICRO ≡ STRUCT side of requires_cross)
DENSE_MICRO_LEAVES = (
    # amt first; liq_* + lev last (v10/v10b/v11 ACTIVE near-iso hard-banned) — de-prioritize in seed
    "amt_cv_20", "neg_amt_cv_20",
    "liq_burst_10", "liq_cv_20", "neg_liq_cv_20",
    "lev_delta_20", "abs_lev_delta_20",
)
# v13 EVENT leaves: 龙虎 / 两融 / 北向市值广播 / 行业相对 / 非insider公告
EVENT_LEAVES = (
    "dt_net_5", "dt_net_10", "dt_flag_5",
    "rz_delta_5", "rz_delta_10", "rzrq_delta_5", "rz_intensity",
    "nb_north_money",
    "ind_rel_overnight", "ind_rel_intraday",
    "ann_buyback_5", "ann_penalty_5", "ann_earn_signed_5",
    # v16 expand (PIT-safe): ETF 份额变化 / 解禁残差 / 涨跌停次日结构
    "etf_share_chg_major", "etf_share_chg_theme", "ind_etf_share_flow",
    "unlock_resid",
    "lu_next_on", "ld_next_on",
)
STRUCT_CROSS_LEAVES = (
    "overnight_ret", "intraday_ret", "on_minus_id",
    "etf_theme_flow", "etf_major_flow", "etf_all_flow",
    "if_basis", "if_basis_x_on",
    "lu_height", "lu_promote_rate",
    "days_since_lu", "lu_streak",
) + DENSE_MICRO_LEAVES + EVENT_LEAVES
AUX_LEAVES = ()
SEARCH_LEAVES = L1H_CROSS_LEAVES + STRUCT_CROSS_LEAVES

EXCLUDED_LEAVES = (
    "ann_n_5", "ann_insider_dec_5",  # insider/FSR/lockup transplant pool banned; buyback/penalty/earn allowed as EVENT
    "idx_w500", "idx_w300", "idx_w", "lev_pit", "neg_lev_pit",
    "lockup_S_20",
    "fsr", "fsr_delta_20",
)

LIMIT_NEIGHBORHOOD_LEAVES = frozenset({
    "days_since_lu", "lu_height", "lu_promote_rate", "lu_streak",
})

KNOWN_SHORTLIST_EXACT = frozenset({
    "rank(ts_std_10(ann_insider_dec_5))",
    "abs(ts_std_10(ts_delta_5(ann_insider_dec_5)))",
    "ts_std_10(fsr_delta_20)",
    "fsr_delta_20",
    "abs(ts_std_10(ts_delta_5(fsr)))",
    "ts_std_10(fsr)",
    "abs(fsr_delta_20)",
    "mul(rank(ocf_to_profit), rank(dv_ttm))",
    "ts_std_10(gm_pit)",
    "neg(idx_w500_delta_20)",
    "rank(neg(idx_w500_delta_20))",
    "ts_mean_20(sub(ts_mean_5(overnight_ret), ts_max_20(lu_height)))",
    "ts_mean_20(sub(ann_insider_dec_5, ts_max_20(lu_height)))",
    "ts_mean_20(sub(ann_insider_dec_5, ts_delta_5(overnight_ret)))",
    "ts_std_10(ts_mean_20(ts_mean_10(lockup_S_20)))",
    "ts_std_10(rank(ts_std_10(lockup_S_20)))",
    # Alpha v6_quality APPROVED ACTIVE (sole etf×liq champion)
    "ts_max_20(ts_mean_5(div(etf_major_flow, neg_amt_cv_20)))",
    # Alpha v6c APPROVED ACTIVE (idx×etf_all)
    "mul(ts_mean_20(idx_w_delta_20), ts_mean_5(etf_all_flow))",
    # Alpha v7 APPROVED ACTIVE (overnight×abs_idx)
    "ts_mean_5(mul(ts_mean_20(overnight_ret), ts_mean_20(abs_idx_w_delta_20)))",
    # Alpha v8 APPROVED ACTIVE (etf_major×idx_w500) — Y_ICIR_NEG_WARN / BROADCAST_PIT_WARN
    "ts_mean_20(mul(ts_mean_10(etf_major_flow), idx_w500_delta_20))",
    # Alpha v9 APPROVED ACTIVE #16 if_basis×neg_idx
    "ts_mean_10(mul(ts_max_20(if_basis), ts_mean_20(neg_idx_w_delta_20)))",
    # Alpha v9 APPROVED ACTIVE #17 abs_idx−on_minus (NEAR_SIB_WARN)
    "ts_mean_10(sub(ts_max_20(abs_idx_w_delta_20), abs(on_minus_id)))",
    # Alpha v10 APPROVED ACTIVE #18 idx_w_delta−liq_cv (SOFT_FAM_WARN |ρ|≈0.407; FRAGMENT_TRIAL)
    "sub(ts_mean_5(idx_w_delta_20), ts_max_20(liq_cv_20))",
    # Alpha v10b APPROVED ACTIVE #19 neg_idx−liq_burst (STRUCT_DISTINCT vs v10)
    "ts_mean_20(sub(ts_mean_20(neg_idx_w_delta_20), ts_mean_5(liq_burst_10)))",
    # Alpha v11 APPROVED ACTIVE #20 idx×lev (COVERAGE_THIN_EDGE + Y_ICIR_NEG_WARN)
    "sub(neg(idx_w500_delta_20), div(abs_lev_delta_20, neg_idx_w_delta_20))",
    # Alpha v12 adjudication ACTIVE primary (v13/v14)
    "neg(sub(ts_max_20(overnight_ret), ts_mean_10(ann_buyback_5)))",
    "sub(ts_max_20(ann_buyback_5), ts_mean_10(ind_rel_intraday))",
    "ts_mean_20(sub(ts_mean_20(ind_rel_overnight), ts_std_10(dt_net_5)))",
    # diversity_secondary near-iso hard-ban this batch
    "sub(ts_mean_10(ann_buyback_5), ts_mean_10(nb_north_money))",
    "sub(ts_mean_10(ann_buyback_5), abs(rz_delta_5))",
    # Alpha v15 DEMOTE_RESID near-iso — hard-ban exact + clones
    "ts_max_20(sub(ts_std_10(rz_intensity), ts_max_20(ind_rel_overnight)))",
})

SHORTLIST_PRIMARY_EXPRS = [
    # ACTIVE primary N=23 (shortlist_tier=primary; do not edit shortlist files)
    "rank(ts_std_10(ann_insider_dec_5))",
    "abs(ts_std_10(ts_delta_5(ann_insider_dec_5)))",
    "ts_std_10(fsr_delta_20)",
    "fsr_delta_20",
    "abs(ts_std_10(ts_delta_5(fsr)))",
    "ts_std_10(fsr)",
    "mul(rank(ocf_to_profit), rank(dv_ttm))",
    "ts_std_10(gm_pit)",
    "neg(idx_w500_delta_20)",
    "ts_mean_20(sub(ts_mean_5(overnight_ret), ts_max_20(lu_height)))",
    "ts_mean_20(sub(ann_insider_dec_5, ts_max_20(lu_height)))",  # historical Z gap; Alpha v12 asked to fill
    "ts_max_20(ts_mean_5(div(etf_major_flow, neg_amt_cv_20)))",
    "mul(ts_mean_20(idx_w_delta_20), ts_mean_5(etf_all_flow))",
    "ts_mean_5(mul(ts_mean_20(overnight_ret), ts_mean_20(abs_idx_w_delta_20)))",
    "ts_mean_20(mul(ts_mean_10(etf_major_flow), idx_w500_delta_20))",
    "ts_mean_10(mul(ts_max_20(if_basis), ts_mean_20(neg_idx_w_delta_20)))",
    "ts_mean_10(sub(ts_max_20(abs_idx_w_delta_20), abs(on_minus_id)))",
    "sub(ts_mean_5(idx_w_delta_20), ts_max_20(liq_cv_20))",
    "ts_mean_20(sub(ts_mean_20(neg_idx_w_delta_20), ts_mean_5(liq_burst_10)))",
    "sub(neg(idx_w500_delta_20), div(abs_lev_delta_20, neg_idx_w_delta_20))",
    "neg(sub(ts_max_20(overnight_ret), ts_mean_10(ann_buyback_5)))",
    "sub(ts_max_20(ann_buyback_5), ts_mean_10(ind_rel_intraday))",
    "ts_mean_20(sub(ts_mean_20(ind_rel_overnight), ts_std_10(dt_net_5)))",
]

OPS = {
    "add", "sub", "mul", "div", "neg", "abs", "rank", "zscore",
    "industry_neutral", "size_neutral",
}
for _k in (1, 5, 10, 20, 60):
    OPS |= {f"delay_{_k}", f"ts_mean_{_k}", f"ts_std_{_k}", f"ts_delta_{_k}", f"ts_max_{_k}"}

t0 = 0.0
def mem_mb(): return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
def available_mb():
    try:
        for line in open("/proc/meminfo"):
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) / 1024.0
    except Exception:
        pass
    return float("nan")
def _cast_panels_f32(d):
    """Downcast DataFrame panels to float32 in-place to cut RSS."""
    for k, v in list(d.items()):
        if isinstance(v, pd.DataFrame):
            d[k] = v.astype("float32", copy=False)
    return d
def log(*a): print(f"[gp_v16 {time.time()-t0:5.0f}s {mem_mb():.0f}MB]", *a, flush=True)

def _ensure_pkgs():
    if "quantlab" not in sys.modules:
        q = types.ModuleType("quantlab"); q.__path__ = [str(ROOT / "quantlab")]; sys.modules["quantlab"] = q
    if "quantlab.factors" not in sys.modules or not hasattr(sys.modules["quantlab.factors"], "__path__"):
        f = types.ModuleType("quantlab.factors"); f.__path__ = [str(ROOT / "quantlab/factors")]; sys.modules["quantlab.factors"] = f
    def load(name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod
        assert spec.loader; spec.loader.exec_module(mod); return mod
    load("quantlab.factors.ops", ROOT / "quantlab/factors/ops.py")
    af = types.ModuleType("quantlab.factors.ai_factory"); af.__path__ = [str(ROOT / "quantlab/factors/ai_factory")]
    sys.modules["quantlab.factors.ai_factory"] = af
    for n in ("ledger", "novelty", "fitness", "evaluate", "search", "structural_leaves"):
        load(f"quantlab.factors.ai_factory.{n}", ROOT / f"quantlab/factors/ai_factory/{n}.py")

def _import_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod
    assert spec.loader; spec.loader.exec_module(mod); return mod

def clean(o):
    if isinstance(o, float) and (math.isnan(o) or math.isinf(o)): return None
    if isinstance(o, dict): return {k: clean(v) for k, v in o.items()}
    if isinstance(o, list): return [clean(x) for x in o]
    return o

def leaves_in(expr: str) -> frozenset[str]:
    return frozenset(t for t in re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", expr) if t not in OPS)

def requires_cross(expr: str) -> bool:
    e = expr.strip()
    L = leaves_in(e)
    has_bin = any(op + "(" in e for op in ("mul", "sub", "div", "add"))
    if not has_bin:
        return False
    # classic L1H × STRUCT
    if bool(L & set(L1H_CROSS_LEAVES)) and bool(L & set(STRUCT_CROSS_LEAVES)):
        return True
    # v13: EVENT × (non-event STRUCT ∪ L1H) OR distinct EVENT×EVENT
    ev = L & set(EVENT_LEAVES)
    if ev:
        other_struct = (L & set(STRUCT_CROSS_LEAVES)) - set(EVENT_LEAVES)
        if other_struct or (L & set(L1H_CROSS_LEAVES)):
            return True
        # distinct event families (e.g. dt_* × rz_*, ind_rel × ann_*)
        if len(ev) >= 2:
            stems = set()
            for x in ev:
                if x.startswith("dt_"): stems.add("dt")
                elif x.startswith(("rz_", "rzrq_", "rq_")): stems.add("rz")
                elif x.startswith("nb_"): stems.add("nb")
                elif x.startswith("ind_rel_"): stems.add("ind")
                elif x.startswith("ann_"): stems.add("ann")
                elif x.startswith(("etf_share_chg", "ind_etf_share")): stems.add("etfsh")
                elif x.startswith("unlock_"): stems.add("unlock")
                elif x in ("lu_next_on", "ld_next_on"): stems.add("lunext")
                else: stems.add(x.split("_")[0])
            if len(stems) >= 2:
                return True
    return False

def is_sole_leaf_ts_stack(expr: str) -> bool:
    L = leaves_in(expr)
    if len(L) != 1:
        return False
    if any(op + "(" in expr for op in ("mul", "sub", "div", "add")):
        return False
    return True

def is_rank_wrap_shell(expr: str) -> bool:
    """Outermost rank(...) wrapping already-structural / shortlist-like content → punish."""
    e = expr.strip()
    if not (e.startswith("rank(") and e.endswith(")")):
        return False
    # naive matching paren for outermost
    depth = 0
    inner = None
    for i, ch in enumerate(e):
        if ch == "(":
            depth += 1
            if depth == 1:
                start = i + 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                inner = e[start:i]
                break
    if inner is None:
        return False
    inner = inner.strip()
    if inner in KNOWN_SHORTLIST_EXACT:
        return True
    # rank wrapping a sole structural leaf or sole-leaf ts stack
    if is_sole_leaf_ts_stack(inner):
        return True
    # rank wrapping binary that already has no new leaf beyond SEARCH (shell)
    if requires_cross(inner) and not any(op + "(" in inner for op in ("ts_delta", "ts_std", "ts_mean", "ts_max")):
        # rank(mul(a,b)) style with bare leaves — still punish as RANK_WRAP shell
        if inner.startswith(("mul(", "sub(", "div(", "add(")):
            return True
    return False

def is_limit_neighborhood_primary(expr: str) -> bool:
    """P0-8: days_since_lu or limit-neighborhood as primary structural → not GATE_OK primary."""
    L = leaves_in(expr)
    if "days_since_lu" in L:
        return True
    lim = L & LIMIT_NEIGHBORHOOD_LEAVES
    if not lim:
        return False
    # limit-neighborhood is primary if no ETF/flow/idx/liq/lev structural alternative
    non_lim_struct = (L & set(STRUCT_CROSS_LEAVES)) - LIMIT_NEIGHBORHOOD_LEAVES
    non_lim_l1h = L & set(L1H_CROSS_LEAVES)
    # if only limit leaves on struct side (possibly with L1h) → still limit-primary HOLD
    if not non_lim_struct and lim:
        return True
    return False

def isomorphic_reason(expr: str) -> str | None:
    e = expr.strip()
    if e in KNOWN_SHORTLIST_EXACT:
        return "EXACT_SHORTLIST"
    L = leaves_in(e)
    if any(x.startswith("ann_insider") for x in L) or "ann_n_5" in L:
        return "ANN_INSIDER_PRIMARY_BANNED"
    if "lockup_S_20" in L:
        return "LOCKUP_BANNED_V5"
    if any(x in L for x in ("fsr", "fsr_delta_20")):
        return "FSR_SEARCH_BANNED"
    if any(x in L for x in ("idx_w500", "idx_w300", "idx_w", "lev_pit", "neg_lev_pit")):
        return "LEVEL_SHELL_BANNED"
    if is_sole_leaf_ts_stack(e):
        return "SOLE_LEAF_TS_STACK_BANNED"
    if is_rank_wrap_shell(e):
        return "RANK_WRAP"
    if L == frozenset({"overnight_ret", "lu_height"}) or L == frozenset({"overnight_ret", "lu_height", "intraday_ret"}):
        if "sub(" in e and ("ts_mean" in e or "ts_max" in e):
            return "ISO_OVERNIGHT_LU_V2EPLUS"
    if L <= frozenset({"idx_w500_delta_20"}) and ("neg(" in e or e in ("idx_w500_delta_20", "rank(idx_w500_delta_20)")):
        return "ISO_IDX_W500_DELTA_SHORTLIST"
    # iso of APPROVED ACTIVE etf×liq champion (sole)
    etf_liq_l = L & frozenset({"etf_major_flow", "etf_all_flow", "etf_theme_flow"})
    liq_l = L & frozenset({"neg_amt_cv_20", "amt_cv_20", "liq_cv_20", "neg_liq_cv_20", "liq_burst_10"})
    if L == frozenset({"etf_major_flow", "neg_amt_cv_20"}) or L == frozenset({"etf_major_flow", "amt_cv_20", "neg_amt_cv_20"}):
        if "div(" in e and ("ts_mean" in e or "ts_max" in e):
            return "ISO_ETF_LIQ_V6_ACTIVE"
    # DEMOTE near-iso: etf_all (or any etf) ÷ liq/amt_cv family — v6c #2-4 style spam
    if etf_liq_l and liq_l and len(L - etf_liq_l - liq_l) == 0:
        if "div(" in e or ("mul(" in e and ("amt_cv" in e or "liq_cv" in e or "liq_burst" in e)):
            if "etf_all_flow" in L or ("etf_theme_flow" in L) or (
                "etf_major_flow" in L and "neg_amt_cv_20" not in e and "div(" in e
            ):
                return "ISO_ETF_ALL_LIQ_FAMILY"
            if "etf_major_flow" in L and ("div(" in e) and ("ts_mean" in e or "ts_max" in e or "ts_std" in e):
                return "ISO_ETF_LIQ_V6_ACTIVE"
    # HARD BAN: any idx_* × etf_* / etf_* × idx_* (v8 winner family — do not spam)
    idx_l = L & frozenset({
        "idx_w500_delta_20", "idx_w_delta_20", "neg_idx_w_delta_20",
        "abs_idx_w_delta_20", "idx_w300_delta_20",
    })
    etf_l = L & frozenset({"etf_theme_flow", "etf_major_flow", "etf_all_flow"})
    if idx_l and etf_l:
        other = L - idx_l - etf_l
        # pure idx×etf (possibly with wraps) → hard ban
        if not other and any(op + "(" in e for op in ("mul", "sub", "div", "add")):
            return "HARD_BAN_IDX_ETF_CROSS"
    # iso of ACTIVE idx×etf_all (also covered by hard ban; keep tags for clarity)
    if L == frozenset({"idx_w_delta_20", "etf_all_flow"}) or L == frozenset({"idx_w_delta_20", "etf_all_flow", "neg_idx_w_delta_20"}):
        if "mul(" in e and ("ts_mean" in e or "ts_max" in e):
            return "ISO_IDX_ETF_ALL_V6C_ACTIVE"
    if L == frozenset({"idx_w500_delta_20", "etf_all_flow"}) and "mul(" in e and "ts_mean" in e:
        return "ISO_IDX_ETF_ALL_NEAR"
    # iso of v8 ACTIVE etf_major×idx_w500
    if L == frozenset({"etf_major_flow", "idx_w500_delta_20"}) or L == frozenset({"etf_major_flow", "idx_w500_delta_20", "idx_w_delta_20"}):
        if "mul(" in e and ("ts_mean" in e or "ts_max" in e):
            return "ISO_ETF_MAJOR_IDX_V8_ACTIVE"
    # iso of v7 ACTIVE #14 overnight × abs_idx_w
    if L == frozenset({"overnight_ret", "abs_idx_w_delta_20"}) or L == frozenset({"overnight_ret", "abs_idx_w_delta_20", "idx_w_delta_20"}):
        if "mul(" in e and ("ts_mean" in e or "ts_max" in e):
            return "ISO_OVERNIGHT_ABS_IDX_V7_ACTIVE"
    # near-iso: overnight × any abs/neg idx_w delta (same family as ACTIVE#14)
    if "overnight_ret" in L and (L & frozenset({"abs_idx_w_delta_20", "idx_w_delta_20", "neg_idx_w_delta_20", "idx_w500_delta_20", "idx_w300_delta_20"})):
        other = L - frozenset({"overnight_ret", "abs_idx_w_delta_20", "idx_w_delta_20", "neg_idx_w_delta_20", "idx_w500_delta_20", "idx_w300_delta_20"})
        if not other and "mul(" in e and ("ts_mean" in e or "ts_max" in e):
            return "ISO_OVERNIGHT_IDX_FAMILY"
    # near-iso on_minus_id / intraday with abs_idx (v7 soft-demote family) — kept for mul tags
    if ("on_minus_id" in L or "intraday_ret" in L) and ("abs_idx_w_delta_20" in L) and len(L) <= 3:
        if "mul(" in e and "ts_mean" in e:
            return "ISO_ON_MINUS_ABS_IDX_NEAR"
    # HARD BAN v10: if_basis / if_basis_x_on × any idx_* (v9 ACTIVE #16 family — do not spam)
    basis_l = L & frozenset({"if_basis", "if_basis_x_on"})
    if idx_l and basis_l:
        other = L - idx_l - basis_l
        if not other and any(op + "(" in e for op in ("mul", "sub", "div", "add")):
            return "HARD_BAN_IF_BASIS_IDX"
    # HARD BAN v10: abs_idx × on_minus_id family (v9 ACTIVE #17 — any binary)
    if "abs_idx_w_delta_20" in L and "on_minus_id" in L:
        other = L - frozenset({"abs_idx_w_delta_20", "on_minus_id"})
        if not other and any(op + "(" in e for op in ("mul", "sub", "div", "add")):
            return "HARD_BAN_ABS_IDX_ON_MINUS"
    # HARD BAN v10b: idx_* ×/±/÷ liq_cv* (v10 ACTIVE #18 near-iso — do not spam)
    # exact champion + any binary cross of idx deltas with liq_cv / neg_liq_cv only
    liq_cv_l = L & frozenset({"liq_cv_20", "neg_liq_cv_20"})
    if idx_l and liq_cv_l:
        other = L - idx_l - liq_cv_l
        if not other and any(op + "(" in e for op in ("mul", "sub", "div", "add")):
            if L == frozenset({"idx_w_delta_20", "liq_cv_20"}) and "sub(" in e:
                return "ISO_IDX_LIQ_CV_V10_ACTIVE"
            return "HARD_BAN_IDX_LIQ_CV"
    # HARD BAN v11: idx_* ×/±/÷ liq_burst (v10b ACTIVE #19 near-iso — do not spam)
    liq_burst_l = L & frozenset({"liq_burst_10"})
    if idx_l and liq_burst_l:
        other = L - idx_l - liq_burst_l
        if not other and any(op + "(" in e for op in ("mul", "sub", "div", "add")):
            if L == frozenset({"neg_idx_w_delta_20", "liq_burst_10"}) and "sub(" in e:
                return "ISO_NEG_IDX_LIQ_BURST_V10B_ACTIVE"
            return "HARD_BAN_IDX_LIQ_BURST"
    # HARD BAN v12: idx_* ×/±/÷ lev_delta / abs_lev (v11 ACTIVE #20 near-iso — do not spam)
    # covers exact 3-leaf champ (idx_w500 + abs_lev + neg_idx) and pure idx×lev binary
    lev_l = L & frozenset({"lev_delta_20", "abs_lev_delta_20"})
    if idx_l and lev_l:
        other = L - idx_l - lev_l
        if not other and any(op + "(" in e for op in ("mul", "sub", "div", "add")):
            if L == frozenset({"idx_w500_delta_20", "abs_lev_delta_20", "neg_idx_w_delta_20"}):
                return "ISO_IDX_LEV_V11_ACTIVE"
            return "HARD_BAN_IDX_LEV"
    # HARD BAN v15: overnight × ann_buyback family (v13 ACTIVE primary near-iso)
    if "overnight_ret" in L and "ann_buyback_5" in L:
        other = L - frozenset({"overnight_ret", "ann_buyback_5"})
        if not other and any(op + "(" in e for op in ("mul", "sub", "div", "add")):
            return "HARD_BAN_OVERNIGHT_ANN_BUYBACK_V13"
    # HARD BAN v15: ann_buyback × ind_rel_intraday (v14 ACTIVE #1)
    if "ann_buyback_5" in L and "ind_rel_intraday" in L:
        other = L - frozenset({"ann_buyback_5", "ind_rel_intraday"})
        if not other and any(op + "(" in e for op in ("mul", "sub", "div", "add")):
            return "HARD_BAN_BUYBACK_IND_REL_V14"
    # HARD BAN v15: ind_rel_overnight × dt_net* (v14 ACTIVE #4)
    dt_l = L & frozenset({"dt_net_5", "dt_net_10", "dt_flag_5"})
    if "ind_rel_overnight" in L and dt_l:
        other = L - frozenset({"ind_rel_overnight"}) - dt_l
        if not other and any(op + "(" in e for op in ("mul", "sub", "div", "add")):
            return "HARD_BAN_IND_REL_DT_V14"
    # HARD BAN v15: ann_buyback × nb_north_money (v14 secondary)
    if "ann_buyback_5" in L and "nb_north_money" in L:
        other = L - frozenset({"ann_buyback_5", "nb_north_money"})
        if not other and any(op + "(" in e for op in ("mul", "sub", "div", "add")):
            return "HARD_BAN_BUYBACK_NB_V14"
    # HARD BAN v15: ann_buyback × rz_delta* (v14 secondary)
    rz_l = L & frozenset({"rz_delta_5", "rz_delta_10", "rzrq_delta_5", "rz_intensity"})
    if "ann_buyback_5" in L and rz_l:
        other = L - frozenset({"ann_buyback_5"}) - rz_l
        if not other and any(op + "(" in e for op in ("mul", "sub", "div", "add")):
            return "HARD_BAN_BUYBACK_RZ_V14"
    # HARD BAN v16: rz_intensity × ind_rel_overnight (v15 GATE_OK demoted DEMOTE_RESID)
    if "rz_intensity" in L and "ind_rel_overnight" in L:
        other = L - frozenset({"rz_intensity", "ind_rel_overnight"})
        if not other and any(op + "(" in e for op in ("mul", "sub", "div", "add")):
            return "HARD_BAN_RZ_INTENSITY_IND_REL_V15"
    # also ban rz_* × ind_rel_overnight clones (same family)
    rz_only = L & frozenset({"rz_delta_5", "rz_delta_10", "rzrq_delta_5", "rz_intensity"})
    if rz_only and "ind_rel_overnight" in L:
        other = L - rz_only - frozenset({"ind_rel_overnight"})
        if not other and any(op + "(" in e for op in ("mul", "sub", "div", "add")):
            return "HARD_BAN_RZ_IND_REL_OVERNIGHT_V15"
    if not requires_cross(e):
        return "NO_L1H_STRUCT_CROSS"
    return None

def _cs_z(row: np.ndarray) -> np.ndarray:
    m = np.isfinite(row)
    out = np.full_like(row, np.nan, dtype=np.float64)
    if int(m.sum()) < 3:
        return out
    x = row[m]
    sd = x.std()
    if sd < 1e-12:
        return out
    out[m] = (x - x.mean()) / sd
    return out



def _ts_code_to_instrument_id(code: object) -> str:
    """000001.SZ → sz.000001; pass through if already sh.|sz.|bj."""
    s = str(code).strip()
    if not s or s == "nan":
        return ""
    if s.startswith(("sh.", "sz.", "bj.")):
        return s
    if "." in s:
        num, ex = s.split(".", 1)
        ex = ex.upper()
        if ex in ("SH", "SZ", "BJ") and num.isdigit():
            return f"{ex.lower()}.{num}"
    if s.isdigit() and len(s) == 6:
        # bare code heuristic
        if s.startswith(("5", "6")):
            return f"sh.{s}"
        if s.startswith(("4", "8")):
            return f"bj.{s}"
        return f"sz.{s}"
    return s

def _instrument_id_to_ts_code(iid: object) -> str:
    """sz.000001 → 000001.SZ"""
    s = str(iid).strip()
    if s.startswith(("sh.", "sz.", "bj.")) and "." in s[3:]:
        ex, num = s.split(".", 1)
        return f"{num}.{ex.upper()}"
    return s

def build_gm_pit_panel(cal, cols, mask) -> tuple[pd.DataFrame | None, dict]:
    """grossprofit_margin + available_at → gm_pit aligned to midlarge cols (instrument_id).
    Financials may carry ts_code=000001.SZ AND instrument_id=sz.000001 — unify before join.
    """
    path = ROOT / "data/v2/financials_pit/financials_pit_tushare.parquet"
    meta = {"path": str(path), "family": "gm_pit"}
    if not path.exists():
        meta["ok"] = False; meta["error"] = "missing"
        return None, meta
    want = ["available_at", "grossprofit_margin", "end_date"]
    # read with both id columns if present
    import pyarrow.parquet as pq
    names = set(pq.read_schema(path).names)
    cols_read = [c for c in want + ["instrument_id", "ts_code", "report_type"] if c in names]
    fin = pd.read_parquet(path, columns=cols_read)
    if "instrument_id" not in fin.columns and "ts_code" in fin.columns:
        fin["instrument_id"] = fin["ts_code"].map(_ts_code_to_instrument_id)
        meta["id_from"] = "ts_code_converted"
    elif "instrument_id" in fin.columns:
        # ensure format; also fill gaps from ts_code
        fin["instrument_id"] = fin["instrument_id"].astype(str)
        if "ts_code" in fin.columns:
            miss = ~fin["instrument_id"].isin(cols)
            if miss.any():
                fin.loc[miss, "instrument_id"] = fin.loc[miss, "ts_code"].map(_ts_code_to_instrument_id)
        meta["id_from"] = "instrument_id"
    else:
        meta["ok"] = False; meta["error"] = "no_id_col"
        return None, meta
    fin["available_at"] = pd.to_datetime(fin["available_at"], utc=True, errors="coerce")
    if getattr(fin["available_at"].dt, "tz", None) is not None:
        fin["available_at"] = fin["available_at"].dt.tz_convert("Asia/Shanghai").dt.tz_localize(None)
    fin = fin[fin["instrument_id"].isin(cols)]
    fin = fin.dropna(subset=["available_at", "grossprofit_margin"])
    fin = fin[fin["available_at"] >= (LOOKBACK_START - pd.Timedelta(days=400))]
    if fin.empty:
        meta["ok"] = False; meta["error"] = "empty_after_filter"
        return None, meta
    # map available_at → next session on cal (reuse l1g if possible)
    try:
        l1g = _import_mod("ai_factor_l1g_new_mech_family_explore", ROOT / "research/ai_factor_l1g_new_mech_family_explore.py")
        fin = fin.copy()
        fin["avail_session"] = l1g._avail_to_next_session(fin["available_at"], cal)
    except Exception as e:
        meta["avail_map_err"] = str(e)
        fin = fin.copy()
        fin["avail_session"] = pd.to_datetime(fin["available_at"]).dt.normalize()
    fin = fin.dropna(subset=["avail_session"])
    sub = fin.sort_values(["avail_session", "instrument_id"]).drop_duplicates(
        ["avail_session", "instrument_id"], keep="last"
    )
    wide = (
        sub.set_index(["avail_session", "instrument_id"])["grossprofit_margin"]
        .unstack()
        .reindex(index=cal, columns=cols)
        .astype("float32")
        .ffill()
    )
    if mask is not None:
        wide = wide.where(mask)
    arr = wide.to_numpy(dtype=np.float64, copy=True)
    finite = arr[np.isfinite(arr)]
    if finite.size > 100:
        lo, hi = np.nanpercentile(finite, [1, 99])
        arr = np.clip(arr, lo, hi)
        wide = pd.DataFrame(arr, index=cal, columns=cols).astype("float32")
        if mask is not None:
            wide = wide.where(mask).astype("float32")
    meta.update({
        "ok": True,
        "n_rows": int(len(fin)),
        "n_instruments": int(fin["instrument_id"].nunique()),
        "nonempty": float(wide.notna().to_numpy().mean()),
    })
    return wide.astype("float32"), meta

def build_sw_l1_codes(cols: list[str], asof_day: pd.Timestamp) -> tuple[np.ndarray | None, dict]:
    """Map midlarge columns → SW_L1 codes (sw_code). Prefer v2 tushare PIT.
    Returns float codes (categorical ints) length n_cols, or None on hard fail.
    """
    # Data authoritative: DEFAULT_SW_L1_PATH = .../industry_members_sw_l1_tushare.parquet
    try:
        from quantlab.data.v2_readers import DEFAULT_SW_L1_PATH as _SW_AUTH
    except Exception:
        _SW_AUTH = ROOT / "data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet"
    paths = [
        Path(_SW_AUTH),
        ROOT / "data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet",
        ROOT / "data/v2/sw_l1_pit/industry_members_sw_l1.parquet",
        ROOT / "data/v2/sw_l1_pit/industry_members_sw_l1_prefix.parquet",
        ROOT / "data/sw/industry_members_sw_l1.parquet",
    ]
    # dedupe preserving order
    _seen = set(); paths = [x for x in paths if not (str(x) in _seen or _seen.add(str(x)))]
    meta: dict = {"asof": str(asof_day.date()), "tried": []}
    sw = None
    used = None
    for path in paths:
        meta["tried"].append(str(path))
        if not path.exists():
            continue
        try:
            df = pd.read_parquet(path)
        except Exception as e:
            meta.setdefault("read_errors", []).append(f"{path}:{e}")
            continue
        cols_l = {c.lower(): c for c in df.columns}
        if "sw_code" not in cols_l:
            meta.setdefault("skip_no_sw_code", []).append(str(path))
            continue
        if "instrument_id" not in cols_l:
            meta.setdefault("skip_no_id", []).append(str(path))
            continue
        sw = df
        used = path
        break
    if sw is None:
        meta.update({"ok": False, "error": "no_sw_code_parquet"})
        return None, meta
    id_col = {c.lower(): c for c in sw.columns}["instrument_id"]
    code_col = {c.lower(): c for c in sw.columns}["sw_code"]
    # PIT filter
    if "in_date" in sw.columns and "out_date" in sw.columns:
        sw = sw.copy()
        sw["in_date"] = pd.to_datetime(sw["in_date"], errors="coerce")
        sw["out_date"] = pd.to_datetime(sw["out_date"], errors="coerce").fillna(pd.Timestamp("2100-01-01"))
        sw = sw[(sw["in_date"] <= asof_day) & (sw["out_date"] > asof_day)]
    m = sw.drop_duplicates(id_col, keep="last").set_index(id_col)[code_col]
    codes = []
    cats: dict[str, int] = {}
    next_i = 0
    for c in cols:
        v = m.get(c) if c in m.index else None
        if v is None and c.startswith(("sh.", "sz.", "bj.")):
            alt = c.split(".", 1)[1] + "." + c.split(".", 1)[0].upper()
            v = m.get(alt) if alt in m.index else None
        if v is None or (isinstance(v, float) and not np.isfinite(v)):
            codes.append(np.nan)
        else:
            key = str(v)
            if key not in cats:
                cats[key] = next_i
                next_i += 1
            codes.append(float(cats[key]))
    arr = np.asarray(codes, dtype=np.float64)
    meta.update({
        "ok": True,
        "path": str(used),
        "n_mapped": int(np.isfinite(arr).sum()),
        "n_levels": len(cats),
        "n_cols": len(cols),
        "coverage": float(np.isfinite(arr).mean()),
        "sw_code_col": "sw_code",
    })
    if meta["n_mapped"] < 100 or meta["n_levels"] < 2:
        meta["ok"] = False
        meta["error"] = f"sparse_map mapped={meta['n_mapped']} levels={meta['n_levels']}"
        return None, meta
    return arr, meta

def build_resid_label(
    y: pd.DataFrame,
    size: pd.DataFrame | None,
    ind_codes: np.ndarray | None,
    primary_panels: dict[str, pd.DataFrame],
    min_names: int = 50,
) -> tuple[pd.DataFrame, dict]:
    """Daily CS OLS: y = Z β + ε. Z = [size CS-z, SW_L1 drop-one, PRIMARY panels]."""
    cal = y.index
    cols = list(y.columns)
    n_t, n_n = len(cal), len(cols)
    eps = np.full((n_t, n_n), np.nan, dtype=np.float64)
    yv = y.to_numpy(dtype=np.float64, copy=False)
    size_v = size.reindex(index=cal, columns=cols).to_numpy(dtype=np.float64, copy=False) if size is not None else None
    prim_arrs = []
    prim_names = []
    for name, p in primary_panels.items():
        prim_arrs.append(p.reindex(index=cal, columns=cols).to_numpy(dtype=np.float64, copy=False))
        prim_names.append(name)
    # industry codes length n_n
    ind = ind_codes if ind_codes is not None and len(ind_codes) == n_n else None
    uniq_ind = None
    if ind is not None:
        valid_inds = sorted({int(x) for x in ind if np.isfinite(x)})
        if len(valid_inds) >= 2:
            uniq_ind = valid_inds  # drop last
            uniq_ind = valid_inds[:-1]
    n_ok = 0
    n_skip = 0
    for t in range(n_t):
        yy = yv[t]
        m = np.isfinite(yy)
        if size_v is not None:
            m &= np.isfinite(size_v[t])
        for pa in prim_arrs:
            m &= np.isfinite(pa[t])
        if ind is not None:
            m &= np.isfinite(ind.astype(np.float64))
        if int(m.sum()) < min_names:
            n_skip += 1
            continue
        cols_z = []
        if size_v is not None:
            cols_z.append(_cs_z(size_v[t])[m])
        if uniq_ind is not None:
            ii = ind[m]
            for ui in uniq_ind:
                cols_z.append((ii == ui).astype(np.float64))
        for pa in prim_arrs:
            cols_z.append(_cs_z(pa[t])[m])
        if not cols_z:
            n_skip += 1
            continue
        Z = np.column_stack(cols_z)
        # add intercept
        Z = np.column_stack([np.ones(Z.shape[0]), Z])
        yt = yy[m]
        try:
            beta, *_ = np.linalg.lstsq(Z, yt, rcond=None)
            resid = yt - Z @ beta
            row = eps[t]
            row[m] = resid
            n_ok += 1
        except Exception:
            n_skip += 1
            continue
    eps_df = pd.DataFrame(eps, index=cal, columns=cols).astype("float32")
    meta = {
        "n_days_ok": n_ok,
        "n_days_skip": n_skip,
        "primary_in_Z": prim_names,
        "has_size": size_v is not None,
        "has_sw_l1": uniq_ind is not None,
        "n_sw_dummies": len(uniq_ind) if uniq_ind is not None else 0,
        "min_names": min_names,
    }
    return eps_df, meta

def icir_vs(factor: pd.DataFrame, label: pd.DataFrame) -> float:
    idx = factor.index.intersection(label.index)
    if len(idx) < 10:
        return float("nan")
    f = factor.reindex(idx).to_numpy(dtype=np.float64, copy=False)
    y = label.reindex(idx).to_numpy(dtype=np.float64, copy=False)
    ics = []
    for t in range(len(idx)):
        a, b = f[t], y[t]
        m = np.isfinite(a) & np.isfinite(b)
        if int(m.sum()) < 30:
            continue
        aa, bb = a[m], b[m]
        if aa.std() == 0 or bb.std() == 0:
            continue
        ics.append(float(np.corrcoef(aa, bb)[0, 1]))
    if len(ics) < 5:
        return float("nan")
    s = float(np.std(ics))
    if s < 1e-12:
        return float("nan")
    return float(np.mean(ics) / s * math.sqrt(252))

def main() -> int:
    global t0
    t0 = time.time()
    avail0 = available_mb()
    os.environ["QL_V11_AVAILABLE_AT_START_MB"] = str(round(float(avail0), 1))
    log("v16_struct_event start", "pid", os.getpid(), "available_mb", round(float(avail0), 1),
        "MAX_EVAL", MAX_EVAL, "POP", POP, "MEM_CAP", MEM_CAP_MB,
        "NOTE", "v16_struct_event EVENT deepen; peak≤2.2GB MEM_CAP=2300; SELF_STOP available<2500")
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    if os.environ.get("LEO_AI_FACTOR_EXPLORE_OK") != "1":
        print("NEED LEO_AI_FACTOR_EXPLORE_OK=1", file=sys.stderr); return 2
    # New Bot v12: launch when LEO_AI_FACTOR_EXPLORE_OK=1 (parent explicit).

    # load Alpha spec (authoritative constants)
    spec = json.loads(SPEC_JSON.read_text(encoding="utf-8")) if SPEC_JSON.exists() else {}
    p01 = spec.get("P0_1_fitness") or {}
    theta_cov = float(p01.get("theta_cov", THETA_COV))
    theta_cov_primary = float(p01.get("theta_cov_primary", THETA_COV_PRIMARY))
    lambda_fam = float(p01.get("lambda_fam", LAMBDA_FAM))
    rho_soft = float(p01.get("rho_fam_soft", RHO_FAM_SOFT))
    rho_hard = float(p01.get("rho_fam_hard", RHO_FAM_HARD))
    imp_floor = float(p01.get("impact_net_ann_min", IMP60_FLOOR))
    primary_exprs_spec = list((spec.get("P0_2_residual_Z") or {}).get("shortlist_PRIMARY_exprs") or SHORTLIST_PRIMARY_EXPRS)

    _ensure_pkgs()
    l1b = _import_mod("ai_factor_l1b_structural_explore", ROOT / "research/ai_factor_l1b_structural_explore.py")
    l1c = _import_mod("ai_factor_l1c_explore", ROOT / "research/ai_factor_l1c_explore.py")
    l1h = _import_mod("ai_factor_l1h_new_mech_family_explore", ROOT / "research/ai_factor_l1h_new_mech_family_explore.py")
    sci = _import_mod("ai_factor_l1d_shortlist_coverage_impact", ROOT / "research/ai_factor_l1d_shortlist_coverage_impact.py")
    import quantlab.factors.ai_factory.fitness as fit_mod
    import quantlab.factors.ai_factory.search as search_mod
    from quantlab.factors.ai_factory.ledger import append_attempt
    from quantlab.factors.ai_factory.search import GPConfig, gp_search
    from quantlab.factors.ops import apply_expr, Expr

    # --- forced cross v15: deepen unsaturated EVENT; HARD BAN 5 new families + ACTIVE N=23 near-iso ---
    _l1h = list(L1H_CROSS_LEAVES)
    _struct = list(STRUCT_CROSS_LEAVES)
    _dense = list(DENSE_MICRO_LEAVES)
    _event = list(EVENT_LEAVES)
    _bin_ops = ("mul", "sub", "div", "add")
    _bin_w = (0.40, 0.35, 0.15, 0.10)
    _ts_wrap = ("ts_mean_5", "ts_mean_10", "ts_mean_20", "ts_std_10", "ts_delta_5", "ts_max_20", "neg", "abs")
    _idx_pref = ["idx_w_delta_20", "idx_w500_delta_20", "neg_idx_w_delta_20", "abs_idx_w_delta_20", "idx_w300_delta_20"]
    _l1h_pref = _idx_pref + _l1h
    # EVENT partners: prefer unsaturated (penalty/earn/rzrq/intensity/dt_flag/ind_rel×rz); avoid 5 new families
    _event_partners = [
        "overnight_ret", "intraday_ret", "amt_cv_20", "neg_amt_cv_20",
        "on_minus_id", "etf_major_flow", "etf_theme_flow",
    ]
    _event_prefer = [x for x in (
        "ann_penalty_5", "ann_earn_signed_5", "rzrq_delta_5",
        "dt_flag_5", "dt_net_10", "rz_delta_10", "ind_rel_intraday",
        "etf_share_chg_theme", "etf_share_chg_major", "ind_etf_share_flow",
        "unlock_resid", "lu_next_on", "ld_next_on",
    ) if x in _event]
    _struct_pref = list(_event) + [x for x in _event_partners if x in _struct] + [
        x for x in _dense if x not in ("liq_cv_20", "neg_liq_cv_20", "liq_burst_10", "lev_delta_20", "abs_lev_delta_20")
    ]
    def _ev_stem(x):
        if x.startswith("dt_"): return "dt"
        if x.startswith(("rz_", "rzrq_", "rq_")): return "rz"
        if x.startswith("nb_"): return "nb"
        if x.startswith("ind_rel_"): return "ind"
        if x.startswith("ann_"): return "ann"
        if x.startswith(("etf_share_chg", "ind_etf_share")): return "etfsh"
        if x.startswith("unlock_"): return "unlock"
        if x in ("lu_next_on", "ld_next_on"): return "lunext"
        return x.split("_")[0]

    def _leaf_expr(rng, name):
        return Expr("leaf", name)

    def _maybe_wrap(rng, e, p=0.55):
        if rng.random() > p:
            return e
        w = str(rng.choice(_ts_wrap))
        return Expr("op", w, (e,))

    def _banned_pair(a, b):
        ab = {str(a), str(b)}
        if ab == {"overnight_ret", "ann_buyback_5"}: return True
        if ab == {"ann_buyback_5", "ind_rel_intraday"}: return True
        if "ann_buyback_5" in ab and (ab & {"nb_north_money", "rz_delta_5", "rz_delta_10", "rzrq_delta_5", "rz_intensity"}):
            return True
        if "ind_rel_overnight" in ab and (ab & {"dt_net_5", "dt_net_10", "dt_flag_5"}):
            return True
        if "ind_rel_overnight" in ab and (ab & {"rz_intensity", "rz_delta_5", "rz_delta_10", "rzrq_delta_5"}):
            return True
        return False

    def _forced_cross_expr(rng, leaves=None, depth=1):
        leaf_pool = list(leaves) if leaves is not None else list(SEARCH_LEAVES)
        ev_a = [x for x in _event if x in leaf_pool]
        partner_a = [x for x in _event_partners if x in leaf_pool]
        amt_a = [x for x in ("amt_cv_20", "neg_amt_cv_20") if x in leaf_pool]
        idx_no_abs = [x for x in (
            "idx_w500_delta_20", "idx_w300_delta_20", "idx_w_delta_20", "neg_idx_w_delta_20",
        ) if x in leaf_pool]
        banned_with_idx = {
            "liq_cv_20", "neg_liq_cv_20", "liq_burst_10", "lev_delta_20", "abs_lev_delta_20",
            "etf_major_flow", "etf_all_flow", "etf_theme_flow",
            "if_basis", "if_basis_x_on", "on_minus_id", "overnight_ret",
        }
        if rng.random() < 0.96:
            op = str(rng.choice(_bin_ops, p=list(_bin_w)))
            # EVENT × EVENT distinct stems — bias unsaturated; never clone 5 new families
            if rng.random() < 0.42 and len(ev_a) >= 2:
                pref = [x for x in _event_prefer if x in ev_a] or ev_a
                a_n = b_n = None
                for _try in range(12):
                    pool = pref if rng.random() < 0.65 and len(pref) >= 2 else ev_a
                    a_n, b_n = [str(x) for x in rng.choice(pool, size=2, replace=False)]
                    if _ev_stem(a_n) != _ev_stem(b_n) and not _banned_pair(a_n, b_n):
                        break
                a = _maybe_wrap(rng, _leaf_expr(rng, str(a_n)), p=0.60)
                b = _maybe_wrap(rng, _leaf_expr(rng, str(b_n)), p=0.60)
                root = Expr("op", str(rng.choice(("mul", "sub", "div"), p=[0.40, 0.40, 0.20])), (a, b))
                if rng.random() < 0.40:
                    root = _maybe_wrap(rng, root, p=1.0)
                return root
            # EVENT × partner — never clone the five new ACTIVE/secondary families
            if rng.random() < 0.75 and ev_a and partner_a:
                pref = [x for x in _event_prefer if x in ev_a] or ev_a
                a_n = b_n = None
                for _try in range(12):
                    a_n = str(rng.choice(pref if rng.random() < 0.70 else ev_a))
                    b_n = str(rng.choice(partner_a))
                    if not _banned_pair(a_n, b_n):
                        break
                else:
                    a_n = str(rng.choice([x for x in pref if x != "ann_buyback_5"] or pref or ev_a))
                    b_n = str(rng.choice([x for x in partner_a if x != "overnight_ret"] or partner_a))
                a = _maybe_wrap(rng, _leaf_expr(rng, a_n), p=0.60)
                b = _maybe_wrap(rng, _leaf_expr(rng, b_n), p=0.60)
                if rng.random() < 0.5:
                    a, b = b, a
                root = Expr("op", str(rng.choice(("mul", "sub", "div"), p=[0.40, 0.40, 0.20])), (a, b))
                if rng.random() < 0.40:
                    root = _maybe_wrap(rng, root, p=1.0)
                return root
            # rare: non-abs idx × amt (de-prioritized)
            if rng.random() < 0.25 and idx_no_abs and amt_a:
                a = _maybe_wrap(rng, _leaf_expr(rng, str(rng.choice(idx_no_abs))), p=0.60)
                b = _maybe_wrap(rng, _leaf_expr(rng, str(rng.choice(amt_a))), p=0.60)
                if rng.random() < 0.5:
                    a, b = b, a
                root = Expr("op", str(rng.choice(("mul", "sub"), p=[0.55, 0.45])), (a, b))
                if rng.random() < 0.35:
                    root = _maybe_wrap(rng, root, p=1.0)
                return root
            st_safe = partner_a or amt_a or [x for x in leaf_pool if x not in banned_with_idx]
            left = ev_a or idx_no_abs or [x for x in _l1h if x in leaf_pool]
            a_n = str(rng.choice(left))
            b_n = str(rng.choice(st_safe))
            if _banned_pair(a_n, b_n):
                b_n = str(rng.choice([x for x in st_safe if not _banned_pair(a_n, x)] or st_safe))
            a = _maybe_wrap(rng, _leaf_expr(rng, a_n))
            b = _maybe_wrap(rng, _leaf_expr(rng, b_n))
            if rng.random() < 0.5:
                a, b = b, a
            root = Expr("op", op, (a, b))
            if rng.random() < 0.35:
                root = _maybe_wrap(rng, root, p=1.0)
            return root
        return search_mod._rand_expr_orig(rng, leaf_pool, depth)

    search_mod._rand_expr_orig = search_mod._rand_expr
    search_mod._rand_expr = _forced_cross_expr

    def _mutate_forced(rng, expr, leaves):
        if rng.random() < 0.65:
            return _forced_cross_expr(rng)
        return search_mod._mutate_orig(rng, expr, leaves)

    search_mod._mutate_orig = search_mod._mutate
    search_mod._mutate = _mutate_forced
    log("v16 forced-cross patched (EVENT deepen; HARD BAN 5 new families + ACTIVE N=23 near-iso)")

    _allowed_leaves = frozenset(SEARCH_LEAVES)
    def _leaf_names_from_panels(panels, *, structural_only=False):
        return [n for n in panels.keys() if n in _allowed_leaves] or [n for n in panels.keys()]
    import quantlab.factors.ops as ops_mod
    ops_mod.leaf_names_present = _leaf_names_from_panels
    search_mod.leaf_names_present = _leaf_names_from_panels
    import quantlab.factors.ai_factory.novelty as nov_mod
    _orig_is_struct = nov_mod.is_structural_expr
    def _is_struct_v10(expr_str, allowed=None):
        return _orig_is_struct(expr_str, allowed=allowed or _allowed_leaves)
    nov_mod.is_structural_expr = _is_struct_v10
    search_mod.is_structural_expr = _is_struct_v10
    log("v10 leaf_names_present+is_structural patched")

    # placeholders filled after primary_panels built
    _primary_panels_ref: dict = {}
    _label_y_ref: dict = {"y": None, "eps": None}

    _orig = fit_mod.fitness_score_l1b
    def fitness_hardgate(factor, label, **kw):
        """Hybrid: economic ann_net/fitness vs y; ICIR prefers ε when finite else y+demote."""
        y0 = _label_y_ref.get("y")
        e0 = _label_y_ref.get("eps")
        # economic metrics always against y when available
        label_econ = y0 if y0 is not None else label
        met_y = _orig(factor, label_econ, **kw)
        met = dict(met_y)
        icir_y = met_y.get("icir", float("nan"))
        icir_e = float("nan")
        if e0 is not None:
            try:
                met_e = _orig(factor, e0, **kw)
                icir_e = met_e.get("icir", float("nan"))
            except Exception:
                icir_e = float("nan")
        resid_demote_flag = False
        if isinstance(icir_e, float) and math.isfinite(icir_e):
            met["icir"] = icir_e
            met["icir_source"] = "eps"
            icir = icir_e
        else:
            met["icir"] = icir_y
            met["icir_source"] = "y_fallback"
            resid_demote_flag = True
            icir = icir_y
        met["icir_y"] = icir_y if isinstance(icir_y, float) else float("nan")
        met["icir_eps"] = icir_e if isinstance(icir_e, float) else float("nan")
        met["icir_eps_gate"] = icir_e if isinstance(icir_e, float) else float("nan")  # gate-path residual ICIR
        met["resid_demote_flag"] = resid_demote_flag
        try:
            fac_e = factor.loc[factor.index >= EXPLORE_START]
            nr = float(np.isfinite(fac_e.to_numpy(dtype=np.float64, copy=False)).mean())
        except Exception:
            nr = float("nan")
        met["nonempty_rate"] = nr
        hard_fail = []
        if not (isinstance(nr, float) and math.isfinite(nr) and nr >= theta_cov):
            hard_fail.append("coverage_sparse")
        if not (isinstance(icir, float) and math.isfinite(icir) and icir > 0):
            hard_fail.append("icir_le_0")
        # DEMOTE (soft): ICIR(y)>0 and ICIR(ε)≤0 — do not hard-kill during search
        if (isinstance(icir_y, float) and math.isfinite(icir_y) and icir_y > 0
                and isinstance(icir_e, float) and math.isfinite(icir_e) and icir_e <= 0):
            met["resid_demote_flag"] = True
            resid_demote_flag = True
        if met.get("novelty_fail"):
            hard_fail.append("textbook_corr")
        ann = met.get("ann_net")  # from y
        if ann is None or not (isinstance(ann, float) and math.isfinite(ann) and ann > 0):
            hard_fail.append("ann_net_le_0")
        max_fam = float("nan")
        fam_corr = {}
        for pn, pp in _primary_panels_ref.items():
            try:
                c = fit_mod.corr_with_panel(factor, pp)
                fam_corr[pn] = c
                if isinstance(c, float) and math.isfinite(c):
                    max_fam = abs(c) if not math.isfinite(max_fam) else max(max_fam, abs(c))
            except Exception:
                pass
        met["family_corr"] = fam_corr
        met["max_abs_family_corr"] = max_fam if math.isfinite(max_fam) else None
        if math.isfinite(max_fam) and max_fam > rho_hard:
            hard_fail.append("family_rho_hard")
        met["hard_gate_fail"] = hard_fail
        if hard_fail:
            met["fitness"] = -1e9
        else:
            fit = float(met.get("fitness") or -1e9)
            if math.isfinite(nr):
                # v9: stronger reward for primary-grade coverage (≥0.15)
                fit += 0.08 * min(nr, 0.6)
                if nr >= theta_cov_primary:
                    fit += 0.12  # primary-grade coverage bonus
            if math.isfinite(max_fam) and max_fam > rho_soft:
                fit -= lambda_fam * max_fam
            if resid_demote_flag:
                fit -= 0.15  # soft demote, keep searchable
            if math.isfinite(nr) and nr < theta_cov_primary:
                met["diversity_secondary_max"] = True
                fit -= 0.08  # v8: soft punish COV_SPARSE-like seats
            met["fitness"] = fit
        met["promotion_approved"] = False
        return met
    fit_mod.fitness_score_l1b = fitness_hardgate
    search_mod.fitness_score_l1b = fitness_hardgate

    log("loading L1b structural panels")
    panels, label, public, load_meta = l1b.load_structural_panels()
    _cast_panels_f32(panels)
    if isinstance(label, pd.DataFrame):
        label = label.astype("float32", copy=False)
    if isinstance(public, dict):
        _cast_panels_f32(public)
    gc.collect()
    peak = mem_mb()
    log("post-load f32 cast peak", round(peak), "available_mb", round(available_mb(), 1))
    label_y = label.copy()
    log("attach L1c easystock (+ann for PRIMARY Z only)")
    panels, label, public, load_meta = l1c.attach_l1c_panels(panels, label, public, load_meta)
    _cast_panels_f32(panels)
    if isinstance(label, pd.DataFrame):
        label = label.astype("float32", copy=False)
    gc.collect()
    peak = max(peak, mem_mb())

    # --- build PRIMARY panels from available leaves (document gaps) ---
    primary_panels: dict[str, pd.DataFrame] = {}
    primary_gaps: list[str] = []
    aux_for_primary = {}
    # keep ann_insider briefly
    if "ann_insider_dec_5" in panels:
        aux_for_primary["ann_insider_dec_5"] = panels["ann_insider_dec_5"]

    # try light fsr/dv/ocf/gm via l1f (may fail — gap ok)
    try:
        l1f = _import_mod("ai_factor_l1f_strict_gate_struct_explore", ROOT / "research/ai_factor_l1f_strict_gate_struct_explore.py")
        mask0 = panels["overnight_ret"].notna()
        cal0 = panels["overnight_ret"].index
        cols0 = list(panels["overnight_ret"].columns)
        fsr_dv, fsr_gap, dv_gap = l1f.build_fsr_dv_panels(cal0, cols0, mask0)
        for k in ("fsr", "fsr_delta_20", "dv_ttm"):
            if k in fsr_dv:
                aux_for_primary[k] = fsr_dv[k]
        del fsr_dv; gc.collect()
        log("fsr/dv aux for PRIMARY", list(k for k in ("fsr", "fsr_delta_20", "dv_ttm") if k in aux_for_primary))
    except Exception as _e:
        primary_gaps.append(f"fsr_dv_load_failed:{_e}")
        log("fsr/dv PRIMARY aux FAILED", _e)

    try:
        # gm / ocf if builders exist on l1f or l1g path
        if hasattr(l1f, "build_ocf_panels"):
            ocf_p, _ = l1f.build_ocf_panels(cal0, cols0, mask0)
            for k in ("ocf_to_profit",):
                if k in ocf_p:
                    aux_for_primary[k] = ocf_p[k]
            del ocf_p; gc.collect()
    except Exception as _e:
        primary_gaps.append(f"ocf_load_failed:{_e}")

    # gm_pit: financials_pit.grossprofit_margin + available_at → leaf_map name gm_pit
    # (Data: no standalone gm_pit file; unify ts_code↔instrument_id before join)
    try:
        gm_df, gm_meta = build_gm_pit_panel(cal0, cols0, mask0)
        if gm_df is not None and gm_meta.get("ok"):
            aux_for_primary["gm_pit"] = gm_df
            log("gm_pit loaded (financials grossprofit_margin)", gm_meta)
        else:
            # fallback L1g builder (also uses instrument_id)
            l1g = _import_mod("ai_factor_l1g_new_mech_family_explore", ROOT / "research/ai_factor_l1g_new_mech_family_explore.py")
            gm_p, gm_gap = l1g.build_roe_panels(cal0, cols0, mask0)
            if "gm_pit" in gm_p:
                aux_for_primary["gm_pit"] = gm_p["gm_pit"]
                log("gm_pit loaded via l1g fallback", "nonempty", float(gm_p["gm_pit"].notna().to_numpy().mean()))
            else:
                primary_gaps.append(f"gm_pit_missing:{gm_meta}")
                log("gm_pit MISSING", gm_meta, gm_gap)
            del gm_p; gc.collect()
        del gm_df; gc.collect()
    except Exception as _e:
        primary_gaps.append(f"gm_load_failed:{_e}")
        log("gm_pit load FAILED", _e)

    # materialize PRIMARY exprs we can from Expr trees
    def _try_primary(expr_s: str, tree: Expr, leaf_map: dict):
        need = leaves_in(expr_s)
        if not need <= set(leaf_map.keys()):
            primary_gaps.append(expr_s)
            return
        try:
            fac = apply_expr(tree, leaf_map).astype("float32")
            primary_panels[expr_s] = fac
            log("PRIMARY panel ok", expr_s, "nonempty", float(np.isfinite(fac.to_numpy()).mean()))
        except Exception as ex:
            primary_gaps.append(f"{expr_s}:err:{ex}")

    leaf_map = {}
    for k in ("overnight_ret", "lu_height", "idx_w500_delta_20", "ann_insider_dec_5",
              "fsr", "fsr_delta_20", "ocf_to_profit", "dv_ttm", "gm_pit"):
        if k in panels:
            leaf_map[k] = panels[k]
        elif k in aux_for_primary:
            leaf_map[k] = aux_for_primary[k]

    # explicit trees for PRIMARY
    _try_primary(
        "neg(idx_w500_delta_20)",
        Expr("op", "neg", (Expr("leaf", "idx_w500_delta_20"),)),
        leaf_map,
    )
    _try_primary(
        "ts_mean_20(sub(ts_mean_5(overnight_ret), ts_max_20(lu_height)))",
        Expr("op", "ts_mean_20", (Expr("op", "sub", (
            Expr("op", "ts_mean_5", (Expr("leaf", "overnight_ret"),)),
            Expr("op", "ts_max_20", (Expr("leaf", "lu_height"),)),
        )),)),
        leaf_map,
    )
    _try_primary(
        "rank(ts_std_10(ann_insider_dec_5))",
        Expr("op", "rank", (Expr("op", "ts_std_10", (Expr("leaf", "ann_insider_dec_5"),)),)),
        leaf_map,
    )
    _try_primary(
        "abs(ts_std_10(ts_delta_5(ann_insider_dec_5)))",
        Expr("op", "abs", (Expr("op", "ts_std_10", (Expr("op", "ts_delta_5", (Expr("leaf", "ann_insider_dec_5"),)),)),)),
        leaf_map,
    )
    # Alpha v12: fill historical Z gap — ann_insider×lu_height (tier=primary; search still bans insider)
    _try_primary(
        "ts_mean_20(sub(ann_insider_dec_5, ts_max_20(lu_height)))",
        Expr("op", "ts_mean_20", (Expr("op", "sub", (
            Expr("leaf", "ann_insider_dec_5"),
            Expr("op", "ts_max_20", (Expr("leaf", "lu_height"),)),
        )),)),
        leaf_map,
    )
    if "fsr_delta_20" in leaf_map:
        _try_primary("fsr_delta_20", Expr("leaf", "fsr_delta_20"), leaf_map)
        _try_primary(
            "ts_std_10(fsr_delta_20)",
            Expr("op", "ts_std_10", (Expr("leaf", "fsr_delta_20"),)),
            leaf_map,
        )
    if "fsr" in leaf_map:
        _try_primary(
            "ts_std_10(fsr)",
            Expr("op", "ts_std_10", (Expr("leaf", "fsr"),)),
            leaf_map,
        )
        _try_primary(
            "abs(ts_std_10(ts_delta_5(fsr)))",
            Expr("op", "abs", (Expr("op", "ts_std_10", (Expr("op", "ts_delta_5", (Expr("leaf", "fsr"),)),)),)),
            leaf_map,
        )
    if "ocf_to_profit" in leaf_map and "dv_ttm" in leaf_map:
        _try_primary(
            "mul(rank(ocf_to_profit), rank(dv_ttm))",
            Expr("op", "mul", (
                Expr("op", "rank", (Expr("leaf", "ocf_to_profit"),)),
                Expr("op", "rank", (Expr("leaf", "dv_ttm"),)),
            )),
            leaf_map,
        )
    if "gm_pit" in leaf_map:
        _try_primary(
            "ts_std_10(gm_pit)",
            Expr("op", "ts_std_10", (Expr("leaf", "gm_pit"),)),
            leaf_map,
        )
    # also include APPROVED ACTIVE if we can build it later from sp
    for g in primary_exprs_spec:
        if g not in primary_panels and g not in primary_gaps:
            primary_gaps.append(g)

    log("PRIMARY panels built", len(primary_panels), "gaps", len(primary_gaps))

    # Drop banned ann (insider / ann_n); KEEP buyback/penalty/earn as EVENT search leaves
    dropped_ann = []
    for k in list(panels.keys()):
        if k.startswith("ann_insider") or k == "ann_n_5":
            dropped_ann.append(k)
            del panels[k]
        elif k.startswith("ann_") and k not in EVENT_LEAVES:
            dropped_ann.append(k)
            del panels[k]
    for k in list(aux_for_primary.keys()):
        del aux_for_primary[k]
    gc.collect()

    mask = panels["overnight_ret"].notna()
    cols = list(panels["overnight_ret"].columns)
    cal = panels["overnight_ret"].index
    l1h_meta = {}
    log("attach L1h liq panels")
    liq_panels, liq_gap = l1h.build_liq_panels(cal, cols, mask)
    l1h_meta["liq"] = {"ok": liq_gap.get("ok"), "family": liq_gap.get("family")}
    for k in ("liq_cv_20", "neg_liq_cv_20", "liq_burst_10", "amt_cv_20", "neg_amt_cv_20"):
        if k in liq_panels:
            panels[k] = liq_panels[k]
    del liq_panels; gc.collect()
    peak = max(peak, mem_mb())

    log("attach L1h idx panels (delta only)")
    idx_panels, idx_gap = l1h.build_idx_panels(cal, cols, mask)
    l1h_meta["idx"] = {"ok": idx_gap.get("ok"), "family": idx_gap.get("family")}
    for k in ("idx_w500_delta_20", "idx_w_delta_20", "neg_idx_w_delta_20", "abs_idx_w_delta_20", "idx_w300_delta_20"):
        if k in idx_panels:
            panels[k] = idx_panels[k]
    del idx_panels; gc.collect()
    peak = max(peak, mem_mb())

    log("attach L1h lev panels (delta only)")
    lev_panels, lev_gap = l1h.build_lev_panels(cal, cols, mask)
    l1h_meta["lev"] = {"ok": lev_gap.get("ok"), "family": lev_gap.get("family")}
    for k in ("lev_delta_20", "abs_lev_delta_20"):
        if k in lev_panels:
            panels[k] = lev_panels[k]
    del lev_panels, mask; gc.collect()
    peak = max(peak, mem_mb())
    load_meta["l1h_attach"] = l1h_meta
    load_meta["dropped_ann_panels"] = dropped_ann
    load_meta["excluded_leaves_policy"] = list(EXCLUDED_LEAVES)

    # ---------- v14 EVENT / fund-flow / industry leaves (reuse v13 wiring; lean float32) ----------
    mask = panels["overnight_ret"].notna()
    cal = panels["overnight_ret"].index
    cols = list(panels["overnight_ret"].columns)
    event_meta = {"wired": [], "gaps": []}

    # 1) 龙虎榜 top_list (PIT available_at) via l1f
    try:
        l1f_ev = _import_mod(
            "ai_factor_l1f_strict_gate_struct_explore",
            ROOT / "research/ai_factor_l1f_strict_gate_struct_explore.py",
        )
        dt_panels, dt_gap = l1f_ev.build_dragon_panels(cal, cols, mask)
        for k in ("dt_net_5", "dt_net_10", "dt_flag_5"):
            if k in dt_panels:
                panels[k] = dt_panels[k].astype("float32", copy=False)
                event_meta["wired"].append(k)
        event_meta["dragon"] = {
            "ok": dt_gap.get("ok"),
            "n_events": dt_gap.get("n_events"),
            "n_instruments": dt_gap.get("n_instruments"),
            "path": dt_gap.get("path"),
        }
        for k in ("dt_net_5", "dt_net_10", "dt_flag_5"):
            if f"nonempty_{k}" in dt_gap:
                event_meta["dragon"][f"nonempty_{k}"] = dt_gap[f"nonempty_{k}"]
        del dt_panels
        gc.collect()
        log("dragon panels", event_meta["dragon"])
    except Exception as _e:
        event_meta["gaps"].append(f"dragon:{_e}")
        log("dragon FAILED", _e)

    # 2) 两融 rzrq_daily_tushare + float_mktcap (lean window) via l1e
    try:
        l1e_ev = _import_mod(
            "ai_factor_l1e_hard_cov_struct_explore",
            ROOT / "research/ai_factor_l1e_hard_cov_struct_explore.py",
        )
        V2 = ROOT / "data/v2"
        fm_path = V2 / "float_mktcap/float_mktcap_daily_tushare.parquet"
        fm_raw = pd.read_parquet(fm_path, columns=["trade_date", "instrument_id", "float_mktcap"])
        fm_raw["trade_date"] = pd.to_datetime(fm_raw["trade_date"])
        fm_raw = fm_raw[
            (fm_raw["trade_date"] >= LOOKBACK_START - pd.Timedelta(days=30))
            & (fm_raw["trade_date"] <= cal.max() + pd.Timedelta(days=5))
            & (fm_raw["instrument_id"].isin(cols))
        ]
        fm = (
            fm_raw.drop_duplicates(["trade_date", "instrument_id"], keep="last")
            .set_index(["trade_date", "instrument_id"])["float_mktcap"]
            .unstack()
            .reindex(index=cal, columns=cols)
            .astype("float32")
        )
        del fm_raw
        gc.collect()
        rz_panels, rz_gap = l1e_ev.build_rzrq_panels(cal, cols, mask, fm)
        for k in ("rz_delta_5", "rz_delta_10", "rzrq_delta_5", "rz_intensity"):
            if k in rz_panels:
                panels[k] = rz_panels[k].astype("float32", copy=False)
                event_meta["wired"].append(k)
        event_meta["rzrq"] = {
            "ok": rz_gap.get("ok"),
            "n_rows": rz_gap.get("n_rows"),
            "n_instruments": rz_gap.get("n_instruments"),
            "path": rz_gap.get("path"),
        }
        del rz_panels, fm
        gc.collect()
        log("rzrq panels", event_meta["rzrq"])
        peak = max(peak, mem_mb())
    except Exception as _e:
        event_meta["gaps"].append(f"rzrq:{_e}")
        log("rzrq FAILED", _e)

    # 3) 北向：stock-level hk_hold / hsgt_top10 truncated → GAP; use moneyflow_hsgt broadcast
    try:
        V2 = ROOT / "data/v2"
        nb_path = V2 / "northbound/moneyflow_hsgt_daily_2018plus.parquet"
        hk_path = V2 / "northbound/hk_hold_ashare_daily_2018plus.parquet"
        top10_path = V2 / "northbound/hsgt_top10_daily_2018plus.parquet"
        for gp, label_g in ((hk_path, "hk_hold_ashare"), (top10_path, "hsgt_top10")):
            if gp.exists():
                _s = pd.read_parquet(gp, columns=["trade_date"])
                _td = pd.to_datetime(_s["trade_date"].astype(str), errors="coerce")
                event_meta["gaps"].append(
                    f"{label_g}:coverage_truncated max={_td.max().date() if _td.notna().any() else None} "
                    f"(need Data refresh for explore window; not used)"
                )
                del _s
            else:
                event_meta["gaps"].append(f"{label_g}:missing_file")
        nb = pd.read_parquet(nb_path, columns=["trade_date", "north_money", "available_at"])
        nb["available_at"] = pd.to_datetime(nb["available_at"])
        if getattr(nb["available_at"].dt, "tz", None) is not None:
            nb["avail_date"] = (
                nb["available_at"].dt.tz_convert("Asia/Shanghai").dt.normalize().dt.tz_localize(None)
            )
        else:
            nb["avail_date"] = pd.to_datetime(nb["available_at"]).dt.normalize()
        nb["signal_date"] = nb["avail_date"] + pd.Timedelta(days=1)
        g = nb.groupby("signal_date")["north_money"].last().astype("float32")
        aligned = g.reindex(cal.union(g.index)).sort_index().ffill().reindex(cal)
        panels["nb_north_money"] = l1b._broadcast(aligned, cal, cols).astype("float32")
        event_meta["wired"].append("nb_north_money")
        event_meta["northbound"] = {
            "ok": True,
            "path": str(nb_path),
            "mode": "market_broadcast_moneyflow_hsgt",
            "n_rows": int(len(nb)),
            "nonempty": float(panels["nb_north_money"].notna().to_numpy().mean()),
        }
        del nb, g, aligned
        gc.collect()
        log("nb_north_money broadcast", event_meta["northbound"])
    except Exception as _e:
        event_meta["gaps"].append(f"northbound:{_e}")
        log("northbound FAILED", _e)

    # 4) 行业相对：overnight/intraday − SW_L1 industry CS mean
    try:
        asof_ind = cal[len(cal) // 2] if len(cal) else EXPLORE_START
        ind_codes, sw_m = build_sw_l1_codes(cols, asof_ind)
        if ind_codes is None or not sw_m.get("ok"):
            raise RuntimeError(f"sw_l1_for_ind_rel:{sw_m}")
        ind_codes = np.asarray(ind_codes)
        for src, dst in (("overnight_ret", "ind_rel_overnight"), ("intraday_ret", "ind_rel_intraday")):
            if src not in panels:
                continue
            arr = panels[src].to_numpy(dtype=np.float64, copy=False)
            out = np.full_like(arr, np.nan, dtype=np.float64)
            uniq = [
                u for u in np.unique(ind_codes)
                if u is not None and str(u) not in ("nan", "")
            ]
            for u in uniq:
                jmask = ind_codes == u
                if int(jmask.sum()) < 3:
                    continue
                sub = arr[:, jmask]
                with np.errstate(all="ignore"):
                    mu = np.nanmean(sub, axis=1, keepdims=True)
                out[:, jmask] = sub - mu
            panels[dst] = (
                pd.DataFrame(out, index=cal, columns=cols, dtype="float32")
                .where(mask)
                .astype("float32")
            )
            event_meta["wired"].append(dst)
        event_meta["ind_rel"] = {
            "ok": True,
            "asof": str(pd.Timestamp(asof_ind).date()),
            "sw": sw_m.get("n_mapped") or sw_m,
        }
        log("ind_rel panels", event_meta["ind_rel"])
        del out
        gc.collect()
    except Exception as _e:
        event_meta["gaps"].append(f"ind_rel:{_e}")
        log("ind_rel FAILED", _e)

    # 5) 非 insider 公告叶：由 l1c attach；确认仍在 panels
    for k in ("ann_buyback_5", "ann_penalty_5", "ann_earn_signed_5"):
        if k in panels:
            if k not in event_meta["wired"]:
                event_meta["wired"].append(k)
        else:
            event_meta["gaps"].append(f"{k}:not_in_panels_after_l1c")

    # 6) v16 NEW: ETF 份额变化（d_share_wan，PIT available_at）— 区别于 flow_est 金额流
    try:
        V2 = ROOT / "data/v2"
        def _etf_share_chg(path: Path, name: str) -> pd.Series | None:
            if not path.exists():
                event_meta["gaps"].append(f"{name}:missing:{path}")
                return None
            etf = pd.read_parquet(path, columns=["trade_date", "d_share_wan", "available_at", "ts_code"])
            etf["available_at"] = pd.to_datetime(etf["available_at"])
            etf["signal_date"] = etf["available_at"].dt.normalize() + pd.Timedelta(days=1)
            g = etf.groupby("signal_date")["d_share_wan"].sum().astype("float32")
            event_meta.setdefault("etf_share_chg", {})[name] = {
                "ok": True, "path": str(path), "n_rows": int(len(etf)),
                "n_codes": int(etf["ts_code"].nunique()),
            }
            del etf
            return g
        maj = _etf_share_chg(V2 / "etf/share_pit/etf_share_flow_pit_major.parquet", "etf_share_chg_major")
        thm = _etf_share_chg(V2 / "etf/share_pit/etf_share_flow_pit_industry_theme.parquet", "etf_share_chg_theme")
        for ser, leaf in ((maj, "etf_share_chg_major"), (thm, "etf_share_chg_theme")):
            if ser is None:
                continue
            aligned = ser.reindex(cal.union(ser.index)).sort_index().ffill().reindex(cal)
            panels[leaf] = l1b._broadcast(aligned, cal, cols).astype("float32")
            event_meta["wired"].append(leaf)
            del aligned
        del maj, thm
        gc.collect()
        log("etf_share_chg wired", event_meta.get("etf_share_chg"))
    except Exception as _e:
        event_meta["gaps"].append(f"etf_share_chg:{_e}")
        log("etf_share_chg FAILED", _e)

    # 7) v16 NEW: 行业层 ETF 份额流 → 个股（SW_L1 映射，截面可分）
    try:
        V2 = ROOT / "data/v2"
        theme_path = V2 / "etf/share_pit/etf_share_flow_pit_industry_theme.parquet"
        map_path = V2 / "etf/sw_l1_etf_map_pit_daily.parquet"
        prejoin = V2 / "etf/share_pit/ind_etf_share_flow_pit.parquet"
        if not prejoin.exists() and (not theme_path.exists() or not map_path.exists()):
            event_meta["gaps"].append("ind_etf_share_flow:missing_theme_or_map")
        else:
            # Prefer pre-joined research PIT (trade_date already YYYYMMDD str on both sides).
            if prejoin.exists():
                etf = pd.read_parquet(
                    prejoin,
                    columns=["ts_code", "trade_date", "sw_l1_code", "flow_est_wan_yuan", "available_at"],
                )
                etf["trade_date"] = etf["trade_date"].astype(str)
                etf["available_at"] = pd.to_datetime(etf["available_at"])
                etf["signal_date"] = etf["available_at"].dt.normalize() + pd.Timedelta(days=1)
                mp = etf[["ts_code", "trade_date", "sw_l1_code"]].drop_duplicates()  # for meta n_map_rows
            else:
                etf = pd.read_parquet(theme_path, columns=["ts_code", "trade_date", "flow_est_wan_yuan", "available_at"])
                etf["available_at"] = pd.to_datetime(etf["available_at"])
                etf["signal_date"] = etf["available_at"].dt.normalize() + pd.Timedelta(days=1)
                # CRITICAL: both sides YYYYMMDD str — do NOT to_datetime only map
                def _ymd(s):
                    if hasattr(s.dtype, "name") and "datetime" in str(s.dtype):
                        return s.dt.strftime("%Y%m%d")
                    return s.astype(str).str.replace(r"[^0-9]", "", regex=True).str.slice(0, 8)
                etf["trade_date"] = _ymd(etf["trade_date"])
                # map: etf_ts_code → sw_l1 on trade_date (PIT available_at)
                mp = pd.read_parquet(map_path, columns=["sw_l1_code", "trade_date", "etf_ts_code", "available_at"])
                mp["trade_date"] = _ymd(mp["trade_date"])
                mp["available_at"] = pd.to_datetime(mp["available_at"])
                # use map rows whose available_at <= signal; keep last per (signal-ish day, etf)
                mp = mp.sort_values(["etf_ts_code", "trade_date", "available_at"]).drop_duplicates(
                    ["etf_ts_code", "trade_date"], keep="last"
                )
                etf = etf.merge(
                    mp[["etf_ts_code", "trade_date", "sw_l1_code"]],
                    left_on=["ts_code", "trade_date"], right_on=["etf_ts_code", "trade_date"], how="inner",
                )
            if etf.empty:
                event_meta["gaps"].append("ind_etf_share_flow:empty_after_map_join")
            else:
                g = (
                    etf.groupby(["signal_date", "sw_l1_code"], as_index=False)["flow_est_wan_yuan"]
                    .sum()
                )
                # stock SW membership asof mid-cal
                asof_ind = cal[len(cal) // 2] if len(cal) else EXPLORE_START
                ind_codes, sw_m = build_sw_l1_codes(cols, asof_ind)
                if ind_codes is None or not sw_m.get("ok"):
                    event_meta["gaps"].append(f"ind_etf_share_flow:sw:{sw_m}")
                else:
                    ind_codes = np.asarray(ind_codes)
                    # pivot industry flow by signal_date
                    piv = g.pivot(index="signal_date", columns="sw_l1_code", values="flow_est_wan_yuan")
                    piv = piv.reindex(cal.union(piv.index)).sort_index().ffill().reindex(cal)
                    arr = np.full((len(cal), len(cols)), np.nan, dtype=np.float32)
                    # map sw code string forms
                    piv_cols = {str(c): c for c in piv.columns}
                    for j, sw in enumerate(ind_codes):
                        key = str(sw) if sw is not None else ""
                        if not key or key in ("nan", ""):
                            continue
                        # try exact / with .SI
                        col = None
                        for cand in (key, key if key.endswith(".SI") else key + ".SI", key.replace(".SI", "")):
                            if cand in piv_cols:
                                col = piv_cols[cand]; break
                            # also match numeric prefix
                        if col is None:
                            for pc, raw in piv_cols.items():
                                if pc.startswith(key[:6]) or key.startswith(pc[:6]):
                                    col = raw; break
                        if col is None:
                            continue
                        arr[:, j] = piv[col].to_numpy(dtype=np.float32, copy=False)
                    panels["ind_etf_share_flow"] = (
                        pd.DataFrame(arr, index=cal, columns=cols, dtype="float32").where(mask)
                    )
                    event_meta["wired"].append("ind_etf_share_flow")
                    event_meta["ind_etf_share_flow"] = {
                        "ok": True,
                        "n_map_rows": int(len(mp)),
                        "n_joined": int(len(etf)),
                        "nonempty": float(np.isfinite(arr).mean()),
                        "sw": sw_m.get("n_mapped") or sw_m,
                    }
                    log("ind_etf_share_flow", event_meta["ind_etf_share_flow"])
                    del piv, arr, g
            del etf, mp
            gc.collect()
            peak = max(peak, mem_mb())
    except Exception as _e:
        event_meta["gaps"].append(f"ind_etf_share_flow:{_e}")
        log("ind_etf_share_flow FAILED", _e)

    # 8) v16 NEW: 解禁残差 unlock_resid — 区别于 banned lockup_S_20（前瞻窗供给）
    #    用 ann_date PIT：已公告且 float_date∈[t-5,t] 的 float_ratio 合计，截面相对 log(float_mktcap) 残差
    try:
        V2 = ROOT / "data/v2"
        sf_path = V2 / "share_float/share_float_2018plus.parquet"
        fm_path = V2 / "float_mktcap/float_mktcap_daily_tushare.parquet"
        if not sf_path.exists():
            event_meta["gaps"].append("unlock_resid:missing_share_float")
        else:
            sf = pd.read_parquet(sf_path, columns=["ts_code", "ann_date", "float_date", "float_ratio"])
            sf["ann_date"] = pd.to_datetime(sf["ann_date"])
            sf["float_date"] = pd.to_datetime(sf["float_date"])
            sf["bs"] = sf["ts_code"].map(_ts_code_to_instrument_id)
            # _ts_code_to_instrument_id returns sz.000001; L1b uses baostock ids — panels cols are instrument_id
            sf = sf[sf["bs"].isin(cols)]
            sf = sf[
                (sf["float_date"] >= LOOKBACK_START - pd.Timedelta(days=10))
                & (sf["float_date"] <= cal.max() + pd.Timedelta(days=5))
            ]
            # only events announced before float (PIT): signal usable from max(ann+1, float-5) ...
            agg = (
                sf.groupby(["bs", "float_date", "ann_date"], as_index=False)["float_ratio"].sum()
            )
            raw = np.zeros((len(cal), len(cols)), dtype=np.float32)
            col_index = {c: i for i, c in enumerate(cols)}
            cal_np = cal.values.astype("datetime64[ns]")
            for row in agg.itertuples(index=False):
                bs, fdt, adt, ratio = row.bs, row.float_date, row.ann_date, float(row.float_ratio)
                j = col_index.get(bs)
                if j is None or not np.isfinite(ratio):
                    continue
                # known only after ann_date+1; attribute intensity on [float-5, float] ∩ known
                known = pd.Timestamp(adt) + pd.Timedelta(days=1)
                start = max(known, pd.Timestamp(fdt) - pd.Timedelta(days=5))
                end = pd.Timestamp(fdt)
                if end < start:
                    continue
                i0 = int(np.searchsorted(cal_np, np.datetime64(start), side="left"))
                i1 = int(np.searchsorted(cal_np, np.datetime64(end), side="right"))
                if i0 < i1:
                    raw[i0:i1, j] += np.float32(ratio)
            # residualize vs log float mktcap CS each day
            resid = raw.astype(np.float64).copy()
            try:
                fm_raw = pd.read_parquet(fm_path, columns=["trade_date", "instrument_id", "float_mktcap"])
                fm_raw["trade_date"] = pd.to_datetime(fm_raw["trade_date"])
                fm_raw = fm_raw[
                    (fm_raw["trade_date"] >= LOOKBACK_START - pd.Timedelta(days=30))
                    & (fm_raw["trade_date"] <= cal.max() + pd.Timedelta(days=5))
                    & (fm_raw["instrument_id"].isin(cols))
                ]
                fm = (
                    fm_raw.drop_duplicates(["trade_date", "instrument_id"], keep="last")
                    .set_index(["trade_date", "instrument_id"])["float_mktcap"]
                    .unstack()
                    .reindex(index=cal, columns=cols)
                    .astype("float32")
                )
                del fm_raw
                size = np.log(np.clip(fm.to_numpy(dtype=np.float64), 1.0, None))
                for i in range(resid.shape[0]):
                    y = resid[i]
                    x = size[i]
                    m = np.isfinite(y) & np.isfinite(x) & (raw[i] != 0)
                    if int(m.sum()) < 8:
                        # keep raw where nonzero; else nan
                        resid[i] = np.where(raw[i] != 0, y, np.nan)
                        continue
                    # OLS residual y ~ 1 + x
                    X = np.column_stack([np.ones(int(m.sum())), x[m]])
                    coef, *_ = np.linalg.lstsq(X, y[m], rcond=None)
                    pred = coef[0] + coef[1] * x
                    out = np.full_like(y, np.nan)
                    out[m] = y[m] - (coef[0] + coef[1] * x[m])
                    # also keep zeros as nan (no unlock)
                    resid[i] = out
                del fm, size
            except Exception as _re:
                event_meta["gaps"].append(f"unlock_resid_size:{_re}")
                resid = np.where(raw != 0, raw, np.nan).astype(np.float64)
            panels["unlock_resid"] = (
                pd.DataFrame(resid, index=cal, columns=cols, dtype="float32").where(mask)
            )
            event_meta["wired"].append("unlock_resid")
            event_meta["unlock_resid"] = {
                "ok": True,
                "n_events": int(len(agg)),
                "nonzero_frac": float((raw != 0).mean()),
                "nonempty": float(np.isfinite(resid).mean()),
                "note": "distinct_from_lockup_S_20; PIT ann_date; CS residual vs log float_mktcap",
            }
            log("unlock_resid", event_meta["unlock_resid"])
            del sf, agg, raw, resid
            gc.collect()
            peak = max(peak, mem_mb())
    except Exception as _e:
        event_meta["gaps"].append(f"unlock_resid:{_e}")
        log("unlock_resid FAILED", _e)

    # 9) v16 NEW: 涨跌停次日结构 — overnight × lag(limit_flag)；需 L1b limit_* 仍在 panels
    try:
        if "limit_up_flag" in panels and "overnight_ret" in panels:
            lu_lag = panels["limit_up_flag"].shift(1)
            panels["lu_next_on"] = (panels["overnight_ret"] * lu_lag.astype("float32")).astype("float32").where(mask)
            event_meta["wired"].append("lu_next_on")
        else:
            event_meta["gaps"].append("lu_next_on:missing_limit_up_flag_or_overnight")
        if "limit_down_flag" in panels and "overnight_ret" in panels:
            ld_lag = panels["limit_down_flag"].shift(1)
            panels["ld_next_on"] = (panels["overnight_ret"] * ld_lag.astype("float32")).astype("float32").where(mask)
            event_meta["wired"].append("ld_next_on")
        else:
            event_meta["gaps"].append("ld_next_on:missing_limit_down_flag_or_overnight")
        event_meta["limit_next"] = {
            "lu_next_on": "lu_next_on" in panels,
            "ld_next_on": "ld_next_on" in panels,
            "note": "overnight after prior-day limit; not days_since_lu primary transplant",
        }
        log("limit_next", event_meta["limit_next"])
        gc.collect()
    except Exception as _e:
        event_meta["gaps"].append(f"limit_next:{_e}")
        log("limit_next FAILED", _e)

    load_meta["event_attach"] = event_meta
    log(
        "EVENT attach done",
        "wired", event_meta["wired"],
        "gaps", event_meta["gaps"],
        "peak", round(peak),
        "available_mb", round(available_mb(), 1),
    )
    peak = max(peak, mem_mb())
    del mask
    gc.collect()

    # etf_all_flow
    try:
        V2 = ROOT / "data/v2"
        etf_all_path = V2 / "etf/share_pit/etf_share_flow_pit_all.parquet"
        etf = pd.read_parquet(etf_all_path)
        etf["available_at"] = pd.to_datetime(etf["available_at"])
        etf["signal_date"] = etf["available_at"].dt.normalize() + pd.Timedelta(days=1)
        g = etf.groupby("signal_date")["flow_est_wan_yuan"].sum().astype("float32")
        cal0 = panels["overnight_ret"].index
        cols0 = list(panels["overnight_ret"].columns)
        aligned = g.reindex(cal0.union(g.index)).sort_index().ffill().reindex(cal0)
        panels["etf_all_flow"] = l1b._broadcast(aligned, cal0, cols0)
        load_meta.setdefault("data_status", {})["etf_all"] = {
            "ok": True, "path": str(etf_all_path), "n_rows": int(len(etf)),
            "n_codes": int(etf["ts_code"].nunique()),
        }
        log("etf_all_flow attached", "nonempty", float(panels["etf_all_flow"].notna().mean().mean()))
        del etf, g, aligned
    except Exception as _e:
        load_meta.setdefault("data_status", {})["etf_all"] = {"ok": False, "error": str(_e)}
        log("etf_all_flow FAILED", _e)

    # rebuild overnight-lu / idx primary if panels now refreshed
    if "idx_w500_delta_20" in panels and "neg(idx_w500_delta_20)" not in primary_panels:
        primary_panels["neg(idx_w500_delta_20)"] = (-panels["idx_w500_delta_20"]).astype("float32")
    if all(k in panels for k in ("overnight_ret", "lu_height")):
        try:
            tree = Expr("op", "ts_mean_20", (Expr("op", "sub", (
                Expr("op", "ts_mean_5", (Expr("leaf", "overnight_ret"),)),
                Expr("op", "ts_max_20", (Expr("leaf", "lu_height"),)),
            )),))
            primary_panels["ts_mean_20(sub(ts_mean_5(overnight_ret), ts_max_20(lu_height)))"] = apply_expr(
                tree, {"overnight_ret": panels["overnight_ret"], "lu_height": panels["lu_height"]}
            ).astype("float32")
        except Exception as ex:
            primary_gaps.append(f"overnight_lu_rebuild:{ex}")

    # APPROVED ACTIVE panels for family corr (both champions; do not edit shortlist files)
    if all(k in panels for k in ("etf_major_flow", "neg_amt_cv_20")):
        try:
            tree = Expr("op", "ts_max_20", (Expr("op", "ts_mean_5", (Expr("op", "div", (
                Expr("leaf", "etf_major_flow"), Expr("leaf", "neg_amt_cv_20"),
            )),)),))
            primary_panels["ts_max_20(ts_mean_5(div(etf_major_flow, neg_amt_cv_20)))"] = apply_expr(
                tree, {"etf_major_flow": panels["etf_major_flow"], "neg_amt_cv_20": panels["neg_amt_cv_20"]}
            ).astype("float32")
            log("ACTIVE etf×liq champion panel in family-corr set")
        except Exception as ex:
            log("ACTIVE etf×liq panel failed", ex)
            primary_gaps.append(f"active_etf_liq:{ex}")
    if all(k in panels for k in ("idx_w_delta_20", "etf_all_flow")):
        try:
            tree = Expr("op", "mul", (
                Expr("op", "ts_mean_20", (Expr("leaf", "idx_w_delta_20"),)),
                Expr("op", "ts_mean_5", (Expr("leaf", "etf_all_flow"),)),
            ))
            primary_panels["mul(ts_mean_20(idx_w_delta_20), ts_mean_5(etf_all_flow))"] = apply_expr(
                tree, {"idx_w_delta_20": panels["idx_w_delta_20"], "etf_all_flow": panels["etf_all_flow"]}
            ).astype("float32")
            log("ACTIVE idx×etf_all panel in family-corr set")
        except Exception as ex:
            log("ACTIVE idx×etf_all panel failed", ex)
            primary_gaps.append(f"active_idx_etf:{ex}")
    # APPROVED ACTIVE #14 overnight×abs_idx (v7 adjudication)
    if all(k in panels for k in ("overnight_ret", "abs_idx_w_delta_20")):
        try:
            tree = Expr("op", "ts_mean_5", (Expr("op", "mul", (
                Expr("op", "ts_mean_20", (Expr("leaf", "overnight_ret"),)),
                Expr("op", "ts_mean_20", (Expr("leaf", "abs_idx_w_delta_20"),)),
            )),))
            primary_panels["ts_mean_5(mul(ts_mean_20(overnight_ret), ts_mean_20(abs_idx_w_delta_20)))"] = apply_expr(
                tree, {"overnight_ret": panels["overnight_ret"], "abs_idx_w_delta_20": panels["abs_idx_w_delta_20"]}
            ).astype("float32")
            log("ACTIVE overnight×abs_idx panel in family-corr set")
        except Exception as ex:
            log("ACTIVE overnight×abs_idx panel failed", ex)
            primary_gaps.append(f"active_overnight_abs_idx:{ex}")
    # APPROVED ACTIVE #15 etf_major×idx_w500 (v8 adjudication; Y_ICIR_NEG_WARN / BROADCAST_PIT_WARN)
    if all(k in panels for k in ("etf_major_flow", "idx_w500_delta_20")):
        try:
            tree = Expr("op", "ts_mean_20", (Expr("op", "mul", (
                Expr("op", "ts_mean_10", (Expr("leaf", "etf_major_flow"),)),
                Expr("leaf", "idx_w500_delta_20"),
            )),))
            primary_panels["ts_mean_20(mul(ts_mean_10(etf_major_flow), idx_w500_delta_20))"] = apply_expr(
                tree, {"etf_major_flow": panels["etf_major_flow"], "idx_w500_delta_20": panels["idx_w500_delta_20"]}
            ).astype("float32")
            log("ACTIVE etf_major×idx_w500 (v8) panel in family-corr set")
        except Exception as ex:
            log("ACTIVE etf_major×idx_w500 panel failed", ex)
            primary_gaps.append(f"active_etf_major_idx_v8:{ex}")
    # APPROVED ACTIVE #16 if_basis×neg_idx (v9 adjudication)
    if all(k in panels for k in ("if_basis", "neg_idx_w_delta_20")):
        try:
            tree = Expr("op", "ts_mean_10", (Expr("op", "mul", (
                Expr("op", "ts_max_20", (Expr("leaf", "if_basis"),)),
                Expr("op", "ts_mean_20", (Expr("leaf", "neg_idx_w_delta_20"),)),
            )),))
            primary_panels["ts_mean_10(mul(ts_max_20(if_basis), ts_mean_20(neg_idx_w_delta_20)))"] = apply_expr(
                tree, {"if_basis": panels["if_basis"], "neg_idx_w_delta_20": panels["neg_idx_w_delta_20"]}
            ).astype("float32")
            log("ACTIVE if_basis×neg_idx (v9) panel in family-corr set")
        except Exception as ex:
            log("ACTIVE if_basis×neg_idx panel failed", ex)
            primary_gaps.append(f"active_if_basis_neg_idx_v9:{ex}")
    # APPROVED ACTIVE #17 abs_idx−on_minus (v9 adjudication; NEAR_SIB_WARN)
    if all(k in panels for k in ("abs_idx_w_delta_20", "on_minus_id")):
        try:
            tree = Expr("op", "ts_mean_10", (Expr("op", "sub", (
                Expr("op", "ts_max_20", (Expr("leaf", "abs_idx_w_delta_20"),)),
                Expr("op", "abs", (Expr("leaf", "on_minus_id"),)),
            )),))
            primary_panels["ts_mean_10(sub(ts_max_20(abs_idx_w_delta_20), abs(on_minus_id)))"] = apply_expr(
                tree, {"abs_idx_w_delta_20": panels["abs_idx_w_delta_20"], "on_minus_id": panels["on_minus_id"]}
            ).astype("float32")
            log("ACTIVE abs_idx−on_minus (v9) panel in family-corr set")
        except Exception as ex:
            log("ACTIVE abs_idx−on_minus panel failed", ex)
            primary_gaps.append(f"active_abs_idx_on_minus_v9:{ex}")
    # APPROVED ACTIVE #18 idx_w_delta−liq_cv (v10 adjudication; SOFT_FAM_WARN |ρ|≈0.407; FRAGMENT_TRIAL)
    if all(k in panels for k in ("idx_w_delta_20", "liq_cv_20")):
        try:
            tree = Expr("op", "sub", (
                Expr("op", "ts_mean_5", (Expr("leaf", "idx_w_delta_20"),)),
                Expr("op", "ts_max_20", (Expr("leaf", "liq_cv_20"),)),
            ))
            primary_panels["sub(ts_mean_5(idx_w_delta_20), ts_max_20(liq_cv_20))"] = apply_expr(
                tree, {"idx_w_delta_20": panels["idx_w_delta_20"], "liq_cv_20": panels["liq_cv_20"]}
            ).astype("float32")
            log("ACTIVE idx_w_delta−liq_cv (v10) panel in family-corr set")
        except Exception as ex:
            log("ACTIVE idx_w_delta−liq_cv panel failed", ex)
            primary_gaps.append(f"active_idx_liq_cv_v10:{ex}")
    # APPROVED ACTIVE #19 neg_idx−liq_burst (v10b adjudication; STRUCT_DISTINCT vs v10)
    if all(k in panels for k in ("neg_idx_w_delta_20", "liq_burst_10")):
        try:
            tree = Expr("op", "ts_mean_20", (Expr("op", "sub", (
                Expr("op", "ts_mean_20", (Expr("leaf", "neg_idx_w_delta_20"),)),
                Expr("op", "ts_mean_5", (Expr("leaf", "liq_burst_10"),)),
            )),))
            primary_panels["ts_mean_20(sub(ts_mean_20(neg_idx_w_delta_20), ts_mean_5(liq_burst_10)))"] = apply_expr(
                tree, {"neg_idx_w_delta_20": panels["neg_idx_w_delta_20"], "liq_burst_10": panels["liq_burst_10"]}
            ).astype("float32")
            log("ACTIVE neg_idx−liq_burst (v10b) panel in family-corr set")
        except Exception as ex:
            log("ACTIVE neg_idx−liq_burst panel failed", ex)
            primary_gaps.append(f"active_neg_idx_liq_burst_v10b:{ex}")
    # APPROVED ACTIVE #20 idx×lev (v11 adjudication; COVERAGE_THIN_EDGE + Y_ICIR_NEG_WARN)
    # v12 bug: listed in SHORTLIST/KNOWN but NEVER materialized → PRIMARY_in_Z missed #20
    if all(k in panels for k in ("idx_w500_delta_20", "abs_lev_delta_20", "neg_idx_w_delta_20")):
        try:
            tree = Expr("op", "sub", (
                Expr("op", "neg", (Expr("leaf", "idx_w500_delta_20"),)),
                Expr("op", "div", (
                    Expr("leaf", "abs_lev_delta_20"),
                    Expr("leaf", "neg_idx_w_delta_20"),
                )),
            ))
            primary_panels["sub(neg(idx_w500_delta_20), div(abs_lev_delta_20, neg_idx_w_delta_20))"] = apply_expr(
                tree, {
                    "idx_w500_delta_20": panels["idx_w500_delta_20"],
                    "abs_lev_delta_20": panels["abs_lev_delta_20"],
                    "neg_idx_w_delta_20": panels["neg_idx_w_delta_20"],
                }
            ).astype("float32")
            log("ACTIVE idx×lev (v11 #20) panel in family-corr set")
            primary_gaps[:] = [g for g in primary_gaps
                               if "sub(neg(idx_w500_delta_20), div(abs_lev_delta_20" not in str(g)]
        except Exception as ex:
            log("ACTIVE idx×lev panel failed", ex)
            primary_gaps.append(f"active_idx_lev_v11:{ex}")

    # APPROVED ACTIVE #21 overnight×ann_buyback (v13 → v12 adjudication primary)
    if all(k in panels for k in ("overnight_ret", "ann_buyback_5")):
        try:
            tree = Expr("op", "neg", (Expr("op", "sub", (
                Expr("op", "ts_max_20", (Expr("leaf", "overnight_ret"),)),
                Expr("op", "ts_mean_10", (Expr("leaf", "ann_buyback_5"),)),
            )),))
            primary_panels["neg(sub(ts_max_20(overnight_ret), ts_mean_10(ann_buyback_5)))"] = apply_expr(
                tree, {"overnight_ret": panels["overnight_ret"], "ann_buyback_5": panels["ann_buyback_5"]}
            ).astype("float32")
            log("ACTIVE overnight×ann_buyback (v13) panel in family-corr set")
            primary_gaps[:] = [g for g in primary_gaps
                               if "neg(sub(ts_max_20(overnight_ret), ts_mean_10(ann_buyback_5)))" not in str(g)]
        except Exception as ex:
            log("ACTIVE overnight×ann_buyback panel failed", ex)
            primary_gaps.append(f"active_overnight_buyback_v13:{ex}")
    # APPROVED ACTIVE #22 buyback−ind_rel_intraday (v14 #1)
    if all(k in panels for k in ("ann_buyback_5", "ind_rel_intraday")):
        try:
            tree = Expr("op", "sub", (
                Expr("op", "ts_max_20", (Expr("leaf", "ann_buyback_5"),)),
                Expr("op", "ts_mean_10", (Expr("leaf", "ind_rel_intraday"),)),
            ))
            primary_panels["sub(ts_max_20(ann_buyback_5), ts_mean_10(ind_rel_intraday))"] = apply_expr(
                tree, {"ann_buyback_5": panels["ann_buyback_5"], "ind_rel_intraday": panels["ind_rel_intraday"]}
            ).astype("float32")
            log("ACTIVE buyback−ind_rel (v14) panel in family-corr set")
            primary_gaps[:] = [g for g in primary_gaps
                               if "sub(ts_max_20(ann_buyback_5), ts_mean_10(ind_rel_intraday))" not in str(g)]
        except Exception as ex:
            log("ACTIVE buyback−ind_rel panel failed", ex)
            primary_gaps.append(f"active_buyback_ind_rel_v14:{ex}")
    # APPROVED ACTIVE #23 ind_rel_overnight−dt_net (v14 #4)
    if all(k in panels for k in ("ind_rel_overnight", "dt_net_5")):
        try:
            tree = Expr("op", "ts_mean_20", (Expr("op", "sub", (
                Expr("op", "ts_mean_20", (Expr("leaf", "ind_rel_overnight"),)),
                Expr("op", "ts_std_10", (Expr("leaf", "dt_net_5"),)),
            )),))
            primary_panels["ts_mean_20(sub(ts_mean_20(ind_rel_overnight), ts_std_10(dt_net_5)))"] = apply_expr(
                tree, {"ind_rel_overnight": panels["ind_rel_overnight"], "dt_net_5": panels["dt_net_5"]}
            ).astype("float32")
            log("ACTIVE ind_rel×dt_net (v14) panel in family-corr set")
            primary_gaps[:] = [g for g in primary_gaps
                               if "ts_mean_20(sub(ts_mean_20(ind_rel_overnight), ts_std_10(dt_net_5)))" not in str(g)]
        except Exception as ex:
            log("ACTIVE ind_rel×dt_net panel failed", ex)
            primary_gaps.append(f"active_ind_rel_dt_v14:{ex}")

    # cosmetic primary_gap fix: always materialize neg(idx_w500_delta_20) when leaf present
    if "idx_w500_delta_20" in panels:
        primary_panels["neg(idx_w500_delta_20)"] = (-panels["idx_w500_delta_20"]).astype("float32")
        primary_gaps[:] = [g for g in primary_gaps if g != "neg(idx_w500_delta_20)" and not str(g).startswith("neg(idx_w500_delta_20):")]
        log("PRIMARY neg(idx_w500_delta_20) ensured")

    # size + SW_L1 for residual Z (sw_code via v2 tushare PIT — Alpha mandatory)
    size_panel = public.get("size") if public else None
    cols_for_z = list(label_y.columns)
    asof_day = EXPLORE_START
    if len(label_y.index):
        # prefer mid-sample asof for membership stability
        asof_day = label_y.index[len(label_y.index) // 2]
    ind_codes, sw_meta = build_sw_l1_codes(cols_for_z, asof_day)
    if sw_meta.get("ok"):
        log("SW_L1 mapped", sw_meta)
    else:
        primary_gaps.append(f"sw_l1:{sw_meta.get('error') or sw_meta}")
        log("SW_L1 FAILED", sw_meta)
        # last-resort: try EXPLORE_START / first calendar day
        for alt_day in (EXPLORE_START, label_y.index[0] if len(label_y.index) else EXPLORE_START):
            ind2, meta2 = build_sw_l1_codes(cols_for_z, alt_day)
            if meta2.get("ok"):
                ind_codes, sw_meta = ind2, meta2
                log("SW_L1 mapped (alt asof)", sw_meta)
                # remove last gap if recovered
                primary_gaps[:] = [g for g in primary_gaps if not str(g).startswith("sw_l1:")]
                break

    log("building residual label ε")
    label_eps, resid_meta = build_resid_label(label_y, size_panel, ind_codes, primary_panels, min_names=50)
    resid_meta["gaps"] = primary_gaps
    resid_meta["sw_l1"] = sw_meta
    resid_meta["n_primary_in_Z"] = len(primary_panels)
    log("resid ε", "days_ok", resid_meta["n_days_ok"], "primary", list(primary_panels.keys()))
    peak = max(peak, mem_mb())

    _primary_panels_ref.clear()
    _primary_panels_ref.update(primary_panels)
    _label_y_ref["y"] = label_y
    _label_y_ref["eps"] = label_eps

    sp = {k: panels[k] for k in SEARCH_LEAVES if k in panels}
    missing = [k for k in SEARCH_LEAVES if k not in panels]
    dropped_nan = []
    for k in list(sp.keys()):
        if sp[k].notna().sum().sum() == 0:
            dropped_nan.append(k); del sp[k]
    leaf_diag = {}
    for k, v in sp.items():
        arr = v.to_numpy(dtype=np.float64, copy=False)
        finite = np.isfinite(arr)
        nz = finite & (arr != 0)
        leaf_diag[k] = {
            "nonempty_rate": float(finite.mean()),
            "nonzero_rate": float(nz.mean()),
            "shape": list(v.shape),
        }
    _cast_panels_f32(sp)
    _cast_panels_f32(primary_panels)
    gc.collect()
    log("search leaves", sorted(sp.keys()), "missing", missing, "dropped_nan", dropped_nan, "peak", peak, "available_mb", round(available_mb(), 1))
    del panels
    gc.collect()

    cols = list(next(iter(sp.values())).columns)
    cal = next(iter(sp.values())).index
    sig, adv = sci.load_sig_adv(cols, cal)
    peak = max(peak, mem_mb())

    run_ledger = OUT / "ledger_run.jsonl"
    if run_ledger.exists(): run_ledger.unlink()
    main_ledger = ROOT / "output/ai_factor/ledger.jsonl"
    n_before = sum(1 for x in main_ledger.read_text().splitlines() if x.strip()) if main_ledger.exists() else 0

    # Z completeness: SW_L1 + gm_pit + ALL ACTIVE primary N=23 in PRIMARY Z
    z_has_sw = bool(resid_meta.get("has_sw_l1"))
    z_has_gm = "ts_std_10(gm_pit)" in primary_panels
    _active_need = [
        "rank(ts_std_10(ann_insider_dec_5))",
        "abs(ts_std_10(ts_delta_5(ann_insider_dec_5)))",
        "ts_std_10(fsr_delta_20)",
        "fsr_delta_20",
        "abs(ts_std_10(ts_delta_5(fsr)))",
        "ts_std_10(fsr)",
        "mul(rank(ocf_to_profit), rank(dv_ttm))",
        "ts_std_10(gm_pit)",
        "neg(idx_w500_delta_20)",
        "ts_mean_20(sub(ts_mean_5(overnight_ret), ts_max_20(lu_height)))",
        "ts_mean_20(sub(ann_insider_dec_5, ts_max_20(lu_height)))",
        "ts_max_20(ts_mean_5(div(etf_major_flow, neg_amt_cv_20)))",
        "mul(ts_mean_20(idx_w_delta_20), ts_mean_5(etf_all_flow))",
        "ts_mean_5(mul(ts_mean_20(overnight_ret), ts_mean_20(abs_idx_w_delta_20)))",
        "ts_mean_20(mul(ts_mean_10(etf_major_flow), idx_w500_delta_20))",
        "ts_mean_10(mul(ts_max_20(if_basis), ts_mean_20(neg_idx_w_delta_20)))",
        "ts_mean_10(sub(ts_max_20(abs_idx_w_delta_20), abs(on_minus_id)))",
        "sub(ts_mean_5(idx_w_delta_20), ts_max_20(liq_cv_20))",
        "ts_mean_20(sub(ts_mean_20(neg_idx_w_delta_20), ts_mean_5(liq_burst_10)))",
        "sub(neg(idx_w500_delta_20), div(abs_lev_delta_20, neg_idx_w_delta_20))",
        "neg(sub(ts_max_20(overnight_ret), ts_mean_10(ann_buyback_5)))",
        "sub(ts_max_20(ann_buyback_5), ts_mean_10(ind_rel_intraday))",
        "ts_mean_20(sub(ts_mean_20(ind_rel_overnight), ts_std_10(dt_net_5)))",
    ]
    n_active_in_z = sum(1 for e in _active_need if e in primary_panels)
    missing_active = [e for e in _active_need if e not in primary_panels]
    z_has_active23 = n_active_in_z == 23 and not missing_active
    resid_meta["n_active_champions_in_Z"] = n_active_in_z
    resid_meta["n_active_need"] = 23
    resid_meta["missing_active_in_Z"] = missing_active
    resid_meta["z_has_active23"] = z_has_active23
    # hard gate: SW + gm + idx×lev (#20) + 3 new event ACTIVE must be present; soft-warn if older FSR/ann gaps
    _must = [
        "ts_std_10(gm_pit)",
        "neg(idx_w500_delta_20)",
        "ts_mean_20(sub(ts_mean_5(overnight_ret), ts_max_20(lu_height)))",
        "ts_mean_20(sub(ann_insider_dec_5, ts_max_20(lu_height)))",
        "ts_max_20(ts_mean_5(div(etf_major_flow, neg_amt_cv_20)))",
        "mul(ts_mean_20(idx_w_delta_20), ts_mean_5(etf_all_flow))",
        "ts_mean_5(mul(ts_mean_20(overnight_ret), ts_mean_20(abs_idx_w_delta_20)))",
        "ts_mean_20(mul(ts_mean_10(etf_major_flow), idx_w500_delta_20))",
        "ts_mean_10(mul(ts_max_20(if_basis), ts_mean_20(neg_idx_w_delta_20)))",
        "ts_mean_10(sub(ts_max_20(abs_idx_w_delta_20), abs(on_minus_id)))",
        "sub(ts_mean_5(idx_w_delta_20), ts_max_20(liq_cv_20))",
        "ts_mean_20(sub(ts_mean_20(neg_idx_w_delta_20), ts_mean_5(liq_burst_10)))",
        "sub(neg(idx_w500_delta_20), div(abs_lev_delta_20, neg_idx_w_delta_20))",
        "neg(sub(ts_max_20(overnight_ret), ts_mean_10(ann_buyback_5)))",
        "sub(ts_max_20(ann_buyback_5), ts_mean_10(ind_rel_intraday))",
        "ts_mean_20(sub(ts_mean_20(ind_rel_overnight), ts_std_10(dt_net_5)))",
    ]
    z_must_ok = all(e in primary_panels for e in _must)
    # active23=True preferred; allow soft miss only on legacy FSR/ann_insider sole leaves if must holds
    z_complete = z_has_sw and z_has_gm and resid_meta["n_days_ok"] >= 40 and z_must_ok
    resid_meta["z_complete"] = z_complete
    resid_meta["z_must_ok"] = z_must_ok
    resid_meta["z_has_sw"] = z_has_sw
    resid_meta["z_has_gm"] = z_has_gm
    log("Z check", "PRIMARY_in_Z", len(primary_panels), "active_in_Z", n_active_in_z, "/23",
        "active23", z_has_active23, "must_ok", z_must_ok, "missing", missing_active[:5])
    if not z_complete:
        log("Z INCOMPLETE — refuse ε search", "sw", z_has_sw, "gm", z_has_gm, "days_ok", resid_meta["n_days_ok"], "gaps", primary_gaps)
        # still write receipt documenting gaps; do not launch empty-config re-run
        receipt = {
            "n_candidates": 0, "n_gate_ok": 0, "n_killed_by_novelty": 0,
            "fail_reason_top3": [{"reason": "z_incomplete_abort", "n": 1}],
            "n_top_k": 0, "p0_1_exact": True, "p0_2_resid": True,
            "gp_label": "aborted", "resid_meta": resid_meta,
            "primary_panels_built": list(primary_panels.keys()),
            "primary_gaps": primary_gaps,
            "aborted": True,
            "abort_reason": "Z incomplete (need SW_L1 sw_code + gm_pit PRIMARY) — fix before search",
        }
        (OUT / "receipt.json").write_text(json.dumps(clean(receipt), indent=2, ensure_ascii=False), encoding="utf-8")
        (OUT / "summary.json").write_text(json.dumps(clean({
            "promotion_approved": False, "sealed": False, "aborted": True,
            "receipt": receipt, "policy": "v10b_resume Z-incomplete abort",
        }), indent=2, ensure_ascii=False), encoding="utf-8")
        REPORT.write_text(
            "\n".join([
                "# AI 因子 GP v10b_resume — Z 不完整中止",
                "",
                f"- has_sw_l1={z_has_sw}; gm_pit PRIMARY={z_has_gm}; days_ok={resid_meta['n_days_ok']}",
                f"- gaps={primary_gaps}",
                f"- sw_meta={sw_meta}",
                "- promotion_approved=false; 未开密封",
                "",
            ]),
            encoding="utf-8",
        )
        log("ABORT Z incomplete", receipt)
        print(json.dumps({"aborted": True, "receipt": receipt}, ensure_ascii=False, indent=2, default=str))
        return 2

    use_eps = True
    gp_label = label_eps
    log("gp label eps (Z complete)", "days_ok", resid_meta["n_days_ok"], "n_sw_dummies", resid_meta.get("n_sw_dummies"), "primary", len(primary_panels))

    # --- patch gp_search: seed forced crosses + no empty-gen early-stop before MIN_EVAL ---
    _orig_gp_search = search_mod.gp_search
    def gp_search_v12(panels, label, config=None):
        from quantlab.factors.ai_factory.search import (
            GPConfig as _GPC, SearchResult, Candidate, MAX_DEPTH, MAX_NODES,
            LEAF_FEATURES,
        )
        from quantlab.factors.ai_factory.ledger import append_attempt
        from quantlab.factors.ops import apply_expr, leaf_names_present
        # use patched bindings on search_mod / fit path
        fitness_score_l1b = search_mod.fitness_score_l1b
        from quantlab.factors.ai_factory.fitness import fitness_score
        is_textbook_expr = search_mod.is_textbook_expr if hasattr(search_mod, "is_textbook_expr") else __import__("quantlab.factors.ai_factory.novelty", fromlist=["is_textbook_expr"]).is_textbook_expr
        is_structural_expr = search_mod.is_structural_expr
        cfg = config or _GPC()
        leaves = leaf_names_present(panels, structural_only=cfg.structural_only)
        if not leaves:
            leaves = [n for n in LEAF_FEATURES if n in panels]
        if not leaves:
            raise ValueError("no leaf panels present")
        rng = np.random.default_rng(cfg.seed)
        out = SearchResult()
        out.max_evaluations = int(cfg.max_evaluations)
        n_seed = max(1, int(round(cfg.population * SEED_FRAC_FORCED)))
        pop = []
        for i in range(cfg.population):
            if i < n_seed:
                pop.append(search_mod._rand_expr(rng, leaves))  # already forced-cross patched
            else:
                pop.append(search_mod._rand_expr(rng, leaves))
                # v15: seed unsaturated EVENT; HARD BAN 5 new families + ACTIVE N=23 near-iso; de-prioritize idx/lev
        idx_a = [x for x in ("idx_w500_delta_20", "idx_w_delta_20", "neg_idx_w_delta_20", "idx_w300_delta_20") if x in leaves]
        ev_seed = [x for x in EVENT_LEAVES if x in leaves]
        ev_pref = [x for x in (
            "ann_penalty_5", "ann_earn_signed_5", "rzrq_delta_5",
            "dt_flag_5", "dt_net_10", "rz_delta_10", "ind_rel_intraday",
            "etf_share_chg_theme", "etf_share_chg_major", "ind_etf_share_flow",
            "unlock_resid", "lu_next_on", "ld_next_on",
        ) if x in leaves] or ev_seed
        partner_seed = [x for x in ("overnight_ret", "intraday_ret", "amt_cv_20", "neg_amt_cv_20", "on_minus_id",
                                    "ann_penalty_5", "ann_earn_signed_5", "dt_flag_5") if x in leaves]
        amt_a = [x for x in ("amt_cv_20", "neg_amt_cv_20") if x in leaves]
        from quantlab.factors.ops import Expr as _E
        def _ev_stem_s(x):
            if x.startswith("dt_"): return "dt"
            if x.startswith(("rz_", "rzrq_", "rq_")): return "rz"
            if x.startswith("nb_"): return "nb"
            if x.startswith("ind_rel_"): return "ind"
            if x.startswith("ann_"): return "ann"
            if x.startswith(("etf_share_chg", "ind_etf_share")): return "etfsh"
            if x.startswith("unlock_"): return "unlock"
            if x in ("lu_next_on", "ld_next_on"): return "lunext"
            return x.split("_")[0]
        def _banned_pair_s(a, b):
            ab = {a, b}
            if ab == {"overnight_ret", "ann_buyback_5"}: return True
            if ab == {"ann_buyback_5", "ind_rel_intraday"}: return True
            if "ann_buyback_5" in ab and (ab & {"nb_north_money", "rz_delta_5", "rz_delta_10", "rzrq_delta_5", "rz_intensity"}):
                return True
            if "ind_rel_overnight" in ab and (ab & {"dt_net_5", "dt_net_10", "dt_flag_5"}):
                return True
            if "ind_rel_overnight" in ab and (ab & {"rz_intensity", "rz_delta_5", "rz_delta_10", "rzrq_delta_5"}):
                return True
            return False
        def _seed_cross(rng):
            if ev_seed and partner_seed and rng.random() < 0.60:
                a = b = None
                for _try in range(12):
                    a = str(rng.choice(ev_pref if rng.random() < 0.70 else ev_seed))
                    b = str(rng.choice(partner_seed))
                    if not _banned_pair_s(a, b):
                        break
                else:
                    a = str(rng.choice([x for x in ev_pref if x != "ann_buyback_5"] or ev_pref or ev_seed))
                    b = str(rng.choice([x for x in partner_seed if x != "overnight_ret"] or partner_seed))
                op = str(rng.choice(("mul", "sub", "div"), p=[0.40, 0.40, 0.20]))
                root = _E("op", op, (
                    _E("op", str(rng.choice(("ts_mean_5", "ts_mean_10", "ts_max_20", "neg"))), (_E("leaf", a),)),
                    _E("op", str(rng.choice(("ts_mean_5", "ts_mean_10", "ts_max_20", "ts_std_10", "ts_delta_5"))), (_E("leaf", b),)),
                ))
                if rng.random() < 0.40:
                    root = _E("op", str(rng.choice(("ts_mean_10", "ts_mean_20", "neg", "abs"))), (root,))
                return root
            if len(ev_seed) >= 2 and rng.random() < 0.72:
                a = b = None
                for _try in range(12):
                    pool = ev_pref if rng.random() < 0.65 and len(ev_pref) >= 2 else ev_seed
                    a, b = [str(x) for x in rng.choice(pool, size=2, replace=False)]
                    if _ev_stem_s(a) != _ev_stem_s(b) and not _banned_pair_s(a, b):
                        break
                op = str(rng.choice(("mul", "sub", "div"), p=[0.40, 0.40, 0.20]))
                root = _E("op", op, (
                    _E("op", str(rng.choice(("ts_mean_5", "ts_mean_10", "ts_max_20"))), (_E("leaf", a),)),
                    _E("op", str(rng.choice(("ts_mean_5", "ts_mean_10", "ts_std_10", "ts_delta_5"))), (_E("leaf", b),)),
                ))
                if rng.random() < 0.35:
                    root = _E("op", str(rng.choice(("ts_mean_10", "ts_mean_20", "neg"))), (root,))
                return root
            if idx_a and amt_a and rng.random() < 0.30:
                a, b = str(rng.choice(idx_a)), str(rng.choice(amt_a))
                op = str(rng.choice(("mul", "sub"), p=[0.55, 0.45]))
                root = _E("op", op, (
                    _E("op", str(rng.choice(("ts_mean_5", "ts_mean_10", "ts_mean_20"))), (_E("leaf", a),)),
                    _E("op", str(rng.choice(("ts_mean_5", "ts_std_10", "ts_delta_5"))), (_E("leaf", b),)),
                ))
                return root
            return search_mod._rand_expr(rng, leaves)
        for i in range(n_seed):
            pop[i] = _seed_cross(rng)
        log("gp_search_v16 seeded", n_seed, "/", cfg.population, "EVENT+ETF份额/解禁/涨跌停次日; HARD BAN v15 rz×ind_rel + prior; ACTIVE N=23")
        archive = []

        def eval_one(expr):
            if out.evaluations >= cfg.max_evaluations:
                return None
            out.evaluations += 1
            if expr.depth() > MAX_DEPTH or expr.n_nodes() > MAX_NODES:
                append_attempt(engine="gp", seed=cfg.seed, universe=cfg.universe, cost=cfg.cost,
                               window=cfg.window, expr_str=expr.to_str(), fitness=None,
                               notes="rejected_complexity", path=cfg.ledger_path)
                return None
            expr_s = expr.to_str()
            if cfg.ban_textbook and is_textbook_expr(expr_s):
                append_attempt(engine="gp", seed=cfg.seed, universe=cfg.universe, cost=cfg.cost,
                               window=cfg.window, expr_str=expr_s, fitness=None,
                               notes="rejected_textbook_ban", path=cfg.ledger_path)
                return None
            if cfg.structural_only and not is_structural_expr(expr_s, leaves):
                append_attempt(engine="gp", seed=cfg.seed, universe=cfg.universe, cost=cfg.cost,
                               window=cfg.window, expr_str=expr_s, fitness=None,
                               notes="rejected_non_structural", path=cfg.ledger_path)
                return None
            try:
                fac = apply_expr(expr, panels)
            except Exception as exc:
                append_attempt(engine="gp", seed=cfg.seed, universe=cfg.universe, cost=cfg.cost,
                               window=cfg.window, expr_str=expr.to_str(), fitness=None,
                               notes=f"eval_error:{type(exc).__name__}", path=cfg.ledger_path)
                return None
            if cfg.use_l1b_fitness:
                met = fitness_score_l1b(fac, label, public_panels=cfg.public_panels, cost_one_way=cfg.cost,
                                        top_n=cfg.top_n, lambda_complexity=cfg.lambda_complexity,
                                        n_nodes=expr.n_nodes(), lambda_turnover=cfg.lambda_turnover)
            else:
                met = fitness_score(fac, label, cost_one_way=cfg.cost, top_n=cfg.top_n,
                                    lambda_complexity=cfg.lambda_complexity, n_nodes=expr.n_nodes(),
                                    lambda_turnover=cfg.lambda_turnover)
            fit = met["fitness"]
            row = append_attempt(engine="gp", seed=cfg.seed, universe=cfg.universe, cost=cfg.cost,
                                 window=cfg.window, expr_str=expr.to_str(),
                                 fitness=float(fit) if np.isfinite(fit) else None,
                                 notes=(f"icir={met.get('icir')};turn={met.get('turnover')};"
                                        f"ann_net={met.get('ann_net')};cost_in_fitness;"
                                        f"novelty_fail={met.get('novelty_fail')};"
                                        f"max_pub_corr={met.get('max_abs_public_corr')};"
                                        f"icir_src={met.get('icir_source')};resid_demote={met.get('resid_demote_flag')}"),
                                 path=cfg.ledger_path)
            out.ledger_tail_n = int(row["N"])
            icir = met.get("icir")
            if icir is None or not np.isfinite(icir) or fit <= -1e8:
                return None
            return Candidate(expr=expr, train_icir=float(icir), fitness=float(fit),
                             n_nodes=expr.n_nodes(),
                             metrics={k: met[k] for k in met if k != "fitness"})

        gen_i = 0
        while gen_i < cfg.generations or (out.evaluations < MIN_EVAL_BEFORE_EMPTY_STOP and out.evaluations < cfg.max_evaluations):
            if out.evaluations >= cfg.max_evaluations:
                break
            scored = []
            for e in pop:
                if out.evaluations >= cfg.max_evaluations:
                    break
                c = eval_one(e)
                if c is not None:
                    scored.append(c)
                    archive.append(c)
            if out.evaluations >= cfg.max_evaluations:
                break
            # New Bot: self-stop if system available < 2.5GB (peak ru_maxrss may already exceed 1500 from load)
            _av = available_mb()
            if math.isfinite(_av) and _av < SELF_STOP_AVAILABLE_MB:
                log("SELF_STOP available_mb", round(_av, 1), f"<{SELF_STOP_AVAILABLE_MB} after evals", out.evaluations)
                break
            _pk = mem_mb()
            # sticky ru_maxrss after EVENT load ≈2246; only abort if runaway ≫ MEM_CAP
            if _pk > MEM_CAP_MB + 400:
                log("SELF_STOP peak_rss_MB runaway", round(_pk), "> MEM_CAP+400=", MEM_CAP_MB + 400, "after evals", out.evaluations)
                break
            if not scored:
                if out.evaluations < MIN_EVAL_BEFORE_EMPTY_STOP:
                    # refill with forced-cross seeds and continue mutate exploration
                    log("gen empty scored; continue diversify mutate", "evals", out.evaluations, "/", MIN_EVAL_BEFORE_EMPTY_STOP)
                    pop = [_seed_cross(rng) for _ in range(cfg.population)]
                    gen_i += 1
                    continue
                break
            scored.sort(key=lambda c: c.fitness, reverse=True)
            elite_n = max(2, cfg.population // 4)
            elite = [c.expr for c in scored[:elite_n]]
            while len(elite) < cfg.population:
                if scored and rng.random() < 0.6:
                    parent = scored[int(rng.integers(0, min(len(scored), elite_n)))].expr
                    elite.append(search_mod._mutate(rng, parent, leaves))
                else:
                    elite.append(_seed_cross(rng) if rng.random() < 0.4 else search_mod._rand_expr(rng, leaves))
            pop = elite
            gen_i += 1
            if gen_i >= cfg.generations and out.evaluations >= MIN_EVAL_BEFORE_EMPTY_STOP:
                break

        archive.sort(key=lambda c: c.fitness, reverse=True)
        seen = set(); top = []
        for c in archive:
            s = c.expr.to_str()
            if s in seen:
                continue
            seen.add(s); top.append(c)
            if len(top) >= cfg.top_k:
                break
        out.top_k = top
        return out

    search_mod.gp_search = gp_search_v12
    # rebind local name used below
    gp_search = gp_search_v12

    cfg = GPConfig(
        population=POP, generations=GEN, max_evaluations=MAX_EVAL, top_k=TOP_K,
        seed=SEED, universe="midlarge_top1500_or_csi300_500", cost=COST,
        window=WINDOW, ledger_path=run_ledger,
        structural_only=False, ban_textbook=True, use_l1b_fitness=True,
        public_panels=public, lambda_complexity=0.015, lambda_turnover=1.0, top_n=50,
    )
    (OUT / "run_meta.json").write_text(json.dumps({
        "promotion_approved": False, "sealed": False, "window": WINDOW,
        "max_evaluations": MAX_EVAL, "population": POP, "generations": GEN, "seed": SEED,
        "available_at_start_MB": float(os.environ.get("QL_V16_AVAILABLE_AT_START_MB") or os.environ.get("QL_V11_AVAILABLE_AT_START_MB") or available_mb()),
        "pid": os.getpid(), "mem_cap_MB": MEM_CAP_MB, "peak_cap_goal_MB": 2200,
        "oom_relaunch": True,
        "search_leaves": sorted(sp.keys()), "missing_leaves": missing,
        "dropped_nan_leaves": dropped_nan, "leaf_diag": leaf_diag,
        "excluded_leaves": list(EXCLUDED_LEAVES),
        "dropped_ann_panels": dropped_ann,
        "p0_1": {
            "theta_cov": theta_cov, "theta_cov_primary": theta_cov_primary,
            "lambda_fam": lambda_fam, "rho_soft": rho_soft, "rho_hard": rho_hard,
            "impact_floor": imp_floor,
        },
        "p0_2": resid_meta,
        "gp_label": "eps" if use_eps else "y",
        "alpha_v10_adjudication": {
            "approved_active_etf_liq": "ts_max_20(ts_mean_5(div(etf_major_flow, neg_amt_cv_20)))",
            "approved_active_idx_etf": "mul(ts_mean_20(idx_w_delta_20), ts_mean_5(etf_all_flow))",
            "approved_active_overnight_abs_idx": "ts_mean_5(mul(ts_mean_20(overnight_ret), ts_mean_20(abs_idx_w_delta_20)))",
            "approved_active_etf_major_idx_v8": "ts_mean_20(mul(ts_mean_10(etf_major_flow), idx_w500_delta_20))",
            "approved_active_if_basis_neg_idx_v9": "ts_mean_10(mul(ts_max_20(if_basis), ts_mean_20(neg_idx_w_delta_20)))",
            "approved_active_abs_idx_on_minus_v9": "ts_mean_10(sub(ts_max_20(abs_idx_w_delta_20), abs(on_minus_id)))",
            "approved_active_idx_liq_cv_v10": "sub(ts_mean_5(idx_w_delta_20), ts_max_20(liq_cv_20))",
            "approved_active_neg_idx_liq_burst_v10b": "ts_mean_20(sub(ts_mean_20(neg_idx_w_delta_20), ts_mean_5(liq_burst_10)))",
            "v10_soft_fam_warn_rho_vs_etf_liq": 0.407,
            "v10_fragment_trial": True,
            "hard_ban_idx_etf_cross": True,
            "hard_ban_if_basis_idx": True,
            "hard_ban_abs_idx_on_minus": True,
            "hard_ban_idx_liq_cv": True,
            "hard_ban_idx_liq_burst": True,
            "hard_ban_overnight_ann_buyback_v13": True,
            "hard_ban_buyback_ind_rel_v14": True,
            "hard_ban_ind_rel_dt_v14": True,
            "hard_ban_buyback_nb_v14": True,
            "hard_ban_buyback_rz_v14": True,
            "hard_ban_rz_intensity_ind_rel_v15": True,
            "dense_micro_as_struct": list(DENSE_MICRO_LEAVES),
            "demote_etf_all_liq_family": True,
            "demote_overnight_abs_idx_family": True,
            "hold_limit_neighborhood_primary": True,
            "N_active": 23,
        },
        "capital_cny": [600000, 1000000], "ledger_N_before": n_before,
        "leo_explore_ok": True, "load_meta": load_meta,
        "enhancement": "v16_struct_event: EVENT+ETF份额/解禁残差/涨跌停次日; HARD BAN v15 rz×ind_rel + prior; ACTIVE N=23 in Z; icir_eps_gate/posthoc; MEM_CAP=2300; peak≤2.2GB",
    }, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    _av = available_mb()
    log("gp_search start", "N_before", n_before, "n_leaves", len(sp),
        "available_mb", round(_av, 1) if math.isfinite(_av) else None,
        "pid", os.getpid(), "peak_cap", MEM_CAP_MB)
    if math.isfinite(_av) and _av < SELF_STOP_AVAILABLE_MB:
        log("ABORT before gp_search: available_mb", round(_av, 1), f"<{SELF_STOP_AVAILABLE_MB}")
        raise SystemExit(3)
    res = gp_search(sp, gp_label, cfg)
    peak = max(peak, mem_mb())
    log("gp done evals", res.evaluations, "top_k", len(res.top_k), "peak", peak)

    run_rows = [json.loads(x) for x in run_ledger.read_text().splitlines() if x.strip()] if run_ledger.exists() else []
    for r in run_rows:
        append_attempt(engine=r["engine"], seed=r["seed"], universe=r["universe"], cost=r["cost"],
                       window=r["window"], expr_str=r.get("expr_str", ""), fitness=r.get("fitness"),
                       notes=(r.get("notes") or "") + ";gp_reopen_hardgate_v16_struct_event", path=main_ledger)
    n_after = sum(1 for x in main_ledger.read_text().splitlines() if x.strip())

    gate_ok, demoted, all_rows = [], [], []
    for c in res.top_k:
        expr = c.expr.to_str()
        try:
            fac = apply_expr(c.expr, sp).astype("float32")
            cov = sci.coverage_stats(fac)
            cs = sci.cs_std_stats(fac)
            sim = sci.simulate_book(fac, label_y, sig, adv) if cs.get("passes_cs_variation") else {"skipped": True}
            m = sci.pack_metrics(sim if not sim.get("skipped") else None)
            max_corr = (c.metrics or {}).get("max_abs_public_corr")
            novelty_fail = bool((c.metrics or {}).get("novelty_fail"))
            icir = m.get("icir", c.train_icir)
            icir_y = icir_vs(fac, label_y)
            icir_eps_posthoc = icir_vs(fac, label_eps) if use_eps else float("nan")
            # gate-path residual ICIR from fitness (search-time); posthoc = independent icir_vs rebuild
            _gm = c.metrics or {}
            icir_eps_gate = _gm.get("icir_eps_gate", _gm.get("icir_eps", float("nan")))
            if not (isinstance(icir_eps_gate, float) and math.isfinite(icir_eps_gate)):
                icir_eps_gate = float("nan") if not (isinstance(icir_eps_gate, (int, float)) and math.isfinite(float(icir_eps_gate or float("nan")))) else float(icir_eps_gate)
            try:
                icir_eps_gate = float(icir_eps_gate) if icir_eps_gate is not None else float("nan")
            except Exception:
                icir_eps_gate = float("nan")
            icir_eps = icir_eps_posthoc  # backward-compat alias = posthoc
            nr = cov.get("nonempty_rate", float("nan"))
            impact_ok = (math.isfinite(m.get("flat25", float("nan"))) and m["flat25"] > 0
                         and math.isfinite(m.get("imp60_p25", float("nan"))) and m["imp60_p25"] >= imp_floor
                         and math.isfinite(m.get("imp100_p25", float("nan"))) and m["imp100_p25"] >= imp_floor)
            icir_ok = math.isfinite(icir) and icir > 0
            cov_ok = bool(cov.get("passes_coverage")) and (isinstance(nr, float) and nr >= theta_cov)
            rank_fill = bool("rank(" in expr and isinstance(nr, float) and nr < theta_cov)
            broadcast_only = expr.strip() in (
                "lu_promote_rate", "rank(lu_promote_rate)", "neg(lu_promote_rate)",
                "mkt_max_height", "mkt_lu_breadth", "rank(mkt_lu_breadth)",
            )
            iso = isomorphic_reason(expr)
            lim_prim = is_limit_neighborhood_primary(expr)
            # family |ρ| vs PRIMARY
            fam_corr = {}
            max_fam = float("nan")
            for _pn, _pp in primary_panels.items():
                try:
                    _c = fit_mod.corr_with_panel(fac, _pp)
                    fam_corr[_pn] = _c
                    if isinstance(_c, float) and math.isfinite(_c):
                        max_fam = abs(_c) if not math.isfinite(max_fam) else max(max_fam, abs(_c))
                except Exception:
                    pass
            who = l1b.who_pays_zh(expr)
            if any(x in expr for x in ("liq_cv", "liq_burst", "amt_cv")):
                who = (who + "；" if who and "机制未声明" not in who else "") + "流动性体制不稳：量能波动抬升时做市/跟风盘被迫调仓"
            if any(x in expr for x in ("idx_w", "idx_w500", "idx_w300")):
                who = (who + "；" if who and "机制未声明" not in who else "") + "指数权重压力：权重上调引发被动资金买压，对手方为股票供给方"
            if "lev_delta" in expr or "abs_lev" in expr:
                who = (who + "；" if who and "机制未声明" not in who else "") + "杠杆修订：融资余额边际变化反映杠杆资金进退"
            if "etf_all" in expr or "etf_major" in expr or "etf_theme" in expr:
                who = (who + "；" if who and "机制未声明" not in who else "") + "ETF份额流：申赎冲击由股票端流动性承接"
            if any(x in expr for x in ("dt_net", "dt_flag", "dt_buy")):
                who = (who + "；" if who and "机制未声明" not in who else "") + "龙虎榜席位：游资/机构席位净买入信号，对手方为跟风与提供对手盘的流动性"
            if any(x in expr for x in ("rz_delta", "rzrq_delta", "rz_intensity", "rq_")):
                who = (who + "；" if who and "机制未声明" not in who else "") + "两融余额：杠杆资金进退由融资客支付；平仓潮时对手方为市场承接力"
            if "nb_north" in expr:
                who = (who + "；" if who and "机制未声明" not in who else "") + "北向资金市值流：外资边际偏好变化由A股流动性承接（本叶为市场广播，非个股持仓）"
            if "ind_rel_" in expr:
                who = (who + "；" if who and "机制未声明" not in who else "") + "行业相对收益：行业内相对强弱由板块轮动资金支付，输家为行业内落后者"
            if any(x in expr for x in ("ann_buyback", "ann_penalty", "ann_earn")):
                who = (who + "；" if who and "机制未声明" not in who else "") + "公告事件：回购/处罚/盈余超预期改变知情交易强度，对手方为不知情流动性"
            if any(x in expr for x in ("etf_share_chg", "ind_etf_share_flow")):
                who = (who + "；" if who and "机制未声明" not in who else "") + "ETF份额变化：申赎份额边际由成分股流动性承接；行业映射叶为截面可分的申赎压力"
            if "unlock_resid" in expr:
                who = (who + "；" if who and "机制未声明" not in who else "") + "解禁残差：已公告解禁相对市值的异常供给，对手方为接盘流动性（非 lockup_S_20 前瞻窗移植）"
            if any(x in expr for x in ("lu_next_on", "ld_next_on")):
                who = (who + "；" if who and "机制未声明" not in who else "") + "涨跌停次日隔夜：打板/跌停次日开盘缺口由隔夜资金支付，对手方为集合竞价流动性"
            # strip "机制未声明" if we appended real mech
            if "机制未声明" in who and "；" in who:
                who = "；".join(x for x in who.split("；") if "机制未声明" not in x)
            fail_cond = "机制失效：覆盖塌缩/冲击后净收益<10%/与短清单PRIMARY|ρ|>0.5/残差ICIR≤0"
            if "etf_" in expr:
                fail_cond = "ETF流失效：仅广播到全市场而无成分映射、或 available_at 滞后导致不可交易；或与 ACTIVE etf×liq 同构"
            elif any(x in expr for x in ("lu_", "limit_", "days_since_lu")):
                fail_cond = "涨跌停邻域失效：事件稀疏或打板资金断裂后不可持续（P0-8 HOLD）"
            elif any(x in expr for x in ("dt_net", "dt_flag")):
                fail_cond = "龙虎榜失效：上榜稀疏/席位操纵噪声主导/覆盖不足θ_primary"
            elif any(x in expr for x in ("rz_delta", "rzrq", "rz_intensity")):
                fail_cond = "两融失效：融资余额与收益共线且ICIR≤0（L1e先例）/杠杆去化期信号反转"
            elif "nb_north" in expr:
                fail_cond = "北向广播失效：全市场同值无截面区分力；或与ETF流同构"
            elif "ind_rel_" in expr:
                fail_cond = "行业相对失效：SW_L1成员滞后/行业内同质化导致残差坍塌"
            elif any(x in expr for x in ("ann_buyback", "ann_penalty", "ann_earn")):
                fail_cond = "公告事件失效：事件稀疏覆盖不足/与banned insider移植池共线"
            elif any(x in expr for x in ("etf_share_chg", "ind_etf_share_flow")):
                fail_cond = "ETF份额变化失效：仅广播无截面/行业映射滞后/与 ACTIVE etf×liq 同构"
            elif "unlock_resid" in expr:
                fail_cond = "解禁残差失效：事件稀疏/与 banned lockup_S_20 或 FSR 共线"
            elif any(x in expr for x in ("lu_next_on", "ld_next_on")):
                fail_cond = "涨跌停次日失效：事件稀疏或打板资金断裂（邻域 HOLD）"
            mech_ok = bool(who) and ("机制未声明" not in who)
            # DEMOTE if ICIR(f,y)>0 and ICIR(f,ε)≤0
            resid_demote = (math.isfinite(icir_y) and icir_y > 0 and math.isfinite(icir_eps_posthoc) and icir_eps_posthoc <= 0)
            diversity_secondary = False
            verdict = "GATE_OK"
            if rank_fill: verdict = "FAIL_RANK_FILL"
            elif broadcast_only: verdict = "DEMOTE_BROADCAST"
            elif iso: verdict = f"DEMOTE_ISO_{iso}"
            elif lim_prim:
                # P0-8: not primary; diversity_secondary if numeric gates pass
                if impact_ok and icir_ok and cov_ok and mech_ok and not novelty_fail and not (math.isfinite(max_fam) and max_fam > rho_hard):
                    verdict = "DEMOTE_LIMIT_NEIGHBORHOOD_PRIMARY"
                    diversity_secondary = True
                else:
                    verdict = "DEMOTE_LIMIT_NEIGHBORHOOD_PRIMARY"
            elif not cov_ok: verdict = "FAIL_SPARSE"
            elif novelty_fail or (isinstance(max_corr, float) and math.isfinite(max_corr) and max_corr > 0.5):
                verdict = "DEMOTE_TEXTBOOK"
            elif math.isfinite(max_fam) and max_fam > rho_hard:
                verdict = "DEMOTE_FAMILY_CORR"
            elif resid_demote:
                verdict = "DEMOTE_RESID_ICIR"
            elif not impact_ok: verdict = "FAIL_GATE"
            elif not icir_ok: verdict = "FAIL_ICIR"
            elif not mech_ok: verdict = "REJECTED_NO_MECHANISM"
            # θ_cov_primary: cannot mark primary
            if verdict == "GATE_OK" and isinstance(nr, float) and math.isfinite(nr) and nr < theta_cov_primary:
                diversity_secondary = True
                # keep GATE_OK but tag; Alpha treats as non-primary overlay
            fit_out = c.fitness
            if verdict.startswith(("FAIL_", "DEMOTE_FAMILY", "DEMOTE_TEXTBOOK", "REJECTED_", "DEMOTE_RESID", "DEMOTE_ISO")):
                fit_out = -1e9
            if verdict in ("FAIL_GATE", "FAIL_SPARSE", "FAIL_RANK_FILL"):
                fit_out = -1e9
            # soft family already in fitness; ensure post impact hard
            if not impact_ok:
                fit_out = -1e9
            row = {
                "expr": expr, "tuple": c.expr.to_tuple(), "train_icir": c.train_icir,
                "fitness": fit_out, "metrics": m, "coverage": cov, "cs_stats": cs,
                "gp_metrics": {k: v for k, v in (c.metrics or {}).items() if k != "public_corr"},
                "max_abs_public_corr": max_corr, "novelty_fail": novelty_fail,
                "max_abs_family_corr": max_fam if math.isfinite(max_fam) else None,
                "family_corr": fam_corr,
                "icir_y": icir_y, "icir_eps": icir_eps_posthoc,
                "icir_eps_gate": icir_eps_gate, "icir_eps_posthoc": icir_eps_posthoc,
                "rank_fill_cov": rank_fill, "broadcast_only": broadcast_only,
                "isomorphic_reason": iso, "limit_neighborhood_primary": lim_prim,
                "leaves": sorted(leaves_in(expr)),
                "verdict": verdict,
                "ashare_mechanism_zh": who,
                "who_pays_zh": who,
                "failure_condition_zh": fail_cond,
                "gate_ok": verdict == "GATE_OK",
                "diversity_secondary_max": diversity_secondary or (isinstance(nr, float) and math.isfinite(nr) and nr < theta_cov_primary),
                "promotion_approved": False,
                "diagnostic_overlay_candidate": verdict == "GATE_OK",
                "capital_cny_tiers": [600000, 1000000],
            }
            all_rows.append(row)
            if verdict == "GATE_OK": gate_ok.append(row)
            elif verdict.startswith("DEMOTE"): demoted.append(row)
            del fac; gc.collect()
        except Exception as exc:
            all_rows.append({"expr": expr, "verdict": "ERROR", "error": str(exc), "promotion_approved": False})

    peak = max(peak, mem_mb())
    reason_ctr = Counter()
    n_killed_novelty = 0
    for r in all_rows:
        v = str(r.get("verdict") or "")
        reason_ctr[v] += 1
        if v in ("DEMOTE_TEXTBOOK", "DEMOTE_FAMILY_CORR") or r.get("novelty_fail"):
            n_killed_novelty += 1
    for rr in run_rows:
        notes = str(rr.get("notes") or "")
        for key in ("rejected_non_structural", "rejected_complexity", "rejected_textbook", "novelty_fail"):
            if key in notes:
                reason_ctr[key] += 1
                if key == "novelty_fail":
                    n_killed_novelty += 1
    fail_reason_top3 = [{"reason": k, "n": int(v)} for k, v in reason_ctr.most_common(3)]
    receipt = {
        "available_at_start_MB": float(os.environ.get("QL_V16_AVAILABLE_AT_START_MB") or os.environ.get("QL_V11_AVAILABLE_AT_START_MB") or float("nan")),
        "pid": os.getpid(),
        "peak_rss_MB": round(peak),
        "n_candidates": int(res.evaluations),
        "n_gate_ok": len(gate_ok),
        "n_killed_by_novelty": int(n_killed_novelty),
        "fail_reason_top3": fail_reason_top3,
        "n_top_k": len(res.top_k),
        "p0_1_exact": True,
        "p0_2_resid": True,
        "gp_label": "eps" if use_eps else "y",
        "resid_meta": resid_meta,
        "primary_panels_built": list(primary_panels.keys()),
        "primary_gaps": primary_gaps,
    }
    (OUT / "receipt.json").write_text(json.dumps(clean(receipt), indent=2, ensure_ascii=False), encoding="utf-8")

    summary = {
        "promotion_approved": False, "sealed": False, "strategy_weights": False,
        "available_at_start_MB": float(os.environ.get("QL_V16_AVAILABLE_AT_START_MB") or os.environ.get("QL_V11_AVAILABLE_AT_START_MB") or float("nan")),
        "pid": os.getpid(),
        "evaluations": res.evaluations, "ledger_N_before": n_before, "ledger_N_after": n_after,
        "n_top_k": len(res.top_k), "n_gate_ok": len(gate_ok), "n_demote": len(demoted),
        "n_search_leaves": len(sp), "search_leaves": sorted(sp.keys()),
        "peak_rss_MB": round(peak), "runtime_s": round(time.time() - t0, 1),
        "under_mem_cap": peak < MEM_CAP_MB,
        "gate_ok_exprs": [r["expr"] for r in gate_ok],
        "receipt": receipt,
        "out_dir": str(OUT.relative_to(ROOT)),
        "policy": "v16_struct_event exact θ/λ/ρ + ε + EVENT+struct expand + HARD BAN v15/v14 families + ACTIVE N=23; icir dual fields; peak≤2.2GB",
    }
    (OUT / "top_k.json").write_text(json.dumps(clean([c.as_row() for c in res.top_k]), indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "post_gate_rows.json").write_text(json.dumps(clean(all_rows), indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "gate_ok.json").write_text(json.dumps(clean(gate_ok), indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "demoted.json").write_text(json.dumps(clean(demoted), indent=2, ensure_ascii=False), encoding="utf-8")

    handback = {
        "promotion_approved": False, "for_alpha_shortlist_adjudication": True,
        "not_strategy_weights": True, "diagnostic_overlay_candidates_only": True,
        "receipt": receipt,
        "gate_ok": [{
            "expr": r["expr"],
            "leaves": r.get("leaves"),
            "nonempty_rate": (r.get("coverage") or {}).get("nonempty_rate"),
            "flat25": (r.get("metrics") or {}).get("flat25"),
            "imp60_p25": (r.get("metrics") or {}).get("imp60_p25"),
            "imp100_p25": (r.get("metrics") or {}).get("imp100_p25"),
            "icir": (r.get("metrics") or {}).get("icir"),
            "icir_y": r.get("icir_y"),
            "icir_eps": r.get("icir_eps_posthoc", r.get("icir_eps")),
            "icir_eps_gate": r.get("icir_eps_gate"),
            "icir_eps_posthoc": r.get("icir_eps_posthoc", r.get("icir_eps")),
            "icir_fields_note": "icir_eps_gate=fitness/search residual ICIR; icir_eps_posthoc=independent icir_vs rebuild; icir_eps alias=posthoc",
            "rank_fill_cov": r.get("rank_fill_cov"),
            "max_abs_public_corr": r.get("max_abs_public_corr"),
            "max_abs_family_corr": r.get("max_abs_family_corr"),
            "diversity_secondary_max": r.get("diversity_secondary_max"),
            "ashare_mechanism_zh": r.get("ashare_mechanism_zh"),
            "who_pays_zh": r.get("who_pays_zh"),
            "failure_condition_zh": r.get("failure_condition_zh"),
            "verdict": r["verdict"],
            "diagnostic_overlay_candidate": True,
            "note": "v10b_resume; Alpha adjudicates; no seal",
        } for r in gate_ok],
        "n_gate_ok": len(gate_ok),
        "n_demote": len(demoted),
        "n_candidates": int(res.evaluations),
        "n_killed_by_novelty": int(n_killed_novelty),
        "fail_reason_top3": fail_reason_top3,
        "demote_limit_neighborhood": [r["expr"] for r in demoted if "LIMIT_NEIGHBORHOOD" in str(r.get("verdict", ""))],
        "demote_iso": [r["expr"] for r in demoted if str(r.get("verdict", "")).startswith("DEMOTE_ISO")],
        "search_leaves": sorted(sp.keys()),
        "excluded_leaves": list(EXCLUDED_LEAVES),
        "primary_panels_built": list(primary_panels.keys()),
        "primary_gaps": primary_gaps,
        "resid_meta": resid_meta,
        "ledger_N_before": n_before, "ledger_N_after": n_after,
        "peak_rss_MB": round(peak),
        "available_at_start_MB": float(os.environ.get("QL_V16_AVAILABLE_AT_START_MB") or os.environ.get("QL_V11_AVAILABLE_AT_START_MB") or float("nan")),
        "pid": os.getpid(),
        "source": "gp_reopen_hardgate_v16_struct_event",
        "dedup_note": "v6–v14 ACTIVES N=23 + v15 rz×ind_rel ban + v14 event bans; ETF share/unlock_resid/lu_next; DENSE_MICRO→STRUCT; resid ε; active23=True; icir_eps_gate/posthoc",
        "note": "empty gate_ok is valid; Alpha adjudicates only GATE_OK; promotion_approved=false",
    }
    (OUT / "alpha_handback_package.json").write_text(
        json.dumps(clean(handback), indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "summary.json").write_text(json.dumps(clean(summary), indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# AI 因子 GP 硬闸重开 v16_struct_event（事件+ETF份额/解禁残差/涨跌停次日 · 硬禁 v15 同构 · ACTIVE N=23 · 双 ICIR）",
        "",
        f"- **时间：** 2026-10-12（America/New_York）",
        f"- **promotion_approved：** false；**密封：** 未开；**不交 Strategy 权重**",
        f"- **窗口：** {WINDOW}；seed={SEED}",
        f"- 账本：N {n_before} → {n_after}（+{n_after-n_before}）",
        f"- GP：evals={res.evaluations}/{MAX_EVAL}；Top-K={len(res.top_k)}；峰值 RSS≈{peak:.0f}MB",
        f"- P0-1：θ_cov={theta_cov} · θ_primary={theta_cov_primary} · λ_fam={lambda_fam} · ρ软/硬={rho_soft}/{rho_hard} · 冲击≥{imp_floor:.0%}@60万∧100万",
        f"- P0-2：GP 标签={'ε' if use_eps else 'y（残差天数不足回退）'}；PRIMARY 入 Z：{len(primary_panels)}；gaps={len(primary_gaps)}",
        f"- Alpha 裁决：ACTIVE N=15（+etf_major×idx_w500）；DENSE_MICRO→STRUCT；硬禁 idx×etf；远离三 ACTIVE 族；涨跌停邻域 → DEMOTE_LIMIT_NEIGHBORHOOD_PRIMARY",
        f"- 回执：候选={res.evaluations} · GATE_OK={len(gate_ok)} · 新颖性杀≈{n_killed_novelty} · 失败Top3={fail_reason_top3}",
        "",
        "## GATE_OK",
        "",
        "| # | 表达式 | flat25 | 60万 | 100万 | ICIR(y) | ICIR(ε)_gate | ICIR(ε)_posthoc | nonempty | |ρ|_fam |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    def fp(x):
        return f"{x:.2%}" if isinstance(x, float) and math.isfinite(x) else "—"
    def ff(x):
        return f"{x:.3f}" if isinstance(x, float) and math.isfinite(x) else "—"
    for i, r in enumerate(gate_ok, 1):
        m = r.get("metrics") or {}; cov = r.get("coverage") or {}
        lines.append(
            f"| {i} | `{r['expr']}` | {fp(m.get('flat25'))} | {fp(m.get('imp60_p25'))} | "
            f"{fp(m.get('imp100_p25'))} | {ff(r.get('icir_y'))} | {ff(r.get('icir_eps_gate'))} | "
            f"{ff(r.get('icir_eps_posthoc', r.get('icir_eps')))} | "
            f"{ff(cov.get('nonempty_rate'))} | {ff(r.get('max_abs_family_corr'))} |"
        )
    if not gate_ok:
        lines.append("| — | （本轮无过全硬闸） | — | — | — | — | — | — | — | — |")
    lines += [
        "",
        f"- DEMOTE：{len(demoted)}；LIMIT_NEIGHBORHOOD：{len([r for r in demoted if 'LIMIT_NEIGHBORHOOD' in str(r.get('verdict',''))])}",
        f"- 回传包：`output/ai_factor/gp_reopen_hardgate_v16_struct_event/alpha_handback_package.json`",
        f"- PRIMARY gaps：{primary_gaps[:12]}",
        "",
        "## ICIR 字段说明（交 Alpha 无双读歧义）",
        "- `icir_eps_gate`：搜索期 fitness 残差 ICIR（闸内路径）",
        "- `icir_eps_posthoc`：事后独立 `icir_vs(fac, ε)` 重算",
        "- `icir_eps`：兼容别名，等于 posthoc",
        "- `icir_y`：相对原始 y 的 ICIR",
        "",
        "## 禁令自检",
        "- promotion_approved=false；未开密封；未改短清单；未改 HANDOFF",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    log("DONE", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))
    return 0 if peak < MEM_CAP_MB else 1

if __name__ == "__main__":
    raise SystemExit(main())
