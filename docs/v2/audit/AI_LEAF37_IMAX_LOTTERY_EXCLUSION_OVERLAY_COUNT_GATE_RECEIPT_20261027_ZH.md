# 叶37 IMAX/隔夜彩票剔除 overlay HI_LIQ 轻量计数闸短回执（2026-10-27）

- 角色：QuantLab AI（后台执行器）
- 时点：2026-10-27 16:45 ET（America/New_York；ISO `2026-10-27T16:45:00-04:00`）
- 状态：轻量计数完成；**非** X2 / selfcheck / Book-Smoke；**未**申 `.ok`；**未**挂/抬 QUIET；**未**改叶33 `afbbe7e7` / 叶35 `434ff42c`；`research/leaf36*` / `research/leaf37*` **ABSENT**。
- 预检：`pgrep -f 'kline.py|export_static.py|snapshot.py|gen.py'` → **EMPTY_OK**。
- `live=false`；`promotion_approved=false`；`EXECUTED_full_alpha=false`。
- mechanism_tag：`g1g5_ashare_imax_lottery_exclusion_overlay_v1`
- 上游：叶36 inquiry **HOLD CLOSED** → 改派备选 A；**未**放宽叶36 覆盖阈
- dig：磁盘现算 **`74234fca`** MATCH

## 结论

| 项 | 值 |
|---|---|
| **gate_pass** | **`true`** |
| 规则 | `computable_median>=300 AND excl_median>=30 AND zero_frac<=0.05 AND jaccard_max vs leaf18/18v/27 <0.7 (rho>0.5 strength-only；leaf24 disclose-only)` |
| APPROX | **是**（醒目；IMAX_proxy=raw r_id top5/20d） |
| 峰 RSS | **1030.1 MB**（rss 意向 1500 禁抬） |
| MemAvailable 起/止 Gi | 12.432 / 11.882 |
| X2/selfcheck/Book-Smoke | **未开** |
| 建议改升备选 B | **否**（PRIMARY 过闸；B 仅登记不升） |

## 覆盖（X2 样内 HI_LIQ；再平衡每 20 交易日）

窗：2024-06-03 → 2026-10-09；n_rebal=30。  
口径：HI_LIQ ∩ 可算 `IMAX_proxy`（raw `r_id` 20 日 top-5 均，有效日≥15）。

| 口径 | median | min | p10 | 零覆盖日占比 |
|---|---:|---:|---:|---:|
| **可算 IMAX 名（masked）** | **2816.5** | 1179.0 | 1475.4 | **0.0**（0/30） |
| top-20% 高 IMAX 剔除名数 | **564.0** | 236.0 | 295.5 | — |
| HI_LIQ 宇宙规模 | 3154.0 | 1480.0 | 1684.6000000000001 | — |
| 掩码后曾可算票数（并集） | 4927 | | | |

## 重叠（最多 6 个均匀再平衡日）

样本日：2024-06-03, 2024-11-28, 2025-05-30, 2025-10-28, 2026-04-27, 2026-10-09

**定义（写死）**：本叶剔除集 = HI_LIQ 内 `IMAX_proxy` top_q=0.20；对照「高风险尾」= 对照 α 的**最低** top_q=0.20（叶18/18v/27/24 的 α 均为「低风险优先」极性：α≈−ivol 或 −IMAX，故低 α = 高波动/高 IMAX 侧）。ρ = Spearman(−IMAX_proxy, α)。

| 对照 | ρ_mean | ρ_max | J_mean | J_max | 强度过滤 ρ_mean>0.5 | 硬拒 J≥0.7 |
|---|---:|---:|---:|---:|---|---|
| 叶18（sha8 `1a42f9e8`） | 0.5051 | 0.5240 | 0.2911 | **0.3107** | True | **False** |
| 叶18v（sha8 `237e760c`） | 0.5051 | 0.5240 | 0.2911 | **0.3107** | True | **False** |
| 叶27（sha8 `652b8a68`） | 0.6653 | 0.7468 | 0.3261 | **0.4430** | True | **False** |
| 叶24（披露；年 sha 0ccc0f96/70a2cc47/5a1fc629） | 0.3806 | 0.4554 | 0.2004 | **0.2229** | False | **不计入硬拒**（反同构靠交付形态 A） |

**叶18 vs 叶18v（醒目）**：样本日共同行 n=17411；α corr≈0.9999999999999998；MAE=0.0 → 样本日 α **数值恒等**（文件 sha 不同；重叠读数因此重合）。硬拒仍按 ≥0.7 规则执行（本拍未触）。

说明：Jaccard≥0.7 硬拒本拍**未触**；ρ>0.5 强度过滤对叶18/27 **已触**（披露-only，不解阻也不单独废叶）。**未算**收益/IC/CAGR。叶24 重叠中等偏低（proxy≠全 e_id + 叶24 另残差叶18/18v），反同构靠 **形态 A overlay ≠ 完整主叶**。

## APPROX / GAP

**APPROX（醒目）**
- `IMAX_proxy` = raw `r_id` 20 日最大 5 日均值（≥15 有效），**不是**叶24 全路径 `e_id`（SW L1 + logmv_{t−1}）
- top_q=0.20 为 DRAFT 冻结意向，**未**读收益选阈值
- 无完整 overlay 向量落盘；无 `--allow-real-data` 长跑
- 叶18v 样本日与叶18 α 恒等 → 正交读数不双计增量信息

**GAP**
- 未跑全 e_id 残差 IMAX 覆盖对照（冻结/脚本窗可补）
- 未算 vs 叶34/35/36 剔除集 Jaccard（X2 阶段可补）
- 连续 soft-penalty + SW+style 未构建

输入 sha8：hiliq=`c5433e80`；panel 年={"2023": "6588573a", "2024": "bbbfe95a", "2025": "164cde98", "2026": "8df4afec"}；leaf18=`1a42f9e8`；leaf18v=`237e760c`；leaf27=`652b8a68`。

## 备选 B（登记不升）

> 本拍 PRIMARY 过闸，**不**建议改升。若后续硬拒：备选 **(B) 行业级客户动量（先 IO 表 PIT 可得性）**——**勿自开**。

## 产物钉

| 文件 | 备注 |
|---|---|
| who_pays | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` |
| COVER | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_COVER_DRAFT_20261027_ZH.md` |
| 计数脚本 | `/tmp/quantlab_leaf37_imax_lottery_exclusion_count_gate.py` + audit 副本 |
| JSON | `output/ai_factory/leaf37_imax_lottery_exclusion_count_20261027.json` |
| dig | `74234fca` |

下一跳：priority 回主 → 排号 → Arch 只审不签 →（另窗）FROZEN→独立 X2；叶36 inquiry 不复开；备选 B 不升；不推 Leo；≠X2 ACCEPT。
