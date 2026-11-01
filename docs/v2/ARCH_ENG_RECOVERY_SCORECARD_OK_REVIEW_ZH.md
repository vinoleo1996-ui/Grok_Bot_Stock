# Arch 审查：Eng 恢复核对 / S2-3 diff / 记分卡修订 / κ / .ok 申请（2026-10-18 01:3x ET）

- 审查人：QuantLab Arch（执行器，只读核查）。没有运行任何 runner、优化器、回测、smoke；没有改 execution.py、FROZEN 件和纸面代码。唯一的执行是 import 闭包检查（只 import quantlab.metrics / quantlab.portfolio.trade_calendar / core_feas_defs，峰值 RSS 约 98MB），以及在 /tmp 里对重建件打 patch。
- 被审对象：`_recovery/eng/OK_REQUEST_ENG.md`（12bd81ac…）、`_recovery/eng/RECOVERY_REPORT_ZH.md`（c0ec2bbc…）、`docs/v2/ENG_V1_3_AUDIT_FIX_RECEIPT_ZH.md`（e82cf8ca…）、`docs/v2/eng_s2_3/`（README 20b0be79…）、`core_x2/v1_3_RUN_MANIFEST_ADDENDUM_20261018_ENG.json`（fc58fa08…）、`scripts_eng/ok_runner_pin.py`（b302911b…）。
- **引用主 Agent 01:32 ET 裁定**：纸面轨使用的 `quantlab/platform/execution.py` 必须保持 373fed30、原样不动，直到 10-19 纸面例程跑完；SD1 开发一律放旁路文件。因此不为纸面安全赶任何 .ok。

## 结论
**结论 = 有 P0，本轮不放任何 .ok（3 份全部暂缓）。** Eng 的恢复核对、S2-3 patch、κ 行号、记分卡修订内容核实无误。但有三点挡住发 .ok：
1. execution.py 正被原地修改（P0）；
2. pin 门控只读两份已冻结的 gate .ok，Arch 没有合规的位置写 pin（P1-1）；
3. 记分卡渲染会原地覆盖 manifest 记录的产物（P1-2）。

## 1. execution.py 现状（P0-1）
| 时间 (ET) | sha256 | 大小 | 来源 |
|---|---|---|---|
| 基准（git HEAD blob；/workspace/sd1_orig 副本） | 373fed309f055888e83572d3fbef8f5b5052ebfcb208307962a272bca6fc486c | — | 本次逐位核实：HEAD blob 和 sd1_orig 副本完全一致 |
| 01:29:59 实测 | 9ea22e389ea2996247243dc9aebb101a93474846ee5c3edf17b67bf4fc69065b | 110916 | mtime 01:23:18 |
| 01:33:12 实测 | **9533075eeeec8aae79d32b3ba58056efc4c3ea64f4adc60d6a3d51cea13e0e61** | 111006 | mtime 01:30:31，**还在变** |

- 现行文件 ≠ 373fed30，SD1 代码直接写进了主干文件（与原件相差 333 行，含 `SD1_*` 常量、`engine_version`、`strategy_v1_sd1`、halt/delist 分支）。这违反主 Agent 01:32 裁定。
- 纸面依赖链：`quantlab/portfolio/research_loop.py`（d3ded87e）L538 与 `b4_paper.py`（ffe195e6）L108 → `v2_multisleeve_book`（6adefbeb）→ `quantlab.platform.execution`。另外 `quantlab/platform/__init__.py` L47 无条件 import execution，所以 import 任何 `quantlab.platform.*` 都会带上它。
- 旁路文件情况：`delist_accounting.py`（b56180e2，01:24:29 新建）和 `tradability.py`（18341572，01:25:38；内容是 wb_SD1，git 未跟踪）是新增的旁路文件，原件 373fed30 不 import 它们。允许留着，但只能由旁路的 execution 副本引用。
- `/workspace/sd1_orig/research/` 下 3 个 research 文件（g1g5_fund_resid_alpha、leaf_selfcheck_common、alpha_decay_gate）的现值和副本 sha 一致，没有被改。
- **处置（归 Eng / SD1 执行器，Arch 不改主干）**：
  1. 立即停止原地编辑。
  2. 当前改动另存到旁路文件，例如 `quantlab/platform/execution_sd1.py`，保留现 sha 记录。
  3. 用 `/workspace/sd1_orig/quantlab/platform/execution.py` 把主干还原为 373fed30。
  4. 清掉 `quantlab/platform/__pycache__/execution*.pyc`。
  5. 把 sha 报给 Arch 复核。10-19 纸面例程跑完之前，主干必须保持 373fed30。

