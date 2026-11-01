# Eng SD1 r3.1 回执（2026-10-18 02:5x ET，America/New_York）

- 依据：Arch 复审 docs/v2/ARCH_SD1_R3_REVIEW_ZH.md 2b8f81c9373f61f6ad02d72dbb2acc06bdc51ef156d7d39ddad3f2fcb1535a2b（§6.1 P1-1、§6.2 P2-1、§6.3 P3-1~4、§7）；r3 回执 docs/v2/eng_sd1/ENG_SD1_R3_RECEIPT_ZH.md 587a39f2…87d2d1（不改写，订正写在本文 §3）。
- 本轮只执行了：py_compile（cfile 写 /tmp，已删）、sha256sum、sd1_pit_static_check.py（pinned 和 disclosure 两种模式，纯文本 + ast 扫描，不 import 项目代码）。**没有跑测试、没有对拍、没有写 .ok、没有 import 项目模块。**
- 未动：execution.py 373fed30…486c、`__init__.py` bfdfa63c…99fc、ok_runner_pin.py c7805d9a…2485、纸面闭包 156 项（扫描时逐个核对 156/156 一致）、冻结文件、所有 .ok。r3 基线备份在 /workspace/sd1_work/pre_r3_1/。
- live=false · promotion=false

## 1. P1-1 静态扫描重做（sd1_pit_static_check.py 3cfc1135 → a8c0d3f6）
- 三种模式：
  - `--mode pinned --closure J --closure-sha256 H --files F...`：只扫给定的钉住文件和纸面闭包 J 的 156 项。J 的 sha 必须等于 H，每一项的 sha 必须等于 J 里记录的值，否则判失败（closure_ok=false）。不读其他 agent 的文件，所以结果只取决于钉住的字节。有 VIOLATION 或闭包不一致时 rc=1。
  - `--mode disclosure [--json OUT] [--strict]`：全仓（SCOPE）披露报告，默认 rc=0，不进单测结果。不带参数时就是这个模式。加 `--strict` 才会在有 VIOLATION 时 rc=1。
  - `--paths F...`：植入文件模式，不用任何白名单，保持不变。
- 新增 `FUNC_WHITELIST`，按「路径 + 函数名」放行，**不按 sha**。用 ast 找到命中行外层的所有 def，任何一层的名字在白名单里就判 ALLOWED_FUNC。同一文件里不在该函数内的命中仍判 VIOLATION。文件解析不了就不放行。每条都注明「主 Agent 02:44 裁定（基准池按 delist_date 截断）」：
  - `research/g1g5_imax_intraday_alpha.py` :: `pool_benchmarks`
  - `research/g1g5_sue_desens_cs_alpha.py` :: `pool_benchmarks`
- 我读了这两个文件（当前 sha 分别是 1e8de734…e5dc 和 07c99873…bfaa，02:37 之后又改过）。delist_date 用来截断基准池只出现在 `pool_benchmarks` 里（imax 在 L369/377/378/379/400/467，sue 在 L398/406/407/408/429/496）。**白名单函数之外的命中，每个文件各 5 条，都在 `evaluate()` 里**：
  - imax L648、L649（回执说明文字）；L679–681（结果键 `poolEW_cagr244_cut_delist_date`、`wb_cagr244_cut_delist_date`、`*_diff_vs_cut_delist_date`，以及 note 字段）
  - sue L715、L716、L747–749，内容与 imax 相同
  - 这些行不读退市表，只是在报告文字和结果键名里出现 delist_date 这个词，但按裁定仍判 VIOLATION，请 Arch 或 AI 定夺：改名，或者把 `evaluate` 也列进白名单。Eng 没有替他们决定。它们只出现在 disclosure 报告里，不影响 SD1 单测。
