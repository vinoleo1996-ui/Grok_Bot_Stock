#!/usr/bin/env python3
"""AI Factor L1c / QuantMind explore — non-LU main leaves.

Main: consecutive-board height/promote/breadth, limit-DOWN seq, lockup,
      ann title event counts (title_only, no invented body).
Control: pure limit-UP leaves (days_since_lu, lu_streak, ...).
Explore 2024-06→latest, mid/large. No sealed. promotion_approved=False.
Capital tiers 60万/100万. Peak RSS < 2.5GB.
"""
from __future__ import annotations

import gc
import importlib.util
import json
import math
import os
import resource
import sys
import time
import types
import traceback
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/workspace/QuantLab")
SCRATCH = Path("/workspace/scratch/tic")
V2 = ROOT / "data/v2"
OUT_DIR = ROOT / "output/ai_factor/l1c_explore"
REPORT = ROOT / "output/alpha/AI_FACTOR_L1c_EXPLORE_ZH.md"
EXPLORE_START = pd.Timestamp("2024-06-03")
LOOKBACK_START = pd.Timestamp("2024-01-02")
SEALED_END = pd.Timestamp("2024-05-31")
MAX_EVAL_MAIN = 200
MAX_EVAL_CTRL = 40
TOP_K = 15
COST = 0.0025
SEED = 20261012
CAPITALS = (600_000, 1_000_000)
PROMOTION_APPROVED = False
MEM_CAP_MB = 2500

MAIN_LEAVES = (
    "lu_height",
    "mkt_max_height",
    "lu_promote_rate",
    "mkt_lu_breadth",
    "theme_lu_density",
    "limit_down_flag",
    "ld_streak",
    "ld_count_5",
    "days_since_ld",
    "lockup_S_20",
    "ann_n_5",
    "ann_buyback_5",
    "ann_insider_dec_5",
    "ann_penalty_5",
    "ann_earn_signed_5",
    "overnight_ret",
    "on_minus_id",
    "etf_major_flow",
    "etf_theme_flow",
    "if_basis",
    "if_basis_x_on",
)
CTRL_LEAVES = (
    "days_since_lu",
    "lu_streak",
    "limit_up_flag",
    "lu_count_5",
    "etf_flow_x_lu",
    "if_basis_x_lu",
)


def mem_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def log(*a):
    print(f"[l1c {time.time()-t0:5.0f}s {mem_mb():.0f}MB]", *a, flush=True)


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
        if name in sys.modules and hasattr(sys.modules[name], "__file__"):
            # force reload ops/novelty after patch
            pass
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
        "quantmind_loop",
    ):
        load(
            f"quantlab.factors.ai_factory.{name}",
            ROOT / f"quantlab/factors/ai_factory/{name}.py",
        )
    return sys.modules


