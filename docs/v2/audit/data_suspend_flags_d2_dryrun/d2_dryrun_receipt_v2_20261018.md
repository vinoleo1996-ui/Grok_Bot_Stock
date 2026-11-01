# D2 dry-run 回执 v2（build_suspend_flags_v2.py，v2.ok）
- 时间：2026-10-18 02:14:20–02:15:26 EDT；执行人：QuantLab Data；单进程，live=false，promotion=false
- 命令：`cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 nice -n 10 python3 scripts/fix_sd1/build_suspend_flags_v2.py --arch-ok output/data/ARCH_RUN_AUTH_CS_PANEL_RESUMEFIX_v2.ok`
  - 没有加 --execute；用法与脚本 docstring 一致。
- 外层监视：/tmp/d2_mon.py，用完已删除。
  - 用 Popen 起上面的命令，每秒读 /proc/<pid>/status 的 VmRSS，超过 1450MB 就 SIGTERM。
  - 跑完读 getrusage(RUSAGE_CHILDREN)。
- 运行前自查（02:14:15）：
  - .ok sha 为 cc04d83d…，未过期。
  - 7 个文件与 _recovery/data/sd1_r5_20261018/SHA256SUMS 一致（7/7 OK）。
  - MemAvailable 约 10.9 GB。
  - ps 中没有冲突进程。
  - 本轮没有改代码。
- stdout：d2_dryrun_stdout_20261018_v2.txt。
  - GATE_PASS step=D2_suspend_flags mode=dryrun ok_sha256=cc04d83d…
  - 末行为 "DRY-RUN PASS: nothing written"，exit 0。
- 没有出现 VOID：join key 无重复，raw 内容运行前后比对也没有报错。

## 1. 逐年统计（脚本自报）
| 年 | 行数 | halted_fullday | intraday_halt | resume_announced | is_resume_day | conflict_v1 |
|---|---|---|---|---|---|---|
| 2018 | 45,221 | 41,541 | 111 | 1,324 | 3,528 | 1,402 |
| 2019 | 8,162 | 5,176 | 149 | 585 | 2,810 | 707 |
| 2020 | 12,873 | 8,833 | 240 | 588 | 3,750 | 776 |
| 2021 | 13,903 | 10,328 | 229 | 561 | 3,306 | 727 |
| 2022 | 20,812 | 18,602 | 119 | 545 | 2,013 | 559 |
| 2023 | 12,158 | 11,616 | 92 | 387 | 379 | 382 |
| 2024 | 3,742 | 3,368 | 43 | 329 | 328 | 353 |
| 2025 | 4,047 | 3,434 | 39 | 572 | 570 | 592 |
| 2026 | 2,696 | 2,212 | 45 | 458 | 451 | 482 |
| 合计 | 123,614 | | | | | 5,980 |

- conflict_v1（tier1 v1 判停牌但实际有成交，即假停牌）按类别：
  - R/nointra 4939；S/intra 1001；R|S/intra 38；S/nointra 1；R|S/nointra 1。
- 其他计数：fullday_but_traded=2，is_resume_day_without_R=12169，R_without_resume=383，first_session_forced_no_resume=20180102。
- intraday_halt：2018–2020 年与 D1b 的 intraday_halt_rows_all（111/149/240）一致。2021–2026 年 D2 略多（229 对 218 等），原因是 D2 统计全部 suspend_d 记录，D1b 只统计掩码里的行。

### 125 行对账：未完成
- 方案 §31 的口径是：asof_extend 面板中 tradestatus=0 且 vol>0 的约 125 行，应全部为 conflict_v1=True。
- dry-run 的 stdout 只有按年和按类别的 conflict 汇总，没有逐行结果，所以没法证明这 125 行是 conflict 的子集。
- 能看到的只有：2026 年 conflict_v1=482，不小于 125，方向上一致。
- 逐行对账需要 execute 产出表之后再和 asof 面板 join，或者另做一次只读核对（需要 .ok）。本轮没有做。

### 需要 Arch 关注：is_resume_day 2018–2022 年明显偏高
- 2018–2022 年 is_resume_day 远高于 resume_announced，例如 2018 年 3528 对 1324；全期 is_resume_day_without_R=12169。2023 年以后两者基本相等。
- 和 D1b 比也偏高。D1b 2018 年的 resume_events_all_mask_rows 是 1286，true_resume_eligible 是 632。
- 两者口径不同：D2 统计全市场所有代码，D1b 只统计掩码内。但差距太大，不能只用口径来解释。
- 一个推测：2018–2022 年 raw daily 里，有些代码在非停牌日也出现 amount=0 的行（例如退市整理期、长期无成交）。按"前一交易日 amount>0"的定义，下一次有成交就被判为复牌。
- 本轮没有改代码，也没有额外读数据验证。建议 Arch 决定是否在 execute 之前，做一次只读抽样（需要 .ok），或者调整披露口径。

## 2. 截止日
- CUTOFF = mask_last_date = 20261014。
- 纳入范围：20180102–20261014 共 2128 个 daily 文件，按与代码相同的 glob 规则数文件名得到。
- 被截掉、不纳入的：20261015、20261016（excluded_after_cutoff）。

## 3. days_walked
- stdout 不打印 days_walked。manifest 只在 execute 模式下写出，其值等于 len(days)。
- 按代码的同一规则数文件名，预期 days_walked=2128。这是由文件列表推出来的，不是脚本输出。
- D1b 的 sessions_walked 也只在 execute 时可见。按 Arch 的裁定（P3），两者是否相等在 execute 回执里核对。

## 4. raw 内容哈希
- D1b 和 D2 的 dry-run 都调用 C.raw_content_sha256(20261014)，但 stdout 都没有打印这个值，RAWC 只进 manifest。
- 所以没法直接比对两步的哈希。可以确认的是两步运行时都通过了 .ok 的数据 pin。D2 还有一层自检：运行结束时重新计算 raw 内容哈希，与开始时（RAWC）相同，否则会 VOID；这次没有 VOID。
- 两步的哈希值是否一致，在 execute 回执里用 manifest.raw_content 对照。

## 5. 资源与零写入
- 峰值 RSS：getrusage 测得 292,160 KB（约 285 MB）；监视器测得 VmRSS 最大 291,332 KB；脚本自报 rss_mb=285。
  - 这个脚本只在最后打印一次 rss_mb，没有逐年值。监视器是每秒采样的。
  - 远低于 1450MB 的停机阈值，监视器没有发出 SIGTERM。
- 零写入确认：
  - 四个目标路径都不存在（4 个 No such file）。
  - .ok 之后 output/、data/ 没有新增 staging 或 VOID 文件。
  - scripts/fix_sd1 下没有 __pycache__；/tmp/d2_mon.py 已删除。
- 未跑 D3D4。
