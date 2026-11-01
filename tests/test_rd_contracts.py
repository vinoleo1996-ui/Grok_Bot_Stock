"""Failure conditions for the research ledger. Do not weaken these to match a bug."""
from datetime import date, datetime
from zoneinfo import ZoneInfo

import pandas as pd
import pytest

from quantlab.config import ROOT
from quantlab.data.v2_readers import (
    V2DataRoots,
    default_v2_roots,
    load_etf_510300,
    load_merged_calendar,
    load_merged_panel,
)
from quantlab.universe.d1_masks import filter_research_instruments, sw_l1_asof


def _members():
    return pd.DataFrame({
        "instrument_id": ["sh.600000", "sh.600000", "sh.600001"],
        "sw_code": ["801010", "801020", "801030"],
        "sw_name": ["early", "same-day", "naive-prior"],
        "in_date": ["2020-01-01", "2020-01-01", "2020-01-01"],
        "out_date": [None, None, None],
        "available_at": [
            datetime(2026, 7, 1, 18, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
            datetime(2026, 7, 2, 0, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
            "2026-07-01",
        ],
    })


def test_sw_l1_asof_drops_rows_not_published_before_the_session():
    assigned = sw_l1_asof(_members(), date(2026, 7, 2), ["sh.600000", "sh.600001"])
    assert assigned["sh.600000"].sw_name == "early"
    assert assigned["sh.600000"].is_unknown_bucket is False
    assert assigned["sh.600001"].sw_name == "naive-prior"
    assert "sh.600000" in assigned
    assert assigned["sh.600000"].sw_code == "801010"


def test_sw_l1_asof_empty_request_returns_no_rows():
    assert sw_l1_asof(_members(), date(2026, 7, 2), []) == {}


def test_sw_l1_asof_same_day_publication_is_excluded_even_when_membership_dates_match():
    assigned = sw_l1_asof(_members(), date(2026, 7, 2), ["sh.600000"])
    assert assigned["sh.600000"].sw_name != "same-day"


def test_missing_panel_and_etf_files_fail():
    missing = ROOT / "data" / "v2" / "does_not_exist_rd"
    with pytest.raises(FileNotFoundError) as panel:
        load_merged_panel("sh.600000", d0_root=missing, asof_extend_dir=missing)
    assert "sh.600000.parquet" in str(panel.value)
    with pytest.raises(FileNotFoundError) as etf:
        load_etf_510300(roots=V2DataRoots(missing, missing, missing / "etf.parquet"))
    assert str(etf.value).endswith("etf.parquet")


def test_present_panel_is_read_without_a_return_column_or_promotion(tmp_path):
    d0 = tmp_path / "d0" / "panels"
    extend = tmp_path / "extend" / "panels"
    d0.mkdir(parents=True)
    extend.mkdir(parents=True)
    pd.DataFrame({
        "event_time": [date(2026, 6, 30), date(2026, 7, 1)],
        "close": [10.0, 11.0],
    }).to_parquet(d0 / "sh.600000.parquet")
    pd.DataFrame({
        "event_time": [date(2026, 6, 30), date(2026, 7, 2)],
        "close": [99.0, 12.0],
    }).to_parquet(extend / "sh.600000.parquet")
    view = load_merged_panel(
        "sh.600000",
        d0_root=tmp_path / "d0",
        asof_extend_dir=tmp_path / "extend",
        d0_asof_cutoff=date(2026, 6, 30),
    )
    assert view.promotion_approved is False
    assert "return" not in view.frame.columns
    assert sorted(view.frame["close"].tolist()) == [10.0, 12.0]


def test_present_etf_file_is_read_and_stays_unpromoted(tmp_path):
    path = tmp_path / "etf_daily_adj.parquet"
    pd.DataFrame({
        "ts_code": ["510300.SH", "510500.SH"],
        "trade_date": ["20260701", "20260701"],
        "close": [4.0, 8.0],
    }).to_parquet(path)
    bundle = load_etf_510300(roots=V2DataRoots(tmp_path, tmp_path, path))
    assert bundle.promotion_approved is False
    assert bundle.n_bars == 1
    assert bundle.panel_frame["close"].tolist() == [4.0]
    assert "return" not in bundle.panel_frame.columns


def test_extend_panel_falls_back_per_instrument_when_the_passed_dir_lacks_it(tmp_path):
    d0 = tmp_path / "d0" / "panels"
    primary = tmp_path / "asof_extend_tushare_202610" / "panels"
    sibling = tmp_path / "asof_extend_202610" / "panels"
    d0.mkdir(parents=True)
    primary.mkdir(parents=True)
    sibling.mkdir(parents=True)
    pd.DataFrame({"event_time": [date(2026, 6, 30)], "close": [10.0]}).to_parquet(d0 / "sh.600000.parquet")
    pd.DataFrame({"event_time": [date(2026, 7, 2)], "close": [12.0]}).to_parquet(sibling / "sh.600000.parquet")
    view = load_merged_panel(
        "sh.600000",
        d0_root=tmp_path / "d0",
        asof_extend_dir=tmp_path / "asof_extend_tushare_202610",
        d0_asof_cutoff=date(2026, 6, 30),
    )
    assert "extend_per_id_fallback" in view.quality_notes
    assert sorted(view.frame["close"].tolist()) == [10.0, 12.0]


def test_unrelated_extend_dir_does_not_search_the_sibling(tmp_path):
    missing = tmp_path / "does_not_exist_rd"
    with pytest.raises(FileNotFoundError):
        load_merged_panel("sh.600000", d0_root=missing, asof_extend_dir=missing)


def test_calendar_view_exposes_the_fields_strategy_feed_reads(tmp_path):
    extend = tmp_path / "asof_extend_tushare_202610"
    extend.mkdir()
    pd.DataFrame({"session": ["2026-07-01", "2026-07-02"], "is_open": [1, 1]}).to_parquet(extend / "calendar.parquet")
    (extend / "manifest.json").write_text('{"d0_as_of": "2026-06-30"}', encoding="utf-8")
    view = load_merged_calendar(d0_root=tmp_path / "d0", asof_extend_dir=extend)
    assert view.first_session == date(2026, 7, 1)
    assert view.last_session == date(2026, 7, 2)
    assert view.n_sessions == 2
    assert view.d0_asof_cutoff == date(2026, 6, 30)
    assert view.promotion_approved is False
    assert default_v2_roots().sw_l1_path.name == "industry_members_sw_l1_tushare.parquet"


def test_research_instruments_keep_only_stock_and_equity_etf():
    frame = pd.DataFrame({
        "instrument_id": ["sh.600000", "sh.510300", "fut.IF"],
        "asset_type": ["stock", "equity_etf", "future"],
    })
    kept = filter_research_instruments(frame)
    assert kept["instrument_id"].tolist() == ["sh.600000", "sh.510300"]
    with pytest.raises(ValueError, match="instruments_asset_type_missing"):
        filter_research_instruments(frame.drop(columns=["asset_type"]))


@pytest.mark.xfail(reason="architect-002: quantlab/smallcap/panel.py:94 still backfills adj factor", strict=True)
def test_adj_factor_gap_is_not_filled_from_a_later_factor():
    line = (ROOT / "quantlab" / "smallcap" / "panel.py").read_text(encoding="utf-8").splitlines()[93]
    assert "bfill" not in line
