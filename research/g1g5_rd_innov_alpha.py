#!/usr/bin/env python3
"""Leaf22 rd_innov (prereg docs/v2/AI_G1G5_RD_INNOV_WHO_PAYS_PREREG_ZH.md, FROZEN 2026-10-18 00:51:07 ET).
α_raw = z(RDA) + z(ΔRDS) − z(CAPSH) within SW L1 (financials excluded); pool resid on ind+logmv+mom20/60+vol20+logADV+leaf19 α;
size-domain rank; ind+size resid; slow α 20d; separate fast gate. X2 ONLY (sealed window not built/evaluated unless X2 gates pass).
--stage fund | --stage build --uni U | --stage eval. live=false; no Book-Smoke; run under research/run_rss_guard.sh (1.5GB)."""
import argparse, json, sys, gc, glob, resource, numpy as np, pandas as pd
from pathlib import Path
from datetime import datetime
from collections import deque, defaultdict
R = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(R))
import research.g1g5_fund_resid_alpha as FE
OUT = R/"output/ai_factory/leaf22_rd_innov"; OUT.mkdir(exist_ok=True); FP = R/"data/v2/financials_pit"; PC = FE.PC
X2S, X2E = FE.WIN["x2"]; WARM = "2024-01-01"
rss = lambda: resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
IND_NAMES = pd.read_csv(PC/"ind_names.csv").iloc[:, 0].tolist(); FIN = {i for i, n in enumerate(IND_NAMES) if n in ("银行", "非银金融")}
L19 = {"HILIQ": R/"output/ai_factory/leaf19_cfacc_rnoa/alpha_HILIQ_20261014_213132.parquet", "FULLA": R/"output/ai_factory/leaf19_cfacc_rnoa/alpha_FULLA_20261014_213132.parquet"}

def fund():
    rows = []
    for f in sorted(glob.glob(str(R/"data/v2/tushare_raw/income/*.parquet"))):
        if Path(f).name[:1] not in "036": continue
        x = pd.read_parquet(f, columns=["ts_code","ann_date","end_date","report_type","rd_exp","revenue"])
        x = x[x.report_type.astype(str).str.replace(".0", "", regex=False) == "1"]
        x = x[pd.to_datetime(x.end_date.astype(str), errors="coerce") >= "2021-01-01"]
        if len(x): rows.append(x)
    inc = pd.concat(rows); inc["end_date"] = pd.to_datetime(inc.end_date.astype(str)); inc["ann"] = pd.to_datetime(inc.ann_date.astype(str), errors="coerce")
    inc = inc.dropna(subset=["ann"]).sort_values(["ts_code","end_date","ann", "rd_exp"], na_position="last")
    first_ann = inc.groupby(["ts_code","end_date"]).ann.transform("min"); inc = inc[inc.ann == first_ann]
    inc = inc.groupby(["ts_code","end_date"], as_index=False).agg(rd_exp=("rd_exp","max"), revenue=("revenue","max"), ann=("ann","first"))
    inc["avail"] = inc.ann + pd.Timedelta(days=1)  # ann_date 18:00 → next session
    ta = FE.first_version(pd.read_parquet(FP/"bs_cf_pit_tushare.parquet", columns=["ts_code","end_date","available_at","report_type","total_assets"]).query("report_type=='1'"), ["total_assets"])
    bs = pd.read_parquet(FP/"balancesheet_pit_tushare.parquet", columns=["ts_code","end_date","available_at","report_type","r_and_d"]); bs = bs[bs.report_type.astype(str).str.replace(".0", "", regex=False) == "1"]
    bs = bs.dropna(subset=["available_at"]).copy(); bs["avail"] = pd.to_datetime(bs.available_at.astype(str).str[:10]) + pd.Timedelta(days=1)
    dev = bs.sort_values("avail").drop_duplicates(["ts_code","end_date"], keep="first")[["ts_code","end_date","avail","r_and_d"]]
    for t in (ta, dev): t["end_date"] = pd.to_datetime(t.end_date)
    d = inc.merge(ta, on=["ts_code","end_date"], how="left", suffixes=("", "_t")).merge(dev, on=["ts_code","end_date"], how="left", suffixes=("", "_d"))
    d = FE.single_q(d, "rd_exp"); d = FE.single_q(d, "revenue"); d = d.sort_values(["ts_code","end_date"]); g = d.groupby("ts_code")
    contig = g.end_date.shift(3) == (d.end_date - pd.offsets.QuarterEnd(3)); lag4 = g.end_date.shift(4) == d.end_date - pd.DateOffset(years=1)
    d["rd_ttm"] = g["rd_exp_q"].transform(lambda s: s.rolling(4, min_periods=4).sum()).where(contig)
    d["rev_ttm"] = g["revenue_q"].transform(lambda s: s.rolling(4, min_periods=4).sum()).where(contig)
    ta4 = g.total_assets.shift(4).where(lag4); d["rda"] = d.rd_ttm/((d.total_assets + ta4)/2)
    rds = (d.rd_ttm/d.rev_ttm).where(d.rev_ttm > 0); d["drds"] = rds - rds.groupby(d.ts_code).shift(4).where(lag4)
    dv = d.r_and_d.fillna(0); ddev = (dv - dv.groupby(d.ts_code).shift(4).where(lag4)).clip(lower=0); ddev = ddev.fillna(0)
    d["capsh"] = (ddev/(d.rd_ttm + ddev)).where(d.rd_ttm.notna())
    d.loc[d.rd_ttm < 0, ["rda","drds","capsh"]] = np.nan; d.loc[d.rda.abs() > 1, "rda"] = np.nan; d.loc[d.drds.abs() > 1, "drds"] = np.nan
    d["capsh"] = d.capsh.clip(0, 1)
    d["avail"] = d[["avail","avail_t","avail_d"]].max(1)  # latest of fields used (lagged rows are earlier by construction)
    d = d.replace([np.inf, -np.inf], np.nan).dropna(subset=["avail","rda"])
    d = d[["ts_code","end_date","avail","rda","drds","capsh"]]; d.to_parquet(OUT/"fund_table.parquet", index=False)
    print("fund rows", len(d), "by year", d.end_date.dt.year.value_counts().sort_index().to_dict(), "capsh>0", float((d.capsh > 0).mean()), f"rss={rss():.0f}", flush=True)

