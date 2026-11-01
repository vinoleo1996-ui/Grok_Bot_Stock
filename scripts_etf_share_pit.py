import pandas as pd,glob,os,sys
R="data/v2/etf/raw/"; O="data/v2/etf/share_pit/"
codes=sys.argv[1].split(",") if len(sys.argv)>1 else [os.path.basename(f)[:-8] for f in glob.glob(R+"fund_share/*.parquet")]
cal=sorted(pd.read_parquet(R+"fund_daily/510300.SH.parquet",columns=["trade_date"]).trade_date.astype(str).unique()) if os.path.exists(R+"fund_daily/510300.SH.parquet") else None
out=[]
for c in codes:
    fs=R+f"fund_share/{c}.parquet"; fn=R+f"fund_nav/{c}.parquet"
    if not os.path.exists(fs): continue
    s=pd.read_parquet(fs)[["ts_code","trade_date","fd_share"]].drop_duplicates("trade_date",keep="last")
    s["trade_date"]=s.trade_date.astype(str); s=s[s.trade_date>="20180101"].sort_values("trade_date")
    if os.path.exists(fn):
        n=pd.read_parquet(fn)[["nav_date","ann_date","unit_nav","adj_nav"]].dropna(subset=["unit_nav"])
        n["nav_date"]=n.nav_date.astype(str); n=n.sort_values("ann_date").drop_duplicates("nav_date",keep="first")
        s=s.merge(n.rename(columns={"nav_date":"trade_date","ann_date":"nav_ann_date"}),on="trade_date",how="left")
    else: s["unit_nav"]=None;s["nav_ann_date"]=None;s["adj_nav"]=None
    s["share_wan"]=s.fd_share; s["d_share_wan"]=s.fd_share.diff()
    s["flow_est_wan_yuan"]=s.d_share_wan*s.unit_nav  # 申赎估算=Δ份额×当日单位净值
    td=pd.to_datetime(s.trade_date)
    nxt=s.trade_date.shift(-1).fillna((td+pd.offsets.BDay(1)).dt.strftime("%Y%m%d"))
    s["share_available_at"]=pd.to_datetime(nxt)+pd.Timedelta(hours=9)   # 保守：T+1 交易日 09:00 (Asia/Shanghai)
    na=pd.to_datetime(s.nav_ann_date.astype(str),errors="coerce")
    s["nav_available_at"]=pd.concat([na,td],axis=1).max(axis=1)+pd.Timedelta(hours=23,minutes=59)
    s["available_at"]=s[["share_available_at","nav_available_at"]].max(axis=1)
    out.append(s)
df=pd.concat(out); tag=sys.argv[2] if len(sys.argv)>2 else "all"
df.to_parquet(O+f"etf_share_flow_pit_{tag}.parquet",index=False)
print(tag,df.ts_code.nunique(),len(df),df.trade_date.min(),df.trade_date.max(),"nav_missing",df.unit_nav.isna().mean().round(4))
