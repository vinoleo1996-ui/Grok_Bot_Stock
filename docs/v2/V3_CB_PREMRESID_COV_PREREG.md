# V3_CB_PREMRESID_COV_PREREG — 溢价平价残差 × 放宽期限带（覆盖修复）
研究级，promotion_approved=false。写于 **2026-10-12 02:45 ET，运行前**。

## 差异
| | CB-PREMRESID（已 fail） | **CB-PREMRESID-COV** |
|---|---|---|
| 期限带 | [1,3] → X1 avg_names=0 | **[0.5, 5]** 年（覆盖探针） |
| 排序 | 同：prem 对 parity 十分位残差 | 同；**≠** MATPREM/NEAR/MERGE/RELAX 原低溢价 |
| 压舱 | 511010 | **单压舱 518880（GOLD 腿）**；禁 DD |

## 规则
- `prem_resid = cb_over_rate − median_by_parity_decile`；score=−resid；top min(15,n) 等权。
- 转股期 ∩ ytm∈[0.5,5] ∩ ADV20≥5e6 ∩ remain≥1e8 ∩ 非强赎。
- CB 袖套 50% + 518880 50%。AUM 60/100万。无 IC/小盘。
- **硬闸：** X1 avg_names=0 或 Sharpe≤0 → fail_precheck。正式需 X2 CAGR≥12%。

## 结果（2026-10-12 02:48 ET）
**pass_explore** 双 AUM。X1 avg_names≈5.13 Sharpe≈0.32；X2 CAGR≈25.5%。交接：`output/v3/handoff_strategy/cb_premresid_cov/`。promotion_approved=false。

## Strategy 对账（2026-10-12 ≈02:57 ET · 全量面板复核）
- **NAV 缺口修复**：移除 `filter_cb_panels`，改用全量 `cb_panels`（对齐 `output/v3/cb_premresid_cov/NAV_GAP_AUDIT_ZH.md`）。
- **pass_all=true**；A≡B≡Beta（max\|Δ\|≈0）。研究级 **explore-pass**（**非晋级**）。
- 主表 60/100万：X2≈**25.51%/25.72%**、MDD≈**−17.48/−17.23%**；X1≈2.69%/2.68%、空仓≈**25.8%**、avg_names≈5.19。
- vs MATPREM 日相关≈0.50（非近亲）。压舱 GOLD only；禁 DD 叠。
- 台账：`descriptive_CB_PREMRESID_COV_explore_pass_recon_fullpanel`；短报 `output/strategy_recon/cb_premresid_cov/SHORT_ZH.md`。
- `promotion_approved=false`；禁小盘。
