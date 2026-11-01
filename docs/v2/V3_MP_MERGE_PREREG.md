# V3_MP_MERGE_PREREG — ytm[0.5,3.0] 合并带 + 低转股溢价20

研究级，**promotion_approved=false**。写于 2026-10-12 01:46 ET（正式双窗前）。  
X1 预检 Sharpe **0.80** → 允许双窗。

## 差异
合并 NEAR∪MATPREM 期限带为 **[0.5,3.0]**；Top20；无 8% 帽。≠ 母[1,3]/NEAR/FAR。

## 规则
FULLCB；转股期；ytm∈[0.5,3.0]；最低 cb_over_rate 20；袖 50%+债金逆波。无 IC。AUM∈{60万,100万}。  
闸门：两窗 MDD≤25%、夏普>0；X2 CAGR≥12%。

## 结果（2026-10-12 01:49 ET；`output/v3/mp_merge/results.json`）

| AUM | X1 | X2 | S | 判定 |
|---|---|---|---|---|
| 60万 | 3.2%/-5.0%/0.80 | 15.4%/-5.2%/1.50 | 7.7%/-13.0%/1.07 | **通过** |
| 100万 | 3.2%/-5.0%/0.78 | 16.1%/-5.4%/1.54 | 7.7%/-13.3%/1.05 | **通过** |

短报：`output/v3/mp_merge/SHORT_ZH.md`。**已交接**。promotion_approved=false。
