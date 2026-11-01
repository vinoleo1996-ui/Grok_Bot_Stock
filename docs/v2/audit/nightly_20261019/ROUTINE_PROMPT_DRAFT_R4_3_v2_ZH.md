# 10-19 日更例程提示词草稿（05:30 ET 驱动版 v3；Data 起草，按 Arch 设计审查 2dada5ed 全 17 项修订，待 Arch 终审）

- 作者：QuantLab Data；修订 2026-10-18 13:02 ET（原地修改；上一版 1d372ced… 已归档 _recovery/data/nightly_20261019/predraft2_20261018T114300/）。
- 驱动：docs/v2/audit/nightly_20261019/run_nightly_v1.py（f99dd11aa26f611aca382f98b00ea14fdbcafc99960c8259102e421f02281b0a）；兜底：docs/v2/audit/nightly_20261019/routine_fallback_v1.py（559d1e017b1c53b1dd1cdffdc0571fc1d33a6157ea4437735421cc3fab271384）；恢复脚本 cal_restore_v2.py（6686876b…）、比对 cal_compare_v1.py（74093ff3…）。
- 对照的现行例程：ROUTINE_A_CURRENT_20261018.txt（a95cda62…）；逐节 diff 见 ROUTINE_DIFF_ZH.md。
- 档位：strict（默认）与 relaxed **同一时间盒**（Arch 第 1 项）：daily_pull 单次 30 分钟硬停；call B 预算 75 分钟（主 Agent 12:32），起跑闸门 起跑 + 75 ≤ 16:00，在 min(起跑 + 75, 16:00) 硬停并判 FAILED；绝不跨 16:40。不再有 06:20 / 06:30。两档唯一区别：relaxed（需 .ok allow_profile_relaxed_20261019=true）允许 MAX_RUN 后最多重试 allow_daily_pull_retry_20261019 次。
- live=false，promotion_approved=false；不启动 8787；不碰 moneyflow。

---

## 例程正文（复制给调度器的部分）

A股收盘后日更（研究级，live/promotion 保持 false，不启动 8787，不碰 moneyflow）。今天 2026-10-19（周一），05:30 ET 开始。

### 一、启动前检查（只读；**本例程不对任何进程发信号**）
1. 94322（remaining_after_stk_surv.py）与 94403（relay_outage_backfill.py）：只读 /proc/<pid>/stat。state=T（暂停）或已退出（文件不存在 / Z / PID 已被别的程序复用）才可继续；S / R / D 一律不跑，priority=true 报主 Agent 与 Arch。**不要对 94322 或 94403 发 SIGCONT 或任何信号**（主 Agent 12:32 第 4 条；旧文的 94322 SIGCONT 一节已删除；原 05:00 的 94403 CONT 例程已删除）。驱动会再按 cmdline 查一遍全部 relay_outage_backfill.py 进程（T 或不存在才继续），并且绝不给它们发信号。已知事实：94403 已于 2026-10-18 04:59:31 ET 自行退出（docs/v2/audit/data_cs_panel_v3_dryrun/cont_94403_20261018.md）。
2. 下面两条 pgrep 都必须为空（只读）：
```
pgrep -af "(^|[ /])([k]line|[e]xport_static|[s]napshot|[g]en)\.py( |$)"
pgrep -af "(^|[ /])([n]ightly_update|[t]ier1_pull|[r]un_backfill_[a-z0-9_]+)\.py( |$)"
```
（94322 若为 T，会出现在第二类的 remaining_after_stk_surv 匹配里，驱动按“T 允许”处理；本例程只看上面两条。）
3. ET 日期必须是 2026-10-19 且不早于 05:25（驱动也核）。

