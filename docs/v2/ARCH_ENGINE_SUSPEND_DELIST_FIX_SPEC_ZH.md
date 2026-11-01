# 回测引擎「停牌/退市」修复规格（SD1）

- 写于 2026-10-18 01:01 ET（Arch，按 `date` 实测）。来源：主 Agent 00:49 ET 派发；问题出自 `docs/v2/AI_HILIQ_POOL_REVIEW_X2_ZH.md` 第①节。
- 性质：**只是规格**。Arch 没改任何引擎或主干代码，没跑 book-smoke，没算收益，没建 .ok。实现交 Eng，用新版本号。
- live=false，promotion=false。**纸面轨不动**，FROZEN 配置不动。当前 book_smoke_v1_3 按旧引擎跑完，记分卡标注「停牌/退市偏乐观（SD0）」。
- 附带的只读计数脚本：`docs/v2/audit/arch_engine_suspend_delist_event_count.py`（sha256 6788492193f1…5e7d）。输出 `…event_count.json`（sha256 2cac6017…fb83），峰值 RSS 246MB。

## 0. 结论摘要

1. **主回测引擎**（book-smoke 走 `run_weight_schedule`）在**停牌**上基本正确：停牌日拒单；复牌日按实际价计入跳空；开盘价触及涨跌停时也拒单。
   - 但**退市**没有终值处理：退市后持仓永远冻结，按最后收盘价计入 NAV。
   - 另外，冻结头寸占着的预算没有按比例归一，而是按代码字母序挤出后面的买单。
2. **权重型评价引擎**问题更大，包括 FE.book_ret、LC._ret、alpha_decay_gate 和 leaf_selfcheck_v3 的 IC：
   - 停牌、退市日都可以按最后价调出；
   - 退市后按 0 收益记；
   - 没有涨跌停检查。
   - 另外 Arch 新发现：**cs_panel 系统性缺复牌首日这一行**。X2 内 702 次复牌中，有 701 次缺这一行，复牌跳空的收益因此整段丢失。ADG 的 `pct_change(fill_method=None).fillna(0)` 也会丢掉复牌跳空。
3. 数据上，停牌日历、涨跌停价、退市日期、退市整理期日线都有。缺两样：**退市后三板（退市板块）价格**，以及**吸收合并/私有化的对价表**。所以强制退市在无法卖出时只能保守核销。
4. **推荐核销值：强制退市 = 最后价的 0%（直接归零）**，记分卡并列 30% 和 70% 两档敏感性。吸收合并按换股比例转换，私有化按现金对价；缺对价表时，退化为最后收盘价转现金并打标。
5. 初步事件数（只数次数，基于目标权重，见 §5）：
   - Core v1.3 与 capacity_adv 在 X2 **都没有持有到退市**。持仓期间停牌只有 2–3 段，共 15–19 个持仓日。
   - B4 曾持有广汇汽车（面值退市），但在最后交易日前约两周已经调出。引擎实际持仓文件证实 2024-07-03 已卖出。
   - 结论：对现行 HI_LIQ 策略影响预计很小。对 FULLA 叶评价和 cs_panel 复牌缺口的影响**未计数**，须修后统计。

## 1. 现有代码审计（行号以本文写作时的文件为准）

### 1.1 主回测引擎（book-smoke 路径）

调用链：`quantlab/cli.py:291-292` → `quantlab/portfolio/book_smoke.py:105-150` → `quantlab/portfolio/v2_multisleeve_book.py:487-539 run_book`。

- **加载面板**：个股走 `quantlab/platform/execution.py:1194-1352 load_execution_panels`。
  - 字段含 open/close/volume/amount/limit_up/limit_down（L1226）；
  - 停牌面板 = `open_status ∈ {halted, suspended}`（L1299-1300）。
- **执行**：`run_weight_schedule`（execution.py:623 起），配置 `ExecConfig.strategy_v1`（L343-352）：next_open 成交、enforce_limits=True、unfilled=carry。

