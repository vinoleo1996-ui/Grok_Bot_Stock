# 叶15 tp_rerate 权重验收记录（2026-10-14，Alpha）

- 结论：**WATCH / DONE_FAIL**（主 Agent 定）；**不派 Book-Smoke**；promotion/live=false。
- 新口径 GATE_V3（T+1、净、244）FAIL：60万 13.85%/-14.40%，低于 capacity_adv 13.93%；100万 17.21%/-12.72%，低于 17.77%。衰减门 v1.1 DECAY_DOWNGRADE（最新 α<0，净 CAGR ≤ 510300），换手 1.72%/日。
- 目标价取 report_rc 的 max_price/min_price（取 >0 者的均值），**没有用 tp**：tp 是利润总额。
- 机构数：AI 归一后复核，未虚增。
- JSON：output/alpha/AI_G1G5_TP_RERATE_WEIGHT_ACCEPT_20261014.json；重判：ALPHA_GATEV3_REJUDGE_NEWBASIS_20261014_ZH.md
