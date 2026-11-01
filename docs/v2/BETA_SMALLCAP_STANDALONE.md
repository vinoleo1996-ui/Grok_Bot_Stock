# Standalone small-cap β sleeve (research)

> 2026-10-10 · Leo · `promotion_approved=false` · Mandate JSON **not** edited  
> Supersedes the default-OFF satellite rule (small-cap no longer forced inside `max_etf=0.40`).  
> Core 510300 sleeve unchanged.

## Status banner (read first)

| Window | Ranking / basket status |
|---|---|
| **2015-01-05 onward** | **COMPLETE under B1.** Primary as-of float mktcap: `data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet` (5,831 names incl. delisted; yuan; research-grade; manifest alongside). Absolute band **3001–5000** when universe ≥ 5,000; if 3,001 ≤ N < 5,000 use 3001–N; if N < 3,001 fall back to **relative bottom 40%** (2015–2017). |
| Pre-2015 | Out of scope for this panel. |

Other switches (current defaults):
- Research profile: **~50 names**, notional **5,000,000 CNY**
- Live 600k profile: **20–30 names**, per-name min weight 0.5%, retention buffer **2×N** (ON when `current=` passed)
- Drawdown brake: provider default **OFF**; compare arm only
- Terminal delist marks **−50% / −100%**: **defined**, **not** wired into Beta harness / Strategy NAV yet (no invented claims on unfixed path)
- B3 2015-06~2016-01: descriptive stress JSON at `output/v2_proto/smallcap_b3_stress_2015.json` (not Strategy engine)

## What it is

A stock-basket β sleeve in **parallel** with core 510300. **Not** bound by `max_etf`. Tiers **T10 / T15 / T20 = 10% / 15% / 20% of book**.

| Piece | Path |
|---|---|
| Provider | `quantlab/beta/smallcap_sleeve.py` → `SmallcapBetaSleeveProvider` |
| Survivorship | `quantlab/beta/survivorship.py` |
| Brake / concave map | `quantlab/beta/dd_brake.py` |
| Config | `quantlab/beta/configs/smallcap_standalone_v1.json` |
| Main report | `scripts/smallcap_beta_sleeve.py` → `output/v2_proto/smallcap_beta_sleeve.json` |
| Live / retention / B1 | `smallcap_live_profile.py`, `smallcap_retention_compare.py`, `smallcap_survivorship_b1.py` |
| B2 engine cross-check | `docs/v2/BETA_B2_ENGINE_CROSSCHECK.md` + `scripts/smallcap_b2_engine_crosscheck.py` (skeleton; waiting on Eng E1) |

## Selection (per session) — B1 order

1. **Full-market float-cap rank** (survivorship B1): primary `float_mktcap_daily_from2015_tushare` (rolling mean); fallback attrib panel ∪ delisted daily. Absolute **3001–5000** / 3001–N / relative bottom 40% as above.
2. **Then** risk filters inside the band: history ≥253 sessions, **not ST**, trading, **close ≥ 2.0 CNY**, **not non-standard annual audit**, ADV60 ≥ 5M CNY.
3. Fundamentals: `pe_ttm > 0` and `0 < PB ≤ 3` (tier fallback if fewer than target pass).
4. Seeded order (sha256, seed 0); retention: keep current holdings while inside top `retain_top` (research 150 = 3×N) / live `retain_mult × N` (default 2).
5. SW_L1 industry cap ≤12 (research) or scaled for live N; ~50 names research / 20–30 live; equal weight inside the sleeve.

Old **"exclude smallest 30% market cap"** filter stays dropped (Leo). Mandate JSON untouched.

## Risk exclusions (after the band)

| Rule | Source | Status |
|---|---|---|
| ST / *ST | **Primary:** `data/v2/st_flags/is_st_daily_2018_2026.parquet`. Namechange PIT = fallback only. Delisted ST daily available for pre-panel work. | ON |
| Low price | raw close on session **< 2.0 CNY** | ON |
| Non-standard audit | latest **annual** opinion (`end_date` month 12) with `available_at` date **< session** from `data/v2/audit/audit_opinion_pit_tushare.parquet`; `is_non_standard` → exclude; missing → keep + count; lookback FY(session.year−2) | ON (`data_ready=true`) |

