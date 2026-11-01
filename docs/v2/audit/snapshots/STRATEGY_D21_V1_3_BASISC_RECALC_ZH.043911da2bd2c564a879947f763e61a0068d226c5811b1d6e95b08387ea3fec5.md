# D21：v1.3 按口径 C 重算（送审稿 r3，只 py_compile，未运行）

- r1 起草：QuantLab Strategy，2026-10-18 02:18 ET（git 提交 b975819e 时间）。r1 正文快照：docs/v2/audit/snapshots/STRATEGY_D21_V1_3_BASISC_RECALC_ZH.8b7a29f0775de8e325a3105001d309cf40624221eb60b576d409536e75382753.md。
- **r3 修改：2026-10-18 02:44 EDT（`date` 实测）**。依据：Arch 复审 ARCH_V1_4_RUNNER_REVIEW_R2_ZH.md f9edf4a3（§7 裁定 6、P2-2、P2-3、P3-2、P3-4、P3-7）；主 Agent CLARIFY-2（02:30 ET 改向消息）。live=false，promotion=false。
- **CLARIFY-2 引用说明**：`rg -l CLARIFY-2 docs/v2` 在 02:30、02:41 ET 都没有结果，文件尚未落盘，所以**写不出它的 sha**。代码里统一引用 R 的 `CLARIFY2_SHA256` 常量（当前为空串 → D21 和 v1.4 都拒绝启动，直到文件落盘、常量填好、新 sha 经 Arch 重审）。
- **只写了代码，没有执行。** 只跑过 `python -m py_compile`（.venv_opt、qlvenv 都通过）。没有建 .ok，没有改 b6238254，没碰任何 v1.3 / v1.4 产物，没碰 research/ai_debate_memory_runner.py。
- 文件：`research/optimizer_core_v1_3_basisC_recalc_d21.py` = **86c6f7bb5a04030a7970e59fa5074fd03c1ef8c2f1285153dc57e87509f2bc3c**（下文 D@86c6f7bb；r1 = 0a7d2183，快照在 research/_runner_archive/）。
- combined_sha256（D21 + R + V + C，公式同前）= **497c151b2a281462fa60ae242f74659be53313c1ea92c7ccb0856987aad256d0**（R = 94643e27…；R 再改，此值随之变）。

## 1. 做什么（D@86c6f7bb 行号）
1. **主结果 = §8 基线（CLARIFY-2）**：`replay(decide="A")`（155–213）按 b6238254 第 312–366 行重放 v1.3 决策：prepare_day → v1.3 ① 一手成本剔除 → `V.solve_v11`（POOL_STD=IND_POOL=True）→ 每袖 `V.lot_round_greedy` → v1.3 采用规则（口径 A 的 lot_flag，两袖耦合）。持仓与 w0 链条沿用口径 A 的决策；**只**把可行性标签按口径 C 重判（v1.4 的 `book_exposures` + `hard_eval(…,"C")`，TOL=1e-6，当天 v1.3 的 slack，含两袖耦合）。
2. **§8**：主结果用与 v1.4 **同一份** `R.post_run_disclosures`（CLARIFY-1 两袖同日 + CLARIFY-2：无数据日留分母、记不可证可行、绝对 <24 升级、有效日 80% 只作对照、judgeable 恒为 true）。另用复现的口径 A 标签算一份 A 对 A 对照。
3. **第二披露列（CLARIFY-2）**：`replay(decide="C")`，唯一区别是第 203 行：采用条件改为「两袖口径 C 硬约束都过」，否则沿用。w0 链条因此改变，是反事实路径，**不是 v1.3**。输出 `d21_status_Cdecision_disclosure_only.csv`、`d21_counts_Cdecision_disclosure_only.json`、summary 的 `disclosure_only_C_decision_path`，**只披露，不参与 §8 或任何判定**。
4. **复现核对 + 可引用标准（写进代码，CLARIFY-2 / Arch 裁定 6）**：`repro_check`（242–285）
   - 标签：复现的口径 A 标签与 `core_v1_3_disclosure.csv` 逐行比对（键集合取并集，两边缺行都算不符）；
   - 权重：每个调仓日持仓权重最大绝对差 ≤ 1e-6（`CITE_WEIGHT_TOL`，58）；
   - 持仓集合一致，手数一致（`_lots` 231–239：用当天 PIT 收盘价和整手规则，把两边权重都换算成手数再比；无价格的名字（如 510300 压舱）只比权重）；
   - **全部满足 → `citable=VALID`；任一不满足 → `citable=VALID_WITH_DISCLOSURE`，并写明「复现与 canonical v1.3 不一致：解释前不得引用为「v1.3 口径 C」对照（须 Arch 逐项解释）」**（278–285）；
   - 核对本身只披露、不作废（canonical 是在未钉确定性环境下跑的）。
