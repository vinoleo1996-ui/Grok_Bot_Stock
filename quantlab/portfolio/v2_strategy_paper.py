"""Research-grade Strategy paper v1 — first NAV / returns curve.

Uses Eng ``quantlab.platform.strategy_feed`` + Beta sleeve + Alpha M01/EP
factory + PortfolioConstructorV2. ``promotion_approved=false`` always.

Outputs under ``output/strategy_paper_v1/`` only.

Reproduce::

    cd /workspace/QuantLab
    PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.portfolio.v2_strategy_paper
"""
from __future__ import annotations

from quantlab.promotion_gate import overall_promotion_approved as _gate

import json
import math
import time
from dataclasses import asdict
from datetime import date, timedelta
from pathlib import Path
from typing import Mapping

import numpy as np
import pandas as pd

from quantlab.beta import VolTargetBetaSleeveProvider
from quantlab.data.v2_readers import default_v2_roots, load_ep_research, load_sw_l1_members
from quantlab.factors.residual_factory import ResearchResidualAlphaFactorFactory
from quantlab.factors.v2_min_pipeline import compute_momentum_cross_section
from quantlab.mandate_v2 import load_mandate_v2
from quantlab.platform.strategy_feed import (
    DEFAULT_PAPER_START_FAST,
    STRATEGY_PAPER_V1_OUTPUT_DIR,
    biweekly_rebalance_sessions,
    d1_members_at,
    etf_510300_daily_returns,
    merged_close_panel,
    merged_daily_returns,
    trading_sessions,
)
from quantlab.portfolio.v2_constructor import PortfolioConstructorV2
from quantlab.universe.d1_masks import D1MaskConfig
from quantlab.v2_schemas import SWL1AsOfAssignment


# --- research knobs (documented in LIMITATIONS / summary) ---
PAPER_START = DEFAULT_PAPER_START_FAST  # 2024-06-01
# None = latest tradeable from merged calendar ∩ ETF 510300 (do not hard-stop at D0 2026-06-30).
PAPER_END: date | None = None
CANDIDATE_POOL = 250  # D1 max_instruments sample (full-universe too slow)
# pool=250 is an internal smoke/iteration shortcut — NOT an external / Full-D1 claim.
PAPER_RUN_TIER = "smoke_iteration_pool250"
LOOKBACK_CALENDAR_DAYS = 420  # room for M01_12_1


def resolve_paper_end(
    *,
    start: date = PAPER_START,
    end: date | None = PAPER_END,
    roots=None,
) -> date:
    """Pick research paper end from live data (never invent past calendar/ETF).

    Uses Eng ``trading_sessions(start, end=None)`` last session, then clips to
    ETF 510300 ``date_max`` when that is earlier. Documents provenance via
    returned date only — callers record sources in summary.
    """
    from quantlab.data.v2_readers import load_etf_510300

    roots = roots or default_v2_roots()
    if end is not None:
        sessions = trading_sessions(start, end, roots=roots)
        if not sessions:
            raise RuntimeError(f"no_trading_sessions_in_window:{start}->{end}")
        return sessions[-1]

    sessions = trading_sessions(start, None, roots=roots)
    if not sessions:
        raise RuntimeError("no_trading_sessions_from_merged_calendar")
    cal_last = sessions[-1]

    etf = load_etf_510300(roots=roots)
    etf_last = etf.date_max
    if etf_last is None:
        return cal_last
    if isinstance(etf_last, str):
        etf_last = date.fromisoformat(str(etf_last)[:10])
    elif hasattr(etf_last, "date") and not isinstance(etf_last, date):
        etf_last = etf_last.date()  # type: ignore[assignment]
    return min(cal_last, etf_last)


def _ensure_out() -> Path:
    out = Path(STRATEGY_PAPER_V1_OUTPUT_DIR)
    out.mkdir(parents=True, exist_ok=True)
    return out


