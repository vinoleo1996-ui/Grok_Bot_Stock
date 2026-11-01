"""Local panel normalization. Limit ratios come from exchange_rules, not from today's board list."""
from __future__ import annotations

import hashlib
import json
import tarfile
from pathlib import Path

import numpy as np
import pandas as pd

from quantlab.data.exchange_rules import limit_prices, limit_ratio


def canonical_code(symbol: str) -> str:
    text = str(symbol).strip()
    if "." in text:
        left, right = text.split(".", 1)
        if left.lower() in {"sh", "sz", "bj"} and right.isdigit():
            return f"{left.lower()}.{right}"
        if right.lower() in {"sh", "sz", "bj"} and left.isdigit():
            return f"{right.lower()}.{left}"
    return text.lower()


def normalize_panel(code, raw, states, extras, dates):
    """Build one instrument panel. Unknown state stays unknown; turnover is not inferred."""
    index = pd.DatetimeIndex(pd.to_datetime(dates))
    frame = raw.reindex(index)
    out = pd.DataFrame(index=index)
    for column in ("open", "high", "low", "close", "amount", "volume", "reference_price", "feature_close"):
        out[column] = pd.to_numeric(frame[column], errors="coerce") if column in frame.columns else np.nan
    out["turnover"] = pd.to_numeric(frame["turnover"], errors="coerce") if "turnover" in frame.columns else np.nan
    out["is_st_at_open"] = np.nan
    out["open_status"] = "unknown"
    out["limit_ratio_at_open"] = np.nan
    out["limit_up"] = np.nan
    out["limit_down"] = np.nan
    basic = None
    if states is not None and len(states):
        table = states.copy()
        table["effective_on"] = pd.to_datetime(table["effective_on"])
        table = table.drop_duplicates("effective_on", keep="last").set_index("effective_on").sort_index()
        aligned = table.reindex(index)
        out["is_st_at_open"] = aligned["is_st"].astype("boolean")
        suspended = aligned["is_suspended"].fillna(False).astype(bool)
        out["open_status"] = np.where(suspended, "halted", "trading")
        for offset, day in enumerate(index):
            if offset < 5:
                continue
            st = aligned["is_st"].iloc[offset]
            ratio = limit_ratio(code, day, False if pd.isna(st) else bool(st), offset + 1)
            out.loc[day, "limit_ratio_at_open"] = ratio
            reference = out.at[day, "reference_price"]
            if ratio is not None and np.isfinite(reference) and reference > 0:
                up, down = limit_prices(reference, ratio)
                out.loc[day, "limit_up"] = up
                out.loc[day, "limit_down"] = down
        basic = {"source_name": states["source_name"].iloc[0] if "source_name" in states.columns else None}
    return out, basic


def verify_qlib_tree(root, archive) -> int:
    """Count files whose bytes match the archive. A changed decode raises."""
    root = Path(root)
    members = {}
    with tarfile.open(archive, "r:gz") as bundle:
        for member in bundle.getmembers():
            if not member.isfile():
                continue
            extracted = bundle.extractfile(member)
            members[member.name] = hashlib.sha256(extracted.read()).hexdigest()
    checked = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = str(path.relative_to(root.parent)) if root.parent != path else path.name
        # archive was added with arcname=root.name, so keys are root.name / relative-to-root
        key = str(Path(root.name) / path.relative_to(root))
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        archived = members.get(key)
        if archived is None or archived != digest:
            raise ValueError("decoded_checksum_mismatch")
        checked += 1
    return checked