Not added (Leo): high-volatility de-risking; any market-cap-based exclusion beyond the band itself.

Typical funnel (B1; listed → band → filters): see `output/v2_proto/smallcap_beta_sleeve.json` and `smallcap_survivorship_b1.json`. On 2026-06-30 / 2026-10-09 later-delisted-in-band = 0 (microcaps below band); on 2023-12-29 stress formation ≈54.

## Risk controls

| Control | Setting |
|---|---|
| ADV floor | ADV60 ≥ 5M CNY |
| Single-name cap | min(0.5% of book, 3% of sleeve, Mandate 5%) |
| Capacity | order ≤ 1% of ADV; min trade 2000 CNY ×1.10 buffer; 100-share lots at research notional (5M) |
| Crowding | basket median turnover (20d vs trailing 250d percentile ≥ 0.9) or ≥20% of names up >25% in 20d → `crowding_flag` |
| Stress | `smallcap_crash_2024_02`: basket formed 2023-12-29, window 2024-01-02→2024-02-29 |

## Strategy API

```python
from quantlab.beta import SmallcapBetaSleeveProvider, VolTargetBetaSleeveProvider
sc = SmallcapBetaSleeveProvider(mandate)
core_plan = VolTargetBetaSleeveProvider(mandate).plan(session)
plan = sc.plan(session, current=prev_names, core_plan=core_plan)
plan.basket.names / .industry_mix / .filters_hit / .funnel
plan.tiers["T15"].name_weights          # per-name book weights
plan.crowding["crowding_flag"]
plan.interaction_with_core["T15"]       # residual_book_weight_cap_after, β gap after
sc.stress_test("smallcap_crash_2024_02")
```

The small-cap weight comes **out of the residual book**:
`residual_book_weight_cap_after = core residual_cap − tier`. B6 `residual_weight_to_hit_target_beta_after` is recomputed with the basket's descriptive β.

## Capital: research notional vs real account (Leo 21:35 ET)

Basket stays **~50 names** (no capacity-driven reduction of N). Capital is configurable in
`smallcap_standalone_v1.json → risk_controls`:

| Key | Value |
|---|---|
| `account_capital_cny` | 600,000 (real account, documented) |
| `research_notional_cny` | **5,000,000** (default for research) |
| `capacity_buffer` | 1.10 (overnight move to next-open fill + fees) |
| min trade | 2,000 CNY (Mandate `min_trade_notional_cny`; `lot_size_rounding=floor_buy_to_lot`) |

Rule: required capital `C = N / tier × 1.10 × max(2,000, 100 × max price in basket)`.
The binding constraint is always the one-lot cost of the most expensive name.

| Basket | Most expensive | T10 | T15 | T20 |
|---|---|---:|---:|---:|
| 2026-06-30 | sz.301257 45.38 | 2.50M | 1.66M | 1.25M |
| 2026-10-09 | sz.301257 40.30 | 2.22M | 1.48M | 1.11M |
| 2023-12-29 (stress) | sz.300860 54.63 | 3.00M | 2.00M | 1.50M |

5M is the next round number above the max (3.0M, T10 at stress formation), with headroom for pricier names
on later rebalances. At 5M every name clears one lot and the min trade at all tiers (lot-unaffordable = 0).
Per-name notional at 5M: T10 10,000 / T15 15,000 / T20 20,000 CNY.

## Promotion scope

Eng lifted the **platform** overall gate (`quantlab/promotion_gate.py`, `OVERALL_PROMOTION_OVERRIDE=None`; noted as
Leo-confirmed in the Eng chat 2026-10-10 20:52 ET), so `load_mandate_v2().promotion_approved` is now True. That is a
data/platform gate. **This sleeve stays research-only**: its plans/outputs carry `promotion_approved=false`; the gate
status is recorded in the output for visibility.

## Engine dependency

The current backtest engine books limit-up / limit-down / halt days as 0 return. **No CAGR/MDD/Sharpe** are reported for this sleeve until Strategy/Eng fix that. Stress and β numbers are labelled `pre_engine_fix_descriptive`.

## Known gaps / conflicts

