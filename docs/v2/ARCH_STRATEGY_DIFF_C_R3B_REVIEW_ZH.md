# Arch 审查：Strategy DIFF C r3b（申万 L1 as-of 交易日空档沿用 + CLEAN 默认表）

- 审查人：QuantLab Arch。只做静态审查：没有运行或 import 项目代码，没有跑 pytest，没有读任何 parquet 的值（只读了 3 个 parquet 的 schema 和 footer 行数，以及 sw_l1_pit/manifest.json 元数据），没有改动真实仓库，没有写 .ok，没有给任何 agent 发消息。
- 时间：2026-10-18T10:55:05-04:00（ET，取自 `date`）
- 被审对象：docs/v2/audit/STRATEGY_SW_PIT_ASOF_TRADEDAY_PROPOSAL_20261018_r3b.diff，sha256 913e683082cfd63707f314cc4bd5f5166854cc787d685c1560a3e29cd891f5ae（实测一致），1683 行，07:22 ET 生成。它是 C r3（02bee140，从未审）的完整替代，基线是 DIFF B r2（d0fb1d3f）落地后的状态。
- 方法：HEAD 0ec38296 用 git archive 导出到 /tmp/arch_c3b_bm40Ec/w（set -euo pipefail，cd 后核对 pwd），先打 B r2，再打 C r3b，两次 `git apply --check` 都通过。真实仓库没有 apply。
- 背景材料：B r2 审查 c72f0856（ARCH_STRATEGY_SW_PIT_ASOF_FIX_R2_REVIEW_ZH.md，L74 主规则）；C / C r2 审查 28eabd35（ARCH_STRATEGY_SW_PIT_ASOF_TRADEDAY_C_REVIEW_ZH.md，L7 主 Agent 06:01 裁定）；Strategy 的 READ_LOG 2571956e、STRATEGY_SW_LOOKAHEAD_P3_ADDENDUM_20261018.md；r3b 文件头 L1–L87 的逐条说明。C r3 没有单独的 Arch 审查，本次按累计改动（B r2 → C r3b）一并审。

## 结论：PASS（有条件）

P0=0，P1=0。P2 两条：P2-1 沿用（日历 pin 续期，现在多了一个 2026-12-31 的硬期限），P2-2 新增（CLEAN 表的非 A 股代码写法占位，落地前必须由 Data 补齐）。P3 十条。
- 主规则、空档沿用、日历参数化和越界报错，按字面实现正确，边界情况逐条核对通过（见第 3 节）。
- 改动的 5 个文件都不在纸面冻结闭包里，也没有任何冻结模块 import 它们；89d4afa3 只被读取。**落地不必等 10-19 纸面跑完**，但不得落在 10-19 16:40–18:40 ET 窗口内，且要先满足第 8 节的条件。
- 叶25 冻结的前置条件：本 diff（或因 P2-2 出的 r3c）落地、selftest 53 passed 回执经 Arch 审过，叶25 预注册钉落地后的 sw_members_asof sha。

## 1. sha 链 ✔

| 文件 | HEAD | B r2 之后 | C r3b 之后（实测） | 申报 |
|---|---|---|---|---|
| research/sw_members_asof.py | 不存在 | 0444d9d6 | e1adef52bee577b9ea70af60fc7323a3c7ab9765e78e1873b1927c5a1fc88897 | 一致 |
| research/tests_sw_pit/test_sw_members_asof.py | 不存在 | 4f468b48 | 9943b412aafdf0ac22eb03350c79479c15f95e674ccb0e2d56caa78bf4a768a7 | 一致 |
| research/strategy_hiliq_capadv_b4_x2.py（hx2） | 1c51531a | 1728c126 | b867ee1560df5926d37aef8f2c95087c1186eac1ccbb6fa3733dea599c22df9e | 一致 |
| research/strategy_fulla_b4_x2.py（fulla） | 7bd657ed | 88b6f367 | 3ed5a8ddc0d165c91c9893a95c90a25c91f60a7632cde5f507d5c6b2d01379ed | 一致 |
| docs/v2/STRATEGY_SW_PIT_ASOF_FIX_PREREG_ZH.md | 不存在 | c2b37127 | 9db7cd143bb9891f1044becd13305a586432f282658f368c72db856f6a559856 | 一致 |
| research/sw_pit_freshness.py / test_sw_pit_freshness.py | 5191997e / cee59fc5 | 不变 | 不变 | 一致 |

