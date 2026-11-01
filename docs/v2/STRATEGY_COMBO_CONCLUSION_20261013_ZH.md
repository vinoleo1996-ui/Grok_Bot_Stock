# Strategy 组合路线纸面结论（2026-10-13）

- 状态：**PAPER_TRACK_2_CONFIRMED**（Leo 2026-10-13 22:46 ET 在 Strategy 聊天确认「盖章并交 Eng」）；live=false；strategy_promotion=false；密封窗不动
- 结论首次给出：2026-10-13 14:53 ET；本文件写入：2026-10-13 16:20 ET
- 窗口：X2（2024-06-03→2026-10-09），属样本内；成本开；core=0/stock=1；只做纸面

## 结论
1. 不再换卫星叶来堆叠，也不再开新的集中化变体。
2. 把三腿集中化 B4（capacity_adv/earnings_event/insider_increase = 50/25/25，每腿只取前 N 名：60万 N=6、100万 N=10，单名占全组合 ≤6%）冻结，作为与 capacity_adv 并列的第二条纸面观察轨，用 2026-11 起的前向纸面检验。
3. equity_incentive 叶只记入 WATCH，不并入组合。
4. capacity_adv 仍是唯一的纸面主干，其纸面 STATUS 不变。

## 基准
| 臂 | 60万 CAGR/MDD | 100万 CAGR/MDD |
|---|---|---|
| capacity_adv 主干 | 13.82% / −10.07% | 12.23% / −11.62% |
| earnings_event 单叶 | 13.64% / −18.29% | 13.87% / −19.08% |
| insider_increase 单叶 | 13.14% / −16.50% | 13.14% / −17.20% |
| 510300 | 11.27% / −16.24% | 11.27% / −16.24% |

## 组合结果
判定标准见三腿预注册 docs/v2/STRATEGY_THREE_LEG_PREREG_ZH.md：两档 CAGR 都高于主干，且 MDD 不深于 −15%。

| 组合 | 60万 CAGR/MDD | 100万 CAGR/MDD | 判定 |
|---|---|---|---|
| 主干+卫星 6 组（etf_core/idx_rebal/lowturn） | 均低于主干 1.9–3.2pp | — | 0/6 |
| 三腿原版 B1 等权 | 13.70% / −12.74% | 12.43% / −14.20% | 不过（60万） |
| 三腿原版 B2 逆波动 | 12.47% / −11.98% | 12.63% / −13.76% | 不过 |
| 三腿原版 B3 回撤倒数 | 12.43% / −11.98% | 12.80% / −13.08% | 不过 |
| 三腿原版 B4 50/25/25 | 12.49% / −11.95% | 13.09% / −12.75% | 不过 |
| 集中化 B1 | 15.97% / −16.49% | 14.50% / −15.22% | 不过（MDD 超 −15%） |
| 集中化 B2 | 15.73% / −15.32% | 14.63% / −14.36% | 不过（60万 MDD 超 −15%） |
| 集中化 B3 | 15.61% / −14.34% | 14.33% / −13.95% | 过 |
| **集中化 B4** | **15.11% / −13.85%** | **14.24% / −13.17%** | **过** |
| CORE 集中化（capacity_adv 单独集中） | 13.69% / −12.57% | 13.83% / −11.66% | 不胜主干 |
| 主干+equity_incentive 70/30 | 11.74% / −10.37% | 13.75% / −12.08% | 不过 |
| 主干+equity_incentive 80/20 | 11.40% / −9.94% | 12.67% / −11.41% | 不过（60万） |
| 四腿（集中化 B1×3/4 + equity_incentive×1/4） | 14.49% / −13.81% | 13.24% / −13.90% | 不胜主干（双优口径） |

相关性（相对 510300 的超额收益）：capacity_adv 与 earnings_event 为 −0.20，capacity_adv 与 insider_increase 为 +0.49，earnings_event 与 insider_increase 为 +0.09。

## 稳健性（docs/v2/BOOK_SMOKE_CONC_V2_ROBUST_SUMMARY_ZH.md）
- B4 60万：判为稳健；成本×1.5 后 14.77%，高于主干同口径的 13.41%。
- B4 100万：判为脆弱，原因是 N+1 时 CAGR 反而高 1.90pp，偏离方向向上；成本×1.5 后 13.83%，高于主干同口径的 11.89%。
- B1 两档都判为稳健，但 MDD 超过 −15%，所以不采用。

## 风险披露
- B4 的 MDD 比主干深 2–4pp，不满足「CAGR 更高且 MDD 更浅」。
- 集中化规则是在三腿原版失败后才加的，再叠加 X2 本身是样本内，存在过拟合风险。
- CORE 集中化在 100万档也比主干高 1.60pp，说明增益有一部分来自集中持股和 2025 年的行情，并不全是分散带来的。
- 原版 60万档的落差主要来自整手问题：约 11–12% 的目标股票因凑不够一手没成交。集中化后买不进的比例降到约 4–5%。
- 只做纸面；live=false，strategy_promotion=false，未盖章。

## 来源
- output/strategy_core_satellite/
- output/strategy_three_leg/
- docs/v2/BOOK_SMOKE_CONC_V2_SUMMARY_ZH.md
- docs/v2/BOOK_SMOKE_CONC_V2_ROBUST_SUMMARY_ZH.md
- docs/v2/BOOK_SMOKE_G1G5_EQUITY_INCENTIVE_COMBO_SUMMARY_ZH.md
