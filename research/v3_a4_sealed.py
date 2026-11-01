# V3 A4 sealed run, prereg docs/prereg/V3_A4_CB_RESET_PUT_PRESSURE.md. Research only; each arm once. promotion_approved=false.
import pandas as pd, numpy as np, os, json, hashlib, resource, sys
from math import erf, sqrt
ROOT='/workspace/QuantLab'; OUT=ROOT+'/output/alpha/V3_A4_SEALED'; sys.path.insert(0,ROOT)
from quantlab.platform.execution import sqrt_impact_cost
PRE=ROOT+'/docs/prereg/V3_A4_CB_RESET_PUT_PRESSURE.md'; PSHA=hashlib.sha256(open(PRE,'rb').read()).hexdigest()
assert PSHA=='5a20436789e70df042fa4df971ec5b9ab396d8daa91c33579900c4962a04dea7', PSHA
mem=lambda: resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
SEAL0=pd.Timestamp('2018-01-01'); SEAL_END=pd.Timestamp('2024-05-31'); END=pd.Timestamp('2026-10-09')
# ---------- CB data
b=pd.read_parquet(ROOT+'/data/v2/cb/cb_basic.parquet'); b=b[b.cb_type=='CB'].set_index('ts_code')
for c in ['maturity_date','delist_date','list_date']: b[c]=pd.to_datetime(b[c],errors='coerce',format='%Y%m%d')
d=pd.read_parquet(ROOT+'/data/v2/cb/cb_daily.parquet',columns=['ts_code','trade_date','open','close','vol','amount','cb_value','cb_over_rate','is_placeholder'])
d=d[d.ts_code.isin(b.index)&~d.is_placeholder]; d['date']=pd.to_datetime(d.trade_date)
d=d[(d.date>='2017-06-01')&(d.date<=END)]
pv=lambda v: d.pivot_table(index='date',columns='ts_code',values=v)
CL=pv('close'); OP=pv('open'); VOL=pv('vol').fillna(0); AMT=pv('amount').fillna(0)*1e4; CV=pv('cb_value'); PR=pv('cb_over_rate')
D=CL.index; cols=CL.columns; del d
OP,VOL,AMT,CV,PR=[x.reindex(index=D,columns=cols) for x in (OP,VOL,AMT,CV,PR)]; VOL=VOL.fillna(0); AMT=AMT.fillna(0)
print('cb mem',mem(),flush=True)
OP=OP.where(OP>0)
traded=VOL>0
# exits per prereg §2.6
last=CL.apply(lambda s: s[s.notna()&traded[s.name]].index.max() if (traded[s.name]).any() else pd.NaT)
gap=(b.delist_date.reindex(cols)-last).dt.days
normal=(gap<=30)&gap.notna()
live=b.delist_date.reindex(cols).isna()&((END-last).dt.days<=30)
kind=pd.Series(np.where(normal|live,'normal','default'),index=cols)
def price_panel(recov):
    O=OP.copy(); C=CL.copy()
    for c in cols:
        l=last[c]
        if pd.isna(l): continue
        lc=CL.at[l,c]; after=D>l
        v=lc if kind[c]=='normal' else lc*recov
        O.loc[after,c]=v; C.loc[after,c]=v
    C=C.ffill(); O=O.fillna(C)
    return (O.shift(-1)/O-1).fillna(0).clip(-0.95,5)
RO={r:price_panel(r) for r in (0.3,0.0,1.0)}
RC=CL.where(traded).ffill().pct_change(fill_method=None)
SIG=RC.rolling(20,min_periods=10).std(); ADV=AMT.rolling(20,min_periods=10).mean()
AGE=traded.cumsum()
# signals
TRIG=(CV<85).astype(float).where(CV.notna()).rolling(30,min_periods=30).sum()
mat=b.maturity_date.reindex(cols)
# ---------- underlying
cv=lambda s: s.str[-2:].str.lower()+'.'+s.str[:6]
stk=cv(b.stk_code.reindex(cols)); stk.index=cols
P0=ROOT+'/data/local_market/1c85fd9aceaa03c3c4863bec/panels'; SC={}; ST={}
for s in sorted(set(stk.dropna())):
    f=f'{P0}/{s}.parquet'
    if not os.path.exists(f): continue
    x=pd.read_parquet(f,columns=['close','is_st_at_open']); x.index=pd.to_datetime(x.index)
    SC[s]=x.close; ST[s]=x.is_st_at_open
