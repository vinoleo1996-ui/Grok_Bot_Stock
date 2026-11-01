# Arch 审阅：叶31 Amihud Impact Slow X2 selfcheck_v1 独立票（只审不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-27T03:06:07-04:00`（America/New_York；墙钟 `2026-10-27 03:06 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 `.ok`；**不挂 QUIET**；**不代跑**任何 evaluate/`--execute`；不改脚本/主干；不抬 rss；**不解阻 X2**；禁当 X2 ACCEPT；≠Book-Smoke；live=false；promotion=false；**不推 Leo**；不触 A18；**不审** `0087c928` |
| 触发 | 主 03:01 ET 交审（TEAM_STATE 顶条）+ 本拍执行令；包钉以主令表为准 |
| 对照 | 脚本 `e1fe578c` · COVER `96b704e1` · CMD `25c16a2b` · DIFF `3880d0ad` · 落盘回执 `00060e44` · alpha `d4ceb78b` · overlap `8396f211` · meta `696ab1cc` · 构建 UNCHANGED `08f37fd2` · 模板 UNCHANGED `797724d4` · Arch CONSUME `7bd6f33a` · Alpha 闸 `a476567d` · AI RUN `49d6641c` |

## 0. 一句话

包钉全件 **MATCH**；PRIMARY = 钉既有叶31 Amihud Impact Slow HILIQ×x2 alpha（`d4ceb78b`）→ §3.3 `build_eval_weights` → `leaf_selfcheck_common.evaluate` 写 `selfcheck_v1.json`；**≠** 复跑 alpha / **≠** Book-Smoke / **≠** X2 ACCEPT。新脚本 `e1fe578c` 不覆写钉盘 alpha/meta/overlap，不碰构建 `08f37fd2`；产物隔离 `_selfcheck/` + `leaf_reports/leaf31_amihud/selfcheck_v1.json`。**SELFCHECK_EXECUTED=false** 盘证成立。rss 软/硬 **1500** + `check_rss_hard` **硬 ABORT** + peak_proof。forbid **十八**票含构建 CONSUMED **`fdbaa512`**、叶30 selfcheck **`aa25e989`**、R3 **`7e239487`** 与 R1/R2 VOID **`5ae077fa`/`5af20222`**。Alpha 闸 **`a476567d` ACCEPT（仅构建过程）**；IC/ICIR/WF **ABSENT_UNTIL_SELFCHECK**（PIN_GAP）。CMD **已去掉**未实现 `--arch-ok-path`（对齐叶25/30 P0）。开放 CONDITIONS：DIFF 为 leaf30→leaf31 派生 delta（非 `/dev/null`→新文件，但 patch 可还原 ≡ 脚本）；`--execute` alone 不校验 live `.ok`；alpha≈158 万行 → 峰可能贴/破 1500（硬 ABORT+peak_proof）。**本回合不签 `.ok`**；请主另排独立签窗。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| 脚本（新 CHANGED） | `research/leaf31_amihud_impact_slow_x2_selfcheck_v1.py` | `e1fe578c` | `e1fe578ca70bd61f6c98bd849357beecb918f9e88f0732ac6bbc98dcfb0d4b38` | **MATCH** |
| COVER | `docs/v2/audit/AI_LEAF31_AMIHUD_IMPACT_SLOW_X2_SELFCHECK_COVER_DRAFT_20261027_ZH.md` | `96b704e1` | `96b704e13cdf6e829315f78686dbf2b2908c7536c924eda2f1270e2f8c2e4dbf` | **MATCH** · DRAFT ONLY |
| CMD | `docs/v2/audit/AI_LEAF31_AMIHUD_IMPACT_SLOW_X2_SELFCHECK_CMD_DRAFT_20261027_ZH.md` | `25c16a2b` | `25c16a2bceac23448d6b93a08e09fb61cb0f0fde4581bce9263a4f8a67097dd7` | **MATCH** · 现不可跑；**禁** `--arch-ok-path` |
| DIFF | `docs/v2/audit/AI_LEAF31_AMIHUD_IMPACT_SLOW_X2_SELFCHECK_DIFF_DRAFT_20261027.diff` | `3880d0ad` | `3880d0ad1913ad94349751ab4f96e43ad691ac3827035db71671b66a649d89a3` | **MATCH** · leaf30→leaf31 派生 |
| 落盘回执 | `docs/v2/audit/AI_LEAF31_AMIHUD_IMPACT_SLOW_X2_SELFCHECK_SCRIPT_RECEIPT_20261027_ZH.md` | `00060e44` | `00060e441f9a6086dd8657356dc1ca0c97ec650a6930809d79b8c25e6492b38f` | **MATCH** · dry-compile PASS（采信；本审未复跑） |
| alpha | `output/ai_factory/_leaf31_amihud/20261027_024204/alpha_HILIQ_x2_20261027_024422.parquet` | `d4ceb78b` | `d4ceb78b1d4b7c5516149a74bad87141083695ac6c4b7be43e3fa9a64c4452ce` | **MATCH** |
| overlap | `…/overlap_vs_leaf19_25_27_30.json` | `8396f211` | `8396f2111411dd0f9040d0215369394e83e646adca2dac15072b1003289df75b` | **MATCH** |
| meta | `…/run_meta.json` | `696ab1cc` | `696ab1cc25eed077cf7171b4461e8e6946677901c3fbfaf68be5cd55c4d9ab12` | **MATCH** · x2_end=`2026-10-09`；mechanism=`g1g5_ashare_amihud_impact_slow_v1` |
| 构建脚本 | `research/leaf31_amihud_impact_slow_alpha_build.py` | `08f37fd2` | `08f37fd2deb15f6a2a4e6bc7bc16e07d16fc50c70b807e0e1ae617627f98bde0` | **MATCH UNCHANGED** |
| 模板（只读） | `research/leaf30_crr_x2_selfcheck_v1.py` | `797724d4` | `797724d411704ffc8dfe1fcc77039c87ffadda4e6dcd38fb60af60ee8bb27344` | **MATCH UNCHANGED** |
| Arch CONSUMED | `docs/v2/audit/ARCH_LEAF31_AMIHUD_IMPACT_SLOW_X2_CONSUMED_PASS_20261027_ZH.md` | `7bd6f33a` | `7bd6f33ae302f15cf3b3803497ee20e8bba0f31beab1b3b8c6ee8be0d5284e66` | **MATCH** |
| Alpha 闸 | `docs/v2/ALPHA_LEAF31_AMIHUD_X2_ALPHA_GATE_REVIEW_20261027_ZH.md` | `a476567d` | `a476567d537629f182e7c0da656a059f59708a2c1c1575b854600884a93153c0` | **MATCH** · ACCEPT 仅构建过程 |

