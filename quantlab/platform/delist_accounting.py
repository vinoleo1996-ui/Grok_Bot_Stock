"""SD1 delisting accounting layer (spec docs/v2/ARCH_ENGINE_SUSPEND_DELIST_FIX_SPEC_ZH.md §3.1/§3.5/§3.6, sha256 2e428f39…bdbb0b).

Ex-post delisting information (stock_delisted*, stock_basic delist_date / list_status=D, delist_events_v1) is
**accounting-layer only**. The loaders below are callable solely from the engine modules and the audit/test/parity
scripts in ``_ALLOWED_CALLERS``; any other caller (selection, weights, optimizer, masks, research leaves) gets
``StrategyLayerDelistAccess`` (a PermissionError) from an explicit ``raise`` — never ``assert``, so ``python -O``
keeps the guard (T10/T11). Static complement: scripts_eng/sd1_pit_static_check.py.

``load_delist_events`` frame (one row per delisted stock) for ``execution_sd1.run_weight_schedule(delist_events=...)`` and
``tradability.weight_book_returns``:
    code (ts_code), instrument_id, last_trade_date, type (FORCED_PERIOD | FORCED_NO_PERIOD | MERGER_SWAP | CASH_OUT |
    UNKNOWN), period_start, force_sell_from (first session the period is PUBLIC = max(period_start, namechange ann_date)),
    swap_ratio, acquirer, cash_per_share, pay_date, last_close, flags, type_source, needs_manual_source,
    source_path, source_sha256
Source (Arch SD1 review P2-4 / A5, 2026-10-18): passed EXPLICITLY as ``source=`` — ``src_events_v1`` (Data
delist_events_v1, spec §3.5 step 0) | ``src_table_v2`` (stock_delisted_v2, DATA_SUSPEND_DELIST_FIX_PLAN §2, D-3/D-4
fixed) | ``src_table_v1_d3rule`` (frozen stock_delisted v1 + the D-3 face-value rule applied here). Never auto-switched by file existence: a missing file raises FileNotFoundError. The
table's full sha256 is recorded in every row (``source_sha256``) so results state the exact table they used; a formal
run's .ok pins path + sha. Merger/privatisation rows without a manually verified announcement source are UNKNOWN
(engines book them as DELIST_WRITEOFF_UNKNOWN, recovery 0 main basis; 主 Agent E-1 final 01:53).
needs_manual_source=True rows NEVER get a force_sell_from (Arch P1-5 / A5 condition 1): flag
NEEDS_MANUAL_SOURCE_NO_FORCE_SELL; the engines enforce the same rule again on the column (defence in depth).
``load_halt_extra`` builds ExecPanels.halt_extra from Data ``suspend_flags_v2`` (spec §3.1 / D-2) when it exists.
Reads only requested codes / columns (filters), no full-panel loads. live=false; promotion_approved=false.
"""
from __future__ import annotations

import hashlib
import inspect
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DELIST_EVENTS_V1 = ROOT / "data/v2/ref/delist_events_v1.parquet"
STOCK_DELISTED_V2 = ROOT / "data/v2/ref/stock_delisted_v2.parquet"
STOCK_DELISTED = ROOT / "data/v2/ref/stock_delisted.parquet"
# Source names are deliberately token-free so research callers can name one without tripping the PIT static scan.
DELIST_SOURCES = {"src_events_v1": DELIST_EVENTS_V1,       # Data delist_events_v1 (spec §3.5 step 0)
                  "src_table_v2": STOCK_DELISTED_V2,       # Data D-3/D-4 fixed table
                  "src_table_v1_d3rule": STOCK_DELISTED}   # frozen v1 table + the D-3 face-value rule applied here
NAMECHANGE = ROOT / "data/v2/st_events/namechange_all.parquet"
DELISTED_DAILY = ROOT / "data/v2/delisted/delisted_daily_tushare.parquet"
CONSIDERATION = ROOT / "data/v2/ref/delist_consideration.parquet"
SUSPEND_FLAGS_V2 = ROOT / "data/v2/suspend_flags/suspend_flags_v2.parquet"
EVENT_COLUMNS = ("code", "instrument_id", "last_trade_date", "type", "period_start", "force_sell_from", "swap_ratio",
                 "acquirer", "cash_per_share", "pay_date", "last_close", "flags", "type_source", "needs_manual_source",
                 "source_path", "source_sha256")
