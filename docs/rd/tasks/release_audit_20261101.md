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

## 全量分卷（2026-11-01 19:25 CST）

`v2.tar.gz` 现为 part000–469，共 470 片，没有缺号。最后一片 5,384,992 字节，其余每片 20,971,520 字节，合计约 9.84 GB。part000 以 gzip 头 `1f8b` 开始，part349 不是新的 gzip 头，所以后 121 片是同一条压缩流的后半段。加上此前的 `local_market` 94 片和 `data_small.tar.gz`，Release 共 565 个资产。没有 `.py`、`.sh`、`.env`，新增文件名里也没有 secret、token、password。

这次多出来的契约文件：

- `data/v2/etf/etf_daily_adj.parquet`：1,576,797 行。`trade_date` 2015-01-05 至 2026-10-27。`available_at` 空值 0。其中 `ts_code` 以 510300 开头的 2,869 行。列里有 `close` 和 `close_hfq`，读取器不把后复权价改名为 `close`。
- `data/v2/float_mktcap/float_mktcap_daily_tushare.parquet`：9,756,821 行。`trade_date` 2018-01-02 至 2026-10-09。有 `instrument_id`、`float_mktcap`。没有 `available_at`。文件内 `promotion_approved` 全是 false，`quality_status` 全是 `research`。按决策日读取时，现有读取器会因缺列失败，不用 `trade_date` 冒充公布时点。

`output/d1/ENG_PING_PATHS.json` 和 `data/v2/dividends/dividends.parquet` 仍然不在。`Stock-patches` 仍然是 0 条。E/P 仍只有 `e_available_at`。先前探索窗把 U30 记为缺文件、把基准指到 D0 的 `sh.510300`，对应的是当时只下到 part348 的包；ETF 日表现在已经在，U30 仍缺公布时点列。没有为这两张新表重跑消融，也没有把晋升写成 true。
