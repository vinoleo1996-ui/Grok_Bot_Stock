# Arch 设计级审查：Data 10-19 日更驱动 run_nightly_v1 与 run .ok 申请

- 审查人：QuantLab Arch；写成时间 2026-10-18T12:30:37-04:00（ET，date 生成）。
- 范围：主 Agent 12:25 ET 改为**设计级审查**。Data 说明 a7292a61 是旧版（缺 runner 修订），新版本今天下午提交。本文只裁定设计、待决问题和新版必须满足的清单，不对 a7292a61 做逐行结论。文中引用的 a7292a61 行号只用来说明设计问题在哪里，不是行级发现。
- 方法：只读静态审查，全部草稿工作在 /tmp/arch_nightly_review。没有运行驱动，没有读取价格、收益、权重、因子或财务数值，没有在 repo 里 git apply。只读过的元数据有三类：tushare_raw 各目录的文件名清单、logs/nightly/2026101{4,5,6}_summary.json 里各步的 status/sec、冻结文件的 sha256。
- 本文**不是 .ok**。没有签发任何 .ok。

## 0. 审查对象（sha256 已逐个重算）
| 文件 | sha256 |
|---|---|
| docs/v2/audit/nightly_20261019/run_nightly_v1.py（旧版，876 行） | a7292a616fede1deda8c88df064c015064073c5c72abb7ba691d1bf30896c5fa |
| docs/v2/audit/nightly_20261019/NIGHTLY_20261019_OK_REQUEST_ZH.md | 9da130492706d15491e8cf15f39b55bc0e4f10cca5324a631d938562dfa4f4f7 |
| docs/v2/audit/nightly_20261019/ROUTINE_PROMPT_DRAFT_ZH.md | 1d372ced090170a5b3ea608600ebae5718afa064269e488083e794605142f8ee |
| docs/v2/audit/nightly_20261019/ROUTINE_DIFF_ZH.md | 6b4efc98ebadf910e61677b25ba5d3b2e8ecf410bef76cb5e7b6b9af6cd3410c |
| docs/v2/audit/nightly_20261019/ROUTINE_A_CURRENT_20261018.txt | a95cda62964104f5b21ea8f150b85cc4d1fafff84bb64e08f0981620c2a74b45 |
| docs/v2/audit/nightly_20261019/cal_restore_v2.py | 6686876bdcfc95f11d493b5201f55eb726e69e4894d8c96bfaf46ab1748387a4 |
| docs/v2/audit/nightly_20261019/cal_compare_v1.py | 74093ff3be4c431bab8c469307b207b43b8e1cff707dd0bac1319a7e265cddfc |
| docs/v2/audit/nightly_sha_scope_snapshot_v2_20261018.py | c930ed5c627bf937e6b5d139c52f18945f045286e78dba66cbe5adfab92ab79a |
| docs/v2/audit/nightly_20261019/nightly_sha_scope_20261019.txt | 04d716af2a87a8bf365431c97097a5c740353c6c273de82677d826f1c4d98807 |
| scripts/nightly_update.py | ec079d56912aea8a4358a7ae97a73a3ad6ee3df34e83845ad4d655d31d838636 |
| scripts/acquire/tier1_pull.py | b630bca24fe7c86a656cf375c4aa1f543d98dac86178ba7ae50881cf4dbeb711 |

## 1. 结论
- **设计层面：PASS_WITH_CONDITIONS。** 整体方向可行：单驱动串行、每次尝试后都原子恢复日历、只写一个 marker 且放在最后、隔离后再重试、快照前后对比。但下面 6 项 P1 设计缺口必须在新版里补上，2 项 P0 级别的兜底必须做到。
- **a7292a61：不可签（作废，等新版）。** 新版须先通过第 5 节清单的行级审查，Arch 才签 run .ok。
- 待决问题的建议裁定见第 4 节：**06:20 与 06:30 两个 strict 值都不保留**（两者本身互相矛盾）；Q-A2 **不同意**（call B 超时必须判 FAILED 并停）；Q-A3 **有条件同意**。

