"""Platform execution/cost options on tiny synthetic panels (research-only)."""
import numpy as np
import pandas as pd
import pytest

from quantlab.platform.execution import (
    ExecConfig, ExecPanels, ZERO_COST, capacity_curve, cost_ladder, forward_return_components,
    infer_volume_scale, lot_rule_for, normalize_volume_to_shares, reconcile_zero_cost,
    round_order_quantity, run_weight_schedule, split_returns, sqrt_impact_cost, vwap_panel,
)

D = pd.bdate_range("2026-01-05", periods=8)
NOCOST = ExecConfig(fill="next_open", enforce_limits=False, **ZERO_COST)


def panels(n=8, close=None, open_=None, vol=1e6, codes=("sh.600001", "sz.000002")):
    rng = np.random.default_rng(0)
    if close is None:
        close = pd.DataFrame(10 * np.cumprod(1 + rng.normal(0, .02, (n, len(codes))), axis=0), index=D[:n], columns=list(codes))
    if open_ is None:
        open_ = close.shift(1).fillna(close.iloc[0]) * (1 + rng.normal(0, .005, close.shape))
    close, open_ = close.round(2), open_.round(2)   # exchange tick (Ledger rounds fills to 0.01)
    v = pd.DataFrame(vol, index=close.index, columns=close.columns)
    return ExecPanels(close=close, open=open_, high=pd.concat([close, open_]).groupby(level=0).max() * 1.01,
                      low=pd.concat([close, open_]).groupby(level=0).min() * .99, volume=v, amount=v * close)


def test_lot_rounding_main_star_bj():
    assert lot_rule_for("sh.600000").minimum == 100 and lot_rule_for("sh.600000").step == 100
    assert round_order_quantity("sh.600000", 1999, 1) == 1900
    assert round_order_quantity("sh.688001", 199, 1) == 0
    assert round_order_quantity("sh.688001", 237.9, 1) == 237
    assert round_order_quantity("bj.430017", 157, 1) == 157
    assert round_order_quantity("sh.600000", 150, -1, holding=1050) == 100
    assert round_order_quantity("sh.600000", 50, -1, holding=50) == 50   # odd residual closes position


def test_participation_cap_10pct_carry_and_drop():
    p = panels(vol=1000.0)  # cap 100 shares/day
    sched = {D[0]: {"sh.600001": 0.5}}
    r = run_weight_schedule(p, sched, initial_cash=1e6, config=ExecConfig(fill="next_open", participation_cap=0.10, enforce_limits=False, **ZERO_COST))
    assert r["final_shares"]["sh.600001"] == 100 * 7   # carried 7 sessions
    r2 = run_weight_schedule(p, sched, initial_cash=1e6, config=ExecConfig(fill="next_open", participation_cap=0.10, unfilled="drop", enforce_limits=False, **ZERO_COST))
    assert r2["final_shares"]["sh.600001"] == 100
    assert r2["fill_ratio"] < 0.01


def test_limit_up_blocks_buy_limit_down_blocks_sell_halt_blocks_both():
    p = panels()
    c = "sh.600001"
    lu = pd.DataFrame(np.inf, index=p.close.index, columns=p.close.columns)
    ld = pd.DataFrame(-np.inf, index=p.close.index, columns=p.close.columns)
    lu.loc[D[1], c] = p.open.loc[D[1], c]           # open at limit-up on T+1
    q = ExecPanels(p.close, p.open, p.high, p.low, p.volume, p.amount, lu, ld)
    cfg = ExecConfig(fill="next_open", **ZERO_COST)
    r = run_weight_schedule(q, {D[0]: {c: .5}}, initial_cash=1e6, config=cfg, record_fills=True)
    assert any(e["reason"] == "limit_up" for e in r["events"])
    assert r["fills"][0]["date"] == str(D[2].date())     # carried, filled next day
    ld.loc[D[4], c] = p.open.loc[D[4], c]
    q = ExecPanels(p.close, p.open, p.high, p.low, p.volume, p.amount, lu.replace(p.open.loc[D[1], c], np.inf), ld)
    r = run_weight_schedule(q, {D[0]: {c: .5}, D[3]: {}}, initial_cash=1e6, config=cfg, record_fills=True)
    assert any(e["reason"] == "limit_down" for e in r["events"])
    assert [f["date"] for f in r["fills"] if f["side"] < 0] == [str(D[5].date())]
    # halt: suspended day blocks buy, valuation carries last close then realizes move
    close = p.close.copy(); close.loc[D[1]:D[2], c] = np.nan
    h = ExecPanels(close, p.open, p.high, p.low, p.volume, p.amount)
    r = run_weight_schedule(h, {D[0]: {c: .5}}, initial_cash=1e6, config=cfg, record_fills=True)
    assert r["fills"][0]["date"] == str(D[3].date())
    assert sum(e["reason"] == "suspended" for e in r["events"]) == 2


