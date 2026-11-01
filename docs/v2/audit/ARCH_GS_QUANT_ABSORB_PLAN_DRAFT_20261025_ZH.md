# gs-quant 架构吸收计划草案（Arch · 只提案）

- **状态**：DRAFT · **live=false** · **promotion=false** · **不授权**装依赖 / 改主干 / 签 `.ok`
- **起草**：QuantLab Arch · 箱时 `2026-10-25 12:43:10 EDT`（America/New_York）
- **触发**：Leo 点名开源库 [gs-quant](https://github.com/goldmansachs/gs-quant)；主 Agent 令并行落架构对照 absorb plan（≠装库、≠改代码）
- **上游对照基线**：箱内只读 refs `docs/v2/refs/gs_quant/`（与主侧计划同源钉）
- **与主侧关系**：互补 `MAIN_GS_QUANT_ABSORB_PLAN_20261025_ZH.md`（G1–G9）。本页做**四块架构对照 + 责任映射 + 吸收级别**；**不覆盖**主侧条目编号，实施 DIFF 仍交 Eng，另审另签。
- **与 AlphaLens 队列**：`MAIN_ALPHALENS_ABSORB_PLAN_20261025_ZH.md` 仍 **pending Leo / 主裁推进中**（A1 回测≡纸面可与本草案 P0-2 互相加强）。**勿覆盖** AlphaLens 计划。

---

## 1. 仓库钉

| 项 | 值 |
|---|---|
| URL | https://github.com/goldmansachs/gs-quant |
| 默认分支 | `master` |
| HEAD sha（refs 钉） | `bbe7071653ccfc0d431e11c3a31dbd511afc394f` |
| 上游标签语义 | release **2.2.1**（commit message: `Chore: Make release 2.2.1`；committer 2026-10-13 UTC） |
| LICENSE | **Apache-2.0**（`LICENSE`；`pyproject.toml` `license = Apache-2.0`；`NOTICE` Copyright Goldman Sachs） |
| 运行前提（上游） | Python ≥3.10；**完整定价/数据 API 需 GS Marquee `client_id`/`secret`（机构客户）** |
| 箱内路径 | `docs/v2/refs/gs_quant/` · `REF_COMMIT.txt` 同上 sha |

> Apache-2.0 允许学习与带归属复用；QuantLab **默认重写**进本厂契约（PIT / 账本 / Gate / 244 年化），**不**把 `pip install gs-quant` 绑进研究/验收锁文件。

---

## 2. 四块架构对照（风险 / 定价 / 回测≡实盘 / 组合原语）

### 2.1 风险（因子 · 协方差 · 风险模型原语）

| GS 公开形态 | QuantLab 现况 | 映射判断 |
|---|---|---|
| `models.risk_model`：`RiskModel` / `FactorRiskModel` / `Unit` / `FactorType`；**实现大量走** `api.gs.risk_models`（Marquee） | Mandate 波动预算 / β 预算（Beta sleeve：16% vol · β∈[0.70,1.00] 研究轨）；`strategy` Ledoit–Wolf + `target_vol_weights`；行业中性在优化器预注册 / 构造层 | **接口形可学（暴露·协方差·边际贡献）**；**云端因子载荷/协方差 = OUT** |
| `markets.factor_analytics.FactorAnalytics` | 多因子叶 + residual factory；缺组合层「因子+特异」统一分解对接纸面 Mandate | B：本地风险模型**插件协议**（输入自建收益/载荷 → 输出边际风险）；数据自建 |
| `risk.ResultInfo` / `ErrorValue` / `FloatWithInfo`（`unit` + `error` + `request_id`） | 指标散落；244/252 对照未消尽；失败偶发静默 | B→A：结果 schema `value+unit+periods_per_year+error_code`；主报 **244**（禁用 GS 252 默认覆盖） |
| `risk.measures`：`PnlExplainClose` / `PnlExplainLive` | 纸面/回测/诊断 `price_basis` 声明不足 | 见 §2.3（P0） |

**既有方向不改写**：宇宙/闸门、Mandate HARD、优化器 FROZEN 规格、叶宇宙规则——本草案**不**改。

### 2.2 定价（通用工具 vs 专有数据）

| GS 公开形态 | 可借鉴？ | 级别 |
|---|---|---|
| `markets.PricingContext` / `HistoricalPricingContext`：栈式 as-of、`market_data_location`、`CloseMarket` vs `LiveMarket`、batch/async | **上下文对象形态**极有价值（研究/纸面/回测同一入口） | **A/B → P0 ResearchContext** |
| `instrument.*` + `resolve()` + IR/FX/EqVol 衍生品定价栈 | A 股现货+ETF 纸面主线**不需要**整栈；依赖 GS analytics 服务 | **C / 大部 OUT**（仅阅读设计，不移植） |
| `priceable.Priceable` / `Portfolio.calc(measure)` 批量测度 | 组合级「一次上下文、多测度」可对照 scorecard 聚合 | **C→B**（研究工具形；不接远端价） |
| `session.GsSession` OAuth2 / Kerberos | 认证通道本身 | **OUT**（见负面清单） |

**结论**：吸收「**定价上下文 + Close/Live 市场对象可切换且可审计**」；**不**吸收 Marquee 定价服务、曲线云端、衍生品 resolve 主线。

### 2.3 回测 ≡ 实盘（同一套原语）

| GS 公开形态 | QuantLab 文化 | 吸收点 |
|---|---|---|
| `backtests.strategy.Strategy` = Triggers → Actions → `BacktestBaseEngine` | `backtest.engine` + `ledger`/`tax`；纸面轨 `portfolio/*_paper*`；Book-Smoke / Gate；AlphaLens A1「同模块路径」 | **B**：把调仓日 / 风险缩放 / 禁买映射为 Trigger/Action **表（文档）**，不重写引擎 |
| `PnlExplainClose` ≠ `PnlExplainLive`；CloseMarket / LiveMarket 显式 | 开盘/收盘/复权口径曾漂移；execution 核对文化已有但未单页钉死 Close≠Live | **A/B · P0**：检查单增补凡 NAV/超额须声明 `price_basis` + market 等价物 |
| `execution_engine.SimulatedExecutionEngine` + `OrderEvent` | `v2_execution_costs` / paper T+1 文化；capacity_adv 成本观测 | **C/B**：事件/订单抽象可读；成本模型仍本厂 |
| `backtests.data_sources` / `api.gs.backtests*` | — | **OUT**（云端回测 API） |

**亮点一句话**：GS 把「研究定价日的市场快照」与「实盘/实时市场」做成**可切换对象**，而不是两套脚本——对齐 QuantLab「paper 轨与回测同源模块」检查文化。

### 2.4 组合原语（构造 · 约束 · 再平衡）

| GS 公开形态 | QuantLab 现况 | 吸收点 |
|---|---|---|
| `markets.position_set.Position` / `PositionSet`：`weight` / `quantity` / `notional` + `reference_notional`（有参考名义则**强制权重完备**） | `v2_constructor` / ledger 股数账本；权重↔股数↔名义转换规则未单页冻结 | **B · P1**：仓位原语契约页（输入空间 w|q|N、舍入、现金残差、T+1） |
| `markets.optimizer`：`Asset/Country/Sector/Industry/FactorConstraint`、`TurnoverConstraint`、`OptimizerObjective`、`OptimizerStrategy` | 工业选股优化器方向（非 Top-N）：`STRATEGY_OPTIMIZER_PREREG_FROZEN` + Beta 共签；单名/行业/换手/Size HARD；求解宇宙 HI_LIQ | **B/C**：约束**枚举与优先级**思路可对照；**求解器与 Marquee 优化服务 = OUT**；本厂 λ/CVX 路径不变 |
| `markets.portfolio.Portfolio` / `hedge` | 多袖套 book / Beta sleeve / satellite OFF | **C**：阅读组合树与对冲动作命名 |
| `RebalanceAction` + Periodic/Date/Risk triggers | `v2_rebalance`（Mandate ordinary_rebalance；风险缩放 stub→Beta） | **B · P2**：文档映射表即可 |

**略提**：

- **时序/日历**：`datetime.GsCalendar` + `business_day_offset` → Data(+Eng) 钉 SSE/SZSE（或统一 CN）单一入口（主侧 G6）。
- **可复现性**：上游有较完整 `gs_quant/test/*`；吸收「缓存键含上下文 sha、空结果不写长缓存」对齐 AlphaLens A5 / 主侧 G9。
- **许可证**：Apache-2.0 已钉；归属保留；默认重写。

---

## 3. 对照表（GS → QuantLab 责任方 → 吸收级别）

级别：**A** 直接借鉴接口形 · **B** 思路移植（本厂重写）· **C** 仅阅读 · **OUT** 专有数据/不可作生产源。

| GS 模块/概念 | QuantLab 责任方 | 级别 | 备注 |
|---|---|---|---|
| `PricingContext` / `DataContext` / 栈式 as-of | **Arch(+Eng)** | **A/B** | → `ResearchContext(asof, calendar, data_mode, cost_model_sha)` |
| `CloseMarket` / `LiveMarket` / `PnlExplainClose|Live` | **Arch** | **A/B** | 回测≡纸面检查单 Close≠Live |
| `ResultInfo` unit/error | **Eng(+Arch)** | **B** | 指标 schema；主报 244 |
| `Position` / `PositionSet` 互斥输入 | **Eng(+Beta)** | **B** | 仓位原语契约 |
| `Strategy(Triggers→Actions)→Engine` | **Arch(+Alpha)** | **B/C** | 文档映射，不重写引擎 |
| `GsCalendar` / business day | **Data(+Eng)** | **B** | CN 交易日历单一入口 |
| `DataCoordinate` / `Dataset` 查询身份 | **Data(+Arch)** | **B/C** | 本地坐标；**不接** GS 云 Dataset |
| `models.risk_model` **接口形** | **Beta(+Alpha)** | **B** | 插件协议；数据自建 |
| `models.risk_model` **Marquee 载荷/API** | — | **OUT** | 见 §5 |
| `markets.optimizer` 约束枚举思路 | **Strategy(+Beta)** | **B/C** | 对照 FROZEN 优化器；不接远端求解 |
| `markets.optimizer` / hedges **云端** | — | **OUT** | |
| `analytics.processor` DAG + cache 边界 | **Eng(+Web)** | **C/B** | 缓存键含 context sha |
| `instrument` 衍生品定价 + `resolve()` | **Arch** | **C / OUT** | 非 A 股现货主线 |
| `api.gs.*` / `GsSession` 凭证通道 | — | **OUT** | 全面禁止作生产源 |
| `timeseries` 统计小工具 | **AI/Alpha（只读）** | **C** | 可选阅读；不绑依赖 |
| `mcp` / `skills` 文档 | **Arch** | **C** | 仅帮助理解上游意图 |

---

## 4. 吸收候选（P0 / P1 / P2）

### P0（文档优先 · 今日可开提纲；代码另 DIFF+.ok）

| ID | 候选 | 价值 | 依赖 | 风险 | Owner | 需 Leo 点头？ |
|---|---|---|---|---|---|---|
| **P0-1** | **ResearchContext**（对齐 PricingContext/DataContext） | 叶/回测/纸面 as-of 漂移的根因治理；与 AlphaLens A1/A2 互补 | 只文档设计页；不改主干 | 过度设计拖慢叶窗；须错开 mem_probe r3 / 叶27 签窗 | Arch(+Eng) | **否**（Leo 已点名学 gs-quant；设计页即可）。装库/改主干另批 |
| **P0-2** | **Close≠Live / price_basis 显式化** | 防止「回测收盘、纸面开盘」静默分叉；强化 execution 核对文化 | 检查单增补；对齐既有 Book-Smoke/Gate | 与 AlphaLens A1 文案重复→合并引用，勿双份真理 | Arch | **否**（检查单层） |

**P0 条数 = 2**。一句话摘要：先钉「同一研究上下文 + Close/Live 价格口径可审计」，再谈组合/风险插件。

### P1

| ID | 候选 | 价值 | 依赖 | 风险 | Owner | 需 Leo 点头？ |
|---|---|---|---|---|---|---|
| **P1-1** | 指标 `ResultInfo` 形 schema（unit/error/244） | 消 244/252 混用；禁 NaN→0 | Eng 小 DIFF | 触及 scorecard 展示 | Eng(+Arch) | 否（schema）；改主报口径若争议则是 |
| **P1-2** | 仓位原语契约（w|q|N 互斥、reference_notional、T+1） | 多袖套构造可审计 | 对照 `v2_constructor`/ledger | 误伤纸面轨哈希 | Eng(+Beta) | 否（契约页）；改 ledger 另签 |
| **P1-3** | CN 交易日历单一入口（GsCalendar 思路） | T+1/节假日一致 | Data 现有日历散落 | 与美股心智/252 混淆 | Data(+Eng) | 否 |

### P2

| ID | 候选 | 价值 | 依赖 | 风险 | Owner | 需 Leo 点头？ |
|---|---|---|---|---|---|---|
| **P2-1** | Trigger/Action 文档映射表 | 策略可测性、叶 who_pays 引用 | 不改引擎 | 文档空转 | Arch(+Alpha) | 否 |
| **P2-2** | 本地 Dataset 坐标 `{source,table,field,frequency,pit_asof}` | 多源字段稳定身份 | manifest/sha 已有 | 范围蔓延 | Data(+Arch) | 否 |
| **P2-3** | 本地风险模型插件协议（非云端） | 组合因子+特异分解对接 Mandate | Beta 袖套/优化器 | 被误当成「已有 GS 风险模型」 | Beta(+Alpha) | **是**（若要进纸面风险缩放） |
| **P2-4** | 优化器约束枚举对照（单名/行业/换手） | 与 FROZEN 优化器交叉审 | Strategy/Beta 既有规格 | 重复造轮 / 扰动 HARD | Strategy(+Beta+Arch) | **是**（若改 HARD 数字） |

---

## 5. 负面清单（OUT · 不得接入 / 不得当生产行情源）

**条数 = 12（硬禁）**

1. **`GsSession` / OAuth2 `client_id`+`client_secret` / Kerberos / MQLogin** — 任何 Marquee 认证作 QuantLab 运行时依赖。
2. **`api.gs.data` / `Dataset` 远端拉取** — 不得作 A 股行情、基本面、财务 PIT、申万行业生产/验收源。
3. **`api.gs.risk_models` / Marquee `FactorRiskModel` 因子载荷与协方差云端数据** — 不得当「本厂因子」。
4. **`api.gs.price` / 云端定价与 `instrument.resolve()` 依赖的 analytics 服务** — 不得进纸面/验收价源。
5. **`api.gs.backtests` / `backtests_xasset`** — 云端回测结果不得写入 scorecard。
6. **`api.gs.portfolios` / `api.gs.hedges` / 远端 Optimizer 求解** — 不得替换本厂构造/λ 路径。
7. **`api.gs.indices` / baskets / One Delta / Security Master 云端** — 非本厂指数与证券主数据源。
8. **`api.gs.esg` / `carbon` / thematics / marketview 远端屏** — 研究可读，禁止当生产特征源。
9. **FRED/TradingEconomics 等经 gs-quant 封装的第三方** — 若要用，走本厂 Data 契约另批；不经 Marquee 暗接。
10. **利率 / FX / 通胀 / 权益波动率衍生品整栈** 作 QuantLab 主线（A 股现货+ETF 纸面优先）。
11. **用 gs-quant 默认 252 日年化覆盖已冻结的 QuantLab 244 主报口径**（252 仅对照）。
12. **声称「已 pip / 已接入 gs-quant = 可实盘或已严格验收」**；本草案与后续吸收均 `live=false`，不消费无关 `.ok`。

---

## 6. 排期与禁项（Arch 提醒）

1. **本回合**：只落本草案 + 使用既有 refs；**不** `pip install` 进 qlenv；**不**改 `TEAM_STATE`；**不**签 `.ok`。
2. **错开实窗**：叶25 mem_probe r3 另审另签；叶27 默认 14:00–14:45 ET 独立 `.ok` 窗——吸收**文档**可并行，**代码 DIFF** 必须错峰。
3. **内存**：任何试探脚本单进程 RSS≤1.5GB；优先静态读 refs，禁全量装库压测。
4. **改动交 Eng**：本页零代码授权；PASS 设计后另 DIFF + Arch 审 + 独立实峰 `.ok`。
5. **宇宙/闸门/Mandate HARD**：不在此草案改写。

---

## 7. 回执元数据

- 路径：`docs/v2/audit/ARCH_GS_QUANT_ABSORB_PLAN_DRAFT_20261025_ZH.md`
- refs HEAD：`bbe7071653ccfc0d431e11c3a31dbd511afc394f`
- LICENSE：Apache-2.0
- P0 候选条数：**2**（ResearchContext；Close≠Live/price_basis）
- OUT 清单条数：**12**
- 主侧对照：`MAIN_GS_QUANT_ABSORB_PLAN_20261025_ZH.md`（不覆盖）
- AlphaLens：`MAIN_ALPHALENS_ABSORB_PLAN_20261025_ZH.md` **仍 pending**（不覆盖）
- **live=false** · 本草案**不授权**装依赖或改代码
