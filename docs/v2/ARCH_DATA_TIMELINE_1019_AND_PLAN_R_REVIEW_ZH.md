# Arch 审查：10-19 日更时间线 / 日历比对恢复脚本 / 快照 v2 / 方案 R 补跑 .ok 申请 r2 / SW r3.2 / 日历 r3 / 备用 r3.2

- 审查人：QuantLab Arch（静态审查子代理）；生成时间 2026-10-18T11:07:16-04:00（ET，date 生成）。
- 方式：只读（Read / rg / ls / sha256sum / 代码阅读）。没有运行任何项目脚本，没有读 parquet 内容或任何价格、财务、因子数值，没有 git apply，没有签 .ok，没有发消息。
- 依据：docs/v2/ARCH_DATA_REVISIONS_1040_REVIEW_ZH.md（11cb0690）、主 Agent 书面裁定（一律恢复到 141078fa；不加只读；cyq 只跑一次；RSS 停止线 1484800）。
- live=false，promotion=false。

## 0. sha 核对（全部先核）
| 文件 | 申报 | 实测 | 结论 |
|---|---|---|---|
| docs/v2/audit/nightly_20261019/TIMELINE_10_19_ZH.md | 3d90d84c | 3d90d84c987e1ed20a3e1613ccacc1660fb7457dcb228a2ee7c7107ed0563503 | 一致 |
| docs/v2/audit/nightly_20261019/cal_compare_v1.py | 74093ff3 | 74093ff3be4c431bab8c469307b207b43b8e1cff707dd0bac1319a7e265cddfc | 一致 |
| docs/v2/audit/nightly_20261019/cal_restore_v1.py | 181549b8 | 181549b87dc61c9f2dfc682cbc4777f984bce1f07ac3536f68cdc685a900344e | 一致 |
| docs/v2/audit/nightly_20261019/nightly_sha_scope_20261019.txt | 04d716af（167 项） | 04d716af2a87a8bf365431c97097a5c740353c6c273de82677d826f1c4d98807 | 一致；解析 167 项：MUST 164 / EXPECTED 2 / RESTORED_TO_PIN 1 |
| docs/v2/audit/nightly_sha_scope_snapshot_v2_20261018.py | c930ed5c | c930ed5c627bf937e6b5d139c52f18945f045286e78dba66cbe5adfab92ab79a | 一致 |
| docs/v2/audit/BACKFILL_1014_1016_OK_REQUEST_ZH_r2.md | 2aad5036 | 2aad50362823808c2b53628d130e9f70deb1d567e32b82299cf0476490ac4e67 | 一致 |
| docs/v2/audit/nightly_sha_scope_backfill_1014_1016.txt | 579c8605（414 项） | 579c8605266af1724b942fe1f3f2c000e0f97013cb9ff345c184b20c723b54c0 | 一致；MUST 382 / EXPECTED 32 |
| docs/v2/plans/DATA_SW_L1_PIT_V2_FIX_PLAN_ZH_r3_2.md | fabd7afb | fabd7afb595c6cfcd0f6a1792e563556cdb4f937aa3e3788b6eb0b32be338f03 | 一致 |
| docs/v2/plans/DATA_CALENDAR_2027_PACKAGE_PLAN_ZH_r3.md | 3772c424 | 3772c424063af26ca650687196d364e8d57243c421d678c069c2bfbe04b22e99 | 一致 |
| docs/v2/plans/DATA_DAILY_FALLBACK_PUBLIC_SOURCE_PLAN_ZH_r3_2.md | 23d97887 | 23d9788492f08c342f477c50fe6c03afb635720af13fe52b4f647c34f0de017b | **前 8 位不符（实测 23d97884）**，内容即 r3.2 增量；记 P3-7，签 code-change .ok 时以实测全长为准 |
| scripts/acquire/tier1_pull.py / scripts/nightly_update.py / scripts/acquire/cyq_perf_monthly.py | b630bca2 / ec079d56 / 6aae6c1b | b630bca24fe7c86a656cf375c4aa1f543d98dac86178ba7ae50881cf4dbeb711 / ec079d56912aea8a4358a7ae97a73a3ad6ee3df34e83845ad4d655d31d838636 / 6aae6c1b8de7b37752fb5032c22ea65b698f252cc57f8e5af94b1e13d6e09c1f | 一致 |
| 141078fa 全长 | 基线 | docs/v2/audit/nightly_sha_baseline_20261018_1022.txt L8：141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086 | 与恢复脚本调用、TIMELINE L13 / L102 一致 |

