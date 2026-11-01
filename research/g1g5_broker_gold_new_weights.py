#!/usr/bin/env python3
"""G1G5 broker_gold_new (叶16; frozen prereg 06:51:36 ET + allA supplement 07:25:11 ET). Derived from tp_rerate template.
 leaf (叶15) X2 weights. Prereg docs/v2/AI_G1G5_TP_RERATE_WHO_PAYS_PREREG_ZH.md (FROZEN 2026-10-14 06:33:06 ET).
Event: >=3 distinct orgs raise target price (max/min_price) >=20% vs own previous within 10 sessions; cooldown 60; entry weight at T1
(first session after d; engine fills next open); hold 60; reversal filter: drop if pre-event 20d adj return >= 80th pct of pool on T1.
<=20x4%; SW L1<=28%; ballast 510300. promotion_approved=false; live=false; no GP; no Book-Smoke.
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

POOL = __import__("os").environ.get("BGN_POOL", "all_a")  # all_a = primary (Leo 07:24 ET), mid_large = comparison
LEAF = "broker_gold_new_alla" if POOL == "all_a" else "broker_gold_new"
MECHANISM_TAG = "g1g5_ashare_broker_gold_new_v1" + ("_allA" if POOL == "all_a" else "")
UNIVERSE_ID = "g1g5_" + ("all_a_tradable" if POOL == "all_a" else "mid_large_top300") + "_broker_gold_new"
SCORE_N = 300
MAX_NAMES = 20
NAME_W = 0.04
IND_CAP = 0.28
BALLAST = "510300.SH"
HARD_EXCLUDE = frozenset({"600519.SH", "002371.SZ"})
WEIGHT_START, WEIGHT_END = "2024-01-02", "2026-10-09"
CAP_ADV = ROOT / "output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet"
WHO_PAYS_PREREG = "docs/v2/AI_G1G5_BROKER_GOLD_NEW_WHO_PAYS_PREREG_ZH.md" + (" + AI_G1G5_BROKER_GOLD_NEW_ALLA_SUPPLEMENT_PREREG_ZH.md" if POOL == "all_a" else "")
WHO_PAYS_ZH = (
    "券商月度金股新进：同月至少两家券商新进（上月不在该券商名单）该票，代表卖方新增共识推荐经销售渠道传导形成月初集中买盘；"
    "付钱的是不跟踪卖方月度推荐、月初被动卖出的资金；当月第2个交易日写权重、第3个交易日(T2)开盘成交，持有至当月最后一个交易日。"
)


def rss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def load_events(universe, sessions):
    """PIT monthly events per frozen count rules (research/broker_gold_new_count.py). Returns rows (inst, n_brokers, t1, t_last)."""
    import glob, unicodedata
    from research.all_a_universe_mask import universe_mask
    b = pd.concat(pd.read_parquet(f) for f in sorted(glob.glob(str(ROOT / "data/v2/tushare_raw/broker_recommend/*.parquet"))))
    b["broker"] = b.broker.astype(str).map(lambda s: unicodedata.normalize("NFKC", s).strip())
    b = b.drop_duplicates(["month", "broker", "ts_code"]); months = sorted(b.month.unique())
    sess = pd.DatetimeIndex(sessions)
    top = pd.read_parquet(ROOT / "data/v2/universe/mid_large_top300_monthly_pit.parquet")
    top = top[top.in_top300].copy(); top["av"] = pd.to_datetime(top.available_at).dt.tz_localize(None)
    conv = lambda x: x.split(".")[1] + "." + x.split(".")[0].upper()
    rows, stats = [], []
    for i, m in enumerate(months[1:], 1):
        cur = b[b.month == m]; prev = b[b.month == months[i - 1]]
        pset = set(zip(prev.broker, prev.ts_code))
        new = cur[cur.broker.isin(set(prev.broker)) & ~pd.Series(list(zip(cur.broker, cur.ts_code)), index=cur.index).isin(pset)]
        c = new.groupby("ts_code").broker.nunique(); c = c[c >= 2]
        ms = sess[(sess.year == int(m[:4])) & (sess.month == int(m[4:]))]
        if len(ms) < 3: continue
        T2 = ms[2]
        if not (pd.Timestamp("2024-01-02") <= T2 <= pd.Timestamp("2026-10-09")): continue
        if ms[0] > pd.Timestamp(WEIGHT_END): continue  # data availability (lookahead truncation)
        if POOL == "all_a":
            ua = universe_mask(T2); pool = set(ua.index[ua.in_all_a])
        else:
            snap = top[top.av <= T2 + pd.Timedelta(hours=9)]; pool = {conv(x) for x in snap[snap.month == snap.month.max()].instrument_id}
        k = 0
        for inst, n in c.items():
            if inst in HARD_EXCLUDE or inst not in pool: continue
            rows.append(dict(inst=inst, nb=int(n), t1=ms[1], tl=ms[-1], month=m)); k += 1
        stats.append(dict(month=m, n=k, pool=len(pool)))
    load_events.stats = stats
    return pd.DataFrame(rows)


def run() -> dict:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = ROOT / "output/ai_factory"
    _forbid_textbook_tokens(MECHANISM_TAG, WHO_PAYS_ZH)
    bench = _load_benchmark_closes("510300")
    cal = bench.index[(bench.index >= WEIGHT_START) & (bench.index <= WEIGHT_END)]
    cal_full = bench.index[bench.index >= "2023-09-01"]
    sw = _load_sw_members()
    ev = load_events(None, bench.index)
    universe = sorted(set(ev["inst"])) if len(ev) else []
    uni = dict(instruments=universe, anchor_session="PIT per T2", source_pit=("research/all_a_universe_mask.py" if POOL == "all_a" else "data/v2/universe/mid_large_top300_monthly_pit.parquet"))
    pos = {d: i for i, d in enumerate(cal_full)}
    n_ev, n_conf, n_rev = len(ev), len(ev), 0
    recs = []
    for r in ev.itertuples():
        if r.t1 > cal[-1]: continue
        recs.append(dict(inst=r.inst, d=r.t1, t1=r.t1, t2=r.t1, s=pos[r.t1], e=min(pos[r.tl], pos[cal[-1]] + 1), nb=r.nb,
                         typ="broker_gold_new", ind=sw_code_on(r.inst, r.t1, sw) or "_UNK"))
    E = pd.DataFrame(recs)
    gc.collect()

    decisions, prev, daily_n = [], None, []
    for dt in cal:
        i = pos[dt]
        act = E[(E["s"] <= i) & (E["e"] > i)].sort_values(["nb", "inst"], ascending=[False, True], kind="mergesort") if len(E) else E
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
    wpath = out / f"g1g5_{LEAF}_daily_weights_{stamp}.parquet"
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
        if "broker_gold_new" in k: continue
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
        note_zh="close-to-close, w(t-1)×r(t), 无成本、非正式 Book-Smoke；复权（adj_factor×X2 close；510300 close_hfq）",
    )
    # per-year
    yr = {}
    for y, g in df.groupby(df.index.year):
        X = np.c_[np.ones(len(g)), g["b"].values]
        cf, *_ = np.linalg.lstsq(X, g["e"].values, rcond=None)
        yr[str(y)] = dict(alpha_ann=float(cf[0] * 252), beta=float(cf[1]), leaf_cagr=cagr(g["e"]), bench_cagr=cagr(g["b"]))
    selfcheck["by_year"] = yr
    # pooled event stats
    ev_stats = dict(full_window_count=getattr(load_events, "stats", None), n_events_raw=n_ev, n_confirmed=n_conf, n_reversal_dropped=n_rev,
                    by_type=E["typ"].value_counts().to_dict() if len(E) else {},
                    by_year=E.groupby(E["t2"].dt.year).size().to_dict() if len(E) else {})

    # extra de-beta residual corr vs other leaves (adj prices)
    import glob as _g
    def _latest(k):
        fs = sorted(_g.glob(str(out / f"g1g5_{k}_daily_weights_*.parquet")))
        return Path(fs[-1]) if fs else None
    R_other = {"capacity_adv": r_c}
    resid_e = pd.Series(ee, index=df.index)
    rho_more = {"capacity_adv": rho}
    for k in ("report_rc_allup", "earnings_event", "analyst_recoverage", "insider_increase", "equity_incentive", "block_trade", "tp_rerate"):
        fp = _latest(k)
        if fp is None: continue
        ow = pd.read_parquet(fp, columns=["date", "instrument", "target_weight"]); ow["date"] = ow["date"].astype(str).str[:10]
        ro = leaf_ret(ow); del ow; gc.collect()
        R_other[k] = ro
        dd = pd.concat([ro.rename("o"), df["b"]], axis=1).reindex(df.index).dropna()
        X = np.c_[np.ones(len(dd)), dd["b"].values]; cf, *_ = np.linalg.lstsq(X, dd["o"].values, rcond=None)
        ro_res = pd.Series(dd["o"].values - X @ cf, index=dd.index)
        j = pd.concat([resid_e, ro_res], axis=1).dropna()
        rho_more[k] = dict(file=fp.name, rho=float(np.corrcoef(j.iloc[:, 0], j.iloc[:, 1])[0, 1]))
    selfcheck["rho_resid_vs"] = rho_more
    selfcheck["mdd_leaf"] = float(((1 + df["e"]).cumprod() / (1 + df["e"]).cumprod().cummax() - 1).min())
    selfcheck["mdd_cap"] = float(((1 + df["c"]).cumprod() / (1 + df["c"]).cumprod().cummax() - 1).min())
    selfcheck["mdd_bench"] = float(((1 + df["b"]).cumprod() / (1 + df["b"]).cumprod().cummax() - 1).min())
    # portfolio layer overlay (conc v2 topN logic, merged cap 6%, gross, adj prices) -- self-check estimate, NOT Book-Smoke
    def topn_overlay(mix, N):
        Ws = {}
        for k, m in mix.items():
            src = weights if k == "leaf" else pd.read_parquet(CAP_ADV, columns=["date", "instrument", "target_weight"])
            src = src[["date", "instrument", "target_weight"]].copy(); src["date"] = src["date"].astype(str).str[:10]
            Ws[k] = {d: g.set_index("instrument")["target_weight"] for d, g in src[src.target_weight > 0].groupby("date")}
        days = sorted(set.intersection(*[set(v) for v in Ws.values()]))
        rows = []
        for d in days:
            agg = {}
            for k, m in mix.items():
                w = Ws[k][d] * m
                isetf = np.array([i[:2] in ("51", "56", "58", "15") for i in w.index])
                for i, v in w[isetf].items(): agg[i] = agg.get(i, 0) + v
                st = w[~isetf]
                if len(st):
                    keep = st.sort_values(ascending=False, kind="mergesort").head(N); keep = keep * st.sum() / keep.sum()
                    for i, v in keep.items(): agg[i] = agg.get(i, 0) + v
            for i in list(agg):
                if i[:2] not in ("51", "56", "58", "15") and agg[i] > 0.06:
                    agg[BALLAST] = agg.get(BALLAST, 0) + agg[i] - 0.06; agg[i] = 0.06
            t = sum(agg.values()); rows += [(d, i, v / t) for i, v in agg.items()]
        return pd.DataFrame(rows, columns=["date", "instrument", "target_weight"])
    port = {}
    for aum, N in (("60w", 6), ("100w", 10)):
        for name, mix in (("cap_only", {"cap": 1.0}), ("cap80_leaf20", {"cap": .8, "leaf": .2}), ("cap70_leaf30", {"cap": .7, "leaf": .3})):
            W = topn_overlay(mix, N); r = leaf_ret(W).reindex(df.index).dropna(); del W; gc.collect()
            nav = (1 + r).cumprod()
            port[f"{aum}_{name}"] = dict(cagr=cagr(r), mdd=float((nav / nav.cummax() - 1).min()),
                                        sharpe=float(r.mean() / r.std() * np.sqrt(252)), n=int(len(r)))
    for aum in ("60w", "100w"):
        base = port[f"{aum}_cap_only"]
        for nm in ("cap80_leaf20", "cap70_leaf30"):
            p = port[f"{aum}_{nm}"]; p["beats_cap_cagr"] = p["cagr"] > base["cagr"]; p["beats_cap_mdd"] = p["mdd"] > base["mdd"]
    port["verdict_80_20_both_tiers"] = bool(all(port[f"{a}_cap80_leaf20"]["beats_cap_cagr"] and port[f"{a}_cap80_leaf20"]["beats_cap_mdd"] for a in ("60w", "100w")))
    port["note_zh"] = "自检估计：conc v2 topN（60万 N=6/100万 N=10，合并单名≤6%），毛、无成本、复权、w(t-1)×r(t)；非 Book-Smoke"
    selfcheck["portfolio_layer"] = port

    ledger = JsonlDebateLedger(out / f"debate_ledger_g1g5_{LEAF}_{stamp}.jsonl")
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
    mp = out / f"g1g5_{LEAF}_run_meta_{stamp}.json"
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
