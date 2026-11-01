# Book-Smoke 回执：G1G5 **降换手**（制度摩擦 lowturn）**X2 满窗日更** vs 纯 510300

**run_id**：`book_smoke_20261012_112547`  
**strategy_promotion_approved**：`false`  
**sealed_claim**：`false`（不声称过密封线 / 不交 Strategy / 不下单）  
**promotion_approved**：`false`  
**Mandate**：`docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md`  
**授权**：Leo 经 New Bot 【立刻|降换手 Book-Smoke】  
**门锁（Leo 2026-10-12，研究对照非过关）**：净成本 **CAGR ∈ [12%, 18%]** · **MDD 不差于 −28%**  
**Leo 纠偏**：过闸可进**研究备选**；本满窗未过闸 → **本跑次不标备选**。

## 实验设置

| 项 | 值 |
|---|---|
| 权重长表 | `output/intel/g1g5_lowturn_daily_weights_20261012_112301.parquet`（**33400** 行 / **668** sessions / **50** 标的） |
| 对照 meta | `output/intel/g1g5_lowturn_run_meta_20261012_112301.json`（`reaches_x2_end=true` · `stub_window=false` · `stub_forward_fill=false`） |
| mechanism_tag | **`g1g5_ashare_inst_friction_v1_lowturn`** |
| 父机制 | `g1g5_ashare_inst_friction_v1`（四臂不变：份额流/解禁/T+1/涨跌停带宽） |
| 降换手改动 | **季末再平衡** + **带宽粘性**（进 top12 / 出 rank>28）；日活跃约 **15.5–16** 只 |
| meta 换手 | mean_one_way **0.0287 → 0.00752**（约 −74%）；`n_rebalance_sessions=13` |
| universe_id | `g1g5_mid_large_liquid_top50` |
| 袖套模式 | **满仓 stock 表**：`{"core":0.0,"stock":1.0,"alpha_event":0.0}` |
| 对照 | `C0` = 纯 510300 |
| 窗 | 探索窗 **X2** `2024-06-03→2026-10-09` |
| 资金 | 60万 ∧ 100万 |
| 成本 | 开（`ExecConfig.strategy_v1`） |
| 可消费 | stock **book_consumable** rows=**10374** / sessions=**570**（X2∩权重日历=整窗） |
| 角色 | 月频制度摩擦满窗失败后的**降换手变体测**；对照=月频摩擦 X2 + 动量 X2 |

## ✅ 满窗日更（无 stub 前推）— 已用数据核验

| 核验项 | 结果 |
|---|---|
| 权重日历 | **2024-01-02→2026-10-09**（668 sessions） |
| meta `reaches_x2_end` | **true** |
| meta `stub_forward_fill` / `stub_window` | **false / false** |
| BOOK `n_signals` | **570**（= X2 可消费 sessions） |
| 唯一组合数（X2） | **12**（2024:4 + 2025:5 + 2026:5；季末节奏，少于月频的 35） |
| 尾段相同组合长度 | **1**（末日才一变，非长尾粘住前推） |
| 日权重合计 | 恒 **1.0**；日活跃约 **15.9** 只（min12/max20） |

→ **禁止**再写「后半持仓前推」。本回执是**真实满窗季末再平衡**结果。

## 数字表（探索窗满窗；成本开；非密封）

| AUM | arm | CAGR | vs C0 | MDD | Sharpe | cost/AUM | target_weight 行数 |
|---|---|---|---|---|---|---|---|
| 600000 | X2/BOOK | **10.13%** (0.1013) | **-1.13 pp** | **-17.86%** | 0.708 | **0.0136** | 9075 |
| 600000 | X2/C0 | **11.27%** (0.1127) | — | -16.24% | 0.651 | 0.0002 | 570 |
| 1000000 | X2/BOOK | **10.21%** (0.1021) | **-1.06 pp** | **-17.90%** | 0.699 | **0.0147** | 9075 |
| 1000000 | X2/C0 | **11.27%** (0.1127) | — | -16.24% | 0.651 | 0.0002 | 570 |

起止：`2024-06-03→2026-10-09`。BOOK `n_codes=48`，`n_signals=**570**`，`gross_mean≈0.89`（60万）/ `≈0.92`（100万），`fill_ratio≈0.99` / `0.99`。

## 三包对照表（同窗 X2 满窗）

| | **本包降换手** | 月频制度摩擦 | 动量扩池 |
|---|---|---|---|
| mechanism | `…_friction_v1_lowturn` | `…_friction_v1` | `…_expand`（截面动量） |
| 再平衡 | 季末+粘性 | 月频 top20 | 月频 top20 |
| 60万 BOOK CAGR/MDD | **10.13% / −17.86%** | 8.24% / −13.95% | 11.37% / −15.15% |
| 100万 BOOK CAGR/MDD | **10.21% / −17.90%** | 9.61% / −13.02% | 11.42% / −15.88% |
| 60万 cost/AUM | **0.0136** | 0.0264 | 0.0284 |
| 100万 cost/AUM | **0.0147** | 0.0283 | 0.0307 |
| vs C0 ΔCAGR（60/100） | **−1.13 / −1.06 pp** | −3.03 / −1.66 pp | +0.11 / +0.15 pp |
| any_pass | **false** | false | false |

