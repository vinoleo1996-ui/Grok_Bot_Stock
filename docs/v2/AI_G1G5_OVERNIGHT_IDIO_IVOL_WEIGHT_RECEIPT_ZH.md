# 叶18 overnight_idio_ivol（隔夜特质波动）回执
时间：2026-10-14 09:04:59 ET（AI）。预注册：docs/v2/AI_G1G5_OVERNIGHT_IDIO_IVOL_WHO_PAYS_PREREG_ZH.md（FROZEN 08:25:59 ET；覆盖附录读收益前；prereg sha b00a1f9ea5e50cf9…）。
扫描：docs/v2/AI_LEAF18_CANDIDATE_SCAN_ZH.md（HARD PIVOT 修订：选②）。原 tech_qual_cert **ABORTED**。
promotion=false；live=false；禁 GP/高杠杆；**未跑 Book-Smoke/8787**；**不交 Alpha**（闸门未过）。

## 结论：WATCH（DONE_FAIL 倾向）
- 主交付为 **base-α 向量**（α=−20日特质隔夜 ivol；分域标定 + 行业/市值残差）；快门 1–3 日隔夜左尾单独存，未与 α 加权合成。
- 同构闸：Jaccard max 全 <0.06 → 过；ρ_excess 最高 equity_incentive ≈0.46（HI_LIQ）/<0.5 → 过（未降为过滤）。vs capacity_adv ρ≈−0.26。
- 可交易闸：**不过**（双边换手 ≈20.9%/日 >20%；成本拖累 > 毛超额一半）。
- 衰减门 v1.1：**DECAY_DOWNGRADE**（非 KEEP）。
- Gate A（残差 α>0）：**不过**（HI_LIQ α_ann_leaf **−5.26%**；FULLA 见下）。
- Gate B（cap80+叶20 vs capacity_adv）：HI_LIQ 60万 **−2.38pp** / 100万 **−1.32pp** → **不过**。FULLA 60万 +0.25pp / 100万 −0.29pp → **不过**。
- GATE_V3：**FAIL**（不可交易 + 衰减非 KEEP + CAGR 未双档高于主干）。
- Leo「跑不赢主干即砍」：单叶净 CAGR 低于 capacity_adv；叠加两档不优于主干 → **WATCH，不派 Book-Smoke，不交 Alpha**。

## 短名单与选定
① 应计/RNOA（应计叶已烟灭，同族风险）/ ② 隔夜-日内·特质波动 / ③ 脱敏 SUE（无一致预期）。按 PIT 就绪度 + 低预期 ρ vs capacity_adv 选定 **② overnight_idio_ivol**。

## 冻结与覆盖
| 项 | 值 |
|---|---|
| 冻结 ET | 2026-10-14 08:25:59 |
| 覆盖闸 | HI_LIQ sealed/X2 median valid ivol 1754/3075；FULLA X2 4954 → **PASS** |
| 方向 | 冻结为低特质隔夜波动优先（α=−ivol）；未事后改规则 |

## 产物（α 主交付）
| 宇宙/窗 | α / gate / eval weights |
|---|---|
| HI_LIQ X2（主） | `output/ai_factory/leaf18_overnight_idio_ivol/alpha_HILIQ_x2_*` 等 |
| FULLA X2（对照） | alpha_FULLA_x2_* |
| HI_LIQ sealed | alpha_HILIQ_sealed_* |
| FULLA sealed∩mask | alpha_FULLA_sealed_* |
| 自检链 | `g1g5_overnight_idio_ivol_hiliq_daily_weights_20261014_205327.parquet` |

## 判定表（X2；244 主报；复权+净+T+1）
| 项 | HI_LIQ（主） | FULLA（对照） |
|---|---|---|
| 单叶毛 CAGR | 14.66% | 20.02% |
| 净 CAGR（T+1，17.5bp） | 4.85% | 9.55% |
| 残差 α 总 / 2024 / 2025 / 2026 | -5.26 / -2.48 / -6.98 / -5.14 | -0.56 / 11.02 / -2.15 / -7.44 |
| 双边换手/日；成本拖累/年 | 20.9%；8.92% | 20.9%；8.92% |
| 可交易 | 否 | 否 |
| 衰减门 | DOWNGRADE | DOWNGRADE |
| ρ vs capacity_adv / equity_incentive | -0.259 / 0.463 | -0.220 / 0.457 |
| Jaccard max | 0.053 | 0.053 |
| cap80+叶20 ΔCAGR 60万/100万 | -2.38pp / -1.32pp | 0.25pp / -0.29pp |
| GATE_V3 | FAIL | FAIL |

## 密封窗（描述性，不作晋级证据）
| 宇宙 | 净 CAGR | 残差 α | MDD |
|---|---|---|---|
| HI_LIQ | −8.64% | −8.73% | −53.5% |
| FULLA（掩码重叠） | −1.77% | +9.36% | −27.2% |

## Arch TODO（本叶未改 leaf_selfcheck_v3）
1. P1 退市终值收益；2. P2 验收残差宇宙切 FULLA/HI_LIQ（当前 factor_report 仍 mid_large top300）。**不阻塞本叶结论。**

## 披露
- 峰值 RSS：HI_LIQ X2 ≈1.26GB（达标）；FULLA X2 / HI_LIQ sealed 峰值约 1.74–1.88GB（>1.5GB 目标，已披露）。
- 「intraday」= 日线 open/close 分解，非分钟线。
- 再平衡每 5 日导致换手偏高（~21%/日）→ 不可交易；未事后改冷却/再平衡规则。
- **不交 Alpha ACCEPT**（主 Agent：闸门失败 → WATCH，no Alpha）。
