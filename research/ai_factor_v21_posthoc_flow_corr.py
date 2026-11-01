#!/usr/bin/env python3
"""Post-hoc v21: append contemporaneous flow |corr| diagnostics + near-duplicate clusters.
Does NOT relaunch GP. Diagnostic only — NOT gates. promotion=false.
"""
from __future__ import annotations

import gc
import importlib.util
import json
import math
import resource
import sys
import types
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/workspace/QuantLab")
OUT = ROOT / "output/ai_factor/gp_reopen_hardgate_v21_etf_timing_ret"
V21 = ROOT / "research/ai_factor_gp_reopen_hardgate_v21_etf_timing_ret.py"

# near-duplicate thresholds (signal-signal |corr| and ICIR proximity)
SIG_CORR_CLUSTER = 0.90
ICIR_TIE_EPS = 1e-4


def mem_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def clean(o):
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(x) for x in o]
    if isinstance(o, (np.bool_, bool)):
        return bool(o)
    if isinstance(o, (np.floating, float)):
        x = float(o)
        return None if not math.isfinite(x) else x
    if isinstance(o, (np.integer, int)):
        return int(o)
    if isinstance(o, pd.Timestamp):
        return str(o)
    return o


def load_v21():
    spec = importlib.util.spec_from_file_location("v21mod", V21)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    # prevent main() side effects — only import defs
    sys.modules["v21mod"] = mod
    # stub env so accidental main wouldn't run; we never call main
    spec.loader.exec_module(mod)
    return mod


def ensure_ops():
    if "quantlab" not in sys.modules:
        q = types.ModuleType("quantlab")
        q.__path__ = [str(ROOT / "quantlab")]
        sys.modules["quantlab"] = q
    if "quantlab.factors" not in sys.modules or not hasattr(sys.modules["quantlab.factors"], "__path__"):
        f = types.ModuleType("quantlab.factors")
        f.__path__ = [str(ROOT / "quantlab/factors")]
        sys.modules["quantlab.factors"] = f
    if "quantlab.factors.ops" not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            "quantlab.factors.ops", ROOT / "quantlab/factors/ops.py"
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules["quantlab.factors.ops"] = mod
        assert spec.loader
        spec.loader.exec_module(mod)
    return sys.modules["quantlab.factors.ops"]



def parse_expr_str(s: str, Expr):
    """Parse Expr.to_str() form: op(a, b) / leaf_name."""
    s = s.strip()

    def parse_at(i: int):
        # skip spaces
        while i < len(s) and s[i].isspace():
            i += 1
        start = i
        while i < len(s) and (s[i].isalnum() or s[i] == "_"):
            i += 1
        name = s[start:i]
        if not name:
            raise ValueError(f"empty name at {i} in {s!r}")
        while i < len(s) and s[i].isspace():
            i += 1
        if i < len(s) and s[i] == "(":
            i += 1  # skip (
            kids = []
            while True:
                while i < len(s) and s[i].isspace():
                    i += 1
                if i < len(s) and s[i] == ")":
                    i += 1
                    break
                kid, i = parse_at(i)
                kids.append(kid)
                while i < len(s) and s[i].isspace():
                    i += 1
                if i < len(s) and s[i] == ",":
                    i += 1
                    continue
                if i < len(s) and s[i] == ")":
                    i += 1
                    break
                raise ValueError(f"expected , or ) at {i} in {s!r}")
            return Expr("op", name, tuple(kids)), i
        return Expr("leaf", name), i

    node, j = parse_at(0)
    while j < len(s) and s[j].isspace():
        j += 1
    if j != len(s):
        raise ValueError(f"trailing junk at {j}: {s[j:]!r}")
    return node


