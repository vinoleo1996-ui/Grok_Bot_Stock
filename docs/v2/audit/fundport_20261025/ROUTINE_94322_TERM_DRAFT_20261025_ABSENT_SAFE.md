# 94322 TERM 例程草案（2026-10-25，absent-safe）

**状态：DRAFT / 当前不可装入执行。** Arch 00:11–00:13：进程已退出，今晚不签 TERM .ok；禁止按旧 PID 94322 / starttime=100197 申请或复用任何 TERM/STOP .ok。

## 适用前提（将来若同类合并进程再起）
- 须有 Arch **新签** 的 TERM .ok（路径/sha 填入下方占位符），且 .ok 内身份字段与**当时** /proc 一致。
- 禁止复用 10-19 旧 .ok（含 8db79434、dc827675）及任何已 VOID 进 `_consumed` 的文件。

## 例程正文（粘贴用）

依据：Arch 签的 `<<ARCH_TERM_OK_PATH>>`（sha256 `<<ARCH_TERM_OK_SHA256>>`）。live=false。所有命令 stdin 用 </dev/null。只读 /proc/<pid>/stat（进程级），不用 kill -0，不 pkill/killall。

0. 核对 .ok：sha 一致、不在 _consumed/、未过期、窗口内。不符→不发信号，priority=true 报 P1。

1. 目标 PID 取自 .ok（不得写死 94322）。读 /proc/<pid>/stat：
   - 文件不存在或状态 Z：**不发信号**，回执记「已退出 / absent」，priority=false 通知 Arch 与主 Agent，结束（计 success）。
   - 四项身份（starttime jiffies、PPID、cmdline 全文、cwd）任一与 .ok 不符：**不发信号**，回执记「身份不符」，priority=true 报 P1，结束。
   - lstart 只写入回执，不参与判定。

2. 前置落盘检查：若最终 parquet 或 DONE 已存在，或日志已有 Q7a done/partial → **不发信号**，报「已落盘」，结束。

3. 仅当进程在、四项全中、且未落盘：对**该 PID** 发 SIGTERM（发前重核身份）。前后 5 秒记 state/RSS/MemAvailable/子孙。5 秒后仍在→报 P1，**不**发 KILL。子孙不处理，先报 Arch。

4. TERM 后若最终路径出现不可读半截文件：仅当 .ok 显式 allow_quarantine 时 os.replace 到 _quarantine（max_files=1），否则只报 P2。

5. 回执：docs/v2/audit/fundport_YYYYMMDD/…_TERM_RECEIPT.md（原子写）。通知 Arch + 主 Agent。不发 Leo。

## 与旧稿差异
- 删除「必须发 TERM」语义；absent / 身份不符 → 不发信号。
- PID/starttime 全部来自当时 .ok，不写死 100197/94322。
