#!/usr/bin/env python3
"""etf_daily_adj 增量 (研究级, promotion_approved=false). 幂等: 只追加 > 现有最后日 的交易日.
口径同 scripts_etf_build2.py: ETF 宇宙=etf/etf_basic.parquet; fund_daily ⟕ fund_adj; *_hfq=raw*adj_factor;
available_at=trade_date 15:00 (Asia/Shanghai, naive); 列名/dtype/__index_level_0__ 保持不变.
原始切片落 data/v2/etf/raw/{fund_daily,fund_adj}/YYYYMMDD.parquet (每日 2 请求).
最后把 tables.etf_daily_adj 写入 output/daily_update_status.json 并重算 status.
用法: python3 scripts/acquire/etf_daily_adj_incr.py [--date YYYYMMDD] [--no-status]
"""
import sys, os, json, argparse, hashlib, pathlib, datetime as dt, time
from zoneinfo import ZoneInfo
ROOT=pathlib.Path("/workspace/QuantLab"); sys.path.insert(0,str(ROOT)); sys.path.insert(0,str(ROOT/"scripts/acquire"))
import pandas as pd
E=ROOT/"data/v2/etf"; P=E/"etf_daily_adj.parquet"; RAW=ROOT/"data/v2/tushare_raw"; ET=ZoneInfo("America/New_York")
STATUS=ROOT/"output/daily_update_status.json"
def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()
def wait_mem():
    while True:
        m=[int(l.split()[1]) for l in open("/proc/meminfo") if l.startswith("MemAvailable")][0]/1e6
        if m>=2: return
        print(f"MemAvailable {m:.2f}GB<2GB wait 60s",flush=True); time.sleep(60)
def pull(api,**p):
    from tushare_relay_pull import pull as _p
    return _p(api,preferred="relay",**p)
def raw(api,d):
    f=E/f"raw/{api}/{d}.parquet"
    if f.exists() and f.stat().st_size>0: return pd.read_parquet(f)
    x=pull(api,trade_date=d)
    if x is None or len(x)==0: raise RuntimeError(f"{api} {d} empty")
    t=pathlib.Path(str(f)+".tmp"); x.to_parquet(t,index=False); os.replace(t,f); return x
def run(end):
    wait_mem()
    cur=pd.read_parquet(P); last=cur.trade_date.max()
    todo=[p.stem for p in sorted((RAW/"daily").glob("2*.parquet")) if last<p.stem<=end]
    if todo:
        etf=pd.read_parquet(E/"etf_basic.parquet"); codes=set(etf.ts_code)
        fd=pd.concat([raw("fund_daily",d) for d in todo]); fa=pd.concat([raw("fund_adj",d) for d in todo])
        fd=fd[fd.ts_code.isin(codes)].copy(); fa=fa[fa.ts_code.isin(codes)].copy()
        fd["trade_date"]=fd.trade_date.astype(str); fa["trade_date"]=fa.trade_date.astype(str)
        m=fd.merge(fa.drop_duplicates(["ts_code","trade_date"]),on=["ts_code","trade_date"],how="left")
        for c in ["open","high","low","close","pre_close"]: m[c+"_hfq"]=m[c]*m.adj_factor
        m["available_at"]=pd.to_datetime(m.trade_date)+pd.Timedelta(hours=15); m["available_at_tz"]="Asia/Shanghai"
        m=m.merge(etf[["ts_code","name","category"]],on="ts_code",how="left").sort_values(["trade_date","ts_code"])
        m=m[cur.columns].astype(cur.dtypes.to_dict())
        m.index=range(int(cur.index.max())+1,int(cur.index.max())+1+len(m))
        out=pd.concat([cur,m]); out=out[~out.duplicated(["ts_code","trade_date"],keep="first")]
        t=pathlib.Path(str(P)+".tmp"); out.to_parquet(t); os.replace(t,P); cur=out
        print("appended",len(m),"rows for",todo,flush=True)
    mx=cur.trade_date.max()
    return dict(path=str(P),last_date=f"{mx[:4]}-{mx[4:6]}-{mx[6:]}",rows=len(cur),n_etfs_last_day=int((cur.trade_date==mx).sum()),
                sha256=sha(P),finished_at=dt.datetime.now(ET).isoformat(timespec="seconds"),
                columns_used_by_eng=["close_hfq","adj_factor"],promotion_approved=False)
def write_status(r,end):
    st=json.loads(STATUS.read_text()) if STATUS.exists() else {"schema":"quantlab.v2.daily_update_status.v1","tables":{},"errors":{}}
    st["tables"]["etf_daily_adj"]=r; st.setdefault("errors",{}).pop("etf_daily_adj",None)
    exp=st.get("target_trade_date") or f"{end[:4]}-{end[4:6]}-{end[6:]}"
    ok=all(str(t.get("last_date",""))[:10]>=exp for k,t in st["tables"].items() if k!="dividend") and not st["errors"]
    st.update(status="ok" if ok else "partial",finished_at=dt.datetime.now(ET).isoformat(timespec="seconds"),promotion_approved=False,live=False)
    t=STATUS.with_suffix(".tmp"); t.write_text(json.dumps(st,ensure_ascii=False,indent=2)); os.replace(t,STATUS); print("STATUS",st["status"])
if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--date",default=sorted(p.stem for p in (RAW/"daily").glob("2*.parquet"))[-1]); ap.add_argument("--no-status",action="store_true")
    a=ap.parse_args(); r=run(a.date); print(json.dumps(r,ensure_ascii=False))
    if not a.no_status: write_status(r,a.date)
