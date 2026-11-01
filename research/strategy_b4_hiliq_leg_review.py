#!/usr/bin/env python3
"""RESEARCH-ONLY: B4@HI_LIQ leg review (earnings_event / insider_increase 25% each?).

BANNER: analysis only. Does NOT touch B4 paper track / FROZEN_CONFIG / paper outputs.
live=false, promotion=false. Outputs only under output/strategy_hiliq/b4_leg_review/.
X2 2024-06-03..2026-10-09 is IN-SAMPLE; arms chosen after the fact (selection bias).

Synthesis replicates research/strategy_hiliq_capadv_b4_x2.py::build_topn exactly
(per-leg topN 6/10, single-name <=6% -> 510300, SW-L1 stock sleeve <=25% iterative),
plus an explicit "BAL" pseudo-leg (=510300) and per-leg provenance tracking.
book-smoke receipt is redirected into the review dir (no docs/ side effect).
"""
from __future__ import annotations
import importlib.util, json, subprocess, sys, hashlib
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("hx2", ROOT / "research/strategy_hiliq_capadv_b4_x2.py")
hx2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(hx2)

OUT = ROOT / "output/strategy_hiliq/b4_leg_review"
OUT.mkdir(parents=True, exist_ok=True)
LEGS = ROOT / "output/strategy_hiliq/legs"
BAL, CAP, IND_CAP = hx2.BAL, hx2.CAP, hx2.IND_CAP
N_BY_AUM = hx2.N_BY_AUM
X2 = hx2.X2
PER = 244

N1 = {  # Arch T5 repoint (ind_cap_ok_book=true)
    "capacity_adv": LEGS / "g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet",
    "earnings_event": LEGS / "g1g5_earnings_event_hiliq_v1_daily_weights_20261014_202822.parquet",
    "insider_increase": LEGS / "g1g5_insider_increase_hiliq_v1_daily_weights_20261014_202928.parquet",
}
OLD = {  # quarantined pre-N1 legs (REJECT_IND_CAP) - provenance check only
    "capacity_adv": N1["capacity_adv"],
    "earnings_event": LEGS / "_rejected_ind_cap/g1g5_earnings_event_hiliq_v1_daily_weights_20261014_195336.parquet",
    "insider_increase": LEGS / "_rejected_ind_cap/g1g5_insider_increase_hiliq_v1_daily_weights_20261014_195433.parquet",
}
ARMS = {
    "B4_50_25_25": {"capacity_adv": 0.5, "earnings_event": 0.25, "insider_increase": 0.25},
    "CAP_EE_50_50": {"capacity_adv": 0.5, "earnings_event": 0.5},
    "CAP_II_50_50": {"capacity_adv": 0.5, "insider_increase": 0.5},
    "CAP_BAL_50_50": {"capacity_adv": 0.5, "BAL": 0.5},  # control: event legs -> 510300
}
_leg_cache: dict = {}


def legG(path: Path):
    if path not in _leg_cache:
        d = hx2.load_leg(path)
        _leg_cache[path] = {s: g.set_index("instrument")["weight"] for s, g in d.groupby("session")}
    return _leg_cache[path]


