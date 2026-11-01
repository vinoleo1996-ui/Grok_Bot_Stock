# Arch 审查：方案 R 补跑 .ok 申请 r3 / r3.1 与执行器 v3（run_backfill_r_v3.py）

- 审查人：QuantLab Arch（静态审查，只读）。审查时间：2026-10-18 11:23–11:45 ET（-04:00）。新文件，不改任何被审文件。
- 方法：只读源码与元数据；**未运行执行器（含 --check-only）**、未 import 项目代码、未 git apply；草稿在 /tmp/arch_r3_review（set -euo pipefail，已核 cd）。唯一的“执行”是在 /tmp 验证一条与项目无关的解释器行为：`/usr/bin/python3 /usr/bin/python3 --version` → `SyntaxError: source code cannot contain null bytes`，rc=1（见 P1-1）。

## 0. sha 核对（全部先核，全部一致）
| 文件 | 期望 | 实测 |
|---|---|---|
| docs/v2/audit/BACKFILL_1014_1016_OK_REQUEST_ZH_r3.md | 76e5f1f1… | 76e5f1f1cc6f70e3c243cde7142bd0673a1f822df82ea90b13c8bc07ba5e4bd7 ✔ |
| docs/v2/audit/BACKFILL_1014_1016_OK_REQUEST_ZH_r3_1.md | 4c7f7ad8… | 4c7f7ad823bffe5a5f06ddb7f3dadd1c9be34cea643edc4b1b5eb0fbb18a36d0 ✔ |
| docs/v2/audit/backfill_1014_1016/run_backfill_r_v3.py（690 行） | f006c0b2… | f006c0b2b19de4428d3ec943245e0fae4cbbd991ed1caf8e213205dbae40dd3d ✔ |
| docs/v2/ARCH_DATA_TIMELINE_1019_AND_PLAN_R_REVIEW_ZH.md（前次审查） | 717c3e7c… | 717c3e7c642a7edf8bc05b23d02c8b4a74948938c146df5e149562502b46cbac ✔ |
| docs/v2/audit/BACKFILL_1014_1016_OK_REQUEST_ZH_r2.md | 2aad5036… | 2aad50362823808c2b53628d130e9f70deb1d567e32b82299cf0476490ac4e67 ✔ |
| 执行器 PINS 八项（nightly ec079d56、relay_health 6d3ea9f5、cyq 6aae6c1b、tier3 64a71f56、freshness a759d297、tushare_proxy ae91f230、快照 v2 c930ed5c、范围 579c8605） | 同前次 §9 | 全部一致 ✔ |
| output/daily_update_status.json / tushare_raw/trade_cal.parquet / sw_pit L1 | 7991455a / 141078fa / 0b1d3432 | 一致 ✔ |
| 备用 r3.2 DATA_DAILY_FALLBACK_PUBLIC_SOURCE_PLAN_ZH_r3_2.md | 23d97884… | 23d9788492f08c342f477c50fe6c03afb635720af13fe52b4f647c34f0de017b ✔（P3-7 关闭） |
| docs/v2/eng_sd1/paper_import_closure.json | 6919e7af… | 6919e7afe605cc4d1af48868a06b6550db66e3fd1923a3e61bdcc16c621bae20 ✔（156 项） |

现场只读状态（11:27 ET）：94322 为 `Ssl`（`python3 scripts/acquire/remaining_after_stk_surv.py`，etime 10:03:47），**不是 T**；RESEARCH_QUIET.lock 不存在；方案 R .ok 不存在；/tmp/arch1018 存在且无 backfill_* 产物；_recovery/data 存在、_recovery/data/backfill_1014_1016 不存在。

## 1. 结论
**FAIL（执行器 f006c0b2 不可钉、不可签）；设计层面通过。** 有一条阻断性 P1：第 0 步 dry-run 的命令把解释器拼了两次，执行器每次都会在 dry-run 处以退出码 2 结束，补跑永远起不来，而且会白白用掉单次 .ok。另有三条 P2 须同批修。修成 v3.1（新文件、不覆盖）并附增量 diff 后，Arch 做快速增量复核；P1-1、P2-1、P2-2、P2-3 全部关闭即可按 §6 的键值签发（仍需两轮 stock_basic 探测与 94322=T 证据）。13:30 ET 签发线不变。

