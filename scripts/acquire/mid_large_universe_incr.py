#!/usr/bin/env python3
"""mid_large universe 增量 (口径见 data/v2/universe/MID_LARGE_RULE.md, 不变).
session S 成员 = SSE+SZSE(排除BSE), 排除 S 日 ST/*ST(namechange 区间), 以前一交易日 float_mktcap>0 且 turnover_rate>0 排序, 取前 n_eligible//2.
available_at = S 09:00 Asia/Shanghai. 只追加 session > 现有 session_max, 旧行不动. 幂等可重复运行.
交易日历 = daily_basic_full_tushare 的 trade_date (最新可得 session = daily_basic 最新日).
用法: python3 scripts/acquire/mid_large_universe_incr.py [--date YYYYMMDD] [--verify N] [--no-status]
"""
import argparse, json, os, hashlib, shutil, pathlib, datetime as dt
import pandas as pd, pyarrow.parquet as pq, pyarrow as pa
from zoneinfo import ZoneInfo
ROOT=pathlib.Path("/workspace/QuantLab"); ET=ZoneInfo("America/New_York")
OUT=ROOT/"data/v2/universe/mid_large_members_pit.parquet"; MAN=OUT.with_name("mid_large_members_pit_manifest.json")
DB=ROOT/"data/v2/valuation/daily_basic_full_tushare.parquet"; ST=ROOT/"data/v2/st_events/st_events_from_namechange.parquet"
STATUS=ROOT/"output/daily_update_status.json"

def build(sessions, cal, st):
    need=set(); prev={}
    for s in sessions:
        i=cal.index(s); prev[s]=cal[i-1]; need.add(cal[i-1])
    db=pq.read_table(DB,columns=["ts_code","instrument_id","trade_date","turnover_rate","float_mktcap"],
                     filters=[("trade_date","in",[pd.Timestamp(x) for x in need])]).to_pandas()
    db["d"]=db.trade_date.dt.strftime("%Y-%m-%d")
    st=st[st.name.str.contains("ST",na=False)].copy()
    out=[]
    for s in sessions:
        b=db[db.d==prev[s]]
        b=b[b.ts_code.str.endswith((".SH",".SZ"))]
        s8=s.replace("-","")
        stc=set(st[(st.start_date<=s8)&(st.end_date.isna()|(st.end_date>=s8))].ts_code)
        b=b[~b.ts_code.isin(stc)&(b.float_mktcap>0)&(b.turnover_rate>0)]
        k=len(b)//2
        b=b.sort_values("float_mktcap",ascending=False,kind="mergesort").head(k)
        out.append(pd.DataFrame({"session":s,"instrument_id":b.instrument_id.values,"universe_id":"mid_large",
            "available_at":pd.Timestamp(s+" 09:00",tz="Asia/Shanghai"),"float_mktcap_basis":b.float_mktcap.values,"basis_trade_date":prev[s]}))
    df=pd.concat(out,ignore_index=True); df["available_at"]=df.available_at.astype("datetime64[us, Asia/Shanghai]"); return df

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1<<20),b""): h.update(c)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--date"); ap.add_argument("--verify",type=int,default=0); ap.add_argument("--no-status",action="store_true"); a=ap.parse_args()
    cal=sorted(pd.Series(pq.read_table(DB,columns=["trade_date"]).column(0).to_pandas().unique()).dt.strftime("%Y-%m-%d"))
    end=a.date and f"{a.date[:4]}-{a.date[4:6]}-{a.date[6:]}" or cal[-1]
    st=pd.read_parquet(ST); old=pd.read_parquet(OUT); smax=old.session.max()
    if a.verify:
        ss=sorted(old.session.unique())[-a.verify:]; re=build(ss,cal,st)
        o=old[old.session.isin(ss)].reset_index(drop=True)
        m=o.merge(re,on=["session","instrument_id"],how="outer",indicator=True,suffixes=("","_r"))
        print("VERIFY sessions",ss,"old",len(o),"rebuilt",len(re),m._merge.value_counts().to_dict(),
              "max|mcap diff|",(m.float_mktcap_basis-m.float_mktcap_basis_r).abs().max()); return
    new=[s for s in cal if smax<s<=end]
    if new:
        add=build(new,cal,st)
        bak=OUT.with_name(f"mid_large_members_pit.bak_{smax.replace('-','')}.parquet")
        if not bak.exists(): shutil.copy2(OUT,bak)
        full=pd.concat([old,add[old.columns]],ignore_index=True)
        tbl=pa.Table.from_pandas(full,schema=pq.read_schema(OUT).remove_metadata(),preserve_index=False)
        tmp=OUT.with_suffix(".tmp"); pq.write_table(tbl,tmp); os.replace(tmp,OUT)
        print("APPENDED",new,add.groupby("session").size().to_dict())
    else: print("UP-TO-DATE",smax)
    df=pd.read_parquet(OUT,columns=["session","instrument_id"]); h=sha(OUT)
    man=json.loads(MAN.read_text()); man.update(rows=len(df),sessions=int(df.session.nunique()),session_max=df.session.max(),
        instruments_union=int(df.instrument_id.nunique()),sha256=h,promotion_approved=False,
        incremental={"script":"scripts/acquire/mid_large_universe_incr.py","appended_sessions":new,"at":dt.datetime.now(ET).isoformat(timespec="seconds")})
    MAN.write_text(json.dumps(man,ensure_ascii=False,indent=2))
    if a.no_status: return
    r=dict(path=str(OUT),last_date=df.session.max(),rows=len(df),n_members_last=int((df.session==df.session.max()).sum()),
           sha256=h,manifest=str(MAN),finished_at=dt.datetime.now(ET).isoformat(timespec="seconds"))
    st_=json.loads(STATUS.read_text()) if STATUS.exists() else {"schema":"quantlab.v2.daily_update_status.v1","tables":{},"errors":{}}
    st_["tables"]["mid_large_universe"]=r; st_.setdefault("errors",{}).pop("mid_large_universe",None)
    exp=st_.get("target_trade_date",end)
    ok=all(str(t.get("last_date",""))[:10]>=exp for k,t in st_["tables"].items() if k!="dividend") and not st_["errors"]
    st_.update(status="ok" if ok else "partial",finished_at=r["finished_at"],promotion_approved=False,live=False)
    t=STATUS.with_suffix(".tmp"); t.write_text(json.dumps(st_,ensure_ascii=False,indent=2)); os.replace(t,STATUS); print("STATUS",st_["status"])
if __name__=="__main__": main()