MANUAL_FLAG = "NEEDS_MANUAL_SOURCE_NO_FORCE_SELL"

# Repo-relative files (or directory prefixes ending in '/') allowed to call the loaders directly.
_ALLOWED_CALLERS = (
    "quantlab/platform/execution_sd1.py",
    "quantlab/platform/tradability.py",
    "quantlab/platform/delist_accounting.py",
    "docs/v2/audit/",
    "tests/test_sd1_suspend_delist.py",
    "scripts_eng/sd0_parity_runner.py",
)


class StrategyLayerDelistAccess(PermissionError):
    """Ex-post delisting information requested outside the accounting layer (spec §3.6, T10)."""


def _rel(fn: str) -> str:
    try:
        return str(Path(fn).resolve().relative_to(ROOT))
    except (ValueError, OSError):
        return str(fn)


def guard_accounting_caller() -> str:
    """Raise StrategyLayerDelistAccess unless the first caller outside this module is allow-listed."""
    here = _rel(__file__)
    f = inspect.currentframe()
    try:
        f = f.f_back if f is not None else None
        while f is not None and _rel(f.f_code.co_filename) == here:
            f = f.f_back
        caller = _rel(f.f_code.co_filename) if f is not None else "<unknown>"
    finally:
        del f
    if not any(caller == a or (a.endswith("/") and caller.startswith(a)) for a in _ALLOWED_CALLERS):
        raise StrategyLayerDelistAccess(
            f"SD1 PIT guard: {caller} may not read delisting dates/reasons (accounting layer only; spec §3.6)")
    return caller


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _face_value_codes(codes) -> set:
    """D-3 rule: the last 20 traded closes all < 1 CNY (reads only the needed codes and columns)."""
    codes = list(codes)
    if not codes or not DELISTED_DAILY.exists():
        return set()
    d = pd.read_parquet(DELISTED_DAILY, columns=["ts_code", "trade_date", "close", "vol"], filters=[("ts_code", "in", codes)])
    d = d[pd.to_numeric(d["vol"], errors="coerce") > 0]
    out = set()
    for c, g in d.sort_values("trade_date").groupby("ts_code"):
        last = pd.to_numeric(g["close"], errors="coerce").dropna().tail(20)
        if len(last) == 20 and bool((last < 1.0).all()):
            out.add(c)
    return out


def _period_ann(ts_codes) -> dict:
    """{ts_code: ann_date} of the delisting-period name change ('…退' or '退市…'), PIT by ann_date."""
    if not NAMECHANGE.exists():
        return {}
    n = pd.read_parquet(NAMECHANGE, columns=["ts_code", "name", "start_date", "ann_date"])
    nm = n.name.astype(str)
    n = n[n.ts_code.isin(list(ts_codes)) & (nm.str.endswith("退") | nm.str.startswith("退市"))]
    return {c: g.sort_values("start_date").iloc[0].ann_date for c, g in n.groupby("ts_code")}


