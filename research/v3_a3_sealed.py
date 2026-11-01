# V3 A3 sealed run, prereg docs/prereg/V3_A3_LOCKUP_SUPPLY_AVOID.md. Research only; each arm once. promotion_approved=false.
import pandas as pd, numpy as np, os, json, hashlib, resource, sys
from math import erf, sqrt
ROOT='/workspace/QuantLab'; OUT=ROOT+'/output/alpha/V3_A3_SEALED'; sys.path.insert(0,ROOT)
from quantlab.platform.execution import sqrt_impact_cost
PRE=ROOT+'/docs/prereg/V3_A3_LOCKUP_SUPPLY_AVOID.md'; PSHA=hashlib.sha256(open(PRE,'rb').read()).hexdigest()
assert PSHA.startswith('14ea939e'), PSHA
mem=lambda: resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
SEAL_END=pd.Timestamp('2024-05-31'); END=pd.Timestamp('2026-10-08')
cv=lambda c: c.str[-2:].str.lower()+'.'+c.str[:6]
iw=pd.read_parquet(ROOT+'/data/v2/index_members/index_weight_csi300_500_1000.parquet',columns=['index_code','con_code','trade_date'])
iw=iw[iw.index_code.isin(['000300.SH','000905.SH'])]; iw['inst']=cv(iw.con_code); iw['snap']=pd.to_datetime(iw.trade_date)
names=sorted(set(iw.inst))
D0=ROOT+'/data/local_market/1c85fd9aceaa03c3c4863bec/panels'; fr=[]
for n in names:
    f=f'{D0}/{n}.parquet'
    if not os.path.exists(f): continue
    d=pd.read_parquet(f,columns=['open','close','amount','factor','tradestatus','is_st_at_open','limit_up','limit_down'])
    d.index=pd.to_datetime(d.index); d=d[(d.index>='2017-10-01')&(d.index<=END)]
    lim=((d.open>=d.limit_up-1e-3)|(d.open<=d.limit_down+1e-3)).fillna(False)
    ok=(d.tradestatus==1)&(d.is_st_at_open.fillna(0)==0)&(~lim)&d.open.notna()&(d.open>0)
    fr.append(pd.DataFrame({'oa':(d.open*d.factor).astype('float32'),'ca':(d.close*d.factor).astype('float32'),'cr':d.close.astype('float32'),
        'amt':d.amount.astype('float32'),'ok':ok.astype('float32'),'inst':n},index=d.index))
p=pd.concat(fr); del fr
pv=lambda v: p.pivot_table(index=p.index,columns='inst',values=v)
O=pv('oa');C=pv('ca');CR=pv('cr');A=pv('amt');OK=pv('ok').fillna(0)>0; del p
C=C.ffill(); O=O.fillna(C); CR=CR.ffill(); D=C.index; cols=C.columns
RO=(O.shift(-1)/O-1).fillna(0).clip(-0.9,5)   # open t -> open t+1
RC=C.pct_change()
SIG=RC.shift(1).rolling(20,min_periods=10).std(); ADV=A.shift(1).rolling(20,min_periods=10).mean()
fm=pd.read_parquet(ROOT+'/data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet',columns=['instrument_id','trade_date','float_mktcap'])
fm=fm[fm.instrument_id.isin(cols)]; fm['trade_date']=pd.to_datetime(fm.trade_date)
FM=fm.pivot_table(index='trade_date',columns='instrument_id',values='float_mktcap').reindex(D).ffill().reindex(columns=cols); del fm
print('panel',C.shape,'mem',mem(),flush=True)
# ---- share_float
sf=pd.read_parquet(ROOT+'/data/v2/share_float/share_float_2018plus.parquet',columns=['ts_code','ann_date','float_date','float_share'])
sf['inst']=cv(sf.ts_code); sf=sf[sf.inst.isin(cols)].copy()
sf['ann']=pd.to_datetime(sf.ann_date,errors='coerce'); sf['fd']=pd.to_datetime(sf.float_date,errors='coerce'); sf=sf.dropna(subset=['fd'])
sf=sf.groupby(['inst','fd'],as_index=False).agg(sh=('float_share','sum'),ann=('ann','max'),ann_min=('ann','min'))
# trading-day index of float date (next trading day if non-trading)
sf['fi']=D.searchsorted(sf.fd); sf=sf[sf.fi<len(D)]
sf['ai']=D.searchsorted(sf.ann,side='right')  # first trading day strictly after ann -> available_at 09:00 that day
sf.loc[sf.ann.isna(),'ai']=10**9
ci={c:i for i,c in enumerate(cols)}; sf['ci']=sf.inst.map(ci)
CRv=CR.values; FMv=FM.values  # float_mktcap in CNY (verified: sample 2.3e8 for small BJ name)
# unit check: median (cr*float_share)/float_mktcap
def strength(t,ev):
    # ev rows with fi in [t+1,t+20] and ai<=t ; S=sh*CR[t-1]/FM[t-1]
    m=(ev.fi>=t+1)&(ev.fi<=t+20)&(ev.ai<=t); e=ev[m]
    S=np.zeros(len(cols)); 
    if len(e):
        v=e.sh.values*CRv[t-1,e.ci.values]/FMv[t-1,e.ci.values]
        np.add.at(S,e.ci.values,np.nan_to_num(v))
    return S,e
