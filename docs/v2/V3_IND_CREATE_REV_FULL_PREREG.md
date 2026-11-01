# V3_IND_CREATE_REV_FULL_PREREG — 全宇宙行业 ETF 创设反转多头书
研究级，**promotion_approved=false**。写于 **2026-10-12 06:53 ET，运行前**。
批次：`ortho_evt_ind3_full`。压舱 **GOLD 518880 only**（空仓残差）。引擎：`run_weight_schedule` + `ExecConfig.strategy_v1` + `derive_nonstock_limits=True`。

## 修复点（相对 IND-CREATE-REV-BOOK）
BOOK 臂用 `sw_l1_etf_map_pit_daily` **每申万一级 1 只** → X1 液态≈3.7 行业/日 → tercile avg_names≈1.16 → Sharpe≤0 fail_precheck。  
本臂改为 **全行业 ETF 宇宙**：`etf_basic.category==行业` ∩ `etf_share_flow_pit_all` ∩ `etf_daily_adj`，**不做** one-ETF-per-SW-L1 限制。目标 avg_names **明显 >3**。

## 独特收益来源（谁付钱）— A 股机制
行业 ETF 一级净创设偏高常由渠道/散户主题升温后催促 AP；高点持续创设后退潮二级承压。本臂月频等权做多 **近端 20 日 ΣΔshare 最低 tercile**（创设最少/赎回偏多）。付钱的是：高位催促 AP 创设的 FOMO 散户/渠道。

## ≠
| 臂 | 持仓 | 机制 |
|---|---|---|
| IND-RATE / CREATE-HHI / NAV-STRESS | 510300↔GOLD 削仓 | 扳机不同，持仓同构 |
| IND-CREATE-REV-BOOK | map-pit 每行业 1 只篮 | 同信号，池过窄 |
| **本臂** | **全宇宙流动行业 ETF 篮** + 空→GOLD | 20d ΣΔshare 底 tercile；**不持 510300** |

## 规则
- 池：`category==行业`；`amt20≥1000`（`etf_daily_adj.amount` 20 日均；单位同既有 amt20；X1 月均合格≈11 → tercile≈3.4；经典 2000 仅 tercile≈2.2，为 avg_names>3 选用 1000）；上市≥60 交易日（自首次行情日起）。
- 信号：`etf_share_flow_pit_all.d_share_wan` 按 `share_available_at` 对齐；月调仓日前 20 可用日 ΣΔshare。
- 每月末：截面升序底 tercile（`max(1,N//3)`）等权；无合格 → `{518880:1}`。
- AUM 60/100万；禁小盘/IC；禁 CB/利率/IND-RATE 近亲与 MARGIN 再磨。

## 闸门
HARD：X1 Sharpe≤0 或 avg_names==0 → fail_precheck。正式：X1&X2 Sharpe>0、MDD>−25%、X2 CAGR≥12%。  
必报 vs IND-RATE-DIFF 日 ρ（\|ρ\|>0.85 → near_relative）。仅 pass_explore 交接；promotion_approved=false。
