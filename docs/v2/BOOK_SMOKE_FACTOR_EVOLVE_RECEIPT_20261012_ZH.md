# Book-Smoke 回执：factor_evolve 权重长表 vs 纯 510300

**run_id**：`book_smoke_20261012_102510`  
**strategy_promotion_approved**：`false`  
**sealed_claim**：`false`（不声称过密封线 / 不交 Strategy / 不下单）  
**Mandate**：`docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md`  
**门锁（Leo 2026-10-12）**：净成本 **CAGR 12%–18%** · **MDD 不差于 −28%**

## 实验设置

| 项 | 值 |
|---|---|
| 权重长表 | `output/factor_evolve/fe_20261012_101924_10514de4_weights.parquet`（latest_meta 同） |
| 袖套 | `stock=1.0, core=0.0, alpha_event=0.0`（WeightLongTableSleeve） |
| 对照 | `C0` = 纯 510300 |
| 窗 | 探索窗 **X2** `2024-06-03→2026-10-09` |
| 资金 | 60万 ∧ 100万 |
| 成本 | 开（`ExecConfig.strategy_v1`） |
| 可消费 | stock **book_consumable** rows=50 / sessions=**10** |

## ⚠ 覆盖缺口（必须读）

factor_evolve stub 权重只覆盖 **2024-06-03→2024-06-14（10 个交易日 / 50 行）**。  
引擎 `combine()` 在最后一次信号后 **持仓前推** 至 X2 末日 → 约两年净值主要由  
**2024-06 中旬等权篮**（茅台 / 科创50 / 创业板 / 半导体 / 宽基混搭）的长期持有贡献，  
**不是**完整窗因子日更。`n_unique_portfolios≈5`。

→ 本回执只证明：**权重长表能进主书 + 相对 C0 有可算增量**；**不能**当作密封过线或因子演化有效性证明。

## 数字表（探索窗；成本开；非密封）

| AUM | arm | CAGR | vs C0≈11.3% | MDD | Sharpe | cost/AUM | target_weight 行数 |
|---|---|---|---|---|---|---|---|
| 600000 | X2/BOOK | **25.60%** (0.2560) | +14.3 pp | **−29.40%** | 0.927 | 0.0024 | 2850 |
| 600000 | X2/C0 | **11.27%** (0.1127) | — | −16.24% | 0.651 | 0.0002 | 570 |
| 1000000 | X2/BOOK | **24.56%** (0.2456) | +13.3 pp | **−29.47%** | 0.879 | 0.0026 | 2850 |
| 1000000 | X2/C0 | **11.27%** (0.1127) | — | −16.24% | 0.651 | 0.0002 | 570 |

起止：`2024-06-03→2026-10-09`。BOOK `n_codes=10`，`fill_ratio≈0.999`。

## 对照门锁

| AUM/arm | CAGR∈[12%,18%] | MDD≥−28% | 过门？ |
|---|---|---|---|
| 60万 BOOK | **否**（25.6% > 18%） | **否**（−29.4% < −28%） | **否** |
| 100万 BOOK | **否**（24.6% > 18%） | **否**（−29.5% < −28%） | **否** |

C0 基线仍未过 CAGR 下沿（11.3% < 12%）；MDD 宽于 −28%。

## 工程备注

- `run_book`：schedule 含 HFQ 默认 7 ETF 之外的代码时，回落 `load_execution_panels`（个股/扩 ETF 可定价）。
- JSON：`output/v3/book_smoke_factor_evolve/book_smoke_summary.json`
- promotion=false；不下单；不交 Strategy。

## 结论（诚实）

1. **管线通**：factor_evolve 长表经 WeightLongTableSleeve 进主书，BOOK ≠ C0。  
2. **相对基线**：探索窗 BOOK CAGR 明显高于纯 510300≈11.3%，但 **MDD 更深且突破 −28% 门锁**。  
3. **不可晋级**：权重 stub + 持仓前推 → 数字不可当作策略有效；`strategy_promotion_approved=false`。  
4. 下一步若要严肃对照：需要 **覆盖完整 X2 的日更权重长表**（非 10 日 stub），再重跑 Book-Smoke。
