# B2 — Small-cap β sleeve engine cross-check (skeleton)

> Research-only · `promotion_approved=false` · Mandate JSON not edited  
> **Status: waiting on Eng E1** (execution / paper entrypoint that Strategy+Beta will call).  
> Do not fill performance numbers until E1 lands and this checklist is run on that engine.

## Purpose

Re-check T10 / T15 / T20 on Strategy’s **fixed** paper engine (close valuation; limit/halt only block fills; blocked orders roll forward; Mandate costs + stamp by date; min trade 2,000 CNY). Beta’s own harness numbers stay research-only and are **not** promotion evidence.

## Arms to run

| ID | Profile | N / capital | Brake | Retention | Terminal delist |
|---|---|---|---|---|---|
| R50_nobrake | research | ~50 / 5M | OFF | 2×N (or retain_top=150) | none (baseline) |
| R50_brake | research | ~50 / 5M | ON (d=0.20, γ calibrated, floor=0.20) | same | none |
| R50_samevol | research | ~50 / 5M | static exposure matched to brake vol | same | none |
| R50_delist50 | research | ~50 / 5M | OFF | same | **−50%** at last close on delist |
| R50_delist100 | research | ~50 / 5M | OFF | same | **−100%** at last close on delist |
| L600_noret | live | 20–30 / 600k | OFF | OFF | none |
| L600_ret2x | live | 20–30 / 600k | OFF | **2×N** | none |
| L600_delist50 | live | 20–30 / 600k | OFF | 2×N | **−50%** |
| L600_delist100 | live | 20–30 / 600k | OFF | 2×N | **−100%** |

Optional references (from prior Beta harness): ex-post best static weight — label look-ahead, not a candidate.

## Engine rules to match (fixed path)

- Holdings always marked to **close**; limit-up / limit-down / halt **do not** zero returns.
- Buys blocked on limit-up / halt / ST; sells blocked on limit-down / halt; **unfilled orders roll forward**.
- Costs: commission 2.5 bp (min 5 CNY), slippage 5 bp, stamp tax sell-only by date (`v2_execution_costs.stamp_tax_bps_sell`).
- Min trade notional 2,000 CNY; board lot 100 (live profile pre-screens 1 lot).
- Decide at close d → trade at close d+1 (or T+1 open/VWAP if E1 standardizes that — state which).
- Ranking: **B1 full-market then filter** for any session ≥ 2023-01-03. Pre-2023 sessions: mark `survivorship_incomplete=true` and do not claim clean ranks.

## Metrics (per arm × tier)

CAGR, MDD, Calmar, ann vol, turnover (one-way / year), cost / sleeve capital, avg & min exposure, time at floor (brake arms), book-contribution MDD at tier weight.  
Acceptance focus (Leo / card 68 lineage): **drawdown and Calmar**, not CAGR chasing.

## Output convention

- Script: `scripts/smallcap_b2_engine_crosscheck.py`
- JSON: `output/v2_proto/smallcap_b2_engine_crosscheck.json`
- Fields: `status`, `engine_entrypoint`, `arms[]`, `tiers[]`, `metrics` (null until run), `promotion_approved=false`
- When E1 lands: set `status=ran_on_E1`, fill `engine_entrypoint`, attach nav paths; never flip promotion.

## Preconditions

1. Eng **E1** paper/execution entrypoint documented and importable.
2. Data full-market circ_mv panel for 2015–2022 if any arm window starts before 2023 (else restrict window and label).
3. Strategy baseline heavy jobs not overlapping (avoid 02:30–03:30 ET windows when flagged).

## Sign-off

| Role | Checks | Sign |
|---|---|---|
| Beta | arms list matches config; B1 ranking on; terminal marks wired | |
| Strategy | engine = fixed path; costs/stamp/lots match Mandate | |
| Eng | E1 entrypoint stable; no `block_mark_to_zero` | |
| Leo | research-only; no Mandate edit; promotion_approved=false | |

## Filled 2026-10-11 03:50 ET — engine entrypoint (from Strategy/Eng)

- **Engine**: `quantlab.platform.execution.run_weight_schedule(panels=load_execution_panels(ids,start,end), schedule={date:{code:w}}, initial_cash=5e6, config=ExecConfig.strategy_v1(impact_k=1.0, min_trade_value=2000), record_weights=True)`. It fills at the next open, rounds prices to 0.01, lot-rounds the target holding, caps participation at 10%, carries unfilled orders forward, enforces limits, charges commission 2.5bp (min 5 CNY), stamp tax by date, and square-root impact with k=1.0. This is the fixed-engine convention Leo confirmed. Strategy's paper runner can't take an external book.
- **510300** is just one more code in the schedule. Its prices are spliced from `data/v2/etf_510300` because the merged reader stops at 2026-06-30.
- **Runner**: `scripts/smallcap_engine_compare.py` (arms A0 / S10 / S15 / S20 / C2 / C3). Selector: `quantlab/beta/smallcap_history_selector.py` (2015+, B1 ranking). Output: `output/v2_proto/smallcap_engine_compare/summary.json` plus `nav_<arm>.csv`.
- **Terminal delist**: not in the engine. It is applied as a post-engine NAV overlay: subtract scenario × (held value at the close on last_trade_date) from every later NAV point. −50% is primary, −100% is the sensitivity.
- **Launch** (one heavy job; only after full_d1_fixed_armA finishes):
  `cd /workspace/QuantLab && PYTHONPATH=. nohup /workspace/qlvenv/bin/python scripts/smallcap_engine_compare.py --start 2015-06-01 --end 2026-10-09 > output/v2_proto/smallcap_engine_compare.log 2>&1 &`
- Dry run: 2024-06-03→2024-07-31 ran end to end in 9 s (`output/v2_proto/smallcap_engine_compare_dryrun/`). Those numbers are NOT results.
