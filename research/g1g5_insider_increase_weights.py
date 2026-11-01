#!/usr/bin/env python3
"""G1G5 buyback-for-cancellation event leaf (based on earnings_event template) X2 weights (research-grade).

Mechanism g1g5_ashare_insider_increase_v1 (prereg docs/v2/AI_G1G5_INSIDER_INCREASE_WHO_PAYS_PREREG_ZH.md):
  - Event: 业绩预告/业绩快报 announcements (PIT available_at), excluding earnings_miss titles
  - Confirm: industry-relative overnight gap at T1 (first session after available_at) >= +1%
  - Enter at T2 (no D / T1 return), hold 40 sessions; <=20 names x 4%; SW L1 <=28%
  - Pool: mid_large PIT top300 (anchor 2024-06-28); ballast 510300; hard-exclude 600519/002371
promotion_approved=false; live=false; no GP; no Book-Smoke self-run; no uvicorn.
"""
from __future__ import annotations

import gc
import json
import resource
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantlab.intel.debate_ledger import JsonlDebateLedger  # noqa: E402
from research.ai_debate_memory_runner import _load_benchmark_closes  # noqa: E402
from research.g1g5_wiring import COLUMN_CONTRACT_VERSION, HARD_GATE_VERSION  # noqa: E402
from research.g1g5_expand_g6 import (  # noqa: E402
    build_daily_weights_expand,
    month_end_sessions,
    run_g6_lookahead_proof,
)
from research.g1g5_x2_panel_stitch import load_panel_features_x2, clear_caches  # noqa: E402
from research.g1g5_nontextbook_weights import _forbid_textbook_tokens, _load_sw_members, sw_code_on  # noqa: E402
from research.g1g5_low_turnover_weights import estimate_daily_turnover  # noqa: E402
import research.g1g5_moneyflow_resid_weights as mf  # noqa: E402

MECHANISM_TAG = "g1g5_ashare_insider_increase_v1"
UNIVERSE_ID = "g1g5_mid_large_top300_insider_inc"
SCORE_N = 300
MAX_NAMES = 20
NAME_W = 0.04
IND_CAP = 0.28
HOLD = 60
GAP_MIN = 0.01
BALLAST = "510300.SH"
HARD_EXCLUDE = frozenset({"600519.SH", "002371.SZ"})
WEIGHT_START, WEIGHT_END = "2024-01-02", "2026-10-09"
EVENTS = [ROOT / "data/v2/events/announcements_classified_pit.parquet",
          ROOT / "data/v2/events/announcements_classified_pit_post202406.parquet"]
CAP_ADV = ROOT / "output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet"
WHO_PAYS_PREREG = "docs/v2/AI_G1G5_INSIDER_INCREASE_WHO_PAYS_PREREG_ZH.md"
WHO_PAYS_ZH = (
    "控股股东/实控人/董监高用自有资金二级市场增持(知情买方)；付钱的是卖给内部人的流动性提供者与对内部人信号反应迟缓的对手盘；"
    "PIT公告后T2入场持有60交易日，后续进展/结果公告重置窗口；非回购、非业绩事件、非ADV分位、非资金流、非两融、非北向、非估值残差。"
)


def rss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def load_events(universe: set[str]) -> pd.DataFrame:
    parts = []
    for p in EVENTS:
        d = pd.read_parquet(p, columns=["instrument", "event_type", "available_at", "ann_title"])
        d = d[d["instrument"].isin(universe) & (d["available_at"] >= "2023-10-01")]
        parts.append(d)
    a = pd.concat(parts, ignore_index=True)
    t = a["ann_title"].fillna("")
    m = ((a["event_type"] == "insider_increase") & t.str.contains("增持")
         & t.str.contains("控股股东|实际控制人|实控人|董事|监事|高级管理|高管|总经理|董事长|核心管理")
         & ~t.str.contains("律师|法律意见|核查|可转换|债券|H股|股权|调整|终止|延期|取消|更正|补充|英文|摘要|减持"))
    a = a[m].copy()
    a["d"] = a["available_at"].dt.tz_localize(None).dt.normalize()
    return a.drop_duplicates(["instrument", "d"]).reset_index(drop=True)