print('und mem',mem(),flush=True)
SC=pd.DataFrame(SC).reindex(D).ffill(); ST=pd.DataFrame(ST).reindex(D).ffill()
import pyarrow.parquet as pq
fm=pq.read_table(ROOT+'/data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet',columns=['instrument_id','trade_date','float_mktcap']).to_pandas(strings_to_categorical=True)
fm['float_mktcap']=fm.float_mktcap.astype('float32')
fm['trade_date']=pd.to_datetime(fm.trade_date); fm=fm[(fm.trade_date>='2017-06-01')]
fm['rk']=fm.groupby('trade_date').float_mktcap.rank(ascending=False,method='first')
fm=fm[fm.instrument_id.isin(set(stk.dropna()))]
RK=fm.pivot_table(index='trade_date',columns='instrument_id',values='rk').reindex(D).ffill(limit=5); del fm
print('loaded mem',mem(),flush=True)
def umap(panel):  # positional map underlying columns -> cb columns (NaN where missing)
    ix=panel.columns.get_indexer(stk.fillna('__none__').values); a=panel.values[:,np.maximum(ix,0)].astype(float); a[:,ix<0]=np.nan; return a
RKm=umap(RK); STm=umap(ST)
def under(panel,t): return (RKm if panel is RK else STm)[t]
K=pd.DataFrame(100*umap(SC)/CV.values,index=D,columns=cols)
# ---------- weekly rebal (last trading day of each ISO week)
wk=pd.Series(D,index=D).groupby([D.isocalendar().year.values,D.isocalendar().week.values]).max().values
reb_days=[pd.Timestamp(x) for x in wk if pd.Timestamp(x)>=pd.Timestamp('2018-01-02') and pd.Timestamp(x)<END]
rebs={}; elig=[]
for day in reb_days:
    t=D.get_loc(day)
    ok=traded.iloc[t].values&(AGE.iloc[t].values>=20)&(ADV.iloc[t].values>=1e7)&CV.iloc[t].notna().values&PR.iloc[t].notna().values
    ok&=((mat-day).dt.days.values>0.5*365.25)
    rk=under(RK,t-1); st=under(ST,t)
    ok&=(np.nan_to_num(rk,nan=1e9)<=1500)&(np.nan_to_num(st,nan=1)==0)
    U=np.nonzero(ok)[0]
    pz=(day>=(mat-pd.DateOffset(years=2,months=6))).values
    tr=TRIG.iloc[t].values; pr=PR.iloc[t].values; cvv=CV.iloc[t].values
    T1=U[(tr[U]>=10)&pz[U]&(pr[U]>20)]
    T2=U[(tr[U]>=10)&~pz[U]&(pr[U]>20)]
    T4=U[pz[U]&(pr[U]>20)&(cvv[U]>=100)&(cvv[U]<=115)]
    # quintile cells within pool
    px=CL.iloc[t].values
    qp=pd.qcut(pd.Series(px[U]).rank(method='first'),5,labels=False).values if len(U)>=5 else np.zeros(len(U),int)
    qr=pd.qcut(pd.Series(pr[U]).rank(method='first'),5,labels=False).values if len(U)>=5 else np.zeros(len(U),int)
    cell=dict(zip(U,qp*5+qr))
    rebs[t]=dict(U=U,T1=T1,T2=T2,T4=T4,cell=cell)
    elig.append(dict(date=day,pool=len(U),T1=len(T1),T2=len(T2),T4=len(T4)))
E=pd.DataFrame(elig).set_index('date'); E.to_csv(OUT+'/eligible_counts.csv')
print('rebals',len(rebs),'mem',mem(),flush=True)
N=len(cols)
def ew(idx):
    w=np.zeros(N); 
    if len(idx): w[idx]=1/len(idx)
    return w
def target(arm,r):
    U=r['U']
    if arm=='BASE': return ew(U)
    if arm in ('T1','T2','T4'):
        s=r[arm]; return ew(s) if len(s)>=5 else ew(U)
    if arm=='T3C':  # matched control for T1
        if len(r['T1'])<5: return ew(U)
        T1=set(r['T1']); w=np.zeros(N); wt=1/len(T1); cell=r['cell']; spill=0
        for c in T1:
            ctl=[u for u in U if cell[u]==cell[c] and u not in T1]
            if ctl: w[ctl]+=wt/len(ctl)
            else: spill+=wt
        if spill: w+=spill*ew(U)
        return w
