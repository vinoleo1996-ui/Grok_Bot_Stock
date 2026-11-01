"""Stable Strategy paper-v1 feed (Platform Eng).

Thin facade over :mod:`quantlab.data.v2_readers`, :mod:`quantlab.universe.d1_masks`,
and :mod:`quantlab.portfolio.v2_rebalance`. Does **not** change
PortfolioConstructorV2 / Alpha / Beta research conclusions. Does **not** write
NAV — Strategy owns ``output/strategy_paper_v1/``.

``promotion_approved`` forced False everywhere.

Memory knobs (Full D1 / ~15Gi box):
  - ``merged_close_panel(..., chunk_size=250, dtype="float32")``
  - ``iter_merged_close_chunks`` — never hold full wide panel
  - optional feather/parquet disk cache under ``output/strategy_feed_cache/``
  - ``d1_members_at`` per session (do not cache all sessions' frames)
  - pass ``close_panel=`` into ``merged_daily_returns`` (no second load)
"""
from __future__ import annotations

from quantlab.promotion_gate import overall_promotion_approved as _gate

from datetime import date
from pathlib import Path
from typing import Iterator, Sequence

import pandas as pd

from quantlab.config import ROOT
from quantlab.data.v2_readers import (
    V2DataRoots,
    default_v2_roots,
    load_etf_510300,
    load_merged_calendar,
    load_merged_panel,
)
from quantlab.mandate_v2 import MandateV2, load_mandate_v2
from quantlab.portfolio.v2_rebalance import RebalanceScheduleV2, min_sessions_for_cadence
from quantlab.universe.d1_masks import D1MaskConfig, D1MaskResult, build_d1_masks_for_session

# Strategy-owned output root (Eng documents only; does not invent NAV).
STRATEGY_PAPER_V1_OUTPUT_DIR = ROOT / "output" / "strategy_paper_v1"

# Research disk cache for wide close panels (optional).
STRATEGY_FEED_CACHE_DIR = ROOT / "output" / "strategy_feed_cache"
STRATEGY_PAPER_V1_CACHE_DIR = STRATEGY_PAPER_V1_OUTPUT_DIR / "_cache"

# Defaults Strategy asked for (~2024-01-01 → latest tradeable).
DEFAULT_PAPER_START = date(2024, 1, 1)
DEFAULT_PAPER_START_FAST = date(2024, 6, 1)

# Recommended Full-D1 memory defaults (box ~15Gi, no swap).
DEFAULT_CLOSE_CHUNK_SIZE = 300
DEFAULT_CLOSE_DTYPE = "float32"


def _as_date(value: date | str) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def _resolve_end(
    start_d: date,
    end: date | str | None,
    *,
    roots: V2DataRoots,
) -> date:
    if end is None:
        cal = load_merged_calendar(roots=roots)
        return cal.last_session or start_d
    return _as_date(end)


def _normalize_dtype(dtype: str | None) -> str:
    if dtype is None:
        return DEFAULT_CLOSE_DTYPE
    d = str(dtype).lower().strip()
    if d in ("float32", "f4", "f32"):
        return "float32"
    if d in ("float64", "f8", "f64", "float"):
        return "float64"
    raise ValueError(f"unsupported_close_dtype:{dtype}")


def _chunk_ids(ids: Sequence[str], chunk_size: int) -> Iterator[list[str]]:
    buf = [str(x) for x in ids]
    n = max(1, int(chunk_size))
    for i in range(0, len(buf), n):
        yield buf[i : i + n]


