"""CB + broader ETF support in the platform engine (synthetic)."""
import numpy as np
import pandas as pd
import pytest

from quantlab.platform.execution import (ExecConfig, ExecPanels, ZERO_COST, instrument_type, lot_rule_for,
                                         tick_for_code, stamp_exempt, round_order_quantity, fund_limit_pct,
                                         derived_limit_pct, run_weight_schedule, reconcile_zero_cost, round_to_tick)

CB, CB2, ETF, STAR_ETF, STK = "sh.113596", "sz.128100", "sh.510500", "sh.588000", "sz.000001"


def _panels(codes, n=8, start="2023-01-02", close=None, open_=None, tp=None):
    idx = pd.bdate_range(start, periods=n)
    base = {CB: 120.0, CB2: 110.0, ETF: 6.0, STAR_ETF: 1.0, STK: 10.0}
    rng = np.random.default_rng(0)
    c = close if close is not None else pd.DataFrame(
        {k: base.get(k, 10.0) * np.cumprod(1 + rng.normal(0, 0.01, n)) for k in codes}, index=idx)
    o = open_ if open_ is not None else c.shift(1).fillna(c) * 1.001
    v = pd.DataFrame(1e9, index=idx, columns=c.columns)
    return ExecPanels(close=c, open=o, volume=v, amount=v * c, terminal_price=tp)


def test_classifier_and_rules():
    assert instrument_type("sh.113596") == "cb" and instrument_type("113596.SH") == "cb"
    for c in ("sh.110059", "sh.111001", "sh.118000", "sz.123001", "sz.127001", "sz.128001"):
        assert instrument_type(c) == "cb"
    assert instrument_type("sh.132001") == "eb"  # EB classified separately (not CB)
    assert instrument_type("sh.510300") == "fund" and instrument_type("sz.159915") == "fund"
    assert instrument_type("sz.000001") == "stock" and instrument_type("sh.600000") == "stock"
    assert lot_rule_for(CB).minimum == 10 and lot_rule_for(CB).step == 10
    assert round_order_quantity(CB, 57, 1) == 50
    assert tick_for_code(CB) == 0.001 and tick_for_code(STK) == 0.01
    assert stamp_exempt(CB) and stamp_exempt(ETF) and not stamp_exempt(STK)
    assert round_to_tick(123.4567, tick_for_code(CB)) == pytest.approx(123.457)


def _sell_fill(code, cfg_kw):
    p = _panels([code])
    d = p.close.index
    sch = {d[0]: {code: 0.5}, d[3]: {}}
    cfg = ExecConfig(fill="next_open", price_tick="auto", enforce_limits=False, **cfg_kw)
    return run_weight_schedule(p, sch, initial_cash=100_000, config=cfg, record_fills=True)


def test_cb_stamp_exempt_and_commission_min():
    r = _sell_fill(CB, {})
    assert all(f["stamp"] == 0 for f in r["fills"])
    for f in r["fills"]:
        assert f["commission"] == pytest.approx(max(1.0, f["qty"] * f["price"] * 0.0001))
        assert f["qty"] % 10 == 0
    # small trade -> min commission 1 CNY
    r2 = _sell_fill(CB, {})
    p = _panels([CB]); d = p.close.index
    r3 = run_weight_schedule(p, {d[0]: {CB: 0.05}}, initial_cash=100_000,
                             config=ExecConfig(price_tick="auto", enforce_limits=False), record_fills=True)
    assert r3["fills"][0]["commission"] == 1.0
    # stock still stamped, stock commission 5 min
    rs = _sell_fill(STK, {})
    assert any(f["stamp"] > 0 for f in rs["fills"])
    assert all(f["commission"] >= 5.0 for f in rs["fills"])


def test_cb_tick_rounding():
    r = _sell_fill(CB, {})
    for f in r["fills"]:
        assert abs(f["price"] / 0.001 - round(f["price"] / 0.001)) < 1e-6


def _limit_case(code, start, jump):
    idx = pd.bdate_range(start, periods=4)
    c = pd.DataFrame({code: [100.0, 100.0, 100.0, 100.0]}, index=idx)
    o = c.copy(); o.iloc[1] = 100.0 * (1 + jump)
    p = ExecPanels(close=c, open=o, volume=c * 1e6, amount=c * 1e8)
    r = run_weight_schedule(p, {idx[0]: {code: 0.5}}, initial_cash=100_000,
                            config=ExecConfig(price_tick="auto", unfilled="drop", **ZERO_COST), record_fills=True)
    return r


