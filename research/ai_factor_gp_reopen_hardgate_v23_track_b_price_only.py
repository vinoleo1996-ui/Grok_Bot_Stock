#!/usr/bin/env python3
"""GP reopen v22 — B-track ETF timing with available_at PIT asof (New Bot 2026-10-12).

Why: Beta rejected v21 — share-flow panes keyed by trade_date same day → package
ICIR≈1.6 but PIT ICIR≈−0.10; real NAV smoke failed (trade_date leakage).

Fix:
  - ETF share-flow features enter ONLY via strict available_at ≤ decision_time asof
    (decision=D 09:00 open; NOT fixed lag1; handles 23:59 and 09:00 clocks).
  - Fitness / GATE only on PIT ICIR; also report leak-control (trade_date-aligned)
    ICIR fields but NOT as pass gates.
  - y = industry ETF fwd 1d (report 5d) excess vs 510300 — NOT flow.
  - sleeve=etf_timing_price; hand Beta ONLY; NOT Alpha shortlist; no Strategy.
  - MEM_CAP=2200; SELF_STOP sticky>2400 OR available<2500 — DO NOT raise.
  - SEED=20261105; WINDOW=gp_reopen_hardgate_v23_track_b_etf_price_20240603_explore
  - Lean window LOOKBACK=2024-04-01 PANEL_END=2025-06-30

Launch: LEO_AI_FACTOR_EXPLORE_OK=1 /workspace/qlvenv/bin/python -u …
"""
from __future__ import annotations

import gc
import importlib.util
import json
import math
import os
import resource
import sys
import time
import types
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/workspace/QuantLab")
OUT = ROOT / "output/ai_factor/gp_reopen_hardgate_v23_track_b_etf_price"
REPORT_NOTE = OUT / "REPORT_NOTE_ZH.md"
V2 = ROOT / "data/v2"

EXPLORE_START = pd.Timestamp("2024-06-03")
LOOKBACK_START = pd.Timestamp("2024-04-01")  # lean — DO NOT widen
PANEL_END = pd.Timestamp("2025-06-30")
SEED = 20261106
WINDOW = "gp_reopen_hardgate_v23_track_b_etf_price_20240603_explore"
MAX_EVAL = 120
COST = 0.0025  # round-trip proxy for after-cost gate
PROMOTION_APPROVED = False
MEM_CAP_MB = 2200  # DO NOT raise
SELF_STOP_AVAILABLE_MB = 2500
SELF_STOP_RSS_STICKY_MB = 2400  # DO NOT raise
IMPACT_CNY = (600_000, 1_000_000)  # 60万 ∧ 100万

CB_GOLD_BANNED_STEMS = (
    "cb_", "convertible", "bond_prem", "matprem", "gold", "au999", "au9999",
    "gld_", "huangjin",
)

t0 = time.time()


def mem_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def available_mb() -> float:
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) / 1024.0
    except Exception:
        pass
    return float("nan")


def log(*a):
    print(f"[gp_v23b {time.time()-t0:5.0f}s {mem_mb():.0f}MB]", *a, flush=True)


def clean(o):
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(x) for x in o]
    if isinstance(o, (np.bool_, bool)):
        return bool(o)
    if isinstance(o, (np.floating, float)):
        x = float(o)
        return None if not math.isfinite(x) else x
    if isinstance(o, (np.integer, int)):
        return int(o)
    if isinstance(o, pd.Timestamp):
        return str(o)
    return o


def _ensure_pkgs():
    if "quantlab" not in sys.modules:
        q = types.ModuleType("quantlab")
        q.__path__ = [str(ROOT / "quantlab")]
        sys.modules["quantlab"] = q
    if "quantlab.factors" not in sys.modules or not hasattr(sys.modules["quantlab.factors"], "__path__"):
        f = types.ModuleType("quantlab.factors")
        f.__path__ = [str(ROOT / "quantlab/factors")]
        sys.modules["quantlab.factors"] = f

    def load(name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        assert spec.loader
        spec.loader.exec_module(mod)
        return mod

    load("quantlab.factors.ops", ROOT / "quantlab/factors/ops.py")


def leaves_in(expr: str) -> frozenset[str]:
    import re
    return frozenset(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expr)) - {
        "ts_mean", "ts_std", "ts_delta", "ts_max", "ts_min", "neg", "abs", "rank",
        "mul", "sub", "div", "add", "delay",
    }


def _ymd_series(s: pd.Series) -> pd.Series:
    return pd.to_datetime(
        s.astype(str).str.replace("-", "", regex=False).str[:8],
        format="%Y%m%d",
        errors="coerce",
    )


def load_sessions() -> pd.DatetimeIndex:
    """SSE open sessions spanning lean window (+lookback buffer)."""
    paths = [
        V2 / "asof_extend_202610/calendar.parquet",
        V2 / "tushare_raw/trade_cal.parquet",
    ]
    for p in paths:
        if not p.exists():
            continue
        df = pd.read_parquet(p)
        if "session" in df.columns:
            sess = pd.to_datetime(df["session"]).dropna().sort_values().unique()
            return pd.DatetimeIndex(sess)
        if "cal_date" in df.columns:
            open_mask = df["is_open"] == 1 if "is_open" in df.columns else slice(None)
            sub = df.loc[open_mask]
            sess = _ymd_series(sub["cal_date"]).dropna().sort_values().unique()
            return pd.DatetimeIndex(sess)
    raise FileNotFoundError("no trade calendar found for PIT asof")


# Decision clock for PIT asof (documented; NOT a fixed lag1 / NOT always 09:00 publish).
# Data: available_at = max(份额下一交易日09:00, 净值max(ann,trade)23:59);
# by_sw_l1 ~75% 23:59 / ~25% 09:00 — must use wall-clock asof, not td+1 shift.
DECISION_CLOCK = "open"  # decision_time(D) = D 09:00 Asia/Shanghai (session open)
# Alternative documented: "prior_close" → decision_time(D) = prev_session(D) 15:00


