# Amihud winsorize / MAD silent-zero fix

**Date:** 2026-10-10 (ET)  
**Owner:** Platform Eng  
**promotion_approved / overall gate:** unchanged (this is a numerical hygiene fix only)

## Root cause

1. `quantlab/factors/engine.py` `winsorize_zscore` computed
   `mad = median(|x-med|) * 1.4826`. When `mad < 1e-9` it fell back to `std`;
   when that was also `< 1e-9` it returned `x * 0.0` with **no note**.
2. Main-book Amihud in `quantlab/factors/p1_factor_lib.py`
   `compute_liquidity_family` used raw `|ret| / amount` (amount in CNY yuan).
   Typical raw Amihud is ~`1e-11`, so MAD and std often both sit below `1e-9`.
   `_cs_z` → `winsorize_zscore` then **silent-zeroed the whole cross-section**.
3. Symptom (Alpha): IC of `LIQ02_AMIHUD` became NaN after 2025-12 in
   `output/alpha/TRADABLE_IC_V1_ZH.md` §3 until research scaled by `×1e9`
   (`research/tradable_ic_v1.py` L36–38). Main-book did not scale.

Alpha minimal repro (pre-fix):

```python
x = pd.Series(np.random.uniform(1e-12, 5e-11, size=2000))
assert (winsorize_zscore(x) == 0).all()   # silent all-zero
assert winsorize_zscore(x * 1e9).std() > 0.5
```

## Fix (Eng-owned)

1. **Defense in depth — scale Amihud**  
   `AMIHUD_RAW_SCALE = 1e9` applied to daily `|r|/amount` before the 20d mean
   and `_cs_z`. Rank-invariant; matches Alpha research / attrib magnitude
   convention (attrib still uses **+** sign; main-book keeps **−**; sign is a
   separate Leo decision — weights not changed here).

2. **Shared helper — no silent zero**  
   `winsorize_zscore(..., degenerate_fallback='rank')` (new default):
   - MAD ok → MAD z (unchanged)
   - MAD &lt; eps → std fallback (unchanged)
   - MAD and std &lt; eps → **average-rank z** (preserves order)
   - Truly constant CS → zeros **with** note `constant_cross_section_n=…`
   - Opt-in legacy: `degenerate_fallback='zero'` still returns `x*0` but records
     `zero_legacy` in `WINSORIZE_LAST_DIAG` / `return_diag=True`.

3. `_cs_z(..., notes_out=)` forwards winsorize diag notes into liquidity family notes.

## Before / after

| Input | Before | After (default) |
|-------|--------|-----------------|
| Amihud-scale CS ~1e-11 | all zeros, no note | rank (or std) z, note `mad_std_below_eps_rank_fallback_n=…` |
| Amihud via `compute_liquidity_family` | often all-zero z | ×1e9 then MAD z; note `amihud_scaled_x1e9_rank_invariant` |
| Normal factors (O(1) scale) | MAD z ±4 clip | unchanged |
| Constant CS | silent zeros | zeros + `constant_cross_section` note |
| `degenerate_fallback='zero'` | n/a | legacy zeros + explicit note |

## Tests

`tests/test_winsorize_mad_amihud.py` — Alpha repro, legacy opt-in, constant CS,
normal scale, liquidity-family path with CNY-scale amount.

## Out of scope

- Sign conflict (− main-book vs + `research/attrib_v2/factor_diag.py`): Leo decides; Eng did not flip weights.
- Alpha research script `research/tradable_ic_v1.py` still has a local copy of the old helper (already ×1e9 on Amihud); not rewritten.
- No Full D1 / Strategy runner edits; overall promotion gate untouched.
