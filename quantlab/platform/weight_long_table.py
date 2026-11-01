"""Frozen weight long-table contract for Book-Smoke / factor_evolve / Strategy.

Eng-owned. Research-grade only: ``promotion_approved`` is always False.
Canonical columns: session | instrument_id | weight
Optional: sleeve (when dumping multi-sleeve in one file; Book-Smoke still
prefers separate --stock-path / --alpha-event-path today).

Coverage rule (research): 全日更长表须覆盖目标窗、禁止仅前推解读
(see ``assert_session_coverage`` / docs/v2/SKELETON_ONECLICK_ZH.md).

Aliases accepted on ingest (same as WeightLongTableSleeve):
  session <- session|date|trade_date
  instrument_id <- instrument_id|instrument|ts_code|code
  weight <- weight|target_weight
  sleeve <- sleeve|sleeve_name (optional)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, TypedDict

import pandas as pd

PROMOTION_APPROVED = False

COLUMN_CONTRACT_VERSION = "weight_long_v1_20261012"
AUTHORITATIVE_COLS = ("session", "instrument_id", "weight")
OPTIONAL_COLS = ("sleeve",)

SESSION_ALIASES = ("session", "date", "trade_date")
INST_ALIASES = ("instrument_id", "instrument", "ts_code", "code")
WEIGHT_ALIASES = ("weight", "target_weight")
SLEEVE_ALIASES = ("sleeve", "sleeve_name")

SleeveName = Literal["core", "stock", "alpha_event", "beta", "other"]


class WeightLongRow(TypedDict, total=False):
    """One consumable weight row (research hint → Book schedule)."""

    session: str  # YYYY-MM-DD or parseable date
    instrument_id: str  # e.g. sh.510300 / 510300.SH (normalized on validate)
    weight: float  # > 0; sleeve-local or book-local depending on producer
    sleeve: SleeveName
    promotion_approved: bool  # always False when written by Eng helpers


class WeightLongTableMeta(TypedDict, total=False):
    column_contract_version: str
    n_rows: int
    n_sessions: int
    columns: list[str]
    promotion_approved: bool
    path: str
    status: str  # ok | empty | error
    error: str


def normalize_instrument_id(s: str) -> str:
    s = str(s).strip()
    if not s:
        return s
    if "." in s:
        a, b = s.split(".", 1)
        if len(a) == 2 and a.isalpha():
            return a.lower() + "." + b
        if len(b) == 2 and b.isalpha():
            return b.lower() + "." + a
    if s.isdigit() and len(s) == 6:
        return ("sh." if s.startswith(("5", "6", "9")) else "sz.") + s
    return s


def _resolve_col(cols_lower: dict[str, str], aliases: tuple[str, ...]) -> str | None:
    for a in aliases:
        if a in cols_lower:
            return cols_lower[a]
    return None


def empty_weight_frame(*, with_sleeve: bool = False) -> pd.DataFrame:
    cols = list(AUTHORITATIVE_COLS) + (["sleeve"] if with_sleeve else [])
    return pd.DataFrame(columns=cols)


def normalize_weight_frame(df: pd.DataFrame, *, require_positive: bool = True) -> pd.DataFrame:
    """Map aliases → canonical cols; coerce dtypes; drop invalid rows.

    When multiple aliases exist as separate columns (e.g. instrument on some
    rows, code on others), values are coalesced left-to-right by alias priority.
    Raises ValueError if a required canonical field has no alias column at all.
    """
    if df is None or not isinstance(df, pd.DataFrame):
        raise ValueError("weight_long_table: expected DataFrame")
    if df.empty:
        return empty_weight_frame(with_sleeve="sleeve" in {c.lower() for c in df.columns})

    cols_lower = {str(c).lower(): c for c in df.columns}

    def _coalesce(aliases: tuple[str, ...]) -> pd.Series | None:
        series_list = []
        for a in aliases:
            src = cols_lower.get(a)
            if src is not None:
                series_list.append(df[src])
        if not series_list:
            return None
        out = series_list[0]
        for s in series_list[1:]:
            out = out.where(out.notna() & (out.astype(str).str.strip() != ""), s)
            # also fillna for pure NaN
            out = out.fillna(s)
        return out

    sess = _coalesce(SESSION_ALIASES)
    inst = _coalesce(INST_ALIASES)
    wcol = _coalesce(WEIGHT_ALIASES)
    missing = [
        n
        for n, v in (("session", sess), ("instrument_id", inst), ("weight", wcol))
        if v is None
    ]
    if missing:
        raise ValueError(
            f"weight_long_table: missing columns {missing} "
            "(aliases documented in module docstring)"
        )

    sleeve = _coalesce(SLEEVE_ALIASES)
    out = pd.DataFrame(
        {
            "session": pd.to_datetime(sess.astype(str)),
            "instrument_id": inst.map(normalize_instrument_id),
            "weight": pd.to_numeric(wcol, errors="coerce"),
        }
    )
    if sleeve is not None:
        out["sleeve"] = sleeve.astype(str)
    out = out.dropna(subset=["session", "instrument_id", "weight"])
    # drop empty instrument strings after normalize
    out = out[out["instrument_id"].astype(str).str.strip() != ""]
    if require_positive:
        out = out[out["weight"] > 0]
    return out.reset_index(drop=True)



def validate_weight_frame(df: pd.DataFrame, *, require_rows: bool = False) -> WeightLongTableMeta:
    """Validate / normalize; return machine-readable meta. Never flips promotion."""
    try:
        norm = normalize_weight_frame(df, require_positive=True)
    except ValueError as e:
        return WeightLongTableMeta(
            column_contract_version=COLUMN_CONTRACT_VERSION,
            n_rows=0,
            n_sessions=0,
            columns=[],
            promotion_approved=False,
            status="error",
            error=str(e),
        )
    n = int(len(norm))
    if require_rows and n == 0:
        return WeightLongTableMeta(
            column_contract_version=COLUMN_CONTRACT_VERSION,
            n_rows=0,
            n_sessions=0,
            columns=list(norm.columns),
            promotion_approved=False,
            status="empty",
            error="zero_positive_weight_rows",
        )
    return WeightLongTableMeta(
        column_contract_version=COLUMN_CONTRACT_VERSION,
        n_rows=n,
        n_sessions=int(norm["session"].nunique()) if n else 0,
        columns=list(norm.columns),
        promotion_approved=False,
        status="ok" if n else "empty",
    )


def validate_weight_path(path: str | Path, *, require_rows: bool = False) -> WeightLongTableMeta:
    p = Path(path)
    meta = WeightLongTableMeta(
        column_contract_version=COLUMN_CONTRACT_VERSION,
        n_rows=0,
        n_sessions=0,
        columns=[],
        promotion_approved=False,
        path=str(p),
        status="error",
    )
    if not p.exists():
        meta["error"] = f"missing:{p}"
        return meta
    try:
        df = pd.read_parquet(p) if p.suffix.lower() in (".parquet", ".pq") else pd.read_csv(p)
    except Exception as e:  # noqa: BLE001 — surface read errors in meta
        meta["error"] = f"read_error:{e}"
        return meta
    out = validate_weight_frame(df, require_rows=require_rows)
    out["path"] = str(p)
    return out


def write_weight_long_table(df: pd.DataFrame, path: str | Path, *, with_sleeve: bool = False) -> WeightLongTableMeta:
    """Normalize, stamp promotion_approved=false in sidecar meta, write parquet/csv."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if df is None or (isinstance(df, pd.DataFrame) and df.empty):
        norm = empty_weight_frame(with_sleeve=with_sleeve)
    else:
        norm = normalize_weight_frame(df, require_positive=True)
    if path.suffix.lower() in (".parquet", ".pq"):
        norm.to_parquet(path, index=False)
    else:
        norm.to_csv(path, index=False)
    meta = validate_weight_frame(norm, require_rows=False)
    meta["path"] = str(path)
    meta["promotion_approved"] = False
    # sidecar for consumers that want contract version without reading parquet schema
    import json

    sidecar = path.with_suffix(path.suffix + ".meta.json")
    sidecar.write_text(
        json.dumps(dict(meta), ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    return meta



def assert_session_coverage(
    df: pd.DataFrame,
    *,
    target_start: str | None = None,
    target_end: str | None = None,
    min_sessions: int | None = None,
    forbid_forward_fill_interpretation: bool = True,
) -> dict[str, Any]:
    """Light check: daily weight table must cover the target window.

    Research rule: do **not** interpret engine hold-forward after the last
    weight session as intentional daily rebalance (禁止仅前推解读).
    Does not rewrite weights; returns a machine-readable verdict.
    """
    norm = normalize_weight_frame(df, require_positive=True)
    if norm.empty:
        return {
            "ok": False,
            "status": "empty",
            "n_sessions": 0,
            "session_min": None,
            "session_max": None,
            "covers_target": False,
            "forbid_forward_fill_interpretation": forbid_forward_fill_interpretation,
            "error": "zero_positive_weight_rows",
            "promotion_approved": False,
        }
    sess = pd.to_datetime(norm["session"]).dt.normalize()
    smin = sess.min()
    smax = sess.max()
    n_sess = int(sess.nunique())
    covers = True
    reasons: list[str] = []
    if target_start is not None:
        ts = pd.Timestamp(target_start).normalize()
        if smin > ts:
            covers = False
            reasons.append(f"starts_after_target:{smin.date()}>{ts.date()}")
    if target_end is not None:
        te = pd.Timestamp(target_end).normalize()
        if smax < te:
            covers = False
            reasons.append(f"ends_before_target:{smax.date()}<{te.date()}")
    if min_sessions is not None and n_sess < int(min_sessions):
        covers = False
        reasons.append(f"n_sessions<{min_sessions}:{n_sess}")
    return {
        "ok": covers,
        "status": "ok" if covers else "coverage_gap",
        "n_sessions": n_sess,
        "session_min": str(smin.date()),
        "session_max": str(smax.date()),
        "covers_target": covers,
        "forbid_forward_fill_interpretation": bool(forbid_forward_fill_interpretation),
        "coverage_rule_zh": "全日更长表须覆盖目标窗、禁止仅前推解读",
        "reasons": reasons,
        "promotion_approved": False,
    }


def assert_session_coverage_path(
    path: str | Path,
    *,
    target_start: str | None = None,
    target_end: str | None = None,
    min_sessions: int | None = None,
) -> dict[str, Any]:
    """Read parquet/csv then ``assert_session_coverage`` (light; no resid_etf heavy validate)."""
    p = Path(path)
    if not p.exists():
        return {
            "ok": False,
            "status": "error",
            "error": f"missing:{p}",
            "promotion_approved": False,
            "forbid_forward_fill_interpretation": True,
            "coverage_rule_zh": "全日更长表须覆盖目标窗、禁止仅前推解读",
        }
    df = pd.read_parquet(p) if p.suffix.lower() in (".parquet", ".pq") else pd.read_csv(p)
    out = assert_session_coverage(
        df,
        target_start=target_start,
        target_end=target_end,
        min_sessions=min_sessions,
    )
    out["path"] = str(p)
    return out


def schema_handshake() -> dict[str, Any]:
    """Machine-readable contract for Alpha / AI / Strategy."""
    return {
        "column_contract_version": COLUMN_CONTRACT_VERSION,
        "authoritative_cols": list(AUTHORITATIVE_COLS),
        "optional_cols": list(OPTIONAL_COLS),
        "session_aliases": list(SESSION_ALIASES),
        "instrument_aliases": list(INST_ALIASES),
        "weight_aliases": list(WEIGHT_ALIASES),
        "sleeve_aliases": list(SLEEVE_ALIASES),
        "dtypes": {
            "session": "datetime64[ns] (written as parseable date)",
            "instrument_id": "str (normalized sh./sz. prefix preferred)",
            "weight": "float64 > 0",
            "sleeve": "str optional",
        },
        "promotion_approved": False,
        "strategy_promotion_approved": False,
        "book_consumable_rule": "positive weight rows with resolvable session+instrument_id",
        "coverage_rule_zh": "全日更长表须覆盖目标窗、禁止仅前推解读",
        "forbid_forward_fill_interpretation": True,
        "module": "quantlab.platform.weight_long_table",
    }
