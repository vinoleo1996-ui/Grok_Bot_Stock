"""Unit tests for TradingAgents-style as_of text guard."""
from __future__ import annotations

import pytest

from quantlab.factors.ai_factory.asof_text_guard import (
    TextFeatureRow,
    as_of,
    as_of_window,
    assert_no_text_lookahead,
    coverage_gap,
    filter_text_features_asof,
)


def test_as_of_clamps_future():
    assert as_of("2024-07-01", "2024-06-15") == "2024-06-15"
    assert as_of("2024-06-01", "2024-06-15") == "2024-06-01"
    assert as_of(None, "2024-06-15") == "2024-06-15"


def test_as_of_window_clamps_end():
    s, e = as_of_window("2024-06-01", "2024-07-01", "2024-06-15")
    assert e == "2024-06-15"
    assert s == "2024-06-01"


def test_filter_rejects_lookahead_announcement():
    rows = [
        TextFeatureRow(id="a1", available_at="2024-06-10", body="ok"),
        TextFeatureRow(id="a2", available_at="2024-06-20", body="future leak"),
        {"id": "a3", "available_at": "2024-06-15", "title": "boundary ok"},
    ]
    res = filter_text_features_asof(rows, "2024-06-15", source="ann", subject="filings")
    assert res.promotion_approved is False
    ids = {r.id for r in res.allowed}
    assert ids == {"a1", "a3"}
    assert any(r["reason"] == "lookahead_available_at_after_trade_date" for r in res.rejected)
    with pytest.raises(AssertionError):
        assert_no_text_lookahead(rows, "2024-06-15")


def test_missing_available_at_rejected_on_historical():
    rows = [{"id": "x", "title": "no stamp"}]
    res = filter_text_features_asof(rows, "2024-06-15")
    assert len(res.allowed) == 0
    assert res.rejected[0]["reason"] == "missing_available_at"


def test_coverage_gap_when_only_recent():
    msg = coverage_gap(
        ["2024-06-20", "2024-06-21"],
        "2024-01-01",
        "2024-01-31",
        source="rss",
        subject="news",
    )
    assert msg is not None
    assert "unavailable" in msg
