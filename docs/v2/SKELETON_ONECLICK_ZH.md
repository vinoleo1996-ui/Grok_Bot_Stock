# 骨架一键验收（Eng）

**角色**：Eng · 平台接口 · 研究级  
**日期**：2026-10-12（ET）  
**门控**：`promotion_approved` / `strategy_promotion_approved` **均 false**（本页命令不改 `promotion_gate`）  
**开源**：只读参考 `/workspace/opensource/{TradingAgents,QuantMind}`，**不 vendor 进主仓**

## 一键

```bash
cd /workspace/QuantLab
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.v2_skeleton_smoke
# 或
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli skeleton-smoke
```

退出码 0 = 四步骨架通：`trading_loop` → `factor_evolve` → `weight_long_table` 契约 → `book_smoke --skip-run`。  
**默认不跑净值**（轻量）。若要顺带 C0 NAV：加 `--book-nav`（更重，仍非全量 D1/GP）。

摘要 JSON：`output/v3/skeleton_smoke/skeleton_smoke_summary.json`

## 分项命令

| 目标 | 一句话 | 命令 |
|---|---|---|
| trading_loop | TradingAgents 适配状态机 stub，写一条 pending 决策 | `PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli trading-loop --session 2024-07-01 --instrument 510500.SH` |
| 同上（模块） | | `python -m quantlab.agents.trading_loop` |
| factor_evolve | QuantMind 风格硬闸 stub → 可消费权重长表 | `PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli factor-evolve --smoke` |
| 同上（模块） | | `python -m quantlab.agents.factor_evolve --smoke` |
| book_smoke | Mandate 主书骨架；**默认 skip-run**（不物化 NAV） | `PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli book-smoke` |
| book_smoke NAV | 显式跑净值（重） | `python -m quantlab.cli book-smoke --run-nav --stock-path output/factor_evolve/latest…` |
| 权重契约 | 握手 / 校验 | 见下节 |

图示：`python -m quantlab.cli trading-loop --show-graph`

## 权重长表契约（冻结）

> **覆盖规则**：全日更长表须覆盖目标窗、**禁止仅前推解读**。
> 引擎在末条权重后的持仓前推 ≠ 日更继续；严肃对照前请用
> `assert_session_coverage` / `assert_session_coverage_path` 核对 `session_min..session_max`。
> 闭环一键见 `LIVE_DRYRUN_COMMANDS_ZH.md`（`python -m quantlab.cli live-dry-run`）。


**Eng 模块**：`quantlab.platform.weight_long_table`  
**版本**：`weight_long_v1_20261012`

| 列 | 必需 | dtype | 别名 |
|---|---|---|---|
| `session` | ✓ | datetime / 可解析日 | `date`, `trade_date` |
| `instrument_id` | ✓ | str（偏好 `sh.`/`sz.`） | `instrument`, `ts_code`, `code` |
| `weight` | ✓ | float **> 0** | `target_weight` |
| `sleeve` | 可选 | str | `sleeve_name` |

- 写入辅助：`write_weight_long_table(df, path)` → parquet + `.meta.json`，`promotion_approved=false`
- 校验：`validate_weight_path(path)` / `validate_weight_frame(df)`
- 握手：`schema_handshake()`
- Book 消费：`WeightLongTableSleeve`（`quantlab.portfolio.v2_multisleeve_book`）按路径挂到 `stock` / `alpha_event` 袖套；多袖套单文件的 `sleeve` 列目前为契约预留，主路径仍是分文件 + `--stock-path` / `--alpha-event-path`

factor_evolve 产出的 QM P0 meta 标签 `weight_long_v1_qm_p0_20261012` 与 Eng 权威列一致；列权威以 Eng 模块为准。

```bash
PYTHONPATH=. /workspace/qlvenv/bin/python -c \
  "from quantlab.platform.weight_long_table import schema_handshake; import json; print(json.dumps(schema_handshake(),ensure_ascii=False,indent=2))"
```

## stub vs 真

| 组件 | 状态 |
|---|---|
| trading_loop 状态机 / 决策 JSONL / settle 契约 | **stub**（无 LLM、不下单） |
| factor_evolve 候选 + 硬闸 + 合成分数 → 长表 | **stub**（`--smoke`；真面板需 Leo 探索批准 + Data） |
| weight_long_table 契约 / 校验 / 别名 | **真**（Eng 冻结） |
| book_smoke `--skip-run` | **真接线**（写回执骨架，不调 Data） |
| book_smoke `--run-nav` | **真引擎**（读市数据；研究级；非密封） |
| AI 工厂 L2+ / 密封窗 / 晋级 | **未开** |

## 给 Alpha / AI / Strategy

- **Alpha / AI**：挖因子后请产出权威三列（或 AI 别名 `date,instrument,target_weight`），经 `normalize_weight_frame` / `write_weight_parquet` 落盘；KPI = **可消费长表行数**，不是 GP 尝试次数。  
- **Strategy**：`book-smoke --run-nav --stock-path <parquet>`；无长表时 BOOK≈C0（510300）。  
- **Beta**：risk_review 节点在 trading_loop stub 里仅占位；Mandate 门锁仍归研究结论，不归 Eng。  
- **不要**把 ≤10 个交易日的 stub 长表当生产日更。

## 相关文档

- `SYSTEM_ARCH_V3_ZH.md` / `SYSTEM_ARCH_V3_AI_NATIVE_ZH.md` / `SYSTEM_ARCH_V3_INTERFACES.md`
- `OPENSOURCE_ENG_ADOPTION_ZH.md` · `TRADINGAGENTS_ADAPT_OVERVIEW_ZH.md`
- `MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md`
- 开源只读：`/workspace/opensource/README_ZH.md`
