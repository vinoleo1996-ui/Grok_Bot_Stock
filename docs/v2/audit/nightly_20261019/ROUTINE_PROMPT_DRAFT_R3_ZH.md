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
10. 核查只认本次 call B 写入：summary（logs/nightly/20261019_summary.json）顶层 finished 与 mtime 在 call B 窗口内、各步 ok 且无 skipped；hsgt 本次日志 remaining=0；daily_update_status finished_at 晚于 call B 起跑、status=ok、target_trade_date 与 REQUIRED_TABLES last_date 统一成 YYYYMMDD 后 == 20261019、rows 不少于跑前；freshness generated_at 晚于 call B 起跑且 overall=ok；快照 AFTER + compare 退出 0。
11. 先写回执 docs/v2/audit/nightly_20261019/driver_receipt_<时间>.json，**最后写唯一 marker**（DONE 或 FAILED，含 reason_codes），然后退出。任何异常 / 信号 / 子工具超时都走同一收尾：停树 → 恢复并双核日历 → 回执 → 唯一 FAILED → 退出 11。

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
| 0 | 日历 == PIN 且 marker 已存在，无需动作 | 无 |
| 1 | 驱动未写 marker，兜底已代写 FAILED（writer=routine_fallback，reason=driver_killed） | priority=true 给主 Agent 与 Arch |
| 3 | marker 已存在，但日历不是 PIN，兜底已原子恢复到 141078fa 并核过 | priority=true 给主 Agent 与 Arch（说明驱动收尾时日历异常） |
| 5 | 日历 sha 仍不是 141078fa（无合格备份或 .ok 未授权 allow_routine_fallback_restore_20261019） | **P1**，立即 priority=true 给主 Agent 与 Arch |
| 5（拒绝执行） | 当天已有失败的兜底回执（其中 exit=5 或 restore.ok=false），兜底拒绝执行，什么都不做；回执 action=refused_prior_failed_receipt（与上一行同为 5，靠回执区分） | 只报告：priority=true 给主 Agent 与 Arch；不重试，不再跑兜底 |
| 6 | 仍有 run_nightly_v1 / nightly_update / tier1_pull 进程（pgrep 非空），什么都没做 | 不要发信号；5 分钟后再跑一次，仍为 6 则 priority=true |
| 7 | 没有比驱动 .ok issued_at 更新的 run_<STAMP> 目录（没有证据表明驱动启动过）；只报告，不写 FAILED | 不重跑，不补写 marker；priority=true 报主 Agent 与 Arch，交人工判断 |
| 2 | 参数错误 | 报 Data |

### 六、回执与报告（沿用现行例程第 7 步与报告规则）
1. Data 回执（docs/v2/audit/nightly_20261019/ 下新文件）：两条命令与 rc、备份 / 恢复 sha、比对结果、快照结果、reason_codes，以及每一步按实际行数 / 日期范围判定（不以 summary 状态为准）；驱动 marker 已给 daily / daily_basic / adj_factor / stk_limit / trade_cal 与 REQUIRED_TABLES；其余步骤由你只读各自产物 / manifest / 日志补齐。兜底若跑过，附 routine_fallback_receipt_<时间>.json。
2. 有新交易日数据落地：给 Leo 中文简报。
3. Eng：完成通知 priority=false（marker 路径与 sha）。
4. 回执路径 + sha 发给 Arch 与主 Agent；若驱动代设了锁，回执与 TEAM_STATE 写明。

### 七、不变的约束
10-19 之后继续跳过 sw 与 trade_cal 步骤，直到主 Agent 与 Arch 同意。MemAvailable < 2GB 等待（nightly 内置，驱动的时间盒照样计时）。不用 heredoc。只停自己起的确切 PID；不 pkill / killall；不加 --force；不删文件；本例程不给 94322 / 94403 发任何信号；94322 的 STOP 由 04:25 例程用 dc827675 执行，本例程只核状态；16:40–18:40 ET 不跑任何东西。

## R3 变更
- 写于 2026-10-18T13:47:57-0400（取自 date）；作者 QuantLab Data。R3 以 ROUTINE_PROMPT_DRAFT_R2_ZH.md（a5ef41b2754440447ed369d7c8ca26166a27983827eeed04a522041dbf9727a6）为基础，R2 与原稿 ROUTINE_PROMPT_DRAFT_ZH.md（02498e1e478f23d4f8060e38e6ae533678f91ad66e1ac9a0f78f1d15c7e2eb41）都未动；本文件是新文件。驱动 f99dd11a… 与兜底 559d1e01… 只读核对，未改。
- 文头标题「驱动版 v3」与「修订 13:02 ET」说明两轮都未改。

