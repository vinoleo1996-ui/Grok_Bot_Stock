"""TradingAgents-adapted research loop for A-share QuantLab.

Original QuantLab state machine + decision memory settle.
Does NOT vendor LangGraph / Yahoo / Reddit stacks.
strategy_promotion_approved is always False here.
"""

from .state_machine import LoopNode, LOOP_EDGES, next_node, stub_run_once
from .schemas import DecisionLogEntry, Rating

PROMOTION_APPROVED = False

__all__ = [
    "LoopNode",
    "LOOP_EDGES",
    "next_node",
    "stub_run_once",
    "DecisionLogEntry",
    "Rating",
    "PROMOTION_APPROVED",
]
