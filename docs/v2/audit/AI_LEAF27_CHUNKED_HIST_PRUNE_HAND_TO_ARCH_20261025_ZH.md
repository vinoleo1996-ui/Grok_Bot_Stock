# 叶27 hist-prune 独立 DRAFT · HAND TO ARCH（**SUBMITTED_TO_ARCH**）

- **时刻**：2026-10-25T16:31:55-04:00（America/New_York；墙钟 2026-10-25 16:31 ET）
- **角色**：QuantLab AI
- **主令交审**：`docs/v2/audit/MAIN_LEAF27_CHUNKED_HIST_PRUNE_SUBMIT_TO_ARCH_20261025_ZH.md` sha8 **`3806f922`**（全长 `3806f92228ea8577530773161dc36090ffbe153ade0db804fe1092384397d6aa`）
- **status**：**SUBMITTED_TO_ARCH**（由 DRAFT_READY_FOR_ARCH_HOLD `cc21f3c7` 改投）
- **ok_requested**：**false** · **禁自开跑** · **禁申 `.ok`** · **禁抬帽** · live=false · promotion_approved=false

## 前置盘证

| 项 | 值 |
|---|---|
| ndays40 `.ok` VOID | Arch 回执 sha8 **`ad2947ef`**；consumed `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_NDAYS40.a7d98ac9.VOID.ABORT_RSS.20261025T1627ET.ok` |
| QUIET | 已 lift（`output/loop/_lifted/RESEARCH_QUIET_leaf27_ndays40_ABORT_RSS_LIFTED_20261025T1627ET.lock`）；现盘无 QUIET |
| ndays40 ABORT 回执 | `03064d50` MATCH（1514MB@chunk6_mktcap；ET_TS=`20261025_162212`） |
| 主 ABORT ack | `169c432a` |
| 脚本 | **CHANGED** `8cb3e86f`（prev `262f9bf6`；`hist_prune_r1`） |

## 交审钉（包齐 · 盘证 MATCH）

| 件 | 路径 | sha256 / sha8 |
|---|---|---|
| COVER | `docs/v2/audit/AI_LEAF27_CHUNKED_HIST_PRUNE_COVER_DRAFT_20261025_ZH.md` | `850225060aeb07d4350d38ca569fe241956359605ee492520235105aca6b8019` / **`85022506`** |
| CMD | `docs/v2/audit/AI_LEAF27_CHUNKED_HIST_PRUNE_CMD_DRAFT_20261025_ZH.md` | `4cc9773a4ebde6548308e717e694df520a4b72877a02a8c40f20df0220f7b3a3` / **`4cc9773a`** |
| DIFF | `docs/v2/audit/AI_LEAF27_CHUNKED_HIST_PRUNE_DIFF_DRAFT_20261025.diff` | `0c7af6ed66b9a9152a95ee3a0d008264ee3bb3b6801e496ff4ab587e27686e90` / **`0c7af6ed`** |
| HAND | `docs/v2/audit/AI_LEAF27_CHUNKED_HIST_PRUNE_DRAFT_HAND_20261025_ZH.md` | `cc21f3c762bac4f370b25cac0b6c6b3d788a6cfa3008c195a909598ddb8b6152` / **`cc21f3c7`**（HOLD 原文；本文件为 SUBMITTED 投递） |
| VERIFY | `docs/v2/audit/AI_LEAF27_CHUNKED_HIST_PRUNE_DRAFT_VERIFY_20261025_ZH.md` | `4714256a107a724cfb85b404be9564ed042772b935062c4f5f6bafa276165931` / **`4714256a`** |
| 脚本 CHANGED | `research/leaf27_chunked_members_mktcap_r1.py` | `8cb3e86f0d5b199c474b38eba1950a44b18e4c0a1ded67d0f371429a55810012` / **`8cb3e86f`** |
| ndays40 ABORT 回执 | `docs/v2/audit/AI_LEAF27_CHUNKED_NDAYS40_HILIQ_X2_RUN_RECEIPT_20261025_ZH.md` | `03064d50bc1997e40cff3a10c55d10e91930473472a183d7ac0c0782b514b099` / **`03064d50`** |

## 提案（PRIMARY ONLY + hist_prune_r1）

- PRIMARY（唯一）：`--universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40` + 脚本 **`8cb3e86f`**（块边界 `_prune_hist` + 空 deque 清理 + 保留 `di%40`）
- **无**同票 FALLBACK；ABORT → **停+上报**（禁再静默换 mode / 禁抬帽）
- rss_limit：**1500** 禁抬帽
- sampler：`/tmp/quantlab_leaf27_chunked_histprune_*` only
- out_dir 建议：`output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_histprune`
- 因子钉：β/W/残差序/HI_LIQ-only / BETA_WIN/IVOL_WIN **未改**；仅 hist 存活键 prune 频率与块边界
- **forbid_restored**（明文）：**`a7d98ac9`** / **`8e51de63`** / **`3a6caa4f`** / **`8bcd79dc`** / **`725be3e0`**
- 禁自开跑；禁申 X2.ok；≠X2；峰证明 REQUIRED

## 请 Arch

1. 审 COVER+CMD+DIFF（脚本宣称 CHANGED `8cb3e86f` vs prev `262f9bf6`；CODE_CHANGE）
2. **本回合不签** `.ok` / 不代跑 / 不挂 QUIET；签窗另排听主
3. 审毕回执主（PASS / PASS_WITH_CONDITIONS / FAIL）即可

## 门禁

- AI：**禁自开跑** / **禁申 `.ok`** / **禁抬帽** / 禁 RESTORED 上列 sha8 / 禁静默换 mode
- live=false · promotion_approved=false · ≠X2
