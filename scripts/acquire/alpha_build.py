"""Build research-grade Alpha tables from tushare_raw. promotion_approved=false."""
import pandas as pd, glob, json, pathlib
R=pathlib.Path("data/v2/tushare_raw"); V=pathlib.Path("data/v2")
def load(p):
    f=sorted(glob.glob(str(R/p))); return pd.concat([pd.read_parquet(x) for x in f if pathlib.Path(x).stat().st_size],ignore_index=True) if f else pd.DataFrame()
out={}
# index members
w=load("index_weight/*.parquet")
if len(w):
    o=V/"index_members"; o.mkdir(exist_ok=True)
    w=w.drop_duplicates(["index_code","con_code","trade_date"]); w.to_parquet(o/"index_weight_csi300_500_1000.parquet",index=False)
    ev=[]
    for ix,g in w.groupby("index_code"):
        ds=sorted(g.trade_date.astype(str).unique()); prev=None
        for d in ds:
            cur=set(g[g.trade_date==d].con_code)
            if prev is not None:
                for c in cur-prev[1]: ev.append((ix,c,"in",prev[0],d))
                for c in prev[1]-cur: ev.append((ix,c,"out",prev[0],d))
            prev=(d,cur)
    e=pd.DataFrame(ev,columns=["index_code","con_code","event","prev_snapshot","snapshot_date"])
    e["effective_date_bound"]="(prev_snapshot, snapshot_date]"; e["ann_date"]=None
    e.to_parquet(o/"index_member_events.parquet",index=False)
    snaps=w.groupby("index_code").agg(n_snap=("trade_date","nunique"),start=("trade_date","min"),end=("trade_date","max"),avg_n=("con_code","size"))
    out["index"]={"snapshots":snaps.astype(str).to_dict("index"),"events":e.groupby(["index_code","event"]).size().astype(int).to_dict().__repr__(),"event_months":e.snapshot_date.str[:6].value_counts().sort_index().to_dict()}
# share_float
s=load("share_float/*.parquet")
if len(s):
    o=V/"share_float"; o.mkdir(exist_ok=True)
    s=s.drop_duplicates(); s.to_parquet(o/"share_float_2018plus.parquet",index=False)
    out["share_float"]={"rows":len(s),"codes":s.ts_code.nunique(),"ann":[s.ann_date.min(),s.ann_date.max()],"float":[s.float_date.min(),s.float_date.max()],
      "nonnull":{c:round(s[c].notna().mean()*100,2) for c in ["ann_date","float_date","float_share","float_ratio","share_type"]},
      "by_ann_year":s.ann_date.astype(str).str[:4].value_counts().sort_index().to_dict()}
# namechange / ST
n=load("namechange/*.parquet")
if len(n):
    o=V/"st_events"; o.mkdir(exist_ok=True)
    n=n.drop_duplicates(); n.to_parquet(o/"namechange_all.parquet",index=False)
    st=n[n.name.str.contains("ST",na=False)|n.change_reason.astype(str).str.contains("ST|撤销|摘帽|戴帽|退市风险",na=False)].copy()
    st.to_parquet(o/"st_events_from_namechange.parquet",index=False)
    out["namechange"]={"rows":len(n),"codes":n.ts_code.nunique(),"ann":[str(n.ann_date.min()),str(n.ann_date.max())],"start":[str(n.start_date.min()),str(n.start_date.max())],
      "st_rows":len(st),"reasons":st.change_reason.value_counts().head(12).to_dict(),"ann_nonnull":round(n.ann_date.notna().mean()*100,2),"st_2018plus":int((st.start_date.astype(str)>="20180101").sum())}
# top list
for api in ["top_list","top_inst"]:
    t=load(f"{api}/*.parquet")
    if len(t):
        o=V/"dragon_tiger"; o.mkdir(exist_ok=True); t.to_parquet(o/f"{api}.parquet",index=False)
        out[api]={"rows":len(t),"days":t.trade_date.nunique(),"range":[t.trade_date.min(),t.trade_date.max()],"files":len(glob.glob(str(R/api/'*')))}
json.dump(out,open("output/d1/alpha_build_summary.json","w"),ensure_ascii=False,indent=1,default=str)
print(json.dumps(out,ensure_ascii=False,default=str)[:6000])