def test_halted_holding_marked_to_close_not_zeroed():
    p = panels(); c = "sh.600001"
    r = run_weight_schedule(p, {D[0]: {c: .5}}, initial_cash=1e6, config=NOCOST)
    sh = r["final_shares"][c]
    close = p.close.copy(); close.loc[D[4]:D[5], c] = np.nan
    r2 = run_weight_schedule(ExecPanels(close, p.open, volume=p.volume, amount=p.amount), {D[0]: {c: .5}}, initial_cash=1e6, config=NOCOST)
    assert r2["final_shares"][c] == sh
    assert r2["nav"].iloc[-1] == pytest.approx(r["nav"].iloc[-1])
    assert r2["nav"].loc[D[5]] == pytest.approx(r2["nav"].loc[D[3]])


def test_sqrt_impact_monotonic_and_units():
    adv, sig = 1e8, 0.02
    vals = [1e5, 1e6, 4e6, 1.6e7]
    costs = sqrt_impact_cost(vals, adv, sig, k=1.0)
    assert np.all(np.diff(costs) > 0)
    # 1e6 CNY on 1e8 ADV, sigma 2%: rate = 0.02*sqrt(0.01)=0.002 -> 2000 CNY
    assert costs[1] == pytest.approx(2000.0)
    # scale invariance: shares vs lots does not matter, only CNY values
    assert sqrt_impact_cost(4e6, 4e8, sig) == pytest.approx(sqrt_impact_cost(1e6, 1e8, sig) * 4)
    assert sqrt_impact_cost(1e6, np.nan, sig) == 0.0
    p = panels(n=8)
    base = ExecConfig(fill="next_open", enforce_limits=False, sigma_window=3, adv_window=3, **{**ZERO_COST, "impact_k": 1.0})
    sched = {D[4]: {"sh.600001": .5}}
    c1 = run_weight_schedule(p, sched, initial_cash=1e6, config=base)["costs"]["impact"]
    c2 = run_weight_schedule(p, sched, initial_cash=4e6, config=base)["costs"]["impact"]
    assert c1 > 0 and c2 / c1 == pytest.approx(8.0, rel=0.02)   # 4x size -> 4^1.5


def test_t1_open_and_vwap_fill_prices():
    p = panels(); c = "sh.600001"
    r = run_weight_schedule(p, {D[0]: {c: .5}}, initial_cash=1e6, config=NOCOST, record_fills=True)
    assert r["fills"][0]["price"] == pytest.approx(p.open.loc[D[1], c])
    amt = p.amount.copy(); amt.loc[D[1], c] = p.volume.loc[D[1], c] * 10.123
    q = ExecPanels(p.close, p.open, p.high.clip(lower=11), p.low.clip(upper=9), p.volume, amt)
    cfg = ExecConfig(fill="next_vwap", enforce_limits=False, **ZERO_COST)
    r = run_weight_schedule(q, {D[0]: {c: .5}}, initial_cash=1e6, config=cfg, record_fills=True)
    assert r["fills"][0]["price"] == pytest.approx(10.123)
    r = run_weight_schedule(p, {D[0]: {c: .5}}, initial_cash=1e6, config=ExecConfig(fill="close", enforce_limits=False, **ZERO_COST), record_fills=True)
    assert r["fills"][0]["date"] == str(D[0].date()) and r["fills"][0]["price"] == pytest.approx(p.close.loc[D[0], c])


