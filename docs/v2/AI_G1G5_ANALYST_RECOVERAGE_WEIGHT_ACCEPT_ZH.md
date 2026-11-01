# Alpha 裁定：g1g5_ashare_analyst_recoverage_v1（叶12，分析师断档后重新覆盖）
**结论：RESEARCH_ACCEPT（硬闸过）→ WATCH；book_smoke = NOT_DISPATCHED。** promotion_approved=false；live=false；handoff=NO；禁 GP。

- 权重：output/ai_factory/g1g5_analyst_recoverage_daily_weights_20261014_122813.parquet，sha256 bd43e0ec…7b53（已核一致）；198,396 行 / 668 日 / 297 名。
- 预注册：AI_G1G5_ANALYST_RECOVERAGE_WHO_PAYS_PREREG_ZH.md，FROZEN 00:28:09 ET；权重落盘 00:28:34 ET → 预注册先于权重（仅 25 秒）。
- 复核口径：复权价（research/adj_price.py；510300 close_hfq），毛收益无成本；脚本 output/alpha/verify_analyst_recoverage_20261014.py，输出 .out.json。

## 1. 硬闸（全过）
长表 date,instrument,target_weight；Σw≡1；无负权/重复/NaN/缺日（无 stub）；单名 max 4%；600519/002371 恒 0；510300 压舱恒 20%（无全压舱日）。
逐日 Jaccard vs 36 个前包：max 0.216（capacity_adv），vs earnings_event 0.136 → 远低于 0.7。
PIT：代码构造 T1=report_date 后首个交易日、T2=次一交易日入场，收益 shift(1)，严格晚于可得日。代理检查 5297 次入场全部有前置事件；631 次“最近事件距入场<2 日”系池内满 20 名轮换重新入场被新事件代理误配，非构造违规（AI 已注意时可补 per-event 审计）。G6 pass；peak RSS 1241MB（软 GAP）。
附注：权重脚本头部 docstring 仍为 report_rc_allup 模板文字（“>=3 orgs all raise…”），请 AI 修正。

## 2. 自报数复核（一致）
毛 CAGR 13.80% / MDD −15.17% / Sharpe 0.73 / β 1.00；残差 α +1.64%（2024 **+14.05**｜2025 **−5.79**｜2026 **−5.70**）→ α 只在 2024、此后两年为负，衰减。
去 β 残差相关：capacity_adv 0.043｜report_rc_allup 0.095｜earnings_event 0.268｜insider_increase 0.330｜equity_incentive 0.466；2026 年内 0.175/0.080/0.156/0.454/0.462（与 insider/equity_incentive 有明显共性）。

## 3. 事件重合
入场当日已被 report_rc_allup 持有：162/5297（3.1%）；落在 report_rc_allup 入场后 60 日窗内 172（3.2%）；落在 earnings_event 入场后 40 日窗内 184（3.5%）。与 AI 自报（2.6%/3.1%）同量级 → 事件层基本独立。

## 4. 弱样本外：是（弱）
同一数据源 data/v2/events/report_rc_2018plus.parquet 已在叶11 report_rc_allup（00:22 ET 出收益）做过收益研究，早于本叶预注册冻结（00:28）。规则不同，但同数据、同研究者、6 分钟内 → 判弱 OOS。另：池锚 2024-06-28 的静态 top300 对 2024 上半年有轻微前视，而本叶 α 恰集中在 2024。

## 5. 组合门（docs/v2/ALPHA_GATE_COMBO_LEVEL_20261013_ZH.md，不放松）
| 口径 | capacity_adv 单跑 | 90/10 | 80/20 | 70/30 |
|---|---|---|---|---|
| 本侧简单混合（毛，复权） | 17.66% / −13.18% | 17.35% / −13.01% | 17.02% / −12.85% | 16.68% / −12.69% |
| AI 60万 | 14.96% / −13.63% | – | 12.74% / −15.63% | 11.61% / −16.85% |
| AI 100万 | 18.85% / −12.25% | – | 19.62% / −12.70% | 19.47% / −13.29% |

本侧混合：MDD 略浅但 CAGR 每档都低；AI 分档：60万 CAGR 与 MDD 都更差，100万 MDD 更深。无一口径两档同时 CAGR 与 MDD 双优 → **组合门不过，不派 Book-Smoke**。

## 6. 缺口
α 2025/2026 为负且衰减；单边日均换手 31.6%（扣费后更差）；事件极密，近似池内高换手轮动；弱 OOS；与 equity_incentive/insider 2026 残差相关 ~0.46；脚本头模板残留。
