# 不含北交所的下一张账：ST 与退市

核对日：2026-11-01。只读盘上 parquet 的 `ParquetFile.schema_arrow` 与 `metadata.num_rows`，没有整表进内存，没有改 parquet，没有调外部行情，没有跑账户，没有把晋升写成 true，没有新建 `delist_events_v1.parquet`。

下一张账指 `research/rd_ablation_20261101.py`。北交所代码序账已经停用；`stable_book` 在第 121 行抛 `ValueError`，不产出名单。

## 1. 每张表

行数来自 `metadata.num_rows`。列名来自 `schema_arrow`。

`data/local_market/1c85fd9aceaa03c3c4863bec/instruments.parquet` 在，6274 行。与本题有关的列：`is_st`（Arrow 类型 `null`，不是 bool）、`asset_type`（dictionary）、`active`（bool）。没有 `delist_date`。另有 `instrument_id`、`listing_date`、`available_at`、`state_basis`、`lifecycle_basis`。`is_st` 的物理类型是 null，不能当作已经接上的 ST 标记。

`data/v2/st_flags/is_st_daily_2018_2026.parquet` 在，320476 行。列只有 `instrument_id`、`trade_date`、`is_st_at_open`（bool）。

`data/v2/st_flags/st_intervals_tushare.parquet` 在，2716 行。列：`ts_code`、`name`、`start_date`、`end_date`、`ann_date`、`change_reason`、`instrument_id`、`quality_status`。

`data/v2/delisted/delisted_is_st_daily_from2015.parquet` 不在。

`data/v2/ref/stock_delisted.parquet` 在，339 行。退市相关列：`delist_date`、`instrument_id`、`last_trade_date`、`last_close`、`was_st_within_1y_of_delist`、`delist_reason_category`、`last_names`、`delisting_period_start`、`entered_delisting_period`、`delisting_period_trade_days`、`delist_price`、`delist_price_basis`、`available_at`。schema 里还有 `promotion_approved`，本轮没有读它的值。

`data/v2/ref/stock_delisted_v2.parquet` 在，339 行。上面 v1 那些列都在，另外有 `delist_period_start`、`delist_period_ann_date`、`entered_delisting_period_v2`、`face_value_delist_flag`、`delist_reason_category_v2`、`needs_manual_source`、`sd1_delist_type_default`。schema 里同样有 `promotion_approved`，本轮没有读它的值。

`data/v2/ref/delist_events_v1.parquet` 不在。本轮没有建这张表。

`data/v2/st_events/namechange_all.parquet` 在，12872 行。列：`ts_code`、`name`、`start_date`、`end_date`、`ann_date`、`change_reason`。

`data/v2/meta/stock_basic_incl_delisted.parquet` 在，5912 行。`list_status`、`delist_date`、`instrument_id`、`available_at` 都在。同表还有 `ts_code`、`name`、`list_date`、`exchange`。schema 里有 `promotion_approved`，本轮没有读它的值。

抽查三只 D0 面板的 schema（不是全目录普查）：`panels/sh.600000.parquet`、`panels/sz.000001.parquet`、`panels/bj.430047.parquet` 的列名里都有 `is_st_at_open`。这只说明这三只文件带该列。

## 2. 剔 ST：这条账现在读哪一列

`research/rd_ablation_20261101.py` 第 189–191 行只向 `instruments.parquet` 要 `instrument_id` 和 `asset_type`，并去掉 `sh.510300`。第 132 行行情列是 `event_time`、`open`、`close`、`volume`、`amount`、`turnover`。全文件没有 `is_st`、`delist`、`st_flag`，也没有 `bj.` 前缀判断。第 121 行的 `bj` 只出现在抛错文案里。第 30 行从 `d1_masks` 引进的是 `sw_l1_asof`，没有调用 `build_d1_masks_for_session`。

因此这条账现在不读任何 ST 列。已落地、列也齐、但没被这条账读的是：

- `data/v2/st_flags/is_st_daily_2018_2026.parquet` 的 `is_st_at_open`
- `data/v2/st_flags/st_intervals_tushare.parquet` 的 `instrument_id`、`start_date`、`end_date`、`ann_date`
- `instruments.parquet` 的 `is_st`（类型仍是 null）和 `active`

若改走 D1 掩码，`quantlab/universe/d1_masks.py` 第 420 行取的是合并后面板当日行的 `is_st_at_open`，第 438 行写成 `st_flag`：`pd.notna(is_st)` 为假时（列缺失、`None` 或 NaN）`st_flag = False`，也就是当成非 ST。第 529 行才用 `~st_flag` 丢掉 ST。同文件第 104–108 行只按 `asset_type` 留 `stock` 与 `equity_etf`，没有 `bj.` 前缀剔除，也不读 `instruments.is_st`、`active` 或上面两张 ST 表。

