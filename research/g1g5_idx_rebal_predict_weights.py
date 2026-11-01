#!/usr/bin/env python3
"""G1G5 CSI300 rebalance PREDICT leaf v2 (research-grade).
Prereg docs/v2/AI_G1G5_IDX_REBAL_PREDICT_WHO_PAYS_PREREG_ZH.md. Predict adds after review cutoff, pre-announcement entry,
swap to actual adds after announcement, exit before effective date; rank by impact = float_mktcap/ADV20.
promotion=false; live=false; no GP; no Book-Smoke.
"""
from __future__ import annotations
import glob, json, re, resource, sys
from datetime import datetime
from pathlib import Path
import numpy as np, pandas as pd, pyarrow.dataset as ds
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from quantlab.intel.debate_ledger import JsonlDebateLedger  # noqa
from research.ai_debate_memory_runner import _load_benchmark_closes  # noqa
from research.g1g5_wiring import COLUMN_CONTRACT_VERSION, HARD_GATE_VERSION  # noqa
from research.g1g5_expand_g6 import run_g6_lookahead_proof, MID_LARGE_PIT  # noqa
from research.g1g5_x2_panel_stitch import load_panel_features_x2, clear_caches  # noqa
from research.g1g5_nontextbook_weights import _load_sw_members, sw_code_on  # noqa
from research.g1g5_low_turnover_weights import estimate_daily_turnover  # noqa

TAG = "g1g5_ashare_idx_rebal_predict_v2"; UID = "g1g5_csi300_predict_midlarge"; BAL = "510300.SH"
NW, MAXN, INDCAP = 0.04, 20, 0.28; HX = {"600519.SH", "002371.SZ"}
WS, WE = "2024-01-02", "2026-10-09"
WHO = ("沪深300被动跟踪资金须在生效前一日收盘买入调入股并支付冲击成本；本叶考察截止后按规则预测名单公告前布局，公告后换真实名单，"
       "生效前一日收盘前退出，按被动需求/成交额(冲击系数)排序；非市值排序、非资金流、非两融、非北向、非估值残差。")
CAP_ADV = ROOT / "output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet"
def rss(): return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
def ts(pid): a, b = pid.split("."); return f"{b}.{a.upper()}"

