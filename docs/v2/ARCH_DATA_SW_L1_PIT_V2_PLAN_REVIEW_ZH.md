# Arch 审查：Data 申万一级 PIT v2 修复方案（静态审）

- 审查对象：docs/v2/plans/DATA_SW_L1_PIT_V2_FIX_PLAN_ZH.md
- 钉住 sha256：2d9f5b8e9981a9d75366622779c6d2c57422154a2c29fe8f1736e9efc62f2ee8（49296 字节）；读前两次（间隔约 5 秒）、读后一次核对均一致；审的是 /tmp 下 cp -p 的副本。
- 审查时间：2026-10-18T07:04:33-04:00
- 方式：只做静态审。没运行方案里的任何代码，没读 parquet、价格或因子数据，没 git apply。§6.2、§6.3 代码抽到 /tmp：py_compile 通过；pyflakes 4.0.3（PYTHONPATH=/tmp/pf）无告警。另外只读了这些：scripts/acquire/sw_pit_refresh.py（a18684fe，和方案一致）、scripts_eng/ok_runner_pin.py（c7805d9a，git 未跟踪）、scripts/nightly_update.py、queue_chain_20261014.py、measure_baseline.py 的相关行（只看代码），以及 SW_95_vs_117_RECON.csv（493f3621，审计证据）。
- 行号 L 指被审文件的行号。

## 结论：有条件通过
- **方案层面通过**：七条规则、首次写入以 89d4afa3 为基线的硬闸门、以内容证据代替时间证据、实施日重拉为硬条件、95/117 对账、13 只在 10-14 前丢失、排期，都和 Arch 裁定一致。
- **代码文本不通过**（§6.1/§6.2/§6.3）：有 3 个 P1、11 个 P2。须按下文“签 code-change .ok 前必改项”修订，连同全文重交（r2）。**不按本 sha 签 code-change .ok。**
- live=false，promotion=false。

## 与 Arch 裁定的一致性核对
| 裁定 | 方案/代码 | 结论 |
|---|---|---|
| 89d4afa3 为主来源，条件 (a) 成立（94e91ffa） | L57、L66、L623；代码 L161-162、--primary 默认 89d4afa3（L361） | 一致；但 L154、L399 仍写 conditionally_accepted（见 P3-1） |
| 时间戳丢失，接受内容证据 | L82、L617；manifest time_evidence（L350） | 一致 |
| 实施日重拉到新目录是硬条件 | L71；--repull_dir 必填（L360） | 有该参数，但没校验它是否独立（见 P2-7） |
| 首次写 v2：以 89d4afa3 为硬基线，行数、代码数阈值 0，每个键都保留，补 out_date 键不变，删除的行写进 conflicts 并仍被拦，不接受 --allow-shrink | L100-103；代码 L379-388、L291、L298-302、L319-325；selftest L502-525 | 逻辑一致；但键比较方式脆弱（P2-2），删行逻辑和硬闸门冲突（P2-4） |
| 与 0b1d3432 的比较只写进 info | L102、L389；selftest L527-532 | 一致 |
| 当前成员降幅扣除退市后 ≤0.3% | L95、L303-307；selftest L485-500 | 只对后续刷新生效，而后续刷新的 prev_built 永远取不到（P2-5） |
| 95 与 117 对账（493f3621） | L648-653 | 接受；正文列表漏 1 只（P3-4） |
| 46 只中有 13 只在 10-14 前就已丢失 | L588、L656-659 | 一致；丢失机制须标为推测（P3-3） |
| “bak 自身是截断拉取”只作推测 | L644 已标 hypothesis | 一致；L629 的待决项要关闭（P3-3） |
| 09-24..10-09 增量核查：Data 开放项，不阻塞方案审 | L67、L568、L628 写成“待 Arch” | 归属写错（P3-2） |

## 发现

