# 业绩预告历史补数回执（研究级，promotion_approved=false）
生成：2026-10-18T00:56:49-04:00（ET）

- 需求：Intel 补 A 股业绩预告历史，公告日 2024-06-01 → 2025-10-12；实际窗口 **20240601 → 20251015**（多补 2025-10-13→10-15 三天：forecast_1y 是滚动一年窗口，现起点已到 20251016，不补合并表会留缺口；数据本身无问题）。
- 来源：tushare `forecast` 走 datahub；按公告日逐日（自然日 502 天）拉，limit=1000 翻页；不按报告期拉；空缓存一律重拉；原始缓存 `data/v2/tushare_raw/forecast/ann_YYYYMMDD.parquet`。
- 结果：`data/v2/events/forecast_2024h2_2025.parquet` 行数 **7040**，股票 3715，公告日 20240606→20251015；新拉 234 天、缓存 268 天、空 234 天、**失败 0 天**。sha256 `d6629a058f1b099bcab0a8e749a6fe47cc7638307883a435d71349eed44aa33a`。
- 合并：`data/v2/events/forecast_2024plus.parquet` = 本表 + `forecast_1y`（4359 行），按键 ['ts_code', 'ann_date', 'end_date', 'update_flag'] 去重（去掉 0 行），共 **11399** 行，公告日 20240606→20261016。sha256 `f1e59284c0a77eeca7eebb3005efce6c90d98639fb907b11dc2278ed9ad4a3e5`。
- 字段：ts_code, ann_date, end_date, type, p_change_min, p_change_max, net_profit_min, net_profit_max, last_parent_net, first_ann_date, summary, change_reason, update_flag（first_ann_date、summary 源头有则保留）+ available_at、availability_basis、source、quality_status、promotion_approved。
- available_at：公告日之后第一个 SSE 开市日 09:00 Asia/Shanghai（交易日历 `data/v2/calendar/trade_cal_sse_pit.parquet`）。⚠ 现有 `forecast_1y` 的 available_at 仍是公告日 18:00（上海），口径不同；合并表已统一为下一交易日 09:00，forecast_1y 本身未改。
- 月度行数：202406:27, 202407:1705, 202408:57, 202409:21, 202410:182, 202411:14, 202412:16, 202501:2881, 202502:18, 202503:61, 202504:271, 202505:12, 202506:22, 202507:1578, 202508:58, 202509:22, 202510:95
- manifest：`data/v2/events/forecast_2024h2_2025_manifest.json`、`data/v2/events/forecast_2024plus_manifest.json`。

## manifest 声明（Arch P1-5 / P3-1，Intel prereg §1、§9）
更新：2026-10-27T18:55:03+08:00（ET）

### forecast_1y（5481 行，sha256 `0be320b87dadb75a05de60b1dc4ca333a8cf5f1a630495f5693cef69d587e039`）
- ① availability_basis：`ann_date_1800_Asia/Shanghai`。合成时点：公告日当天 18:00（上海）。不是真实发布时间戳（数据源无公告时刻字段）。
- ② 首发快照：**否**。不是首发快照：这是 2026-10 从 datahub 回拉的数据商当前版本，无法证明数据商未回写覆盖修正前的值。按 Intel prereg §1.1，修正事件只作敏感性分析。 update_flag=1 共 198 行；first_ann_date≠ann_date 288 行；(ts_code,end_date) 5249 组，其中多行 226 组、多个公告日 226 组（涉及 458 行）；同 (ts_code,end_date,ann_date) 多行 0 组。
- ③ 已退市覆盖：含已退市股=True。窗口起点 20251028 之后退市 24 只，表中出现 19 只；窗口内（20251028→20261024）退市 24 只，出现 19 只。按公告日拉取，不按当前存续股票列表，故无幸存者过滤；未出现的退市股多为窗口内未发布业绩预告（预告非强制）。
- ④ 拉取方式：datahub forecast 按公告日逐日拉（自然日，含周末/节假日；2026-10-18 起，此前只拉开市日会漏周末公告），limit=1000 翻页，空缓存重拉；按日期拉，非按股票、非按报告期。

### forecast_2024h2_2025（7040 行，sha256 `d6629a058f1b099bcab0a8e749a6fe47cc7638307883a435d71349eed44aa33a`）
- ① availability_basis：`next_SSE_trading_day_after_ann_date_0900_Asia/Shanghai`。合成时点：公告日之后第一个 SSE 开市日 09:00（上海）。不是真实发布时间戳。
- ② 首发快照：**否**。不是首发快照：这是 2026-10 从 datahub 回拉的数据商当前版本，无法证明数据商未回写覆盖修正前的值。按 Intel prereg §1.1，修正事件只作敏感性分析。 update_flag=1 共 48 行；first_ann_date≠ann_date 118 行；(ts_code,end_date) 6941 组，其中多行 96 组、多个公告日 96 组（涉及 195 行）；同 (ts_code,end_date,ann_date) 多行 0 组。
- ③ 已退市覆盖：含已退市股=True。窗口起点 20240606 之后退市 91 只，表中出现 64 只；窗口内（20240606→20251015）退市 67 只，出现 40 只。按公告日拉取，不按当前存续股票列表，故无幸存者过滤；未出现的退市股多为窗口内未发布业绩预告（预告非强制）。
- ④ 拉取方式：datahub forecast 按公告日逐日拉（自然日，含周末/节假日），limit=1000 翻页，空缓存重拉；按日期拉，非按股票、非按报告期。

### forecast_2024plus（11399 行，sha256 `f1e59284c0a77eeca7eebb3005efce6c90d98639fb907b11dc2278ed9ad4a3e5`）
- ① availability_basis：`next_SSE_trading_day_after_ann_date_0900_Asia/Shanghai`。合成时点：公告日之后第一个 SSE 开市日 09:00（上海），合并时对 forecast_1y 段已统一重算；forecast_1y 原表仍为 ann_date 18:00。两者都不是真实发布时间戳。
- ② 首发快照：**否**。不是首发快照：这是 2026-10 从 datahub 回拉的数据商当前版本，无法证明数据商未回写覆盖修正前的值。按 Intel prereg §1.1，修正事件只作敏感性分析。 update_flag=1 共 236 行；first_ann_date≠ann_date 344 行；(ts_code,end_date) 11159 组，其中多行 235 组、多个公告日 235 组（涉及 475 行）；同 (ts_code,end_date,ann_date) 多行 0 组。
- ③ 已退市覆盖：含已退市股=True。窗口起点 20240606 之后退市 91 只，表中出现 64 只；窗口内（20240606→20261016）退市 91 只，出现 64 只。按公告日拉取，不按当前存续股票列表，故无幸存者过滤；未出现的退市股多为窗口内未发布业绩预告（预告非强制）。
- ④ 拉取方式：由 forecast_2024h2_2025 与 forecast_1y 合并，两段都按公告日（自然日）逐日拉；按键 (ts_code, ann_date, end_date, update_flag) 去重。

### ⑤ 重叠段（三表共用）
- 区间 20251016→20251116，独立重拉表 `data/v2/events/forecast_overlap_20251016_20251116.parquet`，报告 `docs/v2/DATA_FORECAST_OVERLAP_DIFF_ZH.md`，键 ['ts_code', 'ann_date', 'end_date', 'update_flag']。
- 与当前 forecast_1y：键一致率 0.923077，两边都有 48，仅重拉 4，仅 forecast_1y 0；共有键全字段一致率 1.0。
- 修复前（forecast_1y 只拉开市日）：键一致率 0.923077，仅重拉 4 条（均为周六公告），共有键全字段一致率 1.0。
