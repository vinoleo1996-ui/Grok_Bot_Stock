"""Engine fix 2026-10-10: limit/halt never zeroes held returns; blocked orders carry over.
Research-only, promotion_approved=false."""
from datetime import date

import pandas as pd

from quantlab.portfolio.v2_execution_costs import (
    TradabilityPanels, apply_fill_constraints, carry_target, pending_from_blocks,
)
from quantlab.portfolio.v2_strategy_paper_costs import _book_ret

D1, D2, D3 = date(2025, 3, 3), date(2025, 3, 4), date(2025, 3, 5)


def _panels(lu=(), ld=(), halt=()):
    idx = [D1, D2, D3]
    def mk(cells):
        df = pd.DataFrame(False, index=idx, columns=["X", "Y"])
        for d, c in cells:
            df.at[d, c] = True
        return df
    return TradabilityPanels(limit_up_hit=mk(lu), limit_down_hit=mk(ld), halted=mk(halt), is_st=mk(()))


def test_limit_up_day_return_counted():
    rets = pd.DataFrame({"X": [0.0, 0.10, 0.0], "Y": [0.0, 0.01, 0.0]}, index=[D1, D2, D3])
    tp = _panels(lu=[(D2, "X")])
    book, n_blk = _book_ret({"X": 0.5, "Y": 0.5}, rets, D2, tradability=tp, zero_on_block=True)
    assert abs(book - 0.055) < 1e-12  # X's +10% limit-up return is counted
    assert n_blk == 1  # diagnostic count only


def test_halted_and_limit_down_returns_counted():
    rets = pd.DataFrame({"X": [0.0, -0.10, 0.0], "Y": [0.0, 0.0, 0.0]}, index=[D1, D2, D3])
    tp = _panels(ld=[(D2, "X")], halt=[(D2, "Y")])
    book, _ = _book_ret({"X": 1.0}, rets, D2, tradability=tp, zero_on_block=True)
    assert abs(book + 0.10) < 1e-12
    assert tp.block_mark_to_zero(D2, "X") is False


def test_halted_sell_deferred_then_executed():
    tp = _panels(halt=[(D2, "X")])
    prior = {"X": 0.3, "Y": 0.3}
    target = {"Y": 0.6}
    filled, _d, blocks = apply_fill_constraints(prior_weights=prior, target_weights=target, session=D2, tradability=tp)
    assert filled["X"] == 0.3 and "X" in blocks  # sell blocked on halt day
    pending = pending_from_blocks(target, blocks)
    assert pending == {"X": 0.0}
    # next tradable day: retry only pending names
    tgt3 = carry_target(filled, pending)
    filled3, _d3, blocks3 = apply_fill_constraints(prior_weights=filled, target_weights=tgt3, session=D3, tradability=tp)
    assert "X" not in filled3 and not blocks3
    assert pending_from_blocks(tgt3, blocks3) == {}


def test_limit_up_buy_deferred_then_executed():
    tp = _panels(lu=[(D2, "X")])
    filled, _d, blocks = apply_fill_constraints(prior_weights={}, target_weights={"X": 0.2}, session=D2, tradability=tp)
    assert "X" not in filled
    pending = pending_from_blocks({"X": 0.2}, blocks)
    filled3, _d, blocks3 = apply_fill_constraints(prior_weights=filled, target_weights=carry_target(filled, pending), session=D3, tradability=tp)
    assert filled3 == {"X": 0.2} and not blocks3
