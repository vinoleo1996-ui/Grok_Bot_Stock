"""P7 NETRET_MIDLARGE — cost-aware net-return ridge on mid/large-cap (top1500 float cap; CSI300+500 cross-check).
Research only, promotion_approved=False. Prereg docs/prereg/P7_NETRET_MIDLARGE.md."""
import sys, json, math, time, gc, resource, hashlib
from pathlib import Path
from math import erf, sqrt
import numpy as np, pandas as pd
ROOT=Path('/workspace/QuantLab'); V2=ROOT/'data/v2'; S=Path('/workspace/scratch/tic')
OUT=ROOT/'output/alpha/NETRET_MIDLARGE_P7'; OUT.mkdir(parents=True,exist_ok=True)
PREREG=ROOT/'docs/prereg/P7_NETRET_MIDLARGE.md'; PSHA=hashlib.sha256(PREREG.read_bytes()).hexdigest()
mem=lambda: resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
t0=time.time(); log=lambda *a: print(f'[p7 {time.time()-t0:6.0f}s {mem():.0f}MB]',*a,flush=True)
SEAL=('2018-01-02','2024-05-31'); CONF_START=pd.Timestamp('2024-06-03')
N=100; BUF=150; LAM=10.0; K_IMP=1.0; CAP_REF=5e7; STEP=5
ld=lambda c: pd.read_parquet(S/f'{c}.parquet',columns=cols).astype('float32')
import pyarrow.parquet as pq, gc
allc=[c for c in pq.read_schema(S/'close.parquet').names if (c[:6] in ('sh.600','sh.601','sh.603','sh.605','sh.688','sh.689') or c[:5] in ('sz.00','sz.30'))]
TD=pd.read_parquet(S/'close.parquet',columns=[allc[0]]).index
def piv(path,col,cols):
    x=pd.read_parquet(path,columns=['trade_date','instrument_id',col],filters=[('trade_date','>=',TD[0])])
    x=x[x.instrument_id.isin(set(cols))]; x[col]=x[col].astype('float32'); x['trade_date']=pd.to_datetime(x.trade_date)
    w=x.drop_duplicates(['trade_date','instrument_id'],keep='last').set_index(['trade_date','instrument_id'])[col].unstack().reindex(index=TD,columns=cols)
    del x; gc.collect(); return w.astype('float32')
