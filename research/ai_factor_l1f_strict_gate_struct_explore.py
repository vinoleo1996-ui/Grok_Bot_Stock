#!/usr/bin/env python3
"""L1f strict-gate structural explore after v2b.

Hard GATE_OK requires ALL of:
  1) Hard coverage on non-rank event口径 (no rank_fill illusion)
  2) impact+flat25 @ 60万 AND 100万 ≥ 10%
  3) ICIR > 0
  4) Not rank_fill hallucination
  5) Not title-sparsity primary dependency

Prior fails avoided (not rediscovered as new):
  - rzrq (ICIR≤0), float rank_* (demoted), lockup_days_to / sparse ann
  - shortlist v2b ann_insider kept as prior only

New families preferred: dense continuous CS panels —
  ocf_to_profit quality, float_share_ratio (continuous, NOT unlock evt),
  dv_ttm yield, dragon_tiger net density (expect sparse), st flag (对照).

Ban: broadcast, LD primary, small-cap, textbook mainline, sealed, Strategy.
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
SCRATCH = Path("/workspace/scratch/tic")
OUT_DIR = ROOT / "output/ai_factor/l1f_strict_gate_struct"
REPORT = ROOT / "output/alpha/AI_FACTOR_L1f_STRICT_GATE_STRUCT_EXPLORE_ZH.md"

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
        # prior fails — do not rediscover as primary
        "rz_intensity", "rq_intensity", "rzrq_intensity",
        "rz_bal", "rq_bal", "rz_delta_5", "rz_delta_10", "rq_delta_5", "rzrq_delta_5",
        "float_evt_20", "float_evt_60", "float_ratio_20", "float_ratio_60", "float_evt_flag",
        "lockup_days_to", "lockup_S_20",
    }
)
BANNED_PREFIXES = (
    "mkt_", "etf_", "if_basis", "limit_down_", "ld_", "ann_",
    "rz_", "rq_", "rzrq_", "float_evt", "float_ratio_", "lockup_",
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
    print(f"[l1f_strict {time.time()-t0:5.0f}s {mem_mb():.0f}MB]", *a, flush=True)


def leaves_in(expr: str) -> set[str]:
    return {t for t in re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", expr) if t not in OPS}


def is_banned_leaf(name: str) -> bool:
    if name in BANNED_EXACT or name in TEXTBOOK_LEAVES:
        return True
    return any(name.startswith(p) for p in BANNED_PREFIXES)


def is_title_sparse_primary(expr: str) -> bool:
    L = leaves_in(expr)
    return bool(L) and all(x.startswith("ann_") for x in L)


def family_of(expr: str) -> str:
    L = sorted(leaves_in(expr))
    if not L:
        return "unknown"
    if all(x.startswith("ocf_") for x in L):
        return "ocf_quality"
    if all(x.startswith("fsr") or x.startswith("float_share") for x in L):
        return "float_share_ratio"
    if all(x.startswith("dv_") for x in L):
        return "dv_yield"
    if all(x.startswith("dt_") for x in L):
        return "dragon_tiger"
    if all(x.startswith("st_") for x in L):
        return "st_structure"
    if any(x.startswith("ocf_") for x in L) and any(
        x.startswith("fsr") or x.startswith("float_share") for x in L
    ):
        return "ocf_x_fsr"
    if any(x.startswith("ocf_") for x in L) and any(x.startswith("dv_") for x in L):
        return "ocf_x_dv"
    return "mixed:" + "+".join(L[:3])


def strip_rank(expr: str) -> str:
    """Peel outer rank()/zscore() wrappers for honest coverage口径."""
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


def build_ocf_panels(cal, cols, mask) -> tuple[dict, dict]:
    path = V2 / "financials_pit/ocf_to_profit_pit_daily_tushare.parquet"
    gap = {"path": str(path), "family": "ocf_quality"}
    if not path.exists():
        gap["ok"] = False
        gap["error"] = "missing"
        return {}, gap
    ocf = pd.read_parquet(
        path,
        columns=["trade_date", "instrument_id", "ocf_to_profit", "ocf_to_profit_attr"],
        filters=[("trade_date", ">=", LOOKBACK_START - pd.Timedelta(days=5))],
    )
    ocf["trade_date"] = pd.to_datetime(ocf["trade_date"])
    ocf = ocf[ocf["instrument_id"].isin(cols)]
    gap.update(
        {
            "ok": True,
            "n_rows": int(len(ocf)),
            "n_instruments": int(ocf["instrument_id"].nunique()),
        }
    )

    def pivot_one(valcol: str) -> pd.DataFrame:
        sub = ocf[["trade_date", "instrument_id", valcol]].dropna(subset=[valcol])
        sub = sub.sort_values(["trade_date", "instrument_id"]).drop_duplicates(
            ["trade_date", "instrument_id"], keep="last"
        )
        wide = (
            sub.set_index(["trade_date", "instrument_id"])[valcol]
            .unstack()
            .reindex(index=cal, columns=cols)
            .astype("float32")
        )
        # PIT daily already; light ffill for holiday gaps only
        wide = wide.ffill(limit=3)
        if mask is not None:
            wide = wide.where(mask)
        # winsorize extremes for stability (keep signal, kill ±1000 outliers)
        arr = wide.to_numpy(copy=True)
        lo = np.nanpercentile(arr, 0.5)
        hi = np.nanpercentile(arr, 99.5)
        arr = np.clip(arr, lo, hi)
        return pd.DataFrame(arr, index=cal, columns=cols, dtype="float32")

    out = {
        "ocf_to_profit": pivot_one("ocf_to_profit"),
        "ocf_to_profit_attr": pivot_one("ocf_to_profit_attr"),
    }
    out["ocf_delta_5"] = out["ocf_to_profit"].diff(5).astype("float32")
    out["ocf_delta_10"] = out["ocf_to_profit"].diff(10).astype("float32")
    out["ocf_abs"] = out["ocf_to_profit"].abs().astype("float32")
    if mask is not None:
        for k in ("ocf_delta_5", "ocf_delta_10", "ocf_abs"):
            out[k] = out[k].where(mask).astype("float32")
    for k, df in out.items():
        gap[f"nonempty_{k}"] = float((df.notna() & (df.abs() > 1e-12)).to_numpy().mean())
        gap[f"mean_names_{k}"] = float((df.notna() & (df.abs() > 1e-12)).sum(axis=1).mean())
    del ocf
    gc.collect()
    return out, gap


def build_fsr_dv_panels(cal, cols, mask) -> tuple[dict, dict, dict]:
    path = V2 / "valuation/daily_basic_valuation_tushare.parquet"
    gap_fsr = {"path": str(path), "family": "float_share_ratio"}
    gap_dv = {"path": str(path), "family": "dv_yield"}
    if not path.exists():
        gap_fsr["ok"] = False
        gap_dv["ok"] = False
        return {}, gap_fsr, gap_dv
    val = pd.read_parquet(
        path,
        columns=["trade_date", "instrument_id", "float_share", "total_share", "dv_ttm"],
        filters=[("trade_date", ">=", LOOKBACK_START - pd.Timedelta(days=5))],
    )
    val["trade_date"] = pd.to_datetime(val["trade_date"])
    val = val[val["instrument_id"].isin(cols)]
    with np.errstate(divide="ignore", invalid="ignore"):
        val["fsr"] = (
            val["float_share"] / val["total_share"].replace(0, np.nan)
        ).astype("float64")
    gap_fsr.update(
        {"ok": True, "n_rows": int(len(val)), "n_instruments": int(val["instrument_id"].nunique())}
    )
    gap_dv.update(
        {"ok": True, "n_rows": int(len(val)), "n_instruments": int(val["instrument_id"].nunique())}
    )

    def pivot_val(col: str) -> pd.DataFrame:
        sub = val[["trade_date", "instrument_id", col]].dropna(subset=[col])
        sub = sub.sort_values(["trade_date", "instrument_id"]).drop_duplicates(
            ["trade_date", "instrument_id"], keep="last"
        )
        wide = (
            sub.set_index(["trade_date", "instrument_id"])[col]
            .unstack()
            .reindex(index=cal, columns=cols)
            .astype("float32")
        )
        wide = wide.ffill(limit=5)
        if mask is not None:
            wide = wide.where(mask)
        return wide.astype("float32")

    fsr = pivot_val("fsr")
    # clip to [0,1]
    fsr = fsr.clip(lower=0.0, upper=1.0)
    dv = pivot_val("dv_ttm")
    # dv_ttm often in percent; keep as-is for ranking
    out_fsr = {
        "fsr": fsr,
        "fsr_delta_5": fsr.diff(5).astype("float32"),
        "fsr_delta_20": fsr.diff(20).astype("float32"),
        "neg_fsr": (-fsr).astype("float32"),
    }
    out_dv = {
        "dv_ttm": dv,
        "dv_delta_5": dv.diff(5).astype("float32"),
        "dv_delta_20": dv.diff(20).astype("float32"),
        "neg_dv_ttm": (-dv).astype("float32"),
    }
    if mask is not None:
        for d in (out_fsr, out_dv):
            for k in list(d.keys()):
                d[k] = d[k].where(mask).astype("float32")
    for k, df in out_fsr.items():
        gap_fsr[f"nonempty_{k}"] = float((df.notna() & (df.abs() > 1e-12)).to_numpy().mean())
        gap_fsr[f"mean_names_{k}"] = float((df.notna() & (df.abs() > 1e-12)).sum(axis=1).mean())
    for k, df in out_dv.items():
        gap_dv[f"nonempty_{k}"] = float((df.notna() & (df.abs() > 1e-12)).to_numpy().mean())
        gap_dv[f"mean_names_{k}"] = float((df.notna() & (df.abs() > 1e-12)).sum(axis=1).mean())
    del val
    gc.collect()
    out = {**out_fsr, **out_dv}
    return out, gap_fsr, gap_dv


def build_dragon_panels(cal, cols, mask) -> tuple[dict, dict]:
    path = V2 / "dragon_tiger/top_list.parquet"
    gap = {"path": str(path), "family": "dragon_tiger"}
    if not path.exists():
        gap["ok"] = False
        return {}, gap
    dt = pd.read_parquet(
        path,
        columns=["trade_date", "ts_code", "net_amount", "l_buy", "l_sell", "available_at"],
    )
    dt["trade_date"] = pd.to_datetime(dt["trade_date"], errors="coerce")
    if "available_at" in dt.columns:
        av = pd.to_datetime(dt["available_at"], errors="coerce")
        if getattr(av.dt, "tz", None) is not None:
            avail = av.dt.tz_convert("Asia/Shanghai").dt.normalize().dt.tz_localize(None)
        else:
            avail = av.dt.normalize()
        # usable next session after available_at
        dt["avail_date"] = avail + pd.Timedelta(days=1)
    else:
        dt["avail_date"] = dt["trade_date"] + pd.Timedelta(days=1)
    dt["bs"] = dt["ts_code"].map(_to_baostock)
    dt = dt[dt["bs"].isin(cols)]
    dt = dt[
        (dt["avail_date"] >= LOOKBACK_START - pd.Timedelta(days=40))
        & (dt["avail_date"] <= cal.max() + pd.Timedelta(days=5))
    ]
    gap.update({"ok": True, "n_events": int(len(dt)), "n_instruments": int(dt["bs"].nunique())})

    col_index = {c: i for i, c in enumerate(cols)}
    cal_np = cal.values.astype("datetime64[ns]")
    T, N = len(cal), len(cols)
    net = np.zeros((T, N), dtype=np.float32)
    buy = np.zeros((T, N), dtype=np.float32)
    flag = np.zeros((T, N), dtype=np.float32)
    for row in dt.itertuples(index=False):
        j = col_index.get(row.bs)
        if j is None:
            continue
        d = pd.Timestamp(row.avail_date).normalize()
        i = int(np.searchsorted(cal_np, np.datetime64(d), side="left"))
        if i >= T:
            continue
        if i < T and cal_np[i] < np.datetime64(d):
            i += 1
            if i >= T:
                continue
        na = float(row.net_amount) if row.net_amount is not None and np.isfinite(row.net_amount) else 0.0
        lb = float(row.l_buy) if row.l_buy is not None and np.isfinite(row.l_buy) else 0.0
        net[i, j] += np.float32(na)
        buy[i, j] += np.float32(lb)
        flag[i, j] = 1.0
    del dt
    gc.collect()
    net_df = pd.DataFrame(net, index=cal, columns=cols, dtype="float32")
    buy_df = pd.DataFrame(buy, index=cal, columns=cols, dtype="float32")
    flag_df = pd.DataFrame(flag, index=cal, columns=cols, dtype="float32")
    out = {
        "dt_net_5": net_df.rolling(5, min_periods=1).sum().astype("float32"),
        "dt_net_10": net_df.rolling(10, min_periods=1).sum().astype("float32"),
        "dt_buy_5": buy_df.rolling(5, min_periods=1).sum().astype("float32"),
        "dt_flag_5": flag_df.rolling(5, min_periods=1).sum().astype("float32"),
        "dt_flag": flag_df,
    }
    if mask is not None:
        for k in list(out.keys()):
            out[k] = out[k].where(mask).astype("float32")
    for k, df in out.items():
        gap[f"nonempty_{k}"] = float((df.notna() & (df.abs() > 1e-12)).to_numpy().mean())
        gap[f"mean_names_{k}"] = float((df.notna() & (df.abs() > 1e-12)).sum(axis=1).mean())
    del net, buy, flag, net_df, buy_df, flag_df
    gc.collect()
    return out, gap


def build_st_panels(cal, cols, mask) -> tuple[dict, dict]:
    path = V2 / "st_flags/is_st_daily_2018_2026.parquet"
    gap = {"path": str(path), "family": "st_structure"}
    if not path.exists():
        gap["ok"] = False
        return {}, gap
    st = pd.read_parquet(path)
    st["trade_date"] = pd.to_datetime(st["trade_date"])
    st = st[st["instrument_id"].isin(cols)]
    st = st[
        (st["trade_date"] >= LOOKBACK_START - pd.Timedelta(days=5))
        & (st["trade_date"] <= cal.max() + pd.Timedelta(days=5))
    ]
    gap.update({"ok": True, "n_rows": int(len(st)), "n_instruments": int(st["instrument_id"].nunique())})
    wide = (
        st.drop_duplicates(["trade_date", "instrument_id"], keep="last")
        .set_index(["trade_date", "instrument_id"])["is_st_at_open"]
        .unstack()
        .reindex(index=cal, columns=cols)
    )
    # True/False/NA → float; non-ST days are False in source only for ST rows?
    # The file appears to store only ST=True rows; treat missing as 0 after mask
    flag = wide.fillna(False).astype("float32")
    if mask is not None:
        flag = flag.where(mask)
    out = {
        "st_flag": flag.astype("float32"),
        "st_count_20": flag.rolling(20, min_periods=1).sum().astype("float32"),
        "neg_st_flag": (-flag).astype("float32"),
    }
    if mask is not None:
        for k in list(out.keys()):
            out[k] = out[k].where(mask).astype("float32")
    for k, df in out.items():
        gap[f"nonempty_{k}"] = float((df.notna() & (df.abs() > 1e-12)).to_numpy().mean())
        gap[f"mean_names_{k}"] = float((df.notna() & (df.abs() > 1e-12)).sum(axis=1).mean())
    del st, wide
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
        cands.append({"expr": expr, "family": family, "note": note})

    # --- ocf quality (dense continuous) ---
    for x in ("ocf_to_profit", "ocf_to_profit_attr", "ocf_abs"):
        add(x, "ocf_quality", "raw")
        add(f"rank({x})", "ocf_quality", "rank")
        add(f"neg({x})", "ocf_quality", "neg")
        add(f"rank(neg({x}))", "ocf_quality", "rank neg")
        add(f"zscore({x})", "ocf_quality", "zscore")
        add(f"ts_delta_5({x})", "ocf_quality", "delta5")
        add(f"rank(ts_delta_5({x}))", "ocf_quality", "rank delta5")
        add(f"abs(ts_delta_5({x}))", "ocf_quality", "abs delta5")
        add(f"ts_std_10({x})", "ocf_quality", "ts_std10")
        add(f"rank(ts_std_10({x}))", "ocf_quality", "rank ts_std10")
        add(f"ts_mean_10({x})", "ocf_quality", "ts_mean10")
        add(f"rank(ts_mean_10({x}))", "ocf_quality", "rank ts_mean10")
        add(f"ts_mean_20({x})", "ocf_quality", "ts_mean20")
        add(f"delay_5({x})", "ocf_quality", "delay5")
        add(f"abs(ts_std_10(ts_delta_5({x})))", "ocf_quality", "vol of delta")
        add(f"rank(abs(ts_std_10(ts_delta_5({x}))))", "ocf_quality", "rank vol delta")

    for x in ("ocf_delta_5", "ocf_delta_10"):
        add(x, "ocf_quality", "prebuilt delta")
        add(f"rank({x})", "ocf_quality", "rank prebuilt")
        add(f"neg({x})", "ocf_quality", "neg prebuilt")
        add(f"abs({x})", "ocf_quality", "abs prebuilt")
        add(f"ts_std_10({x})", "ocf_quality", "std delta")
        add(f"rank(ts_std_10({x}))", "ocf_quality", "rank std delta")

    # --- continuous float share ratio (NOT unlock event) ---
    for x in ("fsr", "neg_fsr"):
        add(x, "float_share_ratio", "raw fsr")
        add(f"rank({x})", "float_share_ratio", "rank")
        add(f"zscore({x})", "float_share_ratio", "zscore")
        add(f"ts_delta_5({x})", "float_share_ratio", "delta5")
        add(f"rank(ts_delta_5({x}))", "float_share_ratio", "rank delta5")
        add(f"ts_std_10({x})", "float_share_ratio", "ts_std")
        add(f"rank(ts_std_10({x}))", "float_share_ratio", "rank ts_std")
        add(f"ts_mean_10({x})", "float_share_ratio", "ts_mean")
        add(f"rank(ts_mean_10({x}))", "float_share_ratio", "rank ts_mean")
        add(f"delay_5({x})", "float_share_ratio", "delay5")
        add(f"abs(ts_std_10(ts_delta_5({x})))", "float_share_ratio", "vol delta")

    for x in ("fsr_delta_5", "fsr_delta_20"):
        add(x, "float_share_ratio", "prebuilt delta")
        add(f"rank({x})", "float_share_ratio", "rank")
        add(f"abs({x})", "float_share_ratio", "abs")
        add(f"neg({x})", "float_share_ratio", "neg")
        add(f"ts_std_10({x})", "float_share_ratio", "std")
        add(f"rank(ts_std_10({x}))", "float_share_ratio", "rank std")

    # --- dividend yield continuous ---
    for x in ("dv_ttm", "neg_dv_ttm"):
        add(x, "dv_yield", "raw dv")
        add(f"rank({x})", "dv_yield", "rank")
        add(f"zscore({x})", "dv_yield", "zscore")
        add(f"ts_delta_5({x})", "dv_yield", "delta5")
        add(f"rank(ts_delta_5({x}))", "dv_yield", "rank delta5")
        add(f"ts_std_10({x})", "dv_yield", "ts_std")
        add(f"rank(ts_std_10({x}))", "dv_yield", "rank ts_std")
        add(f"ts_mean_10({x})", "dv_yield", "ts_mean")
        add(f"rank(ts_mean_10({x}))", "dv_yield", "rank ts_mean")
        add(f"delay_5({x})", "dv_yield", "delay5")
        add(f"abs(ts_std_10(ts_delta_5({x})))", "dv_yield", "vol delta")

    for x in ("dv_delta_5", "dv_delta_20"):
        add(x, "dv_yield", "prebuilt delta")
        add(f"rank({x})", "dv_yield", "rank")
        add(f"abs({x})", "dv_yield", "abs")
        add(f"neg({x})", "dv_yield", "neg")
        add(f"ts_std_10({x})", "dv_yield", "std")
        add(f"rank(ts_std_10({x}))", "dv_yield", "rank std")

    # --- dragon tiger (likely sparse; document) ---
    for x in ("dt_net_5", "dt_net_10", "dt_buy_5", "dt_flag_5"):
        add(x, "dragon_tiger", "dt density")
        add(f"rank({x})", "dragon_tiger", "rank")
        add(f"neg({x})", "dragon_tiger", "neg")
        add(f"rank(neg({x}))", "dragon_tiger", "rank neg")
        add(f"ts_std_10({x})", "dragon_tiger", "ts_std")
        add(f"rank(ts_std_10({x}))", "dragon_tiger", "rank ts_std")
        add(f"abs(ts_std_10(ts_delta_5({x})))", "dragon_tiger", "vol delta")
    add("dt_flag", "dragon_tiger", "same-day")
    add("rank(dt_flag)", "dragon_tiger", "rank flag")
    add("neg(dt_flag)", "dragon_tiger", "neg flag")

    # --- ST structure (对照 / likely sparse) ---
    add("st_flag", "st_structure", "st flag")
    add("neg_st_flag", "st_structure", "avoid ST")
    add("rank(neg_st_flag)", "st_structure", "rank avoid ST")
    add("st_count_20", "st_structure", "st count20")
    add("neg(st_count_20)", "st_structure", "neg count")
    add("rank(neg(st_count_20))", "st_structure", "rank neg count")

    # light crosses (dense x dense)
    add("mul(rank(ocf_to_profit), rank(fsr))", "ocf_x_fsr", "ocf x fsr")
    add("mul(rank(ocf_to_profit), rank(neg_fsr))", "ocf_x_fsr", "ocf x low fsr")
    add("mul(rank(neg(ocf_to_profit)), rank(fsr))", "ocf_x_fsr", "low ocf x fsr")
    add("mul(rank(ocf_to_profit), rank(dv_ttm))", "ocf_x_dv", "ocf x dv")
    add("mul(rank(ocf_to_profit), rank(neg_dv_ttm))", "ocf_x_dv", "ocf x low dv")
    add("mul(rank(ts_mean_10(ocf_to_profit)), rank(ts_mean_10(fsr)))", "ocf_x_fsr", "smooth cross")
    add(
        "mul(rank(ts_std_10(ocf_to_profit)), rank(abs(fsr_delta_5)))",
        "ocf_x_fsr",
        "ocf vol x fsr chg",
    )

    seen = set()
    out = []
    for c in cands:
        if c["expr"] in seen:
            continue
        seen.add(c["expr"])
        out.append(c)
    return out


def write_report(rows, meta, gate_ok_list, v2b_note):
    lines = []
    lines.append("# AI 因子 L1f：严格闸门结构叶探索（v2b 之后）")
    lines.append("")
    lines.append("- **时间：** 2026-10-12（America/New_York）")
    lines.append("- **promotion_approved：** false；**密封：** 未开；**不交 Strategy 权重**")
    lines.append("- **trial_kind：** explore_gate / process")
    lines.append("- **本金主口径：** 60 万 / 100 万；主裁决=冲击+flat25")
    lines.append(
        "- **严格 GATE_OK 条件（须同时满足）：** "
        "①非rank硬覆盖；②冲击+25bp@60万∧100万≥10%；③ICIR>0；"
        "④非 rank_fill 幻觉；⑤非 title 稀疏主依赖"
    )
    lines.append(
        "- **禁止：** 广播叶、跌停主候选、小盘、教科书主线、密封、Strategy；"
        "不重挖 rzrq/float_evt/lockup_days_to/ann 稀疏主依赖"
    )
    lines.append("- **公告：** 本批不以 ann title 为主叶；`invented_body=false`")
    lines.append(
        f"- 账本：N {meta.get('ledger_N_before')} → {meta.get('ledger_N_after')} "
        f"（+{meta.get('ledger_N_new')}，explore_gate）"
    )
    lines.append(
        f"- 峰值 RSS：{meta.get('peak_rss_MB'):.0f} MB（上限 {meta.get('mem_cap_MB')}；"
        f"under_cap={meta.get('under_mem_cap')}）；运行 {meta.get('runtime_s')}s"
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
    for key in ("ocf_gap", "fsr_gap", "dv_gap", "dt_gap", "st_gap"):
        g = meta.get(key) or {}
        lines.append(f"### {key}")
        lines.append(f"- ok={g.get('ok')} path=`{g.get('path')}`")
        keys = [k for k in g.keys() if k.startswith("nonempty_")][:8]
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
    lines.append("## 近闸对照（覆盖硬过 ∧ 冲击过但 ICIR≤0，或 ICIR>0 但冲击未过）")
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
    )[:20]
    if not near:
        lines.append("*无。*")
    else:
        lines.append("| 表达式 | flat25 | 60万+25bp | ICIR | nonempty | 裁决 |")
        lines.append("|---|---:|---:|---:|---:|---|")
        for r in near:
            m = r.get("metrics") or {}
            cov = r.get("coverage_norank") or {}
            lines.append(
                f"| `{r.get('expr')}` | {fmt_pct(m.get('flat25'))} | "
                f"{fmt_pct(m.get('imp60_p25'))} | {fmt_f(m.get('icir'), 3)} | "
                f"{fmt_f(cov.get('nonempty_rate'), 4)} | {r.get('verdict')} |"
            )
    lines.append("")
    lines.append("## 与短清单 v2b 并列")
    lines.append("")
    lines.append(v2b_note)
    lines.append("")
    lines.append(f"- **本批 GATE_OK 是否扩容主短清单：** {meta.get('shortlist_grows_beyond_v2b')}")
    lines.append(f"- **建议并入主短清单的新叶数：** {meta.get('n_gate_ok')}")
    lines.append("")
    lines.append("## 诚实裁决")
    lines.append("")
    lines.append(
        f"1. **严格存活：** GATE_OK={meta.get('n_gate_ok')}/{meta.get('n_candidates')}；"
        f"失败拆解见上表。"
    )
    lines.append(
        "2. **覆盖诚实：** 一律用 strip_rank 非rank 口径；rank_fill → FAIL_RANK_FILL，不进 GATE_OK。"
    )
    lines.append(
        "3. **ICIR：** 冲击正但 ICIR≤0 → FAIL_ICIR（同 rzrq 教训），不作稳健主候选。"
    )
    lines.append(
        "4. **先验回避：** 未重挖 rzrq / float_evt unlock / lockup_days_to / ann 稀疏主依赖；"
        "v2b ann_insider 仅作并列先验。"
    )
    lines.append("5. **不开密封、不交 Strategy**；`promotion_approved=false`。")
    lines.append("")
    lines.append("## 产物路径")
    lines.append("")
    lines.append("- 报告：`output/alpha/AI_FACTOR_L1f_STRICT_GATE_STRUCT_EXPLORE_ZH.md`")
    lines.append("- JSON：`output/ai_factor/l1f_strict_gate_struct/`")
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

    log("loading base panels (for midlarge mask only)")
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
    log("cleared structural panels; building L1f dense families", "peak", peak)

    ocf_panels, ocf_gap = build_ocf_panels(cal, cols, mask)
    panels.update(ocf_panels)
    del ocf_panels
    gc.collect()
    peak = max(peak, mem_mb())
    log("ocf done", "peak", peak, "ok", ocf_gap.get("ok"))

    fsr_dv, fsr_gap, dv_gap = build_fsr_dv_panels(cal, cols, mask)
    panels.update(fsr_dv)
    del fsr_dv
    gc.collect()
    peak = max(peak, mem_mb())
    log("fsr/dv done", "peak", peak)

    dt_panels, dt_gap = build_dragon_panels(cal, cols, mask)
    panels.update(dt_panels)
    del dt_panels
    gc.collect()
    peak = max(peak, mem_mb())
    log("dragon done", "peak", peak, "ok", dt_gap.get("ok"))

    st_panels, st_gap = build_st_panels(cal, cols, mask)
    panels.update(st_panels)
    del st_panels
    gc.collect()
    peak = max(peak, mem_mb())
    log("st done; n_panels", len(panels), "peak", peak)

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
                "error": 0,
            },
        )
        fam_counts[fam]["n"] += 1
        norank_expr = strip_rank(expr)
        try:
            if is_title_sparse_primary(expr):
                bump_fail("FAIL_TITLE_SPARSE_PRIMARY")
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
                    "verdict": "FAIL_TITLE_SPARSE_PRIMARY",
                    "promotion_approved": False,
                    "trial_kind": "explore_gate",
                    "norank_expr": norank_expr,
                }
                rows.append(row)
                fit = None
            else:
                tup = _seed_to_tuple(expr)
                fac = apply_expr(parse_expr(to_nested_tuple(tup)), panels).astype("float32")
                # norank factor for honest coverage
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
                # also: if rank nonempty >> norank nonempty by large margin
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
            f"l1f_strict_gate_struct;family={fam};verdict={row.get('verdict')};"
            f"rank_fill={row.get('rank_fill_cov')};cov_nr={row.get('survive_coverage_norank')};"
            f"process_not_sealed;promotion_approved=false"
        )
        for path in (run_ledger, main_ledger):
            append_attempt(
                engine="l1f_strict_gate_struct",
                seed=SEED,
                universe="midlarge_top1500_or_csi300_500",
                cost=0.0025,
                window="explore_20240603_to_latest_l1f_strict",
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
                expr[:52],
                "60+25",
                fmt_pct(fit) if fit is not None else "—",
                "peak",
                peak,
            )
        if mem_mb() > MEM_CAP_MB - 150:
            gc.collect()

    # clean fail map: GATE_OK counted via bump then kept — move out of fail table display
    n_gate_ok = len(gate_ok_list)
    # recount GATE_OK properly in fail_reason_counts for display
    fail_display = {k: v for k, v in fail_reason_counts.items() if k != "GATE_OK"}
    # Ensure GATE_OK not double-counted wrongly: we bumped GATE_OK into fail_reason_counts
    # Remove it from fail_display (already done). Also fix overcount if we bumped on success.
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

    grows = bool(n_gate_ok > 0)
    v2b_note = (
        "短清单 v2b 先验仍 N=2：`rank(ts_std_10(ann_insider_dec_5))`（GATE_OK 覆盖硬过）+ "
        "`abs(ts_std_10(ts_delta_5(ann_insider_dec_5)))`（deepen sparse_warn）。"
        "本批不重挖 ann；新 GATE_OK 才谈扩容。"
    )
    meta = {
        "mode": "l1f_strict_gate_struct_explore",
        "promotion_approved": False,
        "sealed_executed": False,
        "trial_kind": "explore_gate",
        "ann_title_only": True,
        "invented_body": False,
        "n_candidates": len(cands),
        "n_gate_ok": n_gate_ok,
        "fail_reason_counts": fail_display,
        "family_counts": fam_counts,
        "ocf_gap": ocf_gap,
        "fsr_gap": fsr_gap,
        "dv_gap": dv_gap,
        "dt_gap": dt_gap,
        "st_gap": st_gap,
        "ledger_N_before": n_before,
        "ledger_N_after": n_after,
        "ledger_N_new": n_after - n_before,
        "peak_rss_MB": peak,
        "mem_cap_MB": MEM_CAP_MB,
        "under_mem_cap": peak < MEM_CAP_MB,
        "runtime_s": round(time.time() - t0, 1),
        "gate_ok_exprs": [r["expr"] for r in gate_ok_list],
        "shortlist_grows_beyond_v2b": grows,
        "v2b_prior_n": 2,
        "prior_avoided": [
            "rzrq_ICIR_le_0",
            "float_rank_fill_demote",
            "lockup_days_to_sparse",
            "ann_title_sparse_primary",
            "broadcast",
            "LD_primary",
            "textbook",
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
    write_report(rows, meta, gate_ok_list, v2b_note)
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
        "grows_v2b",
        grows,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
