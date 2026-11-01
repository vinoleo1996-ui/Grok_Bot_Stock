"""Cost/turnover-aware fitness helpers for L1 GP. promotion_approved=False always."""
from __future__ import annotations

from typing import Mapping

import numpy as np
import pandas as pd

PROMOTION_APPROVED = False


def _cs_rank_ic_matrix(f: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Per-row Spearman IC; f,y shape (T,N). Returns (T,) with nan where <30 valid."""
    T, N = f.shape
    out = np.full(T, np.nan, dtype=np.float64)
    for t in range(T):
        ft, yt = f[t], y[t]
        m = np.isfinite(ft) & np.isfinite(yt)
        n = int(m.sum())
        if n < 20:
            continue
        a = ft[m]
        b = yt[m]
        # average ranks
        ra = a.argsort().argsort().astype(np.float64)
        rb = b.argsort().argsort().astype(np.float64)
        ra -= ra.mean()
        rb -= rb.mean()
        da = np.sqrt((ra * ra).sum())
        db = np.sqrt((rb * rb).sum())
        if da < 1e-12 or db < 1e-12:
            continue
        out[t] = float((ra * rb).sum() / (da * db))
    return out


def daily_rank_ic(factor: pd.DataFrame, label: pd.DataFrame) -> pd.Series:
    # align
    idx = factor.index.intersection(label.index)
    if len(idx) == 0:
        return pd.Series(dtype="float64")
    f = factor.reindex(idx).to_numpy(dtype=np.float64, copy=False)
    y = label.reindex(idx).to_numpy(dtype=np.float64, copy=False)
    ics = _cs_rank_ic_matrix(f, y)
    return pd.Series(ics, index=idx)


def icir_from_series(ics: pd.Series) -> float:
    a = ics.to_numpy(dtype=float)
    a = a[np.isfinite(a)]
    if len(a) < 10:
        return float("nan")
    sd = a.std(ddof=1)
    return float(a.mean() / sd) if sd > 1e-12 else float("nan")


def rank_turnover(factor: pd.DataFrame, top_n: int = 50) -> float:
    """Mean one-way turnover of equal-weight top-N long book (0..1)."""
    arr = factor.to_numpy(dtype=np.float64, copy=False)
    T, N = arr.shape
    turns: list[float] = []
    prev = None
    for t in range(T):
        row = arr[t]
        m = np.isfinite(row)
        n_ok = int(m.sum())
        k = min(top_n, n_ok)
        if k < max(5, top_n // 5):
            continue
        idx = np.nonzero(m)[0]
        vals = row[idx]
        if len(vals) > k:
            part = np.argpartition(vals, -k)[-k:]
            cur = set(idx[part].tolist())
        else:
            cur = set(idx.tolist())
        if prev is not None:
            turns.append(len(cur.symmetric_difference(prev)) / (2.0 * k))
        prev = cur
    return float(np.mean(turns)) if turns else float("nan")


def long_only_gross_rets(
    factor: pd.DataFrame, label: pd.DataFrame, top_n: int = 50
) -> pd.Series:
    idx = factor.index.intersection(label.index)
    f = factor.reindex(idx).to_numpy(dtype=np.float64, copy=False)
    y = label.reindex(idx).to_numpy(dtype=np.float64, copy=False)
    rets = np.full(len(idx), np.nan)
    for t in range(len(idx)):
        ft, yt = f[t], y[t]
        m = np.isfinite(ft) & np.isfinite(yt)
        n_ok = int(m.sum())
        k = min(top_n, n_ok)
        if k < max(5, top_n // 5):
            continue
        ii = np.nonzero(m)[0]
        vals = ft[ii]
        part = np.argpartition(vals, -k)[-k:]
        rets[t] = float(yt[ii[part]].mean())
    return pd.Series(rets, index=idx)


def fitness_score(
    factor: pd.DataFrame,
    label: pd.DataFrame,
    *,
    cost_one_way: float = 0.0025,
    top_n: int = 50,
    lambda_complexity: float = 0.01,
    n_nodes: int = 1,
    lambda_turnover: float = 1.0,
) -> dict:
    """ICIR minus complexity and cost*turnover penalties (enter fitness, plan §2.3)."""
    # score only on label dates (explore)
    idx = factor.index.intersection(label.index)
    fac = factor.reindex(idx)
    lab = label.reindex(idx)
    ics = daily_rank_ic(fac, lab)
    icir = icir_from_series(ics)
    turn = rank_turnover(fac, top_n=top_n)
    gross = long_only_gross_rets(fac, lab, top_n=top_n)
    g = gross.to_numpy()
    g = g[np.isfinite(g)]
    if len(g) == 0 or not np.isfinite(icir):
        return {
            "fitness": -1e9,
            "icir": icir,
            "ic_mean": float(np.nanmean(ics.to_numpy())) if len(ics) else float("nan"),
            "turnover": turn,
            "ann_gross": float("nan"),
            "ann_net": float("nan"),
            "n_ic_days": int(np.isfinite(ics.to_numpy()).sum()),
            "promotion_approved": False,
        }
    turn_v = turn if np.isfinite(turn) else 1.0
    net_daily_mean = float(g.mean() - cost_one_way * turn_v)
    ann_g = float(g.mean() * 244)
    ann_n = float(net_daily_mean * 244)
    turn_pen = lambda_turnover * cost_one_way * turn_v * 50.0
    fit = icir - lambda_complexity * n_nodes - turn_pen
    if not np.isfinite(fit):
        fit = -1e9
    return {
        "fitness": float(fit),
        "icir": float(icir),
        "ic_mean": float(np.nanmean(ics.to_numpy())),
        "turnover": float(turn) if np.isfinite(turn) else float("nan"),
        "ann_gross": ann_g,
        "ann_net": ann_n,
        "n_ic_days": int(np.isfinite(ics.to_numpy()).sum()),
        "promotion_approved": False,
    }


def corr_with_panel(factor: pd.DataFrame, other: pd.DataFrame) -> float:
    idx = factor.index.intersection(other.index)
    f = factor.reindex(idx).to_numpy(dtype=np.float64, copy=False)
    o = other.reindex(idx).to_numpy(dtype=np.float64, copy=False)
    cors = []
    for t in range(len(idx)):
        a, b = f[t], o[t]
        m = np.isfinite(a) & np.isfinite(b)
        if int(m.sum()) < 30:
            continue
        aa, bb = a[m], b[m]
        if aa.std() == 0 or bb.std() == 0:
            continue
        cors.append(float(np.corrcoef(aa, bb)[0, 1]))
    return float(np.nanmean(cors)) if cors else float("nan")


def fitness_score_l1b(
    factor: pd.DataFrame,
    label: pd.DataFrame,
    *,
    public_panels: Mapping[str, pd.DataFrame] | None = None,
    cost_one_way: float = 0.0025,
    top_n: int = 50,
    lambda_complexity: float = 0.01,
    n_nodes: int = 1,
    lambda_turnover: float = 1.0,
    corr_penalty_threshold: float = 0.5,
    corr_penalty_scale: float = 2.0,
) -> dict:
    """L1b: primary fitness = ann_net minus complexity/turnover/public-corr penalties."""
    base = fitness_score(
        factor,
        label,
        cost_one_way=cost_one_way,
        top_n=top_n,
        lambda_complexity=0.0,
        n_nodes=n_nodes,
        lambda_turnover=lambda_turnover,
    )
    if base["fitness"] <= -1e8:
        base["novelty_fail"] = True
        base["max_abs_public_corr"] = float("nan")
        base["public_corr"] = {}
        return base

    public_corr: dict[str, float] = {}
    max_abs = 0.0
    if public_panels:
        for name, panel in public_panels.items():
            c = corr_with_panel(factor, panel)
            public_corr[name] = c
            if np.isfinite(c):
                max_abs = max(max_abs, abs(c))

    ann_net = base.get("ann_net")
    turn = base.get("turnover")
    turn_v = turn if np.isfinite(turn) else 1.0
    # primary: annualized net (already cost-aware) scaled to fitness units
    fit = float(ann_net) if ann_net is not None and np.isfinite(ann_net) else -1e9
    fit -= lambda_complexity * n_nodes
    # extra turnover drag already in ann_net; mild extra for extreme churn
    if turn_v > 0.5:
        fit -= (turn_v - 0.5) * 0.2
    novelty_fail = bool(max_abs > corr_penalty_threshold)
    if novelty_fail:
        fit -= corr_penalty_scale * (max_abs - corr_penalty_threshold)
    if not np.isfinite(fit):
        fit = -1e9
    base["fitness"] = float(fit)
    base["max_abs_public_corr"] = float(max_abs) if max_abs > 0 else float("nan")
    base["public_corr"] = public_corr
    base["novelty_fail"] = novelty_fail
    base["promotion_approved"] = False
    return base
