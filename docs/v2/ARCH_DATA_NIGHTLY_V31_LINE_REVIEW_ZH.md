# Arch 行级审查 v3.1：Data 10-19 日更驱动 run_nightly_v1（f99dd11a）与兜底 routine_fallback_v1（559d1e01）

- 审查人：QuantLab Arch；写成 2026-10-18T13:55:53-04:00（ET，date 生成）。
- 方法：只读静态审查，草稿目录 /tmp/arch_v31_review。没有运行驱动、兜底或 Data 自测；没有打开任何 parquet；没有在 repo 里 git apply；除本文外没有改 repo 任何文件；没有发任何信号。
- 只读过的非代码文件：logs/nightly 下 10-15 / 10-16 的文本日志（.out / .log）；数据文件只用 stat（大小 / mtime）。
- 对照基准：Arch 行级审 ARCH_DATA_NIGHTLY_V1_LINE_REVIEW_ZH.md（ec1ac8e1，PASS_WITH_CONDITIONS）；主 Agent 13:16 / 13:19 / 13:21 裁定；主 Agent 关于 v3.1 冻结的决定（marker 不加 gap_list 字段、不补 T29、日历异常修复延后为 P3）。
- 本文**不是 .ok**，没有创建任何 .ok。

## 0. 审查对象（sha256 全部重算，与申请一致，无不符）
| 文件 | sha256 |
|---|---|
| docs/v2/audit/nightly_20261019/run_nightly_v1.py（1571 行） | f99dd11aa26f611aca382f98b00ea14fdbcafc99960c8259102e421f02281b0a |
| docs/v2/audit/nightly_20261019/routine_fallback_v1.py（285 行） | 559d1e017b1c53b1dd1cdffdc0571fc1d33a6157ea4437735421cc3fab271384 |
| DRIVER_DIFF_vs_63b5a884_20261018T133614.diff | 403723b9eec15824cdfc88b162c9edfab77b9a86bfd1c8f03a870608be94da44 |
| FALLBACK_DIFF_vs_f3244472_20261018T133614.diff | 4181421191641687d1e2def9c015a70358e365746d025bba188074bdc8abde8a |
| TEST_RECEIPT_v31_20261018T133614.json | 2e476adf35b7b6f0392495d4c6f274d989f2ef4b347f1e225ae4eea23c06c791 |
| DRIVER_DIFF_vs_prev31_20261018T133614_ZH.md | 9fda0202dad0d784f2d191af6c2e957e5ea0e56bc5ed5319ae21e018658e2ae4 |
| NIGHTLY_20261019_OK_REQUEST_R2_ZH.md | b54907e3649057576c507151d0681d50816393465140b8c9e97ad8f75280299d |
| ROUTINE_PROMPT_DRAFT_R2_ZH.md / R3 / R4 | a5ef41b2… / cb48de7b… / 9179e2850c77d33316f6a36dcea4eb31030d284f16dc2dbd6e7472faa5137bb0 |
| 归档旧版 prev31_20261018T131600/：run_nightly_v1.py / routine_fallback_v1.py | 63b5a88462f9… / f3244472da36… |
| Eng 纸面例程 r4.5 / r4.5-strict（终版） | 222c10c966bfc5ed5dc01dbe81ce3a6f3f003e546dd7a404854433254f6b1d5c / ca0f873555d1016baa7f47160b3c0e4efe646cae3379df33449a9a6e0ebaef7f |
| scripts/nightly_update.py / tier1_pull.py / fill_hsgt_top10_extend.py | ec079d56… / 5b70dfed…（仍钉 5b70dfed，驱动 L54、L62）/ 36cff47c… |

- 两份 diff 都能从归档旧版逐字复现（diff -u 旧 新，去掉文件头后与 Data 的 diff 完全相同）。
- 驱动 L76 钉的兜底 sha = 559d1e01…，与磁盘一致。
- 活动 trade_cal 当前 sha = 141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086。run_<STAMP> 备份目录现在还没有（只有 predraft*/prev31 归档）。备份 sha 由驱动 L1333–1341 保证：建备份后 live 与备份两份都必须等于 PIN，否则前置失败；兜底 L237–242 只用 sha==PIN 的备份。所以「PIN 备份 = 141078fa…」靠代码保证成立。

## 1. 结论：PASS_WITH_CONDITIONS
- 旧审的 P1-1/2/3、P2-1/2/4、P3-1/2/4 和主 Agent 的新裁定都已落在安装字节里（见第 2 节）。没有 P0，也没有新的阻塞性 P1。
- 签发条件：
  - C1 按第 8 节键表签。两个新键同取值（建议都是 true；不要一真一假，原因见 F-6）。source_relay_only=false，expires 16:00。
  - C2 例程配对：签 v3.1 就配 r4.5（relaxed）；退回 63b5a884 就配 r4.5-strict。不要交叉配对（第 5 节）。
  - C3 .ok 最早 10-19 17:05 ET 归档，且要同时满足：磁盘上已有 marker、trade_cal sha==PIN、当天兜底没有退出 5（第 4 节）。
  - C4 94322 在 05:25 前必须是 T（04:25 例程用 dc827675 执行 STOP）。如果 STOP 没成功，驱动前置会拒跑，这是正确行为（第 3 节 F-9）。
- Data 例程 R4（9179e285）：PASS（小瑕疵见第 6 节，不阻塞）。

