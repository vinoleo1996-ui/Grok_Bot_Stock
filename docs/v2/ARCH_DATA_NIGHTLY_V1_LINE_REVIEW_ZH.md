# Arch 行级审查：Data 10-19 日更驱动 run_nightly_v1（新版 63b5a884）与兜底 routine_fallback_v1

- 审查人：QuantLab Arch；写成时间 2026-10-18T13:13:44-04:00（ET，date 生成）。
- 方法：只读静态审查，草稿目录 /tmp/arch_nightly_review2。没有运行驱动或兜底，没有读取价格、收益、权重、因子、财务数值，没有在 repo 里 git apply。
  - 读过的元数据：/proc/94322、/proc/94403 的 stat 与 cmdline；paper_import_closure.json 里的路径名（只当文本读）；几个步骤脚本的源码。
  - pgrep 正则只拿假命令行字符串在 /tmp 里用 grep -E 测过。
- 对照基准：Arch 设计审 2dada5ed（17 项清单、P0-1/P0-2/P1-1..7/P2）；主 Agent 与 Arch 在 12:24–12:40 之间的各条裁定（call B 预算 75、兜底恢复条件、94322/94403、tier1_pull 5b70dfed、超时、pgrep、.ok 解析、成功判据、RSS、禁跑时段）。
- 本文**不是 .ok**，没有签发任何 .ok。

## 0. 审查对象（sha256 全部逐个重算并与申请一致）
| 文件 | sha256 |
|---|---|
| docs/v2/audit/nightly_20261019/run_nightly_v1.py（1423 行，原地替换；真实路径就是这里，不在 scripts/） | 63b5a88462f9f75ae7975f52320bbd6f88433cdf4857bf95c6de557d6d880e16 |
| docs/v2/audit/nightly_20261019/routine_fallback_v1.py（161 行） | f3244472da360b74cc692f90548fab4f8839f13f3938bf65374d592b2d61ac5f |
| DRIVER_DIFF_vs_predraft2_20261018T130216.diff | 12727b8fa591c0705f25439a416a3bc5503a655e9b199c0ae6a55e3780fcba87 |
| DRIVER_DIFF_vs_predraft2_20261018T130216_ZH.md | a7c79601839c31a68a384e00214e7e3afa92b910b02c4fe2b76f4446df93b02a |
| DRIVER_TEST_RECEIPT2_20261018T130216_ZH.md | 369b674de4c17e903757605637df106adce739c8cb62227d7b5ccd3f8f29c4dd |
| ROUTINE_PROMPT_DRAFT_ZH.md | 02498e1e478f23d4f8060e38e6ae533678f91ad66e1ac9a0f78f1d15c7e2eb41 |
| ROUTINE_DIFF_ZH.md | ad79a7b008a22a42be15d7b907c718ab4c5299ad4f705715d42ca0684f7bbaba |
| NIGHTLY_20261019_OK_REQUEST_ZH.md | e5fc9fc4425c1df79b68b78b1ca836e97100186fad1e2e09de2f230d3dd7278f |
| docs/v2/tickets/TKT_tushare_proxy_connect15_20261018.md | d19e47f690c070dd75c0ef4fd4bab213e001af99cb4abd51eeac145a992a27a8 |
| scripts/acquire/tier1_pull.py | 5b70dfed08a237034b586ef9738e2c1b81607b20387a62df49a1e6994ba711cf |

- 归档：_recovery/data/nightly_20261019/predraft2_20261018T114300/ 和 predraft3_20261018T125243/ 两处的 SHA256SUMS 都已用 sha256sum -c 逐行核过，全部 OK。旧驱动 a7292a61 在里面。
- 驱动里 SHA_KEYS 列的 20 个钉值都与磁盘一致（scope 04d716af 和 tier1_pull 5b70dfed 单独核过）。