### 二、记录开始时间、选档、只读预检
1. `date "+%Y-%m-%dT%H:%M:%S%z"` 记为 S。S 晚于 06:06 ET 先发 priority=true 给主 Agent（例程晚开），照常继续。
2. 读 output/ai_factory/ARCH_RUN_AUTH_DATA_NIGHTLY_20261019.ok（不存在：不跑，报主 Agent 与 Arch）。其中 allow_profile_relaxed_20261019=true 才加 `--profile relaxed`，否则默认 strict。
3. 只读预检（不建锁、不写文件、不消耗 .ok）：
```
cd /workspace/QuantLab
PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 docs/v2/audit/nightly_20261019/run_nightly_v1.py --date 20261019 [--profile relaxed] --check-only </dev/null
```
**预检通过的退出码是 10**；其他退出码：照实报主 Agent 与 Arch，不跑正式命令。

### 三、正式运行（单条前台命令，不加 &）
```
PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 docs/v2/audit/nightly_20261019/run_nightly_v1.py --date 20261019 [--profile relaxed] </dev/null
```
| 闸门 | strict（默认） | relaxed（.ok 授权） |
|---|---|---|
| daily_pull 单次硬停 | 30 分钟 | 30 分钟 |
| daily_pull 重试 | 无 | 仅 reason_code=MAX_RUN，≤ allow_daily_pull_retry_20261019（最多 2）次，间隔 30 分钟，须满足 Arch Q-A3 (a)–(f)，重试前完整 quiet 复核 |
| call B 起跑闸门 | 起跑 + 75 ≤ 16:00，trade_cal == 141078fa，锁 sha 未变，.ok 未过期 | 同左 |
| call B 超时 | 在 min(起跑 + 75, 16:00) 按停树顺序停，FAILED（CALLB_TIMEOUT），恢复并双核日历 | 同左 |
| cyq / tier3 / hsgt 的 partial（summary status=partial；reason 记 relay_partial，summary 带 skipped 的记 skipped） | .ok allow_relay_partial_20261019=true → WARN；false（缺省）→ FAILED | 同左 |
| hsgt 源端空日（reason=hsgt_source_empty：本次日志 CHUNK DONE fail=0、无 ABORT、auth_max ≥ 20250601，且 remaining = 本次 call B 窗口内写出的 0 行 hsgt_top10/<d>.parquet 个数）；hsgt 其他 rc=2 / remaining>0 情形 | 源端空日：.ok allow_hsgt_source_empty_warn_20261019=true → WARN，false（缺省）→ FAILED；其他情形一律 FAILED | 同左 |
| 判 WARN 时的写法 | marker 顶层 status=OK；steps[] 中对应项 status=WARN（带 warn_reason）；warnings[] 每条 {step, date, actual_rows, reason}；降级日期只追加（O_APPEND）到 output/data_gap_list/nightly_degraded_gaps.jsonl，一行一条 | 同左 |
| 不可降级（与两键无关） | call B rc≠0 → FAILED；REQUIRED 6 张表任一张不全（last_date≠20261019 或 rows 少于跑前）→ FAILED；cyq / tier3 / hsgt 以外的步骤 partial / skipped → FAILED | 同左 |
| RSS | 树合计 ≥ 1484800 kB 或单进程 > 1536000 kB 即停树，FAILED（RSS，不可重试） | 同左 |
| 16:40 | 任何调用到点即停树，FAILED（BLACKOUT） | 同左 |

