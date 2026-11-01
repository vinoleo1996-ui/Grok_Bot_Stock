"""Point-in-time / as_of guards for text, news, and embedding readers.

Adapted from TradingAgents ``dataflows/date_window.py`` ideas (as_of clamp,
in_window, coverage_gap, withhold live-only profiles) for QuantLab A-share
intel loaders. No vendor of TradingAgents code; research-grade only.

Rules:
- Tool / reader end dates never exceed the query ``trade_session`` / decision ts.
- Rows with ``available_at`` strictly after the decision are look-ahead → drop
  or raise (strict mode).
- Undated text is refused in historical runs (cannot prove it is not future).
- A feed that cannot observe a window returns a ``coverage_gap`` string in
  attrs / meta — never claim "no news" from an unobserved window.
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Any, Mapping, Sequence

import pandas as pd

PROMOTION_APPROVED = False

# Shanghai end-of-day research cutoff used when only a calendar session is known.
_DEFAULT_SESSION_CUTOFF = time(18, 0, 0)


def to_naive_ts(value: Any) -> pd.Timestamp:
    """Parse to naive Timestamp (drop tzinfo; wall clock kept as-is, no inventing offsets)."""
    ts = pd.Timestamp(value)
    if getattr(ts, "tz", None) is not None or ts.tzinfo is not None:
        try:
            ts = ts.tz_localize(None)
        except TypeError:
            ts = ts.tz_convert("UTC").tz_localize(None)
    return ts


def session_to_decision_ts(
    trade_session: date | datetime | str | pd.Timestamp,
    *,
    cutoff: time = _DEFAULT_SESSION_CUTOFF,
) -> datetime:
    """Map a calendar session to a decision datetime (default 18:00 wall)."""
    if isinstance(trade_session, datetime) and not isinstance(trade_session, pd.Timestamp):
        return trade_session.replace(tzinfo=None) if trade_session.tzinfo else trade_session
    ts = to_naive_ts(trade_session)
    d = ts.date()
    if isinstance(trade_session, datetime) or (
        isinstance(trade_session, pd.Timestamp) and (ts.hour or ts.minute or ts.second)
    ):
        return ts.to_pydatetime()
    return datetime.combine(d, cutoff)


def as_of(
    requested: date | datetime | str | None,
    trade_session: date | datetime | str,
) -> date:
    """Clamp a requested date so it never exceeds the run's trade session."""
    trade_d = to_naive_ts(trade_session).date()
    if requested is None or requested == "":
        return trade_d
    req_d = to_naive_ts(requested).date()
    return req_d if req_d <= trade_d else trade_d


def as_of_window(
    start: date | datetime | str,
    end: date | datetime | str,
    trade_session: date | datetime | str,
) -> tuple[date, date]:
    """Clamp ``[start, end]`` so ``end`` never exceeds ``trade_session``.

    If the whole window sits after the trade session, shift it back preserving
    length (TradingAgents behaviour), so callers still get a comparable span.
    """
    start_d = to_naive_ts(start).date()
    old_end = to_naive_ts(end).date()
    end_d = as_of(end, trade_session)
    if end_d == old_end or start_d <= end_d:
        return start_d, end_d
    span = (old_end - start_d).days if old_end >= start_d else 0
    return end_d - timedelta(days=span), end_d


def in_window(
    available_at: datetime | date | str | pd.Timestamp | None,
    start: datetime | date | str,
    end: datetime | date | str,
    *,
    allow_undated_if_live: bool = False,
) -> bool:
    """Whether an item's available_at falls in ``[start, end]`` (inclusive end-of-day).

    ``available_at`` None (undated): False unless ``allow_undated_if_live`` and
    ``end`` reaches today — historical backtests must not keep undated text.
    """
    end_ts = to_naive_ts(end)
    # Inclusive through end calendar day
    end_exclusive = end_ts.normalize() + pd.Timedelta(days=1)
    start_ts = to_naive_ts(start)
    if available_at is None or (isinstance(available_at, float) and pd.isna(available_at)):
        if not allow_undated_if_live:
            return False
        today = pd.Timestamp(date.today())
        return end_ts.normalize() >= today - pd.Timedelta(days=1)
    pub = to_naive_ts(available_at)
    return start_ts <= pub < end_exclusive


def coverage_gap(
    *,
    observed_available_ats: Sequence[Any],
    start: date | datetime | str,
    end: date | datetime | str,
    source: str,
    subject: str = "messages",
) -> str | None:
    """Return a gap notice when the feed cannot claim absence over the window.

    Empty result + gap string ⇒ "unavailable", not "no news that day".
    """
    start_d = to_naive_ts(start).date()
    end_d = to_naive_ts(end).date()
    today = date.today()
    if end_d > today:
        return (
            f"<{source} unavailable for {start_d}..{end_d}: "
            f"the window extends past today, so this is not an absence of {subject}>"
        )
    dated = [to_naive_ts(x) for x in observed_available_ats if x is not None and not (isinstance(x, float) and pd.isna(x))]
    if not dated:
        # No dated coverage evidence at all → cannot prove observation
        return (
            f"<{source} unavailable for {start_d}..{end_d}: "
            f"no dated coverage evidence, so this is not an absence of {subject}>"
        )
    oldest = min(dated).date()
    if oldest > start_d:
        return (
            f"<{source} unavailable for {start_d}..{end_d}: "
            f"it only serves items from {oldest} onward, so this is not an absence of {subject}>"
        )
    return None


