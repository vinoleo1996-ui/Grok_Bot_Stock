# V3 A1 sealed run (prereg docs/prereg/V3_A1_LIMIT_T1_EXECUTION.md). Research only. Each arm run once.
import pandas as pd, numpy as np, glob, os, json, math, hashlib, resource, time, sys
from math import erf, sqrt
ROOT='/workspace/QuantLab'; OUT=ROOT+'/output/alpha/V3_A1_A2_SEALED'; os.makedirs(OUT,exist_ok=True)
sys.path.insert(0,ROOT)
from quantlab.platform.execution import sqrt_impact_cost
PRE=ROOT+'/docs/prereg/V3_A1_LIMIT_T1_EXECUTION.md'; PSHA=hashlib.sha256(open(PRE,'rb').read()).hexdigest()
SEAL_END=pd.Timestamp('2024-05-31'); CONF_START=pd.Timestamp('2024-06-03')
mem=lambda: resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
t0=time.time(); LOG=open(OUT+'/run.log','w')
def log(*a):
    s=' '.join(str(x) for x in a); print(s,flush=True); LOG.write(s+'\n'); LOG.flush()
log('prereg sha',PSHA)
# ---------- panel ----------
D0=ROOT+'/data/local_market/1c85fd9aceaa03c3c4863bec/panels'
cols=['open','high','low','close','amount','factor','limit_up','limit_down','tradestatus','is_st_at_open','limit_ratio_at_open']
fr=[]
for f in glob.glob(D0+'/*.parquet'):
    if os.path.basename(f).startswith(('bj.','._')): continue
    d=pd.read_parquet(f)
    if 'event_time' in d.columns: d=d.set_index('event_time')
    d.index=pd.to_datetime(d.index); d=d[d.index>='2017-11-01']
    if len(d)==0: continue
    d=d[[c for c in cols if c in d.columns]].astype('float32').reset_index(); d.columns=['date']+list(d.columns[1:])
    d['inst']=os.path.basename(f)[:-8]; fr.append(d)
p=pd.concat(fr,ignore_index=True); del fr
p['inst']=p.inst.astype('category')
log('panel',p.shape,p.date.min(),p.date.max(),'mem',mem())
p=p.sort_values(['inst','date']).reset_index(drop=True)
for c in ['open','high','low','close']: p[c[0]+'a']=(p[c]*p.factor).astype('float32')
p['vw']=((p.oa+p.ha+p.la+p.ca)/4).astype('float32')
TOL=0.005
p['seal']=p.close>=p.limit_up-TOL; p['zhab']=(p.high>=p.limit_up-TOL)&~p.seal
p['dseal']=p.close<=p.limit_down+TOL; p['qiao']=(p.low<=p.limit_down+TOL)&~p.dseal
g=p.groupby('inst',observed=True)
p['ret']=g.ca.pct_change()
p['sig20']=g.ret.transform(lambda s:s.shift(1).rolling(20,min_periods=10).std()).astype('float32')
p['adv20']=g.amount.transform(lambda s:s.shift(1).rolling(20,min_periods=10).mean()).astype('float32')
p=p.drop(columns=['ha','la','amount','is_st_at_open'][:0]); log('features mem',mem())
# ---------- step 0: state table in sealed window (top1500 universe) ----------
f=pd.read_parquet(ROOT+'/data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet',columns=['instrument_id','trade_date','float_mktcap'])
f=f.rename(columns={'instrument_id':'inst','trade_date':'date'}); f['date']=pd.to_datetime(f.date); f=f[f.date>='2017-11-01']
f['inst']=f.inst.str.lower().str.replace(r'^(\d{6})\.(sh|sz)$',lambda m:m.group(2)+'.'+m.group(1),regex=True) if not f.inst.iloc[0][:2].isalpha() else f.inst
f['rk']=f.groupby('date').float_mktcap.rank(ascending=False); f=f.sort_values(['inst','date']); f['rk']=f.groupby('inst').rk.shift(1)
s=p[['inst','date','oa','ca','tradestatus','is_st_at_open','seal','zhab','dseal','qiao','limit_ratio_at_open','ret','high','limit_up']].copy()
s['inst']=s.inst.astype(str)
gs=s.groupby('inst'); s['no']=gs.oa.shift(-1); s['nc']=gs.ca.shift(-1); s['no2']=gs.oa.shift(-2)
s['on1']=s.no/s.ca-1; s['id1']=s.nc/s.no-1; s['oo']=s.no2/s.no-1
s=s.merge(f[['inst','date','rk']],on=['inst','date'],how='left'); del f
log('rk match rate',float(s.rk.notna().mean()))
s=s[(s.rk<=1500)&(s.tradestatus==1)&(s.is_st_at_open==0)&(s.date>='2018-01-02')]
for c in ['on1','id1','oo']: s['x'+c]=s[c]-s.groupby('date')[c].transform('mean')
def st(m,name,sub):
    q=sub[m]; dm=q.groupby('date')[['xon1','xid1','xoo']].mean(); n=len(dm)
    r={'state':name,'N':int(len(q)),'days':n}
    for c in ['xon1','xid1','xoo']:
        x=dm[c].dropna(); r[c+'_bp']=float(x.mean()*1e4); r[c+'_t']=float(x.mean()/x.std()*np.sqrt(len(x))) if len(x)>2 else None
    return r