def test_vwap_fallback_and_volume_units():
    close = pd.DataFrame({"a": [10., 10.]}); vol_lots = pd.DataFrame({"a": [1000., 1000.]})
    amt = pd.DataFrame({"a": [1_000_000., np.nan]})
    assert infer_volume_scale(amt, vol_lots, close).iloc[0, 0] == 100
    sh = normalize_volume_to_shares(vol_lots, amt, close)
    assert list(sh["a"]) == [100000., 100000.]   # NaN amount -> ffilled scale
    o = pd.DataFrame({"a": [9., 9.]}); hi = pd.DataFrame({"a": [11., 11.]}); lo = pd.DataFrame({"a": [8., 8.]})
    v, fb = vwap_panel(amt, sh, close, o, hi, lo)
    assert v.iloc[0, 0] == pytest.approx(10.0) and v.iloc[1, 0] == pytest.approx(9.5) and bool(fb.iloc[1, 0])
    v2, fb2 = vwap_panel(amt, vol_lots, close, o, hi, lo)   # unit mismatch -> out of range -> fallback
    assert bool(fb2.iloc[0, 0])


def test_overnight_intraday_compound_to_close_to_close():
    p = panels()
    on, it = split_returns(p.open, p.close)
    cc = p.close.pct_change()
    np.testing.assert_allclose(((1 + on) * (1 + it) - 1).iloc[1:], cc.iloc[1:], rtol=1e-12)
    comp = forward_return_components(p.open, p.close, D[1], 3)
    for k, v in comp["cc"].items():
        assert (1 + comp["overnight"][k]) * (1 + comp["intraday"][k]) - 1 == pytest.approx(v, rel=1e-12)
    # engine: nav_open splits each day's book return
    r = run_weight_schedule(p, {D[0]: {"sh.600001": .5, "sz.000002": .4}}, initial_cash=1e6, config=NOCOST)
    nav, navo = r["nav"], r["nav_open"]
    ret = nav.pct_change().iloc[2:]
    np.testing.assert_allclose(((navo / nav.shift(1)) * (nav / navo) - 1).iloc[2:], ret, rtol=1e-12)


def test_zero_cost_reconciliation_identical():
    p = panels(n=8)
    sched = {D[0]: {"sh.600001": .45, "sz.000002": .45}, D[3]: {"sh.600001": .2, "sz.000002": .7}, D[6]: {}}
    rep = reconcile_zero_cost(p, sched, initial_cash=1e6)
    for name in ("ledger", "fastsim", "fastsim_vs_platform_delta_rounding"):
        d = rep["diffs"][name]
        assert d["first_divergence"] is None, (name, d)
        assert d["max_abs_rel_diff"] <= 1e-9
    # legacy delta rounding still reproducible and still differs from target rounding
    assert rep["diffs"]["fastsim_delta_rounding"]["first_divergence"] == str(D[4].date())
    paper = rep["navs"]["platform"] / 1e6
    paper.iloc[5] *= 1.01
    rep2 = reconcile_zero_cost(p, sched, initial_cash=1e6, paper_nav=paper)
    assert rep2["diffs"]["paper"]["first_divergence"] == str(D[5].date())


