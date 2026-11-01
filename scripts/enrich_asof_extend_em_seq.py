#!/usr/bin/env python3
"""Sequential EastMoney enrich for asof_extend — rate-limit friendly."""
from __future__ import annotations
import json, time, urllib.parse, urllib.request
from datetime import datetime, time as dtime
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd

ROOT = Path("/workspace/QuantLab")
PANELS = ROOT / "data/v2/asof_extend_202610/panels"
FM_OUT = ROOT / "data/v2/float_mktcap"
LOG = ROOT / "data/_acquire_logs"
EXT = ROOT / "data/v2/asof_extend_202610"
SH = ZoneInfo("Asia/Shanghai")
NY = ZoneInfo("America/New_York")
START, END = "20260701", "20261009"

def secid(iid: str) -> str | None:
    mkt, code = iid.split(".", 1)
    return {"sh": f"1.{code}", "sz": f"0.{code}", "bj": f"0.{code}"}.get(mkt)

def limit_ratio(iid: str, is_st: bool) -> float:
    if is_st: return 0.05
    code = iid.split(".")[1]; mkt = iid.split(".")[0]
    if mkt == "bj": return 0.30
    if code.startswith(("300","301","688","689")): return 0.20
    return 0.10

def fetch_em(iid: str) -> pd.DataFrame:
    sid = secid(iid)
    if not sid: return pd.DataFrame()
    params = dict(fields1="f1,f2,f3,f4,f5,f6", fields2="f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
                  ut="7eea3edcaed734bea9cbfc24409ed989", klt="101", fqt="0", secid=sid, beg=START, end=END, lmt="1000000")
    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 QuantLabEnrich/1.0", "Referer": "https://quote.eastmoney.com/"})
    last=None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                payload = json.loads(resp.read())
            data = payload.get("data") or {}
            name = data.get("name") or ""
            rows=[]
            for line in data.get("klines") or []:
                p=line.split(",")
                if len(p)<11: continue
                rows.append(dict(date=p[0], open=float(p[1]), close=float(p[2]), high=float(p[3]), low=float(p[4]),
                                 volume=float(p[5]), amount=float(p[6]), turnover=float(p[10]), name=name))
            return pd.DataFrame(rows)
        except Exception as e:
            last=e; time.sleep(1.2*(attempt+1))
    raise RuntimeError(repr(last))

