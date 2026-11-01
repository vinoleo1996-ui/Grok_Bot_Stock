# V2 Mask / Beta prototypes — research-only

> 2026-10-10 · `promotion_approved=false` · SW_L1 `promotable=false`

## Status

Contract-based **prototypes** only. Not live-trading ready. No backtest metrics,
Sharpe, or PnL are produced by Eng smoke paths.

SW_L1 PIT is a free-source research reconstruction. Honor
`data/v2/sw_l1_pit/NOT_PROMOTION_GRADE.md`. Industry tags from this table must
never flip `promotion_approved` or be treated as promotion-grade neutralization
input.

## Data roots (consume; do not mutate 1c85)

| Dataset | Path |
|---|---|
| D0 base | `data/local_market/1c85fd9aceaa03c3c4863bec/` |
| ETF 510300 | `data/v2/etf_510300/` |
| SW_L1 PIT (research) | `data/v2/sw_l1_pit/industry_members_sw_l1.parquet` |
| float_mktcap | `data/v2/float_mktcap/float_mktcap_asof.parquet` (asof 2026-06-30) |
| as_of extend | `data/v2/asof_extend_202610/` (through 2026-10-09) |

## Eng modules

| Path | Role |
|---|---|
| `quantlab/data/v2_readers.py` | Typed readers + D0/asof_extend panel merge |
| `quantlab/universe/mask.py` | Stub + `PrototypeUniverseMaskProvider` |
| `quantlab/universe/d1_masks.py` | Executable L0 pipeline (merged panels) |
| `quantlab/beta/sleeve.py` | Stub + `PrototypeBetaSleeveProvider` / `VolTargetBetaSleeveProvider` (vol16%/β0.70 research) |
| `quantlab/v2_beta_smoke.py` | Beta vol-target weights + flags smoke |
| `quantlab/v2_proto_smoke.py` | Dual-session counts/flags smoke |
| `docs/v2/BETA_VOL_TARGET_HANDOFF.md` | Strategy industry-neutral handoff contract |
| `quantlab/v2_schemas.py` | Frozen field names |
| `docs/v2/ASOF_EXTEND_PANEL_MERGE.md` | Merge rule + extend gap notes |

## Smoke

```bash
cd /workspace/QuantLab
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.v2_proto_smoke
# mid D0 + late extend (2026-06-30 and 2026-10-09)
# or
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli v2-proto-smoke
```

Asserts `promotion_approved=false` and `sw_l1_promotable=false` on both
sessions. Requires `sh.510300` bars on each session. Prints row counts, date
ranges, and quality flags only — **no** backtest metrics.

## Remaining blockers

- Full-universe mask (all ~6k panels) still slow; proto samples `--max-instruments`.
- U30 `median_amount_20d` promotion-grade confirmation still TODO; extend amount gaps waive U30 in research only.
- SW_L1 / financial PIT remain non-promotable.
- Beta vol/β scaling is research-only (not optimized / not promotion-grade); see `BETA_VOL_TARGET_HANDOFF.md`.
- asof_extend mask cols incomplete vs D0 — see `ASOF_EXTEND_PANEL_MERGE.md`.
- float_mktcap asof still 2026-06-30; late sessions use research stale-carry.
