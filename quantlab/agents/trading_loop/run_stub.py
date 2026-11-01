"""CLI: walk stub state machine once and append a pending decision.

Usage:
  python -m quantlab.agents.trading_loop.run_stub
  python -m quantlab.agents.trading_loop.run_stub --session 2024-07-01 --instrument 510500.SH
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .state_machine import DEFAULT_LOG, describe_graph, stub_run_once


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="QuantLab trading-loop stub (research-only)")
    p.add_argument("--session", default="2024-07-01")
    p.add_argument("--instrument", default="510500.SH")
    p.add_argument("--log", type=Path, default=DEFAULT_LOG)
    p.add_argument("--show-graph", action="store_true")
    args = p.parse_args(argv)

    if args.show_graph:
        print(json.dumps(describe_graph(), ensure_ascii=False, indent=2))
        return 0

    # Fresh demo log if default and exists from prior runs — append is fine;
    # callers may pass a clean path.
    trace, entry = stub_run_once(
        session=args.session,
        instrument=args.instrument,
        log_path=args.log,
    )
    print("trace:", " → ".join(trace))
    print("appended:", entry["decision_id"], "status=", entry["status"])
    print("log:", args.log)
    print("strategy_promotion_approved=false")
    return 0


if __name__ == "__main__":
    sys.exit(main())
