"""Arch v1.3 resign: daily_basic_full_tushare.parquet was rebuilt at 00:21:29 ET during the v1.3 run (started 00:20:04).
Compare current file vs backup taken at 00:20 on rows trade_date<=2026-10-09 (run window end), cols used by the run. Read-only."""
import pyarrow.parquet as pq, pyarrow as pa, pyarrow.compute as pc, pandas as pd, numpy as np, json, resource, sys
A='/workspace/QuantLab/data/v2/valuation/daily_basic_full_tushare.parquet'
B='/workspace/QuantLab/backups/valuation/daily_basic_full_tushare.20261018_0020.parquet'
cols=['ts_code','trade_date','close','turnover_rate','float_mktcap','available_at']
res={}
for y in range(2017,2027):
    s0=pd.Timestamp(f'{y}-01-01'); s1=min(pd.Timestamp(f'{y}-12-31'),pd.Timestamp('2026-10-09'))
    f=[('trade_date','>=',s0),('trade_date','<=',s1)]
    a=pq.read_table(A,columns=cols,filters=f).to_pandas(); b=pq.read_table(B,columns=cols,filters=f).to_pandas()
    for x in (a,b):
        x['ts_code']=x['ts_code'].astype(str); x.sort_values(['ts_code','trade_date'],inplace=True); x.reset_index(drop=True,inplace=True)
    same_shape=a.shape==b.shape
    eq = same_shape and all(a[c].equals(b[c]) or ((a[c].isna()&b[c].isna())|(a[c]==b[c])).all() for c in cols)
    res[y]={'rows_cur':len(a),'rows_bak':len(b),'identical':bool(eq)}
    print(y,res[y],round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024),'MB',flush=True)
    del a,b
out={'cur':A,'bak':B,'window_end':'2026-10-09','cols':cols,'by_year':res,'all_identical':all(v['identical'] for v in res.values()),
     'peak_rss_mb':round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)}
json.dump(out,open('/workspace/QuantLab/docs/v2/audit/arch_core_v1_3_resign_datadiff.json','w'),indent=1)
print('DATADIFF_DONE',out['all_identical'])
