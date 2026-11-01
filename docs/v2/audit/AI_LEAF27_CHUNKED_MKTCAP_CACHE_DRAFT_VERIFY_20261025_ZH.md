# 叶27 Gate A mktcap_cache DRAFT 盘证 · 2026-10-25 20:08 ET

| 件 | sha8 | 全长 sha256 | 状态 |
|---|---|---|---|
| COVER | `bf83073a` | `bf83073aab0b6e2a42db13181a7c0d4ba69c8b49e316058de9dc94aaab1cd3be` | **MATCH** · HOLD_UNTIL_MAIN_SUBMIT |
| CMD | `30c58132` | `30c581329708ad57e83cc8d2eb3775b686759c57287bd57554e8ce248d6fe04c` | **MATCH** · HOLD_UNTIL_MAIN_SUBMIT |
| DIFF | `779197d8` | `779197d81e296102e61e5b7174e13e02e206fd523d8e0bcac4cc3be2a468b801` | **MATCH**（vs prev `8cb3e86f` → mktcap_cache_r1） |
| HAND | `70701c1d` | `70701c1dfcea94e03dba7bbe3e6387c28a5213942815a234a66e6b8f22c66eab` | **MATCH** · **DRAFT_READY_FOR_ARCH_HOLD** · **未 SUBMITTED** |
| 脚本（新） | `27aae6db` | `27aae6dbec0c80d96799c3cf6a7baba1bf8eaea866f0dae5feb2876e201175f5` | **MATCH CHANGED** |
| 脚本（旧/hist_prune） | `8cb3e86f` | `8cb3e86f0d5b199c474b38eba1950a44b18e4c0a1ded67d0f371429a55810012` | 基线；禁再签旧字节；bak 已落 |
| Arch 草案 | `a2307c8b` | `a2307c8bf48ab8523c566298a4cd42ef3fc3a704ff2d0be910f943ecbc49fe54` | **MATCH** |
| 尖峰笔记 | `dd193511` | `dd193511f82b21440c8462730f26449bfc1bb8c12c4047df394872e72002eae1` | **MATCH** |
| ABORT 回执 | `d8be85cb` | （既有包；本票触发源） | 对照保留 |
| VOID | `fd159322` | （既有包） | 对照保留 |
| lowmem_v1 | `05bd81ea` | `05bd81ea9da97cd53785b374c36273b327ff0302098c5b1cef1368c051d400f8` | **UNCHANGED** |

## 静态自检（本回合）

| 检 | 结果 |
|---|---|
| `--dry-compile-only` | **PASS**：`live:false` `ok_requested:false` `rss_limit_mb:1500` `hist_prune_tag:hist_prune_r1` `mktcap_cache_tag:mktcap_cache_r1`；**无实数加载** |
| `py_compile` → `/tmp/leaf27_mc.pyc` | **PASS** |
| pyflakes（`/tmp/ql_pyflakes_venv`） | **PASS**（exit 0） |
| schema-only `trade_date` | **PASS**：`timestamp[us]`；filters 2 日烟测行数合理（非 leaf27 实跑） |
| `pgrep` leaf27 | **NO_LEAF27_PROC**（未开跑） |
| git commit | **未做** |
| 申 `.ok` / 交 Arch | **未做**（HOLD） |
| 改 lowmem_v1 | **否** |

## forbid_restored（明文六票）

`2be59acd` / `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0`

## 备份

| 位置 | sha8 |
|---|---|
| `/tmp/leaf27_chunked_members_mktcap_r1.py.8cb3e86f.bak` | `8cb3e86f` |
| `docs/v2/audit/_bak/leaf27_chunked_members_mktcap_r1.py.8cb3e86f.bak` | `8cb3e86f` |

## 状态

- **HOLD_UNTIL_MAIN_SUBMIT**；HAND=**DRAFT_READY_FOR_ARCH_HOLD**（**未**自称 SUBMITTED）
- 等主交审 / 新窗 / 新 `.ok`（脚本钉 `27aae6db`）
- 禁自开跑 / 禁抬帽 / 禁申 `.ok` / 禁申 X2
- PRIMARY：`--chunk-mode ndays --chunk-ndays 40` + hist_prune_r1 + mktcap_cache_r1
- sampler 前缀钉：`/tmp/quantlab_leaf27_chunked_mktcap_cache_*`
- live=false · ≠X2
