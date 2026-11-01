import glob,json,pandas as pd,numpy as np,datetime as dt
D='data/v2/financials_pit'
def iid(c):
    n,x=c.split('.');return {'SH':'sh','SZ':'sz','BJ':'bj'}[x]+'.'+n
IC=['ts_code','ann_date','f_ann_date','end_date','report_type','comp_type','update_flag','basic_eps','diluted_eps','total_revenue','revenue','operate_profit','total_profit','n_income','n_income_attr_p','minority_gain']
inc=pd.concat([x for x in (pd.read_parquet(f) for f in glob.glob('data/v2/tushare_raw/income/*.parquet')) if 'end_date' in x],ignore_index=True)
inc=inc[[c for c in IC if c in inc]]
for c in IC[7:]: inc[c]=pd.to_numeric(inc[c],errors='coerce')
for c in ['ann_date','f_ann_date','end_date','report_type','update_flag']: inc[c]=inc[c].astype(str).replace({'None':None,'nan':None})
inc=inc.drop_duplicates()
fi=pd.concat([x for x in (pd.read_parquet(f) for f in glob.glob('data/v2/tushare_raw/fina_indicator_v2/*.parquet')) if 'end_date' in x],ignore_index=True)
for c in ['ann_date','end_date','update_flag']: fi[c]=fi[c].astype(str).replace({'None':None,'nan':None})
nums=[c for c in fi.columns if c not in('ts_code','ann_date','end_date','update_flag')]
for c in nums: fi[c]=pd.to_numeric(fi[c],errors='coerce')
fi_all_rows=len(fi)
fi=fi.sort_values(['ts_code','end_date','update_flag','ann_date']).drop_duplicates(['ts_code','end_date'],keep='last')
fi=fi.rename(columns={'ann_date':'fina_ann_date','update_flag':'fina_update_flag'})
t=inc.merge(fi,on=['ts_code','end_date'],how='left')
t['instrument_id']=t.ts_code.map(iid)
a=pd.to_datetime(t.f_ann_date.fillna(t.ann_date),format='%Y%m%d',errors='coerce')
t['available_at']=(a+pd.Timedelta(hours=18)).dt.tz_localize('Asia/Shanghai')
for c in ['ann_date','f_ann_date','end_date','fina_ann_date']: t[c]=pd.to_datetime(t[c],format='%Y%m%d',errors='coerce')
t['net_profit']=t.n_income_attr_p
t['source']='tushare.income+fina_indicator(datahub/pcd)';t['schema']='quantlab.v2.financials_pit_tushare.v1'
t['quality_status']='research';t['promotion_approved']=False
t=t.sort_values(['instrument_id','end_date','available_at','update_flag'])
t.to_parquet(f'{D}/financials_pit_tushare.parquet',index=False)
# coverage gate
sb=pd.read_parquet('data/v2/tushare_raw/stock_basic/L.parquet')
listed=sb[(pd.to_datetime(sb.list_date)<=pd.Timestamp('2026-03-31'))].ts_code.map(iid)
def cov(period):
    p=t[(t.end_date==pd.Timestamp(period))&(t.report_type=='1')]
    g=p.groupby('instrument_id')
    r={'period':period,'listed':int(len(listed))}
    for c in ['net_profit','basic_eps','total_revenue','eps','roe','profit_dedt','bps']:
        ok=g[c].apply(lambda s:s.notna().any()); r[c]=round(float(listed.isin(ok[ok].index).mean()),4)
    return r
