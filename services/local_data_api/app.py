"""QuantLab local read-only data API for Mac via Tailscale.

v1.2.0 — OOM-safe reads: pyarrow filter pushdown on date/symbol; never
full-table to_pandas for large/oom_risk datasets. Partitioned roots supported
when catalog `partitioned_path` exists (hive-style dirs under data/v2_partitioned/).
"""
from __future__ import annotations

import io
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.dataset as ds
import pyarrow.parquet as pq
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response

ROOT = Path("/workspace/QuantLab").resolve()
DATA_ROOT = (ROOT / "data").resolve()
CATALOG_PATH = Path(__file__).resolve().parent / "catalog.json"
SYMBOL_COLS = ("ts_code", "code", "instrument_id")
DATE_CANDIDATES = (
    "trade_date",
    "float_date",
    "end_date",
    "ex_date",
    "in_date",
    "ann_date",
    "list_date",
    "available_at",
)
MAX_LIMIT = 50_000
DEFAULT_LIMIT = 5_000
MAX_EXPORT_ROWS = 5_000_000
# Tables at/above this row count (or catalog oom_risk) require date window.
LARGE_NROWS = 500_000
OOM_NROWS = 2_000_000
DEFAULT_FORCE_WINDOW_DAYS = 30
API_VERSION = "1.2.0"

app = FastAPI(title="QuantLab Local Data API", version=API_VERSION)


def _load_catalog() -> list[dict[str, Any]]:
    with CATALOG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _catalog_by_id() -> dict[str, dict[str, Any]]:
    return {e["id"]: e for e in _load_catalog()}


def _resolve_under_data(rel: str, *, must_exist: bool = True) -> Path:
    rel = rel.lstrip("/")
    if ".." in Path(rel).parts:
        raise HTTPException(status_code=400, detail="path traversal rejected")
    if not rel.startswith("data/"):
        raise HTTPException(status_code=400, detail="path must be under data/")
    full = (ROOT / rel).resolve()
    try:
        full.relative_to(DATA_ROOT)
    except ValueError:
        raise HTTPException(status_code=400, detail="path outside data/")
    if must_exist and not full.exists():
        raise HTTPException(status_code=404, detail=f"path not found: {rel}")
    return full


def _resolve_parquet(rel: str) -> Path:
    full = _resolve_under_data(rel)
    if full.is_dir():
        return full
    if full.suffix != ".parquet":
        raise HTTPException(status_code=400, detail="only parquet allowed")
    if not full.is_file():
        raise HTTPException(status_code=404, detail=f"file not found: {rel}")
    return full


def _get_entry(dataset_id: str) -> dict[str, Any]:
    entry = _catalog_by_id().get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail=f"unknown dataset: {dataset_id}")
    return entry


def _is_oom_risk(entry: dict[str, Any]) -> bool:
    if entry.get("oom_risk"):
        return True
    nrows = int(entry.get("nrows") or 0)
    return nrows >= OOM_NROWS


def _requires_date_window(entry: dict[str, Any]) -> bool:
    if entry.get("require_date_filter"):
        return True
    if _is_oom_risk(entry):
        return True
    return int(entry.get("nrows") or 0) > LARGE_NROWS


def _normalize_ymd(val: Any) -> Optional[str]:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    if isinstance(val, pd.Timestamp):
        return val.strftime("%Y%m%d")
    if isinstance(val, datetime):
        return val.strftime("%Y%m%d")
    s = str(val).strip()
    if not s or s.lower() in ("nan", "nat", "none"):
        return None
    digits = re.sub(r"[^0-9]", "", s)
    if len(digits) >= 8:
        return digits[:8]
    return None


def _parse_filter_date(s: str) -> str:
    s = s.strip()
    digits = re.sub(r"[^0-9]", "", s)
    if len(digits) >= 8:
        return digits[:8]
    raise HTTPException(status_code=400, detail=f"bad date: {s}; use YYYYMMDD")


