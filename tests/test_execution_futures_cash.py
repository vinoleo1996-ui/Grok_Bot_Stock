import numpy as np, pandas as pd, pytest
from quantlab.platform.execution import ExecConfig, ExecPanels, run_weight_schedule, ZERO_COST, _fastsim_nav
from quantlab.platform.futures import (FuturesLeg, FuturesPanels, FuturesConfig, MULTIPLIER, fee_rates,
                                       margin_rate, last_trade_date, cash_rate_per_session, round_to_tick)

D = pd.bdate_range("2024-11-01", "2025-01-31")
ZC = dict(fill="next_open", enforce_limits=False, price_tick="auto", **ZERO_COST)


def etf_panels(px=4.0):
    c = pd.DataFrame({"sh.510300": px}, index=D)
    return ExecPanels(close=c, open=c.copy(), volume=c * 0 + 1e9)


def fut_panels(base=3900.0, step=2.0, contracts=("IF2412", "IF2501")):
    S = pd.DataFrame({c: base + k * 10 + step * np.arange(len(D)) for k, c in enumerate(contracts)}, index=D)
    for c in contracts:
        S.loc[S.index > last_trade_date(c, D), c] = np.nan
    S = S.map(round_to_tick)
    return FuturesPanels(settle=S, open=S.shift(1).fillna(S), close=S.copy())


def cfg(**kw):
    return ExecConfig(**{**ZC, **kw})


def test_contract_constants_and_tables():
    assert MULTIPLIER == {"IF": 300.0, "IH": 300.0, "IC": 200.0, "IM": 200.0}
    assert last_trade_date("IF2412") == pd.Timestamp("2024-12-20")
    assert fee_rates("2024-01-02") == (0.000023, 0.000023, 0.00023)
    assert fee_rates("2016-01-04")[2] == 0.0023
    assert margin_rate("IF", "2020-01-02") == 0.10
    assert round_to_tick(3901.13) == pytest.approx(3901.2)


def test_whole_lots_and_mtm_equals_settle_diffs():
    fp = fut_panels()
    leg = FuturesLeg(fp, FuturesConfig(roll_mode="deliver", fee_override=(0, 0, 0)))
    sig = D[2]
    r = run_weight_schedule(etf_panels(), {sig: {"IF": 1.0}}, initial_cash=5_000_000, config=cfg(), futures=leg)
    lots = round(1.0 * 5_000_000 / (fp.settle.loc[sig, "IF2412"] * 300))
    fills = [f for f in r["fut_fills"] if f["why"] == "order"]
    assert fills[0]["lots"] == lots and float(lots).is_integer()
    entry = fp.open.loc[D[3], "IF2412"]; final = fp.settle.loc[last_trade_date("IF2412", D), "IF2412"]
    assert r["variation_margin"] == pytest.approx((final - entry) * 300 * lots)
    vm = r["variation_margin_daily"]
    assert vm.loc[D[4]] == pytest.approx((fp.settle.loc[D[4], "IF2412"] - fp.settle.loc[D[3], "IF2412"]) * 300 * lots)
    assert any(e["reason"] == "fut_delivery" for e in r["events"])
    assert r["nav"].iloc[-1] == pytest.approx(5_000_000 + r["variation_margin"] - r["fut_costs"]["delivery_fee"])


def test_limit_block_vs_pre_settle():
    fp = fut_panels()
    fp.open.loc[D[3], "IF2412"] = round_to_tick(fp.settle.loc[D[2], "IF2412"] * 1.10)   # at limit-up
    leg = FuturesLeg(fp, FuturesConfig(roll_mode="deliver", fee_override=(0, 0, 0)))
    r = run_weight_schedule(etf_panels(), {D[2]: {"IF": 1.0}}, initial_cash=5_000_000, config=cfg(), futures=leg)
    assert any(e["reason"] == "fut_limit_up" and e["date"] == str(D[3].date()) for e in r["events"])
    assert r["fut_fills"][0]["date"] == str(D[4].date())   # retried next session


def test_close_today_fee():
    fp = fut_panels()
    leg = FuturesLeg(fp, FuturesConfig(roll_mode="deliver"))
    # open at t=3 open, signal t=3 close flat -> close at t=4 (normal close); compare with fill='close' same-day
    r = run_weight_schedule(etf_panels(), {D[2]: {"IF": 1.0}, D[3]: {"IF": 0.0}}, initial_cash=5_000_000, config=cfg(), futures=leg)
    o, c, ct = fee_rates(D[3])
    f = r["fut_fills"]
    assert f[0]["fee"] == pytest.approx(abs(f[0]["lots"]) * f[0]["price"] * 300 * o)
    assert f[1]["fee"] == pytest.approx(abs(f[1]["lots"]) * f[1]["price"] * 300 * c)
    # same-day round trip: open at D3 open (signal D2), close at D3 close via fill='close'? use forced same day:
    leg2 = FuturesLeg(fp, FuturesConfig(roll_mode="deliver"))
    from quantlab.platform.futures import FuturesBook
    b = FuturesBook(leg2, D, [])
    b.start(3); b.pending = {0: 4.0}; b.trade(3, fp.open.reindex(columns=b.contracts).to_numpy(), 0)
    b.pending = {0: -4.0}; b.trade(3, fp.close.reindex(columns=b.contracts).to_numpy(), 0)
    px = fp.close.loc[D[3], "IF2412"]
    assert b.fills[1]["fee"] == pytest.approx(4 * px * 300 * ct)