| 项 | 现状 | 位置 | 判定 |
|---|---|---|---|
| 缺行情估值 | `Cm = close.ffill(limit_area="inside").ffill()`：区间内停牌沿用上一收盘，**退市后的尾部也无限 ffill** | execution.py:645 | 停牌 ✓；退市 ✗：永远按最后收盘价估值 |
| 停牌判定 | 有停牌面板时：`SUS = suspended \| close 非有限`；无面板时：`close 非有限 \| volume≤0` | execution.py:679-682 | ✓。停牌日在合并面板里**没有行**（实测 002445.SZ 2026-02-13→03-06），close 为 NaN，因此判为停牌 |
| 停牌日成交 | `SUS 或无价 → 拒单，记 reason="suspended"`，买卖都拒 | execution.py:747-749 | ✓ |
| 未成交单 | carry：每日重试，直到下一个信号日清空重算 | execution.py:320、879 | ✓ |
| 复牌 | 开盘估值用实际开盘价（停牌日沿用上一估值），复牌日按实际 close，跳空计入复牌日 | execution.py:813、850-852、920 | ✓ |
| 涨跌停 | 开盘成交价 ≥ limit_up−eps 不买，≤ limit_down+eps 不卖。510300 在 no_limit_codes 里豁免 | execution.py:750-755；v2_multisleeve_book.py:476-479 | ✓（比「一字板」更严，见 §3.4） |
| 退市终值 | 只有转债有 `terminal_price`（按最后收盘价在次日兑付）；个股没有 | v2_multisleeve_book.py:114-128；execution.py:841-849、1399-1403 | ✗：持仓冻结、按最后价计 NAV；卖单每天记一次 "suspended"，永远不成交 |
| 冻结后再平衡 | `desired = tgt × nav_sig / ref`，nav_sig 含冻结头寸的价值；买单受现金约束，**按代码字母序**成交 | execution.py:872-913、740-741、786-795 | ✗(P2)：剩余预算不按比例归一，排在后面的代码系统性少买 |
| 退市前的 PIT | 引擎不读退市信息；池掩码只用当日及以前的数据 | — | ✓ |

### 1.2 Ledger（`quantlab/backtest/ledger.py`，旧 Engine 路径）

- `trade_permission`（L62-89）检查停牌（open_status）和涨跌停：✓。
- `mark`（L127-134）遇到缺价会保留旧的估值价并记 stale。退市后同样永远按最后价估值：✗。
- 当前 Core/B4/capadv 的 X2 结论没有走这条路径，只列出备查。

### 1.3 权重型评价引擎（叶评价、自检、门控）

| 引擎 | 位置 | 问题 |
|---|---|---|
| FE.book_ret | `research/g1g5_fund_resid_alpha.py:125-147` | `rr.fillna(0)`、`on.fillna(0)`（L131）。目标权重直接生效（L139-145），所以停牌、退市当天都能按最后价调仓。没有涨跌停检查。另外 cs_panel 缺复牌首日行，跳空丢失（见 1.4） |
| LC._ret | `research/leaf_selfcheck_common.py:56-70` | 区间内停牌用 `close_to_close_returns` 处理是对的（`quantlab/platform/strategy_feed.py:419-435`）。但退市后的尾部 NaN 被 `.where(cc.notna(),0).fillna(0)` 记成 0（L65-66），等于按最后价退出。没有可交易性检查和涨跌停检查 |
| ADG gross_and_turnover | `research/alpha_decay_gate.py:41-47` | `_close(i).reindex(P.index).pct_change(fill_method=None)` 再 `.fillna(0)`（L45）。**复牌日跳空丢失**：实测 002445.SZ 2026-03-09 复牌 +10.07%，在这里记成 0 |
| leaf_selfcheck_v3 IC | `research/leaf_selfcheck_v3.py:101-113 _pool_panel` | 价格指数用 cs_panel 的 ret 累乘，复牌行缺失，所以前瞻收益丢跳空 |
| v2_s2_book._fast_nav | `quantlab/portfolio/v2_s2_book.py:332-334` | `close.ffill()` 后算 pct_change，退市后按 0 收益记。只用于诊断 |

### 1.4 数据层异常（转 Data 核查）

- **D-1 cs_panel 缺复牌首日行（P1）**：
  - X2 内全天停牌（suspend_d S 类）结束后，第二天在 cs_panel 有行的复牌事件共 702 次，其中 **701 次复牌首日这一行不存在**。例：002445.SZ，2026-02-12 之后直接跳到 2026-03-10，缺 03-09（当天实际成交，收盘 3.06）。
  - 受影响的有 FE.book_ret、leaf_selfcheck_v3 IC、AI 的 HI_LIQ 等权指数。复核这一点的进程峰值 RSS 2447MB，**超过了 1.5GB 上限**，已如实记录；以后改按年分块读取。
