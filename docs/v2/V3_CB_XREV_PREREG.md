# V3_CB_XREV_PREREG — 下修后 40 日持有窗
研究级，promotion_approved=false。写于 2026-10-12 01:50 ET。X1 预检 Sharpe **0.83**。
## 规则
FULLCB；available_at∈(T−40,T] 的下修类事件；等权（>15 按 ADV 截断）；袖 40%+压舱。**不按溢价**。≠ CALLTV/LIQTOP。
## 结果（2026-10-12 01:51 ET；`output/v3/cb_xrev/results.json`）

| AUM | X1 | X2 | S | 判定 |
|---|---|---|---|---|
| 60万 | 3.2%/-5.0%/0.83 | 9.4%/-5.4%/1.25 | 7.1%/-10.9%/0.85 | **不通过**（X2 CAGR<12%） |
| 100万 | 3.2%/-5.0%/0.82 | 9.2%/-5.4%/1.23 | 7.0%/-11.0%/0.83 | **不通过**（X2 CAGR<12%） |

短报：`output/v3/cb_xrev/SHORT_ZH.md`。**无交接**。promotion_approved=false。
