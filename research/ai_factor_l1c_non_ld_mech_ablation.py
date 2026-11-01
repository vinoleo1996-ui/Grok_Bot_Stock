#!/usr/bin/env python3
"""L1c non-LD front-rank mechanism + ablation (explore).

promotion_approved=False. No sealed. No Strategy weight. No small-cap.
Announcements title_only. Memory < 2.5GB.
"""
from __future__ import annotations

import gc
import importlib.util
import json
import math
import re
import resource
import sys
import time
import types
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/workspace/QuantLab")
SCRATCH = Path("/workspace/scratch/tic")
GATE_DIR = ROOT / "output/ai_factor/l1c_cs_variation_gate"
OUT_DIR = ROOT / "output/ai_factor/l1c_non_ld_mech_ablation"
REPORT = ROOT / "output/alpha/AI_FACTOR_L1c_NON_LD_MECH_ABLATION_ZH.md"
EXPLORE_START = pd.Timestamp("2024-06-03")
LOOKBACK_START = pd.Timestamp("2024-01-02")
TOP_N = 50
K_IMP = 1.0
AUMS = (600_000.0, 1_000_000.0)
FLAT_BPS = (10, 25)
COMMISSION_ONE_WAY = 0.00025
PROMOTION_APPROVED = False
MEM_CAP_MB = 2500
CS_STD_MIN = 1e-8
SEED = 20261012
IMP60_FLOOR = 0.12  # ≥12% net @60万 (impact+flat25)

OPS = {
    "add", "sub", "mul", "div", "neg", "abs", "rank", "zscore",
    "industry_neutral", "size_neutral",
}
for k in (1, 5, 10, 20):
    OPS |= {f"delay_{k}", f"ts_mean_{k}", f"ts_std_{k}", f"ts_delta_{k}", f"ts_max_{k}"}

t0 = 0.0


def mem_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def log(*a):
    print(f"[l1c_non_ld {time.time()-t0:5.0f}s {mem_mb():.0f}MB]", *a, flush=True)


