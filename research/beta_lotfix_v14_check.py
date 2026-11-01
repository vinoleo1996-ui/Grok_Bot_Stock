#!/usr/bin/env python3
"""Beta LOTFIX v1.4 cosign check: arithmetic on v1.3 (poolind) ckpts + cached exposures. No solver, no returns."""
import sys, pickle, json
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "research"))
import optimizer_lambda_calib_sealed as C
CK = ROOT / "output/strategy_optimizer/core_x2/_ckpt_v1_3_poolind"; CA = ROOT / "output/beta/s2_3_band_check/_cache"
OUT = ROOT / "output/beta/lotfix_v14_check"; OUT.mkdir(parents=True, exist_ok=True)
BAL = C.BALLAST; X2S = pd.Timestamp("2024-06-03")
days = [d for d in sorted(pd.Timestamp(p.stem) for p in CK.glob("*.pkl")) if d >= X2S]
recs = {d: pickle.load(open(CK / f"{d:%Y%m%d}.pkl", "rb")) for d in days}
caches = {d: pickle.load(open(CA / f"{d:%Y%m%d}.pkl", "rb")) for d in days}
allnames = sorted({i for d in days if caches[d] is not None for i in caches[d]["alpha"].index})
bs = C.load_daily_basic_window(allnames, days[0] - pd.Timedelta(days=12), days[-1]); bs["trade_date"] = pd.to_datetime(bs["trade_date"])
def px_on(d):
    b = bs[(bs.trade_date <= d) & (bs.trade_date >= d - pd.Timedelta(days=10))]
    return b.sort_values("trade_date").groupby("ts_code")["close"].last()
def stdz(D):
    x = D["ln_mcap"].astype(float).reindex(D["alpha"].index); z = (x - x.mean()) / (x.std(ddof=0) + 1e-12)
    m = (x - x.mean()) ** 2; m = (m - m.mean()) / (m.std(ddof=0) + 1e-12); return z, m
rows_cap, rows_pool, rows_C = [], [], []
for d in days:
    D = caches[d]; r = recs[d]
    if D is None: continue
    P = px_on(d); z, m = stdz(D); b = D["betas"].reindex(D["alpha"].index).fillna(1.0); wb = D["wb"].reindex(D["alpha"].index).fillna(0); wb = wb / wb.sum()
    pool = D["alpha"].index
    for a, c in ((600_000, 0.06), (1_000_000, 0.05)):
        L = pd.Series([C.lot_round_rule(i) for i in pool], index=pool); p = P.reindex(pool); u = L * p / a
        m1 = np.floor(c * 1.0 * a / (L * p) + 1e-6); m2 = np.floor(c * 0.8 * a / (L * p) + 1e-6)
        caplot = np.minimum(m1 * u / 1.0, m2 * u / 0.8)
        ok = p.notna(); h = (c - caplot) / c
        # pool-level: prescreen sets and haircut tilt
        ex1 = ok & (m1 == 0); ex2only = ok & (m1 > 0) & (m2 == 0); cand = ok & (m2 > 0)
        hc = h[cand]
        rows_pool.append({"date": d.date(), "aum": a, "n_pool": int(ok.sum()), "n_ex_sleeve1": int(ex1.sum()), "n_ex_sleeve2_only": int(ex2only.sum()),
                          "haircut_med": float(hc.median()), "haircut_p90": float(hc.quantile(.9)), "haircut_max": float(hc.max()),
                          "corr_h_lnprice": float(np.corrcoef(hc, np.log(p[cand]))[0, 1]), "corr_h_size": float(np.corrcoef(hc, z[cand].fillna(0))[0, 1]),
                          "corr_h_beta": float(np.corrcoef(hc, b[cand])[0, 1]),
                          "ex_size_mean": float(z[ex1 | ex2only].mean()) if (ex1 | ex2only).any() else np.nan,
                          "ex_beta_mean": float(b[ex1 | ex2only].mean()) if (ex1 | ex2only).any() else np.nan,
                          "ex_wb_share": float(wb[ex1 | ex2only].sum()), "pool_beta_bb": float((wb * b).sum())})
        # solver support (only when solved this day)
        lg = r["log"].get(a, {})
        if a in r.get("sleeves", {}) or lg.get("status") in ("OK", "LOT_CASH_GT2", "INFEASIBLE"):
            w = r["w"][a] if lg.get("status") != "INFEASIBLE" or lg.get("stage") == "lot" else None
            if w is not None and lg.get("carry") is None or (lg.get("stage") == "lot"):
                w = r["w"][a]; K = len(w)
                sup = w.index.intersection(pool); cl = caplot.reindex(sup)
                top = caplot.reindex(sup).sort_values(ascending=False)
                rows_cap.append({"date": d.date(), "aum": a, "K": K, "n_at_cap": int((w >= c - 1e-6).sum()), "sum_caplot_support": float(cl.sum()),
                                 "K20_corner": bool(K == 20 and abs(c * 20 - 1) < 1e-9), "min_K_feasible_caps": int(np.searchsorted(np.cumsum(caplot[cand].sort_values(ascending=False).values), 1.0) + 1),
                                 "haircut_support_med": float(((c - cl) / c).median()), "haircut_atcap_mean": float(((c - cl) / c)[w.reindex(sup) >= c - 1e-6].mean()) if (w >= c - 1e-6).any() else np.nan})
        # basis C recheck of v1.3 sleeve ② (and ①) on non-carry days
        if a in r.get("sleeves", {}):
            sl = lg["slack"]
            for sv, B in (("equity_100", 1.0), ("equity80_etf20_510300", 0.8)):
                wl = r["sleeves"][a][sv]["w"].drop(BAL, errors="ignore"); we = wl.reindex(pool).fillna(0)
                ind = pd.Series(D["industry"]); G = we.groupby(ind.reindex(pool).values).sum() / B; Wb = wb.groupby(ind.reindex(pool).values).sum()
                u_ = G.index.union(Wb.index); act = G.reindex(u_).fillna(0) - Wb.reindex(u_).fillna(0)
                E = {"size": float((we * z.fillna(0)).sum() / B - (wb * z.fillna(0)).sum()), "mid": float((we * m.fillna(0)).sum() / B - (wb * m.fillna(0)).sum()),
                     "beta": float((we * b).sum() / B - (wb * b).sum())}
                sb = 0.35 + sl["size_slack"]; ib = 0.08 + sl["ind_slack"]; cash = 1 - float(r["sleeves"][a][sv]["w"].sum())
                failC = {"size": abs(E["size"]) > sb + 1e-6, "mid": abs(E["mid"]) > sb + 1e-6, "beta": abs(E["beta"]) > 0.10 + 1e-6,
                         "ind": float(act.abs().max()) > ib + 1e-6 or float(G.max()) > 0.20 + 1e-6}
                rows_C.append({"date": d.date(), "aum": a, "sleeve": sv, "flagA": r["sleeves"][a][sv]["lot_flag"], "cash": cash,
                               **{f"E_{k}": v for k, v in E.items()}, **{f"failC_{k}": v for k, v in failC.items()}, "failC_any": any(failC.values())})
pd.DataFrame(rows_pool).to_csv(OUT / "pool_prescreen_haircut.csv", index=False)
pd.DataFrame(rows_cap).to_csv(OUT / "support_caplot.csv", index=False)
pd.DataFrame(rows_C).to_csv(OUT / "basisC_recheck_v1_3.csv", index=False)
print("DONE")
