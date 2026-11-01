# 94322 fund_portfolio 合并监看证据（10-18）

只读监看；未向任何进程发信号，未运行项目代码，未读 parquet 行数据。

## Sun Oct 18 17:07:38 EDT 2026（17:00 轮，例程实际 17:07 ET 触发）

**状态**
- /proc/94322/stat：存在，State R（运行中），PPID 94319，starttime 字段（第 22 列）= 100197 jiffies（CLK_TCK=100）。
- cmdline：`python3 scripts/acquire/remaining_after_stk_surv.py`（一致）；cwd：/workspace/QuantLab（一致）；PPID 94319（一致）。
- **lstart：ps 显示 `Sun Oct 18 01:58:57 2026`，与登记值 `Sun Oct 18 01:23:39 2026` 不一致 → 按规则判身份对不上（P1）。**
  - 旁证：ps lstart = btime + starttime/100。现在 /proc/stat btime=1792302136（uptime -s = 01:42:16），/proc/uptime=55528.36s；但该进程日志首行 ts 为 2026-10-18T01:22:24，/proc/94322 目录时间 01:22:23 —— 早于"开机时间"，说明 btime 被宿主机挂起/时钟回补推后，ps lstart 是推算值且会漂移（16:18 读到 01:23:39，现在读到 01:58:57，PID/PPID/cmdline/cwd/starttime jiffies 均不变）。高度疑似同一进程、仅 lstart 推算漂移，但按规则交主 Agent 与 Arch 裁定。
  - ps 94319 的 lstart 同样漂成 01:58:57（ELAPSED 54538s，两者一致）。
- 子孙进程（pgrep -P 逐级）：无。
- 94322 VmRSS 5,568,556 kB（≈5.31GiB），VmHWM 7,254,388 kB（≈6.92GiB，与 16:18 记录的 7.25GB 同值）。
- MemAvailable：5,316,572 kB（≈5.07GiB）。

**落盘**
- data/v2/events/fund_portfolio_2018plus.parquet：不存在。
- data/v2/events/fund_portfolio_2018plus_manifest.json：不存在。
- output/markers/fund_portfolio_2018plus.DONE（MK=ROOT/"output/markers"，脚本第 11/119 行）：不存在。
- 日志（23 行，mtime 15:33:37 ET）：Q7a_fund_portfolio 只有 period_done 行，最后一行 period=20260630（ts 2026-10-18T15:33:37）；无 done / partial / error 行。

**判定**：合并进行中，尚未写盘；进程存活。身份核对中 lstart 不一致 → 按第 6 条以 P1 报主 Agent 和 Arch（附漂移旁证）。
