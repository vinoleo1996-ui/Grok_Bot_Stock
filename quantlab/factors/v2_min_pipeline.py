"""V2 minimal residual/alpha factor pipeline (research-only).

Computes:
  - M01_12_1 / momentum_12m1m (and momentum_3m) on merged close panels
  - V01_EP from accepted ep_pit_daily_tushare (default), fallback ep_tushare_asof / ep_research_asof outside coverage,
    then financials_pit_tushare net_profit / float_mktcap PIT

IC / ICIR are **process metrics only** — never a promotion gate.
``promotion_approved=false`` everywhere; financials PIT marked not promotable.

Sampling via ``max_instruments`` is expected for smoke speed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np
import pandas as pd

from quantlab.factors.engine import factor_momentum, winsorize_zscore
from quantlab.factors.residual_factory import COMPOSITE_MEMBER_IDS, RawFactorPanel


@dataclass(frozen=True)
class ProcessICRow:
    """One session's cross-sectional IC — process metric only."""

    session: date
    factor_id: str
    n_obs: int
    ic_spearman: float | None
    forward_horizon_sessions: int
    process_metric_only: bool = True
    promotion_approved: bool = False

    def __post_init__(self) -> None:
        if self.promotion_approved:
            raise ValueError("process_ic_promotion_approved_must_be_false")
        if not self.process_metric_only:
            raise ValueError("process_ic_must_flag_process_metric_only")


@dataclass(frozen=True)
class ProcessICSummary:
    factor_id: str
    n_sessions: int
    ic_mean: float | None
    ic_std: float | None
    icir: float | None
    rows: tuple[ProcessICRow, ...]
    process_metric_only: bool = True
    promotion_approved: bool = False
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.promotion_approved:
            raise ValueError("ic_summary_promotion_approved_must_be_false")


@dataclass(frozen=True)
class V2MinPipelineResult:
    session: date
    universe_ids: tuple[str, ...]
    max_instruments: int | None
    momentum_raw: Mapping[str, float]
    momentum_3m_raw: Mapping[str, float]
    ep_raw: Mapping[str, float]
    ep_negative_flagged: int
    ep_coverage: int
    financials_promotable: bool = False
    financials_path: str | None = None
    financials_metric_used: str | None = None
    mktcap_source_counts: Mapping[str, int] = field(default_factory=dict)
    ic_summaries: tuple[ProcessICSummary, ...] = ()
    promotion_approved: bool = False
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.promotion_approved:
            raise ValueError("v2_min_pipeline_promotion_approved_must_be_false")
        if self.financials_promotable:
            raise ValueError("financials_must_remain_non_promotable")


def _load_close_panel(
    instrument_ids: Sequence[str],
    *,
    d0_root: Path,
    asof_extend_dir: Path,
    end_session: date,
    lookback_calendar_days: int = 700,  # ~280+ trading days for M01_12_1 + IC window
) -> pd.DataFrame:
    """Wide close panel (DatetimeIndex x instrument_id) from merged panels."""
    from quantlab.data.v2_readers import load_merged_panel

    start = end_session - timedelta(days=lookback_calendar_days)
    series: dict[str, pd.Series] = {}
    for iid in instrument_ids:
        view = load_merged_panel(iid, d0_root=d0_root, asof_extend_dir=asof_extend_dir)
        frame = view.frame
        if frame is None or frame.empty or "close" not in frame.columns:
            continue
        et = pd.to_datetime(frame["event_time"]).dt.normalize()
        close = pd.to_numeric(frame["close"], errors="coerce")
        s = pd.Series(close.values, index=et).sort_index()
        s = s[~s.index.duplicated(keep="last")]
        s = s[(s.index >= pd.Timestamp(start)) & (s.index <= pd.Timestamp(end_session))]
        if len(s) >= 30:
            series[str(iid)] = s
    if not series:
        return pd.DataFrame()
    wide = pd.DataFrame(series).sort_index()
    return wide


