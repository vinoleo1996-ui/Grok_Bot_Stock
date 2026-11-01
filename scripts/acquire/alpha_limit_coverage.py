import pandas as pd, glob, json, sys
F=["limit_up","limit_down","open_status","tradestatus","amount"]
rows=[]
for f in glob.glob("data/local_market/1c85fd9aceaa03c3c4863bec/panels/*.parquet"):
    d=pd.read_parquet(f,columns=F+["available_at"])
    d["date"]=pd.to_datetime(d.available_at.astype(str).str[:10]); d=d[d.date>="2018-01-01"]
    if d.empty: continue
    d["open_status"]=d.open_status.where(~d.open_status.isin(["unknown",""]))
    g=d.assign(y=d.date.dt.year).groupby("y")
    r=g[F].count(); r["rows"]=g.size(); r["code"]=f.split("/")[-1][:-8]; rows.append(r.reset_index())
a=pd.concat(rows); a.to_parquet("output/d1/limit_cov_1c85_by_code_year.parquet")
t=a.groupby("y")[F+["rows"]].sum(); 
for c in F: t[c+"_pct"]=(t[c]/t.rows*100).round(2)
print(t.to_string()); print(a.date.max() if "date" in a else "")
