#!/usr/bin/env python3
"""Leaf30 CRR + CFOOE residual vol_pen alpha build r3_peakcut — HILIQ×x2 (NOT authorized).

NEW file (2026-10-27). Copied from r2 sha8 0a264402; PRIMARY=A rebal-day logmv lazy load.
  FROZEN who_pays sha8 93cad965; Arch prereg f61ffb05; R1 qend_ok (Arch d1c71ece).
  Arch R3 proposal review 61830035 APPROVE_A; proposal f111671a.
  VOID df47501c / abort_ref fe5a2c1e — peak after_logmv_rebal 1433684 >= split → rc=94.
  Ban RESTORED .ok 5af20222 + 5ae077fa; ban blind rerun a2cef5af / 0a264402-as-ticket;
  ban raise rss above 1500.

R3 peak fix vs r2 (keep R2 avail month-bucket + daily month-chunk):
  PRIMARY=A: abolish whole-window logmv_rebal preload; per rebal day
    logmv_d = _load_logmv_t1(..., [d], codes) → consume → del+gc →
    _rss(after_logmv_rebal_YYYYMMDD). Ban residual whole-window preload.
  B month_bucket load_mode NOT in this script (doc-only; ban silent mix).
  peak_proof REQUIRED: after_daily_concat + after_logmv_rebal_*; Exit 94/95; rss=1500.

Mechanism (FROZEN; mechanism_tag=g1g5_ashare_crr_cfooe_volpen_v1):
  YTD→single_q; CRR_raw = sum(OCF_q,L=16)/sum(OP_q,L=16); ≥12 valid q; denom≤0 invalid
  CFOOE ε → vol_pen (8/6); α_raw = rank(CRR) − λ·rank(vol_pen), λ=1.0
  SW L1 demean + vs logmv OLS resid; IC expected POSITIVE (comment pin; no returns)

PRIMARY: --universe HILIQ --window x2  (FULLA → STOP)
X2: 2024-06-03 → 2026-10-09; rebal every 20 trade days
Main data: financials_pit_tushare.operate_profit + cashflow_pit_tushare.n_cashflow_act
  BAN ocf_to_profit as main CRR source
Industry hard exclude: 801780.SI / 801180.SI / 801790.SI
C3: overlap_vs_leaf19_25.json default on real path; sign bans --no-overlap-report
Real path: --allow-real-data + existing --arch-ok-path; ok sha ∉ forbid
--dry-compile-only: print pins; ZERO big-table load
rss soft 1500 MB; sampler only /tmp/quantlab_leaf30_crr_r3_*
live=false; promotion_approved=false; ok_requested=false
No Book-Smoke / selfcheck entry.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import resource
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
SH = ZoneInfo("Asia/Shanghai")
ROOT = Path(__file__).resolve().parents[1]
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

MECHANISM_TAG = "g1g5_ashare_crr_cfooe_volpen_v1"
SCRIPT_REL = "research/leaf30_crr_cfooe_volpen_alpha_build_r3_peakcut.py"
FROZEN_REL = "docs/v2/AI_LEAF30_CRR_CFOOE_VOLPEN_WHO_PAYS_FROZEN_20261026_ZH.md"
FROZEN_SHA8 = "93cad965"
ARCH_PREREG_SHA8 = "f61ffb05"

# Soft cap (MB) — Main order; ban raise
RSS_LIMIT_MB = 1500
C4_KB = 1331200
STOP_KB = 1484800
HARD_KB = 1536000
SPLIT_THRESH_KB = int(0.85 * C4_KB)

X2_START = "2024-06-03"
X2_END = "2026-10-09"
X2_END_TRADE_DATE = "20261009"
REBAL_EVERY = 20
LAMBDA_FROZEN = 1.0  # FROZEN §4; ban post-hoc flip
CRR_L = 16
CRR_MIN_Q = 12
VOL_WIN = 8
VOL_MIN = 6
# IC sign pin (FROZEN): expected POSITIVE vs next-period idiosyncratic return.
# This script NEVER computes returns / IC — direction is documentation-only.
IC_SIGN_EXPECTED = "positive"

FORBID_OK_SHA8 = (
    # R2 VOID.ABORT_PEAK_HWM — ban RESTORED; first item
    "5af20222",  # leaf30 R2 CRR X2 VOID.ABORT_PEAK_HWM Arch df47501c
    # R1 VOID.ABORT_PEAK_HWM — ban RESTORED
    "5ae077fa",  # leaf30 CRR X2 VOID.ABORT_PEAK_HWM Arch ff30406f
    # task-required + leaf25/27 VOID/CONSUMED common tickets
    "3c297052",  # leaf25 full alpha build CONSUMED
    "e107383f",
    "2be59acd",
    "1c32ab1e",  # step_m1 CONSUMED
    "ebc673bf",  # leaf25 x2 selfcheck CONSUMED
    "a7d98ac9",
    "8e51de63",
    "3a6caa4f",
    "8bcd79dc",
    "725be3e0",
    "0f50daf7",
    "3c19dd7d",
    "6054b3bf",
    "6de02e74",  # A18 EXEC — never reuse as leaf30 .ok
)

FP = ROOT / "data/v2/financials_pit"
PIT_FIN = FP / "financials_pit_tushare.parquet"
PIT_CF = FP / "cashflow_pit_tushare.parquet"
# NOTE: ocf_to_profit_pit_daily_tushare is COUNT-GATE APPROX only — BAN as main CRR source.
OCF_TO_PROFIT_APPROX_ONLY = FP / "ocf_to_profit_pit_daily_tushare.parquet"

HI_LIQ_MASK_DEFAULT = ROOT / "output/strategy_hiliq/universe_mask_hiliq_v1.parquet"
SW_L1_DEFAULT = ROOT / "data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet"
FLOAT_MKTCAP_DEFAULT = (
    ROOT / "data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet"
)
CAL_DEFAULT = ROOT / "data/v2/calendar/trade_cal_sse_pit.parquet"
LEAF19_ALPHA_DEFAULT = (
    ROOT / "output/ai_factory/leaf19_cfacc_rnoa/alpha_HILIQ_20261014_213132.parquet"
)
LEAF25_ALPHA_DEFAULT = ROOT / (
    "output/ai_factory/_leaf25_full_factor/20261026_015610/"
    "alpha_HILIQ_x2_20261026_125138.parquet"
)
LEAF25_ALPHA_SHA8_EXPECT = "8be12024"

EXCLUDE_SW = {
    "银行": "801780.SI",
    "房地产": "801180.SI",
    "非银金融": "801790.SI",
}
# 综合 = 801230.SI is NOT in this mask (FROZEN §5)

KEY_PIT = ["ts_code", "end_date", "available_at", "update_flag", "report_type"]
QEND = {"0331", "0630", "0930", "1231"}
NULL = "<NULL>"
SAMPLER_PREFIX = "/tmp/quantlab_leaf30_crr_r3_"

KNOWN_PIT_COLS = {
    "financials": KEY_PIT + ["operate_profit"],
    "cashflow": KEY_PIT + ["n_cashflow_act"],
}
KNOWN_MASK_COLS = ["date", "instrument", "in_universe"]
KNOWN_ALPHA_OUT_COLS = ["trade_date", "ts_code", "alpha"]
KNOWN_SW_COLS = [
    "instrument_id",
    "sw_code",
    "sw_name",
    "in_date",
    "out_date",
    "available_at",
]
KNOWN_FLOAT_COLS = ["instrument_id", "trade_date", "float_mktcap"]


def stage(name: str) -> None:
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(f"STAGE {name} ru_maxrss={rss}", file=sys.stderr, flush=True)


def vmhwm_kb() -> int | None:
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmHWM:"):
                    return int(line.split()[1])
    except OSError:
        return None
    return None


def vmrss_kb() -> int | None:
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1])
    except OSError:
        return None
    return None


def peak_kb() -> int:
    """Peak = max(ru_maxrss, VmHWM). Hard breach → check_rss SystemExit 95 (ban raise cap)."""
    ru = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    hw = vmhwm_kb()
    return max(ru, hw) if hw is not None else ru


def check_rss(label: str, *, rss_limit_mb: int, c4_kb: int, hard_kb: int, split_kb: int) -> int:
    pk = peak_kb()
    soft_kb = int(rss_limit_mb) * 1024
    vr = vmrss_kb()
    print(
        f"RSS_CHECK {label} peak_kb={pk} vmrss_kb={vr} "
        f"soft={soft_kb} split={split_kb} c4={c4_kb} hard={hard_kb}",
        flush=True,
    )
    if pk >= hard_kb or (vr is not None and vr >= hard_kb):
        print(
            f"STOP: RSS hard breached peak_kb={pk} vmrss={vr} >= hard={hard_kb}",
            file=sys.stderr,
        )
        raise SystemExit(95)
    if (vr is not None and vr >= soft_kb) or pk >= soft_kb:
        print(
            f"STOP: RSS soft 1500MB breached peak_kb={pk} vmrss={vr} >= soft={soft_kb}; "
            f"ABORT no self-retry",
            file=sys.stderr,
        )
        raise SystemExit(94)
    if pk >= split_kb:
        print(
            f"STOP: RSS >= 0.85*C4 peak_kb={pk} >= split={split_kb}; "
            f"split further — ban raise cap",
            file=sys.stderr,
        )
        raise SystemExit(94)
    return pk


def assert_tmp_quantlab(path: Path, what: str) -> None:
    resolved = path.resolve()
    parts = resolved.parts
    ok = False
    if len(parts) >= 3 and parts[1] == "tmp":
        name = parts[2]
        if name.startswith("quantlab"):
            ok = True
    if not ok:
        raise SystemExit(f"STOP: {what} must be under /tmp/quantlab_* got={resolved}")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def script_sha256() -> str:
    return sha256_file(Path(__file__).resolve())


def to_ts(x) -> str:
    """instrument_id 'sz.000001' → ts_code '000001.SZ'; pass through ts_code."""
    s = str(x)
    if s.startswith(("sh.", "sz.", "bj.")):
        mkt, code = s.split(".", 1)
        return f"{code}.{mkt.upper()}"
    return s


def normalize_universe(u: str) -> str:
    u = (u or "").strip()
    if u in ("HILIQ", "HI_LIQ"):
        return "HILIQ"
    if u == "FULLA":
        return "FULLA"
    raise SystemExit(f"STOP: unknown --universe={u!r}; PRIMARY is HILIQ")


def dry_compile_only_print(args) -> int:
    """Zero big-table load; print hard pins for Arch/Main precheck."""
    uni = normalize_universe(args.universe) if args.universe != "FULLA" else "FULLA"
    try:
        scr = script_sha256()
    except OSError:
        scr = "<unreadable>"
    payload = {
        "live": False,
        "ok_requested": False,
        "promotion_approved": False,
        "approx": False,
        "approx_note": (
            "Formal build MUST use financials_pit.operate_profit + "
            "cashflow_pit.n_cashflow_act; ocf_to_profit is COUNT APPROX only "
            "(ban as main CRR). Count sample ≠ formal overlap (C3)."
        ),
        "rss_limit_mb": RSS_LIMIT_MB,
        "c4_kb": C4_KB,
        "stop_kb": STOP_KB,
        "hard_kb": HARD_KB,
        "universe": uni,
        "window": args.window,
        "x2_end": args.x2_end,
        "x2_window": f"{X2_START} → {X2_END}",
        "rebal_every_td": REBAL_EVERY,
        "lambda_frozen": LAMBDA_FROZEN,
        "ic_sign_expected": IC_SIGN_EXPECTED,
        "crr_L": CRR_L,
        "crr_min_q": CRR_MIN_Q,
        "vol_win": VOL_WIN,
        "vol_min": VOL_MIN,
        "industry_exclude": EXCLUDE_SW,
        "mechanism_tag": MECHANISM_TAG,
        "script": SCRIPT_REL,
        "script_sha256": scr,
        "script_sha8": scr[:8] if isinstance(scr, str) and len(scr) >= 8 else None,
        "frozen_rel": FROZEN_REL,
        "frozen_sha8": FROZEN_SHA8,
        "arch_prereg_sha8": ARCH_PREREG_SHA8,
        "forbid_ok_sha8": list(FORBID_OK_SHA8),
        "sampler_prefix": SAMPLER_PREFIX,
        "pit_main": {
            "financials": str(PIT_FIN.relative_to(ROOT)),
            "cashflow": str(PIT_CF.relative_to(ROOT)),
            "ban_ocf_to_profit_as_main": str(OCF_TO_PROFIT_APPROX_ONLY.name),
        },
        "leaf19_alpha": str(LEAF19_ALPHA_DEFAULT.relative_to(ROOT)),
        "leaf25_alpha": str(LEAF25_ALPHA_DEFAULT.relative_to(ROOT)),
        "leaf25_alpha_sha8_expect": LEAF25_ALPHA_SHA8_EXPECT,
        "primary_cli": (
            f"PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python {SCRIPT_REL} "
            f"--universe HILIQ --window x2 --x2-end {X2_END_TRADE_DATE} "
            f"--allow-real-data --arch-ok-path <OK> --out <OUT>"
        ),
        "ban_fulla": True,
        "ban_window_both": True,
        "ban_book_smoke": True,
        "ban_selfcheck": True,
        "claims": {
            "crr_16q_operate_profit": True,
            "cfooe_vol_pen": True,
            "lambda_1_0": True,
            "ic_positive_comment_only": True,
            "overlap_report_reserved": True,
            "ocf_to_profit_main": False,
            "book_smoke": False,
            "selfcheck": False,
        },
        "known_schema_static": {
            "pit_cols": KNOWN_PIT_COLS,
            "mask_cols": KNOWN_MASK_COLS,
            "alpha_out_cols": KNOWN_ALPHA_OUT_COLS,
            "sw_cols": KNOWN_SW_COLS,
            "float_cols": KNOWN_FLOAT_COLS,
        },
        "arch_conditions": {
            "C1": "script_written_this_ticket",
            "C2": "ban_ocf_to_profit_as_main_crr",
            "C3": "overlap_vs_leaf19_25_reserved",
            "C5": "avoid_A18_mem_window",
        },
        "qend_ok_filter": True,
        "r1_arch_review_sha8": "d1c71ece",
        "r2_chunk": False,
        "r3_peakcut": True,
        "chunk_mode": getattr(args, "chunk_mode", "month"),
        "prev_script_sha8": "0a264402",
        "void_ref": ["df47501c", "fe5a2c1e", "5af20222"],
        "abort_ref": "fe5a2c1e",
        "arch_review_sha8": "61830035",
        "proposal_sha8": "f111671a",
        "primary_load": "rebal_day",
        "schema": "leaf30_crr_cfooe_volpen_alpha_build_r3_peakcut",
        "sign_notes": {
            "ban_no_overlap_report": True,
            "peak_proof_required": [
                "after_daily_concat",
                "after_logmv_rebal_*",
            ],
            "rss_limit_mb": 1500,
            "x2_sign_bans_no_overlap_report_flag": True,
            "ban_restored_ok_5af20222": True,
            "ban_restored_ok_5ae077fa": True,
            "ban_blind_rerun_a2cef5af": True,
            "ban_blind_rerun_0a264402_as_ticket": True,
            "primary_load": "rebal_day",
            "ban_month_bucket_load_mode_silent_mix": True,
        },
        "note": (
            "dry-compile-only; ZERO big-table load; "
            "R3 peakcut PRIMARY=A rebal_day logmv; NOT authorized to execute; "
            "wait Arch script review → new X2 .ok "
            "(ban RESTORED 5af20222+5ae077fa); "
            "qend_ok_filter on; ban --no-overlap-report in sign; "
            "peak_proof REQUIRED (after_daily_concat + after_logmv_rebal_*); "
            "rss=1500 ban raise; chunk_mode=month; primary_load=rebal_day"
        ),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    if uni == "FULLA" or getattr(args, "window", "x2") == "both":
        print(
            "STOP: PRIMARY is HILIQ×x2; FULLA / --window both forbidden this ticket",
            file=sys.stderr,
        )
        return 2
    return 0


# ---------------------------------------------------------------------------
# PIT helpers (spirit of leaf25 _norm_pit / g1g5 first_version+single_q)
# ---------------------------------------------------------------------------


def _norm_pit(df):
    import pandas as pd

    df = df.copy()
    df["ts_code"] = df["ts_code"].astype(str)
    end_dt = pd.to_datetime(df["end_date"], errors="coerce")
    if end_dt.isna().all() and df["end_date"].notna().any():
        end_dt = pd.to_datetime(
            df["end_date"].astype(str).str.replace("-", "").str[:8],
            format="%Y%m%d",
            errors="coerce",
        )
    df["end_s"] = end_dt.dt.normalize()
    for c in ("report_type", "update_flag"):
        if c in df.columns:
            df[c] = (
                df[c]
                .astype(object)
                .where(df[c].notna(), NULL)
                .astype(str)
                .str.strip()
            )
    av = pd.to_datetime(df["available_at"], errors="coerce", utc=True)
    df["avail_sh_date"] = av.dt.tz_convert(SH).dt.tz_localize(None).dt.normalize()
    # next calendar day ≥ next session (g1g5 first_version spirit)
    df["avail"] = df["avail_sh_date"] + pd.Timedelta(days=1)
    df["qend_ok"] = df["end_s"].dt.strftime("%m%d").isin(QEND)
    return df


def _end_date_filter_value(end_type, end_lo: str):
    import pandas as pd
    import pyarrow as pa

    if pa.types.is_timestamp(end_type) or pa.types.is_date(end_type):
        return pd.Timestamp(end_lo)
    if pa.types.is_string(end_type) or pa.types.is_large_string(end_type):
        return end_lo.replace("-", "")[:8]
    raise SystemExit(
        f"STOP: unsupported end_date Arrow type {end_type!s}; "
        f"expected timestamp/date or string"
    )


def _read_pit_projected(path: Path, cols: list[str], codes: list[str], end_lo: str):
    """Column-projected + code/end_date filtered PIT read (real path only)."""
    import pyarrow.parquet as pq

    if not path.is_file():
        raise SystemExit(f"STOP: PIT missing {path}")
    schema = pq.read_schema(path)
    have = set(schema.names)
    miss = [c for c in cols if c not in have]
    if miss:
        raise SystemExit(f"STOP: {path.name} missing columns {miss}")
    # Hard ban: never treat ocf_to_profit table as this reader
    if path.name.startswith("ocf_to_profit"):
        raise SystemExit(
            "STOP: ban ocf_to_profit as main CRR source (COUNT APPROX only)"
        )
    end_lo_v = _end_date_filter_value(schema.field("end_date").type, end_lo)
    # Warm-up: need ~16+ quarters before X2 → end_lo already padded by caller
    filt = [
        ("ts_code", "in", codes),
        ("end_date", ">=", end_lo_v),
    ]
    df = pq.read_table(path, columns=cols, filters=filt).to_pandas()
    return _norm_pit(df)


def first_version(df, cols):
    """Earliest available_at per (ts_code, end_date) per field; avail = max of fields."""
    import pandas as pd

    df = df.dropna(subset=["available_at"]).copy()
    if "avail" not in df.columns:
        df["avail"] = pd.to_datetime(df.available_at.astype(str).str[:10]) + pd.Timedelta(
            days=1
        )
    df = df.sort_values("avail")
    out = None
    for c in cols:
        x = (
            df.dropna(subset=[c])
            .drop_duplicates(["ts_code", "end_date"], keep="first")[
                ["ts_code", "end_date", "avail", c]
            ]
            .rename(columns={"avail": "av_" + c})
        )
        out = x if out is None else out.merge(x, on=["ts_code", "end_date"], how="outer")
    out["avail"] = out[["av_" + c for c in cols]].max(1)
    return out[["ts_code", "end_date", "avail"] + cols]


def single_q(df, col):
    """YTD → single-quarter: Q1=YTD; else diff vs prior quarter same year."""
    import numpy as np
    import pandas as pd

    df = df.sort_values(["ts_code", "end_date"]).copy()
    df["y"] = df.end_date.dt.year
    df["q"] = df.end_date.dt.quarter
    prev = df.groupby("ts_code")[col].shift(1)
    py = df.groupby("ts_code").y.shift(1)
    pq_ = df.groupby("ts_code").q.shift(1)
    ok_prev = (py == df.y) & (pq_ == df.q - 1)
    df[col + "_q"] = np.where(
        df.q == 1, df[col], np.where(ok_prev, df[col] - prev, np.nan)
    )
    return df


def ols_resid(y, X):
    import numpy as np

    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    return y - X @ b


def pct_rank(s):
    """Pool-internal percentile rank in (0,1]; NaN stays NaN."""
    import numpy as np
    import pandas as pd

    s = pd.Series(s, dtype="float64")
    out = s.rank(method="average", pct=True)
    out = out.where(s.notna(), np.nan)
    return out.to_numpy()


# ---------------------------------------------------------------------------
# Universe / industry / float mktcap (real path)
# ---------------------------------------------------------------------------


def _load_hiliq_chunk_members(mask_path: Path, start: str, end: str):
    import pandas as pd
    import pyarrow.parquet as pq

    if not mask_path.is_file():
        raise SystemExit(
            f"STOP: HI_LIQ mask missing at {mask_path}; "
            f"refuse silent FULLA / empty-universe degradation"
        )
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    tab = pq.read_table(
        mask_path,
        columns=["date", "instrument", "in_universe"],
        filters=[
            ("date", ">=", start_ts),
            ("date", "<=", end_ts),
            ("in_universe", "==", True),
        ],
    )
    df = tab.to_pandas()
    if df.empty:
        raise SystemExit(
            f"STOP: HI_LIQ mask empty for chunk [{start}, {end}] at {mask_path}"
        )
    df["date"] = pd.to_datetime(df["date"]).dt.normalize()
    df["instrument"] = df["instrument"].astype(str)
    by_day: dict = {}
    for d, g in df.groupby("date", sort=True):
        by_day[pd.Timestamp(d)] = sorted(set(g["instrument"].tolist()))
    codes = sorted({c for v in by_day.values() for c in v})
    return by_day, codes, {
        "mask_path": str(
            mask_path.relative_to(ROOT) if mask_path.is_relative_to(ROOT) else mask_path
        ),
        "mask_sha256": sha256_file(mask_path),
        "n_codes_union": len(codes),
        "n_days_with_members": len(by_day),
    }


def _load_sw_table(sw_path: Path):
    import pandas as pd
    import pyarrow.parquet as pq

    t = pq.read_table(
        sw_path,
        columns=[
            "instrument_id",
            "sw_code",
            "sw_name",
            "in_date",
            "out_date",
            "available_at",
        ],
    )
    sw = t.to_pandas()
    sw["ts_code"] = sw["instrument_id"].map(to_ts)
    sw["in_date"] = pd.to_datetime(sw["in_date"], errors="coerce")
    sw["out_date"] = pd.to_datetime(sw["out_date"], errors="coerce")
    sw["available_at"] = pd.to_datetime(sw["available_at"], errors="coerce")
    return sw


def _sw_asof_codes(sw, asof, codes: list[str]) -> dict[str, str]:
    """Return {ts_code: sw_code} as-of date for given codes (hard-mask uses same table)."""
    import pandas as pd

    asof = pd.Timestamp(asof)
    sub = sw[sw["ts_code"].isin(codes)].copy()
    ok = (sub["in_date"].isna() | (sub["in_date"] <= asof)) & (
        sub["out_date"].isna() | (sub["out_date"] > asof)
    )
    avail_ok = sub["available_at"].isna() | (sub["available_at"] <= asof)
    sub = sub.loc[ok & avail_ok].sort_values(["ts_code", "in_date"])
    # latest in_date wins
    sub = sub.drop_duplicates("ts_code", keep="last")
    return dict(zip(sub["ts_code"], sub["sw_code"].astype(str)))


def _exclude_set_asof(sw, asof) -> set[str]:
    import pandas as pd

    asof = pd.Timestamp(asof)
    codes = set(EXCLUDE_SW.values())
    names = set(EXCLUDE_SW.keys())
    m = sw["sw_code"].isin(codes) | sw["sw_name"].isin(names)
    sub = sw.loc[m].copy()
    ok = (sub["in_date"].isna() | (sub["in_date"] <= asof)) & (
        sub["out_date"].isna() | (sub["out_date"] > asof)
    )
    avail_ok = sub["available_at"].isna() | (sub["available_at"] <= asof)
    return set(sub.loc[ok & avail_ok, "ts_code"].astype(str))


def _load_logmv_t1(float_path: Path, dates: list, codes: list[str]):
    """log float mktcap T−1: map trade_date→previous available; keys ts_code."""
    import numpy as np
    import pandas as pd
    import pyarrow.parquet as pq

    if not float_path.is_file():
        raise SystemExit(f"STOP: float_mktcap missing {float_path}")
    # Need one day before first date
    dmin = (min(dates) - pd.Timedelta(days=10)).strftime("%Y%m%d")
    dmax = max(dates).strftime("%Y%m%d")
    # instrument_id filter: reverse map
    id_map = {}
    for c in codes:
        if "." in c:
            code, mkt = c.split(".", 1)
            id_map[f"{mkt.lower()}.{code}"] = c
    ids = list(id_map.keys())
    schema = pq.read_schema(float_path)
    td_type = schema.field("trade_date").type
    import pyarrow as pa

    if pa.types.is_string(td_type) or pa.types.is_large_string(td_type):
        lo, hi = dmin, dmax
    else:
        lo, hi = pd.Timestamp(min(dates) - pd.Timedelta(days=10)), pd.Timestamp(
            max(dates)
        )
    # chunk ids to avoid huge IN filters
    frames = []
    step = 800
    for i in range(0, len(ids), step):
        chunk = ids[i : i + step]
        t = pq.read_table(
            float_path,
            columns=["instrument_id", "trade_date", "float_mktcap"],
            filters=[
                ("instrument_id", "in", chunk),
                ("trade_date", ">=", lo),
                ("trade_date", "<=", hi),
            ],
        )
        frames.append(t.to_pandas())
    if not frames:
        return {}
    df = pd.concat(frames, ignore_index=True)
    df["ts_code"] = df["instrument_id"].map(to_ts)
    df["trade_date"] = pd.to_datetime(df["trade_date"].astype(str).str.replace("-", "").str[:8], format="%Y%m%d", errors="coerce")
    df = df.dropna(subset=["trade_date", "float_mktcap"])
    df["logmv"] = np.log(df["float_mktcap"].astype(float).clip(lower=1.0))
    df = df.sort_values(["ts_code", "trade_date"])
    # For each asof date, take last trade_date < asof (T−1 PIT)
    out: dict[tuple, float] = {}
    by_code = {k: g for k, g in df.groupby("ts_code", sort=False)}
    for d in dates:
        d = pd.Timestamp(d)
        for c in codes:
            g = by_code.get(c)
            if g is None:
                continue
            prev = g[g["trade_date"] < d]
            if prev.empty:
                continue
            out[(d, c)] = float(prev["logmv"].iloc[-1])
    return out


# ---------------------------------------------------------------------------
# Fund panel: single-q → CRR + CFOOE ε → vol_pen
# ---------------------------------------------------------------------------


def build_fund_quarter_panel(codes: list[str], end_lo: str):
    """Build per-(ts_code,end_date) panel with OP_q, OCF_q, CRR, eps, vol_pen, avail.

    R1 (Arch d1c71ece): after PIT read, keep only qend_ok calendar quarter-ends
    (0331/0630/0930/1231) so rolling(16) spans 16 calendar quarters.
    """
    import numpy as np
    import pandas as pd

    fin = _read_pit_projected(
        PIT_FIN, KEY_PIT + ["operate_profit"], codes, end_lo
    )
    cf = _read_pit_projected(
        PIT_CF, KEY_PIT + ["n_cashflow_act"], codes, end_lo
    )
    # R1 (Arch d1c71ece): keep only calendar quarter-ends so rolling(16)=16 calendar quarters
    if "qend_ok" not in fin.columns or "qend_ok" not in cf.columns:
        raise SystemExit(
            "STOP: qend_ok missing after _norm_pit (R1 Arch d1c71ece); refuse silent skip"
        )
    fin = fin[fin["qend_ok"]]
    cf = cf[cf["qend_ok"]]
    fin = fin[fin["report_type"] == "1"]
    cf = cf[cf["report_type"] == "1"]
    fi = first_version(fin, ["operate_profit"])
    bc = first_version(cf, ["n_cashflow_act"])
    d = fi.merge(bc, on=["ts_code", "end_date"], how="inner", suffixes=("", "_b"))
    d["avail"] = d[["avail", "avail_b"]].max(1)
    d["end_date"] = pd.to_datetime(d["end_date"])
    # R1 belt: re-assert calendar QEND after merge (mmdd ∈ QEND)
    d = d[d["end_date"].dt.strftime("%m%d").isin(QEND)]
    for c in ("operate_profit", "n_cashflow_act"):
        d = single_q(d, c)
    d = d.sort_values(["ts_code", "end_date"])
    d["ocf_q"] = d["n_cashflow_act_q"]
    d["op_q"] = d["operate_profit_q"]
    # CRR over trailing L quarters
    g = d.groupby("ts_code", sort=False)

    def _crr_row(s_ocf, s_op):
        # rolling sum with min_periods=CRR_MIN_Q
        ocf_sum = s_ocf.rolling(CRR_L, min_periods=CRR_MIN_Q).sum()
        op_sum = s_op.rolling(CRR_L, min_periods=CRR_MIN_Q).sum()
        n_valid = s_ocf.notna().astype(int).rolling(CRR_L, min_periods=1).sum()
        n_valid_op = s_op.notna().astype(int).rolling(CRR_L, min_periods=1).sum()
        n = np.minimum(n_valid, n_valid_op)
        crr = ocf_sum / op_sum
        crr = crr.where((n >= CRR_MIN_Q) & (op_sum > 0))
        return crr

    d["crr"] = g.apply(
        lambda x: _crr_row(x["ocf_q"], x["op_q"]), include_groups=False
    ).reset_index(level=0, drop=True)
    # single-q ratio for CFOOE input
    d["cfooe_raw"] = np.where(
        (d["op_q"].notna()) & (d["op_q"] > 0) & d["ocf_q"].notna(),
        d["ocf_q"] / d["op_q"],
        np.nan,
    )
    d = d.replace([np.inf, -np.inf], np.nan)
    return d[
        [
            "ts_code",
            "end_date",
            "avail",
            "ocf_q",
            "op_q",
            "crr",
            "cfooe_raw",
        ]
    ].copy()


def attach_eps_vol_pen(panel, sw, logmv_by_end, rss_check=None):
    """Cross-section OLS of cfooe_raw on SW dummy + logmv at each end_date; then vol_pen.

    R2: optional rss_check(label) every 4 end_dates to close after_fund→vol_pen gap.
    """
    import numpy as np
    import pandas as pd

    rows = []
    for i_end, (end, g) in enumerate(panel.groupby("end_date", sort=True)):
        g = g.dropna(subset=["cfooe_raw"]).copy()
        if len(g) < 30:
            g["eps"] = np.nan
            rows.append(g)
            continue
        # asof for industry ≈ end_date + typical publish lag; use avail median as proxy day
        asof = pd.Timestamp(g["avail"].median())
        sw_map = _sw_asof_codes(sw, asof, g["ts_code"].tolist())
        excl = _exclude_set_asof(sw, asof)
        g = g[~g["ts_code"].isin(excl)].copy()
        if len(g) < 30:
            g["eps"] = np.nan
            rows.append(g)
            continue
        g["sw_code"] = g["ts_code"].map(sw_map)
        g = g[g["sw_code"].notna()].copy()
        # logmv: prefer precomputed by (end, code); else nan drop
        g["logmv"] = g["ts_code"].map(
            lambda c, e=end: logmv_by_end.get((pd.Timestamp(e), c))
        )
        g = g.dropna(subset=["logmv", "sw_code", "cfooe_raw"])
        if len(g) < 30:
            g["eps"] = np.nan
            rows.append(g)
            continue
        D = pd.get_dummies(g["sw_code"], drop_first=True).to_numpy(float)
        X = np.column_stack([np.ones(len(g)), D, g["logmv"].to_numpy(float)])
        y = g["cfooe_raw"].to_numpy(float)
        g = g.copy()
        g["eps"] = ols_resid(y, X)
        rows.append(g)
        if rss_check is not None and (i_end + 1) % 4 == 0:
            rss_check(f"vol_pen_end_{pd.Timestamp(end).strftime('%Y%m%d')}")
    if not rows:
        panel = panel.copy()
        panel["eps"] = np.nan
        panel["vol_pen"] = np.nan
        return panel
    out = pd.concat(rows, ignore_index=True)
    out = out.sort_values(["ts_code", "end_date"])
    out["vol_pen"] = (
        out.groupby("ts_code")["eps"]
        .transform(lambda s: s.rolling(VOL_WIN, min_periods=VOL_MIN).std())
    )
    # merge vol_pen/eps back onto full panel keys
    m = out[["ts_code", "end_date", "eps", "vol_pen"]]
    base = panel.merge(m, on=["ts_code", "end_date"], how="left")
    return base


# ---------------------------------------------------------------------------
# C3 overlap report (reserved; formal α only — count sample ≠ this)
# ---------------------------------------------------------------------------


def spearman_rho(a, b) -> float:
    import numpy as np
    import pandas as pd

    if len(a) < 5:
        return float("nan")
    ra = pd.Series(a).rank().to_numpy()
    rb = pd.Series(b).rank().to_numpy()
    if np.nanstd(ra) == 0 or np.nanstd(rb) == 0:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def top_jaccard(codes_a, scores_a, codes_b, scores_b, k: int = 20) -> float:
    import numpy as np
    import pandas as pd

    if len(codes_a) == 0 or len(codes_b) == 0:
        return float("nan")
    sa = pd.Series(scores_a, index=codes_a)
    sb = pd.Series(scores_b, index=codes_b)
    ta = set(sa.nlargest(min(k, len(sa))).index)
    tb = set(sb.nlargest(min(k, len(sb))).index)
    u = ta | tb
    if not u:
        return float("nan")
    return float(len(ta & tb) / len(u))


def write_overlap_report(
    alpha_df,
    out_path: Path,
    leaf19_path: Path,
    leaf25_path: Path,
    sample_n: int = 6,
) -> dict:
    """C3: Jaccard top20 + Spearman ρ vs leaf19/leaf25 on uniform rebal sample.

    NOTE: count-gate APPROX sampling ≠ this formal overlap (must use full CRR α).
    """
    import numpy as np
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq

    alpha_df = alpha_df.copy()
    alpha_df["trade_date"] = pd.to_datetime(alpha_df["trade_date"])
    days = sorted(alpha_df["trade_date"].unique())
    if not days:
        payload = {"error": "empty_alpha", "note": "count_sample_neq_formal"}
        out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
        return payload
    # rebal-like: every REBAL_EVERY among unique days
    rebal = days[::REBAL_EVERY]
    if rebal[-1] != days[-1]:
        rebal = list(rebal) + [days[-1]]
    if len(rebal) <= sample_n:
        sample = list(rebal)
    else:
        idxs = np.linspace(0, len(rebal) - 1, sample_n)
        sample = []
        seen = set()
        for i in idxs:
            d = rebal[int(round(i))]
            if d not in seen:
                sample.append(d)
                seen.add(d)

    def _load_other(path: Path, date_col: str, inst_col: str):
        if not path.is_file():
            return None
        schema = pq.read_schema(path)
        field = schema.field(date_col)
        is_str = pa.types.is_string(field.type) or pa.types.is_large_string(field.type)
        cols = [date_col, inst_col, "alpha"]
        if is_str:
            dmin = min(sample).strftime("%Y-%m-%d")
            dmax = max(sample).strftime("%Y-%m-%d")
            t = pq.read_table(
                path, columns=cols, filters=[(date_col, ">=", dmin), (date_col, "<=", dmax)]
            )
        else:
            t = pq.read_table(
                path,
                columns=cols,
                filters=[
                    (date_col, ">=", min(sample).to_datetime64()),
                    (date_col, "<=", max(sample).to_datetime64()),
                ],
            )
        df = t.to_pandas()
        df[date_col] = pd.to_datetime(df[date_col])
        want = set(pd.Timestamp(d) for d in sample)
        df = df[df[date_col].isin(want)].copy()
        df.rename(columns={date_col: "date", inst_col: "instrument"}, inplace=True)
        df["instrument"] = df["instrument"].astype(str)
        return df

    # leaf19 uses date/instrument; leaf25 uses trade_date/ts_code
    l19 = _load_other(leaf19_path, "date", "instrument")
    if l19 is None:
        # try trade_date/ts_code
        l19 = _load_other(leaf19_path, "trade_date", "ts_code")
    l25 = _load_other(leaf25_path, "trade_date", "ts_code")
    if l25 is None:
        l25 = _load_other(leaf25_path, "date", "instrument")

    rows = []
    for d in sample:
        a = alpha_df[alpha_df["trade_date"] == pd.Timestamp(d)]
        if a.empty:
            continue
        codes = a["ts_code"].astype(str).tolist()
        scores = a["alpha"].to_numpy(float)
        ent = {"date": str(pd.Timestamp(d).date()), "n_alpha": len(codes)}
        for tag, other in (("leaf19", l19), ("leaf25", l25)):
            if other is None:
                ent[f"rho_{tag}"] = None
                ent[f"j20_{tag}"] = None
                continue
            o = other[other["date"] == pd.Timestamp(d)]
            if o.empty:
                ent[f"rho_{tag}"] = None
                ent[f"j20_{tag}"] = None
                continue
            m = pd.DataFrame({"instrument": codes, "a": scores}).merge(
                o.rename(columns={"alpha": "b"})[["instrument", "b"]],
                on="instrument",
                how="inner",
            )
            ent[f"rho_{tag}"] = spearman_rho(m["a"].to_numpy(), m["b"].to_numpy())
            ent[f"j20_{tag}"] = top_jaccard(
                codes, scores, o["instrument"].tolist(), o["alpha"].to_numpy(float), 20
            )
            # hard gate flags (disclosure only here)
            ent[f"jaccard_hard_reject_{tag}"] = bool(
                ent[f"j20_{tag}"] is not None and ent[f"j20_{tag}"] >= 0.7
            )
            ent[f"strength_filter_{tag}"] = bool(
                ent[f"rho_{tag}"] is not None and ent[f"rho_{tag}"] > 0.5
            )
        rows.append(ent)

    payload = {
        "schema": "leaf30_overlap_vs_leaf19_25",
        "note": (
            "C3 formal overlap on full CRR α; count-gate APPROX sample ≠ this file. "
            "Jaccard≥0.7 hard reject; ρ>0.5 strength filter only."
        ),
        "lambda": LAMBDA_FROZEN,
        "sample_dates": [str(pd.Timestamp(d).date()) for d in sample],
        "leaf19_path": str(
            leaf19_path.relative_to(ROOT)
            if leaf19_path.is_relative_to(ROOT)
            else leaf19_path
        ),
        "leaf25_path": str(
            leaf25_path.relative_to(ROOT)
            if leaf25_path.is_relative_to(ROOT)
            else leaf25_path
        ),
        "leaf25_sha8": (
            sha256_file(leaf25_path)[:8] if leaf25_path.is_file() else None
        ),
        "rows": rows,
        "live": False,
    }
    tmp = out_path.with_suffix(out_path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(out_path)
    return payload


# ---------------------------------------------------------------------------
# Alpha build (real path)
# ---------------------------------------------------------------------------


def _month_chunks(start: str, end: str) -> list[dict]:
    import pandas as pd

    s = pd.Timestamp(start)
    e = pd.Timestamp(end)
    chunks = []
    cur = pd.Timestamp(s.year, s.month, 1)
    cid = 0
    while cur <= e:
        nxt = (cur + pd.offsets.MonthBegin(1)) - pd.Timedelta(days=1)
        c0 = max(cur, s)
        c1 = min(nxt, e)
        if c0 <= c1:
            chunks.append(
                {
                    "chunk_id": cid,
                    "start": c0.strftime("%Y-%m-%d"),
                    "end": c1.strftime("%Y-%m-%d"),
                }
            )
            cid += 1
        cur = cur + pd.offsets.MonthBegin(1)
    return chunks


def build_alpha_for_window(args) -> tuple:
    """Build daily base-α for HILIQ×x2 (R2 month-chunk peak path). Returns (alpha_df, meta)."""
    import numpy as np
    import pandas as pd

    chunk_mode = getattr(args, "chunk_mode", "month") or "month"
    if chunk_mode != "month":
        raise SystemExit(
            f"STOP: --chunk-mode must be 'month' (got {chunk_mode!r}); "
            "ban whole-window densify path"
        )

    stage("build_start")
    split_kb = int(0.85 * args.c4_kb)

    def _rss(label: str) -> int:
        return check_rss(
            label,
            rss_limit_mb=args.rss_limit_mb,
            c4_kb=args.c4_kb,
            hard_kb=args.hard_kb,
            split_kb=split_kb,
        )

    _rss("build_start")

    # Warm-up for 16Q: pull PIT from ~2019
    end_lo = "2019-01-01"
    by_day, codes, mask_meta = _load_hiliq_chunk_members(
        Path(args.hi_liq_mask), X2_START, X2_END
    )
    _rss("after_mask")
    sw = _load_sw_table(Path(args.sw_l1))
    _rss("after_sw")

    panel = build_fund_quarter_panel(codes, end_lo)
    _rss("after_fund")

    # R2: load logmv for avail days by **calendar-month buckets** (ban full densify).
    # r1 bug: comment said month-ends but `avail_sample = all normalize(avail)` → peak gap.
    avail_days = sorted(
        {pd.Timestamp(a).normalize() for a in panel["avail"].dropna().unique()}
    )
    buckets: dict[tuple[int, int], list] = {}
    for a in avail_days:
        buckets.setdefault((int(a.year), int(a.month)), []).append(a)

    logmv_by_end: dict = {}
    tmp_base = panel.dropna(subset=["avail"]).copy()
    tmp_base["_avail_n"] = pd.to_datetime(tmp_base["avail"]).dt.normalize()
    for (yy, mm) in sorted(buckets.keys()):
        dates_m = buckets[(yy, mm)]
        logmv_avail = _load_logmv_t1(Path(args.float_mktcap), dates_m, codes)
        mask = tmp_base["_avail_n"].isin(dates_m)
        sub = tmp_base.loc[mask, ["end_date", "avail", "ts_code"]]
        for end, g in sub.groupby("end_date"):
            for _, r in g.iterrows():
                key_a = (pd.Timestamp(r["avail"]).normalize(), r["ts_code"])
                if key_a in logmv_avail:
                    logmv_by_end[(pd.Timestamp(end), r["ts_code"])] = logmv_avail[key_a]
        del logmv_avail, sub
        gc.collect()
        _rss(f"after_logmv_avail_{yy}{mm:02d}")
    del tmp_base
    gc.collect()
    _rss("after_logmv_avail")

    panel = attach_eps_vol_pen(panel, sw, logmv_by_end, rss_check=_rss)
    del logmv_by_end
    gc.collect()
    _rss("after_vol_pen")

    # Rebalance dates from HI_LIQ calendar
    all_days = sorted(by_day.keys())
    rebal_idx = list(range(0, len(all_days), REBAL_EVERY))
    if rebal_idx[-1] != len(all_days) - 1:
        rebal_idx.append(len(all_days) - 1)
    rebal_days = [all_days[i] for i in rebal_idx]

    # R3 PRIMARY=A: per-rebal-day logmv T-1 lazy load (ban whole-window preload)
    # Point-in-time: for each rebal day, take latest fund row with avail <= day
    panel = panel.sort_values(["ts_code", "avail", "end_date"])
    alpha_rebal_rows = []
    coverage = []
    for d in rebal_days:
        logmv_d = _load_logmv_t1(Path(args.float_mktcap), [d], codes)
        members = set(by_day.get(pd.Timestamp(d), []))
        excl = _exclude_set_asof(sw, d)
        members = members - excl
        if not members:
            coverage.append({"date": str(pd.Timestamp(d).date()), "n": 0})
            del logmv_d
            gc.collect()
            _rss(f"after_logmv_rebal_{pd.Timestamp(d).strftime('%Y%m%d')}")
            continue
        sub = panel[(panel["avail"] <= pd.Timestamp(d)) & panel["ts_code"].isin(members)]
        if sub.empty:
            coverage.append({"date": str(pd.Timestamp(d).date()), "n": 0})
            del logmv_d
            gc.collect()
            _rss(f"after_logmv_rebal_{pd.Timestamp(d).strftime('%Y%m%d')}")
            continue
        latest = sub.sort_values(["ts_code", "avail", "end_date"]).drop_duplicates(
            "ts_code", keep="last"
        )
        latest = latest.dropna(subset=["crr", "vol_pen"])
        if len(latest) < 50:
            coverage.append({"date": str(pd.Timestamp(d).date()), "n": int(len(latest))})
        if latest.empty:
            coverage.append({"date": str(pd.Timestamp(d).date()), "n": 0})
            del logmv_d
            gc.collect()
            _rss(f"after_logmv_rebal_{pd.Timestamp(d).strftime('%Y%m%d')}")
            continue
        r_crr = pct_rank(latest["crr"].to_numpy(float))
        r_vol = pct_rank(latest["vol_pen"].to_numpy(float))
        # FROZEN: α_raw = rank(CRR) − λ·rank(vol_pen); IC expected positive
        raw = r_crr - LAMBDA_FROZEN * r_vol
        latest = latest.copy()
        latest["alpha_raw"] = raw
        sw_map = _sw_asof_codes(sw, d, latest["ts_code"].tolist())
        latest["sw_code"] = latest["ts_code"].map(sw_map)
        latest["logmv"] = latest["ts_code"].map(
            lambda c, dd=d: logmv_d.get((pd.Timestamp(dd), c))
        )
        latest = latest.dropna(subset=["sw_code", "logmv", "alpha_raw"])
        if latest.empty:
            coverage.append({"date": str(pd.Timestamp(d).date()), "n": 0})
            del logmv_d
            gc.collect()
            _rss(f"after_logmv_rebal_{pd.Timestamp(d).strftime('%Y%m%d')}")
            continue
        latest["alpha_dm"] = latest["alpha_raw"] - latest.groupby("sw_code")[
            "alpha_raw"
        ].transform("mean")
        X = np.column_stack(
            [np.ones(len(latest)), latest["logmv"].to_numpy(float)]
        )
        latest["alpha"] = ols_resid(latest["alpha_dm"].to_numpy(float), X)
        coverage.append({"date": str(pd.Timestamp(d).date()), "n": int(len(latest))})
        for _, r in latest.iterrows():
            alpha_rebal_rows.append(
                {
                    "rebal_date": pd.Timestamp(d),
                    "ts_code": r["ts_code"],
                    "alpha": float(r["alpha"]),
                }
            )
        del logmv_d
        gc.collect()
        _rss(f"after_logmv_rebal_{pd.Timestamp(d).strftime('%Y%m%d')}")

    if not alpha_rebal_rows:
        raise SystemExit("STOP: zero alpha rows (check PIT / HI_LIQ / CRR completeness)")

    A = pd.DataFrame(alpha_rebal_rows)
    del alpha_rebal_rows
    gc.collect()
    A = A.sort_values(["rebal_date", "ts_code"])
    rebal_sorted = sorted(A["rebal_date"].unique())

    # R2: daily expand by month chunks → temp parquet; ban stacking full-window daily_rows
    import pyarrow as pa
    import pyarrow.parquet as pq

    month_chunks = _month_chunks(X2_START, X2_END)
    # temp under /tmp/quantlab_leaf30_crr_r2_*
    ts_tag = datetime.now(ET).strftime("%Y%m%d_%H%M%S")
    tmp_root = Path(f"{SAMPLER_PREFIX}chunk_{ts_tag}")
    assert_tmp_quantlab(tmp_root, "r2-month-chunk-tmp")
    tmp_root.mkdir(parents=True, exist_ok=True)
    part_paths: list[Path] = []

    for ch in month_chunks:
        c0 = pd.Timestamp(ch["start"])
        c1 = pd.Timestamp(ch["end"])
        days_in = [d for d in all_days if c0 <= pd.Timestamp(d) <= c1]
        if not days_in:
            continue
        # Pre-index A by rebal for this month's needed rebals
        month_rows = []
        for d in days_in:
            prev = [r for r in rebal_sorted if r <= d]
            if not prev:
                continue
            rd = prev[-1]
            members = set(by_day.get(pd.Timestamp(d), []))
            excl = _exclude_set_asof(sw, d)
            members = members - excl
            g = A[A["rebal_date"] == rd]
            g = g[g["ts_code"].isin(members)]
            if g.empty:
                continue
            # vectorized append (avoid per-row Python dict when possible)
            td = pd.Timestamp(d).strftime("%Y-%m-%d")
            month_rows.append(
                pd.DataFrame(
                    {
                        "trade_date": td,
                        "ts_code": g["ts_code"].astype(str).to_numpy(),
                        "alpha": g["alpha"].astype(float).to_numpy(),
                    }
                )
            )
        if month_rows:
            cdf = pd.concat(month_rows, ignore_index=True)
            p = tmp_root / f"chunk_{int(ch['chunk_id']):03d}.parquet"
            table = pa.Table.from_pandas(cdf, preserve_index=False)
            tmpf = p.with_suffix(p.suffix + ".tmp")
            pq.write_table(table, tmpf, compression="zstd")
            tmpf.replace(p)
            part_paths.append(p)
            del cdf, table, month_rows
        else:
            del month_rows
        gc.collect()
        _rss(f"month_chunk_{int(ch['chunk_id']):03d}_{ch['start'][:7]}")

    if not part_paths:
        raise SystemExit("STOP: zero daily alpha rows after month-chunk expand")

    frames = [pd.read_parquet(p) for p in part_paths]
    alpha_df = pd.concat(frames, ignore_index=True)
    del frames
    gc.collect()
    _rss("after_daily_concat")

    # best-effort cleanup of temp chunks (keep dir if sample_dir requested)
    if args.sample_dir is None:
        for p in part_paths:
            try:
                p.unlink(missing_ok=True)
            except OSError:
                pass
        try:
            tmp_root.rmdir()
        except OSError:
            pass

    med_cov = float(np.median([c["n"] for c in coverage])) if coverage else 0.0
    meta = {
        "schema": "leaf30_crr_cfooe_volpen_alpha_build_r3_peakcut",
        "prev_script_sha8": "0a264402",
        "void_ref": ["df47501c", "fe5a2c1e", "5af20222"],
        "abort_ref": "fe5a2c1e",
        "arch_review_sha8": "61830035",
        "proposal_sha8": "f111671a",
        "primary_load": "rebal_day",
        "r2_chunk": False,
        "r3_peakcut": True,
        "chunk_mode": chunk_mode,
        "qend_ok_filter": True,
        "live": False,
        "promotion_approved": False,
        "ok_requested": False,
        "approx": False,
        "approx_note": (
            "Formal 16Q OP CRR + CFOOE vol_pen; NOT ocf_to_profit COUNT APPROX"
        ),
        "mechanism_tag": MECHANISM_TAG,
        "lambda": LAMBDA_FROZEN,
        "ic_sign_expected": IC_SIGN_EXPECTED,
        "industry_exclude": EXCLUDE_SW,
        "crr_L": CRR_L,
        "crr_min_q": CRR_MIN_Q,
        "vol_win": VOL_WIN,
        "vol_min": VOL_MIN,
        "rebal_every_td": REBAL_EVERY,
        "universe": "HILIQ",
        "window": "x2",
        "x2_start": X2_START,
        "x2_end": X2_END,
        "mask_meta": mask_meta,
        "coverage_rebal": coverage,
        "coverage_median": med_cov,
        "coverage_gate_median_ge_300": bool(med_cov >= 300),
        "n_daily_rows": int(len(alpha_df)),
        "n_month_chunks_written": int(len(part_paths)),
        "frozen_sha8": FROZEN_SHA8,
        "arch_prereg_sha8": ARCH_PREREG_SHA8,
        "sampler_prefix": SAMPLER_PREFIX,
        "rss_limit_mb": args.rss_limit_mb,
        "peak_kb": peak_kb(),
        "created_et": datetime.now(ET).strftime("%Y-%m-%dT%H:%M:%S%z"),
        "notes": [
            "α_raw = rank(CRR) − 1.0·rank(vol_pen); then SW L1 demean + logmv OLS resid",
            "IC expected positive (comment pin); script does not compute returns",
            "Ban ocf_to_profit as main; ban FULLA; ban Book-Smoke/selfcheck",
            "R2 retained: month-bucket avail logmv + month-chunk daily expand",
            "R3 PRIMARY=A: per-rebal-day logmv lazy load; ban whole-window logmv_rebal",
            "C3 overlap written when --overlap-report / default real path",
            "Ban RESTORED .ok 5af20222+5ae077fa; ban blind rerun a2cef5af/0a264402-as-ticket; ban raise rss",
        ],
    }
    return alpha_df, meta



def run_build(args) -> int:
    import pyarrow as pa
    import pyarrow.parquet as pq

    uni = normalize_universe(args.universe)
    if uni == "FULLA":
        print("STOP: FULLA forbidden this ticket (PRIMARY HILIQ×x2)", file=sys.stderr)
        return 2
    if args.window != "x2":
        print(
            f"STOP: --window must be x2 this ticket (got {args.window})",
            file=sys.stderr,
        )
        return 2
    if str(args.x2_end).replace("-", "") != X2_END_TRADE_DATE:
        print(
            f"STOP: --x2-end must be {X2_END_TRADE_DATE} (got {args.x2_end})",
            file=sys.stderr,
        )
        return 2
    if args.rss_limit_mb > RSS_LIMIT_MB:
        print("STOP: ban raise rss_limit above 1500", file=sys.stderr)
        return 2
    if args.c4_kb > C4_KB or args.stop_kb > STOP_KB or args.hard_kb > HARD_KB:
        print(
            "STOP: ban raise C4/stop/hard above 1331200/1484800/1536000",
            file=sys.stderr,
        )
        return 2

    if args.sample_dir is not None:
        assert_tmp_quantlab(args.sample_dir, "sample-dir")
        # prefix check
        sd = str(args.sample_dir.resolve())
        if not sd.startswith(SAMPLER_PREFIX.rstrip("_")) and not sd.startswith(
            "/tmp/quantlab_leaf30_crr_r3"
        ):
            # allow /tmp/quantlab_leaf30_crr_r3_* only
            if "/quantlab_leaf30_crr_r3" not in sd:
                raise SystemExit(
                    f"STOP: sampler must be under {SAMPLER_PREFIX}* got={sd}"
                )
        args.sample_dir.mkdir(parents=True, exist_ok=True)

    # Real-path gate (no silent default run)
    if not args.allow_real_data:
        print(
            "STOP: real build requires --allow-real-data + --arch-ok-path "
            "(use --dry-compile-only for static pins)",
            file=sys.stderr,
        )
        return 2
    if args.arch_ok_path is None or not Path(args.arch_ok_path).is_file():
        print(
            "STOP: --allow-real-data requires existing --arch-ok-path",
            file=sys.stderr,
        )
        return 2
    # --execute optional; if present still requires the same gate (already satisfied)
    ok_sha = sha256_file(Path(args.arch_ok_path))
    if ok_sha[:8] in FORBID_OK_SHA8:
        print(
            f"STOP: ban reuse forbid/CONSUMED/VOID .ok sha={ok_sha} sha8={ok_sha[:8]}",
            file=sys.stderr,
        )
        return 2

    if args.out is None:
        print("STOP: --out is required for build", file=sys.stderr)
        return 2

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    alpha_df, meta = build_alpha_for_window(args)
    et_ts = datetime.now(ET).strftime("%Y%m%d_%H%M%S")
    final_name = f"alpha_HILIQ_x2_{et_ts}.parquet"
    final_path = out / final_name
    table = pa.Table.from_pandas(alpha_df, preserve_index=False)
    tmpf = final_path.with_suffix(final_path.suffix + ".tmp")
    pq.write_table(table, tmpf, compression="zstd")
    tmpf.replace(final_path)

    scr = script_sha256()
    meta.update(
        {
            "script": SCRIPT_REL,
            "script_sha256": scr,
            "script_sha8": scr[:8],
            "prev_script_sha8": "0a264402",
            "void_ref": ["df47501c", "fe5a2c1e", "5af20222"],
            "abort_ref": "fe5a2c1e",
            "arch_review_sha8": "61830035",
            "proposal_sha8": "f111671a",
            "primary_load": "rebal_day",
            "r3_peakcut": True,
            "chunk_mode": getattr(args, "chunk_mode", "month"),
            "arch_ok_path": str(args.arch_ok_path),
            "arch_ok_sha256": ok_sha,
            "arch_ok_sha8": ok_sha[:8],
            "final_alpha": final_name,
            "forbid_ok_sha8": list(FORBID_OK_SHA8),
            "execute_flag": bool(args.execute),
            "pit_shas": {
                "financials": sha256_file(PIT_FIN) if PIT_FIN.is_file() else None,
                "cashflow": sha256_file(PIT_CF) if PIT_CF.is_file() else None,
            },
        }
    )

    # C3 overlap (default on real path unless --no-overlap-report)
    if args.overlap_report or not args.no_overlap_report:
        ov_path = out / "overlap_vs_leaf19_25.json"
        try:
            ov = write_overlap_report(
                alpha_df,
                ov_path,
                Path(args.leaf19_alpha),
                Path(args.leaf25_alpha),
            )
            meta["overlap_report"] = str(ov_path.name)
            meta["overlap_summary"] = {
                "n_rows": len(ov.get("rows", [])),
                "leaf25_sha8": ov.get("leaf25_sha8"),
            }
        except Exception as e:  # noqa: BLE001 — disclose; do not hide
            meta["overlap_report_error"] = repr(e)

    meta_path = out / "run_meta.json"
    tmpm = meta_path.with_suffix(".json.tmp")
    tmpm.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmpm.replace(meta_path)

    pk = peak_kb()
    print(
        f"OK leaf30_crr_alpha_r3_peakcut universe=HILIQ window=x2 final={final_path} "
        f"peak_kb={pk} meta={meta_path} lambda={LAMBDA_FROZEN} approx=false",
        flush=True,
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Leaf30 CRR + CFOOE vol_pen alpha build r3_peakcut (HILIQ×x2); "
            "NOT authorized without --allow-real-data + --arch-ok-path"
        )
    )
    ap.add_argument(
        "--universe",
        default="HILIQ",
        choices=("HILIQ", "HI_LIQ"),  # FULLA intentionally absent
        help="PRIMARY HILIQ (alias HI_LIQ)",
    )
    ap.add_argument(
        "--window",
        default="x2",
        choices=("x2",),
        help="PRIMARY x2 only this ticket",
    )
    ap.add_argument("--x2-end", default=X2_END_TRADE_DATE)
    ap.add_argument("--out", type=Path, default=None, help="Required for real build")
    ap.add_argument("--rss-limit-mb", type=int, default=RSS_LIMIT_MB)
    ap.add_argument("--c4-kb", type=int, default=C4_KB)
    ap.add_argument("--stop-kb", type=int, default=STOP_KB)
    ap.add_argument("--hard-kb", type=int, default=HARD_KB)
    ap.add_argument("--allow-real-data", action="store_true", default=False)
    ap.add_argument("--arch-ok-path", type=Path, default=None)
    ap.add_argument(
        "--execute",
        action="store_true",
        default=False,
        help="Optional; still requires --allow-real-data + --arch-ok-path",
    )
    ap.add_argument("--hi-liq-mask", type=Path, default=HI_LIQ_MASK_DEFAULT)
    ap.add_argument("--sw-l1", type=Path, default=SW_L1_DEFAULT)
    ap.add_argument("--float-mktcap", type=Path, default=FLOAT_MKTCAP_DEFAULT)
    ap.add_argument("--leaf19-alpha", type=Path, default=LEAF19_ALPHA_DEFAULT)
    ap.add_argument("--leaf25-alpha", type=Path, default=LEAF25_ALPHA_DEFAULT)
    ap.add_argument("--sample-dir", type=Path, default=None)
    ap.add_argument(
        "--overlap-report",
        action="store_true",
        default=False,
        help="Force write overlap_vs_leaf19_25.json (also default on real path)",
    )
    ap.add_argument(
        "--no-overlap-report",
        action="store_true",
        default=False,
        help="Skip C3 overlap JSON on real path (X2 sign will BAN this flag; keep CLI for dry/dev only)",
    )
    ap.add_argument(
        "--dry-compile-only",
        action="store_true",
        help="Print pins; ZERO big-table load; exit",
    )
    ap.add_argument(
        "--chunk-mode",
        default="month",
        choices=("month",),
        help="R2 peak path: month chunks only (ban whole-window densify)",
    )
    args = ap.parse_args(argv)

    if args.dry_compile_only:
        return dry_compile_only_print(args)

    # No silent build
    if not args.allow_real_data and not args.execute:
        print(
            "STOP: missing authorization flags "
            "(need --allow-real-data + --arch-ok-path; or --dry-compile-only)",
            file=sys.stderr,
        )
        return 2
    if args.execute and not args.allow_real_data:
        print(
            "STOP: --execute requires --allow-real-data + --arch-ok-path",
            file=sys.stderr,
        )
        return 2
    if args.out is None:
        print(
            "STOP: --out is required for build (or pass --dry-compile-only)",
            file=sys.stderr,
        )
        return 2

    return run_build(args)


if __name__ == "__main__":
    raise SystemExit(main())