- 测试 T10（37e85043 → 70ddd427）：
  - `test_static_check_catches_planted`：植入文件的 2 条 VIOLATION 用例保留；删掉了末尾那次无参数的全仓扫描。
  - 新增 `test_static_check_pinned_scope`：用子进程跑 `--mode pinned`，文件集是 TEST_DEPS 里的 .py 加测试文件本身，再加闭包；闭包 sha 取自 TEST.ok 的 `dep_sha256_paper_import_closure`。断言 rc=0、closure_ok、n_closure=156、n_violations=0、n_allowed_func=0，并且没有任何 research/ 文件被扫到。
  - 新增 `test_static_check_function_whitelist`：用合成内容冒充白名单路径（`rel_as`），不读真实 research 文件。断言函数内和嵌套函数内的命中判 ALLOWED_FUNC；`evaluate` 和模块级的命中判 VIOLATION；换成别的路径或用 forced 模式时 4 条全部判 VIOLATION。
  - TEST_DEPS 新增 `paper_import_closure` = docs/v2/eng_sd1/paper_import_closure.json 6919e7afe605cc4d1af48868a06b6550db66e3fd1923a3e61bdcc16c621bae20，共 69 项。另外加了 `import json`。
- 本轮的实际扫描结果（02:5x ET）：
  - pinned：rc=0。扫了 162 个文件（156 项闭包加上不在闭包里的钉住 .py），闭包 156/156 一致，7 条 PREEXISTING（beta/survivorship、portfolio/v2_multisleeve_book、universe/mask），0 条 VIOLATION，0 条 ALLOWED_FUNC。报告在 docs/v2/eng_sd1/pit_static_check_r3_1_pinned.json，sha 9835f0e8bfcf79b6230d64cf166257d9e6294589315ea5492c01fce56b42a713。
  - disclosure：rc=0（加 --strict 时是 1）。扫了 666 个文件，43 条命中：21 条 PREEXISTING、12 条 ALLOWED_FUNC、10 条 VIOLATION（两个 g1g5 文件各 5 条，都在 evaluate）。报告在 docs/v2/eng_sd1/pit_static_check_r3_1_disclosure.json，sha 27c121044aa755c2b92e2e6bc80168b0036dfa3cbef46bd46aaaece506f8d908。
  - 说明：pinned 模式扫的 tests/、quantlab/platform/ 不在 SCOPE 内，照旧跳过。这与 r2/r3 的规则一致，只是范围变成了确定的文件集。

## 2. P2-1：删除遗留 pyc
- 删除前（`ls -la --time-style=full-iso tests/__pycache__/`）：
  ```
  drwxr-xr-x 2 box box  4096 2026-10-18 01:34:27.332683904 -0400 .
  -rw-r--r-- 1 box box 45816 2026-10-18 01:34:27.332683904 -0400 test_sd1_suspend_delist.cpython-313.pyc   (sha256 30defb2a78381912cedd80eb069f43b4dd72ecbc6dd5c1a7acb56ac5bdd3240f)
  ```
- 删除后：
  ```
  drwxr-xr-x 2 box box  4096 2026-10-18 02:51:56.072683904 -0400 .
  （空）
  ```
- 只删了这一个文件，目录保留。tests/__pycache__ 里原本只有它一个。其他目录的旧 pyc 按指示留到 10-19 纸面跑完以后再处理。删前备份在 /workspace/sd1_work/pre_r3_1/。

## 3. 订正（不改写 r3 回执）
- **T3 公式（Arch P3-4）**：差额是 `0.023841858 = 1e6 × (0.4 − float32(1 − (float32(0.3) + float32(0.3))))`。r3 消息里写成「1e6×float32(1−(…))」，漏了「0.4 −」，那其实是现金应有的观测值 399999.976，不是差额。r3 回执 §2 L38 写的是观测值的式子，测试 L358 的注释写的是正确的差额式子，都不用改。
- 承接 r3 回执里的订正：r2 回执标题时间应为 02:28（不是 02:3x）。

## 4. P3 说明（也写进了 runner docstring）
- **P3-1**：runner 只在每个子进程启动前复查 16:40–18:40 窗口和冲突进程。子进程跑到一半进入窗口不会被拦，这由「14:00 ET 前开始」的规定覆盖。r3.1 起每个子进程的报告项里记 `child_started_et` 和 `child_finished_et`（ET，带时区偏移）。runner b4621ad5 → 7e3cc6ef。
- **P3-2**：VmRSS/VmHWM 轮询只看直接子进程。孙进程（pytest 里 T10 扫描、T11 -O 起的子进程）**只在事后靠 RUSAGE_CHILDREN 检查**，它包括已回收的孙进程。
- **P3-3**：SD1 路径（SD0 不变）的 TW/AW 是 float64，权重矩阵内存翻倍：全市场约 2000 日 × 5500 码 × 8B ≈ 88MB 一张，两张约 176MB。合成单测不受影响；**将来跑全市场 SD1 时要把这部分算进 1.5GB 预算。**
- 单测 RSS 采样（下次按 TEST.ok 跑时）：每 0.1 秒采样 /proc VmRSS，同时读 VmHWM，并用 getrusage 补查。

