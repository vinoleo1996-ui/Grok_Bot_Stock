import numpy as np, pandas as pd, pytest
from quantlab.platform import execution as ex
from quantlab.platform import futures as fu


def test_eb_classification_rules():
    for c in ("sh.132015", "sz.120001", "132015.SH"):
        assert ex.instrument_type(c) == "eb" and ex.is_exchange_bond(c) and not ex.is_convertible_bond(c)
        assert ex.stamp_exempt(c) and ex.tick_for_code(c) == 0.001
        assert ex.lot_rule_for(c) == ex.LotRule(10, 10)
        assert ex.derived_limit_pct(c, "2024-01-02") is None      # no +-20% for EBs
    assert ex.derived_limit_pct("sh.113050", "2024-01-02") == 0.20
    assert ex.instrument_type("sh.600000") == "stock"


def test_eb_commission_and_no_limit():
    d = pd.bdate_range("2024-01-02", periods=4)
    c = pd.DataFrame({"sh.132015": [100.0, 100.0, 125.0, 125.0]}, index=d)
    p = ex.ExecPanels(close=c, open=c.copy(), high=c.copy(), low=c.copy(), volume=c * 0 + 1e6, amount=c * 0 + 1e8)
    cfg = ex.ExecConfig(fill="next_open", price_tick="auto", commission=0.0003, min_commission=5.0, slippage=0.0,
                        participation_cap=None, enforce_limits=True, impact_k=0.0)
    r = ex.run_weight_schedule(p, {d[1]: {"sh.132015": 0.5}}, initial_cash=1_000_000, config=cfg, record_fills=True)
    f = r["fills"]
    assert len(f) == 1 and f[0]["qty"] % 10 == 0 and f[0]["price"] == 125.0   # +25% open: not limited
    assert abs(f[0]["commission"] - max(1.0, f[0]["qty"] * 125.0 * 0.0001)) < 1e-6
    assert r["costs"]["stamp"] == 0
    # same move on a CB after 2022-08-01 is blocked by the derived +-20% band
    p2 = ex.ExecPanels(close=c.rename(columns={"sh.132015": "sh.113050"}), open=c.rename(columns={"sh.132015": "sh.113050"}),
                       volume=c.rename(columns={"sh.132015": "sh.113050"}) * 0 + 1e6, amount=c.rename(columns={"sh.132015": "sh.113050"}) * 0 + 1e8)
    r2 = ex.run_weight_schedule(p2, {d[1]: {"sh.113050": 0.5}}, initial_cash=1_000_000, config=cfg, record_fills=True)
    assert f[0]["date"] == str(d[2].date())                      # EB fills on the +25% day
    assert r2["fills"][0]["date"] == str(d[3].date())            # CB deferred past the limit day


@pytest.mark.skipif(not ex._CB_TABLE.is_file(), reason="no cb table")
def test_cb_table_reader_units():
    diag = {}
    out = ex.load_cb_panels(["sh.113050", "sh.132024"], "2026-09-01", "2026-10-09", diag=diag)
    assert "cb_daily.parquet" in diag["cb_source"]["dir"]
    r = (out["amount"] / (out["volume"] * out["close"])).stack()
    assert r.between(0.9, 1.1).mean() > 0.95


@pytest.mark.skipif(not ex._FUND_TABLE.is_file(), reason="no etf table")
def test_fund_table_reader_and_adj_flag_off():
    out = ex.load_fund_daily_panels(["sz.159915"], "2026-09-01", "2026-10-09")
    assert out["close"].index.max() == pd.Timestamp("2026-10-09")
    r = (out["amount"] / (out["volume"] * out["close"])).stack()
    assert r.between(0.9, 1.1).mean() > 0.95
    p1, _ = ex.load_execution_panels(["sz.159915"], "2026-09-01", "2026-10-09")   # default ON since 2026-10-11 rebuild
    assert p1.adj_factor is not None and p1.adj_factor["sz.159915"].notna().all()
    p, diag = ex.load_execution_panels(["sz.159915"], "2026-09-01", "2026-10-09", fund_adj_factor_actions=False)
    assert p.adj_factor is None or "sz.159915" not in p.adj_factor.columns or p.adj_factor["sz.159915"].isna().all()
    assert "off" in diag.get("fund_adj_factor_actions", "")


def test_margin_table_2022_row_replaced():
    for r in ("IF", "IH", "IC", "IM"):
        assert fu.margin_rate(r, "2026-10-09") == 0.12
    assert fu.margin_rate("IC", "2021-01-04") == 0.12 and fu.margin_rate("IF", "2021-01-04") == 0.10
    assert fu.fee_rates("2024-01-02") == (0.000023, 0.000023, 0.00023)


def test_load_shibor_and_511880():
    s = fu.load_shibor("ON", start="2026-01-01")
    assert s.index.max() >= pd.Timestamp("2026-10-01") and 0 < s.median() < 0.1
    assert fu.load_shibor("3M").name == "shibor_3m"
    r = fu.load_511880_returns("2026-01-01", "2026-10-09")
    assert r.index.max() == pd.Timestamp("2026-10-09") and abs(r).max() < 0.01
    d = pd.bdate_range("2026-09-01", "2026-09-30")
    rr = fu.cash_rate_per_session(d, s, series_kind="annual", day_count=360)
    assert rr[0] == 0 and 0 < rr[1:].mean() < 1e-3
