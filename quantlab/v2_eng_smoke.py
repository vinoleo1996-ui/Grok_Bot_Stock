"""Unified V2 Eng research smoke — universe funnel + Beta idle + min factors.

Research-only::

  promotion_approved = false
  sw_l1_dataset may be True (tushare); overall promotion_approved=false
  financials_pit_promotable = dataset-level (accepted tushare default)
  IC/ICIR = process_metric_only (never a promotion gate)

Run::

    PYTHONPATH=. python -m quantlab.v2_eng_smoke
    PYTHONPATH=. python -m quantlab.cli v2-eng-smoke --max-instruments 80
"""
from __future__ import annotations

from quantlab.promotion_gate import overall_promotion_approved as _gate

import json
import sys
from datetime import date
from pathlib import Path


DEFAULT_MID_SESSION = date(2026, 6, 30)
DEFAULT_LATE_SESSION = date(2026, 10, 9)


def _md_table(headers: list[str], rows: list[list[object]]) -> str:
    head = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join("" if c is None else str(c) for c in r) + " |" for r in rows]
    return "\n".join([head, sep, *body])


def _funnel_block(result) -> dict:
    """Filter funnel + member sample from D1MaskResult."""
    frame = result.frame
    src_counts: dict[str, int] = {}
    if not frame.empty and "float_mktcap_source" in frame.columns:
        src_counts = {str(k): int(v) for k, v in frame["float_mktcap_source"].value_counts().items()}
    u30_waived = int(frame["u30_waived_amount_gap"].sum()) if (
        not frame.empty and "u30_waived_amount_gap" in frame.columns
    ) else 0
    sample = []
    if not frame.empty:
        for _, r in frame.head(8).iterrows():
            sample.append(
                {
                    "instrument_id": str(r["instrument_id"]),
                    "listing_trading_days": r.get("listing_trading_days"),
                    "median_amount_20d": r.get("median_amount_20d"),
                    "float_mktcap": r.get("float_mktcap"),
                    "float_mktcap_source": r.get("float_mktcap_source"),
                    "suspended": bool(r.get("suspended", False)),
                    "limit_up_buy_block": bool(r.get("limit_up_buy_block", False)),
                    "limit_down_sell_block": bool(r.get("limit_down_sell_block", False)),
                    "u30_waived_amount_gap": bool(r.get("u30_waived_amount_gap", False)),
                    "industry_sw_l1_code": r.get("industry_sw_l1_code"),
                }
            )
    return {
        "session": str(result.session),
        "float_mktcap_source_primary": result.float_mktcap_source,
        "float_mktcap_source_counts": src_counts,
        "u30_waived_amount_gap": u30_waived,
        "funnel": {
            "n_instruments_in": result.n_instruments_in,
            "n_after_listing_ge_120": result.n_after_listing,
            "n_after_tradable_not_st": result.n_after_tradable_st,
            "n_after_u30": result.n_after_u30,
            "n_after_limit_up_buy_block": result.n_after_limits,
            "n_after_mktcap_kick_bottom_30pct": result.n_after_mktcap,
            "member_count": len(result.member_ids),
        },
        "member_sample": sample,
        "promotion_approved": bool(result.promotion_approved),
        "sw_l1_promotable": bool(result.sw_l1_promotable),
        "notes_head": list(result.notes[:10]),
    }


def _beta_block(plan, bars_on_session: int) -> dict:
    return {
        "session": str(plan.session),
        "benchmark_etf": plan.benchmark_etf,
        "benchmark_etf_instrument_id": plan.benchmark_etf_instrument_id,
        "etf_source": "data/v2/etf_510300",
        "etf_sleeve_weight": plan.etf_sleeve_weight,
        "cash_weight": plan.cash_weight,
        "residual_book_weight_cap": plan.residual_book_weight_cap,
        "max_etf_sleeve_weight": plan.max_etf_sleeve_weight,
        "bars_on_session": bars_on_session,
        "etf_panel_available": plan.etf_panel_available,
        "index_bars_available": plan.index_bars_available,
        "vol_target_applied": False,
        "promotion_approved": False,
        "note": "idle/empty-run research weights — not optimized, not backtested",
        "todos_head": list(plan.todos[:8]),
    }


