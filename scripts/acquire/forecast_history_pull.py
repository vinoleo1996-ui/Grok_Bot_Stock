#!/usr/bin/env python3
"""业绩预告历史补数 (Intel 需求, 2026-10-18): tushare forecast 走 datahub, 按公告日逐日(自然日)拉, limit=1000 翻页.
窗口 20240601 → 20251014 (覆盖 forecast_1y 滚动起点前的全部缺口). 空缓存一律重拉; 失败日不写缓存并列入 fails.
available_at = 公告日之后第一个 SSE 开市日 09:00 Asia/Shanghai.
产出: data/v2/events/forecast_2024h2_2025.parquet (+manifest), forecast_2024plus.parquet (与 forecast_1y 合并按键去重, +manifest),
回执 docs/v2/DATA_FORECAST_HISTORY_RECEIPT_ZH.md. promotion_approved=false. MemAvailable<2GB 暂停."""
import sys, os, time, json, hashlib, pathlib, datetime as dt
ROOT = pathlib.Path("/workspace/QuantLab"); sys.path.insert(0, str(ROOT))
import pandas as pd
from zoneinfo import ZoneInfo
from quantlab.data_sources.tushare_proxy import datahub, _to_df
SH = ZoneInfo("Asia/Shanghai"); ET = ZoneInfo("America/New_York")
START, END = os.environ.get("FC_START", "20240601"), os.environ.get("FC_END", "20251014")
CACHE = ROOT / "data/v2/tushare_raw/forecast"; CACHE.mkdir(parents=True, exist_ok=True)
EV = ROOT / "data/v2/events"; OUT = EV / "forecast_2024h2_2025.parquet"; MERGED = EV / "forecast_2024plus.parquet"
F1Y = EV / "forecast_1y.parquet"; RCPT = ROOT / "docs/v2/DATA_FORECAST_HISTORY_RECEIPT_ZH.md"
COLS = ["ts_code", "ann_date", "end_date", "type", "p_change_min", "p_change_max", "net_profit_min", "net_profit_max",
        "last_parent_net", "first_ann_date", "summary", "change_reason", "update_flag"]
