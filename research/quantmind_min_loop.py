#!/usr/bin/env python3
"""CLI: QuantMind-style min loop (preflight→evolve→backtest→explain→export).

Default: synthetic smoke (no market data, no sealed).
Real explore: pass --panels-dir with structural parquet panels + label;
  still requires Leo explore approval in Alpha chat — this CLI does not open sealed.

Examples:
  PYTHONPATH=/workspace/QuantLab /workspace/qlvenv/bin/python research/quantmind_min_loop.py --smoke
  PYTHONPATH=/workspace/QuantLab /workspace/qlvenv/bin/python research/quantmind_min_loop.py \\
      --smoke --capital 1000000 --direction consecutive_board_promote

promotion_approved=false always. Memory target <2.5GB.
"""
from __future__ import annotations

import argparse
import json
import resource
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/workspace/QuantLab")
sys.path.insert(0, str(ROOT))

from quantlab.factors.ai_factory.evaluate import align_open_open_label  # noqa: E402
from quantlab.factors.ai_factory.quantmind_loop import (  # noqa: E402
    CAPITAL_CNY_ALLOWED,
    Direction,
    run_quantmind_loop,
)
from quantlab.factors.ai_factory.search import GPConfig  # noqa: E402
from quantlab.factors.ai_factory.structural_leaves import (  # noqa: E402
    build_easystock_panels,
)


def mem_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


DIRECTIONS: dict[str, Direction] = {
    "consecutive_board_promote": Direction(
        direction_id="consecutive_board_promote",
        text_zh="连板晋级率下行时，高位连板股次日拥挤卖压；用晋级率与连板高度交互做空最拥挤端。",
        mechanism_tag="consecutive_board",
        who_pays_zh="晋级失败的追板资金与被迫隔夜的T+1买家。",
        seed_exprs=[
            "neg(lu_height)",
            "neg(mul(lu_height, lu_promote_rate))",
            "rank(lu_promote_rate)",
            "neg(mkt_max_height)",
        ],
    ),
    "theme_breadth_fade": Direction(
        direction_id="theme_breadth_fade",
        text_zh="题材宽度（涨停扩散）见顶回落时，主题拥挤买方成为卖方；宽度差分做β/拥挤调节。",
        mechanism_tag="theme",
        who_pays_zh="一日游题材资金与跟风ETF申购盘。",
        seed_exprs=[
            "neg(mkt_lu_breadth)",
            "neg(ts_delta_5(mkt_lu_breadth))",
            "mul(lu_height, mkt_lu_breadth)",
        ],
    ),
    "emotion_ebb": Direction(
        direction_id="emotion_ebb",
        text_zh="情绪退潮：市场最大连板高度回落叠加晋级率走弱，预测中大盘短窗超额偏弱。",
        mechanism_tag="limit_up",
        who_pays_zh="杠杆短线盘去杠杆时砸给指数成分承接盘。",
        seed_exprs=[
            "neg(mkt_max_height)",
            "sub(lu_promote_rate, delay_1(lu_promote_rate))",
            "neg(lu_count_5)",
        ],
    ),
}