def _candidate_pool(n: int, roots) -> list[str]:
    """First N stock ids that have a D0 panel file (deterministic sample)."""
    inst = pd.read_parquet(roots.d0_root / "instruments.parquet")
    panel_dir = roots.d0_root / "panels"
    ids: list[str] = []
    for iid in inst["instrument_id"].astype(str).tolist():
        if (panel_dir / f"{iid}.parquet").is_file():
            ids.append(iid)
        if len(ids) >= n:
            break
    return ids


def _close_panel_to_ts_index(close: pd.DataFrame) -> pd.DataFrame:
    """Factory / momentum helpers expect DatetimeIndex."""
    if close.empty:
        return close
    out = close.copy()
    out.index = pd.to_datetime(out.index)
    out.index.name = "event_time"
    return out.sort_index()


def _sw_assignments_from_frame(frame: pd.DataFrame, session: date) -> list[SWL1AsOfAssignment]:
    out: list[SWL1AsOfAssignment] = []
    if frame is None or frame.empty:
        return out
    for _, r in frame.iterrows():
        iid = str(r["instrument_id"])
        unknown = bool(r.get("industry_sw_l1_unknown", True))
        code = r.get("industry_sw_l1_code")
        name = r.get("industry_sw_l1_name")
        code_s = None if code is None or (isinstance(code, float) and math.isnan(code)) else str(code)
        name_s = None if name is None or (isinstance(name, float) and math.isnan(name)) else str(name)
        qs = r.get("industry_sw_l1_quality")
        qs_s = None if qs is None or (isinstance(qs, float) and math.isnan(qs)) else str(qs)
        out.append(
            SWL1AsOfAssignment(
                instrument_id=iid,
                session=session,
                sw_code=None if unknown else code_s,
                sw_name=None if unknown else name_s,
                available_at=None,
                quality_status=qs_s,
                is_unknown_bucket=unknown or not code_s,
            )
        )
    return out


def _industry_labels(frame: pd.DataFrame) -> dict[str, str]:
    labels: dict[str, str] = {}
    if frame is None or frame.empty:
        return labels
    for _, r in frame.iterrows():
        iid = str(r["instrument_id"])
        if bool(r.get("industry_sw_l1_unknown", True)):
            labels[iid] = "UNKNOWN"
        else:
            code = r.get("industry_sw_l1_code")
            labels[iid] = str(code) if code is not None and str(code) != "nan" else "UNKNOWN"
    return labels


def _fm_map(frame: pd.DataFrame) -> dict[str, float]:
    out: dict[str, float] = {}
    if frame is None or frame.empty:
        return out
    for _, r in frame.iterrows():
        iid = str(r["instrument_id"])
        v = r.get("float_mktcap")
        if v is None or (isinstance(v, float) and (math.isnan(v) or not math.isfinite(v))):
            continue
        try:
            fv = float(v)
        except (TypeError, ValueError):
            continue
        if fv == fv and math.isfinite(fv) and fv > 0:
            out[iid] = fv
    return out


def _integrate_scores(m01: Mapping[str, float], ep: Mapping[str, float]) -> dict[str, float]:
    """Equal-weight CS z integrate of available members (research stub)."""
    from quantlab.factors.engine import winsorize_zscore

    panels = []
    if m01:
        panels.append(winsorize_zscore(pd.Series(dict(m01), dtype=float)).rename("M01_12_1"))
    if ep:
        panels.append(winsorize_zscore(pd.Series(dict(ep), dtype=float)).rename("V01_EP"))
    if not panels:
        return {}
    stacked = pd.concat(panels, axis=1)
    s = stacked.mean(axis=1, skipna=True).dropna()
    return {str(k): float(v) for k, v in s.items() if np.isfinite(v)}


