# cs_panel 复牌首日缺行：重建方案 r5（回应 Arch 审核 r4）

QuantLab Data，最后修改 2026-10-18 02:05 EDT（以文件 mtime 为准，不写未来时间）。状态 DRAFT。D1a dry-run 已在 r4 .ok（3a1bb537…）下跑完：PASS，9 年 v1 逐位一致，峰值 RSS 1241MB；stdout 存于 docs/v2/audit/data_cs_panel_d1a_dryrun/d1a_dryrun_stdout_20261018.txt（48a3da22…）。D1b/D2/D3D4 的 dry-run 等 Arch 重签。
回应的审核文档：r2 docs/v2/ARCH_DATA_CS_PANEL_REBUILD_REVIEW_ZH.md（530f53cd…）、r3 docs/v2/ARCH_DATA_CS_PANEL_REBUILD_REVIEW_R3_ZH.md（4cd19c94…）。r3 起，没有 .ok 不运行任何 SD1 脚本，也不做任何自测；自测需要 .ok 里写 allow_selftest=true。
本轮没有运行任何真实数据的 dry-run 或重建。上轮未经 .ok 跑了 dry-run（r2 P2-1），Data 记为流程违规，那些数字一律作废，只以授权后的回执为准。
live=false，promotion_approved=false，strategy_promotion=false。

## 0. 根因
`research/ai_cs_panel_build.py` 只保留冻结 HI_LIQ 掩码中 fulla|in_universe 为真的行。掩码 `research/strategy_hiliq_universe_v1.py:148` 定义 `suspended = suspend_d S | ~bar_prev`，复牌首日因此必然被判为停牌，这一行就被丢掉了。各项计数在 .ok 之后由脚本按 §5 的定义自行产出，不再沿用"4971 次中应补 2865"的说法。

## 1. 文件（共享模块按 sha 传递钉定）
- `scripts/fix_sd1/sd1_common.py`：门禁（照抄 tie-sens 的 parse/enforce/check_out_dir 并扩展）、Staging/VOID、共用复牌定义 `ResumeState`。三个脚本各自硬编码它的 sha256，在 import 之前校验，不一致即拒跑。
- `scripts/fix_sd1/build_cs_panel_v2_resumefix.py`：`--arch-ok PATH --fixes none|resume [--execute]`。none 对应步骤 D1a，resume 对应步骤 D1b。
- `scripts/fix_sd1/test_sd1_common.py`：单元测试，只用合成数据，不读真实数据。

## 2. 逐条回应 r2 的 P1 和 P2
**P1-1 门禁**。所有模式都要过 `--arch-ok`，dry-run 要求 allow_dryrun=true，--execute 要求 allow_full=true，allow_smoke 必须为 false。
- 解析：只认 `^[a-z0-9_]+=value$` 行；键重复、缺失或为空都拒跑。AUTH_REQUIRED 与 r2 §6 逐字一致，固定值逐个校验，not_authorized 必须包含 §6 列出的 9 项。
- 检查顺序：
  1. 解析 .ok；
  2. 校验模式开关；
  3. 复算 5 个代码和方案文件的 sha（两份方案、三个脚本）；
  4. 输出目录：不存在或为空目录才放行；D3D4 的目标文件已存在、或残留 staging 目录，都拒跑；
  5. 步骤顺序：后序步骤已有产出算乱序，拒跑；前一步的 RECEIPT 缺失、状态不是 PASS、生成时用的 .ok sha 或 5 个钉定 sha 与本次不同，都拒跑；
  6. 复算数据输入的 sha：掩码、v1 cs_panel 9 年、float_mktcap、sw_l1、stock_delisted v1、namechange_all、delisted_daily。
- 第 6 步之前不读任何数据，全部通过后才打印 GATE_PASS。自测见 output/diag/arch_gate_selftest_20261018.txt。

**P1-2 一致性断言（D1a）**。2018–2026 逐年断言 `DataFrame.equals(v1)` 和 `pa.Table.equals(v1 表)` 都为真。任何一年 v1 文件缺失或不相等，就写 VOID、非零退出，整个目录不提交。执行模式下逐年记录两边文件的 sha 和 bytes_equal；bytes_equal 为 false 时，在 manifest 里记录 parquet 元数据差异（created_by、schema、kv 元数据）。
D1b 逐年断言：v1 行缺失为 0，v1 值改动为 0，补回行的 hiliq 和 fulla 都是 False，且 rows = rows_v1 + restored。任何一条不满足都 VOID。

