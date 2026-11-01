# AI v21 `etf_timing_ret` — Beta 纸深度复核

更新：2026-10-12 07:51 ET（America/New_York）  
来源包：`output/ai_factor/gp_reopen_hardgate_v21_etf_timing_ret/`  
说明：`BETA_NOTE_ZH.md`；包：`beta_etf_timing_ret_package.json`；标签定义：`label_definition.json`  
复核方：QuantLab Beta。`promotion_approved=false`。**不交 Strategy**。  
冒烟 runner：`output/v3/run_etf_timing_v21_ret_smoke.py`；诊断：`output/v3/etf_timing_v21_ret/diagnostics.json`；batch：`output/v3/pretest_batch_20261012_etf_timing_v21_ret.json`。

---

## 0. 一句话裁决

**reject / research_observe。**  
标签已换成 **fwd 1d/5d 超额 vs 510300**（不再是 v20 流延续）——方向对。但包内 ICIR≈1.6 **≈ trade_date 泄漏路径**（PIT 下≈−0.1）；叶子仍是份额流，去流残差后预测力塌。60万 X1 真持行业 ETF 冒烟 **R1–R10 全 fail_precheck**，无交接。

---

## 1. 包内容摘要

| 项 | 内容 |
|---|---|
| sleeve | `etf_timing_ret`（`for_beta=true`，`for_alpha_shortlist=false`） |
| evals / pass | 120 / 18；peak≈927MB；seed=20261104；窗 explore `2024-06-03→2025-06-30`（lookback 2024-04-01） |
| 叶子 X | `ind_etf_share_flow` / `etf_all_flow` / `etf_share_chg_major` / `etf_share_chg_theme` |
| 标签 y | **fwd_1d_excess_vs_510300**（主）；fwd_5d_excess（副）；**明确 NOT flow_continuation** |
| 典型 Top | `neg(ind_etf_share_flow)`；`mul(abs(theme), neg(ind))`；`all_max − ind_mean` |
| 谁付钱（宣称） | 行业 ETF 相对 510300 的超额（创设拥挤反转叙事） |
| 失败条件 | (a) trade_date 泄漏虚高 ICIR；(b) 去流残差 ICIR≈0；(c) X1 Sharpe≤0 / avg_names=0 |

---

## 2. 标签核验 + flow 诊断对照（防再踩 v20）

### 2.1 标签是否真是超额？

| 检验 | 结果 |
|---|---|
| `label_definition.json` / BETA_NOTE | y = AUM 加权申万一级行业 ETF `close_hfq` 收益 − 510300；**禁止 flow_continuation** ✅ |
| 截面 IC：裸流 vs 次日收益 ≡ vs 次日超额 | 两者同为 **−0.64**（减市场不改截面排序）— 标签形态正确，但「超额」在截面上≈「绝对收益」 |
| 包窗长度 | 仅 ~1y explore lean（301 日 / 26 SW）— ICIR 样本薄 |

### 2.2 泄漏 / 自相关 / 去流残差

| 检验 | 数值 | 解读 |
|---|---|---|
| 裸 `ind_etf_share_flow` vs 次日同序列（PIT）ICIR | **+10.72** | 叶子仍强自相关（与 v20 同） |
| 截面均值 lag1 / lag5 | **0.41 / 0.19** | 流持续 |
| 裸流 vs 次日/5日行业 ETF 收益 | **−0.64 / −1.43** | 对价格偏负（拥挤） |
| **包窗 PIT**：`neg(flow)` vs fwd1d excess | **≈ −0.10** | 真实可交易对齐下 **无正 ICIR** |
| **包窗 trade_date 泄漏**：同上 | **≈ +1.36** | **≈ 包内宣称 1.608** → 虚高主因 |
| R1 去流残差 vs fwd1d excess（全样本） | **≈ −0.12** | 去掉流截面后几乎无预测 |
| R1 corr(因子截面均值, 流截面均值) | **−1.0** | 就是 −flow |

**结论：** v21 换了 y，但 TrackB 仍用 **trade_date 聚合特征**（同 v20 瑕疵）。包内 ICIR 不能作晋级证据；flow 诊断对照已写入 `diagnostics.json`。

---

## 3. 对照 Beta 约束

