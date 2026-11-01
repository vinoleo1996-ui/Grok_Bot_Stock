"""EastMoney stockrank + guba hotspot pilot for CSI300 (Xueqiu WAF alternate).
Research-only. available_at = capture day 15:00 Asia/Shanghai + first_captured_at=now.
No historical PIT claim for rank boards.
"""
import json, pathlib, datetime as dt, hashlib
import requests, pandas as pd

ROOT = pathlib.Path("/workspace/QuantLab")
OUT = ROOT / "data/v2/text/em_heat"
OUT.mkdir(parents=True, exist_ok=True)
H = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.eastmoney.com/",
    "Content-Type": "application/json",
}
TZ = "Asia/Shanghai"

def csi300():
    iw = ROOT / "data/v2/tushare_raw/index_weight"
    files = sorted(iw.glob("000300_SH_*.parquet"), reverse=True)
    for f in files:
        d = pd.read_parquet(f)
        if len(d) == 0:
            continue
        col = "con_code" if "con_code" in d.columns else "ts_code"
        return sorted(d[col].astype(str).unique()), f.stem
    # fallback xueqiu members file
    alt = ROOT / "data/v2/text/xueqiu/csi300_members_latest.parquet"
    if alt.exists():
        d = pd.read_parquet(alt)
        c = "ts_code" if "ts_code" in d.columns else d.columns[0]
        return sorted(d[c].astype(str).unique()), "xueqiu_fallback"
    return [], "none"

def main():
    members, src = csi300()
    now = dt.datetime.now().astimezone()
    avail = now.astimezone(dt.timezone(dt.timedelta(hours=8))).replace(hour=15, minute=0, second=0, microsecond=0)
    if now.astimezone(dt.timezone(dt.timedelta(hours=8))).hour < 15:
        avail = avail - dt.timedelta(days=1)

    # full market rank page (then filter CSI300)
    rows = []
    page = 1
    while page <= 20:
        r = requests.post(
            "https://emappdata.eastmoney.com/stockrank/getAllCurrentList",
            headers=H,
            json={"appId": "appId01", "globalId": "786e4c21-70dc-435a-93bb-38", "pageNo": page, "pageSize": 100},
            timeout=20,
        )
        j = r.json()
        data = j.get("data") or []
        if not data:
            break
        for x in data:
            rows.append(x)
        if len(data) < 100:
            break
        page += 1

    df = pd.DataFrame(rows)
    (OUT / "stockrank_raw_sample.json").write_text(json.dumps({"n": len(df), "cols": list(df.columns), "sample": rows[:2]}, ensure_ascii=False, indent=2, default=str))
    if len(df) == 0:
        (OUT / "PILOT.md").write_text("# EM heat pilot\n\nstockrank empty\n")
        print("EMPTY", flush=True)
        return 1

    # normalize code
    code_col = next((c for c in ("sc", "srcSecurityCode", "securityCode", "code", "SECURITY_CODE") if c in df.columns), None)
    if code_col is None:
        # try nested
        print("cols", list(df.columns), flush=True)
        (OUT / "PILOT.md").write_text(f"# EM heat pilot\n\nunknown cols: {list(df.columns)}\n")
        return 2

    def to_ts(c):
        c = str(c).strip()
        if "." in c:
            return c
        if c.startswith("SH") or c.startswith("SZ") or c.startswith("BJ"):
            return c[2:] + "." + c[:2]
        if c.startswith("6") or c.startswith("9"):
            return c + ".SH"
        if c.startswith("0") or c.startswith("3"):
            return c + ".SZ"
        if c.startswith("4") or c.startswith("8"):
            return c + ".BJ"
        return c

    df["ts_code"] = df[code_col].map(to_ts)
    memset = set(members)
    hit = df[df.ts_code.isin(memset)].copy() if memset else df.copy()
    hit["rank_page_src"] = "em_stockrank_getAllCurrentList"
    hit["available_at"] = avail.isoformat()
    hit["first_captured_at"] = now.isoformat()
    hit["promotion_approved"] = False
    hit["universe"] = "CSI300" if memset else "ALL_RANK"
    hit["member_src"] = src
    path = OUT / "csi300_stockrank_snapshot_pit.parquet"
    hit.to_parquet(path, index=False)

    # guba homepage list (market-level hot topics, not per-stock)
    try:
        gr = requests.get(
            "https://guba.eastmoney.com/interface/GetData.aspx?path=newtopic/api/Topic/HomePageListRead&ps=50&p=1&type=0",
            headers={"User-Agent": "Mozilla/5.0", "Referer": "https://guba.eastmoney.com/"},
            timeout=20,
        )
        gj = gr.json()
        topics = gj.get("re") or []
        tdf = pd.DataFrame(topics)
        tdf["available_at"] = avail.isoformat()
        tdf["first_captured_at"] = now.isoformat()
        tdf["promotion_approved"] = False
        tdf["source"] = "em_guba_HomePageListRead"
        tpath = OUT / "guba_hot_topics_snapshot_pit.parquet"
        tdf.to_parquet(tpath, index=False)
        tn = len(tdf)
    except Exception as e:
        tn = 0
        tpath = None
        topics_err = str(e)

    md = f"""# 东财热度试点（雪球 WAF 替代）

> 研究级 · **未改** promotion_approved_overall · 无历史 PIT 宣称

| 项 | 值 |
|---|---|
| stockrank 全表页拉取 | {len(df)} 行 |
| CSI300 命中 | {len(hit)} / {len(members)} |
| 成分来源 | `{src}` |
| 路径 | `{path}` |
| available_at | {avail.isoformat()}（抓取日 15:00 +08；榜单无史） |
| first_captured_at | {now.isoformat()} |
| guba 热帖首页 | {tn} 条 → `{tpath}` |

## 局限

- 人气榜/股吧热帖为**当日快照**，不能回填历史；回测只能从首次抓取日起 forward。
- 雪球讨论仍 WAF；本试点不绕雪球。
- `getCurrentList` 需单票代码，全 CSI300 逐票需另限速任务。

**End.**
"""
    (OUT / "PILOT.md").write_text(md)
    (ROOT / "output/d1/EM_HEAT_CSI300_PILOT.md").write_text(md)
    print(json.dumps({"rank_rows": len(df), "csi_hit": len(hit), "members": len(members), "guba": tn, "path": str(path)}, ensure_ascii=False), flush=True)

if __name__ == "__main__":
    main()