## 2. 逐项核对（行号均指新文件）
| 项 | 结论 | 证据 |
|---|---|---|
| P1-1 兜底代写 FAILED 前要求有起跑证据 | 已实现 | fallback L134–145 run_evidence（run_<STAMP> 晚于 .ok issued_at）；L250–268：无证据就退出 7，不写 |
| P1-2 兜底 pgrep 范围 | 已实现 | fallback L26–28 三条锚定、括号转义的模式；L103–123：94322/94403 只在确切 PID、cmdline 一致、state=T 时排除 |
| P1-3 受保护进程核整棵树 | 已实现 | 驱动 L413–443：T 时 descendants()，任何后代不是 T/Z/不存在就前置失败；relay_outage_backfill 同样核树 L430–440 |
| P2-1 收尾 sha 不符先恢复 | 已实现 | L1463–1468：compare_restore(final)，失败退出 4，成功退出 1 |
| P2-2 PPID=1 孤儿挡 DONE | 已实现 | L537–538 ORPHAN 判失败；call A 记为 dirty，不重试（L1382、L1390） |
| P2-4 兜底不重复动手 | 已实现 | fallback L148–157、L217–221（当天已有失败回执就退出 5）；L231–234（DONE 在而 sha 不符：只报，不恢复） |
| P3-1 docstring | 已改 | L15 |
| P3-2 去重 | 已实现 | L161–165 add_code + counts；L533–536 residual 按 pid 去重 |
| P3-4 冻结件 | 已实现 | FROZEN L43–46（加 sw_l1_pit 89d4afa3/87d769aa、sw_pit 0b1d3432），cal_shas L999–1004 跑前跑后都核 |
| P3-3 / P3-6 | 未做（按冻结决定延后） | — |
| 新键解析：只认小写 true/false，缺省 false | 已实现 | L125 列为可选键；L793–797：出现时值必须是 "true" 或 "false"（大小写敏感，空值也拒）；缺省按 false；ok_known_keys L700–701 |
| WARN 只限 call B 的 cyq/tier3/hsgt | 已实现 | L596：要求 tag=="callB"、k 在 RELAY_ONLY（L80）、键为 true、status=="partial" 才降级；其余仍走 L598 判失败；call A（L1380）不可能降级 |
| hsgt WARN：fail=0 + HTTP 200 且 0 行的证据 | 已实现（见 F-2） | L670–681：fail=0、remaining>0、auth_max≥20250601、无 ABORT，且 remaining 等于本次窗口内写出的 0 行文件数（L685–696）；save_day 只在 pull 成功后写（fill_hsgt L122） |
| DONE 仍是 OK，带 warnings[{step,date,actual_rows,reason}] 和 ok_flags 布尔 | 已实现 | L1119–1121；actual_rows 用 int()；ok_flags 用 bool() |
| REQUIRED 6 表不全就 FAILED | 已实现，与键无关 | post_checks L1496–1501；freshness overall L1508 |
| call B rc 不放宽 | 已实现 | L1437、L1469（所有 invocations rc==0 且恰好两条）。注：nightly_update.py 只要不崩溃就退出 0（L97–139 没有 sys.exit），所以 rc 闸门本身很弱，步骤结果靠 summary 判 |
| skipped 只许出现在 status=WARN 的 cyq/tier3/hsgt 项里 | 已实现 | L1108–1118、L1131–1136、L1146–1170（否则 DONE 降为 FAILED，并把 skipped 改写成 not_run） |
| 降级日期写入缺口清单 | 已实现 | L47、L1236–1248（第 4 节） |
| daily_pull 重试 ≤2、间隔 ≥30 分钟、先隔离、每次重试满足时间闸门 | 已实现（口径见 F-5） | L1356–1411：max_retry=min(2,键值)，L1394；L1408 睡 30 分钟；L1386 先隔离，L1401 隔离完成才可重试；L1403 下次起跑 +30+75 ≤ 16:00（比裁定的 +75 更严） |
| call B 最晚 14:45 起跑 | 已实现 | L1421 起跑 + budget(75) ≤ 16:00；L1431 硬停在 min(起跑 + 75, 16:00) |
| tier1_pull 钉 5b70dfed | 是 | L54、L62；磁盘一致 |

旧行号对应：63b5a884 L564–568（check_summary 循环）对应新 L591–598；L601–610（check_hsgt_log）对应 L658–683；L1029–1033（marker 去 skipped）对应 L1131–1136 加 L1146–1170；L1330–1335（post_checks 开头）对应 L1474 起。Data 的映射成立，只是辅助函数实际从 L1146 开始，不是 L1150。

## 3. 发现（新问题与风险）
- **F-1（P3，冻结后处理）**：L654 的 P1 告警文本里有「cal refresh skipped」字样。这条告警只在 call A 日志缺那一行时写出，会进 marker 的 alerts，L1131 就把 DONE 降成 FAILED。结果是失败方向保守（fail-closed），而 strict 例程本来也会挡。按主 Agent 冻结决定延后到 P3：把告警措辞改掉，不带 skipped。
- **F-2（P3，需主 Agent 知悉）**：allow_relay_partial=true 时，hsgt 的 partial（RELAY_DOWN 快速失败或 rc=3）走 L596 直接记 WARN，L661 跳过 hsgt 日志检查，不要求 fail=0。这符合「cyq/tier3/hsgt 可降级」裁定；「fail=0 + 200/0 行」那条只约束 hsgt_source_empty 这一类。附带说明：L673 的 log_ok0 只记录，不作闸门。0 行文件与 remaining 计数相等，已经是更硬的证据。
- **F-3（P3）**：缺口清单在 finish（L1236）里只要 warnings 非空就追加，FAILED 运行也一样。行里带 run=STAMP 和 recorded_et，但 marker 里没有 STAMP 字段（只能从 marker.receipt.path 的 driver_receipt_<STAMP>.json 里取出）。18:40 后 supersede 重跑时，同一 <D> 会留下旧行。
- **F-4（P3）**：hsgt_source_empty 的 warnings[].date 是空日自己的日期（L676，可能早于 D，例如 20251226），不一定等于 D。r4.5 只收集 date==<D> 的行，这种 WARN 会被判成「warnings 元素找不到对应行」。结果是误报 P1，但照常跑，不会误挡。
- **F-5（口径）**：只有 MAX_RUN 可以重试（L117、L1392）。rc=0 但行数不合格（ATTEMPT_FAILED）时只隔离、不重试，延续旧审 Q-2。主 Agent 裁定里「先隔离再重试」如果本意是坏文件也要重试，就需要改代码（冻结决定下不改）。隔离位置是 RUN_DIR/quarantine/a<k>/<api>/（_recovery 下），不是字面上的 _quarantine/，同盘 rename，并报 P1（L1079）。行数门槛的参照日 ref_day 取小于 D 的最近文件，10-19 时就是 20261016。
- **F-6（例程配合）**：r4.5 relaxed 2a 的 (ii) 要求只要有 WARN，两个 ok_flags 都必须是 true。如果只签一个键为 true（例如 relay_partial=true、hsgt=false），驱动会写出合法的带 WARN 的 DONE，例程却会挡下。所以两个键必须同取值。长期看，建议 Eng 改成按 reason 只核对应的那个键。
- **F-7（P3）**：缺口清单逐行 os.write 不检查短写；没有加锁，但只有驱动一个写者。写失败会被吞掉（只记进回执，DONE 照写），r4.5 会报 P1 照常跑。可以接受。
- **F-8（既有，非驱动）**：RELAY_DOWN 时，nightly_update.py 的 register_backfill（L86–95）用非原子 write_text 整份重写 relay_outage_backfill_queue.json。这是 Data 不把缺口写进该文件的正当理由；同时也说明它本身有截断风险（94403 读它；运行期间 94403 必须是 T 或不存在）。
- **F-9（确认）**：94322 如果 05:30 仍是 Ssl：驱动 guarded_check（L428–429）和 pgrep_gates（L886）都会前置失败。例程先跑 --check-only，退出 2，什么都不写，正式命令不会跑。之后兜底 busy()（fallback L120–122）会因为 S 状态的 remaining_after_stk_surv.py 命中 scripts/acquire 模式而退出 6，不动手。94322 变成 T 以后，没有 run 目录，兜底退出 7。不会误写 FAILED。行为正确。
- **F-10（测试）**：没有重跑 Data 自测，原因有三。(1) 测试会对自己起的假进程发 SIGSTOP/SIGKILL（tdrv6 L28、L146–154、L311–338），并且按 cwd 匹配进程，和「不杀任何进程」冲突。(2) tdrv6 在 L413 之前没有把 TRADE_CAL/FROZEN/PIT_CAL 换成假路径，全程也没有重定向 GAP_LIST/QUIET_LOCK，不能证明纯合成。(3) 测试回执本身自洽：30 条全 PASS，名称与 T01–T28（T23 a/b/c）一致，被测驱动 sha=f99dd11a，leftover 全空。真实 output/data_gap_list/ 目录不存在，说明测试没有写到真实缺口清单。T27 只调了 write_marker，缺口清单的追加没有被测试覆盖。
- **F-11（P3）**：marker 里的 raw_file sha 在 call A 结束时测量（L1384）。call B 各步不写 tushare_raw/<api>/<D>.parquet（adj_factor_incr 只读 raw，L14；index_pull 写 index_daily），所以到 marker 时仍然有效。纸面 2b 在 18:40 后重算，期间如果有别的进程（例如 CONT 后的 94322）改写同一文件，会被挡。风险低，属于 fail-closed。

