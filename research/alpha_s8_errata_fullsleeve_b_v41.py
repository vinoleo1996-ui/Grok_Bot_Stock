"""Alpha 2026-10-18 v4.1: recompute AI-style-set full-sleeve B with PRIOR-DAY logmv (A1) and prior-day logmv+pool (A3),
fixing the same-day logmv bug inherited from ai_hiliq_sec8_supplement.neutral_eps (AI diag 01:03). Frozen (Alpha) style set
already uses t-1 exposures (alpha_hiliq_s8_paradigm.resid_ret -> xmat(c, d0)); recomputed here for reference. Read-only; live=false."""
import sys, json, gc, numpy as np, pandas as pd
from pathlib import Path
R = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(R))
import research.alpha_hiliq_s8_paradigm as S8
from research.alpha_combo_marginal import nw_se
PC = R/"output/ai_factory/panel_cache"; OUT = R/"output/alpha/recon_eqinc"
P = pd.concat([pd.read_parquet(PC/f"cs_panel_{y}.parquet", columns=["date","instrument","hiliq","ret","logmv","ind"]) for y in (2023, 2024, 2025, 2026)])
P["date"] = pd.to_datetime(P.date); P = P.sort_values(["instrument","date"])
g = P.groupby("instrument", sort=False)
P["logmv_l1"] = g.logmv.shift(1); P["hiliq_l1"] = g.hiliq.shift(1).fillna(False).astype(bool); P["ind_l1"] = g.ind.shift(1)
RW = P.pivot_table(index="date", columns="instrument", values="ret").astype("float32").sort_index()
mom = RW.shift(1).rolling(20, min_periods=15).sum().stack().rename("mom20"); vol = RW.shift(1).rolling(20, min_periods=15).std().stack().rename("vol20"); del RW; gc.collect()
P = P[P.date >= "2024-01-01"].join(mom.astype("float32"), on=["date","instrument"]).join(vol.astype("float32"), on=["date","instrument"]); del mom, vol; gc.collect()
def eps(poolcol, mvcol, indcol):
    rows = []
    for d, x in P[P[poolcol]].groupby("date", sort=True):
        x = x.dropna(subset=["ret", mvcol, "mom20", "vol20", indcol]); x = x[x[indcol] >= 0]
        if len(x) < 100: continue
        X = np.column_stack([pd.get_dummies(x[indcol]).to_numpy(float), x[[mvcol,"mom20","vol20"]].to_numpy(float)]); X[:, -3:] = (X[:, -3:]-X[:, -3:].mean(0))/X[:, -3:].std(0)
        y = x.ret.to_numpy(float).clip(-.21, .31); b, *_ = np.linalg.lstsq(X, y, rcond=None)
        rows.append(pd.DataFrame({"date": d, "instrument": x.instrument.values, "eps": (y-X@b).astype("float32")}))
    return pd.concat(rows).pivot(index="date", columns="instrument", values="eps")
EA1 = eps("hiliq", "logmv_l1", "ind"); EA3 = eps("hiliq_l1", "logmv_l1", "ind_l1"); EA0 = eps("hiliq", "logmv", "ind"); del P; gc.collect()
c = S8.build(); E = S8.resid_ret(c)
def al(X): return X.reindex(index=c["ev"], columns=c["U"])
EA1, EA3, EA0 = al(EA1), al(EA3), al(EA0)
def nstat(E, W):
    Wl = W.shift(2).fillna(0.0); gg = (Wl*E.reindex_like(Wl).fillna(0.0)).sum(axis=1)
    to = W.diff().abs().sum(axis=1).fillna(W.abs().sum(axis=1)).shift(1).fillna(0.0); n = (gg-S8.COST*to).iloc[3:]; se = nw_se(n.values, 5)
    return dict(ann_net=float(n.mean()*244), t_hac5=float(n.mean()/se) if se > 0 else None)
res = {"check_frozen_style_uses_t-1_exposures": "yes: resid_ret regresses R[d] on xmat(c, d0=d-1) incl. log float mcap at d0 and pool INU at d0"}
for k, st in {"capacity_adv": None, **S8.LEGS}.items():
    p = S8.CAP if st is None else S8.LEGD/f"g1g5_{k}_hiliq_v1_daily_weights_20261014_{st}.parquet"
    S = S8.sig(c, p); W = S.div(S.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    res[k] = dict(frozen_style=nstat(E, W), ai_style_A0_sameday_bug=nstat(EA0, W), ai_style_A1_prior_logmv=nstat(EA1, W), ai_style_A3_prior_logmv_pool=nstat(EA3, W))
    print(k, res[k], flush=True)
(OUT/"step_e_fullsleeve_b_v41.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
