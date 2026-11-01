#!/usr/bin/env python3
"""S6 shadow paper track daily extend (idempotent). Prereg docs/v2/STRATEGY_S6_SHADOW_PREREG_ZH.md (params unchanged).
Paper only; live=false; promotion=false; no Book-Smoke; no 8787; no GP.

Rule (= output/strategy_wf_combo/wf_screen.py build(), S6 = cap/ee/eq 50/25/25):
  per leg keep top-N stock names by weight (60w N=6, 100w N=10; ties: numpy quicksort on leg-file row order (= history)),
  renormalize to the leg's stock budget; ETF parts pass through; merged single-name cap 6%, overflow -> 510300.SH;
  normalize to 1. Sessions = intersection of legs' sessions, from 2024-05-01 (as wf_screen).
  Rebuilt every session from legs => S6 changes exactly when a leg change touches top-N/cap (capacity_adv month-end,
  event legs on events); frozen last day is not a rebalance day in the extension.
History reference (no separately frozen S6 file exists): output/strategy_wf_combo/weights_S6_{60w,100w}.parquet
(Strategy's WF combo source weights, 2024-05-06..2026-10-09). Leg frozen refs = wf_screen.py P.
Usage: python3 research/s6_paper_extend.py [--run-legs] [--legs-only-check]
Writes output/strategy_paper_s6/S6_cap50_ee25_eq25_topN_{60w,100w}_<YYYYMMDD>.parquet (+ .check.json); never overwrites.
"""
from __future__ import annotations
import argparse, glob, json, os, subprocess, sys
from pathlib import Path
os.environ.setdefault("QL_X2_EXTEND_END", "2026-12-31")
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "research"))
import b4_paper_extend as B  # reuse sha/data_end/leg_end/change_days/run_legs pieces

AF = ROOT / "output/ai_factory"; OUT = ROOT / "output/strategy_paper_s6"; OUT.mkdir(parents=True, exist_ok=True)
MIX = {"capacity_adv": 0.5, "earnings_event": 0.25, "equity_incentive": 0.25}
N = {600000: 6, 1000000: 10}; CAP = 0.06; BAL = "510300.SH"; TOL = 1e-8
FROZEN_END = "2026-10-09"; SESS_START = "2024-05-01"
FROZEN = {600000: ROOT / "output/strategy_wf_combo/weights_S6_60w.parquet",
          1000000: ROOT / "output/strategy_wf_combo/weights_S6_100w.parquet"}
FROZEN_LEGS = {"capacity_adv": AF / "g1g5_capacity_adv_daily_weights_20261013_111219.parquet",
               "earnings_event": AF / "g1g5_earnings_event_daily_weights_20261014_005430.parquet",
               "equity_incentive": AF / "g1g5_equity_incentive_daily_weights_20261014_023222.parquet"}
B.FROZEN_LEGS.update(FROZEN_LEGS)
# scripts pinned in output/strategy_paper_s6/FROZEN_CONFIG.json (Eng content gate)
TRACK_SCRIPTS = ["research/s6_paper_extend.py", "research/b4_paper_extend.py", "research/capacity_adv_paper_extend.py",
                 "research/g1g5_capacity_adv_weights.py", "research/g1g5_earnings_event_weights.py", "research/g1g5_equity_incentive_weights.py"]
etf = B.etf


def run_eq_leg(end: str) -> None:
    env = dict(os.environ, QL_X2_EXTEND_END=end, PYTHONHASHSEED=os.environ.get("S6_SEED", "0"))
    B.run_event_leg("equity_incentive", end, env)  # frozen script, only WEIGHT_END moved; writes .parquet.check.json


def topn(st: pd.Series, n: int) -> pd.Series:
    # Must equal Strategy history: pandas default (numpy quicksort) on leg-file row order. Deterministic (no hash
    # dependence: input order = parquet row order). A code tie-break was tested and changes 60w history (5/31-6/27/2024
    # capacity_adv 12-way 4% ties), so it is NOT used; see receipt.
    return st.sort_values(ascending=False, kind="quicksort").head(n)


