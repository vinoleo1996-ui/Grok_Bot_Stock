# Eng 回执 r2：SD1 停牌/退市修复——按 Arch 审查修订（未运行）

- 写于 2026-10-18 02:1x ET（Eng）。依据：
  - Arch 审查 `docs/v2/ARCH_SD1_IMPL_REVIEW_ZH.md`（7f0b48197d7a62fb626cfb6f9f8ee443832521d1379c6d91ec3873817efe0baf，含附记 B）；
  - 主 Agent 01:53 ET 最终裁定 E-1、E-2；
  - 运行授权规范 `docs/v2/ARCH_RUN_AUTH_SELFTEST_SPEC_ZH.md`（1aa43bdd01935f55fd81f4ef0e1ddf92ef585d7ba6571e7078cd28ee86239a03）。
  - r1 回执（ffe236a9…）作废，以本文为准。
- **本轮只执行了两样**：一是 `py_compile`，pyc 写到 /tmp，不在仓库里留文件；二是只读静态扫描 `sd1_pit_static_check.py`，在 PYTHONDONTWRITEBYTECODE=1 下运行，结果 0 违规、21 条历史引用。
- **以下都没有运行**：pytest、对拍、任何旁路模块。没有 import 项目模块，没有写 .ok。
- live=false，promotion=false。

## 1. 纸面安全（复核）

- `quantlab/platform/execution.py` = 373fed309f055888e83572d3fbef8f5b5052ebfcb208307962a272bca6fc486c
- `quantlab/platform/__init__.py` = bfdfa63cbd7f39d7f0b1eb5a9b91ca00a30bdbd21e31ef3b90d89ac6080e99fc
- `scripts_eng/ok_runner_pin.py` = c7805d9a78e4f5478fa4c9e3becda48e76453ee0889b4f7027009a676c3e2485
- 以上三个文件都没有碰过。
- 纸面导入闭包 156 个文件重新逐个比对 sha，**156/156 不变**。
- 研究侧 FE、LC、ADG 的原文件不变。

## 2. 文件与 sha（r2，全长）

| 文件 | sha256 | 本轮改动 |
|---|---|---|
| quantlab/platform/execution_sd1.py | 35b46c2ba1bc0ea90bc7c97b173fc034c261a910d1cf20097a891a015bc14059 | E-1 两类核销与 G2；A2 留现金天数；A3 披露；track 必填；needs_manual_source 不强卖 |
| quantlab/platform/tradability.py | 4d684a48ca159783e74097e1264d926ad6cebc186ae1a1c5af6710c884bf6ecb | E-1；E-2 打 OPTIMISTIC_NO_LIMIT；P1-6 复牌日禁新买与 hiliq_carry 核对；track、delist_source 必填 |
| quantlab/platform/delist_accounting.py | 222b63aee4c47827a9f459dc3145bf254a3b8c9e9cd872e66578af44ce87062a | P1-5；P2-4 显式数据源并记表 sha；P2-7 |
| research/wb_sd1_books.py | cadc065a15c8d1bfd930d35673b2d4d6858a29db86501ed2beb2e35720dbc7fe | track、delist_source 必填；新增 `*_full` 返回 flags 和 summary |
| tests/test_sd1_suspend_delist.py | 8305246bee90fb5fd4da623953b30fa57d6e6559eee7b00b6bb5a0dcf504fa08 | P1-3 代码内 selftest 门禁；P1-7；新增 E-1、E-2、P1-5、P1-6 单测 |
| scripts_eng/sd0_parity_runner.py | c4d2411cec8047182029561aaa10ba1097e57d3b719b8bfb5f6e26e65055e825 | 按 Arch §8 和附记 B 重写，取代 4b9c30a4 |
| scripts_eng/sd1_pit_static_check.py | 3cfc11351f092b145d205628225564cd3c569b4eda2b5862eb854544a55d360a | P2-5 扫描范围扩大 |
| scripts_eng/ok_runner_pin_v2.py（新，**待审，未启用**） | a4b5dbd479fd2d0644d131c992c81f52dfe22f0bbaee2d9b9f072401e58e58d1 | 见 §6 |

