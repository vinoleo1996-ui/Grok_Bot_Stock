"""Dual-track event window gates + weight long-table sleeve."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from quantlab.beta.event_arm_window_gates import classify_coverage, load_gates_config
from quantlab.portfolio.v2_multisleeve_book import DEFAULT_SLEEVES, SPOT_MAX_GROSS, WeightLongTableSleeve


def test_default_sleeves_are_stock_etf_mainline():
    assert DEFAULT_SLEEVES.get("core") == 1.0
    assert DEFAULT_SLEEVES.get("stock", 0) == 0.0
    assert "cb" not in DEFAULT_SLEEVES or DEFAULT_SLEEVES.get("cb", 0) == 0
    assert SPOT_MAX_GROSS == 1.0


def test_dual_track_does_not_kill_on_x1_zero_alone():
    r = classify_coverage(n_events_x1_full=0, n_events_native=50)
    assert r["coverage_label"] == "coverage_shifted"
    assert r["kill_on_this_coverage"] is False


def test_native_zero_is_blocked():
    r = classify_coverage(n_events_x1_full=0, n_events_native=0)
    assert r["coverage_label"] == "coverage_blocked"
    assert r["kill_on_this_coverage"] is True


def test_gates_config_readable():
    cfg = load_gates_config()
    assert cfg["gate_mode_default"] == "dual_track"
    assert cfg["fail_precheck_rules"]["x1_full_zero_alone"] is False


def test_weight_long_table_aliases(tmp_path: Path):
    df = pd.DataFrame(
        {
            "date": ["2024-06-03", "2024-06-03"],
            "ts_code": ["600000.SH", "000001.SZ"],
            "target_weight": [0.4, 0.6],
        }
    )
    path = tmp_path / "w.parquet"
    df.to_parquet(path, index=False)
    sleeve = WeightLongTableSleeve(path, name="stock")
    idx = pd.DatetimeIndex([pd.Timestamp("2024-06-03"), pd.Timestamp("2024-06-04")])
    sched = sleeve.schedule(None, idx)
    assert sleeve.status == "book_consumable"
    assert sched[pd.Timestamp("2024-06-03")]["sh.600000"] == pytest.approx(0.4)
    assert sched[pd.Timestamp("2024-06-03")]["sz.000001"] == pytest.approx(0.6)


def test_missing_path_not_book_consumable():
    sleeve = WeightLongTableSleeve(None, name="alpha_event")
    assert sleeve.schedule(None, pd.DatetimeIndex([pd.Timestamp("2024-06-03")])) == {}
    assert sleeve.status == "not_book_consumable"
