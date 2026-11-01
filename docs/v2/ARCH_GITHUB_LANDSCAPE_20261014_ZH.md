# GitHub 量化开源项目普查（2026-10-14，研究级）

约束：禁 GP、禁小盘、不改主干、live=false。本文只做调研，没有改代码。
数据来源：star 和最近 push 日期取自 GitHub search API（cursor-github search_repositories），抓取时间是 2026-10-14 早上 ET。亮点只根据仓库描述概括，加上 ARCH_REVIEW_20261014_ZH.md 里已核对过的发布说明；表中没有写未经核实的绩效数字。
筛选规则：量化/交易相关，star 较高，且 2026 年内有 push（停更的项目单独标出）。纯加密高频机器人、求职清单、同名但无关的仓库（如 alphafold、Quantumult）已剔除。

## 1. 名单（44 个）
### A. AI agent / LLM 交易系统
| 仓库 | ★ | 最近 push | 核心亮点 |
|---|---|---|---|
| [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) | 111112 | 2026-10-03 | 多 agent 分工：分析师、多空研究员辩论、交易员、风控 |
| [virattt/ai-hedge-fund](https://github.com/virattt/ai-hedge-fund) | 63985 | 2026-10-02 | 多“投资人人格” agent 加风控/组合经理 agent |
| [ZhuLinsen/daily_stock_analysis](https://github.com/ZhuLinsen/daily_stock_analysis) | 66332 | 2026-10-14 | LLM 多市场分析，定时零成本运行，生成决策看板并推送 |
| [HKUDS/Vibe-Trading](https://github.com/HKUDS/Vibe-Trading) | 35451 | 2026-10-13 | 个人交易 agent |
| [hsliuping/TradingAgents-CN](https://github.com/hsliuping/TradingAgents-CN) | 32283 | 2026-09-22 | TradingAgents 中文/A 股增强版 |
| [HKUDS/AI-Trader](https://github.com/HKUDS/AI-Trader) | 22778 | 2026-06-11 | agent 原生的全自动交易 |
| [AI4Finance-Foundation/FinRL](https://github.com/AI4Finance-Foundation/FinRL) | 16639 | 2026-10-13 | 金融强化学习框架 |
| [AI4Finance-Foundation/FinRobot](https://github.com/AI4Finance-Foundation/FinRobot) | 8216 | 2026-09-28 | LLM 金融 agent 平台（研报、分析链） |
| [AI4Finance-Foundation/FinRL-Trading](https://github.com/AI4Finance-Foundation/FinRL-Trading) | 3814 | 2026-09-18 | FinRL-X：模块化 AI 原生交易基础设施 |
| [simonlin1212/TradingAgents-astock](https://github.com/simonlin1212/TradingAgents-astock) | 3701 | 2026-10-11 | A 股多 agent 投研：龙虎榜、游资、解禁等数据源，7 位分析师辩论 |
| [OpenByteInc/QuantDinger](https://github.com/OpenByteInc/QuantDinger) | 12767 | 2026-10-09 | 开源 AI 交易 OS |
| [TraderAlice/OpenAlice](https://github.com/TraderAlice/OpenAlice) | 7290 | 2026-10-11 | 多资产交易 agent |
| [The-Swarm-Corporation/AutoHedge](https://github.com/The-Swarm-Corporation/AutoHedge) | 6277 | 2026-05-11 | swarm 式自治对冲基金 |
| [pipiku915/FinMem-LLM-StockTrading](https://github.com/pipiku915/FinMem-LLM-StockTrading) | 963 | 2024-08-18（停更） | 分层记忆加角色设定的 LLM 交易 agent |
| [LLMQuant/quant-mind](https://github.com/LLMQuant/quant-mind) | 3061 | 2026-08-15 | agent 原生的论文/知识抽取与检索 |
| [himself65/finance-skills](https://github.com/himself65/finance-skills) | 3407 | 2026-10-11 | AI 金融分析技能集 |
| [tradermonty/claude-trading-skills](https://github.com/tradermonty/claude-trading-skills) | 3008 | 2026-10-14 | 面向股票的 agent 技能集 |

### B. AI/LLM 因子挖掘与研究自动化
| 仓库 | ★ | 最近 push | 核心亮点 |
|---|---|---|---|
| [microsoft/RD-Agent](https://github.com/microsoft/RD-Agent) | 14930 | 2026-10-11 | 1.0.0（09-23）：因子/模型协同演化，hypo_critic/hypo_rewrite 先批判假设再改写 |
| [microsoft/qlib](https://github.com/microsoft/qlib) | 49354 | 2026-10-08 | v0.9.8 安全加固（trusted 才加载 artifact）；Alpha158/360 等因子库、滚动训练 |
| [ICT-FinD-Lab/alphagen](https://github.com/ICT-FinD-Lab/alphagen) | 1264 | 2026-06-04 | 用 RL 生成公式化 α **组合**，目标是组合 IC，不追求单因子 IC |
| [imbue-bit/AlphaGPT](https://github.com/imbue-bit/AlphaGPT) | 3183 | 2026-06-12 | 深度强化学习自动因子工厂 |
| [hugo2046/QuantsPlaybook](https://github.com/hugo2046/QuantsPlaybook) | 6555 | 2026-10-03 | 券商金工研报复现（A 股因子/择时） |
| [stefan-jansen/machine-learning-for-trading](https://github.com/stefan-jansen/machine-learning-for-trading) | 21343 | 2026-10-13 | 第 3 版：从数据到部署的 ML 交易全流程 |

### C. 选股 / 多因子 / A 股平台
| 仓库 | ★ | 最近 push | 核心亮点 |
|---|---|---|---|
| [vnpy/vnpy](https://github.com/vnpy/vnpy) | 45861 | 2026-10-06 | 4.5.0：vnpy.alpha 改用自研因子绩效分析，cs_rank 改为百分位，回测支持 fill_price/VWAP |
| [myhhub/stock](https://github.com/myhhub/stock) | 14796 | 2026-04-02 | 指标、形态、综合选股、回测 |
| [sngyai/Sequoia-X](https://github.com/sngyai/Sequoia-X) | 8036 | 2026-07-10 | A 股收盘后自动扫描选股并推送 |
| [shy3130/tick-stock-panel](https://github.com/shy3130/tick-stock-panel) | 5842 | 2026-10-14 | 自托管 A 股策略、监控、回测工作台，零运维 |
| [yutiansut/QUANTAXIS](https://github.com/yutiansut/QUANTAXIS) | 11282 | 2026-09-18 | 任务调度、分布式、多账户，纯本地 |
| [ricequant/rqalpha](https://github.com/ricequant/rqalpha) | 6823 | 2026-10-14 | 可插拔 mod 的 A 股回测框架 |
| [fasiondog/hikyuu](https://github.com/fasiondog/hikyuu) | 3560 | 2026-10-14 | C++/Python 高性能，按系统组件拆分（信号、资金管理、止损……） |
| [wondertrader/wondertrader](https://github.com/wondertrader/wondertrader) | 6389 | 2026-09-01 | 研发到交易一站式框架 |
| [zvtvz/zvt](https://github.com/zvtvz/zvt) | 4312 | 2026-07-01 | 模块化量化框架，因子/选股器抽象 |
| [waditu/czsc](https://github.com/waditu/czsc) | 6406 | 2026-10-14 | 缠论工具，附带大量信号/绩效评估工具函数 |

### D. 回测 / 撮合引擎
| 仓库 | ★ | 最近 push | 核心亮点 |
|---|---|---|---|
| [nautechsystems/nautilus_trader](https://github.com/nautechsystems/nautilus_trader) | 29978 | 2026-10-14 | Rust 原生的确定性事件驱动引擎，回测和实盘同一套代码 |
| [QuantConnect/Lean](https://github.com/QuantConnect/Lean) | 21995 | 2026-10-13 | 可插拔的 Fill/Slippage/Fee 模型 |
| [polakowo/vectorbt](https://github.com/polakowo/vectorbt) | 9367 | 2026-10-13 | 向量化参数网格回测，适合大规模敏感性扫描 |
| [kernc/backtesting.py](https://github.com/kernc/backtesting.py) | 9047 | 2026-08-05 | 轻量回测 |
| [edtechre/pybroker](https://github.com/edtechre/pybroker) | 3612 | 2026-10-05 | 结合 ML 的回测，walk-forward、bootstrap 指标 |
| [pst-group/pysystemtrade](https://github.com/pst-group/pysystemtrade) | 3553 | 2026-10-08 | Carver 体系：波动率目标、预测值缩放、组合 buffer |
| [freqtrade/freqtrade](https://github.com/freqtrade/freqtrade) | 55369 | 2026-10-14 | （加密货币）参考 lookahead/recursive 偏差分析工具 |

### E. 组合优化、风控与绩效
| 仓库 | ★ | 最近 push | 核心亮点 |
|---|---|---|---|
| [dcajasn/Riskfolio-Lib](https://github.com/dcajasn/Riskfolio-Lib) | 4541 | 2026-10-04 | CVaR/CDaR/MaxDD 等回撤类风险度量，风险预算，HRP/HERC |
| [PyPortfolio/PyPortfolioOpt](https://github.com/PyPortfolio/PyPortfolioOpt) | 6095 | 2026-07-07 | 有效前沿、Black-Litterman、HRP、协方差收缩 |
| [skfolio/skfolio](https://github.com/skfolio/skfolio) | 2494 | 2026-10-13 | sklearn API，组合用 CV（CPCV/walk-forward），可防止组合层过拟合 |
| [ranaroussi/quantstats](https://github.com/ranaroussi/quantstats) | 7706 | 2026-09-27 | 绩效/回撤 tearsheet |
| [goldmansachs/gs-quant](https://github.com/goldmansachs/gs-quant) | 13192 | 2026-10-13 | 风险模型与归因工具包 |
| [quantopian/alphalens](https://github.com/quantopian/alphalens) | 4468 | 2024-02-12（停更） | IC/分层/换手因子分析的范式；建议改用 reloaded 版或自研 |

### F. 数据工具（A 股为主）
| 仓库 | ★ | 最近 push | 核心亮点 |
|---|---|---|---|
| [akfamily/akshare](https://github.com/akfamily/akshare) | 22925 | 2026-10-13 | A 股、ETF、宏观数据接口，含交易日历 |
| [simonlin1212/a-stock-data](https://github.com/simonlin1212/a-stock-data) | 10860 | 2026-10-11 | A 股全栈数据：逐笔、研报、资金面、公告、ETF 期权、可转债 |
| [Micro-sheep/efinance](https://github.com/Micro-sheep/efinance) | 4083 | 2026-07-17 | 基金、股票、债券、期货数据 |
| [openbb-finance/OpenBB](https://github.com/openbb-finance/OpenBB) | 74212 | 2026-10-12 | 面向分析师和 agent 的开放数据平台（search 结果里显示的 owner 是 openbq-org，未核实，按原样记录） |

索引类（只作为后续扫描源）：wilsonfreitas/awesome-quant（30061 ★）、thuquant/awesome-quant（5672 ★）、paperswithbacktest/awesome-systematic-trading（14693 ★）、georgezouq/awesome-ai-in-finance（6660 ★）。

## 2. 对照 QuantLab 的可借鉴方法
| # | 借鉴点 | 来源 | 对应 QuantLab 瓶颈 / Top5 | 负责 agent | 工作量 |
|---|---|---|---|---|---|
| 1 | **组合层回撤预算**：用 CDaR/MaxDD 风险度量和风险预算替代追 CAGR，配合 skfolio 的 CPCV/walk-forward 验证权重 | Riskfolio-Lib、skfolio | 瓶颈 2 / Top3（S6 候选） | Beta + Strategy | 中 |
| 2 | **叶以“对组合的边际贡献”验收**：比照 alphagen 的组合 IC 目标，叶 ACCEPT 时加一项“加入现有叶组合后残差 IC/Calmar 的增量”，不再只看单叶 | alphagen、RD-Agent | 瓶颈 1 / Top2 α 衰减闸门 | AI + Alpha | 中 |
| 3 | **成交模型可插拔，加参数网格敏感性**：Fill/Slippage/Fee 拆成接口（参照 Lean），VWAP/close/开盘三种成交方式和费率网格用向量化方式一次扫完（参照 vectorbt），60万/100万分档输出 | Lean、vnpy 4.5、vectorbt | 瓶颈 6 / Top4 | Eng + Strategy | 中 |
| 4 | **标准因子 tearsheet 加偏差检查**：IC/分层/换手报告（alphalens 范式，自研）加 lookahead/recursive 偏差检查（参照 freqtrade），绩效页用 quantstats 风格 | alphalens、freqtrade、quantstats | 瓶颈 5 / Top5 | AI + Eng + Web | 中 |
| 5 | **数据与日历加固**：交易日历用 akshare，数据过期时告警；a-stock-data 作为公告/资金面事件叶的备用数据源（只读核对，不替换主数据） | akshare、a-stock-data | 瓶颈 4 / Top1 | Data + Eng | 小 |
| 6 | 辩论式 agent 只输出**风险标记**，不直接下决策；结论写进已有 debate memory，按事后结算给分（TradingAgents/FinMem 的分层记忆） | TradingAgents(-CN/-astock)、FinMem | Intel 第 6 项 | Intel + AI | 中 |
| 7 | 假设先批判再改写：叶的预注册加一步 critic 审查（RD-Agent hypo_critic/rewrite），减少注定失败的叶 | RD-Agent 1.0 | 叶工厂效率 | AI | 小 |
| 8 | 波动率目标和持仓 buffer（Carver 体系）用来压换手和成本 | pysystemtrade | 成本 2.2–2.5% | Beta | 小 |
| 9 | 每日收盘后定时出看板和推送（外部 cron，不起守护进程） | daily_stock_analysis、Sequoia-X | 运维 | Web + Eng | 小 |

**不采纳**：FinRL/AlphaGPT 的 RL 端到端交易（过拟合风险高，不可解释）；任何 GP/符号回归式因子搜索（违反禁 GP，alphagen 只借鉴“组合目标”的思路，不用它的生成器）；小盘或形态选股（myhhub/Sequoia-X 只参考工程流程）；实盘接口（vnpy/nautilus 的 live 功能，live=false）。

## 3. 后续
每日 9 点 ET 的巡检把扫描范围扩大到本文名单和 4 个 awesome 索引，重点跟踪 release：RD-Agent、qlib、vnpy、skfolio、Riskfolio-Lib、TradingAgents、nautilus_trader。
