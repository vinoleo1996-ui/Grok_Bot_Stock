#!/usr/bin/env python3
"""Minimal runner / inventory for event + capital-structure skeleton.

Research-only. Does not run H3. Does not mutate MAINBOOK. promotion_approved=false.

Usage (from repo root)::

    python research/event_signal_skeleton.py
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantlab.factors.event_pipeline import (
    EventRecord,
    SignalSpec,
    align_to_sessions,
    assert_no_lookahead,
    available_at_to_signal_session,
    build_event_signals,
    inventory_data,
    load_lhb_raw,
    process_ic_tradable,
    register_trial_placeholder,
    sealed_segment_mask,
)

SH = ZoneInfo("Asia/Shanghai")


def _demo_fake_events() -> list[EventRecord]:
    """Two–three fake events for smoke only (not a backtest)."""
    return [
        EventRecord(
            instrument="000001.SZ",
            event_type="buyback",
            available_at=datetime(2020, 3, 10, 18, 30, tzinfo=SH),
            polarity=1.0,
            event_id="fake_buyback_1",
            source="skeleton_demo",
        ),
        EventRecord(
            instrument="600000.SH",
            event_type="inquiry_letter",
            available_at=datetime(2020, 3, 11, 9, 0, tzinfo=SH),
            polarity=-1.0,
            event_id="fake_inquiry_1",
            source="skeleton_demo",
        ),
        EventRecord(
            instrument="000002.SZ",
            event_type="insider_increase",
            available_at=datetime(2020, 3, 12, 16, 5, tzinfo=SH),
            polarity=1.0,
            event_id="fake_insider_1",
            source="skeleton_demo",
        ),
    ]


def main() -> int:
    inv = inventory_data(ROOT)
    print("=== data inventory ===")
    print(json.dumps(inv, indent=2, ensure_ascii=False))

    tl, ti, lhb_todos = load_lhb_raw(ROOT)
    print("=== LHB stub ===")
    print(
        {
            "top_list_rows": None if tl is None else len(tl),
            "top_inst_rows": None if ti is None else len(ti),
            "todos": list(lhb_todos),
        }
    )

    sessions = [
        date(2020, 3, 10),
        date(2020, 3, 11),
        date(2020, 3, 12),
        date(2020, 3, 13),
        date(2020, 3, 16),
    ]
    sealed, confirm = sealed_segment_mask(
        [date(2018, 1, 2), date(2024, 5, 31), date(2024, 6, 3)]
    )
    assert sealed == [date(2018, 1, 2), date(2024, 5, 31)]
    assert confirm == [date(2024, 6, 3)]

    events = _demo_fake_events()
    mapping = {
        e.event_id: available_at_to_signal_session(e.available_at, sessions)
        for e in events
    }
    assert_no_lookahead(events, {k: v for k, v in mapping.items() if v}, sessions)

    spec = SignalSpec(
        signal_id="EV_BUYBACK_T1",
        family="event",
        event_types=("buyback",),
        entry="t1_open",
        hold_sessions=20,
        universe="full_d1",
        kill_lines=("limit_up_buy_block", "suspend"),
        exclude_event_day_from_labels=True,
        promotion_approved=False,
    )
    # buyback available 2020-03-10 18:30 → first signal session 2020-03-11
    panel = build_event_signals(date(2020, 3, 11), events, sessions, spec)
    assert panel.promotion_approved is False
    assert "000001.SZ" in panel.values

    ic = process_ic_tradable([panel], segment="2018-01..2024-05")
    assert ic.promotion_approved is False
    assert ic.ic_mean is None  # no fake IC

    ph = register_trial_placeholder(
        family="alpha_event_v1",
        trial_id="skeleton_smoke",
        note="smoke only; not a counted research trial",
    )
    assert ph.promotion_approved is False

    buckets = align_to_sessions(events, sessions)
    print("=== smoke ===")
    print(
        {
            "signal_map": {k: str(v) for k, v in mapping.items()},
            "panel_session": str(panel.session),
            "panel_values": panel.values,
            "ic_notes": list(ic.notes),
            "trial_placeholder": ph.trial_id,
            "bucket_sessions": [str(k) for k in sorted(buckets)],
            "promotion_approved": False,
            "written_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
