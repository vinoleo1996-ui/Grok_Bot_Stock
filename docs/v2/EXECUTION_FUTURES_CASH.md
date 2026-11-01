# 执行引擎：现金计息 + 股指期货腿（V3 B1/B2 §9）

代码：`quantlab/platform/futures.py`，并在 `quantlab/platform/execution.py::run_weight_schedule(..., futures=)` 里挂接。测试：`tests/test_execution_futures_cash.py`。
两项功能都需要手动打开，默认关闭（`cash_rate=None`、`futures=None`），旧结果逐位不变。

## 1. 现金计息 `ExecConfig.cash_rate`
- 计息对象：每个交易日开始时，按上一日收盘的**闲置现金** = 现金 − 期货保证金占用（小于 0 时按 0），乘以 r[t]，记入现金。分红现金和期货可用资金都计息，保证金不计息。
- 常数年化：`cash_rate=0.02`，`cash_rate_convention="act365"`（默认，r = 年化 × 两交易日间自然日 / 365，长假期间照样计息），或 `"per_session"`（r = 年化 / 252）。
- 序列 `pd.Series`（按交易日）：
  - `cash_rate_kind="annual"`：小数年化利率，用 t−1 日的值，按 ACT/`cash_rate_day_count` 计息（默认 365，Shibor 用 360）。
  - `cash_rate_kind="return"`：直接用当日收益率，比如 511880 的日收益。
- 511880 数据：`futures.load_511880_returns(start, end)`，由 `data/v2/etf/raw` 的 fund_daily 乘 fund_adj 复权后计算。覆盖 2018-01-02 到 **2026-03-19**，年化约 2.09%。
- **Shibor**：box 上没有，Data 已经在补。
- 输出：`cash_interest`（合计）、`cash_interest_daily`。
- 快仿（`smallcap.sim.Costs.cash_rate_per_session`，在 `_fastsim_nav(cash_rate=...)` 里接好）计息公式相同，测试中和平台引擎的相对差 <1e-12（快仿没有期货）。Ledger 还没有现金计息，零成本对账请保持 `cash_rate=None`。

## 2. 股指期货腿
用法：
```python
from quantlab.platform.futures import FuturesLeg, FuturesPanels, FuturesConfig
leg = FuturesLeg(FuturesPanels(settle=S, open=O, pre_settle=PS, expiry={"IF2412": "2024-12-20"}),
                 FuturesConfig(roll_mode="roll", roll_days=5, contract_months="quarterly"))
r = run_weight_schedule(etf_panels, {day: {"sh.510300": 0.8, "IF": 0.5}}, config=cfg, futures=leg)
```
- 调仓表里用品种根代码（IF/IH/IC/IM）作键，值是**带符号的名义权重**（名义 / 信号日 NAV），负值表示做空。现货代码照旧。权重会一直沿用，直到下一次给出新值。
- 手数 = round(w × NAV / (信号日结算价 × 乘数))，`lot_rounding="floor"` 时改为向零截断。手数在信号日锁定，下一交易日按开盘价成交；`fill="close"` 时按当日结算价成交。
- 品种规则：乘数 IF/IH 300、IC/IM 200；最小变动 0.2 点；整手；不收印花税。
- 涨跌停：以 pre_settle 为基准 ±10%，合约最后交易日 ±20%（交易所规则）。触及涨跌停时，买（卖）单不成交，下一交易日重试。没有 pre_settle 时用上一日结算价；上市首日没有基准价，不检查涨跌停。
- 逐日盯市：VM = 持仓 × 结算价 × 乘数 − 参考值，按结算价结算到现金（见模块头部公式）。结算价缺失的日子不结算，NAV 里计入以上一日结算价为基准的浮盈。
- 保证金 = |手数| × 结算价 × 乘数 × (保证金率(日期, 品种) + `margin_add`)。现货买入不能动用保证金占用的现金。如果收盘后现金低于保证金，记 `fut_margin_shortfall` 事件。`shortfall_action="flag"`（默认）只记录；`"reduce"` 在下一交易日开盘强制减到现金能覆盖的手数（向零截断），成交标记为 `forced_reduce`。
- 展期，`roll_mode="roll"`：持仓合约离最后交易日不超过 `roll_days` 个交易日时，在当天开盘平旧开新，换到下一个合约（`contract_months="quarterly"` 时只在季月合约之间换）。展期成本 = 两腿手续费 + 滑点（`slippage_ticks`），单独归入 roll_cost。如果找不到下一个合约，记 `fut_roll_no_next`，持有到交割。
- 交割，`roll_mode="deliver"`：在最后交易日按当日结算价现金交割（交易所的最后交易日结算价就是交割结算价），交割费为名义 × 0.01%（`delivery_fee`），记 `fut_delivery`。
- 最后交易日 = 合约月份第三个周五；如果那天不是交易日，顺延到下一个交易日。也可以用 `FuturesPanels.expiry` 直接指定。
- 输出：`margin_peak`、`margin`（逐日）、`variation_margin`、`variation_margin_daily`、`roll_cost`、`n_rolls`、`fut_costs`（fee/slippage/roll_fee/roll_slippage/delivery_fee）、`fut_total_fees`、`fut_exposure`（名义 / NAV）、`fut_fills`、`fut_positions`。事件写在 `events` 里，原因以 `fut_` 开头。

