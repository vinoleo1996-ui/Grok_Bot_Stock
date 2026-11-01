"""P8 EVENTS_MIDLARGE sealed run (each arm once). Research only, promotion_approved=False.
Prereg docs/prereg/P8_EVENTS_MIDLARGE.md + Amendment A (sha 3148e794...)."""
import sys, json, time, gc, resource, hashlib
from pathlib import Path
from math import erf, sqrt
import numpy as np, pandas as pd, pyarrow.parquet as pq
ROOT=Path('/workspace/QuantLab'); V2=ROOT/'data/v2'; S=Path('/workspace/scratch/tic'); sys.path.insert(0,str(ROOT))
from quantlab.platform.execution import sqrt_impact_cost
OUT=ROOT/'output/alpha/P8_EVENTS_MIDLARGE_SEALED'; OUT.mkdir(parents=True,exist_ok=True)
PSHA=hashlib.sha256((ROOT/'docs/prereg/P8_EVENTS_MIDLARGE.md').read_bytes()).hexdigest(); assert PSHA.startswith('3148e794'),PSHA
mem=lambda: resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
t0=time.time(); log=lambda *a: print(f'[p8 {time.time()-t0:5.0f}s {mem():.0f}MB]',*a,flush=True)
SEAL0=pd.Timestamp('2018-01-02'); SEAL1=pd.Timestamp('2024-05-31'); LOADEND=pd.Timestamp('2024-07-31')
allc=[c for c in pq.read_schema(S/'close.parquet').names if (c[:6] in ('sh.600','sh.601','sh.603','sh.605','sh.688','sh.689') or c[:5] in ('sz.00','sz.30'))]
TD0=pd.read_parquet(S/'close.parquet',columns=[allc[0]]).index
def piv(path,col,cols,TD):
    x=pd.read_parquet(path,columns=['trade_date','instrument_id',col],filters=[('trade_date','>=',TD[0])])
    x=x[x.instrument_id.isin(set(cols))]; x[col]=x[col].astype('float32'); x['trade_date']=pd.to_datetime(x.trade_date)
    w=x.drop_duplicates(['trade_date','instrument_id'],keep='last').set_index(['trade_date','instrument_id'])[col].unstack().reindex(index=TD,columns=cols)
    del x; gc.collect(); return w.astype('float32')
TDm=TD0[(TD0>=pd.Timestamp('2017-06-01'))&(TD0<=LOADEND)]
FM=piv(V2/'float_mktcap/float_mktcap_daily_from2015_tushare.parquet','float_mktcap',allc,TDm)
iw=pd.read_parquet(V2/'index_members/index_weight_csi300_500_1000.parquet',columns=['index_code','con_code','trade_date']); iw=iw[iw.index_code.isin(['000300.SH','000905.SH'])]
iw['c']=iw.con_code.str[-2:].str.lower()+'.'+iw.con_code.str[:6]; iw['d']=pd.to_datetime(iw.trade_date)
rk=FM.rank(axis=1,ascending=False); cols=sorted(set(FM.columns[(rk<=1800).any(axis=0).values])|(set(iw.c)&set(allc))); del rk
FM=FM[cols]; TD=TDm; NT=len(TD); NC=len(cols); ci={c:i for i,c in enumerate(cols)}
ld=lambda c: pd.read_parquet(S/f'{c}.parquet',columns=cols).reindex(TD).astype('float32')
cl=ld('close'); op=ld('open'); fa=ld('factor').ffill(); amt=ld('amount'); tov=ld('turnover'); ts=ld('tradestatus'); lu=ld('limit_up'); st=ld('is_st_at_open')
aC=(cl*fa).ffill(); aO=(op*fa); aO=aO.fillna(aC); del fa
RO=(aO.shift(-1)/aO-1).fillna(0).clip(-0.9,5).values.astype('float32')
ret=aC.pct_change(fill_method=None)
SIG=ret.rolling(20,min_periods=15).std().shift(1).values; ADV=amt.rolling(20,min_periods=15).mean().shift(1).values
AGE=cl.notna().cumsum().values
TRADE=((ts==1)&op.notna()&(op>0)).values
BUYOK=TRADE&~((op>=lu-0.005)&lu.notna()).values&~(st==1).values
base=TRADE&~(st==1).values&(AGE>=120)&FM.notna().values
FMv=np.where(base,FM.values,np.nan); r1=pd.DataFrame(FMv).rank(axis=1,ascending=False).values
U1=(r1<=1500)  # membership evaluated at day t (use row e-1 for event at e)
SNAP={d:set(g.c) for d,g in iw.groupby('d')}; SNAPD=sorted(SNAP); U2=np.zeros((NT,NC),bool)
for t,d in enumerate(TD):
    i=np.searchsorted(SNAPD,d,side='right')-1
    if i>=0: U2[t,[ci[c] for c in SNAP[SNAPD[i]] if c in ci]]=True
