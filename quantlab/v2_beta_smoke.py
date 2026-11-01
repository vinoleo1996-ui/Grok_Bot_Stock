"""V2 Beta vol-target / β-budget / drawdown research smoke — weights + flags only.

No Sharpe, PnL, or fabricated performance. Forces::

  promotion_approved = False
  sw_l1_promotable   = False

Run::

    PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.v2_beta_smoke
"""
from __future__ import annotations

import json
import sys
from datetime import date


DEFAULT_MID_SESSION = date(2026, 6, 30)
DEFAULT_LATE_SESSION = date(2026, 10, 9)


def _gap_block(plan) -> dict:
    """Typed Mandate β-gap + drawdown + portfolio decomposition fields."""
    return {
        "target_beta": plan.target_beta_vs_benchmark,
        "unit_beta": plan.unit_beta,
        "implied_sleeve_beta": plan.implied_sleeve_beta,
        "beta_gap_to_mandate": plan.beta_gap_to_mandate,
        "residual_beta_budget_for_strategy": plan.residual_beta_budget_for_strategy,
        "implied_beta_in_band": plan.implied_beta_in_band,
        "max_etf_sleeve_weight": plan.max_etf_sleeve_weight,
        "max_etf_raised": False,
        "residual_beta_owner": "Strategy",
        "beta_gap_is_structural": plan.beta_gap_is_structural,
        "max_sleeve_beta_at_max_etf": plan.max_sleeve_beta_at_max_etf,
        "assumed_residual_unit_beta": plan.assumed_residual_unit_beta,
        "residual_weight_to_hit_target_beta": plan.residual_weight_to_hit_target_beta,
        "implied_portfolio_beta_at_residual_fill": plan.implied_portfolio_beta_at_residual_fill,
        "etf_drawdown": plan.etf_drawdown,
        "drawdown_tier": plan.drawdown_tier,
        "drawdown_scale_applied": plan.drawdown_scale_applied,
        "etf_weight_pre_drawdown": plan.etf_weight_pre_drawdown,
        "effective_target_annual_vol": plan.effective_target_annual_vol,
    }