两份范围文件都覆盖 paper_import_closure.json 全部 156 项且均为 MUST_NOT_CHANGE；sw_l1_pit 89d4afa3（industry_members_sw_l1_tushare.parquet）、87d769aa（industry_members_sw_l1.parquet）、sw_pit L1 均为 MUST（脚本解析核对）。

## 1. 结论一览
| 项 | 结论 |
|---|---|
| (1) cal_restore_v1.py / cal_compare_v1.py | **PASS with conditions**（无 P0–P2；P3-1、P3-2） |
| (2) 06:20 硬截止停进程逻辑 | **PASS with conditions**（P2-1 残留 .tmp.parquet；P3-3、P3-4） |
| (3) 时间线与 05:30 开跑 | **PASS with conditions**（P2-2 0 行 / 半日数据判据；P3-5 suspend_d） |
| (4) 方案 R .ok 申请 r2 + 范围 579c8605 | **PASS with conditions**（P2-3 串行写法、P2-4 RSS 停止线须自动执行、P2-5 快照改用 v2；P3-6 bundle 备份）。两轮探测证据到位后可签（§9 表） |
| (5) 快照 v2 | **PASS**：三条 P2 全部关闭（P3-8 一条小项） |
| (6) SW r3.2 / 日历 r3 / 备用 r3.2 | SW r3.2 **PASS**（P2-A 关闭）；日历 r3 **PASS**（P3-a、P3-b 关闭，§2 笔误按勘误处理）；备用 r3.2 **PASS**（sha 申报笔误 P3-7） |

## 2. (1) 恢复与比对脚本
### 2.1 cal_restore_v1.py（181549b8）逐项
| 要求 | 位置 | 结论 |
|---|---|---|
| 备份 sha 先核，不符目标不动 | L89-93 | 满足（exit 2） |
| --expect-sha 全长 64 位 | L72-74 | 满足；**但未钉死为 141078fa**（见 P3-1） |
| 目标限制 | L77-78 realpath == data/v2/tushare_raw/trade_cal.parquet 或 /tmp | 满足 |
| 备份与目标同一文件拒绝 | L86-87 samefile | 满足 |
| 留存被重写文件（新文件 O_EXCL，失败不阻断恢复） | L95-113、copy_new L47-58 | 满足；留存失败返回 3，恢复优先，符合裁定 |
| 同目录临时文件 O_EXCL + fsync | L116-118、L49-55 | 满足 |
| 临时文件 sha 核验后才替换 | L124-128 | 满足 |
| os.replace + fsync 目录 | L131-132 | 满足（同目录 rename，原子，等价 mv -T） |
| 替换后复核 | L136-139 | 满足（exit 1 = P0 报警） |
| 永不删备份 | 全文只 unlink 临时文件（L122、L127） | 满足 |
| 一律恢复（目标已是 pin 也恢复） | L11 说明，流程无短路 | 满足裁定 |
- **P3-1**：L72 只校验格式。建议加常量 PIN=141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086，目标为真实路径时要求 exp == PIN（/tmp 自测可放开）。例程 L102 已传对的值，所以不阻断；10-19 照现文本用也可，以例程命令行为准。
- **P3-2**：L116 临时名只含 pid；若同名残留存在，copy_new 以 O_EXCL 失败 → exit 2 → **恢复没做**。概率极低，但出错路径是纸面停跑。例程须把 restore_rc=2 视为 P0 并立即人工复跑一次（新 PID 即新临时名），不要等。备份 chmod a-w 未在脚本内核验，回执记 stat 即可。

