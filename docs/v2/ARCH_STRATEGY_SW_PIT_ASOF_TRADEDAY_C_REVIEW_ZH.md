# Arch 审查：Strategy DIFF C（申万 L1 空档沿用，d−1 改为上一个 SSE 交易日）

- 审查人：QuantLab Arch。只做静态审查，没有运行项目代码，没有 import 项目模块，没有跑 pytest。
- 时间：2026-10-18T06:13:21-04:00（ET，取自 `date`）
- 被审对象：docs/v2/audit/STRATEGY_SW_PIT_ASOF_TRADEDAY_PROPOSAL_20261018.diff，sha256 7504e80756353ce85275a4209a3939a599243da5be99139dca472ab4bb948595，502 行
- 基线：HEAD 9b1d2349 用 git archive 导出到 /tmp/arch_diffc_1792318137/base，先打 r2（d0fb1d3f…），再打 C。全程在 /tmp 下进行，git apply 前先 `cd` 并核对 pwd，没有在 /workspace 下 apply。审完 tmp 目录已删除。
- 要落实的裁定：主 Agent 06:01。严格 in_date<d；只有旧 out_date 等于 d 之前最近的 SSE 交易日时才沿用旧行业，且只沿用 1 个交易日；日历作为参数传入；d 超出日历覆盖就报错；单测要覆盖跨周末和超出日历报错。

## 结论：PASS（有条件）

没有 P0 或 P1。有 1 个 P2（运维层面，不阻塞落地），还有若干 P3。
落地顺序按 Strategy 第 (5) 条：r2 落地 → 叶 23 跑完、回执审完 → 按自然日跑的 pitfix-compare 跑完 → Arch 另签 code-change .ok 和 selftest .ok（预期 29 passed，exit code 单独记录）。
落地后，所有钉了 hx2 sha 的 .ok 都要按 8c5932d3 重签。strategy_tie_sensitivity_prereg_v1 的 dep_hx2_sha256 也在其中。

## 1. sha 链 ✔

| 文件 | HEAD | r2 之后 | C 之后（实测） | 申报 | /tmp/swr5/c |
|---|---|---|---|---|---|
| research/sw_members_asof.py | 不存在 | 0444d9d6… | 405e8182c6e4c9895b62162eb6dc8f7a58a6ce7addab0288c8072b066720ce16 | 一致 | 一致 |
| research/tests_sw_pit/test_sw_members_asof.py | 不存在 | 4f468b48… | fc9d969994f4b5d4beb84823fa958318871690b12343b7905385061979859e2c | 一致 | 一致 |
| research/strategy_hiliq_capadv_b4_x2.py（hx2） | 1c51531a… | 1728c126… | 8c5932d36d176c777ce9ed2550fda35d0213672b5a1c56c1b02591533f4b7825 | 一致 | 一致 |
| docs/v2/STRATEGY_SW_PIT_ASOF_FIX_PREREG_ZH.md | 不存在 | c2b37127… | 0b917e8ff555a4f55c6084a5832c6c77cf3f2ca2a5d7bc537071e1ed31f0f85f | 一致 | 一致 |
| research/strategy_fulla_b4_x2.py（fulla） | 7bd657ed… | 88b6f367… | 88b6f367…（不变） | 一致 | 一致 |
| research/sw_pit_freshness.py | 5191997e… | 不变 | 5191997e…（不变） | 一致 | 一致 |

- r2 和 C 的 `git apply --check` 都通过。r2 有一处 EOF 空行告警，C 已经去掉，hx2 现在以 `)\n` 结尾。
- C 只改上面 4 个文件。test_sw_pit_freshness.py 仍是 cee59fc5，没动。
- 真实仓库目前没有 research/sw_members_asof.py，即 r2 尚未落地，和申报一致。
- 数据 pin：trade_cal_sse_pit.parquet 是 fa4260b8…，sw l1 表是 0b1d3432…，都实测吻合。

## 2. TradeCal 和 load_trade_cal ✔

- **pin**：TRADE_CAL_SHA_PIN 是 fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41，和真实文件、manifest.json 一致。load_trade_cal 只读一次字节，再用这份字节同时算 sha 和解析，没有 TOCTOU。sha 不等就抛 SwPitIntegrityError。sha_pin=None 时只记录不校验，生产调用方都没有传 None。
- **校验项**：
  - 非空，且 cal_date、is_open 两列都在；
  - cal_date 必须能按 %Y%m%d 解析，带横杠的写法会变成 NaT 并报错；
  - 不能有重复日期；
  - is_open 经 to_numeric 后必须属于 {0,1}，NaN 和 2 都会报错；
  - 排序后从 start 到 end 逐日连续；
  - 至少有一个开市日。
