# gs-quant 源码级深读笔记（Leo 要求：理解透彻，不只 README）

- **触发**：Leo t1072u（2026-10-25 ~12:41 ET）—「别人的核心算法逻辑你要理解透彻，不是只看一个 readme，我需要你理解源码」
- **上游钉**：`docs/v2/refs/gs_quant/REF_COMMIT.txt` = `bbe7071653ccfc0d431e11c3a31dbd511afc394f`（release **2.2.1**）
- **包根**：`docs/v2/refs/gs_quant/gs_quant/`
- **对照粗计划**：`MAIN_GS_QUANT_ABSORB_PLAN_20261025_ZH.md`（本笔记是**源码纠正/加深**，不是计划复述）
- **QuantLab 硬钉**：A 股 + 境内股票 ETF；纸面；`live=false`；主报年化 **244**；禁 Marquee 生产源；不 pip 绑死；不签 `.ok`；不改 paper
- **时钟**：用户时区 America/New_York；本笔记落盘标签 **2026-10-25 12:42 EDT**

## HARD DO-NOT（全文适用）

1. 禁止 Marquee / `api/gs/*` / GS 假日 Dataset / 风险模型云端载荷作 A 股生产或验收源。
2. 禁止把 `AnnualizationFactor.DAILY=252` / `PaymentFrequency.DAILY=252` 覆盖 QuantLab **244**。
3. 禁止 `pip install gs-quant` 进研究/验收锁；默认重写进本厂契约。
4. 禁止抬 live；禁止签无关 `.ok`；禁止改 paper 轨。

---

## 0. 总览：真正的「算法骨架」不是包布局

粗计划扫目录时得到「有 Context / 有回测 DSL / 有 ResultInfo」。源码显示更精确的五条脊骨：

| # | 脊骨 | 真实落点 | 一句话机制 |
|---|---|---|---|
| 1 | **双栈上下文** | `context_base.py` + `markets/core.py` + `data/core.py` | `ContextVar` 维护**按类独立**的路径栈；`PricingContext` 与 `DataContext` **不是同一个对象** |
| 2 | **Market 对象即价格口径** | `markets/markets.py` + `risk/measures.py` | Close/Live/Relative 是一等公民；PnL Explain = 当前 market → 目标 market 的相对测度 |
| 3 | **两阶段事件回测** | `backtests/generic_engine.py` | 先批量建 simple/semi 触发，再按日跑 path_dependent；仓位与现金账本分离 |
| 4 | **带单位/错误的结果** | `risk/core.py` | `ResultInfo(unit, error, request_id)`；异单位禁止相加；失败不是静默 NaN |
| 5 | **仓位三维 + 单一计价策略** | `markets/position_set.py`（**不在** `entities/`） | `reference_notional` 路径强制 weight 完备且禁 quantity/notional；计价时只选 Weight\|Quantity\|Notional 之一 |

---

## 1. Context 栈（G1 源码真相）

### 1.1 入口类 / 文件

- `gs_quant/context_base.py`：`ContextMeta` / `ContextBase` / `ContextBaseWithDefault`
- `gs_quant/markets/core.py`：`PricingContext`、`PricingCache`、`PositionContext`
- `gs_quant/markets/historical.py`：`HistoricalPricingContext`、`BackToTheFuturePricingContext`
- `gs_quant/data/core.py`：`DataContext`
- `gs_quant/markets/markets.py`：`CloseMarket` / `LiveMarket` / `OverlayMarket` / `RelativeMarket` / `close_market_date`

### 1.2 关键路径（逐步）

