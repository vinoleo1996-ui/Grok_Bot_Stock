#!/usr/bin/env python3
"""Standalone small-cap β sleeve — research smoke/report (no performance claims).

Writes ``output/v2_proto/smallcap_beta_sleeve.json`` for 2026-06-30 and 2026-10-09:
basket count, filters hit, industry mix, ADV floor drops, single-name cap,
tier weights (10/15/20%), crowding flags, interaction with core 510300 plan,
and the 2024-02 stress-harness status (pre-engine-fix descriptive only).

Run::

    cd /workspace/QuantLab
    PYTHONPATH=. /workspace/qlvenv/bin/python scripts/smallcap_beta_sleeve.py
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SESSIONS = (date(2026, 6, 30), date(2026, 10, 9))
OUT = ROOT / "output" / "v2_proto" / "smallcap_beta_sleeve.json"


def main() -> int:
    from quantlab.beta import VolTargetBetaSleeveProvider
    from quantlab.beta.smallcap_sleeve import SmallcapBetaSleeveProvider
    from quantlab.mandate_v2 import load_mandate_v2

    from quantlab.promotion_gate import gate_status

    m = load_mandate_v2()
    # Platform overall gate is Eng-owned (quantlab/promotion_gate.py); record it,
    # but this Beta sleeve stays research-only: its own outputs are promotion_approved=False.
    platform_gate = gate_status()
    sc = SmallcapBetaSleeveProvider(m)
    core = VolTargetBetaSleeveProvider(m)
    cfg = sc.config()

    by_session = {}
    for s in SESSIONS:
        core_plan = core.plan(s)
        pl = sc.plan(s, core_plan=core_plan)
        b = pl.basket
        assert pl.promotion_approved is False and pl.bound_by_max_etf is False
        assert b.data_ready and len(b.names) > 0, f"empty_basket:{s}"
        assert max(b.industry_mix.values()) <= int(cfg["selection"]["max_names_per_industry"])
        for t, tw in pl.tiers.items():
            assert tw.per_name_weight <= tw.single_name_cap_book + 1e-12
            assert tw.lot_infeasible_names == 0, f"lot_unaffordable:{s}:{t}:{tw.lot_infeasible_names}"
            assert tw.min_trade_feasible, f"min_trade:{s}:{t}"
            assert tw.sleeve_weight_effective <= tw.sleeve_weight_target + 1e-9
        by_session[str(s)] = {
            "session": str(s),
            "data_session": str(b.data_session),
            "basket_count": len(b.names),
            "band_used": b.band_used,
            "funnel": dict(b.funnel),
            "filters_hit": dict(b.filters_hit),
            "adv_floor_drops": b.filters_hit.get("drop_adv_floor"),
            "adv_stats_selected": dict(b.adv_stats),
            "fundamentals_fallback_used": b.fundamentals_fallback_used,
            "industry_mix_sw_l1": dict(b.industry_mix),
            "n_industries": len(b.industry_mix),
            "max_names_one_industry": max(b.industry_mix.values()),
            "names": list(b.names),
            "tiers": {
                t: {
                    "sleeve_weight_target": tw.sleeve_weight_target,
                    "sleeve_weight_effective": tw.sleeve_weight_effective,
                    "per_name_weight": tw.per_name_weight,
                    "single_name_cap_book": tw.single_name_cap_book,
                    "single_name_cap_binding": tw.single_name_cap_binding,
                    "per_name_notional_cny_at_research_notional": tw.per_name_notional_cny,
                    "min_trade_feasible": tw.min_trade_feasible,
                    "lot_infeasible_names": tw.lot_infeasible_names,
                    "adv_capacity_breaches": tw.adv_capacity_breaches,
                }
                for t, tw in pl.tiers.items()
            },
            "capacity_required_capital": dict(pl.capacity),
            "lot_unaffordable_at_research_notional": {t: tw.lot_infeasible_names for t, tw in pl.tiers.items()},
            "crowding": dict(pl.crowding),
            "beta_descriptive": dict(pl.beta_descriptive),
            "interaction_with_core_510300": pl.interaction_with_core,
            "core_plan": {
                "etf_sleeve_weight": core_plan.etf_sleeve_weight,
                "cash_weight": core_plan.cash_weight,
                "residual_book_weight_cap": core_plan.residual_book_weight_cap,
                "implied_sleeve_beta": core_plan.implied_sleeve_beta,
                "drawdown_tier": core_plan.drawdown_tier,
            },
            "notes": list(b.notes),
            "promotion_approved": False,
        }

    stress = sc.stress_test("smallcap_crash_2024_02")
    payload = {
        "ok": True,
        "phase": "beta_smallcap_standalone_research",
        "promotion_approved": False,
        "promotion_scope": "beta_smallcap_sleeve_research_only",
        "platform_overall_gate_eng": platform_gate,
        "bound_by_max_etf": False,
        "mandate_json_edited": False,
        "main_beta": "sh.510300",
        "performance_reporting": "blocked_until_engine_limit_fix",
        "capital": {
            "account_capital_cny": cfg["risk_controls"]["account_capital_cny"],
            "research_notional_cny": cfg["risk_controls"]["research_notional_cny"],
            "capacity_buffer": cfg["risk_controls"]["capacity_buffer"],
            "note": cfg["risk_controls"]["research_notional_note"],
            "open_capacity_note": "600k account cannot hold 50 names at T10/T15 (and not fully at T20); research runs at larger notional",
        },
        "contract": sc.describe_contract(),
        "config_path": "quantlab/beta/configs/smallcap_standalone_v1.json",
        "data_paths": {
            "panels": cfg["data"]["panels_dir"],
            "panels_builder": cfg["data"]["panels_builder"],
            "sw_l1": cfg["data"]["sw_l1"],
            "reference_m2_replication": "research/attrib_v2/benchmarks.py (c1/c2)",
        },
        "by_session": by_session,
        "stress_tests": {"smallcap_crash_2024_02": stress},
        "note": "Selections/weights/flags only. Stress numbers are pre-engine-fix descriptive raw-price data, not performance claims.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    # Preserve sections owned by other scripts (live profile / retention compare) on rerun.
    if OUT.exists():
        try:
            prev = json.loads(OUT.read_text(encoding="utf-8"))
        except Exception:
            prev = {}
        for k in ("live_profile", "retention_compare"):
            if k in prev and k not in payload:
                payload[k] = prev[k]
    payload["sidecar_files"] = {
        "live_profile": "output/v2_proto/smallcap_live_profile.json",
        "retention_compare": "output/v2_proto/smallcap_retention_compare.json",
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps({"ok": True, "wrote": str(OUT), "sessions": list(by_session), "stress": stress["harness_status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
