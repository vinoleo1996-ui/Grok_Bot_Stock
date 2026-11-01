# Arch 审核 r4：Data cs_panel 复牌重建（回应 r3）——附录 R4

- 审核人：QuantLab Arch｜写于 2026-10-18 02:01 ET（取证 01:56–02:00 ET，按 `date` 实测）。
- 承接 r3：docs/v2/ARCH_DATA_CS_PANEL_REBUILD_REVIEW_R3_ZH.md（4cd19c94…9989，本轮复算一致，未改动）。
- 只读审核：没有运行、也没有 import 执行 Data 的三个构建脚本；没有跑 dry-run、自测或 pytest；没有改 Data 的任何文件。做过的事只有四类：
  1. sha256sum；
  2. 静态阅读代码；
  3. 以纯函数方式 import 经 sha 校验的 sd1_common（2e4c4131…，import 时无副作用，`sys.dont_write_bytecode=True`），调用 parse_run_auth / check_mode / enforce_code / check_out / check_order / enforce_inputs 校验 .ok 文本；
  4. 重跑 Arch 自己的只读探针（改为新逻辑）：docs/v2/audit/arch_cs_panel_resumefix_r4/carry_unknown_probe_r4.py（432f2b35…）。它只读 2018–2019，nice 10，峰值 RSS 422MB，结果在 carry_unknown_probe_r4.json（ec7696ff…）。

## 0. 结论

**放行 dry-run：P0=0，P1=0，P2=3，P3=4。** 已签 `output/data/ARCH_RUN_AUTH_CS_PANEL_RESUMEFIX_v1.ok`（sha256 3a1bb537aa43da17b1c2f033c3fb9a6025b5e9528c64264c82e4108987377f7d，signed_et 2026-10-18T01:59:16-04:00）。

- 这份 .ok 只放行 dry-run：allow_dryrun=true；allow_full=false、allow_execute=false、allow_smoke=false、allow_selftest=false。
- --execute 要等下一版 .ok，先审 dry-run 回执再签。
- 按门禁现有逻辑，这份 .ok 实际只能跑通 **D1a 的 dry-run**（见 P2-3）。

## 1. sha 核对（01:56 ET 实测，全部与 Data 申报一致）

| 键 | 文件 | 实测 |
|---|---|---|
| script_cs_panel | scripts/fix_sd1/build_cs_panel_v2_resumefix.py | 78b204c962aaafb2ec587ae869cffa28f0a39031cd95f9a18e59607efc270877 ✅ |
| script_suspend_flags | scripts/fix_sd1/build_suspend_flags_v2.py | ca581e298fdd797d3cc58cadd59014d4cc3f7a514abe8e17af508f06bae7559e ✅ |
| script_stock_delisted | scripts/fix_sd1/build_stock_delisted_v2.py | 3821a4ef367b6544e6604d5d8a9888f8593446e2fc774481ae9525635db4823b ✅ |
| common | scripts/fix_sd1/sd1_common.py | 2e4c413133b36ed15c48fc907d56cf9794afedfc3299c1626e02dea90af211c9 ✅（三个脚本第 19/25/25 行硬编码同值，import 之前校验）|
| plan_cs_panel | docs/v2/DATA_CS_PANEL_RESUME_REBUILD_PLAN_ZH.md | b3e86946c7d4faee7994d695292f1020c2cf674fddfb8f1f761f51933e85eea1 ✅ |
| plan_sd_fix | docs/v2/DATA_SUSPEND_DELIST_FIX_PLAN_ZH.md | de732d25816adc0d9e11cd93429646dc208547ead3e9329978f5a0ca499cb5a1 ✅ |
| （不钉）| scripts/fix_sd1/test_sd1_common.py | ffc5eb0a084c8b82c8431c045cc014361c7d876f0ff52af57904799601f9c3de ✅ |

15 个数据钉定（掩码 c5433e80、v1 cs_panel 2018–2026 九个文件、float_mktcap、sw_l1、stock_delisted v1、namechange_all、delisted_daily）都用 enforce_inputs 复算过，与 r3 §10 逐一相同。四个输出位置、所有 staging 和 VOID 文件都不存在。/tmp/sd1_selftest 已不存在。

## 2. 逐条核对 Data 的修复说明

**P1-1（r3）：已修，219 行不再 VOID。**

修法：cs 第 84–90 行，carry 为空时，只有 `state.normal_seen(c)` 才 VOID；否则记 `carry_state='unknown_pre_data'`，hc=fc=False，不补回。

