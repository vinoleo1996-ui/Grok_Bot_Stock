# V3_CB_CALL_HEAT_PREREG — 强赎邻近热度 → 削中大盘
研究级，promotion_approved=false。写于 2026-10-12 03:00 ET，运行前。
## ≠
不持有/排序转债溢价；信号=市场强赎邻近广度，映射到 **510300** 仓位；≠ MATPREM 持仓，≠ IND-RATE。
## 规则
可交易 CB（ADV≥1e7）中 `close≥128` 占比；> expanding 中位 → w_eq=0.25；否则 0.45；余 **518880**。
闸门同左。

## Strategy 对账附记（2026-10-12 03:04 ET）
研究级复核：`output/strategy_recon/cb_call_heat/`；`pass_all=true`；**near_relative** vs IND-RATE-DIFF（日≈0.985）与 CB-PREMRESID-COV（日≈0.88）→ **非独立 explore-pass** / research_observe。
主表 60/100万 X2≈20.27%/20.26%，MDD≈−24.3%（近 Mandate 25%）；X1 Sharpe≈0.12 / MDD≈−22.2%。
面板：`prepare_panels_for_execution(policy='full')`。GOLD only。**promotion_approved=false**。台账：`descriptive_CB_CALL_HEAT_near_relative_research_observe`。
