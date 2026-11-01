"""V2 Strategy research paper-loop smoke — Mandate → funnel stub → Beta plan → constructor.

Research-only::

  promotion_approved = false
  no live trading / no promotion gate flip

Prefer live ``VolTargetBetaSleeveProvider.plan()`` when 510300 data loads;
fall back to ``StubBetaSleeveProvider`` (synth / idle caps) on failure.
Pass ``plan.residual_book_weight_cap`` into
``PortfolioConstructorV2.construct(book_weight_cap=...)``.

Run::

    PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.v2_strategy_smoke
    PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli v2-strategy-smoke

Uses idle / stub Alpha scores so the constructor path is exercised without
requiring full D1 panel IO. S1: synthetic returns exercise LW+target_vol;
no-panel path stays equal stub. promotion_approved=false. Optional ``--use-d1`` attempts a light D1 membership
probe and falls back to synthetic universe on failure.
"""
from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path


DEFAULT_SESSION = date(2026, 6, 30)


def _synthetic_scores(n: int = 40) -> dict[str, float]:
    """Deterministic idle Alpha scores for smoke (not a real factor)."""
    out: dict[str, float] = {}
    for i in range(n):
        # Alternate SSE/SZSE-looking ids; values decline with rank
        prefix = "sh" if i % 2 == 0 else "sz"
        code = f"{600000 + i:06d}" if prefix == "sh" else f"{1 + i:06d}"
        out[f"{prefix}.{code}"] = float(n - i)
    return out


def _synthetic_industries(ids: list[str]) -> dict[str, str]:
    labels = ("SW1", "SW2", "SW3", "SW4", "UNKNOWN")
    return {iid: labels[i % len(labels)] for i, iid in enumerate(ids)}


def _todo_flag(todos: tuple[str, ...] | list[str], prefix: str) -> str | None:
    """Return value after ``prefix=`` from a plan.todos entry, if present."""
    needle = prefix if prefix.endswith("=") else f"{prefix}="
    for t in todos:
        if t.startswith(needle):
            return t[len(needle) :]
    return None


def _parse_bool_flag(raw: str | None) -> bool | None:
    if raw is None:
        return None
    s = raw.strip().lower()
    if s in ("true", "1", "yes"):
        return True
    if s in ("false", "0", "no"):
        return False
    return None


def _parse_float_flag(raw: str | None) -> float | None:
    if raw is None:
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def _plan_beta_block(plan, *, provider_name: str, live: bool, fallback_error: str | None = None) -> dict:
    """Record etf/cash/residual_cap + Mandate-band flag (research only)."""
    todos = list(plan.todos or ())
    implied_beta = _parse_float_flag(_todo_flag(todos, "implied_sleeve_beta"))
    in_band = _parse_bool_flag(_todo_flag(todos, "implied_beta_in_band"))
    # When live plan has weights but no flag (should not happen), derive band check
    if live and in_band is None and plan.etf_sleeve_weight is not None:
        unit = _parse_float_flag(_todo_flag(todos, "unit_beta"))
        if unit is not None:
            implied_beta = float(plan.etf_sleeve_weight) * unit
            lo, hi = plan.target_beta_band
            in_band = lo - 1e-12 <= implied_beta <= hi + 1e-12

    block: dict = {
        "provider": provider_name,
        "live_vol_target": live,
        "etf_sleeve_weight": plan.etf_sleeve_weight,
        "cash_weight": plan.cash_weight,
        "residual_book_weight_cap": plan.residual_book_weight_cap,
        "max_etf_sleeve_weight": plan.max_etf_sleeve_weight,
        "target_annual_vol": plan.target_annual_vol,
        "target_beta": plan.target_beta_vs_benchmark,
        "target_beta_band": list(plan.target_beta_band),
        "implied_sleeve_beta": implied_beta,
        "implied_beta_in_band": in_band,
        "mandate_tension_flag": (
            in_band is False
        ),  # True when clipped sleeve β sits outside Mandate band (flag only)
        "index_bars_available": plan.index_bars_available,
        "etf_panel_available": plan.etf_panel_available,
        "data_ready": plan.data_ready,
        "vol_target_applied": live,
        "promotion_approved": False,
        "sw_l1_promotable": False,
        "residual_beta_owner": "Strategy",
        "note": (
            "Strategy consumes residual_book_weight_cap; owns residual β vs Mandate band. "
            "max_etf not raised; promotion_approved=false."
            if live
            else "vol/beta live plan unavailable — StubBetaSleeveProvider idle caps (synth fallback)"
        ),
        "todos_head": todos[:8],
    }
    if fallback_error:
        block["fallback_error"] = fallback_error
    return block


