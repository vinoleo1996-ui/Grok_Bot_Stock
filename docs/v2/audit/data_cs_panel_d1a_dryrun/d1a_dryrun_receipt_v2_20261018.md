# D1a dry-run 回执 v2（r5 代码，v2.ok）
- 时间：2026-10-18 02:08:38–02:09:03 EDT；执行人：QuantLab Data；单进程，live=false，promotion=false
- 命令：`PYTHONDONTWRITEBYTECODE=1 nice -n 10 python3 scripts/fix_sd1/build_cs_panel_v2_resumefix.py --arch-ok output/data/ARCH_RUN_AUTH_CS_PANEL_RESUMEFIX_v2.ok --fixes none`
  - 没有加 --execute。
  - 峰值 RSS 的测法与单测回执相同（外层 subprocess + getrusage）。
- .ok：cc04d83d9889f8f4a3ead8a82bce0aa98d23ad94978635d12f1feb068c3ecfae；expires 2026-10-19 02:07 ET，运行时未过期。
- 代码与方案的 7 个 sha 和 .ok 一致，与 _recovery/data/sd1_r5_20261018/SHA256SUMS 一致。
- stdout：docs/v2/audit/data_cs_panel_d1a_dryrun/d1a_dryrun_stdout_20261018_v2.txt，sha256 见送审消息。
  - 内容为 GATE_PASS step=D1a_fixesnone_check mode=dryrun ok_sha256=cc04d83d…。
  - 末行为 "DRY-RUN PASS: nothing written"，exit 0。
- 逐年一致性：

| 年 | 行数（=v1） | frame_equals | table_equals | rss_mb |
|---|---|---|---|---|
| 2018 | 783,166 | true | true | 704 |
| 2019 | 846,470 | true | true | 908 |
| 2020 | 880,720 | true | true | 957 |
| 2021 | 983,990 | true | true | 1026 |
| 2022 | 1,087,168 | true | true | 1070 |
| 2023 | 1,163,879 | true | true | 1119 |
| 2024 | 1,198,136 | true | true | 1260 |
| 2025 | 1,204,295 | true | true | 1270 |
| 2026 | 924,485 | true | true | 1270 |

- 峰值 RSS：子进程 maxrss 为 1,300,980 KB（约 1270 MB），不超过 1.5 GB。
- 运行前 MemAvailable 约 11.1 GB。
- 没有出现 VOID，也没有触发不变式。fixes none 路径不走补回，这条路径本身也不会产出 unknown 计数。
- 零写入确认：
  - output/ai_factory/panel_cache_v2_fixesnone、panel_cache_v2_resumefix、data/v2/suspend_flags、data/v2/ref/stock_delisted_v2.parquet 都不存在（ls 报 No such file）。
  - output/、data/ 在 .ok 之后没有新增 staging 或 VOID 文件。
  - scripts/fix_sd1 下没有 __pycache__。
- 本次 dry-run 取代 02:04 的 v1.ok 旧代码 dry-run（Arch r5 P2-1）。
- 未跑 D1b、D2、D3D4。
