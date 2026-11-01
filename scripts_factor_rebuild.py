# Replace D0 panel 'factor' (<=2026-06-30) with Tushare adj_factor (stocks) / fund_adj (ETF),
# scaled so value at the last D0 session equals old D0 factor there (extend continuity kept).
import glob,os,shutil,json,pandas as pd,numpy as np,pyarrow.dataset as ds
D0="data/local_market/1c85fd9aceaa03c3c4863bec/panels/"; BAK="data/local_market/1c85fd9aceaa03c3c4863bec/panels_bak_factor_20261011/"
CUT=pd.Timestamp("2026-06-30")
os.makedirs(BAK,exist_ok=True)
for extra in ["data/v2/etf_510300/panels/sh.510300.parquet"]:
    b=extra.replace(".parquet",".bak_factor_20261011.parquet")
    if not os.path.exists(b): shutil.copy2(extra,b)
af=ds.dataset("data/v2/tushare_raw/adj_factor_hist",format="parquet").to_table(columns=["ts_code","trade_date","adj_factor"]).to_pandas()
af["ts_code"]=af.ts_code.astype("category"); AF={k:v for k,v in af.groupby("ts_code",observed=True)}; del af
FA=ds.dataset("data/v2/etf/raw/fund_adj",format="parquet").to_table(columns=["ts_code","trade_date","adj_factor"]).to_pandas(); FA={k:v for k,v in FA.groupby("ts_code")}
log=[]
def tsc(iid): return iid[3:]+"."+iid[:2].upper()
def rebuild(path,iid,series_src,keep_after_cut=False):
    f=pd.read_parquet(path)
    t=pd.to_datetime(f.event_time) if "event_time" in f else pd.to_datetime(f.index)
    t=t.dt.tz_localize(None) if hasattr(t,"dt") and getattr(t.dt,"tz",None) else t
    tt=pd.DatetimeIndex(t)
    a=series_src.reindex(tt).ffill()  # ffill over suspension days
    old=f.factor.astype(float).values
    mask=(tt<=CUT) if not keep_after_cut else np.ones(len(tt),bool)
    anchor_idx=np.where(mask & ~np.isnan(a.values))[0]
    if len(anchor_idx)==0: log.append((iid,"no_tushare")); return
    k=old[anchor_idx[-1]]/a.values[anchor_idx[-1]]
    new=old.copy(); m2=mask & ~np.isnan(a.values); new[m2]=a.values[m2]*k
    f["factor_d0_orig"]=old; f["factor"]=new.astype(f.factor.dtype)
    f["factor_basis"]=np.where(m2,"tushare_adj_factor_scaled_to_d0_anchor","d0_orig_no_tushare")
    f.to_parquet(path); log.append((iid,int(m2.sum()),int((~m2).sum())))
for p in sorted(glob.glob(D0+"*.parquet")):
    iid=os.path.basename(p)[:-8]
    if not os.path.exists(BAK+os.path.basename(p)): shutil.copy2(p,BAK+os.path.basename(p))
    if iid.startswith(("sh.5","sz.1")):
        fa=pd.read_parquet("data/v2/etf/raw/fund_adj_510300_2012.parquet") if iid=="sh.510300" else None
        x=FA.get(tsc(iid),pd.DataFrame(columns=["ts_code","trade_date","adj_factor"]))
        if fa is not None: x=pd.concat([fa,x])
    else:
        x=AF.get(tsc(iid),pd.DataFrame(columns=["ts_code","trade_date","adj_factor"]))
    if x.empty: log.append((iid,"no_tushare")); continue
    s=x.drop_duplicates("trade_date").assign(d=lambda z:pd.to_datetime(z.trade_date.astype(str))).set_index("d").adj_factor.astype(float).sort_index()
    rebuild(p,iid,s)
    if iid=="sh.510300":
        rebuild("data/v2/etf_510300/panels/sh.510300.parquet",iid,s,keep_after_cut=True)
json.dump(log,open("output/d1/factor_rebuild_log.json","w"),default=str); print("DONE",len(log))
