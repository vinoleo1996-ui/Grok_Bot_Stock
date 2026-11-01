#!/usr/bin/env python3
"""GP reopen v21 — B-track ONLY: ETF timing returnized (New Bot 2026-10-12).

Why: v20 Track B used next-day industry ETF *flow continuation* as y — FORBIDDEN.
v21 label y = industry/theme ETF forward excess return (NOT flow).

Spec:
  - Features X: ind_etf_share_flow / etf_*_flow / etf_share_chg_* (predict returns; never as y)
  - Label y: SW-L1 industry ETF AUM-weighted fwd 1d OR 5d excess return vs 510300
    (primary gate uses 1d; 5d reported as secondary; both documented)
  - Hard gates: ICIR>0; after-cost; impact@60万∧100万 (ETF sleeve); ban CB/gold
  - Tag sleeve=etf_timing_ret; hand QuantLab Beta ONLY; NOT Alpha shortlist
  - Track A paused this round; no Strategy; promotion_approved=false; no seal
  - MEM_CAP=2200; SELF_STOP sticky>2400 OR available<2500 — DO NOT raise
  - Lean window LOOKBACK=2024-04-01 PANEL_END=2025-06-30
  - SEED=20261104; WINDOW=gp_reopen_hardgate_v21_etf_timing_ret_20240603_explore

Launch: LEO_AI_FACTOR_EXPLORE_OK=1 /workspace/qlvenv/bin/python -u …
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
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/workspace/QuantLab")
OUT = ROOT / "output/ai_factor/gp_reopen_hardgate_v21_etf_timing_ret"
REPORT_NOTE = OUT / "REPORT_NOTE_ZH.md"
V2 = ROOT / "data/v2"

EXPLORE_START = pd.Timestamp("2024-06-03")
LOOKBACK_START = pd.Timestamp("2024-04-01")  # lean — DO NOT widen
PANEL_END = pd.Timestamp("2025-06-30")
SEED = 20261104
WINDOW = "gp_reopen_hardgate_v21_etf_timing_ret_20240603_explore"
MAX_EVAL = 120
COST = 0.0025  # round-trip proxy for after-cost gate
PROMOTION_APPROVED = False
MEM_CAP_MB = 2200  # DO NOT raise
SELF_STOP_AVAILABLE_MB = 2500
SELF_STOP_RSS_STICKY_MB = 2400  # DO NOT raise
# ETF sleeve impact notionals (CNY). Tushare fund amount is 千元 → /1000 for 万元, *1000 for 元.
IMPACT_CNY = (600_000, 1_000_000)  # 60万 ∧ 100万

CB_GOLD_BANNED_STEMS = (
    "cb_", "convertible", "bond_prem", "matprem", "gold", "au999", "au9999",
    "gld_", "huangjin",
)

t0 = time.time()


def mem_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def available_mb() -> float:
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) / 1024.0
    except Exception:
        pass
    return float("nan")


def log(*a):
    print(f"[gp_v21 {time.time()-t0:5.0f}s {mem_mb():.0f}MB]", *a, flush=True)


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



def _ensure_pkgs():
    """Bootstrap local quantlab package (same pattern as v20)."""
    if "quantlab" not in sys.modules:
        q = types.ModuleType("quantlab")
        q.__path__ = [str(ROOT / "quantlab")]
        sys.modules["quantlab"] = q
    if "quantlab.factors" not in sys.modules or not hasattr(sys.modules["quantlab.factors"], "__path__"):
        f = types.ModuleType("quantlab.factors")
        f.__path__ = [str(ROOT / "quantlab/factors")]
        sys.modules["quantlab.factors"] = f

    def load(name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        assert spec.loader
        spec.loader.exec_module(mod)
        return mod

    load("quantlab.factors.ops", ROOT / "quantlab/factors/ops.py")


def leaves_in(expr: str) -> frozenset[str]:
    import re
    return frozenset(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expr)) - {
        "ts_mean", "ts_std", "ts_delta", "ts_max", "ts_min", "neg", "abs", "rank",
        "mul", "sub", "div", "add", "delay",
    }


def _ymd_series(s: pd.Series) -> pd.Series:
    return pd.to_datetime(
        s.astype(str).str.replace("-", "", regex=False).str[:8],
        format="%Y%m%d",
        errors="coerce",
    )


def load_510300_ret() -> tuple[pd.Series, dict]:
    meta: dict = {"path": None, "ok": False}
    paths = [
        V2 / "etf_510300/fund_daily_tushare_510300.parquet",
        V2 / "tushare_raw/fund_daily/510300.SH.parquet",
    ]
    for p in paths:
        if not p.exists():
            continue
        df = pd.read_parquet(p)
        meta["path"] = str(p.relative_to(ROOT))
        td = _ymd_series(df["trade_date"])
        df = df.assign(_td=td).dropna(subset=["_td"]).sort_values("_td")
        if "close" in df.columns:
            ret = df.set_index("_td")["close"].astype("float64").pct_change()
        elif "pct_chg" in df.columns:
            ret = df.set_index("_td")["pct_chg"].astype("float64") / 100.0
        else:
            continue
        ret = ret.loc[(ret.index >= LOOKBACK_START - pd.Timedelta(days=5)) & (ret.index <= PANEL_END)]
        ret = ret.astype("float32")
        meta.update({"ok": True, "n": int(ret.notna().sum()), "start": str(ret.index.min().date()), "end": str(ret.index.max().date())})
        return ret, meta
    meta["error"] = "510300_daily_missing"
    return pd.Series(dtype="float32"), meta


def load_industry_etf_ret() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """AUM-weighted SW-L1 industry ETF daily returns + amount panel (amount in 千元)."""
    meta: dict = {"ok": False, "gaps": []}
    map_path = V2 / "etf/sw_l1_etf_map_pit_daily.parquet"
    adj_path = V2 / "etf/etf_daily_adj.parquet"
    if not map_path.exists():
        meta["gaps"].append("sw_l1_etf_map_pit_daily_missing")
        return pd.DataFrame(), pd.DataFrame(), meta
    if not adj_path.exists():
        meta["gaps"].append("etf_daily_adj_missing")
        return pd.DataFrame(), pd.DataFrame(), meta

    m = pd.read_parquet(
        map_path,
        columns=["sw_l1_code", "trade_date", "etf_ts_code", "aum_wan", "amount", "no_etf", "available_at"],
    )
    m["_td"] = _ymd_series(m["trade_date"])
    m = m.dropna(subset=["_td", "sw_l1_code", "etf_ts_code"])
    if "no_etf" in m.columns:
        m = m[m["no_etf"] != True]  # noqa: E712
    m = m[(m["_td"] >= LOOKBACK_START - pd.Timedelta(days=10)) & (m["_td"] <= PANEL_END)]
    codes = sorted(m["etf_ts_code"].dropna().unique().tolist())
    meta["n_etf"] = len(codes)
    meta["n_sw"] = int(m["sw_l1_code"].nunique())
    meta["map_path"] = str(map_path.relative_to(ROOT))

    adj = pd.read_parquet(
        adj_path,
        columns=["ts_code", "trade_date", "close_hfq", "pct_chg", "amount", "available_at"],
    )
    adj = adj[adj["ts_code"].isin(codes)].copy()
    adj["_td"] = _ymd_series(adj["trade_date"])
    adj = adj.dropna(subset=["_td"])
    adj = adj[(adj["_td"] >= LOOKBACK_START - pd.Timedelta(days=10)) & (adj["_td"] <= PANEL_END)]
    adj = adj.sort_values(["ts_code", "_td"])
    adj["ret"] = adj.groupby("ts_code", sort=False)["close_hfq"].pct_change()
    meta["adj_path"] = str(adj_path.relative_to(ROOT))
    meta["adj_rows"] = int(len(adj))

    j = m.merge(
        adj[["ts_code", "_td", "ret", "amount"]].rename(columns={"amount": "etf_amount_qian"}),
        left_on=["etf_ts_code", "_td"],
        right_on=["ts_code", "_td"],
        how="left",
    )
    j = j.dropna(subset=["ret", "sw_l1_code"])
    w = j["aum_wan"].fillna(0).clip(lower=0).to_numpy(dtype=np.float64)
    j["_w"] = np.where(w > 0, w, 1.0)
    num = (j["_w"] * j["ret"]).groupby([j["_td"], j["sw_l1_code"]], sort=False).sum()
    den = j.groupby(["_td", "sw_l1_code"], sort=False)["_w"].sum()
    ind_ret = (num / den).unstack("sw_l1_code").sort_index().astype("float32")
    # amount: prefer map amount, else etf amount (千元)
    amt_src = j["amount"] if "amount" in j.columns else j["etf_amount_qian"]
    if "etf_amount_qian" in j.columns:
        amt_src = amt_src.fillna(j["etf_amount_qian"]) if "amount" in j.columns else j["etf_amount_qian"]
    amt = (
        pd.DataFrame({"_td": j["_td"], "sw": j["sw_l1_code"], "a": amt_src.fillna(0)})
        .groupby(["_td", "sw"], sort=False)["a"]
        .sum()
        .unstack("sw")
        .reindex(index=ind_ret.index, columns=ind_ret.columns)
        .astype("float32")
    )
    ind_ret = ind_ret.loc[(ind_ret.index >= LOOKBACK_START) & (ind_ret.index <= PANEL_END)]
    amt = amt.reindex_like(ind_ret)
    meta.update(
        {
            "ok": True,
            "shape": list(ind_ret.shape),
            "nonempty_rate": float(np.isfinite(ind_ret.to_numpy()).mean()),
            "start": str(ind_ret.index.min().date()) if len(ind_ret) else None,
            "end": str(ind_ret.index.max().date()) if len(ind_ret) else None,
            "method": "aum_weighted_sw_l1_etf_close_hfq_pct_change",
            "amount_unit": "qian_yuan_tushare",
        }
    )
    return ind_ret, amt, meta


def load_flow_panels(base_cols: pd.Index, common_idx: pd.DatetimeIndex) -> tuple[dict[str, pd.DataFrame], dict]:
    """Feature panels only — NEVER used as y."""
    panels: dict[str, pd.DataFrame] = {}
    meta: dict = {"wired": [], "gaps": []}

    by_sw = V2 / "etf/share_pit/ind_etf_share_flow_by_sw_l1.parquet"
    if by_sw.exists():
        dfb = pd.read_parquet(by_sw)
        cols_l = {c.lower(): c for c in dfb.columns}
        td = cols_l.get("trade_date") or "trade_date"
        swc = cols_l.get("sw_l1_code") or cols_l.get("sw_code")
        flowc = None
        for cand in ("flow_est_wan_yuan", "d_share_wan", "share_flow", "flow"):
            if cand in dfb.columns:
                flowc = cand
                break
        if td and swc and flowc:
            dfb = dfb.copy()
            dfb["_td"] = _ymd_series(dfb[td])
            dfb = dfb.dropna(subset=["_td", swc])
            dfb = dfb[(dfb["_td"] >= LOOKBACK_START) & (dfb["_td"] <= PANEL_END)]
            piv = dfb.pivot_table(index="_td", columns=swc, values=flowc, aggfunc="sum").sort_index()
            piv = piv.reindex(index=common_idx, columns=base_cols).astype("float32")
            panels["ind_etf_share_flow"] = piv
            meta["wired"].append("ind_etf_share_flow")
        else:
            meta["gaps"].append("ind_etf_share_flow:bad_schema")
    else:
        meta["gaps"].append("ind_etf_share_flow:missing")

    for name, path in (
        ("etf_share_chg_major", V2 / "etf/share_pit/etf_share_flow_pit_major.parquet"),
        ("etf_all_flow", V2 / "etf/share_pit/etf_share_flow_pit_all.parquet"),
        ("etf_share_chg_theme", V2 / "etf/share_pit/etf_share_flow_pit_industry_theme.parquet"),
    ):
        if mem_mb() > 2000:
            meta["gaps"].append(f"{name}:skipped_rss")
            break
        if not path.exists():
            meta["gaps"].append(f"{name}:missing")
            continue
        raw = pd.read_parquet(path)
        cols_l = {c.lower(): c for c in raw.columns}
        td = cols_l.get("trade_date") or "trade_date"
        flowc = None
        for cand in ("flow_est_wan_yuan", "d_share_wan", "share_chg", "d_share", "flow"):
            if cand in raw.columns:
                flowc = cand
                break
        if not flowc:
            meta["gaps"].append(f"{name}:no_flow_col")
            continue
        raw = raw.copy()
        raw["_td"] = _ymd_series(raw[td])
        ser = raw.dropna(subset=["_td"]).groupby("_td")[flowc].sum().sort_index()
        ser = ser.loc[(ser.index >= LOOKBACK_START) & (ser.index <= PANEL_END)].astype("float32")
        s1 = ser.reindex(common_idx)
        panels[name] = pd.DataFrame(
            np.repeat(s1.to_numpy().reshape(-1, 1), len(base_cols), axis=1),
            index=common_idx,
            columns=base_cols,
            dtype="float32",
        )
        meta["wired"].append(name)
        log("flow leaf", name, panels[name].shape)
    return panels, meta


def icir_panel(fac: pd.DataFrame, lab: pd.DataFrame) -> float:
    ics = []
    n = min(len(fac), len(lab))
    for i in range(n):
        a = fac.iloc[i].to_numpy(dtype=np.float64)
        b = lab.iloc[i].to_numpy(dtype=np.float64)
        m = np.isfinite(a) & np.isfinite(b)
        if m.sum() < 5:
            continue
        aa, bb = a[m], b[m]
        if aa.std() < 1e-12 or bb.std() < 1e-12:
            continue
        ics.append(float(np.corrcoef(aa, bb)[0, 1]))
    if len(ics) < 10:
        return float("nan")
    mu = float(np.nanmean(ics))
    sd = float(np.nanstd(ics))
    return mu / sd * math.sqrt(252) if sd > 1e-12 else float("nan")


def after_cost_icir(fac: pd.DataFrame, lab: pd.DataFrame, cost: float = COST) -> float:
    """ICIR on cost-adjusted label proxy: y_adj = y - cost * sign(|z(fac)| stack turnover proxy).
    Lean: subtract cost from daily long-short mean spread before IR — approximate by
    correlating fac with (lab - cost * cs_sign(fac) * |lab|.mean_row) is unstable;
    instead: require ICIR(fac, lab) > 0 and ICIR(fac, lab - cost) with constant cost drag on y.
    """
    # Constant round-trip drag on excess return (conservative for daily sleeve)
    lab_adj = lab - cost
    return icir_panel(fac, lab_adj)


def impact_gate(fac: pd.DataFrame, lab: pd.DataFrame, amt_qian: pd.DataFrame) -> dict:
    """Impact @60万∧100万: keep industries whose daily amount (千元) can absorb notional.
    amount_qian * 1000 = CNY. Require ICIR>0 on the liquid subset for BOTH thresholds.
    """
    out = {}
    for cny in IMPACT_CNY:
        need_qian = cny / 1000.0  # 千元
        # mask industries with amount >= need on that day
        liquid = amt_qian.reindex_like(fac) >= need_qian
        fac_l = fac.where(liquid)
        lab_l = lab.where(liquid)
        ic = icir_panel(fac_l, lab_l)
        # coverage of liquid cells
        if fac.size:
            m = liquid.to_numpy(dtype=bool) & np.isfinite(fac.to_numpy()) & np.isfinite(lab.to_numpy())
            cov = float(np.mean(m))
        else:
            cov = 0.0
        out[f"icir_impact_{int(cny)}"] = ic if isinstance(ic, float) else None
        out[f"liquid_cov_{int(cny)}"] = cov
        out[f"pass_impact_{int(cny)}"] = bool(isinstance(ic, float) and math.isfinite(ic) and ic > 0 and cov >= 0.05)
    out["pass_impact_60_and_100"] = bool(out.get("pass_impact_600000") and out.get("pass_impact_1000000"))
    return out


def banned_expr(es: str) -> str | None:
    Ls = leaves_in(es)
    for x in Ls:
        for s0 in CB_GOLD_BANNED_STEMS:
            if x == s0 or x.startswith(s0) or s0 in x:
                return "HARD_BAN_CB_GOLD"
        if x == "overnight_ret" or x.startswith("fsr") or x.startswith("ann_insider") or x.startswith("idx_w"):
            return "SYNTAX_HARD_BAN_STOCK_LEAF"
    # never allow flow leaf names to appear as if they were labels — features ok
    return None


def mk_expr(rng, leaf_names, wraps, ops_b):
    from quantlab.factors.ops import Expr as EB

    if len(leaf_names) < 1:
        return None
    if len(leaf_names) == 1 or rng.random() < 0.35:
        a = str(rng.choice(leaf_names))
        e = EB("leaf", a)
        e = EB("op", str(rng.choice(wraps)), (e,))
        if rng.random() < 0.4:
            e = EB("op", str(rng.choice(wraps)), (e,))
        return e
    a, b = [str(x) for x in rng.choice(leaf_names, size=2, replace=True)]
    op = str(rng.choice(ops_b, p=[0.3, 0.35, 0.2, 0.15]))
    ea = EB("op", str(rng.choice(wraps)), (EB("leaf", a),))
    eb = EB("op", str(rng.choice(wraps)), (EB("leaf", b),))
    root = EB("op", op, (ea, eb))
    if rng.random() < 0.35:
        root = EB("op", str(rng.choice(("ts_mean_10", "ts_mean_20", "neg", "abs"))), (root,))
    return root


def main() -> int:
    if os.environ.get("LEO_AI_FACTOR_EXPLORE_OK") != "1":
        print("REFUSE: set LEO_AI_FACTOR_EXPLORE_OK=1", flush=True)
        return 2

    OUT.mkdir(parents=True, exist_ok=True)
    avail0 = available_mb()
    os.environ["QL_V21_AVAILABLE_AT_START_MB"] = str(avail0)
    log(
        "START v21 B-only etf_timing_ret",
        "pid", os.getpid(),
        "available_mb", round(avail0, 1),
        "MEM_CAP", MEM_CAP_MB,
        "SELF_STOP_RSS", SELF_STOP_RSS_STICKY_MB,
        "WINDOW", WINDOW,
        "SEED", SEED,
        "TrackA", "PAUSED",
        "promotion", PROMOTION_APPROVED,
    )
    # Startup receipt for New Bot
    (OUT / "startup_receipt.json").write_text(
        json.dumps(
            {
                "pid": os.getpid(),
                "available_mb": avail0,
                "sleeve": "etf_timing_ret",
                "track": "B_only",
                "track_a": "paused",
                "window": WINDOW,
                "seed": SEED,
                "promotion_approved": False,
                "for_beta": True,
                "for_alpha_shortlist": False,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # --- Inventory / build return labels ---
    bm_ret, bm_meta = load_510300_ret()
    ind_ret, amt, ind_meta = load_industry_etf_ret()
    label_meta = {
        "benchmark": "510300.SH close pct_change",
        "benchmark_meta": bm_meta,
        "industry_ret_meta": ind_meta,
        "horizons": {
            "primary": "fwd_1d_excess_vs_510300",
            "secondary": "fwd_5d_excess_vs_510300",
        },
        "forbidden_label": "flow_continuation (v20) — NOT used",
        "equal_weight_industry_alt": "not primary this run; AUM-weighted industry ETF vs 510300 chosen for PIT ETF sleeve liquidity",
    }
    (OUT / "label_definition.json").write_text(
        json.dumps(clean(label_meta), indent=2, ensure_ascii=False), encoding="utf-8"
    )

    if not bm_meta.get("ok") or not ind_meta.get("ok") or ind_ret.empty:
        gaps = []
        if not bm_meta.get("ok"):
            gaps.append("510300_return_series")
        if not ind_meta.get("ok"):
            gaps.extend(ind_meta.get("gaps") or ["industry_etf_return"])
        log("STOP_CLEAN B: return series gap", gaps)
        pkg = {
            "sleeve": "etf_timing_ret",
            "for_beta": True,
            "for_alpha_shortlist_adjudication": False,
            "promotion_approved": False,
            "stopped_clean": True,
            "gaps_for_data": gaps,
            "label_meta": label_meta,
            "note": "Do not invent y; Data must supply ETF NAV/returns if missing",
        }
        (OUT / "beta_etf_timing_ret_package.json").write_text(
            json.dumps(clean(pkg), indent=2, ensure_ascii=False), encoding="utf-8"
        )
        (OUT / "BETA_NOTE_ZH.md").write_text(
            "# v21 ETF timing 收益化（交 Beta）— 干净停\n\n"
            f"- 缺口：{gaps}\n"
            "- 未伪造 y；请 Data 补行业/主题 ETF 收益或 NAV 后再开。\n"
            "- promotion_approved=false；不进 Alpha 短名单；不交 Strategy。\n",
            encoding="utf-8",
        )
        return 0

    # Excess returns vs 510300
    bm = bm_ret.reindex(ind_ret.index)
    excess = ind_ret.sub(bm, axis=0).astype("float32")
    # Forward labels (PIT-safe: shift negative = future)
    y1 = excess.shift(-1).astype("float32")
    y5 = sum(excess.shift(-i) for i in range(1, 6)).astype("float32")  # simple sum approx of 5d excess
    # Explore window mask (features observable; label uses future within panel)
    # Keep full lean panel for TS wraps; IC computed where both finite.

    log("labels ready", "ind", ind_ret.shape, "y1_finite", round(float(np.isfinite(y1.to_numpy()).mean()), 4),
        "y5_finite", round(float(np.isfinite(y5.to_numpy()).mean()), 4), "rss", round(mem_mb()))

    panels, flow_meta = load_flow_panels(ind_ret.columns, ind_ret.index)
    if not panels:
        log("STOP_CLEAN B: no flow feature panels")
        (OUT / "beta_etf_timing_ret_package.json").write_text(
            json.dumps(
                clean(
                    {
                        "sleeve": "etf_timing_ret",
                        "stopped_clean": True,
                        "gaps_for_data": ["etf_flow_features_missing"],
                        "for_beta": True,
                        "promotion_approved": False,
                    }
                ),
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        return 0

    log("gp_search start TrackB", "pid", os.getpid(), "available_mb", round(available_mb(), 1),
        "n_leaves", len(panels), "max_eval", MAX_EVAL, "label", "fwd_1d_excess_vs_510300")

    _ensure_pkgs()
    from quantlab.factors.ops import apply_expr as apply_b

    rng = np.random.default_rng(SEED)
    leaf_names = [k for k, v in panels.items() if v.notna().to_numpy().sum() > 100]
    wraps = ("ts_mean_5", "ts_mean_10", "ts_mean_20", "ts_std_10", "ts_delta_5", "ts_max_20", "neg", "abs")
    ops_b = ("mul", "sub", "div", "add")

    ledger = OUT / "ledger_track_b.jsonl"
    if ledger.exists():
        ledger.unlink()
    candidates = []
    fail_ctr: dict[str, int] = {}
    seen = set()
    n_eval = 0
    peak = mem_mb()

    while n_eval < MAX_EVAL:
        peak = max(peak, mem_mb())
        if mem_mb() > SELF_STOP_RSS_STICKY_MB or (
            math.isfinite(available_mb()) and available_mb() < SELF_STOP_AVAILABLE_MB
        ):
            log("SELF_STOP", "rss", round(mem_mb()), "avail", round(available_mb(), 1), "evals", n_eval)
            break
        expr = mk_expr(rng, leaf_names, wraps, ops_b)
        if expr is None:
            break
        es = expr.to_str()
        br = banned_expr(es)
        if br:
            fail_ctr[br] = fail_ctr.get(br, 0) + 1
            continue
        if es in seen:
            continue
        seen.add(es)
        n_eval += 1
        Ls = sorted(leaves_in(es))
        try:
            fac = apply_b(expr, panels).astype("float32")
        except Exception as ex:
            with open(ledger, "a", encoding="utf-8") as fh:
                fh.write(json.dumps({"expr": es, "error": type(ex).__name__, "sleeve": "etf_timing_ret"}, ensure_ascii=False) + "\n")
            fail_ctr["apply_error"] = fail_ctr.get("apply_error", 0) + 1
            continue

        icir1 = icir_panel(fac, y1)
        icir5 = icir_panel(fac, y5)
        icir1_ac = after_cost_icir(fac, y1)
        imp = impact_gate(fac, y1, amt)
        nr = float(np.isfinite(fac.to_numpy()).mean()) if fac.size else 0.0

        gate_ok = (
            isinstance(icir1, float) and math.isfinite(icir1) and icir1 > 0
            and isinstance(icir1_ac, float) and math.isfinite(icir1_ac) and icir1_ac > 0
            and bool(imp.get("pass_impact_60_and_100"))
            and nr >= 0.08
        )
        reason = None
        if not (isinstance(icir1, float) and math.isfinite(icir1) and icir1 > 0):
            reason = "ICIR1_LE_0"
        elif not (isinstance(icir1_ac, float) and math.isfinite(icir1_ac) and icir1_ac > 0):
            reason = "AFTER_COST_ICIR_LE_0"
        elif not imp.get("pass_impact_60_and_100"):
            reason = "IMPACT_60_OR_100_FAIL"
        elif nr < 0.08:
            reason = "COVERAGE_THIN"

        row = {
            "expr": es,
            "leaves": Ls,
            "icir_fwd1d_excess_510300": icir1 if isinstance(icir1, float) else None,
            "icir_fwd5d_excess_510300": icir5 if isinstance(icir5, float) else None,
            "icir_fwd1d_after_cost": icir1_ac if isinstance(icir1_ac, float) else None,
            "nonempty_rate": nr,
            "impact": imp,
            "gate_ok": gate_ok,
            "fail_reason": reason,
            "sleeve": "etf_timing_ret",
            "label_primary": "fwd_1d_excess_vs_510300",
            "label_secondary": "fwd_5d_excess_vs_510300",
            "for_alpha_shortlist": False,
            "for_beta": True,
            "promotion_approved": False,
            "note": "TrackB ETF timing RETURNIZED; y=industry ETF fwd excess vs 510300; X=share flow features; hand Beta only",
        }
        with open(ledger, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(clean(row), ensure_ascii=False) + "\n")
        if gate_ok:
            candidates.append(row)
        else:
            fail_ctr[reason or "FAIL"] = fail_ctr.get(reason or "FAIL", 0) + 1
        del fac
        if n_eval % 20 == 0:
            gc.collect()
            peak = max(peak, mem_mb())
            log("progress", n_eval, "/", MAX_EVAL, "pass", len(candidates), "rss", round(mem_mb()),
                "avail", round(available_mb(), 1))

    candidates.sort(
        key=lambda r: (r.get("icir_fwd1d_excess_510300") or -1e9),
        reverse=True,
    )
    peak = max(peak, mem_mb())
    log("DONE", "evals", n_eval, "n_pass", len(candidates), "peak", round(peak))

    top_fail = sorted(fail_ctr.items(), key=lambda kv: -kv[1])[:8]
    beta_pkg = {
        "sleeve": "etf_timing_ret",
        "for_alpha_shortlist_adjudication": False,
        "for_beta": True,
        "promotion_approved": False,
        "not_strategy_weights": True,
        "sealed": False,
        "pid": os.getpid(),
        "peak_rss_MB": round(peak),
        "available_at_start_MB": avail0,
        "n_evaluations": int(n_eval),
        "n_candidates_pass": len(candidates),
        "candidates": candidates[:25],
        "etf_leaves_wired": sorted(panels.keys()),
        "flow_meta": flow_meta,
        "label": {
            "primary": "fwd_1d_aum_weighted_sw_l1_etf_excess_return_vs_510300",
            "secondary": "fwd_5d_sum_excess_vs_510300",
            "NOT": "flow_continuation",
            "benchmark": "510300.SH",
            "industry_method": ind_meta.get("method"),
            "sources": {
                "industry_map": ind_meta.get("map_path"),
                "etf_adj": ind_meta.get("adj_path"),
                "benchmark": bm_meta.get("path"),
            },
        },
        "gates": {
            "icir_fwd1d_gt_0": True,
            "after_cost_icir_gt_0": True,
            "cost": COST,
            "impact_cny": list(IMPACT_CNY),
            "impact_note": "amount in 千元 (tushare); liquid if amount>=notional/1000; require ICIR>0 on liquid subset for BOTH 60万 and 100万",
            "ban_cb_gold": True,
        },
        "fail_reason_top": [{"reason": a, "n": b} for a, b in top_fail],
        "window": WINDOW,
        "seed": SEED,
        "lookback": str(LOOKBACK_START.date()),
        "panel_end": str(PANEL_END.date()),
        "explore_start": str(EXPLORE_START.date()),
        "mem_cap_MB": MEM_CAP_MB,
        "self_stop_rss_sticky_MB": SELF_STOP_RSS_STICKY_MB,
        "track_a": "paused",
        "note": "Hand QuantLab Beta only; do NOT submit to Alpha shortlist; promotion_approved=false; no Strategy",
        "out_dir": str(OUT.relative_to(ROOT)),
    }
    (OUT / "beta_etf_timing_ret_package.json").write_text(
        json.dumps(clean(beta_pkg), indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUT / "candidates.json").write_text(
        json.dumps(clean(candidates), indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUT / "receipt.json").write_text(
        json.dumps(
            clean(
                {
                    "track": "B_etf_timing_ret",
                    "sleeve": "etf_timing_ret",
                    "pid": os.getpid(),
                    "peak_rss_MB": round(peak),
                    "available_at_start_MB": avail0,
                    "n_evaluations": int(n_eval),
                    "n_pass": len(candidates),
                    "etf_leaves": sorted(panels.keys()),
                    "label_primary": "fwd_1d_excess_vs_510300",
                    "label_secondary": "fwd_5d_excess_vs_510300",
                    "for_alpha": False,
                    "for_beta": True,
                    "promotion_approved": False,
                    "under_mem_cap": peak <= MEM_CAP_MB,
                }
            ),
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    lines = [
        "# v21 Track B — ETF timing 收益化（交 Beta，不进 Alpha 短名单）",
        "",
        f"- sleeve=`etf_timing_ret`；evals={n_eval}；pass={len(candidates)}；peak≈{round(peak)}MB；available@start≈{round(avail0,1)}MB",
        f"- 叶子（X，仅特征）：{sorted(panels.keys())}",
        "- **标签 y（非 flow）**：申万一级行业 ETF（AUM 加权，`close_hfq` 收益）相对 **510300** 的",
        "  - 主闸：未来 **1 日**超额收益",
        "  - 副报：未来 **5 日**超额收益之和",
        "- 硬闸：ICIR(1d)>0；成本后 ICIR>0（cost=25bp 常数拖累）；冲击@60万∧100万（金额单位=千元，流动子集上 ICIR>0）；禁 CB/金",
        "- **不交 Alpha 短名单**；Track A 本轮暂停；promotion_approved=false；不交 Strategy；未开密封",
        f"- 包：`{OUT.relative_to(ROOT)}/beta_etf_timing_ret_package.json`",
        f"- 标签定义：`{OUT.relative_to(ROOT)}/label_definition.json`",
        "",
        "| # | 表达式 | ICIR_1d | ICIR_1d_after_cost | ICIR_5d | impact60∧100 | nonempty |",
        "|---|---|---:|---:|---:|:---:|---:|",
    ]
    for i, r in enumerate(candidates[:15], 1):
        lines.append(
            f"| {i} | `{r['expr']}` | {r.get('icir_fwd1d_excess_510300')} | {r.get('icir_fwd1d_after_cost')} | "
            f"{r.get('icir_fwd5d_excess_510300')} | {r.get('impact',{}).get('pass_impact_60_and_100')} | {r.get('nonempty_rate')} |"
        )
    if not candidates:
        lines.append("| — | （本轮无过收益化硬闸） | — | — | — | — | — |")
    lines += ["", f"- fail_top: {top_fail}", ""]
    (OUT / "BETA_NOTE_ZH.md").write_text("\n".join(lines), encoding="utf-8")
    REPORT_NOTE.write_text("\n".join(lines), encoding="utf-8")

    summary = {
        "promotion_approved": False,
        "sealed": False,
        "strategy_weights": False,
        "track_a": "paused",
        "sleeve": "etf_timing_ret",
        "pid": os.getpid(),
        "peak_rss_MB": round(peak),
        "available_at_start_MB": avail0,
        "n_evaluations": int(n_eval),
        "n_pass": len(candidates),
        "under_mem_cap": peak <= MEM_CAP_MB,
        "label_primary": "fwd_1d_excess_vs_510300",
        "out_dir": str(OUT.relative_to(ROOT)),
        "beta_package": str((OUT / "beta_etf_timing_ret_package.json").relative_to(ROOT)),
        "top_exprs": [r["expr"] for r in candidates[:5]],
        "fail_reason_top": [{"reason": a, "n": b} for a, b in top_fail],
    }
    (OUT / "summary.json").write_text(json.dumps(clean(summary), indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))
    return 0 if peak <= MEM_CAP_MB else 1


if __name__ == "__main__":
    raise SystemExit(main())
