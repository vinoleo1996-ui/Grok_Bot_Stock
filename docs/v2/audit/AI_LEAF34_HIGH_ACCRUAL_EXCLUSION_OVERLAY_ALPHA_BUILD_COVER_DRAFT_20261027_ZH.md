# 叶34 高应计剔除 overlay · 正式构建脚本封面 · **DRAFT ONLY**

- **角色**：QuantLab AI
- **时刻**：2026-10-27T10:28:46-04:00（America/New_York；墙钟 2026-10-27 10:28 ET）
- **状态**：**DRAFT ONLY** · **ok_requested=false** · **不是 `.ok`** · **不申 `.ok`** · **禁自开跑** · live=false · promotion_approved=false · **EXECUTED=false**
- **优先级**：主令 2026-10-27 10:14 ET；Arch FROZEN 只审 **PASS_WITH_CONDITIONS** sha8 **`027efa26`**（FROZEN **`8be1099e` MATCH**；PIN **`bb418e6a` MATCH**；RECEIPT **`438ee33d` MATCH**）→ C2 落正式脚本

## 一句话

新脚本 `research/leaf34_high_accrual_exclusion_overlay_alpha_build.py` sha8 **`482009dc`** 已落盘；硬钉 FROZEN **`8be1099e`** / PIN **`bb418e6a`**：mechanism=`g1g5_ashare_high_accrual_exclusion_overlay_v1`；PRIMARY=**mask-only** top_q=**0.20**（高应计 mask=0）；soft-penalty **非 PRIMARY**（默认关）；C3=`accrual_cf=1−ocf_to_profit` + PIT `e_available_at≤t` + NP≤0 剔除 + YTD_cumulative；再平衡 20；X2 2024-06-03→2026-10-09；HI_LIQ PRIMARY；overlap vs 叶19/25/27/30/31/32/**33**；rss=1500+peak_proof；forbid∋`245df63f`+`c5ed13df`+`5774bb6e`+二十票+`81521fb5`；KEEP 三闸+**KEEP 不解阻**；C11 overlay≠应计主叶；C12 APPROX≠X2 ACCEPT。`--dry-compile-only` **PASS**。**未实跑** / **未申 `.ok`** / **未挂 QUIET**。交主→Arch **只审脚本**。≠X2 ACCEPT。`0087c928`/叶28/29 另队；叶33 **`afbbe7e7` UNCHANGED**；叶32 HOLD **`45dd87dc`** 不回撤。

## 对照钉（MATCH）

| 项 | sha8 / 值 |
|---|---|
| **正式构建脚本（NEW）** | **`482009dc`** · 全长 `482009dc697cbf74b369cbf3fb035f1fc447a4af9339de8abf283f3ed4e971bc` |
| PREREG_FROZEN | **`8be1099e`** |
| FROZEN RECEIPT | **`438ee33d`** |
| Arch FROZEN 审 | **`027efa26`** |
| Arch who_pays 审 | **`9d8a2f9e`** |
| WHO / COVER / COUNT / JSON / PIN | **`fa6aa2e3`** / **`76b37ca3`** / **`806e1758`** / **`9730d432`** / **`bb418e6a`** |
| 模板（只读未改） | leaf33 formal **`afbbe7e7` UNCHANGED**；leaf32 **`4e0f3c00`** |
| rss | **1500** 禁抬 + peak_proof REQUIRED |
| PRIMARY | HILIQ × x2 end `20261009`；**mask-only** top_q=0.20 |
| FULLA | 仅 `--also-fulla-research`（默认关；不得作 PRIMARY） |
| forbid | `245df63f+c5ed13df+5774bb6e`+二十票+`81521fb5`（24 sha8） |
| C10 | `0087c928` 另队；叶28/29 不夹带 |
| 拟 `.ok`（未创建） | `output/ai_factory/ARCH_RUN_AUTH_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_HILIQ.ok` |

## 提案

| 项 | 内容 |
|---|---|
| **改动范围** | **仅新建** `research/leaf34_high_accrual_exclusion_overlay_alpha_build.py` + 本批 COVER/CMD/DIFF/RECEIPT |
| **动作** | (1) 硬钉 FROZEN/PIN 常量；(2) dry-compile pins；(3) 真跑路径：再平衡日懒加载 ocf 日表 → accrual_cf → top_q mask → 日度 exclusion mask；(4) overlap JSON vs 19/25/27/30–33；(5) peak_proof |
| **真跑门** | `--allow-real-data` + 现存 `--arch-ok-path`（sha8 not in forbid）+ 主窗；**本拍未开** |
| **不改** | FROZEN/`afbbe7e7`/`4e0f3c00`/`45dd87dc`/`0087c928`/任一 `.ok`/QUIET；禁 RESTORED `245df63f`+`c5ed13df`+`5774bb6e`+二十票+`81521fb5` |

## 禁止清单

- 本拍实跑 / `--allow-real-data` / 申 `.ok` / 挂 QUIET / 抬 rss / git commit
- RESTORED **`245df63f`+`c5ed13df`+`5774bb6e`+二十票+`81521fb5`**
- 事后改 top_q / 翻剔除方向；卖方/金股；CFACC TopN / accrual_quality TopN 当主 α；叶19/25 α 当主输入
- PRIMARY 静默改 FULLA；并入 `0087c928`；夹带叶28/29
- 报 Leo；声称 X2 ACCEPT / Book-Smoke；**KEEP 不解阻**；COUNT APPROX 当 ACCEPT

## 请 Arch / 主

1. **主**：收本 DRAFT → hand Arch **只审脚本**（COVER+CMD+DIFF+脚本 `482009dc`）。
2. **Arch**：只审不签；PASS 后主排**新窗**并签发**新** `.ok`（禁 RESTORED；拟名见上）。
3. 实跑另窗；失败/ABORT → 停+上报；≠X2 ACCEPT。

## 盘证

| 件 | 路径 |
|---|---|
| COVER | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_ALPHA_BUILD_COVER_DRAFT_20261027_ZH.md` |
| CMD | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_ALPHA_BUILD_CMD_DRAFT_20261027_ZH.md` |
| DIFF | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_ALPHA_BUILD_DIFF_DRAFT_20261027.diff` |
| SCRIPT_RECEIPT | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_ALPHA_BUILD_SCRIPT_RECEIPT_20261027_ZH.md` |
| 脚本 | `research/leaf34_high_accrual_exclusion_overlay_alpha_build.py` |

live=false · ≠X2 · ok_requested=false · EXECUTED=false · leo_notify=false