U2&=base
# EW4 score (R02,TURN,RV60,BP) as in P7
F={'R02':-(aC/aC.shift(20)-1),'TURN':-tov.rolling(20,min_periods=15).mean(),'RV60':-ret.rolling(60).std()}
pb=piv(V2/'valuation/daily_basic_valuation_tushare.parquet','pb',cols,TD); F['BP']=1/pb.where(pb>0); del pb
EW4=sum(F[k].where(U1).rank(axis=1,pct=True).fillna(0.5) for k in F).values/4; del F,ret,tov,amt,cl,op,lu,st,ts
# industry & size decile for event benchmark
sw=pd.read_parquet(V2/'sw_l1_pit/industry_members_sw_l1_tushare.parquet'); sw['out_date']=sw['out_date'].fillna(pd.Timestamp('2100-01-01'))
gc.collect(); log('panels',NT,NC)
# ---- events
a=pd.read_parquet(V2/'events/announcements_classified_pit.parquet',columns=['instrument','event_type','subtype','available_at','ann_date'])
a=a[a.event_type!='other']; a['c']=a.instrument.str[-2:].str.lower()+'.'+a.instrument.str[:6]; a=a[a.c.isin(ci)]
av=a.available_at.dt.tz_convert('Asia/Shanghai').dt.tz_localize(None); day=av.dt.normalize()
e=np.where(av.dt.hour*60+av.dt.minute<570, TD.searchsorted(day,side='left'), TD.searchsorted(day,side='right'))
a['e']=e; a['ci']=a.c.map(ci); a=a[(a.e>=1)&(a.e<NT)]
a['ym']=a.ann_date.str[:6]
cov=pd.read_csv(OUT/'verify_monthly_coverage.csv'); low={m.replace('-','') for m in cov[cov['cov']<0.90].month}
a['lowcov']=a.ym.isin(low)
a=a[(TD[a.e.values]>=SEAL0)&(TD[a.e.values]<=SEAL1)]
assert (av[a.index].values < (TD[a.e.values]+pd.Timedelta('9h30min')).values).all()  # no lookahead
EV={'EV1':(a.event_type=='buyback')&a.subtype.str.startswith('repurchase_',na=False)&(a.subtype!='repurchase_terminate'),
 'EV2inc':a.event_type=='insider_increase','EV3beat':a.event_type=='earnings_beat','EV4reply':a.event_type=='inquiry_reply',
 'EV2dec':a.event_type=='insider_decrease','EV3miss':a.event_type=='earnings_miss','EV4letter':a.event_type=='inquiry_letter','EV5':a.event_type=='penalty'}
EV['LONGALL']=EV['EV1']|EV['EV2inc']|EV['EV3beat']|EV['EV4reply']
LONG=['EV1','EV2inc','EV3beat','EV4reply','LONGALL']; FILT=['EV2dec','EV3miss','EV4letter','EV5']
evc={k:int(v.sum()) for k,v in EV.items()}; log('events',evc)
CAP=[5e7,2e8]; STAMP=np.array([0.001 if d<pd.Timestamp('2023-08-28') else 0.0005 for d in TD])
def costs(dw,t,row):
    turn=float(np.abs(dw).sum()); row['turn']=turn
    nz=np.nonzero(dw)[0]; sells=-dw[nz].clip(max=0).sum()
    for cap in CAP:
        if turn==0: row[f'c{cap:.0e}']=0.0; continue
        tv=cap*np.abs(dw[nz]); adv=np.nan_to_num(ADV[t,nz],nan=1e6); sg=np.nan_to_num(SIG[t,nz],nan=0.03)
        row[f'c{cap:.0e}']=(sqrt_impact_cost(tv,adv,sg).sum()+np.maximum(2.5e-4*tv,5).sum())/cap+STAMP[t]*sells
def finish(rows):
    df=pd.DataFrame(rows).set_index('date')
    for bp in (25,50,100): df[f'flat{bp}']=df.gross-bp*1e-4*df.turn
    df['imp5e7']=df.gross-df['c5e+07']; df['imp2e8']=df.gross-df['c2e+08']; return df
