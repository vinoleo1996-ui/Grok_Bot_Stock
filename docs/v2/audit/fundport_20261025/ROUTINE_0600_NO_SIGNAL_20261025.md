# 06:00 收口例程全文（无信号）folder 94322-06-00-term

状态：paused。原 TERM 路径取消。交 Arch 审。

主 Agent 00:13/00:14 + Arch 00:11：原 06:00 TERM 已取消。本例程若被恢复，只做只读收口，永不发信号。live=false。

0) `date`；窗口外则报 P2、删除本例程。
1) 读目标 PID（历史为 94322，以当时 .ok 为准，无 .ok 则只查 94322）：/proc 不存在或状态 Z → 记 absent=success，不发信号；查最终 parquet/DONE/日志 Q7a done|partial。
2) 若已落盘：priority=true 报「已落盘，走回执」。
3) 若 absent 且未落盘：priority=false 报「合并未完成退出（非静默成功）」，附退出留证路径。
4) 若进程仍在：不发 TERM/STOP/KILL（今晚及本例程生命周期内禁止）；priority=true 报 P1「进程仍在，需 Arch 另裁」，结束。
5) 四项身份不符同样不发信号，报 P1。
6) 删除本例程与监看例程。不发 Leo。不碰备份。