`quantlab/beta/smallcap_history_selector.py` 第 63–72 行的 `_st_sources` 会读区间表、`is_st_daily_2018_2026.parquet` 的 `is_st_at_open`，以及不在盘上的 `delisted_is_st_daily_from2015.parquet`。第 69 行没有 `exists` 判断，文件不在时读取会失败。消融脚本没有调用这个选择器。

## 3. 退市：哪个来源缺文件会失败

`quantlab/platform/delist_accounting.py` 第 41–43 行三个来源各绑一个文件，不按文件是否存在自动切换：

| 来源 | 文件 | 盘上 | 缺文件时 |
| --- | --- | --- | --- |
| `src_events_v1` | `data/v2/ref/delist_events_v1.parquet` | 不在 | 第 162–163 行 `FileNotFoundError` |
| `src_table_v2` | `data/v2/ref/stock_delisted_v2.parquet` | 在，339 行 | 同一处会失败；现在文件在 |
| `src_table_v1_d3rule` | `data/v2/ref/stock_delisted.parquet` | 在，339 行 | 同一处会失败；现在文件在 |

第 157–163 行写明：`source` 必须显式传入，文件不在就抛错，没有静默回退。现在只有 `src_events_v1` 会因为缺文件失败。不要新建 `delist_events_v1.parquet`。

`src_table_v2` 给 `_derive`（第 128–132、146、151 行）用的列都在 schema 里：`last_trade_date`、`delist_reason_category_v2`、`delist_period_start`、`entered_delisting_period_v2`、`face_value_delist_flag`、`needs_manual_source`、`ts_code`、`instrument_id`、`last_close`。

`src_table_v1_d3rule` 给 `_derive`（第 135–138、146、151 行）用的列都在 schema 里：`last_trade_date`、`delist_reason_category`、`delisting_period_start`、`entered_delisting_period`、`delisting_period_trade_days`、`ts_code`、`instrument_id`、`last_close`。v1 的面值重分类另读 `data/v2/delisted/delisted_daily_tushare.parquet`（第 45、103–104 行）。这张辅助表不在；缺了返回空集，不把 `load_delist_events` 打成失败。

`namechange_all.parquet` 在，且有第 119 行要的 `ts_code`、`name`、`start_date`、`ann_date`。它不是 `DELIST_SOURCES`。文件不在时第 117–118 行返回空字典，不失败。`data/v2/ref/delist_consideration.parquet` 不在；第 190 行有文件才合并，不在就跳过。

`stock_basic_incl_delisted.parquet` 的 `list_status`、`delist_date`、`instrument_id`、`available_at` 都在，但 `load_delist_events` 没有打开它。模块说明第 3 行提到 `stock_basic` 的 `delist_date` / `list_status=D`，源码里没有对应路径。`instruments.parquet` 也没有 `delist_date`。

这条消融账不在第 54–61 行的 `_ALLOWED_CALLERS` 里，也没有调用 `load_delist_events`。它第 26 行用的是 `quantlab.platform.execution.run_weight_schedule`。该函数第 623–625 行的参数里没有 `delist_events`。`execution.py` 第 180 行的 `bj.` 只决定手数，不是剔除，也不是退市。会计层那份带 `delist_events` 的 `run_weight_schedule` 在 `quantlab/platform/execution_sd1.py` 第 741–744 行，这条账没有走那里。研究脚本若直接调 `load_delist_events`，第 87 行会先抛 `StrategyLayerDelistAccess`，到不了缺文件那一行。

## 4. 结论

已落地、且对应读取函数要的列都在的，是 ST 日表、ST 区间表、`stock_delisted.parquet`、`stock_delisted_v2.parquet`、`namechange_all.parquet`，以及 `stock_basic_incl_delisted.parquet` 的四列。下一张消融账现在一列都没读。

能被这条账在现有代码里用到的 ST 列，只有在接上 `build_d1_masks_for_session` 之后的面板行 `is_st_at_open`。该列缺失时第 438 行当成非 ST。`instruments.is_st` 类型是 null，接不上。`delisted_is_st_daily_from2015.parquet` 与 `delist_events_v1.parquet` 都不在；后者缺了会让显式指定的 `src_events_v1` 失败，不要补建。v1/v2 退市表列齐，但这条账的执行函数不接收退市事件。同文件的 D1 掩码也不按 `bj.` 剔除。