covs=[cov('2026-06-30'),cov('2026-03-31'),cov('2025-12-31')]
# EP
mc=pd.read_parquet('data/v2/float_mktcap/float_mktcap_daily_tushare.parquet',columns=['instrument_id','trade_date','float_mktcap'])
cons=t[t.report_type=='1'].copy()
def ep(asof):
    cut=pd.Timestamp(asof).tz_localize('Asia/Shanghai')+pd.Timedelta(hours=23,minutes=59)
    c=cons[cons.available_at<=cut].sort_values(['available_at','update_flag']).drop_duplicates(['instrument_id','end_date'],keep='last')
    c=c[c.net_profit.notna()]
    piv=c.set_index(['instrument_id','end_date']).net_profit
    lat=c.sort_values('end_date').drop_duplicates('instrument_id',keep='last')[['instrument_id','end_date','net_profit','available_at','ann_date']]
    def ttm(r):
        E=r.end_date
        if E.month==12: return r.net_profit
        try: return r.net_profit+piv[(r.instrument_id,pd.Timestamp(E.year-1,12,31))]-piv[(r.instrument_id,E-pd.DateOffset(years=1))]
        except KeyError: return np.nan
    lat['net_profit_ttm']=lat.apply(ttm,axis=1)
    m=mc[mc.trade_date==mc[mc.trade_date<=pd.Timestamp(asof)].trade_date.max()][['instrument_id','float_mktcap']]
    o=lat.merge(m,on='instrument_id',how='left')
    o['ep_latest']=o.net_profit/o.float_mktcap;o['ep_ttm']=o.net_profit_ttm/o.float_mktcap;o['session']=pd.Timestamp(asof)
    o=o.rename(columns={'end_date':'report_period','ann_date':'announced_on'})
    o['source']='financials_pit_tushare';o['quality_status']='research';o['promotion_approved']=False
    o.to_parquet(f'{D}/ep_tushare_asof_{asof.replace("-","")}.parquet',index=False);return o
e1=ep('2026-06-30');e2=ep('2026-10-09')
old=pd.read_parquet(f'{D}/ep_research_asof_20260630.parquet')
x=old.merge(e1,on='instrument_id',suffixes=('_old',''))
s=x[x.ep_sane]
xc={'old_rows':len(old),'old_ep_nonnull':int(old.ep.notna().sum()),'new_rows':len(e1),'new_ep_latest_nonnull':int(e1.ep_latest.notna().sum()),'new_ep_ttm_nonnull':int(e1.ep_ttm.notna().sum()),
 'overlap_both_nonnull':int((x.ep.notna()&x.ep_latest.notna()).sum()),
 'pearson_ep_latest_vs_old(sane)':round(s[['ep','ep_latest']].corr().iloc[0,1],4),'spearman_ep_latest_vs_old':round(s[['ep','ep_latest']].corr('spearman').iloc[0,1],4),
 'spearman_ep_ttm_vs_old':round(s[['ep','ep_ttm']].corr('spearman').iloc[0,1],4),
 'same_report_period_share':round(float((x.report_period_old.astype(str).str[:10]==x.report_period.astype(str).str[:10]).mean()),4),
 'net_profit_exact_match_share(rel<1e-4)':round(float(((x.net_profit_old-x.net_profit).abs()<=1e-4*x.net_profit_old.abs()+1).mean()),4)}
caps=json.load(open('logs/fina_cap.json')) if glob.glob('logs/fina_cap.json') else {}
man={'dataset':'financials_pit_tushare','path':f'/workspace/QuantLab/{D}/financials_pit_tushare.parquet','rows':len(t),'instruments':int(t.instrument_id.nunique()),
 'versions_kept':'all income update_flag/report_type versions; fina_indicator joined as latest per (ts_code,end_date) snapshot (fina has no report_type)',
 'available_at':'coalesce(f_ann_date,ann_date) 18:00 Asia/Shanghai','fina_indicator_raw_rows':fi_all_rows,'coverage_report_type1':covs,'ep_crosscheck_20260630':xc,'truncation':caps,
 'total_equity':'not available (balancesheet not pulled); bps from fina_indicator included',
 'ep_files':[f'{D}/ep_tushare_asof_20260630.parquet',f'{D}/ep_tushare_asof_20261009.parquet'],
 'quality_status':'research','promotion_approved':False,'built_at':dt.datetime.now().isoformat()}
json.dump(man,open(f'{D}/financials_pit_tushare_manifest.json','w'),indent=1,ensure_ascii=False,default=str)
print(json.dumps(man,indent=1,ensure_ascii=False,default=str))
