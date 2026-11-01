# V3_MP_RELAX_PREREG — ytm[1,3] +（转股期 OR 上市龄≥1年）

研究级，**promotion_approved=false**。写于 2026-10-12 01:46 ET（正式双窗前）。  
X1 预检 Sharpe **0.80** → 允许双窗。

## 差异
放宽入池：`in_conv OR list_age≥1`。期限带仍 [1,3]（≠ MERGE 的 [0.5,3]）。≠ 母臂硬 conv。

## 规则
FULLCB；上述放宽；最低溢价 20；袖 50%+压舱。无 IC。AUM∈{60万,100万}。同闸门。

## 结果（2026-10-12 01:49 ET；`output/v3/mp_relax/results.json`）

| AUM | X1 | X2 | S | 判定 |
|---|---|---|---|---|
| 60万 | 3.2%/-5.0%/0.80 | 12.8%/-5.4%/1.32 | 7.7%/-12.0%/1.06 | **通过** |
| 100万 | 3.2%/-5.0%/0.78 | 13.2%/-5.4%/1.33 | 7.6%/-12.1%/1.04 | **通过** |

短报：`output/v3/mp_relax/SHORT_ZH.md`。**已交接**。promotion_approved=false。