## 5. 新 sha（r3.1，全长）
| 文件 | sha256 | r3 |
|---|---|---|
| tests/test_sd1_suspend_delist.py | 70ddd427cbd8905758ff4b66f934b2155b425fcecdddaf089c826b82b041711a | 37e85043 |
| scripts_eng/sd1_pit_static_check.py | a8c0d3f611b926850581289dbca55f5793c927a6c9ff7c819c98247fa144db35 | 3cfc1135 |
| scripts_eng/sd0_parity_runner.py | 7e3cc6ef0f4a3cf645d64b641834198d5cbea1cce313c505d74a3d3962823542 | b4621ad5 |
| docs/v2/eng_sd1/SD1_r3_to_r3_1.diff | 24ada2758db9f999a5a81c16c05563698708940c01027fde14e8aa84b114576b | 新 |
| docs/v2/eng_sd1/paper_import_closure.json（新钉为 dep） | 6919e7afe605cc4d1af48868a06b6550db66e3fd1923a3e61bdcc16c621bae20 | 未变 |
| docs/v2/eng_sd1/SD1_SHAS.txt | 06d5b017aed3d8d224b1c36124f50889a7a184eb117ca39a92d4604f6a0ca00b | 5e572361 |
- 下面这些未变：execution_sd1 8c7615f7…00b1、tradability 968def30…892e、delist_accounting 222b63ae…062a、wb_sd1_books a2c36840…53ef、ok_runner_pin_v2 b7d8ea3f…31f1、execution.py 373fed30、`__init__` bfdfa63c、ok_runner_pin c7805d9a。
- diff 的做法：以 /workspace/sd1_work/pre_r3_1/ 为 r3 基线，按 static_check、test、runner 的顺序对每个文件做 `diff -u --label a/<p>(r3) --label b/<p>(r3.1)`，再依次拼接，共 280 行。
- py_compile 三个文件都 OK（cfile 写到 /tmp/r31_*，已删）。

## 6. ARCH_SD1_TEST.ok 与 4975aac8 相比的变化（草案在 SD1_SHAS.txt）
- **新增 1 个键**：`dep_sha256_paper_import_closure=6919e7afe605cc4d1af48868a06b6550db66e3fd1923a3e61bdcc16c621bae20`。这是按 §7 末段的要求加的，因为测试现在要读闭包清单。dep 键从 68 个变成 69 个。
- **改 4 个值**：
  - runner_sha256_test_sd1_suspend_delist = 70ddd427cbd8905758ff4b66f934b2155b425fcecdddaf089c826b82b041711a（4975aac8 签的是 r2 的 8305246b）
  - dep_sha256_execution_sd1 = 8c7615f7376b4482fe2f011fe08d47b2f2292c28be315659da5c0c5db74b00b1
  - dep_sha256_tradability = 968def30059826fa80846531b28ce514c9ed548d3c924034f3db31e3091b892e
  - dep_sha256_sd1_pit_static_check = a8c0d3f611b926850581289dbca55f5793c927a6c9ff7c819c98247fa144db35
- 其余 64 个 dep 值重算后未变；其他键与 4975aac8 相同。signed_et 和 expires_et 由 Arch 定。仍走 v1 门禁 c7805d9a。命令不变：`cd /workspace/QuantLab && env -u QL_SD1_REAL_DATA PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python -m pytest tests/test_sd1_suspend_delist.py -q -p no:cacheprovider`
- 风险提示：闭包里 156 项中任何一个文件改动（也就是纸面路径改动），T10 pinned 都会判失败（closure_mismatch）。这是有意的：纸面路径变化应该让人注意到，结果仍然只取决于钉住的字节。
- ARCH_SD1_EXEC.ok：维持作废。runner 改成了 7e3cc6ef，所以届时 out_tag 要以 7e3cc6ef 结尾；草案已更新。
