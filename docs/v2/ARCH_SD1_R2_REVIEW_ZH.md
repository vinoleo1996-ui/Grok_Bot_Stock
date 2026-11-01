# Arch 复审：Eng SD1 r2 + sd0_parity_runner c4d2411c + ok_runner_pin_v2 r2

- 时间：2026-10-18 02:20–02:30 ET；审核人：QuantLab Arch（只审不改）
- 依据：Eng 申请 docs/v2/eng_sd1/MSG_TO_ARCH_SD1_R2_ZH.md（4cad8ff5a6adc1ed64a1bb8f2521a229292c2ed8d49b1f4e2b15b92fba3430b0）；上轮审查 docs/v2/ARCH_SD1_IMPL_REVIEW_ZH.md（7f0b4819，含附记 B）；运行授权规范 docs/v2/ARCH_RUN_AUTH_SELFTEST_SPEC_ZH.md（1aa43bdd）；主 Agent 裁定 SD1 E-1/E-2（01:53）、v1.4 E-2（01:59）。
- 本轮 Arch 没有运行 Eng 的测试、runner 或 pytest，没有 import 任何项目模块。只做了 sha256、AST 静态解析，以及一个不 import 项目代码的 .ok 解析复刻（/tmp/arch_sd1/replica_check.py，f937170b…）。
- live=false，promotion=false。

## 1. 结论

| 项目 | 结论 |
|---|---|
| SD1 r2 合成单测 | **放行**。P0=0，P1=0。已签 `docs/v2/eng_sd1/ARCH_SD1_TEST.ok` |
| sd0_parity_runner c4d2411c（paper 套件） | **放行，附条件**。P0=0，P1=0。已签 `docs/v2/eng_sd1/ARCH_SD1_EXEC.ok`，**须等单测回执经 Arch 审过才能跑** |
| research / unit 套件 | 不放行（allow_parity_research=false，allow_parity_unit=false） |
| ok_runner_pin_v2 r2（6810b024） | **无 P1**，可以批准采用，但只能逐个 runner 切换，**不得原地替换 v1 c7805d9a**（见 §6 P2-V1、P2-V2） |
| P1-6 复牌日闸门退用 is_resume_day | 对纸面对拍**零影响**；对 FE wb_SD1 真实运行是 P2，真实运行前须处理（见 §5） |

上轮遗留的 P1-1、P1-2、P1-3、P1-8，以及 P1-5/6/7、P2-1/2/4/5/6/7、P3-B1 均已关闭（逐项见 §3）。

## 2. sha 核对（Arch 实测，全长）

- 主干：execution.py = 373fed309f055888e83572d3fbef8f5b5052ebfcb208307962a272bca6fc486c，__init__.py = bfdfa63cbd7f39d7f0b1eb5a9b91ca00a30bdbd21e31ef3b90d89ac6080e99fc，ok_runner_pin.py = c7805d9a78e4f5478fa4c9e3becda48e76453ee0889b4f7027009a676c3e2485。**三个都没动。**
- r2 旁路和脚本：execution_sd1 35b46c2b…4059、tradability 4d684a48…6ecb、delist_accounting 222b63ae…062a、wb_sd1_books cadc065a…dbc7fe、test 8305246b…fa08、runner c4d2411c…e825、pit_static_check 3cfc1135…360a。**全部与申请一致。**
- 文档：receipt 0b4142e9…、r1→r2 diff 3ff5ab31…、SD1.patch 363d49bb…，均一致。
- 清单 SD1_SHAS.txt：申请里写的 57eb6e40 在审查期间被 Eng 改成 621a7af4b8a6500f81bb0db505836afdab8d9151f0bc6672766d064f2d9d0683（02:15:21）。按行数核对，新增 6 行都是注释，另把 v2 的 sha 改为 6810b024，键值行没有变化。Arch 按 621a7af4 重新核对了全部 174 条方括号 sha，**0 条不符**；纸面闭包 156/156 一致。
- 权重文件 6 份（capadv_20261013 4348877e、capadv_paper_20261014_r2 e03028ee、b4_60w efcef7c4、b4_100w 4736c030、s6_60w 6ce63a79、s6_100w b1f9ae65）：实测 sha = runner 硬编码值 = 清单值。
- TEST_DEPS 68 项：键名与清单完全一致，68 个 sha 全部一致。Arch 用独立 AST 闭包复算（含函数内 import），得到 66 个 quantlab 文件，与 TEST_DEPS 中的 66 个 quantlab 项**一一对应、无缺无多**；另外 2 项是 ok_runner_pin 和 sd1_pit_static_check。
- 越界写入检查：output/_sd0_parity 不存在；本轮之前 docs/v2/eng_sd1/ 下没有 .ok；没有 SD1 相关进程在跑。r2 的 py_compile 产物都在 /tmp（pc_*.pyc）。

