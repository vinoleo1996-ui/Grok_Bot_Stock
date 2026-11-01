"""Memory-lean wide panels for Full D1 research paper (Strategy).

Builds float32 close/turnover + bool tradability in one streaming pass over
instruments. Does **not** install or retain ``load_merged_panel`` long-frame
cache (that alone is ~6274 × ~1.4MB ≈ 8.6Gi and caused Full D1 TURN OOM).

``promotion_approved=false``. Research-only.
"""
from __future__ import annotations

import gc
from datetime import date
from pathlib import Path
from typing import Callable, Mapping, Sequence

import numpy as np
import pandas as pd

from quantlab.data.v2_readers import V2DataRoots, default_v2_roots, load_merged_panel
from quantlab.portfolio.v2_execution_costs import TradabilityPanels
from quantlab.portfolio.v2_panel_cache import clear_merged_panel_cache, cache_stats


def rss_gb() -> float:
    try:
        with open("/proc/self/status", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) / (1024.0 * 1024.0)
    except OSError:
        return -1.0
    return -1.0


def to_float32(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    out = df.copy()
    for c in out.columns:
        if pd.api.types.is_float_dtype(out[c]) or pd.api.types.is_integer_dtype(out[c]):
            out[c] = pd.to_numeric(out[c], errors="coerce").astype(np.float32)
    return out


def date_index_to_timestamp(df: pd.DataFrame) -> pd.DataFrame:
    """Copy with DatetimeIndex for P1 ``_session_ts``."""
    if df is None or df.empty:
        return df if df is not None else pd.DataFrame()
    out = df.copy()
    out.index = pd.DatetimeIndex([pd.Timestamp(x) for x in out.index])
    return out


def build_lean_close_turnover_tradability(
    instrument_ids: Sequence[str],
    *,
    load_start: date,
    end: date,
    tradability_start: date,
    roots: V2DataRoots | None = None,
    chunk_size: int = 200,
    min_close_bars: int = 30,
    progress_every: int = 400,
    on_progress: Callable[[dict], None] | None = None,
    collect_factor: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame, TradabilityPanels, dict]:
    """One pass: float32 close + turnover (date index) + tradability bools.

    Peak RSS stays near one long-frame (~1–2MB) plus accumulating wide columns.
    Explicitly clears any installed merged-panel cache after the pass.
    """
    roots = roots or default_v2_roots()
    lo, hi = pd.Timestamp(load_start), pd.Timestamp(end)
    t_lo, t_hi = pd.Timestamp(tradability_start), pd.Timestamp(end)

    close_map: dict[str, pd.Series] = {}
    factor_map: dict[str, pd.Series] = {}  # collect_factor: D0 'factor' (total-return adj factor)
    tov_map: dict[str, pd.Series] = {}
    lu_map: dict[str, pd.Series] = {}
    ld_map: dict[str, pd.Series] = {}
    halt_map: dict[str, pd.Series] = {}
    st_map: dict[str, pd.Series] = {}

    miss_limit = miss_ts = miss_st = 0
    loaded_close = loaded_trad = 0
    skipped = 0
    n = len(instrument_ids)

    for i, iid in enumerate(instrument_ids):
        iid_s = str(iid)
        try:
            view = load_merged_panel(iid_s, roots=roots)
        except Exception:
            skipped += 1
            continue
        frame = view.frame
        if frame is None or frame.empty or "event_time" not in frame.columns:
            skipped += 1
            continue
        if "close" not in frame.columns:
            skipped += 1
            continue

        et = pd.to_datetime(frame["event_time"]).dt.normalize()
        # --- close / turnover window (lookback → end) ---
        mask = (et >= lo) & (et <= hi)
        if int(mask.sum()) >= min_close_bars:
            sub = frame.loc[mask, [c for c in ("close", "turnover", "factor") if c in frame.columns]]
            et_sub = et[mask]
            # drop duplicate sessions
            order = np.arange(len(et_sub))
            tmp = pd.DataFrame({"_et": et_sub.to_numpy(), "_ord": order})
            tmp = tmp.drop_duplicates(subset=["_et"], keep="last")
            keep_idx = sub.index[tmp["_ord"].to_numpy()]
            sub = sub.loc[keep_idx]
            et_keep = pd.DatetimeIndex(tmp["_et"].to_numpy())
            idx_dates = pd.Index([ts.date() for ts in et_keep], name="session")

            close = pd.to_numeric(sub["close"], errors="coerce")
            if int(close.notna().sum()) >= min_close_bars:
                close_map[iid_s] = pd.Series(
                    close.to_numpy(dtype=np.float32, copy=True),
                    index=idx_dates,
                    dtype=np.float32,
                    name=iid_s,
                )
                loaded_close += 1
                if collect_factor and "factor" in sub.columns:
                    fac = pd.to_numeric(sub["factor"], errors="coerce")
                    factor_map[iid_s] = pd.Series(fac.to_numpy(dtype=np.float64, copy=True), index=idx_dates, name=iid_s)
                if "turnover" in sub.columns:
                    tov = pd.to_numeric(sub["turnover"], errors="coerce")
                    if int(tov.notna().sum()) > 0:
                        tov_map[iid_s] = pd.Series(
                            tov.to_numpy(dtype=np.float32, copy=True),
                            index=idx_dates,
                            dtype=np.float32,
                            name=iid_s,
                        )

        # --- tradability window (paper start → end) ---
        tmask = (et >= t_lo) & (et <= t_hi)
        if int(tmask.sum()) > 0:
            cols = [
                c
                for c in (
                    "close",
                    "limit_up",
                    "limit_down",
                    "tradestatus",
                    "open_status",
                    "is_st_at_open",
                )
                if c in frame.columns
            ]
            tsub = frame.loc[tmask, cols].copy()
            tsub["_et"] = pd.to_datetime(frame.loc[tmask, "event_time"]).dt.normalize().to_numpy()
            tsub = tsub.drop_duplicates(subset=["_et"], keep="last")
            idx = pd.Index([ts.date() for ts in tsub["_et"]], name="session")
            close_t = pd.to_numeric(tsub["close"], errors="coerce") if "close" in tsub.columns else None
            loaded_trad += 1

            if "limit_up" in tsub.columns and close_t is not None:
                lim_u = pd.to_numeric(tsub["limit_up"], errors="coerce")
                miss_limit += int(lim_u.isna().sum())
                hit_u = (close_t.notna() & lim_u.notna() & (close_t >= lim_u - 1e-9)).fillna(False)
            else:
                miss_limit += len(tsub)
                hit_u = pd.Series(False, index=tsub.index)

            if "limit_down" in tsub.columns and close_t is not None:
                lim_d = pd.to_numeric(tsub["limit_down"], errors="coerce")
                miss_limit += int(lim_d.isna().sum())
                hit_d = (close_t.notna() & lim_d.notna() & (close_t <= lim_d + 1e-9)).fillna(False)
            else:
                miss_limit += len(tsub)
                hit_d = pd.Series(False, index=tsub.index)

            if "tradestatus" in tsub.columns:
                ts = pd.to_numeric(tsub["tradestatus"], errors="coerce")
                miss_ts += int(ts.isna().sum())
                halted = (ts == 0.0).fillna(False)
                if "open_status" in tsub.columns:
                    halted = halted | tsub["open_status"].astype(str).eq("halted").fillna(False)
            else:
                miss_ts += len(tsub)
                halted = pd.Series(False, index=tsub.index)

            if "is_st_at_open" in tsub.columns:
                st_raw = pd.to_numeric(tsub["is_st_at_open"], errors="coerce")
                miss_st += int(st_raw.isna().sum())
                st = (st_raw.fillna(0.0) != 0.0)
            else:
                miss_st += len(tsub)
                st = pd.Series(False, index=tsub.index)

            lu_map[iid_s] = pd.Series(hit_u.to_numpy(dtype=bool), index=idx, dtype=bool)
            ld_map[iid_s] = pd.Series(hit_d.to_numpy(dtype=bool), index=idx, dtype=bool)
            halt_map[iid_s] = pd.Series(halted.to_numpy(dtype=bool), index=idx, dtype=bool)
            st_map[iid_s] = pd.Series(st.to_numpy(dtype=bool), index=idx, dtype=bool)

        # drop frame refs
        del view, frame
        if (i + 1) % chunk_size == 0:
            gc.collect()
        if on_progress is not None and ((i + 1) % progress_every == 0 or (i + 1) == n):
            on_progress(
                {
                    "i": i + 1,
                    "n": n,
                    "loaded_close": loaded_close,
                    "loaded_trad": loaded_trad,
                    "rss_gb": round(rss_gb(), 3),
                    "cache": cache_stats(),
                }
            )

    def _wide_f32(m: Mapping[str, pd.Series]) -> pd.DataFrame:
        if not m:
            return pd.DataFrame(dtype=np.float32)
        out = pd.DataFrame(m)
        out.index = pd.Index(out.index, name="session")
        out = out.sort_index()
        return out.astype(np.float32)

    def _wide_bool(m: Mapping[str, pd.Series]) -> pd.DataFrame:
        if not m:
            return pd.DataFrame(dtype=bool)
        out = pd.DataFrame(m)
        out.index = pd.Index(out.index, name="session")
        return out.sort_index().fillna(False).astype(bool)

    closes = _wide_f32(close_map)
    turnover = _wide_f32(tov_map)
    tradability = TradabilityPanels(
        limit_up_hit=_wide_bool(lu_map),
        limit_down_hit=_wide_bool(ld_map),
        halted=_wide_bool(halt_map),
        is_st=_wide_bool(st_map),
        n_instruments_loaded=loaded_trad,
        n_limit_price_missing_cells=miss_limit,
        n_tradestatus_missing_cells=miss_ts,
        n_is_st_missing_cells=miss_st,
        notes=[
            "lean_single_pass_no_long_frame_cache",
            "missing_limit_price→no_hit; missing tradestatus→not halted; missing is_st→not ST",
            "promotion_approved=false",
        ],
    )

    # Ensure no long-frame cache retains GiB after this builder.
    clear_merged_panel_cache()
    gc.collect()

    meta = {
        "n_pool": n,
        "n_close_cols": int(closes.shape[1]) if closes is not None else 0,
        "n_turnover_cols": int(turnover.shape[1]) if turnover is not None else 0,
        "n_tradability_loaded": loaded_trad,
        "n_skipped": skipped,
        "close_shape": list(closes.shape),
        "turnover_shape": list(turnover.shape),
        "rss_gb_after": round(rss_gb(), 3),
        "cache_after": cache_stats(),
        "dtype_close": str(closes.dtypes.iloc[0]) if closes.shape[1] else None,
        "promotion_approved": False,
    }
    if collect_factor:
        # caller pops this (not JSON): float64 wide total-return factor aligned to closes
        meta["factor_panel"] = (pd.DataFrame(factor_map).reindex(index=closes.index, columns=closes.columns)
                                if factor_map else None)
    return closes, turnover, tradability, meta