- 真实仓库里 hx2、fulla 仍是 HEAD 版本（1c51531a / 7bd657ed），sw_members_asof.py 不存在：B r2 还没落地，也没有签过它的 code-change .ok（output 和 docs 下没有对应 .ok）。所以落地必须是“先 B r2、再 C r3b”两步。
- 数据 pin 实测：trade_cal_sse_pit.parquet fa4260b8…8a41 ✔；CLEAN industry_members_sw_l1_tushare.parquet 89d4afa3…f66c ✔；legacy sw_pit 0b1d3432…89f6 ✔；sw_l1_pit/manifest.json 0493991c。
- 静态检查（Strategy 在静默窗口内没做，文件头 L4–L5 自报）：py_compile 4 个 .py 全部通过（cfile 写在 /tmp，工作树没有 __pycache__）；pyflakes（/tmp/pf，4.0.3）只有基线遗留的两条（hx2 L669 charts2、fulla L180 nav_path），新代码 0 条；merge_asof 在 4 个文件里 0 处。

## 2. 以前的发现是否都已关闭

| 来源 | 发现 | r3b 状态（行号为 r3b 落地后的文件行号） |
|---|---|---|
| c72f0856 P3-1 | d−1 改为上一个 SSE 交易日 | ✔ 关闭：l1_asof L431、L437 |
| c72f0856 P3-2a | in_date 无法解析的行不能沿用 | ✔ sw_members_asof L436 |
| c72f0856 P3-2b | 无后继沿用要单独披露 | ✔ L443–L447 n_rows_gap_carry_no_successor |
| c72f0856 P3-3 | 写 summary 前抛异常时没有 VOID.md | 仍开（P3 可选，由 run .ok 条款兜底；pitfix 已暂停） |
| c72f0856 P3-4 | prereg 引用 1545/1109 | ✔ prereg L32 已改 |
| c72f0856 P3-5 | guard 测试 | ✔（C 已补） |
| c72f0856 P3-6 | 基线 assert | 仍开（hx2 main L562 `assert p.exists()`，基线遗留，不在本次范围） |
| c72f0856 P3-8 | EOF 空行 | B r2 仍有该告警，C 系列已去掉，落地后无残留 |
| 28eabd35 P2-1 | 日历 pin 写死、2027 续期 | **仍开**，文件头 L11 自认未处理，见本文 P2-1 |
| 28eabd35 P3-1 | docstring [ns] | ✔ L106 已写 [us] |
| 28eabd35 P3-2 | d 必须是开市日 | ✔ L120–L124 require_open |
| 28eabd35 P3-3 | NaT session | ✔ L113–L114（prev_open）、L405–L409（两条路径都拒绝） |
| 28eabd35 P3-4 | 测试缺口（工作日节假日、match=、非开市日） | ✔ C r2 已补，r3b 保留 |
| 28eabd35 P3-5 | fulla 显式传 cal | ✔ fulla L271–L275 |
| 28eabd35 P3-7 | 候选行 in_date ≤ out_date | ✔ L436 |
| 28eabd35 P3-r2-1 | 纯规则 NaT session 被静默当成未知 | ✔ L405–L409，纯规则也报错；有测试 test_pure_rule_nat_session_raises |
| 28eabd35 P3-r2-2 | 超长 docstring、reclass_share 说明 | ✔ L1–L2 拆行，reclass_share docstring L516–L520 |
| 主 Agent 06:49 | 重叠默认 raise、研究轨 count、pitfix 暂停、必报字段 | ✔ ON_OVERLAP_CHOICES、_check_on_overlap、hx2 L54 / fulla L35 count、PITFIX_PAUSED、sw_pit_required(_ok) |
| Arch 07:16 #1 | CLEAN 列和 dtype 常量 | ✔ 已和真实文件 schema 核对一致（见 3.7）；L168–L172 |
| Arch 07:16 #2 | norm_code 白名单 | 已实现（L177–L179、L185–L195），但非 A 股写法是占位，见 P2-2 |
| Arch 07:16 #3 | pitfix allow .ok | 已实现（hx2 L798–L822），字段名待定，见 P3-4 |

