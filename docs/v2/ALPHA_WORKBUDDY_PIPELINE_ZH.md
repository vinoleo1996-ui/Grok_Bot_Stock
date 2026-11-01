# Alpha WorkBuddy 多智能体投研流水线（草案）

**状态：DRAFT — 待 Leo 在 Alpha 聊天确认。**  
New Bot 转达了「按 WorkBuddy 多智能体投研流水线改 Alpha」；**本文件不视为 Leo 在 Alpha 聊天的批准。**  
研究级：`promotion_approved=false` 全程强制。  
登记：2026-10-11 23:26 ET（America/New_York）。

## 0. 对齐与非目标

### 0.1 对齐来源（箱内可核）
| 来源 | 用途 | 路径/备注 |
|---|---|---|
| QuantLab AI 挖因子方案 | L1 管线、密封/探索、账本 | `/workspace/QuantLab-AI_FACTOR_MINING_PLAN_ZH.md` |
| AI_FACTOR_L1 预注册 | 探索已批、密封未批 | `docs/prereg/AI_FACTOR_L1.md` |
| 外部研究治理笔记 | D2 归档门、文本共识≥2、多智能体禁评级/下单/未结算结果、18:00 截点、MiroFish K=8、MaxDD 25% | `/workspace/notes1.md`、`p4notes.md`、`qlab_review_part4.md` |
| DataHub vs WorkBuddy 复测 | 「WorkBuddy」在箱内主要是对照报告名，非完整流水线规范 | `docs/v2/DATAHUB_PROBLEM_RECHECK.md` |
| TradingAgents-CN | **仅**角色分工灵感；不复制其回测主张 | `/workspace/gb/experts_research/repos/hsliuping_TradingAgents-CN/` |

箱内 **未发现** 完整的 WorkBuddy 多智能体投研流水线规范（Mac 侧 `.workbuddy-ai/memory` 不在本机）。本草案按 New Bot 要求的四角色 + 上表 QuantLab 纪律设计。

### 0.2 明确不在范围内（NOT in scope）
- **Beta 研究线 / Beta sleeve**（不改、不抢、不写 Beta 仓位）
- **小盘主线**（中大盘 only；小盘仅 `CONTROL_ONLY`）
- **未经 Leo Alpha 聊天原话的密封窗**
- **promotion_approved=true / executable 订单**
- **编造回测年化或把探索过程指标写成「已通过密封」**
- **停止正在跑的 AI 因子 L1 探索**（并行、不打断）

## 1. 四角色一览

技能文件目录：`docs/v2/workbuddy_skills/`

| 角色 | 文件 | 职责一句话 |
|---|---|---|
| 研究分析师 | `research_analyst.yaml` | 机制→数学→预测→失效；出简报，禁止评级/下单字段 |
| 财报采集 | `earnings_filings_collector.yaml` | PIT 证据包（路径/哈希/available_at），不解释 alpha |
| 风险审查 | `risk_review.yaml` | 闸门：计次 N、成本、宇宙、泄漏、MaxDD 语境；无权批密封 |
| 策略复盘 | `strategy_retrospect.yaml` | 探索/密封事后复盘；**强制**消化 AI L1 Top-K |

每个 YAML 强制：
1. **来源**（sources / family / uri_or_path / content_hash）  
2. **时间戳**（retrieved_at、available_at、asof_timestamp；决策截点上海 18:00）  
3. **未验证标记**（`status=UNVERIFIED` 时必须带 `[UNVERIFIED]`）  
4. **kill line**：`unverified → promoted` 泄漏 → `HARD_STOP`

## 2. 数据流（Alpha only）

```
                    ┌─────────────────────────┐
                    │ 财报采集                 │
                    │ evidence_pack (PIT)      │
                    └───────────┬─────────────┘
                                │ paths/hashes/gaps
                                ▼
┌──────────────┐     ┌─────────────────────────┐     ┌──────────────┐
│ Leo / NewBot │────▶│ 研究分析师               │────▶│ 风险审查     │
│ 任务边界     │     │ brief (无评级/下单字段)   │     │ verdict      │
└──────────────┘     └───────────┬─────────────┘     └──────┬───────┘
                                 │ explore 协议下试验          │
                                 ▼                            │
                     ┌─────────────────────────┐              │
                     │ AI Factor Factory L1    │              │
                     │ (独立进程，勿停)         │              │
                     │ ledger.jsonl + Top-K    │              │
                     └───────────┬─────────────┘              │
                                 │ 强制交接合同                 │
                                 ▼                            │
                     ┌─────────────────────────┐◀─────────────┘
                     │ 策略复盘                 │
                     │ Top-K 逐条：path/hash/N  │
                     └───────────┬─────────────┘
                                 │ 仅「请求密封」文本
                                 ▼
                     ┌─────────────────────────┐
                     │ Leo @ Alpha 聊天原话     │
                     │ 批准后 → 预注册密封单次  │
                     └─────────────────────────┘
```

