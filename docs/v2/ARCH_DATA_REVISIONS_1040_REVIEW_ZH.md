# Arch 审查：Data 10-18 修订包（SW r3.1 / 日历 r2 / 备用 r3.1 / sha 范围 / 快照脚本 / 勘误 / 补跑申请）

- 审查人：QuantLab Arch；签署时间：2026-10-18T10:49:04-04:00（ET）。
- 方式：只做静态审。Read / rg / sha256sum / stat / ls / find / tar -tv（只读成员头）；快照脚本复制到 /tmp/arch_rev_1040 后只做 py_compile，没有执行；没读任何 parquet 内容，没运行项目代码，没 git apply，没提交，没签 .ok，没发消息。
- 文中 L 指被审文件行号；「代码 L」指源码行号。live=false，promotion=false。
- 主 Agent 书面裁定（10:44 转达）已纳入：①方案 R 获批，条件②作废；②10-19 日历一律从备份原子恢复到 141078fa，内容比对保留，不一致记 P1。

## 0. 结论一览
| 文件 | sha256 | 结论 |
|---|---|---|
| SW r3.1 docs/v2/plans/DATA_SW_L1_PIT_V2_FIX_PLAN_ZH_r3_1.md | daa19d2695f2e42591712204a6e622dcd16801434d3dd4480c15d56d9490ddab | PASS with conditions：424f9021 的 P2/P3 全部关闭；新 P2 一条（selftest 正例必挂），改后可签 code-change .ok（10-19 纸面后） |
| 日历 2027 r2 docs/v2/plans/DATA_CALENDAR_2027_PACKAGE_PLAN_ZH_r2.md | c1b51e13aa923d35b294eb98b8563ae5781257d1120873885c55cf8ca9f804d7 | PASS with conditions：5d35e63c 的 P2/P3 全部关闭；新 P3 两条 |
| 备用 r3.1 docs/v2/plans/DATA_DAILY_FALLBACK_PUBLIC_SOURCE_PLAN_ZH_r3_1.md | 5071d1aefd74890034b2bf9bd12e025e2c08a21f455179855ed6c4c6d4065673 | PASS with conditions：f977d4b9 的 P2/P3 全部关闭；§4 L80 须随 10-19 恢复裁定改写；Q6 已裁 |
| sha 范围 docs/v2/audit/nightly_sha_scope_20261018.txt | b24a4a88b23efd8d1663238e6e590984afa08c719b5d397f589a87d9fc6319be | PASS：所要求的文件全部在列，与 closure 交叉核对 156/156；补跑与 10-19 各出一份专用范围（新文件） |
| 10:22 基线 docs/v2/audit/nightly_sha_baseline_20261018_1022.txt | dfdc25552918c7de24af240138fbc298d1ef2cb532723e18a6a4b7d892fb674c | PASS：本次 sha256sum -c 167/167 仍吻合（10:4x ET） |
| 快照脚本 docs/v2/audit/nightly_sha_scope_snapshot_20261018.py | 0aa6c6505a90aa7b09cb1c56b079695499a44515758a0da849aebfab29328e37 | CONDITIONAL：只 stat + sha256sum、无项目 import、不解析数据，成立；但输出路径不受限且非原子、元数据变化不判失败、不核范围 sha（3 个 P2）。今天补跑可在 .ok 补偿条件下用 v1；10-19 日更前须换新文件名 v2 |
| 勘误 docs/v2/audit/DATA_20261018_NEW_DOCS_ERRATA_ZH.md | ba2660a4ab972bf8167f00526e9bd11c7e3804c0fde5ea1f25aa169e48e01ad0 | 接受：四处未来时间已更正（L8-11）；管道违规补报（L18）记 Data P3，与 SW r3.1 §8 合并 |
| 补跑申请 docs/v2/audit/BACKFILL_1014_1016_OK_REQUEST_ZH.md | 122277e2f0c58a423e34ce23676bf8263a38660bbeefb1cf176708194bc252b7 | 方案 R：代码核对属实（不写任何 MUST_NOT_CHANGE 文件，不调用 daily_pull/daily_basic/events/eng_panels/trade_cal/sw）；按 §4 补齐备份、专用范围、RSS 线与逐步判定后可签 run .ok |