def compute_momentum_cross_section(
    close: pd.DataFrame,
    session: date,
) -> tuple[dict[str, float], dict[str, float]]:
    """M01_12_1 (momentum_12m1m) and momentum_3m at ``session`` (z-scored CS)."""
    if close.empty or pd.Timestamp(session) not in close.index:
        # nearest prior session
        idx = close.index[close.index <= pd.Timestamp(session)]
        if len(idx) == 0:
            return {}, {}
        session_ts = idx[-1]
    else:
        session_ts = pd.Timestamp(session)

    moms = factor_momentum(close)
    m12 = moms["momentum_12m1m"]
    m3 = moms["momentum_3m"]
    if session_ts not in m12.index:
        return {}, {}
    row12 = m12.loc[session_ts].dropna()
    row3 = m3.loc[session_ts].dropna()
    return (
        {str(k): float(v) for k, v in row12.items()},
        {str(k): float(v) for k, v in row3.items()},
    )


def compute_ep_cross_section(
    session: date,
    universe_ids: Sequence[str],
    float_mktcap: Mapping[str, float],
    *,
    roots=None,
    fin_view=None,
    bs_view=None,
    ep_research_view=None,
) -> tuple[dict[str, float], dict[str, object]]:
    """V01_EP research path (never promotable). Prefer ep_research table when present."""
    from quantlab.data.v2_readers import (
        default_v2_roots,
        ep_research_lookup,
        financials_metric_asof,
        load_ep_research,
        load_financials_pit,
    )

    roots = roots or default_v2_roots()
    meta: dict[str, object] = {
        "financials_promotable": False,
        "promotion_approved": False,
        "negative_e_flagged": 0,
        "metric_used": None,
        "path": None,
        "quality_label": None,
    }

    ep_view = ep_research_view
    # PIT: never use an EP as-of file dated after the requested session
    if ep_view is not None and ep_view.session is not None and ep_view.session > session:
        ep_view = None
    if ep_view is None:
        try:
            ep_view = load_ep_research(roots=roots, session=session)
        except FileNotFoundError:
            ep_view = None
    if ep_view is not None:
        if (ep_view.promotable or ep_view.promotion_approved) and getattr(ep_view, "source_variant", "research") != "tushare":
            raise RuntimeError("ep_research_promotable_leak")
        ep_pref = ep_research_lookup(ep_view, instrument_ids=universe_ids, require_sane=True)
        if ep_pref:
            meta["path"] = ep_view.path
            meta["quality_label"] = ep_view.quality_label
            is_ts = getattr(ep_view, "source_variant", "research") == "tushare"
            is_pit = "ep_pit_daily_tushare" in str(ep_view.path)
            meta["metric_used"] = ("ep_pit_daily_tushare" if is_pit else "ep_tushare_asof") if is_ts else "ep_research_asof"
            meta["ep_source_variant"] = getattr(ep_view, "source_variant", "research")
            meta["ep_dataset_accepted"] = bool(ep_view.promotable)
            meta["ep_definition"] = (
                "ep_pit_daily_ttm_attr_np_over_total_mv" if is_ts and is_pit
                else "ep_tushare_ep_latest_net_profit_over_float_mktcap" if is_ts
                else "ep_research_precomputed_net_profit_over_mktcap"
            )
            meta["ep_research_session"] = str(ep_view.session) if ep_view.session else None
            if ep_view.session is not None and ep_view.session != session:
                meta["ep_research_stale_carry"] = True
                meta["ep_research_note"] = (
                    f"research_carry_ep_asof={ep_view.session}:requested={session}"
                )
            if ep_view.frame is not None and "net_profit" in ep_view.frame.columns:
                sub = ep_view.frame[
                    ep_view.frame["instrument_id"].astype(str).isin(set(map(str, universe_ids)))
                ]
                meta["negative_e_flagged"] = int(
                    (pd.to_numeric(sub["net_profit"], errors="coerce") < 0).sum()
                )
            return {iid: float(v) for iid, v in ep_pref.items() if np.isfinite(v)}, meta

    view = fin_view if fin_view is not None else load_financials_pit(roots=roots)
    if (view.promotable or view.promotion_approved) and getattr(view, "source_variant", "research") != "tushare":
        raise RuntimeError("financials_pit_promotable_leak")
    meta["path"] = view.path
    meta["quality_label"] = view.quality_label
    meta["available_at_rule"] = view.available_at_rule
    meta["policy_path"] = view.policy_path

    raw_all = financials_metric_asof(
        view.frame, session, universe_ids, "net_profit", negative_as_missing=False
    )
    neg = sum(1 for v in raw_all.values() if v < 0)
    meta["negative_e_flagged"] = neg
    earnings = financials_metric_asof(
        view.frame, session, universe_ids, "net_profit", negative_as_missing=True
    )
    meta["metric_used"] = "net_profit"

    if not earnings:
        bs = bs_view if bs_view is not None else load_financials_pit(roots=roots, prefer="baostock")
        meta["path"] = bs.path
        meta["quality_label"] = bs.quality_label
        earnings = financials_metric_asof(
            bs.frame, session, universe_ids, "eps_ttm", negative_as_missing=True
        )
        meta["metric_used"] = "eps_ttm_baostock_fallback"
        ep = {iid: float(v) for iid, v in earnings.items() if np.isfinite(v)}
        meta["ep_definition"] = "eps_ttm_as_ep_proxy_research"
        return ep, meta

    ep: dict[str, float] = {}
    for iid, e in earnings.items():
        mkt = float_mktcap.get(iid)
        if mkt is None or not np.isfinite(mkt) or mkt <= 0:
            continue
        ep[iid] = float(e) / float(mkt)
    meta["ep_definition"] = "net_profit / float_mktcap"
    return ep, meta


