# V3_IND_RATE_P90_PREREG — 行业份额变化率强度（P90）→ 中大盘反转
研究级，promotion_approved=false。写于 **2026-10-12 02:53 ET，运行前**。

## ≠ IND-RATE-DIFF（父臂 WATCH）
| | IND-RATE-DIFF | **IND-RATE-P90** |
|---|---|---|
| 聚合 | 截面 **等权均值** Δ5 pct | 截面 **90 分位（强度）** Δ5 pct |
| 机制含义 | 平均流入热度 | **最拥挤尾部** 行业流入强度扩散 |
| 压舱 | 518880 GOLD | 同（禁 DD） |

## 规则
- 数据/PIT 同父；`rate_i=Δ5(fd_share) pct`；`signal = CS_p90(rate_i)` → expanding z。
- z>0 → w_eq=0.25；否则 0.45；余 518880。
- 硬闸：X1 Sharpe>0（覆盖用行业非空数>0）。正式 X2≥12%。无 IC/小盘。

## 结果（2026-10-12 02:55 ET）
**pass_explore** 双 AUM。交接 `output/v3/handoff_strategy/ind_rate_p90/`。promotion_approved=false。

## Strategy 对账（2026-10-12 ≈02:58 ET）
- 两引擎 **pass_all=true**（A≡B≡Beta）。
- **vs IND-RATE-DIFF X2 日/周相关 ≈0.995 / 0.993**（60万与100万）→ **near_relative**（阈 0.85）。
- **不作独立 explore-pass**；记 **research_observe / 族内 secondary**（父臂 IND-RATE-DIFF 已在 WATCH）。
- 主表：X2≈**24.34%** / −18.63% / 1.31；**X1 Sharpe≈0.19 / MDD≈−19.5%**。
- 台账：`descriptive_IND_RATE_P90_near_relative_research_observe`；短报 `output/strategy_recon/ind_rate_p90/SHORT_ZH.md`。
- GOLD only；`promotion_approved=false`；禁小盘。