- **Mandate conflict:** `universe.microcap_policy` still says `exclude_bottom_pct=0.30` and `microcap_as_universe_banned=true`. This sleeve overrides that for research only. Promotion would need a Mandate decision.
- **Open capacity note — 600k account cannot hold 50 names at T10/T15:** per name 1,200 / 1,800 CNY < 2,000 min trade; T20 (2,400) clears min trade but ~8–10 names fail one lot. Research therefore runs at a larger notional (below).
- `pe_ttm` is null for loss-makers in the Tushare daily_basic data, so null is treated as fail.
- The research panels start 2023-01-03, so at the 2023-12-29 stress formation the history is truncated (flagged). The min-history rule is relaxed to 222 sessions for that run only.
- SW_L1 comes from the Tushare research table (`promotable=false`).

## Drawdown brake + concave exposure map (research switch, Leo 2026-10-10 22:09 ET)

Source: literature card `output/research_survey/cards/68_2609.23272_DrawdownControlInvariance.md`.
Code: `quantlab/beta/dd_brake.py`; config block `dd_brake` in `configs/smallcap_standalone_v1.json`;
compare: `PYTHONPATH=. python scripts/smallcap_dd_brake_compare.py` → `output/v2_proto/smallcap_dd_brake_compare.json` (~7 s).