## 1. 结论：PASS_WITH_CONDITIONS
- 新版逐项落实了设计审的 17 项清单（见第 3 节）。没有 P0。
- 有 3 项 P1，集中在兜底脚本和 94322 进程树的前置条件；另有若干 P2/P3。
- 签发路径（二选一，由主 Agent 定）：
  - **A（推荐）**：Data 交 v3.1 小改（只动第 2 节 P1-1..3 加 P2-1、P2-2；hsgt 和中转步骤按第 4 节裁定），重跑 T01–T19 并补 T20–T23（第 5 节）。Arch 做增量 diff 复核后，按新 sha 签。
  - **B（保底）**：如果 v3.1 到 17:00 ET 还没交，就签现版 63b5a884 / f3244472。P1 项改由例程文字和 Arch 例程补位（第 6 节 B 方案条件）。
- 签发不受代码阻塞。但**运行**有三个硬前提要在 10-19 05:25 前了结，见第 7 节：94322 当前是 S 状态；中转步骤 partial 默认判 FAILED；relaxed 档与重试次数的决定。

## 2. 行级发现
### P0
- 无。

### P1
- **P1-1 兜底脚本代写 FAILED 前，没有任何「驱动确实起跑过」的证据**（routine_fallback_v1.py L133–145）。只要 pgrep 为空且没有 marker，它就写 FAILED reason=driver_killed。
  - Data 自己的例程只在驱动命令结束后才调它（ROUTINE_PROMPT_DRAFT 第五节），这时没问题。但设计审 D-P0-2 要求 Arch 的 06:00–16:40 每 20 分钟例程也能调它。那个例程如果在驱动起跑前（例程晚开）调用，或者在 check-only 和正式运行之间调用，就会凭空写 FAILED，当天纸面直接停。
  - 修法：只有同时满足「run_root 下存在 run_<STAMP> 目录，且 STAMP 晚于 .ok 的 issued_at」才写 FAILED；否则退出新码 7（no_run_evidence），只报不写。
- **P1-2 兜底的 pgrep 范围不够**（routine_fallback_v1.py L22、L112–115）。现在只认 run_nightly_v1 / nightly_update / tier1_pull，认不出 call B 的步骤脚本，比如 scripts/acquire/tier3_daily_snapshot.py，或者 python -c 形式的 import tier1_materialize。主 Agent 的裁定是「驱动和子进程都不在」才可恢复。
  - 修法：再加两条锚定、括号转义的模式：`(^|[ /])[s]cripts/acquire/[A-Za-z0-9_]+\.py( |$)` 和 `[i]mport tier1_materialize`。
  - 注意：13:09 ET 实测 94322 的 cmdline 是 python3 scripts/acquire/remaining_after_stk_surv.py，会命中第一条。所以必须按 PID 排除 94322 和 94403，而且只在它们是 T 状态时排除（读 /proc/<pid>/stat，进程级）。
- **P1-3 受保护进程只核了 PID 本身，没核整棵进程树**（run_nightly_v1.py L399–421）。主 Agent 的裁定是：94322 / 94403 的整棵树都必须是 T，或者都不存在，按进程级 /proc/<pid>/stat 判定。
  - 修法：对每个 GUARDED PID 用 descendants() 枚举，每个后代的 stat 都必须是 T、Z 或不存在，否则前置失败，并把明细记进 R.checks.guarded。永不发信号。
  - 13:09 ET 实测：94322 是 S，没有子进程；94403 不存在。实际风险低，但这是裁定原文的要求。

### P2
- **P2-1 收尾 sha 不符时不恢复**（L1320–1321，对应 Q-4/B7）。sha 等于 141078fa 就足以证明恢复到位（字节完全相同）；但不符时现在直接退出 4，不走恢复链。
  - 修法：不符时先跑 compare_restore("final")，再判 FAILED。恢复成功退出 1，恢复失败退出 4。
- **P2-2 PPID=1 可疑孤儿只记录，不挡 DONE**（L371–378、L509–517；成功判定在 L1240、L1296、L1322）。一个启动时间晚于本次调用、cmdline 含 scripts/acquire 的游离进程可能还在写产物，驱动这时写出 DONE 就是错的。
  - 修法：call A 或 call B 只要有 logged_only 孤儿，就 fail，reason_code=ORPHAN。仍然不发信号（对应 Q-6a）。
