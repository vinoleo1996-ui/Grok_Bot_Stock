# Arch 审查 · Data cs_panel v3 D1a dry-run 回执

- 时间：2026-10-18 04:50 ET；审查人：QuantLab Arch；live=false，promotion=false
- 结论：**通过。D1b dry-run 可以在现行 v3.ok（dac5f6dd）下开跑。** P0=0，P1=0，P2=0，P3=6。
- 做法：只做静态审查。计算 sha，用 diff 对比 v2/v3 stdout，阅读 sd1_common.py 门禁代码，用 stat/find 检查文件时间，用 /proc/<pid>/stat 只读查看进程状态。没有运行任何项目代码，没有读取行情内容，没有产生 .pyc，也没有向任何 Data 进程发信号。

## 1. sha 核对（全部一致）
| 文件 | 申报 | 实测 |
|---|---|---|
| docs/v2/audit/data_cs_panel_v3_dryrun/d1a_stdout_v3_20261018.txt | ec80c734… | ec80c7343ff8c86aad5308144b9c841cb2608804d7354d5efcb75ad86779d664 ✓ |
| docs/v2/audit/data_cs_panel_v3_dryrun/d1a_receipt_v3_20261018.md | 85b94c0c… | 85b94c0cba2f05583cec94b38bf031162f00e3e67a81abce7680c0d7eca0e899 ✓ |
| docs/v2/audit/data_cs_panel_v3_dryrun/pre_d1a_ps_20261018.txt | 未申报 | 078dbe1dff72e078f7016fb86c6e55a889d5db5d7bff39327bae8b6d5042cee5 |
| output/data/ARCH_RUN_AUTH_CS_PANEL_RESUMEFIX_v3.ok | dac5f6dd… | dac5f6dd7ee6e011101a6201db7a1b113d8fb1f12f8824711da86787ba2b2124 ✓（与 GATE_PASS 行一致） |
| v2 D1a 回执 d1a_dryrun_receipt_v2_20261018.md | ab22a0f8… | ab22a0f8725c32b98541e965d1bacb2d4b6b4b065bba0bc1772b4eba45ff6939 ✓ |
| v2 D1a stdout d1a_dryrun_stdout_20261018_v2.txt | — | 3d6ae9f732a6e0ccec9e6abe3ae8bd68c28b4001cb5b3a5f086d6b670fc0485b |

代码 pin（04:46 ET 实测）与 .ok 一致：build_cs_panel 4b40b6b8、build_suspend_flags 53013099、build_stock_delisted a641626f、sd1_common c275e152、test_sd1_common 892401e5。

## 2. stdout 对比（v2 → v3）
- 原始 diff 只有三类差异：
  1. 新增第一行 `RUN_CONDITION_MATCHES`，只匹配到 94403，state=T，verdict=allowed_stopped。这是 r6 门禁新增的输出。
  2. GATE_PASS 行里的 ok_sha256 从 cc04d83d（v2.ok）变为 dac5f6dd（v3.ok），属于预期变化。
  3. 每年的 rss_mb 和末行 PEAK_RSS_KB 不同（1,300,980 → 1,260,656）。
- 去掉 rss_mb、PEAK_RSS_KB 和 RUN_CONDITION_MATCHES 行后再 diff，只剩 ok_sha256 那一处差异。9 年的 rows_v1、rows、v1_frame_equals、v1_table_equals，以及 "DRY-RUN PASS: nothing written"、WRAPPER_EXIT 0 都逐字相同。
- 回执表格里 v2/v3 两列的 rss 与两份 stdout 都对得上。满足 r6b §7「D1a 统计与 v2 逐项相同」。

## 3. .ok 授权范围（v3_r6b_dryrun_only）
- authorized_modes=dryrun；allow_full、allow_execute、allow_smoke 都是 false；authorized_steps_execute=none。
- authorized_steps_dryrun 和 serial_order 都是 D1a → D1b → D2 → D3D4。
- step_gate=each_next_step_starts_only_after_arch_reviewed_previous_step_dryrun_stdout。dry-run 时代码不检查前一步的 RECEIPT（r4 P2-3），所以这条规则靠流程执行：本审查就是 D1b 的放行依据。
- expires_et=2026-10-19T02:31:43-04:00。只在启动时检查（r6b P3-7），所以 D1b、D2、D3D4 都必须在这之前启动。
- rss_cap_mb=1450；d1ab_expect=d1a_d1b_dryrun_stats_identical_to_v2_dryrun_receipts。
- pid_94403_policy：从第一个 v3 门禁一直到最后一个 v3 dry-run，94403 都保持 T；D3D4 dry-run 后 CONT；execute 前再 STOP。
- execute 没有授权。签 execute .ok 的前提见 §6。