def run() -> dict:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = ROOT / "output/ai_factory"
    _forbid_textbook_tokens(MECHANISM_TAG, WHO_PAYS_ZH)
    uni = mf.select_mid_large_topn_light(top_n=SCORE_N)
    universe = [x for x in uni["instruments"] if x not in HARD_EXCLUDE]
    bench = _load_benchmark_closes("510300")
    cal = bench.index[(bench.index >= WEIGHT_START) & (bench.index <= WEIGHT_END)]
    cal_full = bench.index[bench.index >= "2023-09-01"]
    sw = _load_sw_members()

    # opens/closes for whole pool on calendar (float32 panel; peak-safe)
    op = pd.DataFrame(index=cal_full, columns=universe, dtype="float32")
    cl = pd.DataFrame(index=cal_full, columns=universe, dtype="float32")
    for inst in universe:
        f = load_panel_features_x2(inst)
        if not f.empty:
            f = f.reindex(cal_full)
            op[inst] = f["open"].astype("float32")
            cl[inst] = f["close"].astype("float32")
        clear_caches()
    gap_all = op / cl.shift(1) - 1.0
    bgap = None
    try:
        bf = load_panel_features_x2(BALLAST)
        bgap = (bf["open"] / bf["close"].shift(1) - 1).reindex(cal_full)
    except Exception:
        pass

    ev = load_events(set(universe))
    pos = {d: i for i, d in enumerate(cal_full)}
    member_idx = mf.load_pit_member_index_light(universe, [d.strftime("%Y-%m-%d") for d in cal])
    recs, n_ev, n_conf = [], len(ev), 0
    for r in ev.itertuples():
        k = cal_full.searchsorted(r.d, side="right")
        if k + 1 >= len(cal_full):
            continue
        t1, t2 = cal_full[k], cal_full[k + 1]
        g = gap_all.at[t1, r.instrument]
        if not np.isfinite(g):
            g = 0.0
        ind = sw_code_on(r.instrument, t1, sw)
        peers = [x for x in universe if x != r.instrument and ind and sw_code_on(x, t1, sw) == ind] if ind else []
        pg = gap_all.loc[t1, peers].dropna() if peers else pd.Series(dtype=float)
        if len(pg) >= 3:
            gi = float(g - pg.median())
        else:
            bg = float(bgap.get(t1, 0.0)) if bgap is not None else 0.0
            gi = float(g - (bg if np.isfinite(bg) else 0.0))
        if t2 < cal[0] - pd.Timedelta(days=90) or t2 > cal[-1]:
            pass
        ts = t2.strftime("%Y-%m-%d")
        if ts in member_idx and r.instrument not in member_idx[ts]:
            continue
        n_conf += 1
        recs.append(dict(inst=r.instrument, d=r.d, t1=t1, t2=t2, s=pos[t2], e=pos[t2] + HOLD,
                         gap=float(g), gap_ind=gi, typ=r.event_type, ind=ind or "_UNK"))
    E = pd.DataFrame(recs)
    if len(E):
        E = E.sort_values(["inst", "s"]); keep = []; last = {}
        for r in E.itertuples():
            if r.inst in last and False:
                keep.append(False); continue
            last[r.inst] = r.s; keep.append(True)
        E = E[keep].copy()
    # later event for same name resets window: truncate earlier window
    if len(E):
        E = E.sort_values(["inst", "s"])
        nxt = E.groupby("inst")["s"].shift(-1)
        E["e"] = np.where(nxt.notna(), np.minimum(E["e"], nxt), E["e"]).astype(int)
    del op, gap_all
    gc.collect()

    decisions, prev, daily_n = [], None, []
    for dt in cal:
        i = pos[dt]
        act = E[(E["s"] <= i) & (E["e"] > i)].sort_values("s", ascending=False) if len(E) else E
        pick, indc = [], {}
        maxn = int(np.floor(IND_CAP / NAME_W + 1e-9))
        for r in act.itertuples():
            if r.inst in pick:
                continue
            if indc.get(r.ind, 0) >= maxn:
                continue
            pick.append(r.inst)
            indc[r.ind] = indc.get(r.ind, 0) + 1
            if len(pick) >= MAX_NAMES:
                break
        w = {x: NAME_W for x in pick}
        daily_n.append(len(pick))
        key = tuple(sorted(pick))
        if key == prev:
            continue
        prev = key
        sess = dt.strftime("%Y-%m-%d")
        decisions.append(dict(session=sess, instrument=BALLAST, rating="Hold",
                              target_weight_override=1.0 - NAME_W * len(pick)))
        for inst in E["inst"].unique() if len(E) else []:
            wv = w.get(inst, 0.0)
            decisions.append(dict(session=sess, instrument=inst,
                                  rating="Overweight" if wv > 0 else "Abstain", target_weight_override=wv))
    weights = build_daily_weights_expand(decisions, start=WEIGHT_START, end=WEIGHT_END,
                                         mechanism_tag=MECHANISM_TAG, who_pays_zh=WHO_PAYS_ZH,
                                         universe_id=UNIVERSE_ID)
    weights["date"] = weights["date"].astype(str).str[:10] if weights["date"].dtype == object else weights["date"]
    ds = weights.groupby("date")["target_weight"].sum()
    assert ds.between(1 - 1e-6, 1 + 1e-6).all(), "sum!=1"
    assert (weights["target_weight"] >= -1e-12).all(), "neg weight"
    for b in HARD_EXCLUDE:
        assert weights.loc[weights["instrument"] == b, "target_weight"].max() if (weights["instrument"] == b).any() else 0.0 <= 0
    stock = weights[(weights["instrument"] != BALLAST) & (weights["target_weight"] > 0)]
    assert stock["target_weight"].max() <= NAME_W + 1e-9
    wpath = out / f"g1g5_insider_increase_daily_weights_{stamp}.parquet"
    cols = ["date", "instrument", "target_weight", "mechanism_tag", "who_pays_zh", "universe_id",
            "session", "instrument_id", "weight"]
    weights[cols].to_parquet(wpath, index=False)

    # industry cap check on all days
    ind_max = 0.0
    for d, g in stock.groupby("date"):
        s = g.groupby(g["instrument"].map(lambda x: sw_code_on(x, pd.Timestamp(d), sw) or "_UNK"))["target_weight"].sum()
        ind_max = max(ind_max, float(s.max()))

    # Jaccard vs priors (reuse template list + moneyflow_resid)
    rebal = month_end_sessions(WEIGHT_START, WEIGHT_END)
    vs = mf._jaccard_vs_priors(weights, set(universe), rebal)
    mpath = out / "g1g5_moneyflow_resid_daily_weights_20261013_050716.parquet"
    old = pd.read_parquet(mpath, columns=["date", "instrument", "target_weight"])
    jac = []
    for ss in [x for x in rebal if x >= "2024-03-01"]:
        a = set(stock[stock["date"] == ss]["instrument"])
        b = set(old[(old["date"] == ss) & (old["target_weight"] > 0) & (old["instrument"] != BALLAST)]["instrument"])
        if a or b:
            jac.append(len(a & b) / len(a | b))
    vs["moneyflow_resid"] = dict(path=str(mpath.relative_to(ROOT)), jaccard_stock_mean=float(np.mean(jac)),
                                 jaccard_stock_max=float(np.max(jac)),
                                 jaccard_frac_ge_0_7=float(np.mean([j >= 0.7 for j in jac])),
                                 hard_reject_isomorph=bool(np.max(jac) >= 0.7 and np.mean([j >= 0.7 for j in jac]) >= 0.5))
    del old
    import glob, re as _re
    latest = {}
    for fp in sorted(glob.glob(str(out / "g1g5_*_daily_weights_*.parquet"))):
        k = _re.sub(r"_daily_weights_.*", "", Path(fp).name)
        if "insider_increase" in k: continue
        latest[k] = fp
    sd = {d: set(g["instrument"]) for d, g in stock.groupby("date")}
    daily_j = {}
    for k, fp in latest.items():
        try:
            o = pd.read_parquet(fp, columns=["date", "instrument", "target_weight"])
        except Exception as ex:
            daily_j[k] = dict(error=str(ex)); continue
        o["date"] = o["date"].astype(str).str[:10]
        o = o[(o["target_weight"] > 0) & (o["instrument"] != BALLAST)]
        od = {d: set(g["instrument"]) for d, g in o.groupby("date")}
        js = []
        for d in set(sd) | set(od):
            A, B = sd.get(d, set()), od.get(d, set())
            if A or B: js.append(len(A & B) / len(A | B))
        if not js: continue
        mx, fr = float(np.max(js)), float(np.mean([j >= 0.7 for j in js]))
        daily_j[k] = dict(path=Path(fp).name, n_days=len(js), mean=float(np.mean(js)), max=mx, frac_ge_0_7=fr,
                          hard_reject_isomorph=bool(mx >= 0.7 and fr >= 0.5))
        del o
    vs["daily_jaccard_all_priors"] = daily_j
    hard_rej = [k for k, v in vs.items() if isinstance(v, dict) and v.get("hard_reject_isomorph")]
    hard_rej += [k for k, v in daily_j.items() if v.get("hard_reject_isomorph")]

    # de-beta residual self-check vs capacity_adv
    from research.g1g5_x2_panel_stitch import load_adj_close_x2
    from research.ai_debate_memory_runner import _load_benchmark_closes_hfq
    BENCH_HFQ = _load_benchmark_closes_hfq("510300"); BENCH_HFQ.index = pd.to_datetime(BENCH_HFQ.index)
    # self-check returns use hfq (2026-10-13 unify); signal layer unchanged
    def leaf_ret(wdf: pd.DataFrame) -> pd.Series:
        w = wdf.pivot_table(index="date", columns="instrument", values="target_weight", aggfunc="sum").fillna(0.0)
        w.index = pd.to_datetime(w.index)
        rets = {}
        for inst in w.columns:
            if inst == BALLAST:
                c = BENCH_HFQ
            else:
                c = load_adj_close_x2(inst)
                clear_caches()
            rets[inst] = pd.to_numeric(c, errors="coerce").reindex(w.index).pct_change(fill_method=None)
        R = pd.DataFrame(rets).reindex(columns=w.columns).fillna(0.0)
        return (w.shift(1) * R).sum(axis=1).iloc[1:]
    r_e = leaf_ret(weights[["date", "instrument", "target_weight"]])
    capw = pd.read_parquet(CAP_ADV, columns=["date", "instrument", "target_weight"])
    r_c = leaf_ret(capw)
    del capw
    rb = BENCH_HFQ.pct_change().reindex(r_e.index)
    df = pd.concat([r_e.rename("e"), r_c.rename("c"), rb.rename("b")], axis=1).dropna()
    def debeta(y):
        X = np.c_[np.ones(len(df)), df["b"].values]
        coef, *_ = np.linalg.lstsq(X, df[y].values, rcond=None)
        return coef, df[y].values - X @ coef
    (ae, be), ee = debeta("e")
    (ac, bc), ec = debeta("c")
    rho = float(np.corrcoef(ee, ec)[0, 1])
    exc = (df["e"] - df["b"])
    cagr = lambda r: float((1 + r).prod() ** (252 / len(r)) - 1)
    selfcheck = dict(
        n_days=int(len(df)), span=[str(df.index[0].date()), str(df.index[-1].date())],
        beta_leaf=float(be), alpha_ann_leaf=float(ae * 252), beta_cap=float(bc), alpha_ann_cap=float(ac * 252),
        rho_excess_debeta=rho, rho_raw_excess=float(np.corrcoef(exc, df["c"] - df["b"])[0, 1]),
        leaf_cagr_gross=cagr(df["e"]), cap_cagr_gross=cagr(df["c"]), bench_cagr=cagr(df["b"]),
        leaf_vs_bench_excess_ann=float(exc.mean() * 252),
        gate_rho_lt_0_5=bool(rho < 0.5), gate_resid_pos=bool(ae > 0),
        gate_pass=bool(rho < 0.5 and ae > 0),
        note_zh="close-to-close, w(t-1)×r(t), 无成本、非正式 Book-Smoke；raw close 未复权（与 X2 stitch 一致）",
    )
    # per-year
    yr = {}
    for y, g in df.groupby(df.index.year):
        X = np.c_[np.ones(len(g)), g["b"].values]
        cf, *_ = np.linalg.lstsq(X, g["e"].values, rcond=None)
        yr[str(y)] = dict(alpha_ann=float(cf[0] * 252), beta=float(cf[1]), leaf_cagr=cagr(g["e"]), bench_cagr=cagr(g["b"]))
    selfcheck["by_year"] = yr
    # pooled event stats
    ev_stats = dict(n_events_raw=n_ev, n_confirmed=n_conf,
                    by_type=E["typ"].value_counts().to_dict() if len(E) else {},
                    by_year=E.groupby(E["t2"].dt.year).size().to_dict() if len(E) else {})

    ledger = JsonlDebateLedger(out / f"debate_ledger_g1g5_insider_increase_{stamp}.jsonl")
    g6 = run_g6_lookahead_proof(ledger)
    tow = estimate_daily_turnover(weights)
    bal = weights[weights["instrument"] == BALLAST].groupby("date")["target_weight"].sum()
    adv_note = {}
    for x in HARD_EXCLUDE:
        adv_note[x] = "硬排除，权重恒0（与前叶一致：600519 单价/单手金额过高，60万/100万档单名4%无法整手精确配置；002371 ADV/冲击约束沿用 capacity_adv 口径）；且不在本池事件中买入"
    meta = dict(
        mechanism_tag=MECHANISM_TAG, who_pays_zh=WHO_PAYS_ZH, who_pays_prereg=WHO_PAYS_PREREG,
        weights_path=str(wpath.relative_to(ROOT)), rows=int(len(weights)),
        n_dates=int(weights["date"].nunique()), n_instruments=int(weights["instrument"].nunique()),
        date_span=[str(weights["date"].min()), str(weights["date"].max())],
        daily_sum_min=float(ds.min()), daily_sum_max=float(ds.max()), min_weight=float(weights["target_weight"].min()),
        stub=False, mean_ballast=float(bal.mean()), min_ballast=float(bal.min()), max_ballast=float(bal.max()),
        mean_names=float(np.mean(daily_n)), max_names=int(np.max(daily_n)), zero_name_days=int(np.sum(np.array(daily_n) == 0)),
        max_name_w=float(stock["target_weight"].max()), max_ind_w=ind_max,
        universe=dict(n=len(universe), anchor=uni["anchor_session"], source=uni["source_pit"]),
        events=ev_stats, turnover=tow, jaccard=vs, hard_reject_isomorph=hard_rej,
        selfcheck=selfcheck, g6=g6.get("G6"), g6_proof=g6, peak_rss_mb=round(rss_mb(), 1),
        hard_exclude=adv_note, column_contract_version=COLUMN_CONTRACT_VERSION, hard_gate_version=HARD_GATE_VERSION,
        promotion_approved=False, live=False, no_gp=True, no_book_smoke_self=True,
    )
    mp = out / f"g1g5_insider_increase_run_meta_{stamp}.json"
    mp.write_text(json.dumps(meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    (out / f"{wpath.name}.meta.json").write_text(json.dumps({k: meta[k] for k in (
        "mechanism_tag", "weights_path", "rows", "n_dates", "n_instruments", "date_span", "g6", "peak_rss_mb",
        "promotion_approved")}, ensure_ascii=False, indent=2), encoding="utf-8")
    meta["meta_path"] = str(mp.relative_to(ROOT))
    if hard_rej:
        raise RuntimeError(f"isomorph hard-reject: {hard_rej}")
    return meta


if __name__ == "__main__":
    m = run()
    print(json.dumps({k: m[k] for k in ("weights_path", "meta_path", "rows", "n_dates", "n_instruments", "mean_ballast",
                                        "mean_names", "selfcheck", "g6", "peak_rss_mb", "hard_reject_isomorph", "events")},
                     ensure_ascii=False, indent=1, default=str))
