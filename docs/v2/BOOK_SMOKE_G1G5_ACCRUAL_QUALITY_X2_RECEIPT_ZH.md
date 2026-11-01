# Book-Smoke 回执：G1G5 **应计质量叶 accrual_quality**（`accrual_quality_v1`）**X2 满窗** vs 纯 510300

**run_id**：`book_smoke_20261013_022718`  
**strategy_promotion_approved**：`false`  
**sealed_claim**：`false`（不声称过密封线 / 不交 Strategy / 不下单）  
**promotion_approved**：`false`  
**Mandate**：`docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md`（本跑次**未改** Mandate）  
**授权**：Leo 经 New Bot 【立刻 Book-Smoke】Alpha ACCEPT `accrual_quality` 后派 Eng  
**Alpha ACCEPT**：`docs/v2/AI_G1G5_ACCRUAL_QUALITY_WEIGHT_ACCEPT_ZH.md`  
**预注册**：`docs/v2/AI_G1G5_ACCRUAL_QUALITY_WHO_PAYS_PREREG_ZH.md`  
**门锁（Alpha）**：净成本 **CAGR ∈ [12%, 18%]** · **MDD ≥ −28%** @60万∧100万 vs C0=纯510300（外部 12–15%/≤25% 仅参考）  
**结构正交**：已败十包 + capacity_adv + margin_delta（WATCH）+ northbound/OCF/d1_val；本叶主仓 **个股≈0.800 + 510300 压舱≈0.200**（PIT BS 营运资本应计/TA→行业 demean→log 流通市值残差；**低应计优先**；月频；硬排除 `600519`/`002371`；**非** OCF / EP·BM / ADV / 两融 / 北向 / 动量 / 四臂 / etf_core 0.70）→ 非换皮。本满窗 **两端均未过 CAGR 下沿** → **any_pass=false** → **WATCH**；**research_candidate=false**；**promotion=false / 不交 Strategy / handoff=NO**。

## 实验设置

| 项 | 值 |
|---|---|
| 权重长表 | `output/ai_factory/g1g5_accrual_quality_daily_weights_20261013_022400.parquet`（**52772** 行 / **668** sessions / **79** 标的） |
| 对照 meta | `output/ai_factory/g1g5_accrual_quality_run_meta_20261013_022400.json`（`stub_window=false` · `stub_forward_fill=false` · `n_rebalance_sessions=35` · `hard_exclude` 设计=`600519`/`002371` · `mean_ballast_share≈0.200` · `mean_stock_share≈0.800`） |
| mechanism_tag | **`g1g5_ashare_accrual_quality_v1`** |
| who_pays | 投资者过度依赖应计盈余、低估低应计/资产负债表盈余的对手盘：PIT BS 营运资本应计/TA（Sloan 代理，无 Dep）→ 申万一级 demean → log 流通市值残差；低应计优先；主叙事=非 OCF 应计质量（资产负债表） |
| 明确排除 | ocf_to_profit；EP/BM 估值残差；ADV 容量分位；两融/北向资金流；截面相对强弱；四臂摩擦/解禁/份额流/调仓；ETF-core overlay；小盘主线；stub 前推；D2 moneyflow 主腿 |
| 名义结构 | **全窗** 个股≈**0.800** / 510300 压舱≈**0.200**；**X2** 个股≈**0.800** / 压舱≈**0.200**（恒定；无压舱膨胀） |
| universe_id | `g1g5_mid_large_liquid_top50` |
| 袖套消费 | `{"core":0.0,"stock":1.0,"alpha_event":0.0}` = **整本账由该长表驱动**；表内已含压舱 → **禁止**再叠 core overlay |
| 对照 | `C0` = 纯 510300 |
| 窗 | 探索窗 **X2** `2024-06-03→2026-10-09` |
| 资金 | 60万 ∧ 100万 |
| 成本 | 开（`ExecConfig.strategy_v1`） |
| 可消费 | stock **book_consumable** rows=**17368** / sessions=**570**（X2∩权重日历=整窗；引擎 target 非零行 **14820**） |
| meta 换手 | 全日 mean_one_way **≈0.0075**；`n_rebalance_days_nonzero=21`（全窗日历）；cadence=`month_end_plus_first_last`；`n_rebalance_sessions=35` |
| 角色 | BS 应计质量（低应计）主测；对照=capacity_adv + margin_delta + northbound/OCF/估值 + 已败包 + 纯 510300 |

