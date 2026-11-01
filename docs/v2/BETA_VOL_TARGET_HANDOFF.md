# Beta vol-target / β-budget → Strategy handoff

> **Update 2026-10-10 21:30 ET:** a standalone small-cap β sleeve (`SmallcapBetaSleeveProvider`, tiers 10/15/20% of book, **not** bound by `max_etf`) now runs in parallel with this 510300 sleeve. It supersedes the in-`max_etf` satellite. Its weight comes out of `residual_book_weight_cap`. See `BETA_SMALLCAP_STANDALONE.md`. Core 510300 logic here is unchanged.


> 2026-10-10 · `promotion_approved=false` · SW_L1 `promotable=false`  
> Owner: Beta (vol / β / drawdown research) · Consumer: Strategy (portfolio constructor)

## What Beta owns now

`PrototypeBetaSleeveProvider` / `VolTargetBetaSleeveProvider` scale the 510300
sleeve toward Mandate knobs, then apply a research drawdown risk-off scaler:

| Knob | Value | Source |
|---|---|---|
| `target_annual_vol` | 0.16 | `MandateV2.risk` |
| `target_beta_vs_benchmark` | 0.70 | `MandateV2.risk` |
| `target_beta_band` | [0.5, 0.85] | `MandateV2.risk` |
| `max_etf_sleeve_weight` | 0.40 | `MandateV2.portfolio_limits` |
| `vol_targeting_enabled` | true | `MandateV2.risk` |
| drawdown scaler | L1–L4 | Mandate `risk.drawdown_scaler` (research mapping) |

**Research formula** (unit-ETF metrics = 100% sleeve exposure):

```
w_vol  = target_annual_vol / realized_vol
w_beta = target_beta / unit_beta
etf_pre_dd = min(w_vol, w_beta, max_etf_sleeve_weight)

# Drawdown risk-off (510300 peak→trough, unreset):
#   L1+ (dd≥12%): effective_target_vol = target_vol * 0.75; re-scale
#   L2  (dd≥18%): also risk_asset_cap = 0.60
#   L3  (dd≥22%): also risk_asset_cap = 0.30
#   L4  (dd≥25%): research cap 0.15 (Mandate: human confirm — not automated)
etf_sleeve_weight = min(etf_pre_dd, re-scaled with effective vol & caps)
# never raises weight vs etf_pre_dd

cash_weight = max(min_cash_buffer_normal, min(default_cash, 1 - etf))
residual_book_weight_cap = 1 - etf_sleeve_weight - cash_weight
```

- Trailing window: 60 trading sessions (price returns on `sh.510300` closes).
- β vs `sh.000300` from D0 `benchmark.parquet` when overlap exists; else
  research fallback `unit_beta=1.0` with flag `unit_beta_assumed_1_index_gap`.
- Caller may pass `realized_vol` / `portfolio_beta` into `plan()` as unit-ETF
  overrides.
- **No** Sharpe / PnL / promotion narrative. `promotion_approved` stays false
  and `BetaSleevePlan` still raises if set true.
- **Never** raises `max_etf_sleeve_weight`.

## Mandate β-gap contract (typed on `BetaSleevePlan`)

P2.1 diagnosis: gap is **structural** (`max_etf × unit_β ≈ 0.39 < 0.70`), not an OLS bug. See `BETA_P2_IMPL_DIAGNOSIS.md`. Closing **portfolio** β uses Strategy residual sizing via `residual_weight_to_hit_target_beta` (default `assumed_residual_unit_beta=1.0`). Do **not** raise `max_etf` or edit Mandate to paper over.

## Mandate β-gap contract (typed on `BetaSleevePlan`)

Beta reports the clip gap; Strategy owns residual β. Measurable fields:

| Field | Meaning |
|---|---|
| `target_beta_vs_benchmark` | Mandate target (0.70) |
| `unit_beta` | Trailing ETF vs index β (≈1) |
| `implied_sleeve_beta` | `etf_sleeve_weight * unit_beta` |
| `beta_gap_to_mandate` | `target_beta - implied_sleeve_beta` (signed) |
| `residual_beta_budget_for_strategy` | `max(0, beta_gap_to_mandate)` |
| `implied_beta_in_band` | Whether implied sleeve β ∈ `[0.5, 0.85]` |
| `beta_gap_is_structural` | `max_etf×unit_β < target_β` |
| `max_sleeve_beta_at_max_etf` | Structural sleeve ceiling |
| `residual_weight_to_hit_target_beta` | Strategy residual gross to close portfolio β |
| `implied_portfolio_beta_at_residual_fill` | Sleeve + that residual × assumed unit β |
| `max_etf_raised` | Always `false` on handoff surface |

