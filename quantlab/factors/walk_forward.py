"""Walk-forward / rolling evaluation skeleton (process IC only).

Emits :class:`ProcessICSummary`-style metrics. Never a promotion gate.
``promotion_approved`` is always False.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Callable, Mapping, Sequence

from quantlab.factors.v2_min_pipeline import (
    ProcessICRow,
    ProcessICSummary,
    cross_section_ic,
    summarize_ic,
)


@dataclass(frozen=True)
class WalkForwardWindow:
    """One train/eval split on the session calendar (research scaffolding)."""

    window_id: int
    train_start: date
    train_end: date
    eval_session: date
    expanding: bool
    n_train_sessions: int


@dataclass(frozen=True)
class WalkForwardProcessReport:
    """Aggregated process-IC walk-forward report — not promotion evidence."""

    factor_id: str
    windows: tuple[WalkForwardWindow, ...]
    ic_summary: ProcessICSummary
    forward_horizon_sessions: int
    process_metric_only: bool = True
    promotion_approved: bool = False
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.promotion_approved:
            raise ValueError("walk_forward_promotion_approved_must_be_false")
        if not self.process_metric_only:
            raise ValueError("walk_forward_must_flag_process_metric_only")
        if self.ic_summary.promotion_approved:
            raise ValueError("walk_forward_ic_summary_promotion_must_be_false")


@dataclass(frozen=True)
class WalkForwardBatchResult:
    reports: tuple[WalkForwardProcessReport, ...]
    promotion_approved: bool = False
    notes: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.promotion_approved:
            raise ValueError("walk_forward_batch_promotion_approved_must_be_false")


def iter_session_windows(
    sessions: Sequence[date],
    *,
    train_size: int,
    step: int = 1,
    expanding: bool = False,
    min_train: int | None = None,
) -> tuple[WalkForwardWindow, ...]:
    """Rolling (or expanding) windows: train on prior sessions, eval on next.

    ``eval_session`` is the first session after the train end in the calendar.
    Requires ``train_size >= 1`` and enough sessions for at least one eval.
    """
    sess = list(sessions)
    if train_size < 1:
        raise ValueError("train_size_must_be_positive")
    if step < 1:
        raise ValueError("step_must_be_positive")
    floor = min_train if min_train is not None else train_size
    out: list[WalkForwardWindow] = []
    wid = 0
    # rolling: train is sess[i : i+train_size], eval is sess[i+train_size]
    # expanding: train is sess[0 : i+train_size], eval same
    i = 0
    while True:
        train_end_idx = i + train_size - 1
        eval_idx = train_end_idx + 1
        if eval_idx >= len(sess):
            break
        if expanding:
            train_start_idx = 0
        else:
            train_start_idx = i
        n_train = train_end_idx - train_start_idx + 1
        if n_train < floor:
            i += step
            continue
        out.append(
            WalkForwardWindow(
                window_id=wid,
                train_start=sess[train_start_idx],
                train_end=sess[train_end_idx],
                eval_session=sess[eval_idx],
                expanding=expanding,
                n_train_sessions=n_train,
            )
        )
        wid += 1
        i += step
    return tuple(out)


def run_walk_forward_process_ic(
    factor_by_session: Mapping[date, Mapping[str, float]],
    forward_ret_by_session: Mapping[date, Mapping[str, float]],
    *,
    factor_id: str,
    sessions: Sequence[date],
    train_size: int,
    step: int = 1,
    expanding: bool = False,
    forward_horizon: int = 5,
) -> WalkForwardProcessReport:
    """Emit process IC on each eval session (factor vs forward return).

    Does **not** fit or select on train — train bounds are recorded for
    future research hooks (e.g. neutralize params). IC is process-only.
    """
    windows = iter_session_windows(
        sessions, train_size=train_size, step=step, expanding=expanding
    )
    rows: list[ProcessICRow] = []
    used_windows: list[WalkForwardWindow] = []
    for w in windows:
        fac = factor_by_session.get(w.eval_session)
        fwd = forward_ret_by_session.get(w.eval_session)
        if not fac or not fwd:
            continue
        rows.append(
            cross_section_ic(
                fac,
                fwd,
                session=w.eval_session,
                factor_id=factor_id,
                horizon=forward_horizon,
            )
        )
        used_windows.append(w)
    summary = summarize_ic(rows, factor_id)
    return WalkForwardProcessReport(
        factor_id=factor_id,
        windows=tuple(used_windows),
        ic_summary=summary,
        forward_horizon_sessions=forward_horizon,
        process_metric_only=True,
        promotion_approved=False,
        notes=(
            "process_metric_only=true",
            "promotion_approved=false",
            "not_a_promotion_gate",
            f"expanding={expanding}",
            f"train_size={train_size}",
            f"step={step}",
        ),
    )


def run_walk_forward_batch(
    factors_by_id: Mapping[str, Mapping[date, Mapping[str, float]]],
    forward_ret_by_session: Mapping[date, Mapping[str, float]],
    *,
    sessions: Sequence[date],
    train_size: int,
    step: int = 1,
    expanding: bool = False,
    forward_horizon: int = 5,
) -> WalkForwardBatchResult:
    """Walk-forward process IC for multiple factor ids."""
    reports = []
    for fid, by_sess in factors_by_id.items():
        reports.append(
            run_walk_forward_process_ic(
                by_sess,
                forward_ret_by_session,
                factor_id=fid,
                sessions=sessions,
                train_size=train_size,
                step=step,
                expanding=expanding,
                forward_horizon=forward_horizon,
            )
        )
    return WalkForwardBatchResult(
        reports=tuple(reports),
        promotion_approved=False,
        notes=("process_metric_only=true", "promotion_approved=false"),
    )


FactorPanelFn = Callable[[date], Mapping[str, float]]


def run_walk_forward_with_factory(
    compute_factor: FactorPanelFn,
    compute_forward: FactorPanelFn,
    *,
    factor_id: str,
    sessions: Sequence[date],
    train_size: int,
    step: int = 1,
    expanding: bool = False,
    forward_horizon: int = 5,
) -> WalkForwardProcessReport:
    """Lazy variant: call callables per eval session (for pipeline hooks)."""
    factor_by_session: dict[date, Mapping[str, float]] = {}
    forward_by_session: dict[date, Mapping[str, float]] = {}
    windows = iter_session_windows(
        sessions, train_size=train_size, step=step, expanding=expanding
    )
    for w in windows:
        if w.eval_session not in factor_by_session:
            factor_by_session[w.eval_session] = dict(compute_factor(w.eval_session))
        if w.eval_session not in forward_by_session:
            forward_by_session[w.eval_session] = dict(compute_forward(w.eval_session))
    return run_walk_forward_process_ic(
        factor_by_session,
        forward_by_session,
        factor_id=factor_id,
        sessions=sessions,
        train_size=train_size,
        step=step,
        expanding=expanding,
        forward_horizon=forward_horizon,
    )
