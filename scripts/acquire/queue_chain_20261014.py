"""串行队列: 等 cyq PID 结束 → G3 hsgt 回补 → ETF 份额增量 → block_trade 双源 → report_rc(datahub) → 股权激励(东财) → G0 SHA256.
一次一个重拉数; MemAvailable<2GB 暂停; promotion_approved=false. 进度追加 output/remaining_queue_status.json"""
import os,sys,json,time,hashlib,pathlib,subprocess,datetime,traceback
import pandas as pd, requests
ROOT=pathlib.Path("/workspace/QuantLab"); sys.path.insert(0,str(ROOT)); os.chdir(ROOT)
from quantlab.data_sources.tushare_proxy import relay,datahub,_to_df
ST=ROOT/"output/remaining_queue_status.json"; RAW=ROOT/"data/v2/tushare_raw"
def log(item,status,**k):
    r=dict(item=item,status=status,ts=datetime.datetime.now().isoformat(),**k); print(json.dumps(r,ensure_ascii=False),flush=True)
    open(ST,"a").write(json.dumps(r,ensure_ascii=False,default=str)+"\n")
def mem_wait():
    while True:
        for l in open("/proc/meminfo"):
            if l.startswith("MemAvailable"): v=int(l.split()[1])
        if v>2_000_000: return
        print("mem<2GB pause",flush=True); time.sleep(60)
def sha(p): h=hashlib.sha256(); [h.update(b) for b in iter(lambda f=open(p,"rb"):f.read(1<<20),b"")]; return h.hexdigest()
def tdays(a,b):
    c=pd.read_parquet(RAW/"trade_cal.parquet"); c=c[c.is_open.astype(int)==1]; return sorted(d for d in c.cal_date.astype(str) if a<=d<=b)
def nxt_open(d):
    c=pd.read_parquet(RAW/"trade_cal.parquet"); c=sorted(c[c.is_open.astype(int)==1].cal_date.astype(str)); return next(x for x in c if x>d)
LAST="20261013"
def call(fn,api,tries=5,**kw):
    for a in range(tries):
        try:
            s,r=fn(api,**kw)
            if s==200 and isinstance(r,dict) and r.get("code") in (0,None) and "data" in r and not (r.get("meta") or {}).get("sample"): return _to_df(r)
            err=f"{s} {str(r)[:120]}"
        except Exception as e: err=str(e)[:120]
        time.sleep(min(60,5*2**a))
    raise RuntimeError(f"{api} {kw} {err}")
def man(path,**k):
    p=pathlib.Path(path); m=dict(table=str(p.relative_to(ROOT)),sha256=sha(p),promotion_approved=False,built=datetime.datetime.now().isoformat(),**k)
    json.dump(m,open(p.with_name(p.stem+"_manifest.json"),"w"),ensure_ascii=False,indent=2,default=str); return m

def wait_cyq(pid=4094376):
    while os.path.exists(f"/proc/{pid}"): time.sleep(30)
    m=ROOT/"data/v2/cyq/manifest.json"; log("3b_cyq","finished",manifest_exists=m.exists())
def g3():
    env=dict(os.environ,TOP10_START="20220601",TOP10_END="20231231",CHUNK_DAYS="400")
    for i in range(4):
        mem_wait(); rc=subprocess.call([sys.executable,"scripts/acquire/fill_hsgt_top10_extend.py"],env=env,stdout=open("logs/g3_hsgt_backfill.log","a"),stderr=subprocess.STDOUT)
        if rc==0: break
    x=pd.read_parquet("data/v2/northbound/hsgt_top10_daily_2018plus.parquet")
    w=x[(x.trade_date.astype(str)>="20220601")&(x.trade_date.astype(str)<="20231231")]
    empt={}
    for d in ["20250815","20250818","20250819","20250820","20251029","20251226","20260701"]:
        try: empt[d]=len(call(relay,"hsgt_top10",trade_date=d))
        except Exception as e: empt[d]="err:"+str(e)[:60]
    log("G3","done" if w.trade_date.nunique()>300 else "partial",rc=rc,window_days=int(w.trade_date.nunique()),window_rows=len(w),recheck_empty_days=empt)
