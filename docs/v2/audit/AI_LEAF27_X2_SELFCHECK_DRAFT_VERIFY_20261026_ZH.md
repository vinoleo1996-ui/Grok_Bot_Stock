# 叶27 X2 selfcheck_v2 DRAFT 盘证 · 2026-10-26 00:35 ET

| 件 | sha8 | 全长 sha256 | 状态 |
|---|---|---|---|
| PIN | `4e0473bd` | `4e0473bdd312761a12b3be0defd5d33194a3f8ea3dca1ec5b7ad264f6ce3fb82` | **MATCH** · SELFCHECK_EXECUTED=false |
| COVER | `1e28d0e5` | `1e28d0e5232df70a601870ae9b145074ba9608638c485dee31c4a9b0d39f77f4` | **MATCH** · HOLD_UNTIL_MAIN_SUBMIT |
| CMD | `61c3ef3b` | `61c3ef3bdf493ba7d40428a72fbb1a2798946398605f1110e116be7de058ef0a` | **MATCH** · HOLD_UNTIL_MAIN_SUBMIT |
| DIFF | `1c4fb74a` | `1c4fb74a2b3c70f86544905d95fc2a0babadd9add7ec56f984754ef9d46bad4b` | **MATCH**（新文件 vs /dev/null） |
| HAND | `3dd71dc3` | `3dd71dc3e3d0b7f3636e80834bec5dd58f519c2b8f8ca141fcb453c4f5391dc0` | **MATCH** · **DRAFT_READY_FOR_ARCH_HOLD** · **未 SUBMITTED** |
| 脚本（新） | `a40d7069` | `a40d7069374bb940863b8af6e3e103a07aa6c82f10c9cf389f53c76c57edddc0` | **MATCH CHANGED** |
| 构建脚本 | `585ba746` | `585ba7467a5896354c937d14fe0590fa80535afd6b6263015d3c12e3dfccd4ec` | **UNCHANGED** |
| alpha | `652b8a68` | `652b8a68b28871ddc1cbf623834650c23c79c8a81235fabc578ede71f17cf1b1` | **MATCH** |
| meta | `85c2dc78` | `85c2dc7897c2796e36357042d8521e8b4b91beec8f2cd43bf18c31bdf48d4068` | **MATCH** |
| summary | `80596bff` | `80596bffb7de1296f6859f3e7bf1afa5c73ef2ec79a579bb365061cba8579cd6` | **MATCH** |

## 静态自检（本回合）

| 检 | 结果 |
|---|---|
| `--dry-compile-only` | **PASS**：`live:false` `ok_requested:false` `selfcheck_executed:false` `rss_soft_mb:1500` `pin_sha_match:true`；forbid 八票含 `0f50daf7`；**无 evaluate / 无权重实数** |
| `py_compile` → `/tmp/leaf27_x2_selfcheck_v2.pyc` | **PASS** |
| pyflakes（`/tmp/ql_pyflakes_venv`） | **PASS**（exit 0） |
| `pgrep` kline/export_static/snapshot/gen | **PGREP_EMPTY_OK**（未开跑） |
| SELFCHECK_EXECUTED | **false** |
| git commit | **未做** |
| 申 `.ok` / 交 Arch | **未做**（HOLD；等主交审） |
| 改 `585ba746` | **否** |
| Book-Smoke | **否** |

## forbid_restored（明文八票）

`e107383f` / `2be59acd` / `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0` / **`0f50daf7`**

## 状态

- **HOLD_UNTIL_MAIN_SUBMIT**；HAND=**DRAFT_READY_FOR_ARCH_HOLD**（**未**自称 SUBMITTED）
- 等主交审 / 新窗 / 新 `.ok`（脚本钉 `a40d7069`）
- 禁自开跑 / 禁抬帽 / 禁申 `.ok` / 禁申 X2 ACCEPT / 禁 Book-Smoke
- PRIMARY：钉 alpha → eval_weights → `leaf_selfcheck_common.evaluate`
- sampler 前缀钉：`/tmp/quantlab_leaf27_x2_selfcheck_*`
- live=false · ≠X2 · ok_requested=false · **SELFCHECK_EXECUTED=false**
