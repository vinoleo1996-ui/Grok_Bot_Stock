"""Embedding store reader (THIS_WEEK Eng stub) with as_of / PIT guards.

No production embedding parquet on disk yet — returns empty panels + TODO.
Schema contract for QuantLab Data: see docs/v2/SYSTEM_ARCH_V3_AI_NATIVE_ZH.md §5.
"""
from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Sequence, TypedDict

import pandas as pd

from quantlab.intel.asof_window import (
    annotate_coverage_gap,
    as_of_window,
    filter_frame_asof,
    session_to_decision_ts,
)

PROMOTION_APPROVED = False
EMBEDDING_LEAF_PREFIX = "emb_"
REPO_ROOT = Path(__file__).resolve().parents[2]
ENG_PING_PATH = REPO_ROOT / "output" / "d1" / "ENG_PING_PATHS.json"


class EmbeddingStoreSpec(TypedDict, total=False):
    path: str
    model_id: str
    dim: int
    available_at_field: str
    session_field: str
    instrument_field: str
    value_cols: list[str]
    promotion_approved: bool


def _eng_ping() -> dict[str, Any]:
    try:
        return json.loads(ENG_PING_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def default_embedding_spec() -> EmbeddingStoreSpec:
    """Build spec from ENG_PING if present; otherwise empty research stub."""
    ping = _eng_ping()
    paths = ping.get("paths") or {}
    raw = None
    for key in ("embedding_store_daily", "intel_embedding_corpus", "ann_embedding_corpus_pit"):
        if paths.get(key):
            raw = paths.get(key)
            break
    spec: EmbeddingStoreSpec = {
        "model_id": "pending_data",
        "dim": 0,
        "available_at_field": "available_at",
        "session_field": "session",
        "instrument_field": "instrument",
        "promotion_approved": False,
    }
    if raw:
        p = Path(str(raw))
        if not p.is_absolute():
            p = REPO_ROOT / p
        spec["path"] = str(p)
    return spec


def embedding_leaf_names(dim: int, prefix: str = EMBEDDING_LEAF_PREFIX) -> tuple[str, ...]:
    if dim <= 0:
        return ()
    return tuple(f"{prefix}{i}" for i in range(dim))


def load_embedding_panels(
    *,
    start: date,
    end: date | None = None,
    instruments: Sequence[str] | None = None,
    spec: EmbeddingStoreSpec | None = None,
    trade_session: date | None = None,
    decision_ts: datetime | None = None,
    strict_asof: bool = False,
) -> dict[str, pd.DataFrame]:
    """Return {emb_i: wide DataFrame indexed by session, columns=instruments}.

    Missing store -> {}. Callers merge into GP panels only when non-empty.

    as_of: when ``trade_session`` / ``decision_ts`` set, rows with
    ``available_at`` after the decision are excluded before pivoting; session
    index is also clamped so no panel column uses a future session.
    """
    spec = spec or default_embedding_spec()
    path_s = spec.get("path")
    if not path_s:
        return {}
    path = Path(path_s)
    if not path.exists():
        return {}

    win_start, win_end = start, end
    if trade_session is not None:
        win_start, win_end = as_of_window(start, end or trade_session, trade_session)

    try:
        df = pd.read_parquet(path)
    except Exception:
        return {}

    session_f = spec.get("session_field", "session")
    inst_f = spec.get("instrument_field", "instrument")
    avail_f = spec.get("available_at_field", "available_at")
    dim = int(spec.get("dim") or 0)
    value_cols = list(spec.get("value_cols") or [])
    if not value_cols:
        if dim > 0:
            value_cols = list(embedding_leaf_names(dim))
        else:
            value_cols = [c for c in df.columns if str(c).startswith(EMBEDDING_LEAF_PREFIX)]

    if session_f not in df.columns or inst_f not in df.columns or not value_cols:
        return {}

    # PIT filter on available_at when present
    if avail_f in df.columns and (trade_session is not None or decision_ts is not None):
        df = filter_frame_asof(
            df,
            trade_session=trade_session,
            decision_ts=decision_ts or (
                session_to_decision_ts(trade_session) if trade_session else None
            ),
            available_at_field=avail_f,
            strict=strict_asof,
        )
        # annotate gap on the long frame (stored on each wide panel attrs below)
        df = annotate_coverage_gap(
            df,
            start=win_start,
            end=win_end or trade_session,
            source="intel.embeddings",
            available_at_field=avail_f,
            subject="embeddings",
        )

    out: dict[str, pd.DataFrame] = {}
    gap = (df.attrs or {}).get("coverage_gap") if hasattr(df, "attrs") else None
    for col in value_cols:
        if col not in df.columns:
            continue
        wide = df.pivot_table(index=session_f, columns=inst_f, values=col, aggfunc="last")
        wide.index = pd.to_datetime(wide.index).date
        if win_start is not None:
            wide = wide.loc[[d for d in wide.index if d >= win_start]]
        if win_end is not None:
            wide = wide.loc[[d for d in wide.index if d <= win_end]]
        # Extra session clamp: never expose sessions after trade_session
        if trade_session is not None:
            wide = wide.loc[[d for d in wide.index if d <= trade_session]]
        if instruments is not None:
            cols = [c for c in instruments if c in wide.columns]
            wide = wide.reindex(columns=list(instruments)) if not cols else wide[cols]
        wide = wide.astype("float32")
        wide.attrs["promotion_approved"] = False
        if gap:
            wide.attrs["coverage_gap"] = gap
        if trade_session is not None:
            wide.attrs["asof_trade_session"] = str(trade_session)
        out[str(col)] = wide
    return out
