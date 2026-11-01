# Arch 审阅：叶37 IMAX Lottery Exclusion Overlay X2 selfcheck_v1 独立票（只审不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-27T19:04:45-04:00`（America/New_York；墙钟 `2026-10-27 19:04 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 `.ok`；**不挂 QUIET**；**不代跑**任何 evaluate/`--execute`；不改脚本/主干；不抬 rss；**不解阻 X2**；禁当 X2 ACCEPT；≠Book-Smoke；live=false；promotion=false；**不推 Leo**；不触 A18；**不审** `0087c928`；并行 cand4 B port 另线不夹带 |
| 触发 | 主 19:00 ET 交审（TEAM_STATE）+ 本拍执行令；包钉以主令表为准；模板对照叶34 审票 `e2902e64` / 脚本 `d210efba` |
| 对照 | 脚本 `015e6f06` · COVER `8c83ba13` · CMD `6f5d48bd` · DIFF `2542e7cd` · 落盘回执 `bb616bdb` · mask `2503a41e` · overlap `8177578f` · meta `e9e9aa1d` · B1 `32605aca` UNCHANGED · 基盘 `108aba8f` ban_as_live · 模板叶34 `d210efba` · 叶32 `dcf6b559` · common `218b61cf` · Arch CONSUME `c0a6b5ae` · consumed `.ok` `b5be1164` · VOID `4096d401` · FROZEN `c5927f1b` · PIN `e01be34c` · AI RUN `c6d8b1ce` · ACK `08652c66` · SIGNED `7b3bd298` · 审 `b403a7e5` · VOID回执 `998171e1` |

## 0. 一句话

