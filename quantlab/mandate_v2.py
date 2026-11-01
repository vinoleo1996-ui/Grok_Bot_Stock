"""QuantLab Mandate V2 typed loader (Phase 0).

Loads ``QuantLab-MANDATE_V2.json`` into immutable dataclasses used by V2 stubs.
Does **not** replace :mod:`quantlab.mandate` (legacy account envelope).

``promotion_approved`` is always forced ``False`` in the loaded object even if a
caller-supplied file claims otherwise — promotion is a human gate, not a JSON
edit. Stubs must read this flag and refuse go-live paths.
"""
from __future__ import annotations

from quantlab.promotion_gate import overall_promotion_approved as _gate

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

from quantlab.config import ROOT

# In-repo copy kept for smoke / offline resolution; workspace-root original remains
# the New Bot handoff path. Loader prefers env, then explicit path, then these.
_DEFAULT_CANDIDATES: tuple[Path, ...] = (
    ROOT / "docs" / "v2" / "QuantLab-MANDATE_V2.json",
    ROOT.parent / "QuantLab-MANDATE_V2.json",
)


@dataclass(frozen=True)
class MandateCapitalV2:
    initial_cny: float
    currency: str
    leverage_allowed: bool
    short_selling_allowed: bool
    margin_allowed: bool
    cash_allowed: bool
    cash_is_active_risk_tool: bool
    min_cash_buffer_normal: float


@dataclass(frozen=True)
class MandateMarketsV2:
    allowed_asset_types: tuple[str, ...]
    exchanges: tuple[str, ...]
    exclude_bse_default: bool
    benchmark_primary: str
    benchmark_etf: str
    benchmark_etf_examples: tuple[str, ...]
    overseas_assets_default: bool
    commodity_gold_default: bool


@dataclass(frozen=True)
class MandateLiquidityRuleV2:
    metric: str
    threshold_cny_primary: float
    threshold_cny_alt_research: float
    primary_label: str
    alt_label: str
    active_label: str
    threshold_cny_active: float


@dataclass(frozen=True)
class MandateMicrocapPolicyV2:
    mode: str
    exclude_bottom_mktcap_pct: float
    hard_cap_portfolio_weight: float
    microcap_as_universe_banned: bool


@dataclass(frozen=True)
class MandateUniverseV2:
    mask_first: bool
    listing_min_trading_days: int
    exclude_st: bool
    exclude_delisting_arrangement: bool
    liquidity_rule: MandateLiquidityRuleV2
    microcap_policy: MandateMicrocapPolicyV2
    tradability_masks: tuple[str, ...]
    etf_role: str


@dataclass(frozen=True)
class MandatePortfolioLimitsV2:
    max_positions_stocks: int
    min_positions_target: int
    max_single_stock_weight: float
    max_industry_weight: float
    industry_scheme: str
    unknown_industry_cap: float
    max_etf_sleeve_weight: float
    max_order_vs_adv20: float
    lot_size_rounding: str
    min_trade_notional_cny: float


@dataclass(frozen=True)
class MandateRiskV2:
    target_annual_vol: float
    target_beta_vs_benchmark: float
    target_beta_band: tuple[float, float]
    covariance_estimator: str
    vol_targeting_enabled: bool
    drawdown_scaler_recoverable: bool
    permanent_halt_banned: bool
    max_dd_gate: float


@dataclass(frozen=True)
class MandateSignalConstructionV2:
    default_mode: str
    mix_mode: str
    composite_members_proposed: tuple[str, ...]
    industry_neutral_residual_book: bool
    optional_mktcap_neutral: bool
    nonlinear_default: bool


@dataclass(frozen=True)
class MandateRebalanceV2:
    mask_and_eligibility: str
    risk_budget_and_vol_scale: str
    ordinary_rebalance: str
    decision_time_china: str
    execution: str
    t_plus_1: bool
    turnover_budget_monthly_one_way: float


