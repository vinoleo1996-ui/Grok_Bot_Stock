# 开源对照：Eng 采纳评估（TradingAgents / QuantMind）

**角色**：Eng（平台）· 研究级 · `promotion_approved=false`  
**日期**：2026-10-11（ET）  
**依据**：`/workspace/QuantLab-OPENSOURCE_DEEP_READ_ZH.md` §7.1 Eng（E1–E4）及 §1 / §4  
**备份**：`/tmp/oss_eng_bak/`

---

## 1. §7 Eng 任务结论

| ID | 任务 | 决策 | 本周交付 |
|---|---|---|---|
| **E1** | `asof_window` 文本/舆情 Reader 守卫 | **ADAPT（必做）** | `quantlab/intel/asof_window.py` + messages/embeddings 接线 + 单测 |
| **E2** | 因子演化状态机 evolve/poll/backtest/explain/export | **ADAPT（契约桩）** | `quantlab/factors/ai_factory/pipeline_export.py`；完整 CLI 留给 Alpha |
| **E3** | AUM 档 `capital_cny ∈ {6e5,1e6}` 写入 NAV 元数据 | **ADAPT（延后）** | export 记录已收 `capital_cny`；账本 schema 改动等 Strategy 对齐，本周不改引擎 NAV |
| **E4** | 阶段检查点可恢复 | **REJECT-as-Eng-owner** | 目录约定属 Alpha/WorkBuddy 产物布局；Eng 不占用 |

---

## 2. TradingAgents：辩论账本接口

### 2.1 含义（若接入 Eng）

TradingAgents 提供：

1. **PIT `date_window`**（as_of / in_window / coverage_gap / withhold live）  
2. **多角色辩论图**（Bull/Bear → Research Manager → Risk → PM）  
3. **决策 memory log + 事后 settlement**（相对基准 alpha；**明确不做组合现金账本**）

对 QuantLab：

| 层 | Eng 该做什么 | Alpha/Beta 该做什么 |
|---|---|---|
| 接口 | TypedDict/Protocol：`DebateTurn` / `DecisionEntry` / `SettlementRecord` + JSONL store | 角色提示词、谁发言、何时触发 |
| 存储 | `output/intel/debate_ledger.jsonl`（研究级） | 读 pending / 写 reflection 文本 |
| promotion_gate | 恒 `false`；settlement ≠ 晋级 | 密封仍走 `validate_gate` + Leo 原话 |
| 消费 | 只提供读取 API | Alpha：每日情报/WorkBuddy；Beta：**可选**把 settled rating 当风险预算特征，**禁止**当成交价 |

### 2.2 决策：**ADAPT**（拒绝整仓 LangGraph / 美股工具链）

**Adopt 的部分：** E1 PIT 纪律；决策质量 settlement 与「非现金账本」边界。  
**Reject 的部分：** Yahoo/Reddit 默认栈；无现金账本的「回测年化」冒充 Strategy NAV；Trading-R1（无代码）。  
**不 vendor** TradingAgents 源码进专有仓；对照重写小模块即可。

### 2.3 最小 Eng 契约（已落桩）

- `quantlab/intel/debate_ledger.py`：`DebateTurn` / `DecisionEntry` / `SettlementRecord` / `JsonlDebateLedger` / `make_pending_decision`  
- 与现有 `research_signal_ledger.py`（前向捕获证据）**并列**，不合并：前者是 LLM 辩论决策质量，后者是信号捕获证据链。

---

## 3. QuantMind：export 契约

### 3.1 含义

`factor_pipeline.py` 五段式：

```
preflight → evolve → poll → backtest → explain → export(|IC|≥min)
```

HTTP 容器 + Qlib + 默认 Alpha158/动量模板 **不**进入 Eng 运行时。

### 3.2 决策：**ADAPT**（契约 + dry_run；拒绝默认策略模板 / AGPL 整仓链入）

| QuantMind | QuantLab 映射 |
|---|---|
| evolve | `ai_factory.rdagent_min_loop` |
| backtest/IC | `evaluate` / `fitness`（Alpha 实现） |
| explain | export 记录的 `explain_zh`（Alpha LLM） |
| export | `pipeline_export.dry_run_export` → `FactorExportRecord` |
| Top-K / AUM | 字段 `capital_cny`；宇宙白名单；教科书方向拒收 |

### 3.3 最小 Eng 契约（已落桩）

- `quantlab/factors/ai_factory/pipeline_export.py`  
- 拒收方向词：反转/动量/低波…；`mechanism_tag` 必填；`promotion_approved` 永不 True；`window=sealed` 直接拦。

---

## 4. as_of 文本守卫（E1）如何工作

```
caller(trade_session / decision_ts)
  → as_of_window 钳制 [start,end]
  → load parquet
  → filter_frame_asof: available_at ≤ decision_ts（默认 session 18:00）
  → 缺覆盖：attrs['coverage_gap'] = "<source unavailable ... not an absence>"
  → strict_asof=True：未来行直接 ValueError(pit_lookahead)
```

- 入口：`quantlab/intel/asof_window.py`  
- 接线：`messages.load_message_frame(..., trade_session=, decision_ts=, strict_asof=)`  
  `embeddings.load_embedding_panels(..., trade_session=, ...)`  
- 完成定义：回测日注入「未来公告」→ 过滤掉；`strict_asof` → 必失败（单测覆盖）。

---

## 5. New Bot / Alpha 下一步

1. **Alpha**：用 `load_message_frame(trade_session=...)` / `load_messages_for_session` 替换裸读公告；工厂进化循环对接 `dry_run_export`；辩论角色落 WorkBuddy Skills，写 `JsonlDebateLedger`。  
2. **New Bot**：确认 E3（AUM 元数据进 NAV）是否本周要 Eng 改 ledger schema；E4 检查点目录交给 Alpha。  
3. **Data**：继续 `intel_message_corpus` / `embedding_store_daily` ENG_PING 键；公告 embedding 语料 PIT。  
4. **Beta**：勿把 TradingAgents rating 当主 Alpha；若用 settled rating，仅作仓位调节器预注册。

---

## 6. 文件清单

| 路径 | 动作 |
|---|---|
| `quantlab/intel/asof_window.py` | 新增 |
| `quantlab/intel/debate_ledger.py` | 新增 |
| `quantlab/intel/messages.py` | 接线 as_of |
| `quantlab/intel/embeddings.py` | 接线 as_of |
| `quantlab/intel/__init__.py` | 导出 |
| `quantlab/factors/ai_factory/pipeline_export.py` | 新增 |
| `quantlab/factors/ai_factory/__init__.py` | 导出 |
| `tests/test_intel_asof_window.py` | 新增 |
| `docs/v2/OPENSOURCE_ENG_ADOPTION_ZH.md` | 本文件 |
| `docs/v2/SYSTEM_ARCH_V3_AI_NATIVE_ZH.md` | 追加开源采纳小节 |
