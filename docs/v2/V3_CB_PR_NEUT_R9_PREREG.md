# V3_CB_PR_NEUT_R9_PREREG — 中性化平价溢价率残差第8–9分位
研究级，promotion_approved=false。写于 2026-10-12 05:20 ET，运行前。

## 唯一收益来源（一句）
每日横截面 OLS：`cb_over_rate ~ 1 + cb_value + log(remain_size) + TTM` 的残差取第**8–9**十分位（**避开第10最极端便宜桶**）ADV/流动性过滤后等权；收割相对同平价/余额/期限的估值残差补偿（机构定价摩擦）。

## ≠ 禁族
- ≠ MATPREM（溢价×期限带排序，非回归残差）
- ≠ PARITY-BAND（绝对平价带[85,105] ADV）
- ≠ PREMRESID-COV / 裸低溢价（非未中性化低 `cb_over_rate`）
- ≠ PUTFLOOR / MATWALL / IND-RATE / LPR / COV / SEASON / BOND-NAV-MR

## 简化（相对华泰 2023）
盒上 **无评级字段** → 不做 Rating 三分组；预注册写明为简化版 \(PR\sim Parity+\log Size+TTM\)。

## 规则
- 流动性：当日 `amount≥3000`（字段量级为千元）
- 余额：`cb_share_raw` PIT `remain_size`；若缺失则回退 `issue_size`；回归用 `log(size)`，`size>0`
- TTM：`(maturity_date−T)/365.25 > 0`
- 可交易：转股期 ∩ 非已公告实施/提示强赎排除 ∩（PIT remain≥1e8 若可得）
- 残差十分位：最低残差=第10桶（最「便宜」）；持有第**8–9**桶；第10桶排除
- 桶内等权；n_ols<10 或无法切分 → 空仓；CB 袖套 50% + **518880** 50%（空仓则 100% GOLD）
- 再平衡：月末；FULLCB=1；主表仅 60万/100万；GOLD only
HARD GATE：X1 Sharpe≤0 或 avg_names==0 → fail_precheck。
正式闸：X1+X2 Sharpe>0，MDD≥−25%，X2 CAGR≥12%。

## 数据风险
X1（2015–17）可转债池极薄，`amount≥3000` 下多数月末 n_ols<10 → 预期空仓率高、黄金主导；正式以闸门为准。

## Strategy 台账附记（2026-10-12T05:15:52-04:00）
X1 **avg_names=0**（Sharpe≈0.46 为纯 GOLD）→ **fail_precheck**；未开正式双窗；无交接；ortho_ext1b。
台账：`descriptive_CB_PR_NEUT_R9_fail_precheck`。
**正交义务：** 与 PREMRESID-COV 同族；日后重开交接必须测日相关，`|ρ|>0.85` → near_relative 拒独立 pass。亦核 MATPREM/PARITY/GOLD。
**promotion_approved=false**；GOLD only。
