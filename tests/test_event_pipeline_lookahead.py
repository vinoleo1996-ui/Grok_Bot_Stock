"""Event pipeline: no look-ahead + promotion_approved hard-false."""
from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

from quantlab.factors.event_pipeline import (
    EventRecord,
    SignalSpec,
    assert_no_lookahead,
    available_at_to_signal_session,
    build_event_signals,
    process_ic_tradable,
    register_trial_placeholder,
)

SH = ZoneInfo("Asia/Shanghai")


def _sessions():
    return [
        date(2021, 6, 1),
        date(2021, 6, 2),
        date(2021, 6, 3),
        date(2021, 6, 4),
        date(2021, 6, 7),
    ]


def _fake_events():
    return [
        EventRecord(
            instrument="000001.SZ",
            event_type="buyback",
            available_at=datetime(2021, 6, 1, 19, 0, tzinfo=SH),  # after close
            polarity=1.0,
            event_id="e1",
        ),
        EventRecord(
            instrument="600000.SH",
            event_type="penalty",
            available_at=datetime(2021, 6, 2, 10, 0, tzinfo=SH),  # during session
            polarity=-1.0,
            event_id="e2",
        ),
        EventRecord(
            instrument="000002.SZ",
            event_type="earnings_beat",
            available_at=datetime(2021, 6, 3, 16, 5, tzinfo=SH),
            polarity=1.0,
            event_id="e3",
        ),
    ]


def test_signal_session_strictly_after_available_day_when_excluding_event_day():
    sessions = _sessions()
    # available 2021-06-01 → first signal 2021-06-02
    s = available_at_to_signal_session(
        datetime(2021, 6, 1, 19, 0, tzinfo=SH), sessions, exclude_event_calendar_day=True
    )
    assert s == date(2021, 6, 2)
    # mid-session 2021-06-02 → still exclude calendar day → 2021-06-03
    s2 = available_at_to_signal_session(
        datetime(2021, 6, 2, 10, 0, tzinfo=SH), sessions, exclude_event_calendar_day=True
    )
    assert s2 == date(2021, 6, 3)


def test_assert_no_lookahead_passes_and_catches_violation():
    sessions = _sessions()
    events = _fake_events()
    good = {
        e.event_id: available_at_to_signal_session(e.available_at, sessions)
        for e in events
    }
    assert_no_lookahead(events, good, sessions)

    bad = dict(good)
    bad["e1"] = date(2021, 6, 1)  # on available day → look-ahead / front-run
    with pytest.raises(AssertionError, match="look_ahead"):
        assert_no_lookahead(events, bad, sessions)


def test_build_event_signals_and_promotion_flags_false():
    sessions = _sessions()
    events = _fake_events()
    spec = SignalSpec(
        signal_id="EV_MIX_SMOKE",
        family="event",
        event_types=("buyback", "penalty", "earnings_beat"),
        entry="t1_open",
        hold_sessions=5,
        universe="full_d1",
        promotion_approved=False,
    )
    # e1 maps to 2021-06-02
    panel = build_event_signals(date(2021, 6, 2), events, sessions, spec)
    assert panel.promotion_approved is False
    assert panel.values.get("000001.SZ") == 1.0
    assert "600000.SH" not in panel.values  # penalty signals on 06-03

    ic = process_ic_tradable([panel])
    assert ic.promotion_approved is False
    assert ic.icir is None

    ph = register_trial_placeholder(family="alpha_event_v1", trial_id="unit_test")
    assert ph.promotion_approved is False


def test_signal_spec_rejects_promotion_true():
    with pytest.raises(ValueError, match="promotion_approved_must_be_false"):
        SignalSpec(
            signal_id="bad",
            family="event",
            event_types=("buyback",),
            entry="t1_open",
            hold_sessions=1,
            universe="full_d1",
            promotion_approved=True,
        )
