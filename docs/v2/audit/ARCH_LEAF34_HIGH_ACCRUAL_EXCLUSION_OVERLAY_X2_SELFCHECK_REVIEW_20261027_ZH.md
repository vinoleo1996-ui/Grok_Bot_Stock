# Arch 审阅：叶34 High Accrual Exclusion Overlay X2 selfcheck_v1 独立票（只审不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-27T11:28:45-04:00`（America/New_York；墙钟 `2026-10-27 11:28 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 `.ok`；**不挂 QUIET**；**不代跑**任何 evaluate/`--execute`；不改脚本/主干；不抬 rss；**不解阻 X2**；禁当 X2 ACCEPT；≠Book-Smoke；live=false；promotion=false；**不推 Leo**；不触 A18；**不审** `0087c928` |
| 触发 | 主 11:22 ET 交审（TEAM_STATE）+ 本拍执行令；包钉以主令表为准 |
| 对照 | 脚本 `d210efba` · COVER `0bf02521` · CMD `4255ad33` · DIFF `a1a6689d` · 落盘回执 `a5467d7d` · mask `8b5d6d24` · overlap `77368c8f` · meta `4fc6108d` · 构建 UNCHANGED `482009dc` · 模板叶32 `dcf6b559` · 叶33 `afbbe7e7` · Arch CONSUME `fea9b3ff` · consumed `.ok` `c1b71e64` · FROZEN `8be1099e` · PIN `bb418e6a` |

## 0. 一句话