### 日期费率表 `FEE_TABLE`（交易所费率，名义的比例；券商加收用 `fee_add`）
| 生效日 | 开仓 | 平仓 | 平今 |
|---|---|---|---|
| 2010-04-16 | 0.000025 | 0.000025 | 0.000025（近似） |
| 2015-09-07 | 0.000023 | 0.000023 | 0.0023 |
| 2017-02-17 | 0.000023 | 0.000023 | 0.00092 |
| 2017-09-18 | 0.000023 | 0.000023 | 0.00069 |
| 2018-12-03 | 0.000023 | 0.000023 | 0.00046 |
| 2019-04-22 | 0.000023 | 0.000023 | 0.000345 |
| 2023-03-20 | 0.000023 | 0.000023 | 0.00023 |

### 保证金表 `MARGIN_TABLE`（交易所投机保证金）
| 生效日 | IF/IH | IC | IM |
|---|---|---|---|
| 2015-09-07 | 40% | 40% | – |
| 2017-02-17 | 20% | 30% | – |
| 2017-09-18 | 15% | 30% | – |
| 2018-12-03 | 10% | 15% | – |
| 2019-04-22 | 10% | 12% | – |
| 2022-07-22 | 12% | 12% | 12% |

**来源 / 假设：** 两张表都是按中金所历次调整公告（2015 年抑制过度交易，2017–2019 年和 2023 年分步放松）凭记忆整理的；CFFEX 网站在 box 上不可达，没能逐条核对。2015-09-07 之前的数值是近似。2022 年以后的保证金率尤其需要 Data 或合规核实。表可以直接改，也可以用 `fee_override` / `margin_override` 覆盖。平今判定：当日新开的手数先平，算平今。

## 3. 需要 Data 提供（box 上 `data/v2/futures/raw/` 为空）
1. IF/IH/IC/IM 全部合约日线（2010 年起；IM 从 2022-07-22 起）：trade_date、合约代码、open、high、low、close、**settle**、**pre_settle**、volume、amount、oi。
2. 合约表：合约代码、上市日、最后交易日、交割日、交割结算价。
3. 历史费率和保证金率的官方公告表，用来核对上面两张表。
4. Shibor 隔夜（以及 1W），按日给出；511880 的日线补齐到 2026-03-19 之后。

## 4. 已知限制
- 期货只有日线，按开盘价或结算价成交，没有冲击成本（只有 `slippage_ticks`）。
- 保证金不足时没有模拟日内追保。强制减仓在下一交易日开盘执行，不是盘中强平。
- Ledger 还不支持期货腿和现金计息。三引擎对账只在两项都关闭时适用。
- 现货和期货共用一个现金池，现货卖出的现金可以直接补保证金，没有模拟银期转账延迟。


## 2026-10-11 更新（核对后）
- 保证金表：原 2022-07-22 行（IF/IH 12%、IC 14%、IM 15%）不可信（疑为期货公司保证金），已按 `docs/v2/FUTURES_FEE_MARGIN_VERIFY.md` 改为 IF/IH/IC/IM 均 12%（当前交易所标准；来源 ccbfutures.com 2026-05-06、guoshengqh.com 2026-09-29）。IF/IH 由 10% 升到 12% 的确切日期未找到公告原文，暂放 2022-07-22；请用 `margin_override` 做 2019-04-22 之后 10%/12% 敏感性。
- 手续费表（含平今）2015-09-07 至 2023-03-20 各行已核对正确；2010-04-16 行仍是近似。
- 现金计息：`futures.load_shibor(tenor='ON'|'1W'|'3M'...)` 读 `data/v2/rates/shibor.parquet`，返回小数年化利率，配 `ExecConfig(cash_rate=s, cash_rate_kind='annual', cash_rate_day_count=360)`（ACT/360，t-1 定盘）。`load_511880_returns()` 默认改读 `data/v2/etf/etf_daily_adj.parquet`（到 2026-10-09），配 `cash_rate_kind='return'`；旧 raw 目录为回退。