- **错误路径**：prev_open 有三种报错，都抛 SwPitIntegrityError，没有任何退回自然日的分支：
  - d 早于 start；
  - d 晚于 end；
  - d 之前没有开市日（searchsorted 结果小于 0）。
  默认参数 cal=None 时走 load_trade_cal()，仍校验钉住的 sha，这不算退回自然日。
- **真实日历**：
  - 覆盖 2005-01-01..2026-12-31，共 8035 行，其中开市日 5343 天。第一个开市日是 2005-01-04，所以 d=2005-01-04 会报“之前没有开市日”。
  - 拿 prev_open 和日历自带的 pretrade_date 对比：5342 个开市日里一致 5341 个。唯一的不一致是 20130424，它的 pretrade_date 是空串，属于数据列本身的瑕疵。TradeCal 不读这一列，不影响结果。已记为 P3-6 给 Data。
- **dtype**（新增检查项）：
  - 在 pandas 3.0.6 下（qlvenv 和系统 python 版本相同），日历解析结果、session 和 sw 表的 in_date/out_date 都是 datetime64[us]。真实文件里的 in_date/out_date 是 timestamp[us]。
  - 实测确认：us 与 ns 混用时 `==` 和 np.searchsorted 都正确。
  - 这里没有 merge_asof，也没有 pyarrow filter。
  - prev_open 的 docstring 写的是 “datetime64[ns]”，与实际不符，记为 P3-1。

## 3. 沿用逻辑 ✔

- 逻辑如下：
  - 无有效行的 (code,d) 才进入候选；
  - 候选要求 in_date 已解析、out_date 非空；
  - 沿用条件是 `out_date == prev_open(d)`；
  - 有多条候选时，按 (in_date,_pri,_ord) 取最后一条。
- 因为下一个 session d' 的 prev_open(d')=d≠out_date，在交易日 session 上最多沿用 1 天。✔
- 边界情况：
  - **节假日**：例如 9-30 出、国庆后第一个交易日进，prev_open 就是 9-30，会沿用。真实全表上，交易日规则比自然日规则多沿用 341 个代码日，全部来自周末和节假日。✔
  - **d 是第一个开市日**：会报错，测试里覆盖了合成日历 2018-01-01（周一）的情况。✔
  - **d 本身不是开市日**：不报错，prev_open 取 d 之前最近的开市日。如果 keys 里同时有周六和周一，周五出的行在两天都会被沿用。调用方只传交易 session，所以实际不会发生。记为 P3-2，建议加一个计数或严格开关。
  - **out_date 落在非开市日**：不沿用，计入 n_rows_gap_out_closed_day_not_carried，符合字面裁定。
  - **in_date 落在非开市日**：真实表有 1252 行。按严格 in_date<d，例如周六进，下周一就已经是有效行，不会产生空档，这种情况不需要沿用。✔
  - **范围检查作用于全部 keys**：开启 gap_carry 时，连已有有效行的 key 也要过范围检查，所以 session 从 2027-01-01 起会一律报错。这符合“d 超出覆盖就报错”的裁定，见 P2-1。
  - **NaT session**：numpy 求 min 得到 NaT，与 Timestamp 比较为 False，所以不会触发范围检查报错。之后它会被放到最后一个开市日，不会命中有效行，可能被误沿用（理论上只有 out_date=2026-12-31 的行才会，真实表里没有）。记为 P3-3，建议显式拒绝 NaT。
  - **in_date > out_date 的异常行**：真实表 0 行。
- **统计项**：
  - n_rows_gap_carry_no_successor 的“后继”定义是同一代码的另一行，且 in_date ≥ out_date。在 X2 全网格上实测 1 次，全表 46 次，和 r2 审查里“46 个退出”一致。
  - n_rows_gap_out_closed_day_not_carried 在 X2 上是 0。
  - 全表的 n_reclass_gap_rows 仍按自然日统计，已在文档里写明，按 Strategy 待定 (4) 放到下一轮。

## 4. 真实数据独立复算

只用 pandas，在 /tmp 里内联重写规则，没有 import 项目代码。数据是 sw l1 0b1d3432 和 trade_cal fa4260b8。进程 maxrss 1393MB，低于 1.5GB。

| 口径 | 交易日规则 | 自然日规则 | 放宽规则（prev_open ≤ out_date < d） |
|---|---|---|---|
| X2 变更级（第一个空档交易日落在 X2 的变更，共 227 次） | **227** ✔ | 208 ✔ | — |
| X2 代码日级（5600 个代码 × 570 个 session = 3,192,000） | **225**（有后继 224，无后继 1） | 206 | 225（多出 0） |
| 全表代码日级（d 在日历覆盖内，取 out_date 之后的下一个开市日） | **1516**（无后继 46） | 1175 | 1516（多出 0） |

