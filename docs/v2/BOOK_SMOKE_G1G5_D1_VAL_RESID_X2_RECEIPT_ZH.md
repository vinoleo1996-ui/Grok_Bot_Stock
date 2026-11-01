# Book-Smoke 回执：G1G5 **叶B D1 估值残差 asof**（`d1_val_resid_v1`）**X2 满窗** vs 纯 510300

**run_id**：`book_smoke_20261013_110353`  
**strategy_promotion_approved**：`false`  
**sealed_claim**：`false`（不声称过密封线 / 不交 Strategy / 不下单）  
**promotion_approved**：`false`  
**Mandate**：`docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md`（本跑次**未改** Mandate）  
**授权**：Leo 经 New Bot 【派单·叶B Book-Smoke】立刻满窗  
**预注册**：`docs/v2/AI_G1G5_D1_VAL_RESID_WHO_PAYS_PREREG_ZH.md`  
**门锁（Leo 2026-10-12，研究对照非过关）**：净成本 **CAGR ∈ [12%, 18%]** · **MDD 不差于 −28%**  
**结构正交**：已败六包 + 叶A（纯个股≈1.0）；本叶主仓 **个股≈0.80 + 510300 压舱≈0.20**（D1 asof 估值残差 + 行业/市值中性 + 20d 超额正交；月频；**非**裸 EP/BM；**非** etf_core 0.70）→ 非 expand / 叶A 换皮。本满窗未过闸 → **本跑次不标备选**。

## 实验设置

| 项 | 值 |
|---|---|
| 权重长表 | `output/ai_factory/g1g5_d1_val_resid_daily_weights_20261013_110154.parquet`（**34068** 行 / **668** sessions / **51** 标的） |
| 对照 meta | `output/ai_factory/g1g5_d1_val_resid_run_meta_20261013_110154.json`（`reaches_x2_end=true` · `stub_window=false` · `stub_forward_fill=false` · G6 pass） |
| mechanism_tag | **`g1g5_ashare_d1_val_resid_v1`** |
| who_pays | 错误定价纠偏：D1 asof 估值倍数经申万一级行业与流通市值中性后的残差修正；低估侧收敛由边际资金支付相对 510300 的持有窗；并对相对宽基 20 日超额收益暴露做正交化压低 |
| 明确排除 | 裸 EP/BM/PE 截面排序；残差收益×份额流同构；四臂摩擦/解禁/调仓流；ETF-core 直接持有；截面相对强弱主轴；**非** expand / friction月频 / lowturn / resid_etf / etf_core / friction_cost_redesign / 叶A-OCF 同构 |
| 名义结构 | **个股≈0.80** / **510300 压舱≈0.20**（表内恒定；日均活跃个股 20） |
| universe_id | `g1g5_mid_large_liquid_top50` |
| 袖套消费 | `{"core":0.0,"stock":1.0,"alpha_event":0.0}` = **整本账由该长表驱动**；表内已含压舱 → **禁止**再叠 core overlay |
| 对照 | `C0` = 纯 510300 |
| 窗 | 探索窗 **X2** `2024-06-03→2026-10-09` |
| 资金 | 60万 ∧ 100万 |
| 成本 | 开（`ExecConfig.strategy_v1`） |
| 可消费 | stock **book_consumable** rows=**14028** / sessions=**570**（X2∩权重日历=整窗；活跃权重大行 11970） |
| meta 换手 | mean_one_way **≈0.0062**；`n_rebalance_days_nonzero=33`；cadence=`month_end_plus_first_last`；`n_rebalance_sessions=35` |
| 角色 | 叶B D1 估值残差 asof 主测（个股≈0.80+压舱≈0.20，月频）；对照=叶A + 已败六包 + 纯 510300 |

## ✅ 满窗日更（无 stub 前推）+ 结构核验

