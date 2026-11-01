# AI G1G5 降换手重生回执（X2）

- **时间：** 2026-10-12 ~11:24 ET
- **Leo 确认卡：** 「启动降换手+开GP」
- **promotion_approved：** false；不下单；不交 Strategy；禁 stub 前推；禁半窗乐观当备选

## 1) 权重产物

| 项 | 值 |
|---|---|
| **路径** | `output/intel/g1g5_lowturn_daily_weights_20261012_112301.parquet` |
| 行数 / sessions / 标的 | **33400 / 668 / 50** |
| 日期跨度 | 2024-01-02 → **2026-10-09** |
| reaches_x2_end | **true** |
| stub_window / stub_forward_fill | false / false |
| 日权重合计 | min=mean=max=**1.0** |
| mechanism_tag | `g1g5_ashare_inst_friction_v1_lowturn` |
| parent | `g1g5_ashare_inst_friction_v1`（非教科书四臂） |
| universe_id | `g1g5_mid_large_liquid_top50` |
| 列契约 | `weight_long_v1_20261012` + 别名 `session,instrument_id,weight` |
| meta sidecar | `output/intel/g1g5_lowturn_daily_weights_20261012_112301.parquet.meta.json` |
| run meta | `output/intel/g1g5_lowturn_run_meta_20261012_112301.json` |
| G6 | **pass** |
| peak_rss | **1899.2 MB**（≤2GB） |

## 2) 降换手设计

| 项 | 旧（月频非教科书 X2） | 新（本批） |
|---|---|---|
| 再平衡 | 月末 ≈35 次 | **季末+首末日 = 13 次** |
| 选股 | 每期 top20 等权硬切 | **进 top12 / 出 rank>28 带宽粘性**；持仓 cap=20 等权 |
| 日均单向换手 mean_one_way | **0.02871** | **0.00752** |
| 换手降幅 | — | **≈73.8%**（`turnover_reduction_ratio=0.738`） |
| 非零换手交易日 | （月频更多） | **12** / 667 |

再平衡 sessions：`2024-01-02, 2024-03-29, 2024-06-28, 2024-09-30, 2024-12-31, 2025-03-31, 2025-06-30, 2025-09-30, 2025-12-31, 2026-03-31, 2026-06-30, 2026-09-30, 2026-10-09`

脚本：`research/g1g5_low_turnover_weights.py`

## 3) who_pays（摘要）

A股制度摩擦组合（ETF份额流 / 解禁残差 / T+1 / 涨跌停带宽）+ 季频带宽粘性压成本/AUM；**明确排除**教科书式相对强弱或估值排序主线；who_pays **无「动量」字样**。

## 4) 请 New Bot

派 Beta Book-Smoke @60万/100万 vs 510300，主测本包：

`output/intel/g1g5_lowturn_daily_weights_20261012_112301.parquet`

对照（勿当主线）：月频非教科书 X2 `g1g5_nontextbook_daily_weights_20261012_111316.parquet`；动量备选 `g1g5_expand_daily_weights_20261012_111354.parquet`。

## 5) 不做

- 不下单；不交 Strategy；不扩 ACTIVE；不把过闸数字当晋级；不半窗乐观当备选
