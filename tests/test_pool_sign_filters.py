"""Filters for the pool sign test. No account and no code-order book."""
import importlib.util
from datetime import date
from pathlib import Path

import pandas as pd

_PATH = Path(__file__).resolve().parents[1] / "research" / "rd_pool_sign_20261101.py"
_SPEC = importlib.util.spec_from_file_location("rd_pool_sign_20261101", _PATH)
pool = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(pool)


def test_beijing_and_st_drop_and_a_missing_st_day_is_a_gap():
    st_days = {pd.Timestamp("2024-06-03"): {"sh.600000"}}
    kept, reason = pool.filter_names(["bj.830000", "sh.600000", "sz.000001"], pd.Timestamp("2024-06-03"), st_days, set())
    assert kept == ["sz.000001"]
    assert reason == ""
    empty, gap = pool.filter_names(["sz.000001"], pd.Timestamp("2024-06-04"), st_days, set())
    assert empty == []
    assert gap == "st_day_missing"


def test_cleanup_requires_the_row_to_be_visible_before_the_session():
    frame = pd.DataFrame({
        "instrument_id": ["sh.600001", "sh.600002"],
        "entered_delisting_period_v2": [True, True],
        "delist_period_start": ["20240601", "20240601"],
        "delist_date": ["20240620", "20240620"],
        "available_at": [
            pd.Timestamp("2024-05-31 18:00", tz="Asia/Shanghai"),
            pd.Timestamp("2024-06-03 18:00", tz="Asia/Shanghai"),
        ],
    })
    rows = pool.delist_cleanup_rows(frame)
    assert pool.cleanup_ids(rows, date(2024, 6, 3)) == {"sh.600001"}
    assert pool.cleanup_ids(rows, date(2024, 6, 21)) == set()


def test_raw_open_return_adds_cash_and_share_ratio_without_adj_close():
    assert pool.period_return(10.0, 9.0, 1.0, 0.0) == 0.0
    assert abs(pool.period_return(10.0, 10.0, 0.0, 0.1) - 0.1) < 1e-12


def test_primary_cost_uses_strategy_v1_rates_and_5bp_is_separate():
    primary, extra = pool.traded_cost({}, {"sh.600000": 1.0}, commission=0.00025, stamp=0.0005)
    assert primary == 0.00025 + 0.00025
    assert extra == 0.0005
