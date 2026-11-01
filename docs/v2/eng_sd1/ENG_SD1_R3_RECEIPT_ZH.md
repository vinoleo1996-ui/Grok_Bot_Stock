# SD1 r3 回执（Eng，2026-10-18 02:4x ET）

本轮执行过的只有三样：读代码、py_compile（输出到 /tmp）、静态扫描 sd1_pit_static_check。没有跑 pytest，没有跑对拍，没有 import 任何项目模块，没有写 .ok。
- execution.py 373fed30、`__init__.py` bfdfa63c、ok_runner_pin.py c7805d9a 均未改动；纸面闭包 156/156 个文件不变。
- 测试仍走 v1 门禁 c7805d9a，没有切到 v2。
- r2 备份在 /workspace/sd1_work/pre_r3/。
- live=false，promotion=false。

**授权状态（Arch 02:29 裁定）：**
- docs/v2/eng_sd1/ARCH_SD1_EXEC.ok（eb3c35870e60fd418fcaa977aa695be2c211158185061d64f91ce7d76fa625e5）已作废。
- ARCH_SD1_TEST.ok（4975aac8…dfdc）与 r3 的测试文件和 2 个 dep 不再匹配。
- 两份都要由 Arch 重签：先签 TEST.ok，出单测回执后再签 EXEC.ok。

## 0. 勘误（selftest 回执）
- docs/v2/eng_sd1/SD1_SELFTEST_RECEIPT_ZH.md（1873c9ab…）标题写的是"02:3x ET"，实际写成时间是 **2026-10-18 02:28 ET**。该文件是用 open('x') 创建的，不重写，在此更正。
- 该回执的 RSS 采样间隔是 1 秒（P3）。下次 selftest 改为每 0.1 秒采样一次，同时读 VmRSS 和 VmHWM，并记录最后一次的 VmHWM 与 getrusage children ru_maxrss（采样器是 /tmp 下的临时脚本，不是钉住的文件）。

## 1. T1 根因（BLOCKER，只读代码判定）
**结论：CFG0 和 CFG1 都失败，原因相同；属于测试夹具错误，不是引擎错误。** SD0 和 SD1 的行为都符合规格 2e428f39，对 SD0 对拍和 10-19 纸面没有影响。

逐步推演：
1. 夹具：r2 测试 `_panels`（L213 `prev = C.ffill().shift(1)`，L215 `LD = (prev * 0.9).round(2)`）用上一个有效收盘价生成跌停价。停牌 d[3]–d[5] 期间 ffill 沿用 10，所以复牌日 d[6] 的 LD = 9.0，而夹具给的开盘价是 8.0（−20%）。
2. 下单：d[3] 停牌日收到信号，目标权重从 1.0 降到 0.5。估值价 `Cm` 是 ffill 后的收盘价（pristine execution.py L645；execution_sd1 L780），d[3] 取 10，于是生成卖单 −50000 股（pristine L888–912；SD1 L1250 起相同），unfilled 默认为 carry（pristine L317，SD1 L384）。
3. d[4]、d[5] 停牌，订单记 suspended，继续挂着（CFG1 在 d[4] 的 _sd1_renorm 把 X 归入冻结集 F，订单保留）。
4. d[6] 复牌开盘 8.0 ≤ LD 9.0：open_touch 不许卖（pristine L754–755；execution_sd1 r3 L913–914，r2 为 L911–912，逻辑完全相同），记 limit_down 事件，订单继续挂。
5. d[7] LD = 8 × 0.9 = 7.2，开盘 8.0 高于跌停价，卖出 50000 股。

为什么是夹具错：10% 涨跌幅的股票不可能以 −20% 开盘。−20% 的复牌只会出现在无涨跌幅限制的复牌日，Data 用 limit 为 NaN 表示这种情况（规格 §3.4 第 151 行："特殊情形由 Data 提供，引擎只读 limit 字段"）。规格 T1 一行（第 214 行）只要求停牌日无成交、NAV 不变、复牌日计入跳空，这几项 r2 都通过了。"复牌日 d[6] 必须卖出"是 Eng 在 r2 自己加的断言，与这个夹具矛盾。

