# Book-Smoke 回执：G1G5 **两融边际叶 margin_delta**（`margin_delta_v1`）**X2 满窗** vs 纯 510300

**run_id**：`book_smoke_20261013_021225`  
**strategy_promotion_approved**：`false`  
**sealed_claim**：`false`（不声称过密封线 / 不交 Strategy / 不下单）  
**promotion_approved**：`false`  
**Mandate**：`docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md`（本跑次**未改** Mandate）  
**授权**：Leo 经 New Bot 【立刻 Book-Smoke】Alpha ACCEPT `margin_delta` 后派 Eng  
**Alpha ACCEPT**：`docs/v2/AI_G1G5_MARGIN_DELTA_WEIGHT_ACCEPT_ZH.md`  
**预注册**：`docs/v2/AI_G1G5_MARGIN_DELTA_WHO_PAYS_PREREG_ZH.md`  
**门锁（Alpha）**：净成本 **CAGR ∈ [12%, 18%]** · **MDD ≥ −28%** @60万∧100万 vs C0=纯510300（外部 12–15%/≤25% 仅参考）  
**结构正交**：已败十包 + 叶A/叶B + capacity_adv + northbound；本叶主仓 **个股≈0.74 + 510300 压舱≈0.26**（全窗 Δrzye→行业 demean→log 流通市值残差；月频；硬排除 `600519`/`002371`；**非** ADV 分位 / 北向 / 估值残差 / OCF / 动量 / 四臂 / etf_core 0.70）→ 非换皮。本满窗 **两端均未过 CAGR 下沿** → **any_pass=false** → **WATCH**；**research_candidate=false**；**promotion=false / 不交 Strategy / handoff=NO**。

## 实验设置

| 项 | 值 |
|---|---|
| 权重长表 | `output/ai_factory/g1g5_margin_delta_daily_weights_20261013_020825.parquet`（**32732** 行 / **668** sessions / **49** 标的） |
| 对照 meta | `output/ai_factory/g1g5_margin_delta_run_meta_20261013_020825.json`（`stub_window=false` · `stub_forward_fill=false` · `n_rebalance_sessions=35` · `hard_exclude=[002371.SZ,600519.SH]` · `mean_ballast_share≈0.264` · `mean_stock_share≈0.736`） |
| mechanism_tag | **`g1g5_ashare_margin_delta_v1`** |
| who_pays | 国内两融/杠杆资金边际加仓与去杠杆压力下的错误定价对手盘：个股融资余额 Δrzye（asof available_at）经申万一级 demean + log 流通市值残差分位；高Δ优先；主叙事=杠杆资金流 |
| 明确排除 | 北向 hk_hold；ADV 容量分位选股；估值残差/裸 EP/BM；OCF；截面相对强弱；四臂摩擦/解禁/份额流/调仓；ETF-core overlay；小盘主线；stub 前推；D2 moneyflow 主腿 |
| 名义结构 | **全窗** 个股≈**0.736** / 510300 压舱≈**0.264**；**X2** 个股≈**0.748** / 压舱≈**0.252**（压舱可升至 ≈0.424，共 325/668 日 >0.25） |
| universe_id | `g1g5_mid_large_liquid_top50` |
| 袖套消费 | `{"core":0.0,"stock":1.0,"alpha_event":0.0}` = **整本账由该长表驱动**；表内已含压舱 → **禁止**再叠 core overlay |
| 对照 | `C0` = 纯 510300 |
| 窗 | 探索窗 **X2** `2024-06-03→2026-10-09` |
| 资金 | 60万 ∧ 100万 |
| 成本 | 开（`ExecConfig.strategy_v1`） |
| 可消费 | stock **book_consumable** rows=**16026** / sessions=**570**（X2∩权重日历=整窗；活跃权重大行 13888） |
| meta 换手 | mean_one_way **≈0.0206**；`n_rebalance_days_nonzero=34`；cadence=`month_end_plus_first_last`；`n_rebalance_sessions=35` |
| 角色 | 两融 Δrzye 杠杆资金流主测；对照=capacity_adv + northbound + 叶B/叶A + 已败包 + 纯 510300 |

## ✅ 满窗日更（无 stub 前推）+ 结构核验