def zin(v, ind):
    out = np.zeros(len(v))
    for k in np.unique(ind):
        i = np.where((ind == k) & np.isfinite(v))[0]
        if len(i) < 5: continue
        x = v[i]; lo, hi = np.quantile(x, [.01, .99]); x = x.clip(lo, hi); s = x.std()
        if s > 0: out[i] = (x-x.mean())/s
    return out

def build(uni):
    col = FE.UCOL[uni]; ft = pd.read_parquet(OUT/"fund_table.parquet").rename(columns={"ts_code": "instrument"}).sort_values("avail")
    a19 = pd.read_parquet(L19[uni], columns=["date","instrument","alpha"], filters=[("date", ">=", pd.Timestamp(X2S).to_pydatetime())]).rename(columns={"alpha": "a19"}); a19["date"] = pd.to_datetime(a19.date)
    tail = defaultdict(lambda: deque(maxlen=3)); cov = []
    for y in (2024, 2025, 2026):
        lo = pd.Timestamp(WARM) if y == 2024 else pd.Timestamp(f"{y-1}-09-01")
        P = pd.concat([pd.read_parquet(PC/f"cs_panel_{yy}.parquet", columns=["date","instrument","ret","logmv","ind","adv20_yuan",col], filters=[("date", ">=", lo.to_pydatetime())]) for yy in sorted({lo.year, y})])
        RW = P.pivot_table(index="date", columns="instrument", values="ret").sort_index().astype("float32")
        mom20 = RW.shift(1).rolling(20, min_periods=15).sum(); mom60 = RW.shift(1).rolling(60, min_periods=40).sum(); vol20 = RW.shift(1).rolling(20, min_periods=15).std()
        gstart = pd.Timestamp(X2S) - pd.Timedelta(days=10) if y == 2024 else pd.Timestamp(f"{y}-01-01")
        P = P[(P.date >= gstart) & (P.date.dt.year == y) & (P.date <= X2E) & P[col] & (P.ind >= 0) & ~P.ind.isin(FIN) & np.isfinite(P.logmv)].copy()
        for nm, M in (("mom20", mom20), ("mom60", mom60), ("vol20", vol20)): P = P.join(M.stack().rename(nm).astype("float32"), on=["date","instrument"])
        del RW, mom20, mom60, vol20; gc.collect()
        P["ladv"] = np.log(P.adv20_yuan.clip(lower=1e4)); P = P.dropna(subset=["mom20","mom60","vol20","ret"]); P = P[~P.instrument.isin(FE.EXCL)].sort_values("date")
        P = pd.merge_asof(P, ft[["instrument","avail","rda","drds","capsh"]], left_on="date", right_on="avail", by="instrument", direction="backward")
        P.loc[(P.date - P.avail).dt.days > 200, ["rda","drds","capsh"]] = np.nan
        P = P.merge(a19, on=["date","instrument"], how="left"); P["a19"] = P.a19.fillna(0.0)
        AL, GL = [], []
        for d, g in P.groupby("date", sort=True):
            if len(g) < 100: continue
            ind = g.ind.to_numpy(); D = (ind[:, None] == np.unique(ind)[None, :]).astype(float)
            S = g[["logmv","mom20","mom60","vol20","ladv"]].to_numpy(float); S = (S-S.mean(0))/S.std(0)
            eps = FE.ols_resid(g.ret.to_numpy(float).clip(-.21, .31), np.column_stack([D, S[:, :1]])); qd = np.quantile(eps, .05)
            ins = g.instrument.to_numpy()
            for i_, e_ in zip(ins, eps): tail[i_].append(e_ < qd)
            if d < pd.Timestamp(X2S): continue  # warm-up only (gate tail); no output before X2
            GL.append(pd.DataFrame({"date": d, "instrument": ins, "gate": np.array([0 if any(tail[i_]) else 1 for i_ in ins], dtype="int8")}))
            rda = g.rda.to_numpy(float); ok = np.isfinite(rda)
            if ok.sum() < 50: cov.append((d, int(ok.sum()))); continue
            z = zin(rda, ind) + zin(g.drds.to_numpy(float), ind) - zin(g.capsh.to_numpy(float), ind)
            a19v = g.a19.to_numpy(float); X = np.column_stack([D, S, (a19v - a19v.mean())])
            raw = z[ok]; r1 = FE.ols_resid(raw, X[ok]); mv = g.logmv.to_numpy(float)[ok]
            a, dom = FE.dom_rank(r1, mv); a = FE.ols_resid(a, np.column_stack([D[ok], S[ok][:, :1]])); a, _ = FE.dom_rank(a, mv)
            AL.append(pd.DataFrame({"date": d, "instrument": ins[ok], "alpha": a.astype("float32"), "size_domain": dom.astype("int8"), "ind": ind[ok], "raw": raw.astype("float32")})); cov.append((d, int(ok.sum())))
        if AL: pd.concat(AL).to_parquet(OUT/f"alpha_{uni}_{y}.parquet", index=False)
        if GL: pd.concat(GL).to_parquet(OUT/f"gate_{uni}_{y}.parquet", index=False)
        print(uni, y, "days", len(AL), f"rss={rss():.0f}", flush=True); del P, AL, GL; gc.collect()
    c = pd.DataFrame(cov, columns=["date","n"]); c.to_parquet(OUT/f"coverage_{uni}.parquet", index=False)
    json.dump(dict(median=float(c.n.median()), p10=float(c.n.quantile(.1)), days=len(c), peak_rss_mb=rss()), open(OUT/f"build_meta_{uni}.json", "w"))