r3 处理：T1 拆成四个独立用例（测试 L245–303），CFG0 和 CFG1 分开断言。
- `test_cfg0_resume_sell_executes` / `test_cfg1_resume_sell_executes`：复牌日不设涨跌幅（d[6] 的 LD/LU 置 NaN）。复牌日 d[6] 必须卖出 50000 股，ref_price=8.0，即按复牌实际开盘价、而不是停牌前收盘价成交（满足 Arch 裁定 4）。
- `test_cfg0_open_below_limit_down_carries` / `test_cfg1_open_below_limit_down_carries`：保留原夹具，断言 d[6] 不成交、有 limit_down 事件、d[7] 卖出 50000 股。这记录了 open_touch 的行为。
- 两类用例都保留原来的 NAV 断言（停牌日不变，复牌日 −2e5）。

影响：引擎代码一行未改。SD0 路径与 pristine 的逐位一致不受影响；10-19 纸面走的是主 execution.py 373fed30，没有动。

## 2. T3：0.0238 的来源（Arch 裁定 3，容差不放宽）
- 精确对账：观察值 399999.9761581421 = nav(1e6, float64) × float32(1 − (float32(0.3) + float32(0.3)))。其中 float32(0.3) = 0.30000001192092896，两者之和是 0.6000000238418579，1 减去它得 0.3999999761581421。差额 −0.02384185791015625 与观察值逐位相同（本机 numpy 复算，没有 import 项目代码）。
- 所以这不是记账缺口。手续费（夹具里为 0）、整手余数（lots=False）、冻结的停牌持仓（X 没有持仓）都不存在。cash、shares、NAV 一直是 float64；只有记录下来的 actual_weights 是 float32，相对误差约 6e-8，乘上 1e6 的 NAV 就是 0.024。
- 为什么是 float32：pristine execution.py L718–720、L882、L940 就把 target_weights 和 actual_weights 存成 float32 诊断输出，SD0 照此保留。
- r3：SD1 路径（engine_version == exec_SD1）改成 float64（execution_sd1 L874 `WDT`）。exec_SD0 仍是 float32，与 pristine 逐位相同；T9 新增 dtype 等于 pristine 的断言。
- 测试改为显式公式加绝对容差 1e-6：renorm 模式期望现金 = 0；cash 模式期望现金 = NAV_open(d3) × w_X(0.4)。同时核对引擎 float64 账面现金 r["cash"]，以及 actual_weights 的 dtype 为 float64。

## 3. T10 / T11（Arch 裁定 2）
- 种植调用改为 `load_delist_events(source='src_events_v1')`。
- 新增 `test_no_source_is_type_error`：不传 source 时，不论是策略调用方还是本测试文件，都必须恰好抛 TypeError（pytest.raises 之后再 `assertIs(type(...), TypeError)`）。
- `test_strategy_caller_raises`：传了 source 的策略调用方必须恰好抛 PermissionError。两个用例都是精确类型，互不顶替。
- 防误读真实数据：T10 的 setUp 和 T11 子进程都先把 DELIST_SOURCES 全部指到 OUT_DIR 下不存在的文件。即使守卫失效，也只会抛 FileNotFoundError，会被精确类型检查判为失败，不会去读真实数据。
- T11 子进程按类型名打印（`GUARD_EXC PermissionError` / `NOSRC_EXC TypeError`），测试按整行逐一断言。

## 4. 排队的 r3 项
- runner（P2-R1、P3-2、P3-7）：
  - `_guard_reason()`：16:40–18:40 窗口、其他对拍进程、fix_sd1 进程，启动时和每个子进程启动前都查一次。命中时这个用例记 REFUSED_GUARD，后面的用例记 NOT_RUN_ABORTED，all_pass=false。
  - 轮询改为每 0.2 秒读一次 VmRSS 和 VmHWM，任一超过上限就 kill。
  - 子进程结束后，worker 自报的 ru_maxrss 或父进程 RUSAGE_CHILDREN 超过上限，记 FAIL_RSS。
  - `_compare` 比较 parquet 时同时比 index 的值、dtype 和 names。
  - 文档写明父进程也要带 PYTHONDONTWRITEBYTECODE=1，并在 14:00 ET 前启动。
