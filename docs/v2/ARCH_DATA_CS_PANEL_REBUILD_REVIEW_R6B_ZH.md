# Arch 复审 r6b · Data cs_panel 复牌重建（SD1 D1–D4）

- 时间：2026-10-18 02:35 ET；审查人：QuantLab Arch；live=false，promotion=false
- 结论：**有条件通过：放行 v3 四步 dry-run 与合成单测**。P0=0，P1=0，P2=3，P3=9。三项 P2 都不阻塞 dry-run，但 P2-2 必须在 execute 之前修好。execute 仍未授权，需另签 execute .ok，并带两个期望值键。
- 本轮做法：静态审查，没有运行任何 Data 脚本或单测，也没有读取行情内容。只做了三件事：计算 sha；对比 r5 与 r6b 快照的 diff；把 sd1_common 的常量用 AST 取出、按 parse_run_auth 的规则自行校验新 .ok（没有 import sd1_common）。数据 pin 只计算文件 sha，没有解析内容。

## 1. sha 核对（7/7 一致）
现行文件、Data 申报值、快照 `_recovery/data/sd1_r6b_20261018/SHA256SUMS` 三方一致，`sha256sum -c` 结果全部 OK。

| 文件 | sha256 |
|---|---|
| scripts/fix_sd1/build_cs_panel_v2_resumefix.py | 4b40b6b8b43eef4511aea07343c439a7691dfb23bcf89113432946c5dfb4cd21 |
| scripts/fix_sd1/build_suspend_flags_v2.py | 53013099315348fd21a12673270aebca2204810f5868653eed22ad4c5e69ce73 |
| scripts/fix_sd1/build_stock_delisted_v2.py | a641626f42defe2d2ece3b7457ecfa76fac40e460387483dcdcd885e87f0d732 |
| scripts/fix_sd1/sd1_common.py | c275e15250942553529cc101d8302ec641f0b216150649e0a118a71a4b7d07fa |
| scripts/fix_sd1/test_sd1_common.py | 892401e5ec99e6471f5aa3a18ab68bf9adcd2c28cd1b9cc868f95cbb8cbed32f |
| docs/v2/DATA_CS_PANEL_RESUME_REBUILD_PLAN_ZH.md | 362e323994d3e40181ee2f26da3864c5fdf4720c0b1f1a5e35b095652eec3bbe |
| docs/v2/DATA_SUSPEND_DELIST_FIX_PLAN_ZH.md | dd84efe8ff63ae3657d99d31ac3bb39927e80c458df69033bc56012093bf492a |

- 三个 build 脚本里硬编码的 COMMON_SHA256 都是 c275e152，与实测一致。
- 15 个数据 pin（mask、v1 cs_panel 2018–2026、float_mktcap、sw_l1、stock_delisted v1、namechange_all、delisted_daily）在 02:3x 重新计算，全部等于 v2.ok 的值，各文件 mtime 都早于 01:15。
- 四个目标输出不存在，也没有 staging 或 VOID 残留。
- 关于 Data 申报的「6 个 sha」：.ok 的 PIN_CODE 正好是 6 项，即两份方案文档、三个脚本和 common。test 文件不在 PIN_CODE 里，它的 sha 记在 v3.ok 的 test_sd1_common_sha256（仅供参考），由 selftest .ok 负责钉住。

## 2. r5 → r6b 逐项审查
### 2.1 cs_panel（D1b）
- 相对 r5，diff 只有 COMMON_SHA256 这一行，D1b 的逻辑与 r5 逐位相同。sd1_common.ResumeState 和 classify_restore 也没有改动。
- 结论：D1b 不受影响。v3 下 D1a、D1b 的 dry-run 统计必须与 v2 dry-run 回执逐项相同，唯一的新增是 RUN_CONDITION_MATCHES 行。

### 2.2 门禁（common，对照 02:21 裁定）
| 裁定 | 实现 | 判定 |
|---|---|---|
| nightly_update.py、tier3_daily_snapshot.py 存在即拒 | 已加入 FORBID_PATTERNS；命中即判 forbid，不看进程状态 | ✓ |
| relay_outage_backfill 仅 state==T 放行 | STOPPED_OK_PATTERNS；状态取自 `/proc/<pid>/stat` 中最后一个 `)` 之后的字段，comm 含空格或括号也不会解析错；t（tracing stop）判拒 | ✓ |
| 豁免时先剔除 scripts/fix_sd1/ 再匹配 | `probe = cmd.replace(SELF_EXEMPT, "")`。如果 fix_sd1 命令行里另有禁词，仍然拒 | ✓ |
| pid、state、cmdline 写入 stdout 和 manifest | 所有模式都打印 RUN_CONDITION_MATCHES，并写入 rc.forbid_matches → manifest.run_conditions | ✓ |
| expires_et 必填、带偏移，到期即拒 | 写在 AUTH_REQUIRED 里；正则要求带偏移；`now >= exp` 即拒；用 aware datetime 比较，时区换算正确（Python 3.13） | ✓ |
| FIXED.run_forbid_concurrent 新值 | 与申请字符串逐字一致 | ✓ |

