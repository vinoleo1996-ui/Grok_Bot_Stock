# Platform execution + cost options (`quantlab/platform/execution.py`)

Research-grade engineering helpers. Opt-in only: `Ledger` and `smallcap.sim` defaults are unchanged.
No strategy performance conclusions here.

## Units
| field | unit |
|---|---|
| `close/open/high/low/limit_up/limit_down` | CNY per share |
| `volume` | **shares** (convert lots with `normalize_volume_to_shares`) |
| `amount`, ADV, trade value, impact cost | CNY |
| `sigma_daily` | std of daily close-to-close returns (fraction) |
| weights | fraction of NAV at the signal close |

Units (ENG_PING `units_note`, 2026-10-10/11):
* Default merge `asof_extend_tushare_202610`: volume=**shares**, amount=**CNY** (prefer for amount).
* Legacy `asof_extend_202610`: volume may be **lots** → use `volume_shares` / `volume_unit`.
* D0: volume=shares.
`load_execution_panels` priority: `volume_shares` → `volume_unit` scale → infer from
`amount/(volume*close)` (~100=lots, ~1=shares); missing amount → 100 after D0 cutoff, 1 before.

## API
```python
from quantlab.platform.execution import (ExecConfig, ExecPanels, ZERO_COST, run_weight_schedule,
    capacity_curve, reconcile_zero_cost, cost_ladder, split_returns, forward_return_components,
    sqrt_impact_cost, vwap_panel, normalize_volume_to_shares, round_order_quantity, lot_rule_for,
    load_execution_panels)

panels, diag = load_execution_panels(ids, "2025-01-01", "2026-10-09")   # small id lists; float32; 1 file at a time
res = run_weight_schedule(panels, schedule, initial_cash=2e6, config=ExecConfig(
        fill="next_open",          # close | next_open | next_vwap
        commission=0.00025, min_commission=5.0, stamp_before=0.001, stamp_after=0.0005,  # stamp cut 2023-08-28
        slippage=0.0,              # fraction per side
        impact_k=1.0, sigma_window=20, adv_window=20,   # 0 = impact off
        participation_cap=0.10,    # of that day's volume in shares; None = off
        unfilled="carry",          # carry | drop
        lots=True, enforce_limits=True, min_trade_value=0.0,
        no_limit_codes=frozenset({"sh.510300"}), order_rounding="target"))
# res: nav, nav_open, costs{commission,stamp,slippage,impact}, total_cost, requested_notional,
#      filled_notional, fill_ratio, final_shares, cash, events, fills, vwap_fallback_cells, impact_missing_fills
```
`schedule = {signal_session: {code: weight}}`; codes absent from a new signal are sold.

### Session order
1. mark at open → `nav_open`; 2. execute pending orders (sells first) at the fill price;
3. mark at close → `nav`; 4. on a signal day new target quantities (locked at signal-close NAV/close,
lot-rounded) replace all pending orders. `fill="close"` executes them at that same close.

### Fill prices
* `close`: signal-day close (same-day; look-ahead-ish, kept for comparison).
* `next_open`: T+1 open.
* `next_vwap`: T+1 `amount / volume_shares`. Fallback if amount missing/≤0 or VWAP outside [low, high]
  (unit mismatch): typical price (O+H+L+C)/4, else close. Count in `vwap_fallback_cells`.

### Costs
* commission `max(min_commission, rate*notional)`; stamp on sells only; slippage `px*(1±slippage)`.
* sqrt impact (CNY) = `trade_value * k * sigma_daily * sqrt(trade_value / ADV_value)`;
  sigma = rolling std of close-to-close returns (`sigma_window`, shifted 1 day, no look-ahead);
  ADV = rolling mean amount (`adv_window`, shifted 1). Missing ADV/sigma → 0 cost, counted in `impact_missing_fills`.
  Impact is charged to cash (does not move the fill price).
* participation cap: filled qty ≤ `cap * volume_shares` that day. Remainder: `carry` retries on
  following sessions until the next signal replaces it; `drop` discards it after the attempt day.

### Lots (what is implemented)
* main board / ChiNext: 100-share lots.
* STAR `688xxx/689xxx`: min 200, then 1-share steps.
* Beijing `bj.*`: min 100, then 1-share steps.
* Sells: same rule, but a sell that closes the whole position may be an odd quantity.

### Tradability (fills only; valuation always mark-to-close)
* buy blocked when fill price ≥ limit_up − 0.005; sell blocked when ≤ limit_down + 0.005.
* suspended (flag, NaN close, or volume==0) blocks both sides.
* halted holdings carry the last close; the full move realizes on resumption.

### Return decomposition
* `split_returns(open, close) -> (overnight, intraday)`; `(1+on)(1+id)-1 == close-to-close`.
* `forward_return_components(open, close, session, horizon)` → `{cc, overnight, intraday, open_entry}`
  dicts; pass any to `quantlab.factors.v2_min_pipeline.cross_section_ic(factor, fwd, ...)`.
* book level: `nav_open/nav.shift(1)-1` overnight, `nav/nav_open-1` intraday (includes trades at open).

