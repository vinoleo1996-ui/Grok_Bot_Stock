import numpy as np
import pandas as pd
import pytest
from dataclasses import replace

from quantlab.platform.execution import (ExecConfig, ExecPanels, ZERO_COST, reconcile_zero_cost,
                                         run_weight_schedule, total_return_factor)
from quantlab.platform.strategy_feed import close_to_close_returns

D = pd.bdate_range("2025-03-03", periods=8)
CFG = ExecConfig(fill="close", enforce_limits=False, participation_cap=None, **ZERO_COST)


def _panels(close, cash=None, ratio=None, factor=None, code="sz.000001"):
    c = pd.DataFrame({code: close}, index=D)
    z = lambda v: None if v is None else pd.DataFrame({code: v}, index=D)
    return ExecPanels(close=c, open=c.copy(), cash_div=z(cash), share_ratio=z(ratio), adj_factor=z(factor))


def test_cash_dividend_nav_unchanged_except_tax():
    close = [10, 10, 10, 9.5, 9.5, 9.5, 9.5, 9.5]   # ex 0.5 on D[3]
    cash = [0, 0, 0, 0.5, 0, 0, 0, 0]
    p = _panels(close, cash=cash)
    r = run_weight_schedule(p, {D[0]: {"sz.000001": 1.0}}, initial_cash=100_000, config=CFG)
    nav = r["nav"]
    assert nav.iloc[-1] == pytest.approx(100_000, abs=1e-6)
    assert r["final_shares"]["sz.000001"] == 10_000
    taxed = run_weight_schedule(p, {D[0]: {"sz.000001": 1.0}}, initial_cash=100_000,
                                config=replace(CFG, dividend_tax=0.10))["nav"]
    assert taxed.iloc[-1] == pytest.approx(100_000 - 10_000 * 0.5 * 0.10)
    old = run_weight_schedule(p, {D[0]: {"sz.000001": 1.0}}, initial_cash=100_000,
                              config=replace(CFG, corporate_actions=False))["nav"]
    assert old.iloc[-1] == pytest.approx(95_000)   # legacy behaviour reproducible


def test_bonus_10_for_10_doubles_shares_nav_continuous():
    close = [10, 10, 10, 5, 5, 5, 5, 5]
    p = _panels(close, ratio=[0, 0, 0, 1.0, 0, 0, 0, 0])
    r = run_weight_schedule(p, {D[0]: {"sz.000001": 1.0}}, initial_cash=100_000, config=CFG)
    assert r["final_shares"]["sz.000001"] == 20_000
    assert (r["nav"] - 100_000).abs().max() < 1e-6


def test_factor_fallback_and_event_factor_mismatch():
    close = [10, 10, 10, 9.5, 9.5, 9.5, 9.5, 9.5]
    fac = [1, 1, 1, 10 / 9.5, 10 / 9.5, 10 / 9.5, 10 / 9.5, 10 / 9.5]
    p = _panels(close, factor=fac)            # no event rows -> factor ratio scales shares
    nav = run_weight_schedule(p, {D[0]: {"sz.000001": 1.0}}, initial_cash=100_000, config=CFG)["nav"]
    assert nav.iloc[-1] == pytest.approx(100_000, rel=1e-9)
    # bogus 10-for-10 event that the factor contradicts (reorg transfer to investors) -> factor wins
    p2 = _panels(close, ratio=[0, 0, 0, 1.0, 0, 0, 0, 0], factor=fac)
    r2 = run_weight_schedule(p2, {D[0]: {"sz.000001": 1.0}}, initial_cash=100_000, config=CFG)
    assert r2["nav"].iloc[-1] == pytest.approx(100_000, rel=1e-9)
    assert r2["corporate_action_flags"]


def test_lots_trade_on_raw_prices_after_bonus():
    close = [10, 10, 10, 5, 5, 5, 5, 5]
    p = _panels(close, ratio=[0, 0, 0, 0.5, 0, 0, 0, 0])   # 10-for-5: 1000 -> 1500 shares
    cfg = replace(CFG, fill="next_open")
    r = run_weight_schedule(p, {D[0]: {"sz.000001": 0.1}, D[5]: {"sz.000001": 0.0}}, initial_cash=100_000,
                            config=cfg, record_fills=True)
    buys = [f for f in r["fills"] if f["side"] > 0]
    sells = [f for f in r["fills"] if f["side"] < 0]
    assert buys[0]["qty"] == 1000 and buys[0]["price"] == 10
    assert sells[0]["qty"] == 1500 and sells[0]["price"] == 5     # raw price, post-bonus share count
    assert not r["final_shares"]


def test_three_engines_reconcile_with_corporate_actions():
    rng = np.random.default_rng(0)
    codes = ["sz.000001", "sh.600000", "sz.000002"]
    px = pd.DataFrame(10 * np.cumprod(1 + rng.normal(0, 0.01, (len(D), 3)), axis=0).round(2), index=D, columns=codes)
    cash = pd.DataFrame(0.0, index=D, columns=codes); ratio = cash.copy()
    cash.iloc[3, 0] = 0.3; px.iloc[3:, 0] = (px.iloc[3:, 0] - 0.3).round(2)
    ratio.iloc[4, 1] = 1.0; px.iloc[4:, 1] = (px.iloc[4:, 1] / 2).round(2)
    p = ExecPanels(close=px, open=px.copy(), cash_div=cash, share_ratio=ratio)
    sched = {D[0]: {c: 0.3 for c in codes}, D[5]: {codes[0]: 0.5, codes[1]: 0.4}}
    rep = reconcile_zero_cost(p, sched, initial_cash=1_000_000)
    navs = rep["navs"]
    for e in ("ledger", "fastsim"):
        assert (navs[e] / navs["platform"] - 1).abs().max() < 1e-9, e
    # total-return closes have no fake ex-date drop
    trr = close_to_close_returns(px, total_return_factor(p))
    assert trr.iloc[4, 1] > -0.05 and trr.iloc[3, 0] > -0.05
