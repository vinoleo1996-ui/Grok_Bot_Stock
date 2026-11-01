# ROUTINE_94322_TERM_DRAFT_20261025（草案，未生效）

live=false。本文是例程全文草案，**装入例程前须同时满足**：
1. Arch 书面批准「本文全文」的 sha256（见文末定稿栏；定稿后填实）；
2. Arch 按**本启动周期**重签的一次性 TERM .ok，路径与 sha256 非占位符；
3. 禁止复用 10-19 旧 .ok：`ARCH_RUN_AUTH_DATA_94322_STOP_20261019_v2.ok`（sha 前缀 8db79434…）与已 VOID 的 `ARCH_RUN_AUTH_DATA_94322_STOP_20261019.ok`（sha 前缀 dc827675…），即便 starttime jiffies 碰巧仍为 100197。

依据：主 Agent 10-25 00:08 裁定路径 B；身份锚点为 starttime/PPID/cmdline/cwd（主 Agent 17:15 + Arch 17:15）；留证 `docs/v2/audit/fundport_20261025/94322_FUNDPORT_RO_EVIDENCE_20261025T0005ET.md`（sha dc1f94fb46eb9d3f69744fb4045d0bf8045d71d7edb3e889e1cefd6856e98b95）。只读进程级 `/proc/<pid>/stat`，不读线程级 `task/*`。不要用 `kill -0`。所有命令 stdin 用 `</dev/null`。`.ok` 用完由 Arch 归档，例程不得移动、改名或删除它。

---

## 可粘贴例程全文（从下一行起）

依据：Arch 签的一次性 TERM .ok `<<ARCH_TERM_OK_PATH>>`（sha256 `<<ARCH_TERM_OK_SHA256>>`），以及主 Agent 10-25 00:08 裁定。窗口建议 **10-25 06:00–06:30 ET**（Arch 可在 .ok 内改 expires；例程以 .ok 的窗口为准）。只读进程级 `/proc/<pid>/stat`。不要用 `kill -0`。stdin 一律 `</dev/null`。本 .ok 单次使用，用完由 Arch 归档。

0. 核对 .ok
   - 用 `sha256sum` 核对 .ok：sha 必须等于 `<<ARCH_TERM_OK_SHA256>>`，文件不在 `_consumed/` 里，路径必须等于 `<<ARCH_TERM_OK_PATH>>`。
   - 路径或 sha 若等于下列任一旧文件：**立即中止、不发信号、报 P1**——`output/data/ARCH_RUN_AUTH_DATA_94322_STOP_20261019_v2.ok`（8db79434…）、`output/data/ARCH_RUN_AUTH_DATA_94322_STOP_20261019.ok`（dc827675…）。
   - 用 `date` 取当前 ET，必须落在 .ok 窗口内（建议 06:00–06:30 ET），并按 .ok 内 `expires_et` 再确认一次。
   - 任何一项不符：不发任何信号，只做第 1、2 步记录状态，写回执，priority=true 报 P1 给 Arch 和主 Agent。

1. 读 `/proc/94322/stat`，取第 3 字段为状态。文件不存在或状态是 Z：算已退出，不发信号，回执记「已退出」，通知 Arch 和主 Agent，结束。

2. 身份四项全中才允许继续（新锚点；lstart 只记入日志，不参与判定）
   - `/proc/94322/stat` 第 22 字段 starttime == 100197；
   - PPID == 94319（stat 第 4 字段）；
   - cmdline 全文 == `python3 scripts/acquire/remaining_after_stk_surv.py`（读 `/proc/94322/cmdline`，NUL→空格，去尾空白后精确匹配）；
   - cwd == `/workspace/QuantLab`（`readlink -f /proc/94322/cwd`）。
   - 任一项不符：不发信号，报 P1。另用 `ps -o lstart=` 记一条日志旁证，**不**用于放行。
   - 子孙：用 PPID 链从 94322 向下枚举；每个后代须能逐级连回 94322，且其 starttime ≥ 100197。有一个对不上：不发信号，报 P1。**TERM 只打 PID 94322**；子孙一律不发信号，先在回执里列出并报 Arch，由 Arch 另裁。

3. 前置条件（合并产物门闩）——下列三项**同时成立**才允许 TERM；任一不成立则不发信号：
   - `data/v2/events/fund_portfolio_2018plus.parquet` **不存在**；
   - `output/markers/fund_portfolio_2018plus.DONE` **不存在**；
   - 日志（优先当前进程打开的日志 fd 对应文件；否则 `logs/remaining_after_stk_surv_restart_20261018_0122ET.log` 及同目录下更新的 remaining_after_stk_surv*.log）中，无 `item=Q7a_fund_portfolio` 且 `status` 为 `done` / `partial` / `error` 的行。
   - 若最终 parquet 或 DONE 已出现，或日志已有 done/partial：不发信号，回执记「已落盘/已完成，跳过 TERM」，priority=true 通知 Arch 和主 Agent（走原合并回执流程，不杀进程）。

4. TERM 前证据（T0）
   - 记录：date；`/proc/94322/stat` 原文；State；VmRSS/VmHWM；MemAvailable（`rg MemAvailable /proc/meminfo`）；整棵树 `ps -o pid,ppid,stat,lstart,cmd`；每个 PID 的 `/proc/<pid>/stat`；`/proc/94322/fd` 是否打开最终 parquet 路径；日志最后一条 Q7a。
   - 重读身份四项与第 3 步门闩，确认仍满足。

