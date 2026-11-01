#!/usr/bin/env python3
"""Leaf21 biz_climate (prereg docs/v2/AI_G1G5_BIZ_CLIMATE_WHO_PAYS_PREREG_ZH.md, FROZEN). ΔContractLiab(+adv_receipts)/avgTA + ΔlogInvTurnover,
within-SW-L1 z, financials excluded; pool-internal resid (ind+logmv+mom20/60+vol20+logADV), size-domain calibrate, slow α 20d, separate fast gate.
Chunked: --stage build --uni U  (per-year alpha/gate parquet) ; --stage eval (weights, window perf, canonical X2 weights).
live=false; promotion=false; no Book-Smoke; run under research/run_rss_guard.sh (1.5GB)."""
import argparse, json, sys, gc, resource, numpy as np, pandas as pd
from pathlib import Path
from datetime import datetime
from collections import deque, defaultdict
R = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(R))
import research.g1g5_fund_resid_alpha as FE
OUT = R/"output/ai_factory/leaf21_biz_climate"; OUT.mkdir(exist_ok=True); FP = R/"data/v2/financials_pit"; PC = FE.PC
rss = lambda: resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
IND_NAMES = pd.read_csv(PC/"ind_names.csv").iloc[:, 0].tolist(); FIN = {i for i, n in enumerate(IND_NAMES) if n in ("银行", "非银金融")}

def fund_table():
    bs = pd.read_parquet(FP/"balancesheet_pit_tushare.parquet", columns=["ts_code","end_date","available_at","report_type","contract_liab","adv_receipts","inventories"])
    bs = bs[bs.report_type.astype(str).str.replace(".0", "", regex=False) == "1"].copy()
    bs["cl"] = bs.contract_liab.fillna(0) + bs.adv_receipts.fillna(0); bs.loc[bs.contract_liab.isna() & bs.adv_receipts.isna(), "cl"] = np.nan
    b = FE.first_version(bs, ["cl", "inventories"])
    ta = FE.first_version(pd.read_parquet(FP/"bs_cf_pit_tushare.parquet", columns=["ts_code","end_date","available_at","report_type","total_assets"]).query("report_type=='1'"), ["total_assets"])
    fi = pd.read_parquet(FP/"financials_pit_tushare.parquet", columns=["ts_code","end_date","available_at","report_type","revenue","grossprofit_margin"]).query("report_type=='1'")
    fi["cogs"] = fi.revenue*(1-fi.grossprofit_margin/100); fi = FE.first_version(fi, ["cogs"])
    d = b.merge(ta, on=["ts_code","end_date"], how="outer", suffixes=("", "_t")).merge(fi, on=["ts_code","end_date"], how="outer", suffixes=("", "_f"))
    d["end_date"] = pd.to_datetime(d.end_date); d = d[d.ts_code.str[:1].isin(list("036"))]
    d = FE.single_q(d, "cogs"); d = d.sort_values(["ts_code","end_date"]); g = d.groupby("ts_code")
    lag4ok = g.end_date.shift(4) == d.end_date - pd.DateOffset(years=1)
    contig = g.end_date.shift(3) == (d.end_date - pd.offsets.QuarterEnd(3))
    d["cogs_ttm"] = g["cogs_q"].transform(lambda s: s.rolling(4, min_periods=4).sum()).where(contig)
    ta4 = g.total_assets.shift(4).where(lag4ok); inv4 = g.inventories.shift(4).where(lag4ok); cl4 = g.cl.shift(4).where(lag4ok)
    d["dcl"] = (d.cl - cl4)/((d.total_assets + ta4)/2)
    turn = d.cogs_ttm/((d.inventories + inv4)/2); turn = turn.where((d.inventories > 0) & (inv4 > 0) & (turn > 0)); d["turn"] = turn
    d["dturn"] = np.log(d.turn/d.groupby("ts_code").turn.shift(4).where(lag4ok))
    # availability: latest of all fields actually used (own + lagged rows are earlier by construction)
    av = d[["avail","avail_t","avail_f"]].max(1); d["avail"] = av
    d = d.replace([np.inf, -np.inf], np.nan)
    d.loc[d.dcl.abs() > 2, "dcl"] = np.nan; d.loc[d.dturn.abs() > 3, "dturn"] = np.nan
    d = d.dropna(subset=["avail"]); d = d[d.dcl.notna() | d.dturn.notna()]
    return d[["ts_code","end_date","avail","dcl","dturn"]]

