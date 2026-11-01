# 预注册：组合层 walk-forward 优化（是否存在比 B4 帕累托更优的组合）

- 冻结时间：2026-10-14 01:25 ET（写于任何搜索/收益读取之前）
- 作者：QuantLab Strategy（研究执行）
- 门锁：只做纸面；live=false；promotion=false；禁 GP；禁小盘；L≤1.0（不加杠杆）；密封窗不碰；不改 capacity_adv / B4 两条纸面轨的 STATUS、FROZEN_CONFIG 及任何冻结文件；不盖章。
- 样本：X2 探索窗 2024-06-03 → 2026-10-09（样本内，已被多轮研究看过，结论只能是「研究级」）。

## 1. 候选腿（文件写死）
| 腿 | 文件 | 门状态 |
|---|---|---|
| cap = capacity_adv | output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet | 过 Alpha 门（主干） |
| ee = earnings_event | output/ai_factory/g1g5_earnings_event_daily_weights_20261014_005430.parquet | 过 |
| ins = insider_increase | output/ai_factory/g1g5_insider_increase_daily_weights_20261014_011841.parquet | 过 |
| eq = equity_incentive | output/ai_factory/g1g5_equity_incentive_daily_weights_20261014_023222.parquet | 过（两档） |
| rc = 叶11 report_rc_allup | output/ai_factory/g1g5_report_rc_allup_daily_weights_20261014_122118.parquet | RESEARCH_ACCEPT→WATCH，Book-Smoke 未派（无引擎门数字） |

其它 WATCH 叶（margin_delta、moneyflow_resid、accrual_quality、northbound、indcap_momneut_ocf、d1_val_resid、idx_rebal_flow/predict、etf_core_sleeve、friction_cost、analyst_recoverage、block_trade、buyback_cancel、interim_div、unlock_rebound）：Book-Smoke 已灭/DONE_FAIL 或未派且 Alpha 判为无组合价值 → **不纳入**（未过 Alpha 门）。

## 2. 构造规则（沿用 B4 v2，不改）
每腿每日取原权重前 N 名个股（60万 N=6，100万 N=10），腿内个股预算按比例放大回原个股总额；腿内 ETF 原样；合并后单名 ≤6%，超出部分进 510300；逐日归一。代码复用 research/small_aum_conc_lib.py 的 run_group 逻辑。
风险叠加（R 类）：只缩放个股部分，缩下的权重进 511880.SH（货币 ETF，引擎原生停车位），不加杠杆。信号只用 t−1 及以前数据。

## 3. 网格（共 16 组，写死，不增不改）
静态配比（cap/ee/ins/eq/rc）：
- S0 = B4 50/25/25/0/0（参照，计入尝试数）
- S1 40/20/20/20/0
- S2 25/25/25/25/0
- S3 45/22.5/22.5/0/10（叶11 90/10：0.9×B4 + 0.1×rc）
- S4 40/15/15/15/15
- S5 60/40/0/0/0
- S6 50/25/0/25/0
训练段定权重（每折各自拟合）：
- D1 逆波动 cap/ee/ins（训练段腿日收益波动）
- D2 逆波动 cap/ee/ins/eq
- D3 逆波动 五腿
- D4 最小方差 cap/ee/ins/eq，长仓，单腿权重 ∈[0.10,0.60]
- D5 在 S0–S6 中选训练段 Calmar 最高者
风险叠加（参数写死）：
- R1 = S0 + 回撤触发：筛选净值自高点回撤 ≤−8% → 个股×0.5；回撤恢复到 ≥−4% 才复位
- R2 = S0 + 波动目标：20 日实现波动年化目标 14%，缩放系数 ≤1
- R3 = D5 + R1 规则
- R4 = S1 + R1 规则

## 4. walk-forward 切分（写死）
- F1：训练 2024-06-03→2024-12-31；验证 2025-01-02→2025-07-31（落在 2025-08 之前）
- F2：训练 2024-06-03→2025-07-31；验证 2025-08-01→2026-10-09
D 类在每折训练段定权重，验证段固定不动；引擎用权重文件按「2025-07-31 前用 F1 权重、之后用 F2 权重」拼接。S/R 类无拟合参数。

## 5. 筛选与判定
- 快速筛选：腿权重×复权日收益（t−1 权重），成本近似 0.16%×单边换手。只用于决定送引擎的候选，最多送 4 组。
- 送引擎条件：两档、两折验证段，候选 CAGR ≥ 同段 S0 且 MDD ≥ 同段 S0（不劣），至少一项严格更优；验证段 MDD 不深于 −15%。
- 引擎复核：Eng book-smoke，sleeves core=0/stock=1，成本开，60万/100万，X2，单进程串行。
- **最终判定（以引擎数字为准）**：两档 X2 全窗 MDD 都不深于 −15%，且两档在两折验证段（引擎 nav 切段）CAGR 与 MDD 都不劣于 B4、至少一项严格更优 → 「帕累托优于 B4」。否则不过。跑完不调参，不补组。
- 指标：CAGR、MDD、Calmar、月胜率、日胜率、换手、成本、2025-08 前后分段、分年；图+表；报告全部 16 组（含失败）。
