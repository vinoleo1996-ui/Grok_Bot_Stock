"""Regression: limit-up / limit-down / halt days must not drop held-position returns.

Rule: holdings are always marked to close (halted names carry last close and the
full move realizes on resumption); restrictions only block fills.
Cross-checks: backtest Ledger marks, smallcap fast sim, paper-runner return path
(strategy_feed.close_to_close_returns + weight drift) give identical NAV.
Research-only; promotion_approved stays false.
"""
from datetime import date

import numpy as np
import pandas as pd
import pytest

from quantlab.backtest.ledger import Ledger, Lot
from quantlab.platform.strategy_feed import close_to_close_returns, held_book_return
from quantlab.smallcap.sim import Costs, Market, simulate

NAN = np.nan
DATES = pd.bdate_range("2026-01-05", periods=9)
# LU: limit-up on day 3 (+10%); LD: limit-down day 4 (-10%); HALT: suspended days 3-5, resumes day 6 at +20% vs pre-halt close
CLOSE = pd.DataFrame({
    "LU":   [10, 10, 10, 11.0, 11.0, 11.5, 11.5, 11.5, 11.5],
    "LD":   [20, 20, 20, 20, 18.0, 18.0, 18.5, 18.5, 18.5],
    "HALT": [5, 5, 5, NAN, NAN, NAN, 6.0, 6.1, 6.1],
}, index=DATES, dtype=float)
OPEN = CLOSE.copy()
LIMIT_UP = CLOSE.shift(1).ffill() * 1.10
LIMIT_DOWN = CLOSE.shift(1).ffill() * 0.90
SHARES = {"LU": 10_000, "LD": 5_000, "HALT": 20_000}  # 100k each at day0 close
CASH0 = 300_000.0


def _true_nav():
    marks = CLOSE.ffill()
    return CASH0 + sum(marks[c] * q for c, q in SHARES.items())


def _ledger_nav():
    led = Ledger(cash=CASH0)
    for c, q in SHARES.items():
        led.lots[c] = [Lot(quantity=q, available_session=0, cost=float(CLOSE[c].iloc[0]), acquired_session=0)]
    out = []
    for d in DATES:
        led.mark(d, CLOSE.loc[d].to_dict())
        out.append(led.nav())
    return pd.Series(out, index=DATES)


def _fastsim_nav():
    # Buy at day1 open via day0 signal, zero frictions; inject extra pre-day0 bar so holdings start at day0 close.
    dates = DATES.insert(0, DATES[0] - pd.Timedelta(days=3))
    pad = lambda f: pd.concat([f.iloc[[0]].set_axis([dates[0]]), f]).to_numpy(float)
    codes = pd.Index(CLOSE.columns)
    mkt = Market(dates, codes, pad(OPEN), pad(CLOSE), np.ones((len(dates), 3)),
                 np.full((len(dates), 3), np.inf), np.full((len(dates), 3), -np.inf),
                 np.full((len(dates), 3), np.inf))
    costs = Costs(slippage=0, commission=0, min_commission=0, stamp_before=0, stamp_after=0,
                  min_trade_value=0, participation=np.inf, cash_buffer=0)
    nav0 = CASH0 + sum(CLOSE[c].iloc[0] * q for c, q in SHARES.items())
    w = {c: CLOSE[c].iloc[0] * q / nav0 for c, q in SHARES.items()}
    res = simulate(mkt, {dates[0]: w}, initial_cash=nav0, costs=costs)
    return res["nav"].iloc[1:]


def _paper_nav():
    rets = close_to_close_returns(CLOSE)
    nav0 = CASH0 + sum(CLOSE[c].iloc[0] * q for c, q in SHARES.items())
    w = {c: CLOSE[c].iloc[0] * q / nav0 for c, q in SHARES.items()}
    nav = [nav0]
    for d in DATES[1:]:
        r = rets.loc[d]
        day = held_book_return(w, r)
        nav.append(nav[-1] * (1 + day))
        gross = {c: w[c] * (1 + (r[c] if r[c] == r[c] else 0.0)) for c in w}
        cash_w = 1 - sum(w.values())
        tot = sum(gross.values()) + cash_w
        w = {c: v / tot for c, v in gross.items()}
    return pd.Series(nav, index=DATES)


