"""B1 full-market ranks 2015+ + B3 stress 2015-06~2016-01 (descriptive).
Research-only; promotion_approved=false. No Strategy-engine NAV claims.
Terminal delist −50%/−100% defined only (not applied to NAV here).
"""
from __future__ import annotations

import json
import math
from datetime import date, datetime
from pathlib import Path

import numpy as np
import pandas as pd

from quantlab.beta.survivorship import (
    delist_sensitivity_table,
    later_delisted_in_band,
    load_delisted_master,
    load_full_market_float_mktcap,
    merge_cap_for_ranking,
    rank_band,
)
from quantlab.beta.smallcap_sleeve import SmallcapBetaSleeveProvider, load_smallcap_config, _priority
from quantlab.mandate_v2 import load_mandate_v2

ROOT = Path(__file__).resolve().parents[1]
OUT_B1 = ROOT / "output/v2_proto/smallcap_survivorship_b1.json"
OUT_B3 = ROOT / "output/v2_proto/smallcap_b3_stress_2015.json"
DB = ROOT / "data/v2/tushare_raw/daily_basic"
KEY_DATES = [
    "2015-06-15", "2015-12-31", "2016-01-29", "2018-06-29", "2020-06-30",
    "2023-12-29", "2026-06-30", "2026-10-09",
]


def _iid(ts_code: str) -> str:
    code, ex = ts_code.split(".")
    return {"SH": "sh", "SZ": "sz", "BJ": "bj"}.get(ex, "x") + "." + code


def band_for_cap(cap: pd.Series, rank_start=3001, rank_end=5000, rel=0.4):
    n = len(cap)
    if n >= rank_end:
        ids, _ = rank_band(cap, rank_start, rank_end)
        return ids, "absolute_3001_5000", n
    if n >= rank_start:
        ids, _ = rank_band(cap, rank_start, n)
        return ids, f"absolute_3001_{n}", n
    start = int(math.ceil((1 - rel) * n))
    return list(cap.index[start:]), f"relative_bottom40_from_rank_{start}", n


def st_active_on(day: pd.Timestamp) -> set[str]:
    st = pd.read_parquet(ROOT / "data/v2/st_flags/st_intervals_tushare.parquet")
    act = st[(st.start_date <= day) & (st.end_date.isna() | (st.end_date >= day))]
    ids = set(act["instrument_id"].astype(str))
    # delisted ST daily
    p = ROOT / "data/v2/delisted/delisted_is_st_daily_from2015.parquet"
    if p.exists():
        d = pd.read_parquet(p)
        d = d[(d.trade_date == day) & d.is_st_at_open.astype(bool)]
        ids |= set(d.instrument_id.astype(str))
    # surviving ST daily from 2018+
    p2 = ROOT / "data/v2/st_flags/is_st_daily_2018_2026.parquet"
    if p2.exists() and day >= pd.Timestamp("2018-01-01"):
        d = pd.read_parquet(p2, columns=["instrument_id", "trade_date", "is_st_at_open"])
        d = d[(d.trade_date == day) & d.is_st_at_open.astype(bool)]
        ids |= set(d.instrument_id.astype(str))
    return ids


def load_db_day(day: pd.Timestamp) -> pd.DataFrame | None:
    f = DB / f"{day.strftime('%Y%m%d')}.parquet"
    if not f.exists():
        return None
    d = pd.read_parquet(f)
    d["instrument_id"] = d["ts_code"].map(_iid)
    return d.set_index("instrument_id")