## 2. 恢复核对（Eng 第 1 节）
- `_recovery/eng/SHA256SUMS` 共 27 条，逐条复算全部一致；Eng 自己的脚本 sha 也都和申请一致（6b590f5a / 14167702 / 73b27c1e / b302911b / 5d83ecaa / 847806e9）。
- 4 个代码不一致项，逐个 diff 核过：

| runner | manifest sha（= `_recovery/eng/scripts_eng/` 去 pin 版） | 现行 | diff 内容 |
|---|---|---|---|
| core_x2_book_smoke | 6dfb4f11 | 5d83ecaa | 只有 3 行 import / enforce，加 meta 里一个 `runner_pin` 字段 |
| s2_3_exec_layer | 3d4b08e3 | 847806e9 | 只有 sys.path 加脚本目录、2 行 enforce，加 meta `runner_pin` |
| core_c5_rereport | abbc90ac | 73b27c1e | 只有 2 行 enforce |
| core_x2_scorecard | 857624cb | 14167702 | 857624cb → a401107c（备份件）只多 2 行 enforce；a401107c → 14167702 是本轮的审计修复文字（P1-2、P2-1..7），不只是 pin |

  结论：「4 个只差 pin 代码」对前 3 个成立。scorecard 的现行版另外含审计修复，Eng 回执已写明，不算误报。
- manifest `v1_3_RUN_MANIFEST.json` 仍为 8824a87e，未被改动；gate sha f27c7e97 / 11a69392 与现文件一致。
- **Origin**：用 Origin 只读接口核实，`leo-vino/QuantLab` 和 `leo-vino/QuantLab-data` 两个仓库确实存在，Arch 原清单记错，应更正。细节：
  - QuantLab-data 最新 2f4f77a9，2026-10-15 22:36:59 ET，作者 QuantLab Frontend (agiuser)，与 Eng 说法一致。
  - QuantLab main 最新 7197939d，2026-10-15 10:25:33 ET，但作者 / 提交人是 **Leo vino**（合并 PR #2；被合并的 ff5cddc5 是 Cursor Agent 提交），**不是 Frontend**。Eng 的「两者都是 Frontend 推的」只对 QuantLab-data 成立（P3）。
  - 两个仓库都早于今晚，不含今晚产物。
- **本地 git**：HEAD e7b240d（10-18 00:55:09 ET）。`git status --short` 共 1373 行，不止 1 个改动文件。纸面代码 research_loop.py / b4_paper.py / trade_calendar.py 不在 git（`git show HEAD:` 为空），与 Eng 说法一致。

## 3. S2-3 diff（Eng 第 2 节）
- 在 /tmp 用 `patch -o` 把 `s2_3_exec_layer_diff_0048.patch`（653dc8e0）打到 `a_pre0048_RECONSTRUCTED`（059cf43e）上，**得到 3d4b08e3…，逐位一致**。b 文件 = manifest code sha = `_recovery` 去 pin 版。
- 注意这是循环验证：a 是由 b 反做 3 处替换得到的，patch 能逐位还原只证明 a 与 patch 自洽，不能独立证明 00:47:18 ET 的真实状态（Eng 已如实标为重建件）（P2-1）。
- Arch 审过 diff 内容，a→b 只有三类改动：
  1. 新增 `--weights-ok` 参数；`--allow-real` 时要求 weights_ok 文本里列有本权重 sha。
  2. 按 release .ok 校验 3 份文档 sha。若 .ok 缺对应键则静默跳过，偏弱但不影响数字。
  3. meta 加 `weights_ok` / `weights_ok_sha256` 两个字段。

  整手、带、HARD、换手、成本、汇总逻辑都没动。**Arch 判断：这次 diff 不改变 S2-3 数字。** 建议主 Agent 据此裁定是否解除 VOID_PENDING_DIFF。在裁定前保持 VOID；Arch 不自行解除。
- 4 个正式目录都有 `VOID_PENDING_DIFF.md`，sha 都是 5a5577d6…，核实。

## 4. 记分卡修订（Eng 第 3 节）
- 生成器 14167702 核实；未渲染核实：md / md.gen 仍是 5b9250d2，等于 manifest。
- P2-3 的 28/96、18/81 引用 Eng 复核值，本次未独立重算 core_v1_3_disclosure.csv（P3，渲染前可补）。
- P2-6：`v2_multisleeve_book.py`（6adefbeb）L34 `CASH_ETF="sh.511880"`、L459–460 把未投资预算停到 511880、L76 从 `etf_daily_adj.parquet` 读行情，核实。
- P2-7：B、C 列引擎 sha 未记录，属已知缺口，同意披露。

