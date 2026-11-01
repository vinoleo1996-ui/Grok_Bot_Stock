"""Typed readers for data/v2.

Paths and the D0/extend merge rule come from
docs/v2/ASOF_EXTEND_PANEL_MERGE.md and quantlab/v2_schemas.py.
A missing file raises FileNotFoundError. This module does not compute returns.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
import json

import pandas as pd

from quantlab.config import ROOT

DEFAULT_FINANCIALS_PIT_TUSHARE = ROOT / "data" / "v2" / "financials_pit" / "financials_pit_tushare.parquet"
DEFAULT_EP_PIT = ROOT / "data" / "v2" / "ep" / "ep_pit_daily_tushare.parquet"
DEFAULT_EP_TUSHARE_ASOF = ROOT / "data" / "v2" / "ep" / "ep_tushare_asof_20260630.parquet"
DEFAULT_EP_RESEARCH_FALLBACK = ROOT / "data" / "v2" / "financials_pit" / "ep_research_asof_20260630.parquet"
DEFAULT_ETF_PANEL = ROOT / "data" / "v2" / "etf" / "etf_daily_adj.parquet"
DEFAULT_FLOAT_MKTCAP = ROOT / "data" / "v2" / "float_mktcap" / "float_mktcap_daily_tushare.parquet"
DEFAULT_D0 = ROOT / "data" / "local_market" / "1c85fd9aceaa03c3c4863bec"
DEFAULT_ASOF_EXTEND_DIR = ROOT / "data" / "v2" / "asof_extend_tushare_202610"
DEFAULT_SW_L1_PATH = ROOT / "data" / "v2" / "sw_l1_pit" / "industry_members_sw_l1_tushare.parquet"
DEFAULT_DIVIDENDS = ROOT / "data" / "v2" / "dividends" / "dividends.parquet"
DOCUMENTED_CUTOFF = date(2026, 6, 30)


def _require_file(path: Path) -> Path:
    if not path.is_file():
        raise FileNotFoundError(str(path))
    return path


def _as_date(value) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def _shanghai_date(value) -> date | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
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


@dataclass(frozen=True)
class V2DataRoots:
    d0_root: Path
    asof_extend_dir: Path
    etf_panel_path: Path
    financials_pit_path: Path = DEFAULT_FINANCIALS_PIT_TUSHARE
    ep_pit_path: Path = DEFAULT_EP_PIT
    float_mktcap_path: Path = DEFAULT_FLOAT_MKTCAP
    dividend_path: Path = DEFAULT_DIVIDENDS


def default_v2_roots() -> V2DataRoots:
    return V2DataRoots(
        d0_root=DEFAULT_D0,
        asof_extend_dir=ROOT / "data" / "v2" / "asof_extend_tushare_202610",
        etf_panel_path=DEFAULT_ETF_PANEL,
    )


def _extend_dir(roots: V2DataRoots, override: Path | None) -> Path:
    """Accepted default is the tushare extend dir; the 2026-10-10 note names the fallback dir."""
    if override is not None:
        return Path(override)
    primary = Path(roots.asof_extend_dir)
    if primary.exists():
        return primary
    fallback = ROOT / "data" / "v2" / "asof_extend_202610"
    if fallback.exists():
        return fallback
    return primary


def resolve_d0_asof_cutoff(extend_dir: Path | None = None, *, roots: V2DataRoots | None = None) -> date:
    """Cutoff from extend manifest.json field d0_as_of, else the documented 2026-06-30."""
    base = _extend_dir(roots or default_v2_roots(), extend_dir)
    manifest = base / "manifest.json"
    if manifest.is_file():
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        raw = payload.get("d0_as_of") or payload.get("d0_asof_cutoff")
        if raw:
            return _as_date(raw)
    return DOCUMENTED_CUTOFF


@dataclass
class MergedPanelView:
    instrument_id: str
    d0_asof_cutoff: date
    n_d0_rows: int
    n_extend_rows: int
    n_merged_rows: int
    date_min: date | None
    date_max: date | None
    panel_source: str
    promotion_approved: bool
    quality_notes: tuple
    frame: pd.DataFrame | None


@dataclass
class MergedCalendarView:
    sessions: pd.DatetimeIndex
    last_session: date | None
    path_primary: str
    includes_extend: bool
    promotion_approved: bool = False


@dataclass(frozen=True)
class EtfInstrumentStatus:
    """Quality label copied from the ETF file. Not a fabricated instrument row."""

    quality_status: str


@dataclass
class Etf510300Bundle:
    panel_frame: pd.DataFrame
    date_max: date | None
    path: str
    promotion_approved: bool = False
    date_min: date | None = None
    n_bars: int = 0
    instrument: EtfInstrumentStatus | None = None


@dataclass
class TabularView:
    frame: pd.DataFrame
    path: str
    source_variant: str
    promotable: bool = False
    promotion_approved: bool = False
    session: date | None = None
    quality_label: str = ""
    available_at_nulls: int = 0
    available_at_rule: str = ""
    policy_path: str | None = None
    n_rows: int = 0
    session_max: date | None = None
    metrics: tuple = ()
    n_non_null: int = 0


@dataclass
class FloatMktcapLookup:
    values: dict[str, float] = field(default_factory=dict)
    source_by_id: dict[str, str] = field(default_factory=dict)
    primary_source: str = "none"
    notes: tuple[str, ...] = ()


def _session_index(frame: pd.DataFrame) -> pd.DatetimeIndex:
    if "session" in frame.columns:
        return pd.DatetimeIndex(pd.to_datetime(frame["session"])).normalize()
    if "cal_date" in frame.columns:
        return pd.DatetimeIndex(pd.to_datetime(frame["cal_date"].astype(str))).normalize()
    if "trade_date" in frame.columns:
        return pd.DatetimeIndex(pd.to_datetime(frame["trade_date"].astype(str))).normalize()
    if "event_time" in frame.columns:
        return pd.DatetimeIndex(pd.to_datetime(frame["event_time"])).normalize()
    if isinstance(frame.index, pd.DatetimeIndex):
        return frame.index.normalize()
    raise ValueError(f"calendar_session_column_missing:{list(frame.columns)}")


def _read_calendar_file(path: Path) -> pd.DatetimeIndex:
    frame = pd.read_parquet(_require_file(path))
    if "is_open" in frame.columns:
        frame = frame[frame["is_open"].astype(int) == 1]
    idx = _session_index(frame)
    return pd.DatetimeIndex(sorted(pd.unique(idx)))


def load_merged_calendar(
    *,
    roots: V2DataRoots | None = None,
    d0_root: Path | None = None,
    asof_extend_dir: Path | None = None,
) -> MergedCalendarView:
    roots = roots or default_v2_roots()
    extend = _extend_dir(roots, asof_extend_dir)
    d0 = Path(d0_root) if d0_root is not None else Path(roots.d0_root)
    extend_path = extend / "calendar.parquet"
    d0_path = d0 / "calendar.parquet"
    if extend_path.is_file():
        sessions = _read_calendar_file(extend_path)
        return MergedCalendarView(sessions, sessions[-1].date() if len(sessions) else None, str(extend_path), True)
    if d0_path.is_file():
        sessions = _read_calendar_file(d0_path)
        return MergedCalendarView(sessions, sessions[-1].date() if len(sessions) else None, str(d0_path), False)
    raise FileNotFoundError(str(extend_path))


def _panel_file(root: Path, instrument_id: str) -> Path | None:
    panels = Path(root) / "panels"
    for name in (f"{instrument_id}.parquet", f"{instrument_id.replace('.', '_')}.parquet"):
        path = panels / name
        if path.is_file():
            return path
    return None


def _with_event_time(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    if "event_time" not in out.columns:
        if isinstance(out.index, pd.DatetimeIndex):
            out = out.reset_index().rename(columns={out.index.name or "index": "event_time"})
        elif "session" in out.columns:
            out["event_time"] = pd.to_datetime(out["session"])
        elif "trade_date" in out.columns:
            out["event_time"] = pd.to_datetime(out["trade_date"].astype(str))
        else:
            raise ValueError(f"panel_event_time_missing:{list(out.columns)}")
    out["event_time"] = pd.to_datetime(out["event_time"])
    return out


def load_merged_panel(
    instrument_id: str,
    *,
    roots: V2DataRoots | None = None,
    d0_root: Path | None = None,
    asof_extend_dir: Path | None = None,
    d0_asof_cutoff: date | None = None,
) -> MergedPanelView:
    roots = roots or default_v2_roots()
    d0 = Path(d0_root) if d0_root is not None else Path(roots.d0_root)
    extend = _extend_dir(roots, asof_extend_dir)
    cutoff = d0_asof_cutoff or resolve_d0_asof_cutoff(extend, roots=roots)
    d0_path = _panel_file(d0, instrument_id)
    extend_path = _panel_file(extend, instrument_id)
    if d0_path is None and extend_path is None:
        raise FileNotFoundError(str(d0 / "panels" / f"{instrument_id}.parquet"))
    parts = []
    notes: list[str] = []
    n_d0 = n_ext = 0
    if d0_path is not None:
        d0_frame = _with_event_time(pd.read_parquet(d0_path))
        d0_frame = d0_frame[d0_frame["event_time"].dt.normalize() <= pd.Timestamp(cutoff)]
        n_d0 = len(d0_frame)
        parts.append(d0_frame)
    if extend_path is not None:
        ext_frame = _with_event_time(pd.read_parquet(extend_path))
        ext_frame = ext_frame[ext_frame["event_time"].dt.normalize() > pd.Timestamp(cutoff)]
        n_ext = len(ext_frame)
        if "amount" in ext_frame.columns and ext_frame["amount"].isna().all():
            notes.append("extend_amount_all_null")
        if "is_st_at_open" not in ext_frame.columns:
            notes.append("extend_is_st_at_open_missing")
        parts.append(ext_frame)
    frame = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
    if not frame.empty:
        frame = frame.sort_values("event_time").drop_duplicates("event_time", keep="last")
    if d0_path and extend_path:
        source = "merged"
    elif d0_path:
        source = "d0_only"
    else:
        source = "extend_only"
    dates = pd.to_datetime(frame["event_time"]).dt.date if not frame.empty else []
    return MergedPanelView(
        instrument_id=str(instrument_id),
        d0_asof_cutoff=cutoff,
        n_d0_rows=n_d0,
        n_extend_rows=n_ext,
        n_merged_rows=len(frame),
        date_min=min(dates) if len(dates) else None,
        date_max=max(dates) if len(dates) else None,
        panel_source=source,
        promotion_approved=False,
        quality_notes=tuple(notes),
        frame=frame,
    )


def panel_session_row(panel: pd.DataFrame, session: date) -> pd.Series:
    if panel is None or panel.empty:
        raise ValueError("empty panel")
    frame = _with_event_time(panel)
    stamps = pd.to_datetime(frame["event_time"]).dt.date
    match = frame.loc[stamps == session]
    if match.empty:
        raise ValueError(f"session_missing:{session}")
    return match.iloc[-1]


def load_etf_510300(*, roots: V2DataRoots | None = None) -> Etf510300Bundle:
    path = _require_file(Path((roots or default_v2_roots()).etf_panel_path))
    frame = pd.read_parquet(path)
    if "ts_code" in frame.columns:
        frame = frame[frame["ts_code"].astype(str).str.startswith("510300")]
    frame = _with_event_time(frame)
    dates = list(pd.to_datetime(frame["event_time"]).dt.date) if not frame.empty else []
    if "quality_status" in frame.columns and frame["quality_status"].notna().any():
        status = str(frame["quality_status"].dropna().iloc[-1])
    else:
        status = "quality_status_column_missing"
    return Etf510300Bundle(
        frame,
        max(dates) if dates else None,
        str(path),
        False,
        min(dates) if dates else None,
        len(frame),
        EtfInstrumentStatus(status),
    )


def _variant(path: Path) -> str:
    return "tushare" if "tushare" in path.name else "research"


def load_sw_l1_members(*, path: Path | None = None, roots: V2DataRoots | None = None) -> TabularView:
    if path is None:
        path = ROOT / "data" / "v2" / "sw_l1_pit" / "industry_members_sw_l1_tushare.parquet"
    path = _require_file(Path(path))
    frame = pd.read_parquet(path)
    nulls = int(frame["available_at"].isna().sum()) if "available_at" in frame.columns else len(frame)
    return TabularView(
        frame, str(path), _variant(path), _dataset_promotable(path, frame), False,
        available_at_nulls=nulls, n_rows=len(frame), n_non_null=_n_non_null(frame),
    )


def _drop_unpublished(frame: pd.DataFrame, session: date | None) -> pd.DataFrame:
    if session is None:
        return frame
    if "available_at" not in frame.columns:
        raise ValueError("available_at_missing")

    def _visible(value) -> bool:
        published = _shanghai_date(value)
        return published is not None and published < session

    keep = frame["available_at"].map(_visible)
    return frame.loc[keep.to_numpy()].copy()


def _dataset_promotable(path: Path, frame: pd.DataFrame) -> bool:
    """Dataset flag only. strategy promotion stays false; a tushare name alone is not enough."""
    if "tushare" not in path.name or "available_at" not in frame.columns:
        return False
    return bool(frame["available_at"].notna().any())


def _n_non_null(frame: pd.DataFrame) -> int:
    for column in ("float_mktcap", "ep", "value"):
        if column in frame.columns:
            return int(frame[column].notna().sum())
    return int(len(frame))


def _coverage_min(frame: pd.DataFrame) -> date | None:
    for column in ("trade_date", "session", "event_time", "cal_date"):
        if column not in frame.columns:
            continue
        stamps = pd.to_datetime(frame[column], errors="coerce")
        if stamps.notna().any():
            return pd.Timestamp(stamps.min()).date()
    return None


def _metric_names(frame: pd.DataFrame) -> tuple:
    if "metric" not in frame.columns:
        return ()
    return tuple(sorted(set(frame["metric"].dropna().astype(str))))


def load_ep_research(*, roots: V2DataRoots | None = None, session: date | None = None, prefer: str | None = None) -> TabularView:
    if prefer == "tushare":
        path = _require_file(DEFAULT_EP_TUSHARE_ASOF)
    else:
        path = _require_file(Path((roots or default_v2_roots()).ep_pit_path))
    raw = pd.read_parquet(path)
    outside = ""
    if session is not None and prefer != "tushare":
        start = _coverage_min(raw)
        if start is not None and session < start:
            outside = "lookahead_outside_pit_coverage"
            if DEFAULT_EP_RESEARCH_FALLBACK.is_file():
                path = DEFAULT_EP_RESEARCH_FALLBACK
                raw = pd.read_parquet(path)
    promotable = False if outside else _dataset_promotable(path, raw)
    frame = _drop_unpublished(raw, session)
    labels = [part for part in (outside, "available_at_strictly_before_session" if session else "") if part]
    return TabularView(
        frame, str(path), _variant(path), promotable, False, session=session,
        quality_label=" ".join(labels),
        n_rows=len(frame),
        n_non_null=_n_non_null(frame),
    )


def ep_research_lookup(view: TabularView, *, instrument_ids, require_sane: bool = True) -> dict[str, float]:
    frame = view.frame
    if frame is None or frame.empty or "ep" not in frame.columns:
        return {}
    wanted = {str(item) for item in instrument_ids}
    sub = frame[frame["instrument_id"].astype(str).isin(wanted)] if "instrument_id" in frame.columns else frame
    out = {}
    for row in sub.itertuples(index=False):
        value = getattr(row, "ep", None)
        if value is None or not pd.notna(value):
            continue
        number = float(value)
        if require_sane and not pd.notna(number):
            continue
        out[str(getattr(row, "instrument_id"))] = number
    return out


def load_financials_pit(*, roots: V2DataRoots | None = None, prefer: str | None = None, ocf_source: str | None = None) -> TabularView:
    path = Path((roots or default_v2_roots()).financials_pit_path)
    if prefer == "baostock":
        path = ROOT / "data" / "v2" / "financials_pit" / "financials_pit_baostock.parquet"
    path = _require_file(path)
    frame = pd.read_parquet(path)
    if ocf_source == "legacy_research":
        quality = "ocf_to_profit=legacy_research"
        promotable = False
    elif "source" in frame.columns and frame["source"].astype(str).eq("ocf_to_profit_pit_tushare").any():
        quality = "ocf_to_profit=tushare_pit"
        promotable = _dataset_promotable(path, frame)
    else:
        quality = ""
        promotable = _dataset_promotable(path, frame)
    return TabularView(
        frame, str(path), _variant(path), promotable, False,
        quality_label=quality,
        available_at_rule="available_at_strictly_before_session",
        n_rows=len(frame),
        metrics=_metric_names(frame),
        n_non_null=_n_non_null(frame),
    )


def financials_metric_asof(frame: pd.DataFrame, session: date, instrument_ids, metric: str, *, negative_as_missing: bool = False) -> dict[str, float]:
    if "available_at" not in frame.columns:
        raise ValueError("available_at_missing")
    visible = _drop_unpublished(frame, session)
    if "metric" in visible.columns:
        visible = visible[visible["metric"].astype(str) == metric]
    wanted = {str(item) for item in instrument_ids}
    if "instrument_id" in visible.columns:
        visible = visible[visible["instrument_id"].astype(str).isin(wanted)]
    value_col = "value" if "value" in visible.columns else metric
    out: dict[str, float] = {}
    if value_col not in visible.columns or "instrument_id" not in visible.columns:
        return out
    for row in visible.itertuples(index=False):
        number = getattr(row, value_col)
        if not pd.notna(number):
            continue
        number = float(number)
        if negative_as_missing and number < 0:
            continue
        out[str(getattr(row, "instrument_id"))] = number
    return out


def float_mktcap_lookup_for_session(session: date, *, asof_path: Path | None = None, instrument_ids=None, prefer_daily: bool = True) -> FloatMktcapLookup:
    path = Path(asof_path) if asof_path is not None else DEFAULT_FLOAT_MKTCAP
    if not path.is_file():
        if asof_path is not None:
            raise FileNotFoundError(str(path))
        return FloatMktcapLookup(notes=(f"float_mktcap_file_missing:{path}",))
    frame = _drop_unpublished(pd.read_parquet(path), session)
    if "trade_date" in frame.columns:
        frame = frame[pd.to_datetime(frame["trade_date"].astype(str)).dt.date <= session]
    wanted = None if instrument_ids is None else {str(item) for item in instrument_ids}
    values: dict[str, float] = {}
    source: dict[str, str] = {}
    column = "float_mktcap" if "float_mktcap" in frame.columns else None
    if column and "instrument_id" in frame.columns:
        for row in frame.itertuples(index=False):
            iid = str(getattr(row, "instrument_id"))
            if wanted is not None and iid not in wanted:
                continue
            number = getattr(row, column)
            if pd.notna(number):
                values[iid] = float(number)
                source[iid] = "v2_daily" if prefer_daily else "v2_parquet"
    return FloatMktcapLookup(values, source, "v2_daily" if values else "none", ())


def load_float_mktcap_asof(*, roots: V2DataRoots | None = None) -> TabularView:
    path = _require_file(Path((roots or default_v2_roots()).float_mktcap_path))
    frame = pd.read_parquet(path)
    return TabularView(
        frame, str(path), _variant(path), _dataset_promotable(path, frame), False,
        n_rows=len(frame), n_non_null=_n_non_null(frame),
    )


def load_float_mktcap_daily(*, roots: V2DataRoots | None = None, session: date | None = None) -> TabularView:
    view = load_float_mktcap_asof(roots=roots)
    if session is not None:
        view.frame = _drop_unpublished(view.frame, session)
        view.session = session
        view.n_rows = len(view.frame)
    return view


def load_dividends(path: Path | None = None, *, roots: V2DataRoots | None = None) -> TabularView:
    chosen = Path(path) if path is not None else DEFAULT_DIVIDENDS
    chosen = _require_file(chosen)
    frame = pd.read_parquet(chosen)
    return TabularView(
        frame, str(chosen), _variant(chosen), _dataset_promotable(chosen, frame), False,
        n_rows=len(frame), n_non_null=_n_non_null(frame),
    )


def load_financials_available_at(*, roots: V2DataRoots | None = None) -> TabularView:
    path = _require_file(ROOT / "data" / "v2" / "financials_pit" / "financials_available_at.parquet")
    frame = pd.read_parquet(path)
    return TabularView(frame, str(path), _variant(path), False, False, n_rows=len(frame))


def load_asof_extend_meta(*, roots: V2DataRoots | None = None) -> dict:
    extend = _extend_dir(roots or default_v2_roots(), None)
    path = _require_file(extend / "manifest.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["promotion_approved"] = False
    return payload


def resolve_sw_l1_research_path(explicit: Path | None = None) -> tuple[Path, str]:
    if explicit is not None and Path(explicit).is_file():
        chosen = Path(explicit)
        return chosen, _variant(chosen)
    if DEFAULT_SW_L1_PATH.is_file():
        return DEFAULT_SW_L1_PATH, _variant(DEFAULT_SW_L1_PATH)
    raise FileNotFoundError(str(DEFAULT_SW_L1_PATH))


def sw_l1_asof_assignments(members: pd.DataFrame, session: date, instrument_ids):
    """Same PIT filter as ``d1_masks.sw_l1_asof``, one assignment per requested id."""
    from quantlab.universe.d1_masks import sw_l1_asof
    from quantlab.v2_schemas import SWL1AsOfAssignment

    found = sw_l1_asof(members, session, instrument_ids)
    sess = session if isinstance(session, date) else _as_date(session)
    rows = []
    for instrument_id in instrument_ids:
        if instrument_id in found:
            rows.append(found[instrument_id])
            continue
        rows.append(SWL1AsOfAssignment(
            instrument_id=str(instrument_id),
            session=sess,
            sw_code=None,
            sw_name=None,
            available_at=None,
            quality_status=None,
            is_unknown_bucket=True,
        ))
    return tuple(rows)


def etf_510300_bars(bundle: Etf510300Bundle, start: date, end: date):
    """Map stored OHLC rows to bars. Missing price columns raise; returns are not computed."""
    from quantlab.v2_schemas import ETF_510300_INSTRUMENT_ID, Etf510300Bar

    frame = _with_event_time(bundle.panel_frame)
    required = ("open", "high", "low", "close", "volume", "amount")
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"etf_bar_columns_missing:{','.join(missing)}")
    sessions = pd.to_datetime(frame["event_time"]).dt.date
    chosen = frame.loc[((sessions >= start) & (sessions <= end)).to_numpy()]
    bars = []
    for row in chosen.itertuples(index=False):
        session = pd.Timestamp(row.event_time).date()
        if "available_at" in chosen.columns and pd.notna(row.available_at):
            available = pd.Timestamp(row.available_at).to_pydatetime()
        else:
            available = datetime.combine(session, datetime.min.time())
        quality = str(row.quality_status) if "quality_status" in chosen.columns and pd.notna(row.quality_status) else "unspecified"
        bars.append(Etf510300Bar(
            instrument_id=ETF_510300_INSTRUMENT_ID,
            session=session,
            open=float(row.open),
            high=float(row.high),
            low=float(row.low),
            close=float(row.close),
            volume=float(row.volume),
            amount=float(row.amount),
            available_at=available,
            quality_status=quality,
        ))
    return tuple(bars)
