# Book-Smoke 回执：G1G5 **摩擦降成本再设计**（`friction_cost_redesign_v1`）**X2 满窗** vs 纯 510300

**run_id**：`book_smoke_20261012_214602`  
**strategy_promotion_approved**：`false`  
**sealed_claim**：`false`（不声称过密封线 / 不交 Strategy / 不下单）  
**promotion_approved**：`false`  
**Mandate**：`docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md`（本跑次**未改** Mandate）  
**授权**：Leo 经 New Bot 【派工|Book-Smoke|研究级】下一叶摩擦降成本再设计  
**预注册**：`docs/v2/AI_G1G5_FRICTION_COST_REDESIGN_WHO_PAYS_PREREG_ZH.md`  
**门锁（Leo 2026-10-12，研究对照非过关）**：净成本 **CAGR ∈ [12%, 18%]** · **MDD 不差于 −28%**  
**结构正交**：已败五包含 100% 股票满仓四包 + ETF-core≈70%/袖套≈30%；本叶主仓 **个股≈0.85** + 宽基压舱 **510300≈0.15**（半月再平衡；禁 etf_core overlay；禁 lowturn 季末+进12/出28）→ 非换皮。本满窗未过闸 → **本跑次不标备选**。

## 实验设置

| 项 | 值 |
|---|---|
| 权重长表 | `output/ai_factory/g1g5_friction_cost_redesign_daily_weights_20261012_214334.parquet`（**34068** 行 / **668** sessions / **51** 标的） |
| 对照 meta | `output/ai_factory/g1g5_friction_cost_redesign_run_meta_20261012_214334.json`（`reaches_x2_end=true` · `stub_window=false` · `stub_forward_fill=false` · G6 pass） |
| mechanism_tag | **`g1g5_ashare_friction_cost_redesign_v1`** |
| who_pays | 解禁公告窗供给冲击残差对手盘 + 行业ETF创设/赎回份额流转映射到成分股的配置对手盘；D1 换手/流通市值 asof 容量匹配 + 单票硬顶压冲击；砍掉 T+1/涨跌停高换手臂 |
| 明确排除 | 教科书相对强弱/估值主线；**非** expand / friction月频 / lowturn / resid_etf / etf_core 五包同构 |
| 名义结构 | **个股≈0.85**（慢制度两臂 top≤20，流通市值×流动性缩放，L≤5%） / **510300 压舱≈0.15** |
| universe_id | `g1g5_mid_large_liquid_top50` |
| 袖套消费 | `{"core":0.0,"stock":1.0,"alpha_event":0.0}` = **整本账由该混合长表驱动**（表内已含个股+510300）；**禁止**再叠 core overlay；**禁止**过滤掉 510300 只留个股 |
| 对照 | `C0` = 纯 510300 |
| 窗 | 探索窗 **X2** `2024-06-03→2026-10-09` |
| 资金 | 60万 ∧ 100万 |
| 成本 | 开（`ExecConfig.strategy_v1`） |
| 可消费 | stock **book_consumable** rows=**14028** / sessions=**570**（X2∩权重日历=整窗；活跃权重大行 11970） |
| meta 换手 | mean_one_way **≈0.0462**；`n_rebalance_days_nonzero=67`；cadence=`biweekly_step_10_plus_first_last`；`n_rebalance_sessions=68` |
| 角色 | 摩擦降成本再设计主测（个股≈0.85+压舱≈0.15，半月）；对照=已败五包 + 纯 510300 |

## ✅ 满窗日更（无 stub 前推）+ 结构核验

| 核验项 | 结果 |
|---|---|
| 权重日历 | **2024-01-02→2026-10-09**（668 sessions） |
| meta `reaches_x2_end` | **true** |
| meta `stub_forward_fill` / `stub_window` | **false / false** |
| BOOK `n_signals` | **570**（= X2 可消费 sessions） |
| 唯一组合数（X2） | **59**（2024:16 + 2025:25 + 2026:20；跨年去重后 59；半月节奏） |
| 尾段相同组合长度 | **1**（末日才一变，非长尾粘住前推） |
| 日权重合计 | 恒 **1.0** |
| **日均个股权重** | **≈0.85**（min/max 均 ≈0.85） |
| **日均 510300 压舱** | **≈0.15**（min/max 均 ≈0.15） |
| 日均活跃 | 总 ≈21 只（个股 ≈20 + 压舱 1） |
| 未滑向 etf_core 0.70 | **是**（压舱恒 0.15≪0.25；无行业 ETF 持仓） |
| 未复刻 lowturn 季末+进12/出28 | **是**（`not_lowturn_params`：`no_quarter_end_only` / `no_enter12_exit28`；半月 step=10） |
| 未双计 510300 overlay | **是**（sleeves.core=0；表内已含压舱） |

