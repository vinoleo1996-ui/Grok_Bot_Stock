# V3_IND_NAV_CHEAP_BOOK_PREREG — 行业 ETF 折价多头书（持仓=折价篮）
研究级，**promotion_approved=false**。写于 **2026-10-12 06:50 ET，运行前**。
批次：`ortho_evt_ind3_book`。压舱 **GOLD 518880 only**（残差）。引擎同 hub。

## 独特收益来源（谁付钱）— A 股机制
行业 ETF `prem=close/unit_nav−1` 深度折价时，二级急售常快于 AP 赎回/套利闭环（尤其主题退潮、流动性薄的行业产品）。本臂做多 **最负溢价 tercile** 的流动性行业 ETF，淡出溢价丰厚者。付钱的是：急于出货、不愿等 AP 套利收敛的二级卖盘，以及延迟创设/赎回的 AP 时滞对手方。

## ≠
| 臂 | 持仓 | 机制 |
|---|---|---|
| **IND-NAV-STRESS** | 510300↔GOLD | CS mean \|prem\| 高 → **削宽基** |
| **BOND-NAV-MR** | 511010↔GOLD | 债基 NAV 均值回归 |
| **本臂** | **折价行业 ETF 篮**（非 510300） | 截面 **最负 prem** 多头；非应力削仓 |

## 规则
- 池：map-pit 每行业 1 只；`amt20≥2000`；上市≥60 日；需有效 `unit_nav` 与 `close`（PIT：`nav_available_at` 与行情 `available_at` 保守对齐）。
- 每月末：按 `prem` 升序取底 tercile（`max(1,N//3)`）等权；无合格 → GOLD。
- **不持 510300**。AUM 60/100万；禁小盘/IC。

## 闸门
同 hub；必报 vs IND-RATE-DIFF 与 vs BH 510300/GOLD 45/55；avg_names=行业 ETF 只数。promotion_approved=false。