def cross_section_ic(
    factor: Mapping[str, float],
    forward_ret: Mapping[str, float],
    *,
    session: date,
    factor_id: str,
    horizon: int,
) -> ProcessICRow:
    ids = sorted(set(factor) & set(forward_ret))
    if len(ids) < 8:
        return ProcessICRow(
            session=session,
            factor_id=factor_id,
            n_obs=len(ids),
            ic_spearman=None,
            forward_horizon_sessions=horizon,
        )
    f = pd.Series({i: factor[i] for i in ids}, dtype=float)
    r = pd.Series({i: forward_ret[i] for i in ids}, dtype=float)
    ic = float(f.corr(r, method="spearman"))
    if not np.isfinite(ic):
        ic = None
    return ProcessICRow(
        session=session,
        factor_id=factor_id,
        n_obs=len(ids),
        ic_spearman=ic,
        forward_horizon_sessions=horizon,
    )


def summarize_ic(rows: Sequence[ProcessICRow], factor_id: str) -> ProcessICSummary:
    ics = [r.ic_spearman for r in rows if r.ic_spearman is not None]
    if len(ics) < 2:
        return ProcessICSummary(
            factor_id=factor_id,
            n_sessions=len(rows),
            ic_mean=float(np.mean(ics)) if ics else None,
            ic_std=None,
            icir=None,
            rows=tuple(rows),
            notes=("insufficient_ic_sessions_for_icir", "process_metric_only=true"),
        )
    mean = float(np.mean(ics))
    std = float(np.std(ics, ddof=1))
    icir = (mean / std) if std > 1e-12 else None
    return ProcessICSummary(
        factor_id=factor_id,
        n_sessions=len(rows),
        ic_mean=mean,
        ic_std=std,
        icir=icir,
        rows=tuple(rows),
        notes=("process_metric_only=true", "promotion_approved=false", "not_a_promotion_gate"),
    )


def _forward_returns(
    close: pd.DataFrame,
    session: date,
    horizon: int,
) -> dict[str, float]:
    """Close-to-close forward return over ``horizon`` sessions."""
    idx = close.index[close.index >= pd.Timestamp(session)]
    if len(idx) <= horizon:
        return {}
    # find session or next available
    if pd.Timestamp(session) in close.index:
        t0 = pd.Timestamp(session)
    else:
        prior = close.index[close.index <= pd.Timestamp(session)]
        if len(prior) == 0:
            return {}
        t0 = prior[-1]
    loc = close.index.get_loc(t0)
    if isinstance(loc, slice):
        loc = loc.start
    if isinstance(loc, np.ndarray):
        loc = int(loc.flat[0])
    t1_loc = loc + horizon
    if t1_loc >= len(close.index):
        return {}
    t1 = close.index[t1_loc]
    row0 = close.loc[t0]
    row1 = close.loc[t1]
    out: dict[str, float] = {}
    for col in close.columns:
        a, b = row0.get(col), row1.get(col)
        if pd.isna(a) or pd.isna(b) or float(a) == 0:
            continue
        out[str(col)] = float(b) / float(a) - 1.0
    return out


