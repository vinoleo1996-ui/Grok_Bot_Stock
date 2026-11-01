"""Phase 0 smoke: import stubs, load Mandate V2, probe D0 meta — no market backtest.

Run (from QuantLab root, with pandas/pyarrow available)::

    PYTHONPATH=. python -m quantlab.v2_smoke
    PYTHONPATH=. python -m quantlab.cli v2-smoke

Exits 0 on structural ok; never prints fabricated performance metrics.
``promotion_approved`` must remain false.
"""
from __future__ import annotations

from quantlab.promotion_gate import overall_promotion_approved as _gate

import json
import sys
from datetime import date
from pathlib import Path


def run_smoke(mandate_path: str | None = None, d0_root: str | None = None) -> dict:
    from quantlab.beta import StubBetaSleeveProvider
    from quantlab.data.v2_d0_meta import DEFAULT_D0_ROOT, D0MetaStore
    from quantlab.factors.residual_factory import StubResidualAlphaFactorFactory
    from quantlab.mandate_v2 import load_mandate_v2
    from quantlab.universe import StubUniverseMaskProvider
    from quantlab.v2_schemas import schema_handshake_payload

    mandate = load_mandate_v2(mandate_path)
    if bool(mandate.promotion_approved) != _gate():
        raise RuntimeError("smoke_fail:mandate_promotion_gate_mismatch")

    root = Path(d0_root) if d0_root else DEFAULT_D0_ROOT
    store = D0MetaStore(root)
    probe = store.probe()
    if probe.manifest.promotion_approved:
        raise RuntimeError("smoke_fail:d0_manifest_promotion_must_be_false")

    uni = StubUniverseMaskProvider(mandate, d0_root=root)
    beta = StubBetaSleeveProvider(mandate, d0_root=root)
    factory = StubResidualAlphaFactorFactory(mandate)

    # Use a session inside D0 calendar (as_of neighbourhood).
    session = probe.calendar.last_session
    # last calendar session may be after as_of; clamp to as_of if parseable
    if probe.manifest.as_of:
        try:
            as_of = date.fromisoformat(str(probe.manifest.as_of)[:10])
            if probe.calendar.first_session <= as_of <= probe.calendar.last_session:
                session = as_of
        except ValueError:
            pass

    membership = uni.membership_at(session)
    plan = beta.plan(session)

    # Index bars: real D0 read (not a backtest). Cap to 3 days for smoke payload size.
    index_n = 0
    index_err = None
    try:
        bars = beta.load_index_bars(session, session)
        index_n = len(bars)
    except Exception as exc:  # noqa: BLE001 — smoke reports errors, does not invent data
        index_err = f"{type(exc).__name__}:{exc}"

    # 510300 / SW_L1 must NotImplement — confirm they do not silently succeed.
    etf_blocked = False
    sw_blocked = False
    try:
        beta.load_etf_bars(session, session)
    except NotImplementedError:
        etf_blocked = True
    try:
        uni.sw_l1_asof(session, ())
    except NotImplementedError:
        sw_blocked = True
    # empty instrument list on sw_l1_asof still raises by design; also try with ids
    if not sw_blocked:
        try:
            uni.sw_l1_asof(session, ("sz.000001",))
        except NotImplementedError:
            sw_blocked = True

    handshake = schema_handshake_payload()

    status = {
        "ok": True,
        "phase": "0",
        "promotion_approved": False,
        "mandate_id": mandate.mandate_id,
        "mandate_version": mandate.version,
        "mandate_path": mandate.source_path,
        "benchmark_etf": mandate.markets.benchmark_etf,
        "target_vol": mandate.risk.target_annual_vol,
        "target_beta": mandate.risk.target_beta_vs_benchmark,
        "d0": {
            "root": probe.manifest.root,
            "snapshot_id": probe.manifest.snapshot_id,
            "as_of": probe.manifest.as_of,
            "calendar_sessions": probe.calendar.n_sessions,
            "calendar_range": [
                str(probe.calendar.first_session),
                str(probe.calendar.last_session),
            ],
            "instruments_unique": probe.instruments.n_unique_ids,
            "asset_types": dict(probe.instruments.asset_type_counts),
            "benchmark_code": probe.benchmark.code,
            "benchmark_rows": probe.benchmark.n_rows,
            "has_float_mktcap": probe.instruments.has_float_mktcap,
            "has_510300_instrument": probe.instruments.has_510300,
            "has_510300_panel": probe.benchmark.has_etf_510300_panel,
            "sw_l1_pit_ready": probe.industry_gap.sw_l1_pit_ready,
            "industry_gap_note": probe.industry_gap.note,
        },
        "session_probed": str(session),
        "universe": {
            "calendar_ok": membership.calendar_ok,
            "member_count": len(membership.member_ids),
            "data_ready": membership.data_ready,
            "todos_head": list(membership.todos[:4]),
        },
        "beta": {
            "index_bars_available": plan.index_bars_available,
            "etf_panel_available": plan.etf_panel_available,
            "index_bars_loaded_for_session": index_n,
            "index_load_error": index_err,
            "etf_load_not_implemented": etf_blocked,
            "todos_head": list(plan.todos[:4]),
        },
        "residual_factory": factory.describe_contract(),
        "sw_l1_load_not_implemented": sw_blocked,
        "schema_handshake": handshake,
        "note": "Phase 0 smoke only — no backtest metrics, no promotion",
    }

    if not etf_blocked or not sw_blocked:
        status["ok"] = False
        status["error"] = "expected NotImplemented for missing 510300/SW_L1 loaders"
    if membership.promotion_approved or plan.promotion_approved:
        status["ok"] = False
        status["error"] = "promotion_approved leaked true"
    return status


def main(argv: list[str] | None = None) -> int:
    import argparse

    p = argparse.ArgumentParser(prog="quantlab.v2_smoke")
    p.add_argument("--mandate", default=None, help="Path to QuantLab-MANDATE_V2.json")
    p.add_argument(
        "--d0-root",
        default=None,
        help="D0 snapshot root (default data/local_market/1c85fd9aceaa03c3c4863bec)",
    )
    args = p.parse_args(argv)
    try:
        status = run_smoke(mandate_path=args.mandate, d0_root=args.d0_root)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": f"{type(exc).__name__}:{exc}"}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(status, ensure_ascii=False, indent=2, default=str))
    return 0 if status.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
