"""Cross-sectional factor orthogonalization (research-only skeleton).

Residualize one factor against another (OLS) or a ordered set (Gram-Schmidt).
IC/ICIR are never computed here; ``promotion_approved`` is always False.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Mapping, Sequence

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class OrthogonalizedPanel:
    """One factor residualized vs controls at one session."""

    factor_id: str
    session: date
    versus_ids: tuple[str, ...]
    method: str  # ols_residual | gram_schmidt
    values: Mapping[str, float]
    n_obs: int
    promotion_approved: bool = False
    process_metric_only: bool = True
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.promotion_approved:
            raise ValueError("ortho_panel_promotion_approved_must_be_false")


@dataclass(frozen=True)
class OrthogonalizedSetResult:
    """Ordered Gram-Schmidt / sequential OLS residual set."""

    session: date
    order: tuple[str, ...]
    method: str
    panels: tuple[OrthogonalizedPanel, ...]
    promotion_approved: bool = False
    notes: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.promotion_approved:
            raise ValueError("ortho_set_promotion_approved_must_be_false")


def _aligned_frame(
    target: Mapping[str, float],
    controls: Sequence[Mapping[str, float]],
) -> pd.DataFrame:
    keys = set(target)
    for c in controls:
        keys &= set(c)
    ids = sorted(keys)
    data: dict[str, list[float]] = {"target": [float(target[i]) for i in ids]}
    for j, c in enumerate(controls):
        data[f"c{j}"] = [float(c[i]) for i in ids]
    return pd.DataFrame(data, index=ids)


def residualize_ols(
    target: Mapping[str, float],
    *controls: Mapping[str, float],
    add_intercept: bool = True,
) -> dict[str, float]:
    """Cross-sectional OLS residual of ``target`` on ``controls`` (intersecting ids)."""
    if not controls:
        return {str(k): float(v) for k, v in target.items() if np.isfinite(v)}
    frame = _aligned_frame(target, controls)
    if len(frame) < max(4, len(controls) + 2):
        return {}
    y = frame["target"].to_numpy(dtype=float)
    x_cols = [c for c in frame.columns if c.startswith("c")]
    x = frame[x_cols].to_numpy(dtype=float)
    if add_intercept:
        x = np.column_stack([np.ones(len(frame)), x])
    try:
        beta, *_ = np.linalg.lstsq(x, y, rcond=None)
        resid = y - x @ beta
    except np.linalg.LinAlgError:
        return {}
    out: dict[str, float] = {}
    for iid, r in zip(frame.index.astype(str), resid):
        if np.isfinite(r):
            out[str(iid)] = float(r)
    return out


def residualize_vs(
    target: Mapping[str, float],
    control: Mapping[str, float],
    *,
    factor_id: str,
    control_id: str,
    session: date,
) -> OrthogonalizedPanel:
    """Residualize factor A vs factor B (single control)."""
    values = residualize_ols(target, control)
    return OrthogonalizedPanel(
        factor_id=factor_id,
        session=session,
        versus_ids=(control_id,),
        method="ols_residual",
        values=values,
        n_obs=len(values),
        promotion_approved=False,
        notes=("research_only", "promotion_approved=false", "process_metric_only=true"),
    )


def gram_schmidt_set(
    factors: Mapping[str, Mapping[str, float]],
    order: Sequence[str],
    *,
    session: date,
) -> OrthogonalizedSetResult:
    """Sequential residualization in ``order`` (first kept raw; later vs prior orthos).

    Each subsequent factor is OLS-residualized against all earlier orthogonalized
    panels (Gram-Schmidt style via regression residuals).
    """
    if not order:
        return OrthogonalizedSetResult(
            session=session,
            order=(),
            method="gram_schmidt",
            panels=(),
            promotion_approved=False,
            notes=("empty_order", "promotion_approved=false"),
        )
    missing = [fid for fid in order if fid not in factors]
    if missing:
        raise KeyError(f"ortho_missing_factor_ids:{','.join(missing)}")

    orth_maps: list[dict[str, float]] = []
    panels: list[OrthogonalizedPanel] = []
    for i, fid in enumerate(order):
        raw = factors[fid]
        if i == 0:
            vals = {str(k): float(v) for k, v in raw.items() if np.isfinite(v)}
            versus: tuple[str, ...] = ()
        else:
            vals = residualize_ols(raw, *orth_maps)
            versus = tuple(order[:i])
        orth_maps.append(vals)
        panels.append(
            OrthogonalizedPanel(
                factor_id=fid,
                session=session,
                versus_ids=versus,
                method="gram_schmidt",
                values=vals,
                n_obs=len(vals),
                promotion_approved=False,
                notes=("research_only", "promotion_approved=false"),
            )
        )
    return OrthogonalizedSetResult(
        session=session,
        order=tuple(order),
        method="gram_schmidt",
        panels=tuple(panels),
        promotion_approved=False,
        notes=("research_only", "promotion_approved=false", "not_a_promotion_gate"),
    )
