# Book-Smoke 回执：G1G5 **个股资金流残差叶 moneyflow_resid**（`moneyflow_resid_v1`）**X2 满窗** vs 纯 510300

**run_id**：`book_smoke_20261013_051054`  
**strategy_promotion_approved**：`false`  
**sealed_claim**：`false`（不声称过密封线 / 不交 Strategy / 不下单）  
**promotion_approved**：`false`  
**Mandate**：`docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md`（本跑次**未改** Mandate）  
**授权**：Leo 经 New Bot 【加急 Book-Smoke】+ QuantLab AI 【Alpha ACCEPT 已到·立刻开烟】派 Eng  
**Alpha ACCEPT**：`docs/v2/AI_G1G5_MONEYFLOW_RESID_WEIGHT_ACCEPT_ZH.md`  
**JSON**：`output/alpha/AI_G1G5_MONEYFLOW_RESID_WEIGHT_ACCEPT_20261013.json`  
**预注册**：`docs/v2/AI_G1G5_MONEYFLOW_RESID_WHO_PAYS_PREREG_ZH.md`  
**门锁（Alpha）**：净成本 **CAGR ∈ [12%, 18%]** · **MDD ≥ −28%** @60万∧100万 vs C0=纯510300（外部 12–15%/≤25% 仅参考）  
**结构正交**：已败十包 + capacity_adv + margin_delta（WATCH）+ accrual_quality（WATCH）+ northbound/OCF/d1_val；本叶主仓 **个股≈0.757 + 510300 压舱≈0.243**（PIT Σ`net_mf_amount` L≈20 / ADV → 行业 demean → log 流通市值残差；**高残差优先**；ADV **仅分母**；月频；硬排除 `600519`/`002371`；**非** ADV 分位 / 两融 Δrzye / 北向 / 应计 / OCF / 估值残差 / 相对强弱 / 四臂 / etf_core 0.70）→ 非换皮。本满窗 **两端均未过 CAGR 下沿** → **any_pass=false** → **WATCH**；**research_candidate=false**；**promotion=false / 不交 Strategy / handoff=NO**。

## 实验设置

| 项 | 值 |
|---|---|
| 权重长表 | `output/ai_factory/g1g5_moneyflow_resid_daily_weights_20261013_050716.parquet`（**32732** 行 / **668** sessions / **49** 标的） |
| 对照 meta | `output/ai_factory/g1g5_moneyflow_resid_run_meta_20261013_050716.json`（`stub_window=false` · `stub_forward_fill=false` · `n_rebalance_sessions=35` · `hard_exclude` 设计=`600519`/`002371` · `mean_ballast_share≈0.243` · `mean_stock_share≈0.757`） |
| mechanism_tag | **`g1g5_ashare_moneyflow_resid_v1`** |
| who_pays | 忽视行业/市值中性后的个股净资金流入强度（相对 ADV）的对手盘：PIT Σ`net_mf_amount`（L≈20）/ADV → 申万一级 demean → log 流通市值残差；高残差优先；主叙事=个股资金流残差（moneyflow/ADV）；ADV 仅分母 |
| 明确排除 | ADV 流动性分位选股；两融 Δrzye；北向 hk_hold；应计/OCF/估值残差；截面相对强弱；四臂摩擦/解禁/份额流/调仓；ETF-core overlay；小盘主线；stub 前推 |
| 名义结构 | **全窗** 个股≈**0.757** / 510300 压舱≈**0.243**；**X2** 个股≈**0.760** / 压舱≈**0.240**（余量归压舱；无 etf_core 0.70 膨胀） |
| universe_id | `g1g5_mid_large_liquid_top50` |
| 袖套消费 | `{"core":0.0,"stock":1.0,"alpha_event":0.0}` = **整本账由该长表驱动**；表内已含压舱 → **禁止**再叠 core overlay |
| 对照 | `C0` = 纯 510300 |
| 窗 | 探索窗 **X2** `2024-06-03→2026-10-09` |
| 资金 | 60万 ∧ 100万 |
| 成本 | 开（`ExecConfig.strategy_v1`） |
| 可消费 | stock **book_consumable** rows=**16480** / sessions=**570**（X2∩权重日历=整窗；引擎 target 非零行 **14114**） |
| meta 换手 | 全日 mean_one_way **≈0.0203**；`n_rebalance_days_nonzero=34`（全窗日历）；cadence=`month_end_plus_first_last`；`n_rebalance_sessions=35` |
| 角色 | 个股资金流残差（mf/ADV）主测；对照=capacity_adv + margin_delta + accrual_quality + northbound/OCF/估值 + 已败包 + 纯 510300 |

