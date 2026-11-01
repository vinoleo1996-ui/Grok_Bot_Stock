# V3_CB_MATWALL_MID_PREREG — 中期剩余期限日历墙
研究级，promotion_approved=false。写于 2026-10-12 04:40 ET，运行前。

## 唯一收益来源（一句）
剩余年限 ytm∈[2.0,5.0] 的可转债日历供给池，ADV 等权持有（中期墙供给，非估值排序）。

## ≠ 禁族
- ≠ MATPREM / NEAR/MERGE/RELAX（无溢价×期限残差排序）
- ≠ CB-PARITY-BAND（非 cb_value 平价带）
- ≠ CB-PREMRESID-COV（非溢价残差）
- ≠ 建议近端墙 [0.75,2]（X1 覆盖≈0；本臂改写为中期带保 avg_names）

## 规则
转股期 ∩ ADV≥1e7 ∩ remain≥1e8 ∩ 非强赎 ∩ ytm∈[2,5]；ADV top min(15,n) 等权；
CB 50% + **518880** 50%。全量 CB 面板 FULLCB=1。主表仅 60万/100万。

## Strategy 对账附记（2026-10-12T04:44:55-04:00）
研究级复核：`output/strategy_recon/cb_matwall_mid/`；EngA≡Beta；**pass_all=false**（EngA–EngB 绝对阈未过）；全部 |ρ_daily|≤0.85（最大 vs PARITY≈0.825）→ **非独立 explore-pass** / research_observe。
主表 60/100万 X2≈20.51%/21.28%，MDD≈−22.6/−22.7%；**X1 avg_names≈3.55**（空仓≈34.4%；黄金≈67.2%）。
面板：`prepare_panels_for_execution(policy='full')`。GOLD only。**promotion_approved=false**。台账：`descriptive_CB_MATWALL_MID_recon_AB_gap_research_observe`。