T_START=TD.searchsorted(SEAL0); T_END=TD.searchsorted(SEAL1,side='right')-1
def sim_long(evmask,U,H,lag=0):
    ev=a[evmask][['ci','e']].copy(); ev['e']=ev.e+lag; ev=ev[ev.e<=T_END]
    ev=ev[U[ev.e.values-1,ev.ci.values]]
    byday=ev.groupby('e').ci.apply(lambda s: np.unique(s.values)).to_dict()
    exp={}; w=np.zeros(NC,np.float32); rows=[]; nbuy=0; nskip=0
    for t in range(T_START,T_END+1):
        held=set(exp)
        for c in [c for c,x in exp.items() if x<=t and TRADE[t,c]]: del exp[c]
        for c in byday.get(t,[]):
            if c in exp: exp[c]=max(exp[c],t+H)
            elif BUYOK[t,c]: exp[c]=t+H; nbuy+=1
            else: nskip+=1
        tgt=np.zeros(NC,np.float32)
        if exp:
            k=np.fromiter(exp.keys(),int); 
            if set(exp)!=held: tgt[k]=1/len(k)
            else: tgt=w.copy()
        dw=tgt-w; w=tgt; row=dict(date=TD[t],gross=float(w@RO[t]),n=len(exp)); costs(dw,t,row); rows.append(row)
        w=w*(1+RO[t]); s=w.sum(); w=w/s if s>0 else w
    df=finish(rows); df.attrs.update(nbuy=nbuy,nskip=nskip); return df
MON=set(pd.Series(range(NT),index=TD).groupby([TD.year,TD.month]).first().values)
def sim_overlay(evmask,U,basek):
    if evmask is not None:
        ev=a[evmask][['ci','e']]; neg=np.zeros((NT,NC),bool); neg[ev.e.values,ev.ci.values]=True
        neg20=pd.DataFrame(neg).rolling(20,min_periods=1).max().values>0
    w=np.zeros(NC,np.float32); cash=0.0; rows=[]
    for t in range(T_START,T_END+1):
        tgt=None
        if t in MON or not w.any():
            m=U[t-1]&BUYOK[t]
            if basek=='EW4':
                sc=np.where(m,EW4[t-1],-1); idx=np.argsort(-sc)[:100]; m=np.zeros(NC,bool); m[idx]=True
            if evmask is not None: m&=~neg20[t]
            tgt=(m/m.sum()) if m.sum()>0 else np.zeros(NC); cash=0.0 if m.sum()>0 else 1.0
        elif evmask is not None:
            hit=neg[t]&(w>0)&TRADE[t]
            if hit.any(): tgt=w.copy(); cash+=float(tgt[hit].sum()); tgt[hit]=0
        dw=np.zeros(NC) if tgt is None else tgt-w
        if tgt is not None: w=tgt.astype(np.float32)
        row=dict(date=TD[t],gross=float(w@RO[t])); costs(dw,t,row); rows.append(row)
        w=w*(1+RO[t]); s=w.sum()+cash; w=w/s; cash=cash/s
    return finish(rows)
CK=['gross','flat25','flat50','flat100','imp5e7','imp2e8']
ann=lambda x: float((1+x).prod()**(244/len(x))-1)
def mdd(x): v=(1+x).cumprod(); return float((v/v.cummax()-1).min())
def nw_t(x,L=20):
    x=np.asarray(x,float); m=x.mean(); d=x-m; n=len(d); s=d@d/n
    for l in range(1,L+1): s+=2*(1-l/(L+1))*(d[l:]@d[:-l])/n
    return float(m/np.sqrt(s/n))
pone=lambda t: 1-0.5*(1+erf(t/sqrt(2)))
BASES={}
for uk,U in (('U1',U1),('U2',U2)):
    BASES[uk]=sim_overlay(None,U,'EW'); BASES[uk+'_EW4']=sim_overlay(None,U,'EW4')
log('bases done')
res=[]; YR=[]; DAILY={}
def record(arm,uk,kind,H,x,b,extra={}):
    r=dict(arm=arm,univ=uk,kind=kind,H=H,**extra)
    for ck in CK:
        r[f'ann_{ck}']=ann(x[ck]); r[f'base_ann_{ck}']=ann(b[ck]); d=x[ck]-b[ck]; r[f'exc_{ck}']=float(d.mean()*244); r[f't_{ck}']=nw_t(d)
    r['mdd_flat25']=mdd(x.flat25); r['base_mdd_flat25']=mdd(b.flat25); r['turn_ann']=float(x.turn.mean()*244)
    r['sharpe_flat25']=float(x.flat25.mean()/x.flat25.std()*sqrt(244)); r['p_one']=pone(r['t_flat25'])
    d=(x.flat25-b.flat25); 
    for y,g in d.groupby(d.index.year): YR.append(dict(arm=arm,univ=uk,H=H,kind=kind,year=y,exc_flat25=float(g.sum())))
    res.append(r); return r