### 2.2 cal_compare_v1.py（74093ff3）
- 只读：只读 --current / --backup（L229-237）；只写 --out 及 .diff.csv，限 docs/v2/audit/nightly_20261019/ 或 /tmp，目标存在即拒绝（L193-205），写法为 O_EXCL 临时文件 + fsync + os.link + fsync 目录（L208-226）。满足。
- C1 可读（L328-334）、C2 schema 含 arrow 类型 / 可空性 / pandas dtype（L337-344）、C3 元数据与实读行数（L352-357）、C4 (exchange, cal_date) 去重（L359-369）、C5 排序后逐格（L371-391，mergesort、NaN 视同）、C6 SSE 20261019 / 20261020 各一行且 is_open==1（L248-265、L393-398）。全部满足 11cb0690 §5.3。
- 比对结果只决定是否报 P1，不决定是否恢复（TIMELINE L107）——正确。
- 观察：比对器只记录备份 sha（L314-319），不校验它等于 pin；pin 校验由恢复脚本 L92 承担，可接受。

## 3. (2) 06:20 硬截止（TIMELINE §5.2、§5.4）
- 写入方确认：tier1_pull.py 不起子进程（tushare_proxy.py 无 subprocess / Popen），所以没有孙进程；nightly_update.py L118 subprocess.call 起唯一子进程 tier1_pull.py extend 20261019。先停子进程再停父进程的顺序正确（只停父进程，子进程变孤儿会继续写）。nice 直接 exec，$! 即 nightly PID，正确。
- 停子进程后 nightly 自己写 logs/nightly/20261019_summary.json（L120 记 fail rc=-15，L137）并退出——预期行为。
- **trade_cal 撕裂**：tier1_pull.py L92 原地非原子 to_parquet，SIGKILL 落在写入中会留半截文件；C1 会判不可读 → P1，但恢复照做，恢复完全覆盖这种情况。恢复必须在两个 PID 都确认退出后再做（§5.4 第 5 步已写），正确。
- **日线原始文件撕裂**：save()（L58-62）先写 <d>.tmp.parquet 再 os.replace，目标文件不会撕裂。但：
- **P2-1**：被杀在 to_parquet 中途会留下 data/v2/tushare_raw/<api>/20261019.tmp.parquet。它不会让 cached_day 跳过（cached_day 只看 <d>.parquet，L65-67），但任何 glob("*.parquet") 的下游会把它当一个日子：tier1_pull.py 自己 L96 的 existing 就会得到 stem "20261019.tmp"。截止后必须 `ls -l data/v2/tushare_raw/{daily,daily_basic,adj_factor,stk_limit,suspend_d}/ | rg tmp`（只看名字与大小），发现即按 §8(c) 隔离，并且不起 call B。
- 被截止时某接口尚未 save → 该接口无 20261019 文件 → 下次运行会重拉（不会永久跳过）；已 save 的接口若为 0 行或不全则会永久跳过，处理见 §8(c)。
- **P3-3（CPID 时点）**：§5.2 只在 sleep 2 后读一次 children。nightly 先 wait_mem（L113）再起子进程，MemAvailable<2GB 时会停 60 秒循环，2 秒时 children 可能为空。截止时（第 1 步）必须重读 /proc/$NPID/task/$NPID/children 并按 args 认定 CPID；为空且 NPID 仍在，就只按 §5.4 第 4 步处理 NPID。
- **P3-4（检查与发信号之间退出 / PID 复用）**：subprocess.call 会立即回收子进程，PID 理论上可被复用；cmdline + PPID 复核（§5.4 第 2 步）把窗口压到微秒级，可接受。kill 返回 ESRCH（已退出）时不得让例程因 set -e 中断：写成 `kill -TERM "$CPID" 2>/dev/null || true` 后照常轮询 /proc；Z 视为已退出正确。