def run_beta_smoke(
    mandate_path: str | None = None,
    d0_root: str | None = None,
    *,
    session: str | None = None,
    late_session: str | None = None,
) -> dict:
    from pathlib import Path

    from quantlab.beta import PrototypeBetaSleeveProvider, VolTargetBetaSleeveProvider
    from quantlab.data.v2_readers import default_v2_roots, load_etf_510300
    from quantlab.mandate_v2 import load_mandate_v2

    from quantlab.promotion_gate import gate_status

    mandate = load_mandate_v2(mandate_path)
    # Platform overall gate is Eng-owned; Beta plans themselves must stay False.
    platform_gate = gate_status()

    roots = default_v2_roots()
    if d0_root:
        from dataclasses import replace

        roots = replace(roots, d0_root=Path(d0_root))

    etf = load_etf_510300(roots=roots)
    if etf.promotion_approved:
        raise RuntimeError("smoke_fail:etf_promotion_must_be_false")

    mid = date.fromisoformat(session) if session else DEFAULT_MID_SESSION
    late = date.fromisoformat(late_session) if late_session else DEFAULT_LATE_SESSION

    provider = VolTargetBetaSleeveProvider(mandate, d0_root=roots.d0_root)
    _ = PrototypeBetaSleeveProvider

    per_session: dict[str, dict] = {}
    for sess in (mid, late) if late != mid else (mid,):
        plan = provider.plan(sess)
        if plan.promotion_approved:
            raise RuntimeError(f"smoke_fail:beta_promotion_approved_true:{sess}")
        if plan.etf_sleeve_weight is None:
            raise RuntimeError(f"smoke_fail:etf_weight_none:{sess}")
        if plan.etf_sleeve_weight > plan.max_etf_sleeve_weight + 1e-12:
            raise RuntimeError(f"smoke_fail:etf_weight_over_cap:{sess}")
        bars = provider.load_etf_bars(sess, sess)
        if len(bars) < 1:
            raise RuntimeError(f"smoke_fail:etf_510300_missing_bar_on_session:{sess}")

        # Gap contract must be populated on live plans
        if plan.unit_beta is None or plan.implied_sleeve_beta is None:
            raise RuntimeError(f"smoke_fail:gap_fields_missing:{sess}")
        if plan.beta_gap_to_mandate is None or plan.residual_beta_budget_for_strategy is None:
            raise RuntimeError(f"smoke_fail:beta_gap_missing:{sess}")
        if plan.implied_beta_in_band is None:
            raise RuntimeError(f"smoke_fail:implied_beta_in_band_missing:{sess}")
        # Consistency: gap = target - implied; residual budget = max(0, gap)
        expected_gap = plan.target_beta_vs_benchmark - plan.implied_sleeve_beta
        if abs(plan.beta_gap_to_mandate - expected_gap) > 1e-9:
            raise RuntimeError(f"smoke_fail:beta_gap_mismatch:{sess}")
        expected_budget = max(0.0, expected_gap)
        if abs(plan.residual_beta_budget_for_strategy - expected_budget) > 1e-9:
            raise RuntimeError(f"smoke_fail:residual_beta_budget_mismatch:{sess}")

        # Drawdown fields present
        if plan.drawdown_tier is None:
            raise RuntimeError(f"smoke_fail:drawdown_tier_missing:{sess}")
        if plan.etf_weight_pre_drawdown is None:
            raise RuntimeError(f"smoke_fail:etf_weight_pre_drawdown_missing:{sess}")
        if plan.etf_sleeve_weight > plan.etf_weight_pre_drawdown + 1e-12:
            raise RuntimeError(f"smoke_fail:drawdown_raised_etf_weight:{sess}")
        if plan.effective_target_annual_vol is None:
            raise RuntimeError(f"smoke_fail:effective_target_vol_missing:{sess}")

        # P2.1 structural gap contract
        if plan.beta_gap_is_structural is None or plan.max_sleeve_beta_at_max_etf is None:
            raise RuntimeError(f"smoke_fail:structural_gap_fields_missing:{sess}")
        if plan.max_sleeve_beta_at_max_etf + 1e-12 < plan.target_beta_vs_benchmark:
            if plan.beta_gap_is_structural is not True:
                raise RuntimeError(f"smoke_fail:structural_flag_false_when_ceiling_below_target:{sess}")
        if plan.residual_weight_to_hit_target_beta is None:
            raise RuntimeError(f"smoke_fail:residual_weight_to_hit_missing:{sess}")
        if plan.residual_weight_to_hit_target_beta > plan.residual_book_weight_cap + 1e-9:
            raise RuntimeError(f"smoke_fail:residual_weight_exceeds_cap:{sess}")
        if plan.implied_portfolio_beta_at_residual_fill is None:
            raise RuntimeError(f"smoke_fail:portfolio_beta_fill_missing:{sess}")
        # With assumed residual unit β=1, fill should land on target (within tol) when feasible
        if abs(float(plan.assumed_residual_unit_beta) - 1.0) < 1e-12:
            if abs(plan.implied_portfolio_beta_at_residual_fill - plan.target_beta_vs_benchmark) > 5e-3:
                raise RuntimeError(
                    f"smoke_fail:portfolio_fill_not_near_target:{sess}:"
                    f"{plan.implied_portfolio_beta_at_residual_fill}"
                )

        # Caller-supplied path: scale from explicit unit metrics
        plan_caller = provider.plan(sess, realized_vol=0.20, portfolio_beta=1.0)

        gap = _gap_block(plan)
        per_session[str(sess)] = {
            "session": str(sess),
            "etf_sleeve_weight": plan.etf_sleeve_weight,
            "cash_weight": plan.cash_weight,
            "residual_book_weight_cap": plan.residual_book_weight_cap,
            "max_etf_sleeve_weight": plan.max_etf_sleeve_weight,
            "target_annual_vol": plan.target_annual_vol,
            "target_beta_vs_benchmark": plan.target_beta_vs_benchmark,
            "target_beta_band": list(plan.target_beta_band),
            "index_bars_available": plan.index_bars_available,
            "etf_panel_available": plan.etf_panel_available,
            "bars_on_session": len(bars),
            "data_ready": plan.data_ready,
            "promotion_approved": False,
            "mandate_beta_gap": gap,
            "portfolio_beta_decomposition": {
                "sleeve_beta": plan.implied_sleeve_beta,
                "max_sleeve_beta_at_max_etf": plan.max_sleeve_beta_at_max_etf,
                "beta_gap_is_structural": plan.beta_gap_is_structural,
                "assumed_residual_unit_beta": plan.assumed_residual_unit_beta,
                "residual_weight_to_hit_target_beta": plan.residual_weight_to_hit_target_beta,
                "implied_portfolio_beta_at_residual_fill": plan.implied_portfolio_beta_at_residual_fill,
                "residual_book_weight_cap": plan.residual_book_weight_cap,
                "note": "fill residual at residual_weight_to_hit_target_beta (not full cap) to approach portfolio β 0.70",
            },
            "drawdown_scaler": {
                "etf_drawdown": plan.etf_drawdown,
                "drawdown_tier": plan.drawdown_tier,
                "drawdown_scale_applied": plan.drawdown_scale_applied,
                "etf_weight_pre_drawdown": plan.etf_weight_pre_drawdown,
                "etf_weight_post_drawdown": plan.etf_sleeve_weight,
                "weight_delta": round(
                    float(plan.etf_sleeve_weight) - float(plan.etf_weight_pre_drawdown), 6
                ),
                "effective_target_annual_vol": plan.effective_target_annual_vol,
            },
            "caller_override": {
                "realized_vol": 0.20,
                "portfolio_beta": 1.0,
                "etf_sleeve_weight": plan_caller.etf_sleeve_weight,
                "cash_weight": plan_caller.cash_weight,
                "residual_book_weight_cap": plan_caller.residual_book_weight_cap,
                "drawdown_tier": plan_caller.drawdown_tier,
                "implied_sleeve_beta": plan_caller.implied_sleeve_beta,
                "beta_gap_to_mandate": plan_caller.beta_gap_to_mandate,
                "residual_beta_budget_for_strategy": plan_caller.residual_beta_budget_for_strategy,
            },
            "todos_head": list(plan.todos[:22]),
        }

    # Late session (full-history DD ~0.24) should engage L3 and cut etf below pre-dd
    late_key = str(late)
    if late_key in per_session:
        late_dd = per_session[late_key]["drawdown_scaler"]
        if late_dd["etf_drawdown"] is not None and late_dd["etf_drawdown"] >= 0.22:
            if late_dd["drawdown_tier"] not in {"L3", "L4_extreme"}:
                raise RuntimeError(
                    f"smoke_fail:expected_L3_or_L4_on_late_dd:{late_dd['drawdown_tier']}"
                )
            if late_dd["etf_weight_post_drawdown"] > 0.30 + 1e-9:
                raise RuntimeError(
                    f"smoke_fail:L3_cap_not_applied:{late_dd['etf_weight_post_drawdown']}"
                )
            if late_dd["weight_delta"] >= 0:
                raise RuntimeError("smoke_fail:late_drawdown_did_not_reduce_etf")

    # Mid session DD ~0.14 → L1 (vol mult) may keep weight at max_etf bind
    mid_key = str(mid)
    if mid_key in per_session:
        mid_dd = per_session[mid_key]["drawdown_scaler"]
        if mid_dd["etf_drawdown"] is not None and mid_dd["etf_drawdown"] >= 0.12:
            if mid_dd["drawdown_tier"] == "none":
                raise RuntimeError("smoke_fail:expected_L1_plus_on_mid_dd")
            if mid_dd["effective_target_annual_vol"] > mandate.risk.target_annual_vol - 1e-12:
                # should be 0.75 * 0.16 = 0.12
                if abs(mid_dd["effective_target_annual_vol"] - mandate.risk.target_annual_vol * 0.75) > 1e-9:
                    raise RuntimeError(
                        f"smoke_fail:L1_vol_mult_missing:{mid_dd['effective_target_annual_vol']}"
                    )

    # --- smallcap_satellite research menu: OFF vs ON ---
    provider_off = VolTargetBetaSleeveProvider(mandate, d0_root=roots.d0_root, smallcap_satellite=False)
    provider_on = VolTargetBetaSleeveProvider(mandate, d0_root=roots.d0_root, smallcap_satellite=True)
    if provider_off.smallcap_satellite:
        raise RuntimeError("smoke_fail:smallcap_satellite_default_must_be_false")
    sat_compare: dict[str, dict] = {}
    for sess in (mid, late) if late != mid else (mid,):
        plan_off = provider_off.plan(sess)
        plan_on = provider_on.plan(sess)
        if plan_off.promotion_approved or plan_on.promotion_approved:
            raise RuntimeError(f"smoke_fail:satellite_promotion_leak:{sess}")
        if plan_off.smallcap_satellite:
            raise RuntimeError(f"smoke_fail:flag_off_but_plan_true:{sess}")
        if not plan_on.smallcap_satellite:
            raise RuntimeError(f"smoke_fail:flag_on_but_plan_false:{sess}")
        if plan_on.etf_sleeve_weight is not None and plan_on.etf_sleeve_weight > plan_on.max_etf_sleeve_weight + 1e-12:
            raise RuntimeError(f"smoke_fail:satellite_etf_over_max:{sess}")
        if plan_on.satellite_data_ready:
            if plan_on.core_etf_weight is None or plan_on.satellite_etf_weight is None:
                raise RuntimeError(f"smoke_fail:satellite_weights_missing:{sess}")
            combo = float(plan_on.core_etf_weight) + float(plan_on.satellite_etf_weight)
            if abs(combo - float(plan_on.etf_sleeve_weight)) > 1e-5:
                raise RuntimeError(f"smoke_fail:satellite_weights_sum:{sess}")
            if plan_on.contribution_weight_core is None or plan_on.contribution_weight_satellite is None:
                raise RuntimeError(f"smoke_fail:contribution_weights_missing:{sess}")
            if abs(plan_on.contribution_weight_core + plan_on.contribution_weight_satellite - 1.0) > 1e-5:
                raise RuntimeError(f"smoke_fail:contribution_weights_sum:{sess}")
            if plan_on.contribution_weight_satellite > provider_on.max_satellite_frac + 1e-9:
                raise RuntimeError(f"smoke_fail:satellite_frac_over_cap:{sess}")
        sat_compare[str(sess)] = {
            "off": {
                "smallcap_satellite": plan_off.smallcap_satellite,
                "etf_sleeve_weight": plan_off.etf_sleeve_weight,
                "core_etf_weight": plan_off.core_etf_weight,
                "satellite_etf_weight": plan_off.satellite_etf_weight,
                "contribution_weight_core": plan_off.contribution_weight_core,
                "contribution_weight_satellite": plan_off.contribution_weight_satellite,
                "implied_sleeve_beta": plan_off.implied_sleeve_beta,
                "promotion_approved": False,
            },
            "on": {
                "smallcap_satellite": plan_on.smallcap_satellite,
                "etf_sleeve_weight": plan_on.etf_sleeve_weight,
                "core_etf_weight": plan_on.core_etf_weight,
                "satellite_etf_weight": plan_on.satellite_etf_weight,
                "contribution_weight_core": plan_on.contribution_weight_core,
                "contribution_weight_satellite": plan_on.contribution_weight_satellite,
                "satellite_code": plan_on.satellite_code,
                "satellite_asset": plan_on.satellite_asset,
                "satellite_unit_beta": plan_on.satellite_unit_beta,
                "satellite_data_ready": plan_on.satellite_data_ready,
                "implied_sleeve_beta": plan_on.implied_sleeve_beta,
                "max_etf_sleeve_weight": plan_on.max_etf_sleeve_weight,
                "promotion_approved": False,
            },
        }
    menu_off = provider_off.satellite_menu(mid)
    menu_on = provider_on.satellite_menu(mid)
    if menu_off.get("promotion_approved") is not False or menu_on.get("promotion_approved") is not False:
        raise RuntimeError("smoke_fail:menu_promotion_not_false")
    # B1 polish: raise-CAGR candidates listed even when flag OFF
    for menu in (menu_off, menu_on):
        ids = {c.get("id") for c in (menu.get("raise_cagr_candidates") or [])}
        for need in ("etf_proxy_512100", "etf_proxy_510500", "wide_basket_50", "m2_smallcap_control"):
            if need not in ids:
                raise RuntimeError(f"smoke_fail:raise_cagr_menu_missing:{need}")
        proxy_codes = {a.get("code") for a in (menu.get("etf_proxy_compare_arms") or [])}
        if "sh512100" not in proxy_codes or "sh510500" not in proxy_codes:
            raise RuntimeError("smoke_fail:etf_proxy_compare_arms_incomplete")
        basket_ids = {a.get("arm_id") for a in (menu.get("stock_basket_arms") or [])}
        if "wide_basket_50" not in basket_ids or "m2_smallcap_control" not in basket_ids:
            raise RuntimeError("smoke_fail:stock_basket_arms_incomplete")
        if not menu.get("stock_basket_hooks"):
            raise RuntimeError("smoke_fail:stock_basket_hooks_missing")
        if menu.get("b6", {}).get("field") != "residual_weight_to_hit_target_beta":
            raise RuntimeError("smoke_fail:b6_wiring_missing")
        overlay = menu.get("bond_risk_parity_overlay") or {}
        if overlay.get("default") is not False:
            raise RuntimeError("smoke_fail:bond_overlay_default_not_false")
        if overlay.get("enabled") is not False and not provider_on.bond_risk_parity_overlay:
            pass  # off provider must be disabled
    if menu_off.get("bond_risk_parity_overlay", {}).get("enabled") is not False:
        raise RuntimeError("smoke_fail:overlay_enabled_while_satellite_off")
    # B6 still on live plan
    sample_plan = provider_off.plan(mid)
    if sample_plan.residual_weight_to_hit_target_beta is None:
        raise RuntimeError("smoke_fail:b6_field_missing_on_plan")
    if sample_plan.implied_portfolio_beta_at_residual_fill is None:
        raise RuntimeError("smoke_fail:b6_portfolio_fill_missing")
    # Side-by-side 510500 arm
    provider_500 = VolTargetBetaSleeveProvider(
        mandate, d0_root=roots.d0_root, smallcap_satellite=True, satellite_code="sh510500"
    )
    plan_500 = provider_500.plan(mid)
    if plan_500.satellite_code != "sh510500":
        raise RuntimeError(f"smoke_fail:510500_arm:{plan_500.satellite_code}")
    catalog = provider_off.compare_arms_catalog()
    if catalog.get("promotion_approved") is not False:
        raise RuntimeError("smoke_fail:catalog_promotion")
    if catalog.get("smallcap_satellite_default") is not False:
        raise RuntimeError("smoke_fail:catalog_satellite_default")

    # promotion must stay false on BetaSleevePlan construction
    try:
        from quantlab.beta.sleeve import BetaSleevePlan

        BetaSleevePlan(
            session=mid,
            benchmark_etf="510300",
            benchmark_etf_instrument_id="sh.510300",
            benchmark_index_id="sh.000300",
            target_annual_vol=0.16,
            target_beta_vs_benchmark=0.70,
            target_beta_band=(0.5, 0.85),
            max_etf_sleeve_weight=0.4,
            cash_weight=0.05,
            etf_sleeve_weight=0.25,
            residual_book_weight_cap=0.70,
            promotion_approved=True,
        )
        raise RuntimeError("smoke_fail:promotion_approved_true_did_not_raise")
    except ValueError as exc:
        if "beta_sleeve_promotion_approved_must_be_false" not in str(exc):
            raise

    handoff = provider.strategy_handoff_surface()
    if handoff.get("promotion_approved") is not False:
        raise RuntimeError("smoke_fail:handoff_promotion_not_false")
    if handoff.get("sw_l1_promotable") is not False:
        raise RuntimeError("smoke_fail:handoff_sw_l1_promotable_not_false")
    if handoff.get("max_etf_raised") is not False:
        raise RuntimeError("smoke_fail:handoff_max_etf_raised_not_false")
    if handoff.get("residual_beta_owner") != "Strategy":
        raise RuntimeError("smoke_fail:handoff_residual_beta_owner")
    if handoff.get("smallcap_satellite_default") is not False:
        raise RuntimeError("smoke_fail:handoff_satellite_default_not_false")
    for key in (
        "implied_sleeve_beta",
        "beta_gap_to_mandate",
        "residual_beta_budget_for_strategy",
        "implied_beta_in_band",
        "drawdown_tier",
        "etf_drawdown",
        "smallcap_satellite",
        "compare_arms",
    ):
        if key not in handoff:
            raise RuntimeError(f"smoke_fail:handoff_missing:{key}")

    status = {
        "ok": True,
        "phase": "0_beta_essence_b1_b6",
        "promotion_approved": False,
        "promotion_scope": "beta_sleeve_research_only",
        "platform_overall_gate_eng": platform_gate,
        "sw_l1_promotable": False,
        "provider": "VolTargetBetaSleeveProvider",
        "mandate_id": mandate.mandate_id,
        "mandate_version": mandate.version,
        "mandate_targets": {
            "target_annual_vol": mandate.risk.target_annual_vol,
            "target_beta_vs_benchmark": mandate.risk.target_beta_vs_benchmark,
            "vol_targeting_enabled": mandate.risk.vol_targeting_enabled,
            "max_etf_sleeve_weight": mandate.portfolio_limits.max_etf_sleeve_weight,
            "industry_neutral_residual_book": mandate.signal_construction.industry_neutral_residual_book,
            "industry_scheme": mandate.portfolio_limits.industry_scheme,
            "drawdown_scaler_recoverable": mandate.risk.drawdown_scaler_recoverable,
        },
        "etf_510300": {
            "n_bars": etf.n_bars,
            "date_range": [str(etf.date_min), str(etf.date_max)],
            "quality_status": etf.instrument.quality_status,
            "promotion_approved": False,
            "quality_gaps_head": list(etf.quality_gaps[:4]),
        },
        "by_session": per_session,
        "smallcap_satellite": {
            "default_off": True,
            "bond_risk_parity_overlay_default": False,
            "max_satellite_frac": provider_on.max_satellite_frac,
            "by_session": sat_compare,
            "menu_off_raise_cagr_ids": [c.get("id") for c in (menu_off.get("raise_cagr_candidates") or [])],
            "etf_proxy_compare_arms": menu_off.get("etf_proxy_compare_arms"),
            "stock_basket_arm_ids": [a.get("arm_id") for a in (menu_off.get("stock_basket_arms") or [])],
            "bond_overlay_off": menu_off.get("bond_risk_parity_overlay"),
            "b6": menu_off.get("b6"),
            "b6_plan_residual_weight": sample_plan.residual_weight_to_hit_target_beta,
            "b6_plan_portfolio_fill": sample_plan.implied_portfolio_beta_at_residual_fill,
            "arm_510500": {
                "satellite_code": plan_500.satellite_code,
                "satellite_etf_weight": plan_500.satellite_etf_weight,
                "contribution_weight_satellite": plan_500.contribution_weight_satellite,
            },
            "catalog_arm_ids": [a.get("id") for a in (catalog.get("arms") or [])],
            "menu_off": {k: menu_off[k] for k in ("smallcap_satellite", "compare_arms", "promotion_approved", "config_path") if k in menu_off},
            "doc": "docs/v2/BETA_SMALLCAP_SATELLITE.md",
            "config": "quantlab/beta/configs/compare_arms_v1.json",
            "promotion_approved": False,
        },
        "strategy_handoff_surface": handoff,
        "note": (
            "Beta research smoke — Mandate vol16%/β0.70 + drawdown risk-off, "
            "β-gap contract for Strategy; counts/flags only; no Sharpe/PnL; "
            "SW_L1 research-only; promotion_approved=false; max_etf not raised"
        ),
    }
    return status


def main(argv: list[str] | None = None) -> int:
    import argparse

    p = argparse.ArgumentParser(prog="quantlab.v2_beta_smoke")
    p.add_argument("--mandate", default=None)
    p.add_argument("--d0-root", default=None)
    p.add_argument("--session", default=None)
    p.add_argument("--late-session", default=None)
    args = p.parse_args(argv)
    try:
        status = run_beta_smoke(
            mandate_path=args.mandate,
            d0_root=args.d0_root,
            session=args.session,
            late_session=args.late_session,
        )
    except Exception as exc:  # noqa: BLE001
        print(
            json.dumps({"ok": False, "error": f"{type(exc).__name__}:{exc}"}, ensure_ascii=False, indent=2)
        )
        return 1
    print(json.dumps(status, ensure_ascii=False, indent=2, default=str))
    return 0 if status.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
