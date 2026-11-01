# 2026-10-18 恢复清单（Arch 执行器，只读核查）

- 编写：2026-10-18 01:18 ET。box 于 01:05:41 ET 重启，快照恢复于约 01:14 ET 完成（恢复文件 mtime 为 01:10–01:14 ET，原始 mtime 未保留，所以无法从 mtime 判断快照时点）。
- 内容推断的快照时点：TEAM_STATE 中最晚的重启前 Arch 行是 01:04 ET；叶 23 预注册（01:04:41 冻结）在；MILP 规格（约 01:04–01:05 起草）不在。所以快照大约截至 01:04–01:05 ET。
- git：HEAD e7b240d（2026-10-18 00:55:09 ET），`git fsck` 无报错。docs/v2 里的冻结件多数未被 git 跟踪，所以 git 不能作为它们的恢复来源。
- 文件数：执行时 /workspace/QuantLab 共 181767→181856（01:15–01:17 ET），仍在缓慢增加，增量来自各 agent 的正常写入，不是恢复进程；docs/v2 约 711，output 约 12726。
- 数据面板：data/ 目录已恢复（如 data/v2/intel_consensus 全在）。cs_panel 未逐个核对 sha（没有已知原 sha）。
- /cursor/stores：01:13 和 01:17 ET 两次检查均未挂载。
- 外部来源：Cursor Origin 命名空间 leo-vino、GitHub 均无 QuantLab 仓库；/workspace/cloud-agent-artifacts 不存在；QuantLab-source.tgz、ql_mac_sync_20261012.tgz、eng_panels 备份 tgz 里都不含目标文件。
- 本清单只做核查：没有往目录树里放任何恢复文件，没有写 git，也没有建 .ok。

## 逐文件核对

