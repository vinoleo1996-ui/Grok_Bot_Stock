import pyarrow.parquet as pq, pandas as pd, glob, os
R='/workspace/QuantLab/'
pl=pd.concat([pq.read_table(f).to_pandas().assign(pf=os.path.basename(f)) for f in glob.glob(R+'data/v2/tushare_raw/index_member_all/*.parquet')])
print(pl.out_date.map(type).value_counts().to_dict(), pl.out_date.head(3).tolist(), pl.in_date.head(3).tolist())
for c in ['002420.SZ','300741.SZ','688002.SH']: print(pl[pl.ts_code==c][['pf','l1_code','in_date','out_date','is_new']].to_string())
raw=pq.read_table(R+'data/v2/sw_pit/sw2021_members_l1l2l3_raw.parquet').to_pandas()
for c in ['002420.SZ','300741.SZ']: print(raw[raw.ts_code==c][['l1_code','l2_code','in_date','out_date','is_new']].to_string())
cur=pq.read_table(R+'data/v2/sw_pit/industry_members_sw_l1_pit.parquet').to_pandas()
print('cur max in_date',cur.in_date.max(),'raw max',raw.in_date.max(),'perL1 max',pl.in_date.max())
m=set(pl.ts_code)-set(cur.ts_code); x=pl[pl.ts_code.isin(m)]
print('perL1-only codes',len(m),'their max in_date',x.in_date.max(),'is_new',x.is_new.value_counts().to_dict(), 'by pf',x.pf.nunique())
print(sorted(os.path.getmtime(f) for f in glob.glob(R+'data/v2/tushare_raw/index_member_all/*'))[:1])
print([l.strip() for l in open('/proc/self/status') if l.startswith('VmHWM')])