def _pick_date_col_from_names(names: list[str], preferred: Optional[str]) -> Optional[str]:
    if preferred and preferred in names:
        return preferred
    for c in DATE_CANDIDATES:
        if c in names:
            return c
    return None


def _pick_symbol_col_from_names(names: list[str], preferred: Optional[str] = None) -> Optional[str]:
    if preferred and preferred in names:
        return preferred
    for c in SYMBOL_COLS:
        if c in names:
            return c
    return None


def _pick_date_col(df: pd.DataFrame, preferred: Optional[str]) -> Optional[str]:
    return _pick_date_col_from_names(list(df.columns), preferred)


def _pick_symbol_col(df: pd.DataFrame, preferred: Optional[str] = None) -> Optional[str]:
    return _pick_symbol_col_from_names(list(df.columns), preferred)


def _ymd_to_arrow_scalar(ymd: str, arrow_type: pa.DataType) -> pa.Scalar:
    """Cast YYYYMMDD to a scalar matching the parquet column type."""
    if pa.types.is_timestamp(arrow_type):
        dt = datetime.strptime(ymd, "%Y%m%d")
        unit = arrow_type.unit
        tz = arrow_type.tz
        return pa.scalar(dt, type=pa.timestamp(unit, tz=tz))
    if pa.types.is_date32(arrow_type) or pa.types.is_date64(arrow_type):
        dt = datetime.strptime(ymd, "%Y%m%d").date()
        return pa.scalar(dt, type=arrow_type)
    if pa.types.is_integer(arrow_type):
        return pa.scalar(int(ymd), type=arrow_type)
    # string / large_string / other → compare as YYYYMMDD text
    return pa.scalar(ymd, type=pa.string() if pa.types.is_string(arrow_type) else arrow_type)


def _force_recent_window(entry: dict[str, Any]) -> tuple[str, str, int]:
    """Derive [start,end] from catalog date_max when client omits dates."""
    days = int(entry.get("force_window_days") or DEFAULT_FORCE_WINDOW_DAYS)
    raw_max = entry.get("date_max")
    if not raw_max:
        raise HTTPException(
            status_code=400,
            detail=(
                "large/oom dataset requires start/end (and/or symbol); "
                "catalog has no date_max to auto-window"
            ),
        )
    end = _parse_filter_date(str(raw_max))
    end_dt = datetime.strptime(end, "%Y%m%d")
    start = (end_dt - timedelta(days=days)).strftime("%Y%m%d")
    return start, end, days


def _open_dataset(entry: dict[str, Any]) -> tuple[ds.Dataset, str, bool]:
    """Open single-file or hive-partitioned dataset. Prefer partitioned_path if live.

    Partition dirs use ``ym=YYYYMM`` (not the date column name) so hive keys do not
    collide with in-file trade_date/float_date types.
    """
    part_rel = entry.get("partitioned_path")
    if part_rel:
        try:
            part_path = _resolve_under_data(part_rel, must_exist=False)
            if part_path.is_dir() and any(part_path.rglob("*.parquet")):
                # Explicit ym:string hive key — avoids merging ym int with date col types.
                partitioning = ds.HivePartitioning(pa.schema([("ym", pa.string())]))
                try:
                    dataset = ds.dataset(
                        str(part_path), format="parquet", partitioning=partitioning
                    )
                    return dataset, part_rel, True
                except Exception:
                    # Incomplete/legacy layout → fall back to flat source
                    pass
        except HTTPException:
            pass
    path = _resolve_parquet(entry["path"])
    dataset = ds.dataset(str(path), format="parquet")
    return dataset, entry["path"], False


