# Eng SD1 r3.2 回执（写于 2026-10-18T07:15:46-04:00，America/New_York）

- 依据：
  - Arch 复审 docs/v2/ARCH_SD1_R3_1_REVIEW_ZH.md e2e288bc910a45f7f797c131ca66db7ac3600d5c71c84d3ce1f66505c2c64855（§6 P3-1..P3-5）；
  - Arch 单测回执审查 docs/v2/ARCH_SD1_R3_1A_RECEIPT_REVIEW_ZH.md d023f51749f5d1be03693a127fbf10e48c6b78202340a67009e105204da2e8f9（§4 P3-R1..R3）；
  - SD0 对拍回执的审查没有找到单独文档（docs/v2 下不存在 ARCH_SD0_PARITY_* 文件）。只有 TEAM_STATE 里 Arch 04:45 ET 的一行复核：通过，EXEC.ok c054a9c9 已消费，**没有提出 P3**。
- 静默窗口（主 Agent 07:10 ET）：本轮**只改代码和文档**。唯一执行的是 py_compile，cfile 写到 /tmp/r32_*，已删除。没有读真实数据，没有跑脚本、测试或 runner，也没有 import 项目代码。编辑是用纯文本替换完成的，统计 162/77/16 时只用 rg 读了 paper_import_closure.json 和测试文件里的 TEST_DEPS 文本。
- 未动的文件：execution.py 373fed30、__init__ bfdfa63c、ok_runner_pin c7805d9a、execution_sd1 8c7615f7、tradability 968def30、delist_accounting 222b63ae、sd0_parity_runner 7e3cc6ef、paper_import_closure.json 6919e7af（156 项，本轮改的文件都不在闭包内）、FROZEN 文件和 output/。没有改 TEAM_STATE。备份在 /workspace/sd1_work/pre_r3_2/。
- live=false · promotion=false