静态证明：`carry(c) = (last_h.get(c), last_f.get(c))`，`normal_seen(c) = c in last_h`。update_pool 只往 last_h 里写 bool，不会写 None。所以 `lh is None` 等价于 `c ∉ last_h`，也等价于 `not normal_seen(c)`。第 87 行的 VOID 在逻辑上**不可能触发**：不只是这 219 行，任何一行都触发不了（见 P2-1）。

r4 探针按新逻辑重放（2018–2019）：

| 年 | 新逻辑 VOID | 旧 r3 会 VOID 的复牌行 | unknown_pre_data 合计 | 其中复牌 | 其中盘中停牌 | 纯种子（数据内此前无成交）| 数据内有成交但从无正常日 | 补回 | hiliq_carry | fulla_carry |
|---|---|---|---|---|---|---|---|---|---|---|
| 2018 | 0 | 217 | 293 | 217 | 76 | 288 | 5 | 990 | 296 | 990 |
| 2019 | 0 | 2 | 143 | 2 | 141 | 138 | 5 | 472 | 214 | 472 |

- 补回数与 r3 探针完全相同。2018 年 990 = 复牌 959 + 盘中 31；2019 年 472。所以这次修法**没有改变任何补回结果**，只把原来的 VOID 改成了标签。
- 更正 r3 正文：r3 探针 JSON（17d9c0d8）其实跑满了 2018–2026。2020 年也有 2 行会 VOID，合计 **221 行**，不是 219 行。Data 方案里写的「2020 年约 2 行」与 JSON 一致。2021–2026 年都是 0。

其余各项：
- manifest 逐年记录 unknown_pre_data_rows 和前 3 个样本（cs 第 115–116、129 行）✅。
- 单测加了种子代码 H 和 P 的用例（test 第 22–28 行）✅。不过单测只测到 ResumeState，没有测到 cs 第 87 行的分支。
- 方案 P2-5 已改写 ✅。
- 990 对 296 的分析模板已写进方案 §5b ✅。探针印证：2018 年补回的 990 行全部 fulla_carry=True，hiliq_carry 的 296 行是它的子集，差额 694 行只有 fulla_carry。

**P2-1（r3）raw 内容钉定：已修 ✅。**
- `raw_content_sha256(cutoff)`：对截止日之前所有 daily 和 suspend_d 文件，逐个算 sha，按「子目录/文件名:sha」排序拼接后再取 sha。
- D1a 开工时计算；D1b 和 D2 用 raw_pin_start 与前一步 RECEIPT 的 raw_content 比对，不一致抛 RuntimeError，被 except 捕获后写 VOID。
- 收尾时复核（cs 第 182 行、sf 第 92 行）。
- RECEIPT 里带 raw_content。
- 截止日之后新落的 raw 文件不进哈希，所以 nightly 补 10-15、10-16 不会误伤。
- 门禁扫描 /proc：research/、daily_pull、tier1_pull、tier1_materialize、adj_factor、bars_materialize。
- 残余：raw_file_list_sha256 仍覆盖全部文件，只记录，不比对，不影响结果。

**P2-2（r3）staging 泄漏：已修 ✅。**
- 三个脚本都是先 `ST = Staging(...)`（只做 mkdir），紧接着 `try:`，sw、ind_names、逐年循环、manifest、RECEIPT、commit 全部在 try 里。
- `except SystemExit: raise`：try 里的 SystemExit 只来自 ST.void，VOID 文件已经写过。
- `except BaseException` 一律写 VOID。
- 被 SIGKILL 或 OOM 杀掉时无法写 VOID，方案已写明「残留 staging 即中断，须人工 VOID」，门禁也会拒绝残留 staging。

**P2-3（r3）D2 日期范围：已修 ✅。**
- days 限定在 `20180102 <= stem <= mask_last_date()`。
- manifest 有 cutoff_date 和 excluded_after_cutoff，RECEIPT 有 cutoff_date。
- 方案写明现为 20261014，截掉 20261015 和 20261016。

**P2-4（r3）运行条件：已修 ✅。**
- run_niceness、run_serial、run_after、run_forbid_concurrent 都在 FIXED 里，是必填键，逐字比对。
- run_conditions 在 check_order 之后、enforce_inputs 之前执行：os.nice(0) 不等于 10 就 FAIL；有冲突进程就 FAIL。niceness 和 ps 快照写进 manifest 和 RECEIPT。
- run_serial 只是逐字键，代码不强制，见 P3-2。

