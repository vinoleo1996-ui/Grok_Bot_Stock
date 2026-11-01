#!/usr/bin/env python3
"""Reconcile original-repo 50-name smallcap basket vs V2 strict static smallcap (one factor at a time).

Research-only; promotion_approved=false. Fixed spec choices; no tuning on 2018-01..2024-05 (pre-registered dev window).
Usage: scripts/smallcap_reconcile.py ladder | final
"""
from __future__ import annotations

import json, math, sys, time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "output/v2_proto/smallcap_reconcile"
CAP = 5_000_000.0
EVERY = 20


def log(*a):
    print(f"[reconcile {time.strftime('%H:%M:%S')}]", *a, flush=True)


# ---------------- selector with knobs ----------------
def make_selector():
    from quantlab.beta.smallcap_history_selector import daily_basic_panels, st_on, industry_on
    from quantlab.beta.smallcap_sleeve import _load_audit_annual, _priority, load_smallcap_config
    from quantlab.beta.survivorship import load_full_market_float_mktcap, load_delisted_master
    cfg = load_smallcap_config()
    fm = load_full_market_float_mktcap(); P = daily_basic_panels(); M = load_delisted_master()
    amt = P["amt_proxy"]
    adv60 = amt.where(amt > 0).rolling(60, min_periods=40).mean()
    au = _load_audit_annual("data/v2/audit/audit_opinion_pit_tushare.parquet")

    def select(day, prev, k):
        idx = fm.index[fm.index <= day]; day = idx[-1]; t = len(idx) - 1
        if k["band"] == "cap":
            score = fm.iloc[max(0, t - 19): t + 1].mean(skipna=True).dropna()
        else:  # ADV band (original): 60d mean traded amount (daily_basic proxy)
            dbi = adv60.index[adv60.index <= day]
            score = adv60.loc[dbi[-1]].dropna(); score = score[score.index.isin(fm.columns[fm.loc[day].notna()])]
        if k.get("survivor_only"):
            dead = set(M.index[M["delist_date"] <= pd.Timestamp(k["end"])])
            score = score[~score.index.isin(dead)]
        if k.get("st_pre"):
            score = score[~score.index.isin(st_on(day))]
        n = len(score); r = score.sort_values(ascending=False)
        band = list(r.index[3000:5000]) if n >= 5000 else list(r.index[math.ceil(0.6 * n):])
        hist_n = fm.iloc[: t + 1][band].notna().sum()
        min_hist = min(253, max(60, t + 1 - 20))
        dbi = P["close"].index[P["close"].index <= day]; dd = dbi[-1]
        close = P["close"].loc[dd]; pe = P["pe_ttm"].loc[dd]; pb = P["pb"].loc[dd]; adv = adv60.loc[dd]
        st = st_on(day) if k.get("excl") else set()
        if k.get("excl"):
            v = au[(au["avail_date"] < day) & (au["end_date"].dt.year >= day.year - 2)]
            lt = v.groupby("instrument_id").tail(1); ns = set(lt.instrument_id[lt.is_non_standard.astype(bool)])
        else:
            ns = set()
        pool = []
        for c in band:
            if hist_n.get(c, 0) < min_hist: continue
            if c in st: continue
            px = close.get(c, np.nan)
            if not (px == px): continue
            if k.get("excl") and px < 2.0: continue
            if c in ns: continue
            a = adv.get(c, np.nan)
            if not (a == a) or a < 5e6: continue
            pool.append(c)
        if k.get("fund"):
            ok = {c: (pe.get(c, np.nan) > 0) and (0 < pb.get(c, np.nan) <= 3) for c in pool}
            passing = sorted([c for c in pool if ok[c]], key=lambda c: _priority(0, c))
            failing = sorted([c for c in pool if not ok[c]], key=lambda c: _priority(0, c))
            order = passing + (failing[: max(0, 50 - len(passing))] if len(passing) < 50 else [])
        else:
            order = sorted(pool, key=lambda c: _priority(0, c))
        ind = industry_on(day, order)
        keep = [c for c in (prev or []) if c in set(order[:150])]
        chosen, cnt = [], {}
        for c in keep + [c for c in order if c not in keep]:
            g = ind.get(c, "unknown")
            if cnt.get(g, 0) >= k["ind_cap"]: continue
            chosen.append(c); cnt[g] = cnt.get(g, 0) + 1
            if len(chosen) == 50: break
        return chosen
    return select, fm


def baskets_for(select, fm, start, end, k):
    idx = fm.index[(fm.index >= pd.Timestamp(start)) & (fm.index <= pd.Timestamp(end))]
    dates = list(idx[::EVERY]); out, prev = {}, None
    for d in dates:
        prev = select(d, prev, {**k, "end": end}); out[d] = prev
    return dates, out


# ---------------- panels (adjusted / raw) ----------------
_PCACHE: dict = {}


