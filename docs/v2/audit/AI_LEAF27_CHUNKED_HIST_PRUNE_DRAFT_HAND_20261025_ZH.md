# 叶27 hist-prune 独立侧稿 HAND 回执 · **DRAFT_READY_FOR_ARCH_HOLD**

- **角色**：QuantLab AI（执行器）
- **时刻**：2026-10-25T16:28:37-04:00（America/New_York；墙钟 2026-10-25 16:28 ET）
- **status**：**DRAFT_READY_FOR_ARCH_HOLD** — **未 SUBMITTED**；**勿交 Arch 审**；等主令「交审」后再 hand
- **ok_requested**：false · **live**：false · **实跑**：未做 · **`.ok`**：未申 · **QUIET**：本回合 **未擅 lift**（盘上 QUIET 已由 Arch VOID 流程移至 `_lifted/…ndays40…1627ET.lock`；`.ok` `a7d98ac9` 已入 `_consumed/…VOID.ABORT_RSS…`）
- **三件+脚本盘证**：COVER `85022506` / CMD `4cc9773a` / DIFF `0c7af6ed`；脚本 **CHANGED** `8cb3e86f`（prev `262f9bf6`）
- **触发**：ndays40 ABORT 回执 `03064d50`（1514@chunk6）；主 ack `169c432a`；主令 hist-prune DRAFT only

## 三件 + 脚本盘证

| 件 | 路径 | sha256 |
|---|---|---|
| COVER | `docs/v2/audit/AI_LEAF27_CHUNKED_HIST_PRUNE_COVER_DRAFT_20261025_ZH.md` | `850225060aeb07d4350d38ca569fe241956359605ee492520235105aca6b8019` |
| CMD | `docs/v2/audit/AI_LEAF27_CHUNKED_HIST_PRUNE_CMD_DRAFT_20261025_ZH.md` | `4cc9773a4ebde6548308e717e694df520a4b72877a02a8c40f20df0220f7b3a3` |
| DIFF | `docs/v2/audit/AI_LEAF27_CHUNKED_HIST_PRUNE_DIFF_DRAFT_20261025.diff` | `0c7af6ed66b9a9152a95ee3a0d008264ee3bb3b6801e496ff4ab587e27686e90` |
| 脚本（CHANGED） | `research/leaf27_chunked_members_mktcap_r1.py` | `8cb3e86f0d5b199c474b38eba1950a44b18e4c0a1ded67d0f371429a55810012` |

sha8 速查：COVER **`85022506`** · CMD **`4cc9773a`** · DIFF **`0c7af6ed`** · 脚本 **`8cb3e86f`**

## 对照钉

| 钉 | 值 |
|---|---|
| ndays40 ABORT 回执 | `03064d50…`（ET_TS=`20261025_162212`；1514MB @chunk6_mktcap） |
| 主 ack | `169c432a` |
| 已消费 ndays40 `.ok` | `a7d98ac9` **禁 RESTORED**（盘：`_consumed/…VOID.ABORT_RSS.20261025T1627ET.ok`） |
| VOID/禁复用 | **`a7d98ac9`** / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0` |
| ndays40 baseline 包 | COVER `ec5f67e9` / CMD `af6f0d49` / DIFF `5449dde5`（**不覆盖**） |
| PRIMARY CLI | `--chunk-mode ndays --chunk-ndays 40`（**同** ABORT 票；代码修复） |
| hist_prune | chunk-boundary + 保留 di%40；tag `hist_prune_r1` |
| rss_limit | 1500 禁抬 |
| sampler | `/tmp/quantlab_leaf27_chunked_histprune_*` only |
| 交审门 | 等主令「交审」；**HOLD** 非 SUBMITTED |

## 动作边界

- **未**交 Arch；**未**申 `.ok`；**未**实跑；**未** git commit
- **未**擅 lift QUIET；**未**抬帽；**未**启动任何实数进程
- 工作树已打 hist_prune_r1 补丁（脚本 `8cb3e86f`）；静态 py_compile/pyflakes/dry-compile OK
- 禁自开跑 / 禁申 X2.ok / 禁复用 VOID/CONSUMED / 禁静默切 mode
- ≠X2 · live=false · **DRAFT_READY_FOR_ARCH_HOLD**（**未 SUBMITTED**）