def _close_series_one(
    iid: str,
    *,
    lo: pd.Timestamp,
    hi: pd.Timestamp,
    roots: V2DataRoots,
    dtype: str,
) -> pd.Series | None:
    view = load_merged_panel(str(iid), roots=roots)
    if view.frame is None or view.frame.empty or "close" not in view.frame.columns:
        return None
    frame = view.frame
    et = pd.to_datetime(frame["event_time"]).dt.normalize()
    mask = (et >= lo) & (et <= hi)
    # Avoid full-frame .copy(); take only needed columns then filter.
    sub = frame.loc[mask, ["event_time", "close"]]
    if sub.empty:
        return None
    et2 = pd.to_datetime(sub["event_time"]).dt.normalize()
    closes = pd.to_numeric(sub["close"], errors="coerce")
    # last observation per session
    tmp = pd.DataFrame({"_et": et2, "close": closes})
    tmp = tmp.drop_duplicates(subset=["_et"], keep="last")
    s = pd.Series(
        tmp["close"].to_numpy(dtype=dtype, copy=False),
        index=pd.Index([ts.date() for ts in tmp["_et"]], name="session"),
        name=str(iid),
        dtype=dtype,
    )
    return s


def _sessions_in_range(
    start: date,
    end: date,
    *,
    calendar: Sequence[date] | pd.DatetimeIndex | None = None,
    roots: V2DataRoots | None = None,
) -> list[date]:
    if calendar is None:
        view = load_merged_calendar(roots=roots or default_v2_roots())
        idx = view.sessions
    elif isinstance(calendar, pd.DatetimeIndex):
        idx = calendar.tz_localize(None).normalize() if calendar.tz is not None else calendar.normalize()
    else:
        idx = pd.DatetimeIndex(pd.to_datetime(list(calendar))).normalize()
    lo, hi = pd.Timestamp(start), pd.Timestamp(end)
    clipped = idx[(idx >= lo) & (idx <= hi)]
    return [ts.date() for ts in clipped]


def trading_sessions(
    start: date | str = DEFAULT_PAPER_START,
    end: date | str | None = None,
    *,
    calendar: Sequence[date] | pd.DatetimeIndex | None = None,
    roots: V2DataRoots | None = None,
) -> list[date]:
    """Merged D0+asof_extend trading sessions in ``[start, end]``.

    If ``end`` is None, use merged calendar last session.
    """
    roots = roots or default_v2_roots()
    start_d = _as_date(start)
    if end is None:
        view = load_merged_calendar(roots=roots)
        if view.last_session is None:
            return []
        end_d = view.last_session
        if calendar is None:
            calendar = view.sessions
    else:
        end_d = _as_date(end)
    return _sessions_in_range(start_d, end_d, calendar=calendar, roots=roots)


def iter_merged_close_chunks(
    instrument_ids: Sequence[str],
    start: date | str = DEFAULT_PAPER_START,
    end: date | str | None = None,
    *,
    chunk_size: int = DEFAULT_CLOSE_CHUNK_SIZE,
    dtype: str = DEFAULT_CLOSE_DTYPE,
    roots: V2DataRoots | None = None,
) -> Iterator[pd.DataFrame]:
    """Yield wide close chunks (index=session, columns=ids) without holding the full panel.

    Prefer this over :func:`merged_close_panel` when peak RAM matters. Default
    ``dtype=float32``. Research-only; ``promotion_approved`` not claimed.
    """
    roots = roots or default_v2_roots()
    start_d = _as_date(start)
    end_d = _resolve_end(start_d, end, roots=roots)
    lo, hi = pd.Timestamp(start_d), pd.Timestamp(end_d)
    dt = _normalize_dtype(dtype)
    n = max(1, int(chunk_size))

    for chunk in _chunk_ids(instrument_ids, n):
        series_map: dict[str, pd.Series] = {}
        for iid in chunk:
            s = _close_series_one(iid, lo=lo, hi=hi, roots=roots, dtype=dt)
            if s is not None:
                series_map[str(iid)] = s
        if not series_map:
            yield pd.DataFrame(dtype=dt)
            continue
        out = pd.DataFrame(series_map)
        out = out.astype(dt, copy=False)
        out.index = pd.Index(out.index, name="session")
        yield out.sort_index()


