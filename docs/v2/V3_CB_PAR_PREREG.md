# V3_CB_PAR_PREREG — 近面值价区[95,102] 高 ADV（非双低/非溢价）
研究级，promotion_approved=false。写于 2026-10-12 01:54 ET。X1 预检 Sharpe **0.56**。
## 差异
≠ CB1-FLOOR（双低∩[95,115]）；≠ MATPREM 族（无 ytm/溢价）；选券按 **ADV**。压舱纯 511010。
## 规则
每 10 日 FULLCB；价∈[95,102]；ADV Top15；袖 45% + 511010 55%。无 IC。AUM 60/100万。同闸门。
## 结果（2026-10-12 01:55 ET；`output/v3/cb_par/results.json`）

| AUM | X1 | X2 | S | 判定 |
|---|---|---|---|---|
| 60万 | 1.6%/-4.9%/0.56 | 7.5%/-8.4%/1.16 | 7.2%/-6.3%/1.51 | **不通过**（X2 CAGR<12%） |
| 100万 | 1.6%/-4.9%/0.55 | 7.5%/-8.4%/1.15 | 7.1%/-6.3%/1.49 | **不通过**（X2 CAGR<12%） |

短报：`output/v3/cb_par/SHORT_ZH.md`。**无交接。** promotion_approved=false。
