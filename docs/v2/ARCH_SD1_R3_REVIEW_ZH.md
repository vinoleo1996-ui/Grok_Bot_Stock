# Arch 复审：Eng SD1 r3（含 sd0_parity_runner b4621ad5、ok_runner_pin_v2 r3）

- 审查人：QuantLab Arch；时间：2026-10-18 02:47 ET 起（America/New_York）
- 方式：**纯静态审查**。没有运行 Eng 的测试、runner、对拍；只用 python 做了 sha256、diff 复现、闭包核对和 T3 的纯算术（numpy float32）。峰值内存远低于 1.5GB。
- 依据：规格 docs/v2/ARCH_ENGINE_SUSPEND_DELIST_FIX_SPEC_ZH.md 2e428f39；上轮复审 docs/v2/ARCH_SD1_R2_REVIEW_ZH.md 73cb88ac；单测回执 docs/v2/eng_sd1/SD1_SELFTEST_RECEIPT_ZH.md 1873c9ab（31 过 / 4 败 / 1 跳过）；Eng r3 回执 docs/v2/eng_sd1/ENG_SD1_R3_RECEIPT_ZH.md 587a39f2。
- live=false · promotion=false

## 1. 结论

| 对象 | 结论 |
|---|---|
| SD1 r3 引擎、测试修复（T1/T3/T10/T11） | **代码层通过**。P0=0。T1、T3 定性经 Arch 独立核实属实 |
| T10 静态扫描子项 | **P1-1，须 r3.1**：现行测试对全仓扫描（结果取决于其他 agent 的改动），按本轮裁定改为只扫 SD1 钉住文件集 + 纸面导入闭包 |
| sd0_parity_runner b4621ad5 | 通过（P2-R1、P3-2、P3-7 已落实），附 P3 |
| ok_runner_pin_v2 r3（b7d8ea3f） | **批准按 runner 逐个采用**；不得原地替换 v1 c7805d9a |
| ARCH_SD1_TEST.ok | **本轮不签**。现行测试的 T10 会扫全仓，必失败。等 r3.1 的新 sha 再签，草稿见 §7 |
| ARCH_SD1_EXEC.ok | 维持作废（eb3c3587）。单测回执经 Arch 审过后再签，out_tag 以届时的 runner sha8 结尾 |

## 2. sha 与完整性核对（Arch 实测，全长）

- r3 文件全部与 Eng 申请一致：execution_sd1 8c7615f7…00b1、tradability 968def30…892e、wb_sd1_books a2c36840…53ef、test 37e85043…000a、runner b4621ad5…af73、ok_runner_pin_v2 b7d8ea3f…31f1；delist_accounting 222b63ae…062a、sd1_pit_static_check 3cfc1135…360a 未变；SD1_SHAS.txt 5e572361…0d2b；SD1_r2_to_r3.diff 04834a67…0210；SD1.patch fd9a97e6…c32c；r3 回执 587a39f2…87d2d1。
- 主干未动：execution.py 373fed30…486c、__init__.py bfdfa63c…99fc、ok_runner_pin.py c7805d9a…2485。
- **diff 逐位复现**：以 /workspace/sd1_work/pre_r3/ 为 r2 基线（其中 execution_sd1 35b46c2b、tradability 4d684a48、test 8305246b、runner c4d2411c、wb_sd1_books cadc065a、v2 6810b024，与 73cb88ac §2 的 r2 sha 全部一致），对 6 个文件按 `diff -u --label a/<p>(r2) --label b/<p>(r3)` 依次拼接，得 sha256 = 04834a67…0210，与申请**逐位一致**。
- **纸面闭包**：paper_import_closure.json 156 项逐个重算 sha，**156/156 一致**；SD1 四个旁路文件都不在闭包内。
- **TEST.ok 依赖核对（回应 wb_sd1_books 疑问）**：测试文件 TEST_DEPS 共 68 项，与 4975aac8 的 68 个 dep_sha256_* 键一一对应（双向差集为空）。逐个重算后**只有 execution_sd1、tradability 两项变了**；加上 runner_sha256_test_sd1_suspend_delist，正好是 Eng 说的 3 个值。**wb_sd1_books 不是 TEST.ok 的 dep**（测试不 import 它，runner 的 MODULE_DEPS 也不含），它的 sha 变化不影响两份 .ok。

