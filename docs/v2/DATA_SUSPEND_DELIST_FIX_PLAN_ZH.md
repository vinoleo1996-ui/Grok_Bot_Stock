# D-2 / D-3 / D-4 修复方案 r5（SD1 引擎输入）

QuantLab Data，最后修改 2026-10-18 02:05 EDT（以 mtime 为准）。状态 DRAFT，等 Arch .ok（r3 §10 那一份 .ok 同时覆盖 D1a、D1b、D2、D3D4 四步）。
冻结产物一律不动：asof/D0 面板、tier1 bars、stock_delisted.parquet、HI_LIQ 掩码。另出新版本。
tier1_materialize 第 66–72 行的修改需要另一份 .ok，不在本次范围；在那之前，SD1 一律以 suspend_flags_v2 为准。live=false，promotion_approved=false。

## 1. D-2 → suspend_flags_v2（步骤 D2_suspend_flags）
- **根因**：`scripts/acquire/tier1_materialize.py` 第 66–72 行，suspend_d 当天只要有任何记录（包括 R 复牌和盘中 S）就把 tradestatus 置 0。
- **形式**：单独一张稀疏表，不改面板，侵入最小。
- **脚本**：`scripts/fix_sd1/build_suspend_flags_v2.py --arch-ok PATH [--execute]`。门禁同 cs_panel 方案的 P1-1，并且要求 D1b 的 RECEIPT 为 PASS。输出 `data/v2/suspend_flags/`，包含 suspend_flags_v2.parquet、manifest.json、RECEIPT_D2_suspend_flags.json，先写 staging 再 rename。
- **日期范围（r3 P2-3）**：截到掩码最后一个交易日（现为 20261014），与 D1 同一跨度；manifest 记录 cutoff_date，并逐个列出截掉的日期（excluded_after_cutoff，现为 20261015 和 20261016），回执单列这两天。
- **共性改动（r3 P2-1、P2-2、P2-4）**：raw_content 内容哈希开工时与 D1b 的 RECEIPT 比对、收尾时复核；staging 之后的全部代码都在 try 内，异常写 VOID；run_conditions（niceness 和 ps 快照）写进 manifest 和 RECEIPT。D3D4 同样记录 run_conditions，并把全部代码包进 try。
- **r4 改动**：dry-run 不比对前序 RECEIPT 和 raw 内容（execute 照旧）；manifest 新增 days_walked，回执核对它等于 D1b 的 sessions_walked；回执写明单进程运行；运行命令加 PYTHONDONTWRITEBYTECODE=1。
- **行的范围**：suspend_d 有记录的 (ts_code, 日)，加上所有 is_resume_day 行。复牌定义调用 sd1_common.ResumeState，与 cs_panel 用同一个函数（P1-5）：排除新股首日和此前从未成交的代码；前一交易日按 amount>0 判断；首个数据日一律记 False；盘中 S 不算复牌。
- **join 键**：`(instrument_id, trade_date)`，instrument_id 形如 sz.002445，同时保留 ts_code。表里没有某行，就表示当天正常交易。

| 列 | 定义 | available_at（上海时间）| 来源 | SD1 用途 |
|---|---|---|---|---|
| suspend_type_raw, suspend_timing | 原值，S、R 或 R\|S | t 09:00 | suspend_d | 留痕 |
| halted_fullday | S 且 timing 为空 | t 09:00 | suspend_d | 买卖都拒 |
| intraday_halt, intraday_halt_timing | S 且 timing 非空 | t 09:00 | suspend_d | 停牌时段覆盖 09:30 才拒开盘成交 |
| **resume_announced** | 当日有 R 记录 | **t 09:00** | suspend_d R（盘前发布）| 盘前判断当日禁止新买入 |
| is_resume_day | 共用定义 | t 16:00 | daily vol + suspend_d | 只用于披露 |
| vol, amount, traded | — | t 16:00 | daily | 核对 |
| prev_traded_date, halt_sessions | 复牌行 | t 16:00 | daily | 把复牌收益挂回停牌前持仓 |
| tradestatus_v2 | 全天 S 且无成交为 0，其余为 1 | t 16:00 | 推导 | 会计 |
| tier1_v1_tradestatus, conflict_v1 | 旧规则的结果；旧规则判停牌但有成交 | — | 推导 | 对账 |
| available_at_open, available_at_close | 带时区的时间戳 | — | — | — |