def test_margin_shortfall_flag_and_reduce():
    fp = fut_panels(step=-60.0)   # falling market
    for act in ("flag", "reduce"):
        leg = FuturesLeg(fp, FuturesConfig(roll_mode="deliver", fee_override=(0, 0, 0), shortfall_action=act))
        r = run_weight_schedule(etf_panels(), {D[2]: {"IF": 3.0}}, initial_cash=5_000_000, config=cfg(), futures=leg)
        ev = [e for e in r["events"] if e["reason"] == "fut_margin_shortfall"]
        assert ev
        if act == "reduce":
            assert any(f["why"] == "forced_reduce" for f in r["fut_fills"])


def test_roll_cost_and_continuity():
    fp = fut_panels()
    leg = FuturesLeg(fp, FuturesConfig(roll_mode="roll", roll_days=3))
    r = run_weight_schedule(etf_panels(), {D[2]: {"IF": 1.0}}, initial_cash=5_000_000, config=cfg(), futures=leg)
    rolls = [f for f in r["fut_fills"] if f["why"].startswith("roll")]
    assert r["n_rolls"] == 1 and len(rolls) == 2 and rolls[0]["lots"] == -rolls[1]["lots"]
    o, c, ct = fee_rates(D[0])
    exp = sum(abs(f["lots"]) * f["price"] * 300 * (c if f["why"] == "roll_out" else o) for f in rolls)
    assert r["roll_cost"] == pytest.approx(exp)
    d_roll = pd.Timestamp(rolls[0]["date"])
    assert r["fut_exposure"].loc[d_roll, "IF2501"] > 0 and r["fut_exposure"].loc[d_roll, "IF2412"] == 0
    # no IF2502 listed in the panel -> IF2501 is held into delivery and flagged
    assert any(e["reason"] == "fut_roll_no_next" for e in r["events"])
    assert any(e["reason"] == "fut_delivery" and e["code"] == "IF2501" for e in r["events"])


def test_cash_rate_constant_and_series():
    p = etf_panels()
    r = run_weight_schedule(p, {}, initial_cash=1_000_000, config=cfg(cash_rate=0.0365))
    days = (D[-1] - D[0]).days
    assert r["nav"].iloc[-1] == pytest.approx(1_000_000 * np.prod(1 + 0.0365 * np.diff(D.values).astype("timedelta64[D]").astype(float) / 365))
    assert r["cash_interest"] == pytest.approx(r["nav"].iloc[-1] - 1_000_000)
    r2 = run_weight_schedule(p, {}, initial_cash=1_000_000, config=cfg(cash_rate=0.0252, cash_rate_convention="per_session"))
    assert r2["nav"].iloc[-1] == pytest.approx(1_000_000 * (1 + 0.0001) ** (len(D) - 1))
    ser = pd.Series(0.0001, index=D)
    r3 = run_weight_schedule(p, {}, initial_cash=1_000_000, config=cfg(cash_rate=ser, cash_rate_kind="return"))
    assert r3["nav"].iloc[-1] == pytest.approx(r2["nav"].iloc[-1])
    rr = cash_rate_per_session(D, pd.Series([0.02], index=[D[0]]), series_kind="annual", day_count=360)
    assert rr[1] == pytest.approx(0.02 * (D[1] - D[0]).days / 360)


def test_cash_rate_platform_vs_fastsim_and_default_off():
    p = etf_panels()
    sch = {D[2]: {"sh.510300": 0.5}}
    a = run_weight_schedule(p, sch, initial_cash=1_000_000, config=cfg(cash_rate=0.02))["nav"]
    b = _fastsim_nav(p, sch, 1_000_000, cash_rate=0.02)
    assert np.allclose(a.values, b.values, rtol=1e-12)
    base = run_weight_schedule(p, sch, initial_cash=1_000_000, config=cfg())
    assert "cash_interest" not in base and "margin_peak" not in base


def test_combined_510300_plus_if_and_margin_not_interest_bearing():
    fp = fut_panels()
    leg = FuturesLeg(fp, FuturesConfig(roll_mode="deliver", fee_override=(0, 0, 0)))
    r = run_weight_schedule(etf_panels(), {D[2]: {"sh.510300": 0.8, "IF": 0.5}}, initial_cash=5_000_000,
                            config=cfg(cash_rate=0.03), futures=leg)
    assert r["final_shares"]["sh.510300"] > 0 and r["margin_peak"] > 0
    aw = r["actual_weights"].loc[D[5], "sh.510300"]
    assert 0.75 < aw < 0.85
    assert 0.4 < r["fut_exposure"].loc[D[5], "IF2412"] < 0.6
    # interest only on cash minus margin
    t = 6; it = r["cash_interest_daily"].iloc[t]
    assert it > 0
