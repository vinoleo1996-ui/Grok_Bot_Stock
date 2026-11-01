"""Cross-section scores / AI daily weights → Book-Smoke consumable weight long-table.

Authoritative columns (internal):
  session | instrument_id | weight  (+ optional mechanism_tag)

AI daily handoff aliases accepted on ingest:
  date ↔ session
  instrument ↔ instrument_id
  target_weight ↔ weight

Full daily series required for production; ≤10 distinct sessions without
--smoke → stub_window WARN in meta (not a success KPI).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Sequence

import pandas as pd

from quantlab.agents.factor_evolve.schemas import (
    AUTHORITATIVE_WEIGHT_COLS,
    COLUMN_CONTRACT_VERSION,
    FactorCandidate,
    PROMOTION_APPROVED,
)

PROMOTION_APPROVED = PROMOTION_APPROVED  # re-export
STUB_SESSION_WARN_MAX = 10


def _normalize_instrument(s: str) -> str:
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


def normalize_weight_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Map AI / external aliases onto authoritative columns.

    Accepts any of:
      session|date|trade_date
      instrument_id|instrument|ts_code|code
      weight|target_weight
    Optional: mechanism_tag
    """
    if df is None or df.empty:
        cols = list(AUTHORITATIVE_WEIGHT_COLS)
        return pd.DataFrame(columns=cols)

    out = df.copy()
    rename: dict[str, str] = {}
    cols_lower = {c.lower(): c for c in out.columns}

    def _pick(*names: str) -> str | None:
        for n in names:
            if n in out.columns:
                return n
            if n.lower() in cols_lower:
                return cols_lower[n.lower()]
        return None

    sess_src = _pick("session", "date", "trade_date")
    inst_src = _pick("instrument_id", "instrument", "ts_code", "code")
    w_src = _pick("weight", "target_weight")
    if sess_src and sess_src != "session":
        rename[sess_src] = "session"
    if inst_src and inst_src != "instrument_id":
        rename[inst_src] = "instrument_id"
    if w_src and w_src != "weight":
        rename[w_src] = "weight"
    if rename:
        out = out.rename(columns=rename)

    missing = [c for c in AUTHORITATIVE_WEIGHT_COLS if c not in out.columns]
    if missing:
        raise ValueError(
            f"weight frame missing authoritative cols after alias map: {missing}; "
            f"have={list(df.columns)}"
        )

    keep = ["session", "instrument_id", "weight"]
    if "mechanism_tag" in out.columns:
        keep.append("mechanism_tag")
    out = out[keep].copy()
    out["session"] = pd.to_datetime(out["session"].astype(str))
    out["instrument_id"] = out["instrument_id"].map(_normalize_instrument)
    out["weight"] = pd.to_numeric(out["weight"], errors="coerce")
    out = out.dropna(subset=["session", "instrument_id", "weight"])
    out = out[out["weight"] > 0].reset_index(drop=True)
    return out


