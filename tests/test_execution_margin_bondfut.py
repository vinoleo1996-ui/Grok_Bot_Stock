import numpy as np, pandas as pd, pytest
from quantlab.platform.execution import ExecConfig, ExecPanels, run_weight_schedule, ZERO_COST
from quantlab.platform.futures import (FuturesLeg, FuturesPanels, FuturesConfig, ALL_MULTIPLIER, BOND_TICK,
                                       last_trade_date, round_to_tick, margin_rate, daily_limit)
from quantlab.platform.margin import MarginConfig

D = pd.bdate_range("2025-01-02", "2025-06-30")
ZC = dict(fill="next_open", enforce_limits=False, price_tick="auto", **ZERO_COST)


def cfg(**kw):
    return ExecConfig(**{**ZC, **kw})


def stock_panels(path):
    c = pd.DataFrame({"sh.510300": path}, index=D)
    return ExecPanels(close=c, open=c.copy(), volume=c * 0 + 1e12)


# ------------------------------------------------------------- margin account
def test_default_off_unchanged_and_capped_at_cash():
    p = stock_panels(np.full(len(D), 4.0))
    r = run_weight_schedule(p, {D[0]: {"sh.510300": 1.5}}, initial_cash=1_000_000, config=cfg())
    assert r["final_shares"]["sh.510300"] * 4.0 <= 1_000_000 + 1e-6
    assert "financing_interest" not in r


def test_leverage_15_with_interest_accrual():
    p = stock_panels(np.full(len(D), 4.0))
    m = MarginConfig(financing_rate=0.05, spread=0.01, day_count=365, max_leverage=2.0)
    r = run_weight_schedule(p, {D[0]: {"sh.510300": 1.5}}, initial_cash=1_000_000, config=cfg(), margin=m)
    q = r["final_shares"]["sh.510300"]
    assert q == pytest.approx(375_000)            # 1.5 * 1e6 / 4, whole lots
    debt0 = q * 4.0 - 1_000_000                   # 500k borrowed at D[1] open
    # hand-accrue: interest on prior-close debt, ACT/365, compounding into debt
    debt = debt0; tot = 0.0
    for a, b in zip(D[1:-1], D[2:]):
        it = debt * 0.06 * (b - a).days / 365; tot += it; debt += it
    assert r["financing_interest"] == pytest.approx(tot, rel=1e-12)
    assert r["nav"].iloc[-1] == pytest.approx(1_000_000 - tot, rel=1e-12)
    assert r["leverage"].iloc[1] == pytest.approx(1.5, rel=1e-12)   # drifts up as interest erodes equity
    assert r["peak_leverage"] == pytest.approx(1_500_000 / (1_000_000 - tot), rel=1e-9)
    assert r["liquidation_events"] == 0 and r["min_maintenance_ratio"] > 2.9
    # NAV identity
    assert r["nav"].iloc[-1] == pytest.approx(r["cash"] + q * 4.0)
    assert r["debt"].iloc[-1] == pytest.approx(-r["cash"])


def test_max_leverage_caps_borrowing():
    p = stock_panels(np.full(len(D), 4.0))
    r = run_weight_schedule(p, {D[0]: {"sh.510300": 3.0}}, initial_cash=1_000_000, config=cfg(),
                            margin=MarginConfig(financing_rate=0.0, max_leverage=2.0))
    assert r["final_shares"]["sh.510300"] * 4.0 <= 2_000_000 + 1e-6
    assert r["peak_leverage"] <= 2.0 + 1e-9