## 3. 规则与边界情况

主规则（l1_asof L411–L412）：`in_date < d` 且（out_date 为空或 `out_date >= d`），d 先 normalize。✔
空档沿用（L429–L447）：d 无有效行时，候选旧行要求 in_date 已解析、out_date 非空、in_date ≤ out_date，且 `prev_open(d) <= out_date < d`；只沿用 d 当天，不要求后继行。✔
日历：gap_carry 不传 cal 直接报错（L398–L399、IndustryAsOf L492–L494）；load_trade_cal 单次读字节、核 fa4260b8（L131–L138）；prev_open 依次拒绝 NaT、越界、非开市日、之前无开市日（L105–L128）；没有任何退回自然日的分支。✔

1. **d 是节后第一个开市日**：prev_open(d) 是节前最后一个开市日，窗口覆盖整个假期，out_date 落在节前最后一天或假期内的都会沿用 1 天。下一个 session 的 prev_open 就是 d，大于 out_date，所以最多 1 个交易日。✔ 有测试 test_weekday_holiday_carry_after_holiday。
2. **out_date 落在非开市日**：下一个开市日 d 满足 prev_open(d) ≤ out_date < d，会沿用，并计入 n_rows_gap_carry_out_on_closed_day（L442）。真实 legacy 表中这类行全部早于 2005-01-01，已在 28eabd35 核过。✔
3. **多条重叠**：默认 on_overlap="raise"，按 (code,d) 计，有 >1 条有效行就报错并列出代码（L413–L418）；hx2、fulla 都显式用 "count"，按 OVERLAP_TIEBREAK（in_date 最新 → is_new=Y → out_date 空 → 文件后序）取一条并披露 overlap_codes。✔ 但空档沿用的多候选不受 on_overlap 约束，见 P3-1。
4. **同日出/进**：旧 out=D、新 in=D。d=D 时只有旧行有效；d=下一个开市日时只有新行有效。没有空档，也不会沿用。✔ 新 in_date 早于旧 out_date 的属于重叠，走第 3 条。
5. **重复行**：完全相同的两行在 d 日都有效，raise 模式下会报错（即使 l1_name 相同）；count 模式下 conflict=false。见 P3-2。
6. **in_date 为空或无法解析**：prep_sw 解析成 NaT，NaT < d 恒为 False，永不有效；沿用候选也排除（L436）；无法解析的计入 n_in_unparsed。out_date 无法解析直接报错（prep_sw）。✔ CLEAN 的 in_date 本身是 timestamp[us]，只可能为空，不会无法解析。in_date > out_date 的行被静默忽略，没有表级计数，见 P3-3。
7. **dtype / tz / 精度**：
   - session 一律 `astype(str).str[:10]` 后 to_datetime（errors="coerce"），NaT 报错。我在 qlvenv（pandas 3.0.6）实测：字符串、YYYYMMDD 整数、date 对象、带 tz 的 Timestamp 都得到 datetime64[us]，带 tz 的取当地日期；同一列格式不一致时后面的变 NaT 并报错，属于 fail-closed。
   - CLEAN 真实 schema（只读 footer）：instrument_id/sw_code/sw_name/source/quality_status/schema/is_new 是 large_string，in_date/out_date/available_at 是 timestamp[us]（无 tz），revision 是 int64，共 11 列，pandas 元数据版本 3.0.6，无索引列，行数 7920（等于 manifest metrics.rows）。pandas 3.0.6 读 large_string 得到 "str"，timestamp[us] 得到 "datetime64[us]"（已用合成文件实测），所以 SW_L1_CLEAN_COLUMNS 与真实文件一致。schema 检查会拒绝 ns 精度和带 tz 的列（有测试），属于严格 fail-closed；v2 换表时要一起改（文件头 L75–L78 已列）。
   - 日历解析结果是 datetime64[us]，session 也是 [us]，searchsorted 同单位。us/ns 混用的比较在 28eabd35 已实测正确。
   - 代码键：CLEAN 路径的 ts_code 是 object，keys 一侧是 pandas 3 的 str；我实测两者 merge 正常命中。
   - 没有 merge_asof，所以不存在 merge_asof 对 dtype/排序的严格要求问题。
