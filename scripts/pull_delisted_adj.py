import sys,os,pandas as pd,concurrent.futures as cf
sys.path.insert(0,'.')
from quantlab.data_sources.tushare_proxy import df
D=pd.read_parquet('data/v2/tushare_raw/stock_basic/D.parquet')
OUT='data/v2/delisted/raw_adj_factor'
def one(c):
    o=f'{OUT}/{c}.parquet'
    if os.path.exists(o) and os.path.getsize(o)>500: return c,'skip'
    for src in ('datahub','relay','datahub'):
        try:
            x=df('adj_factor',source=src,ts_code=c)
            if len(x): x.to_parquet(o); return c,len(x)
        except Exception: pass
    return c,0
with cf.ThreadPoolExecutor(10) as ex:
    for i,r in enumerate(ex.map(one,D.ts_code.tolist())):
        if i%50==0: print(i,r,flush=True)
print('DONE')