| 核验项 | 结果 |
|---|---|
| 权重日历 | **2024-01-02→2026-10-09**（668 sessions） |
| meta `reaches_x2_end` | **true** |
| meta `stub_forward_fill` / `stub_window` | **false / false** |
| BOOK `n_signals` | **570**（= X2 可消费 sessions） |
| 唯一组合数（X2） | **29**（2024:8 + 2025:13 + 2026:10；跨年去重后 29；月频节奏） |
| 尾段相同组合长度 | **3**（末日附近短粘，非长尾 stub 前推） |
| 日权重合计 | 恒 **1.0** |
| **日均个股权重** | **≈0.80**（min/max 均 ≈0.80） |
| **日均 510300 压舱** | **≈0.20**（min/max 均 ≈0.20） |
| 日均活跃 | **20** 只（min 20 / max 20） |
| 未滑向 etf_core 0.70 | **是**（压舱仅宽基 510300≈0.20；无行业 ETF；禁 overlay） |
| 非裸 EP/BM | **是**（预注册口径：行业 demean + 流通市值三分位 demean + 20d 超额正交；非裸截面 EP/BM 排序） |
| 未双计 510300 overlay | **是**（sleeves.core=0；压舱仅来自表内 0.20） |

→ **禁止**再写「后半持仓前推」或「滑向 etf_core 0.70 / 裸价值排序」。本回执是**真实满窗月频再平衡 + 个股≈0.80/压舱≈0.20 估值残差账**结果。

## 数字表（探索窗满窗；成本开；非密封）

| AUM | arm | CAGR | vs C0 | MDD | Sharpe | cost/AUM | target_weight 行数 |
|---|---|---|---|---|---|---|---|
| 600000 | X2/BOOK | **11.64%** (0.1164) | **+0.37 pp** | **−14.88%** | 0.795 | **0.0120** | 11970 |
| 600000 | X2/C0 | **11.27%** (0.1127) | — | −16.24% | 0.651 | 0.0002 | 570 |
| 1000000 | X2/BOOK | **9.76%** (0.0976) | **−1.51 pp** | **−16.71%** | 0.661 | **0.0120** | 11970 |
| 1000000 | X2/C0 | **11.27%** (0.1127) | — | −16.24% | 0.651 | 0.0002 | 570 |

起止：`2024-06-03→2026-10-09`。BOOK `n_codes=39`（引擎计数；X2 target 非零 **39** 码含 510300，其中个股 **38**；actual 成交 **37** 码），`n_signals=**570**`，`gross_mean≈0.90`（60万）/ `≈0.94`（100万），`fill_ratio≈0.995` / `0.997`。

## 八包对照表（同窗 X2 满窗）

| | **本包 叶B D1估值残差** | 叶A OCF+行业硬顶+动量中性 | 摩擦降成本再设计 | ETF-core+袖套 | 残差×ETF | 降换手 | 月频制度摩擦 | 动量扩池 |
|---|---|---|---|---|---|---|---|---|
| mechanism | `…_d1_val_resid_v1` | `…_indcap_momneut_ocf_v1` | `…_friction_cost_redesign_v1` | `…_etf_core_sleeve_v1` | `…_resid_etf_flow_v1` | `…_friction_v1_lowturn` | `…_friction_v1` | `…_expand` |
| 持仓形态 | **个股≈80%+510300≈20%** | 纯个股≈100% | 个股≈85%+510300≈15% | ETF≈70%+个股≈30% | 100% 股票 | 100% 股票 | 100% 股票 | 100% 股票 |
| 再平衡 | **月频** | 月频 | 半月 | 月频 | 月频 top20 | 季末+粘性 | 月频 top20 | 月频 top20 |
| 60万 BOOK CAGR/MDD | **11.64% / −14.88%** | 8.61% / −14.60% | 6.03% / −16.06% | 8.46% / −20.39% | 5.25% / −14.92% | 10.13% / −17.86% | 8.24% / −13.95% | 11.37% / −15.15% |
| 100万 BOOK CAGR/MDD | **9.76% / −16.71%** | 8.10% / −15.98% | 6.74% / −15.79% | 9.43% / −20.05% | 5.52% / −14.74% | 10.21% / −17.90% | 9.61% / −13.02% | 11.42% / −15.88% |
| 60万 cost/AUM | **0.0120** | 0.0161 | 0.0380 | 0.0369 | 0.0254 | 0.0136 | 0.0264 | 0.0284 |
| 100万 cost/AUM | **0.0120** | 0.0150 | 0.0407 | 0.0438 | 0.0277 | 0.0147 | 0.0283 | 0.0307 |
| vs C0 ΔCAGR（60/100） | **+0.37 / −1.51 pp** | −2.66 / −3.17 | −5.23 / −4.53 | −2.81 / −1.84 | −6.01 / −5.75 | −1.13 / −1.06 | −3.03 / −1.66 | +0.11 / +0.15 |
| any_pass | **false** | false | false | false | false | false | false | false |