def build(mix: dict, aum: int, legs: dict, ind_map: dict):
    used = [k for k in mix if k != "BAL"]
    G = {k: legG(legs[k]) for k in used}
    common = sorted(set.intersection(*[set(g) for g in G.values()]))
    n = N_BY_AUM[aum]
    rows, prov = [], []
    for s in common:
        agg: dict[str, float] = {}
        src: dict[str, dict[str, float]] = {}  # stock -> leg -> pre-cap weight
        if "BAL" in mix:
            agg[BAL] = agg.get(BAL, 0.0) + mix["BAL"]
        for k in used:
            w = G[k].get(s)
            if w is None:
                continue
            w = w * mix[k]
            e_mask = [hx2._is_etf(i) for i in w.index]
            e = w[e_mask]; st = w[[not x for x in e_mask]]
            for i, v in e.items():
                agg[i] = agg.get(i, 0.0) + float(v)
            if len(st) == 0:
                continue
            keep = st.sort_values(ascending=False).head(n)
            keep = keep * (st.sum() / keep.sum()) if keep.sum() > 0 else keep
            for i, v in keep.items():
                agg[i] = agg.get(i, 0.0) + float(v)
                src.setdefault(i, {})[k] = src.get(i, {}).get(k, 0.0) + float(v)
        for i in list(agg):
            if (not hx2._is_etf(i)) and agg[i] > CAP:
                agg[BAL] = agg.get(BAL, 0.0) + agg[i] - CAP
                agg[i] = CAP
        agg, _ = hx2.apply_ind_cap(agg, ind_map, IND_CAP)
        t = sum(agg.values())
        for i, v in agg.items():
            if v > 0:
                rows.append((s, i, v / t))
        for i, d in src.items():
            tot = sum(d.values())
            for k, v in d.items():
                prov.append((s, i, k, v / tot))
    W = pd.DataFrame(rows, columns=["session", "instrument", "weight"])
    W = W.groupby(["session", "instrument"], as_index=False)["weight"].sum()
    W["date"] = W["session"]; W["target_weight"] = W["weight"]
    W["instrument_id"] = W["instrument"].map(hx2.to_id)
    W["mechanism_tag"] = "hiliq_leg_review_research_only"
    W["who_pays_zh"] = "研究诊断（非纸面）"; W["universe_id"] = "HI_LIQ_V1.1"
    Pv = pd.DataFrame(prov, columns=["session", "instrument", "leg", "share"])
    return W, Pv


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run_smoke(stock_path: Path, out_dir: Path, capitals: str) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "-m", "quantlab.cli", "book-smoke", "--run-nav",
           "--stock-path", str(stock_path.relative_to(ROOT)), "--out", str(out_dir.relative_to(ROOT)),
           "--receipt", str((out_dir / "receipt.md").relative_to(ROOT)),
           "--windows", "X2", "--capitals", capitals,
           "--sleeves", '{"core":0,"stock":1,"alpha_event":0}', "--arms", "BOOK,C0"]
    with open(out_dir / "run.log", "w") as f:
        r = subprocess.run(cmd, cwd=str(ROOT), stdout=f, stderr=subprocess.STDOUT, text=True)
    sp = out_dir / "book_smoke_summary.json"
    return json.loads(sp.read_text()) if sp.exists() else {"ok": False, "rc": r.returncode}


def nav_metrics(nav_csv: Path) -> dict:
    nav = pd.read_csv(nav_csv, parse_dates=["_et"]).sort_values("_et").set_index("_et")["nav"]
    r = nav.pct_change().dropna()
    n = len(r)
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (PER / n) - 1
    dd = nav / nav.cummax() - 1
    mdd = dd.min()
    trough = dd.idxmin(); peak = nav.loc[:trough].idxmax()
    sharpe = r.mean() / r.std() * np.sqrt(PER)
    m = nav.resample("ME").last(); mr = pd.concat([nav.iloc[:1], m]).pct_change().dropna()
    mr = mr[mr.index > nav.index[0]]
    return dict(cagr=cagr, mdd=mdd, sharpe=sharpe, calmar=cagr / abs(mdd), vol=r.std() * np.sqrt(PER),
                win_daily=float((r > 0).mean()), win_monthly=float((mr > 0).mean()), n_ret_days=n,
                mdd_peak=str(peak.date()), mdd_trough=str(trough.date()), total_return=nav.iloc[-1] / nav.iloc[0] - 1)