def _derive(src: pd.DataFrame, v2: bool) -> pd.DataFrame:
    src = src[src.last_trade_date.notna()].copy()
    if v2:
        cat = src["delist_reason_category_v2"].astype(str)
        ps = src["delist_period_start"]
        has_period = src["entered_delisting_period_v2"].fillna(False).astype(bool) & ps.notna()
        face = set(src.loc[src["face_value_delist_flag"].fillna(False).astype(bool), "ts_code"])
        manual = src.get("needs_manual_source", pd.Series(False, index=src.index)).fillna(False).astype(bool)
        source = "stock_delisted_v2"
    else:
        cat = src.delist_reason_category.astype(str)
        ps = src.delisting_period_start
        has_period = src.entered_delisting_period.fillna(False).astype(bool) & ps.notna() \
            & (src.delisting_period_trade_days.fillna(0) > 0)
        face = _face_value_codes(src.loc[cat.str.contains("吸收合并|私有化|主动"), "ts_code"])
        manual = cat.str.contains("吸收合并|私有化|主动") & ~src.ts_code.isin(face)
        source = "stock_delisted_v1+D3_rule(interim)"
    forced = cat.str.startswith("强制退市") | src.ts_code.isin(face)
    typ = np.where(has_period, "FORCED_PERIOD", np.where(forced, "FORCED_NO_PERIOD", "UNKNOWN"))
    flags = np.where(src.ts_code.isin(face) & ~cat.str.startswith("强制退市"), "D3_FACE_VALUE_RECLASSIFIED",
                     np.where(manual & (typ == "UNKNOWN"), "MA_UNVERIFIED_NO_ANNOUNCEMENT_SOURCE", ""))
    return pd.DataFrame(dict(code=src.ts_code.values, instrument_id=src.instrument_id.values,
                             last_trade_date=pd.to_datetime(src.last_trade_date).values, type=typ,
                             period_start=pd.to_datetime(ps.where(has_period).astype("string"), format="%Y%m%d",
                                                         errors="coerce").values,
                             swap_ratio=np.nan, acquirer=None, cash_per_share=np.nan, pay_date=None,
                             last_close=src.last_close.values, flags=flags, type_source=source,
                             needs_manual_source=manual.values))


def load_delist_events(codes=None, *, source: str) -> pd.DataFrame:
    """Accounting-layer delisting events for ``codes`` (ts_code or instrument_id; None = all). Guarded.
    ``source`` is mandatory and explicit (one of DELIST_SOURCES); its file must exist (no fallback chain)."""
    guard_accounting_caller()
    if source not in DELIST_SOURCES:
        raise ValueError(f"source must be one of {sorted(DELIST_SOURCES)} (explicit; no auto-switch), got {source!r}")
    path = DELIST_SOURCES[source]
    if not path.exists():
        raise FileNotFoundError(f"delist source {source!r} -> {path} does not exist (no silent fallback; Arch P2-4)")
    src_sha = _sha256_file(path)
    if source == "src_events_v1":
        ev = pd.read_parquet(path)
        ev["type_source"] = "delist_events_v1"
        for c in EVENT_COLUMNS:
            if c not in ev.columns:
                ev[c] = None
    else:
        ev = _derive(pd.read_parquet(path), v2=(source == "src_table_v2"))
        ev["force_sell_from"] = pd.NaT
    ev["needs_manual_source"] = ev["needs_manual_source"].astype("boolean").fillna(False).astype(bool)
    if ev["force_sell_from"].isna().all():
        ann = _period_ann(ev.code.tolist())
        ff = []
        for c, ps in zip(ev.code, ev.period_start):
            if pd.isna(ps):
                ff.append(pd.NaT); continue
            a = pd.to_datetime(str(ann.get(c)), format="%Y%m%d", errors="coerce") if ann.get(c) is not None else pd.NaT
            ff.append(max(pd.Timestamp(ps), a) if pd.notna(a) else pd.Timestamp(ps))
        ev["force_sell_from"] = ff
    ev["force_sell_from"] = pd.to_datetime(ev["force_sell_from"], errors="coerce")
    blocked = ev["needs_manual_source"] & ev["force_sell_from"].notna()
    if blocked.any():   # Arch P1-5: a row whose period/announcement still needs a manual source never forces a sell
        fl = ev["flags"].fillna("").astype(str)
        ev.loc[blocked, "flags"] = np.where(fl[blocked] == "", MANUAL_FLAG, fl[blocked] + "|" + MANUAL_FLAG)
        ev.loc[blocked, "force_sell_from"] = pd.NaT
    if CONSIDERATION.exists():
        cdf = pd.read_parquet(CONSIDERATION)
        keep = [c for c in ("swap_ratio", "acquirer", "cash_per_share", "pay_date") if c in cdf.columns]
        ev = ev.drop(columns=keep).merge(cdf[["code"] + keep], on="code", how="left")
        ev["consideration_sha256"] = _sha256_file(CONSIDERATION)
    ev["source_path"] = _rel(str(path))
    ev["source_sha256"] = src_sha
    if codes is not None:
        want = {str(c) for c in codes}
        ev = ev[ev.code.astype(str).isin(want) | ev.instrument_id.astype(str).isin(want)]
    out = ev.reset_index(drop=True)
    out.attrs.update(delist_source=source, source_path=_rel(str(path)), source_sha256=src_sha)
    return out


