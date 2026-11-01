"""Walk-forward / label alignment stubs. promotion_approved always False."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Sequence

import numpy as np
import pandas as pd

from quantlab.factors.ops import Expr, apply_expr

PROMOTION_APPROVED = False


@dataclass(frozen=True)
class EvalResult:
    fold_id: str
    icir: float
    ann_excess_net_pp: float | None
    n_days: int
    notes: tuple[str, ...] = ()
    promotion_approved: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "promotion_approved", False)


def align_open_open_label(open_px: pd.DataFrame) -> pd.DataFrame:
    """y_t = open[t+2]/open[t+1] - 1 (conservative PIT entry)."""
    return open_px.shift(-2) / open_px.shift(-1) - 1.0


def assert_no_lookahead_label(open_px: pd.DataFrame, label: pd.DataFrame) -> None:
    manual = open_px.shift(-2) / open_px.shift(-1) - 1.0
    a = label.to_numpy(dtype=float)
    b = manual.reindex_like(label).to_numpy(dtype=float)
    m = np.isfinite(a) & np.isfinite(b)
    if m.any() and not np.allclose(a[m], b[m], equal_nan=True):
        raise AssertionError("label alignment look-ahead mismatch")


def walk_forward_ic(
    expr: Expr,
    panels: Mapping[str, pd.DataFrame],
    label: pd.DataFrame,
    train_dates: Sequence,
    cost_one_way: float = 0.0025,
) -> EvalResult:
    fac = apply_expr(expr, panels)
    idx = [d for d in train_dates if d in fac.index and d in label.index]
    if not idx:
        return EvalResult("empty", float("nan"), None, 0, ("no_train_dates",))
    ics: list[float] = []
    for dt in idx:
        x, y = fac.loc[dt], label.loc[dt]
        m = x.notna() & y.notna()
        if int(m.sum()) < 8:
            continue
        ics.append(float(np.corrcoef(x[m].rank(), y[m].rank())[0, 1]))
    if len(ics) < 5:
        return EvalResult("train", float("nan"), None, len(idx), ("insufficient_ics",))
    arr = np.asarray(ics)
    icir = float(arr.mean() / arr.std(ddof=1)) if arr.std(ddof=1) > 1e-12 else float("nan")
    _ = cost_one_way
    return EvalResult(
        "train",
        icir,
        None,
        len(idx),
        ("cost_in_fitness_via_search", "promotion_approved=false"),
    )