- **P2-3 中转专用步骤一律判 FAILED。** 代码里 RELAY_ONLY（L74）定义了但没用，check_summary（L546–570）对 hsgt/cyq/tier3 的 partial 与 skipped 一律判失败。
  - 10-14 到 10-16 三个夜里 cyq 或 tier3 每晚都是 partial（中转快速失败）。照现规则，10-19 很可能 FAILED，纸面停。
  - 这是决定项，不是代码缺陷，裁定建议见第 4 节 Q-3 / Q-E1。
- **P2-4 兜底在 sha 不符时会被重复调用，违背「不重试」**（routine_fallback_v1.py L154–155；例程第五节只对退出码 6 才重跑，但 Arch 的 20 分钟例程会反复调）。另外，DONE 已存在而 sha 不符时它也会恢复（L118–129）。
  - 修法：(a) 启动时如果发现本日已有一份兜底回执，且其中 restore.ok=false 或退出码为 5，就退出 5，不再动手；(b) DONE 已存在且 sha 不符时只报 P0，不恢复。

### P3
- P3-1 docstring L15 写着「SOURCE=relay 固定」，与实现（L100、L427、L706：只有 .ok source_relay_only=true 才设）不符。改文档即可。
- P3-2 两个已知的重复记录：reason_codes 记两次 SIGNAL（stop_tree L342 和统一收尾 L1394 各记一次）；residual 同一 PID 出现两次（stop_tree 的 residual 与孤儿扫描 acted 在 L510 合并）。**只影响展示，不影响判定**，因为任何残留都已判 FAILED。建议写 marker 前按 pid 和 code 去重，并保留原始计数。
- P3-3 compare_restore 发现进程树还在时（L869–872）直接返回 ok=False，结果是退出 4「日历未恢复」。即使 sha 仍等于 PIN 也是这样，误报 P0。建议这种情况记 RESIDUAL 和当前 sha：sha 等于 PIN 时退出 1 加 P0 告警，不等于 PIN 时才退出 4。
- P3-4 冻结件只在 FROZEN（L41）核 closure 6919e7af。sw_l1_pit 89d4afa3 / 87d769aa 和 sw_pit 0b1d3432 只靠快照 compare 事后兜底。建议加进 FROZEN，cal_shas 的前后核对就能覆盖（不需要 .ok 键）。
- P3-5 审计工具调用（L884、L890、L1208、L1314–1316）没有传 phase_deadline，所以只受「工具默认值」和「距 16:40」约束。可以接受，因为 call B 最晚 16:00 停，到 16:40 之后会以 TOOL_TIMEOUT 收尾成 FAILED。记录在案。
- P3-6 兜底的 ok_flag（routine_fallback_v1.py L60–69）只认那一个键，不核 .ok 的 sha 和有效期；restore_atomic（L72–87）恢复前不留存被改写的文件。建议恢复前把当前文件复制进 run 目录（O_EXCL），再做替换。
- P3-7 parse_ok（L633）允许整行 # 注释。Arch 签发的 .ok 不会带注释，不影响。
- P3-8 测试覆盖：端到端用例把审计工具（cal_restore_v2、快照）换成了假函数，所以真工具的串联没有端到端测过。可以接受，因为 10-18 的工具自测已另行覆盖。