- **相关文件**：
  - `docs/v2/eng_sd1/SD1.patch`（全部 SD1 新文件）；
  - `SD1_r1_to_r2.diff`（r1→r2 增量，其中 runner 的基线是 4b9c30a4）；
  - `SD1_vs_execution_reference.diff`；
  - `pit_static_check.json`；
  - `SD1_SHAS.txt`（57eb6e40e5a72ece0cff482cdacebaf5cff2e1cbde9f9e7c9c99f42ab2347f41），含两份 .ok 草案的逐行内容。

## 3. P1 修复对照

### P1-1：注入顺序

- WORKER 在 import 任何 quantlab 模块**之前**，用 `spec_from_file_location("quantlab.platform.execution", 引擎文件)` 和 `module_from_spec` 建模块，放进 `sys.modules`，再 `exec` 刚读入并算过 sha 的同一份字节。这样 `__init__` 第 47 行 import execution 时，拿到的就是这个注入模块。
- 如果 `sys.modules` 里已经有任何 quantlab 模块，直接拒跑。
- 注入后核对 `quantlab.platform.execution is mod`。
- 跑之前和跑之后各断言一次 `run_weight_schedule.__code__.co_filename` 等于期望文件，要求注入模块和 v2_multisleeve_book 里绑定的函数都满足。
- pristine 子进程走同一套流程，加载的是真正的 execution.py。
- 子进程输出它实际执行的引擎 sha，运行结束前再复算一次；父进程核对它等于 .ok 里 `dep_sha256_execution` 或 `dep_sha256_execution_sd1` 的值，不一致记 FAIL_ENGINE_IDENTITY。
- T9 的 `_head_engine` 同样断言两个引擎的 co_filename。

### P1-2：门控

- 调用 `enforce(..., modes=[f"parity_{suite}"], deps=...)`。deps 包括：execution（还要求等于 373fed30）、execution_sd1、tradability、delist_accounting、platform_init、ok_runner_pin、book_smoke、v2_multisleeve_book，以及每个权重文件的 `dep_sha256_w_<key>`。
- sha 一律 64 位精确比对。
- runner 自己还核对以下 .ok 键：
  - 显式写有 `allow_smoke=false`；
  - `out_root=output/_sd0_parity`；
  - `out_tag` 等于 `--out-tag`，并以 runner sha8 `c4d2411c` 结尾；
  - `exec_serial=true`、`exec_nice=10`、`rss_cap_mb≤1536`。
- 输出目录 `<out_root>/<suite>_<out_tag>` 用 `mkdir(exist_ok=False)` 创建；用例 JSON 和报告一律用 `open(...,"x")` 写。

### P1-3：pytest 门禁写进测试代码

- 测试文件顶层先做两件事：
  - 调 `ok_runner_pin.enforce(__file__, [docs/v2/eng_sd1/ARCH_SD1_TEST.ok], modes=["selftest"], deps=TEST_DEPS)`；
  - 做自查（ok_runner_pin c7805d9a 不查的项目）。
- 两步都通过后，才 import numpy、pandas 和三个旁路模块。不满足就 `SystemExit`，收集阶段直接中止，没有任何跳过路径。
- 已按 01:59 裁定，把 smoke 改为 selftest。
- 自查内容：
  - scope=selftest；
  - format、signed_by；
  - 7 个已知 allow_* 都显式写出；allow_real_data 与 QL_SD1_REAL_DATA 一致；除 selftest、real_data 外，其余 allow_* 都是 false；
  - signed_et、expires_et 是带时区偏移的 ISO8601，signed_et 不在未来，expires_et 未过期；
  - 没有 BOM、CR 或行内注释；
  - out_dir 只能是 mkdtemp 或 /tmp/<tag>，不得在仓库或 output/ 下，退出时删除；
  - 要求 PYTHONDONTWRITEBYTECODE=1。