def test_maintenance_breach_liquidates_and_restores():
    px = np.full(len(D), 4.0); px[20:] = 2.4          # -40% crash on D[20]
    p = stock_panels(px)
    m = MarginConfig(financing_rate=0.0, max_leverage=2.0, liquidation_ratio=1.3, restore_ratio=1.5)
    r = run_weight_schedule(p, {D[0]: {"sh.510300": 2.0}}, initial_cash=1_000_000, config=cfg(), margin=m)
    ev = [e for e in r["events"] if e["reason"] == "margin_liquidation"]
    assert ev and ev[0]["date"] == str(D[20].date())
    # 500k shares*2.4 = 1.2M vs 1.0M debt -> 1.2 < 1.3
    assert ev[0]["ratio"] == pytest.approx(1.2)
    assert r["maintenance_ratio"].iloc[21] >= 1.5 - 1e-3          # restored after next-open sale
    assert r["liquidation_events"] == 1
    assert r["min_maintenance_ratio"] == pytest.approx(1.2)
    # flag-only: no selling
    r2 = run_weight_schedule(p, {D[0]: {"sh.510300": 2.0}}, initial_cash=1_000_000, config=cfg(),
                             margin=MarginConfig(financing_rate=0.0, max_leverage=2.0, liquidation_action="flag"))
    assert r2["final_shares"]["sh.510300"] == 500_000 and r2["liquidation_events"] > 1


def test_warning_and_haircut():
    px = np.full(len(D), 4.0); px[20:] = 3.0
    m = MarginConfig(financing_rate=0.0, haircuts={"sh.510300": 0.9}, liquidation_action="flag")
    r = run_weight_schedule(stock_panels(px), {D[0]: {"sh.510300": 2.0}}, initial_cash=1_000_000, config=cfg(), margin=m)
    assert r["maintenance_ratio"].iloc[5] == pytest.approx(2_000_000 * 0.9 / 1_000_000)
    assert r["maintenance_ratio"].iloc[20] == pytest.approx(1_500_000 * 0.9 / 1_000_000)
    assert any(e["reason"] == "margin_warning" for e in r["events"])


# ------------------------------------------------------------- bond futures
def bond_panels(contracts=("T2503", "T2506", "T2509"), base=108.0, step=0.01):
    S = pd.DataFrame({c: base - 0.1 * k + step * np.arange(len(D)) for k, c in enumerate(contracts)}, index=D)
    for c in contracts:
        S.loc[S.index > last_trade_date(c, D), c] = np.nan
    S = S.map(lambda x: round_to_tick(x, 0.005) if np.isfinite(x) else x)
    return FuturesPanels(settle=S, open=S.shift(1).fillna(S), close=S.copy())


def test_bond_constants():
    assert ALL_MULTIPLIER["T"] == ALL_MULTIPLIER["TF"] == ALL_MULTIPLIER["TL"] == 10_000 and ALL_MULTIPLIER["TS"] == 20_000
    assert BOND_TICK == {"T": 0.005, "TF": 0.005, "TS": 0.002, "TL": 0.01}
    assert last_trade_date("T2503") == pd.Timestamp("2025-03-14")      # 2nd Friday
    assert last_trade_date("IF2503") == pd.Timestamp("2025-03-21")     # index unchanged
    assert margin_rate("T", "2025-01-02") == 0.02 and margin_rate("TS", "2025-01-02") == 0.005
    assert daily_limit("TF") == 0.012 and daily_limit("IF") == 0.10


def test_bond_pnl_scale_lots_fees_and_roll_before_delivery_month():
    fp = bond_panels()
    leg = FuturesLeg(fp, FuturesConfig(roll_mode="roll", roll_days=0, contract_months="quarterly"))
    r = run_weight_schedule(stock_panels(np.full(len(D), 4.0)), {D[0]: {"T": 2.0}}, initial_cash=5_000_000,
                            config=cfg(), futures=leg)
    lots = round(2.0 * 5_000_000 / (fp.settle.loc[D[0], "T2503"] / 100 * 1_000_000))
    f0 = r["fut_fills"][0]
    assert f0["lots"] == lots and f0["fee"] == pytest.approx(3.0 * lots)
    rolls = [f for f in r["fut_fills"] if f["why"] == "roll_out"]
    assert rolls[0]["date"] == "2025-03-03" and rolls[0]["code"] == "T2503"   # first session of March
    assert rolls[1]["date"] == "2025-06-02"
    # VM = sum price diffs x 10,000 x lots
    vm = r["variation_margin_daily"]
    assert vm.loc[D[5]] == pytest.approx((fp.settle.loc[D[5], "T2503"] - fp.settle.loc[D[4], "T2503"]) * 10_000 * lots)
    assert r["margin"].loc[D[5]] == pytest.approx(lots * fp.settle.loc[D[5], "T2503"] * 10_000 * 0.02)
    assert r["nav"].iloc[-1] == pytest.approx(5_000_000 + r["variation_margin"] - r["fut_total_fees"])