## 2. 设计级发现（P0–P3）
> 行号指 a7292a61 或被调用的文件，只用来定位设计问题。新版按第 5 节逐条核对。

### P0
- **D-P0-1 异常、信号、驱动自身挂起都没有兜底路径。** run_nightly_v1.py main（L666–830）没有顶层 try/finally，也没有 SIGTERM/SIGINT/SIGHUP 处理。run_tool（L260–264）调 subprocess.call 不带超时，run_nightly（L289）的 p.wait() 也不带超时。
  - 后果：驱动一旦被杀或崩溃，nightly_update / tier1_pull 会变成孤儿继续跑；trade_cal 可能停在被 tier1_pull 重写过的状态（tier1_pull.py L92 是直接 to_parquet，不是原子写，中途被杀会留下截断的文件）；而且不会写 marker。这违反已定计划里「挂起、异常、信号一律写 FAILED，纸面停」。
  - 要求：顶层 try/except BaseException，加上信号处理，统一走一条收尾路径：停整棵子进程树 → 只要已经做过备份，就跑恢复链并双核 sha → 写回执 → 写唯一 FAILED → 退出（新版的 exit 10 可以用在这里）。所有子工具调用和 wait 都必须带超时。超时本身也走这条收尾路径。
- **D-P0-2 驱动外没有日历兜底。** 如果驱动被 SIGKILL（信号处理接不住），没有任何机制恢复 trade_cal。
  - 要求：06:00–16:40 每 20 分钟的例程增加一条检查：驱动 PID 已不在、又没有 marker、trade_cal 的 sha 不等于 141078fa → 立即发 P0 给主 Agent 和 Arch。是否允许例程用 run 目录里的备份调 cal_restore_v2 自动恢复，由 .ok 的一个显式键决定（建议 allow_routine_fallback_restore_20261019=true，只限钉住的 cal_restore_v2 加上 sha==PIN 的备份）。不管恢复与否，都要写 FAILED（例程代写，并在 marker 里注明 writer=routine_fallback）。

### P1
- **D-P1-1 call B 超时只告警、不停也不判失败**（L800 的停止时刻是 16:40，L808–809 超时只记 P1）。这与已定计划「call B 必须在起跑 +55 分钟内且不晚于 16:00 完成，超时写 FAILED」冲突。裁定见 Q-A2。
- **D-P1-2 strict 档没有 30 分钟的单次硬停**（PROFILES L72：daily_pull_max_min=None，只有 06:20 墙钟）。从 05:30 起跑，strict 实际给了 50 分钟，违背「daily_pull 30 分钟硬停」。另外 06:20 和 06:30 两个值互相矛盾，见 Q-A1。
- **D-P1-3 停止顺序不对。** stop_tree（L237–252）没有先 SIGSTOP 父进程，就直接 TERM 子进程。nightly_update 会因此认为当前步骤结束，进入下一步、再起新的子进程，而这个新子进程不在已经枚举好的名单里。代码里 parent=None，没有核 PPID。call B 的匹配串只用了 "scripts/"（L800），过宽。子进程退出后如果还有残留，L294–295 只告警，没有记 fail。
  - 要求顺序：核父进程的 cmdline 后 SIGSTOP 父进程 → 重新枚举整棵树 → 对每个后代先 SIGSTOP 冻结 → 从最深一层开始 TERM（同时 CONT）→ 带超时等待 → 还活着就 KILL → 最后处理父进程 → 再枚举一次，做孤儿扫描（PPID=1 且 cmdline 匹配的只记录、只报）。只发给确切 PID，每次都核 cmdline 和 PPID。任何残留都算 FAILED。