**P1-3 fulla 不变**。已删掉 `fulla |= is_resume_day & elig`，hiliq 和 fulla 恒等于掩码原定义。新增两个记账列：
- `hiliq_carry`：复牌前最后一个有成交、且掩码未判停牌的交易日，该股 in_universe 为真；
- `fulla_carry`：同一天该股 fulla_v1 为真。
保留行的条件改为 keep = v1_keep ∨ (补回候选 ∧ (hiliq_carry ∨ fulla_carry))。新增 `row_origin`（v1 或 restored）。
603007.SH 2026-04-21 是摘帽复牌：复牌前一天 st=T，所以 fulla_carry=F、hiliq_carry=F，不会被补回。

**P1-5 统一复牌定义**：`ResumeState`，cs_panel 和 suspend_flags_v2 共用同一实现。
is_resume_day(c,t) 要同时满足：
- 当日 vol>0；
- 当日没有全天 S；
- 该股此前在数据里有过成交，或者首个交易日掩码 young=False（即已上市满 60 个交易日）。这样排除了新股首日和此前从未成交的代码；
- t 不是首个数据日 2018-01-02（P2-3：这一天一律记 False，避免 3,252 行伪复牌）；
- 前一交易日 amount≤0（与掩码 bar_prev 同口径），或者当日有 R 记录。
盘中 S（前一日有成交、当日无 R）不算复牌（P2-4），这类行由 restore_reason=intraday_halt 加 carry 列记账保留。

**P1-6 原子落盘（r4 补 r3 P2-2）**。Staging 创建之后的全部代码，包括 sw、ind_names、逐年循环、manifest、RECEIPT、commit，都包在同一个 try 里，任何异常都写 VOID。残留 staging 即视为中断：下次运行会被门禁拒绝，须人工 VOID。dry-run 出错只中止、不写 VOID 文件，因为 dry-run 没有写过任何东西（r3 P3-2，定为这一口径）。先写 `<out>.staging_<ts>/`，全部年份、manifest、RECEIPT 都写完再 rename 成正式目录。中途异常、RSS 超过 1.5GB 或 MemAvailable 低于 2GB，都会删掉 staging 并写 `<out>.VOID_<ts>.md`，然后中止（不是暂停，P3-2）。目标已存在就拒跑。ind_names.csv 必须与 v1 同名文件 sha 一致，否则 VOID。

**P2-2 串行顺序**：D1a → D1b → D2 → D3D4。每步写 manifest 和 RECEIPT_<step>.json，下一步的门禁检查它。启动前人工确认 `ps` 里没有其他研究任务；整个流程排在 fund_portfolio 和 broker_recommend 合并之前。

**P2-5 carry 跨年延续（r4 按 Arch r3 P1-1 改写，r5 按 r4 P2-1/P2-2 再改）**：state 从 2018-01-02 起逐日延续到 2026，不再用"年初往前 60 天"的窗口。
- 判定逻辑抽成纯函数 `sd1_common.classify_restore`，只对补回候选行（掩码判停牌、当日有成交、v1 未保留、无全天 S、复牌或盘中停牌）生效：
  - carry 状态存在：carry_state='known'，按 carry 值补回；
  - `unknown_pre_data`：种子代码，且数据里在 t 之前没有任何 vol>0 的日子；
  - `unknown_no_normal_session`：t 之前有过成交，但成交日全被掩码判停牌；
  - `unknown_first_trade_in_data`：非种子代码，数据内第一次成交就是盘中停牌日（新股首日临时停牌）；
  - 三类 unknown 一律不补回，按 v1 处理。
- 不变式（违反即 VOID）：unknown_pre_data 必须属于种子集合，且 2021 年及以后为 0；非种子代码没有任何前序成交却被判为复牌，也属于违反。
- manifest 逐年按"事件类型（复牌/盘中停牌）× 标签"分列 unknown 行数，并列出 5 个样本。Arch 探针预期：
  - 2018 年 293 行：复牌 217、盘中 76；纯种子 288、有成交无正常日 5；
  - 2019 年 143 行：复牌 2、盘中 141；纯种子 138、有成交无正常日 5；
  - 2020 年复牌 2 行。
