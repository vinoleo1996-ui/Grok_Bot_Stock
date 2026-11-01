# 回测 ≡ 纸面 / 实盘同源检查单（Arch · 含 G2 Close≠Live）

- **状态**：CHECKLIST · **live=false** · **promotion=false** · **不改码** · **不签 `.ok`**
- **权威对齐**：
  - gs-quant 主计划 G2：`MAIN_GS_QUANT_ABSORB_PLAN_20261025_ZH.md`（APPROVED_DOC）
  - AlphaLens A1：`MAIN_ALPHALENS_ABSORB_PLAN_20261025_ZH.md`（回测≡实盘同源）
  - 源码深读：`MAIN_GS_QUANT_SOURCE_DEEP_DIVE_20261025_ZH.md` sha **`1fcb7b00ca7c53c0e8be3211550acb04c4f7f70230e91bd5651355238c53f68d`**（sha8 `1fcb7b00`）§2 / §3
- **源码钉**：`docs/v2/refs/gs_quant/` @ `bbe7071653ccfc0d431e11c3a31dbd511afc394f`（`bbe7071`）
- **价格口径实证参考**：`AI_CAPACITY_ADV_PRICE_BASIS_DIAG_ZH.md` · `ENG_PRICE_BASIS_AUDIT_RECEIPT_ZH.md`
- **G1 配套**：`ARCH_G1_RESEARCH_CONTEXT_DESIGN_20261025_ZH.md`
- **起草**：Arch · `2026-10-25 12:46:27 EDT`（America/New_York）
- **硬禁**：Marquee/`api.gs` 不作 A 股生产源；主报年化 **244**；不 pip 绑死；不挡叶25 r3 / 叶27 14:00 ET

> A1 原文交付路径曾写 `docs/v2/ARCH_CHECKLIST_BACKTEST_EQ_LIVE_ZH.md`。本回合权威落点为本文件（`docs/v2/audit/...`）。勿维护两份互相漂移的检查单。

---

## 0. 一句话原则

**凡写入主报 / Book-Smoke / 纸面 NAV / 超额 α 的数字，必须证明：scoring · universe · gate · cost · calendar · `price_basis` 与对照轨走同一模块路径；价格口径是一等公民（Market 身份），不是注释里的口头禅。**

---

## 1. 源码锚点（G2 · Close≠Live）

路径相对 `docs/v2/refs/gs_quant/gs_quant/`，HEAD=`bbe7071653ccfc0d431e11c3a31dbd511afc394f`。

### 1.1 Market 对象即口径：`markets/markets.py`

| 符号 | 行号（约） | 要点 |
|---|---|---|
| `class CloseMarket` | L140–188 | `date` + `location`；可 `to_dict()` / `__hash__` → **可进审计键** |
| `CloseMarket.roll_hr_and_min = (24, 0)` | L146 | close 可用性滚动；未到点可能回滚 `prev_business_date` |
| `class LiveMarket` | L220–239 | **无 date**，仅 location；表示运行时实时行情 |
| `close_market_date` | L60–88 | 由 location tz + roll 时点决定「哪一天的收盘」；**源码对外部用户故意不传 calendars**（周末可回滚，**无假日表时节假日回滚会错**）→ QuantLab 必须绑本厂 SSE/SZSE，禁 Marquee HOLIDAY |

### 1.2 相对 PnL = 换 Market，不是换列名：`risk/measures.py`

| 符号 | 行号（约） | 要点 |
|---|---|---|
| `__RelativeRiskMeasure.pricing_context` | L40–45 | `current.clone(market=RelativeMarket(from_market=current.market, to_market=self.__to_market))` |
| `PnlExplainClose` | L55–59 | `to_market=CloseMarket()` |
| `PnlExplainLive` | L62–66 | `to_market=LiveMarket()` |

**机制**：Close≠Live 在上游是 **两个不同的 `to_market` 端点**，强制「从哪到哪」显式；不是「同一个 close 字段有时当 live」。

