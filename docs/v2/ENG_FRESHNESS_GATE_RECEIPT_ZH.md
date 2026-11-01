# 交易日历 + 新鲜度闸门 Eng 回执（架构评审 Top1，Leo 批准；2026-10-14 ET）

live=false；不改权重；无 GP；峰值 RSS 789MB。

## 改动
- 新增 `quantlab/portfolio/trade_calendar.py`：SSE 日历（data/v2/tushare_raw/trade_cal.parquet，与 AI 扩展脚本用的是同一个，覆盖未来日期）。与 Data 的已实现日历 data/v2/asof_extend_202610/calendar.parquet 交叉核对：3104 个交易日完全一致。Data 的日历只到最近一个交易日，没有未来日期，所以以 trade_cal 为准。
- 应到交易日 = 运行日（ET）17:00 前取前一个交易日，17:00 后取当天（Data 夜间约 23:30 ET 完成）。
- `paper-daily`：
  - 运行日不是 SSE 交易日 → exit 0，`SKIPPED_NON_TRADING_DAY`，只追加一行到 `output/loop/skips.jsonl`。
  - 新鲜度：`output/daily_update_status.json` 需要 status=ok、target_trade_date = 应到交易日，且 etf_daily_adj / daily_ohlcv_raw_pit / daily_basic / mid_large_universe / etf510300 / asof_ts 的 last_date ≥ 目标；任一不满足 → **exit 3，`REFUSED_STALE_DATA`**，不跑 NAV，recon 列出原因，记分卡 md 顶部红色 STALE 横幅、每行加 🔴STALE，json 中 meta.STALE=true + stale_reasons。
  - FWD 起点检查：2026-11-02 必须是 SSE 交易日，且是 11 月第一个交易日 → ok（11-02 周一开市）。三条轨共用 b4_paper.FORWARD_START，不会差一天。
  - capacity_adv 月末守卫改用 SSE 日历每月最后开市日（替换原来的 BMonthEnd 工作日近似）；下一个调仓日 = 2026-10-30。
  - 测试钩子：环境变量 `QL_ASOF_ET`（模拟运行时刻）、`QL_STATUS_PATH`（替代状态文件）。

## 测试
| 场景 | 结果 |
|---|---|
| 今天（10-14 05:5x ET 实跑 --run-nav） | 通过，应到 10-13，exit 0，61.8s，RSS 789MB；三条轨 OK；X2H NAV 不变（816,368/1,317,300；835,205/1,363,378；870,612/1,425,853） |
| 假周末 2026-10-17 06:37 | SKIPPED_NON_TRADING_DAY，exit 0 |
| 节假日 2026-10-01 06:37 | SKIPPED_NON_TRADING_DAY，exit 0 |
| /tmp 状态副本 etf_daily_adj=10-12 | REFUSED_STALE_DATA，exit 3，原因 "table etf_daily_adj last_date=2026-10-12 < 2026-10-13"，记分卡 STALE；之后实跑覆盖恢复，/tmp 已删，测试产生的 skip 记录已清除 |

## 06:37 工作日例行任务
- 06:37 < 17:00 → 处理前一个交易日的数据：周一 10-19 → 10-16；节后 10-08 → 09-30（假期中的工作日 10-01~10-07 跳过，节后第一天自动补上）；11-02 → 10-30（月末调仓日）；11-03 → 11-02（FWD 第一天）。
- 注意：例行任务看到 exit 3 应视为"等 Data"，不要重试轰炸。17:00 后手动跑会要求当天数据，在 Data 夜间完成前会被拒绝（预期行为）。

