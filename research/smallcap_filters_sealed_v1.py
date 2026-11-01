"""P5 SMALLCAP_FILTERS_SEALED_V1 — static small-cap basket + prereg filters. Research only, promotion_approved=False.
Prereg: docs/prereg/P5_SMALLCAP_FILTERS.md (sha d52a6646...). Control identical to capital_flow_sealed_v1.smallcap_ctrl."""
import gc, json, time, resource
from pathlib import Path
import numpy as np, pandas as pd
from math import erf, sqrt
t0=time.time(); ROOT=Path('/workspace/QuantLab'); V2=ROOT/'data/v2'; S=Path('/workspace/scratch/tic')
OUT=ROOT/'output/alpha/SMALLCAP_FILTERS_SEALED_V1'; OUT.mkdir(parents=True, exist_ok=True)
SEAL_S,SEAL_E,CONF_S=pd.Timestamp('2018-01-01'),pd.Timestamp('2024-05-31'),pd.Timestamp('2024-06-01')
COSTS=(25,50,100); mem=lambda: resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
ld=lambda c: pd.read_parquet(S/f'{c}.parquet').loc['2017-10-01':].astype('float32')
op=ld('open'); cols=[c for c in op.columns if c[:6] in ('sh.600','sh.601','sh.603','sh.605','sh.688','sh.689') or c[:5] in ('sz.00','sz.30')]
op=op[cols]; dates=op.index; ND,NC=op.shape; cix={c:i for i,c in enumerate(cols)}
fa=ld('factor')[cols].ffill().values; O=op.values; del op
C=ld('close')[cols].reindex(dates).values; lu=ld('limit_up')[cols].reindex(dates).values
ts=ld('tradestatus')[cols].reindex(dates).values
aO=O*fa; aC=C*fa; del fa
tradable=(ts==1)&np.isfinite(O)&(O>0); del ts
buyable=tradable & ~((O>=lu-0.005)&np.isfinite(lu))
LUC=((C>=lu-0.005)&np.isfinite(lu)&np.isfinite(C)); del lu
ovn=np.full_like(aO,np.nan); ovn[1:]=aO[1:]/aC[:-1]-1
intra=C/O-1; del C, aC
ovn=np.nan_to_num(np.clip(ovn,-0.5,0.5)).astype('float32'); intra=np.nan_to_num(np.clip(intra,-0.5,0.5)).astype('float32')
cs=lambda x: np.vstack([np.zeros((1,NC),x.dtype), np.cumsum(x,0)])  # cs[k]=sum rows <k
OV=cs(ovn); IN=cs(intra); del ovn, intra
fwd={}
for h in (5,20):
    f=np.full_like(aO,np.nan); f[:-h]=aO[h:]/aO[:-h]-1; fwd[h]=f.astype('float32')
del aO; gc.collect()
import pyarrow.parquet as pq
fm=pq.read_table(V2/'float_mktcap/float_mktcap_daily_tushare.parquet',columns=['trade_date','instrument_id','float_mktcap']).to_pandas(types_mapper=None)
fm=fm[fm.trade_date>='2017-10-01']; fm['instrument_id']=fm.instrument_id.astype('category'); fm['float_mktcap']=fm.float_mktcap.astype('float32'); fm=fm.drop_duplicates(['trade_date','instrument_id'],keep='last')
FMC=fm.pivot(index='trade_date',columns='instrument_id',values='float_mktcap').reindex(index=dates,columns=cols).ffill().astype('float32').values
del fm; gc.collect()
ti=pd.read_parquet(V2/'dragon_tiger/top_inst_labeled.parquet',columns=['trade_date','ts_code','exalter','buy','sell','net_buy','seat_type'])
ti=ti.drop_duplicates(['trade_date','ts_code','exalter','buy','sell'])
ti['hot']=np.where(ti.seat_type=='retail_or_hot_money',ti.net_buy,0.0)
ev=ti.groupby(['trade_date','ts_code']).hot.sum().reset_index(); del ti
ev['col']=(ev.ts_code.str[-2:].str.lower()+'.'+ev.ts_code.str[:6]).map(cix); ev=ev[ev.col.notna()]
T=pd.to_datetime(ev.trade_date).values; p=np.searchsorted(dates.values,T); ok=(p<ND)
ok[ok]&=(dates.values[p[ok]]==T[ok]); ev=ev[ok]; p=p[ok]
L=np.zeros((ND,NC),np.int16); Lh=np.zeros((ND,NC),np.int16)
np.add.at(L,(p,ev.col.values.astype(int)),1); hp=ev.hot.values>0; np.add.at(Lh,(p[hp],ev.col.values[hp].astype(int)),1)
LC=cs(L.astype(np.int32)); LHC=cs(Lh.astype(np.int32)); LUCC=cs(LUC.astype(np.int32)); del L,Lh,LUC
print('panels',ND,NC,f'{time.time()-t0:.0f}s maxrss {mem():.0f}MB',flush=True)
def win(cum,a,b):  # sum over rows a..b inclusive
    a=max(a,0); return cum[b+1]-cum[a]