### 1.3 历史路径强制 Close：`markets/historical.py`

| 符号 | 行号（约） | 要点 |
|---|---|---|
| `HistoricalPricingContext._market` | **L110–111** | 每个历史日 → `CloseMarket(..., check=True)` |
| `calc` 日循环 | L121–123 | 禁止历史批量默默用 Live |

### 1.4 缓存禁 Live：`markets/core.py`

| 符号 | 行号（约） | 要点 |
|---|---|---|
| `PricingCache.put` | **L71–73** | **`LiveMarket` 结果不入缓存**；`ErrorValue` 亦不缓存 |
| `PricingContext.market` 默认 | L519–527 | 默认 CloseMarket |

### 1.5 回测调度交叉引用（证明「口径挂在日循环上」）：`backtests/generic_engine.py`

| 符号 | 行号（约） | 要点 |
|---|---|---|
| `GenericEngine.__run` | **L211–338** | 日程 ∪ `trigger.get_trigger_times()` → resolve 初始组合 → 批量 simple/semi → **按日** `_process_triggers_and_actions_for_date` → `_handle_cash` |
| 日程并集 | L228–246 | 触发日并入定价日，避免「有成交无计价日」 |
| 路径依赖阶段 | L311–314 | 必须时间序；依赖当日状态的动作不能预批错序 |
| 现金缺价 | `_handle_cash`（深读笔记 §3） | 缺价 **RuntimeError**，不静默 0 |

**QuantLab 映射**：学调度拓扑与「缺价 fail-closed」；**不**绑 Marquee `PricingContext` API。

### 1.6 附录 · 仓位互斥：`markets/position_set.py` L249–256

`reference_notional` 路径强制全员 `weight`，禁 `notional`/`quantity`。检查单层：组合快照若声明参考名义，不得混填股数/名义（细节 G4）。

### 1.7 日历：`datetime/gscalendar.py` L112–119

假日来自 `Dataset.GS.HOLIDAY*`（Marquee）→ **只学接口**；QuantLab 假日表自建 SSE/SZSE。

---

## 2. Close≠Live 节（G2 正文 · 强制）

### 2.1 定义

| `price_basis`（声明值） | 含义（A 股现货/ETF） | 约当 GS Market |
|---|---|---|
| `close_raw` | 未复权收盘 | CloseMarket + raw close |
| `open_raw` | 未复权开盘（常见 T+1 成交） | Close≠；近似「次日 open 快照」 |
| `close_adj` / `hfq` | 复权/后复权收盘 | Close + adj |
| `total_return_engine` | 引擎 RAW OHLC + 显式公司行为补回（Book-Smoke 主路径） | Close + corporate_actions |
| `live_diag` | 诊断用实时/近实时（研究 only） | LiveMarket；**禁入主报缓存** |

### 2.2 硬规则（打勾用）

- [ ] **R1** 凡 NAV / 累计收益 / 超额 α / 分年 α / 腿归因数字，正文或 meta **必须**出现 `price_basis=...` 与 `calendar=...`。
- [ ] **R2** 回测轨与纸面轨对比时，`price_basis` **必须相同**；若不同，禁止写「一致/验证通过」，只允许写「口径分叉对照」。
- [ ] **R3** 叶自检若用 `close_raw` 算收益，而 Book-Smoke 用 `total_return_engine`，**不得**把自检数字写入主报或 ACCEPT 结论（见 Eng 回执：自检系统性低估）。
- [ ] **R4** `live_diag` 与任何 `*_raw`/`*_adj`/`total_return_engine` 序列不得画在同一未标注图上；缓存键必须分离（对齐 PricingCache 禁 Live）。
- [ ] **R5** 信号用价与收益用价可不同，但**两边都要声明**（例：capacity_adv 信号≈市值/换手、收益走引擎总回报——见 `AI_CAPACITY_ADV_PRICE_BASIS_DIAG_ZH.md`）。
- [ ] **R6** 主报年化 `periods_per_year=244`；禁止用 gs-quant/美股 252 覆盖。
- [ ] **R7** 缺价 fail-closed；禁 NaN→0 充 NAV。