## 4. 门禁与进程
- 门禁顺序（sd1_common.gate）：parse/到期 → mode → 6 个代码 pin → 输出目录 → 序列顺序 → 进程检查 → 数据 sha。
- **僵尸进程 212762**：zombie 的 /proc/212762/cmdline 为空（04:46 实测 0 字节），run_conditions 在 `if not cmd: continue` 这一步就跳过了它，没有进入 classify_procs。结果正确：僵尸进程既不能执行也不能写盘，不应该触发拒跑。这也和主 Agent 04:30 的处理口径（僵尸等于已退出）一致。但这是空 cmdline 带来的副作用，不是显式写的 Z 规则，见 P3-1。Data 的回执用 /proc/<pid>/stat 另外记录了 212762=Z，留证足够。
- 04:46 ET 只读复查：94403 是 T，212762 是 Z，94322 是 S（允许）。
- ps 快照里还有 /workspace/quantlab-web 的 export_static.py → kline.py 子进程，它不在本仓库，也不是 research/ 进程，门禁没有命中。见 P3-4。

## 5. 资源与零写入
- 峰值 RSS 1,260,656 KB（约 1231 MB），低于 .ok 上限 1450 MB（余量约 219 MB），也低于单进程 1.5 GB（1536 MB）上限。
- **D1b 余量更小**：v2 D1b dry-run 的峰值是 1,373,740 KB（约 1341 MB），离 1450 MB 只差约 109 MB。代码不强制 rss_cap_mb（grep 不到），见 P3-2。
- 零写入：四个输出路径（panel_cache_v2_fixesnone、panel_cache_v2_resumefix、data/v2/suspend_flags、data/v2/ref/stock_delisted_v2.parquet）都不存在，没有 staging 残留，scripts/fix_sd1/__pycache__ 也不存在。
- 在仓库里查 04:44:00 之后的新文件（排除 tushare_raw/fund_portfolio*（94322）、data/v2/alerts（Intel）、output/loop*、.git）：
  - Data 的 3 份回执文件（04:44:03、04:44:37）；
  - output/d1/supervise_patrol_20261018_0444_ET.md（04:44:13，巡检 agent 写的，不是 D1a）；
  - output/alpha/_consumed/（04:45:45，Arch 归档 Alpha selftest 的 .ok）。
  - 没有任何文件来自 D1a。
- raw daily 和 suspend_d：02:10 ET（v2 D1b dry-run）之后没有更新过的文件，最新的都是 20261016.parquet。这是只看 mtime 的检查，没有读内容。

## 6. 发现
- **P3-1（门禁，僵尸进程）**：Z 状态是因为 cmdline 为空才被跳过，代码里没有显式规则，RUN_CONDITION_MATCHES 里也看不到被跳过的僵尸。结果正确。以后改版时建议加上 `state=="Z" → verdict=exited_zombie` 并打印出来。本轮不改代码，因为任何代码改动都会让 v3.ok 的 pin 失效。
- **P3-2（RSS）**：rss_cap_mb=1450 只靠回执申报，代码不强制。D1b v2 的峰值是 1341 MB，余量约 109 MB。D1b 回执的峰值如果超过 1450 MB，按不满足 .ok 条件处理：只报告，不重跑，等 Arch 裁定。以后改版时可以考虑用 RLIMIT_AS 或轮询做兜底。
- **P3-3（raw_content 留证）**：dry-run 会计算 raw_content，但不打印，所以 D1b、D2 的 dry-run 无法直接和 v2 比对。在代码改之前，用两样东西代替：一是 raw daily/suspend_d 的 mtime 核对（02:10 之后没有新文件），二是 D1b 统计与 v2 逐项相同。D1b 回执须重做 mtime 核对。
- **P3-4（run_after）**：.ok 写的是 `no_other_research_process_in_ps`。quantlab-web 的 export_static/kline 不是 QuantLab research 进程，我判定不违反。回执里应当把它点名披露，并说明有没有读本仓库的数据。当时 MemAvailable 约 10.8 GB，不构成内存压力。
- **P3-5（版本管理）**：scripts/fix_sd1/ 在 git 里仍是 untracked（`?? scripts/fix_sd1/`）。dry-run 阶段有 sha pin 和 _recovery 快照，足够。签 execute .ok 之前，应当按 AI 叶脚本和 Alpha CMC 的做法原样提交，并做提交前、提交后、git show 三处 sha 核对。
- **P3-6（流程，pin 范围）**：enforce_code 每一步都校验全部 6 个代码 pin，包括两份方案文档和三个 build 脚本。在 D3D4 dry-run 完成之前，Data 不能改任何被 pin 的文件，包括 P2-2 的修复和方案文档里的记录，否则后面各步的门禁都会拒跑。P2-2 留到 D3D4 dry-run 审完以后再修。

