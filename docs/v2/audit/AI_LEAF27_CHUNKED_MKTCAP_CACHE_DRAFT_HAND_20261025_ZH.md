# 叶27 Gate A mktcap_cache 独立侧稿 HAND 回执 · **DRAFT_READY_FOR_ARCH_HOLD**

- **角色**：QuantLab AI（执行器）
- **时刻**：2026-10-25T20:08:10-04:00（America/New_York；墙钟 2026-10-25 20:08 ET）
- **status**：**SUBMITTED_TO_ARCH** — 主已交审（2026-10-25 20:13 ET）；Arch **只审不签**；HAND_TO_ARCH `4cac1bae`；AI 停等审回
- **ok_requested**：false · **live**：false · **实跑**：未做 · **`.ok`**：未申 · **QUIET**：本回合 **未擅 lift**
- **三件+脚本盘证**：COVER `bf83073a` / CMD `30c58132` / DIFF `779197d8`；脚本 **CHANGED** `27aae6db`（prev `8cb3e86f`）
- **触发**：hist-prune ABORT 回执 `d8be85cb`（1518@chunk6_mktcap）；Arch 草案 `a2307c8b` RECOMMENDED=A；Leo 开 A；主令立刻出 COVER/CMD/DIFF/HAND

## 三件 + 脚本盘证

| 件 | 路径 | sha256 |
|---|---|---|
| COVER | `docs/v2/audit/AI_LEAF27_CHUNKED_MKTCAP_CACHE_COVER_DRAFT_20261025_ZH.md` | `bf83073aab0b6e2a42db13181a7c0d4ba69c8b49e316058de9dc94aaab1cd3be` |
| CMD | `docs/v2/audit/AI_LEAF27_CHUNKED_MKTCAP_CACHE_CMD_DRAFT_20261025_ZH.md` | `30c581329708ad57e83cc8d2eb3775b686759c57287bd57554e8ce248d6fe04c` |
| DIFF | `docs/v2/audit/AI_LEAF27_CHUNKED_MKTCAP_CACHE_DIFF_DRAFT_20261025.diff` | `779197d81e296102e61e5b7174e13e02e206fd523d8e0bcac4cc3be2a468b801` |
| 脚本（CHANGED） | `research/leaf27_chunked_members_mktcap_r1.py` | `27aae6dbec0c80d96799c3cf6a7baba1bf8eaea866f0dae5feb2876e201175f5` |

sha8 速查：COVER **`bf83073a`** · CMD **`30c58132`** · DIFF **`779197d8`** · 脚本 **`27aae6db`**

## 对照钉

| 钉 | 值 |
|---|---|
| Arch 草案 | `a2307c8b`（RECOMMENDED=A） |
| 尖峰笔记 | `dd193511` |
| ABORT 回执 | `d8be85cb`（1518MB @chunk6_mktcap） |
| VOID 权威 | `fd159322` |
| forbid 六票 | `2be59acd` / `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0` |
| hist-prune 基线包 | COVER `85022506` 等（**不覆盖**） |
| PRIMARY CLI | `--chunk-mode ndays --chunk-ndays 40`（**同** ABORT 票；代码修复） |
| mktcap_cache | 跨块 DayFloatMap + miss-only filters；tag `mktcap_cache_r1` |
| hist_prune | **保留** `hist_prune_r1` |
| rss_limit | 1500 禁抬 |
| sampler | `/tmp/quantlab_leaf27_chunked_mktcap_cache_*` only |
| 交审门 | 主已交审；停等 Arch 审回 |

## 动作边界

- **未**交 Arch；**未**申 `.ok`；**未**实跑；**未** git commit
- **未**擅 lift QUIET；**未**抬帽；**未**启动任何实数进程
- 工作树已打 mktcap_cache_r1 补丁（脚本 `27aae6db`）；备份 `8cb3e86f` → `/tmp/…8cb3e86f.bak` 与 `docs/v2/audit/_bak/`
- 静态 py_compile/pyflakes/dry-compile OK；schema-only 探 `trade_date` 类型 OK
- **未**改 `research/g1g5_on_minus_id_idio_ivol_alpha_lowmem_v1.py`（仍 `05bd81ea`）
- 禁自开跑 / 禁申 X2.ok / 禁复用 VOID/CONSUMED / 禁静默切 mode
- ≠X2 · live=false · **SUBMITTED_TO_ARCH**（H2A `4cac1bae`）
