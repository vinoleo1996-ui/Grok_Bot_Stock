#!/usr/bin/env python3
"""Settle Eng debate_ledger pending decisions vs 510300 using trading_loop ETF bars.

Research-only: promotion_approved=false; no orders; allow_mock=False by default.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantlab.agents.trading_loop.settle import DEFAULT_ETF_DAILY, compute_horizon_returns
from quantlab.intel.debate_ledger import DEFAULT_DEBATE_LEDGER, JsonlDebateLedger, SettlementRecord


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", type=Path, default=DEFAULT_DEBATE_LEDGER)
    ap.add_argument("--etf-path", type=Path, default=DEFAULT_ETF_DAILY)
    ap.add_argument("--horizon", type=int, default=5)
    ap.add_argument("--allow-mock", action="store_true")
    args = ap.parse_args(argv)

    ledger = JsonlDebateLedger(args.ledger)
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    settled, pending, unavailable = [], [], []
    for p in ledger.pending_decisions():
        did = str(p.get("decision_id") or "")
        instrument = str(p.get("instrument") or "")
        session = str(p.get("session") or "")
        m = compute_horizon_returns(
            instrument,
            session,
            args.horizon,
            benchmark="510300.SH",
            etf_path=args.etf_path,
            allow_mock=args.allow_mock,
        )
        if m["status"] == "settled":
            rec = SettlementRecord(
                decision_id=did,
                session=session,
                instrument=instrument,
                horizon_days=args.horizon,
                benchmark="510300.SH",
                raw_return=float(m["raw_return"]),
                alpha_vs_benchmark=float(m["alpha_vs_510300"]),
                reflection_zh=m["reflection_zh"] + " [settle_debate_ledger_vs_510300]",
                settled_at=now,
                promotion_approved=False,
            )
            ledger.append_settlement(rec)
            settled.append({**{k: m[k] for k in ("entry_date","exit_date","raw_return","bench_return","alpha_vs_510300","settle_source")}, "decision_id": did, "instrument": instrument, "session": session})
        elif m["status"] == "pending":
            pending.append(did)
        else:
            rec = SettlementRecord(
                decision_id=did,
                session=session,
                instrument=instrument,
                horizon_days=args.horizon,
                benchmark="510300.SH",
                raw_return=None,
                alpha_vs_benchmark=None,
                reflection_zh=f"unavailable: {m.get('reflection_zh')}；不伪造。",
                settled_at=now,
                promotion_approved=False,
            )
            ledger.append_settlement(rec)
            unavailable.append(did)

    print(json.dumps({
        "ledger": str(args.ledger),
        "settled_n": len(settled),
        "pending_n": len(pending),
        "unavailable_n": len(unavailable),
        "settled": settled,
        "strategy_promotion_approved": False,
        "allow_mock": bool(args.allow_mock),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