- 回执单列这些行数，抽样 3 只（含 000032.SZ 2018-01-03）。
- 单测已覆盖 classify_restore 的各个分支（合成数据），按 selftest 规范先 enforce 后 import，等 Arch 签 selftest .ok 后再运行。

**P2-6 两个新列**：补回行加 `prev_traded_date`（复牌前最后一个有成交日）和 `halt_sessions`（中间停了几个交易日）。

**r3 P2-1 raw 内容钉定**：manifest 和 RECEIPT 新增 `raw_content`。它的算法是：把截止日（掩码最后交易日，现为 20261014）之前的所有 raw daily 和 suspend_d 文件逐个算 sha，按 `子目录/文件名:sha` 排序拼接后再取一次 sha。D1a、D1b、D2 三步各自在开工时算一次，与上一步 RECEIPT 中的值比对，不一致即中止；收尾时再算一次，与开工时不一致就 VOID。重建期间禁止运行往 raw 写数据的 nightly 步骤（daily_pull、tier1_pull、adj_factor、bars）。门禁会扫描 ps，发现这类进程或任何 research/ 进程就 FAIL。
**r4 P2-3 dry-run 覆盖面**：dry-run 模式下 check_order 和 raw_pin_start 跳过前序 RECEIPT 比对，但仍检查后序步骤的输出必须不存在。这样 D1b、D2、D3D4 都能先做 dry-run。execute 模式下照旧，前序 RECEIPT 必须为 PASS 且 ok_sha256 一致。
**r4 P3**：
- 回执写明每步都是单进程运行。run_serial 没有代码强制：命令行含 fix_sd1 的进程，冲突扫描会放过。
- 回执核对 D1b 的 manifest.sessions_walked 等于 D2 的 manifest.days_walked。
- 所有运行命令都加 `PYTHONDONTWRITEBYTECODE=1`，例如：`PYTHONDONTWRITEBYTECODE=1 nice -n 10 python3 scripts/fix_sd1/<script> --arch-ok <ok> ...`。
**r3 P2-4 运行条件自证**：.ok 新增强制键 run_niceness=10、run_serial=true、run_after、run_forbid_concurrent，门禁逐字校验。门禁在开工时记录 `os.nice(0)` 和 ps 快照（python 和 nightly 进程），niceness 不等于 10，或者有冲突进程（research/、daily_pull、tier1_pull、tier1_materialize、adj_factor、bars_materialize，不含 fix_sd1 自身），就 FAIL 退出。这些信息写进 manifest 和 RECEIPT 的 run_conditions 字段。运行命令一律用 `nice -n 10`，每次只跑一步。
**r3 P3-3**：RSS 和可用内存守卫，除年边界外，年内每 20 个交易日也检查一次（D2 同样每 20 日）。
**r3 P3-5**：门禁校验 signed_et 为带时区偏移的 ISO8601；allow_selftest 是可选键，出现时必须精确为 true 或 false。common_sha256 已成为必填钉定键。
**P2-8 manifest**：记录 .ok 路径和 sha、全部钉定 sha、common sha、前一步 RECEIPT 的 sha、raw daily 加 suspend_d 文件清单的哈希。逐年记录：rows、rows_v1、rows_added、v1_rows_missing_in_v2、v1_value_mismatch（D1a 记 v1_frame_equals、v1_table_equals、bytes_equal）、restored、restored_by_reason、restored_hiliq_carry、restored_fulla_carry、resume_events_all_mask_rows、true_resume_eligible_2865_basis、intraday_halt_rows_all、rss_mb、sha256、v1_sha256。

**P3-1**：时间戳已改为实际时间；诊断文档里的过期句随本轮一并更正（诊断文档不在钉定范围内）。
**P3-4**：回执抽样增加 unknown_pre_data 样本 3 只（含 000032.SZ 2018-01-03），以及 603007.SH 2026-04-21（应不补回）和 300658.SZ 2026-01-19（跨年 carry）。

