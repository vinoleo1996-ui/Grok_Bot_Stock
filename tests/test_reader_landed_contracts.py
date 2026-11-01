"""Readers accept the columns and paths that actually landed. They do not rewrite those files."""
from datetime import date

import pandas as pd

from quantlab.data.v2_readers import (
    V2DataRoots,
    etf_510300_bars,
    financials_metric_asof,
    load_dividends,
    load_ep_research,
    load_etf_510300,
    load_financials_pit,
    load_merged_calendar,
)


def _roots(tmp_path, **paths):
    etf = paths.pop("etf_panel_path", tmp_path / "etf.parquet")
    return V2DataRoots(tmp_path, tmp_path, etf, **paths)


def test_ep_uses_e_available_at_without_rewriting_the_file(tmp_path):
    path = tmp_path / "ep_pit_daily_tushare.parquet"
    pd.DataFrame({
        "instrument_id": ["sh.600000", "sh.600000"],
        "trade_date": ["20240603", "20240604"],
        "ep": [0.1, 0.2],
        "e_available_at": [
            pd.Timestamp("2024-06-02 18:00", tz="Asia/Shanghai"),
            pd.Timestamp("2024-06-04 18:00", tz="Asia/Shanghai"),
        ],
    }).to_parquet(path, index=False)
    view = load_ep_research(roots=_roots(tmp_path, ep_pit_path=path), session=date(2024, 6, 4))
    assert "available_at_from_e_available_at" in view.quality_label
    assert view.promotion_approved is False
    assert view.frame["ep"].tolist() == [0.1]
    assert "available_at" not in pd.read_parquet(path).columns


def test_wide_financials_metric_uses_the_named_column(tmp_path):
    path = tmp_path / "financials_pit_tushare.parquet"
    pd.DataFrame({
        "instrument_id": ["sh.600000", "sh.600000"],
        "net_profit": [1.0, 5.0],
        "available_at": [
            pd.Timestamp("2024-06-01 18:00", tz="Asia/Shanghai"),
            pd.Timestamp("2024-06-03 18:00", tz="Asia/Shanghai"),
        ],
    }).to_parquet(path, index=False)
    view = load_financials_pit(roots=_roots(tmp_path, financials_pit_path=path))
    assert "net_profit" in view.metrics
    assert view.quality_label == "wide_columns"
    assert view.promotion_approved is False
    values = financials_metric_asof(view.frame, date(2024, 6, 4), ["sh.600000"], "net_profit")
    assert values == {"sh.600000": 5.0}


def test_dividends_land_beside_corporate_actions_and_gain_instrument_ids(tmp_path):
    path = tmp_path / "dividend_by_exdate_tushare.parquet"
    pd.DataFrame({
        "ts_code": ["000001.SZ", "600000.SH", "830000.BJ"],
        "ann_date": ["20240601", "20240601", "20240601"],
        "ex_date": ["20240610", "20240610", "20240610"],
        "div_proc": ["实施", "实施", "实施"],
        "cash_div_tax": [0.1, 0.2, 0.3],
        "stk_div": [0.0, 0.0, 0.0],
    }).to_parquet(path, index=False)
    view = load_dividends(path)
    assert view.promotion_approved is False
    assert view.frame["instrument_id"].tolist() == ["sz.000001", "sh.600000", "bj.830000"]
    assert "available_at_from_ann_date" in view.quality_label


def test_etf_daily_adj_vol_and_amount_match_the_d0_panel_units(tmp_path):
    path = tmp_path / "etf_daily_adj.parquet"
    pd.DataFrame({
        "ts_code": ["510300.SH", "159915.SZ"],
        "trade_date": ["20240603", "20240603"],
        "open": [3.58, 1.0],
        "high": [3.60, 1.0],
        "low": [3.50, 1.0],
        "close": [3.587, 1.0],
        "vol": [10.0, 99.0],
        "amount": [1.5, 9.0],
    }).to_parquet(path, index=False)
    bundle = load_etf_510300(roots=_roots(tmp_path, etf_panel_path=path))
    assert bundle.promotion_approved is False
    assert "amount_cny_from_thousand" in bundle.instrument.quality_status
    bars = etf_510300_bars(bundle, date(2024, 6, 3), date(2024, 6, 3))
    assert len(bars) == 1
    assert bars[0].volume == 10.0
    assert bars[0].amount == 1500.0
    assert bars[0].close == 3.587
    stored = pd.read_parquet(path)
    assert "volume" not in stored.columns
    assert stored.loc[stored.ts_code == "510300.SH", "amount"].iloc[0] == 1.5


def test_fund_extend_appends_later_sessions_from_trade_date(tmp_path):
    from quantlab.platform.execution import _extend_fund_panel

    etf = tmp_path / "etf.parquet"
    pd.DataFrame({
        "ts_code": ["510300.SH", "510300.SH"],
        "trade_date": ["20240603", "20240604"],
        "open": [3.5, 3.6],
        "high": [3.6, 3.7],
        "low": [3.4, 3.5],
        "close": [3.58, 3.62],
        "vol": [10.0, 20.0],
        "amount": [1.5, 2.0],
    }).to_parquet(etf, index=False)
    base = pd.DataFrame({
        "event_time": [pd.Timestamp("2024-06-03")],
        "open": [3.5],
        "high": [3.6],
        "low": [3.4],
        "close": [3.58],
        "volume": [10.0],
        "amount": [1500.0],
    })
    diag = {}
    out = _extend_fund_panel("sh.510300", base, _roots(tmp_path, etf_panel_path=etf), diag)
    assert len(out) == 2
    assert float(out.iloc[-1]["volume"]) == 20.0
    assert float(out.iloc[-1]["amount"]) == 2000.0
    assert diag["fund_panel_extended"]["sh.510300"]["note"] == "volume_from_vol amount_cny_from_thousand"
    assert _extend_fund_panel("sh.600000", base, _roots(tmp_path, etf_panel_path=etf), {}) is base


def test_tushare_extend_calendar_falls_back_to_the_sibling_dir(tmp_path):
    primary = tmp_path / "asof_extend_tushare_202610"
    sibling = tmp_path / "asof_extend_202610"
    primary.mkdir()
    sibling.mkdir()
    pd.DataFrame({"session": ["2024-06-03"], "is_open": [1]}).to_parquet(sibling / "calendar.parquet")
    view = load_merged_calendar(d0_root=tmp_path / "d0", asof_extend_dir=primary)
    assert view.includes_extend is True
    assert view.path_primary.endswith("asof_extend_202610/calendar.parquet")
    assert view.promotion_approved is False
