# Arch 审查：Alpha CMC v1.1 / s8 v1.1（2026-10-18 ET）

- 审查人：QuantLab Arch；审查时间：2026-10-18 02:50–03:00 ET
- 依据：主 Agent 2026-10-18 02:44 ET 裁定（风格项一律 t−1；ladv 不再额外移位；acap t−1；叶24 残差化 = 冻结风格集 + vol20_{t−1}；e_id = SW L1 + logmv_{t−1}）；`docs/v2/ARCH_RUN_AUTH_SELFTEST_SPEC_ZH.md`（1aa43bdd）；`scripts_eng/ok_runner_pin.py`（c7805d9a）
- 审查方式：只读通读加静态分析（diff、patch 回放、AST 扫描 import 闭包和 f 前缀）。**没有运行任何项目代码，没有读取任何真实数据。**
- live=false，promotion=false

## 0. 结论
- **结论：逻辑通过，无 P0、无 P1。** 每个回归量都从源头追到了信息日期，信号侧全部是 t−1，s8 和 CMC 都没有前瞻。
- **selftest .ok 本次不签（流程阻断 B-1，不是代码缺陷）。** 规范 §2 要求钉住测试文件，即 `runner_sha256_<测试文件 stem>`，但 Alpha 交审的文件里没有合成测试文件。两个 v1.1 脚本在 `__main__` 下只接受 `modes=["full"]`：selftest .ok 里 allow_full=false，会被 enforce 拒跑；allow_full=true 又不符合 selftest 授权。所以必须另写一个测试文件（harness），顶层先过门禁 `modes=["selftest"]`，再 import 被测模块。测试文件交来、Arch 审过后，按 §6 模板签发。
- **签全量运行 .ok（allow_full=true）之前必须先修 P2-1 和 P2-2。** P2-3 建议在 v1.1 里修（还没运行过，没有沉没成本）；不修的话必须披露。

## 1. sha 核验（2026-10-18 02:52 ET 实算）
| 文件 | sha256 | 结果 |
|---|---|---|
| research/alpha_combo_marginal_v1_1.py | f1abd3ed95f06bd695823a3cc224509727dbc36a7d0cbf09b0b51664c868ae5e | 与交审一致 |
| research/alpha_hiliq_s8_paradigm_v1_1.py | 10b2846313b91546c8a549c74b2be26dc1e3f1e4434fa1a4fe5b049a71444429 | 一致 |
| docs/v2/ALPHA_S8_CMC_V1_1.patch | eb2479bf2f4a73aa23cdbe81c7e737f4e20b336d32fec946b389b5340e781cbe | 一致；在旧文件上回放后，两个结果的 sha 与上面两行完全相同 |
| docs/v2/ALPHA_S8_CMC_V1_1_HANDOFF_ZH.md | 204f6e6742a7beb32a75a6fcb982dae6584b26be68604101943f4839ae429a08 | 一致 |
| docs/v2/ALPHA_HILIQ_S8_PARADIGM_RULES_20261014_ZH.md | 13e13c4b0cce836238d743b379fd66113b44c38816dfeb397aa3263daf6ccc8a | 一致；文末追加的锚点澄清与代码一致。仓库不在 git 下，无法用 diff 证明「原有内容未改」，只能确认正文的风格集和阈值表与冻结口径相符 |
| research/alpha_combo_marginal.py（旧） | bee230199ac27bf9730aa77c63b104a67bb104229622c57524867a9b54a5c51c | 未改 |
| research/alpha_hiliq_s8_paradigm.py（旧） | af48bc05fbcfb55e72336806c03455dbf4f0b52079c833aed9f141bece00966c | 未改 |
| scripts_eng/ok_runner_pin.py | c7805d9a78e4f5478fa4c9e3becda48e76453ee0889b4f7027009a676c3e2485 | 一致 |
| research/leaf_selfcheck_v3.py / leaf_selfcheck_common.py | ecaa30d8… / 218b61cf… | 一致 |

