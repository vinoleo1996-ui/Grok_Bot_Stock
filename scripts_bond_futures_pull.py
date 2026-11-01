#!/usr/bin/env python3
"""Light T/TF/TS/TL fut_daily catch-up. Skip existing files. Do not start while heavy jobs run."""
import sys,os; sys.path.insert(0,".")
exec(open("scripts_cb_etf_pull2.py").read().split("cal=call")[0])
import pandas as pd
def P(*a): print(*a, flush=True)
F="data/v2/futures/raw/"
fbx=pd.read_parquet(F+"fut_basic.parquet")
fbx=fbx[fbx.fut_code.isin(["T","TF","TS","TL"])]
os.makedirs(F+"daily", exist_ok=True)
n=0
for c in sorted(fbx.ts_code):
    fn=F+f"daily/{c}.parquet"
    if os.path.exists(fn): continue
    try:
        call("fut_daily", ts_code=c).to_parquet(fn); n+=1
        if n%20==0: P("bond", n, c)
    except Exception as e:
        P("FAIL", c, str(e)[:80])
P("BOND_FUT_DONE", n, "of", len(fbx))
