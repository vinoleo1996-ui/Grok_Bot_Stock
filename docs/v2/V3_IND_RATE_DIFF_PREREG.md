# V3_IND_RATE_DIFF_PREREG — 行业份额变化率 → 中大盘扩散反转
研究级，promotion_approved=false。写于 **2026-10-12 02:45 ET，运行前**。
数据：`etf_share_flow_pit_all.parquet` + `sw_l1_etf_map_pit`；X1 raw 拼接。严格 available_at。

## 差异
| | 裸流入 / IND-CROWD-REV | **IND-RATE-DIFF** |
|---|---|---|
| 信号 | 净流入水平 / 拥挤广度(z>1占比) | **份额变化率** mean(Δ5 pct) 跨行业 ETF |
| 映射 | 顺流或广度降仓 | 高变化率（拥挤流入）→ **降 510300**（中大盘扩散耗尽） |
| 禁 | — | 禁止裸 net-inflow 臂 |

## 规则
- 行业 ETF（category=行业∩有 sw 映射）；`rate=Δ5(fd_share)/lag`；截面等权均值 → expanding z。
- z>0 → w_eq=0.25；否则 0.45；余 **518880**（GOLD 压舱，禁 DD）。
- 硬闸同左。

## 结果（2026-10-12 02:48 ET）
**pass_explore** 双 AUM。X1 Sharpe≈0.12；X2 CAGR≈24.7%。交接：`output/v3/handoff_strategy/ind_rate_diff/`。promotion_approved=false。
