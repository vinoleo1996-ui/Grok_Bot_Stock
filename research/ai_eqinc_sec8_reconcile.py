"""Reconcile equity_incentive §8 sign conflict (AI 10-14 supplement vs Alpha §8 v3). Read-only: imports Alpha's
research/alpha_hiliq_s8_paradigm.py functions (not edited); reimplements AI neutral_eps (ai_hiliq_sec8_supplement.py runs main() on import).
Factorial: residual-return style set {Alpha: SWL1+logfloatmc+β120+mom(120→20)+logADV20 ; AI: SWL1+logmv+mom20+vol20}
× weighting {Alpha topN normalized to 100% stock, tie=column order ; AI book weights incl. 20% ETF, stock_share≈0.8}
× IC def {Alpha rank IC of style-residualized weight vs raw fwd20 ; AI Pearson of binary membership resid on ind+logmv+cap vs fwd ε t+2..t+21}.
live=false; no Book-Smoke."""
import sys, json, resource, gc, numpy as np, pandas as pd
from pathlib import Path
R = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(R))
import research.alpha_hiliq_s8_paradigm as S8
from research.alpha_combo_marginal import ic_tstats
rss = lambda: resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
LEG = S8.LEGD/"g1g5_equity_incentive_hiliq_v1_daily_weights_20261014_202436.parquet"; PC = R/"output/ai_factory/panel_cache"
import ctypes; trim = lambda: (gc.collect(), ctypes.CDLL("libc.so.6").malloc_trim(0))
TMP = R/"output/ai_factory/hiliq_sec8/_reconcile_tmp"; TMP.mkdir(exist_ok=True)
STAGE = sys.argv[1] if len(sys.argv) > 1 else "all"
if STAGE == "alpha":  # dump Alpha's exact build() context, then residualize in numpy (same math as S8.xmat/resid_multi/resid_ret)
    c = S8.build(); print("ctx", f"rss={rss():.0f}", flush=True)
    ev, U = c["ev"], c["U"]; S = S8.sig(c, LEG); S.to_parquet(TMP/"S.parquet"); c["F"].to_parquet(TMP/"F.parquet")
    INU = c["INU"].reindex(index=ev, columns=U).to_numpy(bool); Xs = np.stack([c["X"][k].reindex(index=ev, columns=U).to_numpy("float64") for k in ("mc","beta","mom","liq")], -1)
    INDc = c["IND"].reindex(index=ev, columns=U).fillna("_UNK").astype(str); cats = sorted(set(INDc.values.ravel())); IND = INDc.replace({k: i for i, k in enumerate(cats)}).to_numpy(int)
    Rr = c["R"].reindex(columns=U); Rr = Rr.reindex(Rr.index.union(ev)).sort_index(); Rv = Rr.reindex(ev).to_numpy("float64"); Sv = S.to_numpy("float64")
    del c; trim(); print("dumped", f"rss={rss():.0f}", flush=True)
    T, N = len(ev), len(U); ZA = np.full((T, N), np.nan); EA = np.full((T, N), np.nan)
    def xm(k):
        pool = np.where(INU[k])[0]; Xd = Xs[k, pool]; ok = np.isfinite(Xd).all(1); pool = pool[ok]
        D = (IND[k, pool][:, None] == np.unique(IND[k, pool])[None, :]).astype(float)
        return pool, np.c_[np.ones(len(pool)), Xs[k, pool], D]
    prev = None
    for k in range(T):
        pool, Xm = xm(k)
        if len(pool) >= 50:
            y = Sv[k, pool]; cf, *_ = np.linalg.lstsq(Xm, y, rcond=None); e = y-Xm@cf
            if y.std() > 0 and e.std() > 0: ZA[k, pool] = (e-e.mean())/e.std()
        if prev is not None and len(prev[0]) >= 1:
            p0, X0 = prev; y = Rv[k, p0]; ok = ~np.isnan(y)
            if ok.sum() >= 50: cf, *_ = np.linalg.lstsq(X0[ok], y[ok], rcond=None); EA[k, p0[ok]] = y[ok]-X0[ok]@cf
        prev = (pool, Xm)
    pd.DataFrame(ZA, index=ev, columns=U).to_parquet(TMP/"ZA.parquet"); pd.DataFrame(EA, index=ev, columns=U).to_parquet(TMP/"EA.parquet")
    print("ZA/EA", f"rss={rss():.0f}", flush=True); sys.exit(0)
if STAGE == "ai":
    EA = pd.read_parquet(TMP/"EA.parquet")
out = {}
if STAGE == "combo":
    EA = pd.read_parquet(TMP/"EA.parquet"); EI = pd.read_parquet(TMP/"EI.parquet"); S = pd.read_parquet(TMP/"S.parquet"); ZA = pd.read_parquet(TMP/"ZA.parquet"); Fr = pd.read_parquet(TMP/"F.parquet")
    c = dict(ev=EA.index, F=Fr)
    nz = S[S > 0]; out["leg_weight_ties"] = dict(mean_names=float((S > 0).sum(1).mean()), mean_distinct_weights=float(nz.apply(lambda r: r.dropna().nunique(), axis=1).mean()), stock_sleeve_mean=float(S.sum(1).mean()))