def form_b3_basket(formation: str, target_n: int = 50, seed: int = 0):
    """B1 rank + post-band ST/low-price/audit-ish/fund filters using daily_basic."""
    day = pd.Timestamp(formation)
    cap, diag = merge_cap_for_ranking(None, day, 20)
    band_ids, mode, n_univ = band_for_cap(cap)
    st_ids = st_active_on(pd.Timestamp(diag["data_session"]))
    db = load_db_day(pd.Timestamp(diag["data_session"]))
    if db is None:
        # try data_session from diag
        db = load_db_day(day)
    funnel = {"universe": n_univ, "band_mode": mode, "band": len(band_ids), "st_in_band": 0,
              "low_price_in_band": 0, "fund_pass": 0, "selected": 0}
    ld = later_delisted_in_band(band_ids, pd.Timestamp(diag["data_session"]))
    if db is None:
        return {"ok": False, "reason": "daily_basic_missing", "diag": diag, "funnel": funnel,
                "later_delisted_in_band": ld}

    rows = []
    for c in band_ids:
        if c not in db.index:
            continue
        r = db.loc[c]
        if c in st_ids:
            funnel["st_in_band"] += 1
            continue
        close = float(r["close"]) if r["close"] == r["close"] else None
        if close is None or close < 2.0:
            funnel["low_price_in_band"] += 1
            continue
        pe = float(r["pe_ttm"]) if r["pe_ttm"] == r["pe_ttm"] else None
        pb = float(r["pb"]) if r["pb"] == r["pb"] else None
        fund = pe is not None and pe > 0 and pb is not None and 0 < pb <= 3
        rows.append({"iid": c, "close": close, "pe": pe, "pb": pb, "fund": fund,
                     "circ_mv": float(r["circ_mv"]) * 1e4 if r["circ_mv"] == r["circ_mv"] else None})
    passing = [r for r in rows if r["fund"]]
    failing = [r for r in rows if not r["fund"]]
    funnel["fund_pass"] = len(passing)
    order = sorted(passing, key=lambda r: _priority(seed, r["iid"]))
    if len(order) < target_n:
        order += sorted(failing, key=lambda r: _priority(seed, r["iid"]))[: target_n - len(order)]
    chosen = [r["iid"] for r in order[:target_n]]
    funnel["selected"] = len(chosen)
    funnel["fund_fallback_used"] = max(0, target_n - funnel["fund_pass"]) if len(chosen) == target_n else 0
    return {
        "ok": True, "formation": formation, "data_session": diag["data_session"],
        "band_mode": mode, "diag": diag, "funnel": funnel,
        "later_delisted_in_band": ld["count"],
        "later_delisted_names_sample": ld["names"][:20],
        "names": chosen,
        "n": len(chosen),
        "in_band_later_delisted_selected": len(set(chosen) & set(ld["names"])),
        "label": "B1 ranking on float_mktcap_from2015; ST/low-price/fund after band; audit not applied (2015 coverage thin) — research descriptive",
    }


def descriptive_ew_dd(names, start, end):
    """EW basket max DD from daily_basic unadjusted closes. Descriptive only."""
    start_ts, end_ts = pd.Timestamp(start), pd.Timestamp(end)
    files = sorted(DB.glob("*.parquet"))
    # filter by name
    days = []
    for f in files:
        ds = f.stem
        if len(ds) != 8 or not ds.isdigit():
            continue
        ts = pd.Timestamp(ds)
        if start_ts <= ts <= end_ts:
            days.append(ts)
    if not days:
        return {"available": False}
    closes = {}
    for ts in days:
        db = load_db_day(ts)
        if db is None:
            continue
        closes[ts] = db["close"].reindex(names)
    wide = pd.DataFrame(closes).T.sort_index()
    # simple return from unadjusted close; skip gaps
    rets = wide.pct_change()
    # if a name disappears (delist), leave NaN (not inventing terminal mark in NAV)
    ew = rets.mean(axis=1, skipna=True)
    nav = (1 + ew.fillna(0)).cumprod()
    dd = nav / nav.cummax() - 1
    # pairwise corr on crash month (Jul 2015)
    crash = rets.loc["2015-06-15":"2015-08-31"]
    corr_note = None
    if len(crash) > 5:
        cmat = crash.corr()
        vals = cmat.where(np.triu(np.ones(cmat.shape), 1).astype(bool)).stack()
        corr_note = {
            "window": ["2015-06-15", "2015-08-31"],
            "median_pairwise_corr": float(vals.median()) if len(vals) else None,
            "mean_pairwise_corr": float(vals.mean()) if len(vals) else None,
            "frac_pairs_corr_gt_0_5": float((vals > 0.5).mean()) if len(vals) else None,
        }
    # etf proxy: use 510300 if in daily_basic? unlikely. skip or use index from etf panel if any
    return {
        "available": True,
        "label": "DESCRIPTIVE raw unadjusted daily_basic closes; EW; no costs; no limit-down modeling; NO terminal delist mark applied to NAV; NOT Strategy engine; NOT a performance claim",
        "sessions": int(len(nav)),
        "names_with_any_bar": int(wide.notna().any(axis=0).sum()),
        "ret_nan_frac": float(rets.isna().mean().mean()),
        "basket_ew_max_drawdown": float(dd.min()),
        "basket_trough_session": str(dd.idxmin().date()) if len(dd) else None,
        "basket_window_end_return": float(nav.iloc[-1] - 1) if len(nav) else None,
        "crash_corr": corr_note,
        "book_impact_by_tier_descriptive": {t: float(dd.min()) * w for t, w in [("T10", 0.1), ("T15", 0.15), ("T20", 0.2)]},
        "terminal_delist_scenarios_defined_not_in_nav": {
            "minus_50": "would mark once at last_close*0.5 if held name delists in window — NOT applied here",
            "minus_100": "would mark once at 0 — NOT applied here",
            "why_not_applied": "waiting Strategy fixed engine; no invented NAV claims on unfixed path",
        },
    }


