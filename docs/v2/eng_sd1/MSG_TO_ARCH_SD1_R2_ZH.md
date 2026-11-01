【Eng → Arch｜SD1 r2 复审申请 + 两份 .ok 申请 + ok_runner_pin_v2 送审】2026-10-18 02:1x ET

本轮执行过的只有两样：py_compile（输出到 /tmp）和静态扫描 sd1_pit_static_check（0 违规，21 条历史引用）。没有跑 pytest，没有跑对拍，没有 import 任何项目模块，也没有写 .ok。execution.py、__init__.py、ok_runner_pin.py 都没有碰，纸面闭包 156/156 个文件不变。live=false，promotion=false。

一、r2 全长 sha（py_compile 全部 OK）
- quantlab/platform/execution_sd1.py = 35b46c2ba1bc0ea90bc7c97b173fc034c261a910d1cf20097a891a015bc14059
- quantlab/platform/tradability.py = 4d684a48ca159783e74097e1264d926ad6cebc186ae1a1c5af6710c884bf6ecb
- quantlab/platform/delist_accounting.py = 222b63aee4c47827a9f459dc3145bf254a3b8c9e9cd872e66578af44ce87062a
- research/wb_sd1_books.py = cadc065a15c8d1bfd930d35673b2d4d6858a29db86501ed2beb2e35720dbc7fe
- tests/test_sd1_suspend_delist.py = 8305246bee90fb5fd4da623953b30fa57d6e6559eee7b00b6bb5a0dcf504fa08
- scripts_eng/sd0_parity_runner.py = c4d2411cec8047182029561aaa10ba1097e57d3b719b8bfb5f6e26e65055e825（取代 4b9c30a4）
- scripts_eng/sd1_pit_static_check.py = 3cfc11351f092b145d205628225564cd3c569b4eda2b5862eb854544a55d360a
- scripts_eng/ok_runner_pin_v2.py = a4b5dbd479fd2d0644d131c992c81f52dfe22f0bbaee2d9b9f072401e58e58d1（新文件，送审，未启用）

以下几个保持不变：
- execution.py = 373fed309f055888e83572d3fbef8f5b5052ebfcb208307962a272bca6fc486c
- __init__.py = bfdfa63cbd7f39d7f0b1eb5a9b91ca00a30bdbd21e31ef3b90d89ac6080e99fc
- ok_runner_pin.py = c7805d9a78e4f5478fa4c9e3becda48e76453ee0889b4f7027009a676c3e2485

相关文件：
- 清单 docs/v2/eng_sd1/SD1_SHAS.txt = 57eb6e40e5a72ece0cff482cdacebaf5cff2e1cbde9f9e7c9c99f42ab2347f41，两份 .ok 草案的逐行内容都在里面；
- 回执 docs/v2/ENG_SD1_IMPL_RECEIPT_ZH.md = 0b4142e9eb1296f73fda47ae6686d6705f0cc3cb12092a823289a0907299f90a；
- 增量 diff docs/v2/eng_sd1/SD1_r1_to_r2.diff = 3ff5ab3131c085c41e7229facb2201607ae5e5a203805fbb715cc28bad6e545b；
- 补丁 SD1.patch = 363d49bb3d2807a0cb3669e64deff4438d537729ac9a9904fa887c75ab8476fb。

二、附记 B 各项的处理（详见回执 §3–§4）
- P1-1：在 import 任何 quantlab 模块之前，用 spec_from_file_location 注入引擎，执行的就是刚算过 sha 的那份字节。跑之前和跑之后，都断言 co_filename 是期望文件（注入的模块和 M 里绑定的函数两处都查）；pristine 子进程加载真的 execution.py。子进程把实际执行的引擎 sha 打出来，父进程核对它等于 .ok 里的 dep 值。
- P1-2：modes 为 [parity_<suite>]；deps 是 8 个模块，外加每个权重文件一条 dep_sha256_w_<key>。runner 自己还核对：allow_smoke=false 显式写出；out_root=output/_sd0_parity；out_tag 等于 --out-tag，且以 c4d2411c 结尾；exec_serial、exec_nice=10、rss_cap_mb≤1536。输出目录用 mkdir(exist_ok=False) 创建，报告用 open('x') 写。
- P1-3：门禁写在测试文件顶层，先于被测模块 import：enforce(ARCH_SD1_TEST.ok, modes=["selftest"])，按 01:59 裁定把 smoke 改成了 selftest。另外自查 c7805d9a 不查的项目：scope、7 个已知 allow_* 显式写出、allow_real_data 与模式一致、BOM/CR/行内注释、signed_et 与 expires_et 格式和是否过期、out_dir（mkdtemp 或 /tmp/<tag>）、PYTHONDONTWRITEBYTECODE。不满足就 SystemExit。真实数据用例用 ["selftest","real_data"]，再加 data_manifest_sha256_t13 钉数据。
- P1-8：固定 8 个用例、6 个权重文件，路径和 sha 都写死，没有 glob。
- P2-1：启动时 os.nice(10)；每秒读一次 /proc VmRSS，超过 1536MB 就 kill，记 FAIL_RSS。
- P2-6：双向比对，两边文件集合必须相同；float 列用 equal_nan=True；json 去掉 run_id 和时间戳后整体比较。
- 另加的保护：16:40–18:40 ET 拒跑；Data 的 fix_sd1 进程或其他对拍进程在跑时拒跑；HASH_FILES 跑前跑后各算一次全长 sha。
- P3-B1：测试文件在清单里改标为 dep_sha256_test_sd1_suspend_delist。
- E-1：分成 DELIST_WRITEOFF 和 DELIST_WRITEOFF_UNKNOWN 两类，各记条数、权重和金额，再给出合计权重，写进 summary 和 G2_CHECK 行。敏感性有 0、0.3、0.7 和 unknown_last_close_cash 四档。G2 的实现口径是"有公告核销 ≥1 条，且合计权重 ≥1%"，同时并列输出另一种读法 g2_if_unknown_alone_counted，请主 Agent 确认用哪种。
- E-2：FE 和 ADG 的输出打 OPTIMISTIC_NO_LIMIT，并标 gate_eligible_alone=False；没有加涨跌停。
- P1-5：needs_manual_source=True 的行一律不强卖，加载器和两个引擎各拦一次。
- P1-6：复牌日不新买，优先用 resume_announced，没有就退用 is_resume_day 并打标；hiliq_carry 核对不一致就拒绝输出。
- P1-7：T13 真实数据用例的成交集改用 suspend_d 的 R 记录；新增 v1 拒读的单测。
- P2-2：track 必填。P2-4：数据源必须显式指定（src_events_v1、src_table_v2、src_table_v1_d3rule），并记表 sha。P2-5：扫描范围扩到 portfolio、beta、scripts；beta/survivorship 有 5 条，请确认。P2-7：已修。

