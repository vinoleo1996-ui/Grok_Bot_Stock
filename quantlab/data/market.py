"""Research panels and the liquidity universe used by the cash ledger."""
from __future__ import annotations

import numpy as np
import pandas as pd

from quantlab.data.contracts import asof_records, decision_time
from quantlab.data.industry import resolve_industries


def panels_for_research(dataset):
    """Close, amount, and turnover aligned through manifest as_of.

    A historical adjustment snapshot replaces the feature price only. Raw close
    on the stored panel is left unchanged.
    """
    as_of = dataset.manifest.get("as_of")
    limit = pd.Timestamp(as_of) if as_of else None
    use_feature = dataset.manifest.get("feature_price_basis") == "historical_adjustment_snapshot"
    closes, amounts, turnovers = {}, {}, {}
    for code, panel in dataset.panels.items():
        frame = panel
        if limit is not None:
            frame = frame.loc[:limit]
        price = frame["feature_close"] if use_feature and "feature_close" in frame.columns else frame["close"]
        closes[code] = price
        amounts[code] = frame["amount"] if "amount" in frame.columns else pd.Series(np.nan, index=frame.index)
        turnovers[code] = frame["turnover"] if "turnover" in frame.columns else pd.Series(np.nan, index=frame.index)
    close = pd.DataFrame(closes).sort_index()
    amount = pd.DataFrame(amounts).reindex(close.index)
    turnover = pd.DataFrame(turnovers).reindex(close.index)
    return close, amount, turnover


def _listing_start(value, calendar: pd.DatetimeIndex):
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    try:
        stamp = pd.Timestamp(value)
    except (ValueError, TypeError):
        return "invalid"
    if pd.isna(stamp):
        return "invalid"
    if stamp.tzinfo is not None:
        stamp = stamp.tz_convert("Asia/Shanghai").tz_localize(None)
    if stamp != stamp.normalize():
        return int(calendar.searchsorted(stamp, side="right"))
    return int(calendar.searchsorted(stamp.normalize(), side="left"))


def _observation_age(panel, start, day) -> int:
    if panel is None or "close" not in panel.columns:
        return 0
    window = panel.loc[(panel.index >= pd.Timestamp(start)) & (panel.index <= pd.Timestamp(day)), "close"]
    return int(window.notna().sum())


def universe_at(dataset, day, amount, cfg):
    """Eligible instrument ids and the as-of record used for that session."""
    cutoff = decision_time(day)
    records = asof_records(dataset.instruments, cutoff)
    if records.empty:
        return [], records
    records = records.copy()
    day = pd.Timestamp(day)
    calendar = pd.DatetimeIndex(dataset.calendar)
    position = int(calendar.searchsorted(day))
    industries = resolve_industries(dataset, day)
    sectors = []
    for instrument_id in records.index:
        if instrument_id in industries.index and pd.notna(industries.loc[instrument_id].get("sector")):
            sectors.append(industries.loc[instrument_id]["sector"])
        else:
            sectors.append("UNKNOWN")
    records["sector"] = sectors
    flags = []
    for instrument_id, row in records.iterrows():
        panel = dataset.panels.get(instrument_id)
        daily = row.get("state_basis") == "daily_observation_required"
        eligible_row = bool(row.get("active", False)) and str(row.get("quality_status", "ok")) == "ok" and panel is not None
        value = row.get("is_st", False)
        if daily and eligible_row and day in panel.index and "is_st_at_open" in panel.columns:
            value = panel.at[day, "is_st_at_open"]
        if value is None or (isinstance(value, float) and np.isnan(value)):
            flags.append(np.nan)
        else:
            try:
                if pd.isna(value):
                    flags.append(np.nan)
                else:
                    flags.append(bool(value))
            except TypeError:
                flags.append(bool(value))
    records["is_st"] = pd.Series(flags, index=records.index, dtype=object)
    minimum_days = int(cfg.universe.a_min_listing_days)
    minimum_amount = float(cfg.universe.a_min_avg_amount_wan) * 10_000.0
    history = amount.loc[:day].tail(20) if amount is not None and len(amount) else None
    selected = []
    for instrument_id, row in records.iterrows():
        panel = dataset.panels.get(instrument_id)
        if not bool(row.get("active", False)):
            continue
        if str(row.get("quality_status", "ok")) != "ok":
            continue
        if panel is None or day not in panel.index or not np.isfinite(panel.at[day, "close"]):
            continue
        st = records.at[instrument_id, "is_st"]
        if st is True or (isinstance(st, float) and np.isnan(st)) or pd.isna(st):
            continue
        if cfg.universe.a_exclude_st and st is True:
            continue
        listing = _listing_start(row.get("listing_date"), calendar)
        if listing == "invalid":
            continue
        if listing is None:
            start = row.get("observation_start", calendar[0] if len(calendar) else day)
            age = _observation_age(panel, start, day)
        else:
            if listing > position:
                continue
            age = position - listing + 1
        if age < minimum_days:
            continue
        if cfg.research.universe_mode == "pit_cap":
            cap = row.get("float_mktcap", np.nan)
            if not np.isfinite(cap) or cap < cfg.universe.a_min_mktcap_yi * 1e8:
                continue
        if history is None or instrument_id not in history.columns:
            continue
        window = pd.to_numeric(history[instrument_id], errors="coerce")
        if window.mean() < minimum_amount:
            continue
        selected.append(instrument_id)
    return sorted(selected), records


def exposure_matrix(dataset, day, records, codes, as_of=None) -> pd.DataFrame:
    """One-hot sector rows for the codes. Industry resolution wins over the record sector."""
    industries = resolve_industries(dataset, day)
    sectors = {}
    for code in codes:
        if code in industries.index and pd.notna(industries.loc[code].get("sector")):
            sectors[code] = industries.loc[code]["sector"]
        elif records is not None and code in getattr(records, "index", []) and "sector" in records.columns and pd.notna(records.loc[code].get("sector")):
            sectors[code] = records.loc[code]["sector"]
        else:
            sectors[code] = "UNKNOWN"
    names = sorted(set(sectors.values()))
    frame = pd.DataFrame(0.0, index=names, columns=list(codes))
    for code, sector in sectors.items():
        frame.loc[sector, code] = 1.0
    return frame
