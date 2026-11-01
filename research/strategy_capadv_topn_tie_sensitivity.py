#!/usr/bin/env python3
"""RESEARCH-ONLY SENSITIVITY (not a replacement): B4@HI_LIQ per-leg Top-N tie-break variants.
Replicates strategy_b4_hiliq_leg_review.build (N1 legs, 50/25/25, Top-6/10, 6% cap, SW-L1<=25%) and only
changes the tie-break among equal leg weights. X2 in-sample; no sealed window; no paper/FROZEN touch; live=false.
Outputs: output/strategy_hiliq/topn_tie_audit/sens_*"""
import json, sys, hashlib, time
from pathlib import Path
import numpy as np, pandas as pd, pyarrow.parquet as pq, pyarrow.compute as pc
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import importlib.util
spec = importlib.util.spec_from_file_location("lr", ROOT/"research/strategy_b4_hiliq_leg_review.py"); lr = importlib.util.module_from_spec(spec); spec.loader.exec_module(lr)
hx2 = lr.hx2
OUT = ROOT/"output/strategy_hiliq/topn_tie_audit"; OUT.mkdir(parents=True, exist_ok=True)
MIX = {"capacity_adv": 0.5, "earnings_event": 0.25, "insider_increase": 0.25}
LEGS = lr.N1

def adv_table(sessions):
    f = pq.ParquetFile(str(ROOT/"data/v2/valuation/daily_basic_full_tushare.parquet")); parts = []
    s0 = pd.Timestamp(min(sessions)) - pd.Timedelta(days=60); s1 = pd.Timestamp(max(sessions))
    for i in range(f.metadata.num_row_groups):
        t = f.read_row_group(i, columns=["ts_code", "trade_date", "turnover_rate", "float_mktcap"]).to_pandas()
        t = t[(t.trade_date >= s0) & (t.trade_date <= s1)]
        if len(t): parts.append(t)
    d = pd.concat(parts); d["adv"] = d.float_mktcap * d.turnover_rate / 100.0
    P = d.pivot_table(index="trade_date", columns="ts_code", values="adv").sort_index()
    A = P.rolling(20, min_periods=10).mean().shift(1)  # strictly prior-day info
    A.index = A.index.strftime("%Y-%m-%d"); return A

def build(selector):
    G = {k: lr.legG(LEGS[k]) for k in MIX}
    common = sorted(set.intersection(*[set(g) for g in G.values()]))
    ind_map = hx2.load_industry_map(); out = {}
    for aum in (600000, 1000000):
        n = lr.N_BY_AUM[aum]; rows = []
        for s in common:
            agg = {}
            for k, m in MIX.items():
                w = G[k].get(s)
                if w is None: continue
                w = w*m; em = [hx2._is_etf(i) for i in w.index]; e = w[em]; st = w[[not x for x in em]]
                for i, v in e.items(): agg[i] = agg.get(i, 0.0)+float(v)
                if not len(st): continue
                keep = selector(st, n, s, k)
                keep = keep*(st.sum()/keep.sum()) if keep.sum() > 0 else keep
                for i, v in keep.items(): agg[i] = agg.get(i, 0.0)+float(v)
            for i in list(agg):
                if (not hx2._is_etf(i)) and agg[i] > lr.CAP:
                    agg[lr.BAL] = agg.get(lr.BAL, 0.0)+agg[i]-lr.CAP; agg[i] = lr.CAP
            agg, _ = hx2.apply_ind_cap(agg, ind_map, lr.IND_CAP); t = sum(agg.values())
            rows += [(s, i, v/t) for i, v in agg.items() if v > 0]
        W = pd.DataFrame(rows, columns=["session", "instrument", "weight"]).groupby(["session", "instrument"], as_index=False).weight.sum()
        W["date"] = W.session; W["target_weight"] = W.weight; W["instrument_id"] = W.instrument.map(hx2.to_id)
        W["mechanism_tag"] = "topn_tie_sensitivity_research_only"; W["who_pays_zh"] = "研究敏感性（非替换、非纸面）"; W["universe_id"] = "HI_LIQ_V1.1"
        out[aum] = W
    return out

def sel_prod(st, n, s, k): return st.sort_values(ascending=False).head(n)
def keyed(key_fn):
    def f(st, n, s, k):
        tk = key_fn(st, s, k); o = np.lexsort((tk, -st.round(12).values)); return st.iloc[o[:n]]
    return f

