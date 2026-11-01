"""Merge X1 top_list/top_inst raw into dragon_tiger parquets; optional seat label. Research-grade."""
from __future__ import annotations
import os, sys, json, pathlib, shutil
sys.path.insert(0, "/workspace/QuantLab")
import pandas as pd
import numpy as np

ROOT = pathlib.Path("/workspace/QuantLab")
RAW = ROOT / "data/v2/tushare_raw"
V = ROOT / "data/v2"
INST_PAT = r"机构|基金|社保|保险|券商|托管|沪股通|深股通|港股通|北向|QFII"

def load_glob(api):
    files = sorted((RAW / api).glob("*.parquet"))
    if not files:
        return pd.DataFrame()
    return pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)

def main():
    tl = load_glob("top_list")
    ti = load_glob("top_inst")
    assert len(tl) and len(ti), "missing raw"
    tl["trade_date"] = tl["trade_date"].astype(str).str.replace("-", "").str[:8]
    ti["trade_date"] = ti["trade_date"].astype(str).str.replace("-", "").str[:8]
    # seat label (simple regex; full seat_type map can be reapplied later)
    ti = ti.copy()
    ti["seat_label"] = np.where(
        ti["exalter"].astype(str).str.contains(INST_PAT, na=False),
        "机构/通道",
        "营业部/游资候选",
    )
    for df in (tl, ti):
        d = df["trade_date"]
        df["available_at"] = pd.to_datetime(d, format="%Y%m%d") + pd.Timedelta(hours=18)
        df["available_at_tz"] = "Asia/Shanghai"
        df["available_at_rule"] = "trade_date 18:00 Asia/Shanghai (post-close publish)"
        df["promotion_approved"] = False
    # alpha conservative available_at
    ti["available_at_alpha_conservative"] = ti["available_at"] + pd.Timedelta(days=1) - pd.Timedelta(hours=3)  # T+1 15:00
    # seat_type from map if exists
    emap = V / "dragon_tiger/exalter_institution_map.parquet"
    if emap.exists():
        m = pd.read_parquet(emap)
        ti = ti.drop(columns=[c for c in ("seat_type", "is_institution") if c in ti.columns], errors="ignore")
        ti = ti.merge(m[["exalter", "seat_type", "is_institution"]], on="exalter", how="left")
        # fill unmapped via seat_label
        ti["seat_type"] = ti["seat_type"].fillna(pd.Series(
            np.where(ti["seat_label"] == "机构/通道", "institution", "retail_or_hot_money"), index=ti.index)
        )
        ti["is_institution"] = ti["is_institution"].fillna(ti["seat_label"] == "机构/通道")
    else:
        ti["seat_type"] = np.where(ti["seat_label"] == "机构/通道", "institution", "retail_or_hot_money"), index=ti.index)
        ti["is_institution"] = ti["seat_label"] == "机构/通道"

    odir = V / "dragon_tiger"
    odir.mkdir(exist_ok=True)
    for name, df in [("top_list", tl), ("top_inst", ti)]:
        p = odir / f"{name}.parquet"
        if p.exists():
            shutil.copy2(p, odir / f"{name}.parquet.bak_pre_x1")
        df = df.drop_duplicates(subset=[c for c in df.columns if c in ("trade_date", "ts_code", "exalter", "side", "reason")][:4] if name=="top_inst" else ["trade_date","ts_code","reason"], keep="last")
        # safer dedupe
        if name == "top_list":
            df = df.drop_duplicates(["trade_date", "ts_code", "reason"], keep="last")
        else:
            keys = [k for k in ["trade_date", "ts_code", "exalter", "side", "reason"] if k in df.columns]
            df = df.drop_duplicates(keys, keep="last")
        df = df.sort_values("trade_date")
        df.to_parquet(p, index=False)
        if name == "top_list":
            tl = df
        else:
            ti = df
    ti.to_parquet(odir / "top_inst_labeled.parquet", index=False)

    cal = pd.read_parquet(RAW / "trade_cal.parquet")
    cal = cal[cal.is_open.astype(int) == 1]
    dmin, dmax = str(tl.trade_date.min()), str(tl.trade_date.max())
    ds = sorted(x for x in cal.cal_date.astype(str) if dmin <= x <= dmax)
    have = set(tl.trade_date.astype(str))
    miss = [d for d in ds if d not in have]
    x1 = tl[(tl.trade_date >= "20150101") & (tl.trade_date <= "20171231")]
    summary = {
        "top_list_rows": int(len(tl)),
        "top_inst_rows": int(len(ti)),
        "days": int(tl.trade_date.nunique()),
        "range": [dmin, dmax],
        "x1_top_list_rows": int(len(x1)),
        "x1_days": int(x1.trade_date.nunique()),
        "x1_range": [str(x1.trade_date.min()), str(x1.trade_date.max())] if len(x1) else None,
        "trading_days_in_range": len(ds),
        "missing_vs_cal": len(miss),
        "missing_sample": miss[:20],
        "seat_label_counts": ti.seat_label.value_counts().to_dict() if "seat_label" in ti.columns else {},
        "available_at_rule": "trade_date 18:00 Asia/Shanghai (post-close publish); available_at_alpha_conservative=T+1 15:00",
        "can_backdate_available_at": False,
        "can_backdate_reason": "no source evidence for earlier publish clock; keep T 18:00 / conservative T+1 15:00",
        "promotion_approved": False,
        "paths": {
            "top_list": str(odir / "top_list.parquet"),
            "top_inst": str(odir / "top_inst.parquet"),
            "top_inst_labeled": str(odir / "top_inst_labeled.parquet"),
        },
    }
    json.dump(summary, open(odir / "coverage_summary.json", "w"), ensure_ascii=False, indent=2, default=str)
    json.dump(summary, open(odir / "x1_extend_summary.json", "w"), ensure_ascii=False, indent=2, default=str)
    print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))

if __name__ == "__main__":
    main()