- **D-P1-4 成功判据在设计上还依赖「状态」，没有依赖「实测」。**
  - (a) marker 里四个原始文件的 date_range 被硬编码成 [D, D]（L550），根本没有实测，这属于不得造数。
  - (b) nightly_update 用 --steps 跑子集时会把结果合并进当天已有的 summary（nightly_update.py L131–135）。驱动在 L834–848 直接读这个 summary，没有核对每条记录是不是本次 call B 写的。nightly_update 被停的话根本不会写 summary，这时读到的是旧内容。daily_update_status 和 freshness 也没有核生成时间是否晚于 call B 起跑。
  - (c) L858–863 用字符串比较 last_date，两种格式会混淆：如果状态文件写的是 YYYYMMDD，"20261016" >= "2026-10-19" 会被判为真。必须先统一成 YYYYMMDD 再比较，并且要求等于 20261019，不是大于等于。
  - (d) nightly_update 把 rc 0 和 rc 2 都记成 ok（L119–120）。hsgt 的 rc=2 意思是「还有剩余没拉完」，会被当成完成。
  - 完整的判据设计见第 3 节。
- **D-P1-5 .ok 的格式和校验设计不合 Arch 规则。** 申请 §3 用的是 "key: value"，还带行内 # 注释和非 ASCII 的 allow_kill 值。驱动只在 sha 键存在时才校验（L333–339，缺键就放过）；date 键可以缺省（L325）；没有拒绝 _consumed/ 路径和 DRAFT 文本；live、promotion_approved、signed_by、issued_at 都不校验。新版要求见第 5 节 C 组。
- **D-P1-6 被调用的整条链没有钉住。** .ok 只钉了 nightly_update 和 tier1_pull。nightly_update 实际还会调用 11 个步骤脚本，tier1_pull 还用到 tushare_proxy / relay_health，这些都没有钉。范围文件 04d716af 也不覆盖 scripts/。审查之后到运行之前，任何改动都发现不了。全长 sha 列在第 6 节，新版驱动启动时必须逐个核。
- **D-P1-7 例程第一节与「一次一个真实数据进程」冲突。** 例程草稿 §一沿用旧规则：94322（remaining_after_stk_surv.py）如果是 T 状态，就 SIGCONT 让它继续。可叶 23 的 .ok 10-19 04:30 ET 到期，05:30 再继续它等于无 .ok 运行，而且会和日更并发（RSS 叠加，违反单真实数据进程规则）。Arch 12:16 的证据显示 94322 仍是 Ssl。
  - 要求：删除 §一里的 SIGCONT。改成：05:25 时 94322 只要还活着（不论什么状态），驱动的前置检查就失败，并报 P0 给主 Agent 和 Arch。是否在 10-19 04:30 之后按确切 PID 停 94322，由 Arch 单独签 .ok，这件事要在 10-19 05:25 之前了结。

### P2
- **D-P2-1 pgrep 前置条件**（L69：kline.py|export_static.py|snapshot.py|gen.py）没有转义，也没有锚定，会误命中 tier3_daily_snapshot.py 和驱动自己调用的 nightly_sha_scope_snapshot_v2_*.py。误命中会导致驱动拒跑、纸面停一天。另外它不覆盖其他真实数据进程。
  - 建议改成：`pgrep -af "(^|[ /])([k]line|[e]xport_static|[s]napshot|[g]en)\.py( |$)"`
  - 另加一条：`pgrep -af "(^|[ /])([r]emaining_after_stk_surv|[n]ightly_update|[t]ier1_pull|[r]un_backfill_[a-z0-9_]+)\.py( |$)"` 也必须为空（驱动自己起的 NPID 及其后代在起跑前不存在）。
- **D-P2-2 重试判定用中文子串匹配**（L775 匹配「截止」或「16:40」），RSS 超线被停在 relaxed 档会被当成可重试。要求改为结构化的 reason_code（MAX_RUN、WALL_CUTOFF、BLACKOUT、RSS、HANG、SIGNAL、P0）。只有 MAX_RUN 可以重试。
- **D-P2-3 call B 的 55 分钟预算余量很小。** 已有 summary 的 sec：10-15 call B 各步合计约 3160 秒（约 52.7 分钟），其中 tier3 占 2434 秒；10-14 的 tier3 是 1502 秒；10-16 因为 tier3 和 cyq 走了中转快速失败，只用了约 8.5 分钟。再加上 nightly_update 内置的 MemAvailable<2GB 暂停（L20–21），55 分钟只剩约 2 分钟余量。
  - 建议：把预算写成 .ok 键 call_b_budget_min。Arch 建议 75，上限仍是 16:00。如果主 Agent 坚持 55，就要接受 tier3 慢导致 FAILED 的风险。见 Q-A2。