### 2.3 实证锚（防空谈）

| 来源 | 已证明的分叉 |
|---|---|
| `ENG_PRICE_BASIS_AUDIT_RECEIPT_ZH.md` | Book-Smoke/X2 引擎 = RAW+公司行为总回报；叶自检常 = 未复权 close，低估数 pp/年 |
| `AI_CAPACITY_ADV_PRICE_BASIS_DIAG_ZH.md` | capacity_adv **信号**不吃复权价；除息对入选集合影响≈0；收益层仍须与引擎口径分开声明 |

---

## 3. AlphaLens A1 同源检查（合并节）

对每一条「宣称」数字（PR/回执/看板），逐项勾选：

| # | 检查项 | 证据 |
|---|---|---|
| A1-1 | scoring 函数/脚本路径与纸面轨相同（禁平行简化因子） | 路径 + sha |
| A1-2 | universe 读者与纸面相同（禁当日股票池回测污染） | pool id + asof |
| A1-3 | gate / 禁买 / 涨跌停规则同一模块 | module path |
| A1-4 | cost / 税 / 冲击模型同一（`cost_model_sha`） | sha |
| A1-5 | **`price_basis` + calendar 同一**（本页 §2） | 声明串 |
| A1-6 | ResearchContext 四元组可复述（见 G1） | asof/calendar/data_mode/cost_model_sha |
| A1-7 | 反面教材：回测≠实盘、池污染不得复发（AlphaLens A7） | 链接审计 |

**不通过 ⇒ 不得写 ACCEPT / 不得进主报 scorecard。**

---

## 4. Book-Smoke / Gate 预检（文档钩子 · 今日不改码）

建议未来预检伪码（Eng DIFF 另签）：

```text
if claim.includes_nav_or_alpha:
    require price_basis in ALLOWED
    require calendar
    require cost_model_sha or explicit_zero_cost_flag
    require same_module_paths(scoring, universe, gate, cost)
    if price_basis == live_diag: forbid_main_scorecard()
    if periods_per_year and periods_per_year != 244: forbid_main_report()
```

---

## 5. 禁止复发（短清单）

1. 回测用复权收盘、纸面用未复权开盘，无声明却称「验证一致」。
2. 叶自检未复权毛收益替代 Book-Smoke NAV。
3. live/诊断行情写入 close 长缓存。
4. 252 年化进主报。
5. Marquee / `api.gs.*` 行情或假日 Dataset 当 A 股生产源。
6. 用 gs-quant 示例 PnL 数字填 QuantLab scorecard。

---

## 6. 非目标

- 本文件不授权改引擎、不重跑回测、不签 `.ok`、不抬 live。
- 不移植 `PnlExplain*` 云端计算；只吸收 **Market 对象化口径 + 显式相对端点**。
- 不挡叶25 r3 / 叶27 14:00 ET。

---

## 7. 回执

- 路径：`docs/v2/audit/ARCH_CHECKLIST_BACKTEST_EQ_LIVE_ZH.md`
- 含 **§2 Close≠Live**（G2）+ **§3 A1 同源**
- refs：`bbe7071653ccfc0d431e11c3a31dbd511afc394f`
- **live=false** · 文档 only

---

## 修订（对齐主深读 `1fcb7b00`）

- `2026-10-25 12:50 ET`：钉深读全文 sha；显式陷阱——**`close_market_date` 无本厂假日表时节假日回滚错误**（G2 新陷阱 / 主旁注）。
- `price_basis` = **可序列化 Market 身份**（Close / Live / Relative），不是口头口径。
- 旁注收悉不挡 P0：G6/年化 252 升急；G4 真路径=`markets/position_set.py`；G5 补 CalcType 两阶段+cash 分离——另页跟进。
