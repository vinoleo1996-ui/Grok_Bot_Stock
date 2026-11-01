#!/usr/bin/env python3
"""业绩预告 manifest 声明 (Arch P1-5 / Intel prereg §1、§9): 给 forecast_1y、forecast_2024h2_2025、forecast_2024plus 三份 manifest
写入 ① availability_basis ② 是否首发快照(+修正统计) ③ 已退市覆盖 ④ 拉取方式 ⑤ 重叠段, 并刷新 sha256; 同步写入回执的「manifest 声明」一节.
幂等; nightly events 步之后自动跑 (forecast_1y 每晚重写 manifest)."""
import json, pathlib, re, datetime as dt
import pandas as pd
ROOT = pathlib.Path("/workspace/QuantLab"); EV = ROOT / "data/v2/events"; RCPT = ROOT / "docs/v2/DATA_FORECAST_HISTORY_RECEIPT_ZH.md"
DL = ROOT / "data/v2/ref/stock_delisted.parquet"; OVJ = ROOT / "output/forecast_overlap_diff.json"; OVJ0 = ROOT / "output/forecast_overlap_diff_before_naturalday_fix.json"
def sha(p):
    import hashlib; h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
BASIS = {
 "forecast_1y": ("ann_date_1800_Asia/Shanghai", "合成时点：公告日当天 18:00（上海）。不是真实发布时间戳（数据源无公告时刻字段）。"),
 "forecast_2024h2_2025": ("next_SSE_trading_day_after_ann_date_0900_Asia/Shanghai", "合成时点：公告日之后第一个 SSE 开市日 09:00（上海）。不是真实发布时间戳。"),
 "forecast_2024plus": ("next_SSE_trading_day_after_ann_date_0900_Asia/Shanghai", "合成时点：公告日之后第一个 SSE 开市日 09:00（上海），合并时对 forecast_1y 段已统一重算；forecast_1y 原表仍为 ann_date 18:00。两者都不是真实发布时间戳。"),
}
PULL = {
 "forecast_1y": "datahub forecast 按公告日逐日拉（自然日，含周末/节假日；2026-10-18 起，此前只拉开市日会漏周末公告），limit=1000 翻页，空缓存重拉；按日期拉，非按股票、非按报告期。",
 "forecast_2024h2_2025": "datahub forecast 按公告日逐日拉（自然日，含周末/节假日），limit=1000 翻页，空缓存重拉；按日期拉，非按股票、非按报告期。",
 "forecast_2024plus": "由 forecast_2024h2_2025 与 forecast_1y 合并，两段都按公告日（自然日）逐日拉；按键 (ts_code, ann_date, end_date, update_flag) 去重。",
}
def stats(name, df):
    dl = pd.read_parquet(DL)[["ts_code", "delist_date"]].dropna(); dl["delist_date"] = dl.delist_date.astype(str)
    a0, a1 = str(df.ann_date.min()), str(df.ann_date.max())
    in_win = dl[dl.delist_date >= a0]   # 窗口起点之后（含窗口内及之后）退市的股票
    present = sorted(set(in_win.ts_code) & set(df.ts_code))
    present_in = sorted(set(dl[(dl.delist_date >= a0) & (dl.delist_date <= a1)].ts_code) & set(df.ts_code))
    any_dl = sorted(set(dl.ts_code) & set(df.ts_code))
    uf = df.update_flag.astype(str)
    fa = df.first_ann_date.astype(str)
    g = df.groupby(["ts_code", "end_date"])
    nver = g.ann_date.nunique(); nrows = g.size()
    same_day = df.groupby(["ts_code", "end_date", "ann_date"]).size()
    return dict(
        first_release_snapshot=False,
        first_release_snapshot_note="不是首发快照：这是 2026-10 从 datahub 回拉的数据商当前版本，无法证明数据商未回写覆盖修正前的值。按 Intel prereg §1.1，修正事件只作敏感性分析。",
        revision_stats=dict(rows=len(df), update_flag_1_rows=int((uf == "1").sum()), update_flag_values={k: int(v) for k, v in uf.value_counts().items()},
            first_ann_date_ne_ann_date_rows=int(((fa != df.ann_date.astype(str)) & fa.ne("None") & fa.ne("nan")).sum()),
            first_ann_date_null_rows=int((fa.isin(["None", "nan"]) | df.first_ann_date.isna()).sum()),
            ts_end_groups=int(len(nrows)), ts_end_groups_multi_rows=int((nrows > 1).sum()), ts_end_groups_multi_ann_dates=int((nver > 1).sum()),
            rows_in_multi_version_groups=int(nrows[nrows > 1].sum()), same_ts_end_ann_multi_rows_groups=int((same_day > 1).sum())),
        delisted_coverage=dict(includes_delisted=bool(present), ref=str(DL.relative_to(ROOT)), window_ann_date=[a0, a1],
            delisted_since_window_start_total=int(in_win.ts_code.nunique()), delisted_since_window_start_present=len(present),
            delisted_within_window_total=int(dl[(dl.delist_date >= a0) & (dl.delist_date <= a1)].ts_code.nunique()), delisted_within_window_present=len(present_in),
            any_delisted_ever_present=len(any_dl), examples=present[:15],
            note="按公告日拉取，不按当前存续股票列表，故无幸存者过滤；未出现的退市股多为窗口内未发布业绩预告（预告非强制）。"),
    )