## ✅ 满窗日更（无 stub 前推）+ 结构核验

| 核验项 | 结果 |
|---|---|
| 权重日历 | **2024-01-02→2026-10-09**（668 sessions） |
| meta `stub_forward_fill` / `stub_window` | **false / false** |
| BOOK `n_signals` | **570**（= X2 可消费 sessions） |
| 唯一组合数（X2） | **30**（2024:8 + 2025:12 + 2026:10；月频节奏） |
| 尾段相同组合长度 | **1**（末日无长尾 stub 前推） |
| 日权重合计 | 恒 **1.0** |
| **日均个股权重（X2）** | **≈0.760** |
| **日均 510300 压舱（X2）** | **≈0.240** |
| 日均活跃个股（X2） | **≈23.8**（设计 topN=25） |
| 单名顶 | **≤0.04**（观测个股 max=**0.032**；压舱单日最高观测≈0.392，余量归压舱） |
| 硬排除 `600519`/`002371` | **权重表 0 行**（设计硬排除生效） |
| 未滑向 etf_core 0.70 | **是**（压舱仅宽基 510300≈0.24；无行业 ETF；禁 overlay） |
| 非 ADV 分位 / 非两融 / 非北向 / 非应计·OCF·估值主轴 | **是**（预注册口径：PIT moneyflow/ADV 残差；ADV 仅分母） |
| 未双计 510300 overlay | **是**（sleeves.core=0；压舱仅来自表内） |

→ **禁止**再写「后半持仓前推」或「滑向 etf_core 0.70 / ADV 分位·两融·北向·应计换皮」。本回执是**真实满窗月频再平衡 + 个股≈0.76/压舱≈0.24 资金流残差账**结果。

## 数字表（探索窗满窗；成本开；非密封）

数字来自 `output/v3/book_smoke_g1g5_moneyflow_resid_x2/book_smoke_summary.json`（禁止臆造）。

| AUM | arm | CAGR | vs C0 | MDD | Sharpe | cost/AUM | target_weight 行数 |
|---|---|---|---|---|---|---|---|
| 600000 | X2/BOOK | **9.75%** (0.0975) | **−1.52 pp** | **−15.25%** | 0.745 | **0.0197** | 14114 |
| 600000 | X2/C0 | **11.27%** (0.1127) | — | −16.24% | 0.651 | 0.0002 | 570 |
| 1000000 | X2/BOOK | **9.70%** (0.0970) | **−1.57 pp** | **−16.27%** | 0.712 | **0.0202** | 14114 |
| 1000000 | X2/C0 | **11.27%** (0.1127) | — | −16.24% | 0.651 | 0.0002 | 570 |

起止：`2024-06-03→2026-10-09`。BOOK 引擎 `n_codes=49`（target 宇宙）；X2 target 非零 **49** 码含 510300（个股 **48**）；两端 actual 成交均为 **49** 码，**target∉actual=[]**；`n_signals=**570**`，`gross_mean≈0.905`（60万）/ `≈0.953`（100万），`fill_ratio≈0.911` / `0.937`。

## 对照门锁（Alpha 门）

| AUM/arm | CAGR∈[12%,18%] | MDD≥−28% | 过门？ |
|---|---|---|---|
| 60万 BOOK | **否**（9.75% &lt; 12%） | **是**（−15.25% ≥ −28%） | **否** |
| 100万 BOOK | **否**（9.70% &lt; 12%） | **是**（−16.27% ≥ −28%） | **否** |

C0 基线仍未过 CAGR 下沿（≈11.27%）。  
**任意 AUM 过门：否（any_pass=false）。** **两端同向过门：否（both_aum_pass=false）。**  
→ **本跑次不标研究备选（research_candidate=false）** → **WATCH**；仍为研究对照，**非** promotion / 密封 / Strategy 授权。Alpha 标 ACCEPT→WATCH；**勿再派烟**。

## vs C0 增量

| AUM | ΔCAGR | ΔMDD |
|---|---|---|
| 60万 | **−1.52 pp**（输纯 510300） | **+0.99 pp**（回撤略浅） |
| 100万 | **−1.57 pp**（输纯 510300） | **−0.03 pp**（与 C0 近平） |