## 5. κ（Eng 第 4 节；按 373fed30 = /workspace/sd1_orig 副本逐行核）
- L28 `STAMP_CUT=2023-08-28`；L308 `commission=0.00025`；L309 `min_commission=5.0`；L310/311 `stamp_before=0.001` / `stamp_after=0.0005`；L312 `slippage=0.0`；L290–302 `sqrt_impact_cost`（L300 `rate=k*sg*sqrt(|tv|/adv)`）；L619–620 `_stamp`；L697–698 COMM/MINC；L764 `px0*(1+side*slippage)`；L778 `comm=max(MINC, notional*COMM)`；L779 只在卖出收印花、基金免。**全部核实。**
- 结论成立：线性部分买 2.5bp、卖 7.5bp，κ≈5bp/单边；510300 是 2.5bp/单边。5 元最低佣金在名义额 5/0.00025 = 2 万元以下生效。
- 补充两项不属线性 κ 的约束（P3）：`strategy_v1` L347 有参与率上限 `participation_cap=0.10`；book 层 `min_trade_value=2000`（v2_multisleeve_book L477）。ExecConfig 默认 `impact_k=0`，但 strategy_v1 打开为 1.0。
- 探针占位 0.0015 偏高（约为 κ 的 3 倍），同意 Eng 的判断；MILP 规格改用 κ=5bp/边，510300 2.5bp。

## 6. ok_runner_pin.py（b302911b）
- `own_sha` 每次运行时用 `Path(script).resolve().read_bytes()` 重算 sha，核实。没有 argv、环境变量或参数开关，**无绕过**，核实。只读，不创建 .ok，核实。没有 pin、或给的 .ok 都不存在，就 SystemExit，核实。
- 可解析的键（写 .ok 必须用这两种）：`runner_sha256_<script_stem>=<hex>`，或 `runner_sha256[<相对 repo 路径或文件名>]=<hex>`。正则是 `[0-9a-fA-F]{8,64}\b`。
- 弱点（P2-2）：
  1. 接受 ≥8 位前缀（`startswith`）。Arch 一律写 64 位全长。
  2. 门控只看 runner sha，不检查 signed_by / allow_full / allow_smoke / live；这些要靠各 runner 自己或 Arch 文本约束。
  3. 不存在的 .ok 会被静默跳过。
  4. **pin 只从各 runner 写死的 .ok 路径读取**：scorecard 读 `ARCH_RESIGN_A_v1_3.ok` 和 `ARCH_S2_3_RELEASE.ok`，c5 和 c_col 读 `ARCH_RESIGN_A_v1_3.ok`。

## 7. import 闭包
| 脚本 | 仓库内闭包（静态 + 实际 import 核对） | 依赖 execution.py？ |
|---|---|---|
| core_x2_scorecard.py 14167702 | ok_runner_pin（b302911b）、quantlab.metrics（a822dfee）；metrics L75 惰性 import quantlab.portfolio.trade_calendar（ef44e7cd，纸面代码，git 未跟踪），会带上 quantlab.portfolio 包（v2_constructor、v2_rebalance、mandate_v2、config、promotion_gate） | **否**（sys.modules 里没有 quantlab.platform） |
| core_c5_rereport.py 73b27c1e | ok_runner_pin、core_feas_defs（1626b22e，= manifest） | **否** |
| c_col_exec_diagnostic.py 6b590f5a | ok_runner_pin、`quantlab.platform.execution`（L27），会带上 quantlab/platform/__init__ 全包 | **是**（P0-1 期间不得运行） |

## 8. .ok 处置
| # | 对象 | 处置 | 理由 |
|---|---|---|---|
| 1 | 记分卡 `--disclosure-only`（14167702） | **暂缓，未写 .ok** | (a) 有 P0-1，按本轮规则「无 P0 才放」。(b) P1-1：门控只从 `ARCH_RESIGN_A_v1_3.ok` / `ARCH_S2_3_RELEASE.ok` 读 pin。这两份是 FROZEN `v1_3_RUN_MANIFEST.json` 钉住的 gate（f27c7e97 / 11a69392），往里追加 pin 行会改变其 sha，破坏 manifest 和恢复标准（必须与原 sha 逐位一致）；记分卡渲染时还会把 GATE_V13 的 sha 前缀印进披露。在别的路径另写 .ok，门控又读不到。(c) P1-2：脚本没有 out_dir，会原地覆盖 `scorecard_three_col.md` / `.md.gen`（manifest 记 5b9250d2）；md 与 md.gen 不一致时还会追加写 `scorecard_notes_manual.md`（manifest 记 b84a705c）。闭包本身不含 execution.py，这一点通过。 |
| 2 | c5 rereport（73b27c1e） | **暂缓，并判为不需要** | 代码 = manifest abbc90ac + 2 行 pin，输入未变，重跑只会用相同内容覆盖 manifest 产物（c5_* 4 份），没有信息增量。确实要重出时，必须带 `--tag`，写到带后缀的新文件。P1-1 的阻碍同样适用。 |
| 3 | C 列诊断（6b590f5a） | **暂缓（按任务要求）** | import execution.py。条件：主干恢复为 373fed30、SD1 交付、SD0 逐位证明之后，在 .ok 里同时钉 execution.py 的 sha（或指定在 SD0 原件上跑）。 |