### P1
- **P1-1 代码里没有运行门禁，selftest 的 enforce 调用写错。** §6.2 的 main()（L356-402）和 §6.1 的 sw_pit_refresh 都没调用 ok_runner_pin.enforce。dry-run、execute、实施日重拉都会读真实数据或写 repo，代码层面却不校验 .ok，也区分不了 dry-run 和 execute 的授权。§6.3 L416-417 写的是 `enforce(modes=["selftest"])`，而真实签名是 `enforce(script, ok_paths, modes=(), deps=None)`（ok_runner_pin.py L78），一运行就会 TypeError。ok_runner_pin.py 目前在 git 里未跟踪（??），按已定顺序要先提交。
- **P1-2 代码规范化会崩，或产生同一证券的两个 id。** to_iid（L183-184）遇到不带点的代码（如 T00018）直接 ValueError。如果后缀写法和 89d4afa3 的 instrument_id 不同，fill_from_full（L217-222）会把同一证券当成“缺失代码”按 rank2 补进来，形成两个 id，assert_one_open 拦不住。方案也没给出 89d4afa3 中 instrument_id 格式的证据，而已知 62 个 raw 重建出来的唯一差异恰好是 T00018 的写法（L66）。
- **P1-3 没有规则处理 10-10 之后到实施日之间的变化。** 6a 默认只用 89d4afa3（10-10 抓取），全量补缺用的 FULL（L164）是 10-14 那次被截断的旧全量文件，没钉 sha，§6.1 改完后它也不会再更新。实施日（最早 10-20 之后，可能到 12 月）重拉到的新上市代码、新的 closed/open 变化会让 normdiff_vs_repull 不为空，execute 被拦（L395-396）。到时只能逐只写 normdiff_allow 或切到 6b，方案两种都没写清楚。gap2（09-24..10-09）的结论也没有落到代码里的入口。

### P2
- **P2-1 日期解析（L194-198）。** to_datetime(errors="coerce") 没指定 format。整数 YYYYMMDD 会被当成纳秒 epoch。非法 out_date 会被悄悄变成 NaT，也就是变成 open 记录，等于编造在任成员。这违反“不编造”。
- **P2-2 键比较依赖 astype(str)（L299-300、L314-315、L320-321）。** pandas 把 datetime 列转字符串的格式取决于整列是否全是零点。只要一侧有非零点时间，或者精度（us/ns）、时区不同，所有键都会被判为丢失，闸门误拦且无法通过，info 也会失真。qlvenv 的 pandas 3.0.6 保留 us 精度，两侧精度可能不同。
- **P2-3 out_date 口径没定。** RECON CSV 显示 out_date 是最后在任日。例如 000030：801230 止于 2013-06-28（周五），801880 从 2013-07-01（周一）开始。daily_missing（L267）用 out_date>d，换行业当天会被算成缺失。这和 Intel 单测“出表当天仍是成员”不一致（影响文档 94e91ffa §3 L47）。窗口内一旦有换行业，§8 预期的“修后 0 缺失”就不成立。
- **P2-4 resolve_open_closed 的删行和硬闸门冲突。** 有多条 open 时直接删掉较旧的那条（L230-232），会丢键，硬闸门拒绝且不能覆盖。同一键既有 open 又有 closed 时删掉 open（L227-229），行数下降，被“行数阈值 0”拒绝。§8 L589 写的是“改为 closed”，代码做的却是删除。如果 89d4afa3 里有这两类情况，6a 就无法完成。
- **P2-5 输出版本化之后没有“上一版本”指针。** §6.0 L89 写的“manifest 指向的最近一份已审版本”没有实现：
  - sw_pit_refresh 的 l2 闸门永远在和没有版本号的旧 industry_members_sw_l2_pit.parquet 比（L143-145）。
  - v2 manifest 写的键是 built_et（L352），prev_built_from_manifest 读的却是 built（L286），所以后续刷新永远不会扣除退市。如果改成读 built_et，带时区的值和不带时区的值比较（L281-282）会 TypeError。
  - OUT 是固定文件名，加上 FileExistsError（L397），v2 只能写一次，L103“之后的刷新以 v2 为基线”没有实现路径。
- **P2-6 sw_pit_refresh 的 diff 不完整，也不能直接 apply。**
  - 原文件 L20-21 的 classify_l1/l2 仍然覆盖写。
  - 分拉失败只 print 一下就继续（L126）。重拉目录被截断时照样会产出，这正是 10-14 的失效方式。
  - 分拉结果先 append 再落盘（L124-125），落盘失败会造成内存和目录不一致。
  - §7 第 4 步要求“只拉，不建表”，脚本却仍然建 l2、raw union 和 manifest，需要一个 --pull-only 模式。
  - nightly_update.py L39 仍注册着 sw 步骤；L54-58 的 BUNDLE_MAP 复制固定文件名，版本化之后 bundle 会复制陈旧文件。
  - hunk 头的行数不对：@@ -2,4 +2,8 @@ 实际是 4→7，@@ -26,9 +30,11 @@ 实际是 7→9。
