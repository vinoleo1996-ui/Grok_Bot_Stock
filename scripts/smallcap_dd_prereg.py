#!/usr/bin/env python3
"""Runner for docs/v2/BETA_SMALLCAP_DD_PREREG.md (locked by Leo 2026-10-11 10:48 ET; addendum 12:0x ET).

Usage: smallcap_dd_prereg.py --window explore_a|explore_b|sealed --engine-sha <sha256> --ex-rights-fixed
Sealed window: lock written at START (status=started), updated at end (status=done); any existing lock refuses a rerun.
Research-only; promotion_approved=false.
"""
from __future__ import annotations

import argparse, hashlib, json, math, sys, time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
OUT = ROOT / "output/v2_proto/smallcap_dd_prereg"
ETF = "sh.510300"
CAP = 5_000_000.0
EVERY = 20
WINDOWS = {"explore_a": ("2015-06-01", "2017-12-29"), "explore_b": ("2024-06-03", "2026-10-09"),
           "sealed": ("2018-01-02", "2024-05-31")}
ARMS = {  # frozen parameters (prereg §3)
    "B100": {"kind": "static", "w_sc": 1.0},
    "MIX": {"kind": "static", "w_sc": 0.60, "w_etf": 0.20},
    "VT": {"kind": "voltarget", "sigma_target": 0.20, "lookback": 60, "band": 0.05},
    "BRAKE": {"kind": "brake", "dd_limit": 0.20, "floor": 0.20, "rerisk_max_step": 0.05, "trade_band": 0.05},
    "C_SV": {"kind": "static_samevol", "match": "VT"},
}
BASKET = dict(band="cap", fund=True, excl=True, ind_cap=12, st_pre=False, survivor_only=False)  # L6
WARMUP_DAYS = 420  # calendar days before start for VT/BRAKE signals (>=250 sessions)


def log(*a):
    print(f"[dd-prereg {time.strftime('%H:%M:%S')}]", *a, flush=True)


def engine_sha():
    import quantlab.platform.execution as ex
    return hashlib.sha256(Path(ex.__file__).read_bytes()).hexdigest()