def withhold_live_only(
    trade_session: date | datetime | str | None,
    *,
    label: str,
    kind: str = "live_profile",
) -> str | None:
    """Notice when a live-only feed would leak post-decision info into a past run."""
    if trade_session is None:
        return None
    trade_d = to_naive_ts(trade_session).date()
    if trade_d >= date.today():
        return None
    return (
        f"# {kind} withheld for {label}\n"
        f"# Point-in-time as of: {trade_d}\n\n"
        f"This feed has no historical vintage. Serving it into a {trade_d} run "
        f"would put post-decision information into the analysis."
    )


def assert_available_at_le_decision(
    row: Mapping[str, Any],
    decision_ts: datetime | date | str | pd.Timestamp,
    *,
    field: str = "available_at",
) -> None:
    """Raise ``ValueError`` if row[field] is missing or strictly after decision_ts."""
    avail = row.get(field)
    if avail is None or (isinstance(avail, float) and pd.isna(avail)):
        raise ValueError(f"message_missing_{field}")
    avail_ts = to_naive_ts(avail)
    dec_ts = to_naive_ts(decision_ts)
    if isinstance(decision_ts, date) and not isinstance(decision_ts, datetime):
        dec_ts = to_naive_ts(session_to_decision_ts(decision_ts))
    if avail_ts > dec_ts:
        raise ValueError(
            f"pit_lookahead: {field}={avail_ts!r} > decision_ts={dec_ts!r}"
        )


def filter_frame_asof(
    df: pd.DataFrame,
    *,
    trade_session: date | datetime | str | None,
    available_at_field: str = "available_at",
    decision_ts: datetime | None = None,
    strict: bool = False,
) -> pd.DataFrame:
    """Drop (or raise on) rows with available_at after the decision / session cutoff.

    If ``trade_session`` and ``decision_ts`` are both None, returns ``df`` unchanged
    (caller opted out of as_of filtering).
    """
    if trade_session is None and decision_ts is None:
        return df
    if df is None or df.empty:
        return df
    if available_at_field not in df.columns:
        if strict:
            raise ValueError(f"asof_guard_missing_column:{available_at_field}")
        out = df.copy()
        out.attrs = dict(getattr(df, "attrs", {}) or {})
        out.attrs["asof_guard"] = "skipped_missing_available_at"
        out.attrs["promotion_approved"] = False
        return out

    dec = decision_ts or session_to_decision_ts(trade_session)  # type: ignore[arg-type]
    dec_ts = to_naive_ts(dec)
    ts = pd.to_datetime(df[available_at_field], errors="coerce")
    # Compare as naive wall clocks (drop tz without shifting when possible)
    if getattr(ts.dt, "tz", None) is not None:
        try:
            ts = ts.dt.tz_localize(None)
        except TypeError:
            ts = ts.dt.tz_convert("UTC").tz_localize(None)

    future_mask = ts > dec_ts
    if strict and bool(future_mask.any()):
        n = int(future_mask.sum())
        raise ValueError(f"pit_lookahead_rows:{n}_after_{dec_ts.isoformat()}")

    kept = df.loc[~future_mask & ts.notna()].copy()
    # Also drop NaT available_at in historical mode (undated = refuse)
    attrs = dict(getattr(df, "attrs", {}) or {})
    attrs["asof_decision_ts"] = dec_ts.isoformat()
    attrs["asof_dropped_future"] = int(future_mask.sum())
    attrs["asof_dropped_undated"] = int(ts.isna().sum())
    attrs["promotion_approved"] = False
    if trade_session is not None:
        attrs["asof_trade_session"] = str(to_naive_ts(trade_session).date())
    kept.attrs.update(attrs)
    return kept.reset_index(drop=True)


def annotate_coverage_gap(
    df: pd.DataFrame,
    *,
    start: date | datetime | str | None,
    end: date | datetime | str | None,
    source: str,
    available_at_field: str = "available_at",
    subject: str = "messages",
) -> pd.DataFrame:
    """Attach coverage_gap string to attrs when the window is unobserved."""
    out = df if df is None else df.copy()
    if out is None:
        out = pd.DataFrame()
    attrs = dict(getattr(out, "attrs", {}) or {})
    if start is None or end is None:
        attrs["coverage_gap"] = None
        out.attrs.update(attrs)
        return out
    observed: list[Any] = []
    if available_at_field in out.columns and not out.empty:
        observed = list(out[available_at_field].tolist())
    gap = coverage_gap(
        observed_available_ats=observed,
        start=start,
        end=end,
        source=source,
        subject=subject,
    )
    # If frame empty after filter, still report gap for the *requested* window
    # using observed from pre-filter if caller passed them via attrs.
    pre = attrs.get("asof_prefilter_available_ats")
    if gap is None and out.empty and pre:
        gap = coverage_gap(
            observed_available_ats=list(pre),
            start=start,
            end=end,
            source=source,
            subject=subject,
        )
    if out.empty and gap is None:
        # Empty after a fully observed window → real absence; leave gap None.
        # Empty with no observation evidence → gap (handled above when observed empty).
        gap = coverage_gap(
            observed_available_ats=[],
            start=start,
            end=end,
            source=source,
            subject=subject,
        )
    attrs["coverage_gap"] = gap
    attrs["promotion_approved"] = False
    out.attrs.update(attrs)
    return out
