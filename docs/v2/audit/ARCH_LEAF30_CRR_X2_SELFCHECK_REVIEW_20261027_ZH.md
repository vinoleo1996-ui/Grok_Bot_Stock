# Arch 审阅：叶30 CRR X2 selfcheck_v1 独立票（只审不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-27T01:33:36-04:00`（America/New_York；墙钟 `2026-10-27 01:33 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 `.ok`；**不挂 QUIET**；**不代跑**任何 evaluate/`--execute`；不改脚本/主干；不抬 rss；**不解阻 X2**；禁当 X2 ACCEPT；≠Book-Smoke；live=false；promotion=false；**不推 Leo**；不触 A18 |
| 触发 | 主 01:29 ET 交审（TEAM_STATE 顶条旁）+ 本拍执行令；包钉以主令表为准 |
| 对照 | 脚本 `797724d4` · COVER `fdec5e1a` · PIN `993d26e2` · CMD `37ea30a5` · DIFF `8bff7a2a` · 落盘回执 `268f9dfa` · alpha `c8c7a5a5` · overlap `f9991d9d` · meta `a6acfe27` · 构建 UNCHANGED `3ee9fed2` · Arch CONSUME `20efb33f` · Alpha 闸 `1c992d62` · AI RUN `88a08738` |

## 0. 一句话

包钉全件 **MATCH**；PRIMARY = 钉既有 R3 peakcut HILIQ×x2 alpha（`c8c7a5a5`）→ §3.3 `build_eval_weights` → `leaf_selfcheck_common.evaluate` 写 `selfcheck_v1.json`；**≠** 复跑 alpha / **≠** Book-Smoke / **≠** X2 ACCEPT。新脚本 `797724d4` 不覆写钉盘 alpha/meta/overlap，不碰构建 `3ee9fed2`；产物隔离 `_selfcheck/` + `leaf_reports/leaf30_crr/selfcheck_v1.json`。**SELFCHECK_EXECUTED=false** 盘证成立。rss 软/硬 **1500** + `check_rss_hard` **硬 ABORT** + peak_proof。forbid **十六**票含 R3 构建票 **`7e239487`** 与 R1/R2 VOID **`5ae077fa`/`5af20222`**。Alpha 闸 **`1c992d62` ACCEPT（仅构建过程）**；IC/ICIR/WF **ABSENT_UNTIL_SELFCHECK**（PIN_GAP）。开放 CONDITIONS：CMD 拟 CLI 含脚本**未实现**的 `--arch-ok-path`；DIFF 为 leaf25→leaf30 派生 delta（非 `/dev/null`→新文件，但 patch 可还原 ≡ 脚本）；`--execute` alone 不校验 live `.ok`。**本回合不签 `.ok`**；请主另排独立签窗。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| 脚本（新 CHANGED） | `research/leaf30_crr_x2_selfcheck_v1.py` | `797724d4` | `797724d411704ffc8dfe1fcc77039c87ffadda4e6dcd38fb60af60ee8bb27344` | **MATCH** |
| COVER | `docs/v2/audit/AI_LEAF30_CRR_X2_SELFCHECK_COVER_DRAFT_20261027_ZH.md` | `fdec5e1a` | `fdec5e1a79e034f47000e9e05a4c2fb5f40b40500272892f2ba81eaf979224e2` | **MATCH** · DRAFT ONLY |
| PIN | `docs/v2/audit/AI_LEAF30_CRR_X2_SELFCHECK_V1_PIN_RECEIPT_20261027_ZH.md` | `993d26e2` | `993d26e20868251488e86278ffef5b2b9d89a7d07a7a2b4181786859a0f8cb44` | **MATCH** · SELFCHECK_EXECUTED=false |
| CMD | `docs/v2/audit/AI_LEAF30_CRR_X2_SELFCHECK_CMD_DRAFT_20261027_ZH.md` | `37ea30a5` | `37ea30a5fa8a7f98ce42e4beea3833e8f02e5aa27eba8e9810cbfc3ea58973e7` | **MATCH** · 现不可跑 |
| DIFF | `docs/v2/audit/AI_LEAF30_CRR_X2_SELFCHECK_DIFF_DRAFT_20261027.diff` | `8bff7a2a` | `8bff7a2a4c409bc5ea26dc6d8d65ee7f4632539672ec8a2b8b2b3e70b6567271` | **MATCH** · leaf25→leaf30 派生 |
| 落盘回执 | `docs/v2/audit/AI_LEAF30_CRR_X2_SELFCHECK_SCRIPT_RECEIPT_20261027_ZH.md` | `268f9dfa` | `268f9dfa2a52032988cdbe6df20d773066bbb679ffad873e83f5cb62429a252b` | **MATCH** |
| alpha | `output/ai_factory/_leaf30_crr/20261027_003132/alpha_HILIQ_x2_20261027_010815.parquet` | `c8c7a5a5` | `c8c7a5a5c8df7f2c62d28b340602b6a4c3996d43285f8e78ec3a51e6c42a07a1` | **MATCH** |
| overlap | `…/overlap_vs_leaf19_25.json` | `f9991d9d` | `f9991d9de4526b3fbe94f5101c68ee09d5c3d996d64a0307cbb4682fb35687cd` | **MATCH** |
| meta | `…/run_meta.json` | `a6acfe27` | `a6acfe274481f19bbd643a91acb68cacd3c81456b2d7c649db2e7db8175fea5a` | **MATCH** |
| 构建脚本 | `research/leaf30_crr_cfooe_volpen_alpha_build_r3_peakcut.py` | `3ee9fed2` | `3ee9fed2c91a8c523128d9a0b0956f29a11fd2935d961e978aa07b9eafb0a182` | **MATCH UNCHANGED** |
| Arch CONSUMED | `docs/v2/audit/ARCH_LEAF30_CRR_ALPHA_BUILD_R3_PEAKCUT_CONSUMED_PASS_20261027_ZH.md` | `20efb33f` | `20efb33f660c92088d4e558fb5ff0e3e4a49b6fc9565aacf838b72ebe6e1db6d` | **MATCH** |
| Alpha 闸 | `docs/v2/ALPHA_LEAF30_CRR_R3_ALPHA_GATE_REVIEW_20261027_ZH.md` | `1c992d62` | `1c992d62c63ffd4560ad2ee0f738602f70e047741fc4f0cde9140953c3015f3d` | **MATCH** · ACCEPT 仅构建过程 |