## 4. 兜底与 .ok 归档时间
- 兜底读 .ok 的地方有两处：L243 allow_routine_fallback_restore（只在日历不是 PIN 且没有 DONE 时用）；L252 issued_at（只在没有任何 marker 时用）。它不核 .ok 的 sha 和有效期（P3-6），所以 16:00 过期后兜底照样能用。
- .ok 被移到 _consumed/ 之后：ok_kv 返回 {}，issued 是 None，run_evidence 为空。这时没有 marker 就退出 7，不代写 FAILED。日历如果不是 PIN，也会因为未授权而不恢复，退出 5。Data 说的 exit 7 成立，而且日历恢复能力也会一起丢掉。
- 驱动最晚结束时间：call B 最晚 16:00 硬停；之后的审计工具超时上限是到 16:40（L469）；16:40 后工具超时 1 秒，走 restore_native 收尾，约 16:41–16:42 结束。Data 例程规定驱动结束后 20 分钟内跑兜底，所以最晚约 17:02。Arch 的 20 分钟例程到 16:40 为止。
- **安全归档时间：10-19 17:05 ET 之后**，并且同时满足：磁盘上已有 DONE 或 FAILED marker、trade_cal sha==141078fa…、当天兜底没有退出 5。Data 建议的 16:40 偏早，Data 自己的兜底可能晚到约 17:02。

## 5. marker 与 Eng 纸面例程（r4.5 / r4.5-strict）
- 驱动写的 marker（L1092–1143）：顶层 schema、status（OK/FAILED）、date、invocations、prior_attempts、steps（list）、warnings、ok_flags、trade_cal_sha256、superseded_failed_marker、receipt、written_at_et 等。steps 每项用 step 加 kind 标识：
  - raw_file（daily/daily_basic/adj_factor/stk_limit/suspend_d）：path、exists、rows、sha256、date_range（L1096–1099）
  - calendar（trade_cal）：cal_info 给 path、rows、sha256、date_range（L1101、L926–931）
  - required_table（status_<表>）（L1105–1107）
  - call_b_step（L1109–1118）：WARN 项带 status=WARN、warn_reason、nightly_status，以及可选的 skipped、source_empty_days
- Eng 各条声明的核对：
  - 2b 同时处理 list 和 dict 两种形状：正确。v3.1 用 element[step]；旧 63b5a884 是 dict（旧 L1006–1015）。
  - 2b 只对 sha256 非空的 raw_file 和 calendar 项重算：成立。DONE 时 daily 和 daily_basic 是 GATED 表（L1045–1052 要求存在），L1040 一定会算 sha256，所以必定非空。calendar 项一定带 rows 和 sha256；只有 cal_info 抛异常时才没有 sha，那种情况 2b 会挡（fail-closed）。
  - nightly_update.py L108 写小写 ok：成立（bundle）；L120 也是小写 ok。marker 的 call_b_step 原样抄 summary 的 status，所以是 ok，只有 WARN 是大写。
  - r4.5-strict 2a 与现行 strict 文本逐字相同：成立（与 CURRENT_PROMPT 和 r4.1-strict 的 2a 都 diff 一致）。
  - r4.4 到 r4.5 只改了 DEGRADED_GAPS 段里的两句（单向子多重集；多出的行看 prior_attempts）：成立。两版各只有 1 行变化（r4.5 L40 / strict L35），两版的段落完全相同。
- 缺口清单比对的字段：jsonl 每行是 dict(w_, run, recorded_et, source)（L1242）。其中 step 就是字面的 cyq / tier3 / hsgt（来自 CALL_B_STEPS 的键 L78–79 和 L676 的 hsgt），不是 cyq_perf、tier3_pull 一类名字；date 是 YYYYMMDD 字符串；actual_rows 是 int；reason 取值 relay_partial / skipped / hsgt_source_empty。marker 的 warnings[] 与 jsonl 来自同一个 R[warnings] 列表，四元组逐字相同。r4.4/4.5 的例外句不会误挡合法 WARN。行里多出的 run/recorded_et/source 三个键，只要按四元组投影比对就没有影响。
- r4.5 剩余问题，都不会误挡，只会误报 P1：
  - (a) F-4：hsgt 空日日期 ≠ D。建议把「Collect every line with date == <D>」改成「Collect every line whose date == <D> or equals any marker warnings[].date」。
  - (b) 判断「多出的行是否预期」用的是 prior_attempts，但 prior_attempts 是同一次运行里 call A 的重试，它们不写缺口清单。真正会留下旧行的是 18:40 后 supersede 重跑。建议改成「if the marker superseded_failed_marker is non-null」。
  - (c) F-6：relaxed 2a 的 (ii) 要求两个键都是 true。
