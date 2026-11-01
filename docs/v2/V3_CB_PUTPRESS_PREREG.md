# V3_CB_PUTPRESS_PREREG — 回售提示窗（未出结果）
研究级，promotion_approved=false。写于 2026-10-12 01:50 ET。X1 预检 Sharpe **0.80**。
## 规则
回售提示∈(T−30,T] 且尚无回售结果；FULLCB；ADV 截断 15；袖 40%。≠ LIQTOP（LIQTOP 排除回售）。
## 结果（2026-10-12 01:51 ET；`output/v3/cb_putpress/results.json`）

| AUM | X1 | X2 | S | 判定 |
|---|---|---|---|---|
| 60万 | 2.7%/-5.0%/0.80 | 4.9%/-1.8%/2.26 | 6.3%/-5.2%/1.22 | **不通过**（X2 CAGR<12%） |
| 100万 | 2.7%/-5.0%/0.80 | 4.9%/-1.8%/2.26 | 6.1%/-5.3%/1.19 | **不通过**（X2 CAGR<12%） |

短报：`output/v3/cb_putpress/SHORT_ZH.md`。**无交接**。promotion_approved=false。
