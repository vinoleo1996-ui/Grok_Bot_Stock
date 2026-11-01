# Book-Smoke 回执：G1G5 **容量叶 capacity_adv**（`capacity_adv_v1`）**X2 满窗** vs 纯 510300

**run_id**：`book_smoke_20261013_111418`  
**strategy_promotion_approved**：`false`  
**sealed_claim**：`false`（不声称过密封线 / 不交 Strategy / 不下单）  
**promotion_approved**：`false`  
**Mandate**：`docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md`（本跑次**未改** Mandate）  
**授权**：Leo 经 New Bot 【派单·容量叶 Book-Smoke】立刻满窗  
**预注册**：`docs/v2/AI_G1G5_CAPACITY_ADV_WHO_PAYS_PREREG_ZH.md`  
**门锁（Leo 2026-10-12，研究对照非过关）**：净成本 **CAGR ∈ [12%, 18%]** · **MDD 不差于 −28%**  
**结构正交**：已败八包 + 叶A/叶B；本叶主仓 **个股≈0.79 + 510300 压舱≈0.21**（ADV 流动性分位 + 单名/参与率双硬顶；硬排除 `600519`/`002371`；月频；**非**估值残差 / OCF / 动量 / 四臂摩擦 / etf_core 0.70）→ 非叶B 换皮。本满窗 **两端同向过门** → **标研究备选（research_candidate=true）**；仍 **promotion=false / 不交 Strategy / handoff=NO**。

## 实验设置

| 项 | 值 |
|---|---|
| 权重长表 | `output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet`（**32732** 行 / **668** sessions / **49** 标的） |
| 对照 meta | `output/ai_factory/g1g5_capacity_adv_run_meta_20261013_111219.json`（`stub_window=false` · `stub_forward_fill=false` · `n_rebalance_sessions=35` · `hard_exclude=[002371.SZ,600519.SH]` · `adv_participation_k=0.02` · `aum_binding=1e6`） |
| mechanism_tag | **`g1g5_ashare_capacity_adv_v1`** |
| who_pays | 可成交容量约束下的流动性溢价/冲击成本错误定价对手盘：D1 asof ADV 代理（流通市值×换手）经申万一级行业 demean 后的流动性分位选股；单名≤4% + ADV 参与率双硬顶，压百万元端巨头成交/冲击缺口 |
| 明确排除 | 估值残差/裸 EP/BM；OCF 兑现；截面相对强弱主轴；四臂摩擦/解禁/份额流/调仓；ETF-core overlay；小盘主线；stub 前推 |
| 名义结构 | **个股≈0.79** / **510300 压舱≈0.21**（X2 日均；压舱可因容量缩权升至 ≈0.32，共 41/570 日 >0.25） |
| universe_id | `g1g5_mid_large_liquid_top50` |
| 袖套消费 | `{"core":0.0,"stock":1.0,"alpha_event":0.0}` = **整本账由该长表驱动**；表内已含压舱 → **禁止**再叠 core overlay |
| 对照 | `C0` = 纯 510300 |
| 窗 | 探索窗 **X2** `2024-06-03→2026-10-09` |
| 资金 | 60万 ∧ 100万 |
| 成本 | 开（`ExecConfig.strategy_v1`） |
| 可消费 | stock **book_consumable** rows=**15739** / sessions=**570**（X2∩权重日历=整窗；活跃权重大行 13449） |
| meta 换手 | mean_one_way **≈0.0125**；`n_rebalance_days_nonzero=34`；cadence=`month_end_plus_first_last`；`n_rebalance_sessions=35` |
| 角色 | 容量/ADV 可成交约束主测（设计目标：**60万与100万同向**）；对照=叶B + 叶A + 已败包 + 纯 510300 |

## ✅ 满窗日更（无 stub 前推）+ 结构核验

