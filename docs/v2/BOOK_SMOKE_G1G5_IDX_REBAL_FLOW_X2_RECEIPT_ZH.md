# Book-Smoke 回执：G1G5 **指数调仓迁移流**（`idx_rebal_flow_v1`）**X2 满窗** vs 纯 510300

**run_id**：`book_smoke_20261012_224226`  
**strategy_promotion_approved**：`false`  
**sealed_claim**：`false`（不声称过密封线 / 不交 Strategy / 不下单）  
**promotion_approved**：`false`  
**Mandate**：`docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md`（本跑次**未改** Mandate）  
**角色**：New Bot search-loop 代跑 Book-Smoke（Alpha 已 ACCEPT 权重、声明 PENDING；**≠** QuantLab AI 开工）  
**预注册**：`docs/v2/AI_G1G5_IDX_REBAL_FLOW_WHO_PAYS_PREREG_ZH.md`  
**门锁（研究对照非过关）**：净成本 **CAGR ∈ [12%, 18%]** · **MDD 不差于 −28%**  
**结构正交**：相对六败包活跃个股 Jaccard=0；事件调入强制流；**本满窗未过闸 → 不标备选**。

## 实验设置

| 项 | 值 |
|---|---|
| 权重长表 | `output/ai_factory/g1g5_idx_rebal_flow_daily_weights_20261012_215737.parquet`（**3243** 行 / **668** sessions / **121** 标的） |
| Alpha verify | `output/alpha/AI_G1G5_IDX_REBAL_FLOW_WEIGHT_VERIFY_STATS_20261012.json`（research ACCEPT · handoff locks） |
| mechanism_tag | **`g1g5_ashare_idx_rebal_flow_v1`** |
| who_pays | 指数调仓迁移流：CSI300/500 调入公告后被动跟踪强制再平衡买卖需求支付相对 510300 的持有窗 |
| 明确排除 | 截面相对强弱 / 估值质量 / 解禁席位份额流 / ETF-core 直接持有 / 摩擦四臂换皮 |
| 名义结构 | 稀疏事件：活跃日个股≈0.70 + 510300≈0.30；全日均个股≈0.11 + 压舱≈0.89（~15.4% 活跃日） |
| 袖套消费 | `{"core":0.0,"stock":1.0,"alpha_event":0.0}` |
| 对照 | `C0` = 纯 510300 |
| 窗 | 探索窗 **X2** `2024-06-03→2026-10-09` |
| 资金 | 60万 ∧ 100万 |
| 成本 | 开 |

## 数字表（探索窗满窗；成本开；非密封）

| AUM | arm | CAGR | vs C0 | MDD | Sharpe | cost/AUM | target_weight 行数 |
|---|---|---|---|---|---|---|---|
| 600000 | X2/BOOK | **9.97%** (0.0997) | **−1.29 pp** | **−18.43%** | 0.590 | **0.0079** | 3145 |
| 600000 | X2/C0 | **11.27%** (0.1127) | — | -16.24% | 0.651 | 0.0002 | 570 |
| 1000000 | X2/BOOK | **10.04%** (0.1004) | **−1.23 pp** | **−19.07%** | 0.585 | **0.0087** | 3145 |
| 1000000 | X2/C0 | **11.27%** (0.1127) | — | -16.24% | 0.651 | 0.0002 | 570 |

## 七包对照（同窗 X2；本包第七）

| 臂 | 60万 CAGR/MDD | 100万 CAGR/MDD | any_pass |
|---|---|---|---|
| expand（动量扩池） | 11.37% / −15.15% | 11.42% / −15.88% | false（教科书非主线） |
| lowturn | 10.13% / −17.86% | 10.21% / −17.90% | false |
| **idx_rebal_flow（本包）** | **9.97% / −18.43%** | **10.04% / −19.07%** | **false** |
| nontextbook/friction | 8.24% / −13.95% | 9.61% / −13.02% | false |
| etf_core_sleeve | 8.46% / −20.39% | 9.43% / −20.05% | false |
| friction_cost_redesign | 6.03% / −16.06% | 6.74% / −15.79% | false |
| resid_etf | 5.25% / −14.92% | 5.52% / −14.74% | false |

## 对照门锁

| AUM/arm | CAGR∈[12%,18%] | MDD≥−28% | 过门？ |
|---|---|---|---|
| 60万 BOOK | **否**（9.97% < 12%） | **是**（−18.43%） | **否** |
| 100万 BOOK | **否**（10.04% < 12%） | **是**（−19.07%） | **否** |

C0 ≈11.27% 仍未过 12%。**any_pass=false**。成本低（≈0.8%）但 alpha 不足，相对 C0 ≈−1.2〜−1.3 pp。

## 机制与候选口径

- 事件调入强制流正交声明成立（Jaccard vs 六败=0；稀疏活跃日诚实）。  
- **满窗 any_pass=false** → **不标研究备选**；**不交 Strategy**；`promotion_approved=false`。  
- 代跑 ≠ QuantLab AI 开工。禁再投同构调仓流换皮。

## 工程备注

- 模块：`python3 -m quantlab.portfolio.book_smoke`
- JSON：`output/v3/book_smoke_g1g5_idx_rebal_flow_x2/book_smoke_summary.json`
- NAV：`output/v3/book_smoke_g1g5_idx_rebal_flow_x2/aum_{600000,1000000}/X2/{BOOK,C0}/`
- 可消费 sessions=570；n_codes=121；cost/AUM 低因稀疏换手。

## 结论（诚实）

1. **管线通 + 满窗真跑**：121 码可定价；无 stub。  
2. **门锁未进**：两端 ≈10% CAGR，欠 12% 约 **2.0 pp**；相对 C0 负约 **1.3 pp**。  
3. **七包满窗均败**；expand 仍最近但教科书非主线。  
4. **一句话**：调仓流结构正交、成本低，但探索窗未过门锁、逊于纯 510300——第七包灭，不进备选、不交 Strategy。