def _factor_block(pipe) -> dict:
    ic_rows = []
    for s in pipe.ic_summaries:
        ic_rows.append(
            {
                "factor_id": s.factor_id,
                "n_sessions": s.n_sessions,
                "ic_mean": s.ic_mean,
                "ic_std": s.ic_std,
                "icir": s.icir,
                "process_metric_only": True,
                "promotion_approved": False,
            }
        )
    return {
        "session": str(pipe.session),
        "universe_used": len(pipe.universe_ids),
        "max_instruments": pipe.max_instruments,
        "momentum_M01_12_1_coverage": len(pipe.momentum_raw),
        "momentum_3m_coverage": len(pipe.momentum_3m_raw),
        "ep_V01_coverage": pipe.ep_coverage,
        "ep_negative_flagged": pipe.ep_negative_flagged,
        "financials_metric_used": pipe.financials_metric_used,
        "financials_path": pipe.financials_path,
        "financials_promotable": False,
        "mktcap_source_counts": dict(pipe.mktcap_source_counts),
        "ic_process_metrics": ic_rows,
        "promotion_approved": False,
        "notes_head": list(pipe.notes[:10]),
    }


def run_eng_smoke(
    mandate_path: str | None = None,
    d0_root: str | None = None,
    *,
    session: str | None = None,
    late_session: str | None = None,
    max_instruments: int = 80,
    factor_max_instruments: int | None = None,
    ic_lookback_sessions: int = 12,
    forward_horizon: int = 5,
    skip_factors: bool = False,
) -> dict:
    from dataclasses import replace

    from quantlab.beta import PrototypeBetaSleeveProvider
    from quantlab.data.v2_readers import (
        default_v2_roots,
        load_asof_extend_meta,
        load_ep_research,
        load_etf_510300,
        load_financials_pit,
        load_float_mktcap_asof,
        load_float_mktcap_daily,
        load_merged_calendar,
        load_sw_l1_members,
        resolve_d0_asof_cutoff,
    )
    from quantlab.mandate_v2 import load_mandate_v2
    from quantlab.universe.d1_masks import D1MaskConfig, build_d1_masks_for_session

    mandate = load_mandate_v2(mandate_path)
    mandate.require_not_promoted()
    if bool(mandate.promotion_approved) != _gate():
        raise RuntimeError("smoke_fail:mandate_promotion_gate_mismatch")

    roots = default_v2_roots()
    if d0_root:
        roots = replace(roots, d0_root=Path(d0_root))

    sw = load_sw_l1_members(roots=roots)
    # Accepted tushare SW dataset may carry dataset-level promotion flags from
    # Data acceptance; overall strategy promotion_approved stays False.
    if sw.source_variant != "tushare":
        if sw.promotable or sw.promotion_approved:
            raise RuntimeError("smoke_fail:non_tushare_sw_l1_must_not_be_promotable")
    if sw.available_at_nulls != 0:
        raise RuntimeError("smoke_fail:sw_l1_available_at_nulls")
    fm = load_float_mktcap_asof(roots=roots)
    try:
        # session-filtered read: tushare default is 9.7M rows (memory-safe smoke)
        fm_daily = load_float_mktcap_daily(roots=roots, session=date(2026, 10, 9))
    except FileNotFoundError:
        fm_daily = None
    try:
        ep_res = load_ep_research(roots=roots, session=date(2026, 10, 9))
    except FileNotFoundError:
        ep_res = None
    etf = load_etf_510300(roots=roots)
    extend = load_asof_extend_meta(roots=roots)
    cutoff = resolve_d0_asof_cutoff(roots=roots)
    cal = load_merged_calendar(roots=roots)
    fin = load_financials_pit(roots=roots)
    if fin.source_variant != "tushare" or not fin.promotable or "financials_pit_tushare" not in fin.path:
        raise RuntimeError("smoke_fail:financials_default_not_accepted_tushare")
    if ep_res is None or ep_res.source_variant != "tushare" or not ep_res.promotable:
        raise RuntimeError("smoke_fail:ep_default_not_accepted_tushare")
    if "ep_pit_daily_tushare" not in ep_res.path:
        raise RuntimeError("smoke_fail:ep_default_not_pit_daily_tushare")
    for _s in (date(2025, 6, 30), date(2026, 6, 30), date(2026, 7, 15)):
        _ep_mid = load_ep_research(roots=roots, session=_s)
        if "ep_pit_daily_tushare" not in _ep_mid.path or not _ep_mid.promotable or _ep_mid.session > _s:
            raise RuntimeError(f"smoke_fail:ep_pit_daily_not_default:{_s}")
        _fr = _ep_mid.frame[_ep_mid.frame["ep"].notna()]
        _av = _fr["available_at"].dt.tz_convert("Asia/Shanghai").dt.date
        if (_av >= _s).any():
            raise RuntimeError(f"smoke_fail:ep_lookahead:{_s}")
    _ocf = fin.frame[fin.frame["metric"] == "ocf_to_profit"]
    if _ocf.empty or set(_ocf["source"].unique()) != {"ocf_to_profit_pit_tushare"}:
        raise RuntimeError("smoke_fail:ocf_to_profit_not_tushare_pit")
    from quantlab.data.v2_readers import load_dividends, load_financials_available_at

    fin_at = load_financials_available_at(roots=roots)
    # timing-only index (Data corrected acceptance 2026-10-10 21:32 ET: superseded by
    # financials_pit_tushare for values) — require tushare variant, not acceptance.
    if fin_at.source_variant != "tushare":
        raise RuntimeError("smoke_fail:financials_available_at_default_not_tushare")
    div = load_dividends(roots=roots)
    if not div.promotable or div.n_rows < 1:
        raise RuntimeError("smoke_fail:dividend_default_not_accepted")
    if fm_daily is not None and not fm_daily.promotion_approved:
        raise RuntimeError("smoke_fail:float_mktcap_daily_default_not_accepted_tushare")
    print(f"[eng_smoke] accepted defaults: float={fm_daily.path if fm_daily else None} rows@1009={fm_daily.n_rows if fm_daily else 0}; "
          f"fin_at={fin_at.path} n={fin_at.n_rows}; div={div.path} n={div.n_rows}; extend={roots.asof_extend_dir}")

    # Mid/late are fixed control sessions — do not derive mid from asof (asof may be 10-09).
    mid = date.fromisoformat(session) if session else DEFAULT_MID_SESSION
    late = date.fromisoformat(late_session) if late_session else DEFAULT_LATE_SESSION

    u = mandate.universe
    cfg = D1MaskConfig(
        listing_min_trading_days=u.listing_min_trading_days,
        exclude_bottom_mktcap_pct=u.microcap_policy.exclude_bottom_mktcap_pct,
        liquidity_threshold_cny=u.liquidity_rule.threshold_cny_active,
        open_status_mode="research",
        waive_u30_on_amount_gap=True,
    )

    funnel_by_session: dict[str, dict] = {}
    mask_results = {}
    for sess in (mid, late):
        result = build_d1_masks_for_session(
            sess,
            d0_root=roots.d0_root,
            asof_extend_dir=roots.asof_extend_dir,
            config=cfg,
            max_instruments=max_instruments,
            sw_l1_path=roots.sw_l1_path,
            float_mktcap_path=roots.float_mktcap_path,
        )
        if bool(result.promotion_approved) != _gate():
            raise RuntimeError(f"smoke_fail:mask_overall_promotion_gate_mismatch:{sess}")
        mask_results[sess] = result
        funnel_by_session[str(sess)] = _funnel_block(result)

    beta = PrototypeBetaSleeveProvider(mandate, d0_root=roots.d0_root)
    beta_by_session: dict[str, dict] = {}
    for sess in (mid, late):
        plan = beta.plan(sess)
        bars = beta.load_etf_bars(sess, sess)
        if plan.promotion_approved:
            raise RuntimeError(f"smoke_fail:beta_promotion_leak:{sess}")
        if len(bars) < 1:
            raise RuntimeError(f"smoke_fail:etf_510300_missing_bar:{sess}")
        beta_by_session[str(sess)] = _beta_block(plan, len(bars))

    factors_by_session: dict[str, dict] = {}
    markdown_parts: list[str] = []

    # --- markdown: funnel ---
    md_funnel_rows = []
    for sid, block in funnel_by_session.items():
        f = block["funnel"]
        md_funnel_rows.append(
            [
                sid,
                f["n_instruments_in"],
                f["n_after_listing_ge_120"],
                f["n_after_tradable_not_st"],
                f["n_after_u30"],
                f["n_after_limit_up_buy_block"],
                f["n_after_mktcap_kick_bottom_30pct"],
                block["float_mktcap_source_primary"],
                block["u30_waived_amount_gap"],
            ]
        )
    markdown_parts.append("### Tradable-universe filter funnel (research)")
    markdown_parts.append(
        _md_table(
            [
                "session",
                "in",
                "listing>=120",
                "tradable!~ST",
                "U30",
                "!~limit_up_buy",
                "!~bottom30%mktcap",
                "mktcap_src",
                "u30_waived",
            ],
            md_funnel_rows,
        )
    )
    markdown_parts.append("")
    markdown_parts.append(f"promotion_approved=false · sw_l1_dataset_promotable={bool(sw.promotable)} · variant={sw.source_variant} · max_instruments={max_instruments}")
    markdown_parts.append(f"panel_merge: d0[session<={cutoff}]+extend[session>{cutoff}] (1c85 untouched)")

    # member sample mid
    mid_sample = funnel_by_session[str(mid)]["member_sample"]
    if mid_sample:
        markdown_parts.append("")
        markdown_parts.append(f"### Member sample ({mid})")
        markdown_parts.append(
            _md_table(
                [
                    "instrument_id",
                    "listing_days",
                    "med_amt_20d",
                    "float_mktcap",
                    "mktcap_src",
                    "susp",
                    "lim_up",
                    "sw_l1",
                ],
                [
                    [
                        r["instrument_id"],
                        r["listing_trading_days"],
                        None if r["median_amount_20d"] is None else f"{r['median_amount_20d']:.3g}",
                        None if r["float_mktcap"] is None else f"{r['float_mktcap']:.3g}",
                        r["float_mktcap_source"],
                        r["suspended"],
                        r["limit_up_buy_block"],
                        r["industry_sw_l1_code"],
                    ]
                    for r in mid_sample
                ],
            )
        )

    # beta table
    markdown_parts.append("")
    markdown_parts.append("### Beta sleeve idle weights (510300)")
    markdown_parts.append(
        _md_table(
            [
                "session",
                "etf_w",
                "cash_w",
                "residual_cap",
                "max_etf",
                "bars_on_session",
                "etf_source",
                "promotion_approved",
            ],
            [
                [
                    sid,
                    b["etf_sleeve_weight"],
                    b["cash_weight"],
                    b["residual_book_weight_cap"],
                    b["max_etf_sleeve_weight"],
                    b["bars_on_session"],
                    b["etf_source"],
                    False,
                ]
                for sid, b in beta_by_session.items()
            ],
        )
    )

    if not skip_factors:
        from quantlab.factors.v2_min_pipeline import run_v2_min_pipeline

        fmax = factor_max_instruments if factor_max_instruments is not None else max_instruments
        # Prefer mid session (has denser amount/float); also run late if members exist
        for sess in (mid, late):
            mres = mask_results[sess]
            if not mres.member_ids:
                factors_by_session[str(sess)] = {
                    "session": str(sess),
                    "skipped": True,
                    "reason": "empty_mask_members",
                    "promotion_approved": False,
                }
                continue
            fm_map = {}
            src_map = {}
            if not mres.frame.empty:
                for _, r in mres.frame.iterrows():
                    iid = str(r["instrument_id"])
                    if r.get("float_mktcap") is not None and pd_notna(r.get("float_mktcap")):
                        fm_map[iid] = float(r["float_mktcap"])
                    src_map[iid] = str(r.get("float_mktcap_source") or "none")
            pipe = run_v2_min_pipeline(
                sess,
                mres.member_ids,
                fm_map,
                d0_root=roots.d0_root,
                asof_extend_dir=roots.asof_extend_dir,
                max_instruments=fmax,
                ic_lookback_sessions=ic_lookback_sessions,
                forward_horizon=forward_horizon,
                mktcap_source_by_id=src_map,
            )
            if pipe.promotion_approved or pipe.financials_promotable:
                raise RuntimeError(f"smoke_fail:factor_promotion_leak:{sess}")
            factors_by_session[str(sess)] = _factor_block(pipe)

        markdown_parts.append("")
        markdown_parts.append(
            "### Factor process metrics (IC/ICIR) — process_metric_only=true, NOT a promotion gate"
        )
        ic_md = []
        for sid, fb in factors_by_session.items():
            if fb.get("skipped"):
                continue
            for row in fb.get("ic_process_metrics") or []:
                ic_md.append(
                    [
                        sid,
                        row["factor_id"],
                        row["n_sessions"],
                        None if row["ic_mean"] is None else f"{row['ic_mean']:.4f}",
                        None if row["ic_std"] is None else f"{row['ic_std']:.4f}",
                        None if row["icir"] is None else f"{row['icir']:.4f}",
                        True,
                        False,
                    ]
                )
        if ic_md:
            markdown_parts.append(
                _md_table(
                    [
                        "session_anchor",
                        "factor_id",
                        "n_ic_sessions",
                        "ic_mean",
                        "ic_std",
                        "icir",
                        "process_metric_only",
                        "promotion_approved",
                    ],
                    ic_md,
                )
            )
        cov_rows = []
        for sid, fb in factors_by_session.items():
            if fb.get("skipped"):
                continue
            cov_rows.append(
                [
                    sid,
                    fb.get("momentum_M01_12_1_coverage"),
                    fb.get("ep_V01_coverage"),
                    fb.get("ep_negative_flagged"),
                    fb.get("financials_metric_used"),
                    False,
                ]
            )
        if cov_rows:
            markdown_parts.append("")
            markdown_parts.append("### Factor coverage")
            markdown_parts.append(
                _md_table(
                    [
                        "session",
                        "M01_12_1_n",
                        "V01_EP_n",
                        "neg_E_flagged",
                        "ep_metric",
                        "fin_promotable",
                    ],
                    cov_rows,
                )
            )

    status = {
        "ok": True,
        "phase": "0_eng_smoke_universe_beta_factors",
        "promotion_approved": _gate(),
        "promotion_gate": __import__("quantlab.promotion_gate", fromlist=["gate_status"]).gate_status(),
        "sw_l1_promotable": bool(sw.promotable),
        "sw_l1_dataset_promotion_approved": bool(sw.promotion_approved),
        "sw_l1_source_variant": sw.source_variant,
        "financials_pit_promotable": bool(fin.promotable),
        "financials_pit_source_variant": fin.source_variant,
        "ep_source_variant": None if ep_res is None else ep_res.source_variant,
        "ep_dataset_accepted": None if ep_res is None else bool(ep_res.promotable),
        "process_metric_only": True,
        "mandate_id": mandate.mandate_id,
        "sessions": [str(mid), str(late)],
        "d0_asof_cutoff": str(cutoff),
        "max_instruments": max_instruments,
        "merge_rule": f"d0[session<={cutoff}]+extend[session>{cutoff}]",
        "roots": roots.as_dict(),
        "data_probe": {
            "sw_l1_n_rows": sw.n_rows,
            "sw_l1_path": sw.path,
            "sw_l1_source_variant": sw.source_variant,
            "sw_l1_quality_label": sw.quality_label,
            "float_mktcap_asof_non_null": fm.n_non_null,
            "float_mktcap_asof_session": str(fm.session) if fm.session else None,
            "float_mktcap_daily_rows": None if fm_daily is None else fm_daily.n_rows,
            "float_mktcap_daily_session_max": None if fm_daily is None else str(fm_daily.session_max),
            "ep_path": None if ep_res is None else ep_res.path,
            "financials_path": fin.path,
            "ep_research_n_rows": None if ep_res is None else ep_res.n_rows,
            "ep_research_n_sane": None if ep_res is None else ep_res.n_ep_sane,
            "ep_research_session": None if ep_res is None else str(ep_res.session),
            "etf_n_bars": etf.n_bars,
            "asof_extend_calendar_max": str(extend.calendar_max),
            "merged_calendar_last": str(cal.last_session),
            "financials_n_rows": fin.n_rows,
            "financials_metrics": list(fin.metrics),
            "financials_quality_label": fin.quality_label,
        },
        "universe_funnel": funnel_by_session,
        "beta_idle_weights": beta_by_session,
        "factors": factors_by_session,
        "sample_tables_markdown": "\n".join(markdown_parts),
        "blockers": [
            "SW_L1 tushare dataset may be promotion-grade; overall still not accepted",
            "financials PIT + EP default = accepted tushare (dataset-level); EP=ep_pit_daily_tushare, ocf_to_profit=ocf_to_profit_pit_tushare; factor outputs research-grade",
            "float_mktcap daily late-session coverage is seed-subset (~955 on 2026-10-09)",
            "asof_extend amount/limit/ST only ~50/5201 panels filled → U30 research waive",
            "Beta idle weights only — no vol-target yet",
            "IC/ICIR are process metrics only — never a promotion gate",
            f"sampled max_instruments={max_instruments} (full universe slow)",
            "promotion_approved=false everywhere",
        ],
        "note": (
            "Eng smoke only — funnel counts, idle Beta weights, momentum+EP process IC; "
            "no Sharpe/PnL promotion narrative; promotion_approved=false"
        ),
    }

    # Hard gates
    for sid, b in beta_by_session.items():
        if b["bars_on_session"] < 1:
            status["ok"] = False
            status["error"] = f"beta_gate_fail:{sid}"
    for sid, block in funnel_by_session.items():
        if block["promotion_approved"] != _gate():
            status["ok"] = False
            status["error"] = f"mask_gate_fail:{sid}"
    return status


