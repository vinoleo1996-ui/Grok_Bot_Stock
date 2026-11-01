# 叶30 CRR HI_LIQ 计数闸短回执（2026-10-26）

- 角色：QuantLab AI（后台执行器）
- 时点：2026-10-26 17:34 ET（America/New_York；箱 `date`）
- 状态：计数完成；**非** X2 / selfcheck / Book-Smoke；**未**申 `.ok`；**未**动 A18（`.ok` sha8 `6de02e74`）；**未**挂/抬 QUIET。
- `live=false`；`promotion_approved=false`。

## 结论

| 项 | 值 |
|---|---|
| **gate_pass** | **`true`** |
| 规则 | `masked_median>=300 AND zero_frac_masked<=0.05 AND jaccard_top20_max vs leaf19/25 <0.7 (rho>0.5 strength-only)` |
| APPROX | **是**（见下；完整 16 季 CRR 规格仅在 who_pays） |
| 峰 RSS | **1075.9 MB**（软目标 &lt;800；本拍轻量计数仍偏高，已结束未抬限） |
| MemAvailable 起/止 Gi | 4.495 / 3.653 |
| A18 避让 | 是（未触 `.ok`；Eng 窗前完成计数；未抢 mem HOLD） |
| X2/selfcheck/Book-Smoke | **未开** |

## 覆盖（X2 样内 HI_LIQ；再平衡每 20 交易日）

| 口径 | median | min | p10 | 零覆盖日占比 |
|---|---:|---:|---:|---:|
| 原始（未剔银/地/非银） | 2431.0 | 1191.0 | 1376.1000000000001 | 0/30 |
| **掩码后** | **2298.5** | 1088.0 | 1273.3 | **0.0** |
| 掩码后曾可算票数（并集） | 4294 | | | |

行业硬排除（盘面名）：银行=`801780.SI`；房地产=`801180.SI`；非银金融=`801790.SI`（综金按非银）。

## 重叠（最多 6 个均匀再平衡日；截面 rank Spearman + Top-20 Jaccard）

样本日：2024-06-03, 2024-11-28, 2025-05-30, 2025-10-28, 2026-04-27, 2026-10-09

| 对照 | ρ_mean | ρ_max | J20_mean | J20_max | 强度过滤 ρ_mean&gt;0.5 |
|---|---:|---:|---:|---:|---|
| 叶19 `cfacc_rnoa` | 0.3650 | 0.4450 | 0.0085 | 0.0256 | False |
| 叶25 alpha x2 | 0.3707 | 0.4968 | 0.0395 | 0.0526 | False |

说明：Jaccard≥0.7 硬拒门槛本拍**未触**；ρ&gt;0.5 只算强度过滤（本拍均值均 &lt;0.5）。**未算**收益/IC/CAGR。

## APPROX / GAP

**APPROX（醒目）**
- CRR proxy = ocf_to_profit from ocf_to_profit_pit_daily_tushare (YTD_cumulative OCF/net_profit), NOT full 16Q operate_profit CRR
- vol_pen not computed this count pass (coverage uses CRR proxy validity only; overlap uses rank(ocf_to_profit))
- lambda not selected from returns

**GAP**
- ocf_daily_lacks_operate_profit_column_full_CRR_needs_financials_pit

叶25 alpha sha8 actual=`8be12024`（期望 `8be12024`） MATCH。

## 产物钉

| 文件 | sha256 | sha8 |
|---|---|---|
| who_pays `docs/v2/AI_LEAF30_CRR_CFOOE_VOLPEN_WHO_PAYS_DRAFT_20261026_ZH.md` | `e00ba1b7171cd5621c3250881d731d331e1da33f7a80154c2cc0d1979e6c6c00` | **`e00ba1b7`** |
| 计数脚本 `research/leaf30_crr_hiliq_count_gate.py` | `ad524f9e039b40b25d3294b9ca84d56a7c108f16fd2a2d51454ba28c1e4a10d0` | **`ad524f9e`** |
| JSON `output/ai_factory/leaf30_crr_hiliq_count_20261026.json` | `b0e7b1d0809c8bf03356175f32347b4a3492b70ce478e5941f9e98dfe77ceee5` | **`b0e7b1d0`** |

下一跳：priority 回主 → 排冻结 → Arch →（另窗）X2；叶26 不交审；叶28/29 FROZEN；不推 Leo。
