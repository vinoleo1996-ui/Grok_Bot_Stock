# Arch 复审：Eng SD1 r3.1（T10 静态扫描改造、sd0_parity_runner 7e3cc6ef）

- 审查人：QuantLab Arch；时间：2026-10-18 02:58 ET 起（America/New_York）
- 方式：**纯静态审查**。没有运行测试、对拍，没有 import 项目代码。只做了 sha256、diff 复现、AST 读码（ast.parse 读 TEST_DEPS 字面量、查 f 前缀），以及按授权以 PYTHONDONTWRITEBYTECODE=1 运行 scripts_eng/sd1_pit_static_check.py 的 pinned / disclosure 两种模式（只读文件，输出写 /tmp）。运行后确认没有新增 __pycache__。峰值内存远低于 1.5GB。
- 依据：上轮复审 docs/v2/ARCH_SD1_R3_REVIEW_ZH.md 2b8f81c9（§6.1 P1-1、P2-1、P3-1..4、§7）；Eng 消息 docs/v2/eng_sd1/MSG_TO_ARCH_SD1_R3_1_ZH.md 423c3634…681d；回执 ENG_SD1_R3_1_RECEIPT_ZH.md 49ac9770…f250。
- live=false · promotion=false

## 1. 结论

| 对象 | 结论 |
|---|---|
| SD1 r3.1（sd1_pit_static_check a8c0d3f6、测试 70ddd427、runner 7e3cc6ef） | **通过**。P0=0，P1=0，P2=0，P3 见 §6 |
| 上轮 P1-1（T10 只扫确定文件集） | **已落实** |
| 上轮 P2-1（tests/__pycache__ 遗留 pyc） | **已落实** |
| 上轮 P3-1..P3-4 | **已落实**（runner 记子进程起止时刻；docstring 写明孙进程与 float64 内存；T3 公式订正） |
| ARCH_SD1_TEST.ok | **本轮签发**（§7），原 4975aac8 归档到 docs/v2/eng_sd1/_superseded/ |
| ARCH_SD1_EXEC.ok | **维持作废**（eb3c3587）。单测回执经 Arch 审过后再签，out_tag 以 7e3cc6ef 结尾 |
| 披露扫描里的 10 条 VIOLATION | **不放宽白名单**，只作披露，不阻断 SD1；由 AI 在叶 r2.6/r5 处理（§5） |

## 2. sha 与完整性核对（Arch 实测，全长）

- 主干未动：quantlab/platform/execution.py 373fed309f055888e83572d3fbef8f5b5052ebfcb208307962a272bca6fc486c；quantlab/platform/__init__.py bfdfa63cbd7f39d7f0b1eb5a9b91ca00a30bdbd21e31ef3b90d89ac6080e99fc；scripts_eng/ok_runner_pin.py c7805d9a78e4f5478fa4c9e3becda48e76453ee0889b4f7027009a676c3e2485。
- r3.1 文件全部与 Eng 申请一致：
  - tests/test_sd1_suspend_delist.py 70ddd427cbd8905758ff4b66f934b2155b425fcecdddaf089c826b82b041711a
  - scripts_eng/sd1_pit_static_check.py a8c0d3f611b926850581289dbca55f5793c927a6c9ff7c819c98247fa144db35
  - scripts_eng/sd0_parity_runner.py 7e3cc6ef0f4a3cf645d64b641834198d5cbea1cce313c505d74a3d3962823542
  - docs/v2/eng_sd1/SD1_r3_to_r3_1.diff 24ada2758db9f999a5a81c16c05563698708940c01027fde14e8aa84b114576b
  - docs/v2/eng_sd1/SD1_SHAS.txt 06d5b017aed3d8d224b1c36124f50889a7a184eb117ca39a92d4604f6a0ca00b
  - docs/v2/eng_sd1/ENG_SD1_R3_1_RECEIPT_ZH.md 49ac9770dcf12cd395010f7ccf1198b835b91c890f6d40d33254c943a677f250
  - docs/v2/eng_sd1/MSG_TO_ARCH_SD1_R3_1_ZH.md 423c3634497b9f4dcaa079d399bdff18bc1c4600296ded952a302ae13172681d
  - docs/v2/eng_sd1/paper_import_closure.json 6919e7afe605cc4d1af48868a06b6550db66e3fd1923a3e61bdcc16c621bae20（156 项，内容未变）
  - pit_static_check_r3_1_pinned.json 9835f0e8bfcf79b6230d64cf166257d9e6294589315ea5492c01fce56b42a713；pit_static_check_r3_1_disclosure.json 27c121044aa755c2b92e2e6bc80168b0036dfa3cbef46bd46aaaece506f8d908
