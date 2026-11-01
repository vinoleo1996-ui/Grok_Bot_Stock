# 决策记忆结算规格（相对 510300 alpha）

**日期**：2026-10-12 · America/New_York  
**状态**：研究规格 · **`strategy_promotion_approved=false`** · **不自动下单**  
**实现**：`quantlab/agents/trading_loop/settle.py` · CLI `settle_pending`  
**对照灵感**：TradingAgents Memory log + `settle_all_pending`（相对区域基准 alpha）；**重写为 A 股 / 510300 / 仓内行情**，不调用 Yahoo。

---

## 1. 目的

把「某日对某标的的研究决策」在持有窗走完后打成**可复盘的质量分数**：

- **原始收益** `raw_return`
- **相对沪深300 ETF（510300.SH）的 alpha** `alpha_vs_510300 = raw − bench`
- **短反思** `reflection_zh`（供后续 PM/分析师阅读）

这是**决策质量记忆**，不是组合现金账本，不是密封 NAV，不是晋级证据。

---

## 2. 记录生命周期

| 状态 | 含义 |
|---|---|
| `pending` | 已写入决策；持有窗未满或基准未齐 |
| `settled` | 已算出 raw / bench / alpha + reflection |
| `unavailable` | 无行情或价格无效，放弃该条 |
| `rejected_by_pm` | PM 未批准研究提案（不进入 settle） |

字段见 `quantlab/agents/trading_loop/schemas.py` → `DecisionLogEntry`。

默认日志路径：`output/trading_loop/decision_log.jsonl`（一行一个 JSON）。

---

## 3. PIT / 时点纪律

| 阶段 | 规则 |
|---|---|
| **决策时** | `session` = 决策 as-of 日；分析师 brief 只能用 `available_at ≤ session` 的证据（二期强制；一期 stub 无实据） |
| **入场价** | 标的在 `session` **当日或之后第一个**有效交易日收盘（避免用未开盘价） |
| **出场价** | 入场后再数 `horizon_trading_days` 个**该标的**交易日收盘 |
| **基准** | 同一日历入/出场日，对 510300 用 `asof` 对齐收盘 |
| **结算时** | **允许**看入场之后的价格（事后评分）；这不是前视造信号，而是对已做决策的结果记账 |
| **写入反思的时点** | `settled_at` = 结算脚本运行时刻；`exit_date` = 结果可知日 |

禁止：用结算得到的 alpha 回填同一 `session` 的分析师输入。

---

## 4. 收益定义

设入场收盘 \(P_0\)、出场 \(P_1\)，基准 \(B_0,B_1\)：

\[
r_{\text{raw}} = \frac{P_1-P_0}{P_0},\quad
r_{\text{bench}} = \frac{B_1-B_0}{B_0},\quad
\alpha = r_{\text{raw}} - r_{\text{bench}}
\]

- 默认 `horizon_trading_days = 5`（可按决策覆盖）。  
- 评级方向解读（研究用，非自动调仓）：
  - Buy / Overweight：期望 \(\alpha>0\)
  - Sell / Underweight：期望 \(\alpha<0\)（若实现为做多相对基准，符号解释写在 reflection；一期不做空）
  - Hold / Abstain：结算仍记收益，反思标注「无方向主张」

一期实现：**一律按多头持有窗计 raw**（与「只做多、无融券」一致）；反向评级的「正确性」留给二期符号翻转规则。

---

## 5. 数据源优先级

1. **仓内** `data/v2/etf/etf_daily_adj.parquet`（`ts_code,trade_date,close,available_at`）— 宽基/行业 ETF 决策首选  
2. 二期：个股日线 PIT 面板（中大盘宇宙）  
3. **`allow_mock=true`（默认）**：缺表时用确定性假序列，并在 `settle_source=mock` 标明  
4. `--no-mock`：缺表 → `unavailable`，不造假

基准恒为 **`510300.SH`**（可被条目字段覆盖，但主书口径禁止改成 SPY 等）。

---

## 6. 与主书 / 晋级的防火墙

| 允许 | 禁止 |
|---|---|
| 追加 JSONL；打印 settled alpha | 改 `strategy_promotion_approved` |
| 供 AI/PM 读最近反思 | 把平均 alpha 写成密封 CAGR |
| 导出研究对照 | 自动生成券商订单 / 改默认真书权重 |
| Beta 可选读 settled 分布作**风险讨论** | 把 settled rating 当成交价或 fill |

Mandate 门锁（CAGR 12–18%、MDD−28%、60∧100万）只约束**主书 Book-Smoke / 密封**，不由本 settle 单独判定过线。

---

## 7. CLI 与成功标准（一期）

```bash
python3 -m quantlab.agents.trading_loop.run_stub --session 2024-07-01 --instrument 510500.SH
python3 -m quantlab.agents.trading_loop.settle_pending
```

成功：`settled_n≥1`（历史 session 足够长时），日志中出现 `alpha_vs_510300`、`reflection_zh`、`settle_source=etf_daily_adj`（或明确 `mock`），且 `strategy_promotion_approved=false`。

---

## 8. 二期扩展（备忘）

- 与 `intel/debate_ledger.JsonlDebateLedger` 双写 / 迁移  
- 按 rating 分组的网格回测记忆（独立 `run_id`，不污染主日志）  
- 结算失败不阻断新决策（上游行为）；本包已按「单条 unavailable」处理  
- 个股 PIT 收盘与涨跌停「只挡成交不改估值」对齐主引擎语义
