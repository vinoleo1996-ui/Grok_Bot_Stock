# usage: python3 scripts_factor_jump_count.py <tag>   counts non-ex-date factor jumps >0.1% on merged D0+extend
import sys,glob,json,os,pandas as pd,numpy as np
tag=sys.argv[1]; D0="data/local_market/1c85fd9aceaa03c3c4863bec/panels/"; EXT="data/v2/asof_extend_tushare_202610/panels/"
CUT=pd.Timestamp("2026-06-30")
dv=pd.read_parquet("data/v2/corporate_actions/dividend_tushare.parquet",columns=["ts_code","ex_date"]).dropna()
fd=pd.read_parquet("data/v2/etf/raw/fund_div.parquet",columns=["ts_code","ex_date"]).dropna()
ex=pd.concat([dv,fd]); ex["iid"]=ex.ts_code.str[-2:].str.lower()+"."+ex.ts_code.str[:6]
exs=ex.groupby("iid").ex_date.apply(lambda s:set(pd.to_datetime(s.astype(str)))).to_dict()
def et(f): 
    if "event_time" in f: return pd.to_datetime(f.event_time).dt.tz_localize(None) if getattr(pd.to_datetime(f.event_time).dt,"tz",None) else pd.to_datetime(f.event_time)
    return pd.to_datetime(f.index).tz_localize(None) if getattr(f.index,"tz",None) else pd.to_datetime(f.index)
rows=[]
for p in sorted(glob.glob(D0+"*.parquet")):
    iid=os.path.basename(p)[:-8]
    f=pd.read_parquet(p,columns=["factor"]+(["event_time"] if "event_time" in __import__("pyarrow.parquet").parquet.read_schema(p).names else [])); s=pd.Series(f.factor.astype(float).values,index=et(f)); s=s[s.index<=CUT]
    e=EXT+iid+".parquet"
    if not os.path.exists(e) and os.path.exists(f"data/v2/etf_510300/panels/{iid}.parquet"): e=f"data/v2/etf_510300/panels/{iid}.parquet"
    import pyarrow.parquet as pq
    if os.path.exists(e) and "factor" in pq.read_schema(e).names:
        g=pd.read_parquet(e,columns=["factor"]+(["event_time"] if "event_time" in pq.read_schema(e).names else [])); s2=pd.Series(g.factor.astype(float).values,index=et(g)); s=pd.concat([s,s2[s2.index>CUT]])
    s=s[~s.index.duplicated(keep="last")].sort_index().dropna()
    r=s.pct_change().abs(); j=r[r>1e-3]
    j=j[~j.index.isin(exs.get(iid,set()))]
    for d,v in j.items(): rows.append((iid,d,v))
o=pd.DataFrame(rows,columns=["iid","date","abs_chg"]); o.to_parquet(f"output/d1/factor_jumps_{tag}.parquet")
w=o[(o.date>="2024-06-03")&(o.date<="2026-10-09")]
res={"tag":tag,"all_n":len(o),"all_lt_0.5pct":int((o.abs_chg<5e-3).sum()),"all_instruments":int(o.iid.nunique()),
 "window_2024-06-03_2026-10-09_n":len(w),"window_lt_0.5pct":int((w.abs_chg<5e-3).sum()),
 "sh.510300_window":int((w.iid=="sh.510300").sum()),"sz.000620_window":int((w.iid=="sz.000620").sum()),
 "top10_all":o.iid.value_counts().head(10).to_dict()}
json.dump(res,open(f"output/d1/factor_jumps_{tag}.json","w"),ensure_ascii=False,indent=1,default=str); print(res)