def test_cost_ladder_and_capacity_curve_synthetic():
    p = panels(n=8, vol=50_000.0)
    sched = {D[2]: {"sh.600001": .45, "sz.000002": .45}, D[5]: {"sh.600001": .9}}
    lad = cost_ladder(p, sched, initial_cash=1e6, base=ExecConfig(fill="next_open", enforce_limits=False, lots=False, sigma_window=2, adv_window=2, **ZERO_COST))
    row = lad.set_index("item")
    assert row.loc["zero_cost", "delta_vs_zero"] == 0
    for item in ("commission", "stamp", "slippage_10bp", "sqrt_impact_k1"):
        assert row.loc[item, "cost_cny"] > 0
    cap = capacity_curve(p, sched, config=ExecConfig(fill="next_open", impact_k=1.0, participation_cap=0.10, sigma_window=2, adv_window=2, enforce_limits=False))
    assert list(cap["capital"]) == [5e5, 2e6, 1e7]
    assert cap["fill_ratio"].is_monotonic_decreasing
    assert (cap["fill_ratio"] <= 1 + 1e-12).all()


def test_zero_cost_reconciliation_off_tick_opens():
    p = panels(n=8)
    p.open = p.open * 1.00337          # off-tick opens: all engines must round fills to 0.01
    sched = {D[0]: {"sh.600001": .45, "sz.000002": .45}, D[3]: {"sh.600001": .2, "sz.000002": .7}, D[6]: {}}
    rep = reconcile_zero_cost(p, sched, initial_cash=1e6)
    for name in ("ledger", "fastsim"):
        assert rep["diffs"][name]["first_divergence"] is None
        assert rep["diffs"][name]["max_abs_rel_diff"] <= 1e-9


def test_strategy_v1_preset_and_defaults_backward_compatible():
    from quantlab.platform.execution import impact_sensitivity_configs, run_impact_sensitivity
    bare = ExecConfig()
    assert bare.price_tick is None and bare.impact_k == 0.0 and bare.participation_cap is None
    c = ExecConfig.strategy_v1()
    assert (c.fill, c.price_tick, c.impact_k, c.participation_cap, c.unfilled, c.lots, c.enforce_limits,
            c.order_rounding) == ("next_open", "auto", 1.0, 0.10, "carry", True, True, "target")
    assert ExecConfig.strategy_v1(impact_k=2.0).impact_k == 2.0
    cfgs = impact_sensitivity_configs()
    assert sorted(cfgs) == [0.5, 1.0, 2.0] and all(v.price_tick == "auto" for v in cfgs.values())
    with pytest.raises(ValueError):
        ExecConfig(order_rounding="bad")
    p = panels(n=8, vol=50_000.0)
    sched = {D[2]: {"sh.600001": .45, "sz.000002": .45}}
    base = ExecConfig.strategy_v1(sigma_window=2, adv_window=2, enforce_limits=False)
    t = run_impact_sensitivity(p, sched, initial_cash=1e6, base=base)
    assert list(t["k"]) == [0.5, 1.0, 2.0] and t["impact_cny"].is_monotonic_increasing


def test_tick_rounding_fill_price():
    p = panels(n=4)
    p.open = p.open + 0.003
    r = run_weight_schedule(p, {D[0]: {"sh.600001": .5}}, initial_cash=1e6,
                            config=ExecConfig(fill="next_open", enforce_limits=False, price_tick=0.01, **ZERO_COST),
                            record_fills=True)
    px = r["fills"][0]["price"]
    assert abs(px * 100 - round(px * 100)) < 1e-9 and px != r["fills"][0]["ref_price"]


def test_target_and_actual_weights_output():
    p = panels(n=6)
    sched = {D[0]: {"sh.600001": .5, "sz.000002": .3}, D[3]: {"sh.600001": .9}}
    r = run_weight_schedule(p, sched, initial_cash=1e6, config=NOCOST)
    tw, aw = r["target_weights"], r["actual_weights"]
    assert tw.shape == aw.shape == (6, 2) and tw.dtypes.eq(np.float32).all() and aw.dtypes.eq(np.float32).all()
    assert tw.loc[D[0], "sh.600001"] == pytest.approx(.5) and tw.loc[D[2], "sz.000002"] == pytest.approx(.3)
    assert tw.loc[D[4], "sz.000002"] == 0 and tw.loc[D[4], "sh.600001"] == pytest.approx(.9)
    assert aw.loc[D[0]].sum() == 0                     # next_open: nothing filled on signal day
    assert aw.loc[D[1], "sh.600001"] == pytest.approx(.5, abs=.01)
    assert aw.loc[D[4], "sz.000002"] == 0
    assert run_weight_schedule(p, sched, initial_cash=1e6, config=NOCOST, record_weights=False)["target_weights"] is None


