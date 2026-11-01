"""Unit smoke: turn_compare weight dump helpers (2–3 sessions, no Full D1).

Research-only. promotion_approved=false.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from quantlab.portfolio.v2_strategy_paper_turn_compare import (
    ETF_WEIGHT_INSTRUMENT_ID,
    _append_book_weight_rows,
    _write_weight_parquet,
)


def test_append_and_write_three_sessions(tmp_path: Path):
    """Tiny smoke: 3 rebalance sessions → long parquet schema Eng/E1 expect."""
    tw_a: list[dict] = []
    tw_b: list[dict] = []
    planned: list[dict] = []
    sessions = [date(2024, 6, 3), date(2024, 6, 18), date(2024, 7, 2)]

    for i, sess in enumerate(sessions):
        # planned pre-fill
        _append_book_weight_rows(
            planned,
            session=sess,
            stock_weights={"sh.600000": 0.10 + 0.01 * i, "sz.000001": 0.05},
            etf_weight=0.40,
        )
        # post-fill A (slightly different from planned)
        _append_book_weight_rows(
            tw_a,
            session=sess,
            stock_weights={"sh.600000": 0.09 + 0.01 * i, "sz.000001": 0.05},
            etf_weight=0.39,
        )
        # post-fill B
        _append_book_weight_rows(
            tw_b,
            session=sess,
            stock_weights={"sh.600000": 0.08, "sz.000002": 0.06},
            etf_weight=0.38,
        )

    p_a = _write_weight_parquet(tmp_path / "target_weights.parquet", tw_a)
    p_plan = _write_weight_parquet(tmp_path / "planned_target_weights.parquet", planned)
    p_b = _write_weight_parquet(tmp_path / "arm_b_target_weights.parquet", tw_b)

    for p in (p_a, p_plan, p_b):
        assert p.is_file()
        df = pd.read_parquet(p)
        assert list(df.columns) == ["session", "instrument_id", "weight"]
        assert df["weight"].dtype == np.float32
        assert str(df["session"].dtype) in ("object", "string", "str", "string[python]") or str(
            df["session"].dtype
        ).startswith("string")
        assert set(df["session"].astype(str)) == {str(s) for s in sessions}
        assert ETF_WEIGHT_INSTRUMENT_ID in set(df["instrument_id"].astype(str))
        # 2 stocks + 1 ETF per session
        assert len(df) == 3 * 3

    df_a = pd.read_parquet(p_a)
    etf_rows = df_a[df_a["instrument_id"] == ETF_WEIGHT_INSTRUMENT_ID]
    assert len(etf_rows) == 3
    assert float(etf_rows["weight"].iloc[0]) == pytest.approx(0.39, abs=1e-6)

    df_plan = pd.read_parquet(p_plan)
    assert float(
        df_plan.loc[
            (df_plan["session"] == "2024-06-03")
            & (df_plan["instrument_id"] == "sh.600000"),
            "weight",
        ].iloc[0]
    ) == pytest.approx(0.10, abs=1e-6)


def test_empty_rows_writes_schema_only(tmp_path: Path):
    p = _write_weight_parquet(tmp_path / "target_weights.parquet", [])
    df = pd.read_parquet(p)
    assert list(df.columns) == ["session", "instrument_id", "weight"]
    assert len(df) == 0
    assert df["weight"].dtype == np.float32


def test_skips_near_zero_weights():
    rows: list[dict] = []
    _append_book_weight_rows(
        rows,
        session="2024-06-03",
        stock_weights={"sh.600000": 1e-15, "sz.000001": 0.1},
        etf_weight=0.0,
    )
    assert len(rows) == 1
    assert rows[0]["instrument_id"] == "sz.000001"