- 真实数据：设 `QL_SD1_REAL_DATA=1` 时，modes 为 `["selftest","real_data"]`，要求 allow_real_data=true，并核对 `data_manifest_sha256_t13`。它等于把读到的全部文件按 sha256sum 格式列出、按路径排序后，整体再取一次 sha256。
- TEST_DEPS 共 68 项：被测模块的静态 AST 导入闭包，函数内 import 也算进去，范围故意放宽。
- 测试里的临时文件只写在 out_dir 下；子进程同样设 PYTHONDONTWRITEBYTECODE=1。
- runner 的 `--suite unit` 由 allow_parity_unit 控制：设 PYTHONDONTWRITEBYTECODE=1，nice 10，用 qlvenv 运行，有 RSS 看门狗。测试文件自己的门禁照样生效。

### 其余 P1

- **P1-4**：SD1_SHAS 已重写，全部为现场复算的全长 sha；ok_runner_pin 为 c7805d9a。
- **P3-B1**：测试文件在 SD1_SHAS 里改标为 dep。
- **P1-8**：paper 用例写成固定清单（8 个用例、6 个权重文件），路径和 sha 都写死，.ok 里再钉一遍，两边都要对上。去掉了 glob。

### P2

- **P2-1**：启动时 `os.nice(10)`；父进程每秒读一次 `/proc/<pid>/status` 的 VmRSS，超过上限就 SIGKILL，记 FAIL_RSS。
- **P2-6**：比对改为双向，两边文件集合必须相同：
  - parquet 先比列名、dtype、形状，float 列用 `equal_nan=True`；
  - csv 和其他文件逐字节比；
  - json 去掉 run_id 和时间戳后整体比较；
  - RECEIPT.md 里带 run_id，只核对存在。
- **另加的进程保护**：
  - 16:40–18:40 ET 拒跑（纸面 17:40 前后各 1 小时，按每天执行）；
  - 有其他对拍进程，或 Data 的 `scripts/fix_sd1/` 进程在跑时拒跑；
  - book_smoke 的 HASH_FILES 跑前跑后各算一次全长 sha，有变化则整轮作废。

### 潜在 P1 与其余 P2

- **P1-5**：两处都改了。
  - `load_delist_events` 对 needs_manual_source=True 的行，把 force_sell_from 置为 NaT，并打标 NEEDS_MANUAL_SOURCE_NO_FORCE_SELL；
  - 两个引擎的 plan 也按这一列再拦一次。
  - 单测 T15 用合成 v2 表：仿 002509 的行（False，2020-06-04 起）正常强卖，True 行不强卖。
- **P1-6**：
  - FE 适配器读 v2 的 `is_resume_day` 和 `hiliq_carry`（v2 缺这两列就报错）。有 `resume_announced`（09:00 可知）时优先用它；没有就用 is_resume_day（16:00 才知道，只用来拦新买，偏保守，打标 ENTRY_GATE_IS_RESUME_DAY_T1600）。复牌日的新买记为 `RESUME_DAY_ENTRY_GATE`。
  - `check_hiliq_carry`：持仓穿越停牌、在复牌日没有价格的，算不一致；有不一致就 RuntimeError，拒绝输出。T16 覆盖。
- **P1-7**：
  - T13 真实数据用例的成交集改用 suspend_d 的 R 记录，和面板相互独立；
  - 新增反同义反复单测；
  - 新增 cs_panel_v1 拒读单测：没有 v2 文件时 FileNotFoundError；allow_cs_panel_v1=True 时打标 `cs_panel_v1(D-1 gap)`。