def merged_close_panel(
    instrument_ids: Sequence[str],
    start: date | str = DEFAULT_PAPER_START,
    end: date | str | None = None,
    *,
    roots: V2DataRoots | None = None,
    chunk_size: int | None = None,
    dtype: str = DEFAULT_CLOSE_DTYPE,
    use_disk_cache: bool = False,
    cache_dir: Path | str | None = None,
    cache_format: str = "feather",
) -> pd.DataFrame:
    """Wide close panel from D0+asof_extend merge.

    Parameters
    ----------
    chunk_size:
        If set (e.g. 200–400), load instrument ids in chunks then column-concat.
        Peak RAM ≈ one chunk of panels + growing float32 frame.
    dtype:
        ``float32`` (default, half RAM vs float64) or ``float64``.
    use_disk_cache:
        If True, read/write a research cache file under
        ``output/strategy_feed_cache/`` (or ``cache_dir``).

    Returns
    -------
    DataFrame
        index = session (date), columns = instrument_id, values = close.
        Missing bars are NaN. ``promotion_approved`` not claimed.
    """
    roots = roots or default_v2_roots()
    start_d = _as_date(start)
    end_d = _resolve_end(start_d, end, roots=roots)
    dt = _normalize_dtype(dtype)
    ids = [str(x) for x in instrument_ids]

    if use_disk_cache:
        cached = load_cached_close_panel(
            ids,
            start_d,
            end_d,
            dtype=dt,
            cache_dir=cache_dir,
            cache_format=cache_format,
        )
        if cached is not None:
            return cached

    if chunk_size is None:
        # Single-pass (legacy path). Still float32 by default.
        lo, hi = pd.Timestamp(start_d), pd.Timestamp(end_d)
        series_map: dict[str, pd.Series] = {}
        for iid in ids:
            s = _close_series_one(iid, lo=lo, hi=hi, roots=roots, dtype=dt)
            if s is not None:
                series_map[str(iid)] = s
        if not series_map:
            out = pd.DataFrame(dtype=dt)
        else:
            out = pd.DataFrame(series_map).astype(dt, copy=False)
            out.index = pd.Index(out.index, name="session")
            out = out.sort_index()
    else:
        parts: list[pd.DataFrame] = []
        for part in iter_merged_close_chunks(
            ids,
            start_d,
            end_d,
            chunk_size=int(chunk_size),
            dtype=dt,
            roots=roots,
        ):
            if part is not None and not part.empty:
                parts.append(part)
        if not parts:
            out = pd.DataFrame(dtype=dt)
        else:
            out = pd.concat(parts, axis=1)
            # Drop duplicate columns if any id repeated
            if out.columns.duplicated().any():
                out = out.loc[:, ~out.columns.duplicated(keep="last")]
            out = out.astype(dt, copy=False).sort_index()
            out.index = pd.Index(out.index, name="session")

    if use_disk_cache and not out.empty:
        cache_merged_close_panel(
            out,
            ids,
            start_d,
            end_d,
            dtype=dt,
            cache_dir=cache_dir,
            cache_format=cache_format,
        )
    return out


def _cache_key_stem(
    instrument_ids: Sequence[str],
    start: date,
    end: date,
    *,
    dtype: str,
) -> str:
    import hashlib

    h = hashlib.sha1()
    from quantlab.data.v2_readers import DEFAULT_ASOF_EXTEND_DIR

    # extend source in key: accepted-default switch (tushare) invalidates old caches
    h.update(f"{start.isoformat()}|{end.isoformat()}|{dtype}|{len(instrument_ids)}|{DEFAULT_ASOF_EXTEND_DIR.name}".encode())
    for iid in instrument_ids:
        h.update(b"\0")
        h.update(str(iid).encode())
    return f"close_{start.isoformat()}_{end.isoformat()}_{dtype}_{h.hexdigest()[:12]}"


