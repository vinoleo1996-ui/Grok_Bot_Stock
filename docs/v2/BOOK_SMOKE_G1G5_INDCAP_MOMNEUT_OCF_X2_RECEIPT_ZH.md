# Book-Smoke 回执：G1G5 **叶A 行业硬顶+动量暴露中性·OCF兑现**（`indcap_momneut_ocf_v1`）**X2 满窗** vs 纯 510300

**run_id**：`book_smoke_20261013_110016`  
**strategy_promotion_approved**：`false`  
**sealed_claim**：`false`（不声称过密封线 / 不交 Strategy / 不下单）  
**promotion_approved**：`false`  
**Mandate**：`docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md`（本跑次**未改** Mandate）  
**授权**：Leo 经 New Bot 【派单·叶A Book-Smoke】（可与 Alpha 短裁并行预备）  
**预注册**：`docs/v2/AI_G1G5_INDCAP_MOMNEUT_OCF_WHO_PAYS_PREREG_ZH.md`  
**门锁（Leo 2026-10-12，研究对照非过关）**：净成本 **CAGR ∈ [12%, 18%]** · **MDD 不差于 −28%**  
**结构正交**：已败六包含 100% 股票满仓四包 + ETF-core≈70%/袖套≈30% + 个股≈85%/压舱≈15%；本叶主仓 **纯个股≈1.0**（510300 压舱权重恒 **0**；月频；OCF 兑现选股 + 行业硬顶 + 动量暴露中性，**非**截面动量排序主轴）→ 非 expand 换皮。本满窗未过闸 → **本跑次不标备选**。

## 实验设置

| 项 | 值 |
|---|---|
| 权重长表 | `output/ai_factory/g1g5_indcap_momneut_ocf_daily_weights_20261013_105739.parquet`（**34068** 行 / **668** sessions / **51** 标的） |
| 对照 meta | `output/ai_factory/g1g5_indcap_momneut_ocf_run_meta_20261013_105739.json`（`reaches_x2_end=true` · `stub_window=false` · `stub_forward_fill=false` · G6 pass） |
| mechanism_tag | **`g1g5_ashare_indcap_momneut_ocf_v1`** |
| who_pays | 经营现金流相对净利润的兑现落差（OCF/利润 PIT）在中大盘液态宇宙内被错误定价的对手盘；申万一级单行业硬顶 ≤28%；相对 510300 的 20d 超额动量暴露走廊中性化（≈0±1.5pp） |
| 明确排除 | 截面相对强弱/动量排序主轴；教科书 EP/BM；残差×份额流；ETF-core overlay；四臂摩擦；指数调仓流；**非** expand / friction月频 / lowturn / resid_etf / etf_core / friction_cost_redesign 六包同构 |
| 名义结构 | **纯个股≈1.0** / **510300 压舱≈0.0**（表内含 510300 行但权重恒 0；覆盖充足未落压舱） |
| universe_id | `g1g5_mid_large_liquid_top50` |
| 袖套消费 | `{"core":0.0,"stock":1.0,"alpha_event":0.0}` = **整本账由该长表驱动**；**禁止**再叠 core overlay |
| 对照 | `C0` = 纯 510300 |
| 窗 | 探索窗 **X2** `2024-06-03→2026-10-09` |
| 资金 | 60万 ∧ 100万 |
| 成本 | 开（`ExecConfig.strategy_v1`） |
| 可消费 | stock **book_consumable** rows=**12729** / sessions=**570**（X2∩权重日历=整窗；活跃权重大行 10885） |
| meta 换手 | mean_one_way **≈0.0090**；`n_rebalance_days_nonzero=33`；cadence=`month_end_plus_first`；`n_rebalance_sessions=35` |
| 角色 | 叶A OCF兑现+行业硬顶+动量暴露中性主测（纯个股月频）；对照=已败六包 + 纯 510300 |

## ✅ 满窗日更（无 stub 前推）+ 结构核验

| 核验项 | 结果 |
|---|---|
| 权重日历 | **2024-01-02→2026-10-09**（668 sessions） |
| meta `reaches_x2_end` | **true** |
| meta `stub_forward_fill` / `stub_window` | **false / false** |
| BOOK `n_signals` | **570**（= X2 可消费 sessions） |
| 唯一组合数（X2） | **29**（2024:7 + 2025:13 + 2026:11；跨年去重后 29；月频节奏） |
| 尾段相同组合长度 | **1**（末日才一变，非长尾粘住前推） |
| 日权重合计 | 恒 **1.0** |
| **日均个股权重** | **≈1.0**（min/max 均 ≈1.0） |
| **日均 510300 压舱** | **≈0.0**（权重恒 0） |
| 日均活跃 | ≈19 只（min 17 / max 20） |
| 未滑向 etf_core 0.70 | **是**（压舱恒 0；无行业 ETF 持仓；禁 overlay） |
| 未退化为 expand 动量选股主轴 | **是**（预注册口径：动量仅作暴露走廊中性化；选股主轴=OCF/利润 PIT） |
| 未双计 510300 overlay | **是**（sleeves.core=0；表内压舱权重恒 0） |

