"""TradingAgents-style as_of / available_at guard for text & announcement features.

Alpha-callable stub; Eng owns full Reader packaging (OPENSOURCE_DEEP_READ §7.1 E1).
Any text/announcement row whose available_at (or pub time) is after trade_date
is rejected as look-ahead. Missing coverage returns coverage_gap, never an empty
list that pretends "no news".

promotion_approved is always False here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Any, Iterable, Mapping, Sequence

PROMOTION_APPROVED = False

UTC = timezone.utc
# Decision cutoff used elsewhere in QuantLab (Shanghai 18:00) — documented only;
# this module compares calendar dates / timestamps, callers pass trade_date.


def _parse_date(value: str | date | datetime | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    s = str(value).strip()
    if not s:
        return None
    # Accept YYYY-MM-DD or YYYYMMDD or ISO with time
    if "T" in s or " " in s:
        s = s.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(s).date()
        except ValueError:
            s = s[:10]
    s = s.replace("/", "-")
    if len(s) == 8 and s.isdigit():
        return date(int(s[:4]), int(s[4:6]), int(s[6:8]))
    try:
        return date.fromisoformat(s[:10])
    except ValueError:
        return None


def _to_utc_aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def as_of(requested: str | None, trade_date: str) -> str | None:
    """Clamp a model-requested date so it is never later than trade_date."""
    if not trade_date:
        return requested
    td = _parse_date(trade_date)
    if td is None:
        raise ValueError(f"trade_date {trade_date!r} is not a date")
    if requested is None or str(requested).strip() == "":
        return trade_date
    rd = _parse_date(requested)
    if rd is None:
        return trade_date
    return requested if rd <= td else trade_date


def as_of_window(start_date: str, end_date: str, trade_date: str) -> tuple[str, str]:
    """Return [start, end] with end clamped to trade_date; shift window if wholly after."""
    start = _parse_date(start_date)
    if start is None:
        raise ValueError(f"start_date {start_date!r} is not a date; give YYYY-MM-DD")
    td = _parse_date(trade_date)
    if td is None:
        raise ValueError(f"trade_date {trade_date!r} is not a date")
    end_clamped = as_of(end_date, trade_date)
    end = _parse_date(end_clamped)
    assert end is not None
    old_end = _parse_date(end_date)
    if end == old_end or start <= end:
        return start_date, end_clamped  # type: ignore[return-value]
    span = (old_end - start) if old_end is not None and old_end >= start else timedelta(0)
    new_start = end - span
    return new_start.isoformat(), end.isoformat()


def coverage_gap(
    observed_dates: Iterable[str | date | datetime | None],
    start_date: str,
    end_date: str,
    source: str,
    subject: str,
) -> str | None:
    """Placeholder when a feed cannot cover [start, end]; None if window is observed."""
    start = _parse_date(start_date)
    end = _parse_date(end_date)
    if start is None or end is None:
        return f"<{source} unavailable for {start_date}..{end_date}: unreadable window, so this is not an absence of {subject}>"
    today = date.today()
    parsed = []
    for d in observed_dates:
        if d is None:
            continue
        if isinstance(d, datetime):
            parsed.append(d.date())
        elif isinstance(d, date):
            parsed.append(d)
        else:
            p = _parse_date(d)
            if p is not None:
                parsed.append(p)
    oldest = min(parsed) if parsed else today
    if end > today:
        reason = "the window extends past today"
    elif oldest > start:
        reason = "it only serves recent items"
    else:
        return None
    return (
        f"<{source} unavailable for {start_date}..{end_date}: {reason}, "
        f"so this is not an absence of {subject}>"
    )


@dataclass
class TextFeatureRow:
    """One announcement/news/sentiment row with PIT fields."""

    id: str
    available_at: str | date | datetime
    body: str = ""
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class GuardResult:
    allowed: list[TextFeatureRow]
    rejected: list[dict[str, Any]]
    coverage_gap_msg: str | None = None
    promotion_approved: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "promotion_approved", False)


def _available_date(row: TextFeatureRow | Mapping[str, Any]) -> date | None:
    if isinstance(row, TextFeatureRow):
        return _parse_date(row.available_at)
    for key in ("available_at", "ann_date", "pub_time", "published_at", "asof"):
        if key in row and row[key] is not None:
            return _parse_date(row[key])
    return None


def filter_text_features_asof(
    rows: Sequence[TextFeatureRow | Mapping[str, Any]],
    trade_date: str,
    *,
    source: str = "text",
    subject: str = "announcements",
    require_available_at: bool = True,
) -> GuardResult:
    """Keep only rows with available_at.date() <= trade_date.

    Rows missing available_at are rejected when require_available_at=True
    (look-ahead risk). Empty allowed set with a coverage_gap when no dated
    coverage reaches the window start.
    """
    td = _parse_date(trade_date)
    if td is None:
        raise ValueError(f"trade_date {trade_date!r} is not a date")
    allowed: list[TextFeatureRow] = []
    rejected: list[dict[str, Any]] = []
    observed: list[date] = []
    for raw in rows:
        if isinstance(raw, TextFeatureRow):
            row = raw
            rid = row.id
        else:
            rid = str(raw.get("id") or raw.get("ann_id") or raw.get("ts_code") or "")
            avail = raw.get("available_at") or raw.get("ann_date") or raw.get("pub_time")
            row = TextFeatureRow(
                id=rid,
                available_at=avail if avail is not None else "",
                body=str(raw.get("body") or raw.get("title") or ""),
                meta=dict(raw),
            )
        ad = _available_date(row)
        if ad is None:
            if require_available_at:
                rejected.append(
                    {
                        "id": rid,
                        "reason": "missing_available_at",
                        "trade_date": trade_date,
                    }
                )
                continue
            # undated: only allow on live (today) runs
            if td < date.today():
                rejected.append(
                    {
                        "id": rid,
                        "reason": "undated_on_historical_run",
                        "trade_date": trade_date,
                    }
                )
                continue
            allowed.append(row)
            continue
        observed.append(ad)
        if ad > td:
            rejected.append(
                {
                    "id": rid,
                    "reason": "lookahead_available_at_after_trade_date",
                    "available_at": ad.isoformat(),
                    "trade_date": trade_date,
                }
            )
            continue
        allowed.append(row)
    gap = None
    if not allowed:
        gap = coverage_gap(
            observed,
            start_date=trade_date,
            end_date=trade_date,
            source=source,
            subject=subject,
        )
        if gap is None and rejected:
            gap = (
                f"<{source} no in-window {subject} for {trade_date}: "
                f"{len(rejected)} rejected as look-ahead or undated>"
            )
    return GuardResult(allowed=allowed, rejected=rejected, coverage_gap_msg=gap)


def assert_no_text_lookahead(
    rows: Sequence[TextFeatureRow | Mapping[str, Any]],
    trade_date: str,
) -> None:
    """Hard fail if any row is available after trade_date (unit-test helper)."""
    res = filter_text_features_asof(rows, trade_date)
    if res.rejected:
        bad = [r for r in res.rejected if r.get("reason") == "lookahead_available_at_after_trade_date"]
        if bad:
            raise AssertionError(
                f"look-ahead text features for trade_date={trade_date}: {bad[:3]}"
            )