def _metrics(nav: pd.Series, daily_ret: pd.Series, turnovers: list[float]) -> dict:
    nav = nav.dropna()
    rets = daily_ret.reindex(nav.index).dropna()
    n = int(len(rets))
    if n < 2 or nav.empty:
        return {
            "cagr": None,
            "sharpe_rf0": None,
            "max_drawdown": None,
            "n_days": n,
            "date_start": None,
            "date_end": None,
        }
    start_nav = float(nav.iloc[0])
    end_nav = float(nav.iloc[-1])
    from quantlab.metrics import PERIODS as _QP
    years = n / float(_QP)
    cagr = (end_nav / start_nav) ** (1.0 / years) - 1.0 if years > 0 and start_nav > 0 else None
    mu = float(rets.mean())
    sig = float(rets.std(ddof=1)) if n > 1 else float("nan")
    sharpe = (mu / sig) * math.sqrt(float(_QP)) if sig and sig > 1e-12 else None
    peak = nav.cummax()
    dd = nav / peak - 1.0
    max_dd = float(dd.min())
    return {
        "cagr": None if cagr is None else float(cagr),
        "sharpe_rf0": None if sharpe is None else float(sharpe),
        "max_drawdown": max_dd,
        "n_days": n,
        "date_start": str(nav.index[0]),
        "date_end": str(nav.index[-1]),
        "total_return": float(end_nav / start_nav - 1.0),
        "ann_vol": float(sig * math.sqrt(float(_QP))) if sig == sig else None,
        "turnover_one_way_mean_per_rebalance": float(np.mean(turnovers)) if turnovers else None,
        "n_rebalances": len(turnovers),
        "risk_free_assumed": 0.0,
        "sharpe_note": "rf=0 research convention; not a promotion metric",
    }