## ✅ 满窗日更（无 stub 前推）+ 结构核验

| 核验项 | 结果 |
|---|---|
| 权重日历 | **2024-01-02→2026-10-09**（668 sessions） |
| meta `stub_forward_fill` / `stub_window` | **false / false** |
| BOOK `n_signals` | **570**（= X2 可消费 sessions） |
| 唯一组合数（X2） | **19**（2024:6 + 2025:9 + 2026:6；月频节奏） |
| 尾段相同组合长度 | **3**（末日无长尾 stub 前推） |
| 日权重合计 | 恒 **1.0** |
| **日均个股权重（X2）** | **≈0.800**（恒 0.80） |
| **日均 510300 压舱（X2）** | **≈0.200**（恒 0.20） |
| 日均活跃个股（X2） | **≈25.0**（恒 25；设计 topN=25） |
| 单名顶 | **≤0.04**（观测 max=**0.032**） |
| 硬排除 `600519`/`002371` | **权重表 0 行**（设计硬排除生效） |
| 未滑向 etf_core 0.70 | **是**（压舱仅宽基 510300≈0.20；无行业 ETF；禁 overlay） |
| 非 OCF / 非估值残差 / 非 ADV / 非两融 / 非北向主轴 | **是**（预注册口径：PIT BS 应计质量） |
| 未双计 510300 overlay | **是**（sleeves.core=0；压舱仅来自表内） |

→ **禁止**再写「后半持仓前推」或「滑向 etf_core 0.70 / OCF·估值·ADV·两融·北向换皮」。本回执是**真实满窗月频再平衡 + 个股≈0.80/压舱≈0.20 应计质量账**结果。

## 数字表（探索窗满窗；成本开；非密封）

数字来自 `output/v3/book_smoke_g1g5_accrual_quality_x2/book_smoke_summary.json`（禁止臆造）。

| AUM | arm | CAGR | vs C0 | MDD | Sharpe | cost/AUM | target_weight 行数 |
|---|---|---|---|---|---|---|---|
| 600000 | X2/BOOK | **5.50%** (0.0550) | **−5.77 pp** | **−12.05%** | 0.465 | **0.0109** | 14820 |
| 600000 | X2/C0 | **11.27%** (0.1127) | — | −16.24% | 0.651 | 0.0002 | 570 |
| 1000000 | X2/BOOK | **5.81%** (0.0581) | **−5.45 pp** | **−13.81%** | 0.460 | **0.0118** | 14820 |
| 1000000 | X2/C0 | **11.27%** (0.1127) | — | −16.24% | 0.651 | 0.0002 | 570 |

起止：`2024-06-03→2026-10-09`。BOOK 引擎 `n_codes=57`（target 宇宙）；X2 target 非零 **57** 码含 510300（个股 **56**）；两端 actual 成交均为 **56** 码，**target∉actual=['sh.688111']**；`n_signals=**570**`，`gross_mean≈0.874`（60万）/ `≈0.931`（100万），`fill_ratio≈0.597` / `0.623`。

## 对照门锁（Alpha 门）

| AUM/arm | CAGR∈[12%,18%] | MDD≥−28% | 过门？ |
|---|---|---|---|
| 60万 BOOK | **否**（5.50% &lt; 12%） | **是**（−12.05% ≥ −28%） | **否** |
| 100万 BOOK | **否**（5.81% &lt; 12%） | **是**（−13.81% ≥ −28%） | **否** |

C0 基线仍未过 CAGR 下沿（≈11.27%）。  
**任意 AUM 过门：否（any_pass=false）。** **两端同向过门：否（both_aum_pass=false）。**  
→ **本跑次不标研究备选（research_candidate=false）** → **WATCH**；仍为研究对照，**非** promotion / 密封 / Strategy 授权。

## vs C0 增量

| AUM | ΔCAGR | ΔMDD |
|---|---|---|
| 60万 | **−5.77 pp**（输纯 510300） | **+4.19 pp**（回撤略浅） |
| 100万 | **−5.45 pp**（输纯 510300） | **+2.43 pp**（回撤略浅） |

解读：MDD 两端均好于门锁 −28% 且浅于 C0，但 **CAGR 两端均低于 12% 下沿且相对 C0 同向大幅为负**——BS 应计质量主轴在本探索窗未能兑现超额；相对门锁下沿缺口约 **−6.50 pp**（60万）/ **−6.19 pp**（100万）。

