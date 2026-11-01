import sys, json; sys.path.insert(0,'.')
import numpy as np, pandas as pd
import research.g1g5_capacity_adv_weights_hiliq as C
m=json.load(open('output/strategy_hiliq/legs/g1g5_capacity_adv_run_meta_20261014_195620.json'))
reb=m['rebalance_sessions']; uni=[i for i in C._fulla_universe()['instruments'] if i not in C.HARD_EXCLUDE]
sw=C._load_sw_members(); d1=C._preload_d1_adv(uni, reb)
w=pd.read_parquet('output/strategy_hiliq/legs/g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet',columns=['date','instrument','target_weight'])
w['date']=w.date.astype(str).str[:10]; rows=[]
for s in reb:
    present=sorted(i for i in C._fulla_members_on(s)&set(uni) if i not in C.HARD_EXCLUDE)
    snap=C._d1_adv_snapshot(d1,present,s); sc,meta=C.score_adv_liquidity(s,present,snap=snap,sw=sw)
    ranked=sorted(((i,sc[i]) for i in present if i in snap), key=lambda x:(-x[1],x[0]))
    pos=[(i,v) for i,v in ranked if v>0]; ru=pos if len(pos)>=12 else ranked
    tgt,cm=C.select_capacity_adv(ru,snap=snap,sw=sw,session=s,active_n=25,ind_cap=C.IND_CAP,budget=C.STOCK_BUDGET)
    vals=np.array([v for _,v in ru]); dup=int(len(vals)-len(np.unique(np.round(vals,12))))
    zero_filled=int(sum(1 for i in present if i in snap and sc[i]==0.0))
    prod=set(w[(w.date==s)&(w.target_weight>0)&(w.instrument!='510300.SH')].instrument)
    rows.append(dict(session=s,n_present=len(present),n_snap=len(snap),n_scored=meta.get('n_scored'),status=meta['status'],n_pos=len(pos),
      used_pos=len(pos)>=12,dup_scores_in_ranked=dup,zero_filled_in_snap=zero_filled,n_skipped_indcount=sum(1 for x in cm.get('skipped_head',[]) if x['reason']=='ind_count_cap'),
      n_skipped=cm['n_skipped'],picked=len(tgt),match_prod=set(tgt)==prod))
df=pd.DataFrame(rows); df.to_csv('output/strategy_hiliq/topn_tie_audit/capadv_leg_score_tie_by_rebalance.csv',index=False); print(df.to_string())