- strict 2a 对完全干净的 v3.1 运行：
  - 干净运行时全文没有 skipped（F-1 那种情况除外，而且那时驱动已经降成 FAILED），invocations 恰好两条（L1469 保证），2b 处理 list。所以按语义会放行。
  - 唯一风险是字面对 schema 字段名：例程写的是 schema_version / name / date_min / date_max / started_at / ended_at / written_at，驱动写的是 schema / step / date_range / started_et / finished_et / written_at_et。这处差异旧驱动同样存在，不是 v3.1 新引入的。
- 配对结论：
  - v3.1（f99dd11a）配 r4.5：正确。
  - 63b5a884 配 r4.5-strict：正确。旧驱动会把两个新键当未知键拒跑，旧 check_summary 也让任何 partial/skipped 都判 FAILED，所以旧驱动不会写出降级的 DONE；strict 2a 禁止一切 skipped，与此一致。
  - 交叉配对：r4.5 配旧驱动可能误挡（旧 marker 没有 warnings / ok_flags 字段，而 r4.5 写明这两个字段总是存在）；r4.5-strict 配 v3.1 会挡下所有降级夜（保守，不算误放）。

## 6. Data 的 .ok 申请 R2 与例程 R2/R3/R4
- 申请 R2：两个新 sha 和全部钉值与安装字节一致。块内 57 个键，没有重复。两个新键都是 false，与 L122–125（可选、缺省 false）相符。过时之处：
  - §5 写的键数 55、§2 的 expires 16:40、文头的 v3 / 13:02、§4 退出码没有兜底 7、§6 Q-3 / Q-4(a) 都已过时。
  - relaxed=false、retry=0 和主 Agent「最多重试 2 次」的裁定不一致。本文第 8 节改为 true / 2。
- 例程 R2 除 Data 自列的三处外还有这些过时文字：
  - 三.10「各步 ok 且无 skipped；hsgt remaining=0」没写降级例外；
  - 五 exit 6 只列了三种进程名；
  - 五 exit 5 没有「已有失败回执」和「DONE 在而 sha 不符」两种情形；
  - 六.1 没提 warnings / 缺口清单；
  - 文头还是 v3 / 13:02。
- 例程 R4 核对（父 Agent 列的各行）：
  - L65：call B 重跑时在回执里列出上次追加的 gaps 行，报 P1 照常跑。合理。文中写的「r4.4」应改为 r4.5；而且 r4.5 下 supersede 重跑的 prior_attempts 通常为空，所以会报 P1，与 L65 一致。
  - L88：判定顺序是失败回执→5、pgrep→6、然后 5>1>7>3>0。与 fallback L217–226、L269–279 一致。
  - L89/L97：竞态时（write_new 抛 FileExistsError，L263–264）返回 0 或 3，以磁盘上的 marker 为准。正确。
  - L90/L92：exit 1 需要有起跑证据且日历==PIN；代写了 FAILED 但日历仍不是 PIN 时返回 5。正确（L269–273）。
  - L93：DONE 在而 sha 不符，报 P0，不恢复，不重跑。正确（L231–234）。
  - L95、L100–105：三条 pgrep 模式与 fallback L26–28 逐字一致；排除逻辑与 L111–122 一致（自身 PID、已退出或 Z、确切 PID + cmdline + T）；exit 6 不写回执（L226）。正确。
  - L96：exit 7 之前会先恢复（恢复块 L231–248 在证据判断之前执行），并核对 141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086，与 PIN 常量（fallback L24、驱动 L38）一致。正确。
  - 剩余小瑕疵：三.10 那句仍是旧文（上方判定表已更正）。不阻塞。
  - R4 判定：PASS。

## 7. source_relay_only 证据与建议
- f99dd11a 的实际作用：
  - true 时 child_env（L447–453）给 call A 和 call B 的所有子进程设 SOURCE=relay。真正读 SOURCE 的只有 tier1_pull（L14–20），这时只走 relay，不再回落 datahub。
  - tushare_relay_pull 的 _call 只在 preferred 既不是 relay 也不是 datahub 时才看 SOURCE（L14–25）；etf_daily_adj_incr 和 eng_daily_panels 都传 preferred=relay，所以不受影响，照样能回落 datahub。
  - 所以 true 的效果是：daily_pull（以及 call B 的 index_pull）只走 relay。relay 宕机时，tier1_pull 每页重试 8 次后抛错，rc≠0（ATTEMPT_FAILED，不可重试）或者拖到 30 分钟 MAX_RUN，**当天基本必定 FAILED**。
  - false（不设）时 tier1_pull 是 auto：先 datahub 再 relay（L18）。
- 日志证据（只读文本）：
  - 20261016_run_0019ET.out 里 8 处与来源有关的字样，全是 RELAY_DOWN fast-fail（hsgt/sw/cyq/tier3 在 summary 行和 JSON 里各 4 处），没有任何 datahub 字样。那次 relay 在约 00:25 ET（summary finished 12:26+08:00）被 relay_up() 判定宕机；daily_pull 在 00:19:02–00:19:16 成功，每个接口约 3 秒。
  - 10-15 那次（23:55 ET 起）daily_pull 也是每个接口约 3 秒。10-15 hsgt 日志里有 relay 池报错 upstream_pool_exhausted（504），说明 relay 当时可达但不稳定。
  - 日志本身都没有逐接口记来源；能证明来源的只有原始文件里的标签。
- 6 张 REQUIRED 表的来源：
  - daily_ohlcv_raw_pit、daily_basic、asof_ts 都来自 tier1_pull 的 raw（auto，先 datahub）。tier1_pull 在 pull() 结束时把 df.attrs[source] 设为实际成功的源（L50），并在 save() 时（23:55 / 00:19）写入文件。
  - 注意 tier1_materialize L76 的「(datahub)」是写死的字符串，不能当证据。
  - etf_daily_adj、etf510300 先 relay 后回落 datahub。
  - mid_large_universe 不联网。
- 01:14 重写问题：
  - logs/nightly 和 tushare_raw 下 10-15/10-16 文件的 mtime 都在 01:13–01:14，纳秒尾数都一样（…683904），这是快照恢复的特征，与 Eng 5b19a009（01:05:41 重启后全盘快照恢复，内容保留）一致。
  - 所以原始文件里的来源标签很可能是 23:55 / 00:19 拉取时写下的，早于恢复。本文没有读 parquet 元数据，这一点只是推断。
