"""Regression: Amihud-scale MAD must not silent-zero the cross-section."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from quantlab.factors.engine import WINSORIZE_LAST_DIAG, winsorize_zscore
from quantlab.factors.p1_factor_lib import AMIHUD_RAW_SCALE, compute_liquidity_family


def test_alpha_repro_tiny_amihud_scale_no_longer_silent_zero():
    """Alpha TRADABLE_IC_V1_ZH §3 minimal repro (amount in CNY → ~1e-11)."""
    rng = np.random.default_rng(0)
    x = pd.Series(rng.uniform(1e-12, 5e-11, size=2000))
    z, diag = winsorize_zscore(x, return_diag=True)
    # Must NOT silently all-zero under default safe fallback
    assert not (z == 0).all(), diag
    assert float(z.std()) > 1e-6, diag
    assert diag["mode"] in {"rank_fallback", "std_fallback", "raw_fallback"}, diag
    assert "n=" in str(diag.get("note") or "") or diag["mode"] != "mad"

    z2, diag2 = winsorize_zscore(x * 1e9, return_diag=True)
    assert float(z2.std()) > 0.5, diag2
    assert diag2["mode"] == "mad"


def test_legacy_zero_opt_in_still_available_but_noted():
    rng = np.random.default_rng(1)
    x = pd.Series(rng.uniform(1e-12, 5e-11, size=500))
    z, diag = winsorize_zscore(x, degenerate_fallback="zero", return_diag=True)
    assert (z == 0).all()
    assert diag["mode"] == "zero_legacy"
    assert "degenerate_zero_legacy" in diag["note"]


def test_constant_cs_zeros_with_explicit_note():
    x = pd.Series([3e-11] * 40)
    z, diag = winsorize_zscore(x, return_diag=True)
    assert (z == 0).all()
    assert diag["mode"] == "constant_cs_zero"
    assert "constant_cross_section" in diag["note"]


def test_normal_scale_unchanged():
    s = pd.Series([1.0, 2.0, 3.0, 2.2, 1.8, 100.0, -50.0])
    z, diag = winsorize_zscore(s, return_diag=True)
    assert np.isfinite(z).all()
    assert float(z.abs().max()) <= 4.0
    assert diag["mode"] == "mad"
    assert WINSORIZE_LAST_DIAG["mode"] == "mad"


def test_amihud_family_scales_x1e9_and_nonzero_z():
    """Main-book path: raw Amihud tiny unless ×1e9 before _cs_z."""
    rng = np.random.default_rng(42)
    n_days, n_ids = 60, 30
    idx = pd.bdate_range("2025-01-02", periods=n_days)
    cols = [f"s{i}" for i in range(n_ids)]
    # prices ~10, daily ret ~1%; amount in CNY yuan ~1e8–1e9 → |r|/amt ~1e-11
    close = pd.DataFrame(10.0, index=idx, columns=cols)
    for i, c in enumerate(cols):
        rets = rng.normal(0.0, 0.01, size=n_days)
        close[c] = 10.0 * np.cumprod(1.0 + rets)
    amount = pd.DataFrame(
        rng.uniform(5e7, 5e9, size=(n_days, n_ids)), index=idx, columns=cols
    )
    turnover = pd.DataFrame(0.02, index=idx, columns=cols)
    session = idx[-1].date()
    liq, notes = compute_liquidity_family(close, amount, turnover, session)
    amihud = liq["LIQ02_AMIHUD"]
    assert amihud, notes
    zs = np.array(list(amihud.values()), dtype=float)
    assert zs.std() > 1e-6, (zs[:5], notes)
    assert not np.allclose(zs, 0.0), notes
    assert any("amihud_scaled_x1e+09" in n or "amihud_scaled_x1e9" in n for n in notes), notes
    assert AMIHUD_RAW_SCALE == 1e9
