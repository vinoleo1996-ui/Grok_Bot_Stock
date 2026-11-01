# V3 A2 sealed run, prereg docs/prereg/V3_A2_INDEX_REBAL_MIGRATION.md (amendment A). Research only; each arm once.
import pandas as pd, numpy as np, glob, os, json, hashlib, resource, sys
from math import erf, sqrt
ROOT='/workspace/QuantLab'; OUT=ROOT+'/output/alpha/V3_A2_SEALED'; sys.path.insert(0,ROOT)
from quantlab.platform.execution import sqrt_impact_cost
PRE=ROOT+'/docs/prereg/V3_A2_INDEX_REBAL_MIGRATION.md'; PSHA=hashlib.sha256(open(PRE,'rb').read()).hexdigest()
mem=lambda: resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
SEAL_END=pd.Timestamp('2024-05-31')
cv=lambda c: c.str[-2:].str.lower()+'.'+c.str[:6]
ev=pd.read_parquet(ROOT+'/data/v2/index_members/index_member_events.parquet'); ev=ev[ev.review.notna()]; ev['inst']=cv(ev.con_code)
cal=pd.read_parquet(ROOT+'/data/v2/index_members/csi_review_calendar.parquet').set_index('review')
iw=pd.read_parquet(ROOT+'/data/v2/index_members/index_weight_csi300_500_1000.parquet',columns=['index_code','con_code','trade_date'])
iw=iw[iw.index_code.isin(['000300.SH','000905.SH'])]; iw['inst']=cv(iw.con_code); iw['snap']=pd.to_datetime(iw.trade_date)
names=sorted(set(iw.inst)|set(ev[ev.index_code.isin(['000300.SH','000905.SH'])].inst))
D0=ROOT+'/data/local_market/1c85fd9aceaa03c3c4863bec/panels'; fr=[]
for n in names:
    f=f'{D0}/{n}.parquet'
    if not os.path.exists(f): continue
    d=pd.read_parquet(f,columns=['open','close','amount','factor','tradestatus'])
    d.index=pd.to_datetime(d.index); d=d[d.index>='2017-11-01']
    d=pd.DataFrame({'oa':(d.open*d.factor).astype('float32'),'ca':(d.close*d.factor).astype('float32'),'amt':d.amount.astype('float32'),'ts':d.tradestatus.astype('float32')},index=d.index); d['inst']=n; fr.append(d)
p=pd.concat(fr); del fr
O=p.pivot_table(index=p.index,columns='inst',values='oa'); C=p.pivot_table(index=p.index,columns='inst',values='ca'); A=p.pivot_table(index=p.index,columns='inst',values='amt'); del p
C=C.ffill(); O=O.fillna(C); R=C.pct_change(); SIG=R.shift(1).rolling(20,min_periods=10).std(); ADV=A.shift(1).rolling(20,min_periods=10).mean()
D=C.index; print('panel',C.shape,'mem',mem())
fm=pd.read_parquet(ROOT+'/data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet',columns=['instrument_id','trade_date','float_mktcap'])
fm=fm[fm.instrument_id.isin(names)]; fm['trade_date']=pd.to_datetime(fm.trade_date); FM=fm.pivot_table(index='trade_date',columns='instrument_id',values='float_mktcap'); del fm
snaps=sorted(iw.snap.unique())
rows=[]
for rv,c in cal.iterrows():
    ann=pd.Timestamp(c.ann_date); eff=pd.Timestamp(c.effective_date)
    i0=D.searchsorted(ann,side='right'); ie=D.searchsorted(eff)
    if i0>=len(D) or ie>=len(D): continue
    ent=D[i0]; ex=D[ie]; exm1=D[ie-1]
    e=ev[ev.review==rv]; s=lambda ix,k: set(e[(e.index_code==ix)&(e.event==k)].inst)
    arms={'A2_T1_MIGRATE_IN_300':s('000300.SH','in')&s('000905.SH','out'),'A2_T2_MIGRATE_OUT_300':s('000300.SH','out')&s('000905.SH','in')}
    sn=[x for x in snaps if x<ent][-1]; bench=sorted(set(iw[iw.snap==sn].inst)&set(C.columns))
    for ex_lab,xd in [('eff',ex),('eff_m1',exm1)]:
        br=(C.loc[xd,bench]/O.loc[ent,bench]-1).mean()
        for arm,S in arms.items():
            for n in sorted(S&set(C.columns)):
                r=C.loc[xd,n]/O.loc[ent,n]-1
                if not np.isfinite(r): continue
                rows.append(dict(review=rv,ann_src=c.ann_date_source,eff_src=c.effective_source,entry=ent,exit=xd,exit_rule=ex_lab,arm=arm,inst=n,ret=r,bench=br,xs=r-br,
                    sig_in=SIG.loc[ent,n],adv_in=ADV.loc[ent,n],sig_out=SIG.loc[xd,n],adv_out=ADV.loc[xd,n],
                    demand_proxy=FM[n].loc[:D[i0-1]].iloc[-1]/ADV.loc[ent,n] if n in FM and ADV.loc[ent,n]>0 else np.nan,stamp=0.001 if xd<pd.Timestamp('2023-08-28') else 0.0005))
