# Book-Smoke 回执：G1G5 全日更辩论袖套（overlay）vs 纯 510300

**run_id**：`book_smoke_20261012_104935`  
**strategy_promotion_approved**：`false`  
**sealed_claim**：`false`（不声称过密封线 / 不交 Strategy / 不下单）  
**promotion_approved**：`false`  
**Mandate**：`docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md`  
**授权**：Leo 经 New Bot 【批冒烟|G1G5 全日更】（本条 Book-Smoke only）  
**门锁（Leo 2026-10-12，研究对照非过关）**：净成本 **CAGR ∈ [12%, 18%]** · **MDD 不差于 −28%**

## 实验设置

| 项 | 值 |
|---|---|
| 权重长表 | `output/intel/g1g5_daily_weights_20261012_104627.parquet`（726 行 / 242 sessions；**非 stub**） |
| 对照 meta | `output/intel/g1g5_run_meta_20261012_104627.json` |
| 接线回执 | `docs/v2/AI_G1G5_WIRING_RECEIPT_ZH.md` |
| mechanism_tag | `g1g5_pit_debate_rule_v1` |
| universe_id | `g1g5_mid_large_liquid` |
| 袖套模式 | **overlay**：`{"core":1.0,"stock":1.0,"alpha_event":0.0}` |
| combine 语义 | `book += sleeve_w * table_weight`；core 恒为 510300×1.0，stock 加上表内绝对权重（~4–6% 卫星仓） |
| 对照 | `C0` = 纯 510300 |
| 窗 | 探索窗 **X2** `2024-06-03→2026-10-09` |
| 资金 | 60万 ∧ 100万 |
| 成本 | 开（`ExecConfig.strategy_v1`） |
| 可消费 | stock **book_consumable** rows=**585** / sessions=**144**（X2∩权重日历） |
| 日权重合计 | 约 **0.04–0.06**（辩论袖套卫星仓，不是满仓因子表） |
| 成分 | 卫星：`600519.SH` / `601318.SH` / `000858.SZ` + 压舱 `510300` |

## ⚠ 覆盖缺口（必须读）

权重日历仅覆盖 **2024-01-02→2024-12-31**（全日更 242 sessions）。  
落在 X2 内的可消费信号为 **2024-06-03→2024-12-31（144 sessions）**。  
X2 后半段 **2025-01-01→2026-10-09** 无新权重：引擎 `combine()` 在最后一次信号后 **持仓前推** → 约一年半净值主要由  
**2024 年末卫星袖套叠在 510300 上的长期持有**贡献，**不是** G1G5 全日更覆盖整窗。  
`n_unique_portfolios≈3`（目标权重视图）。

→ 本回执只证明：**G1G5 长表能以 overlay 进主书 + 相对 C0 有可算对比**；**不能**当作密封过线、辩论规则有效性或晋级证据。  
**切勿**用 stub 前推、**切勿**交 Strategy。

## 毛敞口说明

overlay 下 core+stock 名义可略 >1；执行侧经 `cash_target` / `max_gross` 归一后，BOOK 实现 `gross_mean≈0.95`（60万）/ `≈0.96`（100万），`fill_ratio≈0.99` / `0.98`。相对纯 C0（gross≈1.0）有少量闲置现金与卫星换仓成本。

## 数字表（探索窗；成本开；非密封）

| AUM | arm | CAGR | vs C0 | MDD | Sharpe | cost/AUM | target_weight 行数 |
|---|---|---|---|---|---|---|---|
| 600000 | X2/BOOK | **11.05%** (0.1105) | **−0.22 pp** | **−15.64%** | 0.664 | 0.0003 | 2280 |
| 600000 | X2/C0 | **11.27%** (0.1127) | — | −16.24% | 0.651 | 0.0002 | 570 |
| 1000000 | X2/BOOK | **10.65%** (0.1065) | **−0.62 pp** | **−15.89%** | 0.641 | 0.0004 | 2280 |
| 1000000 | X2/C0 | **11.27%** (0.1127) | — | −16.24% | 0.651 | 0.0002 | 570 |

起止：`2024-06-03→2026-10-09`。BOOK `n_codes=4`，`n_signals=144`。

## 对照门锁

| AUM/arm | CAGR∈[12%,18%] | MDD≥−28% | 过门？ |
|---|---|---|---|
| 60万 BOOK | **否**（11.05% < 12%） | **是**（−15.64% ≥ −28%） | **否** |
| 100万 BOOK | **否**（10.65% < 12%） | **是**（−15.89% ≥ −28%） | **否** |

C0 基线仍未过 CAGR 下沿（11.27% < 12%）；MDD 宽于 −28%。  
**任意 AUM 过门：否。** 本结果为研究对照，非过关声称。

## vs C0 增量

| AUM | ΔCAGR | ΔMDD |
|---|---|---|
| 60万 | −0.22 pp（略逊） | +0.60 pp（回撤略浅） |
| 100万 | −0.62 pp（略逊） | +0.36 pp（回撤略浅） |

解读：~5% 辩论袖套在探索窗上 **未抬升 CAGR**，相对纯 510300 略有拖累（卫星换仓成本 + 闲置现金）；MDD 略改善但仍属基线附近噪声量级。

## 工程备注

- 模块：`python3 -m quantlab.portfolio.book_smoke`
- `run_book`：schedule 含 HFQ 默认 7 ETF 之外的 3 只个股时，回落 `load_execution_panels`。
- JSON：`output/v3/book_smoke_g1g5/book_smoke_summary.json`（含 `experiment` / `weight_coverage_caveat` / `mandate_door` / `vs_baseline_C0`）
- NAV 产物：`output/v3/book_smoke_g1g5/aum_{600000,1000000}/X2/{BOOK,C0}/`
- promotion=false；不下单；不交 Strategy；不开密封 X1；不晋级 V31；不跑 STOCK-* 事件臂。

## 结论（诚实）

1. **管线通**：G1G5 非 stub 长表经 WeightLongTableSleeve + overlay 进主书，consumable sessions=144 ≫10，BOOK ≠ C0（偏差小但可算）。  
2. **相对基线**：探索窗 BOOK CAGR **略低于** 纯 510300≈11.3%；MDD 略浅。  
3. **未过门锁**：CAGR 两端均 <12%；MDD 单项过 −28% 线，合取 **不过门**。  
4. **不可晋级**：权重日历止于 2024-12-31 + 持仓前推 → 数字不可当作全日更策略有效或密封过线；`strategy_promotion_approved=false`。  
5. **下一步建议**（研究向，勿交 Strategy）：若要严肃对照，需要 **覆盖完整 X2（至少至 2026-10）的 G1G5 日更权重**，再以同一 overlay 重跑 Book-Smoke；勿用 stub 前推填洞。