def _synth(n_dates: int = 60, n_assets: int = 40, seed: int = 7):
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2024-06-03", periods=n_dates)
    cols = [f"a{i:02d}" for i in range(n_assets)]
    rets = rng.normal(0, 0.012, size=(n_dates, n_assets))
    open_px = pd.DataFrame(100 * np.cumprod(1 + rets, axis=0), index=dates, columns=cols)
    # synthetic limit-ups: fat-tail positive days
    shock = rng.random(size=(n_dates, n_assets)) > 0.93
    lu_flag = pd.DataFrame(shock, index=dates, columns=cols)
    # streak
    streak = np.zeros((n_dates, n_assets), dtype=np.float32)
    for i in range(n_dates):
        if i == 0:
            streak[i] = shock[i].astype(np.float32)
        else:
            streak[i] = np.where(shock[i], streak[i - 1] + 1.0, 0.0)
    lu_streak = pd.DataFrame(streak, index=dates, columns=cols)
    easy = build_easystock_panels(lu_flag=lu_flag, lu_streak=lu_streak, mask=None)
    panels = {
        "limit_up_flag": lu_flag.astype("float32"),
        "lu_streak": lu_streak,
        "lu_count_5": lu_flag.astype("float32").rolling(5, min_periods=1).sum(),
        "overnight_ret": pd.DataFrame(rng.normal(0, 0.005, size=open_px.shape), index=dates, columns=cols),
        "intraday_ret": pd.DataFrame(rng.normal(0, 0.008, size=open_px.shape), index=dates, columns=cols),
        **easy,
    }
    # simpler days_since
    ds = np.full((n_dates, n_assets), np.nan, dtype=np.float32)
    last = np.full(n_assets, -1, dtype=np.int32)
    for i in range(n_dates):
        hit = shock[i]
        last[hit] = i
        ok = last >= 0
        ds[i, ok] = (i - last[ok]).astype(np.float32)
    panels["days_since_lu"] = pd.DataFrame(ds, index=dates, columns=cols)
    label = align_open_open_label(open_px)
    # public control panels (novelty corr only)
    public = {
        "ret_20": open_px.pct_change(20),
        "rv_20": open_px.pct_change().rolling(20).std(),
        "turn_20": open_px.pct_change().abs().rolling(20).mean(),
    }
    return panels, label, public


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="synthetic panels only")
    ap.add_argument("--capital", type=int, default=600_000, choices=sorted(CAPITAL_CNY_ALLOWED))
    ap.add_argument(
        "--direction",
        default="consecutive_board_promote",
        choices=sorted(DIRECTIONS.keys()),
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=ROOT / "output/ai_factor/quantmind_smoke",
    )
    ap.add_argument("--gp-evals", type=int, default=12, help="tiny GP budget for smoke")
    ap.add_argument("--seed", type=int, default=20261011)
    args = ap.parse_args()

    if not args.smoke:
        print("Only --smoke is enabled in this CLI for now (no sealed / no full explore).", file=sys.stderr)
        return 2

    panels, label, public = _synth()
    direction = DIRECTIONS[args.direction]
    ledger = args.out / "ledger_smoke.jsonl"
    if ledger.exists():
        ledger.unlink()
    cfg = GPConfig(
        population=6,
        generations=2,
        max_evaluations=args.gp_evals,
        top_k=8,
        seed=args.seed,
        universe="synthetic_midlarge",
        cost=0.0025,
        window="synthetic_smoke_l1c",
        ledger_path=ledger,
        structural_only=True,
        ban_textbook=True,
        use_l1b_fitness=True,
        public_panels=public,
    )
    print(f"[quantmind] start capital={args.capital} dir={args.direction} mem={mem_mb():.0f}MB", flush=True)
    result = run_quantmind_loop(
        panels=panels,
        label=label,
        direction=direction,
        out_dir=args.out,
        capital_cny=args.capital,
        public_panels=public,
        gp_config=cfg,
    )
    peak = mem_mb()
    summary = {
        "promotion_approved": False,
        "capital_cny": result.capital_cny,
        "ledger_N": result.ledger_N,
        "evaluations": result.evaluations,
        "n_top_k": len(result.top_k),
        "export_paths": result.export_paths,
        "stage_ok": {s.stage: s.ok for s in result.stages},
        "peak_mem_mb": peak,
        "notes": result.notes,
        "sealed": False,
    }
    (args.out / "cli_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"[quantmind] peak_mem_mb={peak:.1f}", flush=True)
    return 0 if all(s.ok for s in result.stages if s.stage != "preflight" or s.ok) and peak < 2500 else 1


if __name__ == "__main__":
    raise SystemExit(main())