def decision_times(sessions: pd.DatetimeIndex, clock: str = DECISION_CLOCK) -> pd.DatetimeIndex:
    sess = sessions.sort_values()
    if clock == "open":
        return pd.DatetimeIndex(sess + pd.Timedelta(hours=9))
    if clock == "prior_close":
        # usable at D's decision iff known by previous session's close
        # map: decision at D uses info with available_at <= prev_session 15:00
        # We still index panels by session D; search uses prior-close timestamps.
        prev = sess.to_series().shift(1)
        # first session has no prior — use sess[0]-1day 15:00
        prev_idx = pd.DatetimeIndex(prev.fillna(sess[0] - pd.Timedelta(days=1)))
        return pd.DatetimeIndex(prev_idx + pd.Timedelta(hours=15))
    raise ValueError(f"unknown decision clock: {clock}")


def available_at_to_usable_session(
    available_at: pd.Series,
    sessions: pd.DatetimeIndex,
    *,
    clock: str = DECISION_CLOCK,
) -> pd.Series:
    """Map available_at → first session D with decision_time(D) >= available_at.

    Strict PIT: feature usable on D iff available_at <= decision_time(D).
    Default decision_time(D) = D 09:00 (open). This is NOT fixed lag1 and does
    NOT assume every row is 09:00 — 23:59 publishes become usable only on the
    next session's open; 09:00 publishes are usable that same session (≤ open).
    """
    aa = pd.to_datetime(available_at)
    if getattr(aa.dt, "tz", None) is not None:
        aa = aa.dt.tz_convert("Asia/Shanghai").dt.tz_localize(None)
    sess = sessions.sort_values()
    dec = decision_times(sess, clock=clock)
    # first decision_time >= available_at  →  corresponding session
    pos = dec.searchsorted(aa.to_numpy(), side="left")
    out = pd.Series(pd.NaT, index=available_at.index, dtype="datetime64[ns]")
    valid = pos < len(sess)
    if np.any(valid):
        out.iloc[np.flatnonzero(valid)] = sess.to_numpy()[pos[valid]]
    return out


def load_510300_ret() -> tuple[pd.Series, dict]:
    meta: dict = {"path": None, "ok": False}
    paths = [
        V2 / "etf_510300/fund_daily_tushare_510300.parquet",
        V2 / "tushare_raw/fund_daily/510300.SH.parquet",
    ]
    for p in paths:
        if not p.exists():
            continue
        df = pd.read_parquet(p)
        meta["path"] = str(p.relative_to(ROOT))
        td = _ymd_series(df["trade_date"])
        df = df.assign(_td=td).dropna(subset=["_td"]).sort_values("_td")
        if "close" in df.columns:
            ret = df.set_index("_td")["close"].astype("float64").pct_change()
        elif "pct_chg" in df.columns:
            ret = df.set_index("_td")["pct_chg"].astype("float64") / 100.0
        else:
            continue
        ret = ret.loc[(ret.index >= LOOKBACK_START - pd.Timedelta(days=5)) & (ret.index <= PANEL_END)]
        ret = ret.astype("float32")
        meta.update(
            {
                "ok": True,
                "n": int(ret.notna().sum()),
                "start": str(ret.index.min().date()),
                "end": str(ret.index.max().date()),
            }
        )
        return ret, meta
    meta["error"] = "510300_daily_missing"
    return pd.Series(dtype="float32"), meta


def load_industry_etf_ret() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """AUM-weighted SW-L1 industry ETF daily returns + amount panel (amount in 千元)."""
    meta: dict = {"ok": False, "gaps": []}
    map_path = V2 / "etf/sw_l1_etf_map_pit_daily.parquet"
    adj_path = V2 / "etf/etf_daily_adj.parquet"
    if not map_path.exists():
        meta["gaps"].append("sw_l1_etf_map_pit_daily_missing")
        return pd.DataFrame(), pd.DataFrame(), meta
    if not adj_path.exists():
        meta["gaps"].append("etf_daily_adj_missing")
        return pd.DataFrame(), pd.DataFrame(), meta

    m = pd.read_parquet(
        map_path,
        columns=["sw_l1_code", "trade_date", "etf_ts_code", "aum_wan", "amount", "no_etf", "available_at"],
    )
    m["_td"] = _ymd_series(m["trade_date"])
    m = m.dropna(subset=["_td", "sw_l1_code", "etf_ts_code"])
    if "no_etf" in m.columns:
        m = m[m["no_etf"] != True]  # noqa: E712
    m = m[(m["_td"] >= LOOKBACK_START - pd.Timedelta(days=10)) & (m["_td"] <= PANEL_END)]
    codes = sorted(m["etf_ts_code"].dropna().unique().tolist())
    meta["n_etf"] = len(codes)
    meta["n_sw"] = int(m["sw_l1_code"].nunique())
    meta["map_path"] = str(map_path.relative_to(ROOT))

    adj = pd.read_parquet(
        adj_path,
        columns=["ts_code", "trade_date", "close_hfq", "pct_chg", "amount", "available_at"],
    )
    adj = adj[adj["ts_code"].isin(codes)].copy()
    adj["_td"] = _ymd_series(adj["trade_date"])
    adj = adj.dropna(subset=["_td"])
    adj = adj[(adj["_td"] >= LOOKBACK_START - pd.Timedelta(days=10)) & (adj["_td"] <= PANEL_END)]
    adj = adj.sort_values(["ts_code", "_td"])
    adj["ret"] = adj.groupby("ts_code", sort=False)["close_hfq"].pct_change()
    meta["adj_path"] = str(adj_path.relative_to(ROOT))
    meta["adj_rows"] = int(len(adj))

    j = m.merge(
        adj[["ts_code", "_td", "ret", "amount"]].rename(columns={"amount": "etf_amount_qian"}),
        left_on=["etf_ts_code", "_td"],
        right_on=["ts_code", "_td"],
        how="left",
    )
    j = j.dropna(subset=["ret", "sw_l1_code"])
    w = j["aum_wan"].fillna(0).clip(lower=0).to_numpy(dtype=np.float64)
    j["_w"] = np.where(w > 0, w, 1.0)
    num = (j["_w"] * j["ret"]).groupby([j["_td"], j["sw_l1_code"]], sort=False).sum()
    den = j.groupby(["_td", "sw_l1_code"], sort=False)["_w"].sum()
    ind_ret = (num / den).unstack("sw_l1_code").sort_index().astype("float32")
    amt_src = j["amount"] if "amount" in j.columns else j["etf_amount_qian"]
    if "etf_amount_qian" in j.columns:
        amt_src = amt_src.fillna(j["etf_amount_qian"]) if "amount" in j.columns else j["etf_amount_qian"]
    amt = (
        pd.DataFrame({"_td": j["_td"], "sw": j["sw_l1_code"], "a": amt_src.fillna(0)})
        .groupby(["_td", "sw"], sort=False)["a"]
        .sum()
        .unstack("sw")
        .reindex(index=ind_ret.index, columns=ind_ret.columns)
        .astype("float32")
    )
    ind_ret = ind_ret.loc[(ind_ret.index >= LOOKBACK_START) & (ind_ret.index <= PANEL_END)]
    amt = amt.reindex_like(ind_ret)
    meta.update(
        {
            "ok": True,
            "shape": list(ind_ret.shape),
            "nonempty_rate": float(np.isfinite(ind_ret.to_numpy()).mean()),
            "start": str(ind_ret.index.min().date()) if len(ind_ret) else None,
            "end": str(ind_ret.index.max().date()) if len(ind_ret) else None,
            "method": "aum_weighted_sw_l1_etf_close_hfq_pct_change",
            "amount_unit": "qian_yuan_tushare",
        }
    )
    return ind_ret, amt, meta


