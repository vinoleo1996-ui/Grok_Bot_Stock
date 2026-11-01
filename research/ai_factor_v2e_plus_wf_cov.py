#!/usr/bin/env python3
"""Shortlist v2e++ (N=14) WF + capacity + coverage-risk annotation.

Reuses v2c WF for overlapping 8 exprs. Fresh WF for newcomers.
Lockup rows = diversity_secondary only. No GP / sealed / Strategy weights.
Memory soft-cap: peak RSS well under 2.5GB.
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
OUT_DIR = ROOT / "output/ai_factor/shortlist_v2e_plus_wf_cov"
REPORT = ROOT / "output/alpha/AI_FACTOR_SHORTLIST_V2e_plus_WF_COV_ZH.md"
V2E_PLUS = ROOT / "output/ai_factor/shortlist_v2e_plus/shortlist_v2e_plus.json"
V2E_PP = ROOT / "output/ai_factor/shortlist_v2e_plus_plus/shortlist_v2e_plus_plus.json"
V2C_WF_RESULTS = ROOT / "output/ai_factor/v2c_wf_stability/results.json"

EXPLORE_START = pd.Timestamp("2024-06-03")
LOOKBACK_START = pd.Timestamp("2024-01-02")
MEM_CAP_MB = 2500
SOFT_CAP_MB = 2200
SEED = 20261012
ROLL_IC = 20
ROLL_ICIR = 60
WEAK_ICIR_MAX = 0.02
TOP_N = 50
K_IMP = 1.0
AUMS = (600_000.0, 1_000_000.0)
FLAT_BPS = (10, 25)
COMMISSION_ONE_WAY = 0.00025
MONTHLY_MIN_DAYS = 8

OPS = {
    "add", "sub", "mul", "div", "neg", "abs", "rank", "zscore",
    "industry_neutral", "size_neutral",
}
for _k in (1, 5, 10, 20):
    OPS |= {f"delay_{_k}", f"ts_mean_{_k}", f"ts_std_{_k}", f"ts_delta_{_k}", f"ts_max_{_k}"}

FRESH_PRIORITY = [
    "ts_mean_20(sub(ts_mean_5(overnight_ret), ts_max_20(lu_height)))",
    "ts_mean_20(sub(ann_insider_dec_5, ts_max_20(lu_height)))",
    "neg(idx_w500_delta_20)",
    "ts_std_10(gm_pit)",
    "ts_std_10(ts_mean_20(ts_mean_10(lockup_S_20)))",
    "ts_std_10(rank(ts_std_10(lockup_S_20)))",
]

t0 = 0.0
SW_L1 = ROOT / "data/sw/industry_members_sw_l1.parquet"
CSI300 = ROOT / "data/bench/csi300_000300_akshare_daily.parquet"
SCRATCH = Path("/workspace/scratch/tic")


def mem_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def log(*a):
    print(f"[v2e_wf {time.time()-t0:5.0f}s {mem_mb():.0f}MB]", *a, flush=True)


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


def family_of(expr: str, prior_family: str | None = None) -> str:
    if prior_family:
        return prior_family
    L = leaves_in(expr)
    if any("lockup" in x for x in L):
        return "lockup_S"
    if any("ann_insider" in x for x in L) and any("lu_height" in x for x in L):
        return "ann_insider_x_lu_height"
    if any("overnight" in x for x in L) and any("lu_height" in x for x in L):
        return "overnight_x_lu_height"
    if any("ann_insider" in x for x in L):
        return "ann_insider"
    if any(x.startswith("fsr") or x == "float_share_ratio" for x in L):
        return "float_share_ratio"
    if "ocf_to_profit" in L or "dv_ttm" in L:
        return "ocf_x_dv"
    if any("gm" in x for x in L):
        return "earn_roe_delta"
    if any("idx_w500" in x for x in L):
        return "idx_w500_delta"
    return "other"


def coverage_risk_summary(member: dict, cov: dict, fam: str) -> dict:
    tags = []
    prior_tag = str(member.get("tag") or member.get("coverage_tag") or "")
    corr = member.get("corr_info") or {}
    flags = list(corr.get("flags") or [])
    honesty_flags = list((member.get("honesty") or {}).get("flags") or [])
    for f in flags + honesty_flags:
        if f in ("EDGE_WARN", "DIVERSITY_WARN", "SPARSE_WARN", "RANK_WRAP_WARN", "DIVERSITY_SAME_FAMILY") and f not in tags:
            tags.append(f)
    for token in ("EDGE_WARN", "DIVERSITY_WARN", "SPARSE_WARN", "RANK_WRAP_WARN", "DIVERSITY_SAME_FAMILY"):
        if token in prior_tag and token not in tags:
            tags.append(token)
    if "sparse_warn" in prior_tag.lower() or member.get("coverage_tag") == "sparse_warn":
        if "sparse_warn" not in tags and "SPARSE_WARN" not in tags:
            tags.append("sparse_warn")
    if member.get("coverage_tag") == "coverage_pass" or ("coverage_pass" in prior_tag and "sparse" not in prior_tag.lower()):
        if "coverage_pass" not in tags and "sparse_warn" not in tags and "SPARSE_WARN" not in tags:
            tags.append("coverage_pass")
    nr = cov.get("nonempty_rate")
    if isinstance(nr, float) and math.isfinite(nr):
        if nr < 0.08:
            if "sparse_warn" not in tags and "SPARSE_WARN" not in tags:
                tags.append("sparse_warn")
            summary = f"sparse nonempty={nr:.2%}"
        elif nr < 0.15:
            summary = f"event_like nonempty={nr:.2%}"
            if "event_like_coverage" not in tags:
                tags.append("event_like_coverage")
        elif nr < 0.40:
            summary = f"moderate nonempty={nr:.2%}"
        else:
            summary = f"dense nonempty={nr:.2%}"
            if "coverage_pass" not in tags and "sparse_warn" not in tags and "SPARSE_WARN" not in tags:
                tags.append("coverage_pass")
    else:
        summary = "coverage_unknown"
    role = str(member.get("role") or "")
    adj = str(member.get("adjudication_role") or "")
    if "diversity_secondary" in role or adj == "diversity_secondary":
        if "DIVERSITY_WARN" not in tags:
            tags.append("DIVERSITY_WARN")
        summary += "; diversity_secondary_only"
    fam_notes = {
        "ann_insider": "; title_only ann_insider",
        "overnight_x_lu_height": "; overnight×lu_height EDGE watch",
        "ann_insider_x_lu_height": "; ann×lu diversity secondary",
        "idx_w500_delta": "; index reconstitution event-like",
        "lockup_S": "; lockup supply diversity_secondary (not main overlay)",
        "earn_roe_delta": "; gm_pit vol leaf",
        "float_share_ratio": "; FSR continuous (not lockup calendar)",
        "ocf_x_dv": "; ocf×dv dense quality",
    }
    summary += fam_notes.get(fam, "")
    return {
        "tags": tags,
        "summary": summary,
        "nonempty_rate": nr,
        "passes_coverage": cov.get("passes_coverage"),
        "preserved_from_shortlist": prior_tag,
    }


def capacity_robustness_label(cost: dict) -> dict:
    i60 = cost.get("imp60_p25")
    i100 = cost.get("imp100_p25")
    f25 = cost.get("flat25")
    gross = cost.get("gross")
    turn = cost.get("turn")
    notes = []
    if not (isinstance(i60, float) and math.isfinite(i60)):
        return {"label": "cap_unknown", "notes": ["missing imp60_p25"], "gap_60_100": None,
                "imp60_p25": None, "imp100_p25": None, "flat25": None}
    gap = float(i60 - i100) if isinstance(i100, float) and math.isfinite(i100) else float("nan")
    if math.isfinite(gap):
        notes.append(f"Δ(60→100万+25bp)={gap:.2%}")
    if i60 < 0.10:
        label = "cap_fail"
        notes.append("60万+25bp<10% floor")
    elif math.isfinite(gap) and gap >= 0.015:
        label = "cap_fragile"
        notes.append("100万衰减≥1.5pp")
    elif math.isfinite(gap) and gap >= 0.008:
        label = "cap_moderate"
    elif i60 >= 0.15 and (not math.isfinite(gap) or gap < 0.005):
        label = "cap_robust"
    elif i60 >= 0.10:
        label = "cap_ok"
        if i60 < 0.11:
            notes.append("impact barely ≥10%")
    else:
        label = "cap_edge"
    if isinstance(f25, float) and math.isfinite(f25) and isinstance(gross, float) and math.isfinite(gross) and gross > 0:
        notes.append(f"flat25/gross={f25/gross:.2f}")
    if isinstance(turn, float) and math.isfinite(turn):
        notes.append(f"turn={turn:.3f}")
    return {"label": label, "imp60_p25": i60, "imp100_p25": i100 if isinstance(i100, float) else None,
            "flat25": f25 if isinstance(f25, float) else None,
            "gap_60_100": gap if math.isfinite(gap) else None, "notes": notes}


def fmt_pct(x):
    if isinstance(x, float) and math.isfinite(x):
        return f"{x:.2%}"
    return "—"


def fmt_f(x, nd=3):
    if isinstance(x, float) and math.isfinite(x):
        return f"{x:.{nd}f}"
    return "—"



def _ensure_pkgs():
    if "quantlab" not in sys.modules:
        q = types.ModuleType("quantlab")
        q.__path__ = [str(ROOT / "quantlab")]
        sys.modules["quantlab"] = q
    if "quantlab.factors" not in sys.modules or not hasattr(sys.modules["quantlab.factors"], "__path__"):
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
        load(f"quantlab.factors.ai_factory.{name}", ROOT / f"quantlab/factors/ai_factory/{name}.py")


def _import_mod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


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


def simulate_paths(factor, label, sig, adv, *, top_n=TOP_N):
    from quantlab.factors.ai_factory.fitness import daily_rank_ic, icir_from_series

    idx = factor.index.intersection(label.index)
    idx = idx[idx >= EXPLORE_START]
    f = factor.reindex(idx).to_numpy(dtype=np.float64, copy=False)
    y = label.reindex(idx).to_numpy(dtype=np.float64, copy=False)
    s = sig.reindex(idx).to_numpy(dtype=np.float64, copy=False)
    a = adv.reindex(idx).to_numpy(dtype=np.float64, copy=False)
    T, N = f.shape
    gross = np.full(T, np.nan)
    turn_ow = np.full(T, np.nan)
    n_hold = np.full(T, np.nan)
    top_idx = [None] * T
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
        top_idx[t] = cur_idx.astype(np.int32)
        n_hold[t] = float(k)
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
        "dates": [str(d.date()) for d in idx],
        "gross_path": gross,
        "turn_ow_path": turn_ow,
        "n_hold_path": n_hold,
        "top_idx": top_idx,
        "imp_frac": imp_frac,
        "cols": list(factor.columns),
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
    out["ic_series"] = ics
    out["ic_mean"] = float(np.nanmean(ics.to_numpy()))
    out["icir"] = float(icir_from_series(ics))
    return out


def rolling_ic_stats(ics: pd.Series, win_ic=ROLL_IC, win_icir=ROLL_ICIR) -> dict:
    s = ics.dropna()
    if len(s) < win_ic:
        return {"error": "too_short"}
    roll_mean = s.rolling(win_ic, min_periods=max(10, win_ic // 2)).mean()
    roll_std = s.rolling(win_icir, min_periods=max(20, win_icir // 2)).std(ddof=1)
    roll_icir = (s.rolling(win_icir, min_periods=max(20, win_icir // 2)).mean() / roll_std).replace(
        [np.inf, -np.inf], np.nan
    )
    monthly = []
    for per, ser in s.groupby(s.index.to_period("M")):
        arr = ser.to_numpy(dtype=float)
        arr = arr[np.isfinite(arr)]
        if len(arr) < MONTHLY_MIN_DAYS:
            continue
        mu = float(arr.mean())
        sd = float(arr.std(ddof=1)) if len(arr) > 1 else float("nan")
        icir_m = float(mu / sd) if sd and sd > 1e-12 else float("nan")
        monthly.append({
            "month": str(per), "ic_mean": mu, "ic_std": sd, "icir": icir_m,
            "n": int(len(arr)), "ic_pos_frac": float((arr > 0).mean()),
        })
    rm = roll_mean.dropna().to_numpy()
    ri = roll_icir.dropna().to_numpy()
    return {
        "full_ic_mean": float(s.mean()),
        "full_ic_std": float(s.std(ddof=1)),
        "full_icir": float(s.mean() / s.std(ddof=1)) if s.std(ddof=1) > 1e-12 else float("nan"),
        "full_ic_pos_frac": float((s.to_numpy() > 0).mean()),
        "n_ic_days": int(len(s)),
        "roll_ic_win": win_ic,
        "roll_icir_win": win_icir,
        "roll_ic_mean_mean": float(np.nanmean(rm)) if len(rm) else float("nan"),
        "roll_ic_mean_std": float(np.nanstd(rm, ddof=1)) if len(rm) > 1 else float("nan"),
        "roll_ic_mean_pos_frac": float((rm > 0).mean()) if len(rm) else float("nan"),
        "roll_ic_mean_min": float(np.nanmin(rm)) if len(rm) else float("nan"),
        "roll_ic_mean_max": float(np.nanmax(rm)) if len(rm) else float("nan"),
        "roll_icir_mean": float(np.nanmean(ri)) if len(ri) else float("nan"),
        "roll_icir_pos_frac": float((ri > 0).mean()) if len(ri) else float("nan"),
        "roll_icir_min": float(np.nanmin(ri)) if len(ri) else float("nan"),
        "roll_icir_max": float(np.nanmax(ri)) if len(ri) else float("nan"),
        "monthly": monthly,
        "n_months_pos_ic": int(sum(1 for m in monthly if m["ic_mean"] > 0)),
        "n_months": int(len(monthly)),
    }


def coverage_stats(fac: pd.DataFrame) -> dict:
    sample = fac.loc[fac.index >= EXPLORE_START]
    active = sample.notna() & (sample.abs() > 1e-12)
    nonempty = float(active.to_numpy().mean())
    n_names = active.sum(axis=1).astype(float)
    mean_names = float(n_names.mean()) if len(n_names) else float("nan")
    med_names = float(n_names.median()) if len(n_names) else float("nan")
    frac_ge = float((n_names >= 20).mean()) if len(n_names) else float("nan")
    passes = bool(
        math.isfinite(nonempty) and nonempty >= 0.08
        and math.isfinite(mean_names) and mean_names >= 50
        and math.isfinite(frac_ge) and frac_ge >= 0.80
    )
    fail_reasons = []
    if not (math.isfinite(nonempty) and nonempty >= 0.08):
        fail_reasons.append(f"nonempty<8%({nonempty:.4f})")
    if not (math.isfinite(mean_names) and mean_names >= 50):
        fail_reasons.append(f"mean_event_names<50({mean_names:.2f})")
    if not (math.isfinite(frac_ge) and frac_ge >= 0.80):
        fail_reasons.append(f"frac_days_ge20<80%({frac_ge:.4f})")
    return {
        "nonempty_rate": nonempty, "mean_event_names": mean_names,
        "median_event_names": med_names, "frac_days_ge_N": frac_ge,
        "N_event_threshold": 20, "passes_coverage": passes, "fail_reasons": fail_reasons,
    }


def pack_cost(sim_like: dict) -> dict:
    def _ann(path):
        cur = sim_like
        for pth in path:
            if not isinstance(cur, dict):
                return float("nan")
            cur = cur.get(pth)
        return cur.get("ann", float("nan")) if isinstance(cur, dict) else float("nan")
    return {
        "gross": _ann(["gross"]), "flat10": _ann(["flat", "10"]), "flat25": _ann(["flat", "25"]),
        "imp60": _ann(["impact", "600000"]), "imp100": _ann(["impact", "1000000"]),
        "imp60_p25": _ann(["impact", "600000_plus_flat25"]),
        "imp100_p25": _ann(["impact", "1000000_plus_flat25"]),
        "ic_mean": float(sim_like.get("ic_mean") or float("nan")),
        "icir": float(sim_like.get("icir") or float("nan")),
        "turn": float(sim_like.get("mean_turn_ow") or float("nan")),
        "n_days": int(sim_like.get("n_days") or 0),
    }


def load_csi300_ret(index) -> pd.Series:
    df = pd.read_parquet(CSI300)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").drop_duplicates("date").set_index("date")
    return df["close"].astype("float64").pct_change().reindex(index)


def beta_sketch(gross_path: np.ndarray, dates, mkt_ret: pd.Series) -> dict:
    idx = pd.DatetimeIndex(pd.to_datetime(dates))
    g = pd.Series(gross_path, index=idx)
    m = mkt_ret.reindex(idx)
    mask = g.notna() & m.notna()
    if mask.sum() < 40:
        return {"error": "too_few_overlap", "n": int(mask.sum())}
    y = g[mask].to_numpy(dtype=float)
    x = m[mask].to_numpy(dtype=float)
    x0, y0 = x - x.mean(), y - y.mean()
    var = float(np.dot(x0, x0))
    if var < 1e-18:
        return {"error": "mkt_var0"}
    beta = float(np.dot(x0, y0) / var)
    corr = float(np.dot(x0, y0) / (math.sqrt(var) * math.sqrt(np.dot(y0, y0)))) if np.dot(y0, y0) > 0 else float("nan")
    roll = []
    g2, m2 = g[mask], m[mask]
    win = 60
    for i in range(win, len(g2) + 1):
        yy = g2.iloc[i - win : i].to_numpy(dtype=float)
        xx = m2.iloc[i - win : i].to_numpy(dtype=float)
        xx0, yy0 = xx - xx.mean(), yy - yy.mean()
        v = float(np.dot(xx0, xx0))
        if v < 1e-18:
            continue
        roll.append(float(np.dot(xx0, yy0) / v))
    return {
        "benchmark": "CSI300", "n_overlap_days": int(mask.sum()),
        "beta_full": beta, "corr_full": corr,
        "roll_beta60_mean": float(np.mean(roll)) if roll else float("nan"),
        "roll_beta60_std": float(np.std(roll, ddof=1)) if len(roll) > 1 else float("nan"),
        "note": "descriptive OLS Top-N EW gross vs CSI300",
    }


def build_sw_l1_map(cols: list[str]):
    from collections import Counter
    if not SW_L1.exists():
        return None, {"error": "sw_l1_missing"}
    df = pd.read_parquet(SW_L1, columns=["instrument_id", "sw_code", "sw_name", "in_date", "out_date"])
    want = set(cols)
    df = df[df["instrument_id"].isin(want)].copy()
    df["in_ts"] = pd.to_datetime(df["in_date"], errors="coerce")
    df["out_ts"] = pd.to_datetime(df["out_date"], errors="coerce")
    if getattr(df["in_ts"].dt, "tz", None) is not None:
        df["in_ts"] = df["in_ts"].dt.tz_localize(None)
    if getattr(df["out_ts"].dt, "tz", None) is not None:
        df["out_ts"] = df["out_ts"].dt.tz_localize(None)
    mapping = {}
    for r in df.itertuples(index=False):
        mapping.setdefault(r.instrument_id, []).append((r.in_ts, r.out_ts, str(r.sw_name), str(r.sw_code)))
    meta = {
        "n_universe": len(cols), "n_mapped": len(mapping),
        "coverage_frac": float(len(mapping) / len(cols)) if cols else float("nan"),
        "quality": "research_sketch_not_promotable",
    }
    return mapping, meta


def sw_name_on(mapping, instrument: str, day: pd.Timestamp):
    rows = mapping.get(instrument)
    if not rows:
        return None
    d = pd.Timestamp(day)
    if getattr(d, "tzinfo", None) is not None:
        d = d.tz_localize(None)
    for in_ts, out_ts, name, _code in rows:
        if pd.isna(in_ts) or in_ts > d:
            continue
        if pd.notna(out_ts) and out_ts <= d:
            continue
        return name
    return rows[-1][2] if rows else None


def industry_exposure_sketch(top_idx_list, dates, cols, mapping, sample_stride=5) -> dict:
    from collections import Counter
    if mapping is None:
        return {"error": "no_sw_map"}
    daily_hhi, daily_top1, daily_top3, daily_mapped_frac = [], [], [], []
    name_hits = {}
    n_sampled = 0
    for t, di in enumerate(top_idx_list):
        if di is None or t % sample_stride != 0:
            continue
        day = pd.Timestamp(dates[t])
        names = []
        for j in di:
            nm = sw_name_on(mapping, cols[int(j)], day)
            if nm:
                names.append(nm)
                name_hits[nm] = name_hits.get(nm, 0) + 1
        k = len(di)
        mapped = len(names)
        daily_mapped_frac.append(mapped / k if k else float("nan"))
        if mapped == 0:
            continue
        c = Counter(names)
        fracs = np.array([v / mapped for v in c.values()], dtype=float)
        sorted_f = sorted(fracs, reverse=True)
        daily_hhi.append(float((fracs ** 2).sum()))
        daily_top1.append(float(sorted_f[0]))
        daily_top3.append(float(sum(sorted_f[:3])))
        n_sampled += 1
    total_hits = sum(name_hits.values()) or 1
    top_industries = sorted(
        ({"sw_name": k, "share_of_topN_slots": v / total_hits, "hits": v} for k, v in name_hits.items()),
        key=lambda x: -x["share_of_topN_slots"],
    )[:10]
    return {
        "sample_stride_days": sample_stride, "n_sampled_days": n_sampled,
        "mean_mapped_frac": float(np.nanmean(daily_mapped_frac)) if daily_mapped_frac else float("nan"),
        "mean_HHI": float(np.mean(daily_hhi)) if daily_hhi else float("nan"),
        "mean_top1_share": float(np.mean(daily_top1)) if daily_top1 else float("nan"),
        "mean_top3_share": float(np.mean(daily_top3)) if daily_top3 else float("nan"),
        "top_industries_by_slot_share": top_industries,
    }


def stability_verdict(expr, family, roll, cov, beta, ind, cost, cov_risk_tag) -> dict:
    notes, flags, soft = [], [], []
    n_m = roll.get("n_months") or 0
    n_pos = roll.get("n_months_pos_ic") or 0
    pos_frac_m = (n_pos / n_m) if n_m else float("nan")
    roll_pos = roll.get("roll_ic_mean_pos_frac")
    full_icir = roll.get("full_icir")
    cost_icir = cost.get("icir")
    icir_ref = cost_icir if isinstance(cost_icir, float) and math.isfinite(cost_icir) else full_icir
    weak_pred = isinstance(icir_ref, float) and math.isfinite(icir_ref) and 0 < icir_ref < WEAK_ICIR_MAX
    if math.isfinite(pos_frac_m):
        if pos_frac_m >= 0.55:
            soft.append("monthly_ic_majority_positive")
        elif pos_frac_m < 0.45:
            flags.append("monthly_ic_weak_majority")
            notes.append(f"月度 IC 正月占比偏低 {pos_frac_m:.0%} ({n_pos}/{n_m})")
        else:
            notes.append(f"月度 IC 正月占比中性 {pos_frac_m:.0%} ({n_pos}/{n_m})")
    if isinstance(roll_pos, float) and math.isfinite(roll_pos):
        if roll_pos < 0.45:
            flags.append("rolling_ic_mean_often_negative")
            notes.append(f"滚动{ROLL_IC}日 IC 均值>0 占比仅 {roll_pos:.0%}")
        else:
            soft.append("rolling_ic_mean_mostly_nonneg")
    if isinstance(full_icir, float) and math.isfinite(full_icir):
        if full_icir < 0:
            flags.append("full_icir_negative")
            notes.append(f"全样本 ICIR={full_icir:.3f}<0")
        elif full_icir < WEAK_ICIR_MAX:
            flags.append("weak_predictive_power_icir")
            notes.append(f"**弱预测力**：全样本 ICIR={full_icir:.3f}≈0.01 波动叶级")
        elif full_icir < 0.05:
            notes.append(f"全样本 ICIR={full_icir:.3f} 偏弱")
        else:
            soft.append("full_icir_nonneg")
    if weak_pred and "weak_predictive_power_icir" not in flags:
        flags.append("weak_predictive_power_icir")
        notes.append(f"**弱预测力**：ICIR={icir_ref:.3f}<{WEAK_ICIR_MAX}")
    nr = cov.get("nonempty_rate")
    if isinstance(nr, float) and math.isfinite(nr):
        notes.append(f"nonempty={nr:.2%}；覆盖风险={cov_risk_tag}")
        if nr < 0.08:
            flags.append("coverage_sparse")
    b = beta.get("beta_full") if isinstance(beta, dict) else None
    if isinstance(b, float) and math.isfinite(b):
        notes.append(f"相对 CSI300 β≈{b:.2f}")
        soft.append("beta_not_extreme") if abs(b) <= 1.3 else flags.append("high_mkt_beta")
    hhi = ind.get("mean_HHI") if isinstance(ind, dict) else None
    if isinstance(hhi, float) and math.isfinite(hhi):
        notes.append(f"Top-N SW L1 均 HHI≈{hhi:.3f}")
        soft.append("industry_not_highly_concentrated") if hhi <= 0.20 else flags.append("industry_concentrated")
    imp60 = cost.get("imp60_p25")
    if isinstance(imp60, float) and math.isfinite(imp60) and imp60 >= 0.10:
        soft.append("cost_gate_holds_60w_ge10pct")
    elif isinstance(imp60, float) and math.isfinite(imp60):
        flags.append("cost_gate_slip")
        notes.append(f"重估 60万+25bp={imp60:.2%} <10%")
    hard = [f for f in flags if f in ("cost_gate_slip", "full_icir_negative")]
    if hard or len([f for f in flags if f in ("rolling_ic_mean_often_negative", "monthly_ic_weak_majority")]) >= 2:
        label, stable = "unstable", False
    elif weak_pred or "weak_predictive_power_icir" in flags:
        label, stable = "weak_icir", False
    elif len(flags) == 0 and ("monthly_ic_majority_positive" in soft or (pos_frac_m or 0) >= 0.5):
        label, stable = "stable_enough_explore", True
    elif "coverage_sparse" in flags and (pos_frac_m or 0) >= 0.55:
        label, stable = "stable_enough_explore", True
        notes.append("覆盖稀疏但滚动/月度 IC 尚可 → stable_enough_explore")
    elif (pos_frac_m or 0) >= 0.5 and "rolling_ic_mean_often_negative" not in flags:
        label, stable = "stable_enough_explore", True
    else:
        label, stable = "unstable", False
    return {
        "expr": expr, "family": family, "stable_explore": bool(stable), "label": label,
        "weak_predictive_power": bool(weak_pred or "weak_predictive_power_icir" in flags),
        "coverage_risk_tag": cov_risk_tag, "flags": flags, "soft_passes": soft, "notes": notes,
        "promote": False, "promotion_approved": False,
        "monthly_ic_pos_frac": pos_frac_m,
        "icir_ref": icir_ref if isinstance(icir_ref, float) else float("nan"),
    }



def resolve_shortlist():
    if V2E_PP.exists():
        rows = json.loads(V2E_PP.read_text(encoding="utf-8"))
        return rows, "v2e_plus_plus", V2E_PP
    rows = json.loads(V2E_PLUS.read_text(encoding="utf-8"))
    return rows, "v2e_plus", V2E_PLUS


def reuse_v2c_row(v2c_row: dict, member: dict) -> dict:
    fam = family_of(member["expr"], member.get("family"))
    cov = dict(v2c_row.get("coverage") or {})
    if member.get("coverage"):
        cov.update(member["coverage"])
    cost = dict(v2c_row.get("cost") or {})
    sm = member.get("metrics") or {}
    cost_sl = {}
    for k in ("gross", "flat10", "flat25", "imp60", "imp100", "imp60_p25", "imp100_p25", "icir", "ic_mean", "turn"):
        if k in sm and isinstance(sm[k], (int, float)) and math.isfinite(sm[k]):
            cost_sl[k] = float(sm[k])
    cap_cost = dict(cost)
    cap_cost.update(cost_sl)
    cov_risk = coverage_risk_summary(member, cov, fam)
    cap = capacity_robustness_label(cap_cost)
    verdict = dict(v2c_row.get("verdict") or {})
    tag = "|".join(cov_risk["tags"]) or cov_risk["summary"]
    verdict["coverage_risk_tag"] = tag
    return {
        "expr": member["expr"], "role": member.get("role"), "source": member.get("source"),
        "family": fam, "adjudication_role": member.get("adjudication_role"),
        "prior_verdict": member.get("verdict"),
        "prior_tag": member.get("tag") or member.get("coverage_tag"),
        "cost": cost, "cost_shortlist": cost_sl,
        "rolling_ic": v2c_row.get("rolling_ic"),
        "turnover_dist": v2c_row.get("turnover_dist"),
        "coverage": cov, "coverage_risk": cov_risk, "coverage_risk_tag": tag,
        "ann_event_coverage": v2c_row.get("ann_event_coverage"),
        "beta": v2c_row.get("beta"), "industry": v2c_row.get("industry"),
        "capacity": cap, "verdict": verdict,
        "wf_provenance": "reuse_v2c_wf_stability",
        "wf_source_path": "output/ai_factor/v2c_wf_stability/results.json",
        "promotion_approved": False, "trial_kind": "explore_gate",
        "diagnostic_overlay_candidate": bool(member.get("diagnostic_overlay_candidate")),
    }


def eval_one(expr, panels, label, sig, adv, mkt, sw_map, cols, member):
    from quantlab.factors.ops import apply_expr, parse_expr
    fam = family_of(expr, member.get("family"))
    tup = _seed_to_tuple(expr)
    fac = apply_expr(parse_expr(to_nested_tuple(tup)), panels).astype("float32")
    sim = simulate_paths(fac, label, sig, adv)
    cost = pack_cost(sim)
    sm = member.get("metrics") or {}
    cost_sl = {k: float(sm[k]) for k in (
        "gross", "flat10", "flat25", "imp60", "imp100", "imp60_p25", "imp100_p25", "icir", "ic_mean", "turn"
    ) if k in sm and isinstance(sm[k], (int, float)) and math.isfinite(sm[k])}
    roll = rolling_ic_stats(sim["ic_series"])
    tp = sim["turn_ow_path"]
    tp_ok = tp[np.isfinite(tp)]
    turn_dist = {
        "mean": float(np.mean(tp_ok)) if len(tp_ok) else float("nan"),
        "p25": float(np.percentile(tp_ok, 25)) if len(tp_ok) else float("nan"),
        "p50": float(np.percentile(tp_ok, 50)) if len(tp_ok) else float("nan"),
        "p75": float(np.percentile(tp_ok, 75)) if len(tp_ok) else float("nan"),
        "p90": float(np.percentile(tp_ok, 90)) if len(tp_ok) else float("nan"),
        "n": int(len(tp_ok)),
    }
    cov = coverage_stats(fac)
    if member.get("coverage"):
        cov = {**cov, **member["coverage"]}
    cov_risk = coverage_risk_summary(member, cov, fam)
    tag = "|".join(cov_risk["tags"]) or cov_risk["summary"]
    beta = beta_sketch(sim["gross_path"], sim["dates"], mkt)
    ind = industry_exposure_sketch(sim["top_idx"], sim["dates"], cols, sw_map)
    verdict = stability_verdict(expr, fam, roll, cov, beta, ind, cost, tag)
    cap_cost = dict(cost)
    cap_cost.update(cost_sl)
    cap = capacity_robustness_label(cap_cost)
    row = {
        "expr": expr, "role": member.get("role"), "source": member.get("source"),
        "family": fam, "adjudication_role": member.get("adjudication_role"),
        "prior_verdict": member.get("verdict"),
        "prior_tag": member.get("tag") or member.get("coverage_tag"),
        "cost": cost, "cost_shortlist": cost_sl,
        "rolling_ic": roll, "turnover_dist": turn_dist,
        "coverage": cov, "coverage_risk": cov_risk, "coverage_risk_tag": tag,
        "beta": beta, "industry": ind, "capacity": cap, "verdict": verdict,
        "wf_provenance": "fresh_wf_this_run",
        "promotion_approved": False, "trial_kind": "explore_gate",
        "diagnostic_overlay_candidate": bool(member.get("diagnostic_overlay_candidate")),
    }
    del fac, sim
    gc.collect()
    return row


def write_report(summary, results, peak, n_before, n_after, universe_name):
    n = len(results)
    lines = []
    lines.append(f"# AI 因子短清单 {universe_name}：Walk-Forward + 容量稳健 + 覆盖风险标注（N={n}）")
    lines.append("")
    lines.append("- **时间：** 2026-10-12（America/New_York）")
    lines.append("- **promotion_approved：** false；**密封：** 未开；**不交 Strategy 权重**；**不开 GP**")
    lines.append("- **trial_kind：** explore_gate / process")
    lines.append("- **本金主口径：** 60 万 / 100 万（flat + √冲击；主裁决=冲击+flat25）")
    lines.append(f"- **宇宙：** {universe_name}（报告文件名保持 V2e_plus_WF_COV；成员以本 JSON 为准）")
    lines.append(f"- 账本：N {n_before} → {n_after}（+{n_after-n_before}，explore_gate 过程计次）")
    lines.append(
        f"- 峰值 RSS：{peak:.0f} MB（硬上限 {MEM_CAP_MB}；软帽 {SOFT_CAP_MB}；"
        f"under_soft={peak < SOFT_CAP_MB}）"
    )
    lines.append(
        "- 上游：`AI_FACTOR_SHORTLIST_V2e_plus_plus`（N=14）；"
        "`AI_FACTOR_V2c_WF_STABILITY_ZH.md`（8 条复用）"
    )
    lines.append(
        f"- 滚动窗：IC 均值 {ROLL_IC} 日；ICIR {ROLL_ICIR} 日；弱预测力 ICIR < {WEAK_ICIR_MAX}"
    )
    lines.append("- **复用：** v2c 重叠 8 条 WF 数字复用并标注 provenance；新叶新鲜跑 WF")
    lines.append("- **lockup 新员：** 均为 **diversity_secondary only**（无主 overlay）")
    lines.append("- **成员身份未改**（本任务只标注）")
    lines.append("")
    lines.append("## 成员一览与一句话稳定性裁决")
    lines.append("")
    lines.append("| # | role | 表达式 | WF标签 | 容量 | 覆盖风险 | provenance | 一句话 |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(results, 1):
        v = r.get("verdict") or {}
        cap = r.get("capacity") or {}
        one = (v.get("notes") or ["—"])[0]
        if len(one) > 90:
            one = one[:87] + "…"
        lines.append(
            f"| {i} | {r.get('role')} | `{r['expr']}` | **{v.get('label')}** | "
            f"{cap.get('label')} | {r.get('coverage_risk_tag')} | "
            f"{r.get('wf_provenance')} | {one} |"
        )
    lines.append("")
    lines.append("## 成本闸 / 容量稳健（60/100万 + flat25）")
    lines.append("")
    lines.append("| 表达式 | ICIR | flat25 | 60万+25bp | 100万+25bp | Δ60→100 | 换手 | **容量标签** |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for r in results:
        base = dict(r.get("cost") or {})
        base.update({k: v for k, v in (r.get("cost_shortlist") or {}).items() if v is not None})
        cap = r.get("capacity") or {}
        gap = cap.get("gap_60_100")
        lines.append(
            f"| `{r['expr']}` | {fmt_f(base.get('icir'), 3)} | {fmt_pct(base.get('flat25'))} | "
            f"{fmt_pct(base.get('imp60_p25'))} | {fmt_pct(base.get('imp100_p25'))} | "
            f"{fmt_pct(gap) if isinstance(gap, float) and math.isfinite(gap) else '—'} | "
            f"{fmt_f(base.get('turn'), 3)} | **{cap.get('label')}** |"
        )
    lines.append("")
    lines.append(
        "> 容量：`cap_robust`（高净值且 60→100 衰减<0.5pp）；`cap_ok`；`cap_moderate`（≥0.8pp）；"
        "`cap_fragile`（≥1.5pp）；`cap_fail`（<10%）。"
    )
    lines.append("")
    lines.append("## 滚动 IC / ICIR（探索窗）")
    lines.append("")
    lines.append(
        f"| 表达式 | 全样本IC | 全样本ICIR | IC>0日占比 | 滚动{ROLL_IC}d均值>0占比 | "
        f"滚动{ROLL_ICIR}d ICIR均值 | 正IC月数 | 月度正占比 |"
    )
    lines.append("|---|---|---|---|---|---|---|---|")
    for r in results:
        roll = r.get("rolling_ic") or {}
        nm = roll.get("n_months") or 1
        lines.append(
            f"| `{r['expr']}` | {fmt_f(roll.get('full_ic_mean'), 4)} | {fmt_f(roll.get('full_icir'), 3)} | "
            f"{fmt_pct(roll.get('full_ic_pos_frac'))} | {fmt_pct(roll.get('roll_ic_mean_pos_frac'))} | "
            f"{fmt_f(roll.get('roll_icir_mean'), 3)} | "
            f"{roll.get('n_months_pos_ic')}/{roll.get('n_months')} | "
            f"{fmt_pct((roll.get('n_months_pos_ic') or 0) / nm)} |"
        )
    lines.append("")
    lines.append("### 月度 IC 明细（仅新鲜 WF；复用见 v2c 报告）")
    lines.append("")
    for r in results:
        if r.get("wf_provenance") != "fresh_wf_this_run":
            continue
        lines.append(f"#### `{r['expr']}`")
        lines.append("")
        lines.append("| 月 | IC均值 | ICIR | n | IC>0占比 |")
        lines.append("|---|---|---|---|---|")
        for m in (r.get("rolling_ic") or {}).get("monthly") or []:
            lines.append(
                f"| {m['month']} | {fmt_f(m['ic_mean'], 4)} | {fmt_f(m['icir'], 3)} | "
                f"{m['n']} | {fmt_pct(m['ic_pos_frac'])} |"
            )
        lines.append("")
    lines.append("> 复用成员月度明细：`AI_FACTOR_V2c_WF_STABILITY_ZH.md`（provenance=`reuse_v2c_wf_stability`）。")
    lines.append("")
    lines.append("## 换手分布")
    lines.append("")
    lines.append("| 表达式 | 均换手 | p25 | p50 | p75 | p90 |")
    lines.append("|---|---|---|---|---|---|")
    for r in results:
        t = r.get("turnover_dist") or {}
        lines.append(
            f"| `{r['expr']}` | {fmt_f(t.get('mean'), 3)} | {fmt_f(t.get('p25'), 3)} | "
            f"{fmt_f(t.get('p50'), 3)} | {fmt_f(t.get('p75'), 3)} | {fmt_f(t.get('p90'), 3)} |"
        )
    lines.append("")
    lines.append("## 覆盖风险标注（保留 EDGE_WARN / DIVERSITY_WARN / sparse / coverage_pass）")
    lines.append("")
    lines.append("| 表达式 | nonempty | 硬过? | **tags** | summary |")
    lines.append("|---|---|---|---|---|")
    for r in results:
        cr = r.get("coverage_risk") or {}
        c = r.get("coverage") or {}
        lines.append(
            f"| `{r['expr']}` | {fmt_f(c.get('nonempty_rate'), 4)} | {c.get('passes_coverage')} | "
            f"**{' / '.join(cr.get('tags') or []) or '—'}** | {cr.get('summary')} |"
        )
    lines.append("")
    lines.append("## 贝塔草图（CSI300）+ 行业 HHI")
    lines.append("")
    lines.append("| 表达式 | β | corr | rollβ均值 | 均HHI | Top1 | 前3行业 |")
    lines.append("|---|---|---|---|---|---|---|")
    for r in results:
        b = r.get("beta") or {}
        ind = r.get("industry") or {}
        tops = ind.get("top_industries_by_slot_share") or []
        top3s = ", ".join(f"{x['sw_name']}({x['share_of_topN_slots']:.0%})" for x in tops[:3]) or "—"
        if b.get("error"):
            lines.append(
                f"| `{r['expr']}` | err | — | — | {fmt_f(ind.get('mean_HHI'),3)} | — | {top3s} |"
            )
        else:
            lines.append(
                f"| `{r['expr']}` | {fmt_f(b.get('beta_full'), 3)} | {fmt_f(b.get('corr_full'), 3)} | "
                f"{fmt_f(b.get('roll_beta60_mean'), 3)} | {fmt_f(ind.get('mean_HHI'), 3)} | "
                f"{fmt_pct(ind.get('mean_top1_share'))} | {top3s} |"
            )
    lines.append("")
    lines.append("> β/HHI 描述性草图，非完整风险模型；不晋级。")
    lines.append("")
    lines.append("## 稳定性裁决汇总")
    lines.append("")
    by_label = {}
    for r in results:
        lab = (r.get("verdict") or {}).get("label") or "unknown"
        by_label.setdefault(lab, []).append(r["expr"])
    lines.append(f"- **N={n}**（宇宙={universe_name}）；`promotion_approved=false`；不开密封；不交 Strategy。")
    for lab in ("stable_enough_explore", "weak_icir", "unstable", "unknown"):
        xs = by_label.get(lab) or []
        if not xs:
            continue
        lines.append(f"- **{lab}：** {len(xs)}/{n}")
        for e in xs:
            lines.append(f"  - `{e}`")
    n_reuse = sum(1 for r in results if r.get("wf_provenance") == "reuse_v2c_wf_stability")
    n_fresh = sum(1 for r in results if r.get("wf_provenance") == "fresh_wf_this_run")
    lines.append(f"- **provenance：** reuse_v2c={n_reuse}；fresh={n_fresh}")
    lines.append("- **lockup×2：** diversity_secondary only；勿升主 overlay。")
    lines.append("")
    lines.append("## 路径")
    lines.append("")
    lines.append(f"- 报告：`{REPORT.relative_to(ROOT)}`")
    lines.append(
        f"- JSON：`{OUT_DIR.relative_to(ROOT)}/`（summary.json / results.json / members/ / "
        "rolling_ic_monthly.json / coverage.json / exposure_sketch.json）"
    )
    lines.append("- 账本：`output/ai_factor/ledger.jsonl`（explore_gate / process，非 sealed）")
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    global t0
    t0 = time.time()
    peak = mem_mb()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "members").mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    _ensure_pkgs()
    members, universe_name, sl_path = resolve_shortlist()
    log("universe", universe_name, "N", len(members), "from", sl_path)
    assert len(members) >= 12, f"expected >=12, got {len(members)}"

    v2c_results = json.loads(V2C_WF_RESULTS.read_text(encoding="utf-8"))
    v2c_by_expr = {r["expr"]: r for r in v2c_results}

    results_by_expr = {}
    fresh_jobs = []
    for m in members:
        expr = m["expr"]
        if expr in v2c_by_expr:
            results_by_expr[expr] = reuse_v2c_row(v2c_by_expr[expr], m)
        else:
            fresh_jobs.append(m)
    pri = {e: i for i, e in enumerate(FRESH_PRIORITY)}
    fresh_jobs.sort(key=lambda m: pri.get(m["expr"], 100))
    log("reuse", len(results_by_expr), "fresh", len(fresh_jobs), [m["expr"][:50] for m in fresh_jobs])

    l1b = _import_mod("ai_factor_l1b_structural_explore", ROOT / "research/ai_factor_l1b_structural_explore.py")
    l1c = _import_mod("ai_factor_l1c_explore", ROOT / "research/ai_factor_l1c_explore.py")
    l1g = _import_mod("ai_factor_l1g_new_mech_family_explore", ROOT / "research/ai_factor_l1g_new_mech_family_explore.py")
    l1h = _import_mod("ai_factor_l1h_new_mech_family_explore", ROOT / "research/ai_factor_l1h_new_mech_family_explore.py")
    from quantlab.factors.ai_factory.ledger import append_attempt

    needed = set()
    for m in fresh_jobs:
        needed |= leaves_in(m["expr"])
    needed |= {"ann_insider_dec_5", "overnight_ret", "lu_height", "lockup_S_20"}
    log("needed", sorted(needed))

    log("load L1b")
    panels, label, public, load_meta = l1b.load_structural_panels()
    peak = max(peak, mem_mb())
    del public
    gc.collect()
    cols = list(panels["overnight_ret"].columns)
    cal = panels["overnight_ret"].index
    mask = panels["overnight_ret"].notna()

    log("attach L1c")
    panels, label, _p2, load_meta = l1c.attach_l1c_panels(panels, label, {}, load_meta)
    peak = max(peak, mem_mb())
    gc.collect()

    keep = set(needed) | {"overnight_ret", "limit_up_flag", "lu_streak", "lockup_S_20"}
    for k in list(panels.keys()):
        if k not in keep:
            del panels[k]
    gc.collect()
    log("trimmed", sorted(panels.keys()), f"{mem_mb():.0f}MB")

    if "gm_pit" in needed:
        log("build gm_pit")
        roe_p, _g = l1g.build_roe_panels(cal, cols, mask)
        if "gm_pit" in roe_p:
            panels["gm_pit"] = roe_p["gm_pit"]
        del roe_p
        gc.collect()
        peak = max(peak, mem_mb())

    if "idx_w500_delta_20" in needed:
        log("build idx")
        idx_p, _i = l1h.build_idx_panels(cal, cols, mask)
        if "idx_w500_delta_20" in idx_p:
            panels["idx_w500_delta_20"] = idx_p["idx_w500_delta_20"]
        del idx_p
        gc.collect()
        peak = max(peak, mem_mb())

    missing = needed - set(panels.keys())
    if missing:
        log("WARN missing", sorted(missing))

    explore_idx = cal[cal >= EXPLORE_START]
    sig, adv = load_sig_adv(cols, cal)
    peak = max(peak, mem_mb())
    log("sig/adv", sig.shape, f"peak={peak:.0f}")
    mkt = load_csi300_ret(explore_idx)
    sw_map, sw_meta = build_sw_l1_map(cols)

    main_ledger = ROOT / "output/ai_factor/ledger.jsonl"
    run_ledger = OUT_DIR / "ledger_run.jsonl"
    if run_ledger.exists():
        run_ledger.unlink()
    n_before = sum(1 for x in main_ledger.read_text().splitlines() if x.strip()) if main_ledger.exists() else 0

    for i, job in enumerate(fresh_jobs):
        expr = job["expr"]
        need = leaves_in(expr)
        if need - set(panels.keys()):
            log("SKIP", expr, sorted(need - set(panels.keys())))
            continue
        if mem_mb() > SOFT_CAP_MB:
            gc.collect()
            log("soft-cap gc", f"{mem_mb():.0f}")
        log(f"fresh [{i+1}/{len(fresh_jobs)}]", expr[:70])
        row = eval_one(expr, panels, label, sig, adv, mkt, sw_map, cols, job)
        results_by_expr[expr] = row
        (OUT_DIR / "members" / f"fresh_{i+1:02d}.json").write_text(
            json.dumps(row, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
        )
        fit = (row.get("cost") or {}).get("imp60_p25")
        notes = (
            f"v2e_plus_wf_cov;universe={universe_name};label={row['verdict'].get('label')};"
            f"cap={row['capacity'].get('label')};cov={row.get('coverage_risk_tag')};"
            f"provenance=fresh;promotion_approved=false"
        )
        for path in (run_ledger, main_ledger):
            append_attempt(
                engine="v2e_plus_wf_cov", seed=SEED,
                universe="midlarge_top1500_or_csi300_500", cost=0.0025,
                window="explore_20240603_to_latest_v2e_plus_wf_cov",
                expr_str=expr,
                fitness=fit if isinstance(fit, float) and math.isfinite(fit) else None,
                notes=notes + (";explore_gate_process" if path == main_ledger else ""),
                path=path,
            )
        peak = max(peak, mem_mb())
        log("done", row["verdict"].get("label"), row["capacity"].get("label"),
            "ICIR", fmt_f((row.get("cost") or {}).get("icir"), 3), f"{mem_mb():.0f}MB")

    # free heavy panels before report
    del panels, sig, adv
    gc.collect()

    n_after = sum(1 for x in main_ledger.read_text().splitlines() if x.strip()) if main_ledger.exists() else 0

    results = []
    for m in members:
        if m["expr"] in results_by_expr:
            results.append(results_by_expr[m["expr"]])
        else:
            log("MISSING result for", m["expr"])

    for i, r in enumerate(results):
        (OUT_DIR / "members" / f"member_{i+1:02d}.json").write_text(
            json.dumps(r, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
        )

    label_counts = {}
    for r in results:
        lab = (r.get("verdict") or {}).get("label") or "unknown"
        label_counts[lab] = label_counts.get(lab, 0) + 1

    peak = max(peak, mem_mb())
    summary = {
        "mode": "v2e_plus_wf_cov",
        "universe": universe_name,
        "report_name": str(REPORT.relative_to(ROOT)),
        "shortlist_path": str(sl_path.relative_to(ROOT)),
        "promotion_approved": False,
        "sealed_executed": False,
        "trial_kind": "explore_gate",
        "window": "explore_20240603_to_latest",
        "n_members": len(results),
        "label_counts": label_counts,
        "verdicts": {r["expr"]: (r.get("verdict") or {}).get("label") for r in results},
        "capacity_labels": {r["expr"]: (r.get("capacity") or {}).get("label") for r in results},
        "coverage_risk_tags": {r["expr"]: r.get("coverage_risk_tag") for r in results},
        "wf_provenance": {r["expr"]: r.get("wf_provenance") for r in results},
        "one_line_verdicts": {
            r["expr"]: ((r.get("verdict") or {}).get("notes") or ["—"])[0] for r in results
        },
        "n_stable_explore": sum(1 for r in results if (r.get("verdict") or {}).get("label") == "stable_enough_explore"),
        "n_weak_icir": sum(1 for r in results if (r.get("verdict") or {}).get("label") == "weak_icir"),
        "n_unstable": sum(1 for r in results if (r.get("verdict") or {}).get("label") == "unstable"),
        "n_reuse_v2c": sum(1 for r in results if r.get("wf_provenance") == "reuse_v2c_wf_stability"),
        "n_fresh": sum(1 for r in results if r.get("wf_provenance") == "fresh_wf_this_run"),
        "lockup_roles": "diversity_secondary_only",
        "sw_l1_meta": sw_meta,
        "ledger_N_before": n_before,
        "ledger_N_after": n_after,
        "ledger_N_new": n_after - n_before,
        "peak_rss_MB": round(peak),
        "mem_cap_MB": MEM_CAP_MB,
        "soft_cap_MB": SOFT_CAP_MB,
        "under_mem_cap": peak < MEM_CAP_MB,
        "under_soft_cap": peak < SOFT_CAP_MB,
        "runtime_s": round(time.time() - t0, 1),
        "suggest_sealed": False,
        "membership_unchanged": True,
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    (OUT_DIR / "results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    (OUT_DIR / "rolling_ic_monthly.json").write_text(json.dumps(
        {r["expr"]: (r.get("rolling_ic") or {}).get("monthly") for r in results}, indent=2, ensure_ascii=False
    ), encoding="utf-8")
    (OUT_DIR / "coverage.json").write_text(json.dumps({
        r["expr"]: {"coverage": r.get("coverage"), "coverage_risk": r.get("coverage_risk"),
                    "coverage_risk_tag": r.get("coverage_risk_tag")} for r in results
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT_DIR / "exposure_sketch.json").write_text(json.dumps({
        r["expr"]: {"beta": r.get("beta"), "industry": r.get("industry"), "capacity": r.get("capacity")}
        for r in results
    }, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    write_report(summary, results, peak, n_before, n_after, universe_name)
    log("wrote", REPORT, "peak", f"{peak:.0f}", "N", len(results), universe_name)
    print(json.dumps({
        "n_members": summary["n_members"], "universe": universe_name,
        "label_counts": label_counts, "verdicts": summary["verdicts"],
        "capacity_labels": summary["capacity_labels"],
        "peak_rss_MB": summary["peak_rss_MB"], "under_soft_cap": summary["under_soft_cap"],
        "runtime_s": summary["runtime_s"], "report": str(REPORT.relative_to(ROOT)),
        "one_line_verdicts": summary["one_line_verdicts"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
