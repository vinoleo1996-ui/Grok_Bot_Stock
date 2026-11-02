"""Event pipeline: no look-ahead + promotion_approved hard-false."""
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import pytest

from quantlab.factors.event_pipeline import (
    EventRecord,
    SignalSpec,
    assert_no_lookahead,
    available_at_to_signal_session,
    build_event_signals,
    load_events_parquet,
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


def test_cninfo_sample_uses_announcement_time_without_rewriting_the_file(tmp_path):
    path = tmp_path / "cninfo.parquet"
    pd.DataFrame({
        "instrument_id": ["sz.000001"],
        "title": ["2023年三季度报告"],
        "announcement_id": ["1218135621"],
        "announcement_time": ["2023-10-25T00:00:00+08:00"],
        "source": ["cninfo_hisAnnouncement"],
        "promotion_approved": [False],
    }).to_parquet(path, index=False)
    records, notes = load_events_parquet(path)
    assert records[0].instrument == "sz.000001"
    assert records[0].event_id == "1218135621"
    assert records[0].event_type == "cninfo_periodic_announcement"
    assert records[0].polarity == 0.0
    assert records[0].available_at.tzinfo is not None
    assert records[0].available_at.date() == date(2023, 10, 25)
    assert "available_at_from_announcement_time" in notes
    assert "polarity_unclassified" in notes
    assert "available_at" not in pd.read_parquet(path).columns
    bare = tmp_path / "bare.parquet"
    pd.DataFrame({"title": ["no clock"]}).to_parquet(bare, index=False)
    empty, missing = load_events_parquet(bare)
    assert empty == []
    assert any("missing columns" in item for item in missing)
    landed = Path("data/v2/free_hunt/fundamentals/cninfo_periodic_announcements_sample.parquet")
    if landed.is_file():
        live, live_notes = load_events_parquet(landed)
        assert len(live) == 301
        assert live[0].instrument == "sz.000001"
        assert "available_at" not in pd.read_parquet(landed).columns
        assert "polarity_unclassified" in live_notes


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