def resolve_feed_cache_dir(cache_dir: Path | str | None = None) -> Path:
    if cache_dir is None:
        return STRATEGY_FEED_CACHE_DIR
    return Path(cache_dir)


def cache_merged_close_panel(
    panel: pd.DataFrame,
    instrument_ids: Sequence[str],
    start: date | str,
    end: date | str,
    *,
    dtype: str = DEFAULT_CLOSE_DTYPE,
    cache_dir: Path | str | None = None,
    cache_format: str = "feather",
) -> Path:
    """Write research close panel to feather/parquet. Returns path written."""
    start_d, end_d = _as_date(start), _as_date(end)
    dt = _normalize_dtype(dtype)
    root = resolve_feed_cache_dir(cache_dir)
    root.mkdir(parents=True, exist_ok=True)
    stem = _cache_key_stem(instrument_ids, start_d, end_d, dtype=dt)
    fmt = str(cache_format).lower().strip()
    if fmt not in ("feather", "parquet"):
        raise ValueError(f"unsupported_cache_format:{cache_format}")
    path = root / f"{stem}.{fmt}"
    to_store = panel.copy()
    # Feather wants string/Range/Datetime index — store session as column.
    to_store = to_store.reset_index()
    if fmt == "feather":
        to_store.to_feather(path)
    else:
        to_store.to_parquet(path, index=False)
    meta = {
        "promotion_approved": _gate(),
        "n_ids": len(instrument_ids),
        "start": start_d.isoformat(),
        "end": end_d.isoformat(),
        "dtype": dt,
        "format": fmt,
        "path": str(path),
    }
    (root / f"{stem}.meta.json").write_text(
        __import__("json").dumps(meta, indent=2), encoding="utf-8"
    )
    return path


def load_cached_close_panel(
    instrument_ids: Sequence[str],
    start: date | str,
    end: date | str,
    *,
    dtype: str = DEFAULT_CLOSE_DTYPE,
    cache_dir: Path | str | None = None,
    cache_format: str = "feather",
) -> pd.DataFrame | None:
    """Load research close cache if present and column set matches; else None."""
    start_d, end_d = _as_date(start), _as_date(end)
    dt = _normalize_dtype(dtype)
    root = resolve_feed_cache_dir(cache_dir)
    stem = _cache_key_stem(instrument_ids, start_d, end_d, dtype=dt)
    fmt = str(cache_format).lower().strip()
    path = root / f"{stem}.{fmt}"
    if not path.is_file():
        # try the other format
        alt = root / f"{stem}.{'parquet' if fmt == 'feather' else 'feather'}"
        if alt.is_file():
            path = alt
            fmt = alt.suffix.lstrip(".")
        else:
            return None
    if fmt == "feather":
        df = pd.read_feather(path)
    else:
        df = pd.read_parquet(path)
    if "session" in df.columns:
        df = df.set_index("session")
    elif "index" in df.columns:
        df = df.set_index("index")
        df.index.name = "session"
    # Coerce index to date
    df.index = pd.Index(
        [
            x if isinstance(x, date) and not isinstance(x, pd.Timestamp) else pd.Timestamp(x).date()
            for x in df.index
        ],
        name="session",
    )
    want = [str(x) for x in instrument_ids]
    have = set(map(str, df.columns))
    if any(w not in have for w in want):
        # Incomplete cache — ignore
        return None
    out = df.loc[:, want].astype(dt, copy=False)
    return out.sort_index()


def close_to_close_returns(closes, total_return_factor=None):
    """Mark-to-close daily returns that never drop a move across halts.

    Suspended / missing interior sessions carry the last close (return 0 that
    day) and the full cumulative move is realized on the resumption session.
    Leading (pre-listing) and trailing (post-delist) NaNs are left as NaN.
    Trading restrictions (limit-up/down, halt) must only block fills, never
    valuation — callers must not zero these returns on restricted days.
    """
    filled = closes.ffill(limit_area="inside")
    if total_return_factor is not None:
        # Opt-in (2026-10-11): raw closes x cumulative total-return factor (e.g.
        # quantlab.platform.execution.total_return_factor or the D0 'factor'), so ex-dividend /
        # bonus-share drops are not booked as losses. Default None keeps legacy raw-close returns.
        f = total_return_factor.reindex(index=filled.index, columns=filled.columns).ffill()
        filled = filled * f.where(f > 0)
    return filled.pct_change(fill_method=None)


