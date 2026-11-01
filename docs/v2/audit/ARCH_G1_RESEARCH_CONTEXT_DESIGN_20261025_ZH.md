# G1 · ResearchContext 设计页（Arch · P0 文档 only）

- **状态**：DESIGN_DOC · **live=false** · **promotion=false** · **不改码** · **不签 `.ok`**
- **权威**：`MAIN_GS_QUANT_ABSORB_PLAN_20261025_ZH.md`（APPROVED_DOC）条目 **G1**
- **源码钉**：`docs/v2/refs/gs_quant/` @ `bbe7071653ccfc0d431e11c3a31dbd511afc394f`（release 2.2.1 / `bbe7071`）
- **深读对照**：`MAIN_GS_QUANT_SOURCE_DEEP_DIVE_20261025_ZH.md` sha **`1fcb7b00ca7c53c0e8be3211550acb04c4f7f70230e91bd5651355238c53f68d`**（sha8 `1fcb7b00`）§1（本页不复述计划表，锚定实现）
- **AlphaLens 对照**：`MAIN_ALPHALENS_ABSORB_PLAN_20261025_ZH.md` **A1**（回测≡纸面同源模块路径）
- **附录**：`ARCH_GS_QUANT_ABSORB_PLAN_DRAFT_20261025_ZH.md`（架构对照，可保留）
- **起草**：Arch · `2026-10-25 12:46:27 EDT`（America/New_York）
- **硬禁**：Marquee / `api.gs.*` 不作 A 股生产源；不 `pip install gs-quant` 绑死；主报年化 **244**；不挡叶25 r3 / 叶27 14:00 ET 窗

---

## 1. 源码锚点（必须读过再谈设计）

路径均相对 `docs/v2/refs/gs_quant/gs_quant/`，HEAD=`bbe7071653ccfc0d431e11c3a31dbd511afc394f`。

### 1.1 Context 栈：`context_base.py`

| 符号 | 行号（约） | 机制 |
|---|---|---|
| `from contextvars import ContextVar` | L17 | 协程/线程局部栈，非全局单例 |
| `_get_context_var` / `ContextMeta.path` | L25–49 | **按类独立** path key：`PricingContext.path` ≠ `DataContext.path` |
| `ContextMeta.push` / `pop` | L106–111 | `set((context,) + cls.path)` / `set(path[1:])` |
| `ContextBase.__enter__` / `__exit__` | L116–127 | enter→`push`+`_on_enter`；exit→`_on_exit` 后 **finally `pop`** |
| `ContextBaseWithDefault` | L177+ | 提供 `default_value` / `current` 回落 |

**设计意图（源码）**：隐式参数（定价日、市场、缓存开关）外置到栈顶上下文；可嵌套；未设字段从 prior/active 继承。

### 1.2 定价轴：`markets/core.py` · `PricingContext` / `PricingCache`

| 符号 | 行号（约） | 机制 |
|---|---|---|
| `class PricingCache` | L55–78 | WeakKey 缓存；键 = `(instrument, RiskKey)` |
| **`PricingCache.put`** | **L71–73** | `if not isinstance(result, ErrorValue) and not isinstance(risk_key.market, LiveMarket):` → **LiveMarket 结果永不写入缓存** |
| `class PricingContext(ContextBaseWithDefault)` | L81+ | 参数含 `pricing_date` / `market` / `use_cache` / `market_data_location` 等 |
| `PricingContext.market`（默认） | **L519–527** | 未显式传 `market` 时回落 **`CloseMarket(date=close_market_date(...), location=...)`**，不是 Live |
| `market_data_location` 默认 | L530–534 | 默认 **`PricingLocation.LDN`**（A 股勿照搬） |

### 1.3 数据窗轴（另一条栈）：`data/core.py` · `DataContext`

| 符号 | 行号（约） | 机制 |
|---|---|---|
| `class DataContext(ContextBaseWithDefault)` | L60–73 | **只**承载 `start` / `end` / `interval`；**无** market、**无** pricing_date |
| `start_date` / `end_date` 默认 | L105–111 | 默认 start=今天−30d，end=今天 |

**纠正粗计划**：PricingContext 与 DataContext **不是同一个对象、不是同一条栈**。QuantLab `ResearchContext` 必须**显式组合两轴**，不能假装「一把梭」。

### 1.4 历史日切强制 Close：`markets/historical.py`

| 符号 | 行号（约） | 机制 |
|---|---|---|
| `HistoricalPricingContext._market` | **L110–111** | `return CloseMarket(location=location, date=date, check=True)` |
| `HistoricalPricingContext.calc` 循环 | L121–123 | **每个 date** 新建 CloseMarket 打进 `RiskKey`；历史批量**不用** Live |

### 1.5 Market 身份：`markets/markets.py`（G1 缓存边界依赖）

| 符号 | 行号（约） | 机制 |
|---|---|---|
| `CloseMarket` | L140–188 | 有 `date`+`location`；`check=True` 时 date 走 `close_market_date`（可能回滚） |
| `LiveMarket` | L220–239 | **仅 location**，无 date；表示「运行时实时」 |
| `CloseMarket.roll_hr_and_min` | L146 | 默认 `(24, 0)` |

### 1.6 日历接口（只学形，假日自建）：`datetime/gscalendar.py`

| 符号 | 行号（约） | 机制 |
|---|---|---|
| `GsCalendar.holidays` | L112–119 | 假日来自 `Dataset(Dataset.GS.HOLIDAY*)` → **Marquee** |
| `business_day_calendar` | L121–127 | `numpy.busdaycalendar(weekmask, holidays=...)` |

