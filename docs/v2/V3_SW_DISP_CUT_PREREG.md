# V3_SW_DISP_CUT_PREREG — 申万一级截面离散度升高 → 削 510300
研究级，**promotion_approved=false**。写于 **2026-10-12 06:47 ET，运行前**。
批次：`ortho_evt_ind2`（New Bot 搜索循环；停 CB/利率/GOLD 压舱近亲；停磨 MARGIN-PX-DIV）。
压舱 **GOLD 518880 only**。引擎：`run_weight_schedule` + `ExecConfig.strategy_v1` + `derive_nonstock_limits=True` + `no_limit_codes={'sh.510300'}`。

## 独特收益来源（谁付钱）— A 股机制
申万一级行业日收益的**截面标准差**升高 = 行业相关结构破裂 / 离散度冲击（风格急切、主题单边、或系统性抛售中的分化）。市场常低估「离散度尖峰」对宽基的冲击（相关性体制切换）。本臂：离散度扩展 z 高 → **削 510300**，余仓 GOLD。付钱的是：在相关破裂/离散度尖峰时仍按历史相关持有宽基的投资者（低估离散度与 corr-breakdown 风险）。

## ≠
| 臂 | 机制 |
|---|---|
| **行业价格动量 / E1**（已 park） | 价格动量取前 3 行业 ETF |
| **IND-RATE-DIFF** | 行业 ETF **份额** Δ5 截面均值 → 削 510300 |
| **IND-SHARE-REV** | 份额变化率截面反转轮动行业 ETF 本身 |
| **本臂** | **SW L1 日收益截面离散度**（价格指数）→ 削宽基；不碰份额流、不做行业多头轮动 |

## 规则
- 数据：`data/sw/level1_bars.parquet`（`closeindex` 日收益；覆盖自 1999）。
- 每日：\(d_t=\mathrm{stdev}_{i\in\mathrm{SW1}}(r_{i,t})\)；`z=expanding_z(d, min=60)`（信号 T 日收盘可用 → 月调仓 asof）。
- `z>0` → `w_eq=0.25`；否则 baseline `w_eq=0.45`；余 **518880**。
- 月度调仓；AUM 60/100万；禁小盘/IC。

## 闸门
HARD：X1 Sharpe≤0 或 avg_names==0 → fail_precheck。正式：X1&X2 Sharpe>0、MDD>−25%、X2 CAGR≥12%。报 vs IND-RATE-DIFF 日 \|ρ\|，>0.85 → near_relative。仅 explore-pass 交接；`promotion_approved=false`。