| 约束 | 判定 |
|---|---|
| 禁小盘 | 冒烟 amt20≥2000 + list≥60d ✅ |
| 禁 CB/金主仓 | 残差 **511880** ✅ |
| 行业 ETF 时序袖套 | 形态 ✅ |
| 非 IND-RATE 削仓皮 | 真持行业篮 ✅ |
| 必须预测组合收益且可交易 | **不满足** — 包 ICIR 靠泄漏；PIT 下失效；X1 组合失败 |

---

## 4. 真实收益冒烟（60万 X1；扣成本引擎）

规则：月频；GP 式得分取液态行业 ETF **顶 tercile 等权**；空仓→511880；X1 Sharpe≤0 或 avg_names=0 → **fail_precheck**（不开 X2）。AUM 100万未开。

| arm_id | 表达式（摘） | ICIR流/超额(PIT全) | 包窗超额 PIT/泄漏 | X1 CAGR/MDD/Sharpe | avg | 处置 |
|---|---|---|---|---|---|---|
| **ETF-TIMING-V21-R1** | `neg(ind_etf)` | −10.7 / +0.64 | −0.01 / **+1.36** | −18.9%/−49.5%/ **−0.49** | 1.16 | **fail_precheck** |
| **ETF-TIMING-V21-R2** | `abs(theme)×neg(ind)` | −10.8 / +0.63 | 0.01 / — | −18.9%/−49.5%/ **−0.49** | 1.16 | **fail_precheck** |
| **ETF-TIMING-V21-R3** | `Δ5(ind)/neg(theme)` | −1.0 / +0.00 | −2.37 / — | −15.9%/−50.2%/ **−0.29** | 1.16 | **fail_precheck** |
| **ETF-TIMING-V21-R4** | `max20(all)−mean5(ind)` | −9.6 / +0.79 | +0.31 / — | −9.1%/−44.1%/ **−0.12** | 1.16 | **fail_precheck** |
| **ETF-TIMING-V21-R5** | `abs(major)−mean5(ind)` | −10.6 / +0.94 | +0.31 / — | †现金 Sharpe虚高 | **0.0** | **fail_precheck**（major 自2018） |
| **ETF-TIMING-V21-R6** | `neg(ind)×max20(ind)` | −8.2 / +0.38 | −0.31 / — | −19.5%/−49.5%/ **−0.51** | 1.16 | **fail_precheck** |
| **ETF-TIMING-V21-R7** | `mean20(std10(ind)+…)` | +2.7 / **−0.51** | +0.60 / — | −24.1%/−54.7%/ **−0.61** | 1.16 | **fail_precheck** |
| **ETF-TIMING-V21-R8** | `mean10(std/theme)` | +3.0 / −0.21 | +0.40 / — | −12.7%/−40.5%/ **−0.23** | 1.16 | **fail_precheck** |
| **ETF-TIMING-V21-R9** | `mean10−max20(ind)` | −2.6 / +0.61 | +0.07 / — | −18.8%/−58.7%/ **−0.43** | 1.16 | **fail_precheck** |
| **ETF-TIMING-V21-R10** | `Δ5(theme)/max20(ind)` | −0.9 / +0.09 | +1.90 / — | −23.9%/−54.3%/ **−0.64** | 1.16 | **fail_precheck** |

† R5：`etf_share_chg_major` 仅 2018+ → X1 全 511880，按 avg_names=0 否决。  
**X2 / 100万：无一过预检 → 未开。handoff：NO。**

---

## 5. 是否可写预注册续跑？

**否。** 无候选同时满足：(1) PIT 对齐下对超额 IC>0 且稳健；(2) X1 Sharpe>0；(3) 去流残差仍有预测。  
若 AI 重开：必须 **available_at→signal_date**；适应度用 PIT 超额；禁止 trade_date 特征面板；major 叶不得撑 X1。  
当前 **不写** 可执行 prereg、不交 Strategy。不磨 LIMITUP/UNLOCK/v20。

---

## 6. 处置总表

| 裁决 | 范围 |
|---|---|
| **reject** | R1–R10 组合冒烟 |
| **research_observe** | 标签换收益方向正确；定量证明「包 ICIR≈trade_date 泄漏」 |
| promotion | **false** |
| Strategy handoff | **无** |
