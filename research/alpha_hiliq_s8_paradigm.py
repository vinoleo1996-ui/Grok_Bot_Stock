"""§8 paradigm material for HI_LIQ event legs (Alpha). Rules frozen first:
docs/v2/ALPHA_HILIQ_S8_PARADIGM_RULES_20261014_ZH.md. Research-grade; live=false; promotion=false; no GP; no Eng.
Universe HI_LIQ_V1.1 mask; window X2 2024-06-03..2026-10-09; h=20; styles: SW L1 + log float mcap + beta120 + mom(t-120..t-20) + log ADV20.
"""
from __future__ import annotations
import sys, json, time
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import research.alpha_decay_gate as ADG
from research.alpha_combo_marginal import ic_tstats, nw_se
OUT = ROOT / "output/alpha/hiliq_s8"; OUT.mkdir(parents=True, exist_ok=True)
MASK = ROOT / "output/strategy_hiliq/universe_mask_hiliq_v1.parquet"
LEGD = ROOT / "output/strategy_hiliq/legs"
CAP = LEGD / "g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet"
LEGS = {"equity_incentive": "202436", "earnings_event": "202822", "insider_increase": "202928",
        "insurer_surv": "203108", "report_rc_allup": "203201"}
TYPE_CAP = {"report_rc_allup": "report", "insurer_surv": "survey"}
START, END, H, COST, BAL = "2024-06-03", "2026-10-09", 20, ADG.COST, "510300.SH"
TIERS = {"60w": 6, "100w": 10}
log = lambda *a: print(time.strftime("%H:%M:%S"), *a, flush=True)


def panel():
    cp = OUT / "_panel_close.parquet"
    mk = pd.read_parquet(MASK, columns=["date", "instrument", "in_universe", "adv20_yuan"],
                         filters=[("date", ">=", pd.Timestamp(START)), ("date", "<=", pd.Timestamp(END))])
    mk["instrument"] = mk.instrument.astype(str); mk["date"] = pd.to_datetime(mk.date)
    INU = mk.pivot_table(index="date", columns="instrument", values="in_universe", aggfunc="max").fillna(False).astype(bool)
    U = sorted(INU.columns[INU.any()])
    ADV = mk.pivot_table(index="date", columns="instrument", values="adv20_yuan").reindex(columns=U)
    INU = INU.reindex(columns=U)
    if cp.exists():
        C = pd.read_parquet(cp)
    else:
        b = ADG.bench(); days = b.index[(b.index >= "2023-06-01") & (b.index <= "2026-11-30")]
        cols = {}
        for k, i in enumerate(U):
            try: cols[i] = ADG._close(i).reindex(days)
            except Exception: pass
            if k % 200 == 0: log("close", k, len(U))
        C = pd.DataFrame(cols); C["__b"] = b.reindex(days); C.to_parquet(cp)
    rb = C.pop("__b").pct_change()
    C = C.reindex(columns=U)
    return U, INU, ADV, C, rb


def build():
    U, INU, ADV, C, rb = panel()
    R = C.pct_change(fill_method=None)
    ev = INU.index[(INU.index >= START) & (INU.index <= END)]
    beta = R.rolling(120, min_periods=60).cov(rb).div(rb.rolling(120, min_periods=60).var(), axis=0)
    mom = C.shift(20) / C.shift(120) - 1
    F = C.shift(-H) / C - 1
    from research.g1g5_x2_panel_stitch import to_panel_id
    from research.g1g5_nontextbook_weights import _load_sw_members
    from research.hiliq_v1_universe import industry_on_date
    pids = {to_panel_id(i): i for i in U}
    fm = pd.read_parquet(ROOT / "data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet",
                         columns=["instrument_id", "trade_date", "float_mktcap"],
                         filters=[("trade_date", ">=", pd.Timestamp(START)), ("instrument_id", "in", list(pids))])
    fm["i"] = fm.instrument_id.map(pids)
    MC = np.log(fm.pivot_table(index="trade_date", columns="i", values="float_mktcap").reindex(ev).ffill()).reindex(columns=U)
    sw = _load_sw_members()
    me = pd.Series(ev, index=ev).groupby(ev.to_period("M")).max().values
    IND = pd.DataFrame([industry_on_date(U, d, sw) for d in me], index=me).reindex(columns=U).reindex(ev, method="ffill")
    X = dict(mc=MC, beta=beta.reindex(ev), mom=mom.reindex(ev), liq=np.log(ADV.reindex(ev).clip(lower=1)))
    return dict(U=U, ev=ev, INU=INU.reindex(ev), R=R, F=F.reindex(ev), X=X, IND=IND)


_XC = {}


