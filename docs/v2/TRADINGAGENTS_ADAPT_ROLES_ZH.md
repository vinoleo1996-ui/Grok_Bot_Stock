# TradingAgents 适配：AI 角色规格（辩论 + 记忆结算）

**角色**：AI · 研究级 · `promotion_approved=false` · `strategy_promotion_approved=false`  
**日期**：2026-10-12 · America/New_York  
**对齐代码**：`quantlab/intel/debate_ledger.py`（Eng 契约桩；本规格消费之，不平行发明第二套 schema）  
**总览**：`docs/v2/TRADINGAGENTS_ADAPT_OVERVIEW_ZH.md`

---

## 0. 目标流（研究级）

```
Data/Alpha 契约报告（PIT）
  → 分析师角色产出结构化要点
  → 多空辩论（Bull / Bear）
  → 研究经理合成 → 待定 DecisionEntry（pending）
  → 持有窗结束后 SettlementRecord（原始收益 + 相对基准 alpha + 反思）
  → 下次辩论可读历史 settlement / reflection
```

**硬边界**：上述链路 **不直接下单**；不写 Strategy 权重长表；不抬升 promotion。

---

## 1. 分析师辩论 — 输入

| 字段 | 类型 | 来源 | 规则 |
|---|---|---|---|
| `session` | `YYYY-MM-DD` | 调仓/决策日历日 | 与账本一致 |
| `instrument` | str | 标的 | QuantLab 记号；禁止虚构未在宇宙内的代码 |
| `asof_decision_ts` | datetime/str | 决策时刻 | 默认对齐 `asof_window.session_to_decision_ts`（18:00） |
| `analyst_briefs` | list | 分析师输出 | 见下角角色；须带 `evidence_refs` |
| `alpha_report_refs` | list[str] | Alpha/Data 契约报告路径或 id | **只引用已存在产物**；禁止声称「已晋级/密封通过」 |
| `prior_settlements` | list | `JsonlDebateLedger` 历史 | 同标的优先；可截断最近 K 条 |
| `coverage_gaps` | list[str] | intel readers attrs | 有缺口必须露出，不得默认为空消息 |

### 1.1 分析师角（提示词职责，非下单）

| 角色（ledger `DebateRole`） | 消费 | 禁止 |
|---|---|---|
| `analyst_news` | `intel.messages` 公告/新闻 PIT | Yahoo/美股新闻主源 |
| `analyst_sentiment` | 本地舆情 PIT（S1 契约）或消息极性 | Reddit/StockTwits 作 A 股主源 |
| `analyst_market` | 本地 OHLCV / 量价特征（Data readers） | 盘中偷看未到 `available_at` 的数据 |
| （基本面要点） | 财务 PIT / EP 等已落盘表 | 把教材因子当「晋级 Alpha」叙事 |

技术/基本面若无独立 `DebateRole` 字面量，归入 `analyst_market` 或 `other`，并在 `thesis_zh` 标明子类——**勿擅自扩展 Eng Literal 除非 Eng 改桩**。

---

## 2. 分析师辩论 — 输出 schema

与 Eng TypedDict 对齐（字段名勿改）：

### 2.1 `DebateTurn`

```text
turn_id: str
role: analyst_* | bull | bear | research_manager | risk | portfolio_manager | other
session: YYYY-MM-DD
instrument: str
thesis_zh: str                 # 中文论点；短可证伪
evidence_refs: list[str]       # message_id / content_hash / 报告路径
asof_decision_ts: str
promotion_approved: false      # 恒 false
```

### 2.2 多空结构化辩论包（一轮）

```text
DebateRoundResult:
  session, instrument
  turns: [分析师…] + [bull] + [bear] + [research_manager 可选]
  decision: DecisionEntry | null
  promotion_approved: false
```

**Bull / Bear 约束**：

