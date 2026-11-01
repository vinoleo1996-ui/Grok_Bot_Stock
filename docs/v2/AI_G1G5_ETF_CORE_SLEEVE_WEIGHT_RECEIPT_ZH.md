# AI G1G5 ETF-core+个股袖套 权重回执（X2）

- **时间：** 2026-10-12 ~20:49 ET
- **Leo 确认卡：** 「ETF-core+个股袖套混合」（t176s767）
- **promotion_approved：** false；不下单；不交 Strategy；禁 stub 前推；不开 GP；不投 resid×份额同构
- **who_pays 预注册：** `docs/v2/AI_G1G5_ETF_CORE_SLEEVE_WHO_PAYS_PREREG_ZH.md`

## 1) 权重产物

| 项 | 值 |
|---|---|
| **路径** | `output/ai_factory/g1g5_etf_core_sleeve_daily_weights_20261012_204928.parquet` |
| 行数 / sessions / 标的 | **59452 / 668 / 89** |
| 日期跨度 | 2024-01-02 → **2026-10-09** |
| reaches_x2_end | **true** |
| stub_window / stub_forward_fill | false / false |
| 日权重合计 | min=mean=max=**1.0** |
| 日均活跃名 | ≈**12.9**（8–14） |
| **ETF-core 日均权重** | **0.70** |
| **个股袖套日均权重** | **0.30** |
| mechanism_tag | `g1g5_ashare_etf_core_sleeve_v1` |
| universe_id | `g1g5_etf_core_sleeve_mid_large_v1` |
| 列契约 | `weight_long_v1_20261012` + 别名 `session,instrument_id,weight` |
| meta sidecar | `…204928.parquet.meta.json` |
| run meta | `output/ai_factory/g1g5_etf_core_sleeve_run_meta_20261012_204928.json` |
| G6 | **pass** |
| peak_rss | **2081.2 MB**（软目标 ≤1.5GB **未达**；D1 估值 asof 过滤读主导；仍研究级可消费） |

脚本：`research/g1g5_etf_core_sleeve_weights.py`

末日（2026-10-09）持仓结构示例：ETF `510300.SH` 压舱 + 行业 ETF（如 159206/159363/159692/159869/512200）合计 **0.70**；个股袖套 6 名合计 **0.30**。

## 2) 机制（相对已败四包正交）

| 腿 | 名义 | 定义 |
|---|---:|---|
| **ETF-core** | 0.70 | SW L1 份额流 PIT top5 → `sw_l1_etf_map_pit_daily` 液态代表 ETF（max amt20）；core 内 25%→510300 压舱 |
| **个股袖套** | 0.30 | 流入行业 ∩ 中大盘 top50；D1 `turnover_rate` asof 承接排序 top≤8 等权 |

- **再平衡：** 月末 + 首日（35 次）
- **明确不做：** 100% 股票满仓；残差×份额交互；unlock/T+1/limit 四臂；PE/PB 估值主轴；CB/金主；教科书动量·价值·quality token
- **who_pays：** 份额流对手盘 + 流动性承接对手盘（无「动量/价值」字样）
- **D1：** ACCEPT_FULL 仅研究 asof（换手）；**非**晋级授权；禁假跑 V35

## 3) 相对 prior 对齐（非换皮）

| 对照包 | 样例月 Jaccard | 本包活跃含 ETF 名数 |
|---|---:|---:|
| resid_etf `…002418` | ≈0.10–0.27 | 5–6 |
| nontextbook 月频 `…111316` | ≈0.12–0.32 | 5–6 |
| lowturn `…112301` | ≈0.00–0.16 | 5–6 |

本包日均单向换手 ≈**0.029**（月频量级）。活跃集 Jaccard 明显低于 0.5，且主仓为 **ETF 工具** → **结构正交，非换皮**。

## 4) 请 New Bot

派 Beta Book-Smoke **@60万∧100万 vs 510300**，主测：

`output/ai_factory/g1g5_etf_core_sleeve_daily_weights_20261012_204928.parquet`

对照（勿当主线）：resid_etf / lowturn / expand。请 Alpha 研究级 ACCEPT（不扩 ACTIVE、不密封）。

## 5) 不做

- 不下单；不交 Strategy；不扩 ACTIVE；不密封；不把过闸数字当晋级
- 本任务**不自跑** Book-Smoke
- 不开 GP / 不开 v29
