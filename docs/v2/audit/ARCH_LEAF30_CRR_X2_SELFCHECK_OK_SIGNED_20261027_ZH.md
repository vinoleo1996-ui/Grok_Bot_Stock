# Arch 叶30 CRR X2 selfcheck_v1 · 独立 `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T01:44:10-04:00`（America/New_York） |
| 主令 | 主 01:38 ET priority · 叶30 X2 selfcheck 独立签窗 OPEN |
| 审阅 | `3826aa63…` **PASS_WITH_CONDITIONS** |
| CMD P0 | `c25f1321…`（旧 `37ea30a5` **作废**；禁 `--arch-ok-path`） |
| live / promotion_approved | **false** / **false** |

## 结论

**SIGNED** — 独立叶30 CRR X2 selfcheck_v1（PRIMARY：钉既有 R3 peakcut HILIQ×x2 alpha `c8c7a5a5` → eval_weights → `leaf_selfcheck_common.evaluate` → `selfcheck_v1.json`）`.ok` 已落盘；**≠ X2 ACCEPT**；**≠ Book-Smoke**；**≠ 重跑 alpha**；**≠ RESTORED** 十六票（首项 R3 构建 `7e239487`；次项 R2 VOID `5af20222`；三项 leaf30 VOID `5ae077fa`；含叶25构建 `3c297052` / A18 EXEC `6de02e74`）；脚本全长 **`797724d4…` UNCHANGED**；构建 **`3ee9fed2` UNCHANGED**；审 **`3826aa63`**；CMD **`c25f1321`**；COVER **`a6a141ab`**；PIN **`1001ab12`**；DIFF **`8bff7a2a`**；对齐 **`8d515fff`**；SCRIPT_RECEIPT **`297bedcb`**；Arch CONSUME R3 **`20efb33f`**；rss 软/硬帽 **1500** 禁抬 + 硬 ABORT + peak_proof **REQUIRED**；流程门=本 `.ok`+主窗（`--execute` alone 不算授权）；**禁** CLI `--arch-ok-path`；sampler 外挂 `/tmp/quantlab_leaf30_x2_selfcheck_*`；**Arch 不代跑**。QUIET **已挂且保留**供 AI prelaunch（本回合不 lift；≠A18）。PRIMARY only；**无同票 FALLBACK**；峰＞1500→硬 ABORT 停+上报（禁抬帽）。SELFCHECK_EXECUTED@签=**false**。PIN_GAP IC/ICIR/WF **ABSENT_UNTIL_SELFCHECK**。**≠A18**（禁触 `a62881b9`）。

## 钉点 MATCH 表

