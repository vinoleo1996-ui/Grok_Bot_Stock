"""Platform Eng surface for Strategy / Alpha / Beta consumers.

Research-only: ``promotion_approved`` is always False. Do not invent NAV or
portfolio conclusions here — those stay with Strategy.
"""
from __future__ import annotations

from quantlab.platform.strategy_feed import (
    DEFAULT_CLOSE_CHUNK_SIZE,
    DEFAULT_CLOSE_DTYPE,
    STRATEGY_FEED_CACHE_DIR,
    STRATEGY_PAPER_V1_OUTPUT_DIR,
    biweekly_rebalance_sessions,
    cache_merged_close_panel,
    d1_members_at,
    d1_members_at_chunked,
    describe_strategy_feed,
    etf_510300_daily_returns,
    iter_merged_close_chunks,
    iter_merged_daily_return_chunks,
    load_cached_close_panel,
    merged_close_panel,
    merged_daily_returns,
    trading_sessions,
)

__all__ = [
    "DEFAULT_CLOSE_CHUNK_SIZE",
    "DEFAULT_CLOSE_DTYPE",
    "STRATEGY_FEED_CACHE_DIR",
    "STRATEGY_PAPER_V1_OUTPUT_DIR",
    "biweekly_rebalance_sessions",
    "cache_merged_close_panel",
    "d1_members_at",
    "d1_members_at_chunked",
    "describe_strategy_feed",
    "etf_510300_daily_returns",
    "iter_merged_close_chunks",
    "iter_merged_daily_return_chunks",
    "load_cached_close_panel",
    "merged_close_panel",
    "merged_daily_returns",
    "trading_sessions",
]

# Execution / cost options (opt-in). Import lazily-safe: pure numpy/pandas.
from quantlab.platform import execution  # noqa: E402,F401
__all__.append("execution")