- **D-2 停牌标记异常**：
  - 002445.SZ 2026-08-24：合并面板 `tradestatus=0`、`open_status=halted`，但 OHLC 都是 3.37（一字涨停），成交 4.80M 股，suspend_d 当天也没有 S 记录。
  - 这会被误判为停牌，拒掉本可成交的卖单。数量待 Data 全量统计。
- **D-3 退市分类有误**：`data/v2/ref/stock_delisted.parquet` 的「疑似主动/吸收合并/私有化退市(退市前非ST)」8 只里，3 只最后收盘价 < 1 元：广汇汽车 0.78、鹏都农牧 0.36、海印股份 0.62。
  - 广汇汽车最后 20 个收盘都 < 1，经脚本核实属于面值退市。
  - AI 复核文档第①节把广汇汽车列为吸收合并/私有化类，应当更正。
- **D-4 退市整理期标记不一致**：部分「强制退市(进入退市整理期)」行的 `delisting_period_start` 为空、`delisting_period_trade_days=0`，例如 688287.SH、605081.SH、600696.SH。
- **D-5 整理期首日涨跌幅**：沪深规则下，退市整理期首日不设涨跌幅限制。合并面板的 limit_up/limit_down 是否反映这一点，须 Data 核对（东通退 300379.SZ 整理期 limit_ratio_at_open=0.2）。

## 2. 数据可用性盘点（只列实际存在的文件和字段）

| 需要 | 文件 | 字段 | 覆盖 | PIT |
|---|---|---|---|---|
| 停复牌日历 | `data/v2/tushare_raw/suspend_d/YYYYMMDD.parquet` | ts_code、trade_date、suspend_type(S/R)、suspend_timing | 2130 个文件，20180102→20261016；X2 内 S=7900 行、R=1206 行，962 只股票 | 是：按日发布，当日开盘前可知。suspend_timing 非空的是盘中停牌（X2 内 120 行） |
| 停牌状态（面板） | 合并 D0+asof 面板（`load_merged_panel`） | open_status、tradestatus；停牌日无行 | 全 A | 是（open_status_available_at）。见 D-2 |
| 涨跌停价 | `data/v2/tushare_raw/stk_limit/*.parquet`；合并面板 | up_limit、down_limit；limit_up、limit_down、limit_ratio_at_open | 20180102→20261016 | 是：由前收盘决定，开盘前可知 |
| 退市日期 | `data/v2/meta/stock_basic_incl_delisted.parquet` | list_status(L/D)、delist_date | 5912 行（L 5573、D 339）；P 类 0 行 | **否**：available_at=1970 静态参考，只能用于会计层 |
| 退市原因与终价 | `data/v2/ref/stock_delisted.parquet`（manifest sha 90c8934d…） | last_trade_date、last_close、delist_reason_category、entered_delisting_period、delisting_period_start、delisting_period_trade_days、delist_price（= 最后交易日收盘，Tushare 没有独立退市价）、was_st_within_1y_of_delist | 339 只；X2 内最后交易日 86 只：整理期类 41、ST 类 37、疑似合并私有化 8（分类问题见 D-3/D-4） | available_at = 退市日，**事后信息**，只能用于会计层 |
| 退市整理期行情 | `data/v2/delisted/delisted_daily_tushare.parquet`（124 万行）、`delisted_daily_from2015_tushare.parquet`；合并面板 | 完整 OHLCV、pre_close、adj_factor | 含整理期，如 300379.SZ 到 2026-01-21 | 是（日线） |
| 整理期起点 | `data/v2/st_events/namechange_all.parquet`、`tushare_raw/namechange` | name（以「退」结尾）、start_date、ann_date | 全量 | 是（用 ann_date） |
| ST 标记 | `data/v2/st_flags/is_st_daily_2018_2026.parquet`、`st_intervals_tushare.parquet` | — | — | 是 |
| **退市后三板（退市板块）价格** | **不存在**（在 data/v2 和 output/data_v2_bundle 都搜过） | — | — | — |
| **吸收合并换股比例、现金对价** | **不存在** | — | — | — |
| 交易日历 | `data/v2/calendar/trade_cal_sse_pit.parquet` | is_open、pretrade_date | — | 是 |

## 3. 修复规格

### 3.0 版本与开关