- 建议 **source_relay_only=false**。理由：datahub 是这两夜 REQUIRED 原始数据的实际来源（标签加上时序推断）；relay 在 10-16 夜里宕机过；设 true 会把一条正常的回落路径变成单点失败。

## 8. 建议签发的 .ok 键表（58 键；key=value，LF，无注释；签发时用 date +%Y-%m-%dT%H:%M:%S%:z 填 signed_et 和 issued_at；os.link 独占创建）
- 相对旧审 §6 的变化：
  - sha_driver 换成 f99dd11a，sha_routine_fallback 换成 559d1e01；
  - 新增 allow_relay_partial_20261019=true、allow_hsgt_source_empty_warn_20261019=true（必须同取值，见 F-6；主 Agent 如果要保守，就两个都写 false）；
  - source_relay_only=false；expires_et=2026-10-19T16:00:00-04:00；relaxed=true / retry=2（主 Agent 已裁定）。
- 「call B 最晚 14:45 起跑」由 call_b_budget_min=75 加 call_b_latest_finish=16:00 推出（L1421）。不能另写一个键，驱动会把未知键拒掉（L729–730）。
- 两个新键取 true 的依据：
  - 10-14 到 10-16 每夜都有 cyq/tier3 partial，10-16 四个中转步骤全部 RELAY_DOWN；
  - 纸面不读 cyq/tier3/hsgt（b8109764）；
  - REQUIRED 表、call A、call B rc 都不受这两个键影响；
  - hsgt 空日 WARN 的闸门很严（F-2）。

```
ok_id=ARCH_RUN_AUTH_DATA_NIGHTLY_20261019
ok_type=run
date=20261019
signed_by=QuantLab Arch
signed_et=<date>
issued_at=<date>
expires_et=2026-10-19T16:00:00-04:00
single_use=true
live=false
promotion_approved=false
interpreter=/usr/bin/python3
sha_driver=f99dd11aa26f611aca382f98b00ea14fdbcafc99960c8259102e421f02281b0a
pin_trade_cal=141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086
pin_frozen_closure=6919e7afe605cc4d1af48868a06b6550db66e3fd1923a3e61bdcc16c621bae20
daily_pull_max_min=30
call_b_budget_min=75
call_b_latest_finish=16:00
rss_stop_kb=1484800
rss_hard_kb=1536000
blackout_et=16:40-18:40
allow_kill_scope=driver_descendants_exact_pid
allow_trade_cal_step=false
allow_sw=false
allow_force=false
allow_delete=false
allow_commit=false
sha_cal_restore=6686876bdcfc95f11d493b5201f55eb726e69e4894d8c96bfaf46ab1748387a4
sha_cal_compare=74093ff3be4c431bab8c469307b207b43b8e1cff707dd0bac1319a7e265cddfc
sha_snapshot_tool=c930ed5c627bf937e6b5d139c52f18945f045286e78dba66cbe5adfab92ab79a
sha_scope=04d716af2a87a8bf365431c97097a5c740353c6c273de82677d826f1c4d98807
sha_nightly_update=ec079d56912aea8a4358a7ae97a73a3ad6ee3df34e83845ad4d655d31d838636
sha_tier1_pull=5b70dfed08a237034b586ef9738e2c1b81607b20387a62df49a1e6994ba711cf
sha_tushare_proxy=ae91f230560d445b4d2321e8e022d01b55773e168d4d842fc6987fa9458fc772
sha_relay_health=6d3ea9f57f63af8d82d6eeaf140a989aeb09cda941e6711c25f12fd3bbe0e17f
sha_adj_factor_incr=723726c5623a1739ee1fb1dcf97a6be6efd4532717a4c4411fb5e24dfd1422ad
sha_tier1_materialize=e9c89a6c3a0719d9b78064404f2b7d66a7076430f5676e65335db06efae1c3bb
sha_etf_daily_adj_incr=ae670dfc0da14f7aa90bb1d6edd3377b027f69dcb739987dc016388e45b02ae4
sha_eng_daily_panels=a754205397d22b6bb1109d92ee4040d65faedec2d37afd575f77e63da642f0be
sha_mid_large_universe_incr=fe4bbffe1c7c8e0a3f4d38a590acbbcaab61f53b08939722e9b503fa2901d64b
sha_light_event_windows_pull=f12660b90c01089278f01e22b3bdf53154780802668ed4ea90ea5c38c3fc9d71
sha_forecast_manifest_declare=f77673811aa2dd05d461cf895476212f52b05abc3f26212cba87ea30578bd731
sha_fill_hsgt_top10_extend=36cff47c008244ee50f7fb2fcc5f6fd0588d7141901b3a23afe50c48f058e918
sha_cyq_perf_monthly=6aae6c1b8de7b37752fb5032c22ea65b698f252cc57f8e5af94b1e13d6e09c1f
sha_tier3_daily_snapshot=64a71f5607439c5b09ddd92a8dfeffd94e4f5244297f83fbc5c65e3abfcf1067
sha_data_freshness_status=a759d29788859b43783bac6360014347b2df0e4dce5949302a0908db511f1d50
sha_routine_fallback=559d1e017b1c53b1dd1cdffdc0571fc1d33a6157ea4437735421cc3fab271384
allow_run_daily_pull_20261019=true
allow_run_call_b_20261019=true
allow_restore_trade_cal_20261019=true
allow_write_nightly_marker_20261019=true
allow_routine_fallback_restore_20261019=true
allow_quarantine_mv_daily_raw_20261019=true
allow_create_research_quiet_lock_20261019=true
allow_profile_relaxed_20261019=true
allow_daily_pull_retry_20261019=2
allow_relay_partial_20261019=true
allow_hsgt_source_empty_warn_20261019=true
source_relay_only=false
```
- 签发前在签发时刻重算全部 sha，任何一处不符就不签；签前跑一次驱动 --check-only，确认 .ok 解析通过。

## §九 source_relay_only 生产先例核实（主 Agent 有条件批准 false 后补核）
- 写成 2026-10-18T14:01:36-04:00（ET，date 生成）。只读静态核查，草稿目录 /tmp/arch_v31_src。
- 读过的数据文件元数据：只用 pyarrow.parquet.read_schema 读 schema 级 key-value 元数据（PANDAS_ATTRS / pandas 两个键），没有读任何行或列值。
- 没有运行任何项目代码，没有发信号，没有建 .ok。