def scores_to_long_table(
    candidates: Sequence[FactorCandidate],
    *,
    top_k: int = 5,
    equal_weight: bool = True,
    sleeve_budget: float = 1.0,
) -> pd.DataFrame:
    """Build long table from passed candidates' score_rows.

    Per session: take top_k by score across all passed candidates' rows
    (dedupe instrument keep max score), then equal-weight * sleeve_budget.
    score_rows accept date/instrument aliases; output is authoritative cols
    plus optional mechanism_tag from the winning candidate row.
    """
    rows: list[dict[str, Any]] = []
    for c in candidates:
        mech = str(c.get("mechanism_tag") or "").strip() or None
        for r in c.get("score_rows") or []:
            rows.append(
                {
                    "session": r.get("session") or r.get("date") or r.get("trade_date"),
                    "instrument_id": r.get("instrument_id")
                    or r.get("instrument")
                    or r.get("ts_code")
                    or r.get("code"),
                    "score": float(r.get("score", 0.0)),
                    "candidate_id": c.get("candidate_id"),
                    "mechanism_tag": mech,
                }
            )
    if not rows:
        return pd.DataFrame(columns=list(AUTHORITATIVE_WEIGHT_COLS))
    df = pd.DataFrame(rows)
    df["session"] = pd.to_datetime(df["session"].astype(str))
    df["instrument_id"] = df["instrument_id"].map(_normalize_instrument)
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df = df.dropna(subset=["session", "instrument_id", "score"])
    # max score per session×instrument
    df = df.sort_values("score", ascending=False).drop_duplicates(
        ["session", "instrument_id"], keep="first"
    )
    out_parts: list[pd.DataFrame] = []
    for sess, g in df.groupby("session", sort=True):
        g2 = g.nlargest(int(top_k), "score")
        if g2.empty:
            continue
        if equal_weight:
            w = float(sleeve_budget) / float(len(g2))
            g2 = g2.assign(weight=w)
        else:
            s = g2["score"].clip(lower=0)
            denom = float(s.sum()) or 1.0
            g2 = g2.assign(weight=(s / denom) * float(sleeve_budget))
        cols = ["session", "instrument_id", "weight"]
        if "mechanism_tag" in g2.columns and g2["mechanism_tag"].notna().any():
            cols.append("mechanism_tag")
        out_parts.append(g2[cols])
    if not out_parts:
        return pd.DataFrame(columns=list(AUTHORITATIVE_WEIGHT_COLS))
    out = pd.concat(out_parts, ignore_index=True)
    out = out[out["weight"] > 0].reset_index(drop=True)
    return out


def write_weight_parquet(df: pd.DataFrame, path: Path) -> int:
    """Write parquet in authoritative col order; Eng-validate core 3 cols."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    cols = [c for c in AUTHORITATIVE_WEIGHT_COLS if c in df.columns]
    if "mechanism_tag" in df.columns:
        cols = cols + ["mechanism_tag"]
    if "sleeve" in df.columns and "sleeve" not in cols:
        cols = cols + ["sleeve"]
    out = df[cols] if cols else df
    out.to_parquet(path, index=False)
    try:
        from quantlab.platform.weight_long_table import validate_weight_path

        meta = validate_weight_path(path, require_rows=False)
        if meta.get("status") == "error":
            raise ValueError(meta.get("error") or "weight_long_table_invalid")
    except ImportError:
        pass
    return int(len(out))


def build_weight_meta(
    df: pd.DataFrame,
    *,
    smoke: bool = False,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Meta for weight handoff: column contract + stub-window honesty."""
    n_sess = int(df["session"].nunique()) if (df is not None and not df.empty and "session" in df.columns) else 0
    stub_window = (not smoke) and n_sess > 0 and n_sess <= STUB_SESSION_WARN_MAX
    meta: dict[str, Any] = {
        "column_contract_version": COLUMN_CONTRACT_VERSION,
        "authoritative_cols": list(AUTHORITATIVE_WEIGHT_COLS),
        "aliases_accepted": {
            "session": ["date", "trade_date"],
            "instrument_id": ["instrument", "ts_code", "code"],
            "weight": ["target_weight"],
        },
        "promotion_approved": False,
        "strategy_promotion_approved": False,
        "smoke": bool(smoke),
        "stub_window": bool(stub_window),
        "n_distinct_sessions": n_sess,
        "n_weight_rows": int(len(df)) if df is not None else 0,
        "require_full_daily": True,
        "note_zh": (
            "完整日更长表（AI: date,instrument,target_weight）经 alias 映射为 "
            "session,instrument_id,weight；禁把 ≤10 日 stub 当生产口径。"
        ),
    }
    if stub_window:
        meta["stub_window_warn"] = (
            f"WARN: only {n_sess} distinct sessions (≤{STUB_SESSION_WARN_MAX}); "
            "not a production full-daily series; do not treat as KPI success"
        )
    if extra:
        meta.update(extra)
    return meta


def write_weight_meta(meta: dict[str, Any], path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
