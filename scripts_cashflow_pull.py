import glob,os,sys,pandas as pd,concurrent.futures as cf
sys.path.insert(0,'.')
from quantlab.data_sources.tushare_proxy import df
F='ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,update_flag,n_cashflow_act,net_profit'
OUT='data/v2/tushare_raw/cashflow'
def get(code,s,e):
    for src in ('datahub','datahub','relay'):
        try:
            d=df('cashflow',source=src,ts_code=code,fields=F,start_date=s,end_date=e)
            if len(d) or src=='relay': return d
        except Exception as ex: err=ex
    return pd.DataFrame()
def win(code,s,e,depth=0):
    d=get(code,s,e)
    if len(d)>=100 and depth<5:
        y0,y1=int(s[:4]),int(e[:4])
        if y1>y0:
            m=(y0+y1)//2
            return pd.concat([win(code,s,f'{m}1231',depth+1),win(code,f'{m+1}0101',e,depth+1)])
    return d
def one(f):
    b=os.path.basename(f); o=f'{OUT}/{b}'
    if os.path.exists(o): return b,'skip',0
    code=b[:-8].replace('_','.')
    d=win(code,'20150101','20261231').drop_duplicates()
    for c in ('n_cashflow_act','net_profit'):
        if c in d: d[c]=pd.to_numeric(d[c],errors='coerce')
    for c in d.columns:
        if c not in ('n_cashflow_act','net_profit'): d[c]=d[c].astype(str)
    d.to_parquet(o); return b,'ok',len(d)
fs=sorted(glob.glob('data/v2/tushare_raw/income/*.parquet'))
n=0
with cf.ThreadPoolExecutor(16) as ex:
    for fut in cf.as_completed([ex.submit(one,f) for f in fs]):
        n+=1
        try: r=fut.result()
        except Exception as e: r=('ERR',str(e)[:120])
        if n%250==0 or r[0]=='ERR': print(n,r,flush=True)
print('DONE',n)
