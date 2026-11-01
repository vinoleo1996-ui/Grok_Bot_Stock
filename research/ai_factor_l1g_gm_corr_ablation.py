#!/usr/bin/env python3
"""L1g gm_pit family: textbook corr penalty + ablation → shortlist v2d.

promotion_approved=False. No sealed. No Strategy. No small-cap.
roe_pit GATE_OK stays CONTROL_ONLY (textbook-adjacent), never main shortlist.
gm_pit cores: |corr|>0.5 vs EP/BM/size/turnover/classic_FSR/quality → DEMOTE.
Only honest survivors enter v2d juxtaposed with v2c keepers.
Memory <2.5GB.
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
L1G_DIR = ROOT / "output/ai_factor/l1g_new_mech_family"
V2C_DIR = ROOT / "output/ai_factor/shortlist_v2c"
OUT_MECH = ROOT / "output/ai_factor/l1g_gm_corr_ablation"
OUT_V2D = ROOT / "output/ai_factor/shortlist_v2d"
REPORT_MECH = ROOT / "output/alpha/AI_FACTOR_L1g_GM_CORR_ABLATION_ZH.md"
REPORT_V2D = ROOT / "output/alpha/AI_FACTOR_SHORTLIST_V2d_ZH.md"

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
CORR_THRESHOLD = 0.5

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
    print(f"[l1g_gm {time.time()-t0:5.0f}s {mem_mb():.0f}MB]", *a, flush=True)


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


def core_key(expr: str) -> str:
    e = expr.strip()
    while True:
        m = re.fullmatch(r"(?:rank|zscore)\((.+)\)", e)
        if not m:
            break
        e = m.group(1)
    # unify double-neg
    m = re.fullmatch(r"neg\(neg_(.+)\)", e)
    if m:
        return m.group(1)  # neg(neg_roe_pit) → roe_pit
    m = re.fullmatch(r"neg\(neg\((.+)\)\)", e)
    if m:
        return m.group(1)
    m = re.fullmatch(r"(delay_\d+)\((?:rank|zscore)\((.+)\)\)", e)
    if m:
        return f"{m.group(1)}({m.group(2)})"
    return e


def is_roe_textbook_shell(expr: str) -> bool:
    """roe_pit level / mean / delay = textbook quality shell → control only."""
    ck = core_key(expr)
    L = leaves_in(ck) | leaves_in(expr)
    if "gm_pit" in L or "gm_delta_5" in L or "gm_delta_20" in L:
        return False
    # pure roe level-ish
    if "roe_pit" in L or "neg_roe_pit" in L:
        # deltas of roe would be more original; L1g GATE_OK are all level/mean/delay
        if any(x.startswith("roe_delta") or x.startswith("abs_roe") for x in L):
            return False
        return True
    return False


def is_gm_family(expr: str) -> bool:
    L = leaves_in(expr)
    return bool({"gm_pit", "gm_delta_5", "gm_delta_20"} & L)


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


MECHANISM = {
    "ts_std_10(gm_pit)": {
        "who_pays_zh": (
            "钱从「毛利率 PIT 状态的时序波动」来：grossprofit_margin 在 PIT 修订窗内的 "
            "10 日波动刻画盈利结构扰动/重估强度；高波动侧对应毛利率路径不确定或刚发生修订的中大盘，"
            "对手方支付的是毛利率路径静止股的相对折价。"
        ),
        "fail_when_zh": (
            "失效：①与 EP/BM/ROE 质量水平 |corr|>0.5（教科书质量通道）；②仅反映市值；"
            "③财报修订日历稀疏导致覆盖塌到事件稀疏；④取负后更赚（符号错）；"
            "⑤size 残差后收益消失。"
        ),
        "cluster": "gm_level_vol",
    },
    "neg(gm_pit)": {
        "who_pays_zh": (
            "钱从「低毛利率 PIT 水平」来：偏低毛利率中大盘在截面上可能被过度折价或处于"
            "均值回归/成本改善预期；对手方是高毛利率拥挤溢价。"
        ),
        "fail_when_zh": (
            "失效：①与经典价值/质量（EP/BM/ROE）高度共线 → 教科书壳；②纯小盘/市值通道；"
            "③行业结构主导（低毛利行业堆积）；④符号翻转后显著更赚。"
        ),
        "cluster": "gm_level_neg",
    },
    "roe_pit": {
        "who_pays_zh": "教科书质量 ROE 水平（对照壳，不作主短清单）。",
        "fail_when_zh": "本批强制 CONTROL_ONLY：ROE 水平=经典质量主线。",
        "cluster": "roe_textbook_shell",
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


def build_textbook_panels(cal, cols, mask, fsr_panel, ocf_panel, roe_panel, gm_panel) -> dict:
    """EP / BM / size / turnover / classic FSR / quality (ocf+roe) — control only."""
    out = {}
    ep_path = V2 / "ep/ep_pit_daily_tushare.parquet"
    if ep_path.exists():
        ep = pd.read_parquet(
            ep_path,
            columns=["trade_date", "instrument_id", "ep"],
            filters=[("trade_date", ">=", LOOKBACK_START - pd.Timedelta(days=5))],
        )
        ep["trade_date"] = pd.to_datetime(ep["trade_date"])
        ep = ep[ep["instrument_id"].isin(cols)]
        wide = (
            ep.dropna(subset=["ep"])
            .sort_values(["trade_date", "instrument_id"])
            .drop_duplicates(["trade_date", "instrument_id"], keep="last")
            .set_index(["trade_date", "instrument_id"])["ep"]
            .unstack()
            .reindex(index=cal, columns=cols)
            .astype("float32")
            .ffill(limit=5)
        )
        if mask is not None:
            wide = wide.where(mask)
        out["EP"] = wide.astype("float32")
        del ep, wide
        gc.collect()

    val_path = V2 / "valuation/daily_basic_valuation_tushare.parquet"
    if val_path.exists():
        val = pd.read_parquet(
            val_path,
            columns=["trade_date", "instrument_id", "pb", "pe_ttm", "total_mv"],
            filters=[("trade_date", ">=", LOOKBACK_START - pd.Timedelta(days=5))],
        )
        val["trade_date"] = pd.to_datetime(val["trade_date"])
        val = val[val["instrument_id"].isin(cols)]

        def pivot(col):
            sub = val[["trade_date", "instrument_id", col]].dropna(subset=[col])
            sub = sub.sort_values(["trade_date", "instrument_id"]).drop_duplicates(
                ["trade_date", "instrument_id"], keep="last"
            )
            w = (
                sub.set_index(["trade_date", "instrument_id"])[col]
                .unstack()
                .reindex(index=cal, columns=cols)
                .astype("float32")
                .ffill(limit=5)
            )
            if mask is not None:
                w = w.where(mask)
            return w.astype("float32")

        pb = pivot("pb")
        with np.errstate(divide="ignore", invalid="ignore"):
            bm = (1.0 / pb.replace(0, np.nan)).astype("float32")
        out["BM"] = bm
        tm = pivot("total_mv")
        out["size"] = np.log(tm.where(tm > 0)).astype("float32")
        pe = pivot("pe_ttm")
        with np.errstate(divide="ignore", invalid="ignore"):
            out["EP_from_pe"] = (1.0 / pe.replace(0, np.nan)).astype("float32")
        del val, pb, tm, pe
        gc.collect()

    tov = (
        pd.read_parquet(SCRATCH / "turnover.parquet", columns=cols)
        .astype("float32")
        .loc[lambda d: d.index >= LOOKBACK_START]
        .reindex(index=cal, columns=cols)
    )
    turn20 = tov.rolling(20, min_periods=10).mean().astype("float32")
    if mask is not None:
        turn20 = turn20.where(mask)
    out["turnover"] = turn20
    del tov, turn20
    gc.collect()

    if fsr_panel is not None:
        out["classic_FSR"] = fsr_panel.astype("float32")
    if ocf_panel is not None:
        out["quality_ocf"] = ocf_panel.astype("float32")
    # classic quality = ROE level (explicit textbook shell control for gm family)
    if roe_panel is not None:
        out["quality_roe"] = roe_panel.astype("float32")
    # also expose gm level as classic margin control (for vol transforms)
    if gm_panel is not None:
        out["classic_gm"] = gm_panel.astype("float32")

    return out


def ablation_variants(parent: str) -> list[dict]:
    jobs = []

    def add(ablation: str, expr: str, note: str = ""):
        jobs.append(
            {
                "role": "ablation",
                "parent": parent,
                "ablation": ablation,
                "expr": expr,
                "note": note,
            }
        )

    L = sorted(leaves_in(parent))
    for leaf in L:
        add(f"static_{leaf}", leaf, f"静态 {leaf}")
        add(f"static_rank_{leaf}", f"rank({leaf})", f"静态 rank({leaf})")
        add(f"static_zscore_{leaf}", f"zscore({leaf})", f"静态 zscore({leaf})")
        if not leaf.startswith("neg_"):
            add(f"static_neg_{leaf}", f"neg({leaf})", f"静态 neg({leaf})")

    add("sign_flip", f"neg({parent})", "整体取负")
    add("delay_5", f"delay_5({parent})", "整体 delay5")
    add("delay_20", f"delay_20({parent})", "整体 delay20")
    add("size_neutral_manual", f"__SIZE_RESID__::{parent}", "size 日度残差")

    if "gm_pit" in L:
        add("static_gm", "gm_pit", "经典毛利率水平对照")
        add("static_neg_gm", "neg(gm_pit)", "neg 毛利率水平")
        add("vol_to_mean", "ts_mean_10(gm_pit)", "改用均值平滑")
        add("raw_gm_delta_20", "gm_delta_20", "毛利率 20 日差分")
        if parent.startswith("ts_std_"):
            add("shorter_vol", "ts_std_5(gm_pit)", "更短波动窗")
            add("longer_vol", "ts_std_20(gm_pit)", "更长波动窗")
        if parent.startswith("neg("):
            add("pos_level", "gm_pit", "去掉 neg（正毛利率水平）")
            add("vol_instead", "ts_std_10(gm_pit)", "改用波动叶")

    return jobs


def honesty_verdict(parent: str, base_m: dict, abl_rows: list[dict], corr_info: dict) -> dict:
    fails = []
    passes = []
    notes = []
    flags = list(corr_info.get("flags") or [])

    def m_of(ablation):
        for r in abl_rows:
            if r.get("ablation") == ablation:
                return r.get("metrics") or {}
        return None

    base60 = base_m.get("imp60_p25", float("nan"))
    base100 = base_m.get("imp100_p25", float("nan"))
    base_icir = base_m.get("icir", float("nan"))
    base_flat25 = base_m.get("flat25", float("nan"))

    if corr_info.get("demote_textbook"):
        fails.append("textbook_corr_gt_0.5")
        notes.append(
            f"**教科书相关惩罚：** max|corr|={fmt_f(corr_info.get('max_abs_corr'), 3)} "
            f"vs {corr_info.get('max_corr_name')} → DEMOTE 仅对照，不得入主短清单"
        )

    if corr_info.get("force_control_roe"):
        fails.append("roe_textbook_shell_control_only")
        flags.append("ROE_TEXTBOOK_SHELL")
        notes.append("**roe_pit 教科书质量壳：** 强制 CONTROL_ONLY，不入主短清单")

    if math.isfinite(base_icir) and base_icir <= 0:
        fails.append("icir_le_0")
        flags.append("ICIR_LE_0")
        notes.append(f"ICIR≤0 ({base_icir:.3f}) — 不作稳健主候选")

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
            notes.append(f"delay_20 未衰减 ({d20['imp60_p25']:.2%}) — 持久水平态可疑")
            flags.append("delay20_no_decay")
        else:
            passes.append("delay_20_decays_or_flat")

    static_rows = [
        (r.get("ablation"), r.get("metrics") or {})
        for r in abl_rows
        if str(r.get("ablation", "")).startswith("static_")
        or r.get("ablation") in ("raw_gm_delta_20", "vol_to_mean", "pos_level", "vol_instead")
    ]
    best_static = None
    for k, mm in static_rows:
        if mm and math.isfinite(mm.get("imp60_p25", float("nan"))):
            if best_static is None or mm["imp60_p25"] > best_static[1]["imp60_p25"]:
                best_static = (k, mm)
    if best_static and math.isfinite(base60):
        sk, sm = best_static
        if sm["imp60_p25"] >= base60 - 0.005:
            notes.append(
                f"静态/拆臂 {sk}≈基线 ({sm['imp60_p25']:.2%} vs {base60:.2%}) — 变换增益有限"
            )
            if sk in ("static_gm", "static_gm_pit", "pos_level", "static_roe_pit"):
                flags.append("static_textbookish_comparable")
            passes.append("static_comparable")
        else:
            notes.append(
                f"变换优于最佳静态/拆臂 {sk} ({base60:.2%} > {sm['imp60_p25']:.2%})"
            )
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
    if not (math.isfinite(base100) and base100 >= IMP60_FLOOR):
        fails.append("below_imp100_floor")
    if not (math.isfinite(base_flat25) and base_flat25 > 0):
        fails.append("flat25_nonpositive")

    survive = len(fails) == 0
    if corr_info.get("demote_textbook") or corr_info.get("force_control_roe"):
        verdict = "DEMOTE_TEXTBOOK" if corr_info.get("demote_textbook") else "CONTROL_ONLY_ROE"
        if corr_info.get("force_control_roe") and not corr_info.get("demote_textbook"):
            verdict = "CONTROL_ONLY_ROE"
        if corr_info.get("demote_textbook"):
            verdict = "DEMOTE_TEXTBOOK"
    elif not survive:
        verdict = "FAIL"
    else:
        verdict = "SURVIVE"
        if "ICIR_LE_0" in flags:
            verdict = "SURVIVE_EXPLORE_ICIR_RISK"

    enter = bool(
        survive
        and not corr_info.get("demote_textbook")
        and not corr_info.get("force_control_roe")
        and is_gm_family(parent)
    )

    return {
        "survive_honesty": enter,
        "verdict": verdict,
        "hard_fails": fails,
        "soft_passes": passes,
        "flags": flags,
        "notes": notes,
        "promote": False,
        "enter_shortlist_v2d": enter,
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
                "factor": None,
            }
        fac = size_residualize(fac, size_panel)
    cs = sci.cs_std_stats(fac)
    cov = sci.coverage_stats(fac)
    if not cs.get("passes_cs_variation"):
        sim = {"skipped": True, "reason": "cs_variation_fail", "promotion_approved": False}
        m = sci.pack_metrics(sim)
        fac_out = None
        del fac
    else:
        sim = sci.simulate_book(fac, label, sig, adv)
        m = sci.pack_metrics(sim)
        fac_out = fac
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
        "factor": fac_out,
    }


def corr_screen(fac: pd.DataFrame, textbook: dict) -> dict:
    from quantlab.factors.ai_factory.fitness import corr_with_panel

    public_corr = {}
    max_abs = 0.0
    max_name = None
    for name, panel in textbook.items():
        # classic_gm is a self-control for vol transforms; still count for demote
        # but for neg(gm_pit) vs classic_gm corr will be ~1 — that's intentional textbook demote
        c = corr_with_panel(fac, panel)
        public_corr[name] = c
        if np.isfinite(c) and abs(c) > max_abs:
            max_abs = abs(c)
            max_name = name
    demote = bool(max_abs > CORR_THRESHOLD)
    return {
        "public_corr": public_corr,
        "max_abs_corr": float(max_abs) if max_abs > 0 else float("nan"),
        "max_corr_name": max_name,
        "demote_textbook": demote,
        "flags": ["TEXTBOOK_CORR"] if demote else [],
        "threshold": CORR_THRESHOLD,
    }


def write_mech_report(gate_ok, gm_cores, roe_controls, corr_rows, verdicts, results, meta):
    lines = []
    lines.append("# AI 因子 L1g：gm_pit 教科书相关惩罚 + 消融（→ 短清单 v2d）")
    lines.append("")
    lines.append("- **时间：** 2026-10-12（America/New_York）")
    lines.append("- **promotion_approved：** false；**密封：** 未开；**不交 Strategy 权重**")
    lines.append("- **trial_kind：** explore_gate / process")
    lines.append("- **本金主口径：** 60 万 / 100 万；主裁决=冲击+flat25；IMP60_FLOOR=10%")
    lines.append(
        f"- **教科书相关惩罚：** |corr|>{CORR_THRESHOLD} vs EP/BM/size/turnover/"
        "classic_FSR/quality_ocf/quality_roe/classic_gm → **DEMOTE 仅对照**"
    )
    lines.append("- **roe_pit：** 强制 CONTROL_ONLY（教科书质量壳），**不入主短清单**")
    lines.append("- **禁止：** 广播、跌停主候选、小盘、教科书主线、密封、Strategy")
    lines.append(
        f"- 账本：N {meta.get('ledger_N_before')} → {meta.get('ledger_N_after')} "
        f"（+{meta.get('ledger_N_new')}，explore_gate）"
    )
    lines.append(
        f"- 峰值 RSS：{meta.get('peak_rss_MB'):.0f} MB（上限 {MEM_CAP_MB}；"
        f"under_cap={meta.get('under_mem_cap')}）；运行 {meta.get('runtime_s')}s"
    )
    lines.append("- 上游：`AI_FACTOR_L1g_NEW_MECH_FAMILY_EXPLORE_ZH.md`；`AI_FACTOR_SHORTLIST_V2c_ZH.md`")
    lines.append("")

    lines.append("## ① gm_pit 候选机制说明（钱从谁来 / 失效条件）")
    lines.append("")
    for c in gm_cores:
        expr = c["expr"]
        ck = core_key(expr)
        mech = MECHANISM.get(expr) or MECHANISM.get(ck) or {}
        if not mech:
            for k, v in MECHANISM.items():
                if core_key(k) == ck:
                    mech = v
                    break
        lines.append(f"### `{expr}`")
        lines.append(f"- **簇：** {mech.get('cluster', 'gm')}；core=`{ck}`")
        lines.append(f"- **钱从谁来：** {mech.get('who_pays_zh', '—')}")
        lines.append(f"- **失效条件：** {mech.get('fail_when_zh', '—')}")
        m = c.get("metrics") or {}
        lines.append(
            f"- **L1g 基线：** flat25={fmt_pct(m.get('flat25'))}；"
            f"60万+25bp={fmt_pct(m.get('imp60_p25'))}；ICIR={fmt_f(m.get('icir'), 3)}"
        )
        lines.append("")

    lines.append("## ①b roe_pit 对照壳（不入主短清单）")
    lines.append("")
    lines.append("| 表达式 | flat25 | 60万+25bp | ICIR | 标签 |")
    lines.append("|---|---:|---:|---:|---|")
    for r in roe_controls:
        m = r.get("metrics") or {}
        lines.append(
            f"| `{r['expr']}` | {fmt_pct(m.get('flat25'))} | "
            f"{fmt_pct(m.get('imp60_p25'))} | {fmt_f(m.get('icir'), 3)} | CONTROL_ONLY_ROE |"
        )
    lines.append("")
    lines.append("- **裁决：** 全部 `roe_pit` 水平/均值/delay 等价物 = 教科书质量主线 → **仅对照**。")
    lines.append("")

    lines.append("## ② 教科书相关惩罚筛（|corr|>0.5 → DEMOTE）")
    lines.append("")
    tb_names = meta.get("textbook_panels") or []
    lines.append(f"- 对照面板：{', '.join(f'`{x}`' for x in tb_names)}")
    lines.append("")
    # focus table on gm cores + note roe
    gm_corr = [r for r in corr_rows if is_gm_family(r["expr"])]
    hdr = (
        "| # | 表达式 | max|corr| | 对谁 | DEMOTE? | "
        + " | ".join(tb_names)
        + " |"
    )
    lines.append(hdr)
    lines.append("|---|---|---:|---|:---:|" + "|".join(["---:"] * len(tb_names)) + "|")
    for i, r in enumerate(gm_corr, 1):
        pc = r.get("public_corr") or {}
        cells = " | ".join(fmt_f(pc.get(n), 3) for n in tb_names)
        dem = "**YES**" if r.get("demote_textbook") else "no"
        lines.append(
            f"| {i} | `{r['expr']}` | {fmt_f(r.get('max_abs_corr'), 3)} | "
            f"{r.get('max_corr_name') or '—'} | {dem} | {cells} |"
        )
    n_demote = sum(1 for r in gm_corr if r.get("demote_textbook"))
    n_pass_corr = len(gm_corr) - n_demote
    lines.append("")
    lines.append(
        f"- **gm 族 DEMOTE_TEXTBOOK={n_demote}/{len(gm_corr)}**；过相关惩罚={n_pass_corr}/{len(gm_corr)}。"
    )
    lines.append("- 教科书面板仅作相关对照，**永不入主短清单**。")
    lines.append("")

    # compact roe corr appendix
    roe_corr = [r for r in corr_rows if is_roe_textbook_shell(r["expr"])]
    if roe_corr:
        lines.append("### roe_pit 对照壳相关（摘要）")
        lines.append("")
        lines.append("| 表达式 | max|corr| | 对谁 |")
        lines.append("|---|---:|---|")
        seen_ck = set()
        for r in roe_corr:
            ck = core_key(r["expr"])
            if ck in seen_ck:
                continue
            seen_ck.add(ck)
            lines.append(
                f"| `{r['expr']}` | {fmt_f(r.get('max_abs_corr'), 3)} | "
                f"{r.get('max_corr_name') or '—'} |"
            )
        lines.append("")

    lines.append("## ③ 消融 + 静态对照（gm 核心叶）")
    lines.append("")
    for v in verdicts:
        lines.append(f"### `{v['expr']}` → **{v['verdict']}**")
        bm = v.get("baseline_metrics") or {}
        lines.append(
            f"- 基线：flat25={fmt_pct(bm.get('flat25'))}；60万+25bp={fmt_pct(bm.get('imp60_p25'))}；"
            f"100万+25bp={fmt_pct(bm.get('imp100_p25'))}；ICIR={fmt_f(bm.get('icir'), 3)}"
        )
        ci = v.get("corr_info") or {}
        lines.append(
            f"- 相关：max|corr|={fmt_f(ci.get('max_abs_corr'), 3)} vs {ci.get('max_corr_name')}；"
            f"demote={ci.get('demote_textbook')}"
        )
        if v.get("flags"):
            lines.append(f"- flags：{', '.join(v['flags'])}")
        if v.get("hard_fails"):
            lines.append(f"- hard_fails：{', '.join(v['hard_fails'])}")
        if v.get("soft_passes"):
            lines.append(f"- soft_passes：{', '.join(v['soft_passes'])}")
        for n in v.get("notes") or []:
            lines.append(f"- {n}")
        abls = [r for r in results if r.get("role") == "ablation" and r.get("parent") == v["expr"]]
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

    n_surv = sum(1 for v in verdicts if v.get("enter_shortlist_v2d"))
    n_fail = sum(1 for v in verdicts if v.get("verdict") == "FAIL")
    n_dem = sum(1 for v in verdicts if v.get("verdict") == "DEMOTE_TEXTBOOK")
    n_ctrl = sum(1 for v in verdicts if v.get("verdict") == "CONTROL_ONLY_ROE")
    lines.append("## ④ 诚实裁决汇总")
    lines.append("")
    lines.append("| 裁决 | 计数 |")
    lines.append("|---|---:|")
    lines.append(f"| SURVIVE（可入 v2d） | {n_surv} |")
    lines.append(f"| DEMOTE_TEXTBOOK | {n_dem} |")
    lines.append(f"| CONTROL_ONLY_ROE | {n_ctrl} |")
    lines.append(f"| FAIL | {n_fail} |")
    lines.append(f"| 核心叶合计 | {len(verdicts)} |")
    lines.append("")
    lines.append("- 孪生 rank/zscore 随核心裁决绑定，不单独扩容。")
    lines.append("- **不开密封、不交 Strategy**；`promotion_approved=false`。")
    lines.append("")
    lines.append("## 产物路径")
    lines.append("")
    lines.append("- 报告：`output/alpha/AI_FACTOR_L1g_GM_CORR_ABLATION_ZH.md`")
    lines.append("- JSON：`output/ai_factor/l1g_gm_corr_ablation/`")
    lines.append(f"- 账本：`output/ai_factor/ledger.jsonl` N={meta.get('ledger_N_after')}")
    lines.append("")
    REPORT_MECH.write_text("\n".join(lines), encoding="utf-8")
    log("wrote", REPORT_MECH)


def write_v2d_report(v2d_members, demoted, failed, roe_controls, meta):
    lines = []
    lines.append("# AI 因子短清单 v2d（v2c 保留 + L1g gm_pit 过相关/消融）")
    lines.append("")
    lines.append("- **时间：** 2026-10-12（America/New_York）")
    lines.append("- **promotion_approved：** false；**密封：** 未开；**不交 Strategy 权重**")
    lines.append("- **trial_kind：** explore_gate / process")
    lines.append("- **本金主口径：** 60 万 / 100 万；主裁决=冲击+flat25")
    lines.append("- **禁止：** 广播、跌停主候选、小盘、教科书主线、密封、Strategy")
    lines.append(
        f"- 账本：N {meta.get('ledger_N_before_v2d')} → {meta.get('ledger_N_after')} "
        f"（本步短清单记账 +{meta.get('ledger_N_v2d_new')}）"
    )
    lines.append(
        f"- 峰值 RSS：{meta.get('peak_rss_MB'):.0f} MB；运行 {meta.get('runtime_s')}s"
    )
    lines.append(
        "- 上游：`AI_FACTOR_SHORTLIST_V2c_ZH.md`；`AI_FACTOR_L1g_GM_CORR_ABLATION_ZH.md`"
    )
    lines.append("")

    lines.append("## 入选 / 降级规则")
    lines.append("")
    lines.append("| 规则 | 说明 |")
    lines.append("|---|---|")
    lines.append("| 保留 v2c | ann_insider + L1f FSR/质量交叉 全部并列保留 |")
    lines.append(
        f"| L1g gm 新叶 | 过教科书相关（|corr|≤{CORR_THRESHOLD}）∧ 消融诚实 ∧ ICIR>0 ∧ 冲击闸 |"
    )
    lines.append("| roe_pit | **强制 CONTROL_ONLY**，不入主短清单 |")
    lines.append("| 教科书相关 | |corr|>0.5 → DEMOTE 仅对照 |")
    lines.append("| 孪生 | rank/zscore 对称式不重复计入 |")
    lines.append("")

    lines.append("## 短清单 v2d 成员")
    lines.append("")
    lines.append(
        "| # | 来源 | role | 表达式 | flat25 | 60万+25bp | 100万+25bp | ICIR | "
        "nonempty | 覆盖/相关标签 | 裁决 |"
    )
    lines.append("|---|---|---|---|---:|---:|---:|---:|---:|---|---|")
    for i, r in enumerate(v2d_members, 1):
        m = r.get("metrics") or {}
        cov = r.get("coverage") or {}
        nr = cov.get("nonempty_rate")
        if nr is None and isinstance(cov, dict):
            nr = cov.get("nonempty")
        lines.append(
            f"| {i} | {r.get('source')} | {r.get('role')} | `{r.get('expr')}` | "
            f"{fmt_pct(m.get('flat25'))} | {fmt_pct(m.get('imp60_p25'))} | "
            f"{fmt_pct(m.get('imp100_p25'))} | {fmt_f(m.get('icir'), 3)} | "
            f"{fmt_f(nr, 4) if isinstance(nr, float) else (nr or '—')} | "
            f"{r.get('tag','')} | {r.get('verdict')} |"
        )
    lines.append("")

    if demoted:
        lines.append("## 附表：DEMOTE_TEXTBOOK（相关惩罚，不入主短清单）")
        lines.append("")
        lines.append("| 表达式 | 60万+25bp | ICIR | max|corr| | 对谁 |")
        lines.append("|---|---:|---:|---:|---|")
        for r in demoted:
            m = r.get("metrics") or r.get("baseline_metrics") or {}
            ci = r.get("corr_info") or {}
            lines.append(
                f"| `{r.get('expr')}` | {fmt_pct(m.get('imp60_p25'))} | "
                f"{fmt_f(m.get('icir'), 3)} | {fmt_f(ci.get('max_abs_corr'), 3)} | "
                f"{ci.get('max_corr_name')} |"
            )
        lines.append("")

    if failed:
        lines.append("## 附表：消融 FAIL（过相关但诚实消融未过）")
        lines.append("")
        lines.append("| 表达式 | 60万+25bp | ICIR | hard_fails |")
        lines.append("|---|---:|---:|---|")
        for r in failed:
            m = r.get("baseline_metrics") or r.get("metrics") or {}
            lines.append(
                f"| `{r.get('expr')}` | {fmt_pct(m.get('imp60_p25'))} | "
                f"{fmt_f(m.get('icir'), 3)} | {', '.join(r.get('hard_fails') or [])} |"
            )
        lines.append("")

    if roe_controls:
        lines.append("## 附表：roe_pit CONTROL_ONLY（教科书质量壳）")
        lines.append("")
        lines.append("| 表达式 | 60万+25bp | ICIR |")
        lines.append("|---|---:|---:|")
        seen = set()
        for r in roe_controls:
            ck = core_key(r["expr"])
            if ck in seen:
                continue
            seen.add(ck)
            m = r.get("metrics") or {}
            lines.append(
                f"| `{r['expr']}` | {fmt_pct(m.get('imp60_p25'))} | {fmt_f(m.get('icir'), 3)} |"
            )
        lines.append("")

    n_v2c = meta.get("n_v2c_keepers", 0)
    n_gm = meta.get("n_gm_new_on_v2d", 0)
    lines.append("## 诚实裁决")
    lines.append("")
    lines.append(f"1. **v2d 主成员数：** {len(v2d_members)}（v2c 保留 {n_v2c} + gm 新叶 {n_gm}）。")
    lines.append(
        f"2. **L1g gm 扩容：** SURVIVE={meta.get('n_survive_cores', 0)}；"
        f"DEMOTE_TEXTBOOK={meta.get('n_demote_textbook', 0)}；"
        f"FAIL={meta.get('n_fail_ablation', 0)}；"
        f"roe CONTROL_ONLY 核心={meta.get('n_roe_control_cores', 0)}。"
    )
    lines.append("3. **roe_pit 永不入主短清单**（教科书质量壳，仅对照）。")
    lines.append("4. **教科书相关永不入主短清单**（仅相关对照）。")
    lines.append("5. **不开密封、不交 Strategy**；`promotion_approved=false`。")
    lines.append("")
    lines.append("## 产物路径")
    lines.append("")
    lines.append("- 报告：`output/alpha/AI_FACTOR_SHORTLIST_V2d_ZH.md`")
    lines.append("- JSON：`output/ai_factor/shortlist_v2d/`")
    lines.append(f"- 账本：`output/ai_factor/ledger.jsonl` N={meta.get('ledger_N_after')}")
    lines.append("")
    REPORT_V2D.write_text("\n".join(lines), encoding="utf-8")
    log("wrote", REPORT_V2D)


def main() -> int:
    global t0
    t0 = time.time()
    peak = mem_mb()
    OUT_MECH.mkdir(parents=True, exist_ok=True)
    OUT_V2D.mkdir(parents=True, exist_ok=True)
    REPORT_MECH.parent.mkdir(parents=True, exist_ok=True)

    gate_ok = json.loads((L1G_DIR / "gate_ok.json").read_text())
    gate_ok = sorted(
        gate_ok,
        key=lambda r: (r.get("metrics") or {}).get("imp60_p25") or -1,
        reverse=True,
    )
    v2c = json.loads((V2C_DIR / "shortlist_v2c.json").read_text())
    log("GATE_OK", len(gate_ok), "v2c", len(v2c))

    gm_rows = [r for r in gate_ok if is_gm_family(r["expr"])]
    roe_rows = [r for r in gate_ok if is_roe_textbook_shell(r["expr"])]
    log("gm_GATE_OK", len(gm_rows), "roe_CONTROL", len(roe_rows))

    # unique cores — prefer non-rank
    def pick_cores(rows):
        seen = {}
        for r in rows:
            ck = core_key(r["expr"])
            r["core_key"] = ck
            prev = seen.get(ck)
            if prev is None:
                seen[ck] = r
            else:
                if r["expr"].startswith("rank(") and not prev["expr"].startswith("rank("):
                    pass
                elif not r["expr"].startswith("rank(") and prev["expr"].startswith("rank("):
                    seen[ck] = r
                elif r["expr"].startswith("zscore(") and not prev["expr"].startswith(
                    ("rank(", "zscore(")
                ):
                    pass
                elif not r["expr"].startswith(("rank(", "zscore(")) and prev["expr"].startswith(
                    ("rank(", "zscore(")
                ):
                    seen[ck] = r
        return list(seen.values())

    gm_cores = pick_cores(gm_rows)
    roe_cores = pick_cores(roe_rows)
    log("gm_cores", [c["expr"] for c in gm_cores])
    log("roe_cores", [c["expr"] for c in roe_cores])

    _ensure_pkgs()
    sci = _import_mod(
        "ai_factor_l1d_shortlist_coverage_impact",
        ROOT / "research/ai_factor_l1d_shortlist_coverage_impact.py",
    )
    l1f = _import_mod(
        "ai_factor_l1f_strict_gate_struct_explore",
        ROOT / "research/ai_factor_l1f_strict_gate_struct_explore.py",
    )
    l1g = _import_mod(
        "ai_factor_l1g_new_mech_family_explore",
        ROOT / "research/ai_factor_l1g_new_mech_family_explore.py",
    )
    l1b = _import_mod(
        "ai_factor_l1b_structural_explore",
        ROOT / "research/ai_factor_l1b_structural_explore.py",
    )
    from quantlab.factors.ai_factory.ledger import append_attempt
    from quantlab.factors.ops import apply_expr, parse_expr

    log("loading base for mask/label")
    panels0, label, public, load_meta = l1b.load_structural_panels()
    peak = max(peak, mem_mb())
    size_from_public = None
    if isinstance(public, dict) and public.get("size") is not None:
        size_from_public = public["size"].astype("float32")
    del public
    gc.collect()

    if "overnight_ret" in panels0:
        mask = panels0["overnight_ret"].notna()
        cols = list(panels0["overnight_ret"].columns)
        cal = panels0["overnight_ret"].index
    else:
        cols = list(next(iter(panels0.values())).columns)
        cal = next(iter(panels0.values())).index
        mask = None
    for k in list(panels0.keys()):
        del panels0[k]
    del panels0
    gc.collect()
    log("cleared structural; building gm/roe/fsr/ocf", "peak", peak)

    panels: dict = {}
    roe_panels, roe_gap = l1g.build_roe_panels(cal, cols, mask)
    panels.update(roe_panels)
    del roe_panels
    gc.collect()

    # lightweight fsr/ocf for textbook only — then drop from factor panels if unused
    ocf_panels, ocf_gap = l1f.build_ocf_panels(cal, cols, mask)
    fsr_dv, fsr_gap, dv_gap = l1f.build_fsr_dv_panels(cal, cols, mask)
    # keep fsr/ocf only as textbook refs; also need them if any ablation uses — gm ablations don't
    fsr_ref = fsr_dv.get("fsr")
    ocf_ref = ocf_panels.get("ocf_to_profit")
    del ocf_panels, fsr_dv
    gc.collect()
    peak = max(peak, mem_mb())
    log("factor panels", list(panels.keys()), "peak", peak)

    textbook = build_textbook_panels(
        cal,
        cols,
        mask,
        fsr_panel=fsr_ref,
        ocf_panel=ocf_ref,
        roe_panel=panels.get("roe_pit"),
        gm_panel=panels.get("gm_pit"),
    )
    size_panel = textbook.get("size")
    if size_panel is None:
        size_panel = size_from_public
    # free heavy textbook refs we duplicated
    if fsr_ref is not None:
        del fsr_ref
    if ocf_ref is not None:
        del ocf_ref
    gc.collect()
    peak = max(peak, mem_mb())
    log("textbook panels", list(textbook.keys()), "peak", peak)

    sig, adv = sci.load_sig_adv(cols, cal)
    peak = max(peak, mem_mb())

    # --- corr screen: all gm GATE_OK + roe cores ---
    corr_targets = gm_rows + roe_cores
    corr_rows = []
    for g in corr_targets:
        expr = g["expr"]
        try:
            fac = apply_expr(
                parse_expr(to_nested_tuple(_seed_to_tuple(expr))), panels
            ).astype("float32")
            ci = corr_screen(fac, textbook)
            del fac
            gc.collect()
        except Exception as exc:  # noqa: BLE001
            ci = {
                "public_corr": {},
                "max_abs_corr": float("nan"),
                "max_corr_name": None,
                "demote_textbook": False,
                "flags": [f"CORR_ERROR:{type(exc).__name__}"],
                "error": str(exc),
                "threshold": CORR_THRESHOLD,
            }
        if is_roe_textbook_shell(expr):
            ci["force_control_roe"] = True
            ci["flags"] = list(ci.get("flags") or []) + ["ROE_TEXTBOOK_SHELL"]
        corr_rows.append(
            {"expr": expr, "family": g.get("family"), "metrics": g.get("metrics"), **ci}
        )
        log(
            "corr",
            expr[:48],
            "max",
            fmt_f(ci.get("max_abs_corr"), 3),
            ci.get("max_corr_name"),
            "DEMOTE" if ci.get("demote_textbook") else (
                "CTRL_ROE" if ci.get("force_control_roe") else "ok"
            ),
        )
        peak = max(peak, mem_mb())

    corr_by_expr = {r["expr"]: r for r in corr_rows}

    # --- ablation jobs for gm cores only ---
    jobs = []
    for c in gm_cores:
        jobs.append(
            {
                "role": "primary",
                "family": c.get("family"),
                "parent": c["expr"],
                "ablation": "baseline",
                "expr": c["expr"],
                "gate_imp60_p25": (c.get("metrics") or {}).get("imp60_p25"),
            }
        )
        for a in ablation_variants(c["expr"]):
            jobs.append(a)

    # roe cores: primary only (no ablation expansion) for ledger honesty
    for c in roe_cores:
        jobs.append(
            {
                "role": "primary_roe_control",
                "family": c.get("family"),
                "parent": c["expr"],
                "ablation": "baseline",
                "expr": c["expr"],
                "gate_imp60_p25": (c.get("metrics") or {}).get("imp60_p25"),
            }
        )

    dedup, seen_j = [], set()
    for j in jobs:
        key = (j.get("role"), j.get("parent"), j.get("ablation"), j.get("expr"))
        if key in seen_j:
            continue
        seen_j.add(key)
        dedup.append(j)
    jobs = dedup
    log("jobs", len(jobs))

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
            ev = evaluate_one(tok, panels, label, sig, adv, size_panel, sci)
            fac = ev.pop("factor", None)
            if fac is not None:
                del fac
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
            f"l1g_gm_corr_ablation;role={row.get('role')};ablation={row.get('ablation')};"
            f"parent={row.get('parent')};process_not_sealed;promotion_approved=false"
        )
        for path in (run_ledger, main_ledger):
            append_attempt(
                engine="l1g_gm_corr_ablation",
                seed=SEED,
                universe="midlarge_top1500_or_csi300_500",
                cost=0.0025,
                window="explore_20240603_to_latest_l1g_gm_corr",
                expr_str=row.get("expr") or str(tok),
                fitness=fit if isinstance(fit, float) and math.isfinite(fit) else None,
                notes=notes,
                path=path,
            )
        peak = max(peak, mem_mb())
        if (i + 1) % 8 == 0 or i == 0 or i + 1 == len(jobs):
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

    # verdicts: gm cores get full honesty; roe cores force CONTROL_ONLY
    verdicts = []
    for c in gm_cores:
        base = next(
            (r for r in results if r.get("role") == "primary" and r.get("parent") == c["expr"]),
            None,
        )
        base_m = (base.get("metrics") if base else None) or (c.get("metrics") or {})
        if not math.isfinite(base_m.get("imp60_p25", float("nan"))):
            base_m = c.get("metrics") or {}
        abls = [r for r in results if r.get("role") == "ablation" and r.get("parent") == c["expr"]]
        ci = dict(corr_by_expr.get(c["expr"]) or {})
        # twin demote
        for g in gm_rows:
            if core_key(g["expr"]) == core_key(c["expr"]):
                tci = corr_by_expr.get(g["expr"]) or {}
                if tci.get("demote_textbook"):
                    if (tci.get("max_abs_corr") or 0) >= (ci.get("max_abs_corr") or 0):
                        ci = dict(tci)
                    ci["demote_textbook"] = True
                    if "TEXTBOOK_CORR" not in (ci.get("flags") or []):
                        ci["flags"] = list(ci.get("flags") or []) + ["TEXTBOOK_CORR"]
        v = honesty_verdict(c["expr"], base_m, abls, ci)
        v["expr"] = c["expr"]
        v["core_key"] = core_key(c["expr"])
        v["family"] = c.get("family")
        v["baseline_metrics"] = base_m
        v["coverage"] = (base.get("coverage") if base else None) or c.get("coverage_norank") or c.get(
            "coverage"
        )
        v["n_ablations"] = len(abls)
        v["corr_info"] = {
            "public_corr": ci.get("public_corr"),
            "max_abs_corr": ci.get("max_abs_corr"),
            "max_corr_name": ci.get("max_corr_name"),
            "demote_textbook": ci.get("demote_textbook"),
            "force_control_roe": ci.get("force_control_roe"),
            "flags": ci.get("flags"),
        }
        v["mechanism"] = MECHANISM.get(c["expr"]) or MECHANISM.get(core_key(c["expr"]))
        verdicts.append(v)

    for c in roe_cores:
        base = next(
            (
                r
                for r in results
                if r.get("role") == "primary_roe_control" and r.get("parent") == c["expr"]
            ),
            None,
        )
        base_m = (base.get("metrics") if base else None) or (c.get("metrics") or {})
        ci = dict(corr_by_expr.get(c["expr"]) or {})
        ci["force_control_roe"] = True
        v = honesty_verdict(c["expr"], base_m, [], ci)
        # force control verdict even if honesty would survive
        v["verdict"] = "CONTROL_ONLY_ROE"
        v["enter_shortlist_v2d"] = False
        v["survive_honesty"] = False
        if "roe_textbook_shell_control_only" not in (v.get("hard_fails") or []):
            v["hard_fails"] = list(v.get("hard_fails") or []) + [
                "roe_textbook_shell_control_only"
            ]
        v["expr"] = c["expr"]
        v["core_key"] = core_key(c["expr"])
        v["family"] = c.get("family")
        v["baseline_metrics"] = base_m
        v["coverage"] = (base.get("coverage") if base else None) or c.get("coverage")
        v["n_ablations"] = 0
        v["corr_info"] = {
            "public_corr": ci.get("public_corr"),
            "max_abs_corr": ci.get("max_abs_corr"),
            "max_corr_name": ci.get("max_corr_name"),
            "demote_textbook": ci.get("demote_textbook"),
            "force_control_roe": True,
            "flags": list(ci.get("flags") or []),
        }
        v["mechanism"] = MECHANISM.get("roe_pit")
        verdicts.append(v)

    n_after_mech = (
        sum(1 for x in main_ledger.read_text().splitlines() if x.strip())
        if main_ledger.exists()
        else 0
    )

    # Build v2d: v2c keepers + surviving gm cores
    v2d_members = []
    for m in v2c:
        row = {
            **m,
            "source": m.get("source") or "v2c",
            "on_shortlist_v2d": True,
            "tag": m.get("coverage_tag") or m.get("tag") or "",
        }
        v2d_members.append(row)

    demoted_list = []
    failed_list = []
    gm_new = []
    for v in verdicts:
        if v.get("enter_shortlist_v2d"):
            twins = [g for g in gm_rows if core_key(g["expr"]) == v["core_key"]]
            best = max(
                twins or [v],
                key=lambda r: (r.get("metrics") or v.get("baseline_metrics") or {}).get(
                    "imp60_p25"
                )
                or -1,
            )
            expr = best.get("expr") if isinstance(best, dict) and "expr" in best else v["expr"]
            metrics = (best.get("metrics") if best is not v else None) or v.get("baseline_metrics")
            cov = None
            if isinstance(best, dict):
                cov = best.get("coverage_norank") or best.get("coverage")
            cov = cov or v.get("coverage")
            ci = v.get("corr_info") or {}
            tag = f"corr_ok;max|{fmt_f(ci.get('max_abs_corr'), 2)}|"
            if math.isfinite(ci.get("max_abs_corr") or float("nan")) and (
                ci.get("max_abs_corr") or 0
            ) > 0.4:
                tag += ";near_textbook"
            row = {
                "source": "L1g_GM_SURVIVE",
                "role": "l1g_gm_survive",
                "expr": expr,
                "family": v.get("family"),
                "metrics": metrics,
                "coverage": cov,
                "corr_info": ci,
                "verdict": "SURVIVE",
                "tag": tag,
                "promotion_approved": False,
                "trial_kind": "explore_gate",
                "on_shortlist_v2d": True,
                "core_key": v["core_key"],
                "honesty": {
                    "hard_fails": v.get("hard_fails"),
                    "soft_passes": v.get("soft_passes"),
                    "flags": v.get("flags"),
                    "notes": v.get("notes"),
                },
            }
            v2d_members.append(row)
            gm_new.append(row)
        elif v.get("verdict") == "DEMOTE_TEXTBOOK":
            demoted_list.append(
                {
                    "expr": v["expr"],
                    "metrics": v.get("baseline_metrics"),
                    "corr_info": v.get("corr_info"),
                    "verdict": "DEMOTE_TEXTBOOK",
                    "family": v.get("family"),
                    "hard_fails": v.get("hard_fails"),
                    "notes": v.get("notes"),
                }
            )
        elif v.get("verdict") == "CONTROL_ONLY_ROE":
            pass  # listed separately
        else:
            failed_list.append(v)

    n_before_v2d = n_after_mech
    v2d_ledger = OUT_V2D / "ledger_run.jsonl"
    if v2d_ledger.exists():
        v2d_ledger.unlink()
    for m in gm_new:
        fit = (m.get("metrics") or {}).get("imp60_p25")
        notes = (
            "l1g_shortlist_v2d;enter_main;process_not_sealed;promotion_approved=false;"
            f"corr_ok;verdict={m.get('verdict')}"
        )
        for path in (main_ledger, v2d_ledger):
            append_attempt(
                engine="l1g_shortlist_v2d",
                seed=SEED,
                universe="midlarge_top1500_or_csi300_500",
                cost=0.0025,
                window="explore_20240603_to_latest_shortlist_v2d",
                expr_str=m["expr"],
                fitness=fit if isinstance(fit, float) and math.isfinite(fit) else None,
                notes=notes,
                path=path,
            )
    for d in demoted_list:
        append_attempt(
            engine="l1g_shortlist_v2d",
            seed=SEED,
            universe="midlarge_top1500_or_csi300_500",
            cost=0.0025,
            window="explore_20240603_to_latest_shortlist_v2d",
            expr_str=d["expr"],
            fitness=(d.get("metrics") or {}).get("imp60_p25"),
            notes="l1g_shortlist_v2d;DEMOTE_TEXTBOOK;control_only;promotion_approved=false",
            path=main_ledger,
        )
    for c in roe_cores:
        append_attempt(
            engine="l1g_shortlist_v2d",
            seed=SEED,
            universe="midlarge_top1500_or_csi300_500",
            cost=0.0025,
            window="explore_20240603_to_latest_shortlist_v2d",
            expr_str=c["expr"],
            fitness=(c.get("metrics") or {}).get("imp60_p25"),
            notes="l1g_shortlist_v2d;CONTROL_ONLY_ROE;textbook_shell;promotion_approved=false",
            path=main_ledger,
        )

    n_after = (
        sum(1 for x in main_ledger.read_text().splitlines() if x.strip())
        if main_ledger.exists()
        else 0
    )
    peak = max(peak, mem_mb())

    meta = {
        "mode": "l1g_gm_corr_ablation",
        "promotion_approved": False,
        "sealed_executed": False,
        "trial_kind": "explore_gate",
        "corr_threshold": CORR_THRESHOLD,
        "textbook_panels": list(textbook.keys()),
        "n_gate_ok": len(gate_ok),
        "n_gm_gate_ok": len(gm_rows),
        "n_gm_cores": len(gm_cores),
        "n_roe_control_cores": len(roe_cores),
        "n_jobs": len(jobs),
        "n_demote_textbook": len(demoted_list),
        "n_fail_ablation": len(failed_list),
        "n_survive_cores": sum(1 for v in verdicts if v.get("enter_shortlist_v2d")),
        "n_gm_new_on_v2d": len(gm_new),
        "n_v2c_keepers": len(v2c),
        "n_v2d_members": len(v2d_members),
        "roe_gap": {k: v for k, v in (roe_gap or {}).items() if not isinstance(v, (pd.DataFrame,))},
        "ocf_gap": ocf_gap,
        "fsr_gap": fsr_gap,
        "dv_gap": dv_gap,
        "ledger_N_before": n_before,
        "ledger_N_after": n_after,
        "ledger_N_new": n_after - n_before,
        "ledger_N_before_v2d": n_before_v2d,
        "ledger_N_v2d_new": n_after - n_before_v2d,
        "peak_rss_MB": round(peak),
        "mem_cap_MB": MEM_CAP_MB,
        "under_mem_cap": peak < MEM_CAP_MB,
        "runtime_s": round(time.time() - t0, 1),
        "suggest_sealed": False,
    }

    results_light = []
    for r in results:
        rr = {k: v for k, v in r.items() if k not in ("factor", "sim")}
        if isinstance(r.get("sim"), dict) and r["sim"].get("error"):
            rr["sim_error"] = r["sim"]["error"]
        results_light.append(rr)

    (OUT_MECH / "corr_screen.json").write_text(
        json.dumps(clean(corr_rows), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_MECH / "verdicts.json").write_text(
        json.dumps(clean(verdicts), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_MECH / "results.json").write_text(
        json.dumps(clean(results_light), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_MECH / "demoted_textbook.json").write_text(
        json.dumps(clean(demoted_list), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_MECH / "gm_cores.json").write_text(
        json.dumps(clean(gm_cores), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_MECH / "roe_controls.json").write_text(
        json.dumps(clean(roe_rows), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_MECH / "summary.json").write_text(
        json.dumps(clean(meta), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_mech_report(
        gate_ok, gm_cores, roe_rows, corr_rows, verdicts, results_light, meta
    )

    (OUT_V2D / "shortlist_v2d.json").write_text(
        json.dumps(clean(v2d_members), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_V2D / "demoted_textbook.json").write_text(
        json.dumps(clean(demoted_list), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_V2D / "failed_ablation.json").write_text(
        json.dumps(clean(failed_list), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_V2D / "roe_controls.json").write_text(
        json.dumps(clean(roe_rows), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_V2D / "summary.json").write_text(
        json.dumps(clean(meta), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_v2d_report(v2d_members, demoted_list, failed_list, roe_rows, meta)

    # clear demote/survive/v2d tables in stdout
    print("\n===== DEMOTE_TEXTBOOK =====", flush=True)
    for d in demoted_list:
        print(
            d["expr"],
            fmt_pct((d.get("metrics") or {}).get("imp60_p25")),
            (d.get("corr_info") or {}).get("max_corr_name"),
            fmt_f((d.get("corr_info") or {}).get("max_abs_corr"), 3),
            flush=True,
        )
    print("\n===== SURVIVE → v2d =====", flush=True)
    for m in gm_new:
        print(
            m["expr"],
            fmt_pct((m.get("metrics") or {}).get("imp60_p25")),
            m.get("tag"),
            flush=True,
        )
    print("\n===== FAIL =====", flush=True)
    for f in failed_list:
        print(f.get("expr"), f.get("hard_fails"), flush=True)
    print("\n===== v2d MEMBERS =====", flush=True)
    for i, m in enumerate(v2d_members, 1):
        print(
            i,
            m.get("source"),
            m.get("expr"),
            fmt_pct((m.get("metrics") or {}).get("imp60_p25")),
            flush=True,
        )

    log(
        "DONE",
        "gm_cores",
        len(gm_cores),
        "SURVIVE",
        meta["n_survive_cores"],
        "DEMOTE",
        meta["n_demote_textbook"],
        "FAIL",
        meta["n_fail_ablation"],
        "v2d",
        meta["n_v2d_members"],
        "N",
        n_after,
        "peak",
        peak,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
