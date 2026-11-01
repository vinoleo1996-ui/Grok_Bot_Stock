"""S2 engine fixes (2026-10-11): per-code tick, fund stamp exemption/lots,
fast-sim board-lot parity (STAR 200/1), sh.510300 OHLCV after 2026-06-30."""
import numpy as np
import pandas as pd
import pytest

from quantlab.platform.execution import (ExecConfig, ExecPanels, ZERO_COST, is_exchange_fund, lot_rule_for,
                                         reconcile_zero_cost, run_weight_schedule, stamp_exempt, tick_for_code)


def test_tick_for_code():
    for c in ("sh.510300", "sz.159915", "sz.161005", "sh.588000", "sh.511880", "510300.SH"):
        assert tick_for_code(c) == 0.001 and is_exchange_fund(c) and stamp_exempt(c)
        assert lot_rule_for(c).minimum == 100 and lot_rule_for(c).step == 100
    for c in ("sh.600000", "sz.000001", "sz.300750", "sh.688001", "bj.430047", "sz.002559"):
        assert tick_for_code(c) == 0.01 and not is_exchange_fund(c)


def test_strategy_v1_auto_tick():
    assert ExecConfig.strategy_v1().price_tick == "auto"


def _panels(codes, opens, closes):
    idx = pd.bdate_range("2026-09-01", periods=len(opens))
    o = pd.DataFrame(opens, index=idx, columns=codes)
    c = pd.DataFrame(closes, index=idx, columns=codes)
    v = pd.DataFrame(1e9, index=idx, columns=codes)
    return ExecPanels(close=c, open=o, high=c, low=c, volume=v, amount=v * c), idx


def test_etf_fill_keeps_0001_tick_and_no_stamp():
    p, idx = _panels(["sh.510300", "sh.600000"], [[4.417, 10.0]] * 3, [[4.417, 10.0]] * 3)
    cfg = ExecConfig.strategy_v1(impact_k=0.0, no_limit_codes=frozenset({"sh.510300"}), participation_cap=None)
    sched = {idx[0]: {"sh.510300": 0.5, "sh.600000": 0.4}, idx[1]: {}}
    r = run_weight_schedule(p, sched, initial_cash=1e6, config=cfg, record_fills=True)
    f = pd.DataFrame(r["fills"])
    etf = f[f.code == "sh.510300"]
    assert np.allclose(etf.price, 4.417)  # not 4.42
    assert (etf.stamp == 0).all()
    stk = f[(f.code == "sh.600000") & (f.side < 0)]
    assert (stk.stamp > 0).all()


def test_fastsim_matches_platform_and_ledger_with_star_and_etf():
    codes = ["sh.510300", "sh.688063", "sh.688357", "sz.002559", "sh.600969"]
    rng = np.random.default_rng(0)
    n = 6
    base = np.array([4.417, 37.21, 52.3, 11.07, 8.93])
    px = base * np.cumprod(1 + rng.normal(0, 0.02, (n, len(codes))), axis=0)
    px[:, 0] = np.round(px[:, 0], 3); px[:, 1:] = np.round(px[:, 1:], 2)
    p, idx = _panels(codes, px, px * 1.003)
    sched = {idx[0]: dict(zip(codes, [0.3, 0.004, 0.003, 0.3, 0.3])),
             idx[1]: dict(zip(codes, [0.3, 0.0041, 0.0045, 0.3, 0.3])),
             idx[3]: dict(zip(codes, [0.25, 0.01, 0.002, 0.35, 0.3]))}
    rec = reconcile_zero_cost(p, sched, initial_cash=5e6)
    navs = rec["navs"]
    for col in ("ledger", "fastsim"):
        rel = ((navs[col] - navs["platform"]) / navs["platform"]).abs().max()
        assert rel < 1e-12, (col, rel)
    assert ((navs["fastsim_delta_rounding"] - navs["platform_delta_rounding"]).abs().max()) < 1e-6


def test_fastsim_fund_stamp_exempt():
    from quantlab.smallcap.sim import Costs, _fee
    d = pd.Timestamp("2026-09-01")
    c = Costs()
    assert _fee(1e5, -1, d, c, exempt=True) == pytest.approx(25.0)
    assert _fee(1e5, -1, d, c, exempt=False) == pytest.approx(75.0)


def test_510300_panel_extends_past_d0_cut():
    from quantlab.data.v2_readers import default_v2_roots
    from quantlab.platform.execution import load_execution_panels
    if not default_v2_roots().etf_panel_path.is_file():
        pytest.skip("etf panel missing")
    p, d = load_execution_panels(["sh.510300"], "2026-09-28", "2026-10-09")
    s = p.close["sh.510300"].dropna()
    assert s.index.max() >= pd.Timestamp("2026-10-09")
    o = p.open["sh.510300"].loc["2026-10-09"]
    assert abs(o - 4.369) < 1e-4 and abs(s.loc["2026-10-09"] - 4.385) < 1e-4
    ratio = (p.amount / (p.volume * p.close))["sh.510300"].dropna()
    assert ratio.between(0.95, 1.05).all()  # volume in shares, amount CNY
