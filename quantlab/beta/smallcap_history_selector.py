"""Long-history (2015+) selector for the standalone small-cap β sleeve.

Same rules as SmallcapBetaSleeveProvider.basket (research ~50 names), but built from
full-history sources so a fixed-engine run can start in 2015:
  rank   : as-of float mktcap 20d mean over the FULL market (float_mktcap_daily_from2015, incl. delisted)
  band   : absolute 3001-5000 if N>=5000, else relative bottom 40% (fixed 2026-10-11; old 3001-N branch was a bug)
  then   : history >= min(253, available-20), not ST (intervals ∪ is_st_daily ∪ delisted ST),
           close >= 2 CNY, not non-standard annual audit (PIT), ADV60 proxy >= 5M CNY
  fund   : pe_ttm > 0 and 0 < PB <= 3 (tier fallback)
  order  : sha256 seed order; retain current inside top retain_top; SW_L1 cap 12
ADV proxy: turnover_rate% × circ_mv from daily_basic (amount not in daily_basic) — documented.
Research-only; promotion_approved=false.
"""
from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

from quantlab.beta.smallcap_sleeve import _load_audit_annual, _priority, load_smallcap_config
from quantlab.beta.survivorship import load_full_market_float_mktcap

ROOT = Path(__file__).resolve().parents[2]
DB_DIR = ROOT / "data/v2/tushare_raw/daily_basic"
CACHE = ROOT / "output/v2_proto/cache_smallcap_history"


def _iid(ts):
    code, ex = ts.split(".")
    return {"SH": "sh", "SZ": "sz", "BJ": "bj"}.get(ex, "x") + "." + code


