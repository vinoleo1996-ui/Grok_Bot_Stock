"""L3 residual Alpha factor factory (Phase 0 interface).

Pipeline (Strategy Design V2 §4.4 / Mandate signal_construction):
  1. Raw factors on L0 universe (mask-first members only).
  2. Industry-neutralize via SW_L1 PIT (:class:`SWL1MemberRow` /
     :class:`SWL1AsOfAssignment`) — **not** D0 csrc industry_records.
  3. Optional float_mktcap neutralize.
  4. Integrate composite (default_mode=integrate); mix is control-arm only.

Frozen factor family ids from Mandate ``composite_members_proposed``:
  V01_EP, V02_BP, M01_12_1, Q01_profitability, Q03_safety, L01_RV60

No Sharpe/PnL promotion narrative here.

Minimal executable research path: :mod:`quantlab.factors.v2_min_pipeline`
(M01_12_1 + V01_EP; IC/ICIR as process metrics only).

P1 research path: :mod:`quantlab.factors.p1_factor_lib` +
:mod:`quantlab.factors.p1_pipeline` expand momentum/reversal/value/quality/
low-vol/liquidity; factory wires neutralize + integrate.
Still ``promotion_approved=false``; financials PIT not promotable.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Mapping, Protocol, Sequence

import numpy as np
import pandas as pd

from quantlab.factors.engine import winsorize_zscore
from quantlab.factors.neutralize import cap_bucket_demean, sector_demean
from quantlab.mandate_v2 import MandateV2
from quantlab.v2_schemas import (
    FLOAT_MKTCAP_FIELD,
    SW_L1_TABLE_NAME,
    SWL1AsOfAssignment,
    SWL1MemberRow,
)

# Locked composite member ids (Mandate V2); Data/Eng fill implementations later.
COMPOSITE_MEMBER_IDS: tuple[str, ...] = (
    "V01_EP",
    "V02_BP",
    "M01_12_1",
    "Q01_profitability",
    "Q03_safety",
    "L01_RV60",
)


@dataclass(frozen=True)
class RawFactorPanel:
    """Cross-section of one raw factor at one session (typed stub)."""

    factor_id: str
    session: date
    # instrument_id -> value; empty until Data+Eng compute paths land
    values: Mapping[str, float]
    available_at_ok: bool
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class ResidualFactorPanel:
    """Industry-(optional mktcap-)neutral residual scores."""

    factor_id: str
    session: date
    industry_scheme: str  # SW_L1
    mktcap_neutral: bool
    values: Mapping[str, float]
    sw_l1_coverage: int
    unknown_industry_count: int
    promotion_approved: bool = False
    data_ready: bool = False
    todos: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.promotion_approved:
            raise ValueError("residual_panel_promotion_approved_must_be_false")


@dataclass(frozen=True)
class CompositeScorePanel:
    """Integrated composite residual scores (AQR-style integrate, not mix)."""

    session: date
    mode: str  # integrate | mix (mix = control arm only per Mandate)
    member_ids: tuple[str, ...]
    scores: Mapping[str, float]
    promotion_approved: bool = False
    data_ready: bool = False
    todos: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.promotion_approved:
            raise ValueError("composite_promotion_approved_must_be_false")


class ResidualAlphaFactorFactory(Protocol):
    def list_member_ids(self) -> tuple[str, ...]: ...

    def compute_raw(self, session: date, factor_id: str, universe: Sequence[str]) -> RawFactorPanel: ...

    def neutralize(
        self,
        raw: RawFactorPanel,
        sw_l1: Sequence[SWL1AsOfAssignment],
        *,
        mktcap: Mapping[str, float] | None = None,
    ) -> ResidualFactorPanel: ...

    def integrate(self, residuals: Sequence[ResidualFactorPanel]) -> CompositeScorePanel: ...


@dataclass(frozen=True)
class StubResidualAlphaFactorFactory:
    """Phase 0 stub: schemas locked; compute paths NotImplemented / empty."""

    mandate: MandateV2

    def list_member_ids(self) -> tuple[str, ...]:
        proposed = self.mandate.signal_construction.composite_members_proposed
        return proposed if proposed else COMPOSITE_MEMBER_IDS

    def compute_raw(self, session: date, factor_id: str, universe: Sequence[str]) -> RawFactorPanel:
        if factor_id not in self.list_member_ids():
            raise KeyError(f"unknown_factor_id:{factor_id}")
        if universe:
            raise NotImplementedError(
                "raw_factor_compute_not_implemented:"
                f"factor_id={factor_id} session={session} n={len(universe)}; "
                "await PIT financials/panels + L0 membership"
            )
        return RawFactorPanel(
            factor_id=factor_id,
            session=session,
            values={},
            available_at_ok=False,
            notes=("empty_universe_stub", "promotion_approved=false"),
        )

    def neutralize(
        self,
        raw: RawFactorPanel,
        sw_l1: Sequence[SWL1AsOfAssignment],
        *,
        mktcap: Mapping[str, float] | None = None,
    ) -> ResidualFactorPanel:
        if raw.values or sw_l1:
            raise NotImplementedError(
                "residual_neutralize_not_implemented:"
                f"need {SW_L1_TABLE_NAME} ({SWL1MemberRow.SCHEMA_VERSION}) "
                f"and optional {FLOAT_MKTCAP_FIELD}; "
                "do not use D0 industry_records csrc proxy"
            )
        return ResidualFactorPanel(
            factor_id=raw.factor_id,
            session=raw.session,
            industry_scheme=self.mandate.portfolio_limits.industry_scheme,
            mktcap_neutral=bool(mktcap) and self.mandate.signal_construction.optional_mktcap_neutral,
            values={},
            sw_l1_coverage=0,
            unknown_industry_count=0,
            promotion_approved=False,
            data_ready=False,
            todos=(
                f"TODO(Data): {SW_L1_TABLE_NAME}",
                f"TODO(Data): {FLOAT_MKTCAP_FIELD} if mktcap_neutral",
                "promotion_approved=false",
            ),
        )

    def integrate(self, residuals: Sequence[ResidualFactorPanel]) -> CompositeScorePanel:
        mode = self.mandate.signal_construction.default_mode
        if any(r.values for r in residuals):
            raise NotImplementedError(
                "composite_integrate_not_implemented:"
                f"mode={mode}; await residual panels with real values"
            )
        return CompositeScorePanel(
            session=residuals[0].session if residuals else date.min,
            mode=mode,
            member_ids=self.list_member_ids(),
            scores={},
            promotion_approved=False,
            data_ready=False,
            todos=("no_residual_values", "promotion_approved=false"),
        )

    def describe_contract(self) -> Mapping[str, object]:
        sc = self.mandate.signal_construction
        return {
            "layer": "L3_industry_neutral_residual_alpha_book",
            "default_mode": sc.default_mode,
            "mix_mode": sc.mix_mode,
            "industry_neutral_residual_book": sc.industry_neutral_residual_book,
            "optional_mktcap_neutral": sc.optional_mktcap_neutral,
            "industry_scheme": self.mandate.portfolio_limits.industry_scheme,
            "sw_l1_table": SW_L1_TABLE_NAME,
            "sw_l1_schema_version": SWL1MemberRow.SCHEMA_VERSION,
            "float_mktcap_field": FLOAT_MKTCAP_FIELD,
            "composite_members": list(self.list_member_ids()),
            "min_positions": self.mandate.portfolio_limits.min_positions_target,
            "max_positions": self.mandate.portfolio_limits.max_positions_stocks,
            "promotion_approved": False,
        }


# ---------------------------------------------------------------------------
# Shared helpers (research-only; never promotion gates)
# ---------------------------------------------------------------------------
IMPLEMENTED_RAW_FACTOR_IDS: tuple[str, ...] = (
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


def sw_l1_to_sector_map(sw_l1: Sequence[SWL1AsOfAssignment]) -> dict[str, str]:
    """Map instrument_id -> sw_code (UNKNOWN bucket when missing)."""
    out: dict[str, str] = {}
    for a in sw_l1:
        if a.is_unknown_bucket or not a.sw_code:
            out[str(a.instrument_id)] = "UNKNOWN"
        else:
            out[str(a.instrument_id)] = str(a.sw_code)
    return out


def neutralize_raw_values(
    values: Mapping[str, float],
    sw_l1: Sequence[SWL1AsOfAssignment],
    *,
    mktcap: Mapping[str, float] | None = None,
    mktcap_neutral: bool = False,
) -> tuple[dict[str, float], int, int]:
    """Industry demean (+ optional float_mktcap bucket demean) on a CS map.

    Returns (neutral_values, sw_l1_coverage, unknown_industry_count).
    """
    if not values:
        unknown = sum(1 for a in sw_l1 if a.is_unknown_bucket or not a.sw_code)
        covered = sum(1 for a in sw_l1 if not a.is_unknown_bucket and a.sw_code)
        return {}, covered, unknown
    sector_map = sw_l1_to_sector_map(sw_l1)
    series = pd.Series({str(k): float(v) for k, v in values.items()}, dtype=float)
    series = series.replace([np.inf, -np.inf], np.nan).dropna()
    if series.empty:
        unknown = sum(1 for a in sw_l1 if a.is_unknown_bucket or not a.sw_code)
        covered = sum(1 for a in sw_l1 if not a.is_unknown_bucket and a.sw_code)
        return {}, covered, unknown
    # Ensure every scored name has a sector key (UNKNOWN if absent from SW_L1)
    for iid in series.index.astype(str):
        sector_map.setdefault(str(iid), "UNKNOWN")
    neut = sector_demean(series, sector_map)
    if mktcap_neutral and mktcap:
        neut = cap_bucket_demean(neut, {str(k): float(v) for k, v in mktcap.items()})
    out = {str(k): float(v) for k, v in neut.dropna().items() if np.isfinite(v)}
    covered = sum(
        1
        for iid in out
        if sector_map.get(iid, "UNKNOWN") != "UNKNOWN"
    )
    unknown = sum(1 for iid in out if sector_map.get(iid, "UNKNOWN") == "UNKNOWN")
    return out, covered, unknown


def equal_weight_zscore_integrate(
    residuals: Sequence[ResidualFactorPanel],
    *,
    mode: str,
    member_ids: Sequence[str],
) -> CompositeScorePanel:
    """Equal-weight average of per-member CS z-scores (integrate path).

    ``mode=mix`` is allowed only as a control-arm stub (same math, flagged).
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
    for r in residuals:
        if not r.values:
            continue
        s = pd.Series(dict(r.values), dtype=float)
        z = winsorize_zscore(s)
        z_panels.append(z.rename(r.factor_id))
    notes: list[str] = ["promotion_approved=false", "equal_weight_zscore_integrate"]
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
    # equal weight over available members per instrument
    scores_s = stacked.mean(axis=1, skipna=True).dropna()
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