rows=[]
for win,sub in [('sealed',s[s.date<=SEAL_END]),('confirm',s[s.date>=CONF_START])]:
    b20=sub.limit_ratio_at_open>=0.19
    fake=(~b20)&(sub.ret>=0.09)&(sub.ret<=0.095)&(sub.high<sub.limit_up-TOL)
    for m,n in [(sub.seal,'seal'),(sub.zhab,'zhaban'),(sub.dseal,'dseal'),(sub.qiao,'qiaoban'),(sub.seal&b20,'seal_20pct'),(sub.seal&~b20,'seal_10pct'),(sub.zhab&b20,'zhaban_20pct'),(sub.zhab&~b20,'zhaban_10pct'),(fake,'placebo_fake_seal')]:
        r=st(m,n,sub); r['window']=win; rows.append(r)
    if win=='sealed':
        for y,sy in sub.groupby(sub.date.dt.year):
            for m,n in [(sy.seal,'seal'),(sy.zhab,'zhaban')]:
                r=st(m,n,sy); r['window']=f'sealed_{y}'; rows.append(r)
ST=pd.DataFrame(rows); ST.to_csv(OUT+'/state_table.csv',index=False); log(ST.to_string())
sd=ST[ST.window=='sealed'].set_index('state')
signs={'seal_on>0':sd.loc['seal','xon1_bp']>0,'seal_id<0':sd.loc['seal','xid1_bp']<0,'zhaban_on<0':sd.loc['zhaban','xon1_bp']<0,'zhaban_id>0':sd.loc['zhaban','xid1_bp']>0}
log('signs',signs); del s
RES={'promotion_approved':False,'research_only':True,'prereg':'docs/prereg/V3_A1_LIMIT_T1_EXECUTION.md','prereg_sha256':PSHA,'step0_signs':{k:bool(v) for k,v in signs.items()}}
if not all(signs.values()):
    RES['status']='STOPPED_step0_sign_mismatch'; json.dump(RES,open(OUT+'/results.json','w'),indent=1,default=str); log('STOP'); sys.exit(0)
# ---------- step 2: CSI300 EW book ----------
iw=pd.read_parquet(ROOT+'/data/v2/index_members/index_weight_csi300_500_1000.parquet')
iw=iw[iw.index_code=='000300.SH']; iw['inst']=iw.con_code.str[-2:].str.lower()+'.'+iw.con_code.str[:6]; iw['snap']=pd.to_datetime(iw.trade_date)
snaps=sorted(iw.snap.unique()); mem300={sn:set(iw[iw.snap==sn].inst) for sn in snaps}
names=sorted(set(iw.inst)); p=p[p.inst.astype(str).isin(names)].copy(); p['inst']=p.inst.astype(str)
dates=sorted(p.date[p.date>='2018-01-02'].unique()); D=pd.DatetimeIndex(dates)
def piv(c): return p.pivot(index='date',columns='inst',values=c).reindex(index=D,columns=names)
O=piv('oa').ffill(); C=piv('ca').ffill(); VW=piv('vw'); 
O=O.fillna(C).ffill()  # suspended: last price
VW=VW.fillna(O)
TS=piv('tradestatus').fillna(0).values>0
OPEN_RAW=piv('open').values; LU=piv('limit_up').values; LD=piv('limit_down').values
canbuy=TS&~(OPEN_RAW>=LU-TOL); cansell=TS&~(OPEN_RAW<=LD+TOL)
SEAL=piv('seal').fillna(False).values.astype(bool)&TS; BAD=(piv('zhab').fillna(False).values.astype(bool)|piv('dseal').fillna(False).values.astype(bool))&TS
SIG=piv('sig20').values; ADV=piv('adv20').values; Ov=O.values; Vv=VW.values; Cv=C.values
Ov=np.where(np.isfinite(Ov),Ov,np.nan); del p
T,N=Ov.shape; log('book matrix',T,N,'mem',mem())
reb=np.zeros(T,bool); reb[0]=True
for i in range(1,T): reb[i]=D[i].month!=D[i-1].month
memb=np.zeros((T,N),bool); ni={n:j for j,n in enumerate(names)}
for i in range(T):
    if not reb[i]: continue
    prev=[sn for sn in snaps if sn<D[i]]
    if not prev: continue
    for n in mem300[prev[-1]]: memb[i,ni[n]]=True
