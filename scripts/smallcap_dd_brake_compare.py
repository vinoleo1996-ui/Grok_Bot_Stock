"""Small-cap β sleeve: buffer drawdown brake vs no brake (research; promotion_approved=false).

Harness follows the FIXED engine rules (Strategy 2026-10-10): holdings always marked to
close; limit-up blocks buys, limit-down blocks sells, halt blocks both; blocked orders
roll forward to the next tradable day; costs from Mandate (commission 2.5bp min 5 CNY,
slippage 5bp, stamp tax by date via v2_execution_costs.stamp_tax_bps_sell); min trade
2,000 CNY. It is a Beta-side harness reusing those primitives — NOT Strategy's paper
engine and not yet cross-validated against it.
Lot rounding not modelled (research notional 5M clears 1 lot for all names; see doc).
"""
from __future__ import annotations

import json
import math
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from quantlab.beta.dd_brake import BrakeParams, calibrate_gamma, concavity_check, exposure_map, smooth_step
from quantlab.beta.smallcap_sleeve import SmallcapBetaSleeveProvider
from quantlab.mandate_v2 import load_mandate_v2
from quantlab.portfolio.v2_execution_costs import DEFAULT_MIN_TRADE_NOTIONAL_CNY, mandate_costs, stamp_tax_bps_sell

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/v2_proto/smallcap_dd_brake_compare.json"
START = pd.Timestamp("2023-12-29")


def build_schedule(sc, D, every):
    idx = D.close.index
    s0 = int(np.searchsorted(idx, START))
    cfg_hist = int(sc.config()["universe"]["min_history_sessions"])
    sched, prev, truncated = {}, None, 0
    for t in range(s0, len(idx), every):
        avail = t + 1
        ov = max(120, avail - 20) if avail <= cfg_hist else None
        truncated += ov is not None
        b = sc.basket(idx[t].date(), current=prev, min_history_override=ov)
        if b.names:
            sched[t] = list(b.names)
            prev = list(b.names)
    return s0, sched, truncated


def simulate(D, cols, s0, sched, K, policy, costs, bp):
    idx = D.close.index
    R = np.nan_to_num(D.ret.values, nan=0.0)
    LU, LD, TR = D.lu.values, D.ld.values, D.trad.values
    hold = {}  # col -> CNY
    cash, peak = K, K
    desired, pending, names = {}, set(), []
    e_dec = None
    navs, expo, turn, tfloor, cost_tot, nan_held = [], [], 0.0, 0, 0.0, 0
    raw_ret = D.ret.values
    for t in range(s0, len(idx)):
        if t > s0:
            for c in list(hold):
                if raw_ret[t, c] != raw_ret[t, c]:
                    nan_held += 1
                hold[c] *= 1.0 + R[t, c]
        V = cash + sum(hold.values())
        # execute orders decided at close t-1
        if pending:
            sess = idx[t].date()
            done = set()
            for c in pending:
                tgt = desired.get(c, 0.0) * V
                cur = hold.get(c, 0.0)
                d = tgt - cur
                halt = TR[t, c] != 1
                if d > 0 and (LU[t, c] == 1 or halt):
                    continue
                if d < 0 and (LD[t, c] == 1 or halt):
                    continue
                if abs(d) < DEFAULT_MIN_TRADE_NOTIONAL_CNY and tgt > 0:
                    done.add(c); continue
                fee = max(abs(d) * costs.commission_bps_one_way / 1e4, costs.commission_min_cny_per_order)
                fee += abs(d) * costs.slippage_bps_one_way / 1e4
                if d < 0:
                    fee += -d * stamp_tax_bps_sell(sess) / 1e4
                hold[c] = cur + d
                if hold[c] <= 1e-6:
                    hold.pop(c, None)
                cash -= d + fee
                cost_tot += fee
                turn += abs(d) / V
                done.add(c)
            pending -= done
            V = cash + sum(hold.values())
        peak = max(peak, V)
        z = V / peak
        navs.append(V / K)
        expo.append(sum(hold.values()) / V if V > 0 else 0.0)
        # decide at close t
        new_basket = t in sched
        if new_basket:
            names = sched[t]
        if not names:
            continue
        if policy == "brake":
            tgt_e = exposure_map(z, bp)
            e_new = tgt_e if e_dec is None else smooth_step(e_dec, tgt_e, bp)
        else:
            e_new = float(policy)
        if e_new <= bp.floor + 1e-9:
            tfloor += 1
        if new_basket or e_dec is None or abs(e_new - e_dec) > bp.trade_band:
            e_dec = e_new
            w = e_dec / len(names)
            desired = {c: w for c in names}
            pending = set(desired) | set(hold)
    nav = pd.Series(navs, index=idx[s0:])
    return nav, np.array(expo), turn, tfloor, cost_tot, nan_held


