"""Tests for Eng intel as_of / PIT text guards (TradingAgents-adapted)."""
from __future__ import annotations

from datetime import date, datetime

import pandas as pd
import pytest

from quantlab.intel.asof_window import (
    as_of,
    as_of_window,
    assert_available_at_le_decision,
    coverage_gap,
    filter_frame_asof,
    in_window,
    session_to_decision_ts,
    withhold_live_only,
)
from quantlab.intel.debate_ledger import JsonlDebateLedger, make_pending_decision
from quantlab.intel.messages import load_message_frame
from quantlab.factors.ai_factory.pipeline_export import dry_run_export, pipeline_stages


def test_as_of_clamps_future_request():
    assert as_of("2019-02-20", "2019-02-15") == date(2019, 2, 15)
    assert as_of("2019-02-10", "2019-02-15") == date(2019, 2, 10)
    assert as_of(None, "2019-02-15") == date(2019, 2, 15)


def test_as_of_window_shifts_wholly_future_span():
    start, end = as_of_window("2019-03-01", "2019-03-10", "2019-02-15")
    assert end == date(2019, 2, 15)
    assert (end - start).days == 9


def test_in_window_and_undated_refused():
    assert in_window("2019-02-14 10:00", "2019-02-01", "2019-02-15") is True
    assert in_window("2019-02-16 01:00", "2019-02-01", "2019-02-15") is False
    assert in_window(None, "2019-02-01", "2019-02-15") is False


def test_coverage_gap_when_no_dated_evidence():
    gap = coverage_gap(
        observed_available_ats=[],
        start="2019-02-01",
        end="2019-02-15",
        source="intel.messages",
    )
    assert gap is not None
    assert "not an absence" in gap


def test_filter_drops_future_announcement():
    df = pd.DataFrame(
        {
            "message_id": ["a", "b", "c"],
            "available_at": [
                datetime(2019, 2, 14, 17, 0),
                datetime(2019, 2, 15, 19, 0),  # after 18:00 cutoff
                datetime(2019, 2, 16, 9, 0),  # next day
            ],
            "title": ["ok", "leak", "future"],
        }
    )
    out = filter_frame_asof(df, trade_session=date(2019, 2, 15))
    assert list(out["message_id"]) == ["a"]
    assert out.attrs["asof_dropped_future"] == 2
    assert out.attrs["promotion_approved"] is False


def test_filter_strict_raises_on_future():
    df = pd.DataFrame(
        {
            "message_id": ["x"],
            "available_at": [datetime(2019, 2, 16, 9, 0)],
            "title": ["future"],
        }
    )
    with pytest.raises(ValueError, match="pit_lookahead"):
        filter_frame_asof(df, trade_session=date(2019, 2, 15), strict=True)


def test_assert_available_at_le_decision():
    assert_available_at_le_decision(
        {"available_at": datetime(2019, 2, 15, 17, 0)},
        datetime(2019, 2, 15, 18, 0),
    )
    with pytest.raises(ValueError, match="pit_lookahead"):
        assert_available_at_le_decision(
            {"available_at": datetime(2019, 2, 16, 9, 0)},
            datetime(2019, 2, 15, 18, 0),
        )


def test_load_message_frame_asof_inject_future(tmp_path, monkeypatch):
    """Backtest day must not keep post-cutoff / next-day announcements."""
    path = tmp_path / "msgs.parquet"
    pd.DataFrame(
        {
            "message_id": ["past", "after_cutoff", "next_day"],
            "instrument": ["000001.SZ", "000001.SZ", "000001.SZ"],
            "source": ["ann", "ann", "ann"],
            "category": ["earn", "earn", "earn"],
            "polarity": [0.0, 0.0, 0.0],
            "title": ["yesterday", "same-day leak after 18:00", "tomorrow"],
            "available_at": [
                datetime(2019, 2, 14, 23, 59),
                datetime(2019, 2, 15, 19, 30),  # after default 18:00 cutoff
                datetime(2019, 2, 16, 10, 0),
            ],
            "asof_session": [date(2019, 2, 14), date(2019, 2, 15), date(2019, 2, 16)],
            "content_hash": ["h1", "h2", "h3"],
            "payload_uri": ["", "", ""],
        }
    ).to_parquet(path)

    import quantlab.intel.messages as messages

    monkeypatch.setattr(messages, "default_message_corpus_path", lambda: path)
    df = messages.load_message_frame(
        start=date(2019, 2, 1),
        end=date(2019, 2, 20),  # caller asks past trade_session
        trade_session=date(2019, 2, 15),
        strict_asof=False,
    )
    assert "after_cutoff" not in set(df["message_id"])
    assert "next_day" not in set(df["message_id"])
    assert list(df["message_id"]) == ["past"]
    assert df.attrs.get("promotion_approved") is False

    # strict: same-day post-cutoff row survives the calendar window clamp but
    # must fail the decision_ts guard
    with pytest.raises(ValueError, match="pit_lookahead"):
        messages.load_message_frame(
            start=date(2019, 2, 1),
            end=date(2019, 2, 20),
            trade_session=date(2019, 2, 15),
            strict_asof=True,
        )


def test_withhold_live_only_on_historical():
    notice = withhold_live_only(date(2019, 2, 15), label="000001.SZ")
    assert notice is not None
    assert "2019-02-15" in notice


def test_debate_ledger_pending(tmp_path):
    led = JsonlDebateLedger(tmp_path / "debate.jsonl")
    entry = make_pending_decision(
        decision_id="d1",
        session=date(2019, 2, 15),
        instrument="000001.SZ",
        rating="Hold",
        rationale_zh="研究级占位",
    )
    led.append_decision(entry)
    pending = led.pending_decisions()
    assert len(pending) == 1
    assert pending[0]["promotion_approved"] is False
    led.append_settlement(
        {
            "decision_id": "d1",
            "session": "2019-02-15",
            "instrument": "000001.SZ",
            "horizon_days": 5,
            "benchmark": "000300.SH",
            "raw_return": 0.01,
            "alpha_vs_benchmark": 0.0,
            "reflection_zh": "stub",
            "settled_at": "2019-02-22T18:00:00",
            "promotion_approved": False,
        }
    )
    assert led.pending_decisions() == []


def test_quantmind_export_dry_run_blocks_textbook():
    assert pipeline_stages()[-1] == "export"
    bad = dry_run_export(
        factor_id="f1",
        expr_str="rank(close/delay(close,20))",
        metrics={"ic": 0.05, "ann_net": 0.1},
        direction_zh="20日动量增强",
        mechanism_tag="momentum",
        universe="csi300",
    )
    assert bad.export is None
    assert any("textbook_direction" in r for r in bad.blocked_reasons)
    assert bad.promotion_approved is False

    ok = dry_run_export(
        factor_id="f2",
        expr_str="emb_0",
        metrics={"ic": 0.02, "icir": 0.4, "ann_net": 0.05},
        direction_zh="公告嵌入与涨停回封率",
        mechanism_tag="ann_embed",
        universe="csi300",
        capital_cny=600_000,
    )
    assert ok.export is not None
    assert ok.export["promotion_approved"] is False
    assert "export" in ok.stages_ok


def test_session_cutoff_default_1800():
    ts = session_to_decision_ts(date(2019, 2, 15))
    assert ts == datetime(2019, 2, 15, 18, 0, 0)