def _plot_nav(nav: pd.Series, path: Path) -> bool:
    """Write nav.png (matplotlib if present; else minimal pure-Python PNG)."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 4.5))
        x = pd.to_datetime(nav.index)
        ax.plot(x, nav.values, color="#1f4e79", lw=1.4, label="Strategy paper v1 (research)")
        ax.set_title("QuantLab Strategy paper v1 NAV (research-only, promotion_approved=false)")
        ax.set_ylabel("NAV (start=1.0)")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper left")
        fig.autofmt_xdate()
        fig.tight_layout()
        fig.savefig(path, dpi=120)
        plt.close(fig)
        return True
    except Exception:
        return _plot_nav_png_fallback(nav, path)


def _plot_nav_png_fallback(nav: pd.Series, path: Path) -> bool:
    """Minimal RGB PNG line chart (no external deps)."""
    import struct
    import zlib

    vals = [float(v) for v in nav.values if v == v]
    if len(vals) < 2:
        return False
    w, h = 900, 360
    pad_l, pad_r, pad_t, pad_b = 50, 20, 30, 40
    ymin, ymax = min(vals), max(vals)
    if abs(ymax - ymin) < 1e-12:
        ymax = ymin + 1e-6
    xs = list(range(len(vals)))

    def px(i, v):
        x = pad_l + int((i / (len(vals) - 1)) * (w - pad_l - pad_r))
        y = pad_t + int((1.0 - (v - ymin) / (ymax - ymin)) * (h - pad_t - pad_b))
        return x, y

    # white background
    img = bytearray([255, 255, 255] * (w * h))

    def set_px(x, y, rgb=(31, 78, 121)):
        if 0 <= x < w and 0 <= y < h:
            o = (y * w + x) * 3
            img[o : o + 3] = bytes(rgb)

    def line(x0, y0, x1, y1, rgb=(31, 78, 121)):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for s in range(steps + 1):
            t = s / steps
            set_px(int(x0 + t * (x1 - x0)), int(y0 + t * (y1 - y0)), rgb)

    # axes
    line(pad_l, pad_t, pad_l, h - pad_b, (180, 180, 180))
    line(pad_l, h - pad_b, w - pad_r, h - pad_b, (180, 180, 180))
    # series
    pts = [px(i, v) for i, v in enumerate(vals)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        line(x0, y0, x1, y1)
        set_px(x0, y0)
    set_px(*pts[-1])

    # pack PNG
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = b"".join(b"\x00" + bytes(img[y * w * 3 : (y + 1) * w * 3]) for y in range(h))
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    path.write_bytes(png)
    # also SVG for readability
    svg_path = path.with_suffix(".svg")
    poly = " ".join(f"{x},{y}" for x, y in pts)
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">'
        f'<rect width="100%" height="100%" fill="white"/>'
        f'<polyline fill="none" stroke="#1f4e79" stroke-width="2" points="{poly}"/>'
        f'<text x="12" y="20" font-size="14" fill="#333">Strategy paper v1 NAV (research, promotion_approved=false)</text>'
        f"</svg>"
    )
    svg_path.write_text(svg, encoding="utf-8")
    return True


def run_paper(
    *,
    start: date = PAPER_START,
    end: date | None = PAPER_END,
    candidate_pool: int = CANDIDATE_POOL,
    out_dir: Path | None = None,
) -> dict:
    t_wall0 = time.time()
    out = Path(out_dir) if out_dir else _ensure_out()
    out.mkdir(parents=True, exist_ok=True)

    mandate = load_mandate_v2()
    mandate.require_not_promoted()
    if bool(mandate.promotion_approved) != _gate():
        raise RuntimeError("mandate_promotion_approved_gate_mismatch")

    roots = default_v2_roots()
    pool = _candidate_pool(candidate_pool, roots)
    cfg = D1MaskConfig(open_status_mode="research", waive_u30_on_amount_gap=True)

    # Resolve end from data (calendar ∩ ETF); do not invent.
    from quantlab.data.v2_readers import load_etf_510300, load_merged_calendar

    cal_view = load_merged_calendar(roots=roots)
    etf_bundle = load_etf_510300(roots=roots)
    end = resolve_paper_end(start=start, end=end, roots=roots)
    d0_cutoff = date(2026, 6, 30)
    post_d0 = end > d0_cutoff
    end_provenance = {
        "resolved_end": str(end),
        "merged_calendar_last_session": str(cal_view.last_session) if cal_view.last_session else None,
        "etf_510300_date_max": str(etf_bundle.date_max) if etf_bundle.date_max else None,
        "d0_panel_merge_cutoff": str(d0_cutoff),
        "extends_past_d0_cutoff": post_d0,
        "hard_stop_at_d0": False,
        "note": "end = min(merged calendar last, ETF 510300 date_max) unless caller passed explicit end",
    }
    print(f"[paper] resolved end={end} provenance={end_provenance}", flush=True)

    sessions = trading_sessions(start, end, roots=roots)
    rebal_dates = biweekly_rebalance_sessions(start, end, mandate=mandate, roots=roots)
    if not sessions or not rebal_dates:
        raise RuntimeError("no_sessions_or_rebalances_in_window")

    # Preload panels with momentum lookback
    load_start = start - timedelta(days=LOOKBACK_CALENDAR_DAYS)
    print(f"[paper] preload close panel pool={len(pool)} {load_start}→{end}", flush=True)
    t0 = time.time()
    closes_raw = merged_close_panel(pool, load_start, end, roots=roots)
    stock_rets = merged_daily_returns(pool, load_start, end, roots=roots, close_panel=closes_raw)
    etf_rets = etf_510300_daily_returns(load_start, end, roots=roots)
    print(f"[paper] panels ready shape={closes_raw.shape} in {time.time()-t0:.1f}s", flush=True)

    close_ts = _close_panel_to_ts_index(closes_raw)

    try:
        ep_view = load_ep_research(roots=roots)
    except FileNotFoundError:
        ep_view = None

    factory = ResearchResidualAlphaFactorFactory(
        mandate=mandate,
        close_panel=close_ts,
        ep_research_view=ep_view,
        d0_root=roots.d0_root,
        asof_extend_dir=roots.asof_extend_dir,
    )
    constructor = PortfolioConstructorV2(mandate)
    beta = VolTargetBetaSleeveProvider(mandate, d0_root=roots.d0_root)

    # Holdings state (portfolio weights sum to <=1; cash absorbs rest)
    etf_w = 0.0
    cash_w = 1.0
    stock_w: dict[str, float] = {}
    last_rebal: date | None = None
    turnovers: list[float] = []
    rebal_log: list[dict] = []

    daily_rows: list[dict] = []
    nav = 1.0
    nav_rows: list[dict] = []

    rebal_set = set(rebal_dates)
    sess_in_window = [d for d in sessions if start <= d <= end]

    for i, sess in enumerate(sess_in_window):
        # Mark-to-market FIRST using prior weights (earn sess-1 → sess return)
        # Skip first day (no prior return). Research: close-to-close; no T+1 lag fill.
        if i > 0:
            prev = sess_in_window[i - 1]
            # stock contribution
            book_ret = 0.0
            for iid, w in stock_w.items():
                if w <= 0:
                    continue
                if iid in stock_rets.columns and sess in stock_rets.index:
                    r = stock_rets.at[sess, iid]
                    if r == r and math.isfinite(float(r)):
                        book_ret += float(w) * float(r)
                # missing return → 0 contribution (documented)
            etf_r = 0.0
            if etf_w > 0 and sess in etf_rets.index:
                er = etf_rets.loc[sess]
                if er == er and math.isfinite(float(er)):
                    etf_r = float(etf_w) * float(er)
            # cash ret = 0
            day_ret = book_ret + etf_r
            nav *= 1.0 + day_ret
            daily_rows.append(
                {
                    "date": str(sess),
                    "daily_ret": day_ret,
                    "nav": nav,
                    "etf_w": etf_w,
                    "cash_w": cash_w,
                    "residual_book_w": float(sum(stock_w.values())),
                    "n_names": len(stock_w),
                    "rebalance": sess in rebal_set,
                }
            )
            nav_rows.append({"date": str(sess), "nav": nav, "daily_ret": day_ret})
        else:
            daily_rows.append(
                {
                    "date": str(sess),
                    "daily_ret": 0.0,
                    "nav": nav,
                    "etf_w": etf_w,
                    "cash_w": cash_w,
                    "residual_book_w": 0.0,
                    "n_names": 0,
                    "rebalance": sess in rebal_set,
                }
            )
            nav_rows.append({"date": str(sess), "nav": nav, "daily_ret": 0.0})

        if sess not in rebal_set:
            continue

        # --- rebalance ---
        print(f"[paper] rebalance {sess} nav={nav:.4f}", flush=True)
        d1 = d1_members_at(
            sess,
            instrument_ids=pool,
            config=cfg,
            roots=roots,
            return_result=True,
        )
        assert not isinstance(d1, tuple)
        if d1.promotion_approved:
            raise RuntimeError("d1_promotion_approved_leak")
        members = list(d1.member_ids)
        frame = d1.frame
        # keep only members that passed mask (frame may include non-members)
        if not frame.empty and "instrument_id" in frame.columns:
            mem_set = set(members)
            frame = frame[frame["instrument_id"].astype(str).isin(mem_set)].copy()

        fm = _fm_map(frame)
        factory.float_mktcap = fm
        sw = _sw_assignments_from_frame(frame, sess)
        labels = _industry_labels(frame)

        # Alpha M01 + EP via factory (same compute as min pipeline; no IC)
        raw_m01 = factory.compute_raw(sess, "M01_12_1", members)
        raw_ep = factory.compute_raw(sess, "V01_EP", members)
        res_m01 = factory.neutralize(raw_m01, sw, mktcap=fm or None)
        res_ep = factory.neutralize(raw_ep, sw, mktcap=fm or None)
        composite = factory.integrate([res_m01, res_ep])
        scores = dict(composite.scores)
        if not scores:
            # fallback: raw equal-weight z without neutralize
            scores = _integrate_scores(raw_m01.values, raw_ep.values)

        plan = beta.plan(sess)
        if plan.promotion_approved:
            raise RuntimeError("beta_promotion_approved_leak")
        etf_target = float(plan.etf_sleeve_weight or 0.0)
        cash_target = float(plan.cash_weight or 0.0)
        book_cap = float(plan.residual_book_weight_cap if plan.residual_book_weight_cap is not None else max(0.0, 1.0 - etf_target - cash_target))

        prior_book = dict(stock_w)
        # Constructor produces residual-book weights summing to <= book_cap
        result = constructor.construct(
            scores,
            session=sess,
            industry_labels=labels,
            prior_weights=prior_book if prior_book else None,
            universe=members,
            book_weight_cap=book_cap,
        )
        if result.promotion_approved:
            raise RuntimeError("constructor_promotion_approved_leak")

        stock_w = {k: float(v) for k, v in result.weights.items() if float(v) > 1e-12}
        book_sum = float(sum(stock_w.values()))
        # Reconcile cash: mandate cash + unused book room
        etf_w = etf_target
        cash_w = max(0.0, 1.0 - etf_w - book_sum)
        turnovers.append(float(result.turnover_one_way))
        last_rebal = sess

        rebal_log.append(
            {
                "session": str(sess),
                "n_d1_members": len(members),
                "n_scores": len(scores),
                "n_names": result.n_names,
                "method": result.method,
                "etf_w": etf_w,
                "cash_w": cash_w,
                "residual_book_w": book_sum,
                "book_cap": book_cap,
                "turnover_one_way": result.turnover_one_way,
                "turnover_clipped": result.turnover_clipped,
                "drawdown_tier": plan.drawdown_tier,
                "implied_sleeve_beta": plan.implied_sleeve_beta,
                "beta_gap_to_mandate": plan.beta_gap_to_mandate,
                "residual_beta_budget_for_strategy": plan.residual_beta_budget_for_strategy,
                "implied_beta_in_band": plan.implied_beta_in_band,
                "promotion_approved": False,
            }
        )

    nav_df = pd.DataFrame(nav_rows)
    ret_df = pd.DataFrame(daily_rows)

    nav_series = pd.Series(nav_df["nav"].values, index=nav_df["date"].values)
    ret_series = pd.Series(nav_df["daily_ret"].values, index=nav_df["date"].values)
    metrics = _metrics(nav_series, ret_series, turnovers)

    summary = {
        "title": "QuantLab Strategy paper v1 — research NAV",
        "promotion_approved": False,
        "research_only": True,
        "not_expected_return": True,
        "not_a_promotion_gate": True,
        "window": {"start": str(start), "end": str(end)},
        "end_provenance": end_provenance,
        "post_d0_extend": {
            "active": post_d0,
            "d0_cutoff": str(d0_cutoff),
            "u30_waive_on_amount_gap": True,
            "float_mktcap_late_thin": True,
            "ep_asof_stale_carry": True,
            "index_beta_overlap_ends": "2026-06-30",
            "index_beta_note": "D0 index sh.000300 ends 2026-06-30; Beta late sessions use trailing overlap (research)",
        },
        "candidate_pool": candidate_pool,
        "run_tier": PAPER_RUN_TIER,
        "external_claim": False,
        "full_d1": False,
        "smoke_iteration_note": (
            "candidate_pool=250 is smoke/iteration only; not Full D1 / not external-facing. "
            "Roadmap next after latest-date extend: B costs+limit-up/halt (not Full D1 yet). "
            "max_etf not raised."
        ),
        "n_pool_ids": len(pool),
        "n_trading_sessions": len(sess_in_window),
        "n_rebalances": len(rebal_log),
        "marking": "close_to_close_prior_weights; no_Tplus1_lag; no_limit_up_fill; missing_bar_ret=0",
        "alpha": {
            "members": ["M01_12_1", "V01_EP"],
            "path": "ResearchResidualAlphaFactorFactory compute_raw→neutralize(SW_L1)→integrate",
            "ep_source": str(getattr(ep_view, "path", None)) if ep_view else None,
            "financials_promotable": False,
            "ep_asof_stale_carry": True,
        },
        "beta": {
            "provider": "VolTargetBetaSleeveProvider",
            "benchmark": "510300",
            "max_etf_not_raised": True,
        },
        "d1": {
            "api": "d1_members_at / build_d1_masks_for_session",
            "open_status_mode": "research",
            "waive_u30_on_amount_gap": True,
            "sw_l1_promotable": False,
        },
        "metrics_research_only": metrics,
        "rebalance_log_tail": rebal_log[-5:],
        "wall_seconds": round(time.time() - t_wall0, 1),
        "reproduce": (
            "cd /workspace/QuantLab && "
            "PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.portfolio.v2_strategy_paper"
        ),
        "output_dir": str(out.resolve()),
    }

    nav_path = out / "nav.csv"
    ret_path = out / "returns.csv"
    summary_path = out / "summary.json"
    nav_df.to_csv(nav_path, index=False)
    ret_df.to_csv(ret_path, index=False)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "rebalance_log.json").write_text(
        json.dumps(rebal_log, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    png_ok = _plot_nav(nav_series, out / "nav.png")
    summary["nav_png"] = bool(png_ok)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    _write_limitations_zh(out, summary)
    _write_leo_report_zh(out, summary)
    _write_readme(out, summary)

    print(json.dumps({"ok": True, "metrics": metrics, "out": str(out)}, ensure_ascii=False), flush=True)
    return summary


def _write_limitations_zh(out: Path, summary: dict) -> None:
    m = summary.get("metrics_research_only") or {}
    prov = summary.get("end_provenance") or {}
    post = summary.get("post_d0_extend") or {}
    text = f"""# 研究级局限说明（Strategy paper v1）

