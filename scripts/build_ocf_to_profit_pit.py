import pandas as pd, numpy as np, glob, json, datetime as dt
TZ='Asia/Shanghai'; SMALL=1e6
cf=pd.concat([pd.read_parquet(p) for p in glob.glob('data/v2/tushare_raw/cashflow/*.parquet')],ignore_index=True)
cf=cf[cf.report_type.astype(str)=='1']
for c in ('ann_date','f_ann_date','end_date'): cf[c]=pd.to_datetime(cf[c].replace({'None':None,'nan':None,'':None}),format='%Y%m%d',errors='coerce')
cf['at']=(cf.f_ann_date.fillna(cf.ann_date)+pd.Timedelta(hours=18)).dt.tz_localize(TZ)
cf=cf.dropna(subset=['at','end_date'])
cf=cf.sort_values(['ts_code','at','update_flag']).drop_duplicates(['ts_code','end_date','at'],keep='last')
inc=pd.read_parquet('data/v2/financials_pit/financials_pit_tushare.parquet',columns=['ts_code','instrument_id','end_date','update_flag','available_at','n_income','n_income_attr_p'])
inc=inc.rename(columns={'available_at':'at'}).sort_values(['ts_code','at','update_flag']).drop_duplicates(['ts_code','end_date','at'],keep='last')
iid=inc.drop_duplicates('ts_code').set_index('ts_code').instrument_id
e=pd.concat([cf[['ts_code','end_date','at','n_cashflow_act','update_flag']].assign(k='cf'),
             inc[['ts_code','end_date','at','n_income','n_income_attr_p','update_flag']].assign(k='inc')],ignore_index=True)
e=e[e.end_date>='2014-01-01'].sort_values(['ts_code','at','k'])
ver=[];daily_ev=[]
for code,g in e.groupby('ts_code',sort=False):
    st={}
    for at,gg in g.groupby('at',sort=True):
        touched=set()
        for r in gg.itertuples():
            s=st.setdefault(r.end_date,{'cf':None,'cfat':None,'np':None,'npa':None,'npat':None})
            if r.k=='cf':
                if pd.notna(r.n_cashflow_act): s['cf']=r.n_cashflow_act; s['cfat']=at
            else:
                s['np']=r.n_income; s['npa']=r.n_income_attr_p; s['npat']=at
            touched.add(r.end_date)
        for E in touched:
            s=st[E]
            if s['cf'] is not None and s['np'] is not None:
                ver.append((code,E,s['cf'],s['np'],s['npa'],s['cfat'],s['npat'],at))
        full=[E for E,s in st.items() if s['cf'] is not None and s['np'] is not None]
        if full:
            E=max(full); s=st[E]; daily_ev.append((code,E,s['cf'],s['np'],s['npa'],at))
cols=['ts_code','end_date','n_cashflow_act','net_profit','n_income_attr_p']
v=pd.DataFrame(ver,columns=cols+['cf_available_at','np_available_at','available_at'])
def fin(d):
    d['instrument_id']=d.ts_code.map(iid)
    d['denom_small']=d.net_profit.abs()<SMALL
    d['np_negative']=d.net_profit<0
    d['ocf_to_profit']=np.where(d.denom_small,np.nan,d.n_cashflow_act/d.net_profit)
    d['ocf_to_profit_attr']=np.where(d.n_income_attr_p.abs()<SMALL,np.nan,d.n_cashflow_act/d.n_income_attr_p)
    d['period_basis']='YTD_cumulative'
    d['source']='tushare.cashflow.n_cashflow_act / tushare.income.n_income (datahub/pcd)'
    d['schema']='quantlab.v2.ocf_to_profit_pit_tushare.v1'
    return d
v=fin(v).sort_values(['instrument_id','end_date','available_at']).reset_index(drop=True)
v.to_parquet('data/v2/financials_pit/ocf_to_profit_pit_tushare.parquet',index=False)
de=fin(pd.DataFrame(daily_ev,columns=cols+['available_at'])).dropna(subset=['instrument_id'])
de['cut']=de.available_at.dt.tz_localize(None) if de.available_at.dt.tz is None else de.available_at.dt.tz_convert(TZ).dt.tz_localize(None)
val=pd.read_parquet('data/v2/valuation/daily_basic_valuation_tushare.parquet',columns=['trade_date','instrument_id'])
val=val[val.trade_date>='2018-01-01'].copy(); val['cut']=val.trade_date+pd.Timedelta(hours=15)
dd=pd.merge_asof(val.sort_values('cut'),de.drop(columns=['instrument_id']).assign(instrument_id=de.instrument_id).sort_values('cut'),on='cut',by='instrument_id',direction='backward')
dd=dd.drop(columns='cut').rename(columns={'end_date':'e_end_date','available_at':'e_available_at'}).sort_values(['trade_date','instrument_id']).reset_index(drop=True)
dd.to_parquet('data/v2/financials_pit/ocf_to_profit_pit_daily_tushare.parquet',index=False)
# acceptance
has=dd.ocf_to_profit.notna()
leak=int(((dd.e_available_at.dt.tz_convert(TZ).dt.tz_localize(None))>dd.trade_date+pd.Timedelta(hours=15)).sum())
lat=v[v.end_date=='2026-06-30'].drop_duplicates('instrument_id',keep='last')
listed=pd.read_parquet('data/v2/valuation/daily_basic_valuation_tushare.parquet',columns=['trade_date','instrument_id']);listed=set(listed[listed.trade_date=='2026-06-30'].instrument_id)
lg=pd.read_parquet('data/v2/financials_pit/financials_available_at_latest_per_key.parquet')
lg=lg[lg.metric.astype(str)=='ocf_to_profit'][['instrument_id','report_period','value']]
lg['report_period']=pd.to_datetime(lg.report_period)
lv=v.sort_values('available_at').drop_duplicates(['instrument_id','end_date'],keep='last')
x=lv.merge(lg,left_on=['instrument_id','end_date'],right_on=['instrument_id','report_period']).dropna(subset=['ocf_to_profit','value'])
rel=(x.ocf_to_profit-x.value).abs()/x.value.abs().clip(lower=1e-9)
xs=x[x.value.between(-20,20)&x.ocf_to_profit.between(-20,20)]
res=dict(versions_rows=len(v),instruments=int(v.instrument_id.nunique()),end_date_min=str(v.end_date.min().date()),end_date_max=str(v.end_date.max().date()),
 latest_period_20260630_cover_listed=float(len(set(lat.dropna(subset=['ocf_to_profit']).instrument_id)&listed)/len(listed)),listed_n=len(listed),
 denom_small_share=float(v.denom_small.mean()),np_negative_share=float(v.np_negative.mean()),
 ocf_to_profit_quantiles={str(q):float(v.ocf_to_profit.quantile(q)) for q in (.01,.25,.5,.75,.99)},
 daily_rows=len(dd),daily_dates=int(dd.trade_date.nunique()),daily_coverage=float(has.mean()),daily_future_leak_rows=leak,
 vs_legacy=dict(n=len(x),legacy_instruments=int(lg.instrument_id.nunique()),within_1pct=float((rel<.01).mean()),within_5pct=float((rel<.05).mean()),sign_agree=float((np.sign(x.ocf_to_profit)==np.sign(x.value)).mean()),pearson_clip20=float(xs.ocf_to_profit.corr(xs.value)),rank=float(x.ocf_to_profit.rank().corr(x.value.rank()))),
 built_at=dt.datetime.now().isoformat())
json.dump(res,open('data/v2/financials_pit/ocf_to_profit_pit_tushare_acceptance.json','w'),indent=1)
print(json.dumps(res,indent=1))