| 核验项 | 结果 |
|---|---|
| 权重日历 | **2024-01-02→2026-10-09**（668 sessions） |
| meta `stub_forward_fill` / `stub_window` | **false / false** |
| BOOK `n_signals` | **570**（= X2 可消费 sessions） |
| 唯一组合数（X2） | **30**（2024:8 + 2025:12 + 2026:10；月频节奏） |
| 尾段相同组合长度 | **1**（末日无长尾 stub 前推） |
| 日权重合计 | 恒 **1.0** |
| **日均个股权重（X2）** | **≈0.788**（min≈0.68 / max≈0.80） |
| **日均 510300 压舱（X2）** | **≈0.212**（min≈0.20 / max≈0.32；容量缩权余量→压舱） |
| 日均活跃个股 | **≈22.6**（min 17 / max 25） |
| 单名顶 | **≤0.04**（观测 max=0.04） |
| 硬排除 `600519`/`002371` | **权重表 0 行**（设计硬排除生效） |
| 未滑向 etf_core 0.70 | **是**（压舱仅宽基 510300≈0.21；无行业 ETF；禁 overlay） |
| 非估值残差 / 非 OCF / 非动量主轴 | **是**（预注册口径：ADV 流动性分位 + 容量硬约束） |
| 未双计 510300 overlay | **是**（sleeves.core=0；压舱仅来自表内） |

→ **禁止**再写「后半持仓前推」或「滑向 etf_core 0.70 / 估值残差换皮」。本回执是**真实满窗月频再平衡 + 个股≈0.79/压舱≈0.21 容量约束账**结果。

## 数字表（探索窗满窗；成本开；非密封）

| AUM | arm | CAGR | vs C0 | MDD | Sharpe | cost/AUM | target_weight 行数 |
|---|---|---|---|---|---|---|---|
| 600000 | X2/BOOK | **13.82%** (0.1382) | **+2.56 pp** | **−10.07%** | 1.018 | **0.0172** | 13449 |
| 600000 | X2/C0 | **11.27%** (0.1127) | — | −16.24% | 0.651 | 0.0002 | 570 |
| 1000000 | X2/BOOK | **12.23%** (0.1223) | **+0.97 pp** | **−11.62%** | 0.881 | **0.0171** | 13449 |
| 1000000 | X2/C0 | **11.27%** (0.1127) | — | −16.24% | 0.651 | 0.0002 | 570 |

起止：`2024-06-03→2026-10-09`。BOOK `n_codes=43`（引擎计数；X2 target 非零 **43** 码含 510300，其中个股 **42**；actual 成交 **43** 码，**target∉actual=[]**），`n_signals=**570**`，`gross_mean≈0.91`（60万）/ `≈0.95`（100万），`fill_ratio≈0.970` / `0.969`。

## 对照表（同窗 X2 满窗；本包 + 叶B + 叶A + 关键已败包）

| | **本包 容量ADV** | 叶B D1估值残差 | 叶A OCF+行业硬顶+动量中性 | 摩擦降成本再设计 | ETF-core+袖套 | 降换手 | 动量扩池 |
|---|---|---|---|---|---|---|---|
| mechanism | `…_capacity_adv_v1` | `…_d1_val_resid_v1` | `…_indcap_momneut_ocf_v1` | `…_friction_cost_redesign_v1` | `…_etf_core_sleeve_v1` | `…_friction_v1_lowturn` | `…_expand` |
| 持仓形态 | **个股≈79%+510300≈21%** | 个股≈80%+510300≈20% | 纯个股≈100% | 个股≈85%+510300≈15% | ETF≈70%+个股≈30% | 100% 股票 | 100% 股票 |
| 再平衡 | **月频** | 月频 | 月频 | 半月 | 月频 | 季末+粘性 | 月频 top20 |
| 60万 BOOK CAGR/MDD | **13.82% / −10.07%** | 11.64% / −14.88% | 8.61% / −14.60% | 6.03% / −16.06% | 8.46% / −20.39% | 10.13% / −17.86% | 11.37% / −15.15% |
| 100万 BOOK CAGR/MDD | **12.23% / −11.62%** | 9.76% / −16.71% | 8.10% / −15.98% | 6.74% / −15.79% | 9.43% / −20.05% | 10.21% / −17.90% | 11.42% / −15.88% |
| 60万 cost/AUM | **0.0172** | 0.0120 | 0.0161 | 0.0380 | 0.0369 | 0.0136 | 0.0284 |
| 100万 cost/AUM | **0.0171** | 0.0120 | 0.0150 | 0.0407 | 0.0438 | 0.0147 | 0.0307 |
| vs C0 ΔCAGR（60/100） | **+2.56 / +0.97 pp** | +0.37 / −1.51 | −2.66 / −3.17 | −5.23 / −4.53 | −2.81 / −1.84 | −1.13 / −1.06 | +0.11 / +0.15 |
| any_pass | **true** | false | false | false | false | false | false |

