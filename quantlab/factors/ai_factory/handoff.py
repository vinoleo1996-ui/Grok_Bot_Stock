"""Top-K AI factor handoff to residual/Strategy score panels (THIS_WEEK stub).

Does not invent backtest numbers. Missing Top-K / panels -> data_ready=False.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from quantlab.factors.ai_factory.ledger import DEFAULT_LEDGER
from quantlab.factors.ops import Expr, apply_expr, parse_expr

PROMOTION_APPROVED = False
DEFAULT_TOP_K = (
    Path(__file__).resolve().parents[3] / "output" / "ai_factor" / "gp_explore" / "top_k.json"
)


@dataclass(frozen=True)
class HandoffScorePanel:
    session: date
    scores: Mapping[str, float]
    source: str
    member_exprs: tuple[str, ...]
    n_ledger: int
    promotion_approved: bool = field(default=False, init=False)
    data_ready: bool = False
    todos: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "promotion_approved", False)
        if self.promotion_approved:
            raise ValueError("handoff_promotion_approved_must_be_false")


def _ledger_n(path: Path) -> int:
    if not path.exists():
        return 0
    n = 0
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                n += 1
    return n


def _load_topk_exprs(path: Path) -> list[str]:
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        items = raw.get("top_k") or raw.get("candidates") or raw.get("exprs") or []
    elif isinstance(raw, list):
        items = raw
    else:
        return []
    out: list[str] = []
    for it in items:
        if isinstance(it, str):
            out.append(it)
        elif isinstance(it, dict):
            e = it.get("expr") or it.get("expr_str")
            if e:
                out.append(str(e))
    return out


def _equal_weight_z(rows: list[pd.Series], members: Sequence[str]) -> dict[str, float]:
    if not rows:
        return {}
    mat = pd.concat(rows, axis=1)
    mat = mat.reindex(list(members))
    z = mat.apply(lambda s: (s - s.mean()) / s.std(ddof=0) if s.std(ddof=0) and s.notna().sum() > 1 else s * 0.0, axis=0)
    score = z.mean(axis=1)
    return {str(k): float(v) for k, v in score.items() if np.isfinite(v)}


def handoff_topk_to_scores(
    session: date,
    members: Sequence[str],
    *,
    top_k_path: Path | None = None,
    panels: Mapping[str, pd.DataFrame] | None = None,
    integrate: str = "equal_weight_z",
    ledger_path: Path | None = None,
    max_k: int = 3,
) -> HandoffScorePanel:
    """Map frozen Top-K expressions to a cross-section score panel.

    If top_k or panels missing, returns empty scores with todos (research-safe).
    """
    path = top_k_path or DEFAULT_TOP_K
    n = _ledger_n(ledger_path or DEFAULT_LEDGER)
    todos: list[str] = []
    exprs = _load_topk_exprs(path)[: max(0, max_k)]
    if not exprs:
        todos.append(f"top_k_missing_or_empty:{path}")
    if panels is None:
        todos.append("panels_required_to_eval_exprs")
        return HandoffScorePanel(
            session=session,
            scores={},
            source="ai_factor_l1_topk",
            member_exprs=tuple(exprs),
            n_ledger=n,
            data_ready=False,
            todos=tuple(todos),
        )

    rows: list[pd.Series] = []
    used: list[str] = []
    for e in exprs:
        try:
            # Prefer tuple JSON if present; else skip non-parseable string forms.
            fac = None
            if e.strip().startswith("("):
                import ast

                fac = apply_expr(parse_expr(ast.literal_eval(e)), panels)
            else:
                todos.append(f"expr_string_form_not_auto_parsed:{e[:48]}")
                continue
            if session not in fac.index:
                todos.append(f"session_not_in_factor_index:{e[:32]}")
                continue
            rows.append(fac.loc[session])
            used.append(e)
        except Exception as exc:  # noqa: BLE001 — research stub: collect TODO
            todos.append(f"expr_eval_failed:{type(exc).__name__}")

    if integrate != "equal_weight_z":
        todos.append(f"integrate_mode_unsupported:{integrate}")
    scores = _equal_weight_z(rows, members) if rows else {}
    ready = bool(scores)
    if not ready and not todos:
        todos.append("no_scores")
    return HandoffScorePanel(
        session=session,
        scores=scores,
        source="ai_factor_l1_topk",
        member_exprs=tuple(used),
        n_ledger=n,
        data_ready=ready,
        todos=tuple(todos),
    )