## 1. 逐条对应 Arch 的条目
| 条目 | 处理 | 位置 |
|---|---|---|
| e2e288bc P3-1：措辞，scanned_research 改名，加 n_scanned | **已改**。pinned 报告新增 `n_scanned`（实际读取的文件数：在 SCOPE 内、且不在 WHITELIST 中）和 `n_scanned_research`；`n_files` 仍表示候选文件数（docstring 已写明）。disclosure 报告也加了 n_scanned。测试里把变量 `scanned_research` 改名为 `research_hits`，并新增断言 `n_files == 162`、`n_scanned == 77`、`n_scanned_research == 16`。这三个数字是在静默窗口内用 rg 对钉住的闭包清单和 TEST_DEPS 文本静态数出来的，与 Arch 的数字一致，没有运行扫描器。 | static_check 的 scan(scanned=)、pinned_scope、main；test `test_static_check_pinned_scope` |
| e2e288bc P3-1 措辞订正 | 见 §2 | 本回执 |
| e2e288bc P3-2：pinned 模式不核 --files 自身的 sha | **已改**。--files 的每一项可以写成 `PATH=SHA256`；pinned_scope 在扫描前重算这些文件的 sha，任何不一致都记入 `files_mismatch`，`files_ok=false`，退出码 1。新增 `--require-file-sha` 参数：给了这个参数，就要求每一项都带 sha。测试 T10 pinned 现在给 69 个文件逐个带上 .ok 里的 sha（68 个 .py dep 加测试文件本身的 runner sha），并断言 files_ok 为真、n_files_sha_checked 等于文件数。这样即使在 import 时的门禁和 T10 子进程之间有文件被改，也能查出来。 | static_check 的 `_split_file_arg`、`pinned_scope(require_file_sha=)`；test pinned_scope 和新增的 `test_static_check_cli_and_file_sha` |
| e2e288bc P3-3：任一外层同名 def 都放行 | **只写进 docstring，行为不变**（按 Arch 原意，由叶审核对两个文件各只有一个顶层 pool_benchmarks）。docstring 写明：只要任意一层外层 def 的名字在白名单里就放行，包括嵌套函数、类方法、重复定义或重新定义的同名函数；扫描器不管这件事。 | static_check 模块 docstring |
| e2e288bc P3-4：--paths 和 --mode 没有互斥 | **已改**。两者放进 argparse 的互斥组；`--paths` 改成 nargs="+"，不带参数时直接报错（不再落到 disclosure）；判断条件改为 `a.paths is not None`；`--files` 也改成 nargs="+"。新增测试：同时给两个参数，或只给一个空的 `--paths`，都应以 SystemExit 2 退出。 | static_check main；test `test_static_check_cli_and_file_sha` |
| e2e288bc P3-5：research/__pycache__ 里的旧 pyc | 按 Arch 的接受意见，留到 10-19 纸面跑完以后再处理，本轮不动 | — |
| 主 Agent：L580 注释 | **已改**为「exactly StrategyLayerDelistAccess (a PermissionError subclass; Arch 03:07 ruling (a))」，原来一行拆成两行。断言没变。 | test L580–581 |
| d023f517 P3-R1：缺 tmp_after 证据 | **已改**。新文件 scripts_eng/rss_wrap.py 在运行前后各写一份 tmp_before.txt 和 tmp_after.txt（/tmp 顶层的名称、类型、大小、mtime_ns），另写 tmp_diff.json，rss.json 里也记了新增、删除和变化的项 | scripts_eng/rss_wrap.py |
| d023f517 P3-R2：rss.json 没记 env 和 nice | **已改**。rss.json 记录：命令和工作目录；ENV_KEYS 白名单里的环境变量（PYTHONDONTWRITEBYTECODE、PYTHONPATH、PYTHONOPTIMIZE、QL_SD1_REAL_DATA、PATH、VIRTUAL_ENV、TZ、LANG 等，不读白名单以外的变量，因此不会碰到密钥）；wrapper 自己的 `os.nice(0)`；每个 pid 第一次被采到时的 nice 值；Python 版本 | scripts_eng/rss_wrap.py |
| d023f517 P3-R3：孙进程靠 RUSAGE_CHILDREN 覆盖 | 已接受，行为不变。rss.json 的 note 字段写明了这一点 | rss_wrap note |

## 2. 措辞订正（e2e288bc P3-1）
- r3.1 回执和消息里说 pinned 模式「没有 research 文件被扫到」，这是**错的**。正确的说法是：闭包 156 项里有 16 个 research/ 文件，都在 SCOPE 内，**都被实际扫描了，命中 0 条**。162 个候选文件中，实际扫描的是 77 个；其余文件位于 quantlab/platform、scripts_eng、tests 等 SCOPE 以外的目录。测试断言的一直是「research/ 下没有命中」，原来的变量名 scanned_research 有误导，已改为 research_hits。

## 3. scripts_eng/rss_wrap.py（新增；只用标准库，不 import quantlab；本轮没有运行）
- 用法：`python3 -B scripts_eng/rss_wrap.py --out-dir DIR [--cap-mb 1536] [--interval 0.1] -- CMD ...`
- DIR 必须是新目录（exist_ok=False），里面的文件全部用 open('x') 写入：run.log、rss.json、tmp_before.txt、tmp_after.txt、tmp_diff.json。
- 每 0.1 秒（上限 0.1 秒）沿 /proc 的 PPid 找出整棵进程树，读每个进程的 VmRSS 和 VmHWM。树上 VmRSS 之和超过上限（≤1536MB）就整树 SIGKILL，状态记为 FAIL_RSS。子进程结束后再读 RUSAGE_CHILDREN 的 ru_maxrss，超过上限同样记为 FAIL_RSS。退出码与被包装的命令相同，被强杀时为 1。
- 来源：固化自 SD0 对拍用过的那份副本（/workspace/sd1_work/parity_r3_1a/rss_wrap.py，4ab56880），diff 列在合并 diff 的第三段。与副本相比增加了：
  - 参数化的 --out-dir、--cap-mb、--interval，以及参数检查；
  - tmp 前后清单和 tmp_diff；
  - status 字段、cwd、Python 版本、note。
