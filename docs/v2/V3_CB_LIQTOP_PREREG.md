# V3_CB_LIQTOP_PREREG — 高 ADV 价区[100,115] + 回售回避

研究级，**promotion_approved=false**。写于 2026-10-12 01:42 ET（正式双窗前）。  
X1 预检 Sharpe **0.49** → 允许双窗。**不按溢价排序。**

## 规则
- 每 10 日；FULLCB；价∈[100,115]；排除 available_at∈(T−60,T] 的回售提示/公告。  
- 按 ADV 最高取 15；等权；袖 50% + 债金逆波压舱。无 IC。AUM∈{60万,100万}。  
- 判定：同标准闸门。

## 结果（2026-10-12 01:43 ET；`output/v3/cb_liqtop/results.json`）

| AUM | X1 | X2 | S | 判定 |
|---|---|---|---|---|
| 60万 | 2.1%/-6.9%/0.49 | 5.0%/-4.9%/0.99 | 7.6%/-12.0%/1.41 | **不通过**（X2 CAGR<12%） |
| 100万 | 2.0%/-7.0%/0.47 | 4.9%/-5.0%/0.98 | 7.6%/-12.1%/1.39 | **不通过**（X2 CAGR<12%） |

短报：`output/v3/cb_liqtop/SHORT_ZH.md`。**无 Strategy 交接。** promotion_approved=false。
