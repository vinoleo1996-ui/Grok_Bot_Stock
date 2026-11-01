# QuantLab V2 Phase 0 — engineering skeleton

**Status**: interface scaffold; `promotion_approved=false`  
**Date**: 2026-10-10 (ET)

## Smoke (no market data / no backtest)

```bash
cd /workspace/QuantLab
# needs pandas + pyarrow (e.g. /workspace/qlvenv)
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.v2_smoke
# or
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli v2-smoke
```

## Modules

| Path | Role |
|---|---|
| `quantlab/mandate_v2.py` | Load `docs/v2/QuantLab-MANDATE_V2.json` → typed `MandateV2` (forces `promotion_approved=False`) |
| `quantlab/v2_schemas.py` | **Frozen** SW_L1 / 510300 / float_mktcap / panel mask field names |
| `quantlab/data/v2_d0_meta.py` | Typed D0 readers for calendar / instruments / benchmark index |
| `quantlab/universe/mask.py` | L0 mask API + D0 calendar probe; SW_L1 loader NotImplemented |
| `quantlab/beta/sleeve.py` | L1 Beta sleeve; index bars from D0; 510300 NotImplemented |
| `quantlab/factors/residual_factory.py` | L3 residual / integrate factory stubs |
| `quantlab/v2_smoke.py` | Import + Mandate + D0 probe smoke |

## D0 path

`data/local_market/1c85fd9aceaa03c3c4863bec/` — calendar, instruments (stock), `benchmark.parquet` (sh.000300) readable.  
**Missing**: `industry_members_sw_l1`, `sh.510300` instrument+panel, `float_mktcap`.

## Hand to QuantLab Data

See smoke JSON key `schema_handshake` and `quantlab/v2_schemas.py`.

## Proto follow-on (mask/Beta)

See `docs/v2/PROTO_MASK_BETA.md`. Typed readers: `quantlab/data/v2_readers.py`.
Smoke: `PYTHONPATH=. python -m quantlab.v2_proto_smoke` (`promotion_approved=false`, `sw_l1_promotable=false`).

## Eng smoke (funnel + Beta idle + min factors)

See `docs/v2/ENG_SMOKE.md`.

```bash
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.v2_eng_smoke --max-instruments 50
# or: python -m quantlab.cli v2-eng-smoke
```
