import pyarrow.parquet as pq, pandas as pd, glob, hashlib, datetime, os
R='/workspace/QuantLab/'; O='/tmp/data_ro_audit_20261018/'
def rss(): return [l.strip() for l in open('/proc/self/status') if l.startswith(('VmRSS','VmHWM'))]
def sha(f): return hashlib.sha256(open(f,'rb').read()).hexdigest()
reads=[]
def rd(f,cols=None):
    reads.append((datetime.datetime.now().isoformat(timespec='seconds'),f,sha(f))); return pq.read_table(f,columns=cols).to_pandas()
P=R+'data/v2/sw_pit/'
cur=rd(P+'industry_members_sw_l1_pit.parquet'); bak=rd(P+'industry_members_sw_l1_pit.bak_pre_fix_20261014.parquet')
raw=rd(P+'sw2021_members_l1l2l3_raw.parquet')
print('cur',cur.shape,cur.instrument_id.nunique(),'bak',bak.shape,bak.instrument_id.nunique(),list(bak.columns)[-3:],'raw',raw.shape,raw.ts_code.nunique())
# per-L1 raw pulls
pulls=[]
for f in sorted(glob.glob(R+'data/v2/tushare_raw/index_member_all/*.parquet')):
    d=rd(f); d['pullfile']=os.path.basename(f); pulls.append(d)
pl=pd.concat(pulls,ignore_index=True); print('perL1 pulls rows',len(pl),'codes',pl.ts_code.nunique(), list(pl.columns))
# (a) multiple open
op=cur[cur.out_date.isna()]; g=op.groupby('ts_code').size(); multi=g[g>1].index
A=op[op.ts_code.isin(multi)].sort_values(['ts_code','in_date'])[['ts_code','name','l1_code','l1_name','in_date','out_date','is_new']]
print('(a) n codes multi-open:',len(multi)); print(A.to_string())
# source check for (a): raw rows for these codes
for src,df in [('raw_union',raw),('perL1_pulls',pl)]:
    s=df[df.ts_code.isin(multi)]; so=s[s.out_date.isna()|(s.out_date.astype(str).isin(['None','','NaT','nan']))]
    print(src,'open rows per code:',so.groupby('ts_code').l1_code.nunique().to_dict())
pl[pl.ts_code.isin(multi)].sort_values(['ts_code','in_date']).to_csv(O+'A_12codes_raw_perL1_rows.csv',index=False)
A.to_csv(O+'A_12codes_open_records.csv',index=False)
# (b) universe
cal=rd(R+'data/v2/calendar/trade_cal_sse_pit.parquet',['cal_date','is_open'])
days=pd.to_datetime(cal[cal.is_open==1].cal_date)
sb=pd.concat([rd(f,['ts_code','list_date','delist_date']) for f in sorted(glob.glob(R+'data/v2/tushare_raw/stock_basic/*.parquet'))]).drop_duplicates('ts_code')
dl=rd(R+'data/v2/ref/stock_delisted_v2.parquet',['ts_code','delist_date'])
sb=sb.merge(dl.rename(columns={'delist_date':'dd2'}),on='ts_code',how='left'); sb['dd']=sb.delist_date.where(sb.delist_date.notna()&(sb.delist_date!=''),sb.dd2)
sb=sb[sb.ts_code.str.match(r'^\d{6}\.(SH|SZ)$')]  # A-share; BJ excluded
D0=pd.Timestamp('2026-09-24')
res={}
for D in [D0, days[days<=pd.Timestamp('2026-10-16')].max()]:
    L=sb[(pd.to_datetime(sb.list_date)<=D)&((sb.dd.isna())|(pd.to_datetime(sb.dd,errors='coerce')>D))]
    act=cur[(cur.in_date<=D)&((cur.out_date.isna())|(cur.out_date>D))].ts_code.unique()
    res[D]=sorted(set(L.ts_code)-set(act)); print('missing at',D.date(),len(res[D]),'listed',len(L))
# code-day count over a window: last-month trading days up to 2026-10-16
win=days[(days>=pd.Timestamp('2026-09-24'))&(days<=pd.Timestamp('2026-10-16'))]
rows=[]
for D in win:
    L=sb[(pd.to_datetime(sb.list_date)<=D)&((sb.dd.isna())|(pd.to_datetime(sb.dd,errors='coerce')>D))]
    act=set(cur[(cur.in_date<=D)&((cur.out_date.isna())|(cur.out_date>D))].ts_code)
    rows+= [(c,D) for c in L.ts_code if c not in act]
B=pd.DataFrame(rows,columns=['ts_code','date']); print('code-days missing 09-24..10-16:',len(B),'codes',B.ts_code.nunique(),'days',len(win))
B.to_csv(O+'B_missing_codedays_win.csv',index=False)
# per code: in raw/bak/pulls?
mc=B.ts_code.unique(); info=pd.DataFrame({'ts_code':mc})
info['in_cur_any']=info.ts_code.isin(cur.ts_code); info['in_bak']=info.ts_code.isin(bak.ts_code); info['in_raw_union']=info.ts_code.isin(raw.ts_code); info['in_perL1']=info.ts_code.isin(pl.ts_code)
info=info.merge(sb[['ts_code','list_date','dd']],on='ts_code',how='left')
info['ndays']=info.ts_code.map(B.groupby('ts_code').size())
info.to_csv(O+'B_missing_codes_classified.csv',index=False)
print(info.drop(columns='ts_code').groupby(['in_cur_any','in_bak','in_raw_union','in_perL1']).size())
print('list_date>=2026-06 among missing:',(info.list_date>='20260601').sum())
dropped=set(bak.ts_code)-set(cur.ts_code); print('codes in bak but not cur:',len(dropped))
pd.DataFrame(reads,columns=['read_et','file','sha256']).to_csv(O+'A_reads.csv',index=False)
print(rss())
