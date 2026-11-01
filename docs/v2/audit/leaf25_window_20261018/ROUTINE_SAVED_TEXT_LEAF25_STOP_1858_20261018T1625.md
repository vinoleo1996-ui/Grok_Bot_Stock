背景：QuantLab AI 要跑叶25 步骤 −1（只读、单进程、上限 900 秒）。Data 10-18 13:26 定的空档是 2026-10-18 19:00–19:45 ET，这段时间 94322 整棵进程树必须处于 T。只读进程级的 /proc/<pid>/stat，不读 task/*，不用 kill -0。所有命令的 stdin 用 </dev/null。

主 Agent 10-18 16:18 ET 补充裁定：94322 在合并 fund_portfolio，RSS 约 5GB；不在写盘中途 STOP，冻住占着 5GB 的进程对叶25 没用；叶25 开跑前 MemAvailable 必须 ≥2.5GiB 并留证。所以第 0 步之后要先做第 0.5 步。

0. 核对 .ok
   - 文件：/workspace/QuantLab/output/data/ARCH_RUN_AUTH_DATA_94322_STOP_LEAF25_20261018.ok。Arch 10-18 13:27 签发，sha256 必须是 518ff76e5523a068e2d2b9171f013f92064554e9f1d8f2337ffc4a7dd8fceed1。
   - 不在 _consumed/ 里，全文没有 DRAFT。
   - 用 date 取当前时间，必须在 18:55–19:05 ET 窗口内，并且没过 .ok 里的 expires_et。
   - 按 .ok 里写的 target_pid、PPID、cmdline、lstart 核对。
   - 找不到、sha 不符或任何一项不符：不发信号，用 priority=true 告诉 Arch（98437113-99dd-4a78-944d-75e8e17ca07d）和 QuantLab AI（88c74434-f6c4-4d3b-8f14-b5d16a635a08）：空档不成立，叶25 不要开跑。然后结束。
   - 不要移动、改名或删除这个 .ok，由 Arch 归档。
0.5 合并与内存前置检查（只读）
   - 看 /workspace/QuantLab/logs/remaining_after_stk_surv_restart_20261018_0122ET.log 里有没有 item=Q7a_fund_portfolio、status 为 done/partial/error 的行；同时记下 /proc/94322/status 的 VmRSS、VmHWM 和 /proc/meminfo 的 MemAvailable。
   - 没有完成行（合并还在写）：不发任何信号，用 priority=true 告诉 AI 和 Arch，抄送主 Agent：按主 Agent 16:18 裁定，空档取消，叶25 改到 94322 写完后的空档、23:00 前跑，没有空档就顺延到 10-19 18:45 之后。附上证据，然后结束。
   - 有完成行但 MemAvailable < 2621440 kB（2.5GiB）：不发信号，同样告诉 AI 和 Arch 空档不成立、内存不够，附证据，抄送主 Agent，然后结束。
   - 两项都满足，才继续第 1 步。
1. 读 /proc/94322/stat。文件不存在或状态是 Z，算已退出：不发信号，把证据（含 MemAvailable）发给 AI 和 Arch，说明 94322 已退出；MemAvailable ≥2.5GiB 时空档可用，否则不可用。然后结束。
2. 核对身份：PPID 是 94319；cmdline 是「python3 scripts/acquire/remaining_after_stk_surv.py」；lstart 是 Sun Oct 18 01:23:39 2026。列出整棵树（pgrep -P 逐级），每个后代的 PPID 链必须能逐级连回 94322，而且 lstart 不早于 94322。任何一项对不上：不发信号，用 priority=true 报 P1。记下「STOP 前」证据：整棵树的 ps -o pid,ppid,stat,lstart,cmd，以及每个 PID 的 /proc/<pid>/stat 原文。
3. 只发 SIGSTOP，按确切 PID 发。先停 94322（已经是 T 就不重复发），再从深到浅停后代。每发一个之前，都重读该进程的 cmdline 和 PPID。每个信号记下时刻和 rc。不按模式或进程组发信号，不发 KILL、TERM 或 CONT。
4. 2 秒后复查整棵树：全部是 T、Z 或已退出才算通过。不通过就不重试、不升级信号，用 priority=true 告诉 Arch 和 AI：空档不成立。记下「STOP 后」证据，并再记一次 MemAvailable。
5. 写回执 /workspace/QuantLab/docs/v2/audit/leaf25_window_20261018/94322_STOP_RECEIPT_20261018_LEAF25.md：先写临时文件再改名，记下 sha256。内容包括 .ok 的路径和 sha、每步的 date、第 0.5 步的合并与内存证据、STOP 前后两份证据、每个信号的时刻和 rc、结论。
6. 通过：用 priority=true 把以下内容发给 QuantLab AI 和 Arch：date 时间戳、整棵树处于 T 的 ps 证据、MemAvailable、回执 sha，并说明「空档自 19:00 ET 起可用，至 19:45 ET 止；Arch 签了 AI 的运行 .ok 后才可开跑；开跑前请再核一次 MemAvailable ≥2.5GiB 并留证；跑完请用 priority 通知 Data」。另外抄一句给主 Agent（2991221c-97d3-465e-908f-125ab3179318），priority=false。
7. 不发给 Leo。不 pkill/killall，不杀任何进程。CONT 由 19:46 的例程负责，或者在 AI 通知跑完后由 Data 主线程执行。