live `.ok`（`output/ai_factory` 顶层）=**0**；拟 `.ok` `output/ai_factory/ARCH_RUN_AUTH_LEAF31_AMIHUD_IMPACT_SLOW_X2_SELFCHECK_V1_HILIQ_X2.ok` **未创建**；`output/loop` **无** live QUIET 锁（叶31 X2 QUIET 已 lift → `_lifted/RESEARCH_QUIET_leaf31_amihud_impact_slow_x2_PASS_LIFTED_20261027T0249ET.lock`）；本审**未挂** QUIET；`_selfcheck/` **ABSENT**；`leaf_reports/leaf31_amihud/` **ABSENT**；`selfcheck_v1.json` **ABSENT**；`eval_weights*` **ABSENT** → **SELFCHECK_EXECUTED=false** 成立。

## 2. CMD / COVER / 脚本核验

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| 1 | PRIMARY：钉 alpha → 权重 → selfcheck_v1 | **PASS** | 脚本：`assert_pins` 全长钉 alpha+meta+overlap → `build_eval_weights` → `_selfcheck/eval_weights_*.parquet` → `LC.evaluate(wp)` → `leaf_reports/leaf31_amihud/selfcheck_v1.json`；**非**重算 alpha |
| 2 | ≠ 复跑 alpha / Book-Smoke / X2 ACCEPT | **PASS** | docstring/COVER/CMD/dry meta：`book_smoke:false` `x2_accept:false` `alpha_build_consumed_not_x2_accept:true`；构建脚本禁改 |
| 3 | SELFCHECK_EXECUTED=false | **PASS** | COVER/CMD/回执明文 false；盘上无权重/报告；本审**未代跑** evaluate/`--execute`（采信 AI dry-compile/py_compile PASS，禁复跑） |
| 4 | CONSUMED/Alpha ACCEPT 不解阻 X2 | **PASS** | Arch `7bd6f33a` / Alpha `a476567d` 分层 ACCEPT 仅构建；本票独立脚本；禁 RESTORED `fdbaa512` |
| 5 | forbid **十八**票含 `fdbaa512`+`aa25e989`+`7e239487`+`5af20222`+`5ae077fa` | **PASS** | 脚本 `FORBID_RESTORED` n=18 齐：`fdbaa512`/`aa25e989`/`7e239487`/`5af20222`/`5ae077fa`/`3c297052`/`e107383f`/`2be59acd`/`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`/`0f50daf7`/`3c19dd7d`/`1c32ab1e`/`6054b3bf`/`6de02e74`（相对叶30 十六票新增 `fdbaa512`+`aa25e989`） |
| 6 | rss 软/硬 1500 + 硬 ABORT + peak_proof | **PASS** | `RSS_SOFT_MB=RSS_HARD_MB=1500`；`check_rss_hard` 破则 `SystemExit`；`peak_proof_required=true`；`forbid_raise_rss:true`；dry 钉 `x2_end=20261009` |
| 7 | 不改写 alpha / 不碰 `08f37fd2` | **PASS** | 写路径仅 `_selfcheck/*` + `selfcheck_v1.json` + side_meta；`assert_pins` 校验构建 sha 前缀 `08f37fd2`；实测仍 MATCH |
| 8 | 输出路径隔离 | **PASS** | `SELFCHECK_SUB=…/20261027_024204/_selfcheck`；报告 `leaf_reports/leaf31_amihud/selfcheck_v1.json`；不覆写钉盘 run_meta/alpha/overlap |
| 9 | DIFF vs 脚本 | **PASS_WITH_CONDITIONS** | DIFF **非** `/dev/null`→新文件；头注 derived from leaf30 `797724d4`；形态=叶30→叶31。本机 `patch -p0` 施加于 leaf30 副本 → 字节 ≡ 脚本（sha8 **`e1fe578c`**）。「去头 + ≡ 脚本」严格判据不适用本形态；签前可补 `/dev/null` DIFF，或以脚本全长为权威 |
| 10 | PRIMARY CLI（仅文档对照；现禁跑） | **PASS** | dry：`--universe HILIQ --window x2 --dry-compile-only` 与脚本一致。拟 execute：`--universe HILIQ --window x2 --execute`；CMD **明文禁** `--arch-ok-path`（脚本 argparse **无此旗标**；仅注释/披露）→ **无叶30 式 CMD 漂移**；流程门由 `.ok`+主窗外挂 |
| 11 | `--execute` 门 / 无 .ok 运行时检查 | **PASS_WITH_CONDITIONS** | 缺 `--execute` → exit 2；`--execute` alone 仍 `live:false` 但**不**校验 live `.ok` → 流程门（新 `.ok`+主窗）必须签文硬钉 |
| 12 | 权重规则 §3.3 | **PASS** | NAME_W=0.04 · MAX_NAMES=20 · REBAL_EVERY=5 · IND_CAP(HILIQ)=0.25 · BALLAST=510300.SH · HARD_EXCLUDE={600519.SH,002371.SZ}；无单独 gate 列；SW L1 asof；与叶30 模板 **同构**（仅路径/钉/mechanism/forbid 扩展差异） |
| 13 | PIN_GAP / Alpha 闸披露 | **PASS** | `PIN_GAP_OVERALL=ABSENT_UNTIL_SELFCHECK`；gap=ic/icir/walk_forward；Alpha `a476567d` ACCEPT_BUILD_PROCESS_ONLY；`claim_x2_accept=false`；COVER/回执/脚本齐；`0087c928` 另队声明 |
| 14 | overlap 只读消费 | **PASS** | `assert_pins` 校验 `PIN_OVERLAP` 全长 `8396f211…`；执行路径不改写 overlap |
| 15 | 拟 `.ok` 仅预留 / live=0 / QUIET ABSENT | **PASS** | 拟名未创建；顶层 live `.ok`=0；loop 无 QUIET；本审未挂未签 |
| 16 | sampler | **PASS_WITH_CONDITIONS** | 脚本钉 `SAMPLER_PREFIX=/tmp/quantlab_leaf31_x2_selfcheck_`；**未内建** sampler → 若启用须签文/prelaunch 外挂；禁其它前缀 |
| 17 | 内存峰值风险 | **PASS_WITH_CONDITIONS** | alpha≈**1579217** 行（大于叶30≈97 万）；`evaluate` 按名装 panel + capacity_adv 叠层 → 峰可能贴/破 1500；硬 ABORT 会停；静态审 ≠ 峰证明；peak_proof REQUIRED；MemAvailable 听主软地板 |
| 18 | 静态自检（AI 宣称；本审未复跑） | **PASS**（采信回执） | SCRIPT_RECEIPT：dry-compile PASS / py_compile→`/tmp/leaf31_selfcheck.pyc` PASS；本审遵「禁代跑」未复跑 dry-compile / evaluate / 未 `--execute` |