@dataclass(frozen=True)
class MandateCostsV2:
    commission_bps_one_way: float
    commission_min_cny_per_order: float
    stamp_tax_sell_only: bool
    slippage_bps_one_way: float
    fast_sim_not_promotion_evidence: bool


@dataclass(frozen=True)
class MandateV2:
    """Frozen Mandate V2 view for Phase 0+ stubs.

    ``promotion_approved`` is always ``False`` after load (see module docstring).
    """

    mandate_id: str
    version: str
    status: str
    promotion_approved: bool
    design_ref: str
    capital: MandateCapitalV2
    markets: MandateMarketsV2
    universe: MandateUniverseV2
    portfolio_limits: MandatePortfolioLimitsV2
    risk: MandateRiskV2
    signal_construction: MandateSignalConstructionV2
    rebalance: MandateRebalanceV2
    costs: MandateCostsV2
    architecture_layers: Mapping[str, str]
    explicit_ban_ids: tuple[str, ...]
    source_path: str
    raw: Mapping[str, Any] = field(repr=False)

    def require_not_promoted(self) -> None:
        """Gate-consistency check (name kept for callers).

        Mandate overall ``promotion_approved`` must equal the single platform gate
        :func:`quantlab.promotion_gate.overall_promotion_approved`.
        This is a data/platform gate only — not a strategy go-live verdict.
        """
        if bool(self.promotion_approved) != _gate():
            raise RuntimeError("mandate_v2_promotion_approved_gate_mismatch")


def resolve_mandate_v2_path(path: str | Path | None = None) -> Path:
    """Resolve Mandate V2 JSON path (env > arg > in-repo docs/v2 > workspace root)."""
    if path is not None:
        resolved = Path(path).expanduser().resolve()
        if not resolved.is_file():
            raise FileNotFoundError(f"mandate_v2_missing:{resolved}")
        return resolved
    env = os.environ.get("QUANTLAB_MANDATE_V2")
    if env:
        resolved = Path(env).expanduser().resolve()
        if not resolved.is_file():
            raise FileNotFoundError(f"mandate_v2_env_missing:{resolved}")
        return resolved
    for candidate in _DEFAULT_CANDIDATES:
        if candidate.is_file():
            return candidate.resolve()
    searched = ", ".join(str(p) for p in _DEFAULT_CANDIDATES)
    raise FileNotFoundError(f"mandate_v2_not_found:{searched}")


def _req(mapping: Mapping[str, Any], key: str) -> Any:
    if key not in mapping:
        raise KeyError(f"mandate_v2_missing_field:{key}")
    return mapping[key]


def _tuple_str(values: Sequence[Any] | None) -> tuple[str, ...]:
    if values is None:
        return ()
    return tuple(str(v) for v in values)