R2（2026-10-18T13:41:50-0400）：
1. 第七节（原文 L97）：「不给 94322 / 94403 发任何信号」改为「本例程不给 94322 / 94403 发任何信号；94322 的 STOP 由 04:25 例程用 dc827675 执行，本例程只核状态」（与 Eng 纸面例程 r3 3232fa6b 的 1b 措辞一致）。
2. 驱动 sha：63b5a88462f9f75ae7975f52320bbd6f88433cdf4857bf95c6de557d6d880e16 → f99dd11aa26f611aca382f98b00ea14fdbcafc99960c8259102e421f02281b0a（L4，1 处，全长完整匹配）。
3. 兜底 sha：f3244472da360b74cc692f90548fab4f8839f13f3938bf65374d592b2d61ac5f → 559d1e017b1c53b1dd1cdffdc0571fc1d33a6157ea4437735421cc3fab271384（L4，1 处，全长完整匹配）。

R3（按 Arch 13:45）：
4. 第三节判定表（L45–48；R2 的 L45 一行拆成四行）：cyq / tier3 / hsgt 的 partial 在对应键为 true 时判 WARN，false 时判 FAILED；写明 WARN 时 marker 顶层 status=OK、steps[] 对应项 status=WARN、warnings[] 有记录、降级日期只追加到 output/data_gap_list/nightly_degraded_gaps.jsonl；call B rc≠0 与 REQUIRED 6 表不全一律 FAILED。键与情形的对应按 v3.1 代码核实：allow_relay_partial_20261019 管 summary status=partial 的 cyq / tier3 / hsgt，reason 为 relay_partial，summary 带 skipped 时记 skipped（同一个键，L596–597、L622–627）；allow_hsgt_source_empty_warn_20261019 只管 hsgt_source_empty（L670–681）；hsgt 已按 relay_partial 降级时不再查 hsgt 日志（L661–663）；marker steps[] / warnings[] / ok_flags 见 L1108–1121，白名单外 skipped 降 FAILED 见 L1131–1136、L1150–1170；GAP_LIST 追加见 L47、L1236–1248；call B rc≠0 见 L1437–1438、L1469–1471；REQUIRED 6 表见 L81、L1496–1501。Arch 给的 L564–568、L601–610、L1029–1033、L1330–1335 是 63b5a884 的行号，按 9fda0202 第 2 节对应到 v3.1 的 L591–598、L658–683、L1131–1137 + L1150–1172、L1474 起（post_checks）。
   - 按代码补充一点：只要本次有 warnings，GAP_LIST 就会追加，与最终判 DONE 还是 FAILED 无关（L1236 只看 R["warnings"]）。
5. 第五节兜底退出码表：在 exit 5 行后新增「5（拒绝执行）」行（L90，当天已有失败兜底回执 → 拒绝执行，只报告不重试；fallback L7、L148–157、L217–221）；在 exit 6 行后新增 exit 7 行（L92，无比 .ok issued_at 更新的 run_<STAMP> 目录 → 只报告不写 FAILED，例程不重跑、不补写 marker、priority=true 报主 Agent 与 Arch；fallback L13–14、L250–268、L274–275）。
6. 第三节驱动第 6 步（L58）：「孤儿扫描（PPID=1 的可疑进程只记录 P1，不发信号）」改为「PPID=1 的可疑孤儿挡住 DONE：判 FAILED，reason_codes 含 ORPHAN；驱动不对孤儿发任何信号」（驱动 L23、L385–390、L537–538、L1382）。全文其他地方没有「孤儿只记录」类说法。
7. 删去 R2 变更第 4 条里「以下几处描述的仍是 v3 行为」那句注（三处已在 R3 第 4–6 条改正）。

第五节退出码表与 routine_fallback_v1.py（559d1e01）对照，以下几处与代码不完全一致，本次按要求未改，列出待 Arch 定：
a. exit 1 行：代码要求先有晚于 .ok issued_at 的 run_<STAMP> 目录才代写 FAILED（L251–264）；且退出码优先级是 5 > 1 > 7 > 3 > 0（L269–279），代写了 FAILED 但日历仍不是 PIN 时返回 5，不是 1。
b. exit 5 行：代码里 5 还包括「DONE 已存在而日历 sha 不符：只报 P0、不恢复」（L231–234），表中未写。
c. exit 6 行：表中只写 run_nightly_v1 / nightly_update / tier1_pull；代码是三条模式，另有 scripts/acquire/*.py 与 import tier1_materialize（L26–28），94322 / 94403 只按确切 PID 且 state=T 时排除（L9、L29）；exit 6 不写回执（L226）。
d. exit 7：日历不符且有 sha==PIN 的备份并已授权时，兜底仍会先恢复日历，再按无起跑证据返回 7（L231–248、L274–275）。
e. exit 0：极少数竞态下（检查时无 marker，写入时 FAILED 已被别人写出，FileExistsError）不报 1 而落到 0 或 3（L263–264、L276–279）。
