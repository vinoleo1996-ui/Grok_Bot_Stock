# Arch 审查：Alpha CMC / s8 v1.1 r2（2026-10-18 ET）

- 审查人：QuantLab Arch；审查时间：2026-10-18 03:10–03:30 ET；上一轮：`docs/v2/ARCH_ALPHA_CMC_S8_V1_1_REVIEW_ZH.md`（31b4b8ba）
- 依据：
  - 主 Agent 02:44 裁定（风格项一律 t−1）；
  - 主 Agent 02:59 裁定（P2-3：只允许读 2024-05-31 这一张申万一级成员快照，且只取标签；代码要断言只读了这一张，**也要断言除继承的回看外不读 2024-06 前的行情数据**）；
  - 主 Agent 03:10 补充（β120 和动量约 120 个交易日的窗前**价格**回看继承自旧工具，前提是回看长度、数据源、公式都与旧工具一致，只用于暴露，并在文档中写明继承关系）；
  - 规范 1aa43bdd；ok_runner_pin c7805d9a。
- 审查方式：只读，包括 diff、patch 回放、AST 闭包扫描。py_compile 只编译到 /tmp，编译产物已删除。**没有运行任何项目代码，没有读取任何真实数据。**
- live=false，promotion=false

## 0. 结论
- **结论：不通过（有 1 个 P1），selftest .ok 本轮不签。**
- P1-1：两个脚本都新增了 2024-04-01..2024-05-31 共约 2 个月的窗前**流通市值**读取。两个旧工具都是从 START 开始读。这既不在 03:10 补充的覆盖范围内（补充只涵盖 β 和动量的价格回看），也违反 02:59 裁定「除继承的回看外不读 2024-06 前的行情数据」。交接 L189 写的「v1.1 未新增任何 2024-06 前读取」与代码不符。
- 除 P1-1 外，上一轮的 P2-1、P2-2、P2-3（快照部分）和全部 P3 都已逐项修复并核实。runguard 和闭包清单都合格。测试文件结构合格，隔离有效，stub 不会掩盖被测逻辑。
- 修好 P1-1 后，combo 和 s8 的 sha 都会变，测试文件里钉的 sha 也要跟着重算。所以本轮签 .ok 没有意义，修复版送来后我按 §6 当轮签发。**注意：叶 .ok 的 dep_combo_sha256 不会是 0dbd91ed，要等修复版的 sha。**

## 1. sha 核验（03:12 ET 实算，全部与交审一致）
| 文件 | sha256 |
|---|---|
| research/alpha_combo_marginal_v1_1.py | 0dbd91ed4e59e52f2746ba74390bad1b933c21ea1f2081683989f21b2093395c |
| research/alpha_hiliq_s8_paradigm_v1_1.py | c1b50b931666e43ebae2a02e201378818e537723a4ecd8e3e178ea63dbcef653 |
| research/alpha_v1_1_runguard.py | 5c4d01804f6eaef6401ca426e6602a8f9924cc7f3f74e2e047742259e668d350 |
| docs/v2/ALPHA_V1_1_IMPORT_CLOSURE.manifest | b128dae13bbcca666b864ebc8f1b339f839c658e850d84be7ec15188753c0cf7 |
| docs/v2/ALPHA_S8_CMC_V1_1.patch | e69c384ef26e97d6dcf0062eaf90ff6ea792c3827b9f042a89acded60c9f5808 |
| docs/v2/ALPHA_S8_CMC_V1_1_HANDOFF_ZH.md | f4b05aba3642f2cffaba6025a7f78575b4cd339bd1e697900718e6b78f726efb |
| tests/test_alpha_v1_1_selftest.py | d5fbdbfc901dc1bde9345dac976be2ed24388c25ff6d8acb6c1236133e09a971 |
| 旧 bee23019 / af48bc05、ok_runner_pin c7805d9a、ADG a877cec5、v3 ecaa30d8、common 218b61cf | 均未改 |

在旧文件上回放 patch，得到的 combo、s8、runguard 三个文件的 sha 与上表完全一致。