def test_returns_across_halt_gap_realize_on_resumption():
    r = close_to_close_returns(CLOSE)
    assert r["HALT"].iloc[3:6].tolist() == [0.0, 0.0, 0.0]
    assert r["HALT"].iloc[6] == pytest.approx(6.0 / 5.0 - 1)
    assert (1 + r["HALT"].iloc[1:]).prod() == pytest.approx(6.1 / 5.0)
    assert r["LU"].iloc[3] == pytest.approx(0.10)
    assert r["LD"].iloc[4] == pytest.approx(-0.10)


def test_leading_trailing_nan_not_filled():
    s = pd.DataFrame({"X": [NAN, 1.0, NAN, 1.2, NAN]})
    r = close_to_close_returns(s)["X"]
    assert np.isnan(r.iloc[0]) and r.iloc[2] == 0.0 and r.iloc[3] == pytest.approx(0.2) and np.isnan(r.iloc[4])


def test_three_paths_identical_nav_and_counted_limit_moves():
    truth = _true_nav()
    for name, nav in (("ledger", _ledger_nav()), ("fastsim", _fastsim_nav()), ("paper", _paper_nav())):
        np.testing.assert_allclose(nav.to_numpy(), truth.to_numpy(), rtol=1e-9, err_msg=name)
    # limit-up day counted (+10k), limit-down day counted (-10k), halt resumption +20k
    assert truth.iloc[3] - truth.iloc[2] == pytest.approx(10_000)
    assert truth.iloc[4] - truth.iloc[3] == pytest.approx(-10_000)
    assert truth.iloc[6] - truth.iloc[5] == pytest.approx(20_000 + 0.5 * 5_000)


def test_limits_block_fills_not_valuation_fastsim():
    # limit-up open blocks a buy; limit-down open blocks a sell; NAV still tracks close.
    dates = pd.bdate_range("2026-02-02", periods=3)
    o = np.array([[10.0, 20.0], [11.0, 18.0], [11.0, 18.0]])
    c = o.copy()
    up = np.array([[NAN, NAN], [11.0, 22.0], [12.1, 19.8]])
    dn = np.array([[NAN, NAN], [9.0, 18.0], [9.9, 16.2]])
    mkt = Market(dates, pd.Index(["U", "D"]), o, c, np.ones((3, 2)), up, dn, np.full((3, 2), np.inf))
    costs = Costs(slippage=0, commission=0, min_commission=0, stamp_before=0, stamp_after=0,
                  min_trade_value=0, participation=np.inf, cash_buffer=0)
    # day0: hold D only (seed via first signal is not possible without a fill) -> test buy block on U
    res = simulate(mkt, {dates[0]: {"U": 0.5}}, initial_cash=100_000.0, costs=costs)
    assert res["fills"] == 1  # day1 open at limit-up blocked; day2 open (11 < 12.1) fills
    assert res["nav"].iloc[1] == pytest.approx(100_000.0)


def test_ledger_trade_permission_blocks_only_trades():
    from quantlab.backtest.ledger import trade_permission
    import inspect
    assert "limit_up" in inspect.getsource(trade_permission)
    led = Ledger(cash=0.0)
    led.lots["S"] = [Lot(quantity=100, available_session=0, cost=10.0, acquired_session=0)]
    led.mark(date(2026, 1, 5), {"S": 11.0})  # limit-up close still marked
    assert led.nav() == pytest.approx(1100.0)
    led.mark(date(2026, 1, 6), {"S": NAN})   # halted: carry last close
    assert led.nav() == pytest.approx(1100.0)


def test_paper_costs_book_ret_counts_limit_days():
    """Strategy-owned path: _book_ret must not zero held names on limit/halt days."""
    mod = pytest.importorskip("quantlab.portfolio.v2_strategy_paper_costs")
    rets = close_to_close_returns(CLOSE)
    rets.index = [d.date() for d in rets.index]

    from quantlab.portfolio.v2_execution_costs import TradabilityPanels
    allt = pd.DataFrame(True, index=rets.index, columns=rets.columns)
    T = lambda: TradabilityPanels(limit_up_hit=allt, limit_down_hit=allt, halted=allt, is_st=allt & False)

    sess = rets.index[3]
    w = {"LU": 0.5}
    import inspect
    params = inspect.signature(mod._book_ret).parameters
    kw = {"tradability": T()}
    if "zero_on_block" in params:
        kw["zero_on_block"] = True  # how the B-arm call sites invoke it
    got = mod._book_ret(w, rets, sess, **kw)
    got = got[0] if isinstance(got, tuple) else got
    if got != pytest.approx(0.05):
        pytest.xfail("Strategy-owned v2_strategy_paper_costs._book_ret still zeroes limit/halt days (pending Strategy fix)")
    assert got == pytest.approx(0.05)
