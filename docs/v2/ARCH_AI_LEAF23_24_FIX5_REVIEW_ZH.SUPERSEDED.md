# Arch 审查：AI 叶23 r2.6 / 叶24 r5（FIX5）+ commit f98e408e 核验

- 审查人：QuantLab Arch；时间：2026-10-18 03:28–03:35 ET。上一轮：`docs/v2/ARCH_LEAF23_24_FIX4_RECHECK_ZH.md`（032cef56）。
- 依据：主 Agent 02:44（基准池主口径按退市日截断）、主 Agent 03:22（CMC v1.1 改钉修复后 sha）、Arch CMC v1.1 r3 审查 bbfcb7ef、SD1 规范 2e428f39 §3.6、v1.4 审查 f2edc099 P2-1。
- 方式：静态审查。只做 sha256sum、git show/diff-tree、在 /tmp 临时目录对存档 git apply、AST 解析（f 前缀扫描、.ok 键白名单抽取；只 ast.parse/compile 在内存，不写 .pyc）。唯一执行的是 `scripts_eng/sd1_pit_static_check.py --mode disclosure`：先确认它只用标准库（argparse/ast/hashlib/json/re/sys/pathlib）、不 import 任何项目代码、只读 SCOPE 下 .py 文本、只在 `--json` 时写文件，且 scripts_eng/ 下没有同名遮蔽标准库的文件；以 `python3 -I -B`、PYTHONDONTWRITEBYTECODE=1 运行，不带 --json，运行前后 __pycache__ 目录数均为 231。**没有运行、import 叶脚本或测试，没有读取任何真实数据，没有写 .ok 或 .cmd。** 临时目录已删除。
- live=false；promotion=false。

## 0. 结论
- **Part 1（commit f98e408e）：通过。** 关闭 v1.4 审查 f2edc099 的 P2-1；v1.4/D21 运行 .ok 不再因此受阻（其余前提不变）。
- **Part 2（FIX5）：代码层面通过——P0=0 / P1=0 / P2=1 / P3=6。** P2-1 只阻断 .ok 签发，不需要改代码（把两份叶脚本原样提交即可）。P3 都不阻断。
- 叶 .ok 和 .cmd **本轮不签不写**。签发顺序见 §9。

## 1. Part 1：commit f98e408e31a3aff5749c3a48e6578deb1168cb16
| 项 | 结果 |
|---|---|
| 分支 / HEAD | main，HEAD = f98e408e ✓ |
| 父提交 | fb48928db94b4b5fe025efbbc0097e741a63da65（上一个 HEAD，Track V/C 那次提交）✓ |
| 改动文件 | `git diff-tree` 只有 2 个：M research/ai_debate_memory_runner.py、M research/g1g5_x2_panel_stitch.py（+38/−1）✓ |
| 提交 blob sha | e1736d80c589ecd717731dc38ae99a52f3d448da9841b2c3794ee008f59613ea / 043fa68d4e6dd40f003db04fddfd79fb431c4a00f280a0a5db35cbe733d90620 ✓ |
| 工作区 sha | 与 blob 逐位一致，两文件 `git status` 干净 ✓ |
| 主干 | execution.py 373fed30…、`__init__.py` bfdfa63c… 未动 ✓ |
- 内容就是此前审过的两处：`_load_benchmark_closes_hfq`（只作自检）和 `load_adj_close_x2`（只作自检）；`X2_END` 默认仍冻结在 2026-10-09，只有设了环境变量 `QL_X2_EXTEND_END` 才放开（见 P3-5）。
- v1.4 审查第 102 行「nt_ai_debate_memory_runner_sha256 须等 AI 提交后复核」：现可填 e1736d80…（签 v1.4/D21 .ok 时仍要实测）。

