import sys,os,time,json; sys.path.insert(0,'.')
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from quantlab.data_sources import tushare_proxy as t
KEY=os.environ["DATAHUB_API_KEY"]
CBF="ts_code,trade_date,pre_close,open,high,low,close,change,pct_chg,vol,amount,bond_value,bond_over_rate,cb_value,cb_over_rate"
def call(api,**p):
    for i in range(8):
        try:
            s,d=t._get(f"{t.DATAHUB_HTTPS}/{api}",KEY,p,retries=1,timeout=40)
            msg=str(d.get("msg"))
            if s==200 and d.get("code") in (0,None): return t._to_df(d)
            if s in (503,504) or "pool" in msg or "exhaust" in msg or s==429:
                time.sleep(min(60,3*2**i)); continue
            break
        except Exception: time.sleep(min(60,3*2**i))
    s,d=t.relay(api,**p)
    if d.get("code") not in (0,None): raise RuntimeError(f"{api} {p} {d.get('code')} {d.get('msg')}")
    return t._to_df(d)
cal=call("trade_cal",exchange="SSE",start_date="20180101",end_date="20261011",is_open="1")
days=sorted(cal.cal_date.astype(str))
json.dump(days,open("data/v2/cb/raw/days.json","w"))
jobs=[("cb_daily","cb",dict(fields=CBF)),("fund_daily","etf",{}),("fund_adj","etf",{})]
log=open("data/v2/cb/raw/pull.log","a")
def one(job):
    api,dirn,extra,d=job
    fn=f"data/v2/{dirn}/raw/{api}/{d}.parquet"
    if os.path.exists(fn): return
    try:
        df=call(api,trade_date=d,**extra); df.to_parquet(fn)
        if len(df) in (1000,2000,3000,5000,6000,8000): log.write(f"CAPSUSPECT {api} {d} {len(df)}\n")
    except Exception as e: log.write(f"FAIL {api} {d} {e}\n"); log.flush()
for api,dirn,_ in jobs: os.makedirs(f"data/v2/{dirn}/raw/{api}",exist_ok=True)
alljobs=[(a,dn,e,d) for d in days for a,dn,e in jobs]
with ThreadPoolExecutor(4) as ex:
    for i,_ in enumerate(ex.map(one,alljobs)):
        if i%300==0: print(i,len(alljobs),time.strftime("%H:%M"),flush=True)
print("DONE",flush=True)