- 自然日规则能沿用而交易日规则不能的：X2 和全表都是 0。交易日规则独有的：X2 19 次，全表 341 次。
- **227 和 225 的差别**：227 是按变更计数。其中 3 次变更在第一个空档日已经有别的有效行，所以不需要沿用：
  - 002420.SZ 2026-07-01
  - 300972.SZ 2024-07-30
  - 300972.SZ 2026-03-05
  
  另外还有 1 次是退出申万后没有后继行的沿用，所以代码日级是 227−3+1=225。两种口径互相对得上。
- **放宽规则的影响**：
  - out_date 落在非开市日的行共 37 行，最晚的是 2004-08-09，全部早于日历起点 2005-01-01。
  - 日历覆盖范围内，放宽规则多出的情况是 0，Strategy 的说法属实。
  - 这 37 行如果有人查询 2005 年以前的 d，会直接报错，不会被静默沿用。
- B4 持仓口径（34100 个持仓代码日，两种规则只差 1 次沿用，差异为 0）沿用 r2 审查 c72f0856 的结果，本次没有改变。

## 5. 测试 ✔

- **数量**：test_sw_members_asof.py 有 17 个 def test_，没有 parametrize。test_sw_pit_freshness.py 有 10 个 def，其中 1 个 parametrize 3 组，共 12 个。**合计 29。** ✔
- **只用合成数据**：
  - 合成日历 CAL 覆盖 2018-01-01..2026-12-31，周一到周五开市。
  - 每个 gap-carry 调用和 IndustryAsOf 都显式传了 cal=CAL，所以不会走默认路径去读真实日历。
  - load_trade_cal 用 tmp_path 下的合成 parquet。
  - 全文件没有 read_parquet 真实路径，也没有 data/v2 字样。✔
- **新增 W 行后的影响**：fixture 加了 W.SZ 两行，追加在末尾，原有行号不变（index 2=Y，8=G）。逐个核对旧的 11 个用例，W 只在 rowfilter 用例里出现：2025-03-10 两边都返回 None，结果不变。✔
- 6 个新用例逐个手推，预期都和实现一致（没有运行）：
  1. **跨周末**：W 在 03-10（周一）这天没有有效行。prev_open(周一)=03-07（周五），等于 out_date，所以沿用电子。03-11 新行有效，返回计算机。03-07 旧行仍有效，返回电子。沿用 1 次，无后继 0，未知 0，sha 是 "synthetic"。纯规则下周一返回 None。✔
  2. **自然日情形在交易日规则下的结果**：
     - G 03-11 沿用电子；
     - H 03-11：out 03-09 不等于 03-10，返回 None；
     - H 03-10：out 03-09（周日）落在 (03-07, 03-10) 之间，返回 None，计入 closed=1；
     - Z 03-11 沿用医药生物，无后继；
     - Z 03-12 返回 None；
     - X 03-11 返回计算机。
     
     合计沿用 2 次，无后继 1，closed 1，未知 3。✔
  3. **in_date 无法解析**：G 旧行的 in_date 改成 garbage，返回 None，沿用 0，n_in_unparsed=1。对照组仍返回电子。✔
  4. **超出日历报错**：以下 4 种情况都抛 SwPitIntegrityError：
     - 2027-01-04 晚于 end；
     - 用只到 2025-12-31 的短日历查 2026-01-02；
     - 2017-12-29 早于 start；
     - 2018-01-01 是开市日，但之前没有开市日。
     
     纯规则查 2027 年返回银行，不用日历。2018-01-02 不报错，返回 None。✔
  5. **sha pin 和 TradeCal 校验**：
     - 默认 pin 下读合成文件会报错；
     - 传入正确的 pin 能加载，start 和 end 正确，prev_open(2025-03-10)=2025-03-07；
     - 缺一天、is_open=2、cal_date 写成 2025-03-10、日期重复、空表，这 5 种都会报错。✔
  6. **guard**：以下 4 种都会触发 SystemExit，match 文本对得上：
     - 指向 b4 的 symlink 本身；
     - 该 symlink 下的子目录（resolve 后都落在 b4/）；
     - capadv_x2/new；
     - legs/new。✔
- 测试缺口记为 P3-4：
  - 合成日历里没有工作日休市的节假日；
  - “超出日历”用例没有用 match= 区分三种报错原因；
  - 没有覆盖 d 是非开市日的情况。

