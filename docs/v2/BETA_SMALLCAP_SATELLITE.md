# Beta research switch: `smallcap_satellite`

> **SUPERSEDED 2026-10-10 21:30 ET (Leo):** small-cap is now a **standalone stock-basket β sleeve**, not bound by `max_etf` — see `BETA_SMALLCAP_STANDALONE.md`. The ETF-proxy satellite menu below is kept only as a compare arm / history.


> 2026-10-10 · `promotion_approved=false` · default **OFF**  
> Main β sleeve remains **510300**. Satellite is an optional β/style menu arm.  
> ESSENCE: B1/B2/B3/B5 — see `ESSENCE_REUSE_V2.md` / `quantlab/beta/configs/compare_arms_v1.json`

## Purpose

Allow Strategy to **compare arms** (menu ≠ mainline):

| Arm | Default | Role |
|---|---|---|
| Core 510300 | ON | Main β |
| ETF proxy `sh512100` | OFF | Smallcap style (CSI1000) |
| ETF proxy `sh510500` | OFF | Side-by-side CSI500 |
| Wide-basket 50 | OFF | **Raise-CAGR candidate** (tiny sleeve) |
| M2 control 50 | OFF | **Raise-CAGR candidate** (MDD≈−30% → tiny) |
| 511260 risk-parity overlay | OFF | Cut DD when satellite ON (B5) |

Raise-CAGR candidates are **always listed** on the menu even when flags are OFF.

## Flags

```python
from quantlab.beta import VolTargetBetaSleeveProvider
from quantlab.mandate_v2 import load_mandate_v2

m = load_mandate_v2()
core = VolTargetBetaSleeveProvider(m)  # smallcap_satellite=False, bond_risk_parity_overlay=False

sat = VolTargetBetaSleeveProvider(
    m,
    smallcap_satellite=True,
    satellite_code="sh512100",  # or "sh510500" for compare arm
    max_satellite_frac=0.25,
    bond_risk_parity_overlay=False,  # B5 — only applies if satellite ON + 511260 data landed
)
plan = sat.plan(session)
menu = sat.satellite_menu(session)       # includes raise_cagr_candidates
catalog = sat.compare_arms_catalog()     # full JSON + hooks
```

## B2/B3 — true 50-stock basket path (scaffolding)

Config: `quantlab/beta/configs/compare_arms_v1.json`  
Hooks: `quantlab.smallcap.universe.pool_on` / `select` (and optional `financial_tier`).

- Wide basket: `band='absolute'` ranks 3001–5000 ADV  
- M2: `band='relative'` bottom 40% ADV, exclude ST, financial tier, 50 EW  

Beta exposes specs via `stock_basket_specs()` / `describe_stock_basket_hooks()`.  
**No fabricated returns**; full paper backtest is Strategy-owned after P0.  
Suggested max sleeve weight **0.05** given MDD ledger (~−21% wide / ~−30% M2).

## B5 — 511260 overlay

`bond_risk_parity_overlay=False` by default. When satellite ON and Data lands
511260 bars, overlay can risk-parity vs the satellite leg to cut DD. Probe today:
data **not** on box → `data_ready=false`, TODO(Data).

## B6 — residual β (verified)

`BetaSleevePlan.residual_weight_to_hit_target_beta` still on plan + handoff.  
Status: **beta_delivered**; Strategy consumes after P0 (`b6_strategy_wiring` in config).

## Hard rules

- Do not raise `max_etf` / do not change Mandate β  
- `promotion_approved=false`  
- Core loader remains `load_etf_510300()` (Tushare fund_daily is candidate-only)

## Smoke

```bash
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.v2_beta_smoke
```
