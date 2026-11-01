#!/usr/bin/env python3
"""GP reopen v5: FORCED binary cross (mul/sub/div) L1h delta/CV × structural leaves.
Reject sole-leaf pure ts_* stacks; ban ann_*/lockup_S_20/idx·lev level shells.
Hard gates baked. Explore only. promotion_approved=false. No L1h batch rerun.
"""
from __future__ import annotations
import gc, importlib.util, json, math, os, re, resource, sys, time, types
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path("/workspace/QuantLab")
OUT = ROOT / "output/ai_factor/gp_reopen_hardgate_v5b_struct_fix"
REPORT = ROOT / "output/alpha/AI_FACTOR_GP_REOPEN_HARDGATE_V5B_STRUCT_OFF_ZH.md"
EXPLORE_START = pd.Timestamp("2024-06-03")
LOOKBACK_START = pd.Timestamp("2024-01-02")
IMP60_FLOOR = 0.10
COV_NONEMPTY_MIN = 0.08
SEED = 20261016  # v5_forced_cross
MAX_EVAL = 220
POP, GEN, TOP_K = 30, 8, 20
COST = 0.0025
PROMOTION_APPROVED = False
MEM_CAP_MB = 2500
WINDOW = "gp_reopen_hardgate_v5b_struct_fix_20240603_explore"

# v5 leaf partitions — forced L1h × structural binary cross
L1H_CROSS_LEAVES = (
    # idx weight *delta* (not level / size shell)
    "idx_w500_delta_20", "idx_w_delta_20", "neg_idx_w_delta_20", "abs_idx_w_delta_20",
    "idx_w300_delta_20",
    # liq regime CV/burst
    "liq_cv_20", "neg_liq_cv_20", "liq_burst_10", "amt_cv_20", "neg_amt_cv_20",
    # lev *revision* deltas (not lev_pit level)
    "lev_delta_20", "abs_lev_delta_20",
)
STRUCT_CROSS_LEAVES = (
    "overnight_ret", "intraday_ret", "on_minus_id",
    "etf_theme_flow", "etf_major_flow",
    "if_basis", "if_basis_x_on",
    "lu_height", "lu_promote_rate",
)
# lockup kept out of primary pool (v2e++ diversity saturated); aux empty for v5
AUX_LEAVES = ()

SEARCH_LEAVES = L1H_CROSS_LEAVES + STRUCT_CROSS_LEAVES

# Explicitly excluded (ann / level shells / lockup)
EXCLUDED_LEAVES = (
    "ann_n_5", "ann_buyback_5", "ann_penalty_5", "ann_earn_signed_5", "ann_insider_dec_5",
    "idx_w500", "idx_w300", "idx_w", "lev_pit", "neg_lev_pit",
    "lockup_S_20",
)

# Already-shortlisted / adjudicated exprs — exact + isomorphic demote
KNOWN_SHORTLIST_EXACT = frozenset({
    "rank(ts_std_10(ann_insider_dec_5))",
    "abs(ts_std_10(ts_delta_5(ann_insider_dec_5)))",
    "ts_std_10(fsr_delta_20)",
    "fsr_delta_20",
    "abs(ts_std_10(ts_delta_5(fsr)))",
    "ts_std_10(fsr)",
    "abs(fsr_delta_20)",
    "mul(rank(ocf_to_profit), rank(dv_ttm))",
    "ts_std_10(gm_pit)",
    "neg(idx_w500_delta_20)",
    "rank(neg(idx_w500_delta_20))",
    # v2e+ Alpha adjudication
    "ts_mean_20(sub(ts_mean_5(overnight_ret), ts_max_20(lu_height)))",
    "ts_mean_20(sub(ann_insider_dec_5, ts_max_20(lu_height)))",
    "ts_mean_20(sub(ann_insider_dec_5, ts_delta_5(overnight_ret)))",
    # v3_nonann / v2e++ diversity lockup
    "ts_std_10(ts_mean_20(ts_mean_10(lockup_S_20)))",
    "ts_std_10(rank(ts_std_10(lockup_S_20)))",
})

OPS = {
    "add", "sub", "mul", "div", "neg", "abs", "rank", "zscore",
    "industry_neutral", "size_neutral",
}
for _k in (1, 5, 10, 20, 60):
    OPS |= {f"delay_{_k}", f"ts_mean_{_k}", f"ts_std_{_k}", f"ts_delta_{_k}", f"ts_max_{_k}"}