**硬约束：`promotion_approved=false`。下列数字仅为研究过程度量，不是预期收益，不是晋升门。**

## 本跑次窗口

- 区间：{summary['window']['start']} → {summary['window']['end']}
- **终点来自数据（未发明）**：merged calendar last=`{prov.get('merged_calendar_last_session')}`；ETF 510300 date_max=`{prov.get('etf_510300_date_max')}`；取交集后 `resolved_end={prov.get('resolved_end')}`（不再硬停在 D0 `{prov.get('d0_panel_merge_cutoff')}`）
- 候选池：`max_instruments={summary['candidate_pool']}` —— **smoke/iteration 内部迭代，非对外口径，非 Full D1**（全市场逐券过慢；有偏采样）
- 下一路线（Leo 锁定）：本跑先接到最新数据；**下一项是 B：成本 + 涨停/停牌**，暂不升 Full D1；**不抬 max_etf**
- 再平衡：Mandate 双周（约每 10 个交易日），`RebalanceScheduleV2`
- 打标：收盘价到收盘价；**未**模拟 T+1 成交/涨停买不进；缺 bar 收益按 0

## 数据与因子

1. **EP asof 陈旧**：`ep_research_asof_20260630.parquet`，2026-06-30 之后仍研究级 **stale-carry**；`financials_promotable=false`
2. **SW_L1 非晋升级**：行业中性化用 prefix 重建；`sw_l1_promotable=false`
3. **asof_extend amount 稀疏 / U30 waive**：晚盘（>{prov.get('d0_panel_merge_cutoff')}）大量 amount 缺口；`open_status_mode=research` + `waive_u30_on_amount_gap=True`，流动性过滤偏松，宇宙偏宽
4. **float_mktcap 晚盘更薄**：日频 seed（`float_mktcap_daily_20260630_20261009`）覆盖子集；池内 session hits 远少于 D0 段，微盘剔除不稳定，常靠 stale asof carry
5. **指数 β overlap 止于 2026-06-30**：D0 指数 `sh.000300` 面板止于该日；其后 Beta 用 trailing overlap 估计 unit β（研究级，非完整 PIT）
6. **除权 gaps**：公司行为预热未闭合；价格收益可能含未调整噪声
7. **合成 vs PIT**：面板为 D0+asof_extend merge 研究路径，非完整 PIT 账本
8. **Alpha 仅 M01_12_1 + V01_EP**：V02/Q*/L01 仍 stub；IC/ICIR 未用作门
9. **LW 优化未实现**：`PortfolioConstructorV2` 为 score-rank / equal stub
10. **Mandate β 张力**：`max_etf` 未上调；袖套隐含 β 常低于 0.70，残差 β 归 Strategy；Beta 回撤档（L1–L4）会压 ETF 权重
11. **成本/冲击未计入**：无佣金、无滑点、无印花税
12. **post_d0_extend.active={post.get('active')}**：晚盘段仍纳入 NAV，但质量低于 D0 段，**不可晋升**

