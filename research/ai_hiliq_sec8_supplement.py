#!/usr/bin/env python3
"""HI_LIQ V1 §8 supplement for five regenerated event legs (Alpha request). Read-only on legs; live=false; no Book-Smoke.
Residual IC/ICIR vs capacity_adv, idio α, ind+style-neutral net excess @60万/100万, fast/slow mismatch (ρ, holding period, stacking vs weighted-sum)."""
import json, sys, resource, numpy as np, pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
R = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(R))
import research.leaf_selfcheck_common as LC, research.alpha_decay_gate as ADG
from research.leaf_selfcheck_v3 import metrics, leaf_topn
L = R/"output/strategy_hiliq/legs"; PC = R/"output/ai_factory/panel_cache"; OUT = R/"output/ai_factory/hiliq_sec8"; OUT.mkdir(exist_ok=True)
LEGS = {"equity_incentive": "g1g5_equity_incentive_hiliq_v1_daily_weights_20261014_202436.parquet",
        "earnings_event": "g1g5_earnings_event_hiliq_v1_daily_weights_20261014_202822.parquet",
        "insider_increase": "g1g5_insider_increase_hiliq_v1_daily_weights_20261014_202928.parquet",
        "insurer_surv": "g1g5_insurer_surv_hiliq_v1_daily_weights_20261014_203108.parquet",
        "report_rc_allup": "g1g5_report_rc_allup_hiliq_v1_daily_weights_20261014_203201.parquet"}
CAP = L/"g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet"
X2 = ("2024-06-03", "2026-10-09"); NT = {"60w": 6, "100w": 10}; COST = ADG.COST
rss = lambda: resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024

def nw_t(x, lag):
    x = np.asarray(x, float); x = x[np.isfinite(x)]; n = len(x)
    if n < 10: return None
    m = x.mean(); u = x-m; v = u@u/n
    for k in range(1, lag+1): v += 2*(1-k/(lag+1))*(u[k:]@u[:-k])/n
    return float(m/np.sqrt(v/n)) if v > 0 else None

def neutral_eps(panel):
    """daily CS residual of ret on SW L1 dummies + logmv + mom20 + vol20 (lagged), within HI_LIQ pool."""
    out = []
    for d, g in panel[panel.hiliq].groupby("date", sort=True):
        g = g.dropna(subset=["ret", "logmv", "mom20", "vol20"]); g = g[g.ind >= 0]
        if len(g) < 100: continue
        D = pd.get_dummies(g.ind).to_numpy(float)
        X = np.column_stack([D, g[["logmv", "mom20", "vol20"]].to_numpy(float)])
        X[:, -3:] = (X[:, -3:]-X[:, -3:].mean(0))/X[:, -3:].std(0)
        y = g.ret.to_numpy(float).clip(-0.21, 0.31)
        b, *_ = np.linalg.lstsq(X, y, rcond=None)
        out.append(pd.DataFrame({"date": d, "instrument": g.instrument.values, "eps": (y-X@b).astype("float32")}))
    return pd.concat(out)