## 3. 硬钉对齐

### 3.1 PRIMARY 语义

本票正确切分：**消费**叶31 已落盘 alpha（`d4ceb78b` / meta `696ab1cc` / overlap `8396f211`；Arch CONSUME `7bd6f33a`；AI RUN `49d6641c`；peak_kb=847092≪1500），生成评价权重并跑 selfcheck_v1；**不是**再建 alpha，**不是** Book-Smoke，**不是** X2 ACCEPT。CONSUMED_PASS / Alpha ACCEPT（仅构建）**不解阻**本票开跑，更**不解阻 X2**。

### 3.2 PIN_GAP / Alpha 闸（签文必披露）

| 字段 | 状态 |
|---|---|
| IC / ICIR / walk-forward | **ABSENT_UNTIL_SELFCHECK**（Alpha 闸 `a476567d` 标明 ABSENT） |
| Alpha 闸 VERDICT | **ACCEPT（仅研究级 α 构建过程）**；≠收益过程过闸；≠组合门裁定 |
| claim_x2_accept | **false** |
| 禁称 | X2 ACCEPT / IC 已过闸 / 升纸面 |
| 另队 | `0087c928`（叶30 KEEP）**不夹带**；本审未读未审 |

回执与签文须复述本表；selfcheck 数字即使「过闸」亦不自动构成 X2/ACCEPT。

