# 叶验收 v2 勘误与口径裁定（ALPHA_LEAF_ACCEPT_V2_PREREG_ZH.md）

裁定方：QuantLab Alpha；日期 2026-10-14；promotion_approved=false；live=false；不跑 GP；未提交。

## 1. 冻结时间勘误
§6 所写「2026-10-14 18:06:32 ET」有误（把北京时间当成 ET），正确为 **2026-10-14 06:06:32 ET**。
sha256 计算时该行已替换为占位符，故 **sha 不变**：dffd8eef34aba24fd036e002025c919c86ca53861d77228cc56d583b058a3381。原文件不改动。

## 2. 正式口径（采纳 QuantLab AI 干跑读法）
1. B0 = B4 本身（capacity_adv/earnings_event/insider_increase），不再叠加 capacity_adv。
2. B0 = 三腿 z 按 0.5/0.25/0.25 加权；B1 = 0.8×B0 + 0.2×叶 z。
3. 主报 ρ 只对行业、市值、β 残差化；对 B0 三腿残差化后的 ρ（按构造≈0）列入附录。
4. 无连续打分的事件叶，以持仓权重作为信号。
5. ΔMDD 单列为「回撤恶化 pp」，门槛 ≤1pp。
6. 宇宙 = 锚定 top300 ∩ 当日 PIT 成员。

## 3. 干跑有效
§5「本次跳过干跑」作废；AI 按派活完成的叶11–14 干跑（output/ai_factory/leaf_reports/<leaf>/selfcheck_v2.json）有效。

## 4. §1.3「叶11 约 +0.4pp」作废
该数字基于只含 capacity_adv 的旧基准；按 B0=B4 新口径，叶11 在 60万档 ΔCAGR = −0.18pp。

## 5. 年化天数
引用任何年化指标时须注明年化天数（244 或 252）；不同天数的数字不得直接比较。

## 6. 叶11–14 裁定（记入 output/alpha/ALPHA_LEAF_ACCEPT_V2_VERDICTS_20261014.json → alpha_labels）
| 叶 | ΔIC | CMC | HC | 说明 |
|---|---|---|---|---|
| 11 report_rc_allup | −0.0013 | CMC_FAIL | HC_PASS | 60万 ΔCAGR −0.18pp；H1–H7 完整、换手 2.09%/日、前视截断 PASS；残余为 2024H1 锚定池幸存偏差与 GATE_V3 事后发现（已声明） |
| 12 analyst_recoverage | −0.0036 | CMC_FAIL | HC_REJECT | H6：换手 63.3%/日，一票否决 |
| 13 stk_surv | −0.0062 | CMC_FAIL | HC_REWRITE | H3：L=25 取 p95，约5%事件晚披露；改 p99 或剔除晚披露事件 |
| 14 insurer_surv | +0.0015 | CMC_FAIL | HC_REWRITE | 同 13 |
四叶均不派烟；原有标签（WATCH/DONE_FAIL）不变。insurer_surv 暂无验收记录，未进 alpha_labels，仅在裁定 JSON 中登记。