## 6. guard

C 没有改 pitfix_out_dir_guard 的实现，只补了测试，所以 symlink、capadv_x2、legs 这几种情况现在都有用例保护。实现本身的逻辑如下：
1. 先 resolve 路径；
2. 检查第一层目录是否是 b4、capadv_x2 或 legs；
3. 检查路径里是否含 paper 或 frozen；
4. 检查目录是否已存在或是 symlink。

我对照实现核对过，4 个新用例都会按预期触发。✔

## 7. 调用方

- **hx2**：是唯一改动的调用方，共 3 处都显式传入了 cal：
  - load_industry_asof 里是 `IndustryAsOf(..., cal=load_trade_cal(ROOT))`；
  - smallcap_and_industry 里 IndustryAsOf 和 sw_l1_asof_with_gap_carry 都传了 `cal=ia.cal`；
  - pitfix_compare 的 summary 改用 `asof.cal.sha256`，asof 在第 767 行定义。
  
  build_topn 和 apply_ind_cap 通过 IndustryAsOf.by_session 使用 self.cal。✔
- **fulla（88b6f367，不变）**：
  - `IndustryAsOf(load_sw_l1(ROOT))` 不传 cal，会从 _DEFAULT_ROOT（模块所在仓库根）读日历，同样校验 sha。
  - 第 260 行的 `sw_l1_asof_with_gap_carry(ia.sw, Wx, ...)` 也不传 cal，会再读一次。两次都经过 sha 校验，内容一致，但重复读取，记为 P3-5。
  - 风险：fulla 的 sha 不变，但口径会从自然日变成交易日。凡是 fulla 的 .ok，必须同时钉 sw_members_asof 的 sha（405e8182），不能只钉 fulla。
  - fulla 的 reclass dict 会带出 gap_carry_rule 和 trade_cal_sha256，口径变化可以从产物里看出来。
- **optimizer_core_x2_run**：只在 phase_smoke 里 `from strategy_hiliq_capadv_b4_x2 import run_smoke`，而这个函数第一行就 raise SystemExit（T1 已禁用）。run_smoke 本身也不调用行业函数，所以不受影响。✔
- **strategy_b4_hiliq_leg_review**：用的是 hx2.load_industry_map，即静态的 legacy 映射，没有改动。import hx2 时会多 import 一个 load_trade_cal，但不会读日历。✔
- **strategy_tie_sensitivity_prereg_v1**：钉了 dep_hx2_sha256，hx2 落地后要重签。
- **Intel**：intel_common、event_study、c1_gap_split 用的是 Intel 自己的 sw_members_asof，目前不调用共享函数，等 C 落地后才能接入。
- 全仓 grep 过 research、scripts、quantlab 三个目录，没有其他调用方。

## 8. 静态检查

- pyflakes（`PYTHONPATH=/tmp/pf python3 -m pyflakes`）：
  - sw_members_asof.py：0 条；
  - test_sw_members_asof.py：0 条；
  - hx2：1 条，第 633 行 charts2 未使用。这是基线遗留，r2 版第 632 行就有，不是 C 引入的。
  - fulla：1 条，nav_path 未使用，也是基线遗留。
- py_compile：3 个改动的 .py 都 OK。cfile 写在 /tmp，工作树里没有产生 __pycache__。
- f-string：C 新增的行里，没有漏写 f 前缀的 {name} 字符串。
- C 没有引入新的 import，只有 stdlib、numpy、pandas 和 sw_pit_freshness 的错误类型。测试文件新增了 hashlib 和 os。

## 9. 发现（按严重度）

**P0：无。P1：无。**

**P2-1（运维耦合，不阻塞落地，落地前要定好流程）**：TRADE_CAL_SHA_PIN 是写死在代码里的常量，日历覆盖到 2026-12-31 为止，开启 gap_carry 时对所有 key 都做范围检查。由此有三个后果：
- (a) Data 在 11-30 前把日历延到 2027 时，文件 sha 一定会变。之后 hx2、fulla 以及将来接入的 Intel，所有 gap-carry 调用都会因 sha 不符而报错（fail-closed）。要恢复，必须同时出一个代码 diff 改 pin（sw_members_asof 的 sha 会随之改变），并重签所有钉了它的 .ok。
- (b) nightly 第一步就是 trade_cal_pit.py。只要 relay 返回的内容有任何变化（比如补上 20130424 的 pretrade_date），它就会重写文件，sha 随之改变，效果同 (a)。
- (c) 到 2027-01-01，即使已经有有效行业，查询也会一律报错。

