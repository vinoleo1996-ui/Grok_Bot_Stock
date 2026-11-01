#!/usr/bin/env python3
"""Beta S2-3 cosign check, step 1: cache per-day exposures (β_i, ln_mcap, industry, wb, pool) for X2 rebalance days.
No returns, no NAV. live=false."""
import sys, pickle, gc
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "research"))
import optimizer_lambda_calib_sealed as C
OUT = ROOT / "output/beta/s2_3_band_check/_cache"; OUT.mkdir(parents=True, exist_ok=True)
ck = ROOT / "output/strategy_optimizer/core_x2/_ckpt_v1_2"
days = sorted(pd.Timestamp(p.stem) for p in ck.glob("*.pkl"))
days = [d for d in days if d >= pd.Timestamp("2024-05-31")]
for d in days:
    f = OUT / f"{d:%Y%m%d}.pkl"
    if f.exists(): continue
    D = C.prepare_day(d)
    if D is None: pickle.dump(None, open(f, "wb")); continue
    keep = {k: D[k] for k in ("alpha", "wb", "ln_mcap", "industry", "betas")}
    pickle.dump(keep, open(f, "wb")); print(d.date(), D["n"], round(C.rss_mb()), flush=True)
    del D; gc.collect()
print("CACHE_DONE", len(days))
