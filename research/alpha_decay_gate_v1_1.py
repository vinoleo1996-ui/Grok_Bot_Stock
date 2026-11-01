"""Leaf alpha-decay gate v1.1 (prereg docs/v2/ALPHA_DECAY_GATE_V1_1_PREREG_ZH.md).
Only change vs v1 (research/alpha_decay_gate.py, kept intact): returns are computed on prices
forward-filled across suspension gaps, then pct_change(fill_method=None), so the resume-day return
carries the full move instead of being zeroed by fillna(0). Leading NaN (before listing) stays 0.
Thresholds, window, cost, rules identical to v1. promotion_approved=false; live=false.
"""
from __future__ import annotations
import sys, json
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import research.alpha_decay_gate as V1

PREREG_SHA_V11 = None  # filled from prereg doc at runtime


def gross_and_turnover(weights_path):
    d = pd.read_parquet(weights_path, columns=["date", "instrument", "target_weight"])
    d["date"] = pd.to_datetime(d["date"].astype(str).str[:10])
    P = d.pivot_table(index="date", columns="instrument", values="target_weight", aggfunc="sum").fillna(0).sort_index()
    R = {}
    for i in P.columns:
        c = V1._close(i).dropna()
        c = c.reindex(c.index.union(P.index)).sort_index().ffill()   # carry last price through suspension
        R[i] = c.pct_change(fill_method=None).reindex(P.index)
    R = pd.DataFrame(R).fillna(0)   # only pre-listing / no-data NaN remain
    g = (P.shift(1) * R).sum(axis=1).iloc[1:]
    to = P.diff().abs().sum(axis=1).iloc[1:]
    return g, to


def evaluate_weights(weights_path, prereg_sha=None):
    g, to = gross_and_turnover(weights_path)
    r = V1.evaluate_returns(g, to); r["prereg_sha256"] = prereg_sha; r["gate_version"] = "v1.1"
    r["weights_path"] = str(weights_path); return r


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(json.dumps(evaluate_weights(p), ensure_ascii=False, default=float, indent=1))