def _resolve_beta_plan(mandate, d0_root: str | None, sess: date):
    """Prefer live VolTarget plan; fall back to Stub on data/load failure."""
    from quantlab.beta import StubBetaSleeveProvider, VolTargetBetaSleeveProvider

    try:
        live = VolTargetBetaSleeveProvider(mandate, d0_root=d0_root)
        plan = live.plan(sess)
        if plan.promotion_approved:
            raise RuntimeError("smoke_fail:beta_promotion_approved_must_be_false")
        if plan.residual_book_weight_cap is None:
            raise RuntimeError("smoke_fail:live_beta_missing_residual_book_weight_cap")
        handoff = live.strategy_handoff_surface()
        return plan, _plan_beta_block(plan, provider_name="VolTargetBetaSleeveProvider", live=True), handoff
    except Exception as exc:  # noqa: BLE001 — smoke reports, does not invent
        stub = StubBetaSleeveProvider(mandate, d0_root=d0_root)
        plan = stub.plan(sess)
        if plan.promotion_approved:
            raise RuntimeError("smoke_fail:beta_promotion_approved_must_be_false")
        block = _plan_beta_block(
            plan,
            provider_name="StubBetaSleeveProvider",
            live=False,
            fallback_error=f"{type(exc).__name__}:{exc}",
        )
        return plan, block, None


