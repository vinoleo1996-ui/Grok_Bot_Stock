"""TradingAgents-style debate / decision settlement — Eng contract stub.

Decision (see docs/v2/OPENSOURCE_ENG_ADOPTION_ZH.md): **ADAPT**, do not vendor
TradingAgents LangGraph stack or US Yahoo/Reddit tools.

Eng owns:
- Typed records for debate turns + decision entries + settlement outcomes
- Append-only JSONL store (research-grade; promotion_approved always False)
- Explicit boundary: this is a **decision-quality ledger**, not cash NAV

Alpha / WorkBuddy own role prompts and who speaks; Beta may read settled
ratings only as optional risk-budget features, never as fill prices.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Literal, Protocol, Sequence, TypedDict

PROMOTION_APPROVED = False
DEFAULT_DEBATE_LEDGER = (
    Path(__file__).resolve().parents[2] / "output" / "intel" / "debate_ledger.jsonl"
)

DebateRole = Literal[
    "analyst_market",
    "analyst_news",
    "analyst_sentiment",
    "bull",
    "bear",
    "research_manager",
    "risk",
    "portfolio_manager",
    "other",
]

RatingLabel = Literal[
    "Buy",
    "Overweight",
    "Hold",
    "Underweight",
    "Sell",
    "Abstain",
]


class DebateTurn(TypedDict, total=False):
    turn_id: str
    role: DebateRole
    session: str  # YYYY-MM-DD
    instrument: str
    thesis_zh: str
    evidence_refs: list[str]  # message_ids / content_hashes
    asof_decision_ts: str
    promotion_approved: bool


class DecisionEntry(TypedDict, total=False):
    decision_id: str
    session: str
    instrument: str
    rating: RatingLabel
    rationale_zh: str
    debate_turn_ids: list[str]
    status: Literal["pending", "settled", "unavailable"]
    asof_decision_ts: str
    promotion_approved: bool


class SettlementRecord(TypedDict, total=False):
    decision_id: str
    session: str
    instrument: str
    horizon_days: int
    benchmark: str
    raw_return: float | None
    alpha_vs_benchmark: float | None
    reflection_zh: str
    settled_at: str
    resolution_date: str  # YYYY-MM-DD exit bar; G6 memory PIT filter (resolved≤asof)
    promotion_approved: bool


@dataclass
class DebateRoundResult:
    """One session×instrument debate package (research stub)."""

    session: date
    instrument: str
    turns: list[DebateTurn] = field(default_factory=list)
    decision: DecisionEntry | None = None
    promotion_approved: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "promotion_approved", False)


class DebateLedgerStore(Protocol):
    def append_turns(self, turns: Sequence[DebateTurn]) -> None: ...

    def append_decision(self, entry: DecisionEntry) -> None: ...

    def append_settlement(self, record: SettlementRecord) -> None: ...

    def pending_decisions(self) -> list[DecisionEntry]: ...


class JsonlDebateLedger:
    """Minimal append-only JSONL implementation (no LLM, no market fills)."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or DEFAULT_DEBATE_LEDGER

    def _write(self, kind: str, payload: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        row = {"kind": kind, "promotion_approved": False, **dict(payload)}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    def append_turns(self, turns: Sequence[DebateTurn]) -> None:
        for t in turns:
            body = dict(t)
            body["promotion_approved"] = False
            self._write("debate_turn", body)

    def append_decision(self, entry: DecisionEntry) -> None:
        body = dict(entry)
        body.setdefault("status", "pending")
        body["promotion_approved"] = False
        self._write("decision", body)

    def append_settlement(self, record: SettlementRecord) -> None:
        body = dict(record)
        body["promotion_approved"] = False
        self._write("settlement", body)

    def _read(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        out: list[dict[str, Any]] = []
        with self.path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    out.append(json.loads(line))
        return out

    def pending_decisions(self) -> list[DecisionEntry]:
        settled_ids = {
            r["decision_id"]
            for r in self._read()
            if r.get("kind") == "settlement" and r.get("decision_id")
        }
        out: list[DecisionEntry] = []
        for r in self._read():
            if r.get("kind") != "decision":
                continue
            if r.get("decision_id") in settled_ids:
                continue
            if r.get("status", "pending") == "pending":
                out.append(r)  # type: ignore[arg-type]
        return out


def make_pending_decision(
    *,
    decision_id: str,
    session: date | str,
    instrument: str,
    rating: RatingLabel,
    rationale_zh: str = "",
    debate_turn_ids: Sequence[str] | None = None,
    asof_decision_ts: datetime | str | None = None,
) -> DecisionEntry:
    """Factory: always research-grade, status pending, promotion false."""
    sess = str(session) if not isinstance(session, date) else session.isoformat()
    return DecisionEntry(
        decision_id=decision_id,
        session=sess,
        instrument=instrument,
        rating=rating,
        rationale_zh=rationale_zh,
        debate_turn_ids=list(debate_turn_ids or ()),
        status="pending",
        asof_decision_ts=str(asof_decision_ts or ""),
        promotion_approved=False,
    )
