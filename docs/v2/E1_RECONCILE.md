# E1 零成本双引擎对账脚手架

Research-only. Wraps `quantlab.platform.execution.reconcile_zero_cost` /
`cost_ladder` / `load_execution_panels`. Bare `ExecConfig()` defaults stay OFF;
zero-cost path uses an explicit no-cost config. No strategy performance conclusions.

## CLI

```bash
# Dry-run (synthetic, no market IO) — proves report fields populate
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.platform.e1_reconcile \
  --dry-run --out /tmp/e1_dry

# After Strategy dumps weights under the arm dir (default: planned targets)
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.platform.e1_reconcile \
  --weights-dir output/strategy_paper_costs/full_d1_fixed_armA \
  --weights-file planned_target_weights.parquet \
  --start 2024-06-01 --end 2026-10-09 \
  --out output/e1_reconcile/full_d1_fixed_armA \
  --ids-from-weights --max-instruments 80

# Post-fill actual weights (compare realized fills, not schedule input)
... --weights-file actual
# or: --weights-file target_weights.parquet

# Arm B
... --arm b
# or: --weights-file arm_b

# Optional: costs ladder + strategy_v1 impact_bp
... --with-costs --paper-nav path/to/nav.csv
```

Flags: `--weights-dir`, `--weights`, `--weights-file`, `--arm`, `--paper-nav`,
`--start`, `--end`, `--out`, `--ids-from-weights`, `--with-costs`,
`--max-instruments`, `--initial-cash`, `--corporate-actions on|off` (default on; off = unadjusted, apples-to-apples vs unadjusted paper NAV), `--dry-run`.

## Strategy handoff

Strategy's runner writes under the arm / run dir (long format:
`session`, `instrument_id`, `weight`):

| file | meaning | when to use |
|---|---|---|
| `planned_target_weights.parquet` | pre-fill targets | **default** schedule input — engines simulate fills |
| `target_weights.parquet` | post-fill actual weights | compare realized weights (`--weights-file actual`) |
| `arm_b_target_weights.parquet` | arm B (same long schema) | `--arm b` or `--weights-file arm_b` |

Aliases for `--weights-file`: `planned` / `actual` / `arm_b` (or the full filename).
`--arm b` overrides `--weights-file` and selects `arm_b_target_weights.parquet`.

### Instrument id normalization

Strategy may write undotted ETF / stock ids (e.g. `sh510300`). The loader
normalizes to platform form at load time:

- `sh510300` → `sh.510300`
- `sh600000` → `sh.600000`
- `sz000001` → `sz.000001`
- `bj430047` → `bj.430047`

Already-dotted ids pass through unchanged.

Discovery order: preferred `--weights-file` name in `--weights-dir`, then one
level of `arm_a*` / `zero_cost*` / `A_*` subdirs; then the full candidate list
(planned → actual → arm_b → legacy names → `schedule.json`).

Optional `nav.csv` (columns `date`,`nav`) is auto-discovered for `paper_nav`
comparison; or pass `--paper-nav`.

Keep id lists small (`--max-instruments`) — `load_execution_panels` reads one
instrument file at a time but still grows with the id list.

## Report outputs (`--out`)

| file | content |
|---|---|
| `e1_summary.json` | reference, first_divergence, max_abs_diff / max_abs_rel_diff, effective_n_mean, impact_bp (if `--with-costs`), ExecConfig snapshot, ENG_PING `units_note`, root-cause notes (tick / lot rounding), schedule meta, panel diag |
| `e1_navs.csv` | per-day NAV for platform / ledger / fastsim / (optional paper) + delta-rounding columns |
| `e1_per_day_diffs.csv` | per-day diffs vs reference |
| `e1_cost_ladder.csv` | only with `--with-costs` |
| `E1_RECONCILE_ZH.md` | short Chinese summary |

## Units (ENG_PING `units_note`)

- `asof_extend_tushare_202610` (default merge): volume=股, amount=元 (prefer for amount).
- `asof_extend_202610` (fallback): volume may be 手 → use `volume_shares` / `volume_unit`.
- D0: volume=股.

`load_execution_panels` honors `volume_shares` then `volume_unit`, else infers scale
from `amount/(volume*close)`.

## Related

- `docs/v2/EXECUTION_COSTS_PLATFORM.md` — engine API
- `QuantLab-V2_REBUILD_PLAN_ZH.md` — E1 is P0 after S1 baseline
