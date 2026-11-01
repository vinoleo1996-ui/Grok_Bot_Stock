# Arch 复审 r2：Core v1.4 runner 修订、合成单测、D21（静态审查）

- 审查：QuantLab Arch，2026-10-18 02:18–02:27 ET（America/New_York）。**纯静态**：读代码、复算 sha、git diff 对快照、AST 静态解析 import 闭包；**没有运行** runner、等价性脚本、D21 或合成单测，**没有 import 任何项目模块**。唯一执行的是一段与项目代码无关的审计钩子探针（只用 numpy/pandas/pyarrow，在 /tmp 自建临时文件，已删）。live=false，promotion=false。
- 上轮：`docs/v2/ARCH_V1_4_RUNNER_REVIEW_ZH.md` db7817087deca6d6d2a6af2e5310e0ce3b8cc167f1d52ad92600b9092513d7b1（P1=3）。
- **结论：有条件通过（P0=0，P1=0，P2=4，P3=9）。** 上轮 P1-1/P1-2/P1-3 全部关闭。**已签**合成单测 .ok（见 §6）。**v1.4 与 D21 的运行 .ok 不签**：按 CLARIFY-1 §4 等 Leo 对 Core 去留拍板；另须先关 P2-1（§8 无数据日口径与冻结原文不符）与 P2-2（nontextbook 闭包钉 sha）。

## 1. sha 与快照（全部实测）
| 文件 | 期望 | 实测 |
|---|---|---|
| R `research/optimizer_core_x2_run_v1_4.py` | 3df05b4b…8b10 | ✅ |
| combined（R + b500c21b… + 875daca9…） | 9e6d00c7…c335 | ✅（按 R 第 157–160 行公式，与改动对照一致） |
| E `research/v1_4_snapshot_equiv_check.py` | 13809851…bf7a | ✅ |
| 改动对照 `docs/v2/STRATEGY_V1_4_RUNNER_CHANGES_ZH.md` | e5b6d02d…497b | ✅ |
| T `research/tests_v1_4/test_v14_synthetic.py` | 7176f974…95d3 | ✅ |
| D21 `research/optimizer_core_v1_3_basisC_recalc_d21.py` | 0a7d2183…2ef8e | ✅（ddd23ed4 未改） |
| D21 文档 | **8b7a29f0775de8e325a3105001d309cf40624221eb60b576d409536e75382753**（取代 744ede3d） | ✅；与快照 744ede3d 的 diff **只有第 3 行起草时间**（「约 02:35 ET」→「02:18 ET（b975819e 提交时间）…」），正文未变 |
| 快照 R r1 / E r1 / 改动对照 r1 / D21 文档 r1 | db8bdb8e / 3d2e0533 / d9767ef0 / 744ede3d | ✅ 均只读（-r--r--r--）；R、E 快照与 git 6ca0cdd 的 blob 逐位一致；MANIFEST.md 已登记 |
| 冻结件 LOTFIX d921dd3f / CLARIFY-1 d075a2a6 / 冻结记录 0d47c52f | — | ✅ 未改 |
| 提交 | 246aa99a、b975819e、ddd23ed4（未 push） | ✅ |
| 现有产物 | `core_x2/v1_4*`、v1.4 锁文件 | 不存在 ✅（无 v1.4 运行痕迹） |

- 注意：`research/optimizer_core_v1_1.py`、`research/optimizer_lambda_calib_sealed.py`、`scripts_eng/ok_runner_pin.py` **不在 git（untracked）**，只靠 sha 钉住（P3-1）。

## 2. diff 审读（R、E 对 r1 快照）
- R：+331/−55 行，逐条对应改动对照 r2.3，未发现表外改动。求解、整手、修复逻辑除 P3-1/P3-2（ε 回退计数、上界容差、S5 改为 m==0）外未变。
- E：只改门禁、锁、解释器、输入复核和文案；子进程用 `.ok` 的 python_exe，env = os.environ ∪ DETERMINISM_ENV。

