# AI v20 Track B `etf_timing` — Beta 纸深度复核

更新：2026-10-12 07:47 ET（America/New_York）  
来源包：`output/ai_factor/gp_reopen_hardgate_v20_track_b_etf_timing/`  
说明：`BETA_NOTE_ZH.md`；包：`beta_etf_timing_package.json`  
复核方：QuantLab Beta。`promotion_approved=false`。**不交 Strategy**。  
冒烟 runner：`output/v3/run_etf_timing_v20_smoke.py`；诊断：`output/v3/etf_timing_v20/diagnostics.json`；batch：`output/v3/pretest_batch_20261012_etf_timing_v20.json`。

---

## 0. 一句话裁决

**reject / research_observe（诊断级，非可交易袖套）。**  
包内 ICIR≈1.2–16.8 是 **行业 ETF 份额流自相关**，不是收益预测；用真实行业 ETF 次日/5日收益与 60万 X1 组合冒烟后，**T1–T10 全部 fail_precheck**，无交接、无预注册冒烟续跑。

---

## 1. 包内容摘要（公式 / 叶子 / 谁付钱 / 失败条件）

| 项 | 内容 |
|---|---|
| sleeve | `etf_timing`（显式 `for_beta=true`，`for_alpha_shortlist=false`） |
| evals / pass | 80 / 23；peak≈1976MB；seed=20261120；窗 `2024-06-03` explore lean |
| 叶子 | `ind_etf_share_flow`（申万一极截面流）、`etf_all_flow`、`etf_share_chg_major`；**theme 因 RSS 跳过** |
| 标签 | `next_day_ind_etf_flow_continuation_proxy` = `ind_etf_share_flow.shift(-1)`（代码 L3390） |
| 适应度 | 日频截面 Pearson → IR×√252，记为 `icir_timing_proxy` |
| 典型 Top 式 | `ind_etf − ts_mean_5(all_flow)`（T1 代数等价）；`ts_mean_5(ts_mean_5(ind_etf))`（纯平滑）；`ts_delta_5(ind_etf)` |
| 谁付钱（包内宣称） | **未宣称组合收益来源**；只声明「次日行业 ETF 流延续诊断代理」 |
| 失败条件（诚实版） | (a) 标签≠收益 → 高 ICIR 不可晋级；(b) 流自相关主导；(c) 对 ETF 收益 ICIR≤0；(d) 组合 X1 Sharpe≤0 |

**Track B 实现瑕疵（复核必记）：** 重装面板时用 **`trade_date` 聚合**，未走 `available_at→signal_date`（对比同文件 Track A L1759–1761 的 PIT）。本复核冒烟已改 PIT；即便修正后，流延续 ICIR 仍≈10.7（自相关，非泄漏独有）。

---

## 2. 泄漏 / 自相关量化

| 检验 | 数值 | 解读 |
|---|---|---|
| 原始 `ind_etf_share_flow` vs 次日同序列（PIT）ICIR | **+10.72** | 裸叶子已「过关」→ 标签几乎=滞后自相关 |
| 同检验（trade_date 泄漏路径） | +10.70 | 与 PIT 同量级 → **主因不是 PIT 泄漏，是标签定义** |
| 截面均值 lag1 / lag5 自相关 | **0.41 / 0.19** | 流序列强持续 |
| 原始流 vs **次日行业 ETF 收益** ICIR | **−0.64** | 对价格收益无正预测 |
| 原始流 vs **5日前瞻 ETF 收益** ICIR | **−1.43** | 更负（偏创设拥挤/反转） |
| Top 候选 vs 次日流 / 次日收益 / 5日收益 | 流 ICIR≈5–11；收益 ICIR **全负**（约 −0.2～−1.0） | 包内排序在优化「猜明天的流」，不是「猜明天的价」 |

结论：AI 自注「高 ICIR 可能自相关」**成立且定量坐实**；ICIR_timing_proxy **严重虚高**，不可作 Beta 晋级证据。

---

## 3. 对照 Beta 约束

| 约束 | 判定 |
|---|---|
| 禁小盘 | 冒烟用申万 map-pit 行业 ETF + amt20≥2000 ✅ |
| 禁 CB/金主仓 | 残差 **511880 货币**（非 GOLD/CB）✅；非 IND-RATE 的 510300↔GOLD 削仓皮 |
| 个股+ETF / 行业 ETF 择时 OK | 形态上是行业 ETF 篮 ✅ |
| 非 IND-RATE near_relative 皮 | 持仓空间已脱钩；但因预检失败未开正式 ρ |
| 必须预测组合收益 | **不满足** — 只预测流延续 |

