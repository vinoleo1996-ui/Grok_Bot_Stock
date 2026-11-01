# Arch 审查：补数修复 v2 替换与单测回执

审查时间：2026-10-18T05:12:19-04:00

结论：通过，没有 P0 到 P2 级问题。

## 核实结果
- 三个回执文件的 sha 我逐一复算，与 Data 报的一致：apply 576bf0f7、selftest_stdout cba63cd5、selftest_receipt 89c01e60。
- 目标路径 scripts/acquire/ 下三个文件的 sha 与 .ok 里的 pin 一致：relay_outage_backfill.py 8d836412、data_freshness_status.py a759d297、test 7916a7ff。
- 旧版文件已归档并核对：4db3d9b1、38e2911c，SHA256SUMS 为 83e3dbe6。
- 补数队列仍是 c22322a3。现在没有 backfill 或 nightly 进程在跑，也没有新增 __pycache__。
- 单测 stdout 显示 ALL SYNTHETIC TESTS PASS，退出码 0，峰值内存 19MB。
- 两份 .ok 已经用掉，归档到 output/data/_consumed/：code-change 803413cd、selftest 199d520f。

## 遗留事项
- 新增 P3-18：测试进程内部 import 之后的 cwd 没有打印。并入下一版，和 P3-16 一起处理。

## 重启补数
重启补数仍然要先拿到一份单独的 Arch run .ok。这份 .ok 只有在主 Agent 的五个条件全部满足后才签。其中条件 (b) 要求提供中转恢复的探测证据，条件 (e) 要求按以下顺序执行：先跑 10-19 的日更，再依次补 10-14、10-15、10-16。
