#!/usr/bin/env python3
"""Beta S2-3 cosign empirical check (no NAV / no returns reported).
Mode A 'v1_2_drift': archived v1.2 targets (returns already public), w_cur with raw-close price drift.
Mode B 'v1_3pre_nodrift': archived v1.3 pre-ruling targets (void, unscored), w_cur = prior post-trade weights, NO price info.
Variants: unband | band_aon (draft: all-or-nothing daily disable) | band_greedy (Beta amendment: greedy partial unfreeze).
HARD recheck relative: bound_k = max(spec_k, target_k) so v1.2/v1.3pre target defects do not force disable."""
import sys, pickle, json
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "research"))
import optimizer_lambda_calib_sealed as C
OUT = ROOT / "output/beta/s2_3_band_check"; CACHE = OUT / "_cache"
BAND = 0.005; BAL = C.BALLAST; X2S = pd.Timestamp("2024-06-03")
CK = {"v1_2_drift": ROOT / "output/strategy_optimizer/core_x2/_ckpt_v1_2",
      "v1_3pre_nodrift": ROOT / "output/strategy_optimizer/core_x2/_archive_v1_3_pre_ruling/_ckpt_v1_3"}
SLEEVES = {"equity_100": 0.0, "equity80_etf20_510300": 0.2}

def expo(wl, D):
    lnm = D["ln_mcap"].astype(float); pool = D["alpha"].index
    x = lnm.reindex(pool); z = (x - x.mean()) / (x.std(ddof=0) + 1e-12)
    m = (x - x.mean()) ** 2; m = (m - m.mean()) / (m.std(ddof=0) + 1e-12)
    b = D["betas"].reindex(pool).fillna(1.0); wb = D["wb"].reindex(pool).fillna(0.0)
    we_all = wl.drop(BAL, errors="ignore"); we = we_all.reindex(pool).fillna(0.0)
    bal = float(wl.get(BAL, 0.0)); bb = float((wb * b).sum() / max(wb.sum(), 1e-12))
    f = lambda v: float((we * v.fillna(0)).sum() + bal * (wb * v.fillna(0)).sum() / max(wb.sum(), 1e-12))
    ind = D["industry"]; gi = lambda w: w.groupby(w.index.map(lambda n: ind.get(n, "_UNK"))).sum()
    eqs = float(we_all.sum()); pi = gi(we_all[we_all > 0]); bi = gi(wb) / max(wb.sum(), 1e-12) * eqs
    u = pi.index.union(bi.index); act = pi.reindex(u).fillna(0) - bi.reindex(u).fillna(0)
    # out-of-pool held names: β=1, z/m=0 (disclosed)
    oop = we_all.index.difference(pool); b_oop = float(we_all.reindex(oop).sum())
    return {"beta": float((we * b).sum() + b_oop + bal * bb) - bb, "size": f(z) - float((wb * z.fillna(0)).sum()),
            "mid": f(m) - float((wb * m.fillna(0)).sum()), "ind_act": float(act.abs().max()) / max(eqs, 1e-12),
            "ind_abs": float(pi.max()) / max(eqs, 1e-12), "maxw": float(we_all.max()) if len(we_all) else 0.0,
            "n": int((we_all > 1e-9).sum()), "cash": 1.0 - float(wl.sum()), "bb": bb}

def bounds(spec_slack, a, tx):
    s = 0.35 + spec_slack["size_slack"]; i = 0.08 + spec_slack["ind_slack"]
    return {"beta": max(0.10, abs(tx["beta"])), "size": max(s, abs(tx["size"])), "mid": max(s, abs(tx["mid"])),
            "ind_act": max(i, tx["ind_act"]), "ind_abs": max(0.20, tx["ind_abs"]), "maxw": max(C.NAME_CAP[a], tx["maxw"]),
            "cash_hi": max(0.02, tx["cash"])}

