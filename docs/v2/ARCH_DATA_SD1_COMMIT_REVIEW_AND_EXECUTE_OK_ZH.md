# Arch 审查：fix_sd1 提交 b9674c8b，并签发 execute .ok

审查时间：2026-10-18T05:16:17-04:00

结论：提交审查通过，execute .ok 已签发。

## 提交审查
- commit b9674c8b，parent f8e64dec，时间 10-18 05:12:13 ET。
- 共 7 个新文件、+1283 行，没有 pycache。
- 每个文件我都在两个地方算了 sha：工作区文件，和 git show 取出的提交版本。两边一致，也都和 .ok 里的 pin 一致：
  - 362e3239
  - 903e64ef
  - 6e2e1273
  - 34e46899
  - 6b8fd033
  - 542dd136
  - 7dbcf5d3
- 提交回执 sha 为 6b46951d，与 Data 报的一致。
- 披露：我用 import 校验 gate 时，在 scripts/fix_sd1 下生成了一个 __pycache__，已经当场删掉。git status 干净。

## execute .ok
文件：output/data/ARCH_RUN_AUTH_CS_PANEL_RESUMEFIX_EXECUTE_v1.ok
- sha：f03357f1
- 签发时间：10-18 05:16:02 ET（取自系统时钟）
- 失效时间：10-19 16:00 ET

签发前我用 sd1_common 的 parse_run_auth、check_mode、parse_d3d4_expectations、enforce_code 对这份 .ok 做了离线校验，全部通过。

授权内容：
- 按顺序执行四步：D1a、D1b、D2、D3D4。每一步做完，必须等 Arch 书面放行后才能开始下一步。四步必须用同一份 .ok，因为 gate 会检查上一步的回执是否在同一份 .ok 下产生。
- D3D4 的两个 expectation key 强制生效：
  - face：000861.SZ、002505.SZ、002509.SZ、600297.SH
  - UNKNOWN 计数：56
- 解释器固定为 /usr/bin/python3。

运行条件：
- 进程 94322：在两次写入 fund_portfolio_dh 之间发 SIGSTOP，然后才能开始 D1a。停止的时间和停止前最后写入的文件要记进回执。Arch 审完 D3D4 之后才 SIGCONT 恢复，任何时候都不得 kill。
- 每一步开始前检查 MemAvailable，低于 2GB 就暂停。
- P3-9：D1a、D1b、D2 三步回执里的 raw_content 必须完全一致。
- P3-12：D3D4 执行完后，只读读取 002509.SZ 那一行的五个字段，并统计非覆盖行中来源字段为空的数量，应为 338/338。
- 10-19 16:40–18:40 ET 不得运行。不得与补数重启或其他 Data 任务重叠。
- 回执写到 docs/v2/audit/data_cs_panel_execute/。