def panels_for(ids, start, end, adjusted):
    from quantlab.platform.execution import load_execution_panels, ExecPanels
    from quantlab.data.v2_readers import load_merged_panel
    key = (tuple(sorted(ids)), start, end)
    if key not in _PCACHE:
        lo = (pd.Timestamp(start) - pd.Timedelta(days=10)).date()
        p, diag = load_execution_panels(sorted(ids), lo, end)
        fac = {}
        for c in p.close.columns:
            f = load_merged_panel(c).frame
            s = pd.Series(pd.to_numeric(f["factor"], errors="coerce").to_numpy(), index=pd.to_datetime(f["event_time"]).dt.normalize())
            fac[c] = s[~s.index.duplicated(keep="last")]
        F = pd.DataFrame(fac).reindex(p.close.index).ffill().bfill()
        _PCACHE.clear(); _PCACHE[key] = (p, F, diag)
    p, F, diag = _PCACHE[key]
    if not adjusted:
        return p, diag
    # forward-adjust to each name's last factor in-window (qfq): price*F/F_last, volume/(F/F_last)
    r = (F / F.ffill().iloc[-1]).astype("float32")
    sc = lambda x: None if x is None else x * r
    q = ExecPanels(close=p.close * r, open=sc(p.open), high=sc(p.high), low=sc(p.low),
                   volume=None if p.volume is None else p.volume / r, amount=p.amount,
                   limit_up=sc(p.limit_up), limit_down=sc(p.limit_down), suspended=p.suspended)
    return q, diag


def schedule(dates, baskets, w):
    return {d: {c: w / len(baskets[d]) for c in baskets[d]} for d in dates if baskets[d]}


def stats(nav):
    r = nav.pct_change().dropna(); yrs = len(r) / 252
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1 / yrs) - 1
    mdd = float((nav / nav.cummax() - 1).min()); sh = float(r.mean() / r.std() * math.sqrt(252))
    return {"cagr": float(cagr), "mdd": mdd, "sharpe": sh, "vol": float(r.std() * math.sqrt(252)),
            "start": str(nav.index[0].date()), "end": str(nav.index[-1].date())}


def fast_sim(p, dates, baskets, w, start):
    ret = p.close.pct_change(fill_method=None)
    ret = ret.where(p.close.notna())
    days = ret.index[ret.index >= pd.Timestamp(start)]
    seg = list(dates) + [days[-1] + pd.Timedelta(days=1)]
    out = pd.Series(0.0, index=days)
    for i, d in enumerate(dates):
        m = (days > d) & (days < seg[i + 1])
        names = [c for c in baskets[d] if c in ret.columns]
        out[m] = w * ret.loc[days[m], names].mean(axis=1, skipna=True).fillna(0).to_numpy()
    return (1 + out).cumprod()


def delist_overlay(nav, aw, scenario):
    from quantlab.beta.survivorship import load_delisted_master
    m = load_delisted_master(); nav = nav.copy(); hits = 0
    for c in aw.columns:
        if c not in m.index: continue
        ltd = m.loc[c, "last_trade_date"]
        if not (ltd == ltd) or ltd > nav.index[-1] or ltd < aw.index[0]: continue
        ltd = aw.index[aw.index <= ltd][-1]; w = float(np.nan_to_num(aw.at[ltd, c]))
        if w > 1e-6:
            nav.loc[nav.index > ltd] -= scenario * w * float(nav.at[ltd]); hits += 1
    return nav, hits


def engine(p, sched, cfg, start):
    from quantlab.platform.execution import run_weight_schedule
    res = run_weight_schedule(p, sched, initial_cash=CAP, config=cfg, record_weights=True)
    nav = res["nav"].loc[pd.Timestamp(start):]
    return nav, res


def orig_cost():
    from quantlab.platform.execution import ExecConfig
    # original repo convention (M2 prereg / stable_book): next-open fills, 30bp slippage, commission+stamp, lots; no impact/participation cap
    return ExecConfig(fill="next_open", slippage=0.003, impact_k=0.0, participation_cap=None, lots=True,
                      enforce_limits=True, unfilled="carry", order_rounding="target", price_tick="auto")


def strict_cost():
    from quantlab.platform.execution import ExecConfig
    return ExecConfig.strategy_v1(impact_k=1.0, min_trade_value=2000.0)


