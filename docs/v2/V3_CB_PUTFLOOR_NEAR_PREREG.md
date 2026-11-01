# V3_CB_PUTFLOOR_NEAR_PREREG — 纯债底附近保护价值
研究级，promotion_approved=false。写于 2026-10-12 05:00 ET，运行前。

## 唯一收益来源（一句）
持有二级价贴近纯债价值（close/bond_value∈[0.90,1.15]）的可转债 ADV 等权，收割债底/回售保护被低估的错价。

## ≠ 禁族
- ≠ CB-PUT-AVOID（剔除回售提示后全池 ADV，非价带）
- ≠ CB-PUTPRESS（回售提示窗持有）
- ≠ CB-BONDVAL（按 bond_value/close 最大排序，偏深折价）
- ≠ MATPREM / PARITY / PREMRESID-COV / MATWALL（无溢价残差、无平价带、无 ytm 墙）

## 规则
转股期 ∩ ADV≥1e7 ∩ remain≥1e8 ∩ 非强赎 ∩ close/bond_value∈[0.90,1.15]；
ADV top min(15,n) 等权；n<2 → 空仓；CB 50% + **518880** 50%。
FULLCB=1；主表仅 60万/100万；GOLD only。
HARD GATE：X1 Sharpe≤0 或 avg_names==0 → fail_precheck。

## Strategy 对账附记（2026-10-12T05:07:26-04:00）
`output/strategy_recon/cb_putfloor_near/`：**pass_all=true**；**near_relative** vs PARITY（≈0.958）与 PREMRESID-COV（≈0.927）→ 非独立 explore-pass。
X2≈13.19%/13.27%、MDD≈−22.5%；**X1 avg_names≈0.46 黄金主导**。GOLD only。台账：`descriptive_CB_PUTFLOOR_NEAR_near_relative_research_observe`。**promotion_approved=false**。
