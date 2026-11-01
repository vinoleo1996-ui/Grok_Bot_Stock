Arch，SD1 r3.1 已按你的复审 2b8f81c9 交付。本轮只做了 py_compile（cfile 写到 /tmp，已删）、sha256sum，以及 sd1_pit_static_check 的 pinned 和 disclosure 两种模式。没跑测试，没跑对拍，没写 .ok，没 import 项目代码。execution.py 373fed30、__init__ bfdfa63c、ok_runner_pin c7805d9a、纸面闭包（156/156）和冻结件都没动。

【新 sha（全长）】
- tests/test_sd1_suspend_delist.py 70ddd427cbd8905758ff4b66f934b2155b425fcecdddaf089c826b82b041711a（r3 是 37e85043）
- scripts_eng/sd1_pit_static_check.py a8c0d3f611b926850581289dbca55f5793c927a6c9ff7c819c98247fa144db35（r3 是 3cfc1135）
- scripts_eng/sd0_parity_runner.py 7e3cc6ef0f4a3cf645d64b641834198d5cbea1cce313c505d74a3d3962823542（r3 是 b4621ad5；只加了子进程起止时刻记录和 docstring 说明）
- docs/v2/eng_sd1/SD1_r3_to_r3_1.diff 24ada2758db9f999a5a81c16c05563698708940c01027fde14e8aa84b114576b（基线 /workspace/sd1_work/pre_r3_1/；按 static_check、test、runner 的顺序做 diff -u --label a/<p>(r3) --label b/<p>(r3.1) 后拼接，共 280 行）
- docs/v2/eng_sd1/SD1_SHAS.txt 06d5b017aed3d8d224b1c36124f50889a7a184eb117ca39a92d4604f6a0ca00b
- docs/v2/eng_sd1/ENG_SD1_R3_1_RECEIPT_ZH.md 49ac9770dcf12cd395010f7ccf1198b835b91c890f6d40d33254c943a677f250
- 新钉为 dep：docs/v2/eng_sd1/paper_import_closure.json 6919e7afe605cc4d1af48868a06b6550db66e3fd1923a3e61bdcc16c621bae20（内容未变）
- 扫描报告：pit_static_check_r3_1_pinned.json 9835f0e8bfcf79b6230d64cf166257d9e6294589315ea5492c01fce56b42a713；pit_static_check_r3_1_disclosure.json 27c121044aa755c2b92e2e6bc80168b0036dfa3cbef46bd46aaaece506f8d908
- 以下文件未变：execution_sd1 8c7615f7、tradability 968def30、delist_accounting 222b63ae、wb_sd1_books a2c36840、ok_runner_pin_v2 b7d8ea3f
- 三个改动文件的 py_compile 都 OK。

【P1-1 静态扫描】
- 新增 --mode pinned：只扫给定的钉住文件和闭包 156 项。闭包清单的 sha 必须对上，每一项也必须和清单里记的 sha 一致，否则判失败。不读其他文件，所以结果确定。
- --mode disclosure：全仓披露报告，默认 rc=0，不进单测结果；也是不带参数时的默认模式。加 --strict 时，有违规就 rc=1。
- --paths：植入模式，保持不变。
- FUNC_WHITELIST 按「路径 + 函数名」放行，不按 sha。用 ast 找命中行外层的 def，嵌套在白名单函数里也算放行；文件解析失败就不放行。目前两条，都注明「主 Agent 02:44 裁定（基准池按 delist_date 截断）」：research/g1g5_imax_intraday_alpha.py::pool_benchmarks、research/g1g5_sue_desens_cs_alpha.py::pool_benchmarks。
- T10 的改动：
  - 植入文件仍是 2 条 VIOLATION；删掉了原来的全仓 rc 断言。
  - 新增 test_static_check_pinned_scope：子进程跑 pinned 模式，闭包 sha 取自 TEST.ok 的 dep_sha256_paper_import_closure；断言 rc=0、closure_ok、156 项、0 条违规、没扫到任何 research/ 文件。
  - 新增 test_static_check_function_whitelist：用合成内容冒充白名单路径，不读真实 research 文件。断言函数内和嵌套函数内判放行，evaluate 和模块级判违规；换别的路径或 forced 模式时 4 条全部判违规。
- 本次实际扫描：
  - pinned：rc=0。162 个文件，闭包 156/156 一致，7 条 PREEXISTING（beta/survivorship、portfolio/v2_multisleeve_book、universe/mask），0 条违规。
  - disclosure：rc=0。666 个文件，43 条命中：21 条 PREEXISTING、12 条 ALLOWED_FUNC（两个文件的 pool_benchmarks 各 6 条）、10 条 VIOLATION。
- **需要你或 AI 裁定**：白名单函数之外的命中，每个文件 5 条，都在 evaluate() 里，内容是回执说明文字和结果键名（poolEW_cagr244_cut_delist_date、wb_cagr244_cut_delist_date、*_diff_vs_cut_delist_date、note 字段），不读退市表。具体是 imax L648/649/679/680/681，sue L715/716/747/748/749（文件现在的 sha 是 imax 1e8de734、sue 07c99873，02:37 之后又改过）。按裁定我把它们判为 VIOLATION，不影响 SD1 单测。可以改名，也可以把 evaluate 列进白名单。

【P2-1】tests/__pycache__/test_sd1_suspend_delist.cpython-313.pyc（01:34:27，45816B，sha 30defb2a…240f）已删，删前备份到 /workspace/sd1_work/pre_r3_1/。删前目录里只有这一个文件，删后为空，目录保留。前后清单见回执 §2。其他目录的旧 pyc 留到 10-19 之后处理。

【P3】
- 订正：T3 差额 = 1e6×(0.4 − float32(1−(float32(0.3)+float32(0.3)))) = 0.023841858。
- runner 现在记录每个子进程的 child_started_et 和 child_finished_et。子进程运行期间不复查窗口，由「14:00 前开始」的规定覆盖。
- 孙进程的 RSS 只在事后靠 RUSAGE_CHILDREN 检查。
- SD1 用 float64 后 TW/AW 内存翻倍，全市场约 176MB，将来跑全市场时要计入 1.5GB 预算。

【TEST.ok 与 4975aac8 的差别】草案在 SD1_SHAS 里。
- 新增 1 个键：dep_sha256_paper_import_closure=6919e7afe605cc4d1af48868a06b6550db66e3fd1923a3e61bdcc16c621bae20。这是按你 §7 末段的要求，dep 键从 68 个变成 69 个。
- 改 4 个值：
  - runner_sha256_test_sd1_suspend_delist=70ddd427cbd8905758ff4b66f934b2155b425fcecdddaf089c826b82b041711a
  - dep_sha256_execution_sd1=8c7615f7376b4482fe2f011fe08d47b2f2292c28be315659da5c0c5db74b00b1
  - dep_sha256_tradability=968def30059826fa80846531b28ce514c9ed548d3c924034f3db31e3091b892e
  - dep_sha256_sd1_pit_static_check=a8c0d3f611b926850581289dbca55f5793c927a6c9ff7c819c98247fa144db35
- 其余 64 个 dep 重算未变；signed_et 和 expires_et 由你定；仍用 v1 c7805d9a。
- 命令不变：cd /workspace/QuantLab && env -u QL_SD1_REAL_DATA PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python -m pytest tests/test_sd1_suspend_delist.py -q -p no:cacheprovider
- 提示：闭包 156 项里任何一个文件改动，T10 pinned 都会失败。这是有意的，纸面路径的变化应当被发现。
- EXEC.ok 维持作废；以后签时 out_tag 要以 7e3cc6ef 结尾。
