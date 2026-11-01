"""L1 Beta sleeve around CSI 300 ETF 510300 (Phase 0 interface).

Frozen Data contracts (:mod:`quantlab.v2_schemas`):
  - instruments row: :class:`EquityEtfInstrumentRow` for ``sh.510300``
  - panel: :class:`Etf510300Bar` at ``panels/sh.510300.parquet``
  - research index: :class:`BenchmarkIndexBar` / D0 ``benchmark.parquet`` (sh.000300)

Prototype / VolTarget providers land Mandate vol-target (16%) and β budget
(0.70) as **research** weights. ``promotion_approved`` is always False.
Do not invent ETF bars or performance claims (no Sharpe/PnL).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Mapping, Protocol, Sequence

from quantlab.mandate_v2 import MandateV2
from quantlab.v2_schemas import (
    ETF_510300_BARE_CODE,
    ETF_510300_INSTRUMENT_COLUMN_SPEC,
    ETF_510300_INSTRUMENT_ID,
    ETF_510300_PANEL_COLUMN_SPEC,
    INDEX_CSI300_INSTRUMENT_ID,
    BenchmarkIndexBar,
    EquityEtfInstrumentRow,
    Etf510300Bar,
)

BETA_SLEEVE_ETF_DEFAULT = ETF_510300_BARE_CODE

# Research lookback for trailing vol / β (trading days). Rebalance-friendly.
_DEFAULT_LOOKBACK_SESSIONS = 60
_MIN_RETURN_OBS = 20
_TRADING_DAYS_PER_YEAR = 252.0


@dataclass(frozen=True)
class BetaSleevePlan:
    """Target sleeve weights for one decision session (typed stub output)."""

    session: date
    benchmark_etf: str
    benchmark_etf_instrument_id: str
    benchmark_index_id: str
    target_annual_vol: float
    target_beta_vs_benchmark: float
    target_beta_band: tuple[float, float]
    max_etf_sleeve_weight: float
    cash_weight: float | None
    etf_sleeve_weight: float | None
    residual_book_weight_cap: float | None
    index_bars_available: bool = False
    etf_panel_available: bool = False
    promotion_approved: bool = False
    data_ready: bool = False
    # Mandate β-gap contract (research; Beta never raises max_etf)
    unit_beta: float | None = None
    implied_sleeve_beta: float | None = None
    beta_gap_to_mandate: float | None = None
    residual_beta_budget_for_strategy: float | None = None
    implied_beta_in_band: bool | None = None
    # Drawdown / risk-off scaler (research-only; 510300 peak-to-trough)
    etf_drawdown: float | None = None
    drawdown_tier: str | None = None
    drawdown_scale_applied: bool = False
    etf_weight_pre_drawdown: float | None = None
    effective_target_annual_vol: float | None = None
    # Portfolio β decomposition (research; does not change Mandate / max_etf)
    # Long industry-neutral residual often carries ~unit market β≈1; use that
    # default to size residual weight toward portfolio β≈target without raising max_etf.
    assumed_residual_unit_beta: float | None = None
    max_sleeve_beta_at_max_etf: float | None = None
    beta_gap_is_structural: bool | None = None
    residual_weight_to_hit_target_beta: float | None = None
    implied_portfolio_beta_at_residual_fill: float | None = None
    # Small-cap satellite menu (research; default OFF — does not raise max_etf)
    smallcap_satellite: bool = False
    satellite_code: str | None = None
    satellite_asset: str | None = None
    core_etf_weight: float | None = None
    satellite_etf_weight: float | None = None
    contribution_weight_core: float | None = None
    contribution_weight_satellite: float | None = None
    satellite_unit_beta: float | None = None
    satellite_data_ready: bool = False
    todos: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.promotion_approved:
            raise ValueError("beta_sleeve_promotion_approved_must_be_false")
        if self.etf_sleeve_weight is not None and self.etf_sleeve_weight > self.max_etf_sleeve_weight + 1e-12:
            raise ValueError("etf_sleeve_weight_exceeds_mandate_cap")
        if self.smallcap_satellite and self.core_etf_weight is not None and self.satellite_etf_weight is not None:
            combo = float(self.core_etf_weight) + float(self.satellite_etf_weight)
            if self.etf_sleeve_weight is not None and abs(combo - float(self.etf_sleeve_weight)) > 1e-5:
                raise ValueError("satellite_core_weights_must_sum_to_etf_sleeve_weight")
            if combo > self.max_etf_sleeve_weight + 1e-12:
                raise ValueError("core_plus_satellite_exceeds_mandate_max_etf")


class BetaSleeveProvider(Protocol):
    def plan(
        self,
        session: date,
        *,
        realized_vol: float | None = None,
        portfolio_beta: float | None = None,
    ) -> BetaSleevePlan: ...

    def load_etf_bars(self, start: date, end: date) -> tuple[Etf510300Bar, ...]: ...

    def load_etf_instrument(self) -> EquityEtfInstrumentRow: ...

    def load_index_bars(self, start: date, end: date) -> tuple[BenchmarkIndexBar, ...]: ...


def _annualized_realized_vol(daily_returns: Sequence[float], *, min_obs: int = _MIN_RETURN_OBS) -> float | None:
    """Annualize sample std of daily simple returns. Counts only — no Sharpe."""
    import math

    xs = [float(x) for x in daily_returns if x == x]  # drop NaN
    if len(xs) < min_obs:
        return None
    mean = sum(xs) / len(xs)
    var = sum((x - mean) ** 2 for x in xs) / max(1, len(xs) - 1)
    daily_std = math.sqrt(var)
    if daily_std <= 0.0:
        return None
    return daily_std * math.sqrt(_TRADING_DAYS_PER_YEAR)


def _trailing_beta(
    etf_returns: Sequence[float],
    index_returns: Sequence[float],
    *,
    min_obs: int = _MIN_RETURN_OBS,
) -> float | None:
    """OLS beta of ETF daily returns vs index (aligned sequences, equal length)."""
    n = min(len(etf_returns), len(index_returns))
    if n < min_obs:
        return None
    ys = [float(etf_returns[i]) for i in range(n)]
    xs = [float(index_returns[i]) for i in range(n)]
    # drop paired NaNs
    pairs = [(x, y) for x, y in zip(xs, ys) if x == x and y == y]
    if len(pairs) < min_obs:
        return None
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    var_x = sum((x - mean_x) ** 2 for x in xs)
    if var_x <= 1e-18:
        return None
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    return cov / var_x


def _panel_close_series_to_session(panel, session: date):
    """Return (sessions_sorted, closes) for rows with event_time.date <= session."""
    import pandas as pd

    frame = panel.copy()
    if "event_time" in frame.columns:
        frame["_session"] = pd.to_datetime(frame["event_time"]).dt.normalize()
    elif isinstance(frame.index, pd.DatetimeIndex):
        frame = frame.assign(_session=pd.Series(frame.index.normalize(), index=frame.index))
    else:
        raise ValueError("etf_510300_panel_missing_event_time")
    hi = pd.Timestamp(session)
    frame = frame[frame["_session"] <= hi].sort_values("_session")
    if frame.empty:
        return [], []
    sessions = [pd.Timestamp(ts).date() for ts in frame["_session"].tolist()]
    closes = [float(c) for c in frame["close"].tolist()]
    return sessions, closes


def _simple_returns(closes: Sequence[float]) -> list[float]:
    out: list[float] = []
    for i in range(1, len(closes)):
        prev = closes[i - 1]
        if prev is None or prev != prev or prev == 0.0:
            out.append(float("nan"))
        else:
            out.append((closes[i] / prev) - 1.0)
    return out


def scale_etf_sleeve_weight(
    *,
    target_annual_vol: float,
    target_beta: float,
    max_etf_sleeve_weight: float,
    realized_vol: float | None,
    unit_beta: float | None,
    vol_targeting_enabled: bool,
    fallback_etf_weight: float,
) -> tuple[float, tuple[str, ...]]:
    """Map unit-ETF vol/β into Mandate-capped sleeve weight (research formula).

    Interprets ``realized_vol`` / ``unit_beta`` as metrics of a **100% ETF**
    exposure (not the already-weighted portfolio). Desired weight:

      w_vol  = target_annual_vol / realized_vol   (if vol targeting on)
      w_beta = target_beta / unit_beta
      w      = min(w_vol, w_beta, max_etf_sleeve_weight)  (available legs only)

    Falls back to ``fallback_etf_weight`` (clipped) when neither leg is usable.
    """
    notes: list[str] = []
    candidates: list[float] = []

    if vol_targeting_enabled and realized_vol is not None and realized_vol > 1e-12:
        w_vol = float(target_annual_vol) / float(realized_vol)
        candidates.append(w_vol)
        notes.append(f"w_vol={w_vol:.6f}")
    elif vol_targeting_enabled:
        notes.append("w_vol_unavailable")
    else:
        notes.append("vol_targeting_disabled")

    if unit_beta is not None and abs(unit_beta) > 1e-12:
        w_beta = float(target_beta) / float(unit_beta)
        candidates.append(w_beta)
        notes.append(f"w_beta={w_beta:.6f}")
    else:
        notes.append("w_beta_unavailable")

    cap = float(max_etf_sleeve_weight)
    if candidates:
        raw = min(candidates)
        etf_w = max(0.0, min(raw, cap))
        notes.append(f"etf_w_raw={raw:.6f}")
        notes.append(f"etf_w_clipped={etf_w:.6f}")
    else:
        etf_w = min(float(fallback_etf_weight), cap)
        notes.append(f"etf_w_fallback={etf_w:.6f}")

    return etf_w, tuple(notes)


def _current_drawdown_from_peak(closes: Sequence[float]) -> float | None:
    """Peak-to-trough drawdown of last close vs running peak (unreset)."""
    xs = [float(c) for c in closes if c is not None and c == c]
    if len(xs) < 2:
        return None
    peak = xs[0]
    for c in xs:
        if c > peak:
            peak = c
    if peak <= 0.0:
        return None
    return max(0.0, (peak - xs[-1]) / peak)


def _mandate_drawdown_tier(drawdown: float | None, mandate: MandateV2) -> tuple[str, float, float | None, tuple[str, ...]]:
    """Map ETF drawdown to Mandate drawdown_scaler tier.

    Returns ``(tier, effective_target_vol_mult, risk_asset_cap_or_None, notes)``.
    L4_extreme has no numeric cap in Mandate JSON (human confirm); research uses
    a conservative cap below L3 (0.15) and never auto-promotes or invents fills.
    """
    notes: list[str] = []
    target_vol = float(mandate.risk.target_annual_vol)
    if drawdown is None:
        return "none", 1.0, None, ("drawdown_unavailable",)

    raw = (mandate.raw.get("risk") or {}).get("drawdown_scaler") or {}
    enabled = bool(raw.get("enabled", True))
    notes.append(f"drawdown_scaler_enabled={enabled}")
    notes.append(f"drawdown_ref={raw.get('reference') or 'peak_nav_unreset'}")
    if not enabled:
        return "none", 1.0, None, tuple(notes + ["drawdown_scaler_disabled"])

    # Defaults aligned to Mandate V2 JSON levels
    levels = list(raw.get("levels") or [])
    # Sort descending by threshold so first match is highest tier
    parsed: list[tuple[float, str, str]] = []
    for lv in levels:
        try:
            thr = float(lv.get("drawdown_gte"))
            label = str(lv.get("label") or "")
            action = str(lv.get("action") or "")
            parsed.append((thr, label, action))
        except (TypeError, ValueError):
            continue
    if not parsed:
        parsed = [
            (0.25, "L4_extreme", "cancel_buys_continue_exits_require_human_confirm_to_add_risk"),
            (0.22, "L3", "cap_risk_asset_weight_at_0.30_and_block_new_risk"),
            (0.18, "L2", "cap_risk_asset_weight_at_0.60"),
            (0.12, "L1", "multiply_effective_target_vol_by_0.75"),
        ]
    parsed.sort(key=lambda x: x[0], reverse=True)

    tier = "none"
    vol_mult = 1.0
    risk_cap: float | None = None
    matched_action = ""
    for thr, label, action in parsed:
        if drawdown + 1e-15 >= thr:
            tier = label or "matched"
            matched_action = action
            break

    if tier == "none":
        notes.append("drawdown_tier=none")
        return tier, vol_mult, risk_cap, tuple(notes)

    notes.append(f"drawdown_tier={tier}")
    notes.append(f"drawdown_action={matched_action}")

    # L1+ : Mandate multiplies effective target vol by 0.75
    if "multiply_effective_target_vol_by_0.75" in matched_action or tier in {"L1", "L2", "L3", "L4_extreme"}:
        # Higher tiers inherit L1 vol mult (nested stress)
        if drawdown + 1e-15 >= 0.12:
            vol_mult = 0.75
            notes.append("effective_target_vol_mult=0.75")

    # Caps from L2/L3; L4 research conservative cap (Mandate: human confirm, no auto add-risk)
    if drawdown + 1e-15 >= 0.25 or tier == "L4_extreme":
        risk_cap = 0.15
        notes.append("research_L4_risk_asset_cap=0.15")
        notes.append("L4_human_confirm_not_automated")
    elif drawdown + 1e-15 >= 0.22 or tier == "L3":
        risk_cap = 0.30
        notes.append("risk_asset_cap=0.30")
    elif drawdown + 1e-15 >= 0.18 or tier == "L2":
        risk_cap = 0.60
        notes.append("risk_asset_cap=0.60")

    _ = target_vol  # reserved for callers
    return tier, vol_mult, risk_cap, tuple(notes)


def apply_drawdown_scaler_to_etf_weight(
    *,
    etf_weight_pre: float,
    mandate: MandateV2,
    realized_vol: float | None,
    unit_beta: float | None,
    drawdown: float | None,
    fallback_etf_weight: float,
) -> tuple[float, float, str, bool, float, tuple[str, ...]]:
    """Apply research drawdown risk-off on top of vol/β-clipped ETF weight.

    Returns
    -------
    etf_weight, effective_target_annual_vol, tier, scale_applied, etf_pre, notes
    """
    m = mandate
    tier, vol_mult, risk_cap, tier_notes = _mandate_drawdown_tier(drawdown, m)
    effective_vol = float(m.risk.target_annual_vol) * float(vol_mult)
    notes: list[str] = list(tier_notes)
    notes.append(f"etf_drawdown={drawdown}")
    notes.append(f"effective_target_annual_vol={effective_vol:.6f}")

    # Re-scale with effective vol target when L1+ reduces vol budget
    max_etf = float(m.portfolio_limits.max_etf_sleeve_weight)
    if risk_cap is not None:
        max_etf = min(max_etf, float(risk_cap))

    etf_w, scale_notes = scale_etf_sleeve_weight(
        target_annual_vol=effective_vol,
        target_beta=m.risk.target_beta_vs_benchmark,
        max_etf_sleeve_weight=max_etf,
        realized_vol=realized_vol,
        unit_beta=unit_beta,
        vol_targeting_enabled=m.risk.vol_targeting_enabled,
        fallback_etf_weight=fallback_etf_weight,
    )
    # Never raise above pre-drawdown weight (risk-off only)
    etf_w = min(float(etf_weight_pre), float(etf_w))
    etf_w = round(etf_w, 6)
    scale_applied = abs(etf_w - float(etf_weight_pre)) > 1e-9 or (
        tier != "none" and vol_mult < 1.0 - 1e-15
    )
    # scale_applied true if tier engaged (even when weight unchanged due to max_etf bind)
    if tier != "none":
        scale_applied = True
    notes.extend(scale_notes)
    notes.append(f"etf_weight_pre_drawdown={etf_weight_pre}")
    notes.append(f"etf_weight_post_drawdown={etf_w}")
    notes.append(f"drawdown_scale_applied={scale_applied}")
    return etf_w, effective_vol, tier, scale_applied, float(etf_weight_pre), tuple(notes)


@dataclass(frozen=True)
class StubBetaSleeveProvider:
    """Phase 0: index meta from D0; 510300 loaders raise NotImplementedError."""

    mandate: MandateV2
    d0_root: str | Path | None = None

    def _store(self):
        from quantlab.data.v2_d0_meta import D0MetaStore, DEFAULT_D0_ROOT

        return D0MetaStore(self.d0_root if self.d0_root is not None else DEFAULT_D0_ROOT)

    def plan(
        self,
        session: date,
        *,
        realized_vol: float | None = None,
        portfolio_beta: float | None = None,
    ) -> BetaSleevePlan:
        if realized_vol is not None or portfolio_beta is not None:
            raise NotImplementedError(
                "beta_sleeve_scaling_not_implemented:"
                f"need {ETF_510300_INSTRUMENT_ID} panel + vol path; session={session}"
            )
        index_ok = False
        etf_ok = False
        try:
            bench = self._store().load_benchmark_meta()
            index_ok = bench.is_index_000300 and bench.n_rows > 0
            etf_ok = bench.has_etf_510300_panel
        except FileNotFoundError:
            pass
        m = self.mandate
        etf = m.markets.benchmark_etf or BETA_SLEEVE_ETF_DEFAULT
        todos = (
            f"schema_locked instruments={EquityEtfInstrumentRow.SCHEMA_VERSION}",
            f"schema_locked panel={Etf510300Bar.SCHEMA_VERSION} path={Etf510300Bar.PANEL_PATH}",
            f"TODO(Data): instruments row asset_type=equity_etf id={ETF_510300_INSTRUMENT_ID} "
            f"cols={[n for n, _ in ETF_510300_INSTRUMENT_COLUMN_SPEC]}",
            f"TODO(Data): {Etf510300Bar.PANEL_PATH} cols={[n for n, _ in ETF_510300_PANEL_COLUMN_SPEC]}",
            f"index_sh000300_available={index_ok}",
            f"etf_510300_panel_available={etf_ok}",
            "promotion_approved=false",
        )
        return BetaSleevePlan(
            session=session,
            benchmark_etf=etf,
            benchmark_etf_instrument_id=ETF_510300_INSTRUMENT_ID,
            benchmark_index_id=INDEX_CSI300_INSTRUMENT_ID,
            target_annual_vol=m.risk.target_annual_vol,
            target_beta_vs_benchmark=m.risk.target_beta_vs_benchmark,
            target_beta_band=m.risk.target_beta_band,
            max_etf_sleeve_weight=m.portfolio_limits.max_etf_sleeve_weight,
            cash_weight=None,
            etf_sleeve_weight=None,
            residual_book_weight_cap=None,
            index_bars_available=index_ok,
            etf_panel_available=etf_ok,
            promotion_approved=False,
            data_ready=False,
            todos=todos,
        )

    def load_etf_instrument(self) -> EquityEtfInstrumentRow:
        raise NotImplementedError(
            "etf_510300_instrument_missing:"
            f"await instruments row {ETF_510300_INSTRUMENT_ID} "
            f"schema={EquityEtfInstrumentRow.SCHEMA_VERSION}"
        )

    def load_etf_bars(self, start: date, end: date) -> tuple[Etf510300Bar, ...]:
        _ = (start, end)
        raise NotImplementedError(
            "etf_510300_panel_missing:"
            f"await {Etf510300Bar.PANEL_PATH} schema={Etf510300Bar.SCHEMA_VERSION}; "
            "do not invent OHLCV"
        )

    def load_index_bars(self, start: date, end: date) -> tuple[BenchmarkIndexBar, ...]:
        """Load sh.000300 from D0 benchmark.parquet into frozen bar tuples."""
        import pandas as pd

        store = self._store()
        bench_path = store.root / "benchmark.parquet"
        if not bench_path.is_file():
            raise FileNotFoundError(f"d0_benchmark_missing:{bench_path}")
        frame = pd.read_parquet(bench_path).copy()
        if isinstance(frame.index, pd.DatetimeIndex):
            frame = frame.assign(_session=frame.index)
        elif "event_time" in frame.columns:
            frame = frame.assign(_session=pd.to_datetime(frame["event_time"]))
        else:
            raise ValueError("d0_benchmark_missing_session_index")
        frame["_session"] = pd.to_datetime(frame["_session"]).dt.normalize()
        lo, hi = pd.Timestamp(start), pd.Timestamp(end)
        frame = frame[(frame["_session"] >= lo) & (frame["_session"] <= hi)]
        out: list[BenchmarkIndexBar] = []
        for _, data in frame.iterrows():
            preclose = data["preclose"] if "preclose" in data.index else None
            volume = data["volume"] if "volume" in data.index else None
            amount = data["amount"] if "amount" in data.index else None
            out.append(
                BenchmarkIndexBar(
                    code=str(data["code"]),
                    session=pd.Timestamp(data["_session"]).date(),
                    open=float(data["open"]),
                    high=float(data["high"]),
                    low=float(data["low"]),
                    close=float(data["close"]),
                    preclose=float(preclose) if preclose is not None and pd.notna(preclose) else None,
                    volume=float(volume) if volume is not None and pd.notna(volume) else None,
                    amount=float(amount) if amount is not None and pd.notna(amount) else None,
                    available_at=pd.Timestamp(data["available_at"]).to_pydatetime(),
                    quality_status=str(data["quality_status"]),
                    source=str(data["source"]),
                    revision=str(data["revision"]),
                    return_basis="price_return",
                )
            )
        return tuple(out)

    def describe_contract(self) -> Mapping[str, object]:
        m = self.mandate
        return {
            "layer": "L1_beta_sleeve_cash_plus_equity_etf",
            "benchmark_primary": m.markets.benchmark_primary,
            "benchmark_etf": m.markets.benchmark_etf,
            "etf_instrument_id": ETF_510300_INSTRUMENT_ID,
            "etf_instruments_schema": EquityEtfInstrumentRow.SCHEMA_VERSION,
            "etf_panel_schema": Etf510300Bar.SCHEMA_VERSION,
            "etf_panel_path": Etf510300Bar.PANEL_PATH,
            "index_id": INDEX_CSI300_INSTRUMENT_ID,
            "index_schema": BenchmarkIndexBar.SCHEMA_VERSION,
            "target_annual_vol": m.risk.target_annual_vol,
            "target_beta_vs_benchmark": m.risk.target_beta_vs_benchmark,
            "max_etf_sleeve_weight": m.portfolio_limits.max_etf_sleeve_weight,
            "promotion_approved": False,
        }



def portfolio_beta_decomposition(
    *,
    etf_sleeve_weight: float,
    unit_beta: float | None,
    target_beta: float,
    max_etf_sleeve_weight: float,
    residual_book_weight_cap: float,
    assumed_residual_unit_beta: float = 1.0,
) -> dict[str, float | bool | None]:
    """Decompose sleeve vs portfolio β under a residual unit-β assumption.

    Does **not** raise ``max_etf``. When ``max_etf * unit_beta < target_beta``,
    the sleeve-alone gap is **structural**; closing portfolio β requires Strategy
    residual sizing (or a future Mandate change — forbidden in P2.1).
    """
    if unit_beta is None:
        return {
            "sleeve_beta": None,
            "max_sleeve_beta_at_max_etf": None,
            "beta_gap_is_structural": None,
            "residual_weight_to_hit_target_beta": None,
            "implied_portfolio_beta_at_residual_fill": None,
            "assumed_residual_unit_beta": assumed_residual_unit_beta,
        }
    ub = float(unit_beta)
    etf_w = float(etf_sleeve_weight)
    sleeve_beta = etf_w * ub
    max_sleeve = float(max_etf_sleeve_weight) * ub
    structural = max_sleeve + 1e-12 < float(target_beta)
    gap = float(target_beta) - sleeve_beta
    arb = float(assumed_residual_unit_beta)
    if abs(arb) <= 1e-12:
        resid_w = 0.0 if gap <= 0 else None  # cannot close with zero unit β
    else:
        resid_w = max(0.0, gap / arb)
        resid_w = min(resid_w, float(residual_book_weight_cap))
        resid_w = round(resid_w, 6)
    if resid_w is None:
        port = None
    else:
        port = round(sleeve_beta + resid_w * arb, 6)
    return {
        "sleeve_beta": sleeve_beta,
        "max_sleeve_beta_at_max_etf": max_sleeve,
        "beta_gap_is_structural": structural,
        "residual_weight_to_hit_target_beta": resid_w,
        "implied_portfolio_beta_at_residual_fill": port,
        "assumed_residual_unit_beta": arb,
    }


@dataclass(frozen=True)
class PrototypeBetaSleeveProvider:
    """Beta sleeve with Mandate vol-target + β budget (research-only).

    Consumes landed ``sh.510300`` V2 paths. Scales ``etf_sleeve_weight`` toward
    ``target_annual_vol`` / ``target_beta_vs_benchmark`` using trailing panel
    (and optional index) metrics, or caller-supplied unit-ETF
    ``realized_vol`` / ``portfolio_beta``. ``promotion_approved`` forced False.
    No backtest Sharpe/PnL claims.
    """

    mandate: MandateV2
    d0_root: str | Path | None = None
    # Fallback when vol/β legs unavailable (still clipped to max_etf)
    default_etf_weight: float = 0.25
    default_cash_weight: float = 0.05
    lookback_sessions: int = _DEFAULT_LOOKBACK_SESSIONS
    # Research menu: optional small-cap satellite (default OFF)
    smallcap_satellite: bool = False
    satellite_code: str | None = None  # default resolve: sh512100 → sh510500 → sz159922
    max_satellite_frac: float = 0.25  # of ETF budget; core remains primary
    # B5: optional 511260 risk-parity overlay when satellite ON (default OFF)
    bond_risk_parity_overlay: bool = False

    def _roots(self):
        from dataclasses import replace

        from quantlab.data.v2_readers import default_v2_roots

        roots = default_v2_roots()
        if self.d0_root is not None:
            roots = replace(roots, d0_root=Path(self.d0_root))
        return roots

    def _bundle(self):
        from quantlab.data.v2_readers import load_etf_510300

        return load_etf_510300(roots=self._roots())

    def _compute_unit_metrics(
        self,
        session: date,
        bundle,
    ) -> tuple[float | None, float | None, tuple[str, ...], bool]:
        """Trailing unit-ETF realized vol + β vs index (price returns)."""

        flags: list[str] = []
        lookback = max(int(self.lookback_sessions), _MIN_RETURN_OBS)

        try:
            _sessions, closes = _panel_close_series_to_session(bundle.panel_frame, session)
        except Exception as exc:  # noqa: BLE001
            flags.append(f"etf_close_series_error={type(exc).__name__}")
            return None, None, tuple(flags), False

        rets = _simple_returns(closes)
        trailing = rets[-lookback:] if len(rets) >= lookback else rets
        realized = _annualized_realized_vol(trailing)
        flags.append(f"etf_return_obs={len(trailing)}")
        flags.append(f"realized_vol_computed={realized is not None}")
        if realized is not None:
            flags.append(f"realized_vol={realized:.6f}")

        index_ok = False
        unit_beta: float | None = None
        try:
            # Need lookback+1 closes → align on overlapping calendar with ETF
            # Start far enough back; index D0 currently ends 2026-06-30.
            from datetime import timedelta

            start_guess = session - timedelta(days=int(lookback * 2.5) + 40)
            index_bars = self.load_index_bars(start_guess, session)
            index_ok = len(index_bars) > 0
            if index_bars:
                idx_map = {b.session: float(b.close) for b in index_bars}
                # Align ETF sessions (with closes) to index
                etf_sess = _sessions
                aligned_etf: list[float] = []
                aligned_idx: list[float] = []
                for i in range(1, len(etf_sess)):
                    s0, s1 = etf_sess[i - 1], etf_sess[i]
                    if s1 not in idx_map or s0 not in idx_map:
                        continue
                    prev_e, cur_e = closes[i - 1], closes[i]
                    prev_i, cur_i = idx_map[s0], idx_map[s1]
                    if prev_e and prev_i and prev_e == prev_e and prev_i == prev_i and prev_e != 0 and prev_i != 0:
                        aligned_etf.append((cur_e / prev_e) - 1.0)
                        aligned_idx.append((cur_i / prev_i) - 1.0)
                aligned_etf = aligned_etf[-lookback:]
                aligned_idx = aligned_idx[-lookback:]
                unit_beta = _trailing_beta(aligned_etf, aligned_idx)
                flags.append(f"beta_align_obs={len(aligned_etf)}")
                flags.append(f"unit_beta_computed={unit_beta is not None}")
                if unit_beta is not None:
                    flags.append(f"unit_beta={unit_beta:.6f}")
                # Last ETF session that also had index (overlap may end before `session`)
                overlap_sessions = [s for s in etf_sess if s in idx_map]
                if overlap_sessions:
                    last_overlap = overlap_sessions[-1]
                    flags.append(f"beta_window_last_session={last_overlap}")
                    if last_overlap < session:
                        flags.append("beta_window_ends_before_session")
            else:
                flags.append("index_bars_empty_for_window")
        except FileNotFoundError:
            flags.append("index_benchmark_missing")
        except Exception as exc:  # noqa: BLE001
            flags.append(f"index_beta_error={type(exc).__name__}")

        if unit_beta is None:
            # 510300 tracks CSI300; research fallback β=1.0 when index window missing
            unit_beta = 1.0
            flags.append("unit_beta_assumed_1_index_gap")

        return realized, unit_beta, tuple(flags), index_ok

    def plan(
        self,
        session: date,
        *,
        realized_vol: float | None = None,
        portfolio_beta: float | None = None,
    ) -> BetaSleevePlan:
        """Build BetaSleevePlan with Mandate vol16% / β0.70 research scaling.

        ``realized_vol`` / ``portfolio_beta`` are interpreted as **unit-ETF**
        (100% sleeve) metrics when provided; otherwise computed from the 510300
        panel (price returns) and D0 index overlap. Weights are research-only.
        """
        self.mandate.require_not_promoted()
        m = self.mandate
        etf = m.markets.benchmark_etf or BETA_SLEEVE_ETF_DEFAULT
        bundle = self._bundle()
        if bundle.promotion_approved:
            raise RuntimeError("etf_510300_promotion_approved_must_be_false")

        metric_flags: tuple[str, ...] = ()
        index_ok = False
        vol_src = "caller" if realized_vol is not None else "panel"
        beta_src = "caller" if portfolio_beta is not None else "panel_or_assumed"

        if realized_vol is None or portfolio_beta is None:
            comp_vol, comp_beta, metric_flags, index_ok = self._compute_unit_metrics(session, bundle)
            if realized_vol is None:
                realized_vol = comp_vol
            if portfolio_beta is None:
                portfolio_beta = comp_beta
        else:
            # Still probe index availability for plan flag
            try:
                from quantlab.data.v2_d0_meta import D0MetaStore

                bench = D0MetaStore(self._roots().d0_root).load_benchmark_meta()
                index_ok = bench.is_index_000300 and bench.n_rows > 0
            except FileNotFoundError:
                index_ok = False

        etf_w, scale_notes = scale_etf_sleeve_weight(
            target_annual_vol=m.risk.target_annual_vol,
            target_beta=m.risk.target_beta_vs_benchmark,
            max_etf_sleeve_weight=m.portfolio_limits.max_etf_sleeve_weight,
            realized_vol=realized_vol,
            unit_beta=portfolio_beta,
            vol_targeting_enabled=m.risk.vol_targeting_enabled,
            fallback_etf_weight=self.default_etf_weight,
        )
        etf_w_pre_dd = round(float(etf_w), 6)

        # Peak-to-trough drawdown on 510300 closes (Mandate peak_nav_unreset research)
        etf_dd: float | None = None
        try:
            _sess_dd, closes_dd = _panel_close_series_to_session(bundle.panel_frame, session)
            etf_dd = _current_drawdown_from_peak(closes_dd)
        except Exception as exc:  # noqa: BLE001
            metric_flags = tuple(metric_flags) + (f"drawdown_compute_error={type(exc).__name__}",)

        etf_w, effective_vol, dd_tier, dd_applied, _pre, dd_notes = apply_drawdown_scaler_to_etf_weight(
            etf_weight_pre=etf_w_pre_dd,
            mandate=m,
            realized_vol=realized_vol,
            unit_beta=portfolio_beta,
            drawdown=etf_dd,
            fallback_etf_weight=self.default_etf_weight,
        )
        etf_w = round(float(etf_w), 6)

        # --- Small-cap satellite menu (research; default OFF) ---
        # Splits existing etf_w budget; never raises max_etf / never invents OHLCV.
        from datetime import timedelta

        from quantlab.beta.satellite import (
            contribution_weighted_split,
            load_satellite_series,
            resolve_satellite_code,
        )

        sat_enabled = bool(self.smallcap_satellite)
        core_w = etf_w
        sat_w = 0.0
        contrib_core = 1.0
        contrib_sat = 0.0
        sat_code: str | None = None
        sat_asset: str | None = None
        sat_unit_beta: float | None = None
        sat_ready = False
        sat_notes: tuple[str, ...] = ()

        if sat_enabled:
            sat_code, resolve_notes = resolve_satellite_code(self.satellite_code)
            sat_notes = tuple(resolve_notes)
            if sat_code is None:
                sat_notes = sat_notes + ("smallcap_satellite_on_but_no_code", "fallback_core_only")
            else:
                series = load_satellite_series(sat_code, session)
                sat_notes = sat_notes + tuple(series.notes)
                sat_asset = series.asset or None
                sat_ready = bool(series.data_ready)
                if sat_ready and portfolio_beta is not None:
                    # Satellite unit β vs CSI300 index (same window style as core)
                    lookback = max(int(self.lookback_sessions), _MIN_RETURN_OBS)
                    start_guess = session - timedelta(days=int(lookback * 2.5) + 40)
                    try:
                        index_bars = self.load_index_bars(start_guess, session)
                        idx_map = {b.session: float(b.close) for b in index_bars}
                        aligned_s: list[float] = []
                        aligned_i: list[float] = []
                        sess_s = list(series.sessions)
                        closes_s = list(series.closes)
                        for i in range(1, len(sess_s)):
                            s0, s1 = sess_s[i - 1], sess_s[i]
                            if s0 not in idx_map or s1 not in idx_map:
                                continue
                            prev_s, cur_s = closes_s[i - 1], closes_s[i]
                            prev_i, cur_i = idx_map[s0], idx_map[s1]
                            if prev_s and prev_i and prev_s != 0 and prev_i != 0:
                                aligned_s.append((cur_s / prev_s) - 1.0)
                                aligned_i.append((cur_i / prev_i) - 1.0)
                        aligned_s = aligned_s[-lookback:]
                        aligned_i = aligned_i[-lookback:]
                        sat_unit_beta = _trailing_beta(aligned_s, aligned_i)
                        if sat_unit_beta is None:
                            sat_unit_beta = 1.0
                            sat_notes = sat_notes + ("satellite_unit_beta_assumed_1",)
                        else:
                            sat_notes = sat_notes + (f"satellite_unit_beta={sat_unit_beta:.6f}",)
                    except Exception as exc:  # noqa: BLE001
                        sat_unit_beta = 1.0
                        sat_notes = sat_notes + (f"satellite_beta_error={type(exc).__name__}",)

                    core_ub = float(portfolio_beta) if portfolio_beta is not None else 1.0
                    split = contribution_weighted_split(
                        etf_w,
                        core_ub,
                        float(sat_unit_beta),
                        max_satellite_frac=float(self.max_satellite_frac),
                    )
                    core_w = split.core_weight
                    sat_w = split.satellite_weight
                    contrib_core = split.contribution_weight_core
                    contrib_sat = split.contribution_weight_satellite
                    sat_notes = sat_notes + (
                        f"split_mode={split.mode}",
                        f"max_satellite_frac={split.max_satellite_frac}",
                        f"contribution_weight_core={contrib_core}",
                        f"contribution_weight_satellite={contrib_sat}",
                    )
                else:
                    sat_notes = sat_notes + ("satellite_data_not_ready_core_only",)
                    sat_ready = False

        # Cash floor from Mandate; keep a small active cash buffer when room remains
        min_cash = float(m.capital.min_cash_buffer_normal)
        cash_w = max(min_cash, min(self.default_cash_weight, max(0.0, 1.0 - etf_w)))
        if etf_w + cash_w > 1.0 + 1e-12:
            cash_w = max(0.0, 1.0 - etf_w)
        cash_w = round(float(cash_w), 6)
        residual_cap = round(max(0.0, 1.0 - etf_w - cash_w), 6)

        # Session coverage check (counts only — no fabricated returns)
        session_bar_n = 0
        try:
            from quantlab.data.v2_readers import etf_510300_bars

            session_bar_n = len(etf_510300_bars(bundle, session, session))
        except Exception:  # noqa: BLE001
            session_bar_n = 0

        band_lo, band_hi = m.risk.target_beta_band
        target_beta = float(m.risk.target_beta_vs_benchmark)
        unit_b = float(portfolio_beta) if portfolio_beta is not None else None
        # Sleeve β: core-only when satellite off/unavailable; else contribution mix
        if sat_enabled and sat_ready and sat_unit_beta is not None and unit_b is not None:
            implied_beta = core_w * float(unit_b) + sat_w * float(sat_unit_beta)
        else:
            implied_beta = (etf_w * unit_b) if unit_b is not None else None
        in_band = (
            implied_beta is not None and band_lo - 1e-12 <= implied_beta <= band_hi + 1e-12
        )
        # Positive gap = sleeve short of Mandate target β (Strategy residual budget)
        beta_gap = (target_beta - implied_beta) if implied_beta is not None else None
        residual_beta_budget = max(0.0, beta_gap) if beta_gap is not None else None

        # Research default: long industry-neutral residual ≈ unit market β 1.0
        assumed_resid_ub = 1.0
        decomp = portfolio_beta_decomposition(
            etf_sleeve_weight=etf_w,
            unit_beta=unit_b,
            target_beta=target_beta,
            max_etf_sleeve_weight=m.portfolio_limits.max_etf_sleeve_weight,
            residual_book_weight_cap=residual_cap,
            assumed_residual_unit_beta=assumed_resid_ub,
        )

        todos = (
            "promotion_approved=false",
            "vol_target_beta_budget_research",
            "drawdown_scaler_research",
            f"smallcap_satellite={sat_enabled}",
            "not_live_trading_ready",
            "no_backtest_sharpe_pnl",
            "max_etf_not_raised",
            f"etf_source=data/v2/etf_510300",
            f"etf_bars={bundle.n_bars}",
            f"etf_range={bundle.date_min}..{bundle.date_max}",
            f"etf_bars_on_session={session_bar_n}",
            f"etf_quality_status={bundle.instrument.quality_status}",
            f"lookback_sessions={self.lookback_sessions}",
            f"vol_src={vol_src}",
            f"beta_src={beta_src}",
            f"realized_vol={realized_vol}",
            f"unit_beta={unit_b}",
            f"target_annual_vol={m.risk.target_annual_vol}",
            f"effective_target_annual_vol={effective_vol}",
            f"target_beta={target_beta}",
            f"implied_sleeve_beta={implied_beta}",
            f"beta_gap_to_mandate={beta_gap}",
            f"residual_beta_budget_for_strategy={residual_beta_budget}",
            f"implied_beta_in_band={in_band}",
            f"beta_gap_is_structural={decomp['beta_gap_is_structural']}",
            f"max_sleeve_beta_at_max_etf={decomp['max_sleeve_beta_at_max_etf']}",
            f"assumed_residual_unit_beta={decomp['assumed_residual_unit_beta']}",
            f"residual_weight_to_hit_target_beta={decomp['residual_weight_to_hit_target_beta']}",
            f"implied_portfolio_beta_at_residual_fill={decomp['implied_portfolio_beta_at_residual_fill']}",
            f"etf_drawdown={etf_dd}",
            f"drawdown_tier={dd_tier}",
            f"drawdown_scale_applied={dd_applied}",
            f"etf_weight_pre_drawdown={etf_w_pre_dd}",
            f"core_etf_weight={core_w}",
            f"satellite_etf_weight={sat_w}",
            f"contribution_weight_core={contrib_core}",
            f"contribution_weight_satellite={contrib_sat}",
            f"satellite_code={sat_code}",
            f"satellite_data_ready={sat_ready}",
            f"satellite_unit_beta={sat_unit_beta}",
            f"industry_neutral_residual_book={m.signal_construction.industry_neutral_residual_book}",
            f"industry_scheme={m.portfolio_limits.industry_scheme}",
            "sw_l1_promotable=false",
            "residual_beta_owner=Strategy",
            f"ordinary_rebalance={m.rebalance.ordinary_rebalance}",
            f"risk_budget_and_vol_scale={m.rebalance.risk_budget_and_vol_scale}",
            *scale_notes,
            *dd_notes,
            *sat_notes[:8],
            *metric_flags,
            *bundle.quality_gaps[:4],
        )
        return BetaSleevePlan(
            session=session,
            benchmark_etf=etf,
            benchmark_etf_instrument_id=ETF_510300_INSTRUMENT_ID,
            benchmark_index_id=INDEX_CSI300_INSTRUMENT_ID,
            target_annual_vol=m.risk.target_annual_vol,
            target_beta_vs_benchmark=m.risk.target_beta_vs_benchmark,
            target_beta_band=m.risk.target_beta_band,
            max_etf_sleeve_weight=m.portfolio_limits.max_etf_sleeve_weight,
            cash_weight=cash_w,
            etf_sleeve_weight=etf_w,
            residual_book_weight_cap=residual_cap,
            index_bars_available=index_ok,
            etf_panel_available=True,
            promotion_approved=False,
            data_ready=True,
            unit_beta=unit_b,
            implied_sleeve_beta=implied_beta,
            beta_gap_to_mandate=beta_gap,
            residual_beta_budget_for_strategy=residual_beta_budget,
            implied_beta_in_band=in_band,
            etf_drawdown=etf_dd,
            drawdown_tier=dd_tier,
            drawdown_scale_applied=dd_applied,
            etf_weight_pre_drawdown=etf_w_pre_dd,
            effective_target_annual_vol=effective_vol,
            assumed_residual_unit_beta=float(decomp["assumed_residual_unit_beta"])
            if decomp["assumed_residual_unit_beta"] is not None
            else None,
            max_sleeve_beta_at_max_etf=float(decomp["max_sleeve_beta_at_max_etf"])
            if decomp["max_sleeve_beta_at_max_etf"] is not None
            else None,
            beta_gap_is_structural=bool(decomp["beta_gap_is_structural"])
            if decomp["beta_gap_is_structural"] is not None
            else None,
            residual_weight_to_hit_target_beta=float(decomp["residual_weight_to_hit_target_beta"])
            if decomp["residual_weight_to_hit_target_beta"] is not None
            else None,
            implied_portfolio_beta_at_residual_fill=float(decomp["implied_portfolio_beta_at_residual_fill"])
            if decomp["implied_portfolio_beta_at_residual_fill"] is not None
            else None,
            smallcap_satellite=sat_enabled,
            satellite_code=sat_code,
            satellite_asset=sat_asset,
            core_etf_weight=round(float(core_w), 6),
            satellite_etf_weight=round(float(sat_w), 6) if sat_enabled else None,
            contribution_weight_core=round(float(contrib_core), 6),
            contribution_weight_satellite=round(float(contrib_sat), 6) if sat_enabled else None,
            satellite_unit_beta=float(sat_unit_beta) if sat_unit_beta is not None else None,
            satellite_data_ready=bool(sat_ready) if sat_enabled else False,
            todos=todos,
        )

    def load_etf_instrument(self) -> EquityEtfInstrumentRow:
        return self._bundle().instrument

    def load_etf_bars(self, start: date, end: date) -> tuple[Etf510300Bar, ...]:
        from quantlab.data.v2_readers import etf_510300_bars

        return etf_510300_bars(self._bundle(), start, end)

    def load_index_bars(self, start: date, end: date) -> tuple[BenchmarkIndexBar, ...]:
        return StubBetaSleeveProvider(self.mandate, d0_root=self.d0_root).load_index_bars(start, end)

    def describe_contract(self) -> Mapping[str, object]:
        base = dict(StubBetaSleeveProvider(self.mandate, d0_root=self.d0_root).describe_contract())
        base["provider"] = type(self).__name__
        base["promotion_approved"] = False
        base["vol_targeting"] = True
        base["scaling"] = "min(target_vol/realized_vol, target_beta/unit_beta, max_etf)+drawdown_risk_off"
        base["industry_neutral_residual_book"] = self.mandate.signal_construction.industry_neutral_residual_book
        base["industry_scheme"] = self.mandate.portfolio_limits.industry_scheme
        base["sw_l1_promotable"] = False
        base["smallcap_satellite"] = bool(self.smallcap_satellite)
        base["smallcap_satellite_default"] = False
        base["bond_risk_parity_overlay"] = bool(self.bond_risk_parity_overlay)
        base["bond_risk_parity_overlay_default"] = False
        base["max_satellite_frac"] = float(self.max_satellite_frac)
        base["satellite_code_pref"] = self.satellite_code or "sh512100|sh510500|sz159922"
        try:
            b = self._bundle()
            base["etf_loaded"] = True
            base["etf_n_bars"] = b.n_bars
            base["etf_date_min"] = str(b.date_min)
            base["etf_date_max"] = str(b.date_max)
            base["etf_quality_status"] = b.instrument.quality_status
        except Exception as exc:  # noqa: BLE001
            base["etf_loaded"] = False
            base["etf_load_error"] = f"{type(exc).__name__}:{exc}"
        return base

    def strategy_handoff_surface(self) -> Mapping[str, object]:
        """Fields Strategy consumes for industry-neutral residual book sizing.

        SW_L1 PIT remains research-only (``promotable=false``); Beta never flips
        ``promotion_approved``. Mandate β-gap is measurable: Strategy owns
        ``residual_beta_budget_for_strategy``; Beta never raises ``max_etf``.
        """
        m = self.mandate
        return {
            "etf_sleeve_weight": "BetaSleevePlan.etf_sleeve_weight",
            "cash_weight": "BetaSleevePlan.cash_weight",
            "residual_book_weight_cap": "BetaSleevePlan.residual_book_weight_cap",
            "book_weight_cap_arg": "PortfolioConstructorV2.construct(book_weight_cap=plan.residual_book_weight_cap)",
            "target_beta": "BetaSleevePlan.target_beta_vs_benchmark",
            "unit_beta": "BetaSleevePlan.unit_beta",
            "implied_sleeve_beta": "BetaSleevePlan.implied_sleeve_beta",
            "beta_gap_to_mandate": "BetaSleevePlan.beta_gap_to_mandate",
            "residual_beta_budget_for_strategy": "BetaSleevePlan.residual_beta_budget_for_strategy",
            "implied_beta_in_band": "BetaSleevePlan.implied_beta_in_band",
            "beta_gap_is_structural": "BetaSleevePlan.beta_gap_is_structural",
            "max_sleeve_beta_at_max_etf": "BetaSleevePlan.max_sleeve_beta_at_max_etf",
            "assumed_residual_unit_beta": "BetaSleevePlan.assumed_residual_unit_beta",
            "residual_weight_to_hit_target_beta": "BetaSleevePlan.residual_weight_to_hit_target_beta",
            "implied_portfolio_beta_at_residual_fill": "BetaSleevePlan.implied_portfolio_beta_at_residual_fill",
            "residual_beta_owner": "Strategy",
            "max_etf_raised": False,
            "p2_1_mandate_change": "FORBIDDEN_until_implementation_path_exhausted",
            "etf_drawdown": "BetaSleevePlan.etf_drawdown",
            "drawdown_tier": "BetaSleevePlan.drawdown_tier",
            "drawdown_scale_applied": "BetaSleevePlan.drawdown_scale_applied",
            "etf_weight_pre_drawdown": "BetaSleevePlan.etf_weight_pre_drawdown",
            "effective_target_annual_vol": "BetaSleevePlan.effective_target_annual_vol",
            "industry_neutral_residual_book": m.signal_construction.industry_neutral_residual_book,
            "industry_scheme": m.portfolio_limits.industry_scheme,
            "max_industry_weight": m.portfolio_limits.max_industry_weight,
            "unknown_industry_cap": m.portfolio_limits.unknown_industry_cap,
            "sw_l1_path": "data/v2/sw_l1_pit/industry_members_sw_l1_prefix.parquet",
            "sw_l1_promotable": False,
            "promotion_approved": False,
            "vol_beta_owner": "quantlab.beta.sleeve",
            "target_annual_vol": m.risk.target_annual_vol,
            "target_beta_vs_benchmark": m.risk.target_beta_vs_benchmark,
            "ordinary_rebalance": m.rebalance.ordinary_rebalance,
            "risk_budget_and_vol_scale": m.rebalance.risk_budget_and_vol_scale,
            "smallcap_satellite": bool(self.smallcap_satellite),
            "smallcap_satellite_default": False,
            "bond_risk_parity_overlay": bool(self.bond_risk_parity_overlay),
            "bond_risk_parity_overlay_default": False,
            "residual_weight_to_hit_target_beta": "BetaSleevePlan.residual_weight_to_hit_target_beta",
            "b6_status": "beta_delivered_strategy_consume_after_P0",
            "compare_arms_config": "quantlab/beta/configs/compare_arms_v1.json",
            "core_etf_weight": "BetaSleevePlan.core_etf_weight",
            "satellite_etf_weight": "BetaSleevePlan.satellite_etf_weight",
            "contribution_weight_core": "BetaSleevePlan.contribution_weight_core",
            "contribution_weight_satellite": "BetaSleevePlan.contribution_weight_satellite",
            "satellite_code": "BetaSleevePlan.satellite_code",
            "satellite_data_ready": "BetaSleevePlan.satellite_data_ready",
            "satellite_menu_doc": "docs/v2/BETA_SMALLCAP_SATELLITE.md",
            "compare_arms": (
                "flag_off_core_only_510300",
                "flag_on_contribution_weighted_core_plus_satellite",
            ),
            "note": (
                "Residual alpha book under residual_book_weight_cap; "
                "residual_beta_budget_for_strategy = max(0, target_beta - implied_sleeve_beta); "
                "Beta clips at max_etf and may risk-off via drawdown scaler; "
                "smallcap_satellite default OFF — when ON splits ETF budget by contribution weights "
                "(core 510300 primary; CSI1000/500 ETF satellite proxy); "
                "SW_L1 research-only — never promotion-grade."
            ),
        }


    def satellite_menu(self, session: date | None = None) -> Mapping[str, object]:
        """Compare-arm descriptor for Strategy (flag off/on).

        Always lists raise-CAGR candidates (wide-basket / M2 / ETF proxies).
        """
        from quantlab.beta.satellite import (
            build_bond_overlay_spec,
            contribution_weighted_split,
            load_compare_arms_config,
            load_satellite_series,
            resolve_satellite_code,
            satellite_menu_descriptor,
        )

        cfg = load_compare_arms_config()
        overlay = build_bond_overlay_spec(
            enabled=bool(self.bond_risk_parity_overlay),
            satellite_on=bool(self.smallcap_satellite),
        )
        if not self.smallcap_satellite:
            return satellite_menu_descriptor(
                smallcap_satellite=False,
                split=None,
                series=None,
                bond_overlay=overlay,
                config=cfg,
            )
        sess = session
        if sess is None:
            from datetime import date as _date

            sess = _date(2026, 10, 9)
        code, _ = resolve_satellite_code(self.satellite_code)
        series = load_satellite_series(code, sess) if code else None
        split = contribution_weighted_split(
            0.40,
            1.0,
            1.0,
            max_satellite_frac=float(self.max_satellite_frac),
        )
        return satellite_menu_descriptor(
            smallcap_satellite=True,
            split=split,
            series=series,
            bond_overlay=overlay,
            config=cfg,
        )

    def compare_arms_catalog(self) -> Mapping[str, object]:
        """Full ESSENCE compare-arm config + hooks (Strategy-facing)."""
        from quantlab.beta.satellite import (
            build_bond_overlay_spec,
            describe_stock_basket_hooks,
            etf_proxy_compare_arms,
            load_compare_arms_config,
            raise_cagr_menu_candidates,
            stock_basket_specs,
        )

        cfg = dict(load_compare_arms_config())
        cfg["raise_cagr_candidates"] = list(raise_cagr_menu_candidates(cfg))
        cfg["etf_proxy_compare_arms"] = list(etf_proxy_compare_arms(cfg))
        cfg["stock_basket_specs"] = [s.as_dict() for s in stock_basket_specs(cfg)]
        cfg["stock_basket_hooks"] = describe_stock_basket_hooks()
        cfg["bond_risk_parity_overlay"] = build_bond_overlay_spec(
            enabled=bool(self.bond_risk_parity_overlay),
            satellite_on=bool(self.smallcap_satellite),
        ).as_dict()
        cfg["provider_flags"] = {
            "smallcap_satellite": bool(self.smallcap_satellite),
            "bond_risk_parity_overlay": bool(self.bond_risk_parity_overlay),
            "satellite_code": self.satellite_code,
            "max_satellite_frac": float(self.max_satellite_frac),
        }
        cfg["promotion_approved"] = False
        return cfg


@dataclass(frozen=True)
class VolTargetBetaSleeveProvider(PrototypeBetaSleeveProvider):

    """Explicit name for Mandate vol-target + β-budget Beta sleeve (same logic)."""

    pass