## 3. 各修复项复核

| 项 | 结论 | 要点 |
|---|---|---|
| P1-1 注入 | ✓ 关闭 | WORKER 先断言 sys.modules 里没有 quantlab，再读字节、算 sha，用 spec_from_file_location 建模块，**先放进** sys.modules["quantlab.platform.execution"]，再对同一份字节 exec(compile)，最后才 import quantlab.platform。__init__ 第 47 行的 `from quantlab.platform import execution` 会从 sys.modules 取到这个已注入的模块。两个引擎顶层都只 import 标准库和 numpy/pandas，不会在执行一半时回头 import quantlab.platform。之后断言 quantlab.platform.execution 就是注入的模块、run_weight_schedule 的 co_filename 等于期望文件（注入模块和 M 里绑定的函数都查，跑前跑后各查一次），跑完重算引擎 sha。pristine 一侧走同一路径加载真的 execution.py，父进程核对子进程打印的 sha 等于 .ok 的 dep（pristine = 373fed30）。任何一项不符都记 FAIL_ENGINE_IDENTITY，属失败即关闭 |
| P1-2 门控 | ✓ 关闭 | modes=[parity_paper]；8 个模块 dep 加 6 个 w_ dep，均 64 位精确比对；paper 权重另对硬编码值；allow_smoke=false 须显式写出；out_root、out_tag 与 --out-tag 相等，只许 [A-Za-z0-9._-]，且以 runner sha8 结尾（不可能出现 / 或 ..）；exec_serial、exec_nice、rss_cap_mb≤1536 都查 |
| 输出范围 | ✓ | 根目录 output/_sd0_parity/paper_<tag> 用 mkdir(exist_ok=False) 创建，报告和 CASE.json 用 open('x') 写。book_smoke 的 --out 和 --receipt 都被改到 case 目录内（默认回执 docs/v2/BOOK_SMOKE_…_ZH.md 不会被写）；run_book 只写 odir。对 output/v3/book_smoke_g1g5_capacity_adv_x2 只读（_vs_ref，仅供参考）。纸面产物和冻结件不会被写。HASH_FILES 跑前跑后各算一次 |
| P1-3 测试门控 | ✓ 关闭 | 顶层只先 import ok_runner_pin（它本身就是钉住的 dep），然后 enforce(modes=["selftest"])，再做自查（format、signer、scope、7 个 allow 显式、allow_real_data 与模式一致、BOM/CR/行内注释、signed/expires、out_dir），通过后才 import numpy/pandas 和被测模块。仓库根和 tests/ 下都没有 conftest.py 或 pytest.ini。SystemExit 会让 pytest 报收集错误，测试一条都不会跑 |
| 只读合成数据 | ✓ | T13 真实用例由 skipUnless(QL_SD1_REAL_DATA) 控制；设了这个环境变量但 .ok 里 allow_real_data=false 时，门控会直接拒跑。T15 加载器用例把 DELIST_SOURCES、NAMECHANGE、CONSIDERATION 都指到 OUT_DIR 下的合成文件或不存在的文件；v2 分支不调 _face_value_codes（不读 DELISTED_DAILY）。T16 打桩了 _events_for。T10、T11 的种植调用在读表之前就被 PIT 守卫拦下（即使守卫失效，也会因缺 source 抛 TypeError，不读数据）。execution*.py 里 _wide_limit_funds 会懒读 raw 的 fund_basic_E，但只对 sz.159xxx 触发，测试里没有这类代码（P3-3） |
| 写入范围 | ✓ | OUT_DIR = mkdtemp（/tmp/sd1_selftest_*），atexit 删除；所有 TemporaryDirectory 都建在 OUT_DIR 下；子进程带 PYTHONDONTWRITEBYTECODE=1。quantlab/config.py 在 import 时会对已有目录做 mkdir(exist_ok=True)，实际不写（P3-4） |
| P1-5 needs_manual_source | ✓ | 加载器把这类行的 force_sell_from 置为 NaT 并打标；两个引擎也各拦一次；T15 覆盖 |
| P1-6 复牌日闸门 + hiliq_carry | ✓（代码），⚠ 数据口径 P2，见 §5 | |
| P1-7 T13 | ✓ | 成交集改用 suspend_d 的 R 记录（独立来源）；数据集钉 data_manifest_sha256_t13；新增"不是同义反复"单测和 v1 拒读单测 |
| P1-8 固定用例 | ✓ | 8 个用例、6 个权重文件，路径和 sha 都写死，没有 glob |
| P2-1 RSS | ✓ | os.nice(10)；每秒读一次 /proc/<pid>/status 的 VmRSS，超限 SIGKILL 并记 FAIL_RSS；book_smoke 不开子进程，所以只看子进程本身就够。轮询有 1 秒空档，worker 另记 ru_maxrss（P3-2） |
| P2-6 比对 | ✓ | 双向比对，两边文件集合必须相同；float 列用 equal_nan；json 去掉 run_id 和时间戳后整体比较；空集算失败 |
| P2-2 / P2-4 / P2-5 / P2-7 | ✓ | track 必填；delist_source 必须显式指定，并记表 sha；扫描范围已扩；trade_date 按列类型过滤 |
| P3-B1 | ✓ | 测试已自带门控，TEST.ok 用 runner_sha256_test_sd1_suspend_delist 钉住 |
| 其他保护 | ✓，附 P2-R1 | 16:40–18:40 ET 拒跑；另一个对拍进程或 fix_sd1 在跑时拒跑 |

