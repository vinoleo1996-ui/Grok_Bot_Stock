# SD1 execute 申请前置说明（B 的四项）
- 时间：2026-10-18 02:19 EDT；执行人：QuantLab Data。
- 范围：只读了代码、ps、文件列表与 mtime、nightly 的 summary/log、补拉队列状态文件。没有读数据内容，没有杀进程，没有改代码。

## ① nightly tier3 写哪些路径
- scripts/nightly_update.py 第 41 行：tier3 = tier3_daily_snapshot.py --date <d>。
- tier3_daily_snapshot.py 的写入位置：
  - 第 8、28–30 行：data/v2/tier3_daily/<kind>/<d>.parquet；
  - 第 60 行：data/v2/tier3_daily/manifests/<d>.json。
- nightly_update.py 本身的写入：
  - logs/nightly/<d>_tier3.log；
  - logs/nightly/<d>_summary.json（--steps 子集重跑时合并写入）；
  - output/relay_outage_backfill_queue.json（中转不通时 register_backfill）。
  - 只用 --steps tier3 时，不会进入 bundle 步骤。
- 与 .ok 的 19 个数据 pin 对照：
  - pin 路径为 output/strategy_hiliq/universe_mask_hiliq_v1.parquet、output/ai_factory/panel_cache/cs_panel_2018..2026.parquet（9 个）、float_mktcap、sw_l1_pit/industry_members_sw_l1_tushare.parquet、ref/stock_delisted.parquet、st_events/namechange_all.parquet、delisted/delisted_daily_tushare.parquet，以及代码和方案的 sha。
  - 还有 raw_content（tushare_raw/daily 和 suspend_d，截至 20261014）。
  - **tier3 一个都不碰**：不碰 cs_panel、mask，也不碰 bars、adj_factor、suspend_d、tushare_raw。
- 队列里待补跑的其他步骤（20261016 的 hsgt/sw/cyq）：
  - sw 写 data/v2/sw_pit/*，与 pin 所在的 sw_l1_pit/ 是不同目录；
  - cyq 写 data/v2/cyq/；
  - hsgt 是 fill_hsgt_top10_extend，也不碰 pin。
  - 结论：都不碰 pin。
- 门禁现状：
  - 命令行 "nightly_update.py --steps tier3" 不匹配 FORBID_PATTERNS，所以门禁放行，D1a–D3D4 的 dry-run 都是在它存活时通过的。
  - 风险：如果有人跑全量 nightly，它的子进程 tier1_pull、tier1_materialize、adj_factor_incr 会被禁止名单拦下；但父进程 nightly_update 本身不会被拦，在两个子步骤之间的空档期，门禁可能误放行。

## ② 两个 PID 的状态（02:19 EDT）
- 142531 和 142545 **仍在运行**。
  - 142531：nightly_update.py --date 20261015 --steps tier3，01:47:28 启动；142545 是它的子进程。
  - 父进程是 94403（relay_outage_backfill.py，01:22:24 启动），属于补拉例程，不是人工启动的。
- 进度：logs/nightly/20261015_tier3.log 最后更新于 01:47:35，只写出了 concept_dc_index（1035 行），之后 30 多分钟没有新输出。
  - tier3 的 call() 每页重试 4 次、退避 4–32 秒，最多 200 页。现在像是卡在中转的慢翻页或重试上，无法预计何时结束。
  - 不建议杀；即使要杀，也必须先征得同意。
- 94403 会不会再次拉起 nightly：**会**。
  - output/relay_outage_backfill_queue.json 的状态是 backfilling，还有 6 项待处理。其中 5 项带 retry_cmd，都是 nightly_update.py：20261015 tier3，以及 20261016 的 hsgt、sw、cyq、tier3。
  - 代码第 59–61 行逐个串行执行这些命令；第 70 行在还有未完成项时 sleep 900 秒再进入下一轮。所以接下来几小时会反复拉起 nightly。
  - busy_ok 的 HEAVY 名单（第 12 行）不含 fix_sd1，watcher 不会给 SD1 让路。
- 安排（只是方案，不执行，需你和 Arch 同意）：
  1. 申请 execute .ok 前，确认 142531 已自然结束（ps 中消失，20261015_tier3.log 出现收尾）。
  2. 在 142531 结束后、watcher 下一次拉起之前，对 94403 执行 `kill -STOP 94403`（暂停，可恢复，不丢队列）。记录时刻和 ps 快照，写进 execute 回执。
  3. 四步 execute 串行跑完、回执交出后，执行 `kill -CONT 94403` 恢复，并记录时刻。
  4. 另一种做法：不暂停 watcher，只把 fix_sd1 加进它的 HEAVY 名单（需要 Eng 改代码）。
  - 方案 2 不改代码，但必须避免在 142531 还活着时 STOP 94403：STOP 父进程不会影响子进程，只是子进程结束后 watcher 不会立刻接着跑。

## ③ 门禁禁止名单的位置与草拟改动
- scripts/fix_sd1/sd1_common.py：
  - 第 137 行 FORBID_PATTERNS = ("research/", "daily_pull", "tier1_pull", "tier1_materialize", "adj_factor", "bars_materialize")；
  - 第 147 行做匹配，命令行含 fix_sd1 的进程会被豁免；
  - 第 43 行是 .ok 模板里的 run_forbid_concurrent 字段。
- diff 草稿：docs/v2/audit/data_sd1_execute_prep/sd1_forbid_nightly_DRAFT.diff，**没有应用**。
  - 内容：在禁止名单里加入 "nightly_update" 和 "relay_outage_backfill"。
  - 应用后 common sha 会变，需要先存档、再同步三个脚本、请 Arch 重签。

## ④ 截止日 20261014 与 10-15、10-16 的 raw 是否齐全
- 20261014 是故意选的截止日，与 mask 和 v1 cs_panel 的最后交易日对齐。
- 文件存在情况：tushare_raw 的 daily、suspend_d、adj_factor 下，20261014、20261015、20261016 三天的文件都在，大小与前一天相近。
  - 这些文件的 mtime 都是 10-18 01:13–01:14，是重启后恢复的时刻，不代表下载时刻。
- 下载状态，来自 logs/nightly/*_summary.json：
  - 20261015 overall=partial：trade_cal、daily_pull、bars、daily_basic、events、hsgt 等都是 ok；只有 sw、cyq、tier3 是 partial（只能走中转的步骤）。summary 里没有单独的 adj_factor 步骤。
  - 20261016 overall=partial：daily_pull、adj_factor、bars、freshness 都是 ok；hsgt、sw、cyq、tier3 是 partial。
  - 20261016_adj_factor.log 显示 days_added=[20261014, 20261015, 20261016]，last_date=20261016。
  - 20261016_freshness.log 显示 expected_trade_date=20261016，overall=ok，stale_tables=[]。
- 结论：10-15、10-16 的 raw daily、suspend_d、adj_factor 都已齐全（daily_pull 和 adj_factor 都是 ok，freshness 也是 ok）。还缺的只有中转类步骤 sw、cyq、hsgt、tier3，而 SD1 不用这些数据。
- 如果把截止日延到 10-16，需要先重建 mask 和 v1 cs_panel，这不在本次 .ok 的授权范围内，所以维持 20261014。