FM=piv(V2/'float_mktcap/float_mktcap_daily_tushare.parquet','float_mktcap',allc)
iw0=pd.read_parquet(V2/'index_members/index_weight_csi300_500_1000.parquet'); iw0=iw0[iw0.index_code.isin(['000300.SH','000905.SH'])]
ixset=set(iw0.con_code.str[-2:].str.lower()+'.'+iw0.con_code.str[:6]); del iw0
rkall=FM.rank(axis=1,ascending=False)
cols=sorted(set(FM.columns[(rkall<=1800).any(axis=0).values])|(ixset&set(allc))); del rkall
FM=FM[cols]; gc.collect()
cl=ld('close'); op=ld('open'); fa=ld('factor').ffill()
amt=ld('amount'); tov=ld('turnover'); ts=ld('tradestatus'); lu=ld('limit_up'); st=ld('is_st_at_open')
log('panels',cl.shape,'amount median',float(np.nanmedian(amt.iloc[-1].values)))
aC=cl*fa; aO=(op*fa); aOf=aO.ffill(); del fa; gc.collect()
ret=aC.pct_change(fill_method=None)
F={}
F['R02']=-(aC/aC.shift(20)-1); F['TURN']=-tov.rolling(20,min_periods=15).mean(); F['RV60']=-ret.rolling(60).std()
F['AMIH']=((ret.abs()/amt.replace(0,np.nan))*1e9).rolling(20).mean()  # illiquidity positive
F['MOM']=aC.shift(20)/aC.shift(240)-1
pb=piv(V2/'valuation/daily_basic_valuation_tushare.parquet','pb',cols); F['BP']=1/pb.where(pb>0); del pb
F['EP']=piv(V2/'ep/ep_pit_daily_tushare.parquet','ep',cols)
F['SIZE']=np.log(FM.where(FM>0))
for k in F: F[k]=F[k].astype('float32')
SIG=ret.rolling(20,min_periods=15).std().astype('float32'); ADV=amt.rolling(20,min_periods=15).mean().astype('float32')
AGE=cl.notna().cumsum()
LUC=((cl>=lu-0.005)&lu.notna()&cl.notna()).astype('float32'); LU5=LUC.rolling(5,min_periods=1).max()
ti=pd.read_parquet(V2/'dragon_tiger/top_inst_labeled.parquet',columns=['trade_date','ts_code'])
ti['c']=ti.ts_code.str[-2:].str.lower()+'.'+ti.ts_code.str[:6]; ti['d']=pd.to_datetime(ti.trade_date)
L=pd.crosstab(ti.d,ti.c).clip(upper=1).reindex(index=TD,columns=cols).fillna(0).astype('float32'); LHB20=L.rolling(20,min_periods=1).max(); del ti,L,ret
gc.collect(); log('features built')
sw=pd.read_parquet(V2/'sw_l1_pit/industry_members_sw_l1_tushare.parquet'); sw['out_date']=sw['out_date'].fillna(pd.Timestamp('2100-01-01'))
INDS=sorted(sw.sw_code.unique())
iw=pd.read_parquet(V2/'index_members/index_weight_csi300_500_1000.parquet'); iw=iw[iw.index_code.isin(['000300.SH','000905.SH'])]
iw['c']=iw.con_code.str[-2:].str.lower()+'.'+iw.con_code.str[:6]; iw['d']=pd.to_datetime(iw.trade_date)
SNAP={d:set(g.c) for d,g in iw.groupby('d')}; SNAPD=sorted(SNAP)
def u2_members(d):
    i=np.searchsorted(SNAPD,d,side='right')-1; return SNAP[SNAPD[i]] if i>=0 else None
NUM=['R02','TURN','RV60','BP','EP','AMIH','MOM','SIZE']
def stamp(d): return 0.001 if d<pd.Timestamp('2023-08-28') else 0.0005
def sp(a,b):
    a=pd.Series(a).rank(); b=pd.Series(b).rank(); return a.corr(b)
def csrank(v):
    s=pd.Series(v); r=s.rank(pct=True)-0.5; return r.fillna(0.0).values
dates=[d for d in TD[TD>=pd.Timestamp('2018-01-02')]][::STEP]; dates=[d for d in dates if TD.get_loc(d)+2<len(TD)]
rows=[]
for d in dates:
    loc=TD.get_loc(d)
    base=(ts.iloc[loc]==1)&cl.iloc[loc].notna()&(st.iloc[loc]!=1)&(AGE.iloc[loc]>=120)&FM.iloc[loc].notna()
    ids=base[base].index
    rk=FM.iloc[loc][ids].rank(ascending=False); u1=set(rk[rk<=1500].index)
    m2=u2_members(d); u2=set(ids)&m2 if m2 else set()
    ids=sorted(u1|u2)
    if len(ids)<300: continue
    im=sw[(sw.in_date<=d)&(sw.out_date>d)].drop_duplicates('instrument_id',keep='last').set_index('instrument_id').sw_code.reindex(ids)
    g=lambda P,k: P.iloc[loc+k][ids].values.astype(float) if loc+k<len(TD) else np.full(len(ids),np.nan)
    o1=g(aO,1)
    rec={'date':d,'id':ids,'u1':[i in u1 for i in ids],'u2':[i in u2 for i in ids],'ind':im.values,
         'buy_ok':(g(ts,1)==1)&np.isfinite(o1)&~(g(op,1)>=g(lu,1)-0.005),
         'y5':g(aOf,6)/o1-1,'y20':g(aOf,21)/o1-1,'sig':g(SIG,0),'adv':g(ADV,0),'stamp':stamp(d)}
    for k in NUM:
        rec[k]=F[k].iloc[loc][ids].values.astype(float); rec[k+'_l1']=F[k].iloc[loc-1][ids].values.astype(float)
    rec['LHB20']=g(LHB20,0); rec['LU5']=g(LU5,0); rec['LHB20_l1']=LHB20.iloc[loc-1][ids].values; rec['LU5_l1']=LU5.iloc[loc-1][ids].values
    rows.append(pd.DataFrame(rec))