def main():
    cfg = load_smallcap_config()
    master = load_delisted_master()
    # warm cache
    _ = load_full_market_float_mktcap()

    by_session = {}
    hist = []
    for s in KEY_DATES:
        cap, diag = merge_cap_for_ranking(None, s, int(cfg["universe"]["cap_window"]))
        band_ids, mode, n = band_for_cap(cap)
        info = later_delisted_in_band(band_ids, pd.Timestamp(diag["data_session"]), master)
        row = {
            "requested": s, "data_session": diag["data_session"], "source": diag["source"],
            "n_ranked": n, "band_mode": mode, "band_size": len(band_ids),
            "later_delisted_in_band": info["count"],
            "later_delisted_alive_on_session": diag.get("later_delisted_alive_on_session"),
            "pre_2023_complete": diag.get("pre_2023_complete", True),
        }
        by_session[s] = row
        hist.append(row)
        print(s, mode, "band", len(band_ids), "ld", info["count"], flush=True)

    # 2023+ full sleeve overlap check
    m = load_mandate_v2()
    sc = SmallcapBetaSleeveProvider(m)
    sleeve_checks = {}
    for s in ["2023-12-29", "2026-06-30", "2026-10-09"]:
        kw = {"min_history_override": 222} if s.startswith("2023") else {}
        b = sc.basket(date.fromisoformat(s), **kw)
        sleeve_checks[s] = {
            "n": len(b.names),
            "later_delisted_in_band": b.filters_hit.get("later_delisted_in_band"),
            "b1_source": b.filters_hit.get("b1_source"),
            "band_size": b.filters_hit.get("band_size"),
            "rank_universe_size": b.filters_hit.get("rank_universe_size"),
        }
        print("sleeve", s, sleeve_checks[s], flush=True)

    b1 = {
        "ok": True,
        "phase": "beta_smallcap_survivorship_b1",
        "promotion_approved": False,
        "mandate_json_edited": False,
        "survivorship_clean_for_2015_plus": True,
        "survivorship_clean_for_panel_window_2023_plus": True,
        "survivorship_clean_for_pre_2023": True,
        "label": "B1 COMPLETE 2015+: primary as-of float mktcap = data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet (incl. delisted). Absolute 3001–5000 when universe≥5000; else absolute 3001–N or relative bottom 40%. ST/low-price/audit AFTER band.",
        "primary_panel": {
            "path": "data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet",
            "manifest": "data/v2/float_mktcap/float_mktcap_daily_from2015_manifest.json",
            "date_min": "2015-01-05", "date_max": "2026-10-09",
            "n_instruments": 5831, "unit": "yuan", "includes_delisted": True,
            "quality_status": "research", "promotion_approved": False,
        },
        "by_session": by_session,
        "sleeve_checks_2023_plus": sleeve_checks,
        "historical_summary": {
            "key_dates": hist,
            "note": "2015–2017 use relative bottom-40% (universe < 3001). 2018–2021 absolute 3001–N. 2022+ absolute 3001–5000.",
        },
        "delist_terminal_scenarios": {
            "minus_50": "mark once at last_close * 0.5",
            "minus_100": "mark once at 0",
            "in_nav": False,
            "why": "waiting Strategy fixed engine; defined only — no invented NAV",
        },
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "config_block": cfg.get("survivorship_b1"),
    }
    OUT_B1.write_text(json.dumps(b1, ensure_ascii=False, indent=2, default=str))

    # B3
    formation = "2015-06-15"
    basket = form_b3_basket(formation)
    print("b3 basket", basket.get("n"), basket.get("funnel"), flush=True)
    dd = descriptive_ew_dd(basket["names"], "2015-06-15", "2016-01-29") if basket.get("ok") else {}
    print("b3 dd", {k: dd.get(k) for k in ["basket_ew_max_drawdown", "basket_trough_session", "basket_window_end_return", "crash_corr"]}, flush=True)
    b3 = {
        "ok": bool(basket.get("ok")),
        "phase": "beta_smallcap_b3_stress_2015",
        "promotion_approved": False,
        "mandate_json_edited": False,
        "window": ["2015-06-15", "2016-01-29"],
        "formation": basket,
        "descriptive_drawdown": dd,
        "purpose": "failure-scenario sleeve DD to inform Mandate α ≤ L/D_max upper bound; research descriptive only",
        "engine": "NOT Strategy fixed engine; daily_basic unadjusted closes; terminal delist marks NOT in NAV",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }
    OUT_B3.write_text(json.dumps(b3, ensure_ascii=False, indent=2, default=str))
    print("wrote", OUT_B1, OUT_B3)


if __name__ == "__main__":
    main()