- 门禁顺序：parse（含到期检查）→ mode → 代码 sha → 输出目录 → 序列顺序 → 进程检查 → 数据 sha。读数据之前的所有检查都放在前面。
- 单测覆盖：expires 缺失、过期、非 ISO 三种情况，到期边界（差 1 秒放行、正好到期即拒），以及 classify_procs 9 个用例。这些用例与裁定一致。

### 2.3 D2（对照探针 9b81bff1 的 P2-A/P3）
- **.BJ 规则**：`bj_drop = {c ∈ res : c 以 .BJ 结尾，且 c ∉ R(t)，且 c ∉ prev_full}`。
  - prev_full 是上一个遍历日的全天 S 集合。遍历日来自 raw daily 文件列表，也就是交易日序列；D2 的 days_walked=2128 在 execute 验收中核对。所以「前一交易日」的口径正确。
  - 「全天 S」的定义是 `suspend_type=="S"` 且 timing 为空，与 ResumeState 的 fullday_S 用同一个变量 `full`。
  - 两个集合都只用到 t−1 及之前的信息（更新放在循环末尾），没有前视。
- **全 A 口径**：没有按 mask 过滤。✓
- **ResumeState 未改动**：过滤只作用在 step 的返回值上，不回写内部状态，因此 D1b 不受影响。✓
- **resume_evidence**：判定优先级 R > S_prev > gap_S > none。`s_since_trade = (s_since_trade ∪ full) − vol_pos`，在当日判定之后才更新。✓
- **断言**：逐年与 35 两个断言都只统计非 BJ。
  - 统计和断言都放在 `if EXEC` 写盘之前，不符即 ST.void。execute 时删除 staging 并写 VOID 文件，dry-run 时只中止。
  - stats 会先打印再断言，所以 VOID 时数字仍可查。✓
- **table_rows**：只打印。bj_resume_rows_kept 逐条列出；bj_resume_dropped_missing_row_only 只给总数。

### 2.4 D3D4（对照 02:25 裁定 (a)）
- **parse_d3d4_expectations**：
  - dry-run 时两个键可以缺省；execute 时缺任一键即 SystemExit。拒跑发生在 `C.Staging` 和第一次 read_parquet 之前，此时没有 staging 目录，也没有 VOID 文件。
  - 代码格式校验、去空格、拒绝重复、排序后按集合比较，都已实现，单测覆盖了缺省、给出、execute 缺键、格式错误、重复几种情况。✓
- **D3D4_FACE_CHECK**：
  - 已实现：双向差集；每只代码「整理期前 20 个收盘价」窗口的起止日、个数、最高收盘价、v1/v2 类别和 face_flag；UNKNOWN 与 56 的对账。
  - 窗口函数与 fv() 用同一过滤条件 `z.d < delist_period_start`。✓
- **断言**：face 集合与 unknown_count 不符即 VOID，在写盘之前执行。v3 不写这两个键，所以 dry-run 只打印。✓
- **manual_override == {002509.SZ}**：已实现，但是静态断言，见 P2-2。

## 3. 发现
- **P2-1（流程，94403）**：Data 方案 r6-WIP 原文写的是「94403 的 STOP/CONT 安排（需用户同意后执行）」。
  - 本轮 Arch 实测 ps（只读，02:3x ET）：
    - tier3 1015 的 142531、142545 都已退出；
    - 94403 `relay_outage_backfill.py` 处于 Ss 状态，在跑；
    - 它的子进程 212762 `nightly_update.py --date 20261016 --steps sw` 正在运行。
  - 要求：
    - 如果「用户同意」还没有取得，先由主 Agent 确认，未确认前不得 STOP。门禁会拒跑，这是安全的一侧。
    - STOP 之后，必须等子进程 nightly_update 自然结束，不得杀。只要子进程还在，门禁就会拒（nightly_update.py 任何状态都拒），这是正确行为。