## 1. 逐条关闭核对
### 1.1 SW r3.1（对 424f9021）
| 项 | 位置 | 核对 | 结论 |
|---|---|---|---|
| P2-1 可签代码文本 | §2.1 L28-133（全文 diff，应用后 9bd69929）、§2.2 L135-169（对 r2 §6.2 增量）、§2.3 L171-234（nightly 全文 diff，基线 ec079d56 → 987e273d） | completed_et 带时区微秒（L85、L90）；pull_ok_sha256 = sha(所用 pull .ok)（L91）；先写 COMPLETE 后 consume（L92-94，L141）；跨 ET 午夜拒绝（L86-88）。基线 sha 本次复核：sw_pit_refresh.py a18684fe、nightly_update.py ec079d56、ok_runner_pin.py c7805d9a，均一致 | 关闭 |
| P2-2 归档与标记 | §3 L236-241；代码 L266-278、L317-321；selftest L389-404 | 父目录须为 _consumed、标记存在、标记 ok_sha256 = sha(归档)；三方 sha 一致；selftest 含标记缺失、字节变化、不在 _consumed 三例 | 关闭 |
| P2-3 PRIMARY_KNOWN_AT | §4 L243-249；常量 L257-262 | 取 2026-10-10T14:42:59-04:00；出处为 tar 成员头。本次 tar -tv 复核：data_v2_bundle/sw_l1_pit/industry_members_sw_l1_tushare.parquet，107038 字节，2026-10-10 14:42（box 时区 ET），属实。fetch_time 降为 PRIMARY_KNOWN_AT_FETCH；r3 L175-176、L785-786 替换位置正确；L900、L908 期望改为上海 02:42:59，L870 不变，r3 原行号复核属实 | 关闭（秒级值在 10-19 后探查 .ok 内核，只许提前） |
| P3-1 as_of | §5.1 L407-410；L323 | 取 completed_et 换算上海日期 | 关闭 |
| P3-2 两条时间检查 | §5.2 L412-414；L297-300 | signed_et ≤ completed_et、completed_et 不在未来（now 可注入）；manifest repull_evidence_chain（L333） | 关闭 |
| P3-3 越权读取 | §8 L432-436；勘误 L18 | 自报新的管道违规，改正办法可行 | 关闭（记 Data P3，累计） |
| P3-4 pub_backcast 并列 | §5.3 L416-417 | 回执硬要求同表并列与差值 | 关闭 |
- **新 P2-A（SW r3.1 selftest 正例必挂）**：test_repull_dir_validation_r3_1 在 L369 先取 done=now，再于 L373 写 801010.SI_Y.parquet，所以文件 mtime 晚于 done；validate_repull_dir 的 L307 检查（completed_et 早于目录内 mtime 即拒绝）会让 L376 的正例直接抛错。须改为写完文件后再取 done（或用 os.utime 把文件 mtime 设到 done 之前），并把 L382-385 的「未来」「早于」两例按新顺序复核。code-change .ok 签确切文本，此项不改不签。
- 提醒：文件头 L3「起草 10:30–11:00 ET」为未来时间，以勘误 L9 为准。