```
with PricingContext(pricing_date=D, market=M, use_cache=...):
    # ContextBase.__enter__
    #   ContextMeta.push(self)  → path = (self,) + old_path   # ContextVar，线程/协程局部
    #   _on_enter()：把「可继承属性」物化到本实例（从 prior / current / default 拉齐）
    instrument.calc(risk) → PricingContext.calc → _calc
    #   risk_key = RiskKey(provider, pricing_date, market, params, scenario, risk_measure)
    #   future 挂到 active_context.__pending[(risk_key, instrument)]
    #   若 use_cache：PricingCache.get；命中则直接 set_result
# __exit__
#   _on_exit → __calc()：把 pending 按 provider/params/scenario/dates_markets/measures 分批
#             打成 RiskRequest → GenericRiskApi（此处即 Marquee 边界）
#   finally: pop() + 属性复位
```

`HistoricalPricingContext.calc` 额外循环日期：

```
for date in date_range:
    market = CloseMarket(location=..., date=date, check=True)
    risk_key = RiskKey(..., date, market, ...)
    futures.append(_calc(...))
return HistoricalPricingFuture(futures)
```

`DataContext` 是**另一条** `ContextBaseWithDefault` 栈：只承载 `start/end/interval`，默认 start=今天-30d、end=今天；**不**持有 market / pricing_date。

### 1.3 设计意图

- **隐式参数外置**：定价日、市场位置、场景、异步/批、缓存开关不进每个 instrument 调用签名。
- **栈可嵌套 + 可继承**：内层未设的字段从 prior / active 继承（`_inherited_val`）；`active_context` 跳过 `set_parameters_only` 层，保证真正提交 pending 的是「干活」那层。
- **历史批量 = 日切 CloseMarket**：不用 Live，强制 as-of 收盘口径。

### 1.4 陷阱 / 默认值

| 陷阱 | 源码位置 | 含义 |
|---|---|---|
| 默认 market 是 **CloseMarket**，不是 Live | `PricingContext.market` | 未显式传 market 时自动 `CloseMarket(date=close_market_date(...), location=...)` |
| Close 滚动时点 `roll_hr_and_min=(24,0)` | `CloseMarket.roll_hr_and_min` + `close_market_date` | 本地时区「定价日 24:00」前，close 日期回滚到 `prev_business_date`；**且注释写明外部用户暂不用交易所日历** |
| **Live 结果永不进 PricingCache** | `PricingCache.put` | `isinstance(risk_key.market, LiveMarket)` → 跳过 put；ErrorValue 也不缓存 |
| 未来 pricing_date / market.date 直接 ValueError | `PricingContext.__init__` | 未来日走 `RollFwd` Scenario，不是改 pricing_date |
| PricingContext ≠ DataContext | 两文件两栈 | 粗计划「ResearchContext 一把梭」需拆开或显式组合 |
| 默认 location **LDN** | `market_data_location` default | A 股无关；QuantLab 勿照搬 |

短摘（缓存边界）：

```python
# markets/core.py PricingCache.put
if not isinstance(result, ErrorValue) and not isinstance(risk_key.market, LiveMarket):
    cls.__cache.setdefault(instrument, {})[risk_key] = result
```

### 1.5 QuantLab 精确映射

| gs-quant | QuantLab |
|---|---|
| `PricingContext.pricing_date` + `market` | `ResearchContext.asof` + `price_basis`（close/open/adj）+ 可选 `market_kind` |
| `DataContext(start,end)` | 研究窗 / 叶脚本的 `[start,end]`；**别塞进 asof** |
| `HistoricalPricingContext` 日切 CloseMarket | 回测循环：每个决策日显式绑定当日收盘/开盘对象 |
| `PricingCache` 禁 Live | 纸面/诊断缓存键必须含 `price_basis`；live 路径（未来）禁共享 close 缓存 |
| ContextVar 栈 | 可用 `contextvars` 或显式传参；**叶/回测/纸面进入同一 ResearchContext**（计划 G1 方向对，实现要分 Pricing/Data 两轴） |

---

## 2. Close ≠ Live 与 PnlExplain（G2 源码真相）

### 2.1 入口

- `markets/markets.py`：`CloseMarket` / `LiveMarket` / `RelativeMarket`
- `risk/measures.py`：`PnlExplain` / `PnlExplainClose` / `PnlExplainLive` / `PnlPredictLive`