### Capacity
`capacity_curve(panels, schedule, capitals=(5e5, 2e6, 1e7), config=None)` → DataFrame
`capital, net_return, zero_cost_return, cost_drag, cost_cny, fill_ratio`.
Default config: next_open, k=1, 10% cap. Keep id lists small (memory).

### Reconciliation
`reconcile_zero_cost(panels, schedule, initial_cash, paper_nav=None, tol=1e-9)` runs platform engine
(next_open, lots on, costs/limits/caps off), `backtest.Ledger` (cost_mult=0, slippage 0, cash_buffer 0)
and `smallcap.sim.simulate` (zero costs, cash_buffer 0, gross_cap 1). Returns `navs` DataFrame and
`diffs[name] = {per_day_diff, max_abs_diff, max_abs_rel_diff, first_divergence}`.
`paper_nav` (Strategy's runner NAV; level or unit) is rescaled to `initial_cash`.

Known convention differences the tool exposes:
* Ledger rounds fill prices to the 0.01 tick; use tick-rounded prices for exact match.
* fast sim lot-rounds the **trade** (toward zero); Ledger lot-rounds the **target**. Compare fast sim
  with `diffs["fastsim_vs_platform_delta_rounding"]` (platform with `order_rounding="delta"`).

`cost_ladder(panels, schedule, initial_cash, base=None, items=None)` starts at zero cost and enables one
item at a time (commission, stamp, slippage_10bp, sqrt_impact_k1, participation_10pct, limits, lots).

## Tests
`tests/test_execution_costs_platform.py` (synthetic only).

## Strategy v1 conventions (2026-10-10, agreed with QuantLab Strategy)

- **Tick**: `ExecConfig.price_tick` (default `None` = old behaviour). When set (0.01), the fill price after slippage is rounded half-up to the tick, same as `Ledger.execute`. `round_to_tick(px, tick)` is exported. The fast sim has the same option: `Costs.price_tick`.
- **Lot rounding on target holdings**: `order_rounding='target'` everywhere. Fast sim `Costs.order_rounding` now defaults to `'target'` (floor target holding to 100 shares; unchanged holdings, including odd lots, are not traded). **Legacy**: `Costs(order_rounding='delta')` / `ExecConfig(order_rounding='delta')` reproduces pre-2026-10-10 fast-sim results (trade rounded toward zero).
- **Preset**: `ExecConfig.strategy_v1(impact_k=1.0, **overrides)` = next_open, price_tick=0.01, impact_k=1.0, participation_cap=0.10, unfilled='carry', lots, enforce_limits, order_rounding='target'. Bare `ExecConfig()` defaults are unchanged.
- **Impact sensitivity**: `IMPACT_K_SENSITIVITY=(0.5,1.0,2.0)`, `impact_sensitivity_configs(base=None, ks=...) -> {k: ExecConfig}`, `run_impact_sensitivity(panels, schedule, initial_cash=..., base=None, ks=...) -> DataFrame[k, final_nav, total_return, impact_cny, total_cost, fill_ratio]`.
- **Weights output**: `run_weight_schedule(..., record_weights=True)` (default) returns `target_weights` (latest signal weights carried forward, 0 before the first signal) and `actual_weights` (post-fill holdings x close mark / NAV at that close), both float32 DataFrames session x code. Pass `record_weights=False` to skip (returns `None`). Memory: 4 bytes x sessions x codes per frame (~5.6k codes x 2.5k sessions ≈ 56 MB each).
- **Reconciliation**: `reconcile_zero_cost` now runs platform / Ledger / fast sim all with target rounding + 0.01 tick; on synthetic panels (on-tick and off-tick opens) all match with max |rel diff| <= 1e-9. Extra columns `platform_delta_rounding`, `fastsim_delta_rounding` and diff `fastsim_vs_platform_delta_rounding` keep the legacy convention checkable.


## 2026-10-11：可转债/ETF 新表、可交换债
- `load_execution_panels`：可转债和可交换债读 `data/v2/cb/cb_daily.parquet`（vol 手=10 张 → ×10；amount 万元 → ×1e4；剔除 is_placeholder 行）；merged reader 里没有的场内基金读 `data/v2/etf/etf_daily_adj.parquet`（vol 手=100 份 → ×100；amount 千元 → ×1000）。都用**原始价**成交和估值，hfq 列不用。pyarrow 按代码/日期过滤读。旧 raw 目录在新表不存在、或显式传 `cb_dir`/`fund_dir` 时作回退。
- `fund_adj_factor_actions=False`（默认）：不使用 etf_daily_adj 的复权因子做基金的除权处理。Data 在查 510300 等的假跳变（如 2026-01-19 +2.6%），fund_div 也还没到。确认前不要打开。注意：510300 仍走 merged reader 原路径，该路径原有的复权因子行为没有改动（见 E1 报告中的假跳变问题，另待决定）。
- 可交换债（sh.132xxx、sz.120xxx）：`instrument_type()=='eb'`；免印花税、10 张一手、最小价位 0.001、佣金同可转债（`cb_commission`/`cb_min_commission`），**不设 ±20% 涨跌幅**（Data：2022-08-01 可转债交易规则不适用于可交换债；**待合规复核**）。
