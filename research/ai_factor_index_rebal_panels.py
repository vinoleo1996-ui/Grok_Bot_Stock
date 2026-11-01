#!/usr/bin/env python3
"""STOCK-INDEX-REBAL (V31) leaf wiring scaffold.

Leaves:
  idx_add_flag  — CSI300/CSI500 成分调入 (event=in)，按 available_at 入日
  idx_del_flag  — CSI300/CSI500 成分调出 (event=out)，按 available_at 入日
                  （持仓默认：调入多头；调出不持 / 不做空）

Universe: 事件涉及的 CSI300∪CSI500 成分（本就中大盘）；滤 ST / 价<2 / 停牌；禁小盘。
Index filter: index_code ∈ {000300.SH, 000905.SH} ONLY（排除 000852.SH/CSI1000）。

PIT (hard):
  available_at → normalize()+1d → searchsorted(cal, left) = first session on/after;
  hold window anchored at effective_date; K=10 trading days after effective (fixed).
  Never forward-shift available_at.

Coverage (honest):
  Standard X1 (2015-06→2017-12): events=0 → coverage_blocked.
  Available segment for smoke: 2018-06+ (table earliest available_at ≈ 2018-05-25).

promotion_approved=False.
Does NOT run NAV / backtest / GP / v27 / SEARCH / smoke.
Scaffold + inventory only; Beta owns the pretest run.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/workspace/QuantLab")
V2 = ROOT / "data/v2"
SRC = V2 / "index_members/index_member_events.parquet"
CAL_SRC = V2 / "index_members/csi_review_calendar.parquet"
OUT_DIR = ROOT / "output/ai_factor/stock_index_rebal_v31"
DOC = ROOT / "docs/v2/AI_INDEX_REBAL_WIRING_RECEIPT_ZH.md"

ALLOWED_INDEX = ("000300.SH", "000905.SH")
LEAF_NAMES = ["idx_add_flag", "idx_del_flag"]
K_HOLD = 10
N_NAMES = 25
X1_START = pd.Timestamp("2015-06-01")
X1_END = pd.Timestamp("2017-12-31")
AVAIL_SEG_START = pd.Timestamp("2018-06-01")


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


def load_index_rebal_events(
    *,
    require_avail: bool = True,
    index_codes: tuple[str, ...] = ALLOWED_INDEX,
) -> pd.DataFrame:
    """Load PIT index member in/out events; drop null available_at by default."""
    if not SRC.exists():
        return pd.DataFrame()
    df = pd.read_parquet(SRC)
    df = df[df["index_code"].astype(str).isin(index_codes)].copy()
    df["available_at"] = pd.to_datetime(df["available_at"], errors="coerce")
    df["effective_date"] = pd.to_datetime(df["effective_date"], errors="coerce")
    df["ann_date"] = pd.to_datetime(df["ann_date"], errors="coerce")
    if require_avail:
        df = df[df["available_at"].notna()].copy()
    df["avail_date"] = _normalize_avail(df["available_at"])
    df["instrument"] = df["con_code"].map(_to_baostock)
    df["event"] = df["event"].astype(str).str.lower().str.strip()
    return df.reset_index(drop=True)


def coverage_report(df: pd.DataFrame | None = None) -> dict:
    """Honest X1 + available-segment event counts (no fake backfill)."""
    if df is None:
        df = load_index_rebal_events(require_avail=True)
    if df.empty:
        return {
            "source": str(SRC),
            "rows": 0,
            "x1_events": 0,
            "coverage_blocked_x1": True,
            "available_segment_start": str(AVAIL_SEG_START.date()),
            "available_segment_events": 0,
        }
    av = df["avail_date"]
    x1 = (av >= X1_START) & (av <= X1_END)
    seg = av >= AVAIL_SEG_START
    add = df["event"] == "in"
    return {
        "source": str(SRC),
        "index_codes": list(ALLOWED_INDEX),
        "rows_pit": int(len(df)),
        "avail_min": str(av.min()),
        "avail_max": str(av.max()),
        "x1_window": f"{X1_START.date()}→{X1_END.date()}",
        "x1_events": int(x1.sum()),
        "x1_add": int((x1 & add).sum()),
        "x1_del": int((x1 & ~add).sum()),
        "coverage_blocked_x1": bool(x1.sum() == 0),
        "available_segment_start": str(AVAIL_SEG_START.date()),
        "available_segment_events": int(seg.sum()),
        "available_segment_add": int((seg & add).sum()),
        "available_segment_del": int((seg & ~add).sum()),
        "note": (
            "标准 X1 事件=0 → coverage_blocked；"
            "冒烟须在 2018-06+ 可用段报 coverage/avg_names；勿伪造早年调样。"
        ),
    }


def build_event_leaf_table(
    df: pd.DataFrame | None = None,
    *,
    event: str = "in",
    leaf_name: str = "idx_add_flag",
) -> pd.DataFrame:
    """Return long event table for one leaf (scaffold; not a panel matrix).

    Columns: instrument, index_code, event, available_at, avail_date,
             effective_date, ann_date, leaf, value=1.0
    Caller maps avail_date → calendar session (searchsorted left) before trade.
    """
    if df is None:
        df = load_index_rebal_events(require_avail=True)
    ev = str(event).lower()
    out = df[df["event"] == ev].copy()
    out["leaf"] = leaf_name
    out["value"] = 1.0
    cols = [
        "instrument",
        "con_code",
        "index_code",
        "event",
        "available_at",
        "avail_date",
        "effective_date",
        "ann_date",
        "leaf",
        "value",
        "review",
    ]
    cols = [c for c in cols if c in out.columns]
    return out[cols].reset_index(drop=True)


def universe_rules() -> dict:
    return {
        "primary": "CSI300∪CSI500 (event names; mid/large by construction)",
        "index_filter": list(ALLOWED_INDEX),
        "exclude_index": ["000852.SH"],
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
        ],
    }


def portfolio_rules() -> dict:
    return {
        "signal": "idx_add_flag long; idx_del_flag default underweight/flat (no short)",
        "N": N_NAMES,
        "K_trading_days_after_effective": K_HOLD,
        "weighting": "equal_weight among selected adds",
        "w_stock": "min(0.70, 0.028 * n)",
        "ballast": "sh.510300",
        "n_zero": "100% sh.510300 when n=0",
        "y": "fwd excess vs 510300",
        "cost_bp": 25,
        "aums": [600000, 1000000],
    }


def pit_rules() -> dict:
    return {
        "rule": (
            "available_at.normalize()+1d → searchsorted(cal, left); "
            "trade next open; hold window anchor effective_date; K=10 fixed; "
            "never forward-shift available_at"
        ),
        "never_forward_shift": True,
        "null_available_at": "drop (do not impute / backfill)",
    }


def write_scaffold_receipt() -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cov = coverage_report()
    receipt = {
        "arm": "STOCK-INDEX-REBAL",
        "version": "v31",
        "sleeve": "stock_event_index_rebal",
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
            "wiring_module": str(ROOT / "research/ai_factor_index_rebal_panels.py"),
            "source_events": str(SRC),
            "review_calendar": str(CAL_SRC),
            "package_dir": str(OUT_DIR),
            "doc_receipt": str(DOC),
            "proposal": str(ROOT / "docs/v2/AI_STOCK_ARM_PROPOSAL_V31_INDEX_REBAL_ZH.md"),
        },
        "beta_entry": {
            "load_events": "research.ai_factor_index_rebal_panels.load_index_rebal_events",
            "leaf_add": "build_event_leaf_table(event='in', leaf_name='idx_add_flag')",
            "leaf_del": "build_event_leaf_table(event='out', leaf_name='idx_del_flag')",
            "coverage": "coverage_report()",
            "note": "Beta 主跑可用段冒烟(2018-06+)；本模块只接线，不代跑 NAV。",
        },
        "self_checks": {
            "did_not_run": ["NAV", "backtest", "smoke", "GP", "v27 SEARCH"],
            "did_not_fabricate": ["X1 events", "IC", "early rebal history"],
        },
    }
    out_json = OUT_DIR / "wiring_receipt.json"
    out_json.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="V31 INDEX-REBAL wiring scaffold (no NAV)")
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
    # Force no NAV path
    receipt = write_scaffold_receipt()
    print(json.dumps({"coverage": receipt["coverage"], "out": str(OUT_DIR / "wiring_receipt.json")}, ensure_ascii=False, indent=2))
    if args.materialize_leaves:
        df = load_index_rebal_events()
        for ev, name in (("in", "idx_add_flag"), ("out", "idx_del_flag")):
            tab = build_event_leaf_table(df, event=ev, leaf_name=name)
            path = OUT_DIR / f"{name}_events.parquet"
            tab.to_parquet(path, index=False)
            print(f"wrote {path} rows={len(tab)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
