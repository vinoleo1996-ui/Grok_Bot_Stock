> **【仅参考 / REFERENCE ONLY】2026-10-14 Strategy 标注（Arch 内审 #2/#3）**：本文数字来自旧纸面 `v2_strategy_paper`（v1 线）：close-to-close、无 T+1、不处理涨跌停、两次调仓间权重不漂移，且未传 total_return_factor（原始价、除息日记亏）。与主引擎 book-smoke（B4/S6/capacity_adv）口径**不可比**，不得作为决策依据。修复归属待 Eng 确认，见 docs/v2/STRATEGY_CPCV_CDAR_CONC60_ZH.md §4。

# Strategy paper v1 — Platform feed

**Eng role:** stable readers / callables only.  
**Strategy role:** paper runner + NAV under `output/strategy_paper_v1/` / `output/strategy_paper_costs/`.  
**`promotion_approved=false` everywhere.** Eng does not invent NAV or portfolio conclusions.

## Import

```python
from datetime import date
from quantlab.platform.strategy_feed import (
    STRATEGY_PAPER_V1_OUTPUT_DIR,
    STRATEGY_FEED_CACHE_DIR,
    DEFAULT_CLOSE_CHUNK_SIZE,  # 300
    DEFAULT_CLOSE_DTYPE,       # "float32"
    trading_sessions,
    merged_close_panel,
    iter_merged_close_chunks,
    merged_daily_returns,
    iter_merged_daily_return_chunks,
    cache_merged_close_panel,
    load_cached_close_panel,
    biweekly_rebalance_sessions,
    etf_510300_daily_returns,
    d1_members_at,
    d1_members_at_chunked,
    describe_strategy_feed,
)
```

## Callables (signatures)

| Name | Signature (1-liner) | Notes |
| --- | --- | --- |
| `trading_sessions` | `(start=2024-01-01, end=None, *, calendar=None, roots=None) -> list[date]` | Merged D0+extend calendar |
| `merged_close_panel` | `(ids, start=..., end=None, *, roots=None, chunk_size=None, dtype="float32", use_disk_cache=False, cache_dir=None, cache_format="feather") -> DataFrame` | **Memory knobs:** `chunk_size=200–400`, `dtype=float32`, optional feather cache |
| `iter_merged_close_chunks` | `(ids, start=..., end=None, *, chunk_size=300, dtype="float32", roots=None) -> Iterator[DataFrame]` | Stream columns; do not hold full wide panel |
| `merged_daily_returns` | `(ids, start=..., end=None, *, roots=None, close_panel=None, chunk_size=None, dtype="float32") -> DataFrame` | **Pass `close_panel=`** — never reload |
| `iter_merged_daily_return_chunks` | `(ids, start=..., end=None, *, chunk_size=300, dtype="float32", roots=None)` | Chunked returns without full panel |
| `cache_merged_close_panel` / `load_cached_close_panel` | research feather/parquet under `output/strategy_feed_cache/` | Optional preload-once |
| `biweekly_rebalance_sessions` | `(start=..., end=None, *, calendar=None, mandate=None, roots=None) -> list[date]` | Mandate ordinary rebalance |
| `etf_510300_daily_returns` | `(start=..., end=None, *, roots=None) -> Series` | from `data/v2/etf_510300` panel |
| `d1_members_at` | `(session, *, max_instruments=None, instrument_ids=None, config=None, roots=None, return_result=False)` | **Per rebalance only** — do not cache all sessions' frames |
| `d1_members_at_chunked` | `(session, instrument_ids, *, chunk_size=500, ...)` | Union members scanning pool in chunks |

`describe_strategy_feed()` lists knobs + memory tips (machine-readable).

## Full D1 memory (box ~15Gi, no swap) — recommended

**Root cause of ~11Gi OOM:** unbounded `load_merged_panel` cache (~6k long frames) **plus** full P1 OHLCV preload **plus** separate close/tradability walks.

