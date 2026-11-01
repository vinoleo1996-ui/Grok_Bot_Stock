# QuantLab V2 Strategy — portfolio constructor skeleton

**Status**: research stub · `promotion_approved=false`  
**Date**: 2026-10-10 (ET)  
**Owner**: Strategy (portfolio layer)

## Ownership boundary

| Owner | Owns | Does not own |
|---|---|---|
| **Strategy** | `PortfolioConstructorV2`, rebalance schedule hooks, research paper-loop smoke, turnover / holdings caps encoding, **residual β vs Mandate band** (after Beta sleeve clip) | Eng readers, D0/D1 panel IO, CLI platform smokes, ETF sleeve vol/β math |
| **Eng** | `mandate_v2` loader, `v2_schemas`, universe mask / `d1_masks`, Beta package surface, `v2_smoke` / `v2_eng_smoke`, readers/CLI | Portfolio target weights / promotion decisions |
| **Data** | float_mktcap, asof_extend panels, 510300, SW_L1 PIT, corporate-actions warmup | Combination conclusions, constructor knobs |
| **Beta** | `VolTargetBetaSleeveProvider.plan()` → `etf_sleeve_weight` / `cash_weight` / `residual_book_weight_cap` | Residual book scores, raising `max_etf`, promotion flips |

Hard rule: loaders and smokes **force / assert** `Mandate.promotion_approved is False` and refuse go-live paths. Do not flip promotion flags in JSON or code.

## Beta handoff (consumed here)

See `docs/v2/BETA_VOL_TARGET_HANDOFF.md` and `PrototypeBetaSleeveProvider.strategy_handoff_surface()`.

| Field | Strategy use |
|---|---|
| `BetaSleevePlan.residual_book_weight_cap` | `PortfolioConstructorV2.construct(book_weight_cap=...)` |
| `etf_sleeve_weight` / `cash_weight` | Recorded in smoke; not re-scaled by Strategy |
| `implied_beta_in_band` | **Flag only** — `max_etf=0.40` can clip sleeve β≈0.39 below Mandate band [0.5, 0.85]; Strategy **owns** residual-book β contribution; do **not** raise ETF cap |

Smoke prefers live `VolTargetBetaSleeveProvider.plan()`; on data/load failure falls back to `StubBetaSleeveProvider` (idle caps / synth). SW_L1 remains research-only (`sw_l1_promotable=false`).

## Smoke

```bash
cd /workspace/QuantLab
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.v2_strategy_smoke
# or
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli v2-strategy-smoke
# optional light D1 probe (falls back to synth on failure):
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.v2_strategy_smoke --use-d1
```

Loop exercised: Mandate load → D1 idle/stub (or `--use-d1`) → **live Beta plan** (or stub fallback) → stub residual factory → `PortfolioConstructorV2` with synthetic integrate scores + `book_weight_cap` → biweekly / daily rebalance hooks. Exit 0 on structural ok; no fabricated Sharpe/PnL.

## Modules

| Path | Role |
|---|---|
| `quantlab/portfolio/v2_constructor.py` | Mandate knobs → capped weights; LW optimizer `NotImplemented`; naive score-rank / equal stub; accepts `book_weight_cap` |
| `quantlab/portfolio/v2_rebalance.py` | Biweekly ordinary-rebalance check + daily mask/risk-scale stub (no live scale) |
| `quantlab/portfolio/__init__.py` | Exports V2 constructor / rebalance symbols |
| `quantlab/v2_strategy_smoke.py` | Research paper-loop smoke (Beta handoff consumer) |

## Mandate knobs consumed

- Holdings band: `min_positions_target`–`max_positions_stocks` (30–60)
- `max_single_stock_weight` 5% · `max_industry_weight` 25%
- `turnover_budget_monthly_one_way` 0.35 (prorated per biweekly step)
- `ordinary_rebalance` = biweekly
- Vol 16% / β 0.70 targeting: **Beta sleeve ownership** for ETF/cash weights — Strategy sizes residual book under `residual_book_weight_cap` and owns residual β vs Mandate band (documented tension; not overridden)

## Eng / Data / Beta pings

- Eng: keep `mandate_v2` / mask / Beta surface / eng smokes stable; Strategy will not mutate them.
- Beta: Strategy consumes `plan()` + handoff surface only; does not change sleeve math or `max_etf`.
- Data: ping only if constructor needs a missing field for a non-stub paper path (SW_L1 labels for real industry caps, residual scores from min factors). Skeleton smoke uses synthetic scores/labels.
