"""P6 SMALLCAP_COMBO — Beta strict small-cap basket (B0) + LHB20/LU5 exclusions + one vol-target DD variant.
Research only, promotion_approved=False. Prereg docs/prereg/P6_SMALLCAP_COMBO.md (sha 01c41439...)."""
import sys, json, math, time, gc, resource, pickle
from pathlib import Path
import numpy as np, pandas as pd
from math import erf, sqrt
ROOT=Path('/workspace/QuantLab'); sys.path.insert(0,str(ROOT)); sys.path.insert(0,str(ROOT/'scripts'))
import smallcap_reconcile as R
from quantlab.platform.execution import ExecConfig, run_weight_schedule
OUT=ROOT/'output/alpha/SMALLCAP_COMBO_P6'; OUT.mkdir(parents=True,exist_ok=True)
PREREG_SHA='01c414394472702261431f6977780d346f4a8dce4e64049cd5cd689cdcf81de1'
mem=lambda: resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
t0=time.time(); log=lambda *a: print(f'[p6 {time.time()-t0:6.0f}s {mem():.0f}MB]',*a,flush=True)
WIN={'sealed':('2018-01-02','2024-05-31'),'confirm':('2024-06-03','2026-10-08')}
K={**R.ORIG,'band':'cap','fund':True,'excl':True,'ind_cap':12}

# ---------- step 0: reproduce Beta FINAL (no trial) ----------
rep=R.run_rows([('FINAL_REPRO','Beta FINAL repro',K,'eng',True,'strict',1.0,0.5,'dev')],'p6_repro_tmp')[0]
(R.OUT/'p6_repro_tmp.json').unlink(missing_ok=True)
json.dump(rep,open(OUT/'beta_repro.json','w'),indent=1,default=str); log('repro',rep['cagr'],rep['mdd'])
R._PCACHE.clear(); gc.collect()

# ---------- exclusion panels ----------
S=Path('/workspace/scratch/tic')
cl=pd.read_parquet(S/'close.parquet').loc['2017-10-01':]; lu=pd.read_parquet(S/'limit_up.parquet').loc['2017-10-01':].reindex(index=cl.index,columns=cl.columns)
LUC=((cl>=lu-0.005)&lu.notna()&cl.notna()); del cl,lu; gc.collect()
TD=LUC.index
ti=pd.read_parquet(ROOT/'data/v2/dragon_tiger/top_inst_labeled.parquet',columns=['trade_date','ts_code'])
ti['c']=ti.ts_code.str[-2:].str.lower()+'.'+ti.ts_code.str[:6]; ti['d']=pd.to_datetime(ti.trade_date)
LHB=ti.groupby('d').c.apply(set).to_dict(); del ti
def ban_sets(s):
    i=TD.searchsorted(s,side='right')-1  # index of s (or last <= s)
    lhb=set().union(*[LHB.get(d,set()) for d in TD[max(0,i-19):i]])  # s-19..s-1
    w=LUC.iloc[max(0,i-4):i+1]; luset=set(w.columns[w.any(axis=0).values])  # s-4..s
    return lhb,luset

# ---------- selector with ban (copy of Beta select with pool exclusion) ----------
def baskets(win,every,var):
    s,e=WIN[win]; idx=fm.index[(fm.index>=pd.Timestamp(s))&(fm.index<=pd.Timestamp(e))]
    dates=list(idx[::every]); out={}; prev=None; nb=[]
    for d in dates:
        lhb,lus=ban_sets(d); ban=set()
        if var in ('B1','B3','B4'): ban|=lhb
        if var in ('B2','B3','B4'): ban|=lus
        b=select_ban(d,prev,ban); out[d]=b; prev=b; nb.append(len(ban))
    return dates,out
# wrap: R.make_selector's select has no ban arg -> reproduce by filtering via st_on hook
import quantlab.beta.smallcap_history_selector as H
_st_orig=R.__dict__.get('st_on')
def select_ban(d,prev,ban):
    # Beta select uses st_on(day) (imported inside make_selector closure) for exclusion; emulate ban by temporarily
    # adding banned ids to the 'st' set via the excl branch: implemented by patched st function
    BAN[0]=ban; return select(d,prev,{**K,'end':WIN['confirm'][1]})
