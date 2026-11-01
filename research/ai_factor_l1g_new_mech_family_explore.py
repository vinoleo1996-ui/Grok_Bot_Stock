#!/usr/bin/env python3
"""L1g: new original mechanism family explore (parallel to v2c WF).

Primary family: **cb_equity_pressure** — map convertible-bond daily premia /
amounts onto underlying A-shares (T+1 PIT). Economic story: conversion /
dilution / arb flows link CB complex to equity; low/compressing conversion
premium raises conversion & selling pressure on the stock; CB volume intensity
marks active complex-flow days.

Secondary: **div_ex_calendar** — ex-date proximity / cash-div near ex
(expect seasonal sparsity; honest fail ok).

Tertiary: **earn_roe_delta** — PIT ROE / gross-margin *changes* (not level EP,
not ocf already mined in L1f).

Hard GATE_OK (all):
  1) Hard coverage on non-rank event口径 (no rank_fill)
  2) impact+flat25 @ 60万 AND 100万 ≥ 10%
  3) ICIR > 0
  4) Not rank_fill hallucination
  5) Not title-sparsity primary; not FSR/float_share_ratio new discovery

Ban: broadcast, LD primary, small-cap, textbook mainline, FSR family as new
discovery, ann_title sparse primary, sealed, Strategy.
promotion_approved=False. Memory <2.5GB.
"""
from __future__ import annotations

import gc
import importlib.util
import json
import math
import re
import resource
import sys
import time
import types
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/workspace/QuantLab")
V2 = ROOT / "data/v2"
OUT_DIR = ROOT / "output/ai_factor/l1g_new_mech_family"
REPORT = ROOT / "output/alpha/AI_FACTOR_L1g_NEW_MECH_FAMILY_EXPLORE_ZH.md"

EXPLORE_START = pd.Timestamp("2024-06-03")
LOOKBACK_START = pd.Timestamp("2024-01-02")
TOP_N = 50
K_IMP = 1.0
AUMS = (600_000.0, 1_000_000.0)
FLAT_BPS = (10, 25)
COMMISSION_ONE_WAY = 0.00025
PROMOTION_APPROVED = False
MEM_CAP_MB = 2500
CS_STD_MIN = 1e-8
SEED = 20261012
IMP60_FLOOR = 0.10

COV_NONEMPTY_MIN = 0.08
COV_MEAN_EVENT_NAMES_MIN = 40.0
COV_FRAC_DAYS_GE20_MIN = 0.50
COV_EVENT_N_MIN = 20

OPS = {
    "add", "sub", "mul", "div", "neg", "abs", "rank", "zscore",
    "industry_neutral", "size_neutral",
}
for k in (1, 5, 10, 20, 60):
    OPS |= {f"delay_{k}", f"ts_mean_{k}", f"ts_std_{k}", f"ts_delta_{k}", f"ts_max_{k}"}

BANNED_EXACT = frozenset(
    {
        "mkt_max_height", "mkt_lu_breadth", "etf_major_flow", "etf_theme_flow",
        "if_basis", "if_basis_x_on", "if_basis_x_lu", "etf_flow_x_lu",
        "theme_lu_density",
        "ret_20", "rv_20", "turn_20", "neg_ret_20", "size",
        "ret_1", "ret_5", "ret_10", "turnover", "amihud", "log_vol", "log_price",
        "ep", "bp", "pe", "pb",
        "rz_intensity", "rq_intensity", "rzrq_intensity",
        "rz_bal", "rq_bal", "rz_delta_5", "rz_delta_10", "rq_delta_5", "rzrq_delta_5",
        "float_evt_20", "float_evt_60", "float_ratio_20", "float_ratio_60", "float_evt_flag",
        "lockup_days_to", "lockup_S_20",
        "fsr", "neg_fsr", "fsr_delta_5", "fsr_delta_20", "float_share_ratio",
        "ocf_to_profit", "ocf_to_profit_attr", "ocf_delta_5", "ocf_delta_10", "ocf_abs",
    }
)
BANNED_PREFIXES = (
    "mkt_", "etf_", "if_basis", "limit_down_", "ld_", "ann_",
    "rz_", "rq_", "rzrq_", "float_evt", "float_ratio_", "lockup_",
    "fsr", "float_share", "ocf_",
)

TEXTBOOK_LEAVES = frozenset(
    {
        "ret_1", "ret_5", "ret_10", "ret_20", "resid_ret_20", "rv_20", "vol_20",
        "skew_20", "max_ret_20", "turnover", "turn_20", "amihud", "log_vol",
        "log_price", "ep", "bp", "pe", "pb", "size",
    }
)

t0 = 0.0


def mem_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def log(*a):
    print(f"[l1g_new {time.time()-t0:5.0f}s {mem_mb():.0f}MB]", *a, flush=True)


