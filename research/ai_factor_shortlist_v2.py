#!/usr/bin/env python3
"""Shortlist v2: GATE_OK + deepen increment, honest coverage annotation.

Juxtapose:
  - rank(ts_std_10(ann_insider_dec_5))          # L1d GATE_OK
  - abs(ts_std_10(ts_delta_5(ann_insider_dec_5))) # deepen robust increment

promotion_approved=False. No sealed. No Strategy. title_only. Memory <2.5GB.
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
OUT_DIR = ROOT / "output/ai_factor/shortlist_v2"
REPORT = ROOT / "output/alpha/AI_FACTOR_SHORTLIST_V2_ZH.md"
PRIOR_SHORT = ROOT / "output/ai_factor/l1d_shortlist_coverage_impact/shortlist_annotated.json"
PRIOR_DEEP = ROOT / "output/ai_factor/l1d_shortlist_coverage_impact/ann_insider_dec_deepen/results.json"

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

V2_MEMBERS = [
    {
        "source": "L1d_GATE_OK",
        "role": "gate_ok",
        "expr": "rank(ts_std_10(ann_insider_dec_5))",
        "notes": "L1d coverage-pass GATE_OK; WF stable_enough_explore; title_only",
    },
    {
        "source": "L1d_deepen_increment",
        "role": "deepen_increment",
        "expr": "abs(ts_std_10(ts_delta_5(ann_insider_dec_5)))",
        "notes": "unique pure-structure deepen vs honest-3 (+0.9%@60万+25bp); title_only",
    },
]

t0 = 0.0


def mem_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def log(*a):
    print(f"[shortlist_v2 {time.time()-t0:5.0f}s {mem_mb():.0f}MB]", *a, flush=True)


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


def write_report(rows, meta):
    lines = []
    lines.append("# AI 因子短清单 v2（GATE_OK + 加深增量并列）")
    lines.append("")
    lines.append("- **时间：** 2026-10-12（America/New_York）")
    lines.append("- **promotion_approved：** false；**密封：** 未开；**不交 Strategy 权重**")
    lines.append("- **trial_kind：** explore_gate / process")
    lines.append("- **本金主口径：** 60 万 / 100 万；主裁决=冲击+flat25")
    lines.append("- **禁止：** 广播叶、跌停主候选、小盘、教科书主线、密封、编造公告正文、Strategy 权重")
    lines.append("- **公告：** title_only（`invented_body=false`）")
    lines.append(
        f"- 账本：N {meta.get('ledger_N_before')} → {meta.get('ledger_N_after')} "
        f"（+{meta.get('ledger_N_new')}，explore_gate）"
    )
    lines.append(
        f"- 峰值 RSS：{meta.get('peak_rss_MB'):.0f} MB（上限 {meta.get('mem_cap_MB')}；"
        f"under_cap={meta.get('under_mem_cap')}）；运行 {meta.get('runtime_s')}s"
    )
    lines.append(
        "- 上游：`AI_FACTOR_L1d_SHORTLIST_COVERAGE_IMPACT_ZH.md`；"
        "`AI_FACTOR_L1d_ANN_INSIDER_DEC_DEEPEN_ZH.md`"
    )
    lines.append("")
    lines.append("## 覆盖率门槛（与 L1d 对齐）")
    lines.append("")
    lines.append("| 指标 | 门槛 |")
    lines.append("|---|---:|")
    lines.append("| nonempty_rate | ≥ 8% |")
    lines.append("| mean_event_names | ≥ 40 |")
    lines.append("| frac_days≥20 | ≥ 50% |")
    lines.append("| Top-N event share | 标注（不做硬闸） |")
    lines.append("")
    lines.append("## 短清单 v2 成员（并列）")
    lines.append("")
    lines.append(
        "| # | 来源 | role | 表达式 | flat25 | 60万+25bp | 100万+25bp | ICIR | 换手 | "
        "nonempty | 日均事件股 | TopN事件占比 | 覆盖 | 裁决 |"
    )
    lines.append("|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|")
    for i, r in enumerate(rows, 1):
        m = r.get("metrics") or {}
        cov = r.get("coverage") or {}
        top = r.get("topn_share") or {}
        lines.append(
            f"| {i} | {r.get('source')} | {r.get('role')} | `{r.get('expr')}` | "
            f"{fmt_pct(m.get('flat25'))} | {fmt_pct(m.get('imp60_p25'))} | "
            f"{fmt_pct(m.get('imp100_p25'))} | {fmt_f(m.get('icir'), 3)} | "
            f"{fmt_f(m.get('turn'), 3)} | {fmt_f(cov.get('nonempty_rate'), 4)} | "
            f"{fmt_f(cov.get('mean_event_names'), 1)} | "
            f"{fmt_pct(top.get('mean_topN_event_share'))} | "
            f"{'PASS' if cov.get('passes_coverage') else 'SPARSE_WARN'} | {r.get('verdict')} |"
        )
    lines.append("")
    lines.append("### 覆盖率明细 / 失败原因")
    lines.append("")
    for r in rows:
        cov = r.get("coverage") or {}
        top = r.get("topn_share") or {}
        status = "coverage-pass" if cov.get("passes_coverage") else "sparse-warned"
        fails = cov.get("fail_reasons") or []
        fail_s = ("；失败：" + ", ".join(fails)) if fails else ""
        lines.append(
            f"- `{r.get('expr')}` → **{status}**{fail_s}；"
            f"TopN事件占比={fmt_pct(top.get('mean_topN_event_share'))}"
        )
    lines.append("")
    lines.append("### 诚实注释")
    lines.append("")
    lines.append(
        "- **GATE_OK 核心：** `rank(ts_std_10(ann_insider_dec_5))` — rank 铺满截面，"
        "nonempty 口径≠事件密度；TopN 事件占比仍≈29%。"
    )
    lines.append(
        "- **加深增量：** `abs(ts_std_10(ts_delta_5(ann_insider_dec_5)))` — 相对 honest-3 "
        "唯一纯结构增量（Δ≈+0.9%@60万+25bp），但 **nonempty≈2% → sparse-warned**；"
        "不可当稳健密度，仅 explore 并列。"
    )
    lines.append(
        "- **size_resid 加深不入 v2：** ICIR 翻负，上游已明确不晋级。"
    )
    lines.append("- **不开密封、不交 Strategy**；`promotion_approved=false`。")
    lines.append("")
    lines.append("## 短清单 v2 总裁决")
    lines.append("")
    lines.append(
        f"1. **成员数：** {len(rows)}（GATE_OK + deepen_increment 并列）。"
    )
    lines.append(
        f"2. **覆盖率硬过闸：** {meta.get('n_coverage_pass')}/{len(rows)}；"
        f"冲击闸 GATE_OK={meta.get('n_gate_ok')}；"
        f"GATE_OK_SPARSE_WARN={meta.get('n_gate_ok_sparse')}。"
    )
    lines.append("3. **主候选仍仅 1 条 coverage-pass**；加深叶保留但标 sparse。")
    lines.append("4. **不开密封、不交 Strategy**；`promotion_approved=false`。")
    lines.append("")
    lines.append("## 产物路径")
    lines.append("")
    lines.append("- 报告：`output/alpha/AI_FACTOR_SHORTLIST_V2_ZH.md`")
    lines.append("- JSON：`output/ai_factor/shortlist_v2/`")
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

    log("loading panels")
    panels, label, public, load_meta = l1b.load_structural_panels()
    peak = max(peak, mem_mb())
    panels, label, public, load_meta = l1c.attach_l1c_panels(panels, label, public, load_meta)
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

    # need ann_insider_dec_5 only
    needed = {"ann_insider_dec_5"}
    if "ann_insider_dec_5" not in panels:
        win_panels, win_gap = sci.build_insider_window_panels(panels, cal, cols, mask)
        panels.update(win_panels)
        del win_panels
        gc.collect()
    else:
        win_gap = {"ok": True, "note": "ann_insider_dec_5 already in panels"}

    for k in list(panels.keys()):
        if k not in needed:
            del panels[k]
    gc.collect()
    log("trimmed", sorted(panels.keys()), "peak", peak)

    cols = list(next(iter(panels.values())).columns)
    cal = next(iter(panels.values())).index
    sig, adv = sci.load_sig_adv(cols, cal)
    peak = max(peak, mem_mb())
    size_panel = None
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
    for i, mem in enumerate(V2_MEMBERS):
        expr = mem["expr"]
        try:
            ev = sci.evaluate_token(
                expr, panels, label, sig, adv, size_panel, ind_codes, need_top=True
            )
        except Exception as exc:  # noqa: BLE001
            ev = {
                "expr": expr,
                "sim": {"error": f"{type(exc).__name__}: {exc}", "promotion_approved": False},
                "cs_stats": None,
                "coverage": None,
                "topn_share": None,
            }
        m = sci.pack_metrics(ev.get("sim"))
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
        elif not survive_cov:
            verdict = "FAIL_SPARSE"
        else:
            verdict = "FAIL_GATE"
        row = {
            **mem,
            "metrics": m,
            "coverage": cov,
            "topn_share": ev.get("topn_share"),
            "cs_stats": ev.get("cs_stats"),
            "survive_coverage": survive_cov,
            "gate_ok": gate_ok,
            "verdict": verdict,
            "promotion_approved": False,
            "trial_kind": "explore_gate",
            "on_shortlist_v2": True,
        }
        rows.append(row)
        fit = m.get("imp60_p25")
        notes = (
            f"shortlist_v2;role={mem['role']};verdict={verdict};"
            f"cov_pass={survive_cov};process_not_sealed;promotion_approved=false"
        )
        for path in (run_ledger, main_ledger):
            append_attempt(
                engine="shortlist_v2",
                seed=SEED,
                universe="midlarge_top1500_or_csi300_500",
                cost=0.0025,
                window="explore_20240603_to_latest_shortlist_v2",
                expr_str=expr,
                fitness=fit if isinstance(fit, float) and math.isfinite(fit) else None,
                notes=notes,
                path=path,
            )
        peak = max(peak, mem_mb())
        log(
            f"v2 {i+1}/{len(V2_MEMBERS)}",
            expr[:55],
            verdict,
            "60+25",
            fmt_pct(fit),
            "cov",
            survive_cov,
            "peak",
            peak,
        )

    n_after = (
        sum(1 for x in main_ledger.read_text().splitlines() if x.strip())
        if main_ledger.exists()
        else 0
    )
    peak = max(peak, mem_mb())
    meta = {
        "mode": "shortlist_v2_gate_ok_plus_deepen",
        "promotion_approved": False,
        "sealed_executed": False,
        "trial_kind": "explore_gate",
        "ann_title_only": True,
        "invented_body": False,
        "n_members": len(rows),
        "n_coverage_pass": sum(1 for r in rows if r.get("survive_coverage")),
        "n_gate_ok": sum(1 for r in rows if r.get("verdict") == "GATE_OK"),
        "n_gate_ok_sparse": sum(
            1 for r in rows if r.get("verdict") == "GATE_OK_SPARSE_WARN"
        ),
        "members": [
            {
                "expr": r["expr"],
                "role": r["role"],
                "verdict": r["verdict"],
                "imp60_p25": (r.get("metrics") or {}).get("imp60_p25"),
                "imp100_p25": (r.get("metrics") or {}).get("imp100_p25"),
                "flat25": (r.get("metrics") or {}).get("flat25"),
                "nonempty_rate": (r.get("coverage") or {}).get("nonempty_rate"),
                "passes_coverage": (r.get("coverage") or {}).get("passes_coverage"),
            }
            for r in rows
        ],
        "win_gap": win_gap,
        "ledger_N_before": n_before,
        "ledger_N_after": n_after,
        "ledger_N_new": n_after - n_before,
        "peak_rss_MB": peak,
        "mem_cap_MB": MEM_CAP_MB,
        "under_mem_cap": peak < MEM_CAP_MB,
        "runtime_s": round(time.time() - t0, 1),
        "prior_shortlist_path": str(PRIOR_SHORT),
        "prior_deepen_path": str(PRIOR_DEEP),
    }
    (OUT_DIR / "shortlist_v2.json").write_text(
        json.dumps(clean(rows), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "summary.json").write_text(
        json.dumps(clean(meta), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_report(rows, meta)
    log(
        "DONE",
        "GATE_OK",
        meta["n_gate_ok"],
        "SPARSE_WARN",
        meta["n_gate_ok_sparse"],
        "N",
        n_after,
        "peak",
        peak,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