def main():
    ind_map = hx2.load_industry_map()
    res = {"banner": "RESEARCH-ONLY; X2 in-sample; arms chosen post hoc (selection bias); no paper/FROZEN change; live=false; promotion=false",
           "legs_N1": {k: str(v.relative_to(ROOT)) for k, v in N1.items()},
           "legs_old_quarantined": {k: str(v.relative_to(ROOT)) for k, v in OLD.items()}}
    # ---- 1) provenance: which legs produced the existing B4 parquets?
    prov = {}
    for aum in (600000, 1000000):
        ex = pd.read_parquet(ROOT / f"output/strategy_hiliq/b4/B4_50_25_25_topN_{aum // 10000}w.parquet")
        ex = ex.set_index(["session", "instrument"])["weight"]
        out = {}
        for tag, legs in (("old_1953xx", OLD), ("N1_2028xx", N1)):
            W, _ = build(ARMS["B4_50_25_25"], aum, legs, ind_map)
            w = W.set_index(["session", "instrument"])["weight"]
            j = pd.concat([ex.rename("ex"), w.rename("new")], axis=1).fillna(0)
            out[tag] = dict(rows_existing=int(len(ex)), rows_rebuilt=int(len(w)),
                            max_abs_diff=float((j.ex - j.new).abs().max()),
                            sum_abs_diff_per_day=float((j.ex - j.new).abs().groupby(level=0).sum().mean()),
                            identical=bool((j.ex - j.new).abs().max() < 1e-9))
        prov[str(aum)] = out
    res["provenance_existing_B4"] = prov
    print(json.dumps(prov, indent=1))
    # ---- 2) build arms on N1 legs + book-smoke
    arms_out = {}
    provs = {}
    for name, mix in ARMS.items():
        for aum in (600000, 1000000):
            W, Pv = build(mix, aum, N1, ind_map)
            fp = OUT / f"weights_{name}_{aum // 10000}w.parquet"
            W.to_parquet(fp, index=False)
            Pv.to_parquet(OUT / f"prov_{name}_{aum // 10000}w.parquet", index=False)
            sd = OUT / f"smoke_{name}_{aum // 10000}w"
            summ = run_smoke(fp, sd, str(aum))
            book = summ.get("by_capital", {}).get(str(aum), {}).get("X2/BOOK", {})
            nav_csv = sd / f"aum_{aum}/X2/BOOK/nav.csv"
            m = nav_metrics(nav_csv) if nav_csv.exists() else {}
            arms_out[f"{name}|{aum}"] = dict(arm=name, aum=aum, mix=mix, weights=str(fp.relative_to(ROOT)), sha256=sha(fp),
                                             engine=dict(cagr=book.get("cagr"), mdd=book.get("mdd"), sharpe=book.get("sharpe"),
                                                         cost_pct=book.get("cost_pct_initial"), fill_ratio=book.get("fill_ratio")),
                                             metrics244=m, nav=str(nav_csv.relative_to(ROOT)),
                                             mean_510300=float(W[W.instrument == BAL].groupby("session").weight.sum().mean()))
            print(name, aum, {k: round(v, 4) for k, v in m.items() if isinstance(v, float)}, book.get("cost_pct_initial"))
    # capacity_adv standalone (full leg, same as STRATEGY_HILIQ_CAPADV_X2) - rerun on current engine/data
    pos = OUT / "capadv_only_pos_weights.parquet"
    hx2.write_pos_weights(N1["capacity_adv"], pos)
    sd = OUT / "smoke_CAPADV_ONLY"
    summ = run_smoke(pos, sd, "600000,1000000")
    for aum in (600000, 1000000):
        book = summ.get("by_capital", {}).get(str(aum), {}).get("X2/BOOK", {})
        nav_csv = sd / f"aum_{aum}/X2/BOOK/nav.csv"
        m = nav_metrics(nav_csv)
        arms_out[f"CAPADV_ONLY|{aum}"] = dict(arm="CAPADV_ONLY", aum=aum, mix={"capacity_adv": 1.0}, weights=str(pos.relative_to(ROOT)),
                                              engine=dict(cagr=book.get("cagr"), mdd=book.get("mdd"), sharpe=book.get("sharpe"),
                                                          cost_pct=book.get("cost_pct_initial"), fill_ratio=book.get("fill_ratio")),
                                              metrics244=m, nav=str(nav_csv.relative_to(ROOT)))
        print("CAPADV_ONLY", aum, {k: round(v, 4) for k, v in m.items() if isinstance(v, float)})
    # also re-measure existing (pre-N1) B4 navs with the same 244 metric code
    for aum in (600000, 1000000):
        nav_csv = ROOT / f"output/strategy_hiliq/b4/smoke_B4_{aum // 10000}w/aum_{aum}/X2/BOOK/nav.csv"
        arms_out[f"B4_PRIOR_OLDLEGS|{aum}"] = dict(arm="B4_PRIOR_OLDLEGS", aum=aum, metrics244=nav_metrics(nav_csv),
                                                   nav=str(nav_csv.relative_to(ROOT)), note="existing 10-14 run, not rerun")
    res["arms"] = arms_out
    (OUT / "summary.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))
    print("wrote", OUT / "summary.json")


if __name__ == "__main__":
    main()
