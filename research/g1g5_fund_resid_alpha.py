#!/usr/bin/env python3
"""Leaf19 cfacc_rnoa / Leaf20 sue_resid — fundamental residual base-α (preregs AI_G1G5_CFACC_RNOA_* / AI_G1G5_SUE_RESID_*).
Industrial paradigm: pool-internal, ind+size+style+library(logADV≈capacity_adv) residualization, size-domain calibrate, slow α (20d rebal),
separate fast gate (3d resid-ret left tail), output daily α vector. Evaluation: own panel evaluator (T+1 open, 17.5bp, 244/252).
live=false; promotion=false; no Book-Smoke; chunked per year (RSS<1.5GB)."""
import argparse, warnings, json, resource, hashlib, sys, gc, numpy as np, pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
R = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(R))
PC = R/"output/ai_factory/panel_cache"; FP = R/"data/v2/financials_pit"
WIN = {"sealed": ("2018-01-02", "2024-05-31"), "x2": ("2024-06-03", "2026-10-09")}
UCOL = {"HILIQ": "hiliq", "FULLA": "fulla"}; IND_CAP = {"HILIQ": 0.25, "FULLA": 0.28}
NAME_W, MAX_N, REBAL, COST, BAL = 0.04, 20, 20, 0.00175, "510300.SH"; EXCL = {"600519.SH", "002371.SZ"}
warnings.filterwarnings("ignore")
rss = lambda: resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024

def first_version(df, cols):
    df = df.dropna(subset=["available_at"]).copy()
    df["avail"] = pd.to_datetime(df.available_at.astype(str).str[:10]) + pd.Timedelta(days=1)  # next calendar day ≥ next session
    df = df.sort_values("avail"); out = None
    for c in cols:  # per field: earliest non-null version; avail = latest of the fields used
        x = df.dropna(subset=[c]).drop_duplicates(["ts_code", "end_date"], keep="first")[["ts_code","end_date","avail",c]].rename(columns={"avail": "av_"+c})
        out = x if out is None else out.merge(x, on=["ts_code","end_date"], how="outer")
    out["avail"] = out[["av_"+c for c in cols]].max(1)
    return out[["ts_code", "end_date", "avail"] + cols]

def single_q(df, col):
    df = df.sort_values(["ts_code", "end_date"]).copy(); df["y"] = df.end_date.dt.year; df["q"] = df.end_date.dt.quarter
    prev = df.groupby("ts_code")[col].shift(1); py = df.groupby("ts_code").y.shift(1); pq_ = df.groupby("ts_code").q.shift(1)
    ok_prev = (py == df.y) & (pq_ == df.q-1)
    df[col+"_q"] = np.where(df.q == 1, df[col], np.where(ok_prev, df[col]-prev, np.nan))
    return df

def fund_table(leaf):
    fi = first_version(pd.read_parquet(FP/"financials_pit_tushare.parquet", columns=["ts_code","end_date","available_at","report_type","n_income","n_income_attr_p","operate_profit"]).query("report_type=='1'"), ["n_income","n_income_attr_p","operate_profit"])
    fi = fi[fi.ts_code.str[:1].isin(list("036"))]
    if leaf == "sue_resid":
        d = single_q(fi, "n_income_attr_p"); g = d.groupby("ts_code")["n_income_attr_p_q"]
        d["dq"] = d.n_income_attr_p_q - g.shift(4)
        # require exact 4-quarter lag continuity
        d["lagok"] = (d.groupby("ts_code").end_date.shift(4) == d.end_date - pd.DateOffset(years=1))
        d.loc[~d.lagok, "dq"] = np.nan
        sd = d.groupby("ts_code").dq.transform(lambda s: s.shift(1).rolling(8, min_periods=6).std())
        d["f1"] = (d.dq/sd).clip(-5, 5)
        # avail = max(own avail, needed lags assumed earlier); keep latest end_date per avail
        return d.dropna(subset=["f1"])[["ts_code","end_date","avail","f1"]]
    bc = first_version(pd.read_parquet(FP/"bs_cf_pit_tushare.parquet", columns=["ts_code","end_date","available_at","report_type","total_assets","n_cashflow_act"]).query("report_type=='1'"), ["total_assets","n_cashflow_act"])
    d = fi.merge(bc, on=["ts_code","end_date"], how="inner", suffixes=("", "_b")); d["avail"] = d[["avail","avail_b"]].max(1)
    for c in ("n_income","operate_profit","n_cashflow_act"): d = single_q(d, c)
    d = d.sort_values(["ts_code","end_date"]); g = d.groupby("ts_code")
    contig = g.end_date.shift(3) == (d.end_date - pd.offsets.QuarterEnd(3))
    for c in ("n_income","operate_profit","n_cashflow_act"):
        d[c+"_ttm"] = g[c+"_q"].transform(lambda s: s.rolling(4, min_periods=4).sum()).where(contig)
    ta_l4 = g.total_assets.shift(4).where(g.end_date.shift(4) == d.end_date - pd.DateOffset(years=1))
    avg_ta = (d.total_assets + ta_l4)/2
    d["cfacc"] = (d.n_income_ttm - d.n_cashflow_act_ttm)/avg_ta
    d["rnoa"] = d.operate_profit_ttm/avg_ta
    d["drnoa"] = d.rnoa - d.groupby("ts_code").rnoa.shift(4).where(g.end_date.shift(4) == d.end_date - pd.DateOffset(years=1))
    d = d.replace([np.inf, -np.inf], np.nan).dropna(subset=["cfacc","drnoa"])
    d = d[(d.cfacc.abs() < 2) & (d.drnoa.abs() < 2)]
    return d[["ts_code","end_date","avail","cfacc","drnoa"]]

