# Arch 复审 r5 · Data cs_panel 复牌重建（SD1 D1–D4）

- 时间：2026-10-18 02:07 ET；审查人：QuantLab Arch；live=false，promotion=false
- 结论：**放行四步 dry-run + 合成单测**。P0=0，P1=0，P2=1，P3=5。execute 未授权，需另签 .ok。
- Arch 本轮没有运行任何 Data 脚本或单测，只做了 sha 计算、静态阅读，并用 AST 只取常量重现 parse_run_auth 的校验逻辑（没有 import sd1_common）。

## 1. D1a dry-run 回执核对
- stdout docs/v2/audit/data_cs_panel_d1a_dryrun/d1a_dryrun_stdout_20261018.txt sha=48a3da22…c79ab，实测一致。
- GATE_PASS 行 ok_sha256=3a1bb537（v1.ok）。2018–2026 九年 rows=rows_v1，v1_frame_equals 和 v1_table_equals 都是 true。峰值 rss_mb=1241（≤1500），末行为 "DRY-RUN PASS: nothing written"。
- 四个目标路径（panel_cache_v2_fixesnone、panel_cache_v2_resumefix、data/v2/suspend_flags、stock_delisted_v2.parquet）都不存在，也没有 staging 或 VOID 残留。02:00 之后 output/、data/ 下的新文件都不属于 SD1，其中 fund_portfolio_dh 是另一个抓数任务写的。

## 2. sha 核对（7/7 一致）
| 文件 | sha256 |
|---|---|
| scripts/fix_sd1/build_cs_panel_v2_resumefix.py | 11316ed4cb5fe37f9055006386709924853ad710f9d1031efcd79f90351be094 |
| scripts/fix_sd1/build_suspend_flags_v2.py | aeb46679a5c015c52498266cdf91b53b4ff61c61ab1deb3efad21860c29db988 |
| scripts/fix_sd1/build_stock_delisted_v2.py | 092330cc6b09457a92b71c89e77ee7dd912a76c8675325b5557085228da1f144 |
| scripts/fix_sd1/sd1_common.py | 28fbb15de59103b8b7e87c68e9477b8f037383a617c1bffc54a6808928921263 |
| scripts/fix_sd1/test_sd1_common.py | 74a176e7d3e2727afa2ce86578b7b4a02c17a997cc0277499827844b8432c502 |
| docs/v2/DATA_CS_PANEL_RESUME_REBUILD_PLAN_ZH.md | 54552f4a6c438098d7ce52df145ddd8928466d24d326183cd736acf7bb18a466 |
| docs/v2/DATA_SUSPEND_DELIST_FIX_PLAN_ZH.md | 9691b90e1364cbc920c7c145098caa2be205127cab584f1a4d1084fba1b5d378 |
另外，build 脚本硬编码的 COMMON_SHA256 也是 28fbb15d，与实测一致。19 个数据 pin 沿用 v1.ok 的值，重新实测全部一致。

## 3. 代码审查
- **P2-1 classify_restore**：纯函数，判定顺序如下：先看是否为候选；carry 已知时记 known；否则 prev_traded_date 为空且属于种子集，记 unknown_pre_data（year>2020 时 raise）；为空、不属于种子集，且是 resume，则 raise；为空、不属于种子集、是 intraday，记 unknown_first_trade_in_data；其余记 unknown_no_normal_session。三类 unknown 都不补回（carry 为 False/False）。调用方遇到 ValueError 会 ST.void。逻辑正确。
- **P2-2**：每年都输出 unknown_by_event_x_label、unknown_by_label 和 5 个样本，通过。
- **P2-3**：check_order 在 dry-run 时只跳过前序 RECEIPT 比对，"后序输出不得存在"的检查在跳过之前已经执行；raw_pin_start 也只在 execute 时比对前序。execute 路径没有变化，通过。
- **allow_full=false 能否真正挡住 execute**：gate() 第一步 parse 之后紧接着 check_mode，--execute 要求 allow_full=true，否则直接拒绝；allow_smoke 必须为 false。三个 build 脚本都通过 C.gate 进入。通过。
- **dry-run 是否零写入**：Staging 只在 execute 时 mkdir；dry-run 下 void 只抛异常、不写 VOID 文件；ind_names、parquet、manifest、RECEIPT 的写入都在 `if EXEC` 里。通过。
- **单测门禁**：enforce(modes=["selftest"], deps={sd1_common}) 和自查（scope、allow_real_data=false、out_dir 为 mkdtemp 或 /tmp/）都在 `import sd1_common` 之前。测试只用合成数据，只在 tempfile.mkdtemp 下写 t.ok，结束时 rmtree。通过。

