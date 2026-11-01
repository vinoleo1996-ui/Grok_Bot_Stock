# Arch 审查：Web 自启提案 + 静默守卫回执

- 审查人：QuantLab Arch；时间：2026-10-18T09:44-04:00（ET）
- 方式：纯静态只读。只用 rg / diff / sha256sum / cat，以及 ps、/proc 读取。没起项目 python，没启停进程，没动 ~/.bashrc、~/.profile 和 quantlab-web。
- 唯一的非只读动作：用 `flock -n` 探测过一次 /tmp/ql_start_all.lock，结果是 BUSY，没拿到锁。
- 研究锁 output/loop/RESEARCH_QUIET.lock（b5e78069）未动。
- live=false，promotion=false。

## 结论

| 项 | 结论 |
|---|---|
| 1 自启提案（AUTOSTART_PROPOSAL_ZH.md c065d2ce / autostart.sh.proposed 7953751f） | **CHANGES REQUIRED** |
| 2 静默守卫回执（WEB_QUIET_GUARD_RECEIPT_ZH.md） | **PASS with conditions** |

- 静默期的稳态行为：符合回执描述。
- 未覆盖的部分：静默期开始前已经在跑的子进程不会被中止；保活逻辑实际失效（见 P1-B）。

## 一、核对

- **sha256**：回执 §2 列的 15 个文件，磁盘实测全部一致：ql_quiet.sh、ql_quiet.py、quiet_windows.json、keepalive.sh、start_all.sh、supervise.sh、deploy_loop.sh、loop.sh、server.py、freshness.py、export_static.py、ql_bus.py、API.md、AUTOSTART_PROPOSAL_ZH.md、autostart.sh.proposed。
  - deploy_supervise.sh = a03c1c55，和备份逐字节相同。
  - gen.py、kline.py、snapshot.py 都和备份逐字节相同，未改动。
- **备份**：_recovery/web/pre_quietguard_20261018_092503ET/ 存在，`sha256sum -c SHA256SUMS` 15/15 OK。
  - 里面有 home_bashrc、home_profile、TEAM_STATE 原件。
  - loop.sh 没有备份，回执已披露。
- **~/.bashrc、~/.profile**：~/.bashrc 第 2 行、~/.profile 第 30 行仍是 `# QUIET-WINDOW-DISABLED` 注释。没有 ~/.bash_profile 或 ~/.bash_login，所以登录 shell 会读 .profile。
- **现场（09:42 ET）**：
  - server 2905775（NI 10）没有子进程，全机没有 gen、snapshot、kline、export_static、vercel 进程。
  - deploy.log 自 09:38:10 起每 60 秒记一次 quiet skip。
  - server.log 09:38:46 记了 quiet ON。
  - 5 个守护进程的 environ 里都没有 QL_QUIET_* 覆盖变量（只查了变量名）。

## 二、静默守卫逐项确认（静默期稳态）

- **server 不起 snapshot/gen**：server.py:93-96。scan 在需要刷新时先 `quiet(force=True)`，静默就置 pending 后跳过。gen_start 有守卫（server.py:80），reap 也有（server.py:84）。确认。
- **/api/kline 只回缓存，否则 503**：server.py:176-180，先读内存 KC 和 export/kline 缓存，静默时没缓存回 503。确认，但见 P2-C 的缓存时效窗口。
- **freshness 不读 parquet**：
  - freshness.py:46/51：静默时不读 bars 和 etf 的 parquet。
  - freshness.py:10：交易日历没缓存时也不读。
  - server.py:166 传入 quiet；export_static 经 freshness.py:25-29 自查。确认。
- **deploy_loop 跳过**：deploy_loop.sh:7 循环开头查一次，:10 部署前再查一次（锁和窗口都算）。确认。
- **keepalive 跳过**：keepalive.sh:7 查锁和窗口，确认。另见 P1-B：即便不在静默期，保活实际也起不了作用。
- **supervise 不重启 server**：supervise.sh:6 只看锁。窗口内照常重启是有意设计，server 启动时 scan(first) 会先查静默。磁盘版确认；运行中版本见 P2-A。
- **export_static 自查**：export_static.py:5-7，静默时退出码 3。确认。
- **ql_quiet.sh**：
  - jq 解析失败或时间解析失败都按静默处理（fail-closed）。
  - [start, end) 半开区间正确。
  - ql_quiet.py 的 5 秒超时和异常也都按静默处理。
- **僵尸修复（server.py:72-81）正确**：
  - subprocess.run 会 wait 回收子进程。超时时 run 会先 kill 再 wait。
  - nice 是 exec 进 python，PID 相同，所以超时能杀到真正的 gen。
  - 在线程里跑不会再留下 `<defunct>`。

## 三、发现

### P1

