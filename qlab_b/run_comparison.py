"""qlab_b challenger runner: same dataset, same engine, same ledger as quantlab.

Runs my arm via Engine(strategy='schedule') plus the two reference equal-weight arms,
under both industry policies, then prints a single comparison table. Reuses quantlab's
prepare/account_statistics/block_bootstrap_ci so the ruler matches the opponent's
six-arm protocol. Does not modify quantlab; imports it.
"""
from __future__ import annotations

import sys, json
from copy import deepcopy
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from quantlab.config import CONFIG
from quantlab.data.contracts import load_dataset
from quantlab.data.qualification import research_assessment
from quantlab.backtest.engine import Engine
from quantlab.strategy.decision import review_dates
from quantlab.strategy.legacy import legacy_config
from quantlab.legacy_comparison import account_statistics
from quantlab.research import block_bootstrap_ci

from strategy import momentum_schedule
from prep import prepare_window

MANIFEST = ROOT / "data/free_research_120/dataset/manifest.json"
START, END, SEED = "2020-01-02", "2026-06-30", 20260924
POLICIES = ["enforced", "omit_for_diagnostic"]


def main():
    ds = load_dataset(MANIFEST, profile="free_research")
    assess = research_assessment(ds, require_industry=False)
    if assess["status"] != "research_ready":
        print(json.dumps(assess, default=str, indent=2)); return
    if len(ds.panels) != 120:
        raise ValueError(f"expected frozen 120 cohort, got {len(ds.panels)}")

    cfg = legacy_config(CONFIG)
    cfg.seed = SEED
    cfg.research.feature_profile = "price_volume"
    cfg.research.universe_mode = "pit_liquidity"
    cfg.start_date = START

    prepared = prepare_window(ds, cfg, START, END)
    close = prepared["close"]

    # build tradability screens (isST / tradestatus) from panels, aligned to close
    is_st = pd.DataFrame({c: p["isST"] for c, p in ds.panels.items()}).reindex(columns=close.columns)
    tstat = pd.DataFrame({c: p["tradestatus"] for c, p in ds.panels.items()}).reindex(columns=close.columns)

    reviews = [d for d in review_dates(ds.calendar, "monthly") if START <= str(pd.Timestamp(d).date()) <= END]

    arms = {}
    for policy in POLICIES:
        sched = momentum_schedule(close, is_st, tstat, reviews, industry_policy=policy)
        arms[("qlab_mom12_1", policy)] = dict(strategy="schedule", target_schedule=sched)
    # reference arms (their code path) under both policies
    for policy in POLICIES:
        for s in ("monthly_equal", "vol_matched_equal"):
            arms[(s, policy)] = dict(strategy=s)

    rows = []
    for (label, policy), kwargs in arms.items():
        print(f"[qlab_b] replay {label}/{policy}", flush=True)
        run = Engine(cfg).run(ds, start=START, end=END, data_mode="free_research",
                             prepared=prepared, industry_policy=policy, crowding=False, **kwargs)
        st = account_statistics(run)
        rows.append(dict(arm=label, policy=policy, annual=st["conditional_metrics"]["annual_return"],
                         total=st["conditional_metrics"]["total_return"],
                         mdd=st["conditional_metrics"]["max_drawdown"],
                         sharpe=st["conditional_metrics"].get("sharpe"),
                         mean_w=st["mean_stock_weight"], mean_hold=st["mean_holdings"],
                         fees=st["fees"] + st["slippage"], health=st["run_health"],
                         net_profit=st["net_profit"], ret=run["daily_return"]))
        print(f"   annual={st['conditional_metrics']['annual_return']:.2%} "
              f"net={st['net_profit']:,.0f} cashw={st['mean_stock_weight']:.1%}", flush=True)

    # paired excess of my arm vs references, per policy
    paired = {}
    for policy in POLICIES:
        mine = next(r for r in rows if r["arm"] == "qlab_mom12_1" and r["policy"] == policy)["ret"]
        for ctrl in ("monthly_equal", "vol_matched_equal"):
            b = next(r for r in rows if r["arm"] == ctrl and r["policy"] == policy)["ret"]
            x = (mine - b).dropna()
            paired[f"{policy}__qlab_vs_{ctrl}"] = dict(
                annualized_mean_daily_net_excess=float(x.mean() * 252),
                ci20=block_bootstrap_ci(x, seed=SEED, block=20),
                ci60=block_bootstrap_ci(x, seed=SEED, block=60))

    out = ROOT / "qlab_b" / "results"
    out.mkdir(exist_ok=True)
    (out / "paired.json").write_text(json.dumps(paired, default=str, indent=2))

    print("\n| arm | policy | annual | total | mdd | mean_w | fees+slip |")
    print("|---|---|---:|---:|---:|---:|---:|")
    for r in rows:
        print(f"| {r['arm']} | {r['policy']} | {r['annual']:.2%} | {r['total']:.2%} | "
              f"{r['mdd']:.2%} | {r['mean_w']:.1%} | {r['fees']:,.0f} |")
    print("\nPaired mean-daily net excess (annualized) + block CI:")
    print(json.dumps(paired, default=str, indent=2))
    print("\nVerdict per hypothesis.md (do not change thresholds):")
    for policy in POLICIES:
        me = next(r for r in rows if r["arm"] == "qlab_mom12_1" and r["policy"] == policy)
        c1 = next(r for r in rows if r["arm"] == "monthly_equal" and r["policy"] == policy)
        c2 = next(r for r in rows if r["arm"] == "vol_matched_equal" and r["policy"] == policy)
        win = me["annual"] > c1["annual"] and me["annual"] > c2["annual"]
        print(f"  {policy}: qlab annual={me['annual']:.2%} vs eq={c1['annual']:.2%}, "
              f"vol={c2['annual']:.2%} -> P1(a) {'PASS' if win else 'FAIL'}; P1(b) "
              f"{'TBD(positive excess?)' }")


if __name__ == "__main__":
    main()
