#!/usr/bin/env python3
"""L1d NON-LD structural leaf exploration (explore window).

Families:
  - Lockup calendar variants (lockup_S_*/days_to/flag)
  - Announcement title event families beyond ann_insider_dec_5
    (inquiry_letter/reply, insider_increase, buyback/penalty/earn/n with transforms)

Bans: broadcast (mkt_*/etf_*/if_basis*), limit_down_*/ld_* as primary,
      small-cap, textbook mainline, sealed, Strategy weights, invented ann body.
promotion_approved=False. Memory < 2.5GB.
Cost gate + sqrt impact @ 60万 / 100万. Mid/large only. title_only.
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
OUT_DIR = ROOT / "output/ai_factor/l1d_non_ld_struct_explore"
REPORT = ROOT / "output/alpha/AI_FACTOR_L1d_NON_LD_STRUCT_EXPLORE_ZH.md"
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

OPS = {
    "add", "sub", "mul", "div", "neg", "abs", "rank", "zscore",
    "industry_neutral", "size_neutral",
}
for k in (1, 5, 10, 20):
    OPS |= {f"delay_{k}", f"ts_mean_{k}", f"ts_std_{k}", f"ts_delta_{k}", f"ts_max_{k}"}

# Primary leaves allowed in L1d (NON-LD, NON-broadcast)
ALLOWED_PREFIXES = ("lockup_", "ann_")
BANNED_EXACT = frozenset(
    {
        "mkt_max_height", "mkt_lu_breadth", "etf_major_flow", "etf_theme_flow",
        "if_basis", "if_basis_x_on", "if_basis_x_lu", "etf_flow_x_lu",
        "theme_lu_density",
    }
)
BANNED_PREFIXES = ("mkt_", "etf_", "if_basis", "limit_down_", "ld_")
# Prior family already explored deeply — keep as optional control only, not primary batch
PRIOR_FAMILY = ("ann_insider_dec_5",)

t0 = 0.0


def mem_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def log(*a):
    print(f"[l1d_struct {time.time()-t0:5.0f}s {mem_mb():.0f}MB]", *a, flush=True)


def leaves_in(expr: str) -> set[str]:
    return {t for t in re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", expr) if t not in OPS}


def is_broadcast(name: str) -> bool:
    if name in BANNED_EXACT:
        return True
    return any(name.startswith(p) for p in ("mkt_", "etf_", "if_basis"))


def is_ld(name: str) -> bool:
    return (
        name.startswith("limit_down_")
        or name.startswith("ld_")
        or name == "days_since_ld"
    )


def is_allowed_primary(name: str) -> bool:
    if is_broadcast(name) or is_ld(name):
        return False
    if name in PRIOR_FAMILY:
        return False  # not this batch's primary
    return name.startswith("lockup_") or name.startswith("ann_")


def expr_is_l1d_primary(expr: str) -> bool:
    L = leaves_in(expr)
    if not L:
        return False
    if any(is_broadcast(x) or is_ld(x) for x in L):
        return False
    if any(x in PRIOR_FAMILY for x in L):
        return False
    return all(is_allowed_primary(x) for x in L)


def family_of(expr: str) -> str:
    L = sorted(leaves_in(expr))
    if not L:
        return "unknown"
    if all(x.startswith("lockup_") for x in L):
        return "lockup_calendar"
    if all(x.startswith("ann_") for x in L):
        # sub-family by dominant leaf stem
        stems = []
        for x in L:
            if "inquiry_letter" in x:
                stems.append("ann_inquiry_letter")
            elif "inquiry_reply" in x:
                stems.append("ann_inquiry_reply")
            elif "inquiry_any" in x:
                stems.append("ann_inquiry_any")
            elif "insider_inc" in x:
                stems.append("ann_insider_inc")
            elif "buyback" in x:
                stems.append("ann_buyback")
            elif "penalty" in x:
                stems.append("ann_penalty")
            elif "earn" in x:
                stems.append("ann_earn")
            elif x.startswith("ann_n"):
                stems.append("ann_n")
            else:
                stems.append("ann_other")
        uniq = sorted(set(stems))
        if len(uniq) == 1:
            return uniq[0]
        return "ann_mixed:" + "+".join(uniq)
    if any(x.startswith("lockup_") for x in L) and any(x.startswith("ann_") for x in L):
        return "lockup_x_ann"
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
    # binary ops: split on top-level comma
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
            if split_at is not None:
                a, b = inner[:split_at].strip(), inner[split_at + 1 :].strip()
                return ("op", op, _seed_to_tuple(a), _seed_to_tuple(b))
    raise ValueError(f"cannot parse seed: {s}")


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


def simulate_book(factor, label, sig, adv, *, top_n=TOP_N):
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
    median_std = float(daily_std.median())
    frac_near_zero = float((daily_std.fillna(0) < CS_STD_MIN).mean())
    frac_const = float((daily_nuniq.fillna(1) <= 1).mean())
    return {
        "cs_std_mean": mean_std,
        "cs_std_median": median_std,
        "frac_days_near_zero_std": frac_near_zero,
        "frac_days_constant_cs": frac_const,
        "passes_cs_variation": bool(
            mean_std > CS_STD_MIN and frac_near_zero < 0.5 and frac_const < 0.5
        ),
    }


def _ann(sim, path):
    cur = sim
    for p in path:
        if not isinstance(cur, dict):
            return float("nan")
        cur = cur.get(p)
    if isinstance(cur, dict):
        return cur.get("ann", float("nan"))
    return float("nan")


def verdict_row(row: dict) -> tuple[bool, str]:
    sim = row.get("sim") or {}
    if "error" in sim:
        return False, f"eval_error:{sim['error'][:120]}"
    if sim.get("skipped"):
        return False, sim.get("reason") or "skipped"
    cs = row.get("cs_stats") or {}
    if not cs.get("passes_cs_variation"):
        return False, (
            f"cs_variation_fail:std_mean={cs.get('cs_std_mean')},"
            f"frac_zero={cs.get('frac_days_near_zero_std')},"
            f"frac_const={cs.get('frac_days_constant_cs')}"
        )
    # Primary cost gate (L1c CS gate aligned): flat25>0 AND impact+flat25 @60/100万 >0
    flat25 = _ann(sim, ["flat", "25"])
    imp06 = _ann(sim, ["impact", "600000_plus_flat25"])
    imp10 = _ann(sim, ["impact", "1000000_plus_flat25"])
    fails = []
    if not (isinstance(flat25, float) and math.isfinite(flat25) and flat25 > 0):
        fails.append(f"flat25<={flat25}")
    if not (isinstance(imp06, float) and math.isfinite(imp06) and imp06 > 0):
        fails.append(f"impact+25bp_60万<={imp06}")
    if not (isinstance(imp10, float) and math.isfinite(imp10) and imp10 > 0):
        fails.append(f"impact+25bp_100万<={imp10}")
    if fails:
        return False, "cost_gate_fail:" + ";".join(fails)
    return True, "survive_cs_var+cost+60/100万_impact+25bp"


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
    for name in (
        "ledger",
        "novelty",
        "fitness",
        "evaluate",
        "search",
        "structural_leaves",
    ):
        load(
            f"quantlab.factors.ai_factory.{name}",
            ROOT / f"quantlab/factors/ai_factory/{name}.py",
        )


def _import_l1b():
    path = ROOT / "research/ai_factor_l1b_structural_explore.py"
    spec = importlib.util.spec_from_file_location("ai_factor_l1b_structural_explore", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ai_factor_l1b_structural_explore"] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _import_l1c():
    path = ROOT / "research/ai_factor_l1c_explore.py"
    spec = importlib.util.spec_from_file_location("ai_factor_l1c_explore", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ai_factor_l1c_explore"] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _to_baostock(ts_code: str) -> str:
    if ts_code is None or (isinstance(ts_code, float) and ts_code != ts_code):
        return ""
    s = str(ts_code)
    if s in ("", "nan", "None", "<NA>"):
        return ""
    if "." not in s:
        return s
    code, mkt = s.split(".", 1)
    return f"{mkt.lower()}.{code}"


def build_lockup_calendar_panels(
    index: pd.DatetimeIndex, columns: list[str], mask: pd.DataFrame | None
) -> tuple[dict[str, pd.DataFrame], dict]:
    """Lockup / unlock calendar family (PIT by ann_date). Horizons in calendar days ≈ trading windows."""
    sf_path = V2 / "share_float/share_float_2018plus.parquet"
    gap: dict = {"path": str(sf_path), "ok": False}
    # horizons: calendar days before float_date used as proxy for ~5/10/20/60 trading days
    horizons = {
        "lockup_S_5": 7,
        "lockup_S_10": 14,
        "lockup_S_20": 28,
        "lockup_S_60": 90,
    }
    empty = {
        k: pd.DataFrame(np.nan, index=index, columns=columns, dtype="float32")
        for k in list(horizons) + ["lockup_days_to", "lockup_flag_20", "lockup_near_5"]
    }
    if not sf_path.exists():
        gap["error"] = "missing_share_float"
        return empty, gap

    sf = pd.read_parquet(
        sf_path, columns=["ts_code", "ann_date", "float_date", "float_ratio"]
    )
    sf["ann_date"] = pd.to_datetime(sf["ann_date"])
    sf["float_date"] = pd.to_datetime(sf["float_date"])
    sf["bs"] = sf["ts_code"].map(_to_baostock)
    sf = sf[sf["bs"].isin(columns)]
    sf = sf[
        (sf["float_date"] >= LOOKBACK_START - pd.Timedelta(days=5))
        & (sf["float_date"] <= index.max() + pd.Timedelta(days=100))
    ]
    agg = (
        sf.groupby(["bs", "float_date", "ann_date"], as_index=False)["float_ratio"].sum()
    )
    gap.update({"ok": True, "n_events_used": int(len(agg))})
    del sf
    gc.collect()

    T, N = len(index), len(columns)
    col_index = {c: i for i, c in enumerate(columns)}
    cal_np = index.values.astype("datetime64[ns]")
    arrays = {k: np.zeros((T, N), dtype=np.float32) for k in horizons}
    days_to = np.full((T, N), np.nan, dtype=np.float32)
    # For days_to: track next unlock float_date per name after ann known
    # Build list of (j, float_date, ann_date, ratio) sorted by float_date
    events = []
    for row in agg.itertuples(index=False):
        j = col_index.get(row.bs)
        if j is None:
            continue
        ratio = float(row.float_ratio)
        if not np.isfinite(ratio) or ratio == 0.0:
            continue
        events.append((j, pd.Timestamp(row.float_date), pd.Timestamp(row.ann_date), ratio))
    events.sort(key=lambda x: x[1])

    for j, fdt, adt, ratio in events:
        for name, cal_days in horizons.items():
            start = max(adt + pd.Timedelta(days=1), fdt - pd.Timedelta(days=cal_days))
            end = fdt - pd.Timedelta(days=1)
            if end < start:
                continue
            i0 = int(np.searchsorted(cal_np, np.datetime64(start), side="left"))
            i1 = int(np.searchsorted(cal_np, np.datetime64(end), side="right"))
            if i0 < i1:
                arrays[name][i0:i1, j] += np.float32(ratio)
        # days_to: from max(ann+1, lookback) to float-1, set min days remaining
        start = adt + pd.Timedelta(days=1)
        end = fdt - pd.Timedelta(days=1)
        if end < start:
            continue
        i0 = int(np.searchsorted(cal_np, np.datetime64(start), side="left"))
        i1 = int(np.searchsorted(cal_np, np.datetime64(end), side="right"))
        for i in range(i0, min(i1, T)):
            d = (fdt - pd.Timestamp(index[i])).days
            if d < 0:
                continue
            prev = days_to[i, j]
            if not np.isfinite(prev) or d < prev:
                days_to[i, j] = np.float32(d)

    panels: dict[str, pd.DataFrame] = {}
    for name, arr in arrays.items():
        df = pd.DataFrame(arr, index=index, columns=columns, dtype="float32")
        if mask is not None:
            df = df.where(mask)
        panels[name] = df
    dto = pd.DataFrame(days_to, index=index, columns=columns, dtype="float32")
    if mask is not None:
        dto = dto.where(mask)
    panels["lockup_days_to"] = dto
    # flag: any unlock supply in S_20 window
    flag = (panels["lockup_S_20"] > 0).astype("float32")
    if mask is not None:
        flag = flag.where(mask)
    panels["lockup_flag_20"] = flag
    # near: unlock within 5 calendar days (small days_to)
    near = ((dto <= 5) & dto.notna()).astype("float32") * panels["lockup_S_20"].fillna(0)
    if mask is not None:
        near = near.where(mask)
    panels["lockup_near_5"] = near.astype("float32")

    for name, df in panels.items():
        nz = float((df.fillna(0) > 0).mean().mean()) if name != "lockup_days_to" else float(df.notna().mean().mean())
        gap[f"cov_{name}"] = nz
    del agg, arrays, days_to, events
    gc.collect()
    return panels, gap


def build_ann_title_extra_panels(
    index: pd.DatetimeIndex, columns: list[str], mask: pd.DataFrame | None
) -> tuple[dict[str, pd.DataFrame], dict]:
    """Title-only ann event counts: new families + extra roll windows. No body invent."""
    path = V2 / "text/ann_embedding_corpus_pit.parquet"
    leaf_names = (
        "ann_inquiry_letter_5",
        "ann_inquiry_reply_5",
        "ann_inquiry_any_5",
        "ann_insider_inc_5",
        "ann_buyback_5",
        "ann_buyback_10",
        "ann_penalty_5",
        "ann_penalty_10",
        "ann_earn_signed_5",
        "ann_earn_signed_10",
        "ann_n_5",
        "ann_n_10",
        "ann_n_20",
    )
    gap: dict = {
        "path": str(path),
        "body_source": "title_only",
        "invented_body": False,
        "embeddings_present": False,
    }
    empty = {
        k: pd.DataFrame(np.nan, index=index, columns=columns, dtype="float32")
        for k in leaf_names
    }
    if not path.exists():
        gap["ok"] = False
        gap["error"] = "missing_corpus"
        return empty, gap

    ann = pd.read_parquet(
        path, columns=["available_at", "instrument", "event_type", "body_source"]
    )
    ann["available_at"] = pd.to_datetime(ann["available_at"])
    if getattr(ann["available_at"].dt, "tz", None) is not None:
        ann["avail_date"] = (
            ann["available_at"]
            .dt.tz_convert("Asia/Shanghai")
            .dt.normalize()
            .dt.tz_localize(None)
        )
    else:
        ann["avail_date"] = pd.to_datetime(ann["available_at"]).dt.normalize()
    ann["bs"] = ann["instrument"].map(_to_baostock)
    ann = ann[ann["bs"].astype(str).str.len() > 0]
    ann = ann[ann["bs"].isin(columns)]
    gap.update(
        {
            "ok": True,
            "n_rows": int(len(ann)),
            "n_instruments": int(ann["bs"].nunique()),
            "body_source_counts": ann["body_source"].value_counts().to_dict()
            if "body_source" in ann.columns
            else {},
            "event_type_counts": ann["event_type"].value_counts().to_dict(),
        }
    )
    # assert title_only — do not invent body
    if "body_source" in ann.columns:
        bad = ann[ann["body_source"].astype(str) != "title_only"]
        gap["n_non_title_only"] = int(len(bad))
        if len(bad):
            # still use titles; never invent body text
            gap["note"] = "some rows non-title_only flagged; counts still from event_type only"

    col_index = {c: i for i, c in enumerate(columns)}
    cal_np = index.values.astype("datetime64[ns]")
    T, N = len(index), len(columns)

    def z():
        return np.zeros((T, N), dtype=np.float32)

    n_letter = z()
    n_reply = z()
    n_inc = z()
    n_buy = z()
    n_pen = z()
    n_earn = z()
    n_all = z()

    for row in ann.itertuples(index=False):
        j = col_index.get(row.bs)
        if j is None:
            continue
        d = pd.Timestamp(row.avail_date)
        i = int(np.searchsorted(cal_np, np.datetime64(d), side="left"))
        if i >= T:
            continue
        if i < T and cal_np[i] < np.datetime64(d):
            i += 1
            if i >= T:
                continue
        et = str(row.event_type or "other")
        n_all[i, j] += 1
        if et == "inquiry_letter":
            n_letter[i, j] += 1
        elif et == "inquiry_reply":
            n_reply[i, j] += 1
        elif et == "insider_increase":
            n_inc[i, j] += 1
        elif et in ("buyback", "buyback_excluded"):
            n_buy[i, j] += 1
        elif et == "penalty":
            n_pen[i, j] += 1
        elif et == "earnings_beat":
            n_earn[i, j] += 1
        elif et == "earnings_miss":
            n_earn[i, j] -= 1

    def roll(a: np.ndarray, w: int) -> pd.DataFrame:
        df = pd.DataFrame(a, index=index, columns=columns, dtype="float32")
        out = df.rolling(w, min_periods=1).sum().astype("float32")
        if mask is not None:
            out = out.where(mask)
        return out

    panels = {
        "ann_inquiry_letter_5": roll(n_letter, 5),
        "ann_inquiry_reply_5": roll(n_reply, 5),
        "ann_inquiry_any_5": roll(n_letter + n_reply, 5),
        "ann_insider_inc_5": roll(n_inc, 5),
        "ann_buyback_5": roll(n_buy, 5),
        "ann_buyback_10": roll(n_buy, 10),
        "ann_penalty_5": roll(n_pen, 5),
        "ann_penalty_10": roll(n_pen, 10),
        "ann_earn_signed_5": roll(n_earn, 5),
        "ann_earn_signed_10": roll(n_earn, 10),
        "ann_n_5": roll(n_all, 5),
        "ann_n_10": roll(n_all, 10),
        "ann_n_20": roll(n_all, 20),
    }
    for k, v in panels.items():
        gap[f"nonzero_frac_{k}"] = float((v.fillna(0) > 0).mean().mean())
    del ann, n_letter, n_reply, n_inc, n_buy, n_pen, n_earn, n_all
    gc.collect()
    return panels, gap


def build_candidate_exprs() -> list[dict]:
    """Hand-structured seeds + mild GP-style transforms. No LD, no broadcast, no insider_dec."""
    lockup_leaves = [
        "lockup_S_5",
        "lockup_S_10",
        "lockup_S_20",
        "lockup_S_60",
        "lockup_days_to",
        "lockup_flag_20",
        "lockup_near_5",
    ]
    ann_leaves = [
        "ann_inquiry_letter_5",
        "ann_inquiry_reply_5",
        "ann_inquiry_any_5",
        "ann_insider_inc_5",
        "ann_buyback_5",
        "ann_buyback_10",
        "ann_penalty_5",
        "ann_penalty_10",
        "ann_earn_signed_5",
        "ann_earn_signed_10",
        "ann_n_5",
        "ann_n_10",
        "ann_n_20",
    ]

    seeds: list[str] = []

    def add(e: str):
        if e not in seeds:
            seeds.append(e)

    # --- lockup calendar family ---
    for x in lockup_leaves:
        add(x)
        add(f"neg({x})")
        add(f"rank(neg({x}))")
        add(f"rank({x})")
        add(f"zscore({x})")
        add(f"ts_mean_5({x})")
        add(f"ts_mean_10({x})")
        add(f"ts_std_10({x})")
        add(f"ts_max_5({x})")
        add(f"ts_max_10({x})")
        add(f"delay_5({x})")
        add(f"delay_20({x})")
        add(f"ts_delta_10({x})")
        add(f"rank(ts_std_10({x}))")
        add(f"ts_std_10(rank(ts_mean_5({x})))")
        add(f"abs(ts_std_20(ts_delta_10({x})))")

    # days_to special: smaller = nearer unlock → supply pressure soon → prefer neg or invert
    add("neg(lockup_days_to)")
    add("rank(neg(lockup_days_to))")
    add("ts_max_5(neg(lockup_S_20))")
    add("ts_mean_10(lockup_S_20)")
    add("delay_20(ts_mean_5(lockup_S_20))")
    add("mul(lockup_flag_20, lockup_S_20)")
    add("mul(lockup_near_5, lockup_S_60)")
    add("div(lockup_S_5, lockup_S_60)")
    add("sub(lockup_S_5, lockup_S_20)")

    # --- ann title families ---
    for x in ann_leaves:
        add(x)
        add(f"neg({x})")
        add(f"rank(neg({x}))")
        add(f"rank({x})")
        add(f"zscore({x})")
        add(f"ts_std_10({x})")
        add(f"rank(ts_std_10({x}))")
        add(f"ts_max_5({x})")
        add(f"ts_max_10({x})")
        add(f"ts_mean_5({x})")
        add(f"ts_delta_10({x})")
        add(f"delay_5({x})")
        add(f"delay_20({x})")
        add(f"abs(ts_std_20(ts_delta_10({x})))")
        add(f"ts_std_10(delay_20(ts_delta_5({x})))")
        add(f"delay_20(ts_mean_20(delay_10({x})))")
        add(f"delay_5(ts_std_20(zscore({x})))")
        add(f"ts_max_5(ts_max_5({x}))")

    # cross within ann / lockup (still NON-LD)
    add("mul(ann_n_5, lockup_S_20)")
    add("mul(ann_penalty_5, lockup_S_20)")
    add("mul(ann_buyback_5, lockup_S_20)")
    add("mul(ann_inquiry_any_5, lockup_S_20)")
    add("mul(ann_insider_inc_5, lockup_S_20)")
    add("add(neg(ann_penalty_5), neg(lockup_S_20))")
    add("add(neg(ann_buyback_5), neg(lockup_S_20))")
    add("mul(ann_inquiry_letter_5, ann_inquiry_reply_5)")
    add("add(ann_inquiry_letter_5, ann_insider_inc_5)")
    add("sub(ann_insider_inc_5, ann_penalty_5)")
    add("mul(neg(ann_penalty_5), rank(neg(lockup_S_20)))")
    add("ts_max_20(ts_delta_10(ann_n_5))")
    add("ts_max_20(ts_delta_10(ann_n_10))")
    add("ts_std_20(ts_mean_10(ann_earn_signed_5))")
    add("ts_std_20(ann_penalty_5)")
    add("delay_20(ts_std_20(delay_10(ann_earn_signed_5)))")

    out = []
    for e in seeds:
        if not expr_is_l1d_primary(e):
            continue
        out.append(
            {
                "expr": e,
                "family": family_of(e),
                "leaves": sorted(leaves_in(e)),
                "source": "l1d_seed",
            }
        )
    return out


def who_pays(expr: str) -> str:
    bits = []
    if "lockup" in expr:
        bits.append("解禁股东供给，折价由二级多头承接；临近解禁日卖压更集中")
    if "inquiry" in expr:
        bits.append("问询/回函标题事件：监管注意力与合规交易限制令半知情资金重定价")
    if "insider_inc" in expr:
        bits.append("内部人增持标题：信号或窗口约束下的注意力重定价（title_only）")
    if "buyback" in expr:
        bits.append("回购标题事件后的注意力与公司买盘预期")
    if "penalty" in expr:
        bits.append("处罚标题：合规风险溢价，回避盘支付给敢接盘者或相反")
    if "earn" in expr:
        bits.append("业绩超预期/不及预期标题的短窗重定价")
    if "ann_n" in expr:
        bits.append("公告密集度（标题计数）带来的注意力与信息不对称")
    if not bits:
        bits.append("机制未声明")
    return "；".join(bits)


def main() -> int:
    global t0
    t0 = time.time()
    peak = mem_mb()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    cands = build_candidate_exprs()
    log("candidates", len(cands), "families", sorted({c["family"] for c in cands}))

    _ensure_pkgs()
    l1b = _import_l1b()
    l1c = _import_l1c()
    from quantlab.factors.ops import apply_expr, parse_expr
    from quantlab.factors.ai_factory.ledger import append_attempt

    log("loading structural panels (L1b)")
    panels, label, public, load_meta = l1b.load_structural_panels()
    peak = max(peak, mem_mb())
    # attach L1c for mask consistency; we will replace/extend ann+lockup
    panels, label, public, load_meta = l1c.attach_l1c_panels(panels, label, public, load_meta)
    peak = max(peak, mem_mb())
    del public
    gc.collect()

    mask = panels["overnight_ret"].notna()
    cols = list(panels["overnight_ret"].columns)
    cal = panels["overnight_ret"].index

    log("building lockup calendar family")
    lock_panels, lock_gap = build_lockup_calendar_panels(cal, cols, mask)
    for k, v in lock_panels.items():
        panels[k] = v
    load_meta["lockup_calendar"] = lock_gap
    peak = max(peak, mem_mb())
    log("lockup gap", {k: lock_gap[k] for k in lock_gap if k.startswith("cov_") or k in ("ok", "n_events_used")})

    log("building ann title extra families (title_only)")
    ann_panels, ann_gap = build_ann_title_extra_panels(cal, cols, mask)
    for k, v in ann_panels.items():
        panels[k] = v
    load_meta["ann_title_extra"] = ann_gap
    peak = max(peak, mem_mb())
    log(
        "ann nonzero",
        {k: round(ann_gap[k], 6) for k in ann_gap if k.startswith("nonzero_frac_")},
    )

    needed: set[str] = set()
    for c in cands:
        needed |= set(c["leaves"])
    # keep overnight only if needed — not needed for primary
    for k in list(panels.keys()):
        if k not in needed:
            del panels[k]
    gc.collect()
    log("trimmed panels", sorted(panels.keys()), "mem", mem_mb())
    peak = max(peak, mem_mb())

    cols = list(next(iter(panels.values())).columns)
    cal = next(iter(panels.values())).index
    sig, adv = load_sig_adv(cols, cal)
    peak = max(peak, mem_mb())
    log("sig/adv", sig.shape, "peak", peak)

    main_ledger = ROOT / "output/ai_factor/ledger.jsonl"
    run_ledger = OUT_DIR / "ledger_run.jsonl"
    if run_ledger.exists():
        run_ledger.unlink()
    n_before = (
        sum(1 for x in main_ledger.read_text().splitlines() if x.strip())
        if main_ledger.exists()
        else 0
    )

    results = []
    for i, c in enumerate(cands):
        expr = c["expr"]
        row = dict(c)
        row["who_pays_zh"] = who_pays(expr)
        try:
            tup = _seed_to_tuple(expr)
            fac = apply_expr(parse_expr(to_nested_tuple(tup)), panels)
            if not isinstance(fac, pd.DataFrame):
                raise TypeError(type(fac))
            fac = fac.astype("float32")
            cs = cs_std_stats(fac)
            row["cs_stats"] = cs
            if not cs["passes_cs_variation"]:
                row["sim"] = {
                    "skipped": True,
                    "reason": "cs_variation_fail",
                    "promotion_approved": False,
                }
            else:
                sim = simulate_book(fac, label, sig, adv)
                row["sim"] = sim
            del fac
            gc.collect()
        except Exception as exc:  # noqa: BLE001
            row["sim"] = {
                "error": f"{type(exc).__name__}: {exc}",
                "promotion_approved": False,
            }
            row["cs_stats"] = None

        ok, reason = verdict_row(row)
        row["survive"] = ok
        row["fail_reason"] = None if ok else reason
        row["promotion_approved"] = False
        row["trial_kind"] = "explore_gate"
        results.append(row)

        fit = None
        if isinstance(row.get("sim"), dict) and "flat" in row["sim"]:
            fit = _ann(row["sim"], ["impact", "600000_plus_flat25"])
        notes = (
            f"l1d_non_ld_struct_explore;family={c['family']};survive={ok};reason={reason};"
            f"process_not_sealed;promotion_approved=false;explore_gate_process;"
            f"title_only;no_ld_primary;no_broadcast"
        )
        append_attempt(
            engine="l1d_non_ld_struct_explore",
            seed=SEED,
            universe="midlarge_top1500_or_csi300_500",
            cost=0.0025,
            window="explore_20240603_to_latest_l1d_non_ld_struct",
            expr_str=expr,
            fitness=fit,
            notes=notes,
            path=run_ledger,
        )
        append_attempt(
            engine="l1d_non_ld_struct_explore",
            seed=SEED,
            universe="midlarge_top1500_or_csi300_500",
            cost=0.0025,
            window="explore_20240603_to_latest_l1d_non_ld_struct",
            expr_str=expr,
            fitness=fit,
            notes=notes,
            path=main_ledger,
        )
        peak = max(peak, mem_mb())
        if (i + 1) % 10 == 0 or i == 0 or i + 1 == len(cands):
            g = _ann(row.get("sim") or {}, ["gross"]) if isinstance(row.get("sim"), dict) else None
            log(
                f"[{i+1}/{len(cands)}]",
                c["family"],
                expr[:52],
                "survive",
                ok,
                "gross",
                g,
                "mem",
                mem_mb(),
            )

    n_after = (
        sum(1 for x in main_ledger.read_text().splitlines() if x.strip())
        if main_ledger.exists()
        else 0
    )

    survivors = [r for r in results if r.get("survive")]
    fails = [r for r in results if not r.get("survive")]

    def imp06(r):
        return _ann(r.get("sim") or {}, ["impact", "600000_plus_flat25"])

    survivors_sorted = sorted(
        survivors,
        key=lambda r: (imp06(r) if math.isfinite(imp06(r) or float("nan")) else -1e9),
        reverse=True,
    )

    # Family verdicts
    fam_stats: dict[str, dict] = {}
    for r in results:
        fam = r["family"]
        st = fam_stats.setdefault(
            fam, {"n": 0, "n_survive": 0, "n_cs_fail": 0, "n_cost_fail": 0, "n_err": 0, "best_imp06": float("nan"), "best_expr": None}
        )
        st["n"] += 1
        if r.get("survive"):
            st["n_survive"] += 1
            v = imp06(r)
            if not math.isfinite(st["best_imp06"]) or (math.isfinite(v) and v > st["best_imp06"]):
                st["best_imp06"] = v
                st["best_expr"] = r["expr"]
        else:
            fr = r.get("fail_reason") or ""
            if "cs_variation" in fr:
                st["n_cs_fail"] += 1
            elif "cost_gate" in fr:
                st["n_cost_fail"] += 1
            elif "eval_error" in fr:
                st["n_err"] += 1
        st["verdict"] = (
            "SURVIVE" if st["n_survive"] > 0 else "FAIL"
        )

    summary = {
        "mode": "l1d_non_ld_struct_explore",
        "promotion_approved": False,
        "sealed_executed": False,
        "trial_kind": "explore_gate",
        "window": "explore_20240603_to_latest",
        "capital_cny_primary": [600_000, 1_000_000],
        "flat_bps_one_way": list(FLAT_BPS),
        "k_imp": K_IMP,
        "top_n": TOP_N,
        "cs_std_min": CS_STD_MIN,
        "banned": {
            "broadcast": True,
            "limit_down_primary": True,
            "small_cap": True,
            "textbook_mainline": True,
            "sealed": True,
            "ann_body_invented": False,
            "ann_insider_dec_5_primary": "excluded_prior_batch",
        },
        "ann_title_only": True,
        "invented_body": False,
        "n_candidates": len(cands),
        "n_evaluated": len(results),
        "n_survivors": len(survivors),
        "n_fails": len(fails),
        "survivor_exprs": [r["expr"] for r in survivors_sorted],
        "family_verdicts": fam_stats,
        "lockup_gap": lock_gap,
        "ann_gap": {
            k: ann_gap[k]
            for k in ann_gap
            if k
            in (
                "ok",
                "path",
                "body_source",
                "invented_body",
                "n_rows",
                "n_instruments",
                "n_non_title_only",
            )
            or k.startswith("nonzero_frac_")
        },
        "ledger_N_before": n_before,
        "ledger_N_after": n_after,
        "ledger_N_new": n_after - n_before,
        "peak_rss_MB": round(peak),
        "mem_cap_MB": MEM_CAP_MB,
        "under_mem_cap": peak < MEM_CAP_MB,
        "elapsed_s": round(time.time() - t0, 1),
    }

    def slim(r):
        sim = r.get("sim") or {}
        return {
            "expr": r["expr"],
            "family": r["family"],
            "leaves": r["leaves"],
            "survive": r["survive"],
            "fail_reason": r.get("fail_reason"),
            "who_pays_zh": r.get("who_pays_zh"),
            "cs_stats": r.get("cs_stats"),
            "icir": sim.get("icir") if isinstance(sim, dict) else None,
            "ic_mean": sim.get("ic_mean") if isinstance(sim, dict) else None,
            "flat10": _ann(sim, ["flat", "10"]),
            "flat25": _ann(sim, ["flat", "25"]),
            "imp06": _ann(sim, ["impact", "600000"]),
            "imp10": _ann(sim, ["impact", "1000000"]),
            "imp06_plus25": _ann(sim, ["impact", "600000_plus_flat25"]),
            "imp10_plus25": _ann(sim, ["impact", "1000000_plus_flat25"]),
            "turn": sim.get("mean_turn_ow") if isinstance(sim, dict) else None,
            "gross": _ann(sim, ["gross"]),
            "promotion_approved": False,
            "trial_kind": "explore_gate",
        }

    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str)
    )
    (OUT_DIR / "results.json").write_text(
        json.dumps([slim(r) for r in results], indent=2, ensure_ascii=False, default=str)
    )
    (OUT_DIR / "survivors.json").write_text(
        json.dumps([slim(r) for r in survivors_sorted], indent=2, ensure_ascii=False, default=str)
    )
    (OUT_DIR / "fails.json").write_text(
        json.dumps([slim(r) for r in fails], indent=2, ensure_ascii=False, default=str)
    )
    (OUT_DIR / "family_verdicts.json").write_text(
        json.dumps(fam_stats, indent=2, ensure_ascii=False, default=str)
    )

    # --- Markdown report ---
    lines = [
        "# AI 因子 L1d：非跌停结构叶下一批探索（解禁日历 + 公告 title 其他事件族）",
        "",
        f"- **时间：** 2026-10-12（America/New_York）",
        f"- **promotion_approved：** false；**密封：** 未开；**trial_kind：** explore_gate / process",
        f"- **本金主口径：** 60 万 / 100 万；√冲击 k=1 + 佣金 2.5bp，主裁决用 **冲击+flat25**",
        f"- **禁止：** 广播叶、跌停叶作主候选、小盘、教科书主线、密封、编造公告正文、Strategy 权重",
        f"- **公告：** title_only（`invented_body=false`）；**排除**已深挖的 `ann_insider_dec_5` 主批",
        f"- 账本：N {n_before} → {n_after}（+{n_after - n_before}，均为 explore_gate 过程计次）",
        f"- 峰值 RSS：{round(peak)} MB（上限 {MEM_CAP_MB}；under_cap={peak < MEM_CAP_MB}）；运行 {summary['elapsed_s']}s",
        "",
        "## 探索范围",
        "",
        "1. **解禁日历族：** `lockup_S_5/10/20/60`、`lockup_days_to`、`lockup_flag_20`、`lockup_near_5`",
        "2. **公告 title 新事件族：** `ann_inquiry_letter/reply/any_5`、`ann_insider_inc_5`",
        "3. **公告 title 既有非 insider_dec 族扩展窗：** buyback/penalty/earn/n 的 5/10/20 日滚动 + 变换",
        "4. **闸门：** 截面变异 + flat25>0 + 60/100万冲击∩flat25>0；中大盘；explore 窗 2024-06-03→latest",
        "",
        f"- 候选 {len(cands)}；评估 {len(results)}；**存活 {len(survivors)}**；失败 {len(fails)}",
        "",
        "## 族级裁决（清晰）",
        "",
        "| 族 | n | 存活 | CS失败 | 成本闸失败 | 错误 | 裁决 | 最佳60万+25bp | 最佳表达式 |",
        "|---|---:|---:|---:|---:|---:|---|---:|---|",
    ]
    for fam in sorted(fam_stats.keys()):
        st = fam_stats[fam]
        best = st["best_imp06"]
        best_s = f"{best:.2%}" if isinstance(best, float) and math.isfinite(best) else "—"
        lines.append(
            f"| `{fam}` | {st['n']} | {st['n_survive']} | {st['n_cs_fail']} | "
            f"{st['n_cost_fail']} | {st['n_err']} | **{st['verdict']}** | {best_s} | "
            f"`{st['best_expr'] or '—'}` |"
        )

    lines += [
        "",
        "## 存活明细（按 60万+25bp 降序）",
        "",
        "| # | 族 | 表达式 | ICIR | flat25 | 60万+25bp | 100万+25bp | 换手 | CS标准差 |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    if survivors_sorted:
        for i, r in enumerate(survivors_sorted, 1):
            sim = r.get("sim") or {}
            cs = r.get("cs_stats") or {}
            lines.append(
                f"| {i} | `{r['family']}` | `{r['expr']}` | "
                f"{sim.get('icir', float('nan')) if isinstance(sim, dict) else float('nan'):.3f} | "
                f"{_ann(sim, ['flat', '25']):.2%} | "
                f"{_ann(sim, ['impact', '600000_plus_flat25']):.2%} | "
                f"{_ann(sim, ['impact', '1000000_plus_flat25']):.2%} | "
                f"{(sim.get('mean_turn_ow') if isinstance(sim, dict) else float('nan')):.3f} | "
                f"{cs.get('cs_std_mean', float('nan')):.4g} |"
            )
    else:
        lines.append("| — | — | （无存活） | — | — | — | — | — | — |")

    # Top fails by family for diagnosis
    lines += [
        "",
        "## 失败摘要（每族最多 3 条代表性）",
        "",
    ]
    by_fam_fail: dict[str, list] = {}
    for r in fails:
        by_fam_fail.setdefault(r["family"], []).append(r)
    for fam in sorted(by_fam_fail.keys()):
        lines.append(f"### `{fam}`")
        for r in by_fam_fail[fam][:3]:
            lines.append(f"- `{r['expr']}` → `{r.get('fail_reason')}`")
        lines.append("")

    lines += [
        "## 数据缺口",
        "",
        f"- 解禁：ok={lock_gap.get('ok')}；events={lock_gap.get('n_events_used')}；"
        f"cov_S_20={lock_gap.get('cov_lockup_S_20')}",
        f"- 公告 title：ok={ann_gap.get('ok')}；rows={ann_gap.get('n_rows')}；"
        f"instruments={ann_gap.get('n_instruments')}；invented_body=false",
        f"- inquiry_letter nonzero≈{ann_gap.get('nonzero_frac_ann_inquiry_letter_5')}；"
        f"inquiry_reply≈{ann_gap.get('nonzero_frac_ann_inquiry_reply_5')}；"
        f"insider_inc≈{ann_gap.get('nonzero_frac_ann_insider_inc_5')}",
        "",
        "## 诚实结论",
        "",
    ]
    survive_fams = [f for f, st in fam_stats.items() if st["n_survive"] > 0]
    fail_fams = [f for f, st in fam_stats.items() if st["n_survive"] == 0]
    lines.append(
        f"- **产生存活的族：** {', '.join(f'`{x}`' for x in sorted(survive_fams)) or '无'}"
    )
    lines.append(
        f"- **整族失败的族：** {', '.join(f'`{x}`' for x in sorted(fail_fams)) or '无'}"
    )
    lines.append(
        "- **不开密封、不交 Strategy 权重、promotion_approved=false。** "
        "跌停叶未作主候选；广播叶未进池；`ann_insider_dec_5` 排除本批主探索（见 L1c 非跌停消融）。"
    )
    lines += [
        "",
        "## 产物",
        "",
        f"- 报告：`{REPORT}`",
        f"- JSON：`{OUT_DIR}/`（summary / results / survivors / fails / family_verdicts / ledger_run.jsonl）",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    log("done", "survivors", len(survivors), "peak", peak, "ledger_delta", n_after - n_before)
    print(
        json.dumps(
            {
                "survivors": len(survivors),
                "fails": len(fails),
                "peak_MB": round(peak),
                "ledger_N_before": n_before,
                "ledger_N_after": n_after,
                "ledger_delta": n_after - n_before,
                "family_verdicts": {k: v["verdict"] for k, v in fam_stats.items()},
                "report": str(REPORT),
                "out_dir": str(OUT_DIR),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
