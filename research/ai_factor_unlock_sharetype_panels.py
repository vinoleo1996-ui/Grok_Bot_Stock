#!/usr/bin/env python3
"""Unlock share_type panels for STOCK-UNLOCK-SHARETYPE (V30) leaf wiring.

Leaves (baostock column alignment):
  unlock_private_place_share_20   — share_type含「定增」float_share，avail入日后 rolling(20).sum
  unlock_private_place_ratio_20   — 定增 float_ratio，avail入日后 rolling(20).sum
  unlock_strategic_share_20       — share_type含「战略配售」float_share，rolling(20).sum
  unlock_incentive_share_20       — share_type含「股权激励」float_share，rolling(20).sum
  unlock_private_place_frac_20    — 定增/(定增+战略+激励+ε) on rolling share panels

PIT (hard):
  available_at (ann_date 18:00 Asia/Shanghai) → normalize()+1 calendar day
  → searchsorted(cal, left) = first session on/after that date.
  Never forward-shift available_at.

promotion_approved=False. Does NOT run NAV / backtest / GP / v27 / SEARCH.
"""
from __future__ import annotations

import gc
import json
import os
import resource
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

ROOT = Path("/workspace/QuantLab")
V2 = ROOT / "data/v2"
SRC = V2 / "share_float/share_float_pit.parquet"
OUT_DIR = ROOT / "output/ai_factor/unlock_sharetype_leaves_v1"
DOC = ROOT / "docs/v2/AI_UNLOCK_SHARETYPE_LEAVES_WIRING_RECEIPT_ZH.md"

LOOKBACK_START = pd.Timestamp("2024-04-01")
LOOKBACK_END = pd.Timestamp("2025-06-30")
MEM_CAP_MB = 2200
EPS = 1e-12
ROLL = 20

LEAF_NAMES = [
    "unlock_private_place_share_20",
    "unlock_private_place_ratio_20",
    "unlock_strategic_share_20",
    "unlock_incentive_share_20",
    "unlock_private_place_frac_20",
]

BUCKET_PRIVATE = "private"
BUCKET_STRATEGIC = "strategic"
BUCKET_INCENTIVE = "incentive"


def mem_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def peak_rss_mb() -> float:
    return mem_mb()


def _to_baostock(ts_code: str) -> str:
    s = str(ts_code)
    if "." in s:
        code, ex = s.split(".", 1)
        return f"{ex.lower()}.{code}"
    return s


def _normalize_avail(series: pd.Series) -> pd.Series:
    av = pd.to_datetime(series, errors="coerce")
    if getattr(av.dt, "tz", None) is not None:
        return av.dt.tz_convert("Asia/Shanghai").dt.normalize().dt.tz_localize(None)
    return av.dt.normalize()


def _map_avail_to_cal_idx(avail_dates: np.ndarray, cal_np: np.ndarray) -> np.ndarray:
    """First session on/after avail_date (searchsorted left); never earlier."""
    idx = np.searchsorted(cal_np, avail_dates.astype("datetime64[ns]"), side="left")
    T = len(cal_np)
    idx = np.where(idx < T, idx, T)
    valid = idx < T
    bump = valid & (cal_np[np.clip(idx, 0, T - 1)] < avail_dates.astype("datetime64[ns]"))
    idx = np.where(bump, idx + 1, idx)
    idx = np.where(idx < T, idx, T)
    return idx.astype(np.int64)


def _bucket_share_type(s: str) -> str:
    s = str(s)
    if "定增" in s:
        return BUCKET_PRIVATE
    if "战略配售" in s:
        return BUCKET_STRATEGIC
    if "股权激励" in s:
        return BUCKET_INCENTIVE
    return "other"


