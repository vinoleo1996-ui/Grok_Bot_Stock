"""Alpha full-A re-judge harness (research-grade; no GP; no Book-Smoke; promotion/live=false).

Universe is NOT defined here. Strategy freezes it; this script only consumes a mask file
(parquet/csv with columns date, instrument, in_universe) and recomputes on the new basis
(net 17.5bp/unit TO, T+1 next_open fills, 244-day annualisation):
  - IC/ICIR, both readings (full-sample ICIR + rolling-252 median ICIR), style-residualised (SW L1/log float mcap/rolling beta)
  - residual-correlation (orthogonality) matrix across all books
  - CMC (docs/v2/ALPHA_LEAF_ACCEPT_V2_PREREG_ZH.md §1) for leaves 11–15
  - decay gate v1.1 (research/alpha_decay_gate_v1_1.py)
  - GATE_V3 (docs/v2/GATE_V3_MDD25_PREREG_ZH.md): cap80+leaf20, topN 6/10, name<=6%, vs capacity_adv alone same basis
Weights: defaults are the pinned top300 packs; for full A pass --weights JSON {book: path} with AI-regenerated packs.
--apply-mask moves stock weight outside the mask into 510300 (diagnostic only; real full-A packs must be regenerated).
Usage: python3 research/alpha_fullA_rejudge.py --mask M.parquet --out OUT.json [--weights W.json] [--apply-mask] [--books a,b] [--skip ic,ortho,cmc,decay,gate]
       python3 research/alpha_fullA_rejudge.py --make-top300-mask PATH   (smoke helper: current anchor top300 ∩ PIT members)
"""
from __future__ import annotations
import sys, json, argparse
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import research.alpha_combo_marginal as ACM
import research.leaf_selfcheck_common as LC
import research.alpha_decay_gate_v1_1 as D11

AF = "output/ai_factory/"
DEFAULT_W = {
    "capacity_adv": AF + "g1g5_capacity_adv_daily_weights_paper_20261013_r2.parquet",
    "earnings_event": AF + "g1g5_earnings_event_daily_weights_20261014_111825.parquet",
    "insider_increase": AF + "g1g5_insider_increase_daily_weights_20261014_111825.parquet",
    "equity_incentive": AF + "g1g5_equity_incentive_daily_weights_20261014_135031.parquet",
    "B4_60w": "output/small_aum_concentration/v2/B_B4_50_25_25_topN_60w_20261013_r2.parquet",
    "B4_100w": "output/small_aum_concentration/v2/B_B4_50_25_25_topN_100w_20261013_r2.parquet",
    "report_rc_allup": AF + "g1g5_report_rc_allup_daily_weights_20261014_122118.parquet",
    "analyst_recoverage": AF + "g1g5_analyst_recoverage_daily_weights_20261014_122813.parquet",
    "stk_surv": AF + "g1g5_stk_surv_daily_weights_20261014_172311.parquet",
    "insurer_surv": AF + "g1g5_insurer_surv_daily_weights_20261014_175849.parquet",
    "tp_rerate": AF + "g1g5_tp_rerate_daily_weights_20261014_183329.parquet",
}
CAP_GATE = AF + "g1g5_capacity_adv_daily_weights_20261013_111219.parquet"  # GATE_V3 core (same as leaf_selfcheck_common)
LEAVES = ["report_rc_allup", "analyst_recoverage", "stk_surv", "insurer_surv", "tp_rerate"]
LEAF_NO = dict(zip(LEAVES, range(11, 16)))


def load_mask(p) -> dict:
    p = Path(p); m = pd.read_parquet(p) if p.suffix == ".parquet" else pd.read_csv(p)
    assert {"date", "instrument", "in_universe"} <= set(m.columns), "mask needs date, instrument, in_universe"
    m = m[m.in_universe.astype(bool)]; m["date"] = m["date"].astype(str).str[:10]
    return {d: set(g.instrument) for d, g in m.groupby("date")}


def install_mask(M: dict):
    """Replace ACM's universe (anchor top300 ∩ PIT members) by the mask; rest of ctx() identical."""
    U = sorted(set().union(*M.values()))
    import research.g1g5_moneyflow_resid_weights as mf
    orig_sel, orig_mem = mf.select_mid_large_topn_light, mf.load_pit_member_index_light
    mf.select_mid_large_topn_light = lambda top_n=300: {"instruments": U}
    mf.load_pit_member_index_light = lambda U_, days: {d: M.get(d, set()) for d in days}
    ACM._CTX.clear(); ACM._B0.clear()
    return orig_sel, orig_mem


def masked_weights(path, M, apply) -> tuple[str, float]:
    """Return (path_to_use, mean stock weight outside mask). With apply, writes a masked copy (excess → 510300)."""
    d = pd.read_parquet(path, columns=["date", "instrument", "target_weight"]); d["date"] = d["date"].astype(str).str[:10]
    st = ~d.instrument.map(LC.etf)
    out_ = d[st & ~d.apply(lambda r: r.instrument in M.get(r.date, ()), axis=1)] if len(M) else d.iloc[:0]
    frac = float(out_.groupby("date").target_weight.sum().reindex(d.date.unique()).fillna(0).mean())
    if not apply or frac == 0: return str(path), frac
    keep = d.drop(out_.index); add = out_.groupby("date").target_weight.sum().reset_index().assign(instrument=LC.BAL)
    nd = pd.concat([keep, add]).groupby(["date", "instrument"], as_index=False).target_weight.sum()
    q = ROOT / "output/alpha/fullA_masked" / Path(path).name; q.parent.mkdir(parents=True, exist_ok=True); nd.to_parquet(q)
    return str(q), frac


