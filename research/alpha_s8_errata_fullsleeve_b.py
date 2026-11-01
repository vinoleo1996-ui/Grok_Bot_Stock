"""Alpha 2026-10-18 §8 errata B: full stock sleeve (all held names, normalized) neutral net excess for five HI_LIQ legs,
under prereg style set (Alpha ε) and AI style set (AI ε, disclosure). Read-only; live=false."""
import sys, json, numpy as np, pandas as pd
from pathlib import Path
R = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(R))
import research.alpha_hiliq_s8_paradigm as S8
from research.alpha_combo_marginal import nw_se
OUT = R/"output/alpha/recon_eqinc"
c = S8.build(); E = S8.resid_ret(c)
ae = pd.read_parquet(OUT/"_ai_eps.parquet"); ae["date"] = pd.to_datetime(ae.date)
EI = ae.pivot(index="date", columns="instrument", values="eps").reindex(index=c["ev"], columns=c["U"]); del ae
def nstat(E, W):
    Wl = W.shift(2).fillna(0.0); g = (Wl*E.reindex_like(Wl).fillna(0.0)).sum(axis=1)
    to = W.diff().abs().sum(axis=1).fillna(W.abs().sum(axis=1)).shift(1).fillna(0.0); n = (g-S8.COST*to).iloc[3:]; se = nw_se(n.values, 5)
    return dict(ann_net=float(n.mean()*244), ann_gross=float(g.iloc[3:].mean()*244), to=float(to.mean()), t_hac5=float(n.mean()/se) if se > 0 else None)
res = {}
for k, st in {"capacity_adv": None, **S8.LEGS}.items():
    p = S8.CAP if st is None else S8.LEGD/f"g1g5_{k}_hiliq_v1_daily_weights_20261014_{st}.parquet"
    S = S8.sig(c, p); W = S.div(S.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    res[k] = dict(distinct_w=float(S[S > 0].apply(lambda r: r.dropna().nunique(), axis=1).mean()), names=float((S > 0).sum(1)[S.sum(1) > 0].mean()),
                  prereg_style=nstat(E, W), ai_style=nstat(EI, W)); print(k, res[k], flush=True)
(OUT/"step_d_fullsleeve_b.json").write_text(json.dumps(res, indent=1))