- **P2-2**：`strategy_v1_sd1(*, track)` 改成关键字必填；`sd1_blocked_buy_budget(None/空)` 报 ValueError；三个适配器的 track 也必填。
- **P2-3**：已披露。成交量只用于判断能否成交，不进选股；summary 里的 halt_extra_source 写明这一点。
- **P2-4**：
  - `load_delist_events(codes, *, source=)` 必须显式指定数据源，取值为 `src_events_v1`、`src_table_v2`、`src_table_v1_d3rule` 之一；文件不存在就 FileNotFoundError，不会自动切换。
  - 每行记录 source_path 和 source_sha256；summary 和 G2_CHECK 行里都有 delist_source 和 sha。
  - 名字故意不含扫描词，研究侧调用写源名时不会触发静态扫描。
- **P2-5**：SCOPE 扩到 quantlab/portfolio/、quantlab/beta/、scripts/。
  - 文件级白名单（数据构建、采集、生存偏差审计）：build_delisted、pull_delisted、build_float_mktcap_from2015、scripts/acquire/、scripts/fix_sd1/、smallcap_reconcile、smallcap_survivorship_b1。
  - 逐行列为 PREEXISTING 的 13 条：beta/survivorship 5 条（B1 生存偏差，**请 Arch 确认**）、v2_multisleeve_book:118（可转债 delist_date 终值）、smallcap_* 的 `delist_events=len(...)` 计数列名。
  - 扫描结果：21 条历史引用，0 违规。
- **P2-7**：`load_halt_extra` 按 trade_date 列的实际类型（int、日期、字符串）过滤。整理期名称规则仍是以"退"结尾或以"退市"开头，已披露。

## 4. 主 Agent 01:53 最终裁定的落地

### E-1

- 有公告的核销（FORCED_*）记 `DELIST_WRITEOFF`，UNKNOWN 记 `DELIST_WRITEOFF_UNKNOWN`，主口径回收为 0。
- 两类分别记录条数、权重（核销日仓位价值 ÷ 前一日收盘 NAV）和金额，再给出合计权重。这些写在 `sd1_summary`（权重引擎是 `summary`）和 sd1_events 的 `G2_CHECK` 行里。
- `run_delist_sensitivity` 返回 `{0.0 主口径, 0.3, 0.7, "unknown_last_close_cash"}`。后三个的 basis 都是 sensitivity_disclosure_only；权重引擎对应 `run_wb_delist_sensitivity`。
- **G2 的实现口径（请主 Agent 确认）**：`g2_triggered = (有公告核销 ≥1 条) 且 (有公告 + UNKNOWN 合计权重 ≥ 1%)`。这样同时满足"UNKNOWN 单独不触发"和"合计 ≥1% 触发"两句。另外并列输出 `g2_if_unknown_alone_counted`，即另一种读法：只看合计。
- T14 覆盖四种情形：合计 ≥1%；有公告单独 ≥1%；只有 UNKNOWN、合计 ≥1%（不触发）；合计 <1%。

### E-2

- FE 和 ADG 不加涨跌停。输出打标 `OPTIMISTIC_NO_LIMIT`，summary 里 `gate_eligible_alone=False`，以 book_smoke 为准。
- cs_panel_v2 带上原始涨跌停价之后，FE 切回 open_touch，受影响的叶重算，只作披露。ADG 保持冻结预注册的收盘成交。
- LC 本来就执行 open_touch，不受影响。
- T16 覆盖。

### Arch A2、A3

- **A2**：cash 模式下，事件表新增 `BLOCKED_BUDGET_CASH_HELD`，记 sessions（从被拦那天到下一个信号日）和权重；summary 里汇总。T3 覆盖。
- **A3**：RENORM 事件带 `pricing=exec_day_open`；summary 里 `a3_renorm_priced_at_exec_open=True`。

## 5. 要 Arch .ok 才能执行的命令（草案逐行见 SD1_SHAS.txt）

