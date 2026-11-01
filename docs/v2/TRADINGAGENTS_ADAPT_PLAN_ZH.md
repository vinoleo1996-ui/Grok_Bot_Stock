# TradingAgents → QuantLab 对接方案（A 股原创）

**日期**：2026-10-12 · America/New_York  
**状态**：研究级 · **`strategy_promotion_approved=false`** · 不自动下单 · 不重启事件臂工厂  
**来源对照**：https://www.zdoc.app/zh/TauricResearch/TradingAgents · 上游 https://github.com/TauricResearch/TradingAgents（`/tmp/TradingAgents` 只读）  
**门锁**：净成本 CAGR **12%–18%** · MDD **不差于 −28%** · 主线个股+ETF · AUM **60万∧100万** · 禁小盘主仓 · 现货无融资（L≤1.0）

---

## 0. 一句话

**抽 TradingAgents 的流程缺口（分析师并行 → 多空辩论 → 交易员提案 → 风控 → PM 拍板 → 决策记忆结算），用 QuantLab 专责与 A 股 PIT 数据重写；禁止整仓粘贴 / Yahoo·Reddit / 美股因子默认栈。**

Leo 已明确：框架**适合** QuantLab。本文不写「不适合」，只写怎么接。

---

## 1. 角色对照（TradingAgents → QuantLab 专责）

| TradingAgents 角色 | 职责摘要 | QuantLab 映射 | 一期是否接线 LLM |
|---|---|---|---|
| 基本面分析师 | 财报/内在价值 | **Data** 供 PIT 表；**AI** 写 brief | stub 文案 |
| 情绪/新闻分析师 | 新闻·宏观·舆情 | **AI** + `quantlab/intel`（已有 `asof_window`） | stub |
| 技术分析师 | 价量指标 | **AI** 对照 brief；**禁止**当主仓唯一依据 | stub |
| 资金/结构（QuantLab 增补） | 北向/两融/席位/解禁等机制 | **Data** 表 + **AI** brief | stub（有表才填 evidence） |
| Bull / Bear 研究员 | 结构化多空辩论 | **AI** | stub |
| Research Manager | 综合辩论出方向 | **AI** | stub |
| Trader | 时机与规模提案 | **AI** → `target_weight_hint`（**非**主书权重） | stub |
| Risk（激进/保守/中性） | 波动·流动性·组合风险 | **Beta**（对照 Mandate 门） | stub 规则句 |
| Portfolio Manager | 批准/拒绝 | **Grok Bot** 整理；**Leo** 最终授权 | stub：`approve_research` ≠ 晋级 |
| Memory settle | 事后相对基准 alpha + 反思 | **Eng/本包** `settle_pending` | **可跑** |
| 模拟交易所成交 | 订单执行 | **不接**一期；主书仍走 `v2_multisleeve_book` / Book-Smoke | 禁 |

> 已有契约桩：`quantlab/intel/debate_ledger.py`（Eng ADAPT）。本包 `quantlab/agents/trading_loop/` 是**可跑状态机 + 结算**，与 ledger 并列，不 vendor LangGraph。

---

## 2. 流程缺口（对照上游，我们缺什么）

| 上游能力 | QuantLab 现状（2026-10-12） | 缺口等级 | 一期动作 |
|---|---|---|---|
| 分析师并行 → 报告齐再辩论 | 专责消息异步，无统一「报告齐」闸 | 高 | 状态机节点 `ANALYSTS_PARALLEL` |
| 多空辩论轮次 | `debate_ledger` 有类型，无驱动循环 | 高 | `DEBATE_BULL_BEAR` |
| Trader 价格锚定/规模 | 无；事件臂只出因子叶 | 高 | `TRADER_PROPOSAL` → hint 写入决策日志 |
| Risk → PM 拍板 | Beta 冒烟 ≠ 决策质检；PM 角色散落 | 高 | `RISK_REVIEW` → `PM_GATE` |
| 决策记忆 + `settle_all_pending`（相对区域基准 alpha） | **无闭环**（仅 TypedDict） | **最高** | 本包 settle vs **510300** |
| 检查点恢复 | 无 LangGraph checkpoint | 中 | 二期；一期 JSONL 追加即可 |
| 网格 backtest 评分记忆 | 与密封 Book-Smoke 分离未定义 | 中 | 二期；一期单决策 settle |
| Yahoo/SEC/Reddit 工具 | 不应搬 | — | **永久拒绝默认栈**；只用仓内 A 股 PIT |

---

## 3. 与主书 / Mandate 边界（硬约束）

1. **决策日志 ≠ 主书 NAV**：settlement 是「这笔研究判断事后怎样」，不改 `DEFAULT_SLEEVES`，不写实盘权重。  
2. **`approve_research` ≠ `strategy_promotion_approved`**：后者恒 `false`，直至 Leo 密封授权。  
3. **基准固定**：A 股主书 alpha 相对 **510300.SH**（与 Mandate 一致）。  
4. **宇宙**：中大盘个股篮 / 宽基·行业·主题 ETF；**禁小盘主仓**。  
5. **杠杆**：现货名义 L≤1.0，无融资；Trader hint 不得暗示融资加仓。  
6. **不重启** V30–V34 事件臂空转工厂；本任务是多智能体研究闭环。

---

## 4. 一期最小可跑路径（已落地骨架）

```
START
  → ANALYSTS_PARALLEL   （4 份 stub brief）
  → DEBATE_BULL_BEAR
  → RESEARCH_MANAGER
  → TRADER_PROPOSAL     （weight hint）
  → RISK_REVIEW         （Mandate 对照句）
  → PM_GATE             （approve_research / reject）
  → LOG_DECISION        （JSONL pending）
  → END
另轨：settle_pending    （持有窗走完 → alpha vs 510300 + reflection）
```

代码：`quantlab/agents/trading_loop/`  
样例日志：`output/trading_loop/decision_log.jsonl`  
规格：`docs/v2/TRADINGAGENTS_MEMORY_SETTLE_SPEC_ZH.md`

### 一行命令

```bash
cd /workspace/QuantLab
python3 -m quantlab.agents.trading_loop.run_stub --session 2024-07-01 --instrument 510500.SH
python3 -m quantlab.agents.trading_loop.settle_pending
```

---

## 5. 二期（不在本次交付）

- 真 LLM 接线（分析师/辩论/PM），provider 可分 quick/deep  
- 把 `intel/debate_ledger` 与本包日志合并或双写  
- 检查点恢复；网格日期回测记忆（独立 log，勿污染主记忆）  
- Trader hint → 可选导出 `date,instrument,target_weight` 供 Book-Smoke **对照袖套**（仍 promotion=false）  
- 舆情/公告 PIT Reader 与 `asof_window` 深度绑定  

---

## 6. 明确不做

- 不 `pip install` 上游包进主依赖；不复制 Yahoo/Reddit/SEC 模块进仓  
- 不改 `strategy_promotion_approved`  
- 不自动向券商/模拟所下单  
- 不把 settled alpha 写成密封 CAGR 过线证据（过线仍走 Book-Smoke + 密封窗）

---

## 与 QuantMind 融合

并行适配与拼管线见 **`docs/v2/TA_QUANTMIND_FUSION_ZH.md`**（辩论结算 × 因子演化权重 × Book-Smoke）。  
QuantMind 计划：`docs/v2/QUANTMIND_ADAPT_PLAN_ZH.md` · 权重 stub：`quantlab/agents/factor_evolve/`。

