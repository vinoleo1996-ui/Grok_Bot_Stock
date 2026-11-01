# Runner archive — OPTIMIZER Core v1.3 (written 2026-10-18 00:38 ET (mtime 00:38:38; git d2ed883e 00:38:45), Strategy; Arch P2-3)
Archived copies are frozen; do not edit or run them. Live file: `research/optimizer_core_x2_run.py`.
Combined sha = sha256 of "research/optimizer_core_x2_run.py=<sha>\nresearch/optimizer_core_v1_1.py=<sha>\nresearch/optimizer_lambda_calib_sealed.py=<sha>\n".

| file | sha256 | role |
|---|---|---|
| optimizer_core_x2_run.29b38cf8.py | 29b38cf880ebb7c3c648b1f5a7936bedd14468d2ad472f9da96f087099bfc40a | **Produced the canonical v1.3 weights** (`core_x2/core_*_{60w,100w}.parquet`, `_ckpt_v1_3_poolind/` 107 pkl, meta, CSVs), full run 2026-10-18 00:20:04–00:27:01 ET. Arch-reviewed (ARCH_CORE_v1_3_RUN_AUTH_REVIEW_ZH.md). Combined sha 5e7d597b91440cb145b2124df91cdb7e12008ee0f3f16cae9f025570f665183a. Source: /tmp/optimizer_core_x2_run.py.pre_smokefix (sha verified). |
| optimizer_core_x2_run.f688e703.py | f688e7030455df684b233c76ad70adb8172d1fb8b0e5723bd723faccf15b60c9 | Smoke-isolation fix (Arch conditional PASS, ARCH_SMOKE_ISOLATION_FIX_v1_3_REVIEW_ZH.md). Combined f03387d6d7759272fb53f0fabfd8ce01c22a72f674b00f88cdd84f8b67f307fd. Ran only the VOID 00:32 ET smoke (violation; `_smoke_v1_3/_VOID_ckpt_20261018_0032/`). Produced no canonical output. |
| optimizer_core_x2_run.b6238254.py | b623825457efb2a3ce22c450d12e87624dc8f5642ad310e4ecc869362c64cbb4 | Current live runner: P2-1 structured run-auth (RUN_AUTH_FORMAT.md), P2-2 asserts -> SystemExit, P3 ckpt version check. Combined 51f54743a2ed1546d0f56744676da6d96e94ed46029eb67950dfe807bfbd87aa. **Never executed as a runner** (unit tests of loader/auth functions only). Pending Arch review. |
| optimizer_core_v1_1.b500c21b.py | b500c21bca955ea8c8667808f412e734a5c70dae9b20823e5b890d6a5938067e | Solver helper, unchanged across all three runners. |
| optimizer_lambda_calib_sealed.875daca9.py | 875daca9cfbb861cdf685a9f7ff836f1dc18fa80eccf2cf238baccaaf40d3b9c | Constants/prepare_day, unchanged across all three runners. |
| test_guards_v1_3_b6238254.py / .out.txt | — | Loader + run-auth unit tests (no solver); expects pkl copies in /tmp/ldtest2. Output identical under `python -O`. |

- 2026-10-18 01:59 ET：strategy_hiliq_capadv_b4_x2.3f7f75c3.py = hx2 改第 676 行前原样（sha 3f7f75c3…532c2）。Arch 01:57 放行（纸面 import 闭包 95 文件不含 hx2）。新 sha 4f952de2d2fdf9e30a605916aeb88bc3751afd738264a644640fe2e89ce03c1f；只改 alpha_diag_note_zh 字符串，指向 ALPHA_EQUITY_SIGN_RECON_20261018_ZH.md §7；未重跑 hx2.main。