### 2.2 关键路径

```python
class PnlExplain(__RelativeRiskMeasure):
    def __init__(self, to_market: Market): ...
    @property
    def pricing_context(self):
        current = PricingContext.current
        return current.clone(
            market=RelativeMarket(from_market=current.market, to_market=self.__to_market)
        )

class PnlExplainClose(PnlExplain):
    def __init__(self): super().__init__(CloseMarket())

class PnlExplainLive(PnlExplain):
    def __init__(self): super().__init__(LiveMarket())
```

机制：**不是**「换一个价格字段」，而是把当前 PricingContext 的 market **克隆成 RelativeMarket(from→to)**，再算相对 PnL。Close 与 Live 是两个不同的 `to_market` 端点。

`CloseMarket.date` 在 `check=True` 时走 `close_market_date`（可能回滚）；`LiveMarket` 只有 location，无 date。

### 2.3 设计意图

- 价格口径是 **Market 对象身份**，可序列化进 RiskKey / 审计。
- 相对测度强制「从哪到哪」显式，避免「我以为是收盘」的静默漂移。

### 2.4 陷阱

- `PnlExplainClose()` 里的 `CloseMarket()` **无 date** → 依赖当前 PricingContext 的 `close_market_date` 解析；嵌套上下文时易踩错日。
- RelativeMarket.location 要求 from/to location 一致，否则 `location=None`。
- QuantLab 没有衍生品 Risk API；吸收的是**对象化口径**，不是照搬 PnlExplain 云端计算。

### 2.5 QuantLab 映射

- NAV / 超额 / 腿重建：**必须**声明 `price_basis ∈ {close, open, vwap, adj_close, …}`，等价于挂一个 Market 身份。
- 回测≡纸面检查单（对齐 AlphaLens A1）：同一 `price_basis` + 同一日历 + 同一 cost_sha；禁止「回测用复权收盘、纸面用未复权开盘」无声明。
- 诊断样本若混用 live 行情与历史 close，必须拆成两条序列，禁止同一图无标注。

---

## 3. 回测 DSL 与引擎调度（G5 源码真相）

### 3.1 入口

- `backtests/strategy.py`：`Strategy(initial_portfolio, triggers, cash_accrual)`
- `backtests/triggers.py`：`Trigger` + `*TriggerRequirements`（Periodic / Mkt / Risk / …）
- `backtests/actions.py`：`Action` 族（AddTrade / Hedge / …）；`CalcType` ∈ {simple, semi_path_dependent, path_dependent}
- `backtests/backtest_engine.py`：`BacktestBaseEngine.get_action_handler`（抽象）
- `backtests/generic_engine.py`：`GenericEngine.run_backtest` / `__run`（**主调度循环**）
- `backtests/backtest_objects.py`：`BackTest`（portfolio_dict / cash_payments / hedges / results）、`PnlDefinition`

### 3.2 调度循环（算法精华）

```
run_backtest(strategy, start, end, frequency|states, risks, initial_value, holiday_calendar, pnl_explain):
  with PricingContext(...):          # 整段回测共享外层定价上下文
    dates = RelativeDateSchedule(...) or states
    dates |= ∪ trigger.get_trigger_times()   # 触发日并入定价日
    risks = union(user, strategy.risks, pnl_risks, price_measure)

    BackTest(...)
    _resolve_initial_portfolio → portfolio_dict[d] + cash_payments 入/出
    _build_simple_and_semi_triggers_and_actions:
        for trigger if calc_type != path_dependent:
            for d in dates:
                if trigger.has_triggered(d, backtest): collect
            for action if not path_dependent:
                handler.apply_action(triggered_dates, backtest, info)  # 批量写组合/对冲意图
    _price_semi_det_triggers:  # 一次 Historical/按日 PricingContext 批量计价
        for day, port in portfolio_dict: port.calc(risks)
    for d in dates:            # ★ 路径依赖阶段：必须按时间序
        _process_triggers_and_actions_for_date(d, ...):
            path_dependent trigger/action → 先 __ensure_risk_results([d])
            再 apply_action；对冲按当日 risk 缩放写入后续 portfolio_dict
    _calc_new_trades
    _handle_cash:              # 现金与仓位分离；按 cash_payments 计价并累加 cash_dict
        缺价直接 RuntimeError（不静默 0）
    transaction_costs = sum(entries)
  return backtest
```