→ **禁止**再写「后半持仓前推」或「滑向 etf_core / lowturn」。本回执是**真实满窗半月再平衡 + 个股/压舱混合结构**结果。

## 数字表（探索窗满窗；成本开；非密封）

| AUM | arm | CAGR | vs C0 | MDD | Sharpe | cost/AUM | target_weight 行数 |
|---|---|---|---|---|---|---|---|
| 600000 | X2/BOOK | **6.03%** (0.0603) | **−5.23 pp** | **−16.06%** | 0.469 | **0.0380** | 11970 |
| 600000 | X2/C0 | **11.27%** (0.1127) | — | -16.24% | 0.651 | 0.0002 | 570 |
| 1000000 | X2/BOOK | **6.74%** (0.0674) | **−4.53 pp** | **−15.79%** | 0.498 | **0.0407** | 11970 |
| 1000000 | X2/C0 | **11.27%** (0.1127) | — | -16.24% | 0.651 | 0.0002 | 570 |

起止：`2024-06-03→2026-10-09`。BOOK `n_codes=51`，`n_signals=**570**`，`gross_mean≈0.89`（60万）/ `≈0.93`（100万），`fill_ratio≈0.96` / `0.97`。

## 六包对照表（同窗 X2 满窗）

| | **本包 摩擦降成本再设计** | ETF-core+袖套 | 残差×ETF | 降换手 | 月频制度摩擦 | 动量扩池 |
|---|---|---|---|---|---|---|
| mechanism | `…_friction_cost_redesign_v1` | `…_etf_core_sleeve_v1` | `…_resid_etf_flow_v1` | `…_friction_v1_lowturn` | `…_friction_v1` | `…_expand` |
| 持仓形态 | **个股≈85%+510300≈15%** | ETF≈70%+个股≈30% | 100% 股票 | 100% 股票 | 100% 股票 | 100% 股票 |
| 再平衡 | **半月** | 月频 | 月频 top20 | 季末+粘性 | 月频 top20 | 月频 top20 |
| 60万 BOOK CAGR/MDD | **6.03% / −16.06%** | 8.46% / −20.39% | 5.25% / −14.92% | 10.13% / −17.86% | 8.24% / −13.95% | 11.37% / −15.15% |
| 100万 BOOK CAGR/MDD | **6.74% / −15.79%** | 9.43% / −20.05% | 5.52% / −14.74% | 10.21% / −17.90% | 9.61% / −13.02% | 11.42% / −15.88% |
| 60万 cost/AUM | **0.0380** | 0.0369 | 0.0254 | 0.0136 | 0.0264 | 0.0284 |
| 100万 cost/AUM | **0.0407** | 0.0438 | 0.0277 | 0.0147 | 0.0283 | 0.0307 |
| vs C0 ΔCAGR（60/100） | **−5.23 / −4.53 pp** | −2.81 / −1.84 pp | −6.01 / −5.75 pp | −1.13 / −1.06 pp | −3.03 / −1.66 pp | +0.11 / +0.15 pp |
| any_pass | **false** | false | false | false | false | false |

回执对照：`docs/v2/BOOK_SMOKE_G1G5_ETF_CORE_SLEEVE_X2_RECEIPT_ZH.md` · `docs/v2/BOOK_SMOKE_G1G5_RESID_ETF_X2_RECEIPT_ZH.md` · `docs/v2/BOOK_SMOKE_G1G5_LOWTURN_X2_RECEIPT_ZH.md` · `docs/v2/BOOK_SMOKE_G1G5_NONTEXTBOOK_X2_RECEIPT_ZH.md` · `docs/v2/BOOK_SMOKE_G1G5_EXPAND_X2_RECEIPT_ZH.md`

### 相对同窗包：结构正交是否换来 alpha？

| 对照 | 60万 ΔCAGR | 100万 ΔCAGR | 解读 |
|---|---|---|---|
| vs 动量扩池 | **−5.34 pp** | **−4.68 pp** | 明显逊于动量满窗 |
| vs 月频制度摩擦 | **−2.21 pp** | **−2.87 pp** | 逊于已败月频摩擦 |
| vs 降换手 | **−4.10 pp** | **−3.47 pp** | 逊于已降成本摩擦变体 |
| vs ETF-core+袖套 | **−2.43 pp** | **−2.69 pp** | 逊于 ETF-core 结构 |
| vs 残差×ETF | **+0.78 pp** | **+1.22 pp** | 略强于残差×ETF，但仍未过门锁 |
| vs C0 | **−5.23 pp** | **−4.53 pp** | 两端明显跑输纯 510300 |
| cost/AUM | ≈0.038–0.041 | 与 etf_core 同量级 | meta 换手≈0.046（半月）高于月频包，账本成本偏高 |

