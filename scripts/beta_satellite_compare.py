#!/usr/bin/env python3
"""Research: small-weight satellite compare arms (weights/flags/paths only).

Writes ``output/v2_proto/beta_satellite_compare.json``.
No Sharpe/CAGR/PnL. promotion_approved=false. Does not raise max_etf.

Run::

    cd /workspace/QuantLab
    PYTHONPATH=. /workspace/qlvenv/bin/python scripts/beta_satellite_compare.py
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
OUT = ROOT / "output" / "v2_proto" / "beta_satellite_compare.json"


def main() -> int:
    from quantlab.beta import VolTargetBetaSleeveProvider, load_compare_arms_config
    from quantlab.mandate_v2 import load_mandate_v2

    mandate = load_mandate_v2()
    if mandate.promotion_approved:
        print(json.dumps({"ok": False, "error": "promotion_approved_must_be_false"}))
        return 1

    cfg = load_compare_arms_config()
    tiny_suggestions = []
    for arm in cfg.get("arms") or []:
        if isinstance(arm, dict) and arm.get("kind") == "stock_basket":
            tiny_suggestions.append(
                {
                    "id": arm.get("id"),
                    "kind": arm.get("kind"),
                    "raise_cagr_candidate": True,
                    "suggested_max_sleeve_weight": float(arm.get("suggested_max_sleeve_weight") or 0.05),
                    "enabled_by_default": False,
                    "note": arm.get("note"),
                    "mdd_ledger_note": arm.get("mdd_ledger_note"),
                    "weight_status": "catalog_suggestion_only_not_live_scaled",
                }
            )

    providers = {
        "off": VolTargetBetaSleeveProvider(mandate, smallcap_satellite=False, max_satellite_frac=0.25),
        "on_512100": VolTargetBetaSleeveProvider(
            mandate, smallcap_satellite=True, satellite_code="sh512100", max_satellite_frac=0.25
        ),
        "on_510500": VolTargetBetaSleeveProvider(
            mandate, smallcap_satellite=True, satellite_code="sh510500", max_satellite_frac=0.25
        ),
    }

    by_session: dict = {}
    for sess in SESSIONS:
        row: dict = {"session": str(sess), "arms": {}}
        for name, prov in providers.items():
            plan = prov.plan(sess)
            if plan.promotion_approved:
                raise RuntimeError(f"promotion_leak:{name}:{sess}")
            if plan.etf_sleeve_weight is not None and plan.etf_sleeve_weight > plan.max_etf_sleeve_weight + 1e-12:
                raise RuntimeError(f"max_etf_exceeded:{name}:{sess}")
            row["arms"][name] = {
                "smallcap_satellite": plan.smallcap_satellite,
                "satellite_code": plan.satellite_code,
                "satellite_asset": plan.satellite_asset,
                "satellite_data_ready": plan.satellite_data_ready,
                "etf_sleeve_weight": plan.etf_sleeve_weight,
                "core_etf_weight": plan.core_etf_weight,
                "satellite_etf_weight": plan.satellite_etf_weight,
                "cash_weight": plan.cash_weight,
                "residual_book_weight_cap": plan.residual_book_weight_cap,
                "contribution_weight_core": plan.contribution_weight_core,
                "contribution_weight_satellite": plan.contribution_weight_satellite,
                "unit_beta_core": plan.unit_beta,
                "satellite_unit_beta": plan.satellite_unit_beta,
                "implied_sleeve_beta": plan.implied_sleeve_beta,
                "max_etf_sleeve_weight": plan.max_etf_sleeve_weight,
                "drawdown_tier": plan.drawdown_tier,
                "etf_drawdown": plan.etf_drawdown,
                "residual_weight_to_hit_target_beta": plan.residual_weight_to_hit_target_beta,
                "implied_portfolio_beta_at_residual_fill": plan.implied_portfolio_beta_at_residual_fill,
                "beta_gap_is_structural": plan.beta_gap_is_structural,
                "promotion_approved": False,
            }
        row["wide_basket_m2_catalog"] = []
        for tip in tiny_suggestions:
            w = float(tip["suggested_max_sleeve_weight"])
            row["wide_basket_m2_catalog"].append(
                {
                    **tip,
                    "illustration_if_taken_from_residual_cap": {
                        "residual_cap_off": row["arms"]["off"]["residual_book_weight_cap"],
                        "suggested_basket_w": w,
                        "feasible_vs_residual_cap_off": w
                        <= float(row["arms"]["off"]["residual_book_weight_cap"] or 0) + 1e-12,
                    },
                }
            )
        by_session[str(sess)] = row

    menu_off = providers["off"].satellite_menu(SESSIONS[0])
    catalog = providers["off"].compare_arms_catalog()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "ok": True,
        "phase": "beta_satellite_compare_arms_research",
        "promotion_approved": False,
        "main_beta": "sh.510300",
        "max_etf_raised": False,
        "params": {
            "smallcap_satellite": True,
            "max_satellite_frac": 0.25,
            "bond_risk_parity_overlay": False,
            "etf_proxies": ["sh512100", "sh510500"],
        },
        "paths": {
            "compare_arms_config": "quantlab/beta/configs/compare_arms_v1.json",
            "core_loader": "load_etf_510300",
            "core_etf_panel": "data/v2/etf_510300/panels/sh.510300.parquet",
            "equity_etf_universe": "data/etf/universe/equity_etf_daily.parquet",
            "stock_basket_hooks": "quantlab.smallcap.universe.pool_on / select",
            "output": str(OUT.relative_to(ROOT)),
            "docs": [
                "docs/v2/BETA_SMALLCAP_SATELLITE.md",
                "docs/v2/BETA_VOL_TARGET_HANDOFF.md",
            ],
        },
        "mandate_targets": {
            "target_annual_vol": mandate.risk.target_annual_vol,
            "target_beta_vs_benchmark": mandate.risk.target_beta_vs_benchmark,
            "max_etf_sleeve_weight": mandate.portfolio_limits.max_etf_sleeve_weight,
        },
        "by_session": by_session,
        "raise_cagr_candidates_listed": [c.get("id") for c in (menu_off.get("raise_cagr_candidates") or [])],
        "etf_proxy_compare_arms": menu_off.get("etf_proxy_compare_arms"),
        "stock_basket_arm_ids": [a.get("arm_id") for a in (menu_off.get("stock_basket_arms") or [])],
        "b6_strategy_wiring": menu_off.get("b6"),
        "bond_overlay": menu_off.get("bond_risk_parity_overlay"),
        "strategy_consume": {
            "S4_S6": "consume plan() weights + compare_arms_catalog() / satellite_menu()",
            "fields": [
                "etf_sleeve_weight",
                "core_etf_weight",
                "satellite_etf_weight",
                "contribution_weight_*",
                "residual_book_weight_cap",
                "residual_weight_to_hit_target_beta",
            ],
        },
        "catalog_arm_ids": [a.get("id") for a in (catalog.get("arms") or [])],
        "note": "Research compare arms — weights/flags/paths only; no fabricated performance",
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps({"ok": True, "wrote": str(OUT), "promotion_approved": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