### 3.3 残余风险（须写入签条件）

1. **evaluate 装载面**：alpha≈158 万行；panel + capacity_adv 叠层；硬 ABORT 会停，仍须 peak_proof；MemAvailable 听主软地板；建议短窗错开其它研究实跑。
2. **`--execute` 无 `.ok` 校验**：禁在无新 `.ok`/窗外执行；流程门由主+Arch 执守（CMD 已正确禁 `--arch-ok-path`）。
3. **DIFF 形态**：派生 delta 可还原脚本；权威以脚本全长 `e1fe578c…` 为准；可选补 `/dev/null` DIFF。
4. **`selfcheck_v1.json` 固定路径**：重跑会覆写报告；权重/side_meta 带 stamp；回执须交权重 sha + 报告 sha + peak + PIN_GAP 复述。
5. **≠X2 ACCEPT**；禁 RESTORED `fdbaa512`/`aa25e989`/`7e239487`/`5af20222`/`5ae077fa`（及 forbid 全集十八票）。
6. **禁触 A18**；**不审** `0087c928`。

## 4. 条件（另回合签发前必须满足）

1. **主排新签窗**（建议短窗；错开其它研究实跑；MemAvailable 听主软地板；无叠加 QUIET 冲突）——**本回合不签**。
2. 新 `.ok` 硬钉：
   - script sha `e1fe578ca70bd61f6c98bd849357beecb918f9e88f0732ac6bbc98dcfb0d4b38`（sha8 **`e1fe578c`**）
   - CLI PRIMARY（对齐 CMD；**禁** `--arch-ok-path`）：
     `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf31_amihud_impact_slow_x2_selfcheck_v1.py --universe HILIQ --window x2 --execute`
     （alpha/meta 默认即钉盘；可选显式 `--alpha-path`/`--meta-path`）。
   - 钉三件：alpha `d4ceb78b…` / meta `696ab1cc…` / overlap `8396f211…`
   - 构建 **UNCHANGED** `08f37fd2`；模板 `797724d4` UNCHANGED；Arch CONSUME `7bd6f33a`；Alpha 闸 `a476567d`（ACCEPT 仅构建；IC/ICIR/WF ABSENT_UNTIL_SELFCHECK）
   - `rss_soft_mb=1500` · `rss_hard_mb=1500` · `forbid_raise_rss=true`；破硬帽脚本 ABORT；禁抬帽
   - `forbid_restored_ok_sha8`：**十八票**含 **`fdbaa512`** / **`aa25e989`** / **`7e239487`** / **`5af20222`** / **`5ae077fa`** + `3c297052`/`e107383f`/`2be59acd`/`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`/`0f50daf7`/`3c19dd7d`/`1c32ab1e`/`6054b3bf`/`6de02e74`
   - sampler（若启用）：`/tmp/quantlab_leaf31_x2_selfcheck_*` only
   - 权重目录：`…/_leaf31_amihud/20261027_024204/_selfcheck/`；报告：`…/leaf_reports/leaf31_amihud/selfcheck_v1.json`
   - **PIN_GAP** 明文：IC/ICIR/WF ABSENT_UNTIL_SELFCHECK；Alpha ACCEPT 仅构建；≠X2 ACCEPT
   - COVER/CMD/DIFF/回执/本审 全长钉入签文（若改 CMD/脚本须重审重钉）
   - live=false · promotion=false · book_smoke=false · **x2_accept=false** · **alpha_build_consumed_not_x2_accept=true**
   - `0087c928` 另队不夹带；禁触 A18
