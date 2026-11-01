"""Light smokes for Eng skeleton one-click + weight long-table contract."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_weight_long_table_contract_aliases(tmp_path: Path):
    from quantlab.platform.weight_long_table import (
        COLUMN_CONTRACT_VERSION,
        normalize_weight_frame,
        schema_handshake,
        validate_weight_frame,
        write_weight_long_table,
    )

    hs = schema_handshake()
    assert hs["promotion_approved"] is False
    assert hs["column_contract_version"] == COLUMN_CONTRACT_VERSION
    assert hs["authoritative_cols"] == ["session", "instrument_id", "weight"]

    raw = pd.DataFrame(
        [
            {"date": "2024-06-03", "instrument": "510300.SH", "target_weight": 0.6},
            {"date": "2024-06-03", "code": "510500.SH", "weight": 0.4},
            {"date": "2024-06-03", "instrument": "000001.SZ", "target_weight": 0.0},  # dropped
        ]
    )
    norm = normalize_weight_frame(raw)
    assert list(norm.columns)[:3] == ["session", "instrument_id", "weight"]
    assert len(norm) == 2
    assert set(norm["instrument_id"]) == {"sh.510300", "sh.510500"}

    path = tmp_path / "w.parquet"
    meta = write_weight_long_table(raw, path)
    assert meta["status"] == "ok"
    assert meta["n_rows"] == 2
    assert meta["promotion_approved"] is False
    assert path.exists()

    bad = validate_weight_frame(pd.DataFrame({"x": [1]}))
    assert bad["status"] == "error"


def test_trading_loop_stub(tmp_path: Path):
    from quantlab.agents.trading_loop.state_machine import stub_run_once

    log = tmp_path / "dec.jsonl"
    trace, entry = stub_run_once(session="2024-07-01", instrument="510500.SH", log_path=log)
    assert trace[0] == "START" and trace[-1] == "END"
    assert entry["strategy_promotion_approved"] is False
    assert log.exists()


def test_factor_evolve_smoke_emits_contract(tmp_path: Path):
    from quantlab.agents.factor_evolve.run_stub import run
    from quantlab.platform.weight_long_table import validate_weight_path

    meta = run(capital_cny=600_000, top_k=5, out_dir=tmp_path)
    assert meta["strategy_promotion_approved"] is False
    assert meta["n_weight_rows"] > 0
    w = Path((tmp_path / "latest_weights.path").read_text().strip())
    v = validate_weight_path(w, require_rows=True)
    assert v["status"] == "ok"


def test_skeleton_smoke_light(tmp_path: Path):
    from quantlab.v2_skeleton_smoke import run_skeleton_smoke

    status = run_skeleton_smoke(book_nav=False, capital=600_000, out_dir=tmp_path)
    assert status["promotion_approved"] is False
    assert status["strategy_promotion_approved"] is False
    assert status["ok"] is True
    for k in ("trading_loop", "factor_evolve", "weight_long_table", "book_smoke"):
        assert status["steps"][k]["ok"] is True, k


def test_weight_session_coverage_rule():
    """全日更长表须覆盖目标窗；禁止仅前推解读（轻量，无重 parquet）。"""
    from quantlab.platform.weight_long_table import (
        assert_session_coverage,
        schema_handshake,
    )

    hs = schema_handshake()
    assert "覆盖目标窗" in hs["coverage_rule_zh"]
    assert hs["forbid_forward_fill_interpretation"] is True

    df = pd.DataFrame(
        [
            {"session": "2024-01-02", "instrument_id": "sh.510300", "weight": 0.5},
            {"session": "2024-06-28", "instrument_id": "sh.510300", "weight": 0.5},
        ]
    )
    ok = assert_session_coverage(df, target_start="2024-01-02", target_end="2024-06-28")
    assert ok["ok"] is True and ok["covers_target"] is True
    gap = assert_session_coverage(df, target_end="2026-10-09")
    assert gap["ok"] is False and gap["status"] == "coverage_gap"
    assert any("ends_before_target" in r for r in gap["reasons"])


def test_live_dryrun_gates_only(tmp_path: Path):
    from quantlab.v2_live_dryrun import run_live_dryrun

    status = run_live_dryrun(out_dir=tmp_path, skip_skeleton_tail=True)
    assert status["promotion_approved"] is False
    assert status["no_orders"] is True
    for g in ("G1", "G2", "G3", "G4", "G5"):
        assert status["steps"][g]["ok"] is True, g
    assert status["ok"] is True
