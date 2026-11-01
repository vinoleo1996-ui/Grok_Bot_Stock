# 本地 trade_cal：20261019–20261023 is_open 证据（不依赖中转）

- 时刻：2026-10-25 ~04:53 ET
- 用途：Eng 专用补跑包 date_list 钉点；只读
- Arch .ok pin_trade_cal 期望：`141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086`
- live=false

## `/workspace/QuantLab/data/v2/calendar/trade_cal_sse_pit.parquet`
- sha256：`fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41`（sha8 `fa4260b8`）
- MATCH ok pin_trade_cal：`False`
- 行数：8035；列：cal_date, is_open, pretrade_date, available_at
- 切片 all_open=True open_count=5

| date | is_open |
|---|---|
| 20261019 | 1 |
| 20261020 | 1 |
| 20261021 | 1 |
| 20261022 | 1 |
| 20261023 | 1 |

## `/workspace/QuantLab/data/v2/tushare_raw/trade_cal.parquet`
- sha256：`141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086`（sha8 `141078fa`）
- MATCH ok pin_trade_cal：`True`
- 行数：9862；列：exchange, cal_date, is_open, pretrade_date
- 切片 all_open=True open_count=5

| date | is_open |
|---|---|
| 20261023 | 1 |
| 20261022 | 1 |
| 20261021 | 1 |
| 20261020 | 1 |
| 20261019 | 1 |