- **manifest 和回执**：逐年记录 rows、halted_fullday、intraday_halt、resume_announced、is_resume_day、conflict_v1；conflict_v1 按类别计数；fullday_but_traded；"is_resume_day 但无 R"和"有 R 但不是 is_resume_day"两类数量；首个数据日；全部钉定 sha、文件清单哈希、.ok sha、D1b RECEIPT 的 sha。
- **交叉核对**：asof_extend 面板中 tradestatus=0 且 vol>0 的约 125 行，在表中应全部为 conflict_v1=True。
- **抽样至少 10 个**：002445.SZ 2026-08-24（应为 R、复牌、tradestatus_v2=1）、盘中停牌 3 个、复牌 3 个、新股首日 3 个（应不是复牌）。
- **资源**：按日读，约 2 分钟，RSS 低于 0.5GB。

## 2. D-3/D-4 → stock_delisted_v2（步骤 D3D4_stock_delisted）
- **根因**：
  - D-4：`scripts/acquire/ref_tables_20261014.py` 第 54 行只认名称以"退"结尾，而 `scripts/build_delisted.py` 的 reason()（第 17–24 行）认的是"名称含退"，两边不一致，漏掉了上交所"退市XX"写法。
  - D-3：reason() 没有价格规则。
- **脚本**：`scripts/fix_sd1/build_stock_delisted_v2.py --arch-ok PATH [--execute]`。门禁要求 D2 的 RECEIPT 为 PASS，三个目标文件都不得已存在。输出 `data/v2/ref/stock_delisted_v2.parquet` 及同名的 `.manifest.json`、`.receipt.json`，先写 staging 再 rename。
- **join 键**：`ts_code`（同时有 instrument_id）。v1 的列原样保留，脚本内断言 `x[v1cols].equals(v1)`。新增列都是事后信息（available_at=退市日），只有 delist_period_ann_date 可以作 PIT 强卖触发时间。

| 新列 | 定义 |
|---|---|
| delist_period_start / delist_period_ann_date | namechange 中第一条以"退"结尾或以"退市"开头的名称，取它的 start_date 和 ann_date；只有来源核实过的才允许 MANUAL_OVERRIDE |
| delist_period_end, delist_period_days | last_trade_date；delisted_daily 中 [start, end] 区间 vol>0 的天数 |
| entered_delisting_period_v2, delist_period_source | days>0；起点来源（namechange、manual_override 或空）|
| delist_period_pit_usable | 进入了整理期，且来源是 namechange 或已核实的人工覆盖；只有为真时，SD1 才可以把它当强卖触发 |
| face_value_delist_flag, face_value_last20_max_close | 整理期开始**之前**的最后 20 个有成交日收盘全部低于 1 元；没有整理期的取最后 20 个（P3-3）|
| delist_reason_category_v2 | 等于 v1 类别；v1 为合并/私有化且命中面值规则的改为"强制退市(面值退市)"；其余合并/私有化类改为"UNKNOWN(缺公告来源)" |
| needs_manual_source | UNKNOWN 类，或人工覆盖未核实的，为 True |
| **sd1_delist_type_default** | FORCED 或 UNKNOWN。**UNKNOWN 由 SD1 按 FORCED 处理**：sd1_forced_recovery_default=0.0，敏感性 sd1_recovery_sensitivity='0.0,0.3,0.7'。只有补齐公告来源（公告号、日期、URL）之后才能改为 MERGER_SWAP 或 CASH_OUT，走 SD1 规格 §3.5 的对价或 MA_FALLBACK 路径；本版没有这类记录。delist_events_v1 的类型映射也按这个口径（P1-4）|
| override_source_verified, source_ann_no, source_url, source_published_date | 人工覆盖的来源 |

- **002509.SZ 核对结论（P2-7）**：Data 在 2026-10-18 打开了 Arch 给的深交所 PDF。box 上 curl 连接超时，改用 WebFetch 读到了 PDF 全文，所以没有用 pdftotext。核对内容：
  - 公告编号 2020-053《关于公司股票终止上市的公告》；
  - 2020-05-27 收到深证上【2020】442 号，深交所当天决定终止上市；
  - 原因：2020-04-09 至 05-11 连续 20 个交易日收盘低于面值 1 元，适用上市规则 14.4.1 条第（十八）项；
  - "公司股票自 2020 年 6 月 4 日起进入退市整理期"。
  与 delisted_daily 吻合：2020-06-04 至 07-17 共 30 个交易日。结论：面值退市，进入过整理期。写入 MANUAL_OVERRIDE：delist_period_start=20200604，delist_period_ann_date=20200527，source_published_date=20200528（按 URL 路径），override_source_verified=True，并写入 source_url 和公告号。因此 needs_manual_source=False，delist_period_pit_usable=True。
  摘牌公告 2020-094 没有另行打开，最后交易日 07-17 由 delisted_daily 佐证。