Typical clipped state (no extra DD cut): `etf=0.40`, `unit_beta≈0.98` →
`implied_sleeve_beta≈0.39`, `beta_gap≈0.31`, `residual_beta_budget≈0.31`,
`implied_beta_in_band=false`. Strategy may take residual long industry-neutral
exposure under `residual_book_weight_cap` to close portfolio β — **Strategy-owned**.

## Drawdown scaler fields

| Field | Meaning |
|---|---|
| `etf_drawdown` | Peak-to-trough DD of 510300 close (unreset) |
| `drawdown_tier` | `none` / `L1` / `L2` / `L3` / `L4_extreme` |
| `drawdown_scale_applied` | Tier engaged (even if weight stuck at max_etf bind) |
| `etf_weight_pre_drawdown` | Weight after vol/β/max_etf, before DD |
| `effective_target_annual_vol` | Post-L1 vol budget (0.16 or 0.12) |

Example: late session ≈2026-10-09 with full-history DD≈0.24 → **L3** → ETF
cut from 0.40 → **0.30**, residual_cap rises; β-gap widens accordingly.

## Strategy industry-neutral interface

| Field | Role |
|---|---|
| `BetaSleevePlan.etf_sleeve_weight` | Broad beta sleeve size |
| `BetaSleevePlan.cash_weight` | Active cash buffer |
| `BetaSleevePlan.residual_book_weight_cap` | Pass as `PortfolioConstructorV2.construct(book_weight_cap=...)` |
| `residual_beta_budget_for_strategy` | Explicit β shortfall for Strategy to measure |
| `industry_neutral_residual_book` | Mandate true — residual book should be industry-neutral |
| `industry_scheme` | `SW_L1` |
| `max_industry_weight` / `unknown_industry_cap` | Constructor caps |

### SW_L1 research-only (hard)

- Path: `data/v2/sw_l1_pit/industry_members_sw_l1.parquet`
- Honor `data/v2/sw_l1_pit/NOT_PROMOTION_GRADE.md`
- `sw_l1_promotable=false` always; **never** flip `promotion_approved`
- Free-source PIT is fine for research neutralization stubs; not promotion evidence

See also `strategy_handoff_surface()` on the Beta provider and
`docs/v2/STRATEGY_PORTFOLIO_SKELETON.md`.

**Consumer status (2026-10-10):** Strategy smoke prefers live
`VolTargetBetaSleeveProvider.plan()` and passes `residual_book_weight_cap` into
`PortfolioConstructorV2.construct(book_weight_cap=...)`. Strategy owns residual
β vs Mandate band; does not raise `max_etf` or flip promotion. Prefer typed
plan fields (`implied_sleeve_beta`, `beta_gap_to_mandate`, …) over parsing
`todos` when available.

## Smoke

```bash
cd /workspace/QuantLab
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.v2_beta_smoke
```

Asserts gap-field consistency, L1 vol-mult on mid DD, L3 cap on late DD;
prints weights / gap / drawdown blocks only — no Sharpe/PnL.

## Open blockers

- D0 index (`sh.000300`) ends 2026-06-30 → late sessions use trailing overlap
  ending at index max (`beta_window_ends_before_session` flag); vol / DD windows
  stay as-of the decision session on ETF closes.
- OHLC quality gap on 510300 (~0.2% mismatch noted by Data) — Beta does not
  invent bars; uses close price returns as-is.
- L4 human-confirm path is **not** automated (research cap 0.15 only).
- Drawdown uses ETF price peak (not full portfolio NAV) — portfolio-level DD
  remains Strategy/Eng future work.
- Eng proto/eng smokes may still say "idle" in places; live weights are
  vol-targeted + DD-scaled research values.


## Small-cap satellite menu (`smallcap_satellite`, default OFF)

Optional research arm for Strategy A/B. See `BETA_SMALLCAP_SATELLITE.md`.

- Provider: `VolTargetBetaSleeveProvider(mandate, smallcap_satellite=True)`
- Splits existing ETF budget by contribution weights; **does not** raise `max_etf`
- Core remains `load_etf_510300()`; satellite from `data/etf/universe/equity_etf_daily.parquet`
- Plan fields: `core_etf_weight`, `satellite_etf_weight`, `contribution_weight_*`, `satellite_code`
- Handoff: `compare_arms`, `smallcap_satellite_default=false`


## B6 Strategy wiring status

- Field: `BetaSleevePlan.residual_weight_to_hit_target_beta` (+ `implied_portfolio_beta_at_residual_fill`)
- Beta status: **delivered** on plan / `strategy_handoff_surface`
- Strategy: consume after **P0** cost path to size residual toward portfolio β≈0.70
- Does not raise `max_etf`; Mandate unchanged
