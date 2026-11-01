# Arch 审查：Data v3 D2_suspend_flags dry-run 回执

- 审查时间：2026-10-18 04:58 ET
- .ok：dac5f6dd
- 结论：通过（P0/P1/P2=0，P3=1）。放行 D3D4_stock_delisted dry-run。

## 复核
1. 三个 sha 复算一致：stdout a7256773、receipt 1673f0f4、ps 5cf38ba7。GATE_PASS step=D2_suspend_flags mode=dryrun，没有 VOID。
2. table_rows = 111,480 = 123,614 − 12,134，与 R6B 审查 §86 的预期一致。
3. 归一化 diff 只在 stats 行，halted_fullday、intraday_halt、resume_announced、conflict_v1 逐年不变。is_resume_day 等于非 BJ 计数加上保留的 BJ 行，2019 年为 564 = 563 + 1，2020 年为 545 = 542 + 3。差异全部来自 .BJ 修正，属于预期。
4. without_R 从 12,169 降到 35，每一行在回执中都逐条列出。其中 2018 年有 5 行没有前一交易日（gap=-1），属于数据起点的边界情况，可以接受。
5. suspend_flags 和 stock_delisted_v2 都不存在。运行开始后，data/v2 下除 fund_portfolio_dh（94322 写入）之外没有新文件，这一项由 Arch 复算。94403=Ts。

## P3
- P3-9：raw_content 在 dry-run 中不打印。execute 时须在 manifest 里对照 D1b 和 D2 的 raw_content，并在回执中给出这两个 sha。
