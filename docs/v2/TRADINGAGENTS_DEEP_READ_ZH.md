# TradingAgents 深读（QuantLab 对照）

**角色**：AI（后台执行器）· 研究级  
**日期**：2026-10-12 · America/New_York  
**状态**：`strategy_promotion_approved=false` · `promotion_approved=false` · **不下单** · **不交 Strategy** · **未 vendor 整仓**  
**方法**：浅克隆只读 `/tmp/tradingagents_read`（分析后可删）；**禁止**把源码树拷进 QuantLab。

---

## 1. 版本 / commit 锚点

| 项 | 值 |
|---|---|
| 仓库 | https://github.com/TauricResearch/TradingAgents |
| 分支 | `main` |
| HEAD | `1394a3f72aa4393e1a98f51b382434c4b4c2d972` |
| 推送/合并日 | 2026-10-03 16:30:07 −0500（`Merge pull request #1478 … v0.6.0`） |
| 包版本 | `tradingagents.__version__ == "0.6.0"` |
| 通读日 | 2026-10-12（ET） |
| QuantLab 对照 | `TRADINGAGENTS_ADAPT_*`、`TA_QUANTMIND_FUSION_ZH.md`、`OPENSOURCE_ENG_ADOPTION_ZH.md`；桩：`quantlab/intel/debate_ledger.py`、`quantlab/intel/asof_window.py`、`research/ai_debate_memory_runner.py` |

**明确不做**：整仓 LangGraph vendor；Yahoo/Reddit/StockTwits 作 A 股主源；把框架「回测命中率/mean alpha」写成 Strategy 密封 NAV。

---

## 2. 核心调用链（`propagate` 一步步）

入口：`TradingAgentsGraph.propagate(company_name, trade_date, asset_type, portfolio)`  
文件：`tradingagents/graph/trading_graph.py`。

### 2.1 启动与图编译

1. `_validate_trade_date`：强制 `YYYY-MM-DD`，且 `trade_date ≤ today`（`date_window.get_current_date`）。
2. `run_config(self.config)` 把配置压进进程上下文；可选 `checkpoint_scope`（SqliteSaver，按 ticker+date+图形状签名）。
3. `__init__` 已用 `GraphSetup.setup_graph` 建 LangGraph：`StateGraph(AgentState)`；分析师为**并行子图**（每分析师私有消息史 + ToolNode，`max_tool_rounds` 后强制 wrap-up）。
4. `Propagator.create_initial_state` 填初始状态（见 §2.3）。

### 2.2 图拓扑（`graph/setup.py`）

```
START ──┬── Market Analyst (子图) ──┐
        ├── Sentiment Analyst ──────┤
        ├── News Analyst ───────────┤──► Bull Researcher ⇄ Bear Researcher
        ├── Fundamentals Analyst ───┤         │ (count ≥ 2×max_debate_rounds)
        └── Memory Log（并行） ─────┘         ▼
                                      Research Manager
                                              ▼
                                           Trader
                                              ▼
                          Aggressive ⇄ Conservative ⇄ Neutral
                                      (count ≥ 3×max_risk_discuss_rounds)
                                              ▼
                                      Portfolio Manager ──► END
```

路由：`conditional_logic.should_continue_debate` / `should_continue_risk_analysis`；path_map 含全量节点名，防标签漂移崩图（#1088）。

### 2.3 状态字段（`agents/state.py` + 初始值）

| 字段 | 谁写 | 谁读 |
|---|---|---|
| `company_of_interest`, `trade_date`, `asset_type` | Propagator | 全员 / 工具 InjectedState |
| `instrument_context` | `resolve_instrument_context`（yfinance 身份，fail-open） | 提示词锚点 |
| `market/sentiment/news/fundamentals_report` | 各分析师子图 | Bull/Bear/Trader |
| `investment_debate_state`（history/bull/bear/count/current_response） | Bull/Bear/RM | 条件边 + RM |
| `investment_plan` | Research Manager | Trader / PM |
| `trader_investment_plan` | Trader | 风险队 / PM |
| `risk_debate_state` | Aggressive/Conservative/Neutral | 条件边 + PM |
| `final_trade_decision`, `final_rating` | Portfolio Manager | `record_decision` / 回测 |
| `past_context`, `memory_note` | **Memory Log 节点**（与分析师并行） | **仅 PM** |
| `portfolio_context` | 调用方 `portfolio.render` | Trader / PM |

