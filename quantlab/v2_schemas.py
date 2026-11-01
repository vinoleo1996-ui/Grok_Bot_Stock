"""Frozen QuantLab V2 data contracts for Eng ↔ Data coordination (Phase 0).

These dataclasses lock **field names and types** that QuantLab Data will fill.
Missing physical files → loaders raise ``NotImplementedError`` / return empty
typed structures with TODOs. Do **not** invent rows or backtest metrics.

Canonical paths (relative to a V2 snapshot root, e.g. ``data/v2/<id>/`` or the
landed D0 tree ``data/local_market/1c85fd9aceaa03c3c4863bec/``):

  - calendar.parquet
  - instruments.parquet  (stocks + equity_etf rows)
  - panels/<instrument_id>.parquet
  - benchmark.parquet / OR panels for index (research)
  - industry_members_sw_l1.parquet   << SW_L1 PIT (NOT D0 industry_records)
  - panels/sh.510300.parquet         << Beta sleeve ETF (NOT in D0)
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import ClassVar, Literal, Sequence

# ---------------------------------------------------------------------------
# Identity helpers (locked string forms)
# ---------------------------------------------------------------------------
InstrumentId = str  # e.g. "sh.600000", "sz.000001", "sh.510300"
AssetType = Literal["stock", "equity_etf"]

ETF_510300_INSTRUMENT_ID: str = "sh.510300"
ETF_510300_BARE_CODE: str = "510300"
INDEX_CSI300_INSTRUMENT_ID: str = "sh.000300"
SW_L1_TABLE_NAME: str = "industry_members_sw_l1"
SW_L1_SCHEME: str = "SW_L1"

# Panel / mask columns Eng expects on stock & ETF daily panels (DATA_V2_MIN_SPEC §C)
PANEL_MASK_COLUMNS: tuple[str, ...] = (
    "open",
    "high",
    "low",
    "close",
    "volume",
    "amount",
    "turnover",
    "tradestatus",
    "is_st_at_open",
    "limit_up",
    "limit_down",
    "open_status",
    "open_status_available_at",
    "available_at",
    "quality_status",
)


# ---------------------------------------------------------------------------
# SW_L1 PIT — frozen membership table schema
# File: industry_members_sw_l1.parquet  (or manifest key industry_members_sw_l1)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SWL1MemberRow:
    """One PIT industry membership interval (申万一级).

    Semantics:
      - ``in_date`` / ``out_date``: calendar dates of membership (out_date null = still in).
      - ``available_at``: earliest datetime the membership fact was knowable (PIT).
        MUST be non-null for promotion-grade use. D0 ``industry_records.available_at``
        is all-null effective_date_proxy — that table is **not** this schema.
      - Decision cutoff uses rows with ``available_at <= decision_time`` and
        ``in_date <= session`` and (``out_date`` is null or ``out_date > session``).
    """

    SCHEMA_VERSION: ClassVar[str] = "quantlab.v2.industry_members_sw_l1.v1"
    TABLE_NAME: ClassVar[str] = SW_L1_TABLE_NAME

    instrument_id: str
    sw_code: str
    sw_name: str
    in_date: date
    out_date: date | None
    available_at: datetime
    source: str
    revision: str
    quality_status: str  # ok | ... ; *_snapshot_unverified banned from promotion


SW_L1_COLUMN_SPEC: tuple[tuple[str, str], ...] = (
    ("instrument_id", "str"),
    ("sw_code", "str"),
    ("sw_name", "str"),
    ("in_date", "date"),
    ("out_date", "date|null"),
    ("available_at", "datetime tz-aware or Asia/Shanghai naive"),
    ("source", "str"),
    ("revision", "str"),
    ("quality_status", "str"),
)


@dataclass(frozen=True)
class SWL1AsOfAssignment:
    """Resolved SW_L1 label for one instrument at one decision cutoff."""

    instrument_id: str
    session: date
    sw_code: str | None  # None → unknown bucket (Mandate unknown_industry_cap)
    sw_name: str | None
    available_at: datetime | None
    quality_status: str | None
    is_unknown_bucket: bool


# ---------------------------------------------------------------------------
# 510300 Beta-sleeve ETF — frozen instruments + panel schemas
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class EquityEtfInstrumentRow:
    """instruments.parquet row for an equity ETF (Beta sleeve).

    Required for ``sh.510300``. D0 snapshot has asset_type=stock only — missing.
    """

    SCHEMA_VERSION: ClassVar[str] = "quantlab.v2.instruments.equity_etf.v1"
    INSTRUMENT_ID: ClassVar[str] = ETF_510300_INSTRUMENT_ID

    instrument_id: str  # locked example: sh.510300
    available_at: datetime
    effective_at: date | datetime
    source: str
    revision: str
    quality_status: str
    active: bool
    is_st: bool | None
    listing_date: date | None
    delist_date: date | None
    asset_type: AssetType  # must be "equity_etf"
    buy_lot: int
    sell_lot: int
    sell_delay: int  # T+N per real ETF rules
    price_tick: float
    commission: float
    min_commission: float
    limit_ratio: float | None
    min_buy_quantity: int | None = None
    min_sell_quantity: int | None = None


ETF_510300_INSTRUMENT_COLUMN_SPEC: tuple[tuple[str, str], ...] = (
    ("instrument_id", "str = sh.510300"),
    ("available_at", "datetime"),
    ("effective_at", "date|datetime"),
    ("source", "str"),
    ("revision", "str"),
    ("quality_status", "str"),
    ("active", "bool"),
    ("is_st", "bool|null"),
    ("listing_date", "date|null"),
    ("delist_date", "date|null"),
    ("asset_type", "Literal['equity_etf']"),
    ("buy_lot", "int"),
    ("sell_lot", "int"),
    ("sell_delay", "int"),
    ("price_tick", "float"),
    ("commission", "float"),
    ("min_commission", "float"),
    ("limit_ratio", "float|null"),
    ("min_buy_quantity", "int|null"),
    ("min_sell_quantity", "int|null"),
)


@dataclass(frozen=True)
class Etf510300Bar:
    """One raw OHLCV bar for Beta sleeve fills (panels/sh.510300.parquet).

    Ledger uses raw open/close; adj/factor columns may exist for features only.
    Index name on disk may be ``event_time`` (DatetimeIndex) — Eng treats the
    session date as the bar's trading day.
    """

    SCHEMA_VERSION: ClassVar[str] = "quantlab.v2.panels.equity_etf_510300.v1"
    PANEL_PATH: ClassVar[str] = "panels/sh.510300.parquet"
    INSTRUMENT_ID: ClassVar[str] = ETF_510300_INSTRUMENT_ID

    instrument_id: str  # sh.510300
    session: date
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: float
    available_at: datetime
    quality_status: str
    # Mask / tradability (same names as stock panels where applicable)
    tradestatus: float | int | None = None
    open_status: str | None = None  # trading | halted | unknown | derived
    open_status_available_at: datetime | None = None
    limit_up: float | None = None
    limit_down: float | None = None
    turnover: float | None = None
    # Feature-only; never use to fabricate cash distributions
    factor: float | None = None


ETF_510300_PANEL_COLUMN_SPEC: tuple[tuple[str, str], ...] = (
    ("open", "float raw"),
    ("high", "float raw"),
    ("low", "float raw"),
    ("close", "float raw"),
    ("volume", "float"),
    ("amount", "float CNY"),
    ("available_at", "datetime"),
    ("quality_status", "str"),
    ("tradestatus", "float|int|null"),
    ("open_status", "str|null"),
    ("open_status_available_at", "datetime|null"),
    ("limit_up", "float|null"),
    ("limit_down", "float|null"),
    ("turnover", "float|null"),
    ("factor", "float|null feature_only"),
)


@dataclass(frozen=True)
class BenchmarkIndexBar:
    """Research benchmark index bar (sh.000300). Present in D0 ``benchmark.parquet``."""

    SCHEMA_VERSION: ClassVar[str] = "quantlab.v2.benchmark.index_csi300.v1"
    INSTRUMENT_ID: ClassVar[str] = INDEX_CSI300_INSTRUMENT_ID

    code: str  # sh.000300
    session: date
    open: float
    high: float
    low: float
    close: float
    preclose: float | None
    volume: float | None
    amount: float | None
    available_at: datetime
    quality_status: str
    source: str
    revision: str
    return_basis: str = "price_return"  # locked declaration


# ---------------------------------------------------------------------------
# Float mktcap PIT (microcap exclude_bottom_pct) — frozen field name
# ---------------------------------------------------------------------------
FLOAT_MKTCAP_FIELD: str = "float_mktcap"  # on instruments asof OR daily exposure table
FLOAT_MKTCAP_UNIT: str = "CNY"


@dataclass(frozen=True)
class FloatMktcapAsOf:
    """PIT float mktcap used for LSY bottom-pct exclusion."""

    SCHEMA_VERSION: ClassVar[str] = "quantlab.v2.float_mktcap.v1"

    instrument_id: str
    session: date
    float_mktcap: float
    available_at: datetime
    source: str
    revision: str
    quality_status: str


def schema_handshake_payload() -> dict:
    """Machine-readable frozen schema names for Data bot coordination."""
    return {
        "promotion_approved": False,
        "sw_l1": {
            "table": SW_L1_TABLE_NAME,
            "scheme": SW_L1_SCHEME,
            "schema_version": SWL1MemberRow.SCHEMA_VERSION,
            "columns": [{"name": n, "type": t} for n, t in SW_L1_COLUMN_SPEC],
            "row_type": "quantlab.v2_schemas.SWL1MemberRow",
            "not_this": "D0 industry_records.parquet (csrc_2012 effective_date_proxy)",
        },
        "etf_510300": {
            "instrument_id": ETF_510300_INSTRUMENT_ID,
            "bare_code": ETF_510300_BARE_CODE,
            "instruments_schema_version": EquityEtfInstrumentRow.SCHEMA_VERSION,
            "instruments_columns": [
                {"name": n, "type": t} for n, t in ETF_510300_INSTRUMENT_COLUMN_SPEC
            ],
            "panel_path": Etf510300Bar.PANEL_PATH,
            "panel_schema_version": Etf510300Bar.SCHEMA_VERSION,
            "panel_columns": [
                {"name": n, "type": t} for n, t in ETF_510300_PANEL_COLUMN_SPEC
            ],
            "row_types": [
                "quantlab.v2_schemas.EquityEtfInstrumentRow",
                "quantlab.v2_schemas.Etf510300Bar",
            ],
        },
        "benchmark_index": {
            "instrument_id": INDEX_CSI300_INSTRUMENT_ID,
            "schema_version": BenchmarkIndexBar.SCHEMA_VERSION,
            "d0_file": "benchmark.parquet",
            "return_basis": "price_return",
        },
        "float_mktcap": {
            "field": FLOAT_MKTCAP_FIELD,
            "unit": FLOAT_MKTCAP_UNIT,
            "schema_version": FloatMktcapAsOf.SCHEMA_VERSION,
        },
        "panel_mask_columns": list(PANEL_MASK_COLUMNS),
    }


def require_sw_l1_columns(columns: Sequence[str]) -> None:
    missing = [name for name, _ in SW_L1_COLUMN_SPEC if name not in set(columns)]
    if missing:
        raise ValueError(f"sw_l1_columns_missing:{','.join(missing)}")


def require_etf_510300_panel_columns(columns: Sequence[str]) -> None:
    required = {"open", "high", "low", "close", "volume", "amount", "available_at", "quality_status"}
    missing = sorted(required - set(columns))
    if missing:
        raise ValueError(f"etf_510300_panel_columns_missing:{','.join(missing)}")