live `.ok`（`output/ai_factory` 顶层）=**0**；拟 `.ok` `output/ai_factory/ARCH_RUN_AUTH_LEAF30_CRR_X2_SELFCHECK_V1_HILIQ_X2.ok` **未创建**；`output/loop` **无** live QUIET 锁（R3 QUIET 已 lift `1420c412` / 原 `69ea8560`）；本审**未挂** QUIET；`_selfcheck/` **ABSENT**；`leaf_reports/leaf30_crr/` **ABSENT**；`selfcheck_v1.json` **ABSENT**；`eval_weights*` **ABSENT** → **SELFCHECK_EXECUTED=false** 成立。

## 2. CMD / COVER / 脚本核验

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| 1 | PRIMARY：钉 alpha → 权重 → selfcheck_v1 | **PASS** | 脚本：`assert_pins` 全长钉 alpha+meta+overlap → `build_eval_weights` → `_selfcheck/eval_weights_*.parquet` → `LC.evaluate(wp)` → `leaf_reports/leaf30_crr/selfcheck_v1.json`；**非**重算 alpha |
| 2 | ≠ 复跑 alpha / Book-Smoke / X2 ACCEPT | **PASS** | docstring/COVER/CMD/dry meta：`book_smoke:false` `x2_accept:false` `alpha_build_consumed_not_x2_accept:true`；构建脚本禁改 |
| 3 | SELFCHECK_EXECUTED=false | **PASS** | PIN/COVER/CMD/回执明文 false；盘上无权重/报告；本审**未代跑** evaluate/`--execute`（采信 AI dry-compile PASS，禁复跑） |
| 4 | CONSUMED/Alpha ACCEPT 不解阻 X2 | **PASS** | Arch `20efb33f` / Alpha `1c992d62` 分层 ACCEPT 仅构建；本票独立脚本；禁 RESTORED `7e239487` |
| 5 | forbid **十六**票含 `7e239487`+`5af20222`+`5ae077fa` | **PASS** | 脚本 `FORBID_RESTORED` n=16 齐：`7e239487`/`5af20222`/`5ae077fa`/`3c297052`/`e107383f`/`2be59acd`/`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`/`0f50daf7`/`3c19dd7d`/`1c32ab1e`/`6054b3bf`/`6de02e74` |
| 6 | rss 软/硬 1500 + 硬 ABORT + peak_proof | **PASS** | `RSS_SOFT_MB=RSS_HARD_MB=1500`；`check_rss_hard` 破则 `SystemExit`；`peak_proof_required=true`；`forbid_raise_rss:true` |
| 7 | 不改写 alpha / 不碰 `3ee9fed2` | **PASS** | 写路径仅 `_selfcheck/*` + `selfcheck_v1.json` + side_meta；`assert_pins` 校验构建 sha 前缀 `3ee9fed2`；实测仍 MATCH |
| 8 | 输出路径隔离 | **PASS** | `SELFCHECK_SUB=…/20261027_003132/_selfcheck`；报告 `leaf_reports/leaf30_crr/selfcheck_v1.json`；不覆写钉盘 run_meta/alpha/overlap |
| 9 | DIFF vs 脚本 | **PASS_WITH_CONDITIONS** | DIFF **非** `/dev/null`→新文件；头注 derived from leaf25；形态=叶25 `b1db0886`→叶30。本机 `patch` 施加于 leaf25 副本 → 字节 ≡ 脚本（sha8 **`797724d4`**）。「去头 + ≡ 脚本」严格判据不适用本形态；签前可补 `/dev/null` DIFF，或以脚本全长为权威 |
| 10 | PRIMARY CLI（仅文档对照；现禁跑） | **PASS_WITH_CONDITIONS** | dry：`--universe HILIQ --window x2 --dry-compile-only` 与脚本一致。拟 execute CMD 含 **`--arch-ok-path …`**，脚本 argparse **无此旗标**（`--help` 仅 universe/window/alpha-path/meta-path/dry-compile-only/execute）→ 按 CMD 原样跑会 argparse 失败。签前须：**改 CMD 去掉该旗**（对齐叶25：流程门由 `.ok`+主窗外挂），或补脚本旗标+存在性校验 |
| 11 | `--execute` 门 / 无 .ok 运行时检查 | **PASS_WITH_CONDITIONS** | 缺 `--execute` → exit 2；`--execute` alone 仍 `live:false` 但**不**校验 live `.ok` → 流程门（新 `.ok`+主窗）必须签文硬钉 |
| 12 | 权重规则 §3.3 | **PASS** | NAME_W=0.04 · MAX_NAMES=20 · REBAL_EVERY=5 · IND_CAP(HILIQ)=0.25 · BALLAST=510300.SH · HARD_EXCLUDE={600519.SH,002371.SZ}；无单独 gate 列；SW L1 asof |
| 13 | PIN_GAP / Alpha 闸披露 | **PASS** | `PIN_GAP_OVERALL=ABSENT_UNTIL_SELFCHECK`；gap=ic/icir/walk_forward；Alpha `1c992d62` ACCEPT_BUILD_PROCESS_ONLY；`claim_x2_accept=false`；COVER/PIN/脚本齐 |
| 14 | overlap 只读消费 | **PASS** | `assert_pins` 校验 `PIN_OVERLAP` 全长 `f9991d9d…`；执行路径不改写 overlap |
| 15 | 拟 `.ok` 仅预留 / live=0 / QUIET ABSENT | **PASS** | 拟名未创建；顶层 live `.ok`=0；loop 无 QUIET；本审未挂未签 |
| 16 | sampler | **PASS_WITH_CONDITIONS** | 脚本钉 `SAMPLER_PREFIX=/tmp/quantlab_leaf30_x2_selfcheck_`；**未内建** sampler → 若启用须签文/prelaunch 外挂；禁其它前缀 |
| 17 | 内存峰值风险 | **PASS_WITH_CONDITIONS** | alpha≈974711 行；`evaluate` 按名装 panel + capacity_adv 叠层 → 峰可能贴/破 1500；硬 ABORT 会停；静态审 ≠ 峰证明；peak_proof REQUIRED；MemAvailable 听主软地板 |
| 18 | 静态自检（AI 宣称；本审未复跑） | **PASS**（采信回执） | SCRIPT_RECEIPT：dry-compile PASS / py_compile→/tmp PASS；本审遵「禁代跑」未复跑 evaluate / 未 `--execute` |

