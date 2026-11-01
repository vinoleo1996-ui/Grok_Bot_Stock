import pandas as pd, json, numpy as np, sys
def diag(d, cap):
    t=pd.read_parquet(d+'/target_weights.parquet'); a=pd.read_parquet(d+'/actual_weights.parquet')
    nav=pd.read_csv(d+'/nav.csv'); nav['_et']=pd.to_datetime(nav['_et']); nv=nav.set_index('_et')['nav']
    ss=sorted(set(t.session)|set(a.session)); nxt={s:ss[i+1] for i,s in enumerate(ss[:-1])}
    t=t[(t.instrument_id!='sh.510300')&(t.weight>0)&t.session.isin(nxt)].copy()
    t['fs']=t.session.map(nxt)
    m=t.merge(a.rename(columns={'session':'fs','weight':'aw'}),on=['fs','instrument_id'],how='left').fillna({'aw':0})
    m['notional']=m.weight*m.session.map(nv).fillna(cap)
    m['under']=m.weight-m.aw
    top=m.groupby('instrument_id').under.mean().sort_values(ascending=False).head(3)
    return dict(med_notional=float(m.notional.median()), unbuy=float((m.aw<=1e-9).mean()),
      under_med=float(m.under.median()), under_max=float(m.under.max()),
      top=[f'{k} {v*100:.2f}pp' for k,v in top.items()])
if __name__=='__main__':
    print(json.dumps(diag(sys.argv[1],float(sys.argv[2])),ensure_ascii=False))