def test_fastsim_target_vs_legacy_delta_rounding():
    from quantlab.smallcap.sim import Costs, Market, simulate
    with pytest.raises(ValueError):
        p = panels(n=3); C = p.close.to_numpy(); n = np.full_like(C, np.nan)
        simulate(Market(p.close.index, p.close.columns, p.open.to_numpy(), C, np.ones_like(C), n, n, np.full_like(C, np.inf)),
                 {}, costs=Costs(order_rounding="x"))


def test_effective_n_holdings_in_run_ladder_capacity():
    from quantlab.platform.execution import effective_n_holdings
    w = pd.DataFrame([[.5, .5], [1.0, 0.0], [0.0, 0.0]], columns=["a", "b"])
    e = effective_n_holdings(w)
    assert e.iloc[0] == pytest.approx(2.0) and e.iloc[1] == pytest.approx(1.0) and np.isnan(e.iloc[2])
    p = panels(n=8)
    sched = {D[1]: {"sh.600001": .45, "sz.000002": .45}}
    r = run_weight_schedule(p, sched, initial_cash=1e6, config=NOCOST)
    assert r["effective_n"].iloc[0] != r["effective_n"].iloc[0]  # NaN before holdings
    ref = effective_n_holdings(r["actual_weights"].astype(float))
    assert np.allclose(r["effective_n"].dropna(), ref.dropna(), rtol=1e-5)
    assert 2.0 < r["effective_n"].iloc[-1] < 2.6   # 0.45/0.45 -> ~1/0.405
    lad = cost_ladder(p, sched, initial_cash=1e6, base=ExecConfig(fill="next_open", enforce_limits=False, lots=False, sigma_window=2, adv_window=2, **ZERO_COST))
    assert "effective_n_mean" in lad.columns and "impact_bp_per_traded" in lad.columns
    cap = capacity_curve(p, sched, config=ExecConfig(fill="next_open", impact_k=1.0, sigma_window=2, adv_window=2, enforce_limits=False))
    assert {"effective_n_mean", "impact_bp_per_traded", "impact_cny"} <= set(cap.columns)


def test_impact_bp_per_traded_notional():
    p = panels(n=8)
    cfg = ExecConfig(fill="next_open", enforce_limits=False, sigma_window=3, adv_window=3, **{**ZERO_COST, "impact_k": 1.0})
    r = run_weight_schedule(p, {D[4]: {"sh.600001": .5}}, initial_cash=1e6, config=cfg)
    assert r["costs"]["impact"] > 0
    assert r["impact_bp_per_traded"] == pytest.approx(r["costs"]["impact"] / r["filled_notional"] * 1e4)
    z = run_weight_schedule(p, {D[4]: {"sh.600001": .5}}, initial_cash=1e6, config=NOCOST)
    assert z["impact_bp_per_traded"] == 0.0


def test_size_bucket_impact_k_optional():
    from quantlab.platform.execution import IMPACT_K_SIZE_BUCKET_REFERENCE
    from dataclasses import replace
    p = panels(n=8)
    sched = {D[4]: {"sh.600001": .4, "sz.000002": .4}}
    base = ExecConfig(fill="next_open", enforce_limits=False, sigma_window=3, adv_window=3, **{**ZERO_COST, "impact_k": 1.0})
    assert base.impact_k_by_bucket is None
    r0 = run_weight_schedule(p, sched, initial_cash=1e6, config=base, record_fills=True)
    b = replace(base, impact_k_by_bucket={"large": 0.5, "micro": 2.0}, size_bucket={"sh.600001": "large", "sz.000002": "micro"})
    r1 = run_weight_schedule(p, sched, initial_cash=1e6, config=b, record_fills=True)
    i0 = {f["code"]: f["impact"] for f in r0["fills"]}; i1 = {f["code"]: f["impact"] for f in r1["fills"]}
    assert i1["sh.600001"] < i0["sh.600001"] and i1["sz.000002"] > i0["sz.000002"]
    # bucket map without a code mapping -> uniform impact_k (unchanged)
    r2 = run_weight_schedule(p, sched, initial_cash=1e6, config=replace(base, impact_k_by_bucket={"large": 0.5}))
    assert r2["costs"]["impact"] == pytest.approx(r0["costs"]["impact"])
    assert set(IMPACT_K_SIZE_BUCKET_REFERENCE) == {"large", "small", "micro"}


