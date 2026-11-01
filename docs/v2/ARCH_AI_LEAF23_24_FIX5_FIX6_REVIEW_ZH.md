# Arch 审查：AI 叶23 r2.7 / 叶24 r6（FIX5 + FIX6 合审）+ commit f98e408e 核验

- 审查人：QuantLab Arch；时间：2026-10-18 03:28–03:40 ET。上一轮：`docs/v2/ARCH_LEAF23_24_FIX4_RECHECK_ZH.md`（032cef56）。本轮最初按 FIX5（r2.6/r5）写过一稿，审查期间 AI 于 03:32 交付 FIX6，那一稿已改名为 `ARCH_AI_LEAF23_24_FIX5_REVIEW_ZH.SUPERSEDED.md`（36f966e3），以本文为准。
- 依据：主 Agent 02:44（基准池主口径按退市日截断）、03:22（CMC v1.1 改钉修复后 sha）、Arch CMC v1.1 r3 审查 bbfcb7ef、SD1 规范 2e428f39 §3.6、v1.4 审查 f2edc099 P2-1。交叉参考 Alpha 复核 486496a9（FIX5，CONDITIONAL）和 1271bb27（FIX6，PASS）；本文结论独立得出。
- 方式：静态审查。做了以下几件事：
  - sha256sum、git show/diff-tree；在 /tmp 临时目录对存档依次 git apply。
  - AST 解析：f 前缀扫描、.ok 键白名单抽取、模块级先用后定义检查（自写，只 ast.parse）。
  - 在 /tmp venv 安装 pyflakes 4.0.3，对文件做纯语法分析，不 import 被查文件。
  - 唯一执行的仓库脚本是 `scripts_eng/sd1_pit_static_check.py --mode disclosure`。执行前确认：它只用标准库（argparse/ast/hashlib/json/re/sys/pathlib），不 import 任何项目代码；只读 SCOPE 下的 .py 文本；只在 `--json` 时写文件；scripts_eng/ 下没有遮蔽标准库的同名文件。用 `python3 -I -B`、PYTHONDONTWRITEBYTECODE=1 运行，不带 --json，运行前后 __pycache__ 目录数都是 231。
  - **没有运行或 import 叶脚本和测试，没有读取任何真实数据（只对文件算了 sha），没有写 .ok 或 .cmd。** 临时目录已删除。
- live=false；promotion=false。

## 0. 结论
- **Part 1（commit f98e408e）：通过。** 关闭 v1.4 审查 f2edc099 的 P2-1。
- **Part 2（FIX5 + FIX6，终版 r2.7 / r6）：代码层面通过——P0=0 / P1=0 / P2=1 / P3=8。**
  - P2-1：两份叶脚本还没提交 git。不需要改代码，但提交之前不签 .ok。
  - FIX6 修掉的模块加载 NameError，是一个**一直存在的 P1**：从 FIX2 产出的 r2.3/r2 开始，跨 4 个版本。Arch 三轮审查都漏了，记为 Arch 失误，见 §5。
- 叶 .ok 和 .cmd **本轮不签不写**。签发次序见 §11。

## 1. Part 1：commit f98e408e31a3aff5749c3a48e6578deb1168cb16
| 项 | 结果 |
|---|---|
| 分支 / HEAD | main，HEAD = f98e408e ✓ |
| 父提交 | fb48928db94b4b5fe025efbbc0097e741a63da65（上一个 HEAD）✓ |
| 改动文件 | `git diff-tree` 只有 2 个 M：research/ai_debate_memory_runner.py、research/g1g5_x2_panel_stitch.py（+38/−1）✓ |
| 提交 blob sha | e1736d80c589ecd717731dc38ae99a52f3d448da9841b2c3794ee008f59613ea / 043fa68d4e6dd40f003db04fddfd79fb431c4a00f280a0a5db35cbe733d90620 ✓ |
| 工作区 | 与 blob 逐位一致，`git status` 干净 ✓ |
| 主干 | execution.py 373fed30…、`__init__.py` bfdfa63c… 未动 ✓ |
- 内容就是此前审过的两处，都只作自检：`_load_benchmark_closes_hfq`、`load_adj_close_x2`。`X2_END` 默认冻结在 2026-10-09，只有设了环境变量 `QL_X2_EXTEND_END` 才放开（见 P3-5）。
- v1.4 审查第 102 行「nt_ai_debate_memory_runner_sha256 须等 AI 提交后复核」：现在可以填 e1736d80…。签 v1.4/D21 .ok 时仍要实测。

