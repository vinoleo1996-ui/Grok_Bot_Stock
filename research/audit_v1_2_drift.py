"""Audit v1.2 drift: pre-lot w_opt exposures with solver definitions; data coverage. No returns."""
import sys, pickle, json, numpy as np, pandas as pd
sys.argv = ["x"]
import optimizer_core_x2_run as R, optimizer_lambda_calib_sealed as C, optimizer_core_v1_1 as V
days = sys.stdin.read().split()
rows = []
for ds in days:
    d = pd.Timestamp(ds); rec = pickle.load(open(R.OUT / f"_ckpt_v1_2/{d:%Y%m%d}.pkl", "rb"))
    D = C.prepare_day(d)
    pool = D["alpha"].index; lnm = D["ln_mcap"].astype(float); x = lnm.reindex(pool)
    zp = (x - x.mean()) / (x.std(ddof=0) + 1e-12); mp = (x - x.mean()) ** 2; mp = (mp - mp.mean()) / (mp.std(ddof=0) + 1e-12)
    wb = D["wb"].reindex(pool).fillna(0); b = D["betas"].reindex(pool)
    bb = float((wb * b.fillna(1.0)).sum() / wb.sum())
    base = {"date": ds, "pool_n": len(pool), "lnm_nan": int(x.isna().sum()), "beta_nan": int(b.isna().sum()),
            "beta_med": float(b.median()), "beta_b": bb, "wb_sum": float(wb.sum()), "wb_top": float(wb.max()),
            "zb": float((wb * zp.fillna(0)).sum()), "midb": float((wb * mp.fillna(0)).sum())}
    for a in R.AUMS:
        w = rec["w"][a]; lg = rec["log"].get(a, {})
        if w is None or lg.get("status") != "OK": rows.append({**base, "aum": a, "status": lg.get("status")}); continue
        w = w.reindex(pool).fillna(0)
        nanin = int(x.reindex(w[w > 0].index).isna().sum()) + int(b.reindex(w[w > 0].index).isna().sum())
        sl = (lg.get("slack") or {}).get("size_slack", 0)
        rows.append({**base, "aum": a, "status": "OK", "size_slack": sl,
            "pre_size": float((w * zp.fillna(0)).sum()) - base["zb"], "pre_mid": float((w * mp.fillna(0)).sum()) - base["midb"],
            "pre_beta": float((w * b.fillna(1.0)).sum()) - bb, "nan_in_held": nanin, "sum_w": float(w.sum())})
    print(json.dumps(rows[-1]), flush=True)
pd.DataFrame(rows).to_csv(R.OUT.parent / "audit_v1_2" / f"pre_lot_exposures_{days[0]}_{days[-1]}.csv", index=False)