def panel_flat_abs_corr(a: pd.DataFrame, b: pd.DataFrame) -> float:
    """Contemporaneous panel-aligned |Pearson| on finite cells (same index/cols)."""
    aa = a.reindex_like(b).to_numpy(dtype=np.float64).ravel()
    bb = b.to_numpy(dtype=np.float64).ravel()
    m = np.isfinite(aa) & np.isfinite(bb)
    if m.sum() < 50:
        return float("nan")
    x, y = aa[m], bb[m]
    if x.std() < 1e-12 or y.std() < 1e-12:
        return float("nan")
    return abs(float(np.corrcoef(x, y)[0, 1]))


def union_find_cluster(n: int, edges: list[tuple[int, int]]) -> list[list[int]]:
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[rj] = ri

    for i, j in edges:
        union(i, j)
    groups: dict[int, list[int]] = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    return [sorted(v) for v in groups.values()]


def main() -> int:
    print(f"[posthoc] start rss={mem_mb():.0f}MB", flush=True)
    cands_path = OUT / "candidates.json"
    pkg_path = OUT / "beta_etf_timing_ret_package.json"
    note_path = OUT / "BETA_NOTE_ZH.md"
    report_path = OUT / "REPORT_NOTE_ZH.md"

    candidates = json.loads(cands_path.read_text(encoding="utf-8"))
    pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
    assert len(candidates) == 18, f"expected 18 pass, got {len(candidates)}"

    # Confirm gates already in package
    gates = pkg.get("gates") or {}
    gate_confirm = {
        "icir_fwd1d_gt_0_in_gates": bool(gates.get("icir_fwd1d_gt_0")),
        "after_cost_icir_gt_0_in_gates": bool(gates.get("after_cost_icir_gt_0")),
        "impact_cny": gates.get("impact_cny"),
        "all_pass_have_icir1_gt_0": all(
            (r.get("icir_fwd1d_excess_510300") or -1) > 0 for r in candidates
        ),
        "all_pass_have_after_cost_gt_0": all(
            (r.get("icir_fwd1d_after_cost") or -1) > 0 for r in candidates
        ),
        "all_pass_impact_60_and_100": all(
            bool((r.get("impact") or {}).get("pass_impact_60_and_100")) for r in candidates
        ),
    }
    print("[posthoc] gate_confirm", json.dumps(gate_confirm), flush=True)

    v21 = load_v21()
    ops = ensure_ops()
    apply_expr = ops.apply_expr

    # Rebuild lean panels (same window as v21)
    ind_ret, amt, ind_meta = v21.load_industry_etf_ret()
    print(f"[posthoc] ind_ret {ind_ret.shape} rss={mem_mb():.0f}MB ok={ind_meta.get('ok')}", flush=True)
    panels, flow_meta = v21.load_flow_panels(ind_ret.columns, ind_ret.index)
    print(f"[posthoc] flow wired={flow_meta.get('wired')} rss={mem_mb():.0f}MB", flush=True)

    if "ind_etf_share_flow" not in panels or "etf_all_flow" not in panels:
        raise SystemExit(f"missing flow panels for diagnostic: {list(panels.keys())}")

    flow_ind = panels["ind_etf_share_flow"].astype("float32")
    flow_all = panels["etf_all_flow"].astype("float32")

    facs: list[pd.DataFrame] = []
    for i, row in enumerate(candidates):
        expr = parse_expr_str(row["expr"], ops.Expr)
        fac = apply_expr(expr, panels).astype("float32")
        c_ind = panel_flat_abs_corr(fac, flow_ind)
        c_all = panel_flat_abs_corr(fac, flow_all)
        row["corr_abs_vs_contemporaneous_ind_etf_share_flow"] = c_ind
        row["corr_abs_vs_contemporaneous_etf_all_flow"] = c_all
        row["corr_flow_is_diagnostic_only"] = True
        facs.append(fac)
        print(
            f"[posthoc] #{i+1} |corr_ind|={c_ind:.4f} |corr_all|={c_all:.4f}  {row['expr'][:70]}",
            flush=True,
        )
        if mem_mb() > 2000:
            print(f"[posthoc] WARN rss={mem_mb():.0f}", flush=True)

    n = len(candidates)
    # pairwise signal |corr|
    pair_corr = np.eye(n, dtype=np.float64)
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            c = panel_flat_abs_corr(facs[i], facs[j])
            pair_corr[i, j] = pair_corr[j, i] = c if math.isfinite(c) else 0.0
            if math.isfinite(c) and c >= SIG_CORR_CLUSTER:
                edges.append((i, j))

    clusters = union_find_cluster(n, edges)
    # ICIR near-tie groups (by rounded ICIR)
    icirs = [float(r.get("icir_fwd1d_excess_510300") or float("nan")) for r in candidates]
    tie_groups: dict[str, list[int]] = {}
    for i, ic in enumerate(icirs):
        if not math.isfinite(ic):
            continue
        key = f"{round(ic / ICIR_TIE_EPS) * ICIR_TIE_EPS:.6f}"
        tie_groups.setdefault(key, []).append(i)
    icir_tie_groups = [
        {"icir_approx": float(k), "member_ranks_1based": [i + 1 for i in idxs], "exprs": [candidates[i]["expr"] for i in idxs]}
        for k, idxs in sorted(tie_groups.items(), key=lambda kv: -float(kv[0]))
        if len(idxs) >= 2
    ]

    cluster_summaries = []
    recommended_reps = []
    for ci, members in enumerate(sorted(clusters, key=lambda m: min(m)), 1):
        # representative = highest ICIR in cluster
        best = max(members, key=lambda i: icirs[i] if math.isfinite(icirs[i]) else -1e9)
        # max pairwise corr within cluster
        max_pc = 0.0
        for a in members:
            for b in members:
                if a < b:
                    max_pc = max(max_pc, float(pair_corr[a, b]))
        summary = {
            "cluster_id": ci,
            "size": len(members),
            "member_ranks_1based": [i + 1 for i in members],
            "exprs": [candidates[i]["expr"] for i in members],
            "icir_1d": [icirs[i] for i in members],
            "max_pairwise_abs_corr": max_pc if len(members) > 1 else 1.0,
            "representative_rank_1based": best + 1,
            "representative_expr": candidates[best]["expr"],
            "near_duplicate": len(members) > 1,
        }
        cluster_summaries.append(summary)
        recommended_reps.append(
            {
                "cluster_id": ci,
                "rank_1based": best + 1,
                "expr": candidates[best]["expr"],
                "icir_fwd1d_excess_510300": icirs[best],
                "corr_abs_vs_contemporaneous_ind_etf_share_flow": candidates[best][
                    "corr_abs_vs_contemporaneous_ind_etf_share_flow"
                ],
                "corr_abs_vs_contemporaneous_etf_all_flow": candidates[best][
                    "corr_abs_vs_contemporaneous_etf_all_flow"
                ],
            }
        )
        # annotate each candidate
        for i in members:
            candidates[i]["near_duplicate_cluster_id"] = ci
            candidates[i]["near_duplicate_cluster_size"] = len(members)
            candidates[i]["is_cluster_representative"] = i == best
            candidates[i]["cluster_representative_expr"] = candidates[best]["expr"]

    # free factor panels
    del facs
    gc.collect()

    diagnostic_block = {
        "corr_flow_is_diagnostic_only": True,
        "NOT_a_gate": True,
        "method": "panel_flat_pearson_abs_corr_finite_cells_aligned_index_cols",
        "vs_panels": ["ind_etf_share_flow", "etf_all_flow"],
        "contemporaneous": True,
        "note_zh": "信号与同期份额流 |corr| 仅诊断；不过闸。Beta 已 reject v20 flow-continuation（真收益差、流自相关虚高）。v21 y=行业ETF未来超额收益 vs 510300。",
        "v20_beta_rejected": True,
        "v20_reject_reason": "true_return_X1_Sharpe≈-0.5; flow_autocorr≈0.41 inflated ICIR",
        "v21_label": "fwd_1d_aum_weighted_sw_l1_etf_excess_return_vs_510300",
        "near_duplicate": {
            "signal_abs_corr_threshold": SIG_CORR_CLUSTER,
            "icir_tie_eps": ICIR_TIE_EPS,
            "n_clusters": len(cluster_summaries),
            "n_clusters_with_duplicates": sum(1 for c in cluster_summaries if c["near_duplicate"]),
            "clusters": cluster_summaries,
            "icir_tie_groups": icir_tie_groups,
            "beta_recommended_one_per_cluster": recommended_reps,
            "advice_zh": "若干 top 表达式 ICIR 几乎相同且信号高相关——视为重复信号簇；建议 Beta 每簇只取代表（is_cluster_representative=true）。",
        },
        "gate_confirm": gate_confirm,
        "flow_meta": flow_meta,
        "posthoc_peak_rss_MB": round(mem_mb()),
    }

    # Update candidates.json
    cands_path.write_text(json.dumps(clean(candidates), indent=2, ensure_ascii=False), encoding="utf-8")

    # Update package: replace candidates, add diagnostic section
    pkg["candidates"] = candidates[:25]
    pkg["n_candidates_pass"] = len(candidates)
    pkg["flow_corr_diagnostic"] = diagnostic_block
    pkg["near_duplicate_clusters"] = cluster_summaries
    pkg["beta_recommended_representatives"] = recommended_reps
    pkg["note"] = (
        "Hand QuantLab Beta only; do NOT submit to Alpha shortlist; promotion_approved=false; no Strategy. "
        "Beta rejected v20 flow-continuation; v21 y=excess return vs 510300; "
        "contemporaneous flow |corr| appended as DIAGNOSTIC ONLY (not a gate). "
        "Near-duplicate clusters marked — take one representative per cluster."
    )
    pkg["v20_beta_rejected_flow_continuation"] = True
    pkg["v21_y_is_excess_not_flow"] = True
    pkg_path.write_text(json.dumps(clean(pkg), indent=2, ensure_ascii=False), encoding="utf-8")

    # Update notes
    lines = [
        "# v21 Track B — ETF timing 收益化（交 Beta，不进 Alpha 短名单）",
        "",
        f"- sleeve=`etf_timing_ret`；evals=120；pass=18；GP peak≈927MB；posthoc rss≈{round(mem_mb())}MB",
        f"- 叶子（X，仅特征）：{sorted(panels.keys())}",
        "- **标签 y（非 flow）**：申万一级行业 ETF（AUM 加权）相对 **510300** 的未来 1 日超额（主闸）/ 5 日超额和（副报）",
        "- **硬闸已确认**：ICIR(价格超额 1d)>0；成本后 ICIR>0（25bp）；冲击@60万∧100万；禁 CB/金",
        "- **Beta 已 reject v20**：flow-continuation 标签虚高（流自相关≈0.41，真收益 X1 Sharpe≈−0.5）。本轮 y=超额收益，不是 flow。",
        "- **同期 flow |corr| 仅为诊断字段**（`corr_flow_is_diagnostic_only=true`），**不过闸**。",
        "- **近重复簇**：信号两两 |corr|≥0.90 聚为一簇；建议 Beta **每簇只取代表**（`is_cluster_representative`）。",
        "- **不交 Alpha 短名单**；Track A 暂停；promotion_approved=false；不交 Strategy；未开密封",
        f"- 包：`{OUT.relative_to(ROOT)}/beta_etf_timing_ret_package.json`",
        "",
        "## 过闸候选 + flow corr 诊断",
        "",
        "| # | 表达式 | ICIR_1d | after_cost | |corr|vs ind_flow | |corr|vs etf_all | 簇 | 代表? |",
        "|---|---|---:|---:|---:|---:|:---:|:---:|",
    ]
    for i, r in enumerate(candidates, 1):
        lines.append(
            f"| {i} | `{r['expr']}` | {r.get('icir_fwd1d_excess_510300'):.4f} | "
            f"{r.get('icir_fwd1d_after_cost'):.4f} | "
            f"{r.get('corr_abs_vs_contemporaneous_ind_etf_share_flow'):.4f} | "
            f"{r.get('corr_abs_vs_contemporaneous_etf_all_flow'):.4f} | "
            f"C{r.get('near_duplicate_cluster_id')} | "
            f"{'Y' if r.get('is_cluster_representative') else ''} |"
        )
    lines += ["", "## 近重复簇 / ICIR 并列（建议每簇一只）", ""]
    for c in cluster_summaries:
        if c["near_duplicate"]:
            lines.append(
                f"- **簇 C{c['cluster_id']}** size={c['size']} max|corr|={c['max_pairwise_abs_corr']:.4f} "
                f"→ 代表 #{c['representative_rank_1based']} `{c['representative_expr']}`"
            )
            for rk, ex, ic in zip(c["member_ranks_1based"], c["exprs"], c["icir_1d"]):
                mark = " ←REP" if rk == c["representative_rank_1based"] else ""
                lines.append(f"  - #{rk} ICIR={ic:.6f} `{ex}`{mark}")
    if icir_tie_groups:
        lines += ["", "### ICIR 几乎相同（并列组）", ""]
        for g in icir_tie_groups:
            lines.append(f"- ICIR≈{g['icir_approx']:.6f} ranks={g['member_ranks_1based']}")
            for ex in g["exprs"]:
                lines.append(f"  - `{ex}`")
    lines += [
        "",
        f"- 推荐 Beta 代表数：{len(recommended_reps)} / 过闸 {len(candidates)}",
        f"- fail_top: ICIR1_LE_0×102（GP 原统计）",
        "",
    ]
    note_text = "\n".join(lines)
    note_path.write_text(note_text, encoding="utf-8")
    report_path.write_text(note_text, encoding="utf-8")

    # compact digest for parent
    digest = {
        "out_dir": str(OUT.relative_to(ROOT)),
        "paths": {
            "beta_package": str(pkg_path.relative_to(ROOT)),
            "candidates": str(cands_path.relative_to(ROOT)),
            "BETA_NOTE_ZH": str(note_path.relative_to(ROOT)),
            "label_definition": str((OUT / "label_definition.json").relative_to(ROOT)),
        },
        "gate_confirm": gate_confirm,
        "n_pass": len(candidates),
        "n_clusters": len(cluster_summaries),
        "n_dup_clusters": sum(1 for c in cluster_summaries if c["near_duplicate"]),
        "n_recommended_reps": len(recommended_reps),
        "top5_corr": [
            {
                "rank": i + 1,
                "expr": candidates[i]["expr"],
                "icir_1d": candidates[i]["icir_fwd1d_excess_510300"],
                "corr_abs_ind_etf_share_flow": candidates[i][
                    "corr_abs_vs_contemporaneous_ind_etf_share_flow"
                ],
                "corr_abs_etf_all_flow": candidates[i][
                    "corr_abs_vs_contemporaneous_etf_all_flow"
                ],
                "cluster": candidates[i]["near_duplicate_cluster_id"],
                "is_rep": candidates[i]["is_cluster_representative"],
            }
            for i in range(min(5, len(candidates)))
        ],
        "dup_clusters": [c for c in cluster_summaries if c["near_duplicate"]],
        "icir_tie_groups": icir_tie_groups,
        "recommended_reps": recommended_reps,
        "posthoc_rss_MB": round(mem_mb()),
        "promotion_approved": False,
        "for_alpha_shortlist": False,
        "for_beta": True,
    }
    digest_path = OUT / "posthoc_flow_corr_digest.json"
    digest_path.write_text(json.dumps(clean(digest), indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(clean(digest), indent=2, ensure_ascii=False))
    print(f"[posthoc] DONE rss={mem_mb():.0f}MB", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