BAN=[set()]
_orig_st=H.st_on
def st_patched(day): return set(_orig_st(day))|BAN[0]
# rebind inside closure: make_selector imported st_on by name at call time -> re-create selector after patching
H.st_on=st_patched; select,fm=R.make_selector()

VARS=['B0','B1','B2','B3','B4']
BK={}
for win in ('sealed','confirm'):
    for every in (5,20):
        for v in ('B0','B1','B2','B3'):
            BK[(win,every,v)]=baskets(win,every,v); log('basket',win,every,v,len(BK[(win,every,v)][0]))
pickle.dump(BK,open(Path('/workspace/scratch/p6_baskets.pkl'),'wb'))
H.st_on=_orig_st; del fm; gc.collect()

ZERO=ExecConfig(fill='next_open',commission=0.0,min_commission=0.0,stamp_before=0.0,stamp_after=0.0,slippage=0.0,impact_k=0.0,
                participation_cap=None,lots=True,enforce_limits=True,unfilled='carry',order_rounding='target',price_tick='auto')
def run(p,sched,cfg,cap,start):
    r=run_weight_schedule(p,sched,initial_cash=cap,config=cfg,record_weights=True)
    return r['nav'].loc[pd.Timestamp(start):],r
def traded(p,aw,nav):
    aw=aw.fillna(0.0); px=p.close.reindex(aw.index)[aw.columns].ffill()
    rr=(px/px.shift(1)-1).fillna(0.0); R_=nav.reindex(aw.index).pct_change().fillna(0.0)
    drift=aw.shift(1).fillna(0.0)*(1+rr).values/(1+R_.values[:,None])
    return (aw-drift).abs().sum(axis=1)
def stats(nav):
    r=nav.pct_change().dropna(); y=len(r)/244; cagr=(nav.iloc[-1]/nav.iloc[0])**(1/y)-1
    dd=nav/nav.cummax()-1; mdd=float(dd.min())
    # longest drawdown duration (days below prior peak)
    under=(dd<0).astype(int).values; best=cur=0
    for u in under: cur=cur+1 if u else 0; best=max(best,cur)
    return dict(ann=float(cagr),sharpe=float(r.mean()/r.std()*math.sqrt(244)),mdd=mdd,dd_days=int(best),calmar=float(cagr/abs(mdd)) if mdd<0 else None,
                by_year={int(k):float((1+g).prod()-1) for k,g in r.groupby(r.index.year)})
def period_rets(nav,dates):
    pts=[d for d in dates if d in nav.index]+[nav.index[-1]]; v=nav.reindex(pts).values
    return pd.Series(v[1:]/v[:-1]-1,index=pts[:-1])
