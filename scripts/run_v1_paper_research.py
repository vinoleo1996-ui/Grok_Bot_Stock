#!/usr/bin/env python3
"""V1 research paper NAV — end-to-end, promotion_approved=false.

Universe: in-memory D1-like masks on merged panels (U30 waived on amount gaps,
listing>=120, exclude bottom 30% float_mktcap proxy, suspend/limit/ST).
Beta: PrototypeBetaSleeveProvider 510300.
Alpha: M01_12_1 + V01_EP (eps_ttm/close PIT) → SW_L1 neutralize → integrate.
Portfolio: Mandate 30–60 / 5% / 25%, monthly ordinary rebalance (biweekly too
slow for full scan; documented), Mandate costs.

Outputs under output/v1_paper/. Never flips promotion_approved.
"""
from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Mapping

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "v1_paper"
OUT.mkdir(parents=True, exist_ok=True)

# Research knobs
START = date(2020, 1, 2)
# Prefer full history; END resolved from calendar
LOOKBACK_CAL_DAYS = 420  # momentum warm-up before START
MAX_INSTRUMENTS: int | None = (
    int(__import__("os").environ["V1_PAPER_MAX_INSTRUMENTS"])
    if __import__("os").environ.get("V1_PAPER_MAX_INSTRUMENTS")
    else None
)  # None = all SSE/SZSE with panels
REBALANCE = "monthly"  # biweekly|monthly — monthly for compute; document
EXCLUDE_BSE = True
STAMP_CUTOVER = date(2023, 8, 28)


def _log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def stamp_tax_rate(session: date) -> float:
    return 0.001 if session < STAMP_CUTOVER else 0.0005


@dataclass
class PanelCache:
    close: pd.DataFrame  # DatetimeIndex x instrument_id
    amount: pd.DataFrame
    volume: pd.DataFrame
    turnover: pd.DataFrame
    tradestatus: pd.DataFrame
    is_st: pd.DataFrame
    limit_up: pd.DataFrame
    limit_down: pd.DataFrame
    open_status: pd.DataFrame
    listing_date: dict[str, date | None]


def preload_panels(
    instrument_ids: list[str],
    *,
    d0_root: Path,
    asof_extend_dir: Path,
    start_load: date,
    end_load: date,
) -> PanelCache:
    from quantlab.data.v2_readers import load_merged_panel, resolve_d0_asof_cutoff

    cutoff = resolve_d0_asof_cutoff(asof_extend_dir)
    closes: dict[str, pd.Series] = {}
    amounts: dict[str, pd.Series] = {}
    volumes: dict[str, pd.Series] = {}
    turnovers: dict[str, pd.Series] = {}
    trades: dict[str, pd.Series] = {}
    sts: dict[str, pd.Series] = {}
    ups: dict[str, pd.Series] = {}
    downs: dict[str, pd.Series] = {}
    opens: dict[str, pd.Series] = {}
    listing: dict[str, date | None] = {}

    instruments = pd.read_parquet(d0_root / "instruments.parquet")
    list_map = {
        str(r.instrument_id): (
            pd.Timestamp(r.listing_date).date() if pd.notna(r.listing_date) else None
        )
        for r in instruments.itertuples()
    }

    lo, hi = pd.Timestamp(start_load), pd.Timestamp(end_load)
    t0 = time.time()
    ok = 0
    for i, iid in enumerate(instrument_ids):
        listing[iid] = list_map.get(iid)
        view = load_merged_panel(
            iid, d0_root=d0_root, asof_extend_dir=asof_extend_dir, d0_asof_cutoff=cutoff
        )
        frame = view.frame
        if frame is None or frame.empty or "close" not in frame.columns:
            continue
        frame = frame.copy()
        if "event_time" in frame.columns:
            et = pd.to_datetime(frame["event_time"]).dt.normalize()
        elif isinstance(frame.index, pd.DatetimeIndex):
            et = pd.Series(frame.index.normalize(), index=frame.index)
        else:
            continue
        frame = frame.assign(_et=et)
        frame = frame[(frame["_et"] >= lo) & (frame["_et"] <= hi)]
        if frame.empty:
            continue
        frame = frame.sort_values("_et")
        frame = frame[~frame["_et"].duplicated(keep="last")]
        idx = pd.DatetimeIndex(frame["_et"])

        def col(name: str) -> pd.Series:
            if name not in frame.columns:
                return pd.Series(np.nan, index=idx)
            return pd.Series(pd.to_numeric(frame[name], errors="coerce").values, index=idx)

        closes[iid] = col("close")
        amounts[iid] = col("amount")
        volumes[iid] = col("volume")
        turnovers[iid] = col("turnover")
        trades[iid] = col("tradestatus")
        sts[iid] = col("is_st_at_open")
        ups[iid] = col("limit_up")
        downs[iid] = col("limit_down")
        if "open_status" in frame.columns:
            opens[iid] = pd.Series(frame["open_status"].astype(str).values, index=idx)
        else:
            opens[iid] = pd.Series("derived", index=idx)
        ok += 1
        if (i + 1) % 500 == 0:
            _log(f"preload {i+1}/{len(instrument_ids)} ok={ok} elapsed={time.time()-t0:.0f}s")

    def wide(d: dict[str, pd.Series]) -> pd.DataFrame:
        if not d:
            return pd.DataFrame()
        return pd.DataFrame(d).sort_index()

    _log(f"preload done ok={ok} in {time.time()-t0:.0f}s")
    return PanelCache(
        close=wide(closes),
        amount=wide(amounts),
        volume=wide(volumes),
        turnover=wide(turnovers),
        tradestatus=wide(trades),
        is_st=wide(sts),
        limit_up=wide(ups),
        limit_down=wide(downs),
        open_status=wide(opens),
        listing_date=listing,
    )