def run_v2_min_pipeline(
    session: date,
    universe_ids: Sequence[str],
    float_mktcap: Mapping[str, float],
    *,
    d0_root: Path | None = None,
    asof_extend_dir: Path | None = None,
    max_instruments: int | None = 80,
    ic_lookback_sessions: int = 15,
    forward_horizon: int = 5,
    mktcap_source_by_id: Mapping[str, str] | None = None,
) -> V2MinPipelineResult:
    """Run momentum + research EP on a sampled mask universe; IC as process metric."""
    from quantlab.data.v2_readers import default_v2_roots

    roots = default_v2_roots()
    d0 = Path(d0_root) if d0_root is not None else roots.d0_root
    ext = Path(asof_extend_dir) if asof_extend_dir is not None else roots.asof_extend_dir

    ids = list(universe_ids)
    if max_instruments is not None:
        ids = ids[: max(0, int(max_instruments))]
    notes = [
        "promotion_approved=false",
        "process_metric_only=true",
        "financials_pit_not_promotable",
        f"max_instruments={max_instruments}",
        f"universe_in={len(universe_ids)}",
        f"universe_used={len(ids)}",
        f"ic_lookback_sessions={ic_lookback_sessions}",
        f"forward_horizon={forward_horizon}",
    ]

    from dataclasses import replace as dc_replace

    from quantlab.data.v2_readers import load_ep_research, load_financials_pit

    fin_view = load_financials_pit(roots=roots)
    # Restrict financials to universe + earnings-like metrics for IC loop speed
    fin_frame = fin_view.frame
    if fin_frame is not None and not fin_frame.empty:
        idset = set(ids)
        fin_frame = fin_frame[
            fin_frame["instrument_id"].astype(str).isin(idset)
            & fin_frame["metric"].astype(str).isin(["net_profit", "eps_ttm"])
        ].copy()
        fin_view = dc_replace(fin_view, frame=fin_frame, n_rows=int(len(fin_frame)))
    bs_view = None  # lazy
    try:
        ep_research_view = load_ep_research(roots=roots, session=session)
        notes.append(f"ep_path={ep_research_view.path}")
        notes.append(f"ep_source_variant={ep_research_view.source_variant}")
        notes.append(f"ep_dataset_accepted={str(bool(ep_research_view.promotable)).lower()}")
    except FileNotFoundError:
        ep_research_view = None
        notes.append("ep_research_missing")

    close = _load_close_panel(ids, d0_root=d0, asof_extend_dir=ext, end_session=session)
    notes.append(f"close_panel_shape={close.shape}")

    m12, m3 = compute_momentum_cross_section(close, session)
    ep, ep_meta = compute_ep_cross_section(
        session,
        ids,
        float_mktcap,
        roots=roots,
        fin_view=fin_view,
        bs_view=bs_view,
        ep_research_view=ep_research_view,
    )
    if ep_meta.get("metric_used") == "eps_ttm_baostock_fallback" and bs_view is None:
        bs_view = load_financials_pit(roots=roots, prefer="baostock")
    notes.append(f"ep_definition={ep_meta.get('ep_definition')}")
    notes.append(f"ep_metric={ep_meta.get('metric_used')}")

    # Optional CS z-score polish for EP display consistency with momentum
    if ep:
        ep_z = winsorize_zscore(pd.Series(ep, dtype=float))
        ep = {str(k): float(v) for k, v in ep_z.dropna().items()}

    src_counts: dict[str, int] = {}
    if mktcap_source_by_id:
        for iid in ids:
            s = mktcap_source_by_id.get(iid, "none")
            src_counts[s] = src_counts.get(s, 0) + 1

    # Process IC over a short window of prior sessions present in close index
    sessions = [d.date() for d in close.index if d.date() <= session]
    if ic_lookback_sessions > 0 and len(sessions) > forward_horizon + 2:
        window = sessions[-(ic_lookback_sessions + forward_horizon) : -forward_horizon]
    else:
        window = []

    ic_rows_m: list[ProcessICRow] = []
    ic_rows_ep: list[ProcessICRow] = []
    for sess in window:
        m12_s, _ = compute_momentum_cross_section(close, sess)
        ep_s, _ = compute_ep_cross_section(
            sess,
            ids,
            float_mktcap,
            roots=roots,
            fin_view=fin_view,
            bs_view=bs_view,
            ep_research_view=ep_research_view,
        )
        fwd = _forward_returns(close, sess, forward_horizon)
        ic_rows_m.append(
            cross_section_ic(m12_s, fwd, session=sess, factor_id="M01_12_1", horizon=forward_horizon)
        )
        ic_rows_ep.append(
            cross_section_ic(ep_s, fwd, session=sess, factor_id="V01_EP", horizon=forward_horizon)
        )

    summaries = (
        summarize_ic(ic_rows_m, "M01_12_1"),
        summarize_ic(ic_rows_ep, "V01_EP"),
    )

    return V2MinPipelineResult(
        session=session,
        universe_ids=tuple(ids),
        max_instruments=max_instruments,
        momentum_raw=m12,
        momentum_3m_raw=m3,
        ep_raw=ep,
        ep_negative_flagged=int(ep_meta.get("negative_e_flagged") or 0),
        ep_coverage=len(ep),
        financials_promotable=False,
        financials_path=str(ep_meta.get("path")) if ep_meta.get("path") else None,
        financials_metric_used=str(ep_meta.get("metric_used")) if ep_meta.get("metric_used") else None,
        mktcap_source_counts=src_counts,
        ic_summaries=summaries,
        promotion_approved=False,
        notes=tuple(notes),
    )


