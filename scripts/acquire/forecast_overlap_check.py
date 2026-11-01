#!/usr/bin/env python3
"""业绩预告重叠段核对 (Arch P3-1 / Intel prereg §1): 独立重拉 20251016→20251116 (datahub forecast, 按公告日自然日逐日, limit=1000, 不用旧缓存),
与 forecast_1y 按键 (ts_code, ann_date, end_date, update_flag) 逐字段比对. 产出:
 data/v2/events/forecast_overlap_20251016_20251116.parquet (+manifest), docs/v2/DATA_FORECAST_OVERLAP_DIFF_ZH.md, output/forecast_overlap_diff.json"""
import sys, os, json, time, pathlib, datetime as dt
ROOT = pathlib.Path("/workspace/QuantLab"); sys.path.insert(0, str(ROOT / "scripts/acquire")); sys.path.insert(0, str(ROOT))
import pandas as pd, numpy as np
import forecast_history_pull as fh
S, E = os.environ.get("OV_START", "20251016"), os.environ.get("OV_END", "20251116")
CACHE = ROOT / "data/v2/tushare_raw/forecast_overlap_recheck"; CACHE.mkdir(parents=True, exist_ok=True)
OUT = ROOT / "data/v2/events/forecast_overlap_20251016_20251116.parquet"; REP = ROOT / "docs/v2/DATA_FORECAST_OVERLAP_DIFF_ZH.md"
JS = ROOT / "output/forecast_overlap_diff.json"; F1Y = ROOT / "data/v2/events/forecast_1y.parquet"
KEY = fh.KEY; CMP = [c for c in fh.COLS if c not in KEY]
def main():
    days = [d.strftime("%Y%m%d") for d in pd.date_range(S, E)]; parts, fails = [], []
    for d in days:
        c = CACHE / f"ann_{d}.parquet"
        fh.mem_wait()
        try: x = fh.fetch(d)
        except Exception as e: fails.append(f"{d}: {e}"); continue
        x.to_parquet(c, index=False); parts.append(x); time.sleep(0.2)
    raw = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=fh.COLS)
    for col in fh.COLS:
        if col not in raw.columns: raw[col] = None
    o = raw[fh.COLS].copy()
    for col in ["ts_code", "ann_date", "end_date", "type", "first_ann_date", "summary", "change_reason", "update_flag"]:
        o[col] = o[col].where(o[col].isna(), o[col].astype(str))
    for col in ["p_change_min", "p_change_max", "net_profit_min", "net_profit_max", "last_parent_net"]: o[col] = pd.to_numeric(o[col], errors="coerce")
    o = o[(o.ann_date >= S) & (o.ann_date <= E)].drop_duplicates()
    o.to_parquet(OUT, index=False)
    f = pd.read_parquet(F1Y); f = f[(f.ann_date >= S) & (f.ann_date <= E)][fh.COLS]
    ko = o.drop_duplicates(KEY, keep="last"); kf = f.drop_duplicates(KEY, keep="last")
    m = ko.merge(kf, on=KEY, how="outer", suffixes=("_new", "_1y"), indicator=True)
    both = m[m._merge == "both"]; only_new = m[m._merge == "left_only"]; only_1y = m[m._merge == "right_only"]
    diff = {}
    for c in CMP:
        a, b = both[f"{c}_new"], both[f"{c}_1y"]
        if c in ("p_change_min", "p_change_max", "net_profit_min", "net_profit_max", "last_parent_net"):
            eq = (a.isna() & b.isna()) | np.isclose(a.astype(float), b.astype(float), rtol=1e-9, atol=1e-6, equal_nan=False)
        else:
            eq = (a.isna() & b.isna()) | (a.astype(str) == b.astype(str))
        diff[c] = int((~eq).sum())
    any_diff = pd.Series(False, index=both.index)
    for c in CMP:
        a, b = both[f"{c}_new"], both[f"{c}_1y"]
        any_diff |= ~((a.isna() & b.isna()) | (a.astype(str) == b.astype(str)) | (pd.to_numeric(a, errors="coerce").sub(pd.to_numeric(b, errors="coerce")).abs() < 1e-6))
    ex = both[any_diff].head(10)
    res = dict(window=[S, E], days_queried=len(days), fail_days=len(fails), fails=fails, rows_recheck=len(o), rows_forecast_1y=len(f),
               keys_recheck=len(ko), keys_forecast_1y=len(kf), keys_both=len(both), keys_only_recheck=len(only_new), keys_only_forecast_1y=len(only_1y),
               key_match_rate=round(len(both) / max(1, len(set(map(tuple, ko[KEY].values)) | set(map(tuple, kf[KEY].values)))), 6),
               rows_all_fields_equal=int((~any_diff).sum()), field_agreement_rate=round(float((~any_diff).mean()) if len(both) else float("nan"), 6),
               field_diff_counts=diff, key=KEY, compared_fields=CMP,
               forecast_1y_sha256=fh.sha(F1Y), recheck_sha256=fh.sha(OUT), generated_at=dt.datetime.now().astimezone().isoformat(timespec="seconds"))
    JS.write_text(json.dumps(res, ensure_ascii=False, indent=2))
    (OUT.parent / f"{OUT.stem}_manifest.json").write_text(json.dumps(dict(table=OUT.stem, path=str(OUT.relative_to(ROOT)), rows=len(o), n_ts_code=int(o.ts_code.nunique()) if len(o) else 0,
        ann_date_min=o.ann_date.min() if len(o) else None, ann_date_max=o.ann_date.max() if len(o) else None, api="forecast", source_channel="datahub",
        pull="ann_date 逐日(自然日), limit=1000 翻页, 独立重拉不复用旧缓存", purpose="与 forecast_1y 重叠段对比 (Arch P3-1)", fail_days=len(fails),
        sha256=res["recheck_sha256"], created_at=res["generated_at"], promotion_approved=False), ensure_ascii=False, indent=2) + "\n")
    lines = [f"| {k[0]} | {k[1]} | {k[2]} | {k[3]} | " + "; ".join(f"{c}: {r[c+'_new']!r}→1y {r[c+'_1y']!r}"[:120] for c in CMP if str(r[c+'_new']) != str(r[c+'_1y'])) + " |"
             for k, r in zip(ex[KEY].values, ex.to_dict("records"))]
    REP.write_text(f"""# 业绩预告重叠段差异报告（Arch P3-1，研究级，promotion_approved=false）
生成：{res['generated_at']}（ET）

- 重叠段：公告日 **{S} → {E}**（自然日 {len(days)} 天）。datahub `forecast` 按公告日逐日独立重拉（limit=1000，不复用旧缓存），失败 {len(fails)} 天。
- 对比对象：`data/v2/events/forecast_1y.parquet` 同区间（sha256 `{res['forecast_1y_sha256']}`）；重拉表 `{OUT.relative_to(ROOT)}`（sha256 `{res['recheck_sha256']}`）。
- 键：{KEY}；比较字段：{', '.join(CMP)}。
- 行数：重拉 {len(o)}，forecast_1y {len(f)}；键：重拉 {len(ko)}，forecast_1y {len(kf)}，**两边都有 {len(both)}**，仅重拉 {len(only_new)}，仅 forecast_1y {len(only_1y)}；键一致率 **{res['key_match_rate']:.2%}**。
- 两边都有的键中，全部字段一致 {res['rows_all_fields_equal']} / {len(both)}（**{res['field_agreement_rate']:.2%}**）。
- 各字段不一致条数：{', '.join(f'{k}={v}' for k, v in diff.items())}。
- 说明：两次都是「现在回拉」的数据商当前版本，一致只能说明两次拉取口径稳定，不能证明是首发快照。

## 不一致样例（最多 10 条）
| ts_code | ann_date | end_date | update_flag | 差异 |
|---|---|---|---|---|
{chr(10).join(lines) if lines else '| — | — | — | — | 无 |'}
""")
    print(json.dumps({k: res[k] for k in ["rows_recheck", "rows_forecast_1y", "keys_both", "keys_only_recheck", "keys_only_forecast_1y", "key_match_rate", "field_agreement_rate", "field_diff_counts", "fail_days"]}, ensure_ascii=False))
if __name__ == "__main__": main()
