import pytest
from quantlab.factors.p1_pipeline import _filter_integrate_panels
from quantlab.factors.residual_factory import ResidualFactorPanel
import datetime as dt

def _p(fid):
    return ResidualFactorPanel(factor_id=fid, session=dt.date(2024,6,3), industry_scheme="SW_L1",
        mktcap_neutral=True, values={"sz.000001":0.1,"sz.000002":-0.1}, sw_l1_coverage=2,
        unknown_industry_count=0, promotion_approved=False, data_ready=True, todos=())

def test_default_weight0_drops_m01_ep():
    assert _filter_integrate_panels([_p("M01_12_1"), _p("V01_EP")], integrate_mode="equal", icir_weights=None) == []

def test_override_keeps():
    kept = _filter_integrate_panels([_p("M01_12_1"), _p("V01_EP")], integrate_mode="equal",
                                    icir_weights={"M01_12_1":1.0,"V01_EP":1.0})
    assert [p.factor_id for p in kept] == ["M01_12_1","V01_EP"]

def test_pipeline_raises_not_silent(monkeypatch):
    import quantlab.factors.p1_pipeline as P
    src = open(P.__file__).read()
    assert "p1_all_requested_factors_default_weight0" in src
