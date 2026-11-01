"""Exploration-window ablation for the three recorded designs.

Window is 2024-06-03 through 2026-06-30. That is after the sealed window and
inside the D0 panels, which end on 2026-06-30. promotion stays false.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from quantlab.config import CONFIG, ROOT
from quantlab.data.v2_readers import financials_metric_asof, load_financials_pit
from quantlab.factors.engine import (
    factor_flow,
    factor_momentum,
    factor_price_crowding,
    factor_value_kline,
    factor_volatility,
)
from quantlab.mandate_v2 import load_mandate_v2
from quantlab.metrics import summary
from quantlab.platform.execution import ExecConfig, ExecPanels, run_weight_schedule
from quantlab.portfolio.v2_constructor import PortfolioConstructorV2
from quantlab.smallcap.universe import ADV_WINDOW, MIN_ADV, RANK_END, RANK_START
from quantlab.strategy.experts import experts_score
from quantlab.universe.d1_masks import sw_l1_asof

D0 = ROOT / "data/local_market/1c85fd9aceaa03c3c4863bec"
OUT = ROOT / "output/rd_ablation_20261101"
START = pd.Timestamp("2024-06-03")
END = pd.Timestamp("2026-06-30")
HIST = pd.Timestamp("2023-01-01")
HOLD = 60
GROSS = 0.98
MIN_OBS = 253


def _as_session_index(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame
    if isinstance(out.index, pd.DatetimeIndex):
        idx = pd.to_datetime(out.index)
    elif "event_time" in out.columns:
        out = frame.copy()
        idx = pd.to_datetime(out["event_time"])
    else:
        return frame.iloc[0:0]
    if getattr(idx, "tz", None) is not None:
        idx = idx.tz_convert("Asia/Shanghai").tz_localize(None)
    elif hasattr(idx, "dt") and getattr(idx.dt, "tz", None) is not None:
        idx = idx.dt.tz_convert("Asia/Shanghai").dt.tz_localize(None)
    out = out.copy()
    out.index = pd.DatetimeIndex(idx)
    return out


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


def load_amount_store(ids: list[str]) -> dict:
    store = {}
    panels = D0 / "panels"
    for iid in ids:
        path = panels / f"{iid}.parquet"
        if not path.is_file():
            continue
        frame = pd.read_parquet(path, columns=["amount"])
        packed = _positive(frame["amount"])
        if packed is not None:
            store[iid] = packed
    return store


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


def stable_book(pool: list[str], n: int = HOLD) -> list[str]:
    """Retired. Lexicographic order filled the book with Beijing names.

    The user does not trade Beijing Stock Exchange names, and Mandate line 69
    excludes them by default. Do not report a code-order book as a result.
    """
    raise ValueError("code_order_book_retired: excludes neither bj nor a real unscored sample")


def load_prices(ids: list[str]) -> dict[str, pd.DataFrame]:
    frames = {}
    for iid in ids:
        path = D0 / "panels" / f"{iid}.parquet"
        if not path.is_file():
            continue
        import pyarrow.parquet as pq
        present = set(pq.ParquetFile(path).schema_arrow.names)
        columns = [name for name in ("event_time", "open", "close", "volume", "amount", "turnover") if name in present]
        frame = _as_session_index(pd.read_parquet(path, columns=columns))
        if not isinstance(frame.index, pd.DatetimeIndex) or frame.empty:
            continue
        frame = frame[(frame.index >= HIST) & (frame.index <= END)]
        frames[iid] = frame
    return frames


def field_frame(prices: dict[str, pd.DataFrame], column: str, index) -> pd.DataFrame:
    data = {}
    for iid, frame in prices.items():
        if column in frame.columns:
            data[iid] = frame[column].reindex(index)
    return pd.DataFrame(data, index=index)


def run_book(panels: ExecPanels, schedule: dict, cash: float) -> dict:
    result = run_weight_schedule(
        panels, schedule, initial_cash=cash, config=ExecConfig.strategy_v1(), record_weights=False,
    )
    nav = result["nav"]
    stats = summary(nav)
    stats["strategy_promotion_approved"] = False
    stats["terminal_nav"] = float(nav.iloc[-1])
    return stats


def expert_picks(close, amount, turnover, pool: list[str], day, ic_use: pd.DataFrame):
    cols = [iid for iid in pool if iid in close.columns]
    if len(cols) < HOLD:
        return None, ic_use
    hist_close = close.loc[:day, cols]
    hist_amount = amount.loc[:day, cols]
    hist_turn = turnover.loc[:day, cols]
    full = {}
    full.update(factor_momentum(hist_close))
    full.update(factor_value_kline(hist_close, hist_amount))
    full["factor_volatility"] = factor_volatility(hist_close)
    full.update(factor_flow(hist_amount, hist_turn))
    full["factor_price_crowding"] = factor_price_crowding(hist_close, hist_turn)
    full = {name: frame.dropna(how="all") for name, frame in full.items() if frame is not None}
    weights = pd.DataFrame({name: 1.0 for name in full}, index=pd.DatetimeIndex([day]))
    ic = ic_use.reindex(columns=list(full.keys()))
    if ic.dropna(how="all").empty:
        ic = pd.DataFrame(0.0, index=pd.DatetimeIndex([day - pd.Timedelta(days=1)]), columns=list(full.keys()))
    score, _expert_weights = experts_score({k: v for k, v in full.items()}, weights, None, ic)
    if score is None or score.empty:
        return None, ic_use
    last = score.iloc[-1].dropna().sort_values(ascending=False)
    picks = list(last.index[:HOLD])
    # IC for the next decision uses this day's factor and the return through the next session only after it exists.
    return picks, (full, last)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    instruments = pd.read_parquet(D0 / "instruments.parquet", columns=["instrument_id", "asset_type"])
    instruments = instruments[instruments["asset_type"].isin(["stock", "equity_etf"])]
    ids = [str(item) for item in instruments["instrument_id"] if str(item) != "sh.510300"]
    calendar = pd.read_parquet(D0 / "calendar.parquet")
    sessions = pd.DatetimeIndex(pd.to_datetime(calendar["session"])).normalize()
    sessions = sessions[(sessions >= HIST) & (sessions <= END)]
    grid = sessions[sessions >= START][::10]
    print(json.dumps({"stage": "grid", "n": int(len(grid)), "first": str(grid[0].date()), "last": str(grid[-1].date())}), flush=True)

    store = load_amount_store(ids)
    print(json.dumps({"stage": "amount", "names": len(store)}), flush=True)
    wide = {day: wide_pool(store, day) for day in grid}
    wide_books = {day: stable_book(pool) for day, pool in wide.items()}

    members = pd.read_parquet(
        ROOT / "data/v2/universe/mid_large_members_pit.parquet",
        columns=["session", "instrument_id", "available_at"],
    )
    members["session"] = pd.to_datetime(members["session"]).dt.normalize()
    members = members[members["session"].isin(grid)]
    published = members["available_at"].map(lambda value: _known(value))
    # row-wise against its own session
    known = []
    for session, available in zip(members["session"], members["available_at"]):
        known.append(_known_by(available, session))
    members = members.loc[np.array(known)]
    mid = {}
    mid_books = {}
    for day, group in members.groupby("session"):
        pool = sorted(set(group["instrument_id"].astype(str)))
        mid[pd.Timestamp(day)] = pool
        mid_books[pd.Timestamp(day)] = stable_book(pool)

    overlaps = []
    for day in grid:
        a = set(wide.get(day, []))
        b = set(mid.get(day, []))
        denom = len(a | b)
        overlaps.append(len(a & b) / denom if denom else None)
    finite = [item for item in overlaps if item is not None]
    report = {
        "window": [str(START.date()), str(END.date())],
        "sealed_window_rerun": False,
        "strategy_promotion_approved": False,
        "grid_sessions": int(len(grid)),
        "wide_days_with_names": int(sum(bool(wide[day]) for day in grid)),
        "wide_median_pool": int(np.median([len(wide[day]) for day in grid])),
        "mid_days_with_names": int(sum(bool(mid.get(day)) for day in grid)),
        "mid_median_pool": int(np.median([len(mid.get(day, [])) for day in grid])),
        "u30_status": "failed_data",
        "u30_reason": "data/v2/float_mktcap/float_mktcap_daily_tushare.parquet is not in the release",
        "pool_jaccard_median": None if not finite else float(np.median(finite)),
        "executed_jaccard_median": _executed_jaccard(grid, wide_books, mid_books),
    }
    print(json.dumps({"stage": "pools", **{k: report[k] for k in ("wide_median_pool", "mid_median_pool", "pool_jaccard_median")}}), flush=True)

    needed = {"sh.510300"}
    for pool in wide.values():
        needed.update(pool)
    for book in mid_books.values():
        needed.update(book)
    prices = load_prices(sorted(needed))
    index = sessions[(sessions >= START) & (sessions <= END)]
    hist_index = sessions[(sessions >= HIST) & (sessions <= END)]
    panels = ExecPanels(
        close=field_frame(prices, "close", index),
        open=field_frame(prices, "open", index),
        volume=field_frame(prices, "volume", index),
        amount=field_frame(prices, "amount", index),
    )
    bench = {day: {"sh.510300": GROSS} for day in grid}
    report["books"] = {}
    for label, books in (("wide_unscored", wide_books), ("mid_unscored", mid_books), ("hs300_etf", bench)):
        schedule = {day: {iid: GROSS / len(names) for iid in names} if names else {} for day, names in books.items()}
        report["books"][label] = {
            str(int(cash)): run_book(panels, schedule, cash) for cash in (600_000.0, 1_000_000.0)
        }
        print(json.dumps({"stage": "book", "label": label, "cagr60": report["books"][label]["600000"]["cagr"]}), flush=True)

    frozen_days = wide_books
    factor_schedule, factor_note = _factor_schedule(prices, hist_index, grid, wide, frozen_days)
    report["factor_note"] = factor_note
    if factor_schedule:
        report["books"]["wide_five_experts"] = {
            str(int(cash)): run_book(panels, factor_schedule, cash) for cash in (600_000.0, 1_000_000.0)
        }
    financial_schedule, financial_note = _financial_schedule(grid, wide)
    report["financial_note"] = financial_note
    if financial_schedule:
        names = sorted({iid for day in financial_schedule.values() for iid in day})
        extra = [iid for iid in names if iid not in prices]
        if extra:
            prices.update(load_prices(extra))
            panels = ExecPanels(
                close=field_frame(prices, "close", index),
                open=field_frame(prices, "open", index),
                volume=field_frame(prices, "volume", index),
                amount=field_frame(prices, "amount", index),
            )
        report["books"]["wide_net_profit"] = {
            str(int(cash)): run_book(panels, financial_schedule, cash) for cash in (600_000.0, 1_000_000.0)
        }
    report["event_note"] = "failed_data: quantlab/factors/event_pipeline.py names data/v2/free_hunt/fundamentals/cninfo_periodic_announcements_sample.parquet, which is not in the release"
    portfolio = _portfolio(prices, hist_index, grid, frozen_days)
    for label, schedule in portfolio.pop("schedules", {}).items():
        report["books"][label] = {
            str(int(cash)): run_book(panels, schedule, cash) for cash in (600_000.0, 1_000_000.0)
        }
    report["portfolio"] = portfolio
    path = OUT / "summary.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps({"stage": "wrote", "path": str(path)}), flush=True)


def _known_by(value, session: pd.Timestamp) -> bool:
    if value is None or pd.isna(value):
        return False
    stamp = pd.Timestamp(value)
    if stamp.tzinfo is None:
        stamp = stamp.tz_localize("Asia/Shanghai")
    else:
        stamp = stamp.tz_convert("Asia/Shanghai")
    cutoff = pd.Timestamp(session).tz_localize("Asia/Shanghai") + pd.Timedelta(hours=18)
    return stamp <= cutoff


def _known(value) -> bool:
    return value is not None and not pd.isna(value)


def _executed_jaccard(grid, left, right) -> float | None:
    scores = []
    for day in grid:
        a, b = set(left.get(day, [])), set(right.get(day, []))
        denom = len(a | b)
        if denom:
            scores.append(len(a & b) / denom)
    return None if not scores else float(np.median(scores))


def _factor_schedule(prices, index, grid, pools, fallback_books):
    close = field_frame(prices, "close", index)
    amount = field_frame(prices, "amount", close.index)
    turnover = field_frame(prices, "turnover", close.index)
    ic_rows = []
    schedule = {}
    previous_scores = None
    previous_day = None
    try:
        for day in grid:
            pool = pools.get(day) or []
            cols = [iid for iid in pool if iid in close.columns]
            if len(cols) < 30:
                names = fallback_books.get(day) or []
                schedule[day] = {iid: GROSS / len(names) for iid in names} if names else {}
                continue
            hist_close = close.loc[:day, cols]
            full = {}
            full.update(factor_momentum(hist_close))
            full.update(factor_value_kline(hist_close, amount.loc[:day, cols]))
            full["factor_volatility"] = factor_volatility(hist_close)
            full.update(factor_flow(amount.loc[:day, cols], turnover.loc[:day, cols]))
            full["factor_price_crowding"] = factor_price_crowding(hist_close, turnover.loc[:day, cols])
            weights = pd.DataFrame({name: 1.0 for name in full}, index=pd.DatetimeIndex([day]))
            if ic_rows:
                ic_use = pd.DataFrame(ic_rows)
                ic_use.index = pd.DatetimeIndex(ic_use.index)
            else:
                ic_use = pd.DataFrame(0.0, index=pd.DatetimeIndex([day - pd.Timedelta(days=1)]), columns=list(full))
            score, _weights = experts_score(full, weights, None, ic_use.reindex(columns=list(full.keys())))
            last = None if score is None or score.empty else score.iloc[-1].dropna().sort_values(ascending=False)
            if last is None or last.empty:
                return {}, "experts_score returned no row"
            picks = list(last.index[:HOLD])
            schedule[day] = {iid: GROSS / len(picks) for iid in picks}
            if previous_scores is not None and previous_day in close.index and day in close.index:
                realized = close.loc[day] / close.loc[previous_day] - 1
                row = {}
                for name, series in previous_scores.items():
                    aligned = realized.reindex(series.index)
                    row[name] = _spearman(series, aligned)
                ic_rows.append(row)
            previous_scores = {name: frame.iloc[-1] for name, frame in full.items()}
            previous_day = day
        return schedule, "experts_score on the wide pool; IC uses only the previous rebalance's completed return"
    except Exception as exc:  # noqa: BLE001
        return {}, f"experts_score_failed:{type(exc).__name__}:{exc}"


def sessions_for(prices):
    index = None
    for frame in prices.values():
        index = frame.index if index is None else index.union(frame.index)
    return index.sort_values()


def _spearman(left: pd.Series, right: pd.Series) -> float:
    from scipy.stats import spearmanr
    rho, _p = spearmanr(left, right)
    return float(rho) if np.isfinite(rho) else float("nan")


def _financial_schedule(grid, pools):
    try:
        view = load_financials_pit()
    except Exception as exc:  # noqa: BLE001
        return {}, f"load_financials_pit_failed:{type(exc).__name__}:{exc}"
    if "net_profit" not in view.frame.columns or "available_at" not in view.frame.columns:
        return {}, "failed_data: financials file has no net_profit or available_at"
    schedule = {}
    for day in grid:
        pool = pools.get(day) or []
        if not pool:
            schedule[day] = {}
            continue
        values = financials_metric_asof(view.frame, day.date(), pool, "net_profit", negative_as_missing=True)
        ordered = sorted(values, key=lambda iid: (-values[iid], iid))
        picks = ordered[:HOLD]
        schedule[day] = {iid: GROSS / len(picks) for iid in picks} if len(picks) >= 30 else {}
    covered = sum(bool(weights) for weights in schedule.values())
    if covered < len(grid) / 2:
        return {}, f"failed_data: net_profit covered {covered}/{len(grid)} rebalance days"
    return schedule, "financials_metric_asof net_profit, available_at strictly before the session, negative dropped"


def _portfolio(prices, index, grid, books):
    close = field_frame(prices, "close", index)
    returns = close.pct_change(fill_method=None)
    sw = pd.read_parquet(ROOT / "data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet")
    mandate = load_mandate_v2()
    constructor = PortfolioConstructorV2(mandate, proportional_to_score=False, weighting_mode="equal_stub")
    from copy import deepcopy
    cfg = deepcopy(CONFIG)
    cfg.portfolio.target_vol = 0.16
    vol_schedule = {}
    cap_schedule = {}
    notes = []
    prior = {}
    for day in grid:
        names = [iid for iid in books.get(day, []) if iid in returns.columns]
        if len(names) < 5:
            vol_schedule[day] = {}
            cap_schedule[day] = {}
            continue
        hist = returns.loc[:day, names].iloc[:-1].tail(120)
        labels = sw_l1_asof(sw, day.date(), names)
        industry = {iid: (labels[iid].sw_name or "UNKNOWN") for iid in names if iid in labels}
        try:
            built = constructor.construct(
                {iid: 1.0 for iid in names},
                session=day.date(),
                industry_labels=industry,
                prior_weights=prior,
                universe=names,
            )
            weights = built.weights
            cap_schedule[day] = {iid: float(weight) for iid, weight in weights.items()}
            prior = cap_schedule[day]
            notes.append({"day": str(day.date()), "turnover_clipped": built.turnover_clipped, "n": built.n_names})
        except Exception as exc:  # noqa: BLE001
            cap_schedule[day] = {}
            notes.append({"day": str(day.date()), "constructor": f"{type(exc).__name__}:{exc}"})
        vol_schedule[day] = _vol_weights(hist, names, cfg, industry)
    return {
        "constructor_days": len(notes),
        "constructor_clipped_days": int(sum(bool(row.get("turnover_clipped")) for row in notes)),
        "constructor_errors": [row for row in notes if "constructor" in row][:5],
        "vol_empty_days": int(sum(not bool(weights) or "_status" in weights or "_error" in weights for weights in vol_schedule.values())),
        "vol_statuses": sorted({str(weights.get("_status") or weights.get("_error")) for weights in vol_schedule.values() if isinstance(weights, dict) and ("_status" in weights or "_error" in weights)})[:8],
        "schedules": {
            "wide_target_vol": {day: {k: v for k, v in weights.items() if not str(k).startswith("_")} for day, weights in vol_schedule.items()},
            "wide_constructor": cap_schedule,
        },
    }


def _vol_weights(hist: pd.DataFrame, names: list[str], cfg, industry: dict[str, str]):
    from quantlab.strategy.allocation import allocate
    if len(hist) < 40:
        return {}
    frame = pd.DataFrame({
        "asset_type": "stock",
        "sector": [industry.get(iid) or "UNKNOWN" for iid in names],
        "buy_lot": 100,
        "sell_lot": 100,
        "sell_delay": 1,
        "price_tick": 0.01,
        "commission": 0.00025,
        "min_commission": 5.0,
        "limit_ratio": 0.10,
    }, index=names)
    exposures = pd.get_dummies(pd.Series({iid: industry.get(iid) or "UNKNOWN" for iid in names})).T
    expected = pd.Series(1.0, index=names)
    try:
        weights, status = allocate(
            hist, frame, exposures, cfg, gross=GROSS, expected=expected, industry_policy="unknown_capped",
        )
    except Exception as exc:  # noqa: BLE001
        return {"_error": f"{type(exc).__name__}:{exc}"}
    if status != "ok":
        return {"_status": status}
    return {iid: float(weight) for iid, weight in weights.items() if weight > 0}


if __name__ == "__main__":
    main()