回执对照：`docs/v2/BOOK_SMOKE_G1G5_INDCAP_MOMNEUT_OCF_X2_RECEIPT_ZH.md` · `docs/v2/BOOK_SMOKE_G1G5_FRICTION_COST_REDESIGN_X2_RECEIPT_ZH.md` · `docs/v2/BOOK_SMOKE_G1G5_ETF_CORE_SLEEVE_X2_RECEIPT_ZH.md` · `docs/v2/BOOK_SMOKE_G1G5_RESID_ETF_X2_RECEIPT_ZH.md` · `docs/v2/BOOK_SMOKE_G1G5_LOWTURN_X2_RECEIPT_ZH.md` · `docs/v2/BOOK_SMOKE_G1G5_NONTEXTBOOK_X2_RECEIPT_ZH.md` · `docs/v2/BOOK_SMOKE_G1G5_EXPAND_X2_RECEIPT_ZH.md`

### 相对同窗包：结构正交是否换来 alpha？

| 对照 | 60万 ΔCAGR | 100万 ΔCAGR | 解读 |
|---|---|---|---|
| vs 叶A OCF | **+3.03 pp** | **+1.66 pp** | 强于叶A 两端 |
| vs 动量扩池 | **+0.27 pp** | **−1.66 pp** | 60万略强于 expand，100万逊 |
| vs 月频制度摩擦 | **+3.40 pp** | **+0.15 pp** | 强于已败月频摩擦 |
| vs 降换手 | **+1.51 pp** | **−0.45 pp** | 60万强于 lowturn，100万略逊 |
| vs ETF-core+袖套 | **+3.18 pp** | **+0.33 pp** | 强于 ETF-core |
| vs 残差×ETF | **+6.39 pp** | **+4.24 pp** | 明显强于 resid_etf |
| vs 摩擦降成本再设计 | **+5.61 pp** | **+3.02 pp** | 明显强于半月摩擦再设计 |
| vs C0 | **+0.37 pp** | **−1.51 pp** | 60万略胜纯 510300，100万仍负 |
| cost/AUM | ≈0.012 | 八包最低档之一 | meta 换手≈0.006（月频+压舱）账本成本偏低 |

诚实结论：**结构正交声明成立（个股≈0.80 / 压舱≈0.20；月频；D1 估值残差 + 行业/市值中性；非裸 EP/BM；非 etf_core）**，CAGR 为同窗八包中 60万最强（11.64%，距门锁下沿仅约 **0.36 pp**），100万仍逊于 expand / lowturn；相对 C0 仅 60万微正；**门锁未进**。

## 对照门锁

| AUM/arm | CAGR∈[12%,18%] | MDD≥−28% | 过门？ |
|---|---|---|---|
| 60万 BOOK | **否**（11.64% < 12%） | **是**（−14.88% ≥ −28%） | **否** |
| 100万 BOOK | **否**（9.76% < 12%） | **是**（−16.71% ≥ −28%） | **否** |

C0 基线仍未过 CAGR 下沿（≈11.27%）。  
**任意 AUM 过门：否（any_pass=false）。** 本结果为研究对照，非过关声称。  
→ **本跑次不标「研究备选」**（过闸才标）。

## vs C0 增量

| AUM | ΔCAGR | ΔMDD |
|---|---|---|
| 60万 | **+0.37 pp**（略胜纯 510300） | **+1.36 pp**（回撤略浅） |
| 100万 | **−1.51 pp**（逊于纯 510300） | **−0.47 pp**（回撤略深） |