## 指标口径

- CAGR / Sharpe(rf=0) / 最大回撤：由本跑 NAV 实算
- **禁止**把这些数字当作实盘期望或晋升证据

生成墙钟约 {summary.get('wall_seconds')}s。复现命令见 `LEO_REPORT_ZH.md` / `README.md`。
"""
    (out / "LIMITATIONS_ZH.md").write_text(text, encoding="utf-8")


def _write_leo_report_zh(out: Path, summary: dict) -> None:
    m = summary.get("metrics_research_only") or {}

    def pct(x):
        if x is None:
            return "n/a"
        return f"{100.0 * float(x):.2f}%"

    def num(x):
        if x is None:
            return "n/a"
        return f"{float(x):.3f}"

    text = f"""# Leo 短报素材 — Strategy paper v1（研究级）

**promotion_approved=false。数字仅作研究，不是预期收益 / 不是晋升。**

## 关键数字（实算）

| 项 | 值 |
|----|----|
| 区间 | {m.get('date_start')} → {m.get('date_end')} |
| 交易日数 | {m.get('n_days')} |
| 再平衡次数 | {m.get('n_rebalances')} |
| 累计收益 | {pct(m.get('total_return'))} |
| 年化 CAGR | {pct(m.get('cagr'))} |
| 夏普 Sharpe (rf=0) | {num(m.get('sharpe_rf0'))} |
| 最大回撤 | {pct(m.get('max_drawdown'))} |
| 年化波动 | {pct(m.get('ann_vol'))} |
| 单次再平衡换手(单向均值) | {num(m.get('turnover_one_way_mean_per_rebalance'))} |

