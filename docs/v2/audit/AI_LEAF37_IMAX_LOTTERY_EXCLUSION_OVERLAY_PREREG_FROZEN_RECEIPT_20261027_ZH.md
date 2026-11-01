# 叶37 IMAX/隔夜彩票剔除 overlay · PREREG_FROZEN 回执

- 角色：QuantLab AI
- 时刻：2026-10-27 17:00 ET（America/New_York；ISO `2026-10-27T17:00:00-04:00`）
- 动作：按主裁 **FROZEN GO** + Arch **PASS_WITH_CONDITIONS** `4a074f0a` 落 **PREREG_FROZEN**（C1–C13 入钉；**C3=B**）+ IMAX_proxy PIN
- **未实跑** / **未申 `.ok`** / **未落** `research/leaf37*` / **未挂 QUIET** / **未** RESTORED forbid / **未** git commit / **未** SendToUser / **未**联系主·Arch·Leo / **未**改叶33 `afbbe7e7` / 叶35 `434ff42c` / **未**放宽叶36 覆盖阈 / **未**开备选 B
- live=false · ok_requested=false · EXECUTED=false · ≠X2 ACCEPT · leo_notify=false

## 钉表

| 件 | 路径 | sha8 | 全长 |
|---|---|---|---|
| **PREREG_FROZEN** | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_PREREG_FROZEN_20261027_ZH.md` | **`c5927f1b`** | `c5927f1b07a67c4e839c3084202e84f10529a379779a3dfc10ae751487676213` |
| **PIN（C3=B）** | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_IMAX_PROXY_PIN_20261027_ZH.md` | **`e01be34c`** | `e01be34cfedeedffe750e753ace1977071d0b073238ac294fe78d75284ea0c2a` |
| Arch who_pays 审 | `docs/v2/audit/ARCH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_WHO_PAYS_REVIEW_20261027_ZH.md` | `4a074f0a` | MATCH（`4a074f0a983a54f30607f01ac8b93f1c2cc4f1ea716bac438c67d8f3e8c79859`） |
| WHO_PAYS DRAFT | `…WHO_PAYS_DRAFT…` | `0ed8e9d8` | MATCH |
| COVER DRAFT | `…COVER_DRAFT…` | `847245f8` | MATCH |
| COUNT RECEIPT | `…COUNT_GATE_RECEIPT…` | `154bc157` | MATCH |
| COUNT SCRIPT | `…COUNT_GATE_SCRIPT…` | `c10b735f` | MATCH |
| COUNT JSON | `output/ai_factory/leaf37_imax_lottery_exclusion_count_20261027.json` | `2217f580` | MATCH |
| dig | `output/d1/DIG_FACTOR_20261027_1625ET.md` | `74234fca` | MATCH |

路径说明：落于 `docs/v2/audit/`（与叶34/35 同目录）。

## C1–C13 入钉摘要

| # | 条件 | 本 FROZEN |
|---|---|---|
| C1 | 完整预注册 | **FROZEN 全文**：mask-only；q=0.20；再平衡 20d；X2 窗 2024-06-03→2026-10-09；成本 30bp；判定双路径 |
| C2 | 正式脚本另窗 | `research/leaf36*|leaf37*` **ABSENT**；计数脚本 audit **`c10b735f`**（非正式构建） |
| C3 | IMAX APPROX 二选一 | **(B)**：`IMAX_proxy`=raw `r_id` 20d top-5（≥15）为**交付定义**；`full_residual_e_id=false`；持续 APPROX；PIN **`e01be34c`**；本拍**不**升全 e_id |
| C4 | soft-penalty / mask | **明示 mask-only PRIMARY**；soft-penalty 非 PRIMARY；另窗须 SW L1+logmv+style（mom20/vol20/logADV20），缺列→PIN_GAP |
| C5 | top_q 符号冻结 | q=**0.20**；高 IMAX=剔除；禁读收益改阈值/翻方向；再平衡=**20** |
| C6 | HI_LIQ 主 | HI_LIQ PRIMARY（mask hiliq_v1）；不得静默改 FULLA |
| C7 | X2 前完整重叠 | vs 18/18v/27 硬拒；vs 24/34/35/36 披露；ρ18≈0.505 / ρ27≈0.665 强度过滤披露；COUNT 轻量不替 |
| C8 | forbid | `eb70eef4+00eec671+10927bd9+25ae4572+178e90e9+c1b71e64+245df63f+c5ed13df+5774bb6e+81521fb5+02426b73+4bb141c9+fdbaa512+aa25e989+7e239487+5af20222+5ae077fa+3c297052+e107383f+2be59acd+a7d98ac9+8e51de63+3a6caa4f+8bcd79dc+725be3e0+0f50daf7+3c19dd7d+1c32ab1e+6054b3bf+6de02e74`；禁复用叶18/24/27/30–36 `.ok`；禁 `--arch-ok-path`；禁 RESTORED |
| C9 | rss+peak_proof | rss=1500 禁抬；peak_proof REQUIRED |
| C10 | 叶36 inquiry HOLD CLOSED | 禁复开 inquiry；禁放宽覆盖阈；WHO `feaa5dbb` / JSON `575e8276` 不回撤 |
| C11 | overlay≠叶24 −IMAX 主叶 | 交付=mask-only overlay 叠主干；禁完整 `g1g5_ashare_imax_intraday_v1`；禁 18/27/24 α 主输入 |
| C12 | APPROX≠X2 ACCEPT | COUNT gate_pass（APPROX）≠ X2 ACCEPT / Book-Smoke / 升纸面 |
| C13 | decay KEEP | 近端=252d（≥126 才出 α）；KEEP=`latest_resid_α>0 ∧ 非连降5季 ∧ H2_net_cagr>510300`；失败→最多 WATCH/HOLD；**KEEP 不解阻** X2 ACCEPT |

## 机制钉（摘要）

| 项 | FROZEN |
|---|---|
| mechanism | `g1g5_ashare_imax_lottery_exclusion_overlay_v1` |
| 公式 | `r_id=(1+ret)/(1+ret_on)−1`；`IMAX_proxy=mean(top5 r_id,20d)`；`H_t=top_q 0.20` → **mask-only** |
| C3 | **(B)** proxy 交付；`full_residual_e_id=false` |
| C4 | **mask-only PRIMARY** |
| C5 / 再平衡 / X2 窗 / 成本 | q=0.20；20；2024-06-03→2026-10-09；30bp |
| C11 | **≠** 叶24 −IMAX 主叶 |
| 判定 | 叶自身主干级 **或** ρ_excess vs capacity_adv <0.5 且 60万/100万叠加均优于主干 |

## 盘证（本拍后）

| 项 | 值 |
|---|---|
| `research/leaf36*` | **ABSENT** |
| `research/leaf37*` | **ABSENT** |
| live `.ok`（ai_factory 非 consumed/superseded） | **0** |
| QUIET `output/loop/RESEARCH_QUIET.lock` | **ABSENT** |
| 叶33 正式 | **`afbbe7e7` UNCHANGED** |
| 叶35 正式脚本 | **`434ff42c` 未改** |
| 叶36 inquiry HOLD | **不回撤**（`feaa5dbb`/`575e8276`） |

## 请主

**交主 → Arch 只审本 FROZEN**（不签 `.ok`；不代跑；不挂 QUIET）。PASS 后再谈脚本窗（C2 正式 `research/leaf37*`）。≠X2 ACCEPT。勿报 Leo。备选 B 勿开。

live=false · EXECUTED=false · ok_requested=false.
