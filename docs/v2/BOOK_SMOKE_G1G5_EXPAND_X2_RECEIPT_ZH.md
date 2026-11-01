# Book-Smoke 回执：G1G5 扩池（截面动量 PIT）**X2 满窗日更** vs 纯 510300

**run_id**：`book_smoke_20261012_111737`  
**strategy_promotion_approved**：`false`  
**sealed_claim**：`false`（不声称过密封线 / 不交 Strategy / 不下单）  
**promotion_approved**：`false`  
**Mandate**：`docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md`  
**授权**：Leo 经 New Bot 【立刻|双包 X2 满窗 Book-Smoke】（本条=动量对照包）  
**门锁（Leo 2026-10-12，研究对照非过关）**：净成本 **CAGR ∈ [12%, 18%]** · **MDD 不差于 −28%**  
**Leo 纠偏**：过闸动量可进**研究备选**，不机械剔除；本满窗未过闸 → 本跑次不标备选。

## 实验设置

| 项 | 值 |
|---|---|
| 权重长表 | `output/intel/g1g5_expand_daily_weights_20261012_111354.parquet`（**33400** 行 / **668** sessions / **50** 标的） |
| 对照 meta | `output/intel/g1g5_expand_run_meta_20261012_111354.json`（`reaches_x2_end=true` · `stub_window=false` · `stub_forward_fill=false`） |
| mechanism_tag | **`g1g5_pit_debate_rule_v2_expand`**（截面动量 PIT） |
| universe_id | `g1g5_mid_large_liquid_top50` |
| 选股 | 截面 excess_20d vs 510300 → top20 等权；月频再平衡 |
| 袖套模式 | **满仓 stock 表**：`{"core":0.0,"stock":1.0,"alpha_event":0.0}` |
| 对照 | `C0` = 纯 510300 |
| 窗 | 探索窗 **X2** `2024-06-03→2026-10-09` |
| 资金 | 60万 ∧ 100万 |
| 成本 | 开（`ExecConfig.strategy_v1`） |
| 可消费 | stock **book_consumable** rows=**13360** / sessions=**570**（X2∩权重日历=整窗） |
| 角色 | **对照研究包**（主攻=制度摩擦同窗回执） |

## ✅ 满窗日更（无 stub 前推）— 已用数据核验

| 核验项 | 结果 |
|---|---|
| 权重日历 | **2024-01-02→2026-10-09**（668 sessions） |
| meta `reaches_x2_end` | **true** |
| meta `stub_forward_fill` / `stub_window` | **false / false** |
| BOOK `n_signals` | **570** |
| 唯一组合数 | **35**（2024 年 13 + **2025+ 23**） |
| 尾段相同组合长度 | **1** |
| 日权重合计 | 恒 **1.0**；日活跃约 20 只 |

→ **禁止**再写「后半持仓前推」。半窗旧回执 `docs/v2/BOOK_SMOKE_G1G5_EXPAND_RECEIPT_ZH.md` 仅作对照，勿覆盖。

## 与半窗旧回执并列表

半窗 run：`book_smoke_20261012_105647` · 权重止于 2024-12-31 · consumable sessions=144 + 持仓前推 · any_pass=**true**（两端过）。

| AUM | 半窗 BOOK CAGR/MDD | **满窗** BOOK CAGR/MDD | ΔCAGR |
|---|---|---|---|
| 60万 | 13.15% / -14.89% | **11.37% / -15.15%** | **-1.78 pp** |
| 100万 | 13.77% / -15.07% | **11.42% / -15.88%** | **-2.35 pp** |

诚实读法：满窗相对半窗 CAGR **回落约 −1.8～−2.4 pp**；cost/AUM 从 ~0.6% 升至 **~2.8–3.1%**。半窗过门锁在全日更下**未能复现**（两端差 12% 下沿约 0.6 pp）。

## 数字表（探索窗满窗；成本开；非密封）