8. **日历覆盖边界**：日历覆盖 2005-01-01..2026-12-31。session 越界、2005-01-04 之前无开市日都报错。另外 CLEAN 的表检查 _completed_open_day 用当前墙钟时间（L263、L303）：上海日期一旦超过日历末日就报错，与查询的 as_of 无关，见 P2-1。

## 4. 调用方

- **本 diff 改动的调用方只有 hx2 和 fulla**：
  - hx2：load_industry_asof（L119 起）读 CLEAN（默认）→ sw_l1_table_check → IndustryAsOf(cal=, on_overlap="count")；smallcap_and_industry 和 main 都经它并核 pin；pitfix 固定读 legacy 表、legacy pin，且需要 allow .ok。
  - fulla：smallcap_and_industry L271–L278 同样改为 CLEAN + 表检查 + count，并核 pin 89d4afa3。
- **不变的 importer**：
  - strategy_b4_hiliq_leg_review.py 和 tie-sens 用 hx2.load_industry_map。它在 L104–L114 硬编码读 legacy 路径，没有用 SW_L1_REL，所以 SW_L1_REL 改成 CLEAN 不影响它们。✔ import hx2 时会多 import zoneinfo，qlvenv 和 ql-enrich-venv 都能加载 America/New_York、Asia/Shanghai。
  - optimizer_core_x2_run.py L382 仍在 raise SystemExit 之后，是死代码。
- **仓库里其他私有 SW as-of 实现（本 diff 不改，口径各不相同）**：用 rg 在 research、quantlab、scripts_eng、scripts 下找到 50 个含 in_date/out_date 过滤或同名函数的文件（排除 _runner_archive、_recovery、测试）。主要有三类：
  - `in_date <= d < out_date`（out_date 空填 2100-01-01）：tradable_ic_v1、netret_midlarge_p7、mainbook_v2_a2_sealed、capital_flow_*、attrib_v2/common、ai_factor_gp_reopen_hardgate_v10b–v28 系列；
  - 月末快照：alpha_combo_marginal_v1_1 / v1_2、alpha_hiliq_s8_paradigm_v1_1；
  - quantlab：universe/mask.py、universe/d1_masks.py 的 sw_l1_asof，以及 Intel 的 intel_common.sw_members_asof。
  其中 9 个在纸面冻结闭包里（quantlab/beta/smallcap_history_selector.py、smallcap_sleeve.py、factors/residual_factory.py、universe/d1_masks.py、universe/mask.py、v2_proto_smoke.py、v2_schemas.py、v2_smoke.py、research/g1g5_nontextbook_weights.py），10-19 18:40 ET 之前一律不能动。统一到共享函数要另立计划，见 P3-9。

## 5. 冻结件核对 ✔

- paper_import_closure.json 共 156 条，本 diff 的 5 个文件都不在里面；闭包内也没有任何文件 import sw_members_asof、hx2 或 fulla（rg 核过）。research/sw_pit_freshness.py 不在闭包里，而且本 diff 不改它。
- 89d4afa3（CLEAN 表）是冻结数据，本 diff 只是把它设为 hx2/fulla 的默认读取表，只读，不写。87d769aa（industry_members_sw_l1.parquet）在 diff 里没有出现。日历 fa4260b8 只读。
- 落地本身只写 research/ 下 4 个 .py 和 1 个 prereg 文档，不碰 data/、configs/、output/ 下的冻结件和纸面轨。
- 结论：**不必等到 10-19 18:40 ET 之后**。限制只有：不得在 10-19 16:40–18:40 ET 内落地或跑 selftest；落地时不能有进程正在运行 hx2、fulla、leg_review、tie-sens、optimizer_core_x2_run（要 ps 证据）。

