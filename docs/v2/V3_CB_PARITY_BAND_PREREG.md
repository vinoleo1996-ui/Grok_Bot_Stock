# V3_CB_PARITY_BAND_PREREG — 平价带[85,105] 流动性等权
研究级，promotion_approved=false。写于 2026-10-12 03:07 ET，运行前。
## ≠
不按溢价排序；按 **cb_value 落带** 做结构暴露（债股混合区）。≠ MATPREM 低溢价，≠ 510300 热度。
## 规则
转股期 ∩ ADV≥1e7 ∩ remain≥1e8 ∩ cb_value∈[85,105]；ADV top min(15,n) 等权；CB50%+GOLD50%。全量面板。同闸门。

## Strategy 对账附记（2026-10-12T03:12:06-04:00）
研究级复核：`output/strategy_recon/cb_parity_band/`；EngA≡Beta；**pass_all=false**（EngA–EngB 绝对阈未过）；**near_relative** vs CB-PREMRESID-COV（日≈0.90）与 IND-RATE-DIFF（日≈0.92）→ **非独立 explore-pass** / research_observe。
主表 60/100万 X2≈16.74%/16.67%，MDD≈−22.2%；**X1 avg_names≈0.53（黄金主导；空仓≈83.9%）**。
vs MATPREM 日相关≈0.56（非近亲）。面板：`prepare_panels_for_execution(policy='full')`。GOLD only。**promotion_approved=false**。台账：`descriptive_CB_PARITY_BAND_near_relative_research_observe`。