`Trigger.has_triggered` 委托 `trigger_requirements.has_triggered`；`PeriodicTriggerRequirements` 用 `RelativeDateSchedule` 生成日期集，命中时回传 `info_dict`（含 `next_schedule`）给具体 Action。

### 3.3 设计意图

- **策略 = 触发器 × 动作**，引擎可插拔（`supports_strategy` 靠 action handler 是否齐）。
- **CalcType 分两阶段**：能预知的先批量算（省往返）；依赖当日组合风险的（对冲缩放）按日走。
- **PnL 累计路径**：仓位 MTM（results）+ 现金账本（cash_dict）+ 交易成本；不是单一 equity 曲线黑箱。

### 3.4 陷阱

- 默认 `frequency='1m'`；A 股日频策略必须显式 `states=` 交易日列表或正确 holiday_calendar。
- `initial_value` 默认 **0**；现金币种从 `value.unit` 推断。
- path_dependent 日若缺 risk 结果会现场补算；对冲 `hedge_risk==0` **静默 skip**（不报错）——QuantLab 映射时应对「零风险对冲」显式告警。
- 整引擎默认走 Marquee `PricingContext`/`HistoricalPricingContext`；**本地吸收只学调度拓扑，不绑 API**。

### 3.5 QuantLab 映射

| gs 概念 | QuantLab |
|---|---|
| `PeriodicTrigger` + 调仓 Action | 叶级 who_pays / 再平衡日表（文档表，不重写引擎） |
| `CalcType.path_dependent` | 依赖当日敞口的风险缩放 / 禁买检查必须「先有当日状态再决策」 |
| `portfolio_dict` vs `cash_payments` | ledger：持仓腿 vs 现金/费用腿分列 |
| `_handle_cash` 缺价 RuntimeError | 纸面缺价 **fail-closed**，禁 NaN→0 |
| `PnlDefinition` 驱动 exit risks | 归因诊断日与主 NAV 日可分轨，但须声明 |

---

## 4. 风险结果 ResultInfo（G3 源码真相）

### 4.1 入口

- `risk/core.py`：`ResultInfo`、`ErrorValue`、`UnsupportedValue`、`FloatWithInfo`、`ScalarWithInfo`、`composition_info`
- `risk/measures.py`：参数化/相对测度
- `risk/results.py`：聚合视图（体积大；本回合读了 compose/unit 契约，未逐行读完所有视图类）

### 4.2 数据结构与聚合

```python
class ResultInfo(ABC):
    def __init__(self, risk_key, unit=None, error=None, request_id=None): ...
    # unit: dict 如 {'USD': 1} 或幂次 {'A':1,'B':-1} → 显示 "A/B"
    # error: str|dict
    # request_id: 追溯远端请求

FloatWithInfo.__add__: 仅当 self.unit == other.unit 才加；否则 ValueError('unit mismatch')
ErrorValue.__getattr__: 访问任何缺失属性 → AttributeError，带上 error 原文（防静默）
composition_info: 跨日合成时 market.location 必须一致；ErrorValue 进 errors[date] 而非当 0
```

### 4.3 设计意图

- 数值与**单位/错误/请求 id**同行，防止「裸 float」丢失审计信息。
- 聚合前校验市场位置；错误按日保留。

### 4.4 陷阱

- `unit` 是 **dict（幂次）**，不是简单字符串 `"USD"`——schema 设计要能表达复合单位或先降维为 `unit_str` + `ccy`。
- 252 不在 ResultInfo 里；年化在 `timeseries/econometrics.py`（见 §6/§7）。G3 吸收时必须**额外**钉 `periods_per_year=244`。