## 2. 补丁链复现与范围
- 存档 `_recovery/ai/pre_fix5_0325/`：r2.5 07c99873… / r4 1e8de734… ✓
- FIX5 `docs/v2/AI_LEAF23_24_FIX5_DIFF.patch` 6138dce5fbe90d9773f8ac3397787855f24632d1c9f7d670a75dcb7068777d2f：应用后得到 60393573… / a2719e5c… ✓（与 `_recovery/ai/pre_fix6_0331/` 一致）。
- FIX6 `docs/v2/AI_LEAF23_24_FIX6_DIFF.patch` 3679d72026d1cc43e4505dac2b45fdb5f28472a3f8cdbdce7449294ce0d1dbb8：接着应用后，**逐位复现终版**：
  - 叶23 `research/g1g5_sue_desens_cs_alpha.py` r2.7 = 3d094e22d3af3e3cfe4d3c6164fc3d817c93cb92edfc339db2a156981933adc1 ✓
  - 叶24 `research/g1g5_imax_intraday_alpha.py` r6 = 6e46c01cd7268aa549a8d900d78c434b017b25d3cea62c3340754264c4d85c05 ✓
- 预注册未改：叶23 R2_1 8f5d8ac43ba49f11b4461a287addae8c0cf247fbe9d8e81d0b339764e843922e，叶24 c289e77068be607c108359a87e1d17d6b2e8edac9e4cbcca865a9a49430133a8 ✓。`output/ai_factory/prereg_sha_leaf23/24.txt` 只做了追加和「current→superseded」标注 ✓。
- 改动范围：两叶对称。FIX5 动了退市截断口径、CMC 路径与 .ok 键、披露差值位置、说明文字。FIX6 动了：X2S/X2E 提前定义、影子截断计数、复用收益表、说明文字。风格集、选股、记账、判定 t、阶段链都没动。