def _broadcast_series(ser: pd.Series, common_idx: pd.DatetimeIndex, base_cols: pd.Index) -> pd.DataFrame:
    s1 = ser.reindex(common_idx).astype("float32")
    return pd.DataFrame(
        np.repeat(s1.to_numpy().reshape(-1, 1), len(base_cols), axis=1),
        index=common_idx,
        columns=base_cols,
        dtype="float32",
    )


def load_flow_panels_pit_and_leak(
    base_cols: pd.Index,
    common_idx: pd.DatetimeIndex,
    sessions: pd.DatetimeIndex,
) -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame], dict]:
    """Feature panels: PIT asof (for GP/gates) + trade_date leak (diagnostic only).

    PIT rule: map available_at → first session strictly after available_at.date,
    place flow there, ffill so asof semantics hold for ts_* wraps.
    LEAK rule (v21 bug): pivot on trade_date same-day — report ICIR only, never gate.
    """
    panels_pit: dict[str, pd.DataFrame] = {}
    panels_leak: dict[str, pd.DataFrame] = {}
    meta: dict = {
        "wired_pit": [],
        "wired_leak": [],
        "gaps": [],
        "pit_rule": (
            "strict available_at ≤ decision_time(D); DECISION_CLOCK=open → D 09:00; "
            "NOT fixed lag1; Data available_at=max(份额下一交易日09:00,净值max(ann,trade)23:59); "
            "by_sw_l1 ~75% 23:59 / ~25% 09:00; 23:59→next open, 09:00→same open; ffill asof"
        ),
        "decision_clock": "open",
        "decision_time_def": "D 09:00 Asia/Shanghai (session open)",
        "leak_rule": "FORBIDDEN for gates: pivot on trade_date same-day (v21)",
        "asof_checks": {},
    }

    by_sw = V2 / "etf/share_pit/ind_etf_share_flow_by_sw_l1.parquet"
    if by_sw.exists():
        dfb = pd.read_parquet(by_sw)
        cols_l = {c.lower(): c for c in dfb.columns}
        td = cols_l.get("trade_date") or "trade_date"
        swc = cols_l.get("sw_l1_code") or cols_l.get("sw_code")
        flowc = None
        for cand in ("flow_est_wan_yuan", "d_share_wan", "share_flow", "flow"):
            if cand in dfb.columns:
                flowc = cand
                break
        aa_col = cols_l.get("available_at")
        if td and swc and flowc and aa_col:
            dfb = dfb.copy()
            dfb["_td"] = _ymd_series(dfb[td])
            dfb["_aa"] = pd.to_datetime(dfb[aa_col])
            dfb = dfb.dropna(subset=["_td", swc, "_aa"])
            # keep buffer so early lookback sessions get prior asof values
            dfb = dfb[
                (dfb["_td"] >= LOOKBACK_START - pd.Timedelta(days=40))
                & (dfb["_td"] <= PANEL_END)
            ]
            # --- LEAK (diagnostic) ---
            leak = (
                dfb[(dfb["_td"] >= LOOKBACK_START) & (dfb["_td"] <= PANEL_END)]
                .pivot_table(index="_td", columns=swc, values=flowc, aggfunc="sum")
                .sort_index()
            )
            leak = leak.reindex(index=common_idx, columns=base_cols).astype("float32")
            panels_leak["ind_etf_share_flow"] = leak
            meta["wired_leak"].append("ind_etf_share_flow")

            # --- PIT asof ---
            dfb["_usable"] = available_at_to_usable_session(dfb["_aa"], sessions)
            dfb = dfb.dropna(subset=["_usable"])
            pit_raw = (
                dfb.pivot_table(index="_usable", columns=swc, values=flowc, aggfunc="sum")
                .sort_index()
            )
            pit = pit_raw.reindex(index=common_idx, columns=base_cols).astype("float32")
            # asof: forward-fill last known published flow
            pit = pit.ffill().astype("float32")
            panels_pit["ind_etf_share_flow"] = pit
            meta["wired_pit"].append("ind_etf_share_flow")

            # Sanity: PIT vs LEAK should differ; lag check
            aa_dates = dfb["_aa"].dt.normalize()
            td_dates = dfb["_td"].dt.normalize()
            lag = (aa_dates - td_dates).dt.days
            meta["asof_checks"]["ind_etf_share_flow"] = {
                "path": str(by_sw.relative_to(ROOT)),
                "n_rows_used": int(len(dfb)),
                "pct_available_at_lag_ge_1": float((lag >= 1).mean()) if len(lag) else None,
                "pct_usable_gt_trade_date": float(
                    (dfb["_usable"] > dfb["_td"]).mean()
                )
                if len(dfb)
                else None,
                "pit_nonempty": float(np.isfinite(pit.to_numpy()).mean()),
                "leak_nonempty": float(np.isfinite(leak.to_numpy()).mean()),
                "pit_leak_abs_diff_mean": float(
                    np.nanmean(np.abs(pit.to_numpy() - leak.to_numpy()))
                ),
            }
            log(
                "PIT asof ind_etf_share_flow",
                "pit_ne",
                round(meta["asof_checks"]["ind_etf_share_flow"]["pit_nonempty"], 4),
                "leak_ne",
                round(meta["asof_checks"]["ind_etf_share_flow"]["leak_nonempty"], 4),
                "absdiff",
                round(meta["asof_checks"]["ind_etf_share_flow"]["pit_leak_abs_diff_mean"], 2),
            )
        else:
            meta["gaps"].append("ind_etf_share_flow:bad_schema_or_no_available_at")
    else:
        meta["gaps"].append("ind_etf_share_flow:missing")

    for name, path in (
        ("etf_share_chg_major", V2 / "etf/share_pit/etf_share_flow_pit_major.parquet"),
        ("etf_all_flow", V2 / "etf/share_pit/etf_share_flow_pit_all.parquet"),
        ("etf_share_chg_theme", V2 / "etf/share_pit/etf_share_flow_pit_industry_theme.parquet"),
    ):
        if mem_mb() > 2000:
            meta["gaps"].append(f"{name}:skipped_rss")
            break
        if not path.exists():
            meta["gaps"].append(f"{name}:missing")
            continue
        # Prefer columns-only read for heavy all-flow
        # schema probe then column-selective read (etf_all_flow is heavy)
        try:
            import pyarrow.parquet as pq
            schema_cols = [f.name for f in pq.ParquetFile(path).schema_arrow]
        except Exception:
            schema_cols = None
        prefer = ["trade_date", "available_at", "flow_est_wan_yuan", "d_share_wan", "share_chg", "d_share", "flow"]
        if schema_cols:
            cols_read = [c for c in prefer if c in schema_cols]
            raw = pd.read_parquet(path, columns=cols_read) if cols_read else pd.read_parquet(path)
        else:
            raw = pd.read_parquet(path)
        cols_l = {c.lower(): c for c in raw.columns}
        td = cols_l.get("trade_date") or "trade_date"
        aa_col = cols_l.get("available_at")
        flowc = None
        for cand in ("flow_est_wan_yuan", "d_share_wan", "share_chg", "d_share", "flow"):
            if cand in raw.columns:
                flowc = cand
                break
        if not flowc or not aa_col:
            meta["gaps"].append(f"{name}:no_flow_or_available_at")
            continue
        raw = raw.copy()
        raw["_td"] = _ymd_series(raw[td])
        raw["_aa"] = pd.to_datetime(raw[aa_col])
        raw = raw.dropna(subset=["_td", "_aa"])
        raw = raw[
            (raw["_td"] >= LOOKBACK_START - pd.Timedelta(days=40))
            & (raw["_td"] <= PANEL_END)
        ]

        # LEAK diagnostic: sum by trade_date
        leak_ser = (
            raw[(raw["_td"] >= LOOKBACK_START) & (raw["_td"] <= PANEL_END)]
            .groupby("_td")[flowc]
            .sum()
            .sort_index()
            .astype("float32")
        )
        panels_leak[name] = _broadcast_series(leak_ser, common_idx, base_cols)
        meta["wired_leak"].append(name)

        # PIT asof
        raw["_usable"] = available_at_to_usable_session(raw["_aa"], sessions)
        raw = raw.dropna(subset=["_usable"])
        pit_ser = raw.groupby("_usable")[flowc].sum().sort_index().astype("float32")
        pit_ser = pit_ser.reindex(common_idx).ffill().astype("float32")
        panels_pit[name] = _broadcast_series(pit_ser, common_idx, base_cols)
        meta["wired_pit"].append(name)
        meta["asof_checks"][name] = {
            "path": str(path.relative_to(ROOT)),
            "pit_nonempty": float(np.isfinite(panels_pit[name].to_numpy()).mean()),
            "leak_nonempty": float(np.isfinite(panels_leak[name].to_numpy()).mean()),
        }
        log("flow leaf PIT", name, panels_pit[name].shape)
        del raw
        gc.collect()

    return panels_pit, panels_leak, meta


