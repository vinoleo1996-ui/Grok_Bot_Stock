#!/usr/bin/env python3
"""FROZEN_v1.3 pre-performance disclosure stats (weights/disclosure only; NO returns, NO book-smoke, NO scorecard).
Reads core_v1_3_disclosure.csv, core_v1_3_lot_exclusions.csv, core_*.parquet; writes core_v1_3_stats.json and
core_v1_3_lot_exclusion_counts.csv (per date x AUM, zeros included)."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]; OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "output/strategy_optimizer/core_x2"
SIZE_BOX, BETA_BOX, IND_ACTIVE, IND_ABS = 0.35, 0.10, 0.08, 0.20
D = pd.read_csv(OUT / "core_v1_3_disclosure.csv"); D["month"] = D.date.str[:7]
E = pd.read_csv(OUT / "core_v1_3_lot_exclusions.csv")
FAIL = ("INFEASIBLE", "LOT_HARD_FAIL")
D["fail"] = D.status.isin(FAIL); D["feasible"] = D.status.isin(("OK", "LOT_CASH_GT2"))
ss = D.size_slack.fillna(0); isl = D.ind_slack.fillna(0)
D["size_exc"] = (D.size_drift.abs() - (SIZE_BOX + ss)).clip(lower=0)
D["midcap_exc"] = (D.midcap_drift.abs() - (SIZE_BOX + ss)).clip(lower=0)
D["beta_exc"] = (D.beta_drift.abs() - BETA_BOX).clip(lower=0)
D["ind_exc"] = np.maximum((D.ind_active_max - (IND_ACTIVE + isl)).clip(lower=0), (D.ind_abs_max - IND_ABS).clip(lower=0))
rd = sorted(D.date.unique())
# exclusion counts per date x AUM (zeros included); NO_DATA day has no candidate set
cnt = E.groupby(["date", "aum"]).size().rename("n_excluded")
rows = []
for d in rd:
    for a in (600000, 1000000):
        nd = (D[(D.date == d) & (D.aum == a)].status == "NO_DATA_CARRY").all()
        rows.append({"date": d, "window": D[D.date == d].window.iloc[0], "aum": a, "n_excluded": (np.nan if nd else int(cnt.get((d, a), 0))),
                     "cap_amount": {600000: 36000.0, 1000000: 50000.0}[a]})
EC = pd.DataFrame(rows); EC.to_csv(OUT / "core_v1_3_lot_exclusion_counts.csv", index=False)

def drift_block(x):
    o = {"n_days": int(len(x))}
    for k in ("size", "midcap", "beta", "ind"):
        e = x[f"{k}_exc"].dropna()
        o[k] = {"n_with_drift_values": int(len(e)), "days_exc_gt0": int((e > 1e-6).sum()), "days_exc_gt0.05": int((e > 0.05).sum()),
                "max_exc": round(float(e.max()), 4) if len(e) else None}
        if k != "ind":
            v = x[f"{k}_drift"].dropna(); o[k]["max_abs_drift"] = round(float(v.abs().max()), 4) if len(v) else None
            o[k]["min_drift"] = round(float(v.min()), 4) if len(v) else None; o[k]["max_drift"] = round(float(v.max()), 4) if len(v) else None
        else:
            o[k]["max_ind_active"] = round(float(x.ind_active_max.max()), 4) if x.ind_active_max.notna().any() else None
            o[k]["max_ind_abs"] = round(float(x.ind_abs_max.max()), 4) if x.ind_abs_max.notna().any() else None
    return o

def turnover_postlot(aum, sleeve):
    tag = {600000: "60w", 1000000: "100w"}[aum]
    p = pd.read_parquet(OUT / f"core_{sleeve}_{tag}.parquet", columns=["session", "instrument", "weight", "is_rebalance_day", "window"])
    p = p[p.is_rebalance_day]; W = p.pivot_table(index="session", columns="instrument", values="weight", aggfunc="sum").fillna(0.0).sort_index()
    ow = 0.5 * W.diff().abs().sum(axis=1).iloc[1:]   # target-to-target one-way (no price drift; NOT a return calc)
    We = W.drop(columns=["510300.SH"], errors="ignore"); We = We.div(We.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    owe = 0.5 * We.diff().abs().sum(axis=1).iloc[1:]  # equity book renormalized to 1 (same unit as solver one_way_opt / v1.2 0.38-0.40)
    win = p.drop_duplicates("session").set_index("session").window.reindex(ow.index)
    return ow, win, owe

stats = {"version": "FROZEN_v1.3", "returns_computed": False, "live": False, "n_rebal_days": len(rd), "by_aum_sleeve": {}}
for (a, sv), g in D.groupby(["aum", "sleeve"]):
    key = f"{a}_{sv}"; S = {}
    ow, owin, owe = turnover_postlot(a, sv)
    for wname, x in (("ALL", g), ("SEALED", g[g.window == "SEALED"]), ("X2", g[g.window == "X2"])):
        den = x[x.status != "NO_DATA_CARRY"]
        solved = x[x.status.isin(("OK", "LOT_CASH_GT2", "LOT_HARD_FAIL"))]  # step-2 solve produced w_opt
        feas = x[x.feasible]; carry = x[x.fail]
        o = {"n_days": int(len(x)), "n_eval": int(len(den)), "status_counts": {k: int(v) for k, v in x.status.value_counts().items()},
             "n_feasible": int(len(feas)), "feasibility_pct": round(100 * len(feas) / max(len(den), 1), 1),
             "n_strict_ok": int((x.status == "OK").sum()), "strict_feasibility_pct": round(100 * (x.status == "OK").sum() / max(len(den), 1), 1),
             "infeasible_list": [f"{r.date}:{r.status}{'('+str(r.lot_fail_reason)+')' if isinstance(r.lot_fail_reason, str) else ''}" for r in carry.itertuples()],
             "slack_used_days": int(solved.slack_used.sum()), "slack_used_pct": round(100 * solved.slack_used.mean(), 1) if len(solved) else None,
             "slack_at_cap_days": int(solved.slack_at_cap.sum()), "slack_at_cap_pct": round(100 * solved.slack_at_cap.mean(), 1) if len(solved) else None,
             "slack_at_cap_gt50pct": bool(len(solved) and solved.slack_at_cap.mean() > 0.5),
             "postlot_drift_feasible_days": drift_block(feas), "LOT_STYLE_DRIFT_feasible_days": int(feas.LOT_STYLE_DRIFT.sum()),
             "carry_day_drift": drift_block(carry), "carry_days_with_drift": int(carry.size_drift.notna().sum()),
             "cash_feasible": {"median": round(float(feas.cash.median()), 4) if len(feas) else None, "max": round(float(feas.cash.max()), 4) if len(feas) else None,
                               "days_gt_2pct": int((feas.cash > 0.02 + 1e-9).sum()), "p90": round(float(feas.cash.quantile(.9)), 4) if len(feas) else None},
             "names_feasible": {"min": int(feas.n_names.min()) if len(feas) else None, "median": float(feas.n_names.median()) if len(feas) else None, "max": int(feas.n_names.max()) if len(feas) else None},
             "K_solver": {"min": float(solved.K.min()) if len(solved) else None, "median": float(solved.K.median()) if len(solved) else None, "max": float(solved.K.max()) if len(solved) else None,
                          "tries_median": float(solved.tries.median()) if len(solved) else None, "tries_max": float(solved.tries.max()) if len(solved) else None},
             "one_way_solver_median": round(float(x.one_way_opt.dropna().median()), 3) if x.one_way_opt.notna().any() else None}
        sel = ow if wname == "ALL" else ow[owin == wname]
        o["one_way_postlot_target_median"] = round(float(sel.median()), 3) if len(sel) else None
        o["one_way_postlot_target_mean"] = round(float(sel.mean()), 3) if len(sel) else None
        fd = set(feas.date); sele = (owe if wname == "ALL" else owe[owin == wname]); sele = sele[sele.index.isin(fd)]
        o["one_way_postlot_equity_norm_traded_days_median"] = round(float(sele.median()), 3) if len(sele) else None
        ec = EC[(EC.aum == a) & ((EC.window == wname) if wname != "ALL" else True)].n_excluded.dropna()
        o["exclusions_per_day"] = {"min": int(ec.min()), "median": float(ec.median()), "mean": round(float(ec.mean()), 1), "max": int(ec.max()),
                                   "days_with_any": int((ec > 0).sum()), "total_rows": int(ec.sum()),
                                   "distinct_names": int(E[(E.aum == a) & (E.date.isin(EC[(EC.aum == a) & ((EC.window == wname) if wname != "ALL" else True)].date))].instrument.nunique())}
        S[wname] = o
    m = g.groupby("month").fail.sum(); S["stop_rule_months_ge2"] = {k: int(v) for k, v in m[m >= 2].items()}
    S["stop_rule_triggered"] = bool((m >= 2).any())
    stats["by_aum_sleeve"][key] = S
ev = D[D.status != "NO_DATA_CARRY"]; fe = D[D.feasible]
stats["rows"] = {"n_rows_eval": int(len(ev)), "n_LOT_CASH_GT2": int((D.status == "LOT_CASH_GT2").sum()),
                 "pct_rows_cash_gt2_of_eval": round(100 * (D.status == "LOT_CASH_GT2").sum() / len(ev), 1),
                 "pct_rows_cash_gt2_of_feasible": round(100 * (fe.cash > 0.02 + 1e-9).sum() / len(fe), 1),
                 "max_cash_feasible": round(float(fe.cash.max()), 4), "max_cash_row": fe.loc[fe.cash.idxmax(), ["date", "aum", "sleeve", "status"]].to_dict(),
                 "total_exclusion_rows": int(len(E)), "exclusion_rows_by_aum": {str(k): int(v) for k, v in E.groupby("aum").size().items()}}
(OUT / "core_v1_3_stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=1, default=str))
print(json.dumps(stats, ensure_ascii=False, indent=1, default=str))
