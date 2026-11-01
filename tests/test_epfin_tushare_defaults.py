"""Accepted tushare EP / financials defaults (Leo Eng confirm 2026-10-10 21:35 ET)."""
from datetime import date

import pandas as pd
import pytest

from quantlab.data.v2_readers import (
    DEFAULT_FINANCIALS_PIT_TUSHARE,
    financials_metric_asof,
    load_ep_research,
    load_financials_pit,
)

pytestmark = pytest.mark.skipif(not DEFAULT_FINANCIALS_PIT_TUSHARE.is_file(), reason="data missing")


def test_ep_default_is_pit_daily_no_lookahead():
    for sess in (date(2025, 6, 30), date(2026, 7, 15), date(2026, 10, 9)):
        v = load_ep_research(session=sess)
        assert v.source_variant == "tushare" and "ep_pit_daily_tushare" in v.path and v.promotable
        assert v.session <= sess
        fr = v.frame[v.frame["ep"].notna()]
        av = fr["available_at"].dt.tz_convert("Asia/Shanghai").dt.date
        assert not (av >= v.session).any()


def test_ep_explicit_tushare_asof_still_available():
    v = load_ep_research(session=date(2026, 7, 15), prefer="tushare")
    assert "ep_tushare_asof_20260630" in v.path


def test_ep_fallback_outside_pit_coverage_is_labeled():
    # daily PIT covers 2018-01-02..2026-10-09; pre-2018 falls back to research asof
    v = load_ep_research(session=date(2017, 6, 30))
    assert v.source_variant == "research" and not v.promotable
    assert "lookahead_outside_pit_coverage" in v.quality_label


def test_ep_pit_daily_covers_2019_no_lookahead():
    v = load_ep_research(session=date(2019, 6, 28))
    assert "ep_pit_daily_tushare" in v.path and v.promotable and v.session <= date(2019, 6, 28)
    fr = v.frame[v.frame["ep"].notna()]
    av = fr["available_at"].dt.tz_convert("Asia/Shanghai").dt.date
    assert not (av >= v.session).any()


def test_ocf_to_profit_default_tushare_pit_and_legacy_optin():
    f = load_financials_pit()
    o = f.frame[f.frame["metric"] == "ocf_to_profit"]
    assert set(o["source"].unique()) == {"ocf_to_profit_pit_tushare"}
    assert "ocf_to_profit=tushare_pit" in f.quality_label
    g = load_financials_pit(ocf_source="legacy_research")
    assert "ocf_to_profit=legacy_research" in g.quality_label


def test_financials_default_tushare_pit():
    f = load_financials_pit()
    assert f.source_variant == "tushare" and "net_profit" in f.metrics
    sess = date(2026, 4, 1)
    sub = f.frame[f.frame["metric"] == "net_profit"]
    out = financials_metric_asof(sub, sess, None, "net_profit", negative_as_missing=False)
    assert out
    ad = sub["available_at"].dt.tz_convert("Asia/Shanghai").dt.date
    assert (sub[sub["instrument_id"].isin(list(out)[:50])].pipe(lambda d: d[ad.loc[d.index] <= sess])).shape[0] > 0