### 主 Agent 裁定对照

- **E-1（01:53）**：实现为 `g2_triggered = (公告核销条数 ≥1) 且 (公告 + UNKNOWN 合计权重 ≥1%)`。只有 UNKNOWN 时不触发；公告单独 ≥1% 时触发；公告加 UNKNOWN 合计 ≥1% 时触发。**与裁定一致。** `g2_if_unknown_alone_counted` 只作披露，不进判定。主口径是 0 回收，0.3、0.7 和 unknown_last_close_cash 打 sensitivity_disclosure_only。T14 四组边界都有覆盖。
- **E-2（01:53）**：没有加涨跌停；FE 和 ADG 都打 OPTIMISTIC_NO_LIMIT，并标 gate_eligible_alone=False。一致。
- **v1.4 E-2（01:59）**：合成测试要有 selftest .ok，真实数据要 allow_real_data。一致。

## 4. 已签 .ok

| 文件 | sha256 | 要点 |
|---|---|---|
| docs/v2/eng_sd1/ARCH_SD1_TEST.ok | 4975aac8ccb34b90e3ac05a3edddd38629ef523ef6d1e1156a12519a2cdabfdc | scope=selftest；只有 allow_selftest=true，其余 6 个 allow_* 都是 false（含 allow_real_data）；out_dir=mkdtemp；钉测试 sha 和 68 项 dep；signed 2026-10-18T02:20:30-04:00，expires 2026-10-19T02:00:00-04:00 |
| docs/v2/eng_sd1/ARCH_SD1_EXEC.ok | eb3c35870e60fd418fcaa977aa695be2c211158185061d64f91ce7d76fa625e5 | scope=sd0_parity_paper；allow_parity_paper=true，research、unit、smoke、full 都是 false；没有 allow_suite；8 个模块 dep 加 6 个权重 dep；out_tag=r2_20261018_c4d2411c → output/_sd0_parity/paper_r2_20261018_c4d2411c；requires_prior_receipt=ARCH_SD1_TEST_receipt_reviewed_by_arch；latest_start_et_daily=14:00；expires 同上 |

- 两份都用复刻解析器按 v1 c7805d9a、测试自查、runner _gate 三套逻辑静态验过，均 PASS：无 BOM，无 CR，无行内注释，没有重复键。
- v1 门控会忽略未知键，所以 expires_et、requires_prior_receipt、latest_start_et_daily 对 EXEC 只是声明，不由机器强制。**顺序由流程保证：先跑单测并提交回执，Arch 书面放行后才能跑对拍。**
- 将来测试切到 v2 时，TEST.ok 必须加 gate_ok_runner_pin_sha256 并重签；EXEC.ok 切到 v2 时，按 v2 r2 现行逻辑还须写出 allow_real_data（见 P2-V2）。

