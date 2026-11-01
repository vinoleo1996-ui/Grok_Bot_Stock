# Book-Smoke 回执：G1G5 **北向叶 northbound_flow**（`northbound_flow_v1`）**X2 满窗** vs 纯 510300

**run_id**：`book_smoke_20261013_111630`  
**strategy_promotion_approved**：`false`  
**sealed_claim**：`false`（不声称过密封线 / 不交 Strategy / 不下单）  
**promotion_approved**：`false`  
**Mandate**：`docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md`（本跑次**未改** Mandate）  
**授权**：Leo 经 New Bot 【派单·北向叶 Book-Smoke】容量叶跑完后立刻串行满窗  
**预注册**：`docs/v2/AI_G1G5_NORTHBOUND_FLOW_WHO_PAYS_PREREG_ZH.md`  
**门锁（Leo 2026-10-12，研究对照非过关）**：净成本 **CAGR ∈ [12%, 18%]** · **MDD 不差于 −28%**  
**结构正交**：已败九包 + 叶A/叶B + **容量叶（刚过门）**；本叶主仓 **个股≈0.76 + 510300 压舱≈0.24**（北向持股变化流 / hk_hold 断档两融补窗；月频；**非**估值残差 / OCF / 动量 / 四臂摩擦 / etf_core 0.70 / ADV 容量硬顶）→ 非容量叶换皮。本满窗 **两端均未过 CAGR 下沿** → **any_pass=false**；**不标研究备选**；仍 **promotion=false / 不交 Strategy / handoff=NO**。

## 实验设置

| 项 | 值 |
|---|---|
| 权重长表 | `output/ai_factory/g1g5_northbound_flow_daily_weights_20261013_111252.parquet`（**34068** 行 / **668** sessions / **51** 标的） |
| 对照 meta | `output/ai_factory/g1g5_northbound_flow_run_meta_20261013_111252.json`（`stub_window=false` · `stub_forward_fill=false` · `n_rebalance_sessions=35` · `mean_stock_share≈0.767` · `mean_ballast_share≈0.233`） |
| mechanism_tag | **`g1g5_ashare_northbound_flow_v1`** |
| who_pays | 北向配置流：沪深港通北向对个股的边际增持与持股占比上升由境外配置与被动跟踪资金支付相对 510300 的持有窗；本叶吃持股变化与流入的对手盘；hk_hold 断档后再平衡日以两融融资余额变化作同族补窗 |
| 明确排除 | 估值残差/裸 EP/BM；OCF 兑现；截面相对强弱主轴；四臂摩擦/解禁/份额流/调仓；ETF-core overlay；ADV 容量硬顶换皮；小盘主线；stub 前推 |
| 名义结构 | **个股≈0.76** / **510300 压舱≈0.24**（X2 日均；压舱可升至 0.56，共 146/570 日 >0.25） |
| universe_id | `g1g5_mid_large_liquid_top50` |
| 袖套消费 | `{"core":0.0,"stock":1.0,"alpha_event":0.0}` = **整本账由该长表驱动**；表内已含压舱 → **禁止**再叠 core overlay |
| 对照 | `C0` = 纯 510300 |
| 窗 | 探索窗 **X2** `2024-06-03→2026-10-09` |
| 资金 | 60万 ∧ 100万 |
| 成本 | 开（`ExecConfig.strategy_v1`） |
| 可消费 | stock **book_consumable** rows=**13475** / sessions=**570**（X2∩权重日历=整窗；活跃权重大行 11417） |
| meta 换手 | mean_one_way **≈0.0236**；`n_rebalance_days_nonzero=34`；cadence=`month_end_plus_first_last`；`n_rebalance_sessions=35` |
| 角色 | 北向持股变化流主测；对照=**容量叶（刚过门）** + 叶B + 叶A + 已败包 + 纯 510300 |

## ✅ 满窗日更（无 stub 前推）+ 结构核验