### 1.2 日历 2027 r2（对 5d35e63c）
| 项 | 位置 | 核对 | 结论 |
|---|---|---|---|
| P2-1 manifest 重写 | §2 L25-32 | 风险提示含 manifest（L27）；10-19 前后核对含 fa4260b8 与 7ccc911e（L28）；比对模式只写 output/data/trade_cal_compare_<stamp>/（L29）；selftest 用例 9、10（L31-32）。trade_cal_pit.py 90e3df43 复核一致 | 关闭 |
| P2-2 available_at | §3 L34-65；勘误 L15 | max(规则下限, 公告, 拉取完成)，代码强制、三者原值进 manifest、拒绝条件齐全；selftest 用例 11 | 关闭 |
| P2-3 受保护路径 | §4 L67-84 | 三个路径；pull 目录 exist_ok=False；selftest 用例 10。另报 daily_pull 写 tushare_raw/trade_cal.parquet（L85-88），已由本审 §5 处理 | 关闭 |
| P3-1 计数 | §5 L91-101 | 13 / 32 与 Arch 计数一致；撤回「46」 | 关闭 |
| P3-2 串行落地 | §6 L108-111 | 钉基线 + 应用后 sha，不同 .ok、不同天 | 关闭 |
| P3-3 成对命令 | §5 L102-106 | 每条有含 / 不含 _consumed 对照 | 关闭 |
| P3-4 | §1 L18 | 无需改 | 关闭 |
- 新 P3-a：_guard_write（L77-83）只按 resolve 后路径比较；允许目录里若出现指向受保护文件的硬链接可绕过。写出前再比 (st_dev, st_ino)，并要求写目标不存在（write 模式已用 os.link，pull 目录新建，可只补 inode 比较与一条 selftest）。
- 新 P3-b：公告只有日期时取当日 23:59:59 上海（L37），配合 L57 的「公告晚于拉取即拒绝」，等于要求公告次日才能拉取；方向保守，接受，但排期里写明。返回上海无时区墙钟（L61）须在实施时对照 fa4260b8 的列类型（由 Data 在只读探查 .ok 下核），不得凭推断。
- Q7 已裁（见 §5）；Q8（Eng 纸面日历 2027 延长）归主 Agent 指定 owner，建议与本包同期 12-15 前。

### 1.3 备用 r3.1（对 f977d4b9）
| 项 | 位置 | 核对 | 结论 |
|---|---|---|---|
| P2-1 黑名单第 4 项 / QL_FRESH_PATH | §2 L22-48 | 两个确切路径；环境中有 QL_FRESH_PATH 即拒绝、源码 ast 检查；run .ok 四个字段（L39）。写入方 data_freshness_status.py 代码 L9、读取方 research_loop.py L654/L665 复核属实 | 关闭 |
| P2-2 sha 清单范围 | §3 L50-73 | 三个目录全量 + 复用 b24a4a88（超集）；影子轨把 EXPECTED_CHANGE 一律按 MUST_NOT_CHANGE 核（L54）；六字段比对；范围文件自身先核 sha（L63） | 关闭 |
| Q2 全量 sha | §3 L55-57 | 采纳 | 关闭 |
| P3-1 行号 | §5 L82-83 | L169-179 | 关闭 |
| P3-2 自跑 rg | §6 L85-95 | 补充 tier1_materialize 真实写入行 L147，属实 | 关闭 |
| P3-3 | §8 L102 | 保留开放 | 关闭（不阻塞） |
| P3-4 ctime / inode | §3 L55、L64 | 采纳 | 关闭 |
- 须改：§4 L80 的「会影响 closure 与 10-18 基线一致的说法」按主 Agent 裁定改写为：10-19 日更后 tushare_raw/trade_cal.parquet 一律恢复到 141078fa，影子轨 BEFORE 时其 sha 应为 141078fa，inode / ctime 与 10-18 基线不同属预期；BEFORE 时 sha 不是 141078fa 即不启动并报 Arch。
- 若本审 §3 要求的范围文件改版，GUARD_FILE_SCOPE / GUARD_FILE_SCOPE_SHA256（L62-63）随之改钉。
- Q6 裁定：默认做 10-19 当日 + 5 日对照；15:15 ET 仍未开始联网时自动降为只做 10-19 当日，回执写明；16:00 / 16:30 规则不变。