## 3. 核查 (1)：退市截断与 PIT（终版）
### 3.1 代码与说法一致
- 主口径 `cut = delist_date`，不回退到 last_trade_date ✓。
- `carry = (~has) & (mask 停牌) & ~(d > cut)`：最后交易日到退市日之间，面板无行、mask 停牌时，沿用 S 和停牌前市值；收益在 `rr.reindex(columns=U).fillna(0.0)` 里记 0；成员留在 Mp 分母 ✓。
- P2-1 断言 `gone_full` 用同一个 cut，在 X2 全部日上独立重建；只要出现 `(S & gone_full)` 就停跑 ✓。
- 缺退市日的名：在 U 里、且 X2 内有成员日或面板行的 → `SystemExit`；其余只列入 `delisted_missing_delist_date_outside_x2` ✓。没有任何回退路径。
- 影子口径 `cut_dd = last_trade_date`：只驱动 S_dd/MV_dd → Mp_dd/wv_dd → diag 影子字段，函数内就 del ✓。FIX6 新增 `dl_cut_sh`：`cy = S_nc & ~S_dd & gone_dd & ~has`，限 X2 窗内，在 `del S_nc … gone_dd` 之前计算，变量都还活着 ✓。它是与主口径 `cx` 对称的影子截断名·日计数，只披露。
### 3.2 信息日期逐项追踪
| 用途 | 信息日期 | 结论 |
|---|---|---|
| 主口径截断（d > delist_date），Mp = S.shift(1) | 退市日当天已公开 | 无前瞻 |
| (last_trade_date, delist_date] 沿用、收益 0 | 每天只用「当天无成交、mask 停牌」 | 无前瞻 |
| 影子截断（d > last_trade_date） | 事后才知道那是最后一笔 | 轻微前瞻，**只披露**，不进判定、不计家族次数 ✓ |
| 缺退市日停跑、P2-1 断言、end_after 列表、两种截断计数 | 全窗口事后信息 | 只做完整性检查和披露，不改变成员或权重 ✓ |
- **不进选股。** AST 确认：pool_benchmarks 只被调用一次（叶23 L773 / 叶24 L705，都在 evaluate 里）；`read_parquet(DELISTED)` 只出现在 pool_benchmarks 里。Mp/wv 只用于池 EW/wb 基准和 N4 剔除占比，建书前就 del 了。build（α、gate）和 pick_book 都不读 delisted_master。所以退市日只用于基准收益的事后记账。
### 3.3 FIX6 复用收益表
- 改成 `pool_benchmarks(…, rr, s, e)`，函数内 `idx = rr.index`。原来调用方传的就是 `rr.index`，所以 idx 完全相同。
- `RR = rr.reindex(columns=U).fillna(0.0)`，和 FIX5 evaluate 里的 `r0` 是同一个表达式，作为 `r0` 返回。FIX5 函数内的 `PX.pivot_table(...).reindex(index=idx…)`，因为 pivot_table 本身按日期排序、idx 又等于 rr.index，结果也相同。所以主口径与影子口径的计算口径不变。
- rr 来自 evaluate 的 PX（自 2024-05-20 起，`date <= e`；2024-05-20 只用作 T−1）。是同一张截到窗口末、按 PIT 构造的收益表；reindex 返回新对象，rr 没被原地改动 ✓。
### 3.4 与 SD1 guard（StrategyLayerDelistAccess）的关系
- 叶子**不调用** `quantlab/platform/delist_accounting` 的 loader。如果调用，运行时会抛 StrategyLayerDelistAccess，静态扫描也会把 `delist_accounting` 记为违规。
- 叶子直接读 `data/v2/delisted/delisted_master_tushare.parquet`，这张表不在 guard 的 loader 覆盖范围内。依据是 `sd1_pit_static_check.py` 的 FUNC_WHITELIST：只放行这两个文件 `pool_benchmarks` 函数内的退市字段（主 Agent 02:44；Arch 2b8f81c9 §6.1-3）。这是授权的例外，**不算绕过**。
- 设计假设复核：对「直接读表」，这条防线只靠静态扫描，而扫描关键词有盲点（P3-2）。本轮人工 grep `DELISTED|last_trade_date|delisted|delist`，确认没有其他读取。

## 4. 核查 (2)：CMC 路径与 .ok 键
- `TOOLS["dep_combo_sha256"] → research/alpha_combo_marginal_v1_1.py`，实测 5658f612fef313fc5b818fc4cb9d594d757377e0dbf7c7dc86a6e31788b88911 ✓（= Arch r3 审查 bbfcb7ef 批准版）。
- `TOOLS["dep_combo_legacy_sha256"] → research/alpha_combo_marginal.py`，实测 bee230199ac27bf9730aa77c63b104a67bb104229622c57524867a9b54a5c51c ✓，只作对照列。
- 严格性：
  - 键白名单 = OK_FIXED ∪ OK_REQUIRED ∪ TOOLS ∪ TOOL_CLOSURE。多一个键或少一个键都拒跑，所以 `dep_combo_legacy_sha256` 必填 ✓。
  - 两层比对：.ok 里的值要等于脚本常量 `CMC_V11_SHA` / `CMC_LEGACY_SHA`，**也要**等于文件实测 sha ✓。改常量会改变 script_sha256，所以绕不过去。
  - `cmc_cmd_ok(TOOL_CMDS)`：.cmd 的非注释行里至少一行调 `alpha_combo_marginal_v1_1.py`，且这些行每行都带 `--arch-ok`。.cmd 本身由 tool_cmds_sha256 钉住 ✓。
  - 时机：全部在 `authorize()` 里完成，早于 `verify_panel`（第一次读 parquet）、process_check 和各阶段内的 `import research.g1g5_fund_resid_alpha`。模块级只 import 第三方库 numpy/pandas，不读数据 ✓。