| 核验项 | 结果 |
|---|---|
| 权重日历 | **2024-01-02→2026-10-09**（668 sessions） |
| meta `stub_forward_fill` / `stub_window` | **false / false** |
| BOOK `n_signals` | **570**（= X2 可消费 sessions） |
| 唯一组合数（X2） | **27**（2024:8 + 2025:11 + 2026:11；月频节奏） |
| 尾段相同组合长度 | **1**（末日无长尾 stub 前推） |
| 日权重合计 | 恒 **1.0** |
| **日均个股权重（X2）** | **≈0.761**（min≈0.44 / max≈0.80） |
| **日均 510300 压舱（X2）** | **≈0.239**（min≈0.20 / max≈0.56；146/570 日 >0.25） |
| 日均活跃个股 | **≈19.0**（min 11 / max 20） |
| 单名顶 | **≤0.04**（观测 max=0.04） |
| 未滑向 etf_core 0.70 | **是**（压舱仅宽基 510300≈0.24；无行业 ETF；禁 overlay） |
| 非估值残差 / 非 OCF / 非动量 / 非 ADV 容量硬顶 | **是**（预注册口径：北向持股变化 + 两融断档补窗） |
| 未双计 510300 overlay | **是**（sleeves.core=0；压舱仅来自表内） |

→ **禁止**再写「后半持仓前推」或「滑向 etf_core 0.70 / 容量叶换皮」。本回执是**真实满窗月频再平衡 + 个股≈0.76/压舱≈0.24 北向流账**结果。

## 数字表（探索窗满窗；成本开；非密封）

| AUM | arm | CAGR | vs C0 | MDD | Sharpe | cost/AUM | target_weight 行数 |
|---|---|---|---|---|---|---|---|
| 600000 | X2/BOOK | **11.08%** (0.1108) | **−0.19 pp** | **−14.38%** | 0.787 | **0.0237** | 11417 |
| 600000 | X2/C0 | **11.27%** (0.1127) | — | −16.24% | 0.651 | 0.0002 | 570 |
| 1000000 | X2/BOOK | **10.95%** (0.1095) | **−0.32 pp** | **−13.80%** | 0.758 | **0.0247** | 11417 |
| 1000000 | X2/C0 | **11.27%** (0.1127) | — | −16.24% | 0.651 | 0.0002 | 570 |

起止：`2024-06-03→2026-10-09`。BOOK `n_codes=51`（引擎计数；X2 target 非零 **51** 码含 510300，其中个股 **50**；actual 成交 **49** 码，**target∉actual=[sh.600519, sz.002371]**），`n_signals=**570**`，`gross_mean≈0.89`（60万）/ `≈0.94`（100万），`fill_ratio≈0.977` / `0.948`。

## 对照表（同窗 X2 满窗；本包 + **容量叶** + 叶B + 叶A + 关键已败包）

| | **本包 北向流** | **容量ADV（刚过门）** | 叶B D1估值残差 | 叶A OCF+行业硬顶+动量中性 | 动量扩池 | 降换手 |
|---|---|---|---|---|---|---|
| mechanism | `…_northbound_flow_v1` | `…_capacity_adv_v1` | `…_d1_val_resid_v1` | `…_indcap_momneut_ocf_v1` | `…_expand` | `…_friction_v1_lowturn` |
| 持仓形态 | **个股≈76%+510300≈24%** | **个股≈79%+510300≈21%** | 个股≈80%+510300≈20% | 纯个股≈100% | 100% 股票 | 100% 股票 |
| 再平衡 | **月频** | 月频 | 月频 | 月频 | 月频 top20 | 季末+粘性 |
| 60万 BOOK CAGR/MDD | **11.08% / −14.38%** | **13.82% / −10.07%** | 11.64% / −14.88% | 8.61% / −14.60% | 11.37% / −15.15% | 10.13% / −17.86% |
| 100万 BOOK CAGR/MDD | **10.95% / −13.80%** | **12.23% / −11.62%** | 9.76% / −16.71% | 8.10% / −15.98% | 11.42% / −15.88% | 10.21% / −17.90% |
| 60万 cost/AUM | **0.0237** | **0.0172** | 0.0120 | 0.0161 | 0.0284 | 0.0136 |
| 100万 cost/AUM | **0.0247** | **0.0171** | 0.0120 | 0.0150 | 0.0307 | 0.0147 |
| vs C0 ΔCAGR（60/100） | **−0.19 / −0.32 pp** | **+2.56 / +0.97 pp** | +0.37 / −1.51 | −2.66 / −3.17 | +0.11 / +0.15 | −1.13 / −1.06 |
| any_pass | **false** | **true** | false | false | false | false |