- **D-P2-4 网络调用本身没有总时限，整体只靠驱动的墙钟硬停兜住。**
  - tushare_proxy.py L26–47 的 _get：requests 的 timeout 是单次读超时，不是总时长。relay 默认 180 秒（L57–60），重试 5 次；datahub 是 4 组地址 × 2 次 × 90 秒，配了代理再加 4 × 2 × 60 秒（L69–78）。
  - tier1_pull.py：pull 外层重试 8 次（L38–45）；分页 limit=5000、offset 递增（L35、L47–48）；日历刷新在 L85–92 最先执行。
  - 单页最坏约 8 ×（720+480+900）秒，约 4.7 小时。
  - 新版宣称 connect 15 秒 / read 115 秒 / overall 120 秒。如果是靠改 tushare_proxy.py 或 tier1_pull.py 实现，那就是共享代码改动：要单独的代码改动 .ok、钉值随之更新，还要评估其他用户。优先用环境变量（L59 已有 TSPRO_RELAY_TIMEOUT）或者驱动侧的包装来实现。overall 必须是总时长（比如 deadline 由调用方传入），不能用 requests 的 timeout 冒充。
- **D-P2-5 call B 之后不恢复日历。** 收尾时只核 sha，不符就直接退出 4（L826–827）。call B 按设计不应该写 trade_cal，但目前没有证明。要求 call B 之后也走同一条 compare→restore→双核链；sha 一旦不符，即使恢复成功也判 FAILED，并在回执里写明是哪一步改的。

### P3
- **D-P3-1** 锁文件只判断存在与否（L382–385），不核内容（owner、purpose、set_at 是否是当天）。建议核 purpose=nightly_20261019，set_at 的日期要是 2026-10-19。
- **D-P3-2** relaxed 档重试前要等 30 分钟（L784），等完后没有再做 quiet 复核。建议每次重试前做一次 full quiet_gate。
- **D-P3-3** 没有起跑窗口检查：ET 日期必须是 2026-10-19，时刻必须不早于 05:25。
- **D-P3-4** tier1_pull 的 extend 每次都从 20260923 遍历（L97–100），而 cached_day 只要文件大小大于 0 就跳过（L64–67）。所以历史日期的坏文件永远不会被重拉。隔离逻辑只看 D 当天的文件，这一点在回执里写明即可，10-19 不阻塞（10-12 到 10-16 的五个接口文件都在）。
- **D-P3-5（流程）** Data 自报 11:24 ET 在没有 .ok 的情况下对真实 trade_cal 路径跑过一次拒绝路径测试（目标未动，sha 仍为 141078fa）。已经记录。新版的所有测试必须只用 /tmp 下的假文件，并在测试回执里附上 /tmp 路径清单。

## 3. 成功判据设计（不以退出码为准）
设计原则：invocations 恰好 2 条且 rc 都为 0，只是必要条件。DONE 必须由**本次运行实测**的行数和日期范围支持。所有日期统一成 YYYYMMDD 再比较。D=20261019。

