import pandas as pd,numpy as np,json
m=pd.read_parquet("data/v2/etf/etf_daily_adj.parquet",columns=["ts_code","name","category","trade_date","close","pre_close","adj_factor"]).sort_values(["ts_code","trade_date"])
m["prev_close"]=m.groupby("ts_code").close.shift(); m["fchg"]=m.adj_factor/m.groupby("ts_code").adj_factor.shift()-1
d=pd.read_parquet("data/v2/etf/raw/fund_div.parquet"); d=d[d.div_proc.astype(str).str.contains("实施")&d.ex_date.notna()].drop_duplicates(["ts_code","ex_date"])
d["trade_date"]=d.ex_date.astype(str)
x=m.merge(d[["ts_code","trade_date","div_cash"]],on=["ts_code","trade_date"],how="left")
# implied factor from dividend + previous close (raw close of T-1)
x["fchg_div"]=np.where(x.div_cash.notna(), x.prev_close/(x.prev_close-x.div_cash)-1, 0.0)
# split proxy: pre_close vs prev_close mismatch
x["px_ratio"]=x.prev_close/x.pre_close
x["split_like"]=(x.px_ratio-1).abs()>0.02
x["fchg_px"]=x.px_ratio-1   # exchange pre_close based factor (dividend+split)
ev=x[(x.fchg.abs()>1e-3)|x.div_cash.notna()].copy()
ev["diff_div"]=ev.fchg-ev.fchg_div; ev["diff_px"]=ev.fchg-ev.fchg_px
def cls(r):
    if pd.notna(r.div_cash):
        return "div_ok" if abs(r.diff_div)<2e-3 else ("div_mismatch_split" if r.split_like else "div_mismatch")
    if abs(r.diff_px)<2e-3: return "nodiv_but_matches_preclose(split/missing_div)"
    return "unexplained_jump"
ev["cls"]=ev.apply(cls,axis=1)
ev.to_parquet("data/v2/etf/etf_adj_crosscheck_events.parquet")
s={"events":len(ev),"by_cls":ev.cls.value_counts().to_dict()}
bad=ev[ev.cls.isin(["div_mismatch","unexplained_jump"])]
s["bad_etfs"]=int(bad.ts_code.nunique()); s["bad_top"]=bad.groupby(["ts_code","name"]).size().sort_values(ascending=False).head(30).reset_index().values.tolist()
w=ev[ev.ts_code=="510300.SH"]; s["510300"]=w[["trade_date","div_cash","fchg","fchg_div","cls"]].values.tolist()
s["unexplained_abs_median"]=float(bad.fchg.abs().median()) if len(bad) else None
json.dump(s,open("data/v2/etf/etf_adj_crosscheck.json","w"),ensure_ascii=False,indent=1,default=str); print(json.dumps(s,ensure_ascii=False,default=str)[:3000])