## 3. 设计审 17 项清单与各条裁定的逐项核对
| 项 | 结论 | 证据（行号） |
|---|---|---|
| 1 时间盒：30 分钟两档；call B min(起跑+75, 16:00)；不跨 16:40 | 符合 | L86–88、L1228、L1278–1289、L495 |
| 主 Agent：起跑+75 ≤ 16:00（最晚 14:45 起跑），否则 FAILED；超时停树、FAILED、恢复、核 141078fa；超时绝不 DONE | 符合 | 闸门 L1278、停 L1289（CALLB_TIMEOUT）、L1292–1302 恢复与判失败、L1322 |
| 2 停树顺序、确切 PID、cmdline+PPID；call A 认 scripts/acquire/，call B 认完整相对路径 | 符合（父进程是 SIGSTOP 后 SIGKILL，不发 TERM；父已冻结，可接受） | L297–343、L103–109 |
| 3 全部超时；BaseException 加信号处理；统一收尾 | 符合 | L434–466、L502、L1365–1419 |
| 4 reason_code；只有 MAX_RUN 可重试 | 符合 | L111、L1242–1252 |
| 5 超时 file:line；TSPRO_RELAY_TIMEOUT=115；SOURCE 默认不设；tushare_proxy ae91f230 不改 | 符合 | L100、L427、L706；钉 L57；说明文档第 2 节 |
| 6 自测 19/19 | 符合（缺口见 P3-8 和第 5 节新增用例） | RECEIPT2 |
| 7 恢复前确认树已不在；每次尝试后、call B 后、异常路径都恢复；双核 | 符合（收尾处见 P2-1） | L522–526、L864–904、L1232、L1298、L1409 |
| 8 备份两份 sha 加 chmod 444 | 符合 | L1190–1198 |
| 9 兜底 | 部分符合（P1-1、P1-2、P2-4） | routine_fallback_v1.py |
| 10–12 .ok 解析：key=value、ASCII、LF、无行内注释、无重复或未知键、无 DRAFT、拒 _consumed/、全部 sha 键必填、live=false、promotion=false、有效期带时区、issued_at 不晚于当前 | 符合；单次使用靠 marker 预检（L1043–1059）加 Arch 归档实现 | L614–710 |
| 13 实测判据：行数、trade_date min=max=D、只认本次窗口、YYYYMMDD、rc=2 不算 ok | 符合 | L926–969、L546–570、L601–610、L1327–1362 |
| 14 pgrep 锚定并括号转义；不命中 tier3_daily_snapshot.py 和 nightly_sha_scope_snapshot_v2_* | 符合（/tmp 里 grep -E 测过：两者都不命中，nightly_update / remaining_after_stk_surv / run_backfill 都能命中） | L94–96、L790–800 |
| 15 全部钉值、解释器、ET 日期 = D 且 ≥ 05:25 | 符合 | L713–732 |
| 16 RSS：树合计 ≥ 1484800 停，单进程 > 1536000 停 | 符合 | L79–80、L493 |
| 17 不跑 sw 和 trade_cal 步骤，不带 --force，不删文件 | 符合 | L72–73；全文没有 --force |
| tier1_pull 5b70dfed；call A 设 TIER1_SKIP_CAL_REFRESH=1；完整恢复链保留 | 符合 | L48、L101、L591–598；tier1_pull L83–85 跳过、L92–96 原子写 |
| 94322 / 94403 永不发信号；fund_portfolio 写路径不重叠 | 不发信号：符合（L98、L299）；树：见 P1-3；重叠：rg 在整条 nightly 链里 fund_portfolio 零命中，也不写 output/markers | — |
| 16:40–18:40 不跑 | 符合 | L167–169、L1162、L495 |

## 4. 待决问题裁定（建议）
- **Q-1 退出码**：维持现实现。0 = DONE；1 = FAILED；2 = 前置失败；3 = marker 写入失败；4 = 日历未恢复；10 = check-only 通过；11 = 正式运行的统一异常收尾（信号、异常、工具超时）。
  - 设计审里「exit 10」的写法作废，统一异常收尾以 11 为准。
  - 实现上 check-only 失败退出 2（L1166、L1172；check-only 中途异常也是 2），不会写任何文件。例程规定「非 10 一律不跑正式命令」，这样是对的。