def xmat(c, d):
    """Cached (pool, Xm) for day d: intercept + styles + SW L1 dummies, rows with complete styles."""
    if d not in _XC:
        pool = c["INU"].columns[c["INU"].loc[d].values]
        Xd = pd.DataFrame({k: v.loc[d, pool] for k, v in c["X"].items()})
        Xd = Xd.join(pd.get_dummies(c["IND"].loc[d, pool].fillna("_UNK"), dtype=float))
        ok = Xd.notna().all(axis=1)
        Xd = Xd[ok]
        _XC[d] = (Xd.index, np.c_[np.ones(len(Xd)), Xd.values.astype(float)])
    return _XC[d]


def resid_multi(c, Ss: dict, extra: pd.DataFrame | None = None) -> dict:
    """Residualize several signals at once; z-score per day. extra = one additional regressor panel."""
    out = {k: pd.DataFrame(np.nan, index=c["ev"], columns=c["U"]) for k in Ss}
    for d in c["ev"]:
        pool, Xm = xmat(c, d)
        if len(pool) < 50: continue
        if extra is not None: Xm = np.c_[Xm, extra.loc[d, pool].values]
        Y = np.column_stack([Ss[k].loc[d, pool].values for k in Ss])
        cf, *_ = np.linalg.lstsq(Xm, Y, rcond=None); E = Y - Xm @ cf
        for j, k in enumerate(Ss):
            e = E[:, j]
            if Y[:, j].std() > 0 and e.std() > 0: out[k].loc[d, pool] = (e - e.mean()) / e.std()
    return out


def resid_ret(c):
    """Daily cross-sectional residual returns vs industry+style exposures at t-1 = return relative to neutralized HI_LIQ pool."""
    E = pd.DataFrame(np.nan, index=c["ev"], columns=c["U"]); evs = list(c["ev"])
    for k in range(1, len(evs)):
        d0, d = evs[k - 1], evs[k]
        pool, Xm = xmat(c, d0)
        y = c["R"].loc[d, pool].values; ok = ~np.isnan(y)
        if ok.sum() < 50: continue
        cf, *_ = np.linalg.lstsq(Xm[ok], y[ok], rcond=None)
        E.loc[d, pool[ok]] = y[ok] - Xm[ok] @ cf
    return E


def sig(c, path):
    d = pd.read_parquet(path, columns=["date", "instrument", "target_weight"]); d["date"] = pd.to_datetime(d.date.astype(str).str[:10])
    d = d[d.instrument != BAL]
    return d.pivot_table(index="date", columns="instrument", values="target_weight", aggfunc="sum").reindex(index=c["ev"], columns=c["U"]).fillna(0.0)


def ic_series(c, Z):
    s = {}
    for d in Z.index:
        z, f = Z.loc[d], c["F"].loc[d]; ok = z.notna() & f.notna()
        if ok.sum() >= 50 and z[ok].std() > 0: s[d] = z[ok].rank().corr(f[ok].rank())
    return pd.Series(s).dropna()


def icpack(s):
    roll = (s.rolling(252).mean() / s.rolling(252).std()).dropna()
    return dict(rank_ic=float(s.mean()), icir_full=float(s.mean() / s.std()),
                icir_roll252_median=float(roll.median()) if len(roll) else None, n=int(len(s)), **ic_tstats(s, H))


def topn(S, N):
    W = S.copy()
    rk = W.rank(axis=1, ascending=False, method="first")
    W = W.where((rk <= N) & (W > 0), 0.0)
    return W.div(W.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)


def neut_net(E, W):
    Wl = W.shift(2).fillna(0.0)  # T signal → T+1 open fill ≈ earns from T+2 close-to-close (conservative)
    g = (Wl * E.reindex_like(Wl).fillna(0.0)).sum(axis=1)
    to = W.diff().abs().sum(axis=1).fillna(W.abs().sum(axis=1)).shift(1).fillna(0.0)
    n = (g - COST * to).iloc[3:]; act = Wl.sum(axis=1).iloc[3:] > 0
    se = nw_se(n.values, 5)
    return dict(ann_net_excess=float(n.mean() * 244), ann_gross_excess=float(g.iloc[3:].mean() * 244),
                ann_cost=float(COST * to.iloc[3:].mean() * 244), to_daily_two_sided=float(to.mean()),
                t_hac5=float(n.mean() / se) if se > 0 else None, active_day_frac=float(act.mean()), series=n)