- 新引擎标识：**`exec_SD1`**。在 ExecConfig 上新增字段，**不改 `strategy_v1` 现有默认值**。另加工厂方法 `ExecConfig.strategy_v1_sd1()`，相当于 strategy_v1 加下表的 SD1 默认值。
- 旧口径记为 **`exec_SD0`**：所有开关取 legacy 时，必须与现行 NAV **逐位一致**（验收 T9）。

| 开关 | 取值 | SD1 默认 | SD0 值 |
|---|---|---|---|
| `halt_policy` | legacy / freeze_renorm | freeze_renorm | legacy |
| `blocked_buy_budget` | renorm / cash | renorm | （不适用） |
| `limit_policy` | open_touch / one_price_only / off | open_touch | open_touch |
| `delist_policy` | legacy_lastmark / sd1 | sd1 | legacy_lastmark |
| `delist_forced_recovery` | 0~1，乘以最后可成交价 | **0.0** | — |
| `delist_sensitivity` | 元组 | (0.0, 0.3, 0.7) | — |
| `delist_force_sell_in_period` | bool | True | False |
| `ma_consideration_table` | 路径 | `data/v2/ref/delist_consideration.parquet`（待 Data 建） | — |
| `ma_fallback` | last_close_cash | last_close_cash（打标） | — |

- **权重型评价引擎**（FE、LC、ADG、leaf_selfcheck_v3）统一改为调用一个新的共享函数 `quantlab.platform.tradability.weight_book_returns(weights, panels, policy)`，版本号 `wb_SD1`。
  - 不再各写一套 fillna(0)。
  - 旧函数保留，输出打上 `wb_SD0` 标签。
- **数据**：cs_panel 须由 Data/Eng 重建出新版本（例如 `cs_panel_v2`），补回复牌首日行（D-1）。旧 cs_panel 不覆盖。

### 3.1 停牌：不可卖出、也不可买入

- 判定 `halted(t,i)` 满足任一条件即可：
  1. suspend_d 当日有 S 记录，且 suspend_timing 为空（全天停牌）；
  2. 当天没有行情（close 非有限），且 t ≤ last_trade_date；
  3. open_status ∈ {halted, suspended}，**并且**当日成交量 = 0。加这个条件是为了修 D-2 的误标。
- 盘中停牌（suspend_timing 非空）：如果停牌时段覆盖 09:30，开盘成交就拒；否则允许。
- 停牌日买卖都拒，未成交单 carry（沿用现有逻辑）。

### 3.2 当日目标无法执行时：冻结，其余按剩余预算归一

在执行日 t 开盘、成交之前，用 t 开盘时已知的信息（停牌、开盘价、涨跌停价）处理：

1. 冻结集合 F = 当日订单被停牌或涨跌停拦住的持仓股。F 中个股保持现有股数，估值为 `V_F`。
2. 对没有被拦的目标股 j，新目标价值 = `w_j × (NAV_open − V_F − 现金缓冲) / Σ_{k∉F, k 可买} w_k`。也就是剩余预算按目标权重**等比例**重新归一，不再按代码顺序挤出。
3. 想买但被拦的目标股（停牌或一字涨停）：
   - `blocked_buy_budget=renorm`：它的预算并入第 2 步，按比例分给其余股；
   - `=cash`：这部分留作现金。
   - 两种结果都要在事件表里留痕。
4. 对 Core 一类带硬约束的书，归一会让行业、β 暴露偏离求解时的结果。SD1 **不重解**，偏离量写进事件表并披露（与 K2「硬约束优先、超额现金只披露」同一精神）。
5. 下一个信号日照常重算；冻结股仍在 F 中时，重复上面的步骤。

### 3.3 复牌当日按实际价格计入收益

- 主引擎现行处理已经正确，保持不变。
- 权重型引擎必须改用 `close_to_close_returns` 的语义：区间内停牌沿用上一收盘，复牌当日计入完整跳空。cs_panel 必须带复牌首日行。
- 禁止在价格对齐到调仓索引之后，用 `pct_change(fill_method=None).fillna(0)` 吃掉跳空（ADG L45 的做法）。

### 3.4 涨跌停（可选项，说明是否属业内标准）

