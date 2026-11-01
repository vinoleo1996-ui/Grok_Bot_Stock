#!/usr/bin/env python3
"""D1 mask prototype over D0 1c85 (read-only panels). Sampled for smoke speed."""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from quantlab.universe.d1_masks import D1MaskConfig, build_d1_masks_for_session, DEFAULT_D0_ROOT, PSEUDOCODE

OUT = ROOT / "output" / "d1"
OUT.mkdir(parents=True, exist_ok=True)
DATA_OUT = ROOT / "data" / "v2" / "d1_masks"
DATA_OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    # Mid research window session inside 1c85 as_of
    session = date(2024, 6, 28)
    # Prototype: first 200 stock ids with panels (fast smoke). Full-universe later.
    import pandas as pd
    inst = pd.read_parquet(DEFAULT_D0_ROOT / "instruments.parquet")
    inst = inst[inst["asset_type"].astype(str) == "stock"]
    # prefer ones with panels
    panel_dir = DEFAULT_D0_ROOT / "panels"
    ids = []
    for iid in inst["instrument_id"].astype(str).tolist():
        if (panel_dir / f"{iid}.parquet").is_file():
            ids.append(iid)
        if len(ids) >= 250:
            break
    result = build_d1_masks_for_session(
        session,
        instrument_ids=ids,
        config=D1MaskConfig(open_status_mode="research"),
    )
    summary = {
        "session": str(session),
        "n_sampled": len(ids),
        "n_instruments_in": result.n_instruments_in,
        "n_after_listing": result.n_after_listing,
        "n_after_tradable_st": result.n_after_tradable_st,
        "n_after_u30": result.n_after_u30,
        "n_after_limits": result.n_after_limits,
        "n_after_mktcap": result.n_after_mktcap,
        "n_members": len(result.member_ids),
        "promotion_approved": result.promotion_approved,
        "notes": list(result.notes),
        "d0_root": str(DEFAULT_D0_ROOT),
    }
    (OUT / "d1_mask_prototype_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
    )
    (DATA_OUT / "prototype_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
    )
    if not result.frame.empty:
        result.frame.to_parquet(DATA_OUT / f"prototype_members_{session}.parquet", index=False)
        result.frame.to_csv(OUT / f"prototype_members_{session}.csv", index=False)
    (OUT / "PSEUDOCODE.txt").write_text(PSEUDOCODE)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