t0 = 0.0
def mem_mb(): return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
def log(*a): print(f"[gp_v5b {time.time()-t0:5.0f}s {mem_mb():.0f}MB]", *a, flush=True)

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

def leaves_in(expr: str) -> frozenset[str]:
    return frozenset(t for t in re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", expr) if t not in OPS)

def requires_cross(expr: str) -> bool:
    """v5: MUST binary-cross L1h delta/CV with structural via mul/sub/div (add allowed)."""
    e = expr.strip()
    L = leaves_in(e)
    # prefer mul/sub/div; add still counts as binary
    has_bin = any(op + "(" in e for op in ("mul", "sub", "div", "add"))
    if not has_bin:
        return False
    l1h = set(L1H_CROSS_LEAVES)
    struct = set(STRUCT_CROSS_LEAVES)
    has_l1h = bool(L & l1h)
    has_struct = bool(L & struct)
    # required: at least one L1h leaf AND one structural leaf
    return has_l1h and has_struct

def is_sole_leaf_ts_stack(expr: str) -> bool:
    """True if expr is a single-leaf chain of ts_*/delay/rank/zscore/neg/abs only."""
    L = leaves_in(expr)
    if len(L) != 1:
        return False
    # any binary op means not sole-leaf stack
    if any(op + "(" in expr for op in ("mul", "sub", "div", "add")):
        return False
    return True

def isomorphic_reason(expr: str) -> str | None:
    """Return demote reason if expr is exact or highly isomorphic to known shortlist."""
    e = expr.strip()
    if e in KNOWN_SHORTLIST_EXACT:
        return "EXACT_SHORTLIST"
    L = leaves_in(e)
    if any(x.startswith("ann_") for x in L):
        return "ANN_PRIMARY_BANNED"
    if "lockup_S_20" in L:
        return "LOCKUP_BANNED_V5"
    if any(x in L for x in ("idx_w500", "idx_w300", "idx_w", "lev_pit", "neg_lev_pit")):
        return "LEVEL_SHELL_BANNED"
    if is_sole_leaf_ts_stack(e):
        return "SOLE_LEAF_TS_STACK_BANNED"
    if L == frozenset({"overnight_ret", "lu_height"}) or L == frozenset({"overnight_ret", "lu_height", "intraday_ret"}):
        if "sub(" in e and ("ts_mean" in e or "ts_max" in e):
            return "ISO_OVERNIGHT_LU_V2EPLUS"
    if L <= frozenset({"idx_w500_delta_20"}) and ("neg(" in e or e in ("idx_w500_delta_20", "rank(idx_w500_delta_20)")):
        return "ISO_IDX_W500_DELTA_SHORTLIST"
    # v5: MUST L1h × structural binary cross
    if not requires_cross(e):
        return "NO_L1H_STRUCT_CROSS"
    return None

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
    l1h = _import_mod("ai_factor_l1h_new_mech_family_explore", ROOT / "research/ai_factor_l1h_new_mech_family_explore.py")
    sci = _import_mod("ai_factor_l1d_shortlist_coverage_impact", ROOT / "research/ai_factor_l1d_shortlist_coverage_impact.py")
    import quantlab.factors.ai_factory.fitness as fit_mod
    import quantlab.factors.ai_factory.search as search_mod
    from quantlab.factors.ai_factory.ledger import append_attempt
    from quantlab.factors.ai_factory.search import GPConfig, gp_search
    from quantlab.factors.ops import apply_expr, Expr, OPS as OPS_TABLE

    # --- v5: bias population/mutation toward mul/sub/div of L1h × structural ---
    _l1h = list(L1H_CROSS_LEAVES)
    _struct = list(STRUCT_CROSS_LEAVES)
    _bin_ops = ("mul", "sub", "div", "add")  # mul/sub/div preferred via weights
    _bin_w = (0.35, 0.35, 0.20, 0.10)
    _ts_wrap = ("ts_mean_5", "ts_mean_10", "ts_mean_20", "ts_std_10", "ts_delta_5", "ts_max_20", "rank", "neg", "abs")

    def _leaf_expr(rng, name):
        return Expr("leaf", name)

    def _maybe_wrap(rng, e, p=0.55):
        if rng.random() > p:
            return e
        w = str(rng.choice(_ts_wrap))
        return Expr("op", w, (e,))

    def _forced_cross_expr(rng, leaves=None, depth=1):
        """Build mul/sub/div( wrap(L1h), wrap(struct) ) with high probability.
        Signature matches search._rand_expr(rng, leaves, depth=1).
        """
        leaf_pool = list(leaves) if leaves is not None else list(SEARCH_LEAVES)
        if rng.random() < 0.85:
            op = str(rng.choice(_bin_ops, p=list(_bin_w)))
            # pick L1h / struct from available panels when possible
            l1h_avail = [x for x in _l1h if x in leaf_pool] or list(_l1h)
            st_avail = [x for x in _struct if x in leaf_pool] or list(_struct)
            a = _maybe_wrap(rng, _leaf_expr(rng, str(rng.choice(l1h_avail))))
            b = _maybe_wrap(rng, _leaf_expr(rng, str(rng.choice(st_avail))))
            if rng.random() < 0.5:
                a, b = b, a
            root = Expr("op", op, (a, b))
            # optional outer wrap (still keeps binary cross inside)
            if rng.random() < 0.45:
                root = _maybe_wrap(rng, root, p=1.0)
            return root
        # fallback: original random over leaf pool
        return search_mod._rand_expr_orig(rng, leaf_pool, depth)

    search_mod._rand_expr_orig = search_mod._rand_expr
    search_mod._rand_expr = _forced_cross_expr

    def _mutate_forced(rng, expr, leaves):
        if rng.random() < 0.55:
            return _forced_cross_expr(rng)
        return search_mod._mutate_orig(rng, expr, leaves)

    search_mod._mutate_orig = search_mod._mutate
    search_mod._mutate = _mutate_forced
    log("v5 forced-cross rand/mutate patched (mul/sub/div L1h×struct)")

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
            # soft bonus if factor looks like a real cross (nonempty + variation already in fitness)
            met["fitness"] = fit
        met["promotion_approved"] = False
        return met
    fit_mod.fitness_score_l1b = fitness_hardgate
    search_mod.fitness_score_l1b = fitness_hardgate

    log("loading L1b structural panels")
    panels, label, public, load_meta = l1b.load_structural_panels()
    peak = mem_mb()
    log("attach L1c easystock (+ann built but excluded from search)")
    panels, label, public, load_meta = l1c.attach_l1c_panels(panels, label, public, load_meta)
    peak = max(peak, mem_mb())

    # Drop ann panels from memory — not in search pool
    dropped_ann = []
    for k in list(panels.keys()):
        if k.startswith("ann_"):
            dropped_ann.append(k)
            del panels[k]
    gc.collect()

    # Attach selected L1h builders (reuse code; do NOT re-run L1h candidate batch)
    mask = panels["overnight_ret"].notna()
    cols = list(panels["overnight_ret"].columns)
    cal = panels["overnight_ret"].index
    l1h_meta = {}
    log("attach L1h liq panels (selected)")
    liq_panels, liq_gap = l1h.build_liq_panels(cal, cols, mask)
    l1h_meta["liq"] = {k: liq_gap.get(k) for k in ("ok", "family", "nonempty_liq_cv_20", "nonempty_neg_liq_cv_20") if k in liq_gap or k in ("ok", "family")}
    for k in ("liq_cv_20", "neg_liq_cv_20", "liq_burst_10", "amt_cv_20", "neg_amt_cv_20"):
        if k in liq_panels:
            panels[k] = liq_panels[k]
    del liq_panels; gc.collect()
    peak = max(peak, mem_mb())

    log("attach L1h idx panels (delta only)")
    idx_panels, idx_gap = l1h.build_idx_panels(cal, cols, mask)
    l1h_meta["idx"] = {"ok": idx_gap.get("ok"), "family": idx_gap.get("family")}
    for k in ("idx_w500_delta_20", "idx_w_delta_20", "neg_idx_w_delta_20", "abs_idx_w_delta_20", "idx_w300_delta_20"):
        if k in idx_panels:
            panels[k] = idx_panels[k]
    del idx_panels; gc.collect()
    peak = max(peak, mem_mb())

    log("attach L1h lev panels (delta only)")
    lev_panels, lev_gap = l1h.build_lev_panels(cal, cols, mask)
    l1h_meta["lev"] = {"ok": lev_gap.get("ok"), "family": lev_gap.get("family")}
    for k in ("lev_delta_20", "abs_lev_delta_20"):
        if k in lev_panels:
            panels[k] = lev_panels[k]
    del lev_panels, mask; gc.collect()
    peak = max(peak, mem_mb())
    load_meta["l1h_attach"] = l1h_meta
    load_meta["dropped_ann_panels"] = dropped_ann
    load_meta["excluded_leaves_policy"] = list(EXCLUDED_LEAVES)

    sp = {k: panels[k] for k in SEARCH_LEAVES if k in panels}
    missing = [k for k in SEARCH_LEAVES if k not in panels]
    dropped_nan = []
    for k in list(sp.keys()):
        if sp[k].notna().sum().sum() == 0:
            dropped_nan.append(k); del sp[k]
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
        structural_only=False, ban_textbook=True, use_l1b_fitness=True,  # v5b: allow L1h leaves outside STRUCTURAL_LEAF_FEATURES
        public_panels=public, lambda_complexity=0.015, lambda_turnover=1.0, top_n=50,
    )
    (OUT / "run_meta.json").write_text(json.dumps({
        "promotion_approved": False, "sealed": False, "window": WINDOW,
        "max_evaluations": MAX_EVAL, "population": POP, "generations": GEN, "seed": SEED,
        "search_leaves": sorted(sp.keys()), "missing_leaves": missing,
        "dropped_nan_leaves": dropped_nan, "leaf_diag": leaf_diag,
        "excluded_leaves": list(EXCLUDED_LEAVES),
        "dropped_ann_panels": dropped_ann,
        "hard_gates": ["icir>0", f"nonempty>={COV_NONEMPTY_MIN}", "ann_net>0",
                       "novelty_|corr|<=0.5", "ban_textbook", "structural_only",
                       f"post_impact+flat25@60&100万>={IMP60_FLOOR}",
                       "no_ann_primary", "isomorphic_demote_vs_v2e+"],
        "capital_cny": [600000, 1000000], "ledger_N_before": n_before,
        "leo_explore_ok": True, "load_meta": load_meta,
        "parent_script": "ai_factor_gp_reopen_hardgate_v4_cross_l1h.py",
        "enhancement": "v5 FORCED mul/sub/div L1h×struct binary cross; reject sole-leaf ts stacks; ban ann/lockup/level shells",
    }, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    log("gp_search start", "N_before", n_before, "n_leaves", len(sp))
    res = gp_search(sp, label, cfg)
    peak = max(peak, mem_mb())
    log("gp done evals", res.evaluations, "top_k", len(res.top_k), "peak", peak)

    run_rows = [json.loads(x) for x in run_ledger.read_text().splitlines() if x.strip()] if run_ledger.exists() else []
    for r in run_rows:
        append_attempt(engine=r["engine"], seed=r["seed"], universe=r["universe"], cost=r["cost"],
                       window=r["window"], expr_str=r.get("expr_str", ""), fitness=r.get("fitness"),
                       notes=(r.get("notes") or "") + ";gp_reopen_hardgate_v5b_struct_fix", path=main_ledger)
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
            broadcast_only = expr.strip() in (
                "lu_promote_rate", "rank(lu_promote_rate)", "neg(lu_promote_rate)",
                "mkt_max_height", "mkt_lu_breadth", "rank(mkt_lu_breadth)",
            )
            iso = isomorphic_reason(expr)
            verdict = "GATE_OK"
            if rank_fill: verdict = "FAIL_RANK_FILL"
            elif broadcast_only: verdict = "DEMOTE_BROADCAST"
            elif iso: verdict = f"DEMOTE_ISO_{iso}"
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
                "isomorphic_reason": iso, "leaves": sorted(leaves_in(expr)),
                "verdict": verdict,
                "gate_ok": verdict == "GATE_OK", "promotion_approved": False,
                "diagnostic_overlay_candidate": verdict == "GATE_OK",
                "capital_cny_tiers": [600000, 1000000],
            }
            all_rows.append(row)
            if verdict == "GATE_OK": gate_ok.append(row)
            elif verdict.startswith("DEMOTE"): demoted.append(row)
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
        "policy": "v5b_struct_off + forced_cross + ban_sole_leaf_ts + ban_ann_lockup_level",
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
            "leaves": r.get("leaves"),
            "nonempty_rate": (r.get("coverage") or {}).get("nonempty_rate"),
            "flat25": (r.get("metrics") or {}).get("flat25"),
            "imp60_p25": (r.get("metrics") or {}).get("imp60_p25"),
            "imp100_p25": (r.get("metrics") or {}).get("imp100_p25"),
            "icir": (r.get("metrics") or {}).get("icir"),
            "rank_fill_cov": r.get("rank_fill_cov"),
            "max_abs_public_corr": r.get("max_abs_public_corr"),
            "verdict": r["verdict"],
            "diagnostic_overlay_candidate": True,
            "note": "v5_forced_cross; Alpha adjudicates v2e++/v2f",
        } for r in gate_ok],
        "n_gate_ok": len(gate_ok),
        "n_demote": len(demoted),
        "demote_iso": [r["expr"] for r in demoted if str(r.get("verdict","")).startswith("DEMOTE_ISO")],
        "search_leaves": sorted(sp.keys()),
        "excluded_leaves": list(EXCLUDED_LEAVES),
        "ledger_N_before": n_before, "ledger_N_after": n_after,
        "source": "gp_reopen_hardgate_v5b_struct_fix",
        "dedup_note": "Dedup vs v2e+/v2e++; FORCED L1h×struct mul/sub/div; ban sole-leaf ts / ann / lockup / level shells",
        "note": "empty gate_ok is valid; Alpha adjudicates only GATE_OK rows",
    }
    (OUT / "alpha_handback_package.json").write_text(
        json.dumps(clean(handback), indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "summary.json").write_text(json.dumps(clean(summary), indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# AI 因子 GP 硬闸重开 v5（强制 mul/sub/div 二元交叉 L1h×结构 · 禁 sole-leaf ts · explore）",
        "",
        f"- **时间：** 2026-10-12（America/New_York）",
        f"- **promotion_approved：** false；**密封：** 未开；**不交 Strategy 权重**",
        f"- **窗口：** {WINDOW}；宇宙：中大盘 top1500 / 沪深300∪中证500；本金 60万/100万",
        f"- 账本：N {n_before} → {n_after}（+{n_after-n_before}）",
        f"- GP：evals={res.evaluations}/{MAX_EVAL}；Top-K={len(res.top_k)}；seed={SEED}；峰值 RSS≈{peak:.0f}MB",
        f"- 叶空间：{len(sp)} 叶（强制 mul/sub/div 二元：L1h×结构；禁 sole-leaf ts_* / ann_* / lockup；未重跑 L1h 批）",
        f"- 搜索叶：{', '.join(f'`{k}`' for k in sorted(sp.keys()))}",
        f"- 缺失叶：{missing or '无'}；全 NaN 丢弃：{dropped_nan or '无'}",
        f"- 政策排除：{', '.join(f'`{k}`' for k in EXCLUDED_LEAVES)}",
        f"- 硬闸烘焙：ICIR>0 · nonempty≥{COV_NONEMPTY_MIN:.0%} · ann_net>0 · |corr|教科书≤0.5 · ban_textbook · structural_only=False(允许L1h叶) · 同构降级",
        f"- 事后冲击闸：flat25>0 且 冲击+25bp@60万∧100万≥{IMP60_FLOOR:.0%}",
        f"- 增强：非 ann 池 + `l1h.build_{{liq,idx,lev}}_panels` 选叶（仅 delta/CV）",
        "",
        "## 与已收录去重",
        "",
        "- 精确匹配 v2e / v2e+ / `neg(idx_w500_delta_20)` → DEMOTE_ISO",
        "- 叶集=`{overnight_ret, lu_height}` 且 sub+ts_mean/ts_max → 视为与 v2e+ 主 overlay 同构",
        "- 任意 `ann_*` 叶 → ANN_PRIMARY_BANNED（本轮搜索池已剔除）",
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
        f"- DEMOTE（教科书/广播/同构）：{len(demoted)}；其余见 `post_gate_rows.json`",
        "- 回传包：`output/ai_factor/gp_reopen_hardgate_v5b_struct_fix/alpha_handback_package.json`",
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
        f"- JSON：`output/ai_factor/gp_reopen_hardgate_v5b_struct_fix/`",
        f"- 账本：`output/ai_factor/ledger.jsonl` N={n_after}",
        "",
        "## 禁令自检",
        "- promotion_approved=false；未开密封；未改短清单；未重跑 L1h 批；未改 HANDOFF/PARTICIPATION",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    log("DONE", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if peak < MEM_CAP_MB else 1

if __name__ == "__main__":
    raise SystemExit(main())
