# TradingAgents × QuantMind 融合蓝图（禁止两套平行空转）

**日期**：2026-10-12 · America/New_York  
**状态**：研究级 · **`strategy_promotion_approved=false`** · 不下单  
**门锁**：CAGR **12%–18%** · MDD **−28%** · 60万∧100万 · 个股+ETF · 禁小盘主仓  

---

## 0. 问题陈述

单独学 TradingAgents → 只有「辩论+记忆结算」，**主书权重仍空**（Book-Smoke≈纯 510300）。  
单独学 QuantMind → 只有「因子演化/截面分」，**没有决策质量闭环**，易重回 GP 空转计 N。  

Leo 要求：**两者精髓都融入，且拼成一条管线**，不是两个 stub 各跑各的。

---

## 1. 精髓各取什么

| 来源 | 精髓（保留） | 不搬（拒绝） |
|---|---|---|
| **TradingAgents** | 分析师并行 → 多空辩论 → 交易员提案 → 风控/PM → **事后相对基准 α 结算+反思** | LangGraph 整图 · Yahoo/Reddit · 无现金「回测年化」冒充 NAV |
| **QuantMind** | 假设→演化→**截面打分→Top-N 权重**→组合回测形状；硬闸/预检 | Docker 整仓 · QuantDB 默认包 · Qlib 引擎替换 · 实盘桥默认开 |

---

## 2. 融合管线（一张图）

```
                    ┌─────────────────────────────────────┐
                    │  A 股 PIT 表 (Data) · as_of 守卫      │
                    └──────────────┬──────────────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          ▼                                                 ▼
 ┌─────────────────────┐                         ┌──────────────────────┐
 │ TradingAgents 轨     │                         │ QuantMind 轨          │
 │ trading_loop /       │   机制 tag / 谁付钱      │ factor_evolve /       │
 │ debate_ledger        │ ──────────────────────► │ quantmind_loop        │
 │ 辩论→PM approve_     │   仅 approve 的方向      │ 候选→硬闸→截面分      │
 │ research（≠晋级）    │   可进 evolve 队列       │ → 权重长表 (KPI)      │
 └─────────┬───────────┘                         └──────────┬───────────┘
           │ settle α vs 510300                               │
           │ reflection 回写                                  │ weights.parquet
           │                                                 ▼
           │                                      ┌──────────────────────┐
           └─────────────────────────────────────►│ Book-Smoke / 主书      │
             「哪些机制值得加预算」                 │ --alpha-event-path /  │
                                                  │ --stock-path          │
                                                  │ CAGR/MDD @60∧100万    │
                                                  └──────────────────────┘
```

**单一 KPI 链**：辩论通过的机制 → 演化出 **可消费权重行数** → Book-Smoke 读得动 →（仅 Leo 密封后）才谈门锁。

---

## 3. 怎么拼（契约，防空转）

### 3.1 共享字段

| 字段 | 谁写 | 谁读 |
|---|---|---|
| `mechanism_tag` + `who_pays_zh` | 辩论 Trader/RM **或** Direction | 硬闸必查 |
| `approve_research` | PM_GATE | evolve 队列准入（二期强制；一期 stub 手工） |
| `session,instrument_id,weight` | `factor_evolve` | `WeightLongTableSleeve` / Book-Smoke |
| `settlement.alpha_vs_510300` | `settle_pending` | 反思；**禁止**当成交价；可调 risk 预算叙述 |
| `strategy_promotion_approved` | 恒 false | 全员 |

### 3.2 禁止的平行空转

| 坏模式 | 判定 |
|---|---|
| 只跑辩论 dry-run、不产出权重 | 融合失败 |
| 只跑 GP/ledger N、Book-Smoke 仍 `not_book_consumable` | 融合失败 |
| 两套文档互相不引用 | 融合失败 |
| stub Sharpe / 合成 α 写成过线 | 违规 |

### 3.3 一期接线状态

| 节点 | 状态 |
|---|---|
| `trading_loop` 状态机 + settle | ✅ 已有 |
| `debate_ledger` + AI runner | ✅ 已有 |
| `factor_evolve` 硬闸→权重 | ✅ 本批 stub |
| 辩论 approve → evolve 队列自动入 | ⏭ 二期（先手工 mechanism 白名单） |
| Book-Smoke 挂权重 + 拨 `alpha_event` 预算 | ⏭ 下一步（需 Leo 允探索窗重跑） |
| 密封门锁 | ❌ 未开 |

---

## 4. 角色分工（专责）

| 专责 | 融合中的职责 |
|---|---|
| **AI** | 辩论 brief、候选假设、机制库；写 ledger；**不**自报晋级 |
| **Data** | PIT 面板 / 北向·两融·ETF 份额等到 `available_at` |
| **Beta** | 硬闸对照、Book-Smoke/门禁复核；事件臂工厂保持停 |
| **Eng** | `debate_ledger` / export 契约；执行引擎不变 |
| **Grok Bot** | 拼管线、拒粘贴、向 Leo 报可消费权重与 NAV 缺口 |
| **Strategy** | 未授权不接晋级 |

---

## 5. 验收口令（给巡检）

> 「融合是否活着」=  
> (1) 近 24h 有 `debate_ledger` 或 `trading_loop` settle 非 null α **且**  
> (2) `output/factor_evolve/latest_meta.json` 的 `n_weight_rows>0` **且**  
> (3) 权重列契约可被 `WeightLongTableSleeve` 解析。  
> 缺任一条 → 仍算空转，即使两边各自有回执。

---

## 6. 相关路径

- TradingAgents：`docs/v2/TRADINGAGENTS_ADAPT_*.md` · `quantlab/agents/trading_loop/`  
- QuantMind：`docs/v2/QUANTMIND_ADAPT_PLAN_ZH.md` · `quantlab/agents/factor_evolve/` · `quantlab/factors/ai_factory/quantmind_loop.py`  
- 主书：`quantlab/portfolio/book_smoke.py` · `v2_multisleeve_book.py`  
- 回执：`docs/v2/QUANTMIND_ADAPT_RECEIPT_20261012_ZH.md`  