def ols_resid(y, X):
    b, *_ = np.linalg.lstsq(X, y, rcond=None); return y - X@b

def dom_rank(v, mv):
    p70, p90 = np.nanquantile(mv, .7), np.nanquantile(mv, .9); dom = np.where(mv >= p90, 2, np.where(mv >= p70, 1, 0)); out = np.zeros(len(v))
    for k in (0, 1, 2):
        i = np.where(dom == k)[0]
        if len(i) > 1: out[i] = (v[i].argsort().argsort()+1)/len(i)*2-1-1/len(i)
    return out, dom

def build(leaf, uni, ft):
    col = UCOL[uni]; ALPHA, GATE = [], []; from collections import deque, defaultdict; tail = defaultdict(lambda: deque(maxlen=3))
    for y in range(2018, 2027):
        P = pd.concat([pd.read_parquet(PC/f"cs_panel_{yy}.parquet", columns=["date","instrument","ret","logmv","ind","adv20_yuan",col]) for yy in (y-1, y) if (PC/f"cs_panel_{yy}.parquet").exists()])
        RW = P.pivot_table(index="date", columns="instrument", values="ret").sort_index().astype("float32")
        mom20 = RW.shift(1).rolling(20, min_periods=15).sum(); mom60 = RW.shift(1).rolling(60, min_periods=40).sum(); vol20 = RW.shift(1).rolling(20, min_periods=15).std()
        P = P[(P.date.dt.year == y) & P[col] & (P.ind >= 0) & np.isfinite(P.logmv)].copy()
        for nm, M in (("mom20", mom20), ("mom60", mom60), ("vol20", vol20)):
            P = P.join(M.stack().rename(nm).astype("float32"), on=["date","instrument"])
        del RW, mom20, mom60, vol20
        P["ladv"] = np.log(P.adv20_yuan.clip(lower=1e4)); P = P.dropna(subset=["mom20","mom60","vol20","ret"])
        P = P[~P.instrument.isin(EXCL)].sort_values("date")
        fcols = [c for c in ft.columns if c in ("f1","cfacc","drnoa")]
        F = ft.rename(columns={"ts_code":"instrument"}).sort_values("avail")
        P = pd.merge_asof(P, F[["instrument","avail","end_date"]+fcols], left_on="date", right_on="avail", by="instrument", direction="backward")
        if leaf == "sue_resid":  # ≤60 sessions (~90 calendar days) after availability
            P.loc[(P.date - P.avail).dt.days > 90, "f1"] = np.nan
        for d, g in P.groupby("date", sort=True):
            if len(g) < 100: continue
            D = pd.get_dummies(g.ind).to_numpy(float); S = g[["logmv","mom20","mom60","vol20","ladv"]].to_numpy(float); S = (S-S.mean(0))/S.std(0)
            X = np.column_stack([D, S])
            eps = ols_resid(g.ret.to_numpy(float).clip(-.21, .31), np.column_stack([D, S[:, :1]]))
            qd = np.quantile(eps, 0.05)
            for i_, e_ in zip(g.instrument.values, eps): tail[i_].append(e_ < qd)
            GATE.append(pd.DataFrame({"date": d, "instrument": g.instrument.values, "gate": np.array([0 if any(tail[i_]) else 1 for i_ in g.instrument.values], dtype="int8")}))
            ok = g[fcols].notna().all(1).to_numpy()
            if ok.sum() < 50: continue
            gg = g[ok]
            if leaf == "sue_resid": raw = gg.f1.to_numpy(float)
            else: raw = (-gg.cfacc).rank(pct=True).to_numpy() + gg.drnoa.rank(pct=True).to_numpy()
            Xo = X[ok]; r1 = ols_resid(raw, Xo)
            a, dom = dom_rank(r1, gg.logmv.to_numpy(float))
            a = ols_resid(a, np.column_stack([D[ok], S[ok][:, :1]])); a, _ = dom_rank(a, gg.logmv.to_numpy(float))
            ALPHA.append(pd.DataFrame({"date": d, "instrument": gg.instrument.values, "alpha": a.astype("float32"), "size_domain": dom.astype("int8"), "ind": gg.ind.values, "raw": raw.astype("float32")}))
        print(leaf, uni, y, f"rss={rss():.0f}", flush=True); del P; gc.collect()
    return pd.concat(ALPHA), pd.concat(GATE)

