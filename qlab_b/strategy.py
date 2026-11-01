"""qlab_b challenger: 12-1 cross-sectional momentum, top-20 equal weight, monthly.

Owns the DECISION only. Reuses quantlab's engine/ledger for execution, fees, taxes,
risk-exit and reconciliation, so the comparison ruler is identical to the opponent's.
Parameters are frozen in hypothesis.md; this file encodes them, it does not tune them.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

LOOKBACK = 252   # ~12 months
SKIP = 21        # skip most recent ~1 month (standard 12-1 momentum)
TOP_N = 20       # max positions
GROSS = 0.98     # mandate: leave room for cash
MAX_WEIGHT = 0.06  # mandate per-stock cap (0.98/20=4.9% < 6% so equal weight complies)
INDUSTRY_CAGE = 0.25  # enforced policy: unknown-sector stocks share one capped group


def momentum_schedule(close: pd.DataFrame, is_st: pd.DataFrame | None,
                      tradestatus: pd.DataFrame | None, reviews,
                      *, industry_policy: str = "enforced") -> dict:
    """Return {review_date: {code: target_weight}} using only data up to the prior session.

    close/review alignment: decision for date d uses close strictly before d.
    """
    schedule = {}
    for d in reviews:
        d = pd.Timestamp(d)
        hist = close.loc[close.index < d]
        if len(hist) < LOOKBACK + SKIP + 1:
            continue
        past = hist.iloc[-(LOOKBACK + SKIP + 1)]
        recent = hist.iloc[-(SKIP + 1)]
        with np.errstate(divide="ignore", invalid="ignore"):
            mom = recent / past - 1.0
        mom = mom.replace([np.inf, -np.inf], np.nan)
        # tradability screen on the prior session (execution is the next open)
        prev = hist.index[-1]
        ok = pd.Series(True, index=close.columns)
        if is_st is not None and prev in is_st.index:
            ok &= ~is_st.loc[prev].fillna(False).astype(bool)
        if tradestatus is not None and prev in tradestatus.index:
            ok &= tradestatus.loc[prev].fillna(0).astype(float).eq(1)
        mom = mom.where(ok).dropna()
        if mom.empty:
            schedule[d] = {}
            continue
        picked = mom.sort_values(ascending=False).head(TOP_N)
        n = len(picked)
        if n == 0:
            schedule[d] = {}
            continue
        w = GROSS / n
        w = min(w, MAX_WEIGHT)
        # industry policy: all sectors are UNKNOWN here, so enforced == cap total
        if industry_policy == "enforced":
            total = w * n
            if total > INDUSTRY_CAGE:
                w = INDUSTRY_CAGE / n
        target = {c: float(w) for c in picked.index}
        if sum(target.values()) > GROSS + 1e-12:  # safety
            scale = GROSS / sum(target.values())
            target = {c: v * scale for c, v in target.items()}
        schedule[d] = target
    return schedule