回执对照：`docs/v2/BOOK_SMOKE_G1G5_CAPACITY_ADV_X2_RECEIPT_ZH.md` · `docs/v2/BOOK_SMOKE_G1G5_D1_VAL_RESID_X2_RECEIPT_ZH.md` · `docs/v2/BOOK_SMOKE_G1G5_INDCAP_MOMNEUT_OCF_X2_RECEIPT_ZH.md` · `docs/v2/BOOK_SMOKE_G1G5_EXPAND_X2_RECEIPT_ZH.md` · `docs/v2/BOOK_SMOKE_G1G5_LOWTURN_X2_RECEIPT_ZH.md`

### 相对容量叶：北向流是否追上刚过门包？

| 对照 | 60万 ΔCAGR | 100万 ΔCAGR | 解读 |
|---|---|---|---|
| vs 容量 ADV | **−2.74 pp** | **−1.28 pp** | 两端均弱于刚过门的容量叶；未进 12% 下沿 |
| vs 叶B D1估值残差 | **−0.56 pp** | **+1.19 pp** | 60万略弱于叶B；100万强于叶B，但仍未过门 |
| vs C0 | **−0.19 pp** | **−0.32 pp** | **两端均略负于纯 510300**（容量叶两端为正） |
| cost/AUM | ≈0.024 | 高于容量叶 ≈0.017 | meta 换手≈0.0236（高于容量叶≈0.0125）；账本成本仍低于半月摩擦再设计 |

诚实结论：**结构正交声明成立（北向持股变化流；个股≈0.76/压舱≈0.24；月频；非容量/估值/OCF 换皮）**；但本窗 **两端 CAGR 均未进 [12%,18%]**，且相对 C0 同向略负——**不标研究备选**。

## 对照门锁

| AUM/arm | CAGR∈[12%,18%] | MDD≥−28% | 过门？ |
|---|---|---|---|
| 60万 BOOK | **否**（11.08% < 12%） | **是**（−14.38% ≥ −28%） | **否** |
| 100万 BOOK | **否**（10.95% < 12%） | **是**（−13.80% ≥ −28%） | **否** |

C0 基线仍未过 CAGR 下沿（≈11.27%）。  
**任意 AUM 过门：否（any_pass=false）。** **两端同向过门：否（both_aum_pass=false）。**  
→ **不标「研究备选」（research_candidate=false）**；仍为研究对照，**非** promotion / 密封 / Strategy 授权。

距 12% 下沿：60万约 **−0.92 pp**；100万约 **−1.05 pp**。

## vs C0 增量

| AUM | ΔCAGR | ΔMDD |
|---|---|---|
| 60万 | **−0.19 pp**（略负于纯 510300） | **+1.86 pp**（回撤略浅） |
| 100万 | **−0.32 pp**（略负于纯 510300） | **+2.44 pp**（回撤略浅） |

## vs 容量叶（刚过门）增量

| AUM | ΔCAGR vs capacity_adv | ΔMDD vs capacity_adv |
|---|---|---|
| 60万 | **−2.74 pp** | **−4.31 pp**（回撤更深） |
| 100万 | **−1.28 pp** | **−2.18 pp**（回撤更深） |

## 覆盖 / 缺价备注（诚实）

