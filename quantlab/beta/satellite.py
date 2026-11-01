"""Small-cap / wide-basket satellite sleeve (research menu item).

Flag ``smallcap_satellite`` defaults OFF. When ON, Beta may split the *existing*
ETF sleeve budget (already clipped by Mandate ``max_etf``) between core 510300
and a small-cap ETF satellite using contribution weights.

Data: free research panel ``data/etf/universe/equity_etf_daily.parquet``
(default candidate ``sh512100`` CSI1000; fallback ``sh510500`` / ``sz159922``).
Does **not** invent OHLCV. Does **not** raise ``max_etf`` or flip promotion.
Primary 510300 panel remains ``load_etf_510300()`` (Tushare fund_daily is
candidate-only — see ``docs/v2/TUSHARE_CANDIDATE_LOADERS.md``).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Mapping, Sequence

from quantlab.config import ROOT

DEFAULT_EQUITY_ETF_UNIVERSE = ROOT / "data" / "etf" / "universe" / "equity_etf_daily.parquet"

# Mandate examples: 510500 / 512100; 小盘对照臂 → prefer CSI1000 ETF
SATELLITE_CODE_PREFERENCE: tuple[str, ...] = ("sh512100", "sh510500", "sz159922")

# Research: satellite share of ETF budget (core stays primary)
DEFAULT_MAX_SATELLITE_FRAC = 0.25


@dataclass(frozen=True)
class SatelliteSeries:
    """Research OHLC-close series for one satellite ETF (no fabricated bars)."""

    code: str
    asset: str
    path: str
    n_bars: int
    date_min: date | None
    date_max: date | None
    sessions: tuple[date, ...]
    closes: tuple[float, ...]
    data_ready: bool
    promotion_approved: bool = False
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.promotion_approved:
            raise ValueError("satellite_promotion_approved_must_be_false")


@dataclass(frozen=True)
class SatelliteContributionSplit:
    """Contribution-weighted split of an ETF budget (sums to etf_total)."""

    etf_total: float
    core_weight: float
    satellite_weight: float
    contribution_weight_core: float
    contribution_weight_satellite: float
    core_unit_beta: float
    satellite_unit_beta: float
    max_satellite_frac: float
    mode: str  # equal_beta_contribution_capped
    promotion_approved: bool = False

    def __post_init__(self) -> None:
        if self.promotion_approved:
            raise ValueError("satellite_split_promotion_approved_must_be_false")
        if abs(self.core_weight + self.satellite_weight - self.etf_total) > 1e-6:
            raise ValueError("satellite_split_weights_must_sum_to_etf_total")


def resolve_satellite_code(
    preferred: str | None = None,
    *,
    universe_path: str | Path | None = None,
) -> tuple[str | None, tuple[str, ...]]:
    """Pick first available satellite code from preference list (or preferred)."""
    import pandas as pd

    path = Path(universe_path) if universe_path else DEFAULT_EQUITY_ETF_UNIVERSE
    notes: list[str] = []
    if not path.is_file():
        return None, (f"equity_etf_universe_missing:{path}",)

    codes_avail = set(pd.read_parquet(path, columns=["code"])["code"].astype(str).unique())
    order: list[str] = []
    if preferred:
        order.append(str(preferred))
    for c in SATELLITE_CODE_PREFERENCE:
        if c not in order:
            order.append(c)
    for c in order:
        if c in codes_avail:
            notes.append(f"satellite_code_resolved={c}")
            return c, tuple(notes)
    return None, (f"satellite_codes_unavailable:{','.join(order)}",)


def load_satellite_series(
    code: str,
    session: date,
    *,
    universe_path: str | Path | None = None,
) -> SatelliteSeries:
    """Load satellite closes ≤ session from equity ETF universe (research)."""
    import pandas as pd

    path = Path(universe_path) if universe_path else DEFAULT_EQUITY_ETF_UNIVERSE
    if not path.is_file():
        return SatelliteSeries(
            code=code,
            asset="",
            path=str(path),
            n_bars=0,
            date_min=None,
            date_max=None,
            sessions=(),
            closes=(),
            data_ready=False,
            promotion_approved=False,
            notes=(f"equity_etf_universe_missing:{path}", "TODO(Data): land satellite ETF panel"),
        )

    frame = pd.read_parquet(path)
    if "code" not in frame.columns or "date" not in frame.columns:
        return SatelliteSeries(
            code=code,
            asset="",
            path=str(path.resolve()),
            n_bars=0,
            date_min=None,
            date_max=None,
            sessions=(),
            closes=(),
            data_ready=False,
            promotion_approved=False,
            notes=("equity_etf_universe_schema_invalid",),
        )

    close_col = "close_raw" if "close_raw" in frame.columns else (
        "close" if "close" in frame.columns else None
    )
    if close_col is None:
        return SatelliteSeries(
            code=code,
            asset="",
            path=str(path.resolve()),
            n_bars=0,
            date_min=None,
            date_max=None,
            sessions=(),
            closes=(),
            data_ready=False,
            promotion_approved=False,
            notes=("equity_etf_universe_missing_close",),
        )

    sub = frame[frame["code"].astype(str) == str(code)].copy()
    if sub.empty:
        return SatelliteSeries(
            code=code,
            asset="",
            path=str(path.resolve()),
            n_bars=0,
            date_min=None,
            date_max=None,
            sessions=(),
            closes=(),
            data_ready=False,
            promotion_approved=False,
            notes=(f"satellite_code_empty:{code}",),
        )

    sub["_session"] = pd.to_datetime(sub["date"]).dt.normalize()
    hi = pd.Timestamp(session)
    sub = sub[sub["_session"] <= hi].sort_values("_session")
    asset = str(sub["asset"].iloc[0]) if "asset" in sub.columns and len(sub) else ""
    sessions = tuple(pd.Timestamp(ts).date() for ts in sub["_session"].tolist())
    closes = tuple(float(c) for c in sub[close_col].tolist())
    date_min = sessions[0] if sessions else None
    date_max = sessions[-1] if sessions else None
    ready = len(closes) >= 21 and date_max is not None and date_max >= session
    # Allow ready if last bar is on/before session with enough history (session may be non-trading)
    if len(closes) >= 21 and date_max is not None:
        ready = True
    notes = [
        f"source=data/etf/universe/equity_etf_daily.parquet",
        f"close_col={close_col}",
        f"n_bars_to_session={len(closes)}",
        "promotion_approved=false",
        "not_a_literal_50_name_basket:csi_etf_proxy",
    ]
    if not ready:
        notes.append("TODO(Data): insufficient satellite history")
    return SatelliteSeries(
        code=code,
        asset=asset,
        path=str(path.resolve()),
        n_bars=len(closes),
        date_min=date_min,
        date_max=date_max,
        sessions=sessions,
        closes=closes,
        data_ready=ready,
        promotion_approved=False,
        notes=tuple(notes),
    )


def contribution_weighted_split(
    etf_total: float,
    core_unit_beta: float,
    satellite_unit_beta: float,
    *,
    max_satellite_frac: float = DEFAULT_MAX_SATELLITE_FRAC,
) -> SatelliteContributionSplit:
    """Split ETF budget by equal-β-contribution weights; cap satellite share.

    ``w_i ∝ 1 / |unit_beta_i|`` so each sleeve contributes similar β if uncapped,
    then satellite share is capped at ``max_satellite_frac`` (core remains primary).
    Does not change Mandate ``max_etf`` — ``etf_total`` must already be clipped.
    """
    etf_total = max(0.0, float(etf_total))
    bc = abs(float(core_unit_beta))
    bs = abs(float(satellite_unit_beta))
    max_frac = min(1.0, max(0.0, float(max_satellite_frac)))

    if etf_total <= 1e-15:
        return SatelliteContributionSplit(
            etf_total=0.0,
            core_weight=0.0,
            satellite_weight=0.0,
            contribution_weight_core=1.0,
            contribution_weight_satellite=0.0,
            core_unit_beta=bc,
            satellite_unit_beta=bs,
            max_satellite_frac=max_frac,
            mode="equal_beta_contribution_capped",
            promotion_approved=False,
        )

    raw_c = (1.0 / bc) if bc > 1e-12 else 0.0
    raw_s = (1.0 / bs) if bs > 1e-12 else 0.0
    denom = raw_c + raw_s
    if denom <= 1e-15:
        share_s = 0.0
        share_c = 1.0
    else:
        share_s = raw_s / denom
        share_s = min(share_s, max_frac)
        share_c = 1.0 - share_s

    core_w = round(etf_total * share_c, 6)
    sat_w = round(etf_total - core_w, 6)
    return SatelliteContributionSplit(
        etf_total=round(etf_total, 6),
        core_weight=core_w,
        satellite_weight=sat_w,
        contribution_weight_core=round(share_c, 6),
        contribution_weight_satellite=round(share_s, 6),
        core_unit_beta=bc,
        satellite_unit_beta=bs,
        max_satellite_frac=max_frac,
        mode="equal_beta_contribution_capped",
        promotion_approved=False,
    )


def satellite_menu_descriptor(
    *,
    smallcap_satellite: bool,
    split: SatelliteContributionSplit | None,
    series: SatelliteSeries | None,
    core_code: str = "sh.510300",
    bond_overlay: BondRiskParityOverlaySpec | None = None,
    config: Mapping[str, object] | None = None,
) -> Mapping[str, object]:
    """Strategy compare-arm surface for the β/style sleeve menu.

    Always lists raise-CAGR candidates (wide-basket / M2 / ETF proxies) even when
    ``smallcap_satellite`` is OFF — they remain menu items, not mainline.
    """
    cfg = config or load_compare_arms_config()
    return {
        "smallcap_satellite": bool(smallcap_satellite),
        "default_off": True,
        "core": {
            "code": core_code,
            "role": "main_beta_sleeve",
            "contribution_weight": None if split is None else split.contribution_weight_core,
            "weight": None if split is None else split.core_weight,
        },
        "satellite": {
            "enabled": bool(smallcap_satellite),
            "code": None if series is None else series.code,
            "asset": None if series is None else series.asset,
            "role": "smallcap_style_satellite",
            "proxy_note": "CSI1000/500 ETF proxy — not a literal 50-name stock basket",
            "data_ready": False if series is None else series.data_ready,
            "contribution_weight": None if split is None else split.contribution_weight_satellite,
            "weight": None if split is None else split.satellite_weight,
            "unit_beta": None if split is None else split.satellite_unit_beta,
        },
        "raise_cagr_candidates": list(raise_cagr_menu_candidates(cfg)),
        "etf_proxy_compare_arms": list(etf_proxy_compare_arms(cfg)),
        "stock_basket_arms": [s.as_dict() for s in stock_basket_specs(cfg)],
        "stock_basket_hooks": describe_stock_basket_hooks(),
        "bond_risk_parity_overlay": None if bond_overlay is None else bond_overlay.as_dict(),
        "b6": cfg.get("b6_strategy_wiring"),
        "split_mode": None if split is None else split.mode,
        "max_satellite_frac": None if split is None else split.max_satellite_frac,
        "max_etf_raised": False,
        "promotion_approved": False,
        "compare_arms": (
            "flag_off_core_only_510300",
            "flag_on_etf_proxy_512100",
            "flag_on_etf_proxy_510500",
            "flag_on_wide_basket_50_tiny_sleeve",
            "flag_on_m2_control_tiny_sleeve",
            "flag_on_satellite_plus_511260_overlay",
        ),
        "config_path": cfg.get("config_path"),
    }


# ---------------------------------------------------------------------------
# Compare-arm catalog / stock basket / 511260 overlay (ESSENCE B2/B3/B5)
# ---------------------------------------------------------------------------

COMPARE_ARMS_CONFIG_PATH = Path(__file__).resolve().parent / "configs" / "compare_arms_v1.json"


def load_compare_arms_config(path: str | Path | None = None) -> Mapping[str, object]:
    """Load research compare-arm JSON (promotion_approved forced false)."""
    import json

    cfg_path = Path(path) if path else COMPARE_ARMS_CONFIG_PATH
    raw = json.loads(cfg_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("compare_arms_config_not_object")
    raw = dict(raw)
    raw["promotion_approved"] = False
    raw["config_path"] = str(cfg_path.resolve())
    return raw


def raise_cagr_menu_candidates(config: Mapping[str, object] | None = None) -> tuple[Mapping[str, object], ...]:
    """Arms flagged as raise-CAGR candidates (listed even when switches OFF)."""
    cfg = config or load_compare_arms_config()
    arms = []
    for arm in cfg.get("arms") or []:
        if not isinstance(arm, dict):
            continue
        if arm.get("raise_cagr_candidate"):
            arms.append(
                {
                    "id": arm.get("id"),
                    "kind": arm.get("kind"),
                    "code": arm.get("code"),
                    "role": arm.get("role"),
                    "enabled_by_default": bool(arm.get("enabled_by_default", False)),
                    "suggested_max_sleeve_weight": arm.get("suggested_max_sleeve_weight"),
                    "suggested_max_frac_of_etf_budget": arm.get("suggested_max_frac_of_etf_budget"),
                    "essence_rank": arm.get("essence_rank"),
                    "mdd_ledger_note": arm.get("mdd_ledger_note"),
                    "note": arm.get("note"),
                    "menu_status": "listed_default_off",
                }
            )
    return tuple(arms)


def etf_proxy_compare_arms(config: Mapping[str, object] | None = None) -> tuple[Mapping[str, object], ...]:
    """Side-by-side ETF proxies 512100 and 510500."""
    cfg = config or load_compare_arms_config()
    out = []
    for arm in cfg.get("arms") or []:
        if isinstance(arm, dict) and arm.get("kind") == "etf_satellite":
            out.append(
                {
                    "id": arm.get("id"),
                    "code": arm.get("code"),
                    "asset": arm.get("asset"),
                    "compare_with": arm.get("compare_with"),
                    "data_path": arm.get("data_path"),
                    "enabled_by_default": False,
                    "requires_flag": "smallcap_satellite",
                }
            )
    return tuple(out)


@dataclass(frozen=True)
class StockBasketSatelliteSpec:
    """Interface to ``quantlab.smallcap.universe.pool_on`` / ``select`` (no returns)."""

    arm_id: str
    holdings: int
    pool_on_kwargs: Mapping[str, object]
    select_kwargs: Mapping[str, object]
    suggested_max_sleeve_weight: float
    financial_tier: bool
    prereg: str | None
    module: str = "quantlab.smallcap.universe"
    promotion_approved: bool = False
    note: str = ""

    def __post_init__(self) -> None:
        if self.promotion_approved:
            raise ValueError("stock_basket_promotion_approved_must_be_false")

    def as_dict(self) -> Mapping[str, object]:
        return {
            "arm_id": self.arm_id,
            "module": self.module,
            "hooks": {
                "pool_on": dict(self.pool_on_kwargs),
                "select": dict(self.select_kwargs),
                "financial_tier": self.financial_tier,
            },
            "holdings": self.holdings,
            "suggested_max_sleeve_weight": self.suggested_max_sleeve_weight,
            "prereg": self.prereg,
            "promotion_approved": False,
            "returns_invented": False,
            "note": self.note
            or (
                "Strategy/Beta call pool_on→select for membership only; "
                "do not invent OHLCV; tiny sleeve given MDD budget"
            ),
        }


def stock_basket_specs(config: Mapping[str, object] | None = None) -> tuple[StockBasketSatelliteSpec, ...]:
    """Wide-basket + M2 specs from compare-arm config."""
    cfg = config or load_compare_arms_config()
    out: list[StockBasketSatelliteSpec] = []
    for arm in cfg.get("arms") or []:
        if not isinstance(arm, dict) or arm.get("kind") != "stock_basket":
            continue
        pool = arm.get("pool") or {}
        pool_on = dict(pool.get("pool_on") or {})
        select_kw = dict(pool.get("select") or {})
        # Map absolute ranks into universe constants documentation only
        out.append(
            StockBasketSatelliteSpec(
                arm_id=str(arm.get("id")),
                holdings=int(arm.get("holdings") or select_kw.get("holdings") or 50),
                pool_on_kwargs=pool_on,
                select_kwargs=select_kw,
                suggested_max_sleeve_weight=float(arm.get("suggested_max_sleeve_weight") or 0.05),
                financial_tier=bool(pool.get("financial_tier", False)),
                prereg=str(pool["prereg"]) if pool.get("prereg") else None,
                module=str(pool.get("module") or "quantlab.smallcap.universe"),
                promotion_approved=False,
                note=str(arm.get("note") or ""),
            )
        )
    return tuple(out)


def describe_stock_basket_hooks() -> Mapping[str, object]:
    """Static Strategy-facing hooks into smallcap.universe (no panel load)."""
    from quantlab.smallcap import universe as uni

    return {
        "module": "quantlab.smallcap.universe",
        "pool_on": {
            "callable": "pool_on",
            "signature": "pool_on(day, features, kind, band='absolute', exclude_st=False, min_history=...)",
            "wide_basket_example": {
                "kind": "adv",
                "band": "absolute",
                "rank_window": [uni.RANK_START, uni.RANK_END],
                "min_adv": uni.MIN_ADV,
            },
            "m2_example": {
                "kind": "adv",
                "band": "relative",
                "exclude_st": True,
                "min_history": 252,
            },
        },
        "select": {
            "callable": "select",
            "signature": "select(ordered, industries, current, holdings=50, buffer=100, slots=15)",
            "holdings": uni.HOLDINGS,
            "buffer": uni.BUFFER,
            "industry_slots": uni.INDUSTRY_SLOTS,
            "gross": uni.GROSS,
        },
        "financial_tier": "financial_tier(codes, net_profit, pb)",
        "promotion_approved": False,
        "backtest": "not_run_here — Strategy paper after P0; Beta only exposes interface",
    }


@dataclass(frozen=True)
class BondRiskParityOverlaySpec:
    """Optional 511260 risk-parity overlay when satellite ON (default OFF)."""

    enabled: bool = False
    code: str = "sh511260"
    requires_satellite_on: bool = True
    data_ready: bool = False
    data_path: str | None = None
    promotion_approved: bool = False
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.promotion_approved:
            raise ValueError("bond_overlay_promotion_approved_must_be_false")

    def as_dict(self) -> Mapping[str, object]:
        return {
            "enabled": self.enabled,
            "code": self.code,
            "requires_satellite_on": self.requires_satellite_on,
            "data_ready": self.data_ready,
            "data_path": self.data_path,
            "mode": "risk_parity_vs_satellite_leg",
            "default": False,
            "promotion_approved": False,
            "notes": list(self.notes),
        }


def probe_bond_511260_data() -> BondRiskParityOverlaySpec:
    """Probe known paths for 511260 — never invent bars."""
    import pandas as pd

    candidates = [
        ROOT / "data" / "smallcap_assets" / "etf_bars.parquet",
        ROOT / "data" / "etf" / "universe" / "equity_etf_daily.parquet",
    ]
    notes: list[str] = ["bond_risk_parity_overlay_default_off", "cut_dd_research_only"]
    for path in candidates:
        if not path.is_file():
            notes.append(f"missing:{path}")
            continue
        try:
            frame = pd.read_parquet(path)
        except Exception as exc:  # noqa: BLE001
            notes.append(f"unreadable:{path.name}:{type(exc).__name__}")
            continue
        code_col = "code" if "code" in frame.columns else (
            "instrument_id" if "instrument_id" in frame.columns else None
        )
        if code_col is None:
            notes.append(f"no_code_col:{path.name}")
            continue
        codes = set(frame[code_col].astype(str).unique())
        hits = [c for c in codes if "511260" in c.replace(".", "").replace("sh", "").replace("SH", "") or c in {"sh511260", "sh.511260", "511260"}]
        # also direct match variants
        for variant in ("sh511260", "sh.511260", "511260", "SH511260"):
            if variant in codes:
                hits.append(variant)
        if hits:
            return BondRiskParityOverlaySpec(
                enabled=False,
                code=str(hits[0]),
                data_ready=True,
                data_path=str(path.resolve()),
                promotion_approved=False,
                notes=tuple(notes + [f"found:{hits[0]}", f"path:{path}"]),
            )
        notes.append(f"511260_not_in:{path.name}")
    return BondRiskParityOverlaySpec(
        enabled=False,
        code="sh511260",
        data_ready=False,
        data_path=None,
        promotion_approved=False,
        notes=tuple(notes + ["TODO(Data): land 511260 bars for overlay"]),
    )


def build_bond_overlay_spec(*, enabled: bool, satellite_on: bool) -> BondRiskParityOverlaySpec:
    """Research overlay switch — only meaningful when satellite ON; never invents data."""
    base = probe_bond_511260_data()
    notes = list(base.notes)
    if enabled and not satellite_on:
        notes.append("overlay_ignored_satellite_off")
        enabled = False
    if enabled and not base.data_ready:
        notes.append("overlay_on_but_data_missing_no_weights_applied")
    return BondRiskParityOverlaySpec(
        enabled=bool(enabled) and bool(satellite_on) and bool(base.data_ready),
        code=base.code,
        requires_satellite_on=True,
        data_ready=base.data_ready,
        data_path=base.data_path,
        promotion_approved=False,
        notes=tuple(notes),
    )