### 2.4 `_run_graph` 收尾

1. `graph.invoke` / `stream_run` → `final_state`
2. `record_decision`：写 `full_states_log_{date}.json`；`memory_log.store_decision(..., rating=run_rating(state))`（**pending**，本轮不结算自身）
3. `clear_checkpoint_on_success`
4. 返回 `(final_state, run_rating)` — 五档 Buy/Overweight/Hold/Underweight/Sell，或 `REVIEW`（不可交易哨兵，#1170）

### 2.5 Memory Log 并行节点（关键设计）

`_memory_step`：先 `settle_all_pending(wait=False)`（结算**其它**已到窗决策），再 `get_past_context(ticker, as_of=trade_date if historical else None)`。失败只写 `memory_note`，**不中断**分析师路径。

---

## 3. 真实数据处理（日期切片 / 缺数 / 前视）

核心纪律集中在 `tradingagents/dataflows/date_window.py` + `agents/tools.py`（工具用 `InjectedState("trade_date")`，模型填的日期会被夹死）。

### 3.1 通用守卫

| 函数 | 行为 | 路径 |
|---|---|---|
| `as_of(requested, trade_date)` | 请求日 > 交易日 → 回落到 `trade_date` | `date_window.py` |
| `as_of_window(start, end, trade_date)` | 末端夹紧；窗口整体落在交易日之后则平移保持长度；坏 start → `ValueError` | 同上 |
| `in_window(pub_dt, start, end)` | 半开窗 `[start, end+1day)`；**无日期**仅当窗触及「现在」才保留（回测不可证伪未来） | 同上 |
| `coverage_gap(...)` | 源未观测到该窗 → 返回 *unavailable* 占位，**禁止**当「无新闻」 | 同上 |
| `withhold_live_profile` | 历史跑：拒 Yahoo/AV 当日概况（无 vintage） | 同上 |
| `withhold_undated_statements` | 历史跑：拒无 filing date 的 Yahoo/AV 报表 | 同上 |
| `withhold_undisclosed_trades` | 历史跑：拒无 Form4 公开日的内幕交易 | 同上 |
| `is_historical` | `trade_date < today` | 同上 |

短摘（夹紧，≤5 行）：

```python
# date_window.as_of
parsed = _parse(requested)
return requested if parsed is not None and parsed <= _parse(trade_date) else trade_date
```

### 3.2 各数据工具如何切片

| 工具 | 切片 | 缺数据 | 前视挡法 |
|---|---|---|---|
| `get_stock_data` | `as_of_window` → vendor OHLCV | `NoMarketDataError` → `NO_DATA_AVAILABLE` 文案；禁止编造 | 末端 ≤ trade_date；Yahoo `load_ohlcv` 再滤 `Date ≤ as_of` |
| `get_indicators` / `get_verified_market_snapshot` | `as_of(curr_date)` | 同左；snapshot 可 stale 拒绝 | `snapshot._verified_rows` 再截断 |
| `get_fundamentals` | `as_of` | 历史 → `withhold_live_profile` | 不把「今日」概况喂进过去日 |
| `get_balance/cash/income` | `as_of` | Yahoo/AV 历史 → `withhold_undated_statements`；**SEC EDGAR** 按 `filed ≤ as_of` 取最新 filing | EDGAR `_as_of`；Yahoo 无 filing 则整段拒发 |
| `get_news` / `get_global_news` | 窗夹紧 + `in_window` | `coverage_gap` 或显式 unavailable | 发布时间 UTC 规范化；无日期策略见上 |
| `get_insider_transactions` | 传 `trade_date` | 历史无 filing → withhold | 同上 |
| `get_macro_indicators` (FRED) | `as_of(curr_date)` | 可选类：失败降级哨兵，不崩跑 | 末端夹紧 |
| `get_prediction_markets` (Polymarket) | — | **历史跑整段 withhold**（只服务 live odds） | `is_historical` |
| Sentiment 预取 | 新闻 7 日窗 + StockTwits + Reddit | 失败标 unavailable；**源码自承：社媒非归档，历史非严格 PIT** | `in_window` 修剪；仍有覆盖盲区 |

