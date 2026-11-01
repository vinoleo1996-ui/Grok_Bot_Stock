#!/usr/bin/env python3
"""GP reopen v2: load L1b structural + L1c ann/easystock leaves; hard gates baked.
Explore only. promotion_approved=false. Does NOT overwrite gp_reopen_hardgate/.
"""
from __future__ import annotations
import gc, importlib.util, json, math, os, resource, sys, time, types
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path("/workspace/QuantLab")
OUT = ROOT / "output/ai_factor/gp_reopen_hardgate_v2_ann"
REPORT = ROOT / "output/alpha/AI_FACTOR_GP_REOPEN_HARDGATE_V2_ANN_ZH.md"
EXPLORE_START = pd.Timestamp("2024-06-03")
LOOKBACK_START = pd.Timestamp("2024-01-02")
IMP60_FLOOR = 0.10
COV_NONEMPTY_MIN = 0.08
SEED = 20261012
MAX_EVAL = 200
POP, GEN, TOP_K = 28, 7, 20
COST = 0.0025
PROMOTION_APPROVED = False
MEM_CAP_MB = 2500
WINDOW = "gp_reopen_hardgate_v2_ann_20240603_explore"

# Expanded leaf space: L1b structural + L1c easystock/ann (no LD-primary, no pure LU-ctrl)
SEARCH_LEAVES = (
    # overnight / flow / lockup / basis
    "overnight_ret", "intraday_ret", "on_minus_id",
    "etf_theme_flow", "etf_major_flow",
    "lockup_S_20", "if_basis", "if_basis_x_on",
    # easystock structural (L1c) — stock-level + promote (broadcast ok as aux leaf)
    "lu_height", "lu_promote_rate",
    # ann title event counts (title_only; no invented body)
    "ann_n_5", "ann_buyback_5", "ann_penalty_5", "ann_earn_signed_5",
    "ann_insider_dec_5",  # one leaf among many; not sole family
)

t0 = 0.0
def mem_mb(): return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
def log(*a): print(f"[gp_v2ann {time.time()-t0:5.0f}s {mem_mb():.0f}MB]", *a, flush=True)

