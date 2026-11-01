# 10-19 日更驱动 v3.1 说明（对 63b5a884 / f3244472 的增量）

- 生成：2026-10-18 13:40 ET，QuantLab Data。未对真实数据运行；所有自测只用 /tmp 假进程与假文件。
- 依据：Arch 行级审 docs/v2/ARCH_DATA_NIGHTLY_V1_LINE_REVIEW_ZH.md（ec1ac8e1，13:15）；主 Agent 13:19 裁定；Arch 13:21 / 13:23；Eng 13:24 marker 契约 F1–F4。
- 范围（主 Agent 13:21 更正）：只改 run_nightly_v1.py 与 routine_fallback_v1.py，加自测 / diff / 回执 / 本说明。例程草稿（含 2a 和 94322 那句措辞）本次未动，由 Eng 负责。

## 0. 文件与 sha

| 项 | sha256 |
|---|---|
| run_nightly_v1.py v3.1（已安装） | f99dd11aa26f611aca382f98b00ea14fdbcafc99960c8259102e421f02281b0a |
| routine_fallback_v1.py v3.1（已安装） | 559d1e017b1c53b1dd1cdffdc0571fc1d33a6157ea4437735421cc3fab271384 |
| 旧版归档 _recovery/data/nightly_20261019/prev31_20261018T131600/（chmod 444 + SHA256SUMS） | 63b5a884…（驱动） / f3244472…（兜底） |
| DRIVER_DIFF_vs_63b5a884_20261018T133614.diff（419 行） | 403723b9eec15824cdfc88b162c9edfab77b9a86bfd1c8f03a870608be94da44 |
| FALLBACK_DIFF_vs_f3244472_20261018T133614.diff（302 行） | 4181421191641687d1e2def9c015a70358e365746d025bba188074bdc8abde8a |
| TEST_RECEIPT_v31_20261018T133614.json（30/30 PASS，13:33:13–13:35:56 ET） | 2e476adf35b7b6f0392495d4c6f274d989f2ef4b347f1e225ae4eea23c06c791 |
| selftest_v31_tdrv6.py / selftest_v31_thang3.py | cc602684… / 5fa3ff31… |

驱动内 sha_routine_fallback 钉值已改为 559d1e01…（L76）。.ok 的 sha_driver 与 sha_routine_fallback 需按上表新值签。

## 1. 逐条修复与行号（行号均指已安装的 v3.1）

