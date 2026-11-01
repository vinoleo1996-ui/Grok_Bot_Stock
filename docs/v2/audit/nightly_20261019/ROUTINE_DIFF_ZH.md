# 10-19 日更例程逐节 diff：现行 routine a → 驱动版草稿 v3（Data，待 Arch 终审）

- 作者：QuantLab Data；修订 2026-10-18 13:02 ET（原地修改；上一版 6b4efc98… 已归档 _recovery/data/nightly_20261019/predraft3_20261018T125243/）。
- 旧：docs/v2/audit/nightly_20261019/ROUTINE_A_CURRENT_20261018.txt（a95cda62964104f5b21ea8f150b85cc4d1fafff84bb64e08f0981620c2a74b45）。
- 新：ROUTINE_PROMPT_DRAFT_ZH.md（02498e1e478f23d4f8060e38e6ae533678f91ad66e1ac9a0f78f1d15c7e2eb41）+ run_nightly_v1.py（63b5a88462f9f75ae7975f52320bbd6f88433cdf4857bf95c6de557d6d880e16）+ routine_fallback_v1.py（f3244472da360b74cc692f90548fab4f8839f13f3938bf65374d592b2d61ac5f，新）。驱动代码 diff：DRIVER_DIFF_vs_predraft2_20261018T130216.diff。
- 依据：Arch 2dada5ed §5 1–17；主 Agent 12:32（1）–（4）；Arch 12:36 / 12:38；Eng 12:40。
- 记号：「=」不变；「~」改写；「+」新增；「−」删除。

## 本轮相对上一版草稿（1d372ced）的变化
| 项 | 上一版 | 本版 | 依据 |
|---|---|---|---|
| 94322 SIGCONT 一节 | 照搬旧文：T 且 cmdline 对则对 94322 SIGCONT | **− 删除**；改为只读前置：94322 / 94403 须为 T 或已退出，例程与驱动都不发任何信号 | 主 Agent 12:32 第 4 条；Arch 12:36 |
| 94403 | 未提 | + 前置同 94322；写明 94403 已于 10-18 04:59:31 ET 退出（cont_94403_20261018.md）；**原 05:00 的 94403 CONT 例程已删除**（不再存在，本例程也不得替它发 CONT） | Arch 12:38；主 Agent 12:33 |
| 档位时间 | strict 06:20 墙钟 / call B ≤ 06:30；relaxed 30 分钟 / ≤ 16:00；call B 预算 55 | 两档同一时间盒：daily_pull 30 分钟硬停；call B 预算 75，闸门 起跑 + 75 ≤ 16:00，在 min(起跑 + 75, 16:00) 硬停 → FAILED；无 06:20 / 06:30 | Arch 第 1 项；主 Agent 12:32 第 1、2 条 |
| call B 超时 | 只报 P1，不停，16:40 才停 | 硬停 → FAILED（CALLB_TIMEOUT），恢复并双核日历，绝不 DONE | 主 Agent 12:32 第 2 条 |
| 停止顺序 | 先停 tier1_pull 再停 nightly | SIGSTOP 父 → 重新枚举 → 冻结后代 → 最深 TERM + CONT → 10 秒 → KILL → KILL 父 → wait 超时 → 孤儿扫描 | Arch 第 2 项 |
| 失败收尾 | 未捕获异常无统一出口 | 信号 / 异常 / 子工具超时统一：停树 → 恢复日历双核 → 回执 → 唯一 FAILED → 退出 11 | Arch 第 3 项 |
| 退出码 | 0 / 1 / 2 / 3 / 4 | + 10（预检通过）、11（统一异常收尾）、137（被 KILL，转兜底） | 主 Agent 11:42；Arch 第 3 项（见冲突说明） |
| 兜底 | 无 | + 第五节：驱动结束后 20 分钟内跑 routine_fallback_v1.py（pgrep 空 + 备份 sha == PIN 才原子恢复；无 marker 代写 FAILED driver_killed；sha 仍不符 = P1） | Arch 第 9 项；主 Agent 12:32 第 3 条 |
| 中止驱动 | 未写 | + 只对驱动确切 PID 发 TERM，等 ≥ 90 秒，不发 KILL、不碰子进程 | Arch Q-A7 |
| 子进程环境 | 未写 | + TSPRO_RELAY_TIMEOUT=115 恒设；call A 恒设 TIER1_SKIP_CAL_REFRESH=1 并查日志证据；SOURCE=relay 仅 .ok source_relay_only=true | Arch 12:36 / 12:38；Eng 12:40 |
| 钉 sha | 7 个 | Arch §6 全集（含 tier1_pull 5b70dfed、tushare_proxy、relay_health、11 个步骤脚本、routine_fallback） | Arch 第 15 项；Eng 12:40 |
| pgrep 前置 | 一条 web pgrep | 两条锚定 pgrep（web / data）为空 | Arch 第 14 项 |
| 核查 | ≥ 2026-10-19 | 日期统一 YYYYMMDD 后 == 20261019；只认本次写入（时间戳晚于 call B 起跑）；hsgt rc=2 视同 partial | Arch 第 13 项 |

