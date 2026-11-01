#!/usr/bin/env python3
"""每日写 output/data_freshness_status.json 供 Eng 闸门 (只读, promotion_approved=false).
expected_date = 交易日历(SSE)中 <= 今天(Asia/Shanghai) 的最后开市日; 若今天开市且上海时间 < CUTOFF(默认 20:00) 则取前一开市日.
lag_trading_days = expected 与 last_date 之间的开市日数; stale = lag > 0.
"""
import json, hashlib, pathlib, os, sys, datetime as dt
from zoneinfo import ZoneInfo
import pandas as pd, pyarrow.parquet as pq
ROOT=pathlib.Path("/workspace/QuantLab"); SH=ZoneInfo("Asia/Shanghai"); OUT=ROOT/"output/data_freshness_status.json"
CAL=ROOT/"data/v2/calendar/trade_cal_sse_pit.parquet"; CUTOFF=int(os.environ.get("FRESH_CUTOFF_HOUR","20"))
T={ # name: (path, date column)  目录 = 按日文件 YYYYMMDD.parquet
 "daily_raw":("data/v2/tushare_raw/daily",None),
 "daily_ohlcv_raw_pit":("data/v2/bars/daily_ohlcv_raw_pit.parquet","trade_date"),
 "adj_factor":("data/v2/adj/adj_factor_2023h2plus.parquet","trade_date"),
 "daily_basic":("data/v2/valuation/daily_basic_full_tushare.parquet","trade_date"),
 "index_daily_pit":("data/v2/index/index_daily_pit.parquet","trade_date"),
 "etf_daily_adj":("data/v2/etf/etf_daily_adj.parquet","trade_date"),
 "etf510300":("data/v2/etf_510300/panels/sh.510300.parquet","available_at"),
 "mid_large_universe":("data/v2/universe/mid_large_members_pit.parquet","session"),
}
# 2026-10-18 draft (Arch P3-2): warn-level coverage; NEVER affects overall / stale_tables / tables (kept in a separate key so
# strict consumers of "tables" — e.g. quantlab/portfolio/research_loop.py data_freshness() — see no change)
W={ # name: (path, kind)  dir = per-day files YYYYMMDD.parquet ; manifest_sw = sw_pit manifest in_date_range max
 "sw_pit":("data/v2/sw_pit/manifest.json","manifest_sw"),
 "cyq_perf_raw":("data/v2/tushare_raw/cyq_perf","dir"),
 "tier3_concept_dc_index":("data/v2/tier3_daily/concept_dc_index","dir"),
 "tier3_concept_dc_member":("data/v2/tier3_daily/concept_dc_member","dir"),
 "tier3_concept_ths_index":("data/v2/tier3_daily/concept_ths_index","dir"),
 "tier3_anns":("data/v2/tier3_daily/anns","dir"),
 "tier3_news":("data/v2/tier3_daily/news","dir"),
 "tier3_research_report":("data/v2/tier3_daily/research_report","dir"),
}
def warn_tables(opn,exp):
    out={}
    for k,(rel,kind) in W.items():
        p=ROOT/rel; r=dict(path=rel,level="warn")
        try:
            if kind=="manifest_sw":
                m=json.loads(p.read_text()); last=max(str(m[l]["in_date_range"][1]).replace("-","")[:8] for l in ("l1","l2") if l in m)
                r.update(built=m.get("built"),basis="manifest in_date_range max (latest membership change, not a pull date)")
            else:
                fs=sorted(p.glob("2*.parquet")); last=fs[-1].stem; r.update(n_files=len(fs))
            lag=sum(1 for d in opn if last<d<=exp); r.update(last_date=last,lag_trading_days=lag,warn=lag>0)
        except Exception as e:
            r.update(error=str(e)[:200],warn=True,last_date=None,lag_trading_days=None)
        out[k]=r
    return out
def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()
def norm(v):
    if isinstance(v,(pd.Timestamp,dt.datetime)):
        v=pd.Timestamp(v); v=v.tz_convert(SH) if v.tzinfo else v; return v.strftime("%Y%m%d")
    return str(v).replace("-","")[:8]
def main(today=None):
    now=dt.datetime.now(SH); today=today or now.strftime("%Y%m%d")
    cal=pd.read_parquet(CAL); opn=cal[cal.is_open==1].cal_date.tolist()
    past=[d for d in opn if d<=today]; exp=past[-1]
    if exp==today and today==now.strftime("%Y%m%d") and now.hour<CUTOFF: exp=past[-2]
    out={}
    for k,(rel,col) in T.items():
        p=ROOT/rel; r=dict(path=rel)
        try:
            if p.is_dir():
                fs=sorted(p.glob("2*.parquet")); f=fs[-1]; last=f.stem
                r.update(rows=pq.ParquetFile(f).metadata.num_rows, rows_scope=f"last_file {f.name}", n_files=len(fs), sha256=sha(f))
            else:
                s=pd.read_parquet(p,columns=[col])[col]; last=norm(s.max())
                r.update(rows=len(s), sha256=sha(p))
            lag=sum(1 for d in opn if last<d<=exp)
            r.update(last_date=last,lag_trading_days=lag,stale=lag>0)
        except Exception as e:
            r.update(error=str(e)[:200],stale=True,last_date=None,lag_trading_days=None)
        out[k]=r
    c=dict(path=str(CAL.relative_to(ROOT)),rows=len(cal),last_date=cal.cal_date.max(),sha256=sha(CAL))
    c["stale"]=c["last_date"]<f"{today[:4]}1231" or not any(d>today for d in opn); c["lag_trading_days"]=0 if not c["stale"] else None
    out["trade_cal"]=c
    st=[k for k,v in out.items() if v.get("stale")]
    res=dict(expected_trade_date=exp,today_sh=today,cutoff_hour_sh=CUTOFF,overall="ok" if not st else "stale",stale_tables=st,
             tables=out,warn_tables=(wt:=warn_tables(opn,exp)),warn_list=[k for k,v in wt.items() if v.get("warn")],
             promotion_approved=False,generated_at=now.isoformat(),
             generated_at_et=now.astimezone(ZoneInfo("America/New_York")).isoformat())
    t=OUT.with_suffix(".tmp"); t.write_text(json.dumps(res,ensure_ascii=False,indent=2)); os.replace(t,OUT)
    print(json.dumps({k:res[k] for k in ["expected_trade_date","overall","stale_tables","warn_list"]},ensure_ascii=False))
if __name__=="__main__": main(*sys.argv[1:])
