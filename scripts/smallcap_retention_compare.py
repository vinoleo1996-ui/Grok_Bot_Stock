"""Holding-retention buffer compare: research 50 @5M vs live 600k, buffer multiples of N.
RESEARCH-ONLY Beta harness (fixed-engine rules), NOT cross-checked vs Strategy's engine. promotion_approved=false."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

from quantlab.beta.dd_brake import BrakeParams
from quantlab.beta.smallcap_sleeve import SmallcapBetaSleeveProvider
from quantlab.mandate_v2 import load_mandate_v2
from quantlab.portfolio.v2_execution_costs import mandate_costs

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/v2_proto/smallcap_retention_compare.json"
spec = importlib.util.spec_from_file_location("ddc", ROOT / "scripts/smallcap_dd_brake_compare.py")
ddc = importlib.util.module_from_spec(spec); spec.loader.exec_module(ddc)
MULTS = [0.0, 1.5, 2.0, 3.0]
KEEP = ["cagr", "mdd", "calmar", "ann_vol", "turnover_one_way_per_year", "cost_frac_of_sleeve_capital"]


def main():
    m = load_mandate_v2()
    sc = SmallcapBetaSleeveProvider(m)
    cfg = sc.config()
    D = sc._panels()
    cols = {c: i for i, c in enumerate(D.close.columns)}
    idx = D.close.index
    s0 = int(np.searchsorted(idx, ddc.START))
    every = int(cfg["dd_brake"]["rebalance_every_sessions"])
    hist = int(cfg["universe"]["min_history_sessions"])
    N = int(cfg["selection"]["target_names"])
    costs = mandate_costs(m)
    bp = BrakeParams(0.2, 3.4, 0.2, 0.05, 0.05)
    days = list(range(s0, len(idx), every))
    ov = {t: (max(120, t + 1 - 20) if t + 1 <= hist else None) for t in days}
    res = {"label": "RESEARCH-ONLY Beta harness: fixed-engine rules (mark-to-close, blocked orders roll forward, Mandate costs, 2,000 CNY min trade), no brake; NOT cross-checked vs Strategy's engine",
           "window": [str(idx[s0].date()), str(idx[-1].date())], "rebalance_every_sessions": every,
           "buffer_rule": "keep a current holding if it is still eligible (band+filters) and its position in the selection ranking is within retain_mult x N; else replace from the top",
           "promotion_approved": False, "research50": {}, "live600k": {}}
    base = {}  # research baskets per mult (also gives ranked_pool for live)
    for k in MULTS:
        prev, sched = None, {}
        for t in days:
            b = sc.basket(idx[t].date(), current=prev if k > 0 else None,
                          min_history_override=ov[t], retain_top_override=int(round(k * N)))
            if b.names:
                sched[t] = b; prev = list(b.names)
        base[k] = sched
    for tier, w in cfg["tiers"].items():
        res["research50"][tier], res["live600k"][tier] = {}, {}
        for k in MULTS:
            sr = {t: [cols[c] for c in b.names] for t, b in base[k].items()}
            r = ddc.metrics(*ddc.simulate(D, cols, s0, sr, 5_000_000 * w, 1.0, costs, bp), 5_000_000 * w, w)
            res["research50"][tier][f"x{k}"] = {x: r[x] for x in KEEP}
            prev, sl = None, {}
            for t, b in base[0.0].items():
                lv = sc.live_basket(b, tier, current=prev, retain_mult=k)
                sl[t] = [cols[c] for c in lv["names"]]; prev = lv["names"]
            l = ddc.metrics(*ddc.simulate(D, cols, s0, sl, 600_000 * w, 1.0, costs, bp), 600_000 * w, w)
            res["live600k"][tier][f"x{k}"] = {x: l[x] for x in KEEP}
            print(tier, k, "R", round(r["turnover_one_way_per_year"], 2), round(r["calmar"], 3), "L", round(l["turnover_one_way_per_year"], 2), round(l["calmar"], 3), flush=True)
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