def topq(x,mem_,q=0.2,top=True):
    v=x[mem_]; k=int(np.floor(len(v)*q)); 
    if k==0: return np.zeros(len(mem_),bool)
    o=np.argsort(v); idx=o[-k:] if top else o[:k]; m=np.zeros(len(v),bool); m[idx]=True; return m
def drop(name,d,mem_,lag):
    e=d-lag  # lag=0 primary
    if name=='C0': return np.zeros(len(mem_),bool)
    if name=='F1a_LHB_N5': return win(LC,e-6,e-2)[mem_]>0
    if name=='F1b_LHB_N20': return win(LC,e-21,e-2)[mem_]>0
    if name=='F1c_LHB_HOT_N20': return win(LHC,e-21,e-2)[mem_]>0
    if name=='F2a_OVN20_TOP': return topq(win(OV,e-20,e-1),mem_,top=True)
    if name=='F2b_OVN5_TOP': return topq(win(OV,e-5,e-1),mem_,top=True)
    if name=='F2c_INTRA20_BOT': return topq(win(IN,e-20,e-1),mem_,top=False)
    if name=='F3a_LU_D1': return win(LUCC,e-1,e-1)[mem_]>0
    if name=='F3b_LU_5D': return win(LUCC,e-5,e-1)[mem_]>0
VARS=['C0','F1a_LHB_N5','F1b_LHB_N20','F1c_LHB_HOT_N20','F2a_OVN20_TOP','F2b_OVN5_TOP','F2c_INTRA20_BOT','F3a_LU_D1','F3b_LU_5D']
def run(name,h,kind,lag=0):
    wm=(dates>=SEAL_S)&(dates<=SEAL_E) if kind=='sealed' else (dates>=CONF_S)
    idx=np.where(wm)[0]; idx=idx[idx<ND-h]; reb=idx[::h]; rows=[]; prev=None
    for d in reb:
        x=FMC[d-1]; ok=buyable[d]&np.isfinite(x)
        if ok.sum()<100: continue
        thr=np.nanquantile(x[ok],1/3); m=np.where(ok&(x<=thr))[0]; nb=len(m)
        m=m[~drop(name,d,m,lag)]
        rr=float(np.mean(np.nan_to_num(fwd[h][d,m],nan=0.0)))
        s=set(m.tolist()); f=1.0 if prev is None else 1-len(s&prev)/max(len(s),1); prev=s
        rows.append((dates[d],rr,f,len(m),nb))
    return pd.DataFrame(rows,columns=['date','gross','turn','n','n_base'])
def ann(r,h): r=np.asarray(r); y=len(r)*h/244; return np.prod(1+r)**(1/y)-1
def stats(df,h):
    o={'gross_ann':ann(df.gross,h)}
    for cb in COSTS: o[f'net{cb}_ann']=ann(df.gross-2*df.turn*cb/1e4,h)
    n25=df.gross-2*df.turn*50/1e4*0.5
    o['sharpe_net25']=float(n25.mean()/n25.std()*np.sqrt(244/h)); w=np.cumprod(1+n25.values); o['maxdd_net25']=float((w/np.maximum.accumulate(w)-1).min())
    o['turn_oneway']=float(df.turn.mean()); o['avg_n']=float(df.n.mean()); o['avg_dropped_frac']=float(1-(df.n/df.n_base).mean())
    o['chk_compound_eq_total']=bool(abs((1+o['gross_ann'])**(len(df)*h/244)-np.prod(1+df.gross))<1e-6*max(1,np.prod(1+df.gross)))
    return o
