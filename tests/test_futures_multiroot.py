"""Multi-root FuturesLeg (IF+IC+T+TF in one book): independent per-root roll schedules, per-root
fees/margins, combined margin, NAV identity, window boundary, bond delivery-month margin step-up."""
import numpy as np
import pandas as pd

from quantlab.platform.execution import ExecConfig, ExecPanels, run_weight_schedule, ZERO_COST
from quantlab.platform.futures import (FuturesLeg, FuturesPanels, FuturesConfig, last_trade_date, round_to_tick,
                                       ALL_MULTIPLIER, tick_for_root, margin_rate, root_of, BOND_DELIVERY_MARGIN)

D = pd.bdate_range("2025-01-02", "2025-08-29")
ROOTS = {"IF": 4000.0, "IC": 6000.0, "T": 108.0, "TF": 105.0}
CASH0 = 50_000_000.0


def panels(dates=D):
    S = {}
    rng = np.random.default_rng(7)
    for r, base in ROOTS.items():
        walk = base * np.exp(np.cumsum(rng.normal(0, 0.004 if len(r) == 2 and r[0] == "I" else 0.001, len(dates))))
        for k, m in enumerate((3, 6, 9)):
            c = f"{r}25{m:02d}"
            s = pd.Series(walk * (1 - 0.002 * k), index=dates)
            s[s.index > last_trade_date(c, dates)] = np.nan
            S[c] = s.map(lambda x, r=r: round_to_tick(x, tick_for_root(r)) if np.isfinite(x) else x)
    S = pd.DataFrame(S)
    return FuturesPanels(settle=S, open=S.shift(1).fillna(S), close=S.copy())


W = {"IF": 0.5, "IC": -0.3, "T": 2.0, "TF": 1.5}
RD = {"IF": 5, "IC": 2, "T": 15, "TF": 15}


def run(fp, dates=D, cfg=None, w=W):
    etf = pd.DataFrame({"sh.510300": 4.0}, index=dates)
    cfg = cfg or FuturesConfig(roll_mode="roll", roll_days_by_root=RD, contract_months="quarterly",
                               bond_roll_rule="earlier_of", enforce_limits=False)
    return run_weight_schedule(ExecPanels(close=etf, open=etf), {dates[0]: w}, initial_cash=CASH0,
                               config=ExecConfig(fill="next_open", enforce_limits=False, **ZERO_COST),
                               futures=FuturesLeg(fp, cfg))


def test_independent_roll_dates_per_root():
    r = run(panels())
    outs = {f["code"]: pd.Timestamp(f["date"]) for f in r["fut_fills"] if f["why"] == "roll_out"}
    pos = lambda d: D.get_loc(d)
    for c in ("IF2503", "IF2506"):
        assert pos(outs[c]) == pos(last_trade_date(c, D)) - 5
    for c in ("IC2503", "IC2506"):
        assert pos(outs[c]) == pos(last_trade_date(c, D)) - 2
    for c in ("T2503", "TF2503", "T2506", "TF2506"):
        ltd = last_trade_date(c, D); dm = D[D >= ltd.replace(day=1)][0]
        assert pos(outs[c]) == min(pos(ltd) - 15, pos(dm) - 1)
        assert outs[c] < dm                                   # out before delivery month
    days = {r_: {outs[c] for c in outs if root_of(c) == r_} for r_ in ROOTS}
    assert days["IF"].isdisjoint(days["IC"]) and days["IF"].isdisjoint(days["T"])
    assert r["n_rolls"] == 8
    # signs per root preserved after rolls
    end = r["fut_positions"]
    assert end["IF2509"] > 0 and end["IC2509"] < 0 and end["T2509"] > 0 and end["TF2509"] > 0


def test_per_root_fees_and_combined_margin_and_nav_identity():
    fp = panels(); r = run(fp)
    for f in r["fut_fills"]:
        root = root_of(f["code"])
        if root in ("T", "TF"):
            assert abs(f["fee"] - 3.0 * abs(f["lots"])) < 1e-9          # 3 CNY/lot open & close-yesterday
        else:
            assert abs(f["fee"] - 0.000023 * f["price"] * ALL_MULTIPLIER[root] * abs(f["lots"])) < 1e-6
    # rebuild positions from fills -> combined margin per day
    pos = pd.Series(0.0, index=fp.settle.columns); S = fp.settle
    fills = pd.DataFrame(r["fut_fills"]); fills["date"] = pd.to_datetime(fills["date"])
    for t in D:
        for f in fills[fills.date == t].itertuples():
            pos[f.code] += f.lots
        m = sum(abs(q) * S.at[t, c] * ALL_MULTIPLIER[root_of(c)] * margin_rate(root_of(c), t) for c, q in pos.items() if q)
        assert abs(m - r["margin"][t]) < 1e-4
    assert r["margin_peak"] == r["margin"].max()
    # NAV identity: daily change = variation margin - fees (zero-cost cash leg, no interest)
    fee_d = fills.groupby("date")["fee"].sum().reindex(D, fill_value=0.0)
    dn = r["nav"].diff().fillna(r["nav"].iloc[0] - CASH0)
    assert np.allclose(dn, r["variation_margin_daily"] - fee_d, atol=1e-4)
    assert abs(r["nav"].iloc[-1] - (CASH0 + r["variation_margin"] - r["fut_total_fees"])) < 1e-4


def test_window_boundary_expiry_after_window_no_liquidation():
    d = D[D <= "2025-05-30"]          # IF2506/IC2506 LTD 06-20, T2506 delivery month starts 06-02: all outside
    fp = panels(d)
    r = run(fp, d)
    late = [f for f in r["fut_fills"] if pd.Timestamp(f["date"]) > d[-8]]
    assert late == [], late
    assert not any(e.get("reason") == "fut_roll_no_next" for e in r["events"])
    assert set(r["fut_positions"]) == {"IF2506", "IC2506", "T2506", "TF2506"}


def test_bond_delivery_month_margin_step_up_optional():
    fp = panels()
    cfg = dict(roll_mode="roll", roll_days_by_root={"T": 0}, contract_months="quarterly", enforce_limits=False,
               bond_roll_rule="earlier_of", bond_exit_sessions_before_dm=0)   # rolls ON the 1st dm session
    w = {"T": 2.0}
    base = run(fp, cfg=FuturesConfig(**cfg), w=w)
    up = run(fp, cfg=FuturesConfig(**cfg, bond_delivery_margin=True), w=w)
    dm = D[D >= "2025-03-01"][0]; i = D.get_loc(dm)
    for t in (D[i - 2], D[i - 1]):     # still holding T2503 in the 2 sessions before the delivery month
        assert abs(up["margin"][t] / base["margin"][t] - BOND_DELIVERY_MARGIN["T"] / 0.02) < 1e-9
    assert abs(up["margin"][D[i - 3]] - base["margin"][D[i - 3]]) < 1e-6