## 2. sha 范围清单核对（b24a4a88，167 项）
| 要求 | 范围文件位置 | 当前 sha（本次复核） | 结论 |
|---|---|---|---|
| fa4260b8 calendar/trade_cal_sse_pit.parquet | L15 | fa4260b8… | 在列，MUST |
| 7ccc911e calendar/manifest.json | L16 | 7ccc911e… | 在列，MUST |
| tushare_raw/trade_cal.parquet 141078fa | L22 | 141078fa… | 在列，MUST（10-19 改为恢复类，见 §5） |
| output/data_freshness_status.json | L9 | f357de92… | 在列，EXPECTED |
| output/daily_update_status.json | L11 | 7991455a… | 在列，EXPECTED（补跑须改 MUST，见下） |
| 两份 events parquet | L26-27 | aab46c56… / 549a28c3… | 在列，MUST（.bak_rules_v1 副本不是读者路径，不需列） |
| closure 所钉全部文件 | L38-194 | — | 156/156 全在，且 156 个 pin 与当前文件 sha 全部一致；closure json 自身 6919e7af 也在列（L38）；范围多出的 11 项全是非 closure 的数据 / 状态文件，无重复 |
| 89d4afa3 / 87d769aa | L31、L35 | 89d4afa3… / 87d769aa… | 在列，MUST。说明：仓库里没有 configs/data 目录，这两个 sha 对应 data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet 与 industry_members_sw_l1.parquet，已复核 |
- 另列 0b1d3432 sw_pit L1（L33），同意。
- 要求（新文件，不改 b24a4a88）：
  1. 补跑专用范围 docs/v2/audit/nightly_sha_scope_backfill_1014_1016.txt：daily_update_status.json 改为 MUST_NOT_CHANGE（方案 R 无写入方，见 §4.1；回答申请 Q5：同意更严）；增列 data/v2/asof_extend_202610/calendar.parquet（纸面 trade_calendar.py 代码 L13 / L27 交叉核对读它）与 §4.3 备份清单中的文件（tier3 10-13/14/15、cyq 202601-202609、cyq 原始 ≤20261013）为 MUST_NOT_CHANGE。
  2. 10-19 日更专用范围：tushare_raw/trade_cal.parquet 单列一类 [RESTORED_TO_PIN]，判据为恢复后 sha = 141078fa，inode / ctime 变化允许；其余同 b24a4a88。
  3. 两份新范围文件交 Arch 审，sha 写进对应 .ok。

## 3. 快照脚本（0aa6c650，/tmp 静态审，未执行）
- 成立的部分：只 import 标准库（L5），无项目 import；只读范围文件（L9）、对所列文件跑 sha256sum（L20，stdin=DEVNULL）与 os.stat（L29）；不解析任何数据内容；路径为绝对路径，不依赖 cwd；sha256sum 任一文件缺失即退出 2（L21），失败即停。
- **P2-S1 输出路径不受限且非原子**：L32 open(out,"w") 直接截断写，out 可以是任意路径（包括范围内文件或 data/ 下文件）；已存在即覆盖。要求：out 解析后必须位于 /tmp/arch1018/ 或 docs/v2/audit/sha_snapshots/ 之下，不得在范围清单内，目标已存在即拒绝（O_EXCL），写同目录临时文件 → fsync → os.replace。
- **P2-S2 元数据变化不判失败**：L51-52 对 MUST_NOT_CHANGE 文件 sha 相同但 mtime / ctime / inode 不同时只打印 META_ONLY_CHANGE，退出码仍 0。按 f977d4b9 Q2 裁定，ctime / inode 变化须判 FAIL（退出 1），只有 [RESTORED_TO_PIN] 类例外。
- **P2-S3 不核范围一致**：compare（L43-53）用当前范围文件的分类，不核 BEFORE / AFTER 头部的 scope_sha256 是否相同、是否等于 .ok 钉的范围 sha。要求加 --scope-sha 参数，三者不一致退出 2。
- P3：stat 在哈希之后（L29），哈希期间被写可漏判，改为哈希前后各 stat 一次并要求相同；无参数时 L54 IndexError 退出 1，会与「MUST 有变化」混淆，改为退出 2；json 未使用（L5）；meta 不比 size（sha 相同时无实质影响）。
- 位置：docs/v2/audit 下已有 13 个 arch_*.py 审计脚本，先例成立；它不是代码目录，不会被 import。接受放在此处，条件：只用显式路径在 .ok 下运行；任何修改换新文件名（v2），0aa6c650 原样保留不再用于 10-19；sha 写进 .ok。
- 今天补跑用 v1 的补偿条件（写进 run .ok）：输出只写 /tmp/arch1018/backfill_*.txt 新文件名（运行前 ls 确认不存在）；compare 输出出现任何 META_ONLY_CHANGE 行（daily_update_status 与范围内全部 MUST 项）一律按退出码 1 处理；每次 compare 前人工 sha256sum 范围文件与两份快照头部 scope_sha256 比对。10-19 05:55 前必须换 v2 并经 Arch 审。

