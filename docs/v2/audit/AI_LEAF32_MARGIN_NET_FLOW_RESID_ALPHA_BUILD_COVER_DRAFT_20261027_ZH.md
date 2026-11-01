# 叶32 净融资流入强度残差慢 α · 正式构建脚本封面 · **DRAFT ONLY**

- **角色**：QuantLab AI
- **时刻**：2026-10-27T04:08:34-0400（America/New_York；墙钟 2026-10-27 04:08 ET）
- **状态**：**DRAFT ONLY** · **ok_requested=false** · **不是 `.ok`** · **不申 `.ok`** · **禁自开跑** · live=false · promotion_approved=false · **EXECUTED=false**
- **优先级**：主令 ~03:57 ET；Arch FROZEN 只审 **PASS_WITH_CONDITIONS** sha8 **`7c0d864f`**（FROZEN **`6b8de5e9` MATCH**）→ C2 落正式脚本

## 一句话

新脚本 `research/leaf32_margin_net_flow_resid_alpha_build.py` sha8 **`4e0f3c00`** 已落盘；硬钉 FROZEN **`6b8de5e9`**：mechanism=`g1g5_ashare_margin_net_flow_resid_v1`；W/再平衡=20/20；α=`−rank(flow_resid)`；X2 2024-06-03→2026-10-09；HI_LIQ PRIMARY；残差 SW L1 + logmv + mom20/vol20/logADV20；overlap vs 叶19/25/27/30/31 + margin_delta；rss=1500+peak_proof；forbid∋`4bb141c9`+`fdbaa512`+`aa25e989`+`7e239487`+`5af20222`+`5ae077fa`。`--dry-compile-only` **PASS**。**未实跑** / **未申 `.ok`** / **未挂 QUIET**。交主→Arch **只审脚本**。≠X2 ACCEPT。`0087c928` 另队不并入。

## 对照钉（MATCH）

| 项 | sha8 / 值 |
|---|---|
| **正式构建脚本（NEW）** | **`4e0f3c00`** · 全长 `4e0f3c002057393c031598e0379c6622afe8ca4a18579c9ab3b9f3d7ba4ae187` |
| PREREG_FROZEN | **`6b8de5e9`** |
| FROZEN RECEIPT | **`7623ce8c`** |
| Arch FROZEN 审 | **`7c0d864f`** |
| Arch who_pays 审（背景） | **`84df02b5`** |
| WHO_PAYS / COVER（背景） | **`fad5911e`** / **`ebda2603`** |
| 模板（只读未改） | leaf31 build **`08f37fd2`** |
| rss | **1500** 禁抬 + peak_proof REQUIRED |
| PRIMARY | HILIQ × x2 end `20261009` |
| FULLA | 仅 `--also-fulla-research`（默认关；不得作 PRIMARY） |
| forbid 六票 | `4bb141c9`+`fdbaa512`+`aa25e989`+`7e239487`+`5af20222`+`5ae077fa` |
| C9 | `0087c928` 另队不并入 |
| 拟 `.ok`（未创建） | `output/ai_factory/ARCH_RUN_AUTH_LEAF32_MARGIN_NET_FLOW_RESID_X2_HILIQ.ok` |

## 提案

| 项 | 内容 |
|---|---|
| **改动范围** | **仅新建** `research/leaf32_margin_net_flow_resid_alpha_build.py` + 本批 COVER/CMD/DIFF/RECEIPT |
| **动作** | (1) 硬钉 FROZEN 常量；(2) dry-compile pins；(3) 真跑路径：再平衡日懒加载 margin+float+bars → flow_raw → 残差 → −rank → 日度 α；(4) overlap JSON（含 vs margin_delta）；(5) peak_proof |
| **真跑门** | `--allow-real-data` + 现存 `--arch-ok-path`（sha8 not in forbid）+ 主窗；**本拍未开** |
| **不改** | FROZEN/`0087c928`/叶31 脚本/`3ee9fed2`/任一 `.ok`/QUIET；禁 RESTORED 六票 |

## 禁止清单

- 本拍实跑 / `--allow-real-data` / 申 `.ok` / 挂 QUIET / 抬 rss
- RESTORED **`4bb141c9`/`fdbaa512`/`aa25e989`/`7e239487`/`5af20222`/`5ae077fa`**
- 事后翻 α 符号 / W / 再平衡；卖方/金股；Amihud/on_minus_id/CRR/hk_hold 主输入；Δrzye 换皮主规格
- PRIMARY 静默改 FULLA；并入 `0087c928`
- git commit；报 Leo；声称 X2 ACCEPT / Book-Smoke

## 请 Arch / 主

1. **主**：收本 DRAFT → hand Arch **只审脚本**（COVER+CMD+DIFF+脚本 `4e0f3c00`）。
2. **Arch**：只审不签；PASS 后主排**新窗**并签发**新** `.ok`（禁 RESTORED；拟名见上）。
3. 实跑另窗；失败/ABORT → 停+上报；≠X2 ACCEPT。

## 盘证

| 件 | 路径 |
|---|---|
| COVER | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_ALPHA_BUILD_COVER_DRAFT_20261027_ZH.md` |
| CMD | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_ALPHA_BUILD_CMD_DRAFT_20261027_ZH.md` |
| DIFF | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_ALPHA_BUILD_DIFF_DRAFT_20261027.diff` |
| SCRIPT_RECEIPT | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_ALPHA_BUILD_SCRIPT_RECEIPT_20261027_ZH.md` |
| 脚本 | `research/leaf32_margin_net_flow_resid_alpha_build.py` |

live=false · ≠X2 · ok_requested=false · EXECUTED=false · leo_notify=false