| AUM | arm | CAGR | vs C0 | MDD | Sharpe | cost/AUM | target_weight 行数 |
|---|---|---|---|---|---|---|---|
| 600000 | X2/BOOK | **11.37%** (0.1137) | **+0.11 pp** | **-15.15%** | 0.779 | 0.0284 | 11400 |
| 600000 | X2/C0 | **11.27%** (0.1127) | — | -16.24% | 0.651 | 0.0002 | 570 |
| 1000000 | X2/BOOK | **11.42%** (0.1142) | **+0.15 pp** | **-15.88%** | 0.762 | 0.0307 | 11400 |
| 1000000 | X2/C0 | **11.27%** (0.1127) | — | -16.24% | 0.651 | 0.0002 | 570 |

起止：`2024-06-03→2026-10-09`。BOOK `n_codes=51`，`n_signals=**570**`，`gross_mean≈0.89` / `≈0.93`，`fill_ratio≈0.95` / `0.94`。

## 对照门锁

| AUM/arm | CAGR∈[12%,18%] | MDD≥−28% | 过门？ |
|---|---|---|---|
| 60万 BOOK | **否**（11.37% < 12%） | **是**（-15.15% ≥ −28%） | **否** |
| 100万 BOOK | **否**（11.42% < 12%） | **是**（-15.88% ≥ −28%） | **否** |

**任意 AUM 过门：否（any_pass=false）。** 两端 CAGR 略高于 C0，但均未到 12% 下沿。

## vs C0 增量

| AUM | ΔCAGR | ΔMDD |
|---|---|---|
| 60万 | **+0.11 pp** | +1.10 pp（回撤略浅） |
| 100万 | **+0.15 pp** | +0.36 pp（回撤略浅） |

## 机制与候选口径（Leo 纠偏）

- 机制=**截面动量 PIT**（excess_20d vs 510300 → top20）。  
- Leo：**过闸可进研究备选，不机械剔除**；**不作主线 / 不交 Strategy**。  
- **本满窗 any_pass=false** → **本跑次不标「对照研究备选」**。半窗过闸记录保留历史备选痕迹，**不以半窗代替满窗过关**。  
- `promotion_approved=false` · 不开密封 · 不下单。

## 双包对照摘要（同窗满窗）

| | 制度摩擦（主攻） | 本包动量（对照） |
|---|---|---|
| mechanism | `g1g5_ashare_inst_friction_v1` | `g1g5_pit_debate_rule_v2_expand` |
| 60万 BOOK | **8.24% / -13.95%** | **11.37% / -15.15%** |
| 100万 BOOK | **9.61% / -13.02%** | **11.42% / -15.88%** |
| any_pass | **false** | **false** |
| 谁过门 | 无 | 无 |

同窗结论：动量 CAGR 高于制度摩擦，但仍差门锁约 0.6 pp；**双包满窗均未过门**。主攻回执：`docs/v2/BOOK_SMOKE_G1G5_NONTEXTBOOK_X2_RECEIPT_ZH.md`。

## 工程备注

- 模块：`python3 -m quantlab.portfolio.book_smoke`
- JSON：`output/v3/book_smoke_g1g5_expand_x2/book_smoke_summary.json`（含 `experiment` / `weight_coverage_caveat.full_x2_daily=true` / `mandate_door` / `vs_baseline_C0` / `vs_half_window` / `vs_peer_package` / `mechanism_note`）
- NAV：`output/v3/book_smoke_g1g5_expand_x2/aum_{600000,1000000}/X2/{BOOK,C0}/`
- promotion=false；不下单；不交 Strategy；不开密封；不晋级 V31。

## 结论（诚实）

1. **管线通 + 满窗真日更**：668 sessions；`n_signals=570`；已证伪 stub 前推。  
2. **相对基线**：两端 BOOK CAGR **略高于** C0（约 +0.11 / +0.15 pp）；MDD 略浅。  
3. **研究门锁**：**any_pass=false**（两端 CAGR ≈11.4% < 12%）。  
4. **半窗不可外推**：半窗 any_pass=true 被满窗打回。  
5. **Leo 纠偏已落实**：不过闸则本跑次不标备选；过闸才进研究备选——本单未过。  
6. **不交 Strategy** / `promotion=false`。