def metrics(nav, expo, turn, tfloor, cost, nan_held, K, tier_w):
    n = len(nav) - 1
    yrs = n / 252
    cagr = nav.iloc[-1] ** (1 / yrs) - 1
    dd = nav / nav.cummax() - 1
    mdd = float(dd.min())
    r = nav.pct_change().dropna()
    vol = float(r.std() * math.sqrt(252))
    book = 1 + tier_w * (nav - 1)
    bdd = float((book / book.cummax() - 1).min())
    return {
        "cagr": float(cagr), "mdd": mdd, "calmar": float(cagr / -mdd) if mdd < 0 else None,
        "ann_vol": vol, "turnover_one_way_per_year": float(turn / yrs),
        "avg_exposure": float(expo[1:].mean()), "min_exposure": float(expo[1:].min()),
        "time_at_floor_frac": tfloor / len(nav), "cost_cny": float(cost), "cost_frac_of_sleeve_capital": float(cost / K),
        "mdd_date": str(dd.idxmin().date()), "held_name_days_ret_missing_marked_flat": nan_held,
        "book_contribution_mdd": bdd, "book_contribution_cagr": float((book.iloc[-1]) ** (1 / yrs) - 1),
    }


def main():
    m = load_mandate_v2()
    sc = SmallcapBetaSleeveProvider(m)
    cfg = sc.config()
    bc = cfg["dd_brake"]
    D = sc._panels()
    cols = {c: i for i, c in enumerate(D.close.columns)}
    costs = mandate_costs(m)
    s0, sched_named, truncated = build_schedule(sc, D, int(bc["rebalance_every_sessions"]))
    sched = {t: [cols[c] for c in v if c in cols] for t, v in sched_named.items()}
    # γ calibration: basket at start; empirical window = panel start .. start (pre-sim)
    first = sched_named[s0]
    ew = D.ret[first].iloc[: s0 + 1].mean(axis=1)
    two = 1 - (1 + ew).rolling(2).apply(np.prod, raw=True)
    cal = calibrate_gamma(first, two.dropna().tolist())
    ew_full = D.ret[first].iloc[s0:].mean(axis=1)
    cal["ex_post_info_worst_two_day_in_sim_window_same_basket"] = float((1 - (1 + ew_full).rolling(2).apply(np.prod, raw=True)).max())
    bp = BrakeParams(dd_limit=float(bc["dd_limit"]), gamma=float(cal["gamma"]), floor=float(bc["floor"]),
                     rerisk_max_step=float(bc["rerisk_max_step"]), trade_band=float(bc["trade_band"]))
    tiers = {k: float(v) for k, v in cfg["tiers"].items()}
    notional = float(cfg["risk_controls"]["research_notional_cny"])
    res = {}
    for tid, w in tiers.items():
        K = notional * w
        arms = {}
        for name, pol in [("no_brake", 1.0), ("brake", "brake")]:
            arms[name] = metrics(*simulate(D, cols, s0, sched, K, pol, costs, bp), K, w)
        bp30 = BrakeParams(dd_limit=0.30, gamma=bp.gamma, floor=bp.floor, rerisk_max_step=bp.rerisk_max_step, trade_band=bp.trade_band)
        arms["brake_sens_dd30"] = {"dd_limit": 0.30, "sensitivity_not_preregistered": True, **metrics(*simulate(D, cols, s0, sched, K, "brake", costs, bp30), K, w)}
        e_sv = round(arms["brake"]["ann_vol"] / arms["no_brake"]["ann_vol"], 2)
        arms["same_vol_static"] = {"static_exposure": e_sv, **metrics(*simulate(D, cols, s0, sched, K, e_sv, costs, bp), K, w)}
        grid = {}
        for e in [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
            grid[e] = metrics(*simulate(D, cols, s0, sched, K, e, costs, bp), K, w)
        be = max(grid, key=lambda e: grid[e]["calmar"] or -9)
        arms["ex_post_best_static"] = {"static_exposure": be, "look_ahead_reference_only": True, **grid[be]}
        res[tid] = {"book_weight": w, "sleeve_capital_cny": K, "arms": arms}
        print(tid, {a: (round(v["cagr"], 4), round(v["mdd"], 4), v["calmar"] and round(v["calmar"], 2)) for a, v in arms.items()}, flush=True)
    out = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "promotion_approved": False,
        "label": "RESEARCH. Fixed-engine rules (mark-to-close, blocked orders roll forward) via Beta harness reusing v2_execution_costs primitives; NOT Strategy's paper engine; not cross-validated. Sleeve-level NAV; cash earns 0.",
        "window": [str(D.close.index[s0].date()), str(D.close.index[-1].date())],
        "rebalances": len(sched), "rebalances_with_truncated_history": truncated,
        "brake_params": {**bc, "gamma_value": bp.gamma}, "gamma_calibration": cal,
        "concavity_check": concavity_check(bp), "concavity_check_dd30": concavity_check(BrakeParams(0.30, bp.gamma, bp.floor, bp.rerisk_max_step, bp.trade_band)),
        "provider_default_enabled": bc["provider_default_enabled"],
        "tiers": res,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str))
    print(json.dumps({k: out[k] for k in ["window", "rebalances", "gamma_calibration", "concavity_check"]}, indent=1, default=str))


if __name__ == "__main__":
    sys.exit(main())