## 5. 融资账户（2026-10-11，`quantlab/platform/margin.py`，默认关闭）
用法：
```python
from quantlab.platform.margin import MarginConfig
m = MarginConfig(financing_rate=shibor3m, spread=0.01, day_count=365, max_leverage=3.0,
                 liquidation_ratio=1.30, warning_ratio=1.50, restore_ratio=1.50, liquidation_action="liquidate")
r = run_weight_schedule(panels, rpvt_schedule, config=cfg, futures=leg_or_None, margin=m)
```
- 调仓表权重之和可以 > 1，超出部分借现金：现金可以为负，**负债 = max(−现金, 0)**。不传 `margin` 时行为不变（买入仍受现金限制，权重和 > 1 会被截掉）。
- **可借额度**：买入时要求 成交后现金 − 期货保证金占用 ≥ −(max_leverage − 1) × 当日开盘权益。杠杆定义 = 多头市值 / 权益。只在开新仓时限制，之后因亏损/计息杠杆上升不会自动减仓（由维持担保比处理）。
- **利息**：每个交易日开始时，按上一日收盘负债 × (financing_rate[t−1] + spread) × 自然日 / day_count 记入现金（即利息并入负债，按日复利）。financing_rate 可以是常数或按日期的 Series（如 Shibor 3M、LPR），t−1 定盘、前向填充。Beta 的 `financing_rate.csv` 对应 `financing_rate=shibor_3m, spread=0.01, day_count=365`。正现金照旧走 `ExecConfig.cash_rate`。
- **维持担保比例** = (Σ 市值 × haircut + max(现金, 0)) / 负债，每日收盘检查：
  - < `warning_ratio`（默认 150%，警戒线）：记 `margin_warning`。
  - < `liquidation_ratio`（默认 130%，平仓线）：记 `margin_liquidation`。`liquidate`：撤掉全部待成交股票单，下一交易日按引擎成交价（`fill`）**按比例卖出**所有持仓，卖出额 X 使比例恢复到 `restore_ratio`（默认 150%）：X = (R·D − 抵押) / (R − h)。`flag`：只记事件。
  - 130%/150% 取自《证券公司融资融券业务管理办法》及沪深交易所融资融券交易实施细则的常见口径；2019 年后交易所已不再统一规定平仓线，改由券商合同约定（常见仍是 130%/140%/150%）。**需合规按实际券商合同确认**。现实中低于平仓线后通常有 T+1/T+2 追保期，引擎默认下一开盘即卖（偏保守）。
- **折算率 haircut**：`haircuts={code: 折算率}`，默认全部 1.0（简化）。注意现实中折算率用于计算保证金可用余额（开仓额度），这里只用在维持担保比上；ETF 实际折算率常见 0.8–0.9（511010 债券 ETF 可更高），需要时自行传入。
- **输出**：`financing_interest`、`financing_interest_daily`、`debt`、`leverage`、`peak_leverage`、`maintenance_ratio`、`min_maintenance_ratio`、`liquidation_events`、`margin_warnings`。
- **融券（卖空）不支持**，调仓表的负股票权重仍被忽略。
- Ledger 和快仿都没有融资账户，三引擎对账请保持 `margin=None`。

## 6. 国债期货 T / TF / TS / TL（2026-10-11）
调仓表用根代码 `'T','TF','TS','TL'`，值是带符号名义权重；手数 = round(w × NAV / (价格/100 × 面值)) = round(w × NAV / (价格 × 乘数))。
| 品种 | 面值 | 乘数 | 最小变动 | 涨跌停(vs 前结算) | 保证金 |
|---|---|---|---|---|---|
| TS (2Y) | 200 万 | 20,000 | 0.002 | ±0.5% | 0.5% |
| TF (5Y) | 100 万 | 10,000 | 0.005 | ±1.2% | 1.2% |
| T (10Y) | 100 万 | 10,000 | 0.005 | ±2% | 2% |
| TL (30Y) | 100 万 | 10,000 | 0.01 | ±3.5% | 3.5% |
- **已核实**（`data/v2/futures/raw/fut_basic.parquet`）：乘数、最小变动价位（注意 TS 是 0.002 不是 0.005）、最后交易日 = 交割月第二个周五（155 个合约中 150 个正好落在第二个周五，其余因节假日顺延）。
- **假设，待 Data/合规核实**：涨跌停幅度（含最后交易日沿用同一幅度——交易所规则可能不同）、保证金率（按上市时最低标准，`BOND_MARGIN_TABLE` 带日期可改；实际交易所曾多次调整，券商另加）、手续费 3 元/手开平、平今也按 3 元（保守；`bond_fee_override=(开,平,平今)` 可改）。`fee_add` 对国债期货按名义比例加收。
- 合约月份：季月（用 `contract_months="quarterly"`）。**展期**：默认 `bond_roll_before_delivery_month=True`，以交割月第一个交易日为锚，提前 `roll_days` 个交易日换到下一季月合约（个人/一般账户不能持仓进交割月）。**不模拟实物交割**；`roll_mode="deliver"` 时按最后交易日结算价现金了结，仅作近似。
- 盯市、保证金占用、保证金不足事件、展期成本报告与股指期货同一套（§2）。手工核对：`docs/v2/T_QUARTER_HANDCHECK.md`。

