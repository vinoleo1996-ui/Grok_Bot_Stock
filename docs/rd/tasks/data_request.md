# 需要你传达的数据

这次检出没有这些文件。代码不会生成它们。列名只写源码或 `quantlab/v2_schemas.py` 已经点名的字段。

- `data/v2/etf/etf_daily_adj.parquet`：`quantlab/portfolio/v2_multisleeve_book.py` 直接读取。调用方使用 `close` 或 `event_time`/`trade_date`。
- `data/v2/tushare_raw/trade_cal.parquet`：`quantlab/portfolio/trade_calendar.py` 第 12 行。列 `exchange`、`is_open`、`cal_date`。
- `data/local_market/1c85fd9aceaa03c3c4863bec/panels/<instrument_id>.parquet` 与同目录 `calendar.parquet`、`instruments.parquet`。面板需要 `event_time` 或日期索引，以及 `open`、`high`、`low`、`close`、`volume`、`amount`。
- `data/v2/asof_extend_tushare_202610/calendar.parquet`，没有则回退 `data/v2/asof_extend_202610/calendar.parquet`。日期列用 `session`、`cal_date`、`trade_date` 或 `event_time` 之一。`manifest.json` 可带 `d0_as_of`，没有则用文档里的 2026-06-30。
- `data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet`：`instrument_id`、`sw_code`、`sw_name`、`in_date`、`out_date`、`available_at`。`available_at` 不允许整列为空。
- `data/v2/financials_pit/financials_pit_tushare.parquet`：`instrument_id`、`metric`、`value`、`available_at`。
- `data/v2/ep/ep_pit_daily_tushare.parquet`：`instrument_id`、`ep`、`available_at`。上海日期不早于决策日的行会被丢掉。
- `data/v2/float_mktcap/float_mktcap_daily_tushare.parquet`：`instrument_id`、`float_mktcap`、`available_at`。文件不在时 D1 得到空查找并注明缺失，不用面板反推去冒充这张表。
- `output/d1/ENG_PING_PATHS.json` 只记录数据验收。它不能把 `strategy_promotion_approved` 设成 true。
