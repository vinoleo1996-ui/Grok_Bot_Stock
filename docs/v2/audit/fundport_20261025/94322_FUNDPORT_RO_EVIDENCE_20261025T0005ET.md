# 94322 fund_portfolio 只读留证（2026-10-25 ≈00:05 ET）

live=false；本文件只读采集，未对任何进程发信号。

## 1. 宿主与进程身份

| 项 | 值 |
|---|---|
| 采集时刻 ET | 2026-10-25T00:06:12-04:00 |
| uptime -s / btime | 2026-10-24 07:41:49 / 1792842109 |
| PID | 94322 |
| PPID | 94319 |
| State | R（/proc status: R (running)） |
| starttime jiffies（stat 第22列） | 100197 |
| 推算启动 ET | 2026-10-24 07:58:30 EDT |
| 已运行 | 16.13 h |
| cmdline | `python3 scripts/acquire/remaining_after_stk_surv.py` |
| cwd | `/workspace/QuantLab` |
| Threads | 19 |
| 子孙 PID | 无 |
| VmRSS | 5868932 kB |
| VmHWM | 7254388 kB |
| VmSize | 12195356 kB |
| CPU 累计 | 9711.9 s（约 16.7% 墙钟，采样时 ps %CPU≈16.5） |
| MemAvailable | 5563496 kB |

身份四项（新锚点口径）当前全部匹配：starttime=100197、PPID=94319、cmdline 全文、cwd=/workspace/QuantLab。

**重要：** 这是 **10-24 07:41 重启后** 于 07:58:30 新拉起的进程，不是 10-18 01:22 那次。旧 STOP v2 .ok 里的 starttime=100197 是上一启动周期的 jiffies，数值碰巧相同，**不得**直接复用旧 .ok 发信号；若 TERM/STOP 须 Arch 按本启动周期重签。

## 2. 落盘与日志

| 项 | 值 |
|---|---|
| fund_portfolio_2018plus.parquet | 不存在 |
| fund_portfolio_2018plus.DONE | 不存在 |
| HOLD_FUNDPORT_MERGE | 不存在（代码会进入合并） |
| 原始分片目录 | data/v2/tushare_raw/fund_portfolio_dh |
| 报告期目录数 / _DONE 数 / 页 parquet 数 | 34 / 34 / 16538 |
| 日志 | `logs/remaining_after_stk_surv_restart_20261018_0122ET.log` mtime=2026-10-18 15:33:37 EDT size=3198 |
| 日志最后一条 Q7a | `{"item": "Q7a_fund_portfolio", "status": "period_done", "ts": "2026-10-18T15:33:37.437658", "period": "20260630", "pages": 1676}` |
| 日志含 status=done/partial/error（Q7a） | 无（仅有 10-18 的 start + 19 条 period_done，最后一期 20260630 @ 15:33:37） |

重启后日志文件无新行：stdout 接到旧日志且 Python 块缓冲；34 期均有 `_DONE`，循环 `continue` 不打 period_done；合并阶段（L96–L104）中间无日志，直到 `to_parquet` 完成后才打 done/partial。

## 3. 卡在哪一步

脚本 `scripts/acquire/remaining_after_stk_surv.py`：

1. L82–93：拉数 — **已完成**（34/34 `_DONE`，页数与 10-18 日志一致）。
2. L94：`merge_held` — HOLD 文件不存在，**不会 return**。
3. L96：`pd.concat([pd.read_parquet(f) for ... 16538 个文件])` 随后 dedup/排序/算 available_at — **当前正在此段**。
4. L104：`to_parquet` 最终表 — **尚未开始**（无最终文件；`/proc/94322/fd` 仅有 stdin/日志/两个 socket，无 parquet 写句柄）。

3 秒 IO 采样：`rchar +77MB`、`wchar 0`、`write_bytes 0` → 仍在读/算，未写最终产物。累计 `rchar≈202GB`（远超磁盘分片 ≈339MB），符合反复读页缓存 + pandas 拷贝。

## 4. 内存与还会吃多久

- 当前 RSS ≈5.87GB，HWM 7.25GB（与 10-18 合并峰值相同量级）。
- Arch 已知：整表 in-process merge 16.5M 行峰值约 7.25GB；流式按期合并目标 ≤1.5GiB（P3）。
- **无法可靠给出剩余墙钟**：无进度日志；读 16538 个小文件 + 两次 drop_duplicates 可能还需数小时，也可能接近尾声。重启后已跑 ≈16.1h 仍未落盘。
- MemAvailable ≈5.5GB，高于 2.5GiB 线，但进程本身长期占 ≈5.8GB。

## 5. 处置建议（今晚不发 STOP/TERM/KILL）

| 选项 | 建议 |
|---|---|
| A. 继续等 | 可再观察一个短窗（例如到 10-25 06:00 ET）：若出现最终 parquet/DONE 或日志 done 行，按原回执流程交 Arch。**不保证**会结束；已跨 10-18 失败合并 + 本次 16h。 |
| B. 签新 .ok 再 TERM | **推荐（主路径）**：Arch 按本启动周期重签一次性 TERM .ok（PID 94322、starttime=100197、PPID 94319、cmdline/cwd、窗口）；确认仍无最终写句柄后 SIGTERM；**不**复用 10-19 旧 .ok。TERM 后禁止直接重跑同一 L96 整表 concat。 |
| C. 改成分块流式 | **TERM 后必做**：按期（或按月）流式合并，峰值 ≤1.5GiB，中间落盘/可断点；Data 出 diff 说明，Eng 实现，Arch 审 + 新 .ok 后再跑。对应既有 P3（HOLD 解除后的正确合并形态）。 |

默认建议：**A 短窗监看 + 并行准备 B/C 文案**；若 06:00 仍无 DONE/parquet，走 B→C。live=false。

## 6. 附带（用量停摆）

10-18 17:20 起多条例程因 Grok Bot 用量耗尽失败，包括 fundport 监看、BACKUP_PIN 硬链接、04:25 STOP、18:45 CONT、日更等。BACKUP_PIN 窗口已过，需 Arch/主 Agent 决定是否重签硬链接 .ok。本留证不处理这些。