D=pd.concat(rows,ignore_index=True); del rows
del F,aC,aO,aOf,op,cl,amt,tov,lu,st,SIG,ADV,AGE,LUC,LU5,LHB20,FM; gc.collect(); log('dataset',D.shape)
D['buy_ok']=D.buy_ok.astype(bool)
v=CAP_REF/N; imp=K_IMP*D.sig.fillna(D.sig.median())*np.sqrt(v/D.adv.where(D.adv>0))
D['chat']=2*2.5e-4+D.stamp+2*imp.fillna(imp.median()).clip(upper=0.05)
def design(df,lag=False):
    s='_l1' if lag else ''
    X=[]
    for dd,g in df.groupby('date',sort=False):
        M=np.column_stack([csrank(g[k+s].values) for k in NUM]+[g['LHB20'+s].fillna(0).values-0.1,g['LU5'+s].fillna(0).values-0.1]+
                          [(g.ind.values==c).astype(float) for c in INDS])
        X.append(M)
    return np.vstack(X)
def fit(df,yk,net):
    df=df[np.isfinite(df[yk])]; y=df[yk].values-(df.chat.values if net else 0)
    y=y-df.groupby('date')[yk].transform('mean').values+(0 if not net else df.groupby('date').chat.transform('mean').values)
    y=np.clip(y,-0.5,0.5); X=design(df)
    return np.linalg.solve(X.T@X+LAM*np.eye(X.shape[1]),X.T@y)
def ann(nav_ret,H):
    r=np.asarray(nav_ret); nav=np.cumprod(1+r); y=len(r)*H/244
    cagr=nav[-1]**(1/y)-1; ppy=244/H; sh=r.mean()/r.std()*math.sqrt(ppy) if r.std()>0 else np.nan
    mdd=float((nav/np.maximum.accumulate(np.r_[1,nav])[1:]-1).min()); return dict(ann=float(cagr),sharpe=float(sh),mdd=mdd)
