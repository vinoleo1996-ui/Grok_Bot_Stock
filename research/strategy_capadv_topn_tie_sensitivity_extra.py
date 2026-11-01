#!/usr/bin/env python3
"""SENSITIVITY ONLY: extra random tie-break seeds 6..20 (same build as strategy_capadv_topn_tie_sensitivity.py)."""
import sys, json, hashlib, time
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import importlib.util
sp = importlib.util.spec_from_file_location("ts", ROOT/"research/strategy_capadv_topn_tie_sensitivity.py"); ts = importlib.util.module_from_spec(sp); sp.loader.exec_module(ts)
res = {}
for seed in range(6, 21):
    def rk(st, s, k, seed=seed):
        h = int(hashlib.md5(f"{seed}|{s}|{k}".encode()).hexdigest()[:8], 16); return np.random.default_rng(h).permutation(len(st))
    Ws = ts.build(ts.keyed(rk))
    for aum, W in Ws.items():
        tag = f"RAND{seed}_{aum//10000}w"; fp = ts.OUT/f"sens_weights_B4_{tag}.parquet"; W.to_parquet(fp, index=False)
        sd = ts.OUT/f"sens_smoke_B4_{tag}"; sm = ts.lr.run_smoke(fp, sd, str(aum)); nav = sd/f"aum_{aum}"/"X2"/"BOOK"/"nav.csv"
        res[tag] = dict(metrics=ts.lr.nav_metrics(nav) if nav.exists() else None); m = res[tag]["metrics"] or {}
        print(tag, round(m.get("cagr", np.nan), 4), round(m.get("mdd", np.nan), 4), flush=True)
(ts.OUT/"sensitivity_summary_rand_extra.json").write_text(json.dumps(res, indent=1, default=float)); print("WROTE")