**P1-A｜静默开始时正在跑的子进程不会被中止，检查和启动之间也有空档**
- 位置：server.py:94-101、:72-81、:178-182；export_static.py:5-7、:11-14。
- 问题：
  - 静默判定只在启动子进程之前做一次。
  - 锁出现时已经在跑的 snapshot.py（最长 120 秒）和 gen.py（最长 600 秒，会读 actual_weights.parquet，gen.py:122-124）会一直跑完。
  - export_static 只在开头查一次静默，之后逐只股票起 kline.py（每只最长 300 秒，会读 bars/etf/panels 的 parquet），中途锁出现也不会停。
  - scan 在 :94 用 force 查过之后，:101 的 gen_start 用的是缓存值（5 秒内有效）。snapshot 如果在 5 秒内跑完，gen 就可能用过期的“非静默”结果启动。
- 影响：设锁后最多约 10 分钟内，看板仍可能在读真实数据。真实数据单进程规则、RSS 测量和 C5 判定都可能被污染。
- 要求（Web）：
  - gen、snapshot 改为 Popen + wait(timeout=2) 循环，每 2 秒 `quiet(force=True)` 一次，静默就 terminate，5 秒后 kill，最后 wait。依然在线程里回收，不会产生僵尸。
  - export_static 在 kline 循环里每只股票都复查一次 ql_quiet.status()，静默就退出 3。
  - :101 改成 `quiet(force=True)` 后再调 gen_start。
- 要求（Arch 流程，立即生效）：设锁之后、签发任何真实数据 .ok 之前，必须确认以下三项，并留证：
  - `pgrep -P <server PID>` 为空；
  - deploy_loop 下没有 export_static、kline 子进程；
  - healthz 返回 `gen_running=false`。

**P1-B｜start_all 的 flock fd 被守护进程继承，保活和后续 start_all 都静默失效**
- 位置：start_all.sh:8、:10、:11、:14。
- 实测：
  - /proc/{2859816,2859819,2859822,2859825,2905775}/fd/9 都指向 /tmp/ql_start_all.lock。
  - `flock -n` 探测结果是 BUSY。
- 问题：之后任何 start_all.sh 都会在第 8 行 `flock -n 9 || exit 0` 处无日志退出。
  - keepalive 的 start_all --from-keepalive 实际是空操作。
  - 静默解除后 supervise 或 deploy_supervise 如果挂了，不会有人重新拉起，和回执 §3、§9 的说法不符。
  - 这一条影响的是可用性，不危及研究安全，方向是 fail-safe。
- 要求：
  - 拉起守护进程时关掉锁 fd，例如 `setsid nohup ./supervise.sh 9>&- 8>&- …`，或者用 `flock -o`。
  - 每次 start_all 因 flock 退出都要记日志。
  - 修复后的重启要在锁解除后、10-19 窗口外做，并且按 PID 进行。

**P1-C（自启）｜登录 shell 会把调用方的环境带进长期守护进程**
- 位置：autostart.sh.proposed:5-13 → start_all.sh:10-14。
- 问题：
  - 任何 `bash -l` 或 `sh -l`，包括 agent 和 wrapper 的非交互登录 shell，都会触发自启。启用步骤 3 里的 `bash -lc` 自测就是这种情况。
  - 守护进程会继承调用方的全部环境。如果调用方带着测试用的 QL_QUIET_LOCK、QL_QUIET_WINDOWS、QL_QUIET_NOW 覆盖，守护进程会永久忽略真实的研究锁和 10-19 窗口。
  - 守护进程还会继承调用方的 ulimit、cgroup、PATH 和 venv。
- 要求：
  - autostart.sh 和 start_all.sh 拉起守护进程前先 `unset QL_QUIET_LOCK QL_QUIET_WINDOWS QL_QUIET_NOW`，并用 `env -i HOME=… PATH=/usr/local/bin:/usr/bin:/bin LANG=C.UTF-8 TZ=America/New_York` 启动。
  - 或者规定只有设置了 QL_QUIET_TEST=1 时，守护进程才接受这些覆盖。
  - .profile 钩子加两道门：`[ -z "$QL_NO_AUTOSTART" ]`，以及 `case $- in *i*)`（只在交互登录时触发）。如果 Web 坚持非交互登录也要触发，请写明理由，并且第一条必须做到。

### P2

**P2-A｜运行中的 supervise 不一定是磁盘上的版本**
- supervise 2859816 是 09:27 启动的，而 supervise.sh 在 09:35:57 又被改过（现在 sha 是 5c7f10c7）。
- bash 在进入 while 循环时就把整个循环体解析好了，所以运行中的循环是 09:27 那一刻的版本。
- server 的 NI=10 说明这个版本已经带 nice，但锁判定那一行无法从外部核实。
- 要求：静默解除后、10-19 窗口外，按 PID 重启 supervise（先停 2905775，再停 2859816，然后 start_all，需先修好 P1-B），并在回执里补上重启后的 PID 和 sha。

