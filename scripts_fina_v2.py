import glob,os,sys,pandas as pd,concurrent.futures as cf
sys.path.insert(0,'.')
from quantlab.data_sources.tushare_proxy import df
F='ts_code,ann_date,end_date,eps,dt_eps,roe,roe_waa,roe_dt,profit_dedt,netprofit_margin,grossprofit_margin,debt_to_assets,ocf_to_or,bps,update_flag'
OUT='data/v2/tushare_raw/fina_indicator_v2'
def win(code,s,e,depth=0):
    src='datahub'
    try: d=df('fina_indicator',source=src,ts_code=code,fields=F,start_date=s,end_date=e)
    except Exception: d=df('fina_indicator',source='relay',ts_code=code,fields=F,start_date=s,end_date=e)
    if len(d)>=100 and depth<4:
        m=str((int(s[:4])+int(e[:4]))//2)
        return pd.concat([win(code,s,m+'1231',depth+1),win(code,str(int(m)+1)+'0101',e,depth+1)])
    return d
def one(f):
    b=os.path.basename(f); o=f'{OUT}/{b}'
    if os.path.exists(o): return b,'skip',0
    code=b[:-8].replace('_','.')
    src='relay' if hash(code)%2 else 'datahub'
    try: d=df('fina_indicator',source=src,ts_code=code,fields=F)
    except Exception: d=df('fina_indicator',source='datahub' if src=='relay' else 'relay',ts_code=code,fields=F)
    if len(d)>=100:
        mn=str(d.end_date.min()); prev=str(int(mn[:4])-1)+'1231' if mn[4:]=='0331' else mn[:4]+'0101'
        d=pd.concat([d,win(code,'19900101',str(int(mn)-1))]).drop_duplicates()
    for c in d.columns:
        if c not in ('ts_code','ann_date','end_date','update_flag'): d[c]=pd.to_numeric(d[c].replace('',None),errors='coerce')
        else: d[c]=d[c].astype(str)
    d=d.drop_duplicates()
    d.to_parquet(o); return b,'ok',len(d)
fs=sorted(glob.glob('data/v2/tushare_raw/fina_indicator/*.parquet'))
n=0
with cf.ThreadPoolExecutor(24) as ex:
    for fut in cf.as_completed([ex.submit(one,f) for f in fs]):
        n+=1
        try: r=fut.result()
        except Exception as e: r=('ERR',str(e)[:120])
        if n%100==0 or r[0]=='ERR': print(n,r,flush=True)
print('DONE',n)