## 逐节对照（旧 routine a → 新稿）
| 旧节 | 旧内容（摘） | 新稿位置 | 变化 |
|---|---|---|---|
| 开头 | 研究级，live/promotion=false，不启 8787，不碰 moneyflow | 正文首行 | = |
| 【启动前检查】 | 94322：读 stat；T 且 cmdline 对则 SIGCONT；回执；通知 Arch、AI | 第一节 | **−** SIGCONT 删除；**~** 改为 94322 / 94403 只读前置（T 或已退出），不发信号；**+** 两条 pgrep；**+** ET 日期与 05:25 |
| （无） | — | 第二节 | + 记录 S；按 .ok 选档；--check-only 预检（通过 = 退出 10） |
| step 0 | 冻结日历 fa4260b8 + 开市检查；v1 快照对基线 | 第三节第 2、4 条 | ~ 驱动核 PIT / closure 跑前跑后 sha；核 PIN 日历中 20261019 为开市日；快照改 v2 + 范围 04d716af，本次 BEFORE / AFTER 比对 |
| step 1 | cp -p 备份 .bak，核 141078fa | 第三节第 4 条 | ~ run_<时间>/trade_cal.parquet.141078fa，两份 sha，chmod 444 |
| step 2 | call A daily_pull | 第三节第 5、6 条 | ~ 驱动 /usr/bin/python3 前台串行；30 分钟硬停；RSS 1484800 / 1536000；停树顺序见上；子进程环境见上 |
| step 3 | 不论 rc：比对 → 原子恢复 → sha 必须 141078fa | 第三节第 7 条 | ~ 先确认树已不在；cal_compare_v1 → cal_restore_v2（rc=2 复跑）→ 失败 / 超时走驱动自带原子恢复 → 30 秒双核；每次尝试后、call B 后、收尾、异常路径都做 |
| （无） | — | 第三节第 8 条 | + 原始文件判据（实测 trade_date min=max=D）；凭 .ok 隔离；relaxed 仅 MAX_RUN 可重试 |
| step 4 | call B 14 步 | 第三节第 9 条 | = 14 步不变；+ 75 分钟预算闸门与硬停 |
| step 5 | 跑后快照 + fa4260b8/7ccc911e | 第三节第 10 条 | ~ 快照 v2 AFTER + compare |
| step 6 | 按实际行数 / 日期判定 | 第三节第 10 条 + 第六节第 1 条 | ~ 驱动机检只认本次写入；其余步骤 Data 回执补齐 |
| step 7 | 回执 | 第三节第 11 条 + 第六节 | ~ driver_receipt + 唯一 marker（reason_codes） |
| （无） | — | 第四节 | + 退出码 0 / 1 / 2 / 3 / 4 / 10 / 11 / 137 |
| （无） | — | 第五节 | + 20 分钟兜底 routine_fallback_v1.py（退出码 0 / 1 / 3 / 5 / 6 / 2） |
| 报告 | Leo 简报；Eng；Arch 与主 Agent | 第六节 | = ；+ 兜底回执 |
| 约束 | MemAvailable；不 heredoc；只停确切 PID | 第七节 | = ；+ 不给 94322 / 94403 发任何信号 |

## 删除项
− 旧【启动前检查】中对 94322 的 SIGCONT（主 Agent 12:32 第 4 条）。
− 原 05:00 ET 的 94403 CONT 例程（已由主 Agent 删除；本例程不替代它）。
− 旧 step 0 的 v1 快照对基线 dfdc2555；旧 step 1 的 .bak 文件名。
− 上一版草稿的 strict 06:20 / 06:30 与 call B 预算 55。

## 需主 Agent 留意
- 退出码冲突：主 Agent 11:42 定预检通过 = 10；Arch 第 3 项把 “exit 10” 写进统一失败收尾。本稿：预检通过 = 10、统一异常收尾 = 11，待 Arch 确认。
- 例程从此不发任何 SIGCONT；94322 若届时为 S（2026-10-18 12:50 ET 实测 State: S），驱动会拒跑——需要在 05:25 前由其负责方暂停或确认已退出。