## 5. P1-6 退用 is_resume_day 的影响（含 Data D2 新输入）

- 事实：resume_announced（t 日 09:00 可知，来自 suspend_d 的 R 记录）只在 suspend_flags_v2 里，**cs_panel_v2 只有 is_resume_day**（build_cs_panel_v2_resumefix.py 第 37 行的 EXTRA 列）。所以 fe_book_ret_sd1 读 cs_panel_v2 时**每次都会**退用 is_resume_day，并打 ENTRY_GATE_IS_RESUME_DAY_T1600。
- Data D2 dry-run（docs/v2/audit/data_suspend_flags_d2_dryrun/d2_dryrun_stdout_20261018_v2.txt）给出的 is_resume_day / resume_announced：2018 3528/1324、2019 2810/585、2020 3750/588、2021 3306/561、2022 2013/545；2023 379/387、2024 328/329、2025 570/572、2026 451/458；is_resume_day_without_R 共 12169。可见 2018–2022 年 is_resume_day 多标了 2–6 倍，2023 年起两者基本相等。
- **纸面对拍：零影响。** 对拍走 book_smoke 加 execution(_sd1).run_weight_schedule，SD1 开关全部取默认，execution_sd1.py 里没有任何地方引用 is_resume_day 或 resume_announced；而且窗口是 X2/PX，从 2024-06-03 开始，这段时间两个计数本来就相等。
- **FE wb_SD1 真实运行（研究叶）：P2-R2。** 多标的格子上会禁止新开仓。估计约占 2018–2022 年格子的 0.2–0.3%，方向不确定（偏保守，但是用 t 日 16:00 的信息去挡 t 日的入场）。按 E-2，FE 本来就不能单独作为门槛，所以不升 P1。真实 FE 运行前须满足以下之一：(a) FE 改为 join suspend_flags_v2 的 resume_announced 作闸门；(b) Data 把 resume_announced 写进 cs_panel_v2。在此之前，结果必须逐年披露被挡的新开仓次数，以及其中来自 is_resume_day_without_R 的占比，并给一档"闸门关闭"的敏感性。请 Data 说明那 12169 行的成因（Data 怀疑是 amount=0 的非停牌行）。

## 6. 问题清单

**P0：无。P1：无。**

P2
- **P2-R1** 16:40–18:40 拒跑只在启动时检查一次；8 个用例共 16 个子进程，可能要跑几十分钟，16:39 启动就会跑进窗口。处理：运行条件写成"每天 14:00 ET 前启动"（已写进 EXEC.ok 的声明键和注释）；r3 时请 Eng 在每个子进程启动前都重查一次。
- **P2-R2** 见 §5。
- **P2-V1（v2）** 检查 8–15 作用于**所有**列出的 .ok，不只是钉住本脚本的那份。c_col_exec_diagnostic、core_x2_scorecard、s2_3_exec_layer 都会列多份 .ok，而冻结的 .ok（如 ARCH_RESIGN_A_v1_3.ok）没有 expires_et，也可能有别的 allow_*=true；一旦切到 v2，这些都会被拒。因此 v2 只能逐个 runner 采用，c7805d9a 必须保留原样（冻结件钉了它）。建议 r3 把检查 12、13、15 限定在钉住本脚本的 .ok 上，或在文档里写明"v2 只接受单份 .ok"。
- **P2-V2（v2）** 检查 13 要求所有没请求 real_data 的运行都写 allow_real_data=false，但对拍、book 等 runner 本来就读真实数据，这样 .ok 里会出现语义上错误的 false。建议只在 scope=selftest 时强制，或让读真实数据的 runner 请求 real_data 模式。