**Eng 要改什么，Arch 才能放 #1（及 #3）**：
1. 新增专用 .ok 路径 `output/strategy_optimizer/core_x2/ARCH_RUN_AUTH_ENG_AUDITFIX_20261018.ok`，加进 scorecard（和 c_col）的 enforce 列表。不要再用 RESIGN / S2_3_RELEASE 承载 pin。
2. scorecard 加 `--out-tag`（或等价参数），disclosure-only 时写 `scorecard_three_col_auditfix_20261018.md`（含 .gen），不覆盖 manifest 记录的 md / md.gen / notes_manual；或渲染前先把 00:51 版逐位归档，并写进 addendum。前一种更好。
3. 交付新 sha，以及 py_compile 结果。
4. P0-1 先解决（主干 = 373fed30，Arch 复核）。

之后 Arch 出 .ok，草案键如下（门控实际解析的只有第一行）：
`runner_sha256_core_x2_scorecard=<64位新sha>`、`format=quantlab_run_auth_v1`、`signed_by=arch`、`signed_et=…`、`scope=core_x2_scorecard_disclosure_only`、`allow_full=false`、`allow_smoke=false`、`allow_disclosure_only=true`、`out_md=…auditfix_20261018.md`、`dep_sha256_quantlab_metrics=a822dfee88b2f524af61ac1de9fae149885f46c4363e93414897c1c77b4bfb62`、`dep_sha256_trade_calendar=ef44e7cd04911523dbb94c19500393cc0cf423c6728a35826bf0cbb123925eec`、`dep_sha256_ok_runner_pin=b302911bc0ae1058ca549d37d813b2815fb18b2cf7ce66a6f16ae0bf19244263`、`live=false`、`promotion=false`。

## 9. P 清单
- **P0-1** execution.py 原地被改（373fed30 → 9ea22e38 → 9533075e，01:33 ET 仍在变），违反主 Agent 01:32 裁定，纸面 10-19 17:40 ET 例程会用到它。归 Eng / SD1 执行器：停改、移到旁路、还原、报 sha。
- **P1-1** pin 门控只读冻结 gate .ok，Arch 无处合规写 pin → Eng 加专用 .ok 路径。
- **P1-2** 记分卡渲染原地覆盖 manifest 产物 → 加 out-tag，或先归档。
- **P2-1** S2-3 重建件只能做循环验证；diff 已审，不改变数字，是否解除 VOID 待主 Agent 裁定。
- **P2-2** 门控接受 8 位前缀、不校验 allow_* / live、静默跳过缺失 .ok → Arch 一律写全长；建议下一版门控改为只认 64 位。
- **P2-3** 记分卡闭包含未入 git 的 trade_calendar（纸面代码），.ok 里须钉 dep sha。
- **P2-4** DIAG 文档旧内容无法证明是前缀：更正注插在第 3 行（不是追加）；删掉该行或其前后空行后的 sha 都不等于 cf953ada，原版没有保存。
- **P3** Origin 的 QuantLab main 作者是 Leo vino，不是 Frontend；κ 还应补参与率上限 10% 和 min_trade_value 2000；28/96、18/81 渲染前由 Arch 补独立复算。

live=false · promotion=false · 未执行任何 runner · 未写任何 .ok。

## 补记（Arch 01:36 ET）：P0-1 状态更新
- 01:36 ET 复测：主干 `quantlab/platform/execution.py` = **373fed309f055888e83572d3fbef8f5b5052ebfcb208307962a272bca6fc486c**（90033 B，mtime 01:33:21），已还原为基准，符合主 Agent 01:32 裁定。上面 01:33:12 的 9533075e 读数比还原早 9 秒。
- SD1 已移到旁路：`quantlab/platform/execution_sd1.py`（37c5b228…，01:33:48）、`wb_sd1_books.py`（01:34:12）、/workspace/sd1_work/execution_sd1_patched.py。
- P0-1 降级为「已处置、持续监控」：10-19 17:40 ET 纸面例程开跑前，Arch 要再核一次主干 = 373fed30。另须确认 quantlab/platform/__init__.py（bfdfa63c = HEAD）没有改为 import 旁路文件。
- .ok 处置不变：#1、#2 仍被 P1-1 / P1-2 挡住，#3 仍等 SD1 交付和 SD0 证明。本文前面的 sha bbdaf52e 指本补记之前的版本。

