# SELFTEST v3.1-b 回执（QuantLab Data，生成 2026-10-18T11:49:26-04:00，date 生成）

- .ok：output/ai_factory/ARCH_SELFTEST_DATA_BACKFILL_R_V3_1_B.ok，sha 58b3494b382555ce8426719d81b486aa8de933be94bded1141893c1fa9b6f356，expires_et 2026-10-18T13:15:00-04:00，运行时未过期；单次使用，Data 未移动，由 Arch 归档。
- cwd：/tmp。命令（逐字，仅追加输出重定向）：```
cd /tmp && PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 /workspace/QuantLab/docs/v2/audit/backfill_1014_1016/selftest_run_backfill_r_v3_1_b.py </dev/null > /workspace/QuantLab/docs/v2/audit/backfill_1014_1016/selftest_v3_1_b_20261018T114908.txt 2>&1
```
- 时间：11:49:08–11:49:10 ET；只跑一次，未重跑。
- **rc=1；pass=16 fail=2**（FAIL：B2「每步结果为 sent/term_ok/killed」、B3「os.kill 实际顺序」）。
- 实际目录：/tmp/qd_v31_selftest_7mev0xy_（out_dir_prefix /tmp/qd_v31_selftest + 随机后缀）。
- 无「非本自测 PID」的 AssertionError；G1 通过（所有被发信号 PID ∈ SPAWNED=[169532,169533,169534,169547]），G2 通过。
- 输出文件：docs/v2/audit/backfill_1014_1016/selftest_v3_1_b_20261018T114908.txt，sha ca79c02978179cece75fe76e22cbef40b60dfbd9550ec9d25183578ea0a69b2b。

## 两项 FAIL 的原因（Data 分析，供 Arch 裁定）
- stop_tree 记录：SIGSTOP 169532(nightly) sent → TERM_KILL 169534(孙) term_ok → TERM_KILL 169533(子) **gone** → SIGKILL 169532 sent。顺序与预期一致（B2 顺序项 PASS）。
- 子进程 169533 在收到 SIGTERM 之前就已退出：替身 fake_child.py 的逻辑是 p.wait() 等孙进程，孙被 TERM 后它自然 exit；父进程 nightly 已被 SIGSTOP，不能收尸，子变为 Z。执行器 signal_exact 按设计把 Z 视为已退出、不发信号（"SIGNAL skip pid=169533 已退出或 Z"），所以实际 os.kill 只有 3 次：STOP nightly、TERM 孙、KILL nightly。
- 即：两项 FAIL 是**替身子进程设计缺陷**（子随孙退出），不是执行器缺陷；执行器的“最深先”顺序、Z 视为退出、发信号前核 cmdline+ppid（B4 每次都 True/True）均表现正确。但「子进程被 TERM」这一路径本次**仍未被实际演练**。
- 若要覆盖：fake_child 应在孙退出后继续存活（例如 p.wait() 后进入 while True: sleep），并另签 selftest .ok。按规则本次不重跑。

## 其余结果
- orphans_run1：**[]（空）**。B5 未起下一步、B6 替身进程全部消失、B8 rc=-9 且 wait 未超时、P3-2 二次 open(x) 抛 FileExistsError、P3-B 反例 refused 且未发信号并由自测按确切 PID 清理（rc=-15），均 PASS。

## pgrep -af [s]cripts/acquire/|[n]ightly_update|[t]drv4
- 前（11:49:06）：仅 `94322 python3 scripts/acquire/remaining_after_stk_surv.py`；probe3/probe4：无。
- 后（11:49:17）：仅 94322。pgrep -af qd_v31_selftest_7mev0xy_：无残留替身进程。

## sha（前 = 后）
- .ok 58b3494b382555ce8426719d81b486aa8de933be94bded1141893c1fa9b6f356
- selftest_b e3d04311393081a6c185c96bfd91df15d1ca5ca4391e4cbae4d30d78e2279e14
- runner c983aed3db32fdaf9398b5977324b91ea0bf4f45591ccbd9da7d7357bfa7ebeb
- 旧 selftest c57ce86080011a998abd3c3b446e35ed0708620f39da88cf9bfd9880dec42ba5

## __pycache__
- ls -la docs/v2/audit/backfill_1014_1016/：无 __pycache__；find /tmp/qd_v31_selftest_7mev0xy_ -name __pycache__：无。