def _ensure_pkgs():
    if "quantlab" not in sys.modules:
        q = types.ModuleType("quantlab"); q.__path__ = [str(ROOT / "quantlab")]; sys.modules["quantlab"] = q
    if "quantlab.factors" not in sys.modules or not hasattr(sys.modules["quantlab.factors"], "__path__"):
        f = types.ModuleType("quantlab.factors"); f.__path__ = [str(ROOT / "quantlab/factors")]; sys.modules["quantlab.factors"] = f
    def load(name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod
        assert spec.loader; spec.loader.exec_module(mod); return mod
    load("quantlab.factors.ops", ROOT / "quantlab/factors/ops.py")
    af = types.ModuleType("quantlab.factors.ai_factory"); af.__path__ = [str(ROOT / "quantlab/factors/ai_factory")]
    sys.modules["quantlab.factors.ai_factory"] = af
    for n in ("ledger", "novelty", "fitness", "evaluate", "search", "structural_leaves"):
        load(f"quantlab.factors.ai_factory.{n}", ROOT / f"quantlab/factors/ai_factory/{n}.py")

def _import_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod
    assert spec.loader; spec.loader.exec_module(mod); return mod

def clean(o):
    if isinstance(o, float) and (math.isnan(o) or math.isinf(o)): return None
    if isinstance(o, dict): return {k: clean(v) for k, v in o.items()}
    if isinstance(o, list): return [clean(x) for x in o]
    return o

def main() -> int:
    global t0
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    if os.environ.get("LEO_AI_FACTOR_EXPLORE_OK") != "1":
        print("NEED LEO_AI_FACTOR_EXPLORE_OK=1", file=sys.stderr); return 2

    _ensure_pkgs()
    l1b = _import_mod("ai_factor_l1b_structural_explore", ROOT / "research/ai_factor_l1b_structural_explore.py")
    l1c = _import_mod("ai_factor_l1c_explore", ROOT / "research/ai_factor_l1c_explore.py")
    sci = _import_mod("ai_factor_l1d_shortlist_coverage_impact", ROOT / "research/ai_factor_l1d_shortlist_coverage_impact.py")
    import quantlab.factors.ai_factory.fitness as fit_mod
    import quantlab.factors.ai_factory.search as search_mod
    from quantlab.factors.ai_factory.ledger import append_attempt
    from quantlab.factors.ai_factory.search import GPConfig, gp_search
    from quantlab.factors.ops import apply_expr

    # Bake hard gates into fitness
    _orig = fit_mod.fitness_score_l1b
    def fitness_hardgate(factor, label, **kw):
        met = _orig(factor, label, **kw)
        icir = met.get("icir", float("nan"))
        try:
            fac_e = factor.loc[factor.index >= EXPLORE_START]
            nr = float(np.isfinite(fac_e.to_numpy(dtype=np.float64, copy=False)).mean())
        except Exception:
            nr = float("nan")
        met["nonempty_rate"] = nr
        hard_fail = []
        if not (isinstance(icir, float) and math.isfinite(icir) and icir > 0):
            hard_fail.append("icir_le_0")
        if not (isinstance(nr, float) and math.isfinite(nr) and nr >= COV_NONEMPTY_MIN):
            hard_fail.append("coverage_sparse")
        if met.get("novelty_fail"):
            hard_fail.append("textbook_corr")
        ann = met.get("ann_net")
        if ann is None or not (isinstance(ann, float) and math.isfinite(ann) and ann > 0):
            hard_fail.append("ann_net_le_0")
        met["hard_gate_fail"] = hard_fail
        if hard_fail:
            met["fitness"] = -1e9
        else:
            fit = float(met.get("fitness") or -1e9)
            if math.isfinite(nr):
                fit += 0.05 * min(nr, 0.5)
            met["fitness"] = fit
        met["promotion_approved"] = False
        return met
    fit_mod.fitness_score_l1b = fitness_hardgate
    search_mod.fitness_score_l1b = fitness_hardgate

    log("loading L1b structural panels")
    panels, label, public, load_meta = l1b.load_structural_panels()
    peak = mem_mb()
    log("attach L1c easystock + ann title panels")
    panels, label, public, load_meta = l1c.attach_l1c_panels(panels, label, public, load_meta)
    peak = max(peak, mem_mb())

    sp = {k: panels[k] for k in SEARCH_LEAVES if k in panels}
    missing = [k for k in SEARCH_LEAVES if k not in panels]
    # drop all-NaN leaves (e.g. theme_lu_density if ever included)
    dropped_nan = []
    for k in list(sp.keys()):
        if sp[k].notna().sum().sum() == 0:
            dropped_nan.append(k); del sp[k]
    # leaf nonzero diagnostics
    leaf_diag = {}
    for k, v in sp.items():
        arr = v.to_numpy(dtype=np.float64, copy=False)
        finite = np.isfinite(arr)
        nz = finite & (arr != 0)
        leaf_diag[k] = {
            "nonempty_rate": float(finite.mean()),
            "nonzero_rate": float(nz.mean()),
            "shape": list(v.shape),
        }
    log("search leaves", sorted(sp.keys()), "missing", missing, "dropped_nan", dropped_nan, "peak", peak)
    del panels
    gc.collect()

    cols = list(next(iter(sp.values())).columns)
    cal = next(iter(sp.values())).index
    sig, adv = sci.load_sig_adv(cols, cal)
    peak = max(peak, mem_mb())

    run_ledger = OUT / "ledger_run.jsonl"
    if run_ledger.exists(): run_ledger.unlink()
    main_ledger = ROOT / "output/ai_factor/ledger.jsonl"
    n_before = sum(1 for x in main_ledger.read_text().splitlines() if x.strip()) if main_ledger.exists() else 0

    cfg = GPConfig(
        population=POP, generations=GEN, max_evaluations=MAX_EVAL, top_k=TOP_K,
        seed=SEED, universe="midlarge_top1500_or_csi300_500", cost=COST,
        window=WINDOW, ledger_path=run_ledger,
        structural_only=True, ban_textbook=True, use_l1b_fitness=True,
        public_panels=public, lambda_complexity=0.015, lambda_turnover=1.0, top_n=50,
    )
    (OUT / "run_meta.json").write_text(json.dumps({
        "promotion_approved": False, "sealed": False, "window": WINDOW,
        "max_evaluations": MAX_EVAL, "population": POP, "generations": GEN,
        "search_leaves": sorted(sp.keys()), "missing_leaves": missing,
        "dropped_nan_leaves": dropped_nan, "leaf_diag": leaf_diag,
        "hard_gates": ["icir>0", f"nonempty>={COV_NONEMPTY_MIN}", "ann_net>0",
                       "novelty_|corr|<=0.5", "ban_textbook", "structural_only",
                       f"post_impact+flat25@60&100万>={IMP60_FLOOR}"],
        "capital_cny": [600000, 1000000], "ledger_N_before": n_before,
        "leo_explore_ok": True, "load_meta": load_meta,
        "parent_script": "ai_factor_gp_reopen_hardgate.py",
        "enhancement": "l1c.attach_l1c_panels (lu_height/lu_promote_rate/ann_*)",
    }, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    log("gp_search start", "N_before", n_before, "n_leaves", len(sp))
    res = gp_search(sp, label, cfg)
    peak = max(peak, mem_mb())
    log("gp done evals", res.evaluations, "top_k", len(res.top_k), "peak", peak)

    run_rows = [json.loads(x) for x in run_ledger.read_text().splitlines() if x.strip()] if run_ledger.exists() else []
    for r in run_rows:
        append_attempt(engine=r["engine"], seed=r["seed"], universe=r["universe"], cost=r["cost"],
                       window=r["window"], expr_str=r.get("expr_str", ""), fitness=r.get("fitness"),
                       notes=(r.get("notes") or "") + ";gp_reopen_hardgate_v2_ann", path=main_ledger)
    n_after = sum(1 for x in main_ledger.read_text().splitlines() if x.strip())

    gate_ok, demoted, all_rows = [], [], []
    for c in res.top_k:
        expr = c.expr.to_str()
        try:
            fac = apply_expr(c.expr, sp).astype("float32")
            cov = sci.coverage_stats(fac)
            cs = sci.cs_std_stats(fac)
            sim = sci.simulate_book(fac, label, sig, adv) if cs.get("passes_cs_variation") else {"skipped": True}
            m = sci.pack_metrics(sim if not sim.get("skipped") else None)
            max_corr = (c.metrics or {}).get("max_abs_public_corr")
            novelty_fail = bool((c.metrics or {}).get("novelty_fail"))
            icir = m.get("icir", c.train_icir)
            nr = cov.get("nonempty_rate", float("nan"))
            impact_ok = (math.isfinite(m.get("flat25", float("nan"))) and m["flat25"] > 0
                         and math.isfinite(m.get("imp60_p25", float("nan"))) and m["imp60_p25"] >= IMP60_FLOOR
                         and math.isfinite(m.get("imp100_p25", float("nan"))) and m["imp100_p25"] >= IMP60_FLOOR)
            icir_ok = math.isfinite(icir) and icir > 0
            cov_ok = bool(cov.get("passes_coverage"))
            rank_fill = False
            if "rank(" in expr and nr is not None and nr < COV_NONEMPTY_MIN:
                rank_fill = True
            # broadcast-only demote heuristic: sole leaf is market broadcast
            broadcast_only = expr.strip() in (
                "lu_promote_rate", "rank(lu_promote_rate)", "neg(lu_promote_rate)",
                "mkt_max_height", "mkt_lu_breadth", "rank(mkt_lu_breadth)",
            )
            verdict = "GATE_OK"
            if rank_fill: verdict = "FAIL_RANK_FILL"
            elif broadcast_only: verdict = "DEMOTE_BROADCAST"
            elif not cov_ok: verdict = "FAIL_SPARSE"
            elif novelty_fail or (isinstance(max_corr, float) and math.isfinite(max_corr) and max_corr > 0.5):
                verdict = "DEMOTE_TEXTBOOK"
            elif not impact_ok: verdict = "FAIL_GATE"
            elif not icir_ok: verdict = "FAIL_ICIR"
            row = {
                "expr": expr, "tuple": c.expr.to_tuple(), "train_icir": c.train_icir,
                "fitness": c.fitness, "metrics": m, "coverage": cov, "cs_stats": cs,
                "gp_metrics": {k: v for k, v in (c.metrics or {}).items() if k != "public_corr"},
                "max_abs_public_corr": max_corr, "novelty_fail": novelty_fail,
                "rank_fill_cov": rank_fill, "broadcast_only": broadcast_only,
                "verdict": verdict,
                "gate_ok": verdict == "GATE_OK", "promotion_approved": False,
                "diagnostic_overlay_candidate": verdict == "GATE_OK",
                "capital_cny_tiers": [600000, 1000000],
            }
            all_rows.append(row)
            if verdict == "GATE_OK": gate_ok.append(row)
            elif verdict in ("DEMOTE_TEXTBOOK", "DEMOTE_BROADCAST"): demoted.append(row)
            del fac; gc.collect()
        except Exception as exc:
            all_rows.append({"expr": expr, "verdict": "ERROR", "error": str(exc), "promotion_approved": False})

    peak = max(peak, mem_mb())
    summary = {
        "promotion_approved": False, "sealed": False, "strategy_weights": False,
        "evaluations": res.evaluations, "ledger_N_before": n_before, "ledger_N_after": n_after,
        "n_top_k": len(res.top_k), "n_gate_ok": len(gate_ok), "n_demote": len(demoted),
        "n_search_leaves": len(sp), "search_leaves": sorted(sp.keys()),
        "peak_rss_MB": round(peak), "runtime_s": round(time.time() - t0, 1),
        "under_mem_cap": peak < MEM_CAP_MB,
        "gate_ok_exprs": [r["expr"] for r in gate_ok],
        "hard_gates_baked": True,
        "out_dir": str(OUT.relative_to(ROOT)),
    }
    (OUT / "top_k.json").write_text(json.dumps(clean([c.as_row() for c in res.top_k]), indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "post_gate_rows.json").write_text(json.dumps(clean(all_rows), indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "gate_ok.json").write_text(json.dumps(clean(gate_ok), indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "demoted.json").write_text(json.dumps(clean(demoted), indent=2, ensure_ascii=False), encoding="utf-8")
    handback = {
        "promotion_approved": False, "for_alpha_shortlist_adjudication": True,
        "not_strategy_weights": True, "diagnostic_overlay_candidates_only": True,
        "gate_ok": [{
            "expr": r["expr"],
            "nonempty_rate": (r.get("coverage") or {}).get("nonempty_rate"),
            "flat25": (r.get("metrics") or {}).get("flat25"),
            "imp60_p25": (r.get("metrics") or {}).get("imp60_p25"),
            "imp100_p25": (r.get("metrics") or {}).get("imp100_p25"),
            "icir": (r.get("metrics") or {}).get("icir"),
            "rank_fill_cov": r.get("rank_fill_cov"),
            "max_abs_public_corr": r.get("max_abs_public_corr"),
            "verdict": r["verdict"],
            "diagnostic_overlay_candidate": True,
        } for r in gate_ok],
        "n_gate_ok": len(gate_ok),
        "n_demote": len(demoted),
        "search_leaves": sorted(sp.keys()),
        "ledger_N_before": n_before, "ledger_N_after": n_after,
        "source": "gp_reopen_hardgate_v2_ann",
        "note": "empty gate_ok is valid; Alpha adjudicates only GATE_OK rows",
    }
    (OUT / "alpha_handback_package.json").write_text(
        json.dumps(clean(handback), indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "summary.json").write_text(json.dumps(clean(summary), indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# AI 因子 GP 硬闸重开 v2（ann/结构叶补齐 · explore）",
        "",
        f"- **时间：** 2026-10-12（America/New_York）",
        f"- **promotion_approved：** false；**密封：** 未开；**不交 Strategy 权重**",
        f"- **窗口：** {WINDOW}；宇宙：中大盘 top1500 / 沪深300∪中证500；本金 60万/100万",
        f"- 账本：N {n_before} → {n_after}（+{n_after-n_before}）",
        f"- GP：evals={res.evaluations}/{MAX_EVAL}；Top-K={len(res.top_k)}；峰值 RSS≈{peak:.0f}MB",
        f"- 叶空间：{len(sp)} 叶（上轮 gp_reopen_hardgate 仅 7 叶）",
        f"- 搜索叶：{', '.join(f'`{k}`' for k in sorted(sp.keys()))}",
        f"- 缺失叶：{missing or '无'}；全 NaN 丢弃：{dropped_nan or '无'}",
        f"- 硬闸烘焙：ICIR>0 · nonempty≥{COV_NONEMPTY_MIN:.0%} · ann_net>0 · |corr|教科书≤0.5 · ban_textbook · structural_only",
        f"- 事后冲击闸：flat25>0 且 冲击+25bp@60万∧100万≥{IMP60_FLOOR:.0%}",
        f"- 增强：`l1c.attach_l1c_panels` → lu_height / lu_promote_rate / ann_*",
        "",
        "## GATE_OK（回传 Alpha 短清单裁决包）",
        "",
        "| # | 表达式 | flat25 | 60万+25bp | 100万+25bp | ICIR | nonempty | max|ρ| | 裁决 |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    def fp(x):
        return f"{x:.2%}" if isinstance(x, float) and math.isfinite(x) else "—"
    def ff(x):
        return f"{x:.3f}" if isinstance(x, float) and math.isfinite(x) else "—"
    for i, r in enumerate(gate_ok, 1):
        m = r.get("metrics") or {}; cov = r.get("coverage") or {}
        lines.append(
            f"| {i} | `{r['expr']}` | {fp(m.get('flat25'))} | {fp(m.get('imp60_p25'))} | "
            f"{fp(m.get('imp100_p25'))} | {ff(m.get('icir'))} | {ff(cov.get('nonempty_rate'))} | "
            f"{ff(r.get('max_abs_public_corr'))} | GATE_OK |"
        )
    if not gate_ok:
        lines.append("| — | （本轮无过全硬闸） | — | — | — | — | — | — | — |")
    lines += [
        "",
        f"- DEMOTE（教科书/广播）：{len(demoted)}；其余见 `post_gate_rows.json`",
        "- 回传包：`output/ai_factor/gp_reopen_hardgate_v2_ann/alpha_handback_package.json`",
        "- **不开密封、不交 Strategy 权重**；仅 diagnostic_overlay_candidate",
        "",
        "## Top 表达式（含未过闸，按 fitness）",
        "",
        "| # | 表达式 | verdict | fitness | ICIR | flat25 | 60万 |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for i, r in enumerate(all_rows[:15], 1):
        m = r.get("metrics") or {}
        lines.append(
            f"| {i} | `{r.get('expr','')}` | {r.get('verdict')} | "
            f"{ff(r.get('fitness') if isinstance(r.get('fitness'), float) else float('nan'))} | "
            f"{ff(m.get('icir'))} | {fp(m.get('flat25'))} | {fp(m.get('imp60_p25'))} |"
        )
    lines += [
        "",
        "## 产物",
        f"- 报告：`{REPORT.relative_to(ROOT)}`",
        f"- JSON：`output/ai_factor/gp_reopen_hardgate_v2_ann/`",
        f"- 账本：`output/ai_factor/ledger.jsonl` N={n_after}",
        "",
        "## 禁令自检",
        "- promotion_approved=false；未开密封；未改短清单；未重跑 L1h；未改 HANDOFF/PARTICIPATION",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    log("DONE", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if peak < MEM_CAP_MB else 1

if __name__ == "__main__":
    raise SystemExit(main())
