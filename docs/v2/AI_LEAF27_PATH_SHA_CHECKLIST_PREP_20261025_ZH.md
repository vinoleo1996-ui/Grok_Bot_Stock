# 叶27 `.ok` 前路径/实现 sha 对照备忘（AI 预置 · 未核盘）

- 时刻：2026-10-25 ≈07:01 ET（America/New_York）
- 包钉：脚本 `7a5f756c0a1ab09fb55aa2bc3c17f389bde44d222d7066237e503566c908f8c6` / DIFF `e2ed0fc88bfe38c07892a3a87d03f9b2372cb8cfd568fd7de9548f3113978b71` / impl `a532e6db956600ab3e4048edeaabdc653b2e83ed4ef52f2839eeb78e12f87416` / 闭合 `f43279177c6fe8c3e6bce5d2aa60457d6cf586ecaecc375b33546141edaffc3e`
- Arch R2：`4c85a169…`；主豁免：`b39954c3…`；预告：`31462908…`
- **窗**：叶25 闭后、**≥10:50 ET** 另窗；不复用叶25钉；**本轮不申 .ok**
- **本文件仅摘脚本常量**，**未**对数据文件跑 sha（等 Data 盘点后对照）

## 脚本常量 sha

| 常量名 | 期望 sha256 |
|---|---|
| `MKTCAP_SHA` | `346d0dda8a95e8d209fd388cfb1aad5425745fc0b5eb0a16dd4de3ab3d72a1ef` |
| `ETF_SHA` | `48b21e84695b120b8621eff11f31f3e47879bfc05c93d3d979ddab9220ffd74c` |
| `CAPADV_HILIQ_SHA` | `3b288c832b956820af9802f02861af459e215e7d4097a6420724b26cf2d31c4d` |

## 路径常量（相对仓库根）

| 用途 | 路径 |
|---|---|
| OHLC | `data/v2/tushare_raw/daily/{YYYYMMDD}.parquet` |
| 市值 | `data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet` |
| 510300 | `data/v2/etf/etf_daily_adj.parquet` |
| capadv HI_LIQ | `output/strategy_hiliq/legs/g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet` |
| capadv FULLA | `output/strategy_fulla/legs/g1g5_capacity_adv_fulla_v1_daily_weights_20261014_192953.parquet` |
| SW L1 | `data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet` |
| limit ≤2026-06-30 | `data/local_market/1c85fd9aceaa03c3c4863bec/panels/{ex}.{code}.parquet` |
| limit ≥2026-07-01 | `data/v2/asof_extend_tushare_202610/panels/` |
| 宇宙 HI_LIQ / FULLA | `output/strategy_hiliq/universe_mask_hiliq_v1.parquet` / `…/fulla/…` |

## 下一步

1. 等 Data 盘点回执 → AI 对照上表常量（MATCH/DIFF）→ 交 Arch 另窗签 `.ok`  
2. 叶25@10:00–10:45 ET 优先；live=false