def metrics(nav, res, aw, extra=None):
    r = nav.pct_change().dropna(); yrs = len(r) / 252
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1 / yrs) - 1
    mdd = float((nav / nav.cummax() - 1).min())
    sc = aw.drop(columns=[ETF], errors="ignore").fillna(0).sum(axis=1).loc[nav.index]
    out = {"cagr": float(cagr), "mdd": mdd, "calmar": float(cagr / -mdd) if mdd < 0 else None,
           "sharpe": float(r.mean() / r.std() * math.sqrt(252)), "vol": float(r.std() * math.sqrt(252)),
           "avg_smallcap_exposure": float(sc.mean()), "min_smallcap_exposure": float(sc.min()),
           "turnover_one_way_per_year": float(res["filled_notional"] / 2 / nav.mean() / yrs),
           "cost_frac_per_year": float(res["total_cost"] / CAP / yrs),
           "costs": {k: round(float(v)) for k, v in res["costs"].items()}, "fill_ratio": float(res["fill_ratio"]),
           "corporate_action_cash": float(res.get("corporate_action_cash", float("nan"))),
           "corporate_action_events": int(res.get("corporate_action_events", -1)),
           "start": str(nav.index[0].date()), "end": str(nav.index[-1].date())}
    out.update(extra or {})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", choices=list(WINDOWS), required=True)
    ap.add_argument("--engine-sha", required=True)
    ap.add_argument("--ex-rights-fixed", action="store_true")
    a = ap.parse_args()
    sha0 = engine_sha()
    if not a.ex_rights_fixed or a.engine_sha != sha0:
        raise SystemExit("blocked: waiting for Eng ex-dividend/ex-rights fix (pass --ex-rights-fixed and matching --engine-sha)")
    OUT.mkdir(parents=True, exist_ok=True)
    lock = OUT / f"{a.window}.lock"
    if a.window == "sealed":
        if lock.exists():
            raise SystemExit(f"sealed window already run once ({lock}); no re-runs per prereg")
        lock.write_text(json.dumps({"status": "started", "engine_sha": sha0, "at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}))

    import smallcap_reconcile as R
    from quantlab.beta.dd_brake import BrakeParams, calibrate_gamma, exposure_map, smooth_step
    from quantlab.platform.execution import ExecConfig, load_execution_panels, run_weight_schedule
    from quantlab.data.v2_readers import load_merged_panel

    s, e = WINDOWS[a.window]
    t0 = time.time()
    select, fm = R.make_selector()
    dates, B = R.baskets_for(select, fm, s, e, BASKET)
    sizes = [len(v) for v in B.values()]
    log("baskets", len(dates), "sizes", min(sizes), max(sizes))
    ids = sorted({c for v in B.values() for c in v})
    lo = (pd.Timestamp(s) - pd.Timedelta(days=WARMUP_DAYS)).date()
    panels, pdiag = load_execution_panels(ids + [ETF], lo, e)
    log("panels", panels.close.shape, "missing", len(pdiag["missing_ids"]))
    # signal-layer adjusted returns (factor = hfq ratio); never used for fills
    fac = {}
    for c in ids:
        f = load_merged_panel(c).frame
        x = pd.Series(pd.to_numeric(f["factor"], errors="coerce").to_numpy(), index=pd.to_datetime(f["event_time"]).dt.normalize())
        fac[c] = x[~x.index.duplicated(keep="last")]
    F = pd.DataFrame(fac).reindex(panels.close.index).ffill()
    adj_ret = (panels.close[ids] * F).pct_change(fill_method=None)
    sess = panels.close.index
    win_days = sess[(sess >= pd.Timestamp(s)) & (sess <= pd.Timestamp(e))]

    def basket_on(day):
        ks = [d for d in dates if d <= day]
        return B[ks[-1]] if ks else None

    def ew_ret(names, idx):
        return adj_ret.loc[idx, names].mean(axis=1, skipna=True)

    cfg = ExecConfig.strategy_v1(impact_k=1.0, min_trade_value=2000.0)
    assert cfg.corporate_actions is True

    def run(sched, extra=None):
        res = run_weight_schedule(panels, sched, initial_cash=CAP, config=cfg, record_weights=True)
        nav = res["nav"].loc[pd.Timestamp(s):]
        aw = res["actual_weights"]
        row = {"base": None}
        for tag, sc_ in (("delist_minus50", 0.5), ("delist_minus100", 1.0)):
            n2, hits = R.delist_overlay(nav, aw.loc[nav.index], sc_)
            row[tag] = metrics(n2, res, aw, {"delist_hits": hits, **(extra or {})})
        row.pop("base")
        return row, nav

    results = {}
    # B100 / MIX
    results["B100"], nav_b = run({d: {c: 1.0 / len(B[d]) for c in B[d]} for d in dates})
    results["MIX"], _ = run({d: {**{c: 0.60 / len(B[d]) for c in B[d]}, ETF: 0.20} for d in dates})
    log("B100", round(results["B100"]["delist_minus50"]["cagr"], 4), "MIX", round(results["MIX"]["delist_minus50"]["cagr"], 4))
    # VT
    P = ARMS["VT"]; sched, prev, ex_path = {}, None, {}
    for d in dates:
        k = sess.get_loc(d); idx = sess[max(0, k - P["lookback"] + 1): k + 1]
        sig = float(ew_ret(B[d], idx).std() * math.sqrt(252))
        tgt = min(1.0, P["sigma_target"] / sig) if sig > 0 else 1.0
        ex_ = tgt if prev is None or abs(tgt - prev) >= P["band"] else prev
        prev = ex_; ex_path[str(d.date())] = round(ex_, 4)
        sched[d] = {c: ex_ / len(B[d]) for c in B[d]}
    results["VT"], nav_vt = run(sched, {"planned_exposure_by_rebalance": ex_path})
    log("VT", round(results["VT"]["delist_minus50"]["cagr"], 4))
    # BRAKE
    P = ARMS["BRAKE"]
    k0 = sess.get_loc(win_days[0]); pre = sess[max(0, k0 - 250): k0]
    r1 = ew_ret(B[dates[0]], pre).fillna(0)
    two = -((1 + r1).rolling(2).apply(np.prod, raw=True) - 1).dropna()
    g = calibrate_gamma(B[dates[0]], list(two.values))
    bp = BrakeParams(dd_limit=P["dd_limit"], gamma=g["gamma"], floor=P["floor"],
                     rerisk_max_step=P["rerisk_max_step"], trade_band=P["trade_band"])
    sched, nav_s, peak, e_cur, held = {}, 1.0, 1.0, 1.0, None
    planned = []
    for i, d in enumerate(win_days):
        names = basket_on(d)
        if i > 0:
            rt = float(ew_ret(basket_on(win_days[i - 1]), [d]).fillna(0).iloc[0])
            nav_s *= 1 + e_cur * rt; peak = max(peak, nav_s)
        e_new = smooth_step(e_cur, exposure_map(nav_s / peak, bp), bp)
        e_cur = e_new; planned.append(e_cur)
        if d in B or held is None or abs(e_cur - held) >= bp.trade_band:
            held = e_cur; sched[d] = {c: held / len(names) for c in names}
    pe = pd.Series(planned, index=win_days)
    results["BRAKE"], _ = run(sched, {"gamma_calibration": g, "time_at_floor": float((pe <= bp.floor + 1e-9).mean()),
                                      "planned_exposure_avg": float(pe.mean()), "n_schedule_days": len(sched)})
    log("BRAKE", round(results["BRAKE"]["delist_minus50"]["cagr"], 4), "gamma", round(g["gamma"], 3))
    # C_SV
    v_vt = nav_vt.pct_change().std(); v_b = nav_b.pct_change().std()
    w = float(min(1.0, v_vt / v_b))
    results["C_SV"], _ = run({d: {c: w / len(B[d]) for c in B[d]} for d in dates}, {"static_weight": w, "matched_to": "VT"})
    log("C_SV w", round(w, 3), round(results["C_SV"]["delist_minus50"]["cagr"], 4))

    sha1 = engine_sha()
    verdict = None
    if a.window == "sealed":
        m = {k: v["delist_minus50"] for k, v in results.items()}
        verdict = {}
        for arm in ("MIX", "VT", "BRAKE"):
            ref = "B100" if arm == "MIX" else "C_SV"
            c1 = m[arm]["mdd"] >= -0.25; c2 = (m[arm]["calmar"] or -9) > (m[ref]["calmar"] or -9); c3 = m[arm]["cagr"] >= 0.10
            st = "pass" if c1 and c2 and c3 else ("partial" if c1 and c2 and m[arm]["cagr"] >= 0.08 else "fail")
            verdict[arm] = {"mdd_ok": c1, "calmar_beats_" + ref: c2, "cagr_ge_10": c3, "status": st}
        passed = [x for x in ("MIX", "VT", "BRAKE") if verdict[x]["status"] == "pass"]
        verdict["selected"] = passed[0] if passed else None
    summary = {"promotion_approved": False, "window": a.window, "dates": WINDOWS[a.window], "arms": ARMS,
               "basket": BASKET, "basket_sizes": [min(sizes), max(sizes)], "n_rebalances": len(dates),
               "engine": {"call": "run_weight_schedule · ExecConfig.strategy_v1(impact_k=1.0, min_trade_value=2000), corporate_actions=True",
                          "sha_before": sha0, "sha_after": sha1, "unchanged": sha0 == sha1},
               "missing_ids": pdiag["missing_ids"], "results": results, "verdict": verdict,
               "elapsed_s": round(time.time() - t0, 1)}
    (OUT / f"{a.window}.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1, default=str))
    if a.window == "sealed":
        lock.write_text(json.dumps({"status": "done", "engine_sha": sha0, "unchanged": sha0 == sha1,
                                    "at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}))
    log("done", a.window, "engine unchanged", sha0 == sha1, summary["elapsed_s"], "s")


if __name__ == "__main__":
    main()