| 项 | 事实 |
|---|---|
| HFQ 外定价 | `run_book` 对 **51** 码调 `load_execution_panels`（**50** 在 HFQ 外）——多数个股可定价；未 stub 前推补价 |
| target vs actual 码 | X2 BOOK target 非零 **51** 码；actual 成交 **49** 码；**target∉actual：[`sh.600519`, `sz.002371`]** |
| `600519` | 目标 **219** 日 ×≈4% **零成交**（与叶B 同类巨头缺口；容量叶靠硬排除消除） |
| `002371` | 目标 **318** 日 ×≈4% **零成交** |
| 表内 510300 | 668 行均在；X2 日均权重 **≈0.24**（高日可至 0.56） |
| 首日 2024-06-03 | target 有仓；actual 自 2024-06-04 起（T+1 执行日历正常），非缺价 |
| fill / gross | fill_ratio≈0.977（60万）/ 0.948（100万）；gross_mean≈0.89–0.94（执行后低于目标 1.0；闲置现金约 6–11%） |
| gaps 字段 | 引擎 `gaps=[]` |
| hk_hold 断档 | 预注册写死：密窗约至 2024-08、稀疏至 2025-06-30 后无个股持股行；断档再平衡日用两融 Δrzye 补窗（tag 仍 northbound_flow）——**不**把补窗写成独立主叶过门 |

→ **禁止**把缺价/空仓缺口写成 pass；本跑次未用 stub 前推补价；`600519`/`002371` 目标仓未成交属真实覆盖缺口，**不**虚构成交。

## 机制与候选口径

- 本包是 **北向叶：持股变化流**（个股≈0.76 + 510300≈0.24，月频，断档两融补窗），明确排除估值残差/OCF/动量/四臂/etf_core overlay/ADV 容量硬顶与已败同构；结构正交声明成立。  
- **满窗 any_pass=false** → **不标研究备选（research_candidate=false）**。  
- 仍 **`promotion_approved=false`** · **不交 Strategy** · **不开密封** · **不下单** · **禁小盘主线**。  
- **handoff=NO**。

## 工程备注

- 模块：`python3 -m quantlab.portfolio.book_smoke`
- JSON：`output/v3/book_smoke_g1g5_northbound_flow_x2/book_smoke_summary.json`  
  （含 `mechanism_note` / `mandate_door` / `vs_baseline_C0` / `structure_check` / `any_pass` / `research_candidate` / `vs_capacity_adv` / `weight_coverage_caveat` / `headline`）
- NAV：`output/v3/book_smoke_g1g5_northbound_flow_x2/aum_{600000,1000000}/X2/{BOOK,C0}/`
- promotion=false；不下单；不交 Strategy；不开密封；未改 Mandate。

## 结论（诚实）

1. **管线通 + 满窗真日更 + 结构核验过**：668 sessions 至 2026-10-09；`n_signals=570`；唯一组合 27；尾长 1；**日均个股≈0.76 / 压舱≈0.24**；**已证伪 stub 前推与 etf_core 0.70 overlay**。  
2. **换手/成本**：meta mean_one_way≈0.0236；账本 cost/AUM≈**2.37%/2.47%**（高于容量叶与叶B）。  
3. **相对容量叶（刚过门）**：60万 **−2.74 pp**、100万 **−1.28 pp**——未追上。  
4. **相对基线 C0**：60万 **−0.19 pp**；100万 **−0.32 pp**；MDD 两端略浅于 C0，但 CAGR 两端略负。  
5. **覆盖缺口**：`600519` 219 日×≈4% 未成交；`002371` 318 日×≈4% 未成交（与叶B 同类；**不**写成 pass）。  
6. **研究门锁**：**any_pass=false** → **research_candidate=false**；`promotion=false`；不交 Strategy；**handoff=NO**。  
7. **一句话**：北向持股变化流真跑满窗（个股≈0.76+压舱≈0.24），**两端 MDD 过门锁但 CAGR 均未进 12% 下沿且略负于 C0**——不标研究备选，不晋级、不交 Strategy。