def ic_block(W):
    out, Z = {}, {}
    for k, p in W.items():
        Z[k] = ACM.resid_z(ACM.sig(ROOT / p)); out[k] = ACM.ic_stats(Z[k])
    return out, Z


def ortho(Z):
    ks = list(Z); Mx = pd.DataFrame(np.nan, ks, ks)
    for a in ks:
        for b in ks:
            if a <= b:
                v = np.nanmean([Z[a].loc[d].corr(Z[b].loc[d]) for d in Z[a].index]); Mx.loc[a, b] = Mx.loc[b, a] = round(float(v), 4)
    return Mx.to_dict()


def cmc_block(W):
    ACM.LEGS.update({k: ROOT / W[k] for k in ("capacity_adv", "earnings_event", "insider_increase")}); ACM._B0.clear()
    import research.leaf_selfcheck_v3 as V3
    V3.TRACKS["B4"].update({"60w": ROOT / W["B4_60w"], "100w": ROOT / W["B4_100w"]})
    orig = V3.wfile; res = {}
    for l in LEAVES:
        V3.wfile = lambda leaf, _p=ROOT / W[l]: _p
        try: res[l] = ACM.cmc(l)
        finally: V3.wfile = orig
        res[l].pop("definition_notes", None)
    return res


def _m(r):
    x = LC._m(r); x["win_day"] = float((r > 0).mean()); mo = (1 + r).resample("ME").prod() - 1; x["win_month"] = float((mo > 0).mean()); return x


def gate_block(W, decay):
    LC.CAP_ADV = ROOT / W.get("capacity_adv_gate", CAP_GATE); base, res = {}, {}
    for l in LEAVES:
        p = ROOT / W[l]; g, to = D11.gross_and_turnover(p); tiers = {}
        for t, N in (("60w", 6), ("100w", 10)):
            if t not in base: LC.WMIX.clear(); LC.WMIX.update(cap=1.0); base[t] = LC._ret(LC._overlay({"cap": LC.CAP_ADV}, N))
            LC.WMIX.clear(); LC.WMIX.update(cap=0.8, leaf=0.2); ro = LC._ret(LC._overlay({"cap": LC.CAP_ADV, "leaf": p}, N))
            ix = base[t].index.intersection(ro.index); a, b = _m(base[t][ix]), _m(ro[ix])
            tiers[t] = dict(cap=a, combo=b, mdd_le_25=b["mdd"] >= -0.25, cagr_gt_cap=b["cagr"] > a["cagr"], span=[str(ix[0].date()), str(ix[-1].date())])
        cond = dict(mdd=all(tiers[t]["mdd_le_25"] for t in tiers), cagr=all(tiers[t]["cagr_gt_cap"] for t in tiers),
                    decay=decay.get(l, {}).get("outcome") == "KEEP", tradable=float(to.mean()) <= 0.20)
        res[l] = dict(leaf_no=LEAF_NO[l], tiers=tiers, turnover_2s=float(to.mean()), conditions=cond, local="PASS" if all(cond.values()) else "FAIL",
                      note="本地估计；终判以 Eng X2 为准（叶11 X2=FAIL 有约束力）")
    return res


def make_top300_mask(path):
    c = ACM.ctx(); rows = [(d.strftime("%Y-%m-%d"), i, True) for d in c["ev"] for i in c["U"] if i in c["mem"].get(d.strftime("%Y-%m-%d"), set())]
    pd.DataFrame(rows, columns=["date", "instrument", "in_universe"]).to_parquet(path); print("mask rows", len(rows))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--mask"); ap.add_argument("--out"); ap.add_argument("--weights"); ap.add_argument("--apply-mask", action="store_true")
    ap.add_argument("--books"); ap.add_argument("--skip", default=""); ap.add_argument("--make-top300-mask")
    a = ap.parse_args()
    if a.make_top300_mask: return make_top300_mask(a.make_top300_mask)
    W = dict(DEFAULT_W); W.update(json.load(open(a.weights)) if a.weights else {})
    M = load_mask(a.mask); skip = set(filter(None, a.skip.split(",")))
    cov = {}
    for k in list(W):
        if k == "capacity_adv_gate": continue
        W[k], cov[k] = masked_weights(ROOT / W[k], M, a.apply_mask)
    install_mask(M)
    out = dict(mask=a.mask, n_days=len(M), mean_names=float(np.mean([len(v) for v in M.values()])), weights=W, out_of_mask_weight_mean=cov,
               basis="net 17.5bp×TO, T+1 next_open, 244d", promotion_approved=False, live=False, paper=False)
    sigW = {k: W[k] for k in W if k not in ("B4_60w", "B4_100w", "capacity_adv_gate")}
    if "ic" not in skip or "ortho" not in skip:
        ic, Z = ic_block(sigW); out["ic"] = ic
        if "ortho" not in skip: out["ortho_resid_corr"] = ortho(Z)
    if "cmc" not in skip: out["cmc"] = cmc_block(W)
    dec = {}
    if "decay" not in skip:
        for k in [x for x in W if x != "capacity_adv_gate"]:
            dec[k] = D11.evaluate_weights(ROOT / W[k]); dec[k]["flag_only"] = k in ("capacity_adv", "B4_60w", "B4_100w")
        out["decay_v11"] = dec
    if "gate" not in skip: out["gate_v3"] = gate_block(W, dec)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True); json.dump(out, open(a.out, "w"), ensure_ascii=False, indent=1, default=float); print("wrote", a.out)


if __name__ == "__main__":
    main()
