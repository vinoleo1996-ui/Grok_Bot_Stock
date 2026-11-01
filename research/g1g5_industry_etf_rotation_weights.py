#!/usr/bin/env python3
"""G1G5 industry ETF rotation leaf: redemption × residual-resilience divergence (research-grade).
Prereg docs/v2/AI_G1G5_INDUSTRY_ETF_ROTATION_WHO_PAYS_PREREG_ZH.md. promotion=false; live=false; no GP; no Book-Smoke.
"""
from __future__ import annotations
import glob, json, re, resource, sys
from datetime import datetime
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from quantlab.intel.debate_ledger import JsonlDebateLedger  # noqa
from research.ai_debate_memory_runner import _load_benchmark_closes  # noqa
from research.g1g5_wiring import COLUMN_CONTRACT_VERSION, HARD_GATE_VERSION  # noqa
from research.g1g5_expand_g6 import run_g6_lookahead_proof  # noqa
from research.g1g5_x2_panel_stitch import load_panel_features_x2, clear_caches  # noqa
from research.g1g5_low_turnover_weights import estimate_daily_turnover  # noqa

TAG = "g1g5_ashare_industry_etf_rotation_v1"
UNIVERSE_ID = "g1g5_sw_l1_rep_etf_pit"
BALLAST = "510300.SH"
W_ETF, TOPK, REB, AMT_MIN = 0.20, 3, 5, 20000.0
WS, WE = "2024-01-02", "2026-10-09"
WHO = ("行业ETF份额净赎回(资金流出)而行业去β残差仍为正的背离：赎回卖压被知情/配置买盘吸收，付钱的是机械赎回离场的对手盘；"
       "资金流入行业不入选，非单纯动量；非ADV分位、非两融、非北向、非个股资金流、非估值残差。")
CAP_ADV = ROOT / "output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet"
E2 = ROOT / "data/v2/etf"

def rss(): return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
def ymd(s): return pd.to_datetime(s.astype(str), format="%Y%m%d")

