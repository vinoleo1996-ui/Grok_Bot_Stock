# 叶25 X2 selfcheck_v2 DRAFT 盘证 · 2026-10-26 13:35 ET

| 件 | sha8 | 全长 sha256 | 状态 |
|---|---|---|---|
| PIN | `16706b04` | `16706b04e015a1511ee88d04e11d5627ac7b403ea7f14984d40471d359cacbcc` | **MATCH** · SELFCHECK_EXECUTED=false |
| COVER | `c151d351` | `c151d3514764d680842e7f8f0f721de58a865e8541046cfaae423d88879a3073` | **MATCH** · HOLD_UNTIL_MAIN_SUBMIT |
| CMD | `e2dde42d` | `e2dde42d2def49e62f9575a9154dfa368cee01a211ee1c98ebec7a9070361c3c` | **MATCH** · HOLD_UNTIL_MAIN_SUBMIT |
| DIFF | `eba5b6b2` | `eba5b6b209a0027535e45de15a7487eaf1ee18b01845c1395fe363b8cb20f3b0` | **MATCH**（新文件 vs /dev/null） |
| HAND | `41c9d8a6` | `41c9d8a6d137aa5005cd464ba754441e465e75df0cdc6d4d0a5f569f81564c30` | **MATCH** · **DRAFT_READY_FOR_ARCH_HOLD** · **未 SUBMITTED** |
| 脚本（新） | `b1db0886` | `b1db0886ddcc7e6e9686bbfc0cf0f7d061001eaea157b8ce27152bcc6314b0c3` | **MATCH CHANGED** |
| 构建脚本 | `de7b3647` | `de7b36477908ee522c73e71db64ac904356d7a65c420ea897332925c36427856` | **UNCHANGED** |
| alpha | `8be12024` | `8be12024f57fc85833d99e44f94f5c2916b1aaab64f037eed223f0fc61792393` | **MATCH** |
| meta | `44c27f54` | `44c27f5467420861b2c28a6b0311674c06b69fe8d051fbc256ce31cd7bc7d7e9` | **MATCH** |

## 静态自检（本回合）

| 检 | 结果 |
|---|---|
| `--dry-compile-only` | **PASS**：`live:false` `ok_requested:false` `selfcheck_executed:false` `rss_soft_mb:1500` `rss_hard_mb:1500` `pin_sha_match:true`；forbid 十二票含 `3c297052`；`pin_gap.overall=PARTIAL`；**无 evaluate / 无权重实数** |
| `py_compile` → `/tmp/leaf25_x2_selfcheck_v2.pyc` | **PASS** |
| pyflakes（`/tmp/pyflakes_venv`） | **PASS**（exit 0） |
| `pgrep` kline/export_static/snapshot/gen | **PGREP_EMPTY_OK**（未开跑） |
| SELFCHECK_EXECUTED | **false** |
| 拟 `.ok` 已创建？ | **否**（`output/ai_factory/ARCH_RUN_AUTH_LEAF25_X2_SELFCHECK_V2_HILIQ_X2.ok` 不存在） |
| git commit | **未做** |
| 申 `.ok` / 交 Arch | **未做**（HOLD；等主交审） |
| 改 `de7b3647` | **否** |
| Book-Smoke / RESTORED `3c297052` | **否** |
| PIN_GAP 披露入 COVER/CMD/HAND | **是**（PARTIAL；勿称全残差齐） |

## forbid_restored（明文十二票）

`e107383f` / `2be59acd` / `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0` / `0f50daf7` / `3c19dd7d` / `1c32ab1e` / `6054b3bf` / **`3c297052`**

## 状态

- **HOLD_UNTIL_MAIN_SUBMIT**；HAND=**DRAFT_READY_FOR_ARCH_HOLD**（**未**自称 SUBMITTED）
- 等主交审 / 新窗 / 新 `.ok`（脚本钉 `b1db0886`；拟名 `output/ai_factory/ARCH_RUN_AUTH_LEAF25_X2_SELFCHECK_V2_HILIQ_X2.ok`）
- 禁自开跑 / 禁抬帽 / 禁申 `.ok` / 禁申 X2 ACCEPT / 禁 Book-Smoke
- PRIMARY：钉 alpha → eval_weights → `leaf_selfcheck_common.evaluate`（decay + A/B/current）
- sampler 前缀钉：`/tmp/quantlab_leaf25_x2_selfcheck_*`
- live=false · ≠X2 · ok_requested=false · **SELFCHECK_EXECUTED=false** · PIN_GAP=PARTIAL