def excess(e, B):
    t = 1e-6; ex = {}
    for k in ("beta", "size", "mid"): ex[k] = max(0.0, abs(e[k]) - B[k] - t) / B[k]
    for k in ("ind_act", "ind_abs", "maxw"): ex[k] = max(0.0, e[k] - B[k] - t) / B[k]
    ex["cash_neg"] = max(0.0, -e["cash"] - t) / 0.02; ex["cash_hi"] = max(0.0, e["cash"] - B["cash_hi"] - t) / 0.02
    ex["n"] = float(e["n"] < 20 or e["n"] > 30)
    return ex

def run(mode):
    ck = CK[mode]; days = sorted(pd.Timestamp(p.stem) for p in ck.glob("*.pkl"))
    days = [d for d in days if d >= pd.Timestamp("2024-05-31")]
    recs = {d: pickle.load(open(ck / f"{d:%Y%m%d}.pkl", "rb")) for d in days}
    drift = mode.endswith("_drift")
    if drift:
        names = sorted({i for r in recs.values() for a in r.get("sleeves", {}) for sv in r["sleeves"][a].values() for i in sv["w"].index if i != BAL})
        bs = C.load_daily_basic_window(names, days[0] - pd.Timedelta(days=10), days[-1])
        px = bs.pivot_table(index="trade_date", columns="ts_code", values="close", aggfunc="last"); px.index = pd.to_datetime(px.index)
        etf = pd.read_parquet(ROOT / "data/v2/etf/etf_daily_adj.parquet", columns=["ts_code", "trade_date", "close_hfq"])
        etf = etf[etf.ts_code == BAL]; px[BAL] = pd.Series(etf.close_hfq.values, index=pd.to_datetime(etf.trade_date.astype(str))).reindex(px.index)
        px = px.sort_index().ffill()
    rows = []; ret = {}
    for a in (600_000, 1_000_000):
        for sv, bf in SLEEVES.items():
            st = {v: None for v in ("unband", "band_aon", "band_greedy")}; prev_d = None
            for d in days:
                r = recs[d]; D = pickle.load(open(CACHE / f"{d:%Y%m%d}.pkl", "rb"))
                ok = a in r.get("sleeves", {}) and D is not None
                tgt = r["sleeves"][a][sv]["w"].copy() if ok else None
                for v in st:
                    w = st[v]
                    if w is None:
                        if ok: st[v] = (tgt, None)
                        continue
                    wpost_prev = w[0]
                    if drift and prev_d is not None:
                        p0 = px.loc[:prev_d].iloc[-1]; p1 = px.loc[:d].iloc[-1]
                        rr = (p1 / p0).reindex(wpost_prev.index).fillna(1.0)
                        val = wpost_prev * rr; nav = float(val.sum()) + (1.0 - float(wpost_prev.sum()))
                        wcur = val / nav
                    else:
                        wcur = wpost_prev.copy()
                    if not ok:
                        st[v] = (wcur, None)
                        if v == "unband": rows.append({"mode": mode, "aum": a, "sleeve": sv, "date": d.date(), "variant": "ALL", "carry": True})
                        continue
                    tx = expo(tgt, D); B = bounds(r["log"][a]["slack"], a, tx)
                    stocks_both = [i for i in tgt.index if i != BAL and tgt[i] > 0 and wcur.get(i, 0) > 0]
                    frozen = [i for i in stocks_both if abs(tgt[i] - wcur[i]) <= BAND] if v != "unband" else []
                    def build(fz):
                        o = tgt.copy()
                        for i in fz: o[i] = wcur[i]
                        return o
                    wb_ = build(frozen); e = expo(wb_, D); ex = excess(e, B); fail = {k for k, x in ex.items() if x > 0}
                    disabled = False; n_unfrz = 0; fz = list(frozen)
                    if fail and v == "band_aon":
                        disabled = True; wb_ = tgt.copy(); e = expo(wb_, D)
                    elif fail and v == "band_greedy":
                        while fz and sum(excess(e, B).values()) > 0:
                            cand = []
                            for i in sorted(fz):
                                f2 = [j for j in fz if j != i]; e2 = expo(build(f2), D); cand.append((sum(excess(e2, B).values()), i, e2))
                            cand.sort(key=lambda t: (t[0], t[1])); _, i, e = cand[0]; fz.remove(i); n_unfrz += 1
                        wb_ = build(fz); e = expo(wb_, D)
                    stk = lambda s: s.drop(BAL, errors="ignore")
                    u = stk(wb_).index.union(stk(wcur).index)
                    to_exec = 0.5 * float((stk(wb_).reindex(u).fillna(0) - stk(wcur).reindex(u).fillna(0)).abs().sum()) / (1 - bf)
                    u2 = stk(wb_).index.union(stk(wpost_prev).index)
                    to_tt = 0.5 * float((stk(wb_).reindex(u2).fillna(0) - stk(wpost_prev).reindex(u2).fillna(0)).abs().sum()) / (1 - bf)
                    bal_trade = abs(float(wb_.get(BAL, 0)) - float(wcur.get(BAL, 0)))
                    db = [abs(wcur[i] - tgt[i]) * abs(D["betas"].get(i, 1.0) - tx["bb"]) for i in frozen]
                    dbr = [abs(wcur[i] - tgt[i]) * abs(D["betas"].get(i, 1.0)) for i in frozen]
                    rows.append({"mode": mode, "aum": a, "sleeve": sv, "date": d.date(), "variant": v, "carry": False, "x2": d >= X2S,
                                 "n_both": len(stocks_both), "n_frozen_init": len(frozen), "n_frozen_final": len(fz) if not disabled else 0,
                                 "disabled": disabled, "fail_keys": ",".join(sorted(fail)), "n_unfreeze": n_unfrz,
                                 "beta_tgt": tx["beta"], "beta_post": e["beta"], "dbeta": e["beta"] - tx["beta"],
                                 "dbeta_frozen_init": expo(build(frozen), D)["beta"] - tx["beta"] if frozen else 0.0,
                                 "bound_bud_neutral": BAND * len(frozen) and float(np.sum(db)), "bound_raw": float(np.sum(dbr)),
                                 "size_post": e["size"], "mid_post": e["mid"], "ind_act_post": e["ind_act"], "ind_abs_post": e["ind_abs"],
                                 "maxw_post": e["maxw"], "cash_post": e["cash"], "cash_tgt": tx["cash"], "n_post": e["n"], "neff_post_eq": float(stk(wb_).sum() ** 2 / (stk(wb_) ** 2).sum()),
                                 "to_exec": to_exec, "to_tt": to_tt, "etf_trade": bal_trade})
                    st[v] = (wb_, None)
                prev_d = d
    return pd.DataFrame(rows)