- 测试（P3-5）：dont_write_bytecode 的检查移到 import ok_runner_pin 之前。
- ok_runner_pin_v2 r3：
  - P2-V1：检查 8–15 只作用于严格集。传了 `primary_ok` 时严格集就是这一份（它必须钉住本脚本）；没传时是所有钉住本脚本的 .ok。其余列出的 .ok 按 v1 c7805d9a 语义检查（用 v1 方式解析，容忍 CR，不要求 expires_et）。
  - P2-V2：allow_real_data=false 只在 scope=selftest 时要求。
  - P3-8：严格集中，请求的 mode 必须写成精确的 'true'；任何重复键都拒绝；scope 必须写出。
- FE 复牌日闸门（Arch P2-R2 / 探针 9b81bff1；tradability L47–52、L380–451、L454–560、L563–575）：
  - 新增 `resume_gate` 参数，默认 'require_announced'，这是真实 FE 运行唯一可用的主口径。闸门列是 resume_announced：cs_panel_v2 有这一列就直接用；没有就按 (ts_code, trade_date) join Data 的 suspend_flags_v2。join 时 `resume_flags_sha256` 必填，且必须等于文件的 64 位 sha。缺 sha、缺文件、sha 不符都拒跑。
  - 'is_resume_day_fallback' 即 r2 的做法，只作披露，打 ENTRY_GATE_IS_RESUME_DAY_T1600 和 IS_RESUME_DAY_MILD_LOOKAHEAD 两个标。轻度前视的说明是：is_resume_day 用了当日收盘后（t 16:00）的成交信息，但只用来挡当日新买，不参与买卖、仓位或打分，只会减少入场，所以偏保守。
  - 'off' 是闸门关闭的敏感性档，打 RESUME_GATE_OFF_SENSITIVITY。
  - 每个 FE 结果的 `summary['resume_gate']` 都给出：逐年被挡的新开仓数；两列都有时，其中 is_resume_day 但没有 R 记录的逐年数；以及来源和 sha。
  - `fe_resume_gate_sensitivity()` 和 `research/wb_sd1_books.book_ret_sd1_gate_sensitivity()` 输出主口径与闸门关闭的对照，含逐年收益差。
  - 以上都只是代码路径，本轮没有运行。T16 新增 4 个合成用例。

## 5. py_compile 与静态扫描
- py_compile（cfile 写到 /tmp，随即删除）：execution_sd1、tradability、delist_accounting、wb_sd1_books、test、runner、static_check、ok_runner_pin_v2 共 8 个文件，全部 OK。
- 静态扫描 `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts_eng/sd1_pit_static_check.py`：**rc=1**，31 条命中，其中 21 条是历史引用（PREEXISTING），**10 条 VIOLATION**。
  - 10 条全部出自其他 agent 02:37 ET 改过的两个研究文件：research/g1g5_imax_intraday_alpha.py（101600f6…，L369/377/378/447/625）和 research/g1g5_sue_desens_cs_alpha.py（ccde59eb…，L398/406/407/476/692），token 都是 delist_date，属于 Arch bd3abe5c P1-A 的退市截断逻辑。
  - SD1 文件里没有任何新增命中。
  - 原始输出保存在 /workspace/sd1_work/r3_static.json。
  - **影响：T10 的 test_static_check_catches_planted 要求扫描 rc=0，在 Arch 裁定这两个文件之前，r3 selftest 这一项会失败。** 需要 Arch 在两条路里选一条：把这两处列入 PREEXISTING 或白名单（Eng 改扫描脚本，sha 会变）；或者由 AI 改为走会计层。Eng 没有替他们决定。

