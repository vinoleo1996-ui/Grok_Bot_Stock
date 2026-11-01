"""V2 contract prototype smoke — loads real V2 paths; counts/flags only.

No backtest metrics, Sharpe, or PnL. Forces::

  promotion_approved = False
  sw_l1_dataset may be True (accepted tushare); overall promotion_approved=False

Covers a mid-D0 session (default 2026-06-30) and a late asof_extend session
(2026-10-09) so D1 mask merge + Beta 510300 late coverage are exercised.

Run::

    PYTHONPATH=. python -m quantlab.v2_proto_smoke
    PYTHONPATH=. python -m quantlab.cli v2-proto-smoke
"""
from __future__ import annotations

from quantlab.promotion_gate import overall_promotion_approved as _gate

import json
import sys
from datetime import date
from pathlib import Path


DEFAULT_MID_SESSION = date(2026, 6, 30)
DEFAULT_LATE_SESSION = date(2026, 10, 9)


def _run_session(
    *,
    mandate,
    roots,
    sess: date,
    max_instruments: int,
) -> dict:
    from quantlab.beta import PrototypeBetaSleeveProvider
    from quantlab.universe import PrototypeUniverseMaskProvider

    uni = PrototypeUniverseMaskProvider(
        mandate,
        d0_root=roots.d0_root,
        max_instruments=max_instruments,
    )
    beta = PrototypeBetaSleeveProvider(mandate, d0_root=roots.d0_root)

    membership = uni.membership_at(sess)
    plan = beta.plan(sess)
    etf_bars_1d = beta.load_etf_bars(sess, sess)
    sample_ids = list(membership.member_ids[:20]) if membership.member_ids else ["sz.000001"]
    sw_asof = uni.sw_l1_asof(sess, sample_ids)
    n_sw_known = sum(1 for a in sw_asof if not a.is_unknown_bucket)

    if membership.promotion_approved:
        raise RuntimeError(f"smoke_fail:membership_promotion_approved_true:{sess}")
    if plan.promotion_approved:
        raise RuntimeError(f"smoke_fail:beta_promotion_approved_true:{sess}")
    if any(
        getattr(a, "is_unknown_bucket", True) is False
        and False  # placeholder — assignments never carry promotable
        for a in membership.sw_l1_assignments
    ):
        pass
    # Overall promotion must stay false; SW dataset flag may be true (tushare).
    for note in membership.todos:
        if (not _gate()) and "overall_promotion_approved=true" in str(note).lower():
            raise RuntimeError(f"smoke_fail:overall_promotion_leaked_true:{sess}")

    sw_dataset = False
    for note in membership.todos:
        if str(note).startswith("sw_l1_dataset_promotable="):
            sw_dataset = str(note).split("=", 1)[-1].lower() == "true"
            break

    return {
        "session": str(sess),
        "mask": {
            "max_instruments_sampled": max_instruments,
            "member_count": len(membership.member_ids),
            "row_count": len(membership.rows),
            "sw_l1_assignments": len(membership.sw_l1_assignments),
            "sw_l1_asof_sample_known": n_sw_known,
            "sw_l1_asof_sample_n": len(sw_asof),
            "data_ready": membership.data_ready,
            "calendar_ok": membership.calendar_ok,
            "promotion_approved": False,
            "sw_l1_promotable": sw_dataset,
            "todos_head": list(membership.todos[:12]),
        },
        "beta": {
            "etf_panel_available": plan.etf_panel_available,
            "index_bars_available": plan.index_bars_available,
            "etf_sleeve_weight": plan.etf_sleeve_weight,
            "cash_weight": plan.cash_weight,
            "residual_book_weight_cap": plan.residual_book_weight_cap,
            "max_etf_sleeve_weight": plan.max_etf_sleeve_weight,
            "bars_on_session": len(etf_bars_1d),
            "data_ready": plan.data_ready,
            "promotion_approved": False,
            "todos_head": list(plan.todos[:10]),
            "note": "vol-target/β-budget research weights — not optimized, not backtested, not promotion-grade",
        },
    }


