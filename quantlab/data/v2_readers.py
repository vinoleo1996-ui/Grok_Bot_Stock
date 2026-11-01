"""Typed readers for data/v2. Missing files stay missing; this module does not invent bars."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pandas as pd

from quantlab.config import ROOT

DEFAULT_FINANCIALS_PIT_TUSHARE = ROOT / "data" / "v2" / "financials_pit" / "financials_pit_tushare.parquet"
DEFAULT_ETF_PANEL = ROOT / "data" / "v2" / "etf" / "etf_daily_adj.parquet"


@dataclass(frozen=True)
class V2DataRoots:
    d0_root: Path
    asof_extend_dir: Path
    etf_panel_path: Path


def default_v2_roots() -> V2DataRoots:
    return V2DataRoots(
        d0_root=ROOT / "data" / "local_market" / "1c85fd9aceaa03c3c4863bec",
        asof_extend_dir=ROOT / "data" / "v2" / "asof_extend_tushare_202610",
        etf_panel_path=DEFAULT_ETF_PANEL,
    )


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
    promotion_approved: bool = False


def load_merged_panel(*args, **kwargs) -> MergedPanelView:
    path = default_v2_roots().asof_extend_dir
    raise FileNotFoundError(f"merged panel source is not in this checkout: {path}")


def load_merged_calendar(*args, **kwargs) -> MergedCalendarView:
    path = default_v2_roots().asof_extend_dir / "calendar.parquet"
    raise FileNotFoundError(f"merged calendar is not in this checkout: {path}")


def load_etf_510300(*args, **kwargs):
    path = default_v2_roots().etf_panel_path
    raise FileNotFoundError(f"ETF panel is not in this checkout: {path}")


def panel_session_row(panel: pd.DataFrame, session: date):
    if panel is None or panel.empty:
        raise ValueError("empty panel")
    if "event_time" in panel.columns:
        stamps = pd.to_datetime(panel["event_time"]).dt.normalize()
        match = panel.loc[stamps.dt.date == session]
    else:
        stamps = pd.to_datetime(panel.index)
        match = panel.loc[stamps.normalize().date == session] if hasattr(stamps, "date") else panel.iloc[0:0]
    if match.empty:
        raise ValueError(f"session_missing:{session}")
    return match.iloc[-1]


def load_sw_l1_members(*args, **kwargs):
    raise FileNotFoundError("SW L1 membership table is not in this checkout")


def load_ep_research(*args, **kwargs):
    raise FileNotFoundError("EP research table is not in this checkout")


def load_financials_pit(*args, **kwargs):
    raise FileNotFoundError(str(DEFAULT_FINANCIALS_PIT_TUSHARE))


def financials_metric_asof(*args, **kwargs):
    raise FileNotFoundError(str(DEFAULT_FINANCIALS_PIT_TUSHARE))


def ep_research_lookup(*args, **kwargs):
    raise FileNotFoundError("EP lookup table is not in this checkout")


def float_mktcap_lookup_for_session(*args, **kwargs):
    raise FileNotFoundError("float market-cap table is not in this checkout")


def resolve_d0_asof_cutoff(*args, **kwargs):
    return date(2026, 6, 30)
