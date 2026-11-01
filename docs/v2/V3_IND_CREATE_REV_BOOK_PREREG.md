# V3_IND_CREATE_REV_BOOK_PREREG — 行业 ETF 创设反转多头书（持仓=行业篮）
研究级，**promotion_approved=false**。写于 **2026-10-12 06:50 ET，运行前**。
批次：`ortho_evt_ind3_book`。压舱 **GOLD 518880 only**（仅空仓残差，不作 Alpha）。引擎：`run_weight_schedule` + `ExecConfig.strategy_v1` + `derive_nonstock_limits=True`。

## 独特收益来源（谁付钱）— A 股机制
行业 ETF **一级市场净创设（Δshare>0 且靠前）** 常由渠道/散户在主题升温后推动 AP 申购；高点持续创设后主题退潮时二级承压。本臂做 **创设强度截面反转多头书**：每月在「申万一级 → 代表 ETF」映射上，等权做多 **近端累积 Δshare 最低 tercile**（赎回/创设最少的行业），空仓时残差 GOLD。付钱的是：高位催促 AP 创设的散户/渠道，以及主题退潮时的被动赎回冲击对手方。

## ≠ 持仓空间（本批硬规则）
| 臂 | 持仓 | 扳机 |
|---|---|---|
| **IND-RATE / CREATE-HHI / NAV-STRESS / SW-DISP-CUT** | **510300↔GOLD 削仓** | 份额/HHI/折溢价/离散度 |
| **IND-SHARE-REV**（已 fail_precheck） | 行业 ETF 底 3（**20 日份额变化率** pct） | 份额 **收益率** 反转 |
| **本臂** | **行业 ETF 篮**（map-pit 每行业 1 只；底 tercile **累积 Δshare**）+ 空则 GOLD | **创设量（Δshare）** 反转，非 pct、非削 510300 |

## 规则
- 池：`sw_l1_etf_map_pit_daily` 每行业当期代表；`amt20≥2000` 万；上市≥60 交易日；`category==行业`。
- 信号：`etf_share_flow_pit_all` 的 `d_share_wan`，按 `share_available_at` 对齐日历；月调仓日前 20 个可用日 **Σ Δshare**（创设累积）。
- 每月末：截面按 ΣΔ 升序，取 **底 tercile**（`max(1, N//3)`）等权；无合格名 → `{518880:1}`。
- **不持 510300**。AUM 60/100万；禁小盘/IC；月调仓。

## 闸门
HARD：X1 Sharpe≤0 或 avg_names==0 → fail_precheck。正式：X1&X2 Sharpe>0、MDD>−25%、X2 CAGR≥12%。  
必报：vs IND-RATE-DIFF 日 ρ；vs **BH 510300/GOLD 45/55** 日 ρ；\|ρ\|>0.85 vs IND-RATE → near_relative。  
`avg_names` = 调仓日行业 ETF 只数均值（非 1.0 金仓伪装）。仅 pass_explore 交接；promotion_approved=false。
