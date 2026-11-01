import pandas as pd, numpy as np, json, datetime as dt
f=pd.read_parquet('data/v2/financials_pit/financials_pit_tushare.parquet',columns=['ts_code','instrument_id','end_date','update_flag','available_at','n_income_attr_p'])
f=f[f.n_income_attr_p.notna()&f.end_date.dt.month.isin([3,6,9,12])&(f.end_date.dt.day>=28)]
f=f.sort_values(['ts_code','available_at','update_flag']).drop_duplicates(['ts_code','end_date','available_at'],keep='last')
def ttm(v,E):
    if E.month==12: return v.get(E)
    a=v.get(pd.Timestamp(E.year-1,12,31)); p=v.get(E-pd.DateOffset(years=1)+pd.offsets.MonthEnd(0))
    if a is None or p is None or (E.month!=3 and v.get(E) is None): return None
    return v[E]+a-p
ev=[]
for code,g in f.groupby('ts_code',sort=False):
    v={}; iid=g.instrument_id.iat[0]
    for at,gg in g.groupby('available_at',sort=True):
        for E,x in zip(gg.end_date,gg.n_income_attr_p): v[E]=x
        for E in sorted(v,reverse=True)[:6]:
            t=ttm(v,E)
            if t is not None: ev.append((code,iid,at,E,t)); break
ev=pd.DataFrame(ev,columns=['ts_code','instrument_id','e_available_at','e_end_date','e_ttm'])
ev['cut']=ev.e_available_at.dt.tz_convert('Asia/Shanghai').dt.tz_localize(None)
ev=ev.sort_values('cut')
v=pd.read_parquet('data/v2/valuation/daily_basic_valuation_tushare.parquet',columns=['trade_date','instrument_id','total_mv'])
v=v[v.trade_date>='2018-01-01'].dropna(subset=['total_mv'])
v['cut']=v.trade_date+pd.Timedelta(hours=15)   # visible before close of d
v=v.sort_values('cut')
m=pd.merge_asof(v,ev.drop(columns='ts_code'),on='cut',by='instrument_id',direction='backward')
m['ts_code']=m.instrument_id.str.split('.').map(lambda p:f'{p[1]}.{p[0].upper()}')
m['mv']=m.total_mv   # already yuan in contract table
m['ep']=m.e_ttm/m.mv
m['source']='tushare.income(n_income_attr_p cum->TTM, PIT versions)/daily_basic.total_mv'
m['schema']='quantlab.v2.ep_pit_daily_tushare.v1'
out=m[['trade_date','instrument_id','ts_code','e_ttm','mv','ep','e_end_date','e_available_at','source','schema']].sort_values(['trade_date','instrument_id']).reset_index(drop=True)
out.to_parquet('data/v2/ep/ep_pit_daily_tushare.parquet',index=False)
# acceptance
has=out.ep.notna()
leak=(out.e_available_at.dt.tz_convert('Asia/Shanghai').dt.tz_localize(None)>out.trade_date+pd.Timedelta(hours=15))[has].sum()
cov=out.groupby('trade_date').ep.apply(lambda s:s.notna().mean())
old=pd.read_parquet('data/v2/financials_pit/ep_research_asof_20260630.parquet')
x=out[out.trade_date=='2026-06-30'].merge(old[['instrument_id','ep']],on='instrument_id',suffixes=('','_old')).dropna(subset=['ep','ep_old'])
xs=x[x.ep_old.between(-1,1)]
pe=pd.read_parquet('data/v2/valuation/daily_basic_valuation_tushare.parquet',columns=['trade_date','instrument_id','pe_ttm'])
pe=pe[pe.trade_date.isin(pd.to_datetime(['2018-06-29','2020-06-30','2022-06-30','2024-06-28','2025-06-30','2026-06-30','2026-10-09']))&(pe.pe_ttm>0)]
y=out.merge(pe,on=['trade_date','instrument_id']).dropna(subset=['ep']); y['ip']=1/y.pe_ttm; y=y[y.ep>0]
VSPE={str(d.date()):dict(n=len(g),pearson=float(g.ep.corr(g.ip)),rank=float(g.ep.rank().corr(g.ip.rank())),median_ratio=float((g.ep/g.ip).median())) for d,g in y.groupby('trade_date')}
res=dict(rows=len(out),dates=int(out.trade_date.nunique()),date_min=str(out.trade_date.min().date()),date_max=str(out.trade_date.max().date()),
 instruments=int(out.instrument_id.nunique()),ep_nonnull=int(has.sum()),coverage_overall=float(has.mean()),
 coverage_daily_min=float(cov.min()),coverage_daily_median=float(cov.median()),coverage_last=float(cov.iloc[-1]),
 future_leak_rows=int(leak),no_future_pct=float(1-leak/has.sum()),
 vs_old_20260630=dict(n=len(xs),pearson=float(xs.ep.corr(xs.ep_old)),spearman=float(xs.ep.rank().corr(xs.ep_old.rank())),sign_agree=float((np.sign(xs.ep)==np.sign(xs.ep_old)).mean())),
 vs_daily_basic_inv_pe_ttm=VSPE, ep_median=float(out.ep.median()),built_at=dt.datetime.now().isoformat())
json.dump(res,open('data/v2/ep/ep_pit_daily_tushare_acceptance.json','w'),indent=1,ensure_ascii=False)
print(json.dumps(res,indent=1))