回执对照：`docs/v2/BOOK_SMOKE_G1G5_D1_VAL_RESID_X2_RECEIPT_ZH.md` · `docs/v2/BOOK_SMOKE_G1G5_INDCAP_MOMNEUT_OCF_X2_RECEIPT_ZH.md` · `docs/v2/BOOK_SMOKE_G1G5_FRICTION_COST_REDESIGN_X2_RECEIPT_ZH.md` · `docs/v2/BOOK_SMOKE_G1G5_ETF_CORE_SLEEVE_X2_RECEIPT_ZH.md` · `docs/v2/BOOK_SMOKE_G1G5_LOWTURN_X2_RECEIPT_ZH.md` · `docs/v2/BOOK_SMOKE_G1G5_EXPAND_X2_RECEIPT_ZH.md`

### 相对叶B：容量约束是否收窄 100万掉点？

| 对照 | 60万 ΔCAGR | 100万 ΔCAGR | 60→100 掉点 | 解读 |
|---|---|---|---|---|
| vs 叶B D1估值残差 | **+2.18 pp** | **+2.47 pp** | 本包 **1.59 pp** vs 叶B **1.88 pp** | 两端均强于叶B；掉点略收窄；**且两端同向过门**（叶B 仅 60万贴近门锁、100万未进） |
| vs C0 | **+2.56 pp** | **+0.97 pp** | — | **两端均胜纯 510300**（叶B 100万仍负） |
| vs expand | **+2.45 pp** | **+0.81 pp** | — | 强于已败动量扩池 |
| cost/AUM | ≈0.017 | 高于叶B 0.012 | — | meta 换手≈0.0125（高于叶B≈0.006）；账本成本仍远低于半月摩擦再设计 |

诚实结论：**结构正交声明成立（ADV 容量硬约束；硬排除巨头；个股≈0.79/压舱≈0.21；月频）**；设计目标「60万与100万同向」在本窗兑现——两端 CAGR 进 [12%,18%]、MDD 远好于 −28%、且相对 C0 同向为正。

## 对照门锁

| AUM/arm | CAGR∈[12%,18%] | MDD≥−28% | 过门？ |
|---|---|---|---|
| 60万 BOOK | **是**（13.82%） | **是**（−10.07% ≥ −28%） | **是** |
| 100万 BOOK | **是**（12.23%） | **是**（−11.62% ≥ −28%） | **是** |

C0 基线仍未过 CAGR 下沿（≈11.27%）。  
**任意 AUM 过门：是（any_pass=true）。** **两端同向过门：是（both_aum_pass=true）。**  
→ **本跑次标「研究备选」（research_candidate=true）**；仍为研究对照，**非** promotion / 密封 / Strategy 授权。

## vs C0 增量

| AUM | ΔCAGR | ΔMDD |
|---|---|---|
| 60万 | **+2.56 pp**（胜纯 510300） | **+6.17 pp**（回撤明显更浅） |
| 100万 | **+0.97 pp**（胜纯 510300） | **+4.62 pp**（回撤明显更浅） |

