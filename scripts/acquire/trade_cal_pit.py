#!/usr/bin/env python3
"""A 股交易日历 PIT 表 (SSE, Tushare trade_cal), 研究级 promotion_approved=false.
字段: cal_date(YYYYMMDD str), is_open(int), pretrade_date(str), available_at(Asia/Shanghai naive datetime)
available_at 口径: 交易所年度休市安排通常于上一年 12 月发布 -> 取 (cal_year-1)-12-31 09:00; 2005 年(数据起点)以及已经过去的日期同样按此口径.
覆盖 20050101-20261231. 幂等: 全量重拉后与旧表比较, 只有内容变化才重写. 写 manifest(sha256).
"""
import sys, json, hashlib, pathlib, os, datetime as dt
ROOT=pathlib.Path("/workspace/QuantLab"); sys.path.insert(0,str(ROOT/"scripts/acquire"))
import pandas as pd
from tushare_relay_pull import pull
D=ROOT/"data/v2/calendar"; P=D/"trade_cal_sse_pit.parquet"; M=D/"manifest.json"
def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()
def main(end="20261231"):
    x=pull("trade_cal",preferred="relay",exchange="SSE",start_date="20050101",end_date=end,fields="exchange,cal_date,is_open,pretrade_date")
    src=x.attrs.get("source")
    x=x[["cal_date","is_open","pretrade_date"]].astype({"cal_date":str,"is_open":int,"pretrade_date":str}).sort_values("cal_date").drop_duplicates("cal_date").reset_index(drop=True)
    x["available_at"]=pd.to_datetime((x.cal_date.str[:4].astype(int)-1).astype(str)+"-12-31 09:00:00")
    assert x.cal_date.min()<="20050104" and x.cal_date.max()==end, (x.cal_date.min(),x.cal_date.max())
    exp=pd.date_range("2005-01-01",f"{end[:4]}-{end[4:6]}-{end[6:]}").strftime("%Y%m%d")
    assert x.cal_date.tolist()==list(exp), "calendar gap"
    changed=True
    if P.exists():
        old=pd.read_parquet(P); changed=not old.reset_index(drop=True).equals(x)
    if changed:
        t=P.with_suffix(".tmp"); x.to_parquet(t,index=False); os.replace(t,P)
    man=dict(table=str(P.relative_to(ROOT)),exchange="SSE",source=f"tushare trade_cal ({src})",rows=len(x),
             start=x.cal_date.min(),end=x.cal_date.max(),open_days=int(x.is_open.sum()),sha256=sha(P),
             rewritten=changed,available_at_rule="(cal_year-1)-12-31 09:00 Asia/Shanghai",
             promotion_approved=False,finished_at=dt.datetime.now(dt.timezone.utc).isoformat())
    M.write_text(json.dumps(man,ensure_ascii=False,indent=2)); print(json.dumps(man,ensure_ascii=False))
if __name__=="__main__": main(*sys.argv[1:])