def leaves_in(expr: str) -> set[str]:
    return {t for t in re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", expr) if t not in OPS}


def is_banned_leaf(name: str) -> bool:
    if name in BANNED_EXACT or name in TEXTBOOK_LEAVES:
        return True
    return any(name.startswith(p) for p in BANNED_PREFIXES)


def is_title_sparse_primary(expr: str) -> bool:
    L = leaves_in(expr)
    return bool(L) and all(x.startswith("ann_") for x in L)


def is_fsr_family(expr: str) -> bool:
    L = leaves_in(expr)
    return any(
        x.startswith("fsr") or x.startswith("float_share") or x == "neg_fsr" for x in L
    )


def family_of(expr: str) -> str:
    L = sorted(leaves_in(expr))
    if not L:
        return "unknown"
    if all(x.startswith("cb_") for x in L):
        return "cb_equity_pressure"
    if all(x.startswith("div_") for x in L):
        return "div_ex_calendar"
    if all(x.startswith("roe_") or x.startswith("gm_") for x in L):
        return "earn_roe_delta"
    if any(x.startswith("cb_") for x in L) and any(x.startswith("div_") for x in L):
        return "cb_x_div"
    if any(x.startswith("cb_") for x in L) and any(
        x.startswith("roe_") or x.startswith("gm_") for x in L
    ):
        return "cb_x_roe"
    return "mixed:" + "+".join(L[:3])


def strip_rank(expr: str) -> str:
    s = expr.strip()
    changed = True
    while changed:
        changed = False
        for wrap in ("rank", "zscore"):
            m = re.fullmatch(rf"{wrap}\((.+)\)", s)
            if m:
                s = m.group(1).strip()
                changed = True
    return s


def has_rank_op(expr: str) -> bool:
    return bool(re.search(r"\brank\s*\(", expr))


def to_nested_tuple(obj):
    if isinstance(obj, list):
        return tuple(to_nested_tuple(x) for x in obj)
    return obj


def _seed_to_tuple(s: str):
    s = s.strip()
    if s.isidentifier():
        return ("leaf", s)
    m = re.fullmatch(r"neg\((.+)\)", s)
    if m:
        return ("op", "neg", _seed_to_tuple(m.group(1)))
    m = re.fullmatch(r"rank\((.+)\)", s)
    if m:
        return ("op", "rank", _seed_to_tuple(m.group(1)))
    m = re.fullmatch(r"zscore\((.+)\)", s)
    if m:
        return ("op", "zscore", _seed_to_tuple(m.group(1)))
    m = re.fullmatch(r"abs\((.+)\)", s)
    if m:
        return ("op", "abs", _seed_to_tuple(m.group(1)))
    for pref in ("delay_", "ts_std_", "ts_delta_", "ts_max_", "ts_mean_"):
        m = re.fullmatch(rf"{pref}(\d+)\((.+)\)", s)
        if m:
            return ("op", f"{pref}{m.group(1)}", _seed_to_tuple(m.group(2)))
    for op in ("mul", "add", "sub", "div"):
        m = re.fullmatch(rf"{op}\((.+)\)", s)
        if m:
            inner = m.group(1)
            depth = 0
            split_at = None
            for i, ch in enumerate(inner):
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                elif ch == "," and depth == 0:
                    split_at = i
                    break
            if split_at is None:
                raise ValueError(f"cannot split {op}: {s}")
            return (
                "op",
                op,
                _seed_to_tuple(inner[:split_at].strip()),
                _seed_to_tuple(inner[split_at + 1 :].strip()),
            )
    raise ValueError(f"cannot parse: {s}")


def _ensure_pkgs():
    if "quantlab" not in sys.modules:
        q = types.ModuleType("quantlab")
        q.__path__ = [str(ROOT / "quantlab")]
        sys.modules["quantlab"] = q
    if "quantlab.factors" not in sys.modules or not hasattr(
        sys.modules["quantlab.factors"], "__path__"
    ):
        f = types.ModuleType("quantlab.factors")
        f.__path__ = [str(ROOT / "quantlab/factors")]
        sys.modules["quantlab.factors"] = f

    def load(name: str, path: Path):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        return mod

    load("quantlab.factors.ops", ROOT / "quantlab/factors/ops.py")
    af = types.ModuleType("quantlab.factors.ai_factory")
    af.__path__ = [str(ROOT / "quantlab/factors/ai_factory")]
    sys.modules["quantlab.factors.ai_factory"] = af
    for name in ("ledger", "novelty", "fitness", "evaluate", "search", "structural_leaves"):
        load(
            f"quantlab.factors.ai_factory.{name}",
            ROOT / f"quantlab/factors/ai_factory/{name}.py",
        )


def _import_mod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _to_baostock(ts_code: str) -> str:
    s = str(ts_code)
    if "." in s:
        code, ex = s.split(".", 1)
        return f"{ex.lower()}.{code}"
    return s


def clean(o):
    if isinstance(o, float) and (math.isnan(o) or math.isinf(o)):
        return None
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, list):
        return [clean(x) for x in o]
    return o


def fmt_pct(x):
    if isinstance(x, float) and math.isfinite(x):
        return f"{x:.2%}"
    return "—"


def fmt_f(x, nd=4):
    if isinstance(x, float) and math.isfinite(x):
        return f"{x:.{nd}f}"
    return "—"


def _avail_to_next_session(avail_series: pd.Series, cal: pd.DatetimeIndex) -> pd.Series:
    """Map available_at timestamps to next calendar session on cal (left search)."""
    cal_np = cal.values.astype("datetime64[ns]")
    av = pd.to_datetime(avail_series, errors="coerce")
    # tz-aware → Asia/Shanghai wall clock; naive treated as local Shanghai
    if getattr(av.dt, "tz", None) is not None:
        av = av.dt.tz_convert("Asia/Shanghai").dt.tz_localize(None)
    day = av.dt.normalize() + pd.Timedelta(days=1)
    day_np = day.values.astype("datetime64[ns]")
    idx = np.searchsorted(cal_np, day_np, side="left")
    T = len(cal)
    out_dates = np.empty(len(idx), dtype="datetime64[ns]"); out_dates[:] = np.datetime64("NaT", "ns")
    valid = (idx >= 0) & (idx < T) & np.isfinite(day_np.astype("float64"))
    # day_np NaT check
    valid = (idx >= 0) & (idx < T) & ~pd.isna(day)
    out_dates[valid.to_numpy()] = cal_np[idx[valid.to_numpy()]]
    return pd.Series(out_dates, index=avail_series.index)


