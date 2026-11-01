# SHARE_FLOAT X1 early window (2015–2017)

**promotion_approved=false** · research_grade · 2026-10-12

## Why
UNLOCK-WINDOW-RESID / Beta X1 needs `float_date` events in **2015-01→2017-12**. Legacy `share_float_2018plus.parquet` starts **2018-01-02**.

## Pull
- API: Tushare `share_float` via DataHub; monthly `start_date`/`end_date` (= float_date window in practice, same as 2018+ build)
- Window: **201501–201712** (36/36 months, fail=0)
- Raw: `data/v2/tushare_raw/share_float/ann_201501.parquet` … `ann_201712.parquet`
- Rate: workers=2 (staggered vs hk_hold / hsgt_top10 / margin_detail)

## Artifacts
| path | float_date | nrows | notes |
|---|---|---|---|
| `data/v2/share_float/share_float_2015_2017.parquet` | 20150105→20171229 | 42486 | X1 sidecar |
| `data/v2/share_float/share_float_pit.parquet` | 20150105→20261030 | 6449659 | **authoritative PIT** = 2015–17 ∪ 2018+ |
| `data/v2/share_float/share_float_2018plus.parquet` | 2018-01-02→… | 6407173 | **unchanged**; do not use alone for X1 |

## Columns
`ts_code, ann_date, float_date, float_share, float_ratio, holder_name, share_type, available_at, availability_basis, source, quality_status, promotion_approved`

## available_at
- Rule: **`ann_date` 18:00 Asia/Shanghai** (same as V3_UNLOCK_WINDOW_RESID_PREREG / smoke: ann 18:00 → next open tradable)
- If `ann_date` missing/invalid: `available_at` null, `availability_basis=missing_ann` — **no invented early availability**
- Nulls in pit: 0

## X1 coverage confirm
- nrows: **42486**
- float_date: **20150105 → 20171229**
- n_ts_code: 1997; n_float_dates: 720
- by_year: {'2015': 11082, '2016': 13308, '2017': 18096}

## Consumer note
Point UNLOCK-WINDOW-RESID / smoke at `data/v2/share_float/share_float_pit.parquet` (or concat sidecar + 2018plus). Legacy filename kept for non-X1 readers.
