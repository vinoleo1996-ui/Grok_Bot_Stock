# 叶17 major_contract_growth（成长行业重大合同/中标）回执
时间：2026-10-14 08:10:10 ET（AI）。预注册：docs/v2/AI_G1G5_MAJOR_CONTRACT_GROWTH_WHO_PAYS_PREREG_ZH.md（FROZEN 07:56:48 ET；Leo 07:56/07:58 修订附录于读收益前写入；prereg sha 8e2d385c202a2f3d…）。
扫描：docs/v2/AI_LEAF17_CANDIDATE_SCAN_ZH.md。事件脚本 sha 4c641ee0ef51dcf3…。promotion=false；live=false；禁 GP/高杠杆；**未跑 Book-Smoke/8787**。

## 结论：WATCH（DONE_FAIL 倾向）
- 主交付为 **base-α 向量**（分域标定 + 行业/市值残差）；快门 1–3 日成交额单独存，未与 α 加权合成。
- 同构闸：Jaccard max 全 <0.1（远低于 0.7）→ 过；ρ_excess 最高 equity_incentive 0.41（FULLA）/0.38（HI_LIQ）<0.5 → 过（未降为过滤）。
- 可交易闸：**不过**（成本拖累 > 毛超额一半；换手约 7.3–7.5%/日）。
- 衰减门 v1.1：KEEP（两宇宙）。
- Gate A（残差 α>0）：**不过**（FULLA −2.47% / HI_LIQ −1.50%，244 年化）。
- Gate B（cap80+叶20 vs capacity_adv）：FULLA **两档都赢**（60万 +1.01pp / 100万 +0.14pp）；HI_LIQ 60万 −0.11pp / 100万 +0.10pp → **不过**。
- GATE_V3：FAIL（不可交易；HI_LIQ 另有 60万 CAGR 不过）。
- Leo「跑不赢主干即砍」：单叶毛/净 CAGR 均远低于 capacity_adv；仅 FULLA 叠加档形式上过 Gate B，但不可交易 + 残差 α 负 + 2025 残差深度为负 → **不派 Book-Smoke，WATCH**。
- 密封窗（描述性，Leo 07:50 授权报告）：HI_LIQ 净 CAGR −0.90%、α −0.99%；FULLA 重叠段净 −7.76%、α +2.49%（样本短）。不作晋级证据。

## 短名单与选定
见扫描文档。三候选：major_contract_growth / rating_upgrade_cluster / pharma_tech_milestone。按数据质量+低重合+07:58 工艺（白名单+慢α/快gate）选定 **major_contract_growth**。

## 冻结与计数
| 项 | 值 |
|---|---|
| 冻结 ET | 2026-10-14 07:56:48（事件脚本）；07:57:19 / 07:58:58 范式修订（读收益前） |
| 事件脚本 sha256 | 4c641ee0ef51dcf3a162798d869bd7366d88ecb07ff754d40d68216a3cee0681 |
| 计数闸 | FULLA X2 324/124、月均 11.63；HI_LIQ X2 287/114、月均 10.3 → **PASS** |

## 产物（α 主交付）
| 宇宙/窗 | α | gate | eval weights |
|---|---|---|---|
| FULLA X2 | `output/ai_factory/leaf17_major_contract_growth/alpha_FULLA_x2_*.parquet` | gate_FULLA_x2_* | eval_weights_FULLA_x2_* |
| HI_LIQ X2 | alpha_HILIQ_x2_* | gate_HILIQ_x2_* | eval_weights_HILIQ_x2_* |
| HI_LIQ sealed | alpha_HILIQ_sealed_* | gate_* | eval_weights_* |
| FULLA sealed∩mask | alpha_FULLA_sealed_* | | |

## 判定表（X2；244 主报）
| 项 | FULLA（研究主） | HI_LIQ |
|---|---|---|
| 单叶毛 CAGR / MDD | 7.75% / -18.63% | 9.04% / -19.92% |
| 净 CAGR（T+1，17.5bp） | 7.73% | 7.74% |
| 残差 α 总 / 2024 / 2025 / 2026 | -2.47 / 4.78 / -13.72 / 6.88 | -1.5 / 1.64 / -11.68 / 9.59 |
| 双边换手/日；成本拖累/年 | 7.46%；3.19% | 7.25%；3.1% |
| 可交易 | 否 | 否 |
| 衰减门 | KEEP | KEEP |
| ρ vs capacity_adv / equity_incentive | -0.352 / 0.412 | -0.401 / 0.377 |
| Jaccard max（全对比叶） | 0.086 | 0.094 |
| cap80+叶20 ΔCAGR 60万/100万 | 1.01pp / 0.14pp | -0.11pp / 0.1pp |
| GATE_V3 | FAIL | FAIL |

## 密封窗（描述）
| 宇宙 | 净 CAGR | 毛 CAGR | 残差 α | 衰减 | 可交易 |
|---|---|---|---|---|---|
| HI_LIQ | -0.9% | 1.95% | -0.99% | KEEP | 否 |
| FULLA（掩码重叠） | -7.76% | -5.79% | 2.49% | KEEP | 否 |

## Arch TODO（本叶未改 leaf_selfcheck_v3）
1. P1 退市终值收益；2. P2 验收残差宇宙切 FULLA/HI_LIQ（当前 factor_report 仍 mid_large top300）。
## 披露
- X2 构建峰值 RSS ≈1.95GB（>1.5GB 目标；密封 HI_LIQ ≈1.53GB）。下次应只载事件票成交额并分宇宙分进程。
- 快门缺成交额时 fail-open（gate=1），已在脚本注释；gate 通过率极高（>99%），门偏松，可能削弱可交易性惩罚的区分度。
- 交 Alpha ACCEPT 复核；预期 WATCH。不自跑 Book-Smoke。