### Recommended Strategy invocation

```bash
cd /workspace/QuantLab
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.portfolio.v2_strategy_paper_turn_compare --full-d1 \
  --memory-safe --chunk-size 300 --float32 --cache-max-items 400
```

Defaults when `--full-d1` (unless `--no-memory-safe`):

1. **`--memory-safe`** → `build_lean_close_turnover_tradability` single pass (float32 close + turnover + tradability). **No** long-frame panel cache. **No** full OHLCV preload.
2. P1 panels = close (+ turnover); amount/pb empty (TURN amount coverage may waive — research).
3. `merged_daily_returns(..., close_panel=closes)` — no second close load.
4. `d1_members_at` **per rebalance session** only.
5. If not lean: `install_merged_panel_cache(max_items=400)` LRU, then `clear_merged_panel_cache()` after preload.

Mid-tier (NOT main) if still tight:

```bash
... --full-d1 --memory-safe --pool-cap 1500
```

### Platform-only pattern (no runner)

```python
from datetime import date
ids = [...]  # or d1_members_at(...)
# stream — lowest peak
for chunk in iter_merged_close_chunks(ids, date(2024,6,1), date(2026,10,9), chunk_size=250):
    rets = chunk.pct_change()  # process & discard
# or one float32 panel in chunks:
closes = merged_close_panel(ids, date(2024,6,1), date(2026,10,9), chunk_size=300, dtype="float32")
rets = merged_daily_returns(ids, close_panel=closes)  # reuse
members = d1_members_at(date(2024,6,3), instrument_ids=ids)  # one session
# or chunked D1 scan:
members = d1_members_at_chunked(date(2024,6,3), ids, chunk_size=500)
```

**Avoid:** full OHLCV preload when only close/returns needed; unbounded panel cache; caching every session's `D1MaskResult.frame`; calling `merged_daily_returns` without `close_panel`.

## SW / Tushare notes

- **SW default** = accepted tushare (`industry_members_sw_l1_tushare.parquet`). Dataset may be promotable; **overall** feed/Mandate `promotion_approved` stays False.
- ETF returns still use `panels/sh.510300.parquet`.
- Merge default still `asof_extend_202610`.

## Gaps (research)

- Full-universe `d1_members_at` without chunking is slow (panel-per-id).
- asof_extend amount/limit/ST incomplete → U30 research waive on late sessions.
- lean path: amount/pb empty → some P1 factors waive coverage (not invented).
- financials / dividend / float still overall non-promotable.

## Smoke (optional)

```bash
cd /workspace/QuantLab
PYTHONPATH=. /workspace/qlvenv/bin/python -c "
from datetime import date
from quantlab.platform.strategy_feed import (
    describe_strategy_feed, merged_close_panel, iter_merged_close_chunks, d1_members_at,
)
print(describe_strategy_feed()['memory_knobs'])
m = d1_members_at(date(2026,6,30), max_instruments=20)
c = merged_close_panel(m[:10], date(2024,6,1), date(2024,6,30), chunk_size=5, dtype='float32')
print('close', c.shape, c.dtypes.iloc[0])
n = 0
for part in iter_merged_close_chunks(m[:10], date(2024,6,1), date(2024,6,30), chunk_size=4):
    n += part.shape[1]
print('chunk_cols', n)
"
```

## 2026-10-10 accepted defaults + overall gate
See `docs/v2/ACCEPTED_DEFAULTS.md`. Merge panels now default to `asof_extend_tushare_202610`
(fallback `asof_extend_202610`), float daily to `float_mktcap_daily_tushare.parquet`.
`d1_members_at` / feed meta `promotion_approved` follow `quantlab.promotion_gate.overall_promotion_approved()`
(currently True per Leo Eng confirmation 2026-10-10 20:52 ET; data/platform gate only — not a strategy verdict).
Disk cache key includes extend source; rebuild caches.
