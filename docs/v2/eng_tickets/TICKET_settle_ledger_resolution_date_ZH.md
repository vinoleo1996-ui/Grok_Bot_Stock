# TICKET：settle_debate_ledger 写入的 settlement 没有 resolution_date

- 状态：**open**（不在本版本内：settle next_session r3 草稿明确不修这个问题）
- 提出：Eng，2026-10-18（东部时间）；来源是 settle next_session r2/r3 审查时发现的问题，Arch 裁定单独开工单
- 优先级建议：P3（研究记忆通路，不影响纸面、权重和成交）

## 问题
`research/settle_debate_ledger_vs_510300.py` 往 debate ledger 追加 `SettlementRecord` 时：
- settled 行只写了 decision_id、session、instrument、horizon_days、benchmark、raw_return、alpha_vs_benchmark、reflection_zh、settled_at、promotion_approved（r3 草稿另加 settle_rule）；
- **既没写 `resolution_date`，也没写 `exit_date`。** `compute_horizon_returns` 返回的 `exit_date` 只进了 stdout 汇总，没有落到 ledger。

## 位置
- `research/settle_debate_ledger_vs_510300.py`：settled 分支和 unavailable 分支构造 `SettlementRecord(...)` 的地方（仓库原件 L46–57、L63–74）。
- `quantlab/intel/debate_ledger.py` L82：`resolution_date: str  # YYYY-MM-DD exit bar; G6 memory PIT filter (resolved≤asof)`。字段已经定义，但这个脚本没有填。
- 消费方：`research/ai_debate_memory_runner.py` L74 起的 `settlement_resolved_date()`，取值顺序是 `resolution_date` → `exit_date` → `settled_at` 的日期部分；`load_prior_settlements(as_of=...)` 用它做 G6 过滤（只回灌 resolved ≤ as_of 的记录）。
- 对照：`research/g1g5_wiring.py` L635、L654，以及 `ai_debate_memory_runner.py` L949，都正确写了 `resolution_date = exit_date[:10]`。

## 影响
1. 这个脚本写的 settled 行，在 G6 过滤里只能退回用 `settled_at`（运行时的墙钟日期）当「结果揭晓日」。
   - 正常补结算时，settled_at 晚于真实出场日，回放时这条记忆会被**过度屏蔽**：本该从出场日起可用，却要等到 settled_at 之后才可用。这是偏保守的方向，代价是少了记忆。
   - 如果用 `--allow-mock` 跑，mock bar 从 session 起按 bdate 生成，可能延伸到运行日之后，这时 settled_at 会**早于** mock 出场日，G6 就可能放行一条「未来才揭晓」的 mock 记忆。默认 allow_mock=False，而且 mock 本身标了 settle_source=mock，但口径上仍然有缺口。
2. 不同写入方在同一个 ledger 里口径不一致：g1g5_wiring 和 memory_runner 写了 resolution_date，这个脚本没写，审计时难以统一核对。
3. 不影响纸面、权重、成交或 Strategy NAV（promotion_approved 始终为 false）。

## 建议修复（下一版，需要 Arch 审查并签 .ok）
- settled 分支：`resolution_date = str(m["exit_date"])[:10]`，同时把 `entry_date` 和 `exit_date` 也写进 settlement 行。这需要先在 SettlementRecord 里补这两个可选字段，或者明确依赖 total=False 的宽松写法。
- unavailable 分支：不写 resolution_date（继续退回用 settled_at），或者显式写 `resolution_date = settled_at[:10]`，二选一后写进文档。
- 补单测（只用合成数据）：ledger 里的 settled 行带 resolution_date，且等于 exit_date；G6 用 `load_prior_settlements(as_of=exit_date 的前一天)` 时，这条记录被挡住。
- 旧 ledger 行**不回填**；如果要回填，单独申请重算 .ok。

## 不在本版本
settle next_session r3 草稿（`/workspace/sd1_work/settle_next_session/`）不改动这一逻辑。