### 9.1 10-15 / 10-16 夜更是谁起的、带什么环境
- 本机没有 crontab 程序，也没有 /etc/cron.d。夜更是 Data 的例程「A」起的。现行文本 docs/v2/audit/nightly_20261019/ROUTINE_A_CURRENT_20261018.txt L7 的命令是 python3 scripts/nightly_update.py --date D --steps …，**没有 SOURCE**。日志里 20261015_run_2355ET.out、20261016_run_0019ET.out 记的都是全量步骤。
- nightly_update.py 传给子进程的环境是 os.environ 加 env_extra（L44：QL_TODAY、TOP10_START、CHUNK_DAYS、TOP10_END；L102），不设 SOURCE。
- tier1_pull.py：
  - L14 SOURCE 缺省为 auto。
  - L17–20：auto 时 order=[datahub, relay]（preferred=datahub）；只有 SOURCE=relay 才是 relay 单源，SOURCE=datahub 是 datahub 单源。
  - extend 一律 preferred=datahub（L113、cached_day L64–70）。
  - L50 把实际成功的源写进 df.attrs[source]，保存时（L58–62）pandas 把它写成 parquet 的 PANDAS_ATTRS 键。
- **口径更正**：生产里 tier1（daily/daily_basic/adj_factor/stk_limit/suspend_d）是「datahub 优先、relay 兜底」，不是「relay 优先」。etf_daily_adj 和 etf510300 才是「relay 优先、datahub 兜底」（etf_daily_adj_incr.py L25–27、eng_daily_panels.py L26–28 都用 preferred=relay；tushare_relay_pull.py L14–25 在 preferred 明确时不看 SOURCE）。
- 文件证据（read_schema）：
  - tushare_raw/daily/2026101[56].parquet、daily_basic、adj_factor、stk_limit、suspend_d 的 PANDAS_ATTRS 都是 {source: datahub}。
  - 如果当晚设了 SOURCE=relay，tier1_pull 只会用 relay，标签必然是 relay。所以**那两晚 tier1 没有被强制成 relay**。
  - 当晚环境本身没有落盘，无法区分「未设」和「SOURCE=datahub」。按例程命令和 nightly_update L102 推断是未设。
- v3.1 的 false：
  - child_env（run_nightly_v1.py L447–453）只在 CFG[source_relay] 为 true 时加 SOURCE=relay；false 时不加，子进程继承驱动的 os.environ，与 10-15 / 10-16 的做法相同。
  - 驱动另外恒设 TSPRO_RELAY_TIMEOUT=115（L106）和 call A 的 TIER1_SKIP_CAL_REFRESH=1（L107）。这两个只改 relay 超时和日历刷新，不改选源顺序。
  - 注意：false 是「不设」，不是「强制清空」。如果例程 shell 里已经 export 了 SOURCE，会被继承。驱动把继承值记在回执 checks.env_knobs_inherited.SOURCE（L1290–1291）；invocations[].env_set.SOURCE 只反映 .ok（L540），不反映继承值。

### 9.2 六张 REQUIRED 表能否走 datahub，生产里是否用过
| 表（research_loop.py L633） | 生产路径 | datahub 是否已有生产先例 |
|---|---|---|
| daily_ohlcv_raw_pit | tushare_raw/daily 加 adj_factor/stk_limit/suspend_d，经 tier1_materialize.materialize_bars 本地物化 | 是，而且是主源：tushare_raw/daily 共 2130 个文件全是 datahub（20180102–20261016）；stk_limit、suspend_d 各 2130 个全是 datahub；adj_factor 73 个全是 datahub。注意 tier1_materialize L76 的「(datahub)」是写死的字符串，不算证据 |
| daily_basic | tushare_raw/daily_basic，经 materialize_daily_basic 本地物化 | 是：3107 个文件中 datahub 2021 个（含 20261012–20261016 全部），relay 1086 个（20140401–20250915 的历史段） |
| asof_ts | materialize_bars 把同一批 tushare_raw 增量写进 asof_extend_tushare_202610/panels（tier1_materialize L114–152）；eng_daily_panels.asof_ts（L116–124）只校验 | 是，与 daily 同源 |
| etf_daily_adj | etf_daily_adj_incr：relay 优先、datahub 兜底，切片写到 data/v2/etf/raw/{fund_daily,fund_adj}/<d>.parquet | 是：**20261014 的 fund_daily 和 fund_adj 都是 datahub**（relay 不通时生产兜底确实发生过）；20261012/13/15/16 是 relay；更早 2857 个文件没有标签 |
| etf510300 | eng_daily_panels.etf510300：同一个 tushare_relay_pull 帮手，preferred=relay，datahub 兜底 | 代码路径与 etf_daily_adj 相同，兜底不是新源；但这张表没有逐日来源记录（panels/sh.510300.parquet、fund_daily_tushare_510300.parquet 都只有 pandas 键，没有 PANDAS_ATTRS；manifest.json 的 source=tencent_ifzq_fqkline 指历史底座），没有直接的 datahub 先例证据 |
| mid_large_universe | mid_large_universe_incr 只读本地（不联网） | 不适用 |

### 9.3 今晚走了兜底，来源能否记录
- marker：write_marker（L1096–1099）的 raw_file 项只有 path、exists、rows、sha256、date_range，**没有 source**。required_table 和 call_b_step 项也没有。
- 回执：只有 env_set 和 env_knobs_inherited，没有逐表来源。tier1_pull 的日志行（例如「daily 20261016 ok 5567」）也不打印来源。
- 能从文件元数据披露的（只读 schema）：
  - tushare_raw/{daily,daily_basic,adj_factor,stk_limit,suspend_d}/20261019.parquet：对应 daily_ohlcv_raw_pit、daily_basic、asof_ts；
  - data/v2/etf/raw/{fund_daily,fund_adj}/20261019.parquet：对应 etf_daily_adj。
  - etf510300 无法披露；mid_large_universe 不联网。
- v3.1 代码已冻结，不加字段。由 Data 例程回执补披露。

### 9.4 结论
- (1) **VERIFIED**：没有强制 SOURCE=relay，证据是文件标签加例程命令。附口径更正：tier1 生产是 datahub 优先。当晚环境本身没有落盘，属于记录缺口。
- (2) **VERIFIED**：六表中没有任何一张会因 false 引入新源。daily/daily_basic/asof_ts 的 datahub 本来就是主源；etf_daily_adj 的 datahub 兜底 20261014 在生产里用过；etf510300 与它同一代码路径，但没有逐日证据；mid_large_universe 不联网。
- (3) **NOT_VERIFIED**（marker 和回执都不记逐表来源）。6 张表里 5 张可以从文件元数据补披露，etf510300 无法披露。
- 建议：可以签 false，但要同时满足两条：
  - .ok 带下面两行整行注释；
  - Data 例程 R4 第六节第 1 条加一句：「回执须列出 tushare_raw/{daily,daily_basic,adj_factor,stk_limit,suspend_d}/20261019.parquet 与 data/v2/etf/raw/{fund_daily,fund_adj}/20261019.parquet 的 PANDAS_ATTRS source（pyarrow read_schema，只读元数据）；etf510300 来源未记录、按 relay 优先 datahub 兜底披露；另附驱动回执 checks.env_knobs_inherited.SOURCE，非空即报 P1。」
