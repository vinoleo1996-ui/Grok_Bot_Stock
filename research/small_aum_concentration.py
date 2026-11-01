#!/usr/bin/env python3
"""Small-AUM concentration (lot-dilution fix). Prereg docs/v2/AI_SMALL_AUM_CONCENTRATION_PREREG_ZH.md. promotion=false."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from research.g1g5_x2_panel_stitch import load_panel_features_x2, clear_caches  # noqa
P = {"core": "output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet",
     "etf": "output/ai_factory/g1g5_etf_core_sleeve_daily_weights_20261012_204928.parquet",
     "idx": "output/ai_factory/g1g5_idx_rebal_flow_daily_weights_20261012_215737.parquet",
     "low": "output/intel/g1g5_lowturn_daily_weights_20261012_112301.parquet"}
A = {"CORE": {"core": 1.0}, "A1": {"core": .8, "etf": .2}, "A2": {"core": .8, "idx": .2}, "A3": {"core": .8, "low": .2},
     "A4": {"core": .7, "etf": .15, "idx": .15}, "A5": {"core": .7, "etf": .1, "idx": .1, "low": .1},
     "A6": {"core": .7, "etf": .0864, "idx": .0943, "low": .1193}}
BAL, MIN_T, LOTS, CAP = "510300.SH", 15000.0, 2, 0.06
OUT = ROOT / "output/small_aum_concentration"; OUT.mkdir(exist_ok=True)
is_etf = lambda s: s.str.match(r"^(51|56|58|15)\d{4}\.(SH|SZ)$")
D = {k: pd.read_parquet(ROOT / v, columns=["session", "instrument", "weight"]) for k, v in P.items()}
for d in D.values(): d["session"] = d.session.astype(str).str[:10]
common = set.intersection(*[set(d.loc[d.weight > 0, "session"]) for d in D.values()])
names = sorted({x for d in D.values() for x in d.loc[(d.weight > 0), "instrument"] if not (x[:2] in ("51", "56", "58", "15"))})
px = {}
for x in names:
    try:
        f = load_panel_features_x2(x); px[x] = pd.to_numeric(f["close"], errors="coerce")
    except Exception:
        pass
    clear_caches()
PX = pd.DataFrame(px); PX.index = pd.to_datetime(PX.index); PX = PX.sort_index().ffill()
sess = sorted(common); prevclose = PX.shift(1).reindex(pd.to_datetime(sess)); prevclose.index = sess
summary = {}
for aum in (600000, 1000000):
    for arm, mix in A.items():
        out_rows, st = [], dict(dropped_name_days=0, kept_name_days=0, to_ballast=0.0, n_sessions=len(sess))
        for k in mix: D[k + "_g"] = D[k][D[k].session.isin(common) & (D[k].weight > 0)].groupby("session")
        for s in sess:
            agg = {}
            for k, m in mix.items():
                g = D[k + "_g"].get_group(s) if s in D[k + "_g"].groups else None
                if g is None: continue
                w = (g.set_index("instrument").weight * m)
                stk = w[~is_etf(pd.Series(w.index, index=w.index))]
                etf = w.drop(stk.index)
                for i, v in etf.items(): agg[i] = agg.get(i, 0) + v
                if len(stk):
                    lot = prevclose.loc[s].reindex(stk.index) * 100
                    thr = np.maximum(MIN_T, LOTS * lot.fillna(np.inf))
                    keep = stk[(stk * aum) >= thr]
                    st["dropped_name_days"] += int(len(stk) - len(keep)); st["kept_name_days"] += int(len(keep))
                    if len(keep):
                        keep = keep * stk.sum() / keep.sum()
                        cap = max(float(stk.max()), CAP)
                        over = (keep - cap).clip(lower=0); keep = keep - over
                        agg[BAL] = agg.get(BAL, 0) + float(over.sum()); st["to_ballast"] += float(over.sum())
                        for i, v in keep.items(): agg[i] = agg.get(i, 0) + v
                    else:
                        agg[BAL] = agg.get(BAL, 0) + float(stk.sum()); st["to_ballast"] += float(stk.sum())
            tot = sum(agg.values())
            for i, v in agg.items(): out_rows.append((s, i, v / tot))
        W = pd.DataFrame(out_rows, columns=["session", "instrument", "weight"])
        W = W.groupby(["session", "instrument"], as_index=False).weight.sum()
        sm = W.groupby("session").weight.sum(); assert (sm - 1).abs().max() < 1e-9 and (W.weight >= 0).all()
        W["date"] = W.session; W["target_weight"] = W.weight
        W["instrument_id"] = W.instrument.map(lambda x: x[-2:].lower() + "." + x[:6])
        W["mechanism_tag"] = f"small_aum_conc_{arm}_{aum // 10000}w"; W["who_pays_zh"] = "执行层整手集中化（研究混合）"; W["universe_id"] = "core_satellite_conc"
        fp = OUT / f"conc_{arm}_{aum // 10000}w.parquet"; W.to_parquet(fp, index=False)
        nst = W[(~is_etf(W.instrument)) & (W.weight > 0)]
        st.update(file=str(fp.relative_to(ROOT)), rows=len(W), drop_rate=st["dropped_name_days"] / max(1, st["dropped_name_days"] + st["kept_name_days"]),
                  to_ballast_mean=st["to_ballast"] / len(sess), stock_names_per_day_median=float(nst.groupby("session").size().median()),
                  median_ticket_yuan=float(nst.weight.median() * aum), max_stock_w=float(nst.weight.max()),
                  mean_510300=float(W[W.instrument == BAL].groupby("session").weight.sum().reindex(sess).fillna(0).mean()))
        summary[f"{arm}_{aum // 10000}w"] = st
(OUT / "SUMMARY.json").write_text(json.dumps(dict(prereg="docs/v2/AI_SMALL_AUM_CONCENTRATION_PREREG_ZH.md", params=dict(min_ticket=MIN_T, lots=LOTS, cap=CAP),
                                                   common_sessions=[sess[0], sess[-1], len(sess)], arms=summary, promotion_approved=False, live=False), ensure_ascii=False, indent=1))
for k, v in summary.items(): print(k, {a: (round(b, 4) if isinstance(b, float) else b) for a, b in v.items() if a != "file"})