SEC EDGAR（`vendors/sec_edgar.py`）：事实带 `filed`；同一报告期取 **as_of 当日及之前最新 filing**；无则 `NoMarketDataError`。这是框架里对「报表公开日」做得最硬的路径——但**只服务美股 US filer**。

### 3.3 结算侧行情（`memory/settlement.py`）

- `fetch_returns`：Yahoo `get_closes`；持有窗按**交易日**数（日历跨度约 `holding_days×7/5+7`）；`len(stock) ≤ holding_days` → 返回全 None，**保持 pending**（#1169）。
- `alpha = raw − bench_ret`；`resolution_date = exit bar 日`，供记忆 PIT 过滤（#1251）。
- 基准：`benchmark_ticker` 覆盖，否则 `benchmark_map` 按后缀（`.SS`→`000001.SS`，`.SZ`→`399001.SZ`，默认 `SPY`）。**不是 QuantLab 的 510300 ETF**。

### 3.4 回测网格（`backtest.py`）

- 单元格独立；**明确不是组合模拟器**（无数量/成交价/现金账本）。
- 独立 `memory_log_path`，避免污染实盘记忆。
- `summarize`：按 rating 算 hit_rate / mean_alpha；文案自承「指示性、不可严格复现」（单次采样 + 文本源未归档）。

### 3.5 为何 QuantLab 拒 Yahoo（及同栈）

| 边界 | 原因（对照 QuantLab 契约） |
|---|---|
| Yahoo OHLCV / yfinance | 非本地 PIT；复权/时区/停牌口径与 tushare/D0 panel 不一致；A 股 `.SS/.SZ` 仅为 Yahoo 记号，不等于 `available_at` |
| Yahoo 概况/无 filing 报表 | 框架已在历史跑 withhold——说明**作者也承认不可 PIT**；QuantLab 应直接用有 `available_at` 的本地财报 |
| Reddit / StockTwits | 语言与覆盖错配；源码写明非归档；无 A 股 `available_at` |
| Polymarket / 默认 FRED 主叙事 | 美欧宏观/预测市场；可作研究旁路，不可当 A 股主证据 |
| 结算默认 SPY / 上证综指 Yahoo 代码 | Mandate 主书相对 **510300**；现金 NAV 仍属 Strategy，settlement ≠ 晋级 |

Eng 决策已写死：**ADAPT 思想，不 vendor 整仓**（`OPENSOURCE_ENG_ADOPTION_ZH.md`）。

---

## 4. 问题思路：它解决什么 / 不解决什么

### 4.1 它在解决的决策质量问题

1. **角色分离与对抗**：事实报告（分析师）≠ 立场（Bull/Bear）≠ 交易提案（Trader）≠ 风险姿态（Aggressive/Conservative/Neutral）≠ 最终五档评级（PM）。降低单模型「自说自话」。
2. **结构化输出与评级完整性**：RM/Trader/PM 走 schema；`REVIEW` 哨兵避免把「读不出」 silently 变成 Hold（#1170）。
3. **时点意识工具层**：模型乱填日期不能越过 `trade_date`；缺观测窗用 coverage_gap；无 vintage 数据在历史跑拒发。
4. **事后 α 结算 + 短反思回灌**：pending → 持有窗走完 → raw/alpha + 2–4 句 reflection → 同票/跨票 past_context 进 **下一次 PM**（分析师侧默认不读记忆，防污染事实层）。
5. **诚实评价边界**：`backtest.py` 文档写死「评价决策质量，不是组合模拟器」——这与 QuantLab「settlement ≠ 现金 NAV」一致。

### 4.2 它明确不解决（QuantLab 仍要自建）

| 缺口 | 说明 |
|---|---|
| 现金账本 / 可复现 NAV | 无仓位数量、无成交、无费用滑点账本；回测只是 rating×事后 α 聚合 |
| A 股制度/公告 PIT 主链 | 无交易所公告 `available_at`、无涨跌停/停牌/ST、无北向/融资融券本地表 |
| 可消费权重长表 → Book-Smoke | 输出是自然语言决策 + markdown 记忆，不是 `session,instrument_id,weight` |
| 门锁 CAGR/MDD @60万∧100万 | 框架无 AUM 档、无 Strategy 密封门 |
| 严格可复现 | 自承 LLM 单次采样 + 社媒/新闻未归档 → 指示性 |
| 晋级治理 | 无 `promotion_approved` / `validate_gate`；任何「年化好看」都不能当密封 |