def test_cb_limits_pre_post_2022_08_01():
    assert derived_limit_pct(CB, "2022-07-29") is None and derived_limit_pct(CB, "2022-08-01") == 0.20
    assert len(_limit_case(CB, "2022-06-01", 0.25)["fills"]) == 1          # no limit pre-2022-08
    assert len(_limit_case(CB, "2023-06-01", 0.25)["fills"]) == 0          # blocked beyond +20%
    assert len(_limit_case(CB, "2023-06-01", 0.15)["fills"]) == 1


def test_etf_limits_10_20():
    assert fund_limit_pct(ETF) == 0.10 and fund_limit_pct(STAR_ETF) == 0.20
    assert len(_limit_case(ETF, "2023-06-01", 0.12)["fills"]) == 0
    assert len(_limit_case(STAR_ETF, "2023-06-01", 0.12)["fills"]) == 1
    # no_limit_codes override
    idx = pd.bdate_range("2023-06-01", periods=4)
    c = pd.DataFrame({ETF: [100.0] * 4}, index=idx); o = c.copy(); o.iloc[1] = 112.0
    p = ExecPanels(close=c, open=o, volume=c * 1e6, amount=c * 1e8)
    r = run_weight_schedule(p, {idx[0]: {ETF: 0.5}}, initial_cash=100_000, record_fills=True,
                            config=ExecConfig(price_tick="auto", no_limit_codes=frozenset({ETF}), **ZERO_COST))
    assert len(r["fills"]) == 1


def test_stock_unchanged_no_derived_limit():
    assert derived_limit_pct(STK, "2023-06-01") is None
    assert len(_limit_case(STK, "2023-06-01", 0.25)["fills"]) == 1   # stocks: limits only from panels


def test_cb_redemption_payout_to_cash():
    p = _panels([CB, STK], n=8)
    idx = p.close.index
    tp = pd.DataFrame(np.nan, index=idx, columns=p.close.columns)
    tp.iloc[5, 0] = 101.5
    c = p.close.copy(); c.iloc[5:, 0] = np.nan
    p = ExecPanels(close=c, open=p.open.where(c.notna()), volume=p.volume, amount=p.amount, terminal_price=tp)
    r = run_weight_schedule(p, {idx[0]: {CB: 0.4, STK: 0.4}}, initial_cash=100_000,
                            config=ExecConfig(price_tick="auto", **ZERO_COST))
    ev = [e for e in r["events"] if e["reason"] == "terminal_payout"]
    assert len(ev) == 1 and ev[0]["price"] == 101.5
    assert CB not in r["final_shares"] and np.isfinite(r["nav"]).all()
    assert r["terminal_payout_cash"] == pytest.approx(ev[0]["shares"] * 101.5)


def test_engines_reconcile_mixed():
    codes = [CB, CB2, ETF, STAR_ETF, STK]
    p = _panels(codes, n=30)
    d = p.close.index
    sch = {d[0]: {CB: 0.2, CB2: 0.2, ETF: 0.2, STAR_ETF: 0.15, STK: 0.2},
           d[10]: {CB: 0.3, ETF: 0.3, STK: 0.3}, d[20]: {CB2: 0.4, STAR_ETF: 0.4}}
    rep = reconcile_zero_cost(p, sch, initial_cash=1_000_000)
    for name in ("ledger", "fastsim"):
        assert rep["diffs"][name]["max_abs_rel_diff"] < 1e-9, (name, rep["diffs"][name]["max_abs_rel_diff"])


def test_platform_fastsim_reconcile_with_redemption():
    codes = [CB, ETF, STK]
    p = _panels(codes, n=20)
    idx = p.close.index
    tp = pd.DataFrame(np.nan, index=idx, columns=p.close.columns); tp.iloc[12, 0] = 100.0
    c = p.close.copy(); c.iloc[12:, 0] = np.nan
    p = ExecPanels(close=c, open=p.open.where(c.notna()), volume=p.volume, amount=p.amount, terminal_price=tp)
    sch = {idx[0]: {CB: 0.3, ETF: 0.3, STK: 0.3}, idx[15]: {ETF: 0.5, STK: 0.4}}
    rep = reconcile_zero_cost(p, sch, initial_cash=1_000_000, engines=("platform", "fastsim"))
    assert rep["diffs"]["fastsim"]["max_abs_rel_diff"] < 1e-9