def _build_filter(
    schema: pa.Schema,
    date_col: Optional[str],
    start: Optional[str],
    end: Optional[str],
    symbol: Optional[str],
    symbol_col: Optional[str],
) -> Optional[ds.Expression]:
    expr: Optional[ds.Expression] = None

    def _and(e: ds.Expression) -> None:
        nonlocal expr
        expr = e if expr is None else (expr & e)

    if date_col and (start or end):
        if date_col not in schema.names:
            raise HTTPException(status_code=400, detail=f"date_col {date_col} missing in schema")
        arrow_type = schema.field(date_col).type
        field = ds.field(date_col)
        if start:
            s = _parse_filter_date(start)
            _and(field >= _ymd_to_arrow_scalar(s, arrow_type))
        if end:
            e = _parse_filter_date(end)
            # inclusive end-of-day for timestamps: use next day exclusive when timestamp
            if pa.types.is_timestamp(arrow_type):
                end_dt = datetime.strptime(e, "%Y%m%d") + timedelta(days=1)
                unit = arrow_type.unit
                tz = arrow_type.tz
                _and(field < pa.scalar(end_dt, type=pa.timestamp(unit, tz=tz)))
            else:
                _and(field <= _ymd_to_arrow_scalar(e, arrow_type))

    if symbol and symbol_col:
        if symbol_col not in schema.names:
            raise HTTPException(status_code=400, detail=f"symbol_col {symbol_col} missing")
        want = list({symbol, symbol.upper(), symbol.lower()})
        _and(ds.field(symbol_col).isin(want))

    return expr


def _scan_to_table(
    entry: dict[str, Any],
    start: Optional[str],
    end: Optional[str],
    symbol: Optional[str],
    *,
    max_rows: Optional[int] = None,
) -> tuple[pa.Table, dict[str, Any]]:
    """Filter at scan time with pyarrow; never load full large tables into pandas first."""
    dataset, resolved_path, used_partitioned = _open_dataset(entry)
    names = list(dataset.schema.names)
    date_col = _pick_date_col_from_names(names, entry.get("date_col"))
    symbol_col = _pick_symbol_col_from_names(names, entry.get("symbol_col"))

    auto_window = False
    force_days = None
    effective_start, effective_end = start, end

    needs_window = _requires_date_window(entry)
    if needs_window and not (effective_start or effective_end or symbol):
        # Force recent N-day window rather than OOM full scan.
        effective_start, effective_end, force_days = _force_recent_window(entry)
        auto_window = True

    if (effective_start or effective_end) and not date_col:
        raise HTTPException(status_code=400, detail="no date column to filter")

    filt = _build_filter(
        dataset.schema,
        date_col,
        effective_start,
        effective_end,
        symbol,
        symbol_col,
    )

    scanner_kwargs: dict[str, Any] = {"filter": filt} if filt is not None else {}
    if max_rows is not None:
        # Still apply filter; head after scan via slice — for query path we scan then truncate.
        pass

    table = dataset.to_table(**scanner_kwargs)

    meta = {
        "date_col": date_col,
        "symbol_col": symbol_col,
        "resolved_path": resolved_path,
        "used_partitioned": used_partitioned,
        "filters": {
            "start": effective_start,
            "end": effective_end,
            "symbol": symbol,
            "auto_window": auto_window,
            "force_window_days": force_days,
        },
        "scanned_rows": table.num_rows,
    }
    return table, meta


def _df_to_jsonable(df: pd.DataFrame) -> list[dict[str, Any]]:
    out = df.copy()
    for c in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[c]):
            out[c] = out[c].astype(str)
        elif out[c].dtype == object:
            out[c] = out[c].map(
                lambda x: x.isoformat() if isinstance(x, (datetime, pd.Timestamp)) else x
            )
    return json.loads(out.to_json(orient="records", date_format="iso", default_handler=str))


def _catalog_public(e: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": e["id"],
        "path": e["path"],
        "partitioned_path": e.get("partitioned_path"),
        "date_col": e.get("date_col"),
        "symbol_col": e.get("symbol_col"),
        "date_min": e.get("date_min"),
        "date_max": e.get("date_max"),
        "nrows": e.get("nrows"),
        "oom_risk": bool(e.get("oom_risk") or _is_oom_risk(e)),
        "require_date_filter": bool(e.get("require_date_filter") or _requires_date_window(e)),
        "force_window_days": e.get("force_window_days") or DEFAULT_FORCE_WINDOW_DAYS,
        "promotion_approved": bool(e.get("promotion_approved", False)),
        "coverage_caveat": e.get("coverage_caveat"),
        "note": e.get("note"),
    }