- **Q-2**：确认。relaxed 只有 MAX_RUN 可以重试；rc≠0、原始文件不合格、summary 不符（ATTEMPT_FAILED）、RSS、HANG、残留，一律不重试。
- **Q-3 hsgt**：
  - 核查结果：paper_import_closure.json 的 156 条全是代码路径，没有任何数据路径；其中只有 quantlab/portfolio/research_loop.py 在 L115 出现字符串 northbound_flow，那是 alpha 标签别名，不读数据；REQUIRED_TABLES（research_loop.py L633）不含 hsgt。所以 **hsgt 不是纸面输入**。
  - 另外，fill_hsgt_top10_extend.py 的 needs() 用 700 字节当门槛（L46），源端空日只会存下小文件，remaining 就不会归零（10-14 remaining=3）。10-19 在上海 17:30 起跑，当天数据可能还没发布，风险更大。
  - 建议裁定：fail=0、没有 ABORT、而且剩余天数都能拿出 HTTP 200 加 0 行的证据（本次日志段里有 <d>:ok:0 一类记录），就判 hsgt=source_empty，记 WARN 并登记补拉队列，不判 FAILED；fail>0、ABORT 或 rc=3，仍判 FAILED。
  - 需要改 check_hsgt_log（L601–610），并加 .ok 键 allow_hsgt_source_empty_warn_20261019（默认 false）。主 Agent 不同意的话，就维持现在的 remaining=0 严格规则，接受这项风险。
- **Q-E1（中转专用步骤 cyq / tier3 / hsgt 被 RELAY_DOWN 快速失败）**：建议 Eng 和主 Agent 在签发前给出书面决定。
  - Arch 建议放行：这三个步骤不是纸面输入；data_freshness_status.py 把 cyq / tier3 放在 warn_tables，注释写明「NEVER affects overall」；nightly_update 会把它们登记进补拉队列。
  - 放行时状态记 degraded（marker 不得出现 skipped 字样），并加 .ok 键 allow_relay_partial_20261019（默认 false，需代码支持，用上 RELAY_ONLY L74）。
  - 不放行，就接受 10-19 很可能 FAILED（近三夜每晚都有中转步骤 partial）。
- **Q-4 / B7**：sha 等于 141078fa 足以证明恢复（每次调用后已经跑过完整链）。sha 不符时必须恢复，按 P2-1 修。
- **Q-5 / B8 独立 PIN 备份**：10-19 不强制。备份在跑前就核过与 PIN 两次相同，并且只读；兜底只认 sha 等于 PIN 的 run 备份。独立副本只防 run 目录丢失，收益很小，不阻塞签发。
- **Q-6**：
  - (a) 孤儿：同意不发信号，但必须挡住 DONE（P2-2）。
  - (b) summary 已核：nightly_update.py L131–137 把本次 res 合并进旧文件后整份重写；本次选中的步骤都会被本次结果覆盖（只有中途崩溃时才不写，那时 finished 和 mtime 落在窗口外，判失败）。驱动只检查本次调用的步骤（call A 只看 daily_pull，call B 看 14 步），并要求 finished 和 mtime 都落在本次窗口内（L555–562）。所以过滤到本次运行这一点**成立**。
- **Q-7 94322**：驱动永不发信号。主 Agent 必须在 10-19 05:25 前决定：要么由 94322 的属主等它自行结束，要么由 Arch 另签一张按确切 PID 发 SIGSTOP 的 .ok（核 cmdline）。否则驱动在前置检查失败，写 FAILED，当天纸面停。
- **relay_outage_backfill 是否放宽**：不放宽。保持「T 或不存在」。
- **Data 披露事项**：
  - (1) 原地替换正式文件：可以接受。旧版已经归档，两份 SHA256SUMS 都核过，而且旧版从未签发、从未运行；文件名固定是 Eng pgrep 的要求。
  - (2) 对自己的 /tmp 测试目录 rm -rf：没有越界，不影响 repo。以后请改成「留存」或「在回执里列出被删路径清单」。
  - (3) 只读 grep 里用了管道：没有问题，规则禁止的是用 heredoc 写中文文档。

## 5. v3.1 必须补的自测用例（只用 /tmp 假进程）
- T20：兜底在没有 run_* 目录时退出 7，不写 marker（P1-1）。
- T21：驱动和 nightly 被 KILL 后，只剩一个孤立的步骤脚本，兜底退出 6（P1-2）。另一用例：94322 的替身处于 T 状态时，兜底被正确排除。
- T22：GUARDED 的替身本身是 T，但它的子进程是 S，前置检查失败（P1-3）。
- T23：call B 结束后出现 PPID=1 孤儿，判 FAILED（P2-2）；另测收尾时 sha 不符，先恢复再判 FAILED（P2-1）。

