# V3_CB_CALLTV_PREREG — 时变强赎邻近度（价区 + 动态袖套）

研究级，**promotion_approved=false**。  
**写于 2026-10-12 01:38 ET，在正式双窗之前。**  
依据：`docs/v2/BETA_NEXT_AUM_ARMS_ZH.md` ①；CB-LARGEISS fail 后；**已通过 X1 Sharpe 预检**。

## 0. 差异
| 对照 | 本臂 |
|---|---|
| 低溢价×日历/规模家族 | **不按溢价排序**；按 **价距 120** 在 [110,128] 区内选券 |
| MATPREM / MP-NEAR | 无 ytm/转股期日历 |
| CB3 | 无公告事件入场；用价格邻近软强赎区作时变 |
| CB1-FLOOR | 非双低；带为 [110,128] 且目标锚 120 |

## 0b. X1 Sharpe 预检（60万，同规则）
`output/v3/cb_calltv/x1_sharpe_pretest.json`：Sharpe **0.60**，CAGR 3.2%，MDD −5.4%，avg_names≈2.95 → **允许正式双窗**。  
同批关闭：TS-CURVE Sharpe −0.06；CB-LOWBETA Sharpe −0.21。

## 1. 规则（写死）
- 选券日每 10 交易日；FULLCB：ADV≥1000万、remain≥1亿、强赎提示/实施剔除、排除 132/120。  
- 价 ∈ **[110, 128]**；取 |close−120| 最小的 **15** 只；等权。  
- 袖套 \(w_{cb}\)：截面中位价（合格 FULLCB）≥125 → 0.30；≤115 → 0.50；否则 0.40。空区 → \(w_{cb}=0\)。  
- 压舱 \(1-w_{cb}\)：511010/518880 60日逆波。  
- `strategy_v1`；L=1；无 IC；AUM ∈ {600000,1000000} only。

## 2. 判定
探索 X1+X2 一次；S 描述。通过 = 每 AUM：两窗 MDD≤25%、夏普>0，X2 CAGR≥12%。通过才交接。

## 3. 结果（2026-10-12 01:40 ET；`output/v3/cb_calltv/results.json`）

| AUM | X1 | X2 | S（描述） | 判定 |
|---|---|---|---|---|
| 60万 | 3.2%/−5.4%/0.60 | 7.4%/−4.0%/1.34 | 5.7%/−9.0%/0.93 | **不通过**（X2&lt;12%） |
| 100万 | 3.1%/−5.4%/0.58 | 7.3%/−4.0%/1.32 | 5.6%/−9.1%/0.91 | **不通过**（X2&lt;12%） |

短报：`output/v3/cb_calltv/SHORT_ZH.md`。**无 Strategy 交接。** promotion_approved=false。
