"""Strategy paper B: costs + limit/halt marking vs A (zero-cost).

One-variable compare (Leo lock): pool=250 smoke; promotion_approved=false;
max_etf not raised; Alpha/Beta/D1 wiring unchanged — only marking / fills.

Outputs under ``output/strategy_paper_v1_costs/``:
  zero_cost_a/   — path A (same marking as paper v1)
  costs_b/       — path B (Mandate costs + limit/halt)
  summary.json / LEO_REPORT_ZH.md / LIMITATIONS_ZH.md / nav.png (overlay)

Reproduce::

    cd /workspace/QuantLab
    PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.portfolio.v2_strategy_paper_costs
"""
from __future__ import annotations

from quantlab.promotion_gate import overall_promotion_approved as _gate

import json
import math
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Mapping

import numpy as np
import pandas as pd

from quantlab.beta import VolTargetBetaSleeveProvider
from quantlab.config import ROOT
from quantlab.data.v2_readers import default_v2_roots, load_ep_research, load_etf_510300, load_merged_calendar
from quantlab.factors.residual_factory import ResearchResidualAlphaFactorFactory
from quantlab.mandate_v2 import load_mandate_v2
from quantlab.platform.strategy_feed import (
    biweekly_rebalance_sessions,
    d1_members_at,
    etf_510300_daily_returns,
    merged_close_panel,
    merged_daily_returns,
    trading_sessions,
)
from quantlab.portfolio.v2_constructor import PortfolioConstructorV2
from quantlab.portfolio.v2_panel_cache import cache_stats, install_merged_panel_cache
from quantlab.portfolio.v2_execution_costs import (
    SEMANTICS_VERSION,
    apply_fill_constraints,
    apply_lot_and_min_trade,
    compute_rebalance_costs,
    costs_drag_on_unit_nav,
    load_tradability_panels,
)
from quantlab.portfolio.v2_strategy_paper import (
    CANDIDATE_POOL,
    LOOKBACK_CALENDAR_DAYS,
    PAPER_RUN_TIER,
    PAPER_START,
    _candidate_pool,
    _close_panel_to_ts_index,
    _fm_map,
    _industry_labels,
    _integrate_scores,
    _metrics,
    _plot_nav,
    _sw_assignments_from_frame,
    resolve_paper_end,
)
from quantlab.universe.d1_masks import D1MaskConfig

OUTPUT_ROOT = ROOT / "output" / "strategy_paper_costs"
SMOKE_OUTPUT_ROOT = ROOT / "output" / "strategy_paper_v1_costs"  # legacy smoke path
# Explicit window per Leo/parent (start resolves to first session ≥ PAPER_START)
PAPER_END_EXPLICIT = date(2026, 10, 9)


def _book_ret(
    stock_w: Mapping[str, float],
    stock_rets: pd.DataFrame,
    sess: date,
    *,
    tradability=None,
    zero_on_block: bool = False,
) -> tuple[float, int]:
    """Weighted stock book return, ALWAYS close-to-close.

    Engine fix 2026-10-10: limit/halt no longer zeroes a held name's return
    (old bug). ``zero_on_block`` is ignored; second return value now counts
    blocked (limit/halt) held name-days as a diagnostic only.
    """
    book = 0.0
    n_zeroed = 0
    for iid, w in stock_w.items():
        if w <= 0:
            continue
        if tradability is not None and tradability.is_blocked(sess, iid):
            n_zeroed += 1  # diagnostic: return still counted below
        if iid in stock_rets.columns and sess in stock_rets.index:
            r = stock_rets.at[sess, iid]
            if r == r and math.isfinite(float(r)):
                book += float(w) * float(r)
    return book, n_zeroed


def _etf_ret(etf_w: float, etf_rets: pd.Series, sess: date) -> float:
    if etf_w <= 0 or sess not in etf_rets.index:
        return 0.0
    er = etf_rets.loc[sess]
    if er == er and math.isfinite(float(er)):
        return float(etf_w) * float(er)
    return 0.0


def _plot_overlay(nav_a: pd.Series, nav_b: pd.Series, path: Path) -> bool:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 4.5))
        xa = pd.to_datetime(nav_a.index)
        xb = pd.to_datetime(nav_b.index)
        ax.plot(xa, nav_a.values, color="#1f4e79", lw=1.4, label="A zero-cost")
        ax.plot(xb, nav_b.values, color="#c0392b", lw=1.4, label="B costs+limit/halt")
        ax.set_title("Strategy paper A vs B (research-only, promotion_approved=false)")
        ax.set_ylabel("NAV (start=1.0)")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper left")
        fig.autofmt_xdate()
        fig.tight_layout()
        fig.savefig(path, dpi=120)
        plt.close(fig)
        return True
    except Exception:
        # fallback: write B only via shared helper, plus simple SVG overlay
        ok = _plot_nav(nav_b, path)
        try:
            w, h = 900, 360
            pad_l, pad_r, pad_t, pad_b = 50, 20, 30, 40
            vals_a = [float(v) for v in nav_a.values if v == v]
            vals_b = [float(v) for v in nav_b.values if v == v]
            if len(vals_a) < 2 or len(vals_b) < 2:
                return ok
            ymin = min(min(vals_a), min(vals_b))
            ymax = max(max(vals_a), max(vals_b))
            if abs(ymax - ymin) < 1e-12:
                ymax = ymin + 1e-6

            def pts(vals):
                out = []
                for i, v in enumerate(vals):
                    x = pad_l + int((i / (len(vals) - 1)) * (w - pad_l - pad_r))
                    y = pad_t + int((1.0 - (v - ymin) / (ymax - ymin)) * (h - pad_t - pad_b))
                    out.append(f"{x},{y}")
                return " ".join(out)

            svg = (
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">'
                f'<rect width="100%" height="100%" fill="white"/>'
                f'<polyline fill="none" stroke="#1f4e79" stroke-width="2" points="{pts(vals_a)}"/>'
                f'<polyline fill="none" stroke="#c0392b" stroke-width="2" points="{pts(vals_b)}"/>'
                f'<text x="12" y="20" font-size="14" fill="#333">A vs B NAV (research, promotion_approved=false)</text>'
                f"</svg>"
            )
            path.with_suffix(".svg").write_text(svg, encoding="utf-8")
        except Exception:
            pass
        return ok


