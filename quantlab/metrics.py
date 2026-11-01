"""Single source of truth for performance metrics (arch audit P1#1, 2026-10-14).

Convention: A-share annualisation PERIODS = 244 trading days/year (SSE has 242-244 sessions per year).
CAGR = (nav_end/nav_start) ** (PERIODS / n_returns) - 1, i.e. years = number of daily returns / 244.
Sharpe/vol: rf=0, daily simple returns, ddof=1, x sqrt(244). MDD on the NAV path. Calmar = CAGR / |MDD|.
Monthly win rate: calendar months by compounded daily returns; INCOMPLETE first/last months are EXCLUDED
(a month is complete only if the series covers its first and last SSE trading sessions; for a NAV series the
first point is the base, so the first month counts only if the base is on/before the month's first session).
Each result carries `monthly_note` saying what was excluded. Research only; live=false."""
from __future__ import annotations
import math
import numpy as np
import pandas as pd

PERIODS = 244
CONVENTION = "annualisation 244 trading days (quantlab.metrics); monthly win rate excludes incomplete first/last months"


def _s(x) -> pd.Series:
    s = pd.Series(x).dropna().astype(float)
    if not isinstance(s.index, pd.DatetimeIndex):
        try: s.index = pd.to_datetime(s.index.astype(str).str[:10])
        except Exception: pass
    return s.sort_index()


def returns(nav) -> pd.Series:
    return _s(nav).pct_change().dropna()


def nav_from_returns(r, base=1.0) -> pd.Series:
    return base * (1 + _s(r)).cumprod()


def cagr_from_returns(r, periods=PERIODS):
    r = _s(r); return float((1 + r).prod() ** (periods / len(r)) - 1) if len(r) else None


def cagr(nav, periods=PERIODS):
    n = _s(nav); k = len(n) - 1
    return float((n.iloc[-1] / n.iloc[0]) ** (periods / k) - 1) if k > 0 and n.iloc[0] > 0 else None


def mdd(nav):
    n = _s(nav); return float((n / n.cummax() - 1).min()) if len(n) else None


def mdd_from_returns(r):
    return mdd((1 + _s(r)).cumprod().pipe(lambda x: pd.concat([pd.Series([1.0]), x.reset_index(drop=True)])))


def vol(r, periods=PERIODS):
    r = _s(r); return float(r.std(ddof=1) * math.sqrt(periods)) if len(r) > 1 else None


def sharpe(r, periods=PERIODS):
    r = _s(r); sd = r.std(ddof=1) if len(r) > 1 else float("nan")
    return float(r.mean() / sd * math.sqrt(periods)) if sd and sd > 1e-12 else None


def calmar(c, m):
    return float(c / -m) if c is not None and m is not None and m < 0 else None


def annualise_mean(x, periods=PERIODS):
    return float(np.mean(x) * periods)


def daily_win_rate(r):
    r = _s(r); return float((r > 0).mean()) if len(r) else None


def _sessions():
    try:
        from quantlab.portfolio.trade_calendar import open_days
        return open_days()
    except Exception:
        return None


def monthly_returns(r, complete_only=True, nav_base=None):
    """Compounded calendar-month returns from daily returns. nav_base: date of the NAV base point (first NAV row)."""
    r = _s(r)
    m = (1 + r).groupby(r.index.to_period("M")).prod() - 1
    if not complete_only or m.empty:
        return m, "all calendar months (incomplete first/last included)"
    cal = _sessions(); drop = []
    first_obs = pd.Timestamp(nav_base) if nav_base is not None else r.index[0]
    for p, end_obs, start_obs, tag in ((m.index[0], None, first_obs, "first"), (m.index[-1], r.index[-1], None, "last")):
        if cal is not None:
            ms = cal[(cal >= p.start_time) & (cal <= p.end_time)]
            lo, hi = (ms.min(), ms.max()) if len(ms) else (p.start_time, p.end_time)
        else:
            b = pd.bdate_range(p.start_time, p.end_time); lo, hi = b.min(), b.max()
        if tag == "first":
            ok = (start_obs <= lo) if nav_base is not None else (r.index[0] <= lo)
        else:
            ok = end_obs >= hi
        if not ok: drop.append((p, tag))
    keep = m.drop([p for p, _ in drop], errors="ignore")
    note = "excluded incomplete: " + (", ".join(f"{t} {p}" for p, t in drop) if drop else "none") + f"; months used {len(keep)}"
    return keep, note


def monthly_win_rate(r, bench=None, nav_base=None):
    m, note = monthly_returns(r, nav_base=nav_base)
    out = dict(monthly_win=float((m > 0).mean()) if len(m) else None, months=int(len(m)), monthly_note=note)
    if bench is not None:
        b = _s(bench).reindex(_s(r).index).fillna(0)
        bm, _ = monthly_returns(b, nav_base=nav_base); bm = bm.reindex(m.index)
        out["monthly_beat"] = float((m > bm).mean()) if len(m) else None
    return out


def summary(nav, bench_nav=None):
    n = _s(nav); r = returns(n); c = cagr(n); d = mdd(n)
    out = dict(cagr=c, mdd=d, calmar=calmar(c, d), sharpe=sharpe(r), vol=vol(r), daily_win=daily_win_rate(r),
               total_return=float(n.iloc[-1] / n.iloc[0] - 1), start=str(n.index[0])[:10], end=str(n.index[-1])[:10],
               n_returns=int(len(r)), periods_per_year=PERIODS)
    out.update(monthly_win_rate(r, returns(bench_nav) if bench_nav is not None else None, nav_base=n.index[0]))
    return out