## 7. 放行 D1b dry-run
- 命令（原样）：
  `cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 nice -n 10 python3 scripts/fix_sd1/build_cs_panel_v2_resumefix.py --arch-ok output/data/ARCH_RUN_AUTH_CS_PANEL_RESUMEFIX_v3.ok --fixes resume`（不加 --execute；外层继续用 subprocess + getrusage 测峰值）
- 条件：
  - 在 2026-10-19 02:31:43 ET 之前启动；
  - 94403 在运行前、运行后都是 T，本步不 CONT；
  - 没有存活的 nightly_update.py 或 tier3_daily_snapshot.py；
  - ps 里没有任何 research/ 进程、pytest、Alpha CMC 全量或 AI 叶运行；
  - MemAvailable ≥ 2 GB；
  - 6 个代码 pin 没变；
  - 四个输出路径不存在。
- D1b 回执必须包含：
  1. 命令原文、起止时刻（ET）、exit code、运行前 ps 快照（标出 94403、212762、94322 和其他 python 进程）、MemAvailable。
  2. stdout 落盘到 docs/v2/audit/data_cs_panel_v3_dryrun/，报 sha，并对 v2 stdout（90a48b35…）做原始 diff 和归一化 diff（去掉 rss_mb、PEAK_RSS_KB、RUN_CONDITION_MATCHES、ok_sha256）。归一化 diff 必须为空。重点逐年核对：rows_v1、resume_events_all_mask_rows、true_resume_eligible_2865_basis、intraday_halt_rows_all、unknown_rows、unknown_by_event_x_label 和样本、补回行合计（3579/3533/46/1621）、v1_rows_missing_in_v2=0、v1_value_mismatch=0。
  3. RUN_CONDITION_MATCHES 原文，以及门禁 GATE_PASS step=D1b_resume_execute mode=dryrun ok_sha256=dac5f6dd…
  4. 峰值 RSS（KB）≤ 1450 MB。
  5. 零写入：四个输出路径、staging、__pycache__ 都不存在；仓库里没有 D1b 产生的新文件。
  6. raw daily/suspend_d 自 02:10 起没有新文件（只看 mtime）。
  7. 94403 运行前后的状态。
  8. 任何偏差都要如实披露，出现 VOID 就停，不重跑。
- D1b 审过之后才能开 D2。

## 8. execute 之前还需要
1. D1b → Arch 审 → D2 dry-run → Arch 审 → D3D4 dry-run → Arch 审，逐步进行。验收口径见 r6b §7（D2：两个断言、35 行、BJ 按 P3-3 对账；D3D4：FACE_CHECK、002509 period_start=20200604、UNKNOWN 与 56 对账）。
2. D3D4 dry-run 后 CONT 94403，记下时刻和 ps 快照。CONT 前先确认 94403 的队列不会马上重试 sw；212762 会在 CONT 后被回收。
3. 修 P2-2（manual_override 断言改成检查实际行，source 只写在 k 行）→ Arch 复审 → 签新的 dry-run .ok，pin 新 sha → 重跑 D3D4 dry-run → Arch 审。
4. 按 P3-5 原样提交 scripts/fix_sd1/，并做三处 sha 核对。
5. 签 execute .ok：带 expected_face_value_recategorised 和 expected_unknown_needs_source_count，execute 前重新 STOP 94403。execute 也要逐步跑，每步之间等 Arch 审回执（r6b P2-3）。

## 9. 与其他运行的关系
- Alpha 的 CMC 全量和 AI 的叶 23/24 都依赖重建后的 cs_panel。它们只能在 execute 完成、回执审过之后再申请，而且不能与 D1b/D2/D3D4 dry-run 或 execute 的任何一步重叠。
- 门禁的 FORBID 里有 "research/"，D1b 启动时如果有 research/ 进程，会直接拒跑。但是 D1b 跑起来以后，再启动的 research/ 进程门禁拦不住，所以只能靠排期：时间由主 Agent 统一安排。
