# Book-Smoke 回执：G1G5 非教科书（A股制度摩擦）满仓表 vs 纯 510300

**run_id**：`book_smoke_20261012_110436`  
**strategy_promotion_approved**：`false`  
**sealed_claim**：`false`（不声称过密封线 / 不交 Strategy / 不下单）  
**promotion_approved**：`false`  
**Mandate**：`docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md`  
**授权**：Leo 经 New Bot 【立刻|非教科书 Book-Smoke】（本条 Book-Smoke only；主攻机制测）  
**门锁（Leo 2026-10-12，研究对照非过关）**：净成本 **CAGR ∈ [12%, 18%]** · **MDD 不差于 −28%**

## 实验设置

| 项 | 值 |
|---|---|
| 权重长表 | `output/intel/g1g5_nontextbook_daily_weights_20261012_110220.parquet`（**12100** 行 / **242** sessions / **50** 标的；**非 stub**） |
| 对照 meta | `output/intel/g1g5_nontextbook_run_meta_20261012_110220.json` |
| AI 回执 | `docs/v2/AI_G1G5_NONTEXTBOOK_WEIGHT_RECEIPT_ZH.md` |
| mechanism_tag | **`g1g5_ashare_inst_friction_v1`** |
| universe_id | `g1g5_mid_large_liquid_top50`（与动量扩池同宇宙） |
| 四臂（名义） | ETF份额流 **0.40** + 解禁残差 **0.25** + T+1抛压 **0.20** + 涨跌停带宽 **0.15** → top20 等权 |
| 明确排除 | 教科书相对强弱 / 估值排序 / `excess_20d vs 510300` |
| 袖套模式 | **满仓 stock 表**：`{"core":0.0,"stock":1.0,"alpha_event":0.0}` |
| combine 语义 | `book = stock×表内权重`；日权重合计恒 **1.0** |
| 对照 | `C0` = 纯 510300 |
| 窗 | 探索窗 **X2** `2024-06-03→2026-10-09` |
| 资金 | 60万 ∧ 100万 |
| 成本 | 开（`ExecConfig.strategy_v1`） |
| 可消费 | stock **book_consumable** rows=**4840** / sessions=**144**（X2∩权重日历） |
| 角色 | **主攻机制测**；动量扩池包保留为**研究备选/对照**（未废弃；Leo 纠偏：过闸动量可进备选） |

## ⚠ 覆盖缺口（必须读）

权重日历仅覆盖 **2024-01-02→2024-12-31**（全日更 242 sessions，非 stub）。  
落在 X2 内的可消费信号为 **2024-06-03→2024-12-31（144 sessions / 4840 rows）**。  
X2 后半段 **2025-01-01→2026-10-09** 无新权重：引擎 `combine()` 在最后一次信号后 **持仓前推** → 约一年半净值主要由  
**2024 年末截面篮的长期持有**贡献，**不是**制度摩擦全日更覆盖整窗。  

→ 本回执只证明：**非教科书满仓长表能进主书 + 相对 C0 / 动量备选有可算对比 + 研究门锁合取可算**；**不能**当作密封过线、整窗有效性证据、或可交 Strategy。  
**切勿**用 stub 前推解读、**切勿**交 Strategy、**切勿**晋级密封。

## 与动量扩池备选对照（同宇宙 / 同窗 / 机制不同）

动量扩池回执：`docs/v2/BOOK_SMOKE_G1G5_EXPAND_RECEIPT_ZH.md`（run_id `book_smoke_20261012_105647`；any_pass=true；**保留研究备选**）。

| | 动量扩池（备选/对照） | 本批 nontextbook（主攻） |
|---|---|---|
| mechanism_tag | `g1g5_pit_debate_rule_v2_expand` | **`g1g5_ashare_inst_friction_v1`** |
| 选股 | 截面 excess_20d vs 510300 → top20 | 制度摩擦四臂合成 → top20 |
| 60万 BOOK | **13.15%** / −14.89% | **11.08%** / −14.33% |
| 100万 BOOK | **13.77%** / −15.07% | **12.93%** / −14.19% |
| ΔCAGR vs 动量 | — | 60万 **−2.07 pp**；100万 **−0.84 pp** |
| ΔMDD vs 动量 | — | 60万 **+0.56 pp**（略浅）；100万 **+0.88 pp**（略浅） |
| any_pass | true | **true**（仅 100万合取过；60万 CAGR 低于 12%） |

诚实读法：同宇宙同窗下，**动量备选 CAGR 更高**；本包 MDD 略浅、100万仍过研究门锁下沿。二者并行可测，**不互相废弃**。

