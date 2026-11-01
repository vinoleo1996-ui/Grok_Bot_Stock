# Book-Smoke 回执：G1G5 扩池全日更满仓表 vs 纯 510300

**run_id**：`book_smoke_20261012_105647`  
**strategy_promotion_approved**：`false`  
**sealed_claim**：`false`（不声称过密封线 / 不交 Strategy / 不下单）  
**promotion_approved**：`false`  
**Mandate**：`docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md`  
**授权**：Leo 经 New Bot 【立刻|G1G5扩池 Book-Smoke】（本条 Book-Smoke only）  
**门锁（Leo 2026-10-12，研究对照非过关）**：净成本 **CAGR ∈ [12%, 18%]** · **MDD 不差于 −28%**

## 实验设置

| 项 | 值 |
|---|---|
| 权重长表 | `output/intel/g1g5_expand_daily_weights_20261012_105459.parquet`（**12100** 行 / **242** sessions / **50** 标的；**非 stub**） |
| 对照 meta | `output/intel/g1g5_expand_run_meta_20261012_105459.json` |
| 接线/扩池回执 | `docs/v2/AI_G1G5_EXPAND_G6_RECEIPT_ZH.md` |
| mechanism_tag | `g1g5_pit_debate_rule_v2_expand` |
| universe_id | `g1g5_mid_large_liquid_top50` |
| 袖套模式 | **满仓 stock 表**（非 overlay）：`{"core":0.0,"stock":1.0,"alpha_event":0.0}` |
| combine 语义 | `book = stock×表内权重`；日权重合计恒 **1.0**（top20 等权截面）；**勿**再用上批 core=1+stock=1（否则会 ~双倍敞口） |
| 对照 | `C0` = 纯 510300 |
| 窗 | 探索窗 **X2** `2024-06-03→2026-10-09` |
| 资金 | 60万 ∧ 100万 |
| 成本 | 开（`ExecConfig.strategy_v1`） |
| 可消费 | stock **book_consumable** rows=**4840** / sessions=**144**（X2∩权重日历） |
| 日权重合计 | **恒 1.0**（满仓截面表，不是上批 ~5% 卫星仓） |
| 成分 | 50 中大盘可交易子集；日活跃约 20 只等权 |

## 与上批 G1G5（卫星 overlay）差异

上批 `BOOK_SMOKE_G1G5_RECEIPT_ZH.md`：3 标的辩论袖套 **overlay**（core=1 + stock=1，日权重合计约 0.04–0.06）。  
本批：扩池 **50 标的满仓表**（core=0 + stock=1，日权重合计=1.0）。两批数字 **不可直接比**。

## ⚠ 覆盖缺口（必须读）

权重日历仅覆盖 **2024-01-02→2024-12-31**（全日更 242 sessions，非 stub）。  
落在 X2 内的可消费信号为 **2024-06-03→2024-12-31（144 sessions / 4840 rows）**。  
X2 后半段 **2025-01-01→2026-10-09** 无新权重：引擎 `combine()` 在最后一次信号后 **持仓前推** → 约一年半净值主要由  
**2024 年末截面篮的长期持有**贡献，**不是** G1G5 扩池全日更覆盖整窗。  
`n_unique_portfolios≈8`（目标权重视图；月频再平衡落在 X2 前半 + 尾段前推）。

→ 本回执只证明：**扩池满仓长表能进主书 + 相对 C0 有可算对比 + 研究门锁合取可算**；**不能**当作密封过线、动量规则可晋级主线、或全日更整窗有效性证据。  
**切勿**用 stub 前推解读、**切勿**交 Strategy、**切勿**晋级 V31。

## 数字表（探索窗；成本开；非密封）

