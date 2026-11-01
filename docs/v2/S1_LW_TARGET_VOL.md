# S1 — LW + target-vol → V2 residual book

`promotion_approved=false`. Research-only. Does **not** raise `max_etf`. Satellite default **OFF**.

## Goal

Wire original `quantlab/strategy/portfolio.py` (`ledoit_wolf_cov`, `target_vol_weights`) into
`quantlab/portfolio/v2_constructor.py` residual-book construction.

## Behaviour

| Mode | `returns_panel` | Result `method` |
|------|-----------------|-----------------|
| `auto` (default) | usable date×id daily returns | `lw_target_vol` |
| `auto` | missing / sparse / optimize fail | `score_rank_equal_stub` (or proportional) |
| `lw_target_vol` | fail + `allow_stub_fallback=False` | `lw_failed` (empty) |
| `equal_stub` | ignored | equal / proportional stub |

Mandate mapping into legacy `PortfolioConfig`:

- `target_vol` ← `mandate.risk.target_annual_vol`
- `max_sector_weight` ← `mandate.portfolio_limits.max_industry_weight`
- `weight_max_dev` ← `max_single_stock_weight - 1/N` (so per-name cap ≈ Mandate 5%)

Post-LW: Mandate single-name cap re-applied; industry cap re-checked **without** forcing renorm to 1.0 (preserves target-vol cash). Then turnover clip + `book_weight_cap` (B6 `residual_weight_to_hit_target_beta`).

## TURN hook (stub only)

`construct(..., turn_scores=...)` records `turn_scores_hook_stub_ignored_n=…` and does **not** change weights. Full D1+costs+TURN compare is a **follow-on** task after S1 green.

## API

```python
from quantlab.portfolio import PortfolioConstructorV2

ctor = PortfolioConstructorV2(mandate)  # weighting_mode="auto"
result = ctor.construct(
    scores,
    session=session,
    industry_labels=labels,
    returns_panel=rets_df,          # date × instrument_id
    book_weight_cap=residual_cap,   # from Beta plan / residual_weight_to_hit_target_beta
)
# result.method == "lw_target_vol" | "score_rank_equal_stub" | ...
# result.promotion_approved is always False

weights = ctor.optimize_ledoit_wolf(scores, returns_panel=rets_df, industry_labels=labels)
```

## Smoke

```bash
cd /workspace/QuantLab
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.v2_strategy_smoke
```

Expect: no-panel path → stub; synthetic returns → `lw_target_vol`; `ok: true`; `promotion_approved: false`.

## Not in this ship

- Full D1+costs re-run with LW (next; wall-clock)
- TURN weight blend
- Raising `max_etf` / flipping satellite ON