## 2. Part 2：文件定位与补丁复现
- 叶23 = `research/g1g5_sue_desens_cs_alpha.py`：60393573925a84399f27c430009b3e5dc7c575b52e24cd36ed6c31ba73484bce ✓（前一版 07c998737647…，存档一致）。
- 叶24 = `research/g1g5_imax_intraday_alpha.py`：a2719e5c0778d3f1b912b8ecb553689b50476bea1498c6829f797262e15f84ba ✓（前一版 1e8de734080f…，存档一致）。
- diff `docs/v2/AI_LEAF23_24_FIX5_DIFF.patch` 6138dce5fbe90d9773f8ac3397787855f24632d1c9f7d670a75dcb7068777d2f ✓（379 行）。在 /tmp 对 `_recovery/ai/pre_fix5_0325/` 两份存档 `git apply --check` + apply 后，**逐位复现**两个新 sha ✓。
- 预注册未改：叶23 `AI_G1G5_SUE_DESENS_WHO_PAYS_PREREG_R2_1_ZH.md` 8f5d8ac4…，叶24 `AI_G1G5_IMAX_OVERNIGHT_WHO_PAYS_PREREG_ZH.md` c289e770… ✓。`output/ai_factory/prereg_sha_leaf23/24.txt` 对存档只有追加和「current→superseded」标注 ✓。
- 编译：内存中 compile 两文件通过；AST 扫描**没有漏 f 前缀的字符串模板**（既不在 f-string 里、也不走 .format 却含 `{name}` 的常量：0 处）。
- 改动范围：两叶对称，逐 hunk 只涉及 ①退市截断口径 ②CMC 路径与 .ok 键 ③披露差值挪进 pool_benchmarks ④注释/说明文字。风格集、选股、记账、判定 t、阶段链、停跑条件（除已删项）都没动。

## 3. 核查 (1)：退市截断与 PIT
### 3.1 代码与说法一致
- 主口径 `cut = delist_date`，不回退（删除了 `.fillna(last_trade_date)`）✓。
- `gone = d > cut`；`carry = (~has) & (mask suspended) & ~gone`。最后交易日之后到退市日之间：面板无行、mask 停牌 → 沿用 S 和停牌前市值；收益在 evaluate 里 `rr.reindex(...).fillna(0.0)` 记 0，成员仍在 Mp 分母 ✓（预注册「停牌记 0、不剔分母」）。
- P2-1 断言 `gone_full` 用同一个 `cut`（退市日），在 X2 全部日上独立重建；`(S & gone_full).any()` 即停跑 ✓。
- 缺退市日：`no_delist_date` 中凡在 U 且 X2 内有成员日或面板行的，`SystemExit` 停跑；其余列入 `delisted_missing_delist_date_outside_x2` 只披露；没有任何回退到 last_trade_date 的路径 ✓。
- 影子 `cut_dd = last_trade_date`，只驱动 S_dd/MV_dd → Mp_dd/wv_dd → 只写进 diag 的三个影子字段，Mp_dd/wv_dd 在函数内 del，不再返回 ✓。

### 3.2 信息日期逐项追踪
| 用途 | 输入的信息日期 | 结论 |
|---|---|---|
| 主口径截断 S=False（d > delist_date），Mp = S.shift(1) | 退市日当天已公开 | 无前瞻 |
| (last_trade_date, delist_date] 沿用、收益 0 | 每天只用「当天没有成交、mask 停牌」 | 无前瞻 |
| 影子截断（d > last_trade_date） | 事后才确知「那是最后一笔」 | 有轻微前瞻，**只披露**，不进判定、不计家族次数 ✓ |
| 缺退市日停跑、P2-1 断言、end_after 列表 | 用到全窗口事后信息 | 只是完整性检查和披露，不改变任何成员或权重 ✓ |
- **不进选股。** pool_benchmarks 只在 evaluate 中调用一次（叶23 L767 / 叶24 L699）；Mp/wv 只用于池 EW / wb 基准和 N4 剔除占比，在建书前 `del`（叶23 L787）。build 阶段（α、gate）和 pick_book 不读 delisted_master。所以退市日只用于基准收益的事后记账，属 SD1 规范允许的「记账层」用途。

### 3.3 与 SD1 guard（StrategyLayerDelistAccess）的关系
- 叶子**没有**调用 `quantlab/platform/delist_accounting` 的任何 loader（若调用，运行时会抛 StrategyLayerDelistAccess，静态扫描也会把 `delist_accounting` 记为违规）。
- 叶子直接 `pd.read_parquet(data/v2/delisted/delisted_master_tushare.parquet)`，这张表不在 guard 的 loader 覆盖范围内。依据是 `sd1_pit_static_check.py` 的 FUNC_WHITELIST：只允许这两个文件的 `pool_benchmarks` 函数内出现退市字段（主 Agent 02:44；Arch 2b8f81c9 §6.1-3）。这是授权的例外，**不算绕过**。
- 读取点只有一处：两叶各在 `pool_benchmarks` 内 `repin_file` 后读一次；模块级只有路径常量 `DELISTED` 和 sha 钉（TOOLS / panel_recheck 只算 sha，不读内容）。我逐行 grep 了 `DELISTED|last_trade_date|delisted|delist`，确认没有其他读取。
- 设计假设复核：这条防线对「直接读表」只靠静态扫描，而扫描的关键词表有盲点（见 P3-2）。