def weights(A, gate, uni, start, end):
    A = A[(A.date >= start) & (A.date <= end)].merge(gate, on=["date","instrument"], how="left"); A["gate"] = A.gate.fillna(1)
    days = sorted(A.date.unique()); rows = []; cur = None
    for k, d in enumerate(days):
        if k % REBAL == 0:
            g = A[(A.date == d) & (A.gate == 1)].sort_values("alpha", ascending=False); pk, iw = [], {}
            for i, ind in zip(g.instrument, g.ind):
                if len(pk) >= MAX_N: break
                if iw.get(ind, 0)+NAME_W > IND_CAP[uni]+1e-12: continue
                pk.append(i); iw[ind] = iw.get(ind, 0)+NAME_W
            cur = [(i, NAME_W) for i in pk] + [(BAL, 1-NAME_W*len(pk))]
        rows += [(d, i, w) for i, w in cur]
    return pd.DataFrame(rows, columns=["date","instrument","target_weight"])

_RET = {}
def rets(years):
    k = tuple(years)
    if k not in _RET:
        X = pd.concat([pd.read_parquet(PC/f"cs_panel_{y}.parquet", columns=["date","instrument","ret","ret_on"]) for y in years])
        on = X.pivot_table(index="date", columns="instrument", values="ret_on"); rr = X.pivot_table(index="date", columns="instrument", values="ret")
        e = pd.read_parquet(R/"data/v2/etf/etf_daily_adj.parquet", columns=["trade_date","open_hfq","close_hfq"], filters=[("ts_code","==",BAL)])
        e.index = pd.to_datetime(e.trade_date, format="%Y%m%d"); e = e.sort_index()
        rr[BAL] = e.close_hfq.pct_change().reindex(rr.index); on[BAL] = (e.open_hfq/e.close_hfq.shift(1)-1).reindex(on.index)
        _RET.clear(); _RET[k] = (rr.fillna(0).astype("float32"), on.fillna(0).astype("float32"))
    return _RET[k]

def book_ret(W, start, end):
    rr, on = rets(range(int(start[:4]), int(end[:4])+1))
    Pw = W.pivot_table(index="date", columns="instrument", values="target_weight", aggfunc="sum").fillna(0); Pw.index = pd.to_datetime(Pw.index)
    Pw = Pw.reindex(rr.index[(rr.index >= start) & (rr.index <= end)]).ffill().fillna(0)
    cols = Pw.columns; r_ = rr.reindex(columns=cols).fillna(0).loc[Pw.index]; o_ = on.reindex(columns=cols).fillna(0).loc[Pw.index]
    intra = (1+r_)/(1+o_)-1; H = Pw.shift(1).fillna(0)
    r = (1+(H.shift(1).fillna(0)*o_).sum(1))*(1+(H*intra).sum(1))-1 - COST*H.diff().abs().sum(1).fillna(H.abs().sum(1))
    return r.iloc[2:], float(H.diff().abs().sum(1).iloc[2:].mean()/2)

def topn(W, N):
    out = []
    for d, g in W.groupby("date"):
        e = g[g.instrument == BAL]; s = g[g.instrument != BAL]
        if len(s): k = s.head(N).copy(); k["target_weight"] *= s.target_weight.sum()/k.target_weight.sum(); out += [e, k]
        else: out.append(e)
    return pd.concat(out)

