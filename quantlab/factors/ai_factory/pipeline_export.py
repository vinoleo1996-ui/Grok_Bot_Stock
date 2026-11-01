"""QuantMind factor_pipeline export contract — Eng/Alpha adapter stub.

Decision (see docs/v2/OPENSOURCE_ENG_ADOPTION_ZH.md): **ADAPT** the five-stage
shape (preflight → evolve → poll → backtest → explain → export), do **not**
vendor QuantMind HTTP/Qlib containers or default Alpha158 templates.

Maps onto existing stubs:
- evolve / implement  → ``rdagent_min_loop.run_min_loop``
- backtest metrics    → ``evaluate`` / ``fitness`` (caller-supplied)
- explain             → free-text field on export record (Alpha owns LLMs)
- export              → this module's ``dry_run_export`` / ``FactorExportRecord``
- ledger N            → ``ai_factory.ledger.append_attempt``

``export`` never flips ``promotion_approved``; sealed windows stay Leo-gated
via ``validate_gate``.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Literal, Protocol, Sequence, TypedDict

PROMOTION_APPROVED = False
DEFAULT_EXPORT_DIR = (
    Path(__file__).resolve().parents[3] / "output" / "ai_factor" / "exports"
)

PipelineStage = Literal[
    "preflight",
    "evolve",
    "poll",
    "backtest",
    "explain",
    "export",
]


class FactorExportRecord(TypedDict, total=False):
    factor_id: str
    expr_str: str
    direction_zh: str
    mechanism_tag: str
    universe: str
    window: str
    ic: float | None
    icir: float | None
    ann_net: float | None
    capital_cny: float | None
    explain_zh: str
    stage: PipelineStage
    exported_at: str
    promotion_approved: bool
    notes: str


@dataclass
class PipelineDryRunResult:
    stages_ok: list[PipelineStage] = field(default_factory=list)
    export: FactorExportRecord | None = None
    blocked_reasons: list[str] = field(default_factory=list)
    promotion_approved: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "promotion_approved", False)


class FactorPipelineExport(Protocol):
    """Minimal contract Alpha can implement against Eng storage."""

    def dry_run_export(
        self,
        *,
        factor_id: str,
        expr_str: str,
        metrics: dict[str, Any],
        direction_zh: str,
        mechanism_tag: str,
        universe: str,
        window: str = "explore",
    ) -> PipelineDryRunResult: ...


def _refuse_textbook_direction(direction_zh: str) -> str | None:
    banned = ("反转", "动量", "低波", "低波动", "价值成长", "多空动量")
    for b in banned:
        if b in (direction_zh or ""):
            return f"textbook_direction:{b}"
    return None


def dry_run_export(
    *,
    factor_id: str,
    expr_str: str,
    metrics: dict[str, Any],
    direction_zh: str,
    mechanism_tag: str,
    universe: str,
    window: str = "explore",
    capital_cny: float | None = None,
    explain_zh: str = "",
    export_dir: Path | None = None,
    write_file: bool = False,
) -> PipelineDryRunResult:
    """Validate + optionally write a research export record (never promotes)."""
    result = PipelineDryRunResult()
    result.stages_ok.extend(["preflight", "evolve", "poll", "backtest", "explain"])
    reasons: list[str] = []
    bad = _refuse_textbook_direction(direction_zh)
    if bad:
        reasons.append(bad)
    if not mechanism_tag:
        reasons.append("missing_mechanism_tag")
    if universe not in {"csi300", "sse50", "midlarge_top1500", "zz500", "csi800"}:
        reasons.append(f"universe_not_in_allowlist:{universe}")
    if window == "sealed":
        reasons.append("sealed_requires_leo_gate")
    if capital_cny is not None and capital_cny not in {600_000.0, 1_000_000.0, 6e5, 1e6}:
        reasons.append("capital_cny_must_be_600k_or_1m")

    if reasons:
        result.blocked_reasons = reasons
        return result

    rec: FactorExportRecord = {
        "factor_id": factor_id,
        "expr_str": expr_str[:500],
        "direction_zh": direction_zh,
        "mechanism_tag": mechanism_tag,
        "universe": universe,
        "window": window,
        "ic": metrics.get("ic"),
        "icir": metrics.get("icir"),
        "ann_net": metrics.get("ann_net"),
        "capital_cny": float(capital_cny) if capital_cny is not None else None,
        "explain_zh": explain_zh,
        "stage": "export",
        "exported_at": datetime.now().isoformat(timespec="seconds"),
        "promotion_approved": False,
        "notes": "dry_run_export; research-grade only",
    }
    result.stages_ok.append("export")
    result.export = rec
    if write_file:
        dest = export_dir or DEFAULT_EXPORT_DIR
        dest.mkdir(parents=True, exist_ok=True)
        path = dest / f"{factor_id}.json"
        path.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def pipeline_stages() -> tuple[PipelineStage, ...]:
    return ("preflight", "evolve", "poll", "backtest", "explain", "export")