解读：本系列首次出现 **60万∧100万相对 C0 同向为正**；相对门锁下沿 12% 余量约 **+1.82 pp**（60万）/ **+0.23 pp**（100万，贴近下沿但仍过门）。

## 覆盖 / 缺价备注（诚实）

| 项 | 事实 |
|---|---|
| HFQ 外定价 | `run_book` 对 **43** 码调 `load_execution_panels`（**42** 在 HFQ 外）——个股 **可定价**，未 stub 前推补价 |
| target vs actual 码 | X2 BOOK target 非零 **43** 码；actual 成交 **43** 码；**target∉actual：[]（空）** |
| `600519` / `002371` | **权重表硬排除 → target 0 行 / actual 0 行**（叶B 曾有 63+23 日×≈4% 未成交缺口；本叶设计消除该缺口，**非**把未成交写成 pass） |
| 表内 510300 | 668 行均在；X2 日均权重 **≈0.21**（容量缩权日可升至 0.32） |
| 首日 2024-06-03 | target 有仓；actual 自 2024-06-04 起（T+1 执行日历正常），非缺价 |
| fill / gross | fill_ratio≈0.969–0.970；gross_mean≈0.91–0.95（执行后低于目标 1.0；闲置现金约 5–9%） |
| gaps 字段 | 引擎 `gaps=[]` |

→ **禁止**把缺价/空仓缺口写成 pass；本跑次未用 stub 前推补价；巨头缺口由硬排除消除，**不**虚构成交。

## 机制与候选口径

- 本包是 **容量叶：ADV 可成交约束**（个股≈0.79 + 510300≈0.21，月频，硬排除巨头），明确排除估值残差/OCF/动量/四臂/etf_core overlay 与已败同构；结构正交声明成立。  
- **满窗 any_pass=true** → **标研究备选（research_candidate=true）**。  
- 仍 **`promotion_approved=false`** · **不交 Strategy** · **不开密封** · **不下单** · **禁小盘主线**。  
- **handoff=NO**。

## 工程备注

- 模块：`python3 -m quantlab.portfolio.book_smoke`
- JSON：`output/v3/book_smoke_g1g5_capacity_adv_x2/book_smoke_summary.json`  
  （含 `mechanism_note` / `mandate_door` / `vs_baseline_C0` / `structure_check` / `any_pass` / `research_candidate` / `vs_d1_val_resid` / `weight_coverage_caveat` / `headline`）
- NAV：`output/v3/book_smoke_g1g5_capacity_adv_x2/aum_{600000,1000000}/X2/{BOOK,C0}/`
- promotion=false；不下单；不交 Strategy；不开密封；未改 Mandate。

## 结论（诚实）

1. **管线通 + 满窗真日更 + 结构核验过**：668 sessions 至 2026-10-09；`n_signals=570`；唯一组合 30；尾长 1；**日均个股≈0.79 / 压舱≈0.21**；硬排除巨头生效；**已证伪 stub 前推与 etf_core 0.70 overlay**。  
2. **换手/成本**：meta mean_one_way≈0.0125；账本 cost/AUM≈**1.72%/1.71%**（高于叶B，仍远低于半月摩擦再设计）。  
3. **相对叶B**：60万 **+2.18 pp**、100万 **+2.47 pp**；60→100 掉点 **1.59 pp**（叶B 1.88 pp）——容量约束略收窄掉点，且两端同向过门。  
4. **相对基线 C0**：60万 **+2.56 pp**；100万 **+0.97 pp**；MDD 两端均明显浅于 C0。  
5. **覆盖缺口**：`600519`/`002371` **无目标仓**（硬排除）；target∉actual 为空。  
6. **研究门锁**：**any_pass=true** → **research_candidate=true**；`promotion=false`；不交 Strategy；**handoff=NO**。  
7. **一句话**：容量/ADV 约束真跑满窗（个股≈0.79+压舱≈0.21，硬排除巨头），**60万∧100万同向过门且同向胜 C0**——本窗标研究备选，仍不晋级、不交 Strategy。