| AUM | arm | CAGR | vs C0 | MDD | Sharpe | cost/AUM | target_weight 行数 |
|---|---|---|---|---|---|---|---|
| 600000 | X2/BOOK | **13.15%** (0.1315) | **+1.88 pp** | **−14.89%** | 0.881 | 0.0059 | 11400 |
| 600000 | X2/C0 | **11.27%** (0.1127) | — | −16.24% | 0.651 | 0.0002 | 570 |
| 1000000 | X2/BOOK | **13.77%** (0.1377) | **+2.50 pp** | **−15.07%** | 0.894 | 0.0065 | 11400 |
| 1000000 | X2/C0 | **11.27%** (0.1127) | — | −16.24% | 0.651 | 0.0002 | 570 |

起止：`2024-06-03→2026-10-09`。BOOK `n_codes=50`，`n_signals=144`，`gross_mean≈0.92`（60万）/ `≈0.95`（100万），`fill_ratio≈0.95` / `0.96`。

## 对照门锁

| AUM/arm | CAGR∈[12%,18%] | MDD≥−28% | 过门？ |
|---|---|---|---|
| 60万 BOOK | **是**（13.15%） | **是**（−14.89% ≥ −28%） | **是** |
| 100万 BOOK | **是**（13.77%） | **是**（−15.07% ≥ −28%） | **是** |

C0 基线仍未过 CAGR 下沿（11.27% < 12%）；MDD 宽于 −28%。  
**任意 AUM 过门：是（any_pass=true）。** 本结果为**研究对照**，非过关声称；见下方机制提醒与覆盖缺口。

## vs C0 增量

| AUM | ΔCAGR | ΔMDD |
|---|---|---|
| 60万 | **+1.88 pp** | +1.35 pp（回撤略浅） |
| 100万 | **+2.50 pp** | +1.17 pp（回撤略浅） |

解读：扩池满仓截面相对纯 510300 在探索窗上 **抬升了 CAGR**，MDD 亦略浅；但尾段持仓前推 + 截面动量选股机制 → **不可当作可晋级 alpha**。

## ⚠ 机制提醒（Leo 禁教科书动量主线）

`who_pays_zh` / 扩池回执明确：持仓规则为 **截面 excess_20d vs 510300 排序 → top20 等权**（**截面动量 PIT 规则选股**）。  
Leo 明确 **禁教科书动量作主线**。  
→ **本回执不作晋级 / 不作主线候选 / 不进 hard_gates**；仅作授权对照与管线验证。  
`mechanism_tag=g1g5_pit_debate_rule_v2_expand`；`not_hard_gates_candidate=true`。

## 工程备注

- 模块：`python3 -m quantlab.portfolio.book_smoke`
- `run_book`：schedule 含 HFQ 默认 7 ETF 之外的 49 只个股时，回落 `load_execution_panels`。
- JSON：`output/v3/book_smoke_g1g5_expand/book_smoke_summary.json`（含 `experiment` / `weight_coverage_caveat` / `mandate_door` / `vs_baseline_C0` / `mechanism_note`）
- NAV 产物：`output/v3/book_smoke_g1g5_expand/aum_{600000,1000000}/X2/{BOOK,C0}/`
- promotion=false；不下单；不交 Strategy；不开密封 X1 / 事件臂；不晋级 V31。

## 结论（诚实）

1. **管线通**：G1G5 扩池非 stub 满仓长表经 WeightLongTableSleeve（stock=1/core=0）进主书，consumable sessions=144 ≫10，BOOK ≠ C0（可算增量）。  
2. **相对基线**：探索窗 BOOK CAGR **高于** 纯 510300≈11.3%（约 +1.9～+2.5 pp）；MDD 略浅。  
3. **研究门锁合取**：两端 BOOK 均落在 CAGR [12%,18%] 且 MDD ≥ −28% → **any_pass=true**（研究对照口径）。  
4. **不可晋级**：① 权重日历止于 2024-12-31 + 持仓前推；② 机制为截面动量 PIT 选股，Leo 禁教科书动量主线 → **不作主线/晋级候选**；`strategy_promotion_approved=false`。  
5. **下一步建议**（研究向，勿交 Strategy）：若要严肃整窗对照，需要 **覆盖完整 X2（至少至 2026-10）的日更权重**；另需非动量主线机制再评估。勿用 stub 前推填洞；勿因 any_pass 交 Strategy。