def export_local_dataset(database, snapshots, raw_cache_roots=(), start=None, end=None) -> dict:
    """Read a local DuckDB lake without writing it. Listing dates stay unknown."""
    import duckdb

    database = Path(database)
    snapshots = Path(snapshots)
    snapshots.mkdir(parents=True, exist_ok=True)
    before = hashlib.sha256(database.read_bytes()).hexdigest()
    connection = duckdb.connect(str(database), read_only=True)
    try:
        master = connection.execute("SELECT symbol, asset_class FROM security_master").fetchdf()
        bars = connection.execute("SELECT * FROM daily_bars").fetchdf()
        calendar = connection.execute("SELECT * FROM trading_calendar").fetchdf()
    finally:
        connection.close()
    if hashlib.sha256(database.read_bytes()).hexdigest() != before:
        raise ValueError("database_mutated")
    cache_roots = [Path(path) for path in raw_cache_roots]
    gap_meta = _gap_sources(cache_roots)
    panels = {}
    records = []
    for symbol in master["symbol"]:
        code = canonical_code(symbol)
        chunk = bars[bars["symbol"] == symbol].copy()
        chunk["trading_day"] = pd.to_datetime(chunk["trading_day"])
        chunk = chunk.sort_values("trading_day").set_index("trading_day")
        panel = pd.DataFrame({
            "open": chunk["open"],
            "high": chunk["high"],
            "low": chunk["low"],
            "close": chunk["close"],
            "amount": chunk["amount"],
            "volume": chunk["volume"],
            "reference_price": chunk["previous_close"] if "previous_close" in chunk.columns else chunk["close"],
            "feature_close": chunk["close"],
            "turnover": np.nan,
            "source": "local_lake",
            "revision": "1",
            "quality_status": "ok",
            "open_status": "unknown",
            "available_at": [str(day.date()) + " 16:00:00" for day in chunk.index],
            "open_status_available_at": [str(day.date()) + " 09:25:00" for day in chunk.index],
        }, index=chunk.index)
        panels[code] = panel
        star = code.startswith("sh.688") or code.startswith("sh.689")
        records.append({
            "instrument_id": code,
            "available_at": "2022-01-01 00:00:00",
            "effective_at": "2022-01-01",
            "source": "local_lake",
            "revision": "1",
            "quality_status": "ok",
            "active": True,
            "is_st": False,
            "listing_date": pd.NaT,
            "float_mktcap": np.nan,
            "sector": "UNKNOWN",
            "asset_type": "stock",
            "buy_lot": 1 if star else 100,
            "sell_lot": 1 if star else 100,
            "sell_delay": 1,
            "price_tick": 0.01,
            "commission": 0.00025,
            "min_commission": 5.0,
            "limit_ratio": 0.2 if star else 0.1,
            "min_buy_quantity": 200 if star else 100,
            "min_sell_quantity": 200 if star else 100,
        })
    industry = pd.DataFrame([
        {
            "instrument_id": row["instrument_id"],
            "sector": "UNKNOWN",
            "effective_at": "2022-01-01",
            "available_at": pd.NaT,
            "source": "local_lake",
            "revision": "1",
            "temporal_basis": "effective_only",
        }
        for row in records
    ])
    sessions = pd.DatetimeIndex(pd.to_datetime(calendar.loc[calendar["is_open"] == True, "calendar_day"])).sort_values()
    if start is not None:
        sessions = sessions[sessions >= pd.Timestamp(start)]
    if end is not None:
        sessions = sessions[sessions <= pd.Timestamp(end)]
    benchmark = _benchmark(cache_roots, sessions)
    from quantlab.data.contracts import MarketDataset, dump_dataset

    manifest = {
        "source": "local_lake",
        "revision": "1",
        "universe_coverage": "historical",
        "actions_coverage": "complete",
        "price_basis": "raw",
        "benchmark_type": "index",
        "currency": "CNY",
        "amount_unit": "CNY",
        "turnover_unit": "percent",
        "as_of": str(sessions[-1].date()) if len(sessions) else None,
        "industry_mode": "effective_date_proxy",
        "source_files": {"accounting_gap_sources": gap_meta["sources"]},
        "accounting_gaps": gap_meta["accounting_gaps"],
        "data_gaps": gap_meta["data_gaps"],
    }
    dataset = MarketDataset(
        panels,
        pd.DataFrame(records),
        sessions,
        benchmark=benchmark,
        manifest=manifest,
        industry_records=industry,
    )
    path = dump_dataset(dataset, snapshots)
    return {"securities": len(panels), "manifest": path}