## 2. P1-1：窗前流通市值读取不在继承范围内（阻断）
| 项 | bee23019 / af48bc05（旧） | v1.1 r2 |
|---|---|---|
| FMC 读取起点 | CMC L95 和 s8 L61 都是 `trade_date >= START`（2024-06-03） | CMC L204 和 s8 L152 都是 `trade_date >= 2024-04-01` |
| mc 的日历 | ev（从 START 起） | CMC L207 和 s8 L157 的 `cal` 从 2024-04-01 起，再 `.ffill().shift(1)` |
| 实际用到的窗前值 | 无 | START 当日的 mc_{t−1} 取 2024-05-31。如果某只股票 5-31 缺值，向前填充会用到 4–5 月更早的值 |
- 03:10 补充只覆盖 β120 和动量的**价格**回看。流通市值不是价格，旧工具也从来没在窗前读过，所以不算继承。
- 02:59 要求代码断言「除继承的回看外不读 2024-06 前的行情数据」，但代码里没有这样的断言。合成测试的 FMC 也是从 2024-04-01 开始造的，所以测不出这个问题。
- 交接 L189 写着「v1.1 未新增任何 2024-06 前读取」，与事实不符。
- **两种修法，选一种：**
  - (a) FMC 只读 2024-05-31 这**一个交易日**及以后，也就是 `trade_date >= SW_PRE_SNAPSHOT`。这一天恰好是 START 的 t−1 值，是 02:44 裁定的直接结果。但它仍然是一个窗前行情日，**要报主 Agent 确认**，并写入披露。
  - (b) 与旧工具一样从 START 读，`cal` 也从 START 起。这样 START 当日 mc 为 NaN，当天在残差化里被跳过（窗口少 1 天）。这种做法**不需要新的裁定**。Arch 推荐 (b)；如果主 Agent 更倾向保留 START 日，就用 (a)。
- **两种修法都要补上：**
  - 代码断言：价格日历的起点与旧工具常量逐字相同（CMC "2023-09-01"，s8 "2023-06-01"），FMC 实际读到的最早 trade_date ≥ START（选 b）或 = 2024-05-31（选 a）；
  - 测试：包装 read_parquet，记录 filters，断言 FMC 的下界；合成 FMC 改为从窗前更早的日期开始造，以确认确实没有读到；
  - 交接 L64、L189 和两个 docstring 都改成如实表述。

## 3. 03:10 补充的逐条核对（价格回看）
| 条件 | CMC（bee23019 L82/88/90 对 v1.1 L191 起） | s8（af48bc05 L36/52–53 对 v1.1 L124/132–135） | 结论 |
|---|---|---|---|
| 数据源相同 | ADG.bench（510300 close_hfq）和 ADG._close，相同 | 相同 | ✔ |
| 读取范围相同 | days 从 2023-09-01 到 END，逐字相同 | 2023-06-01..2026-11-30，逐字相同 | ✔ |
| 公式相同 | rolling(120, min_periods=60) 的 cov/var 相同，只多了 `.shift(1)` | β 同左；mom 从 `C.shift(20)/C.shift(120)` 平移为 `C.shift(21)/C.shift(121)` | ✔，只有裁定要求的平移 |
| 回看长度 | 窗口长度都是 120。最早触及的价格从 d−120 变为 d−121，**多 1 个交易日**，但仍在相同的已读范围内 | mom 跨度都是 100；最早触及的价格同样多 1 个交易日 | 见 P2-1 |
| 只用于暴露 | 窗前价格只进 β 和 mom。R.reindex(ev) 中 START 当日的收益以 5-31 收盘为基数，这是窗口内第一天的正常日收益，旧工具同样如此 | B 用的 R 也一样；F 截到 END | ✔ |
| 文档写明继承 | 交接 §附 L187–189 写了（但 L189 有误，见 P1-1） | 同 | 修 P1-1 时一并改 |

## 4. 上一轮问题的修复核实
- **P2-1 已修 ✔。**
  - CODE_DEPS 补上了 ai_debate_memory_runner、g1g5_wiring、g1g5_expand_g6、ok_runner_pin、runguard 和 closure_manifest。
  - 闭包清单有 82 条，全部能用 `sha256sum -c` 校验通过。
  - Arch 独立做了一遍 AST 闭包扫描：起点是 combo、s8、runguard、ok_runner_pin，包含函数内 import 和相对 import，结果也是 82 个文件，与清单**集合完全相同**。动态 `__import__` 只有 3 处，导入的都是标准库（json、os、pathlib）。
  - 运行时 `verify_closure` 会核对清单中每个文件的 sha，也会检查已加载的项目模块都在清单里。它在计算结束、写输出之前执行，失败就不写输出（见 P3-2）。