## 路径

- NAV：`{out / 'nav.csv'}`
- 日收益：`{out / 'returns.csv'}`
- 摘要：`{out / 'summary.json'}`
- 图：`{out / 'nav.png'}`
- 局限：`{out / 'LIMITATIONS_ZH.md'}`

## 复现

```bash
cd /workspace/QuantLab
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.portfolio.v2_strategy_paper
```

## 一句话局限

终点取自 calendar∩ETF（本跑 `{summary['window']['end']}`，非硬停 D0）；**pool={summary['candidate_pool']} 为 smoke/iteration，非对外/非 Full D1**；晚盘 float 薄 + U30 waive；EP asof stale-carry；指数 β overlap 止于 2026-06-30；SW_L1/财务不可晋升；无成本（下一项 B）；β 袖套受 max_etf/回撤档约束（不抬 max_etf）；LW 未上。
"""
    (out / "LEO_REPORT_ZH.md").write_text(text, encoding="utf-8")


def _write_readme(out: Path, summary: dict) -> None:
    text = f"""# Strategy paper v1 (research)

`promotion_approved=false`. Metrics are research-only.

## Reproduce

```bash
cd /workspace/QuantLab
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.portfolio.v2_strategy_paper
```

## Outputs

- `nav.csv` / `returns.csv` / `summary.json` / `nav.png`
- `LIMITATIONS_ZH.md` / `LEO_REPORT_ZH.md`
- `rebalance_log.json`

Window: {summary['window']['start']} → {summary['window']['end']}; pool={summary['candidate_pool']} (smoke/iteration, not Full D1 / not external).
"""
    (out / "README.md").write_text(text, encoding="utf-8")


def main() -> None:
    run_paper()


if __name__ == "__main__":
    main()
