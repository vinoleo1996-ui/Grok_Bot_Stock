"""P1 research factor library (STRATEGY RESCUE) — raw cross-sections only.

Families: momentum, reversal, value, quality, low-vol, liquidity.
Always ``promotion_approved=false``. IC/ICIR never computed here.
Amount gaps → waive (omit), never invent.
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np
import pandas as pd

from quantlab.factors.engine import WINSORIZE_LAST_DIAG, winsorize_zscore
from quantlab.factors.neutralize import sector_demean

EPS = 1e-12

# Rank-invariant scale: raw |r|/amount in CNY is ~1e-11; without this,
# winsorize_zscore MAD/std both fall below 1e-9 and used to silent-zero the CS.
AMIHUD_RAW_SCALE: float = 1e9

# Research catalog (extends Mandate composite; not a promotion list)
P1_FACTOR_IDS: tuple[str, ...] = (
    # Momentum
    "M01_12_1",
    "M02_3_1",
    "M03_INDRES_MOM",
    # Reversal
    "R01_5D",
    "R02_20D",
    # Value
    "V01_EP",
    "V02_BP",
    # Quality
    "Q01_profitability",
    "Q01_ROE_STAB",
    "Q03_safety",
    "Q_ACCRUAL_PROXY",
    # Low vol
    "L01_RV60",
    "L02_IDIO_VOL",
    # Liquidity / ESSENCE TURN
    "turn_20d",
    "LIQ01_TOV",
    "LIQ02_AMIHUD",
    # ESSENCE P1-B price-volume (default integrate weight 0 until gate)
    "REV",
    "IVOL",
    "MAX",
)

# Alias → canonical id (ESSENCE scripts/neutral_alpha SIGNALS name)
P1_FACTOR_ALIASES: dict[str, str] = {
    "TURN": "turn_20d",
}

P1_FAMILY: dict[str, str] = {
    "M01_12_1": "momentum",
    "M02_3_1": "momentum",
    "M03_INDRES_MOM": "momentum",
    "R01_5D": "reversal",
    "R02_20D": "reversal",
    "V01_EP": "value",
    "V02_BP": "value",
    "Q01_profitability": "quality",
    "Q01_ROE_STAB": "quality",
    "Q03_safety": "quality",
    "Q_ACCRUAL_PROXY": "quality",
    "L01_RV60": "low_vol",
    "L02_IDIO_VOL": "low_vol",
    "turn_20d": "liquidity",
    "LIQ01_TOV": "liquidity",
    "LIQ02_AMIHUD": "liquidity",
    "REV": "price_volume",
    "IVOL": "price_volume",
    "MAX": "price_volume",
}

# Integrate weights (process-only). Main-book gate-hold at 0 until single-var
# Full D1 contrast passes: REV/IVOL/MAX/L01/L02/LIQ*. turn_20d stays 1.0 only
# so explicit contrast arms (factor_ids includes turn) still integrate it;
# after Full D1 failure prefer weight clamp / industry_size_only — see
# output/alpha/TURN_FAILURE_DIAGNOSIS.md. LIQ01_TOV alias → 0 (no double-count).
# TURN50 product remains rejected.
# MAINBOOK_V2 (Leo 2026-10-10 21:30 ET): members selected from in-sample
# attribution (output/research_attrib_v2/factor_diag.json) — MUST be counted in
# docs/trial_ledger.csv and validated on independent 2018..2024-05 window before
# any conclusion. See output/alpha/MAINBOOK_V2_COMPOSITE.md. M01 removed (still
# computable). LIQ01_TOV duplicates turn_20d → 0. promotion_approved=false.
# Leo 2026-10-10 (~23:00 ET): LIQ02_AMIHUD default weight → 0 (sign conflict +
# scaling bug); stays in MEMBER_IDS for compute/coverage gate; Eng fixed
# winsorize silent-zero (docs/v2/AMIHUD_WINSORIZE_FIX.md); sign still negative.
MAINBOOK_V2_MEMBER_IDS: tuple[str, ...] = (
    "R02_20D",
    "turn_20d",
    "L01_RV60",
    "V02_BP",
    "LIQ02_AMIHUD",
)
P1_DEFAULT_INTEGRATE_WEIGHTS: dict[str, float] = {
    "M01_12_1": 0.0,  # removed from main book V2 (still computable)
    "M02_3_1": 0.0,
    "M03_INDRES_MOM": 0.0,
    "R01_5D": 0.0,
    "R02_20D": 1.0,
    "V01_EP": 0.0,
    "V02_BP": 1.0,
    "Q01_profitability": 0.0,
    "Q01_ROE_STAB": 0.0,
    "Q03_safety": 0.0,
    "Q_ACCRUAL_PROXY": 0.0,
    "L01_RV60": 1.0,
    "L02_IDIO_VOL": 0.0,
    "turn_20d": 1.0,
    "LIQ01_TOV": 0.0,  # alias of turn_20d; do not double-count
    # Leo 2026-10-10: paused at 0 (sign unresolved; Eng scaled ×1e9 + rank fallback).
    # Still computed when in factor_ids; coverage auto-0 gate retained; revive ≠ flip sign here.
    "LIQ02_AMIHUD": 0.0,
    "REV": 0.0,
    "IVOL": 0.0,
    "MAX": 0.0,
}

# Candidates that stay weight-0 in main integrate until Strategy runs a
# single-variable-on arm (see build_single_var_contrast_spec).
P1_SINGLE_VAR_GATE_IDS: tuple[str, ...] = (
    "REV",
    "IVOL",
    "MAX",
    "L01_RV60",
    "L02_IDIO_VOL",
    "LIQ01_TOV",
    "LIQ02_AMIHUD",
    "turn_20d",  # failed Full D1 ols_then_gs equal-weight; re-test via helper
)

# Original-warehouse gate citations (research-only; not V2 promotion evidence)
ESSENCE_TURN_GATE_CITATION: dict[str, object] = {
    "source": "QuantLab-ESSENCE_REUSE_V2.md §1 rank2 + docs/PHASE1_GATE_20261008.md",
    "factor": "TURN / turn_20d",
    "discovery_gate": "pass",
    "ic_t_approx": 10.2,
    "net_excess_cagr_approx": 0.037,
    "incremental_t_approx": 4.5,
    "smb_hml_alpha_t_approx": -0.05,
    "turn50_product": "rejected",
    "promotion_approved": False,
}


def _session_ts(panel: pd.DataFrame, session: date) -> pd.Timestamp | None:
    if panel is None or panel.empty:
        return None
    if pd.Timestamp(session) in panel.index:
        return pd.Timestamp(session)
    idx = panel.index[panel.index <= pd.Timestamp(session)]
    if len(idx) == 0:
        return None
    return idx[-1]


def load_ohlcv_panels(
    instrument_ids: Sequence[str],
    *,
    d0_root: Path,
    asof_extend_dir: Path,
    end_session: date,
    lookback_calendar_days: int = 700,
) -> tuple[dict[str, pd.DataFrame], tuple[str, ...]]:
    """Wide panels: close / amount / turnover / pb_mrq (DatetimeIndex x id).

    Instruments with insufficient close history are skipped. Amount/turnover
    may be all-NaN on asof_extend — callers must waive, not invent.
    Returns (panels, notes).
    """
    from quantlab.data.v2_readers import load_merged_panel

    start = end_session - timedelta(days=lookback_calendar_days)
    buckets: dict[str, dict[str, pd.Series]] = {
        "close": {},
        "amount": {},
        "turnover": {},
        "pb_mrq": {},
        "volume": {},
    }
    amount_waive_ids: list[str] = []
    for iid in instrument_ids:
        view = load_merged_panel(iid, d0_root=d0_root, asof_extend_dir=asof_extend_dir)
        frame = view.frame
        if frame is None or frame.empty or "close" not in frame.columns:
            continue
        et = pd.to_datetime(frame["event_time"]).dt.normalize()
        mask = (et >= pd.Timestamp(start)) & (et <= pd.Timestamp(end_session))
        et = et[mask]
        if len(et) < 30:
            continue
        base = frame.loc[mask].copy()
        base.index = et
        base = base[~base.index.duplicated(keep="last")].sort_index()

        close = pd.to_numeric(base["close"], errors="coerce")
        if close.dropna().shape[0] < 30:
            continue
        buckets["close"][str(iid)] = close

        if "amount" in base.columns:
            amt = pd.to_numeric(base["amount"], errors="coerce")
            # waive if entirely null in window
            if amt.notna().sum() == 0:
                amount_waive_ids.append(str(iid))
            else:
                buckets["amount"][str(iid)] = amt
        else:
            amount_waive_ids.append(str(iid))

        if "turnover" in base.columns:
            tov = pd.to_numeric(base["turnover"], errors="coerce")
            if tov.notna().sum() > 0:
                buckets["turnover"][str(iid)] = tov

        if "pb_mrq" in base.columns:
            pb = pd.to_numeric(base["pb_mrq"], errors="coerce")
            if pb.notna().sum() > 0:
                buckets["pb_mrq"][str(iid)] = pb

        if "volume" in base.columns:
            vol = pd.to_numeric(base["volume"], errors="coerce")
            if vol.notna().sum() > 0:
                buckets["volume"][str(iid)] = vol

    out: dict[str, pd.DataFrame] = {}
    for k, series_map in buckets.items():
        out[k] = pd.DataFrame(series_map).sort_index() if series_map else pd.DataFrame()
    notes = (
        f"amount_waive_n={len(amount_waive_ids)}",
        "amount_gaps_waived_not_invented",
        "promotion_approved=false",
    )
    return out, notes


def _cs_z(
    row: Mapping[str, float] | pd.Series,
    *,
    notes_out: list[str] | None = None,
) -> dict[str, float]:
    s = pd.Series(dict(row), dtype=float) if not isinstance(row, pd.Series) else row.astype(float)
    s = s.replace([np.inf, -np.inf], np.nan).dropna()
    if s.empty:
        return {}
    z, diag = winsorize_zscore(s, return_diag=True)
    if notes_out is not None:
        note = str(diag.get("note") or "")
        mode = str(diag.get("mode") or "")
        if note:
            notes_out.append(f"winsorize_{note}" if not note.startswith("winsorize_") else note)
        elif mode and mode not in ("mad",):
            notes_out.append(f"winsorize_mode={mode}")
    return {str(k): float(v) for k, v in z.dropna().items() if np.isfinite(v)}


def compute_momentum_family(
    close: pd.DataFrame,
    session: date,
    *,
    sector_map: Mapping[str, str] | None = None,
) -> dict[str, dict[str, float]]:
    """M01_12_1, M02_3_1, M03_INDRES_MOM (industry-demeaned 12-1 raw then z)."""
    from quantlab.factors.engine import factor_momentum

    out: dict[str, dict[str, float]] = {
        "M01_12_1": {},
        "M02_3_1": {},
        "M03_INDRES_MOM": {},
    }
    ts = _session_ts(close, session)
    if ts is None or close.empty:
        return out
    moms = factor_momentum(close)
    m12 = moms["momentum_12m1m"]
    m3 = moms["momentum_3m"]
    if ts not in m12.index:
        return out
    row12 = m12.loc[ts].dropna()
    row3 = m3.loc[ts].dropna()
    out["M01_12_1"] = {str(k): float(v) for k, v in row12.items() if np.isfinite(v)}
    out["M02_3_1"] = {str(k): float(v) for k, v in row3.items() if np.isfinite(v)}

    # Industry-residual momentum: demean raw 12-1 (pre-z already z in factor_momentum;
    # re-demean the CS z by sector — equivalent residual mom signal).
    if sector_map and out["M01_12_1"]:
        s = pd.Series(out["M01_12_1"], dtype=float)
        sm = {str(k): sector_map.get(str(k), "UNKNOWN") for k in s.index}
        residual = sector_demean(s, sm)
        out["M03_INDRES_MOM"] = _cs_z(residual)
    return out


def compute_reversal_family(close: pd.DataFrame, session: date) -> dict[str, dict[str, float]]:
    """R01_5D (neg 5d ret), R02_20D (neg 20d ret); higher = stronger reversal bet."""
    out: dict[str, dict[str, float]] = {"R01_5D": {}, "R02_20D": {}}
    ts = _session_ts(close, session)
    if ts is None or close.empty:
        return out
    loc = close.index.get_loc(ts)
    if isinstance(loc, slice):
        loc = loc.start
    if isinstance(loc, np.ndarray):
        loc = int(loc.flat[0])
    row = close.loc[ts]

    def _rev(horizon: int) -> dict[str, float]:
        if loc < horizon:
            return {}
        past = close.iloc[loc - horizon]
        vals = {}
        for col in close.columns:
            a, b = past.get(col), row.get(col)
            if pd.isna(a) or pd.isna(b) or float(a) == 0:
                continue
            # negative return = reversal long signal
            vals[str(col)] = -(float(b) / float(a) - 1.0)
        return _cs_z(vals)

    out["R01_5D"] = _rev(5)
    out["R02_20D"] = _rev(20)
    return out


def compute_bp_from_pb(pb_panel: pd.DataFrame, session: date) -> dict[str, float]:
    """V02_BP ≈ 1 / pb_mrq (research proxy; panel field, not as-filed book)."""
    ts = _session_ts(pb_panel, session)
    if ts is None or pb_panel.empty:
        return {}
    row = pb_panel.loc[ts].dropna()
    vals = {}
    for k, pb in row.items():
        try:
            pbf = float(pb)
        except (TypeError, ValueError):
            continue
        if not np.isfinite(pbf) or pbf <= 0:
            continue
        vals[str(k)] = 1.0 / pbf
    return _cs_z(vals)


def compute_low_vol_family(close: pd.DataFrame, session: date) -> dict[str, dict[str, float]]:
    """L01_RV60 (−ann. realized vol), L02_IDIO_VOL (−idio vol vs EW market)."""
    out: dict[str, dict[str, float]] = {"L01_RV60": {}, "L02_IDIO_VOL": {}}
    ts = _session_ts(close, session)
    if ts is None or close.empty:
        return out
    rets = close.pct_change(fill_method=None)
    # realized vol 60
    vol60 = rets.rolling(60).std() * np.sqrt(252)
    if ts not in vol60.index:
        return out
    row = vol60.loc[ts].dropna()
    out["L01_RV60"] = _cs_z({str(k): -float(v) for k, v in row.items() if np.isfinite(v) and v > 0})

    # idiosyncratic: residual vs cross-sectional EW market return, then 60d std
    mkt = rets.mean(axis=1)
    idio = rets.sub(mkt, axis=0)
    idio_vol = idio.rolling(60).std() * np.sqrt(252)
    if ts in idio_vol.index:
        irow = idio_vol.loc[ts].dropna()
        out["L02_IDIO_VOL"] = _cs_z(
            {str(k): -float(v) for k, v in irow.items() if np.isfinite(v) and v > 0}
        )
    return out


def compute_liquidity_family(
    close: pd.DataFrame,
    amount: pd.DataFrame,
    turnover: pd.DataFrame,
    session: date,
    *,
    window: int = 20,
    min_periods: int | None = None,
) -> tuple[dict[str, dict[str, float]], tuple[str, ...]]:
    """turn_20d / LIQ01_TOV (−mean turnover), LIQ02_AMIHUD (−|ret|/amount).

    ``turn_20d`` is the canonical ESSENCE TURN name (scripts/neutral_alpha.py:
    20d mean turnover, SIGNALS TURN=-1). ``LIQ01_TOV`` is the same definition
    kept for backward compatibility. Amount gaps → waive, never invent.
    """
    notes: list[str] = []
    out: dict[str, dict[str, float]] = {
        "turn_20d": {},
        "LIQ01_TOV": {},
        "LIQ02_AMIHUD": {},
    }
    ts = _session_ts(close, session)
    if ts is None:
        return out, ("no_session",)

    mp = min_periods if min_periods is not None else max(15, window - 5)
    if turnover is not None and not turnover.empty:
        tts = _session_ts(turnover, session)
        if tts is not None:
            tov_ma = turnover.rolling(window, min_periods=mp).mean()
            if tts in tov_ma.index:
                row = tov_ma.loc[tts].dropna()
                # negative direction: low turnover preferred (ESSENCE TURN=-1)
                turned = _cs_z(
                    {str(k): -float(v) for k, v in row.items() if np.isfinite(v)}
                )
                out["turn_20d"] = turned
                out["LIQ01_TOV"] = dict(turned)
                notes.append("turn_20d_canonical_essence_TURN")
                notes.append("LIQ01_TOV_alias_of_turn_20d")
    else:
        notes.append("turnover_panel_empty_waive_turn_20d_LIQ01")

    if amount is None or amount.empty:
        notes.append("amount_panel_empty_waive_LIQ02_AMIHUD")
        return out, tuple(notes)

    ats = _session_ts(amount, session)
    if ats is None:
        notes.append("amount_session_missing_waive_LIQ02")
        return out, tuple(notes)

    rets = close.pct_change(fill_method=None).abs()
    # align
    common_cols = [c for c in close.columns if c in amount.columns]
    if not common_cols:
        notes.append("amount_close_no_overlap_waive_LIQ02")
        return out, tuple(notes)
    # ×1e9 is rank-invariant; keeps MAD/std above winsorize eps when amount is in CNY.
    amihud_daily = (
        rets[common_cols] / (amount[common_cols].replace(0, np.nan) + EPS)
    ) * float(AMIHUD_RAW_SCALE)
    amihud_ma = amihud_daily.rolling(window).mean()
    if ats not in amihud_ma.index:
        notes.append("amihud_session_missing")
        return out, tuple(notes)
    row = amihud_ma.loc[ats]
    waived = int(row.isna().sum())
    vals = {str(k): -float(v) for k, v in row.dropna().items() if np.isfinite(v)}
    out["LIQ02_AMIHUD"] = _cs_z(vals, notes_out=notes)
    notes.append(f"amihud_waived_nulls={waived}")
    notes.append(f"amihud_scaled_x1e9_rank_invariant")
    notes.append("amount_gaps_waived_not_invented")
    # Sign: main-book keeps −|r|/amount (higher = more liquid). Attrib uses +; Leo decides.
    return out, tuple(notes)



def resolve_factor_id(factor_id: str) -> str:
    """Map alias (e.g. TURN) to canonical P1 id."""
    fid = str(factor_id)
    return P1_FACTOR_ALIASES.get(fid, fid)


def compute_essence_pv_family(
    close: pd.DataFrame,
    session: date,
    *,
    window: int = 20,
    min_periods: int | None = None,
) -> tuple[dict[str, dict[str, float]], tuple[str, ...]]:
    """ESSENCE P1-B REV / IVOL / MAX (scripts/neutral_alpha.py semantics).

    Raw definitions match ``Data.raw_signals``; direction from SIGNALS
    (all −1) is applied so higher score = preferred long side after CS z.
    IVOL uses residual std vs equal-weight market only (SMB waived without
    a full float_mktcap panel) — research approx, not BARRA.
    Default integrate weight remains 0 until V2 IC gate is reproduced.
    """
    notes: list[str] = [
        "essence_pv_from_neutral_alpha",
        "default_integrate_weight=0_until_gate",
        "promotion_approved=false",
    ]
    out: dict[str, dict[str, float]] = {"REV": {}, "IVOL": {}, "MAX": {}}
    ts = _session_ts(close, session)
    if ts is None or close.empty:
        return out, ("no_session", *notes)
    loc = close.index.get_loc(ts)
    if isinstance(loc, slice):
        loc = loc.start
    if isinstance(loc, np.ndarray):
        loc = int(loc.flat[0])
    mp = min_periods if min_periods is not None else max(15, window - 5)

    # REV: return from t-21 → t-1 (20 sessions), SIGNALS REV=-1 → negate
    if loc >= 21:
        past = close.iloc[loc - 21]
        prior = close.iloc[loc - 1]
        rev_vals: dict[str, float] = {}
        for col in close.columns:
            a, b = past.get(col), prior.get(col)
            if pd.isna(a) or pd.isna(b) or float(a) == 0:
                continue
            rev_vals[str(col)] = -(float(b) / float(a) - 1.0)
        out["REV"] = _cs_z(rev_vals)
    else:
        notes.append("REV_insufficient_history")

    rets = close.pct_change(fill_method=None)

    # MAX: rolling max daily return over ``window``, SIGNALS MAX=-1 → negate
    max_roll = rets.rolling(window, min_periods=mp).max()
    if ts in max_roll.index:
        row = max_roll.loc[ts].dropna()
        out["MAX"] = _cs_z(
            {str(k): -float(v) for k, v in row.items() if np.isfinite(v)}
        )
    else:
        notes.append("MAX_session_missing")

    # IVOL: residual std of last ``window`` returns vs EW market (+ intercept)
    if loc >= window - 1:
        sl = rets.iloc[loc - window + 1 : loc + 1]
        if len(sl) >= mp:
            mkt = sl.mean(axis=1)
            X = np.column_stack([np.ones(len(sl)), mkt.to_numpy(dtype=float)])
            ivol_vals: dict[str, float] = {}
            if np.isfinite(X).all():
                for col in sl.columns:
                    y = sl[col].to_numpy(dtype=float)
                    if not np.isfinite(y).all():
                        continue
                    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
                    resid = y - X @ beta
                    sd = float(np.std(resid, ddof=min(3, max(1, len(resid) - 1))))
                    if np.isfinite(sd) and sd > 0:
                        ivol_vals[str(col)] = -sd  # SIGNALS IVOL=-1
            out["IVOL"] = _cs_z(ivol_vals) if ivol_vals else {}
            notes.append("IVOL_mkt_only_smb_waived_no_mktcap_panel")
        else:
            notes.append("IVOL_insufficient_history")
    else:
        notes.append("IVOL_insufficient_history")
    return out, tuple(notes)


def compute_quality_from_financials(
    session: date,
    universe_ids: Sequence[str],
    *,
    fin_view=None,
    em_yjbb_frame: pd.DataFrame | None = None,
) -> dict[str, dict[str, float]]:
    """Q01 ROE, Q01_ROE_STAB, Q03_safety (−debt_to_assets), Q_ACCRUAL_PROXY (ocf_to_profit)."""
    from quantlab.data.v2_readers import (
        default_v2_roots,
        financials_metric_asof,
        load_financials_pit,
    )

    out: dict[str, dict[str, float]] = {
        "Q01_profitability": {},
        "Q01_ROE_STAB": {},
        "Q03_safety": {},
        "Q_ACCRUAL_PROXY": {},
    }
    if not universe_ids:
        return out
    roots = default_v2_roots()
    view = fin_view
    if view is None:
        try:
            view = load_financials_pit(roots=roots)
        except FileNotFoundError:
            return out
    if (view.promotable or view.promotion_approved) and getattr(view, "source_variant", "research") != "tushare":
        raise RuntimeError("financials_must_remain_non_promotable")

    roe = financials_metric_asof(
        view.frame, session, universe_ids, "roe", negative_as_missing=False
    )
    out["Q01_profitability"] = _cs_z(roe) if roe else {}

    debt = financials_metric_asof(
        view.frame, session, universe_ids, "debt_to_assets", negative_as_missing=False
    )
    if debt:
        out["Q03_safety"] = _cs_z({k: -float(v) for k, v in debt.items() if np.isfinite(v)})

    ocf = financials_metric_asof(
        view.frame, session, universe_ids, "ocf_to_profit", negative_as_missing=False
    )
    if ocf:
        out["Q_ACCRUAL_PROXY"] = _cs_z(ocf)

    # ROE stability: std of last up-to-8 ROE prints from EM yjbb or fin history
    stab_src = em_yjbb_frame
    if stab_src is None:
        # use full financials history for roe metric
        frame = view.frame
        if frame is not None and not frame.empty:
            sub = frame[frame["metric"].astype(str) == "roe"].copy()
            if universe_ids:
                wanted = set(map(str, universe_ids))
                sub = sub[sub["instrument_id"].astype(str).isin(wanted)]
            if not sub.empty:
                sub["available_at"] = pd.to_datetime(
                    sub["available_at"], errors="coerce", utc=True
                )
                sub = sub[sub["available_at"].notna()]
                try:
                    ad = sub["available_at"].dt.tz_convert("Asia/Shanghai").dt.date
                except (TypeError, AttributeError):
                    ad = sub["available_at"].dt.tz_localize(None).dt.date
                sub = sub.assign(_ad=ad)
                sub = sub[sub["_ad"] <= session]
                stab = {}
                for iid, g in sub.groupby("instrument_id"):
                    g = g.sort_values("available_at").tail(8)
                    vals = pd.to_numeric(g["value"], errors="coerce").dropna()
                    if len(vals) >= 3:
                        sd = float(vals.std(ddof=1))
                        if np.isfinite(sd):
                            stab[str(iid)] = -sd  # lower dispersion better
                out["Q01_ROE_STAB"] = _cs_z(stab) if stab else {}
    else:
        # EM path: roe column, available_at
        sub = stab_src.copy()
        if universe_ids:
            wanted = set(map(str, universe_ids))
            sub = sub[sub["instrument_id"].astype(str).isin(wanted)]
        if "roe" in sub.columns and "available_at" in sub.columns:
            sub["available_at"] = pd.to_datetime(sub["available_at"], errors="coerce", utc=True)
            sub = sub[sub["available_at"].notna()]
            try:
                ad = sub["available_at"].dt.tz_convert("Asia/Shanghai").dt.date
            except (TypeError, AttributeError):
                ad = pd.to_datetime(sub["available_at"], utc=True).dt.tz_localize(None).dt.date
            sub = sub.assign(_ad=ad)
            sub = sub[sub["_ad"] <= session]
            stab = {}
            for iid, g in sub.groupby("instrument_id"):
                g = g.sort_values("available_at").tail(8)
                vals = pd.to_numeric(g["roe"], errors="coerce").dropna()
                if len(vals) >= 3:
                    sd = float(vals.std(ddof=1))
                    if np.isfinite(sd):
                        stab[str(iid)] = -sd
            out["Q01_ROE_STAB"] = _cs_z(stab) if stab else {}
    return out
