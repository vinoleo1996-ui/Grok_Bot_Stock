# V3_CB_PUT_AVOID_PREREG — 回售提示剔除后的流动性 CB 袖套
研究级，promotion_approved=false。写于 2026-10-12 03:00 ET，运行前。
## ≠
MATPREM/PREMRESID（不按溢价/残差排序）；IND-RATE；条款状态机选股以外的低溢价族。
## 规则
全日 ADV≥1e7 ∩ remain≥1e8 ∩ 转股期 ∩ **无**有效「回售提示」available_at；等权 top min(15,n)；CB50%+**518880**50%。全量面板。
硬闸 avg_names>0 且 Sharpe>0。

## Strategy 台账附记（2026-10-12 03:04 ET）
X1 Sharpe 预检失败（Sharpe≈**−0.50**；avg_names≈5.55）→ **fail_precheck**；未开正式双窗；无交接。
源：`output/v3/cb_put_avoid/`。台账：`descriptive_CB_PUT_AVOID_fail_precheck`。**promotion_approved=false**；GOLD only。
