# Arch 复审：Web staged_v2（回应 ARCH_WEB_AUTOSTART_QUIETGUARD_REVIEW_ZH.md ae06116f）

- 审查人：QuantLab Arch；时间：2026-10-18T10:02:17-04:00（ET）
- 方式：纯静态只读。只用 cat/diff/rg/sha256sum/cmp，以及 /proc/<pid>/cmdline 读取。未执行任何 staged 脚本，未安装，未启停或发信号给任何进程，未起项目 python，未读 /workspace/QuantLab/data。工作目录 /tmp/arch_webrr_U5gM。
- 密钥检查只做计数：grep -cFf 对 .token / .vercel_token，未打印任何密钥。
- 研究锁 output/loop/RESEARCH_QUIET.lock（b5e78069）在位，未动。live=false，promotion=false。

## 结论

| 项 | 结论 |
|---|---|
| staged_v2 守卫与守护修复（P1-A/P1-B/P1-C/P2-A~E） | **PASS with conditions** |
| 自启提案 v2（AUTOSTART_PROPOSAL_ZH.md 897d6059 / autostart.sh.proposed a97c90fe） | **PASS**（启用仍须不早于 10-19 18:40 ET 且无研究锁） |

- 原审查的 3 条 P1 全部修复，没有新的 P1。
- 安装前必须完成 2 条 P2（C1 gen.py 原子写、C2 遗留正则日志），Arch 只做这两个文件的增量复核，不再全量复审。
- 安装放行：见第五节。

## 一、核对

- 输入 sha256（前缀全部一致）：
  - WEB_REVIEW_RESPONSE_ZH.md = fcf557994ccf…；AUTOSTART_PROPOSAL_ZH.md = 897d6059fb58…；staged_v2/SHA256SUMS = 98df454056cd…；原审查 ae06116f69887….
- staged_v2：`sha256sum -c SHA256SUMS` 15/15 OK。注意清单里实际是 **15 个文件**（另加 SHA256SUMS 本身），不是消息里说的 14 个：ql_quiet.sh、ql_child.py、start_all.sh、supervise.sh、deploy_supervise.sh、deploy_loop.sh、keepalive.sh、loop.sh、server.py、export_static.py、freshness.py、autostart.sh.proposed、install_v2.sh、test_v2.sh、home_v2.diff。
- 备份：实际路径是 `/workspace/QuantLab/_recovery/web/pre_review_fix_20261018_094840ET/`（不在 quantlab-web/_recovery 下）。`sha256sum -c` 22/22 OK（22 个文件 + SHA256SUMS）。
- 线上未改：备份里 19 个线上文件与 /workspace/quantlab-web 现文件逐字节相同；只有 AUTOSTART_PROPOSAL_ZH.md 不同，是本次 v2 提案，符合预期。~/.bashrc、~/.profile 与备份 home_bashrc、home_profile 逐字节相同，自启钩子仍是注释。
- 与线上 diff：ql_child.py 为新文件；loop.sh 无差异；其余 10 个文件的改动与回应表逐条对应，没有发现回应表以外的改动。
- 现场（只读 /proc cmdline）：5 个守护进程 2859816 `/bin/bash ./supervise.sh`、2859819 `/bin/bash ./deploy_supervise.sh`、2859822 `ql_keepalive_loop /workspace/quantlab-web/keepalive.sh`、2859825 `/bin/bash ./deploy_loop.sh`、2905775 `python3 -X utf8 server.py`，都能被 start_all.sh 的锚定正则精确命中。run/ 目录尚不存在。
- env -i 白名单 PATH 下：python3 → /usr/bin/python3（3.13），node → /usr/bin/node，npx → /usr/local/bin/npx，jq/flock/setsid/nohup 都在 /usr/bin。守护进程在最小环境下能找到所需程序。
- 密钥：.token、.vercel_token 都是 0600。两份密钥在 staged_v2 全部 15 个文件、两份 Web 文档、deploy.log、server.log、start_all.log、/tmp/ql_deploy.out 中的出现次数都是 0。

## 二、逐项确认

### P1-A 运行中子进程不受静默约束 → 已修

