import sys,os,pandas as pd,concurrent.futures as cf
sys.path.insert(0,'.')
from quantlab.data_sources.tushare_proxy import df
D=pd.read_parquet('data/v2/tushare_raw/stock_basic/D.parquet')
def get(api,c,s,e):
    for src in ('datahub','datahub','relay'):
        try:
            x=df(api,source=src,ts_code=c,start_date=s,end_date=e)
            if len(x): return x
        except Exception: pass
    return pd.DataFrame()
def one(r):
    out={}
    for api in ('daily','daily_basic'):
        o=f'data/v2/delisted/raw_{api}/{r.ts_code}.parquet'
        if os.path.exists(o): continue
        y0=int(str(r.list_date)[:4]) if r.list_date else 1990; y1=int(str(r.delist_date)[:4])
        parts=[get(api,r.ts_code,f'{y}0101',f'{min(y+2,y1)}1231') for y in range(y0,y1+1,3)]
        x=pd.concat([p for p in parts if len(p)],ignore_index=True) if any(len(p) for p in parts) else pd.DataFrame()
        x=x.drop_duplicates(); x.to_parquet(o); out[api]=len(x)
    return r.ts_code,out
with cf.ThreadPoolExecutor(8) as ex:
    for i,res in enumerate(ex.map(one,D.itertuples())):
        if i%50==0: print(i,res,flush=True)
print('DONE')