def raw_panels_from_result(result: V2MinPipelineResult) -> tuple[RawFactorPanel, RawFactorPanel]:
    """Typed RawFactorPanel wrappers (Mandate ids M01_12_1 / V01_EP)."""
    assert "M01_12_1" in COMPOSITE_MEMBER_IDS and "V01_EP" in COMPOSITE_MEMBER_IDS
    return (
        RawFactorPanel(
            factor_id="M01_12_1",
            session=result.session,
            values=dict(result.momentum_raw),
            available_at_ok=True,
            notes=("research_merged_panels", "promotion_approved=false"),
        ),
        RawFactorPanel(
            factor_id="V01_EP",
            session=result.session,
            values=dict(result.ep_raw),
            available_at_ok=True,
            notes=(
                "financials_pit_not_promotable",
                f"metric={result.financials_metric_used}",
                "promotion_approved=false",
            ),
        ),
    )



def neutralize_raw_panel(
    raw: RawFactorPanel,
    sw_l1: Sequence,
    *,
    mktcap: Mapping[str, float] | None = None,
    mktcap_neutral: bool = False,
    industry_scheme: str = "SW_L1",
):
    """Hook: SW_L1 (+ optional mktcap) neutralize a RawFactorPanel.

    Thin wrapper over :func:`quantlab.factors.residual_factory.neutralize_raw_values`
    so Eng smoke / research scripts need not instantiate the full factory.
    Returns :class:`ResidualFactorPanel` with ``promotion_approved=False``.
    """
    from quantlab.factors.residual_factory import ResidualFactorPanel, neutralize_raw_values

    values, covered, unknown = neutralize_raw_values(
        raw.values, sw_l1, mktcap=mktcap, mktcap_neutral=mktcap_neutral
    )
    return ResidualFactorPanel(
        factor_id=raw.factor_id,
        session=raw.session,
        industry_scheme=industry_scheme,
        mktcap_neutral=bool(mktcap_neutral) and bool(mktcap),
        values=values,
        sw_l1_coverage=covered,
        unknown_industry_count=unknown,
        promotion_approved=False,
        data_ready=bool(values),
        todos=(
            "sw_l1_research_not_promotable",
            "promotion_approved=false",
            "v2_min_pipeline.neutralize_raw_panel",
        ),
    )


def orthogonalize_raw_pair(
    target: RawFactorPanel,
    control: RawFactorPanel,
):
    """Hook: OLS-residualize ``target`` vs ``control`` (research-only)."""
    from quantlab.factors.orthogonalize import residualize_vs

    return residualize_vs(
        dict(target.values),
        dict(control.values),
        factor_id=target.factor_id,
        control_id=control.factor_id,
        session=target.session,
    )