→ **禁止**再写「后半持仓前推」或「滑向 etf_core / expand 动量主轴」。本回执是**真实满窗月频再平衡 + 纯个股 OCF 账**结果。

## 数字表（探索窗满窗；成本开；非密封）

| AUM | arm | CAGR | vs C0 | MDD | Sharpe | cost/AUM | target_weight 行数 |
|---|---|---|---|---|---|---|---|
| 600000 | X2/BOOK | **8.61%** (0.0861) | **−2.66 pp** | **−14.60%** | 0.641 | **0.0161** | 10885 |
| 600000 | X2/C0 | **11.27%** (0.1127) | — | −16.24% | 0.651 | 0.0002 | 570 |
| 1000000 | X2/BOOK | **8.10%** (0.0810) | **−3.17 pp** | **−15.98%** | 0.593 | **0.0150** | 10885 |
| 1000000 | X2/C0 | **11.27%** (0.1127) | — | −16.24% | 0.651 | 0.0002 | 570 |

起止：`2024-06-03→2026-10-09`。BOOK `n_codes=32`（引擎计数；X2 活跃个股唯一码 **31**），`n_signals=**570**`，`gross_mean≈0.91`（60万）/ `≈0.95`（100万），`fill_ratio≈0.99` / `0.98`。

## 七包对照表（同窗 X2 满窗）

| | **本包 叶A OCF+行业硬顶+动量中性** | 摩擦降成本再设计 | ETF-core+袖套 | 残差×ETF | 降换手 | 月频制度摩擦 | 动量扩池 |
|---|---|---|---|---|---|---|---|
| mechanism | `…_indcap_momneut_ocf_v1` | `…_friction_cost_redesign_v1` | `…_etf_core_sleeve_v1` | `…_resid_etf_flow_v1` | `…_friction_v1_lowturn` | `…_friction_v1` | `…_expand` |
| 持仓形态 | **纯个股≈100%** | 个股≈85%+510300≈15% | ETF≈70%+个股≈30% | 100% 股票 | 100% 股票 | 100% 股票 | 100% 股票 |
| 再平衡 | **月频** | 半月 | 月频 | 月频 top20 | 季末+粘性 | 月频 top20 | 月频 top20 |
| 60万 BOOK CAGR/MDD | **8.61% / −14.60%** | 6.03% / −16.06% | 8.46% / −20.39% | 5.25% / −14.92% | 10.13% / −17.86% | 8.24% / −13.95% | 11.37% / −15.15% |
| 100万 BOOK CAGR/MDD | **8.10% / −15.98%** | 6.74% / −15.79% | 9.43% / −20.05% | 5.52% / −14.74% | 10.21% / −17.90% | 9.61% / −13.02% | 11.42% / −15.88% |
| 60万 cost/AUM | **0.0161** | 0.0380 | 0.0369 | 0.0254 | 0.0136 | 0.0264 | 0.0284 |
| 100万 cost/AUM | **0.0150** | 0.0407 | 0.0438 | 0.0277 | 0.0147 | 0.0283 | 0.0307 |
| vs C0 ΔCAGR（60/100） | **−2.66 / −3.17 pp** | −5.23 / −4.53 | −2.81 / −1.84 | −6.01 / −5.75 | −1.13 / −1.06 | −3.03 / −1.66 | +0.11 / +0.15 |
| any_pass | **false** | false | false | false | false | false | false |

回执对照：`docs/v2/BOOK_SMOKE_G1G5_FRICTION_COST_REDESIGN_X2_RECEIPT_ZH.md` · `docs/v2/BOOK_SMOKE_G1G5_ETF_CORE_SLEEVE_X2_RECEIPT_ZH.md` · `docs/v2/BOOK_SMOKE_G1G5_RESID_ETF_X2_RECEIPT_ZH.md` · `docs/v2/BOOK_SMOKE_G1G5_LOWTURN_X2_RECEIPT_ZH.md` · `docs/v2/BOOK_SMOKE_G1G5_NONTEXTBOOK_X2_RECEIPT_ZH.md` · `docs/v2/BOOK_SMOKE_G1G5_EXPAND_X2_RECEIPT_ZH.md`

### 相对同窗包：结构正交是否换来 alpha？

| 对照 | 60万 ΔCAGR | 100万 ΔCAGR | 解读 |
|---|---|---|---|
| vs 动量扩池 | **−2.76 pp** | **−3.32 pp** | 逊于动量满窗 |
| vs 月频制度摩擦 | **+0.37 pp** | **−1.51 pp** | 60万略强、100万逊于已败月频摩擦 |
| vs 降换手 | **−1.52 pp** | **−2.11 pp** | 逊于已降成本摩擦变体 |
| vs ETF-core+袖套 | **+0.15 pp** | **−1.33 pp** | 60万持平略强、100万逊于 ETF-core |
| vs 残差×ETF | **+3.36 pp** | **+2.58 pp** | 强于残差×ETF，仍未过门锁 |
| vs 摩擦降成本再设计 | **+2.58 pp** | **+1.36 pp** | 强于半月摩擦再设计 |
| vs C0 | **−2.66 pp** | **−3.17 pp** | 两端跑输纯 510300 |
| cost/AUM | ≈0.015–0.016 | 低于多数摩擦包 | meta 换手≈0.009（月频）账本成本偏低 |

