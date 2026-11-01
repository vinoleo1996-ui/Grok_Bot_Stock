"""Live 600k profile for the small-cap β sleeve (20-30 names) vs the 50-name research basket.
Research-only; promotion_approved=false. Stress + harness numbers are descriptive / Beta harness
(fixed-engine rules, NOT Strategy's engine, not cross-validated)."""
from __future__ import annotations

import importlib.util
import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from quantlab.beta import VolTargetBetaSleeveProvider
from quantlab.beta.smallcap_sleeve import SmallcapBetaSleeveProvider
from quantlab.mandate_v2 import load_mandate_v2
from quantlab.portfolio.v2_execution_costs import mandate_costs

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/v2_proto/smallcap_beta_sleeve.json"
SESSIONS = [date(2026, 6, 30), date(2026, 10, 9)]
spec = importlib.util.spec_from_file_location("ddc", ROOT / "scripts/smallcap_dd_brake_compare.py")
ddc = importlib.util.module_from_spec(spec); spec.loader.exec_module(ddc)


def strip(d):
    return {k: v for k, v in d.items() if not k.startswith("_")}


def main():
    m = load_mandate_v2()
    sc, core = SmallcapBetaSleeveProvider(m), VolTargetBetaSleeveProvider(m)
    cfg = sc.config()
    D = sc._panels()
    sec = {"profile": cfg["live_profile"], "promotion_approved": False, "by_session": {}}
    for s in SESSIONS:
        pl = sc.plan(s, core_plan=core.plan(s))
        b = pl.basket
        it = pl.interaction_with_core["T20"]
        row = {}
        for t in cfg["tiers"]:
            lv = sc.live_basket(b, t)
            assert lv["lot_unaffordable"] == 0 and lv["below_min_trade"] == 0
            bd = sc.beta_descriptive(lv["_basket"])
            r = strip(lv)
            r["live_unit_beta_vs_510300_descriptive"] = bd.get("basket_unit_beta_vs_510300")
            if t == "T20":
                r["t20_core_plus_smallcap_beta"] = it["core_plus_smallcap_beta"] - it["smallcap_weight"] * it["smallcap_unit_beta_used"] + it["smallcap_weight"] * (bd.get("basket_unit_beta_vs_510300") or 0.0)
                r["t20_core_plus_smallcap_beta_research50"] = it["core_plus_smallcap_beta"]
            row[t] = r
        sec["by_session"][str(s)] = row
    # stress basket 2023-12-29
    st_spec = next(x for x in cfg["stress_tests"] if x["id"] == "smallcap_crash_2024_02")
    b0 = sc.basket(date(2023, 12, 29), min_history_override=222)
    lo, hi = pd.Timestamp(st_spec["window_start"]), pd.Timestamp(st_spec["window_end"])

    def dd(names):
        r = D.ret[names].loc[lo:hi].fillna(0).mean(axis=1)
        nav = (1 + r).cumprod()
        return float((nav / nav.cummax() - 1).min()), float(nav.iloc[-1] - 1)
    stress = {"label": "pre-engine-fix descriptive, raw adjusted prices, EW, no costs, limit-down not modelled — NOT a performance claim",
              "research50": dict(zip(["max_dd", "window_return"], dd(list(b0.names)))), "n_research": len(b0.names)}
    for t in cfg["tiers"]:
        lv = sc.live_basket(b0, t)
        stress[t] = {"n": lv["n"], "overlap_with_research": lv["overlap_with_research_basket"], **dict(zip(["max_dd", "window_return"], dd(lv["names"])))}
    sec["stress_2024_02"] = stress
    # Beta harness, no brake: live vs research50
    bc = cfg["dd_brake"]
    cols = {c: i for i, c in enumerate(D.close.columns)}
    idx = D.close.index
    s0 = int(np.searchsorted(idx, ddc.START))
    every = int(bc["rebalance_every_sessions"])
    baskets, prev = {}, None
    for t in range(s0, len(idx), every):
        ov = max(120, t + 1 - 20) if t + 1 <= int(cfg["universe"]["min_history_sessions"]) else None
        bb = sc.basket(idx[t].date(), current=prev, min_history_override=ov)
        if bb.names:
            baskets[t] = bb; prev = list(bb.names)
    costs = mandate_costs(m)
    from quantlab.beta.dd_brake import BrakeParams
    bp = BrakeParams(0.2, 3.4, 0.2, 0.05, 0.05)
    harness = {"label": "RESEARCH-ONLY Beta harness, fixed-engine rules, no brake, NOT cross-checked vs Strategy engine; lots not modelled in sim (live names pre-screened for 1 lot)"}
    for t, w in cfg["tiers"].items():
        sched_r = {k: [cols[c] for c in v.names] for k, v in baskets.items()}
        sched_l = {k: [cols[c] for c in sc.live_basket(v, t)["names"]] for k, v in baskets.items()}
        r = ddc.metrics(*ddc.simulate(D, cols, s0, sched_r, 5_000_000 * w, 1.0, costs, bp), 5_000_000 * w, w)
        l = ddc.metrics(*ddc.simulate(D, cols, s0, sched_l, 600_000 * w, 1.0, costs, bp), 600_000 * w, w)
        keep = ["cagr", "mdd", "calmar", "ann_vol", "turnover_one_way_per_year", "cost_frac_of_sleeve_capital", "mdd_date"]
        harness[t] = {"research50_at_5M": {k: r[k] for k in keep}, "live_at_600k": {k: l[k] for k in keep}}
    sec["harness_no_brake"] = harness
    sec["window"] = [str(idx[s0].date()), str(idx[-1].date())]
    (ROOT / "output/v2_proto/smallcap_live_profile.json").write_text(json.dumps(sec, ensure_ascii=False, indent=2, default=str))
    o = json.loads(OUT.read_text())
    o["live_profile"] = sec
    OUT.write_text(json.dumps(o, ensure_ascii=False, indent=2, default=str))
    print(json.dumps(sec, ensure_ascii=False, indent=1, default=lambda x: str(x))[:6000])


if __name__ == "__main__":
    main()