- FIX6 的 L74/L62 注释改为「passed Arch review bbfcb7ef; full-run .ok not yet signed」，与事实相符 ✓。
- **CMC v1.1 有双层授权。** v1.1 本身 `--arch-ok` 必填，runguard 会 `enforce(modes=["full"])`。所以叶 .cmd 必须指向一张**单独签发的 CMC v1.1 全量 .ok**。这张 .ok 要等 Alpha selftest（.ok fa45bf7f39dc…，单次有效）的回执经 Arch 审过才签。这是流程门槛，叶脚本本身不检查。
- 叶23 另有 `dep_capadv_leg_sha256`（已在白名单里，FIX4 草案已列）。它钉的是 `CAPLEG = output/strategy_hiliq/legs/g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet`（capacity_adv HI_LIQ v1.1 腿的日度目标权重，用作第一段 OLS 回归项）。实测 3b288c832b956820af9802f02861af459e215e7d4097a6420724b26cf2d31c4d ✓。叶24 没有这个键。

## 5. 未定义名与先用后定义检查（因为 py_compile 连漏 4 版）
- 方法一：pyflakes 4.0.3（/tmp venv，只做语法分析）。方法二：自写 AST 检查，按顶层语句顺序递归进入 if/for/with/try，看模块级有没有先用后定义。两种方法结论一致。
| 文件 | sha | 模块级先用后定义 | pyflakes |
|---|---|---|---|
| 叶23 r2.7 | 3d094e22 | **无** | 3 条，全是误报：`parts`（L477 lambda `cat`）、`r0`（L778 lambda `ewf`）×2。lambda 引用的名字后来被 del，但每次调用都在 del 之前；两个函数的局部名每次进入都会重新绑定 |
| 叶24 r6 | 6e46c01c | **无** | 同类误报 3 条（L448 `parts`、L710 `r0`×2），另有 L709 `U` 赋值后未用（P3-7） |
| 叶23 r2.6 / 叶24 r5 | 60393573 / a2719e5c | **X2S、X2E（L92 / L80）** | 同上，另有 FIX5 的 `RR` 误报 |
| 历史版本 | r2.2 81c2b4e6 / r1 de87c839 | 无 | — |
| 历史版本 | r2.3 f011b277、r2.4 ccde59eb、r2.5 07c99873 / r2 6f57c82d、r3 101600f6、r4 1e8de734 | **都有 X2S/X2E** | — |
| CMC v1.1 r3：alpha_combo_marginal_v1_1.py | 5658f612 | 无 | 0 条 |
| alpha_hiliq_s8_paradigm_v1_1.py | 455fdf82 | 无 | 0 条 |
| alpha_v1_1_runguard.py | 35991407 | 无 | 0 条 |
| tests/test_alpha_v1_1_selftest.py | 6966a5d9 | 无 | 0 条 |
- 影响：OK_FIXED 在模块加载时就读 X2S/X2E，所以 r2.3–r2.6 和 r2–r5 一 import 就会 NameError，那时还没进 authorize，也没读任何数据。这是**安全方向**的失败：什么都没跑，只是这些版本根本跑不起来。FIX6 把 `X2S, X2E = "2024-06-03", "2026-10-09"` 移到 OK_FIXED 之前，值不变 ✓。
- **Arch 失误记录。** bd3abe5c、b09901f5、032cef56 三轮审查都只核 diff 和 py_compile，没有做未定义名检查。教训：以后每次代码审查都必须跑 pyflakes（/tmp venv）加模块级顺序 AST 检查，并把结果写进审查文档。
- 终版其余检查：内存中 compile 通过；**没有漏 f 前缀的字符串模板**。

