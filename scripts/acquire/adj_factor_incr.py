#!/usr/bin/env python3
"""adj_factor_2023h2plus.parquet 增量追加 (2026-10-18 Data 修: 此前无任何步骤维护, 停在 20261013).
从 data/v2/tushare_raw/adj_factor/YYYYMMDD.parquet 追加 > 现 max(trade_date) 且 <= --date 的交易日; 只追加不改历史; 原子替换; 写 manifest."""
import argparse, hashlib, json, os, pathlib, datetime as dt
import pandas as pd
ROOT=pathlib.Path("/workspace/QuantLab"); P=ROOT/"data/v2/adj/adj_factor_2023h2plus.parquet"; RAW=ROOT/"data/v2/tushare_raw/adj_factor"
def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()
ap=argparse.ArgumentParser(); ap.add_argument("--date",required=True); a=ap.parse_args()
x=pd.read_parquet(P); last=x.trade_date.max()
new=[f for f in sorted(RAW.glob("2*.parquet")) if last<f.stem<=a.date]
parts=[pd.read_parquet(f)[["ts_code","trade_date","adj_factor"]] for f in new]
parts=[p for p in parts if len(p)]
if parts:
    add=pd.concat(parts,ignore_index=True).drop_duplicates(["ts_code","trade_date"],keep="last")
    y=pd.concat([x,add],ignore_index=True)
    assert not y.duplicated(["ts_code","trade_date"]).any()
    t=P.with_suffix(".tmp.parquet"); y.to_parquet(t,index=False); os.replace(t,P)
else: add=pd.DataFrame(); y=x
m=dict(path=str(P.relative_to(ROOT)),rows=len(y),last_date=y.trade_date.max(),prev_last_date=last,days_added=[f.stem for f in new],rows_added=len(add),
       sha256=sha(P),source="tushare_raw/adj_factor daily files",promotion_approved=False,updated_at=dt.datetime.now().astimezone().isoformat(timespec="seconds"))
(P.parent/"adj_factor_2023h2plus_manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n"); print(json.dumps(m,ensure_ascii=False))