def held_book_return(weights, returns_row) -> float:
    """Weighted book return at close; limit/halt days are NOT zeroed (NaN→0 only
    for names with no price at all, i.e. pre-listing/post-delist)."""
    total = 0.0
    for iid, w in weights.items():
        if not w:
            continue
        r = returns_row.get(iid, float("nan")) if hasattr(returns_row, "get") else float("nan")
        try:
            r = float(r)
        except (TypeError, ValueError):
            continue
        if r == r and r not in (float("inf"), float("-inf")):
            total += float(w) * r
    return total


def merged_daily_returns(
    instrument_ids: Sequence[str],
    start: date | str = DEFAULT_PAPER_START,
    end: date | str | None = None,
    *,
    roots: V2DataRoots | None = None,
    close_panel: pd.DataFrame | None = None,
    chunk_size: int | None = None,
    dtype: str = DEFAULT_CLOSE_DTYPE,
) -> pd.DataFrame:
    """Simple daily returns from :func:`merged_close_panel` (pct_change).

    First session per column is NaN. Pass ``close_panel`` to avoid reloading
    (required for Full D1 memory hygiene).
    """
    if close_panel is not None:
        closes = close_panel
    else:
        closes = merged_close_panel(
            instrument_ids,
            start=start,
            end=end,
            roots=roots,
            chunk_size=chunk_size,
            dtype=dtype,
        )
    if closes.empty:
        return closes.copy()
    # pct_change promotes to float64 in some pandas versions — cast back
    rets = close_to_close_returns(closes)
    dt = _normalize_dtype(dtype)
    if str(rets.dtypes.iloc[0]) != dt:
        rets = rets.astype(dt, copy=False)
    return rets


def iter_merged_daily_return_chunks(
    instrument_ids: Sequence[str],
    start: date | str = DEFAULT_PAPER_START,
    end: date | str | None = None,
    *,
    chunk_size: int = DEFAULT_CLOSE_CHUNK_SIZE,
    dtype: str = DEFAULT_CLOSE_DTYPE,
    roots: V2DataRoots | None = None,
) -> Iterator[pd.DataFrame]:
    """Yield return chunks from :func:`iter_merged_close_chunks` (no full panel)."""
    for part in iter_merged_close_chunks(
        instrument_ids,
        start,
        end,
        chunk_size=chunk_size,
        dtype=dtype,
        roots=roots,
    ):
        if part.empty:
            yield part
        else:
            rets = close_to_close_returns(part)
            dt = _normalize_dtype(dtype)
            yield rets.astype(dt, copy=False)


def biweekly_rebalance_sessions(
    start: date | str = DEFAULT_PAPER_START,
    end: date | str | None = None,
    *,
    calendar: Sequence[date] | pd.DatetimeIndex | None = None,
    mandate: MandateV2 | None = None,
    roots: V2DataRoots | None = None,
) -> list[date]:
    """Ordinary rebalance sessions for Mandate ``ordinary_rebalance`` (default biweekly).

    Walks merged trading calendar; marks a session due when trading-session gap
    since last rebalance >= :func:`min_sessions_for_cadence` (biweekly → 10).
    First in-range session is always due. Research-only; no live orders.
    """
    roots = roots or default_v2_roots()
    m = mandate or load_mandate_v2()
    m.require_not_promoted()
    schedule = RebalanceScheduleV2(m)
    sessions = trading_sessions(start, end, calendar=calendar, roots=roots)
    if not sessions:
        return []

    due: list[date] = []
    last: date | None = None
    for sess in sessions:
        decision = schedule.is_ordinary_rebalance_session(
            sess, last_rebalance=last, calendar=sessions
        )
        if decision.ordinary_rebalance_due:
            due.append(sess)
            last = sess
    _ = min_sessions_for_cadence(schedule.cadence)
    return due


