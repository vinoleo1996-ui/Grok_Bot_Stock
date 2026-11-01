# Arch 审阅：叶32 Margin Net Flow Resid X2 selfcheck_v1 独立票（只审不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-27T05:09:43-04:00`（America/New_York；墙钟 `2026-10-27 05:09 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 `.ok`；**不挂 QUIET**；**不代跑**任何 evaluate/`--execute`；不改脚本/主干；不抬 rss；**不解阻 X2**；禁当 X2 ACCEPT；≠Book-Smoke；live=false；promotion=false；**不推 Leo**；不触 A18；**不审** `0087c928` |
| 触发 | 主 05:05 ET 交审（TEAM_STATE 顶条）+ 本拍执行令；包钉以主令表为准 |
| 对照 | 脚本 `dcf6b559` · COVER `e901405b` · CMD `754bf251` · DIFF `3f98d664` · 落盘回执 `30af740d` · alpha `13eee6fd` · overlap `a643d71a` · meta `e510f346` · 构建 UNCHANGED `4e0f3c00` · 模板 UNCHANGED `e1fe578c` · Arch CONSUME `a1a5e35a` · Alpha 闸 `1aa432a5` · FROZEN `6b8de5e9` · AI RUN `f3e8f991` |

## 0. 一句话

包钉全件 **MATCH**；PRIMARY = 钉既有叶32 Margin Net Flow Resid HILIQ×x2 alpha（`13eee6fd`）→ §3.3 `build_eval_weights` → `leaf_selfcheck_common.evaluate` 写 `selfcheck_v1.json`；**≠** 复跑 alpha / **≠** Book-Smoke / **≠** X2 ACCEPT。新脚本 `dcf6b559` 不覆写钉盘 alpha/meta/overlap，不碰构建 `4e0f3c00`；产物隔离 `_selfcheck/` + `leaf_reports/leaf32_margin_flow/selfcheck_v1.json`。**SELFCHECK_EXECUTED=false** 盘证成立。rss 软/硬 **1500** + `check_rss_hard` **硬 ABORT** + peak_proof。forbid **二十**票含构建 CONSUMED **`02426b73`**、叶31 selfcheck **`4bb141c9`**、叶31 build **`fdbaa512`**、叶30 selfcheck **`aa25e989`**、R3 **`7e239487`** 与 R1/R2 VOID **`5ae077fa`/`5af20222`**（七票齐）。Alpha 闸 **`1aa432a5` ACCEPT（仅构建过程）**；IC/ICIR/WF **ABSENT_UNTIL_SELFCHECK**（PIN_GAP）。CMD/argparse **已去掉**未实现 `--arch-ok-path`（对齐叶25/30/31 P0）。decay KEEP 三闸经 `LC.evaluate`→`alpha_decay_gate`（KEEP/DOWNGRADE）+ portfolio gates A/B/current 同构钉死；`0087c928` 仅另队披露、不夹带执行。开放 CONDITIONS：DIFF 为 leaf31→leaf32 派生 delta（非 `/dev/null`→新文件，但 patch 可还原 ≡ 脚本）；`--execute` alone 不校验 live `.ok`；alpha≈123 万行 → 峰可能贴/破 1500（硬 ABORT+peak_proof）。**本回合不签 `.ok`**；请主另排独立签窗。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| 脚本（新 CHANGED） | `research/leaf32_margin_net_flow_resid_x2_selfcheck_v1.py` | `dcf6b559` | `dcf6b559165e43dcaa56df8adc3cb5d9574b6b55cc5ba20cf39d97b0285cda4f` | **MATCH** |
| COVER | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_X2_SELFCHECK_COVER_DRAFT_20261027_ZH.md` | `e901405b` | `e901405bb1015c7f1ade9704211e1e1a2a55214f7381827c12f22966aac626c8` | **MATCH** · DRAFT ONLY |
| CMD | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_X2_SELFCHECK_CMD_DRAFT_20261027_ZH.md` | `754bf251` | `754bf25123c680faaac38e185363d08a0a9e78fd50dde642b02272d8d41c62c9` | **MATCH** · 现不可跑；**禁** `--arch-ok-path` |
| DIFF | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_X2_SELFCHECK_DIFF_DRAFT_20261027.diff` | `3f98d664` | `3f98d66413a05f05cc5d2692fd91d043334b0c4c2c226118bd1a6392f218a0f9` | **MATCH** · leaf31→leaf32 派生 |
| 落盘回执 | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_X2_SELFCHECK_SCRIPT_RECEIPT_20261027_ZH.md` | `30af740d` | `30af740dd89275b6eae2fdd0d8214394179fa44c668e20dac056281927d9ee50` | **MATCH** · dry-compile PASS（采信）；本审复跑 `py_compile` **PASS** |
| alpha | `output/ai_factory/_leaf32_margin_flow/20261027_042805/alpha_HILIQ_x2_20261027_044214.parquet` | `13eee6fd` | `13eee6fdf0922b14756cf22985964dcd177810772a2ee4ec3bdb7c1668646ed2` | **MATCH** |
| overlap | `…/overlap_vs_leaf19_25_27_30_31_margin_delta.json` | `a643d71a` | `a643d71ad77e3ae06eab2dc1fb20a0b99bf3d572db9310821b00ba8627bfe5fe` | **MATCH** |
| meta | `…/run_meta.json` | `e510f346` | `e510f346bed46e6ca64f802de3aaed5f28f469f0a2fbf68ee2d5f2fffc4f6610` | **MATCH** · x2_end=`2026-10-09`；mechanism_tag=`g1g5_ashare_margin_net_flow_resid_v1` |
| 构建脚本 | `research/leaf32_margin_net_flow_resid_alpha_build.py` | `4e0f3c00` | `4e0f3c002057393c031598e0379c6622afe8ca4a18579c9ab3b9f3d7ba4ae187` | **MATCH UNCHANGED** |
| 模板（只读） | `research/leaf31_amihud_impact_slow_x2_selfcheck_v1.py` | `e1fe578c` | `e1fe578ca70bd61f6c98bd849357beecb918f9e88f0732ac6bbc98dcfb0d4b38` | **MATCH UNCHANGED** |
| Arch CONSUMED | `docs/v2/audit/ARCH_LEAF32_MARGIN_NET_FLOW_RESID_X2_CONSUMED_PASS_20261027_ZH.md` | `a1a5e35a` | `a1a5e35af07e297577aef47311e2f79c6c2f04ecdef3a5dd60fb7518a0b3f31e` | **MATCH** |
| Alpha 闸 | `docs/v2/ALPHA_LEAF32_MARGIN_NET_FLOW_RESID_X2_ALPHA_GATE_REVIEW_20261027_ZH.md` | `1aa432a5` | `1aa432a5c0529122c13f8ef05a42ac37921bf3a3c738e7ffe6778eb896c0d885` | **MATCH** · ACCEPT 仅构建过程 |
| FROZEN | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_PREREG_FROZEN_20261027_ZH.md` | `6b8de5e9` | `6b8de5e9d4a4cc6caecbe344bfc4b6ce4da0f9e983f87c7c7b73759e0f893f42` | **MATCH** |

live `.ok`（`output/ai_factory` 顶层）=**0**；拟 `.ok` `output/ai_factory/ARCH_RUN_AUTH_LEAF32_MARGIN_NET_FLOW_RESID_X2_SELFCHECK_V1_HILIQ_X2.ok` **未创建**；`output/loop/RESEARCH_QUIET.lock` **ABSENT**；本审**未挂** QUIET；`_selfcheck/` **ABSENT**；`leaf_reports/leaf32_margin_flow/` **ABSENT**；`selfcheck_v1.json` **ABSENT**；`eval_weights*` **ABSENT** → **SELFCHECK_EXECUTED=false** 成立。

## 2. CMD / COVER / 脚本核验

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| 1 | PRIMARY：钉 alpha → 权重 → selfcheck_v1 | **PASS** | 脚本：`assert_pins` 全长钉 alpha+meta+overlap → `build_eval_weights` → `_selfcheck/eval_weights_*.parquet` → `LC.evaluate(wp)` → `leaf_reports/leaf32_margin_flow/selfcheck_v1.json`；**非**重算 alpha |
| 2 | ≠ 复跑 alpha / Book-Smoke / X2 ACCEPT | **PASS** | docstring/COVER/CMD/dry meta：`book_smoke:false` `x2_accept:false` `alpha_build_consumed_not_x2_accept:true`；构建脚本禁改 |
| 3 | SELFCHECK_EXECUTED=false | **PASS** | COVER/CMD/回执明文 false；盘上无权重/报告；本审**未代跑** evaluate/`--execute`；本审仅 `python3 -m py_compile` **PASS** |
| 4 | CONSUMED/Alpha ACCEPT 不解阻 X2 | **PASS** | Arch `a1a5e35a` / Alpha `1aa432a5` 分层 ACCEPT 仅构建；本票独立脚本；禁 RESTORED `02426b73` |
| 5 | forbid **七票**齐（全集二十） | **PASS** | 脚本 `FORBID_RESTORED` n=20 齐七票：`02426b73`/`4bb141c9`/`fdbaa512`/`aa25e989`/`7e239487`/`5af20222`/`5ae077fa` + 既有十三票（`3c297052`…`6de02e74`） |
| 6 | rss 软/硬 1500 + 硬 ABORT + peak_proof | **PASS** | `RSS_SOFT_MB=RSS_HARD_MB=1500`；`check_rss_hard` 破则 `SystemExit`；`PEAK_PROOF_REQUIRED=True`；`forbid_raise_rss:true`；dry 钉 `x2_end=20261009` |
| 7 | 不改写 alpha / 不碰 `4e0f3c00` | **PASS** | 写路径仅 `_selfcheck/*` + `selfcheck_v1.json` + side_meta；`assert_pins` 校验构建 sha 前缀 `4e0f3c00`；实测仍 MATCH |
| 8 | 输出路径隔离 | **PASS** | `SELFCHECK_SUB=…/20261027_042805/_selfcheck`；报告 `leaf_reports/leaf32_margin_flow/selfcheck_v1.json`；不覆写钉盘 run_meta/alpha/overlap |
| 9 | DIFF vs 脚本 | **PASS_WITH_CONDITIONS** | DIFF **非** `/dev/null`→新文件；头注 derived from leaf31 `e1fe578c`；形态=叶31→叶32。本机 `patch -p0` 施加于 leaf31 副本 → 字节 ≡ 脚本（sha8 **`dcf6b559`**）。权威以脚本全长为准；签前可补 `/dev/null` DIFF |
| 10 | PRIMARY CLI（仅文档对照；现禁跑） | **PASS** | dry：`--universe HILIQ --window x2 --dry-compile-only` 与脚本一致。拟 execute：`--universe HILIQ --window x2 --execute`；CMD **明文禁** `--arch-ok-path`；脚本 argparse **无此旗标**（仅注释/披露）→ **无 CMD 漂移**；流程门由 `.ok`+主窗外挂 |
| 11 | `--execute` 门 / 无 .ok 运行时检查 | **PASS_WITH_CONDITIONS** | 缺 `--execute` → exit 2；`--execute` alone 仍 `live:false` 但**不**校验 live `.ok` → 流程门（新 `.ok`+主窗）必须签文硬钉 |
| 12 | 权重规则 §3.3 | **PASS** | NAME_W=0.04 · MAX_NAMES=20 · REBAL_EVERY=5 · IND_CAP(HILIQ)=0.25 · BALLAST=510300.SH · HARD_EXCLUDE={600519.SH,002371.SZ}；无单独 gate 列；SW L1 asof；与叶31 模板 **同构**（仅路径/钉/mechanism/forbid 扩展差异） |
| 13 | PIN_GAP / Alpha 闸披露 | **PASS** | `PIN_GAP_OVERALL=ABSENT_UNTIL_SELFCHECK`；gap=ic/icir/walk_forward；Alpha `1aa432a5` ACCEPT_BUILD_PROCESS_ONLY；`claim_x2_accept=false`；COVER/回执/脚本齐；`0087c928` 另队声明 |
| 14 | decay KEEP 三闸 + gates A/B/current | **PASS** | 脚本 gate_policy → `LC.evaluate`；`leaf_selfcheck_common`：`decay=ADG.evaluate_weights`（`KEEP`/`DECAY_DOWNGRADE`/`DECAY_WATCH`；三闸：latest_resid_alpha / 5Q decline / H2_net_cagr>510300）+ `portfolio_gates.verdict`={current,A,B}；披露与叶31 同构并加盯 decay KEEP |
| 15 | `0087c928` 不夹带 | **PASS** | 仅 `LEAF30_KEEP_REPAIR_SHA8_SEPARATE` 披露；无 open/read/Path 执行；本审未读未审该票 |
| 16 | overlap 只读消费 | **PASS** | `assert_pins` 校验 `PIN_OVERLAP` 全长 `a643d71a…`；执行路径不改写 overlap |
| 17 | 拟 `.ok` 仅预留 / live=0 / QUIET ABSENT | **PASS** | 拟名未创建；顶层 live `.ok`=0；loop 无 QUIET；本审未挂未签 |
| 18 | sampler | **PASS_WITH_CONDITIONS** | 脚本钉 `SAMPLER_PREFIX=/tmp/quantlab_leaf32_x2_selfcheck_`；**未内建** sampler → 若启用须签文/prelaunch 外挂；禁其它前缀 |
| 19 | 内存峰值风险 | **PASS_WITH_CONDITIONS** | alpha≈**1234632** 行；`evaluate` 按名装 panel + capacity_adv 叠层 → 峰可能贴/破 1500；硬 ABORT 会停；静态审 ≠ 峰证明；peak_proof REQUIRED；MemAvailable 听主软地板 |
| 20 | 静态自检 | **PASS** | SCRIPT_RECEIPT：dry-compile PASS / py_compile PASS；本审复跑 `py_compile` PASS；遵「禁代跑」未跑 dry-compile / evaluate / 未 `--execute` |

## 3. 硬钉对齐

### 3.1 PRIMARY 语义

本票正确切分：**消费**叶32 已落盘 alpha（`13eee6fd` / meta `e510f346` / overlap `a643d71a`；Arch CONSUME `a1a5e35a`；AI RUN `f3e8f991`；peak_kb=929300≪1500），生成评价权重并跑 selfcheck_v1；**不是**再建 alpha，**不是** Book-Smoke，**不是** X2 ACCEPT。CONSUMED_PASS / Alpha ACCEPT（仅构建）**不解阻**本票开跑，更**不解阻 X2**。

### 3.2 PIN_GAP / Alpha 闸（签文必披露）

| 字段 | 状态 |
|---|---|
| IC / ICIR / walk-forward | **ABSENT_UNTIL_SELFCHECK**（Alpha 闸 `1aa432a5` 标明 ABSENT） |
| Alpha 闸 VERDICT | **ACCEPT（仅研究级 α 构建过程）**；≠收益过程过闸；≠组合门裁定 |
| claim_x2_accept | **false** |
| 禁称 | X2 ACCEPT / IC 已过闸 / 升纸面 |
| 另队 | `0087c928`（叶30 KEEP）**不夹带**；本审未读未审 |

回执与签文须复述本表；selfcheck 数字即使「过闸」亦不自动构成 X2/ACCEPT。

### 3.3 残余风险（须写入签条件）

1. **evaluate 装载面**：alpha≈123 万行；panel + capacity_adv 叠层；硬 ABORT 会停，仍须 peak_proof；MemAvailable 听主软地板；建议短窗错开其它研究实跑。
2. **`--execute` 无 `.ok` 校验**：禁在无新 `.ok`/窗外执行；流程门由主+Arch 执守（CMD 已正确禁 `--arch-ok-path`）。
3. **DIFF 形态**：派生 delta 可还原脚本；权威以脚本全长 `dcf6b559…` 为准；可选补 `/dev/null` DIFF。
4. **`selfcheck_v1.json` 固定路径**：重跑会覆写报告；权重/side_meta 带 stamp；回执须交权重 sha + 报告 sha + peak + PIN_GAP 复述。
5. **≠X2 ACCEPT**；禁 RESTORED 七票尤其 **`02426b73`/`4bb141c9`/`fdbaa512`/`aa25e989`/`7e239487`/`5af20222`/`5ae077fa`**（及 forbid 全集二十票）。
6. **禁触 A18**；**不审** `0087c928`。
7. **盯 decay KEEP**：叶30/31 均 DECAY_DOWNGRADE HOLD；本票 evaluate 裁定；签后回执须带 decay outcome + gates A/B/current。

## 4. 条件（另回合签发前必须满足）

1. **主排新签窗**（建议短窗；错开其它研究实跑；MemAvailable 听主软地板；无叠加 QUIET 冲突）——**本回合不签**。
2. 新 `.ok` 硬钉：
   - script sha `dcf6b559165e43dcaa56df8adc3cb5d9574b6b55cc5ba20cf39d97b0285cda4f`（sha8 **`dcf6b559`**）
   - CLI PRIMARY（对齐 CMD；**禁** `--arch-ok-path`）：
     `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf32_margin_net_flow_resid_x2_selfcheck_v1.py --universe HILIQ --window x2 --execute`
     （alpha/meta 默认即钉盘；可选显式 `--alpha-path`/`--meta-path`）。
   - 钉三件：alpha `13eee6fd…` / meta `e510f346…` / overlap `a643d71a…`
   - 构建 **UNCHANGED** `4e0f3c00`；模板 `e1fe578c` UNCHANGED；Arch CONSUME `a1a5e35a`；Alpha 闸 `1aa432a5`（ACCEPT 仅构建；IC/ICIR/WF ABSENT_UNTIL_SELFCHECK）；FROZEN `6b8de5e9`
   - `rss_soft_mb=1500` · `rss_hard_mb=1500` · `forbid_raise_rss=true`；破硬帽脚本 ABORT；禁抬帽
   - `forbid_restored_ok_sha8`：**二十票**含七票 **`02426b73`/`4bb141c9`/`fdbaa512`/`aa25e989`/`7e239487`/`5af20222`/`5ae077fa`** + `3c297052`/`e107383f`/`2be59acd`/`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`/`0f50daf7`/`3c19dd7d`/`1c32ab1e`/`6054b3bf`/`6de02e74`
   - sampler（若启用）：`/tmp/quantlab_leaf32_x2_selfcheck_*` only
   - 权重目录：`…/_leaf32_margin_flow/20261027_042805/_selfcheck/`；报告：`…/leaf_reports/leaf32_margin_flow/selfcheck_v1.json`
   - **PIN_GAP** 明文：IC/ICIR/WF ABSENT_UNTIL_SELFCHECK；Alpha ACCEPT 仅构建；≠X2 ACCEPT
   - **decay KEEP**：回执须带 decay outcome + portfolio gates A/B/current
   - COVER/CMD/DIFF/回执/本审 全长钉入签文（若改 CMD/脚本须重审重钉）
   - live=false · promotion=false · book_smoke=false · **x2_accept=false** · **alpha_build_consumed_not_x2_accept=true**
   - `0087c928` 另队不夹带；禁触 A18
3. 签时挂短窗 QUIET；AI **单次** prelaunch（healthz / wait≥15s / pgrep 空 / 脚本 sha MATCH / dry-compile 复核）后 `--execute`；交回执（权重 sha + selfcheck_v1.json sha + peak rss + **PIN_GAP 复述** + decay/gates）；AI 勿擅 lift / 勿自重跑 / 勿抬帽。
4. **peak_proof REQUIRED**（至少：`rss_mb_peak_self` / `peak_proof.ru_maxrss_mb`；若挂 sampler 则 sampler 峰）。
5. **≠X2 ACCEPT**；不解阻全量 X2；本审不构成自动开跑授权。
6. 禁 RESTORED 任一 VOID/CONSUMED（尤其七票）。

## 5. 禁项（本回合 + 签后）

- **本回合不签** `.ok`；不挂 QUIET；不代跑 evaluate/`--execute`；不排签窗（等主）；不抬帽
- 禁复用/RESTORED：forbid 二十票（含七票）
- 禁抬 rss；禁 Book-Smoke；禁当 X2 ACCEPT；禁复跑 alpha 构建
- 禁改 `research/leaf32_margin_net_flow_resid_alpha_build.py`（`4e0f3c00`）；禁改模板 `e1fe578c`；禁动已 CONSUMED 归档 `.ok`
- 禁把 CONSUMED_PASS / Alpha ACCEPT（构建）当本票授权；禁称 IC 已过闸
- 禁静默 fallback / 禁换 universe/window / 禁换 alpha 路径
- 禁带 `--arch-ok-path` 开跑（脚本不认；CMD 已禁）
- 禁审/夹带 `0087c928`；禁触 A18；**不报 Leo**

## 6. 建议签窗 / 拟 `.ok` 名（勿本回合创建）

- **勿本回合签**（主令硬钉只审不签）。
- 建议：主确认 CONDITIONS（尤其 `--execute` 流程门 + peak_proof + decay KEEP 盯）后排下一空窗；签时 QUIET；与其它 leaf 实跑错开。
- 拟名：`output/ai_factory/ARCH_RUN_AUTH_LEAF32_MARGIN_NET_FLOW_RESID_X2_SELFCHECK_V1_HILIQ_X2.ok`；**新签**，禁 RESTORED 二十票任一内容（尤其 **`02426b73`**）。

## 7. 本回合非动作声明

- **未签**任何 `.ok`
- **未挂** QUIET
- **未代跑** evaluate / `--execute`（仅复跑 `py_compile`；未复跑 dry-compile）
- **未改**主干代码 / 构建脚本 / 模板 / 钉盘 alpha/meta/overlap
- **未动**叶32 X2 已 CONSUMED 归档 `.ok`（`02426b73`）；**未审** `0087c928`
- **不解阻 X2**；**不当 X2 ACCEPT**；**未触 A18**
- live=false · promotion=false · **不推 Leo**

## 8. 结论

**PASS_WITH_CONDITIONS** — 包钉全 MATCH；PRIMARY 语义正确；SELFCHECK_EXECUTED=false 成立；forbid 七票齐（全集二十）；rss 硬 ABORT+peak_proof；decay KEEP 三闸+gates A/B/current 同构；PIN_GAP/Alpha 闸已披露；`0087c928` 不夹带；输出隔离；构建 `4e0f3c00` / 模板 `e1fe578c` UNCHANGED；CMD/argparse 已禁 `--arch-ok-path`（无漂移）。开放项见 §4（新窗+新 `.ok`、DIFF 形态说明、`--execute` 流程门、peak_proof/内存峰、禁 RESTORED/禁 X2 ACCEPT）。**可请主另排独立签窗**；本回合不签。

> 全文件 `sha256sum` 以落盘后实测为准（见 Arch→主回执）。