- **Rule**: e = floor + (1−floor)·clip(γ·(1 − (1−d)/z), 0, 1), z = sleeve NAV / running peak. Equals γ·cushion/V; capped at 1 = tier weight (never levers).
- **NAV basis = sleeve NAV**: Beta owns and can measure it; book NAV includes 510300/residual owned by Strategy. A book-level brake belongs to Strategy once the book is composed.
- **d = 0.20** (sleeve budget; ≈4% of book at T20), **floor = 0.20** (card 68: avoids the zero-exposure absorbing state), de-risk immediately, re-risk ≤ +0.05/day, trade band 0.05, decide at close d → trade at close d+1.
- **γ = 1/L = 3.47**, L = max(structural two-consecutive-limit-down loss of the board mix = 28.9% (many 20%-limit names), empirical worst 2-day EW loss in 2023 pre-window = 4.2%). For reference only, the worst 2-day loss inside the sim window was 15.5%.
- **Concavity**: e(z) is continuous, monotone, concave on the active region (checked numerically). There is no return target, no step ladder, and no adding risk when NAV is below target. Note that with d=0.20, γ·d=0.69, so the brake arm is never fully invested, even at a peak.
- **Default**: OFF on `SmallcapBetaSleeveProvider` (`provider_default_enabled=false`; the provider doesn't apply it). ON only as a compare arm.

### Results (window 2023-12-29 → 2026-10-09, 34 rebalances / 20 sessions; sleeve-level)
LABEL: research. These follow the fixed-engine rules (mark-to-close, limit/halt only block fills, blocked orders roll forward, Mandate costs, 2,000 CNY min trade). They come from a Beta harness that reuses `v2_execution_costs` primitives. This is NOT Strategy's paper engine and hasn't been cross-validated against it. Cash earns 0. Lots aren't modelled. One crash (2024-02) in about 2.8 years. Early rebalances use truncated history (panel start).

| Tier | Arm | CAGR | MDD | Calmar | Vol | Turnover/yr | Avg / min exp | Floor time | Book-contrib MDD |
|---|---|---|---|---|---|---|---|---|---|
| T10 | no brake | 11.1% | −39.0% | 0.29 | 31.3% | 2.92 | 0.97 / 0.95 | 0 | −3.9% |
| T10 | brake d20 | 3.0% | −23.5% | 0.13 | 15.5% | 2.06 | 0.53 / 0.29 | 0.6% | −2.3% |
| T10 | same-vol static 0.50 | 5.7% | −19.6% | 0.29 | 14.9% | 1.39 | 0.47 / 0.38 | 0 | −2.0% |
| T10 | ex-post best static 0.3 | 3.5% | −11.8% | 0.30 | 8.9% | 0.83 | 0.29 / 0.21 | 0 | −1.2% |
| T15 | no brake | 12.0% | −39.1% | 0.31 | 31.7% | 3.06 | 0.98 / 0.96 | 0 | −5.9% |
| T15 | brake d20 | 0.6% | −23.1% | 0.03 | 14.0% | 2.11 | 0.49 / 0.22 | 0.9% | −3.5% |
| T15 | same-vol static 0.44 | 5.2% | −17.3% | 0.30 | 13.2% | 1.25 | 0.42 / 0.33 | 0 | −2.6% |
| T15 | ex-post best static 0.9 | 10.8% | −35.2% | 0.31 | 28.2% | 2.73 | 0.88 / 0.85 | 0 | −5.3% |
| T20 | no brake | 12.1% | −38.9% | 0.31 | 31.8% | 3.12 | 0.99 / 0.97 | 0 | −7.8% |
| T20 | brake d20 | 1.3% | −22.5% | 0.06 | 14.4% | 2.29 | 0.50 / 0.23 | 0.6% | −4.5% |
| T20 | same-vol static 0.45 | 5.6% | −17.7% | 0.31 | 13.7% | 1.31 | 0.44 / 0.34 | 0 | −3.5% |
| T20 | ex-post best static 0.6 | 7.5% | −23.5% | 0.32 | 18.6% | 1.80 | 0.59 / 0.48 | 0 | −4.7% |

Sensitivity d=0.30 (not pre-registered): Calmar −0.05 / −0.07 / 0.02, MDD about −30%. See the JSON.

**Reading**: in this window the brake cuts MDD versus no brake (about −39% → −23%). But it loses to a same-vol static weight on both MDD and Calmar. The 2024-02 crash was V-shaped: the brake sold near the low and re-risked slowly. Static Calmar is flat at about 0.29–0.32 across weights, so "ex-post best static" is noise, not a signal. The brake is path-sensitive: T10, T15 and T20 differ only through min-trade and min-commission effects, yet brake CAGR ranges from 0.6% to 3.0%. Recommendation: do not adopt the brake. If Leo wants less sleeve DD, a lower static exposure (equivalently a lower tier) does better here. Revisit with longer history (2015/2018 bear markets) and Strategy's engine.

## ST / audit data switch (2026-10-10 22:12 ET, Data fix `docs/v2/ST_AND_AUDIT_FIX.md`)
- **ST primary**: `data/v2/st_flags/is_st_daily_2018_2026.parquet` (is_st_at_open on session). Tushare namechange PIT is only a fallback (table missing / session before 2018). Disagreements are reported in `filters_hit.st_disagree_*`: table vs namechange = 0/0 on all three sessions. Table vs research panel (`output/research_attrib_v2/panels`, which was not part of Data's in-place fix) = 3 on 2026-06-30 and 197 on 2026-10-09; the panel still reads 0 after 07-01, and the table is used.
- **Audit (now ON)**: we use the latest annual report (end_date month 12) whose `available_at` local date is before the session date (ann_date 18:00 → usable from the next session). Opinions older than FY(session.year−2) are ignored as stale. If `is_non_standard`, the name is excluded. Missing → not excluded, counted (`audit_missing_*`).

| Session | ST drop | Low-price drop | Audit drop | Audit missing (listed / in band) | Basket | Overlap with previous | Industries / max |
|---|---|---|---|---|---|---|---|
| 2026-06-30 | 208 | 49 | 64 | 207 / 97 | 50 | 49 | 19 / 6 |
| 2026-10-09 | 194 | 29 | 63 | 241 / 93 | 50 | 50 | 20 / 7 |
| 2023-12-29 (stress) | 110 | 39 | 81 | 428 / 78 | 50 | 47 | 20 / 10 |

(Drops are sequential at the funnel: ST → low price → audit. Non-standard names in the reference band: 120 / 118.)
- T20 core + smallcap β: 0.558 (06-30) / 0.396 (10-09). Stress-basket EW drawdown: −39.3% (was −38.3%). Pre-engine-fix descriptive data, not a performance claim.
- The dd-brake compare was rerun: brake Calmar 0.17 / 0.03 / 0.06 versus same-vol static 0.28 / 0.30 / 0.31. The conclusion still holds.

## Live 600k profile (Leo 2026-10-10 22:34 ET)
The research profile is unchanged (~50 names, 5M notional). The live profile is `live_profile` in the config, implemented by `SmallcapBetaSleeveProvider.live_basket(basket, tier)`. Script: `PYTHONPATH=. python scripts/smallcap_live_profile.py` → the `live_profile` section of `output/v2_proto/smallcap_beta_sleeve.json`.
- N = clip(floor(tier / min_name_weight), 20, 30), with min_name_weight = 0.5% of book = 3,000 CNY. That is 1.5× the 2,000 CNY min trade, and the 5 CNY min commission is ≤16.7bp one-way. Resulting N: T10=20, T15=30, T20=30 (4,000 CNY/name, 12.5bp).
- Selection walks the same research ranking (same band and PE/PB/ST/low-price/audit filters). A name is skipped and replaced by the next one if 1 lot × 1.1 > per-name CNY, or if its whole-lot holding would fall below 2,000 CNY. Industry cap = max(3, ceil(12·N/50)).

| Session | Tier | N | Held CNY min / median (after lots) | Lot unaffordable | Swaps | Commission bp | Industries / max | Overlap with 50-name basket |
|---|---|---|---|---|---|---|---|---|
| 2026-06-30 | T10 | 20 | 2,012 / 2,760 | 0 | 6 | 16.7 | 14 / 3 | 20 |
| 2026-06-30 | T15 | 30 | 2,012 / 2,724 | 0 | 9 | 16.7 | 16 / 3 | 30 |
| 2026-06-30 | T20 | 30 | 2,234 / 3,405 | 0 | 1 | 12.5 | 15 / 3 | 30 |
| 2026-10-09 | T10 | 20 | 2,038 / 2,589 | 0 | 6 | 16.7 | 14 / 3 | 20 |
| 2026-10-09 | T15 | 30 | 2,038 / 2,638 | 0 | 10 | 16.7 | 16 / 5 | 30 |
| 2026-10-09 | T20 | 30 | 2,127 / 3,428 | 0 | 1 | 12.5 | 16 / 4 | 30 |

- T20 510300 + smallcap β: live 0.561 / 0.398 vs research 0.558 / 0.396 (06-30 / 10-09).
- Lot rounding leaves median holdings about 10–15% below target, so the effective sleeve weight is somewhat under the tier.
- Stress 2024-02 (formation 2023-12-29; descriptive, pre-engine-fix, raw prices, EW): research50 −39.7%; live T10 −38.3%, T15 −38.6%, T20 −38.8%.
- Beta harness, no brake (research-only; not cross-checked against Strategy's engine), window 2023-12-29 → 2026-10-09: Calmar research50 vs live = 0.29 vs 0.24 (T10), 0.31 vs 0.25 (T15), 0.32 vs 0.32 (T20). Live turnover is about 4.6–6.1/yr vs about 3/yr, and costs are 2.6–4.0% of sleeve capital vs about 1.1%.
- **Open item**: `live_basket` has no retention of current holdings, so live turnover is roughly double the research basket's. Adding retain-current logic is the obvious next fix.

## Holding-retention buffer (2026-10-10 22:35 ET follow-up)
- **Rule**: keep a current holding if it is still eligible (band + PE/PB/ST/low-price/audit filters) and sits within the top `retain_mult × N` of the selection ranking. Otherwise replace it from the top. Live names must still clear lot and min-trade checks and the industry cap. There is no cap-band slack: names that leave the band are dropped.
- **Chosen**: live `live_profile.retain_mult = 2.0` (2×N). Research keeps `retain_top = 150` (3×N), which gives the same result as 2×N. 1.5× gets most of the turnover cut; at 2× research turnover plateaus; 3× adds little. `live_basket(..., current=prev)` applies it; with no `current` (one-off snapshot) it is off.
- **Compare**: `PYTHONPATH=. python scripts/smallcap_retention_compare.py` (~20 s) → `output/v2_proto/smallcap_retention_compare.json` (multiples 0 / 1.5 / 2 / 3). Research-only Beta harness, no brake, not cross-checked against Strategy's engine. Window 2023-12-29 → 2026-10-09.

| Version | Tier | Buffer | Turnover/yr | Cost / sleeve capital | CAGR | MDD | Calmar |
|---|---|---|---|---|---|---|---|
| research50 | T10 | none | 4.32 | 1.6% | 12.2% | −39.3% | 0.31 |
| research50 | T10 | 2×N | 2.87 | 1.1% | 11.8% | −40.2% | 0.29 |
| research50 | T15 | none | 4.46 | 1.5% | 12.9% | −39.4% | 0.33 |
| research50 | T15 | 2×N | 3.00 | 1.1% | 12.7% | −40.3% | 0.31 |
| research50 | T20 | none | 4.55 | 1.5% | 13.2% | −39.2% | 0.34 |
| research50 | T20 | 2×N | 3.06 | 1.1% | 12.7% | −40.2% | 0.32 |
| live600k | T10 | none | 5.91 | 3.9% | 9.2% | −39.1% | 0.24 |
| live600k | T10 | 2×N | 4.25 | 2.8% | 10.5% | −38.4% | 0.27 |
| live600k | T15 | none | 6.08 | 4.0% | 10.0% | −40.1% | 0.25 |
| live600k | T15 | 2×N | 4.90 | 3.2% | 9.3% | −39.3% | 0.24 |
| live600k | T20 | none | 4.64 | 2.6% | 12.4% | −38.7% | 0.32 |
| live600k | T20 | 2×N | 3.15 | 1.7% | 9.2% | −40.0% | 0.23 |

**Reading**: the buffer reliably cuts turnover (about 30% or more) and costs (0.4–1.0 pt of sleeve capital). CAGR and Calmar move in both directions (±3 pt), which reflects name-path noise in a single 2.8-year window with one crash. It is not evidence for or against the buffer. MDD is unchanged at about −39% to −40%.

## Output files (rerun-safe)
`scripts/smallcap_beta_sleeve.py` now preserves the `live_profile` / `retention_compare` sections already in `smallcap_beta_sleeve.json` and lists sidecar files. The live profile also writes `output/v2_proto/smallcap_live_profile.json`, and the retention compare writes `output/v2_proto/smallcap_retention_compare.json`.

## B1 survivorship fix (Leo / V2_REBUILD_PLAN, Data D3 landed 2026-10-10 ~23:07 ET)

Code: `quantlab/beta/survivorship.py`; flag `survivorship_b1` in config (default ON);
report: `PYTHONPATH=. python scripts/smallcap_survivorship_b1.py` → `output/v2_proto/smallcap_survivorship_b1.json`.

### What changed
1. **Ranking order**: float-cap ranks 3001–5000 are taken over the **full market** (panel `circ_mv` ∪ delisted daily `circ_mv` for names still listed that day). ST / low-price / audit are applied **after** the band (risk filters), not before. Legacy mode `ranking_mode_override="legacy_filter_then_rank"` kept for A/B.
2. **Delisted merge**: fills names missing from the research panel; on the 2023+ window the panel already holds most delisted bars, so adds are usually 0–5.
3. **Terminal return scenarios** (no invented post-delist prices): when a held name delists, mark once at last available close with **−50%** or **−100%**. Setup is in the JSON; not yet wired into the Beta harness NAV (Strategy cross-check owns performance).
4. **Label**: **2015+ COMPLETE** via `float_mktcap_daily_from2015_tushare`. B3 descriptive stress landed (see B3 section). Terminal −50%/−100% still not in NAV.

### Numbers
| Session | B1 n | Legacy n | Overlap B1↔legacy | Overlap B1↔prev JSON | Later-delisted in band | Live T20 n / lot-unaffordable |
|---|---|---|---|---|---|---|
| 2026-06-30 | 50 | 50 | 45 | 45 | 0 (8 later-delisted still listed; all below band / microcap) | 30 / 0 |
| 2026-10-09 | 50 | 50 | 44 | 44 | 0 | 30 / 0 |
| 2023-12-29 stress formation | 50 | — | — | — | 54 | — |

- Panel-window history (≈ monthly): later-delisted in band max **84**, mean **≈32**.
- Unique research names selected over 2023-12-29→2026-10-09 rebalances that later delisted: **0** (ST/low-price/audit remove delisting candidates before selection in this window).
- Delist reason field is heuristic (Data: namechange; no official reason).

### Open gaps
- Full-market circ_mv panel for **2015–2022** (needed for B3 failure-scenario ranks).
- Wire −50%/−100% terminal marks into the Beta harness / Strategy paper engine and re-cross-check.
- `reason_basis` heuristic only.

## B3 stress 2015-06~2016-01 (failure scenario; descriptive)

Script: `PYTHONPATH=. python scripts/smallcap_b1_b3_from2015.py` → `output/v2_proto/smallcap_b3_stress_2015.json` (+ refreshes B1 JSON).

- **Formation**: 2015-06-15 under B1 ranks (relative bottom 40%; universe ≈ 2,563 after 20d mean). Band 1,025 names; ST dropped 36; low-price 0; fund pass 20 → **50 selected** (30 via tier fallback because PB≤3 was tight in the 2015 bull tape).
- **Later-delisted in band**: 77; of which **in selected basket**: see JSON `in_band_later_delisted_selected`.
- **Descriptive EW DD** (daily_basic **unadjusted** closes; no costs; no limit-down modeling; **terminal delist −50%/−100% NOT applied to NAV**):
  - Max DD **≈ −47.1%**, trough **2015-07-08**
  - Window-end return (→ 2016-01-29) **≈ −33.9%**
  - Book impact at T10/T15/T20 (sleeve DD × tier): ≈ −4.7% / −7.1% / −9.4% of book
  - Crash window Jun–Aug 2015 pairwise corr: median **≈ 0.68**, mean ≈ 0.63, share of pairs > 0.5 ≈ 36% (high co-movement — informs D_max in α ≤ L/D_max)
- **Label**: research descriptive only. Not Strategy fixed engine. Not promotion evidence.

## B1 key-date ranks (after Data float panel)

| Session | Universe (20d mean) | Band mode | Band size | Later-delisted in band |
|---|---:|---|---:|---:|
| 2015-06-15 | 2563 | relative bottom 40% | 1025 | 77 |
| 2015-12-31 | 2637 | relative bottom 40% | 1054 | 70 |
| 2016-01-29 | 2648 | relative bottom 40% | 1059 | 70 |
| 2018-06-29 | 3387 | absolute 3001–3387 | 387 | 14 |
| 2020-06-30 | 3914 | absolute 3001–3914 | 914 | 81 |
| 2023-12-29 | 5336 | absolute 3001–5000 | 2000 | 54 |
| 2026-06-30 | 5530 | absolute 3001–5000 | 2000 | 0 |
| 2026-10-09 | 5571 | absolute 3001–5000 | 2000 | 0 |

## 2015+ provider path (`data_source='history_2015'`) — 2026-10-11

- API: `SmallcapBetaSleeveProvider(mandate, data_source='history_2015', basket_cache=None)`; `basket()/plan()/tier_weights()/live_basket()/crowding()/beta_descriptive()` work from 2015.
  `data_source='auto'` (default) uses the history path whenever the 2023+ `research_attrib_v2/panels` lack 253 sessions before the session (i.e. before ~2024-01), else the legacy panels. `'panels_2023'` = legacy only.
- Backing: `quantlab/beta/smallcap_history_selector.py` (B1 full-market ranks from `float_mktcap_daily_from2015_tushare`) + `quantlab/beta/smallcap_history_panels.py` (daily_basic wide caches: close, pe_ttm, pb, ADV proxy; 510300 adjusted via ETF reader).
- Cached baskets: `precompute_history_baskets(sessions, path)` writes a retention-chained JSON; pass it as `basket_cache=` (used when `basket()` is called without `current`).
- RAM (peak RSS, one-process small test): legacy panels `basket(2026-06-30)` 2,906 MB → history path `plan()` on 4 sessions + live basket 1,293 MB; selector-only 818 MB. Float panel now cached wide float32 (`output/v2_proto/cache_smallcap_history/float_mktcap_wide_f32_*.parquet`).
- Earliest: baskets from 2015-06 with `history_truncated` (min history <253) until ~2016-02; full-spec from ~2016-02; 2017+ clean.
- **Band bug fixed**: the old selector branch "absolute ranks 3001–N when 3001≤N<5000" gave 0–47-name baskets 2017-04→2018-03 (band of ~77 mostly fresh IPOs). Rule now: absolute 3001–5000 if N≥5000, else bottom 40%. **The 2026-10-11 04:32 engine compare (`output/v2_proto/smallcap_engine_compare/`) used the buggy selector — invalid, rerun required.**
- Proxies/limits on the history path: ADV = turnover_rate×circ_mv (no `amount` in daily_basic); close unadjusted (lot/capacity only; β uses clipped returns, descriptive); no limit-up/down flags → `stress_test()` stays on the 2023+ panels.