建议：把“日历续期 + 改 pin + 重签”做成一个包，由 Data 和 Strategy 同步交付，最晚 12-15 前审完。Intel 的日常循环接入共享函数之前，必须先有这个流程。

**P3**：
- P3-1：prev_open 的 docstring 写的是 datetime64[ns]，在 pandas 3 下实际是 [us]。比较和 searchsorted 不受单位影响（已实测），只需改文档。
- P3-2：没有校验 d 本身是开市日。如果给的是非开市日的 session，周五出的行在周六和周一都会被沿用。建议加计数 n_rows_session_not_open，或加严格开关。
- P3-3：NaT session 能绕过范围检查。建议在 prev_open 里对 NaT 直接抛错。
- P3-4：测试缺口：
  - 合成日历没有工作日节假日（建议把某个周一标成 is_open=0，验证节后沿用）；
  - “超出日历”用例没用 match= 区分三种报错；
  - 没有覆盖 d 是非开市日的情况。
- P3-5：fulla 没有显式传 cal，会读两次日历。建议 fulla 下次改动时顺手改成 `cal=ia.cal`；本次不改，免得重签。（回复 Strategy 待定 (2)）
- P3-6：日历的 pretrade_date 在 20130424 是空串，转给 Data 做 FYI。TradeCal 不使用这一列。另外，日历 parquet 的 mtime 是 01:13，晚于 manifest 里的 finished_at（00:19 ET），但 sha 和 manifest 一致。
- P3-7：候选行没有要求 in_date ≤ out_date。真实表 0 行，可以加一行防御性检查。

## 10. 对 Strategy 待定事项的意见

1. **out_date 落在非开市日**：维持字面裁定，只计数，不放宽。日历覆盖范围内放宽的影响实测为 0，没有必要改动主 Agent 的裁定。将来如果计数大于 0，再报主 Agent。
2. **fulla 显式传 cal**：本次不改，见 P3-5。fulla 的 .ok 必须钉 sw_members_asof 405e8182。
3. **prereg 第 4 节**：按 Strategy 第 (5) 条的落地顺序，C 在自然日 pitfix 跑完之后才落地，和 c2b37127 的 pin 不冲突，所以直接改原文件，不另开附录。
4. **全表 n_reclass_gap_rows 的交易日口径**：放到下一轮。本审查的参考值是：全表代码日级交易日沿用 1516 次，自然日 1175 次。
5. **落地顺序**：同意。

live=false，promotion=false。本审查没有写 .ok，也没有给任何 agent 发消息。

---

# C r2 审查（追加）

- 时间：2026-10-18T06:25:21-04:00（ET，取自 `date`）。只做静态审查，没有跑 pytest，没有运行或 import 项目代码，没有改动真实仓库，也没有写 .ok、没有给任何 agent 发消息。
- 被审对象：docs/v2/audit/STRATEGY_SW_PIT_ASOF_TRADEDAY_PROPOSAL_20261018_r2.diff，sha256 f31784a866c2f7f2a7cdf3db3254955b4544da0de7001d035f3a650fa21dcf8c，645 行。它直接基于 r2，不是在 DIFF C 上叠加。
- 方法：HEAD 9b1d2349 用 git archive 导出到 /tmp/arch_diffc2_1792318981/base，先打 r2（d0fb1d3f），再打 C r2；每次 apply 前都 cd 进去并核对 pwd。审完 tmp 目录已删除。
- 本轮按 Arch 的新决定执行，覆盖上文 §10 第 1、2 条的意见：
  - 窗口放宽为 prev_open ≤ out_date < d，并保留计数；
  - fulla 显式传入 cal；
  - 去掉模块默认日历，不传 cal 就报错。

## 结论：PASS

没有 P0、P1，也没有新的 P2。P2-1（日历 pin 与续期、2027-01-01 截止）仍未解决，Strategy 已注明在等主 Agent 裁定。它不阻塞落地，但要在 Intel 接入共享函数之前定下来。
落地顺序不变：r2 落地 → 叶 23 跑完、回执审完 → 按自然日跑 pitfix-compare（仍用 r2）→ Arch 另签 code-change .ok 和 selftest .ok（预期 35 passed，exit code 单独记录）。

## R1. sha 链 ✔

