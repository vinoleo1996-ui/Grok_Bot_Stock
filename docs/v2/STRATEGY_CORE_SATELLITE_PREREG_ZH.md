# 主干+卫星袖套 组合 smoke · 预登记（PREREG）

**登记时间**：2026-10-13T05:21:35-04:00（America/New_York）——**先于任何组合 NAV 运行**  
**来源**：Leo 2026-10-13 05:20 ET 经 New Bot 转达路线调整。纸面/研究级：promotion_approved=false · strategy_promotion_approved=false · live MAINBOOK=NO · sealed_claim=false · 不下单 · 不改 Mandate · 禁小盘 · 禁 GP。

## 选卫星规则（只看相关性，不看 CAGR）
X2@60万 已有 BOOK NAV，日收益扣 510300(C0) 的**超额收益**与 capacity_adv 超额的相关（附 OLS 去 β 残差相关作佐证）。取最低 3 个：
| 叶 | ρ_excess | ρ_resid | 年化波动 | 权重表 |
|---|---|---|---|---|
| etf_core_sleeve | −0.093 | −0.144 | 21.4% | output/ai_factory/g1g5_etf_core_sleeve_daily_weights_20261012_204928.parquet |
| idx_rebal_flow | −0.031 | −0.137 | 19.6% | output/ai_factory/g1g5_idx_rebal_flow_daily_weights_20261012_215737.parquet |
| lowturn | 0.829 | 0.699 | 15.5% | output/intel/g1g5_lowturn_daily_weights_20261012_112301.parquet |

注：Leo 举例的 moneyflow_resid / margin_delta 实测 ρ_excess≈0.946/0.950（13 叶中**最高**两位），按规则不入选。
主干：output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet（含 510300 压舱）。

## 固定臂（共 6，不做网格，跑后不调）
| 臂 | 主干 | etf_core_sleeve | idx_rebal_flow | lowturn |
|---|---|---|---|---|
| A1 | 0.80 | 0.20 | – | – |
| A2 | 0.80 | – | 0.20 | – |
| A3 | 0.80 | – | – | 0.20 |
| A4 | 0.70 | 0.15 | 0.15 | – |
| A5 | 0.70 | 0.10 | 0.10 | 0.10 |
| A6 风险预算 | 0.70 | 0.0864 | 0.0943 | 0.1193 |
A6 规则：主干固定 70%，余 30% 按卫星 X2 年化波动倒数分配（1/0.214:1/0.196:1/0.155）。

混合：各日按臂权重线性叠加各表 weight（同券含 510300 合并），每日合计=1；X2 内无缺 session。消费：sleeves {"core":0,"stock":1,"alpha_event":0}，不叠 core overlay；成本 strategy_v1（引擎默认）。

## 判定规则
臂**通过**仅当：CAGR > capacity_adv 单独 **且** MDD 浅于 capacity_adv 单独，**60万与100万两档同时成立**（基准：13.82%/−10.07%；12.23%/−11.62%，以本次同口径 BOOK 为准）。通过也仅标 research_observe / paper-candidate-proposal；不盖账本、不改 capacity_adv 纸面 STATUS。

## 过拟合声明
- X2 正是 capacity_adv 被选出的窗口 → 主干在 X2 上有选择偏差，组合对比也在同窗，**非样本外**。
- 卫星只按相关性选；相关性与 A6 波动亦取自 X2（样本内）。
- 低相关卫星 β≈1（近宽基），先验上可能拉高波动、拖累 CAGR；结果为探索，**非密封**。
