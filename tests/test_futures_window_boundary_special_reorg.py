"""Regression: (1) futures expiring AFTER the data window must not be rolled/liquidated in the
last roll_days sessions; (2) corporate-action events contradicting adj_factor by >1% are
'special_reorg' -> factor used by platform + fast sim, excluded from the ledger."""
import numpy as np, pandas as pd, pytest
from quantlab.platform.execution import (ExecConfig, ExecPanels, ZERO_COST, run_weight_schedule,
                                         corporate_action_arrays, reconcile_zero_cost, _ledger_actions,
                                         EVENT_FACTOR_MISMATCH)
from quantlab.platform.futures import FuturesLeg, FuturesPanels, FuturesConfig, round_to_tick, MULTIPLIER, ALL_MULTIPLIER

D = pd.bdate_range("2024-11-01", "2025-01-31")
ZC = dict(fill="next_open", enforce_limits=False, price_tick="auto", **ZERO_COST)


def _etf():
    c = pd.DataFrame({"sh.510300": 4.0}, index=D)
    return ExecPanels(close=c, open=c.copy(), volume=c * 0 + 1e9)


def _fp(code, base, step, tick=0.2):
    S = pd.DataFrame({code: [round(round((base + step * k) / tick) * tick, 4) for k in range(len(D))]}, index=D)
    return FuturesPanels(settle=S, open=S.shift(1).fillna(S), close=S.copy())


@pytest.mark.parametrize("mode", ["roll", "deliver"])
@pytest.mark.parametrize("code,base,step,tick", [("IF2503", 3900.0, 2.0, 0.2), ("IC2612", 5600.0, 3.0, 0.2),
                                                  ("T2503", 105.0, 0.01, 0.005)])
def test_expiry_after_window_no_forced_liquidation(mode, code, base, step, tick):
    fp = _fp(code, base, step, tick)
    leg = FuturesLeg(fp, FuturesConfig(roll_mode=mode, roll_days=5, fee_override=(0, 0, 0),
                                       bond_fee_override=(0, 0, 0)))
    r = run_weight_schedule(_etf(), {D[2]: {code.rstrip("0123456789"): 1.0}}, initial_cash=5_000_000,
                            config=ExecConfig(**ZC), futures=leg)
    fills = r["fut_fills"]
    assert len(fills) == 1 and fills[0]["why"] == "order", fills   # one entry, no roll_out / liquidation
    lots, px = fills[0]["lots"], fills[0]["price"]
    S = fp.settle[code]
    m = ALL_MULTIPLIER[code.rstrip("0123456789")]
    # hand calc: zero cost, cash idle -> NAV = cash + VM = initial + lots*(S_end - entry)*mult
    assert r["nav"].iloc[-1] == pytest.approx(5_000_000 + lots * (S.iloc[-1] - px) * m, abs=1e-6)


@pytest.mark.parametrize("mode", ["roll", "deliver"])
@pytest.mark.parametrize("code,base,step,tick", [("IC2612", 5600.0, 3.0, 0.2), ("T2503", 105.0, 0.01, 0.005)])
def test_signal_in_last_sessions_keeps_unexpired_contract(mode, code, base, step, tick):
    fp = _fp(code, base, step, tick)
    leg = FuturesLeg(fp, FuturesConfig(roll_mode=mode, roll_days=5, fee_override=(0, 0, 0), bond_fee_override=(0, 0, 0)))
    root = code.rstrip("0123456789")
    sched = {D[2]: {root: 1.0}, D[-3]: {root: 1.0}}   # re-signal inside the last 5 sessions
    r = run_weight_schedule(_etf(), sched, initial_cash=5_000_000, config=ExecConfig(**ZC), futures=leg)
    assert not any(f["lots"] < 0 for f in r["fut_fills"]), r["fut_fills"]
    assert not any(e.get("reason") == "fut_no_contract" for e in r.get("events", []))


# ---------------------------------------------------------------- special_reorg
DC = pd.bdate_range("2025-03-03", periods=8)
CFG = ExecConfig(fill="close", enforce_limits=False, participation_cap=None, **ZERO_COST)


def _p(close, cash=None, ratio=None, factor=None, code="sz.000525"):
    c = pd.DataFrame({code: close}, index=DC)
    z = lambda v: None if v is None else pd.DataFrame({code: v}, index=DC)
    return ExecPanels(close=c, open=c.copy(), cash_div=z(cash), share_ratio=z(ratio), adj_factor=z(factor))


def test_threshold_is_one_percent():
    assert EVENT_FACTOR_MISMATCH == 0.01


@pytest.mark.parametrize("code,ratio,cash,fac_ratio,special", [
    ("sz.000525", 0.40, 0.0, 1.10, True),    # reorg-style: declared 4-for-10 transfer, factor only +10%
    ("sz.000656", 0.0, 0.50, 1.035, True),   # cash event implies 1.0526x vs factor 1.035 (1.7% off)
    ("sz.000001", 0.0, 0.50, 1.0526315789 * 1.005, False),  # 0.5% off -> ordinary event
])
def test_special_reorg_uses_factor_and_is_labelled(code, ratio, cash, fac_ratio, special):
    close = [10, 10, 10, 10 / fac_ratio] + [10 / fac_ratio] * 4
    fac = [1, 1, 1] + [fac_ratio] * 5
    sr = [0, 0, 0, ratio, 0, 0, 0, 0]; cd = [0, 0, 0, cash, 0, 0, 0, 0]
    p = _p(close, cash=cd, ratio=sr, factor=fac, code=code)
    flags = []
    CD, SR, FR = corporate_action_arrays(p.aligned(), flags=flags)
    assert bool(flags) == special
    if special:
        assert flags[0]["label"] == "special_reorg"
        assert CD[3, 0] == 0 and SR[3, 0] == 0 and FR[3, 0] == pytest.approx(fac_ratio)
        assert _ledger_actions(p.aligned()).empty            # excluded from ledger action list
        r = run_weight_schedule(p, {DC[0]: {code: 1.0}}, initial_cash=100_000, config=CFG)
        assert r["nav"].iloc[-1] == pytest.approx(100_000, rel=1e-6)   # factor = total-return neutral
        rec = reconcile_zero_cost(p, {DC[0]: {code: 1.0}}, initial_cash=100_000)
        assert (rec["navs"]["fastsim"] / rec["navs"]["platform"] - 1).abs().max() < 1e-9
    else:
        assert SR[3, 0] == ratio and CD[3, 0] == cash
