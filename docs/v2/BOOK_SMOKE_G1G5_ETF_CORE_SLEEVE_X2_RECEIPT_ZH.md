# Book-Smoke 回执：G1G5 **ETF-core+个股袖套**（`etf_core_sleeve_v1`）**X2 满窗** vs 纯 510300

**run_id**：`book_smoke_20261012_205410`  
**strategy_promotion_approved**：`false`  
**sealed_claim**：`false`（不声称过密封线 / 不交 Strategy / 不下单）  
**promotion_approved**：`false`  
**Mandate**：`docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md`（本跑次**未改** Mandate）  
**授权**：Leo 经 New Bot 【派工|Book-Smoke|研究级】下一叶 ETF-core+个股袖套  
**预注册**：`docs/v2/AI_G1G5_ETF_CORE_SLEEVE_WHO_PAYS_PREREG_ZH.md`  
**门锁（Leo 2026-10-12，研究对照非过关）**：净成本 **CAGR ∈ [12%, 18%]** · **MDD 不差于 −28%**  
**结构正交**：已败四包均为 **100% 股票满仓**；本叶主仓 **直接持有行业 ETF**（名义 ≈0.70）+ 有限个股袖套（≈0.30）→ 非换皮。本满窗未过闸 → **本跑次不标备选**。

## 实验设置

| 项 | 值 |
|---|---|
| 权重长表 | `output/ai_factory/g1g5_etf_core_sleeve_daily_weights_20261012_204928.parquet`（**59452** 行 / **668** sessions / **89** 标的） |
| 对照 meta | `output/ai_factory/g1g5_etf_core_sleeve_run_meta_20261012_204928.json`（`reaches_x2_end=true` · `stub_window=false` · `stub_forward_fill=false` · G6 pass） |
| mechanism_tag | **`g1g5_ashare_etf_core_sleeve_v1`** |
| who_pays | 行业ETF创设/赎回份额流对手盘支付 ETF-core 相对宽基配置差 + 流入行业内中大盘个股流动性承接对手盘支付有限袖套 |
| 明确排除 | 教科书相对强弱 / 估值主线；**非** expand / nontextbook / lowturn / resid_etf 四包同构 |
| 名义结构 | **ETF-core ≈0.70**（行业ETF + 510300 压舱） / **个股袖套 ≈0.30** |
| universe_id | `g1g5_etf_core_sleeve_mid_large_v1` |
| 袖套消费 | `{"core":0.0,"stock":1.0,"alpha_event":0.0}` = **整本账由该混合长表驱动**（表内已含 ETF+个股）；**禁止**再叠 core=0.7 的 510300 overlay；**禁止**过滤 ETF 只留个股 |
| 对照 | `C0` = 纯 510300 |
| 窗 | 探索窗 **X2** `2024-06-03→2026-10-09` |
| 资金 | 60万 ∧ 100万 |
| 成本 | 开（`ExecConfig.strategy_v1`） |
| 可消费 | stock **book_consumable** rows=**8644** / sessions=**570**（X2∩权重日历=整窗；活跃权重大行 7418） |
| meta 换手 | mean_one_way **≈0.0291**；`n_rebalance_days_nonzero=34`；cadence=`month_end_plus_first` |
| 角色 | 结构正交主测（ETF-core+袖套）；对照=已败四包 + 纯 510300 |

## ✅ 满窗日更（无 stub 前推）+ 结构核验

| 核验项 | 结果 |
|---|---|
| 权重日历 | **2024-01-02→2026-10-09**（668 sessions） |
| meta `reaches_x2_end` | **true** |
| meta `stub_forward_fill` / `stub_window` | **false / false** |
| BOOK `n_signals` | **570**（= X2 可消费 sessions） |
| 唯一组合数（X2） | **30**（2024:8 + 2025:13 + 2026:11；跨年去重后 30；月频节奏） |
| 尾段相同组合长度 | **1**（末日才一变，非长尾粘住前推） |
| 日权重合计 | 恒 **1.0** |
| **日均 ETF 权重** | **≈0.70**（min/max 均 ≈0.70） |
| **日均个股权重** | **≈0.30** |
| 日均活跃 | ETF ≈5.84 只 / 个股 ≈7.10 只 |
| 未压成 100% 股票 | **是**（结构核验通过） |
| 未双计 510300 overlay | **是**（sleeves.core=0） |

