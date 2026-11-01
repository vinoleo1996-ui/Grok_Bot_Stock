# Arch 增量复核：方案 R 执行器 v3.1（run_backfill_r_v3_1.py）

- 审查人：QuantLab Arch（静态审查，只读）。时间：2026-10-18 11:40 ET（-04:00）。
- 方法：只读源码；未运行执行器与自测，未 import；diff 只在 /tmp/rv31 的副本上用 patch 验证（set -euo pipefail，已核 cd），未在仓库 git apply。
- 前次审查：docs/v2/ARCH_DATA_PLAN_R_R3_REVIEW_ZH.md（FAIL，8338d131）。

## 0. sha 核对
| 文件 | 期望 | 实测 |
|---|---|---|
| run_backfill_r_v3_1.py（922 行） | c983aed3… | c983aed3db32fdaf9398b5977324b91ea0bf4f45591ccbd9da7d7357bfa7ebeb ✔ |
| run_backfill_r_v3_1.diff | 22ffc867… | 22ffc86701639405f34da5f53da5971acffde4c80ab93999fe7c23c8ae655376 ✔ |
| selftest_run_backfill_r_v3_1.py（148 行） | c57ce860… | c57ce86080011a998abd3c3b446e35ed0708620f39da88cf9bfd9880dec42ba5 ✔ |
| run_backfill_r_v3.py（底版） | f006c0b2… | f006c0b2b19de4428d3ec943245e0fae4cbbd991ed1caf8e213205dbae40dd3d ✔ |
| v3 + diff（/tmp 副本 patch） | = v3.1 | c983aed3… ✔ 完全复现 |

## 1. 结论
**PASS_WITH_CONDITIONS。** P1-1、P2-1、P2-2、P2-3（Q4）全部关闭，Q5、Q7、P3-1～P3-8、P3-13 已落实；无新的 P0/P1/P2。剩余均为 P3，不需改码，以签发条件与操作员条件兜住（§4）。sha_runner 可钉 c983aed3db32fdaf9398b5977324b91ea0bf4f45591ccbd9da7d7357bfa7ebeb。allow_restore_cyq_202610_from_backup 可设 true（Q4 八条均满足）。

## 2. 前次发现逐项核对（行号指 v3.1）
| 编号 | 位置 | 结论 |
|---|---|---|
| P1-1 | L485-496、L517、L841-847 | 关闭。run_tool 断言 args[0] 不是解释器（L487），只在 L488 加一次 PY；dry-run 传 c[1:]（L844）；run() 断言 cmd[0]==PY 且 cmd[1]!=PY（L517）。实际 argv 为 nice -n 10 /usr/bin/python3 scripts/nightly_update.py … --dry-run。snap/compare 传 [SNAP,…]，SNAP 为脚本路径，断言通过。不存在必然退出 2 的路径。注意：断言在 python -O 下会被去掉，正式命令未带 -O，可接受。 |
| P2-1 | L228-292、L543-549 | 关闭。顺序：SIGSTOP nightly（核 NIGHTLY_MARK 与 PPID=执行器自身）→ descendants_pp 重读、最深先 TERM→10 s→KILL（每次核 scripts/acquire/ 与期望 PPID）→ SIGKILL nightly；p.wait(60) 超时记 wait_timeout → 退出 3（L861/L888）；orphan_scan 后置。os.kill 全文只有 L237 一处，均为确切 PID；无 pkill/killall/模式杀；94322 在孤儿扫描中显式排除（L279），也不可能是 nightly 子孙。残留见 P3-A、P3-B、P3-C。 |
| P2-2 | L573-599、L719-721、L865-866、L892-893 | 关闭。两次 rc 必须 ==0；summary date==20261016、finished 与 mtime 落在 [start-1, end+1]、所需步骤 status==ok 且无 skipped。只能整份判定的限制已在头注释 L11-12 披露，接受。 |
| P2-3 / Q4 | L651-717、L869-871 | 关闭。唯一调用点 L870（check_cyq 不过）；rc≠0（L866）、compare 不过（L868）、停树（L862）、孤儿（L864）均在其前 finish，不恢复。条件：.ok 键显式 true（L361-364，缺失或非 true/false 即拒签）；备份 sha == SHA256SUMS_pre_run1 == before 快照三方一致（L704-709，快照读不出或路径格式不符→只报告，失败安全）；只写 parquet 与 manifest（同目录 O_EXCL 临时→fsync→核 sha→os.replace→fsync 目录）；parquet 缺失/损坏返回 None 触发（L651-657、L695）；恢复后复核（L713-716）；之后仍 finish(1)（L871）。 |
| Q5 | L746-770 | 关闭。cyq_perf_202610 跳过或缺失即失败（L748）；≥8MB 只记录限于 tier3 20261016 ok 项，记路径/字节/源 sha/原因/目标旧副本 sha（L757-761）。 |
| Q7 / P3-7 | L429-430、L536、L875 | 关闭。run2 前锁 sha 必须等于 run1 前（L875 传 lock_sha_pre）；运行中只记录锁是否存在，不 pgrep。 |
| P3-1 | L902-918 | 关闭。未捕获异常写结果 JSON，未起 run 退出 2、已起 run 退出 1；运行中异常先停树。 |
| P3-2 | L521 | 关闭，open(…,"x")。 |
| P3-3 | L295-366、L875 | 关闭。sha 键、sha_runner、rss_stop_kb 必填；值含 # 拒绝；重复键拒绝；run2 前再核 expires_et。 |
| P3-4 | L394-404 | 关闭，核 cmdline 含 remaining_after_stk_surv.py。 |
| P3-5 | L228-239 | 关闭，parent 必填并核 PPID。 |
| P3-6 | L838-839 | 关闭。--check-only 在 dry-run/备份/快照/运行之前 finish(10)，结果带 mode。 |
| P3-8 | L763-769 | 部分关闭（见 P3-D）。 |
| P3-13 | L23-27 | 关闭，allow_write 已补。 |