## 4. (3) 时间线与开跑时间
- daily_pull 拉 daily_basic：是。tier1_pull.py L102 apis = daily、daily_basic、adj_factor、stk_limit、suspend_d；nightly 的 daily_pull 步骤即 `tier1_pull.py extend <ymd>`（nightly_update.py L28）。
- 实测耗时 84 / 14 / 16 秒与申报出处一致（本审未重开日志数值，只核代码路径）；两源都拒绝时约 17–18 分钟的推算与代码一致（pull L38-45 八次重试、_call 先 datahub 后 relay）。超时型故障只能靠 06:20 截止，正确。
- 时区：10-19 为 EDT（UTC−4），上海 UTC+8，差 12 小时，05:30 ET = 17:30 上海，正确。
- 算术：S + 4 分钟恢复完成，+20 分钟余量 ≤ 06:30 → S ≤ 06:06，正确；05:30 准点 05:54、晚 15 分钟 06:09，均满足；05:55 晚 15 分钟为 06:34，不满足。
- 上游：按 Tushare 文档上限，daily ≤ 16:00/17:00、daily_basic ≤ 17:00（上海）；17:30 有 30 分钟余量，17:15 只有 15 分钟且无本地证据。本地“当日 18:08 上海已有数据”只是推断（TIMELINE L59 自己也这样标）。
- **P2-2（不全的当日数据会被永久缓存）**：cached_day（L64-70）只看文件大小 > 0。返回 0 行会写出 0 行 parquet（非 0 字节），返回半日数据（例如 daily_basic 尚未入齐）也会照写，之后都永久 skip。TIMELINE L33 的 ≥ 5000 门槛能抓 0 行，抓不住“入了九成”。要求改为：call A 后对 daily、daily_basic、adj_factor、stk_limit 四个文件读 parquet 元数据 num_rows，**每个 ≥ 同接口 20261016 文件 num_rows 的 0.98 倍，且 daily_basic ≥ daily 的 0.98 倍**；任一不满足按 §8(c) 处理。只读元数据，不读数值。
- **P3-5**：suspend_d 合法地可能很少甚至 0 行，不设门槛，但回执记 num_rows；若为 0 行，注明“无法区分无停牌与未发布”，且该文件同样会被永久跳过，由 Data 在 10-19 收盘后用只读探测核一次。
- freshness 在上海 20:00 前取前一开市日（data_freshness_status.py L61，TIMELINE L61），05:30 跑出 expected_trade_date=20261016，与开跑时间无关，同意。

