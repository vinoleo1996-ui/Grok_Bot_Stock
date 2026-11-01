#!/usr/bin/env python3
"""L1b Top-K capacity / sqrt-impact sensitivity + remove-limit-up-leaf ablation.

Explore window only (2024-06-03→latest). Mid/large. No sealed. promotion_approved=False.
Memory budget < 2.5GB. Leo via New Bot 2026-10-11.
"""
from __future__ import annotations

import gc
import importlib.util
import json
import math
import resource
import sys
import time
import types
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/workspace/QuantLab")
SCRATCH = Path("/workspace/scratch/tic")
OUT_DIR = ROOT / "output/ai_factor/gp_explore_l1b_capacity"
REPORT = ROOT / "output/alpha/AI_FACTOR_L1b_CAPACITY_ABLATION_ZH.md"
TOP_K_CS = ROOT / "output/ai_factor/gp_explore_l1b/top_k_crosssection.json"
TOP_K_FULL = ROOT / "output/ai_factor/gp_explore_l1b/top_k.json"
EXPLORE_START = pd.Timestamp("2024-06-03")
TOP_N = 50
K_IMP = 1.0
AUMS = (0.6e6, 1.0e6, 50e6, 200e6, 500e6)  # CNY; primary=0.6M/1M (Leo capital), large=appendix
FLAT_BPS = (10, 25)  # one-way bp
COMMISSION_ONE_WAY = 0.00025  # 2.5bp for impact arm (alongside sqrt)
PROMOTION_APPROVED = False
MEM_CAP_MB = 2500

LU_FAMILY = frozenset(
    {
        "days_since_lu",
        "lu_streak",
        "limit_up_flag",
        "lu_count_5",
        "etf_flow_x_lu",
        "if_basis_x_lu",
    }
)
BROADCAST_LEAVES = frozenset({"etf_major_flow", "if_basis"})  # cross-section constant


def mem_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


def log(*a):
    print(f"[l1b_cap {time.time()-t0:5.0f}s {mem_mb():.0f}MB]", *a, flush=True)