## 数字表（探索窗；成本开；非密封）

| AUM | arm | CAGR | vs C0 | MDD | Sharpe | cost/AUM | target_weight 行数 |
|---|---|---|---|---|---|---|---|
| 600000 | X2/BOOK | **11.08%** (0.1108) | **−0.19 pp** | **−14.33%** | 0.831 | 0.0060 | 11400 |
| 600000 | X2/C0 | **11.27%** (0.1127) | — | −16.24% | 0.651 | 0.0002 | 570 |
| 1000000 | X2/BOOK | **12.93%** (0.1293) | **+1.66 pp** | **−14.19%** | 0.913 | 0.0067 | 11400 |
| 1000000 | X2/C0 | **11.27%** (0.1127) | — | −16.24% | 0.651 | 0.0002 | 570 |

起止：`2024-06-03→2026-10-09`。BOOK `n_codes=51`（50 股+路径计价），`n_signals=144`，`gross_mean≈0.90`（60万）/ `≈0.93`（100万），`fill_ratio≈0.99`。

## 对照门锁

| AUM/arm | CAGR∈[12%,18%] | MDD≥−28% | 过门？ |
|---|---|---|---|
| 60万 BOOK | **否**（11.08% < 12%） | **是**（−14.33% ≥ −28%） | **否** |
| 100万 BOOK | **是**（12.93%） | **是**（−14.19% ≥ −28%） | **是** |

C0 基线仍未过 CAGR 下沿（11.27% < 12%）；MDD 宽于 −28%。  
**任意 AUM 过门：是（any_pass=true）**——仅 100万合取过；60万因 CAGR 略低于 12% 未过。本结果为**研究对照**，非过关声称。

## vs C0 增量

| AUM | ΔCAGR | ΔMDD |
|---|---|---|
| 60万 | **−0.19 pp**（略逊于纯 510300） | +1.91 pp（回撤略浅） |
| 100万 | **+1.66 pp** | +2.06 pp（回撤略浅） |

解读：100万规模下制度摩擦满仓相对纯 510300 **抬升 CAGR** 且 MDD 更浅；60万略低于 C0（成本/闲置现金差更敏感）。覆盖缺口仍在 → **不可当作整窗 alpha 证明**。

## 机制与候选口径（Leo 纠偏后）

- 本包 **非**教科书动量；`who_pays_zh` 写清 ETF 申赎 / 解禁供给 / T+1 抛压 / 涨跌停带宽对手盘。  
- **any_pass=true** → 可标 **「主攻机制研究备选」**（与动量扩池备选并行）。  
- 仍 **`promotion_approved=false`** · **不交 Strategy** · **不开密封** · **不下单**。  
- 是否从备选再往前推，等 Leo 点头；下一步优先考虑补全日更至 X2 尾（禁 stub 前推冒充过关）。

## 工程备注

- 模块：`python3 -m quantlab.portfolio.book_smoke`
- `run_book`：schedule 含 HFQ 默认 7 ETF 之外的个股时，回落 `load_execution_panels`（51 codes / 50 outside HFQ）。
- JSON：`output/v3/book_smoke_g1g5_nontextbook/book_smoke_summary.json`（含 `experiment` / `weight_coverage_caveat` / `mandate_door` / `vs_baseline_C0` / `vs_momentum_expand` / `mechanism_note`）
- NAV 产物：`output/v3/book_smoke_g1g5_nontextbook/aum_{600000,1000000}/X2/{BOOK,C0}/`
- promotion=false；不下单；不交 Strategy；不开密封 X1 / 事件臂。

## 结论（诚实）

1. **管线通**：非教科书非 stub 满仓长表经 WeightLongTableSleeve（stock=1/core=0）进主书，consumable sessions=144 ≫10，BOOK ≠ C0（可算增量）。  
2. **相对基线**：100万 BOOK CAGR **高于** 纯 510300≈11.3%（+1.66 pp），MDD 更浅；60万略逊于 C0（−0.19 pp）。  
3. **研究门锁合取**：**any_pass=true**（100万过；60万 CAGR 11.08% 未过下沿）。  
4. **相对动量备选**：同宇宙同窗下 CAGR 低约 **0.8～2.1 pp**，MDD 略浅；动量包保留备选，本包为主攻机制测。  
5. **可标主攻机制研究备选，但不可晋级**：① 权重日历止于 2024-12-31 + 持仓前推；② `promotion=false` / 不交 Strategy。  
6. **下一步建议**（研究向）：补覆盖完整 X2（至少至 2026-10）的制度摩擦日更权重后再重跑；勿用 stub 前推填洞；勿因 any_pass 交 Strategy。