解读：MDD 两端均好于门锁 −28%，但 **CAGR 两端均低于 12% 下沿且相对 C0 同向为负**——个股资金流残差主轴在本探索窗未能兑现超额；相对门锁下沿缺口约 **−2.25 pp**（60万）/ **−2.30 pp**（100万）。相对近邻 WATCH 叶（margin_delta≈7.9–8.6%、accrual≈5.5–5.8%）本叶 CAGR 更高，但仍未过门。

## 覆盖 / 缺价备注（诚实）

| 项 | 事实 |
|---|---|
| HFQ 外定价 | `run_book` 对 **49** 码调 `load_execution_panels`（**48** 在 HFQ 外）——个股 **可定价**，未 stub 前推补价 |
| target vs actual 码 | X2 BOOK target 非零 **49** 码；两端 actual 成交均为 **49** 码；**target∉actual：[]** |
| `600519` / `002371` | **权重表硬排除 → target 0 行 / actual 0 行** |
| 表内 510300 | 668 行均在；X2 日均权重 **≈0.240**（全窗 ≈0.243） |
| 首日 2024-06-03 | target 有仓；actual 自 2024-06-04 起（T+1 执行日历正常），非缺价 |
| fill / gross | fill_ratio≈0.911–0.937；gross_mean≈0.90–0.95（执行后低于目标 1.0；闲置现金约 5–10%） |
| gaps 字段 | 引擎 `gaps=[]` |
| Book-Smoke peak_RSS | **轻量单进程**（wall≈**5.7 s**；NAV 两端各 ~2.1–2.4 s；未启 uvicorn；进程已退出未留峰 RSS 采样；与同类 X2 Book-Smoke 同级轻量） |

→ **禁止**把缺价/空仓缺口写成 pass；本跑次未用 stub 前推补价；巨头缺口由硬排除消除；target/actual 码集一致，**不**虚构成交。

## 机制与候选口径

- 本包是 **个股资金流残差叶：PIT Σ`net_mf_amount`/ADV → 行业·市值残差（高残差优先）**（个股≈0.76 + 510300≈0.24，月频，硬排除巨头），明确排除 ADV 分位 / 两融 / 北向 / 应计·OCF·估值 / 动量 / 四臂 / etf_core overlay 与已败同构；结构正交声明由 Alpha ACCEPT 成立。  
- **满窗 any_pass=false** → **WATCH**；**research_candidate=false**。  
- 仍 **`promotion_approved=false`** · **不交 Strategy** · **不开密封** · **不下单** · **禁小盘主线** · **禁 GP**。  
- **handoff=NO** · **live=false** · **不交 Strategy 实盘** · **不升主书**。

## 工程备注

- 命令：`PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli book-smoke --run-nav --stock-path output/ai_factory/g1g5_moneyflow_resid_daily_weights_20261013_050716.parquet --sleeves '{"core":0.0,"stock":1.0,"alpha_event":0.0}' --windows X2 --capitals 600000,1000000 --arms BOOK,C0 --out output/v3/book_smoke_g1g5_moneyflow_resid_x2 --receipt docs/v2/BOOK_SMOKE_G1G5_MONEYFLOW_RESID_X2_RECEIPT_ZH.md`
- exit_code：**0**（`strategy_promotion_approved=false`）
- JSON：`output/v3/book_smoke_g1g5_moneyflow_resid_x2/book_smoke_summary.json`
- NAV：`output/v3/book_smoke_g1g5_moneyflow_resid_x2/aum_{600000,1000000}/X2/{BOOK,C0}/`
- promotion=false；不下单；不交 Strategy；不开密封；未改 Mandate；未启 uvicorn；未跑 GP/E1/reconcile/Full D1。

## 结论（诚实）

1. **管线通 + 满窗真日更 + 结构核验过**：668 sessions 至 2026-10-09；`n_signals=570`；唯一组合 30；尾长 1；**日均个股≈0.76 / 压舱≈0.24（X2）**；硬排除巨头生效；**已证伪 stub 前推与 etf_core 0.70 overlay**。  
2. **门锁未过**：两端 CAGR≈9.7% &lt; 12%，MDD 过门；**any_pass=false** · **both_aum_pass=false** · **research_candidate=false** → **WATCH**。  
3. **vs C0**：ΔCAGR ≈ −1.5 pp 两端同向；未兑现超额。  
4. **晋级门锁全关**：`promotion_approved=false` · `sealed_claim=false` · **handoff=NO** · **live=false** · 不交 Strategy · 不升 MAINBOOK。  
5. 请 Alpha 将研究级 ACCEPT **标为 WATCH**；**勿再派本叶 Book-Smoke**。
