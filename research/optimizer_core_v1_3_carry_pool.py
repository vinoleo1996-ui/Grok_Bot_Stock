#!/usr/bin/env python3
"""v1.3 disclosure add-on (Arch v1.3 cosign P2): for carry days (INFEASIBLE / LOT_HARD_FAIL), count carried holdings
that are no longer in that day's solver pool (D['alpha'].index, same as Arch recheck). Adds columns
carry_n_out_of_pool, carry_out_of_pool_names to core_v1_3_disclosure.csv. Weights only; NO returns."""
import sys
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "research"))
import optimizer_lambda_calib_sealed as C
OUT = ROOT / "output/strategy_optimizer/core_x2"; TAG = {600000: "60w", 1000000: "100w"}
D = pd.read_csv(OUT / "core_v1_3_disclosure.csv")
m = D.status.isin(["INFEASIBLE", "LOT_HARD_FAIL"])
W = {(a, sv): pd.read_parquet(OUT / f"core_{sv}_{t}.parquet", columns=["session", "instrument", "weight"]) for a, t in TAG.items() for sv in C.REPORT_SLEEVES}
D["carry_n_out_of_pool"] = pd.NA; D["carry_out_of_pool_names"] = ""
for d in sorted(D.loc[m, "date"].unique()):
    P = C.prepare_day(pd.Timestamp(d)); pool = set(P["alpha"].index) if P is not None else set()
    for ix in D.index[m & (D.date == d)]:
        a, sv = D.at[ix, "aum"], D.at[ix, "sleeve"]; w = W[(a, sv)]; held = w[(w.session == d) & (w.weight > 0)].instrument
        out = sorted(i for i in held if i != C.BALLAST and i not in pool)
        D.at[ix, "carry_n_out_of_pool"] = len(out); D.at[ix, "carry_out_of_pool_names"] = ",".join(out)
    print(d, flush=True)
D.to_csv(OUT / "core_v1_3_disclosure.csv", index=False)
x = D[m]; print("CARRY_POOL_DONE rows", len(x), "rows_with_out", int((x.carry_n_out_of_pool > 0).sum()), "instances", int(x.carry_n_out_of_pool.sum()))
print(x[x.carry_n_out_of_pool > 0][["date", "aum", "sleeve", "carry_n_out_of_pool", "carry_out_of_pool_names"]].to_string())