## 3. 上轮意见逐条核对
| 项 | 结论 |
|---|---|
| P1-1 live/promotion | ✅ 必填、恰好 `false`（R 189–191），enforce 再查（206–207） |
| P1-2 输入与依赖钉 sha | ✅ 7 键全长比对，preflight 两次、写 summary 前再算一次，变了 → VOID（1394–1396）；E 两次子运行后复核 → FAIL。**新缺口**：nontextbook 的上游闭包没钉（→ P2-2）；HI_LIQ 掩码只在 preflight 查一次，结束前没复核（P3-4） |
| P1-3 前置执行通道 | ✅ 合成单测 T（§5），已签 selftest .ok |
| P2-1 / E-1 §8 耦合 | ✅ 两袖同日、24/29、分袖只披露、不完整不判定，实现与 CLARIFY-1 §2–§3 一致。**但无数据日处理偏离冻结原文**（→ 本轮 P2-1） |
| P2-2 解释器 | ✅（加严见裁定 2） |
| P2-3 / D18 顺序与环境 | ✅ full 前查 equiv_report（verdict、combined、auth、inputs_after、python_exe、env）+ snap_on/summary.json |
| P2-4 锁 | ✅ O_EXCL、0444、不删；4 把锁按模式分开 |
| P2-5 FAIL 用尽 .ok | ✅ |
| P3-1～P3-7 | ✅（P3-5 仍是采样，两次采样之间的峰值看不到，可接受） |

## 4. runner 门禁 / 输出（本轮新查）
- 已核：live/promotion、全部 sha 键 64 hex、重复键拒、BOM 与行内注释会失配而拒（安全失败）、out_dir/equiv_root 等于代码常量、锁先于 mkdir（1381–1383），输出目录非空即拒，RSS 每次求解后和每日结束采样、超 1536MB raise → VOID。
- **P2-3 `.ok` 不查 expires_et、不拒未知键。** R 与 D21 的 parse 都把不认识的键静默忽略，也不要求 `expires_et`；团队 .ok 格式要求 expires_et。要求：AUTH_REQUIRED 加 `expires_et`（带时区 ISO8601，已过期即拒，signed_et 不得在未来）；改为**键白名单**，出现未知键即拒；不匹配 `^[a-z0-9_]+=` 的非注释行也拒（现为静默跳过）。
- P3-2 输出目录内文件用普通 `open('w')`/ParquetWriter 写；有锁 + 空目录检查兜底，建议关键文件（summary、manifest、VOID.md）改 `open('x')`。

## 5. 合成单测 T（7176f974）
**门禁顺序 ✅**：第 34–36 行先 `enforce(modes=["selftest"], deps=4 项)`，第 75 行自查，第 97 行装钩子，第 100–105 行才 import numpy/pandas/pytest 和 R。只有门禁模块 ok_runner_pin 本身在门禁之前被 import（不可避免；其 sha 由 dep_sha256_ok_runner_pin 与 gate_ok_runner_pin_sha256 双钉）。无 conftest.py、pytest.ini、pyproject.toml。

**自查 ✅**：BOM、CR、format、signed_by、scope=selftest、allow_selftest=true、8 个已知 allow_* 显式 false 且**任何**其他 allow_* 必须 false、live/promotion、signed_et/expires_et 带时区且未过期、out_dir 仅 mkdtemp 或 /tmp/<tag> 且不在仓库内。

**import 闭包 ✅**：AST 静态解析（不 import）：R 的顶层闭包 = {R, V b500c21b, C 875daca9}；C 只在 `load_sw_map`/`_sw_df` 里懒 import nontextbook，而 T 把 load_sw_map 换成了 raise，`_sw_df` 只被 load_sw_map 调用 → 单测不会加载 nontextbook 及其上游。T 的 4 个 dep 恰好覆盖实际加载的项目模块。

**审计钩子实测（探针，/tmp 合成文件）：**
| 读写方式 | 是否触发 Python `open` 审计事件 |
|---|---|
| 内置 open、pathlib.read_bytes、os.open、np.load、pd.read_parquet、pd.read_csv | 触发 ✅ |
| **pq.read_table(str)、pa.memory_map、pq.ParquetWriter(str)** | **不触发**（Arrow C++ 直接开文件） |

