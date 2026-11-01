import sys,json,resource;sys.path.insert(0,'.')
import pandas as pd,numpy as np
import research.g1g5_capacity_adv_weights as C
import research.adj_price as A
uni=C.select_mid_large_topn_light(top_n=C.DEFAULT_SCORE_N); U=[i for i in uni['instruments'] if i not in C.HARD_EXCLUDE]
rebal=C.month_end_sessions(C.WEIGHT_START,C.WEIGHT_END)
d1=C._preload_d1_adv(U,rebal)
# keep trade_date too
import pyarrow.parquet as pq
raw=pd.read_parquet(C.D1_VALUATION,columns=['ts_code','trade_date','turnover_rate','float_mktcap','available_at'],filters=[('ts_code','in',U)])
raw['td']=pd.to_datetime(raw.trade_date).dt.tz_localize(None).dt.normalize(); raw['av']=pd.to_datetime(raw.available_at).dt.tz_localize(None)
raw=raw[(raw.td>='2023-11-01')&raw.av.notna()]
F=A._factors()
w=pd.read_parquet('output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet',columns=['date','instrument','target_weight'])
w['date']=w['date'].astype(str).str[:10]
sw=C._load_sw_members()
rows=[];rank_changes=[];held_aff=[]
for s in rebal:
    S=pd.Timestamp(s)
    sub=raw[raw.av.dt.normalize()<=S].sort_values('av').groupby('ts_code').tail(1)
    sub=sub[(sub.float_mktcap>0)&(sub.turnover_rate>=0)]
    sub['adv']=sub.float_mktcap*sub.turnover_rate/100
    # ex-date flag on snapshot date: factor change vs previous factor day
    def ratio(r):
        if r.ts_code not in F.columns: return 1.0
        f=F[r.ts_code].dropna(); f=f[f.index<=r.td]
        return float(f.iloc[-1]/f.iloc[-2]) if len(f)>=2 and f.index[-1]==r.td else 1.0
    sub['fr']=sub.apply(ratio,axis=1)
    sub['adv_sh']=sub.adv*sub.fr
    sub['sw']=[C.sw_code_on(i,S,sw) for i in sub.ts_code]; sub=sub[sub.sw.notna()]
    for col in ('adv','adv_sh'):
        l=np.log(sub[col]); sub['z_'+col]=l-l.groupby(sub.sw).transform('mean')
    sub['r0']=sub.z_adv.rank(ascending=False); sub['r1']=sub.z_adv_sh.rank(ascending=False)
    aff=sub[sub.fr!=1.0]
    hold=w[(w.date==s)&(w.target_weight>0)&(w.instrument!='510300.SH')].set_index('instrument').target_weight
    for r in aff.itertuples():
        rank_changes.append(dict(session=s,inst=r.ts_code,snap=str(r.td.date()),fr=round(r.fr,4),r0=r.r0,r1=r.r1,top25_0=r.r0<=25,top25_1=r.r1<=25,w=float(hold.get(r.ts_code,0))))
    rows.append(dict(session=s,n=len(sub),n_aff=len(aff),w_aff=float(hold.reindex(aff.ts_code).fillna(0).sum()),
                     top25_set_change=int(len(set(sub[sub.r0<=25].ts_code)^set(sub[sub.r1<=25].ts_code))//2)))
R=pd.DataFrame(rows);RC=pd.DataFrame(rank_changes)
print(R.to_string());print(RC.to_string() if len(RC) else 'no affected')
out=dict(n_rebal=len(R),n_pairs=int(R.n.sum()),n_aff_pairs=int(R.n_aff.sum()),n_aff_names=int(RC.inst.nunique()) if len(RC) else 0,
 sessions_with_aff=int((R.n_aff>0).sum()),max_w_aff=float(R.w_aff.max()),mean_w_aff=float(R.w_aff.mean()),
 top25_changes=int(R.top25_set_change.sum()),max_abs_rank_change=float((RC.r1-RC.r0).abs().max()) if len(RC) else 0,
 peak_rss_mb=round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,1))
print(json.dumps(out));RC.to_csv('output/ai_factory/capacity_adv_price_basis_diag_pairs.csv',index=False);json.dump(out,open('output/ai_factory/capacity_adv_price_basis_diag.json','w'))
