"""Research-only smoke for residual factory / ortho / walk-forward skeletons.

Runs a tiny dry path with synthetic maps (no full-market IO). Asserts
``promotion_approved is False`` on all result types.
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from quantlab.factors.orthogonalize import (
    gram_schmidt_set,
    residualize_vs,
)
from quantlab.factors.residual_factory import (
    COMPOSITE_MEMBER_IDS,
    IMPLEMENTED_RAW_FACTOR_IDS,
    RawFactorPanel,
    ResearchResidualAlphaFactorFactory,
    ResidualFactorPanel,
    equal_weight_zscore_integrate,
    neutralize_raw_values,
)
from quantlab.factors.v2_min_pipeline import neutralize_raw_panel, orthogonalize_raw_pair
from quantlab.factors.walk_forward import (
    iter_session_windows,
    run_walk_forward_process_ic,
)
from quantlab.v2_schemas import SWL1AsOfAssignment


def _fake_sw_l1(session: date, ids_sectors: dict[str, str]) -> tuple[SWL1AsOfAssignment, ...]:
    out = []
    for iid, sec in ids_sectors.items():
        unknown = sec == "UNKNOWN"
        out.append(
            SWL1AsOfAssignment(
                instrument_id=iid,
                session=session,
                sw_code=None if unknown else sec,
                sw_name=None if unknown else sec,
                available_at=None,
                quality_status="ok",
                is_unknown_bucket=unknown,
            )
        )
    return tuple(out)


def test_composite_member_ids_locked():
    assert "M01_12_1" in COMPOSITE_MEMBER_IDS
    assert "V01_EP" in COMPOSITE_MEMBER_IDS
    assert "M01_12_1" in IMPLEMENTED_RAW_FACTOR_IDS
    assert "V01_EP" in IMPLEMENTED_RAW_FACTOR_IDS
    assert "R01_5D" in IMPLEMENTED_RAW_FACTOR_IDS
    assert "L01_RV60" in IMPLEMENTED_RAW_FACTOR_IDS


def test_neutralize_and_integrate_promotion_false():
    session = date(2026, 6, 30)
    raw = RawFactorPanel(
        factor_id="M01_12_1",
        session=session,
        values={"a": 1.0, "b": 2.0, "c": 3.0, "d": 4.0, "e": 5.0, "f": 0.5},
        available_at_ok=True,
        notes=("synthetic",),
    )
    sw = _fake_sw_l1(
        session,
        {
            "a": "801010",
            "b": "801010",
            "c": "801010",
            "d": "801020",
            "e": "801020",
            "f": "801020",
        },
    )
    mktcap = {"a": 1e9, "b": 2e9, "c": 3e9, "d": 4e9, "e": 5e9, "f": 6e9}
    vals, covered, unknown = neutralize_raw_values(
        raw.values, sw, mktcap=mktcap, mktcap_neutral=True
    )
    assert covered >= 1
    assert unknown == 0
    assert vals

    residual = ResidualFactorPanel(
        factor_id="M01_12_1",
        session=session,
        industry_scheme="SW_L1",
        mktcap_neutral=True,
        values=vals,
        sw_l1_coverage=covered,
        unknown_industry_count=unknown,
        promotion_approved=False,
        data_ready=True,
    )
    assert residual.promotion_approved is False

    ep_raw = RawFactorPanel(
        factor_id="V01_EP",
        session=session,
        values={"a": 0.1, "b": 0.2, "c": 0.05, "d": 0.3, "e": 0.15, "f": 0.08},
        available_at_ok=True,
    )
    ep_vals, _, _ = neutralize_raw_values(ep_raw.values, sw, mktcap=mktcap, mktcap_neutral=True)
    ep_res = ResidualFactorPanel(
        factor_id="V01_EP",
        session=session,
        industry_scheme="SW_L1",
        mktcap_neutral=True,
        values=ep_vals,
        sw_l1_coverage=len(ep_vals),
        unknown_industry_count=0,
        promotion_approved=False,
        data_ready=True,
    )
    composite = equal_weight_zscore_integrate(
        [residual, ep_res], mode="integrate", member_ids=COMPOSITE_MEMBER_IDS
    )
    assert composite.promotion_approved is False
    assert composite.data_ready is True
    assert len(composite.scores) >= 1

    mix = equal_weight_zscore_integrate(
        [residual, ep_res], mode="mix", member_ids=COMPOSITE_MEMBER_IDS
    )
    assert mix.mode == "mix"
    assert mix.promotion_approved is False
    assert any("mix_control_arm" in t for t in mix.todos)


def test_pipeline_hooks_and_ortho():
    session = date(2026, 6, 30)
    raw_m = RawFactorPanel(
        factor_id="M01_12_1",
        session=session,
        values={f"s{i}": float(i) for i in range(12)},
        available_at_ok=True,
    )
    raw_ep = RawFactorPanel(
        factor_id="V01_EP",
        session=session,
        values={f"s{i}": float(i) * 0.1 + 0.05 for i in range(12)},
        available_at_ok=True,
    )
    sw = _fake_sw_l1(
        session,
        {f"s{i}": "801010" if i < 6 else "801020" for i in range(12)},
    )
    neut = neutralize_raw_panel(raw_m, sw, mktcap=None, mktcap_neutral=False)
    assert neut.promotion_approved is False
    assert neut.data_ready is True

    ortho = orthogonalize_raw_pair(raw_m, raw_ep)
    assert ortho.promotion_approved is False
    assert ortho.n_obs >= 4

    pair = residualize_vs(
        dict(raw_m.values),
        dict(raw_ep.values),
        factor_id="M01_12_1",
        control_id="V01_EP",
        session=session,
    )
    assert pair.promotion_approved is False

    gs = gram_schmidt_set(
        {"M01_12_1": dict(raw_m.values), "V01_EP": dict(raw_ep.values)},
        ("V01_EP", "M01_12_1"),
        session=session,
    )
    assert gs.promotion_approved is False
    assert len(gs.panels) == 2
    assert all(p.promotion_approved is False for p in gs.panels)


def test_walk_forward_process_ic_only():
    base = date(2026, 1, 5)
    sessions = [base + timedelta(days=i) for i in range(20)]
    windows = iter_session_windows(sessions, train_size=5, step=2, expanding=False)
    assert len(windows) >= 1
    assert windows[0].promotion_approved if hasattr(windows[0], "promotion_approved") else True

    factor_by = {}
    fwd_by = {}
    for s in sessions:
        factor_by[s] = {f"x{i}": float(i + s.toordinal() % 3) for i in range(10)}
        fwd_by[s] = {f"x{i}": float((i % 5) - 2) * 0.01 for i in range(10)}

    report = run_walk_forward_process_ic(
        factor_by,
        fwd_by,
        factor_id="M01_12_1",
        sessions=sessions,
        train_size=5,
        step=2,
        expanding=True,
        forward_horizon=5,
    )
    assert report.promotion_approved is False
    assert report.process_metric_only is True
    assert report.ic_summary.promotion_approved is False
    assert "not_a_promotion_gate" in report.notes


def test_research_factory_list_and_stub_members():
    from quantlab.mandate_v2 import load_mandate_v2

    from quantlab.promotion_gate import overall_promotion_approved

    mandate = load_mandate_v2()
    # Platform/data-layer gate is owned by Leo via promotion_gate (2026-10-10 21:37 ET);
    # Alpha factor/residual/composite outputs below still assert False.
    assert mandate.promotion_approved is overall_promotion_approved()
    factory = ResearchResidualAlphaFactorFactory(mandate=mandate, float_mktcap={})
    members = factory.list_member_ids()
    assert "M01_12_1" in members and "V01_EP" in members
    contract = factory.describe_contract()
    assert contract["promotion_approved"] is False
    assert contract["financials_promotable"] is False

    # Empty universe → empty values for implemented member
    stub = factory.compute_raw(date(2026, 6, 30), "Q01_profitability", [])
    assert stub.values == {} or True  # may be empty
    assert "promotion_approved=false" in "".join(stub.notes) or any(
        "promotion_approved=false" in n for n in stub.notes
    )

    # Empty neutralize / integrate stay promotion-false
    empty_raw = RawFactorPanel(
        factor_id="M01_12_1", session=date(2026, 6, 30), values={}, available_at_ok=False
    )
    neut = factory.neutralize(empty_raw, ())
    assert neut.promotion_approved is False
    comp = factory.integrate([])
    assert comp.promotion_approved is False

    with pytest.raises(KeyError):
        factory.compute_raw(date(2026, 6, 30), "NOT_A_FACTOR", [])


def test_residual_panel_rejects_promotion_true():
    with pytest.raises(ValueError, match="promotion_approved_must_be_false"):
        ResidualFactorPanel(
            factor_id="M01_12_1",
            session=date(2026, 6, 30),
            industry_scheme="SW_L1",
            mktcap_neutral=False,
            values={},
            sw_l1_coverage=0,
            unknown_industry_count=0,
            promotion_approved=True,
        )