def etf_510300_daily_returns(
    start: date | str = DEFAULT_PAPER_START,
    end: date | str | None = None,
    *,
    roots: V2DataRoots | None = None,
) -> pd.Series:
    """sh.510300 simple daily returns from ``data/v2/etf_510300`` panel.

    Index = session (date), name = ``sh.510300``. First bar NaN.
    """
    roots = roots or default_v2_roots()
    start_d = _as_date(start)
    bundle = load_etf_510300(roots=roots)
    if end is None:
        end_d = bundle.date_max or start_d
    else:
        end_d = _as_date(end)

    panel = bundle.panel_frame
    if "event_time" in panel.columns:
        sessions = pd.to_datetime(panel["event_time"]).dt.normalize()
    elif isinstance(panel.index, pd.DatetimeIndex):
        sessions = pd.Series(panel.index.normalize(), index=panel.index)
    else:
        raise ValueError("etf_510300_panel_missing_event_time")

    lo, hi = pd.Timestamp(start_d), pd.Timestamp(end_d)
    mask = (sessions >= lo) & (sessions <= hi)
    if not mask.any() or "close" not in panel.columns:
        return pd.Series(dtype="float32", name="sh.510300")

    sub_sessions = sessions.loc[mask]
    sub_close = pd.to_numeric(panel.loc[mask, "close"], errors="coerce")
    tmp = pd.DataFrame({"_session": sub_sessions, "close": sub_close})
    tmp = tmp.sort_values("_session").drop_duplicates(subset=["_session"], keep="last")
    closes = pd.Series(
        tmp["close"].to_numpy(dtype="float32", copy=False),
        index=pd.Index([ts.date() for ts in tmp["_session"]], name="session"),
        name="sh.510300",
        dtype="float32",
    )
    return close_to_close_returns(closes)


def d1_members_at(
    session: date | str,
    *,
    max_instruments: int | None = None,
    instrument_ids: Sequence[str] | None = None,
    config: D1MaskConfig | None = None,
    roots: V2DataRoots | None = None,
    return_result: bool = False,
) -> tuple[str, ...] | D1MaskResult:
    """Stable D1 membership entry for any calendar session.

    Wraps :func:`build_d1_masks_for_session` (merged panels + float_mktcap + SW_L1).
    By default returns ``member_ids``; set ``return_result=True`` for full
    :class:`D1MaskResult` (funnel counts / frame). Overall
    ``promotion_approved=False`` always; ``sw_l1_promotable`` may be True
    when the accepted tushare SW dataset is attached.

    Memory tip: call **per rebalance session** with the candidate pool; do not
    precompute/cache every session's full ``D1MaskResult.frame`` at once.
    Use ``max_instruments`` for smoke.
    """
    roots = roots or default_v2_roots()
    sess = _as_date(session)
    result = build_d1_masks_for_session(
        sess,
        d0_root=roots.d0_root,
        asof_extend_dir=roots.asof_extend_dir,
        config=config,
        instrument_ids=instrument_ids,
        max_instruments=max_instruments,
        sw_l1_path=roots.sw_l1_path,
        float_mktcap_path=roots.float_mktcap_path,
    )
    if bool(result.promotion_approved) != _gate():
        raise RuntimeError("d1_members_at_overall_promotion_gate_mismatch")
    if return_result:
        return result
    return result.member_ids


