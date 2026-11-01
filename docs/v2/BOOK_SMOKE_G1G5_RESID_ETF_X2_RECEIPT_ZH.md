# Book-Smoke 回执：G1G5 **残差×ETF**（`resid_etf_flow_v1`）**X2 满窗日更** vs 纯 510300

**run_id**：`book_smoke_20261013_002720`  
**strategy_promotion_approved**：`false`  
**sealed_claim**：`false`（不声称过密封线 / 不交 Strategy / 不下单）  
**promotion_approved**：`false`  
**Mandate**：`docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md`  
**授权**：Leo 经 New Bot 【派工|Book-Smoke】主测残差×ETF 满窗包（研究级）  
**门锁（Leo 2026-10-12，研究对照非过关）**：净成本 **CAGR ∈ [12%, 18%]** · **MDD 不差于 −28%**  
**Leo 纠偏**：机制有效就不要机械排除候选；过闸可进**研究备选**；本满窗未过闸 → **本跑次不标备选**。

## 实验设置

| 项 | 值 |
|---|---|
| 权重长表 | `output/ai_factory/g1g5_resid_etf_daily_weights_20261013_002418.parquet`（**33400** 行 / **668** sessions / **50** 标的） |
| 对照 meta | `output/ai_factory/g1g5_resid_etf_run_meta_20261013_002418.json`（`reaches_x2_end=true` · `stub_window=false` · `stub_forward_fill=false` · G6 pass） |
| mechanism_tag | **`g1g5_ashare_resid_etf_flow_v1`** |
| who_pays | 个股行业内残差（20日，流通市值三分位中性）× 行业ETF申赎份额流交互；偏好份额流入行业内正残差个股 |
| 明确排除 | 教科书相对强弱 / 估值 / 质量主线；**非**解禁/T+1/涨跌停四臂摩擦复刻 |
| 合成分 | resid 0.55 + etf_flow 0.30 + interaction 0.15；月频 top20 等权 |
| universe_id | `g1g5_mid_large_liquid_top50` |
| 袖套模式 | **满仓 stock 表**：`{"core":0.0,"stock":1.0,"alpha_event":0.0}` |
| 对照 | `C0` = 纯 510300 |
| 窗 | 探索窗 **X2** `2024-06-03→2026-10-09` |
| 资金 | 60万 ∧ 100万 |
| 成本 | 开（`ExecConfig.strategy_v1`） |
| 可消费 | stock **book_consumable** rows=**13360** / sessions=**570**（X2∩权重日历=整窗） |
| meta 换手 | mean_one_way **≈0.0289**；`n_rebalance_sessions=35` |
| 角色 | 正交机制主测（残差×ETF 流）；对照=动量扩池 / 月频制度摩擦 / 降换手 |

## ✅ 满窗日更（无 stub 前推）— 已用数据核验

| 核验项 | 结果 |
|---|---|
| 权重日历 | **2024-01-02→2026-10-09**（668 sessions） |
| meta `reaches_x2_end` | **true** |
| meta `stub_forward_fill` / `stub_window` | **false / false** |
| BOOK `n_signals` | **570**（= X2 可消费 sessions） |
| 唯一组合数（X2） | **30**（2024:8 + 2025:12 + 2026:10；月频节奏） |
| 尾段相同组合长度 | **1**（末日才一变，非长尾粘住前推） |
| 日权重合计 | 恒 **1.0**；日活跃恒 **20** 只 |

→ **禁止**再写「后半持仓前推」。本回执是**真实满窗月频再平衡**结果。

## 数字表（探索窗满窗；成本开；非密封）

| AUM | arm | CAGR | vs C0 | MDD | Sharpe | cost/AUM | target_weight 行数 |
|---|---|---|---|---|---|---|---|
| 600000 | X2/BOOK | **5.25%** (0.0525) | **−6.01 pp** | **−14.92%** | 0.434 | **0.0254** | 11400 |
| 600000 | X2/C0 | **11.27%** (0.1127) | — | -16.24% | 0.651 | 0.0002 | 570 |
| 1000000 | X2/BOOK | **5.52%** (0.0552) | **−5.75 pp** | **−14.74%** | 0.442 | **0.0277** | 11400 |
| 1000000 | X2/C0 | **11.27%** (0.1127) | — | -16.24% | 0.651 | 0.0002 | 570 |

起止：`2024-06-03→2026-10-09`。BOOK `n_codes=51`，`n_signals=**570**`，`gross_mean≈0.89`（60万）/ `≈0.93`（100万），`fill_ratio≈0.95` / `0.96`。

## 四包对照表（同窗 X2 满窗）

| | **本包残差×ETF** | 降换手 | 月频制度摩擦 | 动量扩池 |
|---|---|---|---|---|
| mechanism | `…_resid_etf_flow_v1` | `…_friction_v1_lowturn` | `…_friction_v1` | `…_expand`（截面动量） |
| 再平衡 | 月频 top20 | 季末+粘性 | 月频 top20 | 月频 top20 |
| 60万 BOOK CAGR/MDD | **5.25% / −14.92%** | 10.13% / −17.86% | 8.24% / −13.95% | 11.37% / −15.15% |
| 100万 BOOK CAGR/MDD | **5.52% / −14.74%** | 10.21% / −17.90% | 9.61% / −13.02% | 11.42% / −15.88% |
| 60万 cost/AUM | **0.0254** | 0.0136 | 0.0264 | 0.0284 |
| 100万 cost/AUM | **0.0277** | 0.0147 | 0.0283 | 0.0307 |
| vs C0 ΔCAGR（60/100） | **−6.01 / −5.75 pp** | −1.13 / −1.06 pp | −3.03 / −1.66 pp | +0.11 / +0.15 pp |
| any_pass | **false** | false | false | false |

