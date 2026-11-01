"""Exploration-window pool sign test. Not a tradable account.

Follows docs/rd/experiments/universe.md. Does not call stable_book, does not
cut the band to 60 names, and does not read adj_close. promotion stays false.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from quantlab.config import ROOT
from quantlab.platform.execution import ExecConfig
from quantlab.smallcap.universe import ADV_WINDOW, MIN_ADV, RANK_END, RANK_START

MIN_OBS = 253

D0 = ROOT / "data/local_market/1c85fd9aceaa03c3c4863bec"
OUT = ROOT / "output/rd_pool_sign_20261101"
START = pd.Timestamp("2024-06-03")
END = pd.Timestamp("2026-06-30")
HIST = pd.Timestamp("2023-01-01")
ST_PATH = ROOT / "data/v2/st_flags/is_st_daily_2018_2026.parquet"
DELIST_PATH = ROOT / "data/v2/ref/stock_delisted_v2.parquet"
FLOAT_PATH = ROOT / "data/v2/float_mktcap/float_mktcap_daily_tushare_pit.parquet"
MID_PATH = ROOT / "data/v2/universe/mid_large_members_pit.parquet"
DIV_PATH = ROOT / "data/v2/corporate_actions/dividend_by_exdate_tushare.parquet"
LISTING_MIN = 120
AMOUNT_MEDIAN_MIN = 30_000_000.0
FLOAT_DROP_BOTTOM = 0.30
SLIPPAGE_5BP = 0.0005


def _positive(series: pd.Series):
    values = pd.to_numeric(series, errors="coerce")
    if not isinstance(values.index, pd.DatetimeIndex):
        return None
    values = values[(values.index >= HIST) & (values.index <= END)]
    values = values[values > 0]
    if len(values) < ADV_WINDOW:
        return None
    return values.index.to_numpy(dtype="datetime64[ns]"), values.to_numpy(dtype=float)


def amount_on(dates, values, day: pd.Timestamp):
    position = int(np.searchsorted(dates, np.datetime64(day), side="right") - 1)
    if position < MIN_OBS - 1 or dates[position] != np.datetime64(day):
        return None
    window = values[position - ADV_WINDOW + 1:position + 1]
    if len(window) < ADV_WINDOW:
        return None
    return float(window.mean())


def wide_pool(store, day: pd.Timestamp) -> list[str]:
    observations = []
    for iid, (dates, values) in store.items():
        amount = amount_on(dates, values, day)
        if amount is not None:
            observations.append((amount, iid))
    observations.sort(key=lambda item: (-item[0], item[1]))
    if len(observations) < RANK_START:
        return []
    chosen = []
    for rank, (amount, iid) in enumerate(observations, start=1):
        if rank < RANK_START:
            continue
        if rank > RANK_END:
            break
        if amount >= MIN_ADV:
            chosen.append(iid)
    return chosen


def load_amount_store(ids: list[str]):
    """Positive-amount store for the existing rank band, plus full series for the 20-day median."""
    store = {}
    medians = {}
    panels = D0 / "panels"
    for iid in ids:
        path = panels / f"{iid}.parquet"
        if not path.is_file():
            continue
        import pyarrow.parquet as pq
        names = set(pq.ParquetFile(path).schema_arrow.names)
        columns = ["amount"] + (["event_time"] if "event_time" in names else [])
        frame = pd.read_parquet(path, columns=columns)
        if "event_time" in frame.columns:
            stamp = pd.to_datetime(frame["event_time"])
        elif isinstance(frame.index, pd.DatetimeIndex):
            stamp = frame.index
        else:
            continue
        if getattr(getattr(stamp, "dt", None), "tz", None) is not None:
            stamp = stamp.dt.tz_convert("Asia/Shanghai").dt.tz_localize(None)
        elif getattr(stamp, "tz", None) is not None:
            stamp = stamp.tz_convert("Asia/Shanghai").tz_localize(None)
        amount = pd.Series(pd.to_numeric(frame["amount"], errors="coerce").to_numpy(), index=pd.DatetimeIndex(stamp))
        amount = amount[~amount.index.duplicated(keep="last")].sort_index()
        packed = _positive(amount)
        if packed is not None:
            store[iid] = packed
        ordered = amount.sort_index()
        ordered = ordered[(ordered.index >= HIST) & (ordered.index <= END)]
        medians[iid] = (
            ordered.index.to_numpy(dtype="datetime64[ns]"),
            ordered.to_numpy(dtype=float),
        )
    return store, medians


def shanghai_date(value) -> date | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    stamp = pd.Timestamp(value)
    if pd.isna(stamp):
        return None
    if stamp.tzinfo is None:
        stamp = stamp.tz_localize("Asia/Shanghai")
    else:
        stamp = stamp.tz_convert("Asia/Shanghai")
    return stamp.date()


def ymd(value) -> date | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    text = str(value).strip()
    if text in ("", "NaT", "None", "nan"):
        return None
    digits = "".join(ch for ch in text[:10] if ch.isdigit())
    if len(digits) < 8:
        return shanghai_date(value)
    return date(int(digits[:4]), int(digits[4:6]), int(digits[6:8]))


def is_beijing(instrument_id: str) -> bool:
    return str(instrument_id).startswith("bj.")


def st_by_day(frame: pd.DataFrame) -> dict[pd.Timestamp, set[str]]:
    """Days present in the ST table. The file stores only is_st_at_open True."""
    day = pd.to_datetime(frame["trade_date"]).dt.normalize()
    grouped: dict[pd.Timestamp, set[str]] = {}
    for stamp, iid in zip(day, frame["instrument_id"].astype(str)):
        grouped.setdefault(pd.Timestamp(stamp), set()).add(iid)
    return grouped


def delist_cleanup_rows(frame: pd.DataFrame) -> list[tuple[str, date, date, date]]:
    rows = []
    flag = frame["entered_delisting_period_v2"].fillna(False).astype(bool)
    for record in frame.loc[flag].itertuples(index=False):
        start = ymd(getattr(record, "delist_period_start"))
        end = ymd(getattr(record, "delist_date"))
        available = shanghai_date(getattr(record, "available_at"))
        iid = str(getattr(record, "instrument_id"))
        if start is None or end is None or available is None:
            continue
        rows.append((iid, start, end, available))
    return rows


def cleanup_ids(rows: list[tuple[str, date, date, date]], session: date) -> set[str]:
    """Names whose cleanup period is already visible and covers this session."""
    return {
        iid
        for iid, start, end, available in rows
        if available < session and start <= session <= end
    }


def filter_names(ids: list[str], day: pd.Timestamp, st_days: dict, cleanup: set[str]) -> tuple[list[str], str]:
    key = pd.Timestamp(day).normalize()
    if key not in st_days:
        return [], "st_day_missing"
    blocked = st_days[key] | cleanup
    kept = [iid for iid in ids if not is_beijing(iid) and iid not in blocked]
    return kept, ""


def median_on(dates: np.ndarray, values: np.ndarray, day: pd.Timestamp) -> float | None:
    if len(dates) == 0:
        return None
    position = int(np.searchsorted(dates, np.datetime64(day), side="right") - 1)
    if position < 0 or dates[position] != np.datetime64(day):
        return None
    window = values[max(0, position - 19):position + 1]
    window = window[np.isfinite(window)]
    if len(window) < 10:
        return None
    return float(np.median(window))


def listing_age(listing: date | None, session: pd.Timestamp, calendar: pd.DatetimeIndex) -> int | None:
    if listing is None:
        return None
    start = int(calendar.searchsorted(pd.Timestamp(listing), side="left"))
    end = int(calendar.searchsorted(session, side="right"))
    if end <= start:
        return 0
    return end - start


def period_return(entry_open: float, exit_open: float, cash: float, share_ratio: float) -> float | None:
    if not np.isfinite(entry_open) or not np.isfinite(exit_open) or entry_open <= 0:
        return None
    return float((exit_open * (1.0 + share_ratio) + cash) / entry_open - 1.0)


def traded_cost(previous: dict[str, float], current: dict[str, float], commission: float, stamp: float) -> tuple[float, float]:
    """Return (strategy_v1 cash cost, extra 5bp two-sided slippage) as fractions of gross."""
    names = set(previous) | set(current)
    turnover_l1 = sum(abs(current.get(name, 0.0) - previous.get(name, 0.0)) for name in names)
    sell = 0.5 * turnover_l1
    primary = turnover_l1 * commission + sell * stamp
    sensitivity = turnover_l1 * SLIPPAGE_5BP
    return float(primary), float(sensitivity)


def compound(returns: list[float]) -> float:
    nav = 1.0
    for value in returns:
        nav *= 1.0 + value
    return nav


def sign_of(value: float) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def jaccard(left: set[str], right: set[str]) -> float | None:
    union = left | right
    if not union:
        return None
    return len(left & right) / len(union)


def load_opens(ids: list[str]) -> dict[str, dict[pd.Timestamp, float]]:
    frames = {}
    panels = D0 / "panels"
    for iid in ids:
        path = panels / f"{iid}.parquet"
        if not path.is_file():
            continue
        import pyarrow.parquet as pq
        names = set(pq.ParquetFile(path).schema_arrow.names)
        columns = ["open"] + (["event_time"] if "event_time" in names else [])
        frame = pd.read_parquet(path, columns=columns)
        if "event_time" in frame.columns:
            stamp = pd.to_datetime(frame["event_time"])
        elif isinstance(frame.index, pd.DatetimeIndex):
            stamp = frame.index
        else:
            continue
        if getattr(getattr(stamp, "dt", None), "tz", None) is not None:
            stamp = stamp.dt.tz_convert("Asia/Shanghai").dt.tz_localize(None)
        elif getattr(stamp, "tz", None) is not None:
            stamp = stamp.tz_convert("Asia/Shanghai").tz_localize(None)
        opens = pd.to_numeric(frame["open"], errors="coerce")
        frames[iid] = {
            pd.Timestamp(day).normalize(): float(price)
            for day, price in zip(stamp, opens)
            if pd.notna(price)
        }
    return frames


def load_dividends() -> dict[str, list[tuple[date, float, float]]]:
    if not DIV_PATH.is_file():
        return {}
    frame = pd.read_parquet(DIV_PATH, columns=["ts_code", "ex_date", "div_proc", "cash_div_tax", "stk_div"])
    frame = frame[frame["div_proc"].astype(str) == "实施"]
    out: dict[str, list[tuple[date, float, float]]] = {}
    for record in frame.itertuples(index=False):
        ex = ymd(record.ex_date)
        iid = _ts_to_instrument(record.ts_code)
        if ex is None or iid is None:
            continue
        cash = float(record.cash_div_tax) if pd.notna(record.cash_div_tax) else 0.0
        shares = float(record.stk_div) if pd.notna(record.stk_div) else 0.0
        if cash == 0.0 and shares == 0.0:
            continue
        out.setdefault(iid, []).append((ex, cash, shares))
    return out


def _ts_to_instrument(code: str) -> str | None:
    text = str(code)
    if text.count(".") != 1:
        return None
    number, exchange = text.split(".", 1)
    prefix = {"SH": "sh.", "SZ": "sz.", "BJ": "bj."}.get(exchange.upper())
    if prefix is None:
        return None
    return f"{prefix}{number}"


def action_between(actions: list[tuple[date, float, float]], start: date, end: date) -> tuple[float, float]:
    cash = 0.0
    shares = 0.0
    for ex, cash_div, stk in actions:
        if start < ex <= end:
            cash += cash_div
            shares += stk
    return cash, shares


def equal_weights(names: list[str]) -> dict[str, float]:
    if not names:
        return {}
    weight = 1.0 / len(names)
    return {name: weight for name in names}


def arm_periods(grid, sessions, books, opens, dividends, bench_opens, commission: float, stamp: float) -> dict:
    session_list = list(sessions)
    index = {pd.Timestamp(day).normalize(): pos for pos, day in enumerate(session_list)}
    gross_port, net_port, net_5bp, bench = [], [], [], []
    previous: dict[str, float] = {}
    used = 0
    for left, right in zip(grid[:-1], grid[1:]):
        entry = _next_session(index, session_list, pd.Timestamp(left).normalize())
        exit_ = _next_session(index, session_list, pd.Timestamp(right).normalize())
        if entry is None or exit_ is None:
            continue
        names = books.get(pd.Timestamp(left).normalize(), [])
        member_returns = []
        for iid in names:
            series = opens.get(iid)
            if series is None:
                continue
            start_px = series.get(entry)
            end_px = series.get(exit_)
            cash, shares = action_between(dividends.get(iid, []), entry.date(), exit_.date())
            value = period_return(start_px if start_px is not None else np.nan, end_px if end_px is not None else np.nan, cash, shares)
            if value is not None:
                member_returns.append(value)
        bench_start = bench_opens.get(entry)
        bench_end = bench_opens.get(exit_)
        bench_value = period_return(bench_start if bench_start is not None else np.nan, bench_end if bench_end is not None else np.nan, 0.0, 0.0)
        if not member_returns or bench_value is None:
            previous = equal_weights(names)
            continue
        gross = float(np.mean(member_returns))
        current = equal_weights(names)
        primary, extra = traded_cost(previous, current, commission, stamp)
        gross_port.append(gross)
        net_port.append(gross - primary)
        net_5bp.append(gross - primary - extra)
        bench.append(bench_value)
        previous = current
        used += 1
    return {
        "periods": used,
        "gross": gross_port,
        "net_strategy_v1_rates": net_port,
        "net_plus_5bp_slippage": net_5bp,
        "benchmark": bench,
    }


def _next_session(index, session_list, day: pd.Timestamp) -> pd.Timestamp | None:
    pos = index.get(day)
    if pos is None or pos + 1 >= len(session_list):
        return None
    return pd.Timestamp(session_list[pos + 1]).normalize()


def excess_sign(portfolio: list[float], benchmark: list[float]) -> dict:
    if not portfolio:
        return {"excess": None, "sign": None}
    excess = compound(portfolio) / compound(benchmark) - 1.0
    return {"excess": excess, "sign": sign_of(excess)}


def load_prior_float(prior_days: set[pd.Timestamp]) -> dict[tuple[pd.Timestamp, str], float]:
    if not FLOAT_PATH.is_file():
        raise FileNotFoundError(str(FLOAT_PATH))
    frame = pd.read_parquet(FLOAT_PATH, columns=["instrument_id", "trade_date", "float_mktcap", "available_at"])
    frame["trade_date"] = pd.to_datetime(frame["trade_date"]).dt.normalize()
    frame = frame[frame["trade_date"].isin(prior_days)]
    out = {}
    for record in frame.itertuples(index=False):
        if not pd.notna(record.float_mktcap):
            continue
        out[(pd.Timestamp(record.trade_date).normalize(), str(record.instrument_id))] = float(record.float_mktcap)
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    config = ExecConfig.strategy_v1()
    stamp = config.stamp_after
    instruments = pd.read_parquet(D0 / "instruments.parquet", columns=["instrument_id", "asset_type", "listing_date"])
    instruments = instruments[instruments["asset_type"].astype(str).isin(["stock", "equity_etf"])]
    instruments = instruments[instruments["instrument_id"].astype(str) != "sh.510300"]
    listing = {
        str(iid): ymd(listed)
        for iid, listed in zip(instruments["instrument_id"], instruments["listing_date"])
    }
    ids = list(listing)
    print(json.dumps({"stage": "ids", "n": len(ids)}), flush=True)
    calendar = pd.read_parquet(D0 / "calendar.parquet")
    sessions = pd.DatetimeIndex(pd.to_datetime(calendar["session"])).normalize()
    sessions = sessions[(sessions >= HIST) & (sessions <= END)]
    grid = list(sessions[sessions >= START][::10])
    st_days = st_by_day(pd.read_parquet(ST_PATH, columns=["instrument_id", "trade_date", "is_st_at_open"]))
    cleanup_rows = delist_cleanup_rows(pd.read_parquet(
        DELIST_PATH,
        columns=["instrument_id", "available_at", "entered_delisting_period_v2", "delist_period_start", "delist_date"],
    ))
    store, medians = load_amount_store(ids)
    print(json.dumps({"stage": "amount", "names": len(store), "grid": len(grid)}), flush=True)
    wide_raw = {pd.Timestamp(day).normalize(): wide_pool(store, pd.Timestamp(day)) for day in grid}
    wide, wide_gap = _apply_all(wide_raw, grid, st_days, cleanup_rows)
    d1_raw = _d1_pools(ids, grid, sessions, listing, medians, st_days, cleanup_rows)
    d1, d1_gap = d1_raw["books"], d1_raw["gap_days"]
    mid_raw, mid_meta = _mid_pools(grid)
    mid, mid_gap = _apply_all(mid_raw, grid, st_days, cleanup_rows) if mid_raw is not None else ({}, ["mid_large_missing"])
    print(json.dumps({"stage": "pools", "wide_gap": len(wide_gap), "d1_gap": len(d1_gap)}), flush=True)
    report = _summarize(grid, wide, d1, mid, wide_gap, d1_gap, mid_gap, sessions, config, stamp, d1_raw, mid_meta)
    path = OUT / "summary.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "wrote": str(path),
        "same_sign": report["same_sign"],
        "stop": report["stop_no_formula_change"],
        "signs": {name: report["arms"][name]["sign_net"] for name in report["arms"]},
    }, ensure_ascii=False), flush=True)


def _apply_all(raw: dict, grid, st_days, cleanup_rows):
    books = {}
    gaps = []
    for day in grid:
        key = pd.Timestamp(day).normalize()
        kept, reason = filter_names(raw.get(key, []), key, st_days, cleanup_ids(cleanup_rows, key.date()))
        books[key] = kept
        if reason:
            gaps.append(str(key.date()))
    return books, gaps


def _d1_pools(ids, grid, sessions, listing, medians, st_days, cleanup_rows) -> dict:
    if not FLOAT_PATH.is_file():
        return {"books": {}, "gap_days": ["float_pit_missing"], "status": "failed_data"}
    prior = {}
    session_list = list(sessions)
    for day in grid:
        pos = int(sessions.searchsorted(pd.Timestamp(day).normalize(), side="left"))
        prior[pd.Timestamp(day).normalize()] = None if pos <= 0 else pd.Timestamp(session_list[pos - 1]).normalize()
    floats = load_prior_float({day for day in prior.values() if day is not None})
    books = {}
    gaps = []
    for day in grid:
        key = pd.Timestamp(day).normalize()
        if key not in st_days:
            books[key] = []
            gaps.append(str(key.date()))
            continue
        blocked_st = st_days[key]
        blocked_delist = cleanup_ids(cleanup_rows, key.date())
        ranked = []
        previous = prior[key]
        for iid in ids:
            if is_beijing(iid) or iid in blocked_st or iid in blocked_delist:
                continue
            age = listing_age(listing.get(iid), key, sessions)
            if age is None or age < LISTING_MIN:
                continue
            series = medians.get(iid)
            if series is None:
                continue
            median = median_on(series[0], series[1], key)
            if median is None or median < AMOUNT_MEDIAN_MIN:
                continue
            if previous is None:
                continue
            cap = floats.get((previous, iid))
            if cap is None:
                continue
            if shanghai_date_ok(previous, key):
                ranked.append((cap, iid))
        if not ranked:
            books[key] = []
            continue
        cutoff = float(np.quantile([cap for cap, _iid in ranked], FLOAT_DROP_BOTTOM))
        books[key] = [iid for cap, iid in ranked if cap > cutoff]
    return {"books": books, "gap_days": gaps, "status": "ok", "float_path": str(FLOAT_PATH)}


def shanghai_date_ok(previous: pd.Timestamp, decision: pd.Timestamp) -> bool:
    """Prior session 18:00 proxy is visible at the next session open."""
    return previous.date() < decision.date()


def visible_at_close(available, session: pd.Timestamp) -> bool:
    """True when the timestamp is at or before 18:00 Asia/Shanghai on the session."""
    from quantlab.data.contracts import decision_time, timestamp

    published = timestamp(available)
    if pd.isna(published):
        return False
    return published <= decision_time(session.date())


def _mid_pools(grid) -> tuple[dict | None, dict]:
    if not MID_PATH.is_file():
        return None, {"status": "failed_data", "reason": "mid_large file missing"}
    frame = pd.read_parquet(MID_PATH, columns=["session", "instrument_id", "available_at"])
    frame["session"] = pd.to_datetime(frame["session"]).dt.normalize()
    wanted = {pd.Timestamp(day).normalize() for day in grid}
    frame = frame[frame["session"].isin(wanted)]
    books = {day: [] for day in wanted}
    visible = 0
    for record in frame.itertuples(index=False):
        session = pd.Timestamp(record.session).normalize()
        if not visible_at_close(record.available_at, session):
            continue
        visible += 1
        books[session].append(str(record.instrument_id))
    return books, {
        "status": "ok",
        "rows_on_grid": int(len(frame)),
        "rows_visible_at_close": visible,
        "clock": "available_at <= decision_time 18:00 Asia/Shanghai",
    }


def _summarize(grid, wide, d1, mid, wide_gap, d1_gap, mid_gap, sessions, config, stamp, d1_meta, mid_meta) -> dict:
    needed = ["sh.510300"]
    for books in (wide, d1, mid):
        for names in books.values():
            needed.extend(names)
    opens = load_opens(sorted(set(needed)))
    bench = opens.get("sh.510300", {})
    dividends = load_dividends()
    arms = {}
    for label, books, gaps in (
        ("wide", wide, wide_gap),
        ("d1_midlarge", d1, d1_gap),
        ("mid_large", mid, mid_gap),
    ):
        periods = arm_periods(grid, sessions, books, opens, dividends, bench, config.commission, stamp)
        net = excess_sign(periods["net_strategy_v1_rates"], periods["benchmark"])
        extra = excess_sign(periods["net_plus_5bp_slippage"], periods["benchmark"])
        sizes = [len(books.get(pd.Timestamp(day).normalize(), [])) for day in grid]
        arms[label] = {
            "status": "gap" if gaps else "ok",
            "gap_days": gaps,
            "median_names": int(np.median(sizes)) if sizes else 0,
            "periods": periods["periods"],
            "sign_net": None if gaps else net["sign"],
            "excess_net": None if gaps else net["excess"],
            "sign_5bp_sensitivity": None if gaps else extra["sign"],
            "tradable_cagr": None,
            "tradable_reason": "full eligible set is not a 30-60 name account",
        }
    if mid_meta.get("rows_on_grid") and mid_meta.get("rows_visible_at_close") == 0:
        arms["mid_large"]["status"] = "empty_after_available_at_date_rule"
    pair_names = (("wide", "d1_midlarge"), ("wide", "mid_large"), ("d1_midlarge", "mid_large"))
    overlaps = {}
    for left, right in pair_names:
        values = []
        for day in grid:
            key = pd.Timestamp(day).normalize()
            value = jaccard(set(wide_or(left, wide, d1, mid, key)), set(wide_or(right, wide, d1, mid, key)))
            if value is not None:
                values.append(value)
        overlaps[f"{left}_vs_{right}"] = None if not values else float(np.median(values))
    signs = [arms[name]["sign_net"] for name in arms]
    same = len(set(signs)) == 1 and signs[0] not in (None, 0)
    return {
        "window": [str(START.date()), str(END.date())],
        "sealed_window_rerun": False,
        "strategy_promotion_approved": False,
        "price": "raw open plus corporate_actions cash and share ratio",
        "adj_close_used": False,
        "cost_primary": "ExecConfig.strategy_v1 commission and stamp on equal-weight turnover; slippage 0; impact not applied",
        "slippage": config.slippage,
        "impact_k": config.impact_k,
        "commission": config.commission,
        "stamp_after": stamp,
        "slippage_5bp": "sensitivity only",
        "grid_sessions": len(grid),
        "stable_book_called": False,
        "cut_to_60": False,
        "arms": arms,
        "jaccard_median": overlaps,
        "same_sign": same,
        "stop_no_formula_change": same,
        "experts_changed": False,
        "constructor_caps_changed": False,
        "d1_status": d1_meta.get("status", "ok"),
        "mid_large_clock": mid_meta,
        "float_known_by": "prior session, visible at the next open",
    }


def wide_or(label, wide, d1, mid, key):
    return {"wide": wide, "d1_midlarge": d1, "mid_large": mid}[label].get(key, [])


if __name__ == "__main__":
    main()