## 6. 测试 ✔（只用合成数据）

- 数量：test_sw_members_asof.py 有 35 个 def test_，其中 2 个 parametrize（5 组、3 组），合计 41；test_sw_pit_freshness.py 10 个 def，其中 1 个 parametrize 3 组，合计 12。**总计 53。** 和文件头 L71–L72 一致。
- 只用内存 DataFrame、合成日历 CAL 和 tmp_path 下的合成 parquet / manifest。所有 gap-carry 调用都显式传 cal=CAL；load_trade_cal、load_sw_l1、sw_l1_table_check 都以 tmp_path 为 root；全文件没有 data/v2 真实路径的读取。✔
- 新增的 6 个 CLEAN 用例我逐个手推过，预期与实现一致（没有运行）：schema 常量与夹具一致；适配器的点号/前缀/大小写/空格写法和 T00018 剔除；4 种 schema 不符都报错；5 种非白名单 id 都报错；manifest 检查的 coverage_day=2026-10-09、lag 1 → 4、未描述的文件标为未检查；metrics 不符、fetch_time 坏、manifest 不可读都报错。
- 缺口：合成夹具里没有“同一 (code,d) 多个空档候选且 l1_name 不同”的用例（对应 P3-1），也没有 in_date > out_date 的计数（P3-3）。

## 7. 内存

- 新增的读取：CLEAN 表 7920 行、日历 8035 行、manifest JSON，都是 MB 级。
- l1_asof 一次性对全部 keys 做 `keys.merge(sw, on=code)`，规模约为 keys 数 × 每个代码的平均行数（CLEAN 约 7920/5914 ≈ 1.34），然后排序去重；空档路径再对缺失的 key 做一次 merge。
  - hx2、fulla 的 keys 是持仓行（约 3.4 万），开销可以忽略。
  - 叶25 按月调仓（r4 L87），约 100 个调仓日 × 约 5500 只 ≈ 55 万个 key，估计瞬时增加不到 300 MB。
  - 如果有调用方传入逐日全网格（例如 5600 × 570 ≈ 319 万个 key），28eabd35 里我在 /tmp 内联复算这一规模时，maxrss 是 1295–1393 MB（含数据加载），已经接近 1331200 kB 的目标线。见 P3-6。
- _overlap_list 按代码循环，代价是 O(重叠代码数 × 行数)，在 count 模式下重叠代码多时会慢，但内存不大。

## 8. 发现

**P0：无。P1：无。**

**P2-1（沿用 28eabd35 P2-1，不阻塞落地，但现在有硬期限）**：
- TRADE_CAL_REL 和 TRADE_CAL_SHA_PIN（L67–L68）写死在代码里。主 Agent 已裁定 2027 日历由 Data 写新版文件、11-30 前审完、12-15 前切换。新文件的路径或 sha 必然变化，所以必须同时出一个代码 diff 改这两个常量（sw_members_asof 的 sha 会随之改变），并重签所有钉它的 .ok。这个 diff 要并入 2027 包一起审。
- 新问题：_completed_open_day（L259–L268）用当前墙钟时间换算上海日期，上海日期超过日历末日就报错（L263、L303）。所以从 **2026-12-31 11:00 ET**（上海 2027-01-01 00:00）起，所有读 CLEAN 表的调用都会报错，即使查询的是历史日期。12-15 切换必须早于这个时点。