RES={}; SER={}
for win in ('sealed','confirm'):
    s,e=WIN[win]
    for every in (5,20):
        b3dates=None
        for v in VARS:
            dates,B=BK[(win,every,'B3' if v=='B4' else v)]
            w={d:1.0 for d in dates}
            if v=='B4':
                g=SER[(win,every,'B3','gross')]; r=g.pct_change(); sig=r.rolling(60,min_periods=40).std()*math.sqrt(244)
                w={d:float(min(1.0,0.20/sig.loc[:d].iloc[-1])) if np.isfinite(sig.loc[:d].iloc[-1]) else 1.0 for d in dates}
            sched={d:{c:w[d]/len(B[d]) for c in B[d]} for d in dates if B[d]}
            ids=sorted({c for x in B.values() for c in x}); p,_=R.panels_for(ids,s,e,True)
            gnav,gr=run(p,sched,ZERO,5e7,s); tr=traded(p,gr['actual_weights'],gr['nav']).reindex(gnav.index).fillna(0.0)
            gret=gnav.pct_change().fillna(0.0); SER[(win,every,v,'gross')]=gnav
            o={'n_ids':len(ids),'avg_weight':float(np.mean(list(w.values()))),'turnover_oneway_ann':float(tr.sum()/2/(len(tr)/244)),'gross':stats(gnav)}
            for cb in (25,50,100):
                n=(1+gret-tr*cb/1e4).cumprod(); SER[(win,every,v,f'flat{cb}')]=n; o[f'flat{cb}']=stats(n)
            caps=(1e7,5e7,2e8) if win=='sealed' else (5e7,)
            for cap in caps:
                nav,r=run(p,sched,ExecConfig.strategy_v1(impact_k=1.0,min_trade_value=2000.0),cap,s); nav=nav/nav.iloc[0]
                key=f'impact_{cap:.0e}'; o[key]=stats(nav); o[key]['cost_frac_ann']=float(r['total_cost']/cap/(len(nav)/244)); o[key]['fill_ratio']=float(r['fill_ratio'])
                o[key]['costs']={k:round(float(x)) for k,x in r['costs'].items()}; SER[(win,every,v,key)]=nav
                if cap==5e7:
                    for sc in (0.5,1.0):
                        dn,hits=R.delist_overlay(nav*1.0,r['actual_weights'].reindex(nav.index),sc); o[f'delist{int(sc*100)}_5e7']={**stats(dn),'hits':hits}
            if v!='B0':
                for ck in ('flat25',f'impact_5e+07'):
                    a=period_rets(SER[(win,every,v,ck)],dates); bb=period_rets(SER[(win,every,'B0',ck)],dates)
                    dd=(a-bb).dropna(); t=dd.mean()/(dd.std(ddof=1)/np.sqrt(len(dd))); pv=2*(1-0.5*(1+erf(abs(t)/sqrt(2))))
                    o[f'delta_{ck}']=dict(d_ann=o[ck]['ann']-RES[f'{win}|h{every}|B0'][ck]['ann'],t=float(t),p=float(pv),n=len(dd),
                        by_year_delta={y:o[ck]['by_year'][y]-RES[f'{win}|h{every}|B0'][ck]['by_year'][y] for y in o[ck]['by_year']})
            RES[f'{win}|h{every}|{v}']=o
            log(win,every,v,f"flat25 {o['flat25']['ann']:.4f} imp5e7 {o['impact_5e+07']['ann']:.4f} mdd {o['flat25']['mdd']:.3f}")
            del p,gr; R._PCACHE.clear(); gc.collect()
# BY across P5 (16) + P6 (8)
p5=json.load(open(ROOT/'output/alpha/SMALLCAP_FILTERS_SEALED_V1/summary.json'))['results']
fam=[(k,v['paired_p']) for k,v in p5.items() if 'BY_q' in v]+[(f'P6|sealed|h{h}|{v}',RES[f'sealed|h{h}|{v}']['delta_flat25']['p']) for v in VARS[1:] for h in (5,20)]
ps=np.array([x[1] for x in fam]); m=len(ps); o_=np.argsort(ps); cm=np.sum(1/np.arange(1,m+1))
q=np.empty(m); q[o_]=np.minimum.accumulate((ps[o_]*m*cm/np.arange(1,m+1))[::-1])[::-1]; q=np.minimum(q,1)
BYQ={k:float(qq) for (k,_),qq in zip(fam,q)}
for v in VARS[1:]:
    for h in (5,20): RES[f'sealed|h{h}|{v}']['delta_flat25']['BY_q']=BYQ[f'P6|sealed|h{h}|{v}']
pd.DataFrame({'|'.join(map(str,k)):s for k,s in SER.items()}).to_csv(OUT/'nav_series.csv')
json.dump({'promotion_approved':False,'research_only':True,'run_id':'SMALLCAP_COMBO_P6','prereg':'docs/prereg/P6_SMALLCAP_COMBO.md','prereg_sha256':PREREG_SHA,
           'beta_repro':rep,'n_primary_trials':8,'BY_family_size':m,'BY_family':BYQ,'results':RES,'runtime_s':time.time()-t0,'maxrss_MB':mem()},
          open(OUT/'summary.json','w'),ensure_ascii=False,indent=1,default=str)
log('done')