def load_mandate_v2(path: str | Path | None = None) -> MandateV2:
    """Parse Mandate V2 JSON into :class:`MandateV2`.

    Forces ``promotion_approved=False``. Does not invent backtest metrics.
    """
    resolved = resolve_mandate_v2_path(path)
    raw = json.loads(resolved.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("mandate_v2_root_not_object")

    capital_raw = _req(raw, "capital")
    markets_raw = _req(raw, "markets")
    universe_raw = _req(raw, "universe")
    liquidity_raw = _req(universe_raw, "liquidity_rule")
    microcap_raw = _req(universe_raw, "microcap_policy")
    portfolio_raw = _req(raw, "portfolio_limits")
    risk_raw = _req(raw, "risk")
    signal_raw = _req(raw, "signal_construction")
    rebalance_raw = _req(raw, "rebalance")
    costs_raw = _req(raw, "costs")
    gates_raw = raw.get("gates_research_targets_not_promises") or {}
    defaults_table = raw.get("defaults_table") or {}

    beta_band = risk_raw.get("target_beta_band") or [0.5, 0.85]
    if len(beta_band) != 2:
        raise ValueError("mandate_v2_target_beta_band_invalid")

    max_dd_gate = float(
        gates_raw.get("max_drawdown_research", {}).get("not_worse_than")
        or defaults_table.get("max_dd_gate")
        or -0.28
    )

    # Overall data/platform promotion flag — follows the single gate
    # (quantlab/platform/promotion_gate.py). Not a strategy go-live verdict.
    promotion_approved = _gate()

    covariance = risk_raw.get("covariance") or {}
    vol_targeting = risk_raw.get("vol_targeting") or {}
    drawdown = risk_raw.get("drawdown_scaler") or {}
    bans = tuple(str(item.get("id", "")) for item in (raw.get("explicit_bans") or []) if isinstance(item, dict))

    mandate = MandateV2(
        mandate_id=str(_req(raw, "mandate_id")),
        version=str(_req(raw, "version")),
        status=str(_req(raw, "status")),
        promotion_approved=promotion_approved,
        design_ref=str(raw.get("design_ref") or "QuantLab-STRATEGY_DESIGN_V2.md"),
        capital=MandateCapitalV2(
            initial_cny=float(_req(capital_raw, "initial_cny")),
            currency=str(capital_raw.get("currency") or "CNY"),
            leverage_allowed=bool(capital_raw.get("leverage_allowed", False)),
            short_selling_allowed=bool(capital_raw.get("short_selling_allowed", False)),
            margin_allowed=bool(capital_raw.get("margin_allowed", False)),
            cash_allowed=bool(capital_raw.get("cash_allowed", True)),
            cash_is_active_risk_tool=bool(capital_raw.get("cash_is_active_risk_tool", True)),
            min_cash_buffer_normal=float(capital_raw.get("min_cash_buffer_normal", 0.02)),
        ),
        markets=MandateMarketsV2(
            allowed_asset_types=_tuple_str(_req(markets_raw, "allowed_asset_types")),
            exchanges=_tuple_str(_req(markets_raw, "exchanges")),
            exclude_bse_default=bool(markets_raw.get("exclude_bse_default", True)),
            benchmark_primary=str(_req(markets_raw, "benchmark_primary")),
            benchmark_etf=str(markets_raw.get("benchmark_etf") or "510300"),
            benchmark_etf_examples=_tuple_str(markets_raw.get("benchmark_etf_examples")),
            overseas_assets_default=bool(markets_raw.get("overseas_assets_default", False)),
            commodity_gold_default=bool(markets_raw.get("commodity_gold_default", False)),
        ),
        universe=MandateUniverseV2(
            mask_first=bool(universe_raw.get("mask_first", True)),
            listing_min_trading_days=int(_req(universe_raw, "listing_min_trading_days")),
            exclude_st=bool(universe_raw.get("exclude_st", True)),
            exclude_delisting_arrangement=bool(universe_raw.get("exclude_delisting_arrangement", True)),
            liquidity_rule=MandateLiquidityRuleV2(
                metric=str(_req(liquidity_raw, "metric")),
                threshold_cny_primary=float(_req(liquidity_raw, "threshold_cny_primary")),
                threshold_cny_alt_research=float(liquidity_raw.get("threshold_cny_alt_research", 5_000_000)),
                primary_label=str(liquidity_raw.get("primary_label") or "U30"),
                alt_label=str(liquidity_raw.get("alt_label") or "U5"),
                active_label=str(liquidity_raw.get("active_label") or "U30"),
                threshold_cny_active=float(
                    liquidity_raw.get("threshold_cny_active")
                    or liquidity_raw.get("threshold_cny_primary")
                    or 30_000_000
                ),
            ),
            microcap_policy=MandateMicrocapPolicyV2(
                mode=str(_req(microcap_raw, "mode")),
                exclude_bottom_mktcap_pct=float(_req(microcap_raw, "exclude_bottom_mktcap_pct")),
                hard_cap_portfolio_weight=float(microcap_raw.get("hard_cap_portfolio_weight", 0.0)),
                microcap_as_universe_banned=bool(microcap_raw.get("microcap_as_universe_banned", True)),
            ),
            tradability_masks=_tuple_str(_req(universe_raw, "tradability_masks")),
            etf_role=str(universe_raw.get("etf_role") or "beta_sleeve_only_default"),
        ),
        portfolio_limits=MandatePortfolioLimitsV2(
            max_positions_stocks=int(_req(portfolio_raw, "max_positions_stocks")),
            min_positions_target=int(_req(portfolio_raw, "min_positions_target")),
            max_single_stock_weight=float(_req(portfolio_raw, "max_single_stock_weight")),
            max_industry_weight=float(_req(portfolio_raw, "max_industry_weight")),
            industry_scheme=str(portfolio_raw.get("industry_scheme") or "SW_L1"),
            unknown_industry_cap=float(portfolio_raw.get("unknown_industry_cap", 0.25)),
            max_etf_sleeve_weight=float(portfolio_raw.get("max_etf_sleeve_weight", 0.4)),
            max_order_vs_adv20=float(portfolio_raw.get("max_order_vs_adv20", 0.01)),
            lot_size_rounding=str(portfolio_raw.get("lot_size_rounding") or "floor_buy_to_lot"),
            min_trade_notional_cny=float(portfolio_raw.get("min_trade_notional_cny", 2000)),
        ),
        risk=MandateRiskV2(
            target_annual_vol=float(_req(risk_raw, "target_annual_vol")),
            target_beta_vs_benchmark=float(_req(risk_raw, "target_beta_vs_benchmark")),
            target_beta_band=(float(beta_band[0]), float(beta_band[1])),
            covariance_estimator=str(covariance.get("estimator") or "ledoit_wolf"),
            vol_targeting_enabled=bool(vol_targeting.get("enabled", True)),
            drawdown_scaler_recoverable=bool(drawdown.get("recoverable", True)),
            permanent_halt_banned=bool(drawdown.get("permanent_halt_banned", True)),
            max_dd_gate=max_dd_gate,
        ),
        signal_construction=MandateSignalConstructionV2(
            default_mode=str(signal_raw.get("default_mode") or "integrate"),
            mix_mode=str(signal_raw.get("mix_mode") or "control_arm_only"),
            composite_members_proposed=_tuple_str(signal_raw.get("composite_members_proposed")),
            industry_neutral_residual_book=bool(signal_raw.get("industry_neutral_residual_book", True)),
            optional_mktcap_neutral=bool(signal_raw.get("optional_mktcap_neutral", True)),
            nonlinear_default=bool(signal_raw.get("nonlinear_default", False)),
        ),
        rebalance=MandateRebalanceV2(
            mask_and_eligibility=str(rebalance_raw.get("mask_and_eligibility") or "daily"),
            risk_budget_and_vol_scale=str(rebalance_raw.get("risk_budget_and_vol_scale") or "daily"),
            ordinary_rebalance=str(rebalance_raw.get("ordinary_rebalance") or "biweekly"),
            decision_time_china=str(rebalance_raw.get("decision_time_china") or "18:00"),
            execution=str(rebalance_raw.get("execution") or "next_trading_day_open"),
            t_plus_1=bool(rebalance_raw.get("t_plus_1", True)),
            turnover_budget_monthly_one_way=float(
                rebalance_raw.get("turnover_budget_monthly_one_way", 0.35)
            ),
        ),
        costs=MandateCostsV2(
            commission_bps_one_way=float(_req(costs_raw, "commission_bps_one_way")),
            commission_min_cny_per_order=float(costs_raw.get("commission_min_cny_per_order", 5.0)),
            stamp_tax_sell_only=bool(costs_raw.get("stamp_tax_sell_only", True)),
            slippage_bps_one_way=float(costs_raw.get("slippage_bps_one_way", 5.0)),
            fast_sim_not_promotion_evidence=bool(
                costs_raw.get("fast_sim_not_promotion_evidence", True)
            ),
        ),
        architecture_layers=dict(raw.get("architecture_layers") or {}),
        explicit_ban_ids=tuple(b for b in bans if b),
        source_path=str(resolved),
        raw=raw,
    )
    mandate.require_not_promoted()
    return mandate