| 对象 | 驱动机检（门槛，决定 DONE / FAILED） | 说明 |
|---|---|---|
| tushare_raw/{daily,daily_basic,adj_factor,stk_limit}/20261019.parquet | 文件存在；rows ≥ 0.98 × 同接口上一开市日；daily_basic ≥ 0.98 × daily；**trade_date 实测 min = max = 20261019**（读 trade_date 单列或 parquet 列统计）；没有 *.tmp.parquet | marker 写实测值，禁止硬编码 |
| suspend_d/20261019.parquet | 存在；rows>0 时 trade_date = D；0 行只记录（P3-5 原注） | 不作为门槛 |
| trade_cal.parquet | 每次尝试后、call B 后、收尾时 sha 都等于 141078fa；记录 rows 和日期范围 | |
| summary（本次） | 只认本次 call B 写的记录：summary 的 finished 晚于 call B 起跑，或者解析 call B 自己的 stdout；14 步全部 status=ok，没有 skipped；hsgt 只认 rc=0（rc=2 算 partial） | 防止读到旧记录被合并 |
| daily_update_status.json | finished_at 晚于 call B 起跑；status=ok；target_trade_date = D；REQUIRED_TABLES（etf_daily_adj、daily_ohlcv_raw_pit、daily_basic、mid_large_universe、etf510300、asof_ts）各表 last_date = D，且 rows ≥ BEFORE 快照的行数 | |
| data_freshness_status.json | generated_at 晚于 call B 起跑；overall=ok；记录 expected_trade_date | 见 Q-A5 |
| 快照 v2 BEFORE/AFTER | compare 退出 0；MUST_NOT_CHANGE 覆盖 PIT 日历 fa4260b8 / 7ccc911e、sw_l1_pit 89d4afa3 / 87d769aa、sw_pit 0b1d3432、closure 6919e7af 及其 156 个文件 | 冻结文件只做事后检测，所以 call B 不得含 sw 和 trade_cal 步骤（两者都已排除） |
| 中转专用步骤 hsgt / cyq / tier3 | Eng 书面确认（Q-E1）之前，partial 一律 FAILED | Arch 同意这条默认 |
| 其余步骤（index_pull、adj_factor、bars、index、etf_daily_adj、events、bundle） | 建议驱动在 marker 里记录 bars、index、etf_daily_adj 的实测 max trade_date，以及 events summary 的 n_fails（只记录，不作门槛） | Data 人读回执补齐其他步骤 |

## 4. 待决问题裁定（建议，最终由主 Agent 定）
- **strict 06:20 daily_pull 截止（pending Arch）：不保留。** strict 改用和计划一致的 30 分钟单次硬停（05:30 起跑即 06:00 硬停）。不另设墙钟截止。
- **strict 06:30 call B 最晚完成（pending Arch）：不保留。** 理由：06:20 截止加 55 分钟是 07:15，已经晚于 06:30，两个值本身矛盾。要满足 06:30，call B 必须在 05:35 前起跑，也就是说前置检查（healthz 最多 90+15 秒）、快照 BEFORE、daily_pull、恢复链（含 30 秒双核）加起来只有 5 分钟。历史上 call B 最长约 52.7 分钟。17:40 的纸面读取也不需要 06:30 前完成。
  - 裁定：strict 和 relaxed 用同一个时间盒：daily_pull 单次 30 分钟硬停；call B 的闸门是「实际起跑时刻 + 预算 ≤ 16:00」，并在 min(起跑 + 预算, 16:00) 时硬停；不得跨入 16:40。两档唯一的区别是 strict 不重试。
  - 建议 10-19 用 relaxed（allow_daily_pull_retry_20261019=2），因为中转不稳定，前提是新版通过行级审查。
- **Q-A1**：同上两条。不保留 06:20 / 06:30，strict 只是「不重试」的 relaxed。
- **Q-A2：不同意。** call B 在 min(实际起跑 + 预算, 16:00) 时必须按第 2 节 D-P1-3 的顺序停掉整棵树，并判 FAILED。超时的运行任何情况下都不能写 DONE。
  - 理由：(1) 这是已定计划的原文要求；(2) 拖过 16:00 后，可能一边在 16:40 被停，一边留下写了一半的表，而 17:40 的纸面读取会读这些表；(3) 只告警会让 DONE 失去时间盒的意义。
  - 预算余量问题按 D-P2-3 处理：建议用 .ok 键 call_b_budget_min=75（上限 16:00）。如果主 Agent 定 55，Arch 接受，但这样会有 tier3 导致 FAILED 的风险。
