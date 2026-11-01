"""Decision-log schemas for the A-share trading research loop.

Research-grade only. Never cash NAV; never auto-order; promotion always false.
"""
from __future__ import annotations

from typing import Any, Literal, TypedDict

PROMOTION_APPROVED = False

Rating = Literal[
    "Buy",
    "Overweight",
    "Hold",
    "Underweight",
    "Sell",
    "Abstain",
]

DecisionStatus = Literal["pending", "settled", "unavailable", "rejected_by_pm"]


class AnalystBrief(TypedDict, total=False):
    role: str  # fund / news / flow / tech
    session: str
    instrument: str
    thesis_zh: str
    evidence_refs: list[str]
    asof_ts: str


class DebateTurnLog(TypedDict, total=False):
    side: Literal["bull", "bear"]
    thesis_zh: str
    evidence_refs: list[str]


class DecisionLogEntry(TypedDict, total=False):
    """One research decision awaiting / after relative-benchmark settle."""

    decision_id: str
    session: str  # YYYY-MM-DD decision as-of (PIT cutoff date)
    instrument: str  # e.g. 510500.SH or 600519.SH
    universe_note: str  # mid/large only; no small-cap main
    rating: Rating
    target_weight_hint: float  # research hint only; not book weight
    horizon_trading_days: int
    benchmark: str  # always 510300.SH for A-share book alpha
    rationale_zh: str
    analysts: list[AnalystBrief]
    debate: list[DebateTurnLog]
    research_manager_zh: str
    trader_proposal_zh: str
    risk_review_zh: str
    pm_verdict: Literal["approve_research", "reject", "hold"]
    status: DecisionStatus
    asof_decision_ts: str
    strategy_promotion_approved: bool
    # filled by settle
    entry_date: str
    exit_date: str
    raw_return: float | None
    bench_return: float | None
    alpha_vs_510300: float | None
    reflection_zh: str
    settled_at: str
    settle_source: str  # e.g. etf_daily_adj | mock


def force_research_flags(entry: dict[str, Any]) -> dict[str, Any]:
    """Stamp immutable research gates on any decision dict."""
    out = dict(entry)
    out["strategy_promotion_approved"] = False
    out.setdefault("benchmark", "510300.SH")
    out.setdefault("universe_note", "中大盘/宽基ETF；禁小盘主仓；现货无融资")
    return out
