#!/usr/bin/env python3
"""V3-A1 holding-layer sealed runner (prereg docs/prereg/V3_A1_HOLDING_LAYER.md).

DEFAULT: --prepare-only (path checks + readiness JSON). Does NOT run sealed.
To execute sealed (Leo approval required):
  LEO_A1_HOLDING_LAYER_OK=1 python research/v3_a1_holding_layer_sealed.py --run-sealed

Research-only. promotion_approved=False. Mid/large CSI300 EW base only.
Prior sealed A1 (V3_A1_LIMIT_T1_EXECUTION) failed on incremental alpha — this
script implements the holding-layer redesign; do not treat old results as pass.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import sys
from pathlib import Path

ROOT = Path("/workspace/QuantLab")
PREREG = ROOT / "docs/prereg/V3_A1_HOLDING_LAYER.md"
OUT = ROOT / "output/alpha/V3_A1_HOLDING_LAYER"
PROMOTION_APPROVED = False


def mem_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


def prereg_sha() -> str:
    return hashlib.sha256(PREREG.read_bytes()).hexdigest()


def find_panels() -> list[Path]:
    candidates = [
        ROOT / "data/local_market/1c85fd9aceaa03c3c4863bec/panels",
        ROOT / "data/v2/asof_extend_202610/panels",
        ROOT / "data/v2/asof_extend_tushare_202610/panels",
    ]
    for c in candidates:
        if c.is_dir() and any(c.glob("sh.*.parquet")):
            return sorted(p for p in c.glob("*.parquet") if not p.name.startswith(("bj.", "._")))
    return []


def readiness() -> dict:
    panels = find_panels()
    iw = ROOT / "data/v2/index_members/index_weight_csi300_500_1000.parquet"
    fmc = ROOT / "data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet"
    old_fail = ROOT / "output/alpha/V3_A1_A2_SEALED_ZH.md"
    return {
        "promotion_approved": False,
        "research_only": True,
        "prereg": str(PREREG.relative_to(ROOT)),
        "prereg_sha256": prereg_sha(),
        "mode": "prepare_only",
        "sealed_executed": False,
        "diff_from_old_A1": (
            "Holding-layer only (SELL_SEAL + NOBUY_COOLDOWN); no VWAP execution arm; "
            "20pct board + fake-seal are formal control arms. Prior sealed A1 failed."
        ),
        "prior_a1_fail_note": str(old_fail) if old_fail.exists() else "see output/alpha/V3_A1_A2_SEALED_ZH.md",
        "paths": {
            "panels_n_files": len(panels),
            "panels_root": str(panels[0].parent) if panels else None,
            "csi300_weights": iw.exists(),
            "float_mktcap": fmc.exists(),
        },
        "arms": [
            "HL_T1_SELL_SEAL",
            "HL_T2_NOBUY_COOLDOWN",
            "HL_T3_CTRL_20PCT",
            "HL_T4_PLACEBO_FAKE_SEAL",
        ],
        "gate": "LEO_A1_HOLDING_LAYER_OK=1 required with --run-sealed",
        "peak_rss_MB_prepare": round(mem_mb()),
    }


def run_sealed() -> dict:
    """Placeholder entry for the real sealed path — blocked unless env gate set.

    Full panel simulation mirrors research/v3_a1_a2_sealed.py holding rules
    without VWAP; implemented when Leo unlocks. Raises if called without gate.
    """
    if os.environ.get("LEO_A1_HOLDING_LAYER_OK") != "1":
        raise RuntimeError(
            "Refusing sealed run: set LEO_A1_HOLDING_LAYER_OK=1 only after Leo "
            "confirms in Alpha chat. Default is prepare-only."
        )
    # Intentionally not implementing full sealed compute in this prep turn.
    # When unlocked, port HL_T1–T4 from v3_a1_a2_sealed.py (drop VWAP; add controls).
    raise NotImplementedError(
        "Sealed compute not enabled in prep skeleton. Unlock + implement after Leo OK."
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--prepare-only", action="store_true", default=True, help="default: readiness only")
    g.add_argument("--run-sealed", action="store_true", help="requires LEO_A1_HOLDING_LAYER_OK=1")
    args = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    if args.run_sealed:
        try:
            res = run_sealed()
        except (RuntimeError, NotImplementedError) as e:
            res = {
                "promotion_approved": False,
                "sealed_executed": False,
                "error": str(e),
                "prereg_sha256": prereg_sha(),
            }
            (OUT / "blocked.json").write_text(json.dumps(res, indent=2, ensure_ascii=False))
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return 2
    else:
        res = readiness()
        (OUT / "readiness.json").write_text(json.dumps(res, indent=2, ensure_ascii=False))
        print(json.dumps(res, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
