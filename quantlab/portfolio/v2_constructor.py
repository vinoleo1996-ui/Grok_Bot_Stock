"""V2 PortfolioConstructor — Mandate-driven integrate scores → capped weights.

Strategy-owned research path (S1). Wires original
:mod:`quantlab.strategy.portfolio` (``ledoit_wolf_cov`` /
``target_vol_weights``) into residual-book construction when a returns
panel is supplied; falls back to score-rank equal stub otherwise.

Hard rules:
  - ``promotion_approved`` always False on outputs
  - refuse go-live / promotion paths
  - max_etf not raised here (Beta sleeve concern)
  - satellite default OFF (Beta concern)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Mapping, Sequence

from quantlab.mandate_v2 import MandateV2

# Research heuristic: monthly one-way budget prorated to one ordinary rebalance.
# biweekly ≈ 2 ordinary steps / month → half of monthly budget per step.
_BIWEEKLY_STEPS_PER_MONTH = 2.0

# Minimum daily rows (after column filter) before LW is attempted.
_LW_MIN_HISTORY = 30
# Drop names with fewer than this many non-null returns.
_LW_MIN_OBS_PER_NAME = 30


@dataclass(frozen=True)
class PortfolioConstructionResultV2:
    """Capped target weights for one research decision session."""

    session: date
    weights: Mapping[str, float]
    n_names: int
    method: str  # lw_target_vol | score_rank_equal_stub | score_proportional_stub | ...
    single_name_cap: float
    industry_cap: float
    turnover_one_way: float
    turnover_budget_applied: float
    turnover_clipped: bool
    industry_scheme: str
    promotion_approved: bool = False
    research_stub: bool = True
    notes: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.promotion_approved:
            raise ValueError("portfolio_v2_promotion_approved_must_be_false")
        if not self.research_stub:
            raise ValueError("portfolio_v2_must_flag_research_stub")
        total = sum(float(w) for w in self.weights.values())
        if self.weights and abs(total - 1.0) > 1e-6 and total > 1e-12:
            # Allow under-invested cash remainder; forbid >1.0
            if total > 1.0 + 1e-6:
                raise ValueError(f"portfolio_v2_weights_sum_gt_one:{total}")

    def as_series(self):
        """Return weights as a pandas Series (lazy import)."""
        import pandas as pd

        return pd.Series(dict(self.weights), dtype=float).sort_values(ascending=False)


@dataclass(frozen=True)
class PortfolioConstructorV2:
    """Mandate-driven integrate → capped weights (research).

    Knobs read from :class:`MandateV2`:
      - holdings band: min_positions_target .. max_positions_stocks (30–60)
      - max_single_stock_weight (5%)
      - max_industry_weight (25%) + unknown_industry_cap
      - turnover_budget_monthly_one_way (0.35)
      - ordinary_rebalance (biweekly) — used only to prorate turnover budget
      - risk.target_annual_vol — LW target-vol scale (residual book local)

    weighting_mode:
      - ``auto`` (default): LW when ``returns_panel`` usable, else stub
      - ``lw_target_vol``: require LW; still falls back to stub on failure
      - ``equal_stub``: force score-rank equal / proportional stub
    """

    mandate: MandateV2
    # When True, allocate proportional to positive rank-scores; else equal among selected.
    proportional_to_score: bool = False
    weighting_mode: str = "auto"  # auto | lw_target_vol | equal_stub
    # Opt-in (Strategy 2026-10-11): after the turnover clip, names NOT in this session's selection keep
    # alpha*prior weight forever (blend never reaches 0) -> holding count creeps up. When > 0, such
    # leftover names below this weight are fully exited and the book is capped at max_positions_stocks.
    prune_residual_below: float = 0.0

    def __post_init__(self) -> None:
        self.mandate.require_not_promoted()
        mode = (self.weighting_mode or "auto").lower()
        if mode not in ("auto", "lw_target_vol", "equal_stub"):
            raise ValueError(f"portfolio_v2_bad_weighting_mode:{self.weighting_mode}")

    def knobs(self) -> Mapping[str, object]:
        m = self.mandate
        return {
            "min_positions_target": m.portfolio_limits.min_positions_target,
            "max_positions_stocks": m.portfolio_limits.max_positions_stocks,
            "max_single_stock_weight": m.portfolio_limits.max_single_stock_weight,
            "max_industry_weight": m.portfolio_limits.max_industry_weight,
            "unknown_industry_cap": m.portfolio_limits.unknown_industry_cap,
            "industry_scheme": m.portfolio_limits.industry_scheme,
            "turnover_budget_monthly_one_way": m.rebalance.turnover_budget_monthly_one_way,
            "ordinary_rebalance": m.rebalance.ordinary_rebalance,
            "signal_mode": m.signal_construction.default_mode,
            "target_annual_vol": m.risk.target_annual_vol,
            "weighting_mode": self.weighting_mode,
            "promotion_approved": False,
            "optimizer": "lw_target_vol_with_equal_stub_fallback",
            "satellite_default": "OFF",
            "max_etf_unchanged": True,
        }

    def optimize_ledoit_wolf(
        self,
        scores: Mapping[str, float],
        *,
        returns_panel: object = None,
        industry_labels: Mapping[str, str] | None = None,
        session: date | None = None,
        book_weight_cap: float | None = None,
    ) -> Mapping[str, float]:
        """LW + target-vol weights for residual book (research).

        Requires a usable ``returns_panel`` (date × instrument daily returns).
        On failure raises ``ValueError`` (callers that want silent fallback
        should use :meth:`construct` with ``weighting_mode='auto'``).
        """
        self.mandate.require_not_promoted()
        if returns_panel is None:
            raise ValueError("portfolio_v2_lw_requires_returns_panel")
        sess = session or date.today()
        result = self.construct(
            scores,
            session=sess,
            industry_labels=industry_labels,
            returns_panel=returns_panel,
            book_weight_cap=book_weight_cap,
            weighting_mode="lw_target_vol",
            allow_stub_fallback=False,
        )
        if result.method != "lw_target_vol":
            raise ValueError(
                f"portfolio_v2_lw_failed:{','.join(result.notes[-4:])}"
            )
        return dict(result.weights)

    def step_turnover_budget(self) -> float:
        """One-way turnover budget for a single ordinary rebalance step."""
        monthly = float(self.mandate.rebalance.turnover_budget_monthly_one_way)
        cadence = (self.mandate.rebalance.ordinary_rebalance or "biweekly").lower()
        if cadence == "biweekly":
            return monthly / _BIWEEKLY_STEPS_PER_MONTH
        if cadence == "weekly":
            return monthly / 4.0
        if cadence.startswith("monthly"):
            return monthly
        # Unknown cadence: use monthly as conservative single-step cap
        return monthly

    def construct(
        self,
        scores: Mapping[str, float],
        *,
        session: date,
        industry_labels: Mapping[str, str] | None = None,
        prior_weights: Mapping[str, float] | None = None,
        universe: Sequence[str] | None = None,
        book_weight_cap: float | None = None,
        returns_panel: object = None,
        weighting_mode: str | None = None,
        allow_stub_fallback: bool = True,
        turn_scores: Mapping[str, float] | None = None,
    ) -> PortfolioConstructionResultV2:
        """Integrate scores → capped long-only weights (research).

        Parameters
        ----------
        scores:
            instrument_id → Alpha / composite score (higher = more preferred).
        industry_labels:
            optional instrument_id → SW_L1 (or scheme) label for industry caps.
        prior_weights:
            previous target weights; when provided, one-way turnover vs budget
            is enforced by shrinking the trade toward prior.
        universe:
            optional membership filter; scores outside universe are dropped.
        book_weight_cap:
            optional residual-book gross cap (e.g. from BetaSleevePlan /
            ``residual_weight_to_hit_target_beta``); if set, final weights are
            scaled to sum <= cap (cash absorbs remainder).
        returns_panel:
            optional pandas DataFrame (date × instrument_id) of daily returns
            for LW covariance + target-vol weights (S1).
        weighting_mode:
            override instance default for this call.
        allow_stub_fallback:
            when False and LW fails, return empty / raise via method flag notes
            rather than silently using equal stub (used by optimize_ledoit_wolf).
        turn_scores:
            **S1 stub hook only** — reserved for TURN overlay after Alpha
            integrate; ignored for weights in this revision (recorded in notes).
        """
        self.mandate.require_not_promoted()
        pl = self.mandate.portfolio_limits
        mode = (weighting_mode or self.weighting_mode or "auto").lower()
        notes: list[str] = [
            "research_path",
            "promotion_approved=false",
            f"signal_mode={self.mandate.signal_construction.default_mode}",
            f"weighting_mode={mode}",
            "satellite_default=OFF",
            "max_etf_unchanged",
        ]
        if turn_scores:
            notes.append(
                f"turn_scores_hook_stub_ignored_n={len(turn_scores)}"
            )

        # Filter + rank
        eligible = {
            str(k): float(v)
            for k, v in scores.items()
            if v is not None and float(v) == float(v)  # drop NaN
        }
        if universe is not None:
            allowed = {str(x) for x in universe}
            eligible = {k: v for k, v in eligible.items() if k in allowed}
            notes.append(f"universe_filter_n={len(allowed)}")

        if not eligible:
            return PortfolioConstructionResultV2(
                session=session,
                weights={},
                n_names=0,
                method="empty_scores_stub",
                single_name_cap=pl.max_single_stock_weight,
                industry_cap=pl.max_industry_weight,
                turnover_one_way=0.0,
                turnover_budget_applied=self.step_turnover_budget(),
                turnover_clipped=False,
                industry_scheme=pl.industry_scheme,
                promotion_approved=False,
                research_stub=True,
                notes=tuple(notes + ["no_eligible_scores"]),
            )

        # Holdings band: prefer up to max; if fewer scores, take all (may be < min)
        max_n = int(pl.max_positions_stocks)
        min_n = int(pl.min_positions_target)
        ranked = sorted(eligible.items(), key=lambda kv: kv[1], reverse=True)
        n_take = min(max_n, len(ranked))
        if n_take < min_n:
            notes.append(f"below_min_positions_target:{n_take}<{min_n}")
        selected = ranked[:n_take]
        ids = [k for k, _ in selected]
        raw_scores = {k: v for k, v in selected}
        labels = {str(k): str(v) for k, v in (industry_labels or {}).items()}

        prefer_lw = mode in ("auto", "lw_target_vol") and returns_panel is not None
        force_stub = mode == "equal_stub" or returns_panel is None
        method = "score_rank_equal_stub"
        weights: dict[str, float] = {}
        lw_ok = False

        if prefer_lw and not force_stub:
            lw_weights, lw_notes, lw_ok = _try_lw_target_vol(
                ids=ids,
                returns_panel=returns_panel,
                industry_labels=labels,
                mandate=self.mandate,
            )
            notes.extend(lw_notes)
            if lw_ok and lw_weights:
                weights = lw_weights
                method = "lw_target_vol"
            elif mode == "lw_target_vol" and not allow_stub_fallback:
                notes.append("lw_failed_no_stub_fallback")
                return PortfolioConstructionResultV2(
                    session=session,
                    weights={},
                    n_names=0,
                    method="lw_failed",
                    single_name_cap=pl.max_single_stock_weight,
                    industry_cap=pl.max_industry_weight,
                    turnover_one_way=0.0,
                    turnover_budget_applied=self.step_turnover_budget(),
                    turnover_clipped=False,
                    industry_scheme=pl.industry_scheme,
                    promotion_approved=False,
                    research_stub=True,
                    notes=tuple(notes),
                )
            else:
                notes.append("lw_fallback_to_equal_stub")

        if not lw_ok:
            # Initial weights: equal or score-proportional among positive shifts
            if self.proportional_to_score:
                shifted = {
                    k: max(v - min(raw_scores.values()) + 1e-12, 1e-12)
                    for k, v in raw_scores.items()
                }
                s = sum(shifted.values())
                weights = {k: shifted[k] / s for k in ids}
                method = "score_proportional_stub"
            else:
                w = 1.0 / len(ids)
                weights = {k: w for k in ids}
                method = "score_rank_equal_stub"
            notes.append("optimizer=equal_stub")

        # Single-name cap (safety even after LW, which uses 1/N+dev)
        weights = _apply_single_name_cap(weights, pl.max_single_stock_weight)
        notes.append(f"single_name_cap={pl.max_single_stock_weight}")

        # Industry cap (LW already constrains via sector; re-apply Mandate unknown_cap)
        weights, ind_notes = _apply_industry_cap(
            weights,
            labels,
            max_industry=pl.max_industry_weight,
            unknown_cap=pl.unknown_industry_cap,
            renormalize=(method != "lw_target_vol"),
        )
        notes.extend(ind_notes)

        if method != "lw_target_vol":
            # Renormalize to 1.0 after caps (long-only full residual book before book cap)
            weights = _renormalize(weights)
        else:
            # Preserve LW under-invest (target-vol cash); only drop negatives
            weights = {k: max(0.0, float(v)) for k, v in weights.items() if float(v) > 1e-12}
            notes.append(f"lw_gross_before_book_cap={sum(weights.values()):.6f}")

        # Turnover vs prior
        budget = self.step_turnover_budget()
        turnover = 0.0
        clipped = False
        if prior_weights:
            prior = {str(k): float(v) for k, v in prior_weights.items() if float(v) > 0}
            weights, turnover, clipped = _clip_turnover(prior, weights, budget)
            if self.prune_residual_below > 0:
                sel = set(ids)
                n0 = len(weights)
                weights = {k: v for k, v in weights.items() if k in sel or v >= self.prune_residual_below}
                if len(weights) > max_n:
                    weights = dict(sorted(weights.items(), key=lambda kv: kv[1], reverse=True)[:max_n])
                if len(weights) < n0:
                    turnover = _one_way_turnover(prior, weights)
                    notes.append(f"pruned_residuals={n0 - len(weights)}")
            notes.append(f"turnover_budget_step={budget}")
            notes.append(f"turnover_one_way={turnover:.6f}")
            if clipped:
                notes.append("turnover_clipped_to_budget")
        else:
            notes.append("no_prior_weights_turnover_skipped")

        # Optional residual book cap (Beta sleeve / residual_weight_to_hit_target_beta)
        if book_weight_cap is not None:
            cap = max(0.0, float(book_weight_cap))
            total = sum(weights.values())
            if total > cap + 1e-12 and total > 0:
                scale = cap / total
                weights = {k: v * scale for k, v in weights.items()}
                notes.append(f"book_weight_cap={cap}")
            elif total > 0:
                notes.append(f"book_weight_cap={cap}_not_binding_gross={total:.6f}")

        # Drop near-zero dust
        weights = {k: round(v, 10) for k, v in weights.items() if v > 1e-12}

        return PortfolioConstructionResultV2(
            session=session,
            weights=dict(sorted(weights.items(), key=lambda kv: kv[1], reverse=True)),
            n_names=len(weights),
            method=method,
            single_name_cap=pl.max_single_stock_weight,
            industry_cap=pl.max_industry_weight,
            turnover_one_way=float(turnover),
            turnover_budget_applied=float(budget),
            turnover_clipped=clipped,
            industry_scheme=pl.industry_scheme,
            promotion_approved=False,
            research_stub=True,
            notes=tuple(notes),
        )


def _mandate_to_portfolio_cfg(mandate: MandateV2, n: int):
    """Map Mandate V2 knobs onto legacy PortfolioConfig for target_vol_weights."""
    from quantlab.config import PortfolioConfig

    pl = mandate.portfolio_limits
    risk = mandate.risk
    n = max(int(n), 1)
    base = 1.0 / n
    # Cap each name at Mandate max_single_stock_weight via weight_max_dev.
    weight_max_dev = max(0.0, float(pl.max_single_stock_weight) - base)
    return PortfolioConfig(
        target_vol=float(risk.target_annual_vol),
        max_sector_weight=float(pl.max_industry_weight),
        weight_max_dev=weight_max_dev,
    )


def _try_lw_target_vol(
    *,
    ids: Sequence[str],
    returns_panel: object,
    industry_labels: Mapping[str, str],
    mandate: MandateV2,
) -> tuple[dict[str, float], list[str], bool]:
    """Attempt original LW + target_vol_weights. Returns (weights, notes, ok)."""
    notes: list[str] = []
    try:
        import pandas as pd
        from quantlab.strategy.portfolio import target_vol_weights
    except Exception as exc:  # noqa: BLE001
        notes.append(f"lw_import_fail:{type(exc).__name__}:{exc}")
        return {}, notes, False

    if returns_panel is None:
        notes.append("lw_no_returns_panel")
        return {}, notes, False

    try:
        if not isinstance(returns_panel, pd.DataFrame):
            returns_panel = pd.DataFrame(returns_panel)
        panel = returns_panel.copy()
        panel.columns = [str(c) for c in panel.columns]
    except Exception as exc:  # noqa: BLE001
        notes.append(f"lw_panel_coerce_fail:{type(exc).__name__}:{exc}")
        return {}, notes, False

    present = [i for i in ids if i in panel.columns]
    missing = [i for i in ids if i not in panel.columns]
    if missing:
        notes.append(f"lw_missing_return_cols={len(missing)}")
    if len(present) < max(5, int(mandate.portfolio_limits.min_positions_target) // 2):
        notes.append(f"lw_too_few_cols:{len(present)}")
        return {}, notes, False

    sub = panel[present]
    ok_cols = [
        c for c in sub.columns if int(sub[c].notna().sum()) >= _LW_MIN_OBS_PER_NAME
    ]
    dropped = len(present) - len(ok_cols)
    if dropped:
        notes.append(f"lw_drop_sparse_cols={dropped}")
    if len(ok_cols) < max(5, int(mandate.portfolio_limits.min_positions_target) // 2):
        notes.append(f"lw_too_few_dense_cols:{len(ok_cols)}")
        return {}, notes, False

    sub = sub[ok_cols]
    # Strict intersection rows (matches original ledoit_wolf_cov dropna how=any)
    clean = sub.dropna(how="any")
    if len(clean) < _LW_MIN_HISTORY:
        notes.append(f"lw_insufficient_history:{len(clean)}<{_LW_MIN_HISTORY}")
        return {}, notes, False

    sector = None
    if industry_labels:
        sector = pd.Series(
            {c: industry_labels.get(c, "UNKNOWN") for c in clean.columns},
            dtype=object,
        )

    cfg = _mandate_to_portfolio_cfg(mandate, n=len(clean.columns))
    notes.append(f"lw_target_vol={cfg.target_vol}")
    notes.append(f"lw_max_sector={cfg.max_sector_weight}")
    notes.append(f"lw_n_names={len(clean.columns)}")
    notes.append(f"lw_n_days={len(clean)}")

    try:
        tv = target_vol_weights(clean, sector=sector, cfg=cfg, vol_mult=1.0)
    except Exception as exc:  # noqa: BLE001
        notes.append(f"lw_optimize_fail:{type(exc).__name__}:{exc}")
        return {}, notes, False

    if tv is None or tv.empty or "weight" not in tv.columns:
        notes.append("lw_empty_result")
        return {}, notes, False

    w = {str(i): float(v) for i, v in tv["weight"].items() if float(v) > 1e-12}
    if not w:
        notes.append("lw_all_zero_weights")
        return {}, notes, False

    gross = float(sum(w.values()))
    notes.append(f"lw_gross={gross:.6f}")
    notes.append("optimizer=lw_target_vol")
    return w, notes, True


def _renormalize(weights: Mapping[str, float]) -> dict[str, float]:
    total = sum(max(0.0, float(w)) for w in weights.values())
    if total <= 0:
        return {}
    return {k: max(0.0, float(w)) / total for k, w in weights.items()}


def _apply_single_name_cap(weights: Mapping[str, float], cap: float) -> dict[str, float]:
    """Clip each name to ``cap`` and redistribute residual pro-rata to uncapped."""
    if cap <= 0:
        raise ValueError("single_name_cap_must_be_positive")
    w = {k: max(0.0, float(v)) for k, v in weights.items()}
    for _ in range(len(w) + 2):
        over = {k: v for k, v in w.items() if v > cap + 1e-15}
        if not over:
            break
        excess = sum(v - cap for v in over.values())
        for k in over:
            w[k] = cap
        free = [k for k, v in w.items() if v < cap - 1e-15]
        if not free or excess <= 0:
            break
        free_sum = sum(w[k] for k in free)
        if free_sum <= 0:
            # equal split among free
            add = excess / len(free)
            for k in free:
                w[k] = min(cap, w[k] + add)
        else:
            for k in free:
                w[k] = min(cap, w[k] + excess * (w[k] / free_sum))
    return w


def _apply_industry_cap(
    weights: Mapping[str, float],
    labels: Mapping[str, str],
    *,
    max_industry: float,
    unknown_cap: float,
    renormalize: bool = True,
) -> tuple[dict[str, float], list[str]]:
    notes: list[str] = []
    w = dict(weights)
    if not labels:
        notes.append("industry_labels_absent_skip_industry_cap")
        return w, notes

    # Group
    groups: dict[str, list[str]] = {}
    for k in w:
        lab = labels.get(k) or "UNKNOWN"
        groups.setdefault(lab, []).append(k)

    for lab, members in groups.items():
        cap = unknown_cap if lab == "UNKNOWN" else max_industry
        gsum = sum(w[m] for m in members)
        if gsum > cap + 1e-12:
            scale = cap / gsum
            for m in members:
                w[m] *= scale
            notes.append(f"industry_cap_applied:{lab}:{gsum:.4f}->{cap}")

    if renormalize:
        # Renormalize after industry shrink so book stays fully invested pre book_cap
        w = _renormalize(w)
        # Re-apply single-pass industry check after renorm (may slightly re-breach);
        # iterate a few times.
        for _ in range(3):
            breached = False
            groups = {}
            for k in w:
                lab = labels.get(k) or "UNKNOWN"
                groups.setdefault(lab, []).append(k)
            for lab, members in groups.items():
                cap = unknown_cap if lab == "UNKNOWN" else max_industry
                gsum = sum(w[m] for m in members)
                if gsum > cap + 1e-12:
                    scale = cap / gsum
                    for m in members:
                        w[m] *= scale
                    breached = True
            if breached:
                w = _renormalize(w)
            else:
                break
    notes.append(f"industry_groups={len(groups)}")
    return w, notes


def _one_way_turnover(prior: Mapping[str, float], target: Mapping[str, float]) -> float:
    keys = set(prior) | set(target)
    return 0.5 * sum(abs(float(target.get(k, 0.0)) - float(prior.get(k, 0.0))) for k in keys)


def _clip_turnover(
    prior: Mapping[str, float],
    target: Mapping[str, float],
    budget: float,
) -> tuple[dict[str, float], float, bool]:
    """Shrink target toward prior so one-way turnover <= budget."""
    to = _one_way_turnover(prior, target)
    if budget < 0:
        raise ValueError("turnover_budget_negative")
    if to <= budget + 1e-12:
        return dict(target), to, False
    if to <= 1e-15:
        return dict(target), 0.0, False
    # target' = prior + alpha * (target - prior), choose alpha so turnover' = budget
    alpha = budget / to
    keys = set(prior) | set(target)
    blended = {
        k: float(prior.get(k, 0.0)) + alpha * (float(target.get(k, 0.0)) - float(prior.get(k, 0.0)))
        for k in keys
    }
    blended = {k: v for k, v in blended.items() if v > 1e-12}
    # Keep non-negative; do not force renorm to 1 (cash may rise when shrinking risk book)
    blended = {k: max(0.0, v) for k, v in blended.items()}
    new_to = _one_way_turnover(prior, blended)
    return blended, new_to, True