| 文件 | 路径 | 原 sha | 现 sha | 匹配 | 来源 | 备注 |
|---|---|---|---|---|---|---|
| LOTFIX v1.4 正文（FROZEN） | `docs/v2/STRATEGY_OPTIMIZER_STAGE2_LOTFIX_DRAFT_ZH.md` | d921dd3f0f698deb | d921dd3f0f698deb | 是 | 快照恢复 |  |
| LOTFIX 快照 d921dd3f | `docs/v2/audit/snapshots/STRATEGY_OPTIMIZER_STAGE2_LOTFIX_DRAFT_ZH.d921dd3f0f698deb822a59e40aa643f1efc7f43f6c36eaed30c7a672dbdf9425.md` | d921dd3f0f698deb | d921dd3f0f698deb | 是 | 快照恢复 |  |
| LOTFIX 快照 a1a2552c | `docs/v2/audit/snapshots/STRATEGY_OPTIMIZER_STAGE2_LOTFIX_DRAFT_ZH.a1a2552caf5fae66c7aa75a6475858591ac5a6a709b16bfdd90cccb060ae83e7.md` | a1a2552caf5fae66 | a1a2552caf5fae66 | 是 | 快照恢复 | 另有短名副本 .a1a2552c.md，sha 相同 |
| LOTFIX 快照 b322e7e2 | `docs/v2/audit/snapshots/STRATEGY_OPTIMIZER_STAGE2_LOTFIX_DRAFT_ZH.b322e7e2aee2484231446db4b981257fe8e8dc786c051bb60b00ea518e297f65.md` | b322e7e2aee24842 | b322e7e2aee24842 | 是 | 快照恢复 |  |
| LOTFIX 中间版 a642b16a（Arch 01:02 签署版） | `（无）` | a642b16a | — | 缺失 | — | 全盘及 git 3871 个 blob 均无 sha 匹配；据 TEAM_STATE 01:02 行，当时只快照了 b322e7e2，a642b16a 可能从未单独落盘 |
| LOTFIX v1.4 冻结记录 | `docs/v2/LOTFIX_V1_4_FREEZE_RECORD_ZH.md` | 0d47c52f8be402d0 | 0d47c52f8be402d0 | 是 | 快照恢复 | _recovery/main/ 下副本 sha 相同（仅供对照） |
| SD1 规格 | `docs/v2/ARCH_ENGINE_SUSPEND_DELIST_FIX_SPEC_ZH.md` | 2e428f3956fcb6d2 | 2e428f3956fcb6d2 | 是 | 快照恢复 |  |
| MILP 抛光预注册规格（DRAFT） | `docs/v2/ARCH_MILP_LOTPOLISH_PREREG_SPEC_ZH.md` | f78f93aa306864f9 | — | 缺失 | — | 缺失：全盘、tgz、git blob 均无；探针脚本和 3 个结果 json 在，规格须重写 |
| MILP 探针 | `docs/v2/audit/arch_milp_probe_v1.py` | 51a6df602b039c45 | 51a6df602b039c45 | 是 | 快照恢复 |  |
| 叶 23 预注册（AI 自报 6eca9eb8，已独立核对） | `docs/v2/AI_G1G5_SUE_DESENS_WHO_PAYS_PREREG_ZH.md` | 6eca9eb8cae08231 | 6eca9eb8cae08231 | 是 | 快照恢复 | _recovery/ai 副本 sha 相同 |
| AI 恢复清单（AI 自报 0f3eb001） | `_recovery/ai/RECOVERY_MANIFEST_ZH.md` | 0f3eb001f21ea96e | 0f3eb001f21ea96e | 是 | 重启后 AI 写入 | 仅供对照 |
| 并列敏感性 .ok | `output/strategy_hiliq/ARCH_RUN_AUTH_TIE_SENS_v1.ok` | 8cc9622760433ca1 | 8cc9622760433ca1 | 是 | 快照恢复 | 对应 01:02 运行已作废；该 .ok 不得再用 |
| 并列敏感性脚本 | `research/strategy_tie_sensitivity_prereg_v1.py` | abef35f4d8422b6c | abef35f4d8422b6c | 是 | 快照恢复 |  |
| 并列敏感性预注册 | `docs/v2/STRATEGY_TIE_SENSITIVITY_PREREG_ZH.md` | 0af0aa1059cbb9a2 | 0af0aa1059cbb9a2 | 是 | 快照恢复 |  |
| 依赖 912fb007 | `research/strategy_capadv_topn_tie_sensitivity.py` | 912fb007 | 912fb00794ae3a11 | 是 | 快照恢复 |  |
| 依赖 fed36cf2 | `research/strategy_b4_hiliq_leg_review.py` | fed36cf2 | fed36cf2567190d3 | 是 | 快照恢复 |  |
| 依赖 3f7f75c3 | `research/strategy_hiliq_capadv_b4_x2.py` | 3f7f75c3 | 3f7f75c31611de6a | 是 | 快照恢复 |  |
| 审计 CSV 6f80fb08 | `output/strategy_hiliq/topn_tie_audit/capadv_leg_score_tie_by_rebalance.csv` | 6f80fb08 | 6f80fb083a60bed9 | 是 | 快照恢复 |  |
| runner b6238254（现行） | `research/optimizer_core_x2_run.py` | b623825457efb2a3 | b623825457efb2a3 | 是 | 快照恢复 | 归档副本 research/_runner_archive/optimizer_core_x2_run.b6238254.py 亦匹配 |
| runner 29b38cf8（归档） | `research/_runner_archive/optimizer_core_x2_run.29b38cf8.py` | 29b38cf880ebb7c3 | 29b38cf880ebb7c3 | 是 | 快照恢复 |  |
| 停跑规则草案 41f29825 | `docs/v2/STRATEGY_OPTIMIZER_STOPRULE_CONSEC_DRAFT_ZH.md` | 41f29825c85a66c8 | 41f29825c85a66c8 | 是 | 快照恢复 |  |
| 停跑规则冻结记录 13c6ad58 | `docs/v2/STOPRULE_CONSEC_FREEZE_RECORD_ZH.md` | 13c6ad58 | 13c6ad5872d8c86e | 是 | 快照恢复 |  |
| S2-3 冻结记录 a8e67a71 | `docs/v2/S2_3_FREEZE_RECORD_ZH.md` | a8e67a71 | a8e67a71ca774a39 | 是 | 快照恢复 |  |
| v1.3 记分卡审计 | `docs/v2/ARCH_V1_3_SCORECARD_AUDIT_ZH.md` | eab8ff78 | eab8ff78a386474f | 是 | 快照恢复 |  |
| N8 修复审查 | `docs/v2/ARCH_AI_N8_FIX_REVIEW_ZH.md` | 63d0122e | 63d0122ee465175c | 是 | 快照恢复 |  |
| RUN_AUTH_FORMAT | `output/strategy_optimizer/core_x2/RUN_AUTH_FORMAT.md` | — | ab3ce57bbbb17212 | 无原值 | 快照恢复 | 无已知原 sha，仅记录现值 |
| Data 诊断 | `docs/v2/DATA_SUSPEND_RESUME_DELIST_DIAG_ZH.md` | — | cf953adadddb765c | 无原值 | 快照恢复 | 无已知原 sha，仅记录现值 |
| Data 重建方案 | `docs/v2/DATA_CS_PANEL_RESUME_REBUILD_PLAN_ZH.md` | — | — | 缺失 | — | 缺失：全盘无此文件，需 Data 重出 |
| Arch 对 Data 重建方案的审查 | `docs/v2/ARCH_DATA_CS_PANEL_REBUILD_REVIEW_ZH.md` | — | fa75e4ff6e64ad14 | 无原值 | git 未跟踪 | 无已知原 sha，仅记录现值 |
| Intel 业绩预告预注册 r3（Intel 自报，已独立核对） | `docs/v2/INTEL_EARNINGS_PREANNOUNCE_PREREG_ZH.md` | 16e891687fac1993 | 16e891687fac1993 | 是 | 快照恢复 | 与旁注 .sha256 一致 |
| Intel 供应链映射 v1（Intel 自报，已独立核对） | `data/v2/intel_consensus/supply_chain_map_v1.csv` | 19fbcbf4aa97e53b | 19fbcbf4aa97e53b | 是 | 快照恢复 | 位于 data/v2，不在 docs/v2 |
| Intel 供应链映射 v1.1（Intel 自报，已独立核对） | `data/v2/intel_consensus/supply_chain_map_v1_1.csv` | 1843fbc5823073de | 1843fbc5823073de | 是 | 快照恢复 | 位于 data/v2 |
| Intel capex 设计（FROZEN，Intel 自报，已独立核对） | `docs/v2/INTEL_HYPERSCALER_CAPEX_DESIGN_ZH.md` | 9702bc46a144d100 | 9702bc46a144d100 | 是 | 快照恢复 | 与旁注 .sha256 一致 |
| AMEND-1 现行版 r2.1 | `docs/v2/LOTFIX_V1_4_AMEND_POOL_SNAPSHOT_ZH.md` | 0029672aed3d9e6a | 0029672aed3d9e6a | 是 | 重启后编辑（Arch） | r1 0fce3cb9 已核实为本文件前 1419 字节；r2 d4c32724 作废（A3 措辞按 Beta 修改，d4c32724 不是现文件的前缀） |
| Beta v1.4 会签（Beta 自报 0ad588a3） | `docs/v2/BETA_LOTFIX_V1_4_COSIGN_ZH.md` | 0ad588a3fb725b5b | 0ad588a3fb725b5b | 是 | 重启后编辑（Beta） | 原文加勘误；_recovery/beta 下 .VOID.md 为 a4b46f60（仅供对照） |
| Beta AMEND-1 会签（Beta 自报 45b7f415） | `docs/v2/BETA_LOTFIX_AMEND1_POOL_SNAPSHOT_COSIGN_ZH.md` | 45b7f4156e99a950 | 45b7f4156e99a950 | 是 | 重启后编辑（Beta） | _recovery/beta 副本 sha 相同 |
| tie VOID 说明 | `output/strategy_hiliq/_VOID_archive/tie_sens_prereg_v1_VOID_20261018_0102/VOID.md` | 8e51a949 | 8e51a94989aba4ff | 是 | 重启后写入（Strategy） | 恢复未覆盖 |
| Alpha LEGS_ACCEPT | `docs/v2/ALPHA_HILIQ_LEGS_ACCEPT_20261014_ZH.md` | — | 1d6cfb55e2c24ef1 | 无原值 | 快照恢复 | 与 Alpha 自查时 1d6cfb55 相同；Alpha 判定 v4.1 节缺失，恢复后未变 |
| Alpha SIGN_RECON | `docs/v2/ALPHA_EQUITY_SIGN_RECON_20261018_ZH.md` | — | 1fa05ff9e5ad7632 | 无原值 | 快照恢复 | 与 Alpha 自查时 1fa05ff9 相同；文件中无 §9 标题，§9 仍缺 |
| alpha_combo_marginal.py | `research/alpha_combo_marginal.py` | — | bee230199ac27bf9 | 无原值 | 快照恢复 | 与 Alpha 自查时 bee23019 相同 |
| Alpha v4.json | `output/alpha/ALPHA_HILIQ_LEGS_ACCEPT_20261014.v4.json` | — | — | 缺失 | — | 缺失（v1/v2/v3 json 在） |
| Alpha step_e_fullsleeve_b_v41.json | `output/alpha/recon_eqinc/step_e_fullsleeve_b_v41.json` | — | — | 缺失 | — | 缺失 |

