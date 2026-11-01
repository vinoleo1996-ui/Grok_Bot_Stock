# Arch 审查：Eng SD1 停牌/退市修复实现（未运行）

- 写于 2026-10-18 01:47 ET（Arch，按 `date` 实测）。被审对象是 Eng 回执 `docs/v2/ENG_SD1_IMPL_RECEIPT_ZH.md`（sha256 ffe236a90f6fc94f26a8bf9fce3ec2c81657f427979caec798745ccaa9fc18cd）以及它列出的全部文件。规格为 `docs/v2/ARCH_ENGINE_SUSPEND_DELIST_FIX_SPEC_ZH.md`（2e428f3956fcb6d2de8204a0b7226242763045afdd280a4d1e860bc6d0fbdb0b，已复算一致）。
- 本次审查只做了只读核对、`py_compile`（输出到 /tmp，不在仓库里留 pyc），以及重跑一次只读的静态扫描 `sd1_pit_static_check.py`（只打印，不写盘）。**没有运行 SD1、对拍脚本或 pytest，也没有 import 任何旁路模块。**没有改 Eng 的任何文件，没有写 .ok。live=false，promotion=false。

## 0. 结论

**判定：没有 P0；有 P1，两份 .ok 都暂缓，不写。**

- **纸面安全成立。**
  - 主干 `quantlab/platform/execution.py` = 373fed30…486c，`quantlab/platform/__init__.py` = bfdfa63c…99fc，都与 git HEAD e7b240d 逐字节一致。
  - `/workspace/sd1_orig` 里的原版副本也与 HEAD 一致。
  - 现有代码没有任何地方 import 这 4 个旁路文件。
  - 纸面闭包 156 个文件的 sha 全部与 Eng 清单一致；01:15 之后被改过的只有 execution.py，它在 01:33:21 还原，现在就是 373fed30。
- **SD0 默认值等于旧行为：静态上成立。**
  - 实际 diff 与 Eng 提供的参考 diff 逐字节相同。
  - 所有 SD1 分支都有开关把守，默认值一个都进不去，返回 dict 的键也与旧版相同。
  - 这一点还要等真实对拍来证明，而对拍脚本现在跑不出结果，见 P1-1。
- **暂缓 .ok 的原因：**
  - 对拍脚本的 SD0 子进程一定会自我拒跑（P1-1）；
  - 对拍脚本的门控不检查 allow_*，模块 sha 可以不钉，也接受 8 位前缀（P1-2）；
  - pytest 文件完全没有 .ok 门控（P1-3）。
  - 按"优先要求补门控"的原则，这次不出只记录用的 .ok。
- **研究套件**：要等纸面套件通过后再审，本轮不放。

## 1. sha 核对（全部 64 位复算）

| 文件 | 申报 | 实测 | 结论 |
|---|---|---|---|
| quantlab/platform/execution_sd1.py | 37c5b22823f72dc8717b1d680602de033cf4f274110f48d0f5f8db53db4597ec | 同 | ✓ |
| quantlab/platform/tradability.py | 20f0423aa5a47b62c4b0ae01bb6f86a3e0b5d431845e4a4b43e3d24c6d87196a | 同 | ✓ |
| quantlab/platform/delist_accounting.py | 895efd2f502743954c018125b3f917f346ce5fc53f2eb8aac5acbde3271c2dd4 | 同 | ✓ |
| research/wb_sd1_books.py | 581e94f41732600ae42fd3903ee6fed8c5a50b5bd656a4427635741b0508a000 | 同 | ✓ |
| tests/test_sd1_suspend_delist.py | 6ae81f061408f45f0cbda23b963cc786174759221f79f630dcd6ded14223635b | 同 | ✓ |
| scripts_eng/sd0_parity_runner.py | 84510915e777b47990257bdaa76a4fea101cdc57911cfeb65b698701b1ace361 | 同 | ✓ |
| scripts_eng/sd1_pit_static_check.py | 5c7d4d54e906566971597c4f6d68939eb55e5f5d76e954c062406952bd74106c | 同 | ✓ |
| quantlab/platform/execution.py | 373fed309f055888e83572d3fbef8f5b5052ebfcb208307962a272bca6fc486c | 同，且等于 `git show HEAD:` | ✓ |
| quantlab/platform/__init__.py | bfdfa63cbd7f39d7f0b1eb5a9b91ca00a30bdbd21e31ef3b90d89ac6080e99fc | 同，且等于 `git show HEAD:` | ✓ |
| FE research/g1g5_fund_resid_alpha.py | 2b49b10b…916e | 同（= sd1_orig 副本） | ✓ |
| LC research/leaf_selfcheck_common.py | 218b61cf…054 | 同（= sd1_orig 副本） | ✓ |
| ADG research/alpha_decay_gate.py | a877cec5…a97 | 同（= sd1_orig 副本） | ✓ |
| **scripts_eng/ok_runner_pin.py** | **b302911bc0ae1058…9244263** | **c7805d9a78e4f5478fa4c9e3becda48e76453ee0889b4f7027009a676c3e2485** | **✗ 清单过期（P1-4）** |
| docs/v2/eng_sd1/SD1.patch | 7a3abf11…c82c | 同 | ✓ |
| docs/v2/eng_sd1/SD1_vs_execution_reference.diff | fb2d57da…717b | 同；与现场 `diff -u execution.py execution_sd1.py` 逐字节一致 | ✓ |
| docs/v2/eng_sd1/pit_static_check.json | 328e03bf…488c | 同；Arch 重跑一次，结果 JSON 完全相同（8 条命中，0 违规） | ✓ |
| 纸面闭包 156 个文件（paper_closure_sha256 行） | — | 156/156 一致 | ✓ |