## 2. 回归量信息日期逐项追溯（d = 信号日；IC 用收盘 d 到收盘 d+20）
### 2.1 CMC v1.1（ctx / resid_z）
| 暴露 | 代码 | 追到源头的信息日期 | 结论 |
|---|---|---|---|
| β120 | L144 `R.rolling(120,min60).cov(rb)/var`；L145 `.shift(1)` | R[d] 是收盘 d−1 到 d 的收益。移位后窗口为 d−120..d−1，最后一个观测是收盘 d−1。rb 是 510300 的 close_hfq（ADG.bench） | t−1 ✔ |
| log 流通市值 | L154 `log(FMp.reindex(cal).ffill()).shift(1).reindex(ev)` | 收盘 d−1；停牌时用 d−1 及以前最近一个值。cal 从 2024-04-01 起，所以 START 当日取 2024-05-31 | t−1 ✔ |
| SW L1 | L156–157：每月最后一个 ev 日 me 调 `sw_code_on`（in_date ≤ me 且 out_date > me），再向前填充 | 不晚于 d 的最近月末生效成员。月末当日用当日生效成员（见 P3-5）；首月没有月末可用（见 P2-3） | PIT ✔ |
| 池 | L147 mask `in_universe[d]` | 写入方 strategy_hiliq_universe_v1.py L130–160：adv 用 `sess < S` 的前 20 日；bar_prev 用 d−1；ST 和停牌取 d 当日状态（盘前已知） | 无前瞻 ✔（表述见 P3-6） |
| 叶 / 腿信号、extra | `sig()` 取 d 的 target_weight | 同日信号，用来正交化，不是风格项。与旧版相同 | 不变 ✔ |
| F | L142 P 只 reindex 到 ≤ END 的日期；L158 `P.shift(-20)/P−1` | d+20 > END 时为 NaN，确实截断了 | ✔（但断言是恒真式，见 P3-1） |
| mom / liq / vol20 | 不使用 | — | 与 bee23019 一致 ✔ |
- tiers 的书收益（V3.LC._ret，T+1 开盘）、vs_poolEW、report_to_leo_eligible、阈值：与 bee23019 逐行一致。
- 与 bee23019 的完整 diff 和交接 §3 所列一致，**没有未声明的改动**。删掉的 `import g1g5_moneyflow_resid_weights` 确实没被用到。`leaf_path` 的 glob 与 V3.wfile 完全相同。

### 2.2 s8 v1.1（build / xmat / resid_multi / resid_ret）
| 暴露 | 信号侧 X_sig | 收益侧 B（X，在 r−1） | 结论 |
|---|---|---|---|
| mc | L149 `shift(1)` → 收盘 d−1 | 收盘 r−1（不变） | ✔ |
| β120 | L134 `beta.shift(1)` → d−120..d−1 | r−119..r−1（不变） | ✔ |
| mom | L135 C(d−21)/C(d−121)−1 | C(r−21)/C(r−121)−1（不变） | ✔ |
| liq | mask `adv20_yuan[d]` = d−20..d−1 均值，已核写入方 L130–141 | 同 | ✔（符合「ladv 不再额外移位」） |
| SW L1 | `industry_on_date`（与 sw_code_on 语义相同）月末加向前填充 | 同 | PIT ✔ |
| F | L136–137 在 `C.loc[:END]` 上计算 | — | 确实截断 ✔ |
- 与 af48bc05 的 diff 只有交接 §3 所列的 9 项。阈值（vA/vAp/vB/vC）、neut_net（权重滞后 2 日）、topn、TYPE_CAP 都没变。去掉了每条腿的 `stamp` 字段，输出文件名也换了，对下游无影响。
- `ic_tstats` / `nw_se` 改从 CMC v1.1 import，函数体与旧版逐字相同。