## 仅供对照的 _recovery/ 目录（不得当作原件使用）

- 目录：_recovery/ai、alpha、beta、eng、main、web。
- _recovery/main/LOTFIX_V1_4_FREEZE_RECORD_ZH.md = 0d47c52f（与原件相同）
- _recovery/ai/RECOVERY_MANIFEST_ZH.md = 0f3eb001；_recovery/ai 里叶 23 副本 = 6eca9eb8（与原件相同）
- _recovery/beta/docs/v2/BETA_LOTFIX_V1_4_COSIGN_ZH.VOID.md = a4b46f60（与现行 0ad588a3 不同）
- _recovery/beta/docs/v2/BETA_LOTFIX_AMEND1_POOL_SNAPSHOT_COSIGN_ZH.md = 45b7f415（与现行版相同）
- Beta 清单 f4eae3c7（Beta 自报）：没有找到 sha 为 f4eae3c7 的文件。_recovery/beta/RECOVERY_MANIFEST_ZH.md 的实测 sha 是 1c76966b，不一致，请 Beta 说明。
- Alpha 重建件（据 _recovery/alpha/MANIFEST.txt，sha 已复算一致）：
  - ALPHA_COMBO_MARGINAL_PENDING_PATCH_ZH.md 235f9980：补丁说明。原件 alpha_combo_marginal.py（bee23019）在，二者不可直接比较
  - ALPHA_HILIQ_LEGS_v4_1_SECTION_ZH.md 66cc9abc：原 v4.1 节没有恢复，无法比对
  - CHECKLIST_s9_ZH.md f2270360：Alpha 自报 GATEV3 清单的 §9 已恢复（f9696254），未逐字比对
  - SIGN_RECON_s6_correction_and_s9_ZH.md 9014ae1d：原 §9 没有恢复，无法比对

## TEAM_STATE_latest.md

- 共 127 行，重启前历史完整，最后一条重启前 Arch 行是 01:04 ET。
- 01:07、01:09、01:13 的 Arch 重启后行都不在（已被恢复覆盖或从未写入）。另有一行标为「[Arch 10-18 05:14 ET]」，时间其实是 UTC，应为 01:14 ET，需要更正。

## tie_sens_prereg_v1（01:02 已作废运行的残留输出，没有打开内容，只列 sha）

- 共 80 个文件：7 个 weights_*.parquet，加上 7 个 smoke_* 子目录。根目录没有 summary.json；smoke_B4_SPLIT_60w 里只有 run.log，所以是不完整输出。

