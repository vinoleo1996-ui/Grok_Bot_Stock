#!/usr/bin/env python3
"""Leaf35 mapping recon PROBE DRAFT — read-only diagnostic (NOT formal alpha build).

DRAFT ONLY. Lives under docs/v2/audit/ (NOT research/).
Does NOT replace research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py (must stay 25ae4572).

Default: --dry-compile-only (no parquet row loads).
Real per-rebal counts require a NEW Arch .ok (forbid RESTORED 10927bd9) + --allow-real-data.
≠X2 ACCEPT; ≠leaf36; EXECUTED_PROBE default false.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in ("/workspace/QuantLab",) and not (ROOT / "research").is_dir():
    # tolerate docs/v2/audit -> parents[3] == repo root when layout matches
    cand = Path("/workspace/QuantLab")
    if (cand / "research").is_dir():
        ROOT = cand

SCRIPT_REL = "docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_DRAFT_20261027.py"
FORMAL_SCRIPT_REL = "research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py"
FORMAL_SHA8_PIN = "25ae4572"
PIN_SHA8 = "dd17044a"
VOID_SHA8 = "dfafff28"
COUNT_JSON_SHA8 = "a17b75fb"
FORBIDDEN_OK = {
    "10927bd9", "178e90e9", "c1b71e64", "245df63f", "c5ed13df",
    "5774bb6e", "81521fb5",
}

ETF_INDEX_MAP = {
    "510300.SH": "000300.SH",
    "510500.SH": "000905.SH",
    "512100.SH": "000852.SH",
}

PROBE_COLS = [
    "rebal_date",
    "n_share_rows",
    "n_share_rows_avail_le_tts",
    "n_weight_rows_schemeA",
    "n_mapped",
    "n_pressure_nonnull",
    "n_hiliq_intersect",
    "empty_reason",
]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dry_compile_only() -> int:
    formal = ROOT / FORMAL_SCRIPT_REL
    formal_sha8 = sha256_file(formal)[:8] if formal.is_file() else "MISSING"
    payload = {
        "role": "leaf35_mapping_recon_probe_draft",
        "dry_compile_only": True,
        "executed_probe": False,
        "allow_real_data": False,
        "x2_accept": False,
        "leaf36": False,
        "formal_script": FORMAL_SCRIPT_REL,
        "formal_sha8_observed": formal_sha8,
        "formal_sha8_pin": FORMAL_SHA8_PIN,
        "formal_unchanged_required": formal_sha8 == FORMAL_SHA8_PIN,
        "pin_sha8": PIN_SHA8,
        "void_sha8": VOID_SHA8,
        "count_json_sha8_ref": COUNT_JSON_SHA8,
        "etf_index_map": dict(ETF_INDEX_MAP),
        "probe_output_columns": list(PROBE_COLS),
        "empty_reason_enum": [
            "A_share_gap_no_avail_le_tts",
            "B_weight_schemeA_empty",
            "C_index_map_fail",
            "D_hiliq_intersect_zero",
            "E_pressure_empty_before_topq",
            "OK_nonempty",
            "PIN_GAP_needs_ok_window",
        ],
        "notes": [
            "COUNT a17b75fb APPROX used month-end weight asof WITHOUT available_at and did NOT filter share available_at<=t_ts",
            "Formal 25ae4572: scheme A weight_available_at + share trade_date==rebal AND available_at_clock<=t_ts(15:00 SH)",
            "PIN dd17044a §1.3: share asof by available_at<=t_ts (does not require trade_date==rebal)",
            "X2 STOP_ZERO_MASK_ROWS: 30x after_pressure_rebal_* then zero rebal_rows; after_mask_cs ABSENT",
            "Real probe needs NEW .ok; forbid RESTORED 10927bd9+legacy",
        ],
        "forbidden_ok_sha8_prefix": sorted(FORBIDDEN_OK),
        "live": False,
        "leo_notify": False,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if formal_sha8 != FORMAL_SHA8_PIN:
        print("STOP: formal script sha8 drifted; refuse probe framing", file=sys.stderr)
        return 2
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Leaf35 mapping recon PROBE DRAFT")
    ap.add_argument("--dry-compile-only", action="store_true", help="pins only; no real table rows")
    ap.add_argument("--allow-real-data", action="store_true", help="requires NEW arch-ok; default off")
    ap.add_argument("--arch-ok-path", default="", help="NEW .ok path (sha8 not in forbid)")
    ap.add_argument("--out", default="", help="optional JSON out for per-rebal rows")
    args = ap.parse_args(argv)

    if args.allow_real_data:
        print(
            "STOP: real probe window not implemented in this DRAFT byte; "
            "sign a NEW .ok then open a follow-on probe ticket. "
            "forbid RESTORED 10927bd9. EXECUTED_PROBE=false",
            file=sys.stderr,
        )
        return 3
    # default dry
    return dry_compile_only()


if __name__ == "__main__":
    raise SystemExit(main())