def add_pit_price_leaves(
    panels: dict[str, pd.DataFrame],
    ind_ret: pd.DataFrame,
    excess: pd.DataFrame,
) -> list[str]:
    """Optional PIT-safe price features: lagged industry / excess returns."""
    added = []
    # Yesterday's industry return / excess — known at open of D
    panels["ind_ret_lag1"] = ind_ret.shift(1).astype("float32")
    panels["ind_excess_lag1"] = excess.shift(1).astype("float32")
    panels["ind_ret_ts_mean_5"] = ind_ret.shift(1).rolling(5, min_periods=3).mean().astype("float32")
    panels["ind_excess_ts_mean_5"] = (
        excess.shift(1).rolling(5, min_periods=3).mean().astype("float32")
    )
    added.extend(
        ["ind_ret_lag1", "ind_excess_lag1", "ind_ret_ts_mean_5", "ind_excess_ts_mean_5"]
    )
    return added


def icir_panel(fac: pd.DataFrame, lab: pd.DataFrame) -> float:
    ics = []
    n = min(len(fac), len(lab))
    for i in range(n):
        a = fac.iloc[i].to_numpy(dtype=np.float64)
        b = lab.iloc[i].to_numpy(dtype=np.float64)
        m = np.isfinite(a) & np.isfinite(b)
        if m.sum() < 5:
            continue
        aa, bb = a[m], b[m]
        if aa.std() < 1e-12 or bb.std() < 1e-12:
            continue
        ics.append(float(np.corrcoef(aa, bb)[0, 1]))
    if len(ics) < 10:
        return float("nan")
    mu = float(np.nanmean(ics))
    sd = float(np.nanstd(ics))
    return mu / sd * math.sqrt(252) if sd > 1e-12 else float("nan")


def after_cost_icir(fac: pd.DataFrame, lab: pd.DataFrame, cost: float = COST) -> float:
    lab_adj = lab - cost
    return icir_panel(fac, lab_adj)