驱动自动做的事（你只看输出与退出码）：
1. marker 预检（只读）：DONE 已存在 → 退出 2，什么都不写；FAILED 已存在 → 只有 .ok supersede_failed_marker_sha256 等于其全长 sha256 才继续（否则退出 2、什么都不写）。
2. 严格解析 .ok（ASCII、LF、key=value、无行内注释、无重复键 / 未知键、全文无 DRAFT、路径不含 /_consumed/；不移动不删除 .ok，记全长 sha）；核全部钉 sha（Arch §6，含 tier1_pull 5b70dfed、tushare_proxy ae91f230、11 个步骤脚本、routine_fallback_v1）、解释器 /usr/bin/python3、ET 日期 = D 且 ≥ 05:25、不在 16:40–18:40、94322 / 94403 / relay_outage_backfill 为 T 或已退出、两条 pgrep 为空。
3. RESEARCH_QUIET.lock：Arch 05:25 设；内容核 purpose=nightly_20261019、set_at 日期为 D；05:28 后仍无且 .ok 允许才按 Arch 模板代设；**驱动绝不删除或移动锁**；healthz quiet + 15 秒 + pgrep；call B 前复核且锁 sha 必须与 call A 前相同。
4. 备份 trade_cal（两份 sha 都是 141078fa，chmod 444）；核 PIN 日历里 20261019 为开市日；PIT 日历与冻结 closure sha 跑前跑后都核；快照 v2 BEFORE。
5. call A：`/usr/bin/python3 scripts/nightly_update.py --date 20261019 --steps daily_pull`，子进程恒设 TSPRO_RELAY_TIMEOUT=115、TIER1_SKIP_CAL_REFRESH=1（SOURCE=relay 只在 .ok source_relay_only=true 时设，默认不设）；查 call A 日志本次段落里有 `cal refresh skipped (TIER1_SKIP_CAL_REFRESH=1)`（没有记 P1 异常，恢复链照做）。
6. 停树顺序（Arch 第 2 项）：核 cmdline + PPID 后 SIGSTOP nightly → 重新枚举 → 冻结全部后代 → 从最深一层起 TERM + CONT → 等 10 秒 → KILL → 最后 KILL nightly → wait（60 秒超时）→ 孤儿扫描（PPID=1 的可疑孤儿挡住 DONE：判 FAILED，reason_codes 含 ORPHAN；驱动不对孤儿发任何信号）。任何拒发 / 杀不掉 → 残留 → 不重试、不起 call B、FAILED。
7. 每次尝试后、call B 后、收尾与异常路径：先确认进程树已不在 → post 副本 → cal_compare_v1 → cal_restore_v2（rc=2 复跑一次；失败或超时走驱动自带原子恢复）→ 间隔 30 秒两次核 sha == 141078fa；否则 P0、退出 4。
8. 原始文件判据（实测，非硬编码）：daily / daily_basic / adj_factor / stk_limit 的 20261019.parquet 行数 ≥ 上一开市日 0.98 倍，daily_basic ≥ daily 0.98 倍，trade_date 实测 min=max=20261019；*.tmp.parquet 残留即不合格；凭 .ok 同盘隔离。
9. call B 14 步（不含 daily_pull、trade_cal、sw）：index_pull,adj_factor,bars,daily_basic,index,etf_daily_adj,eng_panels,mid_large_universe,events,hsgt,cyq,tier3,bundle,freshness。
10. 核查只认本次 call B 写入：summary（logs/nightly/20261019_summary.json）顶层 finished 与 mtime 在 call B 窗口内、各步 status=ok 且无 skipped，例外：.ok allow_relay_partial_20261019=true 时 cyq / tier3 / hsgt 的 partial（含 skipped）记 WARN（驱动 L596–597、L622–627），其他 step 出现 partial / skipped 才判 FAILED；hsgt 本次日志须有 remaining=0 的 CHUNK DONE，例外：hsgt 已按 relay_partial 记 WARN 时不查日志（L661–663），或 .ok allow_hsgt_source_empty_warn_20261019=true 且符合源端空日条件时记 WARN（L670–681）；daily_update_status finished_at 晚于 call B 起跑、status=ok、target_trade_date 与 REQUIRED_TABLES last_date 统一成 YYYYMMDD 后 == 20261019、rows 不少于跑前；freshness generated_at 晚于 call B 起跑且 overall=ok；快照 AFTER + compare 退出 0。
11. 先写回执 docs/v2/audit/nightly_20261019/driver_receipt_<时间>.json，**最后写唯一 marker**（DONE 或 FAILED，含 reason_codes），然后退出。任何异常 / 信号 / 子工具超时都走同一收尾：停树 → 恢复并双核日历 → 回执 → 唯一 FAILED → 退出 11。
12. 起跑前（05:30 ET）间隔 15 秒连读 3 次 /proc/meminfo，MemAvailable 须每次都 ≥ 2621440 kB；任一次不达标即不起驱动、不硬跑、不向 94322 / 94403 发任何信号，回执记三次读数、94322 的 State/VmRSS 与 ps 快照，按『未起跑 = P1、无 marker、paper 阻塞』上报（兜底此时会退出 7，不代写 FAILED）；达标才起驱动，并在回执附 driver 回执中各次调用的 rss_max_sum_kb / rss_max_one_kb。

