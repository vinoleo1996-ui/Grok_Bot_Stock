#!/usr/bin/env python3
"""capacity_adv negative-event pruning (left-tail cut), research-grade X2 weights.

Prereg: docs/v2/AI_G1G5_CAPACITY_ADV_NEGEVENT_WHO_PAYS_PREREG_ZH.md
Base = capacity_adv daily weights 20261013_111219; pruned weight -> 510300.SH. No new buys.
promotion_approved=false; live=false; no GP; no Book-Smoke self-run; no uvicorn.
"""
from __future__ import annotations

import gc, json, resource, sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.dataset as pads

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from quantlab.intel.debate_ledger import JsonlDebateLedger  # noqa: E402
from research.ai_debate_memory_runner import _load_benchmark_closes  # noqa: E402
from research.g1g5_wiring import COLUMN_CONTRACT_VERSION, HARD_GATE_VERSION  # noqa: E402
from research.g1g5_expand_g6 import month_end_sessions, run_g6_lookahead_proof  # noqa: E402
from research.g1g5_x2_panel_stitch import load_panel_features_x2, clear_caches  # noqa: E402
from research.g1g5_nontextbook_weights import _forbid_textbook_tokens  # noqa: E402
from research.g1g5_low_turnover_weights import estimate_daily_turnover  # noqa: E402
import research.g1g5_moneyflow_resid_weights as mf  # noqa: E402

MECHANISM_TAG = "g1g5_ashare_capacity_adv_negevent_v1"
BALLAST = "510300.SH"
HARD_EXCLUDE = {"600519.SH", "002371.SZ"}
CAP_ADV = ROOT / "output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet"
PREREG = "docs/v2/AI_G1G5_CAPACITY_ADV_NEGEVENT_WHO_PAYS_PREREG_ZH.md"
WHO_PAYS_ZH = ("负事件供给/信息冲击承担方：限售解禁前后抛压、减持公告、业绩预亏预减、立案处罚/ST风险窗口内仍持有者；"
               "以capacity_adv为基底，窗口内置零转510300，不新增买入，只剪左尾。")
EVENTS = [ROOT / "data/v2/events/announcements_classified_pit.parquet",
          ROOT / "data/v2/events/announcements_classified_pit_post202406.parquet"]
SF = ROOT / "data/v2/share_float/share_float_pit.parquet"
SF_TYPES = ["首发原始股", "定增股份", "公开增发一般股份", "股权分置限售股份", "其他类型"]
WIN = dict(E2=10, E3=20, E4=20)
E1_PRE, E1_POST, E1_MIN_RATIO = 5, 2, 1.0


def rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def run():
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = ROOT / "output/ai_factory"
    _forbid_textbook_tokens(MECHANISM_TAG, WHO_PAYS_ZH)
    base = pd.read_parquet(CAP_ADV)
    names = sorted(set(base["instrument"]) - {BALLAST})
    bench = _load_benchmark_closes("510300")
    cal = pd.DatetimeIndex(sorted(pd.to_datetime(base["date"].unique())))
    calx = bench.index[(bench.index >= "2023-10-01")]
    pos = {d: i for i, d in enumerate(calx)}
    W = base.pivot_table(index="date", columns="instrument", values="target_weight", aggfunc="sum").fillna(0.0)
    W.index = pd.to_datetime(W.index)
    W = W.reindex(cal)

    # ---- events -> windows [s, e] inclusive positions in calx
    wins = []
    def t1pos(d):
        return int(calx.searchsorted(d, side="right"))
    a = pd.concat([pd.read_parquet(p, columns=["instrument", "event_type", "available_at", "ann_title"],
                                   filters=[("instrument", "in", names)]) for p in EVENTS], ignore_index=True)
    a["d"] = a["available_at"].dt.tz_localize(None).dt.normalize()
    a = a[a["d"] >= "2023-10-01"]
    t = a["ann_title"].fillna("")
    m2 = (a["event_type"] == "insider_decrease") & ~t.str.contains("完毕|结果|终止|可转换公司债券|不减持|未减持|届满|进展")
    m3 = (a["event_type"] == "earnings_miss") & ~t.str.contains("更正|补充|摘要|英文")
    m4 = (((a["event_type"] == "penalty") & t.str.contains("立案|行政处罚|处罚事先告知|纪律处分") & ~t.str.contains("不存在"))
          | (t.str.contains("风险警示|终止上市风险") & ~t.str.contains("撤销")))
    for tag, mk in (("E2", m2), ("E3", m3), ("E4", m4)):
        for r in a[mk].drop_duplicates(["instrument", "d"]).itertuples():
            s = t1pos(r.d)
            wins.append((r.instrument, s, s + WIN[tag] - 1, tag))
    del a; gc.collect()
    sf = pads.dataset(SF).to_table(columns=["ts_code", "float_date", "float_ratio", "share_type", "available_at"],
                                   filter=pads.field("ts_code").isin(names) & pads.field("share_type").isin(SF_TYPES)
                                   & (pads.field("float_date") >= "20231001")).to_pandas()
    sf["fd"] = pd.to_datetime(sf["float_date"])
    sf["av"] = sf["available_at"].dt.tz_localize(None).dt.normalize()
    g = sf.groupby(["ts_code", "fd"]).agg(ratio=("float_ratio", "sum"), av=("av", "min")).reset_index()
    g = g[g["ratio"] >= E1_MIN_RATIO]
    n_e1_late = 0
    for r in g.itertuples():
        F = int(calx.searchsorted(r.fd, side="left"))
        s, e = F - E1_PRE, F + E1_POST
        s = max(s, t1pos(r.av))  # PIT: only after announcement available
        if s > e:
            n_e1_late += 1; continue
        wins.append((r.ts_code, s, e, "E1"))
    del sf; gc.collect()
    WN = pd.DataFrame(wins, columns=["inst", "s", "e", "tag"])

    # ---- apply mask
    mask = pd.DataFrame(False, index=cal, columns=W.columns)
    tagmask = {k: pd.DataFrame(False, index=cal, columns=W.columns) for k in ("E1", "E2", "E3", "E4")}
    cpos = np.array([pos[d] for d in cal])
    for r in WN.itertuples():
        if r.inst not in mask.columns:
            continue
        sel = (cpos >= r.s) & (cpos <= r.e)
        if sel.any():
            mask.loc[sel, r.inst] = True
            tagmask[r.tag].loc[sel, r.inst] = True
    mask[BALLAST] = False
    held = W > 0
    cut = mask & held
    Wn = W.where(~cut, 0.0)
    Wn[BALLAST] = Wn[BALLAST] + (W - Wn).sum(axis=1)
    assert np.allclose(Wn.sum(axis=1), 1.0, atol=1e-6) and (Wn.values >= -1e-12).all()
    for b in HARD_EXCLUDE:
        assert b not in Wn.columns or Wn[b].max() <= 0

    # ---- long table
    L = Wn.stack().rename("target_weight").reset_index()
    L.columns = ["date", "instrument", "target_weight"]
    L["date"] = L["date"].dt.strftime("%Y-%m-%d")
    meta_cols = base.drop_duplicates("instrument").set_index("instrument")
    L["mechanism_tag"] = MECHANISM_TAG
    L["who_pays_zh"] = WHO_PAYS_ZH
    L["universe_id"] = base["universe_id"].iloc[0]
    L["session"] = L["date"]
    L["instrument_id"] = L["instrument"].map(meta_cols["instrument_id"])
    L["weight"] = L["target_weight"]
    L = L.sort_values(["date", "instrument"]).reset_index(drop=True)
    wpath = out / f"g1g5_capacity_adv_negevent_daily_weights_{stamp}.parquet"
    L.to_parquet(wpath, index=False)

    # ---- returns
    cl = {}
    for inst in W.columns:
        if inst == BALLAST:
            cl[inst] = bench
        else:
            cl[inst] = pd.to_numeric(load_panel_features_x2(inst)["close"], errors="coerce"); clear_caches()
    C = pd.DataFrame(cl).reindex(cal)
    R = C.pct_change(fill_method=None).fillna(0.0)
    def port(Wx):
        return (Wx.shift(1) * R).sum(axis=1).iloc[1:]
    rc, rn = port(W), port(Wn)
    rb = R[BALLAST].iloc[1:]
    cagr = lambda r: float((1 + r).prod() ** (252 / len(r)) - 1)
    mdd = lambda r: float(((1 + r).cumprod() / (1 + r).cumprod().cummax() - 1).min())
    def debeta(y):
        X = np.c_[np.ones(len(y)), rb.values]; cf, *_ = np.linalg.lstsq(X, y.values, rcond=None); return cf
    ac, bc = debeta(rc); an, bn = debeta(rn)
    diff = rn - rc
    exr = R.sub(R[BALLAST], axis=0)
    cutw = (W - Wn).where(cut, 0.0)
    # left tail: next-day excess of pruned names, weighted by pruned weight (that is exactly what we avoided)
    avoided = (cutw.shift(1) * exr).iloc[1:].drop(columns=[BALLAST])
    ex_cut = exr.shift(-1)[cut].stack()  # per pruned (name,day) next-day excess vs 510300
    per_tag = {}
    for k, tm in tagmask.items():
        c = tm & held
        s = exr.shift(-1)[c].stack()
        per_tag[k] = dict(n_name_days=int(c.values.sum()), mean_next_day_excess_bp=float(s.mean() * 1e4) if len(s) else None,
                          ann_contrib_est=float(((W.where(c, 0).shift(1) * exr).sum(axis=1).mean()) * 252))
    # window-level: cumulative excess over each pruned window
    wl = []
    for r in WN.itertuples():
        if r.inst not in W.columns: continue
        sel = (cpos >= r.s) & (cpos <= r.e)
        days = cal[sel]
        if len(days) == 0 or not held.loc[days, r.inst].any(): continue
        wl.append((r.tag, float((1 + exr.loc[days, r.inst]).prod() - 1)))
    wl = pd.DataFrame(wl, columns=["tag", "cumex"])
    tow_c, tow_n = estimate_daily_turnover(base), estimate_daily_turnover(L)
    yr = {}
    for y in sorted(set(rc.index.year)):
        yr[str(y)] = dict(cap=cagr(rc[rc.index.year == y]), neg=cagr(rn[rn.index.year == y]))
    selfcheck = dict(
        cagr_cap=cagr(rc), cagr_neg=cagr(rn), cagr_bench=cagr(rb), mdd_cap=mdd(rc), mdd_neg=mdd(rn),
        alpha_ann_cap=float(ac * 252), beta_cap=float(bc), alpha_ann_neg=float(an * 252), beta_neg=float(bn),
        diff_ann_mean=float(diff.mean() * 252), diff_ann_vol=float(diff.std() * np.sqrt(252)),
        corr_debeta_resid=float(np.corrcoef(rc - bc * rb, rn - bn * rb)[0, 1]),
        by_year=yr,
        cut_name_days=int(cut.values.sum()), held_name_days=int(held.drop(columns=[BALLAST]).values.sum()),
        cut_days_any=int(cut.any(axis=1).sum()), n_days=len(cal),
        cut_weight_share_mean=float(cutw.sum(axis=1).mean()), cut_weight_share_max=float(cutw.sum(axis=1).max()),
        cut_weight_share_of_stock=float(cutw.sum(axis=1).sum() / W.drop(columns=[BALLAST]).sum(axis=1).sum()),
        ballast_mean_cap=float(W[BALLAST].mean()), ballast_mean_neg=float(Wn[BALLAST].mean()),
        pruned_next_day_excess_mean_bp=float(ex_cut.mean() * 1e4),
        avoided_contrib_ann=float(avoided.sum(axis=1).mean() * 252),
        window_cum_excess=dict(n=int(len(wl)), mean=float(wl["cumex"].mean()), median=float(wl["cumex"].median()),
                               by_tag=wl.groupby("tag")["cumex"].agg(["count", "mean", "median"]).to_dict("index")),
        per_tag=per_tag, n_e1_dropped_announced_late=n_e1_late,
        n_windows=WN["tag"].value_counts().to_dict(),
        note_zh="close-to-close w(t-1)×r(t)，无成本，raw close（同 X2 stitch），非正式 Book-Smoke",
    )
    # Jaccard vs priors
    rebal = month_end_sessions(str(cal[0].date()), str(cal[-1].date()))
    vs = mf._jaccard_vs_priors(L, set(names), rebal)
    hard_rej = [k for k, v in vs.items() if v.get("hard_reject_isomorph") and k != "capacity_adv"]
    ledger = JsonlDebateLedger(out / f"debate_ledger_g1g5_capacity_adv_negevent_{stamp}.jsonl")
    g6 = run_g6_lookahead_proof(ledger)
    meta = dict(mechanism_tag=MECHANISM_TAG, who_pays_zh=WHO_PAYS_ZH, prereg=PREREG, base=str(CAP_ADV.relative_to(ROOT)),
                weights_path=str(wpath.relative_to(ROOT)), rows=len(L), n_dates=int(L["date"].nunique()),
                n_instruments=int(L["instrument"].nunique()), date_span=[L["date"].min(), L["date"].max()],
                daily_sum_min=float(Wn.sum(axis=1).min()), daily_sum_max=float(Wn.sum(axis=1).max()),
                min_weight=float(Wn.values.min()), stub=False,
                turnover_cap=tow_c, turnover_neg=tow_n, selfcheck=selfcheck, jaccard=vs, hard_reject_isomorph=hard_rej,
                g6=g6.get("G6"), g6_proof=g6, peak_rss_mb=round(rss_mb(), 1),
                column_contract_version=COLUMN_CONTRACT_VERSION, hard_gate_version=HARD_GATE_VERSION,
                promotion_approved=False, live=False, no_gp=True, no_book_smoke_self=True)
    mp = out / f"g1g5_capacity_adv_negevent_run_meta_{stamp}.json"
    mp.write_text(json.dumps(meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    meta["meta_path"] = str(mp.relative_to(ROOT))
    return meta


if __name__ == "__main__":
    m = run()
    print(json.dumps({k: m[k] for k in ("weights_path", "meta_path", "rows", "n_dates", "n_instruments", "turnover_cap",
                                        "turnover_neg", "selfcheck", "hard_reject_isomorph", "g6", "peak_rss_mb")},
                     ensure_ascii=False, indent=1, default=str))
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if "jaccard" in kk or "hard" in kk} for k, v in m["jaccard"].items()}, ensure_ascii=False))