- **ok_runner_pin.py 的出入**：文件 01:38:57 被改写（SD1_SHAS.txt 写于 01:38:05，比它早）。和 `_recovery/eng/scripts_eng/ok_runner_pin.strict_b302911b.py` 比，新版是按 Arch 审查 4698a2c1 做的硬化：只收 64 位、重复键拒跑、live/promotion 必须为 false、支持 modes/deps、缺 .ok 就拒跑。Arch 01:46 已核实这份 c7805d9a 没有绕过。这次改动本身没问题，问题只在 SD1_SHAS.txt 没跟着更新。
- **参考信息（P3，不属于 SD1）**：纸面闭包里有 11 个文件与 git HEAD 不同、33 个不在 git 里，包括 v2_multisleeve_book.py、cli.py、weight_long_table.py 等。它们的 mtime 都在 01:12–01:14 的恢复窗口内，是之前就有的工作区状态，与 SD1 无关。所以纸面基线应理解为"当前工作区 + 闭包 sha"，不是 git HEAD。

## 2. 旁路隔离和 8 条历史引用

- **import 检索**：在 quantlab、research、scripts、scripts_eng、tests、services、qlab_b、rev 和根目录 *.py/*.sh 里，搜 `execution_sd1|tradability|delist_accounting|wb_sd1_books`。
  - 排除 SD1 自己的 7 个文件之后，剩下的命中全是变量名、函数名（如 `load_tradability_panels`、`tradability=`），没有一处 import 这 4 个模块。
  - AST 检查：`tradability` 只 import `delist_accounting` 和 `execution_sd1`；`delist_accounting` 不 import 任何 quantlab 模块；`execution_sd1` 只在函数内 import futures、margin、ledger、contracts、v2_readers、smallcap.sim，不 import `quantlab.platform.execution`，不会污染主干。
- **8 条历史引用（A9）**：逐行到源文件核对过，**确认都不属于策略层使用退市信息**，可以保留为 PREEXISTING。

| 文件:行 | 用途 | 判定 |
|---|---|---|
| quantlab/universe/mask.py:8 | instruments 合约字段列表（docstring）；mask 代码里没有其他 delist 引用 | ✓ |
| research/ai_hiliq_pool_review_x2.py:27/28 | AI 池事后复核审计（退市计数），不是选股 | ✓ |
| research/v3_a2_etf_share_demand_report.py:22/32 | ETF fund_basic 的 delist_date，不是个股 | ✓ |
| research/v3_a4_sealed.py:12/25/27 | 可转债 cb_basic 的 delist_date，用于最后成交日之后的退出估值（正常兑付或违约回收），属会计层；该封存运行已结束 | ✓ |

- **静态扫描的范围缺口（P2-5）**：SCOPE 没有覆盖 `quantlab/portfolio/`（只含 v2_constructor、v2_rebalance 两个文件）、`quantlab/beta/` 和 `scripts/`。Arch 手工搜了这些目录：quantlab/portfolio 和 quantlab/beta 没有命中；scripts/ 里 smallcap_reconcile、smallcap_survivorship_b1、build_* 用到 delist_date，都是生存偏差审计或数据构建脚本，不是选股。SCOPE 应扩大，并把这些登记为白名单。

## 3. 代码与规格、裁定逐项对照

| 项 | 实现 | 判定 |
|---|---|---|
| **SD0 = 旧行为** | `engine_version` 只有在 halt=legacy、limit=open_touch、delist=legacy_lastmark、force_sell=False 时才是 SD0。SD0 下不调用 `_sd1_delist_plan`，`FS_FROM` 为空，`SD1_HALT` 为假；涨跌停分支在 open_touch 时与原代码等价；只多算了 `HI/LO` 两个数组，不影响结果；返回键不变 | ✓（静态）。实证要等 T9 和对拍 |
| **PIT：选股不用当日成交量** | 引擎的停牌判定 §3.1(3) 用了当日成交量（`suspended & ~has_vol`），这是规格 §3.1 本身的写法，**只决定成交是否可行，不进选股**。LC 适配器的 `sus = vol<=0` 同样只用于成交可行性。FE 适配器只凭"无行情"判停牌。选股、权重、掩码代码没有新增任何读取 | ✓。P2-3 要求披露，suspend_flags_v2 落地后改用 halted_fullday / resume_announced |
| **退市会计与回收率开关** | FORCED_*、UNKNOWN 在 last_trade_date 之后第一天按 `回收率 × 最后可成交收盘价` 结算，默认 0；`run_delist_sensitivity` 并列 0、0.3、0.7；wb 引擎相同（`rel=回收率`）；回收率超出 [0,1] 直接报错 | ✓ 符合裁定 2 |
| **cash 与按比例** | `strategy_v1_sd1(track='core')` → cash，其他 → renorm；`_sd1_renorm` 在 cash 模式下把 B 的权重留在分母里（预算留现金），renorm 模式下剔除（按比例分给其余股）；买单现金不足时按比例缩放（`PRORATA_BUY_SCALE`），不再按代码顺序挤 | ✓ 符合裁定 1。P2-2：track=None 时静默取 renorm，Core 漏传就会算错 → 要求 track 必填 |
| **强制卖出时点** | `force_sell_from` = max(period_start, 改名 ann_date)；从该日起每天开盘挂出全仓卖单，受跌停和停牌约束，按实际成交价卖出；整理期内的股票不买入（B 标为 DELIST_PERIOD） | ✓ 符合裁定 3 和规格 §3.5 第 1 步 |
| **UNKNOWN** | 合并、私有化类没有公告来源的记 UNKNOWN，按 FORCED 处理（回收 0），打标 `UNKNOWN_AS_FORCED` 和 `MA_UNVERIFIED_NO_ANNOUNCEMENT_SOURCE`。v1 表路径：60 只疑似合并私有化里，先用面值规则（最后 20 个收盘都 < 1）剔出面值退市 | ✓ 符合 Arch cs_panel 审查"56 只无来源 = UNKNOWN、按强制退市回收 0" |
| **needs_manual_source（002509）** | `_derive(v2=True)` 只在 typ==UNKNOWN 时把 needs_manual_source 用于打标；如果 v2 表把 002509 标成进入整理期，并带人工起点 20200604，就会得到 FORCED_PERIOD 和 force_sell_from，**触发强制卖出** | **✗ P1-5（潜在）**：违反"002509 needs_manual_source=True 不得触发强卖"。现在 v2 表还不存在（实测 data/v2/ref/stock_delisted_v2.parquet 不在），v1 路径下 002509 是"疑似合并私有化"、整理期 0 天，不会强卖；所以不影响 SD0 对拍，但正式 SD1 真实数据运行前必须修 |
| **hiliq_carry 记账** | 主引擎：停牌日拒单、NAV 沿用上一估值，复牌日按实际价计入跳空，与"停牌日记 0、复牌日记真实收益"一致。wb 引擎用 `ffill(limit_area="inside")`，区间内停牌当天记 0，复牌日计完整跳空，T1 覆盖。**FE 适配器只读 cs_panel_v2 的 ret 和 ret_on，没读 hiliq_carry，也没读 is_resume_day** | 记账语义 ✓。**P1-6（潜在）**：缺复牌日入场闸门（Arch 裁定"is_resume_day 当日不新买"），也没有核对 hiliq_carry 与记账是否一致；FE 真实运行要等 cs_panel_v2，所以不挡对拍 |
| **cs_panel_v1 拒读** | `fe_book_ret_sd1` 找不到 v2 文件就 FileNotFoundError，只有显式 `allow_cs_panel_v1=True` 才回退，并打标 | ✓。但 Eng 说"T13 已写好"不准确：T13 测的是复牌行检查函数，**没有测这条拒读逻辑**（P1-7） |
| **T13 真实数据用例** | `traded = panel`，等于拿面板自己当成交集，`missing` 永远是 0，这个测试不可能失败 | **✗ P1-7（潜在）**：成交集必须来自独立来源（合并日线 vol>0，或 suspend_d 的 R 记录） |
| **A5 数据源按"文件是否存在"自动切换** | delist_events_v1 > stock_delisted_v2 > v1。Data 一落盘，结果就会静默改变口径 | P2-4：结果里记下 type_source 和该表的 sha256；正式运行的 .ok 要钉住这张表的路径和 sha |

## 4. A1–A11 裁定

**Arch 直接裁定：**

- **A1 同意。** 现金缓冲 = (1−Σw)·NAV_open，所以剩余预算 = Σw·NAV_open − V_F，与规格 §3.2 第 2 步的算式等价。只有 F、B、BP 非空时才归一，没有冻结时与 SD0 订单一致。
- **A2 同意。**
  - F 的卖单照旧 carry，B 的买单不 carry。
  - cash 模式下复牌后不补买，等下一个信号日重算，符合规格 §3.2 第 5 步和裁定 1 的"留作现金"。
  - 要在事件表里记清"被拦预算留现金的天数"，方便披露。
- **A3 同意。** 归一按执行日开盘价换算股数；开盘价在开盘时已知，属于 PIT。只在触发归一时与 SD0 有差别，须写进披露。
- **A4 同意。** SD1 的冻结和退市逻辑只支持 next_open 和 next_vwap；fill=close 报 NotImplementedError，不会静默退回旧逻辑。ADG 的收盘成交走 wb 引擎，不受影响。
- **A5 同意，附两个条件。**
  - 合并、私有化类没有公告来源时记 UNKNOWN，按 FORCED 回收 0，符合 Arch cs_panel 审查。
  - 条件一：needs_manual_source=True 的行一律不触发强卖（P1-5）。
  - 条件二：记下数据源和表的 sha（P2-4）。
  - 至于 UNKNOWN 核销是否计入 G2 门槛，交主 Agent（E-1）。
- **A6 同意。** 不推断退市，尾部 NaN 打标 TAIL_NAN_NOT_IN_TABLE；SD1 必须显式传入退市表（可以是空表）。
- **A7 同意。** TO = Σ|ex_t − ex_{t−1}|，无冻结时等于旧算法；CASH_OUT 按 cps/last_close 估值，换股按价值比折算（权重账本里没有整手概念）。
- **A8 临时同意，打标披露。**
  - FE 和 ADG 关闭涨跌停，偏离了规格 §3.4"权重型引擎同样执行 open_touch"，结果会偏乐观。
  - ADG 维持冻结预注册的收盘成交，不改。
  - FE 等 cs_panel_v2 带上原始涨跌停价，或接入 stk_limit 后，必须切到 open_touch。
  - 这项改变叶评价的经济口径，同时报主 Agent（E-2）。
- **A9 确认。** 8 条都是 PREEXISTING、不涉选股，见 §2。
- **A10 同意。** SD1 不接入 book_smoke 和 run_book（v2_multisleeve_book 在纸面闭包里）。正式 SD1 回测要另写 runner、另批 .ok，并按规格 §3.7 并列 SD0 和 SD1 两列。
- **A11 同意。** suspend_flags_v2 落地前 halt_extra=None，只用 open_status 加成交量判定，打标披露。suspend_flags_v2 要等 Data 的 D-2 拿到 .ok 并交付后接入，接入时开盘前的逻辑用 resume_announced。

**上报主 Agent（涉及经济口径）：**

- **E-1（A5）**：UNKNOWN 按 FORCED 回收 0 核销的事件，是否计入规格 §4 的 G2 门槛（"出现任何 DELIST_WRITEOFF 且单笔核销权重 ≥ 1%，交主 Agent 重裁"）？
  - 真实的换股合并本来是保值的，按 0 核销是保守偏差，可能把结果误推到 G2。
  - Arch 建议：UNKNOWN 核销单列 DELIST_WRITEOFF_UNKNOWN，不单独触发 G2，但并列 MA_FALLBACK_LAST_CLOSE 口径作为对照。
- **E-2（A8）**：FE 和 ADG 在 wb_SD1 里暂不执行涨跌停，偏离规格 §3.4，叶评价偏乐观。
  - Arch 建议：临时接受，打标 LIMITS_UNAVAILABLE；cs_panel_v2 补上原始涨跌停价后，FE 改成 open_touch 并重算受影响的叶（只作披露）。

## 5. 运行脚本门控审查

### 5.1 `scripts_eng/sd0_parity_runner.py`（84510915…）

**做得对的：**
- 缺 .ok 就拒跑；
- 用 ok_runner_pin 钉本脚本 sha；
- 必须有 `allow_suite=<suite>`；
- execution.py 必须等于 373fed30；
- 输出只写 `output/_sd0_parity/<suite>_<时间戳>/`，目录非空就拒；
- B4 和 S6 的权重按 FROZEN_CONFIG 校验 sha（Arch 实测 4 份都一致）；
- 子进程串行执行，退出码非 0 表示失败；
- book_smoke 只写 `--out` 和 `--receipt`，两者都在 scratch 目录下（Arch 读了 book_smoke.run 和 run_book 的写盘点核实）；
- 不调用纸面 CLI，不改主干（`M.WINDOWS` 只在子进程内存里改）。

**P1 缺陷：**

- **P1-1 SD0 子进程一定拒跑，对拍出不了结果。**
  - `quantlab/platform/__init__.py` 第 47 行无条件执行 `from quantlab.platform import execution`。
  - WORKER 先 `import quantlab.platform`，于是 `preloaded` 恒为 True，`engine=="sd0"` 时直接 `REFUSED`。
  - 结果每个用例都是 RUN_ERROR，退出码 1。不会污染任何东西，但得不到逐位证明。
- **P1-2 门控不合格：**
  - (a) `enforce(__file__, [OK])` 没有传 modes，所以 .ok 里的 allow_full / allow_smoke 根本不检查；
  - (b) `module_sha256[...]` 行是可选的，有就核、没有就放过，而且只要求 8 位，用 `startswith` 比对；
  - (c) 没有用 deps 钉住 ok_runner_pin、`__init__`、book_smoke、v2_multisleeve_book 和各权重文件；
  - (d) 输出目录不受 .ok 约束；
  - (e) 子进程不复核自己实际 import 的引擎文件 sha（门控检查和子进程加载之间有时间差）。
- **P1-4**：SD1_SHAS.txt 里 ok_runner_pin 的 sha 已经过期（b302911b，现在是 c7805d9a）。
- **P1-8 paper 套件的用例集不固定。** capacity_adv 用 `glob(...paper_2*.parquet)` 取最新文件（现在是 `…paper_20261014_r2.parquet`，e03028ee…c44c）。10-19 纸面跑完以后，这个文件可能换成别的，用例集就会变。

**P2：**
- **P2-1 内存**：RSS 只在子进程结束后用 ru_maxrss 记录，没有硬上限；要加 /proc 轮询，超过 1536MB 就杀掉并记 FAIL_RSS。
- **P2-6 比对**：`_compare` 只做单向比对，sd0 多出来的文件发现不了；parquet 比较用 `np.array_equal`，没设 equal_nan，遇到 NaN 会误判失败（这个方向偏保守）；summary.json 只比 metrics。

### 5.2 `tests/test_sd1_suspend_delist.py`（6ae81f06…）

- **P1-3：完全没有 .ok 门控**，任何人都能直接 `pytest`。
- 内容是合成数据单测，不碰真实收益。T13 的真实数据用例默认跳过（需要 QL_SD1_REAL_DATA=1 且 cs_panel_v2 存在）。
- **写盘情况**：
  - tempfile 只用于 T10；
  - T10 会用子进程跑静态扫描（只打印，不写盘）；
  - pytest 默认会在仓库根目录写 `.pytest_cache`，在 tests/ 和 quantlab/platform/ 下写 `__pycache__`（T11 还会写 `.opt-1.pyc`）。

## 6. 并发（01:47 ET `ps`）

- tie-sens（PID 90241）已退出，看不到 Alpha 重算或其他研究进程。
- 只有 Data 的采集进程在跑：`nightly_update --steps tier3`、`tier3_daily_snapshot`（写 data/v2/tier3_daily），以及之前的 `remaining_after_stk_surv`、`relay_outage_backfill`（写 data/v2/events）。它们写的路径和 book_smoke 读的数据（etf、cb、合并面板）没有重叠。
- 正式放行时的条件：串行执行、`nice -n 10`；不得与任何研究运行或 Data 重建（D-1~D-4）同时跑；对拍前后记录 book_smoke `HASH_FILES` 的 sha，前后一致才算有效。

## 7. P 清单

| 级别 | 编号 | 内容 | 是否挡 .ok |
|---|---|---|---|
| P0 | — | 无 | — |
| P1 | P1-1 | 对拍脚本的 SD0 子进程一定拒跑（`__init__` 预先 import 了 execution），对拍不可能产出结果 | 挡 |
| P1 | P1-2 | 对拍门控：不查 allow_*；module_sha 可选且收 8 位前缀；没钉 deps；输出目录不受 .ok 约束；子进程不复核引擎 sha | 挡 |
| P1 | P1-3 | pytest 文件没有 .ok 门控 | 挡（条目 2） |
| P1 | P1-4 | SD1_SHAS.txt 里 ok_runner_pin 的 sha 过期（b302911b → c7805d9a） | 挡（清单必须准确） |
| P1 | P1-8 | paper 套件的 capacity_adv 延伸权重靠 glob 取最新，用例集不固定 | 挡 |
| P1（潜在） | P1-5 | needs_manual_source=True（002509）在 v2 路径下会触发强卖 | 不挡对拍；挡任何 SD1 真实运行 |
| P1（潜在） | P1-6 | FE 适配器没有 is_resume_day 入场闸门，没有核对 hiliq_carry | 不挡对拍；挡 FE wb_SD1 真实运行 |
| P1（潜在） | P1-7 | T13 真实用例是同义反复（traded = panel）；cs_panel_v1 拒读没有单测 | 不挡合成单测；挡 T13 真实数据运行 |
| P2 | P2-1 | RSS 没有硬上限（只事后记录） | 建议并入 P1-2 一起修 |
| P2 | P2-2 | `strategy_v1_sd1(track=None)` 静默取 renorm；Core 漏传就会算错 | — |
| P2 | P2-3 | 停牌判定用当日成交量（只用于成交可行性），须披露；suspend_flags_v2 落地后切换 | — |
| P2 | P2-4 | 退市数据源按文件是否存在自动切换；须在结果里记录 type_source 和表 sha，正式 .ok 钉住 | — |
| P2 | P2-5 | 静态扫描范围漏了 quantlab/portfolio、quantlab/beta、scripts/ | — |
| P2 | P2-6 | `_compare` 单向；没设 equal_nan；summary 只比 metrics | — |
| P2 | P2-7 | `load_halt_extra` 用字符串过滤 trade_date，如果表里是整数会报错；`_period_ann` 靠名字规则（以"退"结尾或"退市"开头）识别整理期 | — |
| P3 | P3-1 | 纸面闭包里 11 个文件与 HEAD 不同、33 个不在 git 里（01:12–01:14 恢复窗口之前就有，与 SD1 无关）；纸面基线 = 工作区 + 闭包 sha | — |

## 8. Eng 必须做的修改（改完重钉 sha、重新申请）

1. **P1-1 注入顺序。** WORKER 在 `import quantlab.platform` **之前**，用 `importlib.util.spec_from_file_location("quantlab.platform.execution", ROOT/"quantlab/platform/execution_sd1.py")` 加载旁路引擎，放进 `sys.modules["quantlab.platform.execution"]`，再 import 包。
   - 跑完要断言 `M.run_weight_schedule.__code__.co_filename` 以 `execution_sd1.py`（sd0）或 `execution.py`（pristine）结尾。
   - 子进程对自己实际加载的引擎文件重新算 sha256，打进输出 JSON；父进程核对它等于 .ok 里钉的值。
   - pristine 子进程同样要断言加载的是 373fed30。
2. **P1-2 门控。**
   - 改成 `ok_runner_pin.enforce(__file__, [OK], modes=("full",), deps={...})`，deps 至少包括：`execution`、`execution_sd1`、`tradability`、`delist_accounting`、`platform_init`、`ok_runner_pin`、`book_smoke`、`v2_multisleeve_book`，以及每个用例的权重文件。
   - `module_sha256[...]` 不再可选，换成 dep_sha256 的 64 位精确比对，去掉 `startswith`。
   - 增加 `.ok` 键 `out_root=output/_sd0_parity` 和 `out_tag=<tag>`：输出目录 = `output/_sd0_parity/<suite>_<out_tag>`，必须不存在，用 `mkdir(exist_ok=False)` 排他创建；out_root 不符就拒跑。
   - `allow_smoke` 在 .ok 里必须显式写成 false，脚本要核对。
3. **P1-3 pytest 门控。** 在测试文件顶部、import 旁路模块**之前**调用 `ok_runner_pin.enforce(__file__, [ROOT/"docs/v2/eng_sd1/ARCH_SD1_TEST.ok"], modes=("smoke",), deps={execution, execution_sd1, tradability, delist_accounting, platform_init, ok_runner_pin, sd1_pit_static_check})`，失败就 `raise SystemExit`。
   - QL_SD1_REAL_DATA=1 时，.ok 还必须有 `allow_real_data=true`，否则拒跑。
   - 运行命令固定为 `PYTHONDONTWRITEBYTECODE=1 nice -n 10 python3 -m pytest -q -p no:cacheprovider tests/test_sd1_suspend_delist.py`。
4. **P1-4** 更新 SD1_SHAS.txt：ok_runner_pin = c7805d9a78e4f5478fa4c9e3becda48e76453ee0889b4f7027009a676c3e2485；runner 和测试文件改完后的新 sha 也要写进去。
5. **P1-8** paper 套件用例改成固定清单：权重路径和 sha 写死，或由 .ok 的 `dep_sha256_w_<name>` 提供；去掉 glob。
6. **P2-1** 父进程每秒读一次子进程的 `/proc/<pid>/status` VmRSS，超过 1536MB 就 kill，记 FAIL_RSS；脚本启动时 `os.nice(10)`。
7. **P2-6** `_compare` 改成双向比对（两边文件集合必须相同）；float 列用 `equal_nan=True`；summary.json 去掉时间戳和 run_id 之后整体比较。
8. **P1-5**（真实运行前）：`_derive` 里 needs_manual_source=True 的行，`force_sell_from` 强制设为 NaT，打标 `NEEDS_MANUAL_SOURCE_NO_FORCE_SELL`；加一条合成单测。
9. **P1-6**（FE 真实运行前）：FE 适配器读 cs_panel_v2 的 `is_resume_day`，当日新买（之前没有持仓）按 B=RESUME_DAY_ENTRY_GATE 处理；读 `hiliq_carry` 并断言：持仓穿越停牌时，复牌日收益已经计入。
10. **P1-7**：T13 真实用例的成交集改用独立来源（合并日线 vol>0，或 suspend_d 的 R 记录）；另加单测：没有 v2 文件且 allow_cs_panel_v1=False 时抛 FileNotFoundError，为 True 时打标 `cs_panel_v1(D-1 gap)`。
11. **P2-2** `strategy_v1_sd1` 和各适配器的 `track` 改成必填，传 None 就报错。**P2-4** 在 sd1_events 和返回结果里记录 `delist_source` 和表的 sha256。**P2-5** 静态扫描的 SCOPE 加上 quantlab/portfolio、quantlab/beta、scripts，并把相关审计、构建脚本登记为白名单。

## 9. .ok 草案（**本轮不写文件**；P1-1/2/3/4/8 修好、Arch 复审通过后才落盘）

对拍 .ok，路径 `docs/v2/eng_sd1/ARCH_SD1_EXEC.ok`（runner 期望的路径）。下面 `<…>` 的位置要等 Eng 修复后填入新 sha，不得预填：

```
format=quantlab_run_auth_v1
signed_by=arch
scope=sd0_parity_paper
allow_full=true
allow_smoke=false
allow_suite=paper
live=false
promotion=false
runner_sha256[scripts_eng/sd0_parity_runner.py]=<修复后 64 位>
dep_sha256_execution=373fed309f055888e83572d3fbef8f5b5052ebfcb208307962a272bca6fc486c
dep_sha256_platform_init=bfdfa63cbd7f39d7f0b1eb5a9b91ca00a30bdbd21e31ef3b90d89ac6080e99fc
dep_sha256_execution_sd1=<若未改则 37c5b22823f72dc8717b1d680602de033cf4f274110f48d0f5f8db53db4597ec>
dep_sha256_tradability=<若未改则 20f0423aa5a47b62c4b0ae01bb6f86a3e0b5d431845e4a4b43e3d24c6d87196a>
dep_sha256_delist_accounting=<修 P1-5 后新 sha>
dep_sha256_ok_runner_pin=c7805d9a78e4f5478fa4c9e3becda48e76453ee0889b4f7027009a676c3e2485
dep_sha256_book_smoke=1a5fa1aa6ab847bd1ecda4d01bd4bda88b23535edceb91021520261be3e8251b
dep_sha256_v2_multisleeve_book=6adefbeb4e66bdd8856c748180b09fa0fbf071d8fe20f6ccdd70ff37a4a603b4
dep_sha256_w_capadv_20261013=4348877ef927c85197a0068c219ab5a5f5957c7d11451a3ca68b73fd985d5caf
dep_sha256_w_capadv_paper_20261014_r2=e03028ee04f43aa33bc584a7846134d7e9001659655f49ecaaa3e6e5c1afd44c
dep_sha256_w_b4_60w=efcef7c43f919317baf2106f14c704a0d6d9351c910e8776a1d1f4cabf4f4480
dep_sha256_w_b4_100w=4736c030996fc631ec40ddaff9ae0dfb93c147f6191a346f3c0476edd57debf0
dep_sha256_w_s6_60w=6ce63a7939a26e410ff2382d42b58988da4d8ace078f477f85f532c2c344cd9d
dep_sha256_w_s6_100w=b1f9ae65483f0ffd161bc5a69e97b905cf634c26e9a58a88058afbd78f363a41
out_root=output/_sd0_parity
out_tag=<Arch 复审时指定>
exec_serial=true
exec_nice=10
rss_cap_mb=1536
```

- pytest 的 .ok（`docs/v2/eng_sd1/ARCH_SD1_TEST.ok`）结构相同：`allow_full=false`、`allow_smoke=true`、`allow_real_data=false`，钉住测试文件的新 sha 和上面的模块 dep。
- 研究套件在纸面套件全部 PASS_BIT_IDENTICAL 之后再审。
- 时间窗：纸面例程 10-19 17:40 ET 前后各 1 小时内不跑对拍，避免和纸面争资源，也避免 17:00 的 execution.py 复核读到中间状态。

## 附记 B：sd0_parity_runner 4b9c30a4 复审（2026-10-18 01:57 ET，Arch）

- 本次只做了只读核对和 sha256sum，没有运行对拍脚本、pytest 或任何旁路模块，没有 import 旁路模块。
- 审查基线是本文 c39eb016…。被审的是 `scripts_eng/sd0_parity_runner.py`，sha 4b9c30a40c509c64f39332d8e3ed7fd8e591b27fbc642f171f0fe50f86d47a18，以及 `docs/v2/eng_sd1/SD1_SHAS.txt`，sha a8b9df451b12757cdccaf78cec5513a6a2109602df27d3f193d7b81d64a54f2d。两者实测都与申报一致。
- SD1_SHAS 里 10 个 dep 的 sha 全部与现场一致：execution 373fed30、platform_init bfdfa63c、execution_sd1 37c5b228、tradability 20f0423a、delist_accounting 895efd2f、wb_sd1_books 581e94f4、test 6ae81f06、book_smoke 1a5fa1aa、v2_multisleeve_book 6adefbeb、ok_runner_pin c7805d9a。

**结论：P1-1、P1-2（部分）、P1-3、P1-8 仍未修好。`docs/v2/eng_sd1/ARCH_SD1_EXEC.ok` 不写。**

### B1. P1 逐项
| 编号 | 现状 | 判定 |
|---|---|---|
| P1-1 注入顺序 | WORKER 第 124 行仍先执行 `import quantlab.platform`。`quantlab/platform/__init__.py` 第 47 行（bfdfa63c）无条件 `from quantlab.platform import execution`，所以 `preloaded` 恒为 True，`engine=="sd0"` 时第 126–127 行必定 REFUSED。每个用例都会是 RUN_ERROR，对拍仍然不可能出结果。§8 第 1 条要求的 `spec_from_file_location` 预注入、`co_filename` 断言、pristine 断言 373fed30 都没做 | **✗ 未修** |
| P1-2(a) modes | `enforce(..., modes=[f"parity_{suite}"])`，对应 allow_parity_paper/research/unit | ✓ |
| P1-2(b) 64 位精确比对 | 旧的 module_sha256 加 startswith 已删除；10 个 dep 都走 `dep_sha256_*`，由 HEX64 fullmatch 精确比对；另核 execution=373fed30 | ✓ |
| P1-2(c) deps | 10 个模块 dep 齐全，但**权重文件没有钉**：capadv 20261013 和 paper 延伸件都没钉；B4/S6 只对照 FROZEN_CONFIG 自带的 sha，不受 .ok 约束 | ✗ 部分（与 P1-8 一并修） |
| P1-2(d) out_root/out_tag | 输出目录仍是 `output/_sd0_parity/<suite>_<时间戳>`，不读 .ok 的 out_root/out_tag。`root.mkdir(parents=True)` 默认 exist_ok=False，所以末级目录已经是排他创建，但目录不受 .ok 约束；报告 json 用 `write_text`，不是 `"x"` | ✗ 未修 |
| P1-2(d') allow_smoke 显式 | 脚本不检查 `allow_smoke=false` 是否显式写出 | ✗ 未修 |
| P1-2(e) 子进程复核引擎 sha | WORKER 只比对 `Path(E_used.__file__).name`，不对实际加载的引擎文件重算 sha256，父进程也不核对 | ✗ 未修 |
| P1-3 pytest 文件门控 | 测试文件 6ae81f06 没改，第 23–25 行在模块顶层直接 import 旁路模块，没有 enforce。Eng 自己也承认直接 pytest 可以绕过。`--suite unit` 只给 runner 路径加了门控；它的 pytest 子进程也没设 `PYTHONDONTWRITEBYTECODE`、没 nice | **✗ 未修** |
| P1-4 SD1_SHAS 中 gate 的 sha | 已改为 c7805d9a…，并注明旧值 b302911b；新 runner sha 已写入 | ✓ 关闭 |
| P1-8 glob | 第 90 行仍用 `glob("g1g5_capacity_adv_daily_weights_paper_2*.parquet")` 取最新文件。目录里现在有 20261013、20261013_r2、20261014_r2 三个候选，用例集仍不固定 | **✗ 未修** |

### B2. P2 复查
- **P2-1 RSS 看门狗：✗ 未修。** 仍然只在子进程结束后读 `ru_maxrss` 事后记录，没有 /proc 轮询，也不会在超过 1536MB 时 kill；没有 `os.nice(10)`。
- **P2-6 双向比对 / equal_nan：✗ 未修。** `_compare` 仍然只遍历 a 侧，b 侧多出的文件发现不了；parquet 比较用 `np.array_equal`，没设 equal_nan；summary.json 只比 metrics。
- 新增 **P3-B1**：SD1_SHAS 把测试文件写成 `runner_sha256[tests/test_sd1_suspend_delist.py]`，但测试文件里没有 enforce，这一行没有约束作用。门控补上之前，应改标为 dep。

### B3. 主 Agent 裁定并入（以 01:53 ET 最终版为准，取代 01:49 ET 版）
- **E-1。** UNKNOWN 核销单列为 `DELIST_WRITEOFF_UNKNOWN`，主口径按 0 回收。另外并列两种口径，都只作披露：「按最后收盘价转现金」（MA_FALLBACK_LAST_CLOSE），以及回收 0.3/0.7 敏感性。G2 规则如下：
  - UNKNOWN 本身不单独触发 G2；
  - 「有公告核销 + UNKNOWN 核销」合计权重 ≥1% 时，仍然触发 G2。
  - 对实现的要求：sd1_events 和结果里要分开记录有公告与 UNKNOWN 两类核销的条数、权重和金额，并给出合计权重，供 G2 判断。`run_delist_sensitivity` 除了 0/0.3/0.7，还要加 last_close 这一列。
- **E-2。** 不要求 SD1 现在补涨跌停，临时接受，FE/ADG 的产出打 `OPTIMISTIC_NO_LIMIT` 标。在此期间：
  - FE 不得单独作门控依据，以 book_smoke 为准；
  - cs_panel_v2 补上涨跌停价之后，FE 切回 open_touch，受影响的叶重算，只作披露；
  - ADG 保持收盘成交。
  - 本文 §4 A8、E-2 原写的标签 LIMITS_UNAVAILABLE 统一改为 OPTIMISTIC_NO_LIMIT。
- 这两条只影响 SD1 真实运行的口径，不影响 SD0 对拍（SD0 等于旧行为）。

### B4. 待 Eng 修的（修完重报 sha）
1. **P1-1。** 照 §8 第 1 条做：在 `import quantlab.platform` 之前，用 spec_from_file_location 把 execution_sd1 注入 `sys.modules["quantlab.platform.execution"]`。sd0 断言 `run_weight_schedule.__code__.co_filename` 以 execution_sd1.py 结尾，pristine 以 execution.py 结尾。两边子进程都对实际加载的文件重算 sha256 并输出，父进程核对它等于 .ok 的 dep 值。
2. **P1-2 (c)(d)(d')。**
   - 权重文件改为 `dep_sha256_w_<name>`，由 .ok 提供并强制核对；
   - 读 .ok 的 `out_root=output/_sd0_parity` 和 `out_tag`，输出目录为 `<out_root>/<suite>_<out_tag>`，要求 out_tag 以 runner sha8 结尾，用 `mkdir(exist_ok=False)` 创建，报告用 `"x"` 写；
   - 核对 .ok 里显式写有 `allow_smoke=false`。
3. **P1-3。**
   - 测试文件顶部、import 旁路模块之前调 `ok_runner_pin.enforce(__file__, [docs/v2/eng_sd1/ARCH_SD1_TEST.ok], modes=("smoke",), deps={...})`；
   - QL_SD1_REAL_DATA=1 时要求 `allow_real_data=true`；
   - unit 子进程设 `PYTHONDONTWRITEBYTECODE=1`，并 nice 10。
4. **P1-8。** 去掉 glob，用例清单写死路径，由 .ok 钉住 sha。
5. **P2-1 / P2-6。** 每秒读 /proc VmRSS，超过 1536MB 就 kill 并记 FAIL_RSS；启动时 `os.nice(10)`；`_compare` 改为双向比对、`equal_nan=True`、summary 去掉时间戳和 run_id 后整体比较。
6. **E-1 落地**（在 SD1 真实运行前）：见 B3。

### B5. 放行条件（届时写 .ok 时用；本轮不写）
- 起草基础是 §9 草案。改动如下：
  - allow_* 键改为 `allow_parity_paper=true`、`allow_parity_research=false`；
  - pytest 门控进代码后，`allow_parity_unit` 才可以设为 true；
  - 保留 `allow_smoke=false`、`exec_serial=true`、`exec_nice=10`、`rss_cap_mb=1536`；
  - 加上 out_root/out_tag。
- 不得与 Data 的 D-1~D-4 重建重叠，也不得落在 10-19 17:40 ET 纸面例程前后 1 小时内。

live=false · promotion=false · 未写 .ok · 未运行任何 runner/pytest。
