"""Operator library v0 (plan E3 / §2.2): pure functions, serializable expressions.

Aligned to ``/workspace/QuantLab-AI_FACTOR_MINING_PLAN_ZH.md``.
All ops are PIT-safe only if callers pass asof-aligned panels known at t close.
``promotion_approved`` is never set here — eval layer forces False.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

import numpy as np
import pandas as pd

# --- caps (plan §4.3: no unconstrained huge formulas) ---
MAX_DEPTH = 4
MAX_NODES = 24
RET_NS = (1, 5, 10, 20)
VOL_NS = (5, 10, 20)
DELAY_NS = (1, 5, 10, 20)

# Leaf feature names expected in a panel dict (expand as Data lands).
EMBEDDING_LEAF_PREFIX: str = "emb_"
# AI-native: panels may include emb_0..emb_{d-1} from intel.embeddings;
# apply_expr already accepts any panel key present — no LEAF_FEATURES change required.

LEAF_FEATURES: tuple[str, ...] = (
    "ret_1",
    "ret_5",
    "ret_20",
    "log_price",
    "log_vol",
    "turnover",
    "amihud",
    "vol_20",
    "skew_20",
    "max_ret_20",
    "gap",
    "limit_up_flag",
    "limit_down_flag",
    "turn_20",
    "rv_20",
    "resid_ret_20",
)

# L1b structural-only leaf universe (plan amendment AI_FACTOR_L1b_STRUCTURAL)
STRUCTURAL_LEAF_FEATURES: tuple[str, ...] = (
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
    # easy-stock structural language (L1c) — non-textbook
    "lu_height",
    "mkt_max_height",
    "lu_promote_rate",
    "mkt_lu_breadth",
    "theme_lu_density",
    # L1c main: limit-down sequences + ann title event counts
    "ld_count_5",
    "days_since_ld",
    "ann_n_5",
    "ann_buyback_5",
    "ann_insider_dec_5",
    "ann_penalty_5",
    "ann_earn_signed_5",
)

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
        "gap",  # raw gap alone is overnight textbook-ish; L1b uses overnight_ret explicitly
    }
)


def cs_rank(x: pd.DataFrame) -> pd.DataFrame:
    return x.rank(axis=1, pct=True)


def cs_zscore(x: pd.DataFrame) -> pd.DataFrame:
    mu = x.mean(axis=1)
    sd = x.std(axis=1).replace(0.0, np.nan)
    return x.sub(mu, axis=0).div(sd, axis=0)


def safe_div(a: pd.DataFrame, b: pd.DataFrame) -> pd.DataFrame:
    return (a / b.replace(0.0, np.nan)).replace([np.inf, -np.inf], np.nan)


@dataclass(frozen=True)
class OpSpec:
    name: str
    arity: int
    fn: Callable[..., pd.DataFrame]


def _build_ops() -> dict[str, OpSpec]:
    ops: dict[str, OpSpec] = {
        "add": OpSpec("add", 2, lambda a, b: a + b),
        "sub": OpSpec("sub", 2, lambda a, b: a - b),
        "mul": OpSpec("mul", 2, lambda a, b: a * b),
        "div": OpSpec("div", 2, safe_div),
        "neg": OpSpec("neg", 1, lambda a: -a),
        "abs": OpSpec("abs", 1, lambda a: a.abs()),
        "rank": OpSpec("rank", 1, cs_rank),
        "zscore": OpSpec("zscore", 1, cs_zscore),
        # industry_neutral / size_neutral are optional arms — stubs require
        # extra panels; registered as identity until wired (still countable).
        "industry_neutral": OpSpec("industry_neutral", 1, lambda a: a),
        "size_neutral": OpSpec("size_neutral", 1, lambda a: a),
    }
    for k in DELAY_NS:
        ops[f"delay_{k}"] = OpSpec(f"delay_{k}", 1, lambda a, k=k: a.shift(k))
    for k in VOL_NS:
        ops[f"ts_mean_{k}"] = OpSpec(
            f"ts_mean_{k}", 1, lambda a, k=k: a.rolling(k, min_periods=max(2, k // 2)).mean()
        )
        ops[f"ts_std_{k}"] = OpSpec(
            f"ts_std_{k}", 1, lambda a, k=k: a.rolling(k, min_periods=max(2, k // 2)).std()
        )
        ops[f"ts_delta_{k}"] = OpSpec(f"ts_delta_{k}", 1, lambda a, k=k: a - a.shift(k))
        ops[f"ts_max_{k}"] = OpSpec(
            f"ts_max_{k}", 1, lambda a, k=k: a.rolling(k, min_periods=max(2, k // 2)).max()
        )
    return ops


OPS: dict[str, OpSpec] = _build_ops()


@dataclass
class Expr:
    kind: str  # 'leaf' | 'op'
    name: str
    children: tuple["Expr", ...] = ()

    def n_nodes(self) -> int:
        return 1 + sum(c.n_nodes() for c in self.children)

    def depth(self) -> int:
        return 1 if not self.children else 1 + max(c.depth() for c in self.children)

    def to_tuple(self) -> tuple:
        if self.kind == "leaf":
            return ("leaf", self.name)
        return ("op", self.name, *(c.to_tuple() for c in self.children))

    def to_str(self) -> str:
        if self.kind == "leaf":
            return self.name
        if not self.children:
            return self.name
        inner = ", ".join(c.to_str() for c in self.children)
        return f"{self.name}({inner})"


def parse_expr(obj: tuple | Expr) -> Expr:
    if isinstance(obj, Expr):
        return obj
    if obj[0] == "leaf":
        return Expr("leaf", obj[1])
    kids = tuple(parse_expr(c) for c in obj[2:])
    return Expr("op", obj[1], kids)


def apply_expr(expr: Expr | tuple, panels: Mapping[str, pd.DataFrame]) -> pd.DataFrame:
    e = parse_expr(expr)
    if e.depth() > MAX_DEPTH or e.n_nodes() > MAX_NODES:
        raise ValueError("expression exceeds MAX_DEPTH/MAX_NODES")
    if e.kind == "leaf":
        if e.name not in panels:
            raise KeyError(e.name)
        return panels[e.name]
    if e.name not in OPS:
        raise KeyError(e.name)
    op = OPS[e.name]
    args = [apply_expr(c, panels) for c in e.children]
    if len(args) != op.arity:
        raise ValueError(f"{e.name} arity {len(args)} != {op.arity}")
    return op.fn(*args)


def leaf_names_present(
    panels: Mapping[str, pd.DataFrame], *, structural_only: bool = False
) -> list[str]:
    names = STRUCTURAL_LEAF_FEATURES if structural_only else LEAF_FEATURES
    return [n for n in names if n in panels]
