"""Synthetic smoke for L1 AI factory. No market data. promotion_approved must stay False."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from quantlab.factors.ai_factory.evaluate import (
    align_open_open_label,
    assert_no_lookahead_label,
    walk_forward_ic,
)
from quantlab.factors.ai_factory.search import GPConfig, gp_search
from quantlab.factors.ops import Expr, apply_expr, parse_expr

ROOT = Path("/workspace/QuantLab")
SMOKE_LEDGER = ROOT / "output/ai_factor/ledger_smoke.jsonl"
TOPK_DIR = ROOT / "output/ai_factor/gp_smoke"


def _synth(n_dates=80, n_assets=30, seed=0):
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2020-01-01", periods=n_dates)
    cols = [f"a{i:02d}" for i in range(n_assets)]
    # open random walk
    rets = rng.normal(0, 0.01, size=(n_dates, n_assets))
    open_px = pd.DataFrame(100 * np.cumprod(1 + rets, axis=0), index=dates, columns=cols)
    close = open_px * (1 + rng.normal(0, 0.002, size=open_px.shape))
    ret_1 = close.pct_change()
    ret_5 = close.pct_change(5)
    panels = {
        "ret_1": ret_1,
        "ret_5": ret_5,
        "ret_20": close.pct_change(20),
        "log_vol": np.log(ret_1.abs() * 1e6 + 1),
        "turn_20": ret_1.abs().rolling(20).mean(),
        "rv_20": ret_1.rolling(20).std(),
        "resid_ret_20": ret_1.rolling(20).mean(),
    }
    label = align_open_open_label(open_px)
    return panels, label, open_px, dates


def test_label_no_lookahead():
    _, label, open_px, _ = _synth()
    assert_no_lookahead_label(open_px, label)
    # feature date t must not equal open[t+1]/open[t]-1 (that would be same-day)
    bad = open_px.shift(-1) / open_px - 1.0
    # label should match shift(-2)/shift(-1)-1, not shift(-1)/open-1
    m = label.notna() & bad.notna()
    # correlation can exist but exact equality should fail on majority
    eq = np.isclose(label.to_numpy(), bad.to_numpy())
    assert eq[m.to_numpy()].mean() < 0.5


def test_gp_smoke_topk_and_ledger_and_promotion_false():
    if SMOKE_LEDGER.exists():
        SMOKE_LEDGER.unlink()
    panels, label, _, dates = _synth()
    cfg = GPConfig(
        population=8,
        generations=2,
        max_evaluations=20,
        top_k=5,
        seed=42,
        window="synthetic_smoke",
        ledger_path=SMOKE_LEDGER,
    )
    res = gp_search(panels, label, cfg)
    assert res.promotion_approved is False
    assert res.evaluations > 0
    assert SMOKE_LEDGER.exists()
    lines = [json.loads(x) for x in SMOKE_LEDGER.read_text().splitlines() if x.strip()]
    assert len(lines) == res.evaluations
    assert lines[-1]["N"] == len(lines)
    assert all(r.get("promotion_approved") is False for r in lines)
    assert len(res.top_k) <= cfg.top_k
    TOPK_DIR.mkdir(parents=True, exist_ok=True)
    rows = [c.as_row() for c in res.top_k]
    (TOPK_DIR / "top_k.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False))
    # walk_forward stub
    if res.top_k:
        ev = walk_forward_ic(res.top_k[0].expr, panels, label, list(dates[:50]))
        assert ev.promotion_approved is False


def test_ops_rank_serializable():
    panels, _, _, _ = _synth(n_dates=40, n_assets=12)
    e = parse_expr(("op", "rank", ("leaf", "ret_1")))
    out = apply_expr(e, panels)
    assert out.shape == panels["ret_1"].shape
