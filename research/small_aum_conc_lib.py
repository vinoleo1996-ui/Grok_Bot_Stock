#!/usr/bin/env python3
"""Small-AUM concentration v2 (Strategy ruling 2026-10-13). Prereg v2 section in docs/v2/AI_SMALL_AUM_CONCENTRATION_PREREG_ZH.md.
Main: per-leg top-N stock names by original weight (N fixed per AUM), leg stock budget renormalized within leg;
then portfolio-level merged single-name cap 6%, excess -> 510300. Control: v1 min-ticket rule with whole-leg->510300.
promotion=false; live=false; no Book-Smoke."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from research.g1g5_x2_panel_stitch import load_panel_features_x2, clear_caches  # noqa
AF = "output/ai_factory/"
P = {"capacity_adv": AF + "g1g5_capacity_adv_daily_weights_20261013_111219.parquet",
     "earnings_event": AF + "g1g5_earnings_event_daily_weights_20261014_005430.parquet",
     "insider_increase": AF + "g1g5_insider_increase_daily_weights_20261014_011841.parquet",
     "etf": AF + "g1g5_etf_core_sleeve_daily_weights_20261012_204928.parquet",
     "idx": AF + "g1g5_idx_rebal_flow_daily_weights_20261012_215737.parquet",
     "low": "output/intel/g1g5_lowturn_daily_weights_20261012_112301.parquet"}
GB = json.load(open(ROOT / "output/strategy_three_leg/weights_table.json"))["weights"]
GA = {"A1": {"capacity_adv": .8, "etf": .2}, "A2": {"capacity_adv": .8, "idx": .2}, "A3": {"capacity_adv": .8, "low": .2},
      "A4": {"capacity_adv": .7, "etf": .15, "idx": .15}, "A5": {"capacity_adv": .7, "etf": .1, "idx": .1, "low": .1},
      "A6": {"capacity_adv": .7, "etf": .0864, "idx": .0943, "low": .1193}}
N = {600000: 6, 1000000: 10}; CAP = 0.06; BAL = "510300.SH"; MIN_T, LOTS = 15000.0, 2
OUT = ROOT / "output/small_aum_concentration/v2"; OUT.mkdir(parents=True, exist_ok=True)
etf = lambda x: x[:2] in ("51", "56", "58", "15")

def build_sessions(groups):
    used = sorted({k for g in groups.values() for k in g})
    D = {k: pd.read_parquet(ROOT / P[k], columns=["session", "instrument", "weight"]) for k in used}
    for d in D.values(): d["session"] = d.session.astype(str).str[:10]
    common = sorted(set.intersection(*[set(d.loc[d.weight > 0, "session"]) for d in D.values()]))
    G = {k: {s: g.set_index("instrument").weight for s, g in d[d.weight > 0].groupby("session")} for k, d in D.items()}
    return common, G

def prices(G):
    names = sorted({i for g in G.values() for w in g.values() for i in w.index if not etf(i)})
    px = {}
    for x in names:
        try: px[x] = pd.to_numeric(load_panel_features_x2(x)["close"], errors="coerce")
        except Exception: pass
        clear_caches()
    PX = pd.DataFrame(px); PX.index = pd.to_datetime(PX.index); return PX.sort_index().ffill().shift(1)

def run_group(tag, groups):
    sess, G = build_sessions(groups); PC = prices(G); PCs = PC.reindex(pd.to_datetime(sess)); PCs.index = sess
    summ = {}
    for aum in (600000, 1000000):
        for arm, mix in groups.items():
            for variant in ("topN", "ctrl510300"):
                rows, cap_cut = [], 0.0
                for s in sess:
                    agg = {}
                    lot = PCs.loc[s] * 100
                    for k, m in mix.items():
                        w = G[k].get(s)
                        if w is None: continue
                        w = w * m
                        e = w[[etf(i) for i in w.index]]; st = w.drop(e.index)
                        for i, v in e.items(): agg[i] = agg.get(i, 0) + v
                        if not len(st): continue
                        if variant == "topN":
                            keep = st.sort_values(ascending=False).head(N[aum])
                            keep = keep * st.sum() / keep.sum()
                        else:
                            thr = np.maximum(MIN_T, LOTS * lot.reindex(st.index).fillna(np.inf))
                            keep = st[st * aum >= thr]
                            if len(keep): keep = keep * st.sum() / keep.sum()
                            else: agg[BAL] = agg.get(BAL, 0) + st.sum()
                        for i, v in keep.items(): agg[i] = agg.get(i, 0) + v
                    # portfolio-level merged cap
                    for i in list(agg):
                        if not etf(i) and agg[i] > CAP:
                            cap_cut += agg[i] - CAP; agg[BAL] = agg.get(BAL, 0) + agg[i] - CAP; agg[i] = CAP
                    t = sum(agg.values())
                    rows += [(s, i, v / t) for i, v in agg.items()]
                W = pd.DataFrame(rows, columns=["session", "instrument", "weight"]).groupby(["session", "instrument"], as_index=False).weight.sum()
                assert ((W.groupby("session").weight.sum() - 1).abs() < 1e-9).all() and (W.weight >= 0).all()
                W["date"] = W.session; W["target_weight"] = W.weight
                W["instrument_id"] = W.instrument.map(lambda x: x[-2:].lower() + "." + x[:6])
                W["mechanism_tag"] = f"small_aum_conc_v2_{variant}_{arm}_{aum // 10000}w"; W["who_pays_zh"] = "执行层整手集中化 v2（研究混合）"; W["universe_id"] = "conc_v2"
                fp = OUT / f"{tag}_{arm}_{variant}_{aum // 10000}w.parquet"; W.to_parquet(fp, index=False)
                stk = W[[not etf(i) for i in W.instrument]]; stk = stk[stk.weight > 0].copy()
                amt = stk.weight * aum
                lt = np.array([PCs.at[s, i] * 100 if i in PCs.columns else np.nan for s, i in zip(stk.session, stk.instrument)])
                summ[f"{arm}_{variant}_{aum // 10000}w"] = dict(
                    file=str(fp.relative_to(ROOT)), group=tag, N=N[aum] if variant == "topN" else None, rows=len(W),
                    mean_510300=float(W[W.instrument == BAL].groupby("session").weight.sum().reindex(sess).fillna(0).mean()),
                    mean_etf_total=float(W[[etf(i) for i in W.instrument]].groupby("session").weight.sum().reindex(sess).fillna(0).mean()),
                    stock_names_per_day_median=float(stk.groupby("session").size().median()),
                    median_ticket_yuan=float(amt.median()), p10_ticket_yuan=float(amt.quantile(.1)),
                    share_lt_1lot=float(np.nanmean(amt.values < lt)), share_lt_minticket=float(np.nanmean(amt.values < np.maximum(MIN_T, LOTS * lt))),
                    lot_price_missing=int(np.isnan(lt).sum()),
                    max_single_stock_w=float(stk.weight.max()), cap_ok=bool(stk.weight.max() <= CAP + 1e-9), cap_cut_to_510300_mean=cap_cut / len(sess))
    return sess, summ

