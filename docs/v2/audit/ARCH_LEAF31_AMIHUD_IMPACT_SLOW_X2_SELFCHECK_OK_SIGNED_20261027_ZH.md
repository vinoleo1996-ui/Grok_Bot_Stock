# Arch 叶31 Amihud Impact Slow X2 selfcheck_v1 · 独立 `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T03:17:52-04:00`（America/New_York） |
| 主令 | 主 03:10 ET priority · 叶31 X2 selfcheck 独立签窗 OPEN · 立即 SIGN |
| 审阅 | `0db69426…` **PASS_WITH_CONDITIONS** |
| CMD | `25c16a2b…`（禁 `--arch-ok-path`；流程门=新 `.ok`+主窗） |
| live / promotion_approved | **false** / **false** |

## 结论

**SIGNED** — 独立叶31 Amihud Impact Slow X2 selfcheck_v1（PRIMARY：钉既有 HILIQ×x2 alpha `d4ceb78b` → eval_weights → `leaf_selfcheck_common.evaluate` → `selfcheck_v1.json`）`.ok` 已落盘；**≠ X2 ACCEPT**；**≠ Book-Smoke**；**≠ 重跑 alpha**；**≠ RESTORED** 十八票（首项叶31 X2 构建 CONSUMED `fdbaa512`；次项叶30 selfcheck `aa25e989`；三项 R3 `7e239487`；四/五项 R2/R1 VOID `5af20222`/`5ae077fa`；及审文全集）；脚本全长 **`e1fe578c…` MATCH**；构建 **`08f37fd2` UNCHANGED**；模板 **`797724d4` UNCHANGED**；审 **`0db69426`**；COVER **`96b704e1`**；CMD **`25c16a2b`**；DIFF **`3880d0ad`**；SCRIPT_RECEIPT **`00060e44`**；Arch CONSUME **`7bd6f33a`**；Alpha 闸 **`a476567d`**（ACCEPT 仅构建）；rss 软/硬帽 **1500** 禁抬 + 硬 ABORT + peak_proof **REQUIRED**；流程门=本 `.ok`+主窗（`--execute` alone 不算授权）；**禁** CLI `--arch-ok-path`；sampler 外挂 `/tmp/quantlab_leaf31_x2_selfcheck_*`；**Arch 不代跑**。QUIET **已挂且保留**供 AI prelaunch（本回合不 lift；≠A18）。PRIMARY only；**无同票 FALLBACK**；峰＞1500→硬 ABORT 停+上报（禁抬帽）。SELFCHECK_EXECUTED@签=**false**。PIN_GAP IC/ICIR/WF **ABSENT_UNTIL_SELFCHECK**。**≠A18**。`0087c928` **另队不夹带**。**不报 Leo**。

## 钉点 MATCH 表

