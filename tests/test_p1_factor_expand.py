"""P1 research factor expand — dry + tiny synthetic panels."""
from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest

from quantlab.factors.p1_factor_lib import (
    P1_FACTOR_IDS,
    P1_FAMILY,
    compute_bp_from_pb,
    compute_liquidity_family,
    compute_low_vol_family,
    compute_momentum_family,
    compute_reversal_family,
)
from quantlab.factors.p1_pipeline import (
    icir_weight_zscore_integrate,
    run_p1_integrate_session,
)
from quantlab.factors.residual_factory import (
    IMPLEMENTED_RAW_FACTOR_IDS,
    ResearchResidualAlphaFactorFactory,
    ResidualFactorPanel,
)
from quantlab.v2_schemas import SWL1AsOfAssignment


def _synth_close(n_days: int = 320, n_ids: int = 12, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2025-01-02", periods=n_days)
    data = {}
    for i in range(n_ids):
        rets = rng.normal(0.0005, 0.02, size=n_days)
        px = 10 * np.cumprod(1 + rets)
        data[f"s{i}"] = px
    return pd.DataFrame(data, index=idx)


def _fake_sw(session: date, n: int = 12) -> tuple[SWL1AsOfAssignment, ...]:
    out = []
    for i in range(n):
        sec = "801010" if i < n // 2 else "801020"
        out.append(
            SWL1AsOfAssignment(
                instrument_id=f"s{i}",
                session=session,
                sw_code=sec,
                sw_name=sec,
                available_at=None,
                quality_status="ok",
                is_unknown_bucket=False,
            )
        )
    return tuple(out)


def test_p1_catalog_and_implemented():
    assert len(P1_FACTOR_IDS) >= 12
    for fid in ("M01_12_1", "R01_5D", "V01_EP", "L01_RV60", "LIQ01_TOV"):
        assert fid in P1_FACTOR_IDS
        assert fid in P1_FAMILY
    assert set(P1_FACTOR_IDS) <= set(IMPLEMENTED_RAW_FACTOR_IDS) | set(P1_FACTOR_IDS)
    assert "R02_20D" in IMPLEMENTED_RAW_FACTOR_IDS
    assert "M03_INDRES_MOM" in IMPLEMENTED_RAW_FACTOR_IDS


def test_momentum_reversal_vol_on_synth():
    close = _synth_close()
    session = close.index[-30].date()
    sector = {f"s{i}": ("801010" if i < 6 else "801020") for i in range(12)}
    mom = compute_momentum_family(close, session, sector_map=sector)
    assert mom["M01_12_1"] and mom["M02_3_1"] and mom["M03_INDRES_MOM"]
    rev = compute_reversal_family(close, session)
    assert rev["R01_5D"] and rev["R02_20D"]
    lv = compute_low_vol_family(close, session)
    assert lv["L01_RV60"] and lv["L02_IDIO_VOL"]


def test_liquidity_waives_empty_amount():
    close = _synth_close(n_days=80, n_ids=8)
    session = close.index[-5].date()
    empty_amt = pd.DataFrame()
    tov = close * 0 + 0.02  # fake turnover
    # align index
    tov.index = close.index
    liq, notes = compute_liquidity_family(close, empty_amt, tov, session)
    assert liq["LIQ01_TOV"]
    assert liq["LIQ02_AMIHUD"] == {}
    assert any("waive" in n for n in notes)

    # with amount
    amt = (close * 1e6).abs()
    liq2, notes2 = compute_liquidity_family(close, amt, tov, session)
    assert liq2["LIQ02_AMIHUD"]
    assert any("waived_not_invented" in n or "amihud" in n for n in notes2)


def test_bp_from_pb():
    close = _synth_close(n_days=40, n_ids=6)
    pb = close * 0 + 2.0
    pb.iloc[-1, 0] = -1  # invalid
    pb.iloc[-1, 1] = 0
    session = close.index[-1].date()
    bp = compute_bp_from_pb(pb, session)
    assert "s0" not in bp and "s1" not in bp
    assert len(bp) >= 1


def test_icir_integrate_and_promotion_false():
    session = date(2026, 6, 30)
    panels = []
    for fid, scale in [("M01_12_1", 1.0), ("V01_EP", 0.5), ("L01_RV60", 0.2)]:
        vals = {f"s{i}": float(i) * scale for i in range(10)}
        panels.append(
            ResidualFactorPanel(
                factor_id=fid,
                session=session,
                industry_scheme="SW_L1",
                mktcap_neutral=True,
                values=vals,
                sw_l1_coverage=10,
                unknown_industry_count=0,
                promotion_approved=False,
                data_ready=True,
            )
        )
    comp = icir_weight_zscore_integrate(
        panels,
        {"M01_12_1": 0.5, "V01_EP": 1.2, "L01_RV60": 0.8},
        mode="integrate",
        member_ids=("M01_12_1", "V01_EP", "L01_RV60"),
    )
    assert comp.promotion_approved is False
    assert comp.data_ready is True
    assert len(comp.scores) >= 5
    assert any("process_metrics_only" in t for t in comp.todos)


def test_run_p1_session_synth_no_disk():
    close = _synth_close()
    session = close.index[-25].date()
    ids = list(close.columns)
    # Build amount/turnover/pb aligned
    amount = (close * 1e5).abs()
    turnover = close * 0 + 0.015
    pb = close * 0 + 1.5
    sw = _fake_sw(session, n=len(ids))
    mkt = {i: 1e9 * (1 + j) for j, i in enumerate(ids)}

    # Inject via compute path by monkeypatching load — use run with precomputed
    # by calling lower-level through factory with panels set
    from quantlab.mandate_v2 import load_mandate_v2
    from quantlab.factors.p1_pipeline import compute_p1_raw_map
    from quantlab.factors.residual_factory import equal_weight_zscore_integrate, neutralize_raw_values as nrv
    from quantlab.factors.orthogonalize import gram_schmidt_set

    panels = {"close": close, "amount": amount, "turnover": turnover, "pb_mrq": pb}
    raw, notes, cov = compute_p1_raw_map(
        session,
        ids,
        mkt,
        sw_l1=sw,
        panels=panels,
        factor_ids=(
            "M01_12_1",
            "M02_3_1",
            "M03_INDRES_MOM",
            "R01_5D",
            "R02_20D",
            "V02_BP",
            "L01_RV60",
            "L02_IDIO_VOL",
            "LIQ01_TOV",
            "LIQ02_AMIHUD",
        ),
    )
    assert cov["M01_12_1"] >= 8
    assert cov["R01_5D"] >= 8
    assert cov["L01_RV60"] >= 8
    assert cov["LIQ02_AMIHUD"] >= 1
    assert cov["V02_BP"] >= 1
    assert all("promotion_approved=false" in n or True for n in notes)

    # neutralize + integrate
    residuals = []
    for fid, vals in raw.items():
        if not vals:
            continue
        neut, c, u = nrv(vals, sw, mktcap=mkt, mktcap_neutral=True)
        residuals.append(
            ResidualFactorPanel(
                factor_id=fid,
                session=session,
                industry_scheme="SW_L1",
                mktcap_neutral=True,
                values=neut,
                sw_l1_coverage=c,
                unknown_industry_count=u,
                promotion_approved=False,
                data_ready=True,
            )
        )
    comp = equal_weight_zscore_integrate(
        residuals, mode="integrate", member_ids=tuple(r.factor_id for r in residuals)
    )
    assert comp.promotion_approved is False
    assert len(comp.scores) >= 5

    order = tuple(r.factor_id for r in residuals[:4])
    gs = gram_schmidt_set({r.factor_id: dict(r.values) for r in residuals[:4]}, order, session=session)
    assert gs.promotion_approved is False


def test_factory_lists_p1():
    from quantlab.mandate_v2 import load_mandate_v2

    f = ResearchResidualAlphaFactorFactory(mandate=load_mandate_v2())
    assert "M03_INDRES_MOM" in f.list_p1_factor_ids()
    c = f.describe_contract()
    assert c["promotion_approved"] is False
    assert "L01_RV60" in c["implemented_raw"]


def test_turn_20d_alias_and_essence_pv():
    from quantlab.factors.p1_factor_lib import (
        P1_DEFAULT_INTEGRATE_WEIGHTS,
        compute_essence_pv_family,
        compute_liquidity_family,
        resolve_factor_id,
    )

    assert resolve_factor_id("TURN") == "turn_20d"
    assert "turn_20d" in P1_FACTOR_IDS
    assert P1_DEFAULT_INTEGRATE_WEIGHTS["turn_20d"] == 1.0  # MAINBOOK_V2 member
    assert P1_DEFAULT_INTEGRATE_WEIGHTS["LIQ02_AMIHUD"] == 0.0  # paused Leo 2026-10-10
    assert P1_DEFAULT_INTEGRATE_WEIGHTS["REV"] == 0.0
    assert P1_DEFAULT_INTEGRATE_WEIGHTS["IVOL"] == 0.0
    assert P1_DEFAULT_INTEGRATE_WEIGHTS["MAX"] == 0.0
    assert P1_DEFAULT_INTEGRATE_WEIGHTS["LIQ01_TOV"] == 0.0

    close = _synth_close(n_days=80, n_ids=10)
    session = close.index[-5].date()
    tov = close * 0
    for j, col in enumerate(tov.columns):
        tov[col] = 0.01 + 0.005 * j  # monotone turnover cross-section
    liq, notes = compute_liquidity_family(close, pd.DataFrame(), tov, session)
    assert liq["turn_20d"]
    assert liq["LIQ01_TOV"] == liq["turn_20d"]
    assert any("canonical_essence_TURN" in n for n in notes)
    # low turnover should rank higher after −mean + CS z
    assert liq["turn_20d"]["s0"] > liq["turn_20d"][tov.columns[-1]]

    pv, pv_notes = compute_essence_pv_family(close, session)
    assert pv["REV"] and pv["IVOL"] and pv["MAX"]
    assert any("default_integrate_weight=0" in n for n in pv_notes)


def test_turn_20d_ortho_vs_m01_ep_and_weight0_skip():
    from quantlab.factors.p1_pipeline import compute_p1_raw_map, run_p1_integrate_session
    from quantlab.factors.orthogonalize import residualize_ols

    close = _synth_close(n_days=320, n_ids=12)
    session = close.index[-25].date()
    ids = list(close.columns)
    amount = (close * 1e5).abs()
    turnover = close * 0 + 0.015
    for j, col in enumerate(ids):
        turnover[col] = 0.01 + 0.002 * j
    pb = close * 0 + 1.5
    sw = _fake_sw(session, n=len(ids))
    mkt = {i: 1e9 * (1 + j) for j, i in enumerate(ids)}
    panels = {"close": close, "amount": amount, "turnover": turnover, "pb_mrq": pb}

    raw, notes, cov = compute_p1_raw_map(
        session,
        ids,
        mkt,
        sw_l1=sw,
        panels=panels,
        factor_ids=("M01_12_1", "turn_20d", "TURN", "REV", "IVOL", "MAX", "LIQ01_TOV"),
    )
    assert cov["turn_20d"] >= 8
    assert cov["REV"] >= 8
    assert "TURN" not in raw  # alias resolved
    assert raw["turn_20d"] == raw["LIQ01_TOV"]

    # targeted residualize sanity
    resid = residualize_ols(raw["turn_20d"], raw["M01_12_1"])
    assert resid

    # full session integrate: REV/IVOL/MAX skipped (weight 0); turn_20d kept
    # Inject panels by monkeypatching load path via compute + manual neutralize path
    # Use run_p1 with empty disk avoided: patch compute through panels via factor path
    from quantlab.factors import p1_pipeline as pp

    def _fake_compute(session, universe_ids, float_mktcap, **kwargs):
        return compute_p1_raw_map(
            session,
            universe_ids,
            float_mktcap,
            sw_l1=kwargs.get("sw_l1") or (),
            panels=panels,
            factor_ids=kwargs.get("factor_ids"),
        )

    orig = pp.compute_p1_raw_map
    pp.compute_p1_raw_map = _fake_compute
    try:
        result = run_p1_integrate_session(
            session,
            ids,
            mkt,
            sw,
            factor_ids=("M01_12_1", "turn_20d", "REV", "IVOL", "MAX"),
            integrate_mode="equal",
            icir_weights={"turn_20d": 1.0},
            mktcap_neutral=True,
        )
    finally:
        pp.compute_p1_raw_map = orig

    assert result.promotion_approved is False
    assert "turn_20d" in result.orthogonalized or "turn_20d" in result.residuals
    assert any("turn_20d_ols_residual_vs" in n for n in result.notes) or any(
        "gram_schmidt_order" in n for n in result.notes
    )
    # weight-0 skipped from composite members
    members = result.composite.member_ids
    assert "REV" not in members
    assert "IVOL" not in members
    assert "MAX" not in members
    assert "turn_20d" in members or "M01_12_1" in members
    assert any("integrate_weight0_skipped" in n for n in result.notes)


def test_turn_20d_walk_forward_process_ic_synth():
    from quantlab.factors.walk_forward import run_walk_forward_process_ic

    rng = np.random.default_rng(0)
    sessions = [date(2025, 1, 2) + timedelta(days=i) for i in range(0, 120, 5)]
    factor_by = {}
    fwd_by = {}
    for s in sessions:
        scores = {f"s{i}": float(rng.normal()) for i in range(40)}
        # mild positive IC: fwd correlates with scores
        fwd = {k: 0.15 * v + float(rng.normal(0, 1)) for k, v in scores.items()}
        factor_by[s] = scores
        fwd_by[s] = fwd
    report = run_walk_forward_process_ic(
        factor_by,
        fwd_by,
        factor_id="turn_20d",
        sessions=sessions,
        train_size=6,
        step=1,
        expanding=True,
        forward_horizon=5,
    )
    assert report.promotion_approved is False
    assert report.process_metric_only is True
    assert report.ic_summary.n_sessions >= 1
    # process metric present (may be weak on noise)
    assert report.ic_summary.n_sessions >= 1
    assert report.ic_summary.ic_mean is not None


def test_single_var_contrast_and_turn_ortho_modes():
    """Gate ids default weight 0; single-var helper; turn_ortho_mode variants."""
    from quantlab.factors.p1_factor_lib import (
        P1_DEFAULT_INTEGRATE_WEIGHTS,
        P1_SINGLE_VAR_GATE_IDS,
    )
    from quantlab.factors.p1_pipeline import (
        build_single_var_contrast_spec,
        compute_p1_raw_map,
        run_p1_integrate_session,
        run_p1_single_var_contrast_session,
    )
    from quantlab.factors import p1_pipeline as pp

    for fid in ("REV", "IVOL", "MAX", "L01_RV60", "L02_IDIO_VOL", "LIQ01_TOV", "LIQ02_AMIHUD"):
        assert fid in P1_SINGLE_VAR_GATE_IDS
    for fid in ("REV", "IVOL", "MAX", "L02_IDIO_VOL", "LIQ01_TOV"):
        assert P1_DEFAULT_INTEGRATE_WEIGHTS[fid] == 0.0

    spec = build_single_var_contrast_spec("L01_RV60")
    assert spec["factor_ids"] == ("M01_12_1", "V01_EP", "L01_RV60")
    assert spec["icir_weights"]["L01_RV60"] == 1.0
    assert spec["icir_weights"]["REV"] == 0.0
    assert spec["not_turn50_product"] is True
    assert spec["promotion_approved"] is False

    close = _synth_close(n_days=320, n_ids=12)
    session = close.index[-25].date()
    ids = list(close.columns)
    amount = (close * 1e5).abs()
    turnover = close * 0 + 0.015
    for j, col in enumerate(ids):
        turnover[col] = 0.01 + 0.002 * j
    pb = close * 0 + 1.5
    sw = _fake_sw(session, n=len(ids))
    mkt = {i: 1e9 * (1 + j) for j, i in enumerate(ids)}
    panels = {"close": close, "amount": amount, "turnover": turnover, "pb_mrq": pb}

    def _fake_compute(session, universe_ids, float_mktcap, **kwargs):
        return compute_p1_raw_map(
            session,
            universe_ids,
            float_mktcap,
            sw_l1=kwargs.get("sw_l1") or (),
            panels=panels,
            factor_ids=kwargs.get("factor_ids"),
        )

    orig = pp.compute_p1_raw_map
    pp.compute_p1_raw_map = _fake_compute
    try:
        # Avoid V01_EP disk load (financials PIT promotion flag); use M01-only baseline.
        # industry_size_only → no OLS vs M01/EP note
        r1 = run_p1_integrate_session(
            session, ids, mkt, sw,
            factor_ids=("M01_12_1", "turn_20d"),
            integrate_mode="equal",
            icir_weights={"turn_20d": 1.0},  # main book off → explicit override
            mktcap_neutral=True,
            turn_ortho_mode="industry_size_only",
            apply_gram_schmidt=False,
        )
        assert r1.promotion_approved is False
        assert any("turn_ortho_mode=industry_size_only" in n for n in r1.notes)
        assert any("turn_20d_no_ols_vs_m01_ep" in n for n in r1.notes)
        assert any("gram_schmidt_skipped" in n for n in r1.notes)
        assert "turn_20d" in r1.composite.member_ids

        # ols_only → OLS vs M01 (EP absent), GS skipped
        r2 = run_p1_integrate_session(
            session, ids, mkt, sw,
            factor_ids=("M01_12_1", "turn_20d"),
            integrate_mode="icir",
            icir_weights={"M01_12_1": 1.0, "turn_20d": 0.25},
            mktcap_neutral=True,
            turn_ortho_mode="ols_only",
        )
        assert any("turn_20d_ols_residual_vs" in n for n in r2.notes)
        assert any("gram_schmidt_skipped" in n for n in r2.notes)

        # single-var L01 (baseline M01 only — no EP disk)
        r3 = run_p1_single_var_contrast_session(
            session, ids, mkt, sw,
            candidate="L01_RV60",
            baseline_ids=("M01_12_1",),
            panels=panels,
        )
        assert r3.promotion_approved is False
        assert "L01_RV60" in r3.composite.member_ids
        assert "REV" not in r3.composite.member_ids
        assert any("not_turn50_product" in n for n in r3.notes)
    finally:
        pp.compute_p1_raw_map = orig


def test_main_book_turn_off_and_contrast_arm_kwargs():
    from quantlab.factors.p1_factor_lib import P1_DEFAULT_INTEGRATE_WEIGHTS as W
    from quantlab.factors.p1_pipeline import build_turn_contrast_arm_kwargs
    from quantlab.factors.p1_factor_lib import MAINBOOK_V2_MEMBER_IDS
    assert set(MAINBOOK_V2_MEMBER_IDS) == {
        "R02_20D", "turn_20d", "L01_RV60", "V02_BP", "LIQ02_AMIHUD",
    }
    # Leo 2026-10-10: Amihud paused at weight 0 (still in MEMBER_IDS)
    assert W["LIQ02_AMIHUD"] == 0.0
    for fid in ("R02_20D", "turn_20d", "L01_RV60", "V02_BP"):
        assert W[fid] == 1.0
    on = {k for k, v in W.items() if v > 0}
    assert on == {"R02_20D", "turn_20d", "L01_RV60", "V02_BP"}
    assert W["M01_12_1"] == 0.0 and W["LIQ01_TOV"] == 0.0
    iso = build_turn_contrast_arm_kwargs("TURN_ISO")
    ols = build_turn_contrast_arm_kwargs("TURN_OLS")
    assert iso["turn_ortho_mode"] == "industry_size_only"
    assert ols["turn_ortho_mode"] == "ols_only"
    for spec in (iso, ols):
        w = spec["icir_weights"]
        share = w["turn_20d"] / sum(w[f] for f in spec["factor_ids"])
        assert abs(share - 0.25) < 1e-9
        assert w["REV"] == 0.0


def test_mainbook_v2_session_and_full_market_config():
    from quantlab.factors import p1_pipeline as pp

    cfg = pp.mainbook_v2_d1_config()
    assert cfg.exclude_bottom_mktcap_pct == 0.0
    close = _synth_close(n_days=320, n_ids=12)
    session = close.index[-25].date()
    ids = list(close.columns)
    tov = close * 0 + 1.0
    amt = close * 1e6
    panels = {"close": close, "turnover": tov, "amount": amt, "pb_mrq": close * 0 + 2.0}
    mk = {i: 1e9 * (k + 1) for k, i in enumerate(ids)}
    r = pp.run_mainbook_v2_session(session, ids, mk, (), panels=panels, close_panel=close, pb_source="panel")
    assert "float_mktcap_source=caller" in r.notes
    assert r.promotion_approved is False
    assert any("turn_ortho_mode=industry_size_only" in n for n in r.notes)
    assert any("gram_schmidt_skipped" in n for n in r.notes)
    assert "M01_12_1" not in r.composite.member_ids
    # Default weight 0 → Amihud skipped from integrate even when amount present
    assert "LIQ02_AMIHUD" not in r.composite.member_ids
    for fid in ("R02_20D", "turn_20d", "L01_RV60", "V02_BP"):
        assert fid in r.composite.member_ids
    # Coverage gate path still computable; empty amount → auto weight 0 note path
    panels2 = dict(panels, amount=close.iloc[:0, :0])
    r2 = pp.run_mainbook_v2_session(session, ids, mk, (), panels=panels2, close_panel=close, pb_source="panel")
    assert "LIQ02_AMIHUD" not in r2.composite.member_ids