ORIG = dict(band="adv", st_pre=False, excl=False, fund=False, ind_cap=15, survivor_only=False)
LADDER = [
    # id, label, selector knobs, sim, prices, cost, weight, delist, window
    ("L0", "原仓库口径快仿：ADV带、不剔ST、无财务、复权收盘→收盘、无成本、100%", ORIG, "fast", True, None, 1.0, 0.0, "is"),
    ("L1", "+ 平台引擎次日开盘成交/涨跌停/整手（原成本：30bp滑点+佣金印花，无冲击）", ORIG, "eng", True, "orig", 1.0, 0.0, "is"),
    ("L2", "+ 带宽改为B1流通市值排名3001–5000（含退市）", {**ORIG, "band": "cap"}, "eng", True, "orig", 1.0, 0.0, "is"),
    ("L3", "+ PE>0 且 0<PB≤3", {**ORIG, "band": "cap", "fund": True}, "eng", True, "orig", 1.0, 0.0, "is"),
    ("L4", "+ ST/低价/非标审计（排名后剔除）、行业上限12", {**ORIG, "band": "cap", "fund": True, "excl": True, "ind_cap": 12}, "eng", True, "orig", 1.0, 0.0, "is"),
    ("L5", "+ 成本改 strategy_v1(impact_k=1, min_trade 2000)", {**ORIG, "band": "cap", "fund": True, "excl": True, "ind_cap": 12}, "eng", True, "strict", 1.0, 0.0, "is"),
    ("L6", "+ 退市终值 −50%（V2 严格口径，100%）", {**ORIG, "band": "cap", "fund": True, "excl": True, "ind_cap": 12}, "eng", True, "strict", 1.0, 0.5, "is"),
    ("L7", "价格不复权（今日此前V2引擎跑法的缺陷）", {**ORIG, "band": "cap", "fund": True, "excl": True, "ind_cap": 12}, "eng", False, "strict", 1.0, 0.5, "is"),
    ("L8", "L6 权重 100%→29%（其余现金）", {**ORIG, "band": "cap", "fund": True, "excl": True, "ind_cap": 12}, "eng", True, "strict", 0.29, 0.5, "is"),
    ("L9", "L7(不复权) 29% 且窗口 2015-06→2026-10（≈C3 闭环）", {**ORIG, "band": "cap", "fund": True, "excl": True, "ind_cap": 12}, "eng", False, "strict", 0.29, 0.5, "full"),
    ("X1", "旁证：L1 仅用存活股排名（幸存者偏差）", {**ORIG, "survivor_only": True}, "eng", True, "orig", 1.0, 0.0, "is"),
    ("X2", "旁证：L1 排名前剔除ST（M2口径）", {**ORIG, "st_pre": True}, "eng", True, "orig", 1.0, 0.0, "is"),
]
WIN = {"is": ("2018-01-02", "2026-09-22"), "full": ("2015-06-01", "2026-10-09"), "dev": ("2018-01-02", "2024-05-31")}


def run_rows(rows, tag):
    select, fm = make_selector()
    cache_b = {}
    results = []
    for rid, label, k, sim, adj, cost, w, dl, win in rows:
        t0 = time.time(); s, e = WIN[win]
        kk = json.dumps({**k, "win": win}, sort_keys=True)
        if kk not in cache_b:
            cache_b[kk] = baskets_for(select, fm, s, e, k)
        dates, B = cache_b[kk]
        ids = sorted({c for v in B.values() for c in v})
        p, diag = panels_for(ids, s, e, adj)
        sizes = [len(v) for v in B.values()]
        if sim == "fast":
            nav = fast_sim(p, dates, B, w, s); extra = {}
        else:
            nav, res = engine(p, schedule(dates, B, w), orig_cost() if cost == "orig" else strict_cost(), s)
            hits = 0
            if dl > 0:
                nav, hits = delist_overlay(nav, res["actual_weights"].loc[nav.index], dl)
            yrs = len(nav) / 252
            extra = {"turnover_one_way_per_year": float(res["filled_notional"] / 2 / nav.mean() / yrs),
                     "cost_frac_per_year": float(res["total_cost"] / CAP / yrs),
                     "costs": {kq: round(float(v)) for kq, v in res["costs"].items()}, "delist_hits": hits,
                     "fill_ratio": float(res["fill_ratio"])}
        row = {"id": rid, "label": label, "weight": w, "adjusted": adj, "cost": cost, "delist": dl, "window": win,
               **stats(nav), **extra, "n_ids": len(ids), "basket_min": min(sizes), "basket_max": max(sizes),
               "missing_ids": len(diag["missing_ids"]), "secs": round(time.time() - t0, 1)}
        log(rid, f"CAGR {row['cagr']:.2%} MDD {row['mdd']:.2%} Sharpe {row['sharpe']:.2f}", f"n_ids {len(ids)} basket {min(sizes)}-{max(sizes)}", row["secs"], "s")
        results.append(row)
        (OUT / f"{tag}.json").write_text(json.dumps({"promotion_approved": False, "rows": results}, ensure_ascii=False, indent=1))
    return results


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    mode = sys.argv[1]
    if mode == "ladder":
        run_rows(LADDER, "ladder")
    elif mode == "final":
        k = {**ORIG, "band": "cap", "fund": True, "excl": True, "ind_cap": 12}
        run_rows([("FINAL", "V2严格100%小盘：B1市值带+PE/PB+ST/低价/审计+strategy_v1+复权+退市−50%，2018-01→2024-05，单次", k, "eng", True, "strict", 1.0, 0.5, "dev")], "final_dev_2018_2024_05")