- r3.1 没有改动的文件，sha 与申请一致：execution_sd1 8c7615f7…00b1、tradability 968def30…892e、delist_accounting 222b63ae…062a、wb_sd1_books a2c36840…53ef、ok_runner_pin_v2 b7d8ea3f…31f1。
- **r3 基线核对**：/workspace/sd1_work/pre_r3_1/ 里，sd1_pit_static_check 3cfc1135、测试 37e85043、runner b4621ad5，与 2b8f81c9 §2 记的 r3 sha 一致。
- **diff 逐位复现**：按 static_check、test、runner 的顺序做 `diff -u --label a/<p>(r3) --label b/<p>(r3.1)` 后拼接，得到 280 行，sha256 = 24ada275…576b，与申请**逐位一致**。r3.1 只改了这三个文件。
- **TEST.ok 依赖核对**：用 ast 读测试文件里 TEST_DEPS 的字面量，共 69 项。Eng 草稿有 69 个 dep_sha256_* 键，两边的差集都为空，逐个重算 sha **69/69 一致**。和 4975aac8 相比：新增 1 个键 dep_sha256_paper_import_closure；改了 4 个值（runner_sha256_test_sd1_suspend_delist、dep_sha256_execution_sd1、dep_sha256_tradability、dep_sha256_sd1_pit_static_check）；没有删掉任何键。其余 64 个值没变。这也满足 2b8f81c9 §7 末段「测试读的新文件要钉为 dep」的要求。
- **P2-1**：tests/__pycache__/ 已经空了（目录保留）。备份 pre_r3_1/test_sd1_suspend_delist.cpython-313.pyc 的 sha 是 30defb2a…240f，45816B，mtime 01:34:27，与回执一致；pycache_before.txt 和 pycache_after.txt 里的前后清单与实际一致。

## 3. 代码审查（diff 全文 + 改动后的完整文件）

### 3.1 sd1_pit_static_check.py（a8c0d3f6）

- **pinned 模式是确定的**：
  - 先比对闭包清单 J 的 sha 和 --closure-sha256。不一致就立即返回 closure_ok=False，rc=1，一个文件也不扫。
  - 一致时，对 156 项逐个重算 sha。文件缺失（now=None）或 sha 不符都记进 closure_mismatch，最后 closure_ok=False，rc=1。
  - 扫描集合 = --files ∪ 闭包项，不做目录遍历，不读其他文件。
  - Arch 实测：把 --closure-sha256 换成全 0，rc=1。
- **FUNC_WHITELIST**：
  - 按「路径 + 函数名」放行，不按 sha。
  - 只有两条，都是 pool_benchmarks（imax、sue），都注明「主 Agent 02:44 裁定（基准池按 delist_date 截断）」。
  - 外层函数用 ast 判定：取所有 FunctionDef / AsyncFunctionDef 的 lineno..end_lineno，按起始行排序，任一外层 def 命中白名单即放行。所以嵌套在白名单函数里的命中也放行。
  - 文件解析失败（SyntaxError）时返回 []，不放行。
  - forced_scope（--paths 植入模式）一律判 VIOLATION。PREEXISTING 优先于 ALLOWED_FUNC。
- **disclosure 模式**：
  - 不带参数时默认就是 disclosure，rc=0。
  - 加 --strict 时，有违规就 rc=1。Arch 实测：默认 rc=0，--mode disclosure rc=0，--strict rc=1。
  - 测试里不再调用它（原来那条全仓 rc 断言已删）。
- **f 前缀检查**：用 AST 查了三个改动文件里含 `{name}` 的普通字符串，命中的只有 docstring、PREEXISTING 白名单里照抄的源码行，以及 runner 的 worker 源码模板（r3 未改的部分，模板本来就不该带 f）。**没有漏写 f 前缀的问题**。r3.1 新增的 f-string（L108 error 消息）写法正确。

