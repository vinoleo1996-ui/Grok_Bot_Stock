#!/usr/bin/env python3
"""STOCK-DIV-IMP (V33) leaf wiring scaffold.

Leaves:
  div_imp_cash_flag   — div_proc 含「实施」∧ cash_div>0；PIT=imp_ann_date∪ann_date；主仓事件旗
  div_imp_yield_xsec  — 实施窗内 cash_div/价 截面（敏感性对照；非主仓常驻 DY）

Universe: CSI300∪CSI500；X1 缺权用 float top800；滤 ST / 价<2 / 停牌；禁小盘。

PIT (hard):
  pit_date = coalesce(imp_ann_date, ann_date) → normalize (Asia/Shanghai 当日 23:59 口径)
  → 下一开盘可交易；持有窗 K=10 交易日锚 pit 入日；不可前移；不用 ex_date 倒推可用日。
  排除 div_proc 含「停止实施」。

Coverage (honest):
  Standard X1 (2015-06→2017-12): events≈5884 (cash 实施) → coverage_ok (NOT blocked).
  Source: data/v2/corporate_actions/dividend_tushare.parquet

promotion_approved=False.
Does NOT run NAV / backtest / GP / v27 / SEARCH / smoke.
Scaffold + inventory only; Beta owns the X1 pretest run.
Does NOT touch V31 stock_index_rebal package.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/workspace/QuantLab")
V2 = ROOT / "data/v2"
SRC = V2 / "corporate_actions/dividend_tushare.parquet"
FLOAT_SRC = V2 / "float_mktcap/float_mktcap_daily_from2015_tushare.parquet"
OUT_DIR = ROOT / "output/ai_factor/stock_div_imp_v33"
DOC = ROOT / "docs/v2/AI_DIV_IMP_WIRING_RECEIPT_ZH.md"

LEAF_NAMES = ["div_imp_cash_flag", "div_imp_yield_xsec"]
K_HOLD = 10
N_NAMES = 25
X1_START = pd.Timestamp("2015-06-01")
X1_END = pd.Timestamp("2017-12-31")
BALLAST = "sh.510300"


def _to_baostock(ts_code: str) -> str:
    s = str(ts_code)
    if "." in s:
        code, ex = s.split(".", 1)
        return f"{ex.lower()}.{code}"
    return s


def _normalize_avail(series: pd.Series) -> pd.Series:
    av = pd.to_datetime(series, errors="coerce")
    if getattr(av.dt, "tz", None) is not None:
        return av.dt.tz_convert("Asia/Shanghai").dt.normalize().dt.tz_localize(None)
    return av.dt.normalize()


def _is_implementation(proc: pd.Series) -> pd.Series:
    s = proc.astype(str).str.strip()
    has_imp = s.str.contains("实施", na=False)
    stopped = s.str.contains("停止", na=False)
    return has_imp & ~stopped


def load_div_imp_events(
    *,
    require_cash: bool = True,
    require_pit: bool = True,
) -> pd.DataFrame:
    """Load cash-dividend implementation events with PIT=imp_ann_date∪ann_date.

    Drops 停止实施. Never uses ex_date to backdate availability.
    """
    if not SRC.exists():
        return pd.DataFrame()
    df = pd.read_parquet(SRC)
    for c in ("ann_date", "imp_ann_date", "ex_date", "record_date", "end_date", "pay_date"):
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    df = df[_is_implementation(df["div_proc"])].copy()
    if require_cash:
        df = df[df["cash_div"].fillna(0) > 0].copy()
    # PIT: imp_ann_date preferred; fall back to ann_date. Never ex_date.
    df["pit_raw"] = df["imp_ann_date"].fillna(df["ann_date"])
    if require_pit:
        df = df[df["pit_raw"].notna()].copy()
    df["avail_date"] = _normalize_avail(df["pit_raw"])
    df["instrument"] = df["ts_code"].map(_to_baostock)
    df["div_proc"] = df["div_proc"].astype(str).str.strip()
    return df.reset_index(drop=True)


def coverage_report(df: pd.DataFrame | None = None) -> dict:
    """Honest X1 event counts from dividend_tushare (no fake IC / no fabricate)."""
    if df is None:
        df = load_div_imp_events(require_cash=True, require_pit=True)
    if df.empty:
        return {
            "source": str(SRC),
            "rows": 0,
            "x1_events": 0,
            "coverage_blocked_x1": True,
            "note": "表空或不可读；勿伪造。",
        }
    av = df["avail_date"]
    x1 = (av >= X1_START) & (av <= X1_END)
    x1_df = df.loc[x1]
    # alternate ann_date window (proposal secondary count)
    ann = pd.to_datetime(df["ann_date"], errors="coerce")
    x1_ann = (ann >= X1_START) & (ann <= X1_END)
    return {
        "source": str(SRC),
        "rows_imp_cash_pit": int(len(df)),
        "pit_min": str(av.min()),
        "pit_max": str(av.max()),
        "x1_window": f"{X1_START.date()}→{X1_END.date()}",
        "x1_events": int(x1.sum()),
        "x1_stocks": int(x1_df["ts_code"].nunique()) if len(x1_df) else 0,
        "x1_unique_ts_end": int(x1_df.groupby(["ts_code", "end_date"]).ngroups) if len(x1_df) else 0,
        "x1_pit_min": str(x1_df["avail_date"].min()) if len(x1_df) else None,
        "x1_pit_max": str(x1_df["avail_date"].max()) if len(x1_df) else None,
        "x1_has_ex_date_frac": float(x1_df["ex_date"].notna().mean()) if len(x1_df) else 0.0,
        "x1_by_ann_date_events": int(x1_ann.sum()),
        "x1_by_ann_date_stocks": int(df.loc[x1_ann, "ts_code"].nunique()) if x1_ann.any() else 0,
        "coverage_blocked_x1": bool(x1.sum() == 0),
        "note": (
            "完整 X1 有事件覆盖成立（分红实施主源非零）；"
            "异动/问询等 classified X1=0 已换维，本臂不用。"
            "勿伪造 IC；勿用 ex_date 前移可用。"
        ),
    }


def build_event_leaf_table(
    df: pd.DataFrame | None = None,
    *,
    leaf_name: str = "div_imp_cash_flag",
) -> pd.DataFrame:
    """Return long event table for primary leaf (scaffold; not a panel matrix).

    Columns: instrument, ts_code, cash_div, avail_date, pit_raw, ann_date,
             imp_ann_date, ex_date, record_date, end_date, leaf, value
    Caller maps avail_date → calendar session (searchsorted left) before trade.
    value=1.0 for flag; for yield leaf value=cash_div (price attach is Beta-side).
    """
    if df is None:
        df = load_div_imp_events(require_cash=True, require_pit=True)
    out = df.copy()
    out["leaf"] = leaf_name
    if leaf_name == "div_imp_yield_xsec":
        # cash amount only; cross-section / price attach left to Beta (no price peek here)
        out["value"] = out["cash_div"].astype(float)
    else:
        out["value"] = 1.0
    cols = [
        "instrument",
        "ts_code",
        "cash_div",
        "avail_date",
        "pit_raw",
        "ann_date",
        "imp_ann_date",
        "ex_date",
        "record_date",
        "end_date",
        "div_proc",
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
    """Pick top-N names for one entry day: prefer cash_div then float mktcap.

    day_events must already be filtered to the tradeable universe for that day.
    """
    if day_events.empty:
        return day_events.iloc[0:0].copy()
    ev = day_events.copy()
    if float_mktcap is not None and "ts_code" in ev.columns:
        ev = ev.assign(_mcap=ev["ts_code"].map(float_mktcap))
    else:
        ev = ev.assign(_mcap=np.nan)
    ev = ev.sort_values(
        ["cash_div", "_mcap"],
        ascending=[False, False],
        na_position="last",
    )
    # one row per instrument
    ev = ev.drop_duplicates(subset=["instrument"], keep="first")
    return ev.head(int(n)).drop(columns=["_mcap"], errors="ignore").reset_index(drop=True)


def universe_rules() -> dict:
    return {
        "primary": "CSI300∪CSI500 (mid/large)",
        "x1_fallback": "float_mktcap top800 (when index membership incomplete)",
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
            "abnormal_move_title_leaf_x1_zero",
        ],
    }


def portfolio_rules() -> dict:
    return {
        "signal": "div_imp_cash_flag long; top N by cash_div then float mktcap",
        "sensitivity_leaf": "div_imp_yield_xsec (cash/price xsec in window; NOT resident DY)",
        "N": N_NAMES,
        "K_trading_days_after_pit": K_HOLD,
        "weighting": "equal_weight among selected names",
        "w_stock": "min(0.70, 0.028 * n)",
        "ballast": BALLAST,
        "n_zero": f"100% {BALLAST} when n=0",
        "y": "fwd excess vs 510300",
        "cost_bp": 25,
        "aums": [600000, 1000000],
    }


def pit_rules() -> dict:
    return {
        "rule": (
            "pit=coalesce(imp_ann_date, ann_date); "
            "normalize Asia/Shanghai day-end 23:59 口径 → next open tradeable; "
            "hold K=10 trading days after pit entry; "
            "never forward-shift; never use ex_date to backdate availability; "
            "drop 停止实施"
        ),
        "never_forward_shift": True,
        "never_use_ex_date_for_avail": True,
        "null_pit": "drop (do not impute / backfill from ex_date)",
    }


def write_scaffold_receipt() -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cov = coverage_report()
    receipt = {
        "arm": "STOCK-DIV-IMP",
        "version": "v33",
        "sleeve": "stock_event_div_imp",
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
            "wiring_module": str(ROOT / "research/ai_factor_div_imp_panels.py"),
            "source_events": str(SRC),
            "float_mktcap": str(FLOAT_SRC),
            "package_dir": str(OUT_DIR),
            "doc_receipt": str(DOC),
            "proposal": str(ROOT / "docs/v2/AI_STOCK_ARM_PROPOSAL_V33_DIV_IMP_ZH.md"),
        },
        "beta_entry": {
            "load_events": "research.ai_factor_div_imp_panels.load_div_imp_events",
            "leaf_flag": "build_event_leaf_table(leaf_name='div_imp_cash_flag')",
            "leaf_yield_sens": "build_event_leaf_table(leaf_name='div_imp_yield_xsec')",
            "select_day": "select_names_for_day(day_events, n=25)",
            "coverage": "coverage_report()",
            "note": "Beta 主跑完整 X1；本模块只接线，不代跑 NAV。勿碰 V31 包。",
        },
        "self_checks": {
            "did_not_run": ["NAV", "backtest", "smoke", "GP", "v27 SEARCH"],
            "did_not_fabricate": ["X1 events", "IC"],
            "did_not_touch": ["stock_index_rebal_v31", "V31 package"],
        },
    }
    out_json = OUT_DIR / "wiring_receipt.json"
    out_json.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="V33 DIV-IMP wiring scaffold (no NAV)")
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
        df = load_div_imp_events()
        for name in LEAF_NAMES:
            tab = build_event_leaf_table(df, leaf_name=name)
            path = OUT_DIR / f"{name}_events.parquet"
            tab.to_parquet(path, index=False)
            print(f"wrote {path} rows={len(tab)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