## 7. 组合账户
股票/ETF/可转债、融资负债、股指期货、国债期货共用一个现金池：
- 权益 NAV = 现金（可为负，负的部分即负债）+ 多头市值 + 期货当日未结算浮盈（结算后为 0，VM 已进现金）。测试里验证了 NAV = 现金 + 市值，以及 股票损益 = NAV − 初始 − VM + 期货费 + 融资利息 − 现金利息。
- 期货保证金占用的现金不能用于买股票；开启融资时，期货保证金不足检查把**未用融资额度**算作可用资金（`free = 现金 + 额度 − 保证金`）。也就是说期货保证金实际上可以用借来的钱交，这是简化：现实中期货账户与信用账户分开，银期转账也不能用融资款。严格口径请把 `max_leverage` 设低或用 `shortfall_action="reduce"`。
- 维持担保比只看股票/ETF 市值和正现金，期货浮盈亏通过 VM 进入现金后间接影响负债。
- 现金计息只对 max(现金 − 期货保证金, 0) 计；负现金只计融资利息。

### 给 Beta / Strategy 的 API 提示
- RPVT 杠杆路线：`run_weight_schedule(etf_panels, rpvt_schedule, config=ExecConfig(cash_rate=shibor3m, cash_rate_kind="annual", cash_rate_day_count=365), margin=MarginConfig(financing_rate=shibor3m, spread=0.01, max_leverage=3.0, haircuts={...}))`。RPVT 杠杆上限 3.0，`max_leverage` 至少设 3.0，否则会被截。
- 期货路线：权益腿 `{"IF": w}`，债券腿 `{"T": w}` 或 `{"TF": w}`；`FuturesConfig(roll_mode="roll", contract_months="quarterly")`。黄金没有 CFFEX 合约，需要 SHFE AU 新腿（未做）。
- 国债期货行情：用 `FuturesPanels(settle=..., open=..., pre_settle=...)`，列名为合约代码（如 `T2503`）。

### 需要 Data 提供（新增）
1. T/TF/TS/TL 全部合约日线（TF 2013-09 起，T 2015-03 起，TS 2018-08 起，TL 2023-04 起）：open/high/low/close/**settle**/**pre_settle**/volume/oi。合约表已在 `fut_basic.parquet`。
2. 国债期货历次保证金率、涨跌停幅度（含最后交易日）、手续费（含平今）的交易所公告表。
3. 融资基准利率：LPR 历史（若用 LPR 加点）；Shibor 3M 目前只到 2026-05-06（Beta 的表是向后填充的）。