---
## 附记 B（2026-10-18 01:38 ET，主 Agent 01:37 裁定）
1. P0 的处置主 Agent 认可。10-19 纸面例程开跑前，Arch 复核 execution.py 是否等于 373fed30，范围包括 platform/__init__.py 的 import 链；不符即阻断纸面，并 priority 报主 Agent。已设一次性核对，10-19 约 17:00 ET。这次主干原地改写记为 Eng 运维违规一次，不涉及数字。
2. S2-3 解除 VOID_PENDING_DIFF，状态改为 VALID_WITH_DISCLOSURE，披露口径同 P2-1：实际运行版 3d4b08e3 精确找回；基线为重建件，patch 复现是循环验证；diff 只涉及输入守卫和 meta，数字不受影响。结论只作描述性，全部未过 0.30。4 个运行目录已各加 STATUS_VALID_WITH_DISCLOSURE.md，原 VOID 文件保留。
3. 3 份 .ok 暂缓获认可。记分卡脚本必须改为写新路径（文件名带 sha 后缀），不得覆盖冻结产物；改好后再签。

---
## 附记 C（2026-10-18 01:45 ET）：Eng 申请 r2 复审，结论是暂缓，不写 .ok
- 被审对象：`_recovery/eng/OK_REQUEST_ENG.md` r2，sha 098d8c7589c20a77caf29949f4849731c4042410eb5a90d5532c25c4ace96dea，已复算一致。
- 方式：只做静态审查，没有运行记分卡和复算脚本。唯一的执行是对 `/tmp/arch_auditfix_draft/` 里的 .ok **草案**调用门控自带的 `parse_ok` / `enforce`：只算 sha、不运行 runner，峰值 RSS 16MB，没有加载 quantlab.platform。
- **结论：有 1 条 P1（sha 后缀没有强制），而且不能靠 .ok 键解决，所以本轮不写 `ARCH_RUN_AUTH_ENG_AUDITFIX_20261018.ok`。** 其余 5 项改动核实通过。

### C1. sha 复核（全部一致）
| 对象 | sha256 |
|---|---|
| scripts_eng/core_x2_scorecard.py | a85444eea3686c4933a584a6fa71f178d0d216032777588d6a6608e06c7cd5de |
| scripts_eng/overcap_recount_v1_3.py | 4dd66271f5bd38853568cf653477e10bc0518a3f3e3e5bee33750f7846eadeee |
| scripts_eng/ok_runner_pin.py | c7805d9a78e4f5478fa4c9e3becda48e76453ee0889b4f7027009a676c3e2485 |
| quantlab/metrics.py | a822dfee88b2f524af61ac1de9fae149885f46c4363e93414897c1c77b4bfb62 |
| quantlab/portfolio/trade_calendar.py | ef44e7cd04911523dbb94c19500393cc0cf423c6728a35826bf0cbb123925eec |
| core_x2/core_v1_3_disclosure.csv | 9586e5f3ecde6580c5b232a4823fe167814f49a697c823acaea46be688bc2c1b |
| c_col_exec_diagnostic.py / core_c5_rereport.py | e9e42f14… / d61f50f2…，与申请单一致 |
| quantlab/platform/execution.py | **373fed309f055888e83572d3fbef8f5b5052ebfcb208307962a272bca6fc486c**（仍是原版） |
| quantlab/platform/__init__.py | bfdfa63cbd7f39d7f0b1eb5a9b91ca00a30bdbd21e31ef3b90d89ac6080e99fc |

受保护件都没动，且都在 manifest 8824a87e 里有记录：
- scorecard_three_col.md / .md.gen：5b9250d2…
- .csv：7622242b…
- notes_manual：b84a705c…
- RESIGN：f27c7e97…
- S2_3_RELEASE：11a69392…

`ARCH_RUN_AUTH_ENG_AUDITFIX_20261018.ok` 和 `overcap_recount_*` 都还不存在。

### C2. 门控 diff（b302911b → c7805d9a；旧版在 `_recovery/eng/scripts_eng/ok_runner_pin.strict_b302911b.py`）
Eng 的硬化声明逐条核实成立：
1. pin 和 dep 只接受 64 位小写 hex，前缀不再算数。
2. 列出的 .ok 缺失就拒跑。
3. 每份列出的 .ok 都要求 `live=false` 和 `promotion=false`。
4. 本次 mode 必须在钉 pin 的 .ok 里是 `allow_<mode>=true`，并且在任一 .ok 里都不能是 `=false`。
5. 同一个键出现两次且值不同就拒跑，值相同则允许。
6. 不认识的键忽略。
7. runner 和 dep 的 sha 都在运行时从文件字节重算。
8. 没有 argv、环境变量或绕过开关。