- ql_child.py:21-23：启动前不用缓存地调 ql_quiet.status()，静默返回 quiet_before_start，不启动。
- ql_child.py:25：Popen(start_new_session=True)。子进程是自己会话和进程组的首进程，pgid 等于子进程 pid，killpg(p.pid) 不可能打到 server 或 supervise 的进程组。argv 首项是 nice，nice 是 exec，pid 不变，所以组内就是真正的 python。
- ql_child.py:32-36：wait(timeout=2) 循环，每轮 is_quiet() 复查（同样不用缓存），超时也停。
- ql_child.py:9-18：先 killpg SIGTERM 并等 5 秒，再 SIGKILL 并 wait 回收。每次发信号前先 poll()；子进程只由我们自己回收，没回收前 pid 被僵尸占着，不会出现 pid 复用后误杀。
- ql_child.py:37-40：finally 中兜底停止并注销登记，异常和 SystemExit 路径都覆盖。
- server.py:74（gen）、:103（snapshot）、:193（kline）都改走 ql_child.run。snapshot 中途静默时 :105 置 pending，不起 gen。
- server.py:81 gen_start 改为 quiet(force=True)。
- server.py:83-85、:158 healthz 新增 gen_running、snapshot_running、kline_running、child_pids。gen_running 同时看 LIVE 和 GEN 线程，偏保守，正确。
- export_static.py:10-11 开头查一次；:16-17 每只代码复查；:18 kline 经 ql_child 运行中再复查；:19 运行中静默退出 3；:39-40 读 freshness 的 parquet 前再查一次；:8-9 收到 TERM/INT 时 stop_all。
- 静态确认 gen.py、snapshot.py、kline.py 里没有 subprocess/Popen/fork，组内不会有孙进程。

### P1-B 锁 fd 继承 → 已修

- start_all.sh:27 spawn 时 `8>&- 9>&-`，并用 setsid、nohup 和 env -i。
- start_all.sh:16 flock 失败写日志并 exit 4。
- keepalive.sh:13 调 start_all 时也关 8/9；autostart.sh.proposed:26 同样。
- 过渡期：安装后旧 keepalive 调到新 start_all，新 start_all 在 :15 重新打开锁文件，会因旧守护进程持有的旧描述而 flock 失败，rc=4 并记日志，不会重复拉起。推演结论与回应一致。

### P1-C 环境污染 → 已修

- start_all.sh:14 判完锁就 unset 五个 QL_QUIET_*；:24 env -i 白名单只有 HOME/USER/LOGNAME/SHELL/PATH/LANG/LC_ALL/TZ。env -i 同时去掉了 BASH_ENV，非交互 bash 不读任何 rc 文件。
- supervise.sh:5、deploy_loop.sh:8、keepalive.sh:5、autostart.sh.proposed:6、install_v2.sh:12 各自再 unset 一次。
- ql_quiet.sh:11 `_ql_ov` 只有 QL_QUIET_TEST=1 时才采用覆盖值，否则一律用默认锁路径 /workspace/QuantLab/output/loop/RESEARCH_QUIET.lock。
- 锁判定不可被环境绕过：ql_quiet.sh:19 锁检查排在第一位；不设 QL_QUIET_TEST=1 时，任何环境变量都改不了锁路径，也到不了“不静默”的分支。QL_QUIET_ALLOW_NOWIN 只作用于窗口文件缺失（:20-21），在锁检查之后，不影响锁。
- server.py 经 ql_quiet.py:7 以子进程调 ql_quiet.sh，继承的是 supervise 给的干净环境。
- 自启门槛：home_v2.diff:10 `case $- in *i*)` 加 QL_NO_AUTOSTART；autostart.sh.proposed:5 再查一次。agent 和 wrapper 的非交互 `bash -l` / `bash -lc` 不会触发。

### P2

- **P2-A**：supervise.sh:7、:12 写 pidfile 并 trap TERM/INT 先停 server。旧版重启已列入切换步骤。确认。
- **P2-B**：start_all.sh:3-4 退出码 0/3/4/5/1；:12 锁 → 3；:16 flock 忙 → 4；:35-40 用 pidfile 和 /proc cmdline 核实，失败 → 5。autostart.sh.proposed:28-30 只在 rc=0 且 supervise pid 核实后，用 noclobber 写标记。确认。
- **P2-C**：server.py:188 每次请求 quiet(force=True)；:192 Semaphore(1) 非阻塞，忙时 503；kline 本身走 ql_child 运行中复查。确认。
- **P2-D**：server.py:251-257 SIGTERM/SIGINT 处理和 atexit 都调 ql_child.stop_all()；子进程登记在 ql_child.LIVE。确认（SIGKILL/OOM 情形见 P3-3）。
- **P2-E**：deploy_loop.sh:24 改为只给 vercel 子 shell 设 VERCEL_TOKEN 环境变量，不再传 --token；:26 日志过滤 token。环境变量只有同 uid 或 root 能读，不像 argv 对所有人可见。确认。