# units sanity
smp=sf.sample(2000,random_state=0); smp=smp[(smp.fi>1)]
ratio=np.nanmedian(smp.sh.values*CRv[smp.fi.values-1,smp.ci.values]/(FM.values[smp.fi.values-1,smp.ci.values]))
print('median sh*px/float_mktcap_raw',ratio,flush=True)
# ---- rebal schedule
mon=pd.Series(D,index=D).groupby([D.year,D.month]).first().values
mon=[pd.Timestamp(x) for x in mon if pd.Timestamp(x)>=pd.Timestamp('2018-02-01')]
snaps=sorted(iw.snap.unique()); memb={s:set(g.inst) for s,g in iw.groupby('snap')}
evs={'real':sf[['ci','fi','ai','sh']].copy()}
pl=sf[['ci','fi','ai','sh']].copy(); pl['fi']=pl.fi-250; pl['ai']=np.where(pl.ai<10**8,pl.ai-250,pl.ai); evs['placebo']=pl[pl.fi>=1]
reb={}; LG=[]
for d in mon:
    t=D.get_loc(d); sn=[x for x in snaps if x<d]
    if not sn: continue
    U=np.array([ci[x] for x in memb[sn[-1]] if x in ci]); U=U[OK.values[t,U]]
    Sr,er=strength(t,evs['real']); Sp,_=strength(t,evs['placebo'])
    reb[t]=dict(U=U,S=Sr,Sp=Sp,ev=er)
    for c in U:
        if Sr[c]>0: LG.append((d,cols[c],Sr[c]))
print('rebals',len(reb),flush=True)
# ---- simulator
CAP=[5e7,2e8]; STAMP=lambda t: 0.001 if D[t]<pd.Timestamp('2023-08-28') else 0.0005
ROv=RO.values; OKv=OK.values; SIGv=SIG.values; ADVv=ADV.values
def targets(arm,t,r):
    U=r['U']; w=np.zeros(len(cols))
    if arm=='BASE': w[U]=1
    elif arm in('T1','T2'): k=U[r['S'][U]<0.05]; w[k]=1
    elif arm=='T4': k=U[r['Sp'][U]<0.05]; w[k]=1
    elif arm=='T3': w[U]=1/(1+10*r['S'][U])
    return w/w.sum()
def sim(arm):
    w=np.zeros(len(cols)); rows=[]; reentry={}
    for t in range(len(D)-1):
        tr=None
        if t in reb:
            r=reb[t]; tgt=targets(arm,t,r); reentry={}
            if arm=='T2':
                U=r['U']; N=len(U); e=r['ev']
                for c in U[r['S'][U]>=0.05]:
                    fis=e[e.ci==c].fi.values; ti=int(fis.max())+20
                    reentry.setdefault(ti,[]).append((c,1/N))
            tr=tgt
        elif arm=='T2' and t in reentry and w.sum()>0:
            add=[(c,q) for c,q in reentry[t] if OKv[t,c]]
            if add:
                tgt=w.copy(); tot=sum(q for _,q in add); tgt*= (1-tot)
                for c,q in add: tgt[c]+=q
                tr=tgt
        if tr is None and not w.any(): continue
        dw=np.zeros(len(cols)) if tr is None else tr-w
        if tr is not None: w=tr.copy()
        g=float(w@ROv[t]); turn=float(np.abs(dw).sum())
        row=dict(date=D[t],gross=g,turn=turn)
        if turn>0:
            nz=np.nonzero(dw)[0]; sells=-dw[nz].clip(max=0).sum()
            for cap in CAP:
                tv=cap*np.abs(dw[nz]); imp=sqrt_impact_cost(tv,ADVv[t,nz],SIGv[t,nz]).sum()
                row[f'c{cap:.0e}']=(imp+np.maximum(2.5e-4*tv,5).sum())/cap+STAMP(t)*sells
        else:
            for cap in CAP: row[f'c{cap:.0e}']=0.0
        rows.append(row)
        w=w*(1+ROv[t]); s=w.sum(); w=w/s if s>0 else w
    df=pd.DataFrame(rows).set_index('date')
    for bp in(25,50,100): df[f'flat{bp}']=df.gross-bp*1e-4*df.turn
    df['imp5e7']=df.gross-df['c5e+07']; df['imp2e8']=df.gross-df['c2e+08']
    return df
