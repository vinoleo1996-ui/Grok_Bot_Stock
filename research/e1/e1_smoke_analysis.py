"""E1 smoke deep-dive (research-only): divergence classification, weights compare, paper gap."""
import json, sys, numpy as np, pandas as pd
from pathlib import Path
from quantlab.platform.e1_reconcile import load_schedule, ids_from_schedule, normalize_instrument_id, ZERO_COST
from quantlab.platform.execution import (load_execution_panels, run_weight_schedule, ExecConfig,
    corporate_action_arrays, _ledger_actions, tick_for_code)
WD = "output/strategy_paper_costs/e1_smoke_armA"; OUT = Path("output/e1_reconcile_e1_smoke")
sched, meta = load_schedule(weights_dir=WD)
ids = ids_from_schedule(sched)
res = {}
for ca in (False, True):
    tag = "ca_on" if ca else "ca_off"
    panels, diag = load_execution_panels(ids, "2024-06-01", "2026-10-09", corporate_actions=ca)
    p = panels.aligned()
    cfg = ExecConfig(fill="next_open", enforce_limits=False, participation_cap=None, price_tick="auto",
                     order_rounding="target", corporate_actions=ca, **ZERO_COST)
    r = run_weight_schedule(panels, sched, initial_cash=600_000.0, config=cfg)
    hold = r["actual_weights"].abs() > 1e-12
    navs = pd.read_csv(OUT / tag / "e1_navs.csv", index_col=0, parse_dates=True)
    C = p.close
    halted = C.isna()
    if ca:
        CD, SR, FR = corporate_action_arrays(p)
        CD0, SR0, _ = corporate_action_arrays(p, fallback=False)
        ev = pd.DataFrame((CD != 0) | (SR != 0), index=C.index, columns=C.columns)
        fb = pd.DataFrame(np.abs(FR - 1) > 1e-9, index=C.index, columns=C.columns) & ~ev
        frac = pd.DataFrame(SR != 0, index=C.index, columns=C.columns)
    sig_days = set(pd.Timestamp(k).normalize() for k in sched)
    fill_days = set(C.index[min(C.index.get_loc(d) + 1, len(C) - 1)] for d in sig_days if d in C.index)
    out = {}
    for eng in [c for c in navs.columns if c != "platform"]:
        d = (navs[eng] - navs["platform"])
        step = d.diff().fillna(d)
        top = step.abs().sort_values(ascending=False).head(10)
        rows = []
        for day, v in top.items():
            if v < 1e-6: break
            prev = C.index[max(C.index.get_loc(day) - 1, 0)]
            held = hold.loc[prev] if prev in hold.index else hold.loc[day]
            names = list(held[held].index)
            cls = []
            if ca:
                e = [n for n in names if ev.at[day, n]]
                f = [n for n in names if fb.at[day, n]]
                if e: cls.append(f"corporate_action(event:{','.join(e[:4])})")
                if f: cls.append(f"corporate_action(factor_fallback_only:{','.join(f[:4])})")
            h = [n for n in names if halted.at[day, n]]
            if h: cls.append(f"halt/missing_price:{','.join(h[:4])}")
            if day in fill_days: cls.append("rebalance_fill_day(lot_rounding/fill_timing)")
            if eng == "paper":
                cls.append("paper_convention(close_fill,no_drift,costs)")
            if "sh.510300" in names and not cls: cls.append("ETF/market_move")
            rows.append(dict(day=str(day.date()), step_cny=round(float(step[day]), 2),
                             cum_cny=round(float(d[day]), 2), cls=cls or ["unexplained"]))
        out[eng] = rows
    res[tag] = dict(top10=out, final={c: float(navs[c].iloc[-1]) for c in navs.columns},
                    cagr={c: float((navs[c].iloc[-1] / navs[c].iloc[0]) ** (252 / (len(navs) - 1)) - 1) for c in navs.columns},
                    n_days=len(navs))
    if ca:
        # ledger vs platform: every event on a held name (separate section, not failure)
        acts = _ledger_actions(p)
        lst = []
        dif = navs["ledger"] - navs["platform"]; st = dif.diff().fillna(0)
        for day in C.index[1:]:
            prev = C.index[C.index.get_loc(day) - 1]
            held = [n for n in hold.columns if hold.at[prev, n]]
            for n in held:
                if ev.at[day, n] or fb.at[day, n]:
                    lst.append(dict(day=str(day.date()), code=n, kind="event" if ev.at[day, n] else "factor_fallback_only",
                                    cash=float(CD[C.index.get_loc(day), C.columns.get_loc(n)]),
                                    ratio=float(SR[C.index.get_loc(day), C.columns.get_loc(n)]),
                                    ledger_minus_platform_step=round(float(st[day]), 2)))
        res["ca_events_held"] = lst
        res["ledger_actions_rows"] = int(len(acts))
    # weights compare (post-fill) — CA off (paper basis)
    if not ca:
        tw = pd.read_parquet(Path(WD) / "target_weights.parquet")
        tw["session"] = pd.to_datetime(tw["session"]).dt.normalize()
        tw["iid"] = tw["instrument_id"].map(normalize_instrument_id)
        aw = r["actual_weights"]
        rows = []
        for s, g in tw.groupby("session"):
            if s not in C.index: continue
            i = C.index.get_loc(s); fd = C.index[min(i + 1, len(C) - 1)]
            sw = g.set_index("iid")["weight"].astype(float)
            ew = aw.loc[fd]; ew = ew[ew.abs() > 1e-12]
            u = sw.index.union(ew.index)
            a, b = sw.reindex(u).fillna(0), ew.reindex(u).fillna(0)
            rows.append(dict(session=str(s.date()), engine_fill_day=str(fd.date()), n_strategy=int((sw > 0).sum()),
                             n_engine=int(len(ew)), l1_diff=float((a - b).abs().sum()),
                             max_abs=float((a - b).abs().max()),
                             etf_strategy=float(sw.get("sh.510300", 0)), etf_engine=float(ew.get("sh.510300", 0)),
                             sum_strategy=float(sw.sum()), sum_engine=float(ew.sum())))
        wc = pd.DataFrame(rows); wc.to_csv(OUT / "e1_weights_compare.csv", index=False)
        res["weights_compare"] = dict(n=len(wc), l1_mean=float(wc.l1_diff.mean()), l1_max=float(wc.l1_diff.max()),
                                      l1_max_session=wc.loc[wc.l1_diff.idxmax(), "session"],
                                      maxabs_max=float(wc.max_abs.max()),
                                      sum_strategy_mean=float(wc.sum_strategy.mean()), sum_engine_mean=float(wc.sum_engine.mean()),
                                      name_mismatch_sessions=int((wc.n_strategy != wc.n_engine).sum()))
        # planned vs post-fill in strategy
        pl = pd.read_parquet(Path(WD) / "planned_target_weights.parquet")
        res["strategy_planned_vs_postfill"] = dict(planned_rows=len(pl), postfill_rows=len(tw))
json.dump(res, open(OUT / "e1_analysis.json", "w"), ensure_ascii=False, indent=1, default=str)
print(json.dumps({k: (v if k != "ca_events_held" else len(v)) for k, v in res.items()}, ensure_ascii=False, indent=1, default=str))
