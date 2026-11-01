import pandas as pd, glob, pathlib, shutil, sys
sys.argv=["x","noop"]
src=pathlib.Path("scripts/acquire/tushare_relay_pull.py").read_text().split("\ndef all_codes")[0]; g={"__file__":"scripts/acquire/tushare_relay_pull.py"}; exec(src,g)
g["cached"]("adj_factor","20260630",preferred="datahub",trade_date="20260630")
af=pd.concat([pd.read_parquet(f) for f in glob.glob("data/v2/tushare_raw/adj_factor/*.parquet")])
af["iid"]=af.ts_code.str[-2:].str.lower()+"."+af.ts_code.str[:6]; af["trade_date"]=pd.to_datetime(af.trade_date.astype(str))
base=af[af.trade_date=="2026-06-30"].set_index("iid").adj_factor
A={k:v.set_index("trade_date").adj_factor for k,v in af.groupby("iid")}
bk=pathlib.Path("data/v2/asof_extend_tushare_202610/panels_backup_prefactor"); bk.mkdir(exist_ok=True)
n=miss=0; chain=0
for f in glob.glob("data/v2/asof_extend_tushare_202610/panels/*.parquet"):
    iid=pathlib.Path(f).stem; p=pd.read_parquet(f)
    if not (bk/pathlib.Path(f).name).exists(): shutil.copy2(f,bk)
    s=A.get(iid)
    p["adj_factor_tushare"]=p.trade_date.map(s) if s is not None else float("nan")
    d0=pathlib.Path(f"data/local_market/1c85fd9aceaa03c3c4863bec/panels/{iid}.parquet")
    p["factor"]=float("nan"); p["factor_basis"]="tushare_adj_factor_only"
    if d0.exists() and iid in base.index:
        q=pd.read_parquet(d0,columns=["factor"]); last=q.factor.dropna()
        if len(last):
            p["factor"]=last.iloc[-1]*p.adj_factor_tushare/base[iid]; p["factor_basis"]="d0_factor_20260630_x_tushare_adj_ratio"; chain+=1
    miss+=p.adj_factor_tushare.isna().sum(); n+=len(p)
    p.to_parquet(f,index=False)
print("rows",n,"adj_factor_missing",miss,"chained_panels",chain)
