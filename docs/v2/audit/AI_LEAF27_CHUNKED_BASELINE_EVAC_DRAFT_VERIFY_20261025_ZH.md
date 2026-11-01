# 叶27 Post-GateA baseline_evac DRAFT 盘证 · 2026-10-25 22:06 ET

| 件 | sha8 | 全长 sha256 | 状态 |
|---|---|---|---|
| COVER | `0ff59ed4` | `0ff59ed4576302224267453821a2a13f07a010ab06f3d14c624b4c73b02f5992` | **MATCH** · HOLD_UNTIL_MAIN_SUBMIT |
| CMD | `bf6ffe4a` | `bf6ffe4a05a2a90fac45e3e4cb8f101a8f5fa619fa48d145a333ecc16f126b25` | **MATCH** · HOLD_UNTIL_MAIN_SUBMIT |
| DIFF | `dc802879` | `dc8028799033600dbd0ed653b2d7868096e514c6d85f5b41bde335e850fd4980` | **MATCH**（vs prev `27aae6db` → baseline_evac_r1） |
| HAND | `b0e01ea4` | `b0e01ea42f589a7cc6f42570cf997ecfe7b5bd93c6e63806b47af6cc6f1a394c` | **MATCH** · **DRAFT_READY_FOR_ARCH_HOLD** · **未 SUBMITTED** |
| 脚本（新） | `585ba746` | `585ba7467a5896354c937d14fe0590fa80535afd6b6263015d3c12e3dfccd4ec` | **MATCH CHANGED**（≠ `27aae6db`） |
| 脚本（旧/Gate A） | `27aae6db` | `27aae6dbec0c80d96799c3cf6a7baba1bf8eaea866f0dae5feb2876e201175f5` | 基线；禁再签旧字节；bak 已落 |
| 主令 | `46dc8cb3` | `46dc8cb34e1a17d0815e63ac80233eae6cf14dcd7220bd10cdb98b6a5112849f` | **MATCH** |
| Arch R2 | `c8dc89b6` | `c8dc89b671e1d803a8295f1819653c135c41a99ef9f66b8a77ed049f82f3b3e2` | **MATCH** |
| 尖峰笔记 | `0b483746` | `0b4837468310b57dfcb87b75cf00c21b4fe41f70c08d27176d2ab4720fd7fe14` | **MATCH** |
| ABORT 回执 | `f0f94c9e` | （既有包；本票触发源） | 对照保留 |
| VOID | `ff0394d0` | （既有包） | 对照保留 |
| VOID `.ok` | `e107383f` | （VOID；禁 RESTORED） | 七票之首 |
| lowmem_v1 | `05bd81ea` | `05bd81ea9da97cd53785b374c36273b327ff0302098c5b1cef1368c051d400f8` | **UNCHANGED** |

## 静态自检（本回合）

| 检 | 结果 |
|---|---|
| `--dry-compile-only` | **PASS**：`live:false` `ok_requested:false` `rss_limit_mb:1500` `baseline_evac_tag:baseline_evac_r1` `mktcap_cache_tag:mktcap_cache_r1` `hist_prune_tag:hist_prune_r1`；forbid 七票含 `e107383f`；对照钉 `c8dc89b6`/`0b483746`/`46dc8cb3`/`27aae6db`；**无实数加载** |
| `py_compile` → `/tmp/leaf27_be.pyc` | **PASS** |
| pyflakes（`/tmp/ql_pyflakes_venv`） | **PASS**（exit 0） |
| `pgrep` kline/export_static/snapshot/gen | **PGREP_EMPTY_OK**（未开跑） |
| 新脚本 sha ≠ `27aae6db…` | **PASS**（`585ba746`） |
| git commit | **未做** |
| 申 `.ok` / 交 Arch | **未做**（HOLD；等主交审） |
| 改 lowmem_v1 | **否** |
| 实现 B/C | **否**（本拍不开） |

## forbid_restored（明文七票）

`e107383f` / `2be59acd` / `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0`

## 备份

| 位置 | sha8 |
|---|---|
| `/tmp/leaf27_chunked_members_mktcap_r1.py.27aae6db.bak` | `27aae6db` |
| `docs/v2/audit/_bak/leaf27_chunked_members_mktcap_r1.py.27aae6db.bak` | `27aae6db` |

## 状态

- **HOLD_UNTIL_MAIN_SUBMIT**；HAND=**DRAFT_READY_FOR_ARCH_HOLD**（**未**自称 SUBMITTED）
- 等主交审 / 新窗 / 新 `.ok`（脚本钉 `585ba746`）
- 禁自开跑 / 禁抬帽 / 禁申 `.ok` / 禁申 X2 / 禁重批旧 Gate A
- PRIMARY：`--chunk-mode ndays --chunk-ndays 40` + hist_prune_r1 + mktcap_cache_r1 + baseline_evac_r1
- sampler 前缀钉：`/tmp/quantlab_leaf27_chunked_baseline_evac_*`
- live=false · ≠X2 · ok_requested=false
