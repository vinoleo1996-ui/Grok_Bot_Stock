"""PRIMARY external Strategy paper: Full D1 + costs + limit/halt + residual-beta-c.

Arms
----
A : zero-cost, book sized to ``residual_book_weight_cap`` (old fill)
B : costs + limit/halt, book sized to ``residual_weight_to_hit_target_beta``

``promotion_approved=false``. Does **not** raise max_etf.
Smoke pool=250 lives under ``output/strategy_paper_costs/smoke_pool250/``.

Reproduce::

    cd /workspace/QuantLab
    PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.portfolio.v2_strategy_paper_full_d1_costs
"""
from __future__ import annotations

from quantlab.portfolio.v2_strategy_paper_costs import run_ab_compare


def main() -> None:
    run_ab_compare(full_d1=True, primary_external=True, use_panel_cache=True)


if __name__ == "__main__":
    main()