### 4.5 QuantLab 映射

指标结果 schema（相对计划加强）：

```
{
  value, unit, periods_per_year,   # 主报 244；对照可另字段 252
  error_code | null,               # 失败不得变 0
  request_id | run_sha,            # 本地用 run/manifest sha
  price_basis, asof                # 从 ResearchContext 拷入
}
```

---

## 5. 仓位原语（G4 源码真相）

### 5.1 真实路径（纠正「entities/」误判）

- **主实现**：`markets/position_set.py` — `Position`、`PositionSet`
- `entities/` 主要是 Marquee 实体/权限树，**不是** weight/quantity/notional 互斥逻辑所在

### 5.2 关键校验路径

**构造期（reference_notional 模式）** — `PositionSet.__init__`：

```python
if reference_notional is not None:
    for p in positions:
        if p.weight is None:   raise ... must have weights
        if p.notional is not None: raise ... cannot have notional
        if p.quantity is not None: raise ... cannot have quantities
```

**计价期（单一策略）** — `__get_default_weighting_strategy` → `__convert_positions_for_pricing`：

- 自动推断：全有 weight 且（有 reference_notional 或缺 quantity）→ Weight；否则全有 notional → Notional；否则 Quantity
- Weight **强制** `reference_notional is not None`
- `__convert_positions_for_pricing`：按策略只填 `weight` **或** `notional` **或** `quantity` 之一进 `PositionPriceInput`（其余显式 None）

### 5.3 设计意图

- 参考名义 + 权重 = 可缩放组合；禁止与股数/名义混填造成「双重定义」。
- 计价 API 一次只认一种输入空间，避免服务端歧义。

### 5.4 陷阱

- `Position` 本身**允许**同时持有 weight/quantity/notional 字段；互斥是在 **PositionSet + 计价路径** 强制的——QuantLab 应在构造层就禁，不要拖到下单。
- 等式比较对 w/q/N 做 `round(..., 5)`——浮点契约要有意设计。
- 解析/定价大量走 `GsAssetApi`（Marquee）——吸收校验逻辑即可。

### 5.5 QuantLab 映射

仓位契约页（G4）应写成：

1. 输入空间三选一：`weight`（+ `ref_notional`）| `quantity` | `notional`
2. T+1 / 现金残差 / 舍入规则单独钉
3. 对照 `v2_constructor` / ledger：构造出口断言互斥；纸面只认 quantity 账本时可从 weight 单次换算后丢弃 weight

---

## 6. 日历（G6 源码真相）

### 6.1 入口

- `datetime/gscalendar.py`：`GsCalendar`
- `datetime/date.py`：`is_business_day` / `business_day_offset` / `prev_business_date` / `business_day_count` / `date_range` / `today`
- **252 钉**：`date.py` `PaymentFrequency.DAILY = 252`；`timeseries/econometrics.py` `AnnualizationFactor.DAILY = 252`

### 6.2 实现机制

```
GsCalendar(calendars).holidays
  → Dataset(HOLIDAY) by exchange + Dataset(HOLIDAY_CURRENCY) by currency   # Marquee
  → np.busdaycalendar(weekmask='1111100', holidays=...)
is_business_day / business_day_offset → np.is_busday / np.busday_offset
```

`date_range(begin, end)` 用 `business_day_offset(..., 1)` 迭代，自动跳非营业日。

### 6.3 设计意图

- 薄封装：日历码 → 假日元组 → numpy busday；业务代码只碰 offset/is_busday。
- 货币日历与交易所日历可组合。

### 6.4 陷阱（极重要）