诚实结论：**结构正交声明成立（个股≈0.85+压舱≈0.15；半月；非 etf_core / 非 lowturn）**，CAGR 仅略强于残差×ETF，相对其余四包与 C0 均负，成本偏高，**门锁未进**。

## 对照门锁

| AUM/arm | CAGR∈[12%,18%] | MDD≥−28% | 过门？ |
|---|---|---|---|
| 60万 BOOK | **否**（6.03% < 12%） | **是**（−16.06% ≥ −28%） | **否** |
| 100万 BOOK | **否**（6.74% < 12%） | **是**（−15.79% ≥ −28%） | **否** |

C0 基线仍未过 CAGR 下沿（≈11.27%）。  
**任意 AUM 过门：否（any_pass=false）。** 本结果为研究对照，非过关声称。  
→ **本跑次不标「研究备选」**（过闸才标）。

## vs C0 增量

| AUM | ΔCAGR | ΔMDD |
|---|---|---|
| 60万 | **−5.23 pp**（逊于纯 510300） | **+0.18 pp**（回撤略浅） |
| 100万 | **−4.53 pp**（逊于纯 510300） | **+0.45 pp**（回撤略浅） |

解读：相对 C0 明显亏收益；回撤略浅于 C0，但相对门锁下沿 12% 差约 **5.3–6.0 pp**。

## 覆盖 / 缺价备注（诚实）

| 项 | 事实 |
|---|---|
| HFQ 外定价 | `run_book` 对 **51** 码调 `load_execution_panels`（**50** 在 HFQ 外）——个股+510300 **可定价**，未 stub 前推补价 |
| `sh.600519` / `sz.002371` | 出现在 target，**未进入 actual**（两票未成交缺口） |
| 首日 2024-06-03 | actual 空仓（T+1 执行日历正常），非缺价；actual 自 2024-06-04 起 |
| fill / gross | fill_ratio≈0.96–0.97；gross_mean≈0.89–0.93（执行后低于目标 1.0；闲置现金约 7–11%） |
| gaps 字段 | 引擎 `gaps=[]`（无结构化缺价列表） |

→ **禁止**把缺价/空仓缺口写成 pass；本跑次未用 stub 前推补价。

## 机制与候选口径

- 本包是 **摩擦降成本再设计**（解禁残差 + 行业ETF份额流→成分股；砍 T+1/涨跌停；半月再平衡；个股≈0.85 + 510300≈0.15），明确排除教科书相对强弱/估值，也**不是**五包同构；结构正交声明成立。  
- **满窗 any_pass=false** → **不标研究备选**。  
- 仍 **`promotion_approved=false`** · **不交 Strategy** · **不开密封** · **不下单** · **禁小盘主线**。  
- **handoff=NO**。

## 工程备注

- 模块：`python3 -m quantlab.portfolio.book_smoke`
- JSON：`output/v3/book_smoke_g1g5_friction_cost_redesign_x2/book_smoke_summary.json`  
  （含 `experiment` / `structure_check` / `weight_coverage_caveat` / `mandate_door` / `vs_baseline_C0` / 对照五包字段 / `turnover_note` / `mechanism_note` / `headline`）
- NAV：`output/v3/book_smoke_g1g5_friction_cost_redesign_x2/aum_{600000,1000000}/X2/{BOOK,C0}/`
- promotion=false；不下单；不交 Strategy；不开密封；未改 Mandate。

## 结论（诚实）

1. **管线通 + 满窗真日更 + 结构核验过**：668 sessions 至 2026-10-09；`n_signals=570`；唯一组合 59；尾长 1；**日均个股≈0.85 / 压舱≈0.15**；**已证伪 stub 前推、etf_core 滑移与 lowturn 复刻**。  
2. **换手/成本**：meta mean_one_way≈0.046；账本 cost/AUM≈**3.8–4.1%**（半月节奏换手偏高，成本与 etf_core 同量级）。  
3. **相对同窗五包**：仅略强于残差×ETF（约 +0.8–1.2 pp），逊于 expand / lowturn / friction月频 / etf_core。  
4. **相对基线 C0**：两端约 **−4.5～−5.2 pp**；MDD 略浅于 C0。  
5. **研究门锁**：**any_pass=false** → **research_candidate=false**；`promotion=false`；不交 Strategy；**handoff=NO**。  
6. **一句话**：结构正交真跑满窗（个股≈0.85+压舱≈0.15，半月），但门锁没进、相对 C0 明显负、成本偏高——摩擦降成本再设计本窗不进研究备选。
