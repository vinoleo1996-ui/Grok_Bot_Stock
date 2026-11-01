"""Diagnose capacity_adv HI_LIQ 25-name full sleeve neutral net excess gap: AI style ε (−48.7%) vs Alpha frozen style ε (+8.2%).
X2 only (features warm-up from 2023-06 past returns). Read-only; live=false. nstat = Alpha alpha_s8_errata_fullsleeve_b.nstat (W.shift(2), COST)."""
import sys, json, resource, numpy as np, pandas as pd
from pathlib import Path
R = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(R))
import research.alpha_decay_gate as ADG
S, E_ = pd.Timestamp("2024-06-03"), pd.Timestamp("2026-10-09"); COST = ADG.COST
rss = lambda: resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
PC = R/"output/ai_factory/panel_cache"
P = pd.concat([pd.read_parquet(PC/f"cs_panel_{y}.parquet", columns=["date","instrument","hiliq","ret","logmv","ind","adv20_yuan"], filters=[("date", ">=", pd.Timestamp("2023-06-01").to_pydatetime())]) for y in (2023, 2024, 2025, 2026)])
P = P[P.date <= E_]
pv = lambda c: P.pivot_table(index="date", columns="instrument", values=c).sort_index()
RW = pv("ret"); LM = pv("logmv").reindex_like(RW); IND = pv("ind").reindex_like(RW); ADV = pv("adv20_yuan").reindex_like(RW)
HL = P.pivot_table(index="date", columns="instrument", values="hiliq", aggfunc="max").reindex_like(RW).fillna(False).astype(bool); del P
e = pd.read_parquet(R/"data/v2/etf/etf_daily_adj.parquet", columns=["trade_date","close_hfq"], filters=[("ts_code","==","510300.SH")]); e.index = pd.to_datetime(e.trade_date.astype(str)); rb = e.close_hfq.sort_index().pct_change().reindex(RW.index)
C = (1+RW.fillna(0)).cumprod().where(RW.notna() | RW.shift(1).notna())
F = dict(mom20=RW.shift(1).rolling(20, min_periods=15).sum(), vol20=RW.shift(1).rolling(20, min_periods=15).std(),
         mv_same=LM, mv_lag=LM.shift(1),
         beta=(RW.rolling(120, min_periods=60).cov(rb).div(rb.rolling(120, min_periods=60).var(), axis=0)).shift(1),
         mom120_20=(C.shift(20)/C.shift(120)-1).shift(1), liq=np.log(ADV.shift(1).clip(lower=1)))
