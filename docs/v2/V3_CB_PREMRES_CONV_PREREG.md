# V3_CB_PREMRES_CONV_PREREG — 转股期溢价平价残差（无期限带切片）
研究级，promotion_approved=false。写于 **2026-10-12 02:53 ET，运行前**。

## ≠ MATPREM / PREMRESID-COV
| | MATPREM 族 | PREMRESID-COV | **PREMRES-CONV** |
|---|---|---|---|
| 排序 | 原低溢价 | 残差×**ytm[0.5,5]** | 残差×**仅转股期**（**无 ytm 带**） |
| 覆盖策略 | — | 放宽期限 | 去掉期限闸 → X1 覆盖 |

## 规则
- `prem_resid` 对 `cb_value` 十分位；score=−resid；转股期内 ∩ ADV≥5e6 ∩ remain≥1e8 ∩ 非强赎；**无 ytm 过滤**。
- top min(15,n)；CB50%+**518880**50%。硬闸：avg_names>0 且 Sharpe>0。正式 X2≥12%。
- handoff 若通过：NAV 用 **全量 cb_panels**（对齐 NAV_GAP_AUDIT 修复建议）。

## 结果（2026-10-12 02:55 ET）
**fail_precheck** Sharpe≈−0.14（avg_names≈7.3）。无正式。

## Strategy 台账（2026-10-12 ≈02:57 ET）
- **outcome：** `fail_precheck`（X1 Sharpe≈**−0.14**≤0；avg_names≈**7.3**>0 覆盖过闸但夏普不过）。
- **无交接**；未开正式双窗；**勿晋升**。
- 台账 id：`descriptive_CB_PREMRES_CONV_fail_precheck`；`docs/trial_ledger.csv` → `CB-PREMRES-CONV_strategy_note`。
- 源：`output/v3/cb_premres_conv/` + `output/v3/pretest_batch_20261012_ortho2.json`。
- 压舱：**GOLD only**；禁 DD 叠；`promotion_approved=false`；禁小盘。