def main():
    variants = {"PROD": sel_prod,
                "CODE": keyed(lambda st, s, k: np.argsort(np.argsort(np.array(st.index)))) }
    # v1: PERSISTENT random priority per (seed, leg, instrument) — mirrors a fixed arbitrary order like PROD's set order.
    # (v0 redrew per session -> daily churn, cost 17-24% of initial; discarded, see _discarded/)
    NSEED = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    for seed in range(1, NSEED + 1):
        def rk(st, s, k, seed=seed):
            return np.array([int(hashlib.md5(f"{seed}|{k}|{i}".encode()).hexdigest()[:12], 16) for i in st.index])
        variants[f"RAND{seed}"] = keyed(rk)
    ex = pd.read_parquet(LEGS["capacity_adv"], columns=["session"]); sess = sorted(ex.session.astype(str).str[:10].unique())
    A = adv_table([x for x in sess if x >= "2024-01-01"])
    def advk(st, s, k):
        row = A.loc[s] if s in A.index else pd.Series(dtype=float)
        return -row.reindex(st.index).fillna(0.0).values  # higher ADV first
    variants["ADV"] = keyed(advk)
    res = {}
    for nm, fn in variants.items():
        Ws = build(fn)
        for aum, W in Ws.items():
            tag = f"{nm}_{aum//10000}w"; fp = OUT/f"sens_weights_B4_{tag}.parquet"; W.to_parquet(fp, index=False)
            if nm == "PROD":
                ref = pd.read_parquet(ROOT/f"output/strategy_hiliq/b4_leg_review/weights_B4_50_25_25_{aum//10000}w.parquet", columns=["session","instrument","weight"])
                j = W[["session","instrument","weight"]].merge(ref, on=["session","instrument"], how="outer", suffixes=("", "_ref")).fillna(0)
                res[f"repro_check_{aum}"] = dict(max_abs_diff=float((j.weight-j.weight_ref).abs().max()), rows=len(W), rows_ref=len(ref))
                print("repro", aum, res[f"repro_check_{aum}"], flush=True)
                nav = ROOT/f"output/strategy_hiliq/b4_leg_review/smoke_B4_50_25_25_{aum//10000}w/aum_{aum}/X2/BOOK/nav.csv"
                res[tag] = dict(metrics=lr.nav_metrics(nav), nav=str(nav.relative_to(ROOT)), reused=True); continue
            sd = OUT/f"sens_smoke_B4_{tag}"; t0 = time.time(); sm = lr.run_smoke(fp, sd, str(aum))
            nav = sd/f"aum_{aum}"/"X2"/"BOOK"/"nav.csv"
            bk = next((v for kk, v in (sm.get("by_capital", {}).get(str(aum), {}) or {}).items() if "BOOK" in kk), {})
            res[tag] = dict(metrics=lr.nav_metrics(nav) if nav.exists() else None, cost_pct=bk.get("cost_pct_initial"), fill_ratio=bk.get("fill_ratio"),
                            sec=round(time.time()-t0, 1), weights=str(fp.relative_to(ROOT)))
            m = res[tag]["metrics"] or {}; print(tag, round(m.get("cagr", np.nan), 4), round(m.get("mdd", np.nan), 4), res[tag]["sec"], flush=True)
            # name overlap vs PROD
        for aum, W in Ws.items():
            P = pd.read_parquet(OUT/f"sens_weights_B4_PROD_{aum//10000}w.parquet")
            a = W[~W.instrument.map(hx2._is_etf)].groupby("session").instrument.apply(set); b = P[~P.instrument.map(hx2._is_etf)].groupby("session").instrument.apply(set)
            ix = a.index.intersection(b.index); ix = [x for x in ix if x >= "2024-06-03"]
            res[f"{nm}_{aum//10000}w"]["jaccard_vs_prod_mean"] = float(np.mean([len(a[d] & b[d])/len(a[d] | b[d]) for d in ix]))
    res["banner"] = "SENSITIVITY ONLY — not a replacement; X2 in-sample; no sealed; live=false; promotion=false; paper untouched"
    (OUT/"sensitivity_summary.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float)); print("WROTE")
if __name__ == "__main__": main()
