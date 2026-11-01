# V3_IND_NAV_CHEAP_FULL_PREREG — 全宇宙行业 ETF 折价多头书
研究级，**promotion_approved=false**。写于 **2026-10-12 06:53 ET，运行前**。
批次：`ortho_evt_ind3_full`。压舱 **GOLD 518880 only**。引擎同 hub。

## 修复点
同 CREATE-REV-FULL：弃 map-pit 每行业 1 只；用 **全 `category==行业` 宇宙** + 流动性过滤，目标 avg_names>3。

## 独特收益来源（谁付钱）— A 股机制
`prem=close/unit_nav−1` 深度折价时，二级急售常快于 AP 套利闭环。本臂做多 **最负溢价 tercile** 的流动行业 ETF。付钱的是：急售不愿等 AP 收敛的二级卖盘/延迟 AP。

## ≠
| 臂 | 持仓 | 机制 |
|---|---|---|
| IND-NAV-STRESS | 510300↔GOLD | CS mean \|prem\| → 削宽基 |
| IND-NAV-CHEAP-BOOK | map-pit 1/行业 | 同信号，池过窄 |
| **本臂** | **全宇宙折价行业 ETF 篮** | 最负 prem tercile；**不持 510300** |

## 规则
- 池：同 CREATE-REV-FULL（`amt20≥1000`；上市≥60 日）；需有效 `unit_nav` 与 `close`（PIT：`nav_available_at`）。
- 每月末：prem 升序底 tercile 等权；无合格 → GOLD。
- AUM 60/100万；禁小盘/IC。

## 闸门
同 CREATE-REV-FULL；必报 vs IND-RATE-DIFF。promotion_approved=false。