| 项 | 期望 | 实测 | 结果 |
|---|---|---|---|
| 脚本 | `e1fe578c…` | `e1fe578ca70bd61f6c98bd849357beecb918f9e88f0732ac6bbc98dcfb0d4b38` | **MATCH** |
| CMD | `25c16a2b` | `25c16a2bceac23448d6b93a08e09fb61cb0f0fde4581bce9263a4f8a67097dd7` | **MATCH** |
| COVER | `96b704e1` | `96b704e13cdf6e829315f78686dbf2b2908c7536c924eda2f1270e2f8c2e4dbf` | **MATCH** |
| SCRIPT_RECEIPT | `00060e44` | `00060e441f9a6086dd8657356dc1ca0c97ec650a6930809d79b8c25e6492b38f` | **MATCH** |
| 审回执 | `0db69426` PASS_WITH_CONDITIONS | `0db6942680ecf7dd6b654b70a61d010cc91ce0a058aa194ce0816b781918a8ea` | **MATCH** |
| DIFF | `3880d0ad` | `3880d0ad1913ad94349751ab4f96e43ad691ac3827035db71671b66a649d89a3` | **MATCH** |
| alpha | `d4ceb78b` | `d4ceb78b1d4b7c5516149a74bad87141083695ac6c4b7be43e3fa9a64c4452ce` | **MATCH** |
| overlap / meta | `8396f211` / `696ab1cc` | `8396f2111411dd0f9040d0215369394e83e646adca2dac15072b1003289df75b` / `696ab1cc25eed077cf7171b4461e8e6946677901c3fbfaf68be5cd55c4d9ab12` | **MATCH** |
| 构建脚本 | `08f37fd2` UNCHANGED | `08f37fd2deb15f6a2a4e6bc7bc16e07d16fc50c70b807e0e1ae617627f98bde0` | **MATCH** |
| 模板叶30 selfcheck | `797724d4` UNCHANGED | `797724d411704ffc8dfe1fcc77039c87ffadda4e6dcd38fb60af60ee8bb27344` | **MATCH** |
| Arch CONSUME | `7bd6f33a` | `7bd6f33ae302f15cf3b3803497ee20e8bba0f31beab1b3b8c6ee8be0d5284e66` | **MATCH** |
| Alpha 闸 | `a476567d` | `a476567d537629f182e7c0da656a059f59708a2c1c1575b854600884a93153c0` | **MATCH** |
| 拟 .ok 签前 | ABSENT | ABSENT | **MATCH** |
| QUIET 签前 | ABSENT | ABSENT | **MATCH** |
| live leaf31 `.ok` | 0 | 0 | **MATCH** |
| `_selfcheck/` / `selfcheck_v1.json` | ABSENT | ABSENT → EXECUTED=false | **MATCH** |
| CMD 拟 CLI | 无 `--arch-ok-path`；`… --universe HILIQ --window x2 --execute` | 同左 | **MATCH** |
| forbid 碰撞 | 新 `.ok` sha8 ∉ 十八票 | `4bb141c9` ∉ forbid | **PASS** |
| pgrep leaf31 selfcheck | 空 | 空 | **MATCH** |
| 窗期 | ≥90min | `2026-10-27T03:17:00-04:00` → `2026-10-27T04:47:00-04:00` / expires `2026-10-27T04:49:00-04:00`；签时 `2026-10-27T03:17:52-04:00` | **IN_WINDOW** |

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF31_AMIHUD_IMPACT_SLOW_X2_SELFCHECK_V1_HILIQ_X2.ok` |
| `.ok` sha8 / 全长 | `4bb141c9` / `4bb141c90ca3e934dd04645f8656f9a06455e1c6d3167688b0988c7c440b5d58` |
| QUIET 路径 | `output/loop/RESEARCH_QUIET.lock` |
| QUIET sha8 / 全长 | `351e98fb` / `351e98fbcd53e0144914744f97ad44eee2a4e392b62f466d78bbd58bf7ed3e87` |
| QUIET holder | `leaf31_AMIHUD_IMPACT_SLOW_X2_SELFCHECK_V1`（含 leaf31_selfcheck；≠A18） |
| 脚本 | `research/leaf31_amihud_impact_slow_x2_selfcheck_v1.py` = `e1fe578ca70bd61f6c98bd849357beecb918f9e88f0732ac6bbc98dcfb0d4b38` |
| 构建脚本 UNCHANGED | `research/leaf31_amihud_impact_slow_alpha_build.py` = `08f37fd2deb15f6a2a4e6bc7bc16e07d16fc50c70b807e0e1ae617627f98bde0` |
| 模板 UNCHANGED | `research/leaf30_crr_x2_selfcheck_v1.py` = `797724d411704ffc8dfe1fcc77039c87ffadda4e6dcd38fb60af60ee8bb27344` |
| 审阅 | `0db6942680ecf7dd6b654b70a61d010cc91ce0a058aa194ce0816b781918a8ea` PASS_WITH_CONDITIONS |
| CMD / COVER / DIFF / RECEIPT | `25c16a2bceac23448d6b93a08e09fb61cb0f0fde4581bce9263a4f8a67097dd7` / `96b704e13cdf6e829315f78686dbf2b2908c7536c924eda2f1270e2f8c2e4dbf` / `3880d0ad1913ad94349751ab4f96e43ad691ac3827035db71671b66a649d89a3` / `00060e441f9a6086dd8657356dc1ca0c97ec650a6930809d79b8c25e6492b38f` |
| CONSUME / Alpha 闸 | `7bd6f33ae302f15cf3b3803497ee20e8bba0f31beab1b3b8c6ee8be0d5284e66` / `a476567d537629f182e7c0da656a059f59708a2c1c1575b854600884a93153c0` |
| alpha / overlap / meta | `d4ceb78b1d4b7c5516149a74bad87141083695ac6c4b7be43e3fa9a64c4452ce` / `8396f2111411dd0f9040d0215369394e83e646adca2dac15072b1003289df75b` / `696ab1cc25eed077cf7171b4461e8e6946677901c3fbfaf68be5cd55c4d9ab12` |
| 窗期 | `2026-10-27T03:17:00-04:00` → `2026-10-27T04:47:00-04:00`；expires `2026-10-27T04:49:00-04:00` |
| CLI PRIMARY | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf31_amihud_impact_slow_x2_selfcheck_v1.py --universe HILIQ --window x2 --execute` |
| CLI 可选显式钉盘 | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf31_amihud_impact_slow_x2_selfcheck_v1.py --universe HILIQ --window x2 --alpha-path output/ai_factory/_leaf31_amihud/20261027_024204/alpha_HILIQ_x2_20261027_024422.parquet --meta-path output/ai_factory/_leaf31_amihud/20261027_024204/run_meta.json --execute` |
| FALLBACK | **无**；峰＞1500 / 失败 → 硬 ABORT 停+上报（禁抬帽） |
| rss 软/硬 | **1500** / **1500** MB；forbid_raise_rss；hard_abort_on_rss=true |
| PIN_GAP | IC/ICIR/WF **ABSENT_UNTIL_SELFCHECK** |
| 采样 | 仅 `/tmp/quantlab_leaf31_x2_selfcheck_*` |
| 产物 | `_selfcheck/` + `leaf_reports/leaf31_amihud/selfcheck_v1.json`（禁覆写钉盘 alpha/meta/overlap） |
| 禁 RESTORED | 十八票：`fdbaa512,aa25e989,7e239487,5af20222,5ae077fa,3c297052,e107383f,2be59acd,a7d98ac9,8e51de63,3a6caa4f,8bcd79dc,725be3e0,0f50daf7,3c19dd7d,1c32ab1e,6054b3bf,6de02e74` |
| Book-Smoke / X2 ACCEPT / 重跑 alpha | **false** / **false** / **false** |
| peak_proof | **REQUIRED** |
| MemAvailable@签 | 13060016 kB |
| ≠A18 | ban_touch_a18_ok_a62881b9=true；未触 |
| `0087c928` | 另队；**不在**本 `.ok` |

## CONDITIONS（签文硬钉）

1. approved_cmd 仅 `… --universe HILIQ --window x2 --execute`（可选显式 alpha/meta path）；**禁** `--arch-ok-path`
2. 流程门=本 `.ok`+主窗；`--execute` alone 不算授权
3. forbid∋`fdbaa512`+`aa25e989`+`7e239487`+`5af20222`+`5ae077fa`（十八票齐）
4. rss=1500 禁抬 + 硬 ABORT + peak_proof REQUIRED
5. 钉 alpha `d4ceb78b`；≠重跑 alpha；≠Book-Smoke；≠X2 ACCEPT
6. sampler 外挂 `/tmp/quantlab_leaf31_x2_selfcheck_*`；Arch 不代跑
7. `0087c928` 另队不夹带；≠A18

## QUIET / pgrep

| 项 | 值 |
|---|---|
| QUIET 挂时 | `2026-10-27T03:17:52-04:00` reason=leaf31_amihud_impact_slow_x2_selfcheck_v1 holder=`leaf31_AMIHUD_IMPACT_SLOW_X2_SELFCHECK_V1` |
| do_not_lift_until_arch_or_consumed | **true**（本拍不 lift） |
| neq_a18 | **true**（未触 `_lifted` 旧 A18 QUIET） |
| pgrep leaf31 selfcheck / kline/… | 空 |
| SELFCHECK_EXECUTED@签 | **false**（无 `_selfcheck/`、无 `selfcheck_v1.json`） |

## 下一跳

1. **主** MATCH `.ok`+`QUIET`+本回执后令 AI prelaunch→execute（须在 expires 前；Arch **不代跑**）
2. AI 交实峰回执（权重 sha + selfcheck_v1.json sha + peak rss + **PIN_GAP IC/ICIR/WF ABSENT_UNTIL_SELFCHECK 复述**；峰＞1500→硬 ABORT 停）→ Arch 核 CONSUME
3. ≠X2 ACCEPT；≠Book-Smoke；不解阻全量 X2；≠A18；不 RESTORED `fdbaa512`/`aa25e989`/`7e239487`/`5af20222`/`5ae077fa`；`0087c928` 另队；live=false；**不报 Leo**

live=false。