def build(legs: dict, aum: int) -> pd.DataFrame:
    D = {}
    for k, p in legs.items():
        d = pd.read_parquet(p, columns=["session", "instrument", "weight"]); d["session"] = d.session.astype(str).str[:10]
        D[k] = d[(d.weight > 0) & (d.session >= SESS_START)]
    sess = sorted(set.intersection(*[set(d.session) for d in D.values()]))
    G = {k: {s: g.set_index("instrument").weight for s, g in d.groupby("session")} for k, d in D.items()}
    rows = []
    for s in sess:
        agg = {}
        for k, m in MIX.items():
            w = G[k].get(s)
            if w is None: continue
            e = w[[etf(i) for i in w.index]]; st = w.drop(e.index)
            for i, v in e.items(): agg[i] = agg.get(i, 0) + v * m
            if len(st):
                keep = topn(st, N[aum]); keep = keep * st.sum() / keep.sum()
                for i, v in keep.items(): agg[i] = agg.get(i, 0) + v * m
        for i in sorted(agg):
            if not etf(i) and agg[i] > CAP: agg[BAL] = agg.get(BAL, 0) + agg[i] - CAP; agg[i] = CAP
        t = sum(agg.values()); rows += [(s, i, v / t) for i, v in agg.items()]
    W = pd.DataFrame(rows, columns=["session", "instrument", "weight"]).groupby(["session", "instrument"], as_index=False).weight.sum()
    W["date"] = W.session; W["target_weight"] = W.weight
    W["instrument_id"] = W.instrument.map(lambda x: x[-2:].lower() + "." + x[:6])
    W["mechanism_tag"] = "wf_combo_S6"; W["who_pays_zh"] = "组合层WF"; W["universe_id"] = "wf_combo"
    return W


def check(W: pd.DataFrame, aum: int, leg_chg: set) -> dict:
    F = pd.read_parquet(FROZEN[aum]); F["session"] = F.session.astype(str).str[:10]
    F = F[F.weight.abs() > 0].sort_values(["session", "instrument"]).reset_index(drop=True)
    H = W[W.session <= FROZEN_END]
    H = H[H.weight.abs() > 0].sort_values(["session", "instrument"]).reset_index(drop=True)
    keys = len(H) == len(F) and (H[["session", "instrument"]].values == F[["session", "instrument"]].values).all()
    dmax = float(np.abs(H.weight.values - F.weight.values).max()) if keys else float("inf")
    new = W[W.session > FROZEN_END]; stk = new[[not etf(i) for i in new.instrument]]
    r = dict(hist_rows=len(H), frozen_rows=len(F), hist_keys_identical=bool(keys), hist_max_abs_diff=dmax,
             hist_ok=bool(keys and dmax <= TOL), new_rows=len(new), new_sessions=sorted(new.session.unique().tolist()),
             new_max_single_stock=float(stk.weight.max()) if len(stk) else None,
             new_sum_ok=bool(((new.groupby("session").weight.sum() - 1).abs() < 1e-9).all()),
             new_nonneg=bool((new.weight >= 0).all()), new_cap_ok=bool(stk.weight.max() <= CAP + 1e-9) if len(stk) else True)
    hf = B.change_days(F); hw = [x for x in B.change_days(W) if x <= FROZEN_END]
    fchg = [x for x in B.change_days(W[W.session >= FROZEN_END]) if x > FROZEN_END]
    r.update(hist_change_days_identical=bool(hf == hw), n_hist_change_days=len(hf), new_change_days=fchg,
             leg_change_days_forward=sorted(x for x in leg_chg if x > FROZEN_END),
             hist_change_subset_of_leg_union=bool(set(hf) <= leg_chg))
    r["rhythm_ok"] = bool(r["hist_change_days_identical"] and set(fchg) <= leg_chg)
    r["ok"] = r["rhythm_ok"] and r["hist_ok"] and r["new_sum_ok"] and r["new_nonneg"] and r["new_cap_ok"]
    return r