- **56 只 UNKNOWN**：manifest 的 stats.unknown_needs_source 和回执逐只列出。
- **回执**：v1 列 0 差异；改类清单；整理期天数分布；整理期类天数为 0 的数量（v1 与 v2 对比）；抽样至少 10 只，对照 delisted_daily，含 600297.SH、002509.SZ、688287.SH、605081.SH、600696.SH。
- **资源**：约 10 秒，RSS 低于 0.6GB。

## 3. 定稿 sha256
统一列在 DATA_CS_PANEL_RESUME_REBUILD_PLAN_ZH.md §7。

## r6-WIP（02:22 EDT，未送签；等 Arch 的 is_resume_day 探针结论，可能还要改 D2，届时一并报 sha）
- **门禁禁止名单**（Arch 02:21 定版，sd1_common.FORBID_PATTERNS / classify_procs）：
  - nightly_update.py、tier3_daily_snapshot.py：只要进程存在就拒跑，不论处于什么状态。
  - relay_outage_backfill：只有 /proc/<pid>/stat 的 state == T 才放行，其他状态都拒跑。
  - 原有禁止项保留：research/、daily_pull、tier1_pull、tier1_materialize、adj_factor、bars_materialize。
  - 豁免规则：先从命令行里去掉 scripts/fix_sd1/ 这段路径，再做匹配。
  - 每一次放行或拒绝，都把 pid、state、cmdline 打印到 stdout（RUN_CONDITION_MATCHES 行，所有模式都打印），并写进 manifest 的 run_conditions.forbid_matches。
- **expires_et 自检**：expires_et 改为必填字段，须为带时区偏移的 ISO8601；当前时间不早于过期时间即拒跑（Arch r5 P3-2）。
- **94403 的 STOP/CONT 安排**（需用户同意后执行）：
  1. 确认 nightly_update.py 和 tier3 进程都已自然结束，不杀。
  2. 执行 kill -STOP 94403，记录时刻和 ps 快照。
  3. 门禁会看到 94403 处于 T 状态，放行并记录。
  4. 串行跑 D1b → D2 → D3D4 的 execute。
  5. 执行 kill -CONT 94403，记录时刻。
  6. 以上四个时刻都写进 execute 回执。
- **execute 各步 manifest 验收项**：
  - D1b：sessions_walked = D2 的 days_walked。
  - D2：
    - 125 行逐行对账（asof_extend 中 tradestatus=0 且 vol>0 的行都应为 conflict_v1=True）；
    - days_walked = 2128；
    - raw_content 哈希 = D1b 的值。
  - D3D4：
    - recategorised 中的面值类应含 600297/002505/000861/002509；
    - unknown_needs_source 对账 56；
    - 进入退市整理期 89→151，拆成 d4_zero_day_fixed_codes（61 只 0 天修正）、entered_newly_codes_other（其余新增）、entered_lost_codes 三部分，逐一解释。
- **D3D4 输出（Arch P2-1）**：
  - dry-run 不再把清单打印成 "..."，改为打印 counts 和完整代码清单；manifest.stats 内容相同。
  - 断言：manual_override 必须恰为 002509.SZ，否则 VOID。
  - 面值四只、UNKNOWN==56 的断言暂未写入，原因见 Data 报告中的疑问。

## r6（02:25 EDT）：is_resume_day 口径修正（Arch 探针 9b81bff1）
- **口径说明（P3）**："daily 缺行即视为停牌"只对沪深代码成立。
  - .BJ（北交所/新三板，包括上市前的新三板阶段）有大量无成交日：daily 缺行，但 suspend_d 里也没有 S。这些日子是薄交易，不是停牌。
  - 探针结论：12,169 行无 R 的复牌日中，12,134 行是这类 .BJ 行。
- **P2-A**：只改 build_suspend_flags_v2.py，sd1_common.ResumeState 不动，所以 D1b、cs_panel 不受影响（掩码里没有 .BJ 代码）。
  - .BJ 代码只在两种情况下判为 is_resume_day：t 日有 R 记录，或前一交易日有全天 S。
  - 仅仅是前一天缺行，不算复牌。
  - 统计范围是研究口径的全 A 股，不限于掩码代码集。
- **P3 新列 resume_evidence**（四选一，按顺序判断）：
  - R：t 日有 R 记录；
  - S_prev：前一交易日有全天 S；
  - gap_S：上次成交以来出现过全天 S；
  - none：以上都没有。
  - 沪深缺 R 的复牌共 35 行（真实复牌或退市整理首日），在 stdout 和 manifest.stats.nonbj_without_R_rows 里逐条披露。