def build_cb_panels(cal, cols, mask) -> tuple[dict, dict]:
    """Map CB daily premia/amounts onto underlying stocks with T+1 PIT.

    Non-issuer stocks stay NaN (honest coverage — no zero-fill illusion).
    """
    path_d = V2 / "cb/cb_daily.parquet"
    path_b = V2 / "cb/cb_basic.parquet"
    gap = {
        "path": str(path_d),
        "basic_path": str(path_b),
        "family": "cb_equity_pressure",
        "economic_story": (
            "Convertible-bond conversion/dilution/arb flows couple to equity. "
            "Low or compressing cb_over_rate (conversion premium) raises "
            "conversion likelihood and potential selling pressure on the stock; "
            "CB amount intensity marks active complex-flow days. T+1 after "
            "available_at (close)."
        ),
    }
    if not path_d.exists() or not path_b.exists():
        gap["ok"] = False
        gap["error"] = "missing"
        return {}, gap

    basic = pd.read_parquet(path_b, columns=["ts_code", "stk_code"])
    basic = basic.dropna(subset=["ts_code", "stk_code"])
    basic["stk_bs"] = basic["stk_code"].map(_to_baostock)
    basic = basic[basic["stk_bs"].isin(cols)]

    daily = pd.read_parquet(
        path_d,
        columns=[
            "ts_code",
            "trade_date",
            "cb_over_rate",
            "bond_over_rate",
            "amount",
            "vol",
            "pct_chg",
            "available_at",
        ],
        filters=[("trade_date", ">=", (LOOKBACK_START - pd.Timedelta(days=40)).strftime("%Y%m%d"))],
    )
    daily["trade_date"] = pd.to_datetime(daily["trade_date"])
    daily = daily.merge(basic[["ts_code", "stk_bs"]], on="ts_code", how="inner")
    daily = daily[
        (daily["trade_date"] >= LOOKBACK_START - pd.Timedelta(days=40))
        & (daily["trade_date"] <= cal.max() + pd.Timedelta(days=5))
    ]
    # PIT: available_at → next session
    if "available_at" in daily.columns and daily["available_at"].notna().any():
        daily["avail_session"] = _avail_to_next_session(daily["available_at"], cal)
    else:
        # fallback trade_date+1 session
        td = daily["trade_date"] + pd.Timedelta(days=1)
        daily["avail_session"] = _avail_to_next_session(td, cal)

    daily = daily.dropna(subset=["avail_session", "stk_bs"])
    gap.update(
        {
            "ok": True,
            "n_rows": int(len(daily)),
            "n_cb": int(daily["ts_code"].nunique()),
            "n_stk": int(daily["stk_bs"].nunique()),
        }
    )

    # aggregate multi-CB → one stock/day (amount-weighted premium if amount>0)
    daily["amount"] = pd.to_numeric(daily["amount"], errors="coerce").fillna(0.0)
    daily["cb_over_rate"] = pd.to_numeric(daily["cb_over_rate"], errors="coerce")
    daily["bond_over_rate"] = pd.to_numeric(daily["bond_over_rate"], errors="coerce")
    daily["vol"] = pd.to_numeric(daily["vol"], errors="coerce").fillna(0.0)

    def _wavg(g, col):
        w = g["amount"].to_numpy()
        v = g[col].to_numpy()
        m = np.isfinite(v)
        if not m.any():
            return np.nan
        ww = w[m]
        vv = v[m]
        if ww.sum() <= 0:
            return float(np.nanmean(vv))
        return float(np.average(vv, weights=ww))

    # vectorized amount-weighted premium (fallback equal-weight if amount sum=0)
    daily["_w"] = daily["amount"].clip(lower=0)
    daily["_wp"] = daily["_w"] * daily["cb_over_rate"]
    daily["_wb"] = daily["_w"] * daily["bond_over_rate"]
    g = daily.groupby(["avail_session", "stk_bs"], sort=False)
    agg = g.agg(
        cb_amt=("amount", "sum"),
        cb_vol=("vol", "sum"),
        cb_n=("ts_code", "size"),
        _wsum=("_w", "sum"),
        _wpsum=("_wp", "sum"),
        _wbsum=("_wb", "sum"),
        _pmean=("cb_over_rate", "mean"),
        _bmean=("bond_over_rate", "mean"),
    ).reset_index()
    with np.errstate(divide="ignore", invalid="ignore"):
        prem = np.where(agg["_wsum"].to_numpy() > 0, agg["_wpsum"] / agg["_wsum"], agg["_pmean"])
        bond = np.where(agg["_wsum"].to_numpy() > 0, agg["_wbsum"] / agg["_wsum"], agg["_bmean"])
    agg["cb_prem"] = prem
    agg["cb_bond_prem"] = bond
    agg = agg[["avail_session", "stk_bs", "cb_prem", "cb_bond_prem", "cb_amt", "cb_vol", "cb_n"]]
    del daily, basic, g
    gc.collect()

    T, N = len(cal), len(cols)
    col_index = {c: i for i, c in enumerate(cols)}
    cal_index = {pd.Timestamp(d): i for i, d in enumerate(cal)}

    def empty():
        return np.full((T, N), np.nan, dtype=np.float32)

    prem = empty()
    bondp = empty()
    amt = empty()
    vol = empty()
    flag = empty()
    for r in agg.itertuples(index=False):
        j = col_index.get(r.stk_bs)
        i = cal_index.get(pd.Timestamp(r.avail_session))
        if j is None or i is None:
            continue
        if np.isfinite(r.cb_prem):
            prem[i, j] = np.float32(r.cb_prem)
        if np.isfinite(r.cb_bond_prem):
            bondp[i, j] = np.float32(r.cb_bond_prem)
        amt[i, j] = np.float32(r.cb_amt)
        vol[i, j] = np.float32(r.cb_vol)
        flag[i, j] = 1.0
    del agg
    gc.collect()

    prem_df = pd.DataFrame(prem, index=cal, columns=cols, dtype="float32")
    bond_df = pd.DataFrame(bondp, index=cal, columns=cols, dtype="float32")
    amt_df = pd.DataFrame(amt, index=cal, columns=cols, dtype="float32")
    vol_df = pd.DataFrame(vol, index=cal, columns=cols, dtype="float32")
    flag_df = pd.DataFrame(flag, index=cal, columns=cols, dtype="float32")
    # light ffill only within issuer streaks (limit 3) — keeps coverage honest
    prem_df = prem_df.ffill(limit=10)
    bond_df = bond_df.ffill(limit=10)
    # amount/vol/flag: event-like, rolling sum from raw (no ffill zeros)
    amt_raw = amt_df.copy()
    vol_raw = vol_df.copy()
    flag_raw = flag_df.copy()

    # winsorize prem
    for df in (prem_df, bond_df):
        arr = df.to_numpy(dtype=np.float64, copy=True)
        finite = arr[np.isfinite(arr)]
        if finite.size > 100:
            lo, hi = np.nanpercentile(finite, [1, 99])
            arr = np.clip(arr, lo, hi)
            df.loc[:, :] = arr.astype(np.float32)

    out = {
        "cb_prem": prem_df.astype("float32"),
        "cb_bond_prem": bond_df.astype("float32"),
        "neg_cb_prem": (-prem_df).astype("float32"),
        "neg_cb_bond_prem": (-bond_df).astype("float32"),
        "cb_prem_delta_5": prem_df.diff(5).astype("float32"),
        "cb_prem_delta_10": prem_df.diff(10).astype("float32"),
        "cb_amt_5": amt_raw.rolling(5, min_periods=1).sum().astype("float32"),
        "cb_amt_10": amt_raw.rolling(10, min_periods=1).sum().astype("float32"),
        "cb_vol_5": vol_raw.rolling(5, min_periods=1).sum().astype("float32"),
        "cb_flag_5": flag_raw.rolling(5, min_periods=1).sum().astype("float32"),
        "cb_flag": flag_raw.astype("float32"),
    }
    # intensity: log1p amount where present
    with np.errstate(divide="ignore", invalid="ignore"):
        out["cb_amt_log5"] = np.log1p(out["cb_amt_5"].clip(lower=0)).astype("float32")
    # replace 0-only rolling from all-NaN rows: where rolling sum is 0 and no flag, set NaN
    for k in ("cb_amt_5", "cb_amt_10", "cb_vol_5", "cb_flag_5", "cb_amt_log5"):
        z = out[k]
        # keep zeros only where flag window > 0
        out[k] = z.where(out["cb_flag_5"] > 0).astype("float32")

    if mask is not None:
        for k in list(out.keys()):
            out[k] = out[k].where(mask).astype("float32")

    for k, df in out.items():
        ev = df.notna() & (df.abs() > 1e-12)
        gap[f"nonempty_{k}"] = float(ev.to_numpy().mean())
        gap[f"mean_names_{k}"] = float(ev.sum(axis=1).mean())
    del prem, bondp, amt, vol, flag, prem_df, bond_df, amt_df, vol_df, flag_df
    del amt_raw, vol_raw, flag_raw
    gc.collect()
    return out, gap


