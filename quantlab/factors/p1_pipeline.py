"""P1 research pipeline: raw → neutralize → ortho → integrate → process IC.

``promotion_approved=false`` everywhere. For Strategy: call
:func:`run_p1_integrate_session` and consume ``composite.scores``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np
import pandas as pd

from quantlab.factors.engine import winsorize_zscore
from quantlab.factors.orthogonalize import gram_schmidt_set, residualize_ols
from quantlab.factors.p1_factor_lib import (
    P1_DEFAULT_INTEGRATE_WEIGHTS,
    P1_FACTOR_ALIASES,
    P1_FACTOR_IDS,
    P1_FAMILY,
    P1_SINGLE_VAR_GATE_IDS,
    compute_bp_from_pb,
    compute_essence_pv_family,
    compute_liquidity_family,
    compute_low_vol_family,
    compute_momentum_family,
    compute_quality_from_financials,
    compute_reversal_family,
    load_ohlcv_panels,
    resolve_factor_id,
)
from quantlab.factors.residual_factory import (
    COMPOSITE_MEMBER_IDS,
    CompositeScorePanel,
    RawFactorPanel,
    ResidualFactorPanel,
    equal_weight_zscore_integrate,
    neutralize_raw_values,
    sw_l1_to_sector_map,
)
from quantlab.factors.v2_min_pipeline import (
    ProcessICSummary,
    compute_ep_cross_section,
)
from quantlab.v2_schemas import SWL1AsOfAssignment


@dataclass(frozen=True)
class P1SessionResult:
    session: date
    universe_ids: tuple[str, ...]
    raw: Mapping[str, Mapping[str, float]]
    residuals: Mapping[str, Mapping[str, float]]
    orthogonalized: Mapping[str, Mapping[str, float]]
    composite: CompositeScorePanel
    ic_summaries: tuple[ProcessICSummary, ...] = ()
    coverage: Mapping[str, int] = field(default_factory=dict)
    stubs: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    promotion_approved: bool = False

    def __post_init__(self) -> None:
        if self.promotion_approved:
            raise ValueError("p1_session_promotion_approved_must_be_false")
        if self.composite.promotion_approved:
            raise ValueError("p1_composite_promotion_must_be_false")


# Default Gram-Schmidt order: M01 + EP before turn_20d (ESSENCE A3)
P1_ORTHO_PRIORITY: tuple[str, ...] = (
    "M01_12_1",
    "V01_EP",
    "turn_20d",
    "M02_3_1",
    "M03_INDRES_MOM",
    "R01_5D",
    "R02_20D",
    "V02_BP",
    "Q01_profitability",
    "Q01_ROE_STAB",
    "Q03_safety",
    "Q_ACCRUAL_PROXY",
    "L01_RV60",
    "L02_IDIO_VOL",
    "LIQ02_AMIHUD",
    "LIQ01_TOV",  # alias; usually weight 0
    "REV",
    "IVOL",
    "MAX",
)

# turn_20d post-neutral handling (Full D1 failure → prefer ols_only / industry_size_only)
# ols_then_gs: legacy A3 (OLS vs M01+EP then Gram-Schmidt) — reproduces failed paper arm
# ols_only: OLS vs M01+EP, skip GS
# industry_size_only: no factor-vs-factor residual; optional GS still controlled by apply_gram_schmidt
# none: no special TURN residualize (same as other factors)
TURN_ORTHO_MODES: tuple[str, ...] = (
    "ols_then_gs",
    "ols_only",
    "industry_size_only",
    "none",
)

AMIHUD_MIN_COVERAGE: float = 0.6

DEFAULT_P1_SESSION_FACTOR_IDS: tuple[str, ...] = (
    "M01_12_1",
    "M02_3_1",
    "M03_INDRES_MOM",
    "R01_5D",
    "R02_20D",
    "V01_EP",
    "V02_BP",
    "Q01_profitability",
    "Q01_ROE_STAB",
    "Q03_safety",
    "Q_ACCRUAL_PROXY",
    "L01_RV60",
    "L02_IDIO_VOL",
    "turn_20d",
    "LIQ01_TOV",
    "LIQ02_AMIHUD",
    "REV",
    "IVOL",
    "MAX",
)


def _normalize_wanted(factor_ids: Sequence[str] | None) -> list[str]:
    if factor_ids is None:
        return list(P1_FACTOR_IDS)
    out: list[str] = []
    seen: set[str] = set()
    for fid in factor_ids:
        can = resolve_factor_id(fid)
        if can not in seen:
            out.append(can)
            seen.add(can)
    return out


def _default_ortho_order(available: Sequence[str]) -> list[str]:
    avail = set(available)
    ordered = [f for f in P1_ORTHO_PRIORITY if f in avail]
    for f in available:
        if f not in ordered:
            ordered.append(f)
    return ordered


def _filter_integrate_panels(
    panels: Sequence[ResidualFactorPanel],
    *,
    integrate_mode: str,
    icir_weights: Mapping[str, float] | None,
) -> list[ResidualFactorPanel]:
    """Drop default-weight-0 members (REV/IVOL/MAX/LIQ01 alias) unless overridden."""
    overrides = {resolve_factor_id(k): float(v) for k, v in (icir_weights or {}).items()}
    kept: list[ResidualFactorPanel] = []
    for p in panels:
        if not p.values:
            continue
        fid = p.factor_id
        if fid in overrides:
            w = overrides[fid]
        else:
            w = float(P1_DEFAULT_INTEGRATE_WEIGHTS.get(fid, 1.0))
        if w <= 0:
            continue
        kept.append(p)
    return kept


def icir_weight_zscore_integrate(
    residuals: Sequence[ResidualFactorPanel],
    icir_weights: Mapping[str, float],
    *,
    mode: str,
    member_ids: Sequence[str],
) -> CompositeScorePanel:
    """ICIR-weighted average of per-member CS z-scores (process weights only).

    Non-positive / missing ICIR → equal fallback weight among present members.
    """
    if not residuals:
        return CompositeScorePanel(
            session=date.min,
            mode=mode,
            member_ids=tuple(member_ids),
            scores={},
            promotion_approved=False,
            data_ready=False,
            todos=("no_residuals", "promotion_approved=false"),
        )
    session = residuals[0].session
    z_panels: list[pd.Series] = []
    weights: list[float] = []
    for r in residuals:
        if not r.values:
            continue
        s = pd.Series(dict(r.values), dtype=float)
        z = winsorize_zscore(s).rename(r.factor_id)
        z_panels.append(z)
        w = float(icir_weights.get(r.factor_id, float("nan")))
        if not np.isfinite(w) or w <= 0:
            w = 1.0
        weights.append(w)
    notes = [
        "promotion_approved=false",
        "icir_weight_zscore_integrate",
        "icir_weights_are_process_metrics_only",
    ]
    if mode == "mix":
        notes.append("mix_control_arm_only")
    if not z_panels:
        return CompositeScorePanel(
            session=session,
            mode=mode,
            member_ids=tuple(member_ids),
            scores={},
            promotion_approved=False,
            data_ready=False,
            todos=("no_residual_values", "promotion_approved=false"),
        )
    stacked = pd.concat(z_panels, axis=1)
    w = np.asarray(weights, dtype=float)
    w = w / w.sum()
    # weighted mean with NaN skip: mask
    arr = stacked.to_numpy(dtype=float)
    mask = np.isfinite(arr)
    num = np.nansum(np.where(mask, arr * w.reshape(1, -1), 0.0), axis=1)
    den = np.nansum(np.where(mask, w.reshape(1, -1), 0.0), axis=1)
    den = np.where(den > 0, den, np.nan)
    scores_s = pd.Series(num / den, index=stacked.index).dropna()
    scores = {str(k): float(v) for k, v in scores_s.items() if np.isfinite(v)}
    return CompositeScorePanel(
        session=session,
        mode=mode,
        member_ids=tuple(member_ids),
        scores=scores,
        promotion_approved=False,
        data_ready=True,
        todos=tuple(notes),
    )


def compute_p1_raw_map(
    session: date,
    universe_ids: Sequence[str],
    float_mktcap: Mapping[str, float],
    *,
    sw_l1: Sequence[SWL1AsOfAssignment] = (),
    d0_root: Path | None = None,
    asof_extend_dir: Path | None = None,
    close_panel: pd.DataFrame | None = None,
    panels: Mapping[str, pd.DataFrame] | None = None,
    fin_view=None,
    ep_research_view=None,
    factor_ids: Sequence[str] | None = None,
) -> tuple[dict[str, dict[str, float]], tuple[str, ...], dict[str, int]]:
    """Compute raw P1 factor cross-sections (CS z where applicable)."""
    from quantlab.data.v2_readers import default_v2_roots

    roots = default_v2_roots()
    d0 = Path(d0_root) if d0_root is not None else roots.d0_root
    ext = Path(asof_extend_dir) if asof_extend_dir is not None else roots.asof_extend_dir
    ids = [str(x) for x in universe_ids]
    use_list = _normalize_wanted(factor_ids)
    wanted = set(use_list)
    notes: list[str] = ["promotion_approved=false", "research_only", "p1_factor_lib"]
    raw: dict[str, dict[str, float]] = {fid: {} for fid in P1_FACTOR_IDS}
    coverage: dict[str, int] = {}
    if not ids:
        notes.append("empty_universe")
        return raw, tuple(notes), {fid: 0 for fid in wanted}

    # panels
    if panels is None:
        if close_panel is not None and not close_panel.empty:
            panels = {"close": close_panel, "amount": pd.DataFrame(), "turnover": pd.DataFrame(), "pb_mrq": pd.DataFrame()}
            panel_notes: tuple[str, ...] = ("close_only_injected",)
        else:
            panels, panel_notes = load_ohlcv_panels(
                ids, d0_root=d0, asof_extend_dir=ext, end_session=session
            )
        notes.extend(panel_notes)
    close = panels.get("close", pd.DataFrame())
    amount = panels.get("amount", pd.DataFrame())
    turnover = panels.get("turnover", pd.DataFrame())
    pb = panels.get("pb_mrq", pd.DataFrame())

    sector_map = sw_l1_to_sector_map(sw_l1) if sw_l1 else {}

    if wanted & {"M01_12_1", "M02_3_1", "M03_INDRES_MOM"}:
        mom = compute_momentum_family(close, session, sector_map=sector_map or None)
        for k, v in mom.items():
            if k in wanted:
                raw[k] = v
                coverage[k] = len(v)
        if "M03_INDRES_MOM" in wanted and not sector_map:
            notes.append("M03_INDRES_MOM_needs_sw_l1_sector_map")

    if wanted & {"R01_5D", "R02_20D"}:
        rev = compute_reversal_family(close, session)
        for k, v in rev.items():
            if k in wanted:
                raw[k] = v
                coverage[k] = len(v)

    if "V01_EP" in wanted:
        ep, meta = compute_ep_cross_section(
            session,
            ids,
            float_mktcap,
            fin_view=fin_view,
            ep_research_view=ep_research_view,
        )
        if meta.get("financials_promotable"):
            raise RuntimeError("financials_must_remain_non_promotable")
        if ep:
            ep = {str(k): float(v) for k, v in winsorize_zscore(pd.Series(ep, dtype=float)).dropna().items()}
        raw["V01_EP"] = ep
        coverage["V01_EP"] = len(ep)
        notes.append(f"ep_metric={meta.get('metric_used')}")
        notes.append("financials_pit_not_promotable")

    if "V02_BP" in wanted:
        bp = compute_bp_from_pb(pb, session)
        raw["V02_BP"] = bp
        coverage["V02_BP"] = len(bp)
        if not bp:
            notes.append("V02_BP_empty_pb_mrq_missing_or_invalid")
        else:
            notes.append("V02_BP_from_pb_mrq_inverse_research_proxy")

    if wanted & {"Q01_profitability", "Q01_ROE_STAB", "Q03_safety", "Q_ACCRUAL_PROXY"}:
        q = compute_quality_from_financials(session, ids, fin_view=fin_view)
        for k, v in q.items():
            if k in wanted:
                raw[k] = v
                coverage[k] = len(v)
        notes.append("quality_from_financials_available_at_research")

    if wanted & {"L01_RV60", "L02_IDIO_VOL"}:
        lv = compute_low_vol_family(close, session)
        for k, v in lv.items():
            if k in wanted:
                raw[k] = v
                coverage[k] = len(v)

    if wanted & {"turn_20d", "LIQ01_TOV", "LIQ02_AMIHUD"}:
        liq, liq_notes = compute_liquidity_family(close, amount, turnover, session)
        for k, v in liq.items():
            raw[k] = v
            coverage[k] = len(v)
        # keep alias relation even if only one id was requested
        if raw.get("turn_20d") and not raw.get("LIQ01_TOV"):
            raw["LIQ01_TOV"] = dict(raw["turn_20d"])
            coverage["LIQ01_TOV"] = len(raw["LIQ01_TOV"])
        if raw.get("LIQ01_TOV") and not raw.get("turn_20d"):
            raw["turn_20d"] = dict(raw["LIQ01_TOV"])
            coverage["turn_20d"] = len(raw["turn_20d"])
        notes.extend(liq_notes)

    if wanted & {"REV", "IVOL", "MAX"}:
        pv, pv_notes = compute_essence_pv_family(close, session)
        for k, v in pv.items():
            if k in wanted:
                raw[k] = v
                coverage[k] = len(v)
        notes.extend(pv_notes)

    stubs = tuple(fid for fid in wanted if coverage.get(fid, 0) == 0)
    return raw, tuple(notes), coverage


def run_p1_integrate_session(
    session: date,
    universe_ids: Sequence[str],
    float_mktcap: Mapping[str, float],
    sw_l1: Sequence[SWL1AsOfAssignment],
    *,
    d0_root: Path | None = None,
    asof_extend_dir: Path | None = None,
    factor_ids: Sequence[str] | None = None,
    integrate_mode: str = "equal",  # equal | icir
    icir_weights: Mapping[str, float] | None = None,
    ortho_order: Sequence[str] | None = None,
    mktcap_neutral: bool = True,
    ic_lookback_sessions: int = 0,
    forward_horizon: int = 5,
    panels: Mapping[str, object] | None = None,
    close_panel: object | None = None,
    ep_research_view=None,
    fin_view=None,
    turn_ortho_mode: str = "ols_then_gs",
    apply_gram_schmidt: bool = True,
    amihud_min_coverage: float = AMIHUD_MIN_COVERAGE,
) -> P1SessionResult:
    """Full P1 path for one session → composite scores for Strategy.

    Default integrate members = intersection of requested ids with non-empty
    residuals after industry(+mktcap) neutralize + optional Gram-Schmidt.

    ``turn_ortho_mode`` (research-only; see TURN_FAILURE_DIAGNOSIS.md):
      ols_then_gs | ols_only | industry_size_only | none
    ``apply_gram_schmidt``: set False to skip set-wise GS (e.g. after OLS-only).

    Optional ``panels`` / ``close_panel`` avoid per-call OHLCV reload (Strategy
    paper TURN compare).
    """
    ids = [str(x) for x in universe_ids]
    use_ids = (
        _normalize_wanted(factor_ids)
        if factor_ids is not None
        else list(DEFAULT_P1_SESSION_FACTOR_IDS)
    )
    raw, notes, coverage = compute_p1_raw_map(
        session,
        ids,
        float_mktcap,
        sw_l1=sw_l1,
        d0_root=d0_root,
        asof_extend_dir=asof_extend_dir,
        factor_ids=use_ids,
        panels=panels,  # type: ignore[arg-type]
        close_panel=close_panel,  # type: ignore[arg-type]
        ep_research_view=ep_research_view,
        fin_view=fin_view,
    )
    notes_l = list(notes)

    residual_panels: list[ResidualFactorPanel] = []
    residual_maps: dict[str, dict[str, float]] = {}
    for fid in use_ids:
        values = raw.get(fid) or {}
        neut, covered, unknown = neutralize_raw_values(
            values,
            sw_l1,
            mktcap=float_mktcap if mktcap_neutral else None,
            mktcap_neutral=mktcap_neutral,
        )
        residual_maps[fid] = neut
        residual_panels.append(
            ResidualFactorPanel(
                factor_id=fid,
                session=session,
                industry_scheme="SW_L1",
                mktcap_neutral=mktcap_neutral,
                values=neut,
                sw_l1_coverage=covered,
                unknown_industry_count=unknown,
                promotion_approved=False,
                data_ready=bool(neut),
                todos=("promotion_approved=false", "p1_pipeline"),
            )
        )

    mode = str(turn_ortho_mode or "ols_then_gs").strip().lower()
    if mode not in TURN_ORTHO_MODES:
        raise ValueError(f"turn_ortho_mode_invalid:{turn_ortho_mode}")
    notes_l.append(f"turn_ortho_mode={mode}")

    # Optional: residualize turn_20d vs M01 + EP (A3); skip for industry_size_only / none
    do_turn_ols = mode in ("ols_then_gs", "ols_only") and bool(
        residual_maps.get("turn_20d")
    )
    if do_turn_ols:
        controls = []
        cids = []
        if residual_maps.get("M01_12_1"):
            controls.append(residual_maps["M01_12_1"])
            cids.append("M01_12_1")
        if residual_maps.get("V01_EP"):
            controls.append(residual_maps["V01_EP"])
            cids.append("V01_EP")
        if controls:
            residual_maps["turn_20d"] = residualize_ols(
                residual_maps["turn_20d"], *controls
            )
            notes_l.append(
                "turn_20d_ols_residual_vs=" + ",".join(cids)
            )
            for i, p in enumerate(residual_panels):
                if p.factor_id == "turn_20d":
                    residual_panels[i] = ResidualFactorPanel(
                        factor_id="turn_20d",
                        session=session,
                        industry_scheme="SW_L1",
                        mktcap_neutral=mktcap_neutral,
                        values=residual_maps["turn_20d"],
                        sw_l1_coverage=len(residual_maps["turn_20d"]),
                        unknown_industry_count=0,
                        promotion_approved=False,
                        data_ready=bool(residual_maps["turn_20d"]),
                        todos=(
                            "promotion_approved=false",
                            "turn_20d_ortho_vs_m01_ep",
                        ),
                    )
                    break
    elif residual_maps.get("turn_20d") and mode == "industry_size_only":
        notes_l.append("turn_20d_no_ols_vs_m01_ep_industry_size_only")

    # Orthogonalize non-empty residuals; default order keeps M01/EP before turn_20d
    # ols_only / apply_gram_schmidt=False → skip GS (fixes double-residual)
    do_gs = bool(apply_gram_schmidt) and mode != "ols_only"
    non_empty = [fid for fid in use_ids if residual_maps.get(fid)]
    order = (
        list(ortho_order)
        if ortho_order is not None
        else _default_ortho_order(non_empty)
    )
    order = [resolve_factor_id(f) for f in order]
    order = [f for f in order if f in residual_maps and residual_maps[f]]
    seen_o: set[str] = set()
    order = [f for f in order if not (f in seen_o or seen_o.add(f))]
    ortho_maps: dict[str, dict[str, float]] = dict(residual_maps)
    if do_gs and len(order) >= 2:
        gs = gram_schmidt_set(
            {f: residual_maps[f] for f in order},
            tuple(order),
            session=session,
        )
        assert gs.promotion_approved is False
        for p in gs.panels:
            ortho_maps[p.factor_id] = dict(p.values)
        notes_l.append(f"gram_schmidt_order={','.join(order)}")
        residual_panels = []
        for fid in use_ids:
            vals = ortho_maps.get(fid) or {}
            residual_panels.append(
                ResidualFactorPanel(
                    factor_id=fid,
                    session=session,
                    industry_scheme="SW_L1",
                    mktcap_neutral=mktcap_neutral,
                    values=vals,
                    sw_l1_coverage=len(vals),
                    unknown_industry_count=0,
                    promotion_approved=False,
                    data_ready=bool(vals),
                    todos=("promotion_approved=false", "post_ortho"),
                )
            )
    else:
        notes_l.append(
            "gram_schmidt_skipped"
            + ("" if do_gs else f"_mode={mode}_or_flag")
        )

    present_all = [p for p in residual_panels if p.values]
    present = _filter_integrate_panels(
        present_all, integrate_mode=integrate_mode, icir_weights=icir_weights
    )
    # MAINBOOK_V2: Amihud auto-falls to weight 0 this session when amount
    # coverage over the universe is below gate (no invented liquidity).
    # denominator = names with a computable price factor (listed/priced),
    # not raw universe ids (which may include not-yet-listed names)
    n_univ = max(
        [len(residual_maps.get(f) or {}) for f in ("R02_20D", "turn_20d", "L01_RV60")]
        + [1]
    )
    amihud_cov = len(residual_maps.get("LIQ02_AMIHUD") or {}) / n_univ
    if "LIQ02_AMIHUD" in use_ids:
        notes_l.append(f"amihud_coverage={amihud_cov:.3f}")
        if amihud_cov < float(amihud_min_coverage) and any(
            p.factor_id == "LIQ02_AMIHUD" for p in present
        ):
            present = [p for p in present if p.factor_id != "LIQ02_AMIHUD"]
            notes_l.append(
                f"LIQ02_AMIHUD_auto_weight0_coverage<{amihud_min_coverage}"
            )
    if present_all and not present:
        # Eng 2026-10-11: never return a silently empty composite when every
        # requested factor was dropped by default weight-0 (S1_w n_names=0 bug).
        raise RuntimeError(
            "p1_all_requested_factors_default_weight0:"
            + ",".join(p.factor_id for p in present_all)
            + " (pass icir_weights={fid: 1.0} to override)"
        )
    skipped = tuple(
        p.factor_id
        for p in present_all
        if p.factor_id not in {x.factor_id for x in present}
    )
    if skipped:
        notes_l.append("integrate_weight0_skipped=" + ",".join(skipped))
    member_ids = tuple(p.factor_id for p in present) or tuple(COMPOSITE_MEMBER_IDS)
    if integrate_mode == "icir":
        # merge defaults then overrides (zeros already filtered unless override > 0)
        weights = dict(P1_DEFAULT_INTEGRATE_WEIGHTS)
        if icir_weights:
            for k, v in icir_weights.items():
                weights[resolve_factor_id(k)] = float(v)
        composite = icir_weight_zscore_integrate(
            present, weights, mode="integrate", member_ids=member_ids
        )
    else:
        composite = equal_weight_zscore_integrate(
            present, mode="integrate", member_ids=member_ids
        )
    notes_l.append("mainbook_v2_defaults=R02_20D,turn_20d,L01_RV60,V02_BP,LIQ02_AMIHUD_w0")
    notes_l.append("essence_A4_REV_IVOL_MAX_default_weight0")

    stubs = tuple(fid for fid in use_ids if coverage.get(fid, 0) == 0)
    ic_summaries: tuple[ProcessICSummary, ...] = ()
    # optional short process-IC on raw (only if lookback requested)
    if ic_lookback_sessions > 0:
        # lightweight: skip heavy reload; caller can use walk_forward separately
        notes_l.append(
            f"ic_lookback_requested={ic_lookback_sessions}_use_walk_forward_module_for_full_WF"
        )

    return P1SessionResult(
        session=session,
        universe_ids=tuple(ids),
        raw={k: dict(v) for k, v in raw.items() if k in use_ids},
        residuals=residual_maps,
        orthogonalized=ortho_maps,
        composite=composite,
        ic_summaries=ic_summaries,
        coverage=coverage,
        stubs=stubs,
        notes=tuple(notes_l),
        promotion_approved=False,
    )



def build_single_var_contrast_spec(
    candidate: str,
    *,
    baseline_ids: Sequence[str] = ("M01_12_1", "V01_EP"),
    candidate_weight: float = 1.0,
    baseline_weight: float = 1.0,
) -> dict[str, object]:
    """Spec for Strategy single-factor-on arm (NOT TURN50 product).

    Returns factor_ids + icir_weights so exactly ``baseline`` + one candidate
    enter integrate; other ``P1_SINGLE_VAR_GATE_IDS`` stay at weight 0.
    ``promotion_approved`` remains false at session level.
    """
    cand = resolve_factor_id(candidate)
    base = [resolve_factor_id(b) for b in baseline_ids]
    if cand in base:
        raise ValueError(f"candidate_already_in_baseline:{cand}")
    weights: dict[str, float] = {b: float(baseline_weight) for b in base}
    weights[cand] = float(candidate_weight)
    for fid in P1_SINGLE_VAR_GATE_IDS:
        weights.setdefault(resolve_factor_id(fid), 0.0)
    # ensure selected candidate not zeroed by setdefault order
    weights[cand] = float(candidate_weight)
    factor_ids = tuple(base + [cand])
    return {
        "factor_ids": factor_ids,
        "icir_weights": weights,
        "integrate_mode": "icir",
        "candidate": cand,
        "baseline_ids": tuple(base),
        "promotion_approved": False,
        "not_turn50_product": True,
        "note": "single_var_contrast_research_only",
    }


def run_p1_single_var_contrast_session(
    session: date,
    universe_ids: Sequence[str],
    float_mktcap: Mapping[str, float],
    sw_l1: Sequence[SWL1AsOfAssignment],
    *,
    candidate: str,
    baseline_ids: Sequence[str] = ("M01_12_1", "V01_EP"),
    candidate_weight: float = 1.0,
    turn_ortho_mode: str = "industry_size_only",
    apply_gram_schmidt: bool = False,
    **kwargs,
) -> P1SessionResult:
    """Run one research arm: baseline + single candidate (weight>0).

    Default skips TURN-vs-M01/EP OLS+GS (safer after Full D1 failure).
    Pass turn_ortho_mode='ols_then_gs' only to reproduce the failed paper arm.
    Never builds a TURN50 standalone book.
    """
    spec = build_single_var_contrast_spec(
        candidate,
        baseline_ids=baseline_ids,
        candidate_weight=candidate_weight,
    )
    kwargs = dict(kwargs)
    kwargs.pop("factor_ids", None)
    kwargs.pop("icir_weights", None)
    kwargs.pop("integrate_mode", None)
    result = run_p1_integrate_session(
        session,
        universe_ids,
        float_mktcap,
        sw_l1,
        factor_ids=spec["factor_ids"],  # type: ignore[arg-type]
        integrate_mode="icir",
        icir_weights=spec["icir_weights"],  # type: ignore[arg-type]
        turn_ortho_mode=turn_ortho_mode,
        apply_gram_schmidt=apply_gram_schmidt,
        **kwargs,
    )
    # annotate
    notes = list(result.notes) + [
        f"single_var_candidate={spec['candidate']}",
        "not_turn50_product",
        "promotion_approved=false",
    ]
    return P1SessionResult(
        session=result.session,
        universe_ids=result.universe_ids,
        raw=result.raw,
        residuals=result.residuals,
        orthogonalized=result.orthogonalized,
        composite=result.composite,
        ic_summaries=result.ic_summaries,
        coverage=result.coverage,
        stubs=result.stubs,
        notes=tuple(notes),
        promotion_approved=False,
    )



# ---------------------------------------------------------------------------
# TURN contrast arms (Leo "both", 2026-10-10). Main book has turn_20d weight 0.
# Clamp semantics: turn_20d's share of total integrate weight is capped at
# ``turn_weight_clamp`` (0.25) with each baseline member at weight 1.0.
# ---------------------------------------------------------------------------
TURN_CONTRAST_ARMS: dict[str, dict[str, object]] = {
    "TURN_ISO": {"turn_ortho_mode": "industry_size_only", "apply_gram_schmidt": False},
    "TURN_OLS": {"turn_ortho_mode": "ols_only", "apply_gram_schmidt": False},
}
TURN_WEIGHT_CLAMP_DEFAULT: float = 0.25


def build_turn_contrast_arm_kwargs(
    arm: str,
    *,
    baseline_ids: Sequence[str] = ("M01_12_1", "V01_EP"),
    turn_weight_clamp: float = TURN_WEIGHT_CLAMP_DEFAULT,
) -> dict[str, object]:
    """kwargs for ``run_p1_integrate_session`` for TURN_ISO / TURN_OLS arms."""
    key = str(arm).upper()
    if key not in TURN_CONTRAST_ARMS:
        raise ValueError(f"turn_contrast_arm_invalid:{arm}")
    if not (0.0 < turn_weight_clamp < 1.0):
        raise ValueError("turn_weight_clamp_must_be_in_(0,1)")
    base = [resolve_factor_id(b) for b in baseline_ids]
    n = len(base)
    turn_w = turn_weight_clamp * n / (1.0 - turn_weight_clamp)
    weights: dict[str, float] = {b: 1.0 for b in base}
    for fid in P1_SINGLE_VAR_GATE_IDS:
        weights.setdefault(resolve_factor_id(fid), 0.0)
    weights["turn_20d"] = float(turn_w)
    return {
        "factor_ids": tuple(base + ["turn_20d"]),
        "integrate_mode": "icir",
        "icir_weights": weights,
        **TURN_CONTRAST_ARMS[key],
    }


def run_p1_turn_contrast_arm_session(
    session: date,
    universe_ids: Sequence[str],
    float_mktcap: Mapping[str, float],
    sw_l1: Sequence[SWL1AsOfAssignment],
    *,
    arm: str,
    baseline_ids: Sequence[str] = ("M01_12_1", "V01_EP"),
    turn_weight_clamp: float = TURN_WEIGHT_CLAMP_DEFAULT,
    **kwargs,
) -> P1SessionResult:
    """Run TURN_ISO / TURN_OLS contrast arm (research-only, not TURN50)."""
    spec = build_turn_contrast_arm_kwargs(
        arm, baseline_ids=baseline_ids, turn_weight_clamp=turn_weight_clamp
    )
    for k in spec:
        kwargs.pop(k, None)
    r = run_p1_integrate_session(session, universe_ids, float_mktcap, sw_l1, **spec, **kwargs)
    return P1SessionResult(
        session=r.session, universe_ids=r.universe_ids, raw=r.raw, residuals=r.residuals,
        orthogonalized=r.orthogonalized, composite=r.composite, ic_summaries=r.ic_summaries,
        coverage=r.coverage, stubs=r.stubs,
        notes=tuple(list(r.notes) + [f"turn_contrast_arm={str(arm).upper()}",
                                     f"turn_weight_clamp={turn_weight_clamp}",
                                     "not_turn50_product", "promotion_approved=false"]),
        promotion_approved=False,
    )


def raw_panels_from_p1(raw: Mapping[str, Mapping[str, float]], session: date) -> list[RawFactorPanel]:
    return [
        RawFactorPanel(
            factor_id=fid,
            session=session,
            values=dict(vals),
            available_at_ok=bool(vals),
            notes=("p1_research", "promotion_approved=false", f"family={P1_FAMILY.get(fid, '?')}"),
        )
        for fid, vals in raw.items()
    ]


# --- MAINBOOK_V2 (Leo 2026-10-10 21:30 ET; research-only) -------------------

MAINBOOK_V2_TURN_ORTHO_MODE = "industry_size_only"
MAINBOOK_V2_APPLY_GRAM_SCHMIDT = False


def mainbook_v2_d1_config(**overrides):
    """D1MaskConfig for full-market universe (no bottom-mktcap cut).

    Uses the existing Eng field ``exclude_bottom_mktcap_pct=0.0`` (quantile(0)
    = min → nothing dropped). Eng defaults in d1_masks.py are NOT changed.
    Mktcap stays a neutralization variable, not a filter.
    """
    from quantlab.universe.d1_masks import D1MaskConfig

    kw = {"exclude_bottom_mktcap_pct": 0.0}
    kw.update(overrides)
    return D1MaskConfig(**kw)


VALUATION_TUSHARE_PATH = Path("/workspace/QuantLab/data/v2/valuation/daily_basic_valuation_tushare.parquet")
FLOAT_MKTCAP_TUSHARE_PATH = Path("/workspace/QuantLab/data/v2/float_mktcap/float_mktcap_daily_tushare.parquet")


def _read_window(path: Path, cols: list[str], start, end) -> pd.DataFrame:
    return pd.read_parquet(
        path,
        columns=["instrument_id", "trade_date", *cols],
        filters=[("trade_date", ">=", pd.Timestamp(start)), ("trade_date", "<=", pd.Timestamp(end))],
    )


def load_valuation_pb_panel(
    instrument_ids: Sequence[str] | None,
    end_session: date,
    *,
    lookback_calendar_days: int = 30,
    path: Path | None = None,
) -> pd.DataFrame:
    """Wide pb panel (DatetimeIndex x id) from Tushare daily_basic valuation.

    pb<=0 or null → NaN (excluded by compute_bp_from_pb). Research-only.
    """
    path = Path(path or VALUATION_TUSHARE_PATH)
    df = _read_window(path, ["pb"], pd.Timestamp(end_session) - pd.Timedelta(days=lookback_calendar_days), end_session)
    if instrument_ids is not None:
        df = df[df["instrument_id"].isin(set(map(str, instrument_ids)))]
    df = df.assign(pb=pd.to_numeric(df["pb"], errors="coerce"))
    df.loc[~(df["pb"] > 0), "pb"] = np.nan
    wide = df.pivot_table(index="trade_date", columns="instrument_id", values="pb", aggfunc="last")
    wide.index = pd.to_datetime(wide.index).normalize()
    return wide.sort_index()


def load_float_mktcap_tushare_asof(
    session: date,
    instrument_ids: Sequence[str] | None = None,
    *,
    max_stale_days: int = 10,
    path: Path | None = None,
) -> dict[str, float]:
    """Full-market float_mktcap (CNY) as-of ``session`` (last value ≤ session,
    within ``max_stale_days``) from float_mktcap_daily_tushare.parquet."""
    path = Path(path or FLOAT_MKTCAP_TUSHARE_PATH)
    df = _read_window(path, ["float_mktcap"], pd.Timestamp(session) - pd.Timedelta(days=max_stale_days), session)
    if instrument_ids is not None:
        df = df[df["instrument_id"].isin(set(map(str, instrument_ids)))]
    df = df[pd.to_numeric(df["float_mktcap"], errors="coerce") > 0]
    last = df.sort_values("trade_date").groupby("instrument_id")["float_mktcap"].last()
    return {str(k): float(v) for k, v in last.items()}


def run_mainbook_v2_session(
    session: date,
    universe_ids: Sequence[str],
    float_mktcap: Mapping[str, float] | None,
    sw_l1: Sequence[SWL1AsOfAssignment],
    *,
    pb_source: str = "valuation_tushare",
    **kwargs,
) -> P1SessionResult:
    """Main-book V2 composite for Strategy (full-market universe ids).

    Members (equal weight): R02_20D, turn_20d, L01_RV60, V02_BP, LIQ02_AMIHUD.
    industry+mktcap neutral; turn_20d ortho=industry_size_only; no GS.
    ``float_mktcap`` None/empty → Tushare full-market as-of loader (a
    caller-provided map is never overridden). ``pb_source``:
    valuation_tushare (canonical) | panel (legacy pb_mrq).
    promotion_approved=false. Selection is in-sample → trial ledger.
    """
    from quantlab.factors.p1_factor_lib import MAINBOOK_V2_MEMBER_IDS, load_ohlcv_panels

    extra: list[str] = []
    ids = [str(x) for x in universe_ids]
    if not float_mktcap:
        float_mktcap = load_float_mktcap_tushare_asof(session, ids)
        extra.append(f"float_mktcap_source=tushare_full_market_n={len(float_mktcap)}")
    else:
        extra.append("float_mktcap_source=caller")
    if pb_source == "valuation_tushare":
        panels = kwargs.get("panels")
        if panels is None:
            from quantlab.data.v2_readers import default_v2_roots

            roots = default_v2_roots()
            panels, _ = load_ohlcv_panels(
                ids,
                d0_root=kwargs.get("d0_root") or roots.d0_root,
                asof_extend_dir=kwargs.get("asof_extend_dir") or roots.asof_extend_dir,
                end_session=session,
            )
        panels = dict(panels)
        panels["pb_mrq"] = load_valuation_pb_panel(ids, session)
        kwargs["panels"] = panels
        extra.append("V02_BP_pb_source=daily_basic_valuation_tushare")
    elif pb_source != "panel":
        raise ValueError(f"pb_source_invalid:{pb_source}")
    kwargs.setdefault("factor_ids", MAINBOOK_V2_MEMBER_IDS)
    kwargs.setdefault("turn_ortho_mode", MAINBOOK_V2_TURN_ORTHO_MODE)
    kwargs.setdefault("apply_gram_schmidt", MAINBOOK_V2_APPLY_GRAM_SCHMIDT)
    kwargs.setdefault("mktcap_neutral", True)
    res = run_p1_integrate_session(session, ids, float_mktcap, sw_l1, **kwargs)
    assert res.promotion_approved is False
    object.__setattr__(res, "notes", tuple(res.notes) + tuple(extra)) if hasattr(res, "__dataclass_fields__") else None
    return res