def test_bond_tick_and_limit_block():
    fp = bond_panels()
    fp.open.loc[D[1], "T2503"] = round_to_tick(fp.settle.loc[D[0], "T2503"] * 1.02, 0.005)
    leg = FuturesLeg(fp, FuturesConfig(roll_mode="roll", contract_months="quarterly", slippage_ticks=1))
    r = run_weight_schedule(stock_panels(np.full(len(D), 4.0)), {D[0]: {"T": 1.0}}, initial_cash=5_000_000,
                            config=cfg(), futures=leg)
    assert any(e["reason"] == "fut_limit_up" and e["date"] == str(D[1].date()) for e in r["events"])
    f = r["fut_fills"][0]
    assert f["date"] == str(D[2].date()) and f["price"] - f["ref_price"] == pytest.approx(0.005)


# ------------------------------------------------------------- combined account
def test_combined_account_cash_conservation():
    rng = np.random.default_rng(7)
    px = 4.0 * np.exp(np.cumsum(rng.normal(0, 0.01, len(D))))
    sp = stock_panels(px)
    I = pd.DataFrame({"IF2503": 3900 + np.cumsum(rng.normal(0, 20, len(D))), "IF2506": 3880 + np.cumsum(rng.normal(0, 20, len(D)))}, index=D).map(round_to_tick)
    T = bond_panels().settle
    S = pd.concat([I, T], axis=1)
    for c in S:
        S.loc[S.index > last_trade_date(c, D), c] = np.nan
    fp = FuturesPanels(settle=S, open=S.shift(1).fillna(S))
    leg = FuturesLeg(fp, FuturesConfig(roll_mode="roll", contract_months="quarterly"))
    m = MarginConfig(financing_rate=0.04, spread=0.01, max_leverage=2.5, liquidation_action="flag")
    sched = {D[0]: {"sh.510300": 1.6, "IF": -0.3, "T": 1.5}, D[60]: {"sh.510300": 1.2, "IF": 0.0, "T": 2.0}}
    c = cfg(cash_rate=0.015)
    r = run_weight_schedule(sp, sched, initial_cash=3_000_000, config=c, futures=leg, margin=m)
    q = r["final_shares"]["sh.510300"]
    # equity = cash + MV + futures (VM already in cash; no open unrealized at settle) ; debt = -cash
    assert r["nav"].iloc[-1] == pytest.approx(r["cash"] + q * px[-1], rel=1e-12)
    # cash conservation: final cash = initial - net stock buys - stock costs + VM - fut fees - financing + cash interest
    stock_pnl = r["nav"].iloc[-1] - 3_000_000 - r["variation_margin"] + r["fut_total_fees"] + r["financing_interest"] - r["cash_interest"]
    r0 = run_weight_schedule(sp, sched, initial_cash=3_000_000, config=c, futures=leg, margin=m, record_fills=True)
    sp_pnl = sum(-f["side"] * f["qty"] * f["price"] for f in r0["fills"]) + q * px[-1]
    assert stock_pnl == pytest.approx(sp_pnl, rel=1e-9, abs=1e-6)
    assert r["peak_leverage"] > 1.5 and r["financing_interest"] > 0 and r["margin_peak"] > 0