- **open_touch（默认，沿用现行）**：next_open 成交时，开盘价触及涨停就不买，触及跌停就不卖。这比只拦「一字板」更保守。A 股回测的常见做法是「涨停不买、跌停不卖」，按成交价是否触板来判断，所以把它定为默认。
- **one_price_only（可选）**：只拦一字板（open=high=low=close=涨停或跌停价）。比 open_touch 宽松，只作敏感性列。
- **权重型引擎**：SD1 起同样执行 open_touch。被拦的单按 3.2 冻结。
- 特殊情形由 Data 提供，引擎只读 limit 字段：退市整理期首日、注册制新股上市前 5 日没有涨跌幅限制；ST 为 5%（2025 年规则变化以 limit_ratio_at_open 为准）。

### 3.5 退市处理顺序

**第 0 步：事件表（会计层专用）。** Data 新建 `data/v2/ref/delist_events_v1.parquet`：
- 字段：ts_code、last_trade_date、type、period_start、consideration 引用。
- type 取值：

| type | 含义 |
|---|---|
| FORCED_PERIOD | 强制退市，进入整理期 |
| FORCED_NO_PERIOD | 交易类强制退市：面值、市值、成交量等，不进整理期（数据中面值退市票的整理期交易日均为 0，例如中银绒业、广汇汽车） |
| MERGER_SWAP | 换股吸收合并 |
| CASH_OUT | 私有化，或主动退市并附现金对价 |
| UNKNOWN | 未能确定 |

- 分类要修正 D-3 和 D-4。面值类的判定规则：最后 20 个交易日收盘都 < 1 元。合并、私有化类须有人工核对的公告来源。

**第 1 步：仍在交易期间（含整理期）。** 按 3.1–3.4 正常执行。
- `delist_force_sell_in_period=True` 时：持仓股一旦**公开**进入退市整理期，从整理期首日起每天开盘发出强制卖单，受跌停约束，按实际成交价卖出。
  - 「公开」的依据是 namechange 的 ann_date ≤ t，或带公告日的 delisting_period_start。
  - 这是 PIT 合法信息，也符合「不持有整理期股票」的常见风控。
- 这就是「**优先按整理期最后可成交价卖出**」的落地方式：按真实可成交的价格逐日卖出，**不**假设能按最后收盘价一次卖完。

**第 2 步：最后交易日之后仍有持仓。** 在 last_trade_date 之后的第一个交易日，用 `terminal_price` 机制结算。复用 execution.py:841-849，个股的 terminal_price 由新加载器填入。

| type | 结算值 / 股 | 说明 |
|---|---|---|
| FORCED_PERIOD / FORCED_NO_PERIOD | `delist_forced_recovery × 最后可成交收盘价`，**默认 0（直接归零）** | 敏感性列 0.3、0.7 |
| MERGER_SWAP | 在换股实施日，按 swap_ratio 换成存续方股票（不足一手的部分按存续方当日收盘价折现金），之后继续按存续方行情估值 | 须有对价表。缺表时：在 terminal 日按最后收盘价转现金，打标 `MA_FALLBACK_LAST_CLOSE` |
| CASH_OUT | 按每股现金对价，在支付日（缺日期时取 terminal 日）转现金 | 缺表时同上打标 |
| UNKNOWN | 按 FORCED 处理（保守），打标 | — |

**推荐核销值 0 的理由：**
1. 库里没有退市板块价格，不能编造。
2. 交易类退市的最后几个交易日通常连续一字跌停，持有者实际上很难卖出。例如中银绒业最后一日开盘 0.17 等于跌停价，广汇汽车最后一日开盘 0.78 等于跌停价。
3. 退市板块流动性极低，价格和回收时间都不确定。
4. 本次修复针对的就是乐观偏差，默认值应该保守。
5. 单名上限 6%/5%，归零的最坏影响有界。

**业内参考：**
- 美股文献对缺失的业绩类退市收益有经验调整：Shumway (1997) 对 NYSE/AMEX 用 −30%，Shumway & Warther (1999) 对 Nasdaq 约 −55%。所以敏感性档里的 0.7 相当于 Shumway 口径的乐观上界，0.3 是中间档。
- 部分开源回测框架在退市时按最后价平仓，属于乐观口径。这一点未逐个核实，Eng 实现时可以查证，但不改本推荐。

### 3.6 只能使用当时可知的信息（PIT）

