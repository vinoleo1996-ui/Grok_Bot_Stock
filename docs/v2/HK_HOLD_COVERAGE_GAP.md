# hk_hold (北向持股) 覆盖说明

Updated: 2026-10-12 ~09:00 ET

## 权威路径
- Raw: `data/v2/tushare_raw/hk_hold/{YYYYMMDD}.parquet`
- PIT A-share panel: `data/v2/northbound/hk_hold_ashare_daily_2018plus.parquet`
- Summary: `data/v2/northbound/northbound_summary.json`
- `available_at` = trade_date 18:00 Asia/Shanghai（收盘后披露；无更紧日内证据）
- `promotion_approved=false`（研究级）

## 覆盖（rebuild 2026-10-12）
- date_min / date_max (A-share rows): **20180102 → 20250630**
- 日频 A 股连续窗口约至 **20240816**；其后多数交易日 API 仅返回港股名（A=0，合并时丢弃）
- **季末仍有完整 A 股持股**：20240930 / 20241231 / 20250331 / 20250630（及更早季末）
- 研究侧：日频因子用 ≤20240816；更长窗用「有 A 行的日期」（含季末点），勿虚构日频

## 列
`code, trade_date, ts_code, name, vol, ratio, exchange, available_at, available_at_tz, promotion_approved`
