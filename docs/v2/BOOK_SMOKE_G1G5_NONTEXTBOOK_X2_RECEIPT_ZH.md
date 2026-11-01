# Book-Smoke 回执：G1G5 非教科书（制度摩擦）**X2 满窗日更** vs 纯 510300

**run_id**：`book_smoke_20261012_111723`  
**strategy_promotion_approved**：`false`  
**sealed_claim**：`false`（不声称过密封线 / 不交 Strategy / 不下单）  
**promotion_approved**：`false`  
**Mandate**：`docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md`  
**授权**：Leo 经 New Bot 【立刻|双包 X2 满窗 Book-Smoke】（本条=主攻包）  
**门锁（Leo 2026-10-12，研究对照非过关）**：净成本 **CAGR ∈ [12%, 18%]** · **MDD 不差于 −28%**

## 实验设置

| 项 | 值 |
|---|---|
| 权重长表 | `output/intel/g1g5_nontextbook_daily_weights_20261012_111316.parquet`（**33400** 行 / **668** sessions / **50** 标的） |
| 对照 meta | `output/intel/g1g5_nontextbook_run_meta_20261012_111316.json`（`reaches_x2_end=true` · `stub_window=false` · `stub_forward_fill=false`） |
| mechanism_tag | **`g1g5_ashare_inst_friction_v1`** |
| universe_id | `g1g5_mid_large_liquid_top50` |
| 四臂（名义） | ETF份额流 **0.40** + 解禁残差 **0.25** + T+1抛压 **0.20** + 涨跌停带宽 **0.15** → top20 等权 |
| 明确排除 | 教科书相对强弱 / 估值排序 / `excess_20d vs 510300` |
| 袖套模式 | **满仓 stock 表**：`{"core":0.0,"stock":1.0,"alpha_event":0.0}` |
| 对照 | `C0` = 纯 510300 |
| 窗 | 探索窗 **X2** `2024-06-03→2026-10-09` |
| 资金 | 60万 ∧ 100万 |
| 成本 | 开（`ExecConfig.strategy_v1`） |
| 可消费 | stock **book_consumable** rows=**13360** / sessions=**570**（X2∩权重日历=整窗） |
| 角色 | **主攻机制测**；动量扩池包为同窗对照（见双包摘要） |

## ✅ 满窗日更（无 stub 前推）— 已用数据核验

| 核验项 | 结果 |
|---|---|
| 权重日历 | **2024-01-02→2026-10-09**（668 sessions） |
| meta `reaches_x2_end` | **true** |
| meta `stub_forward_fill` / `stub_window` | **false / false** |
| BOOK `n_signals` | **570**（= X2 可消费 sessions，非整窗前推） |
| 唯一组合数 | **35**（2024 年 13 + **2025+ 23**） |
| 尾段相同组合长度 | **1**（末日才一变，非长尾粘住） |
| 日权重合计 | 恒 **1.0**；日活跃约 20 只 |

→ **禁止**再写「后半持仓前推」。本回执是**真实满窗月频再平衡**结果。半窗旧回执 `docs/v2/BOOK_SMOKE_G1G5_NONTEXTBOOK_RECEIPT_ZH.md` 因日历止于 2024-12-31 含前推，**数字不可外推、仅作对照**。

## 与半窗旧回执并列表

半窗 run：`book_smoke_20261012_110436` · 权重止于 2024-12-31 · consumable sessions=144 + 持仓前推 · any_pass=**true**（仅 100万）。

| AUM | 半窗 BOOK CAGR/MDD | **满窗** BOOK CAGR/MDD | ΔCAGR |
|---|---|---|---|
| 60万 | 11.08% / -14.33% | **8.24% / -13.95%** | **-2.84 pp** |
| 100万 | 12.93% / -14.19% | **9.61% / -13.02%** | **-3.32 pp** |

诚实读法：满窗相对半窗 **CAGR 大幅回落**（约 −2.8～−3.3 pp）。主因：① 2025–2026 真实换仓，cost/AUM 从半窗 ~0.6% 升至 **~2.6–2.8%**；② 半窗尾段「抱着 2024 年末篮不换」高估了制度摩擦 alpha。

## 数字表（探索窗满窗；成本开；非密封）

