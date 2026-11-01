# 三腿并列组合 预注册（STRATEGY_THREE_LEG）

- 写入时间：2026-10-13T13:37:43-04:00（ET），**早于任何组合 book-smoke 运行**
- 性质：纸面研究；live=false · promotion=false · 禁 GP · 禁小盘 · 禁密封窗（仅 X2）
- 非「主干+卫星」：三腿并列，按固定权重表混合

## 腿（权重长表 + 单独回执已核实）
| 腿 | 权重 parquet | 单独 X2 60万 CAGR/MDD | 100万 |
|---|---|---|---|
| capacity_adv | output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet | 13.82%/−10.07% | 12.23%/−11.62% |
| earnings_event | output/ai_factory/g1g5_earnings_event_daily_weights_20261014_005430.parquet | 13.64%/−18.29% | 13.87%/−19.08% |
| insider_increase | output/ai_factory/g1g5_insider_increase_daily_weights_20261014_011841.parquet | 13.14%/−16.50% | 13.14%/−17.20% |

## 固定权重（最多 4 组，不做网格，跑完不调）
逆波动 / 回撤倒数 依据 X2 60万单腿 BOOK 净值（样本内，见 output/strategy_three_leg/weights_table.json；年化波动 13.85%/20.51%/17.48%，MDD −10.07%/−18.29%/−16.50%）。

| 组 | capacity_adv | earnings_event | insider_increase |
|---|---|---|---|
| B1 等权 | 1/3 | 1/3 | 1/3 |
| B2 逆波动 | 0.4053 | 0.2736 | 0.3211 |
| B3 回撤倒数 | 0.4626 | 0.2549 | 0.2825 |
| B4 50/25/25 | 0.50 | 0.25 | 0.25 |

混合：共同 session 上按权重线性相加 → 长表 → Eng book-smoke，sleeves {"core":0,"stock":1}，成本开（引擎默认 strategy_v1 成本），60万与100万，**以引擎 CAGR 为准**。

## 判定（事前固定）
某组 **过关** 当且仅当：60万 **与** 100万 两档 CAGR 均 **高于 capacity_adv 单独**（13.82% / 12.23%），且两档 MDD **不深于 −15%**。

## 披露
- X2（2024-06→2026-10）是**样本内**：三条叶均在 X2 上挑出，逆波动/回撤倒数权重亦取自 X2，结果有选择偏差，不构成样本外证据。
- 检查 60万档整手噪声（60万 vs 100万差异、按100股整手舍入的权重偏差）。
- 另列分年收益（图+表）。不改 capacity_adv 纸面 STATUS，不盖晋级章。
