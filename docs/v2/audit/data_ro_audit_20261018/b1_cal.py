import pyarrow.parquet as pq, pandas as pd
R='/workspace/QuantLab/'
c=pq.read_table(R+'data/v2/calendar/trade_cal_sse_pit.parquet').to_pandas()
r=pq.read_table(R+'data/v2/tushare_raw/trade_cal.parquet').to_pandas()
print('pit rows',len(c),'min',c.cal_date.min(),'max',c.cal_date.max(),'open',int(c.is_open.sum()))
print('pretrade null/None/empty:',c[c.pretrade_date.isna()|c.pretrade_date.isin(['None','','nan'])][['cal_date','is_open','pretrade_date']].to_string())
print(c[(c.cal_date>='20130419')&(c.cal_date<='20130429')].to_string())
print('raw exchanges',r.exchange.value_counts().to_dict(),'max',r.cal_date.max())
print(r[(r.cal_date>='20130419')&(r.cal_date<='20130429')].to_string())
rs=r[r.exchange=='SSE'][['cal_date','is_open','pretrade_date']]
m=c.merge(rs,on='cal_date',how='outer',suffixes=('','_raw'),indicator=True)
print(m._merge.value_counts().to_dict()); d=m[(m._merge=='both')&((m.is_open!=m.is_open_raw)|(m.pretrade_date.astype(str)!=m.pretrade_date_raw.astype(str)))]
print('diffs',len(d)); print(d.head(10).to_string())
# derivation check: pretrade should be previous open day
o=c[c.is_open==1].cal_date.tolist(); exp={}
import bisect
bad=[(x,p) for x,p in zip(c.cal_date,c.pretrade_date) if (lambda i:o[i-1] if i>0 else None)(bisect.bisect_left(o,x))!=p]
print('rows where pretrade != prior open day:',len(bad),bad[:10])
print([l.strip() for l in open('/proc/self/status') if l.startswith('VmHWM')])