### 3.2 测试（70ddd427）

- test_static_check_catches_planted：植入文件 2 条 VIOLATION 的用例保留，删掉了全仓 rc 断言。
- test_static_check_pinned_scope：
  - 子进程跑 pinned 模式。--files = TEST_DEPS 里 68 个 .py，加测试文件本身。
  - 闭包 sha 取自 `OK_KV["dep_sha256_paper_import_closure"]`。OK_KV 是 import 时 enforce 之后、用 parse_ok 解析 TEST.ok 得到的，所以**直接来自 TEST.ok**。
  - 断言 rc=0、mode=pinned、closure_ok、n_closure=156、0 违规、0 ALLOWED_FUNC、research/ 下没有命中。
- test_static_check_function_whitelist：
  - 合成文件放在 OUT_DIR 的临时目录下，用 rel_as 把它当作 imax 路径处理，**不读任何真实 research 文件**。
  - 预期结果逐行核过：L3 在 _inner 内，ALLOWED_FUNC；L4 在 pool_benchmarks 内，ALLOWED_FUNC；L7 在 evaluate 内，VIOLATION；L9 在模块级，VIOLATION。换成别的路径或 forced 模式时，4 条全是 VIOLATION。期望值正确。

### 3.3 sd0_parity_runner.py（7e3cc6ef）

- 只改了两处：
  - docstring 加了 r3.1 说明（P3-1 / P3-2 / P3-3）；
  - _run_child 在 Popen 前后各取一次 `datetime.now().astimezone()`，返回值里加了 child_started_et / child_finished_et。
- datetime 在 L44 已经 import。守卫、RSS 看门狗、比较逻辑都没动。**符合「只加时间戳和 docstring」**。

## 4. 扫描复现（Arch 实测，2026-10-18 02:58 ET）

| 模式 | Arch 实测 | Eng 申报 | 与 Eng 的 JSON 比较 |
|---|---|---|---|
| pinned（69 个 .py + 156 项闭包） | rc=0；n_files=162；闭包 156/156；7 PREEXISTING（survivorship 5、v2_multisleeve_book 1、universe/mask 1）；0 ALLOWED_FUNC；0 VIOLATION | 相同 | **对象完全相等** |
| disclosure（全 SCOPE） | rc=0（--strict 时 rc=1）；666 个文件；43 条命中 = 21 PREEXISTING + 12 ALLOWED_FUNC + 10 VIOLATION（imax 5、sue 5） | 相同 | **对象完全相等** |

两个叶脚本现在的 sha 是 imax 1e8de734…f7e5dc、sue 07c99873…42bfaa，与 Eng 扫描时一致，期间没再改。

## 5. 10 条 VIOLATION 的裁定（evaluate() 内）

- **核实结果**：两个文件里，delisted_master 只有一处读取，即 pool_benchmarks 内的 `pd.read_parquet(DELISTED, …)`（imax L377、sue L406）。读之前先 repin_file 核 sha。evaluate()（imax L628–786、sue L696–860）里没有读退市表。10 条命中是：
  - 回执说明文字（imax L648/649、sue L715/716）；
  - 结果键名 poolEW/wb_cagr244_cut_delist_date 和 *_diff_vs_cut_delist_date（L679/680、L747/748）；
  - note 字段（L681、L749）。
  这些数值来自 pool_benchmarks 返回的 Mp_dd / wv_dd（ewf 基准收益），只用于基准池年化的披露对比，不回流到选股或权重。这两个文件不在纸面闭包内。
- **裁定**：
  1. **不把 evaluate() 加进白名单**。evaluate 是叶脚本的主评估函数，整函数放行会让以后真正的前瞻读取漏过扫描。
  2. 这 10 条维持 disclosure-only 的 VIOLATION，**不阻断 SD1**（不在 pinned 范围，也不进单测）。
  3. 由 AI 在叶 r2.6/r5 里处理，首选是把 `*_cut_delist_date` 这几个差值键放进 pool_benchmarks 的 diag 里一起返回（计算本来就在白名单函数内），evaluate 只透传 diag。说明文字改用不含扫描词的中文表述（例如「按退市日截断」），或者把说明移进 pool_benchmarks 的 diag。
  4. 改名只是为了让扫描器的信号保持干净，**不能拿它当合规证明**。Arch 在叶审时逐行确认 delisted_master 只在 pool_benchmarks 内读取、*_dd 结果只用于披露，并重跑 disclosure，目标是这两个文件 0 VIOLATION。
  5. FUNC_WHITELIST 不变（只有那两条）。