诚实结论：**结构正交声明成立（纯个股≈1.0；月频；OCF 主轴 + 行业硬顶 + 动量暴露中性；非 expand / 非 etf_core）**，CAGR 强于 friction_cost / resid_etf，接近 etf_core（60万）与 friction月频（60万），但相对 expand / lowturn / C0 仍负，**门锁未进**。

## 对照门锁

| AUM/arm | CAGR∈[12%,18%] | MDD≥−28% | 过门？ |
|---|---|---|---|
| 60万 BOOK | **否**（8.61% < 12%） | **是**（−14.60% ≥ −28%） | **否** |
| 100万 BOOK | **否**（8.10% < 12%） | **是**（−15.98% ≥ −28%） | **否** |

C0 基线仍未过 CAGR 下沿（≈11.27%）。  
**任意 AUM 过门：否（any_pass=false）。** 本结果为研究对照，非过关声称。  
→ **本跑次不标「研究备选」**（过闸才标）。

## vs C0 增量

| AUM | ΔCAGR | ΔMDD |
|---|---|---|
| 60万 | **−2.66 pp**（逊于纯 510300） | **+1.64 pp**（回撤略浅） |
| 100万 | **−3.17 pp**（逊于纯 510300） | **+0.26 pp**（回撤略浅） |

解读：相对 C0 亏收益约 **2.7–3.2 pp**；回撤略浅于 C0；相对门锁下沿 12% 差约 **3.4–3.9 pp**。

## 覆盖 / 缺价备注（诚实）

| 项 | 事实 |
|---|---|
| HFQ 外定价 | `run_book` 对 **32** 码调 `load_execution_panels`（**31** 在 HFQ 外）——个股 **可定价**，未 stub 前推补价 |
| target vs actual 码 | X2 BOOK target **31** 码 == actual **31** 码；**无** target∉actual 成交缺口 |
| 表内 510300 | 668 行均在，权重**恒 0**（覆盖充足未落压舱；非缺价） |
| 首日 2024-06-03 | target 有仓；actual 自 2024-06-04 起（T+1 执行日历正常），非缺价 |
| fill / gross | fill_ratio≈0.99–0.98；gross_mean≈0.91–0.95（执行后低于目标 1.0；闲置现金约 5–9%） |
| gaps 字段 | 引擎 `gaps=[]`（无结构化缺价列表） |

→ **禁止**把缺价/空仓缺口写成 pass；本跑次未用 stub 前推补价。

## 机制与候选口径

- 本包是 **叶A：OCF/利润 PIT 兑现落差 + 申万一级行业硬顶 + 相对 510300 动量暴露走廊中性化**（纯个股≈1.0，月频），明确排除截面动量排序主轴与六包同构；结构正交声明成立。  
- **满窗 any_pass=false** → **不标研究备选**。  
- 仍 **`promotion_approved=false`** · **不交 Strategy** · **不开密封** · **不下单** · **禁小盘主线**。  
- **handoff=NO**。

## 工程备注

- 模块：`python3 -m quantlab.portfolio.book_smoke`
- JSON：`output/v3/book_smoke_g1g5_indcap_momneut_ocf_x2/book_smoke_summary.json`  
  （含 `experiment` / `structure_check` / `weight_coverage_caveat` / `mandate_door` / `vs_baseline_C0` / 对照六包 ΔCAGR / `turnover_note` / `mechanism_note` / `headline` / `any_pass` / `research_candidate`）
- NAV：`output/v3/book_smoke_g1g5_indcap_momneut_ocf_x2/aum_{600000,1000000}/X2/{BOOK,C0}/`
- promotion=false；不下单；不交 Strategy；不开密封；未改 Mandate。

## 结论（诚实）

1. **管线通 + 满窗真日更 + 结构核验过**：668 sessions 至 2026-10-09；`n_signals=570`；唯一组合 29；尾长 1；**日均个股≈1.0 / 压舱≈0.0**；**已证伪 stub 前推与 etf_core overlay**。  
2. **换手/成本**：meta mean_one_way≈0.009；账本 cost/AUM≈**1.5–1.6%**（月频低换手，成本低于多数摩擦包）。  
3. **相对同窗六包**：强于 friction_cost / resid_etf；接近 etf_core（60万）与 friction月频（60万）；逊于 expand / lowturn。  
4. **相对基线 C0**：两端约 **−2.66～−3.17 pp**；MDD 略浅于 C0。  
5. **研究门锁**：**any_pass=false** → **research_candidate=false**；`promotion=false`；不交 Strategy；**handoff=NO**。  
6. **一句话**：结构正交真跑满窗（纯个股 OCF+行业硬顶+动量暴露中性，月频），成本偏低，但门锁没进、相对 C0 仍负——叶A 本窗不进研究备选。