def met(r, b):
    nav = (1+r).cumprod(); n = len(r); mdd = float((nav/nav.cummax()-1).min())
    bb = b.reindex(r.index).fillna(0); beta = float(np.cov(r, bb)[0,1]/bb.var()); res = r-beta*bb
    return dict(cagr244=float(nav.iloc[-1]**(244/n)-1), cagr252=float(nav.iloc[-1]**(252/n)-1), mdd=mdd, sharpe244=float(r.mean()/r.std()*np.sqrt(244)),
                bench_cagr244=float((1+bb).prod()**(244/n)-1), excess_ann244=float((r-bb).mean()*244), resid_alpha244=float(res.mean()*244), resid_alpha252=float(res.mean()*252), beta=beta, n=n)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--leaf", required=True, choices=["cfacc_rnoa","sue_resid"]); a = ap.parse_args()
    out = R/f"output/ai_factory/leaf{'19' if a.leaf=='cfacc_rnoa' else '20'}_{a.leaf}"; out.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S"); ft = fund_table(a.leaf); print("fund rows", len(ft), flush=True)
    e = pd.read_parquet(R/"data/v2/etf/etf_daily_adj.parquet", columns=["trade_date","close_hfq"], filters=[("ts_code","==",BAL)]); e.index = pd.to_datetime(e.trade_date, format="%Y%m%d"); bench = e.close_hfq.sort_index().pct_change(); summ = {"leaf": a.leaf, "stamp": stamp, "et": (datetime.now()-timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S"), "live": False, "promotion_approved": False, "res": {}}
    capw = pd.read_parquet(R/"output/strategy_hiliq/legs/g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet", columns=["date","instrument","target_weight"]); capw = capw[capw.target_weight > 0]; capw["date"] = pd.to_datetime(capw.date)
    for uni in ("HILIQ", "FULLA"):
        A, gate = build(a.leaf, uni, ft); A.to_parquet(out/f"alpha_{uni}_{stamp}.parquet", index=False); gate.to_parquet(out/f"gate_{uni}_{stamp}.parquet", index=False)
        cov = A.groupby("date").size(); summ["res"][uni] = {"coverage": dict(median=float(cov.median()), p10=float(cov.quantile(.1)), days=int(len(cov)))}
        for wn, (s, e) in WIN.items():
            W = weights(A, gate, uni, s, e); W.to_parquet(out/f"eval_weights_{uni}_{wn}_{stamp}.parquet", index=False)
            ent = {}
            for tier, N in (("full20", 20), ("60w", 6), ("100w", 10)):
                Wt = W if N == 20 else topn(W, N); r, to = book_ret(Wt, s, e); ent[tier] = dict(met(r, bench), turnover_daily=to)
                if wn == "x2" and uni == "HILIQ" and N != 20:
                    ct = topn(capw[(capw.date >= s) & (capw.date <= e)], N); rc, _ = book_ret(ct, s, e)
                    mix = pd.concat([ct.assign(target_weight=ct.target_weight*.8), Wt.assign(target_weight=Wt.target_weight*.2)]).groupby(["date","instrument"], as_index=False).target_weight.sum()
                    rm, _ = book_ret(mix, s, e); ix = rc.index.intersection(rm.index)
                    ent[tier]["cap"] = met(rc[ix], bench); ent[tier]["cap80_leaf20"] = met(rm[ix], bench)
                    rl = r.reindex(ix).fillna(0); bb = bench.reindex(ix).fillna(0)
                    def db(x): be = np.cov(x, bb)[0,1]/bb.var(); return x-be*bb
                    ent[tier]["rho_resid_vs_cap"] = float(np.corrcoef(db(rl), db(rc[ix]))[0,1])
            summ["res"][uni][wn] = ent
            if wn == "x2":
                tag = f"{a.leaf}" if uni == "HILIQ" else f"{a.leaf}_fulla"
                W.to_parquet(R/f"output/ai_factory/g1g5_{tag}_daily_weights_{stamp}.parquet", index=False)
                (R/f"output/ai_factory/g1g5_{tag}_run_meta_{stamp}.json").write_text(json.dumps(dict(mechanism_tag=f"g1g5_ashare_{a.leaf}_v1", universe=uni, primary_product="base_alpha_vector", live=False, promotion_approved=False, stamp=stamp), ensure_ascii=False))
            print(uni, wn, json.dumps({t: {k: round(v, 4) for k, v in ent[t].items() if isinstance(v, float)} for t in ent}), flush=True)
        del A, gate; gc.collect()
    summ["peak_rss_mb"] = rss(); (out/f"summary_{stamp}.json").write_text(json.dumps(summ, ensure_ascii=False, indent=1, default=float)); print("DONE", rss())
if __name__ == "__main__": main()
