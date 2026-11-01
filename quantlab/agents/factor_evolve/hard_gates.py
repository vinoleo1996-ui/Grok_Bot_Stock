"""Hard gates before a candidate may emit Book-Smoke weights.

QuantMind P0 (2026-10-12): dual-read ICIR, impact@60万∧100万≥10%,
who_pays_zh, overnight spirit ban. Never flips promotion.
"""
from __future__ import annotations

import math
import re
from typing import Any, Iterable

from quantlab.agents.factor_evolve.schemas import FactorCandidate, GateResult

HARD_GATE_VERSION = "factor_evolve_v2_qm_p0_20261012"
PROMOTION_APPROVED = False
ALLOWED_CAPITAL = frozenset({600_000, 1_000_000})
ALLOWED_UNIVERSE = frozenset({"mid_large_stock", "etf_core", "etf_sector", "etf_theme"})
IMPACT_FLOOR_PCT = 10.0
# |posthoc| large + gate thin → EDGE_WARN (still may pass)
ICIR_DUAL_GAP_POSTHOC_ABS = 1.0
ICIR_DUAL_GAP_GATE_MAX = 0.15

# Textbook / style-factor lexicon (mirror quantmind_loop; keep local to avoid import cycles on stub)
_TEXTBOOK_RE = re.compile(
    r"(?<![非不])(反转|动量|低波|低波动|换手率|turnover|momentum|reversal|low[\s\-]?vol|"
    r"价值因子|成长选股)|(?<![A-Za-z])(EP|BP)(?![A-Za-z])",
    re.I,
)

# Small-cap / ChiNext-main / STAR-main hints banned as primary universe
_SMALLCAP_RE = re.compile(r"(小盘|微盘|创业板主仓|科创板主仓|北交所主仓|ST主仓)", re.I)

# Overnight spirit (HARD BAN) — expr / mechanism / direction
_OVERNIGHT_RE = re.compile(
    r"(ind_rel_overnight|overnight\b|隔夜收益|隔夜跳空|隔夜alpha)",
    re.I,
)


def _try_novelty(expr: str) -> list[str]:
    reasons: list[str] = []
    try:
        from quantlab.factors.ai_factory.novelty import is_textbook_expr  # type: ignore

        if is_textbook_expr(expr):
            reasons.append("novelty.textbook_ban")
    except Exception:
        if _TEXTBOOK_RE.search(expr or ""):
            reasons.append("local.textbook_ban")
    return reasons


def _finite(x: Any) -> bool:
    try:
        return x is not None and math.isfinite(float(x))
    except (TypeError, ValueError):
        return False


def _as_float(x: Any) -> float:
    return float(x)


def _sign(x: float) -> int:
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def gate_candidate(c: FactorCandidate, *, capital_cny: int = 600_000) -> GateResult:
    reasons: list[str] = []
    tags: list[str] = list(c.get("tags") or [])
    cid = str(c.get("candidate_id") or "unknown")
    if capital_cny not in ALLOWED_CAPITAL:
        reasons.append(f"capital_not_in_60_100万:{capital_cny}")
    uk = str(c.get("universe_kind") or "")
    if uk not in ALLOWED_UNIVERSE:
        reasons.append(f"universe_banned_or_missing:{uk or 'empty'}")
    who = str(c.get("who_pays_zh") or "").strip()
    if not who:
        reasons.append("missing_who_pays_zh")
    mech = str(c.get("mechanism_tag") or "").strip()
    if not mech:
        reasons.append("missing_mechanism_tag")
    direction = str(c.get("direction_zh") or "")
    expr = str(c.get("expr_str") or "")
    blob = f"{direction}\n{expr}\n{mech}"
    if _TEXTBOOK_RE.search(blob):
        reasons.append("textbook_direction_or_expr")
    if _SMALLCAP_RE.search(blob) or _SMALLCAP_RE.search(uk):
        reasons.append("smallcap_main_banned")
    if _OVERNIGHT_RE.search(blob):
        reasons.append("HARD_BAN_OVERNIGHT_SPIRIT")
    reasons.extend(_try_novelty(expr))
    scores = c.get("score_rows") or []
    if not scores:
        reasons.append("no_score_rows")

    # --- QuantMind P0: dual-read ICIR ---
    # Production path requires icir_eps_gate. Smoke fixtures must carry the field
    # (no smoke_exempt bypass) so the gate path is identical.
    if "icir_eps_gate" not in c or not _finite(c.get("icir_eps_gate")):
        reasons.append("missing_icir_eps_gate")
    else:
        gate_icir = _as_float(c["icir_eps_gate"])
        if gate_icir <= 0:
            reasons.append("icir_eps_gate_nonpositive")
        posthoc_raw = c.get("icir_eps_posthoc")
        if _finite(posthoc_raw):
            posthoc = _as_float(posthoc_raw)
            if _sign(gate_icir) != 0 and _sign(posthoc) != 0 and _sign(gate_icir) != _sign(posthoc):
                reasons.append("DEMOTE_RESID_sign_flip")
            if abs(posthoc) > ICIR_DUAL_GAP_POSTHOC_ABS and gate_icir < ICIR_DUAL_GAP_GATE_MAX:
                if "EDGE_WARN_ICIR_DUAL_GAP" not in tags:
                    tags.append("EDGE_WARN_ICIR_DUAL_GAP")

    # --- QuantMind P0: impact @ 60万 ∧ 100万 ---
    imp60 = c.get("impact_flat25_pct_60万")
    imp100 = c.get("impact_flat25_pct_100万")
    if not _finite(imp60):
        reasons.append("missing_impact_flat25_pct_60万")
    if not _finite(imp100):
        reasons.append("missing_impact_flat25_pct_100万")
    if _finite(imp60) and _finite(imp100):
        if _as_float(imp60) < IMPACT_FLOOR_PCT or _as_float(imp100) < IMPACT_FLOOR_PCT:
            reasons.append("impact_flat25_below_10pct")

    # promotion always false — gate pass ≠ sealed
    assert PROMOTION_APPROVED is False
    verdict = "pass" if not reasons else "fail"
    out: GateResult = {
        "candidate_id": cid,
        "verdict": verdict,  # type: ignore[typeddict-item]
        "reasons": reasons,
        "hard_gate_version": HARD_GATE_VERSION,
    }
    if tags:
        out["tags"] = tags
    return out


def gate_batch(
    candidates: Iterable[FactorCandidate], *, capital_cny: int = 600_000
) -> list[GateResult]:
    return [gate_candidate(c, capital_cny=capital_cny) for c in candidates]
