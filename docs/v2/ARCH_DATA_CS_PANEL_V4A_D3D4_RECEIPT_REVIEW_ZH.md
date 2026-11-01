# Arch 审查：Data v4a D3D4 dry-run 回执

- 审查时间：2026-10-18T05:10:43-04:00
- 结论：通过，P0、P1、P2 均为 0。
- 已消耗的 .ok：v4a d5c326df，已归档到 output/data/_consumed/。

## 复核
1. 五个回执文件的 sha 复算后与回执一致：receipt 54869b4d、stdout 3fbe7474、ps 19494017、rawdiff 482b041e、normdiff e3b0c442（空文件）。
2. 与 v3 做归一化对比，diff 为 0 行。rss_mb 被额外掩码，这一点回执已披露，可以接受。
3. 输出路径运行前后都不存在。find 查到的 17 个文件都不是本次运行写入的，归属已经说明清楚。
4. 解释器用的是 /usr/bin/python3，与 v3 一致，可以接受。execute 必须继续用同一个解释器，并在回执中写明。

## P3-12 裁定
同意 Data 的方案：不改代码。check_manual_override 在运行时会对实际行做断言，不满足就 VOID。

execute D3D4 写完之后，由 Data 只读读取 stock_delisted_v2.parquet，把以下内容写进 execute 回执：
- 002509.SZ 那一行的五个字段：delist_period_source、delist_period_start、source_ann_no、override_source_verified、source_url；
- 非覆盖行中来源字段为空的计数，应为 338/338。

这一项列为 execute 审查的必查项。

## 下一步
- Data 提交 scripts/fix_sd1，并在工作区、blob、计划 pin 三处核对 sha。
- Arch 签 execute .ok，内容包括：两个 expectation key、SIGSTOP 94322 的条款、P3-12 的读取要求、解释器 /usr/bin/python3。