**P2-2（新增，落地前必须关闭）**：NON_A_SHARE_KNOWN（L179）是占位。文件头 L36–L37 和代码注释 L180–L182 自认：Data r2 L68 只说 CLEAN 里 T00018 的写法和原表不同，没给出具体写法。现在凡是不匹配 A_DOT/A_PFX 的 instrument_id 都会让 load_sw_l1(CLEAN) 报错。CLEAN 是 hx2、fulla 的默认表，也是叶25 要钉的表，所以这个函数落地后很可能在它的默认表上直接报错，叶25 也就无法使用。同样，manifest 比对（L285–L296）里的 n_instruments（5914）、in_date_min（1984-05-09）、in_date_max（2026-09-24）还没有对真实表核过（我只核了行数 7920）。
要求：
- Data 交 §14② 只读核查结果：CLEAN 表中所有不匹配白名单的 instrument_id 原样列出并计数，以及 n_instruments 和 in_date 最小、最大值。
- 如果实际写法不是 "T00018"，或还有其他非白名单 id，Strategy 出 r3c，只改 NON_A_SHARE_KNOWN（另附新 sha 链和新的 incremental diff）。如果 Data 证明只有 "T00018" 这一种写法，r3b 可以原样落地。

**P3**：
- P3-1：空档沿用有多个候选时（L438），即使在 raise 模式下也按 tie order 静默取一条，只计数 n_rows_gap_carry_multi_candidate，和主 Agent 06:49“默认报错”的精神不一致。建议 raise 模式下候选 l1_name 不同时报错，count 模式下并入 overlap_codes。下一轮改即可，hx2、fulla 用 count，不受影响。
- P3-2：完全相同的重复行在 raise 模式下也会报错。建议只在候选 l1_name 冲突时报错，或在 prep_sw 先对完全相同的行去重并计数。属于口径问题，请主 Agent 定。
- P3-3：in_date > out_date 的行被静默忽略，没有表级计数。建议在 prep_stats 加 n_rows_in_after_out。真实 legacy 表为 0，CLEAN 未知，请 Data 在 §14② 一并给出。
- P3-4：pitfix allow .ok 的字段名。按 .ok 规范（key=value、显式 allow_* 键），定为 `allow_pitfix_compare=true`。解析器（hx2 L815–L819）把第一个 `=` 换成 `:`，所以 key=value 写法能被正确识别。建议下一轮再加两项检查：expires_et 未过期，以及 .ok 不在 _consumed/ 下。pitfix 目前暂停，不阻塞。
- P3-5：CLEAN manifest 的 fetch_time 是 10-10，coverage_day 是 10-09。按今天算 lag_tdays=5 ≥ 3，所以 hx2、fulla 的每次运行都会带 stale=True 和 disclosure_zh。X2 末日 10-09 不晚于 coverage_day，不会有 coverage_gap。这只影响披露，但报告要写明。checked_at_et 来自墙钟时间，summary 不能逐字节复现，这一点可以接受。
- P3-6：l1_asof 不分块。keys 超过 100 万的调用方必须按 session 分块调用。由于规则对每个 (code,d) 独立，分块结果完全等价（stats 要逐块加总，raise 模式逐块判断）。建议在 docstring 写明。
- P3-7：叶25 预注册 r4 没写 on_overlap 用哪种模式。要求 r5 写明 "count"（研究轨口径）并披露 overlap_codes，同时钉 sw_members_asof 落地后的 sha、表 89d4afa3、日历 fa4260b8。转给 AI。
- P3-8：selftest 解释器 ql-enrich-venv 的 pyarrow 是 26.0.0，研究解释器 qlvenv 是 25.0.1，pandas 都是 3.0.6。dtype 名称（str、datetime64[us]）我在 qlvenv 上实测一致。回执里要记两边的版本。
- P3-9：仓库里还有约 50 个文件各自实现 SW as-of，口径多为 `in_date <= d < out_date`，与共享函数不同（第 4 节）。本 diff 不改它们。其中 9 个在冻结闭包里，10-19 18:40 ET 之前不能动。要另立迁移计划：先列清单，再逐个钉 sha 迁移。
- P3-10：r3b 在静默窗口内写成，Strategy 没跑 py_compile、pyflakes 和测试（文件头 L4–L5）。本次 Arch 在 /tmp 补做了 py_compile 和 pyflakes（第 1 节），测试必须在 selftest .ok 下跑。

## 9. 签 .ok 前 Strategy 要交的材料