- **策略层**（选股、权重、优化器、掩码）**禁止读取**下列字段，因为它们都是事后信息：stock_delisted 的任何字段、stock_basic 的 delist_date、list_status=D、delist_events_v1。
- 策略层**允许使用**：当日及以前的 ST 标记、ann_date ≤ t 的 namechange、当日 suspend_d、池掩码。
- **会计层**（引擎结算）只能在 last_trade_date 之后的第一个交易日起使用事后价格和对价。在此之前，不得因为「已知会退市」提前卖出。整理期强制卖出依据的是公开的整理期公告，不算提前知道退市。
- 落地方式：新加载器只暴露给引擎。策略侧调用一律报错（用 raise，不用 assert）。另加静态检查：research/ 和策略模块里禁止出现 `stock_delisted`、`delist_date`、`delist_events`，白名单只有引擎加载器和审计脚本。

### 3.7 新旧并列口径与标注

- 自 SD1 合入起，**一个周期内**所有记分卡并列 SD0 和 SD1 两列。headline 取 SD1。
- SD0 列标注「**停牌/退市偏乐观（SD0）**」。在 SD1 合入之前产出的所有回测结论，一律补上这个标注，包括当前的 book_smoke_v1_3 和各叶评价。
- 叶评价（wb_SD0 / wb_SD1）同样并列，并标注 cs_panel 版本。
- Core v1.3 权重**不变**：SD1 只改会计层，不改求解。X2 入场券的判定沿用主 Agent 已有的裁定。SD1 结果只作披露，是否据此重新判定由主 Agent 定。
- **纸面轨不动**：纸面引擎、FROZEN 配置和纸面 NAV 都不切到 SD1。如果要切，需要主 Agent 另行书面裁定。

### 3.8 验收测试（合成数据单测，不碰真实收益）

| # | 场景 | 断言 |
|---|---|---|
| T1 | 区间内停牌 3 天，复牌跳空 −20% | 停牌日没有成交；停牌日 NAV 不变；复牌日 NAV 变化 = 持仓 × −20%；权重型引擎结果相同 |
| T2 | 信号日某持仓股次日停牌 | 冻结股的股数不变；其余买单 = 目标权重 × 剩余预算（按比例）；把代码改名、调换字母序后结果不变 |
| T3 | 想买的股票停牌，分别设 renorm 和 cash | renorm 时预算等比例分给其余股；cash 时留作现金。两种情况都记事件 |
| T4 | open_touch 与 one_price_only | 开盘触及跌停但盘中打开：open_touch 拒卖，one_price_only 允许卖；一字跌停时两者都拒 |
| T5 | FORCED_PERIOD：整理期第 3 天才不再跌停 | 第 3 天开盘按实际价卖出；不能按整理期首日之前的收盘价卖出 |
| T6 | FORCED_NO_PERIOD：一直一字跌停到最后交易日 | terminal 日持仓归零，NAV 下降额 = 持仓股数 × 最后收盘价 × (1 − recovery)；敏感性 0.3、0.7 按比例变化 |
| T7 | MERGER_SWAP，换股比例 0.62 | 实施日股数 = 原股数 × 0.62（不足一手的部分折现金），之后按存续方行情估值；缺表时打 MA_FALLBACK 标 |
| T8 | CASH_OUT | 按对价转现金；缺表时打标 |
| T9 | 全部开关取 legacy | 对固定样本，NAV 与现行 `run_weight_schedule` 逐位一致 |
| T10 | PIT 守卫 | 策略侧读退市信息时抛 SystemExit 或 PermissionError；静态检查能发现故意埋入的违规引用 |
| T11 | `python -O` | 所有守卫照样生效（不依赖 assert） |
| T12 | 权重型引擎退市尾部 | 尾部 NaN 不再记 0 收益；按 3.5 结算 |
| T13 | cs_panel_v2 数据测试 | 对 suspend_d 的每个复牌事件，复牌首日行都存在（当日有成交时） |

## 4. 修复后的影响统计方法与重算门槛

**统计**：Eng 合入 SD1 并经 Arch 复审之后，对每个策略 × 资金档（60万、100万）× 口径（①纯权益、②80/20）分别跑 SD0 与 SD1，输出事件表 `sd1_events.parquet`。

- 事件类型：
  - HALT_HOLD（段数、天数）
  - HALT_BLOCKED（卖、买）
  - LIMIT_BLOCKED（卖、买）
  - RENORM（次数、被挪动的权重）
  - DELIST_SOLD_IN_PERIOD
  - DELIST_WRITEOFF
  - DELIST_MA_CONVERT、DELIST_CASH_OUT
  - DELIST_FALLBACK
- 每个事件记录：股票、日期、冻结时的权重、类型。
- 汇总表按「策略 × 资金档 × 事件类型」分别计数，另列每类事件涉及的权重日之和。