def d1_members_at_chunked(
    session: date | str,
    instrument_ids: Sequence[str],
    *,
    chunk_size: int = 500,
    config: D1MaskConfig | None = None,
    roots: V2DataRoots | None = None,
) -> tuple[str, ...]:
    """Union D1 members by scanning ``instrument_ids`` in chunks (lower peak).

    Each chunk calls :func:`d1_members_at` with that subset only — avoids one
    giant funnel frame. Order of ``member_ids`` follows first-seen across chunks.
    Overall ``promotion_approved`` remains False.
    """
    roots = roots or default_v2_roots()
    sess = _as_date(session)
    seen: dict[str, None] = {}
    for chunk in _chunk_ids(instrument_ids, max(1, int(chunk_size))):
        members = d1_members_at(
            sess,
            instrument_ids=chunk,
            config=config,
            roots=roots,
            return_result=False,
        )
        assert isinstance(members, tuple)
        for mid in members:
            seen.setdefault(str(mid), None)
    return tuple(seen.keys())


def describe_strategy_feed() -> dict[str, object]:
    """Machine-readable contract for Strategy handshake (no metrics)."""
    roots = default_v2_roots()
    cal = load_merged_calendar(roots=roots)
    return {
        "layer": "platform_strategy_feed",
        "promotion_approved": _gate(),
        "strategy_paper_v1_output_dir": str(STRATEGY_PAPER_V1_OUTPUT_DIR),
        "strategy_feed_cache_dir": str(STRATEGY_FEED_CACHE_DIR),
        "eng_writes_nav": False,
        "default_paper_start": str(DEFAULT_PAPER_START),
        "default_paper_start_fast": str(DEFAULT_PAPER_START_FAST),
        "default_close_chunk_size": DEFAULT_CLOSE_CHUNK_SIZE,
        "default_close_dtype": DEFAULT_CLOSE_DTYPE,
        "calendar_first": str(cal.first_session) if cal.first_session else None,
        "calendar_last": str(cal.last_session) if cal.last_session else None,
        "calendar_n_sessions": cal.n_sessions,
        "includes_extend": cal.includes_extend,
        "d0_asof_cutoff": str(cal.d0_asof_cutoff),
        "callables": [
            "merged_close_panel",
            "iter_merged_close_chunks",
            "merged_daily_returns",
            "iter_merged_daily_return_chunks",
            "cache_merged_close_panel",
            "load_cached_close_panel",
            "biweekly_rebalance_sessions",
            "etf_510300_daily_returns",
            "d1_members_at",
            "d1_members_at_chunked",
            "trading_sessions",
        ],
        "memory_knobs": {
            "merged_close_panel.chunk_size": "200–400 recommended for Full D1",
            "merged_close_panel.dtype": "float32 default (half of float64)",
            "merged_close_panel.use_disk_cache": "feather under output/strategy_feed_cache/",
            "iter_merged_close_chunks": "stream columns; do not hold full wide panel",
            "merged_daily_returns.close_panel": "pass preloaded closes — never reload",
            "d1_members_at": "per rebalance session only; optional max_instruments",
            "d1_members_at_chunked": "scan pool in chunks; union members",
            "avoid": "full OHLCV preload when only close/returns needed; unbounded panel cache",
        },
        "roots": {
            "d0_root": str(roots.d0_root),
            "asof_extend_dir": str(roots.asof_extend_dir),
            "etf_510300_panel": str(roots.etf_panel_path),
            "sw_l1_path": str(roots.sw_l1_path),
            "float_mktcap_path": str(roots.float_mktcap_path),
        },
        "fundamentals_defaults": {
            "financials_pit": "data/v2/financials_pit/financials_pit_tushare.parquet (accepted; load_financials_pit default prefer=tushare)",
            "ep": "data/v2/ep/ep_pit_daily_tushare.parquet (accepted PIT daily; load_ep_research(session=...); fallback ep_tushare_asof/ep_research_asof outside 2024-01-02..2026-10-09)",
            "financials_available_at_tushare": "timing index only — not a numeric source",
            "pit_rule": "available_at (Asia/Shanghai date) <= session",
        },
    }