- **Q-A3：有条件同意。** relaxed 档里因 30 分钟单次上限（reason_code=MAX_RUN）被停，算一次失败尝试，可以重试。条件如下：
  - (a) 整棵树已确认不在，孤儿扫描为空；
  - (b) 恢复链完成，两次 sha 都等于 PIN；
  - (c) 所有 .tmp 和不合格文件都已同盘隔离，前后 sha 一致，并核实不在原位；
  - (d) 重试总次数 ≤ min(2, .ok 授权值)；
  - (e) 满足「下次开始 + 30 + 预算 ≤ 16:00」，且不跨 16:40；
  - (f) 重试前重新做一次 full quiet_gate。
  - RSS、HANG、SIGNAL、P0、墙钟截止、16:40 以及 strict 档被停，一律不重试。
- **Q-A4：relaxed 同样适用。** 重试只发生在同一次运行里、marker 写出之前；marker 一旦写出就是当天终局。
  - 例外：如果是「第一次写入之前」的前置失败（回执能证明 daily_pull 没起、trade_cal 仍等于 PIN、tushare_raw 没有新文件），Arch 可以当天 16:00 前签新 .ok，带 supersede_failed_marker_sha256（全长 sha）重跑，但仍须满足「开始 + 30 + 预算 ≤ 16:00」。其余情况一律 18:40 之后再处理。supersede 键只能由 Arch 填写。
- **Q-A5：有条件同意。** freshness overall=ok 是必要条件，不是充分条件，因为 05:30 ET 是上海 17:30，expected_trade_date 会是 20261016。D 当天的证据来自第 3 节：REQUIRED_TABLES 的 last_date = 20261019，加上原始文件实测的 trade_date。另外 freshness 的 generated_at 必须晚于 call B 起跑，marker 记录 expected_trade_date。本轮不改 data_freshness_status.py（钉 a759d297…）。
- **Q-A6：同意。** --check-only 永不建锁、永不写文件，也不消耗 .ok。05:28 前没有锁时，只记 would_create，并跳过 healthz。但 .ok 解析、全部钉值、marker 预检、新版的两条 pgrep 和 94322 检查都必须照做。check-only 的结果只作参考，正式运行要把所有检查重新做一遍。
- Q-E1 到 Q-E3 属于 Eng。Arch 的立场：Eng 书面答复之前，中转步骤 partial 一律 FAILED；marker 的 schema 名固定为 quantlab.v2.nightly_marker.v1，多出的键由 Eng 确认闸门可以容忍。

## 5. 新版行级审查的准入清单（缺任何一项都不签）
A. 时间盒与停止
1. 两档都有 daily_pull 30 分钟单次硬停；call B 在 min(起跑 + 预算, 16:00) 硬停，超时即 FAILED；不跨 16:40；没有 06:20 / 06:30。
2. 停止顺序：SIGSTOP 父进程 → 重新枚举 → 冻结后代 → 从最深一层 TERM（加 CONT）→ 带超时等待 → KILL → 父进程 → 孤儿扫描。只发给确切 PID，核 cmdline 和 PPID。call A 的匹配串用 scripts/acquire/，call B 按步骤脚本的完整相对路径匹配，不能只用 "scripts/"。
3. 所有子进程、子工具、wait 都带超时；顶层 try/except BaseException 加信号处理，统一收尾（停树、恢复日历、双核 sha、回执、唯一 FAILED、exit 10）。
4. 停止原因用结构化 reason_code，只有 MAX_RUN 可以重试。
5. 超时一节：列出每个网络调用的 connect / read / overall 秒数和 page size（limit=5000），注明 file:line；overall 必须是总时长。如果改了共享文件，另报代码改动 .ok，钉值随之更新。
6. 自测回执（只用 /tmp 假数据）至少覆盖：挂起的假 daily_pull 被硬停后写 FAILED、日历恢复；驱动收到 SIGTERM 后写 FAILED；call B 超时写 FAILED；孙进程被停；RSS 超线不重试；summary 是旧的时判 FAILED；last_date 两种日期格式；重复 .ok 键、带行内注释的 .ok、_consumed 路径的 .ok、含 DRAFT 的 .ok 都被拒。