- **P2-2 已修 ✔。** runguard 的 `read_ok_strict` 和 `ok_selfcheck` 检查以下各项：
  - 文件：拒绝任何 BOM 和 CR；值不得为空、不得含空白或 `#`；键名有格式要求；同一个键即使值相同也不得重复；
  - 头部字段：format、signed_by=arch、scope 等于本次模式、live=false、promotion=false；
  - 时间：signed_et 和 expires_et 都必须带时区偏移，且不收 Z 后缀和小数秒；expires 未过期且晚于 signed；signed 不得超前 5 分钟以上；
  - allow_*：8 个已知键都必须显式写出；本次模式对应的那个为 true，其余全部为 false，allow_real_data 按模式处理；
  - out_dir：selftest 只能是 mkdtemp 或 /tmp/<tag>；full 模式必须等于实际输出位置。
  调用顺序是 enforce → runguard（已钉 sha）→ 输出预检 → 看门狗和 RLIMIT → 重 import。写输出前会复查 .ok 未变、未过期。
- **P2-3 快照部分已修 ✔。**
  - `sw_snapshot_dates` 断言 2024-05-31 是日历上 START 之前的最后一个交易日，并且是**唯一**一个早于 START 的快照日；
  - 窗前快照只查 SW 成员表，不用价格或收益；
  - `check_ind_coverage` 遇到池内全为 _UNK 的日子就拒跑；
  - s8 的 X_sig 和 B 集合共用同一个 IND；
  - 交接 L63 披露了与旧版在这 18 天上的差异。
  （窗前行情读取的部分见 P1-1。）
- **P3 全部已修 ✔：**
  - F 截断由 `check_f_truncated` 检查 P 的末日 ≤ END，且 F 最后 H 行全为 NaN，不再是恒真式；
  - `--out` 在门禁后立即预检，写入仍用 "x"；
  - legacy 列：sha 必须与门禁钉值一致；v1.1 输出、universe 不一致、叶文件名不一致、任一档 base 不一致，都拒绝；
  - 看门狗改为每 0.5 秒轮询，上限 1,536,000 KB；
  - SW 月末当日用当日成员、池的说法，表述都改准确了；
  - ok_runner_pin 已列为 dep；
  - 记录 QL_X2_EXTEND_END；
  - 交接 .ok 模板里的行内注释已去掉，grep 无命中；
  - v3 L138 另立单子处理。
- **RLIMIT 的性质 ✔。** `set_rlimit_as` 用的是 `resource.RLIMIT_AS`，限制的是虚拟地址空间，6 GiB 是兜底。虚拟内存总是不小于 RSS，所以两者不冲突。1.5GB 的 RSS 规则由看门狗执行（0.5 秒轮询峰值 → os._exit(3)），两次轮询之间仍可能短暂超限，这一点已披露。兜底能保证的是 RSS 绝不会超过 6 GiB。

## 5. 测试文件审查（tests/test_alpha_v1_1_selftest.py，d5fbdbfc）
- **门禁顺序 ✔。** 先检查 `PYTHONDONTWRITEBYTECODE`，然后 enforce（modes=["selftest"]，钉 7 个 dep），再 runguard 的 `ok_selfcheck("selftest")`，再 mkdtemp（必须在仓库和 output/ 之外，退出时删除），最后才 import numpy、pandas、pytest 和被测模块。没有任何跳过路径。仓库里没有 conftest.py、pytest.ini、pyproject、setup.cfg，也没有 research/__init__.py，所以 pytest 收集阶段不会额外加载项目代码。
- **只用合成数据 ✔。**
  - `pd.read_parquet` 被全局包装，读 mkdtemp 以外的路径会直接 AssertionError；
  - ADG.bench 和 ADG._close 被 monkeypatch，所以 panel_stitch 和 adj_price 不会被 import；
  - SW、to_panel_id、industry_on_date 由内存 stub 提供（`__file__=None`）。
  最后一个用例 `test_only_pinned_project_modules_loaded` 在运行时确认，已加载的项目模块只有 7 个 dep 加测试文件本身。Arch 用静态扫描核对了 ADG、v3、common、combo、s8 的模块顶层 import，与这一结论一致。
- **stub 不掩盖被测逻辑 ✔。** stub 只替换数据访问。`sw_code_on` 和 `industry_on_date` 的 stub 与真实实现的语义一致（in_date ≤ s < out_date）。被测的 t−1 平移、快照日期、覆盖率检查、F 截断、legacy、runguard，都运行的是真实代码。
- **覆盖面 ✔，以下几处没有覆盖：**
  - liq 的 t−1 性质在测试里是平凡成立的（测试没改掩码），实际依赖掩码写入方，上一轮已核；
  - 真实数据的 dtype、真实 to_panel_id 与 FMC 的 instrument_id 格式是否对得上，不在 selftest 范围；
  - **FMC 窗前下界没有测**，见 P1-1。
