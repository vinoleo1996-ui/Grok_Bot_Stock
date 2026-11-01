#!/usr/bin/env python3
"""L1c patrol: drop broadcast leaves; CS-variation-only cost+impact gate.

Explore window only. promotion_approved=False. No sealed. No small-cap.
Announcements title_only — do not invent body. Memory < 2.5GB.
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
L1C_DIR = ROOT / "output/ai_factor/l1c_explore"
OUT_DIR = ROOT / "output/ai_factor/l1c_cs_variation_gate"
REPORT = ROOT / "output/alpha/AI_FACTOR_L1c_CS_VARIATION_GATE_ZH.md"
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

# Explicit broadcast / market-wide leaf names + prefixes
BROADCAST_EXACT = frozenset(
    {
        "mkt_max_height",
        "mkt_lu_breadth",
        "etf_major_flow",
        "etf_theme_flow",
        "if_basis",
        "if_basis_x_on",
        "if_basis_x_lu",
        "etf_flow_x_lu",
        "theme_lu_density",
    }
)
BROADCAST_PREFIXES = ("mkt_", "etf_", "if_basis")

OPS = {
    "add",
    "sub",
    "mul",
    "div",
    "neg",
    "abs",
    "rank",
    "zscore",
    "industry_neutral",
    "size_neutral",
}
for k in (1, 5, 10, 20):
    OPS |= {f"delay_{k}", f"ts_mean_{k}", f"ts_std_{k}", f"ts_delta_{k}", f"ts_max_{k}"}

t0 = 0.0


def mem_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def log(*a):
    print(f"[l1c_cs_gate {time.time()-t0:5.0f}s {mem_mb():.0f}MB]", *a, flush=True)


def leaves_in(expr: str) -> set[str]:
    return {t for t in re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", expr) if t not in OPS}


def is_broadcast_leaf(name: str) -> bool:
    if name in BROADCAST_EXACT:
        return True
    return any(name.startswith(p) for p in BROADCAST_PREFIXES)


def is_cs_variation_leaf(name: str) -> bool:
    """Stock-level variation: limit_down_* / ld_* / ann_* / lockup_* (+ days_since_ld)."""
    if name == "days_since_ld":
        return True  # LD-family alias used in L1c panels
    return (
        name.startswith("limit_down_")
        or name.startswith("ld_")
        or name.startswith("ann_")
        or name.startswith("lockup_")
    )


def expr_is_cs_variation_only(expr: str) -> bool:
    L = leaves_in(expr)
    if not L:
        return False
    if any(is_broadcast_leaf(x) for x in L):
        return False
    return all(is_cs_variation_leaf(x) for x in L)


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
    m = re.fullmatch(r"mul\((.+),(.+)\)", s)
    if m:
        return (
            "op",
            "mul",
            _seed_to_tuple(m.group(1).strip()),
            _seed_to_tuple(m.group(2).strip()),
        )
    m = re.fullmatch(r"add\((.+),(.+)\)", s)
    if m:
        return (
            "op",
            "add",
            _seed_to_tuple(m.group(1).strip()),
            _seed_to_tuple(m.group(2).strip()),
        )
    m = re.fullmatch(r"sub\((.+),(.+)\)", s)
    if m:
        return (
            "op",
            "sub",
            _seed_to_tuple(m.group(1).strip()),
            _seed_to_tuple(m.group(2).strip()),
        )
    m = re.fullmatch(r"div\((.+),(.+)\)", s)
    if m:
        return (
            "op",
            "div",
            _seed_to_tuple(m.group(1).strip()),
            _seed_to_tuple(m.group(2).strip()),
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
        # impact arm already has 2.5bp commission on traded notional
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


def collect_candidates() -> list[dict]:
    """From L1c explore artifacts: top_k_main + CS-var seeds in ledger_run."""
    top = json.loads((L1C_DIR / "top_k_main.json").read_text())
    cands: dict[str, dict] = {}
    for i, row in enumerate(top):
        expr = row["expr"]
        L = leaves_in(expr)
        dropped = not expr_is_cs_variation_only(expr)
        reason = None
        if dropped:
            bad = sorted(x for x in L if is_broadcast_leaf(x) or not is_cs_variation_leaf(x))
            reason = f"has_non_cs_leaves:{bad}"
        cands[expr] = {
            "expr": expr,
            "tuple": row.get("tuple"),
            "source": "top_k_main",
            "top_k_rank": i + 1,
            "l1c_ann_net_ref": (row.get("metrics") or {}).get("ann_net"),
            "l1c_icir_ref": (row.get("metrics") or {}).get("icir"),
            "l1c_fitness_ref": row.get("fitness"),
            "leaves": sorted(L),
            "prefilter_drop": dropped,
            "prefilter_reason": reason,
            "who_pays_zh": row.get("who_pays_zh"),
        }

    # Also pull CS-var-only seeds from same-run ledger (lockup etc. missed top_k due to broadcast pollution)
    ledger_run = L1C_DIR / "ledger_run.jsonl"
    if ledger_run.exists():
        for line in ledger_run.read_text().splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            expr = rec.get("expr_str") or ""
            if not expr or expr in cands:
                continue
            if not expr_is_cs_variation_only(expr):
                continue
            cands[expr] = {
                "expr": expr,
                "tuple": None,
                "source": "ledger_run_cs_var",
                "top_k_rank": None,
                "l1c_ann_net_ref": None,
                "l1c_icir_ref": None,
                "l1c_fitness_ref": rec.get("fitness"),
                "leaves": sorted(leaves_in(expr)),
                "prefilter_drop": False,
                "prefilter_reason": None,
                "who_pays_zh": None,
            }
    return list(cands.values())


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
    if row.get("prefilter_drop"):
        return False, row.get("prefilter_reason") or "prefilter_drop"
    sim = row.get("sim") or {}
    if "error" in sim:
        return False, f"eval_error:{sim['error'][:120]}"
    cs = row.get("cs_stats") or {}
    if not cs.get("passes_cs_variation"):
        return False, (
            f"cs_variation_fail:std_mean={cs.get('cs_std_mean')},"
            f"frac_zero={cs.get('frac_days_near_zero_std')},"
            f"frac_const={cs.get('frac_days_constant_cs')}"
        )
    flat25 = _ann(sim, ["flat", "25"])
    imp06 = _ann(sim, ["impact", "600000"])
    imp10 = _ann(sim, ["impact", "1000000"])
    fails = []
    if not (isinstance(flat25, float) and math.isfinite(flat25) and flat25 > 0):
        fails.append(f"flat25<={flat25}")
    if not (isinstance(imp06, float) and math.isfinite(imp06) and imp06 > 0):
        fails.append(f"impact_60万<={imp06}")
    if not (isinstance(imp10, float) and math.isfinite(imp10) and imp10 > 0):
        fails.append(f"impact_100万<={imp10}")
    if fails:
        return False, "cost_gate_fail:" + ";".join(fails)
    return True, "survive_cs_var+cost+60/100万_impact"


def main() -> int:
    global t0
    t0 = time.time()
    peak = mem_mb()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    cands = collect_candidates()
    to_eval = [c for c in cands if not c["prefilter_drop"]]
    dropped = [c for c in cands if c["prefilter_drop"]]
    log(
        "candidates",
        len(cands),
        "to_eval",
        len(to_eval),
        "prefilter_drop",
        len(dropped),
    )

    _ensure_pkgs()
    l1b = _import_l1b()
    l1c = _import_l1c()
    from quantlab.factors.ops import apply_expr, parse_expr
    from quantlab.factors.ai_factory.ledger import append_attempt

    log("loading structural panels")
    panels, label, public, load_meta = l1b.load_structural_panels()
    peak = max(peak, mem_mb())
    panels, label, public, load_meta = l1c.attach_l1c_panels(panels, label, public, load_meta)
    peak = max(peak, mem_mb())
    log("panels ready", load_meta.get("n_cols"), "peak", peak)

    del public
    needed = set()
    for c in to_eval:
        needed |= set(c["leaves"])
    # always keep nothing else
    for k in list(panels.keys()):
        if k not in needed:
            del panels[k]
    gc.collect()
    log("trimmed panels", sorted(panels.keys()), "mem", mem_mb())

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
    # First record dropped (no sim)
    for c in dropped:
        row = dict(c)
        row["sim"] = None
        row["cs_stats"] = None
        row["survive"] = False
        row["fail_reason"] = c["prefilter_reason"]
        row["promotion_approved"] = False
        row["trial_kind"] = "explore_gate"
        results.append(row)

    for i, c in enumerate(to_eval):
        expr = c["expr"]
        row = dict(c)
        try:
            tup = c.get("tuple")
            if tup is None:
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

        # ledger: process / explore_gate — not sealed
        fit = None
        if isinstance(row.get("sim"), dict) and "flat" in row["sim"]:
            fit = _ann(row["sim"], ["impact", "600000"])
        notes = (
            f"l1c_cs_variation_gate;survive={ok};reason={reason};"
            f"source={c['source']};process_not_sealed;promotion_approved=false"
        )
        append_attempt(
            engine="l1c_cs_variation_gate",
            seed=SEED,
            universe="midlarge_top1500_or_csi300_500",
            cost=0.0025,
            window="explore_20240603_to_latest_l1c_cs_gate",
            expr_str=expr,
            fitness=fit,
            notes=notes,
            path=run_ledger,
        )
        append_attempt(
            engine="l1c_cs_variation_gate",
            seed=SEED,
            universe="midlarge_top1500_or_csi300_500",
            cost=0.0025,
            window="explore_20240603_to_latest_l1c_cs_gate",
            expr_str=expr,
            fitness=fit,
            notes=notes + ";explore_gate_process",
            path=main_ledger,
        )
        peak = max(peak, mem_mb())
        g = _ann(row.get("sim") or {}, ["gross"]) if isinstance(row.get("sim"), dict) else None
        log(
            f"[{i+1}/{len(to_eval)}]",
            expr[:56],
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

    # Prefer unique exprs: for near-duplicates keep best impact 60万
    def imp06(r):
        return _ann(r.get("sim") or {}, ["impact", "600000"])

    survivors_sorted = sorted(
        survivors,
        key=lambda r: (imp06(r) if math.isfinite(imp06(r) or float("nan")) else -1e9),
        reverse=True,
    )

    summary = {
        "mode": "l1c_cs_variation_gate",
        "promotion_approved": False,
        "sealed_executed": False,
        "trial_kind": "explore_gate",
        "window": "explore_20240603_to_latest",
        "capital_cny_primary": [600_000, 1_000_000],
        "flat_bps_one_way": list(FLAT_BPS),
        "k_imp": K_IMP,
        "top_n": TOP_N,
        "cs_std_min": CS_STD_MIN,
        "n_candidates_seen": len(cands),
        "n_prefilter_drop_broadcast": len(dropped),
        "n_evaluated": len(to_eval),
        "n_survivors": len(survivors),
        "n_fails": len(fails),
        "survivor_exprs": [r["expr"] for r in survivors_sorted],
        "prefilter_drop_exprs": [
            {"expr": r["expr"], "reason": r["prefilter_reason"], "leaves": r["leaves"]}
            for r in dropped
        ],
        "ann_title_only": True,
        "invented_body": False,
        "ann_gap": (load_meta or {}).get("ann_title_events"),
        "ledger_N_before": n_before,
        "ledger_N_after": n_after,
        "ledger_N_new": n_after - n_before,
        "peak_rss_MB": round(peak),
        "mem_cap_MB": MEM_CAP_MB,
        "under_mem_cap": peak < MEM_CAP_MB,
        "runtime_s": round(time.time() - t0, 1),
        "suggest_sealed": False,
        "gate_note": "探索闸门过程指标；仅个股截面变异叶；不开密封",
    }

    (OUT_DIR / "results.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False, default=str)
    )
    (OUT_DIR / "survivors.json").write_text(
        json.dumps(survivors_sorted, indent=2, ensure_ascii=False, default=str)
    )
    (OUT_DIR / "fails.json").write_text(
        json.dumps(fails, indent=2, ensure_ascii=False, default=str)
    )
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str)
    )

    # --- Chinese report ---
    lines = []
    lines.append("# AI 因子 L1c：去掉广播叶后的个股变异闸门（探索窗）")
    lines.append("")
    lines.append("- **时间：** 2026-10-12（America/New_York）")
    lines.append("- **promotion_approved：** false；**密封：** 未开；**trial_kind：** explore_gate / process")
    lines.append("- **本金主口径：** 60 万 / 100 万")
    lines.append("- **禁止：** 小盘主线、教科书主结果、密封窗、编造公告正文（title_only）")
    lines.append(
        f"- 账本：N {n_before} → {n_after}（+{n_after - n_before}，均为 explore_gate 过程计次）"
    )
    lines.append(
        f"- 峰值 RSS：{round(peak)} MB（上限 {MEM_CAP_MB}；under_cap={peak < MEM_CAP_MB}）；运行 {summary['runtime_s']}s"
    )
    lines.append("")
    lines.append("## 过滤规则")
    lines.append("")
    lines.append("1. **丢掉广播叶：** `mkt_*` / `etf_*` / `if_basis*` / 以及同日截面近常值叶")
    lines.append(
        "2. **只留个股变异叶：** `limit_down_*` / `ld_*` / `ann_*` / `lockup_*`（含 `days_since_ld`）"
    )
    lines.append(
        "3. **成本闸：** flat 10/25bp；平方根冲击 k=1 + 单边佣金 2.5bp；主看 60万/100万冲击净 > 0 且 flat25 > 0"
    )
    lines.append("")
    lines.append(
        f"- 候选总数 {len(cands)}（top_k_main + 同跑 ledger 中纯 CS 变异种子）；"
        f"预过滤丢掉广播/非 CS {len(dropped)}；进入重估 {len(to_eval)}；**存活 {len(survivors)}**；失败 {len(fails)}"
    )
    lines.append("")
    lines.append("## 预过滤丢掉（广播/非 CS）")
    lines.append("")
    lines.append("| 表达式 | 叶子 | 原因 |")
    lines.append("|---|---|---|")
    for r in dropped:
        lines.append(
            f"| `{r['expr']}` | {', '.join(r['leaves'])} | `{r['prefilter_reason']}` |"
        )
    if not dropped:
        lines.append("| （无） | — | — |")
    lines.append("")
    lines.append("## 存活（CS 变异 + 成本 + 60/100万冲击）")
    lines.append("")
    lines.append(
        "| # | 表达式 | 来源 | ICIR | flat10 | flat25 | 60万冲击 | 100万冲击 | 换手 | CS标准差 |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(survivors_sorted, 1):
        sim = r.get("sim") or {}
        cs = r.get("cs_stats") or {}
        lines.append(
            "| {i} | `{expr}` | {src} | {icir:.3f} | {f10:.2%} | {f25:.2%} | {i06:.2%} | {i10:.2%} | {to:.3f} | {cs:.4g} |".format(
                i=i,
                expr=r["expr"],
                src=r.get("source"),
                icir=float(sim.get("icir") or float("nan")),
                f10=_ann(sim, ["flat", "10"]),
                f25=_ann(sim, ["flat", "25"]),
                i06=_ann(sim, ["impact", "600000"]),
                i10=_ann(sim, ["impact", "1000000"]),
                to=float(sim.get("mean_turn_ow") or float("nan")),
                cs=float(cs.get("cs_std_mean") or float("nan")),
            )
        )
    if not survivors_sorted:
        lines.append("| （无存活） | — | — | — | — | — | — | — | — | — |")
    lines.append("")
    lines.append("## 失败明细")
    lines.append("")
    lines.append("| 表达式 | 失败原因 | flat25 | 60万 | 100万 |")
    lines.append("|---|---|---|---|---|")
    for r in fails:
        sim = r.get("sim") or {}
        f25 = _ann(sim, ["flat", "25"]) if isinstance(sim, dict) else float("nan")
        i06 = _ann(sim, ["impact", "600000"]) if isinstance(sim, dict) else float("nan")
        i10 = _ann(sim, ["impact", "1000000"]) if isinstance(sim, dict) else float("nan")

        def _fmt(x):
            return f"{x:.2%}" if isinstance(x, float) and math.isfinite(x) else "—"

        lines.append(
            f"| `{r['expr']}` | `{r.get('fail_reason')}` | {_fmt(f25)} | {_fmt(i06)} | {_fmt(i10)} |"
        )
    lines.append("")
    lines.append("## 结论（清晰裁决）")
    lines.append("")
    if survivors_sorted:
        lines.append(
            f"- **存活 {len(survivors_sorted)} 条**：通过「个股截面变异 + flat25>0 + 60/100万冲击净>0」。"
        )
        lines.append(
            "- 仍为**探索窗过程指标**；ICIR 可能 ≤0（与 L1c 诚实保留一致），**不申请密封**，`promotion_approved=false`。"
        )
        lines.append(
            "- 存活式多为跌停序列 / 公告标题事件 / 解禁供给；广播叶（市场宽度、ETF、基差）已剔除。"
        )
    else:
        lines.append(
            "- **无存活**：去掉广播叶后，个股变异叶未能同时通过 CS 变异与 60/100万成本冲击闸。"
        )
        lines.append("- **不申请密封**；`promotion_approved=false`。")
    lines.append("")
    lines.append("## 路径")
    lines.append("")
    lines.append(f"- 报告：`{REPORT}`")
    lines.append(f"- 产物：`{OUT_DIR}/`（summary/results/survivors/fails.json）")
    lines.append("- 账本：`output/ai_factor/ledger.jsonl`（explore_gate / process）")
    lines.append("")

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log("done", "survivors", len(survivors), "peak", peak)
    print(json.dumps({"survivors": len(survivors), "fails": len(fails), "peak_MB": round(peak), "report": str(REPORT)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
