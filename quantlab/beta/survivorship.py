"""B1 survivorship helpers for the small-cap β sleeve (research; promotion_approved=false).

V2_REBUILD_PLAN B1: as-of float-cap ranks over the full market including later-delisted
and then-ST names; ST/low-price/audit stay as post-ranking risk filters; terminal return
on delist is reported under −50% and −100% sensitivities (no invented post-delist prices).
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]

@lru_cache(maxsize=1)
def load_full_market_float_mktcap(path: str = "data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet"):
    """Primary as-of float mktcap (CNY) from 2015, includes delisted. Wide panel."""
    import pandas as pd

    fp = ROOT / path
    if not fp.exists():
        return None
    # RAM: wide float32 cache (built once, keyed on source mtime); avoids the long->pivot_table peak.
    cache = ROOT / "output/v2_proto/cache_smallcap_history" / f"float_mktcap_wide_f32_{int(fp.stat().st_mtime)}.parquet"
    if cache.exists():
        return pd.read_parquet(cache)
    d = pd.read_parquet(fp, columns=["instrument_id", "trade_date", "float_mktcap"])
    d["float_mktcap"] = d["float_mktcap"].astype("float32")
    d = d.drop_duplicates(["trade_date", "instrument_id"], keep="last")
    w = d.set_index(["trade_date", "instrument_id"])["float_mktcap"].unstack()
    del d
    w.index = pd.to_datetime(w.index)
    w = w.sort_index()
    cache.parent.mkdir(parents=True, exist_ok=True)
    w.to_parquet(cache)
    return w


@lru_cache(maxsize=1)
def load_full_market_total_mv(path: str = "data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet"):
    import pandas as pd

    fp = ROOT / path
    if not fp.exists():
        return None
    d = pd.read_parquet(fp, columns=["instrument_id", "trade_date", "total_mv"])
    w = d.pivot_table(index="trade_date", columns="instrument_id", values="total_mv", aggfunc="last")
    w.index = pd.to_datetime(w.index)
    return w.sort_index()



@lru_cache(maxsize=1)
def load_delisted_master(path: str = "data/v2/delisted/delisted_master_tushare.parquet"):
    import pandas as pd

    fp = ROOT / path
    if not fp.exists():
        return None
    m = pd.read_parquet(fp)
    for c in ("list_date", "delist_date", "last_trade_date"):
        if c in m.columns:
            m[c] = pd.to_datetime(m[c])
    return m.set_index("instrument_id", drop=False)


@lru_cache(maxsize=1)
def load_delisted_daily_circ_mv(path: str = "data/v2/delisted/delisted_daily_from2015_tushare.parquet"):
    """Wide circ_mv in CNY (yuan), indexed by trade_date."""
    import pandas as pd

    fp = ROOT / path
    if not fp.exists():
        return None
    d = pd.read_parquet(fp, columns=["instrument_id", "trade_date", "circ_mv"])
    w = d.pivot_table(index="trade_date", columns="instrument_id", values="circ_mv", aggfunc="last")
    w.index = pd.to_datetime(w.index)
    return w.sort_index()


@lru_cache(maxsize=1)
def load_delisted_st_daily(path: str = "data/v2/delisted/delisted_is_st_daily_from2015.parquet"):
    import pandas as pd

    fp = ROOT / path
    if not fp.exists():
        return None
    d = pd.read_parquet(fp)
    d = d[d["is_st_at_open"].astype(bool)]
    return {pd.Timestamp(k): frozenset(v) for k, v in d.groupby("trade_date")["instrument_id"]}


def merge_cap_for_ranking(panel_circ_mv_wan, day, cap_window: int = 20):
    """As-of float-cap (CNY) for ranking.

    Primary (2015+): ``data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet``
    (yuan; includes delisted). Fallback: research panel circ_mv (万元→CNY) ∪ delisted daily.
    Rolling mean over ``cap_window`` sessions. Returns (cap_cny Series, diagnostics).
    """
    import pandas as pd

    day = pd.Timestamp(day)
    diag: dict = {"survivorship_ranking": True}
    master = load_delisted_master()
    alive = set()
    if master is not None:
        alive = set(master.index[(master.list_date <= day) & (master.delist_date > day)])
    fm = load_full_market_float_mktcap()
    if fm is not None:
        sub = fm.loc[:day]
        if len(sub):
            # use last session on/before day
            use_day = sub.index[-1]
            hist = sub.tail(cap_window)
            cap = hist.mean(skipna=True).dropna()
            diag.update({
                "available": True,
                "source": "float_mktcap_daily_from2015_tushare",
                "source_path": "data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet",
                "data_session": str(use_day.date()),
                "requested_session": str(day.date()),
                "session_shifted": str(use_day.date()) != str(day.date()),
                "n_ranked": int(len(cap)),
                "later_delisted_alive_on_session": len(alive),
                "unit": "CNY",
                "includes_delisted": True,
                "pre_2023_complete": True,
            })
            return cap.sort_values(ascending=False), diag
    # Fallback: attrib panel ∪ delisted daily
    diag["source"] = "fallback_attrib_panel_union_delisted_daily"
    diag["pre_2023_complete"] = False
    if panel_circ_mv_wan is None or day not in panel_circ_mv_wan.index:
        diag["available"] = False
        return None, diag
    hist = panel_circ_mv_wan.loc[:day].tail(cap_window)
    panel_cap = (hist.mean(skipna=True) * 1e4).dropna()
    daily = load_delisted_daily_circ_mv()
    added = filled = 0
    if daily is not None:
        sub = daily.loc[:day]
        if len(sub):
            dcap = sub.tail(cap_window).mean(skipna=True).dropna()
            if master is not None:
                dcap = dcap[dcap.index.isin(alive)]
            for iid, v in dcap.items():
                if iid not in panel_cap.index:
                    panel_cap.loc[iid] = float(v); added += 1
                elif panel_cap.loc[iid] != panel_cap.loc[iid]:
                    panel_cap.loc[iid] = float(v); filled += 1
    diag.update({"available": True, "n_ranked": int(panel_cap.notna().sum()),
                 "delisted_names_added_to_rank": added, "panel_nan_filled_from_delisted": filled,
                 "later_delisted_alive_on_session": len(alive), "unit": "CNY"})
    return panel_cap.sort_values(ascending=False), diag


def rank_band(cap_cny, rank_start: int = 3001, rank_end: int = 5000):
    """Return list of instrument_ids in the absolute float-cap band (1 = largest)."""
    if cap_cny is None or len(cap_cny) == 0:
        return [], {"band_size": 0}
    r = cap_cny.rank(ascending=False, method="first")
    band = list(r[(r >= rank_start) & (r <= rank_end)].sort_values().index)
    return band, {"band_size": len(band), "universe_ranked": int(len(cap_cny))}


def later_delisted_in_band(band: Sequence[str], day, master=None) -> Mapping[str, object]:
    master = master if master is not None else load_delisted_master()
    if master is None:
        return {"count": 0, "names": []}
    alive_later = master[(master.list_date <= day) & (master.delist_date > day)]
    hit = [i for i in band if i in alive_later.index]
    return {
        "count": len(hit),
        "names": hit,
        "delist_dates": {i: str(alive_later.loc[i, "delist_date"].date()) for i in hit},
        "was_st_within_1y_of_delist": {i: bool(alive_later.loc[i, "was_st_within_1y_of_delist"]) for i in hit},
    }


def delist_terminal_loss(code: str, last_close: float | None, scenario: str) -> Mapping[str, object]:
    """Terminal P&L fraction from last close. scenario in {'minus_50','minus_100'}."""
    if scenario == "minus_50":
        frac = -0.50
    elif scenario == "minus_100":
        frac = -1.00
    else:
        raise ValueError(scenario)
    return {
        "instrument_id": code,
        "scenario": scenario,
        "terminal_return_from_last_close": frac,
        "last_close": last_close,
        "invented_post_delist_price": False,
        "note": "no post-delist bars; apply once at last_trade_date+ as a terminal mark",
    }


def delist_sensitivity_table(codes: Sequence[str]) -> Mapping[str, object]:
    master = load_delisted_master()
    rows = []
    if master is None:
        return {"available": False, "rows": []}
    for c in codes:
        if c not in master.index:
            continue
        row = master.loc[c]
        rows.append({
            "instrument_id": c,
            "delist_date": str(row["delist_date"].date()) if row["delist_date"] == row["delist_date"] else None,
            "last_trade_date": str(row["last_trade_date"].date()) if row["last_trade_date"] == row["last_trade_date"] else None,
            "last_close": float(row["last_close"]) if row["last_close"] == row["last_close"] else None,
            "minus_50": delist_terminal_loss(c, float(row["last_close"]) if row["last_close"] == row["last_close"] else None, "minus_50"),
            "minus_100": delist_terminal_loss(c, float(row["last_close"]) if row["last_close"] == row["last_close"] else None, "minus_100"),
            "delist_reason_category": row.get("delist_reason_category"),
            "reason_basis": row.get("reason_basis"),
        })
    return {"available": True, "n": len(rows), "rows": rows,
            "scenarios": ["minus_50", "minus_100"],
            "rule": "on delist during a holding period, mark the position once at last available close × (1+terminal_return); do not invent post-delist prices"}