缺口文件与 call B 重跑：如果 call B 真的重跑了，Data 回执里要写明前一次运行追加到 output/data_gap_list/nightly_degraded_gaps.jsonl 的是哪几行（行号 + 该行内容）。该文件只追加、不删改，驱动不读它；当天的旧行照常放行、不挡本次运行，报 P1（对应 Eng r4.5 的「照常跑、报 P1」）。

### 四、按退出码处理
| 退出码 | 含义 | 你要做的 |
|---|---|---|
| 0 | DONE（OK） | 见第六节报告 |
| 1 | FAILED（marker 已写，含 reason_codes） | priority=true 给主 Agent 与 Arch：reason_codes、fail_reasons、alerts、隔离清单、日历 sha |
| 2 | 前置条件失败（多数情况写了唯一 FAILED；因已有 marker / 未建锁前被拒则什么都没写） | priority=true，附原因；不自行重跑；18:40 后重跑需新 .ok |
| 3 | marker 写入失败 | P0，priority=true；跑第五节兜底 |
| 4 | 纸面日历未恢复到 141078fa | P0，立即 priority=true；不做任何其他写入；跑第五节兜底 |
| 10 | 只读预检通过（仅 --check-only） | 进入第三节正式运行 |
| 11 | 统一异常收尾（信号 / 异常 / 子工具超时），FAILED 已写 | priority=true，附 reason_codes（SIGNAL / EXCEPTION / TOOL_TIMEOUT） |
| 137 / -9 等（被 SIGKILL / OOM） | 驱动没来得及收尾 | 立即跑第五节兜底 |

需要中止驱动时：只对驱动的确切 PID 发 **TERM**（核 cmdline 含 run_nightly_v1.py），然后至少等 90 秒让它自己停树、恢复日历、写 FAILED；不要发 KILL，不要碰它的子进程。