def zin(v, ind):
    out = np.zeros(len(v)); 
    for k in np.unique(ind):
        i = np.where((ind == k) & np.isfinite(v))[0]
        if len(i) < 5: continue
        x = v[i]; lo, hi = np.quantile(x, [.01, .99]); x = x.clip(lo, hi); s = x.std()
        if s > 0: out[i] = (x-x.mean())/s
    return out

def build(uni):
    col = FE.UCOL[uni]; ft = fund_table().rename(columns={"ts_code": "instrument"}).sort_values("avail"); print("fund rows", len(ft), f"rss={rss():.0f}", flush=True)
    tail = defaultdict(lambda: deque(maxlen=3)); cov = []
    for y in range(2018, 2027):
        P = pd.concat([pd.read_parquet(PC/f"cs_panel_{yy}.parquet", columns=["date","instrument","ret","logmv","ind","adv20_yuan",col]) for yy in (y-1, y) if (PC/f"cs_panel_{yy}.parquet").exists()])
        RW = P.pivot_table(index="date", columns="instrument", values="ret").sort_index().astype("float32")
        mom20 = RW.shift(1).rolling(20, min_periods=15).sum(); mom60 = RW.shift(1).rolling(60, min_periods=40).sum(); vol20 = RW.shift(1).rolling(20, min_periods=15).std()
        P = P[(P.date.dt.year == y) & P[col] & (P.ind >= 0) & ~P.ind.isin(FIN) & np.isfinite(P.logmv)].copy()
        for nm, M in (("mom20", mom20), ("mom60", mom60), ("vol20", vol20)): P = P.join(M.stack().rename(nm).astype("float32"), on=["date","instrument"])
        del RW, mom20, mom60, vol20; gc.collect()
        P["ladv"] = np.log(P.adv20_yuan.clip(lower=1e4)); P = P.dropna(subset=["mom20","mom60","vol20","ret"]); P = P[~P.instrument.isin(FE.EXCL)].sort_values("date")
        P = pd.merge_asof(P, ft[["instrument","avail","dcl","dturn"]], left_on="date", right_on="avail", by="instrument", direction="backward")
        P.loc[(P.date - P.avail).dt.days > 200, ["dcl","dturn"]] = np.nan  # stale (>~2 quarters w/o new report)
        AL, GL = [], []
        for d, g in P.groupby("date", sort=True):
            if len(g) < 100: continue
            ind = g.ind.to_numpy(); D = (ind[:, None] == np.unique(ind)[None, :]).astype(float)
            S = g[["logmv","mom20","mom60","vol20","ladv"]].to_numpy(float); S = (S-S.mean(0))/S.std(0); X = np.column_stack([D, S])
            eps = FE.ols_resid(g.ret.to_numpy(float).clip(-.21, .31), np.column_stack([D, S[:, :1]])); qd = np.quantile(eps, .05)
            ins = g.instrument.to_numpy()
            for i_, e_ in zip(ins, eps): tail[i_].append(e_ < qd)
            GL.append(pd.DataFrame({"date": d, "instrument": ins, "gate": np.array([0 if any(tail[i_]) else 1 for i_ in ins], dtype="int8")}))
            zc = zin(g.dcl.to_numpy(float), ind); zt = zin(g.dturn.to_numpy(float), ind)
            hc, ht = np.isfinite(g.dcl.to_numpy(float)), np.isfinite(g.dturn.to_numpy(float)); ok = hc | ht
            if ok.sum() < 50: cov.append((d, int(ok.sum()))); continue
            raw = (zc + zt)[ok]; r1 = FE.ols_resid(raw, X[ok]); mv = g.logmv.to_numpy(float)[ok]
            a, dom = FE.dom_rank(r1, mv); a = FE.ols_resid(a, np.column_stack([D[ok], S[ok][:, :1]])); a, _ = FE.dom_rank(a, mv)
            AL.append(pd.DataFrame({"date": d, "instrument": ins[ok], "alpha": a.astype("float32"), "size_domain": dom.astype("int8"), "ind": ind[ok], "raw": raw.astype("float32")})); cov.append((d, int(ok.sum())))
        if AL: pd.concat(AL).to_parquet(OUT/f"alpha_{uni}_{y}.parquet", index=False)
        pd.concat(GL).to_parquet(OUT/f"gate_{uni}_{y}.parquet", index=False)
        print(uni, y, "days", len(AL), f"rss={rss():.0f}", flush=True); del P, AL, GL; gc.collect()
    c = pd.DataFrame(cov, columns=["date","n"]); c.to_parquet(OUT/f"coverage_{uni}.parquet", index=False)
    json.dump(dict(median=float(c.n.median()), p10=float(c.n.quantile(.1)), days=len(c), peak_rss_mb=rss()), open(OUT/f"build_meta_{uni}.json", "w"))