**P2-B（自启）｜锁在中途出现时会误写标记**
- 位置：autostart.sh.proposed:10-13；start_all.sh:7-8。
- 问题：
  - autostart 判定不静默之后、start_all 自己查锁之前，如果锁出现了，start_all 会 exit 0。flock 忙时 start_all 也是 exit 0。
  - autostart 收到 0 就写下本次开机的完成标记，结果这次开机就再也不会自启。
- 要求：start_all 对“锁存在”和“flock 忙”分别返回不同的退出码（例如 3 和 4）。autostart 只在返回 0，并且用 pgrep 或 PID 文件确认 supervise 确实在跑之后，才写标记。

**P2-C｜/api/kline 和 /api/freshness 的静默结果有最长 5 秒的缓存**
- 位置：server.py:67、:166、:178。
- 锁出现后的 5 秒内仍可能起 kline.py（最长 60 秒），或者读一次 freshness 的 parquet。
- kline 请求没有并发上限，多个请求可以同时起多个 kline.py。
- 要求：kline 分支改用 `quiet(force=True)`；同时加并发上限 1。

**P2-D｜server 退出时子进程会变成孤儿继续跑**
- gen 线程是 daemon 线程。按 PID 停掉 server 后，正在跑的 gen.py、snapshot.py 会被 PID 53 接管并继续运行。
- 要求：子进程用 start_new_session=True 启动并记下 PID；server 退出时（atexit 或 SIGTERM 处理）按这些 PID 终止并回收。

**P2-E｜Vercel token 出现在命令行参数里**
- 位置：deploy_loop.sh:12，备份版就已经如此，不是这次引入的。
- `--token "$(cat ../.vercel_token)"` 会出现在 npx 和 node 的 argv 里，同一台机器上的进程都能通过 ps 或 /proc/*/cmdline 读到。
- 要求：改为 `VERCEL_TOKEN="$(cat ../.vercel_token)" npx … deploy`，不再传 --token。
- 自启脚本本身不读 token，这一项没问题。

### P3

- **P3-1**：
  - ql_quiet.sh:17 在 quiet_windows.json 缺失时判为非静默（fail-open）。建议文件缺失时也按静默处理，或者只有设置了 QL_QUIET_ALLOW_NOWIN=1 时才放行。
  - autostart.sh.proposed:6 在读不到 boot_id 时退回 `unknown`。如果 /tmp 跨重启保留，就会永久不自启。建议读不到时直接退出并记日志。
- **P3-2**：
  - autostart.sh.proposed:10 在静默期内，每个登录 shell 都会写一行日志，会刷屏。建议同一原因 10 分钟内只记一次。
  - autostart.sh.proposed:13 中 start_all 失败时没有日志，建议补上。
  - 标记文件放在 /tmp 且所有人可写。建议改放 /run/user/$UID，或者用 `set -o noclobber` 写入。
- **P3-3**：
  - start_all.sh:9 的 up() 用 `pgrep -f` 按模式判断进程是否在跑。任何命令行里带 'bash ./supervise.sh' 的进程（包括别人的 rg 或 grep）都会误判为“已在跑”。
  - 建议改用 PID 文件，再用 /proc/PID/cmdline 精确核对。
  - 目前全链路都没有 kill 动作，所以“只按精确 PID 停进程”的要求没有被违反。
- **P3-4**：
  - freshness.py:6/29 的 `_QUIET` 是模块级全局变量，server.py:166 的 FC 也没加锁。并发构建时理论上可能串值，但影响极小。
  - 静默期内 scan 仍会对 output、data 做 stat 和 glob（server.py:87-92）。这只读元数据、不读内容，可以接受。
- **P3-5**：启用步骤 3 里第二个 `bash -lc true` 的验证，在 P1-B 修复前，会因为 flock 忙而空过却仍然写下标记。这样的测试不能当证据。

## 四、放行条件

- **项 1 自启**：
  - 修好 P1-C 和 P2-B，同时 P1-B 已修复。
  - 重新提交新的 sha 后由 Arch 复审。
  - 复审通过后，最早在 10-19 纸面轨跑完之后（不早于 18:40 ET），并且研究锁不存在时，才能取消注释、启用。
  - 在那之前，.bashrc 第 2 行和 .profile 第 30 行保持注释。
- **项 2 守卫**：
  - 现在已上线的守卫可以继续运行，静默期稳态行为符合要求。
  - P1-A 的流程条件即刻生效：设锁后核验没有在跑的子进程，才能签发真实数据 .ok。
  - P1-A 的代码修复、P1-B、P2-A、P2-C、P2-D、P2-E 交给 Web，要在 10-19 16:40 ET 之前完成或给出排期。
  - 代码修改只能在研究锁不存在时做，并且要先备份。