### 五、20 分钟兜底检查（Arch 第 9 项；主 Agent 12:32 第 3 条）
驱动命令结束后（任何退出码，尤其 3、4、137）且最迟在驱动结束后 20 分钟内，跑一次（只读检查；必要时原子恢复日历、代写 FAILED；不发任何信号、不删任何文件）：
```
nice -n 10 /usr/bin/python3 docs/v2/audit/nightly_20261019/routine_fallback_v1.py --date 20261019
```
| 退出码 | 含义 | 你要做的 |
|---|---|---|
| 优先级（多种情况同时发生时） | 判定顺序（fallback L217–226、L269–279）：① 当天已有失败的兜底回执 → 5（拒绝执行，最先判，什么都不做）；② pgrep 有拦截对象 → 6（什么都不做）；③ 其余情况做完恢复 / 代写后，按结束时状态只取一个：日历仍不是 PIN → 5 > 本次已代写 FAILED → 1 > 无起跑证据 → 7 > 本次恢复日历成功 → 3 > 0。例：已代写 FAILED 但日历仍不是 PIN → 返回 5（回执 marker_written 里记着已写的 FAILED） | 按返回的退出码处理；遇到 5 时同时看回执的 marker_written 与 restore，已代写的 FAILED 一并报 |
| 0 | 日历 == PIN，marker 已存在，本次没有恢复也没有代写，无需动作（竞态见下方「0 / 3（竞态）」行） | 核对磁盘上确有 DONE 或 FAILED marker，按 marker 处理；无其他动作 |
| 1 | 没有 DONE / FAILED，且存在 STAMP 晚于驱动 .ok issued_at 的 run_<STAMP> 目录（驱动起跑过的证据），兜底已代写唯一 FAILED（writer=routine_fallback，reason=driver_killed），结束时日历 == PIN（fallback L250–264、L272–273） | priority=true 给主 Agent 与 Arch |
| 3 | marker 已存在，但日历不是 PIN，兜底已原子恢复到 141078fa 并核过 | priority=true 给主 Agent 与 Arch（说明驱动收尾时日历异常） |
| 5 | 结束时日历 sha 仍不是 141078fa（无 sha==PIN 的备份，或 .ok 未授权 allow_routine_fallback_restore_20261019）；按优先级，即使本次已代写 FAILED 也返回 5（fallback L236–248、L269–271） | **P1**，立即 priority=true 给主 Agent 与 Arch |
| 5（DONE 在而 sha 不符） | DONE 已存在但日历 sha 不是 PIN：兜底不恢复日历，只报 P0（fallback L231–234；回执 restore.why 写明） | **P0**；不重跑，priority=true 报主 Agent 与 Arch |
| 5（拒绝执行） | 当天已有失败的兜底回执（其中 exit=5 或 restore.ok=false），兜底拒绝执行，什么都不做；回执 action=refused_prior_failed_receipt（与上一行同为 5，靠回执区分） | 只报告：priority=true 给主 Agent 与 Arch；不重试，不再跑兜底 |
| 6 | 三条 pgrep 模式（原文见表下）任一命中仍在的进程：run_nightly_v1 / nightly_update / tier1_pull、任意 scripts/acquire/*.py、import tier1_materialize；什么都没做，**不写回执**。排除：兜底自身 PID；已退出或 state=Z 的进程；94322（cmdline 含 remaining_after_stk_surv.py）/ 94403（cmdline 含 relay_outage_backfill.py）只在是这个确切 PID、cmdline 核对一致且 /proc/<pid>/stat 为 T 时排除，S / R / D 照样拦（fallback L26–29、L103–123、L222–226） | 不要发信号。兜底不写回执，例程自己留证：当时的 `date`、`ps -eo pid,ppid,stat,lstart,cmd` 中命中的行、各命中 PID 的 /proc/<pid>/stat；5 分钟后再跑一次，仍为 6 则 priority=true 报主 Agent 与 Arch 并附证据 |
| 7 | 没有 marker，且没有比驱动 .ok issued_at 更新的 run_<STAMP> 目录（没有证据表明驱动启动过）；不写 FAILED。若日历不是 PIN 而有 sha==PIN 的备份且 .ok 已授权，兜底会先原子恢复日历，再返回 7（fallback L231–248、L250–268、L274–275） | 核对 data/v2/tushare_raw/trade_cal.parquet 的 sha256 == 141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086，不等就报 P0；不论是否等于 PIN，都不重跑、不补写 marker；priority=true 报主 Agent 与 Arch，交人工判断 |
| 0 / 3（竞态） | 检查时还没有 marker，写 FAILED 时发现已有人写出（FileExistsError，回执 marker_written.error=「已存在，不写第二份」）：不写第二份，按是否恢复过日历返回 0 或 3（fallback L260–264、L276–279） | 以磁盘上实际存在的 marker（output/nightly_markers/nightly_20261019.DONE.json 或 .FAILED.json）为准判定，不以退出码为准 |
| 2 | 参数错误 | 报 Data |

exit 6 的 pgrep 模式（routine_fallback_v1.py L26–28 原文；兜底对每条执行 `pgrep -af <模式>`）：
```
(^|[ /])([r]un_nightly_v1|[n]ightly_update|[t]ier1_pull)\.py( |$)
(^|[ /])[s]cripts/acquire/[A-Za-z0-9_]+\.py( |$)
[i]mport tier1_materialize
```

### 六、回执与报告（沿用现行例程第 7 步与报告规则）
1. Data 回执（docs/v2/audit/nightly_20261019/ 下新文件）：两条命令与 rc、备份 / 恢复 sha、比对结果、快照结果、reason_codes，以及每一步按实际行数 / 日期范围判定（不以 summary 状态为准）；驱动 marker 已给 daily / daily_basic / adj_factor / stk_limit / trade_cal 与 REQUIRED_TABLES；其余步骤由你只读各自产物 / manifest / 日志补齐。兜底若跑过，附 routine_fallback_receipt_<时间>.json。回执还须做三件事（Arch 审查 bf0b4ac2 §九 9.4）：(1) 用 pyarrow.parquet.read_schema 只读 schema 元数据、不读行数据，逐个列出以下 7 个文件 PANDAS_ATTRS 里的 source：data/v2/tushare_raw/{daily,daily_basic,adj_factor,stk_limit,suspend_d}/20261019.parquet（对应 daily_ohlcv_raw_pit、daily_basic、asof_ts）与 data/v2/etf/raw/{fund_daily,fund_adj}/20261019.parquet（对应 etf_daily_adj）；(2) etf510300 披露为「来源未记录（先 relay，失败时回退 datahub）」，mid_large_universe 披露为本地构建、没有网络来源；(3) 附上驱动回执里的 checks.env_knobs_inherited.SOURCE（驱动 L1290，未设时为 null）。只在三种情况下用 priority=true 报 P1 给主 Agent 与 Arch：SOURCE 不是 null；某个 source 既不是 datahub 也不是 relay；7 个文件里有缺 PANDAS_ATTRS 的。除此之外只披露，不报 P1。
2. 有新交易日数据落地：给 Leo 中文简报。
3. Eng：完成通知 priority=false（marker 路径与 sha）。
4. 回执路径 + sha 发给 Arch 与主 Agent；若驱动代设了锁，回执与 TEAM_STATE 写明。
5. 若 call B 的 reason_code 为 RSS（驱动 L515–516 已单独输出，与 MAX_RUN、BLACKOUT、HANG 分开），按 P2 上报：不重试、不写 DONE，待 trade_cal 还原后复核 sha 141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086，纸面轨被门禁拦住属预期（主 Agent 10-18 16:27 选方案 A）。

### 七、不变的约束
10-19 之后继续跳过 sw 与 trade_cal 步骤，直到主 Agent 与 Arch 同意。MemAvailable < 2GB 等待（nightly 内置，驱动的时间盒照样计时）。不用 heredoc。只停自己起的确切 PID；不 pkill / killall；不加 --force；不删文件；本例程不给 94322 / 94403 发任何信号；94322 的 STOP 由 04:25 例程用 dc827675 执行，本例程只核状态；16:40–18:40 ET 不跑任何东西。

## R4 变更
- 写于 2026-10-18T13:52:09-0400（取自 date）；作者 QuantLab Data。R4 以 ROUTINE_PROMPT_DRAFT_R3_ZH.md（cb48de7b1c2a43a9b8c5810cf70a61a2184700fd7bc8091ec9f5379d0216ae02）为基础；R3、R2（a5ef41b2754440447ed369d7c8ca26166a27983827eeed04a522041dbf9727a6）与原稿 ROUTINE_PROMPT_DRAFT_ZH.md（02498e1e478f23d4f8060e38e6ae533678f91ad66e1ac9a0f78f1d15c7e2eb41）都未动；本文件是新文件。驱动 f99dd11a… 与兜底 559d1e01… 只读核对，未改。
- 文头标题「驱动版 v3」与「修订 13:02 ET」说明三轮都未改。下列行号均指本文件（R4）。

R2（2026-10-18T13:41:50-0400）：
1. 第七节：「不给 94322 / 94403 发任何信号」改为「本例程不给 94322 / 94403 发任何信号；94322 的 STOP 由 04:25 例程用 dc827675 执行，本例程只核状态」（与 Eng 纸面例程 r3 3232fa6b 的 1b 措辞一致）。
2. 驱动 sha：63b5a88462f9f75ae7975f52320bbd6f88433cdf4857bf95c6de557d6d880e16 → f99dd11aa26f611aca382f98b00ea14fdbcafc99960c8259102e421f02281b0a（L4，全长完整匹配）。
3. 兜底 sha：f3244472da360b74cc692f90548fab4f8839f13f3938bf65374d592b2d61ac5f → 559d1e017b1c53b1dd1cdffdc0571fc1d33a6157ea4437735421cc3fab271384（L4，全长完整匹配）。

R3（2026-10-18T13:47:57-0400，按 Arch 13:45）：
4. 第三节判定表（L45–48）：cyq / tier3 / hsgt 的 partial 按对应 .ok 键判 WARN 或 FAILED；allow_relay_partial_20261019 管 relay_partial 与 skipped（驱动 L596–597、L622–627），allow_hsgt_source_empty_warn_20261019 只管 hsgt_source_empty（L670–681）；WARN 时 marker 顶层 status=OK、steps[] 对应项 status=WARN、warnings[] 有记录、降级日期只追加到 output/data_gap_list/nightly_degraded_gaps.jsonl（L1108–1121、L1236–1248）；call B rc≠0 与 REQUIRED 6 表不全一律 FAILED（L1437–1438、L1469–1471、L1496–1501）。Arch 原给的 63b5a884 行号按 9fda0202 第 2 节对应到 v3.1。补充：只要有 warnings 就追加 GAP_LIST，与最终 DONE / FAILED 无关（L1236）。
5. 第五节兜底退出码表：新增「5（拒绝执行）」行与 exit 7 行（fallback L7、L148–157、L217–221；L13–14、L250–268、L274–275）。
6. 第三节驱动第 6 步（L58）：孤儿扫描改为「PPID=1 的可疑孤儿挡住 DONE：判 FAILED，reason_codes 含 ORPHAN；驱动不对孤儿发任何信号」（驱动 L23、L385–390、L537–538、L1382）。
7. 删去 R2 变更里「以下几处描述的仍是 v3 行为」那句注。

R4（按 Arch 13:49，把 R3 列出的 a–e 写进第五节正文）：
8. 第三节第 11 条之后新增一段（L65）：call B 若真的重跑，回执写明前一次追加到 nightly_degraded_gaps.jsonl 的行号与内容；当天旧行照常放行、报 P1（对应 Eng r4.4）。驱动只追加、不读该文件（驱动 L1236–1248）。
9. a：表首新增「优先级」行（L88）：先判当天失败回执 → 5，再判 pgrep → 6，其余按结束时状态 5 > 1 > 7 > 3 > 0 取一个；已代写 FAILED 但日历仍不是 PIN 返回 5（fallback L217–226、L269–279）。exit 1 行（L90）补上起跑证据条件和「结束时日历 == PIN」；exit 5 行（L92）补上「即使已代写 FAILED 也返回 5」。
10. b：新增「5（DONE 在而 sha 不符）」行（L93）：不恢复日历、只报 P0；例程不重跑，priority=true 报主 Agent 与 Arch（fallback L231–234）。
11. c：exit 6 行（L95）写全拦截对象与排除条件，三条 pgrep 模式原文放在表下（L100 起，说明行 L100，模式原文 L102–104，代码块到 L105；取自 fallback L26–28）；写明 exit 6 不写回执（L226），例程自留 date、ps -eo pid,ppid,stat,lstart,cmd 命中行、各 PID 的 /proc/<pid>/stat。
12. d：exit 7 行（L96）写明有授权的 PIN 备份时先恢复日历再返回 7；例程核对 trade_cal sha 是否等于 141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086，不等报 P0；无论如何不重跑、不补写 marker。
13. e：新增「0 / 3（竞态）」行（L97），exit 0 行（L89）改为指向它：例程以磁盘上实际存在的 DONE / FAILED marker 为准，不以退出码为准（fallback L260–264、L276–279）。
14. 删去 R3 变更里「以下几处与代码不完全一致，本次按要求未改，列出待 Arch 定」及其 a–e 列表（已由第 9–13 条写进正文）。

R4.1（2026-10-18T13:58:28-0400，按 Arch 13:56 v3.1 行级审 41bcbcc8 §6；R4 本身未动）：
15. 三.10（L62）：「各步 ok 且无 skipped；hsgt 本次日志 remaining=0」改按 v3.1 实际判定写：cyq / tier3 / hsgt 的 partial 或 skipped 在 allow_relay_partial_20261019=true 下记 WARN，其他 step 出现才判 FAILED；hsgt 日志 remaining=0 的要求注明两种例外（已按 relay_partial 降级时不查；allow_hsgt_source_empty_warn_20261019=true 的源端空日记 WARN）。与上方 L45–48 判定表一致。
16. L65：「r4.4」改为「r4.5」（Eng 纸面例程终版 r4.5 222c10c966bfc5ed5dc01dbe81ce3a6f3f003e546dd7a404854433254f6b1d5c）。上面第 8 条是 R4 当时的记录，原文保留。
17. 记录：R4 首版 sha d7c908c553321f6fb566032533ee39a35669f8162f77dd5b07a2f5f05e29d819 已被同名文件用 os.replace 原子覆盖（只修第 11 条里的代码块行号说明，正文未变），现行 R4 为 9179e2850c77d33316f6a36dcea4eb31030d284f16dc2dbd6e7472faa5137bb0；R4.1 以 9179e285 为底。

R4.2（2026-10-18T14:04:31-0400，按 Arch 14:02 指令与审查文档 ARCH_DATA_NIGHTLY_V31_LINE_REVIEW_ZH.md bf0b4ac29048df1d3b6e6a2ab7b84bd4d3d498831836336ea5043672110e1eeb §九 9.4；R4.1 57a44a93 本身未动）：
18. 六.1（L108）末尾加一句：回执列出 7 个原始文件 PANDAS_ATTRS 的 source（read_schema，只读元数据）、披露 etf510300（来源未记录，先 relay 后回退 datahub）与 mid_large_universe（本地构建、无网络来源）、附驱动回执 checks.env_knobs_inherited.SOURCE；P1 只在三种情况下报：SOURCE 不是 null、某个 source 既不是 datahub 也不是 relay、7 个文件里有缺 PANDAS_ATTRS 的。路径按 tier1_pull.py L11、L59（data/v2/tushare_raw/<api>/<D>.parquet）与 etf_daily_adj_incr.py L13、L29（data/v2/etf/raw/<api>/<D>.parquet）写准。tier1 生产本是 datahub 优先、etf 是 relay 优先，「必需表来自 datahub 就报 P1」的设想已作废，未写入。

R4.3（2026-10-18T16:31:51-0400，按 Arch 10-18 16:27 ET 与 16:30 ET；门槛推导见 docs/v2/ARCH_DATA_NIGHTLY_V31_LINE_REVIEW_ZH.md 第十节（文档 sha b3aba2fc12e2b142c3e7530894b8950a5942b1a5f0e6f82414a34f822be6cf5e）；源 R4.2 b2362a24f76c297a46744cc10600a8d4f133e07669b67075d6ae4d158a5d00e6 本身未动）：
19. 三（L64）：在第三节第 11 条之后新增第 12 条，正文逐字取自 Arch 审查文档 §十 10.6：起跑前（05:30 ET）间隔 15 秒连读 3 次 /proc/meminfo，MemAvailable 须每次都 ≥ 2621440 kB，任一次不达标即不起驱动、不发信号、按未起跑 P1 上报；达标才起驱动并在回执附 rss_max_sum_kb / rss_max_one_kb。第二处：六（L113）：在第六节第 4 条之后新增第 5 条，正文逐字取自 Arch 16:30：call B 的 reason_code 为 RSS（驱动 f99dd11a L515–516）时按 P2 上报，不重试、不写 DONE，trade_cal 还原后复核 sha 141078fa，纸面轨被门禁拦住属预期（主 Agent 10-18 16:27 选方案 A）。除这两处与本变更记录外无任何改动。