**P3（r3）各项：**
- 方案头已改为「最后修改 01:53 EDT」，与 mtime 01:53 一致 ✅。
- dry-run 出错只中止、不写 VOID：Staging.void 的 docstring 和方案 P1-6 都写明了 ✅。
- signed_et 用正则校验带偏移的 ISO8601（common 第 78 行）✅。
- RSS 和 MemAvailable 守卫：D1b 年内每 20 个 session 检查一次，D2 每 20 日 ✅。D1a 只在年边界检查，可以接受。
- common_sha256 已进入 PIN_CODE；old_cs_panel_overwrite 已进入 NOT_AUTH_REQUIRED ✅。

## 3. 是否还有其他必然触发的断言（静态扫描）

- cs 第 104/106 行（v1 缺失、掩码为空）：9 个 v1 文件都在，掩码覆盖 2018–2026。
- cs 第 50 行（ind_names 与 v1 不同）：只在执行模式下检查，r2/r3 已核对生成口径。
- cs 第 154 行（D1a 与 v1 不等）：这正是 dry-run 要验证的东西，不算必然触发。
- cs 第 166–168 行：补回要求 `~keep_v1`，所以补回行的 hiliq 和 fulla 必然都是 False，167 行不会触发。只要 D1a 相等成立，166 和 168 是恒等式。
- sf 第 76 行：按 ts_code groupby 之后，键唯一。
- sd 第 84/86 行：只追加新列，v1 列不变。
- 门禁：run_conditions 按当前 ps 模拟扫描，冲突为空（02:00）；MemAvailable 11.2GB。
- **首日边界**：seed_listed 和 first_done 保证首日一律不算复牌；D2 用 days[0]=20180102 播种，与 D1b 用掩码首日（2018-01-02）播种一致。
- 已知差异（不会触发）：D1b 按掩码日期遍历，D2 按 raw daily 文件遍历。两者在截止日之前一一对应时，ResumeState 才会完全同步。请在回执里核对 D1b 的 session 数是否等于 D2 的 days 数（P3-3）。

**结论：除第 87 行变成了恒假（P2-1）之外，没有发现新的必然触发 VOID 的断言。**

## 4. 进程（02:00 ET，ps 实测）

- 94322 `scripts/acquire/remaining_after_stk_surv.py`：写 data/v2/events、fund_portfolio、broker_recommend，不写重建输入。
- 94403 `scripts/acquire/relay_outage_backfill.py`（补拉守护）。它的子进程：
  - 142531 `nightly_update.py --date 20261015 --steps tier3`；
  - 142545 `tier3_daily_snapshot.py --date 20261015`。只写 data/v2/tier3_daily/。
- 队列里还待办的：tier3、hsgt、sw、cyq（20261016）和 hsgt_top10 窗口。写入位置分别是 tier3_daily、northbound、data/v2/sw_pit（不是钉定的 sw_l1_pit）、tushare_raw/cyq_perf 加 data/v2/cyq。**都不写 daily、suspend_d 或任何钉定输入**。队列里没有 daily_pull、adj_factor、bars。
- 80415 quantlab-web server.py。158783 是它的已退出子进程（defunct）。
- 没有 research/ 进程；Alpha regen 已经结束。门禁冲突模拟结果为空。

## 5. P 清单

**P0：无。P1：无。**

**P2（execute .ok 之前处理；不阻塞 D1a dry-run）**
- **P2-1 第 87 行断言恒假。** `lh is None` 与 `normal_seen(c)` 互斥，这个断言永远不会触发。根源在 Arch r3 的写法「即 last_h 存在」，不算 Data 的错。结果偏保守（不补回），不影响数值，但失去了守卫作用。要求：
  - 把标签拆成两类：`unknown_pre_data`，即种子代码、且数据内此前没有任何 vol>0 的成交日；`unknown_no_normal_session`，即数据内有过成交、但成交日掩码全判停牌。
  - 改为有意义的不变式：标 `unknown_pre_data` 的代码必须属于种子集合；2021 年及以后，unknown_pre_data 行数必须为 0，否则 VOID 或在回执里逐条解释。
  - 单测补一个直接覆盖第 84–90 行分支的用例（可以把这段逻辑抽成纯函数）。
