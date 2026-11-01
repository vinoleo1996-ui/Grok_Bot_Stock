#!/usr/bin/env python3
"""Sealed-window λ calibration for OPTIMIZER_V1 Core (Leo concentrated 08:09).

Research-grade only. live=false. Does NOT touch paper FROZEN / capacity_adv paper /
B4-S6 FROZEN_CONFIG. Window 2018-01-02→2024-05-31 only; never uses X2 returns to pick λ.

hard_spec=leo_core_concentrated_0809
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import math
import resource
import sys
import time
import traceback
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SEALED_START = "2018-01-02"
SEALED_END = "2024-05-31"
X2_START = "2024-06-03"  # never use for λ selection
HARD_SPEC = "leo_core_concentrated_0809"
CADENCE = "month_end_plus_first_last"
TURN_FALLBACK_ONE_WAY = 0.25  # monthly two-way ~50%
WEEKLY_BANNED = True
MASK_PATH = ROOT / "output/strategy_hiliq/universe_mask_hiliq_v1.parquet"
MASK_SHA_EXPECT = "c5433e80a74ac3acc0cd5a52d57fdd0bda5ed578fb86fb98cbd652ccb9f1b9af"
DAILY_BASIC = ROOT / "data/v2/valuation/daily_basic_full_tushare.parquet"
CAL_PATH = ROOT / "data/v2/calendar/trade_cal_sse_pit.parquet"
ANN_PATH = ROOT / "data/v2/events/announcements_classified_pit.parquet"
OUT_DIR = ROOT / "output/strategy_optimizer/calib"
WORK = OUT_DIR / "_work"
B4_W = {
    600_000: ROOT / "output/small_aum_concentration/v2/B_B4_50_25_25_topN_60w_20261014_r2.parquet",
    1_000_000: ROOT / "output/small_aum_concentration/v2/B_B4_50_25_25_topN_100w_20261014_r2.parquet",
}
BALLAST = "510300.SH"
HARD_EXCLUDE = frozenset({"600519.SH", "002371.SZ"})
L_SIGMA = 120
L_BETA = 60
L_VOL = 60
ANNUALIZATION = 244

# Leo Core concentrated HARD
NAME_CAP = {600_000: 0.06, 1_000_000: 0.05}
NEFF_LO, NEFF_HI = 20, 30
IND_ACTIVE = 0.08
IND_ABS = 0.20
SIZE_BOX = 0.35  # Slack allowed
BETA_BOX = 0.10
MIN_KEEP_W = 0.020
SUPPORT_LO, SUPPORT_HI = 20, 30
TURN_HARD_CAP = 0.40  # one-way NAV / rebal soft monitor
SIZE_SLACK_MAX = 0.05   # σ beyond ±SIZE_BOX (Strategy)
IND_SLACK_MAX = 0.01    # 1pp beyond ±IND_ACTIVE (Strategy)
LOT_STAR = 200          # STAR board (688/689) lot size
LOT_DEFAULT = 100
REPORT_SLEEVES = ["equity_100", "equity80_etf20_510300"]
METRICS_PLANNED = ["Sharpe", "MDD", "IR"]
ETF_BALLAST_FRAC = 0.20  # sleeve B: 20% 510300 + 80% equity renormalized


def rss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def to_ts(code: str) -> str:
    s = str(code).strip()
    if not s:
        return s
    if "." in s and s.split(".")[-1] in ("SH", "SZ", "BJ"):
        return s
    # baostock sh.600000
    if s[:3] in ("sh.", "sz.", "bj."):
        pref, num = s.split(".", 1)
        return f"{num}.{pref.upper()}"
    return s


def month_ends(start: str, end: str) -> list[pd.Timestamp]:
    cal = pd.read_parquet(CAL_PATH)
    cal["d"] = pd.to_datetime(cal["cal_date"].astype(str), format="%Y%m%d")
    open_days = cal.loc[cal["is_open"] == 1, "d"].sort_values()
    open_days = open_days[(open_days >= start) & (open_days <= end)]
    me = open_days.groupby(open_days.dt.to_period("M")).max()
    return [pd.Timestamp(x).normalize() for x in me.tolist()]


def load_pool(day: pd.Timestamp) -> list[str]:
    d = pd.Timestamp(day).normalize()
    # Try exact timestamp filter; fall back to day-range if needed
    try:
        um = pq.read_table(
            MASK_PATH,
            columns=["instrument", "in_universe"],
            filters=[("date", "=", d), ("in_universe", "=", True)],
        )
    except Exception:
        um = pq.read_table(
            MASK_PATH,
            columns=["date", "instrument", "in_universe"],
            filters=[
                ("date", ">=", d),
                ("date", "<", d + pd.Timedelta(days=1)),
                ("in_universe", "=", True),
            ],
        )
    inst = sorted({to_ts(x) for x in um.column("instrument").to_pylist() if to_ts(x) not in HARD_EXCLUDE})
    del um
    return inst


_SW_CACHE = None

def _sw_df():
    global _SW_CACHE
    if _SW_CACHE is None:
        from research.g1g5_nontextbook_weights import _load_sw_members
        _SW_CACHE = _load_sw_members()
    return _SW_CACHE


def load_sw_map(day: pd.Timestamp, instruments: list[str]) -> dict[str, str]:
    from research.g1g5_nontextbook_weights import sw_code_on

    sw = _sw_df()
    out: dict[str, str] = {}
    for inst in instruments:
        # sw_code_on accepts ts or bao depending on table; try both
        code = sw_code_on(inst, day, sw)
        if not code:
            # try bao form
            if inst.endswith(".SH"):
                bao = "sh." + inst[:-3]
            elif inst.endswith(".SZ"):
                bao = "sz." + inst[:-3]
            elif inst.endswith(".BJ"):
                bao = "bj." + inst[:-3]
            else:
                bao = inst
            code = sw_code_on(bao, day, sw)
        out[inst] = code or "_UNK"
    return out


def load_daily_basic_window(
    instruments: list[str],
    s0: pd.Timestamp,
    s1: pd.Timestamp,
) -> pd.DataFrame:
    pf = pq.ParquetFile(str(DAILY_BASIC))
    want = pa.array(instruments, type=pa.string())
    cols = ["ts_code", "trade_date", "close", "turnover_rate", "float_mktcap", "available_at"]
    chunks: list[pd.DataFrame] = []
    for i in range(pf.metadata.num_row_groups):
        rg = pf.metadata.row_group(i)
        td_stats = None
        for j in range(rg.num_columns):
            col = rg.column(j)
            if col.path_in_schema == "trade_date" and col.statistics and col.statistics.has_min_max:
                td_stats = (pd.Timestamp(col.statistics.min), pd.Timestamp(col.statistics.max))
                break
        if td_stats is not None and (td_stats[1] < s0 or td_stats[0] > s1):
            continue
        table = pf.read_row_group(i, columns=cols)
        tc = table.column("ts_code")
        if not pa.types.is_string(tc.type):
            table = table.set_column(
                table.schema.get_field_index("ts_code"), "ts_code", pc.cast(tc, pa.string())
            )
        table = table.filter(pc.is_in(table.column("ts_code"), value_set=want))
        if table.num_rows == 0:
            continue
        part = table.to_pandas()
        td = pd.to_datetime(part["trade_date"]).dt.tz_localize(None).dt.normalize()
        part = part[(td >= s0) & (td <= s1)].copy()
        if part.empty:
            continue
        part["trade_date"] = td[(td >= s0) & (td <= s1)].values
        if "available_at" in part.columns:
            part["available_at"] = pd.to_datetime(part["available_at"]).dt.tz_localize(None)
        chunks.append(part)
    if not chunks:
        return pd.DataFrame()
    df = pd.concat(chunks, ignore_index=True)
    del chunks
    gc.collect()
    return df


def snapshot_asof(df: pd.DataFrame, day: pd.Timestamp, instruments: list[str]) -> pd.DataFrame:
    """Latest available_at≤day row per ts_code."""
    if df.empty:
        return pd.DataFrame()
    sess = pd.Timestamp(day).normalize()
    if "available_at" in df.columns and df["available_at"].notna().any():
        sub = df[df["available_at"].dt.normalize() <= sess]
    else:
        sub = df[df["trade_date"] <= sess]
    if sub.empty:
        return pd.DataFrame()
    sub = sub.sort_values("available_at" if "available_at" in sub.columns else "trade_date", kind="mergesort")
    last = sub.groupby("ts_code", as_index=False).tail(1)
    last = last[last["ts_code"].isin(instruments)].copy()
    last["adv_yuan"] = last["float_mktcap"].astype(float) * last["turnover_rate"].astype(float) / 100.0
    return last


def residualize_alpha(
    raw: pd.Series,
    industry: dict[str, str],
    ln_mcap: pd.Series,
) -> pd.Series:
    """OLS residual of raw on industry dummies + Size + MidCap within pool."""
    idx = [i for i in raw.index if np.isfinite(raw[i]) and i in ln_mcap.index and np.isfinite(ln_mcap[i])]
    if len(idx) < 30:
        return raw * 0.0
    y = raw.loc[idx].astype(float).values
    z = ln_mcap.loc[idx].astype(float)
    z = (z - z.mean()) / (z.std(ddof=0) + 1e-12)
    mid = (ln_mcap.loc[idx].astype(float) - ln_mcap.loc[idx].mean()) ** 2
    mid = (mid - mid.mean()) / (mid.std(ddof=0) + 1e-12)
    inds = [industry.get(i, "_UNK") for i in idx]
    ind_u = sorted(set(inds))
    # drop one industry for full rank
    ind_u = ind_u[:-1] if len(ind_u) > 1 else ind_u
    cols = []
    for iu in ind_u:
        cols.append(np.array([1.0 if x == iu else 0.0 for x in inds]))
    cols.append(z.values)
    cols.append(mid.values)
    X = np.column_stack(cols + [np.ones(len(idx))])
    try:
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        resid = y - X @ beta
    except Exception:
        resid = y - y.mean()
    out = pd.Series(0.0, index=raw.index, dtype=float)
    out.loc[idx] = resid
    # z-score residual
    sd = float(out.loc[idx].std(ddof=0))
    if sd > 1e-12:
        out.loc[idx] = out.loc[idx] / sd
    return out


def score_capacity_adv_raw(snap: pd.DataFrame, industry: dict[str, str], instruments: list[str]) -> pd.Series:
    """Industry-demeaned log(ADV) z-score (capacity_adv style)."""
    raw_log: dict[str, float] = {}
    for _, row in snap.iterrows():
        inst = str(row["ts_code"])
        if inst in HARD_EXCLUDE or inst not in industry:
            continue
        adv = float(row["adv_yuan"]) if np.isfinite(row["adv_yuan"]) else np.nan
        if not (np.isfinite(adv) and adv > 0):
            continue
        raw_log[inst] = math.log(adv)
    by_ind: dict[str, list[float]] = {}
    for inst, v in raw_log.items():
        by_ind.setdefault(industry.get(inst, "_UNK"), []).append(v)
    ind_mean = {k: float(np.mean(vs)) for k, vs in by_ind.items()}
    resid = {i: raw_log[i] - ind_mean[industry.get(i, "_UNK")] for i in raw_log}
    ser = pd.Series({i: float(resid.get(i, 0.0)) for i in instruments}, dtype=float)
    scored = ser.loc[list(raw_log.keys())] if raw_log else ser
    if len(scored) and float(scored.std(ddof=0)) > 1e-12:
        z = (ser - scored.mean()) / scored.std(ddof=0)
        z = z.where(ser.index.isin(raw_log.keys()), 0.0)
        return z.astype(float)
    return ser * 0.0


def build_wb(snap: pd.DataFrame, instruments: list[str]) -> pd.Series:
    mcap = snap.set_index("ts_code")["float_mktcap"].astype(float)
    w = pd.Series(0.0, index=instruments, dtype=float)
    for i in instruments:
        if i in mcap.index and np.isfinite(mcap.loc[i]) and mcap.loc[i] > 0:
            w.loc[i] = float(mcap.loc[i])
    s = float(w.sum())
    if s <= 0:
        w[:] = 1.0 / max(len(instruments), 1)
    else:
        w /= s
    return w


def returns_from_close(close_wide: pd.DataFrame) -> pd.DataFrame:
    return close_wide.sort_index().pct_change().replace([np.inf, -np.inf], np.nan)


def industry_factor_cov(returns: pd.DataFrame, industry: dict[str, str]) -> tuple[list[str], np.ndarray, np.ndarray]:
    """Return (ind_list, B[n,k], F[k,k]) equal-weight industry portfolios + factor cov."""
    cols = list(returns.columns)
    ind_of = [industry.get(c, "_UNK") for c in cols]
    ind_list = sorted(set(ind_of))
    k = len(ind_list)
    ind_ix = {ind: j for j, ind in enumerate(ind_list)}
    # industry returns
    ir = np.zeros((len(returns), k), dtype=np.float64)
    for j, ind in enumerate(ind_list):
        members = [c for c, ii in zip(cols, ind_of) if ii == ind]
        if not members:
            continue
        ir[:, j] = returns[members].mean(axis=1, skipna=True).fillna(0.0).values
    # cov of industry factors
    if len(returns) >= 10:
        F = np.cov(ir, rowvar=False)
    else:
        F = np.eye(k) * 1e-4
    F = 0.5 * (F + F.T)
    evals, evecs = np.linalg.eigh(F)
    evals = np.clip(evals, 1e-10, None)
    F = (evecs * evals) @ evecs.T
    B = np.zeros((len(cols), k), dtype=np.float64)
    for i, ind in enumerate(ind_of):
        B[i, ind_ix[ind]] = 1.0
    return ind_list, B, F


def idio_var(returns: pd.DataFrame, B: np.ndarray, F: np.ndarray, industry: dict[str, str]) -> np.ndarray:
    cols = list(returns.columns)
    # residual ≈ r - B f_hat; use 60d var of residual approx as var(r)*(1-R^2) simple: use var of r as proxy clipped
    vol = returns.tail(L_VOL).var(axis=0, ddof=0).fillna(1e-4).values
    # subtract average industry var contribution roughly
    ind_var = np.diag(F)  # k
    ind_list = sorted(set(industry.get(c, "_UNK") for c in cols))
    ind_ix = {ind: j for j, ind in enumerate(ind_list)}
    out = np.zeros(len(cols))
    for i, c in enumerate(cols):
        j = ind_ix[industry.get(c, "_UNK")]
        out[i] = max(1e-8, float(vol[i]) - 0.5 * float(ind_var[j] if j < len(ind_var) else 0.0))
    return out


def stock_betas(returns: pd.DataFrame, wb: pd.Series) -> pd.Series:
    cols = [c for c in returns.columns if c in wb.index]
    if len(cols) < 5 or len(returns) < 20:
        return pd.Series(1.0, index=wb.index)
    R = returns[cols].tail(L_BETA).fillna(0.0)
    rb = R.values @ wb.reindex(cols).fillna(0.0).values
    v = float(np.var(rb))
    if v < 1e-16:
        return pd.Series(1.0, index=wb.index)
    out = pd.Series(1.0, index=wb.index, dtype=float)
    for i, c in enumerate(cols):
        out.loc[c] = float(np.cov(R.values[:, i], rb)[0, 1] / v)
    return out


@dataclass
class SolveResult:
    status: str
    w: pd.Series | None
    alpha_term: float
    risk_term_raw: float  # (w-wb)'Σ(w-wb)
    turn_term_raw: float  # ||w-w0||_1
    neff: float
    n_names: int
    info: dict[str, Any]


def solve_core(
    alpha: pd.Series,
    wb: pd.Series,
    w0: pd.Series,
    industry: dict[str, str],
    ln_mcap: pd.Series,
    B: np.ndarray,
    F: np.ndarray,
    delta: np.ndarray,
    betas: pd.Series,
    *,
    aum: int,
    lambda_risk: float,
    lambda_turn: float,
    support: list[str] | None = None,
    size_slack: float = 0.0,
    ind_slack: float = 0.0,
) -> SolveResult:
    import cvxpy as cp

    names = list(support) if support is not None else list(alpha.index)
    names = [n for n in names if n in alpha.index]
    n = len(names)
    if n < 5:
        return SolveResult("INFEASIBLE_SMALL", None, 0, 0, 0, 0, 0, {"reason": "n<5"})

    ix = {nm: i for i, nm in enumerate(names)}
    a = alpha.reindex(names).fillna(0.0).values
    wb_v = wb.reindex(names).fillna(0.0).values
    # renormalize wb on support for second pass? keep global wb projection
    w0_v = w0.reindex(names).fillna(0.0).values
    # map B, delta
    full_names = list(alpha.index)
    full_ix = {nm: i for i, nm in enumerate(full_names)}
    B_s = np.vstack([B[full_ix[nm]] for nm in names]) if names[0] in full_ix else np.ones((n, 1))
    # rebuild B_s from industry
    ind_list = sorted(set(industry.get(nm, "_UNK") for nm in names))
    ind_ix = {ind: j for j, ind in enumerate(ind_list)}
    k = len(ind_list)
    B_s = np.zeros((n, k))
    for i, nm in enumerate(names):
        B_s[i, ind_ix[industry.get(nm, "_UNK")]] = 1.0
    # F on these industries: use diagonal of prior F mapped loosely — rebuild small F as ew cov proxy
    F_s = np.eye(k) * float(np.mean(np.diag(F))) if F.size else np.eye(k) * 1e-4
    # better: slice F if same ind_list order from caller — pass ind_list with F
    delta_s = np.array([delta[full_ix[nm]] if nm in full_ix else 1e-4 for nm in names])

    beta_v = betas.reindex(names).fillna(1.0).values
    z = ln_mcap.reindex(names).astype(float)
    z = (z - z.mean()) / (z.std(ddof=0) + 1e-12)
    z_v = z.fillna(0.0).values
    mid = (ln_mcap.reindex(names).astype(float) - ln_mcap.reindex(names).mean()) ** 2
    mid = (mid - mid.mean()) / (mid.std(ddof=0) + 1e-12)
    mid_v = mid.fillna(0.0).values
    zb = float((wb_v * z_v).sum())  # wb size exposure on support approx
    midb = float((wb_v * mid_v).sum())

    w = cp.Variable(n, nonneg=True)
    name_cap = NAME_CAP[aum]
    dw = w - w0_v
    # risk: (B' (w-wb))' F (B'(w-wb)) + sum delta (w-wb)^2
    active = w - wb_v
    ind_active = B_s.T @ active
    risk = cp.quad_form(ind_active, F_s) + cp.sum(cp.multiply(delta_s, cp.square(active)))
    turn = cp.norm1(dw)
    obj = -(a @ w) + float(lambda_risk) * risk + float(lambda_turn) * turn
    cons = [cp.sum(w) <= 1.0, w <= name_cap]
    # industry vs wb ±8%, abs ≤20%
    wb_ind = B_s.T @ wb_v
    port_ind = B_s.T @ w
    ind_box = IND_ACTIVE + float(ind_slack)
    for j in range(k):
        cons += [
            port_ind[j] - wb_ind[j] <= ind_box,
            wb_ind[j] - port_ind[j] <= ind_box,
            port_ind[j] <= IND_ABS,
        ]
    # Size / MidCap ±0.35σ + slack
    box = SIZE_BOX + float(size_slack)
    cons += [
        (w @ z_v) - zb <= box,
        zb - (w @ z_v) <= box,
        (w @ mid_v) - midb <= box,
        midb - (w @ mid_v) <= box,
    ]
    # beta
    cons += [
        (w @ beta_v) - 1.0 <= BETA_BOX,
        1.0 - (w @ beta_v) <= BETA_BOX,
    ]
    # Neff band enforced by two-step support (20–30 names), not a non-DCP lower bound on ||w||^2.
    # Upper bound on concentration only (N_eff >= NEFF_LO ⇒ sum w^2 <= 1/NEFF_LO).
    cons += [cp.sum_squares(w) <= 1.0 / NEFF_LO]

    prob = cp.Problem(cp.Minimize(obj), cons)
    status = "INFEASIBLE"
    try:
        prob.solve(solver=cp.OSQP, warm_start=True, verbose=False, max_iter=40000, eps_abs=1e-5, eps_rel=1e-5)
        status = str(prob.status)
        if status not in ("optimal", "optimal_inaccurate"):
            prob.solve(solver=cp.CLARABEL, verbose=False)
            status = str(prob.status)
    except Exception as e:
        try:
            prob.solve(solver=cp.CLARABEL, verbose=False)
            status = str(prob.status)
        except Exception as e2:
            status = f"ERROR:{e}|{e2}"
    accept = w.value is not None and status in ("optimal", "optimal_inaccurate", "user_limit")
    if not accept:
        # retry with size slack
        if size_slack < SIZE_SLACK_MAX - 1e-12 or ind_slack < IND_SLACK_MAX - 1e-12:
            return solve_core(
                alpha, wb, w0, industry, ln_mcap, B, F, delta, betas,
                aum=aum, lambda_risk=lambda_risk, lambda_turn=lambda_turn,
                support=support,
                size_slack=min(SIZE_SLACK_MAX, size_slack + 0.05),
                ind_slack=min(IND_SLACK_MAX, ind_slack + 0.005),
            )
        return SolveResult(status, None, 0, 0, 0, 0, 0, {"size_slack": size_slack, "ind_slack": ind_slack})

    wv = np.array(w.value, dtype=float).clip(min=0)
    # zero tiny
    wv[wv < 0.002] = 0.0
    s = wv.sum()
    if s > 1.0:
        wv /= s
    elif s > 0 and s < 1.0:
        pass  # cash ok
    w_ser = pd.Series(wv, index=names, dtype=float)
    active_v = wv - wb_v
    ind_a = B_s.T @ active_v
    risk_raw = float(ind_a @ F_s @ ind_a + np.sum(delta_s * active_v ** 2))
    alpha_term = float(a @ wv)
    turn_raw = float(np.abs(wv - w0_v).sum())
    neff = float(1.0 / max(np.sum(wv ** 2), 1e-12))
    return SolveResult(
        "OK" if status.startswith("optimal") else status,
        w_ser,
        alpha_term,
        risk_raw,
        turn_raw,
        neff,
        int((wv >= MIN_KEEP_W).sum()),
        {"size_slack": size_slack, "ind_slack": ind_slack, "sum_w": float(wv.sum()), "cvx_status": status},
    )


def two_step_polish(
    alpha, wb, w0, industry, ln_mcap, B, F, delta, betas, *, aum, lambda_risk, lambda_turn
) -> SolveResult:
    r1 = solve_core(
        alpha, wb, w0, industry, ln_mcap, B, F, delta, betas,
        aum=aum, lambda_risk=lambda_risk, lambda_turn=lambda_turn, support=None,
    )
    if r1.w is None:
        return r1
    # keep top 20-30 with weight ≥ MIN_KEEP_W
    w = r1.w.sort_values(ascending=False)
    keep = w[w >= MIN_KEEP_W].head(SUPPORT_HI)
    if len(keep) < SUPPORT_LO:
        keep = w.head(SUPPORT_LO)
    support = list(keep.index)
    r2 = solve_core(
        alpha, wb, w0, industry, ln_mcap, B, F, delta, betas,
        aum=aum, lambda_risk=lambda_risk, lambda_turn=lambda_turn, support=support,
    )
    # v1.1 (Arch P1-T3): step-2 failure is INFEASIBLE (caller carries previous weights);
    # never fall back to the step-1 large basket.
    if r2.w is None:
        info = dict(r2.info or {})
        info.update({"reason": "step2_failed", "step2_status": r2.status,
                     "step1_n_pos": int((r1.w > 0).sum()), "final_n": int((r1.w > 0).sum())})
        return SolveResult("INFEASIBLE", None, 0, 0, 0, 0, 0, info)
    r2.info["step1_neff"] = r1.neff
    r2.info["support_n"] = len(support)
    n_pos = int((r2.w > 0).sum())
    r2.info["final_n"] = n_pos
    if not (SUPPORT_LO <= n_pos <= SUPPORT_HI):
        info = dict(r2.info)
        info.update({"reason": "n_names_out_of_20_30"})
        return SolveResult("INFEASIBLE", None, 0, 0, 0, 0, 0, info)
    return r2


def one_way_turnover_series(weights_by_day: dict[pd.Timestamp, pd.Series]) -> list[float]:
    days = sorted(weights_by_day)
    out = []
    prev = None
    for d in days:
        w = weights_by_day[d]
        if prev is not None:
            idx = prev.index.union(w.index)
            a = prev.reindex(idx).fillna(0.0)
            b = w.reindex(idx).fillna(0.0)
            out.append(0.5 * float((a - b).abs().sum()))
        prev = w
    return out



def capacity_adv_sealed_turnover(aum: int) -> dict[str, Any]:
    """Sealed-window capacity_adv weight one-way turnover (month_end_plus_first_last)."""
    # Prefer paper capacity_adv weights (engine-aligned book structure)
    candidates = [
        ROOT / "output/ai_factory/g1g5_capacity_adv_daily_weights_paper_20261014_r2.parquet",
        ROOT / "output/ai_factory/g1g5_capacity_adv_daily_weights_paper_20261013.parquet",
        ROOT / "output/strategy_hiliq/legs/g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet",
    ]
    path = next((c for c in candidates if c.exists()), None)
    if path is None:
        return {"status": "MISSING", "aum": aum, "n_turnover_obs": 0, "median_one_way": None}
    df = pd.read_parquet(path)
    dcol = "date" if "date" in df.columns else "session"
    icol = "instrument" if "instrument" in df.columns else "instrument_id"
    wcol = "weight" if "weight" in df.columns else "target_weight"
    df = df[[dcol, icol, wcol]].copy()
    df.columns = ["date", "instrument", "weight"]
    df["date"] = pd.to_datetime(df["date"]).dt.normalize()
    df = df[(df["date"] >= SEALED_START) & (df["date"] <= SEALED_END)]
    if df.empty:
        return {"status": "EMPTY_SEALED", "aum": aum, "path": str(path.relative_to(ROOT)), "n_turnover_obs": 0}
    dates = sorted(df["date"].unique())
    s = pd.Series(dates)
    me = s.groupby(s.dt.to_period("M")).max().tolist()
    rebal = sorted(set([pd.Timestamp(x) for x in me] + [pd.Timestamp(dates[0]), pd.Timestamp(dates[-1])]))
    by = {}
    for d in rebal:
        sub = df[df["date"] == d].set_index("instrument")["weight"].astype(float)
        by[pd.Timestamp(d)] = sub[sub.abs() > 1e-12]
    turns = one_way_turnover_series(by)
    return {
        "status": "OK" if len(turns) >= 20 else "WEAK_SAMPLE",
        "kind": "capacity_adv_weight_one_way_month_end_plus_first_last",
        "aum": aum,
        "path": str(path.relative_to(ROOT)),
        "note_zh": "纸面/HI_LIQ capacity_adv 权重在密封窗仅覆盖末段；同 AUM 权重文件若不区分则共用",
        "n_rebal": len(rebal),
        "n_turnover_obs": len(turns),
        "median_one_way": float(np.median(turns)) if turns else None,
        "mean_one_way": float(np.mean(turns)) if turns else None,
        "two_way_median": float(np.median(turns)) * 2 if turns else None,
        "cadence": CADENCE,
    }


def b4_paper_sealed_turnover(aum: int) -> dict[str, Any]:
    path = B4_W[aum]
    df = pd.read_parquet(path, columns=["date", "instrument", "weight"])
    df["date"] = pd.to_datetime(df["date"]).dt.normalize()
    df = df[(df["date"] >= SEALED_START) & (df["date"] <= SEALED_END)]
    dates = sorted(df["date"].unique())
    s = pd.Series(dates)
    me = s.groupby(s.dt.to_period("M")).max().tolist()
    by = {}
    for d in me:
        sub = df[df["date"] == d].set_index("instrument")["weight"].astype(float)
        by[pd.Timestamp(d)] = sub[sub.abs() > 1e-12]
    turns = one_way_turnover_series(by)
    return {
        "source": str(path.relative_to(ROOT)),
        "kind": "b4_paper_engine_weight_one_way_month_end",
        "sealed_month_ends": [str(pd.Timestamp(x).date()) for x in me],
        "n_month_ends": len(me),
        "n_turnover_obs": len(turns),
        "median_one_way": float(np.median(turns)) if turns else None,
        "mean_one_way": float(np.mean(turns)) if turns else None,
        "note_zh": "纸面 B4 权重仅覆盖密封窗末段 2024-01→2024-05；obs 少，已另做研究重建对照",
    }


def reconstruct_b4_research_month_end(
    me_days: list[pd.Timestamp],
    aum: int,
) -> dict[str, Any]:
    """Research B4-like 50/25/25 at month-ends (batched ADV; no gap confirm)."""
    name_w_event = 0.04
    max_event_names = 6 if aum == 600_000 else 10
    active_n_cap = 25
    name_cap = NAME_CAP[aum]

    ann = pd.read_parquet(ANN_PATH, columns=["instrument", "event_type", "available_at"])
    ann["available_at"] = pd.to_datetime(ann["available_at"]).dt.tz_localize(None).dt.normalize()
    ann["instrument"] = ann["instrument"].map(to_ts)
    earn = ann[ann["event_type"] == "earnings_beat"].copy()
    insid = ann[ann["event_type"] == "insider_increase"].copy()
    del ann
    gc.collect()

    # Preload pools
    pools: dict[pd.Timestamp, list[str]] = {}
    all_inst: set[str] = set()
    for day in me_days:
        pool = load_pool(day)
        if len(pool) < 50:
            continue
        pools[day] = pool
        all_inst.update(pool)
    if len(pools) < 10:
        return {"status": "FAILED", "reason": "too_few_pools", "n": len(pools)}

    # One daily_basic window covering all month-ends (+margin)
    s0 = min(pools) - pd.Timedelta(days=45)
    s1 = max(pools)
    print(f"  [b4recon] load basic n_inst={len(all_inst)} days={len(pools)} RSS={rss_mb():.0f}", flush=True)
    basic = load_daily_basic_window(sorted(all_inst), s0, s1)
    print(f"  [b4recon] basic rows={len(basic)} RSS={rss_mb():.0f}", flush=True)
    if basic.empty:
        return {"status": "FAILED", "reason": "no_daily_basic"}

    by_day: dict[pd.Timestamp, pd.Series] = {}
    meta_days = []
    for day, pool in sorted(pools.items()):
        snap = snapshot_asof(basic, day, pool)
        if snap.empty or len(snap) < 50:
            continue
        industry = load_sw_map(day, pool)
        raw = score_capacity_adv_raw(snap, industry, pool)
        ranked = raw.sort_values(ascending=False)
        picked = []
        ind_c: dict[str, int] = {}
        snap_set = set(snap["ts_code"].astype(str))
        for inst, sc in ranked.items():
            if inst not in snap_set:
                continue
            ind = industry.get(inst, "_UNK")
            if ind_c.get(ind, 0) >= 4:
                continue
            picked.append(inst)
            ind_c[ind] = ind_c.get(ind, 0) + 1
            if len(picked) >= active_n_cap:
                break
        cap_w = pd.Series(0.0, index=pool, dtype=float)
        if picked:
            advs = snap.set_index("ts_code")["adv_yuan"].astype(float)
            advs = advs.reindex(picked).dropna()
            advs = advs[advs > 0]
            if len(advs):
                ww = advs / advs.sum()
                for i, v in ww.items():
                    cap_w.loc[i] = float(min(name_cap, v))
                s = float(cap_w.sum())
                if s > 0:
                    cap_w /= s

        def event_sleeve(evdf: pd.DataFrame) -> pd.Series:
            w = pd.Series(0.0, index=pool, dtype=float)
            sub = evdf[(evdf["available_at"] <= day) & (evdf["available_at"] > day - pd.Timedelta(days=40))]
            sub = sub[sub["instrument"].isin(pool)].drop_duplicates("instrument")
            names = list(sub["instrument"].head(max_event_names))
            for nm in names:
                w.loc[nm] = name_w_event
            if float(w.sum()) > 1.0:
                w /= float(w.sum())
            return w

        e_w = event_sleeve(earn)
        i_w = event_sleeve(insid)
        blend = (
            0.5 * cap_w.reindex(pool).fillna(0.0)
            + 0.25 * e_w.reindex(pool).fillna(0.0)
            + 0.25 * i_w.reindex(pool).fillna(0.0)
        )
        blend = blend.clip(upper=name_cap)
        s = float(blend.sum())
        if s > 1.0:
            blend /= s
        by_day[day] = blend[blend > 1e-12]
        meta_days.append(str(day.date()))
        if rss_mb() > 1450:
            break

    del basic
    gc.collect()
    turns = one_way_turnover_series(by_day)
    return {
        "status": "OK" if len(turns) >= 10 else "WEAK_SAMPLE",
        "kind": "b4_research_reconstruct_50_25_25_month_end_batched",
        "gap_confirm": "skipped_research_calib_proxy",
        "alpha_leg": "capacity_adv_logadv_top25",
        "aum": aum,
        "n_month_ends": len(by_day),
        "month_ends": meta_days,
        "n_turnover_obs": len(turns),
        "median_one_way": float(np.median(turns)) if turns else None,
        "mean_one_way": float(np.mean(turns)) if turns else None,
        "p25_one_way": float(np.percentile(turns, 25)) if turns else None,
        "p75_one_way": float(np.percentile(turns, 75)) if turns else None,
        "peak_rss_mb": rss_mb(),
    }



def apply_report_sleeve(equity_w: pd.Series, sleeve: str) -> pd.Series:
    """Weight-construction contract for dual reporting sleeves (calib docs only; no NAV).

    equity_100: pure equity book (sum<=1, cash residual OK).
    equity80_etf20_510300: 80% renormalized equity + 20% 510300 ballast.
    """
    w = equity_w.astype(float).clip(lower=0.0).copy()
    if sleeve == "equity_100":
        s = float(w.sum())
        if s > 1.0:
            w = w / s
        return w
    if sleeve == "equity80_etf20_510300":
        s = float(w.sum())
        if s <= 1e-15:
            out = pd.Series({BALLAST: ETF_BALLAST_FRAC}, dtype=float)
            return out
        eq = w / s * (1.0 - ETF_BALLAST_FRAC)
        out = eq.copy()
        out.loc[BALLAST] = float(out.get(BALLAST, 0.0)) + ETF_BALLAST_FRAC
        return out
    raise ValueError(f"unknown_report_sleeve:{sleeve}")


def lot_round_rule(instrument: str) -> int:
    num = str(instrument).split(".")[0]
    if num.startswith(("688", "689")):
        return LOT_STAR
    return LOT_DEFAULT


def sealed_sleeve_metrics_smoke(
    days_data: list[dict],
    weights_by_day: dict,
    *,
    annualization: int = ANNUALIZATION,
) -> dict:
    """Small sealed-window smoke metrics for calib sample only.

    Holds month-end target weights to next rebalance; uses daily_basic close
    already loaded per day is NOT available across days — rebuild a thin
    return path from consecutive day wb/alpha universes via daily_basic.

    NEVER used to choose λ. No X2.
    """
    import math
    days = sorted(weights_by_day)
    if len(days) < 2:
        return {"status": "SKIP", "reason": "need>=2_rebalance_days"}

    # Load closes covering [first, last] for union of names (+ ballast)
    names = set()
    for d in days:
        names |= set(weights_by_day[d].index.astype(str))
    names.add(BALLAST)
    names = sorted(names)
    s0 = days[0] - pd.Timedelta(days=5)
    s1 = days[-1] + pd.Timedelta(days=5)
    basic = load_daily_basic_window(names, s0, s1)
    if basic.empty:
        return {"status": "SKIP", "reason": "no_close_panel"}
    close = basic.pivot_table(index="trade_date", columns="ts_code", values="close", aggfunc="last").sort_index()
    close = close.loc[(close.index >= days[0]) & (close.index <= days[-1])]
    rets = close.pct_change().replace([np.inf, -np.inf], np.nan)

    out = {"status": "OK", "lambda_selection_used_returns": False, "sleeves": {}}
    for sleeve in REPORT_SLEEVES:
        # build daily weight path by forward-filling month-end sleeve weights
        w_me = {d: apply_report_sleeve(weights_by_day[d], sleeve) for d in days}
        # daily returns of book
        book = []
        dates = list(rets.index)
        me_i = 0
        for dt in dates:
            while me_i + 1 < len(days) and days[me_i + 1] <= dt:
                me_i += 1
            w = w_me[days[me_i]]
            row = rets.loc[dt]
            # skip first day NaNs
            if row.isna().all():
                continue
            rr = 0.0
            for inst, wi in w.items():
                if wi == 0 or inst not in row.index:
                    continue
                v = row[inst]
                if np.isfinite(v):
                    rr += float(wi) * float(v)
            book.append((dt, rr))
        if len(book) < 10:
            out["sleeves"][sleeve] = {"status": "SKIP", "n_days": len(book)}
            continue
        ser = pd.Series({d: r for d, r in book}, dtype=float)
        mu = float(ser.mean())
        sd = float(ser.std(ddof=0))
        sharpe = (mu / sd * math.sqrt(annualization)) if sd > 1e-12 else None
        # nav / mdd
        nav = (1.0 + ser).cumprod()
        peak = nav.cummax()
        dd = nav / peak - 1.0
        mdd = float(dd.min()) if len(dd) else None
        # IR vs 510300 if available
        ir = None
        if BALLAST in rets.columns:
            bench = rets[BALLAST].reindex(ser.index).fillna(0.0)
            active = ser - bench
            asd = float(active.std(ddof=0))
            ir = (float(active.mean()) / asd * math.sqrt(annualization)) if asd > 1e-12 else None
        out["sleeves"][sleeve] = {
            "status": "OK",
            "n_days": int(len(ser)),
            "Sharpe": sharpe,
            "MDD": mdd,
            "IR_vs_510300": ir,
            "mean_daily": mu,
            "note_zh": "密封窗烟测样本持仓路径；禁止用于选λ；非X2终判",
        }
    del basic, close, rets
    gc.collect()
    return out

def prepare_day(day: pd.Timestamp) -> dict[str, Any] | None:
    pool = load_pool(day)
    if len(pool) < 80:
        return None
    s0 = day - pd.Timedelta(days=int(L_SIGMA * 1.8 + 30))
    basic = load_daily_basic_window(pool, s0, day)
    if basic.empty:
        return None
    snap = snapshot_asof(basic, day, pool)
    if len(snap) < 80:
        return None
    industry = load_sw_map(day, pool)
    raw = score_capacity_adv_raw(snap, industry, pool)
    mcap = snap.set_index("ts_code")["float_mktcap"].astype(float)
    ln_mcap = np.log(mcap.clip(lower=1.0))
    alpha = residualize_alpha(raw, industry, ln_mcap.reindex(pool))
    wb = build_wb(snap, pool)
    # close wide for returns
    close = basic.pivot_table(index="trade_date", columns="ts_code", values="close", aggfunc="last")
    close = close.reindex(columns=[c for c in pool if c in close.columns])
    rets = returns_from_close(close).tail(L_SIGMA)
    # align columns to pool order with data
    cols = [c for c in pool if c in rets.columns and rets[c].notna().sum() >= max(40, L_VOL // 2)]
    if len(cols) < 80:
        return None
    rets = rets[cols]
    alpha = alpha.reindex(cols).fillna(0.0)
    wb = wb.reindex(cols).fillna(0.0)
    wb = wb / max(wb.sum(), 1e-12)
    ln_mcap = ln_mcap.reindex(cols)
    industry = {c: industry.get(c, "_UNK") for c in cols}
    ind_list, B, F = industry_factor_cov(rets, industry)
    delta = idio_var(rets, B, F, industry)
    # Annualize quadratic risk to 244 trading days so λ_risk is O(1)–O(100) vs z-scored α
    F = F * float(ANNUALIZATION)
    delta = delta * float(ANNUALIZATION)
    betas = stock_betas(rets, wb)
    del basic, close
    gc.collect()
    return {
        "day": day,
        "alpha": alpha,
        "wb": wb,
        "ln_mcap": ln_mcap,
        "industry": industry,
        "B": B,
        "F": F,
        "delta": delta,
        "betas": betas,
        "ind_list": ind_list,
        "n": len(cols),
        "alpha_source": "capacity_adv_logadv_ind_demean_resid_industry_size_midcap_research_proxy",
    }


def calibrate_lambda_risk(days_data: list[dict], aum: int = 1_000_000) -> dict[str, Any]:
    """Choose λ_risk so λ*risk_raw ~ |alpha_term| at typical active portfolio."""
    # Use a unit probe: solve with lambda_risk=1, lambda_turn=0, measure ratio
    ratios = []
    alpha_terms = []
    risk_raws = []
    details = []
    for D in days_data:
        w0 = D["wb"].copy()  # from wb as prior for risk calib (no turn)
        r = two_step_polish(
            D["alpha"], D["wb"], w0, D["industry"], D["ln_mcap"], D["B"], D["F"], D["delta"], D["betas"],
            aum=aum, lambda_risk=1.0, lambda_turn=0.0,
        )
        if r.w is None or r.risk_term_raw <= 1e-15:
            details.append({"day": str(D["day"].date()), "status": r.status})
            continue
        # want λ * risk_raw ≈ |alpha_term|
        ratio = abs(r.alpha_term) / r.risk_term_raw
        ratios.append(ratio)
        alpha_terms.append(r.alpha_term)
        risk_raws.append(r.risk_term_raw)
        details.append({
            "day": str(D["day"].date()),
            "status": r.status,
            "alpha_term": r.alpha_term,
            "risk_raw": r.risk_term_raw,
            "implied_lambda": ratio,
            "neff": r.neff,
            "n_names": r.n_names,
        })
    if not ratios:
        return {"status": "FAILED", "reason": "no_feasible_probe_days", "details": details}
    arr = np.array(ratios, dtype=float)
    chosen = float(np.median(arr))
    # sensitivity ±50%
    sens = {}
    for mult in (0.5, 1.0, 1.5):
        lam = chosen * mult
        a_terms, r_terms = [], []
        for D in days_data[: min(8, len(days_data))]:
            r = two_step_polish(
                D["alpha"], D["wb"], D["wb"].copy(), D["industry"], D["ln_mcap"],
                D["B"], D["F"], D["delta"], D["betas"],
                aum=aum, lambda_risk=lam, lambda_turn=0.0,
            )
            if r.w is None:
                continue
            a_terms.append(abs(r.alpha_term))
            r_terms.append(lam * r.risk_term_raw)
        sens[f"x{mult}"] = {
            "lambda_risk": lam,
            "median_abs_alpha": float(np.median(a_terms)) if a_terms else None,
            "median_lambda_risk_term": float(np.median(r_terms)) if r_terms else None,
            "ratio_risk_over_alpha": (
                float(np.median(r_terms) / max(np.median(a_terms), 1e-15)) if a_terms and r_terms else None
            ),
        }
    return {
        "status": "OK",
        "hard_spec": HARD_SPEC,
        "report_sleeves": REPORT_SLEEVES,
        "primary_benchmark_sleeve": "equity80_etf20_510300",
        "core_run_compare_columns": [
            {
                "id": 1,
                "name": "OPTIMIZER_Core_HI_LIQ",
                "desc_zh": "优化器 Core 在 HI_LIQ_V1.1 池求解"
            },
            {
                "id": 2,
                "name": "capacity_adv_mid_large_static_anchor_paper",
                "desc_zh": "现行 capacity_adv mid_large + 静态锚（纸面 FROZEN 路径）；Eng 不改 FROZEN"
            },
            {
                "id": 3,
                "name": "capacity_adv_Top25_HI_LIQ_V1_1_same_pool",
                "desc_zh": "capacity_adv Top-25 在 HI_LIQ_V1.1 同池重跑，去除 static-anchor=2024-06-28 幸存者偏差"
            }
        ],
        "core_run_compare_note_zh": "三列对照合同（Leo via 主 Agent）；不用于选λ；主对标袖仍为 equity80_etf20_510300",
        "primary_benchmark_note_zh": "Core vs capacity_adv 主对比用 equity80_etf20_510300；λ 仍仅在股票 HARD 层标定，不用收益选参",
        "metrics_planned": METRICS_PLANNED,
        "report_sleeve_contract_zh": {
            "equity_100": "纯股票仓：优化器输出权益权重（sum≤1，余现金）；不做收益选λ",
            "equity80_etf20_510300": "报告袖B：权益权重先按和归一到80%，再加20% 510300；标定不据此挑λ、不做密封NAV回测"
        },
        "size_slack_max_sigma": SIZE_SLACK_MAX,
        "industry_slack_max_pp": IND_SLACK_MAX,
        "lot_rounding": {"default": LOT_DEFAULT, "STAR_688_689": LOT_STAR},
        "method": "median_implied_lambda_from_probe_solve_lambda_risk=1_turn=0_two_step_core",
        "lambda_risk": chosen,
        "percentiles": {
            "p10": float(np.percentile(arr, 10)),
            "p25": float(np.percentile(arr, 25)),
            "p50": float(np.median(arr)),
            "p75": float(np.percentile(arr, 75)),
            "p90": float(np.percentile(arr, 90)),
        },
        "n_probe_ok": len(ratios),
        "n_probe_total": len(days_data),
        "sensitivity_pm50pct": sens,
        "typical_abs_alpha_term": float(np.median(np.abs(alpha_terms))),
        "typical_risk_raw": float(np.median(risk_raws)),
        "aum_probe": aum,
        "x2_returns_used_for_selection": False,
        "details": details,
    }


def calibrate_lambda_turn(
    days_data: list[dict],
    *,
    aum: int,
    lambda_risk: float,
    target_median: float,
) -> dict[str, Any]:
    """Grid-search λ_turn so optimizer one-way turnover median ≈ target ±20%."""
    if target_median is None or target_median <= 0:
        return {"status": "BLOCKED", "reason": "no_b4_turnover_target"}
    # coarse grid then refine
    grid = [0.0, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 0.1, 0.3, 1.0, 3.0]
    best = None
    rows = []
    for lam_t in grid:
        turns = []
        infeas = 0
        w_prev = None
        for D in days_data:
            w0 = w_prev if w_prev is not None else D["wb"].copy()
            # align w0
            w0 = w0.reindex(D["alpha"].index).fillna(0.0)
            r = two_step_polish(
                D["alpha"], D["wb"], w0, D["industry"], D["ln_mcap"],
                D["B"], D["F"], D["delta"], D["betas"],
                aum=aum, lambda_risk=lambda_risk, lambda_turn=lam_t,
            )
            if r.w is None:
                infeas += 1
                continue
            # one-way vs w0
            idx = r.w.index.union(w0.index)
            tow = 0.5 * float((r.w.reindex(idx).fillna(0) - w0.reindex(idx).fillna(0)).abs().sum())
            turns.append(tow)
            w_prev = r.w
        med = float(np.median(turns)) if turns else None
        band_lo, band_hi = target_median * 0.8, target_median * 1.2
        hit = med is not None and band_lo <= med <= band_hi
        row = {
            "lambda_turn": lam_t,
            "median_one_way": med,
            "mean_one_way": float(np.mean(turns)) if turns else None,
            "n_ok": len(turns),
            "n_infeasible": infeas,
            "band_hit": hit,
        }
        rows.append(row)
        if med is None:
            continue
        err = abs(med - target_median)
        if best is None or err < best["err"]:
            best = {"lambda_turn": lam_t, "median_one_way": med, "err": err, "band_hit": hit, **row}

    # refine around best
    if best is not None and best["lambda_turn"] > 0:
        center = best["lambda_turn"]
        fine = sorted(set([center * x for x in (0.4, 0.6, 0.8, 1.0, 1.25, 1.5, 2.0)] + grid))
        for lam_t in fine:
            if any(abs(r["lambda_turn"] - lam_t) < 1e-15 for r in rows):
                continue
            turns = []
            infeas = 0
            w_prev = None
            for D in days_data:
                w0 = w_prev if w_prev is not None else D["wb"].copy()
                w0 = w0.reindex(D["alpha"].index).fillna(0.0)
                r = two_step_polish(
                    D["alpha"], D["wb"], w0, D["industry"], D["ln_mcap"],
                    D["B"], D["F"], D["delta"], D["betas"],
                    aum=aum, lambda_risk=lambda_risk, lambda_turn=lam_t,
                )
                if r.w is None:
                    infeas += 1
                    continue
                idx = r.w.index.union(w0.index)
                tow = 0.5 * float((r.w.reindex(idx).fillna(0) - w0.reindex(idx).fillna(0)).abs().sum())
                turns.append(tow)
                w_prev = r.w
            med = float(np.median(turns)) if turns else None
            band_lo, band_hi = target_median * 0.8, target_median * 1.2
            hit = med is not None and band_lo <= med <= band_hi
            row = {
                "lambda_turn": lam_t,
                "median_one_way": med,
                "mean_one_way": float(np.mean(turns)) if turns else None,
                "n_ok": len(turns),
                "n_infeasible": infeas,
                "band_hit": hit,
            }
            rows.append(row)
            if med is None:
                continue
            err = abs(med - target_median)
            if err < best["err"]:
                best = {"lambda_turn": lam_t, "median_one_way": med, "err": err, "band_hit": hit, **row}

    rows = sorted(rows, key=lambda x: x["lambda_turn"])
    return {
        "status": "OK" if best else "FAILED",
        "hard_spec": HARD_SPEC,
        "aum": aum,
        "lambda_risk_fixed": lambda_risk,
        "target_b4_median_one_way": target_median,
        "band_pm20pct": [target_median * 0.8, target_median * 1.2] if target_median else None,
        "lambda_turn": best["lambda_turn"] if best else None,
        "achieved_median_one_way": best["median_one_way"] if best else None,
        "band_hit": best["band_hit"] if best else False,
        "grid": rows,
        "core_benchmark_label": "capacity_adv_facing_core",
        "x2_returns_used_for_selection": False,
        "method": "grid_search_match_b4_paper_or_research_turnover_median",
    }


def memory_probe_book_smoke(n_names: int = 3000) -> dict[str, Any]:
    """Dry estimate of peak RSS for HI_LIQ-scale weight panel + returns slice."""
    before = rss_mb()
    # simulate weight long table denseness
    n_days = 60
    rng = np.random.default_rng(0)
    # sparse-ish weights: 30 names/day
    rows = n_days * 30
    w = rng.random(rows).astype(np.float32)
    # returns matrix probe
    rets = rng.standard_normal((L_SIGMA, min(n_names, 2500)), dtype=np.float32)
    peak = rss_mb()
    del w, rets
    gc.collect()
    return {
        "probe": "synthetic_hiliq_3000_names_L120_returns_float32_plus_60d_sparse_weights",
        "n_names_assumed": n_names,
        "rss_before_mb": before,
        "rss_peak_mb": peak,
        "rss_delta_mb": peak - before,
        "note_zh": "非真实 book-smoke；估 HI_LIQ~3000 名单进程内附加峰值。真实 book-smoke 另含引擎对象，建议预留 ≥ 该增量 + 400MB",
        "feasible_under_1p5gb": peak < 1500,
    }


def pick_sample_days(all_me: list[pd.Timestamp], n: int = 24) -> list[pd.Timestamp]:
    if len(all_me) <= n:
        return list(all_me)
    idx = np.linspace(0, len(all_me) - 1, n)
    return [all_me[int(round(i))] for i in idx]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-days", type=int, default=24)
    ap.add_argument("--skip-b4-reconstruct", action="store_true", default=True)
    ap.add_argument("--do-b4-reconstruct", action="store_true", help="heavy; avoid under 1.5GB")
    args = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    blockers: list[str] = []

    mask_sha = file_sha256(MASK_PATH)
    if mask_sha != MASK_SHA_EXPECT:
        blockers.append(f"mask_sha_mismatch got={mask_sha[:16]}… expect={MASK_SHA_EXPECT[:16]}…")

    all_me = month_ends(SEALED_START, SEALED_END)
    # cadence month_end_plus_first_last: sample month-ends + ensure first/last sealed sessions
    sample = pick_sample_days(all_me, args.n_days)
    if all_me:
        if all_me[0] not in sample:
            sample = [all_me[0]] + sample
        if all_me[-1] not in sample:
            sample = sample + [all_me[-1]]
        # dedupe preserve order
        seen=set(); sample=[d for d in sample if not (d in seen or seen.add(d))]
    print(f"[calib] sealed month-ends={len(all_me)} sample={len(sample)} RSS={rss_mb():.0f}MB sha_ok={mask_sha==MASK_SHA_EXPECT}")

    # B4 paper sealed turnover
    b4_ref = {str(aum): b4_paper_sealed_turnover(aum) for aum in (600_000, 1_000_000)}
    capadv_ref = {str(aum): capacity_adv_sealed_turnover(aum) for aum in (600_000, 1_000_000)}
    print("[calib] capacity_adv sealed turnover", {k: v.get("median_one_way") for k, v in capadv_ref.items()},
          "fallback_one_way", TURN_FALLBACK_ONE_WAY)
    print("[calib] B4 paper sealed turnover", {k: v.get("median_one_way") for k, v in b4_ref.items()})

    b4_recon = {}
    if False and args.do_b4_reconstruct and not args.skip_b4_reconstruct:  # Leo 08:20: B4 contrast only; skip heavy recon
        # reconstruct on a stride of month-ends (≥20)
        recon_days = pick_sample_days(all_me, max(36, args.n_days))
        # Reconstruct once at 100万 (name_cap tighter); 60万 reuses series with note (turnover similar order)
        print(f"[calib] reconstruct B4 research aum=1000000 days={len(recon_days)} RSS={rss_mb():.0f}")
        try:
            b4_recon["1000000"] = reconstruct_b4_research_month_end(recon_days, 1_000_000)
            print("  ->", b4_recon["1000000"].get("median_one_way"), "n", b4_recon["1000000"].get("n_turnover_obs"))
            b4_recon["600000"] = dict(b4_recon["1000000"])
            b4_recon["600000"]["aum_note"] = "shared_reconstruct_from_100w_namecap; paper sealed overlap remains aum-specific"
            b4_recon["600000"]["aum"] = 600000
        except Exception as e:
            blockers.append(f"b4_recon:{e}")
            b4_recon["1000000"] = {"status": "FAILED", "error": str(e), "traceback": traceback.format_exc()[-500:]}
            b4_recon["600000"] = b4_recon["1000000"]

    # prepare optimizer days
    days_data: list[dict] = []
    for day in sample:
        print(f"[calib] prepare {day.date()} RSS={rss_mb():.0f}MB")
        try:
            D = prepare_day(day)
        except Exception as e:
            print("  prepare fail", e)
            blockers.append(f"prepare_{day.date()}:{e}")
            D = None
        if D is None:
            continue
        days_data.append(D)
        if len(days_data) >= args.n_days and rss_mb() > 1200:
            break
        gc.collect()

    print(f"[calib] prepared {len(days_data)} days RSS={rss_mb():.0f}MB")
    if len(days_data) < 20:
        blockers.append(f"prepared_days_{len(days_data)}_lt_20")

    # λ_risk
    print("[calib] calibrate lambda_risk")
    risk_js = calibrate_lambda_risk(days_data, aum=1_000_000)
    lam_risk = float(risk_js.get("lambda_risk") or 1.0)
    print("  lambda_risk", lam_risk, risk_js.get("status"))

    # targets for turn: prefer research recon median if n_obs>=20 else paper sealed
    turn_js = {}
    for aum in (600_000, 1_000_000):
        paper = b4_ref[str(aum)]
        recon = b4_recon.get(str(aum), {})
        target = None
        target_src = None
        cap = capadv_ref.get(str(aum), {})
        # PRIMARY: capacity_adv same-window same-AUM; B4 contrast only
        if cap.get("n_turnover_obs", 0) >= 20 and cap.get("median_one_way"):
            target = float(cap["median_one_way"])
            target_src = "capacity_adv"
        elif cap.get("n_turnover_obs", 0) >= 10 and cap.get("median_one_way"):
            target = float(cap["median_one_way"])
            target_src = "capacity_adv_n>=10"
            blockers.append(f"capadv_turn_obs_{cap.get('n_turnover_obs')}_lt_20")
        else:
            target = float(TURN_FALLBACK_ONE_WAY)
            target_src = "monthly_two_way_50pct_fallback"
            blockers.append(
                f"capadv_sealed_weak_n={cap.get('n_turnover_obs')};using_fallback_one_way={TURN_FALLBACK_ONE_WAY}"
            )
        print(f"[calib] lambda_turn aum={aum} target={target} src={target_src}")
        js = calibrate_lambda_turn(days_data, aum=aum, lambda_risk=lam_risk, target_median=target or 0.0)
        js["turn_target_src"] = target_src
        js["target_source"] = target_src  # alias
        js["capacity_adv_ref"] = cap
        js["b4_contrast_only"] = paper
        js["b4_research_ref"] = recon
        js["cadence"] = CADENCE
        turn_js[aum] = js
        print("  ->", js.get("lambda_turn"), "hit", js.get("band_hit"), "achieved", js.get("achieved_median_one_way"))

    # INFEASIBLE rate at chosen lambdas
    infeas_stats = {}
    for aum in (600_000, 1_000_000):
        lam_t = float(turn_js[aum].get("lambda_turn") or 0.01)
        n_inf = 0
        n_ok = 0
        w_prev = None
        for D in days_data:
            w0 = w_prev if w_prev is not None else D["wb"].copy()
            w0 = w0.reindex(D["alpha"].index).fillna(0.0)
            r = two_step_polish(
                D["alpha"], D["wb"], w0, D["industry"], D["ln_mcap"],
                D["B"], D["F"], D["delta"], D["betas"],
                aum=aum, lambda_risk=lam_risk, lambda_turn=lam_t,
            )
            if r.w is None:
                n_inf += 1
            else:
                n_ok += 1
                w_prev = r.w
        rate = n_inf / max(n_inf + n_ok, 1)
        infeas_stats[str(aum)] = {"n_ok": n_ok, "n_infeasible": n_inf, "infeasible_rate": rate}
        if rate >= 0.5:
            blockers.append(f"systematic_INFEASIBLE_aum{aum}_rate={rate:.2f}")

    # Dual-sleeve sealed smoke metrics (NOT used for λ selection)
    sleeve_metrics = {"600000": {}, "1000000": {}}
    for aum in (600_000, 1_000_000):
        lam_t = float(turn_js[aum].get("lambda_turn") or 0.01)
        w_by = {}
        w_prev = None
        for D in days_data:
            w0 = w_prev if w_prev is not None else D["wb"].copy()
            w0 = w0.reindex(D["alpha"].index).fillna(0.0)
            r = two_step_polish(
                D["alpha"], D["wb"], w0, D["industry"], D["ln_mcap"],
                D["B"], D["F"], D["delta"], D["betas"],
                aum=aum, lambda_risk=lam_risk, lambda_turn=lam_t,
            )
            if r.w is None:
                continue
            w_by[D["day"]] = r.w
            w_prev = r.w
        try:
            sleeve_metrics[str(aum)] = sealed_sleeve_metrics_smoke(days_data, w_by)
        except Exception as e:
            sleeve_metrics[str(aum)] = {"status": "FAILED", "error": str(e)}
            blockers.append(f"sleeve_metrics_{aum}:{e}")
        print(f"[calib] sleeve metrics aum={aum}", sleeve_metrics[str(aum)].get("status"),
              {k: (v.get("Sharpe"), v.get("MDD"), v.get("IR_vs_510300"))
               for k, v in (sleeve_metrics[str(aum)].get("sleeves") or {}).items()})

    mem = memory_probe_book_smoke(3000)

    meta = {
        "hard_spec": HARD_SPEC,
        "window": [SEALED_START, SEALED_END],
        "mask_path": str(MASK_PATH.relative_to(ROOT)),
        "mask_sha256": mask_sha,
        "mask_sha_expected": MASK_SHA_EXPECT,
        "annualization": ANNUALIZATION,
        "solvers": ["OSQP", "cvxpy"],
        "objective": "max w'α − λ_risk (w−wb)'Σ(w−wb) − λ_turn ||w−w0||_1",
        "tc": "L1_only",
        "nu": 0,
        "wb_proxy": "float_mktcap_hiliq",
        "sigma": "SW_L1_industry_factor_plus_diag_idio_60d_var",
        "L_sigma": L_SIGMA,
        "core_arm": True,
        "domain_budget": False,
        "fast_gate": False,
        "two_step_polish": True,
        "name_cap": NAME_CAP,
        "neff_target": [NEFF_LO, NEFF_HI],
        "industry_active_vs_wb": IND_ACTIVE,
        "industry_abs_cap": IND_ABS,
        "size_midcap_box": SIZE_BOX,
        "size_slack_allowed": True,
        "beta_box_vs_wb": BETA_BOX,
        "n_rebalance_days_sampled": len(days_data),
        "rebalance_days": [str(D["day"].date()) for D in days_data],
        "infeasible_stats": infeas_stats,
        "lambda_risk": risk_js.get("lambda_risk"),
        "lambda_turn_60w": turn_js[600_000].get("lambda_turn"),
        "lambda_turn_100w": turn_js[1_000_000].get("lambda_turn"),
        "b4_turnover_paper_sealed": b4_ref,
        "b4_turnover_research_reconstruct": b4_recon,
        "alpha_source": days_data[0]["alpha_source"] if days_data else None,
        "x2_returns_used_for_selection": False,
        "statement_zh": "标定未使用 X2（2024-06 起）收益 / CAGR / MDD 选 λ；仅看约束可行性、换手、主动暴露。",
        "blockers": blockers,
        "memory_probe": mem,
        "sleeve_metrics_sealed_smoke": sleeve_metrics,
        "sleeve_metrics_used_for_lambda": False,
        "peak_rss_mb": rss_mb(),
        "elapsed_sec": time.time() - t0,
        "created_et": datetime.now().astimezone().isoformat(timespec="seconds"),
        "live": False,
        "promotion_approved": False,
        "strategy_promotion": False,
    }

    # Arch N2 gate: refuse FINAL calib_meta if sample weak
    turn_srcs = {str(a): turn_js[a].get("turn_target_src") for a in (600_000, 1_000_000)}
    turn_ok = all(
        turn_srcs[str(a)] in (
            "capacity_adv",
            "capacity_adv_n>=10",
            "monthly_two_way_50pct_fallback",
        )
        for a in (600_000, 1_000_000)
    )
    n2_ok = (
        len(days_data) >= 20
        and risk_js.get("status") == "OK"
        and turn_ok
        and meta.get("hard_spec") == HARD_SPEC
        and meta.get("x2_returns_used_for_selection") is False
        and "equity80_etf20_510300" in (meta.get("report_sleeves") or [])
        and meta.get("cadence") == CADENCE
    )
    meta["arch_n2_gate"] = {
        "prepared_days": len(days_data),
        "turn_target_src": turn_srcs,
        "turn_ok": turn_ok,
        "b4_role": "contrast_only",
        "pass": n2_ok,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Always write risk/turn drafts; meta FINAL only if N2 passes
    (OUT_DIR / "calib_lambda_risk.json").write_text(json.dumps(risk_js, ensure_ascii=False, indent=2) + "\n")
    (OUT_DIR / "calib_lambda_turn_60w.json").write_text(json.dumps(turn_js[600_000], ensure_ascii=False, indent=2) + "\n")
    (OUT_DIR / "calib_lambda_turn_100w.json").write_text(json.dumps(turn_js[1_000_000], ensure_ascii=False, indent=2) + "\n")
    if n2_ok:
        (OUT_DIR / "calib_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
        # remove any rejected stub
        stub = OUT_DIR / "calib_meta.REJECTED_WEAK.json"
        if stub.exists():
            stub.unlink()
        print("[calib] wrote FINAL calib_meta (Arch N2 pass) RSS", rss_mb(), "blockers", blockers)
        return 0
    else:
        (OUT_DIR / "calib_meta.REJECTED_WEAK.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
        if (OUT_DIR / "calib_meta.json").exists():
            (OUT_DIR / "calib_meta.json").unlink()
        print("[calib] Arch N2 FAIL — no final calib_meta.json", meta["arch_n2_gate"], "blockers", blockers)
        return 3


if __name__ == "__main__":
    sys.exit(main())
