# V3_MARGIN_DELTA_PREREG — 两融余额变化率调节中大盘
研究级，promotion_approved=false。写于 2026-10-12 03:00 ET，运行前。
## ≠
IND-RATE（份额流）、MATPREM（低溢价）、GOLD-BETA（金β）、裸流入、动量。
## 规则
沪深两市 `rzrqye` 合计 20 日变化率 → expanding z；z>0（加杠杆拥挤）→ w_eq=0.25；否则 0.45；余 **518880**。
数据：`margin_exchange_2014_2017` + `margin_exchange_daily_2018plus`（available_at）。AUM 60/100万。
闸门：X1 Sharpe>0；正式 X2≥12%。

## Strategy 台账附记（2026-10-12 03:04 ET）
X1 Sharpe 预检失败（Sharpe≈**−0.03**）→ **fail_precheck**；未开正式双窗；无交接。
源：`output/v3/margin_delta/`；`pretest_batch_20261012_ortho3.json`。台账：`descriptive_MARGIN_DELTA_fail_precheck`。**promotion_approved=false**；GOLD only。