```
4fe5b9528a355b4b83e5b2b056d9b0d5125f94b3366f18dd993fc3678b0f2bfa  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_ADV_100w/aum_1000000/X2/BOOK/actual_weights.parquet
c8b23b40f2fba203b886d7e8868fb8abd44d5da8fdef30cf1604f6d4ebdd20b3  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_ADV_100w/aum_1000000/X2/BOOK/nav.csv
22410fa5f10617ee0370ff490fcf4f7ff049503eeaf876d49317c058e6333e47  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_ADV_100w/aum_1000000/X2/BOOK/sleeve_weights.csv
c99b23dacaa32956135a97b376eb2938487bacedf00cfe0ab039e06ff8752b09  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_ADV_100w/aum_1000000/X2/BOOK/summary.json
cc0c2061b27b24fd3f4b9bbde61ba1a4cc6aea07061ae39a2d6204bd1a565ba4  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_ADV_100w/aum_1000000/X2/BOOK/target_weights.parquet
fe38c93cdef07e9882bdccf9b5ac2cb394595dd2cc3c00d4e95cf90a08de33ad  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_ADV_100w/aum_1000000/X2/C0/actual_weights.parquet
f8fdb368887b409a633a49a5f9e219482b261fa0b093709b9b36c5e874fabd34  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_ADV_100w/aum_1000000/X2/C0/nav.csv
6c3022c0c916b7438ca0a2dd3f564189dd6f87989196eca7d50428b19e58febb  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_ADV_100w/aum_1000000/X2/C0/summary.json
4f07f26c0b53a3e47b30f8d40ad6634a97ec4634bf0790a97108343c9eeaa341  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_ADV_100w/aum_1000000/X2/C0/target_weights.parquet
7a295708d0ff40bd59500be8b08d7e2889ef21c6d1c27ce5c018fa0615125140  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_ADV_100w/book_smoke_summary.json
20fbcd93a8882592aa1723106d773a52908bc582610ef81fd1c9dabccad6c27a  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_ADV_100w/receipt.md
75f36d9165c5ee05850f7a13be0cd6abab9b50600db9d5c7e68d9592549ba48e  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_ADV_100w/run.log
5965080d18aff727599937421603b579b06093cf726ec31c6c06c9b34500c0ab  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_ADV_60w/aum_600000/X2/BOOK/actual_weights.parquet
50410901025ffb3cb33c2b26e09c5820d802a5225102a5e714ce9d5ecf5c64f2  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_ADV_60w/aum_600000/X2/BOOK/nav.csv
05703747ccd8dda5f06449802cdcb37a96c7d4d3a8dc633cc07759f3d837ac46  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_ADV_60w/aum_600000/X2/BOOK/sleeve_weights.csv
3f2fffa109dded899340fff3f0a569fb6b0e7bc48dcd3c782d2d1ff273ac103f  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_ADV_60w/aum_600000/X2/BOOK/summary.json
425fe2c0a5986a4b73502488bab6cb3ff3de8342d443ccafeb5ba044ed3d11a0  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_ADV_60w/aum_600000/X2/BOOK/target_weights.parquet
694fc932aefb5a598500430fa11b667388faeab4d5446dfe72a8f431b8587a6e  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_ADV_60w/aum_600000/X2/C0/actual_weights.parquet
06c4c41a859c5ba5fe6c1be4a6d44b6214ce3d1280be201854c9335934454a5f  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_ADV_60w/aum_600000/X2/C0/nav.csv
fe18426e9cce56e19dc09a8715ee2213b25189eff4bb27744d378bdc12169ff6  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_ADV_60w/aum_600000/X2/C0/summary.json
4f07f26c0b53a3e47b30f8d40ad6634a97ec4634bf0790a97108343c9eeaa341  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_ADV_60w/aum_600000/X2/C0/target_weights.parquet
3e3dd4a138db105891f07ff51c1a36519ff01dbc96fabbd65a4b1ff2b83dda0a  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_ADV_60w/book_smoke_summary.json
45f630696dc8176e5722d934952a5f81fefcf35b25cc2374992ee929c345e842  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_ADV_60w/receipt.md
64827320de4d5f8c5000eeda3dd7f7086fc7ef6483d9f28f5c39189431e315dc  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_ADV_60w/run.log
2abeb84498472a8d212724fd5ee988ea74a88f981873bb30dc956bbb816ddd07  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_CODE_100w/aum_1000000/X2/BOOK/actual_weights.parquet
bff51f6797b326a9ec42a2ba0de38673e2caf223a43ee09fe133c68e39fa5aa1  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_CODE_100w/aum_1000000/X2/BOOK/nav.csv
7f88f67d34d601fb8d58775c161d6c28a389c2d3a3277293783d2faf3695899f  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_CODE_100w/aum_1000000/X2/BOOK/sleeve_weights.csv
6ac533f2d1d12b39225c2900bc8720cba3356e20f3c54e0b339ccc59d8f1646d  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_CODE_100w/aum_1000000/X2/BOOK/summary.json
39dd9c972b894e6a7980bafceae2ec14f28e12bfae13362f2fe90b0a0121ff4f  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_CODE_100w/aum_1000000/X2/BOOK/target_weights.parquet
fe38c93cdef07e9882bdccf9b5ac2cb394595dd2cc3c00d4e95cf90a08de33ad  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_CODE_100w/aum_1000000/X2/C0/actual_weights.parquet
f8fdb368887b409a633a49a5f9e219482b261fa0b093709b9b36c5e874fabd34  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_CODE_100w/aum_1000000/X2/C0/nav.csv
f9d4f4d9f39e1538a1573378062f80bd2a36421f5577103430dd67172d8a3768  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_CODE_100w/aum_1000000/X2/C0/summary.json
4f07f26c0b53a3e47b30f8d40ad6634a97ec4634bf0790a97108343c9eeaa341  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_CODE_100w/aum_1000000/X2/C0/target_weights.parquet
9fb0143d2f4c0f191ebc3704155de3bb86a526a7f49aec6582bbc69bd189efbf  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_CODE_100w/book_smoke_summary.json
4c9362e15950ac8cc4664d557fc18d51e56715ea7ecf84fad3ff60b81ab4aebd  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_CODE_100w/receipt.md
11bf0fc1b213fca5c8a57e88942bddbc9fbf89e657504a9359db62ad4d430233  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_CODE_100w/run.log
9cc833699b1a7cebbf6e0ed556792a30ed6c4ae2b7470b7b1e9cff83472848bf  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_CODE_60w/aum_600000/X2/BOOK/actual_weights.parquet
2e747d3861beb998cd2784c71e3d166c89df716ad034afb6d3557452e9a4244a  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_CODE_60w/aum_600000/X2/BOOK/nav.csv
fc9be4616d093c3d7d3d5e9fc9eb6570f60ba87c4f323c0bf2d5f31e233dda5b  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_CODE_60w/aum_600000/X2/BOOK/sleeve_weights.csv
be54cb91923d8d659a6807a48cc1d269f50eb44649c711be9a711c6356855cbc  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_CODE_60w/aum_600000/X2/BOOK/summary.json
10bd08a3484ff0f756be3ae22d19d7525071a9d07bc99e9b3273ac1c4a863e29  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_CODE_60w/aum_600000/X2/BOOK/target_weights.parquet
694fc932aefb5a598500430fa11b667388faeab4d5446dfe72a8f431b8587a6e  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_CODE_60w/aum_600000/X2/C0/actual_weights.parquet
06c4c41a859c5ba5fe6c1be4a6d44b6214ce3d1280be201854c9335934454a5f  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_CODE_60w/aum_600000/X2/C0/nav.csv
465b9fa2aa2ce951afd6812417cc344ce58ec55c124f67c435f9361c6e0f59e9  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_CODE_60w/aum_600000/X2/C0/summary.json
4f07f26c0b53a3e47b30f8d40ad6634a97ec4634bf0790a97108343c9eeaa341  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_CODE_60w/aum_600000/X2/C0/target_weights.parquet
2c285aacd8862982a8cd5d2dfcc4dc5bb64017dd4016b7fd1bd1118efe0a00e9  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_CODE_60w/book_smoke_summary.json
7d9fa88681424861cc15893b272594f4c7c8e21845b8600e1292c239d9eaf823  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_CODE_60w/receipt.md
4632141ccbf3fff707ba3d7caca1b08cfce9763ce8967b0892a3a684dd238aa4  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_CODE_60w/run.log
cc8e6d0f7accb051322b7474b2e69197088ec90cbf5c180bb9e7289861868e38  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_PROD_100w/aum_1000000/X2/BOOK/actual_weights.parquet
102a5cc997bef4e81ff08cdc018f314ee3be152275600d2327b98eb8a9e0794e  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_PROD_100w/aum_1000000/X2/BOOK/nav.csv
a956bc4103bc8a0e05af00edf1fcb0fbb6af7e8c5e1a1c17fd5288c35fec4a89  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_PROD_100w/aum_1000000/X2/BOOK/sleeve_weights.csv
4ab7d1c1bb5c7c73220db15d4033ef6983b7739e5ab43d0acf57f8aa4b28a63c  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_PROD_100w/aum_1000000/X2/BOOK/summary.json
fd78aec03839006a2b8060f049fd15faef8aed4d50b791231f1645e86c5409d5  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_PROD_100w/aum_1000000/X2/BOOK/target_weights.parquet
fe38c93cdef07e9882bdccf9b5ac2cb394595dd2cc3c00d4e95cf90a08de33ad  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_PROD_100w/aum_1000000/X2/C0/actual_weights.parquet
f8fdb368887b409a633a49a5f9e219482b261fa0b093709b9b36c5e874fabd34  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_PROD_100w/aum_1000000/X2/C0/nav.csv
17c6620b67e15ed9bbf39504de4c500f21726027facfcce831fba8637bf308e0  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_PROD_100w/aum_1000000/X2/C0/summary.json
4f07f26c0b53a3e47b30f8d40ad6634a97ec4634bf0790a97108343c9eeaa341  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_PROD_100w/aum_1000000/X2/C0/target_weights.parquet
aa419b636b1cbe7225d4f97df8e3cd912f13e30e0f40cfa321e121a9c70eeb97  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_PROD_100w/book_smoke_summary.json
18f0cab1fdcfaff5d8e374804fc92bd599de25cc3e3e8c96ec52a273f30adbb0  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_PROD_100w/receipt.md
8bf5f081115d24c0acfb14f0ac0a6e5a71f6859b39826db0e760ed5f4080efb6  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_PROD_100w/run.log
939ce479dfbaeecd678f7ed6fcec7ec4e120fa979aff65c4f193921d4316effc  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_PROD_60w/aum_600000/X2/BOOK/actual_weights.parquet
ee0200d04506a5c575bd4c5032a517cdec5897be50fa36fd664cfe48c9e691f7  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_PROD_60w/aum_600000/X2/BOOK/nav.csv
9dffa3383c08fd519cff77775bba0a25f1bb89549f9af118b01d037b936eb86b  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_PROD_60w/aum_600000/X2/BOOK/sleeve_weights.csv
0e07e887f06b9c97bfec65a5ff17b76e03fbaf22a05c440b84d851bf0f8edcd5  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_PROD_60w/aum_600000/X2/BOOK/summary.json
1c9be0427ceceb4143257fc760c883430597a9e9d26a02a28147c73c16b4d9e4  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_PROD_60w/aum_600000/X2/BOOK/target_weights.parquet
694fc932aefb5a598500430fa11b667388faeab4d5446dfe72a8f431b8587a6e  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_PROD_60w/aum_600000/X2/C0/actual_weights.parquet
06c4c41a859c5ba5fe6c1be4a6d44b6214ce3d1280be201854c9335934454a5f  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_PROD_60w/aum_600000/X2/C0/nav.csv
5b569191c44b2c28877a5056d18fad8b948c451d0cf281377f38bef5d2f6ac22  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_PROD_60w/aum_600000/X2/C0/summary.json
4f07f26c0b53a3e47b30f8d40ad6634a97ec4634bf0790a97108343c9eeaa341  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_PROD_60w/aum_600000/X2/C0/target_weights.parquet
16c9bdeb2b7303802b8543e134cea16f20f3756d46401516cdf4317af3626022  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_PROD_60w/book_smoke_summary.json
3e213bb3b0b2f53e500496a04233c76bfebec1907af95c42b5a0570758eba25d  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_PROD_60w/receipt.md
68b55d1552cab3eceb95a81df65f83cf5bd045cbf87f98b34baf6256b9263dbc  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_PROD_60w/run.log
097d9f2cc0dd2216538547c7bd789ead78a7fd5d97100d3ac81a597f9d82e24f  output/strategy_hiliq/tie_sens_prereg_v1/smoke_B4_SPLIT_60w/run.log
30a96a6aa28fce0bdab83f3d3ed500ecc23363af996f6110318c1b090ae5626c  output/strategy_hiliq/tie_sens_prereg_v1/weights_B4_ADV_100w.parquet
dfd9d124aa4bd3767984f7b0d5a11783e5ac38b12b5da9f7d5059893b75d81f9  output/strategy_hiliq/tie_sens_prereg_v1/weights_B4_ADV_60w.parquet
c186078cf04e894c8a55dfefb986e8e508c9e5915ce1859c0f5514048e60d969  output/strategy_hiliq/tie_sens_prereg_v1/weights_B4_CODE_100w.parquet
068c7b73c3934a4d29776691527369357a140cce6f05de4134671c8be1ef79e1  output/strategy_hiliq/tie_sens_prereg_v1/weights_B4_CODE_60w.parquet
471c396a116bfb699a070141620c5f6e572392ee71e1ea807a8e845d282a10df  output/strategy_hiliq/tie_sens_prereg_v1/weights_B4_PROD_100w.parquet
a3f53ca0d0258675b58d2a30e03a49918189a26c7d1e6043108fe115e9b69ec7  output/strategy_hiliq/tie_sens_prereg_v1/weights_B4_PROD_60w.parquet
2d26bf7cbe71c2c88ea87221000f0bd51c52b0db871efc34893045db584d5844  output/strategy_hiliq/tie_sens_prereg_v1/weights_B4_SPLIT_60w.parquet
```