## 4. 方案 R 代码核对（nightly_update.py ec079d56；cyq 6aae6c1b；tier3 64a71f56；freshness a759d297；relay_health 6d3ea9f5；tushare_proxy ae91f230，均复核一致）
### 4.1 调用面
- nightly 只执行 --steps 列出的步骤（代码 L101、L104）；cyq / tier3 走 RELAY_STEPS 先调 relay_up（L109-112），bundle 是进程内函数（L107-108），freshness 为子进程。
- 四个步骤的脚本只 import quantlab.data_sources.tushare_proxy（不写任何文件）与 relay_health；没有一个 import 或调用 tier1_pull / tier1_materialize / eng_daily_panels / _light_event_windows_pull / forecast_manifest_declare / trade_cal_pit / sw_pit_refresh。**daily_pull、daily_basic、events、eng_panels、trade_cal、sw 均不会被调用，属实。**
- daily_update_status.json：四个步骤都不写（rg 无写入点）。data_freshness_status.json：只有 freshness 写（代码 L85，先写 .tmp 再 os.replace，原子但无 fsync）。bundle 不写任何状态 JSON。
- tushare_raw/trade_cal.parquet：cyq 只读（cyq 代码 L16），不写。calendar/trade_cal_sse_pit.parquet：freshness 只读（代码 L10、L59、L77）。