## 3. 列口径（按 Arch 裁定）
| 列 | 定义 | available_at（上海时间）| 用途 |
|---|---|---|---|
| hiliq, fulla | 掩码原定义，补回行为 False | ≤t 盘前 | 选股和池定义（与 v1 相同）|
| is_resume_day | 见 P1-5 | t 16:00（要用当日 vol）| 只用于披露和当日禁止新买入；引擎盘前用 suspend_flags_v2.resume_announced（t 09:00）|
| intraday_halt | 当日有 S 且 suspend_timing 非空 | t 09:00 | 披露 |
| hiliq_carry, fulla_carry | 见 P1-3 | t 16:00 | **只用于记账**：停牌期间按原权重持有，停牌日收益记 0，复牌日按 close/pre_close 入账。叶评价用 hiliq_carry，全市场池用 fulla_carry。不得用于当日选股或池定义 |
| row_origin, restore_reason, carry_state | v1 或 restored；resume 或 intraday_halt；known、unknown_pre_data 或空 | — | 留痕 |
| prev_traded_date, halt_sessions | 补回行和复牌行 | t 16:00 | 引擎把复牌收益挂回停牌前的持仓 |
| ret, ret_on | close/pre_close−1 和 open/pre_close−1（与 v1 相同）| t 16:00 | 记账 |

**消费方须知**：池必须按 hiliq/fulla 过滤，不能以"这一行存在"作池；记账列不得进入信号。影响到的 research 脚本：leaf_selfcheck_v3、ai_hiliq_pool_review_x2、ai_hiliq_sec8_supplement、ai_capadv_neutral_gap_diag、ai_eqinc_sec8_reconcile、alpha_eqinc_recon_ai_repro、alpha_s8_errata_fullsleeve_b_v41、g1g5_fund_resid_alpha。叶 15–22 是否重算由 Arch 评估。掩码脚本和掩码产物都不改，纸面轨不受影响，v1 panel_cache 不覆盖（⑤）。

## 4. 资源与耗时
按年分块读，进程 RSS 上限 1.5GB，可用内存低于 2GB 就中止。D1a 预计约 3 分钟。D1b 要逐日推进 state，预计约 5 分钟。

## 5. 回执（每步一份，.ok 之后由脚本产出）
回执 docs/v2/DATA_CS_PANEL_RESUME_REBUILD_RECEIPT_ZH.md 逐年列出 r2 §3 表的各列，每个数都写明定义：
- 掩码口径的 is_resume_day；
- 其中盘中 S 的行数；
- 真复牌且合格（即 2865 口径）；
- 实际补回数，按 resume 和 intraday_halt 分开；
- hiliq_carry 和 fulla_carry 计数；
- 2018-01-02 被强制记为 False 的情况，单列披露；
- X2 窗口内 702 次复牌的补回数；
- R 记录口径（4971）的定义和闭合说明。
抽样至少 12 个，ret 与原始 daily 一致到 1e-6：002445.SZ 2026-03-09、002090.SZ 2025-07-23、300658.SZ 2026-01-19、603007.SH 2026-04-21（应不补回）、002445.SZ 2026-08-24，再加随机 7 个。

## 5b. 回执模板附节：为什么 2018 年 FULLA 补回远多于 HI_LIQ（分析写在这里，数值等真跑后填）
Arch 探针显示，2018 年 fulla_carry 补回约 990 行，hiliq_carry 约 296 行。原因：
1. FULLA 门槛只是非 ST、非次新、adv20 不低于 300 万元；HI_LIQ 要求 adv20 不低于 1 亿元。复牌股停牌前多半流动性一般，满足 FULLA 但不满足 HI_LIQ 的占大多数。
2. 2018 年停复牌密集，而且长停牌多（股权质押风险期）。长停牌股停牌前的 adv20 往往已经下滑，跌出 HI_LIQ 的更多。
3. 两个 carry 取的都是"复牌前最后一个正常交易日"的掩码状态，口径一致，差额完全来自池子宽窄，不是漏判。
回执里填：各年的 restored_fulla_carry、restored_hiliq_carry、两者之差；差额部分按 adv20 分档（300 万到 1 亿、1 亿以上但其他原因不在 HI_LIQ）列出分布；抽样 3 只"只有 fulla_carry"的行，展示它停牌前的 adv20。

## 6. D-2、D-3、D-4 如何接入 SD1（⑥）
见 docs/v2/DATA_SUSPEND_DELIST_FIX_PLAN_ZH.md：suspend_flags_v2 的 join 键是 (instrument_id, trade_date)，stock_delisted_v2 的 join 键是 ts_code。

