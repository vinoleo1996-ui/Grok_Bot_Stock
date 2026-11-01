# 回执：个股退市表（给 Arch/Eng，审计 #12）
2026-10-14 06:56 ET，Data。promotion_approved=false。
- 文件：`data/v2/ref/stock_delisted.parquet`，339 行，sha256 `90c8934dddc698f46075a20fe3d60309094919868c5e3a4bacc4d12c765f0603`。
- 来源：datahub `stock_basic list_status=D`（今日 1 次请求，339 只，与本地 delisted_master 一致）+ 本地 `data/v2/delisted/` 日线 + `st_events/namechange_all`。
- 字段：ts_code、instrument_id、name、list_date、delist_date（退市日）、last_trade_date（最后交易日）、delist_price / last_close（最后交易日不复权收盘价）、last_adj_factor、entered_delisting_period、delisting_period_start、delisting_period_trade_days、was_st_within_1y_of_delist、delist_reason_category、gap_days_last_trade_to_delist。
- 退市日范围 19990712→20260730；338 只有最后交易日（1 只无日线）；**89 只进入过退市整理期**（判定：曾用名以「退」结尾）。
- 局限：Tushare 无独立“退市价”字段，delist_price 用最后交易日收盘；整理期判定依赖改名记录，早年无「退」字简称的整理期会漏判；吸收合并退市的换股价未纳入。