## 总结

- **全部冻结件完好：是**（缺失的都不是冻结件）。LOTFIX d921dd3f、冻结记录 0d47c52f、SD1 2e428f39、叶 23 6eca9eb8、runner b6238254/29b38cf8、停跑规则 41f29825/13c6ad58、S2-3 a8e67a71、tie .ok/脚本/预注册/依赖/CSV、Intel 4 件均逐位一致。
- 缺失、需要重出的文件：MILP 预注册规格 f78f93aa（DRAFT，非冻结）、DATA_CS_PANEL_RESUME_REBUILD_PLAN_ZH.md、LOTFIX 中间版 a642b16a（已被 d921dd3f 取代）、Alpha v4.json 和 step_e_fullsleeve_b_v41.json。另外，LEGS_ACCEPT 的 v4.1 节和 SIGN_RECON §9 仍缺。

## 补记（Arch 01:22 ET）
- 各组清单作为输入：_recovery/beta/RECOVERY_INVENTORY_BETA_ZH.md（27b7d007，已核实），另有 _recovery/{ai,alpha,eng,main,web}，均只作对照。
- Intel 的文件全部还在（自报，已独立核实，见上文）。
- 并列敏感性：部分产物已归档到 VOID_0102/partial，清单 31b6c430；.ok 重签为 9a4e82b2（supersedes 8cc96227），全量已于 01:20:49 ET 启动，PID 90241。
- Alpha：重生成 step_e 的 .ok 是 output/alpha/ARCH_RUN_AUTH_ALPHA_V41_REGEN_v1.ok，所有依赖已按 sha 核对一致。.v4.json 按线上 LEGS_ACCEPT JSON（version=v4，fe12db1d）直接复制得到。
- web notice.json 的 enabled 已经是 false。
- **结论：冻结件全部完好，已解除冻结。**
- 补记 01:23 ET：Alpha 按主 Agent 01:21 的指示，把 v4.1r 追加写进了正式文件，标注「照记录、未重算、待核对」：LEGS_ACCEPT f30a372b，SIGN_RECON 80a758ab。重算结果逐项对上之前，这两个文件不算恢复完成。
- 补记 01:34 ET（Arch）：Data 重建方案不再缺失。Data 01:2x 报的「回滚、输入丢失」是误报（当时恢复未完成；输入经 Arch 实测都在，output/diag 为空）。docs/v2/DATA_CS_PANEL_RESUME_REBUILD_PLAN_ZH.md 现存，sha 3a7bb0cd4407bd27fa6e58b53d0b17afca134bd3b1c63e15eb2353b7c88593b8，判定为**重写**而非恢复：文件头自注「原版在 box 重启后丢失，这是重写版」，mtime 01:23:13 EDT 晚于 01:14 恢复完成时刻，本清单此前在恢复后记为全盘缺失，且没有原 sha 可比对，因此不算逐位恢复。同批：DATA_SUSPEND_DELIST_FIX_PLAN_ZH.md 50aaf043…（01:23:13，新文件）；诊断 DATA_SUSPEND_RESUME_DELIST_DIAG_ZH.md 由恢复时的 cf953ada… 改写为 02fc06f6…（01:23:51）；脚本 scripts/fix_sd1/ 三个文件 8eac523b… / 34fd86fe… / 0e89e688…（01:22）。Arch 审核 r2 见 ARCH_DATA_CS_PANEL_REBUILD_REVIEW_ZH.md（530f53cd…），r1 fa75e4ff 已归档到 docs/v2/_archive/。
- 补记 01:36 ET（Arch，Eng 恢复复核；详见 ARCH_ENG_RECOVERY_SCORECARD_OK_REVIEW_ZH.md bbdaf52e…）：
  - **更正第 9 行「外部来源」**：Origin 命名空间 leo-vino **有** `leo-vino/QuantLab`（main 7197939d，2026-10-15 10:25:33 ET，作者 Leo vino / Cursor Agent）和 `leo-vino/QuantLab-data`（main 2f4f77a9，2026-10-15 22:36:59 ET，作者 QuantLab Frontend (agiuser)），Origin 只读接口实测；两者都不含今晚产物；本地 git 未配 remote。GitHub 无 QuantLab 的说法不变。
  - **更正 git 状态**：HEAD e7b240d 不变，但 `git status --short` 有 1373 行改动 / 未跟踪，不止 1 个文档；纸面代码 quantlab/portfolio/research_loop.py（d3ded87e）、b4_paper.py（ffe195e6）、trade_calendar.py（ef44e7cd）**不在 git**，没有独立基准，只能对 FROZEN_CONFIG 里的冻结脚本 sha。
  - Eng core_x2：manifest v1_3_RUN_MANIFEST.json（8824a87e）96 项中 92 项一致；4 个 runner 的差异经 diff 确认只有 runner-pin（scorecard 现行版另含本轮审计修复文字），去 pin 版在 _recovery/eng/scripts_eng/，逐位等于 manifest。S2-3 运行版 3d4b08e3 逐位恢复；改前版 059cf43e 是重建件（只能做循环验证）。
  - 诊断文档 DATA_SUSPEND_RESUME_DELIST_DIAG_ZH.md（cf953ada → 02fc06f6）：**无法证明旧内容是前缀**。更正注插在第 3 行，不是追加在文末；删去该行或前后空行后的 sha 都不等于 cf953ada；原版没有保存。只能按「被改写」记。
  - v1 cs_panel 基线（output/ai_factory/panel_cache，Data 清单 9 个文件，共 9,072,309 行，到 20261014），Arch 01:31 ET 全部复算：2018 035d1f60、2019 b843a7bc、2020 e25a7e59、2021 bea54e54、2022 ad188dda、2023 6acf163e、2024 6d238ee3、2025 39568253、2026 4608d8bc；ind_names.csv 1ce86712。2023–2026 四份与 output/alpha/ARCH_RUN_AUTH_ALPHA_V41_REGEN_v1.ok 的 cs_panel_20xx_sha256 pin **全长逐位一致**；2018 与 Data 清单一致。属冻结产物，没动。
  - **P0（01:33 ET）**：quantlab/platform/execution.py 不等于基准 373fed30（git HEAD blob = /workspace/sd1_orig 副本）。现值 9533075e（01:30:31，111006 B），之前是 9ea22e38（01:23:18），SD1 正在原地编辑，违反主 Agent 01:32 裁定（10-19 纸面跑完前保持 373fed30，SD1 走旁路）。该文件**不算已恢复**，待还原为 373fed30 后由 Arch 复核。delist_accounting.py（b56180e2）、tradability.py（18341572）是新增的 SD1 旁路文件。