用草案验证：
- scorecard（disclosure_only）和 recount（recount）都能得到 PINNED_MATCH。
- full、smoke，以及 c_col 的 diagnostic，都会被拒。

门控本身没有新的 P0 或 P1。

### C3. 记分卡输出路径
- **已强制：**
  - `out_paths()` 在门控之前就会拒绝三种情况：tag 不合法、目标是受保护文件、目标已存在。
  - 受保护集合是 md、md.gen、csv 和 notes_manual。
  - notes_manual 不再追加，只告警。
  - disclosure-only 模式只读取受保护的 csv。
- **P1-3（新增，没过）：sha 后缀没有强制。**
  - tag 只来自 argv 的 `--out-tag`，正则是 `[A-Za-z0-9_]+`，脚本不会自动追加 sha。
  - 门控也不解析任何 out_tag 或 out_md 键（`out_md` 只作记录）。
  - 因此裸 tag `auditfix_20261018` 照样可以写盘，不满足主 Agent 01:37 的「新路径带 sha 后缀」要求。
  - 这一条不能只靠 .ok 解决：.ok 里写了 tag，门控也不会检查它。
- **P2-5：写盘有竞态。** 先判断 `exists()`，再 `write_text`，两步之间是 TOCTOU 窗口，应改用 `open(..., "x")`。
- **P2-6：metrics 在门控前加载。** 模块顶层先 import pandas、numpy 和 quantlab.metrics，门控之后才核 metrics 的 sha。Eng 已自报这一点。改为门控之后再 import 更好。
- **P2-7：import 闭包没钉全。** `quantlab/portfolio/__init__.py`（dc6c39f5）和它 import 的 v2_constructor、v2_rebalance 等文件不在 dep pin 里。这些只在 metrics 惰性 import trade_calendar 时才会加载。

### C4. 复算脚本 overcap_recount_v1_3.py
- 输入：只用 csv 模块读 `core_v1_3_disclosure.csv`，读之前有门控 dep pin 和脚本内常量两道 sha 校验。用到的列 sleeve、status、aum、window、one_way_opt 都存在。不 import pandas 或 quantlab。
- 输出：只写一个文件，`core_x2/overcap_recount_v1_3_<tag>.json`，目标已存在就拒跑。目录固定为 core_x2。
- 问题：
  - 同样没有强制 sha 后缀（P1-3 一并修）。
  - 同样有写盘竞态（P2-5）。
- P3：`match` 字段只和 28/96、18/81 比对。冻结的 RESIGN .ok 第 16 行写的是 28/95、18/80，主 Agent 已收下这处分母更正，但冻结件不能改。复算结果应该原样报分子和分母，并注明这处差异。

### C5. 并发与资源
- 01:44 ET 执行 `ps`：tie-sens PID 90241 已经不在，也没有 Alpha regen 或其他研究进程。
- 在跑的是 Data 采集任务，nice 都是 0：tier3_daily_snapshot、remaining_after_stk_surv、relay_outage_backfill、nightly_update。
- 将来放行时要求：
  - 串行执行，先 recount、再 scorecard；
  - 用 `nice -n 10`；
  - 开跑前再 `ps` 一次，确认没有研究进程在跑。

### C6. 其他核实
- κ 回执（5cebbd1d）第 26–27 行已补上参与率上限 0.10（execution.py L347）和 min_trade_value=2000（v2_multisleeve_book L477）。核实通过，原 P3 关闭。
- S2-3 解除 VOID 的说明在 `docs/v2/eng_s2_3/VOID_LIFTED_20261018_*.md`，共 4 份。
- c_col 的门控列表里已有 AUDITFIX.ok，以后签发时要写 `allow_diagnostic=false`，草案已经写了。
- 附带提一句（属 SD1 审查范围）：`sd0_parity_runner.py` L50 调用 `enforce(__file__, [OK])` 时既不传 modes 也不传 deps，allow_* 和 execution 的 dep pin 都不会被检查。

### C7. 要 Eng 改的（改完报新 sha，Arch 再签）
1. **P1-3 修法，二选一，推荐 (a)：**
   - (a) 两个脚本都要求 `--out-tag` 以 `_<本脚本 sha256 前 8 位>` 结尾，例如 `auditfix_20261018_a85444ee`；不符合就拒跑。sha 前缀用 `ok_runner_pin.sha256_file(__file__)[:8]` 运行时计算。
   - (b) 门控新增解析 `out_tag_<script_stem>=<tag>`：钉 pin 的 .ok 里必须有这个键，并且与 argv 完全一致，同时满足 (a) 的后缀规则。enforce 增加 `out_tag` 参数。
   - 两种做法都要把 tag 写进输出元数据。