### (1) code-change .ok（B r2 + C r3b，或 r3c）
- 前置条件：P2-2 关闭（Data §14② 结果；如有需要，出 r3c 并重新送审 incremental）。
- 落地顺序：`cd /workspace/QuantLab`，核对 pwd 后，`git apply --check` B r2（d0fb1d3f…ee250）→ apply → `git apply --check` C r3b（913e6830…f5ae，或 r3c）→ apply。两步之间不提交，也不跑任何东西。
- old sha：hx2 1c51531a12fd720788105d413264f8d00e6598caf075d96184ba30b5d3c69b45；fulla 7bd657ed936d7adf382e0c30a8537aa3d628dc6eb3e2e65d27b8972abff52316；sw_members_asof.py、test_sw_members_asof.py、prereg 三个文件此前不存在。
- new sha：sw_members_asof e1adef52…8897；test 9943b412…68a7；hx2 b867ee15…df9e；fulla 3ed5a8dd…79ed；prereg 9db7cd14…9856（r3c 则按新链）。
- 不变项前后都要核：sw_pit_freshness.py 5191997e；test_sw_pit_freshness.py cee59fc5；paper_import_closure.json 里的全部 156 个文件；data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet 89d4afa3；industry_members_sw_l1.parquet 87d769aa；trade_cal_sse_pit.parquet fa4260b8。
- 旧文件只读归档到 _recovery/strategy/sw_pit_asof_pre_c3b_20261018/，附 SHA256SUMS。
- 落地时的进程证据：ps 显示没有进程在跑 hx2、fulla、strategy_b4_hiliq_leg_review、tie-sens、optimizer_core_x2_run。
- 时间窗：不得落在 10-19 16:40–18:40 ET。
- 重签清单（文件头 L80–L84）：凡钉 hx2 的 .ok 改为 b867ee15；fulla 改为 3ed5a8dd，并且同时钉 sw_members_asof e1adef52；prereg 9db7cd14；ARCH_RUN_AUTH_TIE_SENS_v1.ok 的 dep_hx2_sha256（3f7f75c3，已过期）和 STRATEGY_TIE_SENSITIVITY_PREREG_ZH.md L75 要重签；跑 main 或 fulla 的 run .ok，sw 表要从 0b1d3432 改钉为 89d4afa3。叶23、叶24 已用过的 .ok 不受影响。
- 附：Strategy 在 /tmp 的 py_compile 和 pyflakes 回执。

### (2) selftest .ok（落地后、Arch 核过 new sha 才签）
- 解释器：/workspace/ql-enrich-venv/bin/python（Python 3.13.5，pytest 9.1.1，pandas 3.0.6，numpy 2.5.3，pyarrow 26.0.0）。
- 跑之前：basetemp /tmp/arch_swpit_asof_c3b_selftest 必须不存在（10:54 ET 核过不存在）；两个测试文件的 sha 是 9943b412 和 cee59fc5。
- 命令（只跑一次）：`cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/ql-enrich-venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/arch_swpit_asof_c3b_selftest research/tests_sw_pit/test_sw_members_asof.py research/tests_sw_pit/test_sw_pit_freshness.py > "$R/stdout.txt" 2> "$R/stderr.txt"; rc=$?; echo "$rc" > "$R/exit.txt"`，其中 R=docs/v2/audit/strategy_sw_pit_asof_c3b_selftest。不准接 `|| true`，不准用管道。
- 预期：53 passed，exit 0。exit code 和 passed 数分开记录，只看 exit code 不算通过。
- 只用合成数据，不读真实数据，不需要 94322 停在 T。但不要和 Data 的补跑同时跑，免得 newermt 回执混在一起。不得在 10-19 16:40–18:40 ET 跑。预计 RSS 在 300 MB 以内。
- 跑完：删除 basetemp；research/ 下不能有新的 __pycache__ 或 .pytest_cache；`find -newermt T0` 只允许回执目录有新文件。

### (3) 叶25 冻结
selftest 回执经 Arch 审过之后，AI 的预注册 r5 要钉 sw_members_asof 落地后的 sha、on_overlap="count"、表 89d4afa3、日历 fa4260b8（P3-7），之后才能冻结。

live=false，promotion=false。本审查没有写 .ok，也没有给任何 agent 发消息。