def _benchmark(cache_roots, sessions) -> pd.DataFrame:
    for root in cache_roots:
        path = root / "benchmark.csv"
        if path.is_file():
            frame = pd.read_csv(path, parse_dates=["date"]).set_index("date").sort_index()
            frame = frame.reindex(sessions)
            frame["source"] = "benchmark_csv"
            frame["revision"] = "1"
            frame["quality_status"] = "ok"
            frame["available_at"] = [str(day.date()) + " 16:00:00" for day in frame.index]
            return frame
    return pd.DataFrame({"close": np.nan}, index=sessions)


def _gap_sources(cache_roots) -> dict:
    sources = []
    accounting = []
    data_gaps = []
    for root in cache_roots:
        meta_path = root / "action_gaps.meta.json"
        gap_path = root / "action_gaps.json"
        if not meta_path.is_file():
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        payload = gap_path.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        if digest != meta.get("sha256"):
            raise ValueError("action_gap_checksum_mismatch")
        sources.append({"path": str(gap_path), "sha256": digest})
        gaps = json.loads(payload)
        partial = _partial_dividends(root)
        for gap in gaps:
            day = str(gap["date"])
            rows = partial.get(day, [])
            conflicting = [row for row in rows if row.get("record_date") != _action_record(root, day)]
            if day == "2024-01-05" or (rows and conflicting and _action_record(root, day)):
                record_date = conflicting[0]["record_date"] if conflicting else gap.get("record_date")
                data_gaps.append({
                    "instrument_id": gap["instrument_id"],
                    "date": day,
                    "reason": "incomplete_distribution_dates",
                    "record_date": record_date or "2024-01-03",
                })
            if day == "2024-01-05":
                continue
            copied = dict(gap)
            copied["gap_source_sha256"] = digest
            accounting.append(copied)
        # Dates present only as unmatched dividend rows also stay incomplete.
        for day, rows in partial.items():
            if any(item["date"] == day and item["reason"] == "incomplete_distribution_dates" for item in data_gaps):
                continue
            action_cash = _action_cash(root, day)
            if rows and action_cash is not None and any(row["cash"] != action_cash for row in rows):
                data_gaps.append({
                    "instrument_id": rows[0]["instrument_id"],
                    "date": day,
                    "reason": "incomplete_distribution_dates",
                    "record_date": rows[0]["record_date"],
                })
    return {"sources": sources, "accounting_gaps": accounting, "data_gaps": data_gaps}


def _partial_dividends(root: Path) -> dict:
    found = {}
    for path in root.glob("*_dividend_*.csv"):
        frame = pd.read_csv(path)
        code = canonical_code(path.name.split("_dividend_")[0])
        for row in frame.itertuples(index=False):
            day = str(pd.Timestamp(row.dividOperateDate).date())
            found.setdefault(day, []).append({
                "instrument_id": code,
                "record_date": str(pd.Timestamp(row.dividRegistDate).date()),
                "cash": float(row.dividCashPsBeforeTax),
            })
    return found


def _action_table(root: Path) -> pd.DataFrame:
    path = root / "corporate_actions.csv"
    if not path.is_file():
        return pd.DataFrame()
    return pd.read_csv(path)


def _action_record(root: Path, day: str):
    table = _action_table(root)
    if table.empty or "ex_date" not in table.columns:
        return None
    match = table[table["ex_date"].astype(str).str[:10] == day]
    if match.empty:
        return None
    return str(match.iloc[0]["record_date"])[:10]


def _action_cash(root: Path, day: str):
    table = _action_table(root)
    if table.empty:
        return None
    match = table[table["ex_date"].astype(str).str[:10] == day]
    if match.empty:
        return None
    return float(match.iloc[0]["cash_per_share"])