def main():
    P = pd.concat([pd.read_parquet(PC/f"cs_panel_{y}.parquet", columns=["date","instrument","hiliq","ret","logmv","ind"]) for y in (2023, 2024, 2025, 2026)])
    RW = P.pivot_table(index="date", columns="instrument", values="ret").astype("float32").sort_index()
    mom = RW.shift(1).rolling(20, min_periods=15).sum().stack().rename("mom20"); vol = RW.shift(1).rolling(20, min_periods=15).std().stack().rename("vol20"); del RW
    P = P[P.date >= "2024-01-01"]
    P = P.join(mom.astype("float32"), on=["date","instrument"]).join(vol.astype("float32"), on=["date","instrument"]); del mom, vol
    E = neutral_eps(P); print("eps", len(E), f"rss={rss():.0f}", flush=True)
    Ew = E.pivot(index="date", columns="instrument", values="eps").sort_index()
    days = list(Ew.index)
    fwd = {h: Ew.shift(-2).rolling(h, min_periods=1).sum().shift(-(h-1)) for h in (1, 5, 20)}  # ε over t+2..t+h+1 (T+1 open approx)
    pool = P[P.hiliq & (P.ind >= 0) & np.isfinite(P.logmv)][["date","instrument","ind","logmv"]].copy(); del P; import gc; gc.collect()
    cap = LC._w(CAP); cap["date"] = pd.to_datetime(cap.date)
    capset = {d: set(x.instrument) for d, x in cap[~cap.instrument.map(LC.etf)].groupby("date")}
    bench = ADG.bench().pct_change()
    rcap = LC._ret(LC._w(CAP)); bb = bench.reindex(rcap.index).fillna(0)
    def debeta(r):
        b = bench.reindex(r.index).fillna(0); be = np.cov(r, b)[0,1]/b.var(); return r-be*b, be
    rcap_res, _ = debeta(rcap)
    res = {"et": (datetime.now()-timedelta(hours=12)).strftime("%Y-%m-%d %H:%M"), "x2": X2, "cost_bp": COST*1e4, "legs": {}}
    def ic_series(sig_by_day, h, ctrl_cap=True):
        ics = []
        for d, gp in pool.groupby("date"):
            if d not in fwd[h].index or d not in sig_by_day: continue
            f = fwd[h].loc[d]; gp = gp[gp.instrument.isin(f.dropna().index)]
            if len(gp) < 200: continue
            s = gp.instrument.isin(sig_by_day[d]).to_numpy(float)
            if s.sum() < 3: continue
            cols = [pd.get_dummies(gp.ind).to_numpy(float), gp.logmv.to_numpy(float)[:,None]]
            if ctrl_cap: cols.append(gp.instrument.isin(capset.get(d, set())).to_numpy(float)[:,None])
            X = np.column_stack(cols); b,*_ = np.linalg.lstsq(X, s, rcond=None); sr = s-X@b
            ics.append((d, float(np.corrcoef(sr, f[gp.instrument].to_numpy(float))[0,1])))
        return pd.Series(dict(ics))
    def icstat(s, h):
        s = s[(s.index >= X2[0]) & (s.index <= X2[1])].dropna(); ss = s.iloc[::h]
        return dict(ic_mean=float(s.mean()), ic_std=float(ss.std()), icir=float(ss.mean()/ss.std()) if ss.std()>0 else None,
                    icir_ann244=float(ss.mean()/ss.std()*np.sqrt(244/h)) if ss.std()>0 else None, t=float(ss.mean()/ss.std()*np.sqrt(len(ss))) if ss.std()>0 else None, n=int(len(ss)), pos_rate=float((s>0).mean()), t_nw=nw_t(s.values, h-1))
    def neutral_net(W):
        Pw = W.pivot_table(index="date", columns="instrument", values="target_weight", aggfunc="sum").fillna(0); Pw.index = pd.to_datetime(Pw.index)
        H = Pw.shift(1).fillna(0)  # held from t+1 open ~ t+1 return day
        st = [c for c in H.columns if not LC.etf(c)]
        e = Ew.reindex(index=H.index, columns=st).fillna(0)
        gross = (H[st].shift(1).fillna(0)*e).sum(1)  # conservative: exposure starts the day after fill
        to = H.diff().abs().sum(1).fillna(H.abs().sum(1)); net = gross - COST*to
        net = net[(net.index >= X2[0]) & (net.index <= X2[1])]
        return dict(ann244=float(net.mean()*244), ann252=float(net.mean()*252), t=float(net.mean()/net.std()*np.sqrt(len(net))), ir244=float(net.mean()/net.std()*np.sqrt(244)), stock_share=float(H[st].sum(1).mean()))
    def hold_period(W):
        st = W[~W.instrument.map(LC.etf)].copy(); st["date"] = pd.to_datetime(st.date)
        idx = {d:i for i,d in enumerate(sorted(pd.to_datetime(W.date.unique())))}; st["k"] = st.date.map(idx)
        runs = []
        for _, x in st.groupby("instrument"):
            k = np.sort(x.k.values); br = np.where(np.diff(k) > 1)[0]; runs += list(np.diff(np.r_[-1, br, len(k)-1]))
        return float(np.mean(runs)) if runs else None
    def mix(capw, legw, share=0.2, mode="sum"):
        rows = []
        for d, gc in capw.groupby("date"):
            c = gc.set_index("instrument").target_weight; lw = legw.get(d)
            if mode == "sum":
                agg = (c*(1-share)).to_dict()
                if lw is not None:
                    for i, v in lw.items(): agg[i] = agg.get(i, 0)+share*v
            else:  # stacking: leg = fast tilt inside slow book, no new names
                agg = c.to_dict(); flag = set(lw[lw > 0].index) if lw is not None else set()
                stv = {i: v for i, v in agg.items() if not LC.etf(i)}; tot = sum(stv.values())
                if flag & set(stv):
                    t2 = {i: v*(1.5 if i in flag else 1.0) for i, v in stv.items()}; s2 = sum(t2.values())
                    for i, v in t2.items(): agg[i] = v*tot/s2
            for i in list(agg):
                if not LC.etf(i) and agg[i] > 0.06: agg[LC.BAL] = agg.get(LC.BAL, 0)+agg[i]-0.06; agg[i] = 0.06
            t = sum(agg.values()); rows += [(d, i, v/t) for i, v in agg.items()]
        return pd.DataFrame(rows, columns=["date","instrument","target_weight"])
    capw_full = LC._w(CAP)
    cap_ic = {h: icstat(ic_series(capset, h, ctrl_cap=False), h) for h in (1, 5, 20)}
    res["capacity_adv"] = dict(ic_ind_size=cap_ic, hold_days=hold_period(capw_full), neutral_net_full=neutral_net(capw_full))
    for tier, N in NT.items():
        ct = leaf_topn(capw_full, N); cw = pd.DataFrame([(d, i, v) for d, s in ct.items() for i, v in s.items()], columns=["date","instrument","target_weight"])
        res["capacity_adv"][tier] = dict(neutral_net=neutral_net(cw))
    for name, f in LEGS.items():
        W = LC._w(L/f); Wd = W.copy(); Wd["date"] = pd.to_datetime(Wd.date)
        sig = {d: set(x.instrument) for d, x in Wd[~Wd.instrument.map(LC.etf)].groupby("date")}
        r = LC._ret(W); rr = r[(r.index >= X2[0]) & (r.index <= X2[1])]
        b = bench.reindex(rr.index).fillna(0); c = rcap.reindex(rr.index).fillna(0)
        X = np.column_stack([np.ones(len(rr)), b, c]); beta, *_ = np.linalg.lstsq(X, rr.values, rcond=None)
        e = rr.values-X@beta; se = np.sqrt(e.var(ddof=3)/len(rr))
        rres, _ = debeta(r); ix = rres.index.intersection(rcap_res.index)
        ent = dict(
            ic_resid_vs_cap={h: icstat(ic_series(sig, h), h) for h in (1, 5, 20)},
            idio_alpha=dict(ann244=float(beta[0]*244), ann252=float(beta[0]*252), t=float(beta[0]/se), beta_mkt=float(beta[1]), beta_cap=float(beta[2])),
            neutral_net_full=neutral_net(W), rho_resid_vs_cap=float(np.corrcoef(rres[ix], rcap_res[ix])[0,1]),
            hold_days=hold_period(W), turnover_daily=float(LC._w(L/f).pivot_table(index="date",columns="instrument",values="target_weight").fillna(0).diff().abs().sum(1).mean()/2),
            mean_names=float(Wd[~Wd.instrument.map(LC.etf)].groupby("date").size().mean()))
        for tier, N in NT.items():
            lt = leaf_topn(W, N); lw = pd.DataFrame([(d, i, v) for d, s in lt.items() for i, v in s.items()], columns=["date","instrument","target_weight"])
            ct = leaf_topn(capw_full, N); cw = pd.DataFrame([(d, i, v) for d, s in ct.items() for i, v in s.items()], columns=["date","instrument","target_weight"])
            rc0 = LC._ret(cw); ws = LC._ret(mix(cw, lt, mode="sum")); stk = LC._ret(mix(cw, lt, mode="stack"))
            ix = rc0.index[(rc0.index >= X2[0]) & (rc0.index <= X2[1])].intersection(ws.index).intersection(stk.index)
            ent[tier] = dict(neutral_net=neutral_net(lw), cap=metrics(rc0[ix]), weighted_sum_80_20=metrics(ws[ix]), stacking_tilt=metrics(stk[ix]))
        res["legs"][name] = ent; print(name, json.dumps({k: ent[k] for k in ("idio_alpha","rho_resid_vs_cap")}, default=float), f"rss={rss():.0f}", flush=True)
    res["peak_rss_mb"] = rss()
    (OUT/"sec8_supplement.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))
    print("done", rss())
main()