def run():
    t0 = time.time(); c = build(); log("ctx", round(time.time() - t0))
    E = resid_ret(c); log("resid_ret")
    Scap = sig(c, CAP)
    SL = {leg: sig(c, LEGD / f"g1g5_{leg}_hiliq_v1_daily_weights_20261014_{st}.parquet") for leg, st in LEGS.items()}
    ZA = resid_multi(c, {"cap": Scap, **SL}); log("resid A")
    ZI = resid_multi(c, SL, extra=Scap); log("resid A_prime")
    Zcap = ZA["cap"]; ICcap = ic_series(c, Zcap)
    cap_to = float(Scap.diff().abs().sum(axis=1).mean())
    cb = neut_net(E, topn(Scap, 25)); capB = {t: cb for t in TIERS}  # capacity_adv own sleeve (≤25 names) as fast/slow reference
    res = dict(cap=dict(ic=icpack(ICcap), to_daily=cap_to, neut_net=capB["60w"] | {"series": None}))
    for leg, st in LEGS.items():
        log("leg", leg)
        p = LEGD / f"g1g5_{leg}_hiliq_v1_daily_weights_20261014_{st}.parquet"
        S = SL[leg]; Za = ZA[leg]; A = icpack(ic_series(c, Za))
        Zi = ZI[leg]; Ap = icpack(ic_series(c, Zi))
        combo = (0.8 * Zcap + 0.2 * Zi.fillna(0)).where(Zcap.notna()); ICc = ic_series(c, combo)
        ix = ICc.index.intersection(ICcap.index); dIC = ICc[ix] - ICcap[ix]
        ccomb = icpack(ICc); ccap = icpack(ICcap[ix])
        d_icir_roll = (ccomb["icir_roll252_median"] - ccap["icir_roll252_median"]) if ccomb["icir_roll252_median"] is not None and ccap["icir_roll252_median"] is not None else None
        ws_ic = 0.8 * ccap["rank_ic"] + 0.2 * Ap["rank_ic"]
        B = {}
        for t, N in TIERS.items():
            r = neut_net(E, topn(S, N)); B[t] = {k: v for k, v in r.items() if k != "series"}
            if t == "60w": rl = r["series"]
        rc = capB["60w"]["series"]; jx = rl.index.intersection(rc.index); y, x = rl[jx].values, rc[jx].values
        Xm = np.c_[np.ones(len(x)), x]; cf, *_ = np.linalg.lstsq(Xm, y, rcond=None); e = y - Xm @ cf
        se_a = nw_se(e, 5)
        rho = float(np.nanmean([Za.loc[d].corr(Zcap.loc[d]) for d in c["ev"]]))
        to_leg = float(S.diff().abs().sum(axis=1).mean())
        hp_ratio = (cap_to / to_leg) if to_leg > 0 else None  # leaf holding period / cap holding period
        same_band = hp_ratio is not None and 0.5 <= hp_ratio <= 2
        ortho_alpha = float(cf[0] * 244)
        Cc = dict(rho_resid_vs_cap=rho, to_daily_leaf=to_leg, to_daily_cap=cap_to, holding_period_ratio_leaf_over_cap=hp_ratio,
                  same_frequency_band=bool(same_band), stacked_ic=ccomb["rank_ic"], cap_ic_same_days=ccap["rank_ic"],
                  weighted_sum_ic=float(ws_ic), stacked_minus_weighted_sum=float(ccomb["rank_ic"] - ws_ic),
                  ortho_alpha_ann_vs_cap=ortho_alpha, ortho_alpha_t_hac5=float(cf[0] / se_a) if se_a > 0 else None,
                  beta_on_cap=float(cf[1]), corr_neut_ret_vs_cap=float(np.corrcoef(x, y)[0, 1]))
        cmc = dict(d_ic=float(dIC.mean()), d_icir_full=ccomb["icir_full"] - ccap["icir_full"], d_icir_roll252_median=d_icir_roll,
                   d_ic_tstats=ic_tstats(dIC, H))
        vA = A["rank_ic"] > 0 and A["icir_full"] > 0 and (A["icir_roll252_median"] or -1) > 0
        vAp = Ap["rank_ic"] > 0 and cmc["d_ic"] >= 0.003 and cmc["d_icir_full"] >= 0.05 and (d_icir_roll is not None and d_icir_roll >= 0.05)
        vB = all(B[t]["ann_net_excess"] > 0 for t in TIERS)
        vC = rho <= 0.5 and not (rho > 0.3 and same_band and ortho_alpha <= 0)
        allp = vA and vAp and vB and vC
        status = "RESEARCH_ACCEPT" if allp else "WATCH"
        if leg in TYPE_CAP and allp: status = "WATCH"
        res[leg] = dict(stamp=st, file=str(p.relative_to(ROOT)), A=A, A_prime=Ap, cmc=cmc, B=B, C=Cc,
                        verdict=dict(A=vA, A_prime=vAp, B=vB, C=vC, all_pass=allp, type_cap=TYPE_CAP.get(leg), status=status))
        log(leg, res[leg]["verdict"])
    res["meta"] = dict(rules="docs/v2/ALPHA_HILIQ_S8_PARADIGM_RULES_20261014_ZH.md", universe="HI_LIQ_V1.1", window=[START, END], h=H,
                       live=False, promotion_approved=False, gp=False, eng_dispatched=False,
                       caveat="B uses capacity_adv top-25 sleeve as fast/slow reference; T+1 approximated by 2-day lag on close-to-close residual returns; not Eng X2.")
    (OUT / "ALPHA_HILIQ_S8_20261014.json").write_text(json.dumps(res, ensure_ascii=False, indent=2, default=lambda o: None))
    log("done", round(time.time() - t0))


if __name__ == "__main__":
    run()