## 3. 硬钉对齐

### 3.1 PRIMARY 语义

本票正确切分：**消费** R3 peakcut 已落盘 alpha（`c8c7a5a5` / meta `a6acfe27` / overlap `f9991d9d`；Arch CONSUME `20efb33f`；AI RUN `88a08738`；peak_kb=917820≪1500），生成评价权重并跑 selfcheck_v1；**不是**再建 alpha，**不是** Book-Smoke，**不是** X2 ACCEPT。CONSUMED_PASS / Alpha ACCEPT（仅构建）**不解阻**本票开跑，更**不解阻 X2**。

### 3.2 PIN_GAP / Alpha 闸（签文必披露）

| 字段 | 状态 |
|---|---|
| IC / ICIR / walk-forward | **ABSENT_UNTIL_SELFCHECK**（Alpha 闸 `1c992d62` 标明 ABSENT） |
| Alpha 闸 VERDICT | **ACCEPT（仅研究级 α 构建过程）**；≠收益过程过闸；≠组合门裁定 |
| claim_x2_accept | **false** |
| 禁称 | X2 ACCEPT / IC 已过闸 / 升纸面 |

回执与签文须复述本表；selfcheck 数字即使「过闸」亦不自动构成 X2/ACCEPT。

### 3.3 残余风险（须写入签条件）

