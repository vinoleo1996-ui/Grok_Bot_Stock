"""Margin financing (融资) account for the V2 platform engine. Opt-in:
``run_weight_schedule(..., margin=MarginConfig(...))``; default None leaves every result unchanged.
Docs: docs/v2/EXECUTION_FUTURES_CASH.md §5.

Accounting (single cash/collateral pool shared with stocks/ETFs/CBs and the futures leg):
  cash may go negative; debt = max(-cash, 0). equity (NAV) = cash + MV(longs) + futures unrealized
  (= positive cash + MV + futures VM-in-cash - debt).
  buy capacity = cash - futures margin reserve + credit, credit = max(0, (max_leverage-1)*equity_open
  - max(-cash,0) ... ) implemented as: cash_after - reserve >= -(max_leverage-1)*equity_open.
  interest: at each session start, debt at prior close x financing rate per session (debited to cash).
  maintenance ratio (维持担保比例) = (sum MV_i*haircut_i + max(cash,0)) / debt, checked at close.
Short selling (融券) is out of scope.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

import numpy as np
import pandas as pd


@dataclass
class MarginConfig:
    financing_rate: object = 0.06          # annual decimal: float, or pd.Series by date (base, e.g. Shibor 3M / LPR)
    spread: float = 0.0                    # added to financing_rate (annual decimal)
    day_count: float = 365.0               # ACT/day_count (360 or 365)
    max_leverage: float = 2.0              # max gross long MV / equity when opening new debt
    warning_ratio: float = 1.50            # 维持担保比例 warning line (event only)
    liquidation_ratio: float = 1.30        # 维持担保比例 平仓线
    restore_ratio: float = 1.50            # forced selling targets this ratio
    liquidation_action: str = "liquidate"  # liquidate (pro-rata sell at next session's fill) | flag
    haircuts: Mapping | None = None        # {code: factor}; default 1.0 for every code
    default_haircut: float = 1.0

    def __post_init__(self):
        assert self.liquidation_action in ("liquidate", "flag")
        assert self.max_leverage >= 1.0 and self.day_count > 0
        assert self.restore_ratio >= self.liquidation_ratio > 1.0


def financing_rate_per_session(dates: pd.DatetimeIndex, cfg: MarginConfig) -> np.ndarray:
    """r[t] applied to debt held over (t-1 close -> t). Rate fixed at t-1 (Series ffilled), ACT/day_count."""
    dates = pd.DatetimeIndex(dates)
    r = np.zeros(len(dates))
    if len(dates) < 2:
        return r
    days = np.diff(dates.values).astype("timedelta64[D]").astype(float)
    fr = cfg.financing_rate
    if np.isscalar(fr):
        a = np.full(len(dates), float(fr))
    else:
        s = pd.Series(fr).copy(); s.index = pd.to_datetime(s.index); s = s.sort_index()
        a = s.reindex(s.index.union(dates)).ffill().reindex(dates).bfill().to_numpy(float)
    a = a + float(cfg.spread)
    r[1:] = a[:-1] * days / float(cfg.day_count)
    return r


class MarginBook:
    def __init__(self, cfg: MarginConfig, dates, codes, events: list):
        self.cfg = cfg; self.dates = dates; self.codes = codes; self.events = events
        self.R = financing_rate_per_session(dates, cfg)
        h = cfg.haircuts or {}
        self.H = np.array([float(h.get(c, cfg.default_haircut)) for c in codes])
        n = len(dates)
        self.debt = np.zeros(n); self.lev = np.full(n, np.nan); self.ratio = np.full(n, np.nan)
        self.interest = np.zeros(n); self.interest_total = 0.0
        self.n_liq = 0; self.n_warn = 0

    def accrue(self, t, cash):
        if t == 0 or cash >= 0:
            return 0.0
        it = -cash * self.R[t]
        self.interest[t] = it; self.interest_total += it
        return -it

    def credit(self, equity, cash):
        """Extra spend allowed beyond cash - reserve (so that cash_after - reserve >= -cap)."""
        return max((self.cfg.max_leverage - 1.0) * equity, 0.0)

    def check(self, t, cash, shares, marks, equity):
        """Close-of-day: record leverage/ratio; return {j: forced sell qty>0} or {}."""
        mv = np.nan_to_num(shares * marks)
        gross = float(mv[mv > 0].sum())
        debt = max(-cash, 0.0)
        self.debt[t] = debt
        self.lev[t] = gross / equity if equity > 0 else np.inf
        if debt <= 0:
            return {}
        coll = float(np.sum(mv * self.H)) + max(cash, 0.0)
        ratio = coll / debt
        self.ratio[t] = ratio
        day = str(self.dates[t].date())
        if ratio < self.cfg.liquidation_ratio:
            R = self.cfg.restore_ratio
            # sell X of collateral (haircut-weighted avg h): (coll - h*X)/(debt - X) = R
            h = float(np.sum(mv * self.H) / mv.sum()) if mv.sum() > 0 else 1.0
            X = (R * debt - coll) / max(R - h, 1e-9)
            X = min(max(X, 0.0), float(mv.sum()))
            frac = X / mv.sum() if mv.sum() > 0 else 0.0
            self.n_liq += 1
            self.events.append(dict(date=day, reason="margin_liquidation", ratio=ratio, debt=debt, collateral=coll,
                                    sell_value=X, action=self.cfg.liquidation_action))
            if self.cfg.liquidation_action == "liquidate" and frac > 0:
                return {j: shares[j] * min(frac, 1.0) for j in np.flatnonzero(shares > 0)}
        elif ratio < self.cfg.warning_ratio:
            self.n_warn += 1
            self.events.append(dict(date=day, reason="margin_warning", ratio=ratio, debt=debt, collateral=coll))
        return {}

    def report(self):
        d = self.dates
        r = pd.Series(self.ratio, index=d)
        return dict(financing_interest=self.interest_total,
                    financing_interest_daily=pd.Series(self.interest, index=d),
                    debt=pd.Series(self.debt, index=d), leverage=pd.Series(self.lev, index=d),
                    peak_leverage=float(np.nanmax(self.lev)) if np.isfinite(self.lev).any() else float("nan"),
                    maintenance_ratio=r, min_maintenance_ratio=float(r.min()) if r.notna().any() else float("nan"),
                    liquidation_events=self.n_liq, margin_warnings=self.n_warn)