## 3. T1 定性（独立核实）

- r2 夹具 `_panels`（pre_r3 测试 L213–215）：`prev = C.ffill().shift(1)`，`LD = (prev*0.9).round(2)`。停牌 d[3]–d[5] 收盘为 NaN，所以复牌日 d[6] 的 prev = 10，LD = 9.0，开盘 8.0。
- 主干 execution.py L754–755：`side<0 and isfinite(LD) and px0 <= LD+eps` → 记 limit_down 事件并 continue。execution_sd1 L913–914 逻辑相同（open_touch 分支）。所以 d[6] 不能卖，按 unfilled='carry'（主干 L317 / SD1 L384）挂到 d[7]（LD = 8×0.9 = 7.2，开盘 8.0 > 7.2）才成交。
- 停牌日的卖单生成：标记价 Cm 用 ffill（主干 L645 / SD1 L780），d[3] 按标记价 10 定量，与 Eng 描述一致。
- 规格 §3.4 L151：特殊情形（无涨跌幅）由 Data 提供，引擎只读 limit 字段；§3.8 T1（L214）只要求停牌日无成交、NAV 不变、复牌日 NAV 变化 = 持仓×−20%、权重型引擎结果相同，**不要求 d[6] 卖出**。那条断言是 r2 测试自己加的。
- **结论：属测试夹具问题，不是引擎问题，CFG0、CFG1 都一样**。引擎在 open_touch 下的行为符合规格 §3.4。
- r3 新测试（L245–330）拆成 4 个用例 + 权重型引擎：无涨跌幅复牌（d[6] 的 LU/LD 设 NaN）→ d[6] 按开盘 8.0 卖 5 万股；原夹具 → d[6] 无卖单且有 limit_down 事件、d[7] 卖 5 万股；两种都核停牌日无成交、NAV 不变、d[6] NAV 变化 = 1e5×(8−10)。覆盖了规格 T1 的全部断言。NaN 限价在引擎里因 `isfinite` 判断而不拦，与 Data 的编码约定一致。

## 4. T3 定性（独立核实）

- 纯算术（numpy）：`float32(1) − (float32(0.3)+float32(0.3))` = 0.39999997615814…；0.4 − 该值 = 2.384185793e−8，乘 1e6 = **0.023841858**，与回执的 0.0238 逐位一致。没有费用、整手或冻结仓位缺口。
- 措辞小订正（P3-4）：Eng 消息里写成「1e6×float32(1−(…))」，那是现金应有值 399999.976；差额是 1e6×(0.4 − float32(1−(…)))。测试 L358 注释写的是正确式子。
- 根因确是 r2 的 TW/AW/cur_tw 用 float32 存。主干 L718–720、L882、L940 也是 float32（诊断用，不参与下单、现金、股数，后三者一直是 float64）。
- **float64 切换不影响 SD0 对拍语义**：r3 在 execution_sd1 L874 用 `WDT = float32 if cfg.engine_version == "exec_SD0" else float64`；engine_version（L424–428）在全部 SD1 开关取旧值时才是 exec_SD0。对拍 runner 注入 execution_sd1 跑默认 ExecConfig → exec_SD0 → float32，与主干逐位可比；runner `_compare`（L295–）同时比 dtypes 和 index，dtype 不同会直接判不等，不会被掩盖。T9（L549–550）也断言 CFG0 下 actual/target_weights 的 dtype 与主干相同。TW/AW 只用于输出，不回流到下单（grep 只在 L875–877、L1244–1246、L1300–1302、L1338–1339 出现）。
- 测试改为：SD1 dtype 必须是 float64，现金期望值写成显式公式（renorm → 0，cash → nav_open(d3)×0.4），绝对容差 1e−6，并另核引擎 float64 账面现金。**符合我上轮「追溯，不放宽容差」的要求。**

