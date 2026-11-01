"""汇总 arch_k6_industry_fullpool_rows.csv → 分组表（版本×资金档×口径）。只读。"""
import pandas as pd, numpy as np
A='/workspace/QuantLab/docs/v2/audit/'
r=pd.read_csv(A+'arch_k6_industry_fullpool_rows.csv')
E=1e-6; sl=r.ind_slack.fillna(0.0)
r['rel_br']=r.act_full_max>0.08+sl+E
r['abs_br']=r.abs_eq_max>0.20+E
r['any_br']=r.rel_br|r.abs_br
r['gt9']=r.act_full_max>0.09+E; r['gt10']=r.act_full_max>0.10+E
r['old_rel_br']=r.act_old_max>0.08+sl+E
r['old_any_br']=r.old_rel_br|r.abs_br
r['old2_rel_br']=r.act_old2_max>0.08+sl+E
r['feas']=r.status.isin(['OK','LOT_CASH_GT2'])
out=[]
for (v,a,s),g in r.groupby(['version','aum','sleeve']):
    i=g.act_full_max.idxmax(); io=g.act_old_max.idxmax(); ia=g.abs_eq_max.idxmax(); f=g[g.feas]
    out.append(dict(version=v,aum=('60万' if a==600000 else '100万'),sleeve=('①纯股票' if s=='equity_100' else '②80/20'),
      n_days=len(g), rel_breach=int(g.rel_br.sum()), abs_breach=int(g.abs_br.sum()), any_breach=int(g.any_br.sum()),
      any_breach_pct=round(100*g.any_br.mean(),1), any_breach_feasible=f"{int(f.any_br.sum())}/{len(f)}", any_breach_X2=int(g[g.window=='X2'].any_br.sum()),
      gt9=int(g.gt9.sum()), gt10=int(g.gt10.sum()),
      max_act=round(100*g.act_full_max[i],2), max_act_signed=round(100*g.act_full_signed[i],2), max_act_date=g.date[i], max_act_ind=g.act_full_ind[i], max_act_status=g.status[i],
      max_abs=round(100*g.abs_eq_max[ia],2), max_abs_date=g.date[ia], max_abs_ind=g.abs_eq_ind[ia],
      old_rel_breach=int(g.old_rel_br.sum()), old_any_breach=int(g.old_any_br.sum()), old_max_act=round(100*g.act_old_max[io],2), old_max_date=g.date[io], old_max_ind=g.act_old_ind[io],
      old2_rel_breach=int(g.old2_rel_br.sum()), old2_max_act=round(100*g.act_old2_max.max(),2), old2_max_date=g.date[g.act_old2_max.idxmax()], old2_max_ind=g.act_old2_ind[g.act_old2_max.idxmax()],
      old_act_median=round(100*g.act_old_max.median(),2), full_act_median=round(100*g.act_full_max.median(),2), full_neg_share=round(float((g.act_full_signed[g.rel_br]<0).mean()),2) if g.rel_br.any() else None))
S=pd.DataFrame(out); S.to_csv(A+'ARCH_K6_INDUSTRY_FULLPOOL_SUMMARY.csv',index=False)
pd.set_option('display.width',300); pd.set_option('display.max_columns',40)
print(S.to_string(index=False))
# top breach days per version (full-pool)
t=r[r.version!='v1_3_void'].sort_values('act_full_max',ascending=False).head(12)[['version','date','aum','sleeve','status','act_full_signed','act_full_ind','ind_slack']]
print(t.to_string(index=False))
print(r.groupby('version').apply(lambda g: g.act_full_ind[g.rel_br].value_counts().head(4).to_dict()))
print(r.groupby('version').apply(lambda g: (g.act_full_signed[g.rel_br]>0).mean()))
