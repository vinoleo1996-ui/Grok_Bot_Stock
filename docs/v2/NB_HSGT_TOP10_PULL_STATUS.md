# hsgt_top10 / hk_hold 补数状态

Updated: 2026-10-12 09:15:40 ET

## hk_hold_ashare — DONE ≥2025-06
- path: `data/v2/northbound/hk_hold_ashare_daily_2018plus.parquet`
- date: 20180102 → 20250630
- nrows: 3,715,734
- max available_at: 2025-06-30 18:00:00
- note: 日频A股连续至约20240816；其后季末点有A股: 20240930,20241231,20250331,20250630

## hsgt_top10 — IN PROGRESS (2024–2025 window first)
- path: `data/v2/northbound/hsgt_top10_daily_2018plus.parquet`
- current parquet: 20180102 → 20220531
- pull: {'status': 'running_windowed', 'window': ['20240101', '20250630'], 'todo': 359, 'done': 10, 'fail': 0, 'last': '20240115', 'last_rows': 20}
- raw daily checkpoints: `data/v2/tushare_raw/hsgt_top10/`
- runner: `scripts/acquire/fill_hsgt_top10_windowed.py` (relay; anns SIGSTOP'd to free pool)
- target date_max ≥ 20250630

## margin_detail — DONE
- path: `data/v2/margin/margin_detail_daily_2018plus.parquet`
- date: 20180102 → 20261009
- max available_at: 2026-10-12 09:00:00

promotion_approved=false throughout.
