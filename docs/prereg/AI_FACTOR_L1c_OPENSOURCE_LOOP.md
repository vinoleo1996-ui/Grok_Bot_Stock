# AI Factor L1c — 开源闭环落地（DRAFT 预注册）

**状态：DRAFT**  
**日期：** 2026-10-11（America/New_York）  
**promotion_approved：** false（全程）  
**对齐：** `/workspace/QuantLab-OPENSOURCE_DEEP_READ_ZH.md` §6–§7.2；`QuantLab-AI_STACK_RETHINK_ZH.md` §6  
**本金口径：** `capital_cny ∈ {600000, 1000000}`（60 万 / 100 万）；更大 AUM 仅附录  

## 1. 机制与范围

把开源深读里 **可搬的工程闭环** 接入 Alpha（不搬教科书模板年化）：

1. **QuantMind 五段式：** preflight → evolve → backtest → explain → export（最小自研，无 AGPL 直链）  
2. **TradingAgents as_of 文本守卫：** 公告/新闻 `available_at ≤ trade_date`；缺覆盖返回 `coverage_gap`  
3. **easy-stock 结构语言：** 连板高度 / 晋级率 / 题材宽度代理 → 非教科书结构叶  

**禁止：** 动量/反转/低波/EP/BP/换手裸表达式作主结果；小盘主线；未批密封窗；把探索过程指标写成晋级。

## 2. 数学 / 管线契约

- 叶白名单 ⊆ `STRUCTURAL_LEAF_FEATURES`（含 L1b + L1c easy-stock 叶）  
- 适应度：扣成本净超额（L1b `fitness_score_l1b`）；与公开因子 `|corr|>0.5` → novelty_fail，不得进主 Top-K  
- 每个候选强制 `mechanism_tag` + `who_pays_zh`（钱从谁来）  
- 账本：`output/ai_factor/ledger.jsonl`（或 run 专用路径）每次尝试计 N  
- 方向词表命中教科书正则 → preflight 失败  

## 3. 可检验预测（探索窗过程指标，非密封）

- 五段闭环在合成面板上可跑通；主 Top-K 无教科书叶  
- as_of 守卫：注入「未来公告」必被拒  
- 60 万 / 100 万写入 run_meta；不把 2 亿/5 亿当主结论  

## 4. 失效条件

- 主 Top-K 再次被教科书叶占据  
- 去掉涨停/连板叶后信号坍塌且无替代结构叶（承接 L1b 消融）  
- 文本叶在探索窗无 `available_at` 覆盖仍强行进 evolve  

## 5. 交付路径

| 组件 | 路径 |
|---|---|
| 五段闭环 | `quantlab/factors/ai_factory/quantmind_loop.py` |
| CLI | `research/quantmind_min_loop.py` |
| as_of 守卫 | `quantlab/factors/ai_factory/asof_text_guard.py` |
| 结构叶 | `quantlab/factors/ai_factory/structural_leaves.py` |
| 方向库 | `docs/v2/ALPHA_DIRECTION_LIB_ZH.md` |
| 状态短报 | `output/alpha/OPENSOURCE_LOOP_STATUS_ZH.md` |

## 6. 密封

**不开密封。** 密封须 Leo 在 Alpha 聊天原话另批。本草案仅研究级骨架 + smoke。

---

## 7. L1c 真实探索窗补记（2026-10-12 ET）

**触发：** Leo 本聊天批准「AI 因子工厂 v1 真实探索窗」后，New Bot 加急 L1c；本块 `promotion_approved=false`，**不开密封**。

### 7.1 主叶 vs 对照叶（预声明）

| 臂 | 叶（白名单） |
|---|---|
| **主结果** | `lu_height`, `mkt_max_height`, `lu_promote_rate`, `mkt_lu_breadth`, `theme_lu_density`；`limit_down_flag`, `ld_streak`, `ld_count_5`, `days_since_ld`；`lockup_S_20`；`ann_n_5` / `ann_buyback_5` / `ann_insider_dec_5` / `ann_penalty_5` / `ann_earn_signed_5`（title 事件计数，title_only，**不编造正文**）；可选结构辅叶 `overnight_ret`, `on_minus_id`, `etf_major_flow`, `etf_theme_flow`, `if_basis`, `if_basis_x_on` |
| **对照臂（不得晋级主 Top-K）** | `days_since_lu`, `lu_streak`, `limit_up_flag`, `lu_count_5`, `etf_flow_x_lu`, `if_basis_x_lu` |
| **禁止主结果** | 动量/反转/低波/EP/BP/换手等教科书叶；小盘主线 |

### 7.2 窗与计次

- 探索窗：`2024-06-03 → latest`；密封窗不碰
- 本块预声明 `max_evaluations ≤ 240`（主搜）+ 对照种子 ≤ 40；账本接续 N（旧累计保留）
- 本金：`capital_cny ∈ {600000, 1000000}`；适应度扣成本净超额；峰值 RSS < 2.5GB

### 7.3 失效 / 报告

- 主 Top-K 被纯涨停叶或教科书叶占据 → 机制失败
- 去掉对照涨停叶后主臂仍可解释 → 记「主臂存活」；否则如实报消融失败
- 交付：`output/alpha/AI_FACTOR_L1c_EXPLORE_ZH.md`；产物 `output/ai_factor/l1c_explore/`
