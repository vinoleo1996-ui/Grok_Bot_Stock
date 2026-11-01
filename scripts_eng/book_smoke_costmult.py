"""Research-only wrapper: run book_smoke with all cost params x MULT via exec_cfg overrides (engine defaults untouched)."""
import os, sys
sys.path.insert(0, os.getcwd())
import quantlab.portfolio.v2_multisleeve_book as M
MULT = float(os.environ.get("COST_MULT", "1.5"))
_orig = M.exec_cfg
def exec_cfg(D, idx, **ov):
    from dataclasses import replace
    base = _orig(D, idx, **ov)
    ks = ("commission","min_commission","stamp_before","stamp_after","slippage","impact_k","cb_commission","cb_min_commission")
    return replace(base, **{k: getattr(base, k) * MULT for k in ks})
M.exec_cfg = exec_cfg
from quantlab.portfolio.book_smoke import run
run(sys.argv[1:])