包钉全件 **MATCH**；PRIMARY = 钉既有叶37 IMAX Lottery Exclusion Overlay B1_LOWMEM×x2 **exclusion_mask**（`2503a41e`）→ `build_eval_weights_from_mask`（**capacity_adv × mask**；≠α TopN）→ `leaf_selfcheck_common.evaluate` 写 `selfcheck_v1.json`；**≠** 复跑 B1/基盘 / **≠** Book-Smoke / **≠** X2 ACCEPT。新脚本 `015e6f06`（派生自叶34 `d210efba` 只读）不覆写钉盘 mask/meta/overlap，不碰 B1 `32605aca` / 基盘 `108aba8f`；产物隔离 `_selfcheck/` + `leaf_reports/leaf37_imax_lottery/selfcheck_v1.json`。**SELFCHECK_EXECUTED=false** 盘证成立。rss 软/硬 **1500** + `check_rss_hard` **硬 ABORT** + peak_proof。forbid **n=32** 含 `b5be1164`+`4096d401`+`eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+`178e90e9`+`c1b71e64`+…。闸门书面冻结：PRIMARY=HI_LIQ **mask-only top_q=0.20** × capacity_adv；C3=**B** IMAX_proxy；b1_lowmem=**true**；coverage_median=**2816.5**≥300；判定=主干级 OR (ρ_excess<0.5 且 60/100万叠加优于主干)；并列 Gate A/B/current；decay KEEP 三闸；**KEEP 不解阻 X2 ACCEPT**（`45dd87dc`；叶36 HOLD 不复开）。CMD/argparse **已去掉**未实现 `--arch-ok-path`（对齐叶34/32/25 P0）。DIFF=`/dev/null`→新文件，本机 `patch -p0` 还原字节 ≡ 脚本（`015e6f06`）。裸跑无 `--execute` **exit=2**（FATAL 文案 MATCH）。开放 CONDITIONS：`--execute` alone 不校验 live `.ok`；mask≈**142** 万行 → 峰可能贴/破 1500（硬 ABORT+peak_proof；build peak_kb=1107536 已近帽）；sampler 未内建。**本回合不签 `.ok`**；请主另排独立签窗。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| 脚本（新 CHANGED） | `research/leaf37_imax_lottery_exclusion_overlay_x2_selfcheck_v1.py` | `015e6f06` | `015e6f0666f697d07f33ea33f4572b4e90d099ab6e6bfba74e10c00328e61e61` | **MATCH** |
| COVER | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_SELFCHECK_COVER_DRAFT_20261027_ZH.md` | `8c83ba13` | `8c83ba135e9e2d675e56b8c47cd82b2ea56aa8189f2ece25477b6cd25769874c` | **MATCH** · DRAFT ONLY |
| CMD | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_SELFCHECK_CMD_DRAFT_20261027_ZH.md` | `6f5d48bd` | `6f5d48bdc5e3f7f63889e72a140b02d56b937337f92d8ceefd2f630be59632b2` | **MATCH** · 现不可跑；**禁** `--arch-ok-path` |
| DIFF | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_SELFCHECK_DIFF_DRAFT_20261027.diff` | `2542e7cd` | `2542e7cdaa2fe24f18bd78b36284d754197cbe533163056141736c6005ff123c` | **MATCH** · `/dev/null`→新文件 |
| 落盘回执 | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_SELFCHECK_SCRIPT_RECEIPT_20261027_ZH.md` | `bb616bdb` | `bb616bdbb54e2530f24fac8a72f4f8e2e5f7cc6b4f42129a1134de1e1b72cedc` | **MATCH** · dry-compile/py_compile 采信；本审复跑均 **PASS** |
| mask | `output/ai_factory/_leaf37_imax_lottery/20261027_183719/exclusion_mask_HILIQ_x2_20261027_183755.parquet` | `2503a41e` | `2503a41e297442da43cca4db2598acec314c8647af954231e7c49456c0862f62` | **MATCH** |
| overlap | `…/overlap_vs_leaf18_18v_27_hard_24_34_35_36_disclose.json` | `8177578f` | `8177578f72f327fe2d20cd05760459f1a934a3dd903a6cde28651b953e368af8` | **MATCH** |
| meta | `…/run_meta.json` | `e9e9aa1d` | `e9e9aa1df45b95cf0e44d995a9151068bd739b5aae4592bc13b6184accfacd2f` | **MATCH** |
| B1 构建（UNCHANGED） | `research/leaf37_imax_lottery_exclusion_overlay_alpha_build_b1_lowmem.py` | `32605aca` | `32605acac230b777cc02e72f8385f31aa64bafd5fdf2784f9f05c8b567090d0c` | **MATCH UNCHANGED** |
| 基盘（ban_as_live） | `research/leaf37_imax_lottery_exclusion_overlay_alpha_build.py` | `108aba8f` | `108aba8f5c3f58f2792d31b36a793ff5251fa732174667e037ffae113eb91f2b` | **MATCH UNCHANGED** |
| 模板叶34（只读） | `research/leaf34_high_accrual_exclusion_overlay_x2_selfcheck_v1.py` | `d210efba` | `d210efba27ff3b45d3da88faa3f0767adc4d6b5481420f48a31bf6e77e38f7f6` | **MATCH UNCHANGED** |
| 模板叶32（只读） | `research/leaf32_margin_net_flow_resid_x2_selfcheck_v1.py` | `dcf6b559` | `dcf6b559165e43dcaa56df8adc3cb5d9574b6b55cc5ba20cf39d97b0285cda4f` | **MATCH UNCHANGED** |
| `leaf_selfcheck_common.py` | `research/leaf_selfcheck_common.py` | `218b61cf` | `218b61cfbf2bf0b6bb133ef030aa2d7ff20b3eafda9724aa98c9f3b1fa5cb054` | **MATCH**（脚本硬钉） |
| Arch CONSUMED | `docs/v2/audit/ARCH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_B1_LOWMEM_X2_CONSUMED_PASS_20261027_ZH.md` | `c0a6b5ae` | `c0a6b5ae6a6408a3bae35b84f8daa2c4734a1ce29cdc2a87212d899bd4903c98` | **MATCH** |
| FROZEN | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_PREREG_FROZEN_20261027_ZH.md` | `c5927f1b` | `c5927f1b07a67c4e839c3084202e84f10529a379779a3dfc10ae751487676213` | **MATCH** |
| PIN（C3=B IMAX_proxy） | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_IMAX_PROXY_PIN_20261027_ZH.md` | `e01be34c` | `e01be34cfedeedffe750e753ace1977071d0b073238ac294fe78d75284ea0c2a` | **MATCH** |
| 叶33 正式（只读） | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` | `afbbe7e7` | （dry pin_sha_table） | **MATCH UNCHANGED** |
| 叶35 正式（只读） | `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py` | `434ff42c` | （dry pin_sha_table） | **MATCH UNCHANGED** |
| 叶34 构建（只读） | `research/leaf34_high_accrual_exclusion_overlay_alpha_build.py` | `482009dc` | （dry pin_sha_table） | **MATCH UNCHANGED** |
| Arch 叶34 审票模板（只读对照） | `docs/v2/audit/ARCH_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_SELFCHECK_REVIEW_20261027_ZH.md` | `e2902e64` | （本机 MATCH） | **MATCH** · 模板对照 |