→ **禁止**再写「后半持仓前推」或「被压成纯股票账」。本回执是**真实满窗月频再平衡 + ETF/个股混合结构**结果。

## 数字表（探索窗满窗；成本开；非密封）

| AUM | arm | CAGR | vs C0 | MDD | Sharpe | cost/AUM | target_weight 行数 |
|---|---|---|---|---|---|---|---|
| 600000 | X2/BOOK | **8.46%** (0.0846) | **−2.81 pp** | **−20.39%** | 0.491 | **0.0369** | 7418 |
| 600000 | X2/C0 | **11.27%** (0.1127) | — | -16.24% | 0.651 | 0.0002 | 570 |
| 1000000 | X2/BOOK | **9.43%** (0.0943) | **−1.84 pp** | **−20.05%** | 0.526 | **0.0438** | 7418 |
| 1000000 | X2/C0 | **11.27%** (0.1127) | — | -16.24% | 0.651 | 0.0002 | 570 |

起止：`2024-06-03→2026-10-09`。BOOK `n_codes=76`，`n_signals=**570**`，`gross_mean≈0.96`（60万）/ `≈0.98`（100万），`fill_ratio≈0.99` / `0.99`。

## 五包对照表（同窗 X2 满窗）

| | **本包 ETF-core+袖套** | 残差×ETF | 降换手 | 月频制度摩擦 | 动量扩池 |
|---|---|---|---|---|---|
| mechanism | `…_etf_core_sleeve_v1` | `…_resid_etf_flow_v1` | `…_friction_v1_lowturn` | `…_friction_v1` | `…_expand` |
| 持仓形态 | **ETF≈70%+个股≈30%** | 100% 股票 | 100% 股票 | 100% 股票 | 100% 股票 |
| 再平衡 | 月频 | 月频 top20 | 季末+粘性 | 月频 top20 | 月频 top20 |
| 60万 BOOK CAGR/MDD | **8.46% / −20.39%** | 5.25% / −14.92% | 10.13% / −17.86% | 8.24% / −13.95% | 11.37% / −15.15% |
| 100万 BOOK CAGR/MDD | **9.43% / −20.05%** | 5.52% / −14.74% | 10.21% / −17.90% | 9.61% / −13.02% | 11.42% / −15.88% |
| 60万 cost/AUM | **0.0369** | 0.0254 | 0.0136 | 0.0264 | 0.0284 |
| 100万 cost/AUM | **0.0438** | 0.0277 | 0.0147 | 0.0283 | 0.0307 |
| vs C0 ΔCAGR（60/100） | **−2.81 / −1.84 pp** | −6.01 / −5.75 pp | −1.13 / −1.06 pp | −3.03 / −1.66 pp | +0.11 / +0.15 pp |
| any_pass | **false** | false | false | false | false |

回执对照：`docs/v2/BOOK_SMOKE_G1G5_RESID_ETF_X2_RECEIPT_ZH.md` · `docs/v2/BOOK_SMOKE_G1G5_LOWTURN_X2_RECEIPT_ZH.md` · `docs/v2/BOOK_SMOKE_G1G5_NONTEXTBOOK_X2_RECEIPT_ZH.md` · `docs/v2/BOOK_SMOKE_G1G5_EXPAND_X2_RECEIPT_ZH.md`

### 相对同窗包：结构正交是否换来 alpha？

| 对照 | 60万 ΔCAGR | 100万 ΔCAGR | 解读 |
|---|---|---|---|
| vs 动量扩池 | **−2.92 pp** | **−1.98 pp** | 逊于动量满窗 |
| vs 月频制度摩擦 | **+0.22 pp** | **−0.17 pp** | 与摩擦包几乎持平 |
| vs 降换手 | **−1.67 pp** | **−0.77 pp** | 逊于已降成本摩擦变体 |
| vs 残差×ETF | **+3.20 pp** | **+3.92 pp** | 明显强于残差×ETF，但仍未过门锁 |
| vs C0 | **−2.81 pp** | **−1.84 pp** | 两端仍跑输纯 510300 |
| cost/AUM | ≈0.037–0.044 | 高于四包 | meta 换手同量级，账本成本偏高（行业ETF执行） |