1. **evaluate 装载面**：panel + capacity_adv 叠层；硬 ABORT 会停，仍须 peak_proof；MemAvailable 听主软地板；建议短窗错开其它研究实跑。
2. **CMD `--arch-ok-path` 漂移**：脚本无此参数；签前改 CMD 或补实现；禁按现 CMD 字面开跑。
3. **`--execute` 无 `.ok` 校验**：禁在无新 `.ok`/窗外执行；流程门由主+Arch 执守。
4. **DIFF 形态**：派生 delta 可还原脚本；权威以脚本全长 `797724d4…` 为准；可选补 `/dev/null` DIFF。
5. **`selfcheck_v1.json` 固定路径**：重跑会覆写报告；权重/side_meta 带 stamp；回执须交权重 sha + 报告 sha + peak + PIN_GAP 复述。
6. **≠X2 ACCEPT**；禁 RESTORED `7e239487`/`5af20222`/`5ae077fa`（及 forbid 全集）。

## 4. 条件（另回合签发前必须满足）

1. **主排新签窗**（建议短窗；错开其它研究实跑；MemAvailable 听主软地板；无叠加 QUIET 冲突）——**本回合不签**。
2. 新 `.ok` 硬钉：
   - script sha `797724d411704ffc8dfe1fcc77039c87ffadda4e6dcd38fb60af60ee8bb27344`（sha8 **`797724d4`**）
   - CLI PRIMARY 须与**可跑**脚本对齐。建议（对齐叶25，去掉无效旗标）：
     `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf30_crr_x2_selfcheck_v1.py --universe HILIQ --window x2 --execute`
     （alpha/meta 默认即钉盘；可选显式 `--alpha-path`/`--meta-path`）。**禁止**原 CMD 字面 `--arch-ok-path`（脚本不认），除非签前 AI 补旗标+校验并重钉脚本 sha。
   - 钉三件：alpha `c8c7a5a5…` / meta `a6acfe27…` / overlap `f9991d9d…`
   - 构建 **UNCHANGED** `3ee9fed2`；Arch CONSUME `20efb33f`；Alpha 闸 `1c992d62`（ACCEPT 仅构建；IC/ICIR/WF ABSENT_UNTIL_SELFCHECK）
   - `rss_soft_mb=1500` · `rss_hard_mb=1500` · `forbid_raise_rss=true`；破硬帽脚本 ABORT；禁抬帽
   - `forbid_restored_ok_sha8`：**十六票**含 **`7e239487`** / **`5af20222`** / **`5ae077fa`** + `3c297052`/`e107383f`/`2be59acd`/`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`/`0f50daf7`/`3c19dd7d`/`1c32ab1e`/`6054b3bf`/`6de02e74`
   - sampler（若启用）：`/tmp/quantlab_leaf30_x2_selfcheck_*` only
   - 权重目录：`…/_leaf30_crr/20261027_003132/_selfcheck/`；报告：`…/leaf_reports/leaf30_crr/selfcheck_v1.json`
   - **PIN_GAP** 明文：IC/ICIR/WF ABSENT_UNTIL_SELFCHECK；Alpha ACCEPT 仅构建；≠X2 ACCEPT
   - COVER/CMD/PIN/DIFF/回执/本审 全长钉入签文（若改 CMD/脚本须重审重钉）
   - live=false · promotion=false · book_smoke=false · **x2_accept=false** · **alpha_build_consumed_not_x2_accept=true**
