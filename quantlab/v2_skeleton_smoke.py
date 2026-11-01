"""One-click Eng skeleton: trading_loop + factor_evolve + book_smoke (+ weight contract).

LIGHT — no full GP, no full D1, no heavy NAV unless --book-nav.
promotion_gate / promotion_approved untouched (always false here).

Usage::

    cd /workspace/QuantLab
    PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.v2_skeleton_smoke
    PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli skeleton-smoke
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_skeleton_smoke(
    *,
    book_nav: bool = False,
    capital: int = 600_000,
    top_k: int = 5,
    out_dir: str | Path | None = None,
) -> dict:
    from quantlab.platform.weight_long_table import (
        COLUMN_CONTRACT_VERSION,
        PROMOTION_APPROVED,
        schema_handshake,
        validate_weight_path,
        write_weight_long_table,
    )
    import pandas as pd

    out = Path(out_dir) if out_dir else ROOT / "output" / "v3" / "skeleton_smoke"
    out.mkdir(parents=True, exist_ok=True)
    result: dict = {
        "ok": False,
        "strategy_promotion_approved": False,
        "promotion_approved": False,
        "column_contract_version": COLUMN_CONTRACT_VERSION,
        "weight_schema": schema_handshake(),
        "steps": {},
    }

    # 1) trading_loop stub
    from quantlab.agents.trading_loop.state_machine import stub_run_once, describe_graph
    from quantlab.agents.trading_loop.run_stub import main as tl_main

    log_path = out / "trading_loop_decision_log.jsonl"
    if log_path.exists():
        log_path.unlink()
    trace, entry = stub_run_once(
        session="2024-07-01",
        instrument="510500.SH",
        log_path=log_path,
    )
    tl_ok = bool(trace) and entry.get("strategy_promotion_approved") is False
    result["steps"]["trading_loop"] = {
        "ok": tl_ok,
        "trace": trace,
        "decision_id": entry.get("decision_id"),
        "status": entry.get("status"),
        "log": str(log_path.relative_to(ROOT)) if log_path.is_relative_to(ROOT) else str(log_path),
        "graph_edges": describe_graph(),
        "module": "quantlab.agents.trading_loop",
        "cli": "python -m quantlab.cli trading-loop --session 2024-07-01 --instrument 510500.SH",
        "stub": True,
    }

    # 2) factor_evolve --smoke → weight long-table
    from quantlab.agents.factor_evolve.run_stub import run as fe_run

    fe_out = out / "factor_evolve"
    meta = fe_run(capital_cny=int(capital), top_k=int(top_k), out_dir=fe_out)
    latest = fe_out / "latest_weights.path"
    if latest.exists():
        wpath = Path(latest.read_text(encoding="utf-8").strip())
    else:
        wp = Path(meta["weight_path"])
        wpath = wp if wp.is_absolute() else (ROOT / wp)
    vmeta = validate_weight_path(wpath, require_rows=True)
    fe_ok = (
        int(meta.get("n_weight_rows") or 0) > 0
        and vmeta.get("status") == "ok"
        and not bool(meta.get("strategy_promotion_approved"))
    )
    result["steps"]["factor_evolve"] = {
        "ok": fe_ok,
        "run_id": meta.get("run_id"),
        "n_weight_rows": meta.get("n_weight_rows"),
        "n_passed": meta.get("n_passed"),
        "n_failed": meta.get("n_failed"),
        "weight_path": str(wpath),
        "validate": dict(vmeta),
        "module": "quantlab.agents.factor_evolve",
        "cli": "python -m quantlab.cli factor-evolve --smoke",
        "stub": True,
    }

    # 3) weight contract synth round-trip (Eng)
    synth = pd.DataFrame(
        [
            {"date": "2024-06-03", "instrument": "510300.SH", "target_weight": 0.5, "sleeve": "core"},
            {"date": "2024-06-03", "instrument": "510500.SH", "target_weight": 0.5, "sleeve": "stock"},
        ]
    )
    synth_path = out / "weight_long_synth.parquet"
    wmeta = write_weight_long_table(synth, synth_path, with_sleeve=True)
    result["steps"]["weight_long_table"] = {
        "ok": wmeta.get("status") == "ok" and wmeta.get("n_rows") == 2,
        "meta": dict(wmeta),
        "module": "quantlab.platform.weight_long_table",
        "cli": "python -c \"from quantlab.platform.weight_long_table import schema_handshake; print(schema_handshake())\"",
        "stub": False,  # contract is real; data is synth
    }

    # 4) book_smoke dry (--skip-run) — no heavy Data()
    from quantlab.portfolio.book_smoke import run as book_run

    book_dir = out / "book_smoke"
    receipt_path = out / "BOOK_SMOKE_SKELETON_RECEIPT.md"
    # book_smoke joins non-absolute --out/--receipt with QuantLab ROOT
    book_out = str(book_dir.relative_to(ROOT)) if book_dir.is_relative_to(ROOT) else str(book_dir)
    receipt = (
        str(receipt_path.relative_to(ROOT)) if receipt_path.is_relative_to(ROOT) else str(receipt_path)
    )
    argv = [
        "--skip-run",
        "--out",
        book_out,
        "--receipt",
        receipt,
        "--capitals",
        str(capital),
        "--sleeves",
        json.dumps({"core": 0.0, "stock": 1.0, "alpha_event": 0.0}),
        "--stock-path",
        str(wpath),
    ]
    book_res = book_run(argv)
    book_ok = book_res.get("strategy_promotion_approved") is False
    step_book = {
        "ok": book_ok,
        "run_id": book_res.get("run_id"),
        "gaps": book_res.get("gaps"),
        "summary": str(book_dir / "book_smoke_summary.json"),
        "module": "quantlab.portfolio.book_smoke",
        "cli": "python -m quantlab.cli book-smoke --skip-run",
        "stub": True,
        "nav_ran": False,
    }
    if book_nav:
        # still LIGHT: single capital, X2, C0 only — caller opt-in
        argv_nav = [
            "--out",
            str(book_dir) + "_nav",
            "--receipt",
            receipt,
            "--capitals",
            str(capital),
            "--windows",
            "X2",
            "--arms",
            "C0",
        ]
        nav_res = book_run(argv_nav)
        step_book["nav_ran"] = True
        step_book["nav_ok"] = bool(nav_res.get("headline"))
        step_book["nav_headline"] = nav_res.get("headline")
        book_ok = book_ok and step_book["nav_ok"]
        step_book["ok"] = book_ok
    result["steps"]["book_smoke"] = step_book

    # unused import guard
    _ = tl_main
    _ = PROMOTION_APPROVED

    result["ok"] = all(s.get("ok") for s in result["steps"].values())
    (out / "skeleton_smoke_summary.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    return result


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--book-nav", action="store_true", help="opt-in: also run C0 NAV (heavier)")
    ap.add_argument("--capital", type=int, default=600_000, choices=[600_000, 1_000_000])
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    status = run_skeleton_smoke(
        book_nav=a.book_nav,
        capital=a.capital,
        top_k=a.top_k,
        out_dir=a.out,
    )
    print(json.dumps(status, ensure_ascii=False, indent=2, default=str))
    return 0 if status.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
