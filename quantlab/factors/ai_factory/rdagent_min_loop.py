"""Minimal RD-Agent-style closed loop stub (STACK_RETHINK §6 Alpha #2).

Stages: Synthesis → Implementation → Validation → Analysis.
Does NOT call sealed windows. promotion_approved always False.
Full microsoft/RD-Agent dependency is NOT required for this minimal loop.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

PROMOTION_APPROVED = False


@dataclass
class Hypothesis:
    expr_str: str
    who_pays_zh: str
    source: str = "structural_gp_or_seed"
    notes: str = ""


@dataclass
class LoopResult:
    hypothesis: Hypothesis
    implemented: bool
    metrics: dict[str, Any] = field(default_factory=dict)
    validation_passed: bool = False
    novelty_ok: bool = False
    textbook_banned_hit: bool = False
    promotion_approved: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "promotion_approved", False)


def validate_candidate(
    *,
    expr_str: str,
    metrics: dict[str, Any],
    is_textbook: Callable[[str], bool],
    is_structural: Callable[[str], bool],
) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if is_textbook(expr_str):
        reasons.append("textbook_ban")
    if not is_structural(expr_str):
        reasons.append("not_structural_leaf")
    if metrics.get("novelty_fail"):
        reasons.append("public_factor_corr>0.5")
    ann = metrics.get("ann_net")
    if ann is None or not (isinstance(ann, (int, float)) and ann == ann) or ann <= 0:
        reasons.append("ann_net_nonpositive")
    if not metrics.get("who_pays_zh") and not metrics.get("who_pays"):
        reasons.append("missing_who_pays")
    return (len(reasons) == 0, reasons)


def run_min_loop(
    hypotheses: list[Hypothesis],
    implement_fn: Callable[[Hypothesis], dict[str, Any]],
    is_textbook: Callable[[str], bool],
    is_structural: Callable[[str], bool],
) -> list[LoopResult]:
    """One-pass closed loop; caller supplies implement_fn (backtest/IC/fitness)."""
    out: list[LoopResult] = []
    for h in hypotheses:
        try:
            met = implement_fn(h)
            implemented = True
        except Exception as exc:  # noqa: BLE001
            met = {"error": type(exc).__name__, "ann_net": None}
            implemented = False
        met = dict(met)
        met.setdefault("who_pays_zh", h.who_pays_zh)
        ok, reasons = validate_candidate(
            expr_str=h.expr_str,
            metrics=met,
            is_textbook=is_textbook,
            is_structural=is_structural,
        )
        met["validation_reasons"] = reasons
        out.append(
            LoopResult(
                hypothesis=h,
                implemented=implemented,
                metrics=met,
                validation_passed=ok,
                novelty_ok=not bool(met.get("novelty_fail")),
                textbook_banned_hit=is_textbook(h.expr_str),
            )
        )
    return out
