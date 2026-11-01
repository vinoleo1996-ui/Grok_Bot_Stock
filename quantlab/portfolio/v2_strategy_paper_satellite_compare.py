"""Strategy paper S4/S6: A=no satellite vs B=+smallcap ETF satellite (512100, frac 0.25 of ETF budget).

Generated from v2_strategy_paper_turn_compare; TURN OFF both arms (M01+EP).
ORIGINAL DOC:

Research-only. promotion_approved=false. Satellite OFF. max_etf not raised.

One variable = Alpha integrate membership:
  Arm A: P1 integrate M01_12_1 + V01_EP
  Arm B: P1 integrate M01_12_1 + V01_EP + turn_20d (ortho after M01/EP)

Both arms: S2 ledger costs + limit/halt fills + residual_weight_to_hit_target_beta
+ S1 LW target_vol when returns_panel usable (else equal stub).

Outputs under output/strategy_paper_costs/turn_compare/ (smoke) or
output/strategy_paper_costs/full_d1_turn/ (Full D1).

Reproduce::

    cd /workspace/QuantLab
    PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.portfolio.v2_strategy_paper_turn_compare
    PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.portfolio.v2_strategy_paper_turn_compare --full-d1 \
        --memory-safe --chunk-size 300 --cache-max-items 400
"""
from __future__ import annotations

from quantlab.promotion_gate import overall_promotion_approved as _gate

import gc
import json
import math
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np
import pandas as pd

from quantlab.beta import VolTargetBetaSleeveProvider
from quantlab.config import ROOT
from quantlab.data.v2_readers import default_v2_roots, load_etf_510300, load_merged_calendar, load_ep_research
from quantlab.factors.p1_pipeline import run_p1_integrate_session
from quantlab.mandate_v2 import load_mandate_v2
from quantlab.platform.strategy_feed import (
    DEFAULT_CLOSE_CHUNK_SIZE,
    biweekly_rebalance_sessions,
    d1_members_at,
    d1_members_at_chunked,
    etf_510300_daily_returns,
    merged_close_panel,
    merged_daily_returns,
    trading_sessions,
)
from quantlab.portfolio.v2_constructor import PortfolioConstructorV2
from quantlab.portfolio.v2_execution_costs import (
    SEMANTICS_VERSION,
    apply_fill_constraints,
    apply_lot_and_min_trade,
    compute_rebalance_costs,
    costs_drag_on_unit_nav,
    load_tradability_panels,
)
from quantlab.portfolio.v2_lean_panels import (
    build_lean_close_turnover_tradability,
    date_index_to_timestamp,
    rss_gb,
    to_float32,
)
from quantlab.portfolio.v2_panel_cache import (
    cache_stats,
    clear_merged_panel_cache,
    install_merged_panel_cache,
)
from quantlab.portfolio.v2_strategy_paper import (
    CANDIDATE_POOL,
    LOOKBACK_CALENDAR_DAYS,
    PAPER_START,
    _candidate_pool,
    _fm_map,
    _industry_labels,
    _metrics,
    _plot_nav,
    _sw_assignments_from_frame,
    resolve_paper_end,
)
from quantlab.portfolio.v2_strategy_paper_costs import (
    PAPER_END_EXPLICIT,
    _all_panel_ids,
    _book_ret,
    _etf_ret,
    _num,
    _pct,
)
from quantlab.universe.d1_masks import D1MaskConfig

FACTORS_BASELINE = ("M01_12_1", "V01_EP")
FACTORS_TURN = ("M01_12_1", "V01_EP", "turn_20d")

OUTPUT_SMOKE = ROOT / "output" / "strategy_paper_costs" / "satellite_smoke"
OUTPUT_FULL = ROOT / "output" / "strategy_paper_costs" / "full_d1_satellite"
SAT_CODE = "sh512100"
SAT_FRAC = 0.25
LEGACY_FULL_D1_PRE_S2 = ROOT / "output" / "strategy_paper_costs" / "full_d1"


def _returns_upto(
    stock_rets: pd.DataFrame,
    sess: date,
    columns: Sequence[str] | None = None,
) -> pd.DataFrame:
    """Point-in-time slice: no future returns into LW. Optional column subset."""
    if stock_rets is None or stock_rets.empty:
        return stock_rets
    idx_dates = [
        x if isinstance(x, date) else pd.Timestamp(x).date() for x in stock_rets.index
    ]
    mask = [d <= sess for d in idx_dates]
    out = stock_rets.loc[mask]
    if columns is not None:
        cols = [c for c in columns if c in out.columns]
        out = out.loc[:, cols] if cols else out.iloc[:, 0:0]
    # Avoid full deep copy of 847×6k; LW gets a narrow slice.
    return out


def _subset_panels(panels: Mapping[str, object] | None, members: Sequence[str]) -> dict | None:
    if panels is None:
        return None
    mem = [str(x) for x in members]
    panels_use: dict = {}
    for k, df in panels.items():
        if df is None or getattr(df, "empty", True):
            panels_use[k] = df
            continue
        cols = [c for c in mem if c in df.columns]
        # view — do not .copy() full wide frame
        panels_use[k] = df.loc[:, cols] if cols else df.iloc[:, 0:0]
    return panels_use