包钉全件 **MATCH**；PRIMARY = 钉既有叶34 High Accrual Exclusion Overlay HILIQ×x2 **exclusion_mask**（`8b5d6d24`）→ `build_eval_weights_from_mask`（**capacity_adv × mask**；≠α TopN）→ `leaf_selfcheck_common.evaluate` 写 `selfcheck_v1.json`；**≠** 复跑 alpha 构建 / **≠** Book-Smoke / **≠** X2 ACCEPT。新脚本 `d210efba` 不覆写钉盘 mask/meta/overlap，不碰构建 `482009dc`；产物隔离 `_selfcheck/` + `leaf_reports/leaf34_high_accrual/selfcheck_v1.json`。**SELFCHECK_EXECUTED=false** 盘证成立。rss 软/硬 **1500** + `check_rss_hard` **硬 ABORT** + peak_proof。forbid **n=25** 含 `c1b71e64`+`245df63f`+`c5ed13df`+`5774bb6e`+二十票(+`81521fb5`)。闸门书面冻结：PRIMARY=HI_LIQ **mask-only top_q=0.20** × capacity_adv；判定=主干级 OR (ρ_excess<0.5 且 60/100万叠加优于主干)；并列 Gate A/B/current；decay KEEP 三闸；**KEEP 不解阻 X2 ACCEPT**（`45dd87dc`）。CMD/argparse **已去掉**未实现 `--arch-ok-path`（对齐叶25/30/31/32 P0）。DIFF=`/dev/null`→新文件，本机 `patch -p0` 还原字节 ≡ 脚本（`d210efba`）。裸跑无 `--execute` **exit=2**（FATAL 文案 MATCH）。开放 CONDITIONS：`--execute` alone 不校验 live `.ok`；mask≈124 万行 → 峰可能贴/破 1500（硬 ABORT+peak_proof）；sampler 未内建。**本回合不签 `.ok`**；请主另排独立签窗。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| 脚本（新 CHANGED） | `research/leaf34_high_accrual_exclusion_overlay_x2_selfcheck_v1.py` | `d210efba` | `d210efba27ff3b45d3da88faa3f0767adc4d6b5481420f48a31bf6e77e38f7f6` | **MATCH** |
| COVER | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_SELFCHECK_COVER_DRAFT_20261027_ZH.md` | `0bf02521` | `0bf0252123d09e61a483ac9b9a9dcc8ebd6cb47ce14d6aef1f8fd62046a1bd03` | **MATCH** · DRAFT ONLY |
| CMD | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_SELFCHECK_CMD_DRAFT_20261027_ZH.md` | `4255ad33` | `4255ad338bec4bf07d5c84b20a2b857a8e477334487065a86d05ab7737768860` | **MATCH** · 现不可跑；**禁** `--arch-ok-path` |
| DIFF | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_SELFCHECK_DIFF_DRAFT_20261027.diff` | `a1a6689d` | `a1a6689dff0ef55de117c7712d7210986fbef3e086947ada5540330f49fd0819` | **MATCH** · `/dev/null`→新文件 |
| 落盘回执 | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_SELFCHECK_SCRIPT_RECEIPT_20261027_ZH.md` | `a5467d7d` | `a5467d7d80237220fea0545db649ef1fa8044656c1aceb5af210d7a37728f1bb` | **MATCH** · dry-compile/py_compile 采信；本审复跑均 **PASS** |
| mask | `output/ai_factory/_leaf34_high_accrual/20261027_105941/exclusion_mask_HILIQ_x2_20261027_105958.parquet` | `8b5d6d24` | `8b5d6d247d8f3968f5fef521aa5d08891f6f6f6c8626dd761c7313bc0d71dabb` | **MATCH** |
| overlap | `…/overlap_vs_leaf19_25_27_30_31_32_33.json` | `77368c8f` | `77368c8fed1f7c167dfa51f4aa2e94e9b405236bf388c8f20f95365613e72fb7` | **MATCH** |
| meta | `…/run_meta.json` | `4fc6108d` | `4fc6108d64ca5a2e112b04fbb468c9d95e554cf8498ba03fc13828c2ef7ee7ad` | **MATCH** |
| 构建脚本 | `research/leaf34_high_accrual_exclusion_overlay_alpha_build.py` | `482009dc` | `482009dc697cbf74b369cbf3fb035f1fc447a4af9339de8abf283f3ed4e971bc` | **MATCH UNCHANGED** |
| 模板叶32（只读） | `research/leaf32_margin_net_flow_resid_x2_selfcheck_v1.py` | `dcf6b559` | `dcf6b559165e43dcaa56df8adc3cb5d9574b6b55cc5ba20cf39d97b0285cda4f` | **MATCH UNCHANGED** |
| 叶33 正式（只读） | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` | `afbbe7e7` | `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` | **MATCH UNCHANGED** |
| Arch CONSUMED | `docs/v2/audit/ARCH_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_CONSUMED_PASS_20261027_ZH.md` | `fea9b3ff` | `fea9b3ff5ac3824f5cb7e19fe27753372fc75da6ab72f82f42620cef01fd666c` | **MATCH** |
| consumed `.ok` 内容 | `_consumed/…c1b71e64.CONSUMED_PASS…` | `c1b71e64` | `c1b71e646093dbbe1cfea41c684d8ee0de8e5af8f0a8f058182c251d7dbe4ce1` | **MATCH** · 禁 RESTORED |
| FROZEN | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_PREREG_FROZEN_20261027_ZH.md` | `8be1099e` | `8be1099e73c6029ad2ddcbe7a18a28fc5a27cc03acfb91cba048e26b7867f815` | **MATCH** |
| PIN（C3 PIT/NP/YTD） | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_OCF_PIT_PIN_20261027_ZH.md` | `bb418e6a` | `bb418e6ae8ee7fd2b0cfc6816360bcb7bb197537dc1aac44fcfb05d375224e9b` | **MATCH** |
| 模板叶31（只读） | `research/leaf31_amihud_impact_slow_x2_selfcheck_v1.py` | `e1fe578c` | `e1fe578ca70bd61f6c98bd849357beecb918f9e88f0732ac6bbc98dcfb0d4b38` | **MATCH**（脚本硬钉） |
| `leaf_selfcheck_common.py` | `research/leaf_selfcheck_common.py` | `218b61cf` | `218b61cfbf2bf0b6bb133ef030aa2d7ff20b3eafda9724aa98c9f3b1fa5cb054` | **MATCH**（脚本硬钉） |

live `.ok`（`output/ai_factory` 顶层）=**0**；拟 `.ok` `output/ai_factory/ARCH_RUN_AUTH_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_SELFCHECK_V1_HILIQ_X2.ok` **未创建**；`output/loop/RESEARCH_QUIET.lock` **ABSENT**；本审**未挂** QUIET；`_leaf34…/_selfcheck/` **ABSENT**；`leaf_reports/leaf34_high_accrual/` **ABSENT**；`selfcheck_v1.json`（叶34）**ABSENT**；`eval_weights*`（叶34）**ABSENT** → **SELFCHECK_EXECUTED=false** 成立。

## 2. CMD / COVER / 脚本核验

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| 1 | PRIMARY：钉 mask → 权重 → selfcheck_v1 | **PASS** | 脚本：`assert_pins` 全长钉 mask+meta+overlap → `build_eval_weights_from_mask` → `_selfcheck/eval_weights_*.parquet` → `LC.evaluate(wp)` → `leaf_reports/leaf34_high_accrual/selfcheck_v1.json`；**非**重算 alpha |
| 2 | ≠ 复跑 alpha / Book-Smoke / X2 ACCEPT | **PASS** | docstring/COVER/CMD/dry meta：`book_smoke:false` `x2_accept:false` `mask_build_consumed_not_x2_accept:true`；构建脚本禁改 |
| 3 | PRIMARY=HI_LIQ mask-only top_q=0.20 × capacity_adv（≠α TopN） | **PASS** | `PRIMARY_DELIVERY=mask_only` `TOP_Q=0.20` `soft_penalty_is_primary=False`；权重=capacity_adv×mask；mask=0→权0；缺失不填假0 |
| 4 | 闸门书面冻结 + KEEP 不解阻 | **PASS** | `GATE_POLICY_FROZEN_ZH` 钉判定 OR ρ_excess&lt;0.5+60/100万；Gate A/B/current；decay KEEP 三闸；`keep_does_not_unblock_x2_accept=true` + `45dd87dc` |
| 5 | SELFCHECK_EXECUTED=false | **PASS** | COVER/CMD/回执明文 false；盘上无权重/报告；本审**未代跑** evaluate/`--execute`；本审 `py_compile` **PASS** + `--dry-compile-only` **PASS** |
| 6 | CONSUMED 不解阻 X2 | **PASS** | Arch `fea9b3ff` / consumed `.ok` `c1b71e64` 分层 CONSUMED 仅构建；本票独立脚本；禁 RESTORED `c1b71e64` |
| 7 | forbid **25**票齐 | **PASS** | `FORBID_RESTORED` n=25：`c1b71e64`/`245df63f`/`c5ed13df`/`5774bb6e` + classic20 + `81521fb5` |
| 8 | rss 软/硬 1500 + 硬 ABORT + peak_proof | **PASS** | `RSS_SOFT_MB=RSS_HARD_MB=1500`；`check_rss_hard` 破则 `SystemExit`；`PEAK_PROOF_REQUIRED=True`；`forbid_raise_rss:true` |
| 9 | 不改写 mask / 不碰 `482009dc` | **PASS** | 写路径仅 `_selfcheck/*` + `selfcheck_v1.json` + side_meta；`assert_pins` 校验构建 sha 前缀 `482009dc`；实测仍 MATCH |
| 10 | 输出路径隔离 | **PASS** | `SELFCHECK_SUB=…/20261027_105941/_selfcheck`；报告 `leaf_reports/leaf34_high_accrual/selfcheck_v1.json`；不覆写钉盘 run_meta/mask/overlap |
| 11 | DIFF vs 脚本 | **PASS** | DIFF=`/dev/null`→新文件；本机 `patch -p0` → 字节 ≡ 脚本（sha8 **`d210efba`**） |
| 12 | PRIMARY CLI（仅文档对照；现禁跑） | **PASS** | dry：`--universe HILIQ --window x2 --dry-compile-only` 与脚本一致。拟 execute：`--universe HILIQ --window x2 --execute`；CMD **明文禁** `--arch-ok-path`；脚本 argparse **无此旗标**（仅注释/披露）→ **无 CMD 漂移** |
| 13 | `--execute` 门 / 无 .ok 运行时检查 | **PASS_WITH_CONDITIONS** | 缺 `--execute` → **exit 2**（本审复跑 MATCH）；`--execute` alone 仍 `live:false` 但**不**校验 live `.ok` → 流程门（新 `.ok`+主窗外挂）必须签文硬钉 |
| 14 | 裸跑无 `--execute` | **PASS** | 本审复跑：exit=**2**；stderr=`FATAL: 缺 --execute。DRAFT/静态请用 --dry-compile-only；正式跑须新 .ok + 主排签窗后再加 --execute。` |
| 15 | dry-compile-only | **PASS** | 本审复跑 exit=**0**；`pin_sha_match=true`；schema 轻读 OK（rows=1244524；cols 含 trade_date/ts_code/mask）；rss_mb≈70.92；`selfcheck_executed=false` |
| 16 | `0087c928` 不夹带 | **PASS** | 仅 `LEAF30_KEEP_REPAIR_SHA8_SEPARATE` 披露；无 open/read/Path 执行；本审未读未审该票；叶28/29 另队 |
| 17 | overlap 只读消费 | **PASS** | `assert_pins` 校验 `PIN_OVERLAP` 全长 `77368c8f…`；执行路径不改写 overlap |
| 18 | 拟 `.ok` 仅预留 / live=0 / QUIET ABSENT | **PASS** | 拟名未创建；顶层 live `.ok`=0；loop 无 QUIET；本审未挂未签 |
| 19 | sampler | **PASS_WITH_CONDITIONS** | 脚本钉 `SAMPLER_PREFIX=/tmp/quantlab_leaf34_x2_selfcheck_`；**未内建** sampler → 若启用须签文/prelaunch 外挂；禁其它前缀 |
| 20 | 内存峰值风险 | **PASS_WITH_CONDITIONS** | mask≈**1244524** 行；`evaluate` 按名装 panel + capacity_adv 叠层 → 峰可能贴/破 1500；硬 ABORT 会停；静态审 ≠ 峰证明；peak_proof REQUIRED |
| 21 | 静态自检 | **PASS** | SCRIPT_RECEIPT：dry-compile PASS / py_compile PASS / 无 `--execute` exit2；本审复跑三者齐 PASS |

## 3. 硬钉对齐

### 3.1 PRIMARY 语义

本票正确切分：**消费**叶34 已落盘 exclusion_mask（`8b5d6d24` / meta `4fc6108d` / overlap `77368c8f`；Arch CONSUME `fea9b3ff`；consumed `.ok` `c1b71e64`），以 **mask-only overlay**（capacity_adv × mask；top_q=0.20 已在构建侧固化）生成评价权重并跑 selfcheck_v1；**不是**再建 alpha，**不是** α TopN，**不是** Book-Smoke，**不是** X2 ACCEPT。CONSUMED_PASS **不解阻**本票开跑，更**不解阻 X2**。**KEEP 不解阻 X2 ACCEPT**（叶32 HOLD `45dd87dc`）。

### 3.2 PIN_GAP / 闸门披露（签文必披露）

| 字段 | 状态 |
|---|---|
| PRIMARY 交付 | **mask_only** top_q=**0.20**；soft-penalty **非 PRIMARY** |
| IC / ICIR / walk-forward | **非本票主交付**（PIN_GAP=`MASK_ONLY_OVERLAY_NO_FULL_ALPHA`） |
| 组合闸 / decay | 由 `evaluate` 产出 Gate A/B/current + decay KEEP 三闸 |
| claim_x2_accept | **false** |
| keep_does_not_unblock_x2_accept | **true**（`45dd87dc`） |
| 禁称 | X2 ACCEPT / IC 已过闸 / 升纸面 |
| 另队 | `0087c928`（叶30 KEEP）/叶28/29 **不夹带**；本审未读未审 |

回执与签文须复述本表；selfcheck 数字即使「过闸」亦不自动构成 X2/ACCEPT。

### 3.3 残余风险（须写入签条件）

1. **evaluate 装载面**：mask≈124 万行；panel + capacity_adv 叠层；硬 ABORT 会停，仍须 peak_proof；MemAvailable 听主软地板；建议短窗错开其它研究实跑。
2. **`--execute` 无 `.ok` 校验**：禁在无新 `.ok`/窗外执行；流程门由主+Arch 执守（CMD 已正确禁 `--arch-ok-path`）。
3. **`selfcheck_v1.json` 固定路径**：重跑会覆写报告；权重/side_meta 带 stamp；回执须交权重 sha + 报告 sha + peak + PIN_GAP/闸门复述。
4. **≠X2 ACCEPT**；禁 RESTORED 尤其 **`c1b71e64`/`245df63f`/`c5ed13df`/`5774bb6e`/`81521fb5`**（及 forbid 全集二十五票）。
5. **禁触 A18**；**不审** `0087c928`。
6. **盯 decay KEEP + ρ_excess**：回执须带 decay outcome + gates A/B/current + ρ_excess（若可得）。

## 4. 条件（另回合签发前必须满足）

1. **主排新签窗**（建议短窗；错开其它研究实跑；MemAvailable 听主软地板；无叠加 QUIET 冲突）——**本回合不签**。
2. 新 `.ok` 硬钉：
   - script sha `d210efba27ff3b45d3da88faa3f0767adc4d6b5481420f48a31bf6e77e38f7f6`（sha8 **`d210efba`**）
   - CLI PRIMARY（对齐 CMD；**禁** `--arch-ok-path`）：
     `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf34_high_accrual_exclusion_overlay_x2_selfcheck_v1.py --universe HILIQ --window x2 --execute`
     （mask/meta 默认即钉盘；可选显式 `--mask-path`/`--meta-path`）。
   - 钉三件：mask `8b5d6d24…` / meta `4fc6108d…` / overlap `77368c8f…`
   - 构建 **UNCHANGED** `482009dc`；模板叶32 `dcf6b559` / 叶33 `afbbe7e7` / 叶31 `e1fe578c` / common `218b61cf` UNCHANGED；Arch CONSUME `fea9b3ff`；FROZEN `8be1099e`；PIN `bb418e6a`
   - `rss_soft_mb=1500` · `rss_hard_mb=1500` · `forbid_raise_rss=true`；破硬帽脚本 ABORT；禁抬帽
   - `forbid_restored_ok_sha8`：**二十五票**含 **`c1b71e64`/`245df63f`/`c5ed13df`/`5774bb6e`/`81521fb5`** + classic20
   - sampler（若启用）：`/tmp/quantlab_leaf34_x2_selfcheck_*` only
   - 权重目录：`…/_leaf34_high_accrual/20261027_105941/_selfcheck/`；报告：`…/leaf_reports/leaf34_high_accrual/selfcheck_v1.json`
   - **闸门/PIN_GAP** 明文：PRIMARY=mask-only top_q=0.20；判定 OR ρ_excess；Gate A/B/current；decay KEEP；**KEEP 不解阻 X2 ACCEPT**；≠X2 ACCEPT
   - COVER/CMD/DIFF/回执/本审 全长钉入签文（若改 CMD/脚本须重审重钉）
   - live=false · promotion=false · book_smoke=false · **x2_accept=false** · **mask_build_consumed_not_x2_accept=true**
   - `0087c928`/叶28/29 另队不夹带；禁触 A18
3. 签时挂短窗 QUIET；AI **单次** prelaunch（healthz / wait≥15s / pgrep 空 / 脚本 sha MATCH / dry-compile 复核）后 `--execute`；交回执（权重 sha + selfcheck_v1.json sha + peak rss + **闸门/PIN_GAP 复述** + decay/gates/ρ_excess）；AI 勿擅 lift / 勿自重跑 / 勿抬帽。
4. **peak_proof REQUIRED**（至少：`rss_mb_peak_self` / `peak_proof.ru_maxrss_mb`；若挂 sampler 则 sampler 峰）。
5. **≠X2 ACCEPT**；不解阻全量 X2；本审不构成自动开跑授权。
6. 禁 RESTORED 任一 VOID/CONSUMED（尤其 `c1b71e64`+四旧票+二十票+`81521fb5`）。

## 5. 禁项（本回合 + 签后）

- **本回合不签** `.ok`；不挂 QUIET；不代跑 evaluate/`--execute`；不排签窗（等主）；不抬帽
- 禁复用/RESTORED：forbid 二十五票（含 `c1b71e64`）
- 禁抬 rss；禁 Book-Smoke；禁当 X2 ACCEPT；禁复跑 alpha 构建
- 禁改 `research/leaf34_high_accrual_exclusion_overlay_alpha_build.py`（`482009dc`）；禁改模板 `dcf6b559`/`e1fe578c`/`afbbe7e7`；禁动已 CONSUMED 归档 `.ok`
- 禁把 CONSUMED_PASS 当本票授权；禁称 IC 已过闸；禁 KEEP 解阻 ACCEPT
- 禁静默 fallback / 禁换 universe/window / 禁换 mask 路径 / 禁 FULLA PRIMARY
- 禁带 `--arch-ok-path` 开跑（脚本不认；CMD 已禁）
- 禁审/夹带 `0087c928`/叶28/29；禁触 A18；**不报 Leo**

## 6. 建议签窗 / 拟 `.ok` 名（勿本回合创建）

- **勿本回合签**（主令硬钉只审不签）。
- 建议：主确认 CONDITIONS（尤其 `--execute` 流程门 + peak_proof + decay KEEP/ρ_excess 盯）后排下一空窗；签时 QUIET；与其它 leaf 实跑错开。
- 拟名：`output/ai_factory/ARCH_RUN_AUTH_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_SELFCHECK_V1_HILIQ_X2.ok`；**新签**，禁 RESTORED 二十五票任一内容（尤其 **`c1b71e64`**）。

## 7. 本回合非动作声明

- **未签**任何 `.ok`
- **未挂** QUIET
- **未代跑** evaluate / `--execute`（仅复跑 `py_compile` + `--dry-compile-only` + 裸跑无 `--execute` 验 exit2）
- **未改**主干代码 / 构建脚本 / 模板 / 钉盘 mask/meta/overlap
- **未动**叶34 X2 已 CONSUMED 归档 `.ok`（`c1b71e64`）；**未审** `0087c928`
- **不解阻 X2**；**不当 X2 ACCEPT**；**未触 A18**
- live=false · promotion=false · **不推 Leo**

## 8. 结论

**PASS_WITH_CONDITIONS** — 包钉全 MATCH；PRIMARY 语义正确（mask-only×capacity_adv；≠α TopN）；闸门书面冻结齐；SELFCHECK_EXECUTED=false 成立；forbid 二十五票齐；rss 硬 ABORT+peak_proof；DIFF `/dev/null` 可还原 ≡ 脚本；裸跑 exit2 MATCH；CMD/argparse 已禁 `--arch-ok-path`（无漂移）；构建 `482009dc` / 叶32 `dcf6b559` / 叶33 `afbbe7e7` UNCHANGED。开放项见 §4（新窗+新 `.ok`、`--execute` 流程门、peak_proof/内存峰、禁 RESTORED/禁 X2 ACCEPT）。**可请主另排独立签窗**；本回合不签。

> 全文件 `sha256sum` 以落盘后实测为准（见 Arch→主回执）。