3. 签时挂短窗 QUIET；AI **单次** prelaunch（healthz / wait≥15s / pgrep 空 / 脚本 sha MATCH / dry-compile 复核）后 `--execute`；交回执（权重 sha + selfcheck_v1.json sha + peak rss + **PIN_GAP 复述**）；AI 勿擅 lift / 勿自重跑 / 勿抬帽。
4. **peak_proof REQUIRED**（至少：`rss_mb_peak_self` / `peak_proof.ru_maxrss_mb`；若挂 sampler 则 sampler 峰）。
5. **≠X2 ACCEPT**；不解阻全量 X2；本审不构成自动开跑授权。
6. 禁 RESTORED 任一 VOID/CONSUMED（尤其 **`fdbaa512`** / **`aa25e989`** / **`7e239487`** / **`5af20222`** / **`5ae077fa`**）。

## 5. 禁项（本回合 + 签后）

- **本回合不签** `.ok`；不挂 QUIET；不代跑 evaluate/`--execute`；不排签窗（等主）；不抬帽
- 禁复用/RESTORED：forbid 十八票（含 **`fdbaa512`/`aa25e989`/`7e239487`/`5af20222`/`5ae077fa`**）
- 禁抬 rss；禁 Book-Smoke；禁当 X2 ACCEPT；禁复跑 alpha 构建
- 禁改 `research/leaf31_amihud_impact_slow_alpha_build.py`（`08f37fd2`）；禁改模板 `797724d4`；禁动已 CONSUMED 归档 `.ok`
- 禁把 CONSUMED_PASS / Alpha ACCEPT（构建）当本票授权；禁称 IC 已过闸
- 禁静默 fallback / 禁换 universe/window / 禁换 alpha 路径
- 禁带 `--arch-ok-path` 开跑（脚本不认；CMD 已禁）
- 禁审/夹带 `0087c928`；禁触 A18；**不报 Leo**

## 6. 建议签窗 / 拟 `.ok` 名（勿本回合创建）

- **勿本回合签**（主令硬钉只审不签）。
- 建议：主确认 CONDITIONS（尤其 `--execute` 流程门 + peak_proof）后排下一空窗；签时 QUIET；与其它 leaf 实跑错开。
- 拟名：`output/ai_factory/ARCH_RUN_AUTH_LEAF31_AMIHUD_IMPACT_SLOW_X2_SELFCHECK_V1_HILIQ_X2.ok`；**新签**，禁 RESTORED 十八票任一内容（尤其 **`fdbaa512`**）。

## 7. 本回合非动作声明

- **未签**任何 `.ok`
- **未挂** QUIET
- **未代跑** evaluate / `--execute`（未复跑 dry-compile）
- **未改**主干代码 / 构建脚本 / 模板 / 钉盘 alpha/meta/overlap
- **未动**叶31 X2 已 CONSUMED 归档 `.ok`（`fdbaa512`）；**未审** `0087c928`
- **不解阻 X2**；**不当 X2 ACCEPT**；**未触 A18**
- live=false · promotion=false · **不推 Leo**

## 8. 结论

**PASS_WITH_CONDITIONS** — 包钉全 MATCH；PRIMARY 语义正确；SELFCHECK_EXECUTED=false 成立；forbid 十八票齐（含 `fdbaa512`/`aa25e989`/`7e239487`/`5af20222`/`5ae077fa`）；rss 硬 ABORT+peak_proof；PIN_GAP/Alpha 闸已披露；输出隔离；构建 `08f37fd2` / 模板 `797724d4` UNCHANGED；CMD 已禁 `--arch-ok-path`（无漂移）。开放项见 §4（新窗+新 `.ok`、DIFF 形态说明、`--execute` 流程门、peak_proof/内存峰、禁 RESTORED/禁 X2 ACCEPT）。**可请主另排独立签窗**；本回合不签。

审阅文 sha8（正文，不含本段）：`8184f5b0815099f96d3b2069ce75d1996ccf7b70c1a599be26b4d0912e8b1d09` · sha8 **`8184f5b0`**

> 全文件 `sha256sum` 以落盘后实测为准（见 Arch→主回执）；正文钉用于追溯。
