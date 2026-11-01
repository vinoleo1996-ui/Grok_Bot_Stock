#!/usr/bin/env python3
"""L1h: new original mechanism family explore (parallel to gm→v2d).

Primary: **liq_regime_instability** — volatility / CV / burstiness of turnover
& amount (NOT Amihud |ret|/V textbook). Economic story: unstable liquidity
regimes raise adverse-selection risk for liquidity providers; cross-section
premia appear when liquidity CV / burst is elevated then mean-reverts into
tradable mid/large names.

Secondary: **idx_weight_pressure** — CSI300/500/1000 PIT weight level & delta
(passive / index-flow pressure around rebalance & drift).

Tertiary: **lev_revision** — debt_to_assets PIT *deltas* (balance-sheet leverage
revision / refi pressure). Explicitly NOT ROE/quality textbook shells.

Banned / exhausted: FSR, ann_title sparse primary, ROE/gm quality shells,
broadcast, LD primary, rank_fill, cb_equity_pressure, lockup, rzrq intensity,
float_evt, ann_insider, small-cap, textbook main shortlist, sealed, Strategy.

Hard GATE_OK: hard cov non-rank; impact+25bp@60万∧100万≥10%; ICIR>0;
not rank_fill; not title-sparse primary; not FSR.
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
SCRATCH = Path("/workspace/scratch/tic")
V2 = ROOT / "data/v2"
OUT_DIR = ROOT / "output/ai_factor/l1h_new_mech_family"
REPORT = ROOT / "output/alpha/AI_FACTOR_L1h_NEW_MECH_FAMILY_EXPLORE_ZH.md"

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
        "roe_pit", "gm_pit", "roe_delta_5", "roe_delta_20", "gm_delta_5", "gm_delta_20",
        "neg_roe_pit", "abs_roe_delta_20",
        "cb_prem", "neg_cb_prem", "cb_bond_prem", "cb_amt_5", "cb_flag",
    }
)
BANNED_PREFIXES = (
    "mkt_", "etf_", "if_basis", "limit_down_", "ld_", "ann_",
    "rz_", "rq_", "rzrq_", "float_evt", "float_ratio_", "lockup_",
    "fsr", "float_share", "ocf_", "roe_", "gm_", "cb_", "div_",
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
    print(f"[l1h_new {time.time()-t0:5.0f}s {mem_mb():.0f}MB]", *a, flush=True)


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


def is_roe_quality_shell(expr: str) -> bool:
    L = leaves_in(expr)
    return any(x.startswith("roe_") or x.startswith("gm_") or x in ("roe_pit", "gm_pit") for x in L)


def family_of(expr: str) -> str:
    L = sorted(leaves_in(expr))
    if not L:
        return "unknown"
    if all(x.startswith("liq_") or x.startswith("amt_") for x in L):
        return "liq_regime_instability"
    if all(x.startswith("idx_") for x in L):
        return "idx_weight_pressure"
    if all(x.startswith("lev_") for x in L):
        return "lev_revision"
    if any(x.startswith("liq_") or x.startswith("amt_") for x in L) and any(
        x.startswith("idx_") for x in L
    ):
        return "liq_x_idx"
    if any(x.startswith("liq_") or x.startswith("amt_") for x in L) and any(
        x.startswith("lev_") for x in L
    ):
        return "liq_x_lev"
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
    cal_np = cal.values.astype("datetime64[ns]")
    av = pd.to_datetime(avail_series, errors="coerce")
    if getattr(av.dt, "tz", None) is not None:
        av = av.dt.tz_convert("Asia/Shanghai").dt.tz_localize(None)
    day = av.dt.normalize() + pd.Timedelta(days=1)
    day_np = day.values.astype("datetime64[ns]")
    idx = np.searchsorted(cal_np, day_np, side="left")
    T = len(cal)
    out_dates = np.empty(len(idx), dtype="datetime64[ns]")
    out_dates[:] = np.datetime64("NaT", "ns")
    valid = (idx >= 0) & (idx < T) & ~pd.isna(day)
    out_dates[valid.to_numpy()] = cal_np[idx[valid.to_numpy()]]
    return pd.Series(out_dates, index=avail_series.index)


def _winsor_df(df: pd.DataFrame, lo=1.0, hi=99.0) -> pd.DataFrame:
    arr = df.to_numpy(dtype=np.float64, copy=True)
    finite = arr[np.isfinite(arr)]
    if finite.size > 100:
        a, b = np.nanpercentile(finite, [lo, hi])
        arr = np.clip(arr, a, b)
        out = df.copy()
        out.loc[:, :] = arr.astype(np.float32)
        return out
    return df.astype("float32")


def _cov_annotate(gap: dict, out: dict):
    for k, df in out.items():
        ev = df.notna() & (df.abs() > 1e-12)
        gap[f"nonempty_{k}"] = float(ev.to_numpy().mean())
        gap[f"mean_names_{k}"] = float(ev.sum(axis=1).mean())


def build_liq_panels(cal, cols, mask) -> tuple[dict, dict]:
    """Liquidity-regime instability from turnover/amount — NOT Amihud."""
    gap = {
        "family": "liq_regime_instability",
        "economic_story": (
            "Liquidity-regime instability: CV and burstiness of turnover/amount "
            "measure whether a name's trading capacity is stable. Unstable regimes "
            "raise adverse-selection risk for liquidity providers; after bursts, "
            "mid/large names often mean-revert as capacity normalizes. Distinct from "
            "Amihud (|ret|/amount level illiquidity) and from textbook turn_20 mean."
        ),
        "path_turnover": str(SCRATCH / "turnover.parquet"),
        "path_amount": str(SCRATCH / "amount.parquet"),
    }
    tov = pd.read_parquet(SCRATCH / "turnover.parquet", columns=cols).astype("float32")
    tov = tov.loc[(tov.index >= LOOKBACK_START) & (tov.index <= cal.max())]
    tov = tov.reindex(index=cal, columns=cols)
    amt = pd.read_parquet(SCRATCH / "amount.parquet", columns=cols).astype("float32")
    amt = amt.loc[(amt.index >= LOOKBACK_START) & (amt.index <= cal.max())]
    amt = amt.reindex(index=cal, columns=cols)

    if mask is not None:
        tov = tov.where(mask)
        amt = amt.where(mask)

    # replace non-positive with NaN for ratio safety
    tov_pos = tov.where(tov > 0)
    amt_pos = amt.where(amt > 0)

    mean20_t = tov_pos.rolling(20, min_periods=10).mean()
    std20_t = tov_pos.rolling(20, min_periods=10).std()
    mean10_t = tov_pos.rolling(10, min_periods=5).mean()
    std10_t = tov_pos.rolling(10, min_periods=5).std()
    mean20_a = amt_pos.rolling(20, min_periods=10).mean()
    std20_a = amt_pos.rolling(20, min_periods=10).std()

    with np.errstate(divide="ignore", invalid="ignore"):
        liq_cv_20 = (std20_t / mean20_t).astype("float32")
        liq_cv_10 = (std10_t / mean10_t).astype("float32")
        liq_burst_10 = (tov_pos / mean20_t).astype("float32")
        liq_burst_5 = (tov_pos / mean10_t).astype("float32")
        amt_cv_20 = (std20_a / mean20_a).astype("float32")
        amt_burst_10 = (amt_pos / mean20_a).astype("float32")
        # acceleration of liquidity (not level turnover)
        liq_accel_5 = (tov_pos.diff(5) / mean20_t).astype("float32")
        liq_accel_10 = (tov_pos.diff(10) / mean20_t).astype("float32")
        # log-amount instability
        log_amt = np.log1p(amt_pos.clip(lower=0)).astype("float32")
        amt_log_std_20 = log_amt.rolling(20, min_periods=10).std().astype("float32")

    # clip extreme CVs
    for df in (liq_cv_20, liq_cv_10, amt_cv_20, liq_burst_10, liq_burst_5, amt_burst_10):
        arr = df.to_numpy(dtype=np.float64, copy=True)
        finite = arr[np.isfinite(arr)]
        if finite.size > 100:
            hi = float(np.nanpercentile(finite, 99.5))
            arr = np.clip(arr, 0.0, hi)
            df.loc[:, :] = arr.astype(np.float32)

    out = {
        "liq_cv_20": liq_cv_20.astype("float32"),
        "liq_cv_10": liq_cv_10.astype("float32"),
        "liq_burst_10": liq_burst_10.astype("float32"),
        "liq_burst_5": liq_burst_5.astype("float32"),
        "neg_liq_cv_20": (-liq_cv_20).astype("float32"),
        "neg_liq_burst_10": (-liq_burst_10).astype("float32"),
        "amt_cv_20": amt_cv_20.astype("float32"),
        "amt_burst_10": amt_burst_10.astype("float32"),
        "neg_amt_cv_20": (-amt_cv_20).astype("float32"),
        "liq_accel_5": liq_accel_5.astype("float32"),
        "liq_accel_10": liq_accel_10.astype("float32"),
        "abs_liq_accel_5": liq_accel_5.abs().astype("float32"),
        "amt_log_std_20": amt_log_std_20.astype("float32"),
        "liq_std_20": std20_t.astype("float32"),
        "liq_std_10": std10_t.astype("float32"),
    }
    if mask is not None:
        for k in list(out.keys()):
            out[k] = out[k].where(mask).astype("float32")

    gap["ok"] = True
    gap["n_cols"] = len(cols)
    _cov_annotate(gap, out)
    del tov, amt, tov_pos, amt_pos, mean20_t, std20_t, mean10_t, std10_t, mean20_a, std20_a
    del log_amt
    gc.collect()
    return out, gap


def build_idx_panels(cal, cols, mask) -> tuple[dict, dict]:
    """CSI300/500/1000 weight pressure — passive flow / rebalance drift."""
    path = V2 / "index_members/index_weight_csi300_500_1000.parquet"
    gap = {
        "path": str(path),
        "family": "idx_weight_pressure",
        "economic_story": (
            "Index-weight pressure: CSI300/500/1000 constituent weights create "
            "persistent passive / smart-beta flow demand. Rising weight (drift or "
            "rebalance) attracts mechanical buying; falling weight frees selling. "
            "Not a textbook size/EP shell — weight is index-mandate exposure."
        ),
    }
    if not path.exists():
        gap["ok"] = False
        return {}, gap

    iw = pd.read_parquet(path)
    iw["trade_date"] = pd.to_datetime(iw["trade_date"])
    iw = iw[iw["trade_date"] >= (LOOKBACK_START - pd.Timedelta(days=40))]
    iw = iw[iw["index_code"].isin(["000300.SH", "000905.SH", "000852.SH"])]
    iw["bs"] = iw["con_code"].map(_to_baostock)
    iw = iw[iw["bs"].isin(cols)]
    iw["weight"] = pd.to_numeric(iw["weight"], errors="coerce")
    gap.update(
        {
            "ok": True,
            "n_rows": int(len(iw)),
            "n_instruments": int(iw["bs"].nunique()),
            "n_dates": int(iw["trade_date"].nunique()),
        }
    )

    # sum weights across indices (a name in 300+500 rare but possible historically)
    g = (
        iw.groupby(["trade_date", "bs"], sort=False)["weight"]
        .sum()
        .reset_index()
    )
    wide = (
        g.set_index(["trade_date", "bs"])["weight"]
        .unstack()
        .reindex(columns=cols)
        .astype("float32")
    )
    # monthly snapshots → daily ffill (PIT: weight known after month-end publish;
    # trade_date in file is snapshot date; treat as available that day close → next session
    # conservative: shift 1 session then ffill)
    wide = wide.reindex(index=cal)
    # first non-null month snapshot appears on its trade_date; shift 1 for T+1
    wide = wide.shift(1).ffill()
    if mask is not None:
        wide = wide.where(mask)

    w_delta_20 = wide.diff(20).astype("float32")
    w_delta_5 = wide.diff(5).astype("float32")
    # also per-index max weight (csi300 vs 500/1000)
    def _one_index(code: str) -> pd.DataFrame:
        sub = iw[iw["index_code"] == code]
        if sub.empty:
            return pd.DataFrame(np.nan, index=cal, columns=cols, dtype="float32")
        w = (
            sub.drop_duplicates(["trade_date", "bs"], keep="last")
            .set_index(["trade_date", "bs"])["weight"]
            .unstack()
            .reindex(columns=cols)
            .astype("float32")
            .reindex(index=cal)
            .shift(1)
            .ffill()
        )
        if mask is not None:
            w = w.where(mask)
        return w.astype("float32")

    w300 = _one_index("000300.SH")
    w500 = _one_index("000905.SH")
    w1000 = _one_index("000852.SH")

    out = {
        "idx_w": wide.astype("float32"),
        "idx_w_delta_20": w_delta_20,
        "idx_w_delta_5": w_delta_5,
        "abs_idx_w_delta_20": w_delta_20.abs().astype("float32"),
        "neg_idx_w": (-wide).astype("float32"),
        "neg_idx_w_delta_20": (-w_delta_20).astype("float32"),
        "idx_w300": w300,
        "idx_w500": w500,
        "idx_w1000": w1000,
        "idx_w300_delta_20": w300.diff(20).astype("float32"),
        "idx_w500_delta_20": w500.diff(20).astype("float32"),
        "idx_flag": (wide.notna() & (wide > 0)).astype("float32"),
    }
    # where no membership, keep NaN (honest — idx_flag zeros would inflate coverage)
    for k in list(out.keys()):
        if k == "idx_flag":
            # flag: 1 if in any index, else NaN (not 0) for hard-cov honesty on event口径
            out[k] = out[k].where(out[k] > 0).astype("float32")
        if mask is not None:
            out[k] = out[k].where(mask).astype("float32")

    for df in (out["idx_w"], out["idx_w_delta_20"], out["idx_w300"], out["idx_w500"]):
        _winsor_df(df)

    _cov_annotate(gap, out)
    del iw, g, wide, w300, w500, w1000, w_delta_20, w_delta_5
    gc.collect()
    return out, gap


def build_lev_panels(cal, cols, mask) -> tuple[dict, dict]:
    """debt_to_assets PIT deltas — leverage revision, NOT ROE/quality shell."""
    path = V2 / "financials_pit/financials_pit_tushare.parquet"
    gap = {
        "path": str(path),
        "family": "lev_revision",
        "economic_story": (
            "Balance-sheet leverage revision: PIT debt_to_assets *changes* capture "
            "refinancing / distress / deleveraging pressure denser than title news. "
            "Explicitly NOT ROE/gross-margin quality textbook shells (banned here)."
        ),
    }
    if not path.exists():
        gap["ok"] = False
        return {}, gap

    fin = pd.read_parquet(
        path,
        columns=["instrument_id", "available_at", "debt_to_assets", "end_date", "report_type"],
    )
    fin["available_at"] = pd.to_datetime(fin["available_at"], utc=True, errors="coerce")
    if getattr(fin["available_at"].dt, "tz", None) is not None:
        fin["available_at"] = fin["available_at"].dt.tz_convert("Asia/Shanghai").dt.tz_localize(None)
    else:
        fin["available_at"] = pd.to_datetime(fin["available_at"], errors="coerce")
    fin = fin[fin["instrument_id"].isin(cols)]
    fin = fin.dropna(subset=["available_at", "debt_to_assets"])
    fin = fin[fin["available_at"] >= (LOOKBACK_START - pd.Timedelta(days=400))]
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

    sub = fin[["avail_session", "instrument_id", "debt_to_assets"]].dropna()
    sub = sub.sort_values(["avail_session", "instrument_id"]).drop_duplicates(
        ["avail_session", "instrument_id"], keep="last"
    )
    lev = (
        sub.set_index(["avail_session", "instrument_id"])["debt_to_assets"]
        .unstack()
        .reindex(index=cal, columns=cols)
        .astype("float32")
        .ffill()
    )
    if mask is not None:
        lev = lev.where(mask)
    lev = _winsor_df(lev)

    out = {
        "lev_pit": lev.astype("float32"),
        "neg_lev_pit": (-lev).astype("float32"),
        "lev_delta_5": lev.diff(5).astype("float32"),
        "lev_delta_20": lev.diff(20).astype("float32"),
        "abs_lev_delta_20": lev.diff(20).abs().astype("float32"),
        "lev_delta_60": lev.diff(60).astype("float32"),
        "abs_lev_delta_60": lev.diff(60).abs().astype("float32"),
    }
    if mask is not None:
        for k in list(out.keys()):
            out[k] = out[k].where(mask).astype("float32")
    _cov_annotate(gap, out)
    del fin, sub, lev
    gc.collect()
    return out, gap


def build_candidates() -> list[dict]:
    """Fast grid: prioritize stability (neg CV) winners + idx/lev (untested)."""
    cands = []

    def add(expr: str, family: str, note: str = ""):
        L = leaves_in(expr)
        if not L or any(is_banned_leaf(x) for x in L):
            return
        if L.issubset(TEXTBOOK_LEAVES):
            return
        if is_fsr_family(expr) or is_title_sparse_primary(expr) or is_roe_quality_shell(expr):
            return
        cands.append({"expr": expr, "family": family, "note": note})

    def grid(leaves, family, transforms=None):
        transforms = transforms or (
            "{x}",
            "rank({x})",
            "neg({x})",
            "rank(neg({x}))",
            "ts_mean_10({x})",
            "rank(ts_mean_10({x}))",
            "ts_std_10({x})",
            "rank(ts_std_10({x}))",
            "delay_5({x})",
            "ts_max_5({x})",
        )
        for x in leaves:
            for tmpl in transforms:
                add(tmpl.format(x=x), family, tmpl)

    # PRIMARY — stability direction (partial run: GATE_OK on neg_liq_cv / neg_amt_cv)
    grid(
        (
            "neg_liq_cv_20",
            "neg_amt_cv_20",
            "neg_liq_burst_10",
            "liq_cv_20",
            "amt_cv_20",
            "liq_burst_10",
            "amt_burst_10",
            "liq_std_20",
            "amt_log_std_20",
            "abs_liq_accel_5",
        ),
        "liq_regime_instability",
    )
    add("mul(rank(neg_liq_cv_20), rank(neg_amt_cv_20))", "liq_regime_instability", "dual stable")
    add("mul(rank(neg_liq_cv_20), rank(liq_burst_10))", "liq_regime_instability", "stable x burst")
    add("mul(rank(neg_amt_cv_20), rank(amt_log_std_20))", "liq_regime_instability", "stable amt x logstd")

    # SECONDARY idx
    grid(
        (
            "idx_w",
            "idx_w_delta_20",
            "abs_idx_w_delta_20",
            "neg_idx_w",
            "neg_idx_w_delta_20",
            "idx_w300",
            "idx_w500",
            "idx_w1000",
            "idx_w300_delta_20",
            "idx_w500_delta_20",
        ),
        "idx_weight_pressure",
    )
    add("mul(rank(idx_w), rank(abs_idx_w_delta_20))", "idx_weight_pressure", "level x chg")
    add("mul(rank(idx_w300), rank(neg_idx_w_delta_20))", "idx_weight_pressure", "300 x fall")
    add("mul(rank(idx_w500), rank(idx_w_delta_20))", "idx_weight_pressure", "500 x rise")

    # TERTIARY lev
    grid(
        (
            "lev_pit",
            "neg_lev_pit",
            "lev_delta_20",
            "abs_lev_delta_20",
            "lev_delta_60",
            "abs_lev_delta_60",
            "lev_delta_5",
        ),
        "lev_revision",
    )

    # crosses
    add("mul(rank(neg_liq_cv_20), rank(idx_w))", "liq_x_idx", "stable liq x weight")
    add("mul(rank(neg_liq_cv_20), rank(idx_w_delta_20))", "liq_x_idx", "stable liq x w rise")
    add("mul(rank(neg_liq_cv_20), rank(neg_lev_pit))", "liq_x_lev", "stable liq x low lev")
    add("mul(rank(neg_liq_cv_20), rank(abs_lev_delta_20))", "liq_x_lev", "stable liq x lev shock")
    add("mul(rank(idx_w), rank(neg_lev_pit))", "liq_x_lev", "weight x low lev")  # mislabeled ok mixed

    seen = set()
    out = []
    for c in cands:
        if c["expr"] in seen:
            continue
        seen.add(c["expr"])
        # fix family for last cross if needed
        if c["note"] == "weight x low lev":
            c["family"] = "mixed:idx_w+neg_lev_pit"
        out.append(c)
    return out


def write_report(rows, meta, gate_ok_list):
    lines = []
    lines.append("# AI 因子 L1h：新原创机制族探索（非 FSR / 非 ann_title / 非 ROE 教科书壳）")
    lines.append("")
    lines.append("- **时间：** 2026-10-12（America/New_York）")
    lines.append("- **promotion_approved：** false；**密封：** 未开；**不交 Strategy 权重**")
    lines.append("- **trial_kind：** explore_gate / process")
    lines.append("- **本金主口径：** 60 万 / 100 万；主裁决=冲击+flat25")
    lines.append(
        "- **严格 GATE_OK：** ①非rank硬覆盖；②冲击+25bp@60万∧100万≥10%；"
        "③ICIR>0；④非 rank_fill；⑤非 title 稀疏主依赖；⑥非 FSR；⑦非 ROE/质量教科书壳"
    )
    lines.append(
        "- **禁止 / 已耗尽回避：** 广播、跌停主候选、小盘、教科书主线入主清单、FSR、"
        "ann_title 稀疏主依赖、ROE/gm 质量壳、cb_equity_pressure、lockup、rzrq、"
        "float_evt、ann_insider、密封、Strategy"
    )
    lines.append(
        f"- 账本：N {meta.get('ledger_N_before')} → {meta.get('ledger_N_after')} "
        f"（+{meta.get('ledger_N_new')}，explore_gate）"
    )
    lines.append(
        f"- 峰值 RSS：{meta.get('peak_rss_MB'):.0f} MB（上限 {meta.get('mem_cap_MB')}；"
        f"under_cap={meta.get('under_mem_cap')}）；运行 {meta.get('runtime_s')}s"
    )
    lines.append("")
    lines.append("## 机制故事（原创）")
    lines.append("")
    lines.append("### 1) liq_regime_instability（主族）")
    lines.append("")
    lines.append(
        "- **钱从谁来：** 做市/流动性提供者的逆向选择补偿。换手/成交额的 **CV / 突发度 / 加速度** "
        "刻画流动性体制是否稳定；体制不稳 → 报价变宽、冲击上升；突发后中大盘往往向常态回归。"
    )
    lines.append(
        "- **与 Amihud 的区别：** Amihud = |收益|/成交额 的 *水平* 非流动性；本族是流动性路径的 "
        "*波动体制*（CV/burst/accel），禁止用 turn_20 均值教科书壳入主清单。"
    )
    lines.append("- **失效条件：** 全市场流动性枯竭共振、涨跌停锁住成交、停牌、极端小盘（本批禁小盘）。")
    lines.append("- **PIT：** scratch turnover/amount 日频面板，中大盘 mask 后计算。")
    lines.append("")
    lines.append("### 2) idx_weight_pressure（次族）")
    lines.append("")
    lines.append(
        "- **钱从谁来：** CSI300/500/1000 被动与智能贝塔机械流。权重上升（漂移/再平衡）→ "
        "指数产品必须买；权重下降 → 卖压释放。不是市值/EP 教科书壳。"
    )
    lines.append("- **失效条件：** 指数规则大改、权重数据滞后、成分股停牌。"
    )
    lines.append("- **PIT：** 月度权重快照 shift(1)+ffill；非成分保持 NaN（诚实覆盖）。")
    lines.append("")
    lines.append("### 3) lev_revision（次族）")
    lines.append("")
    lines.append(
        "- PIT `debt_to_assets` *变化*：再融资/去杠杆/压力修订；**明确不是** ROE/毛利率质量教科书壳"
        "（本批禁 roe_/gm_）。"
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
    for key in ("liq_gap", "idx_gap", "lev_gap"):
        g = meta.get(key) or {}
        lines.append(f"### {key}")
        lines.append(f"- ok={g.get('ok')} path=`{g.get('path') or g.get('path_turnover')}`")
        if g.get("economic_story"):
            lines.append(f"- story: {g.get('economic_story')}")
        keys = [k for k in g.keys() if k.startswith("nonempty_")][:14]
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
    lines.append(
        "3. **未挖 FSR / ann_title 稀疏主依赖 / ROE 质量壳 / 广播 / 跌停主候选 / 小盘 / "
        "已耗尽 cb·lockup·rzrq·float_evt·ann_insider。**"
    )
    lines.append("4. **ICIR≤0 即使冲击正 → FAIL_ICIR。**")
    lines.append("5. **不开密封、不交 Strategy；`promotion_approved=false`。**")
    lines.append("")
    lines.append("## 产物路径")
    lines.append("")
    lines.append("- 报告：`output/alpha/AI_FACTOR_L1h_NEW_MECH_FAMILY_EXPLORE_ZH.md`")
    lines.append("- JSON：`output/ai_factor/l1h_new_mech_family/`")
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
    log("cleared structural; building L1h families", "n_cols", len(cols), "peak", peak)

    liq_panels, liq_gap = build_liq_panels(cal, cols, mask)
    panels.update(liq_panels)
    del liq_panels
    gc.collect()
    peak = max(peak, mem_mb())
    log(
        "liq done",
        "ok",
        liq_gap.get("ok"),
        "peak",
        peak,
        "nonempty_liq_cv_20",
        f"{liq_gap.get('nonempty_liq_cv_20', float('nan')):.4f}"
        if isinstance(liq_gap.get("nonempty_liq_cv_20"), float)
        else "—",
    )

    idx_panels, idx_gap = build_idx_panels(cal, cols, mask)
    panels.update(idx_panels)
    del idx_panels
    gc.collect()
    peak = max(peak, mem_mb())
    log(
        "idx done",
        "ok",
        idx_gap.get("ok"),
        "peak",
        peak,
        "nonempty_idx_w",
        f"{idx_gap.get('nonempty_idx_w', float('nan')):.4f}"
        if isinstance(idx_gap.get("nonempty_idx_w"), float)
        else "—",
    )

    lev_panels, lev_gap = build_lev_panels(cal, cols, mask)
    panels.update(lev_panels)
    del lev_panels
    gc.collect()
    peak = max(peak, mem_mb())
    log("lev done", "ok", lev_gap.get("ok"), "n_panels", len(panels), "peak", peak)

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
                "fail_roe": 0,
                "error": 0,
            },
        )
        fam_counts[fam]["n"] += 1
        norank_expr = strip_rank(expr)
        try:
            if is_title_sparse_primary(expr) or is_fsr_family(expr) or is_roe_quality_shell(expr):
                if is_fsr_family(expr):
                    reason = "FAIL_FSR_BANNED"
                    fam_counts[fam]["fail_fsr"] += 1
                elif is_roe_quality_shell(expr):
                    reason = "FAIL_ROE_QUALITY_SHELL"
                    fam_counts[fam]["fail_roe"] += 1
                else:
                    reason = "FAIL_TITLE_SPARSE_PRIMARY"
                    fam_counts[fam]["fail_title"] += 1
                bump_fail(reason)
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
            f"l1h_new_mech_family;family={fam};verdict={row.get('verdict')};"
            f"rank_fill={row.get('rank_fill_cov')};cov_nr={row.get('survive_coverage_norank')};"
            f"process_not_sealed;promotion_approved=false"
        )
        for path in (run_ledger, main_ledger):
            append_attempt(
                engine="l1h_new_mech_family",
                seed=SEED,
                universe="midlarge_top1500_or_csi300_500",
                cost=0.0025,
                window="explore_20240603_to_latest_l1h_new_mech",
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
        "短清单 v2c 先验含 ann_insider + L1f FSR 族；本批禁 FSR 新挖、禁 ann_title、"
        "禁 ROE/gm 质量壳、禁已耗尽族。仅 GATE_OK 可后续并列扩容（仍不密封、不交 Strategy）。"
        "并行轨 gm→v2d 未在本脚本改动。"
    )
    meta = {
        "mode": "l1h_new_mech_family_explore",
        "promotion_approved": False,
        "sealed_executed": False,
        "trial_kind": "explore_gate",
        "ann_title_only": True,
        "invented_body": False,
        "n_candidates": len(cands),
        "n_gate_ok": n_gate_ok,
        "fail_reason_counts": fail_display,
        "family_counts": fam_counts,
        "liq_gap": liq_gap,
        "idx_gap": idx_gap,
        "lev_gap": lev_gap,
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
        "primary_family": "liq_regime_instability",
        "secondary_families": ["idx_weight_pressure", "lev_revision"],
        "banned_as_new_discovery": [
            "FSR",
            "float_share_ratio",
            "ann_title_sparse_primary",
            "ROE_quality_shell",
            "broadcast",
            "LD_primary",
            "textbook_mainline",
            "rzrq",
            "cb_equity_pressure",
            "lockup",
            "float_evt",
            "ann_insider",
            "amihud_textbook",
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