| 核验项 | 结果 |
|---|---|
| 权重日历 | **2024-01-02→2026-10-09**（668 sessions） |
| meta `stub_forward_fill` / `stub_window` | **false / false** |
| BOOK `n_signals` | **570**（= X2 可消费 sessions） |
| 唯一组合数（X2） | **30**（2024:8 + 2025:13 + 2026:11；月频节奏） |
| 尾段相同组合长度 | **1**（末日无长尾 stub 前推） |
| 日权重合计 | 恒 **1.0** |
| **日均个股权重（X2）** | **≈0.748**（min≈0.58 / max≈0.80） |
| **日均 510300 压舱（X2）** | **≈0.252**（min≈0.20 / max≈0.42；覆盖不足日余量→压舱） |
| 日均活跃个股（X2） | **≈23.4**（min 18 / max 25） |
| 单名顶 | **≤0.04**（观测 max=**0.032**） |
| 硬排除 `600519`/`002371` | **权重表 0 行**（设计硬排除生效） |
| 未滑向 etf_core 0.70 | **是**（压舱仅宽基 510300≈0.25–0.26；无行业 ETF；禁 overlay） |
| 非 ADV / 非北向 / 非估值残差 / 非 OCF / 非动量主轴 | **是**（预注册口径：全窗 Δrzye 杠杆资金流） |
| 未双计 510300 overlay | **是**（sleeves.core=0；压舱仅来自表内） |

→ **禁止**再写「后半持仓前推」或「滑向 etf_core 0.70 / ADV·北向换皮」。本回执是**真实满窗月频再平衡 + 个股≈0.75/压舱≈0.25 两融边际账**结果。

## 数字表（探索窗满窗；成本开；非密封）

数字来自 `output/v3/book_smoke_g1g5_margin_delta_x2/book_smoke_summary.json`（禁止臆造）。

| AUM | arm | CAGR | vs C0 | MDD | Sharpe | cost/AUM | target_weight 行数 |
|---|---|---|---|---|---|---|---|
| 600000 | X2/BOOK | **7.85%** (0.0785) | **−3.41 pp** | **−13.02%** | 0.617 | **0.0189** | 13888 |
| 600000 | X2/C0 | **11.27%** (0.1127) | — | −16.24% | 0.651 | 0.0002 | 570 |
| 1000000 | X2/BOOK | **8.62%** (0.0862) | **−2.65 pp** | **−14.18%** | 0.637 | **0.0205** | 13888 |
| 1000000 | X2/C0 | **11.27%** (0.1127) | — | −16.24% | 0.651 | 0.0002 | 570 |

起止：`2024-06-03→2026-10-09`。BOOK `n_codes=49`（引擎计数；X2 target 非零 **49** 码含 510300，其中个股 **48**；actual 成交 **49** 码，**target∉actual=[]**），`n_signals=**570**`，`gross_mean≈0.91`（60万）/ `≈0.95`（100万），`fill_ratio≈0.977` / `0.979`。

## 对照门锁（Alpha 门）

| AUM/arm | CAGR∈[12%,18%] | MDD≥−28% | 过门？ |
|---|---|---|---|
| 60万 BOOK | **否**（7.85% &lt; 12%） | **是**（−13.02% ≥ −28%） | **否** |
| 100万 BOOK | **否**（8.62% &lt; 12%） | **是**（−14.18% ≥ −28%） | **否** |

C0 基线仍未过 CAGR 下沿（≈11.27%）。  
**任意 AUM 过门：否（any_pass=false）。** **两端同向过门：否（both_aum_pass=false）。**  
→ **本跑次不标研究备选（research_candidate=false）** → **WATCH**；仍为研究对照，**非** promotion / 密封 / Strategy 授权。

## vs C0 增量

| AUM | ΔCAGR | ΔMDD |
|---|---|---|
| 60万 | **−3.41 pp**（输纯 510300） | **+3.22 pp**（回撤略浅） |
| 100万 | **−2.65 pp**（输纯 510300） | **+2.06 pp**（回撤略浅） |

解读：MDD 两端均好于门锁 −28% 且略浅于 C0，但 **CAGR 两端均低于 12% 下沿且相对 C0 同向为负**——杠杆资金流主轴在本探索窗未能兑现超额；相对门锁下沿缺口约 **−4.15 pp**（60万）/ **−3.38 pp**（100万）。

