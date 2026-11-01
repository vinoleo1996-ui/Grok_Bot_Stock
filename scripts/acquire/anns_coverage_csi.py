"""公告覆盖率（沪深300+中证500，2020-01→2024-05）。
月度成分：data/v2/index_members/index_weight_csi300_500_1000.parquet 中当月及之前最近一次快照（PIT 近似）。
月度覆盖：当月成分股中当月至少 1 条公告（announcements_classified_pit，全部来源）的占比。
股票级覆盖：窗口内曾为成分股的股票中，巨潮 by_stock 已拉完（文件存在）的占比。
输出 output/d1/anns_coverage_csi.json"""
import pandas as pd, pathlib, json, datetime, argparse
ap=argparse.ArgumentParser(); ap.add_argument("--index",default="000300.SH,000905.SH",help="逗号分隔，如 000300.SH 只算沪深300"); ARGS=ap.parse_args()
R=pathlib.Path(__file__).resolve().parents[2]; V=R/"data/v2"
START,END="2020-01","2024-05"; IDX=ARGS.index.split(",")
w=pd.read_parquet(V/"index_members/index_weight_csi300_500_1000.parquet",columns=["index_code","con_code","trade_date"])
w=w[w.index_code.isin(IDX)]; w["ym"]=w.trade_date.str[:6]
a=pd.read_parquet(V/"events/announcements_classified_pit.parquet",columns=["instrument","ann_date","source"])
a["ym"]=a.ann_date.str[:6]; a=a[(a.ym>=START.replace("-",""))&(a.ym<=END.replace("-",""))]
has=a.groupby("ym").instrument.apply(set).to_dict()
hasc=a[a.source=="cninfo_hisAnnouncement"].groupby("ym").instrument.apply(set).to_dict()
done={f"{p.stem.split('.')[1]}.{p.stem.split('.')[0].upper()}" for d in ("cninfo","eastmoney") for p in (V/f"announcements/{d}/by_stock").glob("*.parquet")}
snaps=sorted(w.trade_date.unique()); months=pd.period_range(START,END,freq="M").strftime("%Y%m")
rows=[]; ever={i:set() for i in IDX}
for ym in months:
    r={"month":ym}; allm=set()
    for i in IDX:
        sd=max([s for s in w[w.index_code==i].trade_date.unique() if s[:6]<=ym])
        m=set(w[(w.index_code==i)&(w.trade_date==sd)].con_code); ever[i]|=m; allm|=m
        r[f"{i}_n"]=len(m); r[f"{i}_cov"]=round(len(m&has.get(ym,set()))/len(m),4)
    r["union_n"]=len(allm); r["union_cov"]=round(len(allm&has.get(ym,set()))/len(allm),4)
    r["union_cov_cninfo_only"]=round(len(allm&hasc.get(ym,set()))/len(allm),4)
    rows.append(r)
U=set().union(*ever.values())
stock={"ever_members":len(U),"cninfo_done":len(U&done),"cninfo_done_share":round(len(U&done)/len(U),4),
  **{f"{i}_ever":len(ever[i]) for i in IDX},**{f"{i}_done_share":round(len(ever[i]&done)/len(ever[i]),4) for i in IDX}}
df=pd.DataFrame(rows)
out={"generated_at":datetime.datetime.now().isoformat(timespec="seconds"),"window":[START,END],"target":0.95,"indices":IDX,
 "monthly_union_cov_mean":round(df.union_cov.mean(),4),"monthly_union_cov_min":float(df.union_cov.min()),
 "months_ge_target":int((df.union_cov>=0.95).sum()),"months":len(df),"stock_level":stock,"monthly":rows,
 "missing_members_not_pulled":sorted(U-done)}
(R/"output/d1").mkdir(parents=True,exist_ok=True)
json.dump(out,open(R/("output/d1/anns_coverage_csi.json" if len(IDX)==2 and set(IDX)=={"000300.SH","000905.SH"} else f"output/d1/anns_coverage_csi_{'_'.join(i[:6] for i in IDX)}.json"),"w"),ensure_ascii=False,indent=1)
print(json.dumps({k:v for k,v in out.items() if k not in("monthly","missing_members_not_pulled")},ensure_ascii=False))
print(df[["month","union_n","union_cov","union_cov_cninfo_only"]].iloc[::6].to_string(index=False))
