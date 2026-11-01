import pandas as pd, numpy as np
TR='output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet'
LF='output/ai_factory/g1g5_equity_incentive_daily_weights_20261014_023222.parquet'
t=pd.read_parquet(TR); s=pd.read_parquet(LF)
# verify trunk file == targets the trunk run consumed
for c in (600000,1000000):
    g=pd.read_parquet(f'output/v3/book_smoke_g1g5_capacity_adv_x2/aum_{c}/X2/BOOK/target_weights.parquet')
    g['session']=g.session.astype(str).str[:10]; tt=t.assign(session=t.session.astype(str).str[:10])
    m=g.merge(tt.groupby(['session','instrument_id']).weight.sum().reset_index(),on=['session','instrument_id'],how='outer',suffixes=('_run','_file')).fillna(0)
    m=m[m.session.isin(g.session.unique())]
    print('trunk verify',c,'sessions',g.session.nunique(),'max|diff|',float((m.weight_run-m.weight_file).abs().max()))
imap=pd.concat([t,s])[['instrument_id','instrument']].drop_duplicates('instrument_id').set_index('instrument_id').instrument
def blend(parts,tag,path,cols=t.columns,uni=t.universe_id.iloc[0]):
    common=sorted(set.intersection(*[set(d.session) for d,_ in parts]))
    w=None
    for d,a in parts:
        x=d[d.session.isin(common)].groupby(['session','instrument_id']).weight.sum()*a
        w=x if w is None else w.add(x,fill_value=0)
    w=w.reset_index(); w=w[w.weight>0]
    w['weight']=w.weight/w.groupby('session').weight.transform('sum')
    w['date']=w.session; w['instrument']=w.instrument_id.map(imap); w['target_weight']=w.weight
    w['mechanism_tag']=tag; w['who_pays_zh']='诊断组合 '+tag; w['universe_id']=uni
    w=w[list(cols)]; w.to_parquet(path,index=False)
    st=w[w.instrument_id!='sh.510300'].groupby('session').weight.max()
    b=w[w.instrument_id=='sh.510300'].groupby('session').weight.sum().reindex(common).fillna(0)
    print(tag,w.shape,'sessions',len(common),'sum',w.groupby('session').weight.sum().agg(['min','max']).round(6).tolist(),
          'max_name',round(st.max(),4),'days>6%',int((st>0.0605).sum()),'ballast',round(b.mean(),3),'nan_instr',int(w.instrument.isna().sum()))
print('leaf ballast',round(s[s.instrument_id=='sh.510300'].groupby('session').weight.sum().mean(),3))
for a,n in [(0.7,'70_30'),(0.8,'80_20')]:
    blend([(t,a),(s,1-a)],f'g1g5_combo_capadv_eqincent_{n}',f'output/ai_factory/g1g5_combo_capadv_eqincent_{n}_daily_weights.parquet')
for tier in ('60w','100w'):
    b=pd.read_parquet(f'output/small_aum_concentration/v2/B_B1_equal_topN_{tier}.parquet')
    imap=pd.concat([imap,b.drop_duplicates('instrument_id').set_index('instrument_id').instrument]); imap=imap[~imap.index.duplicated()]
    blend([(b,0.75),(s,0.25)],f'conc4leg_B1eq_eqincent_{tier}',f'output/ai_factory/g1g5_conc4leg_B1eq_eqincent_{tier}_daily_weights.parquet')
