# gs-quant 吸收计划（主裁已开 · Leo 2026-10-25「要学」授权）

- **触发**：Leo 2026-10-25 ~12:37 ET —「https://github.com/goldmansachs/gs-quant 这不也是一个很牛逼的参考吗，你为什么也不学」
- **上游**：Goldman Sachs `gs-quant`（Python 量化工具包，Apache-2.0）
- **箱内 refs**：`docs/v2/refs/gs_quant/`（浅克隆；`REF_COMMIT.txt`=`bbe7071653ccfc0d431e11c3a31dbd511afc394f` / release 2.2.1；`PACKAGE_LAYOUT.txt`；`REF_README_ZH.md`；上游 `README.md`/`LICENSE`）
- **QuantLab 语境**：A 股 + 境内股票 ETF；纸面 **60万 / 100万**；`live=false`；`promotion_approved=false`
- **主旨**：学**接口分层、上下文、风险结果单位、回测 DSL、日历/仓位原语**；**不**把 Marquee / GS 私有数据集当生产源
- **对照**：与 `MAIN_ALPHALENS_ABSORB_PLAN_20261025_ZH.md` 互补（A1 回测≡纸面 可互相加强）；本计划不覆盖 LLM/拥挤 UI

## HARD DO-NOT-COPY（全文适用）

1. **禁止**以 GS Marquee `client_id`/`secret`、`api/gs/*` 远端数据集作 A 股行情、基本面、申万、财务 PIT 的生产/验收源（机构客户通道 ≠ QuantLab 数据契约）。
2. **禁止**声称「已接入 gs-quant = 可实盘 / 已通过严格验收」；本回合与后续吸收均 `live=false`，不签无关 `.ok`。
3. **禁止**整仓移植利率/FX/通胀/权益波动率衍生品定价栈作 QuantLab 主线（A 股现货+ETF 纸面优先）。
4. **禁止**下载或依赖 GS 专有风险模型因子载荷/协方差云端数据当「本厂因子」。
5. **禁止**用 gs-quant 的 252 日美股年化默认值**覆盖**已冻结的 QuantLab **244** 主报口径（252 仅对照，见 `AI_ANNUALIZATION_244_NOTE_ZH.md`）。
6. Apache-2.0 允许学习与带归属复用小工具；**默认重写**进 QuantLab 契约（PIT、账本、Gate、容量），不 `pip install gs-quant` 绑死 Marquee。

## 时钟备注

- 用户时区：`America/New_York`（本回合约 **2026-10-25 12:38 EDT**）。
- 盒上默认 `date` 曾显示 **CST（UTC+8）**；用 `TZ=America/New_York` 才与用户钟对齐。审计时间戳以 **ET** 标注；勿混用 CST 墙钟写 TEAM 排期。

## 吸收项（G1–G9）

