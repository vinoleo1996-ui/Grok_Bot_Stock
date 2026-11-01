# Release `quantlab-data-2026-11-01` 验收

下载了 444 个资产，约 8.7 GB，放在 git 忽略的 `data/_release/`。分卷没有缺号：`local_market.tar.gz` part000–093，`v2.tar.gz` part000–348，另有单独的 `data_small.tar.gz`。压缩包没有 `.py`、`.sh`、`.env`，文件名里也没有 secret、token、password。这些文件没有提交进 git。

## 契约路径

| 路径 | 结果 |
| --- | --- |
| `data/v2/tushare_raw/trade_cal.parquet` | 在。9862 行。列 `exchange`、`cal_date`、`is_open`、`pretrade_date`。`cal_date` 2000-01-01 至 2026-12-31。 |
| `data/local_market/1c85fd9aceaa03c3c4863bec` | 在。日历 3043 个 `session`，2014-01-02 至 2026-07-10。`instruments.parquet` 6274 行，`asset_type` 全部是 `stock`。面板 6026 个。抽查 `sh.600000` 的行情止于 2026-06-30。 |
| `data/v2/asof_extend_tushare_202610/calendar.parquet` | 不在。同目录有 `manifest.json` 和 `panels/`。日历在 `data/v2/asof_extend_202610/calendar.parquet`，3114 行，至 2026-10-27。 |
| `data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet` | 在。7920 行。`available_at` 空值 0。最早 1984-05-09 18:00，最晚 2026-09-24 18:00。 |
| `data/v2/financials_pit/financials_pit_tushare.parquet` | 在。422129 行。`available_at` 空值 0，1995-01-05 至 2026-10-10，时区 Asia/Shanghai。没有 `metric`/`value` 长表，净利润在列 `net_profit`。文件内 `promotion_approved` 全是 false。 |
| `data/v2/ep/ep_pit_daily_tushare.parquet` | 在。9754901 行。`trade_date` 2018-01-02 至 2026-10-09。公布列名是 `e_available_at`，没有 `available_at`。按会话读取会因缺列失败，没有改列名。 |
| `data/v2/float_mktcap/float_mktcap_daily_tushare.parquet` | 不在。U30 臂记失败，没有用别的表顶上。 |
| `data/v2/etf/etf_daily_adj.parquet` | 不在。已落地的是 `data/v2/etf_510300/panels/sh.510300.parquet` 和 D0 的 `panels/sh.510300.parquet`。实验基准用 D0 这一份，并在结果里写明路径，没有改名成 `etf_daily_adj`。 |
| `data/v2/universe/mid_large_members_pit.parquet` | 在。5583027 行。`session` 2015-01-06 至 2026-10-27。`available_at` 空值 0。 |
| `output/d1/ENG_PING_PATHS.json` | 不在。不把晋升写成 true。 |

`Stock-patches` 在三份清单里都是 0 条。

探索窗用 2024-06-03 至 2026-06-30，停在 D0 面板的最后一天。没有重跑 2018-01-02 至 2024-05-31 的密封窗。