def impact_gate(fac: pd.DataFrame, lab: pd.DataFrame, amt_qian: pd.DataFrame) -> dict:
    out = {}
    for cny in IMPACT_CNY:
        need_qian = cny / 1000.0
        liquid = amt_qian.reindex_like(fac) >= need_qian
        fac_l = fac.where(liquid)
        lab_l = lab.where(liquid)
        ic = icir_panel(fac_l, lab_l)
        if fac.size:
            m = liquid.to_numpy(dtype=bool) & np.isfinite(fac.to_numpy()) & np.isfinite(lab.to_numpy())
            cov = float(np.mean(m))
        else:
            cov = 0.0
        out[f"icir_impact_{int(cny)}"] = ic if isinstance(ic, float) else None
        out[f"liquid_cov_{int(cny)}"] = cov
        out[f"pass_impact_{int(cny)}"] = bool(
            isinstance(ic, float) and math.isfinite(ic) and ic > 0 and cov >= 0.05
        )
    out["pass_impact_60_and_100"] = bool(
        out.get("pass_impact_600000") and out.get("pass_impact_1000000")
    )
    return out


def banned_expr(es: str) -> str | None:
    Ls = leaves_in(es)
    for x in Ls:
        for s0 in CB_GOLD_BANNED_STEMS:
            if x == s0 or x.startswith(s0) or s0 in x:
                return "HARD_BAN_CB_GOLD"
        if x == "overnight_ret" or x.startswith("fsr") or x.startswith("ann_insider") or x.startswith("idx_w"):
            return "SYNTAX_HARD_BAN_STOCK_LEAF"
        for s0 in ("etf_share", "ind_etf_share", "etf_theme_flow", "etf_major_flow", "etf_all_flow", "share_flow", "share_chg"):
            if s0 in x:
                return "HARD_BAN_SHARE_FLOW_PAUSED"
    return None


def mk_expr(rng, leaf_names, wraps, ops_b):
    from quantlab.factors.ops import Expr as EB

    if len(leaf_names) < 1:
        return None
    if len(leaf_names) == 1 or rng.random() < 0.35:
        a = str(rng.choice(leaf_names))
        e = EB("leaf", a)
        e = EB("op", str(rng.choice(wraps)), (e,))
        if rng.random() < 0.4:
            e = EB("op", str(rng.choice(wraps)), (e,))
        return e
    a, b = [str(x) for x in rng.choice(leaf_names, size=2, replace=True)]
    op = str(rng.choice(ops_b, p=[0.3, 0.35, 0.2, 0.15]))
    ea = EB("op", str(rng.choice(wraps)), (EB("leaf", a),))
    eb = EB("op", str(rng.choice(wraps)), (EB("leaf", b),))
    root = EB("op", op, (ea, eb))
    if rng.random() < 0.35:
        root = EB("op", str(rng.choice(("ts_mean_10", "ts_mean_20", "neg", "abs"))), (root,))
    return root


