# V3_CB_CLAUSE_MISPR_PREREG — 条款状态错价（事件+价格边界）
研究级，promotion_approved=false。写于 2026-10-12 05:20 ET，运行前。

## 唯一收益来源（一句）
在强赎/回售/下修**条款相关态**下，用市价相对朴素上界 `max(bond_value, cb_value)` 的低估分数做多便宜券 ADV 等权（简化 LSMC 条款路径依赖错价代理，禁 IC）。

## ≠ 禁族
- ≠ RESET-COOL（下修后 60 日冷却再 ADV；本臂在**提示/触发窗内**按错价排序）
- ≠ CALL-HEAT（CB≥128 热度广度→削 510300；本臂**不持有/不削** 510300）
- ≠ CLAUSE-SM（(PUT∨RESET)∧¬CALL 状态机 ADV，**不**按债底/平价上界错价分）
- ≠ PUTFLOOR-NEAR（close/bond_value 带内全体 ADV，无条款态过滤）
- ≠ MATPREM / PARITY / COV / IND-RATE / LPR / MATWALL / SEASON / BOND-NAV-MR

## 规则
### 条款相关态（并集，PIT：`available_at.normalize() < T`）
1. **事件**：回售提示/回售公告（≤60日历日）；触发下修提示/董事会提议下修/转股价下修/转股价变动推导（≤90日）；公告提示强赎/已满足强赎条件（≤90日）
2. **强赎接近度（价格）**：`close≥125`（接近强赎触发区）
3. **排除**：已 `公告实施强赎` 且 available_at&lt;T

### 错价分
\[
score = \frac{\max(bond\_value,\ cb\_value) - close}{close}
\]
仅 `score>0`（市价低于债底与平价的朴素上包络）。ADV（amount×1e4 的 20日均）Top `min(15,n)` 等权。

- 可交易：转股期 ∩ remain PIT≥1e8（若可得）∩ ADV≥1e7
- n&lt;2 → 空仓；CB 50% + **518880** 50%
- 再平衡：约每 10 交易日；FULLCB；60/100万；GOLD only
HARD GATE：X1 Sharpe≤0 或 avg_names==0 → fail_precheck。
正式闸：X1+X2 Sharpe>0，MDD≥−25%，X2 CAGR≥12%。

## 数据风险
X1 事件稀疏（回售/已满足强赎几乎无），主要靠 `公告提示强赎`/`转股价变动推导` + `close≥125`；预期 X1 池薄、黄金主导。

## Strategy 对账附记（2026-10-12T05:16:44-04:00）
`output/strategy_recon/cb_clause_mispr/`：EngA≡Beta；**pass_all=false**（X2 A–B隙）；vs MATPREM/COV/CALL-HEAT/GOLD 日相关均&lt;0.85。
**X1 avg_names≈0.04、黄金≈98.9% → ballast_dominated（X1净值近似GOLD）**；Beta S 窗 MDD≈**−27.4%**（非主表证据）。
台账：`descriptive_CB_CLAUSE_MISPR_recon_AB_gap_research_observe`。**promotion_approved=false**。
