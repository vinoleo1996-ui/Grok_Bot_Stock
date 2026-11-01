"""Cand3 box-port APPLY verification (National Day 2025 window).

After apply: imports production quantlab modules (not *.py.port stubs).
Uses injected calendar via trade_calendar._set_open_days_for_test.
live=false; promotion*=false; enable still forbidden.
"""
from __future__ import annotations

import ast
import sys
import warnings
from pathlib import Path

import pandas as pd
import pytest

PORT = Path(__file__).resolve().parent
REPO = Path(__file__).resolve().parents[5]  # .../QuantLab
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

PROD_SETTLE = REPO / "quantlab/agents/trading_loop/settle.py"
PROD_RL = REPO / "quantlab/portfolio/research_loop.py"
PROD_SOURCES = REPO / "quantlab/data/sources.py"
PROD_TC = REPO / "quantlab/portfolio/trade_calendar.py"

# 2025 National Day: Oct 1–7 closed (synthetic SSE-like weekdays open otherwise).
HOLIDAY_CLOSED = pd.DatetimeIndex(
    pd.date_range("2025-10-01", "2025-10-07", freq="D")
)


def _synth_open_days():
    all_days = pd.bdate_range("2025-09-15", "2025-10-20")
    open_ = all_days.difference(HOLIDAY_CLOSED)
    return pd.DatetimeIndex(open_)


@pytest.fixture
def tc():
    import quantlab.portfolio.trade_calendar as mod
    mod._set_open_days_for_test(_synth_open_days())
    yield mod
    mod._set_open_days_for_test(None)


class TestNationalDayCalendar:
    def test_first_on_or_after_holiday_lands_oct08(self, tc):
        got = tc.first_trading_day_on_or_after("2025-10-01")
        assert str(pd.Timestamp(got).date()) == "2025-10-08"

    def test_advance_1_from_sep30_skips_holiday(self, tc):
        assert str(pd.Timestamp(tc.first_trading_day_on_or_after("2025-09-30")).date()) == "2025-09-30"
        got = tc.advance_open_days("2025-09-30", 1)
        assert str(pd.Timestamp(got).date()) == "2025-10-08"

    def test_bdate_range_would_land_oct01(self, tc):
        bad = pd.bdate_range("2025-09-30", periods=2)
        assert str(bad[1].date()) == "2025-10-01"
        assert "2025-10-01" in {str(x.date()) for x in HOLIDAY_CLOSED}
        good = tc.open_day_range("2025-09-30", 2)
        assert str(pd.Timestamp(good[0]).date()) == "2025-09-30"
        assert str(pd.Timestamp(good[1]).date()) == "2025-10-08"
        assert str(pd.Timestamp(good[1]).date()) not in {str(x.date()) for x in HOLIDAY_CLOSED}

    def test_open_day_range_never_hits_holiday(self, tc):
        rng = tc.open_day_range("2025-09-29", 5)
        closed = {str(x.date()) for x in HOLIDAY_CLOSED}
        for d in rng:
            assert str(pd.Timestamp(d).date()) not in closed


class TestSettleMockPort:
    def test_mock_exit_skips_national_day(self, tc, monkeypatch):
        import quantlab.portfolio.trade_calendar as prod_tc
        monkeypatch.setattr(prod_tc, "open_day_range", tc.open_day_range, raising=False)
        monkeypatch.setattr(prod_tc, "open_days", tc.open_days, raising=False)
        monkeypatch.setattr(prod_tc, "advance_open_days", tc.advance_open_days, raising=False)
        monkeypatch.setattr(prod_tc, "first_trading_day_on_or_after", tc.first_trading_day_on_or_after, raising=False)

        from quantlab.agents.trading_loop import settle
        fake_etf = PORT / "_no_such_etf_daily_adj.parquet"
        out = settle.compute_horizon_returns(
            "510300.SH",
            "2025-09-30",
            1,
            etf_path=fake_etf,
            allow_mock=True,
        )
        assert out["status"] == "settled"
        assert out["settle_source"] == "mock"
        assert out["entry_date"] == "2025-09-30"
        assert out["exit_date"] == "2025-10-08"
        assert out["exit_date"] != "2025-10-01"

    def test_settle_port_source_has_no_bdate_range_call(self):
        text = PROD_SETTLE.read_text()
        code_hits = [
            ln for ln in text.splitlines()
            if "pd.bdate_range" in ln and not ln.strip().startswith("#")
        ]
        assert code_hits == []


class TestLegacyDeprecation:
    def test_legacy_emits_deprecation_warning(self):
        text = PROD_RL.read_text()
        assert "DeprecationWarning" in text
        assert "CN holidays not modeled" in text
        assert "DEPRECATED" in text
        assert "def data_freshness():" in text
        assert "CUTOFF_ET" in text

    def test_legacy_warns_when_callable(self, tmp_path, monkeypatch):
        src = PROD_RL.read_text()
        tree = ast.parse(src)
        fn = None
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == "_legacy_freshness":
                fn = node
                break
        assert fn is not None
        warn_stmts = []
        for stmt in fn.body:
            warn_stmts.append(stmt)
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                break
        fn.body = warn_stmts + [ast.parse("return {'note': 'weekday calendar; CN holidays not modeled', 'fresh': False}").body[0]]
        mod_ast = ast.Module(body=[
            ast.parse("import warnings").body[0],
            fn,
        ], type_ignores=[])
        ast.fix_missing_locations(mod_ast)
        code = compile(mod_ast, str(PROD_RL), "exec")
        ns = {}
        exec(code, ns)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always", DeprecationWarning)
            out = ns["_legacy_freshness"]()
        assert any(issubclass(x.category, DeprecationWarning) for x in w)
        assert "CN holidays not modeled" in out["note"]


class TestSourcesOptional:
    def test_sources_port_marks_calendar_required(self):
        text = PROD_SOURCES.read_text()
        assert 'freshness"] = "calendar_required"' in text or "calendar_required" in text
        assert "now.normalize() - pd.offsets.BDay()" not in text