诚实结论：**结构正交声明成立（ETF-core+袖套，非 100% 股票）**，CAGR 好于残差×ETF、贴近平月频摩擦，但相对 C0 仍负、成本偏高，**门锁未进**。

## 对照门锁

| AUM/arm | CAGR∈[12%,18%] | MDD≥−28% | 过门？ |
|---|---|---|---|
| 60万 BOOK | **否**（8.46% < 12%） | **是**（−20.39% ≥ −28%） | **否** |
| 100万 BOOK | **否**（9.43% < 12%） | **是**（−20.05% ≥ −28%） | **否** |

C0 基线仍未过 CAGR 下沿（≈11.27%）。  
**任意 AUM 过门：否（any_pass=false）。** 本结果为研究对照，非过关声称。  
→ **本跑次不标「研究备选」**（过闸才标）。

## vs C0 增量

| AUM | ΔCAGR | ΔMDD |
|---|---|---|
| 60万 | **−2.81 pp**（逊于纯 510300） | −4.15 pp（回撤更深） |
| 100万 | **−1.84 pp**（逊于纯 510300） | −3.80 pp（回撤更深） |

解读：相对 C0 既亏收益又加深回撤；相对门锁下沿 12% 差约 **2.6–3.5 pp**。

## 覆盖 / 缺价备注（诚实）

| 项 | 事实 |
|---|---|
| HFQ 外定价 | `run_book` 对 **76** 码调 `load_execution_panels`（**75** 在 HFQ 外）——行业 ETF **可定价**，未 stub 前推补价 |
| `sz.159031` | 2026-08-31 起有权重，2026-09-01 起有 actual；**已成交**，非缺价 |
| `sz.002371` | 出现在 target，**未进入 actual**（单票未成交缺口） |
| 首日 2024-06-03 | actual 空仓（T+1 执行日历正常），非缺价 |
| fill / gross | fill_ratio≈0.99；gross_mean≈0.96–0.98（执行后略低于目标 1.0） |

→ **禁止**把缺价/空仓缺口写成 pass；本跑次未用 stub 前推补价。

## 机制与候选口径

- 本包是 **ETF-core（份额流选行业 ETF）+ 个股袖套（流入行业内换手承接）**，明确排除教科书相对强弱/估值，也**不是**四包 100% 股票满仓同构；结构正交声明成立。  
- **满窗 any_pass=false** → **不标研究备选**。  
- 仍 **`promotion_approved=false`** · **不交 Strategy** · **不开密封** · **不下单** · **禁小盘主线**。

## 工程备注

- 模块：`python3 -m quantlab.portfolio.book_smoke`
- JSON：`output/v3/book_smoke_g1g5_etf_core_sleeve_x2/book_smoke_summary.json`  
  （含 `experiment` / `structure_check` / `weight_coverage_caveat` / `mandate_door` / `vs_baseline_C0` / `vs_expand_x2` / `vs_friction_monthly_x2` / `vs_lowturn_x2` / `vs_resid_etf_x2` / `turnover_note` / `mechanism_note` / `headline`）
- NAV：`output/v3/book_smoke_g1g5_etf_core_sleeve_x2/aum_{600000,1000000}/X2/{BOOK,C0}/`
- promotion=false；不下单；不交 Strategy；不开密封；未改 Mandate。

## 结论（诚实）

1. **管线通 + 满窗真日更 + 结构核验过**：668 sessions 至 2026-10-09；`n_signals=570`；唯一组合 30；尾长 1；**日均 ETF≈0.70 / 个股≈0.30**；**已证伪 stub 前推与「压成纯股票」**。  
2. **换手/成本**：meta mean_one_way≈0.029；账本 cost/AUM≈**3.7–4.4%**（高于已败四包，行业 ETF 执行更贵）。  
3. **相对同窗四包**：强于残差×ETF（约 +3–4 pp），贴近平月频摩擦，逊于降换手与动量扩池。  
4. **相对基线 C0**：两端约 **−1.8～−2.8 pp**，且 MDD 更深。  
5. **研究门锁**：**any_pass=false** → **research_candidate=false**；`promotion=false`；不交 Strategy。  
6. **一句话**：结构正交真跑满窗，但门锁没进、相对 C0 仍负、成本偏高——ETF-core+袖套本窗不进研究备选。
