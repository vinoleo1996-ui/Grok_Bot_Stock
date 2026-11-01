# V3_CB_RESET_COOL_PREREG — 下修事件冷却剔除后 ADV 等权
研究级，promotion_approved=false。写于 2026-10-12 03:07 ET，运行前。
## ≠
事件冷却（下修后 60 日剔除），**不**按溢价/残差/热度排序。≠ MATPREM，≠ IND-RATE。
## 规则
转股期 ∩ ADV≥1e7 ∩ remain≥1e8 ∩ 无近 60 日「下修」available_at；ADV top min(15,n) 等权；CB50%+GOLD50%。全量面板。同闸门。

## Strategy 台账附记（2026-10-12T03:12:06-04:00）
正式双窗 **fail_explore**：X2 MDD≈**−27.4%/−27.5%** >25%（60/100万 `results.json`）；预检过、正式未过；无交接；ortho4。
源：`output/v3/cb_reset_cool/`。台账：`descriptive_CB_RESET_COOL_fail_explore`。**promotion_approved=false**；GOLD only。