## 追加（2026-10-14 05:5x ET）：Data 的 data_freshness_status.json + 看板总线
- 闸门优先读取 `output/data_freshness_status.json`（存在且 generated_at 不早于 daily_update_status.finished_at 时；否则回退）。拒绝条件：overall != ok，或所需表（etf_daily_adj、daily_ohlcv_raw_pit、daily_basic、mid_large_universe、etf510300）stale=true 或 last_date < 应到交易日。Data 文件没覆盖的表（asof_ts）仍按 daily_update_status 检查；status / target_trade_date 检查保留。注意 Data 的 'daily_raw' 只代表最新一个按日文件，没有作为必需表。
- 应到交易日仍用 Eng 自己的规则（17:00 ET）。Data 的 expected_trade_date（20:00 上海 = 08:00 ET）不一致时打印并记录 `calendar_mismatch`（以 Eng 为准）。已知的不一致窗口：如果 Data 在 08:00–17:00 ET 之间重新生成文件，它会提前一天；17:00 ET 到 Data 夜间完成之间，Eng 要求当天数据 → 拒绝（预期）。06:37 例行任务时两边一致（10-13）。
- 日历交叉核对：Data 的 `data/v2/calendar/trade_cal_sse_pit.parquet` 与 Eng 用的 trade_cal 完全一致（双向差 0）。
- 测试：当前文件 → PASS；/tmp 副本 overall=stale、daily_basic 为 10-12 → 拒绝（两条原因）；/tmp 已删。
- 总线（/workspace/quantlab-web/ql_bus.py，agent="QuantLab Eng"）：paper-daily 成功后发 nav（三条轨 × 两档 X2H NAV，FWD 等 11-02）、holdings（每轨每档前 8 大目标权重）、gate（新鲜度 + rehash/weight-gate/内容门 + 轨道状态 + pin）、receipt。SKIP 时发 alert（info），REFUSED_STALE_DATA 时发 alert（high，带原因）。全部包在 try/except 里，总线异常不会影响 paper-daily（模拟总线故障已验证）；`QL_BUS_OFF=1` 可关闭发送（测试用）。
- 今日实跑：exit 0，55s，峰值 RSS 768MB；总线 seq 34–37（nav/holdings/gate/receipt）已到达看板。为避免看板出现假告警，没有对实际总线发 skip/stale 测试告警。

## 2026-10-14 06:45 ET 修复：截止时间口径（Eng 平台 bug）
- **现象**：06:37 例行 paper-daily 以 exit 3 拒跑。Data 06:07 ET 已完成 10-14 的更新（target=10-14，所有表都到 10-14），而 Eng 按 17:00 ET 截止，期望的是 10-13。上证 15:00（上海）收盘等于 03:00 ET，17:00 ET 这个截止是错的。
- **修复**（trade_calendar.py，唯一常量 `CUTOFF_ET=(6,30)`）：
  - 交易日 D 从 D 日 06:30 ET 起成为必需交易日（required）。03:00 收盘到 06:30 之间是给 Data 的宽限窗，能覆盖 06:37 的例行运行。
  - Data 的 target_trade_date 满足以下条件就被接受，并作为本次处理的交易日（processed_session）：是交易日；收盘已过（`close_passed`，15:00 上海，不在未来）；≥ required；status=ok；所需表的 last_date 都 ≥ target。否则 REFUSED_STALE_DATA，并写明原因。
  - 非交易日 SKIP 的逻辑保持不变。新增 `latest_closed_session()`。
  - 旧的 17 ET 常量只保留为别名（=6），已不再使用。Data 侧 freshness 文件用的是 20:00 上海截止，两者不一致只记 info（对应审计 P2#15，Data 那边仍是 20:00）。
- **测试**（QL_ASOF_ET + 临时 status 副本）：

| 场景 | 结果 |
|---|---|
| 今天 06:37 / 06:45 | PASS，处理 10-14 |
| 10-17 周六 | SKIPPED_NON_TRADING_DAY，exit 0 |
| 10-01 节假日 | SKIP，exit 0 |
| etf_daily_adj 停在 10-13 | REFUSED |
| target=10-13 | REFUSED（早于 required 10-14） |
| 10-14 02:00 ET（target 在未来） | REFUSED |
| 10-14 05:00、target=10-13（宽限窗内） | PASS，处理 10-13 |

  测试写入的两行 skip 记录已删除。
- **实跑** `paper-daily --run-nav`（06:5x–07:0x ET，耗时 10:58，峰值 RSS 1.10GB）：exit 0，freshness PASS，处理 10-14，看板 nav/holdings/gate/receipt 四类事件均已发出。
  - **capacity_adv**：AI 的扩展写出 `g1g5_capacity_adv_daily_weights_paper_20261014_r2.parquet`，内容门（≤10-13 历史有 0 行差异）和 weight-gate 均通过，leg_pin 更新到 10-14。X2H 尾值：60万 814,527（10-14），100万 1,314,932。
  - **B4、S6**：扩展脚本 exit 4 ABORT_LEG_HISTORY_MISMATCH。earnings_event 腿重算后历史 keys 不一致（max_abs_diff=inf），insider_increase 和 equity_incentive 均一致。因此 X2H 停在 10-13：B4 60万 835,205 / 100万 1,363,378；S6 870,612 / 1,425,853。状态均为 PENDING，需要 AI 排查 earnings_event 历史改写（疑似 10-14 新数据改写了事件 PIT）。
  - 发现的问题：B4 扩展失败时状态仍显示 OK（只有 S6 会标 PENDING）。已在代码中补上 b4_pending，本日 recon 已手工改为 PENDING 并注明原因。看板 gate 事件在修正前已经发出，事件里仍是 b4=OK。
