# V3_CB_LARGEISS_PREREG — 大发行规模截面 × 低溢价

研究级，**promotion_approved=false**。  
**写于 2026-10-12 01:36 ET，在任何运行之前（正式双窗之前）。**  
依据：`docs/v2/BETA_NEXT_AUM_ARMS_ZH.md` ②；CB-CONVACT fail 后立即开跑。

## 0. 差异（非日历近亲）
| 对照 | 本臂 |
|---|---|
| MATPREM / MP-NEAR | **无** ytm/转股期日历；信号= **issue_size ≥ 当日合格池中位数** × 低溢价（Strategy 测得两 pass 臂日相关≈0.77，禁止再造日历近亲） |
| SIZEPREM / CONVACT | 非 remain 收缩、非 Δacc_convert |
| CB1-FLOOR / CB2 | 非双低、非价≤130 全池 |
| CB3 / LISTAGE / FAR | 无事件、无上市龄、无远端 ytm |

## 0b. X1 Sharpe 预检（锁本 prereg 前，AUM=60万，同规则）
见 `output/v3/cb_largeiss/x1_sharpe_pretest.json`：

| 指标 | 预检值 |
|---|---|
| CAGR | **−9.4%** |
| MDD | **−29.9%**（已破 −25%） |
| Sharpe | **−0.71**（<<0，模式复现） |
| avg_names / frac_empty | 3.03 / 0.0 |

判定：预检 **decisive X1 Sharpe<<0**；按指令仍完成一次正式 X1+X2 双窗（不 abort），预检记入短报。

## 1. 规则（写死）
- 选券日每 10 交易日；FULLCB：ADV≥1000万、remain≥1亿、强赎提示/实施剔除、排除 132/120。  
- PIT `issue_size`；在合格池内取 **issue_size ≥ 截面中位数** 子集，再取最低溢价 **15**；等权。  
- CB 袖 **50%** + 压舱 **50%**（511010/518880 60日逆波）。空池→100% 压舱。  
- `strategy_v1`；L=1；**无 IC**；AUM ∈ {600000,1000000} only。

## 2. 判定
探索 X1+X2 一次；S 描述。通过 = 每 AUM：两窗 MDD≤25%、夏普>0，X2 CAGR≥12%。通过才交接。

## 3. 失效
预检已示 X1 败；正式双窗若仍败则关闭。

## 4. 结果（2026-10-12 01:37 ET；`output/v3/cb_largeiss/results.json`）

| AUM | X1 | X2 | S（描述） | 判定 |
|---|---|---|---|---|
| 60万 | −9.4%/−29.9%/−0.71 | 9.8%/−7.0%/1.00 | 8.5%/−16.1%/0.89 | **不通过**（X1 MDD+夏普；X2&lt;12%） |
| 100万 | −9.5%/−30.1%/−0.72 | 10.0%/−6.9%/1.00 | 8.5%/−16.5%/0.88 | **不通过**（X1 MDD+夏普；X2&lt;12%） |

预检与正式 X1 一致。短报：`output/v3/cb_largeiss/SHORT_ZH.md`。**无 Strategy 交接。** promotion_approved=false。
