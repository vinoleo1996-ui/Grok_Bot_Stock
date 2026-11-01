"""Exchange price-limit rules used by the cash ledger and panel normalization.

Ratios below are the ones asserted by tests/test_free_research.py and
tests/test_review_fixes_20261007.py. A missing ratio means the rule table does
not cover that session (new-listing window), not a default of 10 percent.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

import pandas as pd

RULE_VERSION = "cn_daily_v1"
RULE_VERSIONS = frozenset({RULE_VERSION})
MAIN_BOARD_ST_10PCT = pd.Timestamp("2026-07-06")
CHINEXT_TWENTY_PCT = pd.Timestamp("2020-08-24")
NEW_LISTING_SESSIONS_WITHOUT_LIMIT = 5


def _digits(code) -> str:
    text = str(code).lower().strip()
    if "." in text:
        left, right = text.split(".", 1)
        text = right if right.isdigit() else left
    return text


def _board(code) -> str:
    num = _digits(code)
    if num.startswith(("300", "301")):
        return "chinext"
    if num.startswith(("688", "689")):
        return "star"
    if num.startswith(("43", "83", "87", "92")):
        return "bse"
    return "main"


def _is_st(value) -> bool:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return False
    try:
        if pd.isna(value):
            return False
    except TypeError:
        pass
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "y", "st"}
    return bool(value)


def _session_stamp(value) -> pd.Timestamp:
    stamp = pd.Timestamp(value)
    if stamp.tzinfo is not None:
        stamp = stamp.tz_convert("Asia/Shanghai").tz_localize(None)
    return stamp.normalize()


def limit_ratio(code, date, is_st=False, listing_age=None):
    """Return the limit ratio, or None when the dated rule is not defined."""
    if listing_age is not None:
        try:
            if pd.notna(listing_age) and int(listing_age) <= NEW_LISTING_SESSIONS_WITHOUT_LIMIT:
                return None
        except (TypeError, ValueError):
            return None
    day = _session_stamp(date)
    board = _board(code)
    st = _is_st(is_st)
    if board == "star":
        return 0.20
    if board == "bse":
        return 0.30
    if board == "chinext":
        if day >= CHINEXT_TWENTY_PCT:
            return 0.20
        return 0.05 if st else 0.10
    if st and day < MAIN_BOARD_ST_10PCT:
        return 0.05
    return 0.10


def limit_prices(reference, ratio, tick=0.01):
    """Round limit prices to the tick with half-up, matching the ledger."""
    step = Decimal(str(tick))

    def round_price(value: Decimal) -> float:
        units = (value / step).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        return float(units * step)

    ref = Decimal(str(reference))
    span = Decimal(str(ratio))
    return round_price(ref * (1 + span)), round_price(ref * (1 - span))
