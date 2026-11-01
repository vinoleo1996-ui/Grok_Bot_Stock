# SELFTEST v3.1-c 回执（QuantLab Data，生成 2026-10-18T11:52:52-04:00，date 生成）

- .ok：output/ai_factory/ARCH_SELFTEST_DATA_BACKFILL_R_V3_1_C.ok，sha 381ae4b0df9b1dfaba7a259ce1c3f9807ae4e03266c31db253f3b045e118e480，expires_et 2026-10-18T12:50:00-04:00，运行时未过期；单次使用，Data 未移动，由 Arch 归档。
- cwd：/tmp。命令（逐字，仅追加输出重定向）：```
cd /tmp && PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 /workspace/QuantLab/docs/v2/audit/backfill_1014_1016/selftest_run_backfill_r_v3_1_c.py </dev/null > /workspace/QuantLab/docs/v2/audit/backfill_1014_1016/selftest_v3_1_c_20261018T115240.txt 2>&1
```
- 时间：11:52:40–11:52:43 ET（12:05 前完成）；只跑一次。
- **rc=0；pass=19 fail=0**。实际目录：/tmp/qd_v31_selftest_2y3w54b4。
- 注：输出首尾行的标签仍写 SELFTEST_B（由 b 复制、未改横幅文字），文件确为 selftest c（sha 19e0130e）。
- 输出文件：docs/v2/audit/backfill_1014_1016/selftest_v3_1_c_20261018T115240.txt，sha 2d373e6708898bdef9a49aed2db67bad3e5847fc36cccd877844115cb15e7dd3。

## stop_tree
- npid=175067：SIGSTOP 175067 sent → TERM_KILL 175077（孙）term_ok → TERM_KILL 175076（子）term_ok → SIGKILL 175067 sent；rc=-9，wait 未超时。

## B3 / B3b / KSTATE
- B3 PASS：恰好四个信号 [(175067,SIGSTOP=19),(175077,SIGTERM=15),(175076,SIGTERM=15),(175067,SIGKILL=9)]。
- B3b PASS：子 175076 收到 TERM 时状态 S（存活，非 Z）。
- 完整 KSTATE（pid, sig, 发信号前状态）：[(175067, 19, S), (175077, 15, S), (175076, 15, S), (175067, 9, T)]
- B4：四个信号前均核了 cmdline 与 ppid（全 True/True）。

## orphans_run1
- **[]（空）**。

## pgrep -af [s]cripts/acquire/|[n]ightly_update|[t]drv4
- 前（11:52:38）：仅 94322（remaining_after_stk_surv.py）；probe3/probe4：无。
- 后（11:52:45）：仅 94322；pgrep -af qd_v31_selftest_：无残留替身进程。

## sha（前 = 后）
- .ok 381ae4b0df9b1dfaba7a259ce1c3f9807ae4e03266c31db253f3b045e118e480
- selftest c 19e0130e90f65a84f0940bb6dd134ecd95507f5fc39d5a43e87457ebc2f91e74
- selftest b e3d04311393081a6c185c96bfd91df15d1ca5ca4391e4cbae4d30d78e2279e14
- runner c983aed3db32fdaf9398b5977324b91ea0bf4f45591ccbd9da7d7357bfa7ebeb

## __pycache__
- ls -a docs/v2/audit/backfill_1014_1016/：无；find /tmp/qd_v31_selftest_2y3w54b4 -name __pycache__：无。