cool=np.zeros((T,N),bool)  # cooldown: BAD at t -> no buy t+1..t+3
for k in (1,2,3): cool[k:]|=BAD[:-k]
stamp=np.where(D<pd.Timestamp('2023-08-28'),0.001,0.0005)
COSTS=[('flat25',25e-4,None),('flat50',50e-4,None),('flat100',100e-4,None),('imp5e7',None,5e7),('imp2e8',None,2e8)]
def sim(arm,cost):
    _,bp,cap=cost; T1=arm in('T1','T4'); T2=arm in('T2','T4'); T3=arm in('T3','T4')
    q=np.zeros(N); cash=1.0; nav=np.zeros(T); turn=0.0; trig=0; pend=np.zeros(N)  # pend: cash earmarked for rebuy
    cur=np.zeros(N,bool)
    for i in range(T):
        px=np.nan_to_num(Ov[i]); val=q*px; V=cash+val.sum(); nav[i]=V
        scale=(cap or 1.0)/1.0
        sells=np.zeros(N); buys=np.zeros(N)
        if reb[i] and memb[i].any():
            cur=memb[i]; pend[:]=0
            elig=cur&canbuy[i]
            if T2: elig&=~cool[i]
            # names held but untradable stay; target EW over eligible using remaining value
            stuck=(val>0)&~cansell[i]&~(cur&~canbuy[i]&False)
            keep_val=val[stuck].sum()
            tgt=np.zeros(N)
            if elig.sum()>0: tgt[elig]=(V-keep_val)/elig.sum()
            tgt[stuck]=val[stuck]
            # held members not eligible-to-buy but sellable: keep existing (no forced sale) if member; sell non-members
            hold_ok=cur&~elig&~stuck&(val>0)
            if hold_ok.any():
                tgt[hold_ok]=val[hold_ok]; free=V-tgt[stuck|hold_ok].sum()
                tgt[elig]=free/max(elig.sum(),1)
            d=tgt-val; sells=np.where(d<0,-d,0)*cansell[i]; buys=np.where(d>0,d,0)*canbuy[i]
        else:
            if T1 and i>0:
                # rebuy pending
                rb=(pend>0)&canbuy[i]
                if T2: rb&=~cool[i]
                buys[rb]=pend[rb]; pend[rb]=0
                # sell after seal yesterday
                sl=SEAL[i-1]&(q>0)&cansell[i]
                sells[sl]=val[sl]; trig+=int(sl.sum())
        # rebalance-day seal sells for T1 too (sell held names sealed yesterday, defer their buy)
        if T1 and reb[i] and i>0:
            sl=SEAL[i-1]&cansell[i]&((val>0)|(buys>0))
            tv=np.where(sl,np.maximum(val-sells,0),0); pend[sl]+=buys[sl]+tv[sl]; sells=sells+tv; buys[sl]=0; trig+=int((sl&(val>0)).sum())
        # leftover pending for sold names set when sold on non-reb days
        if T1 and not reb[i] and i>0:
            sl=SEAL[i-1]&(val>0)&cansell[i]; pend[sl]+=sells[sl]
        # execute
        bpx=Vv[i] if T3 else Ov[i]
        q-=np.divide(sells,px,out=np.zeros(N),where=px>0)
        cash+=sells.sum()
        if bp is not None: c=bp*(sells.sum()+buys.sum())
        else:
            m=cap; tv_s=sells*m; tv_b=buys*m
            imp=sqrt_impact_cost(tv_s,ADV[i],SIG[i]).sum()+sqrt_impact_cost(tv_b,ADV[i],SIG[i]).sum()
            com=np.maximum(2.5e-4*tv_s,5.0*(tv_s>0)).sum()+np.maximum(2.5e-4*tv_b,5.0*(tv_b>0)).sum()
            c=(imp+com+stamp[i]*tv_s.sum())/m
        cash-=c
        # buys: spend, but cap by available cash (excluding pending earmarks is implicit)
        tb=buys.sum()
        if tb>cash and tb>0: buys*=max(cash,0)/tb
        bp_=np.nan_to_num(bpx)
        q+=np.divide(buys,bp_,out=np.zeros(N),where=bp_>0); cash-=buys.sum()
        turn+=sells.sum()/V if V>0 else 0
    return nav,turn,trig