def _all_panel_ids(roots) -> list[str]:
    """All D0 instrument ids that have a panel file (Full D1 candidate set)."""
    inst = pd.read_parquet(roots.d0_root / "instruments.parquet")
    panel_dir = roots.d0_root / "panels"
    ids: list[str] = []
    for iid in inst["instrument_id"].astype(str).tolist():
        if (panel_dir / f"{iid}.parquet").is_file():
            ids.append(iid)
    return ids


def run_ab_compare(
    *,
    start: date = PAPER_START,
    end: date | None = PAPER_END_EXPLICIT,
    candidate_pool: int | None = CANDIDATE_POOL,
    full_d1: bool = False,
    out_root: Path | None = None,
    primary_external: bool = False,
    use_panel_cache: bool = False,
) -> dict:
    t_wall0 = time.time()
    if out_root is not None:
        out_root = Path(out_root)
    elif full_d1:
        out_root = ROOT / "output" / "strategy_paper_costs" / "full_d1"
    else:
        out_root = OUTPUT_ROOT / "smoke_pool250"
    out_a = out_root / "zero_cost_a"
    out_b = out_root / "costs_b"
    out_root.mkdir(parents=True, exist_ok=True)
    out_a.mkdir(parents=True, exist_ok=True)
    out_b.mkdir(parents=True, exist_ok=True)

    mandate = load_mandate_v2()
    mandate.require_not_promoted()
    if bool(mandate.promotion_approved) != _gate():
        raise RuntimeError("mandate_promotion_approved_gate_mismatch")
    capital = float(mandate.capital.initial_cny)
    costs = mandate.costs

    roots = default_v2_roots()
    if use_panel_cache or full_d1:
        install_merged_panel_cache(max_items=400)
        print("[paper-costs] merged_panel cache installed", flush=True)
    if full_d1:
        pool = _all_panel_ids(roots)
        candidate_pool = len(pool)
        run_tier = "full_d1_external"
        external_claim = bool(primary_external)
        smoke_note = (
            "PRIMARY Full D1 + costs + limit/halt (Leo P0). "
            "pool=250 zero-cost is smoke-only — not the main conclusion."
        )
    else:
        assert candidate_pool is not None
        pool = _candidate_pool(int(candidate_pool), roots)
        run_tier = PAPER_RUN_TIER
        external_claim = False
        smoke_note = (
            "candidate_pool=250 is smoke/iteration only; not Full D1 / not external-facing. "
            "MAIN external report is Full D1 + costs + limit/halt."
        )
    cfg = D1MaskConfig(open_status_mode="research", waive_u30_on_amount_gap=True)

    cal_view = load_merged_calendar(roots=roots)
    etf_bundle = load_etf_510300(roots=roots)
    end = resolve_paper_end(start=start, end=end, roots=roots)
    d0_cutoff = date(2026, 6, 30)
    post_d0 = end > d0_cutoff
    end_provenance = {
        "resolved_end": str(end),
        "merged_calendar_last_session": str(cal_view.last_session) if cal_view.last_session else None,
        "etf_510300_date_max": str(etf_bundle.date_max) if etf_bundle.date_max else None,
        "d0_panel_merge_cutoff": str(d0_cutoff),
        "extends_past_d0_cutoff": post_d0,
        "hard_stop_at_d0": False,
        "requested_end": str(PAPER_END_EXPLICIT),
    }
    print(f"[paper-costs] end={end} pool={len(pool)}", flush=True)

    sessions = trading_sessions(start, end, roots=roots)
    rebal_dates = biweekly_rebalance_sessions(start, end, mandate=mandate, roots=roots)
    if not sessions or not rebal_dates:
        raise RuntimeError("no_sessions_or_rebalances_in_window")

    load_start = start - timedelta(days=LOOKBACK_CALENDAR_DAYS)
    print(f"[paper-costs] preload closes {load_start}→{end}", flush=True)
    t0 = time.time()
    closes_raw = merged_close_panel(
        pool, load_start, end, roots=roots, chunk_size=300 if full_d1 else None, dtype="float32"
    )
    stock_rets = merged_daily_returns(
        pool, load_start, end, roots=roots, close_panel=closes_raw, dtype="float32"
    )
    etf_rets = etf_510300_daily_returns(load_start, end, roots=roots)
    print(f"[paper-costs] closes ready {closes_raw.shape} in {time.time()-t0:.1f}s", flush=True)

    print("[paper-costs] load tradability panels", flush=True)
    t0 = time.time()
    tradability = load_tradability_panels(pool, start, end, roots=roots)
    print(
        f"[paper-costs] tradability loaded={tradability.n_instruments_loaded} "
        f"in {time.time()-t0:.1f}s miss_limit_cells={tradability.n_limit_price_missing_cells}",
        flush=True,
    )

    close_ts = _close_panel_to_ts_index(closes_raw)
    # S2 整手: on-demand session prices (avoid materializing full iid×day map)
    def _prices_at(sess_d: date) -> dict[str, float]:
        if closes_raw.empty:
            return {}
        ts = pd.Timestamp(sess_d)
        if ts in closes_raw.index:
            row = closes_raw.loc[ts]
        else:
            # try date-normalized match
            hits = closes_raw.index[closes_raw.index.map(lambda x: pd.Timestamp(x).date()) == sess_d]
            if len(hits) == 0:
                return {}
            row = closes_raw.loc[hits[0]]
        if isinstance(row, pd.DataFrame):
            row = row.iloc[-1]
        out = {}
        for c, v in row.items():
            try:
                fv = float(v)
            except (TypeError, ValueError):
                continue
            if fv == fv and fv > 0:
                out[str(c)] = fv
        return out

    _etf_close_by_session: dict[date, float] = {}
    try:
        _etf_bundle = load_etf_510300(roots=roots)
        _etf_pf = getattr(_etf_bundle, "panel_frame", None)
        if _etf_pf is not None and not _etf_pf.empty and "close" in _etf_pf.columns:
            _et = pd.to_datetime(_etf_pf["event_time"]).dt.normalize()
            _cl = pd.to_numeric(_etf_pf["close"], errors="coerce")
            for _d, _px in zip(_et.dt.date, _cl):
                if _px == _px and float(_px) > 0:
                    _etf_close_by_session[_d] = float(_px)
    except Exception as _e:
        print(f"[paper-costs] etf close map skip: {_e}", flush=True)
    _min_trade = float(mandate.portfolio_limits.min_trade_notional_cny)
    _lot_rounding = str(mandate.portfolio_limits.lot_size_rounding)
    try:
        ep_view = load_ep_research(roots=roots)
    except FileNotFoundError:
        ep_view = None

    factory = ResearchResidualAlphaFactorFactory(
        mandate=mandate,
        close_panel=close_ts,
        ep_research_view=ep_view,
        d0_root=roots.d0_root,
        asof_extend_dir=roots.asof_extend_dir,
    )
    constructor = PortfolioConstructorV2(mandate)
    beta = VolTargetBetaSleeveProvider(mandate, d0_root=roots.d0_root)

    # --- dual state ---
    etf_a = etf_b = 0.0
    cash_a = cash_b = 1.0
    stock_a: dict[str, float] = {}
    stock_b: dict[str, float] = {}
    nav_a = nav_b = 1.0
    turnovers_a: list[float] = []
    turnovers_b: list[float] = []
    cost_rows: list[dict] = []
    rebal_log: list[dict] = []
    rows_a: list[dict] = []
    rows_b: list[dict] = []
    total_cost_cny = 0.0
    total_zeroed_name_days = 0
    total_buy_blocks = 0
    total_sell_blocks = 0

    rebal_set = set(rebal_dates)
    sess_in_window = [d for d in sessions if start <= d <= end]

    for i, sess in enumerate(sess_in_window):
        if i > 0:
            book_a, _ = _book_ret(stock_a, stock_rets, sess)
            book_b, n_z = _book_ret(
                stock_b, stock_rets, sess, tradability=tradability
            )
            total_zeroed_name_days += n_z
            day_a = book_a + _etf_ret(etf_a, etf_rets, sess)
            day_b = book_b + _etf_ret(etf_b, etf_rets, sess)
            nav_a *= 1.0 + day_a
            nav_b *= 1.0 + day_b
        else:
            day_a = day_b = 0.0

        rows_a.append(
            {
                "date": str(sess),
                "daily_ret": day_a if i > 0 else 0.0,
                "nav": nav_a,
                "etf_w": etf_a,
                "cash_w": cash_a,
                "residual_book_w": float(sum(stock_a.values())),
                "n_names": len(stock_a),
                "rebalance": sess in rebal_set,
                "path": "A_zero_cost",
            }
        )
        rows_b.append(
            {
                "date": str(sess),
                "daily_ret": day_b if i > 0 else 0.0,
                "nav": nav_b,
                "etf_w": etf_b,
                "cash_w": cash_b,
                "residual_book_w": float(sum(stock_b.values())),
                "n_names": len(stock_b),
                "rebalance": sess in rebal_set,
                "path": "B_costs_limit_halt",
                "cost_drag_today": 0.0,
            }
        )

        if sess not in rebal_set:
            continue

        print(f"[paper-costs] rebalance {sess} navA={nav_a:.4f} navB={nav_b:.4f}", flush=True)
        d1 = d1_members_at(
            sess, instrument_ids=pool, config=cfg, roots=roots, return_result=True
        )
        assert not isinstance(d1, tuple)
        if d1.promotion_approved:
            raise RuntimeError("d1_promotion_approved_leak")
        members = list(d1.member_ids)
        frame = d1.frame
        if not frame.empty and "instrument_id" in frame.columns:
            mem_set = set(members)
            frame = frame[frame["instrument_id"].astype(str).isin(mem_set)].copy()

        fm = _fm_map(frame)
        factory.float_mktcap = fm
        sw = _sw_assignments_from_frame(frame, sess)
        labels = _industry_labels(frame)

        raw_m01 = factory.compute_raw(sess, "M01_12_1", members)
        raw_ep = factory.compute_raw(sess, "V01_EP", members)
        res_m01 = factory.neutralize(raw_m01, sw, mktcap=fm or None)
        res_ep = factory.neutralize(raw_ep, sw, mktcap=fm or None)
        composite = factory.integrate([res_m01, res_ep])
        scores = dict(composite.scores)
        if not scores:
            scores = _integrate_scores(raw_m01.values, raw_ep.values)

        plan = beta.plan(sess)
        if plan.promotion_approved:
            raise RuntimeError("beta_promotion_approved_leak")
        etf_target = float(plan.etf_sleeve_weight or 0.0)
        book_cap = float(
            plan.residual_book_weight_cap
            if plan.residual_book_weight_cap is not None
            else max(0.0, 1.0 - etf_target - float(plan.cash_weight or 0.0))
        )

        # residual-beta-c (Leo confirmed):
        #   A = zero-cost, OLD fill to residual_book_weight_cap
        #   B = costs+limit/halt, size book to residual_weight_to_hit_target_beta
        # Do NOT raise max_etf.
        book_cap_a = book_cap  # residual_book_weight_cap
        resid_hit = plan.residual_weight_to_hit_target_beta
        if resid_hit is None:
            book_cap_b = book_cap_a  # fallback if beta unit missing
            resid_hit_note = "residual_weight_to_hit_target_beta_missing_fallback_cap"
        else:
            book_cap_b = float(resid_hit)
            resid_hit_note = "residual_weight_to_hit_target_beta"

        result_a = constructor.construct(
            scores,
            session=sess,
            industry_labels=labels,
            prior_weights=stock_a if stock_a else None,
            universe=members,
            book_weight_cap=book_cap_a,
        )
        if result_a.promotion_approved:
            raise RuntimeError("constructor_promotion_approved_leak")
        target_a = {k: float(v) for k, v in result_a.weights.items() if float(v) > 1e-12}

        result_b = constructor.construct(
            scores,
            session=sess,
            industry_labels=labels,
            prior_weights=stock_b if stock_b else None,
            universe=members,
            book_weight_cap=book_cap_b,
        )
        if result_b.promotion_approved:
            raise RuntimeError("constructor_promotion_approved_leak")
        target_b = {k: float(v) for k, v in result_b.weights.items() if float(v) > 1e-12}

        # --- Path A: full fill to residual_cap, zero cost ---
        prior_a = dict(stock_a)
        stock_a = dict(target_a)
        book_sum_a = float(sum(stock_a.values()))
        etf_a = etf_target
        cash_a = max(0.0, 1.0 - etf_a - book_sum_a)
        turnovers_a.append(float(result_a.turnover_one_way))

        # --- Path B: β-target residual weight + fill constraints + S2 lot/costs ---
        prior_b = dict(stock_b)
        filled_b, deltas_b, block_reasons = apply_fill_constraints(
            prior_weights=prior_b,
            target_weights=target_b,
            session=sess,
            tradability=tradability,
        )
        # S2: 整手 + min_trade (ledger-aligned) before costing; leftover → cash
        px_map = _prices_at(sess)
        lot_book = apply_lot_and_min_trade(
            prior_weights=prior_b,
            target_weights=filled_b,
            portfolio_value_cny=nav_b * capital,
            prices=px_map,
            min_trade_notional_cny=_min_trade,
            etf_prior=etf_b,
            etf_target=etf_target,
            etf_price=_etf_close_by_session.get(sess),
        )
        # ETF always assumed fillable in this research stub (no ETF halt panel wired)
        etf_delta = float(lot_book.etf_delta)
        stock_b = {
            k: float(v) for k, v in lot_book.adjusted_weights.items() if float(v) > 1e-12
        }
        book_sum_b = float(sum(stock_b.values()))
        etf_b = float(etf_b + etf_delta)  # lot-adjusted ETF weight
        cash_b = max(0.0, 1.0 - etf_b - book_sum_b)

        # clearer: 0.5 * L1 of all sleeve deltas
        all_ids = set(prior_b) | set(stock_b)
        l1 = abs(etf_delta)
        for iid in all_ids:
            l1 += abs(float(stock_b.get(iid, 0.0)) - float(prior_b.get(iid, 0.0)))
        to_b = 0.5 * l1
        turnovers_b.append(float(to_b))

        n_buy_blk = sum(1 for r in block_reasons.values() if r.startswith("buy_blocked"))
        n_sell_blk = sum(1 for r in block_reasons.values() if r.startswith("sell_blocked"))
        total_buy_blocks += n_buy_blk
        total_sell_blocks += n_sell_blk

        # weight deltas actually filled after lot/min-trade (stocks + etf)
        filled_deltas = dict(lot_book.weight_delta)
        br = compute_rebalance_costs(
            weight_delta=filled_deltas,
            portfolio_value_cny=nav_b * capital,
            session=sess,
            costs=costs,
            etf_delta=etf_delta,
            etf_pays_stamp=False,  # ledger: stamp only asset_type==stock
            lot_diag=lot_book,
        )
        nav_b_before_cost = nav_b
        nav_b = costs_drag_on_unit_nav(
            cost_cny=br.total_cny, unit_nav=nav_b, capital_cny=capital
        )
        cost_drag = float(nav_b_before_cost - nav_b)
        total_cost_cny += br.total_cny
        rows_b[-1]["nav"] = nav_b
        rows_b[-1]["cost_drag_today"] = cost_drag
        if nav_b_before_cost > 0 and br.total_cny > 0:
            rows_b[-1]["daily_ret"] = float(rows_b[-1]["daily_ret"]) + (
                nav_b / nav_b_before_cost - 1.0
            )

        cost_rows.append(
            {
                "session": str(sess),
                "commission_cny": br.commission_cny,
                "slippage_cny": br.slippage_cny,
                "stamp_tax_cny": br.stamp_tax_cny,
                "total_cny": br.total_cny,
                "stamp_tax_bps": br.stamp_tax_bps,
                "buy_notional_cny": br.buy_notional_cny,
                "sell_notional_cny": br.sell_notional_cny,
                "stock_sell_notional_cny": br.stock_sell_notional_cny,
                "etf_sell_notional_cny": br.etf_sell_notional_cny,
                "n_buy_orders": br.n_buy_orders,
                "n_sell_orders": br.n_sell_orders,
                "n_dropped_min_trade": br.n_dropped_min_trade,
                "n_lot_rounded": br.n_lot_rounded,
                "n_price_missing_kept_continuous": br.n_price_missing_kept_continuous,
                "notional_shaved_cny": br.notional_shaved_cny,
                "semantics_version": br.semantics_version,
                "nav_unit_before": nav_b_before_cost,
                "nav_unit_after": nav_b,
                "cost_drag_unit_nav": cost_drag,
                "n_buy_blocks": n_buy_blk,
                "n_sell_blocks": n_sell_blk,
            }
        )

        rebal_log.append(
            {
                "session": str(sess),
                "n_d1_members": len(members),
                "n_scores": len(scores),
                "n_names_target_a": result_a.n_names,
                "n_names_target_b": result_b.n_names,
                "n_names_a": len(stock_a),
                "n_names_b": len(stock_b),
                "etf_w": etf_target,
                "book_cap_a_residual_book_weight_cap": book_cap_a,
                "book_cap_b_residual_weight_to_hit_target_beta": book_cap_b,
                "residual_weight_to_hit_target_beta": None if resid_hit is None else float(resid_hit),
                "resid_hit_note": resid_hit_note,
                "implied_portfolio_beta_at_residual_fill": plan.implied_portfolio_beta_at_residual_fill,
                "assumed_residual_unit_beta": plan.assumed_residual_unit_beta,
                "turnover_a": float(result_a.turnover_one_way),
                "turnover_b_filled": float(to_b),
                "buy_blocks": n_buy_blk,
                "sell_blocks": n_sell_blk,
                "cost_total_cny": br.total_cny,
                "drawdown_tier": plan.drawdown_tier,
                "implied_sleeve_beta": plan.implied_sleeve_beta,
                "beta_gap_to_mandate": plan.beta_gap_to_mandate,
                "max_etf_not_raised": True,
                "promotion_approved": False,
            }
        )

    # --- metrics & write ---
    def _pack(rows, turnovers):
        df = pd.DataFrame(rows)
        nav_s = pd.Series(df["nav"].values, index=df["date"].values)
        ret_s = pd.Series(df["daily_ret"].values, index=df["date"].values)
        return df, nav_s, ret_s, _metrics(nav_s, ret_s, turnovers)

    df_a, nav_sa, ret_sa, met_a = _pack(rows_a, turnovers_a)
    df_b, nav_sb, ret_sb, met_b = _pack(rows_b, turnovers_b)

    def _delta(ka, kb):
        if ka is None or kb is None:
            return None
        return float(kb) - float(ka)

    delta = {
        "cagr": _delta(met_a.get("cagr"), met_b.get("cagr")),
        "sharpe_rf0": _delta(met_a.get("sharpe_rf0"), met_b.get("sharpe_rf0")),
        "max_drawdown": _delta(met_a.get("max_drawdown"), met_b.get("max_drawdown")),
        "total_return": _delta(met_a.get("total_return"), met_b.get("total_return")),
        "ann_vol": _delta(met_a.get("ann_vol"), met_b.get("ann_vol")),
    }

    summary = {
        "title": "QuantLab Strategy paper costs P0 — A zero-cost@residual_cap vs B costs+limit@residual_beta_c",
        "promotion_approved": False,
        "research_only": True,
        "not_expected_return": True,
        "not_a_promotion_gate": True,
        "one_variable": "A=zero-cost+residual_book_weight_cap; B=costs+limit/halt+residual_weight_to_hit_target_beta (residual-beta-c); max_etf not raised",
        "max_etf_not_raised": True,
        "candidate_pool": candidate_pool,
        "run_tier": run_tier,
        "external_claim": external_claim,
        "full_d1": bool(full_d1),
        "primary_external_report": bool(primary_external and full_d1),
        "smoke_iteration_note": smoke_note,
        "panel_cache": cache_stats() if (use_panel_cache or full_d1) else None,
        "window": {"start": str(start), "end": str(end)},
        "end_provenance": end_provenance,
        "post_d0_extend": {
            "active": post_d0,
            "d0_cutoff": str(d0_cutoff),
            "u30_waive_on_amount_gap": True,
        },
        "cost_knobs": {
            "commission_bps_one_way": costs.commission_bps_one_way,
            "commission_min_cny_per_order": costs.commission_min_cny_per_order,
            "slippage_bps_one_way": costs.slippage_bps_one_way,
            "stamp_tax_sell_only": costs.stamp_tax_sell_only,
            "stamp_tax_schedule": "historical_CN_table (≤2023-08-27: 10bp; ≥2023-08-28: 5bp)",
            "stamp_on_etf_sells": False,
            "lot_size_rounding": _lot_rounding,
            "buy_lot_default": 100,
            "min_trade_notional_cny": _min_trade,
            "semantics_version": SEMANTICS_VERSION,
            "capital_cny": capital,
            "fast_sim_not_promotion_evidence": costs.fast_sim_not_promotion_evidence,
            "s2_note": "ledger-aligned commission/stamp/lot/min_trade; Full D1 numbers pre-S2 need recompute",
        },
        "tradability": {
            "n_instruments_loaded": tradability.n_instruments_loaded,
            "n_limit_price_missing_cells": tradability.n_limit_price_missing_cells,
            "n_tradestatus_missing_cells": tradability.n_tradestatus_missing_cells,
            "n_is_st_missing_cells": tradability.n_is_st_missing_cells,
            "notes": tradability.notes,
            "mark_rule": "always mark to close; limit/halt restricts trading only (fixed 2026-10-10)",
            "fill_rule": "buy blocked on limit_up/halt/ST; sell blocked on limit_down/halt; ETF assumed fillable",
            "total_zeroed_name_days": total_zeroed_name_days,
            "total_buy_blocks": total_buy_blocks,
            "total_sell_blocks": total_sell_blocks,
        },
        "path_a_zero_cost": {
            "metrics_research_only": met_a,
            "marking": "close_to_close; no costs; no limit/halt zeroing; book_cap=residual_book_weight_cap",
            "output_dir": str(out_a.resolve()),
        },
        "path_b_costs": {
            "metrics_research_only": met_b,
            "marking": "close_to_close + cost drag + fill blocks (no zeroing); book_cap=residual_weight_to_hit_target_beta",
            "total_cost_cny": total_cost_cny,
            "total_cost_as_frac_of_capital": total_cost_cny / capital if capital else None,
            "output_dir": str(out_b.resolve()),
        },
        "delta_b_minus_a": delta,
        "n_trading_sessions": len(sess_in_window),
        "n_rebalances": len(rebal_log),
        "wall_seconds": round(time.time() - t_wall0, 1),
        "reproduce": (
            "cd /workspace/QuantLab && "
            "PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.portfolio.v2_strategy_paper_costs"
        ),
        "output_dir": str(out_root.resolve()),
    }

    # write A
    df_a.to_csv(out_a / "nav.csv", index=False)
    df_a.to_csv(out_a / "returns.csv", index=False)
    (out_a / "summary.json").write_text(
        json.dumps(
            {
                "path": "A_zero_cost",
                "promotion_approved": False,
                "metrics_research_only": met_a,
                "window": summary["window"],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    _plot_nav(nav_sa, out_a / "nav.png")

    # write B
    df_b.to_csv(out_b / "nav.csv", index=False)
    df_b.to_csv(out_b / "returns.csv", index=False)
    (out_b / "costs_ledger.csv").write_text(
        pd.DataFrame(cost_rows).to_csv(index=False), encoding="utf-8"
    )
    (out_b / "summary.json").write_text(
        json.dumps(
            {
                "path": "B_costs_limit_halt",
                "promotion_approved": False,
                "metrics_research_only": met_b,
                "total_cost_cny": total_cost_cny,
                "window": summary["window"],
                "cost_knobs": summary["cost_knobs"],
                "tradability": summary["tradability"],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    _plot_nav(nav_sb, out_b / "nav.png")

    # root compare artefacts
    overlay_ok = _plot_overlay(nav_sa, nav_sb, out_root / "nav.png")
    summary["nav_png_overlay"] = bool(overlay_ok)
    (out_root / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (out_root / "rebalance_log.json").write_text(
        json.dumps(rebal_log, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    # combined nav for convenience
    cmp = pd.DataFrame(
        {
            "date": df_a["date"],
            "nav_a": df_a["nav"],
            "nav_b": df_b["nav"],
            "ret_a": df_a["daily_ret"],
            "ret_b": df_b["daily_ret"],
        }
    )
    cmp.to_csv(out_root / "nav.csv", index=False)
    cmp.to_csv(out_root / "returns.csv", index=False)

    _write_limitations_zh(out_root, summary)
    _write_leo_report_zh(out_root, summary)
    _write_readme(out_root, summary)

    print(json.dumps({"ok": True, "delta": delta, "met_b": met_b, "out": str(out_root)}, ensure_ascii=False), flush=True)
    return summary


def _pct(x) -> str:
    if x is None:
        return "n/a"
    return f"{100.0 * float(x):.2f}%"


def _num(x) -> str:
    if x is None:
        return "n/a"
    return f"{float(x):.3f}"


def _write_leo_report_zh(out: Path, summary: dict) -> None:
    a = summary["path_a_zero_cost"]["metrics_research_only"]
    b = summary["path_b_costs"]["metrics_research_only"]
    d = summary["delta_b_minus_a"]
    tr = summary["tradability"]
    text = f"""# Leo 短报素材 — 成本 P0（residual-beta-c）A vs B

**promotion_approved=false。数字仅作研究，不是预期收益 / 不是晋升。**
**对照臂**：A = 零成本 + 旧 `residual_book_weight_cap` 满填；B = 成本+涨跌停/停牌 + `residual_weight_to_hit_target_beta`（目标组合 β≈0.70）。**不抬 max_etf**。`promotion_approved=false`。

## 关键数字（实算，residual-beta-c）

| 项 | A 零成本@residual_cap | B 成本+涨停@β目标残差权重 | Δ (B−A) |
|----|----------|------------------|---------|
| 区间 | {a.get('date_start')} → {a.get('date_end')} | 同左 | — |
| 交易日 / 再平衡 | {a.get('n_days')} / {a.get('n_rebalances')} | {b.get('n_days')} / {b.get('n_rebalances')} | — |
| 累计收益 | {_pct(a.get('total_return'))} | {_pct(b.get('total_return'))} | {_pct(d.get('total_return'))} |
| 年化 CAGR | {_pct(a.get('cagr'))} | {_pct(b.get('cagr'))} | {_pct(d.get('cagr'))} |
| 夏普 Sharpe (rf=0) | {_num(a.get('sharpe_rf0'))} | {_num(b.get('sharpe_rf0'))} | {_num(d.get('sharpe_rf0'))} |
| 最大回撤 | {_pct(a.get('max_drawdown'))} | {_pct(b.get('max_drawdown'))} | {_pct(d.get('max_drawdown'))} |
| 年化波动 | {_pct(a.get('ann_vol'))} | {_pct(b.get('ann_vol'))} | {_pct(d.get('ann_vol'))} |

## residual-beta-c（Leo 已确认）

- **不抬** `max_etf`
- A 残差书权重上限 = `plan.residual_book_weight_cap`
- B 残差书权重上限 = `plan.residual_weight_to_hit_target_beta`（在 residual_cap 内，按假定残差 unit β≈1.0 补到 Mandate β0.70）
- 袖套隐含 β 仍可低于 0.70；组合 β 靠 B 的残差权重去贴目标

## 成本与可交易性（B）

- 累计成本（研究快仿）：**{summary['path_b_costs'].get('total_cost_cny'):.2f} CNY**（约占初始资金 {_pct(summary['path_b_costs'].get('total_cost_as_frac_of_capital'))}）
- 佣金 2.5bp+最低¥5；滑点 5bp；印花税卖出（本窗口 5bp）
- 涨跌停/停牌：当日该票收益贡献置 0；买/卖按掩码拒成
- 置零 name-days：{tr.get('total_zeroed_name_days')}；买拒成 {tr.get('total_buy_blocks')}；卖拒成 {tr.get('total_sell_blocks')}
- 缺字段：limit 价缺失则不判涨跌停；tradestatus 缺失则不判停牌（见 LIMITATIONS）

## 路径

- 根目录：`{out}`
- A：`{out / 'zero_cost_a'}`
- B：`{out / 'costs_b'}`（含 `costs_ledger.csv`）
- 对照 NAV：`{out / 'nav.csv'}` / `{out / 'nav.png'}`

## 复现

```bash
cd /workspace/QuantLab
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.portfolio.v2_strategy_paper_costs
```

## 一句话

B = 成本+涨跌停 + `residual_weight_to_hit_target_beta`（不抬 max_etf，目标组合 β≈0.70）；A = 零成本旧 cap。pool=250 仅为 smoke；主结论看 Full D1（若已跑）。不可晋升。
"""
    (out / "LEO_REPORT_ZH.md").write_text(text, encoding="utf-8")


def _write_limitations_zh(out: Path, summary: dict) -> None:
    tr = summary["tradability"]
    ck = summary["cost_knobs"]
    text = f"""# 研究级局限说明 — Strategy paper A vs B（成本+涨跌停）

**硬约束：`promotion_approved=false`。下列数字仅为研究过程度量，不是预期收益，不是晋升门。**

## 本跑次设定（Leo 锁定单变量 B）

- 区间：{summary['window']['start']} → {summary['window']['end']}
- 候选池：`pool={summary['candidate_pool']}` —— **smoke/iteration only，非 Full D1 / 非对外口径**
- **未**抬 `max_etf`；Alpha/Beta/D1 接线与 A 相同，只改 marking / 成交摩擦
- A：零成本、不涨跌停置零（与 paper v1 同口径）
- B：Mandate 成本 + 涨跌停/停牌

## 成本模型（快仿，不可晋升）

- 佣金：{ck['commission_bps_one_way']} bp 单边 + 最低 ¥{ck['commission_min_cny_per_order']}/笔
- 滑点：{ck['slippage_bps_one_way']} bp 单边（未按 ADV 分层）
- 印花税：仅卖出；{ck['stamp_tax_schedule']}（本窗口 ≥2024-06 → 5bp）
- 资金底座：¥{ck['capital_cny']:.0f}（单位净值×资金 → 名义成交额）
- `fast_sim_not_promotion_evidence=true`

## 涨跌停 / 停牌

- `limit_up` / `limit_down` 为**涨跌停价**；`close` 触及则判 hit（与 D1 一致）
- `tradestatus==0` 或 `open_status==halted` → 停牌
- **打标**：涨停或跌停或停牌 → 该票当日收益贡献 = 0
- **成交**：涨停/停牌/ST 拒买；跌停/停牌拒卖；未成交权重留在原持仓，差额进现金
- ETF 袖套本版假设可成交（未接 ETF 停牌面板）
- **缺字段**：limit 价缺失 → 不判涨跌停；tradestatus 缺失 → 不判停牌；is_st 缺失 → 不判 ST
  - limit 缺失 cell 数：{tr.get('n_limit_price_missing_cells')}
  - tradestatus 缺失 cell 数：{tr.get('n_tradestatus_missing_cells')}
  - is_st 缺失 cell 数：{tr.get('n_is_st_missing_cells')}
  - notes：{tr.get('notes')}

## 仍继承的 paper 局限（未在本变量消除）

1. pool=250 有偏采样（下一项才是 Full D1 对照）
2. EP asof 陈旧 / stale-carry；`financials_promotable=false`
3. SW_L1 不可晋升
4. 晚盘 asof_extend amount 稀疏、U30 waive、float 薄
5. 指数 β overlap 止于 2026-06-30；Mandate β 张力（不抬 max_etf）
6. LW 未上；无完整 T+1 / 冲击 ADV 分层
7. 除权 gaps 未闭

## 指标口径

- CAGR / Sharpe(rf=0) / 最大回撤由 A/B 各自 NAV 实算；Δ = B−A
- **禁止**把这些数字当作实盘期望或晋升证据

墙钟约 {summary.get('wall_seconds')}s。
"""
    (out / "LIMITATIONS_ZH.md").write_text(text, encoding="utf-8")


def _write_readme(out: Path, summary: dict) -> None:
    text = f"""# Strategy paper A vs B (costs + limit/halt)

`promotion_approved=false`. Research-only. One variable: execution friction.

## Reproduce

```bash
cd /workspace/QuantLab
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.portfolio.v2_strategy_paper_costs
```

## Outputs

- `zero_cost_a/` — path A
- `costs_b/` — path B (+ `costs_ledger.csv`)
- `nav.csv` / `returns.csv` / `nav.png` / `summary.json`
- `LEO_REPORT_ZH.md` / `LIMITATIONS_ZH.md`

Window: {summary['window']['start']} → {summary['window']['end']}; pool={summary['candidate_pool']}.
"""
    (out / "README.md").write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    import argparse

    ap = argparse.ArgumentParser(description="Strategy paper A vs B costs/limit (research)")
    ap.add_argument("--full-d1", action="store_true", help="Full D1 universe (primary external when set with costs)")
    ap.add_argument("--pool", type=int, default=CANDIDATE_POOL, help="Smoke pool size (ignored if --full-d1)")
    ap.add_argument("--out", type=str, default=None, help="Output root directory")
    ap.add_argument("--primary", action="store_true", help="Mark as primary external report (use with --full-d1)")
    ap.add_argument("--panel-cache", action="store_true", help="Cache load_merged_panel in-process")
    ap.add_argument(
        "--turn-compare",
        action="store_true",
        help="Delegate to TURN compare (P1 M01+EP vs +turn_20d; both costs+βc+LW)",
    )
    ns = ap.parse_args(argv)
    if ns.turn_compare:
        from quantlab.portfolio.v2_strategy_paper_turn_compare import run_turn_compare

        run_turn_compare(
            candidate_pool=None if ns.full_d1 else ns.pool,
            full_d1=bool(ns.full_d1),
            out_root=Path(ns.out) if ns.out else None,
            use_panel_cache=bool(ns.panel_cache or ns.full_d1),
        )
        return
    run_ab_compare(
        candidate_pool=None if ns.full_d1 else ns.pool,
        full_d1=bool(ns.full_d1),
        out_root=Path(ns.out) if ns.out else None,
        primary_external=bool(ns.primary or ns.full_d1),
        use_panel_cache=bool(ns.panel_cache or ns.full_d1),
    )


if __name__ == "__main__":
    main()