- **P2-7 输入没有钉 sha，重拉目录不校验独立性。** 代码只校验了 PRIMARY 的 sha。FULL、PREV（0b1d3432）、STOCK_BASIC（2ef2d71d）、DELISTED（9d757b96）、CAL（fa4260b8）、RAW_0108 都没校验。--repull_dir 可以直接传 RAW_0108 本身（L360、L365），交叉核验就形同虚设。
- **P2-8 自造的 .ok 校验（L271-277）。**
  - scope 用子串匹配，no_allow_shrink 也会命中。
  - 不查 live/promotion=false、allow_*、单次使用、tz-aware。
  - Arch .ok 的格式里没有 scope 键，所以合法的 .ok 也过不了。expires_et 不带时区时会 TypeError。
- **P2-9 安全检查靠 assert，写盘不是原子的。** L201、L207、L236、L293、L396、L398 在 python -O 下全部失效。L398 直接 to_parquet(OUT)，中途中断会留下半个文件，下一次运行 first_write=False，就会拿半个文件当基线。PROTECT 检查在写盘之后才做。manifest 的写入也不是原子的。
- **P2-10 normdiff 只比较 open 成分（L253-257）。** closed 历史（包括 gap2 期间补写的 out_date）不在交叉核验范围内。
- **P2-11 v2 schema 和消费方契约。** COLS（L173）丢掉了 ts_code、name、source。消费方（如 strategy_hiliq_capadv_b4_x2.py L72-76 load_industry_map）是按 0b1d3432 的列来读的。in_date 的精度、时区、out_date 口径都没写进契约。

### P3
- **P3-1 文本陈旧，或和裁定不一致：**
  - L97“首次构建需 allow_shrink .ok、baseline=none”和 L100/L103 矛盾，应限定为 sw_pit_refresh 没有基线的情形。
  - L165 的注释“0b1d3432: 闸门基线”已过时。
  - L408“与 0b1d3432 比只会增长”已过时。
  - L154、L399 的 conditionally_accepted 应改为 accepted（condition_a_met, 94e91ffa）。
  - L54、L61 写“标 quality_status=source_gap”，代码 L251 却把所有行都写成 ok，缺口只单独列成清单。
- **P3-2 归属写错。** L67、L568、L628 把 09-24..10-09 增量核查写成“待 Arch”。它应是 Data 的开放项，实施前完成，不阻塞本次方案审。
- **P3-3 推测要标成推测。** L629 的待决项应关闭为“bak 截断只作推测（hypothesis）保留”。L658 说 13 只是因“全量分页截断或陈旧版本”丢失，也要标为推测。
- **P3-4 §12.1 列表少 1 只。** L653 只列了 21 只，CSV 493f3621 是 22 只，漏了 300893.SZ。
- **P3-5 参数和目录名不一致。** L569 写 --raw_dir，代码里实际是 --primary repull 加 --repull_dir。L71 的目录名是 <YYYYMMDD>，§6.1 L120 是 <YYYYMMDD_HHMMSS>。
- **P3-6 在市口径前后不一致。** load_listed_universe（L243-245）不管退市日期，把 stock_delisted_v2 里的代码全部剔除。delisted_between（L279-282）只用 stock_basic，不用 stock_delisted_v2。在市口径不含 .BJ，这一点要写明。
- **P3-7 dry-run 的产出和判定。** out_dir 用 exist_ok=True（L334），会覆盖之前 dry-run 的证据。dry-run 总是以 0 退出，所以成功与否不能只看退出码，要看 shrink_gate.json、各 normdiff、source_gap、conflicts 的计数。
- **P3-8 排期和 .ok 清单。**
  - §1 的排期符合要求：在叶23 r2.11、叶24、10-19 纸面之后，避开 16:40-18:40 ET，和日历包同批。但没写 12-15 截止。
  - §7.1 的 .ok 清单缺实施日 relay 重拉的 .ok。重拉读真实数据，算一次运行。清单也缺 .ok 消费归档规则。
  - L18“叶23/24 的 .ok 都要重签”说得太宽。它们钉的是 89d4afa3，这份不变，只有迁移到 v2 时才要重签。
