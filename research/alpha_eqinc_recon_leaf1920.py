"""Step B (Alpha, 2026-10-18): (1) equity_incentive sign reconciliation — factorial on one shared ctx;
(2) leaf19 cfacc_rnoa / leaf20 sue_resid §8 material on HI_LIQ X2 (same frozen §8 readings as
docs/v2/ALPHA_HILIQ_S8_PARADIGM_RULES_20261014_ZH.md). Reuses research/alpha_hiliq_s8_paradigm.py (not edited). live=false."""
import sys, json, gc, time, numpy as np, pandas as pd
from pathlib import Path
R = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(R))
import research.alpha_hiliq_s8_paradigm as S8
from research.alpha_combo_marginal import ic_tstats, nw_se
OUT = R/"output/alpha/recon_eqinc"; H = 20
log = lambda *a: print(time.strftime("%H:%M:%S"), *a, flush=True)
LEG = S8.LEGD/"g1g5_equity_incentive_hiliq_v1_daily_weights_20261014_202436.parquet"
AF = R/"output/ai_factory"
NEW = {"cfacc_rnoa": dict(w=AF/"g1g5_cfacc_rnoa_daily_weights_20261014_213132.parquet", a=AF/"leaf19_cfacc_rnoa/alpha_HILIQ_20261014_213132.parquet"),
       "sue_resid": dict(w=AF/"g1g5_sue_resid_daily_weights_20261014_220029.parquet", a=AF/"leaf20_sue_resid/alpha_HILIQ_20261014_220029.parquet")}

def ics(c, Z, F, method="spearman", minn=50):
    s = {}
    for d in Z.index:
        if d not in F.index: continue
        z, f = Z.loc[d], F.loc[d]; ok = z.notna() & f.notna()
        if ok.sum() >= minn and z[ok].std() > 0:
            s[d] = z[ok].rank().corr(f[ok].rank()) if method == "spearman" else z[ok].corr(f[ok])
    return pd.Series(s).dropna()
def pk(s): return dict(ic=float(s.mean()), icir=float(s.mean()/s.std()), n=int(len(s)), **{k: v for k, v in ic_tstats(s, H).items() if k.startswith("ic_t_") and k != "ic_t_note"})

def resid_custom(c, S, cols, extra=None):
    """residualize S on SW L1 dummies + chosen style cols (+extra panel); raw (not z) residual."""
    out = pd.DataFrame(np.nan, index=c["ev"], columns=c["U"])
    for d in c["ev"]:
        pool = c["INU"].columns[c["INU"].loc[d].values]
        Xd = pd.DataFrame({k: c["X"][k].loc[d, pool] for k in cols})
        if extra is not None: Xd["x"] = extra.loc[d, pool]
        Xd = Xd.join(pd.get_dummies(c["IND"].loc[d, pool].fillna("_UNK"), dtype=float)); ok = Xd.notna().all(axis=1)
        Xd = Xd[ok]; y = S.loc[d, Xd.index].values
        if len(Xd) < 50 or y.std() == 0: continue
        Xm = np.c_[np.ones(len(Xd)), Xd.values.astype(float)]; cf, *_ = np.linalg.lstsq(Xm, y, rcond=None)
        out.loc[d, Xd.index] = y - Xm @ cf
    return out

def net_series(E, W, lag=2):
    Wl = W.shift(lag).fillna(0.0); g = (Wl*E.reindex_like(Wl).fillna(0.0)).sum(axis=1)
    to = W.diff().abs().sum(axis=1).fillna(W.abs().sum(axis=1)).shift(1).fillna(0.0)
    return (g - S8.COST*to).iloc[3:], g.iloc[3:]
def nstat(E, W):
    n, g = net_series(E, W); se = nw_se(n.values, 5)
    return dict(ann_net=float(n.mean()*244), ann_gross=float(g.mean()*244), t_hac5=float(n.mean()/se) if se > 0 else None)
