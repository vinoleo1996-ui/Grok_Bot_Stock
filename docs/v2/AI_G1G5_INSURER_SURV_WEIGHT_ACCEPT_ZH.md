# 叶14 insurer_surv 权重验收记录（2026-10-14，Alpha）

- 结论：**WATCH**；**不派 Book-Smoke**；CMC_FAIL；HC_REWRITE（H3）。promotion/live=false，handoff=NO。
- 权重：output/ai_factory/g1g5_insurer_surv_daily_weights_20261014_175849.parquet（sha 见 JSON）
- HC：H3 披露滞后 L=25 取 p95，约 5% 事件披露晚于 25 日，有残余前视风险。须改为 p99 或剔除迟披露事件后重写，未重写前不得再提交。
- CMC：ΔIC < +0.003，不过。
- 新口径 GATE_V3（T+1、净、244）：60万 14.16%/−14.77% vs capacity_adv 13.93%/−14.24%；100万 18.53%/−12.29% vs 17.77%/−12.47%。CAGR 两档都过，MDD 也过，换手 2.27%/日；但衰减门 v1.1 为 DECAY_DOWNGRADE（H2：净 CAGR ≤ 510300），所以 **FAIL**。
- 标记：≥3 家保险机构计数用的 rece_org 未做归一，家数可能虚增。
- JSON：output/alpha/AI_G1G5_INSURER_SURV_WEIGHT_ACCEPT_20261014.json