## 2026-10-11 post factor-rebuild update (Eng)
- Bond futures tables now VERIFIED per docs/v2/FUTURES_FEE_MARGIN_VERIFY.md (国债期货 section): TF exchange margin 1% (was 1.2%); bond close-today fee 0 (open / close-yesterday 3 CNY/lot). T 2%, TS 0.5%, TL 3.5% unchanged.
- Rates: `futures.load_lpr(tenor='1Y'|'5Y')` reads data/v2/rates/lpr.parquet (decimal). Shibor 3M in data/v2/rates/shibor.parquet is complete to 2026-10-10 with no nulls (only holiday gaps: May Day, National Day). Use `load_shibor` on this file; Beta's forward-filled copy (output/v3/handoff_strategy/financing_rate.csv) should be dropped as a rate source.
- Real index-futures bars: `futures.load_index_futures_panels(roots|contracts, start, end)` reads data/v2/futures/raw/daily/*.CFX.parquet (557 IF/IH/IC/IM contracts) + fut_basic expiry. IF quarter hand-check (scripts/if_quarter_handcheck.py, default = real data) matches the engine to 2e-10 CNY.

## 多品种期货腿与国债期货展期（2026-10-12）
- 一个 FuturesLeg 可同时持有多个根代码（IF/IH/IC/IM/T/TF/TS/TL）：权重按根代码给（名义/NAV，带符号，如 `{"IF":0.5,"IC":-0.3,"T":2.0,"TF":1.5}`），每个根各自选合约、各自展期，乘数/最小变动/涨跌停/手续费/保证金都按根取。面板用 `load_futures_panels(roots=("IF","IC","T","TF"), start, end)`（文件名 = 根 + 4 位数字，T 不会误配 TF/TS/TL 或连续合约）。
- `FuturesConfig.roll_days_by_root={"T":15,"TF":15,"IF":5,...}`，缺省用 `roll_days`。
- 国债期货 `bond_roll_rule`：`"delivery_month_anchor"`（旧默认，交割月首个交易日前 roll_days 个交易日）；`"earlier_of"`：在 min(最后交易日 − N, 交割月首个交易日 − `bond_exit_sessions_before_dm`(默认 1)) 那个交易日开盘展期，即"最后交易日前 N 个交易日，但绝不进交割月"。交易所从交割月前 2 个交易日起上调保证金，想完全避开就设 `bond_exit_sessions_before_dm=3`。
- 交割月保证金上调（已核实，FUTURES_FEE_MARGIN_VERIFY.md）：交割月前 2 个交易日起 T 3%、TF 2%、TS 1%、TL 5%；`bond_delivery_margin=True` 开启（默认关）。
- BOND_MARGIN_TABLE 改为按上市日分行（TF 2013-09-06、T 2015-03-20、TS 2018-08-17、TL 2023-04-21，来自 fut_basic.list_date），数值仍是现行核实值往前沿用——**历史调整未知，属假设**。待 Data 核实：各品种上市以来交易所最低保证金的历次调整公告（TF 早期细则据称 1.2%，日期不明）。
- 数据窗口之外到期的合约永远不算"到期/该展期"（窗口边界修复），多品种同样适用。测试：tests/test_futures_multiroot.py。

## 国债期货保证金沿革与数据源（2026-10-11 更新）
- `FuturesConfig.bond_margin_source`（只影响 T/TF/TS/TL 一般月份最低保证金；`margin_override` 优先）：
  - `"hist"`（默认）：中金所核实的官方沿革 `data/v2/futures/bond_fut_margin_official.parquet`（每行附公告链接）。TF 3%(2013-09-06) → 2%(2014-01-02) → 1.5%(2014-11-03，期货公司转载核实) → 1.2%(2015-03-16 起至今)；T 2%(2015-03-20)；TS 0.5%(2018-08-17)；TL 3.5%(2023-04-21)。核查确认 2015-16、2020 年无一般月份调整；2020-09-29 fut_settle 里的 TF 1.4% / TS 0.6% 单日尖刺不属于官方沿革，不计入。`BOND_MARGIN_ASSUMED_FLAT=False`。
  - `"settle_observed"`：由 Tushare fut_settle 逐合约日保证金推出（同日各合约取最低 = 一般月份），含 2020-09-29 尖刺；只作对照。fut_settle 只抽样 443 个交易日，变动日是首次观测日。
  - `"cffex_current"`：**规则下限**（细则写的最低 1%，TF 1%）倒推到上市日。这是敏感性测试，不是实际执行的保证金（2015-03-16 起实际执行 1.2%）。
- 交割月上调（T 3%、TF 2%、TS 1%、TL 5%，交割月前 2 个交易日起）仍只由 `bond_delivery_margin=True` 施加；上面三个基础表都不含上调，不会重复计算。
- 手续费：开仓 / 平昨 3 元/手，平今 0，交割 5 元/手（`BOND_DELIVERY_FEE_PER_LOT`），自上市起不变 = 假设（`BOND_FEE_ASSUMED=True`），没有调整历史。
- 行情：国债期货默认读 `bond_fut_daily.parquet`（与 raw/daily 逐行相同），`load_futures_panels(..., bond_source="raw")` 可切回。Tushare 在 2019-01-18、02-13、02-15 缺 T/TF/TS 结算价，加载时用下一交易日的 pre_settle 补齐（`repair_missing_settle`）；旧加载器会把这几天整天丢掉，导致 2019-02-15 T1903 误报 `fut_roll_no_next`。