与既有 fail 族关系：收益 ICIR 为负 → 更接近「创设反转」叙事，而 **IND-CREATE-REV(-BOOK/-FULL)** 已在 X1 Sharpe≤0 失败；本包 long-high（顺流）同样失败，**不新开反向磨**。

---

## 4. 真实收益冒烟（60万 X1；扣成本引擎）

规则：月频；按 GP 式得分取液态行业 ETF **顶 tercile 等权**；空仓→511880；X1 Sharpe≤0 或 avg_names=0 → **fail_precheck**（不开 X2 正式）。AUM 100万未开（预检全挂）。

| arm_id | 表达式（摘） | ICIR流/收益 | X1 CAGR/MDD/Sharpe | avg_names | 处置 |
|---|---|---|---|---|---|
| **ETF-TIMING-V20-T1** | `ind_etf − ts_mean_5(all)` | 10.7 / −0.64 | −23.7%/−53.7%/ **−0.57** | 1.16 | **fail_precheck** |
| **ETF-TIMING-V20-T2** | `ind_etf − ts_std_10(all)` | 10.8 / −0.64 | −23.7%/−53.7%/ **−0.57** | 1.16 | **fail_precheck** |
| **ETF-TIMING-V20-T3** | `ts_mean_5(ind)+ts_max_20(all)` | 9.6 / −0.79 | −22.6%/−53.1%/ **−0.57** | 1.16 | **fail_precheck** |
| **ETF-TIMING-V20-T4** | `ts_max_20(major)×ts_mean_5(ind)` | 10.6 / −0.98 | +3.0%/−0.2%/9.53† | **0.0** | **fail_precheck**（major 自2018，X1 全现金） |
| **ETF-TIMING-V20-T5** | `ts_mean_5(ind)/ts_std_10(all)` | 9.5 / −0.79 | −22.6%/−53.1%/ **−0.57** | 1.16 | **fail_precheck** |
| **ETF-TIMING-V20-T6** | `ts_mean_5(ind)+ts_mean_10(major)` | 10.6 / −0.95 | †现金 | **0.0** | **fail_precheck** |
| **ETF-TIMING-V20-T7** | `ts_mean_10(ind)−ts_mean_10(major)` | 9.6 / −1.05 | †现金 | **0.0** | **fail_precheck** |
| **ETF-TIMING-V20-T8** | `ts_mean_20(ind)−ts_mean_5(all)` | 7.3 / −0.78 | −21.1%/−51.8%/ **−0.52** | 1.16 | **fail_precheck** |
| **ETF-TIMING-V20-T9** | `ts_mean_5(ts_mean_5(ind))` | 7.3 / −0.93 | −22.1%/−52.4%/ **−0.55** | 1.16 | **fail_precheck** |
| **ETF-TIMING-V20-T10** | `ts_delta_5(ind)` | 5.0 / −0.23 | −23.1%/−61.5%/ **−0.53** | 1.16 | **fail_precheck** |

† T4/T6/T7：`etf_share_flow_pit_major` 仅 **2018-01+**，X1 因子全空 → 整段 511880，Sharpe 虚高，**按 avg_names=0 否决**。

**X2：** 无一过预检 → **未开**（避免空转描述窗）。  
**handoff：NO。**

---

## 5. 是否可写预注册续跑？

**否。** 无候选同时满足：(1) 对 ETF 收益 IC>0；(2) X1 Sharpe>0；(3) 非流自相关伪指标。  
若未来要重开，必须 **换标签** 为行业 ETF **前瞻收益**（或扣成本组合收益），并在预注册写死：流延续 ICIR 不得作为适应度；`etf_share_chg_major` 不得单独撑 X1。  
当前 **不写** 可执行 prereg、不交 Strategy。

---

## 6. 处置总表

| 裁决 | 范围 |
|---|---|
| **reject（不可作 Beta 袖套）** | 全部 T1–T10 组合冒烟 |
| **research_observe** | 包本身：流延续诊断有记录价值；证明「份额流强自相关、对价格收益偏负」 |
| promotion | **false** |
| Strategy handoff | **无** |
| 与 LIMITUP/UNLOCK | **不磨**（本复核范围外；UNLOCK 早窗 Data 已补，另指令再说） |