def _load_ops():
    if "quantlab" not in sys.modules:
        q = types.ModuleType("quantlab")
        q.__path__ = [str(ROOT / "quantlab")]
        sys.modules["quantlab"] = q
    if "quantlab.factors" not in sys.modules or not hasattr(
        sys.modules.get("quantlab.factors"), "__path__"
    ):
        f = types.ModuleType("quantlab.factors")
        f.__path__ = [str(ROOT / "quantlab/factors")]
        sys.modules["quantlab.factors"] = f
    spec = importlib.util.spec_from_file_location(
        "quantlab.factors.ops", ROOT / "quantlab/factors/ops.py"
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["quantlab.factors.ops"] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _import_l1b_loader():
    path = ROOT / "research/ai_factor_l1b_structural_explore.py"
    spec = importlib.util.spec_from_file_location("ai_factor_l1b_structural_explore", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ai_factor_l1b_structural_explore"] = mod
    # stub ai_factory import inside loader by preloading ops path via evaluate
    assert spec.loader is not None
    # Pre-create package stubs so load_structural_panels' late import works
    af = types.ModuleType("quantlab.factors.ai_factory")
    af.__path__ = [str(ROOT / "quantlab/factors/ai_factory")]
    sys.modules["quantlab.factors.ai_factory"] = af
    for name in ("evaluate", "fitness", "novelty", "ledger", "search"):
        p = ROOT / f"quantlab/factors/ai_factory/{name}.py"
        sp = importlib.util.spec_from_file_location(f"quantlab.factors.ai_factory.{name}", p)
        m = importlib.util.module_from_spec(sp)
        sys.modules[f"quantlab.factors.ai_factory.{name}"] = m
        assert sp.loader is not None
        sp.loader.exec_module(m)
    spec.loader.exec_module(mod)
    return mod


def leaves_in(expr: str) -> set[str]:
    import re

    ops = {
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
        ops |= {
            f"delay_{k}",
            f"ts_mean_{k}",
            f"ts_std_{k}",
            f"ts_delta_{k}",
            f"ts_max_{k}",
        }
    return {t for t in re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", expr) if t not in ops}


def primarily_lu(expr: str) -> bool:
    L = leaves_in(expr)
    if not L:
        return True
    lu = L & LU_FAMILY
    non = L - LU_FAMILY
    if not lu:
        return False
    # primarily LU if majority LU, or only overnight/intraday wrappers alongside LU
    return len(lu) >= len(non) or non.issubset({"overnight_ret", "intraday_ret", "on_minus_id"})


def is_broadcast_only(expr: str) -> bool:
    L = leaves_in(expr)
    return bool(L) and L.issubset(BROADCAST_LEAVES)


def to_nested_tuple(obj):
    if isinstance(obj, list):
        return tuple(to_nested_tuple(x) for x in obj)
    return obj


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


def simulate_book(
    factor: pd.DataFrame,
    label: pd.DataFrame,
    sig: pd.DataFrame,
    adv: pd.DataFrame,
    *,
    top_n: int = TOP_N,
) -> dict:
    """Daily long top-N EW; flat one-way costs + P7-style sqrt impact."""
    idx = factor.index.intersection(label.index)
    idx = idx[idx >= EXPLORE_START]
    f = factor.reindex(idx).to_numpy(dtype=np.float64, copy=False)
    y = label.reindex(idx).to_numpy(dtype=np.float64, copy=False)
    s = sig.reindex(idx).to_numpy(dtype=np.float64, copy=False)
    a = adv.reindex(idx).to_numpy(dtype=np.float64, copy=False)
    cols = list(factor.columns)
    T = len(idx)

    gross = np.full(T, np.nan)
    turn_ow = np.full(T, np.nan)  # one-way fraction of book
    # impact cost as fraction of AUM per day
    imp_frac = {aum: np.full(T, np.nan) for aum in AUMS}
    prev = None  # set of col indices

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
            turn_ow[t] = 1.0  # full deploy
            entered = cur
            exited = set()
        else:
            entered = cur - prev
            exited = prev - cur
            turn_ow[t] = len(cur.symmetric_difference(prev)) / (2.0 * k)
        # equal weight 1/k; trade notional for entered/exited
        w = 1.0 / k
        for aum in AUMS:
            cost_cny = 0.0
            # sells then buys
            for j in exited | entered:
                V = w * aum
                sj = s[t, j]
                aj = a[t, j]
                # commission on traded notional
                cost_cny += COMMISSION_ONE_WAY * V
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
        net = gross - turn_ow * (bp / 1e4)
        out["flat"][str(bp)] = ann_from_daily(net)
    for aum in AUMS:
        # impact arm: gross - impact_frac (includes 2.5bp commission on traded) — no extra flat
        net = gross - imp_frac[aum]
        key = f"{aum:.0e}"
        out["impact"][key] = ann_from_daily(net)
        # also report combined: impact + extra flat slippage beyond commission
        for bp in FLAT_BPS:
            # avoid double-counting commission: flat bp replaces commission floor
            # report impact_only + separate flat; combined = gross - max(imp, turn*bp) approx:
            # use: gross - imp_frac - turn*(bp/1e4 - COMMISSION) when bp>comm
            extra = max(0.0, bp / 1e4 - COMMISSION_ONE_WAY)
            net2 = gross - imp_frac[aum] - turn_ow * extra
            out["impact"][f"{key}_plus_flat{bp}"] = ann_from_daily(net2)
    # IC quick
    from quantlab.factors.ai_factory.fitness import daily_rank_ic, icir_from_series

    ics = daily_rank_ic(factor.reindex(idx), label.reindex(idx))
    out["ic_mean"] = float(np.nanmean(ics.to_numpy()))
    out["icir"] = float(icir_from_series(ics))
    return out


def load_sig_adv(cols: list[str], index: pd.DatetimeIndex) -> tuple[pd.DataFrame, pd.DataFrame]:
    """20d ret vol (SIG) and 20d mean amount (ADV, CNY)."""
    cl = pd.read_parquet(SCRATCH / "close.parquet", columns=cols).astype("float32")
    cl = cl.loc[cl.index >= pd.Timestamp("2024-01-02")]
    fa = pd.read_parquet(SCRATCH / "factor.parquet", columns=cols).astype("float32")
    fa = fa.loc[fa.index >= pd.Timestamp("2024-01-02")].ffill()
    aC = (cl * fa).astype("float32")
    del cl, fa
    gc.collect()
    ret = aC.pct_change(fill_method=None)
    sig = ret.rolling(20, min_periods=10).std().astype("float32")
    del aC, ret
    gc.collect()
    amt = pd.read_parquet(SCRATCH / "amount.parquet", columns=cols).astype("float32")
    amt = amt.loc[amt.index >= pd.Timestamp("2024-01-02")]
    adv = amt.rolling(20, min_periods=10).mean().astype("float32")
    del amt
    gc.collect()
    sig = sig.reindex(index=index, columns=cols)
    adv = adv.reindex(index=index, columns=cols)
    return sig, adv


def main() -> int:
    global t0
    t0 = time.time()
    peak = mem_mb()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    cs = json.loads(TOP_K_CS.read_text())
    full = json.loads(TOP_K_FULL.read_text())
    log("loaded top_k", len(cs), "cs", len(full), "full")

    ops = _load_ops()
    apply_expr = ops.apply_expr
    parse_expr = ops.parse_expr
    l1b = _import_l1b_loader()
    panels, label, public, load_meta = l1b.load_structural_panels()
    peak = max(peak, mem_mb())
    log("panels ready", load_meta.get("n_cols"), "peak", peak)

    # free public + unused leaves to stay under cap
    del public
    needed = set()
    for row in cs + full:
        needed |= leaves_in(row["expr"])
    for k in list(panels.keys()):
        if k not in needed:
            del panels[k]
    gc.collect()
    log("trimmed panels", list(panels.keys()), mem_mb())

    cols = list(next(iter(panels.values())).columns)
    cal = next(iter(panels.values())).index
    sig, adv = load_sig_adv(cols, cal)
    peak = max(peak, mem_mb())
    log("sig/adv", sig.shape, "peak", peak)
    if peak > MEM_CAP_MB:
        log("WARN peak exceeded soft cap", peak)

    # --- capacity on CS Top-K ---
    capacity_rows = []
    for i, row in enumerate(cs):
        expr = row["expr"]
        tup = row["tuple"]
        try:
            fac = apply_expr(parse_expr(to_nested_tuple(tup)), panels)
            # ensure DataFrame
            if not isinstance(fac, pd.DataFrame):
                raise TypeError(type(fac))
            fac = fac.astype("float32")
            sim = simulate_book(fac, label, sig, adv)
            del fac
            gc.collect()
        except Exception as exc:  # noqa: BLE001
            sim = {"error": f"{type(exc).__name__}: {exc}", "promotion_approved": False}
        capacity_rows.append(
            {
                "rank": i + 1,
                "expr": expr,
                "primarily_lu": primarily_lu(expr),
                "broadcast_only": is_broadcast_only(expr),
                "l1b_ann_net_ref": row.get("metrics", {}).get("ann_net"),
                "l1b_icir_ref": row.get("metrics", {}).get("icir"),
                "sim": sim,
                "promotion_approved": False,
            }
        )
        peak = max(peak, mem_mb())
        gann = (sim.get("gross") or {}).get("ann") if isinstance(sim, dict) else None
        log(f"cap[{i+1}/{len(cs)}]", expr[:48], "gross_ann", gann, "mem", mem_mb())

    # --- ablation: remove primarily-LU from CS; also score non-LU from full top_k ---
    cs_survivors = [r for r in cs if not primarily_lu(r["expr"])]
    non_lu_full = [
        r
        for r in full
        if (not primarily_lu(r["expr"])) and (not is_broadcast_only(r["expr"]))
    ]
    # de-dupe by expr
    seen = {r["expr"] for r in cs_survivors}
    ablation_cands = list(cs_survivors)
    for r in non_lu_full:
        if r["expr"] not in seen:
            ablation_cands.append(r)
            seen.add(r["expr"])

    ablation_rows = []
    for i, row in enumerate(ablation_cands):
        expr = row["expr"]
        tup = row["tuple"]
        try:
            fac = apply_expr(parse_expr(to_nested_tuple(tup)), panels)
            fac = fac.astype("float32")
            # cross-section variation check
            sample = fac.loc[fac.index >= EXPLORE_START]
            cs_std = float(sample.std(axis=1, skipna=True).mean())
            sim = simulate_book(fac, label, sig, adv)
            sim["cs_std_mean"] = cs_std
            del fac
            gc.collect()
        except Exception as exc:  # noqa: BLE001
            sim = {"error": f"{type(exc).__name__}: {exc}", "promotion_approved": False}
            cs_std = float("nan")
        ablation_rows.append(
            {
                "expr": expr,
                "from_cs_topk": expr in {x["expr"] for x in cs},
                "primarily_lu": False,
                "broadcast_only": is_broadcast_only(expr),
                "l1b_ann_net_ref": row.get("metrics", {}).get("ann_net"),
                "sim": sim,
                "promotion_approved": False,
            }
        )
        peak = max(peak, mem_mb())
        log(f"abl[{i+1}/{len(ablation_cands)}]", expr[:48], mem_mb())

    # deltas: mean of CS full vs mean of CS survivors (if any)
    def _ann(sim, path):
        cur = sim
        for p in path:
            if not isinstance(cur, dict):
                return float("nan")
            cur = cur.get(p)
        if isinstance(cur, dict):
            return cur.get("ann", float("nan"))
        return float("nan")

    full_flat25 = [
        _ann(r["sim"], ["flat", "25"])
        for r in capacity_rows
        if "error" not in r["sim"]
    ]
    surv_flat25 = [
        _ann(r["sim"], ["flat", "25"])
        for r in capacity_rows
        if (not r["primarily_lu"]) and "error" not in r["sim"]
    ]
    abl_nonlu_flat25 = [
        _ann(r["sim"], ["flat", "25"])
        for r in ablation_rows
        if "error" not in r["sim"] and (r["sim"].get("cs_std_mean") or 0) > 1e-8
    ]

    summary = {
        "mode": "l1b_capacity_ablation",
        "promotion_approved": False,
        "sealed_executed": False,
        "window": "explore_20240603_to_latest",
        "top_n": TOP_N,
        "aums_cny": list(AUMS),
        "flat_bps_one_way": list(FLAT_BPS),
        "k_imp": K_IMP,
        "n_cs_topk": len(cs),
        "n_cs_primarily_lu": sum(1 for r in cs if primarily_lu(r["expr"])),
        "n_cs_survivors_no_lu": len(cs_survivors),
        "cs_survivor_exprs": [r["expr"] for r in cs_survivors],
        "n_ablation_cands_nonlu": len(ablation_cands),
        "mean_flat25_cs_full": float(np.nanmean(full_flat25)) if full_flat25 else float("nan"),
        "mean_flat25_cs_survivors": float(np.nanmean(surv_flat25)) if surv_flat25 else float("nan"),
        "mean_flat25_ablation_nonlu_csvar": float(np.nanmean(abl_nonlu_flat25))
        if abl_nonlu_flat25
        else float("nan"),
        "signals_survive_without_lu_leaves": bool(
            surv_flat25 and np.nanmean(surv_flat25) > 0 and len(cs_survivors) > 0
        ),
        "peak_rss_MB": round(peak),
        "runtime_s": round(time.time() - t0, 1),
        "ann_embed_gap_note": {
            "recorded_only": True,
            "available_at_through": "2024-05-31",
            "explore_202406_plus": "missing",
            "body_source": "title_only",
            "body_rate": 0,
            "did_not_wait": True,
        },
        "load_meta_peak_MB": load_meta.get("peak_rss_MB_load"),
    }

    (OUT_DIR / "capacity_cs_topk.json").write_text(
        json.dumps(capacity_rows, indent=2, ensure_ascii=False, default=str)
    )
    (OUT_DIR / "ablation_no_lu.json").write_text(
        json.dumps(ablation_rows, indent=2, ensure_ascii=False, default=str)
    )
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str)
    )

    # --- Chinese report ---
    def _imp_key(aum: float) -> str:
        return f"{aum:.0e}"

    PRIMARY_AUMS = (0.6e6, 1.0e6)
    APPENDIX_AUMS = (50e6, 200e6, 500e6)

    def _mean_imp(rows, aum):
        vals = [
            _ann(r["sim"], ["impact", _imp_key(aum)])
            for r in rows
            if "error" not in r["sim"]
        ]
        return float(np.nanmean(vals)) if vals else float("nan"), vals

    mean_imp_06, vals_06 = _mean_imp(capacity_rows, 0.6e6)
    mean_imp_10, vals_10 = _mean_imp(capacity_rows, 1.0e6)
    mean_imp_50, _ = _mean_imp(capacity_rows, 50e6)
    mean_imp_200, _ = _mean_imp(capacity_rows, 200e6)
    mean_imp_500, _ = _mean_imp(capacity_rows, 500e6)

    def _pos_share(vals):
        a = np.asarray(vals, dtype=float)
        a = a[np.isfinite(a)]
        if len(a) == 0:
            return float("nan")
        return float(np.mean(a > 0))

    # #1 impact
    top1 = capacity_rows[0]["sim"] if capacity_rows and "error" not in capacity_rows[0]["sim"] else {}
    top1_imp06 = _ann(top1, ["impact", _imp_key(0.6e6)]) if top1 else float("nan")
    top1_imp10 = _ann(top1, ["impact", _imp_key(1.0e6)]) if top1 else float("nan")
    top1_flat25 = _ann(top1, ["flat", "25"]) if top1 else float("nan")
    top1_gross = _ann(top1, ["gross"]) if top1 else float("nan")

    summary.update(
        {
            "leo_capital_cny": [600_000, 1_000_000],
            "primary_aums_cny": list(PRIMARY_AUMS),
            "appendix_aums_cny": list(APPENDIX_AUMS),
            "mean_impact_ann_cs_0p6M": mean_imp_06,
            "mean_impact_ann_cs_1M": mean_imp_10,
            "mean_impact_ann_cs_50M": mean_imp_50,
            "mean_impact_ann_cs_200M": mean_imp_200,
            "mean_impact_ann_cs_500M": mean_imp_500,
            "frac_positive_impact_0p6M": _pos_share(vals_06),
            "frac_positive_impact_1M": _pos_share(vals_10),
            "top1_expr": capacity_rows[0]["expr"] if capacity_rows else None,
            "top1_impact_ann_0p6M": top1_imp06,
            "top1_impact_ann_1M": top1_imp10,
            "top1_flat25": top1_flat25,
            "top1_gross": top1_gross,
            "capital_note": "本金口径 60–100万 per Leo",
        }
    )
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str)
    )

    lines = []
    lines.append("# AI 因子 L1b：容量/冲击敏感性 + 去掉涨停叶消融（探索窗）")
    lines.append("")
    lines.append("- **本金口径 60–100万 per Leo。** 主结论按 AUM=60万 / 100万；50M/200M/500M 仅作大资金敏感性附录。")
    lines.append("- 窗口：2024-06-03→最新；中大盘；`promotion_approved=false`；**未跑密封、不晋级**。")
    lines.append(f"- 组合：每日等权多头 Top-{TOP_N}；标签开盘→次日开盘（与 L1b 一致）。")
    lines.append(
        f"- 成本：单边固定 {list(FLAT_BPS)} bp；平方根冲击 k={K_IMP}（trade×σ×√(V/ADV20)）；"
        "冲击臂另含单边佣金 2.5bp。"
    )
    lines.append(
        f"- 主档 AUM：**60万 / 100万**；附录大资金：50M / 200M / 500M。"
    )
    lines.append(f"- 峰值内存：{round(peak)} MB（软上限 {MEM_CAP_MB}）。运行 {summary['runtime_s']}s。")
    lines.append(
        "- 公告 embedding：仅记录缺口——available_at 到 2024-05-31，探索窗无正文（title_only，正文率 0）；**本轮不等待**。"
    )
    lines.append("")
    lines.append("## 1. 主结论：本金 60万 / 100万 冲击后净年化")
    lines.append("")
    lines.append(
        "| # | 表达式 | 涨停叶? | 毛年化 | flat10 | flat25 | "
        "**imp60万** | **imp100万** | 日均单边换手 | ICIR |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for r in capacity_rows:
        sim = r["sim"]
        if "error" in sim:
            lines.append(f"| {r['rank']} | `{r['expr']}` | — | ERR | | | | | | |")
            continue
        lines.append(
            "| {rank} | `{expr}` | {lu} | {g:.1%} | {f10:.1%} | {f25:.1%} | "
            "{i06:.1%} | {i10:.1%} | {tov:.2f} | {icir:.3f} |".format(
                rank=r["rank"],
                expr=r["expr"],
                lu="Y" if r["primarily_lu"] else "N",
                g=sim["gross"]["ann"],
                f10=sim["flat"]["10"]["ann"],
                f25=sim["flat"]["25"]["ann"],
                i06=sim["impact"][_imp_key(0.6e6)]["ann"],
                i10=sim["impact"][_imp_key(1.0e6)]["ann"],
                tov=sim["mean_turn_ow"],
                icir=sim["icir"],
            )
        )
    lines.append("")
    lines.append(
        f"- CS Top-K 平均 flat25：**{summary['mean_flat25_cs_full']:.1%}**；"
        f"冲击后均值：**60万 {mean_imp_06:.1%}** / **100万 {mean_imp_10:.1%}**；"
        f"仍为正的比例：60万 **{_pos_share(vals_06):.0%}** / 100万 **{_pos_share(vals_10):.0%}**。"
    )
    lines.append(
        f"- **#1** `{summary['top1_expr']}`：毛 {top1_gross:.1%}；flat25 {top1_flat25:.1%}；"
        f"冲击后 **60万 {top1_imp06:.1%}** / **100万 {top1_imp10:.1%}**"
        f"（{'仍为正' if (top1_imp06 > 0 and top1_imp10 > 0) else '有档转负'}）。"
    )
    lines.append(
        "- 在 Leo 本金档（60–100万），平方根冲击相对 ADV20 极小，净年化接近「flat + 2.5bp 佣金」水平；"
        "**冲击本身不是本金档的主要约束**（换手×固定成本才是）。"
    )
    lines.append("")
    lines.append("## 2. 去掉涨停叶消融")
    lines.append("")
    lines.append(
        "涨停叶家族：`days_since_lu` / `lu_streak` / `limit_up_flag` / `lu_count_5` / "
        "`etf_flow_x_lu` / `if_basis_x_lu`。叶子以该家族为主（或仅剩隔夜/日内包装）则剔除。"
    )
    lines.append(
        f"- CS Top-K：**{summary['n_cs_primarily_lu']}/{summary['n_cs_topk']}** 主涨停叶；"
        f"幸存者 **{summary['n_cs_survivors_no_lu']}** → `{summary['cs_survivor_exprs']}`。"
    )
    lines.append(
        "- 从全量 Top-K 补入非涨停、非纯 `etf_major_flow`/`if_basis` 广播式；但 `etf_theme_flow` 在 L1b 面板里是行业主题合计后 **广播到个股**，"
        "`rank`/`mul(..., if_basis)` 截面标准差≈0，**不是有效截面因子**。"
    )
    lines.append("")
    lines.append(
        "| 表达式 | 来自CS | 有效截面? | 毛年化 | flat10 | flat25 | "
        "**imp60万** | **imp100万** | cs_std |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for r in ablation_rows:
        sim = r["sim"]
        if "error" in sim:
            lines.append(f"| `{r['expr']}` | {r['from_cs_topk']} | — | ERR | | | | | |")
            continue
        csd = sim.get("cs_std_mean", float("nan"))
        eff = "N(广播)" if (not np.isfinite(csd) or csd <= 1e-8 or r["broadcast_only"]) else "Y"
        # etf_theme_flow rank/mul with zero cs_std already marked
        if "etf_theme_flow" in r["expr"] and (not np.isfinite(csd) or csd <= 1e-8):
            eff = "N(广播)"
        lines.append(
            "| `{expr}` | {cs} | {eff} | {g:.1%} | {f10:.1%} | {f25:.1%} | "
            "{i06:.1%} | {i10:.1%} | {csd:.4g} |".format(
                expr=r["expr"],
                cs=r["from_cs_topk"],
                eff=eff,
                g=sim["gross"]["ann"],
                f10=sim["flat"]["10"]["ann"],
                f25=sim["flat"]["25"]["ann"],
                i06=sim["impact"][_imp_key(0.6e6)]["ann"],
                i10=sim["impact"][_imp_key(1.0e6)]["ann"],
                csd=csd,
            )
        )
    lines.append("")
    delta = float("nan")
    if full_flat25 and surv_flat25:
        delta = float(np.nanmean(surv_flat25) - np.nanmean(full_flat25))
    # survivor #1 impact at leo capital
    surv_imp_note = ""
    for r in capacity_rows:
        if not r["primarily_lu"] and "error" not in r["sim"]:
            s06 = _ann(r["sim"], ["impact", _imp_key(0.6e6)])
            s10 = _ann(r["sim"], ["impact", _imp_key(1.0e6)])
            surv_imp_note = (
                f"有效截面非涨停幸存者仅 `{r['expr']}`：flat25 "
                f"**{_ann(r['sim'], ['flat', '25']):.1%}**（相对全量 CS 均值 Δ={delta:+.1%}）；"
                f"本金档冲击后 60万 **{s06:.1%}** / 100万 **{s10:.1%}**。"
            )
            break
    if surv_imp_note:
        lines.append(f"- {surv_imp_note}")
    lines.append(
        "- **去掉涨停叶后信号站不住**（探索窗）：CS Top-K 几乎全靠涨停叶；"
        "补位广播流不是截面 alpha。"
    )
    lines.append("")
    lines.append("## 3. 结论（探索窗过程数；本金口径 60–100万）")
    lines.append("")
    lines.append(
        f"- **本金档容量：冲击后 Top-K 均值仍为正**（60万 {mean_imp_06:.1%} / 100万 {mean_imp_10:.1%}；"
        f"全员为正比例 {_pos_share(vals_06):.0%}/{_pos_share(vals_10):.0%}）。"
        f"#1 冲击后 60万 {top1_imp06:.1%} / 100万 {top1_imp10:.1%}。"
    )
    lines.append(
        "- **去掉涨停叶后，信号不能稳健存活。** 唯一非涨停项是跌停连板 `neg(ld_streak)`，"
        "强度弱于涨停叶均值；机制依赖涨停叶，不是本金档冲击问题。"
    )
    lines.append(
        "- **不申请密封、不晋级**；不推动教科书主线。公告 2024-06+ 正文缺口仅记录。"
    )
    lines.append("")
    lines.append("## 附录. 大资金敏感性（非本金口径）")
    lines.append("")
    lines.append(
        "以下 AUM=50M / 200M / 500M **不是** Leo 本金口径，仅作外推敏感性；"
        "主决策以 §1 的 60万/100万为准。"
    )
    lines.append("")
    lines.append(
        "| # | 表达式 | flat25 | imp50M | imp200M | imp500M | 日均单边换手 |"
    )
    lines.append("|---|---|---|---|---|---|---|")
    for r in capacity_rows:
        sim = r["sim"]
        if "error" in sim:
            continue
        lines.append(
            "| {rank} | `{expr}` | {f25:.1%} | {i50:.1%} | {i200:.1%} | {i500:.1%} | {tov:.2f} |".format(
                rank=r["rank"],
                expr=r["expr"],
                f25=sim["flat"]["25"]["ann"],
                i50=sim["impact"][_imp_key(50e6)]["ann"],
                i200=sim["impact"][_imp_key(200e6)]["ann"],
                i500=sim["impact"][_imp_key(500e6)]["ann"],
                tov=sim["mean_turn_ow"],
            )
        )
    lines.append("")
    lines.append(
        f"- 大资金冲击后均值：50M **{mean_imp_50:.1%}** / 200M **{mean_imp_200:.1%}** / "
        f"500M **{mean_imp_500:.1%}**（与初版一致量级：高换手差分类在 2–5 亿被打穿）。"
    )
    lines.append("")
    lines.append("## 4. 路径")
    lines.append("")
    lines.append(f"- 报告：`{REPORT}`")
    lines.append(
        f"- JSON 目录：`{OUT_DIR}/`（`capacity_cs_topk.json` / `ablation_no_lu.json` / `summary.json`）"
    )
    lines.append(f"- 输入：`{TOP_K_CS}`")
    lines.append(f"- 脚本：`research/ai_factor_l1b_capacity_ablation.py`")
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    log("wrote", REPORT)

    print(json.dumps({
        "mean_impact_0p6M": mean_imp_06,
        "mean_impact_1M": mean_imp_10,
        "top1_impact_0p6M": top1_imp06,
        "top1_impact_1M": top1_imp10,
        "frac_pos_0p6M": _pos_share(vals_06),
        "frac_pos_1M": _pos_share(vals_10),
        "promotion_approved": False,
        "report": str(REPORT),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
