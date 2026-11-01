import sys; sys.path.insert(0,'/workspace/QuantLab/research')
import pandas as pd, numpy as np, json, optimizer_lambda_calib_sealed as C
OUT='/workspace/QuantLab/output/strategy_optimizer/core_x2/'
disc=pd.read_csv(OUT+'core_v1_3_disclosure.csv'); ex=pd.read_csv(OUT+'core_v1_3_lot_exclusions.csv')
W={}
for sv in ['equity_100','equity80_etf20_510300']:
    for a,t in [(600000,'60w'),(1000000,'100w')]:
        w=pd.read_parquet(OUT+f'core_{sv}_{t}.parquet'); W[(a,sv)]=w[w.is_rebalance_day]
rows=[]; exrows=[]
days=sorted(disc.date.unique())
for day in days:
    d=pd.Timestamp(day); D=C.prepare_day(d)
    if D is None: continue
    pool=D['alpha'].index; x=D['ln_mcap'].astype(float).reindex(pool)
    z=((x-x.mean())/x.std(ddof=0)).fillna(0); m=(x-x.mean())**2; m=((m-m.mean())/m.std(ddof=0)).fillna(0)
    b=D['betas'].reindex(pool).fillna(1.0); wb=D['wb'].reindex(pool).fillna(0); wb=wb/wb.sum()
    zb,mb,bb=(wb*z).sum(),(wb*m).sum(),(wb*b).sum()
    bs=C.load_daily_basic_window(sorted(pool), d-pd.Timedelta(days=10), d); bs['trade_date']=pd.to_datetime(bs['trade_date'])
    px=bs.sort_values('trade_date').groupby('ts_code')['close'].last()
    for a in (600000,1000000):
        cost=pd.Series({i:C.lot_round_rule(i)*px.get(i,np.nan) for i in pool})
        mine=set(cost[cost>C.NAME_CAP[a]*a].index); theirs=set(ex[(ex.date==day)&(ex.aum==a)].instrument)
        exrows.append(dict(date=day,aum=a,mine=len(mine),theirs=len(theirs),miss=len(mine-theirs),extra=len(theirs-mine),nopx=int(cost.isna().sum())))
        for sv in ['equity_100','equity80_etf20_510300']:
            w=W[(a,sv)]; w=w[w.session==day].set_index('instrument').weight
            bal=float(w.get(C.BALLAST,0)); we=w.drop(C.BALLAST,errors='ignore')
            notpool=[i for i in we.index if i not in pool]
            wep=we.reindex(pool).fillna(0)
            ind=pd.Series(D['industry']); gi=wep.groupby(ind.reindex(pool).fillna('_UNK')).sum()/max(wep.sum(),1e-12)
            gb=wb.groupby(ind.reindex(pool).fillna('_UNK')).sum()
            # excluded name bought anew? held names whose lot cost > cap
            held_exp=[i for i in we.index if cost.get(i,0)>C.NAME_CAP[a]*a]
            rows.append(dict(date=day,aum=a,sleeve=sv,n=int((we>0).sum()),cash=1-float(w.sum()),maxw=float(we.max()) if len(we) else np.nan,
              size=float((wep*z).sum()+bal*zb-zb), mid=float((wep*m).sum()+bal*mb-mb), beta=float((wep*b).sum()+bal*bb-bb),
              ind_abs=float(gi.max()), ind_act_pool=float((gi.reindex(gi.index.union(gb.index)).fillna(0)-gb.reindex(gi.index.union(gb.index)).fillna(0)).abs().max()),
              n_notpool=len(notpool), held_expensive=len(held_exp), held_exp_names=','.join(held_exp)))
    print(day, flush=True)
pd.DataFrame(rows).to_csv('/workspace/arch_v13_audit/recheck_expo.csv',index=False)
pd.DataFrame(exrows).to_csv('/workspace/arch_v13_audit/recheck_excl.csv',index=False)
print('DONE')