def _import_l1b():
    path = ROOT / "research/ai_factor_l1b_structural_explore.py"
    spec = importlib.util.spec_from_file_location("ai_factor_l1b_structural_explore", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ai_factor_l1b_structural_explore"] = mod
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


def _days_since(flag: pd.DataFrame) -> pd.DataFrame:
    arr = flag.fillna(False).to_numpy(dtype=bool)
    T, N = arr.shape
    res = np.full((T, N), np.nan, dtype=np.float32)
    last = np.full(N, -1, dtype=np.int32)
    for i in range(T):
        hit = arr[i]
        last[hit] = i
        ok = last >= 0
        res[i, ok] = (i - last[ok]).astype(np.float32)
    return pd.DataFrame(res, index=flag.index, columns=flag.columns)


def build_ann_title_panels(
    index: pd.DatetimeIndex, columns: list[str]
) -> tuple[dict[str, pd.DataFrame], dict]:
    """PIT title event counts from ann_embedding_corpus (title_only). No body invent."""
    path = V2 / "text/ann_embedding_corpus_pit.parquet"
    gap: dict = {
        "path": str(path),
        "body_source": "title_only",
        "embeddings_present": False,
        "invented_body": False,
    }
    if not path.exists():
        gap["ok"] = False
        gap["error"] = "missing_corpus"
        empty = {
            k: pd.DataFrame(np.nan, index=index, columns=columns, dtype="float32")
            for k in (
                "ann_n_5",
                "ann_buyback_5",
                "ann_insider_dec_5",
                "ann_penalty_5",
                "ann_earn_signed_5",
            )
        }
        return empty, gap

    ann = pd.read_parquet(
        path,
        columns=["available_at", "instrument", "event_type", "body_source"],
    )
    ann["available_at"] = pd.to_datetime(ann["available_at"])
    if getattr(ann["available_at"].dt, "tz", None) is not None:
        ann["avail_date"] = ann["available_at"].dt.tz_convert("Asia/Shanghai").dt.normalize().dt.tz_localize(None)
    else:
        ann["avail_date"] = pd.to_datetime(ann["available_at"]).dt.normalize()
    # usable next session after available_at EOD → signal on avail_date+0 calendar then align;
    # conservative: signal_date = avail_date (EOD) → trade next open ≈ use same calendar day
    # for count panels as of that date (known at EOD; label is open→open next so OK for T+1).
    ann["bs"] = ann["instrument"].map(_to_baostock)
    ann = ann[ann["bs"].astype(str).str.len() > 0]
    ann = ann[ann["bs"].isin(columns)]
    ex = ann[ann["avail_date"] >= EXPLORE_START - pd.Timedelta(days=10)]
    gap.update(
        {
            "ok": True,
            "n_rows_all": int(len(ann)),
            "n_rows_explore_plus": int(len(ex)),
            "n_instruments_mapped": int(ann["bs"].nunique()),
            "n_instruments_explore": int(ex["bs"].nunique()),
            "avail_min": str(ann["avail_date"].min().date()) if len(ann) else None,
            "avail_max": str(ann["avail_date"].max().date()) if len(ann) else None,
            "explore_coverage_note": (
                "sparse cross-section: corpus explore-window instruments << midlarge universe; "
                "missing names stay NaN (do not invent)."
            ),
            "body_source_counts": ann["body_source"].value_counts().to_dict()
            if "body_source" in ann.columns
            else {},
        }
    )

    col_index = {c: i for i, c in enumerate(columns)}
    cal = index
    cal_np = cal.values.astype("datetime64[ns]")
    T, N = len(cal), len(columns)

    def empty_arr():
        return np.zeros((T, N), dtype=np.float32)

    n_all = empty_arr()
    n_buy = empty_arr()
    n_ins = empty_arr()
    n_pen = empty_arr()
    n_earn = empty_arr()  # signed: beat +1, miss -1

    # daily counts then rolling 5
    daily = {}
    for row in ann.itertuples(index=False):
        bs = row.bs
        j = col_index.get(bs)
        if j is None:
            continue
        d = pd.Timestamp(row.avail_date)
        i = int(np.searchsorted(cal_np, np.datetime64(d), side="left"))
        if i >= T:
            continue
        if i < T and cal[i] != d:
            # map to next trading day on/after avail
            if i < T and cal_np[i] < np.datetime64(d):
                i += 1
            if i >= T:
                continue
        key = (i, j)
        et = str(row.event_type or "other")
        daily.setdefault(key, {"n": 0, "buy": 0, "ins": 0, "pen": 0, "earn": 0})
        daily[key]["n"] += 1
        if et in ("buyback", "buyback_excluded"):
            daily[key]["buy"] += 1
        if et == "insider_decrease":
            daily[key]["ins"] += 1
        if et == "penalty":
            daily[key]["pen"] += 1
        if et == "earnings_beat":
            daily[key]["earn"] += 1
        elif et == "earnings_miss":
            daily[key]["earn"] -= 1

    for (i, j), v in daily.items():
        n_all[i, j] = v["n"]
        n_buy[i, j] = v["buy"]
        n_ins[i, j] = v["ins"]
        n_pen[i, j] = v["pen"]
        n_earn[i, j] = v["earn"]

    def roll5(a: np.ndarray) -> pd.DataFrame:
        df = pd.DataFrame(a, index=cal, columns=columns, dtype="float32")
        return df.rolling(5, min_periods=1).sum().astype("float32")

    panels = {
        "ann_n_5": roll5(n_all),
        "ann_buyback_5": roll5(n_buy),
        "ann_insider_dec_5": roll5(n_ins),
        "ann_penalty_5": roll5(n_pen),
        "ann_earn_signed_5": roll5(n_earn),
    }
    # where never any ann in lookback window → keep 0 (true zero) not NaN for counted names;
    # names with zero corpus coverage remain 0 everywhere — flag coverage separately
    gap["nonzero_frac_ann_n_5"] = float((panels["ann_n_5"] > 0).mean().mean())
    return panels, gap


def attach_l1c_panels(base_panels, label, public, load_meta):
    """Add easystock + LD extras + ann title counts onto L1b panels."""
    from quantlab.factors.ai_factory.structural_leaves import build_easystock_panels

    lu_flag = (base_panels["limit_up_flag"] > 0.5).astype(bool)
    lu_streak = base_panels["lu_streak"]
    # reconstruct a soft uni mask from non-null overnight
    mask = base_panels["overnight_ret"].notna()
    easy = build_easystock_panels(
        lu_flag=lu_flag.astype("float32"),
        lu_streak=lu_streak,
        mask=mask,
        industry=None,
    )
    for k, v in easy.items():
        base_panels[k] = v.where(mask).astype("float32")

    ld_flag = (base_panels["limit_down_flag"] > 0.5)
    base_panels["ld_count_5"] = (
        ld_flag.astype("float32").rolling(5, min_periods=1).sum().astype("float32").where(mask)
    )
    base_panels["days_since_ld"] = _days_since(ld_flag.astype("float32")).where(mask)

    ann_panels, ann_gap = build_ann_title_panels(
        base_panels["overnight_ret"].index, list(base_panels["overnight_ret"].columns)
    )
    for k, v in ann_panels.items():
        base_panels[k] = v.where(mask).astype("float32")
    load_meta = dict(load_meta)
    load_meta["ann_title_events"] = ann_gap
    load_meta["easystock_leaves"] = list(easy.keys())
    load_meta["l1c_extra_ld"] = ["ld_count_5", "days_since_ld"]
    return base_panels, label, public, load_meta


def who_pays(expr: str) -> str:
    bits = []
    if any(x in expr for x in ("lu_height", "mkt_max_height", "lu_promote", "mkt_lu_breadth", "theme_lu")):
        bits.append("连板/题材情绪：晋级失败的追板资金与被迫隔夜的T+1买家")
    if any(x in expr for x in ("ld_", "limit_down", "days_since_ld")):
        bits.append("跌停序列：恐慌抛售与融券/止损盘；解封时空头回补或继续踩踏")
    if "lockup" in expr:
        bits.append("解禁股东供给，折价由二级多头承接")
    if "ann_" in expr:
        bits.append("公告标题事件后的注意力与合规交易限制令知情/半知情资金重定价")
    if "etf_" in expr:
        bits.append("ETF申赎冲击由股票端流动性承接")
    if "if_basis" in expr or "overnight" in expr or "on_minus" in expr:
        bits.append("期现/隔夜风险在T+1约束下转移给日间流动性提供者")
    if any(x in expr for x in ("days_since_lu", "lu_streak", "limit_up_flag", "lu_count_5")):
        bits.append("【对照臂】纯涨停叶：打板接力断裂时接盘方支付")
    if not bits:
        bits.append("机制未声明")
    return "；".join(bits)


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


def capacity_nets(factor, label, sig, adv, capitals=CAPITALS, top_n=50, flat_bp=25):
    """Flat 25bp + sqrt impact at Leo capital tiers."""
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
    imp = {c: np.full(T, np.nan) for c in capitals}
    prev = None
    K_IMP = 1.0
    COMM = 0.00025
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
        for aum in capitals:
            cost_cny = 0.0
            for j in exited | entered:
                V = w * aum
                cost_cny += COMM * V
                sj, aj = s[t, j], a[t, j]
                if np.isfinite(sj) and np.isfinite(aj) and aj > 0 and V > 0:
                    cost_cny += V * K_IMP * float(sj) * math.sqrt(V / aj)
            imp[aum][t] = cost_cny / aum
        prev = cur
    flat_net = gross - turn_ow * (flat_bp / 1e4)
    out = {
        "flat_25bp": ann_from_daily(flat_net),
        "mean_turn_ow": float(np.nanmean(turn_ow)),
        "icir": float(icir_from_series(daily_rank_ic(factor.reindex(idx), label.reindex(idx)))),
        "impact": {},
    }
    for aum in capitals:
        extra = max(0.0, flat_bp / 1e4 - COMM)
        net = gross - imp[aum] - turn_ow * extra
        out["impact"][str(aum)] = ann_from_daily(net)
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


def eval_expr_list(exprs, panels, label, public, ledger_path, main_ledger, engine, budget):
    from quantlab.factors.ops import apply_expr, parse_expr
    from quantlab.factors.ai_factory.fitness import fitness_score_l1b
    from quantlab.factors.ai_factory.ledger import append_attempt
    from quantlab.factors.ai_factory.novelty import (
        is_l1c_main_expr,
        is_lu_control_expr,
        is_textbook_expr,
        leaves_in_expr_str,
    )

    rows = []
    for es in exprs[:budget]:
        try:
            if isinstance(es, str):
                # parse simple leaf or wrap
                if "(" not in es:
                    expr = parse_expr(("leaf", es))
                else:
                    # use GP-style: only support our seed strings via apply on known forms
                    # fallback: build via leaf if simple
                    expr = parse_expr(_seed_to_tuple(es))
            else:
                expr = parse_expr(es)
            fac = apply_expr(expr, panels)
            met = fitness_score_l1b(
                fac,
                label,
                public_panels=public,
                cost_one_way=COST,
                top_n=50,
                lambda_complexity=0.01,
                n_nodes=expr.n_nodes(),
            )
            s = expr.to_str()
            row = {
                "expr": s,
                "fitness": met.get("fitness"),
                "metrics": met,
                "train_icir": met.get("icir"),
                "n_nodes": expr.n_nodes(),
                "leaves": sorted(leaves_in_expr_str(s)),
                "is_main": is_l1c_main_expr(s),
                "is_lu_control": is_lu_control_expr(s),
                "is_textbook": is_textbook_expr(s),
                "who_pays_zh": who_pays(s),
                "promotion_approved": False,
                "tuple": expr.to_tuple(),
            }
            notes = (
                f"l1c;main={row['is_main']};lu_ctrl={row['is_lu_control']};"
                f"novelty_fail={met.get('novelty_fail')};ann_net={met.get('ann_net')}"
            )
            append_attempt(
                engine=engine,
                seed=SEED,
                universe="midlarge_top1500_or_csi300_500",
                cost=COST,
                window="explore_20240603_to_latest_l1c",
                expr_str=s,
                fitness=met.get("fitness"),
                notes=notes,
                path=ledger_path,
            )
            append_attempt(
                engine=engine,
                seed=SEED,
                universe="midlarge_top1500_or_csi300_500",
                cost=COST,
                window="explore_20240603_to_latest_l1c",
                expr_str=s,
                fitness=met.get("fitness"),
                notes=notes + ";l1c_20261012",
                path=main_ledger,
            )
            rows.append(row)
        except Exception as exc:  # noqa: BLE001
            log("eval_fail", es, type(exc).__name__, str(exc)[:120])
    return rows


def _seed_to_tuple(s: str):
    """Minimal parser for seed strings used in this script."""
    s = s.strip()
    # leaf
    if s.isidentifier():
        return ("leaf", s)
    # neg(x)
    import re

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
    m = re.fullmatch(r"ts_delta_5\((.+)\)", s)
    if m:
        return ("op", "ts_delta_5", _seed_to_tuple(m.group(1)))
    m = re.fullmatch(r"mul\((.+),(.+)\)", s)
    if m:
        return ("op", "mul", _seed_to_tuple(m.group(1).strip()), _seed_to_tuple(m.group(2).strip()))
    m = re.fullmatch(r"add\((.+),(.+)\)", s)
    if m:
        return ("op", "add", _seed_to_tuple(m.group(1).strip()), _seed_to_tuple(m.group(2).strip()))
    m = re.fullmatch(r"sub\((.+),(.+)\)", s)
    if m:
        return ("op", "sub", _seed_to_tuple(m.group(1).strip()), _seed_to_tuple(m.group(2).strip()))
    raise ValueError(f"cannot parse seed: {s}")


def main() -> int:
    global t0
    t0 = time.time()
    peak = mem_mb()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    _ensure_pkgs()
    l1b = _import_l1b()
    from quantlab.factors.ai_factory.search import GPConfig, gp_search
    from quantlab.factors.ai_factory.novelty import (
        is_l1c_main_expr,
        is_lu_control_expr,
        is_textbook_expr,
        leaves_in_expr_str,
        L1C_MAIN_LEAVES,
        LU_CONTROL_LEAVES,
    )
    from quantlab.factors.ops import apply_expr, parse_expr
    from quantlab.factors.ai_factory.ledger import append_attempt

    log("loading L1b structural panels")
    panels, label, public, load_meta = l1b.load_structural_panels()
    peak = max(peak, mem_mb())
    log("base panels", load_meta.get("n_cols"), "peak", peak)

    panels, label, public, load_meta = attach_l1c_panels(panels, label, public, load_meta)
    peak = max(peak, mem_mb())
    log("l1c panels attached", peak)

    # split main vs control panel dicts for GP leaf sampling
    main_panels = {k: panels[k] for k in MAIN_LEAVES if k in panels}
    ctrl_panels = {k: panels[k] for k in CTRL_LEAVES if k in panels}
    # theme may be all-NaN — drop if useless
    if "theme_lu_density" in main_panels:
        if main_panels["theme_lu_density"].notna().sum().sum() == 0:
            del main_panels["theme_lu_density"]
            log("dropped theme_lu_density (all NaN)")

    run_ledger = OUT_DIR / "ledger_run.jsonl"
    if run_ledger.exists():
        run_ledger.unlink()
    main_ledger = ROOT / "output/ai_factor/ledger.jsonl"
    main_before = (
        sum(1 for x in main_ledger.read_text().splitlines() if x.strip())
        if main_ledger.exists()
        else 0
    )

    run_meta = {
        "mode": "explore_l1c_quantmind",
        "leo_authorization": "本聊天批准 AI 因子工厂 v1 真实探索窗 + New Bot 加急 L1c 非涨停主叶",
        "max_evaluations_main": MAX_EVAL_MAIN,
        "max_evaluations_control": MAX_EVAL_CTRL,
        "population": 40,
        "generations": 6,
        "top_k": TOP_K,
        "cost_one_way": COST,
        "seed": SEED,
        "main_leaves": list(main_panels.keys()),
        "control_leaves": list(ctrl_panels.keys()),
        "ban_textbook": True,
        "window": "explore_20240603_to_latest",
        "sealed_window_used_for_labels": False,
        "sealed_end": str(SEALED_END.date()),
        "promotion_approved": False,
        "capital_cny_primary": list(CAPITALS),
        "prereg": "docs/prereg/AI_FACTOR_L1c_OPENSOURCE_LOOP.md §7",
        "load_meta": load_meta,
        "mem_cap_MB": MEM_CAP_MB,
    }
    (OUT_DIR / "run_meta.json").write_text(
        json.dumps(run_meta, indent=2, ensure_ascii=False, default=str)
    )

    # --- MAIN GP ---
    cfg = GPConfig(
        population=40,
        generations=6,
        max_evaluations=MAX_EVAL_MAIN,
        top_k=TOP_K,
        seed=SEED,
        universe="midlarge_top1500_or_csi300_500",
        cost=COST,
        window="explore_20240603_to_latest_l1c_main",
        ledger_path=run_ledger,
        lambda_complexity=0.01,
        lambda_turnover=1.0,
        top_n=50,
        structural_only=True,
        ban_textbook=True,
        use_l1b_fitness=True,
        public_panels=public,
    )
    log("GP main start", list(main_panels.keys()))
    res_main = gp_search(main_panels, label, cfg)
    peak = max(peak, mem_mb())
    assert res_main.promotion_approved is False
    log("GP main done", res_main.evaluations, "peak", peak)

    # append GP rows to main ledger
    run_rows = [json.loads(x) for x in run_ledger.read_text().splitlines() if x.strip()] if run_ledger.exists() else []
    for r in run_rows:
        append_attempt(
            engine=r["engine"] + "_l1c_main",
            seed=r["seed"],
            universe=r["universe"],
            cost=r["cost"],
            window=r["window"],
            expr_str=r.get("expr_str", ""),
            fitness=r.get("fitness"),
            notes=(r.get("notes", "") + ";l1c_main_20261012"),
            path=main_ledger,
        )

    # seed library main (if budget left)
    main_seeds = [
        "neg(lu_height)",
        "neg(mul(lu_height, lu_promote_rate))",
        "rank(lu_promote_rate)",
        "neg(mkt_max_height)",
        "neg(mkt_lu_breadth)",
        "neg(ts_delta_5(mkt_lu_breadth))",
        "neg(ld_streak)",
        "rank(days_since_ld)",
        "neg(ld_count_5)",
        "neg(lockup_S_20)",
        "rank(neg(lockup_S_20))",
        "rank(ann_n_5)",
        "neg(ann_insider_dec_5)",
        "neg(ann_penalty_5)",
        "rank(ann_earn_signed_5)",
        "neg(ann_buyback_5)",
        "rank(on_minus_id)",
        "rank(if_basis_x_on)",
        "rank(etf_major_flow)",
        "mul(ld_streak, lockup_S_20)",
        "mul(ann_n_5, lockup_S_20)",
        "add(neg(ld_streak), neg(lockup_S_20))",
    ]
    seed_budget = max(0, 30 - 0)  # always evaluate seeds; counted separately
    main_seed_rows = eval_expr_list(
        main_seeds,
        {**main_panels, **{k: panels[k] for k in main_panels}},
        label,
        public,
        run_ledger,
        main_ledger,
        "seed_l1c_main",
        seed_budget,
    )
    peak = max(peak, mem_mb())

    # --- CONTROL arm (LU leaves only) ---
    ctrl_seeds = [
        "rank(days_since_lu)",
        "neg(lu_streak)",
        "neg(lu_count_5)",
        "rank(limit_up_flag)",
        "neg(etf_flow_x_lu)",
        "rank(if_basis_x_lu)",
        "neg(days_since_lu)",
        "rank(lu_streak)",
        "abs(lu_count_5)",
        "mul(lu_streak, days_since_lu)",
    ]
    # need ctrl panels only for apply — merge overnight if needed? no, pure ctrl
    ctrl_rows = eval_expr_list(
        ctrl_seeds,
        ctrl_panels,
        label,
        public,
        run_ledger,
        main_ledger,
        "seed_l1c_ctrl_lu",
        MAX_EVAL_CTRL,
    )
    peak = max(peak, mem_mb())
    log("control done", len(ctrl_rows))

    # merge main candidates
    main_cands = []
    for c in res_main.top_k:
        row = c.as_row()
        s = row["expr"]
        row["leaves"] = sorted(leaves_in_expr_str(s))
        row["is_main"] = is_l1c_main_expr(s)
        row["is_lu_control"] = is_lu_control_expr(s)
        row["is_textbook"] = is_textbook_expr(s)
        row["who_pays_zh"] = who_pays(s)
        main_cands.append(row)
    for r in main_seed_rows:
        main_cands.append(r)

    # filter: main Top-K must be non-textbook, not pure-LU-control, prefer is_main
    def _ann(r):
        m = r.get("metrics") or {}
        v = m.get("ann_net")
        return v if v is not None and np.isfinite(v) else float("-inf")

    def _fit(r):
        v = r.get("fitness")
        return v if v is not None and np.isfinite(v) else float("-inf")

    eligible = [
        r
        for r in main_cands
        if not r.get("is_textbook")
        and not r.get("is_lu_control")
        and not (r.get("metrics") or {}).get("novelty_fail")
        and _ann(r) > float("-inf")
    ]
    # demote any that accidentally used CTRL leaves
    eligible = [
        r
        for r in eligible
        if not (set(r.get("leaves") or []) & set(LU_CONTROL_LEAVES))
    ]
    eligible.sort(key=lambda r: (_fit(r), _ann(r)), reverse=True)
    # dedupe by expr
    seen = set()
    top_main = []
    for r in eligible:
        if r["expr"] in seen:
            continue
        seen.add(r["expr"])
        top_main.append(r)
        if len(top_main) >= TOP_K:
            break

    ctrl_sorted = sorted(ctrl_rows, key=lambda r: (_fit(r), _ann(r)), reverse=True)

    # capacity on top main (up to 8) + top 3 control
    cols = list(panels["overnight_ret"].columns)
    idx = panels["overnight_ret"].index
    log("loading sig/adv for capacity")
    sig, adv = load_sig_adv(cols, idx)
    peak = max(peak, mem_mb())

    cap_main = []
    for r in top_main[:8]:
        try:
            fac = apply_expr(parse_expr(r["tuple"] if "tuple" in r else _seed_to_tuple(r["expr"])), panels)
            # prefer tuple
            if "tuple" in r:
                fac = apply_expr(parse_expr(r["tuple"]), panels)
            cap = capacity_nets(fac, label, sig, adv)
            cap_main.append({"expr": r["expr"], "capacity": cap, "who_pays_zh": r.get("who_pays_zh")})
        except Exception as exc:  # noqa: BLE001
            log("cap_fail_main", r["expr"], str(exc)[:100])

    cap_ctrl = []
    for r in ctrl_sorted[:5]:
        try:
            fac = apply_expr(parse_expr(r["tuple"]), ctrl_panels)
            # need full panel align — use panels with ctrl keys
            fac = apply_expr(parse_expr(r["tuple"]), {**ctrl_panels})
            # reindex to label
            cap = capacity_nets(fac, label, sig, adv)
            cap_ctrl.append({"expr": r["expr"], "capacity": cap, "who_pays_zh": r.get("who_pays_zh")})
        except Exception as exc:  # noqa: BLE001
            log("cap_fail_ctrl", r["expr"], str(exc)[:100])

    # ablation: does best main survive without easystock lu_* height family?
    # Compare mean ann_net of main top that use only LD/lockup/ann vs those using board height
    BOARD = {"lu_height", "mkt_max_height", "lu_promote_rate", "mkt_lu_breadth", "theme_lu_density"}
    main_no_board = [
        r for r in top_main if not (set(r.get("leaves") or []) & BOARD)
    ]
    main_with_board = [
        r for r in top_main if set(r.get("leaves") or []) & BOARD
    ]
    ablation = {
        "n_top_main": len(top_main),
        "n_with_board_leaves": len(main_with_board),
        "n_without_board_leaves": len(main_no_board),
        "mean_ann_net_with_board": float(
            np.nanmean([_ann(r) for r in main_with_board])
        )
        if main_with_board
        else None,
        "mean_ann_net_without_board": float(
            np.nanmean([_ann(r) for r in main_no_board])
        )
        if main_no_board
        else None,
        "mean_ann_net_lu_control": float(
            np.nanmean([_ann(r) for r in ctrl_sorted])
        )
        if ctrl_sorted
        else None,
        "main_survives_without_pure_lu_control": len(top_main) > 0,
        "main_survives_without_board_leaves": len(main_no_board) > 0
        and (
            float(np.nanmean([_ann(r) for r in main_no_board])) > 0
            if main_no_board
            else False
        ),
        "note": "board leaves (连板高度/晋级/宽度) are MAIN by prereg; pure LU (days_since_lu/lu_streak) are CONTROL",
    }

    main_N = (
        sum(1 for x in main_ledger.read_text().splitlines() if x.strip())
        if main_ledger.exists()
        else 0
    )
    n_new = main_N - main_before
    peak = max(peak, mem_mb())

    # write artifacts
    (OUT_DIR / "top_k_main.json").write_text(
        json.dumps(top_main, indent=2, ensure_ascii=False, default=str)
    )
    (OUT_DIR / "top_k_control_lu.json").write_text(
        json.dumps(ctrl_sorted, indent=2, ensure_ascii=False, default=str)
    )
    (OUT_DIR / "capacity_main.json").write_text(
        json.dumps(cap_main, indent=2, ensure_ascii=False, default=str)
    )
    (OUT_DIR / "capacity_control_lu.json").write_text(
        json.dumps(cap_ctrl, indent=2, ensure_ascii=False, default=str)
    )
    (OUT_DIR / "ablation.json").write_text(
        json.dumps(ablation, indent=2, ensure_ascii=False, default=str)
    )
    summary = {
        "promotion_approved": False,
        "sealed": False,
        "ledger_N": main_N,
        "ledger_N_before": main_before,
        "N_new": n_new,
        "gp_main_evaluations": res_main.evaluations,
        "n_top_main": len(top_main),
        "n_control": len(ctrl_sorted),
        "peak_rss_MB": round(peak),
        "mem_cap_MB": MEM_CAP_MB,
        "under_mem_cap": peak < MEM_CAP_MB,
        "ablation": ablation,
        "ann_gap": load_meta.get("ann_title_events"),
        "suggest_sealed": False,
        "gate_note": "探索过程指标；不开密封；主 Top-K 禁教科书与纯涨停对照叶",
    }
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str)
    )

    # ZH report
    lines = [
        "# AI 因子工厂 L1c / QuantMind 探索窗报告",
        "",
        f"- **时间：** 2026-10-12（America/New_York）",
        f"- **promotion_approved：** false",
        f"- **密封：** 未开（不建议申请）",
        f"- **账本累计 N={main_N}**（本块新计次 ≈{n_new}；GP 主搜评估 {res_main.evaluations}）",
        f"- **峰值 RSS：** {peak:.0f} MB（上限 {MEM_CAP_MB}）",
        f"- **本金主口径：** 60 万 / 100 万",
        f"- **预注册：** `docs/prereg/AI_FACTOR_L1c_OPENSOURCE_LOOP.md` §7",
        "",
        "## 设计",
        "",
        "- **主叶：** 连板高度/晋级/宽度、跌停序列、解禁、公告 title 事件计数（+隔夜/ETF/基差辅叶）",
        "- **对照叶：** `days_since_lu` / `lu_streak` / `limit_up_flag` / `lu_count_5` / `etf_flow_x_lu` / `if_basis_x_lu`",
        "- **禁止：** 教科书主结果、小盘主线、密封窗、编造公告正文",
        "",
        "## 数据缺口",
        "",
    ]
    ag = load_meta.get("ann_title_events") or {}
    lines += [
        f"- 公告语料：`{ag.get('path')}`；body_source=**{ag.get('body_source')}**；**无向量嵌入列**（仅 title 事件计数）",
        f"- available_at：{ag.get('avail_min')} → {ag.get('avail_max')}",
        f"- 探索窗映射到中大盘后的公告 instrument 数：**{ag.get('n_instruments_explore')}**（稀疏；{ag.get('explore_coverage_note')}）",
        f"- ann_n_5 非零占比：{ag.get('nonzero_frac_ann_n_5')}",
        f"- 真题材映射 / 正文嵌入：仍缺",
        "",
        "## 主结果 Top-K（非涨停对照、非教科书）",
        "",
        "| # | 表达式 | fitness | ICIR | ann_net | 换手 | 钱从谁来 |",
        "|---|---|---|---|---|---|---|",
    ]
    for i, r in enumerate(top_main[:TOP_K], 1):
        m = r.get("metrics") or {}
        lines.append(
            f"| {i} | `{r['expr']}` | {r.get('fitness', float('nan')):.4f} | "
            f"{(r.get('train_icir') if r.get('train_icir') is not None else m.get('icir', float('nan'))):.3f} | "
            f"{m.get('ann_net', float('nan')):.2%} | {m.get('turnover', float('nan')):.3f} | "
            f"{(r.get('who_pays_zh') or '')[:42]} |"
        )
    if not top_main:
        lines.append("| — | （无合格主结果） | — | — | — | — | — |")

    lines += [
        "",
        "## 对照臂（纯涨停叶）",
        "",
        "| # | 表达式 | fitness | ann_net | 说明 |",
        "|---|---|---|---|---|",
    ]
    for i, r in enumerate(ctrl_sorted[:8], 1):
        m = r.get("metrics") or {}
        lines.append(
            f"| {i} | `{r['expr']}` | {r.get('fitness', float('nan')):.4f} | "
            f"{m.get('ann_net', float('nan')):.2%} | 对照，不晋级 |"
        )

    lines += ["", "## 60 万 / 100 万容量（主 Top，冲击+25bp 口径）", ""]
    if cap_main:
        lines += [
            "| 表达式 | 平价25bp净 | 60万冲击净 | 100万冲击净 | 换手 |",
            "|---|---|---|---|---|",
        ]
        for c in cap_main:
            cap = c["capacity"]
            f25 = (cap.get("flat_25bp") or {}).get("ann", float("nan"))
            i60 = (cap.get("impact") or {}).get("600000", {}).get("ann", float("nan"))
            i100 = (cap.get("impact") or {}).get("1000000", {}).get("ann", float("nan"))
            lines.append(
                f"| `{c['expr']}` | {f25:.2%} | {i60:.2%} | {i100:.2%} | {cap.get('mean_turn_ow', float('nan')):.3f} |"
            )
    else:
        lines.append("（无主结果可测容量）")

    lines += [
        "",
        "## 消融（主 vs 对照）",
        "",
        f"- 主 Top 条数：{ablation['n_top_main']}；含连板叶 {ablation['n_with_board_leaves']}；不含连板叶 {ablation['n_without_board_leaves']}",
        f"- 主臂均值 ann_net（含连板叶）：{ablation['mean_ann_net_with_board']}",
        f"- 主臂均值 ann_net（仅跌停/解禁/公告等、无连板叶）：{ablation['mean_ann_net_without_board']}",
        f"- 纯涨停对照均值 ann_net：{ablation['mean_ann_net_lu_control']}",
        f"- 去掉纯涨停对照后主臂是否仍有候选：**{ablation['main_survives_without_pure_lu_control']}**",
        f"- 去掉连板叶后主臂是否仍有正 ann_net：**{ablation['main_survives_without_board_leaves']}**",
        "",
        "## 结论",
        "",
    ]
    if not top_main:
        lines.append(
            "**机制失败风险：** 主叶搜索未产出合格非教科书、非纯涨停对照的 Top-K。"
            "不申请密封。"
        )
    elif not ablation["main_survives_without_board_leaves"] and ablation["n_with_board_leaves"]:
        lines.append(
            "主结果依赖连板结构叶（预注册允许的主叶）；去掉连板叶后偏弱。"
            "纯涨停对照另列。探索过程指标，**不申请密封**。"
        )
    else:
        lines.append(
            "主臂在无纯涨停对照叶下有候选；见 Top-K 与 60/100 万容量。"
            "仍为探索窗过程指标，闸门未到密封标准则 **不申请密封**。"
        )

    lines += [
        "",
        "## 路径",
        "",
        f"- 报告：`{REPORT}`",
        f"- 产物：`{OUT_DIR}/`",
        f"- 账本：`output/ai_factor/ledger.jsonl`",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    log("wrote", REPORT, "N", main_N, "peak", peak)

    print(
        json.dumps(
            {
                "ok": True,
                "ledger_N": main_N,
                "N_new": n_new,
                "n_top_main": len(top_main),
                "n_control": len(ctrl_sorted),
                "peak_rss_MB": round(peak),
                "report": str(REPORT),
                "promotion_approved": False,
                "suggest_sealed": False,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
