# Eng 侧稿回执：结算终场收盘 + 次日入场

日期：2026-10-27。Owner：QuantLab Eng。`live=false`，`promotion_approved=false`，≠X2 ACCEPT。

对照 Arch 文档 `docs/v2/ARCH_GITHUB_WATCH_ZH.md` sha8 `d227a6a4`（2026-10-27 候选 4 + 此前候选 2 next-session）。本 Origin 树的 `main`（`7197939`）没有该文档、也没有现成的 `compute_horizon_returns` / `load_prior_settlements`；本侧稿按 Arch 候选行为在研究路径新建模块，不并入、不启用候选 3（SSE 日历 PR #6）。

## 做了什么

- `quantlab/agents/trading_loop/settle.py`：horizon 结算只认**终场收盘**；默认 `entry_rule=next_session`（第一条 **严格晚于** 决策交易日的 bar）；`on_or_after` 仅用于复原旧结果。退出 = 入场后第 H 个终场交易日；不够则 `pending`，不写已结算。有日历且窗口不可能结束时不取价。取价上界仍短且 `end < today` 时，只把 fetch 上界扩到今天再试，不改 H。基准收益使用同一 `entry_dt`。新写入的 decision_log 打 `settle_rule`；已结算行保持旧值。
- `research/ai_debate_memory_runner.py`：`load_prior_settlements` 过滤后按 `(session 或 resolution_date, 行序)` 降序取最近 K 条，不用文件写入顺序 / `rows[-limit:]`。
- 合成单测：`tests/test_trading_loop_horizon_settle.py`。

as_of 篱笆是 `min(请求日日末, now)` + `available_at` 检查（Finathink 精神，未 import finathink）。未引入 TradingAgents / finathink 依赖。

## 关键文件 sha8（git hash-object）

| 文件 | sha8 |
|---|---|
| `quantlab/agents/trading_loop/settle.py` | `f0648fe0` |
| `research/ai_debate_memory_runner.py` | `8cdf9b61` |
| `tests/test_trading_loop_horizon_settle.py` | `8d710643` |
| `quantlab/agents/trading_loop/__init__.py` | `d7fedfb7` |

## 测试

```
.venv2/bin/python -m py_compile \
  quantlab/agents/trading_loop/__init__.py \
  quantlab/agents/trading_loop/settle.py \
  research/__init__.py \
  research/ai_debate_memory_runner.py \
  tests/test_trading_loop_horizon_settle.py

.venv2/bin/python -m unittest tests.test_trading_loop_horizon_settle -v
```

结果：`py_compile` 通过；`Ran 15 tests in 0.050s` **OK**。本侧稿 **不需要 Arch `.ok`**，也未读真实行情 parquet；夹具只在内存 / `TemporaryDirectory`。

四条指定行为：

1. 决策日大涨：`next_session` 的 `entry_dt` 在次日，收益不含当日 +50%；`on_or_after` 的入场日可以是决策日。
2. 「今天还在交易」或 `available_at > now` 的 bar 不能当终场收盘结算。
3. 国庆式缺口：日历显示窗口未结束则 `pending` 且不取价；取价窗口偏短则扩到今天后再结算或仍 `pending`。
4. 先写 6 月再回填 1 月，`limit=1` 仍取 6 月（按决策日，不按写入序）。

## 明确未做

- **未读真实市场数据**，未物化行情，未跑账户。
- **未改** paper-daily / FROZEN / `capacity_adv` / B4 / S6 权重；本树 `main` 也没有这些配置可改。
- **未改** live 开关、晋级门、优化器门。模块常量 `LIVE=false`、`PROMOTION_APPROVED=false`、`X2_ACCEPT=false`。
- **未启用候选 3**，未合并 SSE 日历 PR。
- 本仓没有 Arch 原文 `docs/v2/ARCH_GITHUB_WATCH_ZH.md`；行为按任务书与 TradingAgents 结算/记忆日期序（caf6792 族）核过，**下一步由 Arch 审阅**，Eng 不批准策略、不自动实盘。

## FIX_A（2026-10-27，对照 Arch 审阅 sha8 `a2051e37` §3 CONDITION A）

只修 CONDITION A。未开箱上 port（CONDITION B），未并候选 3 / PR #6（CONDITION C），未改 paper/FROZEN/权重/叶37。`live=false`。

- `_score_window` 对 `benchmark_closes` 复用 `_load_closes`（同一 `now` / `tz` / `regular_close` / 取价上界）。入场/出场日仍用标的的 `entry_dt` / `exit_dt`，不独自选基准第一根。
- 较安全口径：篱笆若去掉定价出场日所需的基准终场点 → `pending`（`insufficient_benchmark_final_closes`），不用盘中/`available_at>now` 的 bar 渗入 alpha，也不用更早的 stale asof 冒充出场。
- 合成覆盖：今日仍在交易的基准 bar 不影响已结算 alpha；出场日 `available_at>now` 的基准 bar 则 pending。原 15 项仍绿，合计 17 OK。

### 补丁后 sha8（git hash-object）

| 文件 | sha8 |
|---|---|
| `quantlab/agents/trading_loop/settle.py` | `9d98ad4f` |
| `tests/test_trading_loop_horizon_settle.py` | `56e381fc` |
| `research/ai_debate_memory_runner.py` | `8cdf9b61`（未改） |

### 复跑

```
.venv2/bin/python -m unittest tests.test_trading_loop_horizon_settle -v
```

结果：`Ran 17 tests` **OK**。无真行情，无 Arch `.ok`。待 Arch 复审；不 merge。