live `.ok`（`output/ai_factory` 顶层）=**0**；拟 `.ok` `output/ai_factory/ARCH_RUN_AUTH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_SELFCHECK_V1_HILIQ_X2.ok` **未创建**；`output/loop/RESEARCH_QUIET.lock` **ABSENT**；本审**未挂** QUIET；`_leaf37…/_selfcheck/` **ABSENT**；`leaf_reports/leaf37_imax_lottery/` **ABSENT**；`selfcheck_v1.json`（叶37）**ABSENT**；`eval_weights*`（叶37）**ABSENT** → **SELFCHECK_EXECUTED=false** 成立。

## 2. CMD / COVER / 脚本核验

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| 1 | PRIMARY：钉 mask → 权重 → selfcheck_v1 | **PASS** | 脚本：`assert_pins` 全长钉 mask+meta+overlap → `build_eval_weights_from_mask` → `_selfcheck/eval_weights_*.parquet` → `LC.evaluate(wp)` → `leaf_reports/leaf37_imax_lottery/selfcheck_v1.json`；**非**重算 B1/基盘 |
| 2 | ≠ 复跑 B1/基盘 / Book-Smoke / X2 ACCEPT | **PASS** | docstring/COVER/CMD/dry meta：`book_smoke:false` `x2_accept:false` `mask_build_consumed_not_x2_accept:true`；B1/基盘禁改；基盘 ban_as_live |
| 3 | PRIMARY=HI_LIQ mask-only top_q=0.20 × capacity_adv（≠α TopN） | **PASS** | `PRIMARY_DELIVERY=mask_only` `TOP_Q=0.20` `soft_penalty_is_primary=False`；权重=capacity_adv×mask；mask=0→权0；缺失不填假0 |
| 4 | C3=B IMAX_proxy；b1_lowmem；coverage≥300 | **PASS** | dry：`c3_option=B` `c3_formula=IMAX_proxy` `full_residual_e_id=false` `b1_lowmem=true`；coverage_median=2816.5≥300 PASS；C11≠叶24 `g1g5_ashare_imax_intraday_v1` |
| 5 | 闸门书面冻结 + KEEP 不解阻 | **PASS** | `GATE_POLICY_FROZEN_ZH` 钉判定 OR ρ_excess；Gate A/B/current；decay KEEP 三闸；`keep_does_not_unblock_x2_accept=true` + `45dd87dc`；叶36 HOLD 不复开 |
| 6 | SELFCHECK_EXECUTED=false | **PASS** | COVER/CMD/回执明文 false；盘上无权重/报告；本审**未代跑** evaluate/`--execute`；本审 `py_compile` **PASS** + `--dry-compile-only` **PASS** |
| 7 | CONSUMED 不解阻 X2 | **PASS** | Arch `c0a6b5ae` / consumed `.ok` `b5be1164` 分层 CONSUMED 仅 B1 构建；本票独立脚本；禁 RESTORED `b5be1164`+`4096d401` |
| 8 | forbid **32**票齐 | **PASS** | `FORBID_RESTORED` n=32 unique=32：首项 `b5be1164`/`4096d401` + 叶35/34 旧票 + classic |
| 9 | rss 软/硬 1500 + 硬 ABORT + peak_proof | **PASS** | `RSS_SOFT_MB=RSS_HARD_MB=1500`；`check_rss_hard` 破则 `SystemExit`；`PEAK_PROOF_REQUIRED=True`；`forbid_raise_rss:true` |
| 10 | 不改写 mask / 不碰 `32605aca`/`108aba8f` | **PASS** | 写路径仅 `_selfcheck/*` + `selfcheck_v1.json` + side_meta；`assert_pins` 校验 B1/基盘/模板 sha；实测仍 MATCH |
| 11 | 输出路径隔离 | **PASS** | `SELFCHECK_SUB=…/20261027_183719/_selfcheck`；报告 `leaf_reports/leaf37_imax_lottery/selfcheck_v1.json`；不覆写钉盘 run_meta/mask/overlap |
| 12 | DIFF vs 脚本 | **PASS** | DIFF=`/dev/null`→新文件；本机 `patch -p0` → 字节 ≡ 脚本（sha8 **`015e6f06`**；29309 bytes） |
| 13 | PRIMARY CLI（仅文档对照；现禁跑） | **PASS** | dry：`--universe HILIQ --window x2 --dry-compile-only` 与脚本一致。拟 execute：`--universe HILIQ --window x2 --execute`；CMD **明文禁** `--arch-ok-path`；脚本 argparse **无此旗标**（仅注释/披露）→ **无 CMD 漂移** |
| 14 | `--execute` 门 / 无 .ok 运行时检查 | **PASS_WITH_CONDITIONS** | 缺 `--execute` → **exit 2**（本审复跑 MATCH）；`--execute` alone 仍 `live:false` 但**不**校验 live `.ok` → 流程门（新 `.ok`+主窗外挂）必须签文硬钉 |
| 15 | 裸跑无 `--execute` | **PASS** | 本审复跑：exit=**2**；stderr=`FATAL: 缺 --execute。DRAFT/静态请用 --dry-compile-only；正式跑须新 .ok + 主排签窗后再加 --execute。` |
| 16 | dry-compile-only | **PASS** | 本审复跑 exit=**0**；`pin_sha_match=true`；schema 轻读 OK（rows=**1421604**；cols 含 trade_date/ts_code/mask/alpha/imax_proxy）；rss_mb≈68.64；`selfcheck_executed=false`；coverage_gate_pass=true |
| 17 | `0087c928` 不夹带 | **PASS** | 仅 `LEAF30_KEEP_REPAIR_SHA8_SEPARATE` 披露；无 open/read/Path 执行；本审未读未审该票；叶28/29 另队 |
| 18 | overlap 只读消费 | **PASS** | `assert_pins` 校验 `PIN_OVERLAP` 全长 `8177578f…`；执行路径不改写 overlap |
| 19 | 拟 `.ok` 仅预留 / live=0 / QUIET ABSENT | **PASS** | 拟名未创建；顶层 live `.ok`=0；loop 无 QUIET；本审未挂未签 |
| 20 | sampler | **PASS_WITH_CONDITIONS** | 脚本钉 `SAMPLER_PREFIX=/tmp/quantlab_leaf37_x2_selfcheck_`；**未内建** sampler → 若启用须签文/prelaunch 外挂；禁其它前缀 |
| 21 | 内存峰值风险 | **PASS_WITH_CONDITIONS** | mask≈**1421604** 行；`evaluate` 按名装 panel + capacity_adv 叠层；build peak_kb=**1107536** 已近 1500MB 硬帽；硬 ABORT 会停；静态审 ≠ 峰证明；peak_proof REQUIRED；建议短窗错开其它研究实跑 |
| 22 | 静态自检 | **PASS** | SCRIPT_RECEIPT：dry-compile PASS / py_compile PASS / 无 `--execute` exit2；本审复跑三者齐 PASS |
| 23 | 模板叶34 对照 | **PASS** | 主令钉模板 `d210efba` MATCH；Arch 审票模板 `e2902e64` MATCH；脚本硬钉校验模板 sha；派生语义对齐（mask-only overlay selfcheck） |

