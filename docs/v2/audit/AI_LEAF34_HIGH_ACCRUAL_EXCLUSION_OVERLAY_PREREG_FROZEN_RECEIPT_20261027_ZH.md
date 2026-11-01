# 叶34 高应计剔除 overlay · PREREG_FROZEN 回执

- 角色：QuantLab AI
- 时刻：2026-10-27 10:04 ET（America/New_York；ISO `2026-10-27T10:04:06-04:00`）
- 动作：按主令 2026-10-27 09:56 ET + Arch **PASS_WITH_CONDITIONS** `9d8a2f9e` 落 **PREREG_FROZEN**（C1–C13 入钉）
- **未实跑** / **未申 `.ok`** / **未落** `research/leaf34*` / **未挂 QUIET** / **未** RESTORED forbid / **未**并入 `0087c928` / **未** git commit / **未** SendToUser / **未** SendToAgent
- live=false · ok_requested=false · EXECUTED=false · ≠X2 ACCEPT · leo_notify=false

## 钉表

| 件 | 路径 | sha8 | 全长 |
|---|---|---|---|
| **PREREG_FROZEN** | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_PREREG_FROZEN_20261027_ZH.md` | **`8be1099e`** | `8be1099e73c6029ad2ddcbe7a18a28fc5a27cc03acfb91cba048e26b7867f815` |
| **PIN（C3）** | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_OCF_PIT_PIN_20261027_ZH.md` | **`bb418e6a`** | `bb418e6ae8ee7fd2b0cfc6816360bcb7bb197537dc1aac44fcfb05d375224e9b` |
| Arch who_pays 审 | `docs/v2/audit/ARCH_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_WHO_PAYS_REVIEW_20261027_ZH.md` | `9d8a2f9e` | MATCH（`9d8a2f9edde9f00ae230b9914025fc95db2fba35dc102f83c2a38c26d8247ecd`） |
| WHO_PAYS DRAFT | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` | `fa6aa2e3` | MATCH |
| COVER DRAFT | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_COVER_DRAFT_20261027_ZH.md` | `76b37ca3` | MATCH |
| COUNT RECEIPT | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_COUNT_GATE_RECEIPT_20261027_ZH.md` | `806e1758` | MATCH |
| COUNT JSON | `output/ai_factory/leaf34_high_accrual_exclusion_count_20261027.json` | `9730d432` | MATCH |

## C1–C13 入钉摘要

| # | 条件 | 本 FROZEN |
|---|---|---|
| C1 | 完整预注册 | **FROZEN 全文**：mask-only；q=0.20；再平衡 20d；X2 窗 2024-06-03→2026-10-09；成本 30bp |
| C2 | 正式脚本另窗 | `research/leaf34*` **ABSENT**（本拍禁落） |
| C3 | ocf/PIT/NP/period_basis | PIN **`bb418e6a`**：日表路径+行数+sha；`e_available_at≤t`；有效行合取；NP≤0 一律剔除；接受 YTD-ish/`YTD_cumulative`（与 COUNT 同口径）；PRIMARY 不用 BS WC |
| C4 | soft-penalty / mask | **明示 mask-only PRIMARY**；连续 soft-penalty 非 PRIMARY，启用须 SW+style |
| C5 | top_q 符号冻结 | q=0.20；高应计=剔除；禁读收益改阈值/翻方向 |
| C6 | FULLA 双钉 | HI_LIQ PRIMARY（mask hiliq_v1，median≥300）+ FULLA 研究（mask fulla_v1，median≥800） |
| C7 | X2 前完整重叠 | vs 19/25/**27/30–33**；解释叶25 尾窗 n_common=0；披露 ρ_max vs25；Jaccard≥0.7 硬拒；ρ>0.5 强度过滤 |
| C8 | forbid | `245df63f+c5ed13df+5774bb6e`+二十票+**`81521fb5`**；禁复用叶25/27/30–33 `.ok`；禁 `--arch-ok-path` |
| C9 | rss+peak_proof | rss=1500 禁抬；peak_proof REQUIRED |
| C10 | 另队 | `0087c928`/叶28/29 不夹带 |
| C11 | overlay≠应计主叶 | 交付=mask-only；禁 CFACC/accrual_quality TopN 主 α；禁叶19/25 α 主输入 |
| C12 | APPROX≠X2 ACCEPT | COUNT gate_pass（APPROX）≠ X2 ACCEPT / Book-Smoke |
| C13 | decay KEEP | 近端=252d；KEEP 三闸合取；失败→最多 WATCH/HOLD；**KEEP 不解阻** X2 ACCEPT（叶32 `45dd87dc`） |

## 机制钉（摘要）

| 项 | FROZEN |
|---|---|
| mechanism | `g1g5_ashare_high_accrual_exclusion_overlay_v1` |
| 公式 | `accrual_cf=1−ocf_to_profit`（NP>0）→ top_q=0.20 → **mask-only** |
| 再平衡 / X2 窗 / 成本 | 20 / 2024-06-03→2026-10-09 / 30bp |
| PRIMARY / 研究 | HI_LIQ_V1.1 / FULLA_V1 |
| 边界 | ≠叶19/25 完整应计主叶；≠accrual_quality TopN；≠叶30 CRR 主轴 |
| 判定 | 叶自身主干级 **或** ρ_excess vs capacity_adv <0.5 且 60万/100万叠加均优于主干 |

## 上下文不回撤

- 叶33 正式 `research/leaf33_share_unlock_pressure_resid_alpha_build.py` sha8 **`afbbe7e7` UNCHANGED**（本拍未改）
- 叶32 HOLD **`45dd87dc`** 不回撤
- `0087c928`/叶28/29 另队不夹带

## 请主

**交主 → Arch 只审本 FROZEN**（不签 `.ok`；不代跑；不挂 QUIET）。PASS 后再谈脚本窗（C2）。≠X2 ACCEPT。勿报 Leo。

live=false · EXECUTED=false.