2. P2-5：改为排他创建写盘，`open(path, "x")`。记分卡两个输出都已存在才算完成；中途失败必须报错，不能静默。
3. P2-6（建议）：把 `from quantlab import metrics` 挪到 enforce 之后。
4. 修完后报新的全长 sha，并说明 py_compile 结果。门控 c7805d9a 没改就不用重审。

### C8. 签发用草案（未签；`/tmp/arch_auditfix_draft/ARCH_RUN_AUTH_ENG_AUDITFIX_20261018.ok.DRAFT`）
- 键用门控实际解析的格式：`runner_sha256_<stem>`、`dep_sha256_<key>`、`allow_<mode>`、`live` 和 `promotion`。
- 另外写入 `out_tag_core_x2_scorecard=auditfix_20261018_a85444ee`、`out_tag_overcap_recount_v1_3=auditfix_20261018_4dd66271`，以及 `allow_full=false`、`allow_smoke=false`、`allow_diagnostic=false`、`allow_disclosure_only=true`、`allow_recount=true`。
- Eng 交付新 sha 后，把 runner sha 和 tag 前缀替换掉再签。

live=false · promotion=false · 未写 .ok · 未运行任何 runner。

## 附录 D：r3 复审与签发（2026-10-18 01:56 ET，Arch）

- 被审对象：`_recovery/eng/OK_REQUEST_ENG.md` r3，sha 实测 60f4eb8f28512b06046dcfeb1dfa29c43de6e974c61a31315c114a30ab45329f（与申报一致）。
- 本次只做了只读核对、sha256sum、rg 静态追踪、读 csv 计数，并以纯函数方式 import `ok_runner_pin`，对 .ok 做 `parse_ok`/`enforce` 校验（只算文件 hash，不运行任何 runner）。附录 C 的审查基线 sha 为 8b50f6c0…。

### D1. sha 复算（64 位）
| 文件 | 实测 | 结论 |
|---|---|---|
| scripts_eng/core_x2_scorecard.py | 2aa03a8f99477073950f33ff366acbb7aec876e9025a3994ca0a407e0ad089ae | ✓ |
| scripts_eng/overcap_recount_v1_3.py | ff4ac3f0251d04c34408f12092d75c00c79b5353e84c1f0359e5c3b3c046794d | ✓ |
| scripts_eng/ok_runner_pin.py | c7805d9a78e4f5478fa4c9e3becda48e76453ee0889b4f7027009a676c3e2485 | ✓ 未改 |
| core_v1_3_disclosure.csv | 9586e5f3ecde6580c5b232a4823fe167814f49a697c823acaea46be688bc2c1b | ✓ |
| 受保护件：md/.gen 5b9250d2…、csv 7622242b…、notes_manual b84a705c…、RESIGN f27c7e97…、S2_3_RELEASE 11a69392… | 同 | ✓ 未动 |

### D2. 附录 C 逐项核实
- **P1-3 ✓ 关闭。** 两个脚本都在门控前，用 `ok_runner_pin.sha256_file(__file__)[:8]` 在运行时算 sha8，`--out-tag` 不以 `_<sha8>` 结尾就 SystemExit（记分卡 L489–492，复算 L36–38）。tag 和全长 runner sha 都写进输出：记分卡在 md 末行 HTML 注释里，复算在 json 的 `out_tag` 和 `runner_sha256` 字段里。按现 sha，合法 tag 只能是 `auditfix_20261018_2aa03a8f` 和 `auditfix_20261018_ff4ac3f0`。
- **P2-5 ✓ 关闭。** md、.md.gen、full 模式的 csv（L524/546）和复算 json（L72）都用 `open(path,"x")` 排他创建。输出目录不新建：disclosure-only 模式写进已存在的 core_x2，full 模式的 `OUT.mkdir(exist_ok=True)` 只针对已存在的固定目录。文件级排他已足够，不另要求建目录。
- **P2-6 ✓ 关闭。** 模块顶层只 import json/math/sys/pathlib/numpy/pandas；`from quantlab import metrics` 在 L500，位于 enforce 之后。复算脚本不 import quantlab 和 pandas。
- **P2-7 ✓ 关闭。** Arch 用 rg 独立追踪 import 语句（含函数内 import，并查过 importlib/__import__/exec，无命中），闭包如下：
  - metrics（a822dfee）只 import numpy/pandas，L75 在函数内惰性 import `quantlab.portfolio.trade_calendar`；
  - 这会先执行 portfolio/__init__（dc6c39f5），它 import v2_constructor 和 v2_rebalance；
  - v2_constructor 依次 import mandate_v2 → promotion_gate、config；函数内 import config 和 strategy.portfolio，后者经 strategy/__init__ 再 import scoring、portfolio、risk；
  - v2_rebalance 只 import mandate_v2；
  - trade_calendar（ef44e7cd）只 import 标准库和 pandas；
  - config、promotion_gate 只 import 标准库。
  - 闭包共 13 个 quantlab 文件，加上 ok_runner_pin 共 14 项，与 `SCORECARD_QUANTLAB_DEPS` 加 3 个固定 dep 完全一致，没有遗漏。metrics a822dfee 和 trade_calendar ef44e7cd 仍在 import 路径上，已钉住。闭包里没有 quantlab.platform。
  - scripts_eng/ 下没有同名 quantlab 包或 metrics.py，不存在遮蔽。