回执对照：`docs/v2/BOOK_SMOKE_G1G5_LOWTURN_X2_RECEIPT_ZH.md` · `docs/v2/BOOK_SMOKE_G1G5_NONTEXTBOOK_X2_RECEIPT_ZH.md` · `docs/v2/BOOK_SMOKE_G1G5_EXPAND_X2_RECEIPT_ZH.md`

### 相对同窗包：机制正交是否换来 alpha？

| 对照 | 60万 ΔCAGR | 100万 ΔCAGR | 解读 |
|---|---|---|---|
| vs 动量扩池 | **−6.12 pp** | **−5.90 pp** | 远逊动量满窗 |
| vs 月频制度摩擦 | **−2.98 pp** | **−4.09 pp** | 逊于同换手量级摩擦包 |
| vs 降换手 | **−4.88 pp** | **−4.69 pp** | 逊于已降成本的摩擦变体 |
| vs C0 | **−6.01 pp** | **−5.75 pp** | 两端大幅跑输纯 510300 |
| cost/AUM | ≈0.025–0.028 | ≈月频摩擦同量级 | 换手未压低，成本无优势 |

诚实结论：**机制声明正交成立（残差×ETF 流，非动量/非四臂摩擦），但 X2 满窗实证 alpha 未兑现**——四包中 CAGR 最弱，相对 C0 约 −6 pp。

## 对照门锁

| AUM/arm | CAGR∈[12%,18%] | MDD≥−28% | 过门？ |
|---|---|---|---|
| 60万 BOOK | **否**（5.25% < 12%） | **是**（−14.92% ≥ −28%） | **否** |
| 100万 BOOK | **否**（5.52% < 12%） | **是**（−14.74% ≥ −28%） | **否** |

C0 基线仍未过 CAGR 下沿（≈11.27%）。  
**任意 AUM 过门：否（any_pass=false）。** 本结果为研究对照，非过关声称。  
→ **本跑次不标「研究备选」**（过闸才标）。

## vs C0 增量

| AUM | ΔCAGR | ΔMDD |
|---|---|---|
| 60万 | **−6.01 pp**（大幅逊于纯 510300） | +1.32 pp（回撤略浅） |
| 100万 | **−5.75 pp**（大幅逊于纯 510300） | +1.51 pp（回撤略浅） |

解读：MDD 略浅于 C0，但 CAGR 缺口约 **6 pp**，远不足以用「回撤更浅」辩护；相对门锁下沿 12% 差约 **6.5–6.8 pp**。

## 机制与候选口径

- 本包是**残差×行业ETF申赎份额流**交互，明确排除教科书相对强弱/估值/质量，也**不是**解禁/T+1/涨跌停四臂摩擦复刻；与 expand / friction / lowturn 正交声明成立。  
- **满窗 any_pass=false** → **不标研究备选**（Leo：过闸才进备选；纠偏「有效就不要机械排除」——本包实证未显示有效）。  
- 仍 **`promotion_approved=false`** · **不交 Strategy** · **不开密封** · **不下单**。

## 工程备注

- 模块：`python3 -m quantlab.portfolio.book_smoke`
- JSON：`output/v3/book_smoke_g1g5_resid_etf_x2/book_smoke_summary.json`  
  （含 `experiment` / `weight_coverage_caveat.full_x2_daily=true` / `mandate_door` / `vs_baseline_C0` / `vs_momentum_x2` / `vs_friction_monthly_x2` / `vs_lowturn_x2` / `turnover_note` / `mechanism_note` / `headline`）
- NAV：`output/v3/book_smoke_g1g5_resid_etf_x2/aum_{600000,1000000}/X2/{BOOK,C0}/`
- promotion=false；不下单；不交 Strategy；不开密封。

## 结论（诚实）

1. **管线通 + 满窗真日更**：668 sessions 至 2026-10-09；`n_signals=570`；唯一组合 30（月频）；尾长 1；**已证伪 stub 前推**。  
2. **换手/成本**：meta mean_one_way≈0.0289；账本 cost/AUM≈**2.5–2.8%**（≈月频摩擦，远高于降换手 1.4%）。  
3. **相对同窗三包**：CAGR 全面落后（vs 动量约 −6 pp，vs 摩擦约 −3～−4 pp，vs 降换手约 −4.7～−4.9 pp）。  
4. **相对基线 C0**：两端约 **−6 pp**；MDD 略浅但不足以补偿。  
5. **研究门锁**：**any_pass=false** → **不标备选**；`promotion=false`；不交 Strategy。  
6. **一句话**：机制正交、满窗真跑，但门锁没进、相对 C0 大负——残差×ETF 流本窗未兑现研究备选资格。
