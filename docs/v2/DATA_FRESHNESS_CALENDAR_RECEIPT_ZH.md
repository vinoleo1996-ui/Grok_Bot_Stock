# 数据新鲜度 + 交易日历 回执（架构评审 Top1，2026-10-14）

研究级，promotion_approved=false。未启 8787，未碰 moneyflow，fund_portfolio 队列（PID 560350）未受影响。

## ① 510300 / ETF 复权
- `data/v2/etf/etf_daily_adj.parquet`：last_date 20261013，1,559,736 行，sha256 39c0e9a6cb…
- `data/v2/etf_510300/panels/sh.510300.parquet`：last_date 20261013，3,492 行，sha256 d8bd408107…
- 已到最新可得交易日（20261013；10-14 收盘数据由 05:55 ET 日更例行拉取），本次无需增量。
- `scripts/nightly_update.py` 已含 `etf_daily_adj`（scripts/acquire/etf_daily_adj_incr.py）与 `eng_panels`（510300）两步，核实无误。

## ② A 股交易日历 PIT 表
- 文件：`data/v2/calendar/trade_cal_sse_pit.parquet`，manifest `data/v2/calendar/manifest.json`
- 来源 Tushare trade_cal（relay），SSE；字段 cal_date / is_open / pretrade_date / available_at
- 覆盖 20050101–20261231，8,035 个自然日、5,343 个开市日，无缺日；sha256 fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41
- available_at 口径：(年份−1)-12-31 09:00 上海时间（休市安排通常上一年 12 月发布），保守近似
- 脚本 `scripts/acquire/trade_cal_pit.py`，幂等（内容不变不重写）；已作为 `trade_cal` 步骤放在日更最前

## ③ 数据新鲜度状态文件
- 脚本 `scripts/acquire/data_freshness_status.py`，已作为 `freshness` 步骤放在日更末尾
- 输出 `output/data_freshness_status.json`：expected_trade_date、overall(ok/stale)、stale_tables，以及每表 last_date、lag_trading_days、stale、rows、sha256、generated_at（上海与 ET）
- expected_trade_date = 日历中 ≤ 今天(上海) 的最后开市日；当天开市且上海时间 < 20:00 时取前一开市日（FRESH_CUTOFF_HOUR 可调）
- 核心表：daily_raw（tushare_raw/daily 按日文件，行数/sha 为最后一个文件）、daily_ohlcv_raw_pit、adj_factor、daily_basic、index_daily_pit、etf_daily_adj、etf510300、mid_large_universe、trade_cal
- 首次手动生成（2026-10-14 05:48 ET）：expected 20261013，overall=ok，全部表 lag=0
