#!/usr/bin/env python3
"""Build float_mktcap_daily_from2015_tushare.parquet from daily_basic 2015+.
Units: yuan (circ_mv/total_mv * 10000). Research-grade. Includes delisted.
"""
import os, sys, json, datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import pandas as pd, numpy as np

ROOT = Path("/workspace/QuantLab")
RAW = ROOT / "data/v2/tushare_raw/daily_basic"
OUT = ROOT / "data/v2/float_mktcap"
OUT.mkdir(parents=True, exist_ok=True)

def to_iid(s: pd.Series) -> pd.Series:
    s = s.astype(str)
    out = s.copy()
    m = s.str.endswith(".SH"); out = out.where(~m, "sh." + s.str[:6])
    m = s.str.endswith(".SZ"); out = out.where(~m, "sz." + s.str[:6])
    m = s.str.endswith(".BJ"); out = out.where(~m, "bj." + s.str[:6])
    return out

files = sorted(RAW.glob("*.parquet"))
# keep 2015+
files = [f for f in files if f.stem >= "20150101"]
print(f"daily_basic files 2015+: {len(files)} {files[0].stem if files else '-'} -> {files[-1].stem if files else '-'}", flush=True)

rows = []
for i, f in enumerate(files, 1):
    x = pd.read_parquet(f)
    if x.empty or "circ_mv" not in x.columns:
        continue
    y = pd.DataFrame({
        "instrument_id": to_iid(x.ts_code),
        "trade_date": pd.to_datetime(x.trade_date.astype(str)),
        "float_mktcap": pd.to_numeric(x.circ_mv, errors="coerce") * 10000.0,
        "total_mv": pd.to_numeric(x["total_mv"], errors="coerce") * 10000.0 if "total_mv" in x.columns else np.nan,
        "turnover_rate": pd.to_numeric(x["turnover_rate"], errors="coerce") if "turnover_rate" in x.columns else np.nan,
        "source": "tushare_leo",
        "schema": "quantlab.v2.float_mktcap.v1",
        "quality_status": "research",
        "promotion_approved": False,
    })
    rows.append(y)
    if i % 200 == 0:
        print(f"  read {i}/{len(files)}", flush=True)

m = pd.concat(rows, ignore_index=True).dropna(subset=["float_mktcap"])
m = m.sort_values(["instrument_id", "trade_date"]).drop_duplicates(["instrument_id", "trade_date"], keep="last")
dest = OUT / "float_mktcap_daily_from2015_tushare.parquet"
m.to_parquet(dest, index=False)

# spot-check bj.920680 / 2023-12-29
spot = m[(m.instrument_id == "bj.920680") & (m.trade_date == "2023-12-29")]
print("spot bj.920680 2023-12-29:", spot[["float_mktcap", "total_mv"]].to_dict("records") if len(spot) else "MISSING")

# year summary + delisted overlap
sb_d = pd.read_parquet(ROOT / "data/v2/tushare_raw/stock_basic/D.parquet")
sb_d["iid"] = to_iid(sb_d.ts_code)
delisted = set(sb_d.iid)
m["y"] = m.trade_date.dt.year
by = m.groupby("y").agg(rows=("instrument_id", "size"), n=("instrument_id", "nunique"))
print(by.to_string())
print("rows", len(m), "inst", m.instrument_id.nunique(),
      "date", str(m.trade_date.min())[:10], "->", str(m.trade_date.max())[:10])
print("delisted in panel", len(set(m.instrument_id) & delisted), "/", len(delisted))

# 2015-2017 delisted with list overlap
sb_d["list_date"] = pd.to_datetime(sb_d.list_date, errors="coerce")
sb_d["delist_date"] = pd.to_datetime(sb_d.delist_date, errors="coerce")
need = sb_d[(sb_d.list_date < "2018-01-01") & (sb_d.delist_date >= "2015-01-01")]
have = set(m[m.trade_date < "2018-01-01"].instrument_id)
print("delisted overlapping 2015-17 window", len(need), "in panel", len(set(need.iid) & have))

meta = {
    "built_at": datetime.datetime.now(ZoneInfo("America/New_York")).isoformat(),
    "path": str(dest),
    "rows": int(len(m)),
    "n_instruments": int(m.instrument_id.nunique()),
    "date_min": str(m.trade_date.min())[:10],
    "date_max": str(m.trade_date.max())[:10],
    "unit": "yuan",
    "source": "tushare daily_basic circ_mv/total_mv * 10000",
    "includes_delisted": True,
    "quality_status": "research",
    "promotion_approved": False,
    "bj_920680_20231229_float_mktcap": float(spot.float_mktcap.iloc[0]) if len(spot) else None,
    "by_year": {str(int(y)): {"rows": int(r.rows), "n": int(r.n)} for y, r in by.iterrows()},
}
(OUT / "float_mktcap_daily_from2015_manifest.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
print("wrote", dest, "bytes", dest.stat().st_size)
print("DONE")
