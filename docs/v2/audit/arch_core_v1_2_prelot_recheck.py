import sys,pickle,glob,json,hashlib
sys.path.insert(0,'.')
import numpy as np,pandas as pd
import optimizer_lambda_calib_sealed as C, optimizer_core_x2_run as R
R.BETA_POOL=True
bench=pd.read_csv('../output/strategy_optimizer/core_x2/bench_hiliq_wb_x2.csv')
print(bench.columns.tolist(), bench.shape, bench.head(2).to_dict('records'))
rows=[]
for f in sorted(glob.glob('../output/strategy_optimizer/core_x2/_ckpt_v1_2/*.pkl')):
    r=pickle.load(open(f,'rb')); d=pd.Timestamp(r['day'])
    if d<pd.Timestamp('2025-06-01'): continue
    D=C.prepare_day(d)
    if D is None: continue
    for a in (600000,1000000):
        w=r['w'].get(a); lg=r['log'].get(a,{})
        if w is None: continue
        x=R.exposure_drift(w,D)
        # also post-lot
        sl=r['sleeves'].get(a,{})
        post={k:v.get('beta_drift') for k,v in sl.items()}
        postm={k:v.get('midcap_drift') for k,v in sl.items()}
        rows.append(dict(date=r['day'],aum=a,status=lg.get('status'),stage=lg.get('stage'),slack=lg.get('slack'),n=int((w>0).sum()),pre_beta=round(x['beta_drift'],3),pre_mid=round(x['midcap_drift'],3),pre_size=round(x['size_drift'],3),post_beta=post,post_mid=postm,wb_sum=float(D['wb'].sum()),beta_nan=int(D['betas'].reindex(D['alpha'].index).isna().sum()),pool=len(D['alpha'])))
    rows[-1]['_wbD']=D['wb']
    # bench compare
    bd=bench[pd.to_datetime(bench.iloc[:,0])==d] if bench.shape[1]>2 else None
    if bd is not None and len(bd):
        s=bd.set_index(bench.columns[1])[bench.columns[2]]
        u=s.index.union(D['wb'].index)
        rows[-1]['bench_maxdiff']=float((s.reindex(u).fillna(0)-D['wb'].reindex(u).fillna(0)).abs().max())
for r in rows: r.pop('_wbD',None); print(json.dumps(r,default=str))