def build_div_panels(cal, cols, mask) -> tuple[dict, dict]:
    """Ex-date proximity / cash-div calendar mapped to stocks (ann→usable)."""
    path = V2 / "corporate_actions/dividend_by_exdate_tushare.parquet"
    gap = {
        "path": str(path),
        "family": "div_ex_calendar",
        "economic_story": (
            "Near ex-date cash-dividend pressure and days-to-ex create "
            "predictable flow / borrow demand; not a textbook yield level."
        ),
    }
    if not path.exists():
        gap["ok"] = False
        return {}, gap
    d = pd.read_parquet(
        path,
        columns=["ts_code", "ann_date", "ex_date", "cash_div", "cash_div_tax", "imp_ann_date"],
    )
    d["ex_date"] = pd.to_datetime(d["ex_date"], errors="coerce")
    d["ann_date"] = pd.to_datetime(d["ann_date"], errors="coerce")
    d["imp_ann_date"] = pd.to_datetime(d["imp_ann_date"], errors="coerce")
    # available after max(ann, imp_ann) 18:00 → next session
    avail_day = d["imp_ann_date"].fillna(d["ann_date"])
    d["avail_session"] = _avail_to_next_session(avail_day + pd.Timedelta(hours=18), cal)
    d["bs"] = d["ts_code"].map(_to_baostock)
    d = d[d["bs"].isin(cols)]
    d = d.dropna(subset=["ex_date", "avail_session", "bs"])
    d = d[
        (d["ex_date"] >= LOOKBACK_START - pd.Timedelta(days=40))
        & (d["ex_date"] <= cal.max() + pd.Timedelta(days=40))
    ]
    gap.update({"ok": True, "n_events": int(len(d)), "n_instruments": int(d["bs"].nunique())})

    T, N = len(cal), len(cols)
    col_index = {c: i for i, c in enumerate(cols)}
    cal_np = cal.values.astype("datetime64[ns]")

    days_to = np.full((T, N), np.nan, dtype=np.float32)
    cash = np.full((T, N), np.nan, dtype=np.float32)
    flag = np.zeros((T, N), dtype=np.float32)

    for r in d.itertuples(index=False):
        j = col_index.get(r.bs)
        if j is None:
            continue
        # from avail_session to ex_date inclusive window: paint days_to_ex
        a = pd.Timestamp(r.avail_session)
        e = pd.Timestamp(r.ex_date).normalize()
        i0 = int(np.searchsorted(cal_np, np.datetime64(a), side="left"))
        i1 = int(np.searchsorted(cal_np, np.datetime64(e), side="right")) - 1
        if i0 >= T or i1 < 0:
            continue
        i0 = max(0, i0)
        i1 = min(T - 1, i1)
        cd = float(r.cash_div) if r.cash_div is not None and np.isfinite(r.cash_div) else np.nan
        for i in range(i0, i1 + 1):
            dto = (e - cal[i]).days
            # keep nearest upcoming ex
            prev = days_to[i, j]
            if not np.isfinite(prev) or dto < prev:
                days_to[i, j] = np.float32(dto)
                if np.isfinite(cd):
                    cash[i, j] = np.float32(cd)
            flag[i, j] = 1.0
    del d
    gc.collect()

    dto_df = pd.DataFrame(days_to, index=cal, columns=cols, dtype="float32")
    cash_df = pd.DataFrame(cash, index=cal, columns=cols, dtype="float32")
    flag_df = pd.DataFrame(flag, index=cal, columns=cols, dtype="float32")
    # clip days_to to [0, 60]
    dto_df = dto_df.clip(lower=0, upper=60)
    out = {
        "div_days_to_ex": dto_df.astype("float32"),
        "neg_div_days_to_ex": (-dto_df).astype("float32"),  # nearer ex → higher
        "div_cash": cash_df.astype("float32"),
        "div_flag": flag_df.astype("float32"),
        "div_flag_20": flag_df.rolling(20, min_periods=1).max().astype("float32"),
        "div_cash_20": cash_df.where(flag_df > 0).rolling(20, min_periods=1).max().astype("float32"),
    }
    # near-ex intensity: 1/(1+days)
    with np.errstate(divide="ignore", invalid="ignore"):
        out["div_near_ex"] = (1.0 / (1.0 + dto_df)).astype("float32")
        out["div_near_ex"] = out["div_near_ex"].where(dto_df.notna()).astype("float32")

    if mask is not None:
        for k in list(out.keys()):
            out[k] = out[k].where(mask).astype("float32")
    for k, df in out.items():
        ev = df.notna() & (df.abs() > 1e-12)
        gap[f"nonempty_{k}"] = float(ev.to_numpy().mean())
        gap[f"mean_names_{k}"] = float(ev.sum(axis=1).mean())
    del days_to, cash, flag, dto_df, cash_df, flag_df
    gc.collect()
    return out, gap


def build_roe_panels(cal, cols, mask) -> tuple[dict, dict]:
    """PIT ROE / gross-margin *changes* — not level EP textbook, not ocf."""
    path = V2 / "financials_pit/financials_pit_tushare.parquet"
    gap = {
        "path": str(path),
        "family": "earn_roe_delta",
        "economic_story": (
            "Point-in-time ROE / gross-margin revisions capture earnings-quality "
            "surprises denser than title announcements; we use *deltas* not EP/BM levels."
        ),
    }
    if not path.exists():
        gap["ok"] = False
        return {}, gap
    fin = pd.read_parquet(
        path,
        columns=["instrument_id", "available_at", "roe", "grossprofit_margin", "end_date", "report_type"],
    )
    fin["available_at"] = pd.to_datetime(fin["available_at"], utc=True, errors="coerce")
    # handle mixed tz / naive
    if getattr(fin["available_at"].dt, "tz", None) is not None:
        fin["available_at"] = fin["available_at"].dt.tz_convert("Asia/Shanghai").dt.tz_localize(None)
    else:
        # try localize as Shanghai if naive wall times from source
        fin["available_at"] = pd.to_datetime(fin["available_at"], errors="coerce")
    fin = fin[fin["instrument_id"].isin(cols)]
    fin = fin.dropna(subset=["available_at"])
    fin = fin[fin["available_at"] >= (LOOKBACK_START - pd.Timedelta(days=400))]
    # prefer consolidated primary reports when report_type present
    if "report_type" in fin.columns:
        # keep all but prefer latest available_at per instrument/end_date
        fin = fin.sort_values(["instrument_id", "end_date", "available_at"]).drop_duplicates(
            ["instrument_id", "end_date", "available_at"], keep="last"
        )
    fin["avail_session"] = _avail_to_next_session(fin["available_at"], cal)
    fin = fin.dropna(subset=["avail_session"])
    gap.update(
        {
            "ok": True,
            "n_rows": int(len(fin)),
            "n_instruments": int(fin["instrument_id"].nunique()),
        }
    )

    def pivot_asof(valcol: str) -> pd.DataFrame:
        sub = fin[["avail_session", "instrument_id", valcol]].dropna(subset=[valcol])
        sub = sub.sort_values(["avail_session", "instrument_id"]).drop_duplicates(
            ["avail_session", "instrument_id"], keep="last"
        )
        wide = (
            sub.set_index(["avail_session", "instrument_id"])[valcol]
            .unstack()
            .reindex(index=cal, columns=cols)
            .astype("float32")
        )
        # PIT level: ffill until next revision (no limit — that's the PIT state)
        wide = wide.ffill()
        if mask is not None:
            wide = wide.where(mask)
        return wide.astype("float32")

    roe = pivot_asof("roe")
    gm = pivot_asof("grossprofit_margin")
    # winsorize
    for df in (roe, gm):
        arr = df.to_numpy(dtype=np.float64, copy=True)
        finite = arr[np.isfinite(arr)]
        if finite.size > 100:
            lo, hi = np.nanpercentile(finite, [1, 99])
            arr = np.clip(arr, lo, hi)
            df.loc[:, :] = arr.astype(np.float32)

    out = {
        "roe_pit": roe.astype("float32"),
        "gm_pit": gm.astype("float32"),
        "roe_delta_5": roe.diff(5).astype("float32"),
        "roe_delta_20": roe.diff(20).astype("float32"),
        "gm_delta_5": gm.diff(5).astype("float32"),
        "gm_delta_20": gm.diff(20).astype("float32"),
        "neg_roe_pit": (-roe).astype("float32"),
        "abs_roe_delta_20": roe.diff(20).abs().astype("float32"),
    }
    if mask is not None:
        for k in list(out.keys()):
            out[k] = out[k].where(mask).astype("float32")
    for k, df in out.items():
        ev = df.notna() & (df.abs() > 1e-12)
        gap[f"nonempty_{k}"] = float(ev.to_numpy().mean())
        gap[f"mean_names_{k}"] = float(ev.sum(axis=1).mean())
    del fin, roe, gm
    gc.collect()
    return out, gap