def _scores_p1(
    sess: date,
    members: Sequence[str],
    fm: Mapping[str, float],
    sw,
    *,
    factor_ids: Sequence[str],
    roots,
    panels: Mapping[str, object] | None = None,
    ep_research_view=None,
) -> tuple[dict[str, float], tuple[str, ...], Mapping[str, int]]:
    panels_use = _subset_panels(panels, members)
    result = run_p1_integrate_session(
        sess,
        list(members),
        fm,
        sw,
        d0_root=roots.d0_root,
        asof_extend_dir=roots.asof_extend_dir,
        factor_ids=factor_ids,
        integrate_mode="equal",
        # MAINBOOK_V2 (p1_factor_lib) defaults M01_12_1/V01_EP to integrate weight 0;
        # pin this arm's factors to 1.0 so the D1 baseline composite is not empty.
        icir_weights={str(f): 1.0 for f in factor_ids},
        mktcap_neutral=True,
        panels=panels_use,
        ep_research_view=ep_research_view,
    )
    if result.promotion_approved:
        raise RuntimeError("p1_promotion_approved_leak")
    scores = {str(k): float(v) for k, v in dict(result.composite.scores).items()}
    if not scores and any(int(v or 0) > 0 for v in dict(result.coverage).values()):
        raise RuntimeError(f"p1_empty_composite_with_coverage:{sess}:{dict(result.coverage)}")
    return scores, tuple(result.notes), dict(result.coverage)


def _write_status(out_root: Path, payload: dict) -> None:
    out_root.mkdir(parents=True, exist_ok=True)
    payload = dict(payload)
    payload.setdefault("promotion_approved", False)
    payload["rss_gb"] = round(rss_gb(), 3)
    payload["updated_et"] = time.strftime("%Y-%m-%d %H:%M:%S")
    (out_root / "STATUS.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _apply_cost_path(
    *,
    prior: dict[str, float],
    target: dict[str, float],
    etf_prior: float,
    etf_target: float,
    sess: date,
    tradability,
    nav: float,
    capital: float,
    costs,
    prices: Mapping[str, float],
    etf_px: float | None,
    min_trade: float,
) -> tuple[dict[str, float], float, float, float, object, dict[str, str], float]:
    """Fill constraints + S2 lot + costs → (stock_w, etf_w, cash_w, nav_after, br, blocks, turnover)."""
    filled, _deltas, block_reasons = apply_fill_constraints(
        prior_weights=prior,
        target_weights=target,
        session=sess,
        tradability=tradability,
    )
    lot_book = apply_lot_and_min_trade(
        prior_weights=prior,
        target_weights=filled,
        portfolio_value_cny=nav * capital,
        prices=prices,
        min_trade_notional_cny=min_trade,
        etf_prior=etf_prior,
        etf_target=etf_target,
        etf_price=etf_px,
    )
    etf_delta = float(lot_book.etf_delta)
    stock = {k: float(v) for k, v in lot_book.adjusted_weights.items() if float(v) > 1e-12}
    book_sum = float(sum(stock.values()))
    etf_w = float(etf_prior + etf_delta)
    cash_w = max(0.0, 1.0 - etf_w - book_sum)
    all_ids = set(prior) | set(stock)
    l1 = abs(etf_delta)
    for iid in all_ids:
        l1 += abs(float(stock.get(iid, 0.0)) - float(prior.get(iid, 0.0)))
    to = 0.5 * l1
    br = compute_rebalance_costs(
        weight_delta=dict(lot_book.weight_delta),
        portfolio_value_cny=nav * capital,
        session=sess,
        costs=costs,
        etf_delta=etf_delta,
        etf_pays_stamp=False,
        lot_diag=lot_book,
    )
    nav_after = costs_drag_on_unit_nav(
        cost_cny=br.total_cny, unit_nav=nav, capital_cny=capital
    )
    return stock, etf_w, cash_w, nav_after, br, block_reasons, float(to)


def _carry_pending(*, stock, etf_w, pending, sess, tradability, nav, capital, costs, prices, etf_px, min_trade):
    """Retry blocked orders on a non-rebalance day; still-blocked stay pending."""
    from quantlab.portfolio.v2_execution_costs import carry_target, pending_from_blocks
    tgt = carry_target(stock, pending)
    st, ew, cw, nav2, br, blocks, to = _apply_cost_path(prior=dict(stock), target=tgt, etf_prior=etf_w, etf_target=etf_w,
        sess=sess, tradability=tradability, nav=nav, capital=capital, costs=costs, prices=prices, etf_px=etf_px, min_trade=min_trade)
    return st, ew, cw, nav2, br, pending_from_blocks(tgt, blocks), to