## 3. 硬钉对齐

### 3.1 PRIMARY 语义

本票正确切分：**消费**叶37 B1_LOWMEM 已落盘 exclusion_mask（`2503a41e` / meta `e9e9aa1d` / overlap `8177578f`；Arch CONSUME `c0a6b5ae`；consumed `.ok` `b5be1164`），以 **mask-only overlay**（capacity_adv × mask；top_q=0.20 已在构建侧固化；C3=B IMAX_proxy）生成评价权重并跑 selfcheck_v1；**不是**再建 alpha，**不是** α TopN，**不是** Book-Smoke，**不是** X2 ACCEPT，**不是**复跑基盘 `108aba8f`。CONSUMED_PASS **不解阻**本票开跑，更**不解阻 X2**。**KEEP 不解阻 X2 ACCEPT**（叶32 HOLD `45dd87dc`；叶36 HOLD 不复开）。C11≠叶24 `g1g5_ashare_imax_intraday_v1`。

### 3.2 PIN_GAP / 闸门披露（签文必披露）

| 字段 | 状态 |
|---|---|
| PRIMARY 交付 | **mask_only** top_q=**0.20**；soft-penalty **非 PRIMARY** |
| C3 / b1_lowmem | **B** IMAX_proxy；full_residual_e_id=**false**；b1_lowmem=**true** |
| coverage | median=**2816.5** ≥ gate **300** PASS |
| IC / ICIR / walk-forward | **非本票主交付**（PIN_GAP=`MASK_ONLY_OVERLAY_NO_FULL_ALPHA`） |
| 组合闸 / decay | 由 `evaluate` 产出 Gate A/B/current + decay KEEP 三闸 |
| claim_x2_accept | **false** |
| keep_does_not_unblock_x2_accept | **true**（`45dd87dc`；叶36 HOLD） |
| 禁称 | X2 ACCEPT / IC 已过闸 / 升纸面 / 叶24 同构 |
| 另队 | `0087c928`（叶30 KEEP）/叶28/29 **不夹带**；本审未读未审；cand4 B port 另线 |

