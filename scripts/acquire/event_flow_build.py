"""Materialize research-grade event/flow tables from tushare_raw.
promotion_approved=false. Sets available_at in Asia/Shanghai.
"""
from __future__ import annotations
import json, pathlib, re, glob
import pandas as pd
import numpy as np

ROOT = pathlib.Path("/workspace/QuantLab")
RAW = ROOT / "data/v2/tushare_raw"
V = ROOT / "data/v2"
OUT_DOC = ROOT / "docs/v2"
OUT_D1 = ROOT / "output/d1"

# keyword -> category (order matters; first match wins)
TYPE_RULES = [
    (r"回购", "回购"),
    (r"增持", "增持"),
    (r"减持", "减持"),
    (r"业绩预告|业绩预增|业绩预减|业绩扭亏|业绩盈转亏|业绩快报", "业绩预告"),
    (r"问询函|关注函|监管函", "问询函"),
    (r"处罚|警示|公开谴责|监管措施", "监管处罚"),
    (r"重大资产重组|并购|收购", "重组并购"),
    (r"股权激励|员工持股", "股权激励"),
    (r"分红|利润分配|送转", "分红分配"),
    (r"举牌|权益变动", "权益变动"),
    (r"停牌|复牌", "停复牌"),
    (r"立案|诉讼|仲裁", "诉讼立案"),
    (r"年报|半年报|季报|定期报告", "定期报告"),
]

INST_PAT = re.compile(r"机构专用|机构专用席位|沪股通|深股通|港股通|机构")

def load_glob(api):
    files = sorted(glob.glob(str(RAW / api / "*.parquet")))
    frames = []
    for f in files:
        p = pathlib.Path(f)
        if p.stat().st_size == 0:
            continue
        try:
            frames.append(pd.read_parquet(p))
        except Exception:
            continue
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    # coerce mixed object/numeric columns from heterogeneous yearly dumps
    for c in df.columns:
        if df[c].dtype == object and c not in (
            "ts_code", "trade_date", "ann_date", "ann_time", "title", "url",
            "name", "symbol", "ann_type", "exalter", "reason", "side", "code",
            "exchange", "exchange_id",
        ):
            n = pd.to_numeric(df[c], errors="coerce")
            if n.notna().sum() >= df[c].notna().sum() * 0.5:
                df[c] = n
    return df

def classify_title(title, ann_type=None):
    if isinstance(ann_type, str) and ann_type.strip():
        # map known ann_type strings loosely
        t = ann_type.strip()
        for pat, lab in TYPE_RULES:
            if re.search(pat, t):
                return lab
    s = str(title or "")
    for pat, lab in TYPE_RULES:
        if re.search(pat, s):
            return lab
    if isinstance(ann_type, str) and ann_type.strip():
        return ann_type.strip()
    return "其他"

def available_at_ann(row):
    """Asia/Shanghai available_at from ann_time or ann_date 00:00.
    Rule: if ann_time has clock != 00:00:00 use it; else use ann_date 15:00
    (conservative: same-calendar-day bulletin without clock treated as available
    at close). Documented in EVENT_FLOW_DATA_STATUS.md.
    """
    ad = str(row.get("ann_date") or "").replace("-", "")[:8]
    at = str(row.get("ann_time") or "")
    if len(ad) != 8 or not ad.isdigit():
        return pd.NaT
    base = pd.Timestamp(ad)
    # try parse ann_time
    ts = None
    if at and at not in ("None", "nan", "NaT"):
        try:
            ts = pd.Timestamp(at)
        except Exception:
            ts = None
    if ts is not None and not pd.isna(ts):
        if ts.hour == 0 and ts.minute == 0 and ts.second == 0:
            # date-only timestamp → treat as close
            return pd.Timestamp(f"{ad[:4]}-{ad[4:6]}-{ad[6:]} 15:00:00")
        return ts
    return pd.Timestamp(f"{ad[:4]}-{ad[4:6]}-{ad[6:]} 15:00:00")

