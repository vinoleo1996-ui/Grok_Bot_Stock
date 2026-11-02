# 需要你传达的数据

行情 parquet 在 git 忽略的 `data/` 或 Release 里，不进 git。代码不生成它们，也不调用外部行情接口。列名只写源码或 `quantlab/v2_schemas.py` 已经点名的字段。

- `data/v2/etf/etf_daily_adj.parquet`：`quantlab/portfolio/v2_multisleeve_book.py` 直接读取 `close` / `close_hfq`。研究用的 510300 条把 `vol` 当作手数 `volume`，把 `amount` 从千元换成元，并按 `trade_date` 生成 `event_time`。原文件不改。没有 D0 面板的场内基金改读这张表。
- `data/v2/tushare_raw/trade_cal.parquet`：`quantlab/portfolio/trade_calendar.py` 第 12 行。列 `exchange`、`is_open`、`cal_date`。
- `data/local_market/1c85fd9aceaa03c3c4863bec/panels/<instrument_id>.parquet` 与同目录 `calendar.parquet`、`instruments.parquet`。面板需要 `event_time` 或日期索引，以及 `open`、`high`、`low`、`close`、`volume`、`amount`。
- `data/v2/asof_extend_tushare_202610/calendar.parquet`，没有则回退 `data/v2/asof_extend_202610/calendar.parquet`。日期列用 `session`、`cal_date`、`trade_date` 或 `event_time` 之一。`manifest.json` 可带 `d0_as_of`，没有则用文档里的 2026-06-30。
- `data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet`：`instrument_id`、`sw_code`、`sw_name`、`in_date`、`out_date`、`available_at`。`available_at` 不允许整列为空。
- `data/v2/financials_pit/financials_pit_tushare.parquet`：宽表，有 `instrument_id`、`available_at`、`net_profit` 等列，没有 `metric`/`value` 长表。`financials_metric_asof` 按列名读取，并保留该日之前最后一条。
- `data/v2/ep/ep_pit_daily_tushare.parquet`：公布列是 `e_available_at`。读取时在内存里当作 `available_at`，不改原文件。上海日期不早于决策日的行会被丢掉。
- `data/v2/float_mktcap/float_mktcap_daily_tushare.parquet`：原表有 `instrument_id`、`float_mktcap`、`trade_date`，没有 `available_at`。研究代理在另一张 `float_mktcap_daily_tushare_pit.parquet`，规则见 `docs/rd/tasks/float_mktcap_pit_20261101.md`。原表缺列时读取仍失败。
- 分红默认读 `data/v2/corporate_actions/dividend_tushare.parquet`，按除息日的伴随表是同目录 `dividend_by_exdate_tushare.parquet`。`ts_code` 在内存里变成 `instrument_id`。没有 `data/v2/dividends/dividends.parquet` 也不再当作默认路径。
- `data/v2/asof_extend_tushare_202610` 没有日历时，读取器改读同级 `asof_extend_202610/calendar.parquet`。
- 事件样本路径仍是 `data/v2/free_hunt/fundamentals/cninfo_periodic_announcements_sample.parquet`。落地列是 `instrument_id` 和 `announcement_time`，没有 `available_at`、`event_type`、`polarity`。读取时在内存里对上：时钟用公告时间，类型标成未分类的定期报告，极性为 0。原文件不改。没有公告时钟的表仍然失败。
- `output/d1/ENG_PING_PATHS.json` 只记录数据验收。它不能把 `strategy_promotion_approved` 设成 true。
- `data/v2/tushare_raw/stock_basic/` 的 `L.parquet`、`D.parquet`、`P.parquet`，以及 `data/v2/meta/stock_basic_incl_delisted.parquet`，都在全量包里。列包括 `ts_code`、`name`、`list_status`、`list_date`、`delist_date`。含退市的那张还有 `instrument_id` 和 `available_at`。没有改 `instruments.parquet`，也没有调用外部股票列表接口。
- `data/v2/ref/delist_events_v1.parquet` 不在全量包里。退市账用 `data/v2/ref/stock_delisted.parquet` 或 `stock_delisted_v2.parquet`，调用时必须显式指定来源。