回执与签文须复述本表；selfcheck 数字即使「过闸」亦不自动构成 X2/ACCEPT。

### 3.3 残余风险（须写入签条件）

1. **evaluate 装载面**：mask≈142 万行；panel + capacity_adv 叠层；B1 build peak_kb≈1.11M 已近 1500 硬帽；硬 ABORT 会停，仍须 peak_proof；MemAvailable 听主软地板；建议短窗错开其它研究实跑（含 cand4 port）。
2. **`--execute` 无 `.ok` 校验**：禁在无新 `.ok`/窗外执行；流程门由主+Arch 执守（CMD 已正确禁 `--arch-ok-path`）。
3. **`selfcheck_v1.json` 固定路径**：重跑会覆写报告；权重/side_meta 带 stamp；回执须交权重 sha + 报告 sha + peak + PIN_GAP/闸门复述。
4. **≠X2 ACCEPT**；禁 RESTORED 尤其 **`b5be1164`/`4096d401`/`eb70eef4`/`00eec671`/`10927bd9`/`25ae4572`/`178e90e9`/`c1b71e64`**（及 forbid 全集三十二票）。
5. **禁触 A18**；**不审** `0087c928`；叶36 HOLD 不复开；基盘 `108aba8f` ban_as_live 禁跑。
6. **盯 decay KEEP + ρ_excess**：回执须带 decay outcome + gates A/B/current + ρ_excess（若可得）。

## 4. 条件（另回合签发前必须满足）

1. **主排新签窗**（建议短窗；错开其它研究实跑与 cand4 port；MemAvailable 听主软地板；无叠加 QUIET 冲突）——**本回合不签**。
2. 新 `.ok` 硬钉：
   - script sha `015e6f0666f697d07f33ea33f4572b4e90d099ab6e6bfba74e10c00328e61e61`（sha8 **`015e6f06`**）
   - CLI PRIMARY（对齐 CMD；**禁** `--arch-ok-path`）：
     `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf37_imax_lottery_exclusion_overlay_x2_selfcheck_v1.py --universe HILIQ --window x2 --execute`
     （mask/meta 默认即钉盘；可选显式 `--mask-path`/`--meta-path`）。
   - 钉三件：mask `2503a41e…` / meta `e9e9aa1d…` / overlap `8177578f…`
   - B1 **UNCHANGED** `32605aca`；基盘 `108aba8f` ban_as_live；模板叶34 `d210efba` / 叶32 `dcf6b559` / common `218b61cf` UNCHANGED；Arch CONSUME `c0a6b5ae`；FROZEN `c5927f1b`；PIN `e01be34c`
   - `rss_soft_mb=1500` · `rss_hard_mb=1500` · `forbid_raise_rss=true`；破硬帽脚本 ABORT；禁抬帽
   - `forbid_restored_ok_sha8`：**三十二票**含 **`b5be1164`/`4096d401`/`eb70eef4`/`00eec671`/`10927bd9`/`25ae4572`/`178e90e9`/`c1b71e64`** + classic
   - sampler（若启用）：`/tmp/quantlab_leaf37_x2_selfcheck_*` only
   - 权重目录：`…/_leaf37_imax_lottery/20261027_183719/_selfcheck/`；报告：`…/leaf_reports/leaf37_imax_lottery/selfcheck_v1.json`
   - **闸门/PIN_GAP** 明文：PRIMARY=mask-only top_q=0.20；C3=B IMAX_proxy；b1_lowmem=true；判定 OR ρ_excess；Gate A/B/current；decay KEEP；**KEEP 不解阻 X2 ACCEPT**；≠X2 ACCEPT；≠叶24
   - COVER/CMD/DIFF/回执/本审 全长钉入签文（若改 CMD/脚本须重审重钉）
   - live=false · promotion=false · book_smoke=false · **x2_accept=false** · **mask_build_consumed_not_x2_accept=true**
   - `0087c928`/叶28/29 另队不夹带；禁触 A18；叶36 HOLD 不复开
