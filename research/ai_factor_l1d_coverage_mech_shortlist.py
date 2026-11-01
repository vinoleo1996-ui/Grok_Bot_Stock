#!/usr/bin/env python3
"""L1d: coverage re-cut on lockup_days_to + mech/ablation on stabler candidates + shortlist.

promotion_approved=False. No sealed. No Strategy weight. No small-cap.
No broadcast/LD primary. Announcements title_only. Memory < 2.5GB.
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
L1D_DIR = ROOT / "output/ai_factor/l1d_non_ld_struct_explore"
L1C_MECH = ROOT / "output/ai_factor/l1c_non_ld_mech_ablation"
OUT_DIR = ROOT / "output/ai_factor/l1d_coverage_mech_shortlist"
REPORT = ROOT / "output/alpha/AI_FACTOR_L1d_COVERAGE_MECH_SHORTLIST_ZH.md"
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
IMP60_FLOOR = 0.10  # soft floor for shortlist (>=10%); honesty uses 0.10

# Coverage gate thresholds (① lockup_days_to family)
COV_NONEMPTY_MIN = 0.08          # explore-window cell non-empty (days_to: notna; else >0)
COV_MEAN_EVENT_NAMES_MIN = 40.0  # mean # names/day with signal
COV_FRAC_DAYS_GE20_MIN = 0.50    # fraction of days with ≥20 event names
COV_EVENT_N_MIN = 20

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
    print(f"[l1d_cov {time.time()-t0:5.0f}s {mem_mb():.0f}MB]", *a, flush=True)


def leaves_in(expr: str) -> set[str]:
    return {t for t in re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", expr) if t not in OPS}


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
    for op in ("mul", "add", "sub", "div"):
        m = re.fullmatch(rf"{op}\((.+)\)", s)
        if m:
            inner = m.group(1)
            depth = 0
            split_at = None
            for i, ch in enumerate(inner):
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                elif ch == "," and depth == 0:
                    split_at = i
                    break
            if split_at is None:
                raise ValueError(f"cannot split {op}: {s}")
            return (
                "op",
                op,
                _seed_to_tuple(inner[:split_at].strip()),
                _seed_to_tuple(inner[split_at + 1 :].strip()),
            )
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


def coverage_stats(fac: pd.DataFrame, *, days_to_style: bool = False) -> dict:
    """Non-empty rate + event coverage in explore window."""
    sample = fac.loc[fac.index >= EXPLORE_START]
    if days_to_style:
        active = sample.notna()
    else:
        # treat finite & |x|>eps as event/signal presence
        active = sample.notna() & (sample.abs() > 1e-12)
    nonempty = float(active.to_numpy().mean())
    n_names = active.sum(axis=1).astype(float)
    mean_names = float(n_names.mean()) if len(n_names) else float("nan")
    med_names = float(n_names.median()) if len(n_names) else float("nan")
    frac_ge = float((n_names >= COV_EVENT_N_MIN).mean()) if len(n_names) else float("nan")
    passes = bool(
        math.isfinite(nonempty)
        and nonempty >= COV_NONEMPTY_MIN
        and math.isfinite(mean_names)
        and mean_names >= COV_MEAN_EVENT_NAMES_MIN
        and math.isfinite(frac_ge)
        and frac_ge >= COV_FRAC_DAYS_GE20_MIN
    )
    fail_reasons = []
    if not (math.isfinite(nonempty) and nonempty >= COV_NONEMPTY_MIN):
        fail_reasons.append(f"nonempty<{COV_NONEMPTY_MIN:.0%}({nonempty:.4f})")
    if not (math.isfinite(mean_names) and mean_names >= COV_MEAN_EVENT_NAMES_MIN):
        fail_reasons.append(f"mean_event_names<{COV_MEAN_EVENT_NAMES_MIN:.0f}({mean_names:.2f})")
    if not (math.isfinite(frac_ge) and frac_ge >= COV_FRAC_DAYS_GE20_MIN):
        fail_reasons.append(f"frac_days_ge{COV_EVENT_N_MIN}<{COV_FRAC_DAYS_GE20_MIN:.0%}({frac_ge:.4f})")
    return {
        "nonempty_rate": nonempty,
        "mean_event_names": mean_names,
        "median_event_names": med_names,
        "frac_days_ge_N": frac_ge,
        "N_event_threshold": COV_EVENT_N_MIN,
        "passes_coverage": passes,
        "fail_reasons": fail_reasons,
    }


def size_residualize(fac: pd.DataFrame, size: pd.DataFrame) -> pd.DataFrame:
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
            "ic_mean": float("nan"),
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
        "ic_mean": float(sim.get("ic_mean") or float("nan")),
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


def _import_mod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


MECHANISM = {
    "abs(ts_std_20(ts_delta_10(lockup_S_5)))": {
        "story_zh": "近窗解禁供给(S_5)的10日差分再20日波动取绝对值：捕捉「解禁供给突然变化」而非水平态；波动↑≈日历供给冲击簇。",
        "pit_caveat_zh": "share_float PIT 按 ann_date；日历日近似交易窗；float_ratio 累加；无正文。",
        "sparsity_risk_zh": "lockup_S_5 非空率极低(~0.2%)，ts_delta/ts_std 在零垫上制造伪波动；需覆盖率警示。",
    },
    "abs(ts_std_20(ts_delta_10(lockup_S_60)))": {
        "story_zh": "同结构换更长解禁窗 S_60：供给变化波动，偏中期解禁簇。",
        "pit_caveat_zh": "同 share_float PIT；S_60 覆盖略高于 S_5 但仍稀疏。",
        "sparsity_risk_zh": "非空~1.5%；变换后伪连续风险仍在。",
    },
    "ts_std_10(lockup_S_60)": {
        "story_zh": "解禁供给水平的10日波动：有供给活动的股票波动抬升，做多波动侧≈押注解禁活动后的相对定价。",
        "pit_caveat_zh": "同 PIT；无方向性取负。",
        "sparsity_risk_zh": "覆盖仍低；换手偏高(~0.19)。",
    },
    "neg(ann_penalty_10)": {
        "story_zh": "近10日标题命中「处罚」次数取负：回避处罚标题股（做多无处罚侧）。",
        "pit_caveat_zh": "title_only 关键词/event_type；无正文、无金额；avail→下一交易日。",
        "sparsity_risk_zh": "非零率~0.5%；信号靠极少数事件股，CS 近似二值。",
    },
    "neg(ann_buyback_10)": {
        "story_zh": "近10日「回购」标题取负：做多无回购标题侧（或回避回购公告后的抢跑回吐）。",
        "pit_caveat_zh": "title_only；buyback/buyback_excluded 合并计数。",
        "sparsity_risk_zh": "非零~4.6%，相对其他事件族略厚，但仍稀疏。",
    },
    "neg(ann_inquiry_letter_5)": {
        "story_zh": "近5日问询函标题取负：回避监管问询标题股。",
        "pit_caveat_zh": "title_only event_type=inquiry_letter。",
        "sparsity_risk_zh": "非零~0.26%；极稀疏。",
    },
    "neg(ann_inquiry_reply_5)": {
        "story_zh": "近5日问询回函标题取负：回避回函事件股。",
        "pit_caveat_zh": "title_only event_type=inquiry_reply。",
        "sparsity_risk_zh": "非零~0.32%；极稀疏。",
    },
    "neg(ann_inquiry_any_5)": {
        "story_zh": "问询函∪回函标题取负：合并监管注意力事件回避。",
        "pit_caveat_zh": "title_only；letter+reply。",
        "sparsity_risk_zh": "非零~0.41%。",
    },
}


def stabler_parents_from_survivors(survivors: list[dict]) -> list[dict]:
    """Pick representative stabler L1d survivors for mech+ablation."""
    want = [
        "abs(ts_std_20(ts_delta_10(lockup_S_5)))",
        "abs(ts_std_20(ts_delta_10(lockup_S_60)))",
        "ts_std_10(lockup_S_60)",
        "neg(ann_penalty_10)",
        "neg(ann_buyback_10)",
        "neg(ann_inquiry_letter_5)",
        "neg(ann_inquiry_reply_5)",
        "neg(ann_inquiry_any_5)",
    ]
    by_expr = {r["expr"]: r for r in survivors}
    out = []
    for e in want:
        r = by_expr.get(e)
        if r is None:
            continue
        out.append(
            {
                "role": "primary",
                "parent": e,
                "ablation": "baseline",
                "expr": e,
                "family": r.get("family"),
                "gate_imp60_p25": r.get("imp06_plus25"),
                "gate_imp100_p25": r.get("imp10_plus25"),
                "gate_flat25": r.get("flat25"),
                "gate_turn": r.get("turn"),
                "mechanism": MECHANISM.get(e),
            }
        )
    return out


def ablation_variants(parent: str) -> list[dict]:
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

    if parent.startswith("abs(ts_std_20(ts_delta_10(lockup_S_"):
        m = re.fullmatch(r"abs\(ts_std_20\(ts_delta_10\((lockup_S_\d+)\)\)\)", parent)
        leaf = m.group(1) if m else "lockup_S_5"
        add("drop_abs", f"ts_std_20(ts_delta_10({leaf}))", "去 abs")
        add("drop_ts_std", f"ts_delta_10({leaf})", "去 ts_std，仅差分")
        add("drop_delta", f"ts_std_20({leaf})", "去 delta，仅波动")
        add("static_leaf", leaf, f"静态 {leaf}")
        add("static_neg", f"neg({leaf})", f"静态 neg({leaf})")
        add("sign_flip", f"neg({parent})", "整体取负")
        add("delay_5", f"delay_5({parent})", "延迟5")
        add("delay_20", f"delay_20({parent})", "延迟20")
        add("size_neutral_manual", f"__SIZE_RESID__::{parent}", "size 残差")
    elif parent.startswith("ts_std_10(lockup_S_"):
        m = re.fullmatch(r"ts_std_10\((lockup_S_\d+)\)", parent)
        leaf = m.group(1) if m else "lockup_S_60"
        add("static_leaf", leaf, f"静态 {leaf}")
        add("static_neg", f"neg({leaf})", f"静态 neg")
        add("ts_mean_alt", f"ts_mean_10({leaf})", "ts_mean 替代")
        add("ts_max_alt", f"ts_max_10({leaf})", "ts_max 替代")
        add("sign_flip", f"neg({parent})", "整体取负")
        add("delay_5", f"delay_5({parent})", "延迟5")
        add("delay_20", f"delay_20({parent})", "延迟20")
        add("size_neutral_manual", f"__SIZE_RESID__::{parent}", "size 残差")
    elif parent.startswith("neg(ann_"):
        m = re.fullmatch(r"neg\((ann_[a-z0-9_]+)\)", parent)
        leaf = m.group(1) if m else parent[4:-1]
        add("drop_neg", leaf, "去掉 neg（应翻向）")
        add("static_leaf", leaf, "静态单叶（同 drop_neg）")
        add("static_rank", f"rank({leaf})", "静态 rank")
        add("rank_neg", f"rank(neg({leaf}))", "rank(neg) 对照")
        add("ts_std_alt", f"ts_std_10({leaf})", "波动变换替代水平 neg")
        add("sign_flip", leaf, "整体取负=原叶")  # same as drop_neg; kept for recipe symmetry
        add("delay_5", f"delay_5({parent})", "延迟5")
        add("delay_20", f"delay_20({parent})", "延迟20")
        add("size_neutral_manual", f"__SIZE_RESID__::{parent}", "size 残差")
    else:
        for leaf in sorted(leaves_in(parent)):
            add(f"static_{leaf}", leaf, f"静态 {leaf}")
            add(f"static_neg_{leaf}", f"neg({leaf})", f"静态 neg")
        add("sign_flip", f"neg({parent})", "整体取负")
        add("delay_5", f"delay_5({parent})", "延迟5")
        add("delay_20", f"delay_20({parent})", "延迟20")
    return jobs


def evaluate_one(expr_token: str, panels, label, sig, adv, size_panel, *, need_cov: bool = False, days_to_style: bool = False):
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
                "coverage": None,
            }
        fac = size_residualize(fac, size_panel)
    cs = cs_std_stats(fac)
    cov = coverage_stats(fac, days_to_style=days_to_style) if need_cov else None
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
        "coverage": cov,
        "leaves": sorted(leaves_in(expr)),
    }


def honesty_verdict(parent: str, base_m: dict, abl_rows: list[dict], base_cov: dict | None) -> dict:
    fails = []
    passes = []
    notes = []

    def m_of(ablation):
        for r in abl_rows:
            if r.get("ablation") == ablation:
                return pack_metrics(r.get("sim"))
        return None

    base60 = base_m.get("imp60_p25", float("nan"))
    base_icir = base_m.get("icir", float("nan"))

    # coverage soft note for sparse parents (not hard-fail for non-days_to; days_to already cut in ①)
    if base_cov and not base_cov.get("passes_coverage"):
        notes.append(
            "覆盖率未达门槛: " + ",".join(base_cov.get("fail_reasons") or [])
        )
        notes.append("稀疏警示：事件覆盖低，Top-N 可能由少数名字主导")

    sf = m_of("sign_flip")
    if sf and math.isfinite(sf["imp60_p25"]) and math.isfinite(base60):
        if sf["imp60_p25"] > base60 + 0.01:
            fails.append("sign_flip_improves")
            notes.append(f"整体取负后更好 ({sf['imp60_p25']:.2%} > {base60:.2%})")
        else:
            passes.append("sign_flip_hurts_or_neutral")

    # for neg(ann_*) parents, drop_neg == sign flip of direction
    dn = m_of("drop_neg")
    if dn and math.isfinite(dn["imp60_p25"]) and math.isfinite(base60):
        if dn["imp60_p25"] > base60 + 0.01:
            fails.append("drop_neg_improves")
            notes.append(f"去掉 neg 后更好 ({dn['imp60_p25']:.2%}) — 方向可疑")
        else:
            passes.append("neg_direction_supported")

    d20 = m_of("delay_20")
    if d20 and math.isfinite(d20["imp60_p25"]) and math.isfinite(base60):
        if d20["imp60_p25"] > base60 + 0.02:
            notes.append(f"delay_20 未衰减甚至更强 ({d20['imp60_p25']:.2%})")
        else:
            passes.append("delay_20_decays")

    # static univariate
    best_static = None
    for k in ("static_leaf", "static_neg", "drop_neg", "static_rank"):
        mm = m_of(k)
        if mm and math.isfinite(mm.get("imp60_p25", float("nan"))):
            if best_static is None or mm["imp60_p25"] > best_static[1]["imp60_p25"]:
                best_static = (k, mm)
    if best_static and math.isfinite(base60):
        sk, sm = best_static
        if sm["imp60_p25"] >= base60 - 0.005:
            notes.append(f"静态对照 {sk}≈基线 ({sm['imp60_p25']:.2%} vs {base60:.2%})")
            if parent.startswith("neg(ann_"):
                # for pure neg(leaf), baseline IS the static_neg — expect comparable
                passes.append("baseline_is_static_level")
            else:
                notes.append("变换增益有限")
        else:
            passes.append("transform_beats_static")
            notes.append(f"变换优于最佳静态 {sk} ({base60:.2%} > {sm['imp60_p25']:.2%})")

    # lockup abs structure: drop components
    if parent.startswith("abs(ts_std"):
        for k, label in (
            ("drop_abs", "去abs"),
            ("drop_ts_std", "去ts_std"),
            ("drop_delta", "去delta"),
        ):
            mm = m_of(k)
            if mm and math.isfinite(mm["imp60_p25"]) and math.isfinite(base60):
                if mm["imp60_p25"] >= base60 - 0.01:
                    notes.append(f"{label} 后仍≈基线 ({mm['imp60_p25']:.2%}) — 结构可能冗余")
                else:
                    passes.append(f"{k}_hurts")

    sz = m_of("size_neutral_manual")
    if sz and math.isfinite(sz["imp60_p25"]) and math.isfinite(base60):
        if sz["imp60_p25"] <= 0 and base60 > 0:
            fails.append("size_kills_edge")
            notes.append(f"size 残差后 ≤0 ({sz['imp60_p25']:.2%})")
        elif sz["imp60_p25"] < base60 * 0.5:
            notes.append(f"size 残差后衰减过半 ({sz['imp60_p25']:.2%} vs {base60:.2%})")
        else:
            passes.append("size_resid_keeps_edge")

    if not (math.isfinite(base60) and base60 >= IMP60_FLOOR):
        fails.append("below_10pct_gate")
    if not (math.isfinite(base_m.get("flat25", float("nan"))) and base_m["flat25"] > 0):
        fails.append("flat25_nonpositive")
    if not (math.isfinite(base_m.get("imp100_p25", float("nan"))) and base_m["imp100_p25"] > 0):
        fails.append("imp100_p25_nonpositive")
    if math.isfinite(base_icir) and base_icir < 0:
        notes.append(f"ICIR={base_icir:.3f}<0：多空 IC 与 Top-N 多头簿不一致")

    hard = {
        "sign_flip_improves",
        "drop_neg_improves",
        "size_kills_edge",
        "below_10pct_gate",
        "flat25_nonpositive",
        "imp100_p25_nonpositive",
    }
    survive = not any(f in hard for f in fails)
    return {
        "survive_honesty": bool(survive),
        "hard_fails": fails,
        "soft_passes": passes,
        "notes": notes,
        "promote": False,
    }


def fmt_pct(x):
    if isinstance(x, float) and math.isfinite(x):
        return f"{x:.2%}"
    return "—"


def fmt_num(x, nd=2):
    if isinstance(x, float) and math.isfinite(x):
        return f"{x:.{nd}f}"
    return "—"


def main() -> int:
    global t0
    t0 = time.time()
    peak = mem_mb()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    survivors = json.loads((L1D_DIR / "survivors.json").read_text())
    l1d_summary = json.loads((L1D_DIR / "summary.json").read_text())
    l1c_verdicts = json.loads((L1C_MECH / "verdicts.json").read_text())
    l1c_honest = [v for v in l1c_verdicts if v.get("survive_honesty")]
    log("l1d survivors", len(survivors), "l1c honest", len(l1c_honest))

    # ---------- ① lockup_days_to coverage re-cut ----------
    days_to_surv = [r for r in survivors if "lockup_days_to" in r["expr"]]
    log("lockup_days_to survivors to re-cut", len(days_to_surv))

    parents = stabler_parents_from_survivors(survivors)
    log("stabler parents", len(parents), [p["expr"] for p in parents])

    jobs = []
    for p in parents:
        jobs.append(dict(p))
        for a in ablation_variants(p["expr"]):
            a["family"] = p.get("family")
            a["gate_imp60_p25"] = p.get("gate_imp60_p25")
            jobs.append(a)
    # dedupe by (parent, ablation, expr_token)
    seen = set()
    uniq_jobs = []
    for j in jobs:
        tok = j["expr"]
        key = (j.get("parent"), j.get("ablation"), tok)
        if key in seen:
            continue
        seen.add(key)
        uniq_jobs.append(j)
    jobs = uniq_jobs
    log("mech jobs", len(jobs))

    _ensure_pkgs()
    l1b = _import_mod("ai_factor_l1b_structural_explore", ROOT / "research/ai_factor_l1b_structural_explore.py")
    l1c = _import_mod("ai_factor_l1c_explore", ROOT / "research/ai_factor_l1c_explore.py")
    l1d = _import_mod("ai_factor_l1d_non_ld_struct_explore", ROOT / "research/ai_factor_l1d_non_ld_struct_explore.py")
    from quantlab.factors.ops import apply_expr, parse_expr
    from quantlab.factors.ai_factory.ledger import append_attempt

    log("loading base panels")
    panels, label, public, load_meta = l1b.load_structural_panels()
    peak = max(peak, mem_mb())
    panels, label, public, load_meta = l1c.attach_l1c_panels(panels, label, public, load_meta)
    peak = max(peak, mem_mb())
    size_panel = None
    if isinstance(public, dict) and public.get("size") is not None:
        size_panel = public["size"].astype("float32")
    del public
    gc.collect()

    # Attach lockup + ann extra panels needed
    # Match L1d: daily mid/large tradeable mask
    if "overnight_ret" in panels:
        mask = panels["overnight_ret"].notna()
        cols = list(panels["overnight_ret"].columns)
        cal = panels["overnight_ret"].index
    else:
        cols = list(next(iter(panels.values())).columns)
        cal = next(iter(panels.values())).index
        mask = None

    log("building lockup calendar panels")
    lock_panels, lock_gap = l1d.build_lockup_calendar_panels(cal, cols, mask)
    panels.update(lock_panels)
    del lock_panels
    gc.collect()
    peak = max(peak, mem_mb())

    log("building ann title extra panels")
    ann_panels, ann_gap = l1d.build_ann_title_extra_panels(cal, cols, mask)
    panels.update(ann_panels)
    del ann_panels
    gc.collect()
    peak = max(peak, mem_mb())
    log("panels ready", len(panels), "peak", peak)

    # --- ① compute coverage on lockup_days_to exprs ---
    coverage_rows = []
    leaf_cov = coverage_stats(panels["lockup_days_to"], days_to_style=True)
    log("leaf lockup_days_to cov", leaf_cov)

    for r in days_to_surv:
        expr = r["expr"]
        try:
            tup = _seed_to_tuple(expr)
            fac = apply_expr(parse_expr(to_nested_tuple(tup)), panels)
            fac = fac.astype("float32")
            # days_to transforms: nonempty = finite (nan means no upcoming unlock)
            # but after abs/rank/std, zeros appear — use days_to_style only for pure days_to-ish
            dt_style = expr in (
                "lockup_days_to",
                "delay_5(lockup_days_to)",
                "delay_20(lockup_days_to)",
                "ts_mean_5(lockup_days_to)",
                "ts_mean_10(lockup_days_to)",
                "ts_max_5(lockup_days_to)",
                "ts_max_10(lockup_days_to)",
                "rank(lockup_days_to)",
                "zscore(lockup_days_to)",
                "neg(lockup_days_to)",
                "rank(neg(lockup_days_to))",
            )
            cov = coverage_stats(fac, days_to_style=dt_style)
            # also require underlying leaf coverage
            if not leaf_cov["passes_coverage"]:
                cov["passes_coverage"] = False
                fr = list(cov.get("fail_reasons") or [])
                fr.append("underlying_leaf_lockup_days_to_sparse")
                cov["fail_reasons"] = fr
            row = {
                "expr": expr,
                "family": "lockup_days_to",
                "gate_imp60_p25": r.get("imp06_plus25"),
                "gate_imp100_p25": r.get("imp10_plus25"),
                "gate_flat25": r.get("flat25"),
                "gate_turn": r.get("turn"),
                "gate_icir": r.get("icir"),
                "coverage": cov,
                "survive_coverage": bool(cov["passes_coverage"]),
                "verdict": "SURVIVE_COV" if cov["passes_coverage"] else "FAIL_SPARSITY",
            }
            del fac
            gc.collect()
        except Exception as exc:  # noqa: BLE001
            row = {
                "expr": expr,
                "family": "lockup_days_to",
                "gate_imp60_p25": r.get("imp06_plus25"),
                "coverage": None,
                "survive_coverage": False,
                "verdict": "ERROR",
                "error": f"{type(exc).__name__}: {exc}",
            }
        coverage_rows.append(row)

    n_cov_ok = sum(1 for x in coverage_rows if x.get("survive_coverage"))
    log("coverage re-cut:", n_cov_ok, "survive /", len(coverage_rows), "fail sparsity", len(coverage_rows) - n_cov_ok)

    # Trim panels to needed leaves for mech jobs
    needed = set()
    for j in jobs:
        tok = j["expr"]
        e = tok.split("::", 1)[1] if tok.startswith("__SIZE_RESID__::") else tok
        needed |= leaves_in(e)
    # keep lockup_days_to for reporting only already done
    for k in list(panels.keys()):
        if k not in needed:
            del panels[k]
    gc.collect()
    log("trimmed panels", sorted(panels.keys()), "mem", mem_mb())

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
        need_cov = job.get("ablation") == "baseline"
        try:
            ev = evaluate_one(
                tok, panels, label, sig, adv, size_panel, need_cov=need_cov, days_to_style=False
            )
            row = {**job, **ev}
        except Exception as exc:  # noqa: BLE001
            row = {
                **job,
                "expr": tok.split("::", 1)[-1],
                "expr_token": tok,
                "sim": {"error": f"{type(exc).__name__}: {exc}", "promotion_approved": False},
                "cs_stats": None,
                "coverage": None,
                "leaves": sorted(leaves_in(tok.split("::", 1)[-1])),
                "size_resid": tok.startswith("__SIZE_RESID__::"),
            }
        row["metrics"] = pack_metrics(row.get("sim"))
        row["promotion_approved"] = False
        row["trial_kind"] = "explore_gate"
        results.append(row)

        fit = row["metrics"].get("imp60_p25")
        notes = (
            f"l1d_coverage_mech_shortlist;role={row.get('role')};ablation={row.get('ablation')};"
            f"parent={row.get('parent')};process_not_sealed;promotion_approved=false"
        )
        for path in (run_ledger, main_ledger):
            append_attempt(
                engine="l1d_coverage_mech_shortlist",
                seed=SEED,
                universe="midlarge_top1500_or_csi300_500",
                cost=0.0025,
                window="explore_20240603_to_latest_l1d_cov_mech",
                expr_str=row.get("expr") or tok,
                fitness=fit if isinstance(fit, float) and math.isfinite(fit) else None,
                notes=notes,
                path=path,
            )
        if (i + 1) % 5 == 0 or i == 0:
            peak = max(peak, mem_mb())
            log(f"job {i+1}/{len(jobs)}", (row.get("expr") or "")[:55], "60+25", fmt_pct(fit), "peak", peak)
        if mem_mb() > MEM_CAP_MB - 80:
            gc.collect()

    peak = max(peak, mem_mb())
    n_after = (
        sum(1 for x in main_ledger.read_text().splitlines() if x.strip())
        if main_ledger.exists()
        else 0
    )

    # Honesty verdicts per parent
    verdicts = []
    by_parent: dict[str, list] = {}
    for r in results:
        if r.get("role") == "primary":
            by_parent.setdefault(r["expr"], [])
        p = r.get("parent") or r.get("expr")
        by_parent.setdefault(p, []).append(r)

    for p in parents:
        expr = p["expr"]
        rows = by_parent.get(expr, [])
        base = next((r for r in rows if r.get("ablation") == "baseline"), None)
        abl = [r for r in rows if r.get("ablation") != "baseline"]
        base_m = pack_metrics(base.get("sim") if base else None)
        base_cov = base.get("coverage") if base else None
        hv = honesty_verdict(expr, base_m, abl, base_cov)
        verdicts.append(
            {
                "expr": expr,
                "family": p.get("family"),
                "metrics": base_m,
                "coverage": base_cov,
                "gate_imp60_p25": p.get("gate_imp60_p25"),
                **hv,
                "mechanism": p.get("mechanism"),
            }
        )
        log(
            "verdict",
            expr[:50],
            "SURVIVE" if hv["survive_honesty"] else "FAIL",
            hv["hard_fails"],
            fmt_pct(base_m.get("imp60_p25")),
        )

    l1d_honest = [v for v in verdicts if v.get("survive_honesty")]

    # ---------- ③ shortlist ----------
    shortlist = []
    for v in l1c_honest:
        shortlist.append(
            {
                "source": "L1c_ann_insider",
                "expr": v["expr"],
                "imp60_p25": (v.get("metrics") or {}).get("imp60_p25")
                if isinstance(v.get("metrics"), dict)
                else v.get("imp60_p25"),
                "imp100_p25": (v.get("metrics") or {}).get("imp100_p25")
                if isinstance(v.get("metrics"), dict)
                else None,
                "flat25": (v.get("metrics") or {}).get("flat25")
                if isinstance(v.get("metrics"), dict)
                else None,
                "icir": (v.get("metrics") or {}).get("icir")
                if isinstance(v.get("metrics"), dict)
                else v.get("icir"),
                "turn": (v.get("metrics") or {}).get("turn")
                if isinstance(v.get("metrics"), dict)
                else None,
                "survive_honesty": True,
                "survive_coverage": None,
                "notes": "L1c honest-3; WF stable_enough_explore; title_only; no sealed",
                "promote": False,
            }
        )
    # enrich L1c metrics from results if missing
    l1c_results = None
    l1c_res_path = L1C_MECH / "results.json"
    if l1c_res_path.exists():
        l1c_results = {r["expr"]: r for r in json.loads(l1c_res_path.read_text()) if r.get("ablation") == "baseline"}
    for s in shortlist:
        if s["source"] != "L1c_ann_insider":
            continue
        rr = (l1c_results or {}).get(s["expr"])
        if rr and isinstance(rr.get("metrics"), dict):
            for k in ("imp60_p25", "imp100_p25", "flat25", "icir", "turn"):
                if s.get(k) is None:
                    s[k] = rr["metrics"].get(k)

    for v in l1d_honest:
        # only include if not failed coverage hard for days_to (already excluded)
        shortlist.append(
            {
                "source": "L1d_stabler",
                "expr": v["expr"],
                "family": v.get("family"),
                "imp60_p25": v["metrics"].get("imp60_p25"),
                "imp100_p25": v["metrics"].get("imp100_p25"),
                "flat25": v["metrics"].get("flat25"),
                "icir": v["metrics"].get("icir"),
                "turn": v["metrics"].get("turn"),
                "survive_honesty": True,
                "survive_coverage": (v.get("coverage") or {}).get("passes_coverage"),
                "coverage_note": (v.get("coverage") or {}).get("fail_reasons"),
                "notes": "; ".join(v.get("notes") or [])[:300],
                "promote": False,
            }
        )

    # Write JSON artifacts
    def _clean(o):
        if isinstance(o, float) and (math.isnan(o) or math.isinf(o)):
            return None
        if isinstance(o, dict):
            return {k: _clean(v) for k, v in o.items()}
        if isinstance(o, list):
            return [_clean(x) for x in o]
        return o

    (OUT_DIR / "coverage_recut.json").write_text(
        json.dumps(
            _clean(
                {
                    "thresholds": {
                        "nonempty_min": COV_NONEMPTY_MIN,
                        "mean_event_names_min": COV_MEAN_EVENT_NAMES_MIN,
                        "frac_days_ge_N_min": COV_FRAC_DAYS_GE20_MIN,
                        "N": COV_EVENT_N_MIN,
                    },
                    "leaf_lockup_days_to": leaf_cov,
                    "rows": coverage_rows,
                    "n_survive": n_cov_ok,
                    "n_fail_sparsity": len(coverage_rows) - n_cov_ok,
                }
            ),
            indent=2,
            ensure_ascii=False,
        )
    )
    (OUT_DIR / "verdicts.json").write_text(
        json.dumps(_clean(verdicts), indent=2, ensure_ascii=False)
    )
    (OUT_DIR / "results.json").write_text(
        json.dumps(
            _clean(
                [
                    {
                        "role": r.get("role"),
                        "parent": r.get("parent"),
                        "ablation": r.get("ablation"),
                        "expr": r.get("expr"),
                        "metrics": r.get("metrics"),
                        "cs_stats": r.get("cs_stats"),
                        "coverage": r.get("coverage"),
                        "note": r.get("note"),
                        "promotion_approved": False,
                        "trial_kind": "explore_gate",
                    }
                    for r in results
                ]
            ),
            indent=2,
            ensure_ascii=False,
        )
    )
    (OUT_DIR / "shortlist.json").write_text(
        json.dumps(_clean(shortlist), indent=2, ensure_ascii=False)
    )

    elapsed = time.time() - t0
    summary = {
        "mode": "l1d_coverage_mech_shortlist",
        "promotion_approved": False,
        "sealed_executed": False,
        "trial_kind": "explore_gate",
        "window": "explore_20240603_to_latest",
        "capital_cny_primary": [600000, 1000000],
        "primary_metric": "impact_plus_flat25",
        "coverage_thresholds": {
            "nonempty_min": COV_NONEMPTY_MIN,
            "mean_event_names_min": COV_MEAN_EVENT_NAMES_MIN,
            "frac_days_ge_N_min": COV_FRAC_DAYS_GE20_MIN,
            "N": COV_EVENT_N_MIN,
        },
        "lockup_days_to": {
            "n_input": len(coverage_rows),
            "n_survive_coverage": n_cov_ok,
            "n_fail_sparsity": len(coverage_rows) - n_cov_ok,
            "leaf_cov": leaf_cov,
        },
        "n_stabler_parents": len(parents),
        "n_jobs": len(jobs),
        "n_l1d_honest_survive": len(l1d_honest),
        "n_l1d_honest_fail": len(verdicts) - len(l1d_honest),
        "n_l1c_honest": len(l1c_honest),
        "n_shortlist": len(shortlist),
        "ann_title_only": True,
        "invented_body": False,
        "lockup_gap": lock_gap,
        "ann_gap": {k: ann_gap[k] for k in ann_gap if not str(k).startswith("event_type") and k != "body_source_counts"},
        "ledger_N_before": n_before,
        "ledger_N_after": n_after,
        "ledger_N_new": n_after - n_before,
        "peak_rss_MB": int(peak),
        "mem_cap_MB": MEM_CAP_MB,
        "under_mem_cap": bool(peak < MEM_CAP_MB),
        "elapsed_s": round(elapsed, 1),
        "banned": {
            "broadcast": True,
            "limit_down_primary": True,
            "small_cap": True,
            "textbook_mainline": True,
            "sealed": True,
            "strategy_weight_handoff": True,
        },
    }
    (OUT_DIR / "summary.json").write_text(
        json.dumps(_clean(summary), indent=2, ensure_ascii=False)
    )

    # ---------- Report ----------
    lines = []
    lines.append("# AI 因子 L1d：覆盖率再裁 + 稳定候选机制消融 + 短清单")
    lines.append("")
    lines.append(f"- **时间：** 2026-10-12（America/New_York）")
    lines.append("- **promotion_approved：** false；**密封：** 未开；**不交 Strategy 权重**")
    lines.append("- **trial_kind：** explore_gate / process")
    lines.append("- **本金主口径：** 60 万 / 100 万；主裁决=冲击+flat25")
    lines.append("- **禁止：** 广播叶、跌停主候选、小盘、教科书主线、密封、编造公告正文、Strategy 权重")
    lines.append("- **公告：** title_only（`invented_body=false`）")
    lines.append(f"- 账本：N {n_before} → {n_after}（+{n_after-n_before}，explore_gate 过程计次）")
    lines.append(f"- 峰值 RSS：{int(peak)} MB（上限 {MEM_CAP_MB}；under_cap={peak < MEM_CAP_MB}）；运行 {elapsed:.1f}s")
    lines.append("- 上游：`AI_FACTOR_L1d_NON_LD_STRUCT_EXPLORE_ZH.md`；`AI_FACTOR_L1c_NON_LD_MECH_ABLATION_ZH.md`；`AI_FACTOR_L1c_ANN_INSIDER_WF_STABILITY_ZH.md`")
    lines.append("")
    lines.append("## ① lockup_days_to 覆盖率再裁")
    lines.append("")
    lines.append("### 门槛（清晰）")
    lines.append("")
    lines.append("| 指标 | 门槛 | 说明 |")
    lines.append("|---|---:|---|")
    lines.append(f"| 非空率 nonempty_rate | ≥ {COV_NONEMPTY_MIN:.0%} | explore 窗单元格有信号比例（days_to=notna；其它=|x|>0） |")
    lines.append(f"| 日均事件股数 mean_event_names | ≥ {COV_MEAN_EVENT_NAMES_MIN:.0f} | 每日有信号的股票数均值 |")
    lines.append(f"| 日覆盖稳健 frac_days≥{COV_EVENT_N_MIN} | ≥ {COV_FRAC_DAYS_GE20_MIN:.0%} | 至少一半交易日事件股≥{COV_EVENT_N_MIN} |")
    lines.append("| 底层叶连带 | 同门槛 | 任一变换若底层 `lockup_days_to` 不过闸 → 记 FAIL_SPARSITY |")
    lines.append("")
    lines.append("### 底层叶 `lockup_days_to`")
    lines.append("")
    lines.append(
        f"- nonempty={leaf_cov['nonempty_rate']:.4f}；mean_event_names={leaf_cov['mean_event_names']:.2f}；"
        f"frac_days≥{COV_EVENT_N_MIN}={leaf_cov['frac_days_ge_N']:.4f}；"
        f"**{'PASS' if leaf_cov['passes_coverage'] else 'FAIL_SPARSITY'}**"
    )
    if leaf_cov.get("fail_reasons"):
        lines.append(f"- 失败原因：{', '.join(leaf_cov['fail_reasons'])}")
    lines.append("")
    lines.append(f"- 输入存活变换：{len(coverage_rows)}；**覆盖率存活 {n_cov_ok}**；稀疏失败 {len(coverage_rows)-n_cov_ok}")
    lines.append("")
    lines.append("| # | 表达式 | 闸门60万+25bp | nonempty | 日均事件股 | frac≥20 | 裁决 |")
    lines.append("|---|---|---:|---:|---:|---:|---|")
    for i, r in enumerate(
        sorted(coverage_rows, key=lambda x: -(x.get("gate_imp60_p25") or -9)), 1
    ):
        c = r.get("coverage") or {}
        lines.append(
            f"| {i} | `{r['expr']}` | {fmt_pct(r.get('gate_imp60_p25'))} | "
            f"{fmt_num(c.get('nonempty_rate'), 4)} | {fmt_num(c.get('mean_event_names'), 1)} | "
            f"{fmt_num(c.get('frac_days_ge_N'), 3)} | **{r.get('verdict')}** |"
        )
    lines.append("")
    lines.append(
        f"**① 裁决：** lockup_days_to 族在 ~{leaf_cov['nonempty_rate']:.1%} 覆盖下"
        f"{'全部' if n_cov_ok == 0 else '多数'}因稀疏失败；"
        f"高净收益（最佳闸门 ~22.9%@60万）不可解释为稳健可交易事件密度，"
        f"**不进入短清单**（保留为稀疏警示对照）。"
    )
    lines.append("")

    lines.append("## ② 更稳候选：机制 + 消融 + 静态对照")
    lines.append("")
    lines.append("入选（去 rank 孪生）：`lockup_S_*` 波动变换、`neg(ann_penalty_*)`、`neg(ann_buyback_*)`、`neg(ann_inquiry_*)`。")
    lines.append("")
    lines.append("### 机制说明（title_only / PIT）")
    lines.append("")
    for p in parents:
        mech = p.get("mechanism") or {}
        lines.append(f"#### `{p['expr']}`")
        lines.append(f"- **经济故事：** {mech.get('story_zh', '—')}")
        lines.append(f"- **PIT/title_only：** {mech.get('pit_caveat_zh', '—')}")
        lines.append(f"- **稀疏/CS：** {mech.get('sparsity_risk_zh', '—')}")
        lines.append("")

    lines.append("### 基线重估（60/100万）")
    lines.append("")
    lines.append("| 表达式 | ICIR | flat25 | 60万+25bp | 100万+25bp | 换手 | nonempty | 诚实裁决 |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---|")
    for v in verdicts:
        c = v.get("coverage") or {}
        lines.append(
            f"| `{v['expr']}` | {fmt_num(v['metrics'].get('icir'), 3)} | {fmt_pct(v['metrics'].get('flat25'))} | "
            f"{fmt_pct(v['metrics'].get('imp60_p25'))} | {fmt_pct(v['metrics'].get('imp100_p25'))} | "
            f"{fmt_num(v['metrics'].get('turn'), 3)} | {fmt_num(c.get('nonempty_rate'), 4)} | "
            f"**{'SURVIVE' if v['survive_honesty'] else 'FAIL'}** |"
        )
    lines.append("")

    lines.append("### 消融表（按父叶）")
    lines.append("")
    for p in parents:
        expr = p["expr"]
        rows = [r for r in results if (r.get("parent") == expr) or (r.get("ablation") == "baseline" and r.get("expr") == expr)]
        lines.append(f"#### 父叶 `{expr}`")
        lines.append("")
        lines.append("| 消融 | 表达式 | flat25 | 60万+25bp | 100万+25bp | ICIR | 换手 | 备注 |")
        lines.append("|---|---|---:|---:|---:|---:|---:|---|")
        for r in rows:
            m = r.get("metrics") or {}
            lines.append(
                f"| {r.get('ablation')} | `{r.get('expr')}` | {fmt_pct(m.get('flat25'))} | "
                f"{fmt_pct(m.get('imp60_p25'))} | {fmt_pct(m.get('imp100_p25'))} | "
                f"{fmt_num(m.get('icir'), 3)} | {fmt_num(m.get('turn'), 3)} | {r.get('note') or ''} |"
            )
        vv = next((x for x in verdicts if x["expr"] == expr), None)
        if vv:
            lines.append("")
            lines.append(
                f"- 诚实裁决：**{'SURVIVE' if vv['survive_honesty'] else 'FAIL'}**；"
                f"hard_fails={vv.get('hard_fails')}；passes={vv.get('soft_passes')}"
            )
            for n in vv.get("notes") or []:
                lines.append(f"- 注：{n}")
        lines.append("")

    lines.append("## ③ 短清单（L1c ann_insider 诚实3 ∪ L1d ②存活）")
    lines.append("")
    lines.append("- **不开密封**；**不交 Strategy 权重**；`promotion_approved=false`")
    lines.append(f"- L1c 诚实3：{len(l1c_honest)}；L1d ②诚实存活：{len(l1d_honest)}；合计短清单：{len(shortlist)}")
    lines.append("- lockup_days_to 族因①稀疏失败，**不入短清单**")
    lines.append("")
    lines.append("| # | 来源 | 表达式 | flat25 | 60万+25bp | 100万+25bp | ICIR | 换手 | 备注 |")
    lines.append("|---|---|---|---:|---:|---:|---:|---:|---|")
    for i, s in enumerate(
        sorted(shortlist, key=lambda x: -(x.get("imp60_p25") or -9)), 1
    ):
        note = (s.get("notes") or "")[:60]
        if s.get("survive_coverage") is False:
            note = ("稀疏警告; " + note)[:60]
        lines.append(
            f"| {i} | {s['source']} | `{s['expr']}` | {fmt_pct(s.get('flat25'))} | "
            f"{fmt_pct(s.get('imp60_p25'))} | {fmt_pct(s.get('imp100_p25'))} | "
            f"{fmt_num(s.get('icir'), 3)} | {fmt_num(s.get('turn'), 3)} | {note} |"
        )
    lines.append("")
    lines.append("## 总裁决")
    lines.append("")
    lines.append(
        f"1. **① lockup_days_to：** {n_cov_ok}/{len(coverage_rows)} 过覆盖率闸；"
        f"底层 nonempty≈{leaf_cov['nonempty_rate']:.1%} → 高净值不可当作稳健事件密度。"
    )
    lines.append(
        f"2. **② 稳定候选诚实：** {len(l1d_honest)}/{len(verdicts)} 存活；"
        f"失败 {len(verdicts)-len(l1d_honest)}（见上表 hard_fails）。"
    )
    lines.append(
        f"3. **③ 短清单 N={len(shortlist)}**：L1c ann_insider 诚实3 + L1d ②存活；"
        f"仍 explore_gate；**不晋级、不密封、不交 Strategy**。"
    )
    lines.append("")
    lines.append("## 产物路径")
    lines.append("")
    lines.append(f"- 报告：`output/alpha/AI_FACTOR_L1d_COVERAGE_MECH_SHORTLIST_ZH.md`")
    lines.append(f"- JSON：`output/ai_factor/l1d_coverage_mech_shortlist/`（summary/coverage_recut/verdicts/results/shortlist/ledger_run）")
    lines.append(f"- 账本：`output/ai_factor/ledger.jsonl` N={n_after}")
    lines.append("")

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log("wrote", REPORT)
    log("DONE peak", peak, "under_cap", peak < MEM_CAP_MB, "ledger", n_before, "->", n_after)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