## 5. (4) 方案 R（BACKFILL r2 2aad5036、范围 579c8605）
### 5.1 cyq 只跑一次：代码核实属实
- nightly_update.py L40：cyq 命令为 cyq_perf_monthly.py ym ym，ym 取 --date 前 6 位（L24）。
- cyq_perf_monthly.py L15-18：202610 开市日中 d < 上海今天（今天只在上海 19 点后计入）。16:00 ET 10-18 = 04:00 上海 10-19，20261019 不会计入；20261017/18 为周末。L43-44：已有且 > 10000 字节即跳过。ls 实测 data/v2/tushare_raw/cyq_perf/20261008、09、12、13 各约 162 KB，20261014–16 不存在 → new_days=3。属实。
- 注意（不改结论）：cyq 只走中转（RELAY_STEPS，nightly L85、L109-112），中转判宕时整步跳过、记 partial、rc 仍 0，并写 output/relay_outage_backfill_queue.json（L86-95，范围内 EXPECTED，已备份）；单日空返回只记 fails 不写文件（L48-49）；原始日文件 L48、月表 L58、manifest L66 都是非原子写，靠 §4.1 备份兜底。中转若返回不足一页，单日文件也会 >10KB 被永久缓存，§6 每天 ≥ 5000 行判据覆盖。
### 5.2 不写 10-14 / 10-15 summary 与 daily_update_status
- nightly 只写 logs/nightly/{d}_summary.json，d = --date（L99、L130-137），--date 20261016 不会碰 20261014 / 20261015 summary。属实，两者在范围内为 MUST。
- tier3 只写 data/v2/tier3_daily/<kind>/20261016.parquet 与 manifests/20261016.json（tier3_daily_snapshot.py L30、L60）；bundle 只复制 BUNDLE_MAP、cyq 月表与 {d} 的 tier3（nightly L67-83）；freshness 只原子写 output/data_freshness_status.json（L85）；relay_health 写 output/relay_health.json（L16）。四者都不写 output/daily_update_status.json（rg 无命中），范围内为 MUST（7991455a）。属实。
- 方案 R 不调用 daily_pull，tushare_raw/trade_cal.parquet 在范围内为 MUST，cyq L16 只读它。正确。
### 5.3 范围与备份
- 范围 579c8605：closure 156 项、SW 两份冻结文件、SSE PIT 日历及 manifest、Eng 纸面日历、tier3 10-13/14/15、cyq 202601-202609 月表与原始 ≤20261013、10-14/15 summary、daily_update_status 均为 MUST；cyq 202610、cyq manifest、relay_health、队列 JSON、20261016 summary、freshness、bundle 副本为 EXPECTED。覆盖完整。
- 备份清单（r2 §4.1/§4.2）覆盖了所有会被重写的状态文件与 MUST 中最可能被误写的 tier3 10-14/15。
- **P3-6**：bundle 副本（output/data_v2_bundle/cyq/*、sw_pit/*）是截断写（shutil.copy2），可从源重新复制，不强制备份；但建议把 output/data_v2_bundle/cyq/manifest.json 与 cyq_perf_202610.parquet 两个副本也 cp -p 进 §4.1，成本几乎为零。
### 5.4 须改项
- **P2-3（串行）**：r2 L29-30 两条命令都以 & 结尾、连续写出，照抄会并发跑两个真实数据进程，违反“一次一个”。.ok 里写成：run1 后台起 → 记 NPID → 轮询到退出 → wait 取 rc → 快照 / compare / 逐步判定全过 → 才起 run2。
- **P2-4（RSS 停止线必须自动执行）**：r2 §7 只是每 15 秒 ps 采样、人工判断。RLIMIT_RSS 在 Linux 不生效，ulimit / prlimit 无法限制 RSS（RLIMIT_AS 限虚存，会误杀 pandas），包装器 v4 是否能包 nightly 命令本审未核实，不作依据。要求：随 run 起一个采样循环，每 5 秒读 /proc/<pid>/status 的 VmRSS（NPID 与其 children），任一 > 1484800 kB 即按确切 PID 先 TERM 子进程、10 秒后 KILL，再处理 NPID，记 /tmp/arch1018/backfill_rss_runN.log（新文件）；回执写明这是采样峰值。.ok 写 rss_stop_kb=1484800、rss_enforcement=sampler_5s_autokill_exact_pid。
- **P2-5（快照用 v2）**：v2（c930ed5c）已关闭 v1 的三条 P2（§6），范围文件格式兼容（只有 EXPECTED / MUST 两类、绝对路径）。方案 R 改用 v2：snap / compare 都带 --expect-scope-sha 579c8605…，输出在 /tmp/arch1018/；r2 §5 的三条人工补偿随之不再需要（保留人工 sha256sum 范围文件一次即可）。
- 解释器：/usr/bin/python3 已钉（r2 L14、命令行）。nightly 以 sys.executable 起子步骤（L13），所以子进程同一解释器，满足。

## 6. (5) 快照 v2（c930ed5c）
| 原 P2 | v2 位置 | 结论 |
|---|---|---|
| P2-S1 输出不受限 / 非原子 | L27-28 允许目录；L84-100 绝对路径、不在范围内、不存在；L103-120 O_EXCL 临时文件 + fsync + os.link + fsync 目录 | 关闭 |
| P2-S2 META_ONLY 返回 0 | L188-189 META_ONLY_FAIL 计数；L199 计入 exit 1 | 关闭 |
| P2-S3 无 scope_sha 检查 | L74-81 snap / compare 都要求 --expect-scope-sha；L145 头部记录；L177-178 三方一致否则 exit 2 | 关闭 |
| P3 哈希期间变化 / 无参数 / size | L133-140 前后 stat，UNSTABLE exit 2；L206-207；meta 含 size | 关闭 |
- **P3-8**：RESTORED_TO_PIN 只核 AFTER == pin（L190-195），不核 BEFORE == pin。10-19 例程 §5.1 已在 call A 前人工核两份 sha == pin，所以不阻断；建议回执同时贴 BEFORE 快照中该行。

## 7. (6) 其余三份
- **SW r3.2（fabd7afb）**：先写文件、再取 done，并以 os.utime 把 mtime 设到 done−1 秒，正例经 L297 / L299 / L304 / L307 / L310 均通过；“未来”例注入 now=done−1 天，先于 mtime 检查触发；新增 L307 专测（mtime=done+60 秒、now=done+5 分钟）只触发“completed_et 早于目录内文件 mtime”；L304 例（签发 2026-06-01、mtime 2026-01-01）只触发“早于 pull .ok 签发时间”。消息子串改为完整短语，消除了“早于”二义。对照 r3.1 L300-310 的检查顺序逐条推演无误。**P2-A 关闭，PASS**；code-change .ok 签 r3.1 全文 + r3.2 §3，10-19 纸面后。
- **日历 r3（3772c424）**：P3-a _guard_write 增加 (st_dev, st_ino) 比对与“目标已存在即拒绝”，selftest 用例 12 用 /tmp 替身，不碰真实文件——关闭。P3-b 只有日期的公告最早上海次日拉取、2027-01-04 前须落地——关闭。§2 笔误：上海次日 00:00 = 公告日当天 11:00 ET（EST，UTC−5）；Data 的勘误表述正确，按规矩另出勘误、不改原文。PASS。
- **备用 r3.2（实测 23d97884…）**：§1 L80 改写与 11cb0690 §1.3 要求逐字对应（BEFORE sha 非 141078fa 即不启动）；Q6 降级规则落实；范围文件改钉条件写明。PASS。**P3-7**：Data 申报 sha 前缀 23d97887 与实测 23d97884 不符，属申报笔误，请 Data 在回执更正；.ok 钉实测全长 23d9788492f08c342f477c50fe6c03afb635720af13fe52b4f647c34f0de017b。

## 8. Data 三个问题：Arch 建议
### (a) 开跑时间：**05:30 ET**（主 Agent 定）
- 05:55 在例程晚 15 分钟时不满足 20 分钟余量，且留给 daily_pull 的时间不够覆盖快速失败的 17–18 分钟，否决。
- 05:15 离 daily_basic 文档上限只有 15 分钟，又没有本地证据，入半日数据的风险最高，而 P2-2 说明半日数据会被永久缓存，不建议。
- 05:30 余量两头都够。附加：例程起跑前不做任何上游探测（探测本身不落盘也行，但不要因此推迟）。

### (b) 硬截止触发后：**不重跑 daily_pull；call B 默认不起，等主 Agent**（同意 Data 默认）
- 理由：call B 含 bars / daily_basic 物化 / eng_panels（写 output/daily_update_status.json，Eng 闸门读）等依赖 20261019 原始数据的步骤；日线不全时这些步骤会产出“看起来更新了”的状态文件，比停在 10-16 更危险。
- Arch 建议主 Agent 的默认裁定：10-19 纸面跑完（18:40 ET）前不起 call B；之后在新 .ok 下整套重跑（含备份 → daily_pull → 比对 → 恢复），因为 tier1_pull 每次都会重写纸面日历，直到 (c) 代码修改落地。
- 恢复本身不受影响：截止后照做比对与恢复，restore_rc=0 且两次 sha == 141078fa 即纸面日历安全。

### (c) 20261019 原始文件 0 行（或不满足 P2-2 判据）
1. 报 P1（主 Agent + Arch），记 ls -l 与 num_rows（元数据）；**不删除**。
2. 隔离：把不合格的 <api>/20261019.parquet（及任何 20261019.tmp.parquet）`mv` 到 _recovery/data/nightly_20261019/quarantine/<api>/，前后各 sha256sum 与 stat。不隔离就会被 cached_day 永久跳过，也会被 glob 下游读到。**此 mv 属于写 data/，须写进 10-19 日更 .ok 的 allow_quarantine_mv_daily_raw_20261019=true；.ok 未写则只报不动**，同时不起 call B。
3. call B 不起（同 (b)）。
4. 重拉：10-19 18:40 ET 之后、在新 .ok 下进行，且须重复备份 → daily_pull → 比对 → 恢复全序列（tier1_pull 仍会重写日历）；上游可得性先用只读探测确认。
5. 纸面影响：纸面日历已恢复则 06:37 的 sha 门禁照过；纸面是否读 20261019 原始日线、读不到时如何表现，本审未核，须 Eng 书面确认后报主 Agent，不作推断。

## 9. 方案 R run .ok（两轮探测证据到位后可签的确切键值）
签发时：issued_at / signed_et 取 date +%Y-%m-%dT%H:%M:%S%:z；签前重算下表所有 sha，任一不同即不签。
| key | value |
|---|---|
| ok_type | run |
| ok_id | ARCH_RUN_AUTH_DATA_BACKFILL_1014_1016_PLAN_R |
| path | output/ai_factory/ARCH_RUN_AUTH_DATA_BACKFILL_1014_1016_PLAN_R.ok（Arch 写） |
| signed_by | QuantLab Arch |
| signed_et / issued_at | 签发时 date 生成 |
| expires_et | 2026-10-18T15:55:00-04:00 |
| single_use | true（用后移 output/ai_factory/_consumed/，sha8 + CONSUMED/VOID + ET 时间） |
| live / promotion | false / false |
| interpreter | /usr/bin/python3（3.13.5 / pandas 3.0.6 / pyarrow 26.0.0） |
| env | PYTHONDONTWRITEBYTECODE=1；nice -n 10；stdin </dev/null |
| cmd_run1 | /usr/bin/python3 scripts/nightly_update.py --date 20261016 --steps cyq |
| cmd_run2 | /usr/bin/python3 scripts/nightly_update.py --date 20261016 --steps tier3,bundle,freshness |
| cmd_dryrun | 两条命令各加 --dry-run，先跑（只打印，不写 summary，nightly L106、L137） |
| serial | strict：run1 退出、wait 取 rc、快照 compare 与 r2 §6 run1 判定全过后才起 run2；一次一个真实数据进程 |
| latest_start_run1 / run2 | 2026-10-18T14:45:00-04:00 / 2026-10-18T15:00:00-04:00 |
| sha_nightly_update | ec079d56912aea8a4358a7ae97a73a3ad6ee3df34e83845ad4d655d31d838636 |
| sha_relay_health | 6d3ea9f57f63af8d82d6eeaf140a989aeb09cda941e6711c25f12fd3bbe0e17f |
| sha_cyq_perf_monthly | 6aae6c1b8de7b37752fb5032c22ea65b698f252cc57f8e5af94b1e13d6e09c1f |
| sha_tier3_daily_snapshot | 64a71f5607439c5b09ddd92a8dfeffd94e4f5244297f83fbc5c65e3abfcf1067 |
| sha_data_freshness_status | a759d29788859b43783bac6360014347b2df0e4dce5949302a0908db511f1d50 |
| sha_tushare_proxy | ae91f230560d445b4d2321e8e022d01b55773e168d4d842fc6987fa9458fc772 |
| sha_snapshot_tool | c930ed5c627bf937e6b5d139c52f18945f045286e78dba66cbe5adfab92ab79a（v2） |
| scope_file / scope_sha | docs/v2/audit/nightly_sha_scope_backfill_1014_1016.txt / 579c8605266af1724b942fe1f3f2c000e0f97013cb9ff345c184b20c723b54c0 |
| request_doc_sha | 2aad50362823808c2b53628d130e9f70deb1d567e32b82299cf0476490ac4e67 |
| must_not_change_pin | output/daily_update_status.json = 7991455a06b85d7bca09b8c50e2fc1cfe6f421abe33790b90a125097ab2a4850；data/v2/tushare_raw/trade_cal.parquet = 141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086；closure 156 项 + 89d4afa3 + 87d769aa |
| backup_dir | _recovery/data/backfill_1014_1016/（mkdir 不带 -p，已存在即停） |
| backup_sums | SHA256SUMS_pre_run1、SHA256SUMS_pre_run2（set -o noclobber） |
| backup_list_run1 | r2 §4.1 八个文件 + output/data_v2_bundle/cyq/manifest.json + output/data_v2_bundle/cyq/cyq_perf_202610.parquet（P3-6） |
| backup_list_run2 | r2 §4.2 十二个文件；七个 20261016 目标须不存在 |
| rss_stop_kb | 1484800 |
| rss_enforcement | sampler_5s_autokill_exact_pid（P2-4；先子后父，TERM 10 秒后 KILL） |
| rss_hard_kb | 1536000 |
| guard_94322 | run1 前 kill -STOP 94322，/proc/94322/stat 状态须为 T 并留 ps；全部结束后 kill -CONT 94322 |
| pre_ok_quiet | RESEARCH_QUIET.lock 设置 ≥ 15 秒后，healthz 证据 quiet=true、gen_running=false、child_pids={} |
| allow_run_nightly_update_cyq | true |
| allow_run_nightly_update_tier3_bundle_freshness | true |
| allow_network_relay | true |
| allow_write | data/v2/tushare_raw/cyq_perf/2026101{4,5,6}.parquet（新）；data/v2/cyq/cyq_perf_202610.parquet；data/v2/cyq/manifest.json；data/v2/tier3_daily/*/20261016.parquet 与 manifests/20261016.json（新）；output/data_v2_bundle/**；output/data_freshness_status.json；output/relay_health.json；output/relay_outage_backfill_queue.json；logs/nightly/20261016_summary.json、20261016_{cyq,tier3}.log、backfill_20261018_run{1,2}.out；_recovery/data/backfill_1014_1016/**；/tmp/arch1018/** |
| allow_daily_pull / allow_trade_cal / allow_sw / allow_eng_panels / allow_events | false |
| allow_write_daily_update_status | false |
| allow_write_summary_20261014_20261015 | false |
| allow_force | false |
| allow_delete | false（半写文件不删，原样报） |
| allow_kill | 仅本次 nightly 的确切 NPID / CPID（核 cmdline），以及 94322 的 STOP / CONT |
| abort_rules | compare 非 0 或任何 META_ONLY_FAIL；范围 sha 不符；r2 §6 任一判定不满足；RSS > 1484800；summary 出现 RELAY_DOWN；15:55 ET 未结束按确切 PID 停 |
| blackout | 16:40–18:40 ET 不跑任何东西 |
| receipt | docs/v2/audit/BACKFILL_1014_1016_RECEIPT_ZH.md（新文件）+ TEAM_STATE Data 段 |

## 10. 签发前剩余前置条件
1. 两轮中转探测证据（trade_cal + 至少一次大分页完整一页 5000 行），写在 docs/v2/audit/relay_probe_20261018/probe_log.csv；目前只有 10:15:54 一轮小接口，**不满足**。
2. Data 出 r3 增量（或书面确认）接受 P2-3 串行写法、P2-4 自动 RSS 停止、P2-5 快照 v2、P3-6 备份两项；不改原文件。
3. 94322 为 T（Data ps 证据）；RESEARCH_QUIET.lock + 15 秒 + healthz 证据。
4. 签发时重算 §9 全部 sha；13:30 ET 前签不出则按 r2 §9 放弃今天补跑。
5. 跑完后 Arch 核 before / after 快照与备份 SHA256SUMS；补跑改变的输入 sha 由 AI 重钉后才签叶25 step −1 .ok。
6. 10-19 日更：主 Agent 定开跑时间（建议 05:30）；Data 按 P2-1、P2-2、P3-2/3/4 改例程文本后交 Arch 复核；若采用 (c) 第 2 步隔离，10-19 日更 .ok 加 allow_quarantine_mv_daily_raw_20261019=true。

## 11. 发现汇总
| 级别 | 编号 | 位置 | 内容 |
|---|---|---|---|
| P2 | P2-1 | tier1_pull.py L61、L96；TIMELINE §5.4 | 截止后残留 .tmp.parquet，须检查与隔离，不起 call B |
| P2 | P2-2 | tier1_pull.py L64-70；TIMELINE L33 | 半日数据会被永久缓存；门槛改为相对 20261016 的 0.98 倍 |
| P2 | P2-3 | BACKFILL r2 L29-30 | 两条命令都带 &，须严格串行 |
| P2 | P2-4 | BACKFILL r2 §7 | RSS 停止线须 5 秒采样自动按 PID 停，不能只人工看 |
| P2 | P2-5 | BACKFILL r2 §5 | 改用快照 v2 |
| P3 | P3-1 | cal_restore_v1.py L72 | expect sha 未钉为常量 |
| P3 | P3-2 | cal_restore_v1.py L116-123 | 临时名冲突时恢复不做；restore_rc=2 立即人工复跑 |
| P3 | P3-3 | TIMELINE §5.2 L81-83 | CPID 截止时重读 |
| P3 | P3-4 | TIMELINE §5.4 | kill ESRCH 不得中断例程 |
| P3 | P3-5 | TIMELINE L33 | suspend_d 0 行无法判定，记录并事后核 |
| P3 | P3-6 | BACKFILL r2 §4.1 | 加备份两个 bundle 副本 |
| P3 | P3-7 | Data 消息 | 备用 r3.2 sha 申报 23d97887，实测 23d97884 |
| P3 | P3-8 | snapshot v2 L190-195 | RESTORED_TO_PIN 不核 BEFORE == pin |
无 P0 / P1。
