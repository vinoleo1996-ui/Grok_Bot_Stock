"""2026-10-11: bond futures from Data's bond_fut_*.parquet, dated margin history (Tushare fut_settle),
missing-settle repair, and regression for Beta's 2019-02-15 T1903 fut_roll_no_next."""
import numpy as np, pandas as pd, pytest
import quantlab.platform.futures as fu
from quantlab.platform.execution import ExecConfig, ExecPanels, ZERO_COST, run_weight_schedule

ZC = dict(fill="next_open", enforce_limits=False, price_tick="auto", **ZERO_COST)


def test_margin_hist_loaded_and_sensitivity():
    assert fu.BOND_MARGIN_ASSUMED_FLAT is False
    assert fu.margin_rate("TF", "2013-10-08") == 0.03
    assert fu.margin_rate("TF", "2014-06-03") == 0.02
    assert fu.margin_rate("TF", "2015-01-05") == 0.015
    assert fu.margin_rate("TF", "2025-01-02") == 0.012
    assert fu.margin_rate("TF", "2025-01-02", "cffex_current") == 0.01
    assert fu.margin_rate("T", "2015-09-01") == 0.02          # 4%/3% rows in fut_settle are delivery-month step-ups
    assert fu.BOND_MARGIN_SOURCE == "official"
    assert fu.margin_rate("TS", "2020-09-30") == 0.005 and fu.margin_rate("TF", "2020-09-30") == 0.012   # spike not official
    assert fu.margin_rate("TF", "2020-09-30", "settle_observed") == 0.014
    assert fu.margin_rate("TS", "2020-09-30", "settle_observed") == 0.006
    assert fu.margin_rate("TF", "2015-03-16") == 0.012 and fu.margin_rate("TF", "2015-03-13") == 0.015
    assert fu.margin_rate("T", "2015-03-20") == 0.02 and fu.margin_rate("TS", "2018-08-17") == 0.005
    assert fu.margin_rate("TL", "2025-01-02") == 0.035
    # hist base excludes step-ups -> no double count with bond_delivery_margin
    assert all(fu.margin_rate(r, "2025-01-02") < fu.BOND_DELIVERY_MARGIN[r] for r in ("T", "TF", "TS", "TL"))
    assert fu.BOND_FEE_ASSUMED and fu.bond_fee_per_lot("2025-01-02") == (3.0, 3.0, 0.0)
    assert fu.BOND_DELIVERY_FEE_PER_LOT == 5.0


def test_config_margin_source_used_by_book():
    D = pd.bdate_range("2025-01-02", periods=5)
    S = pd.DataFrame({"TF2506": 100.0}, index=D)
    for src, rate in (("hist", 0.012), ("settle_observed", 0.012), ("cffex_current", 0.01)):
        fb = fu.FuturesBook(fu.FuturesLeg(fu.FuturesPanels(settle=S), fu.FuturesConfig(bond_margin_source=src)), D, [])
        fb.pos[0] = 3
        assert fb.margin_req(1) == pytest.approx(3 * 100.0 * 10_000 * rate)


def test_bond_files_match_raw_and_settle_repaired():
    b = fu.load_futures_panels(roots=("T", "TF"), start="2019-01-02", end="2019-03-29")
    r = fu.load_futures_panels(roots=("T", "TF"), start="2019-01-02", end="2019-03-29", bond_source="raw")
    pd.testing.assert_frame_equal(b.settle.sort_index(axis=1), r.settle.sort_index(axis=1), check_names=False)
    for d, nxt in (("2019-01-18", "2019-01-21"), ("2019-02-13", "2019-02-14"), ("2019-02-15", "2019-02-18")):
        assert pd.Timestamp(d) in b.settle.index               # day no longer dropped by pivot_table
        for c in ("T1903", "T1906"):
            assert b.settle.at[pd.Timestamp(d), c] == b.pre_settle.at[pd.Timestamp(nxt), c]
    assert b.expiry["T1906"] == pd.Timestamp("2019-06-14")


def test_regression_t1903_roll_2019_02_15():
    p = fu.load_futures_panels(roots=("T",), start="2018-12-03", end="2019-04-30")
    D = p.settle.index
    c = pd.DataFrame({"sh.510300": 4.0}, index=D)
    leg = fu.FuturesLeg(p, fu.FuturesConfig(roll_mode="roll", contract_months="quarterly", roll_days=15,
                                            bond_roll_rule="earlier_of", bond_exit_sessions_before_dm=3,
                                            bond_fee_override=(0, 0, 0)))
    r = run_weight_schedule(ExecPanels(close=c, open=c.copy(), volume=c * 0 + 1e9), {D[1]: {"T": 1.0}},
                            initial_cash=5_000_000, config=ExecConfig(**ZC), futures=leg)
    assert not any(e.get("reason") == "fut_roll_no_next" for e in r["events"])
    rolls = [(f["date"], f["code"], f["why"]) for f in r["fut_fills"] if f["why"] != "order"]
    assert rolls == [("2019-02-15", "T1903", "roll_out"), ("2019-02-15", "T1906", "roll_in")]


def test_choose_tolerates_missing_settle_row():
    D = pd.bdate_range("2019-02-01", periods=10)
    S = pd.DataFrame({"T1903": 98.0, "T1906": 97.5}, index=D)
    S.iloc[5, :] = np.nan
    fb = fu.FuturesBook(fu.FuturesLeg(fu.FuturesPanels(settle=S, expiry={"T1903": "2019-03-08", "T1906": "2019-06-14"}),
                                      fu.FuturesConfig(roll_days=15)), D, [])
    assert fb.choose("T", 5) is not None