CAPS=[5e7,2e8]
def sim(arm,ro):
    ROv=ro.values; SIGv=SIG.values; ADVv=ADV.values
    w=np.zeros(N); rows=[]
    for t in range(len(D)-1):
        if D[t]<reb_days[0]: continue
        dw=np.zeros(N); 
        if t in rebs:
            tg=target(arm,rebs[t]); dw=tg-w; w=tg
        g=float(w@ROv[t]); turn=float(np.abs(dw).sum()); row=dict(date=D[t+1],gross=g,turn=turn)
        nz=np.nonzero(dw)[0]
        for cap in CAPS:
            tv=cap*np.abs(dw[nz]); imp=sqrt_impact_cost(tv,ADVv[t,nz],SIGv[t,nz]).sum() if len(nz) else 0.0
            row[f'c{cap:.0e}']=(imp+np.maximum(2.5e-4*tv,5).sum()+5e-4*tv.sum())/cap if len(nz) else 0.0
        rows.append(row)
        w=w*(1+ROv[t]); s=w.sum(); w=w/s if s>0 else w
    df=pd.DataFrame(rows).set_index('date')
    df['prereg']=df.gross-(2.5e-4+5e-4)*df.turn
    for bp in (10,25,50): df[f'flat{bp}']=df.gross-bp*1e-4*df.turn
    df['imp5e7']=df.gross-df['c5e+07']; df['imp2e8']=df.gross-df['c2e+08']
    return df
ARMS=['BASE','T1','T2','T4','T3C']
R={a:sim(a,RO[0.3]) for a in ARMS}
RS={(a,rc):sim(a,RO[rc]) for a in ['BASE','T1','T2','T3C','T4'] for rc in (0.0,1.0)}
print('sim done mem',mem(),flush=True)
CK=['gross','prereg','flat10','flat25','flat50','imp5e7','imp2e8']
wk_=lambda s: (1+s).groupby(pd.Grouper(freq='W-FRI')).prod()-1
def nw_t(x,L=4):
    x=np.asarray(x)-np.mean(x); n=len(x); g0=x@x/n; v=g0
    for l in range(1,L+1): v+=2*(1-l/(L+1))*(x[l:]@x[:-l]/n)
    return np.mean(np.asarray(x)+0) if False else None, v
def tstat(inc):
    x=inc.values; n=len(x); m=x.mean(); _,v=nw_t(x); return float(m/sqrt(v/n))
def mdd(x): v=(1+x).cumprod(); return float((v/v.cummax()-1).min())
def ann(x): return float((1+x).prod()**(52/len(x))-1)
PAIRS={'T1':('T1','BASE'),'T2':('T2','BASE'),'T3':('T1','T3C'),'T4':('T4','BASE')}
res=[]; yrs=[]
for arm,(a,bb) in PAIRS.items():
    for win,lo,hi in [('sealed',SEAL0,SEAL_END),('confirm',pd.Timestamp('2024-06-01'),END)]:
        for ck in CK:
            xa=wk_(R[a][ck].loc[lo:hi]); xb=wk_(R[bb][ck].loc[lo:hi]); inc=xa-xb; n=len(inc); t=tstat(inc)
            res.append(dict(arm=arm,window=win,cost=ck,weeks=n,inc_ann=float(inc.mean()*52),t_nw4=t,p_one=1-0.5*(1+erf(t/sqrt(2))),
              arm_ann=ann(xa),ref_ann=ann(xb),arm_mdd=mdd(xa),ref_mdd=mdd(xb),overlay_mdd=mdd(inc),
              turn_ann=float(R[a].loc[lo:hi].turn.sum()/n*52)))
            if win=='sealed' and ck in('flat25','imp5e7'):
                for y,g in inc.groupby(inc.index.year): yrs.append(dict(arm=arm,cost=ck,year=y,inc=float(g.sum())))