| AUM | arm | CAGR | vs C0 | MDD | Sharpe | cost/AUM | target_weight 行数 |
|---|---|---|---|---|---|---|---|
| 600000 | X2/BOOK | **8.24%** (0.0824) | **-3.03 pp** | **-13.95%** | 0.635 | 0.0264 | 11400 |
| 600000 | X2/C0 | **11.27%** (0.1127) | — | -16.24% | 0.651 | 0.0002 | 570 |
| 1000000 | X2/BOOK | **9.61%** (0.0961) | **-1.66 pp** | **-13.02%** | 0.703 | 0.0283 | 11400 |
| 1000000 | X2/C0 | **11.27%** (0.1127) | — | -16.24% | 0.651 | 0.0002 | 570 |

起止：`2024-06-03→2026-10-09`。BOOK `n_codes=51`，`n_signals=**570**`，`gross_mean≈0.89`（60万）/ `≈0.92`（100万），`fill_ratio≈0.98` / `0.98`。

## 对照门锁

| AUM/arm | CAGR∈[12%,18%] | MDD≥−28% | 过门？ |
|---|---|---|---|
| 60万 BOOK | **否**（8.24% < 12%） | **是**（-13.95% ≥ −28%） | **否** |
| 100万 BOOK | **否**（9.61% < 12%） | **是**（-13.02% ≥ −28%） | **否** |

C0 基线仍未过 CAGR 下沿（≈11.27%）。  
**任意 AUM 过门：否（any_pass=false）。** 本结果为研究对照，非过关声称。

## vs C0 增量

| AUM | ΔCAGR | ΔMDD |
|---|---|---|
| 60万 | **-3.03 pp**（逊于纯 510300） | +2.29 pp（回撤略浅） |
| 100万 | **-1.66 pp**（逊于纯 510300） | +3.22 pp（回撤略浅） |

解读：满窗真实换仓后，制度摩擦 BOOK **两端均低于 C0 CAGR**；MDD 仍略浅。半窗「100万过门锁」在全日更下**未能复现**。

## 机制与候选口径（Leo 纠偏后）

- 本包 **非**教科书动量；四臂写清 ETF 申赎 / 解禁供给 / T+1 抛压 / 涨跌停带宽对手盘。  
- **满窗 any_pass=false** → **本跑次不标「主攻机制研究备选」**（门锁未过）。半窗过闸记录保留为历史对照，**不以半窗晋级**。  
- 仍 **`promotion_approved=false`** · **不交 Strategy** · **不开密封** · **不下单**。  
- Leo 纠偏适用：若日后满窗过闸，可进研究备选；本单未过。

## 双包对照摘要（同窗满窗）

| | 本包制度摩擦（主攻） | 动量扩池（对照） |
|---|---|---|
| mechanism | `g1g5_ashare_inst_friction_v1` | `g1g5_pit_debate_rule_v2_expand` |
| 60万 BOOK | **8.24% / -13.95%** | **11.37% / -15.15%** |
| 100万 BOOK | **9.61% / -13.02%** | **11.42% / -15.88%** |
| vs C0（60/100） | -3.03 / -1.66 pp | +0.11 / +0.15 pp |
| any_pass | **false** | **false** |
| 谁过门 | 无 | 无（动量两端 CAGR≈11.4%，差 12% 下沿约 0.6 pp） |

同窗结论：**动量对照 CAGR 高于制度摩擦约 +3.1 / +1.8 pp**，但仍未过 12% 门锁；两包满窗均 **any_pass=false**。

## 工程备注

- 模块：`python3 -m quantlab.portfolio.book_smoke`
- JSON：`output/v3/book_smoke_g1g5_nontextbook_x2/book_smoke_summary.json`（含 `experiment` / `weight_coverage_caveat.full_x2_daily=true` / `mandate_door` / `vs_baseline_C0` / `vs_half_window` / `vs_peer_package` / `mechanism_note`）
- NAV：`output/v3/book_smoke_g1g5_nontextbook_x2/aum_{600000,1000000}/X2/{BOOK,C0}/`
- promotion=false；不下单；不交 Strategy；不开密封。

## 结论（诚实）

1. **管线通 + 满窗真日更**：668 sessions 覆盖至 2026-10-09；`n_signals=570`；已证伪 stub 前推。  
2. **相对基线**：两端 BOOK CAGR **低于** 纯 510300（约 −3.0 / −1.7 pp）；MDD 略浅。  
3. **研究门锁**：**any_pass=false**（两端 CAGR 均 < 12%）。  
4. **半窗不可外推**：半窗 any_pass=true 被满窗打回；成本抬升是关键差异。  
5. **不标备选 / 不交 Strategy**：本跑次未过门锁；`promotion=false`。  
6. **相对动量对照**：同窗动量更高但仍未过门；见动量回执 `docs/v2/BOOK_SMOKE_G1G5_EXPAND_X2_RECEIPT_ZH.md`。
