# V3_BOND_NAV_MR_PREREG — 国债 ETF 折溢价均值回归袖套
研究级，promotion_approved=false。写于 2026-10-12 05:00 ET，运行前。

## 唯一收益来源（一句）
511010 二级价相对单位净值的折溢价扩展 z 分档，在国债 ETF 与黄金之间做均值回归袖套（溢价减债、折价加债）。

## ≠ 禁族
- ≠ NAV-DISC（曾对 510300 折溢价调权益 β，已 fail）
- ≠ heat→510300 / IND-RATE / LPR / EQBOND（本臂**无**510300）
- ≠ DD-BOND30 / CASH-TRIG（非回撤/波动触发）
- ≠ DD×GOLD 叠满

## 规则
- NAV PIT：`ann_date.normalize() < T`（allow_exact_matches=False）
- prem = close_511010 / unit_nav_asof − 1；S = expanding-z(prem, min 60)
- 月末：S≥+1 → w_bond=0.20；S≤−1 → w_bond=0.70；否则 w_bond=0.45；余→**518880**
- 主表仅 60万/100万；GOLD only；promotion_approved=false
HARD GATE：X1 Sharpe≤0 → fail_precheck。

## Strategy 对账附记（2026-10-12T05:07:26-04:00）
`output/strategy_recon/bond_nav_mr/`：**pass_all=true**；**vs GOLD-BETA≈0.57（压舱近亲闸未触发）**；vs IND-RATE-DIFF≈0.89 → near_relative → 非独立 explore-pass。
X2≈14.00%/14.02%、MDD≈−18.0%；无510300。台账：`descriptive_BOND_NAV_MR_near_relative_research_observe`。**promotion_approved=false**。