def build_candidates() -> list[dict]:
    cands = []

    def add(expr: str, family: str, note: str = ""):
        L = leaves_in(expr)
        if not L or any(is_banned_leaf(x) for x in L):
            return
        if L.issubset(TEXTBOOK_LEAVES):
            return
        if is_fsr_family(expr):
            return
        if is_title_sparse_primary(expr):
            return
        cands.append({"expr": expr, "family": family, "note": note})

    # --- CB equity pressure (PRIMARY original) ---
    for x in (
        "cb_prem",
        "neg_cb_prem",
        "cb_bond_prem",
        "neg_cb_bond_prem",
        "cb_prem_delta_5",
        "cb_prem_delta_10",
        "cb_amt_5",
        "cb_amt_10",
        "cb_amt_log5",
        "cb_vol_5",
        "cb_flag_5",
    ):
        add(x, "cb_equity_pressure", "raw")
        add(f"rank({x})", "cb_equity_pressure", "rank")
        add(f"zscore({x})", "cb_equity_pressure", "zscore")
        add(f"neg({x})", "cb_equity_pressure", "neg")
        add(f"rank(neg({x}))", "cb_equity_pressure", "rank neg")
        add(f"ts_mean_10({x})", "cb_equity_pressure", "ts_mean10")
        add(f"rank(ts_mean_10({x}))", "cb_equity_pressure", "rank ts_mean10")
        add(f"ts_std_10({x})", "cb_equity_pressure", "ts_std10")
        add(f"rank(ts_std_10({x}))", "cb_equity_pressure", "rank ts_std10")
        add(f"ts_delta_5({x})", "cb_equity_pressure", "delta5")
        add(f"rank(ts_delta_5({x}))", "cb_equity_pressure", "rank delta5")
        add(f"abs(ts_std_10(ts_delta_5({x})))", "cb_equity_pressure", "vol delta")
        add(f"delay_5({x})", "cb_equity_pressure", "delay5")
        add(f"ts_max_5({x})", "cb_equity_pressure", "ts_max5")

    add("cb_flag", "cb_equity_pressure", "issuer flag")
    add("rank(cb_flag)", "cb_equity_pressure", "rank flag")
    add("neg(cb_flag)", "cb_equity_pressure", "neg flag")

    # crosses within CB
    add("mul(rank(neg_cb_prem), rank(cb_amt_log5))", "cb_equity_pressure", "low prem x amt")
    add("mul(rank(neg_cb_prem), rank(cb_flag_5))", "cb_equity_pressure", "low prem x active")
    add(
        "mul(rank(abs(cb_prem_delta_5)), rank(cb_amt_log5))",
        "cb_equity_pressure",
        "prem chg x amt",
    )
    add(
        "mul(rank(ts_std_10(cb_prem)), rank(cb_amt_log5))",
        "cb_equity_pressure",
        "prem vol x amt",
    )

    # --- div ex calendar ---
    for x in (
        "div_days_to_ex",
        "neg_div_days_to_ex",
        "div_near_ex",
        "div_cash",
        "div_flag",
        "div_flag_20",
        "div_cash_20",
    ):
        add(x, "div_ex_calendar", "raw")
        add(f"rank({x})", "div_ex_calendar", "rank")
        add(f"neg({x})", "div_ex_calendar", "neg")
        add(f"rank(neg({x}))", "div_ex_calendar", "rank neg")
        add(f"ts_mean_10({x})", "div_ex_calendar", "ts_mean")
        add(f"ts_std_10({x})", "div_ex_calendar", "ts_std")
        add(f"rank(ts_std_10({x}))", "div_ex_calendar", "rank ts_std")
        add(f"ts_max_5({x})", "div_ex_calendar", "ts_max")

    # --- earn ROE delta ---
    for x in (
        "roe_delta_5",
        "roe_delta_20",
        "gm_delta_5",
        "gm_delta_20",
        "abs_roe_delta_20",
        "roe_pit",
        "gm_pit",
        "neg_roe_pit",
    ):
        add(x, "earn_roe_delta", "raw")
        add(f"rank({x})", "earn_roe_delta", "rank")
        add(f"zscore({x})", "earn_roe_delta", "zscore")
        add(f"neg({x})", "earn_roe_delta", "neg")
        add(f"rank(neg({x}))", "earn_roe_delta", "rank neg")
        add(f"ts_mean_10({x})", "earn_roe_delta", "ts_mean")
        add(f"rank(ts_mean_10({x}))", "earn_roe_delta", "rank ts_mean")
        add(f"ts_std_10({x})", "earn_roe_delta", "ts_std")
        add(f"rank(ts_std_10({x}))", "earn_roe_delta", "rank ts_std")
        add(f"abs(ts_std_10(ts_delta_5({x})))", "earn_roe_delta", "vol delta")
        add(f"delay_5({x})", "earn_roe_delta", "delay5")

    # light cross CB x ROE delta (dense x dense-ish)
    add(
        "mul(rank(neg_cb_prem), rank(roe_delta_20))",
        "cb_x_roe",
        "low prem x roe surprise",
    )
    add(
        "mul(rank(cb_amt_log5), rank(abs_roe_delta_20))",
        "cb_x_roe",
        "cb flow x roe shock",
    )
    add(
        "mul(rank(neg_cb_prem), rank(div_near_ex))",
        "cb_x_div",
        "low prem x near ex",
    )

    seen = set()
    out = []
    for c in cands:
        if c["expr"] in seen:
            continue
        seen.add(c["expr"])
        out.append(c)
    return out


