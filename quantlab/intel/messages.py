"""Message corpus reader (THIS_WEEK Eng stub) with as_of / PIT text guards.

Reads Data's classified announcements PIT when present. Does not invent rows.
promotion_approved is never True for research intel outputs.

as_of: pass ``trade_session`` or ``decision_ts`` so future ``available_at`` rows
cannot leak into a historical query (see ``intel.asof_window``).
"""
from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Mapping, Sequence, TypedDict

import pandas as pd

from quantlab.intel.asof_window import (
    annotate_coverage_gap,
    as_of_window,
    assert_available_at_le_decision,
    filter_frame_asof,
    session_to_decision_ts,
)
from quantlab.promotion_gate import overall_promotion_approved

PROMOTION_APPROVED = False
REPO_ROOT = Path(__file__).resolve().parents[2]
ENG_PING_PATH = REPO_ROOT / "output" / "d1" / "ENG_PING_PATHS.json"
FALLBACK_CORPUS = REPO_ROOT / "data" / "v2" / "events" / "announcements_classified_pit.parquet"


class MessageRecord(TypedDict, total=False):
    message_id: str
    instrument: str
    source: str
    category: str
    polarity: float
    title: str
    available_at: datetime
    asof_session: date
    content_hash: str
    payload_uri: str


def _eng_ping() -> dict[str, Any]:
    try:
        return json.loads(ENG_PING_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def default_message_corpus_path() -> Path | None:
    """Resolve corpus path: ENG_PING intel_message_corpus -> announcements_classified_pit -> fallback file."""
    ping = _eng_ping()
    paths = ping.get("paths") or {}
    for key in ("intel_message_corpus", "announcements_classified_pit"):
        raw = paths.get(key)
        if not raw:
            continue
        p = Path(str(raw))
        if not p.is_absolute():
            p = REPO_ROOT / p
        if p.exists():
            return p
    if FALLBACK_CORPUS.exists():
        return FALLBACK_CORPUS
    return None


def assert_pit_available(row: Mapping[str, Any], decision_ts: datetime) -> None:
    """Raise if decision_ts is strictly before available_at (look-ahead)."""
    assert_available_at_le_decision(row, decision_ts, field="available_at")


def load_message_frame(
    *,
    start: date | None = None,
    end: date | None = None,
    instruments: Sequence[str] | None = None,
    categories: Sequence[str] | None = None,
    roots: object | None = None,
    trade_session: date | None = None,
    decision_ts: datetime | None = None,
    strict_asof: bool = False,
) -> pd.DataFrame:
    """Load classified PIT message corpus.

    Missing path -> empty DataFrame (caller should treat as TODO / data gap).
    Never sets promotion_approved True. ``roots`` reserved for future V2DataRoots.

    as_of guards:
    - If ``trade_session`` is set, ``end`` is clamped via ``as_of_window``.
    - Rows with ``available_at`` after the decision cutoff are dropped
      (or raise when ``strict_asof=True``).
    - Empty unobserved windows get ``attrs['coverage_gap']`` string (not a false
      "no news" claim).
    """
    _ = roots  # reserved
    _ = overall_promotion_approved()  # visibility only; intel stays research
    path = default_message_corpus_path()
    empty_cols = [
        "message_id",
        "instrument",
        "source",
        "category",
        "polarity",
        "title",
        "available_at",
        "asof_session",
        "content_hash",
        "payload_uri",
    ]

    # Clamp window to trade_session when provided
    win_start, win_end = start, end
    if trade_session is not None:
        s0 = start or trade_session
        e0 = end or trade_session
        win_start, win_end = as_of_window(s0, e0, trade_session)

    if path is None:
        empty = pd.DataFrame(columns=empty_cols)
        empty.attrs["promotion_approved"] = False
        empty.attrs["corpus_path"] = None
        empty.attrs["todos"] = ("message_corpus_missing",)
        return annotate_coverage_gap(
            empty,
            start=win_start,
            end=win_end or trade_session,
            source="intel.messages",
            subject="messages",
        )

    try:
        df = pd.read_parquet(path)
    except Exception:
        empty = pd.DataFrame(columns=empty_cols)
        empty.attrs["promotion_approved"] = False
        empty.attrs["corpus_path"] = str(path)
        empty.attrs["todos"] = ("message_corpus_unreadable",)
        return annotate_coverage_gap(
            empty,
            start=win_start,
            end=win_end or trade_session,
            source="intel.messages",
            subject="messages",
        )

    # Best-effort column normalize (Data schema may use alternate names).
    rename = {}
    for src, dst in (
        ("ts_code", "instrument"),
        ("symbol", "instrument"),
        ("code", "instrument"),
        ("ann_date", "asof_session"),
        ("classify", "category"),
        ("class", "category"),
        ("subtype", "category"),
        ("title_hash", "content_hash"),
    ):
        if src in df.columns and dst not in df.columns:
            rename[src] = dst
    if rename:
        df = df.rename(columns=rename)

    if win_start is not None and "available_at" in df.columns:
        ts = pd.to_datetime(df["available_at"], errors="coerce")
        start_ts = pd.Timestamp(win_start)
        if getattr(ts.dt, "tz", None) is not None:
            start_ts = start_ts.tz_localize(ts.dt.tz)
        df = df.loc[ts >= start_ts]
    if win_end is not None and "available_at" in df.columns:
        ts = pd.to_datetime(df["available_at"], errors="coerce")
        end_ts = pd.Timestamp(win_end) + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
        if getattr(ts.dt, "tz", None) is not None:
            end_ts = end_ts.tz_localize(ts.dt.tz)
        df = df.loc[ts <= end_ts]
    if instruments is not None and "instrument" in df.columns:
        want = set(instruments)
        df = df.loc[df["instrument"].astype(str).isin(want)]
    if categories is not None and "category" in df.columns:
        want_c = set(categories)
        df = df.loc[df["category"].astype(str).isin(want_c)]

    df = df.copy()
    pre_ats = (
        list(df["available_at"].tolist()) if "available_at" in df.columns else []
    )
    df.attrs["promotion_approved"] = False
    df.attrs["corpus_path"] = str(path)
    df.attrs["todos"] = ()
    df.attrs["asof_prefilter_available_ats"] = pre_ats

    # PIT as_of filter: drop future-available text relative to decision
    if trade_session is not None or decision_ts is not None:
        df = filter_frame_asof(
            df,
            trade_session=trade_session,
            decision_ts=decision_ts,
            available_at_field="available_at",
            strict=strict_asof,
        )

    df = annotate_coverage_gap(
        df,
        start=win_start,
        end=win_end or trade_session,
        source="intel.messages",
        subject="messages",
    )
    return df.reset_index(drop=True)


def load_messages_for_session(
    trade_session: date,
    *,
    instruments: Sequence[str] | None = None,
    lookback_days: int = 5,
    strict_asof: bool = True,
) -> pd.DataFrame:
    """Convenience: messages available as of ``trade_session`` (strict by default)."""
    from datetime import timedelta

    start = trade_session - timedelta(days=lookback_days)
    return load_message_frame(
        start=start,
        end=trade_session,
        instruments=instruments,
        trade_session=trade_session,
        decision_ts=session_to_decision_ts(trade_session),
        strict_asof=strict_asof,
    )