一句话：**TradingAgents = 决策质量闭环脚手架；QuantLab Strategy = 可审计现金 NAV。二者不可互相冒充。**

---

## 5. 与 QuantLab 现状差距

| 维度 | TradingAgents 0.6.0 | QuantLab（2026-10-12） | 差距 |
|---|---|---|---|
| 编排 | 完整 LangGraph 并行分析师+双辩论 | **无**图引擎；角色由提示词/runner 顺序模拟 | 不搬图；可用顺序/并行任务近似 |
| 账本 | markdown `trading_memory.md` | JSONL `JsonlDebateLedger`（Eng） | 形态不同；语义已对齐 pending/settled |
| 结算基准 | SPY / 后缀 map（含 000001.SS） | **510300**（`ai_debate_memory_runner`） | 已按 Mandate 改；勿回退 Yahoo 基准 |
| 结算行情 | Yahoo closes | 本地 D0 panels + `etf_daily_adj` | 正确方向；覆盖不足时写 coverage_gap |
| PIT | `date_window` 全工具夹紧 | `intel/asof_window.py`（文本/舆情）+ Data `available_at` | 行情/财报 readers 需持续对齐 as_of |
| 分析师工具 | Yahoo/AV/EDGAR/FRED/Reddit… | 本地 announcements / panels / S1 舆情接口 | **禁止**接 Yahoo 主路径 |
| 记忆回灌对象 | 仅 PM | runner 注入辩论上下文 + factor_evolve 权重长表 | 融合蓝图已写；Book-Smoke 挂接待批 |
| 风控三态辩论 | 有 | 角色规格有，执行仍薄 | 见 G 清单 |
| promotion | 无 | 恒 false | 保持 |
| 回测 | 决策网格 + hit_rate | Book-Smoke / NAV（Strategy） | 禁止用前者冒充后者 |

已有研究桩（勿重复造轮）：

- `quantlab/intel/debate_ledger.py` — TypedDict + JSONL  
- `quantlab/intel/asof_window.py` — as_of / coverage_gap 思想移植  
- `research/ai_debate_memory_runner.py` — 辩论 dry-run、记忆回灌、相对 510300 settle、factor_evolve 权重上下文  

---

## 6. 可执行缺口清单