if __name__ == "__main__":
    df = pd.concat([run(m) for m in CK], ignore_index=True)
    df.to_csv(OUT / "s2_3_band_sim_rows.csv", index=False)
    x = df[(df.variant != "ALL") & (df.x2 == True)]
    g = x.groupby(["mode", "aum", "sleeve", "variant"]).agg(
        n_days=("date", "size"), to_exec_med=("to_exec", "median"), to_tt_med=("to_tt", "median"), to_exec_mean=("to_exec", "mean"),
        disabled_days=("disabled", "sum"), frz_med=("n_frozen_final", "median"), frz_init_med=("n_frozen_init", "median"),
        dbeta_init_absmax=("dbeta_frozen_init", lambda s: s.abs().max()), dbeta_absmax=("dbeta", lambda s: s.abs().max()),
        beta_post_absmax=("beta_post", lambda s: s.abs().max()), beta_tgt_absmax=("beta_tgt", lambda s: s.abs().max()),
        bound_bud_max=("bound_bud_neutral", "max"), bound_raw_max=("bound_raw", "max"),
        maxw_post_max=("maxw_post", "max"), cash_post_min=("cash_post", "min"), etf_trade_med=("etf_trade", "median")).reset_index()
    fk = x[x.variant == "band_aon"].groupby(["mode", "aum", "sleeve"])["fail_keys"].apply(lambda s: s[s != ""].str.split(",").explode().value_counts().to_dict())
    carry = df[df.variant == "ALL"].groupby(["mode", "aum", "sleeve"]).size().to_dict()
    g.to_csv(OUT / "s2_3_band_sim_summary.csv", index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
    print(g.round(4).to_string()); print("FAIL_KEYS(aon, pre-disable):"); print(fk.to_string()); print("CARRY", {str(k): v for k, v in carry.items()})