- **P2-2（D3D4，execute 前必修）**：`set(MANUAL_OVERRIDE) != {"002509.SZ"}` 检查的是常量字典，恒为假，不能证明覆盖真的生效。
  - 第 58 行只在 namechange 缺起点时才覆盖。
  - 第 61 行写 source 和 verified 字段时却不判断 k，即使没有覆盖也会把 override_source_verified 置为 True。
  - execute 版须改为：断言 `x.loc[x.delist_period_source=="manual_override","ts_code"]` 恰为 {002509.SZ}，并且 source 字段只写在 k 行。
  - 本次 dry-run 期间，用 FACE_CHECK 中 002509 的 period_start 是否为 20200604 作为替代核对。
- **P2-3（流程）**：方案第 4 步写的是「串行跑 D1b → D2 → D3D4 的 execute」，一个 STOP 窗口内连续跑完。这与「上一步回执经 Arch 审过才可开下一步」的规则冲突。
  - dry-run 和 execute 都必须逐步跑，每步之间等 Arch 审回执。v3.ok 的 step_gate 键已写明这一点。
- **P3-1**：parse_d3d4_expectations 在 gate 之后调用。gate 里的 enforce_inputs 已经对 3 个数据文件计算过 sha（读了字节，但没有解析内容）。裁定的本意（解析数据前拒跑）满足，但建议把它移进 gate，放在 run_conditions 之前。
- **P3-2**：face_value_recategorised_codes 取的是「v2 类别 == 面值退市」的所有行。这个口径成立的前提是 v1 没有面值类，诊断 D-3 指出 v1 的 reason() 没有面值规则。建议改为 `(v1==MERGER) & (v2==面值)`。如果 dry-run 的 face_minus_diag4 非空，先按这一点排查。
- **P3-3**：BJ 剔除行数只给了总数，建议拆成 gap_S 和 none 两类。审回执时按以下关系对账：
  - 探针给出的 BJ 无 R 行为 12,134，它们在整个成交间隔内都没有 S。预期 bj_resume_dropped_missing_row_only ≥ 12,134。
  - 预期 table_rows = 111,480（= 123,614 − 12,134）。
  - 偏差都要逐条解释。
  - 探针文档第 139 行写的「采用掩码限定时」措辞不准。全 A 加 BJ 规则下预期同样是 111,480，以本条为准。
- **P3-4**：BJ 规则只写在 D2 里，没有单测。D1b 与 D2 的复牌定义因此分成两处，目前一致只是因为 mask 里没有 BJ。建议在 D1b 加断言「mask 中 .BJ 数 = 0」；以后把这条规则收进 common 的纯函数并补单测。
- **P3-5**：进程检查只在 gate 开头做一次，有 TOCTOU 窗口。D1b 和 D2 在结尾重算 raw_content，可以兜住 raw 被改的情况；D3D4 的输入有 sha 钉住。建议 execute 在 commit 前再跑一次 classify_procs，并写入 manifest。
- **P3-6**：cmdline 按子串匹配。
  - 假阳性：其他 agent 的 shell 里有 `rg nightly_update.py` 这类命令时会拒跑，属于安全的一侧，重试即可。
  - 假阴性：`python -m ...` 形式或改名的包装脚本匹配不到。目前实测的调用都是 `scripts/xxx.py` 形式，可以覆盖。
  - 另一个 fix_sd1 实例并发运行时不会被拦（run_serial 没有机器强制，r5 起就有这个问题）。
- **P3-7**：expires_et 如果是格式合法但不存在的日期，fromisoformat 会抛 ValueError，而不是 SystemExit，但同样拒跑。到期只在启动时检查，运行中跨过到期时间不会中止，可以接受。
- **P3-8**：test_sd1_common.py 把 selftest .ok 的路径硬编码为 ARCH_RUN_AUTH_SELFTEST_SD1_COMMON.ok，换文件名就读不到。所以本轮在原路径原子替换，旧版（7a0c1cdc）归档到 output/data/_superseded/。
- **P3-9**：期望值键为空串时等同缺省，因此 execute 无法表达「面值集合为空」。按诊断有 4 只，不影响本次使用。

