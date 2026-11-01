import sys,os,time; sys.path.insert(0,'.')
from quantlab.data_sources import tushare_proxy as t
import pandas as pd
K=os.environ["DATAHUB_API_KEY"]
def call(api,**p):
    for i in range(6):
        try:
            s,d=t._get(f"{t.DATAHUB_HTTPS}/{api}",K,p,retries=1,timeout=40)
            if s==200 and d.get("code") in (0,None): return t._to_df(d)
            if s in (429,503,504) or "pool" in str(d.get("msg")): time.sleep(min(60,3*2**i)); continue
            raise RuntimeError(f"{s} {d.get('msg')}")
        except RuntimeError as e:
            if "failed" in str(e): time.sleep(min(60,3*2**i)); continue
            raise
        except Exception: time.sleep(min(60,3*2**i))
    raise RuntimeError("datahub retries exhausted")
R="data/v2/cb/raw/"
codes=sorted(pd.read_parquet(R+"cb_basic_raw.parquet").ts_code)
for api,kw in [("cb_share",{}),("cb_call",{}),("cb_rate",{"fields":"ts_code,rate_freq,rate_start_date,rate_end_date,coupon_rate"})]:
    os.makedirs(R+api,exist_ok=True); a=time.time()
    for i,c in enumerate(codes):
        fn=R+f"{api}/{c}.parquet"
        if os.path.exists(fn): continue
        try: call(api,ts_code=c,**kw).to_parquet(fn)
        except Exception as e: print("FAIL",api,c,str(e)[:80],flush=True)
        if i%200==0: print(api,i,round(time.time()-a),flush=True)
    pd.concat([pd.read_parquet(f) for f in __import__("glob").glob(R+api+"/*.parquet")],ignore_index=True).to_parquet(R+f"{api}_raw.parquet"); print(api,"done",flush=True)