R={a:sim(a) for a in ['BASE','T1','T2','T3','T4']}; print('sim done mem',mem(),flush=True)
CK=['gross','flat25','flat50','flat100','imp5e7','imp2e8']
def mdd(x): v=(1+x).cumprod(); return float((v/v.cummax()-1).min())
res=[]; yrs=[]
for a in ['T1','T2','T3','T4']:
    for win,lo,hi in [('sealed','2018-01-01',SEAL_END),('confirm','2024-06-01',END)]:
        b=R['BASE'].loc[lo:hi]; x=R[a].loc[lo:hi]
        for ck in CK:
            inc=x[ck]-b[ck]; n=len(inc); t=float(inc.mean()/(inc.std(ddof=1)/sqrt(n)))
            res.append(dict(arm=a,window=win,cost=ck,days=n,inc_ann=float(inc.mean()*244),t=t,p_one=1-0.5*(1+erf(t/sqrt(2))),
              arm_ann=float(x[ck].mean()*244),base_ann=float(b[ck].mean()*244),arm_mdd=mdd(x[ck]),base_mdd=mdd(b[ck]),overlay_mdd=mdd(inc),
              turn_ann=float(x.turn.sum()/n*244),base_turn_ann=float(b.turn.sum()/n*244)))
            if ck=='flat25' and win=='sealed':
                for y,g in inc.groupby(inc.index.year): yrs.append(dict(arm=a,year=y,inc=float(g.sum())))
S=pd.DataFrame(res)
# BY on T1-T3 sealed flat25
m=(S.window=='sealed')&(S.cost=='flat25')&S.arm.isin(['T1','T2','T3'])
p=S.loc[m,'p_one'].values; k=len(p); cm=sum(1/i for i in range(1,k+1)); o=np.argsort(p); q=np.empty(k)
q[o]=np.minimum.accumulate((p[o]*k*cm/np.arange(1,k+1))[::-1])[::-1]; S.loc[m,'BY_q']=np.minimum(q,1)
S.to_csv(OUT+'/summary.csv',index=False); Y=pd.DataFrame(yrs).pivot(index='year',columns='arm',values='inc'); Y.to_csv(OUT+'/by_year_sealed_flat25.csv')
for a in R: R[a].to_csv(OUT+f'/daily_{a}.csv')
# ---- event study S>=5% in universe, float_date [-20,+20] close-to-close vs EW universe
ER=[]; RCv=RC.values
for t,r in reb.items():
    pass
evl=[]
for t,r in reb.items():
    U=r['U']; e=r['ev']; big=U[r['S'][U]>=0.05]
    for c in big:
        fi=int(e[e.ci==c].fi.min()); 
        if fi-20<1 or fi+20>=len(D): continue
        bench=np.nanmean(RCv[fi-20:fi+21][:,U],axis=1); xs=np.nan_to_num(RCv[fi-20:fi+21,c]-bench)
        evl.append(dict(rebal=D[t],inst=cols[c],float_date=D[fi],S=r['S'][c],car_m20_m1=xs[:20].sum(),car_0_p20=xs[20:].sum(),car_m20_p20=xs.sum()))
E=pd.DataFrame(evl); E['window']=np.where(E.float_date<=SEAL_END,'sealed','confirm')
E['bin']=pd.cut(E.S,[0.05,0.10,0.20,10],labels=['5-10%','10-20%','>20%'])
E.to_csv(OUT+'/events.csv',index=False)
ES=E.groupby(['window','bin'],observed=True)[['car_m20_m1','car_0_p20','car_m20_p20']].agg(['mean','count']); ES.to_csv(OUT+'/event_study.csv')
# ---- blocked_data: large-unlock sample using full info (ignore visibility): S_full>=5% at any rebal in sealed
blk=[]
for t,r in reb.items():
    if D[t]>SEAL_END: continue
    U=set(r['U']); a=sf[(sf.fi>=t+1)&(sf.fi<=t+20)&sf.ci.isin(U)]
    v=a.sh.values*CRv[t-1,a.ci.values]/FMv[t-1,a.ci.values]; a=a.assign(Sx=v)
    g=a.groupby('ci').agg(Sx=('Sx','sum'),late=('ann',lambda s: False),fd=('fd','min'),ann=('ann','max'))
    aa=a.groupby('ci').apply(lambda x:(x.ann.isna()|(x.ann>=x.fd)).any()); g['late']=aa
    g=g[g.Sx>=0.05]; g['lead_days']=(g.fd-g.ann).dt.days; blk.append(g)
B=pd.concat(blk); late=float(B.late.mean())
lead=B.lead_days.describe(percentiles=[.05,.25,.5,.75]).to_dict()
out=dict(prereg_sha256=PSHA,promotion_approved=False,research_only=True,unit_ratio=float(ratio),rebals=len(reb),
  first_rebal=str(D[min(reb)].date()),large_sample=int(len(B)),late_frac=late,blocked_data=late>0.20,lead_days=lead,maxrss_MB=mem())
json.dump(out,open(OUT+'/results.json','w'),indent=1,default=str)
pd.set_option('display.width',250)
print(json.dumps(out,default=str,indent=1)); print(S[S.cost.isin(['gross','flat25','imp5e7','imp2e8','flat100'])].round(4).to_string()); print(Y.round(4).to_string()); print(ES.round(4).to_string()); print('maxrss',mem())