def _load_share_float_events(cal_min: pd.Timestamp, cal_max: pd.Timestamp) -> tuple[pd.DataFrame, str]:
    """Load + filter + aggregate holder rows → (ts_code, avail_date, bucket) sums.

    PIT rule: available_at.normalize()+1d (ann 18:00 SH → next calendar day),
    then caller maps via searchsorted onto trading calendar.
    """
    pit_rule = (
        "available_at.normalize()+1d → searchsorted(cal, left); "
        "ann_date 18:00 Asia/Shanghai → next session open; never forward-shift"
    )
    if not SRC.exists():
        return pd.DataFrame(), pit_rule

    need = ["ts_code", "float_share", "float_ratio", "share_type", "available_at"]
    table = pq.read_table(SRC, columns=need)

    # date window with buffer for rolling warmup / edge
    lo = pa.scalar((cal_min - pd.Timedelta(days=40)).tz_localize("Asia/Shanghai").to_pydatetime())
    hi = pa.scalar((cal_max + pd.Timedelta(days=5)).tz_localize("Asia/Shanghai").replace(
        hour=23, minute=59, second=59
    ).to_pydatetime())
    date_mask = pc.and_(
        pc.greater_equal(table["available_at"], lo),
        pc.less_equal(table["available_at"], hi),
    )
    type_mask = pc.or_(
        pc.or_(
            pc.match_substring(table["share_type"], "定增"),
            pc.match_substring(table["share_type"], "战略配售"),
        ),
        pc.match_substring(table["share_type"], "股权激励"),
    )
    table = table.filter(pc.and_(date_mask, type_mask))
    df = table.to_pandas()
    del table
    gc.collect()

    if df.empty:
        return df, pit_rule

    avail_norm = _normalize_avail(df["available_at"])
    # +1 calendar day after ann 18:00 normalize → next-day open semantic
    df["avail_date"] = avail_norm + pd.Timedelta(days=1)
    df["bucket"] = df["share_type"].map(_bucket_share_type)
    df["float_share"] = pd.to_numeric(df["float_share"], errors="coerce").fillna(0.0)
    df["float_ratio"] = pd.to_numeric(df["float_ratio"], errors="coerce").fillna(0.0)
    df = df[df["bucket"].isin([BUCKET_PRIVATE, BUCKET_STRATEGIC, BUCKET_INCENTIVE])]

    g = (
        df.groupby(["ts_code", "avail_date", "bucket"], as_index=False, sort=False)
        .agg(float_share=("float_share", "sum"), float_ratio=("float_ratio", "sum"))
    )
    del df
    gc.collect()
    return g, pit_rule


