# QuantMind → QuantLab 适配计划（抽流程 · 禁傻粘贴）

**日期**：2026-10-12 · America/New_York  
**状态**：研究级 · **`strategy_promotion_approved=false`** · 不下单 · 不开密封  
**上游只读**：https://github.com/qusong0627/QuantMind（`/tmp/QuantMind`）· AGPL — **不 vendor 进专有仓**  
**门锁**：净成本 CAGR **12%–18%** · MDD **不差于 −28%** · AUM **60万∧100万** · 主线个股+ETF · 禁小盘主仓 · 禁 Yahoo/Reddit 作主数据  
**已有仓内胚**：`quantlab/factors/ai_factory/quantmind_loop.py` · `rdagent_min_loop.py` · `research/quantmind_min_loop.py` · L1c 预注册

---

## 0. 一句话

**抽 QuantMind 的「假设→演化→截面打分→组合回测→模拟盘」闭环形状，用 QuantLab PIT 表 + 硬闸 + Book-Smoke 权重长表重写；禁止 Docker 整仓、QuantDB 默认特征包、Alpha158 教科书模板当主结果。**

---

## 1. 模块对照（QuantMind → QuantLab）

| QuantMind 模块 | 上游职责 | QuantLab 映射 | 一期决策 |
|---|---|---|---|
| QuantDB / 300+ 维预计算特征 | 数据底座 | **Data** `data/v2/**` PIT parquet | **ADAPT 契约**；不绑 QuantDB Key |
| RD-Agent AutoAlpha | LLM 假设→公式→遗传演化 | `ai_factory/rdagent_min_loop` + **`agents/factor_evolve`** | **ADAPT 最小 stub**（本批） |
| 13 种模型工场 / Stacking | 训练·推理 | 二期；一期截面分数可由规则/既有 GP 叶供给 | **延后** |
| 批量截面推理 Top-N | 全日打分→推荐 | `weights_from_scores` → 权重长表 | **一期必做** |
| 微软 Qlib 回测 | TopkDropout 等 | **拒绝换引擎**；主书仍 `v2_multisleeve_book` / Book-Smoke | **REJECT 引擎替换** |
| RSS / FinBERT 舆情 | 情绪流 | `intel/asof_window` + 辩论 brief | **ADAPT PIT 守卫**；拒无 as_of |
| Strategy Lab / 工作台 | UI·模板 | WorkBuddy / 文档；不搬 Electron | **REJECT UI 粘贴** |
| 本地模拟盘 T+1 | 撮合·费用 | 现有 `platform/execution`；**不下单** | 研究级对照；实盘桥禁 |
| QuantBot IM 远程 | 微信/飞书指令 | 专责消息总线（已有） | 形状可学；不绑 IM |
| 通达信/实盘桥 | 下单 | **永久拒绝默认启用** | **REJECT** |

---

## 2. 流程缺口（相对 QuantMind 精髓，我们缺什么）

| 精髓能力 | 仓内现状（2026-10-12） | 缺口 | 一期动作 |
|---|---|---|---|
| 假设带「谁付钱」再演化 | L1c / Direction 有；事件臂工厂已停 | 中 | stub 强制 `who_pays_zh` |
| 演化产物 = **可消费权重** | GP/ledger 计 N；Book-Smoke 权重槽空 | **最高** | `factor_evolve` KPI=`n_weight_rows` |
| 截面 Top-N → 组合 | 有 panel 叶，无统一 export→sleeve | 高 | `scores_to_long_table` |
| 硬闸（教科书/小盘/本金） | novelty + validate_gate 散落 | 高 | `hard_gates.py` 统一入口 |
| 生产 RankIC 回填 | 无 | 中 | 二期；一期用 TradingAgents settle α 对照 |
| 模拟盘/工作台 | Book-Smoke 基线≈11.3%@纯510300 | 中 | 权重接上后再跑 Book-Smoke |
| 检查点恢复 | 目录约定 | 低 | JSON meta 即可 |

---

## 3. 与既有 `quantmind_loop` 分工（避免两套空转）

| 层 | 路径 | 产出 | 不做什么 |
|---|---|---|---|
| 研究五段式（已有） | `factors/ai_factory/quantmind_loop.py` | expr Top-K · ledger N · explain | **不直接改主书** |
| **权重出口（本批）** | `agents/factor_evolve/` | `session,instrument_id,weight` parquet | 不算密封年化 |
| 主书消费 | `portfolio/book_smoke.py --stock-path/--alpha-event-path` | NAV@60∧100万 | 晋级仍 false |
| 决策质量 | `agents/trading_loop/` + `intel/debate_ledger` | 相对 510300 α | ≠ 现金账本 |

**融合见** `docs/v2/TA_QUANTMIND_FUSION_ZH.md`。

---

## 4. 一期路径（已落地 / 下一步）

1. ✅ 对照文档（本文）  
2. ✅ `quantlab/agents/factor_evolve` stub：候选→硬闸→权重长表  
3. ⏭ 真实面板：Data 供给中大盘/ETF score panel 后，替换 `_synth_candidates`  
4. ⏭ Book-Smoke：`--alpha-event-path output/factor_evolve/latest_weights` + sleeves 拨预算  
5. ⏭ 辩论门控：仅 `approve_research` 的机制 tag 可进 evolve 队列（融合蓝图）  
6. ❌ 不：vendor RD-Agent、不启 QuantMind Docker、不写实盘桥、不开密封  

---

## 5. 永久拒绝清单

- Yahoo / Reddit / 美股默认工具链作主数据  
- Alpha158 / 动量·反转·低波·EP/BP 作主 Top-K  
- 小盘 / 微盘 / 北交所作主仓宇宙  
- 把 GP 尝试次数或 stub Sharpe 写成密封过线  
- AGPL 源码拷进专有树  

---

## 6. 验收（一期）

- [x] stub `--smoke` 退出 0，且 `n_weight_rows > 0`  
- [x] 教科书/小盘/无分数候选 `verdict=fail`  
- [x] meta 含 `strategy_promotion_approved=false` · `capital_cny ∈ {6e5,1e6}`  
- [ ] （下一步）Book-Smoke 读入权重后 `consumable.alpha_event.status=book_consumable`  