for uk,U in (('U1',U1),('U2',U2)):
    for k in LONG:
        x=sim_long(EV[k],U,20); DAILY[(k,uk)]=x
        record(k,uk,'trial',20,x,BASES[uk],dict(nbuy=x.attrs['nbuy'],nskip_limitup_susp=x.attrs['nskip'],avg_n=float(x.n.mean()),frac_empty=float((x.n==0).mean())))
        if uk=='U1':
            record(k,uk,'sens_H5',5,sim_long(EV[k],U,5),BASES[uk])
            record(k,uk,'sens_lag1',20,sim_long(EV[k],U,20,lag=1),BASES[uk])
            record(k,uk,'sens_cov90',20,sim_long(EV[k]&~a.lowcov,U,20),BASES[uk])
        log(k,uk)
    for k in FILT:
        record(k,uk,'trial',20,sim_overlay(EV[k],U,'EW'),BASES[uk])
        record(k,uk,'sec_EW4',20,sim_overlay(EV[k],U,'EW4'),BASES[uk+'_EW4'])
        if uk=='U1': record(k,uk,'sens_cov90',20,sim_overlay(EV[k]&~a.lowcov,U,'EW'),BASES[uk])
        log(k,uk)
R=pd.DataFrame(res)
m=R.kind=='trial'; p=R.loc[m,'p_one'].values; k=len(p); cm=sum(1/i for i in range(1,k+1)); o=np.argsort(p); q=np.empty(k)
q[o]=np.minimum.accumulate((p[o]*k*cm/np.arange(1,k+1))[::-1])[::-1]; R.loc[m,'BY_q']=np.minimum(q,1)
R['haircut06_ann_flat25']=R.ann_flat25*0.6; R['haircut06_exc_flat25']=R.exc_flat25*0.6
R.to_csv(OUT/'summary.csv',index=False); Y=pd.DataFrame(YR); Y.to_csv(OUT/'by_year_flat25.csv',index=False)
for (k,uk),x in DAILY.items(): x.to_csv(OUT/f'daily_{k}_{uk}.csv')
for kk,b in BASES.items(): b.to_csv(OUT/f'daily_BASE_{kk}.csv')
log('portfolio done')
# ---- event study U1: CAR open->open days e..e+H-1 vs SW L1 x size-decile EW within U1 at e-1
swi=np.full((NT,NC),-1,np.int16); codes={c:i for i,c in enumerate(sorted(sw.sw_code.unique()))}
swx=sw.copy(); swx['c']=swx.instrument_id
for r_ in swx.itertuples():
    if r_.c in ci: 
        i0=TD.searchsorted(r_.in_date); i1=TD.searchsorted(r_.out_date); swi[i0:i1,ci[r_.c]]=codes[r_.sw_code]
cum=np.vstack([np.zeros(NC),np.cumsum(np.log1p(RO.astype(float)),axis=0)])
ES=[]
for k in EV:
    ev=a[EV[k]][['ci','e']].drop_duplicates(); ev=ev[U1[ev.e.values-1,ev.ci.values]]
    for e_,g in ev.groupby('e'):
        u=np.nonzero(U1[e_-1])[0]; dec=pd.qcut(pd.Series(FMv[e_-1,u]).rank(method='first'),10,labels=False).values
        dmap=dict(zip(u,dec))
        for H in (5,20):
            if e_+H>NT: continue
            car_all=cum[e_+H]-cum[e_]
            for c in g.ci.values:
                peer=u[(dec==dmap.get(c,-9))&(swi[e_-1,u]==swi[e_-1,c])&(u!=c)]
                if len(peer)<3: peer=u[(dec==dmap.get(c,-9))&(u!=c)]
                ES.append((k,TD[e_],H,float(np.expm1(car_all[c])-np.mean(np.expm1(car_all[peer])))))
ES=pd.DataFrame(ES,columns=['ev','date','H','car']); ES.to_csv(OUT/'event_study_events.csv',index=False)
est=[]
for (k,H),g in ES.groupby(['ev','H']):
    dm=g.groupby('date').car.mean(); est.append(dict(ev=k,H=H,n=len(g),mean_car=float(g.car.mean()),nw_t=nw_t(dm.values,L=H)))
    for y,gg in g.groupby(g.date.dt.year): est.append(dict(ev=k,H=H,year=y,n=len(gg),mean_car=float(gg.car.mean())))
pd.DataFrame(est).to_csv(OUT/'event_study_summary.csv',index=False)
out=dict(prereg_sha256=PSHA,promotion_approved=False,research_only=True,events=evc,cols=NC,days=int(T_END-T_START+1),maxrss_MB=mem(),runtime_s=time.time()-t0)
json.dump(out,open(OUT/'results.json','w'),indent=1,default=str); log('done',out)