if STAGE == "ai":
    # AI residual returns (reimplemented from ai_hiliq_sec8_supplement.neutral_eps)
    P = pd.concat([pd.read_parquet(PC/f"cs_panel_{y}.parquet", columns=["date","instrument","hiliq","ret","logmv","ind"]) for y in (2023, 2024, 2025, 2026)])
    RW = P.pivot_table(index="date", columns="instrument", values="ret").astype("float32").sort_index()
    mom = RW.shift(1).rolling(20, min_periods=15).sum().stack().rename("mom20"); vol = RW.shift(1).rolling(20, min_periods=15).std().stack().rename("vol20"); del RW
    P = P[P.date >= "2024-01-01"].join(mom.astype("float32"), on=["date","instrument"]).join(vol.astype("float32"), on=["date","instrument"]); del mom, vol; gc.collect()
    rows = []
    for d, g in P[P.hiliq].groupby("date", sort=True):
        g = g.dropna(subset=["ret","logmv","mom20","vol20"]); g = g[g.ind >= 0]
        if len(g) < 100: continue
        X = np.column_stack([pd.get_dummies(g.ind).to_numpy(float), g[["logmv","mom20","vol20"]].to_numpy(float)]); X[:, -3:] = (X[:, -3:]-X[:, -3:].mean(0))/X[:, -3:].std(0)
        y = g.ret.to_numpy(float).clip(-.21, .31); b, *_ = np.linalg.lstsq(X, y, rcond=None)
        rows.append(pd.DataFrame({"date": d, "instrument": g.instrument.values, "eps": (y-X@b).astype("float32")}))
    del P; gc.collect()
    EI = pd.concat(rows).pivot(index="date", columns="instrument", values="eps"); EI.index = pd.to_datetime(EI.index); EI = EI.reindex(index=EA.index, columns=EA.columns); del rows
    EI.to_parquet(TMP/"EI.parquet"); print("EI", f"rss={rss():.0f}", flush=True); sys.exit(0)
cmp = pd.concat([EA.stack().rename("a"), EI.stack().rename("i")], axis=1).dropna(); out["eps_corr_alpha_vs_ai"] = float(cmp.a.corr(cmp.i))
# full leg book weights incl ETF (AI weighting)
W = pd.read_parquet(LEG, columns=["date","instrument","target_weight"]); W["date"] = pd.to_datetime(W.date.astype(str).str[:10])
Wb = W.pivot_table(index="date", columns="instrument", values="target_weight", aggfunc="sum").reindex(index=c["ev"]).fillna(0)
def ai_net(E, Wbook):  # exact AI neutral_net definition
    H = Wbook.shift(1).fillna(0); st = [x for x in H.columns if x[:2] not in ("51","56","58","15")]
    e = E.reindex(index=H.index, columns=st).fillna(0); gross = (H[st].shift(1).fillna(0)*e).sum(1)
    to = H.diff().abs().sum(1).fillna(H.abs().sum(1)); net = (gross-S8.COST*to).loc[S8.START:S8.END]
    return dict(ann244=float(net.mean()*244), t=float(net.mean()/net.std()*np.sqrt(len(net))), stock_share=float(H[st].sum(1).mean()))
def ai_topn(Wbook, N):  # AI leaf_topn: stock sleeve top-N by weight (sort_values desc), rescaled to sleeve total, ETF kept
    out_ = Wbook.copy()*0
    for d in Wbook.index:
        w = Wbook.loc[d]; w = w[w > 0]; e = w[[i[:2] in ("51","56","58","15") for i in w.index]]; s = w.drop(e.index)
        if len(s): k = s.sort_values(ascending=False).head(N); out_.loc[d, k.index] = k*s.sum()/k.sum()
        out_.loc[d, e.index] = e
    return out_
res = {}
for en, E in (("eps_alpha", EA), ("eps_ai", EI)):
    for t, N in S8.TIERS.items():
        r = S8.neut_net(E, S8.topn(S, N)); res[f"{en}|alpha_topn_norm100|{t}"] = {k: v for k, v in r.items() if k != "series"}
        res[f"{en}|ai_book_topn|{t}"] = ai_net(E, ai_topn(Wb, N))
    res[f"{en}|ai_book_full"] = ai_net(E, Wb)
    r = S8.neut_net(E, S); res[f"{en}|alpha_full_sleeve_raw_weights"] = {k: v for k, v in r.items() if k != "series"}
    print(en, "done", f"rss={rss():.0f}", flush=True)
out["neutral_net"] = res
# IC variants
def rank_ic(Z, F): return S8.ic_series(dict(F=F), Z) if False else pd.Series({d: Z.loc[d][(Z.loc[d].notna()) & F.loc[d].notna()].rank().corr(F.loc[d][(Z.loc[d].notna()) & F.loc[d].notna()].rank()) for d in Z.index if ((Z.loc[d].notna()) & F.loc[d].notna()).sum() >= 50}).dropna()
F_raw = c["F"]; F_eA = EA.shift(-2).rolling(20, min_periods=1).sum().shift(-19); F_eI = EI.shift(-2).rolling(20, min_periods=1).sum().shift(-19)
ic = {}
for zn, Z in (("Z_alpha_resid_weight", ZA), ("Z_binary_member", (S > 0).astype(float).where(ZA.notna()))):
    for fn, F in (("fwd_raw_t0_t20", F_raw), ("fwd_epsAlpha_t2_t21", F_eA), ("fwd_epsAI_t2_t21", F_eI)):
        s = rank_ic(Z, F.reindex(index=Z.index, columns=Z.columns)); ic[f"{zn}|{fn}|rank"] = dict(ic=float(s.mean()), **{k: v for k, v in ic_tstats(s, 20).items() if k in ("ic_t_naive","ic_t_hac")})
    print(zn, "ic done", f"rss={rss():.0f}", flush=True)
out["ic"] = ic; out["peak_rss_mb"] = rss()
Path(R/"output/ai_factory/hiliq_sec8/eqinc_reconcile.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float)); print(json.dumps(out, ensure_ascii=False, indent=1, default=float))