## 4. 设计假设复核
1. **「daily 缺行 = 停牌」只对沪深成立**：探针显示沪深 35 行缺 R 都是真实复牌，成立。
2. **BJ 只看 t−1 的全天 S**：Tushare suspend_d 在停牌期间每天都有 S 记录，真实的全天停牌在结束前一日必有 S。gap_S 型（S 在中段中断）按薄交易处理。is_resume_day 只用于披露和禁止新买，BJ 不在 HI_LIQ 掩码和纸面轨里，影响仅限研究口径，可以接受。
3. **逐年期望值硬编码**：这些值来自 Arch 用同一 raw 快照独立复现的结果。如果 94403 等回填改动了截止日前的 raw，计数可能变化，会触发 VOID（fail-closed）。须同时比对 raw_content 哈希与 v2 dry-run 是否相同，以区分是数据变了还是代码有问题。
4. **面值规则**：取进入整理期前最后 20 个有成交的收盘价，全部 <1。停牌日不计入，与交易所「连续 20 个交易日」的口径一致。只对合并或私有化类改归类，其余类别不动，属于有意的限定范围。
5. **UNKNOWN = 60 − 4 = 56**：以 dry-run 实测为准，再写进 execute .ok。

## 5. 94403 处理（Arch 裁定，取最简单且安全的方案）
1. 前提：主 Agent 已确认取得用户同意（见 P2-1）。
2. 在第一个 v3 dry-run 的 gate 之前 `kill -STOP 94403`。
3. 等子进程 nightly_update 自然结束，ps 中不再出现 nightly_update.py 或 tier3_daily_snapshot.py。
4. 从 D1a 到 D3D4 四步 dry-run 期间（含每步之间等 Arch 审回执的时间），94403 一直保持 T 状态。
5. D3D4 dry-run 结束后立即 `kill -CONT 94403`。不要等 execute .ok，因为 execute 的签发时间不确定，回填不宜长时间冻结；10-19 纸面轨优先。
6. execute 前重新 STOP，按 execute .ok 另行规定。
7. 每次 STOP 和 CONT 的时刻都要写进回执，并附 ps 快照。
8. 如果主 Agent 判定 10-19 纸面轨需要 94403 尽快跑完，可以在两步之间 CONT，下一步 gate 之前再 STOP。由门禁验证 T 状态。

## 6. 已签 .ok
| 文件 | sha256 | 要点 |
|---|---|---|
| output/data/ARCH_RUN_AUTH_CS_PANEL_RESUMEFIX_v3.ok | dac5f6dd7ee6e011101a6201db7a1b113d8fb1f12f8824711da86787ba2b2124 | 仅 dry-run，四步；allow_full/execute/smoke/selftest=false；6 个代码 pin 为 r6b、数据 pin 沿用 v2；run_forbid_concurrent 为新值；不含期望值键；supersedes v2 cc04d83d；ok_revision=v3_r6b_dryrun_only；version 按解析器 FIXED 仍写 cs_panel_resumefix_v1；expires 2026-10-19T02:31:43-04:00；step_gate 和 94403 策略写入键中 |
| output/data/ARCH_RUN_AUTH_SELFTEST_SD1_COMMON.ok（原路径替换） | a7159eca51dcf65a769b420039ff194aab6d48520dfda3e04a9c71ab46276959 | scope=selftest；runner 892401e5、dep c275e152；allow_real_data=false；out_dir=mkdtemp；supersedes 7a0c1cdc（已归档 output/data/_superseded/ARCH_RUN_AUTH_SELFTEST_SD1_COMMON.r5_7a0c1cdc.ok）；expires 同上 |

两份文件都是 LF、无 BOM、无行内注释，所有 allow_* 都显式写出，live=false，promotion=false，写入方式为原子写（tmp + rename）。v2.ok 钉的是旧代码，已自然失效。

## 7. 下一步与验收
- 顺序：合成单测 → D1a dry-run → Arch 审 → D1b → Arch 审 → D2 → Arch 审 → D3D4 → Arch 审。stdout 落盘到 docs/v2/audit/data_cs_panel_v3_dryrun/。
- D1a、D1b：统计须与 v2 dry-run 回执逐项相同，峰值 RSS 不超过 1450MB。
- D2：
  - 两个断言通过；
  - 35 行逐条披露；
  - bj_dropped 与 table_rows 按 P3-3 对账；
  - raw_content 与 v2 相同。
- D3D4：
  - FACE_CHECK 双向差集和 4 只窗口；
  - 002509 的 period_start=20200604；
  - UNKNOWN 与 56 对账。
  - Arch 审定后签 execute .ok，写入 expected_face_value_recategorised 和 expected_unknown_needs_source_count。在此之前须先修 P2-2，并重跑 D3D4 dry-run。
