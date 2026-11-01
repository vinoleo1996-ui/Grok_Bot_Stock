#!/usr/bin/env python3
"""Shared v1.3 feasibility definitions, aligned with Strategy's research/optimizer_core_v1_3_stats.py.

research/optimizer_core_v1_3_stats.py runs and writes files at import time (core_v1_3_stats.json,
core_v1_3_lot_exclusion_counts.csv), so it can't be imported safely. Its definitions are re-stated here
verbatim and cross-checked against its core_v1_3_stats.json output (see check_against_stats):
  HARD-feasible = status ∈ {OK, LOT_CASH_GT2}             (stats.py: D.feasible)
  STRICT        = HARD-feasible AND cash ≤ 2%              (≡ status == "OK"; stats.py: strict_feasibility_pct)
  denominator   = rows with status != NO_DATA_CARRY        (excludes the no-data first day 2018-01-02)
Per tier × sleeve is the primary unit; the tier-deduped row (a date counts only if BOTH sleeves pass) is for reference.
No returns. live=false.
"""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

HARD_OK = ("OK", "LOT_CASH_GT2")
FAIL = ("INFEASIBLE", "LOT_HARD_FAIL")
NODATA = "NO_DATA_CARRY"
CASH_MAX = 0.02
EPS = 1e-9
WINDOWS = ("ALL", "SEALED", "X2")
SLEEVE_TAG = {"equity_100": "①", "equity80_etf20_510300": "②"}


def load(disc: Path) -> pd.DataFrame:
    D = pd.read_csv(disc)
    D["hard"] = D.status.isin(HARD_OK)
    D["strict"] = D.hard & (D.cash <= CASH_MAX + EPS)
    D["nodata"] = D.status.eq(NODATA)
    # consistency with Strategy: strict must equal status == OK
    D.attrs["strict_eq_ok"] = bool((D.strict == D.status.eq("OK")).all())
    return D


def _win(D: pd.DataFrame, w: str) -> pd.DataFrame:
    return D if w == "ALL" else D[D.window == w]


def table(D: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for a in sorted(D.aum.unique()):
        for w in WINDOWS:
            x = _win(D[D.aum == a], w)
            for sv in ("equity_100", "equity80_etf20_510300"):
                g = x[(x.sleeve == sv) & ~x.nodata]
                rows.append(dict(window=w, aum=int(a), sleeve=sv, tag=SLEEVE_TAG[sv], kind="tier×sleeve", n_eval=len(g),
                                 n_hard=int(g.hard.sum()), n_strict=int(g.strict.sum()),
                                 hard_pct=round(100 * g.hard.mean(), 1) if len(g) else None,
                                 strict_pct=round(100 * g.strict.mean(), 1) if len(g) else None,
                                 cash_gt2_hard_rows=int((g.hard & ~g.strict).sum())))
            d = x.groupby("date").agg(hard=("hard", "all"), strict=("strict", "all"), nodata=("nodata", "any"))
            d = d[~d.nodata]
            rows.append(dict(window=w, aum=int(a), sleeve="tier_dedup(both)", tag="档去重", kind="tier_dedup_reference", n_eval=len(d),
                             n_hard=int(d.hard.sum()), n_strict=int(d.strict.sum()),
                             hard_pct=round(100 * d.hard.mean(), 1) if len(d) else None,
                             strict_pct=round(100 * d.strict.mean(), 1) if len(d) else None,
                             cash_gt2_hard_rows=int((d.hard & ~d.strict).sum())))
    return pd.DataFrame(rows)


def check_against_stats(T: pd.DataFrame, stats_json: Path) -> list[str]:
    """Compare with Strategy's core_v1_3_stats.json (feasibility_pct / strict_feasibility_pct)."""
    if not stats_json.exists():
        return [f"stats json missing: {stats_json}"]
    S = json.loads(stats_json.read_text(encoding="utf-8"))["by_aum_sleeve"]
    out = []
    for r in T[T.kind == "tier×sleeve"].itertuples():
        s = S.get(f"{r.aum}_{r.sleeve}", {}).get(r.window)
        if not s:
            out.append(f"MISSING {r.aum}_{r.sleeve} {r.window}"); continue
        ok = (abs(s["feasibility_pct"] - r.hard_pct) < 0.05 and abs(s["strict_feasibility_pct"] - r.strict_pct) < 0.05 and s["n_eval"] == r.n_eval)
        if not ok:
            out.append(f"MISMATCH {r.aum} {r.sleeve} {r.window}: eng hard/strict/n={r.hard_pct}/{r.strict_pct}/{r.n_eval} "
                       f"vs stats {s['feasibility_pct']}/{s['strict_feasibility_pct']}/{s['n_eval']}")
    return out or ["MATCH: all tier×sleeve×window HARD/STRICT/n_eval equal to core_v1_3_stats.json"]


def consecutive_fail_runs(D: pd.DataFrame, aum: int, start: str = "2024-06-01") -> list[str]:
    """Runs of consecutive rebalance months with ≥1 HARD failure (tier: any sleeve fails), from `start`."""
    x = D[(D.aum == aum) & (D.date >= start)]
    d = x.groupby("date").hard.all().sort_index()
    runs, cur = [], []
    for dt, ok in d.items():
        if not ok:
            cur.append(dt)
        else:
            if len(cur) >= 2: runs.append((cur[0], cur[-1]))
            cur = []
    if len(cur) >= 2: runs.append((cur[0], cur[-1]))
    return [f"{a[:7]}→{b[:7] if b[:7] != '2026-10' else b}" for a, b in runs]
