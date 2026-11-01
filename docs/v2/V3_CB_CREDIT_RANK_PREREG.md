# V3_CB_CREDIT_RANK_PREREG — 纯债溢价（bond_over_rate）低值排序
研究级，promotion_approved=false。写于 2026-10-12 03:07 ET，运行前。
## ≠ MATPREM / PREMRESID / IND-RATE / CALL-HEAT
排序键=`bond_over_rate`（信用/债底溢价），**不是** `cb_over_rate`；与转股溢价相关≈0。无 510300 腿。
## 规则
转股期 ∩ ADV≥1e7 ∩ remain≥1e8 ∩ 非强赎；取 bond_over_rate **最低** min(15,n) 等权；CB50%+**518880**50%。全量面板。
硬闸 avg_names>0 且 Sharpe>0；正式 X2≥12%。

## Strategy 台账附记（2026-10-12T03:12:06-04:00）
X1 Sharpe 预检失败（Sharpe≈**−0.02**；avg_names≈5.3）→ **fail_precheck**；未开正式双窗；无交接；ortho4。
源：`output/v3/cb_credit_rank/`。台账：`descriptive_CB_CREDIT_RANK_fail_precheck`。**promotion_approved=false**；GOLD only。
