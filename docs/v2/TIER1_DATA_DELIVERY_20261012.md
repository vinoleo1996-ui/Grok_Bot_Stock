# Tier-1 Data Delivery — 2026-10-12

`promotion_approved=false` 单表；**overall 晋级门未改**。
进度实时：`data/_acquire_logs/tier1_status.json`；脚本：`scripts/acquire/tier1_pull.py` / `tier1_materialize.py`。

---

## 1. 全市场日线 — **DONE（置顶）**

| | |
|---|---|
| 权威扁平 PIT | `data/v2/bars/daily_ohlcv_raw_pit.parquet` |
| 日期 | **2026-09-23 → 2026-10-12**（8 个交易日） |
| 标的/行 | 5566 / 44467 |
| 价格 | **原始不复权**；`adj_factor` 单独列 |
| 另含 | limit_up/down、tradestatus、is_st_at_open |
| available_at | trade_date **16:00 Asia/Shanghai** |
| 面板 | `data/v2/asof_extend_tushare_202610/panels/` 已追加到 2026-10-12 |
| Mac API | `daily_ohlcv_raw_pit` |
| 日更 | `python3 scripts/acquire/tier1_pull.py extend YYYYMMDD && python3 scripts/acquire/tier1_materialize.py bars` |

抽样：sz.000001@2026-06-30 close 与本地面板一致。

---

## 2. daily_basic — **可用（2014 中后段仍在补）**

| | |
|---|---|
| 权威表 | `data/v2/valuation/daily_basic_full_tushare.parquet`（11865655 行 / 5911 标的） |
| 日期跨度 | 2014-01-02 → 2026-10-12 |
| 优先列 | turnover_rate_f、volume_ratio（覆盖率 >99.8%） |
| available_at | trade_date **18:00 Asia/Shanghai** |
| Mac API | `daily_basic_full` |
| **缺口** | 2014 日历交易日 raw **63/245**；缺 **2014-04-09→2014-12-31** 约 182 日（后台续拉中）。2015-01→2026-10-12 完整。 |

---

## 3. 指数日线 — **DONE**

| | |
|---|---|
| 路径 | `data/v2/index/index_daily_pit.parquet` |
| 代码 | 000300.SH / 000905.SH / 000852.SH / **932000.CSI**(中证2000) / **000985.CSI**(中证全指) |
| 日期 | 2014-01-02 → 2026-10-12 |
| available_at | trade_date 16:00 Asia/Shanghai |
| Mac API | `index_daily_pit` |

---

## 4. stock_basic 含退市 — **DONE**

| | |
|---|---|
| 路径 | `data/v2/meta/stock_basic_incl_delisted.parquet` |
| 覆盖 | {'L': 5573, 'D': 339}；list_date_min=1990-12-01 |
| Mac API | `stock_basic_incl_delisted` |

---

## 5. balancesheet + cashflow PIT — **CF 完成 / BS 拉取中**

### 审计（existing `financials_pit_tushare`）
**同 end_date 保留多版本**：multi-row ≈21.5%，最多 4 版；update_flag 0/1 均在。原始+修订都留。

### cashflow — DONE
- `data/v2/financials_pit/cashflow_pit_tushare.parquet`
- 315718 行 / 5867 标的
- end_date 2009-12-31→2026-09-30
- available_at: coalesce(f_ann_date,ann_date) 18:00 Asia/Shanghai；全版本保留
- Mac API: `cashflow_pit`

### balancesheet — IN PROGRESS（已物化部分）
- raw: `data/v2/tushare_raw/balancesheet/` **249/5912** 只
- PIT: `data/v2/financials_pit/balancesheet_pit_tushare.parquet`（当前 237 标的 / 27145 行；含 total_assets/total_liab/equity_parent）
- 合并薄表: `data/v2/financials_pit/bs_cf_pit_tushare.parquet`
- Mac API: `balancesheet_pit`（覆盖未满，caveat 已标）
- 后台 6-worker relay 续拉；完成后重跑 `tier1_materialize.py bs_cf`

---

## API
- Tailscale `http://100.124.230.108:8787`
- `/query` limit 默认 5000、**最大 50000**；export 上限 5e6
- 新增 id: daily_ohlcv_raw_pit, daily_basic_full, index_daily_pit, stock_basic_incl_delisted, cashflow_pit, balancesheet_pit

## balancesheet_pit (updated 2026-10-12T16:25:08-0400)
- path: `/workspace/QuantLab/data/v2/financials_pit/balancesheet_pit_tushare.parquet`
- instruments: 5864 / raw_files: 5866
- rows: 451857
- end_date: 1989-12-31 → 2026-09-30
- ann: 1991-06-10 → 2026-10-13
- available_at: coalesce(f_ann_date,ann_date) 18:00 Asia/Shanghai; all update_flag/report_type versions kept
- multi_version_frac: 0.3763698524655804 (max_versions=8)
- promotion_approved: false