def leaves_in(expr: str) -> set[str]:
    return {t for t in re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", expr) if t not in OPS}


def is_ld_leaf(name: str) -> bool:
    return name.startswith("limit_down_") or name.startswith("ld_") or name == "days_since_ld"


def is_ld_only_expr(expr: str) -> bool:
    L = leaves_in(expr)
    return bool(L) and all(is_ld_leaf(x) for x in L)


def to_nested_tuple(obj):
    if isinstance(obj, list):
        return tuple(to_nested_tuple(x) for x in obj)
    return obj


def _seed_to_tuple(s: str):
    s = s.strip()
    if s.isidentifier():
        return ("leaf", s)
    m = re.fullmatch(r"neg\((.+)\)", s)
    if m:
        return ("op", "neg", _seed_to_tuple(m.group(1)))
    m = re.fullmatch(r"rank\((.+)\)", s)
    if m:
        return ("op", "rank", _seed_to_tuple(m.group(1)))
    m = re.fullmatch(r"zscore\((.+)\)", s)
    if m:
        return ("op", "zscore", _seed_to_tuple(m.group(1)))
    m = re.fullmatch(r"abs\((.+)\)", s)
    if m:
        return ("op", "abs", _seed_to_tuple(m.group(1)))
    m = re.fullmatch(r"delay_(\d+)\((.+)\)", s)
    if m:
        return ("op", f"delay_{m.group(1)}", _seed_to_tuple(m.group(2)))
    m = re.fullmatch(r"ts_std_(\d+)\((.+)\)", s)
    if m:
        return ("op", f"ts_std_{m.group(1)}", _seed_to_tuple(m.group(2)))
    m = re.fullmatch(r"ts_delta_(\d+)\((.+)\)", s)
    if m:
        return ("op", f"ts_delta_{m.group(1)}", _seed_to_tuple(m.group(2)))
    m = re.fullmatch(r"ts_max_(\d+)\((.+)\)", s)
    if m:
        return ("op", f"ts_max_{m.group(1)}", _seed_to_tuple(m.group(2)))
    m = re.fullmatch(r"ts_mean_(\d+)\((.+)\)", s)
    if m:
        return ("op", f"ts_mean_{m.group(1)}", _seed_to_tuple(m.group(2)))
    m = re.fullmatch(r"mul\((.+),(.+)\)", s)
    if m:
        return ("op", "mul", _seed_to_tuple(m.group(1).strip()), _seed_to_tuple(m.group(2).strip()))
    m = re.fullmatch(r"add\((.+),(.+)\)", s)
    if m:
        return ("op", "add", _seed_to_tuple(m.group(1).strip()), _seed_to_tuple(m.group(2).strip()))
    m = re.fullmatch(r"sub\((.+),(.+)\)", s)
    if m:
        return ("op", "sub", _seed_to_tuple(m.group(1).strip()), _seed_to_tuple(m.group(2).strip()))
    m = re.fullmatch(r"div\((.+),(.+)\)", s)
    if m:
        return ("op", "div", _seed_to_tuple(m.group(1).strip()), _seed_to_tuple(m.group(2).strip()))
    raise ValueError(f"cannot parse: {s}")


def ann_from_daily(rets: np.ndarray) -> dict:
    r = rets[np.isfinite(rets)]
    if len(r) < 20:
        return {"ann": float("nan"), "sharpe": float("nan"), "mdd": float("nan"), "n": int(len(r))}
    nav = np.cumprod(1.0 + r)
    years = len(r) / 244.0
    cagr = float(nav[-1] ** (1.0 / years) - 1.0) if years > 0 and nav[-1] > 0 else float("nan")
    sd = float(r.std(ddof=1))
    sh = float(r.mean() / sd * math.sqrt(244)) if sd > 1e-12 else float("nan")
    peak = np.maximum.accumulate(nav)
    mdd = float((nav / peak - 1.0).min())
    return {"ann": cagr, "sharpe": sh, "mdd": mdd, "n": int(len(r))}


def simulate_book(factor, label, sig, adv, *, top_n=TOP_N):
    from quantlab.factors.ai_factory.fitness import daily_rank_ic, icir_from_series

    idx = factor.index.intersection(label.index)
    idx = idx[idx >= EXPLORE_START]
    f = factor.reindex(idx).to_numpy(dtype=np.float64, copy=False)
    y = label.reindex(idx).to_numpy(dtype=np.float64, copy=False)
    s = sig.reindex(idx).to_numpy(dtype=np.float64, copy=False)
    a = adv.reindex(idx).to_numpy(dtype=np.float64, copy=False)
    T = len(idx)
    gross = np.full(T, np.nan)
    turn_ow = np.full(T, np.nan)
    imp_frac = {aum: np.full(T, np.nan) for aum in AUMS}
    prev = None
    for t in range(T):
        ft, yt = f[t], y[t]
        m = np.isfinite(ft) & np.isfinite(yt)
        n_ok = int(m.sum())
        k = min(top_n, n_ok)
        if k < max(5, top_n // 5):
            continue
        ii = np.nonzero(m)[0]
        vals = ft[ii]
        part = np.argpartition(vals, -k)[-k:]
        cur_idx = ii[part]
        cur = set(cur_idx.tolist())
        gross[t] = float(yt[cur_idx].mean())
        if prev is None:
            turn_ow[t] = 1.0
            entered, exited = cur, set()
        else:
            entered, exited = cur - prev, prev - cur
            turn_ow[t] = len(cur.symmetric_difference(prev)) / (2.0 * k)
        w = 1.0 / k
        for aum in AUMS:
            cost_cny = 0.0
            for j in exited | entered:
                V = w * aum
                cost_cny += COMMISSION_ONE_WAY * V
                sj, aj = s[t, j], a[t, j]
                if np.isfinite(sj) and np.isfinite(aj) and aj > 0 and V > 0:
                    cost_cny += V * K_IMP * float(sj) * math.sqrt(V / aj)
            imp_frac[aum][t] = cost_cny / aum
        prev = cur

    out = {
        "gross": ann_from_daily(gross),
        "mean_turn_ow": float(np.nanmean(turn_ow)),
        "n_days": int(np.isfinite(gross).sum()),
        "flat": {},
        "impact": {},
        "promotion_approved": False,
    }
    for bp in FLAT_BPS:
        out["flat"][str(bp)] = ann_from_daily(gross - turn_ow * (bp / 1e4))
    for aum in AUMS:
        key = str(int(aum))
        out["impact"][key] = ann_from_daily(gross - imp_frac[aum])
        for bp in FLAT_BPS:
            extra = max(0.0, bp / 1e4 - COMMISSION_ONE_WAY)
            out["impact"][f"{key}_plus_flat{bp}"] = ann_from_daily(
                gross - imp_frac[aum] - turn_ow * extra
            )
    ics = daily_rank_ic(factor.reindex(idx), label.reindex(idx))
    out["ic_mean"] = float(np.nanmean(ics.to_numpy()))
    out["icir"] = float(icir_from_series(ics))
    return out


def load_sig_adv(cols, index):
    cl = pd.read_parquet(SCRATCH / "close.parquet", columns=cols).astype("float32")
    cl = cl.loc[cl.index >= LOOKBACK_START]
    fa = pd.read_parquet(SCRATCH / "factor.parquet", columns=cols).astype("float32")
    fa = fa.loc[fa.index >= LOOKBACK_START].ffill()
    aC = (cl * fa).astype("float32")
    del cl, fa
    gc.collect()
    ret = aC.pct_change(fill_method=None)
    sig = ret.rolling(20, min_periods=10).std().astype("float32")
    del aC, ret
    gc.collect()
    amt = pd.read_parquet(SCRATCH / "amount.parquet", columns=cols).astype("float32")
    amt = amt.loc[amt.index >= LOOKBACK_START]
    adv = amt.rolling(20, min_periods=10).mean().astype("float32")
    del amt
    gc.collect()
    return sig.reindex(index=index, columns=cols), adv.reindex(index=index, columns=cols)


def cs_std_stats(fac: pd.DataFrame) -> dict:
    sample = fac.loc[fac.index >= EXPLORE_START]
    daily_std = sample.std(axis=1, skipna=True)
    daily_nuniq = sample.nunique(axis=1, dropna=True)
    mean_std = float(daily_std.mean())
    frac_near_zero = float((daily_std.fillna(0) < CS_STD_MIN).mean())
    frac_const = float((daily_nuniq.fillna(1) <= 1).mean())
    return {
        "cs_std_mean": mean_std,
        "cs_std_median": float(daily_std.median()),
        "frac_days_near_zero_std": frac_near_zero,
        "frac_days_constant_cs": frac_const,
        "passes_cs_variation": bool(
            mean_std > CS_STD_MIN and frac_near_zero < 0.5 and frac_const < 0.5
        ),
    }


def size_residualize(fac: pd.DataFrame, size: pd.DataFrame) -> pd.DataFrame:
    """Cheap daily OLS residual vs [1, size]. Memory-friendly row loop on numpy."""
    idx = fac.index.intersection(size.index)
    cols = [c for c in fac.columns if c in size.columns]
    F = fac.reindex(index=idx, columns=cols).to_numpy(dtype=np.float64, copy=False)
    S = size.reindex(index=idx, columns=cols).to_numpy(dtype=np.float64, copy=False)
    out = np.full_like(F, np.nan)
    for t in range(F.shape[0]):
        y = F[t]
        x = S[t]
        m = np.isfinite(y) & np.isfinite(x)
        n = int(m.sum())
        if n < 30:
            continue
        yy = y[m]
        xx = x[m]
        # demean both then beta = cov/var
        yy0 = yy - yy.mean()
        xx0 = xx - xx.mean()
        var = float(np.dot(xx0, xx0))
        if var < 1e-18:
            out[t, m] = yy0
            continue
        beta = float(np.dot(xx0, yy0) / var)
        resid = np.full(y.shape, np.nan)
        resid[m] = yy0 - beta * xx0
        out[t] = resid
    return pd.DataFrame(out, index=idx, columns=cols, dtype="float32")


def _ann(sim, path):
    cur = sim
    for p in path:
        if not isinstance(cur, dict):
            return float("nan")
        cur = cur.get(p)
    if isinstance(cur, dict):
        return cur.get("ann", float("nan"))
    return float("nan")


def pack_metrics(sim: dict | None) -> dict:
    if not isinstance(sim, dict) or "flat" not in sim:
        return {
            "gross": float("nan"),
            "flat10": float("nan"),
            "flat25": float("nan"),
            "imp60": float("nan"),
            "imp100": float("nan"),
            "imp60_p25": float("nan"),
            "imp100_p25": float("nan"),
            "icir": float("nan"),
            "turn": float("nan"),
        }
    return {
        "gross": _ann(sim, ["gross"]),
        "flat10": _ann(sim, ["flat", "10"]),
        "flat25": _ann(sim, ["flat", "25"]),
        "imp60": _ann(sim, ["impact", "600000"]),
        "imp100": _ann(sim, ["impact", "1000000"]),
        "imp60_p25": _ann(sim, ["impact", "600000_plus_flat25"]),
        "imp100_p25": _ann(sim, ["impact", "1000000_plus_flat25"]),
        "icir": float(sim.get("icir") or float("nan")),
        "turn": float(sim.get("mean_turn_ow") or float("nan")),
    }


def _ensure_pkgs():
    if "quantlab" not in sys.modules:
        q = types.ModuleType("quantlab")
        q.__path__ = [str(ROOT / "quantlab")]
        sys.modules["quantlab"] = q
    if "quantlab.factors" not in sys.modules or not hasattr(
        sys.modules["quantlab.factors"], "__path__"
    ):
        f = types.ModuleType("quantlab.factors")
        f.__path__ = [str(ROOT / "quantlab/factors")]
        sys.modules["quantlab.factors"] = f

    def load(name: str, path: Path):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        return mod

    load("quantlab.factors.ops", ROOT / "quantlab/factors/ops.py")
    af = types.ModuleType("quantlab.factors.ai_factory")
    af.__path__ = [str(ROOT / "quantlab/factors/ai_factory")]
    sys.modules["quantlab.factors.ai_factory"] = af
    for name in ("ledger", "novelty", "fitness", "evaluate", "search", "structural_leaves"):
        load(
            f"quantlab.factors.ai_factory.{name}",
            ROOT / f"quantlab/factors/ai_factory/{name}.py",
        )


def _import_l1b():
    path = ROOT / "research/ai_factor_l1b_structural_explore.py"
    spec = importlib.util.spec_from_file_location("ai_factor_l1b_structural_explore", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ai_factor_l1b_structural_explore"] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _import_l1c():
    path = ROOT / "research/ai_factor_l1c_explore.py"
    spec = importlib.util.spec_from_file_location("ai_factor_l1c_explore", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ai_factor_l1c_explore"] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


MECHANISM = {
    "rank(ts_std_10(ann_insider_dec_5))": {
        "story_zh": "近5日标题命中「高管减持」次数的10日波动，再截面rank：波动↑≈近期减持事件簇活跃，做多高波动侧实质是押注减持簇后的相对博弈/关注度，而非减持本身的负向信息。",
        "pit_caveat_zh": "ann_* 仅 title_only 关键词命中滚动计数；无正文、无数量/金额；avail_date→下一交易日对齐；漏检/误检均可能。",
        "sparsity_risk_zh": "多数日截面大量为0，信号靠少数事件股；ts_std 放大「刚有事件 vs 长期无事件」差，CS 变异依赖事件稀疏尾部。",
    },
    "ts_std_10(ann_insider_dec_5)": {
        "story_zh": "与 #1 同经济内核，少一层 rank；量纲保留，头部选择对极端事件更敏感。",
        "pit_caveat_zh": "同 title_only / PIT 对齐约束。",
        "sparsity_risk_zh": "与 #1 同；无 rank 时极端值主导 Top-N。",
    },
    "ts_std_10(neg(ann_insider_dec_5))": {
        "story_zh": "数学上 ts_std(neg(x))=ts_std(x)，与 #2 同信号；若独立计票则属重复叶。",
        "pit_caveat_zh": "同 title_only。",
        "sparsity_risk_zh": "同 #2；消融应显示与 #2 近乎重合。",
    },
    "ts_max_5(ts_max_5(ann_insider_dec_5))": {
        "story_zh": "双重 ts_max≈近窗峰值减持标题强度（有效记忆约5–9日），偏「刚发生过减持标题」的水平态而非波动态。",
        "pit_caveat_zh": "title_only；峰值对单次误检敏感。",
        "sparsity_risk_zh": "事件后若干日截面仍抬升，换手可能高于 ts_std 族。",
    },
    "mul(delay_5(div(days_since_ld, ann_insider_dec_5)), ts_delta_20(neg(ann_n_5)))": {
        "story_zh": "交互叶：跌停距今/减持标题 × 公告总数20日差分取负。故事混杂（LD 修复节奏 × 减持稀有度 × 公告噪声变化），可解释性弱，过拟合风险高。",
        "pit_caveat_zh": "含 days_since_ld（非公告正文）+ title_only ann_*；div 在减持=0 时不稳定。",
        "sparsity_risk_zh": "CS 标准差报告达数百，数值病态；需拆臂消融验证是否单臂贡献。",
    },
}

# Ablation recipes keyed by parent expr
def build_jobs(survivors: list[dict]) -> tuple[list[dict], list[dict]]:
    """Return (primary_non_ld, ld_controls) job specs with ablation children."""
    # rank by gate's impact+flat25 @60万
    ranked = []
    for r in survivors:
        m = (r.get("impact_plus_flat25") or {}).get("600000")
        if m is None and isinstance(r.get("sim"), dict):
            m = _ann(r["sim"], ["impact", "600000_plus_flat25"])
        ranked.append((float(m) if m is not None and math.isfinite(float(m)) else -1e9, r))
    ranked.sort(key=lambda x: x[0], reverse=True)

    primary: list[dict] = []
    ld_ctrls: list[dict] = []
    seen = set()

    for rank_i, (imp60, r) in enumerate(ranked, 1):
        expr = r["expr"]
        if is_ld_only_expr(expr):
            if expr in ("neg(limit_down_flag)", "neg(ld_streak)") and expr not in seen:
                ld_ctrls.append(
                    {
                        "role": "ld_control",
                        "gate_rank": rank_i,
                        "parent": None,
                        "ablation": "ld_control_baseline",
                        "expr": expr,
                        "gate_imp60_p25": imp60,
                    }
                )
                seen.add(expr)
            continue

        # front-rank ann_insider #1-5 OR any lockup_/ann_ ≥12%
        L = leaves_in(expr)
        is_insider_front = rank_i <= 5 and "ann_insider_dec_5" in L
        is_ge_12_ann_lock = imp60 >= IMP60_FLOOR and (
            any(x.startswith("ann_") for x in L) or any(x.startswith("lockup_") for x in L)
        )
        if not (is_insider_front or is_ge_12_ann_lock):
            continue
        if expr in seen:
            continue
        seen.add(expr)
        primary.append(
            {
                "role": "primary",
                "gate_rank": rank_i,
                "parent": expr,
                "ablation": "baseline",
                "expr": expr,
                "gate_imp60_p25": imp60,
                "mechanism": MECHANISM.get(expr),
            }
        )

    # Ensure LD controls present even if somehow missing
    for e in ("neg(limit_down_flag)", "neg(ld_streak)"):
        if e not in seen:
            ld_ctrls.append(
                {
                    "role": "ld_control",
                    "gate_rank": None,
                    "parent": None,
                    "ablation": "ld_control_baseline",
                    "expr": e,
                    "gate_imp60_p25": None,
                }
            )

    return primary, ld_ctrls


def ablation_variants(parent: str) -> list[dict]:
    """Generate ablation expr jobs for one primary parent."""
    jobs = []

    def add(ablation: str, expr: str, note: str = ""):
        jobs.append(
            {
                "role": "ablation",
                "parent": parent,
                "ablation": ablation,
                "expr": expr,
                "note": note,
            }
        )

    if parent == "rank(ts_std_10(ann_insider_dec_5))":
        add("drop_rank", "ts_std_10(ann_insider_dec_5)", "去 rank")
        add("drop_ts_std", "rank(ann_insider_dec_5)", "去 ts_std，静态 rank")
        add("static_leaf", "ann_insider_dec_5", "静态单叶对照")
        add("static_neg", "neg(ann_insider_dec_5)", "静态符号翻转对照")
        add("sign_flip", "neg(rank(ts_std_10(ann_insider_dec_5)))", "整体取负")
        add("delay_5", "delay_5(rank(ts_std_10(ann_insider_dec_5)))", "延迟5")
        add("delay_10", "delay_10(rank(ts_std_10(ann_insider_dec_5)))", "延迟10")
        add("delay_20", "delay_20(rank(ts_std_10(ann_insider_dec_5)))", "延迟20")
        add("size_neutral_manual", "__SIZE_RESID__::rank(ts_std_10(ann_insider_dec_5))", "对 size 日度残差")
    elif parent == "ts_std_10(ann_insider_dec_5)":
        add("static_leaf", "ann_insider_dec_5", "静态单叶")
        add("static_neg", "neg(ann_insider_dec_5)", "静态取负")
        add("static_rank", "rank(ann_insider_dec_5)", "静态 rank")
        add("static_zscore", "zscore(ann_insider_dec_5)", "静态 zscore")
        add("ts_mean_alt", "ts_mean_10(ann_insider_dec_5)", "ts_mean 替代 ts_std")
        add("ts_max_alt", "ts_max_10(ann_insider_dec_5)", "ts_max 替代 ts_std")
        add("sign_flip_inner", "ts_std_10(neg(ann_insider_dec_5))", "内层取负（应≈恒等）")
        add("delay_5", "delay_5(ts_std_10(ann_insider_dec_5))", "延迟5")
        add("delay_20", "delay_20(ts_std_10(ann_insider_dec_5))", "延迟20")
        add("size_neutral_manual", "__SIZE_RESID__::ts_std_10(ann_insider_dec_5)", "size 残差")
    elif parent == "ts_std_10(neg(ann_insider_dec_5))":
        add("math_twin", "ts_std_10(ann_insider_dec_5)", "数学孪生对照")
        add("static_leaf", "ann_insider_dec_5", "静态单叶")
        add("static_neg", "neg(ann_insider_dec_5)", "静态取负")
        add("drop_neg_wrapper", "ts_std_10(ann_insider_dec_5)", "去掉无意义 neg")
    elif parent == "ts_max_5(ts_max_5(ann_insider_dec_5))":
        add("single_ts_max", "ts_max_5(ann_insider_dec_5)", "单层 ts_max")
        add("ts_max_10", "ts_max_10(ann_insider_dec_5)", "加长窗")
        add("static_leaf", "ann_insider_dec_5", "静态单叶")
        add("static_neg", "neg(ann_insider_dec_5)", "静态取负")
        add("ts_std_alt", "ts_std_10(ann_insider_dec_5)", "改用 ts_std 族")
        add("sign_flip", "neg(ts_max_5(ts_max_5(ann_insider_dec_5)))", "整体取负")
        add("delay_5", "delay_5(ts_max_5(ts_max_5(ann_insider_dec_5)))", "延迟5")
        add("delay_20", "delay_20(ts_max_5(ts_max_5(ann_insider_dec_5)))", "延迟20")
        add("size_neutral_manual", "__SIZE_RESID__::ts_max_5(ts_max_5(ann_insider_dec_5))", "size 残差")
    elif parent.startswith("mul(delay_5(div(days_since_ld"):
        add("arm_A_only", "delay_5(div(days_since_ld, ann_insider_dec_5))", "仅 LD/减持臂")
        add("arm_B_only", "ts_delta_20(neg(ann_n_5))", "仅公告差分臂")
        add("arm_B_pos", "ts_delta_20(ann_n_5)", "公告差分不去负")
        add("drop_delay", "mul(div(days_since_ld, ann_insider_dec_5), ts_delta_20(neg(ann_n_5)))", "去掉 delay_5")
        add("static_insider", "ann_insider_dec_5", "静态减持叶")
        add("static_ann_n", "ann_n_5", "静态公告计数")
        add("static_dsl", "days_since_ld", "静态距跌停")
        add("neg_insider", "neg(ann_insider_dec_5)", "静态减持取负")
        add("sign_flip", "neg(mul(delay_5(div(days_since_ld, ann_insider_dec_5)), ts_delta_20(neg(ann_n_5))))", "整体取负")
        add("size_neutral_manual", "__SIZE_RESID__::" + parent, "size 残差")
    else:
        # generic: static leaves + sign flip + delays
        for leaf in sorted(leaves_in(parent)):
            if leaf.startswith("ann_") or leaf.startswith("lockup_"):
                add(f"static_{leaf}", leaf, f"静态 {leaf}")
                add(f"static_neg_{leaf}", f"neg({leaf})", f"静态 neg({leaf})")
        add("sign_flip", f"neg({parent})", "整体取负")
        add("delay_5", f"delay_5({parent})", "延迟5")
        add("delay_20", f"delay_20({parent})", "延迟20")

    return jobs


def evaluate_one(expr_token: str, panels, label, sig, adv, size_panel):
    """Evaluate expr or __SIZE_RESID__::expr special token."""
    from quantlab.factors.ops import apply_expr, parse_expr

    size_mode = expr_token.startswith("__SIZE_RESID__::")
    expr = expr_token.split("::", 1)[1] if size_mode else expr_token
    tup = _seed_to_tuple(expr)
    fac = apply_expr(parse_expr(to_nested_tuple(tup)), panels)
    if not isinstance(fac, pd.DataFrame):
        raise TypeError(type(fac))
    fac = fac.astype("float32")
    if size_mode:
        if size_panel is None:
            return {
                "expr": expr,
                "expr_token": expr_token,
                "size_resid": True,
                "sim": {"error": "size_panel_unavailable", "promotion_approved": False},
                "cs_stats": None,
            }
        fac = size_residualize(fac, size_panel)
    cs = cs_std_stats(fac)
    if not cs["passes_cs_variation"]:
        sim = {"skipped": True, "reason": "cs_variation_fail", "promotion_approved": False}
    else:
        sim = simulate_book(fac, label, sig, adv)
    del fac
    gc.collect()
    return {
        "expr": expr,
        "expr_token": expr_token,
        "size_resid": size_mode,
        "sim": sim,
        "cs_stats": cs,
        "leaves": sorted(leaves_in(expr)),
    }


def honesty_verdict(parent: str, base_m: dict, abl_rows: list[dict]) -> dict:
    """Decide if parent survives mechanism+ablation honesty."""
    fails = []
    passes = []
    notes = []

    def m_of(rows, ablation):
        for r in rows:
            if r.get("ablation") == ablation:
                return pack_metrics(r.get("sim"))
        return None

    base60 = base_m.get("imp60_p25", float("nan"))
    base_icir = base_m.get("icir", float("nan"))

    if parent == "ts_std_10(neg(ann_insider_dec_5))":
        twin = m_of(abl_rows, "math_twin") or m_of(abl_rows, "drop_neg_wrapper")
        if twin and math.isfinite(twin["imp60_p25"]) and math.isfinite(base60):
            if abs(twin["imp60_p25"] - base60) < 1e-6:
                fails.append("math_duplicate_of_ts_std_10(ann_insider_dec_5)")
                notes.append("与 ts_std_10(ann_insider_dec_5) 数值重合，不得独立晋级计数")

    # sign flip should hurt if direction is real
    sf = m_of(abl_rows, "sign_flip")
    if sf and math.isfinite(sf["imp60_p25"]) and math.isfinite(base60):
        if sf["imp60_p25"] > base60 + 0.01:
            fails.append("sign_flip_improves")
            notes.append(f"整体取负后 60万+25bp 反而更好 ({sf['imp60_p25']:.2%} > {base60:.2%})")
        else:
            passes.append("sign_flip_hurts_or_neutral")

    # delay should decay for event signals
    d20 = m_of(abl_rows, "delay_20")
    if d20 and math.isfinite(d20["imp60_p25"]) and math.isfinite(base60):
        if d20["imp60_p25"] > base60 + 0.02:
            notes.append(f"delay_20 未衰减甚至更强 ({d20['imp60_p25']:.2%}) — 可疑持久偏差")
        else:
            passes.append("delay_20_decays")

    # static univariate: if static ≥ baseline, transform adds little
    static_keys = [a for a in ("static_leaf", "static_insider", "static_neg", "static_rank", "static_zscore") if m_of(abl_rows, a)]
    best_static = None
    for k in static_keys:
        mm = m_of(abl_rows, k)
        if mm and math.isfinite(mm["imp60_p25"]):
            if best_static is None or mm["imp60_p25"] > best_static[1]["imp60_p25"]:
                best_static = (k, mm)
    if best_static and math.isfinite(base60):
        sk, sm = best_static
        if sm["imp60_p25"] >= base60 - 0.005:
            notes.append(
                f"静态对照 {sk}≈基线 ({sm['imp60_p25']:.2%} vs {base60:.2%}) — 变换增益有限"
            )
            if sk in ("static_neg",) and sm["imp60_p25"] > 0 and base_icir is not None:
                # neg static positive while ts_std also positive → level vs vol story conflict ok
                passes.append("static_comparable")
        else:
            passes.append("transform_beats_static")
            notes.append(f"变换优于最佳静态 {sk} ({base60:.2%} > {sm['imp60_p25']:.2%})")

    # component arms for #5
    if parent.startswith("mul("):
        a = m_of(abl_rows, "arm_A_only")
        b = m_of(abl_rows, "arm_B_only")
        if a and b and math.isfinite(base60):
            a60, b60 = a["imp60_p25"], b["imp60_p25"]
            if math.isfinite(a60) and math.isfinite(b60):
                if max(a60, b60) >= base60 - 0.01:
                    fails.append("interaction_not_needed")
                    notes.append(
                        f"单臂已达交互水平 A={a60:.2%} B={b60:.2%} vs mul={base60:.2%} — 交互无增量"
                    )
                if min(a60, b60) < 0 < max(a60, b60) and base60 > 0:
                    notes.append("一臂正一臂负，交互符号靠乘法偶然对齐风险")
                # huge cs std
                notes.append("闸门报告 CS 标准差极大，数值病态风险")

    # size resid
    sz = m_of(abl_rows, "size_neutral_manual")
    if sz and math.isfinite(sz["imp60_p25"]) and math.isfinite(base60):
        if sz["imp60_p25"] <= 0 and base60 > 0:
            fails.append("size_kills_edge")
            notes.append(f"size 残差后 60万+25bp≤0 ({sz['imp60_p25']:.2%}) — 可能是市值通道")
        elif sz["imp60_p25"] < base60 * 0.5:
            notes.append(f"size 残差后衰减过半 ({sz['imp60_p25']:.2%} vs {base60:.2%})")
        else:
            passes.append("size_resid_keeps_edge")

    # cost gate reaffirm
    if not (math.isfinite(base60) and base60 >= IMP60_FLOOR):
        fails.append("below_12pct_gate")
    if not (math.isfinite(base_m.get("flat25", float("nan"))) and base_m["flat25"] > 0):
        fails.append("flat25_nonpositive")
    if not (math.isfinite(base_m.get("imp100_p25", float("nan"))) and base_m["imp100_p25"] > 0):
        fails.append("imp100_p25_nonpositive")

    # ICIR honesty: negative ICIR with positive long-only book = selection asymmetry, flag
    if math.isfinite(base_icir) and base_icir < 0:
        notes.append(f"ICIR={base_icir:.3f}<0：多空 IC 与 Top-N 多头簿不一致，机制需谨慎")

    survive = len(fails) == 0 and not any(
        x in fails for x in ()  # placeholder
    )
    # special: math duplicate always fails honesty as independent factor
    if "math_duplicate_of_ts_std_10(ann_insider_dec_5)" in fails:
        survive = False
    if "interaction_not_needed" in fails or "size_kills_edge" in fails:
        survive = False
    if "sign_flip_improves" in fails:
        survive = False
    if "below_12pct_gate" in fails or "flat25_nonpositive" in fails:
        survive = False

    # For survivors that only have soft notes, keep survive True if cost ok and no hard fails
    soft_only = [f for f in fails if f not in (
        "math_duplicate_of_ts_std_10(ann_insider_dec_5)",
        "interaction_not_needed",
        "size_kills_edge",
        "sign_flip_improves",
        "below_12pct_gate",
        "flat25_nonpositive",
        "imp100_p25_nonpositive",
    )]
    # Actually all listed are hard. Soft notes don't fail.

    return {
        "survive_honesty": bool(survive),
        "hard_fails": fails,
        "soft_passes": passes,
        "notes": notes,
        "promote": False,  # never promote this stage
    }


def fmt_pct(x):
    if isinstance(x, float) and math.isfinite(x):
        return f"{x:.2%}"
    return "—"


def main() -> int:
    global t0
    t0 = time.time()
    peak = mem_mb()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    survivors = json.loads((GATE_DIR / "survivors.json").read_text())
    primary, ld_ctrls = build_jobs(survivors)
    log("primary", len(primary), "ld_controls", len(ld_ctrls))
    for p in primary:
        log("  select", p["gate_rank"], p["expr"][:70], f"gate60={p['gate_imp60_p25']:.2%}")

    jobs = []
    for p in primary:
        jobs.append(dict(p))
        for a in ablation_variants(p["expr"]):
            a["gate_rank"] = p["gate_rank"]
            a["gate_imp60_p25"] = p["gate_imp60_p25"]
            jobs.append(a)
    for c in ld_ctrls:
        jobs.append(dict(c))

    # dedupe expr_token within same parent+ablation keep first
    log("jobs", len(jobs))

    _ensure_pkgs()
    l1b = _import_l1b()
    l1c = _import_l1c()
    from quantlab.factors.ai_factory.ledger import append_attempt

    log("loading panels")
    panels, label, public, load_meta = l1b.load_structural_panels()
    peak = max(peak, mem_mb())
    panels, label, public, load_meta = l1c.attach_l1c_panels(panels, label, public, load_meta)
    peak = max(peak, mem_mb())
    # size lives in public textbook panels (not structural leaf panels)
    size_panel = None
    if isinstance(public, dict) and public.get("size") is not None:
        size_panel = public["size"].astype("float32")
    del public
    gc.collect()

    needed = set()
    for j in jobs:
        tok = j["expr"]
        e = tok.split("::", 1)[1] if tok.startswith("__SIZE_RESID__::") else tok
        needed |= leaves_in(e)
    for k in list(panels.keys()):
        if k not in needed:
            del panels[k]
    gc.collect()
    log("trimmed", sorted(panels.keys()), "mem", mem_mb())

    cols = list(next(iter(panels.values())).columns)
    cal = next(iter(panels.values())).index
    sig, adv = load_sig_adv(cols, cal)
    peak = max(peak, mem_mb())
    log("sig/adv", sig.shape, "peak", peak)

    main_ledger = ROOT / "output/ai_factor/ledger.jsonl"
    run_ledger = OUT_DIR / "ledger_run.jsonl"
    if run_ledger.exists():
        run_ledger.unlink()
    n_before = (
        sum(1 for x in main_ledger.read_text().splitlines() if x.strip())
        if main_ledger.exists()
        else 0
    )

    results = []
    for i, job in enumerate(jobs):
        tok = job["expr"]
        try:
            ev = evaluate_one(tok, panels, label, sig, adv, size_panel)
            row = {**job, **ev}
        except Exception as exc:  # noqa: BLE001
            row = {
                **job,
                "expr": tok.split("::", 1)[-1],
                "expr_token": tok,
                "sim": {"error": f"{type(exc).__name__}: {exc}", "promotion_approved": False},
                "cs_stats": None,
                "leaves": sorted(leaves_in(tok.split("::", 1)[-1])),
                "size_resid": tok.startswith("__SIZE_RESID__::"),
            }
        row["metrics"] = pack_metrics(row.get("sim"))
        row["promotion_approved"] = False
        row["trial_kind"] = "explore_gate"
        results.append(row)

        fit = row["metrics"].get("imp60_p25")
        notes = (
            f"l1c_non_ld_mech_ablation;role={row.get('role')};ablation={row.get('ablation')};"
            f"parent={row.get('parent')};process_not_sealed;promotion_approved=false"
        )
        append_attempt(
            engine="l1c_non_ld_mech_ablation",
            seed=SEED,
            universe="midlarge_top1500_or_csi300_500",
            cost=0.0025,
            window="explore_20240603_to_latest_l1c_non_ld_ablation",
            expr_str=row.get("expr") or tok,
            fitness=fit if isinstance(fit, float) and math.isfinite(fit) else None,
            notes=notes,
            path=run_ledger,
        )
        append_attempt(
            engine="l1c_non_ld_mech_ablation",
            seed=SEED,
            universe="midlarge_top1500_or_csi300_500",
            cost=0.0025,
            window="explore_20240603_to_latest_l1c_non_ld_ablation",
            expr_str=row.get("expr") or tok,
            fitness=fit if isinstance(fit, float) and math.isfinite(fit) else None,
            notes=notes + ";explore_gate_process",
            path=main_ledger,
        )
        peak = max(peak, mem_mb())
        m = row["metrics"]
        log(
            f"[{i+1}/{len(jobs)}]",
            row.get("ablation"),
            (row.get("expr") or "")[:48],
            "60+25",
            fmt_pct(m.get("imp60_p25")),
            "mem",
            f"{mem_mb():.0f}",
        )

    n_after = (
        sum(1 for x in main_ledger.read_text().splitlines() if x.strip())
        if main_ledger.exists()
        else 0
    )

    # Verdicts per primary
    verdicts = []
    for p in primary:
        base = next(r for r in results if r.get("role") == "primary" and r.get("expr") == p["expr"])
        abls = [r for r in results if r.get("role") == "ablation" and r.get("parent") == p["expr"]]
        v = honesty_verdict(p["expr"], base["metrics"], abls)
        v["expr"] = p["expr"]
        v["gate_rank"] = p["gate_rank"]
        v["mechanism"] = p.get("mechanism")
        v["baseline_metrics"] = base["metrics"]
        v["n_ablations"] = len(abls)
        verdicts.append(v)

    ld_results = [r for r in results if r.get("role") == "ld_control"]

    summary = {
        "mode": "l1c_non_ld_mech_ablation",
        "promotion_approved": False,
        "sealed_executed": False,
        "trial_kind": "explore_gate",
        "window": "explore_20240603_to_latest",
        "capital_cny_primary": [600_000, 1_000_000],
        "primary_metric": "impact_plus_flat25 @60万/100万",
        "imp60_floor": IMP60_FLOOR,
        "n_primary": len(primary),
        "n_ld_controls": len(ld_ctrls),
        "n_jobs": len(jobs),
        "n_survive_honesty": sum(1 for v in verdicts if v["survive_honesty"]),
        "n_fail_honesty": sum(1 for v in verdicts if not v["survive_honesty"]),
        "industry_neutral": "stub_identity_skipped",
        "size_neutral": "manual_daily_ols_residual" if size_panel is not None else "unavailable",
        "ann_title_only": True,
        "invented_body": False,
        "ann_gap": (load_meta or {}).get("ann_title_events"),
        "ledger_N_before": n_before,
        "ledger_N_after": n_after,
        "ledger_N_new": n_after - n_before,
        "peak_rss_MB": round(peak),
        "mem_cap_MB": MEM_CAP_MB,
        "under_mem_cap": peak < MEM_CAP_MB,
        "runtime_s": round(time.time() - t0, 1),
        "suggest_sealed": False,
    }

    (OUT_DIR / "results.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False, default=str)
    )
    (OUT_DIR / "verdicts.json").write_text(
        json.dumps(verdicts, indent=2, ensure_ascii=False, default=str)
    )
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str)
    )
    (OUT_DIR / "selected_primary.json").write_text(
        json.dumps(primary, indent=2, ensure_ascii=False, default=str)
    )

    # --- Report ZH ---
    lines = []
    lines.append("# AI 因子 L1c：非跌停叶机制说明 + 消融（探索窗）")
    lines.append("")
    lines.append("- **时间：** 2026-10-12（America/New_York）")
    lines.append("- **promotion_approved：** false；**密封：** 未开；**不交 Strategy 权重**")
    lines.append("- **trial_kind：** explore_gate / process")
    lines.append("- **本金主口径：** 60 万 / 100 万（flat + √冲击；主裁决=冲击+flat25）")
    lines.append("- **禁止：** 小盘主线、教科书主结果、密封窗、编造公告正文（title_only）")
    lines.append(
        f"- 账本：N {n_before} → {n_after}（+{n_after - n_before}，explore_gate 过程计次）"
    )
    lines.append(
        f"- 峰值 RSS：{round(peak)} MB（上限 {MEM_CAP_MB}；under_cap={peak < MEM_CAP_MB}）；"
        f"运行 {summary['runtime_s']}s"
    )
    lines.append(
        f"- 上游闸门：`output/alpha/AI_FACTOR_L1c_CS_VARIATION_GATE_ZH.md`（严格存活 38）"
    )
    lines.append("")
    lines.append("## 选题规则")
    lines.append("")
    lines.append("1. 从存活排序取前排**非跌停**叶：`ann_insider_dec_5` 相关 #1–#5")
    lines.append("2. 另取任意 `lockup_*` / `ann_*` 且 **≥12% net @60万（冲击+25bp）** 者（本批无额外 lockup 达标）")
    lines.append("3. 跌停叶 `limit_down_*` / `ld_*` **仅作对照，不晋级**")
    lines.append("4. `industry_neutral` 为 ops stub（恒等）→ 跳过；`size` 面板做日度 OLS 残差")
    lines.append("")
    lines.append("## 入选主叶")
    lines.append("")
    lines.append("| gate# | 表达式 | 闸门60万+25bp | 角色 |")
    lines.append("|---|---|---|---|")
    for p in primary:
        lines.append(
            f"| {p['gate_rank']} | `{p['expr']}` | {fmt_pct(p['gate_imp60_p25'])} | primary |"
        )
    for c in ld_ctrls:
        lines.append(
            f"| {c.get('gate_rank')} | `{c['expr']}` | {fmt_pct(c.get('gate_imp60_p25'))} | ld_control |"
        )
    lines.append("")

    lines.append("## 机制说明（title_only）")
    lines.append("")
    for v in verdicts:
        mech = v.get("mechanism") or {}
        lines.append(f"### `{v['expr']}`（gate #{v['gate_rank']}）")
        lines.append("")
        lines.append(f"- **经济故事：** {mech.get('story_zh', '（见消融）')}")
        lines.append(f"- **PIT/title_only：** {mech.get('pit_caveat_zh', 'title_only，无正文')}")
        lines.append(f"- **稀疏/CS：** {mech.get('sparsity_risk_zh', '—')}")
        lines.append("")

    lines.append("## 基线重估（flat + √冲击 @60/100万）")
    lines.append("")
    lines.append(
        "| 表达式 | ICIR | flat10 | flat25 | 冲击60万 | 冲击100万 | 60万+25bp | 100万+25bp | 换手 |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for r in results:
        if r.get("role") not in ("primary", "ld_control"):
            continue
        m = r["metrics"]
        tag = "对照" if r.get("role") == "ld_control" else "主叶"
        lines.append(
            "| `{e}` ({tag}) | {icir:.3f} | {f10} | {f25} | {i60} | {i100} | {p60} | {p100} | {to:.3f} |".format(
                e=r["expr"],
                tag=tag,
                icir=m.get("icir") if math.isfinite(m.get("icir") or float("nan")) else float("nan"),
                f10=fmt_pct(m.get("flat10")),
                f25=fmt_pct(m.get("flat25")),
                i60=fmt_pct(m.get("imp60")),
                i100=fmt_pct(m.get("imp100")),
                p60=fmt_pct(m.get("imp60_p25")),
                p100=fmt_pct(m.get("imp100_p25")),
                to=m.get("turn") if math.isfinite(m.get("turn") or float("nan")) else float("nan"),
            )
        )
    lines.append("")

    lines.append("## 消融表（按父叶）")
    lines.append("")
    for p in primary:
        lines.append(f"### 父叶 `{p['expr']}`")
        lines.append("")
        lines.append(
            "| 消融 | 表达式 | flat25 | 60万+25bp | 100万+25bp | ICIR | 换手 | 备注 |"
        )
        lines.append("|---|---|---|---|---|---|---|---|")
        base = next(r for r in results if r.get("role") == "primary" and r["expr"] == p["expr"])
        m = base["metrics"]
        lines.append(
            f"| baseline | `{base['expr']}` | {fmt_pct(m['flat25'])} | {fmt_pct(m['imp60_p25'])} | "
            f"{fmt_pct(m['imp100_p25'])} | {m['icir']:.3f} | {m['turn']:.3f} | 基线 |"
        )
        for r in results:
            if r.get("role") != "ablation" or r.get("parent") != p["expr"]:
                continue
            m = r["metrics"]
            ic = m.get("icir")
            ic_s = f"{ic:.3f}" if isinstance(ic, float) and math.isfinite(ic) else "—"
            to = m.get("turn")
            to_s = f"{to:.3f}" if isinstance(to, float) and math.isfinite(to) else "—"
            err = ""
            if isinstance(r.get("sim"), dict) and r["sim"].get("error"):
                err = r["sim"]["error"][:40]
            elif isinstance(r.get("sim"), dict) and r["sim"].get("skipped"):
                err = "cs_fail"
            lines.append(
                f"| {r.get('ablation')} | `{r.get('expr')}` | {fmt_pct(m.get('flat25'))} | "
                f"{fmt_pct(m.get('imp60_p25'))} | {fmt_pct(m.get('imp100_p25'))} | {ic_s} | {to_s} | "
                f"{r.get('note','')};{err} |"
            )
        lines.append("")

    lines.append("## 诚实裁决")
    lines.append("")
    lines.append("| 表达式 | 存活诚实？ | 硬失败 | 笔记 |")
    lines.append("|---|---|---|---|")
    for v in verdicts:
        lines.append(
            "| `{e}` | **{ok}** | {hf} | {notes} |".format(
                e=v["expr"],
                ok="是" if v["survive_honesty"] else "否",
                hf=", ".join(v["hard_fails"]) if v["hard_fails"] else "—",
                notes="; ".join(v["notes"][:4]) if v["notes"] else "—",
            )
        )
    lines.append("")
    lines.append("### 跌停对照（不晋级）")
    lines.append("")
    lines.append("| 表达式 | flat25 | 60万+25bp | 100万+25bp | ICIR |")
    lines.append("|---|---|---|---|---|")
    for r in ld_results:
        m = r["metrics"]
        lines.append(
            f"| `{r['expr']}` | {fmt_pct(m['flat25'])} | {fmt_pct(m['imp60_p25'])} | "
            f"{fmt_pct(m['imp100_p25'])} | {m['icir']:.3f} |"
        )
    lines.append("")
    lines.append("## 结论（清晰裁决）")
    lines.append("")
    ok_list = [v["expr"] for v in verdicts if v["survive_honesty"]]
    bad_list = [v["expr"] for v in verdicts if not v["survive_honesty"]]
    if ok_list:
        lines.append(f"- **机制+消融后仍诚实存活（非晋级）：** {len(ok_list)} 条")
        for e in ok_list:
            lines.append(f"  - `{e}`")
    else:
        lines.append("- **机制+消融后：无非跌停叶通过诚实裁决。**")
    if bad_list:
        lines.append(f"- **诚实失败：** {len(bad_list)} 条")
        for v in verdicts:
            if not v["survive_honesty"]:
                lines.append(
                    f"  - `{v['expr']}` — {', '.join(v['hard_fails']) or '见笔记'}"
                )
    lines.append(
        "- 跌停叶仅对照：`neg(limit_down_flag)` / `neg(ld_streak)` — **不晋级**。"
    )
    lines.append(
        "- `promotion_approved=false`；**不开密封**；不交 Strategy 权重；公告仍 title_only，未编造正文。"
    )
    lines.append(
        "- lockup_* 本批无一达到 ≥12% @60万+25bp（最佳 `neg(lockup_S_20)`≈10.45%），故未入主消融。"
    )
    lines.append("")
    lines.append("## 路径")
    lines.append("")
    lines.append(f"- 报告：`{REPORT}`")
    lines.append(
        f"- 产物：`{OUT_DIR}/`（summary/results/verdicts/selected_primary.json, ledger_run.jsonl）"
    )
    lines.append("- 账本：`output/ai_factor/ledger.jsonl`（explore_gate / process，非 sealed）")
    lines.append("")

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log("done", "survive_honesty", summary["n_survive_honesty"], "peak", peak)
    print(
        json.dumps(
            {
                "n_primary": summary["n_primary"],
                "n_survive_honesty": summary["n_survive_honesty"],
                "n_fail_honesty": summary["n_fail_honesty"],
                "peak_MB": round(peak),
                "ledger_N": n_after,
                "report": str(REPORT),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
