# D2_suspend_flags execute 回执（EXECUTE_v1.ok，r6c 代码 b9674c8b）

- 执行人：QuantLab Data；单进程；live=false，promotion_approved=false
- 放行依据：`docs/v2/ARCH_DATA_SD1_EXEC_D1B_REVIEW_ZH.md`（Arch 05:25:59 EDT 书面放行 D2，已通读）
- 时间（America/New_York）：T0=2026-10-18 05:26:47.233856328 EDT；结束 05:27:53.687232929 EDT
- **exit 0**
- 命令：
  `cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 scripts/fix_sd1/build_suspend_flags_v2.py --arch-ok output/data/ARCH_RUN_AUTH_CS_PANEL_RESUMEFIX_EXECUTE_v1.ok --execute`
  - 参数依据脚本 usage：`--arch-ok PATH [--execute]`。D2 没有 --fixes，这与 v3 dry-run 原命令一致，只是加了 --execute。
  - 外层用 /usr/bin/python3 跑 subprocess，用 getrusage(RUSAGE_CHILDREN) 测峰值 RSS。

## 前置核对（05:26:26–05:26:47 EDT，全部满足）
- .ok：`output/data/ARCH_RUN_AUTH_CS_PANEL_RESUMEFIX_EXECUTE_v1.ok`
  - sha256=f03357f19f087def6cd47716f34e7ae0fd093184a2fde7f31231357f13fe1a52 ✓
  - signed_et 05:16:02 不在未来（`date` 为 05:26:39）✓
  - expires 2026-10-19T16:00 未过 ✓
  - 当前不在 forbid_window 内 ✓
- 代码 pin 7 项：工作区、`git show b9674c8b:<path>` 与 .ok 三方一致 ✓
- 数据 pin：sd1_common.PIN_DATA 共 **15 项**（mask 1、v1 cs_panel 9、float_mktcap、sw_l1、stock_delisted_v1、namechange_all、delisted_daily），全部与 .ok 一致 ✓
  - 更正：D1a、D1b 回执里写的"14 项"是笔误，当时脚本实际核对的也是这 15 项。
- scripts/fix_sd1：`git status --porcelain --ignored` 为空，没有 __pycache__ ✓（运行前后都查过）
- 目标路径 data/v2/suspend_flags 及其 staging/VOID 运行前不存在 ✓
- data/v2/ref/stock_delisted_v2* 运行前不存在 ✓
- D1b 收据 sha256=2edd6e26… ✓
- MemAvailable：
  - 11,176,060 kB（ps 留证时）
  - **运行前 11,229,248 kB**
  - **运行后 11,209,164 kB**
  - 均 ≥ 2GB ✓
- 进程留证：`pre_d2_exec_ps_20261018.txt`（sha256=dc02c693ebc01f5ee85b7066a888dade39f0de66d3977fc462cbfa6ed737fde1）
  - 只读 /proc 判断，没有用 kill -0
  - 没有 nightly_update、tier3_daily_snapshot、relay_outage_backfill、daily_pull、tier1_pull、adj_factor、bars_materialize ✓
  - 94403 不存在 ✓
  - 94322 state=**T** ✓
  - 80415 server.py 是 Web 看板，Arch 已确认不在禁止名单内
- 运行后 94322 仍为 T。没有 CONT，也没有 kill。

## 门禁与提交
```
RUN_CONDITION_MATCHES []
GATE_PASS step=D2_suspend_flags mode=execute ok_sha256=f03357f19f087def6cd47716f34e7ae0fd093184a2fde7f31231357f13fe1a52
COMMITTED /workspace/QuantLab/data/v2/suspend_flags
```
- 没有 VOID；data/v2 下没有 staging 或 VOID 残留。

## P3-9 raw_content
- manifest：`{"cutoff": "20261014", "n_files": 4256, "raw_content_sha256": "4d03c9836464b7793fc72b4f2c1cdd885f151cda76c19ab8a22540ad89f1a2be"}`
- RECEIPT_D2 JSON：`{"cutoff": "20261014", "n_files": 4256, "raw_content_sha256": "4d03c9836464b7793fc72b4f2c1cdd885f151cda76c19ab8a22540ad89f1a2be"}`
- 断言：以下五者按 dict 比较全部相等，结果 **True** ✓
  - D2 manifest
  - D2 收据
  - D1a 收据
  - D1b 收据
  - 基准值