- 结论：钩子对 Arrow 原生读写**无效**。T 实际依靠的是对 C.prepare_day / load_daily_basic_window / load_pool / load_sw_map / month_ends、R._open_days、R.load_v13_eq100 的替换。逐个核对 R/C/V 中所有文件 IO 点（R 143/772/784/876/1123/1142、C 105/117/123/175/597/633/666）：被测函数路径上**没有**未被替换的 Arrow 读；Writers 只写 OUT（/tmp）。因此**当前字节下不存在真实数据读取路径**，不构成 P1。
- **P2-4（T）钩子覆盖不全**：①给 `pyarrow.parquet.read_table / ParquetFile / read_schema / ParquetWriter`、`pyarrow.memory_map / OSFile`、`pyarrow.dataset.dataset` 加路径检查包装（禁 data/、output/，禁写仓库）；②路径用 `os.path.realpath`（现用 abspath，经符号链接可绕过）；③另拦 `os.mkdir / os.rename / os.remove / shutil.*` 审计事件对仓库的写。下一版 T 修，不阻断本次 selftest。
- 门禁反例测试：所有 `enforce_run_auth_v14` 反例都在 `check_inputs` 之前 SystemExit，不会碰真实数据 ✅。`check_out_dir` 两个反例在任何文件系统访问前就拒 ✅。锁测试写在 OUT ✅。
- P3-3：建议命令加 `--noconftest` 与 `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`（防止日后新增 conftest 或第三方插件先于门禁执行）。

## 6. 已签：合成单测 .ok
- 路径：`output/strategy_optimizer/core_x2/ARCH_RUN_AUTH_SELFTEST_v1_4.ok`
- sha256：**33ef1df908249913f9fa76ef7de09c9a0d4384a8daf26eb3e27dfb15318469d8**（0444，O_EXCL 新建；UTF-8 无 BOM、LF、无行内注释）
- 内容要点：scope=selftest；runner_sha256_test_v14_synthetic=7176f974…；dep runner_v1_4 3df05b4b / core_v1_1 b500c21b / calib_sealed 875daca9 / ok_runner_pin c7805d9a；gate_ok_runner_pin_sha256=c7805d9a（参考，v1 门禁不读）；allow_selftest=true，其余 allow_*（real_data、dryrun、full、execute、smoke、diagnostic、disclosure_only、equiv_check、mocktest）全 false；live=false；promotion=false；out_dir=mkdtemp；run_niceness=10；run_serial=true；signed_et=2026-10-18T02:24:43-04:00；expires_et=2026-10-19T02:24:43-04:00。
- 运行命令（qlvenv；串行，不与研究进程并发）：
```
cd /workspace/QuantLab && PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python -m pytest research/tests_v1_4/test_v14_synthetic.py -q -p no:cacheprovider --noconftest
```
- 回执须含：命令行、.ok 路径与 sha、T 与 4 个 dep 全长 sha、通过/失败数、`peak_rss_mb.txt` 值（box 无 /usr/bin/time）、`rm -rf /tmp/v14_selftest_*` 之后的 ls、`ls -a research/tests_v1_4/ .pytest_cache` 证明无缓存。**测试通过不构成任何证据**，不改变 v1.4 运行 .ok 的前提。