def etf():
    p=ROOT/"data/v2/etf/share_pit/etf_share_flow_pit_all.parquet"; x=pd.read_parquet(p); add=[]
    for d in tdays("20261010",LAST):
        if (x.trade_date==d).any(): continue
        s=call(relay,"fund_share",trade_date=d,limit=5000); n=call(relay,"fund_nav",nav_date=d,limit=5000)
        s=s[s.ts_code.isin(x.ts_code.unique())][["ts_code","trade_date","fd_share"]]
        n=n[["ts_code","unit_nav","adj_nav","ann_date"]].drop_duplicates("ts_code").rename(columns={"ann_date":"nav_ann_date"})
        t=s.merge(n,on="ts_code",how="left"); t["share_wan"]=t.fd_share
        t["share_available_at"]=pd.Timestamp(nxt_open(d)+" 09:00"); t["nav_available_at"]=pd.Timestamp(d+" 23:59")
        add.append(t); x=pd.concat([x,t],ignore_index=True)
    if add:
        x=x.sort_values(["ts_code","trade_date"]); x["d_share_wan"]=x.groupby("ts_code").share_wan.diff().fillna(0)
        x["flow_est_wan_yuan"]=x.d_share_wan*x.unit_nav; x["available_at"]=x[["share_available_at","nav_available_at"]].max(axis=1)
        pd.read_parquet(p).to_parquet(str(p)+".bak_pre_20261014"); x.to_parquet(p,index=False)
    m=man(p,rows=len(x),date_range=[x.trade_date.min(),x.trade_date.max()],source="tushare relay fund_share+fund_nav",available_at="share: 次交易日 09:00")
    log("Q1_etf_share","done",added=sum(len(a) for a in add),rows=len(x),max_date=x.trade_date.max(),sha256=m["sha256"])
def per_day(item,api,days,outdir,fns,kwf,lim):
    outdir=pathlib.Path(outdir); fails=[]
    for d in days:
        mem_wait()
        for nm,fn in fns.items():
            f=outdir/nm/f"{d}.parquet"
            if f.exists(): continue
            f.parent.mkdir(parents=True,exist_ok=True)
            try:
                parts,off=[],0
                while True:
                    t=call(fn,api,**kwf(d),limit=lim,offset=off); parts.append(t)
                    if len(t)<lim: break
                    off+=lim
                pd.concat(parts,ignore_index=True).to_parquet(f,index=False)
            except Exception as e: fails.append(f"{nm}:{d}:{str(e)[:60]}")
            time.sleep(0.3)
    return fails
def block():
    days=tdays("20180102",LAST); od=RAW/"block_trade_dual"
    fails=per_day("Q2","block_trade",days,od,{"relay":relay,"datahub":datahub},lambda d:dict(trade_date=d),1000)
    def load(s):
        fs=sorted((od/s).glob("*.parquet")); return pd.concat([pd.read_parquet(f).assign(src=s) for f in fs if f.stat().st_size>0],ignore_index=True)
    r,h=load("relay"),load("datahub"); k=["ts_code","trade_date","price","vol","amount","buyer","seller"]
    for t in (r,h):
        for c in ["price","vol","amount"]: t[c]=pd.to_numeric(t[c],errors="coerce").round(4)
    u=pd.concat([r,h]); u["n_src"]=u.groupby(k).src.transform("nunique"); u["sources"]=u.groupby(k).src.transform(lambda s:",".join(sorted(set(s))))
    u=u.drop_duplicates(k).drop(columns="src")
    cal=sorted(tdays("20180101","20261231")); nx={a:b for a,b in zip(cal,cal[1:])}
    u["available_at"]=pd.to_datetime(u.trade_date.map(nx)+" 09:00"); u["promotion_approved"]=False
    p=ROOT/"data/v2/events/block_trade_2018plus.parquet"; p.parent.mkdir(exist_ok=True,parents=True); u.to_parquet(p,index=False)
    dr=u.groupby("trade_date").agg(rows=("ts_code","size"),both=("n_src",lambda s:(s==2).sum())).reset_index()
    dr["only_one"]=dr.rows-dr.both; dr.to_parquet(ROOT/"data/v2/events/block_trade_dual_diff_by_day.parquet",index=False)
    m=man(p,rows=len(u),date_range=[u.trade_date.min(),u.trade_date.max()],source="tushare relay + datahub block_trade 并集",available_at="trade_date 次交易日 09:00",
          diff=dict(relay_rows=len(r),datahub_rows=len(h),both=int((u.n_src==2).sum()),only_relay=int((u.sources=="relay").sum()),only_datahub=int((u.sources=="datahub").sum())),fails=fails[:50],n_fails=len(fails))
    log("Q2_block_trade","done" if len(fails)<50 else "partial",rows=len(u),diff=m["diff"],n_fails=len(fails),sha256=m["sha256"])