## 3. 门禁与输出
- **门禁在重 import 之前（✔）。** 两个文件在 `__main__` 里先 `_cli()`，再 `enforce()`，然后才 import numpy、pandas 和项目模块。门禁之前只用了标准库，加上 `glob`（leaf_path）。
- **--arch-ok 必填（✔）。** argparse 设了 required=True。
- **legacy-json 已钉住（✔）。** 传入后 `deps["legacy_json"]` 进入 enforce，.ok 必须有 dep_sha256_legacy_json，而且 sha 要相符，否则拒跑。工具会拒绝 v1.1 自己的输出，也会拒绝 universe 不一致的文件。旧工具没有被 import。
- **CMC 的 --out 排他创建（✔）。** 用的是 `open(...,"x")`。s8 要求 out_dir 为空，_panel_close 和 JSON 都以 "x"/"xb" 方式写入（✔）。
- **s8 RSS 看门狗。** 每 2 秒检查一次 ru_maxrss（Linux 下单位是 KB，是峰值），超过 1,536,000 KB（=1500 MiB）就 os._exit(3)。逻辑正确，但只能事后发现，不是硬上限（见 P3-4）。CMC 没有看门狗，只记录峰值。
- **f 前缀扫描（✔）。** 用 AST 扫了两个文件中所有非 f 字符串里的 `{name}`，只命中两处 docstring 里的 `mc_{t−1}` 记号，没有模板漏写 f。
- py_compile：两个文件都编译通过。Arch 运行时生成的 2 个 .pyc 已立即删除（见 §7）。

