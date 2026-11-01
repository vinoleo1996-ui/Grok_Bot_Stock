#!/usr/bin/env python3
"""STOCK-DISC-EARLY (V34) leaf wiring scaffold.

Leaves:
  disc_early_flag  — 同 end_date 同伴 available_at 中位以下（首次披露）；主仓事件旗
  disc_late_flag   — 同 end_date 同伴 available_at ≥ 中位（敏感性对照；非主仓）

Universe: CSI300∪CSI500；X1 缺权用 float top800；滤 ST / 价<2 / 停牌；禁小盘。

PIT (hard):
  available_at from financials_available_at_tushare（报告日 18:00 Asia/Shanghai）
  → 下一开盘可交易；持有窗 K=10 交易日锚 pit 入日；不可前移。
  每个 (instrument_id, end_date) 取首次 available_at；重述行按新 aa 再判，不回改历史首次入日。
  早披露：aa < 同 end_date 中大盘同伴中位数。

Coverage (honest):
  X1 2015-06→2017-12 ∩ float top800 ∧ aa < 同 end_date 中位：
    3664 行 / 1057 只 / 18 end_date 簇 → coverage_ok (NOT blocked).
  Source: data/v2/financials_pit/financials_available_at_tushare.parquet

promotion_approved=False.
Does NOT run NAV / backtest / GP / v27 / SEARCH / smoke.
Scaffold + inventory only; Beta owns the X1 pretest run.
Does NOT touch V31 stock_index_rebal package.
Does NOT grind 分红/DY / ocf·应计·质量 / seat / 解禁 / ETF tercile / 价叶.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/workspace/QuantLab")
V2 = ROOT / "data/v2"
SRC = V2 / "financials_pit/financials_available_at_tushare.parquet"
FLOAT_SRC = V2 / "float_mktcap/float_mktcap_daily_from2015_tushare.parquet"
OUT_DIR = ROOT / "output/ai_factor/stock_disc_early_v34"
DOC = ROOT / "docs/v2/AI_DISC_EARLY_WIRING_RECEIPT_ZH.md"

LEAF_NAMES = ["disc_early_flag", "disc_late_flag"]
K_HOLD = 10
N_NAMES = 25
X1_START = pd.Timestamp("2015-06-01")
X1_END = pd.Timestamp("2017-12-31")
BALLAST = "sh.510300"
FLOAT_LOOKBACK_CAL_DAYS = 3  # ≤3 calendar days align to float top800


def _normalize_avail(series: pd.Series) -> pd.Series:
    """Normalize available_at to Asia/Shanghai calendar date (drop 18:00 clock)."""
    av = pd.to_datetime(series, errors="coerce")
    if getattr(av.dt, "tz", None) is not None:
        return av.dt.tz_convert("Asia/Shanghai").dt.normalize().dt.tz_localize(None)
    return av.dt.normalize()


def load_first_disclosure(
    *,
    require_pit: bool = True,
) -> pd.DataFrame:
    """Load first available_at per (instrument_id, end_date) from financials PIT.

    Never forward-shifts. Restatement rows with later aa are separate events;
    historical first entry date is not rewritten.
    """
    if not SRC.exists():
        return pd.DataFrame()
    df = pd.read_parquet(
        SRC,
        columns=[
            "instrument_id",
            "end_date",
            "available_at",
            "ann_date",
            "f_ann_date",
            "report_type",
            "update_flag",
        ],
    )
    df["end_date"] = pd.to_datetime(df["end_date"], errors="coerce")
    df["available_at"] = pd.to_datetime(df["available_at"], errors="coerce")
    for c in ("ann_date", "f_ann_date"):
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    if require_pit:
        df = df[df["available_at"].notna()].copy()
    # SH/SZ A-share only
    df = df[df["instrument_id"].astype(str).str.startswith(("sh.", "sz."))].copy()
    # First disclosure: min available_at per (instrument_id, end_date)
    df = df.sort_values("available_at")
    first = (
        df.groupby(["instrument_id", "end_date"], as_index=False)
        .agg(
            available_at=("available_at", "min"),
            ann_date=("ann_date", "first"),
            f_ann_date=("f_ann_date", "first"),
            report_type=("report_type", "first"),
        )
    )
    first["avail_date"] = _normalize_avail(first["available_at"])
    first["instrument"] = first["instrument_id"].astype(str)
    first["ts_code"] = first["instrument"].map(
        lambda s: (
            f"{s.split('.', 1)[1]}.{s.split('.', 1)[0].upper()}"
            if "." in s
            else s
        )
    )
    return first.reset_index(drop=True)


def _float_top800_slice(
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> pd.DataFrame:
    """Load float mktcap for [start-lookback, end] and keep daily top800."""
    if not FLOAT_SRC.exists():
        return pd.DataFrame(columns=["instrument_id", "trade_date", "float_mktcap"])
    try:
        import pyarrow.dataset as ds

        dataset = ds.dataset(str(FLOAT_SRC), format="parquet")
        lo = start - pd.Timedelta(days=FLOAT_LOOKBACK_CAL_DAYS + 2)
        hi = end + pd.Timedelta(days=2)
        table = dataset.to_table(
            filter=(ds.field("trade_date") >= lo) & (ds.field("trade_date") <= hi),
            columns=["instrument_id", "trade_date", "float_mktcap"],
        )
        flt = table.to_pandas()
    except Exception:
        # Fallback: full read filtered in pandas (heavier; avoid when possible)
        flt = pd.read_parquet(
            FLOAT_SRC,
            columns=["instrument_id", "trade_date", "float_mktcap"],
        )
        lo = start - pd.Timedelta(days=FLOAT_LOOKBACK_CAL_DAYS + 2)
        hi = end + pd.Timedelta(days=2)
        td = pd.to_datetime(flt["trade_date"], errors="coerce")
        flt = flt[(td >= lo) & (td <= hi)].copy()
    flt["trade_date"] = pd.to_datetime(flt["trade_date"], errors="coerce").dt.normalize()
    flt = flt.dropna(subset=["float_mktcap", "trade_date"])
    flt["rank"] = flt.groupby("trade_date")["float_mktcap"].rank(
        ascending=False, method="first"
    )
    return flt.loc[
        flt["rank"] <= 800, ["instrument_id", "trade_date", "float_mktcap"]
    ].reset_index(drop=True)


def attach_float_top800(
    events: pd.DataFrame,
    *,
    lookback_cal_days: int = FLOAT_LOOKBACK_CAL_DAYS,
) -> pd.DataFrame:
    """Keep events whose instrument is in float top800 on avail_date (≤lookback days)."""
    if events.empty:
        return events.iloc[0:0].copy()
    start = events["avail_date"].min()
    end = events["avail_date"].max()
    top800 = _float_top800_slice(start, end)
    if top800.empty:
        out = events.copy()
        out["float_mktcap"] = np.nan
        out["in_top800"] = False
        return out.iloc[0:0].copy()
    cands = []
    for back in range(0, int(lookback_cal_days) + 1):
        t = events[
            ["instrument_id", "end_date", "available_at", "avail_date"]
        ].copy()
        t["trade_date"] = t["avail_date"] - pd.Timedelta(days=back)
        t["back"] = back
        cands.append(t)
    cand = pd.concat(cands, ignore_index=True)
    merged = cand.merge(top800, on=["instrument_id", "trade_date"], how="inner")
    merged = merged.sort_values("back").drop_duplicates(
        subset=["instrument_id", "end_date", "avail_date"], keep="first"
    )
    # re-attach full event columns
    out = events.merge(
        merged[["instrument_id", "end_date", "avail_date", "float_mktcap", "back"]],
        on=["instrument_id", "end_date", "avail_date"],
        how="inner",
    )
    out["in_top800"] = True
    return out.reset_index(drop=True)


def flag_early_vs_peer_median(
    mid_large: pd.DataFrame,
) -> pd.DataFrame:
    """Within same end_date mid/large peers, flag aa < median as early."""
    if mid_large.empty:
        return mid_large.iloc[0:0].copy()
    out = mid_large.copy()
    out["peer_median_aa"] = out.groupby("end_date")["available_at"].transform(
        "median"
    )
    out["disc_early_flag"] = out["available_at"] < out["peer_median_aa"]
    out["disc_late_flag"] = ~out["disc_early_flag"]
    return out.reset_index(drop=True)


def load_disc_early_events(
    *,
    window_start: pd.Timestamp | None = None,
    window_end: pd.Timestamp | None = None,
    require_top800: bool = True,
) -> pd.DataFrame:
    """Load mid/large first-disclosure events with early/late flags.

    Default window = full history (caller filters). For X1 inventory use
    window_start=X1_START, window_end=X1_END.
    """
    first = load_first_disclosure(require_pit=True)
    if first.empty:
        return first
    if window_start is not None:
        first = first[first["avail_date"] >= pd.Timestamp(window_start)].copy()
    if window_end is not None:
        first = first[first["avail_date"] <= pd.Timestamp(window_end)].copy()
    if require_top800:
        mid = attach_float_top800(first)
    else:
        mid = first.copy()
        mid["float_mktcap"] = np.nan
        mid["in_top800"] = False
    return flag_early_vs_peer_median(mid)


def coverage_report(df: pd.DataFrame | None = None) -> dict:
    """Honest X1 event counts (no fake IC / no fabricate).

    Canonical proposal counts: X1 early ∩ top800 = 3664 / 1057 / 18 end_dates.
    """
    if df is None:
        df = load_disc_early_events(
            window_start=X1_START, window_end=X1_END, require_top800=True
        )
    if df.empty:
        return {
            "source": str(SRC),
            "float_source": str(FLOAT_SRC),
            "rows": 0,
            "x1_early_events": 0,
            "x1_early_stocks": 0,
            "coverage_blocked_x1": True,
            "note": "表空或不可读；勿伪造。",
        }
    early = df[df["disc_early_flag"]].copy()
    late = df[df["disc_late_flag"]].copy()
    # Also report first-disclosure (pre top800) for transparency
    first_all = load_first_disclosure(require_pit=True)
    aa = first_all["avail_date"]
    x1_mask = (aa >= X1_START) & (aa <= X1_END)
    x1_first = first_all.loc[x1_mask]
    return {
        "source": str(SRC),
        "float_source": str(FLOAT_SRC),
        "float_lookback_cal_days": FLOAT_LOOKBACK_CAL_DAYS,
        "x1_window": f"{X1_START.date()}→{X1_END.date()}",
        "x1_first_disclosure_rows": int(len(x1_first)),
        "x1_first_disclosure_stocks": int(x1_first["instrument_id"].nunique())
        if len(x1_first)
        else 0,
        "x1_top800_rows": int(len(df)),
        "x1_top800_stocks": int(df["instrument_id"].nunique()) if len(df) else 0,
        "x1_early_events": int(len(early)),
        "x1_early_stocks": int(early["instrument_id"].nunique()) if len(early) else 0,
        "x1_early_end_dates": int(early["end_date"].nunique()) if len(early) else 0,
        "x1_late_events": int(len(late)),
        "x1_late_stocks": int(late["instrument_id"].nunique()) if len(late) else 0,
        "x1_pit_min": str(early["avail_date"].min()) if len(early) else None,
        "x1_pit_max": str(early["avail_date"].max()) if len(early) else None,
        "coverage_blocked_x1": bool(len(early) == 0),
        "note": (
            "完整 X1 有事件覆盖成立（早披露主源非零；3664/1057）；"
            "增减持/大宗/停复牌/异动 X1 缺口已换维，本臂不用。"
            "勿伪造 IC；勿前移 available_at；勿用盈余/ocf/应计打分替代早晚旗。"
        ),
    }


def build_event_leaf_table(
    df: pd.DataFrame | None = None,
    *,
    leaf_name: str = "disc_early_flag",
) -> pd.DataFrame:
    """Return long event table for leaf (scaffold; not a panel matrix).

    Columns include instrument, avail_date, available_at, end_date, peer_median_aa,
    float_mktcap, leaf, value.
    Caller maps avail_date → calendar session (searchsorted left) before trade.
    value=1.0 for matching flag rows only.
    """
    if df is None:
        df = load_disc_early_events(
            window_start=None, window_end=None, require_top800=True
        )
    if leaf_name not in ("disc_early_flag", "disc_late_flag"):
        raise ValueError(f"unknown leaf_name={leaf_name!r}; expected one of {LEAF_NAMES}")
    mask = df[leaf_name] if leaf_name in df.columns else pd.Series(False, index=df.index)
    out = df.loc[mask].copy()
    out["leaf"] = leaf_name
    out["value"] = 1.0
    cols = [
        "instrument",
        "instrument_id",
        "ts_code",
        "end_date",
        "available_at",
        "avail_date",
        "peer_median_aa",
        "float_mktcap",
        "ann_date",
        "f_ann_date",
        "report_type",
        "leaf",
        "value",
    ]
    cols = [c for c in cols if c in out.columns]
    return out[cols].reset_index(drop=True)


def select_names_for_day(
    day_events: pd.DataFrame,
    *,
    n: int = N_NAMES,
    float_mktcap: pd.Series | None = None,
) -> pd.DataFrame:
    """Pick top-N early-disclosure names for one entry day by float mktcap.

    day_events must already be filtered to the tradeable universe for that day
    and to disc_early_flag==True (or the early leaf table).
    """
    if day_events.empty:
        return day_events.iloc[0:0].copy()
    ev = day_events.copy()
    if float_mktcap is not None and "instrument_id" in ev.columns:
        ev = ev.assign(
            _mcap=ev["instrument_id"].map(float_mktcap).fillna(ev.get("float_mktcap"))
        )
    elif "float_mktcap" in ev.columns:
        ev = ev.assign(_mcap=ev["float_mktcap"])
    else:
        ev = ev.assign(_mcap=np.nan)
    ev = ev.sort_values(["_mcap"], ascending=[False], na_position="last")
    ev = ev.drop_duplicates(subset=["instrument"], keep="first")
    return (
        ev.head(int(n))
        .drop(columns=["_mcap"], errors="ignore")
        .reset_index(drop=True)
    )


def universe_rules() -> dict:
    return {
        "primary": "CSI300∪CSI500 (mid/large)",
        "x1_fallback": "float_mktcap top800 (lookback≤3 calendar days)",
        "float_source": str(FLOAT_SRC),
        "filters": ["no_ST", "price>=2", "not_halted", "no_small_cap"],
        "forbidden": [
            "small_cap",
            "CB",
            "gold_main",
            "industry_ETF_timing_tercile",
            "share_flow",
            "price_leaf",
            "dragon_tiger_seat",
            "unlock_sharetype",
            "LIMITUP_FADE",
            "overnight_star",
            "ocf_accrual_roa_textbook_main",
            "div_imp_dy_isomorph",
            "index_rebal_v31_isomorph",
            "abnormal_move_title_leaf_x1_zero",
            "earnings_surprise_magnitude_pead",
        ],
    }


def portfolio_rules() -> dict:
    return {
        "signal": "disc_early_flag long; top N by float mktcap among early names",
        "sensitivity_leaf": "disc_late_flag (late peers; NOT main book)",
        "N": N_NAMES,
        "K_trading_days_after_pit": K_HOLD,
        "weighting": "equal_weight among selected names",
        "w_stock": "min(0.70, 0.028 * n)",
        "ballast": BALLAST,
        "n_zero": f"100% {BALLAST} when n=0",
        "y": "fwd excess vs 510300 (disclosure-calendar event sleeve; NOT monthly quality factor)",
        "cost_bp": 25,
        "aums": [600000, 1000000],
    }


def pit_rules() -> dict:
    return {
        "rule": (
            "pit=first available_at per (instrument_id,end_date) from "
            "financials_available_at_tushare (report-day 18:00 Asia/Shanghai); "
            "normalize → next open tradeable; hold K=10 trading days after pit entry; "
            "early = aa < same-end_date mid/large peer median; "
            "never forward-shift; restatement = new aa event, do not rewrite historical first entry"
        ),
        "never_forward_shift": True,
        "restatement_policy": "new available_at re-evaluated; historical first entry unchanged",
        "null_pit": "drop (do not impute / backfill)",
        "peer_median_scope": "same end_date within mid/large (float top800) cohort",
    }


def write_scaffold_receipt() -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cov = coverage_report()
    receipt = {
        "arm": "STOCK-DISC-EARLY",
        "version": "v34",
        "sleeve": "stock_event_disc_early",
        "scaffold_only": True,
        "nav_run": False,
        "backtest_run": False,
        "smoke_run": False,
        "gp_run": False,
        "v27_gp_started": False,
        "promotion_approved": False,
        "for_alpha": True,
        "handoff_strategy": False,
        "created_at_et": pd.Timestamp.now(tz="America/New_York").isoformat(),
        "leaves": LEAF_NAMES,
        "pit": pit_rules(),
        "universe": universe_rules(),
        "portfolio": portfolio_rules(),
        "coverage": cov,
        "paths": {
            "wiring_module": str(ROOT / "research/ai_factor_disc_early_panels.py"),
            "source_events": str(SRC),
            "float_mktcap": str(FLOAT_SRC),
            "package_dir": str(OUT_DIR),
            "doc_receipt": str(DOC),
            "proposal": str(
                ROOT / "docs/v2/AI_STOCK_ARM_PROPOSAL_V34_DISC_EARLY_ZH.md"
            ),
        },
        "beta_entry": {
            "load_events": "research.ai_factor_disc_early_panels.load_disc_early_events",
            "leaf_early": "build_event_leaf_table(leaf_name='disc_early_flag')",
            "leaf_late_sens": "build_event_leaf_table(leaf_name='disc_late_flag')",
            "select_day": "select_names_for_day(day_events, n=25)",
            "coverage": "coverage_report()",
            "note": (
                "Beta 主跑完整 X1；本模块只接线，不代跑 NAV。"
                "勿碰 V31 包；勿磨分红/DY/ocf/seat/解禁/tercile。"
            ),
        },
        "self_checks": {
            "did_not_run": ["NAV", "backtest", "smoke", "GP", "v27 SEARCH"],
            "did_not_fabricate": ["X1 events", "IC"],
            "did_not_touch": ["stock_index_rebal_v31", "V31 package"],
            "did_not_grind": [
                "div_imp_dy",
                "ocf_accrual_quality",
                "seat",
                "unlock",
                "etf_tercile",
                "price_leaf",
            ],
        },
    }
    out_json = OUT_DIR / "wiring_receipt.json"
    out_json.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(
        description="V34 DISC-EARLY wiring scaffold (no NAV)"
    )
    ap.add_argument(
        "--inventory-only",
        action="store_true",
        default=True,
        help="Write coverage + scaffold receipt only (default)",
    )
    ap.add_argument(
        "--materialize-leaves",
        action="store_true",
        help="Write long event leaf tables (still no NAV/IC); off by default",
    )
    args = ap.parse_args()
    receipt = write_scaffold_receipt()
    print(
        json.dumps(
            {
                "coverage": receipt["coverage"],
                "out": str(OUT_DIR / "wiring_receipt.json"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    if args.materialize_leaves:
        # Full history mid/large for leaf tables (no NAV)
        df = load_disc_early_events(
            window_start=None, window_end=None, require_top800=True
        )
        for name in LEAF_NAMES:
            tab = build_event_leaf_table(df, leaf_name=name)
            path = OUT_DIR / f"{name}_events.parquet"
            tab.to_parquet(path, index=False)
            print(f"wrote {path} rows={len(tab)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
