#!/usr/bin/env python3
"""L1e hard-coverage structural explore — NOT title-sparsity dependent.

Families preferred:
  - rzrq / margin financing structure (stock-level, mid/large)
  - share-float event density calendars (broader than lockup_S_*)
  - ex-dividend proximity calendars (expect FAIL_SPARSE often)

Hard coverage gate (same as L1d): nonempty≥8%, mean_event_names≥40, frac_days≥20 ≥50%.
FAIL_SPARSE → not shortlisted. Cost + CS variation + 60/100万 impact+flat25.
Ban: broadcast, LD primary, small-cap, textbook mainline, sealed, Strategy, invented ann body.
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
OUT_DIR = ROOT / "output/ai_factor/l1e_hard_cov_struct"
REPORT = ROOT / "output/alpha/AI_FACTOR_L1e_HARD_COV_STRUCT_EXPLORE_ZH.md"

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
    }
)
BANNED_PREFIXES = ("mkt_", "etf_", "if_basis", "limit_down_", "ld_", "ann_")

t0 = 0.0


def mem_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def log(*a):
    print(f"[l1e_hcov {time.time()-t0:5.0f}s {mem_mb():.0f}MB]", *a, flush=True)


def leaves_in(expr: str) -> set[str]:
    return {t for t in re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", expr) if t not in OPS}


def is_banned_leaf(name: str) -> bool:
    if name in BANNED_EXACT:
        return True
    return any(name.startswith(p) for p in BANNED_PREFIXES)


def family_of(expr: str) -> str:
    L = sorted(leaves_in(expr))
    if not L:
        return "unknown"
    if all(x.startswith("rz_") or x.startswith("rq_") or x.startswith("rzrq_") for x in L):
        return "rzrq_structure"
    if all(x.startswith("float_") for x in L):
        return "float_event_calendar"
    if all(x.startswith("div_") for x in L):
        return "div_ex_calendar"
    if any(x.startswith("rz_") for x in L) and any(x.startswith("float_") for x in L):
        return "rzrq_x_float"
    return "mixed:" + "+".join(L[:3])


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


def build_rzrq_panels(cal, cols, mask, fm: pd.DataFrame) -> tuple[dict, dict]:
    path = V2 / "margin/rzrq_daily_tushare.parquet"
    gap = {"path": str(path), "family": "rzrq_structure"}
    if not path.exists():
        gap["ok"] = False
        gap["error"] = "missing"
        return {}, gap
    # load only needed window
    rz = pd.read_parquet(
        path,
        columns=["trade_date", "ts_code", "rzye", "rqye", "rzrqye", "available_at"],
    )
    rz["available_at"] = pd.to_datetime(rz["available_at"])
    if getattr(rz["available_at"].dt, "tz", None) is not None:
        rz["avail_date"] = (
            rz["available_at"].dt.tz_convert("Asia/Shanghai").dt.normalize().dt.tz_localize(None)
        )
    else:
        rz["avail_date"] = pd.to_datetime(rz["available_at"]).dt.normalize()
    rz = rz[rz["avail_date"] >= (LOOKBACK_START - pd.Timedelta(days=5))]
    rz["bs"] = rz["ts_code"].map(_to_baostock)
    rz = rz[rz["bs"].isin(cols)]
    gap.update({"ok": True, "n_rows": int(len(rz)), "n_instruments": int(rz["bs"].nunique())})

    def pivot_one(valcol: str) -> pd.DataFrame:
        sub = rz[["avail_date", "bs", valcol]].dropna(subset=[valcol])
        sub = sub.sort_values(["avail_date", "bs"]).drop_duplicates(["avail_date", "bs"], keep="last")
        wide = sub.pivot(index="avail_date", columns="bs", values=valcol)
        wide = wide.reindex(index=cal, columns=cols).astype("float32")
        wide = wide.ffill(limit=5)
        if mask is not None:
            wide = wide.where(mask)
        return wide.astype("float32")

    rzye_df = pivot_one("rzye")
    rqye_df = pivot_one("rqye")
    rzrq_df = pivot_one("rzrqye")
    del rz
    gc.collect()
    # intensity vs float mktcap (万元 vs 元? tushare rzye often 元; fm usually 万元 or 元)
    # Use ratio with fm; protect zeros
    fm2 = fm.reindex(index=cal, columns=cols).astype("float32")
    # Heuristic: if median(rzye)/median(fm) >> 1, scales differ; still rank-ok
    with np.errstate(divide="ignore", invalid="ignore"):
        rz_int = (rzye_df / fm2.replace(0, np.nan)).astype("float32")
        rq_int = (rqye_df / fm2.replace(0, np.nan)).astype("float32")
        rzrq_int = (rzrq_df / fm2.replace(0, np.nan)).astype("float32")
    if mask is not None:
        rz_int = rz_int.where(mask)
        rq_int = rq_int.where(mask)
        rzrq_int = rzrq_int.where(mask)

    out = {
        "rz_intensity": rz_int,
        "rq_intensity": rq_int,
        "rzrq_intensity": rzrq_int,
        "rz_bal": rzye_df,
        "rq_bal": rqye_df,
    }
    # deltas / vol of delta as structural leaves
    out["rz_delta_5"] = rz_int.diff(5).astype("float32")
    out["rz_delta_10"] = rz_int.diff(10).astype("float32")
    out["rq_delta_5"] = rq_int.diff(5).astype("float32")
    out["rzrq_delta_5"] = rzrq_int.diff(5).astype("float32")
    if mask is not None:
        for k in ("rz_delta_5", "rz_delta_10", "rq_delta_5", "rzrq_delta_5"):
            out[k] = out[k].where(mask).astype("float32")

    for k, df in out.items():
        gap[f"nonempty_{k}"] = float((df.notna() & (df.abs() > 1e-12)).to_numpy().mean())
        gap[f"mean_names_{k}"] = float(
            (df.notna() & (df.abs() > 1e-12)).sum(axis=1).mean()
        )
    del rzye_df, rqye_df, rzrq_df, fm2
    gc.collect()
    return out, gap


def build_float_event_panels(cal, cols, mask) -> tuple[dict, dict]:
    path = V2 / "share_float/share_float_2018plus.parquet"
    gap = {"path": str(path), "family": "float_event_calendar"}
    if not path.exists():
        gap["ok"] = False
        return {}, gap
    sf = pd.read_parquet(
        path, columns=["ts_code", "float_date", "float_ratio", "ann_date"]
    )
    sf["float_date"] = pd.to_datetime(sf["float_date"], errors="coerce")
    sf["ann_date"] = pd.to_datetime(sf["ann_date"], errors="coerce")
    # PIT: available after max(ann_date+1, float_date) for post-event density;
    # for pre-unlock density use float_date as event day (known after ann).
    # Use avail = max(ann_date+1day, float_date) clipped to calendar — post-float density.
    sf = sf.dropna(subset=["float_date"])
    sf["bs"] = sf["ts_code"].map(_to_baostock)
    sf = sf[sf["bs"].isin(cols)]
    # available: next session after ann_date if present else float_date
    avail = sf["ann_date"].fillna(sf["float_date"]) + pd.Timedelta(days=1)
    sf["avail_date"] = avail
    sf = sf[
        (sf["avail_date"] >= LOOKBACK_START - pd.Timedelta(days=90))
        & (sf["avail_date"] <= cal.max() + pd.Timedelta(days=5))
    ]
    gap.update({"ok": True, "n_events": int(len(sf)), "n_instruments": int(sf["bs"].nunique())})

    col_index = {c: i for i, c in enumerate(cols)}
    cal_np = cal.values.astype("datetime64[ns]")
    T, N = len(cal), len(cols)
    daily_cnt = np.zeros((T, N), dtype=np.float32)
    daily_ratio = np.zeros((T, N), dtype=np.float32)
    for row in sf.itertuples(index=False):
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
        daily_cnt[i, j] += 1.0
        ratio = float(row.float_ratio) if row.float_ratio is not None and np.isfinite(row.float_ratio) else 0.0
        daily_ratio[i, j] += np.float32(max(ratio, 0.0))
    del sf
    gc.collect()
    base_cnt = pd.DataFrame(daily_cnt, index=cal, columns=cols, dtype="float32")
    base_ratio = pd.DataFrame(daily_ratio, index=cal, columns=cols, dtype="float32")
    out = {
        "float_evt_20": base_cnt.rolling(20, min_periods=1).sum().astype("float32"),
        "float_evt_60": base_cnt.rolling(60, min_periods=1).sum().astype("float32"),
        "float_ratio_20": base_ratio.rolling(20, min_periods=1).sum().astype("float32"),
        "float_ratio_60": base_ratio.rolling(60, min_periods=1).sum().astype("float32"),
        "float_evt_flag": (base_cnt > 0).astype("float32"),
    }
    if mask is not None:
        for k in list(out.keys()):
            out[k] = out[k].where(mask).astype("float32")
    for k, df in out.items():
        gap[f"nonempty_{k}"] = float((df.notna() & (df.abs() > 1e-12)).to_numpy().mean())
        gap[f"mean_names_{k}"] = float(
            (df.notna() & (df.abs() > 1e-12)).sum(axis=1).mean()
        )
    del daily_cnt, daily_ratio, base_cnt, base_ratio
    gc.collect()
    return out, gap


def build_div_panels(cal, cols, mask) -> tuple[dict, dict]:
    path = V2 / "corporate_actions/dividend_by_exdate_tushare.parquet"
    gap = {"path": str(path), "family": "div_ex_calendar"}
    if not path.exists():
        gap["ok"] = False
        return {}, gap
    div = pd.read_parquet(path)
    # need ex_date + ann for PIT
    if "ex_date" not in div.columns:
        gap["ok"] = False
        gap["error"] = "no_ex_date"
        return {}, gap
    div = div.copy()
    div["ex_date"] = pd.to_datetime(div["ex_date"], errors="coerce")
    ann = pd.to_datetime(div.get("ann_date"), errors="coerce") if "ann_date" in div.columns else None
    div["bs"] = div["ts_code"].map(_to_baostock) if "ts_code" in div.columns else None
    div = div.dropna(subset=["ex_date", "bs"])
    div = div[div["bs"].isin(cols)]
    # available after ann+1 if known, else ex_date (conservative: use ann)
    if ann is not None:
        div["avail_date"] = (ann.fillna(div["ex_date"]) + pd.Timedelta(days=1))
    else:
        div["avail_date"] = div["ex_date"]
    div = div[
        (div["avail_date"] >= LOOKBACK_START - pd.Timedelta(days=40))
        & (div["avail_date"] <= cal.max() + pd.Timedelta(days=5))
    ]
    gap.update({"ok": True, "n_events": int(len(div)), "n_instruments": int(div["bs"].nunique())})

    col_index = {c: i for i, c in enumerate(cols)}
    cal_np = cal.values.astype("datetime64[ns]")
    T, N = len(cal), len(cols)
    daily = np.zeros((T, N), dtype=np.float32)
    # days_to_ex: fill known future ex after avail
    days_to = np.full((T, N), np.nan, dtype=np.float32)
    for row in div.itertuples(index=False):
        j = col_index.get(row.bs)
        if j is None:
            continue
        d = pd.Timestamp(row.avail_date).normalize()
        ex = pd.Timestamp(row.ex_date).normalize()
        i = int(np.searchsorted(cal_np, np.datetime64(d), side="left"))
        if i >= T:
            continue
        if i < T and cal_np[i] < np.datetime64(d):
            i += 1
            if i >= T:
                continue
        daily[i, j] += 1.0
        # fill days_to from avail to ex on calendar
        i_ex = int(np.searchsorted(cal_np, np.datetime64(ex), side="left"))
        if i_ex >= T:
            i_ex = T - 1
        for t in range(i, min(i_ex + 1, T)):
            dt = (ex - pd.Timestamp(cal[t])).days
            if dt < 0:
                continue
            prev = days_to[t, j]
            if not np.isfinite(prev) or dt < prev:
                days_to[t, j] = np.float32(dt)
    del div
    gc.collect()
    base = pd.DataFrame(daily, index=cal, columns=cols, dtype="float32")
    dto = pd.DataFrame(days_to, index=cal, columns=cols, dtype="float32")
    out = {
        "div_evt_20": base.rolling(20, min_periods=1).sum().astype("float32"),
        "div_evt_60": base.rolling(60, min_periods=1).sum().astype("float32"),
        "div_days_to": dto,
        "div_flag_20": (base.rolling(20, min_periods=1).sum() > 0).astype("float32"),
    }
    if mask is not None:
        for k in list(out.keys()):
            out[k] = out[k].where(mask).astype("float32")
    for k, df in out.items():
        # days_to: nonempty = notna
        if k == "div_days_to":
            active = df.notna()
        else:
            active = df.notna() & (df.abs() > 1e-12)
        gap[f"nonempty_{k}"] = float(active.to_numpy().mean())
        gap[f"mean_names_{k}"] = float(active.sum(axis=1).mean())
    del daily, days_to, base, dto
    gc.collect()
    return out, gap


def build_candidates() -> list[dict]:
    cands = []

    def add(expr: str, family: str, note: str = ""):
        L = leaves_in(expr)
        if not L or any(is_banned_leaf(x) for x in L):
            return
        cands.append({"expr": expr, "family": family, "note": note})

    # --- rzrq structure ---
    for x in ("rz_intensity", "rq_intensity", "rzrq_intensity"):
        add(x, "rzrq_structure", "raw intensity")
        add(f"rank({x})", "rzrq_structure", "rank intensity")
        add(f"neg({x})", "rzrq_structure", "neg intensity")
        add(f"rank(neg({x}))", "rzrq_structure", "rank neg")
        add(f"zscore({x})", "rzrq_structure", "zscore")
        add(f"ts_delta_5({x})", "rzrq_structure", "delta5")
        add(f"ts_delta_10({x})", "rzrq_structure", "delta10")
        add(f"rank(ts_delta_5({x}))", "rzrq_structure", "rank delta5")
        add(f"abs(ts_delta_5({x}))", "rzrq_structure", "abs delta5")
        add(f"ts_std_10({x})", "rzrq_structure", "ts_std10")
        add(f"rank(ts_std_10({x}))", "rzrq_structure", "rank ts_std10")
        add(f"abs(ts_std_10(ts_delta_5({x})))", "rzrq_structure", "vol of delta")
        add(f"ts_mean_10({x})", "rzrq_structure", "ts_mean10")
        add(f"rank(ts_mean_10({x}))", "rzrq_structure", "rank ts_mean10")
        add(f"delay_5({x})", "rzrq_structure", "delay5")
        add(f"delay_5(rank({x}))", "rzrq_structure", "delay5 rank")

    for x in ("rz_delta_5", "rz_delta_10", "rq_delta_5", "rzrq_delta_5"):
        add(x, "rzrq_structure", "prebuilt delta leaf")
        add(f"rank({x})", "rzrq_structure", "rank prebuilt delta")
        add(f"neg({x})", "rzrq_structure", "neg prebuilt delta")
        add(f"abs({x})", "rzrq_structure", "abs prebuilt delta")
        add(f"ts_std_10({x})", "rzrq_structure", "std of delta leaf")
        add(f"rank(ts_std_10({x}))", "rzrq_structure", "rank std delta")

    # --- float event calendars ---
    for x in ("float_evt_20", "float_evt_60", "float_ratio_20", "float_ratio_60"):
        add(x, "float_event_calendar", "raw float density")
        add(f"rank({x})", "float_event_calendar", "rank")
        add(f"neg({x})", "float_event_calendar", "neg")
        add(f"rank(neg({x}))", "float_event_calendar", "rank neg")
        add(f"ts_std_10({x})", "float_event_calendar", "ts_std10")
        add(f"rank(ts_std_10({x}))", "float_event_calendar", "rank ts_std")
        add(f"ts_delta_5({x})", "float_event_calendar", "delta5")
        add(f"abs(ts_std_10(ts_delta_5({x})))", "float_event_calendar", "vol of delta")
        add(f"ts_max_5({x})", "float_event_calendar", "ts_max5")
        add(f"rank(ts_max_5({x}))", "float_event_calendar", "rank ts_max5")

    add("float_evt_flag", "float_event_calendar", "same-day flag")
    add("rank(float_evt_flag)", "float_event_calendar", "rank flag")
    add("neg(float_evt_flag)", "float_event_calendar", "neg flag")

    # --- div calendars ---
    for x in ("div_evt_20", "div_evt_60", "div_flag_20"):
        add(x, "div_ex_calendar", "div density")
        add(f"rank({x})", "div_ex_calendar", "rank")
        add(f"neg({x})", "div_ex_calendar", "neg")
        add(f"rank(neg({x}))", "div_ex_calendar", "rank neg")
        add(f"ts_std_10({x})", "div_ex_calendar", "ts_std")
        add(f"rank(ts_std_10({x}))", "div_ex_calendar", "rank ts_std")
    add("div_days_to", "div_ex_calendar", "days to ex")
    add("rank(div_days_to)", "div_ex_calendar", "rank days_to")
    add("neg(div_days_to)", "div_ex_calendar", "neg days_to")
    add("rank(neg(div_days_to))", "div_ex_calendar", "rank neg days_to")

    # light cross
    add("mul(rank(rz_intensity), rank(neg(float_evt_60)))", "rzrq_x_float", "rz x avoid unlock")
    add("mul(rank(neg(rz_intensity)), rank(float_evt_60))", "rzrq_x_float", "low rz x unlock")

    # dedupe
    seen = set()
    out = []
    for c in cands:
        if c["expr"] in seen:
            continue
        seen.add(c["expr"])
        out.append(c)
    return out


def write_report(rows, meta, shortlist):
    lines = []
    lines.append("# AI 因子 L1e：硬覆盖结构叶探索（非 title 稀疏依赖）")
    lines.append("")
    lines.append("- **时间：** 2026-10-12（America/New_York）")
    lines.append("- **promotion_approved：** false；**密封：** 未开；**不交 Strategy 权重**")
    lines.append("- **trial_kind：** explore_gate / process")
    lines.append("- **本金主口径：** 60 万 / 100 万；主裁决=冲击+flat25")
    lines.append("- **硬覆盖门槛：** nonempty≥8%；mean_event_names≥40；frac_days≥20≥50%")
    lines.append("- **禁止：** 广播叶、跌停主候选、小盘、教科书主线、密封、ann title 族作主依赖、Strategy 权重")
    lines.append("- **公告：** 本批不以 ann title 为叶；`invented_body=false`")
    lines.append(
        f"- 账本：N {meta.get('ledger_N_before')} → {meta.get('ledger_N_after')} "
        f"（+{meta.get('ledger_N_new')}，explore_gate）"
    )
    lines.append(
        f"- 峰值 RSS：{meta.get('peak_rss_MB'):.0f} MB（上限 {meta.get('mem_cap_MB')}；"
        f"under_cap={meta.get('under_mem_cap')}）；运行 {meta.get('runtime_s')}s"
    )
    lines.append("")
    lines.append("## 批次规模")
    lines.append("")
    lines.append(f"- 候选：{meta.get('n_candidates')}")
    lines.append(f"- FAIL_SPARSE（硬覆盖未过，不进短清单）：{meta.get('n_fail_sparse')}")
    lines.append(f"- FAIL_CS / 其它跳过：{meta.get('n_fail_cs')}")
    lines.append(f"- 覆盖硬过且评估：{meta.get('n_cov_pass_eval')}")
    lines.append(f"- 冲击闸存活（GATE_OK）：{meta.get('n_gate_ok')}")
    lines.append(f"- 短清单（覆盖硬过 ∧ 冲击闸）：{meta.get('n_shortlist')}")
    lines.append("")
    lines.append("## 族摘要")
    lines.append("")
    fam = meta.get("family_counts") or {}
    lines.append("| 族 | 候选 | FAIL_SPARSE | GATE_OK |")
    lines.append("|---|---:|---:|---:|")
    for k, v in sorted(fam.items()):
        lines.append(
            f"| {k} | {v.get('n', 0)} | {v.get('fail_sparse', 0)} | {v.get('gate_ok', 0)} |"
        )
    lines.append("")
    lines.append("## 数据缺口 / 覆盖草图")
    lines.append("")
    for key in ("rzrq_gap", "float_gap", "div_gap"):
        g = meta.get(key) or {}
        lines.append(f"### {key}")
        lines.append(f"- ok={g.get('ok')} path=`{g.get('path')}`")
        # print a few nonempty keys
        keys = [k for k in g.keys() if k.startswith("nonempty_")][:8]
        for k in keys:
            lines.append(f"- {k}={g.get(k):.4f} mean_names={g.get(k.replace('nonempty_','mean_names_'), float('nan')):.1f}"
                         if isinstance(g.get(k), float) else f"- {k}={g.get(k)}")
        lines.append("")
    lines.append("## 短清单（硬覆盖过 ∧ 冲击闸）")
    lines.append("")
    if not shortlist:
        lines.append("*（空）本批无同时过硬覆盖与冲击闸的叶。*")
    else:
        lines.append(
            "| # | 族 | 表达式 | flat25 | 60万+25bp | 100万+25bp | ICIR | 换手 | nonempty | 日均事件股 | 裁决 |"
        )
        lines.append("|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|")
        for i, r in enumerate(shortlist, 1):
            m = r.get("metrics") or {}
            cov = r.get("coverage") or {}
            lines.append(
                f"| {i} | {r.get('family')} | `{r.get('expr')}` | "
                f"{fmt_pct(m.get('flat25'))} | {fmt_pct(m.get('imp60_p25'))} | "
                f"{fmt_pct(m.get('imp100_p25'))} | {fmt_f(m.get('icir'), 3)} | "
                f"{fmt_f(m.get('turn'), 3)} | {fmt_f(cov.get('nonempty_rate'), 4)} | "
                f"{fmt_f(cov.get('mean_event_names'), 1)} | {r.get('verdict')} |"
            )
    lines.append("")
    lines.append("## Top 覆盖硬过但冲击未过（对照）")
    lines.append("")
    cov_fail_gate = [
        r
        for r in rows
        if r.get("survive_coverage") and r.get("verdict") in ("FAIL_GATE", "FAIL_CS")
    ]
    cov_fail_gate = sorted(
        cov_fail_gate,
        key=lambda r: (r.get("metrics") or {}).get("imp60_p25") or float("-inf"),
        reverse=True,
    )[:15]
    if not cov_fail_gate:
        lines.append("*无。*")
    else:
        lines.append("| 表达式 | flat25 | 60万+25bp | ICIR | nonempty | 裁决 |")
        lines.append("|---|---:|---:|---:|---:|---|")
        for r in cov_fail_gate:
            m = r.get("metrics") or {}
            cov = r.get("coverage") or {}
            lines.append(
                f"| `{r.get('expr')}` | {fmt_pct(m.get('flat25'))} | "
                f"{fmt_pct(m.get('imp60_p25'))} | {fmt_f(m.get('icir'), 3)} | "
                f"{fmt_f(cov.get('nonempty_rate'), 4)} | {r.get('verdict')} |"
            )
    lines.append("")
    lines.append("## FAIL_SPARSE 样例（不进短清单）")
    lines.append("")
    sparse = [r for r in rows if r.get("verdict") == "FAIL_SPARSE"][:20]
    for r in sparse:
        cov = r.get("coverage") or {}
        lines.append(
            f"- `{r.get('expr')}` — {', '.join(cov.get('fail_reasons') or [])}"
        )
    if not sparse:
        lines.append("*无（或本批叶均过硬覆盖）。*")
    lines.append("")
    lines.append("## 诚实裁决")
    lines.append("")
    lines.append(
        f"1. **硬覆盖：** 过闸 {meta.get('n_cov_pass_eval')}/{meta.get('n_candidates')}；"
        f"FAIL_SPARSE={meta.get('n_fail_sparse')}（不进短清单）。"
    )
    lines.append(
        f"2. **冲击闸存活：** GATE_OK={meta.get('n_gate_ok')}；短清单 N={meta.get('n_shortlist')}。"
    )
    lines.append(
        "3. **非 title 稀疏依赖：** 主族为 rzrq / float_event / div_ex；"
        "ann_* 与广播/跌停已禁。"
    )
    lines.append("4. **不开密封、不交 Strategy**；`promotion_approved=false`。")
    lines.append("")
    lines.append("## 产物路径")
    lines.append("")
    lines.append("- 报告：`output/alpha/AI_FACTOR_L1e_HARD_COV_STRUCT_EXPLORE_ZH.md`")
    lines.append("- JSON：`output/ai_factor/l1e_hard_cov_struct/`")
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
    l1c = _import_mod("ai_factor_l1c_explore", ROOT / "research/ai_factor_l1c_explore.py")
    from quantlab.factors.ai_factory.ledger import append_attempt
    from quantlab.factors.ops import apply_expr, parse_expr

    log("loading base panels")
    panels, label, public, load_meta = l1b.load_structural_panels()
    peak = max(peak, mem_mb())
    panels, label, public, load_meta = l1c.attach_l1c_panels(panels, label, public, load_meta)
    peak = max(peak, mem_mb())

    # keep size/fm via public size → rebuild fm from size? Better load fm for intensity
    size_panel = public.get("size") if isinstance(public, dict) else None
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

    # float mktcap for intensity denominator
    log("load float_mktcap for rz intensity")
    fm_long = pd.read_parquet(
        V2 / "float_mktcap/float_mktcap_daily_tushare.parquet",
        columns=["trade_date", "instrument_id", "float_mktcap"],
        filters=[("trade_date", ">=", LOOKBACK_START - pd.Timedelta(days=5))],
    )
    fm_long["trade_date"] = pd.to_datetime(fm_long["trade_date"])
    fm = (
        fm_long[fm_long.instrument_id.isin(cols)]
        .drop_duplicates(["trade_date", "instrument_id"], keep="last")
        .set_index(["trade_date", "instrument_id"])["float_mktcap"]
        .unstack()
        .reindex(index=cal, columns=cols)
        .astype("float32")
    )
    del fm_long
    gc.collect()
    # if fm is in 万元 and rzye in 元, ratio still rank-stable
    peak = max(peak, mem_mb())

    # drop heavy unused structural panels to free mem — keep mask source only
    keep_base = set()
    for k in list(panels.keys()):
        if k not in keep_base:
            del panels[k]
    gc.collect()
    log("cleared old panels; building L1e families", "peak", peak)

    rz_panels, rz_gap = build_rzrq_panels(cal, cols, mask, fm)
    panels.update(rz_panels)
    del rz_panels
    gc.collect()
    peak = max(peak, mem_mb())
    log("rzrq panels", len([k for k in panels if k.startswith(('rz','rq'))]), "peak", peak, "gap_ok", rz_gap.get("ok"))

    fl_panels, fl_gap = build_float_event_panels(cal, cols, mask)
    panels.update(fl_panels)
    del fl_panels
    gc.collect()
    peak = max(peak, mem_mb())
    log("float panels done", "peak", peak)

    dv_panels, dv_gap = build_div_panels(cal, cols, mask)
    panels.update(dv_panels)
    del dv_panels, fm
    gc.collect()
    peak = max(peak, mem_mb())
    log("div panels done; n_panels", len(panels), "peak", peak)

    cands = build_candidates()
    # filter to leaves present
    present = set(panels.keys())
    cands = [c for c in cands if leaves_in(c["expr"]) <= present]
    log("candidates", len(cands))

    sig, adv = sci.load_sig_adv(cols, cal)
    peak = max(peak, mem_mb())
    ind_codes = np.full(len(cols), -1, dtype=np.int32)

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
    shortlist = []
    fam_counts: dict[str, dict] = {}
    n_fail_sparse = n_fail_cs = n_cov_pass_eval = n_gate_ok = 0

    for i, cand in enumerate(cands):
        expr = cand["expr"]
        fam = cand.get("family") or family_of(expr)
        fam_counts.setdefault(fam, {"n": 0, "fail_sparse": 0, "gate_ok": 0})
        fam_counts[fam]["n"] += 1
        days_to_style = "days_to" in expr
        try:
            tup = _seed_to_tuple(expr)
            fac = apply_expr(parse_expr(to_nested_tuple(tup)), panels)
            if not isinstance(fac, pd.DataFrame):
                raise TypeError(type(fac))
            fac = fac.astype("float32")
            cs = sci.cs_std_stats(fac)
            cov = sci.coverage_stats(fac, days_to_style=days_to_style)
            if not cov.get("passes_coverage"):
                n_fail_sparse += 1
                fam_counts[fam]["fail_sparse"] += 1
                row = {
                    **cand,
                    "family": fam,
                    "metrics": sci.pack_metrics(None),
                    "coverage": cov,
                    "cs_stats": cs,
                    "survive_coverage": False,
                    "gate_ok": False,
                    "verdict": "FAIL_SPARSE",
                    "promotion_approved": False,
                    "trial_kind": "explore_gate",
                    "on_shortlist": False,
                }
                rows.append(row)
                fit = None
            elif not cs.get("passes_cs_variation"):
                n_fail_cs += 1
                row = {
                    **cand,
                    "family": fam,
                    "metrics": sci.pack_metrics({"skipped": True, "reason": "cs_variation_fail"}),
                    "coverage": cov,
                    "cs_stats": cs,
                    "survive_coverage": True,
                    "gate_ok": False,
                    "verdict": "FAIL_CS",
                    "promotion_approved": False,
                    "trial_kind": "explore_gate",
                    "on_shortlist": False,
                }
                rows.append(row)
                fit = None
            else:
                n_cov_pass_eval += 1
                sim = sci.simulate_book(fac, label, sig, adv)
                m = sci.pack_metrics(sim)
                gate_ok = (
                    math.isfinite(m.get("flat25", float("nan")))
                    and m["flat25"] > 0
                    and math.isfinite(m.get("imp60_p25", float("nan")))
                    and m["imp60_p25"] >= IMP60_FLOOR
                    and math.isfinite(m.get("imp100_p25", float("nan")))
                    and m["imp100_p25"] >= IMP60_FLOOR
                )
                verdict = "GATE_OK" if gate_ok else "FAIL_GATE"
                if gate_ok:
                    n_gate_ok += 1
                    fam_counts[fam]["gate_ok"] += 1
                row = {
                    **cand,
                    "family": fam,
                    "metrics": m,
                    "coverage": cov,
                    "cs_stats": cs,
                    "survive_coverage": True,
                    "gate_ok": gate_ok,
                    "verdict": verdict,
                    "promotion_approved": False,
                    "trial_kind": "explore_gate",
                    "on_shortlist": bool(gate_ok),
                }
                rows.append(row)
                if gate_ok:
                    shortlist.append(row)
                fit = m.get("imp60_p25")
            del fac
        except Exception as exc:  # noqa: BLE001
            row = {
                **cand,
                "family": fam,
                "metrics": sci.pack_metrics(None),
                "coverage": None,
                "cs_stats": None,
                "survive_coverage": False,
                "gate_ok": False,
                "verdict": "ERROR",
                "error": f"{type(exc).__name__}: {exc}",
                "promotion_approved": False,
                "trial_kind": "explore_gate",
                "on_shortlist": False,
            }
            rows.append(row)
            fit = None

        notes = (
            f"l1e_hard_cov_struct;family={fam};verdict={row.get('verdict')};"
            f"cov_pass={row.get('survive_coverage')};process_not_sealed;promotion_approved=false"
        )
        for path in (run_ledger, main_ledger):
            append_attempt(
                engine="l1e_hard_cov_struct",
                seed=SEED,
                universe="midlarge_top1500_or_csi300_500",
                cost=0.0025,
                window="explore_20240603_to_latest_l1e_hcov",
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
                expr[:50],
                "60+25",
                fmt_pct(fit) if fit is not None else "—",
                "peak",
                peak,
            )
        if mem_mb() > MEM_CAP_MB - 150:
            gc.collect()

    shortlist = sorted(
        shortlist,
        key=lambda r: (r.get("metrics") or {}).get("imp60_p25") or float("-inf"),
        reverse=True,
    )
    n_after = (
        sum(1 for x in main_ledger.read_text().splitlines() if x.strip())
        if main_ledger.exists()
        else 0
    )
    peak = max(peak, mem_mb())
    meta = {
        "mode": "l1e_hard_cov_struct_explore",
        "promotion_approved": False,
        "sealed_executed": False,
        "trial_kind": "explore_gate",
        "ann_title_only": True,
        "invented_body": False,
        "n_candidates": len(cands),
        "n_fail_sparse": n_fail_sparse,
        "n_fail_cs": n_fail_cs,
        "n_cov_pass_eval": n_cov_pass_eval,
        "n_gate_ok": n_gate_ok,
        "n_shortlist": len(shortlist),
        "family_counts": fam_counts,
        "rzrq_gap": rz_gap,
        "float_gap": fl_gap,
        "div_gap": dv_gap,
        "ledger_N_before": n_before,
        "ledger_N_after": n_after,
        "ledger_N_new": n_after - n_before,
        "peak_rss_MB": peak,
        "mem_cap_MB": MEM_CAP_MB,
        "under_mem_cap": peak < MEM_CAP_MB,
        "runtime_s": round(time.time() - t0, 1),
        "shortlist_exprs": [r["expr"] for r in shortlist],
    }
    (OUT_DIR / "results.json").write_text(
        json.dumps(clean(rows), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "shortlist.json").write_text(
        json.dumps(clean(shortlist), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "summary.json").write_text(
        json.dumps(clean(meta), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_report(rows, meta, shortlist)
    log(
        "DONE",
        "cand",
        len(cands),
        "sparse",
        n_fail_sparse,
        "GATE_OK",
        n_gate_ok,
        "shortlist",
        len(shortlist),
        "N",
        n_after,
        "peak",
        peak,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