3. 签时挂短窗 QUIET；AI **单次** prelaunch（healthz / wait≥15s / pgrep 空 / 脚本 sha MATCH / dry-compile 复核）后 `--execute`；交回执（权重 sha + selfcheck_v1.json sha + peak rss + **PIN_GAP 复述**）；AI 勿擅 lift / 勿自重跑 / 勿抬帽。
4. **peak_proof REQUIRED**（至少：`rss_mb_peak_self` / `peak_proof.ru_maxrss_mb`；若挂 sampler 则 sampler 峰）。
5. **≠X2 ACCEPT**；不解阻全量 X2；本审不构成自动开跑授权。
6. 禁 RESTORED 任一 VOID/CONSUMED（尤其 **`7e239487`** / **`5af20222`** / **`5ae077fa`**）。

## 5. 禁项（本回合 + 签后）

- **本回合不签** `.ok`；不挂 QUIET；不代跑 evaluate/`--execute`；不排签窗（等主）；不抬帽
- 禁复用/RESTORED：forbid 十六票（含 **`7e239487`/`5af20222`/`5ae077fa`**）
- 禁抬 rss；禁 Book-Smoke；禁当 X2 ACCEPT；禁复跑 alpha 构建
- 禁改 `research/leaf30_crr_cfooe_volpen_alpha_build_r3_peakcut.py`（`3ee9fed2`）；禁动已 CONSUMED 归档 `.ok`
- 禁把 CONSUMED_PASS / Alpha ACCEPT（构建）当本票授权；禁称 IC 已过闸
- 禁静默 fallback / 禁换 universe/window / 禁换 alpha 路径
- 禁按现 CMD 字面带 `--arch-ok-path` 开跑（除非脚本已补齐并重钉）

## 6. 建议签窗 / 拟 `.ok` 名（勿本回合创建）

- **勿本回合签**（主令硬钉只审不签）。
- 建议：主确认 CONDITIONS（尤其 CMD 旗标对齐）后排下一空窗；签时 QUIET；与其它 leaf 实跑错开。
- 拟名：`output/ai_factory/ARCH_RUN_AUTH_LEAF30_CRR_X2_SELFCHECK_V1_HILIQ_X2.ok`；**新签**，禁 RESTORED 十六票任一内容（尤其 **`7e239487`**）。

## 7. 本回合非动作声明

- **未签**任何 `.ok`
- **未挂** QUIET
- **未代跑** evaluate / `--execute`（未复跑 dry-compile；`--help` 只读核 argparse）
- **未改**主干代码 / 构建脚本 / 钉盘 alpha/meta/overlap
- **未动**叶30 R3 已 CONSUMED 归档 `.ok`（`7e239487`）
- **不解阻 X2**；**不当 X2 ACCEPT**
- live=false · promotion=false · **不推 Leo**

## 8. 结论

**PASS_WITH_CONDITIONS** — 包钉全 MATCH；PRIMARY 语义正确；SELFCHECK_EXECUTED=false 成立；forbid 十六票齐（含 `7e239487`/`5af20222`/`5ae077fa`）；rss 硬 ABORT+peak_proof；PIN_GAP/Alpha 闸已披露；输出隔离；构建 `3ee9fed2` UNCHANGED。开放项见 §4（新窗+新 `.ok`、**CMD `--arch-ok-path` 对齐**、DIFF 形态说明、流程门、peak_proof、禁 RESTORED/禁 X2 ACCEPT）。**可请主另排独立签窗**；本回合不签。

审阅文 sha8（正文，不含本段）：`c20a1781c6cf81c9188d160eb89b1f7fca3fdb3eb3c435547b189535f8ec8608` · sha8 **`c20a1781`**

> 全文件 `sha256sum` 以落盘后实测为准（见 Arch→主回执）；正文钉用于追溯。