## 覆盖 / 缺价备注（诚实）

| 项 | 事实 |
|---|---|
| HFQ 外定价 | `run_book` 对 **57** 码调 `load_execution_panels`（**56** 在 HFQ 外）——个股 **可定价**，未 stub 前推补价 |
| target vs actual 码 | X2 BOOK target 非零 **57** 码；两端 actual 成交均为 **56** 码；**target∉actual：['sh.688111']** |
| `600519` / `002371` | **权重表硬排除 → target 0 行 / actual 0 行** |
| 表内 510300 | 668 行均在；X2 日均权重 **≈0.200**（全窗 ≈0.200） |
| 首日 2024-06-03 | target 有仓；actual 自 2024-06-04 起（T+1 执行日历正常），非缺价 |
| fill / gross | fill_ratio≈0.597–0.623（偏低）；gross_mean≈0.87–0.93（执行后低于目标 1.0；闲置现金约 7–13%） |
| gaps 字段 | 引擎 `gaps=[]` |
| Book-Smoke peak_RSS | **≈760 MB**（778548 KB；轻量单进程） |

→ **禁止**把缺价/空仓缺口写成 pass；本跑次未用 stub 前推补价；巨头缺口由硬排除消除；`688111` 一码两端均未进 actual，**不**虚构成交。

## 机制与候选口径

- 本包是 **应计质量叶：PIT BS 营运资本应计/TA（低应计优先）**（个股≈0.80 + 510300≈0.20，月频，硬排除巨头），明确排除 OCF / 估值残差 / ADV / 两融 / 北向 / 动量 / 四臂 / etf_core overlay 与已败同构；结构正交声明由 Alpha ACCEPT 成立。  
- **满窗 any_pass=false** → **WATCH**；**research_candidate=false**。  
- 仍 **`promotion_approved=false`** · **不交 Strategy** · **不开密封** · **不下单** · **禁小盘主线** · **禁 GP**。  
- **handoff=NO** · **live=false** · **不交 Strategy 实盘**。

## 工程备注

- 命令：`PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli book-smoke --run-nav --stock-path output/ai_factory/g1g5_accrual_quality_daily_weights_20261013_022400.parquet --sleeves '{"core":0.0,"stock":1.0,"alpha_event":0.0}' --windows X2 --capitals 600000,1000000 --arms BOOK,C0 --out output/v3/book_smoke_g1g5_accrual_quality_x2 --receipt docs/v2/BOOK_SMOKE_G1G5_ACCRUAL_QUALITY_X2_RECEIPT_ZH.md`
- exit_code：**0**（`strategy_promotion_approved=false`）
- JSON：`output/v3/book_smoke_g1g5_accrual_quality_x2/book_smoke_summary.json`
- NAV：`output/v3/book_smoke_g1g5_accrual_quality_x2/aum_{600000,1000000}/X2/{BOOK,C0}/`
- promotion=false；不下单；不交 Strategy；不开密封；未改 Mandate；未启 uvicorn。

## 结论（诚实）

1. **管线通 + 满窗真日更 + 结构核验过**：668 sessions 至 2026-10-09；`n_signals=570`；唯一组合 19；尾长 3；**日均个股≈0.80 / 压舱≈0.20（X2）**；硬排除巨头生效；**已证伪 stub 前推与 etf_core 0.70 overlay**。  
2. **换手/成本**：全日 mean_one_way≈0.0075；账本 cost/AUM≈**1.09%/1.18%**。  
3. **相对基线 C0**：60万 **−5.77 pp**；100万 **−5.45 pp**；MDD 两端浅于 C0，但收益端全面落后。  
4. **覆盖缺口**：`600519`/`002371` **无目标仓**（硬排除）；两端 target∉actual=`sh.688111`；fill_ratio 偏低（≈0.60）。  
5. **研究门锁**：**any_pass=false** → **research_candidate=false** → **WATCH**；`promotion=false`；不交 Strategy；**handoff=NO**。  
6. **一句话**：应计质量叶真跑满窗（个股≈0.80+压舱≈0.20，硬排除巨头），**60万∧100万 CAGR 均未进 [12%,18%] 且同向大幅输 C0**——本窗入 WATCH，不晋级、不交 Strategy、不下单。
