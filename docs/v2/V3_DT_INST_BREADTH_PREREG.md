# V3_DT_INST_BREADTH_PREREG — 龙虎榜机构席位净买广度 → 中大盘择时
研究级，**promotion_approved=false**。修订 **2026-10-12 19:10 ET**（Data 补齐 X1 后重开）。
批次：`smoke_evtflow_indetf` rerun。禁 CB/利率/GOLD 压舱同族扩臂。压舱 **511880**（现金类，非 GOLD）。

## 独特收益来源（谁付钱）
龙虎榜机构专用席位（`seat_type=institution`）净买入广度刻画「知情资金进场体制」。机构席位披露滞后但方向更净；散户/游资席位噪音大。付钱的是：在机构已铺开买盘后才追龙虎榜热票的游资与散户（信息不对称 + 披露窗口滞后）。

## ≠ 禁族
| 禁族 | 本臂 |
|---|---|
| CALL-HEAT / IND-RATE / MARGIN-DELTA（热度·拥挤→削 510300） | **不是**热度削仓；是机构净买广度升高 → **加** 510300（知情体制） |
| 教科书动量 | 无价格动量排序 |
| GOLD 压舱变体 | 余仓 **511880** |

## 规则（最小）
- 数据：`data/v2/dragon_tiger/top_inst_labeled.parquet`；`seat_type=institution`。
- PIT：`available_at` = trade_date 18:00 SH；**`available_at_alpha_conservative` = T+1 15:00** → 交易 **T+2 开盘**可用（不可前移）。
- 日信号：当日机构席位按 `ts_code` 汇总 `net_buy`，广度 = 净买>0 的标的占比；与 expanding 中位比较（min_periods=40）。
- 广度 > expanding 中位 → w_eq=0.50；否则 0.30；余 **511880**。
- 月度调仓；AUM 仅 60万/100万；禁小盘/IC；L≤1.5。

## 覆盖（Data 2026-10-12 回执）
`top_inst_labeled` **20150105→20261009**（含 X1）；见 `docs/v2/BETA_X1_EVT_FLOW_COVERAGE.md`。旧「coverage_blocked_X1」作废。

## 闸门
X1 Sharpe≤0 或 avg_names=0 → fail_precheck。正式：X2 CAGR≥12% 且 MDD≳−25% 不过。须报 vs IND-RATE-DIFF 日 |ρ|，>0.85 → near_relative（仍报数，不独立交接）。仅 explore-pass 且非 near_relative 才 handoff。