- 2026-10-18 02:01 EDT（Strategy，r2 修改前快照；Arch 审查 ARCH_V1_4_RUNNER_REVIEW_ZH.md db781708）：
  - optimizer_core_x2_run_v1_4.db8bdb8e63da01b3e759a19e317a870c7bbd356fb02724e5df4501eb753ba602.py = v1.4 runner r1 原样（sha db8bdb8e63da01b3e759a19e317a870c7bbd356fb02724e5df4501eb753ba602）。从未执行，只 py_compile。
  - v1_4_snapshot_equiv_check.3d2e05333df033329b03012d99d939fa2c69736be27820198234dccf7d67a1b3.py = 等价性脚本 r1 原样（sha 3d2e05333df033329b03012d99d939fa2c69736be27820198234dccf7d67a1b3）。从未执行，只 py_compile。
  - 改动对照 r1 原样存于 docs/v2/audit/snapshots/STRATEGY_V1_4_RUNNER_CHANGES_ZH.d9767ef0c77014633fc892793a41232da90a106e7dd524fc718091ae9318c6fc.md（sha d9767ef0c77014633fc892793a41232da90a106e7dd524fc718091ae9318c6fc）。

- 2026-10-18 02:32 EDT（Strategy，r3 修改前快照；Arch 复审 ARCH_V1_4_RUNNER_REVIEW_R2_ZH.md f9edf4a3；主 Agent CLARIFY-2 改向）：
  - optimizer_core_x2_run_v1_4.3df05b4b85a3caec050810f1e4eac4035935ef6d7704b7a88df56d079e628b10.py = v1.4 runner r2 原样（提交 246aa99a）。从未执行，只 py_compile。
  - v1_4_snapshot_equiv_check.1380985102b598f16e111bf0b62cbc04e105aa00ad6cfeb3365bbf7ce711bf7a.py = 等价性脚本 r2 原样（246aa99a）。从未执行。
  - test_v14_synthetic.7176f97477b5f9aaf6b6aac8a9b53333a455c0f3e9441f65249a8834882195d3.py = 合成单测 T r1 原样（246aa99a）；主 Agent 按 Arch selftest .ok 33ef1df9 跑过一次（据主 Agent：38 项通过）。Strategy 未运行。
  - optimizer_core_v1_3_basisC_recalc_d21.0a7d21835788fb847c88dee13d0b52fdfe65d6de88fdcce1fccfb8b87fd2ef8e.py = D21 r1 原样（b975819e）。从未执行。
  - 文档快照：docs/v2/audit/snapshots/STRATEGY_V1_4_RUNNER_CHANGES_ZH.e5b6d02d5211dd0fede9555fc651f46dc505ae66de0de62a83e23c5adbc3497b.md、STRATEGY_D21_V1_3_BASISC_RECALC_ZH.8b7a29f0775de8e325a3105001d309cf40624221eb60b576d409536e75382753.md。

- 2026-10-18 02:51 EDT（Strategy，r4 修改前快照；Arch 对 r3 待裁定点的裁定 + 主 Agent CLARIFY-2 落盘 85e843cd）：
  - optimizer_core_x2_run_v1_4.94643e27741835d703440d64d906f4c130f4763a522412a058f5fbd879454ca0.py = R r3 原样（ce45f3da）。从未执行。
  - test_v14_synthetic.2ef7277a1d2ae210bc66cfa176c330938f68b4c8023c6c870bda870e4206d966.py = T r2 原样（ce45f3da）。从未执行。
  - optimizer_core_v1_3_basisC_recalc_d21.86c6f7bb5a04030a7970e59fa5074fd03c1ef8c2f1285153dc57e87509f2bc3c.py = D21 r3 原样（ce45f3da）。从未执行。
  - 文档快照：docs/v2/audit/snapshots/STRATEGY_V1_4_RUNNER_CHANGES_ZH.d72808fb273617bbda8cc3882796bc7d760d3f064cf7fe34da7ac001876d4d59.md、STRATEGY_D21_V1_3_BASISC_RECALC_ZH.043911da2bd2c564a879947f763e61a0068d226c5811b1d6e95b08387ea3fec5.md。

- 2026-10-18 03:05 ET：test_v14_synthetic.d281916d….py = Arch R3/R4 复审 P1-1 修改前 T 原样（sha d281916d37e81523f12652d9c80a4f8fc3307dfc430210efa347e9c6ed6009d9）；只在 DEPS 中加 d21 一行，新 T f1c1a89f84345266709f3a039c6f9b15151abb3fdb117fe2df19ecf6e3483a7b；仅 py_compile，未运行。
