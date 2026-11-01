# TICKET：settle 持有窗内的重复 trade_date 会被按位置重复计数

- 状态：**open**（不在本版本内：settle next_session r3 草稿明确不修这个问题）
- 提出：Eng，2026-10-18（东部时间）；来源是 settle next_session r2/r3 审查时发现的问题，Arch 裁定单独开工单
- 优先级建议：P3。先在只读 .ok 下核实真实数据里有没有重复，再定优先级

## 问题
`compute_horizon_returns` 按**位置**数持有窗：
- `inst_after = inst[inst.index > session]`
- `len(inst_after) <= horizon` → pending
- `exit_dt = inst_after.index[horizon]`

`_load_closes` 只按 trade_date 排序、过滤掉 NaN 和 ≤0 的价格，**不去重**。它还读了 `available_at` 列，但没有用这一列。所以同一个 trade_date 如果有多行（比如同一天有多个 available_at 版本），在入场和出场之间的窗口里会被算成多根 bar。

## 位置
- `quantlab/agents/trading_loop/settle.py`：`_load_closes`（仓库原件 L30–42）没有去重；`compute_horizon_returns` 里的 `len(inst_after)` 和 `inst_after.index[horizon_trading_days]`（原件 L89–98）按位置计数。
- r2/r3 草稿的 `_exact_px` 只检查入场日和出场日**当天**有没有重复（会给出 `*_entry_duplicate` / `*_exit_duplicate` → pending），**窗口中间**的重复它不管。
- r3 草稿的 `pending_age_sessions` 已经用 `nunique()` 去重计数，不受这个问题影响。

## 影响
1. 窗口中间每多一行重复，出场日就提前一个真实交易日，实际持有窗短于 `horizon_trading_days`；raw、bench、alpha 都按这个更短的窗口计算，而且记录本身看不出来。
2. pending 判断也会提前通过：真实 bar 还不够，却被判定为「已满窗」。
3. 基准侧不受计数影响（只在入场、出场两个日期上取价），但重复本身说明数据质量有问题。
4. 真实 `data/v2/etf/etf_daily_adj.parquet` 里**有没有**这种重复还没核实：读 parquet 需要起 python，本轮禁止。不影响纸面、权重和成交。

## 建议修复（下一版，需要 Arch 审查并签 .ok）
- 方案 A（推荐，最保守）：在 `[entry_dt, exit_dt]`（或整个 inst_after）内发现 `index.duplicated()` 时，返回 pending，`pending_reason="inst_window_duplicate"`（基准同理，用 `bench_window_duplicate`）；持有窗按**唯一日期**计数。
- 方案 B：在 `_load_closes` 里按明确的版本策略去重，例如每个 trade_date 只保留 `available_at` 最新的一行，或者只保留 `available_at ≤ 结算时点` 的一行。这需要 Data 确认 available_at 的语义。
- 单测（只用合成数据）：窗口中间有重复时，不能提前出场（方案 A 下是 pending，方案 B 下出场日等于按唯一日期数出来的第 h 根）；入场日和出场日的重复仍按现有逻辑判 pending。
- 修复前，先在 Arch 的只读 .ok 下统计真实数据里 `(ts_code, trade_date)` 有多少重复；如果有，评估是否需要重算受影响的旧记录（重算另需 .ok）。

## 不在本版本
settle next_session r3 草稿（`/workspace/sd1_work/settle_next_session/`）不改动这一逻辑。
