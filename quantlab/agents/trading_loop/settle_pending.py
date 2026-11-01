"""CLI: settle pending decisions in the trading-loop decision log vs 510300.

Usage:
  python -m quantlab.agents.trading_loop.settle_pending
  python -m quantlab.agents.trading_loop.settle_pending --log output/trading_loop/decision_log.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .settle import DEFAULT_ETF_DAILY, DEFAULT_LOG, settle_log


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Settle trading-loop decisions vs 510300")
    p.add_argument("--log", type=Path, default=DEFAULT_LOG)
    p.add_argument("--etf-path", type=Path, default=DEFAULT_ETF_DAILY)
    p.add_argument("--no-mock", action="store_true", help="fail instead of mock bars")
    args = p.parse_args(argv)

    summary = settle_log(
        args.log,
        etf_path=args.etf_path,
        allow_mock=not args.no_mock,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
