"""Research execution friction: Mandate costs + limit/halt marking.

``promotion_approved=false``. Fast-sim costs are **not** promotion evidence
(Mandate ``fast_sim_not_promotion_evidence``).

S2 (ledger-aligned) semantics — see ``docs/v2/S2_LEDGER_COST_ALIGNMENT.md``:
  - commission = max(notional * rate, min_cny) per order (Mandate rates)
  - stamp tax sell-only on **stocks** (not equity ETF), CN historical schedule
  - slippage = notional * Mandate bps (fast-sim; ledger uses price impact at same rate)
  - 整手: floor buys/partial sells to lot; full exit may include odd lot
  - drop orders below ``min_trade_notional_cny`` (Mandate default 2000)
  - fee money() rounding to 0.01 CNY (ledger)

Stamp tax (CN historical sell-only):
  - before 2023-08-28: 10 bp
  - on/after 2023-08-28: 5 bp

Limit / halt conventions match ``quantlab.universe.d1_masks``:
  - limit_up / limit_down are **prices**; hit when close crosses bound
  - halt when tradestatus == 0
  - missing fields → treat as tradable / normal mark (documented by caller)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Mapping, Sequence

import pandas as pd

from quantlab.data.v2_readers import V2DataRoots, default_v2_roots, load_merged_panel
from quantlab.mandate_v2 import MandateCostsV2, MandateV2, load_mandate_v2

# CN stamp-tax cutover (sell-only). Window for paper B starts 2024-06 → always 5bp.
STAMP_TAX_CUTOVER = date(2023, 8, 28)
STAMP_TAX_BPS_BEFORE = 10.0
STAMP_TAX_BPS_ON_OR_AFTER = 5.0

# A-share board lot defaults (matches InstrumentRules fixtures / ledger tests).
DEFAULT_BUY_LOT = 100
DEFAULT_SELL_LOT = 100
DEFAULT_MIN_TRADE_NOTIONAL_CNY = 2000.0  # Mandate portfolio_limits.min_trade_notional_cny
SEMANTICS_VERSION = "ledger_aligned_s2"


def money(x: float) -> float:
    """Ledger ``money()`` — CNY to 0.01, ROUND_HALF_UP."""
    return float(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def stamp_tax_bps_sell(session: date) -> float:
    if session < STAMP_TAX_CUTOVER:
        return STAMP_TAX_BPS_BEFORE
    return STAMP_TAX_BPS_ON_OR_AFTER


@dataclass(frozen=True)
class OrderCostBreakdown:
    buy_notional_cny: float
    sell_notional_cny: float
    n_buy_orders: int
    n_sell_orders: int
    commission_cny: float
    slippage_cny: float
    stamp_tax_cny: float
    total_cny: float
    stamp_tax_bps: float
    # S2 diagnostics (optional; 0 / empty when unused)
    stock_sell_notional_cny: float = 0.0
    etf_sell_notional_cny: float = 0.0
    n_dropped_min_trade: int = 0
    n_lot_rounded: int = 0
    n_price_missing_kept_continuous: int = 0
    notional_shaved_cny: float = 0.0
    semantics_version: str = SEMANTICS_VERSION


@dataclass(frozen=True)
class LotRoundedBook:
    """Holdings after 整手 + min-trade filter (ledger-aligned, research fast-sim)."""

    adjusted_weights: dict[str, float]
    weight_delta: dict[str, float]
    etf_delta: float
    n_dropped_min_trade: int
    n_lot_rounded: int
    n_price_missing_kept_continuous: int
    notional_shaved_cny: float
    notes: tuple[str, ...] = ()


def apply_lot_and_min_trade(
    *,
    prior_weights: Mapping[str, float],
    target_weights: Mapping[str, float],
    portfolio_value_cny: float,
    prices: Mapping[str, float] | None,
    buy_lot: int = DEFAULT_BUY_LOT,
    sell_lot: int = DEFAULT_SELL_LOT,
    min_trade_notional_cny: float = DEFAULT_MIN_TRADE_NOTIONAL_CNY,
    etf_prior: float = 0.0,
    etf_target: float = 0.0,
    etf_price: float | None = None,
    etf_buy_lot: int = DEFAULT_BUY_LOT,
    min_adjust_notional_cny: float | None = None,
) -> LotRoundedBook:
    """Floor share targets to lot (Mandate ``floor_buy_to_lot``); drop tiny orders.

    Ledger rules mirrored in weight space:
      - buy / partial sell: ``qty = floor(raw_shares / lot) * lot``
      - full exit (target≈0): sell entire prior shares (odd lot allowed)
      - skip order if |notional| < min_trade_notional (unless full exit)
      - missing price → keep continuous weight delta (note counted)

    ETF sleeve uses the same lot rule when ``etf_price`` is provided; otherwise
    continuous ``etf_target - etf_prior``.
    """
    if portfolio_value_cny <= 0:
        return LotRoundedBook(
            adjusted_weights={k: float(v) for k, v in target_weights.items() if float(v) > 1e-12},
            weight_delta={},
            etf_delta=float(etf_target) - float(etf_prior),
            n_dropped_min_trade=0,
            n_lot_rounded=0,
            n_price_missing_kept_continuous=0,
            notional_shaved_cny=0.0,
            notes=("non_positive_portfolio_value",),
        )

    prices = prices or {}
    adjusted: dict[str, float] = {}
    deltas: dict[str, float] = {}
    n_drop = 0
    n_lot = 0
    n_miss = 0
    shaved = 0.0
    notes: list[str] = []

    ids = set(prior_weights) | set(target_weights)
    for iid in ids:
        w0 = float(prior_weights.get(iid, 0.0))
        w1 = float(target_weights.get(iid, 0.0))
        continuous_dw = w1 - w0
        if abs(continuous_dw) <= 1e-12:
            if w1 > 1e-12:
                adjusted[iid] = w1
            continue

        px = prices.get(iid)
        if px is None or not (px == px) or float(px) <= 0:
            # no price → cannot lot-round; keep continuous (documented gap)
            n_miss += 1
            if w1 > 1e-12:
                adjusted[iid] = w1
            deltas[iid] = continuous_dw
            continue

        px = float(px)
        prior_shares = (w0 * portfolio_value_cny) / px
        target_shares_raw = (w1 * portfolio_value_cny) / px
        full_exit = w1 <= 1e-12

        if full_exit:
            # ledger: odd lot may be sold as entire remaining position
            qty_delta = -int(max(0, round(prior_shares)))  # sell all whole shares we mark
            # keep fractional mark clean: zero weight
            new_shares = 0
        else:
            side_buy = target_shares_raw > prior_shares
            lot = int(buy_lot if side_buy else sell_lot)
            # floor target shares to lot (Mandate floor_buy_to_lot / ledger target)
            floored_target = (int(target_shares_raw) // lot) * lot
            if abs(floored_target - target_shares_raw) > 1e-9:
                n_lot += 1
            # do not sell below zero; do not invent short
            floored_target = max(0, floored_target)
            # if prior had odd lot and we are not full-exiting, partial sell floors
            prior_int = int(max(0, round(prior_shares)))
            qty_delta = floored_target - prior_int
            # align buy/sell step
            if qty_delta > 0:
                qty_delta = (qty_delta // buy_lot) * buy_lot
            elif qty_delta < 0:
                # partial sell: floor magnitude to sell_lot
                mag = ((-qty_delta) // sell_lot) * sell_lot
                qty_delta = -mag
                # if rounding wiped the trade but prior != floored target intent, drop
            new_shares = prior_int + qty_delta

        notional = abs(qty_delta) * px
        continuous_notional = abs(continuous_dw) * portfolio_value_cny
        shaved += max(0.0, continuous_notional - notional)

        if qty_delta == 0:
            # no trade — keep prior weight (lot / tiny)
            if not full_exit and abs(continuous_dw) * portfolio_value_cny < float(min_trade_notional_cny):
                n_drop += 1
            if w0 > 1e-12:
                adjusted[iid] = w0
            continue

        # Strategy 2026-10-11: resize orders (neither a new entry nor a full exit) use the larger
        # min_adjust_notional_cny so the ¥5 minimum commission does not dominate small trims/top-ups.
        thr = float(min_trade_notional_cny)
        if min_adjust_notional_cny is not None and w0 > 1e-12 and not full_exit:
            thr = max(thr, float(min_adjust_notional_cny))
        if (not full_exit) and notional < thr:
            n_drop += 1
            if w0 > 1e-12:
                adjusted[iid] = w0
            continue

        new_w = (new_shares * px) / portfolio_value_cny if new_shares > 0 else 0.0
        if new_w > 1e-12:
            adjusted[iid] = float(new_w)
        deltas[iid] = float(new_w - w0)

    # ETF sleeve
    etf_dw = float(etf_target) - float(etf_prior)
    if abs(etf_dw) > 1e-12 and etf_price is not None and etf_price == etf_price and float(etf_price) > 0:
        px = float(etf_price)
        lot = int(etf_buy_lot)
        prior_sh = (float(etf_prior) * portfolio_value_cny) / px
        target_sh_raw = (float(etf_target) * portfolio_value_cny) / px
        full_exit = float(etf_target) <= 1e-12
        if full_exit:
            qty_delta = -int(max(0, round(prior_sh)))
            new_sh = 0
        else:
            floored = (int(target_sh_raw) // lot) * lot
            if abs(floored - target_sh_raw) > 1e-9:
                n_lot += 1
            prior_int = int(max(0, round(prior_sh)))
            qty_delta = floored - prior_int
            if qty_delta > 0:
                qty_delta = (qty_delta // lot) * lot
            elif qty_delta < 0:
                qty_delta = -(((-qty_delta) // lot) * lot)
            new_sh = prior_int + qty_delta
        notional = abs(qty_delta) * px
        shaved += max(0.0, abs(etf_dw) * portfolio_value_cny - notional)
        if qty_delta == 0 or (
            (not full_exit) and notional < float(min_trade_notional_cny)
        ):
            if abs(etf_dw) * portfolio_value_cny < float(min_trade_notional_cny) or qty_delta == 0:
                n_drop += 1
            etf_dw = 0.0
        else:
            etf_dw = (new_sh * px) / portfolio_value_cny - float(etf_prior)
    elif abs(etf_dw) > 1e-12:
        notes.append("etf_price_missing_kept_continuous")

    if n_miss:
        notes.append(f"price_missing_kept_continuous={n_miss}")

    return LotRoundedBook(
        adjusted_weights=adjusted,
        weight_delta={k: v for k, v in deltas.items() if abs(v) > 1e-12},
        etf_delta=float(etf_dw),
        n_dropped_min_trade=int(n_drop),
        n_lot_rounded=int(n_lot),
        n_price_missing_kept_continuous=int(n_miss),
        notional_shaved_cny=float(shaved),
        notes=tuple(notes),
    )


def compute_rebalance_costs(
    *,
    weight_delta: Mapping[str, float],
    portfolio_value_cny: float,
    session: date,
    costs: MandateCostsV2,
    etf_delta: float = 0.0,
    etf_label: str = "etf_510300",
    etf_pays_stamp: bool = False,
    lot_diag: LotRoundedBook | None = None,
) -> OrderCostBreakdown:
    """Cost on filled weight deltas (fraction of book → CNY via portfolio_value).

    Ledger-aligned (S2):
      - Commission per order = max(notional * bps, min_cny), money()-rounded sum
      - Slippage = notional * Mandate slippage_bps (one-way)
      - Stamp on **stock** sell notional only (ETF sleeve excluded unless
        ``etf_pays_stamp=True``; ledger InstrumentRules.asset_type=="stock")
      - Optional ``lot_diag`` attaches 整手 / min-trade diagnostics

    Each name (and optional ETF sleeve) with |Δw| > 0 is one order.
    """
    stamp_bps = stamp_tax_bps_sell(session) if costs.stamp_tax_sell_only else 0.0
    if portfolio_value_cny <= 0:
        return OrderCostBreakdown(
            0, 0, 0, 0, 0, 0, 0, 0, stamp_bps,
            semantics_version=SEMANTICS_VERSION,
        )

    buy_notional = 0.0
    sell_notional = 0.0
    stock_sell_notional = 0.0
    etf_sell_notional = 0.0
    n_buy = 0
    n_sell = 0
    commission = 0.0
    rate = costs.commission_bps_one_way / 10_000.0
    min_c = float(costs.commission_min_cny_per_order)

    def _one(delta: float, *, is_etf: bool = False) -> None:
        nonlocal buy_notional, sell_notional, stock_sell_notional, etf_sell_notional
        nonlocal n_buy, n_sell, commission
        if abs(delta) <= 1e-12:
            return
        notional = abs(delta) * portfolio_value_cny
        commission += max(notional * rate, min_c)
        if delta > 0:
            buy_notional += notional
            n_buy += 1
        else:
            sell_notional += notional
            n_sell += 1
            if is_etf:
                etf_sell_notional += notional
            else:
                stock_sell_notional += notional

    for _, dw in weight_delta.items():
        _one(float(dw), is_etf=False)
    _one(float(etf_delta), is_etf=True)

    slip_bps = costs.slippage_bps_one_way / 10_000.0
    slippage = (buy_notional + sell_notional) * slip_bps
    # stamp: stocks only (ledger); optional ETF override
    stamp_base = stock_sell_notional + (etf_sell_notional if etf_pays_stamp else 0.0)
    stamp = stamp_base * (stamp_bps / 10_000.0)
    commission_r = money(commission)
    slippage_r = money(slippage)
    stamp_r = money(stamp)
    total = money(commission_r + slippage_r + stamp_r)

    return OrderCostBreakdown(
        buy_notional_cny=float(buy_notional),
        sell_notional_cny=float(sell_notional),
        n_buy_orders=int(n_buy),
        n_sell_orders=int(n_sell),
        commission_cny=float(commission_r),
        slippage_cny=float(slippage_r),
        stamp_tax_cny=float(stamp_r),
        total_cny=float(total),
        stamp_tax_bps=float(stamp_bps),
        stock_sell_notional_cny=float(stock_sell_notional),
        etf_sell_notional_cny=float(etf_sell_notional),
        n_dropped_min_trade=int(lot_diag.n_dropped_min_trade if lot_diag else 0),
        n_lot_rounded=int(lot_diag.n_lot_rounded if lot_diag else 0),
        n_price_missing_kept_continuous=int(
            lot_diag.n_price_missing_kept_continuous if lot_diag else 0
        ),
        notional_shaved_cny=float(lot_diag.notional_shaved_cny if lot_diag else 0.0),
        semantics_version=SEMANTICS_VERSION,
    )


@dataclass
class TradabilityPanels:
    """Bool panels: index=session (date), columns=instrument_id."""

    limit_up_hit: pd.DataFrame
    limit_down_hit: pd.DataFrame
    halted: pd.DataFrame
    is_st: pd.DataFrame
    # coverage diagnostics
    n_instruments_loaded: int = 0
    n_limit_price_missing_cells: int = 0
    n_tradestatus_missing_cells: int = 0
    n_is_st_missing_cells: int = 0
    notes: list[str] = field(default_factory=list)

    def flags_at(self, session: date, iid: str) -> tuple[bool, bool, bool, bool]:
        """Return (limit_up_hit, limit_down_hit, halted, is_st). Missing → False."""
        lu = ld = halt = st = False
        if iid in self.limit_up_hit.columns and session in self.limit_up_hit.index:
            v = self.limit_up_hit.at[session, iid]
            lu = bool(v) if v == v else False
        if iid in self.limit_down_hit.columns and session in self.limit_down_hit.index:
            v = self.limit_down_hit.at[session, iid]
            ld = bool(v) if v == v else False
        if iid in self.halted.columns and session in self.halted.index:
            v = self.halted.at[session, iid]
            halt = bool(v) if v == v else False
        if iid in self.is_st.columns and session in self.is_st.index:
            v = self.is_st.at[session, iid]
            st = bool(v) if v == v else False
        return lu, ld, halt, st

    def is_blocked(self, session: date, iid: str) -> bool:
        """Diagnostic only: limit-up / limit-down / halt flag that name-day."""
        lu, ld, halt, _st = self.flags_at(session, iid)
        return bool(lu or ld or halt)

    def block_mark_to_zero(self, session: date, iid: str) -> bool:
        """DEPRECATED (engine bug fix 2026-10-10): holdings are ALWAYS marked to
        close. Limit/halt only restricts trading. Always returns False."""
        return False

    def may_buy(self, session: date, iid: str) -> bool:
        lu, _ld, halt, st = self.flags_at(session, iid)
        return not (lu or halt or st)

    def may_sell(self, session: date, iid: str) -> bool:
        _lu, ld, halt, _st = self.flags_at(session, iid)
        return not (ld or halt)


def load_tradability_panels(
    instrument_ids: Sequence[str],
    start: date,
    end: date,
    *,
    roots: V2DataRoots | None = None,
) -> TradabilityPanels:
    """Load limit/halt/ST flags from merged D0+asof_extend panels."""
    roots = roots or default_v2_roots()
    lo, hi = pd.Timestamp(start), pd.Timestamp(end)

    lu_map: dict[str, pd.Series] = {}
    ld_map: dict[str, pd.Series] = {}
    halt_map: dict[str, pd.Series] = {}
    st_map: dict[str, pd.Series] = {}
    miss_limit = 0
    miss_ts = 0
    miss_st = 0
    loaded = 0
    notes: list[str] = []

    for iid in instrument_ids:
        view = load_merged_panel(str(iid), roots=roots)
        if view.frame is None or view.frame.empty:
            notes.append(f"no_panel:{iid}")
            continue
        frame = view.frame
        if "event_time" not in frame.columns or "close" not in frame.columns:
            notes.append(f"missing_close_or_et:{iid}")
            continue
        et = pd.to_datetime(frame["event_time"]).dt.normalize()
        mask = (et >= lo) & (et <= hi)
        sub = frame.loc[mask].copy()
        if sub.empty:
            continue
        loaded += 1
        sub["_et"] = pd.to_datetime(sub["event_time"]).dt.normalize()
        sub = sub.drop_duplicates(subset=["_et"], keep="last")
        idx = pd.Index([ts.date() for ts in sub["_et"]], name="session")
        close = pd.to_numeric(sub["close"], errors="coerce")

        if "limit_up" in sub.columns:
            lim_u = pd.to_numeric(sub["limit_up"], errors="coerce")
            miss_limit += int(lim_u.isna().sum())
            hit_u = (close.notna() & lim_u.notna() & (close >= lim_u - 1e-9)).astype(bool)
        else:
            miss_limit += len(sub)
            hit_u = pd.Series(False, index=sub.index)
            notes.append(f"limit_up_col_absent:{iid}")

        if "limit_down" in sub.columns:
            lim_d = pd.to_numeric(sub["limit_down"], errors="coerce")
            miss_limit += int(lim_d.isna().sum())
            hit_d = (close.notna() & lim_d.notna() & (close <= lim_d + 1e-9)).astype(bool)
        else:
            miss_limit += len(sub)
            hit_d = pd.Series(False, index=sub.index)
            notes.append(f"limit_down_col_absent:{iid}")

        if "tradestatus" in sub.columns:
            ts = pd.to_numeric(sub["tradestatus"], errors="coerce")
            miss_ts += int(ts.isna().sum())
            halted = (ts == 0.0).fillna(False).astype(bool)
            # also honor open_status == halted when present
            if "open_status" in sub.columns:
                os_halt = sub["open_status"].astype(str).eq("halted")
                halted = halted | os_halt.fillna(False)
        else:
            miss_ts += len(sub)
            halted = pd.Series(False, index=sub.index)

        if "is_st_at_open" in sub.columns:
            st_raw = pd.to_numeric(sub["is_st_at_open"], errors="coerce")
            miss_st += int(st_raw.isna().sum())
            st = (st_raw.fillna(0.0) != 0.0).astype(bool)
        else:
            miss_st += len(sub)
            st = pd.Series(False, index=sub.index)

        lu_map[str(iid)] = pd.Series(hit_u.to_numpy(), index=idx, dtype=bool)
        ld_map[str(iid)] = pd.Series(hit_d.to_numpy(), index=idx, dtype=bool)
        halt_map[str(iid)] = pd.Series(halted.to_numpy(), index=idx, dtype=bool)
        st_map[str(iid)] = pd.Series(st.to_numpy(), index=idx, dtype=bool)

    def _wide(m: dict[str, pd.Series]) -> pd.DataFrame:
        if not m:
            return pd.DataFrame(dtype=bool)
        out = pd.DataFrame(m)
        out.index = pd.Index(out.index, name="session")
        return out.sort_index().fillna(False).astype(bool)

    # collapse per-iid absent-col notes
    notes_summary = []
    if any(n.startswith("limit_up_col_absent") for n in notes):
        notes_summary.append("some_instruments_missing_limit_up_col")
    if any(n.startswith("no_panel") for n in notes):
        notes_summary.append(f"no_panel_count={sum(1 for n in notes if n.startswith('no_panel'))}")
    notes_summary.append(
        "missing_limit_price→no_hit (do not invent); missing tradestatus→not halted; "
        "missing is_st→not ST"
    )

    return TradabilityPanels(
        limit_up_hit=_wide(lu_map),
        limit_down_hit=_wide(ld_map),
        halted=_wide(halt_map),
        is_st=_wide(st_map),
        n_instruments_loaded=loaded,
        n_limit_price_missing_cells=miss_limit,
        n_tradestatus_missing_cells=miss_ts,
        n_is_st_missing_cells=miss_st,
        notes=notes_summary,
    )


def apply_fill_constraints(
    *,
    prior_weights: Mapping[str, float],
    target_weights: Mapping[str, float],
    session: date,
    tradability: TradabilityPanels,
) -> tuple[dict[str, float], dict[str, float], dict[str, str]]:
    """Apply no-fill rules; return (filled_weights, filled_deltas, block_reasons).

    - buy blocked on limit_up / halt / ST → keep prior
    - sell blocked on limit_down / halt → keep prior
    Unfilled residual weight stays in cash (caller reconciles).
    """
    ids = set(prior_weights) | set(target_weights)
    filled: dict[str, float] = {}
    deltas: dict[str, float] = {}
    reasons: dict[str, str] = {}
    for iid in ids:
        w0 = float(prior_weights.get(iid, 0.0))
        w1 = float(target_weights.get(iid, 0.0))
        dw = w1 - w0
        if abs(dw) <= 1e-12:
            if w1 > 1e-12:
                filled[iid] = w1
            continue
        if dw > 0:
            if not tradability.may_buy(session, iid):
                lu, _ld, halt, st = tradability.flags_at(session, iid)
                why = []
                if lu:
                    why.append("limit_up")
                if halt:
                    why.append("halt")
                if st:
                    why.append("is_st")
                reasons[iid] = "buy_blocked:" + "+".join(why or ["unknown"])
                if w0 > 1e-12:
                    filled[iid] = w0
                continue
        else:
            if not tradability.may_sell(session, iid):
                _lu, ld, halt, _st = tradability.flags_at(session, iid)
                why = []
                if ld:
                    why.append("limit_down")
                if halt:
                    why.append("halt")
                reasons[iid] = "sell_blocked:" + "+".join(why or ["unknown"])
                if w0 > 1e-12:
                    filled[iid] = w0
                continue
        if w1 > 1e-12:
            filled[iid] = w1
        deltas[iid] = dw
    return filled, deltas, reasons


def pending_from_blocks(
    target_weights: Mapping[str, float],
    block_reasons: Mapping[str, str],
) -> dict[str, float]:
    """Unfilled (blocked) orders → {iid: desired target weight} to carry over."""
    return {iid: float(target_weights.get(iid, 0.0)) for iid in block_reasons}


def carry_target(
    current_weights: Mapping[str, float],
    pending: Mapping[str, float],
) -> dict[str, float]:
    """Target for a carry-over day: hold current book, retry only pending names."""
    tgt = {k: float(v) for k, v in current_weights.items()}
    for iid, w in pending.items():
        if w > 1e-12:
            tgt[iid] = float(w)
        else:
            tgt.pop(iid, None)
    return tgt


def mandate_costs(mandate: MandateV2 | None = None) -> MandateCostsV2:
    m = mandate or load_mandate_v2()
    m.require_not_promoted()
    return m.costs


def costs_drag_on_unit_nav(
    *,
    cost_cny: float,
    unit_nav: float,
    capital_cny: float,
) -> float:
    """Return new unit NAV after deducting cost_cny from portfolio."""
    if capital_cny <= 0 or unit_nav <= 0 or cost_cny <= 0:
        return unit_nav
    pv = unit_nav * capital_cny
    return unit_nav * max(0.0, 1.0 - cost_cny / pv)
