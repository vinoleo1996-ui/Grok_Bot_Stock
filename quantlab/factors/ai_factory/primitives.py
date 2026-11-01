"""Back-compat shim — prefer ``quantlab.factors.ops`` (plan E3)."""
from quantlab.factors.ops import (  # noqa: F401
    LEAF_FEATURES as LEAF_NAMES,
    MAX_DEPTH as PRESET_MAX_DEPTH,
    MAX_NODES as PRESET_MAX_NODES,
    OPS,
    Expr,
    apply_expr,
    parse_expr,
)