我先前要求的各项，在 v3 里的落实情况见 §2；除 §3 所列，其余均已满足。

## 2. 方案 R 必备性质逐项核对（行号均指 run_backfill_r_v3.py）
| 要求 | 位置 | 结论 |
|---|---|---|
| 两条命令严格串行、无 &、无并发 | CMD1/CMD2 L47-48；run() 用 Popen + poll + wait（L412-430）；main 顺序 L641-686；快照、dry-run 用 subprocess.call 同步 | 满足 |
| 子进程命令行与两条命令逐字一致 | L47-48 为 `/usr/bin/python3 scripts/nightly_update.py --date 20261016 --steps cyq` 与 `… --steps tier3,bundle,freshness`；前缀仅 `nice -n 10`（nice 以 exec 替换，NPID 即 python）；env 加 PYTHONDONTWRITEBYTECODE=1；stdin=/dev/null | 满足（dry-run 处见 P1-1） |
| cyq 只跑一次、new_days=3 | 只起一次 run1；判定 months.202610.new_days==3、days==7、range==[20261008,20261016]、fails==[]（L481-484） | 满足 |
| 5 秒自动 RSS 采样，> 1484800 kB 按确切 PID 停（硬线 1536000） | L49-51、L418-429；先子后父 TERM→10 s→KILL（L197-218）；发信号前核 cmdline（L184-194）；采样日志 open x（L409） | 基本满足，停进程顺序有缺陷见 P2-1 |
| 进程树 RSS 求和 | L419-422：NPID + /proc/<pid>/task/*/children 递归；本机该接口存在（已只读核 /proc/17541/task/17541/children） | 满足；Q6 同意 |
| 快照 v2 c930ed5c、范围 579c8605 | PINS L33-34；snap/compare 均带 --expect-scope-sha（L391、L397）；compare rc≠0 或含 META_ONLY_FAIL 即不过（L400） | 满足 |
| 备份两个 cyq bundle 副本 | BK_RUN1 L57-60 共 10 项 | 满足（P3-6 关闭） |
| 备用 r3.2 sha 23d97884 | r3 L15 已更正；实测一致 | 满足（P3-7 关闭） |
| 两轮探测，大页判据 stock_basic list_status=L limit=5000 恰好 5000 行 | r3_1 L33-40 | 文档满足；属签发前证据，执行器不核，由 .ok 前置条件约束 |
| 94322 为 T（或已退出）并留 ps | check_94322 L297-305，run1 前与 run2 前各一次，结果写 checks.p94322 | 满足；PID 复用风险见 P3-4 |
| quiet 前置：锁须已存在，执行器不建不删 | L327-328；全文无任何对 QUIET_LOCK 的写/删（grep 只见 L309/L325-330 读） | 满足 |
| 轮询 healthz 至 quiet=true（≤90 s）→ 再等 15 s → 复核三个 running=false、child_pids={} → pgrep 为空 | L331-356；每 3 s，单次超时 5 s，最坏约 95 s | 满足 |
| run2 前短复核 | L668：time_gate(2)、check_94322、quiet_gate(full=False)（锁仍在 + healthz 复核 + pgrep） | 满足；Q7 见 §4 |
| pgrep 不会匹配到自己 | L353 以列表 argv 调 pgrep（无 sh -c，模式不出现在任何 shell 命令行）；pgrep 自身排除自己；执行器命令行 run_backfill_r_v3.py 不匹配四个模式；快照工具 …snapshot_v2_20261018.py 不匹配 snapshot.py（r3_1 L30 论证正确）；全闸门期间执行器无子进程 | 满足。注意：tier3_daily_snapshot.py 会匹配，只能在 run2 之前做 pgrep，不得把 pgrep 加进运行中采样 |
| 15:55 截止与过期 | .ok expires_et 带时区且未过期（L248-252）；运行中每 5 s 比 at(15:55)（L427-428）→ stop_tree → 退出 3（L659-660、L679-680） | 满足（停树缺陷同 P2-1） |
| 退出码 0/1/2/3 | L631/634/636/645/650/658 → 2；L662/664/666/670/674/682/684 → 1；L660/680 → 3；L686 → 0 | 主路径满足；未捕获异常会以 1 退出且不写结果，见 P3-1 |
| --check-only 真的什么都不跑 | L637-638 在 dry-run、备份、快照、run 之前 finish(0)；此前只做：读 .ok、哈希钉文件、读 /proc/94322、读锁、GET 127.0.0.1:8795/healthz、pgrep；唯一写入为结果 JSON（finish L613-617，在 RESULT_DIR，属 allow_write） | 满足（不触网、不读价格值、不起 nightly）；退出 0 与全通过同码，见 P3-6 |
| 跑后行数与日期范围核对 | cyq：日志每日行数 ≥5000、原始 num_rows==日志、months.202610.rows==22238+三日之和、parquet num_rows==manifest rows、202601-09 条目不变、顶层 date_range 止于 20261016（L449-497）；range/days 由 cyq_perf_monthly.py L59 从真实数据计算，非自报常量。tier3：summary 状态、manifest 行数区间、num_rows==manifest、10-14/15 sha 不变（L527-555）；freshness 生成时刻在 run2 窗口、expected=20261016、overall ok、T 表与跑前一致、cyq_perf_raw lag 0（L570-594）；MUST 项（含 cyq ≤1013 原始、202601-09 月表、tier3 10-13/14/15、closure 156 项、SW 两份冻结文件）由快照 compare 保证 | 基本满足；未核 nightly rc 与 summary 新鲜度，见 P2-2 |
| 只写声明范围；不启停 94322、不移 .ok、不删文件；不碰冻结/纸面 | 写入点仅 L111-121（自身临时文件）、L363-374（_recovery 备份）、L382/L409/L411（/tmp/arch1018 与 logs/nightly/backfill_*.out）、L503-519（cyq 恢复）、L613-616（结果 JSON）；os.kill 仅在 signal_exact，对象仅 NPID 子孙；unlink 仅删自建临时文件；无 shutil.move / rename .ok | 满足；allow_write 需补几项见 P3-13 |
| 时间取系统时钟并带时区 | now()=datetime.now(ZoneInfo(America/New_York))，isoformat 带 -04:00（L73-78） | 满足 |

## 3. 发现
### P1
- **P1-1（阻断）dry-run 解释器重复，执行器必然以 2 退出**：L642 `run_tool(c + ["--dry-run"], …)`，c 为 CMD1/CMD2，首元素已是 PY（L47-48）；run_tool 又在前面加 `["nice","-n","10",PY]`（L383）。实际执行的是 `nice -n 10 /usr/bin/python3 /usr/bin/python3 scripts/nightly_update.py … --dry-run`，Python 把 ELF 文件当脚本读入，rc=1（已在 /tmp 用 `--version` 等价复现）。于是 L644-645 每次 finish(2)。后果：补跑起不来；dry-run 在备份之前，所以不会写数据，但单次 .ok 会被用掉。修法：`run_tool(c[1:] + ["--dry-run"], …)`，并加断言 `c[0] == PY`。v3.1 须附一次 /tmp 替身自测（例如把 nightly 换成只打印 argv 的替身脚本），证明拼出的 argv 与 CMD 一致。

### P2
- **P2-1 停树时父进程会继续跑下一步并留下孤儿**（L197-218，对照 nightly_update.py L104-127）：stop_tree 先逐个停子进程，然后最多等 10 s 让 NPID 自己退出。但 nightly 不会因子进程被杀而退出，它把该步记为 fail rc=-15 后继续下一步。run2 的情形：tier3 被停 → 这 10 s 内 nightly 执行 bundle（把 tier3 半成品复制进 output/data_v2_bundle）→ 起 freshness 子进程 → 执行器才 TERM NPID，freshness 子进程被 init 收养，不在跟踪范围内，继续写 output/data_freshness_status.json。另外，若 NPID 的 cmdline 核对不符被拒发信号，L430 的 p.wait() 会无限阻塞。修法：(1) 先对 NPID 发 SIGSTOP（核 cmdline 含 scripts/nightly_update.py），冻结它、不让它起下一步；(2) 重读子孙，最深者先 TERM→10 s→KILL；(3) 对 NPID 发 SIGKILL（或 TERM 后 CONT）；(4) NPID 退出后扫一遍 /proc：凡 cmdline 含 scripts/acquire/ 且 PID 在 pids_seen 中，或 PPID=1 且启动时刻晚于 run 开始，一律记录，并按确切 PID 停；(5) p.wait 加超时（例如 60 s），超时记录后退出 3。
- **P2-2 未核 nightly 退出码，也未排除陈旧 summary**（L654-664、L676-684）：r1["rc"]、r2["rc"] 从未参与判定。当前 logs/nightly/20261016_summary.json 里已有旧的 `bundle: ok`、`freshness: ok`（finished 2026-10-18T16:59:22+08:00）。如果 nightly 在写 summary 前异常退出（rc≠0），check_run2 读到的 bundle/freshness 状态就是旧的。其他判据大概率能拦住，但不能只靠“大概率”。修法：run1、run2 都要求 rc==0 才进入判定，否则退出 1；check_cyq 与 check_run2 都要核 summary.finished 落在本次 run 的开始与结束之间，date=="20261016"。（rc==0 只是必要条件，不是充分条件。）
- **P2-3 cyq 自动恢复与 Q4 的条件不符**（L494-500、L503-525；r3 L51、L121）：(a) 执行器不读 .ok 的 allow_restore_cyq_202610_from_backup，恢复无条件执行；(b) 恢复的目标 sha 取自 SHA256SUMS_pre_run1（备份时刻），没有与快照 backfill_before.txt 中同一路径的 sha 交叉核对；(c) 若 cyq_perf_202610.parquet 半写或损坏，L494 的 num_rows 会抛异常，被 guarded 吞掉（L600-607），恰恰在最需要恢复的时候不恢复；(d) 恢复后没有复核两文件与 before 快照一致。处理见 Q4 裁定。

### P3
- **P3-1 未捕获异常破坏退出码契约、丢结果文件**：backup 的 SystemExit（L368、L372，退出码 1）、os.mkdir 已存在（L363）、open(…,"x") 目标已存在（L382、L409）、healthz 返回非 dict 时 h.get 报 AttributeError（L338）。这些都会以 1 退出、不写结果 JSON，其中多数发生在任何运行之前，按契约应为 2。修法：main 整体 try/except，未起 run 时 finish(2)，已起 run 时 finish(1)，异常写入 R。
- **P3-2** L411 运行日志 logs/nightly/backfill_20261018_runN.out 用 "a" 打开，应为 "x"（与其余新文件规则一致）。
- **P3-3** check_ok 对 sha_* / scope_sha / sha_runner / rss_stop_kb 用“写了才核”（L253-260），应改为必须存在；run2 起跑前再核一次 expires_et。另外，.ok 值里**不得带行内注释**：parse_ok（L228）会把 `true   # …` 整段当值，truthy 判为假（r3 §7 L118 的写法照抄会出错）。
- **P3-4** check_94322 只看状态（L297-305），应同时核 cmdline 含 remaining_after_stk_surv.py，防 PID 复用。
- **P3-5** stop_tree 调 signal_exact 未传 parent（L200、L205、L213、L218），应传期望 PPID。现在仅靠 must_contain=scripts/acquire/ 过滤，而 94322 的命令行也含 scripts/acquire/，虽然它不可能出现在 NPID 子孙里，但应加 PPID 双保险。
- **P3-6** --check-only 与全通过同为 finish(0)（L638）；结果 JSON 加 mode=check_only|full。check-only 只能在 .ok 已签、锁已设、94322 已 T 之后跑（L628-636），不消耗 .ok（不起 nightly），最多一次。
- **P3-7** run2 前复核时，比对锁文件 sha 与 pre_run1 相同（同一把锁，未被他人重建）；运行中每次采样顺带记录锁是否仍在（只记录不停进程），不得在运行中做 pgrep（tier3_daily_snapshot.py 会匹配）。
- **P3-8** bundle 只核 need 列表（L558-567）；建议对 bundle.files 中所有非 SKIP 条目都核副本 sha == 源 sha。
- **P3-9** cyq_perf_monthly.py L61-66 不更新 manifest 的 sha256 映射，跑后 cyq/cyq_perf_202610.parquet 的 sha256 仍是旧值 604c1a38…；回执如实记录，不判失败，另行处理。
- **P3-10**（建议，不阻断）月表日期独立核对：只读 cyq_perf_202610.parquet 与三份原始日文件的 trade_date 列，逐日计数须等于原始 num_rows，20261008-13 计数等于跑前（由备份月表同列得出）。现有判据中 days==7 与 range 由 cyq L59 从真实数据计算，已能覆盖日期范围，所以本项只作加强。
- **P3-11** 范围文件 579c8605 头部 L2 仍写“用 v1 快照脚本”，已被 r3 取代；文件已钉，不改，在回执注明。
- **P3-12** r3 §1（L18-26、L106）仍写执行器 v2 与 --quiet-evidence，已被 r3_1 改动 1 取代；签发以 r3_1 为准。
- **P3-13** allow_write 需补：logs/nightly/20261016_freshness.log（范围内 EXPECTED，前次 §9 漏列）；output/data_freshness_status.tmp（freshness L85 的临时文件）；data/v2/cyq/.cyq_perf_202610.parquet.restore_tmp.* 与 .manifest.json.restore_tmp.*（仅当 Q4 允许）；各写入目录内执行器 write_new 的 .*.tmp.<pid>。
- Data 自报 P3（/tmp/qd1018 用 heredoc 写补丁）：在项目目录之外，已改正，记录，不另行处理。

## 4. Data 问题裁定
- **Q4 自动恢复：有条件允许（维持我的倾向；现码不满足，须 v3.1 改）**。条件：(1) 只有 .ok 写 allow_restore_cyq_202610_from_backup=true 时才执行，执行器必须读这个键；(2) 恢复前，备份文件 sha == SHA256SUMS_pre_run1 == backfill_before.txt 中该路径的 sha，三者一致才恢复，任一不一致只报告；(3) 只写 data/v2/cyq/cyq_perf_202610.parquet 与 data/v2/cyq/manifest.json，沿用 L503-519 的同目录 O_EXCL 临时文件 → fsync → 核 sha → os.replace → fsync 目录；(4) 202610 parquet 不可读或缺失也视同“低于 22238 行”，触发恢复；(5) 恢复后复核两文件 sha == before 快照，结果写 checks.cyq_restore；(6) 无论恢复成功与否都退出 1，不起 run2；(7) 只在 check_cyq 判不过这一条路径上恢复，compare 不过（退出 1）或停树（退出 3）路径只报告，由 Arch 人工裁定；(8) 新落盘的 2026101{4,5,6}.parquet 原始日文件不删、不动，原样报告（它们 >10000 字节会被 cyq L44 永久跳过，须在回执标出）。若 Data 不愿在 13:30 前实现这些，改为只报告（删去 L498-499），.ok 写 allow_restore_cyq_202610_from_backup=false。
- **Q5 ≥8MB 的 bundle 文件只记录不判失败：有条件同意**。条件：(1) 记录路径、字节数、源 sha、原因（nightly_update.py L77/L81 size≥8e6，未复制），并记录目标位置是否已有旧副本及其 sha；(2) 仅限 tier3 的 20261016 新文件（不在范围清单内）；(3) cyq/cyq_perf_202610.parquet 在范围内属 EXPECTED（scope L48），判据是“副本 sha == 源 sha”，它若因 ≥8MB 被跳过，会留下陈旧副本，必须判失败、退出 1（同时核 summary.bundle.files 中的 `SKIP>8MB cyq_perf_202610.parquet`）。实测 cyq_perf_202610.parquet 453234 字节，tier3 最大的 10-15 文件 407364 字节，实际触发的可能性极低。
- **Q6 RSS 以进程树求和为准：同意**。和 ≥ 任一单进程，单进程硬线 1536000 自然满足；共享页会被重复计入，偏保守，可接受；结果里同时保留 rss_max_single_kb（L423、L433）。如实写明这是 5 秒采样峰值。
- **Q7 run2 前只做短复核：够用（确认我的倾向，现码已满足）**。L668 已包含：锁仍存在、healthz 复核（quiet=true、三个 running=false、child_pids={}）、pgrep 为空、94322 仍为 T（或已退出）、run2 最晚开始时间。healthz 是约 30 s 的缓存值，但锁存在与 pgrep 都是直接核验，足以兜底；不必重复 90 s 轮询和 15 s 等待。补充 P3-7：比对锁 sha 与 run1 前相同。

## 5. 签发前剩余前置条件
1. Data 出 run_backfill_r_v3_1.py（新文件，不覆盖）+ 增量说明 + 对 v3 的 diff，关闭 P1-1、P2-1、P2-2、P2-3（Q4 二选一），P3 尽量同批；附 /tmp 替身自测输出（不碰项目数据）。Arch 增量复核通过后，才把 sha_runner 填为 v3.1 实测 sha。f006c0b2、28bc5e0e、1e81c4f1 三版一律不钉。
2. 两轮中转探测：每轮 trade_cal SSE 20261014–20261020 返回 7 行，且 stock_basic list_status=L limit=5000 第 1 页恰好 5000 行，连续两轮通过；写入 docs/v2/audit/relay_probe_20261018/probe_log.csv，签发时钉其 sha。
3. 94322：kill -STOP 后 `ps -o pid,ppid,stat,etimes,rss,args -p 94322` 与 /proc/94322/stat 第 3 字段 = T（Data 证据）。
4. 锁：由 Arch/操作员按模板设 RESEARCH_QUIET.lock；按 11:20 新规，设锁后轮询 healthz 至 quiet=true（≤90 s），再等 15 s，留 healthz 与 pgrep 证据；锁在期间不签其他 .ok。
5. 签发时重算 §6 表中所有 sha，任一不同即不签；13:30 ET 前签不出，今天的补跑放弃。

## 6. .ok 键值表（v3.1 复核通过、探测与 94322=T 证据到位后签）
格式 key=value，LF，无行内注释；signed_et / issued_at 取 `date +%Y-%m-%dT%H:%M:%S%:z`。执行器实际解析的键已用 ★ 标出，必须逐字使用这些键名。
| key | value |
|---|---|
| ok_id ★ | ARCH_RUN_AUTH_DATA_BACKFILL_1014_1016_PLAN_R |
| ok_type ★ | run |
| path | output/ai_factory/ARCH_RUN_AUTH_DATA_BACKFILL_1014_1016_PLAN_R.ok（Arch 写） |
| signed_by | QuantLab Arch |
| signed_et / issued_at | 签发时 date 生成 |
| expires_et ★ | 2026-10-18T15:55:00-04:00 |
| single_use | true（用后移 output/ai_factory/_consumed/，sha8 + CONSUMED/VOID + ET 时间；只由 Arch 归档） |
| live / promotion | false / false |
| interpreter | /usr/bin/python3 |
| runner_path | docs/v2/audit/backfill_1014_1016/run_backfill_r_v3_1.py |
| sha_runner ★ | <v3.1 实测全长 sha，Arch 增量复核后填写；不得为 f006c0b2…、28bc5e0e…、1e81c4f1…> |
| runner_cmd | cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 docs/v2/audit/backfill_1014_1016/run_backfill_r_v3_1.py </dev/null |
| check_only | 允许在正式运行前跑一次（同命令加 --check-only），不消耗本 .ok |
| cmd_run1 | /usr/bin/python3 scripts/nightly_update.py --date 20261016 --steps cyq |
| cmd_run2 | /usr/bin/python3 scripts/nightly_update.py --date 20261016 --steps tier3,bundle,freshness |
| cmd_dryrun | 上两条各加 --dry-run（nightly L106/L137：不起子进程、不探测中转、不写 summary） |
| serial | strict（run1 退出且 rc==0 → 快照 compare 通过 → cyq 判定全过 → run2 前复核 → 才起 run2；一次一个真实数据进程） |
| latest_start_run1 / latest_start_run2 | 2026-10-18T14:45:00-04:00 / 2026-10-18T15:00:00-04:00 |
| hard_stop_et | 2026-10-18T15:55:00-04:00（按确切 PID 停，退出 3） |
| sha_nightly_update ★ | ec079d56912aea8a4358a7ae97a73a3ad6ee3df34e83845ad4d655d31d838636 |
| sha_relay_health ★ | 6d3ea9f57f63af8d82d6eeaf140a989aeb09cda941e6711c25f12fd3bbe0e17f |
| sha_cyq_perf_monthly ★ | 6aae6c1b8de7b37752fb5032c22ea65b698f252cc57f8e5af94b1e13d6e09c1f |
| sha_tier3_daily_snapshot ★ | 64a71f5607439c5b09ddd92a8dfeffd94e4f5244297f83fbc5c65e3abfcf1067 |
| sha_data_freshness_status ★ | a759d29788859b43783bac6360014347b2df0e4dce5949302a0908db511f1d50 |
| sha_tushare_proxy ★ | ae91f230560d445b4d2321e8e022d01b55773e168d4d842fc6987fa9458fc772 |
| sha_snapshot_tool ★ | c930ed5c627bf937e6b5d139c52f18945f045286e78dba66cbe5adfab92ab79a |
| scope_file | docs/v2/audit/nightly_sha_scope_backfill_1014_1016.txt |
| scope_sha ★ | 579c8605266af1724b942fe1f3f2c000e0f97013cb9ff345c184b20c723b54c0 |
| request_doc_sha | r3=76e5f1f1cc6f70e3c243cde7142bd0673a1f822df82ea90b13c8bc07ba5e4bd7；r3_1=4c7f7ad823bffe5a5f06ddb7f3dadd1c9be34cea643edc4b1b5eb0fbb18a36d0；r2=2aad50362823808c2b53628d130e9f70deb1d567e32b82299cf0476490ac4e67；v3.1 增量说明=<签发时填> |
| review_doc | docs/v2/ARCH_DATA_PLAN_R_R3_REVIEW_ZH.md（本文，sha 见回报）+ v3.1 增量复核文档 |
| fallback_plan_sha | 23d9788492f08c342f477c50fe6c03afb635720af13fe52b4f647c34f0de017b |
| must_not_change_pin | output/daily_update_status.json=7991455a06b85d7bca09b8c50e2fc1cfe6f421abe33790b90a125097ab2a4850；data/v2/tushare_raw/trade_cal.parquet=141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086；data/v2/calendar/trade_cal_sse_pit.parquet=fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41；data/v2/sw_pit/industry_members_sw_l1_pit.parquet=0b1d3432e30f7cdd907df393299cd2f552e1121899239985a00113c4dfcd89f6；closure 156 项（paper_import_closure.json 6919e7af…）+ sw_l1_pit 89d4afa3 / 87d769aa |
| backup_dir | _recovery/data/backfill_1014_1016/（os.mkdir，已存在即停） |
| backup_list_run1 | r3 §2.1 十项（含 output/data_v2_bundle/cyq/manifest.json 与 cyq_perf_202610.parquet） |
| backup_list_run2 | r3 §2.2 十二项；7 个 20261016 目标跑前须不存在 |
| rss_stop_kb ★ | 1484800 |
| rss_hard_kb | 1536000 |
| rss_enforcement | sampler_5s_tree_sum_autokill_exact_pid（先 STOP 父、再子孙最深先 TERM→10 s→KILL、再父；P2-1 修法） |
| guard_94322 | 操作员在 run1 前 kill -STOP 94322，留 ps 与 /proc stat=T；全部结束后 kill -CONT 94322 并留 ps；执行器只核不发 |
| evidence_94322_T | <Data ps 输出与时间，签发时填> |
| probe_evidence | docs/v2/audit/relay_probe_20261018/probe_log.csv sha=<签发时填>；两轮连续：trade_cal 7 行 + stock_basic list_status=L limit=5000 恰好 5000 行 |
| quiet_gate | 锁必须已存在，执行器不建不删；healthz 轮询至 quiet=true ≤90 s → 再等 15 s → 复核 quiet=true、gen/snapshot/kline_running=false、child_pids={} → pgrep -f "kline.py|export_static.py|snapshot.py|gen.py" 为空；run2 前复核锁（sha 不变）+ healthz + pgrep + 94322 |
| allow_run_nightly_update_cyq ★ | true |
| allow_run_nightly_update_tier3_bundle_freshness ★ | true |
| allow_network_relay | true |
| allow_restore_cyq_202610_from_backup | true 仅当 v3.1 满足 Q4 全部 8 条；否则 false |
| allow_write | data/v2/tushare_raw/cyq_perf/2026101{4,5,6}.parquet（新）；data/v2/cyq/cyq_perf_202610.parquet；data/v2/cyq/manifest.json；data/v2/cyq/.*.restore_tmp.*（仅 Q4=true）；data/v2/tier3_daily/*/20261016.parquet 与 manifests/20261016.json（新）；output/data_v2_bundle/**；output/data_freshness_status.json 与 .tmp；output/relay_health.json；output/relay_outage_backfill_queue.json；logs/nightly/20261016_summary.json、20261016_{cyq,tier3,freshness}.log、backfill_20261018_run{1,2}.out；_recovery/data/backfill_1014_1016/**；/tmp/arch1018/backfill_*；docs/v2/audit/backfill_1014_1016/run_backfill_r_result_*.json；以上目录内执行器自建的 .*.tmp.<pid> |
| allow_daily_pull ★ / allow_trade_cal ★ / allow_sw ★ | false / false / false |
| allow_eng_panels / allow_events | false / false |
| allow_write_daily_update_status | false |
| allow_write_summary_20261014_20261015 | false |
| allow_force ★ | false |
| allow_delete ★ | false（半写文件不删，原样报） |
| allow_kill | 仅本次 nightly 的确切 NPID 及其子孙（核 cmdline + PPID）；94322 的 STOP/CONT 只由操作员执行 |
| allow_quiet_lock_write | false（执行器）；锁由 Arch/操作员设、执行器退出且 CONT 94322 后由设锁方解除 |
| allow_move_ok | false（执行器）；只由 Arch 归档 |
| abort_rules | 任一 nightly rc≠0；summary.finished 不在本次 run 窗口；compare rc≠0 或含 META_ONLY_FAIL；范围 sha 不符；cyq/run2 判定任一不满足（含 RELAY_DOWN、skipped）；RSS 树和 > 1484800；15:55 未结束；run2 前复核不过 |
| blackout | 16:40–18:40 ET 不跑任何东西 |
| receipt | docs/v2/audit/BACKFILL_1014_1016_RECEIPT_ZH.md（新文件，含结果 JSON sha、两份 SHA256SUMS、before/after 快照 sha、94322 前后 ps、锁设/解时间、P3-9 的 sha256 映射陈旧、P2-1 的孤儿扫描结果）+ TEAM_STATE Data 段 |

## 7. 发现汇总
| 级别 | 编号 | 位置 | 内容 |
|---|---|---|---|
| P1 | P1-1 | v3 L642 + L383 | dry-run 解释器重复，必然退出 2，补跑起不来且白耗 .ok |
| P2 | P2-1 | v3 L197-218、L430；nightly L104-127 | 停树时 nightly 继续下一步、留孤儿；p.wait 可能无限阻塞 |
| P2 | P2-2 | v3 L654-684 | 未核 nightly rc，未排除陈旧 summary |
| P2 | P2-3 | v3 L494-525；r3 L51、L121 | 自动恢复不读 .ok 键、不与 before 快照交叉核、损坏时不触发、无恢复后复核 |
| P3 | P3-1 | L338、L363、L368、L372、L382、L409 | 未捕获异常 → 退出 1、无结果文件 |
| P3 | P3-2 | L411 | runN.out 用 "a"，应 "x" |
| P3 | P3-3 | L228、L253-260 | sha 键可缺省；行内注释会被当值 |
| P3 | P3-4 | L297-305 | 94322 未核 cmdline |
| P3 | P3-5 | L200-218 | 发信号未核 PPID |
| P3 | P3-6 | L637-638 | check-only 与全通过同码 |
| P3 | P3-7 | L668 | 锁 sha 前后一致；运行中只记锁、不做 pgrep |
| P3 | P3-8 | L557-567 | bundle 只核 need 列表 |
| P3 | P3-9 | cyq L61-66 | manifest sha256 映射跑后陈旧 |
| P3 | P3-10 | L449-497 | 建议 trade_date 列独立核对（不阻断） |
| P3 | P3-11 | 范围文件 L2 | 注释仍写 v1 |
| P3 | P3-12 | r3 L18-26、L106 | 仍写 v2 与 --quiet-evidence |
| P3 | P3-13 | §6 allow_write | 补 freshness.log、.tmp、恢复临时文件 |
无 P0。
