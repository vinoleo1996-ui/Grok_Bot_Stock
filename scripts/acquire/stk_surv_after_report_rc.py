"""stk_surv(机构调研) 2018→LAST. 等队列 Q3_report_rc 完成(读 output/remaining_queue_status.json)后再跑, 一次一个.
stk_surv 只有 surv_date(调研日), 无披露日. 用东财 RPT_ORG_SURVEYNEW 抽样(RECEIVE_START_DATE vs NOTICE_DATE)
估计交易日滞后分布, available_at = 调研日后第 max(2, ceil(p95)) 个交易日 09:00. 幂等: DONE 标记."""
import sys,json,time,math,random,pathlib,datetime,bisect
ROOT=pathlib.Path("/workspace/QuantLab"); sys.path.insert(0,str(ROOT)); sys.path.insert(0,str(ROOT/"scripts/acquire"))
import queue_chain_20261014 as q, pandas as pd, requests
P=ROOT/"data/v2/events/stk_surv_2018plus.parquet"; DONE=ROOT/"output/markers/stk_surv_2018plus.DONE"
def wait_rc():
    while True:
        for l in open(q.ST):
            try: r=json.loads(l)
            except Exception: continue
            if r.get("item") in ("Q3_report_rc","report_rc") and r.get("ts","")>"2026-10-14": return r["status"]
        time.sleep(120)
def lag_sample(pages=25,seed=7):
    cal=q.tdays("20171201","20261231"); out=[]
    j=requests.get("https://datacenter-web.eastmoney.com/api/data/v1/get",params=dict(reportName="RPT_ORG_SURVEYNEW",columns="SECURITY_CODE,RECEIVE_START_DATE,NOTICE_DATE",pageSize=500,pageNumber=1),timeout=60).json()
    npg=j["result"]["pages"]; random.seed(seed)
    for pg in sorted(random.sample(range(1,npg+1),min(pages,npg))):
        try: d=requests.get("https://datacenter-web.eastmoney.com/api/data/v1/get",params=dict(reportName="RPT_ORG_SURVEYNEW",columns="SECURITY_CODE,RECEIVE_START_DATE,NOTICE_DATE",pageSize=500,pageNumber=pg,sortColumns="NOTICE_DATE",sortTypes=-1),timeout=60).json()["result"]["data"]
        except Exception: continue
        for r in d:
            a,b=str(r["RECEIVE_START_DATE"])[:10].replace("-",""),str(r["NOTICE_DATE"])[:10].replace("-","")
            if a.isdigit() and b.isdigit() and a>="2018": out.append(bisect.bisect_left(cal,b)-bisect.bisect_left(cal,a))
        time.sleep(0.5)
    s=pd.Series(out); return s
if __name__=="__main__":
    if DONE.exists() and P.exists(): q.log("Q5_stk_surv","skip_complete"); sys.exit(0)
    q.log("Q5_stk_surv","waiting_report_rc"); st=wait_rc(); q.log("Q5_stk_surv","start",report_rc_status=st)
    s=lag_sample(); qs={k:float(s.quantile(v)) for k,v in dict(p50=.5,p90=.9,p95=.95,p99=.99).items()}
    L=max(2,math.ceil(qs["p95"]))
    days=q.tdays("20180102",q.LAST); od=q.RAW/"stk_surv"
    fails=q.per_day("Q5","stk_surv",days,od,{"relay":q.relay},lambda d:dict(trade_date=d),1000)
    fs=sorted((od/"relay").glob("*.parquet")); x=pd.concat([pd.read_parquet(f) for f in fs if f.stat().st_size>0],ignore_index=True).drop_duplicates()
    cal=q.tdays("20171201","20271231")
    x["available_at"]=pd.to_datetime(x.surv_date.astype(str).map(lambda d: cal[min(len(cal)-1,bisect.bisect_left(cal,d)+L)]+" 09:00"))
    x["promotion_approved"]=False; x.to_parquet(P,index=False)
    m=q.man(P,rows=len(x),date_range=[x.surv_date.min(),x.surv_date.max()],source="tushare relay stk_surv (仅 surv_date, 无披露日)",
        available_at=f"surv_date 后第 {L} 个交易日 09:00 (max(2,ceil(p95 实际披露滞后)))",lag_sample=dict(n=len(s),share_le2=float((s<=2).mean()),**qs),n_fails=len(fails),fails=fails[:50])
    if len(fails)<50: DONE.parent.mkdir(parents=True,exist_ok=True); DONE.write_text(m["sha256"])
    q.log("Q5_stk_surv","done" if len(fails)<50 else "partial",rows=len(x),lag_days=L,lag_sample=m["lag_sample"],n_fails=len(fails),sha256=m["sha256"])