def sleeve(S):  # full stock sleeve normalized to 100%
    return S.div(S.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
def topn_rand(S, N, seed):
    rng = np.random.default_rng(seed); noise = pd.DataFrame(rng.random(S.shape)*1e-9, index=S.index, columns=S.columns)
    return S8.topn(S + noise.where(S > 0, 0.0), N)
def topn_hold(S, N, seed):
    """random tie-break but sticky: keep yesterday's picks while still held (avoids daily re-draw turnover)."""
    rng = np.random.default_rng(seed); W = pd.DataFrame(0.0, index=S.index, columns=S.columns); prev = []
    for d in S.index:
        held = list(S.columns[S.loc[d].values > 0]); keep = [i for i in prev if i in held]
        rest = [i for i in held if i not in keep]; rng.shuffle(rest); pick = (keep + rest)[:N]
        if pick: W.loc[d, pick] = 1.0/len(pick)
        prev = pick
    return W

t0 = time.time(); c = S8.build(); log("ctx")
E = S8.resid_ret(c); log("E alpha")
C = S8.panel()[3]
F0 = c["F"]                                              # ours: close t -> close t+20, raw
F1 = (C.shift(-(H+1))/C.shift(-1) - 1).reindex(c["ev"])  # T+1: close t+1 -> close t+21, raw
Ef = E.reindex(C.index) if False else E
EA_fwd = E.shift(-2).rolling(H, min_periods=1).sum().shift(-(H-1))  # alpha-eps sum t+2..t+21 (AI label form, our eps)
ae = pd.read_parquet(OUT/"_ai_eps.parquet"); ae["date"] = pd.to_datetime(ae.date)
EI = ae.pivot(index="date", columns="instrument", values="eps").reindex(index=c["ev"], columns=c["U"]); del ae; gc.collect()
EI_fwd = EI.shift(-2).rolling(H, min_periods=1).sum().shift(-(H-1))
res = {"recon": {}, "leaves": {}}
S = S8.sig(c, LEG); Scap = S8.sig(c, S8.CAP); M = (S > 0).astype(float); Mcap = (Scap > 0).astype(float)
res["recon"]["leg_structure"] = dict(names_per_day=float((S > 0).sum(1).mean()), distinct_nonzero_weights=float(S[S > 0].apply(lambda r: r.dropna().nunique(), axis=1).mean()))
full = ["mc", "beta", "mom", "liq"]
ZA = S8.resid_multi(c, {"leg": S})["leg"]; ZI = S8.resid_multi(c, {"leg": S}, extra=Scap)["leg"]; log("Z std")
Rw_ind_mc_capM = resid_custom(c, M, ["mc"], extra=Mcap); log("Z ai-x")
R_full_w = resid_custom(c, S, full)
grid = {}
grid["1_ours_frozen: w|full|spearman|raw t..t+20"] = pk(ics(c, ZA, F0))
grid["2_pearson: w|full|pearson|raw t..t+20"] = pk(ics(c, R_full_w, F0, "pearson"))
grid["3_T+1 label: w|full|spearman|raw t+1..t+21"] = pk(ics(c, ZA, F1))
grid["4_pearson+T+1: w|full|pearson|raw t+1..t+21"] = pk(ics(c, R_full_w, F1, "pearson"))
grid["5_resid label(alpha eps): w|full|spearman|eps t+2..t+21"] = pk(ics(c, ZA, EA_fwd))
grid["6_resid label(alpha eps): w|full|pearson|eps t+2..t+21"] = pk(ics(c, R_full_w, EA_fwd, "pearson"))
grid["7_AI X on our pool: memb|ind+mc+capM|pearson|alpha eps t+2..t+21"] = pk(ics(c, Rw_ind_mc_capM, EA_fwd, "pearson"))
grid["8_AI X+AI eps on our pool: memb|ind+mc+capM|pearson|AI eps t+2..t+21"] = pk(ics(c, Rw_ind_mc_capM, EI_fwd, "pearson"))
grid["9_AI X spearman raw: memb|ind+mc+capM|spearman|raw t..t+20"] = pk(ics(c, Rw_ind_mc_capM, F0))
grid["10_ours X+AI eps: w|full|pearson|AI eps t+2..t+21"] = pk(ics(c, R_full_w, EI_fwd, "pearson"))
grid["11_A' frozen: w|full+cap|spearman|raw"] = pk(ics(c, ZI, F0))
# where does the Spearman sign come from: IC restricted to held names vs non-held
hold_ic = {}; nonhold_ic = {}
for d in c["ev"]:
    z, f, m = ZA.loc[d], F0.loc[d], M.loc[d] > 0; ok = z.notna() & f.notna()
    if (ok & m).sum() >= 5: hold_ic[d] = f[ok & m].mean() - f[ok & ~m].mean()
    if (ok & ~m).sum() >= 50: nonhold_ic[d] = z[ok & ~m].rank().corr(f[ok & ~m].rank())
hs, ns = pd.Series(hold_ic).dropna(), pd.Series(nonhold_ic).dropna()
grid["12_held minus nonheld raw fwd20 (mean diff)"] = dict(mean=float(hs.mean()), **{k: v for k, v in ic_tstats(hs, H).items() if k.startswith("ic_t_") and k != "ic_t_note"})
grid["13_spearman among NON-held only (pure style-residual noise)"] = pk(ns)
res["recon"]["ic_grid"] = grid; log("ic grid")
B = {}
B["ours_frozen_topN_first(60w)"] = nstat(E, S8.topn(S, 6)); B["ours_frozen_topN_first(100w)"] = nstat(E, S8.topn(S, 10))
B["full_sleeve_alpha_eps"] = nstat(E, sleeve(S)); B["full_sleeve_AI_eps"] = nstat(EI, sleeve(S))
B["book_incl_etf_AI_eps(~AI full)"] = nstat(EI, S)
for N, t in ((6, "60w"), (10, "100w")):
    a = [nstat(E, topn_rand(S, N, k))["ann_net"] for k in range(20)]; h = [nstat(E, topn_hold(S, N, k))["ann_net"] for k in range(20)]
    B[f"topN_random_daily_redraw_{t}"] = dict(mean=float(np.mean(a)), sd=float(np.std(a)), min=float(np.min(a)), max=float(np.max(a)))
    B[f"topN_random_sticky_{t}"] = dict(mean=float(np.mean(h)), sd=float(np.std(h)), min=float(np.min(h)), max=float(np.max(h)))
    B[f"topN_first_AI_eps_{t}"] = nstat(EI, S8.topn(S, N))
res["recon"]["B_grid"] = B; log("B grid")
eps_corr = pd.concat([E.stack().rename("a"), EI.stack().rename("i")], axis=1).dropna(); res["recon"]["eps_corr_alpha_vs_ai"] = float(eps_corr.a.corr(eps_corr.i)); del eps_corr
(OUT/"step_b_recon.json").write_text(json.dumps(res["recon"], ensure_ascii=False, indent=1, default=float)); log("recon saved")
# ---------- leaf19 / leaf20 §8 (skipped: AI did not submit; 主 Agent 00:17) ----------
import os
if os.environ.get("RUN_LEAF1920") != "1": log("done(recon only)", round(time.time()-t0)); sys.exit(0)
ZcapA = S8.resid_multi(c, {"cap": Scap})["cap"]; ICcap = S8.ic_series(c, ZcapA); cap_to = float(Scap.diff().abs().sum(axis=1).mean())
rc, _ = net_series(E, S8.topn(Scap, 25))
for leaf, p in NEW.items():
    r = {}
    Sw = S8.sig(c, p["w"]); a = pd.read_parquet(p["a"], columns=["date", "instrument", "alpha"]); a = a[(a.date >= S8.START) & (a.date <= S8.END)]
    Sa = a.pivot_table(index="date", columns="instrument", values="alpha").reindex(index=c["ev"], columns=c["U"]); del a
    r["coverage"] = dict(alpha_names_median=float(Sa.notna().sum(1).median()), weight_days=int((Sw.sum(1) > 0).sum()), names_per_day=float((Sw > 0).sum(1)[Sw.sum(1) > 0].mean()))
    Za_alpha = S8.resid_multi(c, {"x": Sa.fillna(0.0).where(Sa.notna(), 0.0)})["x"].where(Sa.notna())
    Zi_alpha = S8.resid_multi(c, {"x": Sa.fillna(0.0)}, extra=Scap)["x"].where(Sa.notna())
    r["single_leaf_alpha_vector"] = dict(A_raw_spearman=pk(ics(c, Sa, F1)), A_resid_spearman_T1=pk(ics(c, Za_alpha, F1)),
                                         A_resid_spearman_t0=pk(ics(c, Za_alpha, F0)), A_prime_vs_cap_T1=pk(ics(c, Zi_alpha, F1)))
    Za = S8.resid_multi(c, {"x": Sw})["x"]; Zi = S8.resid_multi(c, {"x": Sw}, extra=Scap)["x"]
    A = S8.icpack(S8.ic_series(c, Za)); Ap = S8.icpack(S8.ic_series(c, Zi))
    combo = (0.8*ZcapA + 0.2*Zi.fillna(0)).where(ZcapA.notna()); ICc = S8.ic_series(c, combo); ix = ICc.index.intersection(ICcap.index)
    cc, cp = S8.icpack(ICc[ix]), S8.icpack(ICcap[ix]); dIC = ICc[ix] - ICcap[ix]
    cmc = dict(d_ic=float(dIC.mean()), d_icir_full=cc["icir_full"]-cp["icir_full"],
               d_icir_roll=(cc["icir_roll252_median"]-cp["icir_roll252_median"]) if cc["icir_roll252_median"] is not None and cp["icir_roll252_median"] is not None else None,
               d_ic_tstats=ic_tstats(dIC, H))
    Bx = {"full_sleeve": nstat(E, sleeve(Sw))}
    for N, t in ((6, "60w"), (10, "100w")):
        Bx[t+"_rank_by_alpha"] = nstat(E, S8.topn(Sw*(1+1e-6*Sa.rank(axis=1, pct=True).fillna(0)), N))  # ties broken by AI alpha order (prereg: α 降序)
    rl, _ = net_series(E, sleeve(Sw)); jx = rl.index.intersection(rc.index); y, x = rl[jx].values, rc[jx].values
    Xm = np.c_[np.ones(len(x)), x]; cf, *_ = np.linalg.lstsq(Xm, y, rcond=None); se = nw_se(y - Xm@cf, 5)
    rho = float(np.nanmean([Za.loc[d].corr(ZcapA.loc[d]) for d in c["ev"]])); to = float(Sw.diff().abs().sum(axis=1).mean()); hp = cap_to/to if to > 0 else None
    Cx = dict(rho_resid_vs_cap=rho, to_daily_leaf=to, to_daily_cap=cap_to, holding_period_ratio=hp, same_band=bool(hp is not None and 0.5 <= hp <= 2),
              stacked_ic=cc["rank_ic"], cap_ic=cp["rank_ic"], weighted_sum_ic=float(0.8*cp["rank_ic"]+0.2*Ap["rank_ic"]),
              ortho_alpha_ann=float(cf[0]*244), ortho_alpha_t_hac5=float(cf[0]/se) if se > 0 else None, beta_on_cap=float(cf[1]))
    vA = A["rank_ic"] > 0 and A["icir_full"] > 0 and (A["icir_roll252_median"] or -1) > 0
    vAp = Ap["rank_ic"] > 0 and cmc["d_ic"] >= 0.003 and cmc["d_icir_full"] >= 0.05 and (cmc["d_icir_roll"] is not None and cmc["d_icir_roll"] >= 0.05)
    vB = all(Bx[t+"_rank_by_alpha"]["ann_net"] > 0 for t in ("60w", "100w")); vC = rho <= 0.5 and not (rho > 0.3 and Cx["same_band"] and Cx["ortho_alpha_ann"] <= 0)
    r.update(A=A, A_prime=Ap, cmc_ic=cmc, B=Bx, C=Cx, verdict=dict(A=vA, A_prime=vAp, B=vB, C=vC, all_pass=bool(vA and vAp and vB and vC)))
    res["leaves"][leaf] = r; log(leaf, r["verdict"])
(OUT/"step_b_leaf1920_s8.json").write_text(json.dumps(res["leaves"], ensure_ascii=False, indent=1, default=float)); log("done", round(time.time()-t0))