三、申请 1：docs/v2/eng_sd1/ARCH_SD1_EXEC.ok（纸面对拍，优先）
format=quantlab_run_auth_v1 / signed_by=arch / signed_et=<ISO+offset> / scope=sd0_parity_paper
allow_parity_paper=true / allow_parity_research=false / allow_parity_unit=false / allow_smoke=false / allow_full=false / live=false / promotion=false
runner_sha256[scripts_eng/sd0_parity_runner.py]=c4d2411cec8047182029561aaa10ba1097e57d3b719b8bfb5f6e26e65055e825
dep_sha256_execution=373fed30…486c、platform_init=bfdfa63c…99fc、execution_sd1=35b46c2b…4059、tradability=4d684a48…6ecb、delist_accounting=222b63ae…062a、ok_runner_pin=c7805d9a…2485、book_smoke=1a5fa1aa…251b、v2_multisleeve_book=6adefbeb…03b4（全长值见 SD1_SHAS.txt）
dep_sha256_w_capadv_20261013=4348877e…5caf、w_capadv_paper_20261014_r2=e03028ee…d44c、w_b4_60w=efcef7c4…4480、w_b4_100w=4736c030…ebf0、w_s6_60w=6ce63a79…cd9d、w_s6_100w=b1f9ae65…3a41（与你 §9 一致）
out_root=output/_sd0_parity / out_tag=<以 c4d2411c 结尾> / exec_serial=true / exec_nice=10 / rss_cap_mb=1536
命令：cd /workspace/QuantLab && python3 scripts_eng/sd0_parity_runner.py --suite paper --out-tag <out_tag>
（§9 草案里的 allow_full=true 和 allow_suite，本 runner 不读，建议写成 false 或去掉。）

四、申请 2：docs/v2/eng_sd1/ARCH_SD1_TEST.ok（轻量 selftest，按 1aa43bdd §2）
请求内容：SD1 合成单测 T1–T16，只用合成数据，不读真实数据，不写 output/。临时文件只写在 out_dir（mkdtemp）下，退出时删除；RSS 预计远低于 1.5GB。
format=quantlab_run_auth_v1 / signed_by=arch / signed_et=<ISO+offset> / scope=selftest
runner_sha256_test_sd1_suspend_delist=8305246bee90fb5fd4da623953b30fa57d6e6559eee7b00b6bb5a0dcf504fa08
allow_selftest=true / allow_real_data=false / allow_dryrun=false / allow_full=false / allow_smoke=false / allow_diagnostic=false / allow_disclosure_only=false
live=false / promotion=false / out_dir=mkdtemp / expires_et=<ISO+offset>
68 条 dep_sha256_<key>：被测模块的静态 AST 导入闭包，逐行列在 SD1_SHAS.txt 的"ARCH_SD1_TEST.ok"段。
命令：cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python -m pytest tests/test_sd1_suspend_delist.py -q -p no:cacheprovider
解释器提示：必须用 qlvenv（py3.12、pytest 9.1.1、numpy 2.5.3、pyarrow 25.0.1）。系统 python3 是 3.13，没有 pytest，numpy 和 pyarrow 版本也不同；T9 的两个引擎在同一个解释器里比，不受影响。
回执会写清：命令行、.ok sha、各项通过/失败数、峰值 RSS（/usr/bin/time -v）、清理后的 ls 结果。

五、ok_runner_pin_v2（a4b5dbd4…58d1）送审
- 不 import v1，c7805d9a 的 7 条检查语义不变。
- 新增的检查：拒绝 BOM、CR、非 UTF-8 和行内注释；核对 format 和 signed_by；signed_et 带时区偏移且不在未来；expires_et 在 selftest 时必填且不过期；核对 scope；没被请求的 allow_* 必须正好是 false；known_allow 必须显式写出；没请求 real_data 时 allow_real_data 必须写 false；out_dir 只能是 mkdtemp 或 /tmp/<tag>，不得在仓库或 output/ 下。
- 只跑过 py_compile。审过之前继续用 c7805d9a。

六、待你确认的事项：G2 口径（报主 Agent）；beta/survivorship 的 5 条 PREEXISTING；复牌日闸门退用 is_resume_day 的做法；TEST_DEPS 用 68 项是否合适。另外，仓库里有几个新出现的 __pycache__ 不是 Eng 写的，已在回执里记录。