print("features", f"rss={rss():.0f}", flush=True)
import os; LEG = os.environ.get("LEG", "g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet"); ONLY = os.environ.get("ONLY")
cap = pd.read_parquet(R/"output/strategy_hiliq/legs"/LEG, columns=["date","instrument","target_weight"])
cap["date"] = pd.to_datetime(cap.date.astype(str).str[:10]); cap = cap[cap.instrument != "510300.SH"]
Wc = cap.pivot_table(index="date", columns="instrument", values="target_weight", aggfunc="sum")
ev = RW.index[(RW.index >= S) & (RW.index <= E_)]
W = Wc.reindex(index=ev, columns=RW.columns).fillna(0.0); W = W.div(W.sum(1).replace(0, np.nan), axis=0).fillna(0.0)
miss_cols = sorted(set(Wc.columns[(Wc > 0).any()]) - set(RW.columns))
VARS = {
 "A0_AI_exact(同日logmv,截尾,当日池)": dict(st=["mv_same","mom20","vol20"], clip=True, pool_lag=False, z=True),
 "A1_AI+logmv滞后1日": dict(st=["mv_lag","mom20","vol20"], clip=True, pool_lag=False, z=True),
 "A2_A1+不截尾": dict(st=["mv_lag","mom20","vol20"], clip=False, pool_lag=False, z=True),
 "A3_A2+前日池": dict(st=["mv_lag","mom20","vol20"], clip=False, pool_lag=True, z=True),
 "B0_Alpha风格(cs_panel重建)": dict(st=["mv_lag","beta","mom120_20","liq"], clip=False, pool_lag=True, z=False),
 "B1_B0+mom20+vol20": dict(st=["mv_lag","beta","mom120_20","liq","mom20","vol20"], clip=False, pool_lag=True, z=False),
 "B2_B0但同日logmv": dict(st=["mv_same","beta","mom120_20","liq"], clip=False, pool_lag=True, z=False),
 "B3_B0+mom20": dict(st=["mv_lag","beta","mom120_20","liq","mom20"], clip=False, pool_lag=True, z=False),
 "B4_B0+vol20": dict(st=["mv_lag","beta","mom120_20","liq","vol20"], clip=False, pool_lag=True, z=False),
}
Wl = W.shift(2).fillna(0.0); to = W.diff().abs().sum(1).fillna(W.abs().sum(1)).shift(1).fillna(0.0)
res = {}; prevd = dict(zip(ev[1:], ev[:-1]))
if ONLY: VARS = {k: v for k, v in VARS.items() if k[:2] in ONLY.split(",")}
for vn, v in VARS.items():
    Ed = pd.DataFrame(np.nan, index=ev, columns=RW.columns); contrib = {k: [] for k in v["st"]}; indc, rawp = [], []
    for d in ev[1:]:
        d0 = prevd[d]; pool = HL.loc[d0] if v["pool_lag"] else HL.loc[d]
        X = pd.DataFrame({k: F[k].loc[d] for k in v["st"]})[pool]; y = RW.loc[d][pool]; ind = IND.loc[d0 if v["pool_lag"] else d][pool]
        ok = X.notna().all(1) & y.notna() & ind.notna() & (ind >= 0); X, y, ind = X[ok], y[ok], ind[ok]
        if len(y) < 100: continue
        yv = y.to_numpy(float); yv = yv.clip(-.21, .31) if v["clip"] else yv
        Xs = X.to_numpy(float)
        if v["z"]: Xs = (Xs - Xs.mean(0))/Xs.std(0)
        D = (ind.to_numpy()[:, None] == np.unique(ind.to_numpy())[None, :]).astype(float)
        M = np.column_stack([D, Xs]); b, *_ = np.linalg.lstsq(M, yv, rcond=None); eps = yv - M@b
        Ed.loc[d, y.index] = eps
        w = Wl.loc[d].reindex(y.index).fillna(0).to_numpy()
        for j, k in enumerate(v["st"]): contrib[k].append(float(w @ (Xs[:, j]*b[D.shape[1]+j])))
        indc.append(float(w @ (D@b[:D.shape[1]]))); rawp.append(float(w @ yv))
    g = (Wl*Ed.fillna(0.0)).sum(1); n = (g - COST*to).iloc[3:]
    held_nan = float(((Wl > 0) & Ed.isna()).sum(1).iloc[3:].mean())
    res[vn] = dict(ann_net=float(n.mean()*244), ann_gross_eps=float(g.iloc[3:].mean()*244), t=float(n.mean()/n.std()*np.sqrt(len(n))),
                   decomp_ann=dict(raw_port=float(np.mean(rawp)*244), industry=float(np.mean(indc)*244), **{k: float(np.mean(c)*244) for k, c in contrib.items()}),
                   held_names_eps_nan_per_day=held_nan)
    if vn.startswith("A0"): EA0 = Ed
    if vn.startswith("B0"): EB0 = Ed
    print(vn, {k: (round(x, 4) if isinstance(x, float) else x) for k, x in res[vn].items()}, f"rss={rss():.0f}", flush=True)
if not ONLY: res["eps_corr_A0_vs_B0"] = None
if ONLY: EA0 = EB0 = None
else:
  cmpf = pd.concat([EA0.stack().rename("a"), EB0.stack().rename("b")], axis=1).dropna(); res["eps_corr_A0_vs_B0"] = float(cmpf.a.corr(cmpf.b))
# checks
x = RW.loc[ev].where(HL.loc[ev]); res["ret_abs_gt_21pct_share_pool"] = float((x.abs() > .21).sum().sum()/x.notna().sum().sum())
res["held_weight_on_clipped_days"] = float((Wl.loc[ev] * (RW.loc[ev].abs() > .21)).sum(1).mean())
res["cap_cols_missing_in_panel"] = miss_cols[:10]; res["n_missing"] = len(miss_cols)
res["held_exposure_mean"] = {k: float((Wl.loc[ev[3:]]*((F[k].loc[ev[3:]].sub(F[k].loc[ev[3:]].where(HL.loc[ev[3:]]).mean(1), axis=0)).div(F[k].loc[ev[3:]].where(HL.loc[ev[3:]]).std(1), axis=0))).sum(1).mean()) for k in ("mv_same","mom20","vol20","beta","mom120_20","liq")}
res["corr_logmv_same_minus_lag_vs_ret"] = float(pd.concat([(LM-LM.shift(1)).loc[ev].where(HL.loc[ev]).stack().rename("dl"), RW.loc[ev].where(HL.loc[ev]).stack().rename("r")], axis=1).dropna().corr().iloc[0, 1])
res["peak_rss_mb"] = rss(); Path(R/("output/ai_factory/capadv_neutral_gap_diag.json" if not ONLY else f"output/ai_factory/neutral_gap_diag_{LEG[:30]}_{ONLY}.json")).write_text(json.dumps(res, ensure_ascii=False, indent=1)); print(json.dumps(res, ensure_ascii=False, indent=1))