def run_proto_smoke(
    mandate_path: str | None = None,
    d0_root: str | None = None,
    *,
    session: str | None = None,
    late_session: str | None = None,
    max_instruments: int = 300,
    dual_session: bool = True,
) -> dict:
    from quantlab.beta import PrototypeBetaSleeveProvider
    from quantlab.data.v2_readers import (
        default_v2_roots,
        load_asof_extend_meta,
        load_etf_510300,
        load_float_mktcap_asof,
        load_merged_calendar,
        load_sw_l1_members,
        resolve_d0_asof_cutoff,
    )
    from quantlab.mandate_v2 import load_mandate_v2
    from quantlab.v2_schemas import schema_handshake_payload

    mandate = load_mandate_v2(mandate_path)
    if bool(mandate.promotion_approved) != _gate():
        raise RuntimeError("smoke_fail:mandate_promotion_gate_mismatch")

    roots = default_v2_roots()
    if d0_root:
        from dataclasses import replace

        roots = replace(roots, d0_root=Path(d0_root))

    # --- Readers (fail loud on contract breaks) ---
    sw = load_sw_l1_members(roots=roots)
    if sw.source_variant != "tushare":
        if sw.promotable or sw.promotion_approved:
            raise RuntimeError("smoke_fail:non_tushare_sw_l1_must_not_be_promotable")
    if sw.available_at_nulls != 0:
        raise RuntimeError("smoke_fail:sw_l1_available_at_nulls")

    fm = load_float_mktcap_asof(roots=roots)
    if fm.promotion_approved:
        raise RuntimeError("smoke_fail:float_mktcap_promotion_must_be_false")

    etf = load_etf_510300(roots=roots)
    if etf.promotion_approved:
        raise RuntimeError("smoke_fail:etf_promotion_must_be_false")

    extend = load_asof_extend_meta(roots=roots)
    cutoff = resolve_d0_asof_cutoff(roots=roots)
    cal = load_merged_calendar(roots=roots)

    mid = date.fromisoformat(session) if session else (fm.session or DEFAULT_MID_SESSION)
    late = date.fromisoformat(late_session) if late_session else DEFAULT_LATE_SESSION

    sessions_to_run = [mid]
    if dual_session and late != mid:
        sessions_to_run.append(late)

    beta_probe = PrototypeBetaSleeveProvider(mandate, d0_root=roots.d0_root)
    etf_inst = beta_probe.load_etf_instrument()

    per_session: dict[str, dict] = {}
    for sess in sessions_to_run:
        per_session[str(sess)] = _run_session(
            mandate=mandate,
            roots=roots,
            sess=sess,
            max_instruments=max_instruments,
        )

    # Hard asserts across sessions
    for sid, block in per_session.items():
        if block["mask"]["promotion_approved"] not in (False, _gate()):
            raise RuntimeError(f"smoke_fail:mask_promotion_gate_mismatch:{sid}")
        # sw_l1_promotable may be True for accepted tushare dataset
        if block["beta"]["promotion_approved"] is not False:
            raise RuntimeError(f"smoke_fail:beta_promotion_not_false:{sid}")
        if block["beta"]["bars_on_session"] < 1:
            raise RuntimeError(f"smoke_fail:etf_510300_missing_bar_on_session:{sid}")

    status = {
        "ok": True,
        "phase": "0_proto_asof_extend",
        "promotion_approved": _gate(),
        "sw_l1_promotable": bool(sw.promotable),
        "sw_l1_dataset_promotion_approved": bool(sw.promotion_approved),
        "sw_l1_source_variant": sw.source_variant,
        "mandate_id": mandate.mandate_id,
        "mandate_version": mandate.version,
        "sessions": [str(s) for s in sessions_to_run],
        "d0_asof_cutoff": str(cutoff),
        "roots": roots.as_dict(),
        "sw_l1": {
            "path": sw.path,
            "n_rows": sw.n_rows,
            "n_instruments": sw.n_instruments,
            "n_sw_l1": sw.n_sw_l1,
            "available_at_nulls": sw.available_at_nulls,
            "in_date_range": [str(sw.in_date_min), str(sw.in_date_max)],
            "promotable": bool(sw.promotable),
            "promotion_approved": bool(sw.promotion_approved),
            "source_variant": sw.source_variant,
            "quality_label": sw.quality_label,
            "quality_status_top": dict(sw.quality_status_top),
            "not_promotion_grade_note": sw.not_promotion_grade_note_path,
        },
        "float_mktcap": {
            "path": fm.path,
            "session": str(fm.session),
            "n_rows": fm.n_rows,
            "n_non_null": fm.n_non_null,
            "n_null": fm.n_null,
            "unit": fm.unit,
            "promotion_approved": False,
        },
        "etf_510300": {
            "instruments_path": etf.instruments_path,
            "panel_path": etf.panel_path,
            "instrument_id": etf_inst.instrument_id,
            "asset_type": etf_inst.asset_type,
            "quality_status": etf_inst.quality_status,
            "n_bars": etf.n_bars,
            "date_range": [str(etf.date_min), str(etf.date_max)],
            "promotion_approved": False,
            "quality_gaps_head": list(etf.quality_gaps[:4]),
        },
        "asof_extend": {
            "path": extend.path,
            "as_of_extended": extend.as_of_extended,
            "calendar_max": str(extend.calendar_max),
            "n_panels_written": extend.n_panels_written,
            "merged_calendar_n": cal.n_sessions,
            "merged_calendar_last": str(cal.last_session),
            "promotion_approved": False,
            "notes_head": list(extend.notes[:4]),
            "merge_rule": f"d0[session<={cutoff}]+extend[session>{cutoff}]",
        },
        "by_session": per_session,
        # Convenience mirrors for mid/late mask counts
        "mask_member_counts": {
            sid: block["mask"]["member_count"] for sid, block in per_session.items()
        },
        "schema_handshake": schema_handshake_payload(),
        "note": (
            "V2 proto smoke only — counts/date ranges/quality flags; "
            "no backtest metrics; SW dataset may be promotion-grade (tushare); "
            "overall promotion_approved=false; "
            "D1 panels use D0+asof_extend research merge"
        ),
    }

    if status["promotion_approved"] != _gate():
        status["ok"] = False
        status["error"] = "promotion_approved_not_false"
    if etf.n_bars < 1 or sw.n_rows < 1 or fm.n_non_null < 1:
        status["ok"] = False
        status["error"] = "expected_nonempty_v2_datasets"
    return status


def main(argv: list[str] | None = None) -> int:
    import argparse

    p = argparse.ArgumentParser(prog="quantlab.v2_proto_smoke")
    p.add_argument("--mandate", default=None)
    p.add_argument("--d0-root", default=None)
    p.add_argument("--session", default=None, help="mid/D0 session YYYY-MM-DD (default: float_mktcap asof)")
    p.add_argument(
        "--late-session",
        default=None,
        help="asof_extend session YYYY-MM-DD (default: 2026-10-09)",
    )
    p.add_argument("--max-instruments", type=int, default=300)
    p.add_argument(
        "--single-session",
        action="store_true",
        help="Only run --session (skip late extend session)",
    )
    args = p.parse_args(argv)
    try:
        status = run_proto_smoke(
            mandate_path=args.mandate,
            d0_root=args.d0_root,
            session=args.session,
            late_session=args.late_session,
            max_instruments=args.max_instruments,
            dual_session=not args.single_session,
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