解读：60万相对 C0 微正约 **0.37 pp**（八包中与 expand 同属少数跑赢/接近 C0 者）；100万仍亏约 **1.5 pp**；相对门锁下沿 12% 差约 **0.36 pp**（60万）/ **2.24 pp**（100万）。

## 覆盖 / 缺价备注（诚实）

| 项 | 事实 |
|---|---|
| HFQ 外定价 | `run_book` 对 **39** 码调 `load_execution_panels`（**38** 在 HFQ 外）——个股 **可定价**，未 stub 前推补价 |
| target vs actual 码 | X2 BOOK target 非零 **39** 码；actual 成交 **37** 码；**target∉actual：`sh.600519`（63 日×≈4%）、`sz.002371`（23 日×≈4%）** → 两码目标仓未成交（覆盖/成交缺口，非 stub） |
| 表内 510300 | 668 行均在，权重**恒 ≈0.20**（设计压舱，非缺价） |
| 首日 2024-06-03 | target 有仓；actual 自 2024-06-04 起（T+1 执行日历正常），非缺价 |
| fill / gross | fill_ratio≈0.995–0.997；gross_mean≈0.90–0.94（执行后低于目标 1.0；闲置现金约 6–10%；含上述两码未成交贡献） |
| gaps 字段 | 引擎 `gaps=[]`（无结构化缺价列表；码级未成交见上） |

→ **禁止**把缺价/空仓缺口写成 pass；本跑次未用 stub 前推补价；两码 target∉actual **不**抬高 any_pass。

## 机制与候选口径

- 本包是 **叶B：D1 asof 估值残差（行业+市值中性 + 20d 超额正交）**（个股≈0.80 + 510300≈0.20，月频），明确排除裸 EP/BM、残差×份额流、etf_core overlay 与七败/叶A 同构；结构正交声明成立。  
- **满窗 any_pass=false** → **不标研究备选**。  
- 仍 **`promotion_approved=false`** · **不交 Strategy** · **不开密封** · **不下单** · **禁小盘主线**。  
- **handoff=NO**。

## 工程备注

- 模块：`python3 -m quantlab.portfolio.book_smoke`
- JSON：`output/v3/book_smoke_g1g5_d1_val_resid_x2/book_smoke_summary.json`  
  （含 `experiment` / `structure_check` / `weight_coverage_caveat` / `mandate_door` / `vs_baseline_C0` / 对照七包 ΔCAGR / `turnover_note` / `mechanism_note` / `headline` / `any_pass` / `research_candidate`）
- NAV：`output/v3/book_smoke_g1g5_d1_val_resid_x2/aum_{600000,1000000}/X2/{BOOK,C0}/`
- promotion=false；不下单；不交 Strategy；不开密封；未改 Mandate。

## 结论（诚实）

1. **管线通 + 满窗真日更 + 结构核验过**：668 sessions 至 2026-10-09；`n_signals=570`；唯一组合 29；尾长 3；**日均个股≈0.80 / 压舱≈0.20**；**已证伪 stub 前推与 etf_core 0.70 overlay**；非裸 EP/BM。  
2. **换手/成本**：meta mean_one_way≈0.006；账本 cost/AUM≈**1.2%**（月频+压舱，成本为八包最低档之一）。  
3. **相对同窗七包**：60万 CAGR **最强**（11.64%，距门锁仅 0.36 pp）；100万介于 expand/lowturn 与 etf_core 之间。  
4. **相对基线 C0**：60万 **+0.37 pp**；100万 **−1.51 pp**；MDD 60万略浅、100万略深于 C0。  
5. **覆盖缺口**：`600519`/`002371` 共 86 日×≈4% 目标仓未进 actual——诚实记入，不抬 pass。  
6. **研究门锁**：**any_pass=false** → **research_candidate=false**；`promotion=false`；不交 Strategy；**handoff=NO**。  
7. **一句话**：结构正交真跑满窗（个股≈0.80+压舱≈0.20，D1 估值残差月频），成本最低档、60万最贴近门锁且微胜 C0，但仍差下沿约 0.36 pp、100万未进——叶B 本窗不进研究备选。
