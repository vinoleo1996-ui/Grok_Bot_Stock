# 驱动 v3 假进程测试回执（DRIVER_TEST_RECEIPT2）

- 作者：QuantLab Data；运行 2026-10-18T13:00:03-04:00 → 2026-10-18T13:01:49-04:00（ET）。
- 被测驱动：/tmp/qd1018/v3/dry_drv.py（sha 63b5a88462f9f75ae7975f52320bbd6f88433cdf4857bf95c6de557d6d880e16；与已安装的 docs/v2/audit/nightly_20261019/run_nightly_v1.py 字节相同）
- 被测兜底：/tmp/qd1018/v3/routine_fallback_v1.py（sha f3244472da360b74cc692f90548fab4f8839f13f3938bf65374d592b2d61ac5f；与已安装的 routine_fallback_v1.py 相同）
- 测试脚本：/tmp/qd1018/v3/tdrv5.py（c4fae0cbd4dffb15d2f3055d799634ad5f50392d820022e405cec093cf3bf9f3）、/tmp/qd1018/v3/thang2.py（aea78843ecce7a577d426bdb390f5105b2fb45751d553bc63b65857332ce8722）；原始结果 JSON /tmp/qd1018/v3/tdrv5_run1.json（9240703328b02bb750adbc05a60fbfdcd8b5a40526101de739af40260f0bf89e）。
- 命令：`cd /tmp && python3 /tmp/qd1018/v3/tdrv5.py /tmp/qd1018/v3/dry_drv.py /tmp/qd1018/v3/routine_fallback_v1.py /tmp/qd1018/v3/tdrv5_run1.json`（13:00:03 ET 开始；开跑前 chk_busy / chk_fake 确认无 selftest / probe / runner、无残留假进程；12:45–13:00 未起任何假进程）。
- 隔离：全部假文件、假脚本（scripts/nightly_update.py、scripts/acquire/*.py 的假版本）与假日历都在 mkdtemp 目录；驱动模块的 ROOT / RAW / HERE / MARK_DIR / QUIET_LOCK / TRADE_CAL / PIT / FROZEN 全部改指 /tmp；审计工具（快照、比对、恢复）在端到端用例里被替换为假函数；未读写任何 /workspace/QuantLab 真实数据，未对任何真实 PID 发信号（只对测试自起、cwd 在测试目录内的进程发信号）。
- 时间缩放：daily_pull 时间盒 0.15 分钟（9 秒）、call B 预算 0.15 分钟、日历双核间隔 1 秒；生产值不变（30 / 75 / 30 秒）。
- /tmp 目录：/tmp/qd_drv5_d5n5xwim、/tmp/qd_drv5_klqn7fy6、/tmp/qd_drv5_hrzsytj3、/tmp/qd_drv5_fmu8qal4、/tmp/qd_drv5_gl878g1u、/tmp/qd_drv5_rs3p496k

## 结果：全部通过（19 / 19 通过）

| 用例 | 结果 | 内容 |
|---|---|---|
| T01_parse_ok_rejects | PASS | parse_ok：合法文件通过；行内注释、重复键、冒号行、DRAFT、非 ASCII、CR、未知键全部拒绝（Arch 第 6、10 项） |
| T02_check_ok_required_keys | PASS | check_ok：全键 .ok 通过；/_consumed/ 路径、缺 sha_relay_health、tier1_pull 旧 sha b630bca2、signed_by 错、issued_at 未来、live=true、预算非整数全部拒绝；source_relay_only=true 生效（第 11、12 项） |
| T03_expiry_rechecked | PASS | expires_et 复核：过期拒绝、未过期通过 |
| T04_no_double_interpreter | PASS | run_tool 拒绝以解释器开头的参数（无双解释器） |
| T05_last_date_two_formats | PASS | post_checks：last_date 20261019 与 2026-10-19 两种格式都通过；20261016 对 6 张 REQUIRED 表全部判失败（第 13 项） |
| T06_stale_summary_fails | PASS | summary：本次窗口内 ok 通过；含 skipped 失败；旧 finished + 旧 mtime 失败（旧 summary → FAILED） |
| T07_hsgt_rc2_is_partial | PASS | hsgt：remaining=0 通过；remaining=3（rc=2）判 partial 失败 |
| T08_check_only_exit_10 | PASS | --check-only 收尾退出 10 |
| T09_guarded_T_or_exited_never_signaled | PASS | 受保护 PID（用测试自起的 /bin/sleep 代替 94322，绝未触碰真实 94322 / 94403）：S 拒绝、T 放行；signal_exact 对其返回 refused 且进程仍在 |
| T10_tool_timeout | PASS | 审计工具超时（compare 限 2 秒）→ 按确切 PID TERM → 抛 ToolTimeout，进程已不在 |
| T11_stop_order_freeze_then_deepest_first | PASS | 停树顺序：SIGSTOP 父 → 冻结全部后代 → 最深（忽略 TERM 的孙进程）先 TERM+CONT → 10 秒后 KILL → 子 term_ok → KILL 父（第 2 项；孙进程被停） |
| T12_unmarked_child_is_residual_FAILED | PASS | 无标记的 /bin/sleep 子进程不发信号、记 residual（main 中 → 不重试、不起 call B、FAILED） |
| T13_orphan_ppid1_log_only | PASS | setsid 脱离的 PPID=1 孤儿只记录 P1，不发信号 |
| T14_refuse_and_wait_timeout_HANG | PASS | 父 cmdline 不符 → 拒发 → wait 3 秒超时 → HANG |
| T15_daily_pull_hang_hard_stop_FAILED_calendar_restored | PASS | 端到端（thang2.py，strict）：假 tier1_pull 写坏假日历后挂死、忽略 TERM → 9 秒时间盒（生产 30 分钟）MAX_RUN 停树 → 恢复（假 cal_restore 拒绝 → 驱动自带原子恢复）+ 双核 → FAILED，退出 1；子进程环境 TSPRO_RELAY_TIMEOUT=115、SOURCE 未设、TIER1_SKIP_CAL_REFRESH=1；cal refresh skipped 日志证据 found=true |
| T16_driver_SIGTERM_FAILED_exit11_calendar_restored | PASS | 端到端：运行中对假驱动发 SIGTERM → 统一收尾停树 → 恢复日历 → FAILED，退出 11 |
| T17_callB_timeout_FAILED | PASS | 端到端：call A 成功后 call B 挂死 → 9 秒预算（生产 75 分钟）CALLB_TIMEOUT 停树 → FAILED，退出 1，invocations 2 条 |
| T18_RSS_stop_not_retried | PASS | 端到端（relaxed，重试授权 2）：RSS 停线触发 → reason_codes=[RSS]，只 1 次尝试，不重试 → FAILED |
| T19_driver_SIGKILL_routine_fallback | PASS | 端到端：对假驱动 SIGKILL → 无 marker、假日历已坏 → routine_fallback 第一次 pgrep 见孤儿树退出 6（未动）→ 测试按 cwd 清掉自己的假进程 → 第二次原子恢复假日历 + 代写 FAILED（writer=routine_fallback，reason=driver_killed），退出 1 |

## 关键证据（摘自 JSON）
- T11_stop_order_freeze_then_deepest_first：`{"name": "T11_stop_order_freeze_then_deepest_first", "ok": true, "steps": [["SIGSTOP_PARENT", 291468, "sent"], ["SIGSTOP", 291472, "gone"], ["SIGSTOP", 291471, "refused"], ["SIGSTOP", 291470, "sent"], ["SIGSTOP", 291469, "sent"], ["TERM_KILL", 291472, "gone"], ["TERM_KILL", 291471, "refused"], ["TERM_KILL", 291470, "killed"], ["TERM_KILL", 291469, "term_ok"], ["SIGKILL_PARENT", 291468, "sent"]], "rc": -9, "reason_code": "MAX_RUN"}`
- T15_daily_pull_hang_hard_stop_FAILED_calendar_restored：`{"name": "T15_daily_pull_hang_hard_stop_FAILED_calendar_restored", "ok": true, "exit_code": 1, "markers": ["nightly_20261019.FAILED.json"], "reason_codes": ["MAX_RUN"], "calendar": [{"tag": "a1", "at": "2026-10-18T13:01:00-04:00", "sha_before_restore": "c3f17d12a10b9f7cbd1f109ea679a74e86234ee844df43898467b546b5a7661a", "post_copy": {"path": "/tmp/qd_drv5_klqn7fy6/_recovery/data/nightly_20261019/run_20261018T130039/trade_cal.parquet.post_a1", "sha256": "c3f17d12a10b9f7cbd1f109ea679a74e86234ee844df43898467b546b5a7661a"}, "compare_rc": 0, "restore_rc": 1, "native": {"ok": true, "at": "2026-10-18T13:01:00-04:00"}, "sha_after": "06705ab0d3046b223196d69bde02215a3ab766377a580ccced13bf027467b9f4", "sha_after_recheck": "06705ab0d3046b223196d69bde02215a3ab766377a580ccced13bf027467b9f4", "recheck_s": 1, "changed": true}], "env_line": ["ENV TSPRO_RELAY_TIMEOUT=115 SOURCE=None TIER1_SKIP_CAL_REFRESH=1"], "cal_skip_evidence": [{"log": "/tmp/qd_drv5_klqn7fy6/logs/nightly/20261019_daily_pull.log", "found": true, "at": "2026-10-18T13:01:00-04:00"}], "elapsed_s": 21.7, "root": "/tmp/qd_drv5_klqn7fy6"}`
- T16_driver_SIGTERM_FAILED_exit11_calendar_restored：`{"name": "T16_driver_SIGTERM_FAILED_exit11_calendar_restored", "ok": true, "exit_code": 11, "signal": "SIGTERM 293315", "markers": ["nightly_20261019.FAILED.json"], "reason_codes": ["SIGNAL", "SIGNAL"], "stop": [["SIGSTOP_PARENT", 293317, "sent"], ["SIGSTOP", 293318, "sent"], ["TERM_KILL", 293318, "killed"], ["SIGKILL_PARENT", 293317, "sent"]], "elapsed_s": 17.6, "root": "/tmp/qd_drv5_hrzsytj3"}`
- T17_callB_timeout_FAILED：`{"name": "T17_callB_timeout_FAILED", "ok": true, "exit_code": 1, "markers": ["nightly_20261019.FAILED.json"], "reason_codes": ["CALLB_TIMEOUT"], "callb_stop": [["SIGSTOP_PARENT", 294093, "sent"], ["SIGSTOP", 294098, "sent"], ["SIGSTOP", 294097, "sent"], ["TERM_KILL", 294098, "term_ok"], ["TERM_KILL", 294097, "term_ok"], ["SIGKILL_PARENT", 294093, "sent"]], "elapsed_s": 18.2, "root": "/tmp/qd_drv5_fmu8qal4"}`
- T18_RSS_stop_not_retried：`{"name": "T18_RSS_stop_not_retried", "ok": true, "exit_code": 1, "reason_codes": ["RSS"], "attempts": 1, "root": "/tmp/qd_drv5_gl878g1u"}`
- T19_driver_SIGKILL_routine_fallback：`{"name": "T19_driver_SIGKILL_routine_fallback", "ok": true, "driver_rc": -9, "signal": "SIGKILL 295739", "markers_after_kill": [], "calendar_bad_after_kill": true, "fallback1_rc": 6, "orphans_killed_by_test": [[295771, "/usr/bin/python3 scripts/nightly_update.py --date 20261019 --steps daily_pull", "S"], [295772, "/usr/bin/python3 scripts/acquire/tier1_pull.py extend 20261019", "S"]], "fallback2_rc": 1, "marker": {"schema": "quantlab.v2.nightly_marker.v1", "status": "FAILED", "writer": "routine_fallback", "reason": "driver_killed", "date": "20261019", "trade_cal_sha256_before": "c3f17d12a10b9f7cbd1f109ea679a74e86234ee844df43898467b546b5a7661a", "trade_cal_sha256_after": "06705ab0d3046b223196d69bde02215a3ab766377a580ccced13bf027467b9f4", "trade_cal_pin": "06705ab0d3046b223196d69bde02215a3ab766377a580ccced13bf027467b9f4", "restore": {"backup": "/tmp/qd_drv5_rs3p496k/_recovery/data/nightly_20261019/run_20261018T130142/trade_cal.parquet.141078fa", "ok": true, "at": "2026-10-18T13:01:49-04:00"}, "pgrep": {"rc": 1, "lines": []}, "live": false, "promotion_approved": false, "written_at_et": "2026-10-18T13:01:49-04:00"}, "root": "/tmp/qd_drv5_rs3p496k"}`

## 清理
测试结束时由测试脚本按 cwd（== 测试目录）对自己的残留假进程发 SIGKILL（用例设计内：T11 无标记 /bin/sleep 与 setsid 孤儿、T14 被拒发的假 nightly、T19 驱动被 KILL 后的孤儿树）：
`[{"tag": "T11", "killed_by_test": [[291471, "/bin/sleep 301", "S"], [291473, "/usr/bin/python3 scripts/acquire/orphan_launch.py", "S"]], "after": []}, {"tag": "T14", "killed_by_test": [[292163, "/usr/bin/python3 scripts/nightly_update.py --date 20261019 --steps daily_pull", "S"]], "after": []}, {"tag": "T15", "killed_by_test": [], "after": []}, {"tag": "T16", "killed_by_test": [], "after": []}, {"tag": "T17", "killed_by_test": [], "after": []}, {"tag": "T18", "killed_by_test": [], "after": []}, {"tag": "T19", "killed_by_test": [[295771, "/usr/bin/python3 scripts/nightly_update.py --date 20261019 --steps daily_pull", "S"], [295772, "/usr/bin/python3 scripts/acquire/tier1_pull.py extend 20261019", "S"]], "after": []}]`

结束时各测试目录残留进程：`{"/tmp/qd_drv5_d5n5xwim": [], "/tmp/qd_drv5_klqn7fy6": [], "/tmp/qd_drv5_hrzsytj3": [], "/tmp/qd_drv5_fmu8qal4": [], "/tmp/qd_drv5_gl878g1u": [], "/tmp/qd_drv5_rs3p496k": []}`（全空）。

## 观察到的小问题（不影响判定，未改）
- T16 reason_codes 为 [SIGNAL, SIGNAL]（统一收尾与 stop_tree 各记一次）；T11 residual 中同一 PID 出现两次（停树与孤儿扫描各记一次）。仅记录重复，不影响 FAILED 判定。
