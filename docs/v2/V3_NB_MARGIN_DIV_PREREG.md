# V3_NB_MARGIN_DIV_PREREG — 北向 vs 两融背离 → 中大盘择时
研究级，**promotion_approved=false**。修订 **2026-10-12 19:10 ET**（Data 补齐 X1 后重开）。
批次：`smoke_evtflow_indetf` rerun。压舱 **511880**。

## 独特收益来源（谁付钱）
北向（外资主动配置）与两融（内资杠杆）的方向背离：北向流入而两融收缩 = 外资接内资去杠杆抛压（付钱：被迫去杠杆者）；北向流出而两融扩张 = 内资杠杆接外资盘（付钱：后知后觉的融资客）。收益来自两类资金的风险偏好与约束不对称，而非价格动量。

## ≠
IND-RATE / CALL-HEAT / MARGIN-DELTA（单源热度或单源两融）；本臂要 **北向 z 与两融 z 符号相反** 才调仓。**不磨** MARGIN-PX-DIV。

## 规则
- 北向：`data/v2/northbound/moneyflow_hsgt_daily_2014plus.parquet`（或已延伸的 2018plus；须 `date_min≥20141117`）的 `north_money`。
- PIT：`available_at` = trade_date 18:00 SH → 次一交易日可用；**不可前移**（保守口径≈T+1 15:00，交易按次日开盘）。
- 两融：`data/v2/margin/margin_exchange_daily_merged.parquet`（2014+）SSE+SZSE 汇总 `rzrqye`；`mz`=expanding_z(Δ20, min=40)。
- `nz=expanding_z(north_money Δ5, min=40)`。
- `nz>0 ∧ mz<0` → w_eq=0.50；`nz<0 ∧ mz>0` → w_eq=0.20；其余 0.35；余 **511880**。
- 月度调仓；AUM 60万/100万；禁小盘。

## 覆盖（Data 2026-10-12 回执）
北向 **20141117→20261009**（沪自 20141117；深 sgt 自 20161205）；X1 有覆盖。旧「coverage_blocked_X1」作废。见 `docs/v2/BETA_X1_EVT_FLOW_COVERAGE.md`。

## 闸门
同 hub；须报 vs IND-RATE-DIFF；|ρ|>0.85 → near_relative。仅 explore-pass 且非 near_relative 才 handoff。
