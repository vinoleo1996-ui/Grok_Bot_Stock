#!/usr/bin/env python3
"""Dragon-tiger seat-type panels for TrackA leaf expansion.

New leaves (baostock column alignment, same factory contract as build_dragon_panels):
  dt_inst_net_5/10, dt_nb_channel_net_5/10, dt_retail_hot_net_5/10,
  dt_inst_breadth, dt_inst_breadth_5

PIT (hard):
  Prefer available_at_alpha_conservative (≈T+1 15:00) → usable next session open
  (= trade T+2 open). Align via normalize()+1 calendar day then searchsorted on cal
  (same pattern as build_dragon_panels, but start from conservative).
  Fallback: available_at (trade_date 18:00) +1 calendar day → session align.
  Never shift available_at earlier.

promotion_approved=False. Does NOT run GP/SEARCH.
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

ROOT = Path("/workspace/QuantLab")
V2 = ROOT / "data/v2"
OUT_DIR = ROOT / "output/ai_factor/dt_seat_leaves_v1"
DOC = ROOT / "docs/v2/AI_DT_SEAT_LEAVES_WIRING_RECEIPT_ZH.md"
SRC = V2 / "dragon_tiger/top_inst_labeled.parquet"

LOOKBACK_START = pd.Timestamp("2024-04-01")
LOOKBACK_END = pd.Timestamp("2025-06-30")
MEM_CAP_MB = 2200

SEAT_INST = "institution"
SEAT_NB = "northbound_channel"
SEAT_RETAIL = "retail_or_hot_money"

LEAF_NAMES = [
    "dt_inst_net_5",
    "dt_inst_net_10",
    "dt_nb_channel_net_5",
    "dt_nb_channel_net_10",
    "dt_retail_hot_net_5",
    "dt_retail_hot_net_10",
    "dt_inst_breadth",
    "dt_inst_breadth_5",
]


def mem_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def peak_rss_mb() -> float:
    # Linux: ru_maxrss is KB
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


def _avail_date_from_dt(dt: pd.DataFrame) -> tuple[pd.Series, str]:
    """Return (avail_date calendar, rule_label). Never advances availability earlier."""
    if "available_at_alpha_conservative" in dt.columns and dt["available_at_alpha_conservative"].notna().any():
        avail = _normalize_avail(dt["available_at_alpha_conservative"])
        # conservative ≈ T+1 15:00 → +1 calendar day → T+2 open semantic
        rule = (
            "available_at_alpha_conservative.normalize()+1d → searchsorted(cal, left); "
            "≈T+1 15:00 SH → trade T+2 open; never forward-shift"
        )
        return avail + pd.Timedelta(days=1), rule
    if "available_at" in dt.columns:
        avail = _normalize_avail(dt["available_at"])
        rule = (
            "fallback available_at.normalize()+1d → searchsorted(cal, left); "
            "trade_date 18:00 SH → next session; never forward-shift"
        )
        return avail + pd.Timedelta(days=1), rule
    # last resort: trade_date + 1 (should not happen on labeled table)
    td = pd.to_datetime(dt["trade_date"].astype(str), errors="coerce")
    rule = "fallback trade_date+1d (no available_at columns)"
    return td + pd.Timedelta(days=1), rule


def _map_avail_to_cal_idx(avail_dates: np.ndarray, cal_np: np.ndarray) -> np.ndarray:
    """Vectorized: first session on/after avail_date (same intent as build_dragon_panels)."""
    # searchsorted left
    idx = np.searchsorted(cal_np, avail_dates.astype("datetime64[ns]"), side="left")
    T = len(cal_np)
    # clamp: if idx points past end, mark invalid as T
    idx = np.where(idx < T, idx, T)
    # if somehow cal[idx] < avail (shouldn't with left), bump — defensive
    valid = idx < T
    bump = valid & (cal_np[np.clip(idx, 0, T - 1)] < avail_dates.astype("datetime64[ns]"))
    idx = np.where(bump, idx + 1, idx)
    idx = np.where(idx < T, idx, T)
    return idx.astype(np.int64)


def build_dragon_seat_panels(cal, cols, mask) -> tuple[dict, dict]:
    """Build seat-split dragon panels aligned to (cal × cols).

    Returns (panels_dict, gap_meta).
    """
    gap: dict = {
        "path": str(SRC),
        "family": "dragon_tiger_seat",
        "promotion_approved": False,
        "search_enabled": False,
    }
    if not SRC.exists():
        gap["ok"] = False
        gap["error"] = "missing_top_inst_labeled"
        return {}, gap

    need_cols = [
        "trade_date",
        "ts_code",
        "net_buy",
        "seat_type",
        "available_at",
        "available_at_alpha_conservative",
        "exalter",
    ]
    # read only needed; filter seat types of interest
    dt = pd.read_parquet(SRC, columns=[c for c in need_cols if True])
    # drop unused broker_prop (keep but ignore in leaves)
    dt = dt[dt["seat_type"].isin([SEAT_INST, SEAT_NB, SEAT_RETAIL])].copy()
    dt["trade_date"] = pd.to_datetime(dt["trade_date"].astype(str), errors="coerce")
    avail_date, pit_rule = _avail_date_from_dt(dt)
    dt["avail_date"] = avail_date
    gap["available_at_rule"] = pit_rule
    gap["pit_note"] = "T+2 open semantic via conservative; never forward-shift available_at"

    dt["bs"] = dt["ts_code"].map(_to_baostock)
    col_set = set(cols)
    dt = dt[dt["bs"].isin(col_set)]
    cal_min = pd.Timestamp(cal.min())
    cal_max = pd.Timestamp(cal.max())
    dt = dt[
        (dt["avail_date"] >= cal_min - pd.Timedelta(days=40))
        & (dt["avail_date"] <= cal_max + pd.Timedelta(days=5))
    ]
    gap.update(
        {
            "ok": True,
            "n_events": int(len(dt)),
            "n_instruments": int(dt["bs"].nunique()),
            "seat_type_counts": {str(k): int(v) for k, v in dt["seat_type"].value_counts().items()},
            "trade_date_min": str(dt["trade_date"].min().date()) if len(dt) else None,
            "trade_date_max": str(dt["trade_date"].max().date()) if len(dt) else None,
            "avail_date_min": str(dt["avail_date"].min().date()) if len(dt) else None,
            "avail_date_max": str(dt["avail_date"].max().date()) if len(dt) else None,
        }
    )
    if dt.empty:
        gap["ok"] = False
        gap["error"] = "empty_after_filter"
        return {}, gap

    col_index = {c: i for i, c in enumerate(cols)}
    cal_np = cal.values.astype("datetime64[ns]")
    T, N = len(cal), len(cols)

    avail_np = dt["avail_date"].values.astype("datetime64[ns]")
    i_arr = _map_avail_to_cal_idx(avail_np, cal_np)
    j_arr = dt["bs"].map(col_index).to_numpy()
    valid = (i_arr < T) & np.isfinite(j_arr.astype(float))
    dt = dt.loc[valid].copy()
    dt["_i"] = i_arr[valid]
    dt["_j"] = j_arr[valid].astype(np.int64)
    dt["net_buy"] = pd.to_numeric(dt["net_buy"], errors="coerce").fillna(0.0)

    def _scatter_sum(sub: pd.DataFrame) -> np.ndarray:
        arr = np.zeros((T, N), dtype=np.float32)
        if sub.empty:
            return arr
        g = sub.groupby(["_i", "_j"], sort=False)["net_buy"].sum()
        ii = g.index.get_level_values(0).to_numpy(dtype=np.int64)
        jj = g.index.get_level_values(1).to_numpy(dtype=np.int64)
        arr[ii, jj] = g.to_numpy(dtype=np.float32)
        return arr

    def _scatter_breadth_inst(sub: pd.DataFrame) -> np.ndarray:
        """Count institution seats with net_buy>0 per (day, stock)."""
        arr = np.zeros((T, N), dtype=np.float32)
        if sub.empty:
            return arr
        pos = sub[sub["net_buy"] > 0]
        if pos.empty:
            return arr
        # count rows (each exalter row ≈ one seat appearance)
        if "exalter" in pos.columns:
            g = pos.groupby(["_i", "_j"], sort=False)["exalter"].nunique()
        else:
            g = pos.groupby(["_i", "_j"], sort=False)["net_buy"].size()
        ii = g.index.get_level_values(0).to_numpy(dtype=np.int64)
        jj = g.index.get_level_values(1).to_numpy(dtype=np.int64)
        arr[ii, jj] = g.to_numpy(dtype=np.float32)
        return arr

    inst = dt[dt["seat_type"] == SEAT_INST]
    nb = dt[dt["seat_type"] == SEAT_NB]
    retail = dt[dt["seat_type"] == SEAT_RETAIL]

    net_inst = _scatter_sum(inst)
    net_nb = _scatter_sum(nb)
    net_retail = _scatter_sum(retail)
    breadth = _scatter_breadth_inst(inst)

    del dt, inst, nb, retail
    gc.collect()

    def _df(a: np.ndarray) -> pd.DataFrame:
        return pd.DataFrame(a, index=cal, columns=cols, dtype="float32")

    net_inst_df = _df(net_inst)
    net_nb_df = _df(net_nb)
    net_retail_df = _df(net_retail)
    breadth_df = _df(breadth)
    del net_inst, net_nb, net_retail, breadth
    gc.collect()

    out = {
        "dt_inst_net_5": net_inst_df.rolling(5, min_periods=1).sum().astype("float32"),
        "dt_inst_net_10": net_inst_df.rolling(10, min_periods=1).sum().astype("float32"),
        "dt_nb_channel_net_5": net_nb_df.rolling(5, min_periods=1).sum().astype("float32"),
        "dt_nb_channel_net_10": net_nb_df.rolling(10, min_periods=1).sum().astype("float32"),
        "dt_retail_hot_net_5": net_retail_df.rolling(5, min_periods=1).sum().astype("float32"),
        "dt_retail_hot_net_10": net_retail_df.rolling(10, min_periods=1).sum().astype("float32"),
        "dt_inst_breadth": breadth_df.astype("float32"),
        "dt_inst_breadth_5": breadth_df.rolling(5, min_periods=1).sum().astype("float32"),
    }
    del net_inst_df, net_nb_df, net_retail_df, breadth_df
    gc.collect()

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
    gap["ready_for_next_search"] = list(out.keys())
    gap["search_switch"] = "OFF — do not start v27 GP until New Bot releases"
    gap["hk_hold"] = {
        "status": "conditional_wiring_only",
        "note": "日频截断~2024-06/08；未拉全量进工厂",
    }
    gap["hsgt_top10"] = {"status": "BLOCKED", "note": "等 Data 续期；勿开 GP 依赖"}
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
    print(f"[dt_seat] start peak={peak:.0f}MB pid={os.getpid()}", flush=True)

    cal, cols = _load_cal_cols_skinny()
    peak = max(peak, peak_rss_mb())
    print(f"[dt_seat] cal {cal.min().date()}→{cal.max().date()} n={len(cal)} cols={len(cols)} peak={peak:.0f}", flush=True)

    # mask: None — wiring sample keeps all; factory callers can pass midlarge mask
    panels, gap = build_dragon_seat_panels(cal, cols, mask=None)
    peak = max(peak, peak_rss_mb())
    print(f"[dt_seat] built leaves={list(panels.keys())} peak={peak:.0f} ok={gap.get('ok')}", flush=True)

    # dump skinny sample parquets (one file per leaf, float32)
    sample_paths = {}
    for k, df in panels.items():
        p = OUT_DIR / f"{k}.parquet"
        # store as stacked to save space? keep wide for factory-like inspection but compress
        df.to_parquet(p, compression="zstd")
        sample_paths[k] = str(p)
        print(f"[dt_seat] wrote {p.name} shape={df.shape} nonempty={gap.get('nonempty_'+k):.4f}", flush=True)
        peak = max(peak, peak_rss_mb())
        if peak > MEM_CAP_MB:
            print(f"[dt_seat] WARN peak {peak:.0f}>{MEM_CAP_MB}", flush=True)

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
        "v27_gp_started": False,
        "search_enabled": False,
        "module": "research/ai_factor_dt_seat_panels.py",
        "function": "build_dragon_seat_panels",
        "ready_for_next_search_leaves": gap.get("ready_for_next_search", LEAF_NAMES),
        "hk_hold": gap.get("hk_hold"),
        "hsgt_top10": gap.get("hsgt_top10"),
        "available_at_rule": gap.get("available_at_rule"),
    }
    receipt_path = OUT_DIR / "wiring_receipt.json"
    receipt_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"[dt_seat] receipt {receipt_path}", flush=True)

    # Chinese short doc
    lines = [
        "# 龙虎席位叶接线回执（TrackA）",
        "",
        "| 项 | 值 |",
        "|---|---|",
        f"| 日期 | 2026-10-12 ET |",
        f"| PID | {os.getpid()} |",
        f"| peak_rss_MB | {peak:.1f} |",
        f"| 窗 | {LOOKBACK_START.date()} → {LOOKBACK_END.date()} |",
        f"| promotion_approved | **false** |",
        f"| v27 GP / SEARCH | **未启动**（开关关） |",
        "",
        "## 叶名",
        "",
    ]
    for n in LEAF_NAMES:
        ne = gap.get(f"nonempty_{n}")
        mn = gap.get(f"mean_names_{n}")
        lines.append(f"- `{n}` — nonempty={ne:.4f} if isinstance else {ne}; mean_names/day={mn}")
    lines += [
        "",
        "## available_at 规则（硬）",
        "",
        f"- {gap.get('available_at_rule')}",
        "- **不可前移** available_at。",
        "",
        "## 路径",
        "",
        f"- 模块：`research/ai_factor_dt_seat_panels.py` → `build_dragon_seat_panels`",
        f"- 样例面板：`output/ai_factor/dt_seat_leaves_v1/*.parquet`",
        f"- JSON：`output/ai_factor/dt_seat_leaves_v1/wiring_receipt.json`",
        "",
        "## 其它",
        "",
        "- hk_hold：**条件接线**（日频截断~2024-06/08）；**未**拉全量进工厂。",
        "- hsgt_top10：**BLOCKED**（等 Data 续期）。",
        "- 可进下一轮 SEARCH 的叶名见 receipt `ready_for_next_search_leaves`；**本轮不跑 SEARCH**。",
        "- 不交 Strategy。",
        "",
    ]
    # fix the awkward nonempty line
    lines = []
    lines += [
        "# 龙虎席位叶接线回执（TrackA）",
        "",
        "| 项 | 值 |",
        "|---|---|",
        f"| 日期 | 2026-10-12 ET |",
        f"| PID | {os.getpid()} |",
        f"| peak_rss_MB | {peak:.1f} |",
        f"| 窗 | {LOOKBACK_START.date()} → {LOOKBACK_END.date()} |",
        "| promotion_approved | **false** |",
        "| v27 GP / SEARCH | **未启动**（开关关） |",
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
        "- 模块：`research/ai_factor_dt_seat_panels.py` → `build_dragon_seat_panels`",
        "- 样例面板：`output/ai_factor/dt_seat_leaves_v1/*.parquet`",
        "- JSON：`output/ai_factor/dt_seat_leaves_v1/wiring_receipt.json`",
        "",
        "## 其它",
        "",
        "- hk_hold：**条件接线**（日频截断~2024-06/08）；**未**拉全量进工厂。",
        "- hsgt_top10：**BLOCKED**（等 Data 续期）。",
        "- 可进下一轮 SEARCH 的叶名见 receipt `ready_for_next_search_leaves`；**本轮不跑 SEARCH**。",
        "- 不交 Strategy。",
        "",
    ]
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"[dt_seat] doc {DOC} peak={peak:.0f}MB done", flush=True)

    del panels
    gc.collect()
    return 0 if gap.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