def build_unlock_sharetype_panels(cal, cols, mask) -> tuple[dict, dict]:
    """Build unlock share_type panels aligned to (cal × cols).

    Returns (panels_dict, gap_meta).
    """
    gap: dict = {
        "path": str(SRC),
        "family": "unlock_sharetype",
        "promotion_approved": False,
        "search_enabled": False,
        "nav_run": False,
        "gp_run": False,
        "v27_started": False,
    }
    if not SRC.exists():
        gap["ok"] = False
        gap["error"] = "missing_share_float_pit"
        return {}, gap

    cal = pd.DatetimeIndex(cal)
    cal_min = pd.Timestamp(cal.min())
    cal_max = pd.Timestamp(cal.max())
    events, pit_rule = _load_share_float_events(cal_min, cal_max)
    gap["available_at_rule"] = pit_rule
    gap["pit_note"] = "ann 18:00 SH → +1d → first session on/after; never forward-shift available_at"

    if events.empty:
        gap["ok"] = False
        gap["error"] = "empty_after_filter"
        return {}, gap

    events["bs"] = events["ts_code"].map(_to_baostock)
    col_set = set(cols)
    events = events[events["bs"].isin(col_set)].copy()
    gap.update(
        {
            "ok": True,
            "n_events_agg": int(len(events)),
            "n_instruments": int(events["bs"].nunique()),
            "bucket_counts": {str(k): int(v) for k, v in events["bucket"].value_counts().items()},
            "avail_date_min": str(events["avail_date"].min().date()) if len(events) else None,
            "avail_date_max": str(events["avail_date"].max().date()) if len(events) else None,
            "share_type_match": {
                "private": "定增",
                "strategic": "战略配售",
                "incentive": "股权激励",
            },
        }
    )
    if events.empty:
        gap["ok"] = False
        gap["error"] = "empty_after_universe_filter"
        return {}, gap

    col_index = {c: i for i, c in enumerate(cols)}
    cal_np = cal.values.astype("datetime64[ns]")
    T, N = len(cal), len(cols)

    avail_np = events["avail_date"].values.astype("datetime64[ns]")
    i_arr = _map_avail_to_cal_idx(avail_np, cal_np)
    j_arr = events["bs"].map(col_index).to_numpy()
    valid = (i_arr < T) & np.isfinite(j_arr.astype(float))
    events = events.loc[valid].copy()
    events["_i"] = i_arr[valid]
    events["_j"] = j_arr[valid].astype(np.int64)

    def _scatter_sum(sub: pd.DataFrame, value_col: str) -> np.ndarray:
        arr = np.zeros((T, N), dtype=np.float32)
        if sub.empty:
            return arr
        g = sub.groupby(["_i", "_j"], sort=False)[value_col].sum()
        ii = g.index.get_level_values(0).to_numpy(dtype=np.int64)
        jj = g.index.get_level_values(1).to_numpy(dtype=np.int64)
        arr[ii, jj] = g.to_numpy(dtype=np.float32)
        return arr

    priv = events[events["bucket"] == BUCKET_PRIVATE]
    strat = events[events["bucket"] == BUCKET_STRATEGIC]
    ince = events[events["bucket"] == BUCKET_INCENTIVE]

    priv_share = _scatter_sum(priv, "float_share")
    priv_ratio = _scatter_sum(priv, "float_ratio")
    strat_share = _scatter_sum(strat, "float_share")
    ince_share = _scatter_sum(ince, "float_share")

    del events, priv, strat, ince
    gc.collect()

    def _df(a: np.ndarray) -> pd.DataFrame:
        return pd.DataFrame(a, index=cal, columns=cols, dtype="float32")

    priv_share_df = _df(priv_share)
    priv_ratio_df = _df(priv_ratio)
    strat_share_df = _df(strat_share)
    ince_share_df = _df(ince_share)
    del priv_share, priv_ratio, strat_share, ince_share
    gc.collect()

    priv_share_r = priv_share_df.rolling(ROLL, min_periods=1).sum().astype("float32")
    priv_ratio_r = priv_ratio_df.rolling(ROLL, min_periods=1).sum().astype("float32")
    strat_share_r = strat_share_df.rolling(ROLL, min_periods=1).sum().astype("float32")
    ince_share_r = ince_share_df.rolling(ROLL, min_periods=1).sum().astype("float32")
    del priv_share_df, priv_ratio_df, strat_share_df, ince_share_df
    gc.collect()

    denom = (priv_share_r + strat_share_r + ince_share_r + EPS).astype("float32")
    frac = (priv_share_r / denom).astype("float32")

    out = {
        "unlock_private_place_share_20": priv_share_r,
        "unlock_private_place_ratio_20": priv_ratio_r,
        "unlock_strategic_share_20": strat_share_r,
        "unlock_incentive_share_20": ince_share_r,
        "unlock_private_place_frac_20": frac,
    }

    if mask is not None:
        for k in list(out.keys()):
            out[k] = out[k].where(mask).astype("float32")

    for k, df in out.items():
        nz = df.notna() & (df.abs() > 1e-12)
        gap[f"nonempty_{k}"] = float(nz.to_numpy().mean())
        gap[f"mean_names_{k}"] = float(nz.sum(axis=1).mean())
        gap[f"date_min_{k}"] = str(df.index.min().date())
        gap[f"date_max_{k}"] = str(df.index.max().date())
        gap[f"nrows_{k}"] = int(df.shape[0])
        gap[f"ncols_{k}"] = int(df.shape[1])

    gap["leaf_names"] = list(out.keys())
    gap["ready_for_beta_x1"] = list(out.keys())
    gap["search_switch"] = "OFF — wiring only; no v27 GP; Beta owns STOCK-UNLOCK-SHARETYPE X1"
    return out, gap


def _load_cal_cols_skinny():
    """Skinny calendar/universe from scratch close for wiring sample."""
    close = pd.read_parquet("/workspace/scratch/tic/close.parquet")
    cal = close.index
    cal = cal[(cal >= LOOKBACK_START) & (cal <= LOOKBACK_END)]
    cols = list(close.columns)
    del close
    gc.collect()
    return pd.DatetimeIndex(cal), cols