1. **纸面对拍（最优先）**：`cd /workspace/QuantLab && python3 scripts_eng/sd0_parity_runner.py --suite paper --out-tag <以 c4d2411c 结尾>`
   - .ok 为 `docs/v2/eng_sd1/ARCH_SD1_EXEC.ok`，需要：
     - allow_parity_paper=true，allow_parity_research=false，allow_parity_unit=false，allow_smoke=false；
     - runner 钉值，以及 8 个模块 dep 和 6 个权重 dep；
     - out_root、out_tag、exec_serial、exec_nice、rss_cap_mb。
   - 注意：Arch §9 草案里的 allow_full=true 和 allow_suite 本 runner 不读，建议写 allow_full=false，避免 v2 门控把未请求却写成 true 的 allow 判为违规。
2. **SD1 selftest**：`cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python -m pytest tests/test_sd1_suspend_delist.py -q -p no:cacheprovider`
   - .ok 为 `docs/v2/eng_sd1/ARCH_SD1_TEST.ok`，scope=selftest，68 个 dep，out_dir=mkdtemp，带 expires_et。
   - **解释器必须用 qlvenv**（py3.12、pytest 9.1.1、numpy 2.5.3、pyarrow 25.0.1）。系统 python3 是 3.13，没有 pytest，numpy 2.5.4、pyarrow 26.0.0 也和 qlvenv 不同。T9 的两个引擎在同一个解释器里比，不受版本差影响。
3. **研究对拍**：`--suite research`。等纸面全部 PASS_BIT_IDENTICAL 之后再审；用例的权重 sha 由 .ok 提供。
4. **T13 真实数据**：要另开 .ok，并等 Data 出 cs_panel_v2。

### 运行条件

- 串行，nice 10，RSS ≤1.5GB。
- 不得与 Data 的 D-1~D-4 重建同时跑；不得落在 10-19 17:40 ET 前后 1 小时内（runner 每天都按这个时段拒跑）。
- 对拍前后要核对 HASH_FILES 不变。
- 跑完清理 out_dir；不得留下 __pycache__ 或 .pytest_cache。

## 6. ok_runner_pin_v2（新文件，待 Arch 审，未启用）

- `scripts_eng/ok_runner_pin_v2.py` = a4b5dbd479fd2d0644d131c992c81f52dfe22f0bbaee2d9b9f072401e58e58d1，只跑过 py_compile。
- 它不 import v1，c7805d9a 的 7 条检查语义不变，另外新增：
  - 拒绝 BOM、CR、非 UTF-8 和行内注释；
  - 核对 format 和 signed_by；
  - signed_et 必填、带时区偏移、不在未来；expires_et 在 selftest 时必填，且不能过期；
  - 核对 scope；selftest 模式隐含 scope=selftest；
  - .ok 里凡是没被请求的 allow_*，都必须正好是 false；runner 声明的 known_allow 必须显式写出；
  - 没有请求 real_data 时，allow_real_data 必须写成 false；
  - out_dir 只能是 mkdtemp 或 /tmp/<tag>，不得在仓库或 output/ 下；selftest 时必填。
- 审过之前，所有 runner 和测试仍然用 c7805d9a。

## 7. 风险与未决

- 所有测试和对拍都还没运行过。第一次跑可能会暴露断言或桩数据上的小错，修改后要重新钉 sha。
- 请主 Agent 确认 G2 的实现口径（§4 E-1）。
- 请 Arch 确认：beta/survivorship 的 5 条 PREEXISTING；FE 复牌日闸门在没有 resume_announced 时退用 is_resume_day 的做法；TEST_DEPS 用 68 项静态闭包是否合适。
- 本轮扫到仓库里有几个比 r1 新的 `__pycache__` 文件：research_loop、cli、ok_runner_pin.cpython-313 等。它们不是 Eng 写的（Eng 的 py_compile 一律写到 /tmp），来源待查，只记录。
