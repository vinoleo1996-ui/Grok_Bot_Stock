"""S2 ledger-aligned cost semantics (research; promotion_approved=false)."""
from datetime import date

from quantlab.mandate_v2 import load_mandate_v2
from quantlab.portfolio.v2_execution_costs import (
    SEMANTICS_VERSION,
    apply_lot_and_min_trade,
    compute_rebalance_costs,
    money,
    stamp_tax_bps_sell,
)
from quantlab.backtest.ledger import money as ledger_money


def test_semantics_version():
    assert SEMANTICS_VERSION == "ledger_aligned_s2"


def test_money_matches_ledger():
    assert money(1.005) == ledger_money(1.005)
    assert money(1.004) == ledger_money(1.004)


def test_stamp_schedule():
    assert stamp_tax_bps_sell(date(2023, 8, 27)) == 10.0
    assert stamp_tax_bps_sell(date(2023, 8, 28)) == 5.0


def test_etf_sell_not_stamped():
    costs = load_mandate_v2().costs
    br = compute_rebalance_costs(
        weight_delta={"a": -0.1},
        portfolio_value_cny=600_000,
        session=date(2024, 6, 3),
        costs=costs,
        etf_delta=-0.05,
        etf_pays_stamp=False,
    )
    assert abs(br.stamp_tax_cny - 30.0) < 0.02  # 60k * 5bp only


def test_min_commission():
    costs = load_mandate_v2().costs
    br = compute_rebalance_costs(
        weight_delta={"a": 0.0001},
        portfolio_value_cny=600_000,
        session=date(2024, 6, 3),
        costs=costs,
    )
    assert br.commission_cny == 5.0


def test_min_trade_drop_and_full_exit():
    book = apply_lot_and_min_trade(
        prior_weights={"a": 0.05},
        target_weights={"a": 0.0501},
        portfolio_value_cny=600_000,
        prices={"a": 10.0},
        min_trade_notional_cny=2000.0,
    )
    assert book.n_dropped_min_trade >= 1
    exit_book = apply_lot_and_min_trade(
        prior_weights={"a": 0.05},
        target_weights={},
        portfolio_value_cny=600_000,
        prices={"a": 10.0},
    )
    assert "a" not in exit_book.adjusted_weights
    assert exit_book.weight_delta["a"] < 0