## 6. 核查 (3)：披露字段与静态扫描（终版）
- 影子与主口径的 EW/wb 年化差在 pool_benchmarks 里计算，只经 diag 返回；evaluate 只把 diag 当 b3 透传 ✓。
- 字段：
  - 删除：`*_cut_delist_date`、`*_diff_vs_cut_delist_date`、`delisted_last_trade_nat_fallback`，以及返回键 `Mp_dd/wv_dd`。
  - 新增：`poolEW/wb_cagr244_primary_cut_delist_date`、`*_shadow_cut_last_trade_date`、`*_diff_primary_minus_shadow`、`delisted_missing_delist_date_outside_x2`、`delisted_master_max_delist_date`、`shadow_cut`、`shadow_note`。
  - FIX6 新增：`delisted_cut_names_x2`、`delisted_cut_name_days_x2_shadow_last_trade_date`、`delisted_cut_total_x2_shadow_last_trade_date`、`delisted_cut_names_x2_shadow_last_trade_date`。返回 dict 多了 `r0`。
- 下游：research/、scripts/、scripts_eng/、quantlab/、tests/、docs/、output/ai_factory/ 里引用旧名的代码只剩 `output/ai_factory/_drafts/` 的旧草稿（P3-4），其余是历史文档和旧扫描 json。**没有消费者会因改名出错。**
- 静态扫描在终版上复跑（disclosure 模式）：**668 个文件，55 处命中，0 违规**；PREEXISTING 21 处；ALLOWED_FUNC 34 处，两叶各 17 处，全部在 `pool_benchmarks` 内 ✓。
- 披露文字去掉了硬写的「约 8 名」，改为以运行时计数为准 ✓。文中「X2 窗内退市 93 名，其中 76 名两日期相差超过 1 天」引自 Alpha 486496a9，来源见 §9 的流程记录。它只是文字参考，不进任何计算。

## 7. 资源与数据范围
- 没有新增数据读取，也没有新增 2024-06 之前的读取。RR 复用 rr；PX 自 2024-05-20 起（T−1 用）、2018 起的 B3 递推、delisted_master、mask 都是已批准的原有读取。
- RSS 估算（Alpha R-1：evaluate 里同时有 rr 和 r0）：
  - rr ≈ 约 590 日 × 面板全部代码（约 5.5 千）× 8B ≈ 26MB；r0 ≈ 590 × |U|（约 6–7 千）× 8B ≈ 30–35MB。两者合计 ≈ 60MB。
  - 和 FIX5 比：FIX5 在函数里还要另建一份 pivot（RR）再算 r0，transient 是三份；r2.7/r6 少了一份，内存只减不增。和 r2.5/r4 比，增量 ≤ 约 35MB。
  - evaluate 的峰值主要来自 PX 长表、pivot_table 的临时拷贝和 B3 的逐年帧，rr/r0 只占小头。这一项**不可能让峰值越过 1.5GB**，定为 P3-8。看门狗 1536000 KB 不变，超限会 `os._exit(137)`（安全方向）。实测峰值以授权运行回执的 peak_rss_mb 为准。
- 其余依赖 sha 与 FIX4 草案一致：fund_resid 2b49b10b、selfcheck_v3 ecaa30d8、decay a877cec5、common 218b61cf、adj_price 93b54ae7、panel_stitch 043fa68d、moneyflow ca045076、nontextbook 8a56d136、capadv_leg 3b288c83。

