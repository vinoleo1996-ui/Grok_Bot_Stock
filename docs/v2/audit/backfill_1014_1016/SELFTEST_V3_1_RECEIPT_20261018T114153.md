# SELFTEST v3.1 回执（QuantLab Data，生成 2026-10-18T11:41:53-04:00，date 生成）

- .ok：output/ai_factory/ARCH_SELFTEST_DATA_BACKFILL_R_V3_1.ok，sha bf1f1e11e930fab0fa7e07a7436a32faeadeee3db0c3574275b2b14909c06bc7，expires_et 2026-10-18T13:15:00-04:00，运行时未过期；单次使用，由 Arch 归档（Data 未移动）。
- 命令（逐字）：```
cd /tmp && PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 /workspace/QuantLab/docs/v2/audit/backfill_1014_1016/selftest_run_backfill_r_v3_1.py </dev/null > /workspace/QuantLab/docs/v2/audit/backfill_1014_1016/selftest_v3_1_20261018T114138.txt 2>&1
```
- cwd：/tmp；开始 2026-10-18T11:41:41-04:00，结束 11:41:42-04:00；**rc=0**；只跑一次。
- 结果：**pass=21 fail=0**。替身工作目录 /tmp/qd_v31_selftest_xavkbpeu（mkdtemp；.ok 的 out_dir=/tmp/qd_v31_selftest 只作 /tmp 前缀校验，实际目录名带随机后缀，如实披露）。
- 输出文件：docs/v2/audit/backfill_1014_1016/selftest_v3_1_20261018T114138.txt，sha e305ff796b6b74d9eda4004f9c2fb4c6c6891096aa7b9afb76382fcfe4672572。

## pgrep -af [s]cripts/acquire/|[n]ightly_update
- 前（11:41:38）：`94322 python3 scripts/acquire/remaining_after_stk_surv.py`（仅 94322）
- 后（11:41:4x）：`94322 python3 scripts/acquire/remaining_after_stk_surv.py`（仅 94322）

## 文件 sha（前 = 后，未变）
- run_backfill_r_v3_1.py：c983aed3db32fdaf9398b5977324b91ea0bf4f45591ccbd9da7d7357bfa7ebeb
- selftest_run_backfill_r_v3_1.py：c57ce86080011a998abd3c3b446e35ed0708620f39da88cf9bfd9880dec42ba5

## __pycache__
- `ls -la docs/v2/audit/backfill_1014_1016/`：无 __pycache__（只有 run_backfill_r*.py、v3_1.diff、selftest 脚本与输出）。

## stop_tree 记录
- npid=157827，原因「RSS 采样和 452 kB > 1」（自测把 RSS_STOP_KB 设为 1 以强制触发）；步骤：SIGSTOP 157827 sent（ppid=157824 核对通过）→ SIGKILL 157827 sent；rc=-9，wait 未超时。

## orphans_run1
- **[]（空）**，ORPHAN_SCAN run1 found=0。

## 局限（如实披露，供 Arch 判断）
- 停树在**第一次采样**即触发，此时替身 nightly 尚未起子进程，descendants 为空，所以「子孙最深先 TERM→KILL」与 PPID 核对只覆盖了 nightly 本身，**子孙路径未被实际演练**；「nightly 未起下一步」与「孤儿为空」在此场景下是弱证据。
- 「P3-2 runN.out 用 x」一项只验证文件已创建，未验证二次打开会失败（代码 L521 为 open(out_path, "x")）。
- 如需补测子孙路径，须改自测（例如首次采样前等待子进程出现）并另签 selftest .ok。

