# D21：v1.3 按口径 C 重算（送审稿，只 py_compile，未运行）

- 起草：QuantLab Strategy，2026-10-18 约 02:35 ET。live=false，promotion=false。依据：Arch 审查 db781708 的 D21 / E-3、LOTFIX §8 Beta L6、CLARIFY-1（d075a2a6）§4。
- **只写了代码，没有执行。** 只跑过 `python -m py_compile`（.venv_opt、qlvenv 都通过）。没有建 .ok，没有改 `research/optimizer_core_x2_run.py`（b6238254），没碰任何 v1.3 / v1.4 产物。
- 文件：`research/optimizer_core_v1_3_basisC_recalc_d21.py` = **0a7d21835788fb847c88dee13d0b52fdfe65d6de88fdcce1fccfb8b87fd2ef8e**（下文 D@0a7d2183）。
- combined_sha256 = sha256 of
  `research/optimizer_core_v1_3_basisC_recalc_d21.py=<sha>\nresearch/optimizer_core_x2_run_v1_4.py=<sha>\nresearch/optimizer_core_v1_1.py=<sha>\nresearch/optimizer_lambda_calib_sealed.py=<sha>\n`
  按当前文件 = **6d2113e153a8bcd2ebab589b9c661cfcee6f430a6b14b92cf04f93a6f16af797**（R 用的是 3df05b4b…；R 再改，D21 的 combined 也随之变）。

## 1. 做什么（D@0a7d2183 行号）
1. **重放 v1.3 决策路径**（156–209）：逐个调仓日 prepare_day → v1.3 ① 一手成本剔除（`L·P > c_A·A`）→ `V.solve_v11`（POOL_STD=IND_POOL=True，162）→ 每袖 `V.lot_round_greedy` → v1.3 的采用规则（口径 A 的 lot_flag，任一袖 LOT_HARD_FAIL 两袖同沿用，187）。逻辑逐行对应 b6238254 第 312–366 行；**不 import** v1.3 runner（它在 import 时会建目录）。持仓与 w0 链条沿用 v1.3（口径 A）的决策。
2. **口径 C 重判**（140–148、189–196）：用 v1.4 runner 自己的 `book_exposures` + `hard_eval(…,"C")`，容差与 D15 相同（TOL=1e-6），slack 用 v1.3 当天求解所用的 slack。含两袖耦合：某袖当天「严格 C」⇔ 求解成功、两袖口径 C 硬约束都过、且本袖现金 ≤2%。
3. **§8 按 CLARIFY-1**（211–223、283–286）：把结果拼成 v1.4 disclosure 的列格式，直接调用 `R.post_run_disclosures`，所以 C 对 C 用的是与 v1.4 **同一份** §8 代码（每档 sleeve_A/B_strict_days、both_strict_same_day_days、分母 29、逐日明细、24/29、k=3）。另用复现的口径 A 标签再算一份，作 A 对 A 的对照。
4. **复现核对**（226–249，只披露、不作废）：复现的口径 A 标签对 `core_v1_3_disclosure.csv`，复现的调仓日持仓对 4 个 canonical 权重文件（最大绝对差）。canonical 是 29b38cf8 在 00:20 ET 跑的，当时没钉确定性环境，求解器末位可能有差。

## 2. 门禁（与 v1.4 同规则）
- .ok：`output/strategy_optimizer/core_x2/ARCH_RUN_AUTH_D21_v1_3C.ok`（38 行；Arch 写，Strategy 不建），`--auth-sha256` 必填且等于其 sha。
- 必填键（49–51）：format=quantlab_run_auth_v1、version=d21_v1_3_basisC、signed_by=arch、signed_et、allow_full=true、allow_smoke=false、live=false、promotion=false、python_exe、out_dir、runner_sha256、combined_sha256、lotfix_sha256（d921dd3f…）、clarify_sha256（d075a2a6…）、v1.4 的 7 个输入键（同 v1.4 r2.2 的路径与 sha）、以及 5 个 v1.3 产物键：

| key | 路径 | 当前 sha256 |
|---|---|---|
| v13_disclosure_sha256 | output/strategy_optimizer/core_x2/core_v1_3_disclosure.csv | 9586e5f3ecde6580c5b232a4823fe167814f49a697c823acaea46be688bc2c1b |
| v13_w_eq100_60w_sha256 | output/strategy_optimizer/core_x2/core_equity_100_60w.parquet | a9b7647c138942ab3648c85b9271ded0cde4f17938841d7f1254a742536949c1 |
| v13_w_eq100_100w_sha256 | output/strategy_optimizer/core_x2/core_equity_100_100w.parquet | 6ef9c029a3d892f655e34c2a282678d879eb18b26e7c55616208151c4104d6ec |
| v13_w_eq80_60w_sha256 | output/strategy_optimizer/core_x2/core_equity80_etf20_510300_60w.parquet | eab75fe6756fb46beb257324d30c428ba9c51920ddb1cd63622195fd081a24e4 |
| v13_w_eq80_100w_sha256 | output/strategy_optimizer/core_x2/core_equity80_etf20_510300_100w.parquet | ef89f20810fde244445b3221a75e214cc5c6026735728938dea9fc642457b4c0 |

- 启动检查（99–130）：两份文档 sha、掩码 sha、输入路径一致、DETERMINISM_ENV、λ、全部 sha 全长比对、解释器（`R.check_interpreter`）、out_dir 等于代码常量 `output/strategy_optimizer/core_x2/v1_3_basisC_d21`（36）且为空、锁不存在。
- 锁：`core_x2/.d21_v1_3_basisC_run.lock`（39），O_EXCL，代码不删，Arch 归档。
- 跑完、写 summary 前复算 7 个输入和 5 个 v1.3 产物的 sha，变了 → VOID。统一异常处理：没有 summary.json 就写 VOID.md（252–260、305–310）。RSS 每次求解后和每日结束采样（`R.rss_guard`，1536MB）。
- 产出：d21_status.csv、d21_counts_basisC.json、d21_counts_basisA_repro.json、d21_repro_check.json、summary.json（最后写，含其他产出 sha）、run_runtime.json（不进比对）。

## 3. 启动命令（只在 Leo 定 Core 继续之后；D21 先于 v1.4、串行；D21 回执经 Arch 审过再签 v1.4 .ok）
```
cd /workspace/QuantLab && PYTHONHASHSEED=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 nohup /workspace/QuantLab/.venv_opt/bin/python research/optimizer_core_v1_3_basisC_recalc_d21.py --auth-sha256 <ARCH_RUN_AUTH_D21_v1_3C.ok 的 sha> > output/strategy_optimizer/core_x2/d21_run.log 2>&1 &
```
耗时预计与 v1.3 一次相当（约 7 分钟，单线程可能更长）。

## 4. 待 Arch 裁定
1. **路径口径。** D21 让持仓沿 v1.3（口径 A）的决策走，只把每天的可行性标签按口径 C（含耦合）重判；这与 Beta「v1.3 按口径 C、含两袖耦合复算」的读法一致。另一种是「决策也按 C」（C 判失败就沿用），会改变后续 w0 链条——我没有实现，需要的话请裁定。
2. **复现差异的处理。** 复现核对只披露。若标签或权重与 canonical 不一致，是否影响 D21 结论的可引用性，由 Arch 定。
3. **import 闭包**：同 v1.4 r2.9 第 1 点（nontextbook 的上游模块未钉）。D21 的 combined 含 R，所以 R 每改一次，D21 的 .ok 也要重签。
4. 没有为 D21 写单测；如需要，按自测规范另交。