- 补记 01:36 ET（Arch）：上条 P0 已处置。execution.py 已于 01:33:21 还原为 373fed30（90033 B），01:36 复测一致；SD1 移到旁路 quantlab/platform/execution_sd1.py。10-19 纸面跑前再核一次。（上条标注的 01:36 ET 实际约为 01:35 ET。）

- 01:49 ET 补记：Alpha 两个缺失文件已按 .ok d0816a37 复现，不是逐位恢复：step_e_fullsleeve_b_v41.json → 367556b4…087e；ALPHA_HILIQ_LEGS_ACCEPT_20261014.v4.json → fe12db1d（原样拷贝 v4 源文件）。状态 VALID_WITH_DISCLOSURE（RSS 超限一次、重跑峰值未记录）。

- 02:01 ET 补记（Arch，r4）：Data SD1 cs_panel 复牌重建 r4 新 sha，Arch 01:56 ET 实测全部一致：build_cs_panel_v2_resumefix.py 78b204c962aaafb2ec587ae869cffa28f0a39031cd95f9a18e59607efc270877；build_suspend_flags_v2.py ca581e298fdd797d3cc58cadd59014d4cc3f7a514abe8e17af508f06bae7559e；build_stock_delisted_v2.py 3821a4ef367b6544e6604d5d8a9888f8593446e2fc774481ae9525635db4823b；sd1_common.py 2e4c413133b36ed15c48fc907d56cf9794afedfc3299c1626e02dea90af211c9；DATA_CS_PANEL_RESUME_REBUILD_PLAN_ZH.md b3e86946c7d4faee7994d695292f1020c2cf674fddfb8f1f761f51933e85eea1；DATA_SUSPEND_DELIST_FIX_PLAN_ZH.md de732d25816adc0d9e11cd93429646dc208547ead3e9329978f5a0ca499cb5a1；test_sd1_common.py ffc5eb0a084c8b82c8431c045cc014361c7d876f0ff52af57904799601f9c3de（不钉）。审核 r4：docs/v2/ARCH_DATA_CS_PANEL_REBUILD_REVIEW_R4_ZH.md 96207a40d3e9fc46cd81c32124112e43d1eb5ff3fd281d1a6d1cd198d4f23eb8；Arch 签 dry-run .ok：output/data/ARCH_RUN_AUTH_CS_PANEL_RESUMEFIX_v1.ok 3a1bb537aa43da17b1c2f033c3fb9a6025b5e9528c64264c82e4108987377f7d（allow_dryrun=true，allow_full/execute/selftest/smoke=false）；r4 探针 carry_unknown_probe_r4.py 432f2b35c25f80d1a1051a448dfd91e174e47d56eeac387b7e1f433d52ceb08d、.json ec7696ffc9d7f2c3ee822e6cf198278227a5dee20a866f6f4813a868b7e7e025。
- 02:01 ET 补记（Arch）：Alpha 披露补录后的新 sha，Arch 实测一致：docs/v2/ALPHA_HILIQ_LEGS_ACCEPT_20261014_ZH.md 16df6b1907a019b8a64e8a84f45f2a5b37dd6b4c65188ac0c4b09eda286f8d79；docs/v2/ALPHA_EQUITY_SIGN_RECON_20261018_ZH.md 26313a8dee07d2b6f9c917511fa5ef0538f2f290d7652183732353aad6a67c3e（两份 mtime 都是 01:53:41）。补录内容（两份分别在第 94 行和第 101 行）：01:44 重跑的峰值 RSS 没有记录；唯一的记录是首跑的 peak_VmHWM 1,573,940KB，见 output/alpha/recon_eqinc/step_e_v41_regen.log 第 11–12 行，已核对属实；没有为了测内存重跑。

