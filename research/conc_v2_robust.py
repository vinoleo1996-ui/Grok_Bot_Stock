"""Robustness variants for conc v2 B1/B4. Prereg docs/v2/AI_CONC_V2_ROBUSTNESS_PREREG_ZH.md. No returns read.
Part 1 (N±1) files already produced by first pass; this pass computes their stats + drop-3 high-price variants."""
import sys, json
sys.path.insert(0, "research"); sys.path.insert(0, ".")
import numpy as np, pandas as pd
import small_aum_conc_lib as L
OUT = L.ROOT / "output/small_aum_concentration/v2_robust"; L.OUT = OUT
GB = {k: L.GB[k] for k in ("B1_equal", "B4_50_25_25")}
sess, G0 = L.build_sessions(GB); PC = L.prices(G0)
_pc = PC; L.prices = lambda G: _pc
def stats(fp, aum):
    W = pd.read_parquet(fp); sm = W.groupby("session").weight.sum()
    st = W[np.array([not L.etf(i) for i in W.instrument]) & (W.weight > 0).values]
    P = PC.reindex(pd.to_datetime(sorted(W.session.unique()))); P.index = sorted(W.session.unique())
    lt = np.array([P.at[s, i] * 100 if i in P.columns else np.nan for s, i in zip(st.session, st.instrument)]); amt = st.weight.values * aum
    return dict(file=str(fp.relative_to(L.ROOT)), rows=len(W), sum_ok=bool((sm - 1).abs().max() < 1e-9), n_neg=int((W.weight < 0).sum()),
                mean_510300=float(W[W.instrument == L.BAL].groupby("session").weight.sum().reindex(sm.index).fillna(0).mean()),
                names_per_day_median=float(st.groupby("session").size().median()), median_ticket_yuan=float(np.median(amt)),
                share_lt_1lot=float(np.nanmean(amt < lt)), share_lt_minticket=float(np.nanmean(amt < np.maximum(15000, 2 * lt))),
                max_single_stock_w=float(st.weight.max()), cap_ok=bool(st.weight.max() <= 0.06 + 1e-9))
for p in OUT.glob("*ctrl510300*"): p.unlink()
out = {"Nminus": {}, "Nplus": {}, "drop3hp": {}}
for tag in ("Nminus", "Nplus"):
    for arm in GB:
        for a, aum in ((60, 600000), (100, 1000000)):
            out[tag][f"{arm}_{a}w"] = dict(stats(OUT / f"{tag}_{arm}_topN_{a}w.parquet", aum),
                                           N={"Nminus": {60: 5, 100: 9}, "Nplus": {60: 7, 100: 11}}[tag][a])
drops = {}
for arm in GB:
    for a, aum in ((60, 600000), (100, 1000000)):
        W = pd.read_parquet(L.ROOT / f"output/small_aum_concentration/v2/B_{arm}_topN_{a}w.parquet")
        W = W[np.array([not L.etf(i) for i in W.instrument]) & (W.weight > 0).values]
        ss = pd.to_datetime(sorted(W.session.unique()))
        lot = {i: float((PC[i].reindex(ss) * 100).median()) for i in W.instrument.unique() if i in PC}
        hp = [i for i, v in lot.items() if v >= 20000]
        expo = W[W.instrument.isin(hp)].groupby("instrument").weight.sum().sort_values(ascending=False)
        drops[f"{arm}_{a}w"] = [dict(instrument=i, exposure_sum=float(expo[i]), median_lot_yuan=lot[i]) for i in expo.index[:3]]
        ex = set(expo.index[:3])
        orig = L.build_sessions
        L.build_sessions = lambda g, ex=ex: (sess, {k: {s: w.drop([i for i in w.index if i in ex]) for s, w in G0[k].items()} for k in G0})
        L.N = {600000: 6, 1000000: 10}
        L.run_group(f"tmp{a}", {arm: GB[arm]})
        L.build_sessions = orig
        final = OUT / f"drop3hp_B_{arm}_topN_{a}w.parquet"; (OUT / f"tmp{a}_{arm}_topN_{a}w.parquet").replace(final)
        for p in OUT.glob(f"tmp{a}_*"): p.unlink()
        out["drop3hp"][f"{arm}_{a}w"] = stats(final, aum)
(OUT / "SUMMARY.json").write_text(json.dumps(dict(prereg="docs/v2/AI_CONC_V2_ROBUSTNESS_PREREG_ZH.md", drops=drops, variants=out,
    promotion_approved=False, live=False, note="no return data read; exposure-based selection"), ensure_ascii=False, indent=1, default=float))
print(json.dumps(drops, ensure_ascii=False))
for t, o in out.items():
    for k, v in o.items(): print(t, k, {x: (round(y, 4) if isinstance(y, float) else y) for x, y in v.items() if x != "file"})