def main() -> int:
    if os.environ.get("LEO_AI_FACTOR_EXPLORE_OK") != "1":
        print("REFUSE: set LEO_AI_FACTOR_EXPLORE_OK=1", flush=True)
        return 2

    OUT.mkdir(parents=True, exist_ok=True)
    avail0 = available_mb()
    os.environ["QL_V23B_AVAILABLE_AT_START_MB"] = str(avail0)
    log(
        "START v23 TrackB-only PRICE etf_timing_price",
        "pid",
        os.getpid(),
        "available_mb",
        round(avail0, 1),
        "MEM_CAP",
        MEM_CAP_MB,
        "SELF_STOP_RSS",
        SELF_STOP_RSS_STICKY_MB,
        "WINDOW",
        WINDOW,
        "SEED",
        SEED,
        "TrackA",
        "PAUSED",
        "promotion",
        PROMOTION_APPROVED,
        "pit_asof",
        "available_at≤decision_open_09:00",
    )
    (OUT / "startup_receipt.json").write_text(
        json.dumps(
            {
                "pid": os.getpid(),
                "available_mb": avail0,
                "sleeve": "etf_timing_price",
                "track": "B_only",
                "track_a": "paused",
                "window": WINDOW,
                "seed": SEED,
                "promotion_approved": False,
                "for_beta": True,
                "for_alpha_shortlist": False,
                "pit_asof_wired": True,
                "decision_clock": "open",
                "decision_time_def": "D 09:00 Asia/Shanghai",
                "pit_rule": "available_at ≤ decision_time(D=open 09:00); NOT fixed lag1; Data clocks 23:59|09:00; ffill asof",
                "aligned_data_newbot": True,
                "gate_metric": "PIT_ICIR_only",
                "leak_icir": "diagnostic_only_not_gate",
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    bm_ret, bm_meta = load_510300_ret()
    ind_ret, amt, ind_meta = load_industry_etf_ret()
    label_meta = {
        "benchmark": "510300.SH close pct_change",
        "benchmark_meta": bm_meta,
        "industry_ret_meta": ind_meta,
        "horizons": {
            "primary": "fwd_1d_excess_vs_510300",
            "secondary": "fwd_5d_excess_vs_510300",
        },
        "forbidden_label": "flow_continuation (v20) — NOT used",
        "v21_reject": "trade_date same-day share-flow leakage; PIT ICIR≈-0.10",
        "v22_fix": "share-flow via available_at PIT asof only",
    }
    (OUT / "label_definition.json").write_text(
        json.dumps(clean(label_meta), indent=2, ensure_ascii=False), encoding="utf-8"
    )

    if not bm_meta.get("ok") or not ind_meta.get("ok") or ind_ret.empty:
        gaps = []
        if not bm_meta.get("ok"):
            gaps.append("510300_return_series")
        if not ind_meta.get("ok"):
            gaps.extend(ind_meta.get("gaps") or ["industry_etf_return"])
        log("STOP_CLEAN B: return series gap", gaps)
        pkg = {
            "sleeve": "etf_timing_price",
            "for_beta": True,
            "for_alpha_shortlist_adjudication": False,
            "promotion_approved": False,
            "stopped_clean": True,
            "gaps_for_data": gaps,
            "label_meta": label_meta,
        }
        (OUT / "beta_etf_timing_price_package.json").write_text(
            json.dumps(clean(pkg), indent=2, ensure_ascii=False), encoding="utf-8"
        )
        (OUT / "BETA_NOTE_ZH.md").write_text(
            "# v22 ETF timing PIT（交 Beta）— 干净停\n\n"
            f"- 缺口：{gaps}\n"
            "- promotion_approved=false；不进 Alpha 短名单；不交 Strategy。\n",
            encoding="utf-8",
        )
        return 0

    bm = bm_ret.reindex(ind_ret.index)
    excess = ind_ret.sub(bm, axis=0).astype("float32")
    y1 = excess.shift(-1).astype("float32")
    y5 = sum(excess.shift(-i) for i in range(1, 6)).astype("float32")

    log(
        "labels ready",
        "ind",
        ind_ret.shape,
        "y1_finite",
        round(float(np.isfinite(y1.to_numpy()).mean()), 4),
        "rss",
        round(mem_mb()),
    )

    sessions = load_sessions()
    # keep sessions covering lookback buffer
    sessions = sessions[
        (sessions >= LOOKBACK_START - pd.Timedelta(days=60)) & (sessions <= PANEL_END + pd.Timedelta(days=5))
    ]
    log("sessions", len(sessions), str(sessions.min().date()), "→", str(sessions.max().date()))

    # v23: NO share-flow panels — price/vol leaves only
    panels: dict[str, pd.DataFrame] = {}
    panels_leak: dict[str, pd.DataFrame] = {}
    flow_meta = {"share_flow_paused": True, "wired_pit": [], "wired_leak": [], "note": "v23 TrackB price-only"}
    price_added = add_pit_price_leaves(panels, ind_ret, excess)
    # broaden price leaf set
    panels["ind_ret_lag5"] = ind_ret.shift(5).astype("float32")
    panels["ind_excess_lag5"] = excess.shift(5).astype("float32")
    panels["ind_ret_ts_std_10"] = ind_ret.shift(1).rolling(10, min_periods=5).std().astype("float32")
    panels["ind_excess_ts_std_10"] = excess.shift(1).rolling(10, min_periods=5).std().astype("float32")
    bm_lag1 = bm.shift(1).astype("float32")
    def _bcast(ser):
        s1 = ser.reindex(ind_ret.index).astype("float32")
        return pd.DataFrame(
            np.repeat(s1.to_numpy().reshape(-1, 1), ind_ret.shape[1], axis=1),
            index=ind_ret.index, columns=ind_ret.columns, dtype="float32",
        )
    panels["bm_ret_lag1"] = _bcast(bm_lag1)
    panels["bm_ret_ts_mean_5"] = _bcast(bm_lag1.rolling(5, min_periods=3).mean())
    panels["bm_ret_ts_std_10"] = _bcast(bm_lag1.rolling(10, min_periods=5).std())
    price_added = sorted(panels.keys())
    flow_meta["price_leaves_pit"] = price_added
    log("price leaves ONLY", price_added, "n", len(price_added))

    if not panels:
        log("STOP_CLEAN B: no price feature panels")
        (OUT / "beta_etf_timing_price_package.json").write_text(
            json.dumps(clean({"sleeve": "etf_timing_price", "stopped_clean": True,
                              "gaps_for_data": ["price_leaves_missing"], "for_beta": True,
                              "promotion_approved": False}), indent=2, ensure_ascii=False),
            encoding="utf-8")
        return 0

    (OUT / "pit_asof_meta.json").write_text(
        json.dumps(clean(flow_meta), indent=2, ensure_ascii=False), encoding="utf-8"
    )

    log(
        "gp_search start TrackB_PIT",
        "pid",
        os.getpid(),
        "available_mb",
        round(available_mb(), 1),
        "n_leaves",
        len(panels),
        "max_eval",
        MAX_EVAL,
        "label",
        "fwd_1d_excess_vs_510300",
        "gate",
        "PIT_ICIR_only",
        "pit_asof",
        "WIRED",
    )

    _ensure_pkgs()
    from quantlab.factors.ops import apply_expr as apply_b

    rng = np.random.default_rng(SEED)
    leaf_names = [k for k, v in panels.items() if v.notna().to_numpy().sum() > 100]
    wraps = ("ts_mean_5", "ts_mean_10", "ts_mean_20", "ts_std_10", "ts_delta_5", "ts_max_20", "neg", "abs")
    ops_b = ("mul", "sub", "div", "add")

    ledger = OUT / "ledger_track_b.jsonl"
    if ledger.exists():
        ledger.unlink()
    candidates = []
    fail_ctr: dict[str, int] = {}
    seen = set()
    n_eval = 0
    peak = mem_mb()
    dual_icir_rows = []

    while n_eval < MAX_EVAL:
        peak = max(peak, mem_mb())
        if mem_mb() > SELF_STOP_RSS_STICKY_MB or (
            math.isfinite(available_mb()) and available_mb() < SELF_STOP_AVAILABLE_MB
        ):
            log("SELF_STOP", "rss", round(mem_mb()), "avail", round(available_mb(), 1), "evals", n_eval)
            break
        expr = mk_expr(rng, leaf_names, wraps, ops_b)
        if expr is None:
            break
        es = expr.to_str()
        br = banned_expr(es)
        if br:
            fail_ctr[br] = fail_ctr.get(br, 0) + 1
            continue
        if es in seen:
            continue
        seen.add(es)
        n_eval += 1
        Ls = sorted(leaves_in(es))
        try:
            fac = apply_b(expr, panels).astype("float32")
        except Exception as ex:
            with open(ledger, "a", encoding="utf-8") as fh:
                fh.write(
                    json.dumps(
                        {"expr": es, "error": type(ex).__name__, "sleeve": "etf_timing_price"},
                        ensure_ascii=False,
                    )
                    + "\n"
                )
            fail_ctr["apply_error"] = fail_ctr.get("apply_error", 0) + 1
            continue

        # --- PIT metrics (GATE) ---
        icir1_pit = icir_panel(fac, y1)
        icir5_pit = icir_panel(fac, y5)
        icir1_ac_pit = after_cost_icir(fac, y1)
        imp = impact_gate(fac, y1, amt)
        nr = float(np.isfinite(fac.to_numpy()).mean()) if fac.size else 0.0

        # --- LEAK control (diagnostic only; rebuild expr on trade_date panels) ---
        icir1_leak = float("nan")
        try:
            # Only flow leaves exist in leak map; price leaves are already PIT — use panels for those
            leak_map = dict(panels)  # start from PIT (price leaves identical)
            for k, v in panels_leak.items():
                leak_map[k] = v
            fac_leak = apply_b(expr, leak_map).astype("float32")
            icir1_leak = icir_panel(fac_leak, y1)
            del fac_leak
        except Exception:
            icir1_leak = float("nan")

        gate_ok = (
            isinstance(icir1_pit, float)
            and math.isfinite(icir1_pit)
            and icir1_pit > 0
            and isinstance(icir1_ac_pit, float)
            and math.isfinite(icir1_ac_pit)
            and icir1_ac_pit > 0
            and bool(imp.get("pass_impact_60_and_100"))
            and nr >= 0.08
        )
        reason = None
        if not (isinstance(icir1_pit, float) and math.isfinite(icir1_pit) and icir1_pit > 0):
            reason = "PIT_ICIR1_LE_0"
        elif not (isinstance(icir1_ac_pit, float) and math.isfinite(icir1_ac_pit) and icir1_ac_pit > 0):
            reason = "PIT_AFTER_COST_ICIR_LE_0"
        elif not imp.get("pass_impact_60_and_100"):
            reason = "IMPACT_60_OR_100_FAIL"
        elif nr < 0.08:
            reason = "COVERAGE_THIN"

        row = {
            "expr": es,
            "leaves": Ls,
            "icir_pit_fwd1d_excess_510300": icir1_pit if isinstance(icir1_pit, float) else None,
            "icir_pit_fwd5d_excess_510300": icir5_pit if isinstance(icir5_pit, float) else None,
            "icir_pit_fwd1d_after_cost": icir1_ac_pit if isinstance(icir1_ac_pit, float) else None,
            "icir_leak_fwd1d_excess_510300": icir1_leak if isinstance(icir1_leak, float) else None,
            "icir_leak_is_diagnostic_only": True,
            "nonempty_rate": nr,
            "impact": imp,
            "gate_ok": gate_ok,
            "fail_reason": reason,
            "sleeve": "etf_timing_price",
            "label_primary": "fwd_1d_excess_vs_510300",
            "label_secondary": "fwd_5d_excess_vs_510300",
            "for_alpha_shortlist": False,
            "for_beta": True,
            "promotion_approved": False,
            "note": (
                "TrackB ETF timing PRICE; y=industry ETF fwd excess vs 510300; "
                "X=price/vol lags only (share-flow PAUSED); GATE=PIT ICIR only"
            ),
        }
        dual_icir_rows.append(
            {
                "expr": es,
                "icir_pit": row["icir_pit_fwd1d_excess_510300"],
                "icir_leak": row["icir_leak_fwd1d_excess_510300"],
                "gate_ok": gate_ok,
            }
        )
        with open(ledger, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(clean(row), ensure_ascii=False) + "\n")
        if gate_ok:
            candidates.append(row)
        else:
            fail_ctr[reason or "FAIL"] = fail_ctr.get(reason or "FAIL", 0) + 1
        del fac
        if n_eval % 20 == 0:
            gc.collect()
            peak = max(peak, mem_mb())
            log(
                "progress",
                n_eval,
                "/",
                MAX_EVAL,
                "pass",
                len(candidates),
                "rss",
                round(mem_mb()),
                "avail",
                round(available_mb(), 1),
            )

    candidates.sort(
        key=lambda r: (r.get("icir_pit_fwd1d_excess_510300") or -1e9),
        reverse=True,
    )
    peak = max(peak, mem_mb())
    log("DONE", "evals", n_eval, "n_pass", len(candidates), "peak", round(peak))

    # Dual ICIR summary
    pit_vals = [r["icir_pit"] for r in dual_icir_rows if isinstance(r.get("icir_pit"), float) and math.isfinite(r["icir_pit"])]
    leak_vals = [
        r["icir_leak"]
        for r in dual_icir_rows
        if isinstance(r.get("icir_leak"), float) and math.isfinite(r["icir_leak"])
    ]
    dual_summary = {
        "n_eval": n_eval,
        "n_pass_pit_gates": len(candidates),
        "icir_pit_median": float(np.median(pit_vals)) if pit_vals else None,
        "icir_pit_mean": float(np.mean(pit_vals)) if pit_vals else None,
        "icir_pit_max": float(np.max(pit_vals)) if pit_vals else None,
        "icir_leak_median": float(np.median(leak_vals)) if leak_vals else None,
        "icir_leak_mean": float(np.mean(leak_vals)) if leak_vals else None,
        "icir_leak_max": float(np.max(leak_vals)) if leak_vals else None,
        "note": "GATE uses PIT only; leak is trade_date-aligned diagnostic (v21 bug mode)",
    }
    (OUT / "dual_icir_summary.json").write_text(
        json.dumps(clean(dual_summary), indent=2, ensure_ascii=False), encoding="utf-8"
    )

    top_fail = sorted(fail_ctr.items(), key=lambda kv: -kv[1])[:8]
    beta_pkg = {
        "sleeve": "etf_timing_price",
        "for_alpha_shortlist_adjudication": False,
        "for_beta": True,
        "promotion_approved": False,
        "not_strategy_weights": True,
        "sealed": False,
        "pid": os.getpid(),
        "peak_rss_MB": round(peak),
        "available_at_start_MB": avail0,
        "n_evaluations": int(n_eval),
        "n_candidates_pass": len(candidates),
        "candidates": candidates[:25],
        "etf_leaves_wired_pit": sorted(panels.keys()),
        "etf_leaves_wired_leak_diagnostic": sorted(panels_leak.keys()),
        "flow_meta": flow_meta,
        "dual_icir_summary": dual_summary,
        "pit_asof_rule": flow_meta.get("pit_rule"),
        "label": {
            "primary": "fwd_1d_aum_weighted_sw_l1_etf_excess_return_vs_510300",
            "secondary": "fwd_5d_sum_excess_vs_510300",
            "NOT": "flow_continuation",
            "benchmark": "510300.SH",
            "industry_method": ind_meta.get("method"),
            "sources": {
                "industry_map": ind_meta.get("map_path"),
                "etf_adj": ind_meta.get("adj_path"),
                "benchmark": bm_meta.get("path"),
            },
        },
        "gates": {
            "metric": "PIT_ICIR_only",
            "icir_pit_fwd1d_gt_0": True,
            "after_cost_pit_icir_gt_0": True,
            "cost": COST,
            "impact_cny": list(IMPACT_CNY),
            "impact_note": (
                "amount in 千元 (tushare); liquid if amount>=notional/1000; "
                "require PIT ICIR>0 on liquid subset for BOTH 60万 and 100万"
            ),
            "ban_cb_gold": True,
            "leak_icir_not_a_gate": True,
        },
        "fail_reason_top": [{"reason": a, "n": b} for a, b in top_fail],
        "window": WINDOW,
        "seed": SEED,
        "lookback": str(LOOKBACK_START.date()),
        "panel_end": str(PANEL_END.date()),
        "explore_start": str(EXPLORE_START.date()),
        "mem_cap_MB": MEM_CAP_MB,
        "self_stop_rss_sticky_MB": SELF_STOP_RSS_STICKY_MB,
        "track_a": "paused",
        "v21_reject_addressed": "share-flow now available_at PIT asof; dual ICIR reported",
        "note": "Hand QuantLab Beta only; do NOT submit to Alpha shortlist; promotion_approved=false; no Strategy",
        "out_dir": str(OUT.relative_to(ROOT)),
    }
    (OUT / "beta_etf_timing_price_package.json").write_text(
        json.dumps(clean(beta_pkg), indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUT / "candidates.json").write_text(
        json.dumps(clean(candidates), indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUT / "receipt.json").write_text(
        json.dumps(
            clean(
                {
                    "track": "B_etf_timing_price",
                    "sleeve": "etf_timing_price",
                    "pid": os.getpid(),
                    "peak_rss_MB": round(peak),
                    "available_at_start_MB": avail0,
                    "n_evaluations": int(n_eval),
                    "n_pass": len(candidates),
                    "etf_leaves_pit": sorted(panels.keys()),
                    "label_primary": "fwd_1d_excess_vs_510300",
                    "gate_metric": "PIT_ICIR_only",
                    "pit_asof_wired": True,
                    "for_alpha": False,
                    "for_beta": True,
                    "promotion_approved": False,
                    "under_mem_cap": peak <= MEM_CAP_MB,
                    "dual_icir_summary": dual_summary,
                }
            ),
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    lines = [
        "# v22 Track B — ETF timing PIT asof（交 Beta，不进 Alpha 短名单）",
        "",
        f"- sleeve=`etf_timing_price`；evals={n_eval}；**GATE_OK(PIT)={len(candidates)}**；peak≈{round(peak)}MB；available@start≈{round(avail0,1)}MB",
        f"- 叶子（X，PIT）：{sorted(panels.keys())}",
        "- **PIT asof 规则（强制）**：严格 `available_at ≤ 决策时刻`；决策时刻默认 **当日开盘 D 09:00**（`DECISION_CLOCK=open`）。",
        "  Data 口径：`available_at = max(份额下一交易日09:00, 净值max(ann,trade)23:59)`；by_sw_l1 ≈75% 为 23:59、≈25% 为 09:00，**非恒 td+1**。",
        "  → 23:59 发布：下一交易日开盘才可用；09:00 发布：当日开盘可用（≤09:00）。**禁止**固定 lag1 / 一律按 09:00 简化。",
        "  **禁止** trade_date 当日聚合进信号（v21 泄漏根因）；随后 ffill 做 asof。",
        "- **标签 y（非 flow）**：申万一级行业 ETF（AUM 加权）相对 **510300** 的未来 1 日超额（主闸）/ 5 日超额和（副报）",
        "- **硬闸只认 PIT ICIR**：ICIR_pit(1d)>0；成本后 PIT ICIR>0（25bp）；冲击@60万∧100万；禁 CB/金",
        "- **泄漏对照字段**（`icir_leak_*`，trade_date 对齐）**仅为诊断，不过闸**",
        f"- 双 ICIR 摘要：PIT median={dual_summary.get('icir_pit_median')} max={dual_summary.get('icir_pit_max')}；"
        f"LEAK median={dual_summary.get('icir_leak_median')} max={dual_summary.get('icir_leak_max')}",
        "- **不交 Alpha 短名单**；Track A 暂停；promotion_approved=false；不交 Strategy；未开密封",
        f"- 包：`{OUT.relative_to(ROOT)}/beta_etf_timing_price_package.json`",
        f"- asof meta：`{OUT.relative_to(ROOT)}/pit_asof_meta.json`",
        "",
        "| # | 表达式 | ICIR_PIT_1d | after_cost_PIT | ICIR_LEAK_1d(诊断) | ICIR_PIT_5d | impact60∧100 | nonempty |",
        "|---|---|---:|---:|---:|---:|:---:|---:|",
    ]
    for i, r in enumerate(candidates[:15], 1):
        lines.append(
            f"| {i} | `{r['expr']}` | {r.get('icir_pit_fwd1d_excess_510300')} | {r.get('icir_pit_fwd1d_after_cost')} | "
            f"{r.get('icir_leak_fwd1d_excess_510300')} | {r.get('icir_pit_fwd5d_excess_510300')} | "
            f"{r.get('impact', {}).get('pass_impact_60_and_100')} | {r.get('nonempty_rate')} |"
        )
    if not candidates:
        lines.append("| — | （本轮无过 PIT 硬闸） | — | — | — | — | — | — |")
    lines += ["", f"- fail_top: {top_fail}", ""]
    (OUT / "BETA_NOTE_ZH.md").write_text("\n".join(lines), encoding="utf-8")
    REPORT_NOTE.write_text("\n".join(lines), encoding="utf-8")

    summary = {
        "promotion_approved": False,
        "sealed": False,
        "strategy_weights": False,
        "track_a": "paused",
        "sleeve": "etf_timing_price",
        "pid": os.getpid(),
        "peak_rss_MB": round(peak),
        "available_at_start_MB": avail0,
        "n_evaluations": int(n_eval),
        "n_pass": len(candidates),
        "under_mem_cap": peak <= MEM_CAP_MB,
        "pit_asof_wired": True,
        "gate_metric": "PIT_ICIR_only",
        "dual_icir_summary": dual_summary,
        "label_primary": "fwd_1d_excess_vs_510300",
        "out_dir": str(OUT.relative_to(ROOT)),
        "beta_package": str((OUT / "beta_etf_timing_price_package.json").relative_to(ROOT)),
        "top_exprs": [r["expr"] for r in candidates[:5]],
        "fail_reason_top": [{"reason": a, "n": b} for a, b in top_fail],
    }
    (OUT / "summary.json").write_text(json.dumps(clean(summary), indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))
    return 0 if peak <= MEM_CAP_MB else 1


if __name__ == "__main__":
    raise SystemExit(main())