3. 签时挂短窗 QUIET；AI **单次** prelaunch（healthz / wait≥15s / pgrep 空 / 脚本 sha MATCH / dry-compile 复核）后 `--execute`；交回执（权重 sha + selfcheck_v1.json sha + peak rss + **闸门/PIN_GAP 复述** + decay/gates/ρ_excess）；AI 勿擅 lift / 勿自重跑 / 勿抬帽。
4. **peak_proof REQUIRED**（至少：`rss_mb_peak_self` / `peak_proof.ru_maxrss_mb`；若挂 sampler 则 sampler 峰）。
5. **≠X2 ACCEPT**；不解阻全量 X2；本审不构成自动开跑授权。
6. 禁 RESTORED 任一 VOID/CONSUMED（尤其 `b5be1164`+`4096d401`+三十票全集）。

## 5. 禁项（本回合 + 签后）

- **本回合不签** `.ok`；不挂 QUIET；不代跑 evaluate/`--execute`；不排签窗（等主）；不抬帽
- 禁复用/RESTORED：forbid 三十二票（含 `b5be1164`/`4096d401`）
- 禁抬 rss；禁 Book-Smoke；禁当 X2 ACCEPT；禁复跑 B1/基盘
- 禁改 `32605aca` / `108aba8f` / 模板 `d210efba`/`dcf6b559`/`218b61cf`；禁动已 CONSUMED 归档 `.ok`
- 禁把 CONSUMED_PASS 当本票授权；禁称 IC 已过闸；禁 KEEP 解阻 ACCEPT；禁复开叶36；禁冒充叶24
- 禁静默 fallback / 禁换 universe/window / 禁换 mask 路径 / 禁 FULLA PRIMARY
- 禁带 `--arch-ok-path` 开跑（脚本不认；CMD 已禁）
- 禁审/夹带 `0087c928`/叶28/29；禁触 A18；**不报 Leo**；cand4 B port 另线不夹带

## 6. 建议签窗 / 拟 `.ok` 名（勿本回合创建）

- **勿本回合签**（主令硬钉只审不签）。
- 建议：主确认 CONDITIONS（尤其 `--execute` 流程门 + peak_proof/近帽内存 + decay KEEP/ρ_excess 盯）后排下一空窗；签时 QUIET；与其它 leaf 实跑及 cand4 port 错开。
- 拟名：`output/ai_factory/ARCH_RUN_AUTH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_SELFCHECK_V1_HILIQ_X2.ok`；**新签**，禁 RESTORED 三十二票任一内容（尤其 **`b5be1164`/`4096d401`**）。

## 7. 本回合非动作声明

- **未签**任何 `.ok`
- **未挂** QUIET
- **未代跑** evaluate / `--execute`（仅复跑 `py_compile` + `--dry-compile-only` + 裸跑无 `--execute` 验 exit2）
- **未改**主干代码 / B1/基盘 / 模板 / 钉盘 mask/meta/overlap
- **未动**叶37 B1 已 CONSUMED 归档 `.ok`（`b5be1164`）；**未审** `0087c928`；**未碰** cand4 port
- **不解阻 X2**；**不当 X2 ACCEPT**；**未触 A18**
- live=false · promotion=false · **不推 Leo**

## 8. 结论

**PASS_WITH_CONDITIONS** — 包钉全 MATCH；PRIMARY 语义正确（mask-only×capacity_adv；C3=B IMAX_proxy；≠α TopN；≠叶24）；闸门书面冻结齐；SELFCHECK_EXECUTED=false 成立；forbid 三十二票齐；rss 硬 ABORT+peak_proof；DIFF `/dev/null` 可还原 ≡ 脚本；裸跑 exit2 MATCH；CMD/argparse 已禁 `--arch-ok-path`（无漂移）；B1 `32605aca` / 基盘 `108aba8f` / 模板叶34 `d210efba` / 叶32 `dcf6b559` UNCHANGED；模板审票 `e2902e64` 对照 MATCH。开放项见 §4（新窗+新 `.ok`、`--execute` 流程门、peak_proof/近帽内存、禁 RESTORED/禁 X2 ACCEPT）。**可请主另排独立签窗**；本回合不签。

> 全文件 `sha256sum` 以落盘后实测为准（见 Arch→主回执）。
