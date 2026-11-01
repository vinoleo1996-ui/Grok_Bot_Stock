背景：
- 主 Agent 10-18 16:18 ET 裁定，Arch 16:21 ET 补充（审计记录 docs/v2/audit/AUDIT_20261018_1619_ET_ZH.md，sha 4dbcc4c4）。
- 94322 的身份：PPID 94319；cmdline「python3 scripts/acquire/remaining_after_stk_surv.py」；lstart Sun Oct 18 01:23:39 2026；cwd /workspace/QuantLab。
- 它正在进程内合并 fund_portfolio：34 期，共 16,520,890 行。16:18 时 VmRSS 5.25GB、VmHWM 7.25GB，OOM 风险高。
- 规则：让它写完，合并或写盘进行中不 kill、不 STOP。
- 主 Agent 16:22 已定：叶25 今晚顺延，不为它 TERM 94322。18:58 和 19:46 两条例程已暂停，本例程不再处理叶25 空档。

本例程只做只读监看：
- 绝不向任何进程发信号；
- 除证据文件外，不改任何文件；
- 不运行项目代码；
- 不读 parquet 行数据。算 sha 只用 sha256sum；行数只从 manifest 读，或者用 pyarrow.parquet.read_metadata 的 num_rows。

每次运行（17:00、17:20、17:30、17:50、18:00、18:20、18:30、18:50 ET）：
1. 读状态
   - 用 `date` 取时间。
   - 只读 /proc/94322/stat。状态 Z 或进程不存在，算已退出；绝不用 kill -0。
   - 核对 94322 身份：PPID、cmdline、lstart 都要一致。
   - 用 pgrep -P 逐级列出子孙进程。对 94322 和每个子孙进程，读 /proc/<pid>/status 里的 VmRSS 和 VmHWM。
   - 读 /proc/meminfo 里的 MemAvailable。
2. 查落盘
   - 以下三个文件是否存在；存在的，记下大小和 mtime：
     - data/v2/events/fund_portfolio_2018plus.parquet
     - data/v2/events/fund_portfolio_2018plus_manifest.json
     - output/markers 下的 fund_portfolio_2018plus.DONE（以脚本里 MK 的定义为准）
   - 日志 /workspace/QuantLab/logs/remaining_after_stk_surv_restart_20261018_0122ET.log 里，有没有 item=Q7a_fund_portfolio、status 为 done、partial 或 error 的行。
   - 判定：parquet 是直接写到最终路径的，不是原子写。日志里出现 done 或 partial 行，并且 manifest 已出现，才算落盘完成。只有 DONE 标记也出现，才算完整成功。只有文件、没有日志行，算「写盘中」。
3. 记证据：把以上全部内容追加到 /workspace/QuantLab/docs/v2/audit/leaf25_window_20261018/94322_FUNDPORT_MERGE_WATCH_20261018.md，作为单独一段，标题写本次的 date。
4. 17:20 这一轮：无论结果如何，都把这一段证据交给主线程，由主线程用 priority 转给 QuantLab Arch。Arch 要在 17:25 签日更 .ok 之前用到它。
5. 首次发现落盘完成时：
   - 从日志行取 rows、n_fails、sha256；
   - 用 sha256sum 重算 parquet 的 sha，并和日志里的对照；
   - 再用 manifest 或 num_rows 核对行数；
   - 峰值 RSS 取所有证据里 VmHWM 的最大值；
   - 交给主线程，转告主 Agent 和 Arch，内容包括当前 VmRSS、MemAvailable，以及 MemAvailable 是否 ≥2.5GiB（2621440 kB）。
   - 如果 VmRSS 高于 2GiB（2097152 kB），只报告，不做任何处理。是否在 10-19 04:20–04:45 用 TERM .ok，由主 Agent 和 Arch 决定。
6. 94322 已退出，但日志里没有完成行；或者身份对不上：交给主线程，以 P1（priority）报主 Agent 和 Arch。之后每轮只记证据。
7. 18:50 这一轮：记完证据后，把 17:20、18:30、18:50 三个时点的汇总交给主线程，转给 Arch 和主 Agent，然后删除本例程。

结果去向：只交给我（QuantLab Data）的主线程，由主线程用中文转告 Grok Bot 里的 QuantLab Arch 和主 Agent，不直接发给 Leo。除第 4 至第 7 条列出的情况外，只追加证据，不发任何消息。