1. **假日数据默认来自 Marquee Dataset**——QuantLab **禁止**调用；只学 `np.busdaycalendar` 包装形态，假日表用本厂 SSE/SZSE。
2. `close_market_date` 对外部用户 **故意不用** calendars 参数（源码注释）——周末回滚可以，节假日回滚在无日历时会错。
3. **`AnnualizationFactor.DAILY = 252`** 与 **`PaymentFrequency.DAILY = 252`**：日频波动率 `annualize(x) = x * sqrt(252)`；`_get_annualization_factor` 用平均日历日距 <2.1 推断 Daily→252。这是覆盖 244 的最大暗门。
4. `volatility(..., annualization_factor=None)` 默认可改；有显式参数时应用之——QuantLab 封装必须默认 244 并拒绝静默 252。

### 6.5 QuantLab 映射

- 单一入口：`cn_calendar.is_business_day / next_business_day / business_day_offset`（SSE∪SZSE 或统一 CN）
- 所有 T+1 / 调仓日 / ResearchContext 日切走该入口
- 年化：`periods_per_year=244` 主报；252 仅对照列；禁止从 gs-quant 复制 `AnnualizationFactor` 枚举默认值

---

## 7. 可选加深：timeseries / risk_model

### 7.1 timeseries 核心变换（已读 `econometrics.py` 关键段）

- `returns` → `annualize`（√F）→ `volatility`（可传 `annualization_factor`）
- 日频推断硬编码 252（见上）
- **吸收**：变换图（收益→年化→波动）可对齐本厂指标管线；**F 必须可注入且默认 244**

### 7.2 `models/risk_model.py` 接口形态（浅读）

- `RiskModel` / `MarqueeRiskModel` / `FactorRiskModel(MarqueeRiskModel)`
- `Unit` 枚举：`PERCENT` | `STANDARD_DEVIATION`
- `FactorRiskModel`：coverage / term / universe_identifier / vendor / version；`get_factor_data` / `get_covariance_matrix` 等走 `GsFactorRiskModelApi`
- **吸收**：本地插件协议 ≈ `(asset_returns, factor_loadings, cov) → marginal / specific risk`，**数据自建**；类继承树与 Marquee 上传 API **整段跳过**

### 7.3 DataCoordinate（G7 佐证）

- `data/coordinate.py`：`DataCoordinate(measure, dataset_id, dimensions, frequency)` — dimensions 排序后成 tuple，保证身份稳定
- 映射：`{source, table, field, frequency, pit_asof}` 作为本地坐标；不接 GS 云

---

## 8. 相对 `MAIN_GS_QUANT_ABSORB_PLAN` 的源码级 Δ

| G# | 原计划说法 | 源码纠正 / 吸收动作变更 |
|---|---|---|
| **G1** | ResearchContext 合并 Pricing+Data | **拆两轴**：`pricing_asof+market/price_basis` 与 `data_window`；文档写清可组合但非同一栈；吸收 ContextVar 或显式传参二选一 |
| **G1** | 缓存开关 | **补硬规则**：live/纸面未闭合行情 **禁** 与 close 缓存共用；对齐 `PricingCache` 拒 Live |
| **G2** | Close≠Live 检查单 | **升级**：价格口径 = Market 身份；检查单要求可序列化 `price_basis`（+ 可选 relative from→to）；不只写一句「开盘/收盘」 |
| **G2** | — | **新陷阱**：`close_market_date` 无假日表时节假日回滚错误 → QuantLab 必须绑本厂日历 |
| **G3** | value+unit+error | **加强**：unit 可为幂次 dict；异单位禁加；ErrorValue 不可当数用；**强制** `periods_per_year` 与 ResultInfo 同行（防 252 从 timeseries 渗入） |
| **G4** | entities/ Position | **路径纠正**：实现在 `markets/position_set.py`；互斥在 `PositionSet(reference_notional=...)` + 计价策略三选一 |
| **G5** | Triggers→Actions→Engine | **补两阶段 CalcType** 与 **cash_payments 分离**；文档表增加「path_dependent 须先有当日 risk」；缺价 fail-closed |
| **G6** | GsCalendar 可插日历码 | **数据面禁止照搬**：假日来自 Marquee Dataset；只学 numpy busday 包装；**抬优先级提示**：252 枚举与 `annualize` 是 244 的直接威胁，G6 文档须交叉链到年化钉 |
| **G7** | Dataset 坐标 | 源码确认 dimensions 排序 tuple 身份；本地坐标设计可维持 P2 |
| **G8** | risk_model 接口 | 确认 `FactorRiskModel` ⊂ Marquee；只抄 `Unit` + get_factor/cov **方法形态**，不抄上传/云端 |
| **G9** | 缓存键含上下文 sha | 源码旁证：RiskKey 含 date+market+params+scenario+measure；本地缓存键应对齐该完整身份 |