## 完整 stdout+stderr
```
SELFTEST start 2026-10-18T11:41:41-04:00 workdir /tmp/qd_v31_selftest_xavkbpeu ok_keys ['allow_daily_pull', 'allow_delete', 'allow_force', 'allow_network', 'allow_real_data', 'allow_restore_cyq_202610_from_backup', 'allow_run_nightly_update', 'allow_selftest', 'allow_sw_write', 'allow_trade_cal_write', 'cmd', 'expires_et', 'issued_at', 'live', 'ok_id', 'ok_type', 'out_dir', 'precondition_no_plan_r_run', 'precondition_pgrep', 'promotion', 'require_no_repo_pycache', 'require_orphans_run1_empty', 'review_doc_sha', 'scope', 'sha_runner', 'sha_selftest', 'signed_by', 'signed_et', 'single_use']
PASS P1-1 dryrun cmd1 rc==0 rc=0
PASS P1-1 dryrun cmd1 argv==CMD[1:]+--dry-run ['scripts/nightly_update.py', '--date', '20261016', '--steps', 'cyq', '--dry-run']
PASS P1-1 cmd1 解释器只出现一次 ['nice', '-n', '10', '/usr/bin/python3', 'scripts/nightly_update.py', '--date', '20261016', '--steps', 'cyq', '--dry-run']
PASS P1-1 dryrun cmd2 rc==0 rc=0
PASS P1-1 dryrun cmd2 argv==CMD[1:]+--dry-run ['scripts/nightly_update.py', '--date', '20261016', '--steps', 'tier3,bundle,freshness', '--dry-run']
PASS P1-1 cmd2 解释器只出现一次 ['nice', '-n', '10', '/usr/bin/python3', 'scripts/nightly_update.py', '--date', '20261016', '--steps', 'tier3,bundle,freshness', '--dry-run']
PASS P1-1 assert 拒绝重复解释器 
PASS P3-3 行内注释被拒 ['L2 allow_restore_cyq_202610_from_backup 含行内注释']
2026-10-18T11:41:41-04:00 RUN1 start npid=157827 cmd=/usr/bin/python3 scripts/nightly_update.py --date 20261016 --steps cyq
2026-10-18T11:41:41-04:00 STOP_TREE npid=157827 reason=RSS 采样和 452 kB > 1
2026-10-18T11:41:41-04:00 SIGNAL SIGSTOP pid=157827 ppid=157824 cmd='nice -n 10 /usr/bin/python3 scripts/nightly_update.py --date 20261016 --steps cyq'
2026-10-18T11:41:41-04:00 SIGNAL SIGKILL pid=157827 ppid=157824 cmd='nice -n 10 /usr/bin/python3 scripts/nightly_update.py --date 20261016 --steps cyq'
2026-10-18T11:41:41-04:00 ORPHAN_SCAN run1 found=0
2026-10-18T11:41:41-04:00 RUN1 end rc=-9 stopped=RSS 采样和 452 kB > 1 orphans=0 rss_max_sum=452
PASS P2-1 第一步是 SIGSTOP nightly [('SIGSTOP', 157827, 'sent'), ('SIGKILL', 157827, 'sent')]
PASS P2-1 最后一步是 SIGKILL nightly [('SIGSTOP', 157827, 'sent'), ('SIGKILL', 157827, 'sent')]
PASS P2-1 wait 未超时且已停 'RSS 采样和 452 kB > 1'
PASS P2-1 无存活子孙 [157827]
PASS P2-1 nightly 未起下一步 
PASS P3-2 runN.out 用 x（再开同名应失败） /tmp/qd_v31_selftest_xavkbpeu/logs/nightly/backfill_20261018_run1.out
PASS P2-1 孤儿扫描已记录 []
PASS P2-2 陈旧 finished 被拒 ["summary finished='2026-10-18T16:59:22+08:00' 不在本次 t_stale 窗口 a–b"]
PASS P2-2 本次 summary 通过 []
2026-10-18T11:41:42-04:00 cyq 恢复未授权，只报告
PASS Q4 未授权只报告 report_only（.ok allow_restore_cyq_202610_from_backup=false）
2026-10-18T11:41:42-04:00 cyq 恢复：data/v2/cyq/manifest.json sha 三方不一致，只报告
PASS Q4 sha 不一致只报告 report_only（data/v2/cyq/manifest.json 三方 sha 不一致）
2026-10-18T11:41:42-04:00 cyq 判 FAIL 且 202610 parquet rows=None：按备份原子恢复
2026-10-18T11:41:42-04:00 RESTORE data/v2/cyq/cyq_perf_202610.parquet sha_ok=True
2026-10-18T11:41:42-04:00 RESTORE data/v2/cyq/manifest.json sha_ok=True
PASS Q4 损坏 parquet 触发恢复并复核 {"trigger_parquet_rows": null, "allowed": true, "files": {"data/v2/cyq/cyq_perf_202610.parquet": {"backup": "32d3e9cccc33d6bd97426e1c7e2b0687b81b8e7b7b95e327f3e32aee0e9da4d1", "sums": "32d3e9cccc33d6bd97426e1c7e2b0687b81b8e7b7b95e327f3e32aee0e9da4d1", "before_snap": "32d3e9cccc33d6bd97426e1c7e2b0687
PASS Q7 锁 sha 变化被拒 'RESEARCH_QUIET.lock sha 与 run1 前不同（c93ff10b0d2b609969056eaf7fc4de94301ba7df041f10b2bdc3371c58ac3f20 != 0000000000000000000000000000000000000000000000000000000000000000，t）'
SELFTEST end pass=21 fail=0 workdir=/tmp/qd_v31_selftest_xavkbpeu
```
