> **【仅参考 / REFERENCE ONLY】2026-10-14 Strategy 标注（Arch 内审 #2/#3）**：本文数字来自旧纸面 `v2_strategy_paper`（v1 线）：close-to-close、无 T+1、不处理涨跌停、两次调仓间权重不漂移，且未传 total_return_factor（原始价、除息日记亏）。与主引擎 book-smoke（B4/S6/capacity_adv）口径**不可比**，不得作为决策依据。修复归属待 Eng 确认，见 docs/v2/STRATEGY_CPCV_CDAR_CONC60_ZH.md §4。

# Full D1 TURN compare — memory profile & fix

**promotion_approved=false.** Research-only.

## OOM root cause (2026-10-11)

Failed at first rebalance after preload. Kernel OOM-killed python with
`anon-rss≈11.0 GiB` (box ≈15 GiB, ~6 GiB free under concurrent tushare jobs).

| Contributor | Approx | Notes |
|---|---|---|
| `install_merged_panel_cache()` long frames | **~8.6 GiB** | ~6274 × ~1.4 MB/instrument full OHLCV long frame |
| Full-pool `load_ohlcv_panels` wide OHLCV | ~0.1–0.3 GiB | Extra wide copies on top of cache |
| `closes` + `stock_rets` + tradability | ~0.1 GiB | Dense wides |
| Dual P1 + LW temps at first rebalance | spike | Copies / rolling / cov |

Dense float matrices alone were **not** the 11 GiB — the long-frame panel cache was.

## Fix (Strategy-owned, no Eng wait)

1. **Stop full OHLCV preload** for Full D1 TURN.
2. **Lean single-pass** (`quantlab/portfolio/v2_lean_panels.py`): stream each
   instrument once → float32 `close` + `turnover` + bool tradability; **never**
   retain long-frame cache.
3. Inject lean panels into P1 (`close`/`turnover` only; amount/pb empty → waive).
4. LW returns panel **column-sliced** to scored/prior names (not full 6k).
5. `gc.collect()` after each rebalance; `STATUS.json` RSS updates.
6. Smoke (`pool=250`) unchanged process-only path; may still use cache then clear.

## Eng ask (optional speed-ups, not blockers)

If Eng lands these in `quantlab/platform/strategy_feed.py`, Strategy will adopt:

- `merged_close_panel(..., chunk_size=, dtype=float32)`
- `iter_merged_close_chunks(...)`
- optional disk cache for D1 membership by session

Until then: lean path is the Full D1 TURN default (`memory_safe=True` when `--full-d1`).

## Mid-tier fallback

`--full-d1 --pool-cap 1200` → labeled **NOT main** (`smoke_only=true`,
`run_tier=mid_tier_poolN_turn_compare`). Use only if Full D1 still cannot finish.

## Reproduce

```bash
cd /workspace/QuantLab
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.portfolio.v2_strategy_paper_turn_compare --full-d1
```

Outputs: `output/strategy_paper_costs/full_d1_turn/`