E=pd.DataFrame(rows); E['window']=np.where(E.exit<=SEAL_END,'sealed','confirm')
for bp in (25,50,100): E[f'net_flat{bp}']=E['xs']-2*bp*1e-4
nby=E.groupby(['review','arm','exit_rule']).inst.transform('count')
for cap,lab in [(5e7,'imp5e7'),(2e8,'imp2e8')]:
    tv=cap/nby; cost=(sqrt_impact_cost(tv,E.adv_in,E.sig_in)+sqrt_impact_cost(tv,E.adv_out,E.sig_out)+2*np.maximum(2.5e-4*tv,5)+E.stamp*tv)/tv
    E[f'net_{lab}']=E['xs']-cost
E.to_csv(OUT+'/events.csv',index=False)
CK=['xs','net_flat25','net_flat50','net_flat100','net_imp5e7','net_imp2e8']
B=E.groupby(['window','exit_rule','arm','review'])[CK].mean().reset_index(); B['n']=E.groupby(['window','exit_rule','arm','review']).size().values
B.to_csv(OUT+'/review_baskets.csv',index=False)
res=[]
for (w,xr,arm),g in B.groupby(['window','exit_rule','arm']):
    sgn=1 if 'T1' in arm else -1
    for ck in CK:
        x=g[ck]*sgn; k=len(x); t=float(x.mean()/(x.std(ddof=1)/sqrt(k))) if k>2 and x.std()>0 else np.nan
        res.append(dict(window=w,exit_rule=xr,arm=arm,cost=ck,reviews=k,events=int(g.n.sum()),mean_signed=float(x.mean()),pos_frac=float((x>0).mean()),t=t,p_one=1-0.5*(1+erf(t/sqrt(2))) if np.isfinite(t) else np.nan,
            ann_contrib=float(x.groupby(g.review.str[:4]).sum().mean())))
S=pd.DataFrame(res); S.to_csv(OUT+'/summary.csv',index=False)
# demand proxy tercile (report-only)
q=E[(E.window=='sealed')&(E.exit_rule=='eff')].copy(); q['terc']=q.groupby('arm').demand_proxy.transform(lambda s:pd.qcut(s.rank(method='first'),3,labels=False))
q.groupby(['arm','terc'])['xs'].agg(['mean','count']).to_csv(OUT+'/demand_proxy_terciles.csv')
yr=q.groupby(['arm',q.review.str[:4]])['xs'].mean().unstack(0); yr.to_csv(OUT+'/by_year_sealed.csv')
json.dump(dict(prereg_sha256=PSHA,promotion_approved=False,research_only=True,maxrss_MB=mem()),open(OUT+'/results.json','w'),indent=1)
print(S[S.cost.isin(['xs','net_flat25','net_imp5e7'])].to_string()); print(yr.to_string()); print(open(OUT+'/demand_proxy_terciles.csv').read()); print('maxrss',mem())