## 7. 对 Strategy 8 个问题的裁定
1. **nontextbook 上游钉 sha：要钉，钉整个顶层闭包（P2-2）。** AST 静态闭包共 11 个文件：nontextbook 8a56d136、quantlab/__init__ e3b0c442（空文件）、quantlab/intel/__init__ 750fa585、asof_window 593e3588、debate_ledger 8e388df9、embeddings d5c52c0e、messages 9354a34c、quantlab/promotion_gate 514564fd、ai_debate_memory_runner e1736d80、g1g5_wiring ff510148、g1g5_expand_g6 b2d26c0d。实现：新增 `.ok` 键 `dep_nontextbook_closure_sha256`（按 combined 公式对上述 11 个路径排序拼接），runner 启动时现算比对，写 summary；或逐个键，二选一。执行路径：v1.4 只用 `_load_sw_members`、`sw_code_on`，后者调用 ai_debate_memory_runner 的 `to_panel_id`，所以该文件**在执行路径上**。
   - **脏文件**：`research/ai_debate_memory_runner.py` 未提交的 +21 行只新增函数 `_load_benchmark_closes_hfq()`（读 etf_daily_adj 的 close_hfq），没有改动已有函数；v1.4/D21 路径不调用它。归属：**QuantLab AI**，见 `docs/v2/AI_SELFCHECK_ADJ_UNIFY_RECEIPT_ZH.md`（2026-10-13），十余个 g1g5_*_weights 脚本在用。当前字节 e1736d80 **就是** Eng 纸面闭包 `docs/v2/eng_sd1/paper_import_closure.json` 里登记的 sha，所以**不能回退**（回退会破坏纸面闭包）。要求：签 v1.4/D21 .ok 之前，由 AI **原样提交**（字节不变，sha 仍为 e1736d80），Strategy 不得修改。同理 `research/g1g5_x2_panel_stitch.py`（043fa68d，脏 +17/−1，等于纸面闭包登记值）只被 nontextbook 在函数内懒加载，v1.4 路径不到，不钉，但应由 AI 一并提交。
2. **解释器 sys.prefix 检查：采纳，加严。** realpath 无法区分 venv 和 /usr/bin/python3，加 prefix 检查是对的。要求：python_exe 在 venv 时 `pyvenv.cfg` **必须存在**（现在是「存在才查」，删掉 cfg 会静默跳过）；另外 `PYTHONPATH`/`PYTHONHOME`/`PYTHONSTARTUP`/`PYTHONUSERBASE` 任一非空即拒；numpy、pandas、pyarrow、cvxpy 的 `__file__` 必须在 sys.prefix 之下（P3-5）。
3. **§8 无数据日：按冻结原文，剔除（P2-1）。** LOTFIX v1.4 §8 第 268 行冻结原文写的是「在 v1.4 的 X2 正式运行中（29 个调仓日，**排除无数据日**）」，r1 的剔除是对的，r2 改为「留在分母、记为不严格」**偏离冻结原文**，须改回。CLARIFY-1 只改了「严格可行」的计数口径（两袖同日），没有改无数据日的处理。冻结文本没有说清的是：一旦 X2 真有无数据日，门槛应按「<80% × 剩余天数」还是仍按「<24 天」，以及 CLARIFY-1「分母 29」的完整性条件怎么适用。**这一点上报主 Agent 裁定**；在裁定之前，代码要求：剔除无数据日，同时报两种算法；n_no_data_days>0 时 `judgeable=false` 且标 `needs_main_agent_ruling`，不得自行判定。「100万 任一配置」按档计（每档一个配置、两袖同日），与 CLARIFY-1 §3「该配置两袖在同一天都严格」一致，采纳。
4. **4 把锁 + D21 锁，代码不删，Arch 归档后才能重跑：采纳。** 归档做法：Arch 把锁移到 `core_x2/_archive_locks/<ET 时间>/`，记录 sha 与内容；任何 VOID/FAIL 之后，同时归档对应的输出目录。
5. **写 summary 前复算输入，变了 VOID 并用掉 .ok：采纳。** 补：HI_LIQ 掩码（C.MASK_PATH）也要在结束时复核（P3-4）。签 v1.4/D21 .ok 前，Arch 会和 Data 协调：冻结 daily_basic、trade_cal、sw_l1 三个文件（calib 三个 json 在 output/strategy_optimizer/calib 下），运行窗口内 Data 不得重写这些文件，签发前当场复算 7 个 sha。
6. **D21 路径口径：建议维持「持仓沿口径 A 的决策，只用口径 C 重判标签」，需主 Agent 裁定。** 理由：Beta L6 要的是「v1.3 实际路径在口径 C 下的得分」，作为 v1.4 的同口径对照；「决策也按 C」得到的是另一条反事实路径（w0 链条改变），已经不是 v1.3。可以作为第二列披露，但不得用作 §8 的对照基准。**复现差异**：建议「状态标签与 core_v1_3_disclosure.csv 逐行完全一致（0 不符）」作为 D21 可引用的必要条件；权重最大绝对差 ≤1e-6 且每日持仓集合与手数一致视为一致；超出的话 D21 记 VALID_WITH_DISCLOSURE，**不得引用**为「v1.3 口径 C」的对照，直到 Arch 逐项解释清楚。原因：canonical 是在未钉确定性环境下跑的。复现核对本身仍只披露、不作废，与现码一致。上述可引用标准请主 Agent 确认。
7. **首次运行失败：采纳。** 失败 → 停，交回执（含失败用例和日志），改 R 或 T → 新 sha → Arch 重审 → 新 selftest .ok（现 .ok 钉了 T 和 R 的 sha，字节一变就自动失效）。相同字节重跑须先经 Arch 同意。失败和通过都不构成证据。
8. **pytest 用 qlvenv：采纳。** 命令按 §6（加 `--noconftest`、`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`）。须披露：T 在 py3.12.14、numpy 2.5.3、pyarrow 25.0.1 上跑，正式运行在 .venv_opt（3.13.5、numpy 2.5.4、pyarrow 26.0.0）上跑，T 通过不能说明 .venv_opt 下的行为；cvxpy/clarabel/osqp/scipy 两边相同。