@lru_cache(maxsize=1)
def daily_basic_panels():
    """Wide close / pe_ttm / pb / adv_proxy_cny from daily_basic files (cached to parquet)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    keys = ("close", "pe_ttm", "pb", "amt_proxy")
    if all((CACHE / f"{k}.parquet").exists() for k in keys):
        return {k: pd.read_parquet(CACHE / f"{k}.parquet") for k in keys}
    frames = []
    for f in sorted(DB_DIR.glob("*.parquet")):
        if not (len(f.stem) == 8 and f.stem.isdigit()):
            continue
        d = pd.read_parquet(f, columns=["ts_code", "trade_date", "close", "pe_ttm", "pb", "turnover_rate", "circ_mv"])
        frames.append(d)
    d = pd.concat(frames, ignore_index=True)
    d["iid"] = d["ts_code"].map(_iid)
    d["trade_date"] = pd.to_datetime(d["trade_date"].astype(str))
    d["amt_proxy"] = d["turnover_rate"] / 100.0 * d["circ_mv"] * 1e4  # 万元 → CNY
    out = {}
    for k in keys:
        w = d.pivot_table(index="trade_date", columns="iid", values=k, aggfunc="last").sort_index().astype("float32")
        w.to_parquet(CACHE / f"{k}.parquet")
        out[k] = w
    return out


@lru_cache(maxsize=1)
def _st_sources():
    st = pd.read_parquet(ROOT / "data/v2/st_flags/st_intervals_tushare.parquet")
    st = st[["instrument_id", "start_date", "end_date", "ann_date"]].copy()
    daily = pd.read_parquet(ROOT / "data/v2/st_flags/is_st_daily_2018_2026.parquet")
    daily = daily[daily.is_st_at_open.astype(bool)]
    dmap = {pd.Timestamp(k): frozenset(v) for k, v in daily.groupby("trade_date")["instrument_id"]}
    dl = pd.read_parquet(ROOT / "data/v2/delisted/delisted_is_st_daily_from2015.parquet")
    dl = dl[dl.is_st_at_open.astype(bool)]
    dlmap = {pd.Timestamp(k): frozenset(v) for k, v in dl.groupby("trade_date")["instrument_id"]}
    return st, dmap, dlmap


def st_on(day: pd.Timestamp) -> set:
    st, dmap, dlmap = _st_sources()
    act = st[(st.start_date <= day) & (st.end_date.isna() | (st.end_date >= day)) & (st.ann_date.isna() | (st.ann_date < day))]
    return set(act.instrument_id.astype(str)) | set(dmap.get(day, ())) | set(dlmap.get(day, ()))


@lru_cache(maxsize=1)
def _sw():
    cfg = load_smallcap_config()
    sw = pd.read_parquet(ROOT / cfg["data"]["sw_l1"], columns=["instrument_id", "sw_code", "in_date", "out_date"])
    sw["in_date"] = pd.to_datetime(sw["in_date"]); sw["out_date"] = pd.to_datetime(sw["out_date"])
    return sw


def industry_on(day, ids):
    sw = _sw()
    s = sw[sw.instrument_id.isin(ids) & (sw.in_date <= day) & (sw.out_date.isna() | (sw.out_date > day))]
    return dict(zip(s.instrument_id, s.sw_code))


def select(session, current=None, target_n: int | None = None, retain_top: int | None = None) -> dict:
    cfg = load_smallcap_config()
    U, Fd, S, rc = cfg["universe"], cfg["fundamentals"], cfg["selection"], cfg["risk_controls"]
    N = int(target_n or S["target_names"])
    retain_top = int(S["retain_top"] if retain_top is None else retain_top)
    fm = load_full_market_float_mktcap()
    P = daily_basic_panels()
    day = pd.Timestamp(session)
    idx = fm.index[fm.index <= day]
    if len(idx) == 0:
        return {"session": str(day.date()), "names": [], "ok": False}
    day = idx[-1]
    t = len(idx) - 1
    cap = fm.iloc[max(0, t - int(U["cap_window"]) + 1): t + 1].mean(skipna=True).dropna()
    n_univ = len(cap)
    ranked = cap.sort_values(ascending=False)
    rs, re_ = int(U["rank_start"]), int(U["rank_end"])
    # FIX 2026-10-11: the old 'absolute 3001-N when 3001<=N<5000' branch produced tiny bands
    # (e.g. 77 names on 2017-06-30, almost all fresh IPOs -> 0-47-name baskets 2017-04..2018-03).
    # Rule now: absolute ranks 3001-5000 once N>=5000 (== bottom 40% at N=5000, continuous);
    # otherwise relative bottom 40% of the full market.
    if n_univ >= re_:
        band = list(ranked.index[rs - 1: re_]); mode = "absolute_3001_5000"
    else:
        band = list(ranked.index[math.ceil((1 - float(U["relative_bottom_frac"])) * n_univ):]); mode = "relative_bottom40"
    # history: sessions with float data up to day
    hist_n = fm.iloc[: t + 1][band].notna().sum()
    avail = t + 1
    min_hist = min(int(U["min_history_sessions"]), max(60, avail - 20))
    truncated = min_hist < int(U["min_history_sessions"])
    dbi = P["close"].index[P["close"].index <= day]
    if len(dbi) == 0:
        return {"session": str(day.date()), "names": [], "ok": False, "why": "no_daily_basic"}
    dd = dbi[-1]
    close = P["close"].loc[dd]
    pe = P["pe_ttm"].loc[dd]; pb = P["pb"].loc[dd]
    k = P["amt_proxy"].index.get_loc(dd)
    adv = P["amt_proxy"].iloc[max(0, k - 59): k + 1].mean(skipna=True)
    st = st_on(day)
    au = _load_audit_annual("data/v2/audit/audit_opinion_pit_tushare.parquet")
    v = au[(au["avail_date"] < day) & (au["end_date"].dt.year >= day.year - 2)]
    latest = v.groupby("instrument_id").tail(1)
    ns = set(latest.instrument_id[latest.is_non_standard.astype(bool)])
    f = dict(band=len(band), hist=0, st=0, low_px=0, audit=0, no_px=0, adv=0)
    pool = []
    for c in band:
        if hist_n.get(c, 0) < min_hist: f["hist"] += 1; continue
        if c in st: f["st"] += 1; continue
        px = close.get(c, np.nan)
        if not (px == px): f["no_px"] += 1; continue
        if px < float(cfg["risk_exclusions"]["low_price"]["price_floor_cny"]): f["low_px"] += 1; continue
        if c in ns: f["audit"] += 1; continue
        a = adv.get(c, np.nan)
        if not (a == a) or a < float(rc["adv_floor_cny"]): f["adv"] += 1; continue
        pool.append(c)
    fund = {c: (pe.get(c, np.nan) > float(Fd["pe_ttm_gt"])) and (float(Fd["pb_gt"]) < pb.get(c, np.nan) <= float(Fd["pb_le"])) for c in pool}
    passing = sorted([c for c in pool if fund[c]], key=lambda c: _priority(0, c))
    failing = sorted([c for c in pool if not fund[c]], key=lambda c: _priority(0, c))
    order = passing + (failing[: max(0, N - len(passing))] if len(passing) < N else [])
    ind = industry_on(day, order)
    keep = [c for c in (current or []) if c in set(order[:retain_top])]
    chosen, counts = [], {}
    for c in keep + [c for c in order if c not in keep]:
        g = ind.get(c, "unknown")
        if counts.get(g, 0) >= int(S["max_names_per_industry"]): continue
        chosen.append(c); counts[g] = counts.get(g, 0) + 1
        if len(chosen) == N: break
    return {"session": str(day.date()), "names": chosen, "ok": True, "band_mode": mode, "universe": n_univ,
            "filters": f, "pool": len(pool), "fund_pass": len(passing), "fund_fallback": max(0, N - len(passing)),
            "retained": len(keep), "ranked_pool": list(order), "ranked_industries": {c: ind.get(c, "unknown") for c in order},
            "industries": {c: ind.get(c, "unknown") for c in chosen}, "industry_mix": dict(counts),
            "data_session": str(dd.date()), "fund_pass_names": len(passing), "history_truncated": truncated, "n_industries": len(counts),
            "max_per_industry": max(counts.values()) if counts else 0}
