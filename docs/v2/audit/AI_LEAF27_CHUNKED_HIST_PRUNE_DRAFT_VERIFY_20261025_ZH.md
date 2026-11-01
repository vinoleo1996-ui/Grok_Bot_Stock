# 叶27 hist-prune DRAFT 盘证 · 2026-10-25 16:28 ET

| 件 | sha8 | 全长 sha256 | 状态 |
|---|---|---|---|
| COVER | `85022506` | `850225060aeb07d4350d38ca569fe241956359605ee492520235105aca6b8019` | **MATCH** · HOLD_UNTIL_MAIN_SUBMIT |
| CMD | `4cc9773a` | `4cc9773a4ebde6548308e717e694df520a4b72877a02a8c40f20df0220f7b3a3` | **MATCH** · HOLD_UNTIL_MAIN_SUBMIT |
| DIFF | `0c7af6ed` | `0c7af6ed66b9a9152a95ee3a0d008264ee3bb3b6801e496ff4ab587e27686e90` | **MATCH**（vs prev `262f9bf6` → hist_prune_r1） |
| HAND | `cc21f3c7` | `cc21f3c762bac4f370b25cac0b6c6b3d788a6cfa3008c195a909598ddb8b6152` | **MATCH** · **DRAFT_READY_FOR_ARCH_HOLD** · **未 SUBMITTED** |
| 脚本（新） | `8cb3e86f` | `8cb3e86f0d5b199c474b38eba1950a44b18e4c0a1ded67d0f371429a55810012` | **MATCH CHANGED** |
| 脚本（旧/ABORT） | `262f9bf6` | `262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10` | 基线；禁再签旧字节 |
| ndays40 ABORT 回执 | `03064d50` | `03064d50bc1997e40cff3a10c55d10e91930473472a183d7ac0c0782b514b099` | **MATCH**（触发源） |
| ndays40 baseline COVER/CMD/DIFF | `ec5f67e9` / `af6f0d49` / `5449dde5` | （既有包；本票不覆盖） | 对照保留 |

## 静态自检（本回合）

| 检 | 结果 |
|---|---|
| `--dry-compile-only` | OK：`live:false` `ok_requested:false` `rss_limit_mb:1500` `hist_prune_tag:hist_prune_r1`；**无实数加载** |
| `py_compile` → `/tmp/leaf27_hp.pyc` | OK |
| pyflakes（`/tmp/ql_pyflakes_venv`） | OK（exit 0） |
| `pgrep` leaf27 | **NO_LEAF27_PROC**（未开跑） |
| git commit | **未做** |
| 申 `.ok` / 交 Arch | **未做**（HOLD） |

## forbid_restored（明文）

`a7d98ac9`（ndays40 已 VOID） / `8e51de63`（month） / `3a6caa4f` / `8bcd79dc` / `725be3e0`

## QUIET / `.ok` 盘态（本回合核）

| 项 | 盘态 |
|---|---|
| `output/loop/RESEARCH_QUIET.lock` | **不存在**（Arch 已 lift → `_lifted/RESEARCH_QUIET_leaf27_ndays40_ABORT_RSS_LIFTED_20261025T1627ET.lock`） |
| live `.ok` `a7d98ac9` | **不在** `output/ai_factory/`；在 `_consumed/…a7d98ac9.VOID.ABORT_RSS.20261025T1627ET.ok` |
| AI 擅 lift？ | **否** |

## 状态

- **HOLD_UNTIL_MAIN_SUBMIT**；HAND=**DRAFT_READY_FOR_ARCH_HOLD**（**未**自称 SUBMITTED）
- 等主交审 / 新窗 / 新 `.ok`（脚本钉 `8cb3e86f`）
- 禁自开跑 / 禁抬帽 / 禁申 `.ok` / 禁申 X2
- PRIMARY：`--chunk-mode ndays --chunk-ndays 40` + hist_prune_r1
- live=false · ≠X2