- **P3-9 §13 和 Arch 影响文档（94e91ffa）的对比。**
  - 6 个消费方两边一致。§13 还多列了 measure_baseline.py:48，94e91ffa 没列，是 Arch 漏了；已核实它在 L47-48 读 0b1d3432。
  - §13 漏了三处：nightly_update.py 的 BUNDLE_MAP（L54-58）、queue_chain_20261014.py L130（读 sw_pit/manifest.json）、intel_common 的 sw_members_asof（L309）。
  - Strategy 两个脚本缺行号：hiliq 是 L72-76、L316，fulla 是 L255。
  - 要写明：读 89d4afa3 的消费方（g1g5、cs_panel、纸面）不在这次迁移范围内。
- **P3-10 内存。** 预估 <300MB 合理，远低于 1.5GiB 硬线。

## 签 code-change .ok 前必改项（r2 重交全文）
1. P1-1：
   - build、refresh、重拉三处的入口最先调用 enforce(__file__, ok_paths, modes=[...])，dry_run、execute、pull、selftest 各用各的 mode。
   - 改正 selftest 的调用。
   - 先提交 ok_runner_pin.py。
2. P1-2：
   - 写一个唯一的规范化函数，用正则白名单 ^\d{6}\.(SH|SZ|BJ)$ ↔ ^(sh|sz|bj)\.\d{6}$。
   - 写明非 A 股代码（如 T00018）的政策：剔除或保留都行，但要写进 conflicts/manifest。
   - 规范化后，89d4afa3 和 raw/full 必须同格式；补缺之前先按规范化后的 id 求差集。
3. P1-3：二选一，并写进 §7 和代码：
   - (a) v2 的 as_of 定为 89d4afa3 的 fetch 日（10-10），重拉差异全部写入回执，另立 v2.1 增量；
   - (b) 定义“重拉只追加新键、只补 out_date、不删键”的合并规则（仍过硬闸门）。
   - 两种都要把 gap2 结论接进来。FULL 必须钉 sha，或者改用重拉。
4. P2-1/P2-2：
   - 日期用显式 format 解析；coerce 前后的 NaT 数必须一致，否则拒绝；统一成 datetime64[us] 零点。
   - 键比较用 strftime("%Y%m%d") 加规范化后的代码。
   - selftest 增加 us 对 ns、YYYYMMDD 字符串对 datetime、整数日期、非法 out_date 的用例。
5. P2-3：写死 out_date 口径，在 manifest、§13 契约和 daily_missing 里统一。建议 in_date<=d<=out_date，同时通知 cs_panel 和 Intel。
6. P2-4：较旧的 open 改为补 out_date（新 in_date 的前一交易日），保住键；完全重复的行先去重，行数闸门按去重后的行数算。或者在 dry-run 之前，用只读计数证明 89d4afa3 里这两类都是 0（这一步需要 .ok）。
7. P2-5：加“已审版本指针”文件，由 Arch 审完回执后更新；时间一律用 date-only 或 tz-aware；读写用同一个键。
8. P2-6：
   - 基于 a18684fe 重新生成 diff，hunk 头要正确。
   - classify 文件也版本化。
   - 分拉失败要非零退出，并写 INCOMPLETE 标记。
   - 加 --pull-only。
   - 同一份 diff 里停用 nightly 的 sw 步骤，修 BUNDLE_MAP。
9. P2-7：
   - 所有输入钉 sha，写进代码常量和 manifest。
   - repull_dir 不能等于 RAW_0108；目录日期要等于实施日；文件 mtime 要晚于 run .ok 的 signed_et；raw 文件的 sha 写进回执。
10. P2-8：复用 ok_runner_pin.parse_ok/enforce，用 allow_allow_shrink、allow_normdiff 精确匹配，normdiff_allow 逐条列出。
11. P2-9：所有 assert 改成显式 raise；写盘走“tmp → 校验 sha、PROTECT、行数 → os.link 不覆盖”，manifest 同样原子写。
12. P2-10/P2-11：另出一份全键 normdiff 报告；§13 加 v2 schema 和契约（列、精度、时区、out_date 口径），并给出和 0b1d3432 的列映射。
13. P3 项一并修订，不单独阻塞。
14. 开放项（不阻塞本次审）：Data 的 09-24..10-09 增量核查，实施前交。

## 不确定
- 89d4afa3、FULL、0b1d3432 的实际列名和 dtype（sw_code/sw_name、instrument_id 格式、日期精度）本次没读，因为规则不允许读数据。P1-2、P2-1、P2-2 的实际触发程度取决于这些。
- 89d4afa3 里有没有多条 open、有没有同键 open/closed（P2-4），未知。