def load(kind, uni, s, e, rd=None):
    fs = [OUT/f"{kind}_{uni}_{y}.parquet" for y in range(int(s[:4]), int(e[:4])+1) if (OUT/f"{kind}_{uni}_{y}.parquet").exists()]
    cols = ["date","instrument","alpha","ind"] if kind == "alpha" else ["date","instrument","gate"]
    filt = None if rd is None else [("date", "in", [pd.Timestamp(d).to_pydatetime() for d in rd])]
    x = pd.concat([pd.read_parquet(f, columns=cols, filters=filt) for f in fs])
    x["date"] = pd.to_datetime(x.date); return x[(x.date >= s) & (x.date <= e)]

def evaluate():
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S"); summ = dict(leaf="biz_climate", stamp=stamp, live=False, promotion_approved=False, res={})
    for uni in ("HILIQ", "FULLA"):
        bm = json.load(open(OUT/f"build_meta_{uni}.json")); c = pd.read_parquet(OUT/f"coverage_{uni}.parquet"); c["date"] = pd.to_datetime(c.date)
        summ["res"][uni] = {"coverage_all_days": bm}
        for wn, (s, e) in FE.WIN.items():
            days = sorted(pd.concat([pd.read_parquet(f, columns=["date"]) for f in (OUT/f"alpha_{uni}_{y}.parquet" for y in range(int(s[:4]), int(e[:4])+1)) if f.exists()]).date.pipe(pd.to_datetime).loc[lambda x: (x >= s) & (x <= e)].unique())
            rd = days[::FE.REBAL]  # identical rebalance schedule to FE.weights (k % REBAL == 0 over alpha days)
            A = load("alpha", uni, s, e, rd); G = load("gate", uni, s, e, rd)
            _rb = FE.REBAL; FE.REBAL = 1; Wr = FE.weights(A, G, uni, s, e); FE.REBAL = _rb  # picks on rebalance days only
            Wr["date"] = pd.to_datetime(Wr.date); grp = {d: g for d, g in Wr.groupby("date")}; rows = []; cur = None
            for d in days:
                if d in grp: cur = grp[d]
                rows.append(cur.assign(date=d))
            W = pd.concat(rows, ignore_index=True); W.to_parquet(OUT/f"eval_weights_{uni}_{wn}_{stamp}.parquet", index=False)
            cr = c[c.date.isin(rd)].n
            summ["res"][uni][wn] = dict(coverage_rebal_median=float(cr.median()), coverage_rebal_p10=float(cr.quantile(.1)), n_alpha_days=len(days))
            if wn == "x2":
                tag = "biz_climate" if uni == "HILIQ" else "biz_climate_fulla"
                W.to_parquet(R/f"output/ai_factory/g1g5_{tag}_daily_weights_{stamp}.parquet", index=False)
                (R/f"output/ai_factory/g1g5_{tag}_run_meta_{stamp}.json").write_text(json.dumps(dict(mechanism_tag="g1g5_ashare_biz_climate_v1", universe=uni, primary_product="base_alpha_vector", live=False, promotion_approved=False, stamp=stamp), ensure_ascii=False))
            print(uni, wn, summ["res"][uni][wn], f"rss={rss():.0f}", flush=True); del A, G, W; gc.collect()
    summ["peak_rss_mb_eval"] = rss(); (OUT/f"summary_{stamp}.json").write_text(json.dumps(summ, ensure_ascii=False, indent=1)); print("STAMP", stamp)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--stage", required=True); ap.add_argument("--uni"); a = ap.parse_args()
    build(a.uni) if a.stage == "build" else evaluate()
