# V3_CB_SEASON_NEW_PREREG — 新券季养 ADV 等权
研究级，promotion_approved=false。写于 2026-10-12 05:00 ET，运行前。

## 唯一收益来源（一句）
上市龄∈[0,1.0]年的可转债 ADV 等权，收割新券流动性/关注度溢价（无溢价排序）。

## ≠ 禁族
- ≠ CB-LISTAGE（曾用上市龄[1,3]×低溢价 Top15）
- ≠ MATPREM / SIZEPREM（无低溢价、无 remain 收缩×溢价）
- ≠ MATWALL（无 ytm 日历墙）
- ≠ PARITY / PREMRESID-COV

## 规则
转股期 ∩ ADV≥1e7 ∩ remain≥1e8 ∩ 非强赎 ∩ list_age∈[0,1.0]；
ADV top min(15,n) 等权；n<3 → 空仓；CB 50% + **518880** 50%。
FULLCB=1；主表仅 60万/100万；GOLD only。
HARD GATE：X1 Sharpe≤0 或 avg_names==0 → fail_precheck。

## Strategy 对账附记（2026-10-12T05:07:26-04:00）
`output/strategy_recon/cb_season_new/`：EngA≡Beta；**pass_all=false**；**100万 X2 MDD≈−25.19% 未过闸**（60万−25.00%贴闸）；vs PARITY≈0.88 → near_relative → 非独立 explore-pass。
X1 avg_names≈1.45。LISTAGE 无 strategy_recon NAV。台账：`descriptive_CB_SEASON_NEW_tier_fail_near_relative_research_observe`。**promotion_approved=false**。
