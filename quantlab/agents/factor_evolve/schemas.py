"""Schemas for candidate → hard-gate → consumable weight long-table."""
from __future__ import annotations

from typing import Any, Literal, TypedDict

PROMOTION_APPROVED = False

UniverseKind = Literal["mid_large_stock", "etf_core", "etf_sector", "etf_theme"]
GateVerdict = Literal["pass", "fail"]

# Weight long-table column contract (Book-Smoke / debate consume this).
# Eng canonical: quantlab.platform.weight_long_table (COLUMN_CONTRACT_VERSION).
# QM P0 tag kept for evolve-run meta continuity.
COLUMN_CONTRACT_VERSION = "weight_long_v1_qm_p0_20261012"
try:
    from quantlab.platform.weight_long_table import AUTHORITATIVE_COLS as AUTHORITATIVE_WEIGHT_COLS
except Exception:  # pragma: no cover
    AUTHORITATIVE_WEIGHT_COLS = ("session", "instrument_id", "weight")


class FactorCandidate(TypedDict, total=False):
    candidate_id: str
    expr_str: str
    mechanism_tag: str
    who_pays_zh: str
    universe_kind: UniverseKind
    direction_zh: str
    # optional cross-section scores: list of {session, instrument_id, score}
    # (aliases date/instrument accepted at ingest)
    score_rows: list[dict[str, Any]]
    notes: str
    # QuantMind P0 dual-read + impact fields (production requires gate + both impacts)
    icir_eps_gate: float
    icir_eps_posthoc: float
    impact_flat25_pct_60万: float
    impact_flat25_pct_100万: float
    tags: list[str]


class GateResult(TypedDict, total=False):
    candidate_id: str
    verdict: GateVerdict
    reasons: list[str]
    hard_gate_version: str
    tags: list[str]


class EvolveRunMeta(TypedDict, total=False):
    run_id: str
    capital_cny: int
    window: str
    n_candidates: int
    n_passed: int
    n_failed: int
    n_weight_rows: int  # KPI
    weight_path: str
    gate_receipt_path: str
    strategy_promotion_approved: bool
    benchmark: str
    mandate_note: str
    hard_gate_version: str
    column_contract_version: str
    stub_window: bool
    stub_window_warn: str
    smoke: bool
