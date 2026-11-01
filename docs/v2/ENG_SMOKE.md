# V2 Eng smoke — universe funnel + Beta idle + min factors

**Status**: research-only · `promotion_approved=false` · IC/ICIR = process metrics only

## Command

```bash
cd /workspace/QuantLab
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.v2_eng_smoke --max-instruments 50
```

## Data consume paths (Eng)

| Path | Role |
|---|---|
| `data/v2/float_mktcap/float_mktcap_daily_20260630_20261009.parquet` | Preferred float_mktcap by session (`v2_daily`) |
| `data/v2/float_mktcap/float_mktcap_asof.parquet` | Fallback asof / stale_carry |
| `data/v2/financials_pit/ep_research_asof_20260630.parquet` | Preferred V01_EP (`ep_research_asof`) |
| `data/v2/asof_extend_202610/panels/` | Late-session panels (~50/5201 amount-enriched) |
| `output/d1/ENG_PING_PATHS.json` | Data ping manifest |

## Modules

| Path | Role |
|---|---|
| `quantlab/data/v2_readers.py` | `float_mktcap_lookup_for_session`, `load_ep_research` |
| `quantlab/universe/d1_masks.py` | Per-row `float_mktcap_source` (`v2_daily` / …) |
| `quantlab/factors/v2_min_pipeline.py` | Prefers ep_research for V01_EP |
| `quantlab/v2_eng_smoke.py` | Unified smoke + funnel tables |

Never mutates D0 1c85 originals. No Sharpe/PnL promotion narrative.