## 覆盖 / 缺价备注（诚实）

| 项 | 事实 |
|---|---|
| HFQ 外定价 | `run_book` 对 **49** 码调 `load_execution_panels`（**48** 在 HFQ 外）——个股 **可定价**，未 stub 前推补价 |
| target vs actual 码 | X2 BOOK target 非零 **49** 码；actual 成交 **49** 码；**target∉actual：[]（空）** |
| `600519` / `002371` | **权重表硬排除 → target 0 行 / actual 0 行** |
| 表内 510300 | 668 行均在；X2 日均权重 **≈0.252**（全窗 ≈0.264） |
| 首日 2024-06-03 | target 有仓；actual 自 2024-06-04 起（T+1 执行日历正常），非缺价 |
| fill / gross | fill_ratio≈0.977–0.979；gross_mean≈0.91–0.95（执行后低于目标 1.0；闲置现金约 5–9%） |
| gaps 字段 | 引擎 `gaps=[]` |
| Book-Smoke peak_RSS | **≈751 MB**（769172 KB；轻量单进程） |

→ **禁止**把缺价/空仓缺口写成 pass；本跑次未用 stub 前推补价；巨头缺口由硬排除消除，**不**虚构成交。

## 机制与候选口径

- 本包是 **两融边际叶：全窗 Δrzye 杠杆资金流**（个股≈0.74 + 510300≈0.26，月频，硬排除巨头），明确排除 ADV 分位 / 北向 / 估值残差 / OCF / 动量 / 四臂 / etf_core overlay 与已败同构；结构正交声明由 Alpha ACCEPT 成立。  
- **满窗 any_pass=false** → **WATCH**；**research_candidate=false**。  
- 仍 **`promotion_approved=false`** · **不交 Strategy** · **不开密封** · **不下单** · **禁小盘主线** · **禁 GP**。  
- **handoff=NO** · **live=false** · **不交 Strategy 实盘**。

## 工程备注

- 命令：`PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli book-smoke --run-nav --stock-path output/ai_factory/g1g5_margin_delta_daily_weights_20261013_020825.parquet --sleeves '{"core":0.0,"stock":1.0,"alpha_event":0.0}' --windows X2 --capitals 600000,1000000 --arms BOOK,C0 --out output/v3/book_smoke_g1g5_margin_delta_x2 --receipt docs/v2/BOOK_SMOKE_G1G5_MARGIN_DELTA_X2_RECEIPT_ZH.md`
- exit_code：**0**（`strategy_promotion_approved=false`）
- JSON：`output/v3/book_smoke_g1g5_margin_delta_x2/book_smoke_summary.json`
- NAV：`output/v3/book_smoke_g1g5_margin_delta_x2/aum_{600000,1000000}/X2/{BOOK,C0}/`
- promotion=false；不下单；不交 Strategy；不开密封；未改 Mandate；未启 uvicorn。

## 结论（诚实）

1. **管线通 + 满窗真日更 + 结构核验过**：668 sessions 至 2026-10-09；`n_signals=570`；唯一组合 30；尾长 1；**日均个股≈0.75 / 压舱≈0.25（X2）**；硬排除巨头生效；**已证伪 stub 前推与 etf_core 0.70 overlay**。  
2. **换手/成本**：meta mean_one_way≈0.0206；账本 cost/AUM≈**1.89%/2.05%**。  
3. **相对基线 C0**：60万 **−3.41 pp**；100万 **−2.65 pp**；MDD 两端略浅于 C0，但收益端全面落后。  
4. **覆盖缺口**：`600519`/`002371` **无目标仓**（硬排除）；target∉actual 为空。  
5. **研究门锁**：**any_pass=false** → **research_candidate=false** → **WATCH**；`promotion=false`；不交 Strategy；**handoff=NO**。  
6. **一句话**：两融 Δrzye 叶真跑满窗（个股≈0.75+压舱≈0.25，硬排除巨头），**60万∧100万 CAGR 均未进 [12%,18%] 且同向输 C0**——本窗入 WATCH，不晋级、不交 Strategy、不下单。