def _filter_meta_headers(meta: dict[str, Any]) -> dict[str, str]:
    f = meta.get("filters") or {}
    return {
        "X-Date-Col": meta.get("date_col") or "",
        "X-Filter-Start": str(f.get("start") or ""),
        "X-Filter-End": str(f.get("end") or ""),
        "X-Auto-Window": "1" if f.get("auto_window") else "0",
        "X-Force-Window-Days": str(f.get("force_window_days") or ""),
        "X-Used-Partitioned": "1" if meta.get("used_partitioned") else "0",
        "X-Resolved-Path": str(meta.get("resolved_path") or ""),
        "X-Scanned-Rows": str(meta.get("scanned_rows") or 0),
    }


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "ts": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "root": str(ROOT),
        "version": API_VERSION,
        "catalog_n": len(_load_catalog()),
        "query_limit_default": DEFAULT_LIMIT,
        "query_limit_max": MAX_LIMIT,
        "export_rows_max": MAX_EXPORT_ROWS,
        "oom_safe_read": True,
        "default_force_window_days": DEFAULT_FORCE_WINDOW_DAYS,
    }


@app.get("/datasets")
def list_datasets() -> list[dict[str, Any]]:
    return [_catalog_public(e) for e in _load_catalog()]


@app.get("/datasets/{dataset_id}/schema")
def dataset_schema(dataset_id: str) -> dict[str, Any]:
    entry = _get_entry(dataset_id)
    dataset, resolved_path, used_partitioned = _open_dataset(entry)
    cols = [{"name": f.name, "dtype": str(f.type)} for f in dataset.schema]
    pub = _catalog_public(entry)
    pub.update(
        {
            "nrows": entry.get("nrows"),
            "columns": cols,
            "resolved_path": resolved_path,
            "used_partitioned": used_partitioned,
        }
    )
    return pub


@app.get("/datasets/{dataset_id}/head")
def dataset_head(
    dataset_id: str,
    n: int = Query(20, ge=1, le=500),
) -> dict[str, Any]:
    """First n rows without full-table load (iter_batches / scanner)."""
    entry = _get_entry(dataset_id)
    path = _resolve_parquet(entry["path"])
    rows_out: list[dict[str, Any]] = []
    if path.is_dir():
        dataset = ds.dataset(str(path), format="parquet", partitioning=ds.HivePartitioning.discover())
        table = dataset.head(n)
        df = table.to_pandas()
        rows_out = _df_to_jsonable(df)
    else:
        pf = pq.ParquetFile(path)
        batches = []
        taken = 0
        for batch in pf.iter_batches(batch_size=min(1024, n)):
            need = n - taken
            if batch.num_rows > need:
                batch = batch.slice(0, need)
            batches.append(batch)
            taken += batch.num_rows
            if taken >= n:
                break
        if batches:
            table = pa.Table.from_batches(batches)
            rows_out = _df_to_jsonable(table.to_pandas())
    return {
        "id": dataset_id,
        "n": len(rows_out),
        "oom_safe": True,
        "rows": rows_out,
    }


@app.get("/datasets/{dataset_id}/query")
def dataset_query(
    dataset_id: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    symbol: Optional[str] = None,
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    format: str = Query("json", pattern="^(json|csv)$"),
):
    entry = _get_entry(dataset_id)
    table, meta = _scan_to_table(entry, start, end, symbol)
    truncated = table.num_rows > limit
    if truncated:
        table = table.slice(0, limit)
    df = table.to_pandas()

    headers = _filter_meta_headers(meta)
    headers.update(
        {
            "X-Row-Count": str(len(df)),
            "X-Truncated": "1" if truncated else "0",
            "X-Dataset-Id": dataset_id,
        }
    )

    if format == "csv":
        return Response(
            content=df.to_csv(index=False),
            media_type="text/csv",
            headers=headers,
        )

    return {
        "id": dataset_id,
        "path": entry["path"],
        "resolved_path": meta.get("resolved_path"),
        "used_partitioned": meta.get("used_partitioned"),
        "date_col": meta.get("date_col"),
        "symbol_col": meta.get("symbol_col") or entry.get("symbol_col"),
        "promotion_approved": bool(entry.get("promotion_approved", False)),
        "filters": meta.get("filters"),
        "oom_safe_read": True,
        "scanned_rows": meta.get("scanned_rows"),
        "returned": len(df),
        "truncated": truncated,
        "limit": limit,
        "limit_max": MAX_LIMIT,
        "rows": _df_to_jsonable(df),
    }