**重算门槛**（先满足的那条生效）：

- **G0 只标注**：同时满足以下条件时只补标注，结论不重算：
  - 没有任何 DELIST_WRITEOFF 或 DELIST_FALLBACK；
  - HALT_BLOCKED + LIMIT_BLOCKED 每年 ≤ 5 次；
  - SD1 与 SD0 相比，|ΔCAGR| < 0.5pp，且 |ΔMDD| < 1pp。
- **G1 重算并列**：超出 G0，但所有闸门判定（pass/fail）不变。记分卡以 SD1 为 headline 重新发布，SD0 留作对照。
- **G2 交主 Agent 重裁**：任一闸门判定翻转（例如 MDD 在 25% 线两侧，或 X2 入场券由过变不过），或者出现任何 DELIST_WRITEOFF 且单笔核销权重 ≥ 1%。
- **叶评价**：cs_panel_v2 重建后，凡结论离阈值不到 20%（相对）的叶都要重算 IC 和 t。其余叶补标注。

注：Δ 指标就是收益数字，须由 Eng 在授权运行中产出，Arch 先审再报。本规格不产出任何收益。

## 5. 初步事件数（只读目标权重，只数次数，不涉及收益）

口径：
- held(t) = 前一交易日收盘的目标权重 > 0；
- 停牌 = suspend_d 全天 S；
- 被拦调仓 = 目标权重变化后，执行日停牌；
- 退市 = 最后交易日落在 X2，且最后 20 个交易日内曾持有。

X2 = 2024-06-03→2026-10-09，共 570 个交易日。

| 策略（文件） | 持有过的股票 | 持仓股-日 | 停牌段数 / 天数 | 被拦调仓（卖/买） | 持有到退市 | 最后 20 日内持有过的退市票 |
|---|---|---|---|---|---|---|
| Core v1.3 ①纯权益 60万 | 162 | 11781 | 2 / 15（600150.SH 10 天，002828.SZ 5 天） | 0 / 0 | 0 | 0 |
| Core v1.3 ①纯权益 100万 | 130 | 11856 | 2 / 16（600150.SH 10 天，688981.SH 6 天） | 0 / 1 | 0 | 0 |
| Core v1.3 ②80/20 60万 | 162 | 11660 | 2 / 15 | 0 / 0 | 0 | 0 |
| Core v1.3 ②80/20 100万 | 130 | 11879 | 2 / 16 | 0 / 1 | 0 | 0 |
| B4 50/25/25 60万（b4_leg_review smoke 的 target_weights） | 417 | 9915 | 1 / 1 | 1 / 0 | 0 | 1：广汇汽车（面值退市，脚本核实） |
| B4 50/25/25 100万 | 570 | 16182 | 3 / 8 | 1 / 1 | 0 | 1：广汇汽车 |
| capacity_adv 单独 60万 / 100万（目标相同） | 229 | 14225 | 3 / 19 | 0 / 1 | 0 | 0 |

- 广汇汽车：B4 目标权重最后一次 > 0 是 2024-07-01。两个资金档的引擎**实际持仓**文件（actual_weights）最后一次出现都是 2024-07-02，也就是 07-03 开盘已经卖出。该股最后交易日是 2024-07-17，所以**没有持有到退市**。
- 局限：
  1. 计数基于目标权重。引擎在 SD1 下的实际冻结次数，须修复后按 §4 统计。
  2. 涨跌停被拦次数**没有统计**（要读开盘价，留给 SD1 事件表）。
  3. FULLA 叶评价和各 g1g5 叶的事件数**没有统计**。FULLA 含小微盘和更多退市票，预计事件更多，须修复后统计。
  4. cs_panel 复牌缺行（D-1）影响的是叶评价和 AI 的池子等权指数，不影响 book-smoke 主引擎。

## 6. 待主 Agent 裁定

1. `blocked_buy_budget` 的默认值：renorm（按任务原文）还是 cash（对 Core 硬约束更友好）。Arch 倾向：Core 用 cash，其余用 renorm。
2. 强制退市默认核销值 0，敏感性 0.3 和 0.7，是否同意。
3. `delist_force_sell_in_period` 默认 True，是否同意。这会让策略层之外多出一条「整理期强制卖出」的风控规则。
4. cs_panel_v2 的重建排期（Data），以及叶评价重算范围按 §4 的 20% 规则。
