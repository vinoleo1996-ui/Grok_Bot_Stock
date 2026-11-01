"""Disclosure-only: style drift of carried holdings on INFEASIBLE/LOT_HARD_FAIL days (v1.2). No solver/param change, no returns."""
import sys, pickle, pandas as pd
sys.argv = ["x"]
import optimizer_core_x2_run as R, optimizer_lambda_calib_sealed as C
R.BETA_POOL = True
ck = R.OUT / "_ckpt_v1_2"; days = sorted(ck.glob("*.pkl")); held = {}; rows = []
for p in days:
    rec = pickle.load(open(p, "rb")); d = pd.Timestamp(rec["day"]); D = None
    for a in R.AUMS:
        lg = rec["log"].get(a, {})
        if a in rec.get("sleeves", {}):
            for sv, x in rec["sleeves"][a].items(): held[(a, sv)] = x["w"]
            continue
        if lg.get("status") == "NO_DATA_CARRY": continue
        D = D or C.prepare_day(d)
        for sv in C.REPORT_SLEEVES:
            w = held.get((a, sv))
            if w is None: continue
            x = R.exposure_drift(w, D)
            rows.append({"date": f"{d:%Y-%m-%d}", "aum": a, "sleeve": sv, "carry_drift_source": "prior_holdings_on_day_data", **x})
out = pd.DataFrame(rows); print(out.round(3).to_string())
dpath = R.OUT / "core_v1_2_disclosure.csv"; Dd = pd.read_csv(dpath)
for c in ["size_drift", "midcap_drift", "beta_drift", "ind_active_max", "ind_abs_max"]:
    m = Dd.merge(out[["date", "aum", "sleeve", c]], on=["date", "aum", "sleeve"], how="left", suffixes=("", "_carry"))
    Dd[c] = Dd[c].where(Dd[c].notna(), m[c + "_carry"])
Dd["carry_drift_disclosed"] = Dd.set_index(["date", "aum", "sleeve"]).index.isin(out.set_index(["date", "aum", "sleeve"]).index)
sb = 0.35 + Dd["size_slack"].fillna(0)
Dd.loc[Dd.carry_drift_disclosed, "LOT_STYLE_DRIFT"] = ((Dd.size_drift.abs() > sb) | (Dd.midcap_drift.abs() > sb) | (Dd.beta_drift.abs() > 0.10))[Dd.carry_drift_disclosed]
Dd.to_csv(dpath, index=False); out.to_csv(R.OUT.parent / "audit_v1_2" / "carry_day_drift.csv", index=False)