def trading_sessions(calendar: pd.DatetimeIndex, start: date, end: date) -> list[date]:
    s = calendar[(calendar >= pd.Timestamp(start)) & (calendar <= pd.Timestamp(end))]
    return [pd.Timestamp(x).date() for x in s]


def monthly_rebalance_dates(sessions: list[date]) -> list[date]:
    """First trading day of each calendar month in range."""
    out: list[date] = []
    seen: set[tuple[int, int]] = set()
    for d in sessions:
        key = (d.year, d.month)
        if key not in seen:
            seen.add(key)
            out.append(d)
    return out


def biweekly_rebalance_dates(sessions: list[date], min_gap: int = 10) -> list[date]:
    out: list[date] = []
    last_i = -10**9
    for i, d in enumerate(sessions):
        if i - last_i >= min_gap:
            out.append(d)
            last_i = i
    return out


def session_locator(index: pd.DatetimeIndex, session: date) -> pd.Timestamp | None:
    ts = pd.Timestamp(session)
    if ts in index:
        return ts
    prior = index[index <= ts]
    return prior[-1] if len(prior) else None


def derive_float_mktcap_row(
    cache: PanelCache, ts: pd.Timestamp
) -> pd.Series:
    close = cache.close.loc[ts]
    volume = cache.volume.loc[ts]
    turnover = cache.turnover.loc[ts]
    denom = turnover / 100.0
    mkt = close * volume / denom.replace(0, np.nan)
    mkt = mkt.where(turnover > 0)
    return mkt


