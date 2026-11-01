# QuantLab Local Data API

Read-only FastAPI over `/workspace/QuantLab/data/**/*.parquet` for Mac access via Tailscale.

## URLs

| Where | Base |
|---|---|
| On box | `http://127.0.0.1:8787` |
| Mac (Tailscale) | `http://100.124.230.108:8787` |

Box hostname: `grok-bot`. Mac must be on the **same Tailscale account** and online (`tailscale status` shows `100.124.230.108`).

## Query limits

| Param | Default | Max |
|---|---|---|
| `/query` `limit` | **5000** | **50000** |
| `/export` / `/export.parquet` | no JSON wall | **5_000_000** rows (memory safety) |

Large / `oom_risk` tables (Leo five: daily_basic_full, float_mktcap, ep_pit_daily, margin_detail, share_float_pit):
- **v1.2.0** reads with **pyarrow filter pushdown** (no full-table `to_pandas` before filter).
- Missing `start`/`end` → auto-window last `force_window_days` (default 30; share_float 120) vs catalog `date_max`; response sets `filters.auto_window` and `X-Auto-Window: 1`.
- Prefer hive partitions under `data/v2_partitioned/` when present (`partitioned_path` in catalog).
- See `docs/v2/API_DATE_FILTER_PARTITION_PLAN_ZH.md`. **Do not restart 8787 unless Leo says 现在重启.**

For bulk multi-year pulls, prefer **`/export.parquet`** — avoids JSON serialize cost and the 50k row ceiling.

## Quick curl (from Mac)

```bash
# health (also returns query_limit_default / query_limit_max)
curl http://100.124.230.108:8787/health

# catalog with date_col, symbol_col, promotion_approved, coverage_caveat
curl http://100.124.230.108:8787/datasets

curl 'http://100.124.230.108:8787/datasets/moneyflow_hsgt/schema'

# JSON query (default limit=5000, max=50000)
curl 'http://100.124.230.108:8787/datasets/moneyflow_hsgt/query?start=20240101&end=20240131&limit=100'

# CSV
curl 'http://100.124.230.108:8787/datasets/top_list/query?start=20200101&end=20200131&symbol=000001.SZ&limit=500&format=csv' -o top_list.csv

# Parquet bulk export (no 50k wall) — preferred for Mac local cache
curl -OJ 'http://100.124.230.108:8787/datasets/moneyflow_hsgt/export.parquet?start=20240101&end=20240131'
# alias:
curl -OJ 'http://100.124.230.108:8787/datasets/moneyflow_hsgt/export?start=20240101&end=20240131&format=parquet'
```

## Endpoints

- `GET /health` — ok + `query_limit_default` / `query_limit_max` / `export_rows_max`
- `GET /datasets` — catalog (`id`, `path`, `date_col`, `symbol_col`, `date_min`/`date_max`, `nrows`, `promotion_approved`, `coverage_caveat`, `note`)
- `GET /datasets/{id}/schema` — columns + catalog metadata
- `GET /datasets/{id}/head?n=20` — first n rows
- `GET /datasets/{id}/query?start=&end=&symbol=&limit=5000&format=json|csv`
  - `symbol` matches catalog `symbol_col`, else first of `ts_code` / `code` / `instrument_id`
  - `start`/`end`: `YYYYMMDD` against the dataset **date_col** (not always `trade_date`)
  - default `limit=5000`, max `50000`
- `GET /datasets/{id}/export.parquet?start=&end=&symbol=` — download parquet attachment
- `GET /datasets/{id}/export?format=parquet&...` — same as above

## Catalog gotchas (Leo notes)

| Dataset | date filter col | symbol col | caveat |
|---|---|---|---|
| most | `trade_date` | `ts_code` | — |
| `financials_pit` | **`end_date`** (report period) | `ts_code` | promotion PASS |
| `dividend_tushare` | **`ex_date`** | `ts_code` | promotion PASS |
| `share_float_pit` | **`float_date`** | `ts_code` | research |
| `sw_l1_members` | **`in_date`** | **`instrument_id`** | promotion PASS |
| `float_mktcap` | `trade_date` | **`instrument_id`** | promotion PASS |
| `hsgt_top10` | `trade_date` | `ts_code` | ends **20240710** |
| `hk_hold_ashare` | `trade_date` | `ts_code` | daily ~to **20240816**, then quarter-end points |

Only `float_mktcap`, `financials_pit`, `sw_l1_members`, `dividend_tushare` have `promotion_approved=true`. Others are research-grade.

`etf_share_flow_*` have `available_at` — signal must asof; do not use same-day `trade_date`.

## Ops (on box)

```bash
# start
cd /workspace/QuantLab
mkdir -p logs
.venv-data-api/bin/uvicorn services.local_data_api.app:app \
  --host 0.0.0.0 --port 8787 \
  > logs/local_data_api.log 2>&1 &
echo $! > services/local_data_api/uvicorn.pid

# stop / restart
kill $(cat services/local_data_api/uvicorn.pid)
# then start again
```

Catalog: `services/local_data_api/catalog.json`. No writes/deletes; paths confined under `data/`.