def run_strategy_smoke(
    mandate_path: str | None = None,
    d0_root: str | None = None,
    *,
    session: str | None = None,
    use_d1: bool = False,
    n_synth: int = 40,
) -> dict:
    from quantlab.factors.residual_factory import StubResidualAlphaFactorFactory
    from quantlab.mandate_v2 import load_mandate_v2
    from quantlab.portfolio import PortfolioConstructorV2, RebalanceScheduleV2
    from quantlab.universe import StubUniverseMaskProvider

    mandate = load_mandate_v2(mandate_path)
    if mandate.promotion_approved:
        raise RuntimeError("smoke_fail:promotion_approved_must_be_false")
    mandate.require_not_promoted()

    sess = date.fromisoformat(session) if session else DEFAULT_SESSION

    # --- D1 funnel (idle / stub unless --use-d1) ---
    d1_block: dict = {
        "mode": "idle_stub",
        "member_count": 0,
        "promotion_approved": False,
        "notes": ["d1_skipped_use_synth_universe"],
    }
    universe_ids: list[str] = []
    if use_d1:
        try:
            from quantlab.universe.d1_masks import D1MaskConfig, build_d1_masks_for_session

            root = Path(d0_root) if d0_root else None
            kwargs = {}
            if root is not None:
                kwargs["d0_root"] = root
            result = build_d1_masks_for_session(
                sess,
                config=D1MaskConfig(),
                max_instruments=min(80, max(n_synth, 40)),
                **kwargs,
            )
            if result.promotion_approved:
                raise RuntimeError("smoke_fail:d1_promotion_approved_must_be_false")
            universe_ids = list(result.member_ids)
            d1_block = {
                "mode": "d1_masks",
                "member_count": len(universe_ids),
                "n_instruments_in": result.n_instruments_in,
                "n_after_mktcap": result.n_after_mktcap,
                "float_mktcap_source": result.float_mktcap_source,
                "promotion_approved": False,
                "sw_l1_promotable": False,
                "notes_head": list(result.notes[:6]),
            }
        except Exception as exc:  # noqa: BLE001 — smoke reports, does not invent
            d1_block = {
                "mode": "d1_failed_fallback_synth",
                "error": f"{type(exc).__name__}:{exc}",
                "promotion_approved": False,
                "notes": ["fallback_to_synthetic_scores"],
            }

    # Eng L0 stub membership probe (always; calendar-aware when D0 present)
    uni = StubUniverseMaskProvider(mandate, d0_root=d0_root)
    membership = uni.membership_at(sess)

    # --- Beta: prefer live vol/β plan → residual_book_weight_cap ---
    plan, beta_block, handoff = _resolve_beta_plan(mandate, d0_root, sess)
    if plan.promotion_approved:
        raise RuntimeError("smoke_fail:beta_promotion_approved_must_be_false")

    # --- idle / stub factors ---
    factory = StubResidualAlphaFactorFactory(mandate)
    raw = factory.compute_raw(sess, factory.list_member_ids()[0], universe=())
    residual = factory.neutralize(raw, sw_l1=())
    composite = factory.integrate([residual])
    if composite.promotion_approved:
        raise RuntimeError("smoke_fail:composite_promotion_approved_must_be_false")

    # --- synthetic integrate scores for constructor path ---
    scores = _synthetic_scores(n_synth)
    if universe_ids:
        # Prefer real membership ids when D1 returned some; pad scores if needed
        scores = {iid: float(len(universe_ids) - i) for i, iid in enumerate(universe_ids[:n_synth])}
    industries = _synthetic_industries(list(scores.keys()))

    ctor = PortfolioConstructorV2(mandate)
    # Prior weights: half overlap to exercise turnover clip
    ranked = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)
    prior_n = min(len(ranked), mandate.portfolio_limits.min_positions_target)
    prior = {k: 1.0 / prior_n for k in ranked[5 : 5 + prior_n]} if prior_n else {}
    book_cap = plan.residual_book_weight_cap  # live: float; stub idle: None

    constructed = ctor.construct(
        scores,
        session=sess,
        industry_labels=industries,
        prior_weights=prior or None,
        universe=list(scores.keys()),
        book_weight_cap=book_cap,
    )
    if constructed.promotion_approved:
        raise RuntimeError("smoke_fail:constructor_promotion_approved_must_be_false")

    # --- rebalance hooks ---
    schedule = RebalanceScheduleV2(mandate)
    decision = schedule.is_ordinary_rebalance_session(
        sess,
        last_rebalance=sess - timedelta(days=3),
    )
    daily = schedule.daily_mask_risk_scale_hook(sess)
    go_live_refused = False
    try:
        schedule.refuse_go_live()
    except RuntimeError:
        go_live_refused = True

    # S1: LW path works with returns_panel; without panel construct stays stub
    import numpy as np
    import pandas as pd

    rng = np.random.default_rng(42)
    ids_lw = list(scores.keys())
    # 80 sessions × n names — enough for LedoitWolf / target_vol_weights
    rets = pd.DataFrame(
        rng.normal(0.0, 0.015, size=(80, len(ids_lw))),
        columns=ids_lw,
    )
    lw_constructed = ctor.construct(
        scores,
        session=sess,
        industry_labels=industries,
        universe=list(scores.keys()),
        book_weight_cap=book_cap,
        returns_panel=rets,
        weighting_mode="auto",
    )
    if lw_constructed.promotion_approved:
        raise RuntimeError("smoke_fail:lw_constructor_promotion_approved_must_be_false")
    lw_direct_ok = False
    lw_direct_err = None
    try:
        w_direct = ctor.optimize_ledoit_wolf(
            scores,
            returns_panel=rets,
            industry_labels=industries,
            session=sess,
            book_weight_cap=book_cap,
        )
        lw_direct_ok = bool(w_direct) and lw_constructed.method == "lw_target_vol"
    except Exception as exc:  # noqa: BLE001
        lw_direct_err = f"{type(exc).__name__}:{exc}"

    # No panel → stub method (equal / proportional)
    stub_ok = constructed.method in (
        "score_rank_equal_stub",
        "score_proportional_stub",
        "empty_scores_stub",
    )

    weight_sum = sum(constructed.weights.values())
    max_w = max(constructed.weights.values()) if constructed.weights else 0.0

    status = {
        "ok": True,
        "phase": "strategy_portfolio_beta_handoff",
        "promotion_approved": False,
        "mandate_id": mandate.mandate_id,
        "mandate_version": mandate.version,
        "mandate_path": mandate.source_path,
        "session": str(sess),
        "knobs": dict(ctor.knobs()),
        "universe_stub": {
            "calendar_ok": membership.calendar_ok,
            "member_count": len(membership.member_ids),
            "data_ready": membership.data_ready,
            "promotion_approved": membership.promotion_approved,
        },
        "d1": d1_block,
        "beta": beta_block,
        "beta_handoff_surface": dict(handoff) if handoff else None,
        "factors": {
            "factory": "StubResidualAlphaFactorFactory",
            "member_ids": list(factory.list_member_ids()),
            "composite_mode": composite.mode,
            "composite_n_scores": len(composite.scores),
            "data_ready": composite.data_ready,
            "promotion_approved": False,
        },
        "portfolio": {
            "method": constructed.method,
            "n_names": constructed.n_names,
            "weight_sum": weight_sum,
            "book_weight_cap_applied": book_cap,
            "max_single_weight": max_w,
            "single_name_cap": constructed.single_name_cap,
            "industry_cap": constructed.industry_cap,
            "turnover_one_way": constructed.turnover_one_way,
            "turnover_budget_applied": constructed.turnover_budget_applied,
            "turnover_clipped": constructed.turnover_clipped,
            "research_stub": constructed.research_stub,
            "promotion_approved": False,
            "stub_method": constructed.method,
            "stub_path_ok": stub_ok,
            "lw_method": lw_constructed.method,
            "lw_n_names": lw_constructed.n_names,
            "lw_weight_sum": float(sum(lw_constructed.weights.values())),
            "lw_path_ok": lw_constructed.method == "lw_target_vol",
            "lw_direct_ok": lw_direct_ok,
            "lw_direct_err": lw_direct_err,
            "sample_weights": dict(list(constructed.weights.items())[:5]),
            "notes_head": list(constructed.notes[:8]),
            "lw_notes_head": list(lw_constructed.notes[:10]),
        },
        "rebalance": {
            "cadence": decision.cadence,
            "ordinary_rebalance_due": decision.ordinary_rebalance_due,
            "days_since_last": decision.days_since_last,
            "min_sessions_between": decision.min_sessions_between,
            "daily_mask_refresh": daily.mask_refresh,
            "daily_risk_scale_applied": daily.risk_scale_applied,
            "vol_target_owner": daily.vol_target_owner,
            "go_live_refused": go_live_refused,
            "promotion_approved": False,
            "contract": dict(schedule.describe_contract()),
        },
        "note": (
            "Strategy research paper loop — consumes Beta residual_book_weight_cap; "
            "owns residual β vs Mandate band; no backtest metrics; no promotion"
        ),
    }

    # Structural assertions → ok flag
    if mandate.promotion_approved or constructed.promotion_approved or daily.risk_scale_applied:
        status["ok"] = False
        status["error"] = "promotion_or_live_scale_leaked"
    if plan.promotion_approved or beta_block.get("promotion_approved") is not False:
        status["ok"] = False
        status["error"] = "beta_promotion_leaked"
    if not stub_ok:
        status["ok"] = False
        status["error"] = f"expected_stub_without_returns_panel:{constructed.method}"
    if lw_constructed.method != "lw_target_vol":
        status["ok"] = False
        status["error"] = f"expected_lw_target_vol_with_returns:{lw_constructed.method}"
    if not lw_direct_ok:
        status["ok"] = False
        status["error"] = f"optimize_ledoit_wolf_failed:{lw_direct_err}"
    if not go_live_refused:
        status["ok"] = False
        status["error"] = "expected go-live refuse"
    if constructed.n_names == 0:
        status["ok"] = False
        status["error"] = "constructor_produced_empty_weights"
    if constructed.weights and max_w > constructed.single_name_cap + 1e-6:
        status["ok"] = False
        status["error"] = f"single_name_cap_breached:{max_w}"
    # When live Beta supplies a residual cap, weights must respect it
    if book_cap is not None and weight_sum > float(book_cap) + 1e-6:
        status["ok"] = False
        status["error"] = f"book_weight_cap_breached:{weight_sum}>{book_cap}"
    return status


def main(argv: list[str] | None = None) -> int:
    import argparse

    p = argparse.ArgumentParser(prog="quantlab.v2_strategy_smoke")
    p.add_argument("--mandate", default=None, help="Path to QuantLab-MANDATE_V2.json")
    p.add_argument("--d0-root", default=None, help="D0 snapshot root")
    p.add_argument("--session", default=None, help="Decision session YYYY-MM-DD")
    p.add_argument(
        "--use-d1",
        action="store_true",
        help="Attempt D1 mask membership (falls back to synth on failure)",
    )
    p.add_argument("--n-synth", type=int, default=40, help="Synthetic score count")
    args = p.parse_args(argv)
    try:
        status = run_strategy_smoke(
            mandate_path=args.mandate,
            d0_root=args.d0_root,
            session=args.session,
            use_d1=args.use_d1,
            n_synth=args.n_synth,
        )
    except Exception as exc:  # noqa: BLE001
        print(
            json.dumps(
                {"ok": False, "error": f"{type(exc).__name__}:{exc}", "promotion_approved": False},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1
    print(json.dumps(status, ensure_ascii=False, indent=2, default=str))
    return 0 if status.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