def delist_source_info(delist_events) -> dict:
    """{delist_source, source_path, source_sha256} of an events frame (empty frame -> 'none_stated')."""
    if delist_events is None:
        return dict(delist_source=None, source_path=None, source_sha256=None)
    at = dict(getattr(delist_events, "attrs", {}) or {})
    if at.get("delist_source"):
        return dict(delist_source=at["delist_source"], source_path=at.get("source_path"), source_sha256=at.get("source_sha256"))
    def uniq(c):
        if c not in delist_events.columns:
            return None
        v = sorted({str(x) for x in delist_events[c].dropna()})
        return v[0] if len(v) == 1 else (v or None)
    if len(delist_events) == 0:
        return dict(delist_source="none_stated(empty_frame)", source_path=None, source_sha256=None)
    return dict(delist_source=uniq("type_source"), source_path=uniq("source_path"), source_sha256=uniq("source_sha256"))


def _covers_open(timing) -> bool:
    """Intraday halt timing string covers 09:30 (e.g. '09:30-10:30', '0930-1030'); unparseable -> True (conservative)."""
    m = re.findall(r"(\d{1,2}):?(\d{2})", str(timing))
    if len(m) < 1:
        return True
    start = int(m[0][0]) * 60 + int(m[0][1])
    end = int(m[1][0]) * 60 + int(m[1][1]) if len(m) > 1 else 24 * 60
    return start <= 9 * 60 + 30 < end


def load_halt_extra(codes, index, *, years=None) -> pd.DataFrame | None:
    """ExecPanels.halt_extra from Data suspend_flags_v2: halted_fullday | intraday halt covering 09:30. Read by year
    chunks (trade_date filter) and only for ``codes``. None when the table does not exist yet (Data D-2 pending)."""
    if not SUSPEND_FLAGS_V2.exists():
        return None
    idx = pd.DatetimeIndex(index)
    cols = list(map(str, codes))
    out = pd.DataFrame(False, index=idx, columns=cols)
    ys = years or sorted(set(idx.year))
    import pyarrow as pa
    import pyarrow.parquet as pq
    td_type = pq.read_schema(SUSPEND_FLAGS_V2).field("trade_date").type   # Arch P2-7: filter in the column's own type
    if pa.types.is_integer(td_type):
        bounds = lambda y: (y * 10000 + 101, y * 10000 + 1231)
    elif pa.types.is_timestamp(td_type) or pa.types.is_date(td_type):
        bounds = lambda y: (pd.Timestamp(f"{y}-01-01"), pd.Timestamp(f"{y}-12-31 23:59:59"))
    else:
        bounds = lambda y: (f"{y}0101", f"{y}1231")
    for y in ys:
        lo, hi = bounds(y)
        f = pd.read_parquet(SUSPEND_FLAGS_V2, columns=["instrument_id", "ts_code", "trade_date", "halted_fullday",
                                                      "intraday_halt", "intraday_halt_timing"],
                            filters=[("trade_date", ">=", lo), ("trade_date", "<=", hi)])
        if f.empty:
            continue
        f["d"] = (pd.to_datetime(f.trade_date) if not (pa.types.is_integer(td_type) or pa.types.is_string(td_type)
                                                     or pa.types.is_large_string(td_type))
                  else pd.to_datetime(f.trade_date.astype(str).str[:8], format="%Y%m%d", errors="coerce"))
        hit = f.halted_fullday.fillna(False).astype(bool) | (f.intraday_halt.fillna(False).astype(bool)
                                                              & f.intraday_halt_timing.map(_covers_open))
        f = f[hit]
        for key in ("instrument_id", "ts_code"):
            g = f[f[key].astype(str).isin(cols)]
            for c, d in zip(g[key].astype(str), g.d):
                if d in out.index:
                    out.at[d, c] = True
        del f
    return out
