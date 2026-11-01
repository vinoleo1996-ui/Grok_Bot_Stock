# S6 影子纸面候选 预注册（2026-10-14）

- 状态：SHADOW_PAPER_CANDIDATE。未盖章；不替换 B4；不动任何冻结文件；live=false；strategy_promotion=false。
- 来源：组合层 walk-forward（docs/v2/STRATEGY_WF_COMBO_RECEIPT_ZH.md）。S6 是 16 组全部用引擎跑过之后**事后挑出来的**，不是按预注册的 walk-forward 规则选出的；X2 是样本内。总尝试数为 16。
- 定义（冻结）：capacity_adv / earnings_event / equity_incentive = 50/25/25；每腿取前 N 名，60万 N=6、100万 N=10；单名占全组合 ≤6%；sleeves core=0/stock=1；成本按 strategy_v1。换仓节奏照搬各腿冻结规则：capacity_adv 腿月末换仓，事件腿按事件换仓。
- X2 引擎成绩（仅供参考，属样本内）：60万 17.15%/−11.95%，100万 16.37%/−12.66%。

## 前向
- 自 2026-11-02 起，与 B4、capacity_adv 两条纸面线并列跑 FWD 窗口，60万和100万两档都跑；X2H 衔接段单独列出，不计入业绩。
- 每月报告：CAGR、MDD、Calmar、月胜率、成交率、买不进占比、成本。

## 淘汰与替换规则（事先写死）
- 淘汰（任一条成立即停跟踪）：前向 MDD 深于 −15%；或前向满 6 个月时，两档 CAGR 都低于 B4 前向且 MDD 都更深。
- 替换 B4 的候选资格：前向至少满 6 个月，且两档都满足 CAGR ≥ B4 前向、MDD 不深于 B4 前向，同时 MDD 不深于 −15%。满足后也只是提交 Leo 决定，不自动替换。
- 期间不调参、不改配比、不新增腿。

## 依赖
- equity_incentive 权重 output/ai_factory/g1g5_equity_incentive_daily_weights_20261014_023222.parquet 需要由 AI 提供按冻结规则续出的脚本；Eng 按 B4 的做法钉住哈希。
- 由 Alpha 同步做稳健性审查（N±1、剔除头部个股、成本×1.5、分段），只报告，不用于选参。