def build_anns():
    df = load_glob("anns_d")
    if df.empty:
        return {"rows": 0}
    # normalize columns
    for c in ["ts_code", "name", "title", "url", "ann_date", "ann_time", "ann_type", "symbol"]:
        if c not in df.columns:
            df[c] = None
    df["ann_date"] = df["ann_date"].astype(str).str.replace("-", "").str[:8]
    df["category"] = [classify_title(t, a) for t, a in zip(df["title"], df["ann_type"])]
    df["available_at"] = df.apply(available_at_ann, axis=1)
    df["available_at_tz"] = "Asia/Shanghai"
    df["available_at_rule"] = "ann_time if clock>00:00 else ann_date 15:00 Asia/Shanghai"
    df["instrument_id"] = df["ts_code"]
    df["promotion_approved"] = False
    cols = ["instrument_id", "ts_code", "name", "title", "ann_date", "ann_time",
            "available_at", "available_at_tz", "available_at_rule",
            "ann_type", "category", "url", "symbol"]
    out = df[cols].drop_duplicates(subset=["ts_code", "ann_date", "title", "url"], keep="first")
    odir = V / "announcements"; odir.mkdir(parents=True, exist_ok=True)
    # split by year for size
    out["year"] = out["ann_date"].str[:4]
    for y, g in out.groupby("year"):
        g.drop(columns=["year"]).to_parquet(odir / f"anns_meta_{y}.parquet", index=False)
    out.drop(columns=["year"]).to_parquet(odir / "anns_meta_2018plus.parquet", index=False)
    # truncation report from raw file sizes
    trunc_days = []
    for f in sorted((RAW / "anns_d").glob("*.parquet")):
        try:
            n = len(pd.read_parquet(f, columns=["ann_date"] if False else None))
        except Exception:
            # cheaper: row count via parquet metadata
            import pyarrow.parquet as pq
            n = pq.read_metadata(f).num_rows
        if n >= 5000:
            trunc_days.append(f.stem)
    summary = {
        "rows": int(len(out)),
        "codes": int(out.ts_code.nunique()),
        "ann_date_min": str(out.ann_date.min()),
        "ann_date_max": str(out.ann_date.max()),
        "days": int(out.ann_date.nunique()),
        "category_counts": out.category.value_counts().head(20).to_dict(),
        "url_nonnull_pct": round(float(out.url.notna().mean() * 100), 2),
        "ann_type_nonnull_pct": round(float(out.ann_type.notna().mean() * 100), 2),
        "truncated_days_n": len(trunc_days),
        "truncated_days_sample": trunc_days[:30],
        "body": "metadata+url only; full text not in anns_d — fetch via url if needed",
        "promotion_approved": False,
        "path": str(odir / "anns_meta_2018plus.parquet"),
    }
    json.dump(summary, open(odir / "anns_meta_summary.json", "w"), ensure_ascii=False, indent=2, default=str)
    return summary

def build_dragon_tiger():
    tl = pd.read_parquet(V / "dragon_tiger" / "top_list.parquet")
    ti = pd.read_parquet(V / "dragon_tiger" / "top_inst.parquet")
    # label seats
    ti = ti.copy()
    ti["seat_label"] = np.where(
        ti["exalter"].astype(str).str.contains(INST_PAT, na=False),
        "机构/通道",
        "营业部/游资候选",
    )
    # available_at: 龙虎榜通常当日收盘后披露，取 trade_date 18:00 Asia/Shanghai
    for df in (tl, ti):
        d = df["trade_date"].astype(str).str.replace("-", "").str[:8]
        df["available_at"] = pd.to_datetime(d, format="%Y%m%d") + pd.Timedelta(hours=18)
        df["available_at_tz"] = "Asia/Shanghai"
        df["available_at_rule"] = "trade_date 18:00 Asia/Shanghai (post-close publish)"
        df["promotion_approved"] = False
    odir = V / "dragon_tiger"
    tl.to_parquet(odir / "top_list.parquet", index=False)
    ti.to_parquet(odir / "top_inst.parquet", index=False)
    # seat labeled view
    ti.to_parquet(odir / "top_inst_labeled.parquet", index=False)
    cal = pd.read_parquet(RAW / "trade_cal.parquet")
    cal = cal[cal.is_open.astype(int) == 1]
    ds = sorted(x for x in cal.cal_date.astype(str) if "20180101" <= x <= "20261009")
    have = set(tl.trade_date.astype(str))
    miss = [d for d in ds if d not in have]
    summary = {
        "top_list_rows": int(len(tl)),
        "top_inst_rows": int(len(ti)),
        "days": int(tl.trade_date.nunique()),
        "range": [str(tl.trade_date.min()), str(tl.trade_date.max())],
        "trading_days_in_range": len(ds),
        "missing_vs_cal": len(miss),
        "missing_sample": miss[:10],
        "seat_label_counts": ti.seat_label.value_counts().to_dict(),
        "promotion_approved": False,
        "paths": {
            "top_list": str(odir / "top_list.parquet"),
            "top_inst": str(odir / "top_inst.parquet"),
            "top_inst_labeled": str(odir / "top_inst_labeled.parquet"),
        },
    }
    json.dump(summary, open(odir / "coverage_summary.json", "w"), ensure_ascii=False, indent=2, default=str)
    return summary