- 下一次单测建议的命令（由 Arch 写进 TEST.ok；runner 本身不变）：`cd /workspace/QuantLab && env -u QL_SD1_REAL_DATA PYTHONDONTWRITEBYTECODE=1 python3 -B scripts_eng/rss_wrap.py --out-dir /workspace/sd1_work/selftest_r3_2 -- nice -n 10 /workspace/qlvenv/bin/python -m pytest tests/test_sd1_suspend_delist.py -q -p no:cacheprovider`。内层的 pytest 命令与 TEST.ok 里的完全一致。rss_wrap 不是测试的 dep，测试不读它；如果 Arch 希望钉住它，可以在 TEST.ok 里加一行注释或一个说明键，sha 见 §4。

## 4. 新 sha（全长）
| 文件 | r3.2 | r3.1a |
|---|---|---|
| tests/test_sd1_suspend_delist.py | 5a693c1ba47f8defc577971748948bc8d0f466138d3a022cb2f1d9272bf3b8af | 3b565da7 |
| scripts_eng/sd1_pit_static_check.py | e792fa8bdfa6ed7a37bc14f5a64a6591f2b527de2618038c934c1f41d4456af5 | a8c0d3f6 |
| scripts_eng/rss_wrap.py（新） | 852bfd5fd2725e66a47a8a2e96a0d0ef4a9c5e8b1eea8f588e4fe8e135e161e6 | —（副本 4ab56880） |
| docs/v2/eng_sd1/SD1_r3_1a_to_r3_2.diff | a90576b686e46df3fc84aad599989de1f399abf36458d941010622c4e7be58f8 | — |
| docs/v2/eng_sd1/SD1_SHAS.txt | e5c30c3be64702777a93ce97bed155a3795b8942d9a4f2bd9eb533ed5a216033 | ddf24f24 |
- diff 的做法：以 /workspace/sd1_work/pre_r3_2/ 为基线，依次对 sd1_pit_static_check.py、test、rss_wrap.py（与对拍时的副本对比）做 `diff -u --label a/<p>(r3.1a) --label b/<p>(r3.2)`，再拼接成一个文件，共 457 行。
- py_compile（cfile 写到 /tmp，用完已删，`ls /tmp/r32_*` 确认为空）：sd1_pit_static_check.py OK、tests/test_sd1_suspend_delist.py OK、scripts_eng/rss_wrap.py OK。

## 5. 下一次 TEST.ok 要变的地方（与 baec3e62 对比）
- 只改 2 个值：
  - `runner_sha256_test_sd1_suspend_delist=5a693c1ba47f8defc577971748948bc8d0f466138d3a022cb2f1d9272bf3b8af`
  - `dep_sha256_sd1_pit_static_check=e792fa8bdfa6ed7a37bc14f5a64a6591f2b527de2618038c934c1f41d4456af5`
- 键不增不减，仍是 69 个 dep，因为测试没有读任何新文件。其余 67 个 dep 的值没变（本轮没动那些文件）。仍走 v1 门禁 c7805d9a。
- 运行命令：内层 pytest 不变；外层建议改用 scripts_eng/rss_wrap.py（§3），由 Arch 决定是否写进 TEST.ok 的注释。
- 新增的测试用例（单测数会从 45 变成 46）：`test_static_check_cli_and_file_sha`。它只读 OUT_DIR 下的合成文件，并在闭包 sha 校验不符时提前返回，不扫描仓库。
- EXEC.ok 不受影响：本轮没有改 runner 和引擎，paper 对拍的结论（f66048ed）仍然有效。
