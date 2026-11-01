import sys,os,time,json; sys.path.insert(0,'.')
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from quantlab.data_sources import tushare_proxy as t
K=os.environ["DATAHUB_API_KEY"]; D="data/v2/tushare_raw/adj_factor_hist/"; os.makedirs(D,exist_ok=True)
def call(**p):
    for i in range(8):
        try:
            s,d=t._get(f"{t.DATAHUB_HTTPS}/adj_factor",K,p,retries=1,timeout=40)
            if s==200 and d.get("code") in (0,None): return t._to_df(d)
        except Exception: pass
        time.sleep(min(60,3*2**i))
    raise RuntimeError("exhausted")
cal=call.__globals__  # noop
days=[d for d in json.load(open("data/v2/cb/raw/days_20150101.json"))]
s,r=t._get(f"{t.DATAHUB_HTTPS}/trade_cal",K,{"exchange":"SSE","start_date":"20140101","end_date":"20141231","is_open":"1"},retries=3)
days=sorted(set(days)|set(t._to_df(r).cal_date.astype(str))); days=[d for d in days if d<="20260630"]
def one(d):
    fn=D+d+".parquet"
    if os.path.exists(fn): return
    out=[];off=0
    while True:
        x=call(trade_date=d,offset=off,limit=5000); out.append(x)
        if len(x)<5000: break
        off+=5000
    pd.concat(out).drop_duplicates().to_parquet(fn)
with ThreadPoolExecutor(2) as ex:
    for i,_ in enumerate(ex.map(lambda d: (one(d) if True else None),days)):
        if i%200==0: print(i,len(days),time.strftime("%H:%M"),flush=True)
print("DONE",flush=True)
