# TradingAgents 适配总览（QuantLab）

**角色**：AI（工厂 + 辩论/记忆）· 研究级  
**日期**：2026-10-12 · America/New_York  
**状态**：`strategy_promotion_approved=false` · `promotion_approved=false` · **不开 NAV / 冒烟** · **不交 Strategy** · **不启 v27**  
**依据**：Leo 认定合适并令立刻做（经 New Bot）；Eng 已 ADAPT 契约见 `OPENSOURCE_ENG_ADOPTION_ZH.md`  
**源框架**：TauricResearch/TradingAgents（LangGraph 多智能体：基本面/情绪/新闻/技术分析师 → 多空辩论 → 交易员 → 风险/组合经理；记忆日志结算；时点完整性）  
**中文镜像要点**：https://www.zdoc.app/zh/TauricResearch/TradingAgents  

---

## 1. 为何适配（一句话）

采其 **角色分工 + 结构化辩论 + 决策记忆结算 + as_of 时点纪律**；  
**拒** 整仓 LangGraph、美股 Yahoo/Reddit/StockTwits 默认工具链、以及把「无现金账本的回测年化」冒充 Strategy NAV。

---

## 2. 与 QuantLab 边界

| 层 | QuantLab 角色 | TradingAgents 映射 | 本适配做什么 |
|---|---|---|---|
| 行情 / 公告 PIT | **Data** | Yahoo 等外源 → **本地 PIT** | 只消费 Data 已落盘 + Eng readers；不直连 Yahoo |
| 残差因子 / GP | **Alpha** | 分析师「事实报告」的一部分 | 辩论输入可引用 Alpha 契约报告；不虚构晋级 |
| β 袖套 / 事件臂 | **Beta** | 风险预算旁路（可选） | settled rating **仅可**作预注册调节器特征；禁止当成交价 |
| 组合 / 账本 | **Strategy** | Portfolio Manager 下单 | **本阶段不交 Strategy**；辩论与记忆不下单 |
| 平台契约 | **Eng** | date_window / ledger | 已落：`intel/asof_window.py`、`intel/debate_ledger.py` |
| 辩论角色 + 反思 | **AI**（本文） | Bull/Bear + memory | 写提示词/技能、读写 `JsonlDebateLedger`；控峰；研究级 |

Mandate 主书仍以个股 + ETF 为准（`MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md`）。  
**可转债 / 黄金主线、垃圾事件臂提案（seat/解禁/tercile/分红DY/ocf/披露日历同构）本阶段暂停。**

---

## 3. 明确不用：美股 Yahoo 链路

| 禁项 | 原因 |
|---|---|
| Yahoo Finance / yfinance 作 A 股主行情 | 非 QuantLab PIT 契约；时区与复权口径不一致 |
| StockTwits / Reddit 作 A 股主舆情 | 覆盖与语言错配；无 `available_at` |
| 照搬 TradingAgents 默认 `dataflows` 美股工具 | Eng 决策：**ADAPT 思想、不 vendor 整仓** |
| 把框架自带「回测年化」写成 Strategy 密封结论 | settlement ≠ 现金 NAV；`strategy_promotion_approved=false` |

A 股标的记号沿用 QuantLab / tushare 习惯（如 `sh.600000` / `600000.SH`）；若对接外部示例里的 `.SS`/`.SZ`，须在 reader 层显式映射——**待 Eng 定**统一映射表，本文不捏造模块名。

---

## 4. A 股数据契约（研究级）

| 用途 | 约定入口 | 备注 |
|---|---|---|
| 消息 / 公告 PIT | `quantlab.intel.messages.load_message_frame` / `load_messages_for_session` | 经 `asof_window`；源表多为 `data/v2/announcements/...`（Data 管） |
| 文本 as_of 守卫 | `quantlab.intel.asof_window` | 决策时默认 session **18:00** 墙钟；未来行丢弃或 `strict_asof` 抛错 |
| Embedding（若有） | `quantlab.intel.embeddings.load_embedding_panels` | 缺文件 → 空 panel + TODO，不致命 |
| 辩论账本 | `quantlab.intel.debate_ledger.JsonlDebateLedger` | 默认路径 `output/intel/debate_ledger.jsonl` |
| 行情 / 财务 PIT | Data 落盘 + 既有 readers（`quantlab/data_os/pit.py` 等） | tushare 仅作 Data 拉数后端，辩论层不直拉 |
| 舆情热度（S1） | `docs/v2/S1_SENTIMENT_INTERFACE.md` | `xueqiu`/`ths` 等 **本地 PIT**；未交付前不作主源 |

**原则**：辩论只消费「`available_at` ≤ `asof_decision_ts`」的证据；覆盖缺口写 `coverage_gap`，禁止把「未观测」写成「无新闻」。

---

## 5. 适配范围（本轮只写文档）

| 做 | 不做 |
|---|---|
| 落盘本页 + 角色规格 + PIT 对照 | 克隆 TradingAgents 进仓库 |
| 对齐已有 Eng TypedDict / JSONL | 开跑 NAV、冒烟、密封 |
| 定义 AI 辩论 / 记忆结算 IO | 交 Strategy 权重长表 |
| 暂停垃圾事件臂提案 | 启 v27；抬升 promotion |

下一步（另批）：WorkBuddy / 技能 YAML 接线分析师与多空角色 → 写 `DebateTurn` → `make_pending_decision` → 持有窗后 `SettlementRecord`。

---

## 6. 相关路径

- Eng 采纳：`docs/v2/OPENSOURCE_ENG_ADOPTION_ZH.md`
- AI-Native 架构附录 O：`docs/v2/SYSTEM_ARCH_V3_AI_NATIVE_ZH.md`
- 角色规格：`docs/v2/TRADINGAGENTS_ADAPT_ROLES_ZH.md`
- PIT 对照：`docs/v2/TRADINGAGENTS_ADAPT_PIT_ZH.md`
- 代码桩：`quantlab/intel/debate_ledger.py`、`quantlab/intel/asof_window.py`、`quantlab/intel/messages.py`

*研究级。不发明晋级结论。*