def overlap():
    o = json.loads(OVJ.read_text()) if OVJ.exists() else None
    o0 = json.loads(OVJ0.read_text()) if OVJ0.exists() else None
    keep = ["window", "rows_recheck", "rows_forecast_1y", "keys_both", "keys_only_recheck", "keys_only_forecast_1y", "key_match_rate", "field_agreement_rate", "field_diff_counts", "fail_days", "generated_at"]
    return dict(window=(o or {}).get("window", ["20251016", "20251116"]), recheck_table="data/v2/events/forecast_overlap_20251016_20251116.parquet",
                report="docs/v2/DATA_FORECAST_OVERLAP_DIFF_ZH.md", key=["ts_code", "ann_date", "end_date", "update_flag"],
                result=({k: o.get(k) for k in keep} if o else None), before_naturalday_fix=({k: o0.get(k) for k in keep} if o0 else None))
def main():
    out = {}
    for name in ["forecast_1y", "forecast_2024h2_2025", "forecast_2024plus"]:
        p = EV / f"{name}.parquet"; mp = EV / f"{name}_manifest.json"
        if not p.exists(): continue
        df = pd.read_parquet(p); m = json.loads(mp.read_text()) if mp.exists() else dict(table=name)
        b, bn = BASIS[name]
        m.update(availability_basis=b, availability_basis_note=bn, availability_is_synthetic=True, pull_method=PULL[name], pull_by="ann_date_natural_day",
                 overlap_segment=overlap(), sha256=sha(p), bytes=p.stat().st_size, rows=len(df), **stats(name, df),
                 declarations_updated_at=dt.datetime.now().astimezone().isoformat(timespec="seconds"), promotion_approved=False)
        mp.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n"); out[name] = m
    if RCPT.exists() and out:
        L = ["## manifest 声明（Arch P1-5 / P3-1，Intel prereg §1、§9）", f"更新：{dt.datetime.now().astimezone().isoformat(timespec='seconds')}（ET）", ""]
        for n, m in out.items():
            r, d = m["revision_stats"], m["delisted_coverage"]
            L += [f"### {n}（{m['rows']} 行，sha256 `{m['sha256']}`）",
                  f"- ① availability_basis：`{m['availability_basis']}`。{m['availability_basis_note']}",
                  f"- ② 首发快照：**否**。{m['first_release_snapshot_note']} update_flag=1 共 {r['update_flag_1_rows']} 行；first_ann_date≠ann_date {r['first_ann_date_ne_ann_date_rows']} 行；(ts_code,end_date) {r['ts_end_groups']} 组，其中多行 {r['ts_end_groups_multi_rows']} 组、多个公告日 {r['ts_end_groups_multi_ann_dates']} 组（涉及 {r['rows_in_multi_version_groups']} 行）；同 (ts_code,end_date,ann_date) 多行 {r['same_ts_end_ann_multi_rows_groups']} 组。",
                  f"- ③ 已退市覆盖：含已退市股={d['includes_delisted']}。窗口起点 {d['window_ann_date'][0]} 之后退市 {d['delisted_since_window_start_total']} 只，表中出现 {d['delisted_since_window_start_present']} 只；窗口内（{d['window_ann_date'][0]}→{d['window_ann_date'][1]}）退市 {d['delisted_within_window_total']} 只，出现 {d['delisted_within_window_present']} 只。{d['note']}",
                  f"- ④ 拉取方式：{m['pull_method']}",
                  ""]
        ov = overlap(); r = ov["result"] or {}; r0 = ov["before_naturalday_fix"] or {}
        L += [f"### ⑤ 重叠段（三表共用）", f"- 区间 {ov['window'][0]}→{ov['window'][1]}，独立重拉表 `{ov['recheck_table']}`，报告 `{ov['report']}`，键 {ov['key']}。",
              f"- 与当前 forecast_1y：键一致率 {r.get('key_match_rate')}，两边都有 {r.get('keys_both')}，仅重拉 {r.get('keys_only_recheck')}，仅 forecast_1y {r.get('keys_only_forecast_1y')}；共有键全字段一致率 {r.get('field_agreement_rate')}。",
              f"- 修复前（forecast_1y 只拉开市日）：键一致率 {r0.get('key_match_rate')}，仅重拉 {r0.get('keys_only_recheck')} 条（均为周六公告），共有键全字段一致率 {r0.get('field_agreement_rate')}。" if r0 else "", ""]
        t = RCPT.read_text(); t = re.split(r"\n## manifest 声明", t)[0].rstrip() + "\n\n" + "\n".join(L)
        RCPT.write_text(t)
    print(json.dumps({n: dict(rows=m["rows"], sha=m["sha256"][:12], rev=m["revision_stats"], dl={k: m["delisted_coverage"][k] for k in ["delisted_since_window_start_total", "delisted_since_window_start_present", "delisted_within_window_total", "delisted_within_window_present"]}) for n, m in out.items()}, ensure_ascii=False, indent=1))
if __name__ == "__main__": main()
