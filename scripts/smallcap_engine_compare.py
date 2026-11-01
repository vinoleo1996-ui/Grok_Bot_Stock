"""Full-pool small-cap standalone-β comparison on Eng's platform engine (fixed convention).

Engine: quantlab.platform.execution.run_weight_schedule with ExecConfig.strategy_v1(impact_k=1.0)
(next_open fills, 0.01 tick, lot rounding on target, 10% participation cap, unfilled carry,
limit enforcement) + min_trade_value=2000 (Mandate). 510300 is one more code in the schedule
(price series spliced from data/v2/etf_510300 because the merged reader stops at 2026-06-30).

Arms (book level, research notional 5,000,000 CNY):
  A0  : 510300 at VolTargetBetaSleeveProvider.plan(d).etf_sleeve_weight; REST = CASH
        (Strategy's M01+EP residual stock book is NOT included — that baseline is their arm A).
  S10/S15/S20 : A0 + smallcap sleeve at 10/15/20% of book (EW ~50 names, B1 ranking).
  C2  : static 510300 at A0's average ETF weight + static smallcap at 15% (no vol/drawdown timing).
  C3  : static smallcap-only at weight w_c3 chosen so raw-return vol ≈ S15 raw vol (ex-post calibrated
        reference, "naive portfolio most likely to beat us"); rest cash.
Terminal delist: engine marks a delisted holding at its last close forever. NAV overlay subtracts
  scenario × (held value at last_trade_date close) from every NAV point after last_trade_date
  (−50% primary, −100% sensitivity). Applied post-engine; documented.
Research-only; promotion_approved=false. Mandate JSON untouched.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from datetime import date, datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ETF = "sh.510300"


def log(*a):
    print(f"[sc-engine {time.strftime('%H:%M:%S')}]", *a, flush=True)


def rebalance_dates(start, end, every):
    from quantlab.beta.survivorship import load_full_market_float_mktcap
    idx = load_full_market_float_mktcap().index
    s = idx[(idx >= pd.Timestamp(start)) & (idx <= pd.Timestamp(end))]
    return list(s[::every])


def build_baskets(dates):
    from quantlab.beta.smallcap_history_selector import select
    out, prev, diag = {}, None, []
    for d in dates:
        r = select(d, current=prev)
        out[d] = r["names"]; prev = r["names"]
        diag.append({k: r.get(k) for k in ("session", "band_mode", "universe", "pool", "fund_pass", "fund_fallback",
                                            "retained", "history_truncated", "n_industries", "max_per_industry")})
    return out, diag


def etf_plan(dates):
    from quantlab.beta import VolTargetBetaSleeveProvider
    from quantlab.mandate_v2 import load_mandate_v2
    v = VolTargetBetaSleeveProvider(load_mandate_v2())
    return {d: float(v.plan(d.date()).etf_sleeve_weight) for d in dates}


def splice_etf(panels, start, end):
    from quantlab.data.v2_readers import load_etf_510300
    pf = load_etf_510300().panel_frame.copy()
    pf["d"] = pd.to_datetime(pf["event_time"]).dt.normalize()
    pf = pf.drop_duplicates("d", keep="last").set_index("d").loc[pd.Timestamp(start):pd.Timestamp(end)]
    idx = panels.close.index.union(pf.index)
    def put(df, col):
        df = df.reindex(idx)
        if col in pf.columns:
            df[ETF] = pd.to_numeric(pf[col], errors="coerce").reindex(idx).astype("float32")
        return df
    panels.close = put(panels.close, "close"); panels.open = put(panels.open, "open")
    panels.high = put(panels.high, "high"); panels.low = put(panels.low, "low")
    panels.amount = put(panels.amount, "amount"); panels.volume = put(panels.volume, "volume")
    panels.limit_up = put(panels.limit_up, "limit_up"); panels.limit_down = put(panels.limit_down, "limit_down")
    if panels.suspended is not None:
        panels.suspended = panels.suspended.reindex(idx).fillna(False).astype(bool)
        panels.suspended[ETF] = False
    return panels


def schedules(dates, baskets, etf_w, c3_w=None):
    avg_etf = float(np.mean(list(etf_w.values())))
    arms = {"A0": {}, "S10": {}, "S15": {}, "S20": {}, "C2": {}, "C3": {}}
    for d in dates:
        names = baskets[d]; n = max(1, len(names))
        arms["A0"][d] = {ETF: etf_w[d]}
        for k, tier in (("S10", 0.10), ("S15", 0.15), ("S20", 0.20)):
            w = {c: tier / n for c in names}; w[ETF] = etf_w[d]; arms[k][d] = w
        w = {c: 0.15 / n for c in names}; w[ETF] = avg_etf; arms["C2"][d] = w
        if c3_w is not None:
            arms["C3"][d] = {c: c3_w / n for c in names}
    return arms, avg_etf


def raw_vol_calibrate(panels, dates, baskets, etf_w):
    """Raw close-to-close vol of S15 vs EW smallcap → C3 static weight (no engine, ex-post)."""
    r = panels.close.ffill(limit_area="inside").pct_change(fill_method=None)
    s15, sc = [], []
    seg = list(dates) + [r.index[-1] + pd.Timedelta(days=1)]
    for i, d in enumerate(dates):
        sub = r.loc[(r.index > d) & (r.index < seg[i + 1])]
        names = [c for c in baskets[d] if c in sub.columns]
        ew = sub[names].mean(axis=1, skipna=True).fillna(0)
        et = sub[ETF].fillna(0) if ETF in sub.columns else 0
        s15.append(0.15 * ew + etf_w[d] * et); sc.append(ew)
    v15 = pd.concat(s15).std(); vsc = pd.concat(sc).std()
    return float(min(0.95, v15 / vsc)) if vsc > 0 else 0.15, float(v15 * math.sqrt(252)), float(vsc * math.sqrt(252))


def delist_overlay(res, panels, initial_cash, scenario):
    from quantlab.beta.survivorship import load_delisted_master
    m = load_delisted_master()
    nav = res["nav"].copy()
    aw = res.get("actual_weights")
    hits = []
    if aw is None or m is None:
        return nav, hits
    for c in aw.columns:
        if c not in m.index or c == ETF:
            continue
        ltd = m.loc[c, "last_trade_date"]
        if not (ltd == ltd) or ltd > nav.index[-1] or ltd < aw.index[0]:
            continue
        ltd = aw.index[aw.index <= ltd][-1]  # as-of match (ltd may be missing from the session grid)
        w = float(np.nan_to_num(aw.at[ltd, c]))
        if w <= 1e-6:
            continue
        held_val = w * float(nav.at[ltd])
        nav.loc[nav.index > ltd] -= scenario * held_val
        hits.append({"iid": c, "last_trade_date": str(ltd.date()), "weight": w, "held_cny": held_val})
    return nav, hits


def effective_n(res):
    """Engine's effective_n_mean is 1/sum(w^2) on NAV weights incl. cash -> inflated when mostly cash.
    Report it renormalized to invested gross, plus smallcap-sleeve-only (ex ETF), and avg gross exposure."""
    aw = res.get("actual_weights")
    if aw is None:
        return {"effective_n_mean_engine_raw": float(res["effective_n_mean"])}
    w = aw.fillna(0.0).astype(float).clip(lower=0)
    def en(x):
        g = x.sum(axis=1); xn = x.div(g.where(g > 0), axis=0)
        return float((1.0 / (xn ** 2).sum(axis=1)).replace([np.inf], np.nan).mean())
    sc = w.drop(columns=[ETF], errors="ignore")
    return {"effective_n_mean": en(w), "effective_n_sleeve_ex_etf": en(sc) if (sc.sum(axis=1) > 0).any() else None,
            "avg_gross_exposure": float(w.sum(axis=1).mean()), "effective_n_mean_engine_raw": float(res["effective_n_mean"])}


def selection_delist_diag(dates, baskets):
    from quantlab.beta.survivorship import load_delisted_master
    m = load_delisted_master(); out = []
    for c in sorted({x for v in baskets.values() for x in v} & set(m.index)):
        ins = [d for d in dates if c in baskets[d]]; ltd = m.loc[c, "last_trade_date"]
        out.append({"iid": c, "last_in_basket": str(ins[-1].date()), "last_trade_date": str(ltd.date()),
                    "gap_days": int((ltd - ins[-1]).days), "reason": str(m.loc[c, "delist_reason_category"])})
    return out


def metrics(nav, res, initial_cash):
    r = nav.pct_change().dropna()
    yrs = len(r) / 252
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1 / yrs) - 1 if yrs > 0 else float("nan")
    dd = nav / nav.cummax() - 1
    mdd = float(dd.min()); vol = float(r.std() * math.sqrt(252))
    sharpe = float(r.mean() / r.std() * math.sqrt(252)) if r.std() > 0 else float("nan")
    avg_nav = float(nav.mean())
    return {"cagr": float(cagr), "mdd": mdd, "sharpe_rf0": sharpe, "calmar": float(cagr / -mdd) if mdd < 0 else None,
            "ann_vol": vol, "turnover_one_way_per_year": float(res["filled_notional"] / 2 / avg_nav / yrs) if yrs > 0 else None,
            "total_cost_cny": float(res["total_cost"]), "cost_frac_of_capital": float(res["total_cost"] / initial_cash),
            "costs_breakdown": {k: float(v) for k, v in res["costs"].items()}, "fill_ratio": float(res["fill_ratio"]),
            **effective_n(res), "mdd_date": str(dd.idxmin().date()),
            "date_start": str(nav.index[0].date()), "date_end": str(nav.index[-1].date()), "n_days": int(len(nav))}


def main(argv=None):
    from quantlab.platform.execution import ExecConfig, load_execution_panels, run_weight_schedule
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2015-06-01")
    ap.add_argument("--end", default="2026-10-09")
    ap.add_argument("--every", type=int, default=20)
    ap.add_argument("--capital", type=float, default=5_000_000.0)
    ap.add_argument("--arms", default="A0,S10,S15,S20,C2,C3")
    ap.add_argument("--out", default="output/v2_proto/smallcap_engine_compare")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    out = ROOT / a.out; out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    import hashlib
    import quantlab.platform.execution as _ex
    eng_path = Path(_ex.__file__)
    def eng_id():
        st = eng_path.stat()
        return {"path": str(eng_path), "mtime_epoch": st.st_mtime,
                "mtime_et": pd.Timestamp(st.st_mtime, unit="s", tz="UTC").tz_convert("America/New_York").isoformat(),
                "sha256": hashlib.sha256(eng_path.read_bytes()).hexdigest()}
    eng_before = eng_id()
    dates = rebalance_dates(a.start, a.end, a.every)
    log("rebalances", len(dates), dates[0].date(), "→", dates[-1].date())
    baskets, bdiag = build_baskets(dates); log("baskets built", round(time.time() - t0, 1), "s")
    ew = etf_plan(dates); log("etf plan built; avg", round(np.mean(list(ew.values())), 3))
    ids = sorted({c for v in baskets.values() for c in v} | {ETF})
    log("unique ids", len(ids))
    t1 = time.time()
    lo = (pd.Timestamp(a.start) - pd.Timedelta(days=45)).date()
    panels, pdiag = load_execution_panels(ids, lo, a.end)
    # 510300 splice removed 2026-10-11 05:10 ET: engine panels carry real OHLCV through 2026-10-09
    # (checked: 88/88 sessions 2026-06..10 match data/v2 ETF close within 2.4e-7). splice_etf kept only as an unused helper.
    etf_last = panels.close[ETF].dropna().index[-1] if ETF in panels.close.columns else None
    if etf_last is None or etf_last < pd.Timestamp(a.end) - pd.Timedelta(days=7):
        raise SystemExit(f"510300 missing/short in engine panels (last={etf_last}); not splicing silently")
    log("panels", panels.close.shape, "missing", len(pdiag["missing_ids"]), round(time.time() - t1, 1), "s")
    c3_w, v15, vsc = raw_vol_calibrate(panels, dates, baskets, ew)
    arms, avg_etf = schedules(dates, baskets, ew, c3_w)
    cfg = ExecConfig.strategy_v1(impact_k=1.0, min_trade_value=2000.0)
    results = {}
    for name in a.arms.split(","):
        t2 = time.time()
        res = run_weight_schedule(panels, arms[name], initial_cash=a.capital, config=cfg, record_weights=True)
        nav = res["nav"].loc[pd.Timestamp(a.start):]
        row = {"engine_nav": metrics(nav, res, a.capital)}
        for tag, sc in (("delist_minus50", 0.5), ("delist_minus100", 1.0)):
            n2, hits = delist_overlay(res, panels, a.capital, sc)
            row[tag] = {**metrics(n2.loc[pd.Timestamp(a.start):], res, a.capital), "delist_hits": hits}
        results[name] = row
        pd.DataFrame({"nav": nav}).to_csv(out / f"nav_{name}.csv")
        m = row["delist_minus50"]
        log(name, f"CAGR {m['cagr']:.2%} MDD {m['mdd']:.2%} Sharpe {m['sharpe_rf0']:.2f} vol {m['ann_vol']:.2%}",
            f"cost {m['cost_frac_of_capital']:.2%} delist_hits {len(m['delist_hits'])}", round(time.time() - t2, 1), "s")
    eng_after = eng_id()
    eng_unchanged = eng_before["sha256"] == eng_after["sha256"] and eng_before["mtime_epoch"] == eng_after["mtime_epoch"]
    log("engine", eng_before["sha256"][:12], "unchanged_during_run", eng_unchanged)
    summary = {
        "engine_file": {"before": eng_before, "after": eng_after, "unchanged_during_run": eng_unchanged},
        "etf_source": "load_execution_panels (no splice)",
        "ok": True, "promotion_approved": False, "mandate_json_edited": False, "dry_run": a.dry_run,
        "engine": "quantlab.platform.execution.run_weight_schedule · ExecConfig.strategy_v1(impact_k=1.0, min_trade_value=2000)",
        "engine_conventions": ["next_open fills", "0.01 tick", "lot rounding on target", "10% participation cap",
                               "unfilled carry", "limit enforcement", "commission 2.5bp min 5", "stamp by date", "sqrt impact k=1.0"],
        "capital_cny": a.capital, "window": [a.start, a.end], "rebalance_every_sessions": a.every, "n_rebalances": len(dates),
        "arm_definitions": {
            "A0": "510300 at VolTarget plan etf_sleeve_weight; rest CASH (no Strategy residual stock book)",
            "S10/S15/S20": "A0 + smallcap EW ~50 at 10/15/20% of book; B1 ranking; ST/low-price/audit; retain_top 150; no brake",
            "C2": f"static 510300 at A0 avg weight {avg_etf:.3f} + static smallcap 15%; no timing",
            "C3": f"static smallcap-only at {c3_w:.3f} (raw-vol match to S15: {v15:.2%} vs smallcap {vsc:.2%}); ex-post calibrated reference",
        },
        "basket_sizes": {"min": min(len(v) for v in baskets.values()), "max": max(len(v) for v in baskets.values()),
                         "n_below_45": sum(len(v) < 45 for v in baskets.values()),
                         "by_session": {str(k.date()): len(v) for k, v in baskets.items()}},
        "delisted_ever_selected": selection_delist_diag(dates, baskets),
        "terminal_delist": "post-engine NAV overlay: subtract scenario × held value at last_trade_date from later NAV; −50% primary, −100% sensitivity",
        "selector": "quantlab/beta/smallcap_history_selector.py (ADV via turnover_rate×circ_mv proxy; history truncated before 2016)",
        "basket_diag": bdiag[:3] + bdiag[-3:], "panel_diag": {k: v for k, v in pdiag.items() if k != "missing_ids"},
        "missing_ids": pdiag["missing_ids"][:50], "n_unique_ids": len(ids), "elapsed_s": round(time.time() - t0, 1),
        "results": results,
    }
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str))
    log("wrote", out / "summary.json", "elapsed", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