def _export_parquet_bytes(
    dataset_id: str,
    start: Optional[str],
    end: Optional[str],
    symbol: Optional[str],
) -> Response:
    entry = _get_entry(dataset_id)
    # Date window always required for large/oom; auto-window if omitted.
    table, meta = _scan_to_table(entry, start, end, symbol)
    n = table.num_rows
    if n > MAX_EXPORT_ROWS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"export would return {n} rows > max {MAX_EXPORT_ROWS}; "
                "narrow start/end/symbol"
            ),
        )

    buf = io.BytesIO()
    pq.write_table(table, buf, compression="zstd")
    data = buf.getvalue()
    f = meta.get("filters") or {}
    fname = f"{dataset_id}"
    if f.get("start") or f.get("end"):
        fname += f"_{f.get('start') or 'min'}_{f.get('end') or 'max'}"
    if symbol:
        fname += f"_{symbol.replace('.', '_')}"
    fname += ".parquet"

    headers = _filter_meta_headers(meta)
    headers.update(
        {
            "Content-Disposition": f'attachment; filename="{fname}"',
            "X-Row-Count": str(n),
            "X-Dataset-Id": dataset_id,
            "X-Byte-Length": str(len(data)),
        }
    )
    return Response(
        content=data,
        media_type="application/vnd.apache.parquet",
        headers=headers,
    )


@app.get("/datasets/{dataset_id}/export.parquet")
def dataset_export_parquet(
    dataset_id: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    symbol: Optional[str] = None,
):
    """Download filtered rows as parquet (filter pushdown; no full-table pandas)."""
    return _export_parquet_bytes(dataset_id, start, end, symbol)


@app.get("/datasets/{dataset_id}/export")
def dataset_export(
    dataset_id: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    symbol: Optional[str] = None,
    format: str = Query("parquet", pattern="^(parquet)$"),
):
    if format != "parquet":
        raise HTTPException(status_code=400, detail="only format=parquet supported")
    return _export_parquet_bytes(dataset_id, start, end, symbol)


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "service": "QuantLab local data API",
        "readonly": True,
        "version": API_VERSION,
        "query_limit_default": DEFAULT_LIMIT,
        "query_limit_max": MAX_LIMIT,
        "export_rows_max": MAX_EXPORT_ROWS,
        "oom_safe_read": True,
        "default_force_window_days": DEFAULT_FORCE_WINDOW_DAYS,
        "endpoints": [
            "GET /health",
            "GET /datasets",
            "GET /datasets/{id}/schema",
            "GET /datasets/{id}/head?n=20",
            "GET /datasets/{id}/query?start=&end=&symbol=&limit=5000&format=json|csv",
            "GET /datasets/{id}/export.parquet?start=&end=&symbol=",
            "GET /datasets/{id}/export?start=&end=&symbol=&format=parquet",
        ],
        "notes": [
            "v1.2.0: pyarrow date/symbol filter pushdown — no full-table to_pandas on large sets",
            "oom_risk / nrows>5e5: missing start/end auto-windows to last force_window_days (default 30) vs catalog date_max; X-Auto-Window=1",
            "prefer partitioned_path under data/v2_partitioned/ when present (see docs/v2/API_DATE_FILTER_PARTITION_PLAN_ZH.md)",
            "query limit default=5000 max=50000; use /export.parquet for bulk pulls",
            "date_col varies: trade_date | float_date | end_date | ex_date | in_date",
            "Do not restart this service unless Leo explicitly says 现在重启",
        ],
    }