def build_margin():
    md = load_glob("margin_detail")
    ms = load_glob("margin")
    odir = V / "margin"; odir.mkdir(parents=True, exist_ok=True)
    summary = {}
    if len(md):
        md = md.copy()
        md["trade_date"] = md["trade_date"].astype(str).str.replace("-", "").str[:8]
        # available_at = trade_date close (Tushare publishes after close)
        md["available_at"] = pd.to_datetime(md["trade_date"], format="%Y%m%d") + pd.Timedelta(hours=18)
        md["available_at_tz"] = "Asia/Shanghai"
        md["available_at_rule"] = "trade_date 18:00 Asia/Shanghai"
        md["promotion_approved"] = False
        md = md.drop_duplicates(["trade_date", "ts_code"], keep="last")
        md.to_parquet(odir / "margin_detail_daily_2018plus.parquet", index=False)
        mkt = md.ts_code.str[-2:].value_counts().to_dict()
        # per-day market completeness check sample
        by = md.groupby("trade_date").apply(lambda g: g.ts_code.str[-2:].nunique()).describe().to_dict()
        summary["margin_detail"] = {
            "rows": int(len(md)),
            "codes": int(md.ts_code.nunique()),
            "days": int(md.trade_date.nunique()),
            "range": [str(md.trade_date.min()), str(md.trade_date.max())],
            "market_counts_total": mkt,
            "markets_per_day_describe": {k: float(v) for k, v in by.items()},
            "path": str(odir / "margin_detail_daily_2018plus.parquet"),
            "note": "pulled via datahub with fields= to avoid SH-only local cache",
            "promotion_approved": False,
        }
    if len(ms):
        ms = ms.copy()
        ms["trade_date"] = ms["trade_date"].astype(str).str.replace("-", "").str[:8]
        ms["available_at"] = pd.to_datetime(ms["trade_date"], format="%Y%m%d") + pd.Timedelta(hours=18)
        ms["available_at_tz"] = "Asia/Shanghai"
        ms["promotion_approved"] = False
        ms = ms.drop_duplicates(["trade_date", "exchange_id"], keep="last")
        ms.to_parquet(odir / "margin_exchange_daily_2018plus.parquet", index=False)
        summary["margin_exchange"] = {
            "rows": int(len(ms)),
            "days": int(ms.trade_date.nunique()),
            "range": [str(ms.trade_date.min()), str(ms.trade_date.max())],
            "exchanges": ms.exchange_id.value_counts().to_dict() if "exchange_id" in ms else {},
            "path": str(odir / "margin_exchange_daily_2018plus.parquet"),
            "promotion_approved": False,
        }
    json.dump(summary, open(odir / "margin_summary.json", "w"), ensure_ascii=False, indent=2, default=str)
    return summary