- 另外，脚本 raw_pin_start 在 execute 时会和 D1b 收据比对，也通过了。
- 三步（D1a、D1b、D2）的 raw_content 逐字一致。

## days_walked
- manifest：days_walked=**2128**
  - cutoff_date=20261014
  - excluded_after_cutoff=["20261015","20261016"]
- 与 D1b 的 sessions_walked=2128 相同 ✓（Arch r4 P3-3）
- D1b 回执中按规则只读统计的值 2128 也得到确认。

## 统计（execute stdout 与 v3 dry-run 对比；并从输出 parquet 只读复核）
- 方法：把 stdout 的统计 JSON 整体与 v3 dry-run 逐键比较。除 rss_mb（275 对 274）外，**全部键都相同**。
- 下表"输出 parquet"一列，是对 `suspend_flags_v2.parquet` 只读重算的结果。

| 项 | 预期 | v3 dry-run | execute stdout | 输出 parquet |
|---|---|---|---|---|
| 总行数 | 111,480 | 111,480 | 111,480（table_rows 111,480） | 111,480 |
| bj_resume_dropped_missing_row_only | 12,134 | 12,134 | 12,134 | —（被丢弃的行不在输出里） |
| is_resume_day | 5001 | 5001 | 5001（by_year 合计） | 5001 = 非 BJ 4986 + BJ 15 |
| BJ 保留的复牌行 | 15 | 15 | 15 | 15（resume_evidence 全为 R） |
| without_R（非 BJ） | 35 = 24 gap_S + 9 none + 2 S_prev | 35 | 35（R 4966 / gap_S 24 / none 9 / S_prev 2） | 35（is_resume_day 行的 resume_evidence：R 4966 / gap_S 24 / none 9 / S_prev 2） |
| conflict_v1 | 5980 | 5980 | 5980（by_year 合计） | 5980（非 BJ 5948 + BJ 32） |
| 非 BJ is_resume_day 逐年 2018–2026 | 1286/563/542/518/455/304/318/559/441 | 同左 | 同左 | 同左（合计 4986） |

- 其余项与 v3 一致：
  - fullday_but_traded=2
  - R_without_resume=383
  - conflict_v1_by_class：R/nointra 4939、S/intra 1001、R|S/intra 38、S/nointra 1、R|S/nointra 1
  - first_session_forced_no_resume=20180102
- 涉及代码数（只读）：ts_code 共 **3159** 个，其中非 BJ 2881、BJ 278。
  - 有 is_resume_day 的代码 2141 个。
  - 非 BJ 行 67,532，BJ 行 43,948。
  - 日期范围 2018-01-02 至 2026-10-14。
- 逐年行数：42979 / 5916 / 9668 / 11115 / 19254 / 12083 / 3732 / 4037 / 2696，与 v3 一致。
- 列（23 列）：instrument_id、ts_code、trade_date、suspend_type_raw、suspend_timing、halted_fullday、intraday_halt、intraday_halt_timing、resume_announced、is_resume_day、vol、amount、traded、prev_traded_date、halt_sessions、tradestatus_v2、tier1_v1_tradestatus、resume_evidence、conflict_v1、available_at_open、available_at_close、build_version、promotion_approved
  - promotion_approved 全为 False（True 计数 0）。

## 输出（已 commit 到 `data/v2/suspend_flags/`）
| 路径 | 字节 | sha256 |
|---|---|---|
| data/v2/suspend_flags/RECEIPT_D2_suspend_flags.json | 2291 | 06d06a792103abb69cc12aa2ba71932d202da50d20dfc94a41093656ee49a4c2 |
| data/v2/suspend_flags/manifest.json | 7539 | d26f9090d65da58c568ad01481c30b5cc4884afc6bdc222dbc057be3d2019f27 |
| data/v2/suspend_flags/suspend_flags_v2.parquet | 518998 | ac5c10fde28a5dfbea10b755a2b79df1fc876690c1c7d7aebf5134f53a447377 |