P3
- P3-1 runner 父进程的命令行没有 PYTHONDONTWRITEBYTECODE，会在 scripts_eng/__pycache__ 写 ok_runner_pin 的 pyc。已在 .ok 注释和消息里把命令改为带前缀的版本。
- P3-2 VmRSS 轮询间隔 1 秒；子进程 ru_maxrss（peak_rss_mb_self）>1536 时，runner 不会判失败。回执里须逐个报告，超限的按 FAIL 处理。父进程（pandas 比对）不受监控。
- P3-3 _wide_limit_funds 会懒读 raw，而且 try/except 吞掉异常，本测试不会触发；以后加 sz.159xxx 用例时须改用 allow_real_data 或打桩。
- P3-4 quantlab/config.py 在 import 时对已有目录做 mkdir(exist_ok=True)，实际不写，记录在案。
- P3-5 测试文件先 import ok_runner_pin，后检查 dont_write_bytecode，顺序应对调。
- P3-6 T10 的子进程对整个仓库做静态扫描，其他 agent 新增文件可能让它失败，结果依赖仓库状态。回执须附扫描输出。
- P3-7 _compare 比较 parquet 时不比 index；名字叫 bit_identical，实际是逐值比较。
- P3-8 v2：值为 true 时大小写不敏感，为 false 时必须严格等于 'false'，两边不对称；同值重复键仍然允许（规范 §3 写的是不得重复）；runner 不传 scope 且不是 selftest 时不查 scope；known_allow 默认为空；gate sha 只在 selftest 时绑定；expires_et 只在启动时检查一次。
- P3-9 TEST_DEPS 有 68 项，其中多数是共享模块（strategy/*、data/*），任何一个被其他 agent 改动，测试都会拒跑，而且是失败即关闭。这是合理的，但 .ok 很容易过期，过期就重签。
- P3-10 仓库里的散落 __pycache__（Arch 按 mtime 判断）：
  - quantlab/platform/__pycache__ 下的 execution_sd1 / tradability / delist_accounting .cpython-313.pyc（01:33:48–01:34:12）、research/__pycache__/wb_sd1_books.cpython-313.pyc（01:34:12）、tests/__pycache__/test_sd1_suspend_delist.cpython-313.pyc（01:34:27）：时间和文件组合与 Eng r1 用默认 cfile 跑 py_compile 吻合，**很可能是 Eng**（r2 已改为写到 /tmp）。
  - scripts_eng/__pycache__/ok_runner_pin.cpython-313.pyc（02:00:02）：很可能是 Eng 02:00 的 AUDITFIX 运行。
  - 其余（大量 cpython-312 文件 01:18–01:58，来自 qlvenv；quantlab/data_sources 和 scripts/acquire 01:22；.pytest_cache 与 research/intel 01:17:48；quantlab/__pycache__/cli 和 portfolio/research_loop .cpython-313 02:07:57）来自其他 agent，Eng 未写。
  - 建议各 owner 在 10-19 纸面跑完之后自行清理；Arch 不删。

## 7. ok_runner_pin_v2 r2（6810b024924bb1c034ad53dcbe1dd30fa26027f5704562c888fcbfb65587aba1）全审

- c7805d9a 原有的 7 条检查，语义逐条保留：存在且可读；live 和 promotion 为 false；64 位十六进制；重复键须同值；runner pin；allow 须为 true、不得为 false；dep。v2 不 import v1。
- r2 新增：expires_et 对所有模式和 scope 必填，带时区且未过期；selftest 时 gate_ok_runner_pin_sha256 必须等于 Path(__file__).resolve() 当前的 sha，有人用同名文件抢先放进 sys.path 也会被拒；format 白名单只有 quantlab_run_auth_v1；ok_revision 只接受 [1-9]\d* 或 r[1-9]\d*。均正确。
- out_dir：只接受 mkdtemp 或 /tmp/<tag>，resolve 之后不得落在仓库或 output 下，符号链接指回仓库也会被拒。
- **结论：无 P0/P1，可以批准采用**，条件如下：逐个 runner 切换；不改 v1；P2-V1 和 P2-V2 在 r3 修，或在采用文档里写明限制；任何 runner 切到 v2 后，其 .ok 一律由 Arch 重签。

## 8. 给 Eng 的执行顺序与回执要求

1. 跑单测，命令照 TEST.ok 的注释，不得设置 QL_SD1_REAL_DATA。
2. 交单测回执。
3. Arch 审过并书面放行。
4. 再跑 paper 对拍，必须在当天 14:00 ET 前启动。
5. 交对拍回执。
6. research 套件另行申请。

峰值 RSS 用 /proc VmRSS 每秒采样，加 getrusage 或 ru_maxrss，不用 /usr/bin/time（box 上没有）。