def main() -> int:
    t0 = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC.parent.mkdir(parents=True, exist_ok=True)
    peak = peak_rss_mb()
    print(f"[unlock_st] start peak={peak:.0f}MB pid={os.getpid()}", flush=True)

    cal, cols = _load_cal_cols_skinny()
    peak = max(peak, peak_rss_mb())
    print(
        f"[unlock_st] cal {cal.min().date()}→{cal.max().date()} n={len(cal)} "
        f"cols={len(cols)} peak={peak:.0f}",
        flush=True,
    )

    panels, gap = build_unlock_sharetype_panels(cal, cols, mask=None)
    peak = max(peak, peak_rss_mb())
    print(
        f"[unlock_st] built leaves={list(panels.keys())} peak={peak:.0f} ok={gap.get('ok')}",
        flush=True,
    )

    sample_paths = {}
    for k, df in panels.items():
        p = OUT_DIR / f"{k}.parquet"
        df.to_parquet(p, compression="zstd")
        sample_paths[k] = str(p)
        ne = gap.get(f"nonempty_{k}")
        print(f"[unlock_st] wrote {p.name} shape={df.shape} nonempty={ne}", flush=True)
        peak = max(peak, peak_rss_mb())
        if peak > MEM_CAP_MB:
            print(f"[unlock_st] WARN peak {peak:.0f}>{MEM_CAP_MB}", flush=True)

    meta = {
        "pid": os.getpid(),
        "peak_rss_MB": round(peak, 1),
        "elapsed_s": round(time.time() - t0, 1),
        "lookback": [str(LOOKBACK_START.date()), str(LOOKBACK_END.date())],
        "n_cal": int(len(cal)),
        "n_cols": int(len(cols)),
        "leaf_names": LEAF_NAMES,
        "sample_paths": sample_paths,
        "gap": gap,
        "promotion_approved": False,
        "nav_run": False,
        "backtest_run": False,
        "v27_gp_started": False,
        "search_enabled": False,
        "module": "research/ai_factor_unlock_sharetype_panels.py",
        "function": "build_unlock_sharetype_panels",
        "available_at_rule": gap.get("available_at_rule"),
        "source": str(SRC),
        "proposal": "docs/v2/AI_STOCK_ARM_PROPOSAL_V30_UNLOCK_SHARETYPE_ZH.md",
        "note": "wiring only; Beta owns STOCK-UNLOCK-SHARETYPE X1 smoke; no Strategy handoff",
    }
    receipt_path = OUT_DIR / "wiring_receipt.json"
    receipt_path.write_text(
        json.dumps(meta, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )
    print(f"[unlock_st] receipt {receipt_path}", flush=True)

    lines = [
        "# 解禁 share_type 叶接线回执（STOCK-UNLOCK-SHARETYPE / V30）",
        "",
        "| 项 | 值 |",
        "|---|---|",
        "| 日期 | 2026-10-12 ET |",
        f"| PID | {os.getpid()} |",
        f"| peak_rss_MB | {peak:.1f} |",
        f"| 窗 | {LOOKBACK_START.date()} → {LOOKBACK_END.date()} |",
        "| promotion_approved | **false** |",
        "| NAV / 回测 / GP / v27 | **未跑**（仅接线） |",
        "| Strategy | **不交** |",
        "| Beta | 主跑 STOCK-UNLOCK-SHARETYPE X1；本侧只交叶 |",
        "",
        "## 叶名",
        "",
    ]
    for n in LEAF_NAMES:
        ne = gap.get(f"nonempty_{n}")
        mn = gap.get(f"mean_names_{n}")
        ne_s = f"{ne:.4f}" if isinstance(ne, float) else str(ne)
        mn_s = f"{mn:.2f}" if isinstance(mn, float) else str(mn)
        lines.append(f"- `{n}` — nonempty={ne_s}; mean_names/day={mn_s}")
    lines += [
        "",
        "## available_at 规则（硬）",
        "",
        f"- {gap.get('available_at_rule')}",
        "- **不可前移** available_at。",
        "",
        "## 路径",
        "",
        "- 模块：`research/ai_factor_unlock_sharetype_panels.py` → `build_unlock_sharetype_panels`",
        "- 样例面板：`output/ai_factor/unlock_sharetype_leaves_v1/*.parquet`",
        "- JSON：`output/ai_factor/unlock_sharetype_leaves_v1/wiring_receipt.json`",
        "- 源表：`data/v2/share_float/share_float_pit.parquet`",
        "",
        "## 其它",
        "",
        "- 不磨 seat；不启 v27；不交 Strategy。",
        "- 覆盖如实（解禁事件稀），勿降 θ。",
        "",
    ]
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"[unlock_st] doc {DOC} peak={peak:.0f}MB done", flush=True)

    del panels
    gc.collect()
    return 0 if gap.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