def run():
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S"); out = ROOT / "output/ai_factory"
    bench = _load_benchmark_closes("510300"); bench.index = pd.to_datetime(bench.index)
    calf = bench.index[bench.index >= "2023-01-01"]; cal = calf[(calf >= WS) & (calf <= WE)]
    mp = pd.read_parquet(E2 / "sw_l1_etf_map_pit_daily.parquet", columns=["sw_l1_code", "trade_date", "etf_ts_code", "amt20", "no_etf", "sw_l1_name"])
    mp = mp[(~mp.no_etf) & (mp.trade_date >= "20221001")].copy(); mp["d"] = ymd(mp.trade_date)
    etfs = sorted(set(mp.etf_ts_code.dropna()))
    px = pd.read_parquet(E2 / "etf_daily_adj.parquet", columns=["ts_code", "trade_date", "close_hfq"], filters=[("ts_code", "in", etfs)])
    px = px[px.trade_date >= "20221001"]; px["d"] = ymd(px.trade_date)
    P = px.pivot_table(index="d", columns="ts_code", values="close_hfq").reindex(calf)
    R = P.pct_change(fill_method=None); rb = bench.reindex(calf).pct_change()
    # industry-level residual using the PIT rep ETF of each day
    rep = mp.pivot_table(index="d", columns="sw_l1_code", values="etf_ts_code", aggfunc="first").reindex(calf)
    amt = mp.pivot_table(index="d", columns="sw_l1_code", values="amt20", aggfunc="first").reindex(calf)
    inds = list(rep.columns)
    ri = pd.DataFrame(index=calf, columns=inds, dtype=float)
    for c in inds:
        ri[c] = [R.at[d, e] if isinstance(e, str) and e in R.columns else np.nan for d, e in zip(calf, rep[c])]
    cov = ri.rolling(120, min_periods=60).cov(rb) if False else ri.apply(lambda s: s.rolling(120, min_periods=60).cov(rb))
    beta = cov.div(rb.rolling(120, min_periods=60).var(), axis=0)
    res = ri - beta.shift(1).mul(rb, axis=0)
    resid20 = res.rolling(20, min_periods=15).sum()
    # flows (PIT by available_at)
    fl = pd.read_parquet(E2 / "share_pit/ind_etf_share_flow_by_sw_l1.parquet", columns=["trade_date", "sw_l1_code", "flow_est_wan_yuan", "available_at"])
    fl = fl[fl.trade_date >= "20221001"]
    sh = pd.read_parquet(E2 / "share_pit/ind_etf_share_flow_pit.parquet", columns=["trade_date", "sw_l1_code", "share_wan", "unit_nav", "available_at"])
    sh = sh[sh.trade_date >= "20221001"]; sh["aum"] = sh.share_wan * sh.unit_nav
    aum = sh.groupby(["available_at", "sw_l1_code"]).aum.sum().reset_index()
    def asof_panel(df, val):
        df = df.copy(); df["k"] = df.available_at.dt.normalize()
        g = df.groupby(["k", "sw_l1_code"])[val].sum().unstack()
        return g.sort_index()
    Fd = asof_panel(fl, "flow_est_wan_yuan"); Ad = asof_panel(aum, "aum")
    # value known at end of day k (available_at date <= d) -> reindex with ffill on known date
    Fsum = Fd.reindex(Fd.index.union(calf)).fillna(0).rolling(20, min_periods=10).sum()  # 20 available-days sum
    Fsum = Fsum.reindex(calf, method="ffill")
    Aknown = Ad.reindex(Ad.index.union(calf)).ffill().reindex(calf)
    Fr = Fsum / Aknown.shift(20)
    # note: available_at 23:59 on day k => usable for signal at close of k only for next-day trading; signal(d-1) -> weight d
    rows, picks_log, prev = [], [], {BALLAST: 1.0}
    pos = {d: i for i, d in enumerate(calf)}
    for j, d in enumerate(cal):
        if j % REB == 0:
            s = calf[pos[d] - 1]
            fr, rz, am = Fr.loc[s].reindex(inds), resid20.loc[s], amt.loc[s]
            ok = [c for c in inds if np.isfinite(fr.get(c, np.nan)) and np.isfinite(rz.get(c, np.nan)) and am.get(c, 0) >= AMT_MIN]
            sel = []
            if len(ok) >= 3:
                f = fr[ok]; thr = f.quantile(1 / 3)
                cand = [c for c in ok if f[c] <= thr and f[c] < 0 and rz[c] > 0]
                sel = sorted(cand, key=lambda c: -rz[c])[:TOPK]
            w = {rep.at[d, c] if isinstance(rep.at[d, c], str) else rep.at[s, c]: W_ETF for c in sel}
            w = {k: v for k, v in w.items() if isinstance(k, str)}
            w[BALLAST] = 1 - sum(w.values()); prev = w
            picks_log.append(dict(signal=str(s.date()), sel=sel))
        for k, v in prev.items():
            rows.append((d.strftime("%Y-%m-%d"), k, v))
    W = pd.DataFrame(rows, columns=["date", "instrument", "target_weight"])
    W = W.groupby(["date", "instrument"], as_index=False).target_weight.sum()
    full = W.pivot(index="date", columns="instrument", values="target_weight").fillna(0.0).stack().rename("target_weight").reset_index()
    W = full
    ds = W.groupby("date").target_weight.sum(); assert ds.between(1 - 1e-9, 1 + 1e-9).all(); assert (W.target_weight >= 0).all()
    W["mechanism_tag"], W["who_pays_zh"], W["universe_id"], W["session"] = TAG, WHO, UNIVERSE_ID, W["date"]
    W["instrument_id"] = W.instrument.map(lambda x: x.split(".")[1].lower() + "." + x.split(".")[0]); W["weight"] = W.target_weight
    wpath = out / f"g1g5_industry_etf_rotation_daily_weights_{stamp}.parquet"; W.to_parquet(wpath, index=False)
    nb = W[(W.instrument != BALLAST) & (W.target_weight > 0)]
    # returns
    from research.g1g5_x2_panel_stitch import load_adj_close_x2
    from research.ai_debate_memory_runner import _load_benchmark_closes_hfq
    BENCH_HFQ = _load_benchmark_closes_hfq("510300"); BENCH_HFQ.index = pd.to_datetime(BENCH_HFQ.index)
    # self-check returns use hfq (2026-10-13 unify); signal layer unchanged
    def leaf_ret(wdf, etf_px=True):
        w = wdf.pivot_table(index="date", columns="instrument", values="target_weight", aggfunc="sum").fillna(0.0); w.index = pd.to_datetime(w.index)
        rr = {}
        for inst in w.columns:
            if inst == BALLAST: c = BENCH_HFQ
            elif inst in P.columns: c = P[inst]
            else:
                c = load_adj_close_x2(inst); clear_caches()
            rr[inst] = pd.to_numeric(c, errors="coerce").reindex(w.index).pct_change(fill_method=None)
        return (w.shift(1) * pd.DataFrame(rr).fillna(0.0)).sum(axis=1).iloc[1:]
    re_ = leaf_ret(W); rc = leaf_ret(pd.read_parquet(CAP_ADV, columns=["date", "instrument", "target_weight"]))
    df = pd.concat([re_.rename("e"), rc.rename("c"), BENCH_HFQ.pct_change().reindex(re_.index).rename("b")], axis=1).dropna()
    def reg(g, y):
        X = np.c_[np.ones(len(g)), g.b.values]; cf, *_ = np.linalg.lstsq(X, g[y].values, rcond=None); return cf, g[y].values - X @ cf
    (ae, be), ee = reg(df, "e"); (ac, bc), ec = reg(df, "c")
    cagr = lambda r: float((1 + r).prod() ** (252 / len(r)) - 1)
    mdd = lambda r: float(((1 + r).cumprod() / (1 + r).cumprod().cummax() - 1).min())
    yr = {}
    for y, g in df.groupby(df.index.year):
        cf, _ = reg(g, "e"); yr[str(y)] = dict(alpha_ann=float(cf[0] * 252), beta=float(cf[1]), leaf_cagr=cagr(g.e), bench_cagr=cagr(g.b))
    sc = dict(n_days=len(df), beta_leaf=float(be), alpha_ann_leaf=float(ae * 252), beta_cap=float(bc), alpha_ann_cap=float(ac * 252),
              rho_excess_debeta=float(np.corrcoef(ee, ec)[0, 1]), rho_raw_excess=float(np.corrcoef(df.e - df.b, df.c - df.b)[0, 1]),
              leaf_cagr_gross=cagr(df.e), leaf_mdd_gross=mdd(df.e), bench_cagr=cagr(df.b), bench_mdd=mdd(df.b), cap_cagr_gross=cagr(df.c),
              by_year=yr, note_zh="close-to-close 后复权 ETF，无成本，非 Book-Smoke")
    sc["gate_pass"] = bool(sc["rho_excess_debeta"] < 0.5 and ae > 0)
    # daily Jaccard vs all priors (incl. ETF holdings)
    sd = {d: set(g.instrument) for d, g in nb.groupby("date")}
    latest = {}
    for fp in sorted(glob.glob(str(out / "g1g5_*_daily_weights_*.parquet"))):
        k = re.sub(r"_daily_weights_.*", "", Path(fp).name)
        if "industry_etf_rotation" not in k: latest[k] = fp
    dj = {}
    for k, fp in latest.items():
        o = pd.read_parquet(fp, columns=["date", "instrument", "target_weight"]); o["date"] = o.date.astype(str).str[:10]
        o = o[(o.target_weight > 0) & (o.instrument != BALLAST)]; od = {d: set(g.instrument) for d, g in o.groupby("date")}
        js = [len(sd.get(d, set()) & od.get(d, set())) / len(sd.get(d, set()) | od.get(d, set())) for d in set(sd) | set(od) if sd.get(d) or od.get(d)]
        if js:
            mx, fr_ = float(max(js)), float(np.mean([x >= 0.7 for x in js]))
            dj[k] = dict(file=Path(fp).name, mean=float(np.mean(js)), max=mx, frac_ge_0_7=fr_, hard_reject=bool(mx >= 0.7 and fr_ >= 0.5))
    hard = [k for k, v in dj.items() if v["hard_reject"]]
    g6 = run_g6_lookahead_proof(JsonlDebateLedger(out / f"debate_ledger_g1g5_industry_etf_rotation_{stamp}.jsonl"))
    tow = estimate_daily_turnover(W)
    bal = W[W.instrument == BALLAST].groupby("date").target_weight.sum()
    nn = nb.groupby("date").size().reindex(sorted(W.date.unique())).fillna(0)
    meta = dict(mechanism_tag=TAG, who_pays_zh=WHO, prereg="docs/v2/AI_G1G5_INDUSTRY_ETF_ROTATION_WHO_PAYS_PREREG_ZH.md",
                weights_path=str(wpath.relative_to(ROOT)), rows=len(W), n_dates=int(W.date.nunique()), n_instruments=int(W.instrument.nunique()),
                n_etfs_used=int(nb.instrument.nunique()), daily_sum=[float(ds.min()), float(ds.max())], min_weight=float(W.target_weight.min()), stub=False,
                max_single_w=float(nb.target_weight.max()), mean_ballast=float(bal.mean()), min_ballast=float(bal.min()),
                mean_etfs=float(nn.mean()), zero_etf_days=int((nn == 0).sum()), n_rebal=len(picks_log),
                industries_picked=pd.Series([c for p in picks_log for c in p["sel"]]).value_counts().to_dict(),
                turnover=tow, jaccard_daily=dj, hard_reject_isomorph=hard, selfcheck=sc, g6=g6.get("G6"), peak_rss_mb=round(rss(), 1),
                column_contract_version=COLUMN_CONTRACT_VERSION, hard_gate_version=HARD_GATE_VERSION,
                promotion_approved=False, live=False, no_gp=True, no_book_smoke_self=True)
    mpth = out / f"g1g5_industry_etf_rotation_run_meta_{stamp}.json"
    mpth.write_text(json.dumps(meta, ensure_ascii=False, indent=1, default=str)); meta["meta_path"] = str(mpth.relative_to(ROOT))
    (out / f"{wpath.name}.meta.json").write_text(json.dumps({k: meta[k] for k in ("mechanism_tag", "weights_path", "rows", "n_dates", "n_instruments", "g6", "peak_rss_mb", "promotion_approved")}, ensure_ascii=False, indent=1))
    return meta

if __name__ == "__main__":
    m = run(); print(json.dumps({k: v for k, v in m.items() if k not in ("who_pays_zh",)}, ensure_ascii=False, indent=1, default=str))
