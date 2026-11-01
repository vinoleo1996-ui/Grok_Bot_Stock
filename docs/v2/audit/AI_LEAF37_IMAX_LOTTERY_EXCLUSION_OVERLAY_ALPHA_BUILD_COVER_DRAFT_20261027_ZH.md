# 叶37 IMAX/隔夜彩票剔除 overlay · 正式构建脚本封面 · **DRAFT ONLY**

- **角色**：QuantLab AI
- **时刻**：2026-10-27T17:21:30-04:00（America/New_York；墙钟 2026-10-27 17:21 ET）
- **状态**：**DRAFT ONLY** · **ok_requested=false** · **不是 `.ok`** · **不申 `.ok`** · **禁自开跑** · live=false · promotion_approved=false · **EXECUTED=false**
- **优先级**：主令 2026-10-27 ~17:11 ET；Arch FROZEN 只审 **PASS_WITH_CONDITIONS** sha8 **`a5a9336d`**（FROZEN **`c5927f1b` MATCH**；PIN **`e01be34c` MATCH**；RECEIPT **`3992f0fa` MATCH**）→ C2 落正式脚本

## 一句话

新脚本 `research/leaf37_imax_lottery_exclusion_overlay_alpha_build.py` sha8 **`108aba8f`** 已落盘；硬钉 FROZEN **`c5927f1b`** / PIN **`e01be34c`**：mechanism=`g1g5_ashare_imax_lottery_exclusion_overlay_v1`；PRIMARY=**mask-only** top_q=**0.20**（高 IMAX mask=0）；soft-penalty **非 PRIMARY**（默认关）；C3=B `IMAX_proxy`=raw `r_id` 20d top-5（≥15）；`full_residual_e_id=false` 持续 APPROX；再平衡 20；X2 2024-06-03→2026-10-09；HI_LIQ PRIMARY；overlap 硬拒 vs 叶18/18v/27；披露 vs 叶24/34/35/36；rss=1500+peak_proof；forbid∋`eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+旧票；KEEP 三闸+**KEEP 不解阻**；C11 overlay≠叶24 `g1g5_ashare_imax_intraday_v1` 主叶；C12 APPROX≠X2 ACCEPT。`--dry-compile-only` **PASS**。**未实跑** / **未申 `.ok`** / **未挂 QUIET**。交主→Arch **只审脚本**。≠X2 ACCEPT。叶36 HOLD CLOSED WHO **`feaa5dbb`** / JSON **`575e8276`** 不回撤；叶33 **`afbbe7e7` UNCHANGED**；叶35 **`434ff42c` UNCHANGED**；叶32 HOLD **`45dd87dc`**。

## 对照钉（MATCH）

| 项 | sha8 / 值 |
|---|---|
| **正式构建脚本（NEW）** | **`108aba8f`** · 全长 `108aba8f5c3f58f2792d31b36a793ff5251fa732174667e037ffae113eb91f2b` |
| PREREG_FROZEN | **`c5927f1b`** |
| FROZEN RECEIPT | **`3992f0fa`** |
| Arch FROZEN 审 | **`a5a9336d`** |
| Arch who_pays 审 | **`4a074f0a`** |
| WHO / COVER / COUNT / SCRIPT / JSON / PIN / dig | **`0ed8e9d8`** / **`847245f8`** / **`154bc157`** / **`c10b735f`** / **`2217f580`** / **`e01be34c`** / **`74234fca`** |
| 模板（只读未改） | leaf34 **`482009dc`**；leaf33 formal **`afbbe7e7` UNCHANGED**；leaf35 formal **`434ff42c` UNCHANGED** |
| HI_LIQ mask | **`c5433e80`** |
| rss | **1500** 禁抬 + peak_proof REQUIRED |
| PRIMARY | HILIQ × x2 end `20261009`；**mask-only** top_q=0.20；C3=B |
| FULLA | 仅 `--also-fulla-research`（默认关；不得作 PRIMARY） |
| forbid | `eb70eef4+00eec671+10927bd9+25ae4572+178e90e9+c1b71e64+245df63f+c5ed13df+5774bb6e+81521fb5+02426b73`+二十票（30 sha8） |
| C10 | 叶36 HOLD CLOSED；禁复开 inquiry / 禁放宽覆盖阈 |
| 拟 `.ok`（未创建） | `output/ai_factory/ARCH_RUN_AUTH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_HILIQ.ok` |

## 提案

| 项 | 内容 |
|---|---|
| **改动范围** | **仅新建** `research/leaf37_imax_lottery_exclusion_overlay_alpha_build.py` + 本批 COVER/CMD/DIFF/RECEIPT |
| **动作** | (1) 硬钉 FROZEN/PIN 常量；(2) dry-compile pins；(3) 真跑路径：panel→`r_id`→`IMAX_proxy`→top_q mask→日度 exclusion mask；(4) overlap JSON vs 18/18v/27（硬）+24/34/35/36（披露）；(5) peak_proof |
| **真跑门** | `--allow-real-data` + 现存 `--arch-ok-path`（sha8 not in forbid）+ 主窗；**本拍未开** |
| **不改** | FROZEN/PIN/COUNT/`afbbe7e7`/`434ff42c`/`482009dc`/`45dd87dc`/任一 `.ok`/QUIET；禁 RESTORED `eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+旧票；禁 `research/leaf36*` |

## 禁止清单

- 本拍实跑 / `--allow-real-data` / 申 `.ok` / 挂 QUIET / 抬 rss / git commit
- RESTORED **`eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+旧票全集**
- 事后改 top_q / 翻剔除方向；静默升全 `e_id`；叶24 完整 −IMAX 主 α；叶18/27/24 α 当主输入
- PRIMARY 静默改 FULLA；复开叶36 inquiry；放宽其覆盖阈
- 报 Leo；声称 X2 ACCEPT / Book-Smoke；**KEEP 不解阻**；COUNT APPROX 当 ACCEPT

## 请 Arch / 主

1. **主**：收本 DRAFT → hand Arch **只审脚本**（COVER+CMD+DIFF+脚本 `108aba8f`）。
2. **Arch**：只审不签；PASS 后主排**新窗**并签发**新** `.ok`（禁 RESTORED；拟名见上）。
3. 实跑另窗；失败/ABORT → 停+上报；≠X2 ACCEPT。

## 盘证

| 件 | 路径 |
|---|---|
| COVER | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_ALPHA_BUILD_COVER_DRAFT_20261027_ZH.md` |
| CMD | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_ALPHA_BUILD_CMD_DRAFT_20261027_ZH.md` |
| DIFF | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_ALPHA_BUILD_DIFF_DRAFT_20261027.diff` |
| SCRIPT_RECEIPT | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_ALPHA_BUILD_SCRIPT_RECEIPT_20261027_ZH.md` |
| 脚本 | `research/leaf37_imax_lottery_exclusion_overlay_alpha_build.py` |

live=false · ≠X2 · ok_requested=false · EXECUTED=false · leo_notify=false