## 6. 问题清单

- P0：无。P1：无。P2：无。
- **P3-1（措辞）** Eng 消息说 pinned「没扫到任何 research/ 文件」，不准确。
  - 闭包 156 项里有 16 个 research/ 文件（adj_price、ai_debate_memory_runner、g1g5_*_weights、s6_paper_extend 等），都在 SCOPE 内，都被实际扫描了，只是 0 命中。
  - 测试断言的其实是 research/ 下没有命中，变量名 scanned_research 有误导，下一版顺手改成 research_hits。
  - 另外，n_files=162 是候选文件数，其中只有 77 个在 SCOPE 内被实际扫描（quantlab/platform、scripts_eng、tests 等不在 SCOPE）。建议报告里另加 n_scanned。不阻断。
- **P3-2** pinned 模式不核 --files 自身的 sha，这部分靠测试 import 时 ok_runner_pin.enforce 先核 69 个 dep。在单测内这是确定的，但从 import 到 T10 子进程之间理论上有改动窗口；单独用 CLI 跑时也不能自称确定。建议以后 --files 也接受 sha 清单，或者在 T10 开始前重算 dep。不阻断。
- **P3-3** FUNC_WHITELIST 对「任一外层同名 def」放行：嵌在 evaluate 里的同名 pool_benchmarks、类方法、重复定义都会被放行。叶审时 Arch 会核两个文件各只有一个顶层 pool_benchmarks。不阻断。
- **P3-4** --paths 优先于 --mode，两者没有互斥；`--paths` 不带参数时会落到 disclosure。建议改用 argparse 互斥组。不阻断。
- **P3-5** research/__pycache__ 下还有旧 pyc，例如 wb_sd1_books.cpython-313.pyc（01:34:12）。按 Eng 计划 10-19 之后处理，接受。本次 Arch 扫描没有新增 pyc。
- **说明** TEST.ok 命令比 4975aac8 多了 `env -u QL_SD1_REAL_DATA`，与测试的 REAL_DATA 判定一致，接受。

## 7. 签发

- 已签 docs/v2/eng_sd1/ARCH_SD1_TEST.ok（sha 见 TEAM_STATE 和回复消息）。
  - scope=selftest；allow_selftest=true；其余 6 个 allow_* 全部显式写 false（含 allow_real_data=false）；live=false、promotion=false；out_dir=mkdtemp。
  - expires_et=2026-10-19T02:56:00-04:00，早于 10-19 17:40 ET 的纸面轨运行。
  - 69 个 dep 键全部按 §2 实测值写入；仍走 v1 门禁 c7805d9a。
- 原 4975aac8 归档为 docs/v2/eng_sd1/_superseded/ARCH_SD1_TEST.r2_4975aac8.ok。
- 格式已用 ok_runner_pin v1 的 parse_ok / enforce 逻辑和测试 _selftest_selfcheck 的规则逐条核对（读代码核对，没有执行项目代码）：无 BOM、无 CR、无行内 #、没有重复键、sha 全是 64 位小写十六进制、ISO8601 带时区、signed_et 不在未来。
- **EXEC.ok 不签**，eb3c3587 维持作废。

## 8. 给 Eng 的顺序

1. 按新 TEST.ok **只跑一次**单测，命令：`cd /workspace/QuantLab && env -u QL_SD1_REAL_DATA PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python -m pytest tests/test_sd1_suspend_delist.py -q -p no:cacheprovider`。要求：串行；不得与其他重任务并发；RSS ≤ 1.5GB，每 0.1 秒采样 VmRSS 并记录 VmHWM；跑完核对没有新增 __pycache__ 和 .pytest_cache。
2. 必须在 expires_et 之前跑完，并且避开 10-19 16:40–18:40 ET。闭包 156 项中任何一项在开跑前被改，T10 pinned 就会失败。这是预期行为，照实报告，不要自行改 .ok 或测试。
3. 回执交 Arch 审过之后，Arch 再签 EXEC.ok（out_tag 以 7e3cc6ef 结尾）。
