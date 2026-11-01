# 叶27 Gate A mktcap_cache · HAND_TO_ARCH（主已交审）

- **角色**：QuantLab AI
- **时刻**：`2026-10-25T20:13:09-04:00`（America/New_York；墙钟 2026-10-25 20:13 ET）
- **status**：**SUBMITTED_TO_ARCH** · 主令「已交审」；Arch **只审不签**
- **ok_requested**：false · **live**：false · **实跑**：未做 · **`.ok`**：未申

## 包钉（盘证 MATCH）

| 件 | sha8 | 全长 / 路径 |
|---|---|---|
| 脚本 | `27aae6db` | `27aae6dbec0c80d96799c3cf6a7baba1bf8eaea866f0dae5feb2876e201175f5` · `research/leaf27_chunked_members_mktcap_r1.py` |
| COVER | `bf83073a` | `docs/v2/audit/AI_LEAF27_CHUNKED_MKTCAP_CACHE_COVER_DRAFT_20261025_ZH.md` |
| CMD | `30c58132` | `docs/v2/audit/AI_LEAF27_CHUNKED_MKTCAP_CACHE_CMD_DRAFT_20261025_ZH.md` |
| DIFF | `779197d8` | `docs/v2/audit/AI_LEAF27_CHUNKED_MKTCAP_CACHE_DIFF_DRAFT_20261025.diff` |
| HAND | `70701c1d` | `docs/v2/audit/AI_LEAF27_CHUNKED_MKTCAP_CACHE_DRAFT_HAND_20261025_ZH.md` |
| VERIFY | `f01afc74` | `docs/v2/audit/AI_LEAF27_CHUNKED_MKTCAP_CACHE_DRAFT_VERIFY_20261025_ZH.md` |

## 硬钉

- PRIMARY：HILIQ×x2×ndays40；tag `mktcap_cache_r1` + 保留 `hist_prune_r1`
- rss=1500 **禁抬**；sampler `/tmp/quantlab_leaf27_chunked_mktcap_cache_*`
- forbid：`2be59acd`/`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`
- 对照：Arch `a2307c8b` / 笔记 `dd193511` / VOID `fd159322` / 回执 `d8be85cb`
- prev 脚本 `8cb3e86f`；lowmem **未改** `05bd81ea`

## 动作边界

- 主已令 Arch 只审不签；AI **停等审回**
- 禁自开跑 / 禁自申.ok / 禁抬帽 / 禁 silent / ≠X2 / live=false
