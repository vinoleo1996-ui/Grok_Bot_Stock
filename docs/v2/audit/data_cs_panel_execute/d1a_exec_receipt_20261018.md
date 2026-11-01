# D1a execute 回执（EXECUTE_v1.ok，r6c 代码 b9674c8b）

- 执行人：QuantLab Data；单进程；live=false，promotion_approved=false，strategy_promotion=false
- 时间（America/New_York）：T0=2026-10-18 05:18:26.844288081 EDT；结束 05:18:53.777460466 EDT；**exit 0**
- 命令：
  `cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 scripts/fix_sd1/build_cs_panel_v2_resumefix.py --arch-ok output/data/ARCH_RUN_AUTH_CS_PANEL_RESUMEFIX_EXECUTE_v1.ok --fixes none --execute`
  - 外层用 /usr/bin/python3 跑 subprocess，用 getrusage(RUSAGE_CHILDREN) 测峰值 RSS。
  - 解释器 /usr/bin/python3，与 .ok 中 interpreter=/usr/bin/python3 一致。
  - D1a 的参数取自脚本 usage（`--fixes none` 对应 D1a_fixesnone_check，加 `--execute` 为执行模式）。

## 前置核对（05:17:13–05:18:26 EDT，全部满足）
- 已通读 `docs/v2/ARCH_DATA_SD1_COMMIT_REVIEW_AND_EXECUTE_OK_ZH.md` 和 .ok，逐条遵守。只用了 EXECUTE_v1.ok，没有使用 v1、v2、v3、v4 或 v4a 的 .ok。
- .ok：`output/data/ARCH_RUN_AUTH_CS_PANEL_RESUMEFIX_EXECUTE_v1.ok`
  - sha256=f03357f19f087def6cd47716f34e7ae0fd093184a2fde7f31231357f13fe1a52 ✓
  - ok_revision=execute_v1_after_commit_b9674c8b_and_v4a_d3d4_review_9ee8e9d9；supersedes d5c326df…
  - signed_et=2026-10-18T05:16:02-04:00：不晚于 `date`（05:17:35 EDT）✓
  - expires_et=2026-10-19T16:00:00-04:00：未到 ✓
  - forbid_window 为 10-19 16:40–18:40，当前不在窗口内 ✓
  - allow_execute=true，allow_full=true，allow_dryrun=false
  - authorized_modes=execute
  - authorized_steps_execute=D1a_fixesnone_check,D1b_resume_execute,D2_suspend_flags,D3D4_stock_delisted
  - step_gate：每一步需要 Arch 书面放行。本次只做 D1a。
  - 包含 expected_face_value_recategorised=000861.SZ,002505.SZ,002509.SZ,600297.SH 和 expected_unknown_needs_source_count=56；allow_d3d4_expectation_keys=true ✓
  - git_commit_fix_sd1=b9674c8b…；git_commit_receipt_sha256=6b46951d…
- 代码 pin 7 项：工作区、`git show b9674c8b:<path>` 和 .ok 三处一致 ✓
  - 362e3239、903e64ef、6e2e1273、6b8fd033、34e46899、542dd136、7dbcf5d3
- 数据 pin 14 项与 .ok 一致 ✓
  - mask c5433e80
  - v1 cs_panel 2018–2026：035d1f60 / b843a7bc / e25a7e59 / bea54e54 / ad188dda / 6acf163e / 6d238ee3 / 39568253 / 4608d8bc
  - float_mktcap 346d0dda；sw_l1 89d4afa3；stock_delisted_v1 90c8934d；namechange_all 6b81ee0b；delisted_daily e0db051e
- scripts/fix_sd1：`git status --porcelain --ignored` 输出为空，没有 __pycache__ 或 *.pyc ✓（运行前后都检查过）
- 4 个输出目标（panel_cache_v2_fixesnone、panel_cache_v2_resumefix、data/v2/suspend_flags、data/v2/ref/stock_delisted_v2*）及其 staging 运行前都不存在 ✓
- MemAvailable ≥ 2GB ✓
  - 11,187,308 kB（05:17:35）
  - 11,381,820 kB（05:18:19 ps 留证时）
  - 11,395,644 kB（T0 前一刻）
  - 运行后 10,630,840 kB