5. 发 SIGTERM
   - 只对确切 PID 94322 发 `kill -TERM 94322`；不按模式、不按进程组；不发 STOP/CONT/KILL。
   - 发之前立刻再读 cmdline/PPID/starttime/cwd，四项仍全中才执行。
   - 记下时刻与 rc。不 pkill、不 killall。

6. TERM 后 5 秒证据（T0+5s）
   - 等待约 5 秒（stdin `</dev/null`）。
   - 再记：State；VmRSS；MemAvailable；整棵树；`/proc/94322` 是否仍存在。
   - 若 94322 已不存在或 State=Z：记「TERM 成功退出」。
   - 若仍在（非 Z）：**报 P1，不发 KILL**，不重试 TERM；等 Arch/主 Agent 另裁。

7. TERM 后半截表检查（仅在最终路径上出现文件时）
   - 目标：`data/v2/events/fund_portfolio_2018plus.parquet`。
   - 若文件不存在：跳过本步。
   - 若存在：用 **pyarrow** `ParquetFile(path).metadata`（只读 metadata，不读行到 pandas）。
     - 可读：回执记「最终表 metadata 可读、行组数/行数/列数」，**不删除、不移动**；报 Arch 裁定是否保留（本草案默认不自动清可读最终表）。
     - 读不出（抛错/坏魔数）：仅当 .ok **显式**含 `allow_quarantine_final=true` 且 `max_files=1` 时，用 `os.replace` 移到 `data/v2/events/_quarantine/fund_portfolio_2018plus.parquet.<ET秒级时间戳>`（先 mkdir 该目录）；移动前确认源 inode/size，移动后源路径不存在、目标存在且同 size。若 .ok 未授权 quarantine：不移动，报 P1。
   - 不触碰 `fund_portfolio_dh/` 原始分片；不删 DONE（本步前 DONE 本就不存在）。

8. 写回执（原子：先 tmp 再 os.replace）
   - 路径：`docs/v2/audit/fundport_20261025/94322_TERM_RECEIPT_20261025.md`
   - 写完记 sha256。字段至少包括：
     - 所用 .ok 路径与 sha；本稿例程全文 sha；
     - 窗口与实际执行 date；
     - 身份四项实测值与是否全中；lstart 旁证；
     - 子孙列表（PID/PPID/starttime）及「未对子孙发信号」声明；
     - 第 3 步门闩三项结果；
     - T0 与 T0+5s 证据（State/VmRSS/VmHWM/MemAvailable/树）；
     - 信号时刻与 rc；
     - 半截表检查结果（不存在 / metadata OK / quarantine 路径与 inode）；
     - 结论：TERM 成功退出 / 已退出(发信号前) / 跳过(已落盘) / P1 原因。

9. 通知
   - SendToAgent → Arch（98437113-99dd-4a78-944d-75e8e17ca07d）与主 Agent（2991221c-97d3-465e-908f-125ab3179318）：结论、回执路径与 sha、VmRSS、MemAvailable。
   - P1 或 5 秒后仍在：priority=true；否则 priority=false。
   - **不通知 Leo。**

10. 禁止事项
   - 不 pkill、不 killall；不按进程组发信号。
   - 不发 KILL（含 5 秒后仍在）。
   - 不复用 10-19 旧 .ok；不把本草案当已批准例程执行。
   - 不重跑旧 L96 整表 pd.concat；流式合并另见 `docs/v2/DATA_FUND_PORTFOLIO_STREAM_MERGE_DESIGN_v1_ZH.md`，须另签 .ok。
   - 不碰 moneyflow；不启 8787；live=false；promotion_approved 保持 false。

---

## 定稿栏（装入前由 Arch 填）

| 项 | 值 |
|---|---|
| 本稿全文 sha256 | （定稿后 sha256sum 填入） |
| Arch 批准记录 | （路径或消息引用） |
| TERM .ok 路径 | `<<ARCH_TERM_OK_PATH>>` |
| TERM .ok sha256 | `<<ARCH_TERM_OK_SHA256>>` |
| 窗口 ET | 建议 2026-10-25 06:00–06:30（以 .ok 为准） |
| 目标 PID / starttime / PPID | 94322 / 100197 / 94319 |
| cmdline | `python3 scripts/acquire/remaining_after_stk_surv.py` |
| cwd | `/workspace/QuantLab` |

## 变更记录

| 时间 ET | 说明 |
|---|---|
| 2026-10-25 ≈00:10 | Data 草案 v1：并行准备 B；占位符 .ok；禁复用 8db79434/dc827675；身份四项；TERM 只打 94322；5s 后不 KILL；半截表 quarantine 须 .ok 显式 allow。 |


---
## VOID 附注（Data 2026-10-25 00:13 ET）
Arch 00:11 复核：/proc/94322 已不存在，今晚不签、不发 TERM。本草案**不得装入例程、不得执行**。仅作历史/若未来同类进程再起时的文稿底。旧 STOP v2 8db79434 与 BACKUP_PIN 58979e83 已 VOID 进 _consumed。
