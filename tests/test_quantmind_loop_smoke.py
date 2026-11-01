"""Synthetic smoke: QuantMind five-stage loop + easy-stock leaves. No sealed."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from quantlab.factors.ai_factory.evaluate import align_open_open_label
from quantlab.factors.ai_factory.novelty import is_structural_expr, is_textbook_expr
from quantlab.factors.ai_factory.quantmind_loop import (
    Direction,
    run_quantmind_loop,
)
from quantlab.factors.ai_factory.search import GPConfig
from quantlab.factors.ai_factory.structural_leaves import (
    EASYSTOCK_STRUCTURAL_LEAVES,
    build_easystock_panels,
)
from quantlab.factors.ops import STRUCTURAL_LEAF_FEATURES

ROOT = Path("/workspace/QuantLab")
OUT = ROOT / "output/ai_factor/quantmind_smoke_test"


def _panels(n_dates=50, n_assets=25, seed=3):
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2024-06-03", periods=n_dates)
    cols = [f"s{i:02d}" for i in range(n_assets)]
    open_px = pd.DataFrame(
        100 * np.cumprod(1 + rng.normal(0, 0.01, size=(n_dates, n_assets)), axis=0),
        index=dates,
        columns=cols,
    )
    shock = rng.random(size=(n_dates, n_assets)) > 0.92
    lu_flag = pd.DataFrame(shock, index=dates, columns=cols)
    streak = np.zeros((n_dates, n_assets), dtype=np.float32)
    for i in range(n_dates):
        if i == 0:
            streak[i] = shock[i].astype(np.float32)
        else:
            streak[i] = np.where(shock[i], streak[i - 1] + 1.0, 0.0)
    lu_streak = pd.DataFrame(streak, index=dates, columns=cols)
    easy = build_easystock_panels(lu_flag=lu_flag, lu_streak=lu_streak)
    panels = {
        "limit_up_flag": lu_flag.astype("float32"),
        "lu_streak": lu_streak,
        "lu_count_5": lu_flag.astype("float32").rolling(5, min_periods=1).sum(),
        **easy,
    }
    label = align_open_open_label(open_px)
    public = {"ret_20": open_px.pct_change(20), "rv_20": open_px.pct_change().rolling(20).std()}
    return panels, label, public


def test_easystock_leaves_registered():
    for name in EASYSTOCK_STRUCTURAL_LEAVES:
        assert name in STRUCTURAL_LEAF_FEATURES
    assert is_structural_expr("lu_height")
    assert is_structural_expr("neg(lu_promote_rate)")
    assert is_textbook_expr("ret_20")
    assert is_textbook_expr("neg(rv_20)")


def test_quantmind_five_stage_smoke():
    if OUT.exists():
        for p in OUT.glob("*"):
            if p.is_file():
                p.unlink()
    panels, label, public = _panels()
    direction = Direction(
        direction_id="test_promote",
        text_zh="连板晋级率与高度交互（结构叶，不作公开价量因子）。",
        mechanism_tag="consecutive_board",
        who_pays_zh="追板失败资金。",
        seed_exprs=["neg(lu_height)", "rank(lu_promote_rate)", "ret_20"],  # ret_20 must be banned
    )
    ledger = OUT / "ledger.jsonl"
    cfg = GPConfig(
        population=4,
        generations=1,
        max_evaluations=8,
        top_k=5,
        seed=1,
        window="unit_smoke",
        ledger_path=ledger,
        structural_only=True,
        ban_textbook=True,
        use_l1b_fitness=True,
        public_panels=public,
    )
    res = run_quantmind_loop(
        panels=panels,
        label=label,
        direction=direction,
        out_dir=OUT,
        capital_cny=600_000,
        public_panels=public,
        gp_config=cfg,
    )
    assert res.promotion_approved is False
    assert [s.stage for s in res.stages] == [
        "preflight",
        "evolve",
        "backtest",
        "explain",
        "export",
    ]
    assert all(s.ok for s in res.stages)
    assert ledger.exists()
    lines = [json.loads(x) for x in ledger.read_text().splitlines() if x.strip()]
    assert len(lines) >= 1
    assert all(r.get("promotion_approved") is False for r in lines)
    # main top-k must not contain textbook
    for c in res.top_k:
        assert not is_textbook_expr(c["expr"])
        assert is_structural_expr(c["expr"])
        assert c.get("who_pays_zh")
    assert (OUT / "explain.json").exists()
    assert (OUT / "top_k.json").exists()
    # capital must be Leo AUM
    assert res.capital_cny in (600_000, 1_000_000)


def test_textbook_direction_rejected_in_preflight():
    panels, label, public = _panels(n_dates=30, n_assets=12)
    direction = Direction(
        direction_id="bad",
        text_zh="20日反转与低波选股",
        mechanism_tag="limit_up",
        who_pays_zh="x",
        seed_exprs=["neg(lu_height)"],
    )
    res = run_quantmind_loop(
        panels=panels,
        label=label,
        direction=direction,
        out_dir=OUT / "bad_dir",
        capital_cny=1_000_000,
        public_panels=public,
        gp_config=GPConfig(population=0, generations=0, max_evaluations=0, ledger_path=OUT / "bad_ledger.jsonl"),
    )
    assert res.stages[0].stage == "preflight"
    assert res.stages[0].ok is False
    assert "textbook_direction_lexicon" in res.stages[0].payload["errors"]