## 8. 发现
### P2
- **P2-1｜两份叶脚本还没提交 git。** research/g1g5_sue_desens_cs_alpha.py 和 research/g1g5_imax_intraday_alpha.py 都是 `??`。按 v1.4 审查 f2edc099 P2-1 的同一标准：**AI 原样提交 r2.7（3d094e22…）和 r6（6e46c01c…）之前，叶 .ok 不签。** 只提交这两个文件，不跳过 hook；报 commit id，并报提交前、提交后、提交副本三处 sha。`research/alpha_combo_marginal_v1_1.py`（5658f612…）也没被 git 跟踪，由主 Agent 转告 Alpha，在签 CMC v1.1 全量 .ok 前提交。
### P3（不阻断）
- **P3-1｜`cmc_cmd_ok` 只做子串匹配。** 它拦不住 `--arch-ok-x` 这类写法，也不检查 `--arch-ok` 后面的路径；用 `\` 续行会被误拒（安全方向）。眼下的处理：Arch 写 .cmd 时，每条 CMC 命令只占一行，`--arch-ok` 后跟 CMC v1.1 全量 .ok 的绝对路径，行尾不加注释。下一版改用 shlex 分词，并校验 .ok 路径和 sha。
- **P3-2｜SD1 静态扫描关键词有盲点（设计假设复核）。** TOKENS 不含 `last_trade_date` 和 `delisted_master`。请 Eng 在下一版 checker 加上这两个词，并重做 PREEXISTING 基线，单独送审。
- **P3-3｜「缺退市日即停跑」可能被合法数据触发。** 例如窗口末仍在退市整理期、delist_date 还空着的名。另外 `cut[~index.duplicated()]` 只保留第一行，如果 ts_code 有重复，会触发 P2-1 断言停跑（安全方向）。签叶 .ok 前，请 Data 在自己的授权流程内只读报告两件事：delist_date 为空且 last_trade_date ≥ 2024-06-03 的名单；ts_code 重复数。
- **P3-4｜旧草稿残留。** `output/ai_factory/_drafts/leaf23_r2_6_draft.py`（3d17a6a9…）和 `leaf24_r5_draft.py`（11e70e39…）不是交付版，还用着旧字段名，而且在扫描范围之外。移进 `_recovery/ai/` 或删除。
- **P3-5｜`QL_X2_EXTEND_END`。** f98e408e 允许用这个环境变量放开 g1g5_x2_panel_stitch 的 X2_END，而 panel_stitch 在叶工具闭包里。所以叶 .cmd 的每条工具命令都要以 `env -u QL_X2_EXTEND_END` 开头，tool_run_log 的环境快照里不得出现这个变量。
- **P3-6｜回执补充（不改代码）。** 按 uni 逐一核对：diag 的 `*_primary_cut_delist_date` 必须等于 bench 的 `poolEW_cagr244` / `wb_cagr244`（同源计算，不等就报 Arch）。另外要报：主口径和影子口径的截断名数与名·日数、缺退市日名数、两口径差值，并写明「影子只披露，不进判定，不计家族次数」。
- **P3-7｜pyflakes 没有清零。** 剩下的误报（`parts`、`r0`：lambda 引用随后 del 的名字）和叶24 L709 的死变量 `U`，会让 pyflakes 没法直接当门槛用。下一版请把这两个 lambda 改成普通表达式或 def，删掉 L709 的 `U`，让 pyflakes 输出为 0。
- **P3-8｜evaluate 里同时有 rr 和 r0（约 60MB，见 §7）。** 下一版：叶24 在 pool_benchmarks 返回后马上 `del rr`；叶23 L786 用 `r0.index` 代替 `rr.index`，然后同样 del。

## 9. 流程记录（报主 Agent）
- Alpha 在 486496a9 里说明：曾「用自己的一行 pandas 只读了 delisted_master（339 行）」核对披露数字，没有 import 项目模块。规则「没有 Arch .ok 不得运行任何东西」是否覆盖这种不经项目代码的纯数据读取，需要主 Agent 明确裁定。在裁定之前，由此得到的 93/76 只作为叶说明里的文字参考，不进入任何计算或判定。

## 10. 以后签发时 .ok / .cmd 必须包含的内容（本轮**不签**）
### 10.1 两叶 .ok（各 54 个键，白名单由 AST 抽取；多一个、少一个都拒跑）
- 在 032cef56 §6.1/§6.2 的基础上改三处：
  - `script_sha256=3d094e22d3af3e3cfe4d3c6164fc3d817c93cb92edfc339db2a156981933adc1`（叶23 r2.7）/ `6e46c01cd7268aa549a8d900d78c434b017b25d3cea62c3340754264c4d85c05`（叶24 r6）
  - `dep_combo_sha256=5658f612fef313fc5b818fc4cb9d594d757377e0dbf7c7dc86a6e31788b88911`
  - **新增** `dep_combo_legacy_sha256=bee230199ac27bf9730aa77c63b104a67bb104229622c57524867a9b54a5c51c`
- 叶23 键：format, signed_by, leaf, mechanism_tag, scope, window_start, window_end, allow_full, allow_smoke, allow_sensitivity, allow_sealed, live, promotion, promotion_approved, script_sha256, prereg_sha256, cs_panel_dir, cs_panel_manifest_sha256, cs_panel_build_version, data_mask_sha256, data_delisted_sha256, data_forecast_sha256, data_financials_sha256, data_etf_daily_adj_sha256, dep_fe_sha256, dep_selfcheck_sha256, dep_combo_sha256, dep_combo_legacy_sha256, dep_adg_sha256, dep_lc_sha256, dep_l19_hiliq_sha256, dep_l19_fulla_sha256, dep_l20_hiliq_sha256, dep_l20_fulla_sha256, dep_l20w_hiliq_sha256, dep_l20w_fulla_sha256, dep_capadv600_tw_sha256, dep_capadv600_nav_sha256, dep_capadv1000_tw_sha256, dep_capadv1000_nav_sha256, dep_capadv_leg_sha256（=3b288c832b956820af9802f02861af459e215e7d4097a6420724b26cf2d31c4d）, tool_cmds_path, tool_cmds_sha256, tool_closure_adj_price_sha256, tool_closure_panel_stitch_sha256, tool_closure_moneyflow_sha256, tool_closure_nontextbook_sha256, out_dir, sensitivity_specs, serial_order, run_niceness, rss_limit_mb, issued_at, expires_et。
- 叶24 键：在上面的基础上去掉 data_forecast、data_financials、dep_l19*、dep_l20*、dep_capadv_leg；换成 dep_l18_hiliq/fulla、dep_l18v_hiliq/fulla、dep_l18w_hiliq/fulla、dep_l18vw_hiliq/fulla；另加 `research_only=true`。
- 固定值：live=false、promotion=false、promotion_approved=false、allow_full=true、allow_smoke=false、allow_sealed=false、scope=X2、window 2024-06-03..2026-10-09、rss_limit_mb=1500、run_niceness=10。prereg_sha256 = 8f5d8ac4…（叶23）/ c289e770…（叶24）。
- 签发时实测或填写：cs_panel_manifest_sha256；data_mask_sha256（必须等于 D1b 回执的 pins.mask_sha256）；data_delisted_sha256（FIX4 时为 63590f23…，签发时重测）；tool_cmds_sha256；issued_at、expires_et（带时区，expires_et 晚于 issued_at）。文件 LF、无 BOM、无行内注释，单次有效。
### 10.2 .cmd（`output/ai_factory/ARCH_TOOL_CMDS_LEAF23_X2.cmd` / `…LEAF24_X2.cmd`，由 Arch 写）
- 每条 CMC 命令只占一行：`cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 env -u QL_X2_EXTEND_END nice -n 10 python3 research/alpha_combo_marginal_v1_1.py --universe hiliq --base capadv --arch-ok <CMC v1.1 全量 .ok 绝对路径> …`
- legacy 对照可选，调用 `research/alpha_combo_marginal.py`，并注明只作对照列。不用续行，CMC 行不加行尾注释，其余工具命令同样以 `env -u QL_X2_EXTEND_END` 开头。

## 11. 签发次序（门槛）
1. AI 原样提交 r2.7 / r6（P2-1），Arch 核对 commit；Alpha 提交 CMC v1.1 r3 文件。
2. Alpha 用 selftest .ok（fa45bf7f…）跑 CMC v1.1 selftest → **Arch 审过回执** → Arch 签 CMC v1.1 全量 .ok。
3. Data 完成 cs_panel_v2_resumefix 重建（D1b execute）→ **Arch 审过回执**（manifest sha、pins.mask_sha256）。建议同时拿到 P3-3 的只读报告。
4. Arch 写两份 .cmd，签叶23 .ok。签前重测 SW 89d4afa3，并确认 Data 没有晋级任何表。
5. 叶23 按 fund → build_HILIQ → build_FULLA → eval（主口径）跑，每步回执审过才进下一步；再跑 4 个敏感性；然后叶24 同样串行。全程不与 Eng 对拍、Data 重任务或 Alpha selftest 并发。live=false。

live=false；promotion=false。本审查没有建任何 .ok 或 .cmd，没有运行任何叶脚本或测试，没有读取真实数据。