def load(kind, uni, s, e, rd):
    fs = [OUT/f"{kind}_{uni}_{y}.parquet" for y in range(int(s[:4]), int(e[:4])+1) if (OUT/f"{kind}_{uni}_{y}.parquet").exists()]
    cols = ["date","instrument","alpha","ind"] if kind == "alpha" else ["date","instrument","gate"]
    x = pd.concat([pd.read_parquet(f, columns=cols, filters=[("date", "in", [pd.Timestamp(d).to_pydatetime() for d in rd])]) for f in fs])
    x["date"] = pd.to_datetime(x.date); return x[(x.date >= s) & (x.date <= e)]

def evaluate():
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S"); summ = dict(leaf="rd_innov", stamp=stamp, live=False, promotion_approved=False, sealed_read=False, res={})
    s, e = X2S, X2E
    for uni in ("HILIQ", "FULLA"):
        bm = json.load(open(OUT/f"build_meta_{uni}.json")); c = pd.read_parquet(OUT/f"coverage_{uni}.parquet"); c["date"] = pd.to_datetime(c.date)
        days = sorted(pd.concat([pd.read_parquet(f, columns=["date"]) for f in (OUT/f"alpha_{uni}_{y}.parquet" for y in (2024, 2025, 2026)) if f.exists()]).date.pipe(pd.to_datetime).loc[lambda x: (x >= s) & (x <= e)].unique())
        rd = days[::FE.REBAL]; A = load("alpha", uni, s, e, rd); G = load("gate", uni, s, e, rd)
        _rb = FE.REBAL; FE.REBAL = 1; Wr = FE.weights(A, G, uni, s, e); FE.REBAL = _rb
        Wr["date"] = pd.to_datetime(Wr.date); grp = {d: g for d, g in Wr.groupby("date")}; rows = []; cur = None
        for d in days:
            if d in grp: cur = grp[d]
            rows.append(cur.assign(date=d))
        W = pd.concat(rows, ignore_index=True); W.to_parquet(OUT/f"eval_weights_{uni}_x2_{stamp}.parquet", index=False)
        cr = c[c.date.isin(rd)].n
        summ["res"][uni] = dict(coverage_all_days=bm, coverage_rebal_median=float(cr.median()), coverage_rebal_p10=float(cr.quantile(.1)), n_alpha_days=len(days))
        tag = "rd_innov" if uni == "HILIQ" else "rd_innov_fulla"
        W.to_parquet(R/f"output/ai_factory/g1g5_{tag}_daily_weights_{stamp}.parquet", index=False)
        (R/f"output/ai_factory/g1g5_{tag}_run_meta_{stamp}.json").write_text(json.dumps(dict(mechanism_tag="g1g5_ashare_rd_innov_v1", universe=uni, primary_product="base_alpha_vector", live=False, promotion_approved=False, stamp=stamp, window="x2"), ensure_ascii=False))
        print(uni, summ["res"][uni], f"rss={rss():.0f}", flush=True); del A, G, W; gc.collect()
    summ["peak_rss_mb_eval"] = rss(); (OUT/f"summary_{stamp}.json").write_text(json.dumps(summ, ensure_ascii=False, indent=1)); print("STAMP", stamp)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--stage", required=True); ap.add_argument("--uni"); a = ap.parse_args()
    {"fund": fund, "build": lambda: build(a.uni), "eval": evaluate}[a.stage]()