### 已下裁定的执行情况

| 裁定 | staged 实现 | 结论 |
|---|---|---|
| 过渡正则只在无 pidfile 时用、每次命中记 pid+cmdline、下一版删除 | start_all.sh:22-23：pidfile 缺失或失效时才走 legacy，这一点符合；但只记 pid、不记 cmdline；`head -1` 只取第一个命中，其余命中不记日志；代码里没有“v3 删除”标记 | **未完全满足 → C2** |
| 停进程顺序：先停 supervise 并确认退出，再停 server | 回应 §切换步骤 4：keepalive → deploy_supervise → deploy_loop → supervise → server，每停一个用 ps -p 确认 | 满足。文档里“Arch 建议先停 server”的说法要改成按 Arch 裁定执行（P3-11） |
| freshness 只要读前现查静默即可 | server.py:173-175 在 FCL 锁内 quiet(force=True) 后立即 build；export_static.py:39-42 查完立即 build | 满足。读 parquet 期间约 1 秒不可中断，接受 |
| gen.py 必须先写临时文件再原子 rename | gen.py 不在 staged_v2 中，线上 gen.py:97 直接 open(...,"w") 写 html，:180 直接写 gaps.json | **未满足 → C1** |

## 三、发现

### P1

- 无。

### P2（安装前必须完成）

**C1 / P2-1｜gen.py 非原子写**
- 位置：gen.py:97（各页 html）、gen.py:180（gaps.json）。gen.py 不在 staged_v2 中。
- 问题：ql_child 在静默或超时时会 TERM/KILL gen.py，被打断就会在 site/ 留下半份 html 或 json。看板和 export_static 会照原样读取并部署这份残缺产物。
- 要求：
  - 每个输出都先写 `<目标>.tmp.<pid>`，flush 加 fsync 后 os.replace 到目标；异常时删掉临时文件。
  - 把 gen.py 加入 staged_v2、SHA256SUMS，以及 install_v2.sh:8 的 FILES，保证安装前会备份。
  - 建议同时在 gen.py 开头加一次 ql_quiet.status() 自查，静默就 exit 3（见 P3-9）。

**C2 / P2-2｜过渡正则的日志和收敛不足**
- 位置：start_all.sh:22-23。
- 要求：
  - 只在 pidfile 缺失或无效时才调用 legacy（现状满足，保持不变）。
  - 列出全部命中，每个命中都记一行 `pid=… cmdline=…`。
  - 命中数大于 1 时不认领、不写 pidfile，记日志并返回失败（最终 rc=5），避免认错实例。
  - 代码注释写明“过渡用，v3 删除”。

### P3（建议，不阻塞）

- **P3-1｜进程组残留没有清扫**：ql_child.py:11、:33。子进程正常退出，或 _stop 时 poll() 已非 None，都会直接返回，不再对组做 killpg。目前 gen、snapshot、kline 都不起孙进程，没有实际影响。建议在 wait 结束后对 pgid 补一次 killpg(SIGKILL)，组已空时忽略 ProcessLookupError。
- **P3-2｜宽限期不一致**：ql_child.py:46 stop_all 默认 grace=3，规格是 5 秒。建议统一为 5。
- **P3-3｜server 被 SIGKILL 或 OOM 时子进程成孤儿**：server.py:254-257 只覆盖 TERM/INT 和 atexit。子进程在自己的会话里，server 死后会被接管并继续跑（gen 最长 600 秒）。建议把子进程 pid、cmdline 写进 run/children.json，server 启动时按精确 pid 加 cmdline 核对后清理；或在子进程启动时设 PR_SET_PDEATHSIG。
- **P3-4｜窗口条目畸形时 fail-open**：
  - ql_quiet.sh:29 start 为空时直接跳过；:30 end 为空时 `date -d ""` 返回今天 00:00（已实测：与当天零点 epoch 相同），窗口永远不生效。
  - 建议 start 或 end 任一为空都按静默处理（fail-closed）。
  - ql_quiet.sh:21 的 QL_QUIET_ALLOW_NOWIN 建议也受 QL_QUIET_TEST=1 门槛约束（不影响锁）。