| 文件 | r2 之后 | C r2 之后（实测） | 申报 | /tmp/swr5/c2 |
|---|---|---|---|---|
| research/sw_members_asof.py | 0444d9d6… | d8088ce1cb7c15f52b568add3d5aab0c90df7c12bee06aa317c638b12276961e | 一致 | 一致 |
| research/tests_sw_pit/test_sw_members_asof.py | 4f468b48… | 73b00aea0692c53945b4631c78dff82de316527762223ff7866912ddb47bb496 | 一致 | 一致 |
| hx2 research/strategy_hiliq_capadv_b4_x2.py | 1728c126… | e3f1a63e3658e2da8cf802dfea7a5b10d4596894873c6f2b449a11a940c51ded | 一致 | 一致 |
| fulla research/strategy_fulla_b4_x2.py | 88b6f367… | f1b1062ffb5d3db1f8e8e23ad08e2cc378134d3293042d5281c2731608e0cc75 | 一致 | 一致 |
| prereg | c2b37127… | 0b917e8f…（与 C 相同） | 一致 | 一致 |
| sw_pit_freshness.py / test_sw_pit_freshness.py | 5191997e / cee59fc5 | 不变 | 一致 | 一致 |

`git apply --check` 通过，只改了这 5 个文件。

## R2. 各项改动的逻辑 ✔

1. **窗口放宽**：条件是 `(out_date >= _prev) & (out_date < _d)`。因为 d 必须是开市日，下一个 session d' 的 prev_open(d')=d，已经大于 out_date，所以仍然最多沿用 1 个交易日。
   - n_rows_gap_carry_out_on_closed_day 统计的是 out_date > prev_open(d) 的沿用行，也就是 out_date 落在非开市日、按 DIFF C 字面规则本来不会沿用的那部分。
   - 旧计数 n_rows_gap_out_closed_day_not_carried 已删除，hx2 summary 里的说明文字也同步改了。✔
2. **去掉默认日历**：
   - `_DEFAULT_ROOT` 已删除，load_trade_cal(root) 的 root 必须传，不传会报 TypeError。
   - l1_asof 在 gap_carry=True 且 cal 为 None 时，第一行就抛 SwPitIntegrityError，在任何计算之前。
   - IndustryAsOf 的 cal 为 None 时也报错。
   - 全文已经没有 `_DEFAULT_ROOT` 或不带参数的 `load_trade_cal()` 调用。✔
3. **docstring**：已改为 datetime64[us]（pandas 3 下的实际单位）。✔
4. **session 检查顺序**：prev_open 按以下顺序检查：
   1. NaT；
   2. 超出 start..end；
   3. require_open 时，d 不是开市日。判断方法是 `open_days[min(j, n−1)] == x`，所以 end 当天是休市日、或 x 在第一个开市日之前时都能正确判为非开市日；
   4. d 之前没有开市日（j−1 < 0）。
   
   gap-carry 路径固定 require_open=True。例如真实日历中，2005-01-01..03 判为非开市日，2005-01-04 判为“之前没有开市日”，2027 年的日期一律判为超出范围。顺序与申报一致。✔
5. **NaT 来源**：gap-carry 模式下，session 用 errors="coerce" 解析。null、无法解析的值，以及格式与首个元素不一致的值都会变成 NaT，然后被拒绝，属于 fail-closed。纯规则仍用 errors="raise"，没有变化。✔
6. **in_date ≤ out_date**：候选行要求 in_date 已解析、out_date 非空、且 in_date ≤ out_date。结合窗口条件 out_date < d，可推出 in_date < d。✔
7. **调用方**：
   - hx2 有 3 处都显式传入 cal，与 C 相同；
   - fulla 改为 `IndustryAsOf(load_sw_l1(ROOT), cal=load_trade_cal(ROOT))` 和 `sw_l1_asof_with_gap_carry(..., cal=ia.cal)`，日历只读一次。
   
   两者的 ROOT 都是 `Path(__file__).resolve().parents[1]`，即仓库根。✔

## R3. 真实数据复算（只用 pandas，在 /tmp 内联重写 C r2 规则；maxrss 1295MB）

| 口径 | C r2 沿用 | 无后继 | out_date 落在非开市日的沿用 | DIFF C 沿用 | 两者逐行差异 |
|---|---|---|---|---|---|
| X2 全网格（5600 × 570 = 3,192,000 个代码日） | **225** | 1 | 0 | 225 | 0 |
| 全表代码日（d 在日历覆盖内） | **1516** | 46 | 0 | 1516 | 0 |

- 与预期的 225/1516 一致。在日历覆盖范围内，放宽窗口不改变任何一行的结果。
- 真实表中 in_date > out_date 的行为 0，out_date 落在非开市日的 37 行全部不晚于 2004-08-09。
- **新检查在现有输入上不会触发**：
  - 我检查了以下文件：hiliq 6 条腿、fulla 6 条腿（比 Strategy 说的 9 条腿多查了 fulla 的 equity_incentive、report_rc_allup、insurer_surv 三条）、hx2 smallcap 读取的 capadv pos 权重文件，以及 hiliq 和 fulla 现有的 B4 topN 60w/100w 共 4 个文件，取 weight>0 的行。
  - 结果：每个文件都是 668 个 session，范围 2024-01-02..2026-10-09，NaT 为 0，非开市日为 0。
  - 第一个 session 2024-01-02 之前有开市日，最后一个 session 早于 2026-12-31。
  - 所以“NaT / 超出范围 / 非开市日 / 之前没有开市日”这四项检查在现有输入上都不会触发。✔

