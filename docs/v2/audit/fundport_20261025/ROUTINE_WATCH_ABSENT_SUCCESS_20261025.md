# 监看例程全文（absent=success）folder 94322-10-25-06-00

状态：paused。交 Arch 审。

主 Agent / Arch 10-25 口径：只读监看。窗口原至 10-25 06:00 ET；进程已确认退出后本例程保持暂停，若恢复则按下列执行。绝不发 STOP/TERM/KILL/CONT。不改代码、不读 parquet 行、不动备份。live=false。

每次运行：
1) `date` 取 ET。若已过 10-25 06:00，删除本例程并结束。
2) 读 /proc/94322/stat：不存在或状态 Z → 记「absent/已退出」，证据追加后本轮计 success，不发信号；连续确认 absent 后可暂停或删除本例程，priority=false 告知 Arch 与主 Agent 一次即可。
3) 若进程仍在：核四项身份（starttime、PPID、cmdline、cwd）。不符→不发信号，priority=true 报 P1。lstart 只记日志。
4) 记 VmRSS/VmHWM/MemAvailable、子孙；查最终 parquet、DONE、日志 Q7a done|partial。
5) 证据追加 docs/v2/audit/fundport_20261025/94322_FUNDPORT_WATCH_20261025.md。
6) 首次出现 parquet/DONE/日志 done|partial → priority=true 报 Arch 与主 Agent。不发 Leo。
