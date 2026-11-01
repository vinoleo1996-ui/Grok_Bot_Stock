# 回执：block_trade 并行拉取 / stk_surv 追加 / hsgt top10 超时（2026-10-13 美东）

live=false，promotion_approved=false。未启 8787，未碰 moneyflow，未杀/重启 queue_chain_20261014.py(PID 4134298) 及 fill_hsgt_top10_extend.py(PID 4142128)。

## 1. block_trade 双源满窗（独立限速进程）
- 脚本：`scripts/acquire/block_trade_dual_standalone.py`（直接复用队列的 `block()`，逻辑一致）；PID 4151713；日志 `logs/acquire/block_trade_standalone_20261013.log`
- 范围 20180102→20261013 全部交易日；relay+datahub 各自按日落 `data/v2/tushare_raw/block_trade_dual/{relay,datahub}/YYYYMMDD.parquet`；每调用 sleep 0.3s；MemAvailable<2GB 暂停；按日文件断点续拉。
- 产物：`data/v2/events/block_trade_2018plus.parquet`（并集，键 ts_code/trade_date/price/vol/amount/buyer/seller，n_src/sources 列）、`block_trade_dual_diff_by_day.parquet`、`block_trade_2018plus_manifest.json`（含 SHA256、双源差异、fails）。available_at=次交易日 09:00。
- 完成标记：`output/markers/block_trade_2018plus.DONE`（n_fails<50 且 sha 一致才写）。再次运行脚本时直接 skip。
- **队列不重拉的保证**：运行中的队列已加载旧代码，改不了。但队列 `block()` 的 per_day 对已存在的日文件 `continue`，所以等队列跑到 block 步时日文件已齐，只会做零 API 调用的重合并（几十秒），产物内容一样。剩余风险：如果队列在本进程跑完前就到了 block 步（前面还有 g3/g0/nightly/etf），两者会交错拉同一批日期。每个日文件谁先写谁算，不会重复计数，最多有少量重复请求。

## 2. stk_surv（机构调研）
- 可得性：relay 和 datahub 都通（200），字段 ts_code,name,surv_date,fund_visitors,rece_place,rece_mode,rece_org,org_type,comp_rece。**只有调研日 surv_date，没有披露日。**
- 披露滞后核对：东财 RPT_ORG_SURVEYNEW 带 RECEIVE_START_DATE 和 NOTICE_DATE（约 28.8 万条）。随机抽 25 页×500 条，算交易日滞后的 p50/p90/p95/p99。
- available_at = surv_date 后第 max(2, ceil(p95)) 个交易日 09:00，分布写进 manifest 的 lag_sample。
- 脚本：`scripts/acquire/stk_surv_after_report_rc.py`；PID 4151714；日志 `logs/acquire/stk_surv_20261013.log`。它轮询 `output/remaining_queue_status.json`，等到 Q3_report_rc 的记录出现才开始，一次一个。之后队列只剩 incentive（东财轻量）和 g0b。
- 产物：`data/v2/events/stk_surv_2018plus.parquet` + manifest；标记 `output/markers/stk_surv_2018plus.DONE`；按日断点续拉。

## 3. hsgt top10 超时
- `scripts/acquire/fill_hsgt_top10_extend.py`（备份 `.bak_20261013`）：TSPRO_RELAY_TIMEOUT 默认改为 60s（原 180s），每次 relay 调用另加 120s 墙钟上限（线程 future），超时就抛异常，进入原有重试。只改了代码，当前 PID 4142128 不受影响，g3() 下一次重试时生效。