| 项 | 期望 | 实测 | 结果 |
|---|---|---|---|
| 脚本 | `797724d4…` | `797724d411704ffc8dfe1fcc77039c87ffadda4e6dcd38fb60af60ee8bb27344` | **MATCH** |
| CMD | `c25f1321` | `c25f1321a2c1cc117c4466bc69f7ceebba7f847865603f3519d0cb9b0bdea913` | **MATCH** |
| COVER | `a6a141ab` | `a6a141abf173e7cd7ff19b02cd8e8e44fd41a64a505d8453d35f58b365f02b5a` | **MATCH** |
| PIN | `1001ab12` | `1001ab1229ec505ad629749a89b04813d62809749010f13d4f11bed7856659b5` | **MATCH** |
| SCRIPT_RECEIPT | `297bedcb` | `297bedcbd24746afb21b08613517fd75e5e14bc8717cd381bb4145dd59676d38` | **MATCH** |
| 对齐 | `8d515fff` | `8d515fffa5e149684b766b69ea79f20fa8847537998a142b39effbf817242854` | **MATCH** |
| 审回执 | `3826aa63` PASS_WITH_CONDITIONS | `3826aa632769352b08cd708e1c6dabc86ece81c0095e8531499eb32d0278e07e` | **MATCH** |
| DIFF | `8bff7a2a` | `8bff7a2a4c409bc5ea26dc6d8d65ee7f4632539672ec8a2b8b2b3e70b6567271` | **MATCH** |
| alpha | `c8c7a5a5` | `c8c7a5a5c8df7f2c62d28b340602b6a4c3996d43285f8e78ec3a51e6c42a07a1` | **MATCH** |
| overlap / meta | `f9991d9d` / `a6acfe27` | `f9991d9de4526b3fbe94f5101c68ee09d5c3d996d64a0307cbb4682fb35687cd` / `a6acfe274481f19bbd643a91acb68cacd3c81456b2d7c649db2e7db8175fea5a` | **MATCH** |
| 构建脚本 | `3ee9fed2` UNCHANGED | `3ee9fed2c91a8c523128d9a0b0956f29a11fd2935d961e978aa07b9eafb0a182` | **MATCH** |
| Arch CONSUME R3 | `20efb33f` | `20efb33f660c92088d4e558fb5ff0e3e4a49b6fc9565aacf838b72ebe6e1db6d` | **MATCH** |
| 拟 .ok 签前 | ABSENT | ABSENT | **MATCH** |
| QUIET 签前 | ABSENT | ABSENT | **MATCH** |
| live leaf30 `.ok` | 0 | 0 | **MATCH** |
| `_selfcheck/` / `selfcheck_v1.json` | ABSENT | ABSENT → EXECUTED=false | **MATCH** |
| CMD 拟 CLI | 无 `--arch-ok-path`；`… --universe HILIQ --window x2 --execute` | 同左 | **MATCH** |
| pgrep leaf30 | 空 | 空 | **MATCH** |
| 窗期 | ≥90min | `2026-10-27T01:44:00-04:00` → `2026-10-27T03:14:00-04:00` / expires `2026-10-27T03:16:00-04:00`；签时 `2026-10-27T01:44:10-04:00` | **IN_WINDOW** |

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF30_CRR_X2_SELFCHECK_V1_HILIQ_X2.ok` |
| `.ok` sha8 / 全长 | `aa25e989` / `aa25e989cf31e0810a0b485c7db7f7e0272cd2e8af9093bf3722e2c9b0b304ea` |
| QUIET 路径 | `output/loop/RESEARCH_QUIET.lock` |
| QUIET sha8 / 全长 | `0eb56fe2` / `0eb56fe2ac7247a0324e678c19913a6be8d42a6ce87810304457795a65c1cac9` |
| QUIET holder | `leaf30_CRR_X2_SELFCHECK_V1`（含 leaf30_selfcheck；≠A18） |
| 脚本 | `research/leaf30_crr_x2_selfcheck_v1.py` = `797724d411704ffc8dfe1fcc77039c87ffadda4e6dcd38fb60af60ee8bb27344` |
| 构建脚本 UNCHANGED | `research/leaf30_crr_cfooe_volpen_alpha_build_r3_peakcut.py` = `3ee9fed2c91a8c523128d9a0b0956f29a11fd2935d961e978aa07b9eafb0a182` |
| 审阅 | `3826aa632769352b08cd708e1c6dabc86ece81c0095e8531499eb32d0278e07e` PASS_WITH_CONDITIONS |
| CMD / COVER / PIN | `c25f1321a2c1cc117c4466bc69f7ceebba7f847865603f3519d0cb9b0bdea913` / `a6a141abf173e7cd7ff19b02cd8e8e44fd41a64a505d8453d35f58b365f02b5a` / `1001ab1229ec505ad629749a89b04813d62809749010f13d4f11bed7856659b5` |
| DIFF / 对齐 / SCRIPT_RECEIPT | `8bff7a2a4c409bc5ea26dc6d8d65ee7f4632539672ec8a2b8b2b3e70b6567271` / `8d515fffa5e149684b766b69ea79f20fa8847537998a142b39effbf817242854` / `297bedcbd24746afb21b08613517fd75e5e14bc8717cd381bb4145dd59676d38` |
| CONSUME R3 | `20efb33f660c92088d4e558fb5ff0e3e4a49b6fc9565aacf838b72ebe6e1db6d` |
| alpha / overlap / meta | `c8c7a5a5c8df7f2c62d28b340602b6a4c3996d43285f8e78ec3a51e6c42a07a1` / `f9991d9de4526b3fbe94f5101c68ee09d5c3d996d64a0307cbb4682fb35687cd` / `a6acfe274481f19bbd643a91acb68cacd3c81456b2d7c649db2e7db8175fea5a` |
| 窗期 | `2026-10-27T01:44:00-04:00` → `2026-10-27T03:14:00-04:00`；expires `2026-10-27T03:16:00-04:00` |
| CLI PRIMARY | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf30_crr_x2_selfcheck_v1.py --universe HILIQ --window x2 --execute` |
| CLI 可选显式钉盘 | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf30_crr_x2_selfcheck_v1.py --universe HILIQ --window x2 --alpha-path output/ai_factory/_leaf30_crr/20261027_003132/alpha_HILIQ_x2_20261027_010815.parquet --meta-path output/ai_factory/_leaf30_crr/20261027_003132/run_meta.json --execute` |
| FALLBACK | **无**；峰＞1500 / 失败 → 硬 ABORT 停+上报（禁抬帽） |
| rss 软/硬 | **1500** / **1500** MB；forbid_raise_rss；hard_abort_on_rss=true |
| PIN_GAP | IC/ICIR/WF **ABSENT_UNTIL_SELFCHECK** |
| 采样 | 仅 `/tmp/quantlab_leaf30_x2_selfcheck_*` |
| 产物 | `_selfcheck/` + `leaf_reports/leaf30_crr/selfcheck_v1.json`（禁覆写钉盘 alpha/meta/overlap） |
| 禁 RESTORED | 十六票：`7e239487,5af20222,5ae077fa,3c297052,e107383f,2be59acd,a7d98ac9,8e51de63,3a6caa4f,8bcd79dc,725be3e0,0f50daf7,3c19dd7d,1c32ab1e,6054b3bf,6de02e74` |
| Book-Smoke / X2 ACCEPT / 重跑 alpha | **false** / **false** / **false** |
| peak_proof | **REQUIRED** |
| MemAvailable@签 | 12399292 kB |
| ≠A18 | ban_touch_a18_ok_a62881b9=true；未触 |
| 旧 CMD | `37ea30a5` **作废** |

## CONDITIONS（签文硬钉）

1. approved_cmd 仅 `… --universe HILIQ --window x2 --execute`（可选显式 alpha/meta path）；**禁** `--arch-ok-path`
2. 流程门=本 `.ok`+主窗；`--execute` alone 不算授权
3. forbid∋`7e239487`+`5af20222`+`5ae077fa`（十六票齐）
4. rss=1500 禁抬 + 硬 ABORT + peak_proof REQUIRED
5. 钉 alpha `c8c7a5a5`；≠重跑 alpha；≠Book-Smoke；≠X2 ACCEPT
6. sampler 外挂 `/tmp/quantlab_leaf30_x2_selfcheck_*`；Arch 不代跑

## QUIET / pgrep

| 项 | 值 |
|---|---|
| QUIET 挂时 | `2026-10-27T01:44:10-04:00` reason=leaf30_crr_x2_selfcheck_v1 holder=`leaf30_CRR_X2_SELFCHECK_V1` |
| do_not_lift_until_arch_or_consumed | **true**（本拍不 lift） |
| neq_a18 | **true**（未触 `_lifted` 旧 A18 QUIET） |
| pgrep leaf30 / kline/… | 空 |
| SELFCHECK_EXECUTED@签 | **false**（无 `_selfcheck/`、无 `selfcheck_v1.json`） |

## 下一跳

1. **主** MATCH `.ok`+`QUIET`+本回执后令 AI prelaunch→execute（须在 expires 前；Arch **不代跑**）
2. AI 交实峰回执（权重 sha + selfcheck_v1.json sha + peak rss + **PIN_GAP IC/ICIR/WF ABSENT_UNTIL_SELFCHECK 复述**；峰＞1500→硬 ABORT 停）→ Arch 核 CONSUME
3. ≠X2 ACCEPT；≠Book-Smoke；不解阻全量 X2；≠A18；不 RESTORED `7e239487`/`5af20222`/`5ae077fa`；live=false；**不报 Leo**

live=false。
