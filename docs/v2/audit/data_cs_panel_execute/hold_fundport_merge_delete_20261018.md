# 删除 output/HOLD_FUNDPORT_MERGE（主 Agent 预授权）

- 依据：主 Agent 预授权，条件是 cs_panel 重建和 D-2/D-3/D-4 修复完成后才删除。条件已满足：SD1 四步 execute 均已通过 Arch 审查，见 docs/v2/ARCH_DATA_SD1_EXEC_D3D4_REVIEW_ZH.md（05:34:17 EDT）。
- 删除前记录（2026-10-18 05:38:24.734919042 EDT）：
  - size=238 B，mtime=2026-10-18 01:22:16.396683904 -0400
  - sha256=c9801f90d3be9f2600c36ceff5dd7adee410dc00dd346cc105faa2429436cec7
- 原文：
```
HOLD fund_portfolio + broker_recommend merge.
set 2026-10-18 01:2x ET by QuantLab Data per 主 Agent (cs_panel 重建 + D-2/D-3/D-4 修复之后才合并).
删除本文件后重跑 scripts/acquire/remaining_after_stk_surv.py 即合并。
```
- 已删除：2026-10-18 05:38:24.742543193 EDT；`ls` 确认文件已不存在：ls: cannot access 'output/HOLD_FUNDPORT_MERGE': No such file or directory
- 未手动执行 fund_portfolio 或 broker_recommend 合并。
- 影响说明：94322 仍在同一进程内跑 fund_portfolio 分页。脚本第 94 行和第 137 行在分页结束后才检查 HOLD。HOLD 已删除，所以 94322 会在当前进程内自动完成以下合并（不需要重跑脚本）：
  - 剩余分页拉完后，写出 data/v2/events/fund_portfolio_2018plus.parquet（含 manifest），并改写 docs/v2/DATA_FUND_PORTFOLIO_FULLWINDOW_RECEIPT_ZH.md
  - broker_recommend：106 个月的原始缓存已全部存在，会直接合并为 data/v2/events/broker_recommend_2018plus.parquet（含 manifest），并改写 docs/v2/DATA_BROKER_RECOMMEND_RECEIPT_ZH.md