def d1_universe(
    cache: PanelCache,
    session: date,
    calendar: pd.DatetimeIndex,
    *,
    listing_min: int = 120,
    u30_threshold: float = 3e7,
    exclude_bottom_pct: float = 0.30,
    waive_u30_on_amount_gap: bool = True,
    med_amount: pd.DataFrame | None = None,
    fm_daily: pd.DataFrame | None = None,
) -> tuple[list[str], dict[str, float], dict]:
    ts = session_locator(cache.close.index, session)
    if ts is None:
        return [], {}, {"error": "no_session"}

    if med_amount is not None and ts in med_amount.index:
        med_amt = med_amount.loc[ts]
    else:
        loc = cache.close.index.get_loc(ts)
        if isinstance(loc, slice):
            loc = loc.stop - 1
        start_i = max(0, int(loc) - 19)
        amt_window = cache.amount.iloc[start_i : int(loc) + 1]
        med_amt = amt_window.median(axis=0)

    close = cache.close.loc[ts]
    tradestatus = cache.tradestatus.loc[ts]
    is_st = cache.is_st.loc[ts]
    limit_up = cache.limit_up.loc[ts]
    limit_down = cache.limit_down.loc[ts]
    open_status = cache.open_status.loc[ts]
    mkt = derive_float_mktcap_row(cache, ts)
    if fm_daily is not None:
        ts_fm = session_locator(fm_daily.index, session)
        if ts_fm is not None:
            row = fm_daily.loc[ts_fm]
            # prefer daily where present
            mkt = mkt.copy()
            for c in row.index:
                v = row.get(c)
                if pd.notna(v):
                    mkt[c] = float(v)

    ids = [c for c in cache.close.columns if pd.notna(close.get(c))]
    stats = {
        "n_with_close": len(ids),
        "session_used": str(ts.date()),
        "waive_u30_on_amount_gap": waive_u30_on_amount_gap,
    }

    # listing age
    cal = calendar
    sess = pd.Timestamp(session)
    kept: list[str] = []
    for iid in ids:
        ld = cache.listing_date.get(iid)
        if ld is None:
            continue
        age = int(((cal >= pd.Timestamp(ld)) & (cal <= sess)).sum())
        if age < listing_min:
            continue
        # ST
        stv = is_st.get(iid)
        if pd.notna(stv) and bool(stv):
            continue
        # suspended
        tr = tradestatus.get(iid)
        suspended = False
        if pd.notna(tr):
            try:
                suspended = float(tr) == 0.0
            except Exception:
                suspended = False
        ost = str(open_status.get(iid, "derived"))
        if ost == "halted":
            suspended = True
        if suspended:
            continue
        if ost not in {"trading", "derived", "nan", "None"} and ost not in {"unknown"}:
            # keep research derived/unknown
            if ost not in {"trading", "derived", "unknown"}:
                continue
        # U30
        ma = med_amt.get(iid)
        amount_gap = pd.isna(cache.amount.loc[ts].get(iid))
        if pd.isna(ma):
            if not (waive_u30_on_amount_gap and amount_gap):
                continue
        elif float(ma) < u30_threshold:
            continue
        # limit-up buy block
        try:
            if pd.notna(limit_up.get(iid)) and pd.notna(close.get(iid)):
                if float(close[iid]) >= float(limit_up[iid]) - 1e-9:
                    continue
        except Exception:
            pass
        kept.append(iid)

    stats["n_after_filters_pre_mktcap"] = len(kept)
    # bottom 30% mktcap — only among names with valid mktcap; keep unknowns if coverage <50%
    mkt_sub = mkt.reindex(kept).dropna()
    cov = len(mkt_sub) / max(1, len(kept))
    stats["mktcap_coverage"] = round(cov, 3)
    if len(mkt_sub) >= 10 and cov >= 0.5:
        thr = mkt_sub.quantile(exclude_bottom_pct)
        kept2 = []
        for i in kept:
            mv = mkt.get(i)
            if pd.isna(mv):
                kept2.append(i)  # unknown mktcap: keep when coverage high? drop safer
                continue
            if float(mv) >= thr:
                kept2.append(i)
        # actually: drop unknown when coverage high
        kept = [i for i in kept if (i in mkt_sub.index and mkt_sub[i] >= thr)]
        stats["mktcap_floor"] = float(thr)
        stats["mktcap_filter"] = "exclude_bottom_pct"
    elif len(mkt_sub) >= 10:
        # low coverage: skip kick-shell rather than collapse universe
        stats["mktcap_floor"] = None
        stats["mktcap_filter"] = "waived_low_coverage"
    else:
        stats["mktcap_floor"] = None
        stats["mktcap_filter"] = "waived_insufficient"
    stats["n_universe"] = len(kept)
    fm = {i: float(mkt[i]) for i in kept if pd.notna(mkt.get(i))}
    return kept, fm, stats



def load_float_mktcap_daily_wide() -> pd.DataFrame | None:
    """Prefer full-market daily float_mktcap (Jun–Oct 2026 research); else None."""
    path = ROOT / "data" / "v2" / "float_mktcap" / "float_mktcap_daily_20260630_20261009.parquet"
    alt = ROOT / "data" / "v2" / "float_mktcap" / "float_mktcap_daily_from_float_share.parquet"
    frames = []
    for pth in (path, alt):
        if pth.is_file():
            df = pd.read_parquet(pth)
            frames.append(df)
    if not frames:
        return None
    df = pd.concat(frames, ignore_index=True)
    df["session"] = pd.to_datetime(df["session"]).dt.normalize()
    df["instrument_id"] = df["instrument_id"].astype(str)
    df = df.dropna(subset=["float_mktcap"])
    df = df.sort_values(["session", "instrument_id"]).drop_duplicates(["session", "instrument_id"], keep="last")
    wide = df.pivot(index="session", columns="instrument_id", values="float_mktcap").sort_index()
    return wide


def load_eps_ttm_pit() -> pd.DataFrame:

    path = ROOT / "data" / "v2" / "financials_pit" / "baostock_eps_ttm_pit.parquet"
    df = pd.read_parquet(path)
    df = df[df["metric"] == "eps_ttm"].copy()
    df["available_at"] = pd.to_datetime(df["available_at"])
    df["instrument_id"] = df["instrument_id"].astype(str)
    return df.sort_values(["instrument_id", "available_at"])