KEY = ["ts_code", "ann_date", "end_date", "update_flag"]
LIM = 1000
def mem_wait():
    while True:
        m = next(int(l.split()[1]) for l in open("/proc/meminfo") if l.startswith("MemAvailable")) / 1e6
        if m >= 2.0: return
        print(f"MemAvailable {m:.2f}GB<2GB pause 60s", flush=True); time.sleep(60)
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
def fetch(d):
    out, off = [], 0
    while True:
        last = None
        for a in range(4):
            try:
                s, j = datahub("forecast", ann_date=d, limit=LIM, offset=off)
                if s == 200 and j.get("code") in (0, None) and "data" in j: break
                last = f"http {s} code {j.get('code')} {str(j.get('msg'))[:80]}"
            except Exception as e: last = str(e)[:120]
            time.sleep(2 * (a + 1))
        else:
            raise RuntimeError(last)
        x = _to_df(j); out.append(x)
        if len(x) < LIM: break
        off += LIM; time.sleep(0.2)
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()
def main():
    days = [d.strftime("%Y%m%d") for d in pd.date_range(START, END)]
    parts, fails, empty, fetched, cached = [], [], 0, 0, 0
    for i, d in enumerate(days, 1):
        c = CACHE / f"ann_{d}.parquet"
        x = None
        if c.exists() and c.stat().st_size > 0:
            x = pd.read_parquet(c)
            if len(x) == 0: c.unlink(); x = None   # 空缓存重拉
            else: cached += 1
        if x is None:
            mem_wait()
            try: x = fetch(d); fetched += 1
            except Exception as e: fails.append(f"{d}: {e}"); continue
            x.to_parquet(c, index=False); time.sleep(0.2)
        if len(x): parts.append(x)
        else: empty += 1
        if i % 50 == 0 or i == len(days):
            print(time.strftime("%H:%M:%S"), i, "/", len(days), "rows", sum(map(len, parts)), "empty", empty, "fail", len(fails), flush=True)
    if not parts:
        RCPT.write_text(f"# 业绩预告历史补数回执（阻塞）\n\n- 窗口 {START}→{END} 未拉到任何数据；fails={len(fails)}\n- 样例：{fails[:5]}\n"); print("NO DATA"); sys.exit(3)
    cal = pd.read_parquet(ROOT / "data/v2/calendar/trade_cal_sse_pit.parquet"); opn = sorted(cal[cal.is_open == 1].cal_date.astype(str))
    import bisect
    def avail(a):
        a = str(a)[:8]; k = bisect.bisect_right(opn, a)
        if k >= len(opn): return pd.NaT
        n = opn[k]; return pd.Timestamp(dt.datetime(int(n[:4]), int(n[4:6]), int(n[6:]), 9, 0, tzinfo=SH))
    def finish(df):
        for col in COLS:
            if col not in df.columns: df[col] = None
        df = df[COLS].copy()
        for col in ["ts_code", "ann_date", "end_date", "type", "first_ann_date", "summary", "change_reason", "update_flag"]:
            df[col] = df[col].where(df[col].isna(), df[col].astype(str))
        for col in ["p_change_min", "p_change_max", "net_profit_min", "net_profit_max", "last_parent_net"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df["available_at"] = df["ann_date"].map(avail)
        df["availability_basis"] = "next_SSE_trading_day_after_ann_date_0900_Asia/Shanghai"
        df["source"] = "tushare_datahub"; df["quality_status"] = "research_grade"; df["promotion_approved"] = False
        return df
    raw = pd.concat(parts, ignore_index=True)
    raw = raw[(raw.ann_date.astype(str) >= START) & (raw.ann_date.astype(str) <= END)]
    h = finish(raw).drop_duplicates(subset=COLS)
    n_exact = len(h); h = h.sort_values(KEY + ["first_ann_date"]).drop_duplicates(subset=KEY, keep="last").reset_index(drop=True)
    key_dups_h = n_exact - len(h)
    h.to_parquet(OUT, index=False)
    f1 = finish(pd.read_parquet(F1Y)) if F1Y.exists() else pd.DataFrame(columns=h.columns)
    m = pd.concat([h, f1], ignore_index=True)
    n_before = len(m); m = m.sort_values(KEY).drop_duplicates(subset=KEY, keep="last").reset_index(drop=True)
    m.to_parquet(MERGED, index=False)
    now = dt.datetime.now(ET).isoformat(timespec="seconds")
    def man(p, df, extra):
        d = dict(table=p.stem, path=str(p.relative_to(ROOT)), rows=len(df), n_ts_code=int(df.ts_code.nunique()),
                 ann_date_min=str(df.ann_date.min()), ann_date_max=str(df.ann_date.max()), columns=list(df.columns), key=KEY,
                 api="forecast", source_channel="datahub", pull="ann_date 逐日(自然日), limit=1000 翻页, 空缓存重拉",
                 availability_basis="next_SSE_trading_day_after_ann_date_0900_Asia/Shanghai", sha256=sha(p), bytes=p.stat().st_size,
                 created_at=now, promotion_approved=False, quality_status="research_grade", **extra)
        (p.parent / f"{p.stem}_manifest.json").write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n"); return d
    mh = man(OUT, h, dict(window_start=START, window_end=END, days_queried=len(days), fetched_days=fetched, cached_days=cached,
                          empty_days=empty, fail_days=len(fails), fails=fails[:50], key_dup_dropped=key_dups_h))
    mm = man(MERGED, m, dict(inputs=[mh["path"], str(F1Y.relative_to(ROOT))], forecast_1y_sha256=sha(F1Y) if F1Y.exists() else None,
                             rows_before_dedup=n_before, dedup_dropped=n_before - len(m),
                             note="forecast_1y 原 available_at=公告日18:00, 合并表统一重算为下一交易日09:00"))
    tc = h.groupby(h.ann_date.str[:6]).size()
    RCPT.write_text(f"""# 业绩预告历史补数回执（研究级，promotion_approved=false）
生成：{now}（ET）

- 需求：Intel 补 A 股业绩预告历史，公告日 2024-06-01 → 2025-10-12；实际窗口 **{START} → {END}**（多补 10-13/10-14 两天：forecast_1y 为滚动一年窗口，现起点已到 {f1.ann_date.min() if len(f1) else "NA"}，不补会留缺口）。
- 来源：tushare `forecast` 走 datahub；按公告日逐日（自然日 {len(days)} 天）拉，limit=1000 翻页；不按报告期拉；空缓存一律重拉；原始缓存 `data/v2/tushare_raw/forecast/ann_YYYYMMDD.parquet`。
- 结果：`{mh['path']}` 行数 **{len(h)}**，股票 {mh['n_ts_code']}，公告日 {mh['ann_date_min']}→{mh['ann_date_max']}；新拉 {fetched} 天、缓存 {cached} 天、空 {empty} 天、**失败 {len(fails)} 天**{('：' + '; '.join(fails[:10])) if fails else ''}。sha256 `{mh['sha256']}`。
- 合并：`{mm['path']}` = 本表 + `forecast_1y`（{len(f1)} 行），按键 {KEY} 去重（去掉 {n_before - len(m)} 行），共 **{len(m)}** 行，公告日 {mm['ann_date_min']}→{mm['ann_date_max']}。sha256 `{mm['sha256']}`。
- 字段：{', '.join(COLS)}（first_ann_date、summary 源头有则保留）+ available_at、availability_basis、source、quality_status、promotion_approved。
- available_at：公告日之后第一个 SSE 开市日 09:00 Asia/Shanghai（交易日历 `data/v2/calendar/trade_cal_sse_pit.parquet`）。⚠ 现有 `forecast_1y` 的 available_at 仍是公告日 18:00（上海），口径不同；合并表已统一为下一交易日 09:00，forecast_1y 本身未改。
- 月度行数：{', '.join(f'{k}:{v}' for k, v in tc.items())}
- manifest：`data/v2/events/forecast_2024h2_2025_manifest.json`、`data/v2/events/forecast_2024plus_manifest.json`。
""")
    print(json.dumps(dict(hist_rows=len(h), merged_rows=len(m), fails=len(fails), empty=empty, sha_hist=mh["sha256"], sha_merged=mm["sha256"]), ensure_ascii=False))
if __name__ == "__main__": main()