def run():
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S"); out = ROOT / "output/ai_factory"
    bench = _load_benchmark_closes("510300"); bench.index = pd.to_datetime(bench.index)
    calf = bench.index[bench.index >= "2022-01-01"]; cal = calf[(calf >= WS) & (calf <= WE)]
    pos = {d: i for i, d in enumerate(calf)}
    rc = pd.read_parquet(ROOT / "data/v2/index_members/csi_review_calendar.parquet")
    rc = rc[rc.review.isin(["2024-06", "2024-12", "2025-06", "2025-12", "2026-06"])]
    ev = pd.read_parquet(ROOT / "data/v2/index_members/index_member_events.parquet")
    ev = ev[(ev.index_code == "000300.SH") & (ev.event == "in")]
    iw = pd.read_parquet(ROOT / "data/v2/index_members/index_weight_csi300_500_1000.parquet")
    iw = iw[iw.index_code == "000300.SH"]
    db = ds.dataset(str(ROOT / "data/v2/valuation/daily_basic_full_tushare.parquet")).to_table(
        columns=["ts_code", "trade_date", "total_mv", "float_mktcap", "turnover_rate"],
        filter=ds.field("trade_date") >= pd.Timestamp("2022-04-01")).to_pandas()
    db["trade_date"] = pd.to_datetime(db.trade_date).dt.strftime("%Y%m%d")
    db["amt"] = db.turnover_rate / 100.0 * db.float_mktcap
    sw = _load_sw_members()
    batches, acc = [], {}
    for r in rc.itertuples():
        y, m = r.review.split("-"); cut = f"{y}0430" if m == "06" else f"{y}1031"
        start = str(int(cut[:4]) - 1) + cut[4:]
        win = db[(db.trade_date > start) & (db.trade_date <= cut)]
        g = win.groupby("ts_code").agg(n=("total_mv", "count"), mv=("total_mv", "mean"), amt=("amt", "mean"))
        g = g[g.n >= 0.95 * win.trade_date.nunique()]  # amended: listed ~full review year (250 impossible in 12m)
        g = g[g.amt >= g.amt.median()]
        g["rk"] = g.mv.rank(ascending=False)
        snap = iw[iw.trade_date <= cut].trade_date.max(); mem = set(iw[iw.trade_date == snap].con_code)
        pred = g[(g.rk <= 240) & ~g.index.isin(mem)].sort_values("rk").head(30).index.tolist()
        actual = sorted(set(ev[ev.review == r.review].con_code))
        hit = set(pred) & set(actual)
        acc[r.review] = dict(cutoff=cut, member_snapshot=str(snap), n_pred=len(pred), n_actual=len(actual), n_hit=len(hit),
                             precision=len(hit) / max(len(pred), 1), recall=len(hit) / max(len(actual), 1))
        cut_d = pd.Timestamp(cut); k = calf.searchsorted(cut_d, side="right")  # first session after cutoff
        entry = calf[k + 1]  # T+1 after data availability
        ann = pd.Timestamp(r.ann_date); a1 = calf[calf.searchsorted(ann, side="right")]
        eff = pd.Timestamp(r.effective_date); last = calf[calf.searchsorted(eff) - 2]
        batches.append(dict(review=r.review, entry=entry, ann1=a1, last=last, pred=pred, actual=actual))
    allnames = sorted({x for b in batches for x in b["pred"] + b["actual"]} - HX)
    sess = [d.strftime("%Y-%m-%d") for d in cal]
    t = ds.dataset(str(MID_LARGE_PIT)).to_table(columns=["session", "instrument_id"],
        filter=ds.field("session").isin(sess) & ds.field("instrument_id").isin([f"{x[-2:].lower()}.{x[:6]}" for x in allnames])).to_pandas()
    mem_ml = t.assign(i=t.instrument_id.map(ts)).groupby(t.session.astype(str).str[:10]).i.agg(set).to_dict()
    # ADV20 / float mktcap (PIT: use day before decision)
    sub = db[db.ts_code.isin(allnames)].copy(); sub["d"] = pd.to_datetime(sub.trade_date)
    A = sub.pivot_table(index="d", columns="ts_code", values="amt").reindex(calf).rolling(20, min_periods=10).mean()
    F = sub.pivot_table(index="d", columns="ts_code", values="float_mktcap").reindex(calf).ffill()
    del db
    impact = (F / A)
    rows, daily_n, phase = [], [], {}
    for d in cal:
        names, ph = [], "none"
        for b in batches:
            if b["entry"] <= d <= b["last"]:
                ph = "post_ann" if d >= b["ann1"] else "pre_ann"; names = b["actual"] if ph == "post_ann" else b["pred"]
        ds_ = d.strftime("%Y-%m-%d"); prev = calf[pos[d] - 1]
        cand = [x for x in names if x not in HX and x in mem_ml.get(ds_, set()) and x in impact.columns and np.isfinite(impact.at[prev, x])]
        cand = sorted(cand, key=lambda x: -impact.at[prev, x])
        pick, ic = [], {}
        for x in cand:
            ind = sw_code_on(x, d, sw) or "_UNK"
            if ic.get(ind, 0) >= int(INDCAP / NW + 1e-9): continue
            pick.append(x); ic[ind] = ic.get(ind, 0) + 1
            if len(pick) >= MAXN: break
        phase[ph] = phase.get(ph, 0) + 1; daily_n.append(len(pick))
        rows += [(ds_, x, NW) for x in pick] + [(ds_, BAL, 1 - NW * len(pick))]
    W = pd.DataFrame(rows, columns=["date", "instrument", "target_weight"])
    W = W.pivot(index="date", columns="instrument", values="target_weight").fillna(0.0).stack().rename("target_weight").reset_index()
    s_ = W.groupby("date").target_weight.sum(); assert s_.between(1 - 1e-9, 1 + 1e-9).all() and (W.target_weight >= 0).all()
    W["mechanism_tag"], W["who_pays_zh"], W["universe_id"], W["session"] = TAG, WHO, UID, W.date
    W["instrument_id"] = W.instrument.map(lambda x: x[-2:].lower() + "." + x[:6]); W["weight"] = W.target_weight
    wp = out / f"g1g5_idx_rebal_predict_daily_weights_{stamp}.parquet"; W.to_parquet(wp, index=False)
    nb = W[(W.instrument != BAL) & (W.target_weight > 0)]
    indmax = max([nb[nb.date == d].groupby(nb[nb.date == d].instrument.map(lambda x: sw_code_on(x, pd.Timestamp(d), sw) or "_UNK")).target_weight.sum().max() for d in nb.date.unique()] or [0])
    from research.g1g5_x2_panel_stitch import load_adj_close_x2
    from research.ai_debate_memory_runner import _load_benchmark_closes_hfq
    BENCH_HFQ = _load_benchmark_closes_hfq("510300"); BENCH_HFQ.index = pd.to_datetime(BENCH_HFQ.index)
    # self-check returns use hfq (2026-10-13 unify); signal layer unchanged
    def leaf_ret(wdf):
        w = wdf.pivot_table(index="date", columns="instrument", values="target_weight", aggfunc="sum").fillna(0.0); w.index = pd.to_datetime(w.index)
        rr = {}
        for i in w.columns:
            c = BENCH_HFQ if i == BAL else load_adj_close_x2(i); clear_caches()
            rr[i] = pd.to_numeric(c, errors="coerce").reindex(w.index).pct_change(fill_method=None)
        return (w.shift(1) * pd.DataFrame(rr).fillna(0.0)).sum(axis=1).iloc[1:]
    re_ = leaf_ret(W); rcap = leaf_ret(pd.read_parquet(CAP_ADV, columns=["date", "instrument", "target_weight"]))
    df = pd.concat([re_.rename("e"), rcap.rename("c"), BENCH_HFQ.pct_change().reindex(re_.index).rename("b")], axis=1).dropna()
    def reg(g, y):
        X = np.c_[np.ones(len(g)), g.b.values]; cf, *_ = np.linalg.lstsq(X, g[y].values, rcond=None); return cf, g[y].values - X @ cf
    (ae, be), ee = reg(df, "e"); (ac, bc), ec = reg(df, "c")
    cagr = lambda r: float((1 + r).prod() ** (252 / len(r)) - 1); mdd = lambda r: float(((1 + r).cumprod() / (1 + r).cumprod().cummax() - 1).min())
    act = df[(df.index.isin(pd.to_datetime(nb.date.unique()) + pd.Timedelta(0)))]
    yr = {str(y): dict(alpha_ann=float(reg(g, "e")[0][0] * 252), beta=float(reg(g, "e")[0][1]), leaf_cagr=cagr(g.e), bench_cagr=cagr(g.b)) for y, g in df.groupby(df.index.year)}
    # per-batch excess (leaf - bench) cumulative over active windows
    bx = {}
    for b in batches:
        g = df[(df.index > b["entry"]) & (df.index <= calf[pos[b["last"]] + 1])]
        bx[b["review"]] = dict(pre_post_excess=float((1 + g.e).prod() - (1 + g.b).prod()), n_days=len(g))
    sc = dict(n_days=len(df), beta_leaf=float(be), alpha_ann_leaf=float(ae * 252), alpha_ann_cap=float(ac * 252), beta_cap=float(bc),
              rho_excess_debeta=float(np.corrcoef(ee, ec)[0, 1]), rho_raw_excess=float(np.corrcoef(df.e - df.b, df.c - df.b)[0, 1]),
              leaf_cagr_gross=cagr(df.e), leaf_mdd_gross=mdd(df.e), bench_cagr=cagr(df.b), bench_mdd=mdd(df.b), cap_cagr_gross=cagr(df.c),
              excess_ann=float((df.e - df.b).mean() * 252), by_year=yr, by_batch_excess=bx, note_zh="无成本 close-to-close，未复权收盘")
    sc["gate_pass"] = bool(sc["rho_excess_debeta"] < 0.5 and ae > 0)
    sd = {d: set(g.instrument) for d, g in nb.groupby("date")}; dj = {}
    lat = {}
    for fp in sorted(glob.glob(str(out / "g1g5_*_daily_weights_*.parquet"))):
        k = re.sub(r"_daily_weights_.*", "", Path(fp).name)
        if "idx_rebal_predict" not in k: lat[k] = fp
    for k, fp in lat.items():
        o = pd.read_parquet(fp, columns=["date", "instrument", "target_weight"]); o["date"] = o.date.astype(str).str[:10]
        o = o[(o.target_weight > 0) & (o.instrument != BAL)]; od = {d: set(g.instrument) for d, g in o.groupby("date")}
        js = [len(sd.get(d, set()) & od.get(d, set())) / len(sd.get(d, set()) | od.get(d, set())) for d in set(sd) | set(od) if sd.get(d) or od.get(d)]
        both = [len(sd[d] & od[d]) / len(sd[d] | od[d]) for d in set(sd) & set(od)]
        if js: dj[k] = dict(max=float(max(js)), mean=float(np.mean(js)), frac_ge_0_7=float(np.mean([x >= 0.7 for x in js])),
                            both_active_days=len(both), both_active_mean=float(np.mean(both)) if both else None,
                            hard_reject=bool(max(js) >= 0.7 and np.mean([x >= 0.7 for x in js]) >= 0.5))
    hard = [k for k, v in dj.items() if v["hard_reject"]]
    g6 = run_g6_lookahead_proof(JsonlDebateLedger(out / f"debate_ledger_g1g5_idx_rebal_predict_{stamp}.jsonl"))
    bal = W[W.instrument == BAL].groupby("date").target_weight.sum()
    meta = dict(mechanism_tag=TAG, prereg="docs/v2/AI_G1G5_IDX_REBAL_PREDICT_WHO_PAYS_PREREG_ZH.md", weights_path=str(wp.relative_to(ROOT)),
                rows=len(W), n_dates=int(W.date.nunique()), n_instruments=int(W.instrument.nunique()), stub=False,
                min_weight=float(W.target_weight.min()), max_name_w=float(nb.target_weight.max()), max_ind_w=float(indmax),
                mean_ballast=float(bal.mean()), active_days=int((np.array(daily_n) > 0).sum()), mean_names_active=float(np.mean([x for x in daily_n if x > 0])),
                phase_days=phase, prediction_accuracy=acc, batches=[{k: str(v) if not isinstance(v, list) else len(v) for k, v in b.items()} for b in batches],
                turnover=estimate_daily_turnover(W), jaccard_daily=dj, hard_reject_isomorph=hard, selfcheck=sc, g6=g6.get("G6"), peak_rss_mb=round(rss(), 1),
                column_contract_version=COLUMN_CONTRACT_VERSION, hard_gate_version=HARD_GATE_VERSION, promotion_approved=False, live=False, no_gp=True)
    mp = out / f"g1g5_idx_rebal_predict_run_meta_{stamp}.json"; mp.write_text(json.dumps(meta, ensure_ascii=False, indent=1, default=str))
    (out / f"{wp.name}.meta.json").write_text(json.dumps({k: meta[k] for k in ("mechanism_tag", "weights_path", "rows", "n_dates", "n_instruments", "g6", "peak_rss_mb", "promotion_approved")}, ensure_ascii=False))
    meta["meta_path"] = str(mp.relative_to(ROOT)); return meta

if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=1, default=str))
