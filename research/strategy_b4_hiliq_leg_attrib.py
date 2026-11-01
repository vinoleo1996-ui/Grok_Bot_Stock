#!/usr/bin/env python3
"""RESEARCH-ONLY: attribution / correlation / chart for B4@HI_LIQ leg review.
Reads output/strategy_hiliq/b4_leg_review/ (from strategy_b4_hiliq_leg_review.py). No paper/FROZEN touch.
Contribution(t) = sum_i w_actual(i, t-1) * r_adj(i, t), split per leg by pre-cap provenance share on the
latest target session <= t-1; 510300 (leg ETF part + cap/ind-cap ballast) is its own bucket.
Residual = book NAV return - sum(contrib) (costs, lot rounding, open-vs-close execution, cash interest).
Leg standalone gross series: full leg weights at session s, returns s+2 (lag 2 ~ T+1 open), no cost.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from quantlab.platform.execution import load_execution_panels
OUT = ROOT / "output/strategy_hiliq/b4_leg_review"
X2 = ("2024-06-03", "2026-10-09"); PER = 244; BAL = "510300.SH"
S = json.loads((OUT / "summary.json").read_text())
LEGS = {k: ROOT / v for k, v in S["legs_N1"].items()}
SHORT = {"capacity_adv": "capadv", "earnings_event": "earnings", "insider_increase": "insider"}

def to_id(x):
    c, m = x.split("."); return f"{m.lower()}.{c}"

def is_etf(i): return str(i).split(".")[-1][:2] in ("51", "56", "58", "15") or str(i)[:2] in ("51", "56", "58", "15")

# ---- universe of ids
legW = {}
ids = set([to_id(BAL)])
for k, p in LEGS.items():
    d = pd.read_parquet(p, columns=["session", "instrument", "weight"]); d = d[d.weight > 0]
    d["session"] = d.session.astype(str).str[:10]
    legW[k] = d; ids |= set(d.instrument.map(to_id))
print("ids", len(ids))
pan, _ = load_execution_panels(sorted(ids), "2024-01-01", X2[1])
px = (pan.close * pan.adj_factor.fillna(1.0)).ffill()
R = px.pct_change(fill_method=None).fillna(0.0).astype("float64")
R = R.loc[X2[0]:X2[1]]
dates = R.index

# ---- leg standalone gross daily series (stock sleeve normalized, and full incl ETF)
leg_ret = {}
for k, d in legW.items():
    d = d.copy(); d["id"] = d.instrument.map(to_id)
    Wd = d.pivot_table(index="session", columns="id", values="weight", aggfunc="sum").fillna(0.0)
    Wd.index = pd.to_datetime(Wd.index)
    Wd = Wd.reindex(R.index.union(Wd.index)).ffill().reindex(R.index).fillna(0.0)
    Wl = Wd.shift(2).fillna(0.0)
    st_cols = [c for c in Wl.columns if not is_etf(c.split(".")[1])]
    Ws = Wl[st_cols]; Ws = Ws.div(Ws.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    leg_ret[k + "_stocks"] = (Ws * R[st_cols]).sum(axis=1)
    leg_ret[k + "_full"] = (Wl * R[Wl.columns]).sum(axis=1)
leg_ret["510300"] = R[to_id(BAL)]
LR = pd.DataFrame(leg_ret).iloc[2:]
LR.to_csv(OUT / "leg_standalone_gross_daily.csv")

def stats(r):
    nav = (1 + r).cumprod(); n = len(r)
    cagr = nav.iloc[-1] ** (PER / n) - 1; mdd = (nav / nav.cummax() - 1).min()
    return dict(cagr=cagr, mdd=mdd, sharpe=r.mean() / r.std() * np.sqrt(PER), calmar=cagr / abs(mdd), win=float((r > 0).mean()))
leg_stats = {c: stats(LR[c]) for c in LR.columns}
corr_leg = LR[[c for c in LR.columns if c.endswith("_stocks")] + ["510300"]].corr()
# excess vs 510300 correlation
EX = LR[[c for c in LR.columns if c.endswith("_stocks")]].sub(LR["510300"], axis=0)
corr_ex = EX.corr()

# ---- in-book attribution per arm
res = {"leg_standalone_gross": leg_stats, "corr_leg_stocks": corr_leg.round(3).to_dict(), "corr_leg_excess_vs_510300": corr_ex.round(3).to_dict(), "arms": {}}
navs = {}
for key, a in S["arms"].items():
    arm, aum = a["arm"], a["aum"]
    navs[key] = pd.read_csv(ROOT / a["nav"], parse_dates=["_et"]).set_index("_et")["nav"]
    if arm in ("CAPADV_ONLY", "B4_PRIOR_OLDLEGS"):
        continue
    sd = OUT / f"smoke_{arm}_{aum // 10000}w/aum_{aum}/X2/BOOK"
    aw = pd.read_parquet(sd / "actual_weights.parquet"); aw["session"] = pd.to_datetime(aw.session)
    A = aw.pivot_table(index="session", columns="instrument_id", values="weight", aggfunc="sum").fillna(0.0)
    A = A.reindex(dates).ffill().fillna(0.0)
    pv = pd.read_parquet(OUT / f"prov_{arm}_{aum // 10000}w.parquet"); pv["id"] = pv.instrument.map(to_id)
    pv["session"] = pd.to_datetime(pv.session)
    cols = [c for c in A.columns if c in R.columns]
    miss = [c for c in A.columns if c not in R.columns]
    contrib_i = A[cols].shift(1).fillna(0.0) * R[cols]
    # share panel per leg: explicit 0 for legs absent where the instrument IS in target; NaN where absent from target -> ffill
    PV = pv.pivot_table(index=["session", "id"], columns="leg", values="share", aggfunc="sum").fillna(0.0)
    SH = {}
    for leg in PV.columns:
        sh = PV[leg].unstack("id")
        SH[leg] = sh.reindex(dates.union(sh.index)).ffill().reindex(dates).reindex(columns=cols).fillna(0.0)
    buckets = {}
    for leg, sh in SH.items():
        buckets[SHORT[leg]] = (contrib_i * sh.shift(1).fillna(0.0)).sum(axis=1)
    etf_cols = [c for c in cols if is_etf(c.split(".")[1])]
    buckets["510300/ETF"] = contrib_i[etf_cols].sum(axis=1)
    C = pd.DataFrame(buckets)
    stock_unassigned = contrib_i.sum(axis=1) - C.sum(axis=1)
    C["unassigned_stock"] = stock_unassigned
    nav = navs[key].reindex(dates).ffill(); br = nav.pct_change().fillna(0.0)
    C["residual(cost/exec)"] = br - C.sum(axis=1)
    C.to_csv(OUT / f"contrib_daily_{arm}_{aum // 10000}w.csv")
    # avg weight per bucket
    wb = {}
    for leg, sh in SH.items():
        wb[SHORT[leg]] = float((A[cols] * sh).sum(axis=1).mean())
    wb["510300/ETF"] = float(A[etf_cols].sum(axis=1).mean())
    # MDD episode attribution (arithmetic sum of daily contributions)
    m = a["metrics244"]; pk, tr = pd.Timestamp(m["mdd_peak"]), pd.Timestamp(m["mdd_trough"])
    ep = C.loc[(C.index > pk) & (C.index <= tr)].sum()
    yearly = C.groupby(C.index.year).sum()
    # correlation of in-book leg sleeve returns
    sleeve = {}
    for b in [x for x in C.columns if x in SHORT.values()]:
        sleeve[b] = C[b]
    res["arms"][key] = dict(arm=arm, aum=aum, total_arith_contrib=C.sum().round(4).to_dict(),
                            ann_arith_contrib=(C.mean() * PER).round(4).to_dict(),
                            avg_weight=wb, mdd_episode=[m["mdd_peak"], m["mdd_trough"], m["mdd"]],
                            mdd_episode_contrib=ep.round(4).to_dict(), yearly_contrib=yearly.round(4).to_dict(orient="index"),
                            contrib_corr=pd.DataFrame(sleeve).corr().round(3).to_dict() if len(sleeve) > 1 else None,
                            missing_price_ids=miss)
    print(key, "total", C.sum().round(4).to_dict(), "| MDD ep", ep.round(4).to_dict())

# ---- chart: NAV curves
fp = [f for f in ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc") if Path(f).exists()]
if fp:
    font_manager.fontManager.addfont(fp[0]); plt.rcParams["font.family"] = "Noto Sans CJK SC"
plt.rcParams["axes.unicode_minus"] = False
fig, axes = plt.subplots(1, 2, figsize=(15, 5.5), sharey=False)
lab = {"B4_50_25_25": "B4 50/25/25 (N1腿)", "CAPADV_ONLY": "仅 capacity_adv (全腿)", "CAP_EE_50_50": "capadv+earnings 50/50",
       "CAP_II_50_50": "capadv+insider 50/50", "CAP_BAL_50_50": "对照: capadv 50 + 510300 50", "B4_PRIOR_OLDLEGS": "B4 旧回执(隔离旧腿)"}
sty = {"B4_PRIOR_OLDLEGS": dict(ls=":", color="grey"), "CAP_BAL_50_50": dict(ls="--", color="tab:brown")}
for ax, aum in zip(axes, (600000, 1000000)):
    for arm in lab:
        k = f"{arm}|{aum}"
        if k in navs:
            n = navs[k]; ax.plot(n.index, n / n.iloc[0], label=lab[arm], lw=1.4, **sty.get(arm, {}))
    b = (1 + R[to_id(BAL)]).cumprod(); ax.plot(b.index, b / b.iloc[0], label="510300 买入持有(无成本)", lw=1, color="black", alpha=.5)
    ax.set_title(f"HI_LIQ X2 净值（样本内，{aum // 10000}万）"); ax.grid(alpha=.3); ax.axhline(1, color="k", lw=.5)
axes[0].legend(fontsize=8, loc="upper left")
fig.suptitle("研究诊断 · 事后挑选的对照组（有选择偏差）· 非纸面/非晋级 · live=false", fontsize=10)
fig.tight_layout(); fig.savefig(OUT / "b4_leg_review_nav.png", dpi=120)
res["chart"] = str((OUT / "b4_leg_review_nav.png").relative_to(ROOT))
res["bh_510300"] = stats(LR["510300"])
(OUT / "attribution.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))
print({k: {kk: round(float(vv), 4) for kk, vv in v.items()} for k, v in leg_stats.items()})
print(corr_leg.round(3)); print(corr_ex.round(3)); print("font", fp[:1])