## 5. T10 / T11

- T10 `test_strategy_caller_raises`：植入调用带有效 source，只能被 PIT 守卫拦 → 精确断言 PermissionError；`test_no_source_is_type_error`：不带 source → 精确 TypeError 且消息含 source，对策略和允许的调用方都测。所有退市源先指到 OUT_DIR 下不存在的文件，守卫失效也读不到真实数据（会抛 FileNotFoundError，被精确类型断言拒掉）。T11 在 -O 下同样核 `GUARD_EXC PermissionError` 和 `NOSRC_EXC TypeError`。**符合上轮要求。**
- **P1-1（T10 静态扫描子项）**：`test_static_check_catches_planted` 末尾无参数运行 sd1_pit_static_check.py，扫的是 SCOPE 全仓（research/、quantlab/strategy/ 等）。结果取决于其他 agent 的文件：现在 research/g1g5_imax_intraday_alpha.py、research/g1g5_sue_desens_cs_alpha.py 因按主 Agent 02:44 裁定用 delist_date 截断基准池，命中 10 条，单测必失败。SD1 单测结论不能受别的 agent 改动影响。**裁定见 §6.1。**

## 6. 问题清单

### 6.1 P1-1 静态扫描裁定（Arch，r3.1 实现）

1. **不按 sha 加白名单**：这两个叶脚本还会再改，按 sha 白名单会反复失效。
2. **SD1 单测内的 T10 只扫确定的文件集**：SD1 钉住的文件（TEST.ok 的 runner + dep 文件）加纸面导入闭包（paper_import_closure.json 的 156 项），结果不随其他 agent 的改动变化。植入文件的 2 条 VIOLATION 用例保留。
3. **全仓扫描改为独立的披露报告**，不进单测通过与否。research 叶脚本里为构造基准池而用 delist_date，只允许出现在**指定的基准池函数内**：按「路径 + 函数名」列白名单，每条注明依据「主 Agent 02:44 裁定（基准池按 delist_date 截断）」。同一文件中该函数以外的任何命中仍判 VIOLATION。
4. Eng 以 r3.1 交付：测试文件和 sd1_pit_static_check.py 的 sha 会变，报新 sha 和 r3→r3.1 diff。只做 py_compile 和代码阅读，不运行。

### 6.2 P2

- **P2-1** tests/__pycache__/test_sd1_suspend_delist.cpython-313.pyc（01:34:27）仍在（73cb88ac §6 已记，Eng r1 遗留）。请 Eng 在 r3.1 交付前删掉并在回执里列出前后清单；它不会被 PYTHONDONTWRITEBYTECODE=1 的 3.12 运行使用，但会干扰「无 __pycache__」的清理核对。

### 6.3 P3

- **P3-1** runner 只在每个子进程**启动前**复查时间窗和冲突进程；子进程跑到一半进入 16:40 窗口不会被拦。现有「14:00 ET 前开始」的规定已经覆盖；请在回执中写明每个子进程的起止时刻。
- **P3-2** 轮询 VmRSS/VmHWM 只看直接子进程；pytest 再起的子进程（T10 扫描、T11 -O）靠 RUSAGE_CHILDREN 事后补查（它包含已回收的孙进程）。可接受，回执里写明。
- **P3-3** SD1 下 TW/AW 改 float64，权重矩阵内存翻倍（全市场约 2000 日×5500 码×8B ≈ 88MB/张，两张约 176MB）。合成单测无影响；将来跑全市场 SD1 时要计入 1.5GB 预算。
- **P3-4** T3 公式措辞（见 §4），回执订正即可。