### 4.2 预期变化清单（逐次）
| 运行 | 写入 | 方式 | 类别 |
|---|---|---|---|
| 每次 | output/relay_health.json（缓存超 5 分钟才重写，relay_health L16） | 非原子 | 预期 |
| 每次 | logs/nightly/<日期>_<步骤>.log 追加；logs/nightly/<日期>_summary.json 合并重写（L130-137）；logs/nightly/backfill_20261018_runN.out | 非原子 | 预期（summary 先备份） |
| 中转不通时 | output/relay_outage_backfill_queue.json（L86-95，只追加） | 非原子 | 条件性（先备份） |
| run1 cyq | 新增 data/v2/tushare_raw/cyq_perf/20261014、20261015、20261016.parquet（cyq L42-48：上海今天 20261018 之前、202610 的开市日中缺文件或 ≤10000 字节者；现有 1008/1009/1012/1013） | 非原子新建 | 预期 |
| run1 cyq | 重写 data/v2/cyq/cyq_perf_202610.parquet（L52-58，整月从原始文件重建） | 非原子覆盖 | 预期，须先备份 |
| run1 cyq | 重写 data/v2/cyq/manifest.json（L61-66，months.202610 更新，built 必变） | 非原子覆盖 | 预期，须先备份 |
| run2、run3 cyq | 无新增日；仍会重写 cyq_perf_202610.parquet 与 manifest.json（内容应同 run1，built 变） | 非原子覆盖 | 预期。建议（申请 Q3）只在 run1 跑 cyq，run2 取消、run3 去掉 cyq；Data 若保留，按本行判定 |
| run3 tier3 | 新增 data/v2/tier3_daily/{concept_dc_index,concept_dc_member,anns,news,research_report}/20261016.parquet（返回非空才写），concept_ths_index 预计 blocked；新增 data/v2/tier3_daily/manifests/20261016.json | 非原子新建 | 预期 |
| run3 bundle | 覆盖 output/data_v2_bundle/ 下副本：BUNDLE_MAP 15 项（L46-62，含 sw_pit 五个文件的副本）、cyq/cyq_perf_*.parquet 全部月份、tier3_daily/*/20261016.parquet（L79-82） | copy2 截断写，非原子；源文件只读 | 预期。已核 bundle 副本与 sw_pit 源不是硬链接（inode 2334756 ≠ 2146886），不会写穿 |
| run3 freshness | output/data_freshness_status.json（+ 临时 output/data_freshness_status.tmp） | 原子替换 | 预期 |
- **tier3 是否覆盖 10-14 / 10-15**：不会。写入路径按 --date 命名（tier3 L28 BASE/kind/{d}.parquet，L60 manifests/{d}.json），--date 20261016 只写 20261016 文件；bundle 也只复制 {d} 文件（L80）。所以主 Agent 裁定①的「若覆盖则备份」条件按代码不触发；但备份成本很低，仍要求执行（§4.3），跑后按「必须不变」核。
- **方向**：freshness 的 expected_trade_date 保持 20261016（ET 12:00 前上海是 10-18 非开市；12:00 后上海是 10-19 开市但未到 20:00，取前一开市日，代码 L60-61）；tables 各核心表不动，last_date 与 sha256 应与跑前相同；warn_tables 中 cyq_perf_raw 由 20261013 前进到 20261016、tier3_*（concept_ths_index 除外）由 20261015 前进到 20261016。daily_update_status 不动。
- **注意 1（PIT）**：tier3 manifest 的 available_at 写死为「20261016 20:00 上海」（L34），而实际拉取在 10-18 / 10-19 上海；回执须记实际拉取时间，tier3 10-16 视为回补快照。concept_ths_index 不带日期（L39），若中转返回真实数据，20261016 文件其实是 10-18 的目录，回执须标「非 10-16 时点」，不计为 10-16 快照。tier3 promotion=false，无纸面读者，不阻塞。
- **注意 2**：cyq 与 tier3 单日失败仍退出 0（cyq L50、tier3 L57-58），relay_up 把 HTTP <500 都当作通（relay_health L12），所以 status=ok 不代表成功，只按 §4.4 判。
- **注意 3（内存线）**：申请 §9 L177 用 1.5GB = 1572864 kB 作中止线，不对。按团队硬约束：单进程 RSS 硬线 1536000 kB，包装器停止线 1484800 kB；采样 > 1484800 即按 §10 中止。
- **注意 4（解释器）**：历史日更用 /usr/bin/python3（3.13.5，pandas 3.0.6，pyarrow 26.0.0；10-14..10-16 日志首行），命令里写 python3 时 PATH 也解析到它；.ok 钉 /usr/bin/python3 的绝对路径。

### 4.3 备份（按主 Agent 裁定①，写进 run .ok）
- run1 之前，cp -p 到 _recovery/data/backfill_1014_1016/（保持相对路径），并写 sha 清单 SHA256SUMS（sha256sum 输出原样）：data/v2/cyq/cyq_perf_202610.parquet、data/v2/cyq/manifest.json、logs/nightly/2026101{4,5,6}_summary.json、output/relay_outage_backfill_queue.json、output/relay_health.json。
- run3（10-16 那次）之前再备份：data/v2/tier3_daily/{concept_dc_index,concept_dc_member,anns,news,research_report}/2026101{4,5}.parquet 与 data/v2/tier3_daily/manifests/2026101{4,5}.json；同时核对 20261016.parquet 与 manifests/20261016.json 跑前不存在（ls 证据）。
- 跑后：tier3 10-13/14/15 与 cyq 202601-202609、cyq 原始 ≤20261013 必须逐字节不变（专用范围文件 MUST）；cyq_perf_202610.parquet 与 cyq/manifest.json 为有意变化，按 §4.4 判；若 run1 cyq 判 FAIL 且 cyq_perf_202610 行数低于跑前 22238，用备份原子恢复（同目录临时文件 → sync → mv -T），恢复后 sha 等于备份 sha。

### 4.4 逐步判定（只看本次，status 字样不作数；读 parquet 只许读元数据 num_rows，在 run .ok 内由 Data 做）
| 运行 / 步骤 | 必须全部满足 |
|---|---|
| 全部 | 94322 全程 T（STOP 前后、每次运行前、CONT 后 ps 与 /proc/94322/stat 证据）；一次一个进程；每次运行后快照 + compare：MUST 项零 DIFF、零 META_ONLY；daily_update_status 仍为 7991455a；RSS 采样 ≤ 1484800 kB；16:00 ET 前结束 |
| run1 cyq | summary steps.cyq.status=ok 且无 RELAY_DOWN；本次日志段有 20261014、20261015、20261016 三行「日期 行数」、无 FAIL；每天行数 ≥ 5000；三份原始文件存在、各 > 10000 字节，num_rows 等于日志行数；manifest months.202610：new_days=3、fails=[]、days=7、range=[20261008, 20261016]、rows = 22238 + 三天日志行数之和（精确相等，不用 ±3%）、codes ≥ 跑前值；cyq_perf_202610.parquet num_rows = manifest rows；manifest 中 202601-202609 条目与备份逐字段相同；顶层 date_range 末端 20261016 |
| run2 / run3 cyq（若保留） | new_days=0、fails=[]；months.202610 的 rows / days / range / codes 与 run1 后相同 |
| run3 tier3 | manifests/20261016.json：concept_dc_index ok 且 rows 900–1200；concept_dc_member ok 且 rows 80000–110000；news ok 且 rows ≥ 1000；anns、research_report 为 ok 或 empty（不算失败）；concept_ths_index blocked 可接受（若 ok，按 §4.2 注意 1 标注）；每个 ok 项的 20261016.parquet num_rows = manifest rows；10-14 / 10-15 备份文件 sha 不变 |
| run3 bundle | summary steps.bundle.files 含 cyq/cyq_perf_202610.parquet 与 tier3_daily/*/20261016.parquet；这些副本 sha = 源文件 sha；sw_pit 源 0b1d3432 不变 |
| run3 freshness | generated_at_et 落在 run3 时间内；expected_trade_date=20261016；overall=ok；stale_tables=[]；tables 各项 last_date 与 sha256 与跑前 freshness 文件（备份）逐项相同；tables.trade_cal.sha256 = fa4260b8 全长；warn_tables.cyq_perf_raw.last_date=20261016、lag 0；tier3_*（除 concept_ths_index）last_date=20261016 |
| 中止 | 任一条不满足即不起下一次运行，照常做跑后快照与 compare，照常 CONT 94322，报 Arch |