## 4. 核查 (2)：CMC 路径与 .ok 键
- `TOOLS["dep_combo_sha256"] → research/alpha_combo_marginal_v1_1.py`（实测 5658f612fef313fc5b818fc4cb9d594d757377e0dbf7c7dc86a6e31788b88911 ✓，= Arch r3 审查 bbfcb7ef 批准版）。新增 `TOOLS["dep_combo_legacy_sha256"] → research/alpha_combo_marginal.py`（实测 bee230199ac27bf9730aa77c63b104a67bb104229622c57524867a9b54a5c51c ✓）。叶23 L74 / 叶24 L62 位置一致 ✓。
- 严格性：
  - 白名单 = OK_FIXED ∪ OK_REQUIRED ∪ TOOLS ∪ TOOL_CLOSURE。.ok 多一个键拒跑，少一个键也拒跑，所以 `dep_combo_legacy_sha256` 是必填 ✓。
  - 两层比对：.ok 值 == 脚本常量 `CMC_V11_SHA` / `CMC_LEGACY_SHA`，**并且** == 文件实测 sha。任一不符即拒跑 ✓。改常量会改变 script_sha256，所以无法单方面绕过 ✓。
  - `.cmd` 检查 `cmc_cmd_ok(TOOL_CMDS)`：非注释行里至少有一行调 `alpha_combo_marginal_v1_1.py`，且每一行都带 `--arch-ok`；`.cmd` 本身也由 tool_cmds_sha256 钉住 ✓。
  - 时机：全部在 `authorize()` 里，早于 `verify_panel`（第一次读 parquet）、process_check、`import research.g1g5_fund_resid_alpha`（在各阶段函数内）。模块级只 import 了 numpy/pandas（第三方库，不读数据）✓。
- 局限：`cmc_cmd_ok` 只做子串匹配（见 P3-1）。因为 .cmd 由 Arch 编写并钉 sha，目前不构成可利用的漏洞。
- **CMC v1.1 双层授权**：v1.1 自己 `--arch-ok` 必填，并由 runguard `enforce(modes=["full"])` 检查。所以叶子的 .cmd 必须指向一张**单独签发的 CMC v1.1 全量 .ok**。这张 .ok 要等 Alpha selftest（.ok fa45bf7f39dc…，单次有效）的回执经 Arch 审过才签。这是叶全量的前置门槛（流程门槛，叶脚本不检查）。

## 5. 核查 (3)：披露字段与静态扫描
- 影子与主口径的 EW/wb 年化差现在在 pool_benchmarks 末尾计算（`RR = PX.pivot(ret).reindex(idx, U).fillna(0)`，与 evaluate 的 `r0` 同源、同索引）。只经 diag 返回，evaluate 只把 diag 当 b3 透传，不碰退市字段 ✓。
- b3 字段改名：删除 `*_cut_delist_date`、`*_diff_vs_cut_delist_date`、`delisted_last_trade_nat_fallback` 和返回键 `Mp_dd/wv_dd`；新增 `poolEW/wb_cagr244_primary_cut_delist_date`、`*_shadow_cut_last_trade_date`、`*_diff_primary_minus_shadow`、`delisted_missing_delist_date_outside_x2`、`delisted_master_max_delist_date`、`shadow_cut`、`shadow_note` ✓。
- 下游：research/、scripts/、scripts_eng/、quantlab/、tests/、docs/、output/ai_factory/ 下引用旧名的**代码只剩** `output/ai_factory/_drafts/` 里的旧草稿（见 P3-4），其余是历史审查文档和 SD1 旧扫描 json。**没有消费者会因改名而出错**。两叶内部也不再引用 `pb["Mp_dd"]` ✓。
- 静态扫描复跑（disclosure 模式）：**668 个文件，55 处命中，0 违规**，21 处 PREEXISTING，34 处 ALLOWED_FUNC，即两叶各 17 处，全部在 `pool_benchmarks` 内 ✓。与 AI 的说法一致。

## 6. 资源与数据范围
- RSS：新增 RR ≈ 590 日 × |U|（约 6–7 千名）× 8B ≈ 30MB，乘法临时帧合计 ≤约 120MB，函数内释放；同时 Mp_dd/wv_dd 不再带回 evaluate，所以 evaluate 的常驻量与 r2.5/r4 基本持平。远低于 1.5GB，看门狗（1536000 KB）不变。实测峰值以授权运行回执的 peak_rss 为准。
- 数据范围：**没有新的数据读取**。RR 复用已加载的 PX（自 2024-05-20，用于 T−1，与原版相同）。2018 起的 B3 递推、delisted_master、mask 都是已批准的原有读取。**没有新增 2024-06 前的读取。**
- 其余依赖的 sha 与 FIX4 草案一致：fund_resid 2b49b10b、selfcheck_v3 ecaa30d8、decay a877cec5、common 218b61cf、adj_price 93b54ae7、panel_stitch 043fa68d、moneyflow ca045076、nontextbook 8a56d136。

