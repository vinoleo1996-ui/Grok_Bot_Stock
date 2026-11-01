"""Step A of equity_incentive sign reconciliation (Alpha, 2026-10-18): reproduce AI 10-14 supplement numbers with AI's
exact conventions (code copied from research/ai_hiliq_sec8_supplement.py, equity_incentive only), and dump AI eps panel
+ AI pool for step B. Read-only; live=false."""
import json, sys, gc, numpy as np, pandas as pd
from pathlib import Path
R = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(R))
import research.leaf_selfcheck_common as LC
from research.leaf_selfcheck_v3 import leaf_topn
L = R/"output/strategy_hiliq/legs"; PC = R/"output/ai_factory/panel_cache"; OUT = R/"output/alpha/recon_eqinc"
LEG = L/"g1g5_equity_incentive_hiliq_v1_daily_weights_20261014_202436.parquet"
CAP = L/"g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet"
X2 = ("2024-06-03", "2026-10-09"); COST = 0.00175
P = pd.concat([pd.read_parquet(PC/f"cs_panel_{y}.parquet", columns=["date","instrument","hiliq","ret","logmv","ind"]) for y in (2023, 2024, 2025, 2026)])
RW = P.pivot_table(index="date", columns="instrument", values="ret").astype("float32").sort_index()
mom = RW.shift(1).rolling(20, min_periods=15).sum().stack().rename("mom20"); vol = RW.shift(1).rolling(20, min_periods=15).std().stack().rename("vol20"); del RW; gc.collect()
P = P[P.date >= "2024-01-01"].join(mom.astype("float32"), on=["date","instrument"]).join(vol.astype("float32"), on=["date","instrument"]); del mom, vol; gc.collect()
rows = []
for d, g in P[P.hiliq].groupby("date", sort=True):
    g = g.dropna(subset=["ret","logmv","mom20","vol20"]); g = g[g.ind >= 0]
    if len(g) < 100: continue
    X = np.column_stack([pd.get_dummies(g.ind).to_numpy(float), g[["logmv","mom20","vol20"]].to_numpy(float)]); X[:, -3:] = (X[:, -3:]-X[:, -3:].mean(0))/X[:, -3:].std(0)
    y = g.ret.to_numpy(float).clip(-.21, .31); b, *_ = np.linalg.lstsq(X, y, rcond=None)
    rows.append(pd.DataFrame({"date": d, "instrument": g.instrument.values, "eps": (y-X@b).astype("float32")}))
pool = P[P.hiliq & (P.ind >= 0) & np.isfinite(P.logmv)][["date","instrument","ind","logmv"]].copy(); del P; gc.collect()
E = pd.concat(rows); del rows
E.to_parquet(OUT/"_ai_eps.parquet"); pool.to_parquet(OUT/"_ai_pool.parquet")
Ew = E.pivot(index="date", columns="instrument", values="eps").sort_index(); del E; gc.collect()
Ew.index = pd.to_datetime(Ew.index); pool["date"] = pd.to_datetime(pool.date)
cap = LC._w(CAP); cap["date"] = pd.to_datetime(cap.date)
capset = {d: set(x.instrument) for d, x in cap[~cap.instrument.map(LC.etf)].groupby("date")}
W = LC._w(LEG); Wd = W.copy(); Wd["date"] = pd.to_datetime(Wd.date)
sig = {d: set(x.instrument) for d, x in Wd[~Wd.instrument.map(LC.etf)].groupby("date")}
h = 20; fwd = Ew.shift(-2).rolling(h, min_periods=1).sum().shift(-(h-1))
ics = {}
for d, gp in pool.groupby("date"):
    if d not in fwd.index or d not in sig: continue
    f = fwd.loc[d]; gp = gp[gp.instrument.isin(f.dropna().index)]
    if len(gp) < 200: continue
    s = gp.instrument.isin(sig[d]).to_numpy(float)
    if s.sum() < 3: continue
    X = np.column_stack([pd.get_dummies(gp.ind).to_numpy(float), gp.logmv.to_numpy(float)[:, None], gp.instrument.isin(capset.get(d, set())).to_numpy(float)[:, None]])
    b, *_ = np.linalg.lstsq(X, s, rcond=None); sr = s-X@b
    ics[d] = float(np.corrcoef(sr, f[gp.instrument].to_numpy(float))[0, 1])
s = pd.Series(ics); s = s[(s.index >= X2[0]) & (s.index <= X2[1])].dropna()
def neutral_net(Wx):
    Pw = Wx.pivot_table(index="date", columns="instrument", values="target_weight", aggfunc="sum").fillna(0); Pw.index = pd.to_datetime(Pw.index)
    H = Pw.shift(1).fillna(0); st = [c for c in H.columns if not LC.etf(c)]
    e = Ew.reindex(index=H.index, columns=st).fillna(0); gross = (H[st].shift(1).fillna(0)*e).sum(1)
    to = H.diff().abs().sum(1).fillna(H.abs().sum(1)); net = gross-COST*to; net = net[(net.index >= X2[0]) & (net.index <= X2[1])]
    return dict(ann244=float(net.mean()*244), gross244=float(gross[net.index].mean()*244), stock_share=float(H[st].sum(1).mean()))
res = dict(ic20_mean_all_days=float(s.mean()), ic20_nonoverlap_mean=float(s.iloc[::h].mean()), n=int(len(s)), neutral_net_full=neutral_net(W))
for tier, N in {"60w": 6, "100w": 10}.items():
    lt = leaf_topn(W, N); lw = pd.DataFrame([(d, i, v) for d, x in lt.items() for i, v in x.items()], columns=["date","instrument","target_weight"])
    res[tier] = neutral_net(lw)
s.to_frame("ic").to_parquet(OUT/"_ai_ic20_series.parquet")
(OUT/"step_a_ai_repro.json").write_text(json.dumps(res, indent=1)); print(json.dumps(res, indent=1))