- 2026-10-18 02:01 ET [Arch] Beta 清单差异已闭环：f4eae3c7 为 01:15 初版，01:17 追加 .VOID 后为 1c76966b；最终 RECOVERY_MANIFEST_ZH.md=21ea5767…3d2，RECOVERY_INVENTORY_BETA_ZH.md=ec8fde6e…fb8（Arch 实测）。AUDITFIX 产出实测：recount json 5b5d4a95，scorecard md/.gen aca6059e；冻结件未变。
- 2026-10-18 02:08 ET [Arch] r5 复审：ARCH_RUN_AUTH_CS_PANEL_RESUMEFIX_v2.ok cc04d83d9889f8f4a3ead8a82bce0aa98d23ad94978635d12f1feb068c3ecfae；ARCH_RUN_AUTH_SELFTEST_SD1_COMMON.ok 7a0c1cdc54bf2b198a899382d55eb6bf41d507ad01044f800edc3e0594eda775；fix_sd1 r5：cs 11316ed4 sf aeb46679 sd 092330cc common 28fbb15d test 74a176e7 plan_cs 54552f4a plan_sd 9691b90e；D1a stdout 48a3da22。

- 2026-10-18 02:22 ET [Arch] SD1 r2 复审 docs/v2/ARCH_SD1_R2_REVIEW_ZH.md 73cb88ac53b96ed7c5905a216d26fe0ecd093e75141bb6f8b16e925f557c3561（P0=0 P1=0）。已签 docs/v2/eng_sd1/ARCH_SD1_TEST.ok 4975aac8ccb34b90e3ac05a3edddd38629ef523ef6d1e1156a12519a2cdabfdc（selftest，68 dep）；docs/v2/eng_sd1/ARCH_SD1_EXEC.ok eb3c35870e60fd418fcaa977aa695be2c211158185061d64f91ce7d76fa625e5（paper 对拍，out_tag r2_20261018_c4d2411c，须先审单测回执）。实测：execution.py 373fed30、__init__ bfdfa63c、ok_runner_pin c7805d9a 未动；execution_sd1 35b46c2b、tradability 4d684a48、delist_accounting 222b63ae、wb_sd1_books cadc065a、test 8305246b、runner c4d2411c、pit_static_check 3cfc1135；SD1_SHAS.txt 57eb6e40→621a7af4（02:15:21，仅注释与 v2 sha 变）；ok_runner_pin_v2 r2 6810b024（r1 a4b5dbd4 作废）。