回执对照：`docs/v2/BOOK_SMOKE_G1G5_NONTEXTBOOK_X2_RECEIPT_ZH.md` · `docs/v2/BOOK_SMOKE_G1G5_EXPAND_X2_RECEIPT_ZH.md`

### 换手 / 成本是否下降？是否换来门锁？

| 指标 | 月频摩擦 → 本包 lowturn | 解读 |
|---|---|---|
| meta mean_one_way | 0.0287 → **0.00752**（约 −74%） | 权重侧换手声称成立 |
| 60万 cost/AUM | 0.0264 → **0.0136**（约 −48%） | 账本成本**显著下降** |
| 100万 cost/AUM | 0.0283 → **0.0147**（约 −48%） | 同上 |
| 60万 CAGR | 8.24% → **10.13%**（+1.89 pp） | 成本降带来部分修复，仍 <12% |
| 100万 CAGR | 9.61% → **10.21%**（+0.60 pp） | 同上 |
| 门锁 | 两端未过 → **仍未过** | **降换手未换来过闸** |
| vs C0 | 仍两端逊于纯 510300 | 相对基线未翻正 |

诚实结论：**成本目标达到了，门锁目标没有。** CAGR 相对月频摩擦有改善，但仍差 12% 下沿约 **1.8–1.9 pp**，且两端仍低于 C0；相对动量满窗仍低约 **1.2 pp**。

## 对照门锁

| AUM/arm | CAGR∈[12%,18%] | MDD≥−28% | 过门？ |
|---|---|---|---|
| 60万 BOOK | **否**（10.13% < 12%） | **是**（−17.86% ≥ −28%） | **否** |
| 100万 BOOK | **否**（10.21% < 12%） | **是**（−17.90% ≥ −28%） | **否** |

C0 基线仍未过 CAGR 下沿（≈11.27%）。  
**任意 AUM 过门：否（any_pass=false）。** 本结果为研究对照，非过关声称。  
→ **本跑次不标「研究备选」**（过闸才标）。

## vs C0 增量

| AUM | ΔCAGR | ΔMDD |
|---|---|---|
| 60万 | **−1.13 pp**（逊于纯 510300） | −1.62 pp（回撤略深） |
| 100万 | **−1.06 pp**（逊于纯 510300） | −1.66 pp（回撤略深） |

解读：降换手后成本降、CAGR 相对月频摩擦回升，但相对 C0 仍为负；且 MDD 略深于 C0（与月频摩擦「回撤略浅」方向不同——粘性持仓在 2025–2026 段未带来更浅回撤）。

## 机制与候选口径

- 本包仍是**制度摩擦四臂**，非教科书动量；改的是**再平衡频率与带宽粘性**，不是换皮相对强弱。  
- **满窗 any_pass=false** → **不标研究备选**（Leo：过闸才进备选）。  
- 仍 **`promotion_approved=false`** · **不交 Strategy** · **不开密封** · **不下单**。

## 工程备注

- 模块：`python3 -m quantlab.portfolio.book_smoke`
- JSON：`output/v3/book_smoke_g1g5_lowturn_x2/book_smoke_summary.json`  
  （含 `experiment` / `weight_coverage_caveat.full_x2_daily=true` / `mandate_door` / `vs_baseline_C0` / `vs_friction_monthly_x2` / `vs_momentum_x2` / `turnover_note` / `mechanism_note`）
- NAV：`output/v3/book_smoke_g1g5_lowturn_x2/aum_{600000,1000000}/X2/{BOOK,C0}/`
- promotion=false；不下单；不交 Strategy；不开密封。

## 结论（诚实）

1. **管线通 + 满窗真日更**：668 sessions 至 2026-10-09；`n_signals=570`；唯一组合 12（季末节奏）；尾长 1；**已证伪 stub 前推**。  
2. **换手/成本**：meta 换手约 −74%；账本 cost/AUM 约 **−48%**（0.026–0.028 → **0.014–0.015**）——降换手工程目标达成。  
3. **相对月频摩擦**：CAGR 回升约 +0.6～+1.9 pp，仍两端 <12%。  
4. **相对基线 C0**：两端仍约 **−1.1 pp**；MDD 略深。  
5. **相对动量满窗**：仍低约 **1.2 pp**；三包满窗 **均 any_pass=false**。  
6. **研究门锁**：**any_pass=false** → **不标备选**；`promotion=false`；不交 Strategy。  
7. **一句话**：成本下来了，门锁没进来——降换手是必要但不够。