| 编号 | 修法 | 行号 |
|---|---|---|
| P1-1 | 兜底：只有存在 run_<STAMP> 目录且 STAMP（ET）晚于 .ok issued_at，才代写 FAILED；否则退出 7 no_run_evidence，只报不写 | fallback L134–145、L250–268、L274–275 |
| P1-2 | 兜底 pgrep 三条锚定、括号转义模式（加 scripts/acquire/*.py 与 import tier1_materialize）；94322 / 94403 只按确切 PID、cmdline 核对、且 /proc/<pid>/stat 为 T 时排除 | fallback L26–29、L103–123 |
| P1-3 | guarded_check：GUARDED 为 T 时，用 descendants() 枚举整棵树，每个后代须为 T / Z / 不存在，否则前置失败，明细记 R.checks.guarded；relay_outage_backfill 进程同样核树。永不发信号 | 驱动 L413–443 |
| P2-1 | 收尾 sha 不符：先 compare_restore(final)，恢复成功退出 1，失败退出 4；reason_code FINAL_CAL_MISMATCH | 驱动 L1463–1468 |
| P2-2 | call A / call B 只要有 PPID=1 logged_only 孤儿：fail + reason_code ORPHAN（仍不发信号）；call A 的 dirty 也计入孤儿 | 驱动 L537–538、L1382 |
| P2-4 | (a) 本日已有 exit 5 或 restore.ok=false 的兜底回执 → 退出 5 不动手；(b) DONE 已在而 sha 不符 → 只报 P0 不恢复 | fallback L148–157、L217–221、L232–234 |
| P3-1 | docstring 改为「SOURCE 默认不设，只有 .ok source_relay_only=true 才设」 | 驱动 L15 |
| P3-2 | reason_codes 统一经 add_code 去重并记 reason_code_counts；residual 按 pid 去重并记 residual_raw_count | 驱动 L161–166、L532–536 |
| P3-4 | FROZEN 加 sw_l1_pit 89d4afa3 / 87d769aa、sw_pit 0b1d3432（实测 sha 与 Arch 第 6 节钉值一致），cal_shas 前后核对覆盖；closure 仍为第一项（.ok pin_frozen_closure 取第一项） | 驱动 L43–46 |
| 隔离报 P1 | quarantine 每移走一份不合格文件即 alert P1（门槛不变：rows < 0.98 × 同接口上一开市日，0 行同样命中；10-19 的上一开市日就是 10-16） | 驱动 L1079、L1046–1047 |

未在本次范围、保留原状：P3-3、P3-5～P3-8（行级审已记录在案或可接受）。

## 2. 两个新 .ok 键（主 Agent 13:19；Eng 13:24 契约）

- 键：allow_relay_partial_20261019、allow_hsgt_source_empty_warn_20261019。缺省 = false；值只能是小写 true / false，其他写法拒签 .ok（L793–797；T24）。
- 改动点与 Eng 行号（63b5a884）核对一致：check_summary L564–568 → v3.1 L591–598；check_hsgt_log L601–610 → v3.1 L658–683；最终判定 L1330–1335（post_checks）→ v3.1 L1474 起；skipped→fail 分支 L1029–1033 → v3.1 L1131–1137 + L1150–1172。
- 只有 call B 的 cyq / tier3 / hsgt 可以降级：
  - allow_relay_partial=true：summary 里这三步 status=partial（rc=3 或 RELAY_DOWN 快速失败）→ WARN。reason：summary 带 skipped 记 skipped，否则记 relay_partial（L622–628）。
  - allow_hsgt_source_empty_warn=true：hsgt 日志 CHUNK DONE 里 fail=0、无 ABORT、auth_max ≥ 20250601，且 remaining 等于本次 call B 窗口内写出的 0 行 hsgt_top10/<d>.parquet 个数 → WARN，reason=hsgt_source_empty，每个空日一条（L669–683、L685–696）。依据：fill_hsgt_top10_extend.py save_day（L51–63）只有 pull 成功（HTTP 200）后才写；needs() 用 700 字节门槛（L46），所以 0 行文件仍计入 remaining（L217）。fail>0、ABORT、数目不符 → 照旧 FAILED（T26）。
  - 其他任何步骤 partial / skipped → 照旧 FAILED，与键无关（T25：events skipped、daily_basic partial 在键为 true 时仍失败）。
- F1：marker 顶层 warnings 恒在（无则 []），元素只有 {step, date, actual_rows(int), reason}（L1120）。
- F2：marker 顶层 ok_flags = {allow_relay_partial_20261019: bool, allow_hsgt_source_empty_warn_20261019: bool}，JSON 布尔（L1121）。
- F3：不放宽 rc：call B rc≠0 照旧 FAILED（L1437、L1469；T23c）。
- F4：marker 的 steps 改为列表 steps[]，每项带 step 与 kind（raw_file / calendar / required_table / call_b_step）。降级步骤 status=WARN，只有这些项和 warnings[].reason 可以出现 skipped；白名单之外出现 skipped → DONE 降为 FAILED，并把白名单之外的 skipped 改写为 not_run（L1131–1137、L1150–1172；T27）。顶层 status 仍是 OK。
  - 说明：63b5a884 的 marker steps 是以 api 为键的 dict；为满足契约 F4 的 steps[] 写法改成了列表，原有字段全部保留，只多了 step / kind。若 Eng 的 2a 期望原 dict 形状，需要对齐。
- 降级日期追加到 output/data_gap_list/nightly_degraded_gaps.jsonl（O_APPEND + fsync，每条一行，带 run / recorded_et；L47、L1236–1248），DONE / FAILED 都会写。没有写进 output/relay_outage_backfill_queue.json：那个文件由 nightly_update register_backfill 整份重写（nightly_update.py L86–95），94403 的 relay_outage_backfill 也读它，驱动不去并发改写。cyq / tier3 / hsgt 被 RELAY_DOWN 快速失败时，nightly_update 自己已经登记进这个队列。
- REQUIRED 6 表不全：照旧 FAILED，与两个键无关（post_checks；T28）。

## 3. 自测 T01–T28（30 项，全部通过）

T01–T19 照旧重跑通过（T19 的兜底 .ok 补了 issued_at，以满足 P1-1）。新增：
- T20：没有 run_* 目录 → 退出 7，不写 marker；只有早于 issued_at 的 run_* → 7；有晚于 issued_at 的 run_* → 写 FAILED，退出 1。
- T21：驱动与 nightly 不在、只剩一个 PPID=1 的 scripts/acquire/tier3_daily_snapshot.py → 退出 6；94322 替身（--test-guarded，cmdline 为 scripts/acquire/remaining_after_stk_surv.py）为 S → 6，为 T → 按确切 PID 排除并代写 FAILED（1）。
- T22：GUARDED 替身为 T、子进程为 S → 前置失败（P1-3）；子进程也 T → 通过。
- T23a：call B 后出现 PPID=1 孤儿 → FAILED，含 ORPHAN。T23b：收尾前假日历被改 → 先恢复（sha 回到假 PIN）再 FAILED 退出 1，含 FINAL_CAL_MISMATCH、无 P0。T23c：call B rc=1、summary 全 ok → FAILED（F3）。
- T24：两个键缺省 / true / false 可签；True / 1 / yes 拒签。
- T25：relay_partial 键 true / false；非白名单步骤 skipped 照旧失败。
- T26：hsgt 源端空日键 true / false；fail>0、ABORT、数目不符照旧失败。
- T27：marker F1 / F2 / F4（warnings、ok_flags、steps[] 的 WARN 项可带 skipped；非白名单步骤带 skipped → FAILED 并改写）。
- T28：两个键都为 true，REQUIRED 6 表不全 → FAILED。

## 4. 写路径变化（对 13:02 版写路径清单的增量）

- 新增一条：output/data_gap_list/nightly_degraded_gaps.jsonl（只追加）。
- 兜底新增：不写任何新路径；exit 7 只写回执（docs/v2/audit/nightly_20261019/routine_fallback_receipt_*.json，O_EXCL + os.link）。
- rg -i fund_portfolio 对两份 v3.1 文件零命中；整条 nightly 链仍不碰 fund_portfolio_dh 及其临时文件。

## 5. 6 张 REQUIRED 表的实际来源（10-15 / 10-16）与 10-19 走向

证据来源：原始日文件的 parquet schema 元数据 PANDAS_ATTRS（tier1_pull.pull L50 与 tushare_relay_pull.pull L57 都把 df.attrs.source 写进去）；nightly 日志本身不打印来源。

| 表 | 上游 | 10-15 / 10-16 实际来源（证据） | 10-19、source_relay_only=false 时 |
|---|---|---|---|
| daily_ohlcv_raw_pit | daily_pull → tushare_raw/daily 等 → materialize_bars（本地） | datahub（tushare_raw/{daily,adj_factor,stk_limit,suspend_d}/2026101[56].parquet 均为 source=datahub） | tier1_pull _call preferred=datahub（L17–31、L113），SOURCE 不设 = auto：先 datahub，失败再 relay |
| daily_basic | daily_pull → tushare_raw/daily_basic → materialize_daily_basic（本地） | datahub（daily_basic/2026101[56].parquet source=datahub） | 同上，datahub 优先（L125） |
| asof_ts | daily_pull（tier1 extend 生成）→ eng_daily_panels asof_ts 只校验并刷新 manifest | datahub（与 daily 同源；eng_panels 日志 L6 注明由 tier1 extend 生成） | 同上 |
| etf_daily_adj | etf_daily_adj_incr.py → data/v2/etf/raw/{fund_daily,fund_adj}/<d>.parquet | relay（data/v2/etf/raw/fund_daily 与 fund_adj 的 2026101[56].parquet 均为 source=relay） | tushare_relay_pull preferred=relay（etf_daily_adj_incr.py L25–27；tushare_relay_pull.py L14–25）：先 relay，失败再 datahub |
| etf510300 | eng_daily_panels etf510300 → pull(fund_daily / fund_adj, ts_code=510300.SH) | 未落盘记录（fund_daily_tushare_510300.parquet 无 PANDAS_ATTRS；日志不打印来源）。只能按代码判断：relay 优先 | relay 优先、datahub 兜底（eng_daily_panels.py L26–28、L35–36） |
| mid_large_universe | mid_large_universe_incr.py | 不发网络请求（只读本地 parquet，文件内无 tushare_proxy / relay 引用） | 同左 |

注意：
- 上表 tushare_raw 与 etf/raw 的 10-15 / 10-16 文件 mtime 都是 2026-10-18 01:14:20–01:14:22 ET，晚于 nightly 日志时间（10-16 daily_pull 在 00:19 写），而且两天同一秒。说明现存文件在 01:14 被整批改写或复制过，attrs 证明的是现存文件的来源，不一定就是当夜 nightly 写出的那一份。这一点我没有追到具体原因，列为未闭合项。
- relay 优先的两步（etf_daily_adj、etf510300）在 TSPRO_RELAY_TIMEOUT=115 下，relay 卡住时每次请求最长 115 秒才回落 datahub。延迟证据：12:57 ET 探针 stock_basic limit=100 HTTP 200 用时 25.51s、trade_cal 15.51s ReadTimeout（PROBE_1250_RECEIPT_20261018_125839.md，99f3dc9e…）；13:18 ET probe4 stock_basic limit=5000 HTTP 200 5000 行用时 83.55s、trade_cal 15.51s ReadTimeout、index_member_all 200 / 5 行 / 5.0s（probe_log.csv）。call B 的 75 分钟预算须覆盖这一风险。

## 6. 已知缺口（v3.1 新增部分）

1. 兜底读 issued_at 用的是驱动 .ok（默认 output/ai_factory/ARCH_RUN_AUTH_DATA_NIGHTLY_20261019.ok）。如果 Arch 在驱动跑完后把 .ok 移进 _consumed/，兜底读不到 issued_at，会退出 7（安全方向：不写 FAILED），需要人工判。
2. 兜底 exit 7 时如果日历 sha 不符且有 PIN 备份，仍会恢复日历（只从 run_*/ 下 sha==PIN 的备份恢复），回执记 restore；退出码优先级 5 > 1 > 7 > 3 > 0。
3. hsgt 源端空日的证据是本次窗口内写出的 0 行文件，加上日志 last=<d>:ok:0 一并记进回执（log_ok0）。日志每 5 天或最后一天才打印一行，所以不把日志当唯一证据。
4. GAP_LIST 是新路径，Eng / 主 Agent 若已有指定的缺口清单位置，需告知后改钉。
5. 本次未处理 P3-3（compare_restore 树还在时误报退出 4）。
