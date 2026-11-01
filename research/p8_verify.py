import pandas as pd, numpy as np, json, glob, os, resource
ROOT='/workspace/QuantLab'; OUT=ROOT+'/output/alpha/P8_EVENTS_MIDLARGE_SEALED'
a=pd.read_parquet(ROOT+'/data/v2/events/announcements_classified_pit.parquet',columns=['instrument','event_type','subtype','polarity','ann_date','source','classifier_version','available_at'])
r=dict(rows=len(a),codes=int(a.instrument.nunique()),ann_min=a.ann_date.min(),ann_max=a.ann_date.max(),
 classifier=a.classifier_version.value_counts().to_dict(),
 avail_after_ann=float((a.available_at.dt.tz_localize(None).dt.normalize()>=pd.to_datetime(a.ann_date)).mean()))
r['subtype']=a.subtype.value_counts().to_dict(); r['event_type']=a.event_type.value_counts().to_dict()
r['polarity_by_subtype']=a[a.subtype.notna()].groupby('subtype').polarity.agg(lambda s:s.value_counts().to_dict()).to_dict()
r['buyback_event_type_by_subtype']=a[a.subtype.notna()].groupby(['subtype','event_type']).size().reset_index().values.tolist()
# universe
iw=pd.read_parquet(ROOT+'/data/v2/index_members/index_weight_csi300_500_1000.parquet',columns=['index_code','con_code','trade_date'])
iw=iw[iw.index_code.isin(['000300.SH','000905.SH'])]; iw['snap']=pd.to_datetime(iw.trade_date)
hist=set(iw.con_code); codes=set(a.instrument)
r['hist_members']=len(hist); r['hist_members_with_any_ann']=len(hist&codes)
r['hist_members_with_ann_2020plus']=len(hist&set(a[a.ann_date>='20200101'].instrument))
a['ym']=a.ann_date.str[:6]; has=a.groupby('ym').instrument.agg(set)
snaps=sorted(iw.snap.unique()); memb={s:set(g.con_code) for s,g in iw.groupby('snap')}
cov=[]
for ym in pd.period_range('2018-01','2024-05',freq='M'):
    st=ym.start_time; sn=[s for s in snaps if s<=st] or [snaps[0]]
    U=memb[sn[-1]]; h=has.get(ym.strftime('%Y%m'),set())
    cov.append(dict(month=str(ym),n_univ=len(U),covered=len(U&h),cov=len(U&h)/len(U)))
C=pd.DataFrame(cov); C.to_csv(OUT+'/verify_monthly_coverage.csv',index=False)
c2=C[C.month>='2020-01']
r['cov_2020_2024_mean']=float(c2['cov'].mean()); r['cov_min']=float(c2['cov'].min()); r['cov_min_month']=c2.loc[c2['cov'].idxmin(),'month']
r['months_ge95']=f"{int((c2['cov']>=.95).sum())}/{len(c2)}"; r['months_ge90']=f"{int((c2['cov']>=.90).sum())}/{len(c2)}"
r['cov_2018_2019_mean']=float(C[C.month<'2020-01']['cov'].mean())
r['months_lt90']=C[C['cov']<.90].month.tolist()
# truncation: tushare anns_d raw days with >=5000 rows
tr=[]
for f in sorted(glob.glob(ROOT+'/data/v2/tushare_raw/anns_d/*.parquet')):
    n=pd.read_parquet(f,columns=[]).shape[0]
    if n>=5000: tr.append((os.path.basename(f)[:8],n))
r['raw_tushare_anns_d_days_ge5000']=tr; r['n_trunc_raw']=len(tr)
pd_=a[a.source=='tushare_anns_d'].groupby('ann_date').size(); r['table_tushare_days_ge5000']=pd_[pd_>=5000].index.tolist()
r['maxrss_MB']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
json.dump(r,open(OUT+'/verify.json','w'),indent=1,default=str); print(json.dumps({k:v for k,v in r.items() if k not in('subtype','event_type')},indent=1,default=str))
