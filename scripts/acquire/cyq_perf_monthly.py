"""cyq_perf 日度筹码 (tushare relay), 按月分批. 原始按日 data/v2/tushare_raw/cyq_perf/YYYYMMDD.parquet, 物化按月 data/v2/cyq/cyq_perf_YYYYMM.parquet.
用法: python3 scripts/acquire/cyq_perf_monthly.py 202601 202610   (起止月, 含). MemAvailable<2GB 暂停.
available_at = trade_date 18:00 Asia/Shanghai (Tushare 盘后约 17-18 点更新)."""
import sys, os, json, time, pathlib, signal, pandas as pd
class CallTimeout(BaseException): pass   # BaseException: 不被 _get 内部 except Exception 吞掉
def _alarm(*a): raise CallTimeout('relay call >120s')
signal.signal(signal.SIGALRM, _alarm)
os.environ.setdefault("TSPRO_RELAY_TIMEOUT","45")
ROOT=pathlib.Path("/workspace/QuantLab"); sys.path.insert(0,str(ROOT))
from quantlab.data_sources.tushare_proxy import relay,_to_df
RAW=ROOT/"data/v2/tushare_raw/cyq_perf"; OUT=ROOT/"data/v2/cyq"; RAW.mkdir(parents=True,exist_ok=True); OUT.mkdir(parents=True,exist_ok=True)
def mem_ok():
    for l in open("/proc/meminfo"):
        if l.startswith("MemAvailable"): return int(l.split()[1])>2_000_000
def days(m):
    c=pd.read_parquet(ROOT/"data/v2/tushare_raw/trade_cal.parquet"); c=c[c.is_open.astype(int)==1]
    today=pd.Timestamp.now(tz="Asia/Shanghai").strftime("%Y%m%d")
    return sorted(d for d in c.cal_date.astype(str) if d.startswith(m) and d<today or (d.startswith(m) and d==today and pd.Timestamp.now(tz="Asia/Shanghai").hour>=19))
def pull(d):
    out,off=[],0
    while True:
        for a in range(6):
            try:
                signal.alarm(120); s,r=relay("cyq_perf",trade_date=d,limit=5000,offset=off)
            except (Exception, CallTimeout) as e:
                s,r=-1,str(e)
            finally: signal.alarm(0)
            if s==200 and isinstance(r,dict) and not (r.get("meta") or {}).get("source_unavailable"): break
            if s==403: raise RuntimeError(f"forbidden {r}")
            print(f"  retry {d} off={off} a={a} {s} {str(r)[:100]}",flush=True); time.sleep(min(60,6*2**a))
        else: raise RuntimeError(f"exhausted {d} {s} {str(r)[:150]}")
        df=_to_df(r); out.append(df)
        if len(df)<5000: break
        off+=5000
    return pd.concat(out,ignore_index=True)
def months(a,b):
    return [p.strftime("%Y%m") for p in pd.period_range(pd.Period(a[:4]+"-"+a[4:],"M"),pd.Period(b[:4]+"-"+b[4:],"M"),freq="M")]
def main(a,b):
    summ={}
    for m in sorted(months(a,b),reverse=True):
        n=0; fails=[]
        for d in days(m):
            f=RAW/f"{d}.parquet"
            if f.exists() and f.stat().st_size>10000: continue
            while not mem_ok(): print("mem<2GB pause",flush=True); time.sleep(60)
            try:
                x=pull(d)
                if len(x): x.to_parquet(f,index=False); n+=1; print(d,len(x),flush=True)
                else: fails.append(d+":empty")
            except Exception as e: fails.append(d+":"+str(e)[:80]); print("FAIL",d,e,flush=True)
            time.sleep(0.3)
        fs=sorted(RAW.glob(f"{m}*.parquet"))
        if fs:
            t=pd.concat([pd.read_parquet(x) for x in fs],ignore_index=True)
            for c in t.columns:
                if c not in("ts_code","trade_date"): t[c]=pd.to_numeric(t[c],errors="coerce")
            t["available_at"]=pd.to_datetime(t.trade_date.astype(str))+pd.Timedelta(hours=18); t["promotion_approved"]=False
            t.to_parquet(OUT/f"cyq_perf_{m}.parquet",index=False)
            summ[m]=dict(rows=len(t),days=int(t.trade_date.nunique()),codes=int(t.ts_code.nunique()),range=[str(t.trade_date.min()),str(t.trade_date.max())],new_days=n,fails=fails)
        print(m,summ.get(m),flush=True)
    mf=OUT/"manifest.json"; man=json.load(open(mf)) if mf.exists() else {"months":{}}
    man["months"].update(summ)
    allm=man["months"]; man.update(table="cyq/cyq_perf_YYYYMM.parquet",rows=sum(v["rows"] for v in allm.values()),
        date_range=[min(v["range"][0] for v in allm.values()),max(v["range"][1] for v in allm.values())],
        source="tushare relay cyq_perf",available_at="trade_date 18:00 Asia/Shanghai",promotion_approved=False,built=pd.Timestamp.now().isoformat())
    json.dump(man,open(mf,"w"),ensure_ascii=False,indent=2); print("TOTAL",man["rows"],man["date_range"])
if __name__=="__main__": main(sys.argv[1],sys.argv[2])