## 完整 stdout+stderr
```
SELFTEST_B start 2026-10-18T11:52:40-04:00 actual_dir /tmp/qd_v31_selftest_2y3w54b4 out_dir_prefix /tmp/qd_v31_selftest ok_keys ['allow_daily_pull', 'allow_delete', 'allow_force', 'allow_network', 'allow_real_data', 'allow_restore_cyq_202610_from_backup', 'allow_run_nightly_update', 'allow_selftest', 'allow_sw_write', 'allow_trade_cal_write', 'allowed_windows', 'cmd', 'expires_et', 'issued_at', 'live', 'ok_id', 'ok_type', 'on_failure', 'out_dir_prefix', 'precondition_pgrep', 'promotion', 'require_all_cases_pass', 'require_no_repo_pycache', 'require_orphans_run1_empty', 'scope', 'sha_runner', 'sha_selftest_b', 'sha_selftest_c', 'sha_selftest_c_diff', 'signed_by', 'signed_et', 'single_use', 'stop_order_expected']
2026-10-18T11:52:40-04:00 RUN1 start npid=175067 cmd=/usr/bin/python3 scripts/nightly_update.py --date 20261016 --steps cyq
TREE_CONFIRMED npid=175067 child=175076(stat=S) grandchild=175077(stat=S)
2026-10-18T11:52:41-04:00 STOP_TREE npid=175067 reason=RSS 采样和 30948 kB > 1
2026-10-18T11:52:41-04:00 SIGNAL SIGSTOP pid=175067 ppid=175066 cmd='/usr/bin/python3 scripts/nightly_update.py --date 20261016 --steps cyq'
2026-10-18T11:52:41-04:00 SIGNAL SIGTERM pid=175077 ppid=175076 cmd='/usr/bin/python3 /tmp/qd_v31_selftest_2y3w54b4/scripts/acquire/fake_grandchild.py'
2026-10-18T11:52:41-04:00 SIGNAL SIGTERM pid=175076 ppid=175067 cmd='/usr/bin/python3 /tmp/qd_v31_selftest_2y3w54b4/scripts/acquire/fake_child.py'
2026-10-18T11:52:42-04:00 SIGNAL SIGKILL pid=175067 ppid=175066 cmd='/usr/bin/python3 scripts/nightly_update.py --date 20261016 --steps cyq'
2026-10-18T11:52:42-04:00 ORPHAN_SCAN run1 found=0
2026-10-18T11:52:42-04:00 RUN1 end rc=-9 stopped=RSS 采样和 30948 kB > 1 orphans=0 rss_max_sum=30948
PASS B1 子与孙在停树前已确认存活 {"t0": 1792338760.604084, "confirmed_at": 1792338761.104672, "child": 175076, "grandchild": 175077, "timeout": false}
PASS B2 stop_tree 记录顺序 SIGSTOP nightly → 孙 → 子 → SIGKILL nightly [('SIGSTOP', 175067, 'sent'), ('TERM_KILL', 175077, 'term_ok'), ('TERM_KILL', 175076, 'term_ok'), ('SIGKILL', 175067, 'sent')]
PASS B2 每步结果为 sent/term_ok/killed [('SIGSTOP', 175067, 'sent'), ('TERM_KILL', 175077, 'term_ok'), ('TERM_KILL', 175076, 'term_ok'), ('SIGKILL', 175067, 'sent')]
PASS B3 恰好四个信号：STOP nightly → TERM 孙 → TERM 子 → KILL nightly [(175067, 19), (175077, 15), (175076, 15), (175067, 9)]
PASS B3b 子进程收到 TERM 时存活（非 Z） [(175067, 19, 'S'), (175077, 15, 'S'), (175076, 15, 'S'), (175067, 9, 'T')]
PASS B4 每个信号前都核了 cmdline 与 ppid [(175067, 19, True, True), (175077, 15, True, True), (175076, 15, True, True), (175067, 9, True, True)]
PASS B4 事件日志带 ppid 与 cmd 2026-10-18T11:52:41-04:00 SIGNAL SIGSTOP pid=175067 ppid=175066 cmd='/usr/bin/python3 scripts/nightly_update.py --date 20261016 --steps cyq'
2026-10-18T11:52:41-04:00 SIGNAL SIGTERM pid=175077 ppid=175076 cmd='/usr/bin/python3 /tmp/qd_v31_selftest_2y3w54b4/scripts/acquire/fake_grandchild.py'
2026-10-18T11:52:41-04:00 SIGNAL SIGTERM pid=175076 ppid=175067 cmd='/usr/bin/python3 /tmp/qd_v31_selftest_2y3w54b4/scripts/acquire/fake_child.py'
2026-10-18T11:52:42-04:00 SIGNAL SIGKILL pid=175067 ppid=175066 cmd='/usr/bin/python3 scripts/nightly_update.py --date 20261016 --steps cyq'
PASS B5 停树后未起下一步 
PASS B6 替身进程全部消失（Z 视为退出） [(175067, None), (175076, None), (175077, None)]
PASS B7 orphans_run1 为空 []
PASS B8 rc 为 -9 且 wait 未超时 rc=-9 wait_timeout=False
PASS P3-2 二次 open(x) 抛 FileExistsError /tmp/qd_v31_selftest_2y3w54b4/logs/nightly/backfill_20261018_run1.out
2026-10-18T11:52:43-04:00 SIGNAL refuse pid=175147 cmdline/ppid 不符（'/usr/bin/python3 /tmp/qd_v31_selftest_2y3w54b4/other/fake_not_acquire.py' ppid=175066 期望 175066），不发信号
PASS P3-B cmdline 不含 scripts/acquire/ → refused res='refused'
PASS P3-B 未发任何信号 kills 4→4
PASS P3-B 拒绝已写日志 
PASS P3-B 进程仍存活 stat=R
PASS P3-B 自测清理后已退出 rc=-15
PASS G1 所有被发信号的 PID 都在 SPAWNED 中 [175067, 175076, 175077, 175147]
PASS G2 守卫拒绝非本自测 PID pid=1 未发信号
STOP_TREE_RECORDS [{"reason": "RSS 采样和 30948 kB > 1", "at": "2026-10-18T11:52:41-04:00", "npid": 175067, "steps": [["SIGSTOP", 175067, "sent"], ["TERM_KILL", 175077, "term_ok"], ["TERM_KILL", 175076, "term_ok"], ["SIGKILL", 175067, "sent"]]}]
ORPHANS_RUN1 []
KILL_CALLS [[175067, 19], [175077, 15], [175076, 15], [175067, 9]]
SELFTEST_B end pass=19 fail=0 actual_dir=/tmp/qd_v31_selftest_2y3w54b4
```