## 4. 发现清单
### P0：无
### P1：无
### P2
- **P2-1｜依赖闭包没有钉全（阻断全量 .ok，不阻断 selftest）。** 用 AST 静态展开 import 闭包（含函数内的延迟 import），CMC 和 s8 都会拉进大约 78 个项目模块。CODE_DEPS 只钉了其中 7 个（s8 是 9 个）。执行路径上没有钉住的研究模块有：
  - `research/ai_debate_memory_runner.py`（e1736d80…，就是要求 AI 原样提交的那个文件），经 nontextbook 和 panel_stitch 进入；
  - `research/g1g5_wiring.py`（ff510148…）；
  - `research/g1g5_expand_g6.py`（b2d26c0d…）；
  - 整个 quantlab/* 包，其中包括冻结中的主干 `quantlab/platform/execution.py`（373fed30）和 `__init__`（bfdfa63c），经 leaf_selfcheck_common 的函数内 import 进入。
  按 Arch 已有口径（执行路径上闭包外的模块会使运行作废），全量 .ok 签发前，CODE_DEPS 至少要补上上面 3 个 research 模块。quantlab/* 要么逐个钉住，要么钉一份闭包清单文件（manifest）。另外建议把 `ok_runner_pin` 自身也列为 dep（见 P3-7）。
- **P2-2｜全量路径不检查 .ok 的有效期和格式（阻断全量 .ok）。** c7805d9a 不检查 expires_et、scope、BOM、CRLF 和「未列出的 allow_* 是否为 false」（规范 §9 已经写明）。两个 v1.1 脚本也没有自查。后果是过期的全量 .ok 只要 sha 还对得上，就能无限次复用。要求在 enforce 之后、重 import 之前加自查：
  - expires_et 存在、带时区、未过期；
  - scope 是 full 或指定值；
  - 文件无 BOM、换行为 LF；
  - 已知的 allow_* 都显式写出。
  叶 23/24 的 read_ok 已经这样做了，可以照搬。另一条路是由 Eng 出 ok_runner_pin 新版本，另行送审。
- **P2-3｜首月没有行业控制，docstring 的说法不成立（旧版就有）。** me 只从 ev（从 START 起）中取，所以 2024-06-03..06-27 这 18 个交易日 IND 全是 NaN，被 fillna 成同一个 `_UNK` 哑变量，等于没有行业中性化。这影响 CMC 的 resid_z，也影响 s8 的 X_sig 和 B 集合。旧版 bee23019 / af48bc05 也是这样，但 v1.1 docstring 写的「last month-end ≤ d」在这段时间不成立。
  - 建议：在 v1.1 里把 me 的取值范围前推到包含 2024-05-31（例如从 days/cal 取），并在输出里写明与旧版的这一差异。
  - 如果不修：exposure_anchor 和 docstring 都要改成如实表述，输出加披露字段。
  - 这项属于事后、对后续叶子生效的范围，由主 Agent 决定修还是只披露。

### P3
- **P3-1：** CMC L159 的断言 `F.index.max() > END` 是恒真式。F 的索引本来就只到 END，所以断言测不到值是否越界。截断实际上由 L142 的 reindex 保证。建议改成 `assert P.index.max() <= END and F.iloc[-H:].isna().all().all()`。
- **P3-2：** CMC 的 `--out` 要等计算全部结束才排他创建，文件已存在时要白算一遍。建议在门禁之后先检查 `not Path(out).exists()`，写入仍然保留 "x"。
- **P3-3：** legacy_column 有三处可以收紧：
  - 读入时重算的 sha 没有与 `_GATE["deps"]["legacy_json"]` 比对（检查到使用之间存在时间差）；
  - base（capadv/b4）不一致时不拒绝；
  - 叶文件名不一致时只报告。
  建议这三种情况都拒绝，或者在输出顶层置 `legacy_comparison_valid=false`。
- **P3-4：** 看门狗是轮询峰值，2 秒的窗口里内存可能远超上限（以前出现过 3.2GB）；GIL 长期被占用时线程还会延迟。建议加 `resource.setrlimit(RLIMIT_AS, …)` 作为硬兜底，或者分块读取。CMC 也建议加同样的看门狗。
- **P3-5：** SW L1 在月末当天用的是当日生效的成员（in_date ≤ d），不是严格的 t−1。申万的调整都提前公告，实际影响可以忽略，但文档应写成「≤ d 的月末生效成员」，或者改为取 d−1。
- **P3-6：** 交接和 docstring 说「mask 由 d 之前的数据生成」，不准确。ST 和停牌取的是 d 当日状态（盘前已知），adv 和 bar_prev 才是 d−1。结论仍然是没有前瞻，只需改表述。
- **P3-7：** ok_runner_pin 自身没有进 deps，存在「门禁本身被替换」的风险。c7805d9a 还有几处宽松：接受 CRLF；首行带 BOM 时首个键被忽略；同键同值可以重复。行内注释会失败关闭，这一点是安全的。
- **P3-8：** 交接 §5 的 .ok 模板带行内注释（`… # CMC v1.1`）。照抄的话 sha 值会带上注释，被拒。Arch 签发时不会照抄。
- **P3-9：** panel_stitch 的 `X2_END` 可以被环境变量 `QL_X2_EXTEND_END` 改写。CMC 的 P 截到 END，s8 的 F 截到 END，不影响结论。但建议输出记录这个变量，或者断言它没有设置。
- **P3-10（顺带抽查 v3，不在本次范围）：** v3 L138 的 `P.shift(-h)` 是按叶日期的行数移位（P 已经 reindex 到 S.index）。如果叶 parquet 有缺日，h 行就不等于 h 个交易日，而且没有截到 END。这个问题转给 Alpha/AI 单独立项，sha 另审。

## 5. Alpha 的其他声明逐条核对
- **leaf_selfcheck_v3 不需要 v1.1：✔。** v3 中没有 lstsq，也没有截面风格回归。factor_report 是原始权重对前瞻收益的 IC，style_neutral 和 rho 都从 run_meta 读出。
- **common L118 的 β 已经是 t−1：✔。** `(gl.rolling(120,min60).cov(bl)/bl.rolling(...).var()).shift(1)` 是叶净收益对 510300 的时序 β，用在 A 臂去 β。
- **v3 L138 没有截到 END：✔。** 属实，另见 P3-10。
- **阻断项属实（grep 确认）：**
  - `research/g1g5_sue_desens_cs_alpha.py`（07c99873…）L74 和 `research/g1g5_imax_intraday_alpha.py`（1e8de734…）L62 都把 `dep_combo_sha256` 写死为 `R/"research/alpha_combo_marginal.py"`；
  - TOOL_CMDS 指向 `output/ai_factory/ARCH_TOOL_CMDS_LEAF{23,24}_X2.cmd`，这两个文件**目前都不存在**，需要 Arch 按 v1_1 加 `--arch-ok` 写好并钉住；
  - L580 / L518 的 docstring，以及 L713 / L646 的披露文字，仍然引用旧 s8，说它「以 t 为锚」。
  这些由 AI 并入 r2.6/r5。叶 .ok 届时钉 `dep_combo_sha256=f1abd3ed…` 和 `dep_combo_legacy_sha256=bee23019…`；s8 v1.1 只钉在 Alpha 自己的 §8 验收 .ok 里。
- **披露「误执行一次空的 python3」：** 没有加载任何项目代码，按规范 §1 不算运行，只记录，不定级。

## 6. selftest .ok 签发条件和模板（测试文件交来后签）
测试文件要求：
1. 文件顶层先过门禁 `enforce(__file__, [OK], modes=["selftest"], deps={...})`，并按规范 §4 自查：scope=selftest、allow_real_data=false、out_dir 不在 output/ 下。放行之后才 import 两个 v1.1 模块。
2. 不得读任何真实数据。改用以下方式：
   - 把 `UNIVERSE_MASKS` / `FMC` / `MASK` 换成 mkdtemp 里的合成 parquet；
   - monkeypatch `ADG.bench`、`ADG._close`、`_load_sw_members`。
3. 至少覆盖：
   - mc / β / mom 的 t−1 性质：只改 d 当日数据，d 的暴露不变；改 d−1，暴露随之变化；
   - F 在最后 H 日为 NaN；
   - `--out` 和 out_dir 拒绝覆盖；
   - legacy_column 拒绝 v1.1 输出和 universe 不一致的文件；
   - 看门狗触发：在子进程里把阈值临时调小；
   - 缺少 `--arch-ok` 时 argparse 拒绝。
4. 交来测试文件的路径和 sha，以及它 import 到的全部项目模块的 sha。

签发模板（无 BOM，LF，不带行内注释）：
```
format=quantlab_run_auth_v1
signed_by=arch
signed_et=<签发时刻，带时区>
scope=selftest
runner_sha256_<测试文件 stem>=<64 hex>
dep_sha256_combo_v1_1=f1abd3ed95f06bd695823a3cc224509727dbc36a7d0cbf09b0b51664c868ae5e
dep_sha256_s8_v1_1=10b2846313b91546c8a549c74b2be26dc1e3f1e4434fa1a4fe5b049a71444429
dep_sha256_ok_runner_pin=c7805d9a78e4f5478fa4c9e3becda48e76453ee0889b4f7027009a676c3e2485
dep_sha256_<测试文件 import 到的其余项目模块>=<64 hex>
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
expires_et=2026-10-19T02:50:00-04:00
```
路径：`output/alpha/ARCH_RUN_AUTH_SELFTEST_CMC_S8_V1_1.ok`。运行命令和回执要求见规范 §5 和 §7，回执必须记录峰值 RSS。

## 7. Arch 自身披露
- 审查时对两个 v1.1 文件执行过 `python3 -m py_compile`（规范 §1 规定这不算运行）。它在 `research/__pycache__/` 生成了 2 个 .pyc：alpha_combo_marginal_v1_1 和 alpha_hiliq_s8_paradigm_v1_1。02:56 ET 已删除，目录恢复为原来的 22 个文件。以后统一用 `PYTHONDONTWRITEBYTECODE=1`，或者编译到 /tmp。
- 闭包扫描和 f 前缀扫描用的是 Arch 自己写在 /tmp 的 AST 脚本，只解析源码，不 import、不执行项目代码。