@dataclass
class ResearchResidualAlphaFactorFactory:
    """Research-grade residual factory (P1 factor family compute paths).

    Implements momentum / reversal / value / quality / low-vol / liquidity
    raw cross-sections via :mod:`quantlab.factors.p1_factor_lib`. Always
    ``promotion_approved=false``; financials PIT not promotable.
    """

    mandate: MandateV2
    close_panel: pd.DataFrame | None = None
    float_mktcap: Mapping[str, float] = field(default_factory=dict)
    d0_root: Path | None = None
    asof_extend_dir: Path | None = None
    # Optional injected views (avoid re-load in smoke loops)
    ep_research_view: object | None = None
    fin_view: object | None = None
    bs_view: object | None = None
    # Optional OHLCV / PB panels (from p1_factor_lib.load_ohlcv_panels)
    amount_panel: pd.DataFrame | None = None
    turnover_panel: pd.DataFrame | None = None
    pb_panel: pd.DataFrame | None = None
    # SW_L1 as-of for M03 industry-residual momentum
    sw_l1_asof: tuple = ()

    def list_member_ids(self) -> tuple[str, ...]:
        proposed = self.mandate.signal_construction.composite_members_proposed
        return proposed if proposed else COMPOSITE_MEMBER_IDS

    def list_p1_factor_ids(self) -> tuple[str, ...]:
        from quantlab.factors.p1_factor_lib import P1_FACTOR_IDS

        return P1_FACTOR_IDS

    def compute_raw(
        self, session: date, factor_id: str, universe: Sequence[str]
    ) -> RawFactorPanel:
        from quantlab.factors.p1_factor_lib import P1_FACTOR_ALIASES, resolve_factor_id

        fid = resolve_factor_id(factor_id)
        known = set(self.list_member_ids()) | set(IMPLEMENTED_RAW_FACTOR_IDS) | set(
            self.list_p1_factor_ids()
        ) | set(P1_FACTOR_ALIASES)
        if fid not in known and factor_id not in known:
            raise KeyError(f"unknown_factor_id:{factor_id}")
        ids = [str(x) for x in universe]

        if fid in IMPLEMENTED_RAW_FACTOR_IDS:
            return self._compute_p1_member(session, fid, ids)
        # Unknown / not yet implemented composite remnant
        return RawFactorPanel(
            factor_id=factor_id,
            session=session,
            values={},
            available_at_ok=False,
            notes=(
                "stub_awaiting_data_or_eng",
                f"factor_id={factor_id}",
                "promotion_approved=false",
                "research_only",
            ),
        )

    def _compute_p1_member(
        self, session: date, factor_id: str, ids: Sequence[str]
    ) -> RawFactorPanel:
        from quantlab.factors.p1_pipeline import compute_p1_raw_map

        panels = {
            "close": self.close_panel if self.close_panel is not None else pd.DataFrame(),
            "amount": self.amount_panel if self.amount_panel is not None else pd.DataFrame(),
            "turnover": self.turnover_panel
            if self.turnover_panel is not None
            else pd.DataFrame(),
            "pb_mrq": self.pb_panel if self.pb_panel is not None else pd.DataFrame(),
        }
        # If close missing, let compute_p1_raw_map load from disk
        use_panels = panels if self.close_panel is not None and not self.close_panel.empty else None
        raw, notes, coverage = compute_p1_raw_map(
            session,
            ids,
            self.float_mktcap,
            sw_l1=tuple(self.sw_l1_asof) if self.sw_l1_asof else (),
            d0_root=self.d0_root,
            asof_extend_dir=self.asof_extend_dir,
            panels=use_panels,
            fin_view=self.fin_view,
            ep_research_view=self.ep_research_view,
            factor_ids=(factor_id,),
        )
        values = dict(raw.get(factor_id) or {})
        return RawFactorPanel(
            factor_id=factor_id,
            session=session,
            values=values,
            available_at_ok=bool(values),
            notes=tuple(notes) + (f"coverage={coverage.get(factor_id, 0)}",),
        )

    def _compute_m01(self, session: date, ids: Sequence[str]) -> RawFactorPanel:
        from quantlab.factors.v2_min_pipeline import (
            _load_close_panel,
            compute_momentum_cross_section,
        )

        close = self.close_panel
        notes: list[str] = ["promotion_approved=false", "research_merged_panels"]
        if close is None or close.empty:
            if not ids:
                return RawFactorPanel(
                    factor_id="M01_12_1",
                    session=session,
                    values={},
                    available_at_ok=False,
                    notes=("empty_universe", "promotion_approved=false"),
                )
            from quantlab.data.v2_readers import default_v2_roots

            roots = default_v2_roots()
            d0 = Path(self.d0_root) if self.d0_root is not None else roots.d0_root
            ext = (
                Path(self.asof_extend_dir)
                if self.asof_extend_dir is not None
                else roots.asof_extend_dir
            )
            close = _load_close_panel(
                ids, d0_root=d0, asof_extend_dir=ext, end_session=session
            )
            notes.append(f"close_panel_loaded_shape={close.shape}")
        m12, _m3 = compute_momentum_cross_section(close, session)
        idset = set(ids) if ids else set(m12)
        values = {k: float(v) for k, v in m12.items() if k in idset and np.isfinite(v)}
        return RawFactorPanel(
            factor_id="M01_12_1",
            session=session,
            values=values,
            available_at_ok=bool(values),
            notes=tuple(notes),
        )

    def _compute_v01_ep(self, session: date, ids: Sequence[str]) -> RawFactorPanel:
        from quantlab.factors.v2_min_pipeline import compute_ep_cross_section

        ep, meta = compute_ep_cross_section(
            session,
            ids,
            self.float_mktcap,
            fin_view=self.fin_view,
            bs_view=self.bs_view,
            ep_research_view=self.ep_research_view,
        )
        if meta.get("financials_promotable"):
            raise RuntimeError("financials_must_remain_non_promotable")
        # Optional CS z for consistency with min pipeline display
        if ep:
            ep_z = winsorize_zscore(pd.Series(ep, dtype=float))
            ep = {str(k): float(v) for k, v in ep_z.dropna().items()}
        notes = (
            "financials_pit_not_promotable",
            "financials_promotable=false",
            f"metric={meta.get('metric_used')}",
            f"ep_definition={meta.get('ep_definition')}",
            "promotion_approved=false",
        )
        return RawFactorPanel(
            factor_id="V01_EP",
            session=session,
            values=ep,
            available_at_ok=bool(ep),
            notes=notes,
        )

    def neutralize(
        self,
        raw: RawFactorPanel,
        sw_l1: Sequence[SWL1AsOfAssignment],
        *,
        mktcap: Mapping[str, float] | None = None,
    ) -> ResidualFactorPanel:
        use_mktcap = bool(mktcap) and bool(
            self.mandate.signal_construction.optional_mktcap_neutral
        )
        values, covered, unknown = neutralize_raw_values(
            raw.values,
            sw_l1,
            mktcap=mktcap,
            mktcap_neutral=use_mktcap,
        )
        todos = [
            f"industry_scheme={SW_L1_TABLE_NAME}",
            "sw_l1_research_not_promotable",
            "promotion_approved=false",
        ]
        if use_mktcap:
            todos.append(f"mktcap_neutral={FLOAT_MKTCAP_FIELD}")
        return ResidualFactorPanel(
            factor_id=raw.factor_id,
            session=raw.session,
            industry_scheme=self.mandate.portfolio_limits.industry_scheme,
            mktcap_neutral=use_mktcap,
            values=values,
            sw_l1_coverage=covered,
            unknown_industry_count=unknown,
            promotion_approved=False,
            data_ready=bool(values),
            todos=tuple(todos),
        )

    def integrate(self, residuals: Sequence[ResidualFactorPanel]) -> CompositeScorePanel:
        mode = self.mandate.signal_construction.default_mode
        return equal_weight_zscore_integrate(
            residuals, mode=mode, member_ids=self.list_member_ids()
        )

    def integrate_mix_control(
        self, residuals: Sequence[ResidualFactorPanel]
    ) -> CompositeScorePanel:
        """Explicit mix control-arm stub (same EW z integrate, flagged)."""
        return equal_weight_zscore_integrate(
            residuals, mode="mix", member_ids=self.list_member_ids()
        )

    def compute_raw_m01_v01(
        self, session: date, universe: Sequence[str]
    ) -> tuple[RawFactorPanel, RawFactorPanel]:
        """Convenience: both implemented raw members."""
        return (
            self.compute_raw(session, "M01_12_1", universe),
            self.compute_raw(session, "V01_EP", universe),
        )

    def describe_contract(self) -> Mapping[str, object]:
        sc = self.mandate.signal_construction
        return {
            "layer": "L3_industry_neutral_residual_alpha_book",
            "factory": "ResearchResidualAlphaFactorFactory",
            "default_mode": sc.default_mode,
            "mix_mode": sc.mix_mode,
            "industry_neutral_residual_book": sc.industry_neutral_residual_book,
            "optional_mktcap_neutral": sc.optional_mktcap_neutral,
            "industry_scheme": self.mandate.portfolio_limits.industry_scheme,
            "sw_l1_table": SW_L1_TABLE_NAME,
            "sw_l1_schema_version": SWL1MemberRow.SCHEMA_VERSION,
            "float_mktcap_field": FLOAT_MKTCAP_FIELD,
            "composite_members": list(self.list_member_ids()),
            "implemented_raw": list(IMPLEMENTED_RAW_FACTOR_IDS),
            "financials_promotable": False,
            "promotion_approved": False,
        }