def report_rc():
    c=pd.read_parquet(RAW/"trade_cal.parquet"); days=sorted(d for d in c.cal_date.astype(str) if "20180101"<=d<=LAST)  # 自然日(研报周末也发)
    od=RAW/"report_rc_dh"; fails=per_day("Q3","report_rc",days,od,{"dh":datahub},lambda d:dict(report_date=d),1000)
    fs=sorted((od/"dh").glob("*.parquet")); x=pd.concat([pd.read_parquet(f) for f in fs],ignore_index=True).drop_duplicates()
    cal=sorted(tdays("20180101","20261231"))
    import bisect; x["available_at"]=pd.to_datetime(x.report_date.astype(str).map(lambda d: cal[bisect.bisect_right(cal,d)]+" 09:00"))
    x["promotion_approved"]=False; p=ROOT/"data/v2/events/report_rc_2018plus.parquet"; x.to_parquet(p,index=False)
    m=man(p,rows=len(x),date_range=[x.report_date.min(),x.report_date.max()],source="datahub report_rc (relay 无权限)",available_at="report_date 后首个交易日 09:00",n_fails=len(fails),fails=fails[:50])
    log("Q3_report_rc","done" if len(fails)<50 else "partial",rows=len(x),n_fails=len(fails),sha256=m["sha256"])
def incentive():
    rows=[];pg=1
    while True:
        for a in range(5):
            try:
                j=requests.get("https://datacenter-web.eastmoney.com/api/data/v1/get",params=dict(reportName="RPT_EQUITY_INCENTIVE",columns="ALL",pageNumber=pg,pageSize=500,sortColumns="LASTEST_NOTICE_DATE",sortTypes=-1),timeout=30).json(); break
            except Exception: time.sleep(5*2**a)
        d=(j.get("result") or {}).get("data") or []; rows+=d
        if pg>=(j.get("result") or {}).get("pages",0) or not d: break
        pg+=1; time.sleep(0.3)
    x=pd.DataFrame(rows); n0=len(x); x=x[~x.SECUCODE.astype(str).str.endswith(".NQ")].drop_duplicates()
    x["available_at"]=pd.to_datetime(x.LASTEST_NOTICE_DATE)+pd.Timedelta(hours=20); x["promotion_approved"]=False
    x["pit_note"]="仅最新公告日(非首次公告日), 研究级; 回测需与公告表匹配草案日"
    p=ROOT/"data/v2/events/equity_incentive_em.parquet"; x.to_parquet(p,index=False)
    m=man(p,rows=len(x),raw_rows=n0,dropped_neeq=n0-len(x),date_range=[str(x.LASTEST_NOTICE_DATE.min()),str(x.LASTEST_NOTICE_DATE.max())],source="eastmoney RPT_EQUITY_INCENTIVE",available_at="LASTEST_NOTICE_DATE 20:00 (近似, 非首次)")
    log("Q4_equity_incentive","done",rows=len(x),dropped_neeq=n0-len(x),sha256=m["sha256"])
def g0():
    out={}
    for mf in ["data/v2/index_members/manifest_d5.json","data/v2/corporate_actions/manifest_d6_rights_issue.json","data/v2/northbound/hsgt_top10_manifest.json","data/v2/sw_pit/manifest.json","data/v2/cyq/manifest.json"]:
        p=ROOT/mf
        if not p.exists(): continue
        m=json.load(open(p)); files={"manifest_d5.json":["index_members/csi_review_calendar.parquet","index_members/index_member_events.parquet"],"manifest_d6_rights_issue.json":["corporate_actions/rights_issue_em.parquet"],
          "hsgt_top10_manifest.json":["northbound/hsgt_top10_daily_2018plus.parquet"],"manifest.json":None}[p.name]
        if files is None: files=[str(f.relative_to(ROOT/"data/v2")) for f in sorted(p.parent.glob("*.parquet")) if "bak" not in f.name]
        m["sha256"]={f:sha(ROOT/"data/v2"/f) for f in files}; m["sha256_at"]=datetime.datetime.now().isoformat()
        json.dump(m,open(p,"w"),ensure_ascii=False,indent=2,default=str); out[mf]=len(files)
    log("G0","done",manifests=out)
def nightly():
    for a in (["--steps","bundle"],["--steps","hsgt,sw","--date","20261013"],["--steps","bundle"]):
        mem_wait(); rc=subprocess.call([sys.executable,"scripts/nightly_update.py",*a],stdout=open("logs/nightly/verify_20261014.log","a"),stderr=subprocess.STDOUT)
        log("5_nightly "+" ".join(a),"ok" if rc==0 else f"rc={rc}")
STEPS=dict(cyq=wait_cyq,g3=g3,g0=g0,nightly=nightly,etf=etf,block=block,report_rc=report_rc,incentive=incentive,g0b=g0)
if __name__=="__main__":
    for k in (sys.argv[1].split(",") if len(sys.argv)>1 else STEPS):
        try: STEPS[k]()
        except Exception as e: log(k,"blocked",reason=str(e)[:300],tb=traceback.format_exc()[-600:])
