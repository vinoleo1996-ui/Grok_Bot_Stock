"""Regression: CB panel filter vs full must not diverge impact inputs / fill path.

Root cause (output/v3/cb_premresid_cov/NAV_GAP_AUDIT_ZH.md): Strategy recon
``filter_cb_panels`` (schedule-only columns) vs Beta full ``cb_panels`` forked
PREMRESID impact/NAV (X2 −31/−67bp). Eng rule: ``prepare_panels_for_execution``
keeps full panels; fill order is code-sorted so panel width cannot reorder cash-
constrained fills for the same schedule names.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from quantlab.platform.execution import (
    ExecConfig,
    ExecPanels,
    impact_inputs_for_codes,
    prepare_panels_for_execution,
    run_weight_schedule,
    subset_exec_panels,
)


GOLD = "sh.518880"
# Extra CB-like names that inflate panel width (not in schedule)
EXTRA = [f"sh.113{str(i).zfill(3)}" for i in range(10, 30)]
TRADED = ["sh.113050", "sz.128136", GOLD]


def _synth_panels(codes, n=40, start="2024-06-03"):
    idx = pd.bdate_range(start, periods=n)
    rng = np.random.default_rng(42)
    close = {}
    for c in codes:
        px0 = 6.0 if c == GOLD else 120.0 + (hash(c) % 50)
        close[c] = px0 * np.cumprod(1 + rng.normal(0.0005, 0.012, n))
    c = pd.DataFrame(close, index=idx)
    o = c.shift(1).fillna(c) * 1.0005
    # Tight volume so participation_cap + cash compete across names
    vol = pd.DataFrame({k: (5e4 if k != GOLD else 5e6) for k in codes}, index=idx, dtype=float)
    amt = vol * c
    return ExecPanels(close=c, open=o, volume=vol, amount=amt).aligned()


def _schedule(idx, codes_w):
    # Rebalance every 5 sessions across traded names (weights sum ~1)
    sch = {}
    w = {c: 1.0 / len(codes_w) for c in codes_w}
    for t in idx[::5]:
        sch[t] = dict(w)
    return sch


def test_impact_inputs_same_ids_through_subset():
    """Same ids through filter → same ADV/SIG/close/amount (no cross-section leak)."""
    all_codes = EXTRA + TRADED
    full = _synth_panels(all_codes)
    narrow = subset_exec_panels(full, TRADED)
    a = impact_inputs_for_codes(full, TRADED, sigma_window=10, adv_window=10)
    b = impact_inputs_for_codes(narrow, TRADED, sigma_window=10, adv_window=10)
    assert set(a) == set(b) == set(TRADED)
    for c in TRADED:
        for k in ("close", "amount", "adv", "sigma"):
            pd.testing.assert_series_equal(a[c][k], b[c][k], check_names=False)


def test_prepare_panels_keeps_full_width():
    full = _synth_panels(EXTRA + TRADED)
    sch = _schedule(full.close.index, TRADED)
    p = prepare_panels_for_execution(full, sch)
    assert list(p.close.columns) == list(full.close.columns)
    assert p.close.shape[1] > len(TRADED)


def test_full_vs_schedule_only_impact_path_aligned():
    """Canonical full path vs schedule-only subset must match impact/fills for same schedule.

    Would have failed before code-sorted fills when panel width changed column indices
    under cash/participation pressure (NAV-gap class bug).
    """
    all_codes = EXTRA + TRADED
    full = _synth_panels(all_codes)
    sch = _schedule(full.close.index, TRADED)
    cfg = ExecConfig.strategy_v1(
        impact_k=1.0,
        participation_cap=0.10,
        min_trade_value=100.0,
        enforce_limits=False,
    )
    p_full = prepare_panels_for_execution(full, sch)  # policy=full
    p_narrow = prepare_panels_for_execution(full, sch, policy="schedule_only")
    assert p_narrow.close.shape[1] == len(TRADED)
    assert p_full.close.shape[1] == len(all_codes)

    r_full = run_weight_schedule(p_full, sch, initial_cash=600_000.0, config=cfg, record_fills=True)
    r_narrow = run_weight_schedule(p_narrow, sch, initial_cash=600_000.0, config=cfg, record_fills=True)

    assert r_full["costs"]["impact"] == pytest.approx(r_narrow["costs"]["impact"], rel=0, abs=1e-6)
    assert r_full["total_cost"] == pytest.approx(r_narrow["total_cost"], rel=0, abs=1e-6)
    assert r_full["fill_ratio"] == pytest.approx(r_narrow["fill_ratio"], rel=0, abs=1e-9)
    pd.testing.assert_series_equal(r_full["nav"], r_narrow["nav"], check_names=False, atol=1e-6)


def test_prepare_rejects_missing_schedule_codes():
    full = _synth_panels(TRADED)
    with pytest.raises(KeyError, match="missing"):
        prepare_panels_for_execution(full, {full.close.index[0]: {"sh.999999": 1.0}})
