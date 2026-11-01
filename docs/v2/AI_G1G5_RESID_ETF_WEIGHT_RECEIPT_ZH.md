# AI G1G5 个股残差×ETF份额流 权重回执（X2）

- **时间：** 2026-10-13 ~00:25 ET
- **Leo 确认卡：** 「启动残差+ETF新权重」
- **promotion_approved：** false；不下单；不交 Strategy；禁 stub 前推；不开 v29 同构 GP

## 1) 权重产物

| 项 | 值 |
|---|---|
| **路径** | `output/ai_factory/g1g5_resid_etf_daily_weights_20261013_002418.parquet` |
| 行数 / sessions / 标的 | **33400 / 668 / 50** |
| 日期跨度 | 2024-01-02 → **2026-10-09** |
| reaches_x2_end | **true**（50/50 panel 达 X2 末日） |
| stub_window / stub_forward_fill | false / false |
| 日权重合计 | min=mean=max=**1.0**；日均活跃名=**20** |
| mechanism_tag | `g1g5_ashare_resid_etf_flow_v1` |
| universe_id | `g1g5_mid_large_liquid_top50` |
| 列契约 | `weight_long_v1_20261012` + 别名 `session,instrument_id,weight` |
| meta sidecar | `output/ai_factory/g1g5_resid_etf_daily_weights_20261013_002418.parquet.meta.json` |
| run meta | `output/ai_factory/g1g5_resid_etf_run_meta_20261013_002418.json` |
| G6 | **pass** |
| peak_rss | **1767.7 MB**（≤2GB） |

脚本：`research/g1g5_resid_etf_weights.py`

## 2) 机制（相对已败包正交）

| 臂 | 定义 | 名义权重 |
|---|---|---:|
| **ind_size_resid** | trailing 20 日收益 − 同申万一级（宇宙内）等权 → 流通市值三分位 demean → 截面 z | 0.55 |
| **etf_share_flow** | 行业 ETF 份额流 PIT（复用 `score_etf_flow`）→ 成分继承 | 0.30 |
| **interaction** | z(resid)×z(etf)：偏好份额流入行业内的正残差个股 | 0.15 |

- **再平衡：** 月末 + 首日（35 次）→ top20 等权
- **明确不做：** unlock / T+1 / limit 四臂；excess_vs_510300 动量排序；CB/金主；教科书动量·价值·quality 主线 token
- **who_pays：** 残差定价修正对手盘 + ETF 创设/赎回对手盘（无「动量」字样）

## 3) 相对 prior 对齐

| 对照包 | 日均单向换手 mean_one_way | 活跃集 Jaccard（样例月） |
|---|---:|---|
| **本包 resid×ETF** | **0.02894** | — |
| nontextbook 月频 `…111316` | 0.02871 | ≈0.29–0.43（仅新≈8–11/20） |
| lowturn `…112301` | 0.00752 | ≈0.10–0.35（机制+持仓均异） |

换手与月频摩擦包同量级（同为月频 top20 EW）；选股 Jaccard 明显低于 0.5 → **非换皮**。相对 lowturn 换手更高（未做季频带宽），属预期。

## 4) 请 New Bot

派 Beta Book-Smoke @60万/100万 vs 510300，主测本包：

`output/ai_factory/g1g5_resid_etf_daily_weights_20261013_002418.parquet`

对照（勿当主线）：lowturn `output/intel/g1g5_lowturn_daily_weights_20261012_112301.parquet`；月频非教科书 `…111316`；动量 expand `…111354`。

## 5) 不做

- 不下单；不交 Strategy；不扩 ACTIVE；不密封；不把过闸数字当晋级
- 本任务**不自跑** Book-Smoke
- 不开 v29 同构 GP