## 3. 其他必核项
| 项 | 结论 |
|---|---|
| .ok 解析 | key=value，过期须带时区（L337-341）；OK_PATH 固定在 output/ai_factory/，不会读 _consumed/。缺：DRAFT 全文检查、只接受 '=' 分隔（见 P3-E）。 |
| RSS | 进程树 5 秒采样求和 > 1484800 kB 即停树（L531-539），.ok 必须写 rss_stop_kb=1484800（L353）。 |
| --force / 禁写 | CMD1/CMD2 无 --force，步骤只有 cyq 与 tier3,bundle,freshness；.ok 若把 allow_daily_pull/trade_cal/sw/force/delete 设 true 即拒（L358-360）。 |
| must_not_change | 运行前核 daily_update_status 7991455a、trade_cal 141078fa（L375-378）；run1 后再核 7991455a（L872）；sw_pit 0b1d3432 跑后核（L770）；fa4260b8 只经 freshness 表间接核（L788）；closure 6919e7af 执行器不核（见 P3-F）。 |
| pgrep | L458 以列表 argv 调 pgrep，无 shell，pgrep 自排除，执行器命令行不匹配；与方括号写法等效，接受。 |

## 4. 发现（均为 P3，无 P0/P1/P2）
- **P3-A 孤儿扫描第二分支可能误伤非子孙**（L283-285）：PPID=1、启动晚于本次 run、命令行含 scripts/acquire/ 或 scripts/nightly_update.py 的任何进程都会被 TERM/KILL，不要求是本次 nightly 的子孙。正式运行中有锁与“一次一个真实数据进程”规则，概率低。条件：运行窗口内不得另起任何 acquire/nightly 进程（操作员在 run1 前与结束后留 pgrep -af '[s]cripts/acquire/|[n]ightly_update' 证据，除 94322 外须为空）；回执列出 orphans_run1/run2 每一项。v3.2 建议把第二分支改为只记录。
- **P3-B 停树不覆盖非 acquire 孙进程**（L267-268）：子孙命令行不含 scripts/acquire/ 时 signal_exact 拒发，可能残留；孤儿扫描也只认 acquire/nightly 标记。结果会记 refused，回执须如实列出；如有残留按确切 PID 人工处理。
- **P3-C wait 超时后 nightly 可能仍存活**（L543-549）：若 SIGKILL 被拒（cmdline/PPID 不符），超时后直接退出 3，不再处理 nightly。操作员在退出 3 时须立即 ps 核 npid 并按确切 PID 处理。
- **P3-D（Data 已披露）bundle sha 只核 cyq/* 与 tier3_daily/***（L763-769）：sw_pit 等其他条目由 nightly 从未改动的源复制；源侧 sw_pit 已核 0b1d3432（L770），整体又有快照 compare 579c8605 兜底。影响仅限 output/data_v2_bundle 副本一致性，不碰 data/ 源，不阻断。回执附 bundle.files 全表与其他条目的源/副本 sha。
- **P3-E .ok 解析**：不做 DRAFT 全文检查，接受 ':' 分隔（L302），不检查 single_use/live/promotion。由签发方保证：Arch 签的 .ok 只用 '='、无任何 DRAFT 字样（不区分大小写）、写 live=false、promotion=false。
- **P3-F must_not_change 覆盖不全**：closure 6919e7af 与 fa4260b8 不直接核 sha。条件：操作员在 run1 前与全部结束后各留一次 sha256sum（docs/v2/eng_sd1/paper_import_closure.json、data/v2/calendar/trade_cal_sse_pit.parquet、sw_pit L1），写入回执。
- **P3-G** summary 时间只能整份判定（头注释已披露），接受。
- **P3-H** 前次 P3-9～P3-12 仍按前次处理（回执注明），不阻断。

## 5. 自测隔离裁定
**SAFE_WITH_CONDITIONS——不读不写真实数据；但自测脚本自身在 import 执行器前强制要求 selftest .ok（L5-6、L15-42，缺 .ok 即 sys.exit），所以方案 (a) 书面确认无法让它跑起来，必须走 (b) 签 ARCH_SELFTEST_DATA_BACKFILL_R_V3_1.ok。**

| 风险点 | 位置 | 判断 |
|---|---|---|
| 执行器 import 期副作用 | runner L33-92 | 只有常量、dict、ZoneInfo；无文件读写、无子进程、无信号、无网络；main 由 __name__ 守护（L921）。安全。 |
| 路径重定向 | selftest L46-49、L98、L112 | ROOT、SNAP_DIR、BK、QUIET_LOCK、SUMMARY 均改到 mkdtemp 的 /tmp/qd_v31_selftest_*。run_tool/run 在调用时读全局 ROOT 作 cwd 与输出路径，故落在 W。import 期派生的 OK_PATH、SNAP、SCOPE、RESULT_DIR 仍指真实路径，但只被 check_ok/snap/compare/finish 使用，自测都不调用。安全。 |
| 子进程 | selftest L67-74、L86-100 | 只起 W 下的替身 nightly_update.py 与 W/scripts/acquire/fake_step.py；cwd=W，相对路径解析到替身。不起真 nightly、不起真工具。 |
| 网络 / tushare | selftest L141-144 | quiet_gate 在锁 sha 不符处提前返回（runner L429-430），不访问 healthz，不 pgrep；无 tushare 调用；pyarrow 未调用。 |
| 信号——停树 | runner L259-269 | 只对替身 nightly（PPID=自测进程）与其子孙发信号。安全。 |
| 信号——孤儿扫描（主要风险） | runner L272-291（自测 L100 经 run() 触发） | 扫描全 /proc：PPID=1、启动晚于自测 run 开始、命令行含 scripts/acquire/ 或 scripts/nightly_update.py 的真实进程会被 TERM/KILL。94322 被排除且启动更早，不受影响。只在自测运行的几秒内有风险。 |
| 字节码写入仓库 | selftest L43-44 | exec_module 可能在 docs/v2/audit/backfill_1014_1016/__pycache__ 写 .pyc；须设 PYTHONDONTWRITEBYTECODE=1。 |
| 只读的真实文件 | selftest L11-19、L43 | 只读 selftest .ok 与执行器源码，不读价格/因子数据。 |

自测运行条件：
1. 签 output/ai_factory/ARCH_SELFTEST_DATA_BACKFILL_R_V3_1.ok：ok_type=selftest、scope=selftest、allow_selftest=true、allow_real_data=false、其余 allow_* 全为 false、out_dir=/tmp/qd_v31_selftest（只用于满足 /tmp 前缀检查）、sha_selftest=c57ce86080011a998abd3c3b446e35ed0708620f39da88cf9bfd9880dec42ba5、sha_runner=c983aed3db32fdaf9398b5977324b91ea0bf4f45591ccbd9da7d7357bfa7ebeb、expires_et=2026-10-18T13:15:00-04:00；只用 '='，无行内注释，无 DRAFT 字样。
2. 命令：cd /tmp && PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 /workspace/QuantLab/docs/v2/audit/backfill_1014_1016/selftest_run_backfill_r_v3_1.py </dev/null（cwd 用 /tmp，不用仓库目录）。
3. 运行前后各一次 pgrep -af '[s]cripts/acquire/|[n]ightly_update'，除 94322 外须为空；运行期间不得另起 acquire/nightly 进程；不在方案 R 正式运行期间跑。
4. 运行前后 sha256sum 两份被测文件，须不变；运行后确认仓库目录下未出现 __pycache__。
5. 回传：完整 stdout、W 目录路径、pass/fail 计数、结果中 stop_tree 与 orphans_run1 记录；orphans_run1 必须为空列表（非空即说明误伤风险已兑现，立即报 Arch）。
6. 一次性；用后由 Arch 归档到 _consumed/。

## 6. 发现汇总
| 级别 | 编号 | 位置 | 内容 |
|---|---|---|---|
| P3 | P3-A | L283-285 | 孤儿扫描 PPID=1 分支可误伤非子孙；以操作员条件兜住，v3.2 改为只记录 |
| P3 | P3-B | L267-268 | 非 acquire 孙进程不停，可能残留 |
| P3 | P3-C | L543-549 | wait 超时后 nightly 可能仍存活 |
| P3 | P3-D | L763-769 | bundle sha 只核 cyq/* 与 tier3_daily/*（已披露） |
| P3 | P3-E | L295-366 | 不查 DRAFT，接受 ':'，不查 single_use/live/promotion |
| P3 | P3-F | L369-382、L770、L788 | closure 6919e7af、fa4260b8 不直接核 sha |
| P3 | P3-G | L11-12、L573-595 | summary 只能整份判定（已披露） |
无 P0/P1/P2。总体：PASS_WITH_CONDITIONS；自测：SAFE_WITH_CONDITIONS（须签 selftest .ok）。