## 6. 全部文件的新 sha（r3）
| 文件 | sha256 | 相对 r2 |
|---|---|---|
| `quantlab/platform/execution_sd1.py` | 8c7615f7376b4482fe2f011fe08d47b2f2292c28be315659da5c0c5db74b00b1 | r2 35b46c2b |
| `quantlab/platform/tradability.py` | 968def30059826fa80846531b28ce514c9ed548d3c924034f3db31e3091b892e | r2 4d684a48 |
| `quantlab/platform/delist_accounting.py` | 222b63aee4c47827a9f459dc3145bf254a3b8c9e9cd872e66578af44ce87062a | 未变 |
| `research/wb_sd1_books.py` | a2c368408707de2f07ff3dee588bdc8562294d0b7d4e4ea3d8f55f061efb53ef | r2 cadc065a |
| `tests/test_sd1_suspend_delist.py` | 37e850436ffd98f46525f205b8119059e14851186967591f61a0e2fd20c9000a | r2 8305246b |
| `scripts_eng/sd0_parity_runner.py` | b4621ad52fd8448e01025ac15fb5af5a5db44b3bc2a5991b232243218b19af73 | r2 c4d2411c |
| `scripts_eng/sd1_pit_static_check.py` | 3cfc11351f092b145d205628225564cd3c569b4eda2b5862eb854544a55d360a | 未变 |
| `scripts_eng/ok_runner_pin_v2.py` | b7d8ea3f253b4894f10d1089fb2f8edaf751a1a0cd931061b25f59fa11e831f1 | r2 6810b024 |
| `docs/v2/eng_sd1/SD1_SHAS.txt` | 5e572361315b98b3f1a896c23203a1a7e08dc8ecdb8bf02b711afaa71aa80d2b | r2 621a7af4 |
| `docs/v2/eng_sd1/SD1.patch` | fd9a97e608fdf1ff491714419e67c507072a4a9c9b98e9cdf6ac71e4d65ac32c | r2 — |
| `docs/v2/eng_sd1/SD1_r2_to_r3.diff` | 04834a6702a11ab438fde6672a4e8aabc608f42fa3dc9a488f15c8cc7cf52210 | r2 — |
| `docs/v2/eng_sd1/SD1_vs_execution_reference.diff` | 2c7e01f65c2e9dacf44485fc4348253cdd6b2e057b9cd56bc29c2cc9b23ba834 | r2 — |

未变的文件：execution.py 373fed309f055888e83572d3fbef8f5b5052ebfcb208307962a272bca6fc486c；`__init__.py` bfdfa63cbd7f39d7f0b1eb5a9b91ca00a30bdbd21e31ef3b90d89ac6080e99fc；ok_runner_pin.py c7805d9a78e4f5478fa4c9e3becda48e76453ee0889b4f7027009a676c3e2485。

## 7. 重签申请
- **ARCH_SD1_TEST.ok**：键与已签的 4975aac8 完全相同。只有三个值要换：
  - runner_sha256_test_sd1_suspend_delist = 37e850436ffd98f46525f205b8119059e14851186967591f61a0e2fd20c9000a
  - dep_sha256_execution_sd1 = 8c7615f7376b4482fe2f011fe08d47b2f2292c28be315659da5c0c5db74b00b1
  - dep_sha256_tradability = 968def30059826fa80846531b28ce514c9ed548d3c924034f3db31e3091b892e
  - 其余 65 个 dep 实测未变。新的 signed_et 和 expires_et 由 Arch 定。
  - 命令不变：`cd /workspace/QuantLab && env -u QL_SD1_REAL_DATA PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python -m pytest tests/test_sd1_suspend_delist.py -q -p no:cacheprovider`
  - 注意：T10 静态扫描子项在 §5 的问题裁定前会失败。
- **ARCH_SD1_EXEC.ok**：等单测回执之后再签。新 runner = b4621ad52fd8448e01025ac15fb5af5a5db44b3bc2a5991b232243218b19af73，所以 out_tag 必须以 b4621ad5 结尾。dep_sha256_execution_sd1 和 dep_sha256_tradability 同上，其余键不变。
- 新清单 docs/v2/eng_sd1/SD1_SHAS.txt = 5e572361315b98b3f1a896c23203a1a7e08dc8ecdb8bf02b711afaa71aa80d2b，两份草案已更新，作废说明也写在里面。