### 优先级微调建议（文档仍优先，不挡叶25 r3 / 叶27）

1. **P0 不变**：G1（分轴 ResearchContext）+ G2（Market 身份 / price_basis）
2. **G6 年化陷阱** 升为与 G3 同批 **P1-urgent**（写进检查单「禁 252 覆盖 244」旁证链到 `econometrics.AnnualizationFactor`）
3. **G4 路径名** 在契约页改正为 `position_set.py` 语义，勿写 entities/

---

## 9. 未深读完的文件（诚实清单）

下列未逐行读透（本回合以关键控制流/不变量为准）：

- `backtests/generic_engine_action_impls.py`（各 ActionHandler 细节）
- `backtests/predefined_asset_engine.py` / `equity_vol_engine.py`（另引擎变体）
- `backtests/actions.py` 全部 Action 子类体
- `risk/results.py` 后半聚合视图、`result_handlers.py` 全部分支
- `markets/position_set.py` 定价/解析后半（API 往返）
- `models/risk_model.py` 大部 Marquee CRUD
- `timeseries/` 除 econometrics 年化外的 measures_* 
- `analytics/core/processor.py`（G9 仅旁证意图）
- `session.py` / `api/gs/*`（刻意不跟进；属禁区）

若 Leo 要第二轮，优先：`generic_engine_action_impls.py`（加仓/对冲如何改 portfolio_dict）+ `predefined_asset_engine.py`（更接近现货）。

---

## 10. 给 Leo 的口播精华（每模块 2–4 句）

1. **Context**：他们用 `ContextVar` 栈把定价日/市场/场景变成隐式参数；历史回放是「每一天换一个 CloseMarket」；Live 结果强制不进缓存——我们要的是同构的 ResearchContext，而不是抄 Marquee。
2. **Close≠Live**：PnlExplain 不是改列名，是把 market 换成 RelativeMarket(from→to)；收盘解释和实时解释是两个端点。我们纸面/回测必须声明 `price_basis`。
3. **回测引擎**：Strategy = Triggers×Actions；引擎先批量建可预知交易，再按日处理依赖当日风险的动作；仓位和现金分账，缺价直接炸——这点我们要学。
4. **ResultInfo**：每个数带着 unit/error/request_id；不同单位不能加。我们指标输出要带 244 和错误码，禁止 NaN 当 0。
5. **仓位**：真正逻辑在 `position_set.py`；有参考名义时只能权重、不能混股数/名义；计价三选一。
6. **日历/年化**：日历壳是 numpy busday，假日数据却来自 GS 云——我们只用壳+本厂假日。源码里 Daily=252 写死在枚举和 `annualize` 里，这是覆盖我们 244 的最大陷阱。

---

## 回执元数据

- 作者：Main 子代理 / box · 2026-10-25 12:42 EDT
- refs：`bbe7071653ccfc0d431e11c3a31dbd511afc394f`
- 本文件：`docs/v2/audit/MAIN_GS_QUANT_SOURCE_DEEP_DIVE_20261025_ZH.md`
- 关联计划：`docs/v2/audit/MAIN_GS_QUANT_ABSORB_PLAN_20261025_ZH.md`
- live=false；未签 `.ok`；未改 paper；未 pip install；未打 Marquee