## R4. 测试 ✔

- **数量**：test_sw_members_asof.py 有 23 个 def test_（r2 的 11 个 + C 的 6 个 + C r2 的 6 个），没有 parametrize。test_sw_pit_freshness.py 仍是 12 个。**合计 35。** ✔
- **只用合成数据**：日历和 SW 夹具都是合成的。load_trade_cal 只读 tmp_path 下的合成文件，没有读真实数据。✔
- **合成日历的改动**：在周一到周五开市的基础上，把 2025-03-17（周一）设为节假日。夹具新增 V.SZ 两行（旧行 03-14 出，新行 03-18 进），追加在末尾，原有行号不变：2=Y，8=G，12=W。
- **旧用例复核**：
  - r2 的 11 个用例都不涉及 03-13..03-19，节假日不影响它们。V 只在 rowfilter 用例里出现，这几个日期 V 的旧行都有效，两边结果一致。
  - C 的用例里只有 natural_day 一条预期改变：H 03-10 由 None 改为电子（03-07 ≤ 03-09 < 03-10）。
    - 沿用次数：3，分别是 G、H 03-10、Z；
    - 无后继：1（Z）；
    - out_date 落在非开市日：1（H）；
    - 未知：2（H 03-11、Z 03-12）。
    
    手推结果与断言一致。
  - outside 用例加了 match，前三种情况报“outside trade calendar”。2018-01-01 是开市日，会通过 require_open 检查，最后报“no open day before”。✔
  - load_trade_cal 用例新增两项：prev_open(03-18)=03-14（跨过节假日），以及 require_open=False 时 prev_open(03-17)=03-14。✔
- 6 个新用例逐个手推，结果都与实现一致：
  1. **周日出、周一沿用**：H 03-10 返回电子（计入 out_date 在非开市日 1 次）；03-11 时 prev 是 03-10，03-09 不在窗口内，返回 None；03-12 新行有效，返回计算机。沿用 1 次，非开市日 1 次。✔
  2. **节后沿用**：V 03-14 旧行仍有效，返回电子；03-18 时 prev 是 03-14，03-14 在窗口内，返回电子，非开市日计数为 0；03-19 新行有效，返回计算机。纯规则下 03-18 返回 None。✔
  3. **非开市日报错**：03-15（周六）和 03-17（节假日）都报“not an SSE open day”。同一批里的 W 03-10 是开市日，不影响报错。纯规则下周六返回银行。✔
  4. **NaT**：pd.NaT、None、"not-a-date" 三种都报错，match 为“NaT”。在 pandas 3 下，`astype(str)` 会把 None 和 NaT 都变成 NaN，最后同样成为 NaT（已实测）。✔
  5. **没有 cal**：以下 4 种都会报错：
     - 共享函数不传 cal，报 “requires cal”；
     - l1_asof 设 gap_carry=True 但不传 cal，报 “requires cal”；
     - IndustryAsOf 不传 cal，报 “requires cal”；
     - load_trade_cal() 不传 root，报 TypeError。✔
  6. **in_date > out_date**：W 旧行的 in_date 改成 03-09（晚于 out 03-07），03-10 不沿用，返回 None，沿用 0 次。✔

## R5. 调用方与 importer ✔

- research.sw_members_asof 只被 hx2、fulla 和它自己的测试 import。grep 范围包括真实仓库的 research、scripts、quantlab、scripts_eng，以及打完 C r2 的 tmp 基线，排除了 _runner_archive 和 _recovery。两个调用方都显式传入 cal。
- 没有其他 importer 会走到“必须传 cal”的路径：
  - **leg_review**：用了 hx2 的 BAL、CAP、IND_CAP、N_BY_AUM、X2、_is_etf、apply_ind_cap、load_industry_map、load_leg、to_id、write_pos_weights。其中 apply_ind_cap 收到的是 legacy dict，走 dict 分支；write_pos_weights 不涉及行业；它自己的 run_smoke 也不调用行业函数。hx2 在模块顶层只做 import，不构造 IndustryAsOf。✔
  - **tie_sensitivity**：经由 strategy_capadv_topn_tie_sensitivity 间接加载 lr 和 hx2，只用到 `_is_etf`、`apply_ind_cap`、`load_industry_map`、`to_id`，以及 lr 的 nav_metrics 和 run_smoke，都不需要日历。✔
  - **optimizer_core_x2_run**：唯一的引用在 phase_smoke 里 `raise SystemExit` 之后，是死代码。✔
  - **Intel、quantlab**：用的是各自同名的函数，与本模块无关。

