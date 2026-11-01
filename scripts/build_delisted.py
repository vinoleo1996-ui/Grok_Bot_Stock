import pandas as pd,glob,json,os
D=pd.read_parquet('data/v2/tushare_raw/stock_basic/D.parquet')
D['instrument_id']=D.ts_code.map(lambda s:s.split('.')[1].lower()+'.'+s.split('.')[0])
def load(api):
    fs=[f for f in glob.glob(f'data/v2/delisted/raw_{api}/*.parquet') if os.path.getsize(f)>2000]
    x=pd.concat([pd.read_parquet(f) for f in fs],ignore_index=True)
    x['trade_date']=pd.to_datetime(x.trade_date.astype(str)); return x.drop_duplicates(['ts_code','trade_date'])
d=load('daily'); b=load('daily_basic')
d['amount']=d.amount*1000; d['volume']=d.vol*100
b['total_mv']=b.total_mv*1e4; b['circ_mv']=b.circ_mv*1e4
p=d.drop(columns=['vol']).merge(b[['ts_code','trade_date','total_mv','circ_mv','turnover_rate','pe_ttm','pb','total_share','float_share']],on=['ts_code','trade_date'],how='left')
p['instrument_id']=p.ts_code.map(lambda s:s.split('.')[1].lower()+'.'+s.split('.')[0])
p['units']='amount=元;volume=股;total_mv/circ_mv=元';p['source']='tushare.daily+daily_basic(datahub/pcd)'
p.to_parquet('data/v2/delisted/delisted_daily_tushare.parquet',index=False)
nc=pd.concat([pd.read_parquet(f) for f in glob.glob('data/v2/tushare_raw/namechange/*.parquet')]).drop_duplicates()
last=p.groupby('ts_code').trade_date.max().rename('last_trade_date')
def reason(r):
    h=nc[nc.ts_code==r.ts_code].sort_values('start_date'); rs=set(h.change_reason.dropna()); nm=' '.join(h.name.astype(str))
    tail=h.tail(3)
    if '退市整理期' in rs or '退' in str(tail.name.tolist()): base='强制退市(进入退市整理期)'
    elif any(x in rs for x in ('*ST','ST','从ST变为*ST')) and tail.change_reason.isin(['*ST','ST','从ST变为*ST','撤消*ST并实行ST']).any(): base='强制退市(退市前处于ST/*ST)'
    elif 'PT' in rs: base='PT时代退市'
    else: base='疑似主动/吸收合并/私有化退市(退市前非ST)'
    return pd.Series(dict(delist_reason_category=base,last_names='|'.join(tail.name.astype(str)),st_history='|'.join(sorted(rs))))
m=D.merge(last,left_on='ts_code',right_index=True,how='left')
m=pd.concat([m,m.apply(reason,axis=1)],axis=1)
m['delist_date']=pd.to_datetime(m.delist_date); m['list_date']=pd.to_datetime(m.list_date)
m['gap_days_last_trade_to_delist']=(m.delist_date-m.last_trade_date).dt.days
m['reason_basis']='heuristic: tushare namechange ST/退市整理期 history；无官方退市原因字段'
m.to_parquet('data/v2/delisted/delisted_master_tushare.parquet',index=False)
acc=dict(delisted_n=len(D),with_daily=int(p.ts_code.nunique()),with_mv=int(p.dropna(subset=['total_mv']).ts_code.nunique()),
 daily_rows=len(p),mv_nonnull=float(p.total_mv.notna().mean()),last_trade_nonnull=int(m.last_trade_date.notna().sum()),
 delist_2018plus=int((m.delist_date>='2018-01-01').sum()),delist_2018plus_with_mv=int(m[(m.delist_date>='2018-01-01')].ts_code.isin(p.dropna(subset=['total_mv']).ts_code).sum()),
 reason_counts=m.delist_reason_category.value_counts().to_dict(),gap_days_median=float(m.gap_days_last_trade_to_delist.median()))
json.dump(acc,open('data/v2/delisted/acceptance.json','w'),indent=1,ensure_ascii=False); print(json.dumps(acc,ensure_ascii=False,indent=1))
