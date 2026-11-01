# 叶31 Amihud 冲击慢 α · 正式构建脚本封面 · **DRAFT ONLY**

- **角色**：QuantLab AI
- **时刻**：2026-10-27T02:26:17-0400（America/New_York；墙钟 2026-10-27 02:26 ET）
- **状态**：**DRAFT ONLY** · **ok_requested=false** · **不是 `.ok`** · **不申 `.ok`** · **禁自开跑** · live=false · promotion_approved=false · **EXECUTED=false**
- **优先级**：主令 ~02:19 ET；Arch FROZEN 只审 **PASS_WITH_CONDITIONS** sha8 **`7a6a1e1a`**（FROZEN **`bcbec955` MATCH**）→ C2 落正式脚本

## 一句话

新脚本 `research/leaf31_amihud_impact_slow_alpha_build.py` sha8 **`08f37fd2`** 已落盘；硬钉 FROZEN **`bcbec955`**：mechanism=`g1g5_ashare_amihud_impact_slow_v1`；W/再平衡=20/20；α=`−rank(impact_resid)`；X2 2024-06-03→2026-10-09；HI_LIQ PRIMARY；残差 SW L1 + logmv + mom20/vol20/logADV20；overlap vs 叶19/25/27/30；rss=1500+peak_proof；forbid∋`aa25e989`+`7e239487`+`5af20222`+`5ae077fa`。`--dry-compile-only` **PASS**。**未实跑** / **未申 `.ok`** / **未挂 QUIET**。交主→Arch **只审脚本**。≠X2 ACCEPT。`0087c928` 另队不并入。

## 对照钉（MATCH）

| 项 | sha8 / 值 |
|---|---|
| **正式构建脚本（NEW）** | **`08f37fd2`** · 全长 `08f37fd2deb15f6a2a4e6bc7bc16e07d16fc50c70b807e0e1ae617627f98bde0` |
| PREREG_FROZEN | **`bcbec955`** |
| Arch FROZEN 审 | **`7a6a1e1a`** |
| Arch who_pays 审（背景） | **`50cbef3c`** |
| WHO_PAYS / COVER（背景） | **`b1a60f07`** / **`4ff55996`** |
| 模板（只读未改） | leaf30 r3_peakcut **`3ee9fed2`** |
| rss | **1500** 禁抬 + peak_proof REQUIRED |
| PRIMARY | HILIQ × x2 end `20261009` |
| FULLA | 仅 `--also-fulla-research`（默认关；不得作 PRIMARY） |
| forbid | `aa25e989`+`7e239487`+`5af20222`+`5ae077fa` |
| C9 | `0087c928` 另队不并入 |
| 拟 `.ok`（未创建） | `output/ai_factory/ARCH_RUN_AUTH_LEAF31_AMIHUD_IMPACT_SLOW_X2_HILIQ.ok` |

## 提案

| 项 | 内容 |
|---|---|
| **改动范围** | **仅新建** `research/leaf31_amihud_impact_slow_alpha_build.py` + 本批 COVER/CMD/DIFF/RECEIPT |
| **动作** | (1) 硬钉 FROZEN 常量；(2) dry-compile pins；(3) 真跑路径：再平衡日懒加载日频 bars+adj → Amihud → 残差 → −rank → 日度 α；(4) overlap JSON；(5) peak_proof |
| **真跑门** | `--allow-real-data` + 现存 `--arch-ok-path`（sha8 not in forbid）+ 主窗；**本拍未开** |
| **不改** | 叶30 脚本/`0087c928`/任一 `.ok`/QUIET；禁 RESTORED 四票 |

## 禁止清单

- 本拍实跑 / `--allow-real-data` / 申 `.ok` / 挂 QUIET / 抬 rss
- RESTORED **`aa25e989`/`7e239487`/`5af20222`/`5ae077fa`**
- 事后翻 α 符号 / W / 再平衡；卖方/金股；会计主轴；on_minus_id 主输入
- PRIMARY 静默改 FULLA；并入 `0087c928`
- git commit；报 Leo；声称 X2 ACCEPT / Book-Smoke

## 请 Arch / 主

1. **主**：收本 DRAFT → hand Arch **只审脚本**（COVER+CMD+DIFF+脚本 `08f37fd2`）。
2. **Arch**：只审不签；PASS 后主排**新窗**并签发**新** `.ok`（禁 RESTORED；拟名见上）。
3. 实跑另窗；失败/ABORT → 停+上报；≠X2 ACCEPT。

## 盘证

| 件 | 路径 |
|---|---|
| COVER | `docs/v2/audit/AI_LEAF31_AMIHUD_IMPACT_SLOW_ALPHA_BUILD_COVER_DRAFT_20261027_ZH.md` |
| CMD | `docs/v2/audit/AI_LEAF31_AMIHUD_IMPACT_SLOW_ALPHA_BUILD_CMD_DRAFT_20261027_ZH.md` |
| DIFF | `docs/v2/audit/AI_LEAF31_AMIHUD_IMPACT_SLOW_ALPHA_BUILD_DIFF_DRAFT_20261027.diff` |
| SCRIPT_RECEIPT | `docs/v2/audit/AI_LEAF31_AMIHUD_IMPACT_SLOW_ALPHA_BUILD_SCRIPT_RECEIPT_20261027_ZH.md` |
| 脚本 | `research/leaf31_amihud_impact_slow_alpha_build.py` |

live=false · ≠X2 · ok_requested=false · EXECUTED=false · leo_notify=false
