"""Point-in-time industry membership for the cash-ledger research path."""
from __future__ import annotations

import pandas as pd

from quantlab.data.contracts import decision_time, timestamp


def _day_stamp(day) -> pd.Timestamp:
    stamp = timestamp(day)
    return stamp.normalize()


def resolve_industries(dataset, day, mode=None) -> pd.DataFrame:
    """Sector known on ``day``. verified_pit requires a publication time."""
    records = getattr(dataset, "industry_records", None)
    columns = ["instrument_id", "sector", "effective_at", "available_at", "source", "revision", "temporal_basis"]
    if records is None or len(records) == 0:
        return pd.DataFrame(columns=columns).set_index("instrument_id")
    chosen_mode = mode or dataset.manifest.get("industry_mode", "verified_pit")
    cutoff = decision_time(day)
    day_end = _day_stamp(day)
    kept = []
    work = records.copy()
    for instrument_id, group in work.groupby("instrument_id", sort=False):
        rows = group.copy()
        effective = rows["effective_at"].map(lambda value: timestamp(value) if pd.notna(value) else pd.NaT)
        known_effective = effective.map(lambda value: pd.isna(value) or value <= cutoff)
        if chosen_mode == "verified_pit":
            available = rows["available_at"].map(lambda value: timestamp(value) if pd.notna(value) else pd.NaT)
            published = available.map(lambda value: pd.notna(value) and value <= cutoff)
            rows = rows.loc[published.to_numpy() & known_effective.to_numpy()]
        else:
            on_or_before = effective.map(lambda value: pd.notna(value) and value.normalize() <= day_end)
            rows = rows.loc[on_or_before.to_numpy()]
        if rows.empty:
            continue
        rows = rows.assign(_effective=effective.loc[rows.index])
        revision = rows["revision"] if "revision" in rows.columns else ""
        rows = rows.assign(_revision=revision).sort_values(["_effective", "_revision"])
        kept.append(rows.iloc[-1].drop(labels=["_effective", "_revision"]))
    if not kept:
        return pd.DataFrame(columns=columns).set_index("instrument_id")
    out = pd.DataFrame(kept)
    return out.set_index("instrument_id")