- **P3 ✓ 关闭（已对数据核实）。** Arch 直接读 core_v1_3_disclosure.csv，条件为 equity_100、status∈{OK, LOT_CASH_GT2}：
  - 60万：超帽 28，全部可行行 96，有换手值的行 95。缺换手值的只有 2018-01-31（SEALED，OK）。X2 为 11/25。
  - 100万：超帽 18，全部可行行 81，有换手值的行 80。缺换手值的只有 2018-01-31（SEALED，LOT_CASH_GT2）。X2 为 7/17。
  - 2018-01-02 两档都是 NO_DATA_CARRY，不进任何分母。
  - Eng 的解释成立。复算 json 原样输出分子和两种分母，以及 `rows_without_turnover`；记分卡放行条件第 3 条写明了原因。

### D3. 其他确认
- **门控 modes。** 记分卡用 `["disclosure_only"]`（full 模式用 `["full"]`），复算用 `["recount"]`。
- **sha 比对。** ok_runner_pin 用 `HEX64.fullmatch` 和 `!=` 做 64 位精确比对，没有 startswith。runner 自身 sha 在 enforce 里由文件字节重算（L79）。两个脚本里唯一的 `endswith` 用在 tag 后缀规则上，这是预期用法。
- **out_tag 键。** 两个 runner 都只从 argv `--out-tag` 读 tag，门控不解析 .ok 里的 `out_tag_*`/`out_*` 键。这些键只作记录；约束靠 sha8 后缀规则实现，等价于附录 C7 的方案 (a)。
- **记分卡门控列表。** RESIGN 和 S2_3_RELEASE 两份 .ok 都存在，`live/promotion=false`，没有 `allow_disclosure_only=false`，也不钉本脚本 sha，只有 AUDITFIX 钉住。
- **验证结果。** 签发前用 parse_ok 验证：39 个键，无 BOM、无 CR、无 `#`、无重复键冲突，所有 runner/dep 值都是 64 位 hex。对 /tmp 副本和落盘件用 enforce 纯函数校验：
  - scorecard 的 disclosure_only（三份 .ok 一起）得 PINNED_MATCH；
  - recount 得 PINNED_MATCH；
  - full、smoke、diagnostic 全部拒跑。

### D4. 遗留问题（不挡签发）
- **P3-D1。** disclosure-only 模式读取的 c5_feasibility_v1_3.csv、c5_weight_stamp_v1_3.json、core_v1_3_disclosure.csv、s2_3 exec_metrics 等输入没有作为 dep 钉 sha，只靠 manifest 和事后核对。
- **P3-D2。** 第三方库（numpy/pandas/scipy/sklearn）没有钉版本，口径与既往一致。
- **P3-D3。** 01:54 ET 执行 `ps`：没有研究进程。有一个 nice=10 的 `[python3] <defunct>`（PID 154554，非 Arch 所起，已是僵尸、RSS 0）；Data 采集 4 个进程在跑，nice 0。

### D5. 签发
- **已写入** `output/strategy_optimizer/core_x2/ARCH_RUN_AUTH_ENG_AUDITFIX_20261018.ok`，sha256 = 623c038af325336134cc9e04988e8bf1f90594bedb12e905c00958cdbe2be8f3，signed_et=2026-10-18T01:55:00-04:00，排他创建。
- 运行条件：
  - 串行执行，先 recount、后 scorecard（`exec_order` 键）；
  - 使用 `nice -n 10`；
  - 开跑前再 `ps` 一次，确认没有研究进程；
  - 只允许以下两条命令：
    - `nice -n 10 python3 scripts_eng/overcap_recount_v1_3.py --out-tag auditfix_20261018_ff4ac3f0`
    - `nice -n 10 python3 scripts_eng/core_x2_scorecard.py --disclosure-only --out-tag auditfix_20261018_2aa03a8f`
- 任一 runner 或 dep 的 sha 变化都会自动拒跑，须重新申请。

live=false · promotion=false · 未运行任何 runner。