B. 日历恢复链
7. 恢复前确认整棵树已不在；每次尝试后、call B 后、收尾时，以及异常和信号路径上都执行 compare→restore→间隔 30 秒双核；rc=2 复跑一次，仍失败即 P0。
8. 备份在跑前和 PIN 核对两份 sha，并 chmod 444。建议再和一份现存的独立 PIN 备份核一次 sha（只读）。
9. 例程的 20 分钟兜底检查（D-P0-2）写进例程草稿。

C. .ok 校验
10. 只接受 key=value：ASCII、LF、无行内注释；有重复键或未知前缀就拒。
11. 以下键都必须有，缺一个就拒：所有 sha 键（第 6 节全表）、date、ok_id、signed_by=QuantLab Arch、issued_at（不晚于当前时刻）、expires_et（带时区、晚于当前时刻）、single_use=true、live=false、promotion_approved=false。
12. 路径含 /_consumed/ 就拒；文本出现 DRAFT（不分大小写）就拒；驱动不移动也不删除 .ok（归档由 Arch 负责）；回执记下 .ok 的全长 sha。

D. 成功判据
13. 按第 3 节实测，不硬编码；只认本次写入（核时间戳）；日期统一为 YYYYMMDD 并要求等于 D；hsgt rc=2 算 partial。

E. 前置与资源
14. 两条锚定、括号转义的 pgrep 都为空（D-P2-1）；94322 不存在（D-P1-7），例程里删除 SIGCONT。
15. 驱动启动时核第 6 节全部钉值；解释器为 /usr/bin/python3；ET 日期必须是 2026-10-19，时刻不早于 05:25。
16. RSS：进程树合计到 1484800 kB 即停（停止线）；任何单进程都不得超过 1536000 kB；rss 日志保留。
17. 不写 sw 和 trade_cal 步骤；不带 --force；不删文件；冻结文件由快照 compare 兜底。

## 6. 将来 Arch .ok 需要的钉值与条件（草案，**未签**；新版定稿后重算）
被调用文件的全长 sha256（12:3x ET 重算）：
- 驱动：**等新版 sha**（旧版 a7292a616fede1deda8c88df064c015064073c5c72abb7ba691d1bf30896c5fa 作废）
- cal_restore_v2.py 6686876bdcfc95f11d493b5201f55eb726e69e4894d8c96bfaf46ab1748387a4
- cal_compare_v1.py 74093ff3be4c431bab8c469307b207b43b8e1cff707dd0bac1319a7e265cddfc
- nightly_sha_scope_snapshot_v2_20261018.py c930ed5c627bf937e6b5d139c52f18945f045286e78dba66cbe5adfab92ab79a
- nightly_sha_scope_20261019.txt 04d716af2a87a8bf365431c97097a5c740353c6c273de82677d826f1c4d98807
- scripts/nightly_update.py ec079d56912aea8a4358a7ae97a73a3ad6ee3df34e83845ad4d655d31d838636
- scripts/acquire/tier1_pull.py b630bca24fe7c86a656cf375c4aa1f543d98dac86178ba7ae50881cf4dbeb711（如果超时修订改了它，用新值）
- quantlab/data_sources/tushare_proxy.py ae91f230560d445b4d2321e8e022d01b55773e168d4d842fc6987fa9458fc772
- scripts/acquire/relay_health.py 6d3ea9f57f63af8d82d6eeaf140a989aeb09cda941e6711c25f12fd3bbe0e17f
- scripts/acquire/adj_factor_incr.py 723726c5623a1739ee1fb1dcf97a6be6efd4532717a4c4411fb5e24dfd1422ad
- scripts/acquire/tier1_materialize.py e9c89a6c3a0719d9b78064404f2b7d66a7076430f5676e65335db06efae1c3bb
- scripts/acquire/etf_daily_adj_incr.py ae670dfc0da14f7aa90bb1d6edd3377b027f69dcb739987dc016388e45b02ae4
- scripts/acquire/eng_daily_panels.py a754205397d22b6bb1109d92ee4040d65faedec2d37afd575f77e63da642f0be
- scripts/acquire/mid_large_universe_incr.py fe4bbffe1c7c8e0a3f4d38a590acbbcaab61f53b08939722e9b503fa2901d64b
- scripts/acquire/_light_event_windows_pull.py f12660b90c01089278f01e22b3bdf53154780802668ed4ea90ea5c38c3fc9d71
- scripts/acquire/forecast_manifest_declare.py f77673811aa2dd05d461cf895476212f52b05abc3f26212cba87ea30578bd731
- scripts/acquire/fill_hsgt_top10_extend.py 36cff47c008244ee50f7fb2fcc5f6fd0588d7141901b3a23afe50c48f058e918
- scripts/acquire/cyq_perf_monthly.py 6aae6c1b8de7b37752fb5032c22ea65b698f252cc57f8e5af94b1e13d6e09c1f
- scripts/acquire/tier3_daily_snapshot.py 64a71f5607439c5b09ddd92a8dfeffd94e4f5244297f83fbc5c65e3abfcf1067
- scripts/acquire/data_freshness_status.py a759d29788859b43783bac6360014347b2df0e4dce5949302a0908db511f1d50