- 进程：`pre_d1a_exec_ps_20261018.txt`（sha256=30a1d551be52c42109e4a50837f7a885aed08a4d6c356ceaf136000d1349da3b）
  - 存活判断只读 /proc/<pid>/stat 和 /proc/*/cmdline，没有用 kill -0。
  - 没有 nightly_update、tier3_daily_snapshot、relay_outage_backfill、nightly_daily_pull、tier1_pull、adj_factor、bars_materialize、research/、pytest、cmc 或 leaf 进程 ✓
  - /proc/94403/stat 不存在，说明 94403 已退出 ✓
  - 94322：state=**T**（Tsl）

## 94322 SIGSTOP
- 详见 `stop_94322_20261018.md`（sha256=f50971c33d9a1f387b5701b7294f3fefdc315af716a5c3db15baaf8dd1e06623）。
- 停止时刻：**2026-10-18T05:17:56.964027-04:00**。在两次 fund_portfolio_dh 写入之间停的：新文件大小稳定，且没有打开的 fd。
- 停前写入的最后一个文件：`data/v2/tushare_raw/fund_portfolio_dh/20240630/000569000.parquet`
  - 17,558 B；sha256 b55ff439c0c0320f754706c398b7cdef00291d7fd4c77f3e736d05bc73086aa0
  - 1000 行，可完整读取
- 6 秒复核：没有新的写入，没有 tmp 或半写入的文件。
- 运行后 94322 仍为 T。没有 SIGCONT，也没有 kill。

## 门禁原文
```
RUN_CONDITION_MATCHES []
GATE_PASS step=D1a_fixesnone_check mode=execute ok_sha256=f03357f19f087def6cd47716f34e7ae0fd093184a2fde7f31231357f13fe1a52
```
- 末行：`COMMITTED /workspace/QuantLab/output/ai_factory/panel_cache_v2_fixesnone`
- 没有 VOID；output/ai_factory 下没有 VOID 或 staging 残留。

## 统计：与 v3 dry-run D1a 回执逐项对比
| 年 | 行数 v3 dry | 行数 exec | rows_v1 | frame_equals v3/exec | table_equals v3/exec | bytes_equal | 写出 sha = v1 sha | rss_mb v3/exec |
|---|---|---|---|---|---|---|---|---|
| 2018 | 783,166 | 783,166 | 783,166 | true/true | true/true | true | 035d1f60 = v1 035d1f60 | 703/692 |
| 2019 | 846,470 | 846,470 | 846,470 | true/true | true/true | true | b843a7bc = v1 b843a7bc | 877/894 |
| 2020 | 880,720 | 880,720 | 880,720 | true/true | true/true | true | e25a7e59 = v1 e25a7e59 | 957/966 |
| 2021 | 983,990 | 983,990 | 983,990 | true/true | true/true | true | bea54e54 = v1 bea54e54 | 1025/1054 |
| 2022 | 1,087,168 | 1,087,168 | 1,087,168 | true/true | true/true | true | ad188dda = v1 ad188dda | 1077/1067 |
| 2023 | 1,163,879 | 1,163,879 | 1,163,879 | true/true | true/true | true | 6acf163e = v1 6acf163e | 1153/1184 |
| 2024 | 1,198,136 | 1,198,136 | 1,198,136 | true/true | true/true | true | 6d238ee3 = v1 6d238ee3 | 1212/1210 |
| 2025 | 1,204,295 | 1,204,295 | 1,204,295 | true/true | true/true | true | 39568253 = v1 39568253 | 1231/1251 |
| 2026 | 924,485 | 924,485 | 924,485 | true/true | true/true | true | 4608d8bc = v1 4608d8bc | 1231/1251 |

- 结论：
  - 行数、rows_v1、frame_equals、table_equals 9 年全部与 v3 dry-run 相同。
  - execute 新增的字段 bytes_equal=true 9/9：写出的每一年 parquet 与 v1 逐字节相同（sha 等于数据 pin）。
  - 唯一差异是 rss_mb（运行噪声）。

## 输出（已 commit 到最终目录 `output/ai_factory/panel_cache_v2_fixesnone/`）
| 路径 | 字节 | sha256 |
|---|---|---|
| output/ai_factory/panel_cache_v2_fixesnone/RECEIPT_D1a_fixesnone_check.json | 3900 | 21db8530526897286329a828c974f4d7c8fc879bccda33492b3bee62ecb69212 |
| output/ai_factory/panel_cache_v2_fixesnone/cs_panel_2018.parquet | 14886620 | 035d1f60d90911d8c8988b386eb8b845cb3cc0fbe9826af4f2ca7cd19222d8a9 |
| output/ai_factory/panel_cache_v2_fixesnone/cs_panel_2019.parquet | 15815449 | b843a7bc00fc383d016f407a10d910131eeaadf0345acd5c373b67da7cc3f857 |
| output/ai_factory/panel_cache_v2_fixesnone/cs_panel_2020.parquet | 16889239 | e25a7e59fe587b921760da751c2fb330b771847fab9dd56a2fdfa0887eee8904 |
| output/ai_factory/panel_cache_v2_fixesnone/cs_panel_2021.parquet | 19330078 | bea54e540332248165239a3407f85da248d38f0b75aaade25f041302835dead8 |
| output/ai_factory/panel_cache_v2_fixesnone/cs_panel_2022.parquet | 21790056 | ad188ddaf9807ae343bda6db8d53aa20737e4778f66bda7810faa042d699fc5e |
| output/ai_factory/panel_cache_v2_fixesnone/cs_panel_2023.parquet | 23341046 | 6acf163e12fac1aacfe2188ebe9e0f2df4f2abff5ad95d5907c88296bc302ab5 |
| output/ai_factory/panel_cache_v2_fixesnone/cs_panel_2024.parquet | 23987599 | 6d238ee3b2429edc1a5f70d36c1aea48bda70a9031fef54e987a255b11b7fc7b |
| output/ai_factory/panel_cache_v2_fixesnone/cs_panel_2025.parquet | 24481584 | 39568253199713f28305409b512d380340d0d0c915464ee8a1c0020611db331f |
| output/ai_factory/panel_cache_v2_fixesnone/cs_panel_2026.parquet | 18995033 | 4608d8bc1eec7109a85f7b8018ab9a2f4d0fdcd1f36b4d1faefdc9714ecb2868 |
| output/ai_factory/panel_cache_v2_fixesnone/ind_names.csv | 345 | 1ce867127690040bf04b6c8ad5bc16a6d99a396d2ac431893a21eef7892a902a |
| output/ai_factory/panel_cache_v2_fixesnone/manifest.json | 6647 | 1799009acb8c38e78e355e1942ecca1a980448febad758b8896267eadd81253e |

- ind_names.csv 的 sha 与 v1 一致：ind_names_sha256 = ind_names_v1_sha256 = 1ce86712…
- manifest：`output/ai_factory/panel_cache_v2_fixesnone/manifest.json`，sha256=1799009acb8c38e78e355e1942ecca1a980448febad758b8896267eadd81253e
  - step=D1a_fixesnone_check，mode=execute，fixes=none，status=PASS
  - prev_receipt_sha256=null（D1a 是第一步）
  - common_sha256=542dd136…
  - raw_file_list_sha256=d8e00a96f08dd3370281ad53455c2abc7092241d74d75420556b283cacad1c57
  - live、promotion_approved、strategy_promotion 均为 false
- 收据 `RECEIPT_D1a_fixesnone_check.json`：sha256=21db8530526897286329a828c974f4d7c8fc879bccda33492b3bee62ecb69212；manifest_sha256=1799009a…（与上面一致）；status=PASS
- **P3-9 raw_content**（manifest 与收据中的值逐字相同）：
  `{"cutoff": "20261014", "n_files": 4256, "raw_content_sha256": "4d03c9836464b7793fc72b4f2c1cdd885f151cda76c19ab8a22540ad89f1a2be"}`
  - D1b 和 D2 的 execute 回执必须与此逐字一致。
- 说明：manifest 中 sessions_walked=0，first_session_forced_no_resume=null。
  - 原因：`--fixes none` 不走 resume_flags_year（脚本第 103、124 行只在 FIX=="resume" 时调用），ResumeState.sess_idx 初值为 -1，所以 -1+1=0。
  - 与 D2 天数的核对（Arch r4 P3-3）针对的是 D1b。
- manifest 中 run_conditions.ps_snapshot 里有 94322（脚本没有记录它的状态，ps 留证中为 T）和 80415 `python3 -X utf8 server.py`（非 8787 uvicorn，不在 forbid 列表中）。

## 峰值 RSS
- 1,281,432 KB（约 1251 MB）。
  - ≤ .ok rss_cap_mb 1450 MB，也低于 1.5GB 上限 ✓
  - v3 dry-run 为 1,260,656 KB。

## stdout 对比（v3 dry-run d1a_stdout_v3_20261018.txt）
- stdout：`d1a_exec_stdout_20261018.txt`，sha256=cf17fbd96f5b1851546e88ff6fe20f0120cee985a4ff78f48bb0558e4b4374e0
- 原始 diff：`d1a_exec_rawdiff_vs_v3_dryrun.txt`，28 行，sha256=7d3b418aebaa5f8b41e3963796e2d721f4840520e3ef75a7ddd9e8725e2f77c8。差异项：
  1. RUN_CONDITION_MATCHES：v3 为 94403 T allowed_stopped，exec 为 []。
  2. GATE_PASS：mode 从 dryrun 变为 execute，ok_sha 从 dac5f6dd 变为 f03357f1。
  3. 9 个年度行：rss_mb 不同，并新增 sha256、v1_sha256、bytes_equal 三个字段。
  4. 末行：v3 为 DRY-RUN PASS，exec 为 COMMITTED。
  5. 包装行的标签和 RSS 数值。
- 规范化 diff：`d1a_exec_normdiff_vs_v3_dryrun.txt`，**0 行**，sha256=e3b0c442…（空文件）。
  - 规范化规则：去掉 RUN_CONDITION_MATCHES 和 WRAPPER_EXIT 行；ok_sha256 换成 <OK>；mode 换成 <MODE>；rss_mb 换成 <RSS>；去掉 execute 新增的 sha256、v1_sha256、bytes_equal 字段；去掉 DRY-RUN PASS 和 COMMITTED 末行。
  - 剩余行（9 年的 rows、rows_v1、frame_equals、table_equals）逐字一致。

## find -newermt T0 写入核对（运行后执行）
- 命令：`find data/v2 output ref docs scripts -newermt '2026-10-18 05:18:26.844288081' -type f -not -path 'docs/v2/audit/data_cs_panel_execute/*'`
- 按目录统计：

| 目录 | 文件数 |
|---|---|
| output/ai_factory/panel_cache_v2_fixesnone | 12（全部是 D1a 输出） |
| data/v2/tushare_raw/fund_portfolio_dh | **0**（94322 已停） |
| data/v2 其他目录 | 0 |
| output/data | 0 |
| docs（不含本回执目录） | 0 |
| scripts | 0 |

- 仓库根目录下没有 ref/。
- 结论：只有 D1a 的输出被写入 ✓

## 未做
- 没有 D1b、D2、D3D4。
- 94322 没有 SIGCONT，保持 T。
- 没有动补数队列和 moneyflow，没有启 8787，没有发消息，没有 git 操作。
