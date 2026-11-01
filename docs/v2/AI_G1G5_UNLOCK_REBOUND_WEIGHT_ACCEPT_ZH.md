# Alpha 裁定：G1G5 叶8 g1g5_ashare_unlock_rebound_v1 —— RESEARCH_ACCEPT → WATCH（不派 Book-Smoke）
研究级。promotion_approved=false；live=false；handoff=NO；no_gp=true；book_smoke=NOT_DISPATCHED。
裁定时间 2026-10-13 ET。复核脚本 output/alpha/verify_unlock_rebound_20261013.py，原始输出同目录 _raw.json。

## 1. 硬闸（全部复核通过）
| 项 | 结果 |
|---|---|
| 长表 date,instrument,target_weight | 是；39412 行/668 日/59 名（与 earnings_event 57448/668/86 不同；sha256 6fafa2e8…） |
| Σw 每日 | 1.0/1.0；最小权 0；无重复、无 NaN；缺交易日 0（无 stub） |
| 单名上限 | 4.00% |
| 600519/002371 | 恒 0 |
| 510300 压舱 | 均 76.7%（56%–100%），与自报一致 |
| 逐日 Jaccard vs 29 个前包（ai_factory+intel） | max 0.167（vs block_trade）＜0.7，过 |
| PIT | 110 个持仓段，入场均严格晚于 float_date 与 available_at（ann_date 18:00）；最短间隔 2 自然日，中位 4 日；0 违例 |
| 预注册先于权重 | 预注册 mtime 19:31:43 ET，权重 19:32:15 ET，顺序成立。**但**文头写「FROZEN 19:48 ET」，回执称「约 19:50 运行」，与 mtime 不符（差约 17 分钟），记档为标注缺口 |
| G6 / peak RSS | pass / 872MB（软 GAP 内） |

## 2. 自报数字复核（毛、无成本、未复权；全部一致）
毛 CAGR 11.60%（510300 9.45%，capacity_adv 12.07%）；MDD −14.89%；β 0.97；残差 α +2.26%/年；分年 α 2024 +8.89% / 2025 +2.32% / 2026 −7.41%。
- ρ 口径注：自报「ρ_excess 0.041 / 0.037」实为去β残差相关；对 510300 的原始超额相关为 0.127（vs capacity_adv）/ 0.124（vs negevent）。两种口径都 ＜0.5，正交成立。

## 3. 与其它叶的残差相关（全样本｜2024｜2025｜2026）
| vs | 全 | 2024 | 2025 | 2026 |
|---|---|---|---|---|
| capacity_adv | 0.041 | −0.185 | 0.032 | 0.142 |
| capacity_adv_negevent | 0.037 | −0.193 | 0.030 | 0.141 |
| earnings_event | 0.078 | 0.196 | 0.124 | 0.019 |
| insider_increase | 0.286 | 0.322 | 0.156 | 0.292 |
| equity_incentive | 0.237 | 0.265 | 0.012 | 0.348 |

## 4. 风险与缺口（如实标注）
1. α 逐年衰减，2026 年 −7.41%：近期机制失效迹象；与 capacity_adv 同为 2025–26 偏弱，不能对冲主干短板。
2. 压舱 76.7%：本质是「510300 + 约 6 名事件股」，β 0.97。
3. 毛 CAGR 11.60% ＜ 12% 门下沿，且未扣成本、未复权；单叶 Book-Smoke 几乎必败。
4. 事件稀：池内 73 条/58 只（年均约 25 条）。
5. 池锚定 2024-06-28 的 PIT top300 → 2024H1 轻微前视（幸存者），而 α 恰集中在 2024（+8.89%），偏乐观。
6. **弱样本外**：同一 share_float_pit 表上已有收益研究——V3_UNLOCK_WINDOW_RESID（10-12，fail_precheck）、V30 UNLOCK-SHARETYPE（U1–U5 五臂 X1 全负 Sharpe）；预注册另引中金/邢不行外部 60 日反弹结论，且持有期 60 日是看过计数后选的。方向/时点虽不同，但不算干净 OOS。
7. 脚本 research/g1g5_unlock_rebound_weights.py 文头仍是 earnings_event 模板文字（业绩预告/隔夜 gap/40 日），须改正（与 buyback_cancel 同类问题）。

## 5. Book-Smoke 判断
- 门**不变**：单叶 CAGR∈[12%,18%] 且 MDD≥−28%，60万∧100万 两档。「Leo 已不要求单叶过 12%」未见 Leo 在 Alpha 聊天的原话，**不采纳**。
- 单叶：毛 11.60% 已低于门，扣费后更低 → 不派。
- 组合诊断（毛、本地复算）：capacity_adv 单独 12.07%/−13.68%/Sharpe 0.818；70/30 12.05%/−14.03%/0.798；80/20 12.06%/−13.91%/0.808。组合在收益、回撤、Sharpe 上都不优于主干（2026 α 为负且与主干同弱），组合烟测预期无信息量 → 不建议派。
- book_smoke = NOT_DISPATCHED。

## 6. 裁定
RESEARCH_ACCEPT（硬闸全过）→ **WATCH**。不进卫星、不派烟、不晋级、不实盘、禁 GP。若 2026Q4 后补出新事件且 α 转正，可在新预注册下重评。
