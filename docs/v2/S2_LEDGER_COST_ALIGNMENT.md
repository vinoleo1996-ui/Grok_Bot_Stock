> **【交叉引用 2026-10-18 00:03 ET，Strategy】** OPTIMIZER Stage2 的 S2-3（DRAFT，`STRATEGY_OPTIMIZER_STAGE2_S2_3_DRAFT_ZH.md`）的成本口径采用本文的 `ledger_aligned_s2` 语义（2.5bp / ¥5 / 印花税只对股票卖出 / 5bp / 整手 / ¥2000）。本文「S2」与 Stage2「S2-x」同名不同事。本文旧 Full D1 数字仍为 pre-S2，不作 S2-3 基线。

> **【仅参考 / REFERENCE ONLY】2026-10-14 Strategy 标注（Arch 内审 #2/#3）**：本文数字来自旧纸面 `v2_strategy_paper`（v1 线）：close-to-close、无 T+1、不处理涨跌停、两次调仓间权重不漂移，且未传 total_return_factor（原始价、除息日记亏）。与主引擎 book-smoke（B4/S6/capacity_adv）口径**不可比**，不得作为决策依据。修复归属待 Eng 确认，见 docs/v2/STRATEGY_CPCV_CDAR_CONC60_ZH.md §4。

# S2 — Ledger cost semantics → V2 paper path

`promotion_approved=false`. Research-only. Fast-sim remains **not** promotion evidence.

## Goal

Align `quantlab/portfolio/v2_execution_costs.py` (+ Full D1 / paper costs runner) with the **fee / lot / stamp** semantics of the original cash ledger:

- `quantlab/backtest/ledger.py` (`fee`, execute lot rounding, slippage)
- `quantlab/backtest/tax.py` (dividend tax — **not** ported yet; see gaps)
- Mandate V2 costs + `portfolio_limits.lot_size_rounding` / `min_trade_notional_cny`

## Diff table (Mandate / pre-S2 V2 vs ledger)

| Item | Mandate V2 | ledger.py | pre-S2 V2 paper | **S2 V2 (now)** |
|------|------------|-----------|-----------------|-----------------|
| Commission rate | 2.5 bp one-way | `rule.commission` (fixtures 2.5 bp) | 2.5 bp | **2.5 bp (Mandate)** |
| Min commission / order | ¥5 | `rule.min_commission` (¥5) | ¥5 | **¥5** |
| Stamp sell-only | yes, hist CN table | stock sells only; 10bp→5bp @ 2023-08-28 | yes on **all** sell notional incl. ETF | **stock sells only; ETF excluded** |
| Slippage rate | 5 bp one-way | default **30 bp** price impact (`slippage=0.003`) | 5 bp additive on notional | **5 bp Mandate rate** (fast-sim additive; not price-impact engine) |
| Slippage model | notional·bps | fill px = open·(1±slip); may reject at limit | additive cost drag on NAV | **unchanged additive** (documented model gap) |
| 整手 lot | `floor_buy_to_lot` | floor target to `buy_lot`; odd-lot full exit OK | **none** (continuous weights) | **floor to 100; full exit odd-lot OK** |
| Min trade notional | ¥2000 | default `min_trade_value=1000` | none | **¥2000 (Mandate)** |
| Fee rounding | — | `money()` 0.01 HALF_UP | float | **`money()`** |
| Dividend tax | — | `tax.py` holding-period schedule on sells | none | **still none** (needs lot acquisition dates) |
| Participation / ADV cap | `max_order_vs_adv20=0.01` | `participation=0.01` | none | **still none** (P0 scope out) |
| T+1 / sell_delay | mandate t+1 | `rule.sell_delay` lots | none | **still none** |

### Rates vs semantics

- **Rates** follow Mandate (2.5 / 5 / hist stamp), not ledger’s historical default slippage 30 bp.
- **Semantics** follow ledger: min commission, stamp on stocks only, lot floor, min trade, money rounding.

## Code changes

1. `quantlab/portfolio/v2_execution_costs.py`
   - `money()`, `apply_lot_and_min_trade()`, `SEMANTICS_VERSION=ledger_aligned_s2`
   - `compute_rebalance_costs(..., etf_pays_stamp=False, lot_diag=...)`
   - Stamp base = stock sell notional only
2. `quantlab/portfolio/v2_strategy_paper_costs.py`
   - Path B: after limit/halt fill constraints → lot/min-trade → cost
   - Leftover weight from lot floor → cash
   - `cost_knobs.semantics_version` + lot diagnostics in `costs_ledger.csv`

## Full D1 status

| Artifact | Path | S2? |
|----------|------|-----|
| P0 Full D1 A/B (primary external) | `output/strategy_paper_costs/full_d1/` | **pre-S2** — continuous weights; ETF sells were stamped |
| Smoke 250 | `output/strategy_paper_costs/smoke_pool250/` | **pre-S2** (smoke only, not main conclusion) |

**Full D1 must be recomputed** under S2 before any cost-number claim is treated as current. This S2 ship does **not** re-run Full D1 (wall-clock too long); alignment + unit checks only.

Expected directional effect of S2 vs pre-S2 B:

- Slightly **lower** stamp (no ETF sell stamp)
- Slightly **lower** turnover / costs from lot floor + ¥2000 min trade (more cash residual)
- Metrics will move; do not compare pre-S2 vs post-S2 without a fresh Full D1.

## Still deferred (not S2)

- Share-level cash ledger / T+1 settlement / corporate actions / dividend tax
- Slippage as price impact + limit reject
- ADV participation caps
- LW / target-vol (S1) — separate workstream

## Reproduce unit check

```bash
cd /workspace/QuantLab
PYTHONPATH=. /workspace/qlvenv/bin/python -c "from quantlab.portfolio.v2_execution_costs import SEMANTICS_VERSION; print(SEMANTICS_VERSION)"
```

Paper re-run (when scheduled):

```bash
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.portfolio.v2_strategy_paper_costs
# Full D1 flag as used in prior P0 invocation
```

## 中文摘要（给 Leo）

S2 已把原仓账本的**佣金下限、印花税仅股票卖出、整手向下取整、最低成交额 ¥2000、费用分位四舍五入**接到 V2 成本路径；费率仍用 Mandate（佣金 2.5bp、滑点 5bp），不用账本默认 30bp 滑点。  
**磁盘上 Full D1 主结论数字仍是 S2 之前的**，需要重跑后才可更新对外成本表；250 池仍只作烟测。不抬 `max_etf`，`promotion_approved=false`。