def pd_notna(value: object) -> bool:
    try:
        import pandas as pd

        return bool(pd.notna(value))
    except Exception:
        return value is not None


def main(argv: list[str] | None = None) -> int:
    import argparse

    p = argparse.ArgumentParser(prog="quantlab.v2_eng_smoke")
    p.add_argument("--mandate", default=None)
    p.add_argument("--d0-root", default=None)
    p.add_argument("--session", default=None, help="mid session YYYY-MM-DD (default 2026-06-30)")
    p.add_argument("--late-session", default=None, help="late session YYYY-MM-DD (default 2026-10-09)")
    p.add_argument("--max-instruments", type=int, default=80)
    p.add_argument("--factor-max-instruments", type=int, default=None)
    p.add_argument("--ic-lookback-sessions", type=int, default=12)
    p.add_argument("--forward-horizon", type=int, default=5)
    p.add_argument("--skip-factors", action="store_true")
    p.add_argument("--markdown-only", action="store_true", help="print sample tables markdown only")
    args = p.parse_args(argv)
    try:
        status = run_eng_smoke(
            mandate_path=args.mandate,
            d0_root=args.d0_root,
            session=args.session,
            late_session=args.late_session,
            max_instruments=args.max_instruments,
            factor_max_instruments=args.factor_max_instruments,
            ic_lookback_sessions=args.ic_lookback_sessions,
            forward_horizon=args.forward_horizon,
            skip_factors=args.skip_factors,
        )
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": f"{type(exc).__name__}:{exc}"}, ensure_ascii=False, indent=2))
        return 1
    if args.markdown_only:
        print(status.get("sample_tables_markdown") or "")
    else:
        print(json.dumps(status, ensure_ascii=False, indent=2, default=str))
        print("\n----- SAMPLE TABLES (markdown) -----\n")
        print(status.get("sample_tables_markdown") or "")
    return 0 if status.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
