import pandas as pd, pyarrow.dataset as ds, json, re, time, sys
O="data/v2/"; P=lambda *a: print(time.strftime("%H:%M:%S"),*a,flush=True)
exec(open("scripts_cb_etf_build.py").read().split("def tag")[0].split("# ---------- ETF ----------")[1].replace("fb=pd","fb0=pd") if False else "")
src=open("scripts_cb_etf_build.py").read()
BROAD_IND=src[src.index('BROAD='):src.index('etf["category"]')]
fb=pd.read_parquet(O+"etf/raw/fund_basic_E.parquet").drop_duplicates("ts_code")
etf=fb[fb.name.str.contains("ETF",na=False)&~fb.name.str.contains("联接|LOF",na=False)].copy()
exec(BROAD_IND)
etf["category"]=etf.name.map(tag); etf["category_rule"]="name_regex_v1"
etf.to_parquet(O+"etf/etf_basic.parquet"); P("basic",len(etf))
codes=list(etf.ts_code)
def load(api):
    t=ds.dataset(O+f"etf/raw/{api}",format="parquet").to_table(filter=ds.field("ts_code").isin(codes)).to_pandas()
    P(api,len(t)); return t
fd=load("fund_daily"); fa=load("fund_adj")
fd["trade_date"]=fd.trade_date.astype(str); fa["trade_date"]=fa.trade_date.astype(str)
m=fd.merge(fa.drop_duplicates(["ts_code","trade_date"]),on=["ts_code","trade_date"],how="left")
for c in ["open","high","low","close","pre_close"]: m[c+"_hfq"]=m[c]*m.adj_factor
m["available_at"]=pd.to_datetime(m.trade_date)+pd.Timedelta(hours=15); m["available_at_tz"]="Asia/Shanghai"
m=m.merge(etf[["ts_code","name","category"]],on="ts_code",how="left")
m.sort_values(["trade_date","ts_code"]).to_parquet(O+"etf/etf_daily_adj.parquet"); P("written")
r={"etf_universe":len(etf),"delisted":int(etf.delist_date.notna().sum()),"category_counts":etf.category.value_counts().to_dict(),
 "rows":len(m),"etfs_with_daily":int(m.ts_code.nunique()),"date_min":m.trade_date.min(),"date_max":m.trade_date.max(),
 "adj_missing":round(float(m.adj_factor.isna().mean()),5),"close_missing":round(float(m.close.isna().mean()),5),
 "n_days":int(m.trade_date.nunique())}
for c in ["511880.SH","511010.SH","511260.SH","518880.SH","159934.SZ","510300.SH"]:
    x=m[m.ts_code==c]; r[c]=[x.trade_date.min(),x.trade_date.max(),len(x),round(float(x.adj_factor.isna().mean()),4)]
old=pd.read_parquet(O+"etf_510300/fund_daily_tushare_510300.parquet"); old["trade_date"]=old.trade_date.astype(str)
x=old.merge(m[m.ts_code=="510300.SH"],on="trade_date",suffixes=("_o",""));r["check_510300"]=[len(x),float((x.close-x.close_o).abs().max())]
json.dump(r,open(O+"etf/etf_coverage.json","w"),ensure_ascii=False,indent=1,default=str); print(json.dumps(r,ensure_ascii=False,default=str))