def main():
    NOW=datetime.now(NY)
    LOG.mkdir(exist_ok=True); FM_OUT.mkdir(parents=True, exist_ok=True)
    progress=LOG/"asof_enrich_seq_progress.jsonl"
    paths=sorted(PANELS.glob("*.parquet"))
    todo=[]
    for p in paths:
        df=pd.read_parquet(p, columns=["amount"])
        if df["amount"].notna().mean() < 0.5:
            todo.append(p)
    print(json.dumps({"todo": len(todo), "total": len(paths)}), flush=True)
    fm_buf=[]; ok=fail=0
    for i,p in enumerate(todo,1):
        iid=p.stem
        try:
            panel=pd.read_parquet(p); em=fetch_em(iid)
            if em.empty:
                rec={"instrument_id":iid,"ok":True,"rows":0,"note":"em_empty"}; fail+=0; ok+=1
            else:
                em["date"]=pd.to_datetime(em["date"])
                panel=panel.copy(); panel["event_time"]=pd.to_datetime(panel["event_time"])
                name=str(em["name"].iloc[-1]); is_st="ST" in name.upper() or "st" in name
                lr=limit_ratio(iid,is_st)
                m=panel.merge(em[["date","amount","turnover","close"]].rename(columns={"date":"event_time","amount":"amount_em","turnover":"turnover_em","close":"close_em"}), on="event_time", how="left")
                m["amount"]=m["amount_em"]; m["turnover"]=m["turnover_em"]
                em2=em.sort_values("date"); em2["prev_close"]=em2["close"].shift(1)
                m=m.merge(em2[["date","prev_close"]].rename(columns={"date":"event_time"}), on="event_time", how="left")
                tick=0.01
                m["limit_up"]=(m["prev_close"]*(1+lr)/tick).round()*tick
                m["limit_down"]=(m["prev_close"]*(1-lr)/tick).round()*tick
                m["is_st_at_open"]=float(1.0 if is_st else 0.0)
                m["limit_ratio_at_open"]=lr
                m["quality_status"]="research_not_promotable:tencent_ohlc_em_amount_turnover_derived_limits"
                m["source"]="tencent_ifzq+eastmoney_push2his"
                m=m.drop(columns=[c for c in ["amount_em","turnover_em","close_em","prev_close"] if c in m.columns])
                m.to_parquet(p, index=False)
                for _,r in m.iterrows():
                    amt,turn=r.get("amount"),r.get("turnover"); fm=np.nan
                    if pd.notna(amt) and pd.notna(turn) and float(turn)>0:
                        fm=float(amt)*100.0/float(turn)
                    fm_buf.append(dict(instrument_id=iid, session=pd.Timestamp(r["event_time"]).date(), float_mktcap=fm,
                        available_at=datetime.combine(pd.Timestamp(r["event_time"]).date(), dtime(18,0), tzinfo=SH),
                        source="derived_amount_over_turnover_percent_em", revision="asof_extend_em_enrich_seq_v1",
                        quality_status="research_not_promotable:derived_proxy_not_official_float"))
                rec={"instrument_id":iid,"ok":True,"rows":len(m),"amount_nn":int(m["amount"].notna().sum()),"is_st":is_st}
                ok+=1
        except Exception as e:
            rec={"instrument_id":iid,"ok":False,"error":repr(e)}; fail+=1
        with progress.open("a") as f: f.write(json.dumps(rec, ensure_ascii=False)+"\n")
        if i%50==0 or i==len(todo):
            print(json.dumps({"done":i,"todo":len(todo),"ok":ok,"fail":fail,"fm":len(fm_buf)}), flush=True)
        time.sleep(0.08)

    if fm_buf:
        fm=pd.DataFrame(fm_buf)
        old=FM_OUT/"float_mktcap_asof_2026-06-30.parquet"
        parts=[fm]
        if old.exists():
            prev=pd.read_parquet(old); prev["session"]=pd.to_datetime(prev["session"]).dt.date; parts.append(prev)
        all_fm=pd.concat(parts, ignore_index=True).drop_duplicates(["instrument_id","session"], keep="last")
        all_fm=all_fm[["instrument_id","session","float_mktcap","available_at","source","revision","quality_status"]]
        max_sess=max(all_fm["session"])
        latest=all_fm[all_fm["session"]==max_sess]
        daily=FM_OUT/"float_mktcap_daily_20260630_20261009.parquet"
        all_fm.to_parquet(daily, index=False)
        latest.to_parquet(FM_OUT/"float_mktcap_asof.parquet", index=False)
        latest.to_parquet(FM_OUT/f"float_mktcap_asof_{max_sess}.parquet", index=False)
        meta=dict(schema_version="quantlab.v2.float_mktcap.v1", field="float_mktcap", unit="CNY", promotion_approved=False,
                  daily_path=str(daily), asof_path=str(FM_OUT/"float_mktcap_asof.parquet"),
                  session_min=str(min(all_fm["session"])), session_max=str(max_sess),
                  daily_rows=int(len(all_fm)), daily_non_null=int(all_fm["float_mktcap"].notna().sum()),
                  asof_rows=int(len(latest)), asof_non_null=int(latest["float_mktcap"].notna().sum()),
                  formula="amount*100/turnover (turnover percent, amount CNY EM)",
                  limitations=["research_not_promotable","derived proxy not official free-float"],
                  fetch_time=NOW.isoformat())
        (FM_OUT/"manifest.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2)+"\n")
        print(json.dumps({"float_mktcap": {k:meta[k] for k in ["daily_rows","daily_non_null","session_min","session_max","asof_non_null"]}}), flush=True)
    summary=dict(ok=ok, fail=fail, todo=len(todo), promotion_approved=False, fetch_time=NOW.isoformat())
    (LOG/"asof_enrich_seq_latest.json").write_text(json.dumps(summary, indent=2)+"\n")
    (EXT/"enrich_manifest.json").write_text(json.dumps(summary, indent=2)+"\n")
    print(json.dumps({"done":True, **summary}), flush=True)

if __name__=="__main__":
    main()