## 完整 stdout+stderr
```
SELFTEST_B start 2026-10-18T11:49:08-04:00 actual_dir /tmp/qd_v31_selftest_7mev0xy_ out_dir_prefix /tmp/qd_v31_selftest ok_keys ['allow_daily_pull', 'allow_delete', 'allow_force', 'allow_network', 'allow_real_data', 'allow_restore_cyq_202610_from_backup', 'allow_run_nightly_update', 'allow_selftest', 'allow_sw_write', 'allow_trade_cal_write', 'cmd', 'expires_et', 'issued_at', 'live', 'ok_id', 'ok_type', 'out_dir_prefix', 'precondition_no_probe_or_plan_r_run', 'precondition_pgrep', 'promotion', 'require_all_cases_pass', 'require_no_repo_pycache', 'require_orphans_run1_empty', 'scope', 'sha_runner', 'sha_selftest', 'sha_selftest_b', 'signed_by', 'signed_et', 'single_use', 'stop_order_expected']
2026-10-18T11:49:08-04:00 RUN1 start npid=169532 cmd=/usr/bin/python3 scripts/nightly_update.py --date 20261016 --steps cyq
TREE_CONFIRMED npid=169532 child=169533(stat=S) grandchild=169534(stat=S)
2026-10-18T11:49:09-04:00 STOP_TREE npid=169532 reason=RSS 采样和 30976 kB > 1
2026-10-18T11:49:09-04:00 SIGNAL SIGSTOP pid=169532 ppid=169531 cmd='/usr/bin/python3 scripts/nightly_update.py --date 20261016 --steps cyq'
2026-10-18T11:49:09-04:00 SIGNAL SIGTERM pid=169534 ppid=169533 cmd='/usr/bin/python3 /tmp/qd_v31_selftest_7mev0xy_/scripts/acquire/fake_grandchild.py'
2026-10-18T11:49:09-04:00 SIGNAL skip pid=169533 已退出或 Z
2026-10-18T11:49:09-04:00 SIGNAL SIGKILL pid=169532 ppid=169531 cmd='/usr/bin/python3 scripts/nightly_update.py --date 20261016 --steps cyq'
2026-10-18T11:49:09-04:00 ORPHAN_SCAN run1 found=0
2026-10-18T11:49:09-04:00 RUN1 end rc=-9 stopped=RSS 采样和 30976 kB > 1 orphans=0 rss_max_sum=30976
PASS B1 子与孙在停树前已确认存活 {"t0": 1792338548.795488, "confirmed_at": 1792338549.2963235, "child": 169533, "grandchild": 169534, "timeout": false}
PASS B2 stop_tree 记录顺序 SIGSTOP nightly → 孙 → 子 → SIGKILL nightly [('SIGSTOP', 169532, 'sent'), ('TERM_KILL', 169534, 'term_ok'), ('TERM_KILL', 169533, 'gone'), ('SIGKILL', 169532, 'sent')]
FAIL B2 每步结果为 sent/term_ok/killed [('SIGSTOP', 169532, 'sent'), ('TERM_KILL', 169534, 'term_ok'), ('TERM_KILL', 169533, 'gone'), ('SIGKILL', 169532, 'sent')]
FAIL B3 os.kill 实际顺序 STOP nightly → TERM 孙 → TERM 子 → KILL nightly [(169532, 19), (169534, 15), (169532, 9)]
PASS B4 每个信号前都核了 cmdline 与 ppid [(169532, 19, True, True), (169534, 15, True, True), (169532, 9, True, True)]
PASS B4 事件日志带 ppid 与 cmd 2026-10-18T11:49:09-04:00 SIGNAL SIGSTOP pid=169532 ppid=169531 cmd='/usr/bin/python3 scripts/nightly_update.py --date 20261016 --steps cyq'
2026-10-18T11:49:09-04:00 SIGNAL SIGTERM pid=169534 ppid=169533 cmd='/usr/bin/python3 /tmp/qd_v31_selftest_7mev0xy_/scripts/acquire/fake_grandchild.py'
2026-10-18T11:49:09-04:00 SIGNAL skip pid=169533 已退出或 Z
2026-10-18T11:49:09-04:00 SIGNAL SIGKILL pid=169532 ppid=169531 cmd='/usr/bin/python3 scripts/nightly_update.py --date 20261016 --steps cyq'
PASS B5 停树后未起下一步 
PASS B6 替身进程全部消失（Z 视为退出） [(169532, None), (169533, None), (169534, None)]
PASS B7 orphans_run1 为空 []
PASS B8 rc 为 -9 且 wait 未超时 rc=-9 wait_timeout=False
PASS P3-2 二次 open(x) 抛 FileExistsError /tmp/qd_v31_selftest_7mev0xy_/logs/nightly/backfill_20261018_run1.out
2026-10-18T11:49:10-04:00 SIGNAL refuse pid=169547 cmdline/ppid 不符（'/usr/bin/python3 /tmp/qd_v31_selftest_7mev0xy_/other/fake_not_acquire.py' ppid=169531 期望 169531），不发信号
PASS P3-B cmdline 不含 scripts/acquire/ → refused res='refused'
PASS P3-B 未发任何信号 kills 3→3
PASS P3-B 拒绝已写日志 
PASS P3-B 进程仍存活 stat=R
PASS P3-B 自测清理后已退出 rc=-15
PASS G1 所有被发信号的 PID 都在 SPAWNED 中 [169532, 169533, 169534, 169547]
PASS G2 守卫拒绝非本自测 PID pid=1 未发信号
STOP_TREE_RECORDS [{"reason": "RSS 采样和 30976 kB > 1", "at": "2026-10-18T11:49:09-04:00", "npid": 169532, "steps": [["SIGSTOP", 169532, "sent"], ["TERM_KILL", 169534, "term_ok"], ["TERM_KILL", 169533, "gone"], ["SIGKILL", 169532, "sent"]]}]
ORPHANS_RUN1 []
KILL_CALLS [[169532, 19], [169534, 15], [169532, 9]]
SELFTEST_B end pass=16 fail=2 actual_dir=/tmp/qd_v31_selftest_7mev0xy_
```
