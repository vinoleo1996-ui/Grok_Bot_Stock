# 流通市值 available_at

选定方案：新文件，不覆盖 `float_mktcap_daily_tushare.parquet`，读取器也不把 `trade_date` 改名成 `available_at`。

新文件：`data/v2/float_mktcap/float_mktcap_daily_tushare_pit.parquet`

- `available_at` = `trade_date` 当天 18:00 Asia/Shanghai
- `revision` = `tushare_daily_basic_eod18_proxy`
- `quality_status` = `research`
- `promotion_approved` = false

这是收盘后可知的研究代理，不是交易所申报钟，也不能据此晋升。

用法：

- 收盘决策（本仓 `decision_time`，当日 18:00）可以看见当日这一行，因为 `available_at` 不晚于截止。
- 开盘决策只看见前一会话及更早的行。调用时传 `known_by="open"`。
- 原文件没有 `available_at`。把它直接交给 `float_mktcap_lookup_for_session` 仍然失败。
- 不传路径时默认读 `float_mktcap_daily_tushare_pit.parquet`。这张新表不在就 `FileNotFoundError`，不退回原表。
