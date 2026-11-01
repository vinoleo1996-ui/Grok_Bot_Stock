"""Buffer-style drawdown brake + concave exposure map for the small-cap β sleeve.

Research switch (Leo 2026-10-10 22:09 ET), literature card 68 (arXiv 2609.23272):
robust drawdown-safe actions take the form ``u = γ · C``, ``C = V − (1 − d)·V_max``.

Exposure map (fraction of SLEEVE NAV invested in the basket)::

    z  = V / V_max                      # sleeve NAV vs its running peak (unreset)
    h  = clip(γ · (1 − (1 − d) / z), 0, 1)   # = γ · cushion / V, capped at 1 (never lever)
    e  = floor + (1 − floor) · h

* continuous and monotone in z (no step ladder / bang-bang)
* concave in z on the active region (1 − c/z is concave); min(·,1) keeps concavity;
  the only non-concave point is where cushion hits 0 (DD = d) and e sits on the floor
* never adds risk because NAV is below a target — exposure only falls as DD deepens
* recoverable: re-risks as the cushion rebuilds; floor avoids the zero-exposure
  absorbing state noted in the card (Silverman)
* at e = 1 the sleeve holds exactly its tier weight — the brake never levers up

γ calibration: γ = 1 / L, L = worst 2-day basket loss support, taken as the larger of
(a) the structural two-consecutive-limit-down loss of the basket's board mix
(main board 10% → 19%; ChiNext/STAR 20% → 36%; BJ 30% → 51%), and
(b) the empirical worst 2-day EW basket loss over a pre-start calibration window.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


def board_limit(code: str) -> float:
    c = code.split(".")[-1]
    if code.startswith("bj.") or c.startswith(("8", "4", "92")):
        return 0.30
    if c.startswith(("300", "301", "688", "689")):
        return 0.20
    return 0.10


def structural_two_day_loss(codes: Sequence[str]) -> float:
    """EW basket loss if every name hits limit-down two days running."""
    if not codes:
        return 0.19
    losses = [1.0 - (1.0 - board_limit(c)) ** 2 for c in codes]
    return float(sum(losses) / len(losses))


@dataclass(frozen=True)
class BrakeParams:
    dd_limit: float
    gamma: float
    floor: float
    rerisk_max_step: float
    trade_band: float
    nav_basis: str = "sleeve_nav"

    def exposure(self, z: float) -> float:
        return exposure_map(z, self)


def exposure_map(z: float, p: BrakeParams) -> float:
    """Continuous, monotone, concave-on-active-region exposure in [floor, 1]."""
    if z <= 0:
        return p.floor
    h = p.gamma * (1.0 - (1.0 - p.dd_limit) / z)
    h = min(1.0, max(0.0, h))
    return p.floor + (1.0 - p.floor) * h


def smooth_step(prev: float, target: float, p: BrakeParams) -> float:
    """De-risk immediately; re-risk at most ``rerisk_max_step`` per day (anti-whipsaw)."""
    if target <= prev:
        return target
    return min(target, prev + p.rerisk_max_step)


def calibrate_gamma(
    codes: Sequence[str],
    empirical_two_day_losses: Sequence[float] | None,
) -> Mapping[str, float]:
    structural = structural_two_day_loss(codes)
    emp = max((float(x) for x in (empirical_two_day_losses or []) if x == x), default=0.0)
    L = max(structural, emp)
    return {
        "structural_two_limit_down_loss": structural,
        "empirical_worst_two_day_loss": emp,
        "support_loss_used": L,
        "gamma": 1.0 / L if L > 0 else 1.0,
    }


def concavity_check(p: BrakeParams, n: int = 200) -> Mapping[str, object]:
    """Numerical check: e(z) monotone non-decreasing; concave where floor < e < 1."""
    lo = 1.0 - p.dd_limit
    zs = [lo + (1.0 - lo) * i / n for i in range(n + 1)]
    es = [exposure_map(z, p) for z in zs]
    mono = all(es[i + 1] >= es[i] - 1e-12 for i in range(n))
    conc = True
    for i in range(1, n):
        if p.floor + 1e-9 < es[i] < 1.0 - 1e-9:
            if es[i - 1] + es[i + 1] - 2 * es[i] > 1e-9:
                conc = False
                break
    max_jump = max(abs(es[i + 1] - es[i]) for i in range(n))
    return {"monotone_in_z": mono, "concave_on_active_region": conc, "max_step_on_grid": max_jump,
            "dd_at_full_exposure_end": 1.0 - (1.0 - p.dd_limit) / (1.0 - 1.0 / p.gamma) if p.gamma > 1 else 0.0}