def pt(a,b):
    dd=np.asarray(a)-np.asarray(b); t=dd.mean()/(dd.std(ddof=1)/np.sqrt(len(dd))); pv=2*(1-0.5*(1+erf(abs(t)/sqrt(2)))); return float(t),float(pv),float(dd.mean())
def nw_t(dd,h):  # non-overlapping already (rebalance every h); plain t
    return pt(dd,np.zeros(len(dd)))[0]
RES={}; BY=[]; SER={}
for kind in ('sealed','confirm'):
    for h in (5,20):
        for lag in (0,1):
            if kind=='confirm' and lag==1: continue
            base=run('C0',h,kind,lag); SER[(kind,h,lag,'C0')]=base
            for v in VARS:
                df=base if v=='C0' else run(v,h,kind,lag); SER[(kind,h,lag,v)]=df
                st=stats(df,h); n25v=df.gross-2*df.turn*25/1e4; n25c=base.gross-2*base.turn*25/1e4
                t,pv,md=pt(n25v,n25c); st.update(delta_net25_ann=st['net25_ann']-stats(base,h)['net25_ann'],paired_t_net25=t,paired_p=pv,mean_period_delta=md)
                yr=df.assign(y=df.date.dt.year,r=n25v,c=n25c).groupby('y').apply(lambda g: pd.Series({'net25':ann(g.r,h),'ctrl25':ann(g.c,h)}))
                st['by_year_net25']={int(k):float(r.net25) for k,r in yr.iterrows()}; st['by_year_delta']={int(k):float(r.net25-r.ctrl25) for k,r in yr.iterrows()}
                if kind=='sealed':
                    sub={}
                    for nm,(a,b) in {'2018-2020':('2018','2020-12-31'),'2021-2023-09':('2021','2023-09-30'),'2023-10-2024-05':('2023-10','2024-05-31')}.items():
                        mk=(df.date>=a)&(df.date<=b); sub[nm]=float(ann(n25v[mk],h)-ann(n25c[mk],h))
                    st['subperiod_delta']=sub
                RES[f'{kind}|h{h}|lag{lag}|{v}']=st
                print(kind,h,lag,v,f"net25 {st['net25_ann']:.3f} d {st['delta_net25_ann']:+.3f} t {t:.2f}",f'{mem():.0f}MB',flush=True)
# BY over 16 primary sealed comparisons
keys=[f'sealed|h{h}|lag0|{v}' for v in VARS[1:] for h in (5,20)]
ps=np.array([RES[k]['paired_p'] for k in keys]); m=len(ps); o=np.argsort(ps); cm=np.sum(1/np.arange(1,m+1))
q=np.empty(m); q[o]=np.minimum.accumulate((ps[o]*m*cm/np.arange(1,m+1))[::-1])[::-1]; q=np.minimum(q,1)
for k,qq in zip(keys,q): RES[k]['BY_q']=float(qq); RES[k]['bonf_p']=float(min(1,RES[k]['paired_p']*m))
rows=[{'key':k,**{kk:vv for kk,vv in v.items() if not isinstance(vv,dict)}} for k,v in RES.items()]
pd.DataFrame(rows).to_csv(OUT/'results.csv',index=False)
for (kind,h,lag,v),df in SER.items():
    if lag==0: df.to_csv(OUT/f'series_{kind}_h{h}_{v}.csv',index=False)
json.dump({'promotion_approved':False,'research_only':True,'run_id':'SMALLCAP_FILTERS_SEALED_V1','prereg':'docs/prereg/P5_SMALLCAP_FILTERS.md','prereg_sha256':'d52a6646b00f98d8a85759d03de058aa46d5684bc59d1645d2dec923e1c68eb9','n_primary_trials':16,'n_lag_sens':16,'results':RES,'runtime_s':time.time()-t0,'maxrss_MB':mem()},open(OUT/'summary.json','w'),ensure_ascii=False,indent=1,default=str)
print('done',f'{time.time()-t0:.0f}s',f'{mem():.0f}MB')