## R6. 静态检查

- pyflakes（`PYTHONPATH=/tmp/pf python3 -m pyflakes`）：
  - sw_members_asof.py：0 条；
  - test_sw_members_asof.py：0 条；
  - hx2：1 条，第 633 行 charts2 未使用，基线遗留；
  - fulla：1 条，第 167 行 nav_path 未使用，基线遗留。
- py_compile：4 个改动的 .py 都 OK，cfile 写在 /tmp，工作树里没有产生 __pycache__。
- f-string：新增的行里没有漏写 f 前缀的。

## R7. 重签清单核对 ✔

- **output/strategy_hiliq/ARCH_RUN_AUTH_TIE_SENS_v1.ok**（signed_et 2026-10-18T01:19:36-04:00）：
  - dep_hx2_sha256=3f7f75c31611de6a…，等于 research/_runner_archive/strategy_hiliq_capadv_b4_x2.3f7f75c3.py 的 sha。
  - 它与 HEAD 的 1c51531a 已经不一致，所以这张 .ok 现在已过期，C r2 落地后要按 e3f1a63e 重签。
  - docs/v2/STRATEGY_TIE_SENSITIVITY_PREREG_ZH.md 第 75 行钉的是同一个 sha，需要重新预注册。✔
- **其他 .ok**：在 output 和 docs 下，排除 _consumed 和 _VOID 之后共有 12 个 .ok，我用 hx2/fulla/prereg/sw_members_asof 的文件名，以及 1c51531a、1728c126、7bd657ed、88b6f367、c2b37127、0444d9d6、3f7f75c3 这些 sha 去匹配，只命中上面这一张。
- **历史 .ok**：命中的是 _consumed 里的 FRESHNESS_R4（3648d61f）、R5（9fad93b1），以及 _VOID 里的 TIE_SENS_v1.SUPERSEDED_8cc96227。这些都已用过或作废，不需要重签，也不能复用。
- **落地后的规则**：凡钉 hx2 的 .ok 改为 e3f1a63e；凡钉 fulla 的 .ok 改为 f1b1062f，并且必须同时钉 sw_members_asof d8088ce1；钉 prereg 的改为 0b917e8f。为 r2 签的 code-change、selftest、pitfix .ok 只在 C r2 落地前有效。✔
- **叶 23 不受影响**：两张已用过的 .ok（82d79d23、b21e9952）里的 dep_l19_fulla、dep_l20_fulla、dep_l20w_fulla 钉的都是叶子数据文件，不是 strategy_fulla_b4_x2.py；文件里也没有 hx2 或 fulla 的 sha。之后的叶 23 .ok 同样不受影响。✔
- **非 .ok 的引用**：TEAM_STATE_latest.md 和它的 .bak 里引用了 1c51531a 和 7bd657ed，由各自负责的 agent 更新。

## R8. 发现（按严重度）

**P0：无。P1：无。新增 P2：无。**
- **P2-1**：仍未解决，沿用上文的描述。TRADE_CAL_SHA_PIN 写死在代码里，日历续期或 nightly 重写都会改变 sha，从 2027-01-01 起所有查询都会报错。需要主 Agent 定下“续期 + 改 pin + 重签”的流程，在 Intel 接入之前完成。

**P3**：
- **P3-r2-1**：纯规则路径（gap_carry=False）在 pandas 3 下，`astype(str)` 会把 None 和 NaT 变成 NaN，`errors="raise"` 也不会报错，于是 null session 会被静默当成“未知行业”。这是 C 之前就有的行为，C r2 没有改动它。gap-carry 路径已经拒绝这种情况，而生产调用方都走 gap-carry，所以影响很小。建议下一轮让纯规则也对 NaT session 报错，或者单独计数。
- **P3-r2-2**：sw_l1_asof_with_gap_carry 的 docstring 有一行超过 120 列，只是格式问题。reclass_share 的 docstring 可以补上 n_rows_gap_carry_out_on_closed_day 的说明（目前已通过 `**st` 带出到结果里）。
- 上文的 P3-1、P3-2、P3-3、P3-4、P3-5、P3-7 都已在 C r2 中关闭。P3-6 是给 Data 的 FYI，不需要改代码。

live=false，promotion=false。
