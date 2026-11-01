"""B2 small-cap β sleeve × Strategy fixed engine — SKELETON (waiting on Eng E1).

Research-only; promotion_approved=false. Writes a stub JSON listing arms; does NOT
claim CAGR/MDD/Calmar. Fill engine_entrypoint and metrics once E1 lands.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from quantlab.beta.smallcap_sleeve import load_smallcap_config

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/v2_proto/smallcap_b2_engine_crosscheck.json"

ARMS = [
    {"id": "R50_nobrake", "profile": "research50", "brake": False, "retention": "2xN", "terminal_delist": None},
    {"id": "R50_brake", "profile": "research50", "brake": True, "retention": "2xN", "terminal_delist": None},
    {"id": "R50_samevol", "profile": "research50", "brake": "same_vol_static", "retention": "2xN", "terminal_delist": None},
    {"id": "R50_delist50", "profile": "research50", "brake": False, "retention": "2xN", "terminal_delist": "minus_50"},
    {"id": "R50_delist100", "profile": "research50", "brake": False, "retention": "2xN", "terminal_delist": "minus_100"},
    {"id": "L600_noret", "profile": "live600k", "brake": False, "retention": "off", "terminal_delist": None},
    {"id": "L600_ret2x", "profile": "live600k", "brake": False, "retention": "2xN", "terminal_delist": None},
    {"id": "L600_delist50", "profile": "live600k", "brake": False, "retention": "2xN", "terminal_delist": "minus_50"},
    {"id": "L600_delist100", "profile": "live600k", "brake": False, "retention": "2xN", "terminal_delist": "minus_100"},
]


def main() -> int:
    cfg = load_smallcap_config()
    tiers = list(cfg.get("tiers", {"T10": 0.1, "T15": 0.15, "T20": 0.2}))
    # TODO(Eng E1): replace with the real Strategy/Eng paper entrypoint, e.g.
    #   from quantlab.portfolio.v2_strategy_paper_costs import run_...
    # or platform.execution once E1 documents the import path.
    engine_entrypoint = None  # unknown until E1
    payload = {
        "ok": True,
        "phase": "beta_b2_engine_crosscheck",
        "status": "waiting_on_E1",
        "promotion_approved": False,
        "mandate_json_edited": False,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "checklist": "docs/v2/BETA_B2_ENGINE_CROSSCHECK.md",
        "engine_entrypoint": engine_entrypoint,
        "engine_entrypoint_todo": "Eng E1 must publish the fixed paper/execution callable; Beta will not guess.",
        "engine_rules_expected": [
            "mark_to_close",
            "blocked_orders_roll_forward",
            "no_block_mark_to_zero",
            "mandate_costs_plus_stamp_by_date",
            "min_trade_2000_cny",
            "b1_full_market_rank_then_filter_for_sessions_ge_2023-01-03",
        ],
        "tiers": tiers,
        "arms": [{**a, "metrics": None, "nav_path": None, "status": "waiting_on_E1"} for a in ARMS],
        "metrics_schema": ["cagr", "mdd", "calmar", "ann_vol", "turnover_one_way_per_year",
                           "cost_frac_of_sleeve_capital", "avg_exposure", "min_exposure",
                           "time_at_floor_frac", "book_contribution_mdd"],
        "survivorship": {
            "panel_window_2023_plus": "b1_required",
            "pre_2023": "incomplete_until_full_market_circ_mv_panel",
        },
        "note": "Stub only. No performance numbers. promotion_approved=false.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(json.dumps({"ok": True, "wrote": str(OUT), "status": payload["status"],
                      "n_arms": len(ARMS), "promotion_approved": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