def ep_asof(
    eps_df: pd.DataFrame,
    session: date,
    universe: list[str],
    close_row: pd.Series,
) -> dict[str, float]:
    """V01_EP research proxy: eps_ttm / close with available_at <= session 18:00+."""
    # available before next session open ≈ available_at.date() <= session
    cutoff = pd.Timestamp(session) + pd.Timedelta(hours=18)
    # tz-aware vs naive
    avail = eps_df["available_at"]
    if getattr(avail.dt, "tz", None) is not None:
        cutoff = cutoff.tz_localize("Asia/Shanghai")
    sub = eps_df[eps_df["available_at"] <= cutoff]
    if sub.empty:
        return {}
    # last available per instrument
    last = sub.groupby("instrument_id", sort=False).tail(1)
    last = last[last["instrument_id"].isin(universe)]
    out: dict[str, float] = {}
    for r in last.itertuples():
        px = close_row.get(r.instrument_id)
        if px is None or not (px == px) or float(px) <= 0:
            continue
        eps = float(r.value)
        if not math.isfinite(eps):
            continue
        out[str(r.instrument_id)] = eps / float(px)
    return out


def momentum_m01(close: pd.DataFrame, session: date, universe: list[str]) -> dict[str, float]:
    from quantlab.factors.engine import factor_momentum

    ts = session_locator(close.index, session)
    if ts is None:
        return {}
    cols = [c for c in universe if c in close.columns]
    if not cols:
        return {}
    sub = close[cols]
    moms = factor_momentum(sub)
    m12 = moms["momentum_12m1m"]
    if ts not in m12.index:
        return {}
    row = m12.loc[ts].dropna()
    return {str(k): float(v) for k, v in row.items() if math.isfinite(float(v))}


def sw_labels_asof(sw_members: pd.DataFrame, session: date, ids: list[str]) -> dict[str, str]:
    from quantlab.universe.d1_masks import sw_l1_asof

    assign = sw_l1_asof(sw_members, session, ids)
    out: dict[str, str] = {}
    for iid, a in assign.items():
        if a.is_unknown_bucket or not a.sw_code:
            out[iid] = "UNKNOWN"
        else:
            out[iid] = str(a.sw_code)
    for iid in ids:
        out.setdefault(iid, "UNKNOWN")
    return out


def one_way_turnover(prior: Mapping[str, float], target: Mapping[str, float]) -> float:
    keys = set(prior) | set(target)
    return 0.5 * sum(abs(float(target.get(k, 0.0)) - float(prior.get(k, 0.0))) for k in keys)


def apply_trade_costs(
    *,
    prior_stock: Mapping[str, float],
    new_stock: Mapping[str, float],
    prior_etf: float,
    new_etf: float,
    nav: float,
    session: date,
    commission_bps: float,
    slippage_bps: float,
) -> float:
    """Return cost as fraction of NAV (one-way commission+slippage + sell stamp)."""
    # stock trades
    keys = set(prior_stock) | set(new_stock)
    buy = 0.0
    sell = 0.0
    for k in keys:
        delta = float(new_stock.get(k, 0.0)) - float(prior_stock.get(k, 0.0))
        if delta > 0:
            buy += delta
        else:
            sell += -delta
    etf_delta = new_etf - prior_etf
    if etf_delta > 0:
        buy += etf_delta
    else:
        sell += -etf_delta
    traded = buy + sell
    if traded <= 0 or nav <= 0:
        return 0.0
    # approximate: ignore min commission ¥5 for research speed (note in README)
    one_way = (commission_bps + slippage_bps) / 1e4
    cost = traded * one_way
    cost += sell * stamp_tax_rate(session)
    return cost


def summarize_equity(eq: pd.Series) -> dict:
    eq = eq.dropna()
    if len(eq) < 5:
        return {"error": "too_short", "promotion_approved": False}
    rets = eq.pct_change().dropna()
    n = len(rets)
    years = n / 252.0
    total = float(eq.iloc[-1] / eq.iloc[0] - 1.0)
    ann = (1.0 + total) ** (1.0 / years) - 1.0 if years > 0 else float("nan")
    vol = float(rets.std() * math.sqrt(252)) if len(rets) > 2 else float("nan")
    sharpe = float(ann / vol) if vol and vol > 1e-12 else float("nan")
    peak = eq.cummax()
    dd = eq / peak - 1.0
    maxdd = float(dd.min())
    return {
        "start": str(eq.index[0].date() if hasattr(eq.index[0], "date") else eq.index[0]),
        "end": str(eq.index[-1].date() if hasattr(eq.index[-1], "date") else eq.index[-1]),
        "n_sessions": int(n),
        "years": round(years, 3),
        "total_return": round(total, 6),
        "ann_return": round(ann, 6),
        "ann_vol": round(vol, 6),
        "sharpe": round(sharpe, 4) if sharpe == sharpe else None,
        "max_drawdown": round(maxdd, 6),
        "promotion_approved": False,
        "research_only": True,
        "label": "research_only_promotion_approved_false",
    }


