"""Hand-check of one T (10Y treasury future) quarter (docs/v2/T_QUARTER_HANDCHECK.md).
SYNTHETIC prices (no bond futures daily bars on the box). 2 lots T2412 long opened 2024-09-23 open,
rolled at the 2024-12-02 open (first session of the delivery month, roll_days=0) into T2503,
closed at the 2024-12-31 open. Plain pandas, independent of the engine."""
import numpy as np, pandas as pd

M, FEE, MR, LOTS = 10_000, 3.0, 0.02, 2


def tick(x):
    return np.floor(np.asarray(x) / 0.005 + 0.5) * 0.005


def synth():
    d = pd.bdate_range("2024-09-16", "2024-12-31")
    d = d[~d.isin(pd.bdate_range("2024-10-01", "2024-10-07"))]
    rng = np.random.default_rng(1012)
    s = 106 + np.cumsum(rng.normal(0, 0.12, len(d)))
    S = pd.DataFrame({"T2412": tick(s), "T2503": tick(s - 0.15)}, index=d)
    O = pd.DataFrame({c: tick(S[c].shift(1).fillna(S[c].iloc[0]) + rng.normal(0, 0.04, len(d))) for c in S}, index=d)
    S.loc[S.index > "2024-12-13", "T2412"] = np.nan; O.loc[O.index > "2024-12-13", "T2412"] = np.nan
    return S, O


def real():
    """REAL CFFEX bars (data/v2/futures/raw/daily, Tushare fut_daily) for T2412/T2503, same dates."""
    from quantlab.platform.futures import load_futures_panels
    p = load_futures_panels(contracts=["T2412", "T2503"], start="2024-09-16", end="2024-12-31")
    return p.settle[["T2412", "T2503"]], p.open[["T2412", "T2503"]], p


def hand(S, O, cash0=3_000_000.0):
    d = S.index
    entry, roll, exit_ = pd.Timestamp("2024-09-23"), pd.Timestamp("2024-12-02"), pd.Timestamp("2024-12-31")
    rows, cash, held = [], cash0, None
    for t in d:
        fee = vm = 0.0; prev = d[d.get_loc(t) - 1] if d.get_loc(t) else None
        if t == entry:
            held = "T2412"; px = O.at[t, held]; fee += LOTS * FEE; vm += S.at[t, held] - px
        elif t == roll:
            vm += O.at[t, "T2412"] - S.at[prev, "T2412"]; fee += 2 * LOTS * FEE
            held = "T2503"; vm += S.at[t, held] - O.at[t, held]
        elif t == exit_:
            vm += O.at[t, held] - S.at[prev, held]; fee += LOTS * FEE; held = None
        elif held is not None:
            vm += S.at[t, held] - S.at[prev, held]
        vm *= M * LOTS
        cash += vm - fee
        rows.append(dict(date=t, contract=held, settle=S.at[t, held] if held else np.nan, vm=vm, fee=fee,
                         margin=S.at[t, held] * M * MR * LOTS if held else 0.0, cash=cash))
    return pd.DataFrame(rows).set_index("date")


def engine(S, O, cash0=3_000_000.0, panels=None):
    from quantlab.platform.execution import ExecConfig, ExecPanels, run_weight_schedule, ZERO_COST
    from quantlab.platform.futures import FuturesLeg, FuturesPanels, FuturesConfig
    d = S.index
    etf = pd.DataFrame({"sh.510300": 4.0}, index=d)
    sig_in, sig_out = d[d.get_loc(pd.Timestamp("2024-09-23")) - 1], d[d.get_loc(pd.Timestamp("2024-12-31")) - 1]
    w = LOTS * S.at[sig_in, "T2412"] / 100 * 1_000_000 / cash0
    leg = FuturesLeg(panels or FuturesPanels(settle=S, open=O), FuturesConfig(roll_mode="roll", roll_days=0, contract_months="quarterly"))
    return run_weight_schedule(ExecPanels(close=etf, open=etf), {sig_in: {"T": w}, sig_out: {"T": 0.0}}, initial_cash=cash0,
                               config=ExecConfig(fill="next_open", enforce_limits=True, **ZERO_COST), futures=leg)


if __name__ == "__main__":
    import sys
    if "--real" in sys.argv:
        S, O, P = real(); print("REAL T bars (data/v2/futures/raw/daily), exchange pre_settle, limits enforced")
    else:
        S, O = synth(); P = None; print("SYNTHETIC prices")
    h = hand(S, O); r = engine(S, O, panels=P)
    eng = pd.DataFrame(dict(vm=r["variation_margin_daily"], margin=r["margin"], cash=r["nav"]))
    diff = (h[["vm", "margin", "cash"]] - eng).abs().max()
    print(h.loc["2024-09-20":"2024-09-25"].round(2)); print(h.loc["2024-11-28":"2024-12-04"].round(2)); print(h.tail(2).round(2))
    print("fills:", [(f["date"], f["code"], f["lots"], f["price"], f["fee"], f["why"]) for f in r["fut_fills"]])
    print("hand: VM %.2f fees %.2f final cash %.2f | engine: VM %.2f fees %.2f nav %.2f roll_cost %.2f margin_peak %.2f"
          % (h.vm.sum(), h.fee.sum(), h.cash.iloc[-1], r["variation_margin"], r["fut_total_fees"], r["nav"].iloc[-1], r["roll_cost"], r["margin_peak"]))
    print("max abs diff per column:", diff.to_dict())
    assert (diff < 1e-6).all()
    print("OK: engine == hand calc")
