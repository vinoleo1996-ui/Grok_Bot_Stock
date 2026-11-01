# 组合层门 v3（MDD25）预注册 — FROZEN

- 冻结时间：2026-10-14 06:01:04 ET
- 批准：Leo 06:00 ET（经主 Agent 转达）；起草：QuantLab AI
- 适用范围：本文件冻结之后新开的所有卫星叶。已有叶不重审，除非 Leo 另行批准。

## 判定（以下四条全部满足才算通过）
叠加口径：cap80 + 叶20；集中化 topN 规则不变（60万 N=6，100万 N=10，单名 ≤6%）。
1. 叠加后 60万、100万两档的 MDD 都 ≤25%。另报 MDD ≤15% 的变体，仅作参考。
2. 叠加后两档的 CAGR 都高于 capacity_adv 单独。
3. 叶的权重经 research/alpha_decay_gate.py 判为 KEEP。常数按 ALPHA_DECAY_GATE_PREREG_ZH.md，不得改动。
4. 可交易，按 research/leaf_selfcheck_common.py 的定义：
   - 双边日换手 ≤20%；
   - 有毛超额时，成本拖累不超过毛超额的一半；
   - 没有毛超额时，成本拖累 ≤1%/年。
   - 成本按每单位换手 0.00175 计。

自检阶段的数字是复权、毛收益（扣成本前）的估计。终判以 Eng 的 Book-Smoke X2 为准，两档都要满足 1 和 2。旧的现行门以及 A、B 两种门继续并报，只作参考。

## 事后发现声明
叶11 report_rc_allup 满足本门，是在改门之前、已经看过它的回测结果之后发现的。所以本门不能用来证明叶11 有效。叶11 要不要重审，由 Leo 单独决定。

## 不变的约束
禁 GP；禁小盘；禁高杠杆；live 和 promotion 都为 false；本侧不跑 Book-Smoke；单进程 RSS ≤1.5GB。