- .ok 披露机制：
  - parse_ok（L704–732）允许整行 # 注释（L719）；行内注释（值里含 #）会被拒（L725）；未知键会被拒（L729–730）。
  - 注释必须是 ASCII（L708–711），不能含 CR（L712），全文不能含 draft 字样（L714，不分大小写）。
  - 注释受 .ok 全长 sha 约束（marker ok_sha256，L1129），所以不能另加 note 键，只能用整行注释。这是对旧审「.ok 无注释」的有意例外。
- 建议 .ok 末尾追加的两行（逐字）：
```
# source_relay_only=false keeps the 10-15/10-16 production behaviour: driver sets no SOURCE; tier1_pull auto = datahub first then relay; etf_daily_adj and etf510300 = relay first then datahub; raw 20261015/20261016 PANDAS_ATTRS source=datahub (tier1), etf raw source=relay (datahub on 20261014)
# per-table source for 20261019 is NOT in marker or receipt; Data receipt must list PANDAS_ATTRS source of tushare_raw/{daily,daily_basic,adj_factor,stk_limit,suspend_d}/20261019.parquet and etf/raw/{fund_daily,fund_adj}/20261019.parquet; etf510300 source unrecorded; mid_large_universe offline
```

## §十 内存门槛：10-15 / 10-16 峰值证据、现状、机制与建议（主 Agent 16:17 ET 跟进）
- 写成 2026-10-18T16:24:15-04:00（ET）。只读：没有运行项目代码，没有读任何数据行，没有发信号（只读 /proc），没有建 .ok。
- 文件大小只用 ls/du 看。

### 10.1 10-15 / 10-16 夜更内存峰值：没有直接证据
- 查过的地方，都没有那两晚的 RSS 或 maxrss 记录：
  - logs/nightly/2026101[56]_*.log、*_run_*.out、*_summary.json（summary 只有 date/overall/steps/promotion_approved/finished）；
  - _recovery/data/nightly_20261019（没有 rss_*.log；驱动的 rss_<tag>.log 是 v3.1 才有，L499、L513）；
  - 本机没有 /usr/bin/time 输出，没有 rss 采样文件；
  - dmesg 无输出；/var/log 没有 kern.log 或 syslog，所以 OOM 无从查。
- **结论：10-15 / 10-16 各步峰值 RSS 没有记录，不能给逐步实测值。**
- 唯一相关的实测：logs/nightly/daily_basic_rebuild_20261014b.log L31「elapsed=70.27 maxrss_kb=2143204 exit=0」。
  - 这是 10-14 手工重建 daily_basic 的一次，跑的是 tier1_materialize.materialize_daily_basic：按年分批（L285–419），之后 _compare_daily_basic_files 按年比对（L207–245）。日志 L1 显示 3104 个文件，带「year … running_rows」和「history_diff year=…」，与 call B 的 daily_basic 步（nightly_update.py steps_for「daily_basic」）是同一个函数，只是现行版本多了 drop_duplicates（与 .bak_20261014_dupfix 的 diff）。
  - 10-15 / 10-16 的 daily_basic 日志只有行数（12304378 行），没有内存。
- **估计（不是实测）**，只用 ls/du：
  - daily_basic：约 2.1 GB（以 2143204 kB 为准）。原始 daily_basic 共 1.4G、3107 个文件；成品 daily_basic_full_tushare.parquet 745,129,744 B。
  - etf_daily_adj：etf_daily_adj.parquet 72 MB，整表读改写，估计数百 MB。
  - mid_large_universe：48 MB，同样估计数百 MB。
  - bars：每个文件小（daily_ohlcv_raw_pit 2.6 MB；panels 88M、5582 个，逐个追加），估计在 1 GB 以下。
  - daily_pull、eng_panels：主要是网络和小文件。
  - 所以那两晚的峰值应在 call B 的 daily_basic 步，约 2.1 GB（单进程）。

### 10.2 现状（/proc，16:19–16:23 ET）
- MemTotal 16,386,368 kB；SwapTotal 0（没有 swap）。
- MemAvailable 在 16:19:49 为 2,966,608 kB，16:22:57 为 4,899,936 kB，几分钟内波动约 1.9 GB。
- 94322（python3 scripts/acquire/remaining_after_stk_surv.py，PPID 94319 是 bash）：状态 **R**，VmRSS 5,304,716 kB，**VmHWM 7,254,388 kB**，没有子进程。
- SIGSTOP 不释放 RSS：05:30 时 94322 如果是 T，它的 5–7 GB 照样占着，除非它已经结束。另外它的 HWM 比现在高约 1.9 GB，只要还在 R 就可能再涨。
- 两个守卫都要求 94322 是 T 或已结束：驱动 guarded_check（f99dd11a L10）和 wrapper v4（L35、L39；运行中每 0.2 秒复核，L75，不满足即 rc 89）。**现在是 R，两边都会拒绝起跑。**

### 10.3 v3.1 f99dd11a / 兜底 559d1e01 能否表达内存门槛
- 驱动：
  - 有 RSS 停止线：RSS_STOP_KB=1484800（树合计，L85）、RSS_HARD_KB=1536000（单进程，L86），每 5 秒采样（L510–516），超线就停整棵树，FAILED，不可重试（RETRYABLE 只含 MAX_RUN，L117）。
  - .ok 的 rss_stop_kb / rss_hard_kb 必须等于这两个常量（L761–762），不能调。
  - **没有 MemAvailable 检查**（全文无 meminfo；只读 VmRSS，L258–263）。
  - .ok 未知键会被拒（L729–730），代码已冻结，所以只能放整行 # 注释（L719）。注释必须 ASCII、无 CR、不含 draft，见 §九。
- **已有但不在驱动里的门槛**：nightly_update.py L17–21 的 wait_mem() 在每个非 relay 步骤前（L113）检查 MemAvailable < 2.0（÷1e6，即 2,000,000 kB）。不足就每 60 秒暂停、无限等。
  - 在驱动下，等待会吃掉时间盒：daily_pull 30 分钟 MAX_RUN，call B 是预算和 16:00；结果是停树、FAILED。relaxed 档可能先重试一次 MAX_RUN。
  - 所以门槛不能低于 2,000,000 kB，否则就是带病硬跑。
