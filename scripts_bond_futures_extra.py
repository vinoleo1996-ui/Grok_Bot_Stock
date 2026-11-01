#!/usr/bin/env python3
import sys,os,json; sys.path.insert(0,".")
exec(open("scripts_cb_etf_pull2.py").read().split("cal=call")[0])
import pandas as pd
def P(*a): print(*a, flush=True)
F="data/v2/futures/raw/"
fb=pd.read_parquet(F+"fut_basic.parquet"); fb=fb[fb.fut_code.isin(["T","TF","TS","TL"])]
os.makedirs(F+"settle",exist_ok=True)
for c in ["T.CFX","TF.CFX","TS.CFX","TL.CFX"]:
    fn=F+f"bond_map_{c}.parquet"
    if not os.path.exists(fn):
        try: call("fut_mapping",ts_code=c).to_parquet(fn); P("map",c)
        except Exception as e: P("FAILMAP",c,str(e)[:100])
    fn=F+f"daily/{c}.parquet"
    if not os.path.exists(fn):
        try: call("fut_daily",ts_code=c).to_parquet(fn)
        except Exception as e: P("FAILCONT",c,str(e)[:100])
for c in sorted(fb.ts_code):
    fn=F+f"settle/{c}.parquet"
    if os.path.exists(fn): continue
    try: call("fut_settle",ts_code=c).to_parquet(fn)
    except Exception as e: P("FAILSET",c,str(e)[:100])
P("EXTRA_DONE")