def newest(k: str) -> Path:
    return B.newest_leg(k)


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--run-legs", action="store_true"); ap.add_argument("--legs-only-check", action="store_true")
    a = ap.parse_args(); dend = B.data_end()
    if a.run_legs and B.leg_end(newest("equity_incentive")) < dend: run_eq_leg(dend)
    legs = {k: newest(k) for k in MIX}; lend = {k: B.leg_end(p) for k, p in legs.items()}
    lchk = {k: B.leg_hist_check(k, p) for k, p in legs.items()}
    leg_chg = set()
    for p in legs.values(): leg_chg.update(B.change_days(pd.read_parquet(p, columns=["session", "instrument", "weight"])))
    info = dict(prereg="docs/v2/STRATEGY_S6_SHADOW_PREREG_ZH.md", data_end=dend, legs={k: str(p.relative_to(ROOT)) for k, p in legs.items()},
                leg_end=lend, leg_hist_check=lchk, params=dict(mix=MIX, N=N, cap=CAP, ballast=BAL, sess_start=SESS_START),
                seed=os.environ.get("PYTHONHASHSEED"), promotion_approved=False, live=False, forward_paper_start="2026-11-02")
    if a.legs_only_check: print(json.dumps(info, ensure_ascii=False, indent=1)); return 0
    if not all(v["ok"] for v in lchk.values()):
        print(json.dumps(dict(info, status="ABORT_LEG_HISTORY_MISMATCH"), ensure_ascii=False, indent=1)); return 4
    rc = 0
    for aum in (600000, 1000000):
        W = build(legs, aum); bp = B.booked_path(OUT, aum); booked = None
        if bp is not None:
            W, booked = B.splice_booked(W, bp)
            if booked["deferred_rebalance_day"]: leg_chg = leg_chg | {booked["deferred_rebalance_day"]}
            # Option A (Arch APPROVE 20261026): same semantics as b4 — booked realized change days ∪ into leg_chg
            leg_chg |= set(B.change_days(pd.read_parquet(bp, columns=["session", "instrument", "weight"])))
        last = W.session.max(); c = check(W, aum, leg_chg)
        fp = OUT / f"S6_cap50_ee25_eq25_topN_{aum // 10000}w_{last.replace('-', '')}.parquet"
        res = dict(info, aum=aum, last_session=last, check=c, file=str(fp.relative_to(ROOT)), frozen_script_sha256=B.script_shas(TRACK_SCRIPTS),
                   leg_sha256={k: B.sha(p) for k, p in legs.items()}, leg_check_json={k: B.leg_check_path(p).exists() for k, p in legs.items()},
                   frozen_ref=str(FROZEN[aum].relative_to(ROOT)), frozen_ref_sha256=B.sha(FROZEN[aum]), booked_days=booked)
        if not c["ok"]: res["status"] = "ABORT_SELFCHECK"; rc = 2
        else:
            tmp = fp.with_suffix(".tmp.parquet"); W.to_parquet(tmp, index=False)
            if fp.exists():
                same = pd.read_parquet(fp).equals(pd.read_parquet(tmp)); tmp.unlink()
                res["status"] = "NOOP_EXISTS_IDENTICAL" if same else "ABORT_EXISTS_DIFFERENT"; rc = rc or (0 if same else 3)
            else: tmp.rename(fp); res["status"] = "WRITTEN"
            res["sha256"] = B.sha(fp)
        fp.with_suffix(".check.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str))
        print(json.dumps(dict(aum=aum, last=last, status=res["status"], sha256=res.get("sha256"), hist_ok=c["hist_ok"],
                              max_diff=c["hist_max_abs_diff"], rhythm=c["rhythm_ok"], new=c["new_change_days"], new_rows=c["new_rows"],
                              keys=c["hist_keys_identical"], rows=(c["hist_rows"], c["frozen_rows"])), ensure_ascii=False))
    return rc


if __name__ == "__main__":
    sys.exit(main())