| ID | 缺口 | Owner | 验收标准 | 已有桩？ | 下一步动作 |
|---|---|---|---|---|---|
| **G1** | 分析师四报消费**本地 PIT**（行情/公告/财报），拒 Yahoo | Data + AI | 任一历史 `trade_session`：工具输出 `available_at≤asof`；缺窗只出 `coverage_gap`，零 Yahoo 调用 | 部分（`asof_window`、messages loader） | Data 暴露 reader；AI 改 runner 工具绑定到本地，删 Yahoo 路径 |
| **G2** | 情绪源换 A 股本地（雪球/同花顺等 S1），禁 Reddit/StockTwits | Data + AI | S1 接口有 `available_at`；历史跑无「伪空」；未交付前 sentiment 角色显式 `coverage_gap` | 接口文档有，主源未齐 | Data 落盘 S1；AI 在 runner 接 `load_*` 或跳过并记账 |
| **G3** | 完整 Bull⇄Bear 多轮 + RM 结构化计划写入 ledger | AI | `DebateTurn` 含 bull/bear/RM；`count` 达配置轮次；RM 五档之一或 Abstain | 有简化 stub | 按 `TRADINGAGENTS_ADAPT_ROLES` 扩提示词；轮次参数化 |
| **G4** | 风险三态（Aggressive/Conservative/Neutral）→ PM 终评 | AI | ledger 有三态 turns + PM `DecisionEntry`；`REVIEW`/`Abstain` 不记成 Hold | 角色名在 Enum，执行薄 | 实现三态节点；PM 只读风险史+记忆块 |
| **G5** | 结算窗可配置 + 严格 pending 直到满窗 | AI + Eng | `horizon_days` 可配；窗未满不写非 null alpha；满窗后相对 **510300** | runner 已有 510300 settle | 对齐 TA `#1169` 行为；单测覆盖不足与满窗 |
| **G6** | `resolution_date` / as_of 过滤记忆回灌（防前视课） | Eng + AI | 历史跑 `get_past_context` 等价：仅 `resolved≤asof` 的 settlement 注入 | ledger 有 settled_at；过滤逻辑弱 | Eng 加字段约定；AI runner 过滤 |
| **G7** | 反思质量：2–4 句可复用中文课，绑 alpha 数字 | AI | settlement.reflection_zh 非空、含 alpha 引用、可注入下轮 | 有模板字符串 | 可选接 LLM；无钥时保留规则模板，禁止空话 |
| **G8** | `factor_evolve` 权重长表 ↔ 辩论 `mechanism_tag`/`approve_research` | AI + Alpha | 辩论上下文可见权重行数；approve 的机制可进 evolve 队列（二期强制） | 权重上下文已接 stub | 按 `TA_QUANTMIND_FUSION_ZH` 写字段；禁平行空转 |
| **G9** | Book-Smoke 消费权重（非 rating 当成交价） | Beta + New Bot | `WeightLongTableSleeve` 读得到 parquet；探索窗相对 510300；**不下单** | New Bot 主跑探索窗 | AI 只核路径；Beta 出可消费表 |
| **G10** | 决策网格评价（hit_rate/mean α）与 NAV **分轨报告** | AI + Eng | 单独 `output/intel/decision_quality_*`；文案强制「非 NAV」 | 无独立汇总器 | 仿 `backtest.summarize` 读 JSONL；禁止写入 Strategy 密封目录 |
| **G11** | 标的身份映射（`.SS/.SZ` ↔ `sh./sz./ts_code`） | Eng | 单一映射表；辩论与 panel id 一致 | 分散 ad-hoc | Eng 定表；AI/Data 只消费 |
| **G12** | 财报 filing/公告日 PIT（对标 EDGAR `_as_of`） | Data | A 股报表/公告按公开日过滤；无公开日 → withhold | 公告 loader 部分 | Data 补 filing/announce 时间戳；禁用「报告期」冒充公开日 |
| **G13** | Checkpoint/断点续跑（可选） | Eng | 长辩论可按 session+instrument 恢复；签名含角色集 | 无 | 低优先级；目录约定属产物布局，Eng 已 REJECT 强占 |
| **G14** | 治理门：全程 `promotion_approved=false` | 全员 | 任何评分/α 不得触发 Strategy 交卷 | 已恒 false | 保持；仅 Leo 原话密封可改 |

**本轮已完成的文档动作**：本文件落盘；未 clone 进 QuantLab 树；未下单；未交 Strategy。

---

## 7. 通读目录清单（顶层）

只读分析覆盖的顶层 / 核心子树：

1. `tradingagents/graph/` — TradingAgentsGraph、setup、propagation、conditional_logic、analyst_execution、checkpointer  
2. `tradingagents/agents/analysts/` — market / sentiment / news / fundamentals / turn  
3. `tradingagents/agents/researchers/` — bull / bear  
4. `tradingagents/agents/managers/` — research_manager / portfolio_manager  
5. `tradingagents/agents/trader/` — trader  
6. `tradingagents/agents/risk_mgmt/` — aggressive / conservative / neutral  
7. `tradingagents/agents/` — state、tools、rating、schemas、context、structured、post_screen  
8. `tradingagents/memory/` — log / settlement / reflection  
9. `tradingagents/dataflows/` — date_window、router、config、symbols、errors  
10. `tradingagents/dataflows/vendors/` — yahoo/*、sec_edgar、alpha_vantage、reddit、stocktwits、fred、polymarket  
11. `tradingagents/backtest.py`、`default_config.py`、`portfolio.py`、`reporting.py`  
12. `cli/`、`tests/`（抽样：memory、lookahead、date_boundaries、backtest、sec_edgar）  
13. 根：`README.md`、`CHANGELOG.md`、`pyproject.toml`（未当正文复述）

---

## 8. 相关 QuantLab 路径

- 适配总览/角色/PIT：`docs/v2/TRADINGAGENTS_ADAPT_OVERVIEW_ZH.md` 等  
- 融合：`docs/v2/TA_QUANTMIND_FUSION_ZH.md`  
- Eng 采纳：`docs/v2/OPENSOURCE_ENG_ADOPTION_ZH.md`  
- 桩：`quantlab/intel/debate_ledger.py`、`quantlab/intel/asof_window.py`、`research/ai_debate_memory_runner.py`

---

*End of deep read. promotion_approved=false. No vendor. No orders.*
