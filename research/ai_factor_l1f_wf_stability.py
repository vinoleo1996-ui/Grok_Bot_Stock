#!/usr/bin/env python3
"""Shortlist v2c full-8 walk-forward stability (explore).

Covers: ann_insider×2 + L1f newcomers×6 from AI_FACTOR_SHORTLIST_V2c_ZH.md.
promotion_approved=False. No sealed. No Strategy. No small-cap.
Announcements title_only. Memory < 2.5GB.

Report: AI_FACTOR_V2c_WF_STABILITY_ZH.md
JSON:   output/ai_factor/v2c_wf_stability/
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
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/workspace/QuantLab")
SCRATCH = Path("/workspace/scratch/tic")
OUT_DIR = ROOT / "output/ai_factor/v2c_wf_stability"
REPORT = ROOT / "output/alpha/AI_FACTOR_V2c_WF_STABILITY_ZH.md"
# alias note path kept for steering clarity
REPORT_ALIAS_NOTE = "elevated from L1f-only to full v2c N=8"
SW_L1 = ROOT / "data/sw/industry_members_sw_l1.parquet"
CSI300 = ROOT / "data/bench/csi300_000300_akshare_daily.parquet"
V2C_JSON = ROOT / "output/ai_factor/shortlist_v2c/shortlist_v2c.json"

EXPLORE_START = pd.Timestamp("2024-06-03")
LOOKBACK_START = pd.Timestamp("2024-01-02")
TOP_N = 50
K_IMP = 1.0
AUMS = (600_000.0, 1_000_000.0)
FLAT_BPS = (10, 25)
COMMISSION_ONE_WAY = 0.00025
PROMOTION_APPROVED = False
MEM_CAP_MB = 2500
SEED = 20261012
ROLL_IC = 20
ROLL_ICIR = 60
MONTHLY_MIN_DAYS = 8
WEAK_ICIR_MAX = 0.02  # ≈0.01 class volatility leaves

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
    print(f"[v2c_wf {time.time()-t0:5.0f}s {mem_mb():.0f}MB]", *a, flush=True)


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
        a, b = m.group(1).strip(), m.group(2).strip()
        # split on top-level comma already via greedy; for nested rank(...) ok if no nested mul
        return ("op", "mul", _seed_to_tuple(a), _seed_to_tuple(b))
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


def family_of(expr: str) -> str:
    L = leaves_in(expr)
    if any("ann_insider" in x for x in L):
        return "ann_insider"
    if any(x.startswith("fsr") or x == "float_share_ratio" for x in L):
        return "float_share_ratio"
    if "ocf_to_profit" in L or "dv_ttm" in L:
        return "ocf_x_dv"
    return "other"


def coverage_risk_tag(family: str, cov: dict) -> str:
    nr = cov.get("nonempty_rate")
    if family == "ann_insider":
        # deepen has ~2% nonempty; gate_ok has ~52% but event-sparse by design
        if isinstance(nr, float) and nr < 0.08:
            return "ann_insider_sparse_warn"
        return "ann_insider_title_event_sparse_by_design"
    if family == "float_share_ratio":
        if isinstance(nr, float) and nr < 0.08:
            return "fsr_sparse_warn"
        if isinstance(nr, float) and nr < 0.15:
            return "fsr_moderate_coverage"
        return "fsr_coverage_ok"
    if family == "ocf_x_dv":
        return "ocf_dv_dense_ok" if (isinstance(nr, float) and nr >= 0.08) else "ocf_dv_sparse_warn"
    return "coverage_unclassified"


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
    g = s.groupby(s.index.to_period("M"))
    for per, ser in g:
        arr = ser.to_numpy(dtype=float)
        arr = arr[np.isfinite(arr)]
        if len(arr) < MONTHLY_MIN_DAYS:
            continue
        mu = float(arr.mean())
        sd = float(arr.std(ddof=1)) if len(arr) > 1 else float("nan")
        icir_m = float(mu / sd) if sd and sd > 1e-12 else float("nan")
        monthly.append(
            {
                "month": str(per),
                "ic_mean": mu,
                "ic_std": sd,
                "icir": icir_m,
                "n": int(len(arr)),
                "ic_pos_frac": float((arr > 0).mean()),
            }
        )
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
        "roll_ic_mean_month_end": _month_end_sample(roll_mean),
        "roll_icir_month_end": _month_end_sample(roll_icir),
    }


def _month_end_sample(ser: pd.Series) -> list[dict]:
    if ser is None or len(ser) == 0:
        return []
    out = []
    for per, chunk in ser.groupby(ser.index.to_period("M")):
        v = chunk.dropna()
        if len(v) == 0:
            continue
        out.append({"month": str(per), "value": float(v.iloc[-1])})
    return out


def coverage_stats(fac: pd.DataFrame) -> dict:
    sample = fac.loc[fac.index >= EXPLORE_START]
    active = sample.notna() & (sample.abs() > 1e-12)
    nonempty = float(active.to_numpy().mean())
    n_names = active.sum(axis=1).astype(float)
    mean_names = float(n_names.mean()) if len(n_names) else float("nan")
    med_names = float(n_names.median()) if len(n_names) else float("nan")
    frac_ge = float((n_names >= 20).mean()) if len(n_names) else float("nan")
    passes = bool(
        math.isfinite(nonempty)
        and nonempty >= 0.08
        and math.isfinite(mean_names)
        and mean_names >= 50
        and math.isfinite(frac_ge)
        and frac_ge >= 0.80
    )
    fail_reasons = []
    if not (math.isfinite(nonempty) and nonempty >= 0.08):
        fail_reasons.append(f"nonempty<8%({nonempty:.4f})")
    if not (math.isfinite(mean_names) and mean_names >= 50):
        fail_reasons.append(f"mean_event_names<50({mean_names:.2f})")
    if not (math.isfinite(frac_ge) and frac_ge >= 0.80):
        fail_reasons.append(f"frac_days_ge20<80%({frac_ge:.4f})")
    return {
        "nonempty_rate": nonempty,
        "mean_event_names": mean_names,
        "median_event_names": med_names,
        "frac_days_ge_N": frac_ge,
        "N_event_threshold": 20,
        "passes_coverage": passes,
        "fail_reasons": fail_reasons,
    }


def ann_event_coverage(leaf: pd.DataFrame, top_idx_list, dates, cols, explore_idx) -> dict:
    L = leaf.reindex(explore_idx).to_numpy(dtype=np.float64, copy=False)
    T, N = L.shape
    day_any = np.zeros(T, dtype=bool)
    day_n = np.full(T, np.nan)
    day_frac = np.full(T, np.nan)
    top_hit = np.full(T, np.nan)
    for t in range(T):
        row = L[t]
        m = np.isfinite(row)
        if m.sum() < 30:
            continue
        ev = m & (row > 0)
        day_any[t] = bool(ev.any())
        day_n[t] = float(ev.sum())
        day_frac[t] = float(ev.sum() / m.sum())
        ti = top_idx_list[t] if t < len(top_idx_list) else None
        if ti is None:
            continue
        vals = row[ti]
        finite = np.isfinite(vals)
        if finite.sum() == 0:
            continue
        top_hit[t] = float((vals[finite] > 0).mean())
    finite_all = np.isfinite(L)
    n_finite = int(finite_all.sum())
    n_event = int(((L > 0) & finite_all).sum())
    return {
        "frac_days_any_event": float(day_any.mean()) if T else float("nan"),
        "mean_n_event_names_per_day": float(np.nanmean(day_n)),
        "median_n_event_names_per_day": float(np.nanmedian(day_n)),
        "mean_frac_universe_with_event": float(np.nanmean(day_frac)),
        "stock_day_event_rate": float(n_event / n_finite) if n_finite else float("nan"),
        "mean_topN_hit_frac": float(np.nanmean(top_hit)),
        "median_topN_hit_frac": float(np.nanmedian(top_hit)),
        "n_explore_days": int(T),
        "note": "event=ann_insider_dec_5>0 title_only; sparse by design",
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
    alpha_d = float(y.mean() - beta * x.mean())
    resid = y0 - beta * x0
    sy, sx = float(np.sqrt(np.dot(y0, y0))), float(np.sqrt(var))
    corr = float(np.dot(x0, y0) / (sx * sy)) if sx > 1e-12 and sy > 1e-12 else float("nan")
    roll, win = [], 60
    g2, m2 = g[mask], m[mask]
    for i in range(win, len(g2) + 1):
        yy = g2.iloc[i - win : i].to_numpy(dtype=float)
        xx = m2.iloc[i - win : i].to_numpy(dtype=float)
        xx0, yy0 = xx - xx.mean(), yy - yy.mean()
        v = float(np.dot(xx0, xx0))
        if v < 1e-18:
            continue
        roll.append({"date": str(g2.index[i - 1].date()), "beta60": float(np.dot(xx0, yy0) / v)})
    roll_me = []
    if roll:
        ser = pd.Series({pd.Timestamp(r["date"]): r["beta60"] for r in roll})
        for per, chunk in ser.groupby(ser.index.to_period("M")):
            roll_me.append({"month": str(per), "beta60": float(chunk.iloc[-1])})
    return {
        "benchmark": "CSI300 (sh.000300 akshare)",
        "n_overlap_days": int(mask.sum()),
        "beta_full": beta,
        "corr_full": corr,
        "alpha_daily": alpha_d,
        "alpha_ann_naive": float((1.0 + alpha_d) ** 244 - 1.0) if abs(alpha_d) < 0.05 else float("nan"),
        "resid_vol_daily": float(resid.std(ddof=1)),
        "roll_beta60_mean": float(np.mean([r["beta60"] for r in roll])) if roll else float("nan"),
        "roll_beta60_std": float(np.std([r["beta60"] for r in roll], ddof=1)) if len(roll) > 1 else float("nan"),
        "roll_beta60_month_end": roll_me,
        "note": "descriptive OLS Top-N EW gross vs CSI300; not a full risk model",
    }


def build_sw_l1_map(cols: list[str]):
    if not SW_L1.exists():
        return None, {"error": "sw_l1_missing", "path": str(SW_L1)}
    df = pd.read_parquet(SW_L1, columns=["instrument_id", "sw_code", "sw_name", "in_date", "out_date"])
    want = set(cols)
    df = df[df["instrument_id"].isin(want)].copy()
    df["in_ts"] = pd.to_datetime(df["in_date"], errors="coerce")
    df["out_ts"] = pd.to_datetime(df["out_date"], errors="coerce")
    if getattr(df["in_ts"].dt, "tz", None) is not None:
        df["in_ts"] = df["in_ts"].dt.tz_localize(None)
    if getattr(df["out_ts"].dt, "tz", None) is not None:
        df["out_ts"] = df["out_ts"].dt.tz_localize(None)
    mapping: dict[str, list] = {}
    for r in df.itertuples(index=False):
        mapping.setdefault(r.instrument_id, []).append(
            (r.in_ts, r.out_ts, str(r.sw_name), str(r.sw_code))
        )
    meta = {
        "n_universe": len(cols),
        "n_mapped": len(mapping),
        "coverage_frac": float(len(mapping) / len(cols)) if cols else float("nan"),
        "n_sw_names": int(df["sw_name"].nunique()),
        "source": str(SW_L1),
        "quality": "research_sketch_not_promotable; membership PIT via in/out_date",
    }
    return mapping, meta


def sw_name_on(mapping, instrument: str, day: pd.Timestamp) -> str | None:
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
    if mapping is None:
        return {"error": "no_sw_map"}
    daily_hhi, daily_top1, daily_top3, daily_mapped_frac = [], [], [], []
    name_hits: dict[str, int] = {}
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
        "sample_stride_days": sample_stride,
        "n_sampled_days": n_sampled,
        "mean_mapped_frac": float(np.nanmean(daily_mapped_frac)) if daily_mapped_frac else float("nan"),
        "mean_HHI": float(np.mean(daily_hhi)) if daily_hhi else float("nan"),
        "mean_top1_share": float(np.mean(daily_top1)) if daily_top1 else float("nan"),
        "mean_top3_share": float(np.mean(daily_top3)) if daily_top3 else float("nan"),
        "top_industries_by_slot_share": top_industries,
        "note": "SW L1 PIT sketch on Top-N slots; descriptive only",
    }


def pack_cost(sim_like: dict) -> dict:
    def _ann(path):
        cur = sim_like
        for p in path:
            if not isinstance(cur, dict):
                return float("nan")
            cur = cur.get(p)
        return cur.get("ann", float("nan")) if isinstance(cur, dict) else float("nan")

    return {
        "gross": _ann(["gross"]),
        "flat10": _ann(["flat", "10"]),
        "flat25": _ann(["flat", "25"]),
        "imp60": _ann(["impact", "600000"]),
        "imp100": _ann(["impact", "1000000"]),
        "imp60_p25": _ann(["impact", "600000_plus_flat25"]),
        "imp100_p25": _ann(["impact", "1000000_plus_flat25"]),
        "ic_mean": float(sim_like.get("ic_mean") or float("nan")),
        "icir": float(sim_like.get("icir") or float("nan")),
        "turn": float(sim_like.get("mean_turn_ow") or float("nan")),
        "n_days": int(sim_like.get("n_days") or 0),
    }


def stability_verdict(expr: str, family: str, roll: dict, cov: dict, beta: dict, ind: dict, cost: dict, cov_risk: str) -> dict:
    notes, flags, soft = [], [], []
    n_m = roll.get("n_months") or 0
    n_pos = roll.get("n_months_pos_ic") or 0
    pos_frac_m = (n_pos / n_m) if n_m else float("nan")
    roll_pos = roll.get("roll_ic_mean_pos_frac")
    full_icir = roll.get("full_icir")
    cost_icir = cost.get("icir")

    # prefer cost-pack ICIR (same as shortlist) for weak flag; fall back to full
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
        notes.append(f"**弱预测力**：ICIR={icir_ref:.3f}<{WEAK_ICIR_MAX}（波动叶）")

    nr = cov.get("nonempty_rate")
    if isinstance(nr, float) and math.isfinite(nr):
        notes.append(f"nonempty={nr:.2%}；覆盖风险标签={cov_risk}")
        if nr < 0.08:
            flags.append("coverage_sparse")
    if family == "ann_insider":
        notes.append("ann_insider：title_only 事件稀疏族（减持标题）")
    elif family == "float_share_ratio":
        notes.append("FSR 族：连续流通比/差分；非解禁日历事件")

    b = beta.get("beta_full") if isinstance(beta, dict) else None
    if isinstance(b, float) and math.isfinite(b):
        notes.append(f"相对 CSI300 β≈{b:.2f}")
        if abs(b) > 1.3:
            flags.append("high_mkt_beta")
        else:
            soft.append("beta_not_extreme")

    hhi = ind.get("mean_HHI") if isinstance(ind, dict) else None
    if isinstance(hhi, float) and math.isfinite(hhi):
        notes.append(f"Top-N SW L1 均 HHI≈{hhi:.3f}")
        if hhi > 0.20:
            flags.append("industry_concentrated")
        else:
            soft.append("industry_not_highly_concentrated")

    imp60 = cost.get("imp60_p25")
    if isinstance(imp60, float) and math.isfinite(imp60) and imp60 >= 0.10:
        soft.append("cost_gate_holds_60w_ge10pct")
    elif isinstance(imp60, float) and math.isfinite(imp60):
        flags.append("cost_gate_slip")
        notes.append(f"重估 60万+25bp={imp60:.2%} <10%")

    hard = [f for f in flags if f in ("cost_gate_slip", "full_icir_negative")]
    # label triad: stable_enough_explore / weak_icir / unstable
    if hard or len([f for f in flags if f in ("rolling_ic_mean_often_negative", "monthly_ic_weak_majority")]) >= 2:
        label = "unstable"
        stable = False
    elif weak_pred or "weak_predictive_power_icir" in flags:
        label = "weak_icir"
        stable = False  # not "stable_enough" — weak predictive power
    elif len(flags) == 0 and ("monthly_ic_majority_positive" in soft or (pos_frac_m or 0) >= 0.5):
        label = "stable_enough_explore"
        stable = True
    elif "coverage_sparse" in flags and (pos_frac_m or 0) >= 0.55:
        # sparse but IC-stable explore — still flag coverage; treat as stable_enough with note
        label = "stable_enough_explore"
        stable = True
        notes.append("覆盖稀疏但滚动/月度 IC 尚可 → stable_enough_explore（保留 sparse 警示）")
    elif (pos_frac_m or 0) >= 0.5 and "rolling_ic_mean_often_negative" not in flags:
        label = "stable_enough_explore"
        stable = True
    else:
        label = "unstable"
        stable = False

    return {
        "expr": expr,
        "family": family,
        "stable_explore": bool(stable),
        "label": label,
        "weak_predictive_power": bool(weak_pred or "weak_predictive_power_icir" in flags),
        "coverage_risk_tag": cov_risk,
        "flags": flags,
        "soft_passes": soft,
        "notes": notes,
        "promote": False,
        "promotion_approved": False,
        "monthly_ic_pos_frac": pos_frac_m,
        "icir_ref": icir_ref if isinstance(icir_ref, float) else float("nan"),
    }


def fmt_pct(x):
    if isinstance(x, float) and math.isfinite(x):
        return f"{x:.2%}"
    return "—"


def fmt_f(x, nd=3):
    if isinstance(x, float) and math.isfinite(x):
        return f"{x:.{nd}f}"
    return "—"


def load_v2c_jobs() -> list[dict]:
    rows = json.loads(V2C_JSON.read_text(encoding="utf-8"))
    jobs = []
    for r in rows:
        expr = r["expr"]
        fam = r.get("family") or family_of(expr)
        jobs.append(
            {
                "expr": expr,
                "role": r.get("role") or "v2c_member",
                "source": r.get("source"),
                "family": fam,
                "prior_verdict": r.get("verdict"),
                "prior_tag": r.get("tag") or r.get("coverage_tag"),
            }
        )
    return jobs


def write_report(summary, results, peak, n_before, n_after):
    lines = []
    lines.append("# AI 因子短清单 v2c：全 8 条 Walk-Forward 稳定性（探索窗）")
    lines.append("")
    lines.append("- **时间：** 2026-10-12（America/New_York）")
    lines.append("- **promotion_approved：** false；**密封：** 未开；**不交 Strategy 权重**")
    lines.append("- **trial_kind：** explore_gate / process")
    lines.append("- **本金主口径：** 60 万 / 100 万（flat + √冲击；主裁决=冲击+flat25）")
    lines.append("- **禁止：** 小盘主线、教科书主结果、密封窗、广播/跌停主候选")
    lines.append(f"- 账本：N {n_before} → {n_after}（+{n_after-n_before}，explore_gate 过程计次）")
    lines.append(
        f"- 峰值 RSS：{peak:.0f} MB（上限 {MEM_CAP_MB}；under_cap={peak < MEM_CAP_MB}）"
    )
    lines.append(
        "- 上游：`AI_FACTOR_SHORTLIST_V2c_ZH.md`；`AI_FACTOR_L1f_MECH_CORR_ABLATION_ZH.md`；"
        "`AI_FACTOR_L1c_ANN_INSIDER_WF_STABILITY_ZH.md`（ann_insider 先验 WF）"
    )
    lines.append(
        f"- 滚动窗：IC 均值 {ROLL_IC} 日；ICIR {ROLL_ICIR} 日；月度桶 ≥{MONTHLY_MIN_DAYS} 有效 IC 日"
    )
    lines.append(
        f"- **弱预测力阈值：** ICIR < {WEAK_ICIR_MAX}（≈0.01 波动叶）→ 标签 `weak_icir`"
    )
    lines.append(f"- 报告升格说明：{REPORT_ALIAS_NOTE}（全 v2c N=8，非仅 L1f×6）")
    lines.append("")
    lines.append("## 标的表达式（v2c 全员，不晋级）")
    lines.append("")
    lines.append("| # | 来源/角色 | 族 | 表达式 |")
    lines.append("|---|---|---|---|")
    for i, r in enumerate(results, 1):
        lines.append(
            f"| {i} | {r.get('source')}/{r.get('role')} | {r.get('family')} | `{r['expr']}` |"
        )
    lines.append("")
    lines.append("## 成本闸重估（60/100万 + flat25）")
    lines.append("")
    lines.append("| 表达式 | 族 | IC均值 | ICIR | flat25 | 60万+25bp | 100万+25bp | 换手 |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for r in results:
        c = r["cost"]
        lines.append(
            f"| `{r['expr']}` | {r.get('family')} | {fmt_f(c.get('ic_mean'), 4)} | "
            f"{fmt_f(c.get('icir'), 3)} | {fmt_pct(c.get('flat25'))} | "
            f"{fmt_pct(c.get('imp60_p25'))} | {fmt_pct(c.get('imp100_p25'))} | "
            f"{fmt_f(c.get('turn'), 3)} |"
        )
    lines.append("")
    lines.append("## 滚动 IC / ICIR")
    lines.append("")
    lines.append(
        f"| 表达式 | 全样本IC | 全样本ICIR | IC>0日占比 | 滚动{ROLL_IC}d均值>0占比 | "
        f"滚动{ROLL_ICIR}d ICIR均值 | 正IC月数 | 月度正占比 |"
    )
    lines.append("|---|---|---|---|---|---|---|---|")
    for r in results:
        roll = r["rolling_ic"]
        nm = roll.get("n_months") or 1
        lines.append(
            f"| `{r['expr']}` | {fmt_f(roll.get('full_ic_mean'), 4)} | {fmt_f(roll.get('full_icir'), 3)} | "
            f"{fmt_pct(roll.get('full_ic_pos_frac'))} | {fmt_pct(roll.get('roll_ic_mean_pos_frac'))} | "
            f"{fmt_f(roll.get('roll_icir_mean'), 3)} | "
            f"{roll.get('n_months_pos_ic')}/{roll.get('n_months')} | "
            f"{fmt_pct((roll.get('n_months_pos_ic') or 0) / nm)} |"
        )
    lines.append("")
    lines.append("### 月度 IC 明细")
    lines.append("")
    for r in results:
        lines.append(f"#### `{r['expr']}`")
        lines.append("")
        lines.append("| 月 | IC均值 | ICIR | n | IC>0占比 |")
        lines.append("|---|---|---|---|---|")
        for m in r["rolling_ic"].get("monthly") or []:
            lines.append(
                f"| {m['month']} | {fmt_f(m['ic_mean'], 4)} | {fmt_f(m['icir'], 3)} | "
                f"{m['n']} | {fmt_pct(m['ic_pos_frac'])} |"
            )
        lines.append("")

    lines.append("## 换手（Walk 路径）")
    lines.append("")
    lines.append("| 表达式 | 均换手(单向) | p25 | p50 | p75 | p90 |")
    lines.append("|---|---|---|---|---|---|")
    for r in results:
        t = r["turnover_dist"]
        lines.append(
            f"| `{r['expr']}` | {fmt_f(t.get('mean'), 3)} | {fmt_f(t.get('p25'), 3)} | "
            f"{fmt_f(t.get('p50'), 3)} | {fmt_f(t.get('p75'), 3)} | {fmt_f(t.get('p90'), 3)} |"
        )
    lines.append("")

    lines.append("## 覆盖率 + 覆盖风险标注")
    lines.append("")
    lines.append(
        "| 表达式 | 族 | nonempty | 日均活跃名 | 覆盖硬过? | **覆盖风险标签** | 事件覆盖补充 |"
    )
    lines.append("|---|---|---|---|---|---|---|")
    for r in results:
        c = r["coverage"]
        ae = r.get("ann_event_coverage") or {}
        extra = "—"
        if r.get("family") == "ann_insider":
            extra = (
                f"有事件日{fmt_pct(ae.get('frac_days_any_event'))};"
                f"日均事件股{fmt_f(ae.get('mean_n_event_names_per_day'),1)};"
                f"TopN>0 {fmt_pct(ae.get('mean_topN_hit_frac'))}"
            )
        lines.append(
            f"| `{r['expr']}` | {r.get('family')} | {fmt_f(c.get('nonempty_rate'), 4)} | "
            f"{fmt_f(c.get('mean_event_names'), 1)} | {c.get('passes_coverage')} | "
            f"**{r.get('coverage_risk_tag')}** | {extra} |"
        )
    lines.append("")
    lines.append(
        "> **覆盖风险分族：** `ann_insider_*` = title_only 减持事件（语料映射稀疏/加深叶 nonempty≈2%）；"
        "`fsr_*` = 连续流通比差分/波动（非解禁日历）；`ocf_x_dv` = 质量×股息相对密。"
    )
    lines.append("")

    lines.append("## 贝塔草图（相对 CSI300）")
    lines.append("")
    lines.append("| 表达式 | β全样本 | corr | 滚动60d β均值 | 滚动60d β标准差 | n重叠日 |")
    lines.append("|---|---|---|---|---|---|")
    for r in results:
        b = r["beta"]
        if b.get("error"):
            lines.append(f"| `{r['expr']}` | err:{b.get('error')} | — | — | — | {b.get('n', '—')} |")
            continue
        lines.append(
            f"| `{r['expr']}` | {fmt_f(b.get('beta_full'), 3)} | {fmt_f(b.get('corr_full'), 3)} | "
            f"{fmt_f(b.get('roll_beta60_mean'), 3)} | {fmt_f(b.get('roll_beta60_std'), 3)} | "
            f"{b.get('n_overlap_days')} |"
        )
    lines.append("")
    lines.append("> 描述性：Top-N 等权簿 gross 对 CSI300 日收益 OLS；**非完整风险模型**。")
    lines.append("")

    lines.append("## 行业暴露草图（SW L1）")
    lines.append("")
    sw_meta = summary.get("sw_l1_meta") or {}
    lines.append(
        f"- 映射覆盖：{sw_meta.get('n_mapped')}/{sw_meta.get('n_universe')} "
        f"（{fmt_pct(sw_meta.get('coverage_frac'))}）；{sw_meta.get('quality')}"
    )
    lines.append("")
    lines.append("| 表达式 | 映射率 | 均HHI | Top1占比 | Top3占比 | 前3行业（槽位份额） |")
    lines.append("|---|---|---|---|---|---|")
    for r in results:
        ind = r["industry"]
        if ind.get("error"):
            lines.append(f"| `{r['expr']}` | err | — | — | — | — |")
            continue
        tops = ind.get("top_industries_by_slot_share") or []
        top3s = ", ".join(f"{x['sw_name']}({x['share_of_topN_slots']:.0%})" for x in tops[:3])
        lines.append(
            f"| `{r['expr']}` | {fmt_pct(ind.get('mean_mapped_frac'))} | "
            f"{fmt_f(ind.get('mean_HHI'), 3)} | {fmt_pct(ind.get('mean_top1_share'))} | "
            f"{fmt_pct(ind.get('mean_top3_share'))} | {top3s} |"
        )
    lines.append("")

    lines.append("## 稳定性裁决（stable_enough_explore / weak_icir / unstable）")
    lines.append("")
    lines.append("| 表达式 | 标签 | weak_pred? | 覆盖风险 | flags | 笔记摘要 |")
    lines.append("|---|---|---|---|---|---|")
    for r in results:
        v = r["verdict"]
        lines.append(
            f"| `{r['expr']}` | **{v['label']}** | {v.get('weak_predictive_power')} | "
            f"{v.get('coverage_risk_tag')} | {', '.join(v.get('flags') or []) or '—'} | "
            f"{'; '.join((v.get('notes') or [])[:2]) or '—'} |"
        )
    lines.append("")

    lines.append("## 结论（清晰裁决）")
    lines.append("")
    by_label = {}
    for r in results:
        lab = r["verdict"]["label"]
        by_label.setdefault(lab, []).append(r["expr"])
    lines.append(f"- **N=8** 全员评测；`promotion_approved=false`；**不开密封**；不交 Strategy。")
    for lab in ("stable_enough_explore", "weak_icir", "unstable"):
        xs = by_label.get(lab) or []
        lines.append(f"- **{lab}：** {len(xs)}/{len(results)}")
        for e in xs:
            lines.append(f"  - `{e}`")
    n_weak = sum(1 for r in results if r["verdict"].get("weak_predictive_power"))
    lines.append(f"- **弱预测力（ICIR≈0.01 波动叶）显式标注：** {n_weak} 条")
    lines.append(
        "- ann_insider：保留 title_only 事件稀疏风险；加深叶 `abs(ts_std_10(ts_delta_5(...)))` nonempty≈2%。"
    )
    lines.append("- FSR 族：连续流通比通道；与解禁日历无关；覆盖风险按 nonempty 分档。")
    lines.append("")
    lines.append("## 路径")
    lines.append("")
    lines.append(f"- 报告：`{REPORT}`（升格全 v2c；原任务名 L1f_WF 已并入）")
    lines.append(
        f"- 产物：`{OUT_DIR}/`（summary.json / results.json / rolling_ic_monthly.json / "
        "coverage.json / exposure_sketch.json / ledger_run.jsonl）"
    )
    lines.append("- 账本：`output/ai_factor/ledger.jsonl`（explore_gate / process，非 sealed）")
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    global t0
    t0 = time.time()
    peak = mem_mb()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    _ensure_pkgs()
    l1b = _import_mod(
        "ai_factor_l1b_structural_explore",
        ROOT / "research/ai_factor_l1b_structural_explore.py",
    )
    l1c = _import_mod(
        "ai_factor_l1c_explore",
        ROOT / "research/ai_factor_l1c_explore.py",
    )
    l1f = _import_mod(
        "ai_factor_l1f_strict_gate_struct_explore",
        ROOT / "research/ai_factor_l1f_strict_gate_struct_explore.py",
    )
    from quantlab.factors.ops import apply_expr, parse_expr
    from quantlab.factors.ai_factory.ledger import append_attempt

    jobs = load_v2c_jobs()
    assert len(jobs) == 8, f"expected 8 v2c members, got {len(jobs)}"
    needed = set()
    for j in jobs:
        needed |= leaves_in(j["expr"])
    needed.add("ann_insider_dec_5")  # for ann event coverage
    log("jobs", len(jobs), "leaves", sorted(needed))

    log("loading L1b panels")
    panels, label, public, load_meta = l1b.load_structural_panels()
    peak = max(peak, mem_mb())
    del public
    gc.collect()

    if "overnight_ret" in panels:
        mask = panels["overnight_ret"].notna()
        cols = list(panels["overnight_ret"].columns)
        cal = panels["overnight_ret"].index
    else:
        cols = list(next(iter(panels.values())).columns)
        cal = next(iter(panels.values())).index
        mask = None

    # attach L1c for ann_insider leaves
    log("attach L1c ann panels")
    panels, label, _pub2, load_meta = l1c.attach_l1c_panels(panels, label, {}, load_meta)
    peak = max(peak, mem_mb())
    gc.collect()

    # Trim L1b/L1c early — keep only ann leaf needed; free midlarge structural panels
    keep_ann = {"ann_insider_dec_5"} & needed
    for k in list(panels.keys()):
        if k not in keep_ann:
            del panels[k]
    gc.collect()
    log("trimmed L1b/L1c →", sorted(panels.keys()), "mem", f"{mem_mb():.0f}")

    # build L1f dense families (ocf/fsr/dv only — skip dragon/st to save mem)
    log("build L1f ocf/fsr/dv")
    ocf_panels, ocf_gap = l1f.build_ocf_panels(cal, cols, mask)
    # only keep needed ocf leaves
    for k, v in ocf_panels.items():
        if k in needed:
            panels[k] = v
    del ocf_panels
    gc.collect()
    fsr_dv, fsr_gap, dv_gap = l1f.build_fsr_dv_panels(cal, cols, mask)
    for k, v in fsr_dv.items():
        if k in needed:
            panels[k] = v
    del fsr_dv
    gc.collect()
    peak = max(peak, mem_mb())
    log("L1f leaves attached", "peak", f"{peak:.0f}")
    missing = needed - set(panels.keys())
    if missing:
        raise RuntimeError(f"missing leaves: {sorted(missing)}")
    log("trimmed panels", sorted(panels.keys()), "mem", f"{mem_mb():.0f}")

    explore_idx = cal[cal >= EXPLORE_START]
    sig, adv = load_sig_adv(cols, cal)
    peak = max(peak, mem_mb())
    log("sig/adv", sig.shape, "peak", f"{peak:.0f}")

    mkt = load_csi300_ret(explore_idx)
    sw_map, sw_meta = build_sw_l1_map(cols)
    log("sw_l1", sw_meta.get("n_mapped"), "/", sw_meta.get("n_universe"))

    ann_leaf = panels.get("ann_insider_dec_5")

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
        expr = job["expr"]
        fam = job["family"]
        log(f"eval [{i+1}/{len(jobs)}]", fam, expr)
        tup = _seed_to_tuple(expr)
        fac = apply_expr(parse_expr(to_nested_tuple(tup)), panels).astype("float32")
        sim = simulate_paths(fac, label, sig, adv)
        cost = pack_cost(sim)
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
        cov_risk = coverage_risk_tag(fam, cov)
        if fam == "ann_insider" and ann_leaf is not None:
            ann_cov = ann_event_coverage(ann_leaf, sim["top_idx"], sim["dates"], cols, explore_idx)
        else:
            ann_cov = None
        beta = beta_sketch(sim["gross_path"], sim["dates"], mkt)
        ind = industry_exposure_sketch(sim["top_idx"], sim["dates"], cols, sw_map)
        verdict = stability_verdict(expr, fam, roll, cov, beta, ind, cost, cov_risk)

        row = {
            "expr": expr,
            "role": job["role"],
            "source": job["source"],
            "family": fam,
            "prior_verdict": job.get("prior_verdict"),
            "prior_tag": job.get("prior_tag"),
            "cost": cost,
            "rolling_ic": roll,
            "turnover_dist": turn_dist,
            "coverage": cov,
            "coverage_risk_tag": cov_risk,
            "ann_event_coverage": ann_cov,
            "beta": beta,
            "industry": ind,
            "verdict": verdict,
            "promotion_approved": False,
            "trial_kind": "explore_gate",
        }
        results.append(row)

        notes = (
            f"v2c_wf;family={fam};label={verdict.get('label')};cov_risk={cov_risk};"
            f"weak_pred={verdict.get('weak_predictive_power')};"
            f"process_not_sealed;promotion_approved=false"
        )
        fit = cost.get("imp60_p25")
        for path in (run_ledger, main_ledger):
            append_attempt(
                engine="v2c_wf_stability",
                seed=SEED,
                universe="midlarge_top1500_or_csi300_500",
                cost=0.0025,
                window="explore_20240603_to_latest_v2c_wf",
                expr_str=expr,
                fitness=fit if isinstance(fit, float) and math.isfinite(fit) else None,
                notes=notes + (";explore_gate_process" if path == main_ledger else ""),
                path=path,
            )
        peak = max(peak, mem_mb())
        del fac, sim
        gc.collect()
        log(
            "done",
            expr[:56],
            "60+25",
            fmt_pct(cost.get("imp60_p25")),
            "ICIR",
            fmt_f(cost.get("icir"), 3),
            "label",
            verdict.get("label"),
            "mem",
            f"{mem_mb():.0f}",
        )

    n_after = (
        sum(1 for x in main_ledger.read_text().splitlines() if x.strip())
        if main_ledger.exists()
        else 0
    )

    label_counts = {}
    for r in results:
        lab = r["verdict"]["label"]
        label_counts[lab] = label_counts.get(lab, 0) + 1

    summary = {
        "mode": "v2c_wf_stability_full8",
        "report_name": str(REPORT.relative_to(ROOT)),
        "elevated_from": "AI_FACTOR_L1f_WF_STABILITY (scope→full v2c N=8)",
        "promotion_approved": False,
        "sealed_executed": False,
        "trial_kind": "explore_gate",
        "window": "explore_20240603_to_latest",
        "capital_cny_primary": [600_000, 1_000_000],
        "primary_metric": "impact_plus_flat25 @60万/100万",
        "roll_ic_win": ROLL_IC,
        "roll_icir_win": ROLL_ICIR,
        "weak_icir_max": WEAK_ICIR_MAX,
        "n_members": len(results),
        "label_counts": label_counts,
        "verdicts": {r["expr"]: r["verdict"]["label"] for r in results},
        "weak_predictive_power": {
            r["expr"]: r["verdict"].get("weak_predictive_power") for r in results
        },
        "coverage_risk_tags": {r["expr"]: r.get("coverage_risk_tag") for r in results},
        "n_stable_explore": sum(1 for r in results if r["verdict"]["label"] == "stable_enough_explore"),
        "n_weak_icir": sum(1 for r in results if r["verdict"]["label"] == "weak_icir"),
        "n_unstable": sum(1 for r in results if r["verdict"]["label"] == "unstable"),
        "ann_title_only": True,
        "invented_body": False,
        "ocf_gap": ocf_gap,
        "fsr_gap": {k: fsr_gap[k] for k in fsr_gap if not k.startswith("nonempty_") or "fsr" in k},
        "dv_gap_ok": dv_gap.get("ok"),
        "sw_l1_meta": sw_meta,
        "ledger_N_before": n_before,
        "ledger_N_after": n_after,
        "ledger_N_new": n_after - n_before,
        "peak_rss_MB": round(peak),
        "mem_cap_MB": MEM_CAP_MB,
        "under_mem_cap": peak < MEM_CAP_MB,
        "runtime_s": round(time.time() - t0, 1),
        "suggest_sealed": False,
    }

    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str)
    )
    (OUT_DIR / "results.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False, default=str)
    )
    (OUT_DIR / "rolling_ic_monthly.json").write_text(
        json.dumps(
            {r["expr"]: r["rolling_ic"].get("monthly") for r in results},
            indent=2,
            ensure_ascii=False,
        )
    )
    (OUT_DIR / "coverage.json").write_text(
        json.dumps(
            {
                r["expr"]: {
                    "coverage": r["coverage"],
                    "coverage_risk_tag": r.get("coverage_risk_tag"),
                    "ann_event_coverage": r.get("ann_event_coverage"),
                }
                for r in results
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    (OUT_DIR / "exposure_sketch.json").write_text(
        json.dumps(
            {r["expr"]: {"beta": r["beta"], "industry": r["industry"]} for r in results},
            indent=2,
            ensure_ascii=False,
            default=str,
        )
    )

    # also symlink-style copy note under l1f_wf_stability for original path expectation
    alias_dir = ROOT / "output/ai_factor/l1f_wf_stability"
    alias_dir.mkdir(parents=True, exist_ok=True)
    (alias_dir / "README_REDIRECT.txt").write_text(
        "Scope elevated to full v2c N=8.\n"
        f"Canonical outputs: {OUT_DIR}\n"
        f"Canonical report: {REPORT}\n",
        encoding="utf-8",
    )
    # thin pointer report under original L1f name
    alias_report = ROOT / "output/alpha/AI_FACTOR_L1f_WF_STABILITY_ZH.md"
    alias_report.write_text(
        "# （重定向）L1f WF → 已升格为 v2c 全 8 条 WF\n\n"
        "巡检扩 scope：覆盖 shortlist v2c 全员（ann_insider×2 + L1f×6）。\n\n"
        f"- **主报告：** [`AI_FACTOR_V2c_WF_STABILITY_ZH.md`](./AI_FACTOR_V2c_WF_STABILITY_ZH.md)\n"
        f"- **JSON：** `output/ai_factor/v2c_wf_stability/`\n"
        "- promotion_approved=false；不开密封；不交 Strategy\n",
        encoding="utf-8",
    )

    write_report(summary, results, peak, n_before, n_after)
    log("wrote", REPORT, "peak", f"{peak:.0f}", "ledger", f"{n_before}->{n_after}")
    print(
        json.dumps(
            {
                k: summary[k]
                for k in (
                    "n_members",
                    "label_counts",
                    "verdicts",
                    "n_stable_explore",
                    "n_weak_icir",
                    "n_unstable",
                    "peak_rss_MB",
                    "under_mem_cap",
                    "ledger_N_before",
                    "ledger_N_after",
                    "runtime_s",
                    "promotion_approved",
                    "report_name",
                )
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