## 8. P 清单
- **P0**：无。**P1**：无。
- **P2-1（R/D21）** §8 无数据日改回「剔除」，按冻结原文；n_no_data>0 时不判定，报主 Agent（裁定 3）。
- **P2-2（R/D21）** nontextbook 顶层闭包 11 个文件钉 sha；AI 原样提交 ai_debate_memory_runner.py（裁定 1）。
- **P2-3（R/D21）** .ok 必须写 expires_et，过期即拒；键白名单；畸形行拒（§4）。
- **P2-4（T）** 审计钩子对 Arrow 原生 IO 无效：加包装、改用 realpath、拦目录与改名事件（§5）。不阻断本次 selftest。
- P3-1 v1_1、calib_sealed、ok_runner_pin 不在 git，请各自的所有者提交。
- P3-2 summary、manifest、VOID 用 `open('x')`。
- P3-3 pytest 命令加 --noconftest、PYTEST_DISABLE_PLUGIN_AUTOLOAD=1。
- P3-4 结束前复核掩码 sha（R、D21）。
- P3-5 解释器加严（裁定 2）。
- P3-6 改动对照 r2 的「起草约 02:05–02:30 ET」晚于提交 246aa99a 的 02:14:15 ET，请改为实际时间（同 D21 文档的更正）。
- P3-7 D21 用 R.post_run_disclosures 里的停跑规则评估，但 PINNED_DOCS 没钉停跑规则 41f29825，请补上。
- P3-8 v1.4 的 load_v13_eq100 读的 v1.3 产物只记录 sha、不钉；按 D21 的做法补钉 4 个权重文件的键。
- P3-9 T 的 `_selftest_selfcheck` 不查 signed_et 是否在未来；v2 门禁启用后改用 v2。

## 9. 需要主 Agent 的事项
1. §8 无数据日（裁定 3）：冻结原文是「排除」；X2 一旦出现无数据日，门槛按「80% × 剩余天数」还是「24 天」？CLARIFY-1 的「分母 29」怎么适用？
2. D21 口径与可引用标准（裁定 6）。
3. 知悉：已签合成单测 .ok 33ef1df9（只放行合成数据，不读真实数据，不写 output/）；v1.4 与 D21 的运行 .ok 仍等 Leo 对 Core 的决定。

## 10. 附：本轮 Arch 实测命令（只读）
sha256sum、git log/show/diff、diff 对快照、ls/stat、AST 静态闭包脚本 /tmp/arch_closure.py（只做 ast.parse，不 import 项目模块）、审计钩子探针（/tmp/arch_hookprobe，已删）、`<qlvenv python> -c` 读包版本、`pytest --help`。