def run_turn_compare(
    *,
    start: date = PAPER_START,
    end: date | None = PAPER_END_EXPLICIT,
    candidate_pool: int | None = CANDIDATE_POOL,
    full_d1: bool = False,
    out_root: Path | None = None,
    use_panel_cache: bool = False,
    weighting_mode: str = "auto",
    memory_safe: bool | None = None,
    pool_cap: int | None = None,
    chunk_size: int | None = None,
    float32: bool = True,
    cache_max_items: int | None = 400,
    use_disk_cache: bool = False,
) -> dict:
    t_wall0 = time.time()
    if out_root is not None:
        out_root = Path(out_root)
    elif full_d1:
        out_root = OUTPUT_FULL
    else:
        out_root = OUTPUT_SMOKE
    out_a = out_root / "arm_a_baseline_m01_ep"
    out_b = out_root / "arm_b_plus_satellite"
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
    # Default: Full D1 uses memory-safe lean path (no long-frame cache).
    if memory_safe is None:
        memory_safe = bool(full_d1)
    if chunk_size is None:
        chunk_size = DEFAULT_CLOSE_CHUNK_SIZE if (full_d1 or memory_safe) else None
    close_dtype = "float32" if float32 else "float64"

    if full_d1:
        pool = _all_panel_ids(roots)
        if pool_cap is not None and int(pool_cap) > 0 and len(pool) > int(pool_cap):
            pool = pool[: int(pool_cap)]
            candidate_pool = len(pool)
            run_tier = f"mid_tier_pool{candidate_pool}_turn_compare"
            smoke_only = True
            smoke_note = (
                f"NOT MAIN — mid-tier pool={candidate_pool} (Full D1 memory fallback). "
                "Do not treat as external Full D1 main conclusion. "
                "promotion_approved=false. Satellite OFF."
            )
            print(
                f"[sat-cmp] MID-TIER pool_cap={pool_cap} → pool={len(pool)} (NOT main)",
                flush=True,
            )
        else:
            candidate_pool = len(pool)
            run_tier = "full_d1_turn_compare"
            smoke_only = False
            smoke_note = (
                "PRIMARY Full D1 + costs + residual-beta-c + LW(auto) + TURN compare. "
                "Memory-safe lean panels (no full OHLCV preload / no long-frame cache). "
                "promotion_approved=false. Satellite OFF. max_etf not raised."
            )
    else:
        assert candidate_pool is not None
        pool = _candidate_pool(int(candidate_pool), roots)
        run_tier = "smoke_pool250_turn_compare"
        smoke_only = True
        smoke_note = (
            "SMOKE ONLY — pool=250. Not Full D1 / not external-facing main conclusion. "
            "Main conclusion = Full D1 turn compare when available."
        )

    # Smoke may use panel cache; Full D1 memory-safe path must NOT retain long frames.
    if (use_panel_cache or full_d1) and not memory_safe:
        install_merged_panel_cache(max_items=cache_max_items)
        print(
            f"[sat-cmp] merged_panel cache installed max_items={cache_max_items}",
            flush=True,
        )
    elif memory_safe:
        clear_merged_panel_cache()
        print(
            f"[sat-cmp] memory_safe=ON rss={rss_gb():.2f}Gi — no long-frame panel cache",
            flush=True,
        )

    cfg = D1MaskConfig(open_status_mode="research", waive_u30_on_amount_gap=True)
    cal_view = load_merged_calendar(roots=roots)
    etf_bundle = load_etf_510300(roots=roots)
    end = resolve_paper_end(start=start, end=end, roots=roots)
    d0_cutoff = date(2026, 6, 30)
    post_d0 = end > d0_cutoff
    print(
        f"[sat-cmp] end={end} pool={len(pool)} full_d1={full_d1} "
        f"memory_safe={memory_safe} smoke_only={smoke_only}",
        flush=True,
    )
    _write_status(
        out_root,
        {
            "status": "RUNNING",
            "phase": "init",
            "full_d1": bool(full_d1),
            "memory_safe": bool(memory_safe),
            "smoke_only": smoke_only,
            "pool": len(pool),
            "run_tier": run_tier,
        },
    )

    sessions = trading_sessions(start, end, roots=roots)
    rebal_dates = biweekly_rebalance_sessions(start, end, mandate=mandate, roots=roots)
    if not sessions or not rebal_dates:
        raise RuntimeError("no_sessions_or_rebalances_in_window")

    load_start = start - timedelta(days=LOOKBACK_CALENDAR_DAYS)
    etf_rets = etf_510300_daily_returns(load_start, end, roots=roots)

    lean_meta: dict = {}
    if memory_safe:
        print(
            f"[sat-cmp] lean single-pass close+turnover+tradability "
            f"{load_start}→{end} (no full OHLCV preload)",
            flush=True,
        )
        t0 = time.time()

        def _prog(info: dict) -> None:
            print(
                f"[sat-cmp] lean {info['i']}/{info['n']} "
                f"close_cols={info['loaded_close']} rss={info['rss_gb']}Gi",
                flush=True,
            )
            _write_status(
                out_root,
                {
                    "status": "RUNNING",
                    "phase": "lean_preload",
                    "progress": info,
                    "full_d1": bool(full_d1),
                    "memory_safe": True,
                    "smoke_only": smoke_only,
                    "pool": len(pool),
                    "run_tier": run_tier,
                },
            )

        closes_raw, turnover_f32, tradability, lean_meta = build_lean_close_turnover_tradability(
            pool,
            load_start=load_start,
            end=end,
            tradability_start=start,
            roots=roots,
            chunk_size=int(chunk_size or 200),
            progress_every=500,
            on_progress=_prog,
        )
        stock_rets = merged_daily_returns(
            pool, load_start, end, roots=roots, close_panel=closes_raw, dtype=close_dtype
        )
        # P1 wants DatetimeIndex; keep date-index closes for pricing / book_ret
        p1_panels = {
            "close": date_index_to_timestamp(closes_raw),
            "turnover": date_index_to_timestamp(turnover_f32),
            "amount": pd.DataFrame(),
            "pb_mrq": pd.DataFrame(),
            "volume": pd.DataFrame(),
        }
        p1_panel_notes = (
            "lean_close_turnover_injected",
            "no_full_ohlcv_preload",
            "promotion_approved=false",
        )
        print(
            f"[sat-cmp] lean ready close={closes_raw.shape} "
            f"turnover={turnover_f32.shape} "
            f"trad={tradability.n_instruments_loaded} "
            f"in {time.time()-t0:.1f}s rss={rss_gb():.2f}Gi meta={lean_meta}",
            flush=True,
        )
    else:
        print(
            f"[sat-cmp] preload closes {load_start}→{end} "
            f"chunk_size={chunk_size} dtype={close_dtype} disk_cache={use_disk_cache}",
            flush=True,
        )
        t0 = time.time()
        closes_raw = merged_close_panel(
            pool,
            load_start,
            end,
            roots=roots,
            chunk_size=chunk_size,
            dtype=close_dtype,
            use_disk_cache=use_disk_cache,
        )
        if float32:
            closes_raw = to_float32(closes_raw)
        stock_rets = merged_daily_returns(
            pool, load_start, end, roots=roots, close_panel=closes_raw, dtype=close_dtype
        )
        if float32:
            stock_rets = to_float32(stock_rets)
        print(
            f"[sat-cmp] closes ready {closes_raw.shape} in {time.time()-t0:.1f}s "
            f"rss={rss_gb():.2f}Gi",
            flush=True,
        )
        print("[sat-cmp] preload P1 OHLCV panels (once) [smoke path]", flush=True)
        t0 = time.time()
        from quantlab.factors.p1_factor_lib import load_ohlcv_panels

        p1_panels, p1_panel_notes = load_ohlcv_panels(
            pool,
            d0_root=roots.d0_root,
            asof_extend_dir=roots.asof_extend_dir,
            end_session=end,
            lookback_calendar_days=LOOKBACK_CALENDAR_DAYS + 400,
        )
        # Downcast to float32 to cut peak
        p1_panels = {
            k: (to_float32(v) if isinstance(v, pd.DataFrame) else v)
            for k, v in p1_panels.items()
        }
        print(
            f"[sat-cmp] P1 panels ready notes={list(p1_panel_notes)[:4]} "
            f"close_cols={0 if p1_panels.get('close') is None else p1_panels['close'].shape} "
            f"in {time.time()-t0:.1f}s rss={rss_gb():.2f}Gi",
            flush=True,
        )
        print("[sat-cmp] load tradability", flush=True)
        t0 = time.time()
        tradability = load_tradability_panels(pool, start, end, roots=roots)
        print(
            f"[sat-cmp] tradability n={tradability.n_instruments_loaded} "
            f"in {time.time()-t0:.1f}s rss={rss_gb():.2f}Gi",
            flush=True,
        )
        if use_panel_cache or full_d1:
            # Drop long-frame cache after wide panels built (smoke safety).
            clear_merged_panel_cache()
            gc.collect()
            print(
                f"[sat-cmp] cleared panel cache after preload rss={rss_gb():.2f}Gi",
                flush=True,
            )

    try:
        ep_view = load_ep_research(roots=roots)
    except FileNotFoundError:
        ep_view = None

    _write_status(
        out_root,
        {
            "status": "RUNNING",
            "phase": "preload_done",
            "full_d1": bool(full_d1),
            "memory_safe": bool(memory_safe),
            "smoke_only": smoke_only,
            "pool": len(pool),
            "run_tier": run_tier,
            "close_shape": list(getattr(closes_raw, "shape", ())),
            "lean_meta": lean_meta,
            "n_rebalances_planned": len(rebal_dates),
        },
    )

    def _prices_at(sess_d: date) -> dict[str, float]:
        if closes_raw.empty:
            return {}
        ts = pd.Timestamp(sess_d)
        if ts in closes_raw.index:
            row = closes_raw.loc[ts]
        else:
            hits = closes_raw.index[
                closes_raw.index.map(lambda x: pd.Timestamp(x).date()) == sess_d
            ]
            if len(hits) == 0:
                return {}
            row = closes_raw.loc[hits[0]]
        if isinstance(row, pd.DataFrame):
            row = row.iloc[-1]
        out: dict[str, float] = {}
        for c, v in row.items():
            try:
                fv = float(v)
            except (TypeError, ValueError):
                continue
            if fv == fv and fv > 0:
                out[str(c)] = fv
        return out

    etf_close_by_session: dict[date, float] = {}
    try:
        etf_pf = getattr(etf_bundle, "panel_frame", None)
        if etf_pf is not None and not etf_pf.empty and "close" in etf_pf.columns:
            et = pd.to_datetime(etf_pf["event_time"]).dt.normalize()
            cl = pd.to_numeric(etf_pf["close"], errors="coerce")
            for d, px in zip(et.dt.date, cl):
                if px == px and float(px) > 0:
                    etf_close_by_session[d] = float(px)
    except Exception as exc:  # noqa: BLE001
        print(f"[sat-cmp] etf close map skip: {exc}", flush=True)

    min_trade = float(mandate.portfolio_limits.min_trade_notional_cny)
    constructor = PortfolioConstructorV2(mandate, weighting_mode=weighting_mode)
    beta = VolTargetBetaSleeveProvider(mandate, d0_root=roots.d0_root)
    beta_sat = VolTargetBetaSleeveProvider(
        mandate, d0_root=roots.d0_root, smallcap_satellite=True,
        satellite_code=SAT_CODE, max_satellite_frac=SAT_FRAC,
    )
    from quantlab.beta.satellite import load_satellite_series
    _ss = load_satellite_series(SAT_CODE, end)
    _sat_close = pd.Series(list(_ss.closes), index=list(_ss.sessions), dtype="float64")
    sat_rets = _sat_close.pct_change()
    sat_frac_b = 0.0
    sat_frac_log: list[float] = []

    etf_a = etf_b = 0.0
    cash_a = cash_b = 1.0
    stock_a: dict[str, float] = {}
    stock_b: dict[str, float] = {}
    nav_a = nav_b = 1.0
    turnovers_a: list[float] = []
    turnovers_b: list[float] = []
    cost_rows_a: list[dict] = []
    cost_rows_b: list[dict] = []
    rebal_log: list[dict] = []
    rows_a: list[dict] = []
    rows_b: list[dict] = []
    total_cost_a = total_cost_b = 0.0
    total_zeroed = 0
    lw_count_a = lw_count_b = 0
    stub_count_a = stub_count_b = 0

    rebal_set = set(rebal_dates)
    sess_in_window = [d for d in sessions if start <= d <= end]

    for i, sess in enumerate(sess_in_window):
        if i > 0:
            book_a, n_za = _book_ret(
                stock_a, stock_rets, sess, tradability=tradability
            )
            book_b, n_zb = _book_ret(
                stock_b, stock_rets, sess, tradability=tradability
            )
            total_zeroed += n_za + n_zb
            day_a = book_a + _etf_ret(etf_a, etf_rets, sess)
            _sr = sat_rets.get(sess, float("nan"))
            _sr = float(_sr) if _sr == _sr else 0.0
            day_b = book_b + _etf_ret(etf_b * (1.0 - sat_frac_b), etf_rets, sess) + etf_b * sat_frac_b * _sr
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
                "path": "A_baseline_m01_ep_costs",
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
                "path": "B_plus_satellite_costs",
                "cost_drag_today": 0.0,
            }
        )

        if sess not in rebal_set:
            continue

        print(
            f"[sat-cmp] rebalance {sess} navA={nav_a:.4f} navB={nav_b:.4f} "
            f"rss={rss_gb():.2f}Gi",
            flush=True,
        )
        _write_status(
            out_root,
            {
                "status": "RUNNING",
                "phase": "rebalance",
                "session": str(sess),
                "n_done": len(rebal_log),
                "n_planned": len(rebal_dates),
                "nav_a": nav_a,
                "nav_b": nav_b,
                "full_d1": bool(full_d1),
                "memory_safe": bool(memory_safe),
                "smoke_only": smoke_only,
                "pool": len(pool),
                "run_tier": run_tier,
            },
        )
        # Memory-safe: chunked D1 scan (Eng), then frame only for members.
        if memory_safe:
            member_ids = d1_members_at_chunked(
                sess,
                pool,
                chunk_size=int(chunk_size or 500),
                config=cfg,
                roots=roots,
            )
            members = list(member_ids)
            d1 = d1_members_at(
                sess,
                instrument_ids=members,
                config=cfg,
                roots=roots,
                return_result=True,
            )
        else:
            d1 = d1_members_at(
                sess, instrument_ids=pool, config=cfg, roots=roots, return_result=True
            )
            members = None
        assert not isinstance(d1, tuple)
        if d1.promotion_approved:
            raise RuntimeError("d1_promotion_approved_leak")
        if members is None:
            members = list(d1.member_ids)
        frame = d1.frame
        if not frame.empty and "instrument_id" in frame.columns:
            mem_set = set(members)
            frame = frame[frame["instrument_id"].astype(str).isin(mem_set)].copy()

        fm = _fm_map(frame)
        sw = _sw_assignments_from_frame(frame, sess)
        labels = _industry_labels(frame)

        scores_a, notes_a, cov_a = _scores_p1(
            sess, members, fm, sw, factor_ids=FACTORS_BASELINE, roots=roots,
            panels=p1_panels, ep_research_view=ep_view,
        )
        scores_b, notes_b, cov_b = scores_a, notes_a, cov_a  # same Alpha (TURN OFF)

        plan = beta.plan(sess)
        if plan.promotion_approved:
            raise RuntimeError("beta_promotion_approved_leak")
        etf_target = float(plan.etf_sleeve_weight or 0.0)
        plan_b = beta_sat.plan(sess)
        if plan_b.promotion_approved:
            raise RuntimeError("beta_sat_promotion_approved_leak")
        _etf_tot_b = float(plan_b.etf_sleeve_weight or 0.0)
        if plan_b.satellite_data_ready and _etf_tot_b > 1e-9 and plan_b.satellite_etf_weight is not None:
            sat_frac_b = float(plan_b.satellite_etf_weight) / _etf_tot_b
        else:
            sat_frac_b = 0.0
        sat_frac_log.append(sat_frac_b)
        resid_hit = plan.residual_weight_to_hit_target_beta
        if resid_hit is None:
            book_cap = float(
                plan.residual_book_weight_cap
                if plan.residual_book_weight_cap is not None
                else max(0.0, 1.0 - etf_target - float(plan.cash_weight or 0.0))
            )
            resid_note = "residual_weight_to_hit_target_beta_missing_fallback_cap"
        else:
            book_cap = float(resid_hit)
            resid_note = "residual_weight_to_hit_target_beta"

        # LW only needs returns for scored / prior names — not full 6k columns.
        lw_cols = sorted(
            set(scores_a)
            | set(scores_b)
            | set(stock_a)
            | set(stock_b)
            | set(members[: min(len(members), 400)])
        )
        rets_pit = _returns_upto(stock_rets, sess, columns=lw_cols)

        result_a = constructor.construct(
            scores_a,
            session=sess,
            industry_labels=labels,
            prior_weights=stock_a if stock_a else None,
            universe=members,
            book_weight_cap=book_cap,
            returns_panel=rets_pit,
            weighting_mode=weighting_mode,
        )
        result_b = constructor.construct(
            scores_b,
            session=sess,
            industry_labels=labels,
            prior_weights=stock_b if stock_b else None,
            universe=members,
            book_weight_cap=book_cap,
            returns_panel=rets_pit,
            weighting_mode=weighting_mode,
        )
        if result_a.promotion_approved or result_b.promotion_approved:
            raise RuntimeError("constructor_promotion_approved_leak")
        if result_a.method == "lw_target_vol":
            lw_count_a += 1
        else:
            stub_count_a += 1
        if result_b.method == "lw_target_vol":
            lw_count_b += 1
        else:
            stub_count_b += 1

        target_a = {k: float(v) for k, v in result_a.weights.items() if float(v) > 1e-12}
        target_b = {k: float(v) for k, v in result_b.weights.items() if float(v) > 1e-12}

        px_map = _prices_at(sess)
        etf_px = etf_close_by_session.get(sess)

        prior_a = dict(stock_a)
        stock_a, etf_a, cash_a, nav_a_new, br_a, blocks_a, to_a = _apply_cost_path(
            prior=prior_a,
            target=target_a,
            etf_prior=etf_a,
            etf_target=etf_target,
            sess=sess,
            tradability=tradability,
            nav=nav_a,
            capital=capital,
            costs=costs,
            prices=px_map,
            etf_px=etf_px,
            min_trade=min_trade,
        )
        nav_a_before = nav_a
        nav_a = nav_a_new
        cost_drag_a = float(nav_a_before - nav_a)
        total_cost_a += br_a.total_cny
        turnovers_a.append(to_a)
        rows_a[-1]["nav"] = nav_a
        if nav_a_before > 0 and br_a.total_cny > 0:
            rows_a[-1]["daily_ret"] = float(rows_a[-1]["daily_ret"]) + (
                nav_a / nav_a_before - 1.0
            )

        prior_b = dict(stock_b)
        stock_b, etf_b, cash_b, nav_b_new, br_b, blocks_b, to_b = _apply_cost_path(
            prior=prior_b,
            target=target_b,
            etf_prior=etf_b,
            etf_target=_etf_tot_b,
            sess=sess,
            tradability=tradability,
            nav=nav_b,
            capital=capital,
            costs=costs,
            prices=px_map,
            etf_px=etf_px,
            min_trade=min_trade,
        )
        nav_b_before = nav_b
        nav_b = nav_b_new
        cost_drag_b = float(nav_b_before - nav_b)
        total_cost_b += br_b.total_cny
        turnovers_b.append(to_b)
        rows_b[-1]["nav"] = nav_b
        rows_b[-1]["cost_drag_today"] = cost_drag_b
        if nav_b_before > 0 and br_b.total_cny > 0:
            rows_b[-1]["daily_ret"] = float(rows_b[-1]["daily_ret"]) + (
                nav_b / nav_b_before - 1.0
            )

        def _cost_row(br, nav_before, nav_after, drag):
            return {
                "session": str(sess),
                "commission_cny": br.commission_cny,
                "slippage_cny": br.slippage_cny,
                "stamp_tax_cny": br.stamp_tax_cny,
                "total_cny": br.total_cny,
                "nav_unit_before": nav_before,
                "nav_unit_after": nav_after,
                "cost_drag_unit_nav": drag,
                "semantics_version": br.semantics_version,
            }

        cost_rows_a.append(_cost_row(br_a, nav_a_before, nav_a, cost_drag_a))
        cost_rows_b.append(_cost_row(br_b, nav_b_before, nav_b, cost_drag_b))

        rebal_log.append(
            {
                "session": str(sess),
                "n_d1_members": len(members),
                "n_scores_a": len(scores_a),
                "n_scores_b": len(scores_b),
                "coverage_a": dict(cov_a),
                "coverage_b": {k: cov_b.get(k) for k in ("M01_12_1", "V01_EP", "turn_20d")},
                "n_names_a": len(stock_a),
                "n_names_b": len(stock_b),
                "method_a": result_a.method,
                "method_b": result_b.method,
                "etf_w": etf_target,
                "book_cap_residual_weight_to_hit_target_beta": book_cap,
                "resid_hit_note": resid_note,
                "implied_portfolio_beta_at_residual_fill": plan.implied_portfolio_beta_at_residual_fill,
                "turnover_a": to_a,
                "turnover_b": to_b,
                "cost_a_cny": br_a.total_cny,
                "cost_b_cny": br_b.total_cny,
                "buy_blocks_a": sum(1 for r in blocks_a.values() if r.startswith("buy_blocked")),
                "buy_blocks_b": sum(1 for r in blocks_b.values() if r.startswith("buy_blocked")),
                "p1_notes_b_sample": list(notes_b)[:8],
                "max_etf_not_raised": True,
                "satellite_off_arm_a": True,
                "arm_b_core_etf_w": plan_b.core_etf_weight,
                "arm_b_satellite_etf_w": plan_b.satellite_etf_weight,
                "arm_b_satellite_code": plan_b.satellite_code,
                "arm_b_satellite_frac": sat_frac_b,
                "arm_b_resid_hit": plan_b.residual_weight_to_hit_target_beta,
                "promotion_approved": False,
            }
        )
        # Release per-rebalance temporaries; keep peak flat on Full D1.
        del scores_a, scores_b, rets_pit, result_a, result_b, target_a, target_b, px_map
        gc.collect()

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
        "title": "Strategy S4/S6 satellite smoke — A no satellite vs B +512100 ETF satellite (frac 0.25 of ETF budget)",
        "satellite_code": SAT_CODE, "max_satellite_frac": SAT_FRAC,
        "avg_satellite_frac_of_etf_b": (sum(sat_frac_log)/len(sat_frac_log)) if sat_frac_log else None,
        "turn_20d": "OFF_both_arms", "main_beta": "sh.510300",
        "promotion_approved": False,
        "research_only": True,
        "not_expected_return": True,
        "not_a_promotion_gate": True,
        "smoke_only": smoke_only,
        "smoke_iteration_note": smoke_note,
        "one_variable": (
            "Alpha integrate: A=P1(M01_12_1,V01_EP); B=P1(M01_12_1,V01_EP,turn_20d) "
            "with turn_20d OLS-residualized vs M01+EP then Gram-Schmidt. "
            "Both: S2 costs+limit/halt + residual_weight_to_hit_target_beta + S1 LW auto."
        ),
        "max_etf_not_raised": True,
        "satellite_default": "OFF (arm B ON for compare)",
        "candidate_pool": candidate_pool,
        "run_tier": run_tier,
        "full_d1": bool(full_d1),
        "weighting_mode": weighting_mode,
        "memory_safe": bool(memory_safe),
        "lean_panel_meta": lean_meta or None,
        "peak_rss_gb_approx_end": round(rss_gb(), 3),
        "lw_rebalance_counts": {
            "arm_a_lw": lw_count_a,
            "arm_a_stub": stub_count_a,
            "arm_b_lw": lw_count_b,
            "arm_b_stub": stub_count_b,
        },
        "factor_ids_a": list(FACTORS_BASELINE),
        "factor_ids_b": list(FACTORS_BASELINE),
        "window": {"start": str(start), "end": str(end)},
        "end_provenance": {
            "resolved_end": str(end),
            "merged_calendar_last_session": str(cal_view.last_session) if cal_view.last_session else None,
            "etf_510300_date_max": str(etf_bundle.date_max) if etf_bundle.date_max else None,
            "d0_panel_merge_cutoff": str(d0_cutoff),
            "extends_past_d0_cutoff": post_d0,
        },
        "cost_knobs": {
            "commission_bps_one_way": costs.commission_bps_one_way,
            "commission_min_cny_per_order": costs.commission_min_cny_per_order,
            "slippage_bps_one_way": costs.slippage_bps_one_way,
            "stamp_tax_sell_only": costs.stamp_tax_sell_only,
            "semantics_version": SEMANTICS_VERSION,
            "capital_cny": capital,
            "min_trade_notional_cny": min_trade,
            "s2_ledger_aligned": True,
        },
        "arm_a_baseline_m01_ep": {
            "metrics_research_only": met_a,
            "total_cost_cny": total_cost_a,
            "total_cost_as_frac_of_capital": total_cost_a / capital if capital else None,
            "output_dir": str(out_a.resolve()),
        },
        "arm_b_plus_satellite": {
            "metrics_research_only": met_b,
            "total_cost_cny": total_cost_b,
            "total_cost_as_frac_of_capital": total_cost_b / capital if capital else None,
            "output_dir": str(out_b.resolve()),
        },
        "delta_b_minus_a": delta,
        "n_trading_sessions": len(sess_in_window),
        "n_rebalances": len(rebal_log),
        "total_zeroed_name_days_both_arms": total_zeroed,
        "panel_cache": cache_stats() if (use_panel_cache or full_d1) else None,

        "memory_knobs": {
            "chunk_size": chunk_size,
            "float32": bool(float32),
            "close_dtype": close_dtype,
            "memory_safe": bool(memory_safe),
            "cache_max_items": cache_max_items,
            "use_disk_cache": bool(use_disk_cache),
            "promotion_approved": False,
        },        "legacy_full_d1_pre_s2_path": str(LEGACY_FULL_D1_PRE_S2.resolve()),
        "legacy_note_zh": (
            "output/strategy_paper_costs/full_d1/ 为 pre-S2 主表（M01+EP factory，"
            "非本 TURN 对照）；本目录为 S2 账本成本 + P1 TURN 对照。"
        ),
        "wall_seconds": round(time.time() - t_wall0, 1),
        "reproduce": (
            "cd /workspace/QuantLab && PYTHONPATH=. /workspace/qlvenv/bin/python "
            "-m quantlab.portfolio.v2_strategy_paper_satellite_compare"
            + (" --full-d1" if full_d1 else "")
        ),
        "output_dir": str(out_root.resolve()),
    }

    df_a.to_csv(out_a / "nav.csv", index=False)
    (out_a / "costs_ledger.csv").write_text(
        pd.DataFrame(cost_rows_a).to_csv(index=False), encoding="utf-8"
    )
    (out_a / "summary.json").write_text(
        json.dumps(
            {
                "path": "A_baseline_m01_ep_costs",
                "promotion_approved": False,
                "smoke_only": smoke_only,
                "metrics_research_only": met_a,
                "total_cost_cny": total_cost_a,
                "window": summary["window"],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    _plot_nav(nav_sa, out_a / "nav.png")

    df_b.to_csv(out_b / "nav.csv", index=False)
    (out_b / "costs_ledger.csv").write_text(
        pd.DataFrame(cost_rows_b).to_csv(index=False), encoding="utf-8"
    )
    (out_b / "summary.json").write_text(
        json.dumps(
            {
                "path": "B_plus_satellite_costs",
                "promotion_approved": False,
                "smoke_only": smoke_only,
                "metrics_research_only": met_b,
                "total_cost_cny": total_cost_b,
                "window": summary["window"],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    _plot_nav(nav_sb, out_b / "nav.png")

    try:
        from quantlab.portfolio.v2_strategy_paper_costs import _plot_overlay

        _plot_overlay(nav_sa, nav_sb, out_root / "nav.png")
    except Exception:
        _plot_nav(nav_sb, out_root / "nav.png")

    (out_root / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (out_root / "rebalance_log.json").write_text(
        json.dumps(rebal_log, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
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
    _write_leo_report_zh(out_root, summary)
    _write_limitations_zh(out_root, summary)

    _write_status(
        out_root,
        {
            "status": "DONE",
            "phase": "complete",
            "full_d1": bool(full_d1),
            "memory_safe": bool(memory_safe),
            "smoke_only": smoke_only,
            "pool": len(pool),
            "run_tier": run_tier,
            "delta": delta,
            "summary": str((out_root / "summary.json").resolve()),
            "leo_report": str((out_root / "LEO_REPORT_ZH.md").resolve()),
        },
    )
    print(
        json.dumps(
            {
                "ok": True,
                "smoke_only": smoke_only,
                "memory_safe": bool(memory_safe),
                "delta": delta,
                "met_a": met_a,
                "met_b": met_b,
                "out": str(out_root),
                "rss_gb": round(rss_gb(), 3),
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    return summary


def _write_leo_report_zh(out: Path, summary: dict) -> None:
    a = summary["arm_a_baseline_m01_ep"]["metrics_research_only"]
    b = summary["arm_b_plus_satellite"]["metrics_research_only"]
    d = summary["delta_b_minus_a"]
    smoke_banner = (
        "**⚠️ 本报告为 smoke pool=250，仅迭代烟测，不是 Full D1 主结论。**\n\n"
        if summary.get("smoke_only")
        else "**Full D1 主结论口径（研究级）。**\n\n"
    )
    lw = summary.get("lw_rebalance_counts") or {}
    text = f"""# Leo 短报 — TURN 对照（成本+βc+LW）

**promotion_approved=false。数字仅作研究，不是预期收益 / 不是晋升。**
卫星默认关。**不抬 max_etf**。

{smoke_banner}## 对照设定（单变量 = TURN）

| 臂 | Alpha | 共用 |
|----|-------|------|
| **A** | P1 integrate `M01_12_1` + `V01_EP` | S2 成本+涨跌停；`residual_weight_to_hit_target_beta`；S1 LW(auto) |
| **B** | P1 + **`turn_20d`**（对 M01/EP OLS 残差后再 Gram-Schmidt） | 同上 |

## 关键数字

| 项 | A 基线 M01+EP（有成本） | B +TURN（有成本） | Δ (B−A) |
|----|------------------------|-------------------|---------|
| 区间 | {a.get('date_start')} → {a.get('date_end')} | 同左 | — |
| 交易日 / 再平衡 | {a.get('n_days')} / {a.get('n_rebalances')} | {b.get('n_days')} / {b.get('n_rebalances')} | — |
| 累计收益 | {_pct(a.get('total_return'))} | {_pct(b.get('total_return'))} | {_pct(d.get('total_return'))} |
| 年化 CAGR | {_pct(a.get('cagr'))} | {_pct(b.get('cagr'))} | {_pct(d.get('cagr'))} |
| 夏普 Sharpe (rf=0) | {_num(a.get('sharpe_rf0'))} | {_num(b.get('sharpe_rf0'))} | {_num(d.get('sharpe_rf0'))} |
| 最大回撤 | {_pct(a.get('max_drawdown'))} | {_pct(b.get('max_drawdown'))} | {_pct(d.get('max_drawdown'))} |
| 年化波动 | {_pct(a.get('ann_vol'))} | {_pct(b.get('ann_vol'))} | {_pct(d.get('ann_vol'))} |

## 成本 / LW

- A 累计成本：{summary['arm_a_baseline_m01_ep'].get('total_cost_cny'):.2f} CNY（{_pct(summary['arm_a_baseline_m01_ep'].get('total_cost_as_frac_of_capital'))} 本金）
- B 累计成本：{summary['arm_b_plus_satellite'].get('total_cost_cny'):.2f} CNY（{_pct(summary['arm_b_plus_satellite'].get('total_cost_as_frac_of_capital'))} 本金）
- LW 再平衡次数：A lw={lw.get('arm_a_lw')} / stub={lw.get('arm_a_stub')}；B lw={lw.get('arm_b_lw')} / stub={lw.get('arm_b_stub')}
- S2 semantics：`{summary['cost_knobs'].get('semantics_version')}`

## 与 pre-S2 Full D1 主表的关系

- 旧主表（pre-S2、factory M01+EP、无 TURN）：`{summary.get('legacy_full_d1_pre_s2_path')}`
- {summary.get('legacy_note_zh')}

## 路径

- 根目录：`{out}`
- A：`{out / 'arm_a_baseline_m01_ep'}`
- B：`{out / 'arm_b_plus_turn'}`
- `summary.json` / `nav.csv` / `rebalance_log.json`

## 复现

```bash
{summary.get('reproduce')}
```

## 一句话

有成本+β目标残差+LW 下，看 **+turn_20d** 相对 M01+EP 基线是否改善；不可晋升。{" smoke≠主结论。" if summary.get("smoke_only") else ""}
"""
    (out / "LEO_REPORT_ZH.md").write_text(text, encoding="utf-8")


def _write_limitations_zh(out: Path, summary: dict) -> None:
    text = f"""# 局限 — TURN 对照（研究级）

**promotion_approved=false。**

- 单变量：turn_20d 是否进入 P1 integrate；两臂均有成本 / 涨跌停 / residual-beta-c / LW(auto)
- smoke_only={summary.get('smoke_only')}；pool={summary.get('candidate_pool')}
- EP asof 陈旧；SW_L1/财务过程可用但结果不可晋升
- 卫星 OFF；不抬 max_etf
- LW 不足历史时回退等权 stub（见 lw_rebalance_counts）
- pre-S2 Full D1 旧表见 legacy 路径，勿与本对照混报
- 墙钟约 {summary.get('wall_seconds')}s
"""
    (out / "LIMITATIONS_ZH.md").write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    import argparse

    ap = argparse.ArgumentParser(description="Strategy TURN compare (research costs)")
    ap.add_argument("--full-d1", action="store_true")
    ap.add_argument("--pool", type=int, default=CANDIDATE_POOL)
    ap.add_argument("--out", type=str, default=None)
    ap.add_argument("--panel-cache", action="store_true")
    ap.add_argument(
        "--memory-safe",
        action="store_true",
        default=False,
        help="Lean close+turnover pass; no long-frame cache (default ON for --full-d1)",
    )
    ap.add_argument(
        "--no-memory-safe",
        action="store_true",
        default=False,
        help="Force legacy preload (may OOM on Full D1)",
    )
    ap.add_argument(
        "--pool-cap",
        type=int,
        default=None,
        help="Cap universe size (mid-tier NOT-main if set with --full-d1)",
    )
    ap.add_argument(
        "--chunk-size",
        type=int,
        default=None,
        help="Lean GC / close chunk size (Full D1 default 300)",
    )
    ap.add_argument(
        "--float32",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="float32 closes/returns (default on)",
    )
    ap.add_argument(
        "--cache-max-items",
        type=int,
        default=400,
        help="LRU max when not memory-safe (0=unbounded; avoid on Full D1)",
    )
    ap.add_argument(
        "--disk-cache",
        action="store_true",
        help="feather cache for non-lean merged_close_panel",
    )
    ap.add_argument(
        "--weighting-mode",
        type=str,
        default="auto",
        choices=("auto", "lw_target_vol", "equal_stub"),
    )
    ns = ap.parse_args(argv)
    mem = None
    if ns.no_memory_safe:
        mem = False
    elif ns.memory_safe or ns.full_d1:
        mem = True
    cache_max = None if int(ns.cache_max_items) <= 0 else int(ns.cache_max_items)
    run_turn_compare(
        candidate_pool=None if ns.full_d1 else ns.pool,
        full_d1=bool(ns.full_d1),
        out_root=Path(ns.out) if ns.out else None,
        use_panel_cache=bool(ns.panel_cache) and not bool(ns.full_d1),
        weighting_mode=str(ns.weighting_mode),
        memory_safe=mem,
        pool_cap=ns.pool_cap,
        chunk_size=ns.chunk_size,
        float32=bool(ns.float32),
        cache_max_items=cache_max,
        use_disk_cache=bool(ns.disk_cache),
    )


if __name__ == "__main__":
    main()
