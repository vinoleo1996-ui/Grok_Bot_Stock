# V3_IND_NAV_STRESS_PREREG — 行业 ETF 折溢价应力 → 削 510300
研究级，**promotion_approved=false**。写于 **2026-10-12 06:47 ET，运行前**。
批次：`ortho_evt_ind2`。压舱 **GOLD 518880 only**。引擎同 hub。

## 独特收益来源（谁付钱）— A 股机制
行业 ETF `|close/unit_nav−1|` 截面均值升高 = 一级/二级套利与 AP 流动性应力（折溢价扩开）。应力期宽基风险偏好常同步收缩。本臂：折溢价应力扩展 z 高 → **削 510300**，余 GOLD。付钱的是：在 AP/流动性应力下仍提供流动性或被迫成交的参与者（liquidity/AP stress payers）。

## ≠
| 臂 | 机制 |
|---|---|
| **BOND-NAV-MR**（已 research_observe） | 债券 ETF NAV 折溢价均值回归多头 |
| **IND-RATE / 份额流族** | 份额变化，非价格−NAV |
| **本臂** | 行业 ETF **|prem| 截面均值** 作风险-off 削宽基；不做折溢价多头 |

## 规则
- 池：category==行业；`etf_share_flow_pit_all` 的 `unit_nav`/`adj_nav` + `etf_daily_adj.close`。
- PIT：`nav_available_at` 与行情 `available_at` 取保守可用日。
- 每日：有有效 nav 与 close 的行业 ETF，\(s_t=\mathrm{mean}_i(|close/unit\_nav-1|)\)；`z=expanding_z(s, min=40)`。
- `z>0` → `w_eq=0.25`；否则 `0.45`；余 **518880**。
- 若 X1 有效覆盖过薄 → `coverage_blocked`（预检文档化，不开正式）。
- 月度调仓；AUM 60/100万；禁小盘/IC。

## 闸门
同 hub；报 vs IND-RATE-DIFF 日 \|ρ\|。
