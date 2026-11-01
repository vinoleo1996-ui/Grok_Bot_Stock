#!/usr/bin/env python3
"""AI Factor L1 dry-run / explore entrypoint (plan-aligned).

DEFAULT: --synthetic-smoke (no market data).
Real explore: LEO_AI_FACTOR_EXPLORE_OK=1 ... --explore-real
Never runs sealed. Never runs V3-A1.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import resource
import sys
import time
import traceback
import types
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/workspace/QuantLab")
SCRATCH = Path("/workspace/scratch/tic")
V2 = ROOT / "data/v2"
EXPLORE_START = pd.Timestamp("2024-06-03")
SEALED_END = pd.Timestamp("2024-05-31")  # never use sealed labels for search
LOOKBACK_START = pd.Timestamp("2024-01-02")  # feature warm-up only
MAX_EVALUATIONS = 280  # prestate in run meta
TOP_K = 20
COST = 0.0025
SEED = 20261011


def mem_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


def _load_ai_factory():
    """Load ops + ai_factory without executing quantlab.factors.__init__."""
    if "quantlab" not in sys.modules:
        q = types.ModuleType("quantlab")
        q.__path__ = [str(ROOT / "quantlab")]
        sys.modules["quantlab"] = q
    if "quantlab.factors" not in sys.modules or not hasattr(sys.modules["quantlab.factors"], "__path__"):
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
    load("quantlab.factors.ai_factory.ledger", ROOT / "quantlab/factors/ai_factory/ledger.py")
    load("quantlab.factors.ai_factory.fitness", ROOT / "quantlab/factors/ai_factory/fitness.py")
    load("quantlab.factors.ai_factory.evaluate", ROOT / "quantlab/factors/ai_factory/evaluate.py")
    load("quantlab.factors.ai_factory.search", ROOT / "quantlab/factors/ai_factory/search.py")
    return (
        sys.modules["quantlab.factors.ai_factory.search"],
        sys.modules["quantlab.factors.ai_factory.evaluate"],
        sys.modules["quantlab.factors.ai_factory.fitness"],
        sys.modules["quantlab.factors.ops"],
    )


# --- Chinese gloss / who-pays ---
_LEAF_ZH = {
    "ret_1": "1日收益",
    "ret_5": "5日收益",
    "ret_20": "20日收益",
    "log_price": "对数价格",
    "log_vol": "对数成交额",
    "turnover": "换手率",
    "amihud": "Amihud非流动性",
    "vol_20": "20日波动",
    "skew_20": "20日收益偏度",
    "max_ret_20": "20日最大单日涨幅",
    "gap": "隔夜跳空",
    "limit_up_flag": "涨停标记",
    "limit_down_flag": "跌停标记",
    "turn_20": "20日均换手",
    "rv_20": "20日已实现波动",
    "resid_ret_20": "20日残差动量代理",
    "size": "对数流通市值",
}
_OP_ZH = {
    "add": "加",
    "sub": "减",
    "mul": "乘",
    "div": "除",
    "neg": "取负",
    "abs": "绝对值",
    "rank": "截面排名",
    "zscore": "截面标准化",
    "industry_neutral": "行业中性(桩)",
    "size_neutral": "市值中性(桩)",
}


def gloss_zh(expr_str: str) -> str:
    s = expr_str
    for k, v in sorted(_OP_ZH.items(), key=lambda kv: -len(kv[0])):
        s = s.replace(k, v)
    for k, v in sorted(_LEAF_ZH.items(), key=lambda kv: -len(kv[0])):
        s = s.replace(k, v)
    for k in (5, 10, 20, 1):
        s = s.replace(f"delay_{k}", f"滞后{k}日")
        s = s.replace(f"ts_mean_{k}", f"{k}日时序均值")
        s = s.replace(f"ts_std_{k}", f"{k}日时序波动")
        s = s.replace(f"ts_delta_{k}", f"{k}日时序差分")
        s = s.replace(f"ts_max_{k}", f"{k}日时序最大")
    return s


def who_pays_hypothesis(expr_str: str, metrics: dict) -> str:
    e = expr_str.lower()
    bits = []
    if any(x in e for x in ("turn", "amihud", "log_vol")):
        bits.append("流动性提供者/被迫交易者支付冲击溢价（若方向为低换手/低非流动做多）")
    if any(x in e for x in ("ret_20", "ret_5", "resid_ret", "max_ret")):
        bits.append("短期过度反应后的均值回归，或动量延续——由行为偏差交易对手支付")
    if any(x in e for x in ("rv_20", "vol_20", "skew")):
        bits.append("风险厌恶资金回避高波标的，低波溢价由追求彩票型收益者支付")
    if "gap" in e:
        bits.append("隔夜信息消化不完全，日间流动性提供方赚取跳空纠偏")
    if "rank" in e or "zscore" in e:
        bits.append("截面相对定价错误由被动/基准约束资金缓慢纠正")
    if not bits:
        bits.append("机制不明——按预注册不得单独晋级密封")
    ic = metrics.get("ic_mean")
    if ic is not None and isinstance(ic, (int, float)) and np.isfinite(ic) and ic < 0:
        bits.append("探索窗 IC 为负：若符号未翻转则更可能是反转边，需在注释中写清")
    return "；".join(bits)


def run_smoke_inline() -> dict:
    search_mod, eval_mod, _fit_mod, ops_mod = _load_ai_factory()
    GPConfig, gp_search = search_mod.GPConfig, search_mod.gp_search
    align_open_open_label = eval_mod.align_open_open_label
    assert_no_lookahead_label = eval_mod.assert_no_lookahead_label
    walk_forward_ic = eval_mod.walk_forward_ic
    apply_expr, parse_expr = ops_mod.apply_expr, ops_mod.parse_expr

    smoke_ledger = ROOT / "output/ai_factor/ledger_smoke.jsonl"
    topk_dir = ROOT / "output/ai_factor/gp_smoke"
    if smoke_ledger.exists():
        smoke_ledger.unlink()

    rng = np.random.default_rng(0)
    dates = pd.bdate_range("2020-01-01", periods=80)
    cols = [f"a{i:02d}" for i in range(30)]
    rets = rng.normal(0, 0.01, size=(80, 30))
    open_px = pd.DataFrame(100 * np.cumprod(1 + rets, axis=0), index=dates, columns=cols)
    close = open_px * (1 + rng.normal(0, 0.002, size=open_px.shape))
    ret_1 = close.pct_change()
    panels = {
        "ret_1": ret_1,
        "ret_5": close.pct_change(5),
        "ret_20": close.pct_change(20),
        "log_vol": np.log(ret_1.abs() * 1e6 + 1),
        "turn_20": ret_1.abs().rolling(20).mean(),
        "rv_20": ret_1.rolling(20).std(),
        "resid_ret_20": ret_1.rolling(20).mean(),
    }
    label = align_open_open_label(open_px)
    assert_no_lookahead_label(open_px, label)

    cfg = GPConfig(
        population=8,
        generations=2,
        max_evaluations=20,
        top_k=5,
        seed=42,
        window="synthetic_smoke",
        ledger_path=smoke_ledger,
        top_n=8,
        lambda_turnover=0.5,
    )
    res = gp_search(panels, label, cfg)
    assert res.promotion_approved is False
    assert res.evaluations > 0
    lines = [json.loads(x) for x in smoke_ledger.read_text().splitlines() if x.strip()]
    assert len(lines) == res.evaluations
    assert lines[-1]["N"] == len(lines)
    assert all(r.get("promotion_approved") is False for r in lines)

    topk_dir.mkdir(parents=True, exist_ok=True)
    rows = [c.as_row() for c in res.top_k]
    (topk_dir / "top_k.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False))
    if res.top_k:
        walk_forward_ic(res.top_k[0].expr, panels, label, list(dates[:50]))

    e = parse_expr(("op", "rank", ("leaf", "ret_1")))
    out = apply_expr(e, panels)
    assert out.shape == panels["ret_1"].shape

    return {
        "mode": "synthetic_smoke",
        "ok": True,
        "evaluations": res.evaluations,
        "top_k_n": len(res.top_k),
        "ledger_N": lines[-1]["N"],
        "promotion_approved": False,
        "peak_rss_MB": round(mem_mb()),
        "topk": str(topk_dir / "top_k.json"),
        "ledger": str(smoke_ledger),
        "prereg": "docs/prereg/AI_FACTOR_L1.md",
        "plan": "/workspace/QuantLab-AI_FACTOR_MINING_PLAN_ZH.md",
    }


def _ashare_cols(all_names: list[str]) -> list[str]:
    return [
        c
        for c in all_names
        if (
            c[:6] in ("sh.600", "sh.601", "sh.603", "sh.605", "sh.688", "sh.689")
            or c[:5] in ("sz.00", "sz.30")
        )
    ]


def _load_midlarge_explore_panels():
    """Load PIT mid/large panels for explore window only (labels ≥2024-06-03).

    Sealed 2018-01→2024-05 labels are NEVER used for search/fitness.
    """
    import gc
    import pyarrow.parquet as pq

    t0 = time.time()
    log = lambda *a: print(f"[explore {time.time()-t0:5.0f}s {mem_mb():.0f}MB]", *a, flush=True)

    schema = pq.read_schema(SCRATCH / "close.parquet")
    ash = _ashare_cols(list(schema.names))
    log("ashare cols", len(ash))

    # float mktcap from lookback start
    fm_long = pd.read_parquet(
        V2 / "float_mktcap/float_mktcap_daily_tushare.parquet",
        columns=["trade_date", "instrument_id", "float_mktcap"],
        filters=[("trade_date", ">=", LOOKBACK_START)],
    )
    fm_long["trade_date"] = pd.to_datetime(fm_long["trade_date"])
    rk = fm_long.groupby("trade_date")["float_mktcap"].rank(ascending=False)
    keep = set(fm_long.loc[rk <= 1800, "instrument_id"])

    iw = pd.read_parquet(V2 / "index_members/index_weight_csi300_500_1000.parquet")
    iw = iw[iw.index_code.isin(["000300.SH", "000905.SH"])]
    iw = iw[pd.to_datetime(iw.trade_date) >= LOOKBACK_START]
    ix = set(iw.con_code.str[-2:].str.lower() + "." + iw.con_code.str[:6])
    del iw
    cols = sorted((keep | ix) & set(ash))
    log("midlarge candidate cols", len(cols))

    def ld(name: str) -> pd.DataFrame:
        df = pd.read_parquet(SCRATCH / f"{name}.parquet", columns=cols).astype("float32")
        df = df.loc[df.index >= LOOKBACK_START]
        return df

    cl = ld("close")
    op = ld("open")
    fa = ld("factor").ffill()
    amt = ld("amount")
    tov = ld("turnover")
    ts = ld("tradestatus")
    st = ld("is_st_at_open")
    log("price panels", cl.shape)

    aC = (cl * fa).astype("float32")
    aO = (op * fa).astype("float32")
    del fa, op, cl
    gc.collect()

    # pivot float mktcap to wide
    fm = (
        fm_long[fm_long.instrument_id.isin(cols)]
        .drop_duplicates(["trade_date", "instrument_id"], keep="last")
        .set_index(["trade_date", "instrument_id"])["float_mktcap"]
        .unstack()
        .reindex(index=aC.index, columns=cols)
        .astype("float32")
    )
    del fm_long
    gc.collect()

    # daily universe mask: top1500 float OR CSI300/500 member proxy via keep set;
    # recompute rank on loaded cols
    rk_w = fm.rank(axis=1, ascending=False)
    tradable = (ts == 1) & aC.notna() & (st != 1) & fm.notna()
    uni = tradable & (rk_w <= 1500)
    # also allow names in ix that are tradable even if rank>1500 (CSI)
    for c in cols:
        if c in ix:
            uni[c] = uni[c] | (tradable[c] & fm[c].notna())
    log("universe mean n", float(uni.sum(axis=1).mean()))

    ret = aC.pct_change(fill_method=None)
    panels: dict[str, pd.DataFrame] = {}
    panels["ret_1"] = ret.astype("float32")
    panels["ret_5"] = aC.pct_change(5, fill_method=None).astype("float32")
    panels["ret_20"] = aC.pct_change(20, fill_method=None).astype("float32")
    panels["log_vol"] = np.log(amt.where(amt > 0)).astype("float32")
    panels["turnover"] = tov.astype("float32")
    panels["turn_20"] = tov.rolling(20, min_periods=10).mean().astype("float32")
    panels["rv_20"] = ret.rolling(20, min_periods=10).std().astype("float32")
    panels["vol_20"] = panels["rv_20"]
    panels["amihud"] = (
        (ret.abs() / amt.replace(0, np.nan) * 1e9).rolling(20, min_periods=10).mean().astype("float32")
    )
    panels["max_ret_20"] = ret.rolling(20, min_periods=10).max().astype("float32")
    panels["gap"] = (aO / aC.shift(1) - 1.0).astype("float32")
    panels["resid_ret_20"] = ret.rolling(20, min_periods=10).mean().astype("float32")
    panels["size"] = np.log(fm.where(fm > 0)).astype("float32")
    # skew approx
    panels["skew_20"] = ret.rolling(20, min_periods=10).skew().astype("float32")

    # mask non-universe to NaN so IC/search only mid/large
    for k in list(panels.keys()):
        panels[k] = panels[k].where(uni)

    from quantlab.factors.ai_factory.evaluate import align_open_open_label, assert_no_lookahead_label

    label_full = align_open_open_label(aO)
    assert_no_lookahead_label(aO, label_full)
    # CRITICAL: only explore-window labels for search (no sealed)
    label = label_full.where(uni)
    label = label.loc[label.index >= EXPLORE_START]
    # align panels to same dates for apply (keep lookback rows for ts ops, but
    # fitness only scores dates present in label)
    for k in panels:
        panels[k] = panels[k].loc[panels[k].index >= LOOKBACK_START]

    # drop helper size from leaf search? keep as leaf for kill-line corr check only
    size_panel = panels.pop("size")

    meta = {
        "n_cols": len(cols),
        "n_dates_panel": int(len(next(iter(panels.values())))),
        "n_label_dates": int(label.dropna(how="all").shape[0]),
        "explore_start": str(EXPLORE_START.date()),
        "lookback_start": str(LOOKBACK_START.date()),
        "sealed_untouched": True,
        "sealed_end": str(SEALED_END.date()),
        "mean_universe_n": float(uni.loc[uni.index >= EXPLORE_START].sum(axis=1).mean()),
        "peak_rss_MB_load": round(mem_mb()),
    }
    log("panels ready", meta)
    del aC, aO, amt, tov, ts, st, ret, fm, rk_w, tradable, uni
    gc.collect()
    return panels, label, size_panel, meta


def _explore_gate(top_rows: list[dict], size_corrs: list[float]) -> dict:
    """Process-only gate for whether to ask Leo for sealed later."""
    reasons = []
    ok = True
    if not top_rows:
        return {"passed": False, "reasons": ["no_topk"], "promotion_approved": False}
    best = top_rows[0]
    m = best.get("metrics") or {}
    icir = best.get("train_icir")
    ic_mean = m.get("ic_mean")
    ann_net = m.get("ann_net")
    turn = m.get("turnover")
    sc = size_corrs[0] if size_corrs else float("nan")

    if icir is None or not np.isfinite(icir) or icir < 0.3:
        ok = False
        reasons.append(f"icir_below_0.3 ({icir})")
    if ic_mean is None or not np.isfinite(ic_mean) or abs(ic_mean) < 0.01:
        ok = False
        reasons.append(f"abs_ic_mean_below_0.01 ({ic_mean})")
    if ann_net is None or not np.isfinite(ann_net) or ann_net <= 0:
        ok = False
        reasons.append(f"ann_net_nonpositive ({ann_net})")
    if np.isfinite(sc) and abs(sc) >= 0.8:
        ok = False
        reasons.append(f"size_corr_ge_0.8 ({sc})")
    if turn is not None and np.isfinite(turn) and turn > 0.6:
        ok = False
        reasons.append(f"turnover_too_high ({turn})")
    if ok:
        reasons.append("process_gate_ok_not_a_sealed_pass")
    return {
        "passed": bool(ok),
        "reasons": reasons,
        "promotion_approved": False,
        "note": "Explore gate only; sealed requires separate Leo approval and prereg freeze",
    }


def cmd_explore_real() -> dict:
    if os.environ.get("LEO_AI_FACTOR_EXPLORE_OK") != "1":
        return {
            "mode": "explore_real_blocked",
            "sealed_executed": False,
            "explore_executed": False,
            "error": "Set LEO_AI_FACTOR_EXPLORE_OK=1 only after Leo confirms in Alpha chat.",
            "promotion_approved": False,
        }

    t0 = time.time()
    search_mod, eval_mod, fit_mod, ops_mod = _load_ai_factory()
    GPConfig, gp_search = search_mod.GPConfig, search_mod.gp_search
    corr_with_panel = fit_mod.corr_with_panel
    apply_expr = ops_mod.apply_expr

    ledger = ROOT / "output/ai_factor/ledger.jsonl"
    topk_dir = ROOT / "output/ai_factor/gp_explore"
    topk_dir.mkdir(parents=True, exist_ok=True)
    report_path = ROOT / "output/alpha/AI_FACTOR_L1_EXPLORE_ZH.md"

    # clear prior explore rows? append-only ledger — start fresh file for this run's N
    # Plan: ledger is cumulative. If empty smoke leftover, keep append.
    # For clean N of this explore run, write run-local and also append to main.
    run_ledger = topk_dir / "ledger_explore_run.jsonl"
    if run_ledger.exists():
        run_ledger.unlink()

    panels, label, size_panel, load_meta = _load_midlarge_explore_panels()
    peak = mem_mb()

    run_meta = {
        "mode": "explore_real",
        "leo_approval": "批准 AI 因子工厂 v1 真实探索窗",
        "leo_approval_chat": "Alpha",
        "leo_approval_date": "2026-10-11",
        "max_evaluations_prestate": MAX_EVALUATIONS,
        "population": 40,
        "generations": 8,
        "top_k": TOP_K,
        "cost_one_way": COST,
        "seed": SEED,
        "universe": "midlarge_top1500_or_csi300_500",
        "window": "explore_20240603_to_latest",
        "sealed_window_used_for_labels": False,
        "promotion_approved": False,
        "load_meta": load_meta,
    }
    (topk_dir / "run_meta.json").write_text(json.dumps(run_meta, indent=2, ensure_ascii=False))

    cfg = GPConfig(
        population=40,
        generations=8,
        max_evaluations=MAX_EVALUATIONS,
        top_k=TOP_K,
        seed=SEED,
        universe="midlarge_top1500_or_csi300_500",
        cost=COST,
        window="explore_20240603_to_latest",
        ledger_path=run_ledger,
        lambda_complexity=0.015,
        lambda_turnover=1.0,
        top_n=50,
    )
    print(
        json.dumps(
            {"event": "gp_search_start", "max_evaluations": MAX_EVALUATIONS, "promotion_approved": False},
            ensure_ascii=False,
        ),
        flush=True,
    )
    res = gp_search(panels, label, cfg)
    peak = max(peak, mem_mb())
    assert res.promotion_approved is False
    assert res.max_evaluations == MAX_EVALUATIONS

    # append run ledger into main ledger with continuing N
    main_lines_before = 0
    if ledger.exists():
        main_lines_before = sum(1 for x in ledger.read_text().splitlines() if x.strip())
    from quantlab.factors.ai_factory.ledger import append_attempt

    run_rows = [json.loads(x) for x in run_ledger.read_text().splitlines() if x.strip()]
    for r in run_rows:
        append_attempt(
            engine=r["engine"],
            seed=r["seed"],
            universe=r["universe"],
            cost=r["cost"],
            window=r["window"],
            expr_str=r.get("expr_str", ""),
            fitness=r.get("fitness"),
            notes=r.get("notes", "") + ";explore_real_20261011",
            path=ledger,
        )
    main_N = main_lines_before + len(run_rows)

    # annotate Top-K with gloss / who-pays / size corr
    top_rows = []
    size_corrs = []
    for c in res.top_k:
        fac = apply_expr(c.expr, panels)
        # size corr on explore dates only
        sc = corr_with_panel(fac.loc[fac.index >= EXPLORE_START], size_panel.loc[size_panel.index >= EXPLORE_START])
        size_corrs.append(sc)
        row = c.as_row()
        row["gloss_zh"] = gloss_zh(c.expr.to_str())
        row["who_pays_zh"] = who_pays_hypothesis(c.expr.to_str(), c.metrics or {})
        row["size_corr"] = sc
        row["promotion_approved"] = False
        top_rows.append(row)

    (topk_dir / "top_k.json").write_text(json.dumps(top_rows, indent=2, ensure_ascii=False, default=str))

    gate = _explore_gate(top_rows, size_corrs)
    peak = max(peak, mem_mb())

    # Chinese report
    lines = []
    lines.append("# AI 因子工厂 L1 — 真实探索窗报告")
    lines.append("")
    lines.append(f"- 日期：2026-10-11（美东）｜`promotion_approved=false`")
    lines.append(f"- Leo 批准（Alpha 聊天）：「批准 AI 因子工厂 v1 真实探索窗」")
    lines.append(f"- 对齐：`/workspace/QuantLab-AI_FACTOR_MINING_PLAN_ZH.md` + `docs/prereg/AI_FACTOR_L1.md`")
    lines.append(f"- 窗口：探索 **{EXPLORE_START.date()} → latest**；密封 2018-01～2024-05 **未用于标签/搜索**")
    lines.append(f"- 宇宙：流通市值前 1500 或沪深300/中证500；禁小盘主线")
    lines.append(f"- 预声明 `max_evaluations` **N_cap={MAX_EVALUATIONS}**；本跑实际评估次数 **N={res.evaluations}**")
    lines.append(f"- 成本进适应度：单边 {COST*1e4:.0f}bp + 换手惩罚；持仓 top50 等权代理")
    lines.append(f"- 峰值内存：约 **{peak:.0f} MB**（硬约束 <2500MB）")
    lines.append(f"- 账本：`output/ai_factor/ledger.jsonl`（累计 N≈{main_N}）；本跑明细 `{run_ledger}`")
    lines.append(f"- Top-K：`output/ai_factor/gp_explore/top_k.json`")
    lines.append("")
    lines.append("## 本周 KPI")
    lines.append("管线通、账本计次、Top-K 表达式——**不是**公开策略年化作标题。下列 IC/净收益仅作过程指标。")
    lines.append("")
    lines.append("## Top-K 摘要（最多 10 条展示）")
    lines.append("")
    lines.append("| # | 表达式 | 中文释义 | ICIR | IC均值 | 估年化净(过程) | 换手 | 市值相关 | 谁在付钱 |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(top_rows[:10], 1):
        m = r.get("metrics") or {}
        lines.append(
            f"| {i} | `{r['expr']}` | {r.get('gloss_zh','')} | "
            f"{r.get('train_icir', float('nan')):.3f} | {m.get('ic_mean', float('nan')):.4f} | "
            f"{m.get('ann_net', float('nan')):.2%} | {m.get('turnover', float('nan')):.2f} | "
            f"{r.get('size_corr', float('nan')):.2f} | {r.get('who_pays_zh','')[:40]} |"
        )
    lines.append("")
    lines.append("## 探索闸门（过程，非正式晋级）")
    lines.append(f"- **passed={gate['passed']}**")
    for reason in gate["reasons"]:
        lines.append(f"- {reason}")
    lines.append("- 即使 passed，密封窗仍须另开预注册冻结 + Leo 在 Alpha 聊天单独批准。")
    lines.append("")
    lines.append("## Kill-line 对照")
    lines.append("- 无计次：否（已写入 ledger）")
    lines.append("- 触碰密封标签：否")
    lines.append("- 小盘主线：否")
    lines.append("- 高杠杆：否")
    lines.append(f"- size/liquidity 相关过高：见 Top-K size_corr；闸门阈值 |ρ|≥0.8")
    lines.append("- LGBM 基线对照：本跑未跑（骨架占位）；正式密封前须补")
    lines.append("")
    lines.append("## 未做")
    lines.append("- 未跑 AI 密封窗")
    lines.append("- 未跑 V3-A1 持有层密封")
    lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")

    out = {
        "mode": "explore_real",
        "ok": True,
        "promotion_approved": False,
        "sealed_executed": False,
        "explore_executed": True,
        "max_evaluations_prestate": MAX_EVALUATIONS,
        "N": res.evaluations,
        "ledger_cumulative_N": main_N,
        "top_k_n": len(top_rows),
        "top_k_summary": [
            {
                "expr": r["expr"],
                "gloss_zh": r.get("gloss_zh"),
                "icir": r.get("train_icir"),
                "ann_net": (r.get("metrics") or {}).get("ann_net"),
                "size_corr": r.get("size_corr"),
            }
            for r in top_rows[:5]
        ],
        "explore_gate": gate,
        "peak_rss_MB": round(peak),
        "runtime_s": round(time.time() - t0, 1),
        "paths": {
            "topk": str(topk_dir / "top_k.json"),
            "run_meta": str(topk_dir / "run_meta.json"),
            "ledger": str(ledger),
            "run_ledger": str(run_ledger),
            "report": str(report_path),
            "prereg": str(ROOT / "docs/prereg/AI_FACTOR_L1.md"),
        },
        "load_meta": load_meta,
    }
    (topk_dir / "summary.json").write_text(json.dumps(out, indent=2, ensure_ascii=False, default=str))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--synthetic-smoke", action="store_true", default=True)
    g.add_argument("--explore-real", action="store_true")
    args = ap.parse_args(argv)
    try:
        if args.explore_real:
            res = cmd_explore_real()
            code = 2 if res.get("error") else 0
        else:
            res = run_smoke_inline()
            code = 0
    except Exception as exc:  # noqa: BLE001
        res = {
            "mode": "error",
            "ok": False,
            "error": str(exc),
            "trace": traceback.format_exc(),
            "promotion_approved": False,
            "peak_rss_MB": round(mem_mb()),
        }
        code = 1
    print(json.dumps(res, indent=2, ensure_ascii=False, default=str))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
