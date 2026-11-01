"""D6: 配股事件表 (东财 RPT_IPO_ALLOTMENT). available_at = FIRST_NOTICE_DATE(配股说明书/发行公告) 20:00 Asia/Shanghai."""
import json, time, requests, pandas as pd, pathlib
ROOT=pathlib.Path("/workspace/QuantLab"); OUT=ROOT/"data/v2/corporate_actions"
U="https://datacenter-web.eastmoney.com/api/data/v1/get"
rows=[];p=1
while True:
    j=requests.get(U,params=dict(reportName="RPT_IPO_ALLOTMENT",columns="ALL",pageSize=500,pageNumber=p,sortColumns="EQUITY_RECORD_DATE",sortTypes=-1),timeout=30).json()
    rows+=j["result"]["data"]
    if p>=j["result"]["pages"]: break
    p+=1; time.sleep(0.5)
d=pd.DataFrame(rows)
for c in [x for x in d if x.endswith("_DATE")]: d[c]=pd.to_datetime(d[c],errors="coerce")
d=d.rename(columns=str.lower).rename(columns={"secucode":"ts_code"})
d["instrument_id"]=d.ts_code.str.split(".").str[1].str.lower()+"."+d.ts_code.str.split(".").str[0]
d["ratio_per_10"]=d.placing_ratio
d["available_at"]=d.first_notice_date.fillna(d.equity_record_date-pd.Timedelta(days=2))+pd.Timedelta(hours=20)
d["available_at_rule"]=d.first_notice_date.notna().map({True:"first_notice_date 20:00",False:"equity_record_date-2d 20:00 (fallback)"})
d["source"]="eastmoney.RPT_IPO_ALLOTMENT"; d["promotion_approved"]=False
d=d.drop_duplicates(["ts_code","equity_record_date"]).sort_values("ex_dividend_date").reset_index(drop=True)
d.to_parquet(OUT/"rights_issue_em.parquet",index=False)
# cross with unexplained ex-rights subset
hit=None
f=OUT/"exrights_unexplained_recheck_tushare.parquet"
if f.exists():
    R=pd.read_parquet(f); R["session"]=pd.to_datetime(R.session)
    k=d[["instrument_id","ex_dividend_date"]].dropna().assign(m=1)
    x=R.merge(k,left_on=["instrument_id","session"],right_on=["instrument_id","ex_dividend_date"],how="left")
    hit=dict(unexplained_total=len(R),hit_rights_issue=int(x.m.notna().sum()),
             by_status=x.assign(h=x.m.notna()).groupby("status").h.agg(["size","sum"]).astype(int).to_dict("index"))
man=dict(table="corporate_actions/rights_issue_em.parquet",rows=len(d),date_range_ex=[str(d.ex_dividend_date.min().date()),str(d.ex_dividend_date.max().date())],
 source="eastmoney datacenter RPT_IPO_ALLOTMENT (Tushare 无配股接口)",available_at="first_notice_date 20:00 Asia/Shanghai; 缺失时 股权登记日-2天",
 cross_exrights_unexplained=hit,promotion_approved=False,built=pd.Timestamp.now().isoformat())
json.dump(man,open(OUT/"manifest_d6_rights_issue.json","w"),ensure_ascii=False,indent=2,default=str); print(json.dumps(man,ensure_ascii=False,default=str))