## 5. F1：tier1_pull.py（b630bca2）日历刷新与 10-19 处理
### 5.1 代码事实
- 代码 L85 经 datahub（_call 失败时回落 relay，L17-20）拉 SSE 20260901–20261231；L87 读旧表；L89-90 两边 cal_date astype(str)；L91 剔除重叠日期；L92 pd.concat([keep, cal]) 不排序，直接 to_parquet 覆盖原路径（截断写，非原子，无 fsync）；L94-95 的 except 吞掉所有异常，包括写到一半的失败，此时文件可能已损坏，而 daily_pull 继续并可能退出 0。与 --date 无关、与中转是否宕机无关。
### 5.2 是否逐字节稳定
- 理论上可确定：parquet 不含写入时间；行序为「旧表非重叠行原序 + 供应商返回序」，第二次起前半段不变；所以只有在供应商返回的行、顺序、列类型完全相同，且 pandas / pyarrow 版本相同（pandas 元数据写入版本号）时才逐字节相同。
- 会打破字节稳定而内容不变的情形：datahub 失败回落 relay 后列类型不同（如 is_open 为字符串、pretrial_date 全空与非空导致 null 类型 / 字符串类型切换）、供应商改变返回顺序、换解释器（qlvenv 为 pyarrow 25.0.1，日更为 26.0.0）。
- 证据：全机 find 只有这一份 trade_cal.parquet，无历史副本；文件不在 git；当前 mtime 2026-10-18 01:08:43 ET 是恢复时间。141078fa 是 10-18 00:19 ET（20261016 那次 daily_pull 日志首行）刷新之后的状态，但无法证明前几次刷新的字节相同。结论：**可能稳定，无法证明**，所以 10-19 按主 Agent 裁定一律恢复。
- 读者侧：trade_calendar.py 代码 L22 用 exchange=="SSE" 与 is_open.astype(int)==1，cyq 代码 L16 同样 astype(int)，对类型漂移有一定容忍；但比对仍按严格类型判。
### 5.3 内容比对规则（选项 b 的判据，结果只作 P1 判定，不决定是否恢复）
- 由 Data 写一个只读比对脚本（标准库 + pyarrow，只读备份与跑后文件这两份约 95 KB 的文件），Arch 审后在 10-19 日更 .ok 内运行；快照脚本不做这件事。
- 判据，全部满足才算「内容一致」：
  1. 两份都能完整读出（跑后文件损坏或截断即「不一致」）；
  2. 全文件比，不只比 20260901–20261231 窗口；
  3. schema：列名与顺序和备份完全相同（预期 exchange、cal_date、is_open、pretrial_date，以备份实际 schema 为准），每列 arrow 类型与 pandas dtype 相同；
  4. 行数相同；(exchange, cal_date) 在两份里都无重复；
  5. 两份都按 (exchange, cal_date, is_open, pretrial_date) 排序（空值排最后）并重置索引后逐格相同（空与空视为相同）；
  6. 两份都有 exchange=SSE 的 20261019 与 20261020 行，且 is_open=1；
  7. 输出：前后 sha、行数、schema、不一致行数与前 10 个键，写成新文件进 docs/v2/audit/。