## 4. 发现
- **P2-1（流程）**：02:04 的 D1a dry-run 是在 v1.ok 下跑的，跑的是旧代码（common 2e4c4131…），5 个脚本的 mtime 是 02:04–02:05。它只能证明旧代码，不能作为 r5 的证据。须在 v2.ok 下重跑 D1a dry-run。
- **P3-1（不变式"2021 起 pre_data=0"）**：这是 fail-closed 的保护，方向正确，但存在合法触发的可能。r4 探针显示 2019 年纯种子类 unknown 有 138 行，r3 显示 2020 年还有 2 行，说明确实有跨 2018-01-02 的长停牌；如果某只种子股从 2017 年以前一直停到 2021 年以后首次成交，就会被判 VOID。裁定：保留 VOID，不静默放行。一旦触发，Data 须逐条给出代码、首个 S 日期、mask 连续停牌段和复牌日，由 Arch 决定是否改为披露口径，并需另出 .ok。
- **P3-2**：解析器 FIXED 要求 version=cs_panel_resumefix_v1，所以 v2.ok 里的 version 仍写 v1，修订号写在 ok_revision=v2_r5_dryrun_only。expires_et 两套门禁（sd1 gate 和 ok_runner_pin）都不检查，Data 须自查是否过期；建议 Eng 在下一版门禁里补上这项检查。
- **P3-3**：单测 import 的 scripts_eng/ok_runner_pin.py 没有被钉。selftest .ok 里记录了 gate_ok_runner_pin_sha256=c7805d9a，仅作参考，代码不检查。
- **P3-4**：不变式"不属于种子集却判 resume"在 ResumeState 构造上不可达（候选集必须 ∈ has_traded），只能当防御用，不能当证据。
- **P3-5**：r4 审过的版本没有存快照，本轮只能通读 r5 全文。今后改代码前，请先把旧版本归档到 docs/v2/audit/。

## 5. 已签 .ok
- output/data/ARCH_RUN_AUTH_CS_PANEL_RESUMEFIX_v2.ok sha256=cc04d83d9889f8f4a3ead8a82bce0aa98d23ad94978635d12f1feb068c3ecfae
  - allow_dryrun=true；allow_full、allow_execute、allow_smoke、allow_selftest、allow_diagnostic、allow_disclosure_only 均为 false。
  - 授权步骤仅限 D1a、D1b、D2、D3D4 的 dry-run，authorized_steps_execute=none。
  - expires_et=2026-10-19T02:07:04-04:00；supersedes 3a1bb537。
  - 用 AST 重现解析器校验：必填项齐全，FIXED 一致，not_authorized 覆盖完整，6 个代码 pin 和 19 个数据 pin 实测全部一致。
- output/data/ARCH_RUN_AUTH_SELFTEST_SD1_COMMON.ok sha256=7a0c1cdc54bf2b198a899382d55eb6bf41d507ad01044f800edc3e0594eda775
  - scope=selftest；allow_selftest=true，allow_real_data=false，其余 allow_* 均为 false。
  - out_dir=mkdtemp；expires_et=2026-10-19T02:07:04-04:00。
- 运行顺序：先跑单测；然后在 v2.ok 下依次跑 D1a、D1b、D2、D3D4 的 dry-run，每步都用 `PYTHONDONTWRITEBYTECODE=1 nice -n 10`、单进程、串行。每步回执先交 Arch 审；execute 须另签 .ok。
