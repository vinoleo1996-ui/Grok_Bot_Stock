# V3_IND_CROWD_REV_PREREG — 行业 ETF 拥挤广度 → 中大盘权益反转（非裸流入）
研究级，**promotion_approved=false**。写于 **2026-10-12 02:40 ET，运行前**。  
依据：审计 P0-5；数据 `data/v2/etf/share_pit/etf_share_flow_pit_all.parquet`。

## 0. 差异
| | SHARE-AC / ETF-FLOW-NET / SECT-FLOW-DISP | **IND-CROWD-REV** |
|---|---|---|
| 信号 | 单/双宽基流、或行业流离散 | **行业拥挤广度**（Δshare z>1 的行业 ETF 占比） |
| 映射 | 顺流/反拥挤单名/降噪 | 拥挤高 → **降** 510300（扩散耗尽/反转） |
| PIT | 各异 | 严格 `share_available_at` |

## 1. 规则
- 宇宙：`etf_basic.category==行业` ∩ share PIT；X1 用 raw 拼接。
- `z_i = z_60(Δ5 fd_share pct)`；`crowd_breadth = mean(z_i > 1)`。
- 月末：breadth > expanding 中位 → w_eq=0.25；否则 0.45；余 511010。
- 无小盘个股腿（中大盘代理=510300）。闸门同左。

## 2. 结果（2026-10-12 02:41 ET）
fail_precheck。X1 Sharpe≈−0.05。见 `output/v3/ind_crowd_rev/`。无正式、无交接。
