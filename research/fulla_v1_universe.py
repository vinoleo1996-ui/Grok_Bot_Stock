"""FULLA_V1 universe override (AI, 2026-10-14).

Replaces ONLY the candidate pool of g1g5 leg scripts:
  - static universe = every instrument with in_universe=True at least once
  - PIT daily membership = mask in_universe
  - open/close gap panel = bulk tushare daily (same raw OHLC as load_panel_features_x2)
  - industry peers = same sw_code_on semantics, vectorized

Mask: output/strategy_fulla/universe_mask_fulla_v1.parquet (Strategy, FROZEN 07:35 ET).
Leg logic otherwise untouched. live=false; does not touch FROZEN_CONFIG / paper tracks.
"""
from __future__ import annotations

import hashlib
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/workspace/QuantLab")
MASK = ROOT / "output/strategy_fulla/universe_mask_fulla_v1.parquet"
MASK_SHA = "b5d9f1abd34bc550dd18a3eb2617a7d417cc60d29fbb02dceee02024e19fc7cd"
DAILY = ROOT / "data/v2/tushare_raw/daily"


@lru_cache(1)
def _mask() -> pd.DataFrame:
    got = hashlib.sha256(MASK.read_bytes()).hexdigest()
    assert got == MASK_SHA, f"mask sha mismatch: {got}"
    m = pd.read_parquet(MASK, columns=["date", "instrument", "in_universe"])
    m = m[m["in_universe"].astype(bool)].copy()
    m["s"] = m["date"].dt.strftime("%Y-%m-%d")
    return m[["s", "instrument"]]


def select_fulla_v1(top_n=None, anchor=None):
    m = _mask()
    return dict(
        instruments=sorted(m["instrument"].unique().tolist()),
        anchor_session="PIT_daily",
        source_pit=str(MASK),
        mask_sha256=MASK_SHA,
    )


def member_index_fulla_v1(instruments, sessions):
    want = set(instruments)
    ss = {str(s)[:10] for s in sessions}
    m = _mask()
    m = m[m["s"].isin(ss) & m["instrument"].isin(want)]
    out = {s: set() for s in ss}
    for s, g in m.groupby("s", sort=False):
        out[s] = set(g["instrument"].tolist())
    return out


def load_gap_panel(instruments, cal_full: pd.DatetimeIndex) -> tuple[pd.DataFrame, pd.Series | None]:
    """Return (gap_all, ballast_gap) with same definition as
    op/cl from load_panel_features_x2: gap = open/close.shift(1)-1.
    Uses tushare_raw/daily (verified equal to panel open/close)."""
    cache = ROOT / "output/strategy_fulla/legs/_work/gap_panel_fulla_v1.parquet"
    bcache = ROOT / "output/strategy_fulla/legs/_work/bgap_fulla_v1.parquet"
    if cache.exists():
        gap = pd.read_parquet(cache)
        gap = gap.reindex(index=cal_full, columns=list(instruments)).astype("float32")
        bgap = None
        if bcache.exists():
            bgap = pd.read_parquet(bcache)["bgap"].reindex(cal_full)
        return gap, bgap
    want = set(instruments)
    parts = []
    for d in cal_full:
        p = DAILY / f"{d.strftime('%Y%m%d')}.parquet"
        if not p.exists():
            continue
        df = pd.read_parquet(p, columns=["ts_code", "open", "close"])
        df = df[df["ts_code"].isin(want)]
        if df.empty:
            continue
        df = df.copy()
        df["date"] = d
        parts.append(df)
    if not parts:
        gap = pd.DataFrame(index=cal_full, columns=list(instruments), dtype="float32")
        return gap, None
    long = pd.concat(parts, ignore_index=True)
    op = long.pivot(index="date", columns="ts_code", values="open").reindex(cal_full)
    cl = long.pivot(index="date", columns="ts_code", values="close").reindex(cal_full)
    op = op.reindex(columns=list(instruments)).astype("float32")
    cl = cl.reindex(columns=list(instruments)).astype("float32")
    gap = (op / cl.shift(1) - 1.0).astype("float32")
    bgap = None
    try:
        fd = ROOT / "data/v2/tushare_raw/fund_daily/510300.SH.parquet"
        if fd.exists():
            b = pd.read_parquet(fd)
            # trade_date YYYYMMDD
            col_d = "trade_date" if "trade_date" in b.columns else "date"
            b[col_d] = pd.to_datetime(b[col_d].astype(str))
            b = b.set_index(col_d).sort_index()
            bgap = (b["open"] / b["close"].shift(1) - 1).reindex(cal_full)
    except Exception:
        bgap = None
    return gap, bgap


def industry_on_date(instruments, session, sw: pd.DataFrame) -> dict[str, str]:
    """Vectorized sw_code_on for many instruments on one session (same semantics)."""
    from research.g1g5_nontextbook_weights import to_panel_id

    sess = pd.Timestamp(session).normalize()
    want_pids = {to_panel_id(x): x for x in instruments}
    sub = sw[sw["instrument_id"].isin(want_pids.keys())].copy()
    if sub.empty:
        return {}
    hit = sub[(sub["in_date"] <= sess) & ((sub["out_date"].isna()) | (sub["out_date"] > sess))]
    if hit.empty:
        return {}
    # last row per instrument_id (same as iloc[-1] after filter)
    hit = hit.sort_values(["instrument_id", "in_date"])
    last = hit.groupby("instrument_id", sort=False).tail(1)
    return {want_pids[pid]: str(code) for pid, code in zip(last["instrument_id"], last["sw_code"]) if pid in want_pids}


def peers_by_industry(instruments, session, sw: pd.DataFrame) -> dict[str, list[str]]:
    ind_of = industry_on_date(instruments, session, sw)
    buckets: dict[str, list[str]] = {}
    for inst, ind in ind_of.items():
        buckets.setdefault(ind, []).append(inst)
    return buckets
