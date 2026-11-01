"""V2 rebalance schedule hooks (Strategy-owned, research-only).

Ordinary rebalance cadence comes from Mandate ``ordinary_rebalance``
(default biweekly). Daily hooks cover mask / eligibility refresh and a
**stub** risk-scale slot.

Vol 16% / β 0.70 targeting remains **Beta sleeve's job**
(:mod:`quantlab.beta.sleeve`) and is idle in Phase 0 — this module does
not invent vol/beta numbers or go-live orders.

``promotion_approved`` forced False; refuse live trading paths.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Mapping, Sequence

from quantlab.mandate_v2 import MandateV2


@dataclass(frozen=True)
class RebalanceDecisionV2:
    """Whether this session is an ordinary rebalance decision day."""

    session: date
    ordinary_rebalance_due: bool
    cadence: str
    days_since_last: int | None
    min_sessions_between: int
    promotion_approved: bool = False
    research_stub: bool = True
    notes: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.promotion_approved:
            raise ValueError("rebalance_v2_promotion_approved_must_be_false")


@dataclass(frozen=True)
class DailyRiskScaleHookResultV2:
    """Daily mask / risk-scale hook stub (no live scaling applied)."""

    session: date
    mask_refresh: bool
    risk_scale_applied: bool
    scale_factor: float | None
    vol_target_owner: str
    beta_target_owner: str
    target_annual_vol: float
    target_beta_vs_benchmark: float
    promotion_approved: bool = False
    research_stub: bool = True
    notes: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.promotion_approved:
            raise ValueError("daily_risk_hook_promotion_approved_must_be_false")
        if self.risk_scale_applied:
            raise ValueError("daily_risk_hook_must_not_apply_live_scale")


def min_sessions_for_cadence(cadence: str) -> int:
    """Approximate minimum trading sessions between ordinary rebalances."""
    c = (cadence or "biweekly").lower()
    if c == "weekly":
        return 5
    if c == "biweekly":
        return 10
    if c.startswith("monthly"):
        return 20
    return 10


@dataclass(frozen=True)
class RebalanceScheduleV2:
    """Mandate-driven ordinary rebalance + daily hook stubs."""

    mandate: MandateV2

    def __post_init__(self) -> None:
        self.mandate.require_not_promoted()

    @property
    def cadence(self) -> str:
        return self.mandate.rebalance.ordinary_rebalance or "biweekly"

    def is_ordinary_rebalance_session(
        self,
        session: date,
        *,
        last_rebalance: date | None = None,
        calendar: Sequence[date] | None = None,
    ) -> RebalanceDecisionV2:
        """Return whether ``session`` is due for an ordinary (biweekly) rebalance.

        If ``calendar`` is provided (sorted trading days), count sessions between
        ``last_rebalance`` and ``session``. Otherwise fall back to calendar-day
        gaps (research heuristic only).
        """
        self.mandate.require_not_promoted()
        cadence = self.cadence
        need = min_sessions_for_cadence(cadence)
        notes: list[str] = [
            "research_stub",
            "promotion_approved=false",
            f"ordinary_rebalance={cadence}",
            "no_live_orders",
        ]

        if last_rebalance is None:
            notes.append("first_rebalance_or_no_prior")
            return RebalanceDecisionV2(
                session=session,
                ordinary_rebalance_due=True,
                cadence=cadence,
                days_since_last=None,
                min_sessions_between=need,
                promotion_approved=False,
                research_stub=True,
                notes=tuple(notes),
            )

        if calendar:
            cal = sorted({d for d in calendar})
            try:
                i0 = cal.index(last_rebalance)
                i1 = cal.index(session)
            except ValueError:
                notes.append("session_or_last_not_on_calendar_fallback_days")
                gap = (session - last_rebalance).days
                due = gap >= need
                return RebalanceDecisionV2(
                    session=session,
                    ordinary_rebalance_due=due,
                    cadence=cadence,
                    days_since_last=gap,
                    min_sessions_between=need,
                    promotion_approved=False,
                    research_stub=True,
                    notes=tuple(notes),
                )
            gap = i1 - i0
            due = gap >= need
            notes.append("gap_measured_in_trading_sessions")
            return RebalanceDecisionV2(
                session=session,
                ordinary_rebalance_due=due,
                cadence=cadence,
                days_since_last=gap,
                min_sessions_between=need,
                promotion_approved=False,
                research_stub=True,
                notes=tuple(notes),
            )

        gap = (session - last_rebalance).days
        # ~need trading days ≈ need * 1.4 calendar days heuristic when no calendar
        due = gap >= int(need * 1.4)
        notes.append("gap_measured_in_calendar_days_heuristic")
        return RebalanceDecisionV2(
            session=session,
            ordinary_rebalance_due=due,
            cadence=cadence,
            days_since_last=gap,
            min_sessions_between=need,
            promotion_approved=False,
            research_stub=True,
            notes=tuple(notes),
        )

    def daily_mask_risk_scale_hook(
        self,
        session: date,
        *,
        realized_vol: float | None = None,
        portfolio_beta: float | None = None,
    ) -> DailyRiskScaleHookResultV2:
        """Daily mask refresh + risk-scale **stub**.

        Documents ownership: vol / β targeting is Beta sleeve's responsibility
        and remains idle here. Never applies a live scale factor.
        """
        self.mandate.require_not_promoted()
        m = self.mandate
        notes = [
            "research_stub",
            "promotion_approved=false",
            "mask_and_eligibility=daily",
            "risk_budget_and_vol_scale=daily_stub_idle",
            "vol_beta_targeting_owned_by_beta_sleeve",
            "beta_sleeve_idle_today",
            f"realized_vol_ignored={realized_vol is not None}",
            f"portfolio_beta_ignored={portfolio_beta is not None}",
            "no_live_trading",
        ]
        return DailyRiskScaleHookResultV2(
            session=session,
            mask_refresh=True,
            risk_scale_applied=False,
            scale_factor=None,
            vol_target_owner="quantlab.beta.sleeve",
            beta_target_owner="quantlab.beta.sleeve",
            target_annual_vol=m.risk.target_annual_vol,
            target_beta_vs_benchmark=m.risk.target_beta_vs_benchmark,
            promotion_approved=False,
            research_stub=True,
            notes=tuple(notes),
        )

    def refuse_go_live(self) -> None:
        """Hard refuse any go-live / promotion path."""
        self.mandate.require_not_promoted()
        raise RuntimeError(
            "rebalance_v2_go_live_refused:promotion_approved_must_be_false"
        )

    def describe_contract(self) -> Mapping[str, object]:
        m = self.mandate
        return {
            "layer": "L4_portfolio_rebalance_hooks",
            "ordinary_rebalance": m.rebalance.ordinary_rebalance,
            "mask_and_eligibility": m.rebalance.mask_and_eligibility,
            "risk_budget_and_vol_scale": m.rebalance.risk_budget_and_vol_scale,
            "turnover_budget_monthly_one_way": m.rebalance.turnover_budget_monthly_one_way,
            "decision_time_china": m.rebalance.decision_time_china,
            "execution": m.rebalance.execution,
            "t_plus_1": m.rebalance.t_plus_1,
            "target_annual_vol": m.risk.target_annual_vol,
            "target_beta_vs_benchmark": m.risk.target_beta_vs_benchmark,
            "vol_beta_owner": "quantlab.beta.sleeve",
            "promotion_approved": False,
            "research_stub": True,
        }