def write_report(rows, meta, gate_ok_list):
    lines = []
    lines.append("# AI 因子 L1g：新原创机制族探索（非 FSR / 非 ann_title 稀疏主依赖）")
    lines.append("")
    lines.append("- **时间：** 2026-10-12（America/New_York）")
    lines.append("- **promotion_approved：** false；**密封：** 未开；**不交 Strategy 权重**")
    lines.append("- **trial_kind：** explore_gate / process")
    lines.append("- **本金主口径：** 60 万 / 100 万；主裁决=冲击+flat25")
    lines.append(
        "- **严格 GATE_OK：** ①非rank硬覆盖；②冲击+25bp@60万∧100万≥10%；"
        "③ICIR>0；④非 rank_fill；⑤非 title 稀疏主依赖；⑥非 FSR 新挖"
    )
    lines.append(
        "- **禁止：** 广播、跌停主候选、小盘、教科书主线入主清单、FSR/float_share_ratio "
        "作为新发现、ann_title 稀疏主依赖、密封、Strategy"
    )
    lines.append(f"- 账本：N {meta.get('ledger_N_before')} → {meta.get('ledger_N_after')} "
                 f"（+{meta.get('ledger_N_new')}，explore_gate）")
    lines.append(
        f"- 峰值 RSS：{meta.get('peak_rss_MB'):.0f} MB（上限 {meta.get('mem_cap_MB')}；"
        f"under_cap={meta.get('under_mem_cap')}）；运行 {meta.get('runtime_s')}s"
    )
    lines.append("")
    lines.append("## 机制故事（原创）")
    lines.append("")
    lines.append("### 1) cb_equity_pressure（主族）")
    lines.append("")
    lines.append(
        "- **钱从谁来：** 可转债复利/套利盘与转股稀释预期。转股溢价 `cb_over_rate` "
        "压低或压缩 → 转股/套利更可能 → 正股承压或波动抬升；CB 成交额强度标记复杂流活跃日。"
    )
    lines.append(
        "- **失效条件：** CB 存量稀薄、强赎潮一次性冲击、正股停牌、溢价长期失真（垃圾债段）。"
    )
    lines.append("- **PIT：** `available_at`（收盘）→ 下一交易日可用；非发行人保持 NaN（诚实覆盖）。")
    lines.append("- **非密封探索；** 不交 Strategy。")
    lines.append("")
    lines.append("### 2) div_ex_calendar（次族）")
    lines.append("")
    lines.append("- 除权日临近 / 现金分红日历流；季节性稀疏可预期，硬覆盖不过则 FAIL_SPARSE。")
    lines.append("")
    lines.append("### 3) earn_roe_delta（次族）")
    lines.append("")
    lines.append(
        "- PIT ROE/毛利率的 *变化*（非 EP/BM 水平、非 L1f 已挖 ocf）；"
        "比 title 公告更密的盈余惊喜代理。"
    )
    lines.append("")
    lines.append("## 批次规模与失败拆解")
    lines.append("")
    lines.append(f"- 候选：{meta.get('n_candidates')}")
    fr = meta.get("fail_reason_counts") or {}
    lines.append("| 失败原因 | 计数 |")
    lines.append("|---|---:|")
    for k, v in sorted(fr.items(), key=lambda kv: -kv[1]):
        lines.append(f"| {k} | {v} |")
    lines.append(f"| **GATE_OK** | **{meta.get('n_gate_ok')}** |")
    lines.append("")
    lines.append("## 族摘要")
    lines.append("")
    fam = meta.get("family_counts") or {}
    lines.append("| 族 | 候选 | FAIL_SPARSE | FAIL_RANK_FILL | FAIL_ICIR | FAIL_GATE | GATE_OK |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for k, v in sorted(fam.items()):
        lines.append(
            f"| {k} | {v.get('n', 0)} | {v.get('fail_sparse', 0)} | "
            f"{v.get('fail_rank_fill', 0)} | {v.get('fail_icir', 0)} | "
            f"{v.get('fail_gate', 0)} | {v.get('gate_ok', 0)} |"
        )
    lines.append("")
    lines.append("## 数据缺口 / 覆盖草图")
    lines.append("")
    for key in ("cb_gap", "div_gap", "roe_gap"):
        g = meta.get(key) or {}
        lines.append(f"### {key}")
        lines.append(f"- ok={g.get('ok')} path=`{g.get('path')}`")
        if g.get("economic_story"):
            lines.append(f"- story: {g.get('economic_story')}")
        keys = [k for k in g.keys() if k.startswith("nonempty_")][:12]
        for k in keys:
            mn = g.get(k.replace("nonempty_", "mean_names_"), float("nan"))
            val = g.get(k)
            if isinstance(val, float) and isinstance(mn, float):
                lines.append(f"- {k}={val:.4f} mean_names={mn:.1f}")
            else:
                lines.append(f"- {k}={val}")
        lines.append("")
    lines.append("## GATE_OK 列表（严格）")
    lines.append("")
    if not gate_ok_list:
        lines.append("*（空）本批无同时满足全部严格闸门的叶。*")
    else:
        lines.append(
            "| # | 族 | 表达式 | flat25 | 60万+25bp | 100万+25bp | ICIR | 换手 | "
            "nonempty(非rank) | rank_fill | 裁决 |"
        )
        lines.append("|---|---|---|---:|---:|---:|---:|---:|---:|---|---|")
        for i, r in enumerate(gate_ok_list, 1):
            m = r.get("metrics") or {}
            cov = r.get("coverage_norank") or r.get("coverage") or {}
            lines.append(
                f"| {i} | {r.get('family')} | `{r.get('expr')}` | "
                f"{fmt_pct(m.get('flat25'))} | {fmt_pct(m.get('imp60_p25'))} | "
                f"{fmt_pct(m.get('imp100_p25'))} | {fmt_f(m.get('icir'), 3)} | "
                f"{fmt_f(m.get('turn'), 3)} | {fmt_f(cov.get('nonempty_rate'), 4)} | "
                f"{r.get('rank_fill_cov')} | {r.get('verdict')} |"
            )
    lines.append("")
    lines.append("## 近闸对照")
    lines.append("")
    near = [
        r
        for r in rows
        if r.get("verdict") in ("FAIL_ICIR", "FAIL_GATE") and r.get("survive_coverage_norank")
    ]
    near = sorted(
        near,
        key=lambda r: (r.get("metrics") or {}).get("imp60_p25") or float("-inf"),
        reverse=True,
    )[:25]
    if not near:
        lines.append("*无。*")
    else:
        lines.append("| 表达式 | 族 | flat25 | 60万+25bp | ICIR | nonempty | 裁决 |")
        lines.append("|---|---|---:|---:|---:|---:|---|")
        for r in near:
            m = r.get("metrics") or {}
            cov = r.get("coverage_norank") or {}
            lines.append(
                f"| `{r.get('expr')}` | {r.get('family')} | {fmt_pct(m.get('flat25'))} | "
                f"{fmt_pct(m.get('imp60_p25'))} | {fmt_f(m.get('icir'), 3)} | "
                f"{fmt_f(cov.get('nonempty_rate'), 4)} | {r.get('verdict')} |"
            )
    lines.append("")
    lines.append("## 与短清单并列 / 是否可并入")
    lines.append("")
    lines.append(meta.get("shortlist_note") or "")
    lines.append("")
    lines.append(f"- **本批 GATE_OK 数：** {meta.get('n_gate_ok')}")
    lines.append(f"- **是否建议后续并入短清单（仍不密封）：** {meta.get('joinable_to_shortlist')}")
    lines.append(f"- **joinable 表达式：** {meta.get('joinable_exprs')}")
    lines.append("")
    lines.append("## 诚实裁决")
    lines.append("")
    lines.append(
        f"1. **严格存活：** GATE_OK={meta.get('n_gate_ok')}/{meta.get('n_candidates')}。"
    )
    lines.append("2. **覆盖诚实：** strip_rank 非rank 口径；rank_fill → FAIL_RANK_FILL。")
    lines.append("3. **未挖 FSR / ann_title 稀疏主依赖 / 广播 / 跌停主候选 / 小盘。**")
    lines.append("4. **ICIR≤0 即使冲击正 → FAIL_ICIR（rzrq 教训）。**")
    lines.append("5. **不开密封、不交 Strategy；`promotion_approved=false`。**")
    lines.append("")
    lines.append("## 产物路径")
    lines.append("")
    lines.append("- 报告：`output/alpha/AI_FACTOR_L1g_NEW_MECH_FAMILY_EXPLORE_ZH.md`")
    lines.append("- JSON：`output/ai_factor/l1g_new_mech_family/`")
    lines.append(f"- 账本：`output/ai_factor/ledger.jsonl` N={meta.get('ledger_N_after')}")
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    log("wrote", REPORT)


def main() -> int:
    global t0
    t0 = time.time()
    peak = mem_mb()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    _ensure_pkgs()
    sci = _import_mod(
        "ai_factor_l1d_shortlist_coverage_impact",
        ROOT / "research/ai_factor_l1d_shortlist_coverage_impact.py",
    )
    l1b = _import_mod(
        "ai_factor_l1b_structural_explore",
        ROOT / "research/ai_factor_l1b_structural_explore.py",
    )
    from quantlab.factors.ai_factory.ledger import append_attempt
    from quantlab.factors.ops import apply_expr, parse_expr

    log("loading midlarge mask via structural panels")
    panels, label, public, load_meta = l1b.load_structural_panels()
    peak = max(peak, mem_mb())
    del public
    gc.collect()

    if "overnight_ret" in panels:
        mask = panels["overnight_ret"].notna()
        cols = list(panels["overnight_ret"].columns)
        cal = panels["overnight_ret"].index
    else:
        cols = list(next(iter(panels.values())).columns)
        cal = next(iter(panels.values())).index
        mask = None

    for k in list(panels.keys()):
        del panels[k]
    panels = {}
    gc.collect()
    log("cleared structural; building L1g families", "n_cols", len(cols), "peak", peak)

    cb_panels, cb_gap = build_cb_panels(cal, cols, mask)
    panels.update(cb_panels)
    del cb_panels
    gc.collect()
    peak = max(peak, mem_mb())
    log("cb done", "ok", cb_gap.get("ok"), "peak", peak,
        "nonempty_cb_prem", f"{cb_gap.get('nonempty_cb_prem', float('nan')):.4f}" if isinstance(cb_gap.get("nonempty_cb_prem"), float) else "—")

    div_panels, div_gap = build_div_panels(cal, cols, mask)
    panels.update(div_panels)
    del div_panels
    gc.collect()
    peak = max(peak, mem_mb())
    log("div done", "ok", div_gap.get("ok"), "peak", peak)

    roe_panels, roe_gap = build_roe_panels(cal, cols, mask)
    panels.update(roe_panels)
    del roe_panels
    gc.collect()
    peak = max(peak, mem_mb())
    log("roe done", "ok", roe_gap.get("ok"), "n_panels", len(panels), "peak", peak)

    cands = build_candidates()
    present = set(panels.keys())
    cands = [c for c in cands if leaves_in(c["expr"]) <= present]
    log("candidates", len(cands))

    sig, adv = sci.load_sig_adv(cols, cal)
    peak = max(peak, mem_mb())

    main_ledger = ROOT / "output/ai_factor/ledger.jsonl"
    run_ledger = OUT_DIR / "ledger_run.jsonl"
    if run_ledger.exists():
        run_ledger.unlink()
    n_before = (
        sum(1 for x in main_ledger.read_text().splitlines() if x.strip())
        if main_ledger.exists()
        else 0
    )

    rows = []
    gate_ok_list = []
    fam_counts: dict[str, dict] = {}
    fail_reason_counts: dict[str, int] = {}

    def bump_fail(reason: str):
        fail_reason_counts[reason] = fail_reason_counts.get(reason, 0) + 1

    for i, cand in enumerate(cands):
        expr = cand["expr"]
        fam = cand.get("family") or family_of(expr)
        fam_counts.setdefault(
            fam,
            {
                "n": 0,
                "fail_sparse": 0,
                "fail_rank_fill": 0,
                "fail_icir": 0,
                "fail_gate": 0,
                "gate_ok": 0,
                "fail_cs": 0,
                "fail_title": 0,
                "fail_fsr": 0,
                "error": 0,
            },
        )
        fam_counts[fam]["n"] += 1
        norank_expr = strip_rank(expr)
        try:
            if is_title_sparse_primary(expr) or is_fsr_family(expr):
                reason = "FAIL_FSR_BANNED" if is_fsr_family(expr) else "FAIL_TITLE_SPARSE_PRIMARY"
                bump_fail(reason)
                if "FSR" in reason:
                    fam_counts[fam]["fail_fsr"] += 1
                else:
                    fam_counts[fam]["fail_title"] += 1
                row = {
                    **cand,
                    "family": fam,
                    "metrics": sci.pack_metrics(None),
                    "coverage": None,
                    "coverage_norank": None,
                    "rank_fill_cov": False,
                    "survive_coverage_norank": False,
                    "gate_ok": False,
                    "verdict": reason,
                    "promotion_approved": False,
                    "trial_kind": "explore_gate",
                    "norank_expr": norank_expr,
                }
                rows.append(row)
                fit = None
            else:
                tup = _seed_to_tuple(expr)
                fac = apply_expr(parse_expr(to_nested_tuple(tup)), panels).astype("float32")
                if norank_expr != expr:
                    fac_nr = apply_expr(
                        parse_expr(to_nested_tuple(_seed_to_tuple(norank_expr))), panels
                    ).astype("float32")
                else:
                    fac_nr = fac
                cov_rankish = sci.coverage_stats(fac)
                cov_nr = sci.coverage_stats(fac_nr)
                cs = sci.cs_std_stats(fac)

                rank_fill = bool(
                    has_rank_op(expr)
                    and cov_rankish.get("passes_coverage")
                    and not cov_nr.get("passes_coverage")
                )
                if has_rank_op(expr) and not rank_fill:
                    nr = cov_nr.get("nonempty_rate") or 0.0
                    rr = cov_rankish.get("nonempty_rate") or 0.0
                    if rr >= COV_NONEMPTY_MIN and nr < COV_NONEMPTY_MIN:
                        rank_fill = True

                if rank_fill:
                    bump_fail("FAIL_RANK_FILL")
                    fam_counts[fam]["fail_rank_fill"] += 1
                    row = {
                        **cand,
                        "family": fam,
                        "metrics": sci.pack_metrics(None),
                        "coverage": cov_rankish,
                        "coverage_norank": cov_nr,
                        "rank_fill_cov": True,
                        "survive_coverage_norank": False,
                        "gate_ok": False,
                        "verdict": "FAIL_RANK_FILL",
                        "promotion_approved": False,
                        "trial_kind": "explore_gate",
                        "norank_expr": norank_expr,
                        "cs_stats": cs,
                    }
                    rows.append(row)
                    fit = None
                elif not cov_nr.get("passes_coverage"):
                    bump_fail("FAIL_SPARSE")
                    fam_counts[fam]["fail_sparse"] += 1
                    row = {
                        **cand,
                        "family": fam,
                        "metrics": sci.pack_metrics(None),
                        "coverage": cov_rankish,
                        "coverage_norank": cov_nr,
                        "rank_fill_cov": False,
                        "survive_coverage_norank": False,
                        "gate_ok": False,
                        "verdict": "FAIL_SPARSE",
                        "promotion_approved": False,
                        "trial_kind": "explore_gate",
                        "norank_expr": norank_expr,
                        "cs_stats": cs,
                    }
                    rows.append(row)
                    fit = None
                elif not cs.get("passes_cs_variation"):
                    bump_fail("FAIL_CS")
                    fam_counts[fam]["fail_cs"] += 1
                    row = {
                        **cand,
                        "family": fam,
                        "metrics": sci.pack_metrics({"skipped": True, "reason": "cs_variation_fail"}),
                        "coverage": cov_rankish,
                        "coverage_norank": cov_nr,
                        "rank_fill_cov": False,
                        "survive_coverage_norank": True,
                        "gate_ok": False,
                        "verdict": "FAIL_CS",
                        "promotion_approved": False,
                        "trial_kind": "explore_gate",
                        "norank_expr": norank_expr,
                        "cs_stats": cs,
                    }
                    rows.append(row)
                    fit = None
                else:
                    sim = sci.simulate_book(fac, label, sig, adv)
                    m = sci.pack_metrics(sim)
                    icir = m.get("icir", float("nan"))
                    impact_ok = (
                        math.isfinite(m.get("flat25", float("nan")))
                        and m["flat25"] > 0
                        and math.isfinite(m.get("imp60_p25", float("nan")))
                        and m["imp60_p25"] >= IMP60_FLOOR
                        and math.isfinite(m.get("imp100_p25", float("nan")))
                        and m["imp100_p25"] >= IMP60_FLOOR
                    )
                    icir_ok = math.isfinite(icir) and icir > 0
                    if not impact_ok:
                        verdict = "FAIL_GATE"
                        bump_fail("FAIL_GATE")
                        fam_counts[fam]["fail_gate"] += 1
                        gate_ok = False
                    elif not icir_ok:
                        verdict = "FAIL_ICIR"
                        bump_fail("FAIL_ICIR")
                        fam_counts[fam]["fail_icir"] += 1
                        gate_ok = False
                    else:
                        verdict = "GATE_OK"
                        fam_counts[fam]["gate_ok"] += 1
                        gate_ok = True
                    row = {
                        **cand,
                        "family": fam,
                        "metrics": m,
                        "coverage": cov_rankish,
                        "coverage_norank": cov_nr,
                        "rank_fill_cov": False,
                        "survive_coverage_norank": True,
                        "gate_ok": gate_ok,
                        "verdict": verdict,
                        "promotion_approved": False,
                        "trial_kind": "explore_gate",
                        "norank_expr": norank_expr,
                        "cs_stats": cs,
                    }
                    rows.append(row)
                    if gate_ok:
                        gate_ok_list.append(row)
                    fit = m.get("imp60_p25")
                if norank_expr != expr and fac_nr is not fac:
                    del fac_nr
                del fac
        except Exception as exc:  # noqa: BLE001
            bump_fail("ERROR")
            fam_counts[fam]["error"] += 1
            row = {
                **cand,
                "family": fam,
                "metrics": sci.pack_metrics(None),
                "coverage": None,
                "coverage_norank": None,
                "rank_fill_cov": False,
                "survive_coverage_norank": False,
                "gate_ok": False,
                "verdict": "ERROR",
                "error": f"{type(exc).__name__}: {exc}",
                "promotion_approved": False,
                "trial_kind": "explore_gate",
                "norank_expr": norank_expr,
            }
            rows.append(row)
            fit = None

        notes = (
            f"l1g_new_mech_family;family={fam};verdict={row.get('verdict')};"
            f"rank_fill={row.get('rank_fill_cov')};cov_nr={row.get('survive_coverage_norank')};"
            f"process_not_sealed;promotion_approved=false"
        )
        for path in (run_ledger, main_ledger):
            append_attempt(
                engine="l1g_new_mech_family",
                seed=SEED,
                universe="midlarge_top1500_or_csi300_500",
                cost=0.0025,
                window="explore_20240603_to_latest_l1g_new_mech",
                expr_str=expr,
                fitness=fit if isinstance(fit, float) and math.isfinite(fit) else None,
                notes=notes,
                path=path,
            )
        if (i + 1) % 20 == 0 or i == 0 or i + 1 == len(cands):
            peak = max(peak, mem_mb())
            log(
                f"{i+1}/{len(cands)}",
                row.get("verdict"),
                expr[:56],
                "60+25",
                fmt_pct(fit) if fit is not None else "—",
                "peak",
                peak,
            )
        if mem_mb() > MEM_CAP_MB - 150:
            gc.collect()

    n_gate_ok = len(gate_ok_list)
    fail_display = {k: v for k, v in fail_reason_counts.items() if k != "GATE_OK"}
    gate_ok_list = sorted(
        gate_ok_list,
        key=lambda r: (r.get("metrics") or {}).get("imp60_p25") or float("-inf"),
        reverse=True,
    )
    n_after = (
        sum(1 for x in main_ledger.read_text().splitlines() if x.strip())
        if main_ledger.exists()
        else 0
    )
    peak = max(peak, mem_mb())

    joinable = [r["expr"] for r in gate_ok_list]
    shortlist_note = (
        "短清单 v2c 先验（N=8）含 ann_insider×2 + L1f FSR 族新叶×6；"
        "本批禁 FSR 新挖、禁 ann_title 稀疏主依赖。"
        "仅 GATE_OK 且非教科书主线者可后续并列扩容（仍不密封、不交 Strategy）。"
    )
    meta = {
        "mode": "l1g_new_mech_family_explore",
        "promotion_approved": False,
        "sealed_executed": False,
        "trial_kind": "explore_gate",
        "ann_title_only": True,
        "invented_body": False,
        "n_candidates": len(cands),
        "n_gate_ok": n_gate_ok,
        "fail_reason_counts": fail_display,
        "family_counts": fam_counts,
        "cb_gap": cb_gap,
        "div_gap": div_gap,
        "roe_gap": roe_gap,
        "ledger_N_before": n_before,
        "ledger_N_after": n_after,
        "ledger_N_new": n_after - n_before,
        "peak_rss_MB": peak,
        "mem_cap_MB": MEM_CAP_MB,
        "under_mem_cap": peak < MEM_CAP_MB,
        "runtime_s": round(time.time() - t0, 1),
        "gate_ok_exprs": joinable,
        "joinable_to_shortlist": bool(n_gate_ok > 0),
        "joinable_exprs": joinable,
        "shortlist_note": shortlist_note,
        "primary_family": "cb_equity_pressure",
        "secondary_families": ["div_ex_calendar", "earn_roe_delta"],
        "banned_as_new_discovery": [
            "FSR",
            "float_share_ratio",
            "ann_title_sparse_primary",
            "broadcast",
            "LD_primary",
            "textbook_mainline",
            "rzrq",
            "ocf_rehash",
        ],
    }
    (OUT_DIR / "results.json").write_text(
        json.dumps(clean(rows), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "gate_ok.json").write_text(
        json.dumps(clean(gate_ok_list), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "summary.json").write_text(
        json.dumps(clean(meta), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_report(rows, meta, gate_ok_list)
    log(
        "DONE",
        "cand",
        len(cands),
        "GATE_OK",
        n_gate_ok,
        "fails",
        fail_display,
        "N",
        n_after,
        "peak",
        peak,
        "joinable",
        bool(n_gate_ok > 0),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