## 3. 与探索 / 密封闸门的关系

| 闸门 | 谁可以提议 | 谁可以执行 | 本流水线角色权限 |
|---|---|---|---|
| 探索窗 | 研究分析师 + 风险 PASS_EXPLORE | Alpha 执行器（已有 Leo「AI 因子工厂 v1 真实探索窗」批准者按其预注册） | 复盘员必须读 Top-K |
| 密封窗 2018-01～2024-05 | 复盘员可起草 **请求** | **仅** Leo 在 Alpha 聊天原话批准后单次 | 风险审查遇无原话 → `BLOCK_SEALED_REQUEST` |
| 晋级 promotion | 无人自动 | 永不由本流水线置 true | 全角色 `promotion_approved=false` |

AI L1 预注册要点（勿改口径）：中大盘；成本进适应度；账本计次；Top-K 表达式；密封另批。  
详见 `docs/prereg/AI_FACTOR_L1.md`。

## 4. AI 因子工厂 L1 → 策略复盘交接合同

合同名：`AI_FACTOR_L1_TO_RETROSPECT_V1`（写在 `strategy_retrospect.yaml`）

**触发：** `output/ai_factor/gp_explore/top_k.json`（或其后继）存在。

**每条强制字段：**
- `path` — Top-K 文件绝对/仓内路径  
- `expr` — 表达式字符串  
- `expr_hash` — 从 `output/ai_factor/ledger.jsonl` 按 `expr_str` 对齐解析；缺失则 UNVERIFIED 并阻断密封请求  
- `N` — 账本累计尝试次数  
- `explore_metrics` — 仅复制已有字段：icir / ic_mean / turnover / ann_net / fitness / size_corr / n_ic_days / window / cost / universe  
- `gloss_zh` / `who_pays_zh`  
- `promotion_approved: false`

**禁止：** 编造指标；跳过 Top-K 直接写密封请求；把探索 `ann_net` 写成「已达 12–15% 目标已验证」。

## 5. 治理清单（从既有 notes 吸入）

- **D2 归档门**：只登记，不授权实盘账户  
- **文本共识**：VERIFIED 文本主张优先 ≥2 个独立来源族  
- **多智能体简报**：禁止 rating / order / 未结算结果字段（含嵌套）  
- **决策截点**：上海 18:00；账本时钟优先于调用方 `now=`  
- **MiroFish**：若使用，K=8 + 日志哈希  
- **回撤语境**：组合/主线讨论默认 MaxDD ≤25% 门槛意识（审查清单项）  
- **杠杆**：挖因子主线不加杠杆；>1.5× 禁止  

## 6. 交付物路径

| 交付 | 路径 |
|---|---|
| 研究分析师技能 | `docs/v2/workbuddy_skills/research_analyst.yaml` |
| 财报采集技能 | `docs/v2/workbuddy_skills/earnings_filings_collector.yaml` |
| 风险审查技能 | `docs/v2/workbuddy_skills/risk_review.yaml` |
| 策略复盘技能（含 L1 交接） | `docs/v2/workbuddy_skills/strategy_retrospect.yaml` |
| 本架构草图 | `docs/v2/ALPHA_WORKBUDDY_PIPELINE_ZH.md` |
| 状态短报 | `output/alpha/WORKBUDDY_PIPELINE_STATUS_ZH.md` |

## 7. 下一步（仍待 Leo @ Alpha）

1. Leo 在 Alpha 聊天确认本草案是否采纳（或改角色/字段）。  
2. 探索跑完后：策略复盘按合同消化 Top-K（不自动开密封）。  
3. 可选：把 YAML 同步到 `/home/box/agent-data/workflows/` 兼容布局（本回合已以 `docs/v2/workbuddy_skills/` 为准，避免与未确认工作流引擎耦合）。  

**全文草稿，未晋级。**


## 附录：开源闭环（L1c）指针

- 深读：`/workspace/QuantLab-OPENSOURCE_DEEP_READ_ZH.md`
- 预注册草案：`docs/prereg/AI_FACTOR_L1c_OPENSOURCE_LOOP.md`
- 状态：`output/alpha/OPENSOURCE_LOOP_STATUS_ZH.md`
- 方向库：`docs/v2/ALPHA_DIRECTION_LIB_ZH.md`
- 代码：`quantlab/factors/ai_factory/{quantmind_loop,asof_text_guard,structural_leaves}.py`