def build_northbound():
    odir = V / "northbound"; odir.mkdir(parents=True, exist_ok=True)
    summary = {}
    mf = load_glob("moneyflow_hsgt")
    if len(mf):
        mf = mf.copy()
        mf["trade_date"] = mf["trade_date"].astype(str).str.replace("-", "").str[:8]
        mf["available_at"] = pd.to_datetime(mf["trade_date"], format="%Y%m%d") + pd.Timedelta(hours=18)
        mf["available_at_tz"] = "Asia/Shanghai"
        mf["available_at_rule"] = "trade_date 18:00 Asia/Shanghai"
        mf["promotion_approved"] = False
        mf = mf.drop_duplicates(["trade_date"], keep="last").sort_values("trade_date")
        mf.to_parquet(odir / "moneyflow_hsgt_daily_2018plus.parquet", index=False)
        summary["moneyflow_hsgt"] = {
            "rows": int(len(mf)),
            "days": int(mf.trade_date.nunique()),
            "range": [str(mf.trade_date.min()), str(mf.trade_date.max())],
            "path": str(odir / "moneyflow_hsgt_daily_2018plus.parquet"),
            "promotion_approved": False,
        }
    top = load_glob("hsgt_top10")
    if len(top):
        top = top.copy()
        top["trade_date"] = top["trade_date"].astype(str).str.replace("-", "").str[:8]
        top["available_at"] = pd.to_datetime(top["trade_date"], format="%Y%m%d") + pd.Timedelta(hours=18)
        top["available_at_tz"] = "Asia/Shanghai"
        top["promotion_approved"] = False
        top = top.drop_duplicates(["trade_date", "ts_code", "market_type", "rank"], keep="last")
        top.to_parquet(odir / "hsgt_top10_daily_2018plus.parquet", index=False)
        summary["hsgt_top10"] = {
            "rows": int(len(top)),
            "days": int(top.trade_date.nunique()),
            "codes": int(top.ts_code.nunique()),
            "range": [str(top.trade_date.min()), str(top.trade_date.max())],
            "path": str(odir / "hsgt_top10_daily_2018plus.parquet"),
            "promotion_approved": False,
        }
    hk = load_glob("hk_hold")
    if len(hk):
        hk = hk.copy()
        hk["trade_date"] = hk["trade_date"].astype(str).str.replace("-", "").str[:8]
        # keep A-share only for northbound holding panel
        hk_a = hk[hk["ts_code"].astype(str).str.endswith((".SH", ".SZ"))].copy()
        hk_a["available_at"] = pd.to_datetime(hk_a["trade_date"], format="%Y%m%d") + pd.Timedelta(hours=18)
        hk_a["available_at_tz"] = "Asia/Shanghai"
        hk_a["promotion_approved"] = False
        hk_a = hk_a.drop_duplicates(["trade_date", "ts_code"], keep="last")
        hk_a.to_parquet(odir / "hk_hold_ashare_daily_2018plus.parquet", index=False)
        summary["hk_hold_ashare"] = {
            "rows": int(len(hk_a)),
            "days": int(hk_a.trade_date.nunique()),
            "codes": int(hk_a.ts_code.nunique()),
            "range": [str(hk_a.trade_date.min()), str(hk_a.trade_date.max())] if len(hk_a) else [None, None],
            "path": str(odir / "hk_hold_ashare_daily_2018plus.parquet"),
            "note": "filtered to .SH/.SZ; HK names dropped",
            "promotion_approved": False,
        }
    json.dump(summary, open(odir / "northbound_summary.json", "w"), ensure_ascii=False, indent=2, default=str)
    return summary

if __name__ == "__main__":
    import sys
    job = sys.argv[1] if len(sys.argv) > 1 else "all"
    out = {}
    if job in ("dragon", "all"):
        out["dragon_tiger"] = build_dragon_tiger()
    if job in ("anns", "all"):
        out["anns"] = build_anns()
    if job in ("margin", "all"):
        out["margin"] = build_margin()
    if job in ("northbound", "all"):
        out["northbound"] = build_northbound()
    print(json.dumps(out, ensure_ascii=False, indent=2, default=str)[:8000])