def stats(nav,mask):
    x=pd.Series(nav[mask]); r=x.pct_change().dropna(); yrs=len(x)/244
    cagr=(x.iloc[-1]/x.iloc[0])**(1/yrs)-1; mdd=float((x/x.cummax()-1).min())
    return dict(cagr=float(cagr),sharpe=float(r.mean()/r.std()*sqrt(244)),mdd=mdd)
WIN={'sealed':np.asarray(D<=SEAL_END),'confirm':np.asarray(D>=CONF_START)}
NAV={}; R=[]
for cst in COSTS:
    for arm in ['BASE','T1','T2','T3','T4']:
        nav,turn,trig=sim(arm,cst); NAV[(arm,cst[0])]=nav
        log(arm,cst[0],'final',round(nav[-1],4),'trig',trig,'mem',round(mem()))
        R.append(dict(arm=arm,cost=cst[0],turn_total=turn,triggers=trig))
pd.DataFrame({f'{a}|{c}':v for (a,c),v in NAV.items()},index=D).to_parquet(OUT+'/navs.parquet')
out=[]
for arm in ['T1','T2','T3','T4']:
    for cst in [c[0] for c in COSTS]:
        for w,m in WIN.items():
            a=NAV[(arm,cst)]; b=NAV[('BASE',cst)]
            sa,sb=stats(a,m),stats(b,m)
            ra=pd.Series(a[m]).pct_change().dropna(); rb=pd.Series(b[m]).pct_change().dropna(); dd=ra-rb
            t=float(dd.mean()/(dd.std(ddof=1)/np.sqrt(len(dd)))) if dd.std()>0 else 0.0
            p1=1-0.5*(1+erf(t/sqrt(2)))
            out.append(dict(arm=arm,cost=cst,window=w,cagr_arm=sa['cagr'],cagr_base=sb['cagr'],inc_cagr=sa['cagr']-sb['cagr'],t=t,p_one=p1,mdd_arm=sa['mdd'],mdd_base=sb['mdd'],sharpe_arm=sa['sharpe'],sharpe_base=sb['sharpe']))
        # by year (sealed+confirm)
        a=pd.Series(NAV[(arm,cst)],index=D); b=pd.Series(NAV[('BASE',cst)],index=D)
        for y in sorted(set(D.year)):
            m=D.year==y; out.append(dict(arm=arm,cost=cst,window=f'y{y}',inc_cagr=float(a[m].iloc[-1]/a[m].iloc[0]-b[m].iloc[-1]/b[m].iloc[0])))
O_=pd.DataFrame(out)
# BY on flat25 sealed, family = runnable arms (A2 blocked)
x=O_[(O_.cost=='flat25')&(O_.window=='sealed')].copy(); m=len(x); cm=sum(1/k for k in range(1,m+1))
x=x.sort_values('p_one'); x['rank']=range(1,m+1); x['q']=(x.p_one*m*cm/x['rank']).iloc[::-1].cummin().iloc[::-1].clip(upper=1)
O_=O_.merge(x[['arm','q']].assign(cost='flat25',window='sealed'),on=['arm','cost','window'],how='left')
O_.to_csv(OUT+'/increments.csv',index=False); pd.DataFrame(R).to_csv(OUT+'/turnover_triggers.csv',index=False)
RES.update(status='done',base_book='CSI300 EW monthly (snapshot<rebalance date), open-to-open',dates=[str(D[0].date()),str(D[-1].date())],n_names=N,runtime_s=time.time()-t0,maxrss_MB=mem(),by_family_size=m)
json.dump(RES,open(OUT+'/results.json','w'),indent=1,default=str)
log(O_[O_.window.isin(['sealed','confirm'])].to_string()); log('done',time.time()-t0,'maxrss',mem())