def main() -> int:
    import sys

    sys.path.insert(0, str(ROOT))
    from quantlab.mandate_v2 import load_mandate_v2
    from quantlab.data.v2_readers import (
        default_v2_roots,
        load_merged_calendar,
        load_sw_l1_members,
        resolve_sw_l1_research_path,
    )
    from quantlab.beta.sleeve import PrototypeBetaSleeveProvider
    from quantlab.portfolio.v2_constructor import PortfolioConstructorV2
    from quantlab.factors.residual_factory import (
        ResearchResidualAlphaFactorFactory,
        RawFactorPanel,
        neutralize_raw_values,
        equal_weight_zscore_integrate,
    )
    from quantlab.v2_schemas import SWL1AsOfAssignment
    from quantlab.factors.engine import winsorize_zscore
    from quantlab.universe.d1_masks import sw_l1_asof

    mandate = load_mandate_v2()
    mandate.require_not_promoted()
    roots = default_v2_roots()
    cal_view = load_merged_calendar(d0_root=roots.d0_root, asof_extend_dir=roots.asof_extend_dir)
    calendar = cal_view.sessions.normalize()
    end = pd.Timestamp(calendar.max()).date()
    start = START
    load_start = (pd.Timestamp(start) - pd.Timedelta(days=LOOKBACK_CAL_DAYS)).date()

    instruments = pd.read_parquet(roots.d0_root / "instruments.parquet")
    ids = instruments["instrument_id"].astype(str).tolist()
    if EXCLUDE_BSE:
        ids = [i for i in ids if not i.startswith("bj.")]
    # only those with panel files
    panel_ids = set(p.stem for p in (roots.d0_root / "panels").glob("*.parquet"))
    panel_ids |= set(p.stem for p in (roots.asof_extend_dir / "panels").glob("*.parquet"))
    ids = [i for i in ids if i in panel_ids]
    if MAX_INSTRUMENTS is not None:
        ids = ids[:MAX_INSTRUMENTS]

    _log(f"instruments={len(ids)} sample={start}..{end} rebalance={REBALANCE}")
    cache = preload_panels(
        ids,
        d0_root=roots.d0_root,
        asof_extend_dir=roots.asof_extend_dir,
        start_load=load_start,
        end_load=end,
    )
    if cache.close.empty:
        raise SystemExit("no_close_panel")

    sessions = trading_sessions(calendar, start, end)
    if REBALANCE == "biweekly":
        reb_dates = biweekly_rebalance_dates(sessions, 10)
    else:
        reb_dates = monthly_rebalance_dates(sessions)
    # ensure first session included
    if sessions and reb_dates and reb_dates[0] != sessions[0]:
        reb_dates = [sessions[0]] + [d for d in reb_dates if d > sessions[0]]
    _log(f"sessions={len(sessions)} rebalances={len(reb_dates)}")

    eps_df = load_eps_ttm_pit()
    fm_daily = load_float_mktcap_daily_wide()
    _log(f"fm_daily_wide={None if fm_daily is None else fm_daily.shape}")
    sw_path, sw_variant = resolve_sw_l1_research_path(None)
    sw_members = pd.read_parquet(sw_path)
    _log(f"sw_l1={sw_path.name} variant={sw_variant}")

    beta_prov = PrototypeBetaSleeveProvider(mandate)
    ctor = PortfolioConstructorV2(mandate, proportional_to_score=False)

    commission_bps = float(mandate.costs.commission_bps_one_way)
    slippage_bps = float(mandate.costs.slippage_bps_one_way)
    initial = float(mandate.capital.initial_cny)

    # State
    nav = initial
    stock_w: dict[str, float] = {}
    etf_w = 0.0
    cash_w = 1.0
    equity_rows: list[dict] = []
    holdings_rows: list[dict] = []
    turnovers: list[float] = []
    universe_sizes: list[int] = []

    reb_set = set(reb_dates)
    last_reb: date | None = None

    # Precompute close returns, rolling U30 median, and M01 for speed
    close_ret = cache.close.pct_change()
    _log("precompute median_amount_20d + momentum_12m1m ...")
    med_amount_20d = cache.amount.rolling(20, min_periods=10).median()
    from quantlab.factors.engine import factor_momentum
    _moms = factor_momentum(cache.close)
    mom_panel = _moms["momentum_12m1m"]
    _log(f"precompute done mom_shape={mom_panel.shape}")

    etf_bundle = beta_prov._bundle()
    etf_panel = etf_bundle.panel_frame.copy()
    if "event_time" in etf_panel.columns:
        etf_panel["_et"] = pd.to_datetime(etf_panel["event_time"]).dt.normalize()
    else:
        etf_panel["_et"] = pd.to_datetime(etf_panel.index).normalize()
    etf_panel = etf_panel.sort_values("_et")
    etf_panel = etf_panel[~etf_panel["_et"].duplicated(keep="last")]
    etf_close = pd.Series(
        pd.to_numeric(etf_panel["close"], errors="coerce").values,
        index=pd.DatetimeIndex(etf_panel["_et"]),
    ).sort_index()
    etf_ret = etf_close.pct_change()

    t_loop = time.time()
    for i, sess in enumerate(sessions):
        ts = session_locator(cache.close.index, sess)
        if ts is None:
            continue

        # Mark-to-market overnight return from previous close → today close
        if i > 0 and (stock_w or etf_w > 0):
            day_ret = 0.0
            if stock_w:
                rrow = close_ret.loc[ts] if ts in close_ret.index else None
                if rrow is not None:
                    for k, w in stock_w.items():
                        rv = rrow.get(k)
                        if rv is not None and rv == rv:
                            day_ret += float(w) * float(rv)
            if etf_w > 0 and ts in etf_ret.index:
                er = etf_ret.loc[ts]
                if er == er:
                    day_ret += etf_w * float(er)
            # cash earns 0
            nav *= 1.0 + day_ret

        # Rebalance at close (research approx of decision 18:00 / exec next open)
        if sess in reb_set:
            univ, fm, ustats = d1_universe(cache, sess, calendar, med_amount=med_amount_20d, fm_daily=fm_daily)
            universe_sizes.append(len(univ))
            plan = beta_prov.plan(sess)
            book_cap = plan.residual_book_weight_cap
            if book_cap is None:
                book_cap = max(0.0, 1.0 - float(plan.etf_sleeve_weight or 0.25) - float(plan.cash_weight or 0.05))
            etf_target = float(plan.etf_sleeve_weight or 0.0)
            cash_target = float(plan.cash_weight or 0.0)

            close_row = cache.close.loc[ts]
            # mom from precomputed panel
            if ts in mom_panel.index:
                _mrow = mom_panel.loc[ts].reindex(univ).dropna()
                mom = {str(k): float(v) for k, v in _mrow.items() if v == v}
            else:
                mom = momentum_m01(cache.close, sess, univ)
            ep = ep_asof(eps_df, sess, univ, close_row)

            # Z-score raw then neutralize via SW
            sw_assign_map = sw_l1_asof(sw_members, sess, univ)
            sw_seq = tuple(sw_assign_map[i] for i in univ if i in sw_assign_map)
            # fill missing unknowns
            present = set(sw_assign_map)
            for iid in univ:
                if iid not in present:
                    sw_seq = sw_seq + (
                        SWL1AsOfAssignment(
                            instrument_id=iid,
                            session=sess,
                            sw_code=None,
                            sw_name=None,
                            available_at=None,
                            quality_status=None,
                            is_unknown_bucket=True,
                        ),
                    )

            residuals = []
            for fid, raw_map in (("M01_12_1", mom), ("V01_EP", ep)):
                if not raw_map:
                    continue
                z = winsorize_zscore(pd.Series(raw_map, dtype=float))
                raw_z = {str(k): float(v) for k, v in z.dropna().items()}
                vals, covered, unknown = neutralize_raw_values(
                    raw_z, sw_seq, mktcap=fm, mktcap_neutral=False
                )
                from quantlab.factors.residual_factory import ResidualFactorPanel

                residuals.append(
                    ResidualFactorPanel(
                        factor_id=fid,
                        session=sess,
                        industry_scheme="SW_L1",
                        mktcap_neutral=False,
                        values=vals,
                        sw_l1_coverage=covered,
                        unknown_industry_count=unknown,
                        promotion_approved=False,
                        data_ready=bool(vals),
                        todos=("research_only",),
                    )
                )
            composite = equal_weight_zscore_integrate(
                residuals, mode="integrate", member_ids=("M01_12_1", "V01_EP")
            )
            labels = {
                iid: (
                    "UNKNOWN"
                    if sw_assign_map.get(iid) is None
                    or sw_assign_map[iid].is_unknown_bucket
                    or not sw_assign_map[iid].sw_code
                    else str(sw_assign_map[iid].sw_code)
                )
                for iid in univ
            }
            # prior stock weights renormalized within residual book for turnover
            prior_book = dict(stock_w)
            result = ctor.construct(
                composite.scores,
                session=sess,
                industry_labels=labels,
                prior_weights=None,  # research v1: hard refresh to max_n; turnover measured vs prior
                universe=univ,
                book_weight_cap=book_cap,
            )
            new_stock = dict(result.weights)
            # Enforce Mandate max names after turnover blend (clip can reintroduce names)
            max_n = int(mandate.portfolio_limits.max_positions_stocks)
            if len(new_stock) > max_n:
                top = sorted(new_stock.items(), key=lambda kv: kv[1], reverse=True)[:max_n]
                s = sum(v for _, v in top) or 1.0
                # keep residual book scale (= sum before trim, capped by book_cap)
                book_sum = min(float(book_cap), sum(new_stock.values()))
                new_stock = {k: (v / s) * book_sum for k, v in top}
            # Scale so stock + etf + cash = 1
            stock_sum = sum(new_stock.values())
            # etf/cash from beta; if stock_sum < book_cap, cash absorbs
            etf_target = min(etf_target, max(0.0, 1.0 - stock_sum - cash_target))
            # costs
            cost_frac = apply_trade_costs(
                prior_stock=stock_w,
                new_stock=new_stock,
                prior_etf=etf_w,
                new_etf=etf_target,
                nav=nav,
                session=sess,
                commission_bps=commission_bps,
                slippage_bps=slippage_bps,
            )
            nav *= max(0.0, 1.0 - cost_frac)
            to = one_way_turnover(
                {**{f"etf:{etf_w}": etf_w}, **stock_w} if False else stock_w,
                new_stock,
            )
            # include etf in turnover
            to = one_way_turnover(
                {**stock_w, "__etf__": etf_w},
                {**new_stock, "__etf__": etf_target},
            )
            turnovers.append(to)
            stock_w = new_stock
            etf_w = etf_target
            cash_w = max(0.0, 1.0 - sum(stock_w.values()) - etf_w)
            last_reb = sess
            holdings_rows.append(
                {
                    "session": str(sess),
                    "n_names": len(stock_w),
                    "stock_weight_sum": round(sum(stock_w.values()), 6),
                    "etf_weight": round(etf_w, 6),
                    "cash_weight": round(cash_w, 6),
                    "book_cap": round(float(book_cap), 6),
                    "universe_n": len(univ),
                    "turnover_one_way": round(to, 6),
                    "cost_frac": round(cost_frac, 6),
                    "n_scores": len(composite.scores),
                    "promotion_approved": False,
                }
            )
            if len(holdings_rows) % 6 == 1:
                _log(
                    f"reb {sess} univ={len(univ)} names={len(stock_w)} "
                    f"etf={etf_w:.3f} nav={nav:,.0f} scores={len(composite.scores)}"
                )

        equity_rows.append(
            {
                "session": str(sess),
                "nav": nav,
                "stock_w": sum(stock_w.values()),
                "etf_w": etf_w,
                "cash_w": cash_w,
            }
        )

    _log(f"loop done in {time.time()-t_loop:.0f}s")

    eq_df = pd.DataFrame(equity_rows)
    eq_df["session"] = pd.to_datetime(eq_df["session"])
    eq_df = eq_df.set_index("session").sort_index()
    eq_df["nav"] = eq_df["nav"] / initial  # start at 1.0
    # rebuild nav series properly — we stored absolute then divided
    # Actually we mutated nav from initial; normalize to 1.0 at start
    if len(eq_df):
        # re-scale: first nav point should be ~1 after costs maybe
        first = float(eq_df["nav"].iloc[0])
        if first > 0:
            # already divided by initial once — wait we divided absolute by initial
            pass
    # Fix: equity_rows stored absolute CNY nav; divide by initial for index
    # Already done above. But first day before any ret should be 1.0
    eq_path_csv = OUT / "equity_curve.csv"
    eq_path_pq = OUT / "equity_curve.parquet"
    out_eq = eq_df.reset_index()
    out_eq["promotion_approved"] = False
    out_eq["research_only"] = True
    out_eq.to_csv(eq_path_csv, index=False)
    out_eq.to_parquet(eq_path_pq, index=False)

    nav_series = out_eq.set_index("session")["nav"]
    metrics = summarize_equity(nav_series)
    metrics.update(
        {
            "initial_cny": initial,
            "rebalance": REBALANCE,
            "sample_start_requested": str(start),
            "sample_end": str(end),
            "n_rebalances": len(holdings_rows),
            "avg_universe": round(float(np.mean(universe_sizes)), 1) if universe_sizes else None,
            "avg_turnover_one_way": round(float(np.mean(turnovers)), 4) if turnovers else None,
            "median_names": int(np.median([h["n_names"] for h in holdings_rows])) if holdings_rows else None,
            "factors": ["M01_12_1", "V01_EP"],
            "beta_etf": "510300",
            "sw_l1": sw_path.name,
            "costs": {
                "commission_bps": commission_bps,
                "slippage_bps": slippage_bps,
                "stamp_tax": "historical_CN_table",
                "min_commission_ignored": True,
            },
            "promotion_approved": False,
            "research_only": True,
        }
    )
    metrics_path = OUT / "summary_metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    hold_df = pd.DataFrame(holdings_rows)
    hold_df.to_csv(OUT / "rebalance_log.csv", index=False)

    readme = f"""# V1 研究级纸面净值（第一版）

**状态**：`research_only` · `promotion_approved=false`  
**生成时间**：{datetime.now().isoformat(timespec="seconds")}（America/New_York 盒时钟）  
**路径**：`output/v1_paper/`

## 关键数字（过程指标，非晋级结论）

| 指标 | 值 |
|---|---|
| 样本 | {metrics.get('start')} → {metrics.get('end')} |
| 年化收益 | {metrics.get('ann_return')} |
| 年化波动 | {metrics.get('ann_vol')} |
| Sharpe | {metrics.get('sharpe')} |
| 最大回撤 | {metrics.get('max_drawdown')} |
| 再平衡次数 | {metrics.get('n_rebalances')} |
| 平均单边换手 | {metrics.get('avg_turnover_one_way')} |
| 中位持股数 | {metrics.get('median_names')} |

## 结构

1. **宇宙**：合并面板上的 D1 类掩码（上市≥120、踢 ST/停牌/涨停买、U30 在 amount 缺口研究豁免、踢后 30% 流通市值代理）。剔除北交所。
2. **Beta**：`PrototypeBetaSleeveProvider` → 510300，vol16%/β0.70/回撤缩放；`max_etf` 不抬高。
3. **Alpha**：M01_12_1（价量动量）+ V01_EP（baostock `eps_ttm/close`，`available_at` 代理）→ 申万一级研究表中性 → 等权 integrate。
4. **组合**：Mandate 30–60、单票 5%、行业 25%；残差书受 Beta `residual_book_weight_cap` 约束。
5. **再平衡**：本跑为 **{REBALANCE}**（Mandate 默认双周；全市场预载后月度更稳，双周可改开关重跑）。
6. **成本**：佣金 {commission_bps}bp + 滑点 {slippage_bps}bp；印花税按 2023-08-28 前后历史卖出税率。最低佣金 ¥5 未逐笔计入（研究近似）。

## 产物

- `equity_curve.csv` / `equity_curve.parquet` — 净值曲线（起点≈1）
- `summary_metrics.json` — 汇总指标（含 `promotion_approved=false`）
- `rebalance_log.csv` — 再平衡摘要
- `README_ZH.md` — 本说明

## 明确限制（不可晋级）

- 申万 PIT 为研究重建（XLS-prefix），非官方进出史。
- 财务 `available_at` 为公告日代理，**无 as-filed 重述链**。
- 流通市值多为面板派生（close×volume/turnover），非券商级 PIT。
- asof_extend 段 amount 大量缺失 → U30 研究豁免，流动性过滤偏松。
- 执行用收盘再平衡近似，非「决策 18:00 / 次日开盘」严格账本。
- 未做除权公司行动完整账本；未过 Harvey 多重检验。
- **任何年化/Sharpe 仅作流水线冒烟，不得当作实盘或晋级证据。**

## 协调

Strategy / Eng / Alpha / Beta / Data 可只读消费本目录；勿改 `promotion_approved`。
"""
    (OUT / "README_ZH.md").write_text(readme, encoding="utf-8")
    _log(f"wrote {OUT}")
    _log(json.dumps({k: metrics[k] for k in ('ann_return','ann_vol','sharpe','max_drawdown','n_rebalances')}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
