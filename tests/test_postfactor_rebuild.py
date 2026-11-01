"""2026-10-11 post factor rebuild: fund corporate actions default on, verified bond-futures fees/margins,
LPR loader, real index-futures loader."""
import pandas as pd, pytest
from pathlib import Path
from quantlab.platform import futures as fu
from quantlab.platform.futures import margin_rate, bond_fee_per_lot, load_lpr, load_shibor

REPO = Path(__file__).resolve().parents[1]


def test_bond_tables_verified():
    assert margin_rate("TF", "2025-01-02", "cffex_current") == 0.01   # hist (default) = 1.2%, see test_bond_fut_hist.py
    assert margin_rate("T", "2025-01-02") == 0.02 and margin_rate("TL", "2025-01-02") == 0.035
    assert bond_fee_per_lot("2025-01-02") == (3.0, 3.0, 0.0)


@pytest.mark.skipif(not (REPO / "data/v2/rates/lpr.parquet").is_file(), reason="no lpr")
def test_load_lpr():
    s = load_lpr("1Y", start="2026-01-01")
    assert len(s) and s.between(0.01, 0.1).all() and s.index.is_monotonic_increasing
    assert load_lpr("5Y").index.min() >= pd.Timestamp("2019-08-01")


@pytest.mark.skipif(not (REPO / "data/v2/rates/shibor.parquet").is_file(), reason="no shibor")
def test_shibor_3m_no_gap_to_20261010():
    s = load_shibor("3M", start="2026-05-01")
    assert s.index.max() >= pd.Timestamp("2026-10-10")
    assert s.index.to_series().diff().dt.days.max() <= 9  # only holiday gaps


@pytest.mark.skipif(not (REPO / "data/v2/futures/raw/daily/IF2412.CFX.parquet").is_file(), reason="no futures bars")
def test_load_index_futures_panels_real():
    fp = fu.load_index_futures_panels(contracts=["IF2412", "IF2503"], start="2024-10-01", end="2024-12-31")
    assert fp.expiry["IF2412"] == pd.Timestamp("2024-12-20")
    assert fp.settle.loc["2024-12-20", "IF2412"] == pytest.approx(3935.41)
    assert fp.settle.index.max() <= pd.Timestamp("2024-12-31")


@pytest.mark.skipif(not (REPO / "data/v2/etf/raw/fund_div.parquet").is_file(), reason="no fund_div")
def test_fund_corporate_actions_510300_default_on():
    from quantlab.platform.execution import load_execution_panels, corporate_action_arrays
    p, d = load_execution_panels(["sh.510300"], "2024-06-01", "2026-10-09")
    cd = p.cash_div["sh.510300"]
    ev = cd[cd > 0]
    assert list(ev.index.strftime("%Y-%m-%d")) == ["2025-06-18", "2026-01-19"]
    assert ev.iloc[-1] == pytest.approx(0.123, abs=1e-6)
    flags = []
    CD, SR, FR = corporate_action_arrays(p.aligned(), flags=flags)
    assert not flags and (FR == 1).all()   # cash events agree with fund_adj; no factor-only events
    p0, _ = load_execution_panels(["sh.510300"], "2024-06-01", "2026-10-09", fund_adj_factor_actions=False)
    assert p0.cash_div is None or float(p0.cash_div["sh.510300"].sum()) == 0.0


def test_stock_factor_is_rebuilt_column():
    from quantlab.data.v2_readers import load_merged_panel
    fr = load_merged_panel("sz.000620").frame
    if fr is None or "factor_d0_orig" not in fr.columns:
        pytest.skip("no rebuilt factor")
    assert "factor_basis" in fr.columns  # engine reads 'factor' (rebuilt), not factor_d0_orig
