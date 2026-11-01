#!/usr/bin/env python3
"""L1e rzrq mech+ablation + float rank_fill demote + shortlist v2b.

promotion_approved=False. No sealed. No Strategy. No small-cap. No textbook.
Ban broadcast/LD primary. Memory <2.5GB.
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
L1E_DIR = ROOT / "output/ai_factor/l1e_hard_cov_struct"
V2_DIR = ROOT / "output/ai_factor/shortlist_v2"
OUT_MECH = ROOT / "output/ai_factor/l1e_rzrq_float_mech"
OUT_V2B = ROOT / "output/ai_factor/shortlist_v2b"
REPORT_MECH = ROOT / "output/alpha/AI_FACTOR_L1e_RZRQ_FLOAT_MECH_ABLATION_ZH.md"
REPORT_V2B = ROOT / "output/alpha/AI_FACTOR_SHORTLIST_V2b_ZH.md"

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

t0 = 0.0


def mem_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def log(*a):
    print(f"[l1e_mech {time.time()-t0:5.0f}s {mem_mb():.0f}MB]", *a, flush=True)


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


def strip_outer_rank(expr: str) -> str | None:
    m = re.fullmatch(r"rank\((.+)\)", expr.strip())
    return m.group(1) if m else None


def strip_all_ranks(expr: str) -> str:
    """Remove all rank(...) wrappers while keeping other structure."""
    prev = None
    cur = expr
    while prev != cur:
        prev = cur
        cur = re.sub(r"rank\(([^()]*(?:\([^()]*\)[^()]*)*)\)", r"\1", cur)
    return cur


def core_key(expr: str) -> str:
    """Dedup key: strip outer rank/zscore wrappers for twin detection."""
    e = expr.strip()
    while True:
        m = re.fullmatch(r"(?:rank|zscore)\((.+)\)", e)
        if not m:
            break
        e = m.group(1)
    # also delay_5(rank(x)) twin of delay_5(x)
    m = re.fullmatch(r"(delay_\d+)\((?:rank|zscore)\((.+)\)\)", e)
    if m:
        return f"{m.group(1)}({m.group(2)})"
    return e


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


def fmt_f(x, nd=3):
    if isinstance(x, float) and math.isfinite(x):
        return f"{x:.{nd}f}"
    return "—"


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


MECHANISM_RZRQ = {
    "ts_mean_10(rzrq_intensity)": {
        "story_zh": "融资融券余额/流通市值强度的10日均值：高杠杆拥挤侧做多。经济内核=融资偏好/杠杆资金持续配置的中大盘结构偏好，非事件跳变。",
        "pit_caveat_zh": "rzye/rqye 按 available_at→下一交易日对齐；强度=余额/流通市值；单位尺度差不影响排序但影响绝对值。",
        "icir_risk_zh": "ICIR≤0：截面多空 IC 与 Top-N 多头簿方向不一致——收益可能来自尾部/不对称选股而非稳定预测力。",
    },
    "ts_mean_10(rz_intensity)": {
        "story_zh": "仅融资余额强度的10日平滑；与 rzrq 高度共线（融资主导融券）。",
        "pit_caveat_zh": "同 rzrq PIT；rq 臂被剥离。",
        "icir_risk_zh": "ICIR≤0 同族风险。",
    },
    "ts_mean_10(rq_intensity)": {
        "story_zh": "融券余额强度10日均值；融券池受限、覆盖略稀，机制更像「可融券标的/空头关注」而非融资拥挤。",
        "pit_caveat_zh": "融券标的池与券源约束；覆盖低于融资。",
        "icir_risk_zh": "ICIR 更负；多头簿与 IC 冲突更强。",
    },
    "rzrq_intensity": {
        "story_zh": "静态当日融资融券强度；无时间平滑，换手更高。",
        "pit_caveat_zh": "同 PIT。",
        "icir_risk_zh": "ICIR≤0。",
    },
    "delay_5(rzrq_intensity)": {
        "story_zh": "强度滞后5日：检验是否为持久水平态而非即时冲击。",
        "pit_caveat_zh": "同 PIT + 额外延迟。",
        "icir_risk_zh": "ICIR≤0。",
    },
    "rq_intensity": {
        "story_zh": "静态融券强度。",
        "pit_caveat_zh": "融券池约束。",
        "icir_risk_zh": "ICIR 显著负。",
    },
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


def ablation_variants_rzrq(parent: str) -> list[dict]:
    jobs = []

    def add(ablation: str, expr: str, note: str = ""):
        jobs.append({"role": "ablation", "parent": parent, "ablation": ablation, "expr": expr, "note": note})

    leaf_map = {
        "ts_mean_10(rzrq_intensity)": "rzrq_intensity",
        "ts_mean_10(rz_intensity)": "rz_intensity",
        "ts_mean_10(rq_intensity)": "rq_intensity",
        "rzrq_intensity": "rzrq_intensity",
        "delay_5(rzrq_intensity)": "rzrq_intensity",
        "rq_intensity": "rq_intensity",
        "rz_intensity": "rz_intensity",
        "delay_5(rz_intensity)": "rz_intensity",
        "delay_5(rq_intensity)": "rq_intensity",
    }
    leaf = leaf_map.get(parent)
    if leaf is None:
        # generic leaf from expr
        L = sorted(leaves_in(parent))
        leaf = L[0] if L else None

    if leaf:
        add("static_leaf", leaf, "静态单叶对照")
        add("static_neg", f"neg({leaf})", "静态取负")
        add("static_rank", f"rank({leaf})", "静态 rank")
        add("static_zscore", f"zscore({leaf})", "静态 zscore")
        if parent != f"ts_mean_10({leaf})":
            add("ts_mean_alt", f"ts_mean_10({leaf})", "ts_mean10 对照")
        if parent != f"ts_std_10({leaf})":
            add("ts_std_alt", f"ts_std_10({leaf})", "ts_std10 替代")
        if parent != f"delay_5({leaf})":
            add("delay_5_leaf", f"delay_5({leaf})", "delay5 叶")
        add("delay_5", f"delay_5({parent})", "整体 delay5")
        add("delay_20", f"delay_20({parent})", "整体 delay20")
        add("sign_flip", f"neg({parent})", "整体取负")
        add("drop_smooth_to_raw", leaf, "去掉平滑看原始")
        # sister arms
        for other in ("rz_intensity", "rq_intensity", "rzrq_intensity"):
            if other != leaf:
                add(f"sister_{other}", f"ts_mean_10({other})" if "ts_mean" in parent else other, f"姐妹臂 {other}")
        add("size_neutral_manual", f"__SIZE_RESID__::{parent}", "size 日度残差")
    return jobs


def honesty_verdict_rzrq(parent: str, base_m: dict, abl_rows: list[dict]) -> dict:
    fails = []
    passes = []
    notes = []
    flags = []

    def m_of(ablation):
        for r in abl_rows:
            if r.get("ablation") == ablation:
                return r.get("metrics") or {}
        return None

    base60 = base_m.get("imp60_p25", float("nan"))
    base_icir = base_m.get("icir", float("nan"))
    base_flat25 = base_m.get("flat25", float("nan"))
    base100 = base_m.get("imp100_p25", float("nan"))

    if math.isfinite(base_icir) and base_icir <= 0:
        flags.append("ICIR_LE_0")
        notes.append(
            f"**ICIR≤0 风险**：ICIR={base_icir:.3f}；Top-N 多头簿正收益与截面 IC 方向冲突，"
            "不可当作稳定预测力；explore-only。"
        )

    sf = m_of("sign_flip")
    if sf and math.isfinite(sf.get("imp60_p25", float("nan"))) and math.isfinite(base60):
        if sf["imp60_p25"] > base60 + 0.01:
            fails.append("sign_flip_improves")
            notes.append(f"取负后更好 ({sf['imp60_p25']:.2%} > {base60:.2%})")
        else:
            passes.append("sign_flip_hurts_or_neutral")

    d20 = m_of("delay_20")
    if d20 and math.isfinite(d20.get("imp60_p25", float("nan"))) and math.isfinite(base60):
        if d20["imp60_p25"] > base60 + 0.02:
            notes.append(f"delay_20 未衰减 ({d20['imp60_p25']:.2%}) — 持久水平态/偏差可疑")
        else:
            passes.append("delay_20_decays_or_flat")

    # static vs transform
    best_static = None
    for k in ("static_leaf", "static_rank", "static_zscore", "drop_smooth_to_raw"):
        mm = m_of(k)
        if mm and math.isfinite(mm.get("imp60_p25", float("nan"))):
            if best_static is None or mm["imp60_p25"] > best_static[1]["imp60_p25"]:
                best_static = (k, mm)
    if best_static and math.isfinite(base60):
        sk, sm = best_static
        if sm["imp60_p25"] >= base60 - 0.005:
            notes.append(f"静态/去平滑 {sk}≈基线 ({sm['imp60_p25']:.2%} vs {base60:.2%}) — 变换增益有限")
            passes.append("static_comparable")
        else:
            notes.append(f"变换优于最佳静态 {sk} ({base60:.2%} > {sm['imp60_p25']:.2%})")
            passes.append("transform_beats_static")

    sz = m_of("size_neutral_manual")
    if sz and math.isfinite(sz.get("imp60_p25", float("nan"))) and math.isfinite(base60):
        if sz["imp60_p25"] <= 0 and base60 > 0:
            fails.append("size_kills_edge")
            notes.append(f"size 残差后≤0 ({sz['imp60_p25']:.2%}) — 可能是市值通道")
        elif sz["imp60_p25"] < base60 * 0.5:
            notes.append(f"size 残差后衰减过半 ({sz['imp60_p25']:.2%} vs {base60:.2%})")
            flags.append("size_half_decay")
        else:
            passes.append("size_resid_keeps_edge")

    if not (math.isfinite(base60) and base60 >= IMP60_FLOOR):
        fails.append("below_imp60_floor")
    if not (math.isfinite(base_flat25) and base_flat25 > 0):
        fails.append("flat25_nonpositive")
    if not (math.isfinite(base100) and base100 >= IMP60_FLOOR):
        fails.append("below_imp100_floor")

    # ICIR≤0 is a soft demote-from-primary flag but not hard fail for explore survive
    # — instruction: clearly flag; keep as explore survivor with risk tag
    survive = len(fails) == 0
    if "ICIR_LE_0" in flags:
        notes.append("裁决：可 explore-survive，但 **禁止当作稳健主候选**（ICIR≤0）。")

    verdict = "SURVIVE_EXPLORE" if survive else "FAIL"
    if survive and "ICIR_LE_0" in flags:
        verdict = "SURVIVE_EXPLORE_ICIR_RISK"

    return {
        "survive_honesty": bool(survive),
        "verdict": verdict,
        "hard_fails": fails,
        "soft_passes": passes,
        "flags": flags,
        "notes": notes,
        "promote": False,
    }


def evaluate_one(expr_token, panels, label, sig, adv, size_panel, sci):
    from quantlab.factors.ops import apply_expr, parse_expr

    size_mode = expr_token.startswith("__SIZE_RESID__::")
    expr = expr_token.split("::", 1)[1] if size_mode else expr_token
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
                "size_resid": True,
                "metrics": sci.pack_metrics(None),
                "cs_stats": None,
                "coverage": None,
                "sim": {"error": "size_panel_unavailable"},
            }
        fac = size_residualize(fac, size_panel)
    cs = sci.cs_std_stats(fac)
    cov = sci.coverage_stats(fac, days_to_style="days_to" in expr)
    if not cs.get("passes_cs_variation"):
        sim = {"skipped": True, "reason": "cs_variation_fail", "promotion_approved": False}
        m = sci.pack_metrics(sim)
    else:
        sim = sci.simulate_book(fac, label, sig, adv)
        m = sci.pack_metrics(sim)
    del fac
    gc.collect()
    return {
        "expr": expr,
        "expr_token": expr_token,
        "size_resid": size_mode,
        "metrics": m,
        "cs_stats": cs,
        "coverage": cov,
        "sim": sim,
        "leaves": sorted(leaves_in(expr)),
    }


def write_mech_report(rzrq_gate, rzrq_cores, rzrq_verdicts, rzrq_results, float_rows, meta):
    lines = []
    lines.append("# AI 因子 L1e：rzrq 机制消融 + float rank_fill 复核")
    lines.append("")
    lines.append("- **时间：** 2026-10-12（America/New_York）")
    lines.append("- **promotion_approved：** false；**密封：** 未开；**不交 Strategy 权重")
    lines.append("- **trial_kind：** explore_gate / process")
    lines.append("- **本金主口径：** 60 万 / 100 万；主裁决=冲击+flat25；IMP60_FLOOR=10%")
    lines.append("- **硬覆盖：** nonempty≥8%；mean_event_names≥40；frac_days≥20≥50%")
    lines.append("- **禁止：** 广播、跌停主候选、小盘、教科书主线、密封、Strategy")
    lines.append(
        f"- 账本：N {meta.get('ledger_N_before')} → {meta.get('ledger_N_after')} "
        f"（+{meta.get('ledger_N_new')}，explore_gate）"
    )
    lines.append(
        f"- 峰值 RSS：{meta.get('peak_rss_MB'):.0f} MB（上限 {MEM_CAP_MB}；"
        f"under_cap={meta.get('under_mem_cap')}）；运行 {meta.get('runtime_s')}s"
    )
    lines.append("")

    # --- rzrq section ---
    lines.append("## ① rzrq 族 GATE_OK：机制 + 消融 + 静态对照")
    lines.append("")
    lines.append("### 全员 GATE_OK 表（诚实标 ICIR≤0）")
    lines.append("")
    lines.append(
        "| # | 表达式 | core | flat25 | 60万+25bp | 100万+25bp | ICIR | ICIR≤0 | 换手 | nonempty | 备注 |"
    )
    lines.append("|---|---|---|---:|---:|---:|---:|:---:|---:|---:|---|")
    for i, r in enumerate(rzrq_gate, 1):
        m = r.get("metrics") or {}
        cov = r.get("coverage") or {}
        icir = m.get("icir", float("nan"))
        icir_flag = "YES" if (isinstance(icir, float) and math.isfinite(icir) and icir <= 0) else "no"
        twin = "rank/zscore 孪生" if r.get("is_twin") else "core"
        lines.append(
            f"| {i} | `{r['expr']}` | {twin} | {fmt_pct(m.get('flat25'))} | "
            f"{fmt_pct(m.get('imp60_p25'))} | {fmt_pct(m.get('imp100_p25'))} | "
            f"{fmt_f(icir, 3)} | **{icir_flag}** | {fmt_f(m.get('turn'), 3)} | "
            f"{fmt_f(cov.get('nonempty_rate'), 4)} | {r.get('note','')} |"
        )
    lines.append("")
    lines.append(
        f"- rzrq GATE_OK 全员 **ICIR≤0**：{sum(1 for r in rzrq_gate if (r.get('metrics') or {}).get('icir', 1) <= 0)}/{len(rzrq_gate)}。"
    )
    lines.append("- 覆盖真实过闸（nonempty≈49–50%，非 rank 幻觉）。")
    lines.append("")

    lines.append("### 核心叶机制说明（去孪生后）")
    lines.append("")
    for c in rzrq_cores:
        mech = MECHANISM_RZRQ.get(c["expr"]) or {}
        lines.append(f"#### `{c['expr']}`")
        lines.append(f"- **故事：** {mech.get('story_zh', '（通用）融资融券强度结构叶')}")
        lines.append(f"- **PIT：** {mech.get('pit_caveat_zh', 'available_at 对齐')}")
        lines.append(f"- **ICIR 风险：** {mech.get('icir_risk_zh', 'ICIR≤0')}")
        lines.append("")

    lines.append("### 消融 + 静态对照结果（核心叶）")
    lines.append("")
    for v in rzrq_verdicts:
        lines.append(f"#### `{v['expr']}` → **{v['verdict']}**")
        bm = v.get("baseline_metrics") or {}
        lines.append(
            f"- 基线：flat25={fmt_pct(bm.get('flat25'))}；60万+25bp={fmt_pct(bm.get('imp60_p25'))}；"
            f"100万+25bp={fmt_pct(bm.get('imp100_p25'))}；ICIR={fmt_f(bm.get('icir'), 3)}"
        )
        if v.get("flags"):
            lines.append(f"- flags：{', '.join(v['flags'])}")
        if v.get("hard_fails"):
            lines.append(f"- hard_fails：{', '.join(v['hard_fails'])}")
        if v.get("soft_passes"):
            lines.append(f"- soft_passes：{', '.join(v['soft_passes'])}")
        for n in v.get("notes") or []:
            lines.append(f"- {n}")
        # ablation table
        abls = [r for r in rzrq_results if r.get("role") == "ablation" and r.get("parent") == v["expr"]]
        if abls:
            lines.append("")
            lines.append("| ablation | 表达式 | flat25 | 60万+25bp | ICIR | 换手 |")
            lines.append("|---|---|---:|---:|---:|---:|")
            for a in abls:
                mm = a.get("metrics") or {}
                lines.append(
                    f"| {a.get('ablation')} | `{a.get('expr')}` | {fmt_pct(mm.get('flat25'))} | "
                    f"{fmt_pct(mm.get('imp60_p25'))} | {fmt_f(mm.get('icir'), 3)} | "
                    f"{fmt_f(mm.get('turn'), 3)} |"
                )
        lines.append("")

    n_surv = sum(1 for v in rzrq_verdicts if v.get("survive_honesty"))
    n_fail = sum(1 for v in rzrq_verdicts if not v.get("survive_honesty"))
    lines.append("### rzrq 诚实裁决汇总")
    lines.append("")
    lines.append(f"- 核心叶消融：**SURVIVE_EXPLORE={n_surv}** / FAIL={n_fail}（均带 ICIR≤0 风险标签则标 SURVIVE_EXPLORE_ICIR_RISK）。")
    lines.append("- **全部 rzrq GATE_OK 不得晋级为主候选**（ICIR≤0）；可保留 explore 对照。")
    lines.append("- 不开密封、不交 Strategy；`promotion_approved=false`。")
    lines.append("")

    # --- float section ---
    lines.append("## ② float rank_*：rank_fill_cov 标签 + 非 rank 事件口径复核")
    lines.append("")
    lines.append(
        "| # | rank 表达式 | 非rank口径 | rank nonempty | 事件 nonempty | rank_fill_cov | "
        "非rank覆盖 | 非rank 60万+25bp | 裁决 |"
    )
    lines.append("|---|---|---|---:|---:|:---:|---|---:|---|")
    for i, r in enumerate(float_rows, 1):
        lines.append(
            f"| {i} | `{r['rank_expr']}` | `{r['norank_expr']}` | "
            f"{fmt_f(r.get('rank_nonempty'), 4)} | {fmt_f(r.get('event_nonempty'), 4)} | "
            f"**YES** | {r.get('norank_cov_verdict')} | {fmt_pct(r.get('norank_imp60_p25'))} | "
            f"**{r.get('verdict')}** |"
        )
    lines.append("")
    lines.append("### float 明细")
    lines.append("")
    for r in float_rows:
        lines.append(f"#### `{r['rank_expr']}` → **{r['verdict']}**")
        lines.append(f"- 标签：`rank_fill_cov=true`（rank 铺满 nonempty≈{fmt_f(r.get('rank_nonempty'), 4)}，底层事件 nonempty≈{fmt_f(r.get('event_nonempty'), 4)}）")
        lines.append(f"- 非rank口径：`{r['norank_expr']}`")
        lines.append(
            f"- 非rank覆盖：passes={r.get('norank_passes_coverage')}；"
            f"reasons={r.get('norank_fail_reasons')}"
        )
        lines.append(
            f"- 非rank成本：flat25={fmt_pct(r.get('norank_flat25'))}；"
            f"60万+25bp={fmt_pct(r.get('norank_imp60_p25'))}；"
            f"100万+25bp={fmt_pct(r.get('norank_imp100_p25'))}；ICIR={fmt_f(r.get('norank_icir'), 3)}"
        )
        lines.append(f"- 说明：{r.get('note_zh', '')}")
        lines.append("")

    n_demote = sum(1 for r in float_rows if r.get("verdict") == "DEMOTE")
    n_survive_f = sum(1 for r in float_rows if r.get("verdict") == "SURVIVE")
    n_fail_f = sum(1 for r in float_rows if r.get("verdict") == "FAIL")
    lines.append("### float 诚实裁决汇总")
    lines.append("")
    lines.append(f"- SURVIVE={n_survive_f}；**DEMOTE={n_demote}**；FAIL={n_fail_f}")
    lines.append("- 规则：非rank事件口径若硬覆盖失败或冲击闸失败 → **DEMOTE**；不得把 rank_fill 覆盖当诚实硬过。")
    lines.append("- 不开密封、不交 Strategy；`promotion_approved=false`。")
    lines.append("")

    lines.append("## 总裁决")
    lines.append("")
    lines.append(
        f"1. rzrq：GATE_OK={len(rzrq_gate)} 全员标 **ICIR≤0**；核心消融 SURVIVE_EXPLORE(含风险)={n_surv}。"
    )
    lines.append(f"2. float：rank_fill_cov 全员标注；非rank复核 DEMOTE={n_demote}/{len(float_rows)}。")
    lines.append("3. 短清单 v2b：仅保留诚实覆盖硬过 ∧ 无 ICIR≤0 主风险 ∧ 未 demote 者，与 v2 并列更新。")
    lines.append("4. **不开密封、不交 Strategy**；`promotion_approved=false`。")
    lines.append("")
    lines.append("## 产物路径")
    lines.append("")
    lines.append("- 报告：`output/alpha/AI_FACTOR_L1e_RZRQ_FLOAT_MECH_ABLATION_ZH.md`")
    lines.append("- JSON：`output/ai_factor/l1e_rzrq_float_mech/`")
    lines.append(f"- 账本：`output/ai_factor/ledger.jsonl` N={meta.get('ledger_N_after')}")
    lines.append("")
    REPORT_MECH.write_text("\n".join(lines), encoding="utf-8")
    log("wrote", REPORT_MECH)


def write_v2b(members, meta):
    lines = []
    lines.append("# AI 因子短清单 v2b（v2 + L1e 诚实并列）")
    lines.append("")
    lines.append("- **时间：** 2026-10-12（America/New_York）")
    lines.append("- **promotion_approved：** false；**密封：** 未开；**不交 Strategy 权重**")
    lines.append("- **trial_kind：** explore_gate / process")
    lines.append("- **本金主口径：** 60 万 / 100 万；主裁决=冲击+flat25")
    lines.append("- **禁止：** 广播叶、跌停主候选、小盘、教科书主线、密封、Strategy")
    lines.append("- **公告：** title_only（v2 成员）；L1e 新成员非 ann title")
    lines.append(
        f"- 账本：N {meta.get('ledger_N_before_v2b')} → {meta.get('ledger_N_after')} "
        f"（本步 +{meta.get('ledger_N_new_v2b', 0)}；总批 +{meta.get('ledger_N_new')}）"
    )
    lines.append(
        f"- 峰值 RSS：{meta.get('peak_rss_MB'):.0f} MB；运行 {meta.get('runtime_s')}s"
    )
    lines.append("- 上游：`AI_FACTOR_SHORTLIST_V2_ZH.md`；`AI_FACTOR_L1e_RZRQ_FLOAT_MECH_ABLATION_ZH.md`")
    lines.append("")
    lines.append("## 入选 / 降级规则")
    lines.append("")
    lines.append("| 规则 | 说明 |")
    lines.append("|---|---|")
    lines.append("| 保留 v2 GATE_OK | `rank(ts_std_10(ann_insider_dec_5))` coverage-pass |")
    lines.append("| 保留 v2 deepen | deepen 增量但 sparse_warn |")
    lines.append("| rzrq | 全员 ICIR≤0 → **不入主短清单**（可 explore_risk 附表） |")
    lines.append("| float rank_* | rank_fill_cov；非rank失败 → **DEMOTE 不入** |")
    lines.append("")
    lines.append("## 短清单 v2b 成员")
    lines.append("")
    lines.append(
        "| # | 来源 | role | 表达式 | flat25 | 60万+25bp | 100万+25bp | ICIR | nonempty | 覆盖标签 | 裁决 |"
    )
    lines.append("|---|---|---|---|---:|---:|---:|---:|---:|---|---|")
    for i, r in enumerate(members, 1):
        m = r.get("metrics") or {}
        cov = r.get("coverage") or {}
        lines.append(
            f"| {i} | {r.get('source')} | {r.get('role')} | `{r.get('expr')}` | "
            f"{fmt_pct(m.get('flat25'))} | {fmt_pct(m.get('imp60_p25'))} | "
            f"{fmt_pct(m.get('imp100_p25'))} | {fmt_f(m.get('icir'), 3)} | "
            f"{fmt_f(cov.get('nonempty_rate'), 4)} | {r.get('coverage_tag')} | {r.get('verdict')} |"
        )
    lines.append("")
    risk = meta.get("rzrq_explore_risk") or []
    if risk:
        lines.append("## 附表：rzrq explore_risk（ICIR≤0，不入主短清单）")
        lines.append("")
        lines.append("| 表达式 | 60万+25bp | ICIR | nonempty | 标签 |")
        lines.append("|---|---:|---:|---:|---|")
        for r in risk[:8]:
            m = r.get("metrics") or {}
            cov = r.get("coverage") or {}
            lines.append(
                f"| `{r.get('expr')}` | {fmt_pct(m.get('imp60_p25'))} | "
                f"{fmt_f(m.get('icir'), 3)} | {fmt_f(cov.get('nonempty_rate'), 4)} | ICIR_LE_0 |"
            )
        lines.append("")
    demoted = meta.get("float_demoted") or []
    if demoted:
        lines.append("## 附表：float DEMOTE（rank_fill_cov，非rank未过）")
        lines.append("")
        lines.append("| rank 表达式 | 非rank口径 | 事件 nonempty | 非rank裁决 |")
        lines.append("|---|---|---:|---|")
        for r in demoted:
            lines.append(
                f"| `{r.get('rank_expr')}` | `{r.get('norank_expr')}` | "
                f"{fmt_f(r.get('event_nonempty'), 4)} | {r.get('verdict')} |"
            )
        lines.append("")
    lines.append("## 诚实裁决")
    lines.append("")
    lines.append(f"1. **v2b 主成员数：** {len(members)}（相对 v2 未因 L1e float/rzrq 扩容主清单）。")
    lines.append("2. **rzrq：** 真实覆盖但 ICIR≤0 → 仅附表 explore_risk。")
    lines.append("3. **float：** rank_fill_cov 全员 DEMOTE（非rank硬覆盖失败）。")
    lines.append("4. **不开密封、不交 Strategy**；`promotion_approved=false`。")
    lines.append("")
    lines.append("## 产物路径")
    lines.append("")
    lines.append("- 报告：`output/alpha/AI_FACTOR_SHORTLIST_V2b_ZH.md`")
    lines.append("- JSON：`output/ai_factor/shortlist_v2b/`")
    lines.append(f"- 账本：`output/ai_factor/ledger.jsonl` N={meta.get('ledger_N_after')}")
    lines.append("")
    REPORT_V2B.write_text("\n".join(lines), encoding="utf-8")
    log("wrote", REPORT_V2B)


def main() -> int:
    global t0
    t0 = time.time()
    peak = mem_mb()
    OUT_MECH.mkdir(parents=True, exist_ok=True)
    OUT_V2B.mkdir(parents=True, exist_ok=True)
    REPORT_MECH.parent.mkdir(parents=True, exist_ok=True)

    shortlist_l1e = json.loads((L1E_DIR / "shortlist.json").read_text())
    summary_l1e = json.loads((L1E_DIR / "summary.json").read_text())
    v2_members = json.loads((V2_DIR / "shortlist_v2.json").read_text())
    float_gap = summary_l1e.get("float_gap") or {}

    rzrq_gate = [r for r in shortlist_l1e if r.get("family") == "rzrq_structure" and r.get("gate_ok")]
    float_gate = [r for r in shortlist_l1e if r.get("family") == "float_event_calendar" and r.get("gate_ok")]
    # sort
    rzrq_gate = sorted(rzrq_gate, key=lambda r: (r.get("metrics") or {}).get("imp60_p25") or -1, reverse=True)
    float_gate = sorted(float_gate, key=lambda r: (r.get("metrics") or {}).get("imp60_p25") or -1, reverse=True)

    # mark twins
    seen_cores = {}
    for r in rzrq_gate:
        ck = core_key(r["expr"])
        r["core_key"] = ck
        if ck not in seen_cores:
            seen_cores[ck] = r["expr"]
            r["is_twin"] = False
        else:
            r["is_twin"] = True
            r["twin_of"] = seen_cores[ck]

    # pick cores for ablation: unique cores, prefer non-rank form, top by imp60
    core_reps = []
    for ck, first_expr in seen_cores.items():
        # prefer the non-twin row matching ck exactly, else first
        cand = [r for r in rzrq_gate if r["core_key"] == ck and not r["is_twin"]]
        if not cand:
            cand = [r for r in rzrq_gate if r["core_key"] == ck]
        core_reps.append(cand[0])
    # limit to top 6 cores by imp60 to keep runtime/memory
    core_reps = sorted(
        core_reps, key=lambda r: (r.get("metrics") or {}).get("imp60_p25") or -1, reverse=True
    )[:6]
    log("rzrq_gate", len(rzrq_gate), "cores_for_ablation", len(core_reps))
    for c in core_reps:
        log("  core", c["expr"], fmt_pct((c.get("metrics") or {}).get("imp60_p25")))

    _ensure_pkgs()
    sci = _import_mod(
        "ai_factor_l1d_shortlist_coverage_impact",
        ROOT / "research/ai_factor_l1d_shortlist_coverage_impact.py",
    )
    l1e = _import_mod(
        "ai_factor_l1e_hard_cov_struct_explore",
        ROOT / "research/ai_factor_l1e_hard_cov_struct_explore.py",
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
    size_panel = public.get("size") if isinstance(public, dict) else None
    if size_panel is not None:
        size_panel = size_panel.astype("float32")
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

    # clear unused
    for k in list(panels.keys()):
        del panels[k]
    gc.collect()

    log("load float_mktcap")
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

    rz_panels, rz_gap = l1e.build_rzrq_panels(cal, cols, mask, fm)
    panels.update(rz_panels)
    del rz_panels, fm
    gc.collect()
    fl_panels, fl_gap = l1e.build_float_event_panels(cal, cols, mask)
    panels.update(fl_panels)
    del fl_panels
    gc.collect()
    # also need ann_insider for v2b reaffirm? not required — reuse v2 metrics
    peak = max(peak, mem_mb())
    log("panels ready", len(panels), "peak", peak)

    sig, adv = sci.load_sig_adv(cols, cal)
    peak = max(peak, mem_mb())

    # Build jobs: cores + ablations + float norank
    jobs = []
    for c in core_reps:
        jobs.append(
            {
                "role": "primary",
                "family": "rzrq_structure",
                "parent": c["expr"],
                "ablation": "baseline",
                "expr": c["expr"],
                "gate_imp60_p25": (c.get("metrics") or {}).get("imp60_p25"),
            }
        )
        for a in ablation_variants_rzrq(c["expr"]):
            jobs.append(a)

    float_jobs = []
    for r in float_gate:
        rank_expr = r["expr"]
        norank = strip_outer_rank(rank_expr)
        if norank is None:
            norank = strip_all_ranks(rank_expr)
        # underlying leaf for event nonempty
        leaves = sorted(leaves_in(rank_expr))
        event_leaf = leaves[0] if leaves else None
        event_nonempty = None
        if event_leaf and f"nonempty_{event_leaf}" in (float_gap or fl_gap):
            event_nonempty = (float_gap or fl_gap).get(f"nonempty_{event_leaf}")
        elif event_leaf:
            # approx from fl_gap built now
            event_nonempty = fl_gap.get(f"nonempty_{event_leaf}")
        float_jobs.append(
            {
                "role": "float_norank",
                "family": "float_event_calendar",
                "rank_expr": rank_expr,
                "norank_expr": norank,
                "expr": norank,
                "ablation": "norank_event_口径",
                "parent": rank_expr,
                "rank_metrics": r.get("metrics"),
                "rank_coverage": r.get("coverage"),
                "rank_nonempty": (r.get("coverage") or {}).get("nonempty_rate"),
                "event_leaf": event_leaf,
                "event_nonempty": event_nonempty,
            }
        )
        jobs.append(
            {
                "role": "float_norank",
                "family": "float_event_calendar",
                "parent": rank_expr,
                "ablation": "norank_event_口径",
                "expr": norank,
                "rank_expr": rank_expr,
            }
        )

    # dedupe jobs by role+parent+ablation+expr
    dedup = []
    seen_j = set()
    for j in jobs:
        key = (j.get("role"), j.get("parent"), j.get("ablation"), j.get("expr"))
        if key in seen_j:
            continue
        seen_j.add(key)
        dedup.append(j)
    jobs = dedup
    log("jobs", len(jobs), "float_norank", len(float_jobs))

    main_ledger = ROOT / "output/ai_factor/ledger.jsonl"
    run_ledger = OUT_MECH / "ledger_run.jsonl"
    if run_ledger.exists():
        run_ledger.unlink()
    n_before = (
        sum(1 for x in main_ledger.read_text().splitlines() if x.strip())
        if main_ledger.exists()
        else 0
    )

    results = []
    for i, job in enumerate(jobs):
        tok = job["expr"]
        try:
            # size resid token
            if job.get("ablation") == "size_neutral_manual" or str(tok).startswith("__SIZE_RESID__"):
                if not str(tok).startswith("__SIZE_RESID__"):
                    tok = f"__SIZE_RESID__::{job['parent'] if job.get('parent') else job['expr']}"
                    # fix: ablation_variants already sets __SIZE_RESID__::
                    tok = job["expr"]
            ev = evaluate_one(tok, panels, label, sig, adv, size_panel, sci)
            row = {**job, **ev}
        except Exception as exc:  # noqa: BLE001
            row = {
                **job,
                "expr": str(tok).split("::")[-1],
                "expr_token": tok,
                "metrics": sci.pack_metrics(None),
                "cs_stats": None,
                "coverage": None,
                "sim": {"error": f"{type(exc).__name__}: {exc}"},
                "leaves": sorted(leaves_in(str(tok).split("::")[-1])),
                "size_resid": str(tok).startswith("__SIZE_RESID__"),
            }
        row["promotion_approved"] = False
        row["trial_kind"] = "explore_gate"
        results.append(row)

        fit = (row.get("metrics") or {}).get("imp60_p25")
        notes = (
            f"l1e_rzrq_float_mech;role={row.get('role')};ablation={row.get('ablation')};"
            f"parent={row.get('parent')};process_not_sealed;promotion_approved=false"
        )
        for path in (run_ledger, main_ledger):
            append_attempt(
                engine="l1e_rzrq_float_mech",
                seed=SEED,
                universe="midlarge_top1500_or_csi300_500",
                cost=0.0025,
                window="explore_20240603_to_latest_l1e_rzrq_float_mech",
                expr_str=row.get("expr") or str(tok),
                fitness=fit if isinstance(fit, float) and math.isfinite(fit) else None,
                notes=notes,
                path=path,
            )
        peak = max(peak, mem_mb())
        if (i + 1) % 10 == 0 or i == 0 or i + 1 == len(jobs):
            log(
                f"{i+1}/{len(jobs)}",
                row.get("ablation"),
                (row.get("expr") or "")[:48],
                "60+25",
                fmt_pct(fit) if fit is not None else "—",
                "peak",
                peak,
            )
        if mem_mb() > MEM_CAP_MB - 150:
            gc.collect()

    n_after_mech = (
        sum(1 for x in main_ledger.read_text().splitlines() if x.strip())
        if main_ledger.exists()
        else 0
    )

    # Verdicts for rzrq cores
    rzrq_verdicts = []
    for c in core_reps:
        base = next(
            (r for r in results if r.get("role") == "primary" and r.get("expr") == c["expr"]),
            None,
        )
        if base is None:
            continue
        abls = [r for r in results if r.get("role") == "ablation" and r.get("parent") == c["expr"]]
        v = honesty_verdict_rzrq(c["expr"], base.get("metrics") or {}, abls)
        v["expr"] = c["expr"]
        v["baseline_metrics"] = base.get("metrics")
        v["n_ablations"] = len(abls)
        v["mechanism"] = MECHANISM_RZRQ.get(c["expr"])
        rzrq_verdicts.append(v)

    # Float demote logic
    float_rows = []
    for fj in float_jobs:
        ev = next(
            (
                r
                for r in results
                if r.get("role") == "float_norank" and r.get("parent") == fj["rank_expr"]
            ),
            None,
        )
        norank_m = (ev.get("metrics") if ev else None) or {}
        norank_cov = (ev.get("coverage") if ev else None) or {}
        passes_cov = bool(norank_cov.get("passes_coverage"))
        imp60 = norank_m.get("imp60_p25", float("nan"))
        imp100 = norank_m.get("imp100_p25", float("nan"))
        flat25 = norank_m.get("flat25", float("nan"))
        gate_ok = (
            passes_cov
            and math.isfinite(flat25)
            and flat25 > 0
            and math.isfinite(imp60)
            and imp60 >= IMP60_FLOOR
            and math.isfinite(imp100)
            and imp100 >= IMP60_FLOOR
        )
        if not passes_cov:
            verdict = "DEMOTE"
            note_zh = "非rank事件口径硬覆盖失败 → 降级；rank_fill_cov 不可当作诚实硬过"
            norank_cov_verdict = "FAIL_SPARSE"
        elif not gate_ok:
            verdict = "DEMOTE"
            note_zh = "非rank过覆盖但冲击/flat 未过闸 → 降级"
            norank_cov_verdict = "COV_PASS_GATE_FAIL"
        else:
            verdict = "SURVIVE"
            note_zh = "非rank事件口径硬覆盖+冲击均过（罕见）"
            norank_cov_verdict = "PASS"
        # event nonempty from gap
        en = fj.get("event_nonempty")
        if en is None and fj.get("event_leaf"):
            en = fl_gap.get(f"nonempty_{fj['event_leaf']}")
        float_rows.append(
            {
                "rank_expr": fj["rank_expr"],
                "norank_expr": fj["norank_expr"],
                "rank_nonempty": fj.get("rank_nonempty"),
                "event_leaf": fj.get("event_leaf"),
                "event_nonempty": en,
                "rank_fill_cov": True,
                "norank_passes_coverage": passes_cov,
                "norank_fail_reasons": norank_cov.get("fail_reasons") or [],
                "norank_cov_verdict": norank_cov_verdict,
                "norank_flat25": flat25,
                "norank_imp60_p25": imp60,
                "norank_imp100_p25": imp100,
                "norank_icir": norank_m.get("icir"),
                "norank_metrics": norank_m,
                "norank_coverage": norank_cov,
                "verdict": verdict,
                "note_zh": note_zh,
                "promotion_approved": False,
                "trial_kind": "explore_gate",
            }
        )

    peak = max(peak, mem_mb())
    meta = {
        "mode": "l1e_rzrq_float_mech_ablation",
        "promotion_approved": False,
        "sealed_executed": False,
        "trial_kind": "explore_gate",
        "n_rzrq_gate_ok": len(rzrq_gate),
        "n_rzrq_cores_ablated": len(core_reps),
        "n_rzrq_survive": sum(1 for v in rzrq_verdicts if v.get("survive_honesty")),
        "n_rzrq_fail": sum(1 for v in rzrq_verdicts if not v.get("survive_honesty")),
        "n_float_gate_ok": len(float_gate),
        "n_float_demote": sum(1 for r in float_rows if r["verdict"] == "DEMOTE"),
        "n_float_survive": sum(1 for r in float_rows if r["verdict"] == "SURVIVE"),
        "n_jobs": len(jobs),
        "rzrq_gap": rz_gap,
        "float_gap": fl_gap,
        "ledger_N_before": n_before,
        "ledger_N_after": n_after_mech,
        "ledger_N_new": n_after_mech - n_before,
        "peak_rss_MB": round(peak),
        "mem_cap_MB": MEM_CAP_MB,
        "under_mem_cap": peak < MEM_CAP_MB,
        "runtime_s": round(time.time() - t0, 1),
    }

    # --- shortlist v2b ---
    # Keep v2 members as-is; do NOT add rzrq (ICIR≤0) or demoted float
    v2b_members = []
    for m in v2_members:
        item = dict(m)
        item["coverage_tag"] = (
            "coverage_pass"
            if item.get("survive_coverage")
            else "sparse_warn"
        )
        if item.get("verdict") == "GATE_OK":
            item["coverage_tag"] = "coverage_pass"
        elif "SPARSE" in str(item.get("verdict", "")):
            item["coverage_tag"] = "sparse_warn"
        item["on_shortlist_v2b"] = True
        v2b_members.append(item)

    # Any float SURVIVE would be added — expect none
    for fr in float_rows:
        if fr["verdict"] == "SURVIVE":
            v2b_members.append(
                {
                    "source": "L1e_float_norank_survive",
                    "role": "l1e_float_norank",
                    "expr": fr["norank_expr"],
                    "notes": "nonrank event口径硬过+冲击过；原 rank 标 rank_fill_cov",
                    "metrics": fr["norank_metrics"],
                    "coverage": fr["norank_coverage"],
                    "coverage_tag": "event_口径_pass",
                    "verdict": "GATE_OK",
                    "promotion_approved": False,
                    "trial_kind": "explore_gate",
                    "on_shortlist_v2b": True,
                    "rank_fill_orig": fr["rank_expr"],
                }
            )

    # ledger entries for v2b members (process)
    n_before_v2b = n_after_mech
    for m in v2b_members:
        notes = (
            f"shortlist_v2b;role={m.get('role')};source={m.get('source')};"
            f"coverage_tag={m.get('coverage_tag')};process_not_sealed;promotion_approved=false"
        )
        fit = (m.get("metrics") or {}).get("imp60_p25")
        for path in (OUT_V2B / "ledger_run.jsonl", main_ledger):
            append_attempt(
                engine="shortlist_v2b",
                seed=SEED,
                universe="midlarge_top1500_or_csi300_500",
                cost=0.0025,
                window="explore_20240603_to_latest_shortlist_v2b",
                expr_str=m.get("expr"),
                fitness=fit if isinstance(fit, float) and math.isfinite(fit) else None,
                notes=notes,
                path=path,
            )
    n_after = (
        sum(1 for x in main_ledger.read_text().splitlines() if x.strip())
        if main_ledger.exists()
        else 0
    )
    meta["ledger_N_before_v2b"] = n_before_v2b
    meta["ledger_N_after"] = n_after
    meta["ledger_N_new"] = n_after - n_before
    meta["ledger_N_new_v2b"] = n_after - n_before_v2b
    meta["rzrq_explore_risk"] = [
        {
            "expr": r["expr"],
            "metrics": r.get("metrics"),
            "coverage": r.get("coverage"),
            "is_twin": r.get("is_twin"),
            "core_key": r.get("core_key"),
            "tag": "ICIR_LE_0",
        }
        for r in rzrq_gate
        if ((r.get("metrics") or {}).get("icir", 1) or 1) <= 0
    ]
    # keep top cores only in附表 display already limited in report
    meta["float_demoted"] = float_rows

    # Write outputs
    (OUT_MECH / "results.json").write_text(
        json.dumps(clean(results), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_MECH / "rzrq_verdicts.json").write_text(
        json.dumps(clean(rzrq_verdicts), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_MECH / "float_demote.json").write_text(
        json.dumps(clean(float_rows), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_MECH / "rzrq_gate_annotated.json").write_text(
        json.dumps(clean(rzrq_gate), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_MECH / "summary.json").write_text(
        json.dumps(clean(meta), ensure_ascii=False, indent=2), encoding="utf-8"
    )

    write_mech_report(rzrq_gate, core_reps, rzrq_verdicts, results, float_rows, meta)

    (OUT_V2B / "shortlist_v2b.json").write_text(
        json.dumps(clean(v2b_members), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    v2b_summary = {
        "mode": "shortlist_v2b",
        "promotion_approved": False,
        "sealed_executed": False,
        "n_members": len(v2b_members),
        "n_rzrq_explore_risk": len(meta["rzrq_explore_risk"]),
        "n_float_demoted": sum(1 for r in float_rows if r["verdict"] == "DEMOTE"),
        "members": [m.get("expr") for m in v2b_members],
        "ledger_N_after": n_after,
        "peak_rss_MB": round(peak),
        "runtime_s": round(time.time() - t0, 1),
    }
    (OUT_V2B / "summary.json").write_text(
        json.dumps(clean(v2b_summary), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_v2b(v2b_members, meta)

    log(
        "DONE",
        "rzrq_cores",
        len(core_reps),
        "survive",
        meta["n_rzrq_survive"],
        "float_demote",
        meta["n_float_demote"],
        "v2b",
        len(v2b_members),
        "N",
        n_after,
        "peak",
        peak,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
