#!/usr/bin/env python3
"""L1d shortlist N=9: honest coverage + flat25/impact gates; deepen ann_insider_dec.

promotion_approved=False. No sealed. No Strategy. No small-cap. No textbook.
title_only. Ban broadcast/LD primary. Memory < 2.5GB.
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
SHORTLIST_PATH = ROOT / "output/ai_factor/l1d_coverage_mech_shortlist/shortlist.json"
OUT_DIR = ROOT / "output/ai_factor/l1d_shortlist_coverage_impact"
DEEP_DIR = OUT_DIR / "ann_insider_dec_deepen"
REPORT = ROOT / "output/alpha/AI_FACTOR_L1d_SHORTLIST_COVERAGE_IMPACT_ZH.md"
REPORT_DEEP = ROOT / "output/alpha/AI_FACTOR_L1d_ANN_INSIDER_DEC_DEEPEN_ZH.md"
SW_L1 = ROOT / "data/sw/industry_members_sw_l1.parquet"

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

HONEST3 = [
    "rank(ts_std_10(ann_insider_dec_5))",
    "ts_std_10(ann_insider_dec_5)",
    "ts_max_5(ts_max_5(ann_insider_dec_5))",
]

OPS = {
    "add", "sub", "mul", "div", "neg", "abs", "rank", "zscore",
    "industry_neutral", "size_neutral",
}
for k in (1, 5, 10, 20):
    OPS |= {f"delay_{k}", f"ts_mean_{k}", f"ts_std_{k}", f"ts_delta_{k}", f"ts_max_{k}"}

t0 = 0.0


def mem_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def log(*a):
    print(f"[l1d_sci {time.time()-t0:5.0f}s {mem_mb():.0f}MB]", *a, flush=True)


def leaves_in(expr: str) -> set[str]:
    return {t for t in re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", expr) if t not in OPS}


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
    m = re.fullmatch(r"delay_(\d+)\((.+)\)", s)
    if m:
        return ("op", f"delay_{m.group(1)}", _seed_to_tuple(m.group(2)))
    m = re.fullmatch(r"ts_std_(\d+)\((.+)\)", s)
    if m:
        return ("op", f"ts_std_{m.group(1)}", _seed_to_tuple(m.group(2)))
    m = re.fullmatch(r"ts_delta_(\d+)\((.+)\)", s)
    if m:
        return ("op", f"ts_delta_{m.group(1)}", _seed_to_tuple(m.group(2)))
    m = re.fullmatch(r"ts_max_(\d+)\((.+)\)", s)
    if m:
        return ("op", f"ts_max_{m.group(1)}", _seed_to_tuple(m.group(2)))
    m = re.fullmatch(r"ts_mean_(\d+)\((.+)\)", s)
    if m:
        return ("op", f"ts_mean_{m.group(1)}", _seed_to_tuple(m.group(2)))
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


def ann_from_daily(rets: np.ndarray) -> dict:
    r = rets[np.isfinite(rets)]
    if len(r) < 20:
        return {"ann": float("nan"), "sharpe": float("nan"), "mdd": float("nan"), "n": int(len(r))}
    nav = np.cumprod(1.0 + r)
    years = len(r) / 244.0
    cagr = float(nav[-1] ** (1.0 / years) - 1.0) if years > 0 and nav[-1] > 0 else float("nan")
    sd = float(r.std(ddof=1))
    sh = float(r.mean() / sd * math.sqrt(244)) if sd > 1e-12 else float("nan")
    peak = np.maximum.accumulate(nav)
    mdd = float((nav / peak - 1.0).min())
    return {"ann": cagr, "sharpe": sh, "mdd": mdd, "n": int(len(r))}


def simulate_book(factor, label, sig, adv, *, top_n=TOP_N, return_top=False):
    from quantlab.factors.ai_factory.fitness import daily_rank_ic, icir_from_series

    idx = factor.index.intersection(label.index)
    idx = idx[idx >= EXPLORE_START]
    f = factor.reindex(idx).to_numpy(dtype=np.float64, copy=False)
    y = label.reindex(idx).to_numpy(dtype=np.float64, copy=False)
    s = sig.reindex(idx).to_numpy(dtype=np.float64, copy=False)
    a = adv.reindex(idx).to_numpy(dtype=np.float64, copy=False)
    T = len(idx)
    gross = np.full(T, np.nan)
    turn_ow = np.full(T, np.nan)
    imp_frac = {aum: np.full(T, np.nan) for aum in AUMS}
    top_idx_list = [None] * T if return_top else None
    prev = None
    for t in range(T):
        ft, yt = f[t], y[t]
        m = np.isfinite(ft) & np.isfinite(yt)
        n_ok = int(m.sum())
        k = min(top_n, n_ok)
        if k < max(5, top_n // 5):
            continue
        ii = np.nonzero(m)[0]
        vals = ft[ii]
        part = np.argpartition(vals, -k)[-k:]
        cur_idx = ii[part]
        cur = set(cur_idx.tolist())
        gross[t] = float(yt[cur_idx].mean())
        if return_top:
            top_idx_list[t] = cur_idx
        if prev is None:
            turn_ow[t] = 1.0
            entered, exited = cur, set()
        else:
            entered, exited = cur - prev, prev - cur
            turn_ow[t] = len(cur.symmetric_difference(prev)) / (2.0 * k)
        w = 1.0 / k
        for aum in AUMS:
            cost_cny = 0.0
            for j in exited | entered:
                V = w * aum
                cost_cny += COMMISSION_ONE_WAY * V
                sj, aj = s[t, j], a[t, j]
                if np.isfinite(sj) and np.isfinite(aj) and aj > 0 and V > 0:
                    cost_cny += V * K_IMP * float(sj) * math.sqrt(V / aj)
            imp_frac[aum][t] = cost_cny / aum
        prev = cur

    out = {
        "gross": ann_from_daily(gross),
        "mean_turn_ow": float(np.nanmean(turn_ow)),
        "n_days": int(np.isfinite(gross).sum()),
        "flat": {},
        "impact": {},
        "promotion_approved": False,
    }
    for bp in FLAT_BPS:
        out["flat"][str(bp)] = ann_from_daily(gross - turn_ow * (bp / 1e4))
    for aum in AUMS:
        key = str(int(aum))
        out["impact"][key] = ann_from_daily(gross - imp_frac[aum])
        for bp in FLAT_BPS:
            extra = max(0.0, bp / 1e4 - COMMISSION_ONE_WAY)
            out["impact"][f"{key}_plus_flat{bp}"] = ann_from_daily(
                gross - imp_frac[aum] - turn_ow * extra
            )
    ics = daily_rank_ic(factor.reindex(idx), label.reindex(idx))
    out["ic_mean"] = float(np.nanmean(ics.to_numpy()))
    out["icir"] = float(icir_from_series(ics))
    if return_top:
        return out, top_idx_list, idx
    return out


def load_sig_adv(cols, index):
    cl = pd.read_parquet(SCRATCH / "close.parquet", columns=cols).astype("float32")
    cl = cl.loc[cl.index >= LOOKBACK_START]
    fa = pd.read_parquet(SCRATCH / "factor.parquet", columns=cols).astype("float32")
    fa = fa.loc[fa.index >= LOOKBACK_START].ffill()
    aC = (cl * fa).astype("float32")
    del cl, fa
    gc.collect()
    ret = aC.pct_change(fill_method=None)
    sig = ret.rolling(20, min_periods=10).std().astype("float32")
    del aC, ret
    gc.collect()
    amt = pd.read_parquet(SCRATCH / "amount.parquet", columns=cols).astype("float32")
    amt = amt.loc[amt.index >= LOOKBACK_START]
    adv = amt.rolling(20, min_periods=10).mean().astype("float32")
    del amt
    gc.collect()
    return sig.reindex(index=index, columns=cols), adv.reindex(index=index, columns=cols)


def cs_std_stats(fac: pd.DataFrame) -> dict:
    sample = fac.loc[fac.index >= EXPLORE_START]
    daily_std = sample.std(axis=1, skipna=True)
    daily_nuniq = sample.nunique(axis=1, dropna=True)
    mean_std = float(daily_std.mean())
    frac_near_zero = float((daily_std.fillna(0) < CS_STD_MIN).mean())
    frac_const = float((daily_nuniq.fillna(1) <= 1).mean())
    return {
        "cs_std_mean": mean_std,
        "cs_std_median": float(daily_std.median()),
        "frac_days_near_zero_std": frac_near_zero,
        "frac_days_constant_cs": frac_const,
        "passes_cs_variation": bool(
            mean_std > CS_STD_MIN and frac_near_zero < 0.5 and frac_const < 0.5
        ),
    }


def coverage_stats(fac: pd.DataFrame, *, days_to_style: bool = False) -> dict:
    sample = fac.loc[fac.index >= EXPLORE_START]
    if days_to_style:
        active = sample.notna()
    else:
        active = sample.notna() & (sample.abs() > 1e-12)
    nonempty = float(active.to_numpy().mean())
    n_names = active.sum(axis=1).astype(float)
    mean_names = float(n_names.mean()) if len(n_names) else float("nan")
    med_names = float(n_names.median()) if len(n_names) else float("nan")
    frac_ge = float((n_names >= COV_EVENT_N_MIN).mean()) if len(n_names) else float("nan")
    passes = bool(
        math.isfinite(nonempty)
        and nonempty >= COV_NONEMPTY_MIN
        and math.isfinite(mean_names)
        and mean_names >= COV_MEAN_EVENT_NAMES_MIN
        and math.isfinite(frac_ge)
        and frac_ge >= COV_FRAC_DAYS_GE20_MIN
    )
    fail_reasons = []
    if not (math.isfinite(nonempty) and nonempty >= COV_NONEMPTY_MIN):
        fail_reasons.append(f"nonempty<{COV_NONEMPTY_MIN:.0%}({nonempty:.4f})")
    if not (math.isfinite(mean_names) and mean_names >= COV_MEAN_EVENT_NAMES_MIN):
        fail_reasons.append(f"mean_event_names<{COV_MEAN_EVENT_NAMES_MIN:.0f}({mean_names:.2f})")
    if not (math.isfinite(frac_ge) and frac_ge >= COV_FRAC_DAYS_GE20_MIN):
        fail_reasons.append(f"frac_days_ge{COV_EVENT_N_MIN}<{COV_FRAC_DAYS_GE20_MIN:.0%}({frac_ge:.4f})")
    return {
        "nonempty_rate": nonempty,
        "mean_event_names": mean_names,
        "median_event_names": med_names,
        "frac_days_ge_N": frac_ge,
        "N_event_threshold": COV_EVENT_N_MIN,
        "passes_coverage": passes,
        "fail_reasons": fail_reasons,
    }


def topn_event_share(event_leaf: pd.DataFrame, top_idx_list, explore_idx) -> dict:
    """Mean fraction of Top-N names with event_leaf > 0 that day."""
    L = event_leaf.reindex(explore_idx).to_numpy(dtype=np.float64, copy=False)
    T = len(explore_idx)
    hit = np.full(T, np.nan)
    n_ev = np.full(T, np.nan)
    for t in range(T):
        ti = top_idx_list[t] if t < len(top_idx_list) else None
        if ti is None:
            continue
        row = L[t]
        vals = row[ti]
        finite = np.isfinite(vals)
        if finite.sum() == 0:
            continue
        hit[t] = float((vals[finite] > 0).mean())
        # also universe event count
        m = np.isfinite(row)
        if m.sum() >= 30:
            n_ev[t] = float((m & (row > 0)).sum())
    return {
        "mean_topN_event_share": float(np.nanmean(hit)),
        "median_topN_event_share": float(np.nanmedian(hit)),
        "mean_event_names_univ": float(np.nanmean(n_ev)),
        "frac_days_topN_any_event": float(np.nanmean(hit > 0)) if np.isfinite(hit).any() else float("nan"),
    }


def size_residualize(fac: pd.DataFrame, size: pd.DataFrame) -> pd.DataFrame:
    idx = fac.index.intersection(size.index)
    cols = [c for c in fac.columns if c in size.columns]
    F = fac.reindex(index=idx, columns=cols).to_numpy(dtype=np.float64, copy=False)
    S = size.reindex(index=idx, columns=cols).to_numpy(dtype=np.float64, copy=False)
    out = np.full_like(F, np.nan)
    for t in range(F.shape[0]):
        y = F[t]
        x = S[t]
        m = np.isfinite(y) & np.isfinite(x)
        n = int(m.sum())
        if n < 30:
            continue
        yy = y[m]
        xx = x[m]
        yy0 = yy - yy.mean()
        xx0 = xx - xx.mean()
        var = float(np.dot(xx0, xx0))
        if var < 1e-18:
            out[t, m] = yy0
            continue
        beta = float(np.dot(xx0, yy0) / var)
        resid = np.full(y.shape, np.nan)
        resid[m] = yy0 - beta * xx0
        out[t] = resid
    return pd.DataFrame(out, index=idx, columns=cols, dtype="float32")


def industry_demean(fac: pd.DataFrame, ind_codes: np.ndarray) -> pd.DataFrame:
    """Cheap SW L1 demean per day. ind_codes length = n_cols, -1 = unknown."""
    idx = fac.index
    cols = list(fac.columns)
    F = fac.to_numpy(dtype=np.float64, copy=False)
    out = np.full_like(F, np.nan)
    uniq = np.unique(ind_codes[ind_codes >= 0])
    for t in range(F.shape[0]):
        y = F[t]
        for g in uniq:
            m = (ind_codes == g) & np.isfinite(y)
            if m.sum() < 3:
                continue
            out[t, m] = y[m] - y[m].mean()
        # unknowns: leave as demeaned vs all finite
        mu = (ind_codes < 0) & np.isfinite(y)
        if mu.sum() >= 3:
            out[t, mu] = y[mu] - y[mu].mean()
    return pd.DataFrame(out, index=idx, columns=cols, dtype="float32")


def build_sw_codes(cols: list[str]) -> tuple[np.ndarray, dict]:
    meta = {"ok": False, "n_mapped": 0}
    if not SW_L1.exists():
        meta["error"] = "missing_sw"
        return np.full(len(cols), -1, dtype=np.int32), meta
    df = pd.read_parquet(SW_L1)
    # QuantLab SW L1: instrument_id + sw_name (+ sw_code)
    if "instrument_id" not in df.columns:
        meta["error"] = f"bad_cols:{list(df.columns)[:10]}"
        return np.full(len(cols), -1, dtype=np.int32), meta
    ind_col = "sw_name" if "sw_name" in df.columns else ("sw_code" if "sw_code" in df.columns else None)
    if ind_col is None:
        meta["error"] = f"no_ind_col:{list(df.columns)[:10]}"
        return np.full(len(cols), -1, dtype=np.int32), meta
    df = df.copy()
    df["_bs"] = df["instrument_id"].astype(str)
    # prefer latest membership (out_date null / max in_date)
    if "in_date" in df.columns:
        df["_in"] = pd.to_datetime(df["in_date"], errors="coerce")
        df = df.sort_values("_in")
    names = sorted(df[ind_col].dropna().astype(str).unique())
    name2i = {n: i for i, n in enumerate(names)}
    gmap = df.groupby("_bs")[ind_col].agg(lambda s: str(s.iloc[-1]))
    codes = np.full(len(cols), -1, dtype=np.int32)
    for j, c in enumerate(cols):
        if c in gmap.index:
            codes[j] = name2i.get(str(gmap.loc[c]), -1)
    meta.update({"ok": True, "n_mapped": int((codes >= 0).sum()), "n_ind": len(names), "ind_col": ind_col})
    return codes, meta


def _ann(sim, path):
    cur = sim
    for p in path:
        if not isinstance(cur, dict):
            return float("nan")
        cur = cur.get(p)
    if isinstance(cur, dict):
        return cur.get("ann", float("nan"))
    return float("nan")


def pack_metrics(sim: dict | None) -> dict:
    if not isinstance(sim, dict) or "flat" not in sim:
        return {
            "gross": float("nan"),
            "flat10": float("nan"),
            "flat25": float("nan"),
            "imp60": float("nan"),
            "imp100": float("nan"),
            "imp60_p25": float("nan"),
            "imp100_p25": float("nan"),
            "icir": float("nan"),
            "ic_mean": float("nan"),
            "turn": float("nan"),
        }
    return {
        "gross": _ann(sim, ["gross"]),
        "flat10": _ann(sim, ["flat", "10"]),
        "flat25": _ann(sim, ["flat", "25"]),
        "imp60": _ann(sim, ["impact", "600000"]),
        "imp100": _ann(sim, ["impact", "1000000"]),
        "imp60_p25": _ann(sim, ["impact", "600000_plus_flat25"]),
        "imp100_p25": _ann(sim, ["impact", "1000000_plus_flat25"]),
        "icir": float(sim.get("icir") or float("nan")),
        "ic_mean": float(sim.get("ic_mean") or float("nan")),
        "turn": float(sim.get("mean_turn_ow") or float("nan")),
    }


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


def fmt_pct(x):
    if isinstance(x, float) and math.isfinite(x):
        return f"{x:.2%}"
    return "—"


def fmt_f(x, nd=4):
    if isinstance(x, float) and math.isfinite(x):
        return f"{x:.{nd}f}"
    return "—"


def event_leaf_for(expr: str, panels: dict) -> pd.DataFrame | None:
    """Pick underlying event leaf for Top-N event share."""
    L = leaves_in(expr)
    priority = [
        "ann_insider_dec_5",
        "ann_insider_dec_10",
        "ann_insider_dec_20",
        "ann_penalty_10",
        "ann_penalty_5",
        "ann_buyback_10",
        "ann_buyback_5",
        "ann_inquiry_letter_5",
        "ann_inquiry_any_5",
        "ann_inquiry_reply_5",
        "lockup_S_5",
        "lockup_S_60",
        "lockup_days_to",
    ]
    for p in priority:
        if p in L and p in panels:
            return panels[p]
    for p in L:
        if p in panels:
            return panels[p]
    return None


def build_insider_window_panels(panels, cal, cols, mask):
    """Build ann_insider_dec_10/20 from daily counts if we can recover from _5 or rebuild."""
    # Prefer rebuild from corpus via l1c daily path; cheapest: difference of rolling not available.
    # Rebuild lightweight from corpus same as l1c but only insider.
    l1c = sys.modules.get("ai_factor_l1c_explore")
    if l1c is None:
        return {}, {"ok": False, "error": "l1c_not_loaded"}
    V2 = getattr(l1c, "V2", ROOT / "data/v2")
    path = V2 / "text/ann_embedding_corpus_pit.parquet"
    gap = {"path": str(path), "body_source": "title_only", "invented_body": False}
    if not path.exists():
        gap["ok"] = False
        return {}, gap
    ann = pd.read_parquet(path, columns=["available_at", "instrument", "event_type", "body_source"])
    ann["available_at"] = pd.to_datetime(ann["available_at"])
    if getattr(ann["available_at"].dt, "tz", None) is not None:
        ann["avail_date"] = (
            ann["available_at"].dt.tz_convert("Asia/Shanghai").dt.normalize().dt.tz_localize(None)
        )
    else:
        ann["avail_date"] = pd.to_datetime(ann["available_at"]).dt.normalize()
    to_bs = getattr(l1c, "_to_baostock")
    ann["bs"] = ann["instrument"].map(to_bs)
    ann = ann[ann["bs"].astype(str).str.len() > 0]
    ann = ann[ann["bs"].isin(cols)]
    ann = ann[ann["event_type"].astype(str) == "insider_decrease"]
    gap.update(
        {
            "ok": True,
            "n_insider_rows": int(len(ann)),
            "body_source_counts": ann["body_source"].value_counts().to_dict()
            if "body_source" in ann.columns
            else {},
        }
    )
    col_index = {c: i for i, c in enumerate(cols)}
    cal_np = cal.values.astype("datetime64[ns]")
    T, N = len(cal), len(cols)
    daily = np.zeros((T, N), dtype=np.float32)
    for row in ann.itertuples(index=False):
        j = col_index.get(row.bs)
        if j is None:
            continue
        d = pd.Timestamp(row.avail_date)
        i = int(np.searchsorted(cal_np, np.datetime64(d), side="left"))
        if i >= T:
            continue
        if i < T and cal[i] != d:
            if i < T and cal_np[i] < np.datetime64(d):
                i += 1
            if i >= T:
                continue
        daily[i, j] += 1.0
    base = pd.DataFrame(daily, index=cal, columns=cols, dtype="float32")
    out = {
        "ann_insider_dec_daily": base.where(mask) if mask is not None else base,
        "ann_insider_dec_10": base.rolling(10, min_periods=1).sum().astype("float32"),
        "ann_insider_dec_20": base.rolling(20, min_periods=1).sum().astype("float32"),
    }
    if mask is not None:
        for k in ("ann_insider_dec_10", "ann_insider_dec_20"):
            out[k] = out[k].where(mask).astype("float32")
    # ensure _5 exists / refresh
    if "ann_insider_dec_5" not in panels:
        out["ann_insider_dec_5"] = base.rolling(5, min_periods=1).sum().astype("float32")
        if mask is not None:
            out["ann_insider_dec_5"] = out["ann_insider_dec_5"].where(mask).astype("float32")
    gap["nonzero_frac_dec_10"] = float((out["ann_insider_dec_10"] > 0).to_numpy().mean())
    gap["nonzero_frac_dec_20"] = float((out["ann_insider_dec_20"] > 0).to_numpy().mean())
    del ann, daily, base
    gc.collect()
    return out, gap


def deepen_jobs() -> list[dict]:
    """Variants around honest-3 + static controls. No LD/broadcast."""
    jobs = []

    def add(role, expr, note="", parent=None):
        jobs.append(
            {
                "role": role,
                "expr": expr,
                "note": note,
                "parent": parent or expr,
                "family": "ann_insider_dec",
            }
        )

    for e in HONEST3:
        add("honest3_baseline", e, "L1c honest-3 baseline", e)

    # static univariate
    add("static", "ann_insider_dec_5", "static leaf")
    add("static", "rank(ann_insider_dec_5)", "static rank")
    add("static", "zscore(ann_insider_dec_5)", "static zscore")
    add("static", "neg(ann_insider_dec_5)", "static neg")
    add("static", "rank(neg(ann_insider_dec_5))", "static rank neg")

    # window / transform deepen
    deepen_exprs = [
        ("ts_std_5(ann_insider_dec_5)", "shorter ts_std"),
        ("ts_std_20(ann_insider_dec_5)", "longer ts_std"),
        ("rank(ts_std_5(ann_insider_dec_5))", "rank+ts_std_5"),
        ("rank(ts_std_20(ann_insider_dec_5))", "rank+ts_std_20"),
        ("zscore(ts_std_10(ann_insider_dec_5))", "zscore wrap on honest#2"),
        ("rank(zscore(ann_insider_dec_5))", "rank zscore static"),
        ("ts_mean_10(ann_insider_dec_5)", "ts_mean alt"),
        ("ts_max_5(ann_insider_dec_5)", "single ts_max_5"),
        ("ts_max_10(ann_insider_dec_5)", "ts_max_10"),
        ("rank(ts_max_5(ann_insider_dec_5))", "rank ts_max_5"),
        ("rank(ts_max_10(ann_insider_dec_5))", "rank ts_max_10"),
        ("ts_std_10(ann_insider_dec_10)", "leaf window 10"),
        ("rank(ts_std_10(ann_insider_dec_10))", "rank ts_std on leaf10"),
        ("ts_std_10(ann_insider_dec_20)", "leaf window 20"),
        ("rank(ts_std_10(ann_insider_dec_20))", "rank ts_std on leaf20"),
        ("ts_max_5(ts_max_5(ann_insider_dec_10))", "double max on leaf10"),
        ("delay_5(rank(ts_std_10(ann_insider_dec_5)))", "delay5 honest#1"),
        ("delay_10(rank(ts_std_10(ann_insider_dec_5)))", "delay10 honest#1"),
        ("delay_20(rank(ts_std_10(ann_insider_dec_5)))", "delay20 honest#1"),
        ("delay_5(ts_std_10(ann_insider_dec_5))", "delay5 honest#2"),
        ("delay_20(ts_std_10(ann_insider_dec_5))", "delay20 honest#2"),
        ("neg(rank(ts_std_10(ann_insider_dec_5)))", "sign flip honest#1"),
        ("ts_delta_10(ann_insider_dec_5)", "delta of leaf"),
        ("abs(ts_std_10(ts_delta_5(ann_insider_dec_5)))", "vol of delta"),
        ("rank(ts_mean_10(ann_insider_dec_5))", "rank ts_mean"),
    ]
    for e, note in deepen_exprs:
        add("deepen", e, note)

    # size / industry residual tokens
    for e in HONEST3:
        add("size_resid", f"__SIZE_RESID__::{e}", "size residual", e)
        add("ind_resid", f"__IND_RESID__::{e}", "SW L1 demean residual", e)

    # dedupe
    seen = set()
    out = []
    for j in jobs:
        tok = j["expr"]
        if tok in seen:
            continue
        seen.add(tok)
        out.append(j)
    return out


def evaluate_token(expr_token, panels, label, sig, adv, size_panel, ind_codes, *, need_top=False):
    from quantlab.factors.ops import apply_expr, parse_expr

    size_mode = expr_token.startswith("__SIZE_RESID__::")
    ind_mode = expr_token.startswith("__IND_RESID__::")
    expr = expr_token.split("::", 1)[1] if (size_mode or ind_mode) else expr_token
    tup = _seed_to_tuple(expr)
    fac = apply_expr(parse_expr(to_nested_tuple(tup)), panels)
    if not isinstance(fac, pd.DataFrame):
        raise TypeError(type(fac))
    fac = fac.astype("float32")
    if size_mode:
        if size_panel is None:
            return {
                "expr": expr,
                "expr_token": expr_token,
                "sim": {"error": "size_panel_unavailable", "promotion_approved": False},
                "cs_stats": None,
                "coverage": None,
                "topn_share": None,
            }
        fac = size_residualize(fac, size_panel)
    if ind_mode:
        fac = industry_demean(fac, ind_codes)
    cs = cs_std_stats(fac)
    cov = coverage_stats(fac, days_to_style=False)
    topn_share = None
    if not cs["passes_cs_variation"]:
        sim = {"skipped": True, "reason": "cs_variation_fail", "promotion_approved": False}
        explore_idx = None
        top_idx_list = None
    else:
        if need_top:
            sim, top_idx_list, explore_idx = simulate_book(fac, label, sig, adv, return_top=True)
            ev = event_leaf_for(expr, panels)
            if ev is not None and explore_idx is not None:
                topn_share = topn_event_share(ev, top_idx_list, explore_idx)
        else:
            sim = simulate_book(fac, label, sig, adv)
    del fac
    gc.collect()
    return {
        "expr": expr,
        "expr_token": expr_token,
        "size_resid": size_mode,
        "ind_resid": ind_mode,
        "sim": sim,
        "cs_stats": cs,
        "coverage": cov,
        "topn_share": topn_share,
        "leaves": sorted(leaves_in(expr)),
    }


def clean(o):
    if isinstance(o, float) and (math.isnan(o) or math.isinf(o)):
        return None
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, list):
        return [clean(x) for x in o]
    return o


def write_reports(short_rows, deep_rows, meta):
    lines = []
    lines.append("# AI 因子 L1d：短清单覆盖率诚实标注 + 60/100万冲击闸")
    lines.append("")
    lines.append(f"- **时间：** 2026-10-12（America/New_York）")
    lines.append("- **promotion_approved：** false；**密封：** 未开；**不交 Strategy 权重**")
    lines.append("- **trial_kind：** explore_gate / process")
    lines.append("- **本金主口径：** 60 万 / 100 万；主裁决=冲击+flat25")
    lines.append("- **禁止：** 广播叶、跌停主候选、小盘、教科书主线、密封、编造公告正文、Strategy 权重")
    lines.append("- **公告：** title_only（`invented_body=false`）")
    lines.append(
        f"- 账本：N {meta['ledger_N_before']} → {meta['ledger_N_after']}（+{meta['ledger_N_new']}，explore_gate）"
    )
    lines.append(
        f"- 峰值 RSS：{meta['peak_rss_MB']:.0f} MB（上限 {MEM_CAP_MB}；under_cap={meta['under_mem_cap']}）；运行 {meta['runtime_s']:.1f}s"
    )
    lines.append("- 上游：`AI_FACTOR_L1d_COVERAGE_MECH_SHORTLIST_ZH.md`；`AI_FACTOR_L1c_ANN_INSIDER_WF_STABILITY_ZH.md`")
    lines.append("")
    lines.append("## 覆盖率门槛（与 L1d 对齐）")
    lines.append("")
    lines.append("| 指标 | 门槛 |")
    lines.append("|---|---:|")
    lines.append(f"| nonempty_rate | ≥ {COV_NONEMPTY_MIN:.0%} |")
    lines.append(f"| mean_event_names | ≥ {COV_MEAN_EVENT_NAMES_MIN:.0f} |")
    lines.append(f"| frac_days≥20 | ≥ {COV_FRAC_DAYS_GE20_MIN:.0%} |")
    lines.append("| Top-N event share | 标注（不做硬闸；事件驱动头部预期高） |")
    lines.append("")
    lines.append("## 短清单 N=9：覆盖率 + flat25 + 冲击+flat25")
    lines.append("")
    lines.append(
        "| # | 来源 | 表达式 | flat25 | 60万+25bp | 100万+25bp | ICIR | 换手 | nonempty | 日均事件股 | TopN事件占比 | 覆盖 | 裁决 |"
    )
    lines.append("|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|")
    for i, r in enumerate(short_rows, 1):
        m = r["metrics"]
        c = r.get("coverage") or {}
        t = r.get("topn_share") or {}
        cov_tag = "PASS" if r.get("survive_coverage") else "SPARSE_WARN"
        verdict = r.get("verdict", "—")
        lines.append(
            f"| {i} | {r.get('source','')} | `{r['expr']}` | {fmt_pct(m.get('flat25'))} | "
            f"{fmt_pct(m.get('imp60_p25'))} | {fmt_pct(m.get('imp100_p25'))} | "
            f"{fmt_f(m.get('icir'),3)} | {fmt_f(m.get('turn'),3)} | "
            f"{fmt_f(c.get('nonempty_rate'),4)} | {fmt_f(c.get('mean_event_names'),1)} | "
            f"{fmt_pct(t.get('mean_topN_event_share'))} | {cov_tag} | {verdict} |"
        )
    lines.append("")
    lines.append("### 覆盖率明细 / 失败原因")
    lines.append("")
    for r in short_rows:
        c = r.get("coverage") or {}
        fr = c.get("fail_reasons") or []
        tag = "coverage-pass" if r.get("survive_coverage") else "sparse-warned"
        lines.append(
            f"- `{r['expr']}` → **{tag}**"
            + (f"；失败：{', '.join(fr)}" if fr else "")
            + f"；TopN事件占比={fmt_pct((r.get('topn_share') or {}).get('mean_topN_event_share'))}"
        )
    lines.append("")
    n_pass = sum(1 for r in short_rows if r.get("survive_coverage"))
    n_gate = sum(1 for r in short_rows if r.get("verdict") == "GATE_OK")
    n_sparse_ok = sum(
        1 for r in short_rows if r.get("verdict") == "GATE_OK_SPARSE_WARN"
    )
    lines.append("## 短清单总裁决")
    lines.append("")
    lines.append(
        f"1. **覆盖率硬过闸：** {n_pass}/{len(short_rows)}；其余为 **sparse-warned**（仍可保留 explore，不可当作稳健密度）。"
    )
    lines.append(
        f"2. **冲击闸（flat25>0 且 60/100万+25bp≥10%）：** GATE_OK={n_gate}；GATE_OK_SPARSE_WARN={n_sparse_ok}；其余见上表。"
    )
    lines.append("3. **不开密封、不交 Strategy**；`promotion_approved=false`。")
    lines.append("4. **优先加深：** 见姐妹报告 `AI_FACTOR_L1d_ANN_INSIDER_DEC_DEEPEN_ZH.md`。")
    lines.append("")
    lines.append("## 产物路径")
    lines.append("")
    lines.append("- 报告：`output/alpha/AI_FACTOR_L1d_SHORTLIST_COVERAGE_IMPACT_ZH.md`")
    lines.append("- 加深报告：`output/alpha/AI_FACTOR_L1d_ANN_INSIDER_DEC_DEEPEN_ZH.md`")
    lines.append(
        "- JSON：`output/ai_factor/l1d_shortlist_coverage_impact/`（shortlist_annotated/summary/…；deepen 子目录）"
    )
    lines.append(f"- 账本：`output/ai_factor/ledger.jsonl` N={meta['ledger_N_after']}")
    lines.append("")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # deepen report
    honest_m = {
        r["expr"]: r["metrics"]
        for r in deep_rows
        if r.get("role") == "honest3_baseline" and isinstance(r.get("metrics"), dict)
    }
    best_h60 = max(
        (m.get("imp60_p25") or float("-inf") for m in honest_m.values()),
        default=float("nan"),
    )
    lines = []
    lines.append("# AI 因子 L1d：ann_insider_dec 族加深（相对 honest-3）")
    lines.append("")
    lines.append("- **promotion_approved：** false；**密封：** 未开；**不交 Strategy**")
    lines.append("- **title_only**；禁广播/跌停主候选/小盘/教科书")
    lines.append("- **对照基线（honest-3）：**")
    for e in HONEST3:
        m = honest_m.get(e) or {}
        lines.append(
            f"  - `{e}` → flat25={fmt_pct(m.get('flat25'))}；60万+25bp={fmt_pct(m.get('imp60_p25'))}；"
            f"100万+25bp={fmt_pct(m.get('imp100_p25'))}"
        )
    lines.append(f"- honest-3 最佳 60万+25bp ≈ {fmt_pct(best_h60)}")
    lines.append("")
    lines.append("## 加深候选（相对 best honest-3 的 Δ60万+25bp）")
    lines.append("")
    lines.append(
        "| # | role | 表达式 | flat25 | 60万+25bp | 100万+25bp | Δ vs H3 | ICIR | 换手 | CS | 备注 |"
    )
    lines.append("|---|---|---|---:|---:|---:|---:|---:|---:|---|---|")
    ranked = sorted(
        [r for r in deep_rows if isinstance(r.get("metrics"), dict)],
        key=lambda r: -(r["metrics"].get("imp60_p25") or -1e9),
    )
    lift_exprs = []
    for i, r in enumerate(ranked, 1):
        m = r["metrics"]
        dlt = (
            m["imp60_p25"] - best_h60
            if math.isfinite(m.get("imp60_p25", float("nan"))) and math.isfinite(best_h60)
            else float("nan")
        )
        cs_ok = (r.get("cs_stats") or {}).get("passes_cs_variation")
        note = r.get("note") or ""
        if (
            r.get("role") in ("deepen", "size_resid", "ind_resid")
            and math.isfinite(dlt)
            and dlt >= 0.005
            and math.isfinite(m.get("imp60_p25", float("nan")))
            and m["imp60_p25"] >= IMP60_FLOOR
            and math.isfinite(m.get("flat25", float("nan")))
            and m["flat25"] > 0
            and cs_ok
        ):
            lift_exprs.append((r["expr"], dlt, m))
            note = (note + "; **LIFT**").strip("; ")
        lines.append(
            f"| {i} | {r.get('role')} | `{r['expr']}` | {fmt_pct(m.get('flat25'))} | "
            f"{fmt_pct(m.get('imp60_p25'))} | {fmt_pct(m.get('imp100_p25'))} | "
            f"{fmt_pct(dlt) if math.isfinite(dlt) else '—'} | {fmt_f(m.get('icir'),3)} | "
            f"{fmt_f(m.get('turn'),3)} | {'OK' if cs_ok else 'FAIL'} | {note[:40]} |"
        )
    lines.append("")
    lines.append("## 静态对照摘要")
    lines.append("")
    for r in deep_rows:
        if r.get("role") != "static":
            continue
        m = r.get("metrics") or {}
        lines.append(
            f"- `{r['expr']}` → 60万+25bp={fmt_pct(m.get('imp60_p25'))}；flat25={fmt_pct(m.get('flat25'))}"
        )
    lines.append("")
    lines.append("## 诚实裁决：哪些加深相对 honest-3 有增量")
    lines.append("")
    if not lift_exprs:
        lines.append(
            "- **无 deepen/残差叶相对 honest-3 最佳线提升 ≥50bp 且过 10% 冲击闸。** "
            "窗口/delay/zscore/行业残差未提供稳健增量；honest-3 仍为 ann_insider_dec 族短清单核心。"
        )
    else:
        lines.append(f"- **有增量（≥50bp @60万+25bp 且过闸）：{len(lift_exprs)} 条**")
        for e, dlt, m in sorted(lift_exprs, key=lambda x: -x[1]):
            lines.append(
                f"  - `{e}`：Δ={fmt_pct(dlt)} → 60万+25bp={fmt_pct(m.get('imp60_p25'))}"
            )
    lines.append("- 静态单叶显著弱于变换（与 L1c 消融一致）则变换结构仍必要。")
    lines.append("- **不开密封、不交 Strategy**；`promotion_approved=false`。")
    lines.append("")
    lines.append("## 产物")
    lines.append("")
    lines.append("- `output/alpha/AI_FACTOR_L1d_ANN_INSIDER_DEC_DEEPEN_ZH.md`")
    lines.append("- `output/ai_factor/l1d_shortlist_coverage_impact/ann_insider_dec_deepen/`")
    lines.append("")
    REPORT_DEEP.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    global t0
    t0 = time.time()
    peak = mem_mb()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DEEP_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    shortlist = json.loads(SHORTLIST_PATH.read_text())
    assert len(shortlist) == 9, len(shortlist)
    log("shortlist N", len(shortlist))

    _ensure_pkgs()
    l1b = _import_mod("ai_factor_l1b_structural_explore", ROOT / "research/ai_factor_l1b_structural_explore.py")
    l1c = _import_mod("ai_factor_l1c_explore", ROOT / "research/ai_factor_l1c_explore.py")
    l1d = _import_mod("ai_factor_l1d_non_ld_struct_explore", ROOT / "research/ai_factor_l1d_non_ld_struct_explore.py")
    from quantlab.factors.ai_factory.ledger import append_attempt

    log("loading panels")
    panels, label, public, load_meta = l1b.load_structural_panels()
    peak = max(peak, mem_mb())
    panels, label, public, load_meta = l1c.attach_l1c_panels(panels, label, public, load_meta)
    peak = max(peak, mem_mb())
    size_panel = None
    if isinstance(public, dict) and public.get("size") is not None:
        size_panel = public["size"].astype("float32")
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

    log("lockup + ann extra panels")
    lock_panels, lock_gap = l1d.build_lockup_calendar_panels(cal, cols, mask)
    panels.update(lock_panels)
    del lock_panels
    gc.collect()
    ann_panels, ann_gap = l1d.build_ann_title_extra_panels(cal, cols, mask)
    panels.update(ann_panels)
    del ann_panels
    gc.collect()
    peak = max(peak, mem_mb())

    # deepen windows for insider
    log("insider window panels 10/20")
    win_panels, win_gap = build_insider_window_panels(panels, cal, cols, mask)
    panels.update(win_panels)
    del win_panels
    gc.collect()
    peak = max(peak, mem_mb())
    log("panels", len(panels), "peak", peak)

    # trim to needed leaves
    jobs_deep = deepen_jobs()
    needed = set()
    for s in shortlist:
        needed |= leaves_in(s["expr"])
    for j in jobs_deep:
        e = j["expr"].split("::", 1)[-1]
        needed |= leaves_in(e)
    # keep event leaves for topn share
    needed |= {
        "ann_insider_dec_5",
        "ann_insider_dec_10",
        "ann_insider_dec_20",
        "ann_penalty_10",
        "ann_buyback_10",
        "ann_inquiry_letter_5",
        "ann_inquiry_any_5",
        "lockup_S_5",
        "lockup_S_60",
    }
    for k in list(panels.keys()):
        if k not in needed:
            del panels[k]
    gc.collect()
    log("trimmed", sorted(panels.keys()), "mem", mem_mb())

    cols = list(next(iter(panels.values())).columns)
    cal = next(iter(panels.values())).index
    sig, adv = load_sig_adv(cols, cal)
    peak = max(peak, mem_mb())
    ind_codes, sw_meta = build_sw_codes(cols)
    log("sig/adv", sig.shape, "sw", sw_meta, "peak", peak)

    main_ledger = ROOT / "output/ai_factor/ledger.jsonl"
    run_ledger = OUT_DIR / "ledger_run.jsonl"
    if run_ledger.exists():
        run_ledger.unlink()
    n_before = (
        sum(1 for x in main_ledger.read_text().splitlines() if x.strip())
        if main_ledger.exists()
        else 0
    )

    # ---- 1) shortlist annotate ----
    short_rows = []
    for i, s in enumerate(shortlist):
        expr = s["expr"]
        try:
            ev = evaluate_token(
                expr, panels, label, sig, adv, size_panel, ind_codes, need_top=True
            )
        except Exception as exc:  # noqa: BLE001
            ev = {
                "expr": expr,
                "expr_token": expr,
                "sim": {"error": f"{type(exc).__name__}: {exc}", "promotion_approved": False},
                "cs_stats": None,
                "coverage": None,
                "topn_share": None,
            }
        m = pack_metrics(ev.get("sim"))
        cov = ev.get("coverage") or {}
        survive_cov = bool(cov.get("passes_coverage"))
        gate_ok = (
            math.isfinite(m.get("flat25", float("nan")))
            and m["flat25"] > 0
            and math.isfinite(m.get("imp60_p25", float("nan")))
            and m["imp60_p25"] >= IMP60_FLOOR
            and math.isfinite(m.get("imp100_p25", float("nan")))
            and m["imp100_p25"] >= IMP60_FLOOR
            and bool((ev.get("cs_stats") or {}).get("passes_cs_variation"))
        )
        if gate_ok and survive_cov:
            verdict = "GATE_OK"
        elif gate_ok and not survive_cov:
            verdict = "GATE_OK_SPARSE_WARN"
        elif not gate_ok:
            verdict = "FAIL_GATE"
        else:
            verdict = "FAIL"
        row = {
            **s,
            "metrics": m,
            "coverage": cov,
            "topn_share": ev.get("topn_share"),
            "cs_stats": ev.get("cs_stats"),
            "survive_coverage": survive_cov,
            "gate_ok": gate_ok,
            "verdict": verdict,
            "promotion_approved": False,
            "trial_kind": "explore_gate",
        }
        short_rows.append(row)
        fit = m.get("imp60_p25")
        notes = (
            f"l1d_shortlist_coverage_impact;verdict={verdict};"
            f"cov_pass={survive_cov};process_not_sealed;promotion_approved=false"
        )
        for path in (run_ledger, main_ledger):
            append_attempt(
                engine="l1d_shortlist_coverage_impact",
                seed=SEED,
                universe="midlarge_top1500_or_csi300_500",
                cost=0.0025,
                window="explore_20240603_to_latest_l1d_sci",
                expr_str=expr,
                fitness=fit if isinstance(fit, float) and math.isfinite(fit) else None,
                notes=notes,
                path=path,
            )
        peak = max(peak, mem_mb())
        log(
            f"short {i+1}/9",
            expr[:50],
            verdict,
            "60+25",
            fmt_pct(fit),
            "cov",
            survive_cov,
            "peak",
            peak,
        )
        if mem_mb() > MEM_CAP_MB - 100:
            gc.collect()

    # ---- 2) deepen ann_insider_dec ----
    deep_rows = []
    for i, job in enumerate(jobs_deep):
        tok = job["expr"]
        try:
            ev = evaluate_token(
                tok, panels, label, sig, adv, size_panel, ind_codes, need_top=False
            )
        except Exception as exc:  # noqa: BLE001
            ev = {
                "expr": tok.split("::", 1)[-1],
                "expr_token": tok,
                "sim": {"error": f"{type(exc).__name__}: {exc}", "promotion_approved": False},
                "cs_stats": None,
                "coverage": None,
                "topn_share": None,
            }
        m = pack_metrics(ev.get("sim"))
        row = {
            **job,
            "expr": ev.get("expr") or tok.split("::", 1)[-1],
            "expr_token": tok,
            "metrics": m,
            "coverage": ev.get("coverage"),
            "cs_stats": ev.get("cs_stats"),
            "size_resid": ev.get("size_resid"),
            "ind_resid": ev.get("ind_resid"),
            "promotion_approved": False,
            "trial_kind": "explore_gate",
        }
        deep_rows.append(row)
        fit = m.get("imp60_p25")
        notes = (
            f"l1d_ann_insider_dec_deepen;role={job.get('role')};"
            f"process_not_sealed;promotion_approved=false"
        )
        for path in (run_ledger, main_ledger):
            append_attempt(
                engine="l1d_ann_insider_dec_deepen",
                seed=SEED,
                universe="midlarge_top1500_or_csi300_500",
                cost=0.0025,
                window="explore_20240603_to_latest_l1d_sci_deep",
                expr_str=row["expr"],
                fitness=fit if isinstance(fit, float) and math.isfinite(fit) else None,
                notes=notes,
                path=path,
            )
        if (i + 1) % 5 == 0 or i == 0 or i + 1 == len(jobs_deep):
            peak = max(peak, mem_mb())
            log(
                f"deep {i+1}/{len(jobs_deep)}",
                row["expr"][:55],
                "60+25",
                fmt_pct(fit),
                "peak",
                peak,
            )
        if mem_mb() > MEM_CAP_MB - 100:
            gc.collect()

    peak = max(peak, mem_mb())
    n_after = (
        sum(1 for x in main_ledger.read_text().splitlines() if x.strip())
        if main_ledger.exists()
        else 0
    )

    # lift summary
    honest_m = {
        r["expr"]: r["metrics"]
        for r in deep_rows
        if r.get("role") == "honest3_baseline"
    }
    best_h60 = max(
        (m.get("imp60_p25") or float("-inf") for m in honest_m.values()),
        default=float("nan"),
    )
    lifts = []
    for r in deep_rows:
        if r.get("role") not in ("deepen", "size_resid", "ind_resid"):
            continue
        m = r.get("metrics") or {}
        if not (r.get("cs_stats") or {}).get("passes_cs_variation"):
            continue
        dlt = (
            m["imp60_p25"] - best_h60
            if math.isfinite(m.get("imp60_p25", float("nan"))) and math.isfinite(best_h60)
            else float("nan")
        )
        if (
            math.isfinite(dlt)
            and dlt >= 0.005
            and m.get("imp60_p25", float("nan")) >= IMP60_FLOOR
            and m.get("flat25", float("nan")) > 0
            and m.get("imp100_p25", float("nan")) >= IMP60_FLOOR
        ):
            lifts.append(
                {
                    "expr": r["expr"],
                    "role": r["role"],
                    "delta_imp60_p25": dlt,
                    "imp60_p25": m["imp60_p25"],
                    "imp100_p25": m.get("imp100_p25"),
                    "flat25": m.get("flat25"),
                }
            )

    meta = {
        "mode": "l1d_shortlist_coverage_impact_plus_ann_insider_dec_deepen",
        "promotion_approved": False,
        "sealed_executed": False,
        "trial_kind": "explore_gate",
        "ann_title_only": True,
        "invented_body": False,
        "n_shortlist": len(short_rows),
        "n_coverage_pass": sum(1 for r in short_rows if r.get("survive_coverage")),
        "n_gate_ok": sum(1 for r in short_rows if r.get("verdict") == "GATE_OK"),
        "n_gate_ok_sparse": sum(
            1 for r in short_rows if r.get("verdict") == "GATE_OK_SPARSE_WARN"
        ),
        "n_deepen_jobs": len(deep_rows),
        "n_lift_vs_honest3": len(lifts),
        "best_honest3_imp60_p25": best_h60 if math.isfinite(best_h60) else None,
        "lifts": lifts,
        "lock_gap": lock_gap,
        "ann_gap": ann_gap,
        "win_gap": win_gap,
        "sw_meta": sw_meta,
        "ledger_N_before": n_before,
        "ledger_N_after": n_after,
        "ledger_N_new": n_after - n_before,
        "peak_rss_MB": peak,
        "mem_cap_MB": MEM_CAP_MB,
        "under_mem_cap": peak < MEM_CAP_MB,
        "runtime_s": round(time.time() - t0, 1),
    }

    (OUT_DIR / "shortlist_annotated.json").write_text(
        json.dumps(clean(short_rows), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "summary.json").write_text(
        json.dumps(clean(meta), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (DEEP_DIR / "results.json").write_text(
        json.dumps(clean(deep_rows), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (DEEP_DIR / "lifts.json").write_text(
        json.dumps(clean(lifts), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (DEEP_DIR / "summary.json").write_text(
        json.dumps(
            clean(
                {
                    "honest3": HONEST3,
                    "best_honest3_imp60_p25": best_h60 if math.isfinite(best_h60) else None,
                    "n_jobs": len(deep_rows),
                    "n_lift": len(lifts),
                    "lifts": lifts,
                    "promotion_approved": False,
                }
            ),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    write_reports(short_rows, deep_rows, meta)
    log(
        "DONE",
        "short",
        meta["n_gate_ok"],
        "+",
        meta["n_gate_ok_sparse"],
        "sparsewarn",
        "lifts",
        len(lifts),
        "N",
        n_after,
        "peak",
        peak,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