## 7. 定稿 sha256
定稿后不再修改；如需修改，会重算 sha 并在此注明。本文件自身的 sha 见送审消息。
| 文件 | sha256 |
|---|---|
| scripts/fix_sd1/build_cs_panel_v2_resumefix.py（script_cs_panel_sha256）| 11316ed4cb5fe37f9055006386709924853ad710f9d1031efcd79f90351be094 |
| scripts/fix_sd1/build_suspend_flags_v2.py（script_suspend_flags_sha256）| aeb46679a5c015c52498266cdf91b53b4ff61c61ab1deb3efad21860c29db988 |
| scripts/fix_sd1/build_stock_delisted_v2.py（script_stock_delisted_sha256）| 092330cc6b09457a92b71c89e77ee7dd912a76c8675325b5557085228da1f144 |
| scripts/fix_sd1/sd1_common.py（common_sha256；三个脚本内也硬编码）| 28fbb15de59103b8b7e87c68e9477b8f037383a617c1bffc54a6808928921263 |
| docs/v2/DATA_SUSPEND_DELIST_FIX_PLAN_ZH.md（plan_sd_fix_sha256）| 9691b90e1364cbc920c7c145098caa2be205127cab584f1a4d1084fba1b5d378 |
| scripts/fix_sd1/test_sd1_common.py（selftest .ok 的 runner_sha256_test_sd1_common）| 74a176e7d3e2727afa2ce86578b7b4a02c17a997cc0277499827844b8432c502 |

## r6-WIP（02:22 EDT，未送签；等 Arch 的 is_resume_day 探针结论，可能还要改 D2，届时一并报 sha）
- **门禁禁止名单**（Arch 02:21 定版，sd1_common.FORBID_PATTERNS / classify_procs）：
  - nightly_update.py、tier3_daily_snapshot.py：只要进程存在就拒跑，不论处于什么状态。
  - relay_outage_backfill：只有 /proc/<pid>/stat 的 state == T 才放行，其他状态都拒跑。
  - 原有禁止项保留：research/、daily_pull、tier1_pull、tier1_materialize、adj_factor、bars_materialize。
  - 豁免规则：先从命令行里去掉 scripts/fix_sd1/ 这段路径，再做匹配。
  - 每一次放行或拒绝，都把 pid、state、cmdline 打印到 stdout（RUN_CONDITION_MATCHES 行，所有模式都打印），并写进 manifest 的 run_conditions.forbid_matches。
- **expires_et 自检**：expires_et 改为必填字段，须为带时区偏移的 ISO8601；当前时间不早于过期时间即拒跑（Arch r5 P3-2）。
- **94403 的 STOP/CONT 安排**（需用户同意后执行）：
  1. 确认 nightly_update.py 和 tier3 进程都已自然结束，不杀。
  2. 执行 kill -STOP 94403，记录时刻和 ps 快照。
  3. 门禁会看到 94403 处于 T 状态，放行并记录。
  4. 串行跑 D1b → D2 → D3D4 的 execute。
  5. 执行 kill -CONT 94403，记录时刻。
  6. 以上四个时刻都写进 execute 回执。
- **execute 各步 manifest 验收项**：
  - D1b：sessions_walked = D2 的 days_walked。
  - D2：
    - 125 行逐行对账（asof_extend 中 tradestatus=0 且 vol>0 的行都应为 conflict_v1=True）；
    - days_walked = 2128；
    - raw_content 哈希 = D1b 的值。
  - D3D4：
    - recategorised 中的面值类应含 600297/002505/000861/002509；
    - unknown_needs_source 对账 56；
    - 进入退市整理期 89→151，拆成 d4_zero_day_fixed_codes（61 只 0 天修正）、entered_newly_codes_other（其余新增）、entered_lost_codes 三部分，逐一解释。
- **D3D4 输出（Arch P2-1）**：
  - dry-run 不再把清单打印成 "..."，改为打印 counts 和完整代码清单；manifest.stats 内容相同。
  - 断言：manual_override 必须恰为 002509.SZ，否则 VOID。
  - 面值四只、UNKNOWN==56 的断言暂未写入，原因见 Data 报告中的疑问。
