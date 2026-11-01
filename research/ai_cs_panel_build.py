#!/usr/bin/env python3
"""AI cross-sectional panel cache (read-only inputs): daily ret(close/pre_close), open-ret, logmv, PIT SW L1, HILIQ/FULLA flags.
FULLA flag rebuilt from HI_LIQ mask columns (~st & ~suspended & ~young & adv20>=3e6) so sealed window is covered.
Writes output/ai_factory/panel_cache/cs_panel_{year}.parquet. live=false. Chunked by year (RSS<1.5GB)."""
import sys, resource, numpy as np, pandas as pd, pyarrow.parquet as pq
from pathlib import Path
R = Path(__file__).resolve().parents[1]; OUT = R/"output/ai_factory/panel_cache"
def ts(x): m,c=x.split('.',1); return f"{c}.{m.upper()}"
sw = pd.read_parquet(R/"data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet",columns=["instrument_id","sw_name","in_date","out_date"])
sw["inst"]=sw.instrument_id.map(ts); sw["in_date"]=pd.to_datetime(sw.in_date); sw["out_date"]=pd.to_datetime(sw.out_date).fillna(pd.Timestamp("2100-01-01"))
INDS=sorted(sw.sw_name.unique()); IND_ID={n:i for i,n in enumerate(INDS)}
pd.Series(INDS).to_csv(OUT/"ind_names.csv",index=False)
mf=pq.ParquetFile(R/"data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet")
for y in range(int(sys.argv[1]), int(sys.argv[2])+1):
    m=pd.read_parquet(R/"output/strategy_hiliq/universe_mask_hiliq_v1.parquet",filters=[("date",">=",pd.Timestamp(f"{y}-01-01")),("date","<=",pd.Timestamp(f"{y}-12-31"))])
    if not len(m): continue
    m["fulla"]=(~m.st.astype(bool))&(~m.suspended.astype(bool))&(~m.young.astype(bool))&(m.adv20_yuan>=3e6)
    m=m[m.fulla|m.in_universe.astype(bool)][["date","instrument","in_universe","fulla","adv20_yuan"]].rename(columns={"in_universe":"hiliq"})
    mc=pq.read_table(R/"data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet",columns=["instrument_id","trade_date","float_mktcap"],filters=[("trade_date",">=",pd.Timestamp(f"{y}-01-01")),("trade_date","<=",pd.Timestamp(f"{y}-12-31 23:59"))]).to_pandas()
    mc["instrument"]=mc.instrument_id.map(lambda x: ts(x) if x[:2] in("sh","sz","bj") else x); mc["date"]=pd.to_datetime(mc.trade_date).dt.normalize()
    m=m.merge(mc[["date","instrument","float_mktcap"]],on=["date","instrument"],how="left"); del mc
    rows=[]
    for d in sorted(m.date.unique()):
        p=R/f"data/v2/tushare_raw/daily/{pd.Timestamp(d):%Y%m%d}.parquet"
        if p.exists():
            x=pd.read_parquet(p,columns=["ts_code","open","close","pre_close"]); x["date"]=pd.Timestamp(d); rows.append(x)
    px=pd.concat(rows); px["ret"]=px.close/px.pre_close-1; px["ret_on"]=px.open/px.pre_close-1
    m=m.merge(px.rename(columns={"ts_code":"instrument"})[["date","instrument","ret","ret_on","close"]],on=["date","instrument"],how="left")
    s=sw[(sw.in_date<=pd.Timestamp(f"{y}-12-31"))&(sw.out_date>=pd.Timestamp(f"{y}-01-01"))]
    mm=m[["date","instrument"]].merge(s[["inst","sw_name","in_date","out_date"]],left_on="instrument",right_on="inst",how="left")
    mm=mm[(mm.date>=mm.in_date)&(mm.date<mm.out_date)].drop_duplicates(["date","instrument"],keep="last")
    m=m.merge(mm[["date","instrument","sw_name"]],on=["date","instrument"],how="left")
    m["ind"]=m.sw_name.map(IND_ID).fillna(-1).astype("int16"); m["logmv"]=np.log(m.float_mktcap.clip(lower=1)).astype("float32")
    m=m.drop(columns=["sw_name","float_mktcap"]); 
    for c in ["ret","ret_on","close","adv20_yuan"]: m[c]=m[c].astype("float32")
    m.to_parquet(OUT/f"cs_panel_{y}.parquet",index=False)
    print(y,len(m),m.hiliq.sum(),m.ind.eq(-1).mean().round(3),m.ret.isna().mean().round(3),f"rss={resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024:.0f}MB",flush=True)
    del m,px,rows