数据钉值（不得写；trade_cal 例外，它每次都要恢复到 PIN）：
- data/v2/tushare_raw/trade_cal.parquet 141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086
- data/v2/calendar/trade_cal_sse_pit.parquet fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41；manifest.json 7ccc911e8a3ed2e408f30db1f95f12eb71a6fea18003ba88a31246f941cc89a4
- docs/v2/eng_sd1/paper_import_closure.json 6919e7afe605cc4d1af48868a06b6550db66e3fd1923a3e61bdcc16c621bae20
- data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet 89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c
- data/v2/sw_l1_pit/industry_members_sw_l1.parquet 87d769aaca06212186986af489f6507b6f0d98c8937f7a4476f97538562733b3
- data/v2/sw_pit/industry_members_sw_l1_pit.parquet 0b1d3432e30f7cdd907df393299cd2f552e1121899239985a00113c4dfcd89f6

.ok 键草案（只用 key=value，签发时由 date +%Y-%m-%dT%H:%M:%S%:z 生成时间；签好后用 os.link 独占创建，正文不留 DRAFT）：
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
sha_driver=<新版全长 sha>
sha_<每个被调用文件>=<上表全长 sha>
pin_trade_cal=141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086
pin_frozen_closure=6919e7afe605cc4d1af48868a06b6550db66e3fd1923a3e61bdcc16c621bae20
daily_pull_max_min=30
call_b_budget_min=75
call_b_latest_finish=16:00
allow_profile_relaxed_20261019=true
allow_daily_pull_retry_20261019=2
allow_run_daily_pull_20261019=true
allow_run_call_b_20261019=true
allow_restore_trade_cal_20261019=true
allow_routine_fallback_restore_20261019=true
allow_write_nightly_marker_20261019=true
allow_quarantine_mv_daily_raw_20261019=true
allow_create_research_quiet_lock_20261019=true
allow_kill_scope=driver_descendants_exact_pid
allow_trade_cal_step=false
allow_sw=false
allow_force=false
allow_delete=false
allow_commit=false
rss_stop_kb=1484800
rss_hard_kb=1536000
blackout_et=16:40-18:40
```
签发前提：
- (1) 新版通过第 5 节行级审查，自测回执全部有实测；
- (2) Data 的 12:50 连通性结果已收到；
- (3) 94322 已按 D-P1-7 了结；
- (4) Eng 已答复 Q-E1 到 Q-E3，或主 Agent 接受默认 FAILED；
- (5) 主 Agent 已就 Q-A1、Q-A2 和预算（55 或 75）定稿；
- (6) Arch 05:25 设 RESEARCH_QUIET.lock，.ok 在那之前签好；
- (7) .ok 单次使用，用后由 Arch 按 sha8 + CONSUMED/VOID/CONSUMED_FAIL + ET 时间归档到 _consumed/。