- **P2-B，stdout 与 manifest 新增**：
  - table_rows，预期约 111,480，只打印不断言；
  - nonbj_is_resume_day_by_year；
  - nonbj_without_R，以及对应清单；
  - bj_resume_rows_kept：保留下来的 .BJ 复牌行，逐条列出代码、日期、resume_evidence；
  - bj_resume_dropped_missing_row_only：因"仅前一天缺行"而剔除的 .BJ 行数；
  - resume_evidence_counts。
- **断言（不符即 VOID）**：
  - 非 BJ 的 is_resume_day 逐年值须为 2018 1286、2019 563、2020 542、2021 518、2022 455、2023 304、2024 318、2025 559、2026 441；
  - 非 BJ 的 without_R 须为 35。
  - 这些值来自 Arch 的独立复现。
- **D3D4 期望值**：面值退市 4 只、UNKNOWN 56 只按 (a) 处理，以 v3 dry-run 实测打印的清单为准，Arch 审定后再决定是否写成断言。

## r6b（02:26 EDT）：D3D4 期望值走 (a)（Arch 02:25）
- **.ok 可选键**：
  - expected_face_value_recategorised：逗号分隔的代码，排序后按集合比较；
  - expected_unknown_needs_source_count：非负整数。
  - 解析和校验由 sd1_common.parse_d3d4_expectations 完成；parse_run_auth 本来就接受额外的键。
- **dry-run**：两键可以缺省，缺省时只打印实测值。
- **execute**：两键必填，缺失时门禁在读数据之前就拒跑；实测值与期望不符即 VOID。
- **dry-run 新增打印**（D3D4_FACE_CHECK 行，同时写入 manifest.stats）：
  - 实测面值改归类集合，以及它与诊断 4 只（600297/002505/000861/002509）的双向差集；
  - 差集内各只和这 4 只的"进入整理期之前 20 个收盘价"窗口：起止日、收盘价个数、最高收盘价、v1/v2 类别、face_flag；
  - UNKNOWN 数与 56 的对账（measured / diag / diff）。
- **流程**：Arch 按 v3 dry-run 实测清单审定后，把这两个值写进 execute .ok。

## r6c 记录（2026-10-18 ET，QuantLab Data；v3 四步 dry-run 审完之后）
- **P2-2（Arch r6b）**：manual_override 的断言原先检查的是常量，恒为真，现改为检查实际输出行。
  - 新增纯函数 sd1_common.check_manual_override，要求：
    1. delist_period_source=="manual_override" 的代码集合恰为 {002509.SZ}；
    2. 该行 period_start 为 20200604；
    3. override 来源字段（source_ann_no 非空或 override_source_verified=True）只出现在 manual_override 行。
  - 任何一条不满足都 VOID。
  - build_stock_delisted_v2.py 原第 61 行的来源字段赋值，从"该代码所有行"改为"仅被覆盖的行"（掩码 k）。002509.SZ 在 namechange 中没有"退"记录，所以本次输出不变。
  - test_sd1_common.py 新增合成用例：通过、多代码、缺代码、period_start 错、非覆盖行带来源字段、非覆盖行带 verified。
  - sd1_common 的 sha 变为 542dd13650979983f926778d5c7ea39a6f6e7655c2ac40ed1823601eb45ba4b9，三个 build 脚本里写死的 COMMON_SHA256 已同步更新。
- **P3-10（20261014 截止）**：
  - 20261014 来自 sd1_common.mask_last_date()，即 output/strategy_hiliq/universe_mask_hiliq_v1.parquet 的最大日期，只用于 D1、D2。
  - build_stock_delisted_v2.py（D3D4）没有日期截止。它的覆盖范围完全由冻结的 data/v2/ref/stock_delisted.parquet（v1，339 行）决定；v1 表来源是 meta/stock_basic_incl_delisted（10-12 构建，list_status=D 共 339 个，最大 delist_date 20260730）。
  - 07-30 到 10-14 之间没有记录，是因为源表里本来就没有，不是被截止排除的：stock_basic 中 delist_date>20260730 的为 0 个，D 状态代码全部在 master 里。
  - 已知待退：301139.SZ（元道退，namechange 2026-09-30 进入整理期，stock_basic 仍为 L），本版不覆盖，需等 stock_basic 刷新以后另行处理。
- 以上改动使 v3.ok 的 pin（script_cs_panel / script_suspend_flags / script_stock_delisted / common / plan_sd_fix）和单测 .ok（runner、dep）失效，需要 Arch 重签。