- **其他：** fork 子进程测看门狗（退出码 3）和 RLIMIT_AS（MemoryError，退出码 7），子进程用 os._exit 退出，不会触发 atexit。9 个坏 .ok 样本都写在 mkdtemp 里，属于规范 §7 所说的「临时 .ok 格式样本」，退出时随目录删除，不违反「只有 Arch 写 .ok」。

## 6. 下一轮 selftest .ok 签发口径（预告；按测试文件、runguard、ok_runner_pin 的实际检查）
```
format=quantlab_run_auth_v1
signed_by=arch
signed_et=<签发时刻，带时区，无小数秒>
scope=selftest
runner_sha256_test_alpha_v1_1_selftest=<修复后测试文件 sha>
dep_sha256_combo_v1_1=<修复后>
dep_sha256_s8_v1_1=<修复后>
dep_sha256_ok_runner_pin=c7805d9a78e4f5478fa4c9e3becda48e76453ee0889b4f7027009a676c3e2485
dep_sha256_runguard=<当时 sha>
dep_sha256_adg=a877cec51dbb96c75a6d071e222caf35f62fd14f101741a03be117e0e6076a97
dep_sha256_selfcheck_v3=ecaa30d8760f7ae5f53c330c128e6702476d01d8d69112b1dbf2fe769b7eaebe
dep_sha256_selfcheck_common=218b61cfbf2bf0b6bb133ef030aa2d7ff20b3eafda9724aa98c9f3b1fa5cb054
dep_sha256_closure_manifest=<修复后清单 sha>
gate_ok_runner_pin_sha256=c7805d9a78e4f5478fa4c9e3becda48e76453ee0889b4f7027009a676c3e2485
allow_selftest=true
allow_real_data=false
allow_dryrun=false
allow_full=false
allow_execute=false
allow_smoke=false
allow_diagnostic=false
allow_disclosure_only=false
live=false
promotion=false
out_dir=mkdtemp
run_niceness=10
run_serial=true
expires_et=<届时定>
```
- runguard 会拒绝 KNOWN_ALLOW 之外任何不为 false 的 allow_* 键。所以不再写 allow_equiv_check 之类的额外键；即使写，也必须为 false。
- 测试文件没有在 deps 里声明 closure_manifest，所以 enforce 不会检查这一行，它只是记录字段。

## 7. P2 / P3
- **P2-1｜「回看长度」的表述要精确（主 Agent 确认）。** 读取范围和窗口长度都与旧工具一致，但 t−1 平移让最早触及的价格多出 1 个交易日（d−121）。建议交接如实写成「读取范围、窗口长度、数据源相同；按 02:44 平移后最早触及点 +1 日，仍在旧读取范围内」，并请主 Agent 确认这在 03:10 补充的覆盖范围内。Arch 认为在：已读数据完全相同，平移是裁定本身要求的。
- **P3-1：** `RLIMIT_AS_KB` 可以被环境变量 `ALPHA_V11_RLIMIT_AS_KB` 改写，设成 0 就关掉了兜底。实际生效值会记在 watchdog 回执里，但 env_snapshot 没有记录这个变量。建议去掉这个环境变量覆盖，或者拒绝 0 并在 env_snapshot 里记录。
- **P3-2：** `verify_closure` 只在计算结束后执行。这意味着如果有没钉住的模块，它会先被执行，然后才被拒（不写输出）。建议在启动时先核对一遍清单中各文件的 sha，尽早失败。
- **P3-3：** RLIMIT_AS 在 pyarrow 和 jemalloc import 之前就设置了，它们会预留大块虚拟内存，可能触发假性 MemoryError。首次全量运行请在回执里记录 VmPeak。
- **P3-4：** s8 的价格读到 2026-11-30，这是继承旧工具的，结果不受影响，因为 F 截到 END、暴露只用到 d−1。
- **P3-5：** 在多线程的 pytest 进程里调用 fork，Python 3.12 及以上会给出 DeprecationWarning；死锁风险低，但请在回执中记录告警。

## 8. 运行合规记录
- **Alpha 执行 `ast.parse` 和装在 /tmp 的 pyflakes：** 只解析源码，不 import 项目代码，**不算运行，不定级，只记录**。补充口径：在 /tmp 安装或使用工具不需要 .ok，前提是工具不 import、不执行项目模块。会 import 项目代码的工具（pytest 收集、mypy 插件、pylint 的推断 import、python -c 等）都算运行，需要先有 .ok。
- **Arch 自身：** 对 4 个文件做 py_compile 时都指定 `cfile` 写到 mkdtemp，完成后整个目录已删除。仓库内没有新增 .pyc，research/__pycache__ 仍是 22 个文件。闭包扫描脚本 /tmp/arch_closure2.py 只做 AST 解析。