def test_return_stats_ex_suspended_opt_in():
    from quantlab.platform.execution import return_stats_ex_suspended
    r = pd.Series([0.01, 0.0, 0.0, 0.03, -0.01])
    sus = pd.Series([False, True, True, False, False])
    st = return_stats_ex_suspended(r, sus)
    assert st["n_obs"] == 3 and st["n_suspended_excluded"] == 2
    assert st["mean"] == pytest.approx(0.01)
    assert st["mean"] > r.mean()   # zeros not counted
    df = return_stats_ex_suspended(pd.DataFrame({"a": r, "b": r}), pd.DataFrame({"a": sus, "b": ~sus & False}))
    assert df.loc["a", "n_obs"] == 3 and df.loc["b", "n_obs"] == 5


def test_load_execution_panels_honors_volume_shares_and_unit():
    """Synthetic panel only — no full-universe IO. Prefer volume_shares, else volume_unit."""
    from datetime import date
    from unittest.mock import patch

    from quantlab.data.v2_readers import MergedPanelView
    from quantlab.platform.execution import load_execution_panels

    idx = pd.bdate_range("2026-07-01", periods=3)
    base = dict(
        event_time=idx, open=[10.0, 10.1, 10.2], high=[10.5]*3, low=[9.9]*3,
        close=[10.0, 10.2, 10.3], volume=[100.0, 200.0, 150.0],
        amount=[1e5, 2.04e5, 1.545e5], limit_up=[11.0]*3, limit_down=[9.0]*3,
        open_status=["trading"]*3,
    )
    fr = pd.DataFrame({**base, "volume_shares": [10000.0, 20000.0, 15000.0], "volume_unit": ["lot_100sh"]*3})
    view = MergedPanelView(
        instrument_id="sh.600001", d0_asof_cutoff=date(2026, 6, 30),
        n_d0_rows=0, n_extend_rows=3, n_merged_rows=3,
        date_min=date(2026, 7, 1), date_max=date(2026, 7, 3),
        panel_source="extend_only", promotion_approved=False, quality_notes=(), frame=fr,
    )
    with patch("quantlab.data.v2_readers.load_merged_panel", return_value=view):
        panels, diag = load_execution_panels(["sh.600001"], "2026-07-01", "2026-07-03")
    assert panels.volume["sh.600001"].tolist() == [10000.0, 20000.0, 15000.0]
    assert diag["volume_shares_cells"] == 3

    fr2 = pd.DataFrame({**base, "volume_unit": ["lot_100sh"]*3})
    view2 = MergedPanelView(
        instrument_id="sh.600001", d0_asof_cutoff=date(2026, 6, 30),
        n_d0_rows=0, n_extend_rows=3, n_merged_rows=3,
        date_min=date(2026, 7, 1), date_max=date(2026, 7, 3),
        panel_source="extend_only", promotion_approved=False, quality_notes=(), frame=fr2,
    )
    with patch("quantlab.data.v2_readers.load_merged_panel", return_value=view2):
        panels2, diag2 = load_execution_panels(["sh.600001"], "2026-07-01", "2026-07-03")
    assert panels2.volume["sh.600001"].iloc[0] == 10000.0
    assert diag2["volume_unit_scaled_cells"] == 3
