"""Candidate validation gate (THIS_WEEK Eng stub).

Explore may PASS_EXPLORE; sealed never auto-approves without leo_seal_approved.
promotion_approved always False on verdicts.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from quantlab.factors.ai_factory.ledger import DEFAULT_LEDGER

PROMOTION_APPROVED = False

# Hard mid/large universe tokens accepted for explore (Alpha may extend carefully).
_ALLOWED_UNIVERSE_PREFIXES = ("midlarge", "hs300", "csi500", "top1500", "d1_midlarge")
_MIN_COST = 0.001  # 10bp floor for explore gate warning; Alpha cost policy owns final


@dataclass(frozen=True)
class ValidateVerdict:
    status: str
    n_attempts: int
    notes: tuple[str, ...] = ()
    promotion_approved: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "promotion_approved", False)


def _count_ledger(path: Path) -> int:
    if not path.exists():
        return 0
    n = 0
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                n += 1
    return n


def validate_candidate(
    *,
    engine: str,
    expr_str: str | None,
    window: str,
    universe: str,
    cost: float,
    ledger_path: Path | None = None,
    sealed_requested: bool = False,
    leo_seal_approved: bool = False,
    extra_notes: tuple[str, ...] = (),
) -> ValidateVerdict:
    """Validate one AI-factory candidate before handoff / seal request.

    Rules (Eng platform only — not Alpha research conclusions):
    - sealed_requested and not leo_seal_approved -> BLOCK_SEALED
    - missing ledger file or N==0 when engine claims search -> BLOCK_NO_LEDGER
    - universe must look mid/large (ban bare 'smallcap' mainline token)
    - cost below floor -> BLOCK_COST
    - else PASS_EXPLORE
    """
    path = ledger_path or DEFAULT_LEDGER
    n = _count_ledger(path)
    notes: list[str] = list(extra_notes)
    notes.append(f"engine={engine}")
    notes.append(f"window={window}")
    if expr_str:
        notes.append(f"expr_len={len(expr_str)}")

    if sealed_requested and not leo_seal_approved:
        return ValidateVerdict("BLOCK_SEALED", n, tuple(notes + ["leo_seal_required"]))

    if sealed_requested and leo_seal_approved:
        # Still never promotion-approve; Alpha owns the actual sealed run.
        return ValidateVerdict(
            "PASS_SEAL_REQUEST_ONLY",
            n,
            tuple(notes + ["seal_run_not_executed_by_eng", "promotion_approved=false"]),
        )

    u = (universe or "").lower()
    if "smallcap" in u and "control" not in u:
        return ValidateVerdict("BLOCK_UNIVERSE", n, tuple(notes + ["smallcap_mainline_forbidden"]))
    if u and not any(u.startswith(p) or p in u for p in _ALLOWED_UNIVERSE_PREFIXES):
        notes.append("universe_not_in_allowlist_prefixes_warn")

    if cost < _MIN_COST:
        return ValidateVerdict("BLOCK_COST", n, tuple(notes + [f"cost<{_MIN_COST}"]))

    if engine in {"gp", "gp_search", "lgbm", "repr", "elasticnet"} and n <= 0:
        return ValidateVerdict("BLOCK_NO_LEDGER", n, tuple(notes + ["ledger_empty_or_missing"]))

    return ValidateVerdict("PASS_EXPLORE", n, tuple(notes + ["promotion_approved=false"]))