S=pd.DataFrame(res)
m=(S.window=='sealed')&(S.cost=='flat25')&S.arm.isin(['T1','T2','T3'])
p=S.loc[m,'p_one'].values; k=len(p); cm=sum(1/i for i in range(1,k+1)); o=np.argsort(p); q=np.empty(k)
q[o]=np.minimum.accumulate((p[o]*k*cm/np.arange(1,k+1))[::-1])[::-1]; S.loc[m,'BY_q']=np.minimum(q,1)
S.to_csv(OUT+'/summary.csv',index=False)
Y=pd.DataFrame(yrs); Y.pivot_table(index='year',columns=['cost','arm'],values='inc').to_csv(OUT+'/by_year_sealed.csv')
# default sensitivity
sens=[]
for arm,(a,bb) in PAIRS.items():
    for rc in (0.0,1.0):
        x=wk_(RS[(a,rc)]['flat25'].loc[SEAL0:SEAL_END])-wk_(RS[(bb,rc)]['flat25'].loc[SEAL0:SEAL_END])
        sens.append(dict(arm=arm,recovery=rc,inc_ann=float(x.mean()*52),t=tstat(x)))
pd.DataFrame(sens).to_csv(OUT+'/default_sensitivity.csv',index=False)
# reset incidence: K drop >1% between rebal t and next rebal, held names
Kv=K.values; rt=sorted(rebs); inc_rows=[]
for i,t in enumerate(rt[:-1]):
    t2=rt[i+1]; ch=Kv[t2]/Kv[t]-1
    for arm in ('BASE','T1','T2','T4'):
        r=rebs[t]; s=r['U'] if arm=='BASE' or len(r.get(arm,[]))<5 else r[arm]
        v=ch[s]; v=v[np.isfinite(v)]
        if len(v): inc_rows.append(dict(date=D[t],arm=arm,n=len(v),resets=int((v<-0.01).sum())))
IR=pd.DataFrame(inc_rows); IR['win']=np.where(IR.date<=SEAL_END,'sealed','confirm')
RI=IR.groupby(['win','arm'])[['n','resets']].sum(); RI['rate']=RI.resets/RI.n; RI.to_csv(OUT+'/reset_incidence.csv')
# capacity: held-name ADV
cap=[]
for arm in ('T1','T2','T4'):
    v=[];c=[]
    for t,r in rebs.items():
        if D[t]>SEAL_END or len(r[arm])<5: continue
        v.append(np.median(ADV.values[t,r[arm]])); c.append(len(r[arm]))
    cap.append(dict(arm=arm,weeks_active=len(v),median_names=float(np.median(c)) if c else 0,median_held_adv_cny=float(np.median(v)) if v else None))
pd.DataFrame(cap).to_csv(OUT+'/capacity.csv',index=False)
out=dict(prereg_sha256=PSHA,promotion_approved=False,research_only=True,rebals=len(rebs),first_rebal=str(reb_days[0].date()),
  n_default=int((kind=='default').sum()),maxrss_MB=mem())
json.dump(out,open(OUT+'/results.json','w'),indent=1,default=str)
pd.set_option('display.width',250); pd.set_option('display.max_rows',200)
print(json.dumps(out,default=str))
print(E.loc[:SEAL_END].describe().round(1).to_string())
print(S[S.cost.isin(['gross','prereg','flat25','imp5e7','imp2e8','flat50'])].round(4).to_string())
print(Y.pivot_table(index='year',columns=['cost','arm'],values='inc').round(4).to_string())
print(pd.DataFrame(sens).round(4).to_string()); print(RI.round(4).to_string()); print(pd.DataFrame(cap).to_string()); print('maxrss',mem())
# ---- diagnostics (added after run#3 results; deterministic re-execution, no parameter change)
for a in R: R[a].to_csv(OUT+f'/daily_{a}.csv')
dg={}
for a in ARMS: dg[f'turn_ann_sealed_{a}']=float(R[a].loc[SEAL0:SEAL_END].turn.sum()/334*52)
act=IR[(IR.win=='sealed')].copy()
actd=set(D[t] for t,r in rebs.items() if len(r['T1'])>=5)
x=act[act.date.isin(actd)].groupby('arm')[['n','resets']].sum(); x['rate']=x.resets/x.n
dg['reset_rate_T1_active_weeks']=x.round(4).to_dict()
dg['T1_active_weeks_sealed_by_year']=pd.Series([d.year for d in actd if d<=SEAL_END]).value_counts().sort_index().to_dict()
json.dump(dg,open(OUT+'/diagnostics.json','w'),indent=1,default=str); print(json.dumps(dg,default=str,indent=1)); print('maxrss',mem())