## 7. 发现
### P2
- **P2-1｜两份叶脚本仍未提交 git。** `git status` 显示 research/g1g5_sue_desens_cs_alpha.py、research/g1g5_imax_intraday_alpha.py 都是 `??`。按 v1.4 审查 f2edc099 P2-1 的同一标准：**AI 把 r2.6（60393573…）和 r5（a2719e5c…）原样提交之前，叶 .ok 不签。** 只提交这两个文件，不跳过 hook，提交后报 commit id，并报提交前、提交后、提交副本三处 sha。不改代码。同理，`research/alpha_combo_marginal_v1_1.py`（5658f612…）也未跟踪，由主 Agent 转 Alpha，在签 CMC v1.1 全量 .ok 前提交。

### P3（不阻断）
- **P3-1｜`cmc_cmd_ok` 只做子串匹配。** 它不能拒绝 `--arch-ok-x` 这样的写法，也不检查 `--arch-ok` 后面跟的路径。如果命令用 `\` 续行，会误判拒跑（这是安全方向）。处理：Arch 写 .cmd 时，每条 CMC 命令只写一行，`--arch-ok` 后跟 CMC v1.1 全量 .ok 的绝对路径，行尾不加注释。下一版可改用 shlex 分词，校验 `--arch-ok` 的值等于指定 .ok，且该 .ok 的 sha 已钉。
- **P3-2｜SD1 静态扫描关键词有盲点（设计假设复核）。** TOKENS 只有 `stock_delisted|delist_date|delist_events|delist_accounting`，不含 `last_trade_date`、`delisted_master`。所以只读 last_trade_date 的直接读表扫不出来。本轮人工 grep 确认两叶没有这种情况。建议 Eng 在下一版 checker 加入这两个词，并重做 PREEXISTING 基线（单独审，不影响 SD1 本轮结论）。
- **P3-3｜缺退市日停跑可能被合法数据触发。** 例如 10-09 时仍在退市整理期、delist_date 还是空的名。另外 `cut[~index.duplicated()]` 只保留首行：若有重新上市造成的重复 ts_code，会取到任意一行，结果是 P2-1 断言停跑（安全方向，但会浪费一次授权）。建议签叶 .ok 前请 Data 只读报告：delisted_master 中 delist_date 为空、且 last_trade_date ≥ 2024-06-03 的名数及名单；ts_code 重复数。
- **P3-4｜旧草稿残留。** `output/ai_factory/_drafts/leaf23_r2_6_draft.py`（3d17a6a9…）和 `leaf24_r5_draft.py`（11e70e39…）文件名带「r2_6/r5」，但不是交付版：sha 不同，还在用旧字段名。它们在静态扫描 SCOPE 之外，也没有 sha 钉。请 AI 移进 `_recovery/ai/` 或删除；.cmd 永不引用。
- **P3-5｜`QL_X2_EXTEND_END` 环境变量。** commit f98e408e 让 g1g5_x2_panel_stitch 的 X2_END 可以被环境变量放开，而它在叶工具闭包里（moneyflow/nontextbook 会 import）。叶 .cmd 的每条工具命令都要以 `env -u QL_X2_EXTEND_END` 开头；运行者在 tool_run_log 里记录环境快照，其中不得出现该变量。
- **P3-6｜回执补充（不改代码）。** 回执要逐 uni 核对：diag 的 `poolEW_cagr244_primary_cut_delist_date` 与 `wb_cagr244_primary_cut_delist_date` 必须分别等于 bench 的 `poolEW_cagr244` / `wb_cagr244`（同源计算，不等即报 Arch）。同时报：`delisted_missing_delist_date_outside_x2` 名数、`delisted_cut_total_x2`、影子与主口径差值，并写明「影子只披露，不进判定，不计家族次数」。

## 8. 以后签发时 .ok / .cmd 必须包含的内容（本轮**不签**）
### 8.1 两叶 .ok 键（各 54 个，白名单由 AST 从脚本抽取；多一个、少一个都拒跑）
- 在 FIX4 复核 032cef56 §6.1/§6.2 的基础上改三处：
  - `script_sha256=60393573925a84399f27c430009b3e5dc7c575b52e24cd36ed6c31ba73484bce`（叶23）/ `a2719e5c0778d3f1b912b8ecb553689b50476bea1498c6829f797262e15f84ba`（叶24）
  - `dep_combo_sha256=5658f612fef313fc5b818fc4cb9d594d757377e0dbf7c7dc86a6e31788b88911`
  - **新增** `dep_combo_legacy_sha256=bee230199ac27bf9730aa77c63b104a67bb104229622c57524867a9b54a5c51c`
- 叶23 键：format, signed_by, leaf, mechanism_tag, scope, window_start, window_end, allow_full, allow_smoke, allow_sensitivity, allow_sealed, live, promotion, promotion_approved, script_sha256, prereg_sha256, cs_panel_dir, cs_panel_manifest_sha256, cs_panel_build_version, data_mask_sha256, data_delisted_sha256, data_forecast_sha256, data_financials_sha256, data_etf_daily_adj_sha256, dep_fe_sha256, dep_selfcheck_sha256, dep_combo_sha256, dep_combo_legacy_sha256, dep_adg_sha256, dep_lc_sha256, dep_l19_hiliq_sha256, dep_l19_fulla_sha256, dep_l20_hiliq_sha256, dep_l20_fulla_sha256, dep_l20w_hiliq_sha256, dep_l20w_fulla_sha256, dep_capadv600_tw_sha256, dep_capadv600_nav_sha256, dep_capadv1000_tw_sha256, dep_capadv1000_nav_sha256, dep_capadv_leg_sha256, tool_cmds_path, tool_cmds_sha256, tool_closure_adj_price_sha256, tool_closure_panel_stitch_sha256, tool_closure_moneyflow_sha256, tool_closure_nontextbook_sha256, out_dir, sensitivity_specs, serial_order, run_niceness, rss_limit_mb, issued_at, expires_et。
- 叶24 键：同上，但去掉 data_forecast/data_financials/dep_l19*/dep_l20*/dep_capadv_leg，换成 dep_l18_hiliq/fulla、dep_l18v_hiliq/fulla、dep_l18w_hiliq/fulla、dep_l18vw_hiliq/fulla，并加 `research_only=true`。
- 固定值不变：live=false、promotion=false、promotion_approved=false、allow_full=true、allow_smoke=false、allow_sealed=false、scope=X2、window 2024-06-03..2026-10-09、rss_limit_mb=1500、run_niceness=10。
- 签发时实测或填写：cs_panel_manifest_sha256、data_mask_sha256（= D1b 回执 pins.mask_sha256）、data_delisted_sha256（本审时未重测；FIX4 时为 63590f23…）、tool_cmds_sha256、issued_at、expires_et（带时区，且晚于 issued_at）。格式：LF、无 BOM、无行内注释，单次有效。
### 8.2 .cmd（`output/ai_factory/ARCH_TOOL_CMDS_LEAF23_X2.cmd` / `…LEAF24_X2.cmd`，由 Arch 写）
- 每条 CMC 命令一行：`cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 env -u QL_X2_EXTEND_END nice -n 10 python3 research/alpha_combo_marginal_v1_1.py --universe hiliq --base capadv --arch-ok <CMC v1.1 全量 .ok 绝对路径> …`
- legacy 对照（可选）调用 `research/alpha_combo_marginal.py`，并在命令旁写明只作对照列。
- 不用续行，CMC 行不加行尾注释；其余工具命令同样带 `env -u QL_X2_EXTEND_END`。

## 9. 签发次序（门槛）
1. AI 原样提交叶23 r2.6 / 叶24 r5（P2-1），Arch 核 commit。Alpha 提交 CMC v1.1 r3 文件。
2. Alpha 按 selftest .ok（fa45bf7f…）跑 CMC v1.1 selftest → **Arch 审过回执** → Arch 签 CMC v1.1 全量 .ok。
3. Data cs_panel_v2_resumefix 重建（D1b execute）完成 → **Arch 审过回执**（manifest sha、pins.mask_sha256）。建议同时拿到 P3-3 的只读报告。
4. Arch 写两份 .cmd，再签叶23 .ok（重测 SW 89d4afa3、确认 Data 没有晋级任何表）。
5. 叶23：fund → build_HILIQ → build_FULLA → eval（主口径），每步回执审过才进下一步 → 4 个敏感性 → 叶24 同样串行。全程不与 Eng 对拍、Data 重任务、Alpha selftest 并发。live=false。

live=false；promotion=false。本审查没有建任何 .ok 或 .cmd，没有运行任何叶脚本或测试，没有读取真实数据。