- **P3-5｜图表拷贝不复查静默**：server.py:108-110 在 snapshot 成功后，直接从 QuantLab/output/intel/charts 拷 png，中间没有复查静默。这是衍生产物，不是行情，影响很小。建议拷贝前 quiet(force=True)。
- **P3-6｜pidfile 核对是子串匹配**：start_all.sh:19-20 用 grep -F 子串，`supervise.sh` 也会匹配 `deploy_supervise.sh`。建议对 /proc/PID/cmdline 做整串相等比较。
- **P3-7｜自测在拿不到锁时会真跑**：test_v2.sh:17-18 如果测试子 shell 拿不到 flock，会直接退出，接着真正执行 start_all --from-keepalive，可能拉起守护进程。建议拿不到锁时整个测试中止并判 FAIL。
- **P3-8｜部署输出与停止**：deploy_loop.sh:24 的 /tmp/ql_deploy.out 现在是 0644（已核实其中没有 token）。建议 umask 077。deploy_loop.sh:12 的 stop() 不会停掉正在跑的 vercel 子 shell；它不读 QuantLab，可以接受。
- **P3-9｜纵深防御**：
  - server.py、export_static.py 启动时没有从 os.environ 去掉 QL_QUIET_*。手工带 QL_QUIET_TEST=1 启动时，覆盖会生效。建议启动时清掉。
  - loop.sh:4 不经 ql_child 直接跑 gen.py。它目前不被任何脚本启动，建议删除，或在文件头写明“禁止启动”。
  - gen.py、snapshot.py、kline.py 本身没有静默自查，被手工运行时不受约束。建议各加一次开头自查。
- **P3-10｜错误被静默吞掉**：export_static.py:20-21 status 为 error:* 时直接跳过，没有日志。建议记到 stderr。
- **P3-11｜文档一致性**：
  - 文件数应为 15（另加 SHA256SUMS）。
  - 备份路径应写全，并注明在 QuantLab/_recovery 下。
  - 切换步骤 4 改写为“按 Arch 裁定：先停 supervise 并确认退出，再停 server”。

## 四、竞态与残留路径

- **检查到启动之间的竞态**：锁若恰好在 ql_child.py:22 检查之后、:25 Popen 之前出现，子进程会被启动。下一轮 poll（≤2 秒，加 ql_quiet.sh 本身耗时；ql_quiet.py 5 秒超时会按静默处理）发现静默后，再等 5 秒宽限。最坏约 12 秒后组内清空。
  - Arch 流程补充（即刻生效）：设锁后至少等 15 秒，再做三项核验。
  - 第二项核验扩大为：全机 `ps -eo pid,ppid,args` 中没有 gen.py、snapshot.py、kline.py、export_static.py。原因是子进程在自己的会话里，父进程死后会被接管，仅查 `pgrep -P` 可能漏掉。
- **killpg 打错组**：不会。pgid 就是子进程自己的 pid（start_new_session）；发信号前先 poll，未回收前 pid 不会被复用。
- **剩余未经静默检查就读真实数据的路径**：
  - 守护链路内：无。snapshot、gen、kline 都经 ql_child；freshness 读前现查；export_static 逐只复查。
  - 守护链路外：loop.sh，以及手工运行 gen.py、snapshot.py、kline.py（P3-9）。
- **密钥**：未发现任何文件、日志或 argv 中含 token。

## 五、放行

- **安装 staged_v2**：可以，但须同时满足：
  1. Web 完成 C1、C2，提交 gen.py、start_all.sh、install_v2.sh 的新 sha 和更新后的 SHA256SUMS；Arch 只对这几个文件做增量复核，通过后才能装；
  2. 研究锁 b5e78069 已由 Arch 解除，且 output/loop/RESEARCH_QUIET.lock 不存在；
  3. 不在 2026-10-19 16:40–18:40 ET 窗口内；
  4. 按回应 §切换步骤 执行：先 dry-run；第 3 步确认没有子进程；第 4 步按顺序 keepalive → deploy_supervise → deploy_loop → supervise → server，只用精确 PID 的 kill，不加 --force，每停一个都用 ps -p 确认；
  5. 安装后补交回执：重启后的 PID、各文件 sha、test_v2.sh 输出、healthz 输出。
- P3 可以在下一版处理，但 P3-4 和 P3-7 建议随 C1、C2 一起改。
- **自启**：提案 v2 PASS。启用须在 staged_v2 安装并核验之后，不早于 2026-10-19 18:40 ET，且研究锁不存在。在此之前，.bashrc 和 .profile 的钩子保持注释。