- 必须引用至少一条 `evidence_refs`；无证据 → `Abstain` 路径，不硬编故事。
- 不得互相覆写对方 `turn_id`；经理合成另开 turn。
- 输出评级只进 `DecisionEntry.rating`，取值：`Buy|Overweight|Hold|Underweight|Sell|Abstain`。

### 2.3 `DecisionEntry`（待结算）

```text
decision_id: str
session, instrument
rating: RatingLabel
rationale_zh: str
debate_turn_ids: list[str]
status: "pending"              # 初值为 pending
asof_decision_ts: str
promotion_approved: false
```

工厂：`make_pending_decision(...)`（已实现）。

---

## 3. 记忆结算

### 3.1 路径

| 项 | 路径 |
|---|---|
| 主账本 | `output/intel/debate_ledger.jsonl`（`JsonlDebateLedger` 默认） |
| 目录 | 首次写入时由 store `mkdir`；当前可能尚不存在属正常 |
| 并列账本 | `research_signal_ledger`（信号捕获证据）— **不合并**；辩论质量 ≠ 信号证据链 |

### 3.2 `SettlementRecord`

```text
decision_id: str               # 对应 pending decision
session, instrument
horizon_days: int              # 持有窗；预注册时写死，禁止事后改窗刷分
benchmark: str                 # 建议 510300 或沪深300；与 Mandate 基准一致
raw_return: float | null       # 标的持有窗原始收益
alpha_vs_benchmark: float | null
reflection_zh: str             # 中文反思：对/错因、证据是否 PIT、下次可复用要点
settled_at: str
promotion_approved: false
```

### 3.3 结算规则

1. 仅处理 `status=pending` 且持有窗已结束的决策。  
2. 收益与 alpha **研究观察**；禁止写成 Strategy NAV / 密封通过。  
3. 结算后下次辩论经 ledger 读取 reflection；覆盖缺口与错误归因须保留。  
4. 收益计算具体 reader / 复权口径 — **待 Eng/Data 定**统一 helper；AI 不私自发明第二套收益引擎。

---

## 4. 与 Beta / Strategy 交接边界

| 方向 | 允许 | 禁止 |
|---|---|---|
| → Beta | 另批预注册后，settled rating 作 **风险预算/仓位调节特征** | 当成交价、当主 Alpha、当事件臂替代 |
| → Strategy | **无**（本阶段）；权重长表须另批 + Mandate 契约 | 辩论直接写 `--stock-path` / 交主书 |
| → Alpha | 反思可反馈「证据类型是否值得挖因子」 | 用辩论 rating 伪造 `validate_gate` / 密封 |
| promotion | 全部研究输出 `false` | `promotion_approved=true` 或不带 `strategy_` 前缀的暧昧 true |

**不交 Strategy**，直至 New Bot / Leo 另批。

---

## 5. 禁项（执行清单）

- 照搬 Yahoo / StockTwits / Reddit 作 A 股主源  
- 可转债 / 黄金作本适配主线  
- 已拒事件臂垃圾提案同构（seat / 解禁 / tercile / 分红 DY / ocf 质量教材主攻 / 披露日历无增量等）  
- 启 v27；开 NAV/冒烟「证明」辩论有效  
- vendor TradingAgents 整仓进专有树  
- 把 settlement 年化冒充 Strategy 晋级  

---

## 6. AI 落地顺序（文档后，另批执行）

1. WorkBuddy / 技能：分析师 + Bull/Bear 提示词，只读 PIT readers。  
2. 写 `DebateTurn` → `append_turns` → `make_pending_decision` → `append_decision`。  
3. 批处理：扫描 pending → 填 `SettlementRecord` → `append_settlement`。  
4. 只读 API 供下次辩论注入 `prior_settlements`。  
5. 全程 `promotion_approved=false`；控峰内存约定沿用 New Bot（≤2GB 研究峰）。

*研究级。辩论与记忆是决策质量闭环，不是下单系统。*
