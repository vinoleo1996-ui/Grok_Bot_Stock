# 叶38 COVER DRAFT：非标审计意见剔除 overlay

- 时点：2026-10-27 20:42 ET
- mechanism_tag：`g1g5_ashare_audit_nonstd_exclusion_overlay_v1`
- dig sha8 **`fa973826`**
- 状态：DRAFT + 轻量计数完成；**非** X2 / selfcheck / Book-Smoke；**未**申 `.ok`
- **gate_pass=`true`**（厚度过；同构不过拒；peak_rss WATCH）

## 一句话

挂 capacity_adv / HI_LIQ 的**负向剔除 overlay**：最新可用审计意见为非标则 mask=0；非主线因子。

## 钉

| 产物 | 路径 |
|---|---|
| who_pays | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` |
| 计数脚本 | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_COUNT_GATE_SCRIPT_20261027.py` |
| JSON | `output/ai_factory/leaf38_audit_nonstd_exclusion_count_20261027.json` |
| COUNT RECEIPT | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_COUNT_GATE_RECEIPT_20261027_ZH.md` |

## 硬闸摘要

- 厚度：median≥30 ∧ frac(≥10)≥0.60 ∧ zero_frac≤0.50 → 本拍 **PASS**（median=48.0；frac_ge10=1.0）
- Jaccard max vs negevent / 叶36 ≤0.5 → 本拍 **PASS**（0.0562 / 0.0649）
- peak_rss≈1584.4MB >1500 → **WATCH**（正式 X2 前须压峰）

live=false；promotion=false；leo_notify=false；≠X2 ACCEPT。
