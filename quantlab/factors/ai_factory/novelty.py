"""Novelty / textbook ban helpers for L1b. promotion_approved=False always."""
from __future__ import annotations

import re
from typing import Iterable

PROMOTION_APPROVED = False

TEXTBOOK_BANNED_LEAVES: frozenset[str] = frozenset(
    {
        "ret_1",
        "ret_5",
        "ret_10",
        "ret_20",
        "resid_ret_20",
        "rv_20",
        "vol_20",
        "skew_20",
        "max_ret_20",
        "turnover",
        "turn_20",
        "amihud",
        "log_vol",
        "log_price",
        "ep",
        "bp",
        "pe",
        "pb",
    }
)

STRUCTURAL_LEAVES: frozenset[str] = frozenset(
    {
        "limit_up_flag",
        "limit_down_flag",
        "lu_streak",
        "ld_streak",
        "lu_count_5",
        "days_since_lu",
        "overnight_ret",
        "intraday_ret",
        "on_minus_id",
        "etf_major_flow",
        "etf_theme_flow",
        "etf_flow_x_lu",
        "lockup_S_20",
        "if_basis",
        "if_basis_x_on",
        "if_basis_x_lu",
        # easy-stock L1c
        "lu_height",
        "mkt_max_height",
        "lu_promote_rate",
        "mkt_lu_breadth",
        "theme_lu_density",
        "ld_count_5",
        "days_since_ld",
        "ann_n_5",
        "ann_buyback_5",
        "ann_insider_dec_5",
        "ann_penalty_5",
        "ann_earn_signed_5",
    }
)

# L1c: pure limit-UP leaves = control only (not main Top-K)
LU_CONTROL_LEAVES: frozenset[str] = frozenset(
    {
        "days_since_lu",
        "lu_streak",
        "limit_up_flag",
        "lu_count_5",
        "etf_flow_x_lu",
        "if_basis_x_lu",
    }
)

# L1c main promotion whitelist (easystock + LD + lockup + ann title counts + non-LU structure)
L1C_MAIN_LEAVES: frozenset[str] = frozenset(
    {
        "lu_height",
        "mkt_max_height",
        "lu_promote_rate",
        "mkt_lu_breadth",
        "theme_lu_density",
        "limit_down_flag",
        "ld_streak",
        "ld_count_5",
        "days_since_ld",
        "lockup_S_20",
        "ann_n_5",
        "ann_buyback_5",
        "ann_insider_dec_5",
        "ann_penalty_5",
        "ann_earn_signed_5",
        "overnight_ret",
        "intraday_ret",
        "on_minus_id",
        "etf_major_flow",
        "etf_theme_flow",
        "if_basis",
        "if_basis_x_on",
    }
)


def is_lu_control_expr(expr_str: str) -> bool:
    """True if expr uses only LU-control leaves (or empty)."""
    leaves = leaves_in_expr_str(expr_str)
    if not leaves:
        return True
    return leaves.issubset(LU_CONTROL_LEAVES)


def is_l1c_main_expr(expr_str: str) -> bool:
    leaves = leaves_in_expr_str(expr_str)
    if not leaves:
        return False
    if leaves & LU_CONTROL_LEAVES:
        return False
    return leaves.issubset(L1C_MAIN_LEAVES | STRUCTURAL_LEAVES) and bool(
        leaves & L1C_MAIN_LEAVES
    )


_LEAF_RE = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")


def leaves_in_expr_str(expr_str: str) -> set[str]:
    toks = set(_LEAF_RE.findall(expr_str))
    # drop op names commonly appearing
    ops = {
        "add",
        "sub",
        "mul",
        "div",
        "neg",
        "abs",
        "rank",
        "zscore",
        "industry_neutral",
        "size_neutral",
    }
    for k in (1, 5, 10, 20):
        ops |= {f"delay_{k}", f"ts_mean_{k}", f"ts_std_{k}", f"ts_delta_{k}", f"ts_max_{k}"}
    return {t for t in toks if t not in ops}


def is_textbook_expr(expr_str: str) -> bool:
    leaves = leaves_in_expr_str(expr_str)
    if not leaves:
        return True
    return leaves.issubset(TEXTBOOK_BANNED_LEAVES)


def is_structural_expr(expr_str: str, allowed: Iterable[str] | None = None) -> bool:
    allowed_set = set(allowed) if allowed is not None else set(STRUCTURAL_LEAVES)
    leaves = leaves_in_expr_str(expr_str)
    if not leaves:
        return False
    return leaves.issubset(allowed_set)