- manifest.json：sha256=d26f9090d65da58c568ad01481c30b5cc4884afc6bdc222dbc057be3d2019f27
  - step=D2_suspend_flags；mode=execute；status=PASS
  - join_key=[instrument_id, trade_date]
  - raw_file_list_sha256=379d60b3d8b9f4786e2ecc4448231df09373fc2380cfba226c11ea083b49686e
  - sha256=ac5c10fd…（与 parquet 一致）
  - live=false；promotion_approved=false
- RECEIPT_D2_suspend_flags.json：sha256=06d06a792103abb69cc12aa2ba71932d202da50d20dfc94a41093656ee49a4c2
  - status=PASS；sha256=ac5c10fd…
  - manifest_sha256=d26f9090…（与 manifest 一致）
  - **ok_sha256=f03357f1…，与 D1a、D1b 相同** ✓
  - **prev_receipt_sha256=2edd6e2614c4aec7f9fa229626e496d96d21f467bc6fc9615dfc134e327472a9，即 D1b 收据的 sha** ✓
- 说明：D2 的 raw_file_list_sha256（379d60b3）与 D1a、D1b 的（d8e00a96）不同。D2 按 days ≤ CUTOFF 列出 daily 文件再加 suspend_d，D1 列出的是全部 daily 和 suspend_d 文件，两者口径不同，这是预期的。P3-9 要求一致的是 raw_content，它已经逐字一致。

## 峰值 RSS
- 287,864 KB（约 281 MB），低于 .ok 上限 rss_cap 1450 MB ✓
- v3 dry-run 为 285,388 KB。

## stdout 对比（v3 D2 dry-run：d2_stdout_v3_20261018.txt，sha256 a7256773…）
- stdout：`d2_exec_stdout_20261018.txt`，sha256=0839fae0c641b825ac2b93c5040d3b099b5f34a425b3199ea3c968314a5ba6e4
- 原始 diff：`d2_exec_rawdiff_vs_v3_dryrun.txt`，12 行，sha256=3b51a4685e9fb4234fb514d46c9645f0b8ccaee3b6b75c4e455cad12f14a4e69。有差异的是：
  1. RUN_CONDITION_MATCHES 行：v3 为 94403 T，本次为 []
  2. GATE_PASS 行：mode 和 ok_sha 不同
  3. 统计行：只有 rss_mb 不同（275 对 274）
  4. 末行：DRY-RUN PASS 对 COMMITTED
  5. 包装行
- 规范化 diff：`d2_exec_normdiff_vs_v3_dryrun.txt`，**0 行**，sha256=e3b0c442…（空文件）。规则如下：
  - 去掉 RUN_CONDITION_MATCHES 和 WRAPPER_EXIT 行
  - ok_sha256=<64hex> 改为 <OK>
  - mode=(dryrun|execute) 改为 <MODE>
  - "rss_mb": N 改为 <RSS>
  - 去掉 `DRY-RUN PASS: nothing written` 和 `COMMITTED …` 末行
  - D2 的 stdout 不打印 sha 字段，所以不需要像 D1 那样去掉 sha 字段。

## find -newermt T0 写入核对（05:28 后执行）
- 命令：`find data/v2 output ref docs scripts -newermt '2026-10-18 05:26:47.233856328' -type f -not -path 'docs/v2/audit/data_cs_panel_execute/*'`

| 目录 | 文件数 | 说明 |
|---|---|---|
| data/v2/suspend_flags | 3 | 全部是 D2 输出 |
| docs/v2 | 1 | `docs/v2/ARCH_INTEL_SW_PIT_FRESHNESS_R2_REVIEW_ZH.md`，mtime 05:28:04.05，晚于 D2 结束时刻 05:27:53.69。这是 Arch 的另一份审查文档，不是本次写的 |
| data/v2/tushare_raw/fund_portfolio_dh | **0** | 94322 处于 T |
| output、scripts 及 data/v2 其他目录 | 0 | |

- 仓库根目录下没有 ref/ 目录。

## 未做
- 没有跑 D3D4。
- 没有对 94322 发 CONT 或 kill，它保持 T。
- 没有动补数队列和 moneyflow，没有启 8787，没有发消息，没有做 git 操作。
