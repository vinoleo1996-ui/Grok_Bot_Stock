# Alpha 裁定：g1g5_ashare_report_rc_allup_v1（分析师全部上调事件）
**结论：RESEARCH_ACCEPT → WATCH；book_smoke = NOT_DISPATCHED。** promotion_approved=false；live=false；handoff=NO；禁 GP。

- 权重：output/ai_factory/g1g5_report_rc_allup_daily_weights_20261014_122118.parquet，sha256 c980c703…e1b2（已核，一致）；50100 行 / 668 日 / 75 名。
- 预注册：AI_G1G5_REPORT_RC_WHO_PAYS_PREREG_ZH.md，FROZEN 00:20:59 ET；权重落盘 00:22:49 ET → 预注册先于权重。
- 复核口径：复权价（research/adj_price.py；510300 close_hfq），毛收益、无成本；脚本 output/alpha/verify_report_rc_allup_20261014.py。

## 1. 硬闸（全过）
Σw≡1；无负权、无重复、无缺日（无 stub）；单名 max 4%；600519/002371 恒 0；压舱 510300 均 68.8%（20%–100%，全压舱 130 天）。
逐日 Jaccard vs 35 个前包：max 0.25（buyback_cancel），vs earnings_event 0.167、vs capacity_adv 0.111 → 远低于 0.7。
PIT：98 次入场全部有前置事件，事件窗结束后最少 2 个交易日入场（T2），0 违规。G6 pass；peak RSS 1112MB。

## 2. 自报数复核（一致）
毛 CAGR 16.65% / MDD −17.50% / Sharpe 0.88 / β 1.01；残差 α +3.76%（2024 −0.43｜2025 +4.29｜2026 +6.35）。
去 β 残差相关：capacity_adv 0.038｜earnings_event 0.105｜insider_increase 0.116｜equity_incentive 0.100；2026 年内分别 0.128/0.047/0.246/0.165。

## 3. 预注册第 3 条（AI 未算，本侧补）
本叶 98 次入场中，同票落在 earnings_event 事件窗（其 T2 入场起 40 日）内的只有 6 次，占 **6.1%**（远低于 50% 标注线）→ 事件层与 earnings_event 基本不重合，是独立新叶。

## 4. 弱样本外
盘上无 report_rc 的先验收益研究 → 不判弱 OOS。备注：冻结前看过满窗事件计数（含 2018–2021 封存窗，仅计数无价格）；规则取自国信外部研究。

## 5. 组合门（Leo 2026-10-13 确认的组合层口径，不放松）
| 口径 | capacity_adv 单跑 | 90/10 | 80/20 | 70/30 |
|---|---|---|---|---|
| 本侧简单混合（毛，复权） | 17.66% / −13.18% | 17.62% / −13.61% | 17.56% / −14.05% | 17.49% / −14.48% |
| AI conc v2 60万 | 14.96% / −13.63% | – | 15.41% / −14.12% | 15.62% / −14.37% |
| AI conc v2 100万 | 18.85% / −12.25% | – | 20.40% / −12.41% | 20.73% / −12.88% |

两种口径下 MDD 两档都比主干深；本侧简单混合连 CAGR 也略低。门要求 CAGR 与 MDD 两档同时优于主干 → **不过**，不派 Book-Smoke。

## 6. 缺口
组合回撤加深；2024 α 为负；压舱 69%；β≈1 非防守；只用定期报告触发（预告/快报满窗源缺）；机构名未归一。