- 2026-10-18 02:27 ET [Arch] v1.4 runner r2 复审 docs/v2/ARCH_V1_4_RUNNER_REVIEW_R2_ZH.md f9edf4a32d473eff07e8f4b30f79bec624d86ae7e0143d8594a34e7d27921a93（P0=0 P1=0 P2=4 P3=9）。实测：R 3df05b4b…8b10、combined 9e6d00c7…c335、E 13809851…bf7a、改动对照 e5b6d02d…497b、T 7176f974…95d3、D21 0a7d2183…2ef8e、D21 文档 744ede3d→8b7a29f0775de8e325a3105001d309cf40624221eb60b576d409536e75382753（ddd23ed4，仅第 3 行时间戳更正）；快照 R db8bdb8e、E 3d2e0533、改动对照 d9767ef0、D21 文档 744ede3d 均只读且逐位一致；冻结件 d921dd3f/0d47c52f/d075a2a6 未动；无 v1_4*/锁文件。已签 output/strategy_optimizer/core_x2/ARCH_RUN_AUTH_SELFTEST_v1_4.ok 33ef1df908249913f9fa76ef7de09c9a0d4384a8daf26eb3e27dfb15318469d8（selftest，仅合成数据，expires 2026-10-19T02:24:43-04:00）。v1.4/D21 运行 .ok 未签（等 Leo）。