**QuantLab**：学「日历码 → business_day_offset / is_business_day」接口；**假日表自建 SSE/SZSE（或统一 CN）**，禁止 HOLIDAY Dataset 作生产源。

### 1.7 附录一句 · 仓位互斥：`markets/position_set.py`

`PositionSet.__init__`（L240–256）：若 `reference_notional is not None`，则**每个** position 必须有 `weight`，且 **禁** `notional` / `quantity`（否则 `MqValueError`）。G1 不展开契约页（属 G4），但 ResearchContext 产物若携带组合快照，应意识到「输入空间互斥」是上游一等规则。

---

## 2. QuantLab 目标形：`ResearchContext`

### 2.1 字段（最小冻结集）

```text
ResearchContext(
  asof,              # date：决策/定价 as-of（对齐 PricingContext.pricing_date）
  calendar,          # str：日历码，建议 "CN" | "SSE" | "SZSE"（自建假日，非 Marquee）
  data_mode,         # enum：research | paper | diagnostic  （影响缺价/缓存策略）
  cost_model_sha,    # str：成本/税/冲击模型 manifest sha（空串=显式「无成本」也必须声明）
  # —— 组合两轴时建议一并携带（设计扩展，本回合不强制落码）——
  window_start,      # optional：对齐 DataContext.start（研究窗，勿塞进 asof）
  window_end,        # optional：对齐 DataContext.end
  price_basis,       # enum：见 G2；进入上下文后叶/回测/纸面只读此字段
  market_kind,       # enum：close | open | live_diag  （live_diag 禁与 close 共用长缓存）
)
```

### 2.2 不变量（设计契约）

1. **同源进入**：凡叶脚本评分、回测引擎、纸面轨（book-smoke / `*_paper*`）宣称可比的数字，必须能指出进入时的 **同一** `ResearchContext` 身份（或等价字段四元组 + `price_basis`）。
2. **两轴分离**：`asof` ≠ 研究窗；窗用 `window_*`（DataContext 轴），as-of 用 `asof`（PricingContext 轴）。
3. **默认 close**：未声明 `market_kind` 时视为 **close**（对齐源码默认 CloseMarket），禁止静默当 open/live。
4. **缓存边界**：`market_kind=live_diag`（或未来 live）的结果 **不得** 写入与 close 共享的长缓存（对齐 `PricingCache.put` 禁 Live）。空结果不写长缓存（对齐 AlphaLens A5）。
5. **缓存键最小集**：`sha(ResearchContext 规范序列化) + code_manifest_sha + price_basis + calendar`。
6. **年化**：上下文不携带 252；主报 `periods_per_year=244`（对照可另字段）。
7. **fail-closed**：缺价 / 缺日历 / 缺 cost_model_sha（当成本声称非零时）→ 拒出 NAV/超额数字，禁 NaN→0。

### 2.3 与 AlphaLens A1 的对齐

| A1 要求 | ResearchContext 如何满足 |
|---|---|
| 凡宣称数字须证明 scoring / universe / gate / cost 与纸面**同一模块路径** | 进入纸面与回测前绑定同一 context；cost 用 `cost_model_sha`；universe/gate 的 reader sha 进 `code_manifest`（A2 衔接） |
| 禁止平行简化因子 | 简化路径必须换 `data_mode=diagnostic` 且**不得**写入主报 NAV |
| A1 检查单路径 | 见 `ARCH_CHECKLIST_BACKTEST_EQ_LIVE_ZH.md`（本回合 G2）；A1 原文曾写 `docs/v2/ARCH_CHECKLIST_...`，权威落点以 **audit/** 本文件+G2 为准，不另开第二真理 |

### 2.4 进入点（文档约定 · 本回合不改码）

| 轨 | 进入约定（未来 DIFF 目标） | 今日动作 |
|---|---|---|
| 叶 / research 脚本 | 进程入口构造或读入 context；评分输出 meta 带回 `asof/calendar/price_basis/cost_model_sha` | 文档 only |
| 回测 / Book-Smoke | 引擎入口校验 context；循环内按日绑定当日 `asof`（对齐 Historical 日切 Close） | 文档 only |
| 纸面轨 | forward/monitor 与 backfill 共用同一 `price_basis`+`cost_model_sha` | 文档 only |

---

## 3. 非目标 / 不做

- 不实现 Python 类、不改 `quantlab/*`、不签 `.ok`。
- 不 `pip install gs-quant`；不接 `GsSession` / Marquee。
- 不照搬 `PricingLocation.LDN` / `roll_hr_and_min=(24,0)` 美欧心智到 A 股（A 股用自建日历 + 明确 open/close 字段）。
- 不把 DataContext 的默认「今天−30d」当 QuantLab 叶窗默认。
- 不挡叶25 mem_probe r3 / 叶27 签窗。

---

## 4. 下一步（非本回合）

1. Eng：最小 `@dataclass(frozen=True)` + `context_sha()` 草案 DIFF（另审另签）。
2. Arch：G2 检查单落地后，在 Book-Smoke 预检加「缺 `price_basis` / 缺 context 四元组 → FAIL」。
3. Data：CN 日历单一入口（G6）供 `calendar` 字段解析。

## 5. 回执

- 路径：`docs/v2/audit/ARCH_G1_RESEARCH_CONTEXT_DESIGN_20261025_ZH.md`
- refs：`bbe7071653ccfc0d431e11c3a31dbd511afc394f`
- **live=false** · 文档 only

---

## 修订

- `2026-10-25 12:50 ET`：钉主深读笔记全文 sha `1fcb7b00…`；两轴/禁 live↔close 共用缓存键已在 §1–§2。