## 7. ARCH_SD1_TEST.ok 草稿（r3.1 交付后签；未写入文件）

键与 4975aac8 完全相同，命令不变，仍走 v1 门禁 c7805d9a（本轮不切 v2）。

```
format=quantlab_run_auth_v1
signed_by=arch
signed_et=<签发时 ISO8601 带时区>
scope=selftest
runner_sha256_test_sd1_suspend_delist=<r3.1 测试文件 sha256>
allow_selftest=true
allow_real_data=false
allow_dryrun=false
allow_full=false
allow_smoke=false
allow_diagnostic=false
allow_disclosure_only=false
live=false
promotion=false
out_dir=mkdtemp
expires_et=<签发后约 24h，ISO8601 带时区>
dep_sha256_execution=373fed309f055888e83572d3fbef8f5b5052ebfcb208307962a272bca6fc486c
dep_sha256_execution_sd1=8c7615f7376b4482fe2f011fe08d47b2f2292c28be315659da5c0c5db74b00b1
dep_sha256_tradability=968def30059826fa80846531b28ce514c9ed548d3c924034f3db31e3091b892e
dep_sha256_delist_accounting=222b63aee4c47827a9f459dc3145bf254a3b8c9e9cd872e66578af44ce87062a
dep_sha256_platform_init=bfdfa63cbd7f39d7f0b1eb5a9b91ca00a30bdbd21e31ef3b90d89ac6080e99fc
dep_sha256_ok_runner_pin=c7805d9a78e4f5478fa4c9e3becda48e76453ee0889b4f7027009a676c3e2485
dep_sha256_sd1_pit_static_check=<r3.1 sd1_pit_static_check.py sha256>
（其余 61 个 dep_sha256_quantlab__* 原值照抄 4975aac8，已复核未变）
```

如果 r3.1 让测试 import 新的文件（例如闭包清单 paper_import_closure.json 或新增扫描配置），这些文件也必须加进 TEST_DEPS 并钉 sha。

## 8. ok_runner_pin_v2 r3（b7d8ea3f）

- **P2-V1 已修**：所有列出的 .ok 先走 v1 语义（parse_ok_v1、live/promotion=false、请求的 mode 不得为 false）；严格检查只作用于严格集（指定的 primary_ok，未指定时为全部钉住本脚本的 .ok），且严格重解析结果必须与 v1 解析相同。其他 runner 的 .ok 不会因为 v2 规则被误拒。
- **P2-V2 已修**：allow_real_data 必须写 false 只在 selftest scope 强制。
- **P3-8 已修**：严格集内请求的 mode 必须恰好是 `true`；任何重复键都拒（v1 解析只拒值不同的重复，严格重解析再拒全部重复）；scope 必填。
- 剩余说明（P3，不阻断）：指定 primary_ok 时，其他同样钉住本脚本的 .ok 只走 v1 检查（依赖 sha 仍在每份钉住的 .ok 里核）。这是有意设计，写进 v2 docstring 即可。
- **结论：批准按 runner 逐个采用**，每个切换的 runner 单独送审并在其 .ok 里加 gate_ok_runner_pin_sha256；**不得原地替换 v1 c7805d9a**（纸面闭包和现有 runner 继续用 v1）。SD1 单测本轮不切。

## 9. 给 Eng 的顺序

1. r3.1：按 §6.1 改测试 T10 和 sd1_pit_static_check.py；删 tests/__pycache__ 下的遗留 pyc；只做 py_compile（cfile 写 /tmp）。
2. 报新 sha、r3→r3.1 diff、新 SD1_SHAS。Arch 静态复核后签 TEST.ok（§7）。
3. 按 TEST.ok 只跑一次单测，交回执（RSS 每 0.1 秒采样 + VmHWM）。
4. Arch 审过回执后签 EXEC.ok（runner sha8 结尾的 out_tag），再跑 SD0 对拍。