| # | 模式 | gs-quant 做什么 | QuantLab 缺口 | 吸收动作（文档优先） | 专责 | 优先级 |
|---|---|---|---|---|---|---|
| G1 | **PricingContext / DataContext** | `markets.PricingContext` + `data.DataContext`：线程/栈式 as-of、市场位置、缓存开关；`HistoricalPricingContext` 批量历史；`CloseMarket` vs `LiveMarket` | as-of / 决策日 / 行情日散落在叶脚本与 paper 轨；无统一「研究上下文」对象；易漂移 | 设计 1 页：`ResearchContext(asof, calendar, data_mode, cost_model_sha)`；要求叶/回测/纸面进入同一上下文；对照 AlphaLens A1 | Arch(+Eng) | **P0** |
| G2 | **回测≡市价口径显式化** | `PnlExplainClose` / `PnlExplainLive`；Close vs Live 市场对象可切换且可审计 | 纸面/回测/诊断样本价格口径（开盘/收盘/复权）文档化不足；曾有腿重建不一致 | 检查单增补：凡 NAV/超额须声明 `price_basis` + market 对象等价物；与 `ARCH_CHECKLIST_BACKTEST_EQ_LIVE` 合并一节「Close≠Live」 | Arch | **P0** |
| G3 | **RiskMeasure + ResultInfo 单位/错误** | `risk.ResultInfo`：`unit` / `error` / `request_id`；多测度组合结果 | 指标散落；244/252 混用未消尽；失败常无结构化 error 码 | 指标结果 schema：`value + unit + periods_per_year + error_code`；主报 244；失败不得静默 NaN 当 0 | Eng(+Arch) | **P1** |
| G4 | **Position：weight / quantity / notional 互斥** | `Position`/`PositionSet`：参考名义下强制权重完备；禁 weight+notional 双填 | 多袖套/纸面有股数账本，但构造层权重↔股数↔名义转换规则未单页冻结 | 1 页仓位原语契约：输入空间（w\|q\|N）、舍入、现金残差、T+1；对 `v2_constructor`/`ledger` 对照表 | Eng(+Beta) | **P1** |
| G5 | **Backtest = Strategy(Triggers→Actions)→Engine** | `backtests.strategy.Strategy` + `triggers` + `actions` + `BacktestBaseEngine`；事件驱动、可测 | 引擎有 ledger/tax，策略触发多为脚本内联；难做「同策略换引擎」对照 | 文档：把调仓日/风险缩放/禁买映射为 Trigger/Action 表（不重写引擎）；叶级 who_pays 可引用该表 | Arch(+Alpha) | **P2** |
| G6 | **交易所日历抽象** | `GsCalendar` + `business_day_offset` / `is_business_day`；可插日历码 | A 股交易日历存在但分散；与美股 252 心智易混 | 钉 `SSE/SZSE`（或统一 CN）日历单一入口；所有「下一交易日 / T+1」走该入口；测节假日 | Data(+Eng) | **P1** |
| G7 | **DataCoordinate / Dataset 查询身份** | `data.coordinate.DataCoordinate` + `Dataset`/`DataQuery`：字段+实体+频率坐标 | 有 manifest/sha，缺「坐标」级稳定身份（同一字段多源时） | 设计：本地 Dataset 坐标 = `{source, table, field, frequency, pit_asof}`；写入回执，不接 GS 云 | Data(+Arch) | **P2** |
| G8 | **组合风险归因原语（非云端模型）** | `models.risk_model` + `markets.factor_analytics`：因子暴露/协方差接口形态；`Unit` 枚举 | 有多因子叶，缺组合层「因子+特异」分解与对纸面 Mandate 的对接 | 只吸收**接口形态**：本地风险模型插件协议（输入收益/因子载荷→输出边际风险）；**数据自建**；不对 Marquee Risk Model | Beta(+Alpha) | **P2** |
| G9 | **Analytics Processor + 缓存边界** | `analytics.core.processor` DAG；`cachetools`；PricingCache 可选 | 有 `v2_panel_cache`，缺「处理器图 + 缓存键含上下文 sha」规范 | 规定：任何缓存键必须含 `ResearchContext` sha + 代码 manifest；空结果不写长缓存（对齐 AlphaLens A5） | Eng(+Web) | **P3** |

## 排期建议（不挡叶25 / 叶27）

1. **本小时（文档）**：refs 齐 + 本计划落盘；**不**改 paper/live；**不**签 `.ok`。
2. **今日内（已开）**：G1/G2 检查单草案；随后 G3 schema + G4/G6 契约页提纲。
3. **代码变更**：一律另 DIFF + Arch 审 + 独立 `.ok`；错开 mem_probe r3 / 叶27 14:00 ET 窗。
4. **周一双通后**：G6 日历与 Data 中转无关项可并行；G7 坐标设计不依赖 RELAY 解冻。

## 不做

- 不 `pip install gs-quant` 进研究/验收锁文件（除非 Leo 另批「仅离线单元测试沙箱」且禁网络 Marquee）。
- 不移植 `api/gs/*`、篮子/指数云端、One Delta、ESG/Carbon 远端屏。
- 不把 gs-quant 示例 notebook 的绩效数字写入 QuantLab scorecard。
- 不抬 live；不消费 `9e4359f9` 等无关票。

## TEAM_STATE 一行摘要（可粘贴）

`gs-quant 吸收：refs@bbe7071；源码深读 1fcb7b00；计划主裁开 P0 文档（G1/G2→Arch 源码锚定）；禁 Marquee；live=false。`

## 源码深读（Leo t1072u 加码）

- 笔记：`docs/v2/audit/MAIN_GS_QUANT_SOURCE_DEEP_DIVE_20261025_ZH.md` sha8 **`1fcb7b00`**（2026-10-25 ~12:44 ET）
- 相对本计划关键 Δ（以笔记为准）：
  1. G1 拆 PricingContext / DataContext 两轴；缓存禁 live↔close 共用
  2. G2 = 可序列化 Market/`price_basis`（非改列名）；`close_market_date` 无假日表会错
  3. G3 强制同行 `periods_per_year`（主报 244）
  4. G4 真路径 `markets/position_set.py`（非 entities）
  5. G5 补 CalcType 两阶段 + cash_payments 分离
  6. G6/年化：`AnnualizationFactor.DAILY=252` 升急旁证；假日禁吃 Marquee Dataset

## 主裁状态

- 【APPROVED_DOC】Leo t1070u「为什么也不学」= 授权吸收；主裁开 G1/G2 文档；代码仍另 DIFF+.ok
- 与 AlphaLens 计划并行；冲突时以 QuantLab 数据契约与 244 年化钉为准

## 回执元数据

- 起草：Main / box · ET 标签 2026-10-25
- refs 路径：`docs/v2/refs/gs_quant/`
- 本文件路径：`docs/v2/audit/MAIN_GS_QUANT_ABSORB_PLAN_20261025_ZH.md`