## 6. 建议签发的 .ok 完整内容（key=value，LF，无注释；签发时由 date +%Y-%m-%dT%H:%M:%S%:z 填 signed_et 和 issued_at；os.link 独占创建）
依赖决定的键如下，正文里不写注释：
- sha_driver、sha_routine_fallback：A 方案换成 v3.1 的新值；B 方案用下面的现值。
- allow_profile_relaxed_20261019 与 allow_daily_pull_retry_20261019：主 Agent 已定「重试最多 2 次、间隔 ≥ 30 分钟」，建议 true 和 2；主 Agent 改选 strict 的话，就是 false 和 0。
- source_relay_only：建议 false。
- allow_relay_partial_20261019、allow_hsgt_source_empty_warn_20261019：只有 v3.1 支持、并且主 Agent 同意时才加；**现版驱动会把未知键当错误拒跑，B 方案不能写这两个键**。
- expires_et：建议 2026-10-19T16:00:00-04:00。call B 最晚 14:45 起跑，16:00 足够，比申请样例的 16:40 更紧。

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
sha_driver=63b5a88462f9f75ae7975f52320bbd6f88433cdf4857bf95c6de557d6d880e16
sha_routine_fallback=f3244472da360b74cc692f90548fab4f8839f13f3938bf65374d592b2d61ac5f
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
allow_run_daily_pull_20261019=true
allow_run_call_b_20261019=true
allow_restore_trade_cal_20261019=true
allow_write_nightly_marker_20261019=true
allow_routine_fallback_restore_20261019=true
allow_quarantine_mv_daily_raw_20261019=true
allow_create_research_quiet_lock_20261019=true
allow_profile_relaxed_20261019=true
allow_daily_pull_retry_20261019=2
source_relay_only=false
```
- 驱动内部写死、不进 .ok 的数据钉值，供核对：PIT 日历 fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41；manifest 7ccc911e8a3ed2e408f30db1f95f12eb71a6fea18003ba88a31246f941cc89a4；sw_l1_pit 89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c、87d769aaca06212186986af489f6507b6f0d98c8937f7a4476f97538562733b3；sw_pit 0b1d3432e30f7cdd907df393299cd2f552e1121899239985a00113c4dfcd89f6（后三者在快照范围 04d716af 里属于 MUST_NOT_CHANGE）。
- 签发前在签发时刻重算全部 sha。任何一处不符都不签。
- B 方案的补位条件（写进两份例程）：
  - (1) Arch 的 20 分钟例程只在 run_* 目录存在、驱动和 nightly 都不在、并且 `pgrep -af "(^|[ /])[s]cripts/acquire/[A-Za-z0-9_]+\.py( |$)"` 除 T 状态的 94322 外为空时，才调兜底（对应 P1-1、P1-2）；
  - (2) 05:25 前由例程只读核 /proc/94322/task/*/children，每个子进程都必须是 T 或不存在（对应 P1-3）；
  - (3) 兜底退出 5 之后当天不再调用（对应 P2-4）。

## 7. 18:00 ET 前签发的阻塞判断
- 代码：不阻塞。A 方案要求 v3.1 在约 16:30 前送达，Arch 增量复核约需 30 分钟；赶不上就走 B 方案。
- 必须由主 Agent / Eng 在签发前给出的决定：
  - (1) relaxed 档与重试 2 次（建议同意）；
  - (2) Q-E1 中转步骤是否放行（不放行，FAILED 风险高）；
  - (3) Q-3 hsgt 源端空日是否按 WARN 处理；
  - (4) source_relay_only（建议 false）。
  - (2) 和 (3) 如果选「放行」，就只能走 A 方案（需要代码支持新键）。
- 运行前提（不阻塞签发，但阻塞运行）：94322 在 10-19 05:25 前必须是 T 或已退出（13:09 ET 实测是 S，没有子进程）；Arch 05:25 设 RESEARCH_QUIET.lock；10-19 16:40–18:40 不跑。