- 运行时间约为 v1.3 的两倍（两次重放）。

## 2. 门禁（与 v1.4 同规则，r3 加严）
- .ok：`output/strategy_optimizer/core_x2/ARCH_RUN_AUTH_D21_v1_3C.ok`（Arch 写；Strategy 不建），`--auth-sha256` 必填且等于其 sha。
- 解析：`R.parse_ok_strict` + `R.check_auth_times`（D 73–90）：键白名单、畸形行/未知键/重复键/BOM/CR 拒绝、expires_et 必填且不过期、signed_et 不得在未来、signed_by 恰为 arch。
- 启动检查（95–131）：3 份文档 sha（lotfix d921dd3f、**停跑规则 41f29825（P3-7 补钉）**、CLARIFY-1 d075a2a6）、CLARIFY-2（`R.check_clarify2`，117）、掩码、输入路径、确定性环境、λ、全部 sha 全长比对、解释器（`R.check_interpreter`：pyvenv.cfg 必须存在、sys.prefix、PYTHON* 环境变量、包路径）、out_dir 常量且为空、锁不存在。
- 结束前复核（317–318）：`R.end_of_run_recheck`（输入 + 11 文件闭包 + 4 个 v1.3 权重 + 掩码 + 文档 + CLARIFY-2 + 加载模块）和 v1.3 disclosure，变了就作废。
- 输出用排他写（P3-2）：summary（write_x_atomic）、VOID.md、计数 json（write_x）。锁 `core_x2/.d21_v1_3_basisC_run.lock` 代码不删；Arch 归档到 `core_x2/_archive_locks/<ET 时间>/`，VOID 后输出目录一并归档。

### .ok 键白名单模板（ARCH_RUN_AUTH_D21_v1_3C.ok；白名单 = 必填，共 39 个键）
```
format=quantlab_run_auth_v1
version=d21_v1_3_basisC
signed_by=arch
signed_et=<ISO8601 带时区，不得在未来>
expires_et=<ISO8601 带时区，晚于 signed_et>
allow_full=true
allow_smoke=false
live=false
promotion=false
python_exe=/workspace/QuantLab/.venv_opt/bin/python
out_dir=output/strategy_optimizer/core_x2/v1_3_basisC_d21
runner_sha256=86c6f7bb5a04030a7970e59fa5074fd03c1ef8c2f1285153dc57e87509f2bc3c
combined_sha256=497c151b2a281462fa60ae242f74659be53313c1ea92c7ccb0856987aad256d0
lotfix_sha256=d921dd3f0f698deb822a59e40aa643f1efc7f43f6c36eaed30c7a672dbdf9425
stoprule_sha256=41f29825c85a66c889474460605b45a19f5fa475ae46570f299416535cb3559b
clarify_sha256=d075a2a68f2d5c42c750669cdff2dd51f93794e11ea907f08ffc29c39c724d85
clarify2_sha256=<CLARIFY-2 文件 sha；文件尚不存在>
<v1.4 的 7 个数据键、10 个 nt_* 闭包键、4 个 v13_w_* 键：与 STRATEGY_V1_4_RUNNER_CHANGES_ZH.md §r3.2 逐行相同>
v13_disclosure_sha256=9586e5f3ecde6580c5b232a4823fe167814f49a697c823acaea46be688bc2c1b
```

## 3. 启动命令（只在 CLARIFY-2 钉进代码、Leo 定 Core 继续之后；D21 先于 v1.4、串行；D21 回执经 Arch 审过再签 v1.4 .ok；CLARIFY-1 §4）
```
cd /workspace/QuantLab && PYTHONHASHSEED=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 nohup /workspace/QuantLab/.venv_opt/bin/python research/optimizer_core_v1_3_basisC_recalc_d21.py --auth-sha256 <ARCH_RUN_AUTH_D21_v1_3C.ok 的 sha> > output/strategy_optimizer/core_x2/d21_run.log 2>&1 &
```
PYTHONPATH/PYTHONHOME/PYTHONSTARTUP/PYTHONUSERBASE 不得设置。

## 4. 待裁定 / 知悉
1. CLARIFY-2 文件不存在（见开头）。主结果口径、第二披露列、可引用标准都按主 Agent 02:30 ET 改向消息实现；文件落盘后请 Arch 核对代码与原文一致。
2. 「手数一致」我用当天 PIT 收盘价从权重反推手数来比，因为 canonical 权重文件不含手数。请确认这个做法可以接受，或者指定以 v1.3 的 ckpt pkl 为准。
3. 没有给 D21 写单测；需要的话按自测规范另交。
4. import 闭包同 v1.4（11 个文件钉 sha）；R 每改一次，D21 的 combined 和 .ok 都要重签。
