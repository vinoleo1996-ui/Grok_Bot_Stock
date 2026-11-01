"""Minimal state machine for QuantLab TradingAgents adapt (no LangGraph).

Nodes mirror TradingAgents process gaps; actors map to QuantLab 专责.
Stub path produces a DecisionLogEntry without calling LLMs or placing orders.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from .schemas import DecisionLogEntry, force_research_flags

PROMOTION_APPROVED = False

DEFAULT_LOG = (
    Path(__file__).resolve().parents[3]
    / "output"
    / "trading_loop"
    / "decision_log.jsonl"
)


class LoopNode(str, Enum):
    START = "START"
    ANALYSTS_PARALLEL = "ANALYSTS_PARALLEL"  # Data/AI: fund·news·flow·tech briefs
    DEBATE_BULL_BEAR = "DEBATE_BULL_BEAR"  # AI
    RESEARCH_MANAGER = "RESEARCH_MANAGER"  # AI
    TRADER_PROPOSAL = "TRADER_PROPOSAL"  # AI → weight hint (not book)
    RISK_REVIEW = "RISK_REVIEW"  # Beta
    PM_GATE = "PM_GATE"  # Grok Bot / Leo; promotion always false
    LOG_DECISION = "LOG_DECISION"
    END = "END"


# Directed edges (happy path). Settle is out-of-band (settle_pending).
LOOP_EDGES: dict[LoopNode, LoopNode] = {
    LoopNode.START: LoopNode.ANALYSTS_PARALLEL,
    LoopNode.ANALYSTS_PARALLEL: LoopNode.DEBATE_BULL_BEAR,
    LoopNode.DEBATE_BULL_BEAR: LoopNode.RESEARCH_MANAGER,
    LoopNode.RESEARCH_MANAGER: LoopNode.TRADER_PROPOSAL,
    LoopNode.TRADER_PROPOSAL: LoopNode.RISK_REVIEW,
    LoopNode.RISK_REVIEW: LoopNode.PM_GATE,
    LoopNode.PM_GATE: LoopNode.LOG_DECISION,
    LoopNode.LOG_DECISION: LoopNode.END,
}


def next_node(current: LoopNode) -> LoopNode:
    if current == LoopNode.END:
        return LoopNode.END
    return LOOP_EDGES[current]


def _stub_payload(
    *,
    session: str,
    instrument: str,
    decision_id: str,
) -> DecisionLogEntry:
    """Deterministic stub briefs — placeholders until LLM wiring."""
    asof = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    entry: DecisionLogEntry = {
        "decision_id": decision_id,
        "session": session,
        "instrument": instrument,
        "universe_note": "中大盘/宽基ETF；禁小盘主仓；现货无融资",
        "rating": "Overweight",
        "target_weight_hint": 0.02,
        "horizon_trading_days": 5,
        "benchmark": "510300.SH",
        "rationale_zh": "骨架样例：中盘宽基相对沪深300短窗观察（非晋级信号）",
        "analysts": [
            {
                "role": "fund",
                "session": session,
                "instrument": instrument,
                "thesis_zh": "（stub）基本面简报待接线 A 股 PIT 财报",
                "evidence_refs": [],
                "asof_ts": asof,
            },
            {
                "role": "flow",
                "session": session,
                "instrument": instrument,
                "thesis_zh": "（stub）资金流简报待接线北向/两融 PIT",
                "evidence_refs": [],
                "asof_ts": asof,
            },
            {
                "role": "news",
                "session": session,
                "instrument": instrument,
                "thesis_zh": "（stub）新闻简报待接线 cninfo/公告 PIT",
                "evidence_refs": [],
                "asof_ts": asof,
            },
            {
                "role": "tech",
                "session": session,
                "instrument": instrument,
                "thesis_zh": "（stub）技术简报仅作对照，不作主仓依据",
                "evidence_refs": [],
                "asof_ts": asof,
            },
        ],
        "debate": [
            {"side": "bull", "thesis_zh": "（stub）多头：相对基准有结构溢价可能", "evidence_refs": []},
            {"side": "bear", "thesis_zh": "（stub）空头：短窗噪声大，避免小盘漂移", "evidence_refs": []},
        ],
        "research_manager_zh": "（stub）综合多空：研究级 Overweight，不交 Strategy",
        "trader_proposal_zh": "（stub）建议研究仓 hint≤2%；不自动下单",
        "risk_review_zh": "（stub）Beta：对照 Mandate 12–18%/MDD−28%；禁小盘；现货 L≤1.0",
        "pm_verdict": "approve_research",
        "status": "pending",
        "asof_decision_ts": asof,
        "strategy_promotion_approved": False,
    }
    return force_research_flags(entry)  # type: ignore[return-value]


def stub_run_once(
    *,
    session: str = "2024-07-01",
    instrument: str = "510500.SH",
    decision_id: str | None = None,
    log_path: Path | None = None,
) -> tuple[list[str], DecisionLogEntry]:
    """Walk START→END, append one pending decision to JSONL. No LLM, no orders."""
    path = log_path or DEFAULT_LOG
    path.parent.mkdir(parents=True, exist_ok=True)
    did = decision_id or f"stub-{session}-{instrument.replace('.', '_')}"
    trace: list[str] = []
    node = LoopNode.START
    while node != LoopNode.END:
        trace.append(node.value)
        node = next_node(node)
    trace.append(LoopNode.END.value)

    entry = _stub_payload(session=session, instrument=instrument, decision_id=did)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return trace, entry


def describe_graph() -> list[dict[str, Any]]:
    return [{"from": a.value, "to": b.value} for a, b in LOOP_EDGES.items()]