- **新风险（P1，与内存门槛无关，但会决定今晚成败）**：
  - call B 的 daily_basic 步实测 maxrss 是 2,143,204 kB，高于驱动单进程上限 1,536,000 kB 和树合计 1,484,800 kB。
  - 按代码推断，call B 很可能在 daily_basic 步被 RSS 停树，结果 FAILED、不可重试，而且与 MemAvailable 多少无关。
  - 10-15 / 10-16 没有驱动、没有上限，所以那两晚成功不能证明今晚能过。
  - 代码已冻结，.ok 不能调这两个值。需要主 Agent 和 Data 决策：接受「call B 可能 RSS FAILED」，或另开一个版本。不能在本审内改。
- 兜底 559d1e01：
  - 只有在 DONE 和 FAILED 都不存在、并且有晚于 .ok issued_at 的 run_<STAMP> 目录时，才代写 FAILED（L13、L251–266）；否则退出 7、不写 marker（L16、L267–268）。
  - 它也没有内存逻辑。
- **不起跑时没有合法的 FAILED 路径**：
  - marker 只有两个写者：驱动 finish()（L1257，前置失败也会写，除非 no_write）和兜底（必须有起跑证据）。
  - 驱动会因为它自己的前置条件写 FAILED，例如 94322 不是 T/Z/不存在（guarded_check），但它不检查内存。
  - 为了拿到 FAILED 而故意让驱动在前置上失败（例如给错 .ok），不算合法做法，不建议。
  - 所以如果例程因为内存不足不起驱动：**没有 marker，兜底退出 7，paper 2a / r4.5 等不到 DONE 而阻塞**。
- 建议措辞：「未起跑 = P1、无 marker、paper 阻塞」，不要写成「判 FAILED」。

### 10.4 wrapper v4（6174eacb）怎么读 leaf25 .ok
- wrapper 本身不做严格解析：
  - 只算 .ok 的 sha（L25）；
  - okkey() 用 grep -qxE 匹配「allow_no_guard=true」或「allow_c5_ignore=true」（L23、L28、L30）；
  - 不拒未知键，不看注释。
- 但 leaf 进程自己会解析同一份 .ok：
  - ok_runner_pin.parse_ok（c7805d9a，L42–52）跳过 # 行，不拒未知键；
  - alpha_v1_1_runguard.read_ok_strict（35991407，L32–48）允许整行 # 注释（必须从第 1 列开始写 #）；其他行必须是 key=非空无空白值，不能有行内 #，不能有重复键；无 BOM、无 CR。ok_selfcheck（L69–95）只要求所有 allow_* 中除 allow_<mode>/allow_real_data 外都为 false，不拒其他未知键。
- 所以 mem_available_min_kib=2621440 这样的键能通过三处解析，但**没有任何代码读它，等于不生效**，还可能让人误以为有闸门。建议只写整行 # 注释，闸门放在例程启动前检查。
- wrapper 的内存线是 STOPKB=1484800（VmHWM，L11、L77），所以 leaf 峰值大约不会超过 1.48 GB。
- wrapper 没有 MemAvailable 检查。

### 10.5 门槛建议
- **夜更（10-19 05:30 ET 起跑前）：MemAvailable ≥ 2,621,440 kB（2.5 GiB）**。依据：
  1. 至少 2,000,000 kB，否则 nightly_update wait_mem 会暂停、时间盒到期后 FAILED（L17–21、L113）；
  2. 驱动下整棵树上限 1,484,800 kB（L85），留 1 GiB 余量需要 2,533,376 kB；
  3. 不受上限约束的历史峰值约 2,143,204 kB（10.1），2.5 GiB 仍留约 467 MB；
  4. 与 leaf25 同一条线，口径统一。
- MemAvailable 几分钟内能波动约 1.9 GB（10.2），所以要求在 30 秒内连读 3 次都达标。
- 这条只防 OOM，不能解决 10.3 的 daily_basic RSS 停树风险。
- **leaf25（今晚）**：同样 MemAvailable ≥ 2,621,440 kB（wrapper 停止线 1,484,800 kB 加约 1.09 GiB 余量），并且 94322 是 T 或已结束（不满足时 wrapper 返回 rc 89）。
- **leaf25 延后规则**：不满足就不起跑，每 10 分钟复查一次，记 DEFERRED_MEM（附 MemAvailable 三次读数和 94322 状态）；不向 94322 发任何信号；签发人定的最晚起跑时刻一过就不再起跑，顺延到下一个窗口，并且不能占用夜更 05:25–05:30 前的窗口。

### 10.6 Data 例程 R4 第三节（起跑前检查）建议加一句
「起跑前（05:30 ET）间隔 15 秒连读 3 次 /proc/meminfo，MemAvailable 须每次都 ≥ 2621440 kB；任一次不达标即不起驱动、不硬跑、不向 94322 / 94403 发任何信号，回执记三次读数、94322 的 State/VmRSS 与 ps 快照，按『未起跑 = P1、无 marker、paper 阻塞』上报（兜底此时会退出 7，不代写 FAILED）；达标才起驱动，并在回执附 driver 回执中各次调用的 rss_max_sum_kb / rss_max_one_kb。」

### 10.7 夜更 .ok 建议追加的两行（ASCII，整行 #，不含 draft、无 CR）
```
# mem gate (Data routine pre-start, not enforced by driver f99dd11a): start only if /proc/meminfo MemAvailable >= 2621440 kB on 3 reads 15 s apart at 05:30 ET; nightly_update wait_mem pauses below 2000000 kB; driver RSS stop 1484800 kB tree / 1536000 kB one process
# if MemAvailable < 2621440 kB: do not start the driver, no hard run, no marker (fallback exits 7), report P1 nightly not started and paper blocked; never signal 94322 or 94403
```
### 10.8 leaf25 .ok 建议追加的两行（ASCII，整行 # 且从第 1 列开始；不要写成键）
```
# mem gate (routine pre-launch, not enforced by wrapper v4 6174eacb or runguard 35991407): launch only if MemAvailable >= 2621440 kB on 3 reads 15 s apart and pid 94322 state T or exited; wrapper stopline 1484800 kB
# if not met: do not launch, recheck every 10 min, record DEFERRED_MEM with readings and 94322 state, never signal 94322; no launch after the latest launch time set by the signer
```
