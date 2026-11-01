# V3_CB_CLAUSE_SM_PREREG — 条款状态机（PUT∨RESET）∧¬CALL
研究级，promotion_approved=false。写于 2026-10-12 01:57 ET。X1 预检 Sharpe **0.83**。
## 差异
多状态合成；**不按溢价**。≠ 单事件 XREV/PUTPRESS/CALLTV。
## 规则
FULLCB；近 30 日回售提示且无结果 OR 近 40 日下修；排除近 60 日「已满足强赎」；ADV Top15；袖 40%+债金逆波。AUM 60/100万。同闸门。
## 结果（2026-10-12 01:58 ET；`output/v3/cb_clause_sm/results.json`）

| AUM | X1 | X2 | S | 判定 |
|---|---|---|---|---|
| 60万 | 3.2%/-5.0%/0.83 | 10.8%/-5.3%/1.44 | 7.7%/-10.8%/0.92 | **不通过**（X2 CAGR<12%） |
| 100万 | 3.2%/-5.0%/0.82 | 10.7%/-5.4%/1.42 | 7.5%/-11.0%/0.90 | **不通过**（X2 CAGR<12%） |

短报：`output/v3/cb_clause_sm/SHORT_ZH.md`。**无交接**。promotion_approved=false。