def run(arm,uk,H,net,refit=True,score='ridge',win='sealed'):
    yk='y5' if H==5 else 'y20'
    allD=sorted(D.date.unique()); every=H//STEP
    if win=='sealed': td=[d for d in allD if pd.Timestamp('2019-01-01')<=d<=pd.Timestamp(SEAL[1])][::every]
    else: td=[d for d in allD if d>=CONF_START][::every]
    td=[d for d in td if TD.get_loc(d)+H+1<len(TD)]  # label must be realized
    beta=None; by=None; recs=[]; held={}; nav=dict(g=1.0)
    navs={f'flat{b}':[] for b in (25,50,100)}; navs['gross']=[]; imp={5e7:[1.0],2e8:[1.0]}; impr={5e7:[],2e8:[]}
    for d in td:
        if score=='ridge':
            ky=d.year if win=='sealed' else 'conf'
            if beta is None or (refit and ky!=by):
                cut=d if win=='sealed' else CONF_START
                if not refit: cut=pd.Timestamp('2019-01-01')
                tr_dates=[x for x in allD if x<cut]; tr_dates=tr_dates[:max(0,len(tr_dates)-(H//STEP+1))]
                tr=D[D.date.isin(tr_dates)&D[uk]]; beta=fit(tr,yk,net); by=ky
        g=D[(D.date==d)&D[uk]]
        if score=='ridge': p=design(g)@beta; pl=design(g,lag=True)@beta
        else:
            p=np.mean([csrank(g[k].values) for k in ('R02','TURN','RV60','BP')],0); pl=np.mean([csrank(g[k+'_l1'].values) for k in ('R02','TURN','RV60','BP')],0)
        ids=g.id.values; c=g.chat.values; ok=g.buy_ok.values
        adj=p-(np.where(np.isin(ids,list(held)),0.0,c) if score=='ridge' else 0.0)
        order=np.argsort(-adj); rank=np.empty(len(ids)); rank[order]=np.arange(1,len(ids)+1)
        keep=[i for i,r in zip(ids,rank) if i in held and r<=BUF]
        new=[]
        for j in order:
            if len(keep)+len(new)>=N: break
            if ids[j] not in held and ok[j]: new.append(ids[j])
        port=set(keep)|set(new); w={i:1.0/N for i in port}
        dw={i:w.get(i,0)-held.get(i,0) for i in set(w)|set(held)}; tsum=sum(abs(x) for x in dw.values())
        y=pd.Series(g[yk].values,index=ids); gr=float(np.nansum([w[i]*(0 if not np.isfinite(y[i]) else y[i]) for i in port]))
        ok_lab=np.isfinite(g[yk].values)&ok; bench=float(np.nanmean(g[yk].values[ok_lab]))
        ic=sp(p[ok_lab],g[yk].values[ok_lab])
        icl=sp(pl[ok_lab],g[yk].values[ok_lab])
        ew4=np.mean([csrank(g[k].values) for k in ('R02','TURN','RV60','BP')],0); cew=sp(p,ew4)
        Z=np.column_stack([np.ones(len(ids)),csrank(g.SIZE.values)]+[(g.ind.values==q).astype(float) for q in INDS])
        pr=p-Z@np.linalg.lstsq(Z,p,rcond=None)[0]; icr=sp(pr[ok_lab],g[yk].values[ok_lab])
        R2=1-np.var(pr)/np.var(p) if np.var(p)>0 else np.nan
        rng=np.random.default_rng(int(d.strftime('%Y%m%d'))); NZ=rng.standard_normal((ok_lab.sum(),100))
        yr=pd.Series(g[yk].values[ok_lab]).rank().values; NR=pd.DataFrame(NZ).rank().values
        nic=((NR-NR.mean(0))*(yr-yr.mean())[:,None]).mean(0)/(NR.std(0)*yr.std())
        sig=pd.Series(g.sig.values,index=ids); adv=pd.Series(g.adv.values,index=ids)
        for capv in (5e7,2e8):
            navv=imp[capv][-1]; cost=0.0
            for i,x in dw.items():
                V=abs(x)*capv*navv
                if V<=0: continue
                cc=max(2.5e-4*V,5.0)+(V*g.stamp.iloc[0] if x<0 else 0.0)
                s_,a_=sig.get(i,np.nan),adv.get(i,np.nan)
                if np.isfinite(s_) and np.isfinite(a_) and a_>0: cc+=V*K_IMP*s_*math.sqrt(V/a_)
                cost+=cc
            rr=gr-cost/(capv*navv); impr[capv].append(rr); imp[capv].append(navv*(1+rr))
        recs.append(dict(date=d,gross=gr,bench=bench,turn=tsum,ic=ic,ic_lag1=icl,ic_resid=icr,R2_style=R2,corr_ew4=cew,noise_ic=nic.tolist(),n=len(port)))
        held=w
    R=pd.DataFrame(recs).set_index('date')
    o={'arm':arm,'universe':uk,'H':H,'net_target':net,'refit':refit,'score':score,'window':win,'n_periods':len(R)}
    o['gross']=ann(R.gross,H); o['bench_ew']=ann(R.bench,H)
    for b in (25,50,100): o[f'flat{b}']=ann(R.gross-R.turn*b/1e4,H)
    for capv in (5e7,2e8): o[f'impact_{capv:.0e}']=ann(impr[capv],H)
    o['turnover_oneway_ann']=float(R.turn.sum()/2/(len(R)*H/244))
    o['excess_flat25_vs_ew_ann']=o['flat25']['ann']-o['bench_ew']['ann']
    dd=(R.gross-R.turn*25/1e4)-R.bench; t=dd.mean()/(dd.std(ddof=1)/np.sqrt(len(dd))); o['paired_t']=float(t); o['p_one_sided']=float(1-0.5*(1+erf(t/sqrt(2))))
    icir=lambda s: float(s.mean()/s.std()) 
    NI=np.array(R.noise_ic.tolist()); nicir=NI.mean(0)/NI.std(0)
    o['ic']=dict(mean=float(R.ic.mean()),icir=icir(R.ic),icir_lag1=icir(R.ic_lag1),icir_resid_size_ind=icir(R.ic_resid),R2_style=float(R.R2_style.mean()),
                 corr_with_EW4=float(R.corr_ew4.mean()),noise_icir_p95=float(np.quantile(np.abs(nicir),0.95)),pos_ic_frac=float((R.ic>0).mean()))
    r25=R.gross-R.turn*25/1e4; o['by_year_flat25']={int(y):float((1+x).prod()-1) for y,x in r25.groupby(R.index.year)}
    o['by_year_bench']={int(y):float((1+x).prod()-1) for y,x in R.bench.groupby(R.index.year)}
    o['haircut06_flat25']=0.6*o['flat25']['ann']; o['haircut06_impact5e7']=0.6*o['impact_5e+07']['ann']
    R.drop(columns='noise_ic').to_csv(OUT/f'periods_{arm}_{win}.csv')
    log(arm,win,f"g {o['gross']['ann']:.4f} f25 {o['flat25']['ann']:.4f} imp5e7 {o['impact_5e+07']['ann']:.4f} ew {o['bench_ew']['ann']:.4f} turn {o['turnover_oneway_ann']:.2f} icir {o['ic']['icir']:.3f}")
    return o
ARMS=[('T1_RIDGE_NET_H5','u1',5,True,True,'ridge'),('T2_RIDGE_NET_H20','u1',20,True,True,'ridge'),('T3_RIDGE_GROSS_H5','u1',5,False,True,'ridge'),
      ('T4_RIDGE_NET_H5_U2','u2',5,True,True,'ridge'),('B1_FIXED_RIDGE_NET_H5','u1',5,True,False,'ridge'),('B2_EW4_H5','u1',5,True,True,'ew4'),('B2u2_EW4_H5','u2',5,True,True,'ew4')]
RES={}
for a in ARMS:
    for win in ('sealed','confirm'): RES[f'{a[0]}|{win}']=run(*a,win=win)
TR=['T1_RIDGE_NET_H5','T2_RIDGE_NET_H20','T3_RIDGE_GROSS_H5','T4_RIDGE_NET_H5_U2']
ps=np.array([RES[f'{t}|sealed']['p_one_sided'] for t in TR]); m=len(ps); o_=np.argsort(ps); cm=np.sum(1/np.arange(1,m+1))
q=np.empty(m); q[o_]=np.minimum.accumulate((ps[o_]*m*cm/np.arange(1,m+1))[::-1])[::-1]; q=np.minimum(q,1)
for t,qq in zip(TR,q): RES[f'{t}|sealed']['BY_q']=float(qq)
json.dump({'promotion_approved':False,'research_only':True,'run_id':'NETRET_MIDLARGE_P7','prereg':str(PREREG.relative_to(ROOT)),'prereg_sha256':PSHA,
           'n_trials':4,'dataset_rows':int(len(D)),'sample_step_sessions':STEP,'results':RES,'runtime_s':time.time()-t0,'maxrss_MB':mem()},
          open(OUT/'summary.json','w'),ensure_ascii=False,indent=1,default=str)
log('done')