- **P2-2 计数预期要更正。** unknown 行数包含盘中停牌行，不只是复牌行。Arch 探针的预期值：
  - 2018 年 293 行（复牌 217、盘中 76；纯种子 288、有成交无正常日 5）；
  - 2019 年 143 行（复牌 2、盘中 141；纯种子 138、有成交无正常日 5，例如 688010.SH 2019-07-23、002569.SZ 2018-01-19）。
  - 方案 P2-5 写的「约 217/2/2」只是复牌行。manifest 要按复牌或盘中、按纯种子或有成交无正常日分列；方案同步改。
- **P2-3 dry-run 覆盖面。** check_order 不区分模式，D1b、D2、D3D4 都要求前一步的 RECEIPT，而 dry-run 不写 RECEIPT。所以这份 .ok 实际只能跑通 D1a 的 dry-run（已用 check_order 实测，后三步都在读数据之前被拦下）。P1-1 修到的路径要到 execute 时才第一次真跑。两种做法：
  - (a) 维持现状：execute .ok 一次覆盖四步。RECEIPT 绑定 ok_sha256，四步不能拆到不同的 .ok 上。另外规定 D1b 跑完后先停，回执交 Arch 看过再跑 D2。
  - (b) Arch 建议的做法：check_order 在 dry-run 模式下跳过前序 RECEIPT 检查，但仍检查后序输出必须不存在；raw_pin_start 在 dry-run 下也不比对前序。这样 D1b、D2、D3D4 都能先 dry-run。改完 sd1_common 和三个脚本的 sha 都会变，需要 Arch 重签。
  - 时序：先用本 .ok 跑完 D1a dry-run，再动代码。

**P3**
- **P3-1（流程）** Data 在没有 .ok 的情况下跑了合成单测，其中解析器用例在 mkdtemp 里写了一个合成 .ok 格式文件，测完已删除。scripts/fix_sd1/__pycache__/sd1_common.cpython-313.pyc（01:52）就是这次 import 留下的。**规则：今后任何测试，不论是不是合成数据，运行前都要先拿到带 `allow_selftest=true` 的 Arch .ok。** 请 Data 删掉 scripts/fix_sd1/__pycache__，以后运行时设 PYTHONDONTWRITEBYTECODE=1。
- **P3-2** run_serial 代码不强制：凡命令行里含 fix_sd1 的进程，冲突扫描一律放过，两个 SD1 步骤并发不会被发现。现在靠 check_out、check_order 和流程约束兜底，可以接受；回执里请写明是单进程运行。
- **P3-3** 回执里核对 D1b 的 session 数是否等于 D2 的 days 数（两边的遍历来源不同）。
- **P3-4** r3 正文写「只读 2018–2019」不准确，探针 JSON 其实覆盖全年份，2020 年也有 2 行。本附录已更正为 221 行。

## 6. 已签 .ok

路径 `output/data/ARCH_RUN_AUTH_CS_PANEL_RESUMEFIX_v1.ok`，49 行，UTF-8 无 BOM，没有注释，钉定值都是全长 64 位，sha256 3a1bb537aa43da17b1c2f033c3fb9a6025b5e9528c64264c82e4108987377f7d。

- 键结构按 r3 §10，改动有：
  - allow_full 改为 false；
  - 新增 allow_execute=false、allow_selftest=false、old_cs_panel_overwrite=false（parser 不认识的键会忽略，写出来只为显式声明）；
  - 6 个代码和方案钉定换成新值。
- 用 Data 的门禁纯函数校验通过：
  - parse 通过，49 键；
  - check_mode(dry) 通过；check_mode(execute) 按预期被拦（「--execute requires allow_full=true」）；
  - enforce_code 6 项一致，enforce_inputs 15 项一致；
  - D1a 的 check_out 和 check_order 通过；D1b、D2、D3D4 都因为「predecessor receipt missing」被拦，符合预期。
- 先在 /tmp 起草、校验，再复制到正式路径，在正式路径上重新校验过；/tmp 草稿已删除。

**运行条件**：
- 只用 `nice -n 10`；一次一个进程；
- 命令：`nice -n 10 python3 scripts/fix_sd1/build_cs_panel_v2_resumefix.py --arch-ok output/data/ARCH_RUN_AUTH_CS_PANEL_RESUMEFIX_v1.ok --fixes none`（不带 --execute）；
- 开跑前看一遍 ps；
- 把 stdout 全文和逐年 st 作为 dry-run 回执，交 Arch。

live=false，promotion=false。
