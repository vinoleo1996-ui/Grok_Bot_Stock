"""Hand-check of one IF quarter (docs/v2/IF_QUARTER_HANDCHECK.md).
Default (2026-10-11): REAL CFFEX bars (data/v2/futures/raw/daily via futures.load_index_futures_panels); --synthetic = old synthetic path.
Position: 1 IF2412 long opened at the 2024-10-08 open, rolled 5 sessions before the 2024-12-20 last trading
day into IF2503 (close old / open new at the roll-day open), closed at the 2024-12-31 open.
Independent of the engine: plain pandas, step by step."""
import argparse, numpy as np, pandas as pd

def synth():
    d = pd.bdate_range("2024-09-23", "2024-12-31")
    d = d[~d.isin(pd.bdate_range("2024-10-01", "2024-10-07"))]   # National Day
    rng = np.random.default_rng(2412)
    s = 3900 + np.cumsum(rng.normal(0, 30, len(d)))
    tick = lambda x: np.floor(np.asarray(x) / 0.2 + 0.5) * 0.2
    S = pd.DataFrame({"IF2412": tick(s), "IF2503": tick(s - 25)}, index=d)
    O = pd.DataFrame({c: tick(S[c].shift(1).fillna(S[c].iloc[0]) + rng.normal(0, 8, len(d))) for c in S}, index=d)
    S.loc[S.index > "2024-12-20", "IF2412"] = np.nan; O.loc[O.index > "2024-12-20", "IF2412"] = np.nan
    return S, O

def real():
    from quantlab.platform.futures import load_index_futures_panels
    fp = load_index_futures_panels(contracts=["IF2412", "IF2503"], start="2024-09-23", end="2024-12-31")
    S, O = fp.settle[["IF2412", "IF2503"]], fp.open[["IF2412", "IF2503"]]
    return S, O, fp

def hand(S, O, cash0=2_000_000.0):
    M, FO, FC, MR = 300, 0.000023, 0.000023, 0.12          # 2024: fee open/close, IF margin 12%
    d = S.index
    entry, exit_ = pd.Timestamp("2024-10-08"), pd.Timestamp("2024-12-31")
    ltd = pd.Timestamp("2024-12-20"); roll = d[d.get_loc(ltd) - 5]
    rows, cash = [], cash0
    held = None
    for t in d:
        fee = vm = 0.0; c_old = held
        if t == entry:
            held = "IF2412"; px = O.at[t, held]; fee += px * M * FO; vm += S.at[t, held] - px
        elif t == roll:
            po, pn = O.at[t, "IF2412"], O.at[t, "IF2503"]
            vm += po - S.at[d[d.get_loc(t) - 1], "IF2412"]          # old leg: prev settle -> roll price
            fee += po * M * FC + pn * M * FO; roll_fee = po * M * FC + pn * M * FO
            held = "IF2503"; vm += S.at[t, held] - pn               # new leg: roll price -> settle
        elif t == exit_:
            px = O.at[t, held]; vm += px - S.at[d[d.get_loc(t) - 1], held]; fee += px * M * FC; held = None
        elif held is not None:
            vm += S.at[t, held] - S.at[d[d.get_loc(t) - 1], held]
        vm *= M
        cash += vm - fee
        margin = S.at[t, held] * M * MR if held else 0.0
        rows.append(dict(date=t, contract=held, settle=S.at[t, held] if held else np.nan, vm=vm, fee=fee, margin=margin, cash=cash))
    return pd.DataFrame(rows).set_index("date"), roll, roll_fee

def engine(S, O, cash0=2_000_000.0, fp=None):
    from quantlab.platform.execution import ExecConfig, ExecPanels, run_weight_schedule, ZERO_COST
    from quantlab.platform.futures import FuturesLeg, FuturesPanels, FuturesConfig
    d = S.index
    etf = pd.DataFrame({"sh.510300": 4.0}, index=d)
    sig_in = d[d.get_loc(pd.Timestamp("2024-10-08")) - 1]; sig_out = d[d.get_loc(pd.Timestamp("2024-12-31")) - 1]
    w = S.at[sig_in, "IF2412"] * 300 / cash0
    panels = fp if fp is not None else FuturesPanels(settle=S, open=O, expiry={"IF2412": "2024-12-20", "IF2503": "2025-03-21"})
    leg = FuturesLeg(panels,
                     FuturesConfig(roll_mode="roll", roll_days=5, contract_months="quarterly"))
    r = run_weight_schedule(ExecPanels(close=etf, open=etf), {sig_in: {"IF": w}, sig_out: {"IF": 0.0}},
                            initial_cash=cash0, config=ExecConfig(fill="next_open", enforce_limits=True, **ZERO_COST), futures=leg)
    return r

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--synthetic", action="store_true"); a = ap.parse_args()
    if a.synthetic:
        S, O = synth(); fp = None
    else:
        S, O, fp = real()
    h, roll, roll_fee = hand(S, O)
    r = engine(S, O, fp=fp)
    cmp = pd.DataFrame({"hand_vm": h.vm, "eng_vm": r["variation_margin_daily"], "hand_margin": h.margin, "eng_margin": r["margin"],
                        "hand_cash": h.cash, "eng_nav": r["nav"]})
    cmp["d_vm"] = cmp.eng_vm - cmp.hand_vm; cmp["d_margin"] = cmp.eng_margin - cmp.hand_margin; cmp["d_nav"] = cmp.eng_nav - cmp.hand_cash
    out = dict(roll_date=str(roll.date()), hand_total_vm=h.vm.sum(), eng_total_vm=r["variation_margin"],
               hand_fees=h.fee.sum(), eng_fees=r["fut_total_fees"], hand_roll_fee=roll_fee, eng_roll_cost=r["roll_cost"],
               hand_margin_peak=h.margin.max(), eng_margin_peak=r["margin_peak"], hand_final=h.cash.iloc[-1], eng_final=r["nav"].iloc[-1],
               max_abs_d_vm=cmp.d_vm.abs().max(), max_abs_d_margin=cmp.d_margin.abs().max(), max_abs_d_nav=cmp.d_nav.abs().max())
    out["source"] = "synthetic" if a.synthetic else "real CFFEX IF2412/IF2503"
    for k, v in out.items():
        print(f"{k:20s} {v}")
    cmp.to_csv("output/v2_proto/if_quarter_handcheck%s.csv" % ("" if a.synthetic else "_real"))