- 不一致记 P1，立即报 Arch 与主 Agent，并在 10-19 17:00 ET execution.py 核对前定纸面是否照跑；无论一致与否，文件都按 §5.4 恢复。
### 5.4 备份与恢复（每次都恢复）
- 时序要求：纸面日常例程约 06:37 ET 起读这份日历（trade_calendar.py CUTOFF 06:30），而完整日更约 53 分钟，跑完已过 06:37。所以 10-19 日更须拆成两次调用：调用 A 只跑 --steps daily_pull；随即比对并恢复；恢复核验通过后才起调用 B（其余步骤，仍不含 trade_cal、sw）。恢复须在 06:30 ET 前完成，做不到就报主 Agent 让例程等待。
- 调用 A 之前：
  1. mkdir -p _recovery/data/nightly_20261019/；
  2. cp -p data/v2/tushare_raw/trade_cal.parquet _recovery/data/nightly_20261019/trade_cal.parquet.141078fa；
  3. sha256sum 源与备份都等于 141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086，否则不跑；
  4. chmod a-w 备份；stat 记录源的 size、mtime_ns、ctime_ns、inode。
- 调用 A 之后（不论日志是 cal refreshed 还是 cal refresh skip）：
  1. cp -p 当前文件到 _recovery/data/nightly_20261019/trade_cal.parquet.post_daily_pull，记 sha（作为比对输入与证据）；
  2. 跑 §5.3 比对，记录结果；
  3. cp -p 备份到同目录临时文件 data/v2/tushare_raw/.trade_cal.parquet.restore_tmp，sha256sum 等于 141078fa，sync 该文件；
  4. mv -T -f 临时文件到 data/v2/tushare_raw/trade_cal.parquet（同一文件系统 rename，原子），再 sync 所在目录；
  5. sha256sum 目标等于 141078fa，stat 记录新 inode；第 3 步 sha 不符则不 mv，立即报 Arch 与主 Agent（P0，纸面日历状态不明）；
  6. 快照 compare 中该文件按 [RESTORED_TO_PIN] 判：sha 必须 141078fa，inode / ctime 变化允许。
- 可选加固（主 Agent 定，不是本审要求）：调用 A 前对源文件 chmod a-w，box 用户（uid 1000，非 root）下 L92 的写入会因权限失败并被 L94 吞掉，文件不被改写；代价是 ctime 变化，且仍须执行上面的恢复与比对。
- 之后的选项 (c)（只读日历开关 / 改写新目录）在 10-19 纸面跑完后另走 code-change .ok。

## 6. 给 Data 的下一步
1. SW r3.1：按 P2-A 修 selftest，出 r3.2 增量（只含该处）；落地仍在 10-19 纸面之后。
2. 补跑：交补跑专用范围文件、§4.3 备份清单与命令、两次探测证据、钉 /usr/bin/python3 与 §4 各脚本 sha 的 run .ok 申请；RSS 中止线改为 1484800 kB；16:00 ET 前跑完，否则放弃。
3. 10-19：交快照脚本 v2（新文件名）、10-19 专用范围文件、§5.3 比对脚本、§5.4 两段式命令，Arch 审后签日更 .ok。
4. 备用 r3.1：按 §1.3 改 §4 L80 的写法，随 code-change 申请一并提交。
