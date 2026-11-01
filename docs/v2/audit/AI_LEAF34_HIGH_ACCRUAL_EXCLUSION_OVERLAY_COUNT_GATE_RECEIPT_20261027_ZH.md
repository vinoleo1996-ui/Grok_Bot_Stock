# 叶34 高应计剔除 overlay HI_LIQ 轻量计数闸短回执（2026-10-27）

- 角色：QuantLab AI（后台执行器）
- 时点：2026-10-27 09:42 ET（America/New_York；ISO `2026-10-27T09:42:00-04:00`）
- 状态：轻量计数完成；**非** X2 / selfcheck / Book-Smoke；**未**申 `.ok`；**未**挂/抬 QUIET；**未**改叶33 正式 `afbbe7e7`。
- 预检：`pgrep -f 'kline.py|export_static.py|snapshot.py|gen.py'` → **EMPTY_OK**。
- `live=false`；`promotion_approved=false`；`EXECUTED_full_alpha=false`。
- mechanism_tag：`g1g5_ashare_high_accrual_exclusion_overlay_v1`

## 结论

| 项 | 值 |
|---|---|
| **gate_pass** | **`true`** |
| 规则 | `masked_median>=300 AND zero_frac_masked<=0.05 AND jaccard_top20_max vs leaf19/25 <0.7 (rho>0.5 strength-only)` |
| APPROX | **是**（醒目；见下） |
| 峰 RSS | **900.0 MB**（rss 意向 1500 禁抬；本拍未抬限） |
| MemAvailable 起/止 Gi | 12.542 / 11.955 |
| X2/selfcheck/Book-Smoke | **未开** |
| 建议改升备选 | **否**（PRIMARY 过闸；备选(2)/(3) 仅登记不升） |

## 覆盖（X2 样内 HI_LIQ；再平衡每 20 交易日）

窗：2024-06-03 → 2026-10-09；n_rebal=30。  
口径：HI_LIQ ∩ 可算 `accrual_cf_proxy=1−ocf_to_profit`（valid：有限、非 denom_small、NP>0）。

| 口径 | median | min | p10 | 零覆盖日占比 |
|---|---:|---:|---:|---:|
| **可算 overlay 有效名（masked）** | **2431.0** | 1191.0 | 1376.1000000000001 | **0.0**（0/30） |
| top-20% 高应计剔除名数 | 486.5 | 239.0 | 275.3 | — |
| HI_LIQ 宇宙规模 | 3154.0 | 1480.0 | 1684.6000000000001 | — |
| 掩码后曾可算票数（并集） | 4487 | | | |

## 重叠（最多 6 个均匀再平衡日；prefer-low-accrual 极性 = `−accrual_cf_proxy` vs 叶19/25 α）

样本日：2024-06-03, 2024-11-28, 2025-05-30, 2025-10-28, 2026-04-27, 2026-10-09

| 对照 | ρ_mean | ρ_max | J20_mean | J20_max | 强度过滤 ρ_mean>0.5 | 硬拒 J20≥0.7 |
|---|---:|---:|---:|---:|---|---|
| 叶19 `cfacc_rnoa`（sha8 `16202b2e`） | 0.3673 | 0.4409 | 0.0130 | 0.0526 | False | False |
| 叶25 alpha x2（sha8 `8be12024`） | 0.3690 | 0.5117 | 0.0327 | 0.0526 | False | False |

说明：Jaccard≥0.7 硬拒门槛本拍**未触**；ρ>0.5 强度过滤本拍**未触**（均值均 <0.5）。**未算**收益/IC/CAGR；**未**披露 vs 叶27/30/31/32/33（冻结/X2 阶段补）。重叠极性用 `−accrual_cf` 以对齐叶19/25「低应计优先」——检验的是「剔除 overlay 的保留偏好」是否近等权复刻完整应计 α。

## APPROX / GAP

**APPROX（醒目）**
- accrual_cf_proxy = `1 - ocf_to_profit` from `ocf_to_profit_pit_daily_tushare`（YTD-ish OCF/NP），**不是**完整 BS `WC_ACC/TA`
- **未**重建叶19 CFACC-TTM / 叶25 cfacc_desens 全窗 α；仅读已有 α parquet 做重叠
- top_q=0.20 为 DRAFT 冻结意向，**未**读收益选阈值
- 本拍**未**做 SW 银行/地产/非银硬排除（披露-only；金融应计怪异可能抬高噪声）
- 无完整 overlay 向量落盘；无 `--allow-real-data` 长跑

**GAP**
- 未算 vs 叶27/30/31/32/33 Jaccard/ρ（X2 overlap 阶段补）
- 未跑 BS WC 路径覆盖对照
- 连续 soft-penalty + SW+style 残差未在本计数构建

叶19 alpha sha8 actual=`16202b2e`；叶25 alpha sha8 actual=`8be12024`（期望 `8be12024`）MATCH。

## 产物钉

| 文件 | 备注 |
|---|---|
| who_pays | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md`（sha8 见就绪摘要） |
| COVER | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_COVER_DRAFT_20261027_ZH.md` |
| 计数脚本（/tmp only） | `/tmp/quantlab_leaf34_high_accrual_exclusion_count_gate.py` |
| JSON | `output/ai_factory/leaf34_high_accrual_exclusion_count_20261027.json` |
| ocf_daily / hiliq sha8 | `f9faf7e7` / `c5433e80` |

下一跳：priority 回主 → 排号 → Arch 只审不签 →（另窗）FROZEN→独立 X2；叶26 不交审；叶28/29/`0087c928` 另队；不推 Leo；≠X2 ACCEPT。
