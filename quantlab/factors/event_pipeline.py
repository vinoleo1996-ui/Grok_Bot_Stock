"""Event / capital-structure signal pipeline skeleton (research-only).

Hard constraints
----------------
* ``promotion_approved=False`` on every result dataclass (not overridable).
* Signals must use ``available_at``; never event calendar day for labels when
  that would front-run the public clock.
* No look-ahead: signal session >= first session on/after ``available_at``.
* H3 dividend calendar is **paused** — this module does not load or run it.
* Does **not** mutate MAINBOOK weights or Amihud sign.

Plug Data parquet paths when they land; missing files yield empty panels + TODOs.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

import pandas as pd

# ---------------------------------------------------------------------------
# Constants / sealed window
# ---------------------------------------------------------------------------

SEALED_START: date = date(2018, 1, 1)
SEALED_END: date = date(2024, 5, 31)  # selection only; 2024-06+ confirm-only
CONFIRM_START: date = date(2024, 6, 1)

DEFAULT_REPO_ROOT = Path(__file__).resolve().parents[2]

# Known-on-box paths (do not invent coverage). Checked at load time.
KNOWN_PATHS: dict[str, Path] = {
    "lhb_top_list": Path("data/v2/dragon_tiger/top_list.parquet"),
    "lhb_top_inst": Path("data/v2/dragon_tiger/top_inst.parquet"),
    "cninfo_announce_sample": Path(
        "data/v2/free_hunt/fundamentals/cninfo_periodic_announcements_sample.parquet"
    ),
    "st_events": Path("data/v2/st_events/st_events_from_namechange.parquet"),
    "share_float": Path("data/v2/share_float/share_float_2018plus.parquet"),
}

# Expected when Data lands (may be absent today).
PENDING_PATH_KEYS: tuple[str, ...] = (
    "announce_full",  # buyback / insider / earnings / inquiry / penalty
    "northbound_holdings",
    "margin_rzrq",
    "announce_classification",  # LLM/rules labels + polarity + available_at
)


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EventRecord:
    """One atomic public event with a hard availability clock."""

    instrument: str
    event_type: str
    available_at: datetime  # timezone-aware preferred (Asia/Shanghai)
    polarity: float  # +1 long bias, -1 avoid/short-bias (long-only → filter), 0 neutral
    meta: Mapping[str, Any] = field(default_factory=dict)
    event_id: str = ""
    source: str = ""


@dataclass(frozen=True)
class SignalSpec:
    """Tradable signal definition (hypothesis → executable rule)."""

    signal_id: str
    family: str  # "event" | "capital"
    event_types: tuple[str, ...]
    entry: str  # "t1_open" | "t1_vwap"
    hold_sessions: int
    universe: str  # e.g. "full_d1" | "smallcap_sleeve"
    kill_lines: tuple[str, ...] = ()
    exclude_event_day_from_labels: bool = True
    notes: tuple[str, ...] = ()
    promotion_approved: bool = False

    def __post_init__(self) -> None:
        if self.promotion_approved:
            raise ValueError("signal_spec_promotion_approved_must_be_false")


@dataclass(frozen=True)
class EventSignalPanel:
    """Cross-section of event/capital scores at one session."""

    session: date
    signal_id: str
    values: Mapping[str, float]
    n_events: int
    todos: tuple[str, ...] = ()
    promotion_approved: bool = False

    def __post_init__(self) -> None:
        if self.promotion_approved:
            raise ValueError("event_signal_panel_promotion_approved_must_be_false")


@dataclass(frozen=True)
class ProcessICTradableResult:
    """Placeholder for tradable-label IC (open→open); filled when panels+labels exist."""

    signal_id: str
    label: str
    segment: str
    n_sessions: int
    ic_mean: float | None
    icir: float | None
    notes: tuple[str, ...] = ()
    promotion_approved: bool = False

    def __post_init__(self) -> None:
        if self.promotion_approved:
            raise ValueError("process_ic_promotion_approved_must_be_false")


@dataclass(frozen=True)
class TrialPlaceholder:
    family: str
    trial_id: str
    prereg: str
    segment: str
    outcome: str = "pending"
    note: str = ""
    promotion_approved: bool = False

    def __post_init__(self) -> None:
        if self.promotion_approved:
            raise ValueError("trial_placeholder_promotion_approved_must_be_false")


# ---------------------------------------------------------------------------
# Path helpers / stub loaders
# ---------------------------------------------------------------------------


def resolve_data_path(key: str, repo_root: Path | None = None) -> Path | None:
    """Return absolute path if known file exists; else None (caller must TODO)."""
    root = Path(repo_root) if repo_root else DEFAULT_REPO_ROOT
    rel = KNOWN_PATHS.get(key)
    if rel is None:
        return None
    path = root / rel
    return path if path.exists() else None


def inventory_data(repo_root: Path | None = None) -> dict[str, Any]:
    """Report which event/capital inputs exist on box (no invention)."""
    root = Path(repo_root) if repo_root else DEFAULT_REPO_ROOT
    present: dict[str, str] = {}
    missing_known: list[str] = []
    for key, rel in KNOWN_PATHS.items():
        p = root / rel
        if p.exists():
            present[key] = str(p)
        else:
            missing_known.append(key)
    return {
        "present": present,
        "missing_known_keys": missing_known,
        "pending_path_keys": list(PENDING_PATH_KEYS),
        "promotion_approved": False,
        "note": (
            "cninfo_announce_sample is research sample (~15 names), not full-market; "
            "northbound/margin/full announce classification still pending Data"
        ),
    }


def load_events_parquet(
    path: Path | str | None,
    *,
    instrument_col: str = "instrument",
    event_type_col: str = "event_type",
    available_at_col: str = "available_at",
    polarity_col: str = "polarity",
) -> tuple[list[EventRecord], tuple[str, ...]]:
    """Stub loader: accepts a classified-events parquet when Data lands.

    Expected minimal columns (see output/alpha/DATA_SCHEMA_EVENT_CAPITAL_ZH.md):
      instrument, event_type, available_at, polarity [, event_id, meta...]
    """
    todos: list[str] = []
    if path is None:
        todos.append("TODO: path is None — pass announce/LHB classified parquet when Data lands")
        return [], tuple(todos)
    p = Path(path)
    if not p.exists():
        todos.append(f"TODO: missing parquet {p}")
        return [], tuple(todos)
    df = pd.read_parquet(p)
    required = {instrument_col, event_type_col, available_at_col, polarity_col}
    missing_cols = sorted(required - set(df.columns))
    if missing_cols:
        todos.append(f"TODO: parquet missing columns {missing_cols}; got {list(df.columns)}")
        return [], tuple(todos)
    out: list[EventRecord] = []
    for row in df.itertuples(index=False):
        raw_at = getattr(row, available_at_col)
        at = _parse_available_at(raw_at)
        meta = {
            c: getattr(row, c)
            for c in df.columns
            if c not in required and c not in ("event_id", "source")
        }
        out.append(
            EventRecord(
                instrument=str(getattr(row, instrument_col)),
                event_type=str(getattr(row, event_type_col)),
                available_at=at,
                polarity=float(getattr(row, polarity_col)),
                meta=meta,
                event_id=str(getattr(row, "event_id", "") or ""),
                source=str(getattr(row, "source", "") or p.name),
            )
        )
    return out, tuple(todos)


def load_lhb_raw(
    repo_root: Path | None = None,
) -> tuple[pd.DataFrame | None, pd.DataFrame | None, tuple[str, ...]]:
    """Load raw Dragon-Tiger tables if present (not yet classified into EventRecord)."""
    todos: list[str] = []
    root = Path(repo_root) if repo_root else DEFAULT_REPO_ROOT
    tl_path = resolve_data_path("lhb_top_list", root)
    ti_path = resolve_data_path("lhb_top_inst", root)
    tl = ti = None
    if tl_path is None:
        todos.append("TODO: missing data/v2/dragon_tiger/top_list.parquet")
    else:
        tl = pd.read_parquet(tl_path)
    if ti_path is None:
        todos.append("TODO: missing data/v2/dragon_tiger/top_inst.parquet")
    else:
        ti = pd.read_parquet(ti_path)
    if tl is not None or ti is not None:
        todos.append(
            "LHB raw loaded; institution-vs-retail classification + available_at "
            "(T+1 close per P2_EVENT_FLOW_BROAD) still TODO before EventRecord"
        )
    return tl, ti, tuple(todos)


# ---------------------------------------------------------------------------
# Core stubs
# ---------------------------------------------------------------------------


def _parse_available_at(raw: Any) -> datetime:
    if isinstance(raw, datetime):
        return raw if raw.tzinfo else raw.replace(tzinfo=timezone.utc)
    if isinstance(raw, date) and not isinstance(raw, datetime):
        return datetime.combine(raw, time(0, 0), tzinfo=timezone.utc)
    ts = pd.Timestamp(raw)
    if ts.tzinfo is None:
        # Assume Asia/Shanghai wall clock when Data omits tz; store as UTC-aware naive→UTC
        ts = ts.tz_localize("Asia/Shanghai")
    return ts.to_pydatetime()


def available_at_to_signal_session(
    available_at: datetime,
    sessions: Sequence[date],
    *,
    exclude_event_calendar_day: bool = True,
) -> date | None:
    """Map availability clock → first tradable signal session (no look-ahead).

    Rule (research default):
    * Convert ``available_at`` to Asia/Shanghai calendar date ``d``.
    * If disclosure is on/after the session close (or we exclude event day),
      the first eligible signal session is the **next** session strictly after ``d``
      when ``exclude_event_calendar_day`` is True (no front-running event day).
    * Otherwise first session on or after ``d``.

    Returns None if no session qualifies.
    """
    if not sessions:
        return None
    # Wall date in CN
    if available_at.tzinfo is not None:
        local = available_at.astimezone(timezone.utc).astimezone(
            __import__("zoneinfo").ZoneInfo("Asia/Shanghai")
        )
        d = local.date()
    else:
        d = available_at.date()
    ordered = sorted(sessions)
    if exclude_event_calendar_day:
        for s in ordered:
            if s > d:
                return s
        return None
    for s in ordered:
        if s >= d:
            return s
    return None


def assert_no_lookahead(
    records: Sequence[EventRecord],
    signal_sessions: Mapping[str, date],
    sessions: Sequence[date],
    *,
    exclude_event_calendar_day: bool = True,
) -> None:
    """Raise if any mapped signal session precedes availability."""
    for ev in records:
        key = ev.event_id or f"{ev.instrument}|{ev.event_type}|{ev.available_at.isoformat()}"
        sig = signal_sessions.get(key)
        if sig is None:
            continue
        expected = available_at_to_signal_session(
            ev.available_at, sessions, exclude_event_calendar_day=exclude_event_calendar_day
        )
        if expected is not None and sig < expected:
            raise AssertionError(
                f"look_ahead: event {key} signal_session={sig} < expected={expected} "
                f"(available_at={ev.available_at.isoformat()})"
            )
        # Also: signal date must be >= available_at calendar session bound
        if exclude_event_calendar_day:
            at_date = (
                ev.available_at.astimezone(
                    __import__("zoneinfo").ZoneInfo("Asia/Shanghai")
                ).date()
                if ev.available_at.tzinfo
                else ev.available_at.date()
            )
            if sig <= at_date:
                raise AssertionError(
                    f"look_ahead_event_day: signal {sig} on/before available day {at_date}"
                )


def align_to_sessions(
    records: Sequence[EventRecord],
    sessions: Sequence[date],
    *,
    exclude_event_calendar_day: bool = True,
) -> dict[date, list[EventRecord]]:
    """Bucket events by first eligible signal session."""
    buckets: dict[date, list[EventRecord]] = {}
    for ev in records:
        sig = available_at_to_signal_session(
            ev.available_at, sessions, exclude_event_calendar_day=exclude_event_calendar_day
        )
        if sig is None:
            continue
        buckets.setdefault(sig, []).append(ev)
    return buckets


def build_event_signals(
    asof: date,
    records: Sequence[EventRecord],
    sessions: Sequence[date],
    spec: SignalSpec,
) -> EventSignalPanel:
    """Aggregate events available by ``asof`` into a cross-sectional score stub.

    Score = sum of polarities for matching event_types whose signal session == asof
    (same-day entry batch). Full IC/hold logic is Strategy/engine later.
    """
    if spec.promotion_approved:
        raise ValueError("build_event_signals_promotion_blocked")
    todos: list[str] = []
    if not records:
        todos.append("TODO: no EventRecord inputs — await Data announce/LHB classification")
    matched_types = set(spec.event_types)
    buckets = align_to_sessions(
        records, sessions, exclude_event_calendar_day=spec.exclude_event_day_from_labels
    )
    day_events = [e for e in buckets.get(asof, []) if e.event_type in matched_types]
    values: dict[str, float] = {}
    for e in day_events:
        values[e.instrument] = values.get(e.instrument, 0.0) + float(e.polarity)
    return EventSignalPanel(
        session=asof,
        signal_id=spec.signal_id,
        values=values,
        n_events=len(day_events),
        todos=tuple(todos),
        promotion_approved=False,
    )


def process_ic_tradable(
    panels: Sequence[EventSignalPanel],
    *,
    label: str = "oo_1d",
    segment: str = "2018-01..2024-05",
) -> ProcessICTradableResult:
    """Stub: tradable IC when forward open→open labels are wired.

    Does not compute real IC yet (avoids silent fake numbers). Returns None metrics
    and a TODO note until label panels are passed in a later PR.
    """
    sid = panels[0].signal_id if panels else "empty"
    return ProcessICTradableResult(
        signal_id=sid,
        label=label,
        segment=segment,
        n_sessions=len(panels),
        ic_mean=None,
        icir=None,
        notes=(
            "TODO: wire tradable open→open labels (t+1 open → t+2 open); "
            "exclude event calendar day; sealed selection 2018-01..2024-05 only",
        ),
        promotion_approved=False,
    )


def register_trial_placeholder(
    *,
    family: str,
    trial_id: str,
    prereg: str = "output/alpha/ALPHA_EVENT_HYPOTHESES_ZH.md",
    segment: str = "2018-01..2024-05",
    note: str = "",
) -> TrialPlaceholder:
    """In-memory trial placeholder; caller appends to docs/trial_ledger.csv."""
    return TrialPlaceholder(
        family=family,
        trial_id=trial_id,
        prereg=prereg,
        segment=segment,
        outcome="pending",
        note=note or "skeleton registered; blocked on Data",
        promotion_approved=False,
    )


def sealed_segment_mask(sessions: Sequence[date]) -> tuple[list[date], list[date]]:
    """Split sessions into selection (≤2024-05-31) vs confirm-only (≥2024-06-01)."""
    sealed = [s for s in sessions if SEALED_START <= s <= SEALED_END]
    confirm = [s for s in sessions if s >= CONFIRM_START]
    return sealed, confirm


__all__ = [
    "SEALED_START",
    "SEALED_END",
    "CONFIRM_START",
    "KNOWN_PATHS",
    "PENDING_PATH_KEYS",
    "EventRecord",
    "SignalSpec",
    "EventSignalPanel",
    "ProcessICTradableResult",
    "TrialPlaceholder",
    "resolve_data_path",
    "inventory_data",
    "load_events_parquet",
    "load_lhb_raw",
    "available_at_to_signal_session",
    "assert_no_lookahead",
    "align_to_sessions",
    "build_event_signals",
    "process_ic_tradable",
    "register_trial_placeholder",
    "sealed_segment_mask",
]
