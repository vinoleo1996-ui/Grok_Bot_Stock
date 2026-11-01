#!/usr/bin/env python3
"""Leaf32 margin net-flow resid slow alpha build — HILIQ×x2 (NOT authorized).

NEW file (2026-10-27). Nails PREREG_FROZEN sha8 6b8de5e9;
Arch FROZEN review 7c0d864f PASS_WITH_CONDITIONS (C2 formal script).
who_pays 84df02b5 / WHO_PAYS fad5911e / COVER ebda2603 (background only).

Mechanism (FROZEN; mechanism_tag=g1g5_ashare_margin_net_flow_resid_v1):
  net_rz = rzmre - rzche (CNY; may be negative = net repay)
  flow_raw = mean_W(net_rz / float_mktcap_T-1), W=20 trade days; min valid days >=15
  SW L1 demean -> OLS resid vs log float mktcap T-1 + mom20 + vol20 + logADV20
  alpha_raw = -rank(flow_resid); IC expected POSITIVE (comment pin; no return-IC here)
  Ban post-hoc sign / W / rebal flip; ban Amihud / on_minus_id / CRR / hk_hold as main
  Ban Delta-rzye margin_delta as main (margin_delta is overlap-only)

PRIMARY: --universe HILIQ --window x2  (FULLA only via --also-fulla-research; never PRIMARY)
X2: 2024-06-03 -> 2026-10-09; rebal every 20 trade days
Margin: data/v2/margin/margin_detail_daily_2018plus.parquet (PIT=available_at <= rebal)
Float: data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet
Bars (style only): data/v2/tushare_raw/daily/{YYYYMMDD}.parquet + adj_factor
C3: overlap_vs_leaf19_25_27_30_31_margin_delta.json;
     Jaccard>=0.7 hard reject (exit!=0); rho>0.5 strength filter
Real path: --allow-real-data + existing --arch-ok-path; ok sha8 not in forbid
--dry-compile-only: print pins; ZERO big-table load
rss soft 1500 MB hard ABORT + peak_proof; sampler /tmp/quantlab_leaf32_margin_flow_*
out intent: output/ai_factory/_leaf32_margin_flow/
forbid: 4bb141c9+fdbaa512+aa25e989+7e239487+5af20222+5ae077fa
C9: leaf30 KEEP 0087c928 NOT merged
live=false; promotion_approved=false; ok_requested=false
No Book-Smoke / selfcheck entry; !=X2 ACCEPT.
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
ROOT = Path(__file__).resolve().parents[1]
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

MECHANISM_TAG = "g1g5_ashare_margin_net_flow_resid_v1"
SCRIPT_REL = "research/leaf32_margin_net_flow_resid_alpha_build.py"
FROZEN_REL = (
    "docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_PREREG_FROZEN_20261027_ZH.md"
)
FROZEN_SHA8 = "6b8de5e9"
FROZEN_RECEIPT_SHA8 = "7623ce8c"
ARCH_FROZEN_REVIEW_SHA8 = "7c0d864f"
ARCH_WHO_PAYS_REVIEW_SHA8 = "84df02b5"
WHO_PAYS_SHA8 = "fad5911e"
COVER_SHA8 = "ebda2603"
# Leaf30 KEEP repair DRAFT — C9 separate queue; NOT merged into this script
LEAF30_KEEP_REPAIR_SHA8_SEPARATE = "0087c928"

RSS_LIMIT_MB = 1500
C4_KB = 1331200
STOP_KB = 1484800
HARD_KB = 1536000
SPLIT_THRESH_KB = int(0.85 * C4_KB)

X2_START = "2024-06-03"
X2_END = "2026-10-09"
X2_END_TRADE_DATE = "20261009"
REBAL_EVERY = 20
FLOW_W = 20
FLOW_MIN_VALID = 15
# IC sign pin (FROZEN): expected POSITIVE vs next-period idiosyncratic return.
# This script NEVER selects sign from returns — direction is documentation-only.
IC_SIGN_EXPECTED = "positive"
ALPHA_SIGN = "neg_rank_flow_resid"  # alpha = -rank(flow_resid); ban flip

# Style exposures: derived from daily bars (pinned; ban silent swap to capacity_adv)
STYLE_COLS_PINNED = ("mom20", "vol20", "logADV20")
STYLE_SOURCE_PINNED = "derived_from_daily_bars_W20"
# Cost pin (evaluation only; this script does not run PnL)
COST_BP_EVAL = 30
# decay KEEP pin (comment/meta only; this script does NOT run the gate)
DECAY_KEEP_PIN = {
    "latest_resid_alpha_gt_0": True,
    "not_five_quarter_decline": True,
    "H2_net_cagr_gt_510300": True,
    "near_window_td": 252,
    "note": "KEEP = conjunction of three gates; script does not execute decay gate",
}

FORBID_OK_SHA8 = (
    "4bb141c9",  # leaf31 X2 selfcheck .ok CONSUMED — ban RESTORED
    "fdbaa512",  # leaf31 X2 build .ok CONSUMED — ban RESTORED
    "aa25e989",  # leaf30 X2 selfcheck .ok CONSUMED — ban RESTORED
    "7e239487",  # leaf30 R3 build .ok CONSUMED — ban RESTORED
    "5af20222",  # leaf30 R2 VOID.ABORT_PEAK_HWM — ban RESTORED
    "5ae077fa",  # leaf30 R1 VOID.ABORT_PEAK_HWM — ban RESTORED
)

MARGIN_DEFAULT = ROOT / "data/v2/margin/margin_detail_daily_2018plus.parquet"
DAILY_DIR_DEFAULT = ROOT / "data/v2/tushare_raw/daily"
ADJ_FACTOR_DEFAULT = ROOT / "data/v2/adj/adj_factor_2023h2plus.parquet"
HI_LIQ_MASK_DEFAULT = ROOT / "output/strategy_hiliq/universe_mask_hiliq_v1.parquet"
FULLA_MASK_DEFAULT = ROOT / "output/strategy_fulla/universe_mask_fulla_v1.parquet"
SW_L1_DEFAULT = ROOT / "data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet"
FLOAT_MKTCAP_DEFAULT = (
    ROOT / "data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet"
)
CAL_DEFAULT = ROOT / "data/v2/calendar/trade_cal_sse_pit.parquet"
OUT_DEFAULT = ROOT / "output/ai_factory/_leaf32_margin_flow"

LEAF19_ALPHA_DEFAULT = (
    ROOT / "output/ai_factory/leaf19_cfacc_rnoa/alpha_HILIQ_20261014_213132.parquet"
)
LEAF25_ALPHA_DEFAULT = ROOT / (
    "output/ai_factory/_leaf25_full_factor/20261026_015610/"
    "alpha_HILIQ_x2_20261026_125138.parquet"
)
LEAF27_ALPHA_DEFAULT = ROOT / (
    "output/ai_factory/leaf27_on_minus_id_idio_ivol/"
    "alpha_HILIQ_x2_20261025_224033.parquet"
)
LEAF30_ALPHA_DEFAULT = ROOT / (
    "output/ai_factory/_leaf30_crr/20261027_003132/"
    "alpha_HILIQ_x2_20261027_010815.parquet"
)
LEAF31_ALPHA_DEFAULT = ROOT / (
    "output/ai_factory/_leaf31_amihud/20261027_024204/"
    "alpha_HILIQ_x2_20261027_024422.parquet"
)
MARGIN_DELTA_DEFAULT = ROOT / (
    "output/ai_factory/g1g5_margin_delta_daily_weights_20261013_020825.parquet"
)

SAMPLER_PREFIX = "/tmp/quantlab_leaf32_margin_flow_"

KNOWN_MARGIN_COLS = ["trade_date", "ts_code", "rzmre", "rzche", "available_at"]
KNOWN_DAILY_COLS = ["ts_code", "trade_date", "close", "pre_close", "amount", "vol"]
KNOWN_ADJ_COLS = ["ts_code", "trade_date", "adj_factor"]
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
KNOWN_MARGIN_DELTA_COLS = ["date", "instrument", "weight", "target_weight"]
JACCARD_HARD = 0.7
RHO_STRENGTH = 0.5
COVERAGE_MEDIAN_HILIQ = 300
COVERAGE_MEDIAN_FULLA = 800


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
    also_fulla = bool(getattr(args, "also_fulla_research", False))
    payload = {
        "live": False,
        "ok_requested": False,
        "promotion_approved": False,
        "executed": False,
        "x2_accept": False,
        "approx": False,
        "rss_limit_mb": RSS_LIMIT_MB,
        "c4_kb": C4_KB,
        "stop_kb": STOP_KB,
        "hard_kb": HARD_KB,
        "universe_cli": uni,
        "primary_universe": "HILIQ",
        "also_fulla_research": also_fulla,
        "ban_silent_fulla_as_primary": True,
        "window": args.window,
        "x2_end": args.x2_end,
        "x2_window": f"{X2_START} → {X2_END}",
        "rebal_every_td": REBAL_EVERY,
        "flow_W": FLOW_W,
        "flow_min_valid": FLOW_MIN_VALID,
        "alpha_sign": ALPHA_SIGN,
        "ic_sign_expected": IC_SIGN_EXPECTED,
        "mechanism_tag": MECHANISM_TAG,
        "script": SCRIPT_REL,
        "script_sha256": scr,
        "script_sha8": scr[:8] if isinstance(scr, str) and len(scr) >= 8 else None,
        "frozen_rel": FROZEN_REL,
        "frozen_sha8": FROZEN_SHA8,
        "frozen_receipt_sha8": FROZEN_RECEIPT_SHA8,
        "arch_frozen_review_sha8": ARCH_FROZEN_REVIEW_SHA8,
        "arch_who_pays_review_sha8": ARCH_WHO_PAYS_REVIEW_SHA8,
        "who_pays_sha8": WHO_PAYS_SHA8,
        "cover_sha8": COVER_SHA8,
        "leaf30_keep_repair_sha8_separate": LEAF30_KEEP_REPAIR_SHA8_SEPARATE,
        "forbid_ok_sha8": list(FORBID_OK_SHA8),
        "sampler_prefix": SAMPLER_PREFIX,
        "out_intent": str(OUT_DEFAULT.relative_to(ROOT)),
        "margin_detail": str(MARGIN_DEFAULT.relative_to(ROOT)),
        "float_mktcap": str(FLOAT_MKTCAP_DEFAULT.relative_to(ROOT)),
        "bars_daily_dir": str(DAILY_DIR_DEFAULT.relative_to(ROOT)),
        "adj_factor": str(ADJ_FACTOR_DEFAULT.relative_to(ROOT)),
        "style_cols_pinned": list(STYLE_COLS_PINNED),
        "style_source_pinned": STYLE_SOURCE_PINNED,
        "cost_bp_eval": COST_BP_EVAL,
        "decay_keep_pin": DECAY_KEEP_PIN,
        "residual_pipeline": [
            "net_rz=rzmre-rzche",
            "flow_raw=mean_W(net_rz/float_mktcap_T-1)",
            "SW_L1_demean",
            "OLS_vs_log_float_mktcap_T-1",
            "OLS_vs_mom20_vol20_logADV20",
            "neg_rank",
        ],
        "overlap_targets": [
            "leaf19",
            "leaf25",
            "leaf27",
            "leaf30",
            "leaf31",
            "margin_delta",
        ],
        "jaccard_hard": JACCARD_HARD,
        "rho_strength_filter": RHO_STRENGTH,
        "coverage_median_hiliq": COVERAGE_MEDIAN_HILIQ,
        "coverage_median_fulla_research": COVERAGE_MEDIAN_FULLA,
        "leaf19_alpha": str(LEAF19_ALPHA_DEFAULT.relative_to(ROOT)),
        "leaf25_alpha": str(LEAF25_ALPHA_DEFAULT.relative_to(ROOT)),
        "leaf27_alpha": str(LEAF27_ALPHA_DEFAULT.relative_to(ROOT)),
        "leaf30_alpha": str(LEAF30_ALPHA_DEFAULT.relative_to(ROOT)),
        "leaf31_alpha": str(LEAF31_ALPHA_DEFAULT.relative_to(ROOT)),
        "margin_delta_weights": str(MARGIN_DELTA_DEFAULT.relative_to(ROOT)),
        "primary_cli": (
            f"PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python {SCRIPT_REL} "
            f"--universe HILIQ --window x2 --x2-end {X2_END_TRADE_DATE} "
            f"--allow-real-data --arch-ok-path <OK> --out <OUT>"
        ),
        "dry_cli": (
            f"PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python {SCRIPT_REL} "
            f"--dry-compile-only"
        ),
        "ban_book_smoke": True,
        "ban_selfcheck": True,
        "ban_amihud_main": True,
        "ban_on_minus_id_main": True,
        "ban_crr_accounting_main": True,
        "ban_hk_hold_northbound_main": True,
        "ban_margin_delta_as_main": True,
        "ban_seller_report_jin_gu": True,
        "primary_load": "rebal_day_lazy_margin_float_bars",
        "schema": "leaf32_margin_net_flow_resid_alpha_build_v1",
        "known_schema_static": {
            "margin_cols": KNOWN_MARGIN_COLS,
            "daily_cols": KNOWN_DAILY_COLS,
            "adj_cols": KNOWN_ADJ_COLS,
            "mask_cols": KNOWN_MASK_COLS,
            "alpha_out_cols": KNOWN_ALPHA_OUT_COLS,
            "sw_cols": KNOWN_SW_COLS,
            "float_cols": KNOWN_FLOAT_COLS,
            "margin_delta_cols": KNOWN_MARGIN_DELTA_COLS,
        },
        "sign_notes": {
            "ban_no_overlap_report": True,
            "peak_proof_required": [
                "after_mask",
                "after_sw",
                "after_margin_rebal_*",
                "after_float_rebal_*",
                "after_bars_rebal_*",
                "after_logmv_rebal_*",
                "after_daily_concat",
            ],
            "rss_limit_mb": 1500,
            "jaccard_ge_0_7_hard_reject": True,
            "rho_gt_0_5_strength_filter_only": True,
            "ban_restored_ok": list(FORBID_OK_SHA8),
            "ban_raise_rss": True,
            "ban_posthoc_sign_flip": True,
            "c9_leaf30_keep_not_merged": True,
            "arch_ok_path_required_for_real": True,
            "process_gate_note": (
                "Real build requires existing --arch-ok-path (file must exist; "
                "sha8 not in forbid). Process gate = that .ok + Main window; "
                "ban inventing / self-opening a fake .ok."
            ),
        },
        "arch_conditions": {
            "C2": "formal_script_this_ticket",
            "C3": "overlap_vs_leaf19_25_27_30_31_margin_delta",
            "C4": "residual_SW_logmv_mom20_vol20_logADV20",
            "C5": "HILIQ_primary_FULLA_research_optional",
            "C6": "decay_KEEP_pin_only_not_run",
            "C7": "forbid_six_sha8",
            "C8": "rss_1500_peak_proof",
            "C9": "0087c928_separate",
        },
        "note": (
            "dry-compile-only; ZERO big-table load; "
            "NOT authorized to execute; wait Arch script review -> new X2 .ok "
            f"(ban RESTORED {'+'.join(FORBID_OK_SHA8)}); "
            "peak_proof REQUIRED; rss=1500 ban raise; "
            "PRIMARY=HILIQ; FULLA only --also-fulla-research; "
            "alpha=-rank(flow_resid); W/rebal=20/20; "
            f"FROZEN={FROZEN_SHA8}; ArchFROZEN={ARCH_FROZEN_REVIEW_SHA8}"
        ),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    if uni == "FULLA":
        print(
            "STOP: --universe FULLA forbidden as PRIMARY; "
            "use --universe HILIQ and optional --also-fulla-research",
            file=sys.stderr,
        )
        return 2
    if getattr(args, "window", "x2") != "x2":
        print(
            f"STOP: --window must be x2 this ticket (got {args.window})",
            file=sys.stderr,
        )
        return 2
    return 0


def ols_resid(y, X):
    import numpy as np

    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    return y - X @ b


def pct_rank(s):
    import numpy as np
    import pandas as pd

    s = pd.Series(s, dtype="float64")
    out = s.rank(method="average", pct=True)
    out = out.where(s.notna(), np.nan)
    return out.to_numpy()


def _load_mask_members(mask_path: Path, start: str, end: str, *, label: str):
    import pandas as pd
    import pyarrow.parquet as pq

    if not mask_path.is_file():
        raise SystemExit(
            f"STOP: {label} mask missing at {mask_path}; refuse silent empty-universe"
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
            f"STOP: {label} mask empty for [{start}, {end}] at {mask_path}"
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
        "label": label,
    }


def _load_sw_table(sw_path: Path):
    import pandas as pd
    import pyarrow.parquet as pq

    if not sw_path.is_file():
        raise SystemExit(f"STOP: SW L1 missing {sw_path}; PIN_GAP refuse silent skip")
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
    import pandas as pd

    asof = pd.Timestamp(asof)
    sub = sw[sw["ts_code"].isin(codes)].copy()
    ok = (sub["in_date"].isna() | (sub["in_date"] <= asof)) & (
        sub["out_date"].isna() | (sub["out_date"] > asof)
    )
    avail_ok = sub["available_at"].isna() | (sub["available_at"] <= asof)
    sub = sub.loc[ok & avail_ok].sort_values(["ts_code", "in_date"])
    sub = sub.drop_duplicates("ts_code", keep="last")
    return dict(zip(sub["ts_code"], sub["sw_code"].astype(str)))


def _load_logmv_t1(float_path: Path, dates: list, codes: list[str]):
    """log float mktcap T−1: keys (asof_date, ts_code). Missing → absent (PIN later)."""
    import numpy as np
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq

    if not float_path.is_file():
        raise SystemExit(
            f"STOP: float_mktcap missing {float_path}; PIN_GAP refuse silent skip"
        )
    dmin = (min(dates) - pd.Timedelta(days=10)).strftime("%Y%m%d")
    dmax = max(dates).strftime("%Y%m%d")
    id_map = {}
    for c in codes:
        if "." in c:
            code, mkt = c.split(".", 1)
            id_map[f"{mkt.lower()}.{code}"] = c
    ids = list(id_map.keys())
    schema = pq.read_schema(float_path)
    td_type = schema.field("trade_date").type
    if pa.types.is_string(td_type) or pa.types.is_large_string(td_type):
        lo, hi = dmin, dmax
    else:
        lo = pd.Timestamp(min(dates) - pd.Timedelta(days=10))
        hi = pd.Timestamp(max(dates))
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
    df["trade_date"] = pd.to_datetime(
        df["trade_date"].astype(str).str.replace("-", "").str[:8],
        format="%Y%m%d",
        errors="coerce",
    )
    df = df.dropna(subset=["trade_date", "float_mktcap"])
    df["logmv"] = np.log(df["float_mktcap"].astype(float).clip(lower=1.0))
    df = df.sort_values(["ts_code", "trade_date"])
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



def _load_float_panel_window(
    float_path: Path,
    day_list: list,
    codes: list[str],
    *,
    prev_day_extra: object | None = None,
):
    """Lazy float panel for window days (+ optional prev day for T-1).

    Returns DataFrame columns: ts_code, trade_date, float_mktcap.
    Ban whole-X2 preload (peak lesson; rebal-day lazy only).
    """
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq

    if not float_path.is_file():
        raise SystemExit(
            f"STOP: float_mktcap missing {float_path}; PIN_GAP refuse silent skip"
        )
    days = list(day_list)
    if prev_day_extra is not None:
        days = [pd.Timestamp(prev_day_extra).normalize()] + [
            pd.Timestamp(d).normalize() for d in days
        ]
    else:
        days = [pd.Timestamp(d).normalize() for d in days]
    if not days:
        return None
    dmin = min(days) - pd.Timedelta(days=2)
    dmax = max(days)
    id_map = {}
    for c in codes:
        if "." in c:
            code, mkt = c.split(".", 1)
            id_map[f"{mkt.lower()}.{code}"] = c
    ids = list(id_map.keys())
    schema = pq.read_schema(float_path)
    td_type = schema.field("trade_date").type
    if pa.types.is_string(td_type) or pa.types.is_large_string(td_type):
        lo, hi = dmin.strftime("%Y%m%d"), dmax.strftime("%Y%m%d")
    else:
        lo, hi = dmin, dmax
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
        return None
    df = pd.concat(frames, ignore_index=True)
    df["ts_code"] = df["instrument_id"].map(to_ts)
    df["trade_date"] = pd.to_datetime(
        df["trade_date"].astype(str).str.replace("-", "").str[:8],
        format="%Y%m%d",
        errors="coerce",
    ).dt.normalize()
    df = df.dropna(subset=["trade_date", "float_mktcap"])
    df = df[(df["trade_date"] >= dmin.normalize()) & (df["trade_date"] <= dmax)]
    if df.empty:
        return None
    return df[["ts_code", "trade_date", "float_mktcap"]].copy()


def _load_margin_window(
    margin_path: Path,
    day_list: list,
    codes: set[str],
    *,
    asof_rebal,
):
    """Lazy load margin detail for win days with PIT available_at <= asof_rebal.

    Ban whole-window preloaded flow matrix (peak lesson).
    """
    import pandas as pd
    import pyarrow.parquet as pq

    if not margin_path.is_file():
        raise SystemExit(
            f"STOP: margin detail missing {margin_path}; PIN_GAP refuse silent skip"
        )
    asof = pd.Timestamp(asof_rebal).normalize()
    dmin = min(pd.Timestamp(d).normalize() for d in day_list)
    dmax = max(pd.Timestamp(d).normalize() for d in day_list)
    lo = dmin.strftime("%Y%m%d")
    hi = dmax.strftime("%Y%m%d")
    codes_l = sorted(codes)
    frames = []
    step = 800
    for i in range(0, len(codes_l), step):
        chunk = codes_l[i : i + step]
        t = pq.read_table(
            margin_path,
            columns=["trade_date", "ts_code", "rzmre", "rzche", "available_at"],
            filters=[
                ("ts_code", "in", chunk),
                ("trade_date", ">=", lo),
                ("trade_date", "<=", hi),
            ],
        )
        frames.append(t.to_pandas())
    if not frames:
        return None
    df = pd.concat(frames, ignore_index=True)
    df["ts_code"] = df["ts_code"].astype(str)
    df["trade_date"] = pd.to_datetime(
        df["trade_date"].astype(str).str.replace("-", "").str[:8],
        format="%Y%m%d",
        errors="coerce",
    ).dt.normalize()
    df["available_at"] = pd.to_datetime(df["available_at"], errors="coerce")
    pit_ok = df["available_at"].isna() | (df["available_at"].dt.normalize() <= asof)
    df = df.loc[pit_ok].copy()
    want_days = set(pd.Timestamp(d).normalize() for d in day_list)
    df = df[df["trade_date"].isin(want_days)]
    if df.empty:
        return None
    return df



def _load_trade_cal(cal_path: Path, start: str, end: str) -> list:
    import pandas as pd
    import pyarrow.parquet as pq

    if not cal_path.is_file():
        raise SystemExit(f"STOP: trade calendar missing {cal_path}")
    # Prefer HI_LIQ mask days when available; calendar is warm-up helper
    t = pq.read_table(cal_path, columns=["cal_date", "is_open"])
    df = t.to_pandas()
    df = df[df["is_open"] == 1].copy()
    df["d"] = pd.to_datetime(df["cal_date"].astype(str), format="%Y%m%d", errors="coerce")
    df = df.dropna(subset=["d"])
    lo = pd.Timestamp(start) - pd.Timedelta(days=80)  # warm-up for W=20
    hi = pd.Timestamp(end)
    days = sorted(df.loc[(df["d"] >= lo) & (df["d"] <= hi), "d"].tolist())
    return [pd.Timestamp(d).normalize() for d in days]


def _load_daily_window(
    daily_dir: Path,
    day_list: list,
    codes: set[str],
) -> "object":
    """Load close/amount for given trade days; filter to codes. Lazy per-call."""
    import pandas as pd

    frames = []
    missing = []
    for d in day_list:
        ds = pd.Timestamp(d).strftime("%Y%m%d")
        p = daily_dir / f"{ds}.parquet"
        if not p.is_file():
            missing.append(ds)
            continue
        df = pd.read_parquet(
            p, columns=["ts_code", "trade_date", "close", "pre_close", "amount"]
        )
        df["ts_code"] = df["ts_code"].astype(str)
        df = df[df["ts_code"].isin(codes)]
        if df.empty:
            continue
        df["trade_date"] = pd.to_datetime(
            df["trade_date"].astype(str).str.replace("-", "").str[:8],
            format="%Y%m%d",
            errors="coerce",
        )
        frames.append(df)
    if missing and len(missing) == len(day_list):
        raise SystemExit(
            f"STOP: PIN_GAP all daily bars missing under {daily_dir} "
            f"for window n={len(day_list)} first_missing={missing[0]}"
        )
    if not frames:
        return None
    out = pd.concat(frames, ignore_index=True)
    return out


def _load_adj_factors(adj_path: Path, day_list: list, codes: set[str]):
    import pandas as pd
    import pyarrow.parquet as pq

    if not adj_path.is_file():
        raise SystemExit(
            f"STOP: adj_factor cache missing {adj_path}; "
            f"PIN_GAP (research/adj_price cache); refuse silent raw pct"
        )
    dmin = min(day_list).strftime("%Y%m%d")
    dmax = max(day_list).strftime("%Y%m%d")
    # chunk codes
    codes_l = sorted(codes)
    frames = []
    step = 800
    for i in range(0, len(codes_l), step):
        chunk = codes_l[i : i + step]
        t = pq.read_table(
            adj_path,
            columns=["ts_code", "trade_date", "adj_factor"],
            filters=[
                ("ts_code", "in", chunk),
                ("trade_date", ">=", dmin),
                ("trade_date", "<=", dmax),
            ],
        )
        frames.append(t.to_pandas())
    if not frames:
        return {}
    df = pd.concat(frames, ignore_index=True)
    df["ts_code"] = df["ts_code"].astype(str)
    df["trade_date"] = pd.to_datetime(
        df["trade_date"].astype(str).str.replace("-", "").str[:8],
        format="%Y%m%d",
        errors="coerce",
    )
    df = df.dropna(subset=["trade_date", "adj_factor"])
    return {
        (pd.Timestamp(r.trade_date).normalize(), str(r.ts_code)): float(r.adj_factor)
        for r in df.itertuples(index=False)
    }



def _compute_flow_and_styles(
    margin_df,
    float_df,
    bars_panel,
    win_days: list,
    codes: list[str],
):
    """Per code on last day of win_days: flow_raw + mom20/vol20/logADV20.

    flow_raw = mean_W(net_rz / float_mktcap_T-1); invalid days skipped (NOT filled 0).
    Styles from bars (STYLE_SOURCE_PINNED); ban silent capacity_adv swap.
    """
    import numpy as np
    import pandas as pd

    if margin_df is None or margin_df.empty or float_df is None or float_df.empty:
        return {}

    win_set = set(pd.Timestamp(d).normalize() for d in win_days)
    m = margin_df.copy()
    m["trade_date"] = pd.to_datetime(m["trade_date"]).dt.normalize()
    m = m[m["trade_date"].isin(win_set)]
    m["rzmre"] = pd.to_numeric(m["rzmre"], errors="coerce")
    m["rzche"] = pd.to_numeric(m["rzche"], errors="coerce")
    m["net_rz"] = m["rzmre"] - m["rzche"]
    m.loc[m["rzmre"].isna() | m["rzche"].isna(), "net_rz"] = np.nan

    f = float_df.copy()
    f["trade_date"] = pd.to_datetime(f["trade_date"]).dt.normalize()
    f = f.sort_values(["ts_code", "trade_date"])
    float_by = {k: g for k, g in f.groupby("ts_code", sort=False)}

    def float_t1(code: str, day) -> float | None:
        g = float_by.get(code)
        if g is None:
            return None
        prev = g[g["trade_date"] < pd.Timestamp(day)]
        if prev.empty:
            return None
        v = float(prev["float_mktcap"].iloc[-1])
        if not np.isfinite(v) or v <= 0:
            return None
        return v

    m_by = {k: g.sort_values("trade_date") for k, g in m.groupby("ts_code", sort=False)}

    style_by = {}
    if bars_panel is not None and not bars_panel.empty:
        byb = {
            k: g.sort_values("trade_date")
            for k, g in bars_panel.groupby("ts_code", sort=False)
        }
        for c in codes:
            g = byb.get(c)
            if g is None or g.empty:
                continue
            g = g[g["trade_date"].isin(win_days)]
            if g.empty:
                continue
            r = g["r_adj"].to_numpy(float)
            amt = g["amount_cny"].to_numpy(float)
            valid = np.isfinite(r) & np.isfinite(amt) & (amt > 0)
            n_valid = int(valid.sum())
            if n_valid < FLOW_MIN_VALID:
                continue
            rv = r[valid]
            av = amt[valid]
            mom20 = float(np.nansum(rv))
            vol20 = float(np.nanstd(rv, ddof=1)) if n_valid >= 2 else float("nan")
            logadv20 = float(np.log(max(float(np.nanmean(av)), 1.0)))
            if not np.isfinite(vol20):
                continue
            style_by[c] = {
                "mom20": mom20,
                "vol20": vol20,
                "logADV20": logadv20,
                "n_style_valid": n_valid,
            }

    out = {}
    for c in codes:
        g = m_by.get(c)
        if g is None or g.empty:
            continue
        ratios = []
        for d in win_days:
            d = pd.Timestamp(d).normalize()
            row = g[g["trade_date"] == d]
            if row.empty:
                continue
            nr = row["net_rz"].iloc[-1]
            if not np.isfinite(nr):
                continue
            ft1 = float_t1(c, d)
            if ft1 is None:
                continue
            ratios.append(float(nr) / float(ft1))
        n_valid = len(ratios)
        if n_valid < FLOW_MIN_VALID:
            continue
        st = style_by.get(c)
        if st is None:
            continue
        out[c] = {
            "flow_raw": float(np.mean(ratios)),
            "mom20": st["mom20"],
            "vol20": st["vol20"],
            "logADV20": st["logADV20"],
            "n_valid": n_valid,
        }
    return out



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
    paths: dict[str, Path],
    sample_n: int = 6,
) -> dict:
    """C3: Jaccard top20 + Spearman rho vs leaf19/25/27/30/31 + margin_delta.

    Jaccard>=0.7 -> hard_reject flag; caller must exit non-zero if any hard reject.
    rho>0.5 -> strength_filter disclosure only.
    margin_delta uses weight (not alpha); disclosed in meta.
    Missing required path -> PIN_GAP (do not silently skip hard reject).
    """
    import numpy as np
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq

    alpha_df = alpha_df.copy()
    alpha_df["trade_date"] = pd.to_datetime(alpha_df["trade_date"])
    days = sorted(alpha_df["trade_date"].unique())
    if not days:
        payload = {"error": "empty_alpha", "schema": "leaf32_overlap_vs_leaf19_25_27_30_31_margin_delta"}
        out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
        return payload
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

    pin_gaps_ov = []

    def _load_other(path: Path, date_col: str, inst_col: str, score_col: str):
        if not path.is_file():
            return None
        schema = pq.read_schema(path)
        names = set(schema.names)
        if date_col not in names or inst_col not in names or score_col not in names:
            return None
        field = schema.field(date_col)
        is_str = pa.types.is_string(field.type) or pa.types.is_large_string(field.type)
        cols = [date_col, inst_col, score_col]
        if is_str:
            dmin = min(sample).strftime("%Y-%m-%d")
            dmax = max(sample).strftime("%Y-%m-%d")
            t = pq.read_table(
                path,
                columns=cols,
                filters=[(date_col, ">=", dmin), (date_col, "<=", dmax)],
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
        df.rename(
            columns={date_col: "date", inst_col: "instrument", score_col: "score"},
            inplace=True,
        )
        df["instrument"] = df["instrument"].astype(str)
        return df

    others = {}
    score_meta = {}
    for tag, path in paths.items():
        if tag == "margin_delta":
            o = _load_other(path, "date", "instrument", "weight")
            if o is None:
                o = _load_other(path, "date", "instrument", "target_weight")
                score_meta[tag] = "target_weight" if o is not None else None
            else:
                score_meta[tag] = "weight"
            if o is None and not path.is_file():
                pin_gaps_ov.append(
                    {
                        "tag": tag,
                        "gap": "PIN_GAP_missing_file",
                        "path": str(
                            path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
                        ),
                    }
                )
            elif o is None:
                pin_gaps_ov.append(
                    {
                        "tag": tag,
                        "gap": "PIN_GAP_missing_score_col",
                        "path": str(
                            path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
                        ),
                    }
                )
            others[tag] = o
            continue
        o = _load_other(path, "trade_date", "ts_code", "alpha")
        if o is None:
            o = _load_other(path, "date", "instrument", "alpha")
        score_meta[tag] = "alpha" if o is not None else None
        if o is None and not path.is_file():
            pin_gaps_ov.append(
                {
                    "tag": tag,
                    "gap": "PIN_GAP_missing_file",
                    "path": str(
                        path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
                    ),
                }
            )
        others[tag] = o

    rows = []
    any_hard = False
    for d in sample:
        a = alpha_df[alpha_df["trade_date"] == pd.Timestamp(d)]
        if a.empty:
            continue
        codes = a["ts_code"].astype(str).tolist()
        scores = a["alpha"].to_numpy(float)
        ent = {"date": str(pd.Timestamp(d).date()), "n_alpha": len(codes)}
        for tag, other in others.items():
            if other is None:
                ent[f"rho_{tag}"] = None
                ent[f"j20_{tag}"] = None
                ent[f"missing_{tag}"] = True
                continue
            o = other[other["date"] == pd.Timestamp(d)]
            if o.empty:
                ent[f"rho_{tag}"] = None
                ent[f"j20_{tag}"] = None
                continue
            # normalize instrument ids
            o = o.copy()
            o["instrument"] = o["instrument"].map(
                lambda x: to_ts(x) if str(x).startswith(("sh.", "sz.", "bj.")) else str(x)
            )
            codes_n = [to_ts(c) if c.startswith(("sh.", "sz.", "bj.")) else c for c in codes]
            m = pd.DataFrame({"instrument": codes_n, "a": scores}).merge(
                o.rename(columns={"score": "b"})[["instrument", "b"]],
                on="instrument",
                how="inner",
            )
            ent[f"rho_{tag}"] = spearman_rho(m["a"].to_numpy(), m["b"].to_numpy())
            ent[f"j20_{tag}"] = top_jaccard(
                codes_n,
                scores,
                o["instrument"].tolist(),
                o["score"].to_numpy(float),
                20,
            )
            jhard = bool(
                ent[f"j20_{tag}"] is not None and ent[f"j20_{tag}"] >= JACCARD_HARD
            )
            ent[f"jaccard_hard_reject_{tag}"] = jhard
            if jhard:
                any_hard = True
            ent[f"strength_filter_{tag}"] = bool(
                ent[f"rho_{tag}"] is not None and ent[f"rho_{tag}"] > RHO_STRENGTH
            )
        rows.append(ent)

    required_missing = [g for g in pin_gaps_ov if g.get("tag") == "margin_delta"]
    payload = {
        "schema": "leaf32_overlap_vs_leaf19_25_27_30_31_margin_delta",
        "note": (
            "C3 formal overlap on full margin-flow alpha. "
            "Jaccard>=0.7 hard reject (exit non-zero); rho>0.5 strength filter only. "
            "vs margin_delta uses weight/target_weight (active-set / rank exposure); "
            "missing required file -> PIN_GAP (not silent skip). "
            "DRAFT intent cannot replace this file."
        ),
        "mechanism_tag": MECHANISM_TAG,
        "sample_dates": [str(pd.Timestamp(d).date()) for d in sample],
        "paths": {
            k: str(v.relative_to(ROOT) if v.is_relative_to(ROOT) else v)
            for k, v in paths.items()
        },
        "score_col_meta": score_meta,
        "rows": rows,
        "any_jaccard_hard_reject": any_hard,
        "jaccard_hard": JACCARD_HARD,
        "rho_strength": RHO_STRENGTH,
        "pin_gaps": pin_gaps_ov,
        "any_required_pin_gap": bool(required_missing),
        "live": False,
    }
    tmp = out_path.with_suffix(out_path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(out_path)
    return payload


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


def _residualize_cross_section(df):
    """SW L1 demean -> OLS vs logmv + mom20 + vol20 + logADV20 -> flow_resid.

    Missing any style/logmv/sw -> drop row (not silent zero). Small industry -> demean only.
    """
    import numpy as np
    import pandas as pd

    g = df.dropna(
        subset=["flow_raw", "sw_code", "logmv", "mom20", "vol20", "logADV20"]
    ).copy()
    if g.empty:
        g["flow_resid"] = np.nan
        return g
    vc = g["sw_code"].value_counts()
    g["flow_dm"] = g["flow_raw"] - g.groupby("sw_code")["flow_raw"].transform("mean")
    X = np.column_stack(
        [
            np.ones(len(g)),
            g["logmv"].to_numpy(float),
            g["mom20"].to_numpy(float),
            g["vol20"].to_numpy(float),
            g["logADV20"].to_numpy(float),
        ]
    )
    y = g["flow_dm"].to_numpy(float)
    g["flow_resid"] = ols_resid(y, X)
    g.attrs["n_sw_small"] = int((vc < 3).sum())
    return g


def build_alpha_for_window(args, *, universe_label: str = "HILIQ") -> tuple:
    """Build daily base-alpha with rebal-day lazy margin/float/bars load. Returns (alpha_df, meta)."""
    import numpy as np
    import pandas as pd

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

    mask_path = (
        Path(args.hi_liq_mask)
        if universe_label == "HILIQ"
        else Path(args.fulla_mask)
    )
    by_day, codes, mask_meta = _load_mask_members(
        mask_path, X2_START, X2_END, label=universe_label
    )
    _rss("after_mask")
    sw = _load_sw_table(Path(args.sw_l1))
    _rss("after_sw")

    cal_days = _load_trade_cal(Path(args.calendar), X2_START, X2_END)
    cal_index = {d: i for i, d in enumerate(cal_days)}

    all_days = sorted(by_day.keys())
    rebal_idx = list(range(0, len(all_days), REBAL_EVERY))
    if rebal_idx and rebal_idx[-1] != len(all_days) - 1:
        rebal_idx.append(len(all_days) - 1)
    rebal_days = [all_days[i] for i in rebal_idx]

    alpha_rebal_rows = []
    coverage = []
    pin_gaps = []

    for d in rebal_days:
        d = pd.Timestamp(d).normalize()
        members = set(by_day.get(d, []))
        if not members:
            coverage.append({"date": str(d.date()), "n": 0})
            continue
        if d not in cal_index:
            proxy = sorted(set(cal_days) | set(all_days))
            cal_index_local = {dd: i for i, dd in enumerate(proxy)}
            if d not in cal_index_local:
                pin_gaps.append({"date": str(d.date()), "gap": "rebal_not_in_cal"})
                coverage.append({"date": str(d.date()), "n": 0})
                continue
            i_d = cal_index_local[d]
            win_days = proxy[max(0, i_d - FLOW_W + 1) : i_d + 1]
        else:
            i_d = cal_index[d]
            win_days = cal_days[max(0, i_d - FLOW_W + 1) : i_d + 1]

        if len(win_days) < FLOW_MIN_VALID:
            pin_gaps.append({"date": str(d.date()), "gap": "short_window"})
            coverage.append({"date": str(d.date()), "n": 0})
            continue

        if win_days[0] in cal_index and cal_index[win_days[0]] > 0:
            prev0 = cal_days[cal_index[win_days[0]] - 1]
            load_days = [prev0] + list(win_days)
        else:
            prev0 = None
            load_days = list(win_days)

        margin_df = _load_margin_window(
            Path(args.margin_detail), win_days, members, asof_rebal=d
        )
        _rss(f"after_margin_rebal_{d.strftime('%Y%m%d')}")
        if margin_df is None or margin_df.empty:
            pin_gaps.append({"date": str(d.date()), "gap": "margin_empty"})
            coverage.append({"date": str(d.date()), "n": 0})
            del margin_df
            gc.collect()
            continue

        float_df = _load_float_panel_window(
            Path(args.float_mktcap),
            win_days,
            sorted(members),
            prev_day_extra=prev0,
        )
        _rss(f"after_float_rebal_{d.strftime('%Y%m%d')}")
        if float_df is None or float_df.empty:
            pin_gaps.append({"date": str(d.date()), "gap": "float_empty"})
            coverage.append({"date": str(d.date()), "n": 0})
            del margin_df, float_df
            gc.collect()
            continue

        bars = _load_daily_window(Path(args.daily_dir), load_days, members)
        _rss(f"after_bars_rebal_{d.strftime('%Y%m%d')}")
        bars_w = None
        if bars is not None and not bars.empty:
            adj_map = _load_adj_factors(Path(args.adj_factor), load_days, members)
            bars = bars.copy()
            bars["trade_date"] = pd.to_datetime(bars["trade_date"]).dt.normalize()
            bars["adj_factor"] = [
                adj_map.get((pd.Timestamp(td).normalize(), str(tc)))
                for td, tc in zip(bars["trade_date"], bars["ts_code"])
            ]
            bars["amount_cny"] = bars["amount"].astype(float) * 1000.0
            bars.loc[bars["amount_cny"] <= 0, "amount_cny"] = np.nan
            bars["hfq"] = bars["close"].astype(float) * bars["adj_factor"].astype(float)
            bars = bars.sort_values(["ts_code", "trade_date"])
            bars["hfq_prev"] = bars.groupby("ts_code")["hfq"].shift(1)
            bars["r_adj"] = bars["hfq"] / bars["hfq_prev"] - 1.0
            bars_w = bars[bars["trade_date"].isin(win_days)].copy()
            del bars, adj_map
            gc.collect()
        else:
            pin_gaps.append({"date": str(d.date()), "gap": "bars_empty_style"})
            coverage.append({"date": str(d.date()), "n": 0})
            del margin_df, float_df, bars
            gc.collect()
            continue

        feats = _compute_flow_and_styles(
            margin_df, float_df, bars_w, win_days, sorted(members)
        )
        del margin_df, float_df, bars_w
        gc.collect()

        if not feats:
            pin_gaps.append({"date": str(d.date()), "gap": "no_flow_feats"})
            coverage.append({"date": str(d.date()), "n": 0})
            continue

        logmv_d = _load_logmv_t1(Path(args.float_mktcap), [d], sorted(members))
        sw_map = _sw_asof_codes(sw, d, sorted(feats.keys()))
        rows = []
        for c, f in feats.items():
            if c not in sw_map:
                continue
            lm = logmv_d.get((d, c))
            if lm is None:
                continue
            rows.append(
                {
                    "ts_code": c,
                    "flow_raw": f["flow_raw"],
                    "mom20": f["mom20"],
                    "vol20": f["vol20"],
                    "logADV20": f["logADV20"],
                    "logmv": lm,
                    "sw_code": sw_map[c],
                    "n_valid": f["n_valid"],
                }
            )
        del logmv_d, feats
        gc.collect()
        _rss(f"after_logmv_rebal_{d.strftime('%Y%m%d')}")

        if not rows:
            pin_gaps.append({"date": str(d.date()), "gap": "no_resid_inputs"})
            coverage.append({"date": str(d.date()), "n": 0})
            continue
        cs = pd.DataFrame(rows)
        for col in STYLE_COLS_PINNED:
            if col not in cs.columns:
                raise SystemExit(
                    f"STOP: PIN_GAP missing style col {col} at {d.date()}; "
                    f"refuse silent skip (FROZEN section 3)"
                )
        cs = _residualize_cross_section(cs)
        cs = cs.dropna(subset=["flow_resid"])
        if cs.empty:
            coverage.append({"date": str(d.date()), "n": 0})
            continue
        # alpha = -rank(flow_resid)  — FROZEN; ban flip
        rnk = pct_rank(cs["flow_resid"].to_numpy(float))
        cs["alpha"] = -rnk
        coverage.append({"date": str(d.date()), "n": int(len(cs))})
        for _, r in cs.iterrows():
            alpha_rebal_rows.append(
                {
                    "rebal_date": d,
                    "ts_code": r["ts_code"],
                    "alpha": float(r["alpha"]),
                }
            )
        del cs, rows
        gc.collect()
        _rss(f"after_alpha_rebal_{d.strftime('%Y%m%d')}")

    if not alpha_rebal_rows:
        raise SystemExit(
            "STOP: zero alpha rows (check margin / float / daily bars / HI_LIQ / FLOW W)"
        )

    A = pd.DataFrame(alpha_rebal_rows)
    del alpha_rebal_rows
    gc.collect()
    A = A.sort_values(["rebal_date", "ts_code"])
    rebal_sorted = sorted(A["rebal_date"].unique())

    import pyarrow as pa
    import pyarrow.parquet as pq

    month_chunks = _month_chunks(X2_START, X2_END)
    ts_tag = datetime.now(ET).strftime("%Y%m%d_%H%M%S")
    tmp_root = Path(f"{SAMPLER_PREFIX}chunk_{ts_tag}")
    assert_tmp_quantlab(tmp_root, "leaf32-month-chunk-tmp")
    tmp_root.mkdir(parents=True, exist_ok=True)
    part_paths: list[Path] = []

    for ch in month_chunks:
        c0 = pd.Timestamp(ch["start"])
        c1 = pd.Timestamp(ch["end"])
        days_in = [dd for dd in all_days if c0 <= pd.Timestamp(dd) <= c1]
        if not days_in:
            continue
        month_rows = []
        for dd in days_in:
            prev = [r for r in rebal_sorted if r <= dd]
            if not prev:
                continue
            rd = prev[-1]
            members = set(by_day.get(pd.Timestamp(dd), []))
            g = A[A["rebal_date"] == rd]
            g = g[g["ts_code"].isin(members)]
            if g.empty:
                continue
            td = pd.Timestamp(dd).strftime("%Y-%m-%d")
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
            pth = tmp_root / f"chunk_{int(ch['chunk_id']):03d}.parquet"
            table = pa.Table.from_pandas(cdf, preserve_index=False)
            tmpf = pth.with_suffix(pth.suffix + ".tmp")
            pq.write_table(table, tmpf, compression="zstd")
            tmpf.replace(pth)
            part_paths.append(pth)
            del cdf, table, month_rows
        else:
            del month_rows
        gc.collect()
        _rss(f"month_chunk_{int(ch['chunk_id']):03d}_{ch['start'][:7]}")

    if not part_paths:
        raise SystemExit("STOP: zero daily alpha rows after month-chunk expand")

    frames = [pd.read_parquet(pth) for pth in part_paths]
    alpha_df = pd.concat(frames, ignore_index=True)
    del frames
    gc.collect()
    _rss("after_daily_concat")

    if args.sample_dir is None:
        for pth in part_paths:
            try:
                pth.unlink(missing_ok=True)
            except OSError:
                pass
        try:
            tmp_root.rmdir()
        except OSError:
            pass

    med_cov = float(np.median([c["n"] for c in coverage])) if coverage else 0.0
    gate = (
        COVERAGE_MEDIAN_HILIQ if universe_label == "HILIQ" else COVERAGE_MEDIAN_FULLA
    )
    meta = {
        "schema": "leaf32_margin_net_flow_resid_alpha_build_v1",
        "live": False,
        "promotion_approved": False,
        "ok_requested": False,
        "x2_accept": False,
        "mechanism_tag": MECHANISM_TAG,
        "alpha_sign": ALPHA_SIGN,
        "ic_sign_expected": IC_SIGN_EXPECTED,
        "flow_W": FLOW_W,
        "flow_min_valid": FLOW_MIN_VALID,
        "rebal_every_td": REBAL_EVERY,
        "style_cols_pinned": list(STYLE_COLS_PINNED),
        "style_source_pinned": STYLE_SOURCE_PINNED,
        "cost_bp_eval": COST_BP_EVAL,
        "decay_keep_pin": DECAY_KEEP_PIN,
        "universe": universe_label,
        "primary_universe": "HILIQ",
        "window": "x2",
        "x2_start": X2_START,
        "x2_end": X2_END,
        "mask_meta": mask_meta,
        "coverage_rebal": coverage,
        "coverage_median": med_cov,
        "coverage_gate": gate,
        "coverage_gate_pass": bool(med_cov >= gate),
        "pin_gaps": pin_gaps[:50],
        "n_pin_gaps": len(pin_gaps),
        "n_daily_rows": int(len(alpha_df)),
        "n_month_chunks_written": int(len(part_paths)),
        "frozen_sha8": FROZEN_SHA8,
        "frozen_receipt_sha8": FROZEN_RECEIPT_SHA8,
        "arch_frozen_review_sha8": ARCH_FROZEN_REVIEW_SHA8,
        "forbid_ok_sha8": list(FORBID_OK_SHA8),
        "leaf30_keep_repair_sha8_separate": LEAF30_KEEP_REPAIR_SHA8_SEPARATE,
        "sampler_prefix": SAMPLER_PREFIX,
        "rss_limit_mb": args.rss_limit_mb,
        "peak_kb": peak_kb(),
        "primary_load": "rebal_day_lazy_margin_float_bars",
        "created_et": datetime.now(ET).strftime("%Y-%m-%dT%H:%M:%S%z"),
        "notes": [
            "alpha = -rank(flow_resid); flow W=20; rebal=20",
            "flow_raw = mean_W((rzmre-rzche)/float_mktcap_T-1); PIT=available_at",
            "Resid: SW L1 demean + OLS(logmv T-1, mom20, vol20, logADV20)",
            "IC expected positive (comment pin); script does not flip on returns",
            "Ban Amihud / on_minus_id / CRR / hk_hold / margin_delta as main",
            "PRIMARY=HILIQ; FULLA research only via --also-fulla-research",
            "C3 overlap vs leaf19/25/27/30/31 + margin_delta; Jaccard>=0.7 hard reject",
            "peak_proof REQUIRED; rss=1500 ban raise",
            "C9 0087c928 not merged",
            "decay KEEP pin only (not run): latest_resid_alpha>0 AND not 5Q decline AND H2_net_cagr>510300",
        ],
    }
    return alpha_df, meta



def run_build(args) -> int:
    import pyarrow as pa
    import pyarrow.parquet as pq

    uni = normalize_universe(args.universe)
    if uni == "FULLA":
        print(
            "STOP: FULLA forbidden as PRIMARY (use --also-fulla-research)",
            file=sys.stderr,
        )
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
        sd = str(args.sample_dir.resolve())
        if not sd.startswith(SAMPLER_PREFIX.rstrip("_")) and not sd.startswith(
            "/tmp/quantlab_leaf32_margin_flow"
        ):
            print(
                f"STOP: sampler must be under {SAMPLER_PREFIX}* got={sd}",
                file=sys.stderr,
            )
            return 2

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

    alpha_df, meta = build_alpha_for_window(args, universe_label="HILIQ")
    et_ts = datetime.now(ET).strftime("%Y%m%d_%H%M%S")
    final_name = f"alpha_HILIQ_x2_{et_ts}.parquet"
    final_path = out / final_name
    table = pa.Table.from_pandas(alpha_df, preserve_index=False)
    tmpf = final_path.with_suffix(final_path.suffix + ".tmp")
    pq.write_table(table, tmpf, compression="zstd")
    tmpf.replace(final_path)

    meta.update(
        {
            "script": SCRIPT_REL,
            "script_sha256": script_sha256(),
            "script_sha8": script_sha256()[:8],
            "arch_ok_path": str(args.arch_ok_path),
            "arch_ok_sha256": ok_sha,
            "arch_ok_sha8": ok_sha[:8],
            "alpha_path": str(final_path.name),
            "alpha_sha256": sha256_file(final_path),
            "peak_kb_final": peak_kb(),
        }
    )

    # C3 overlap (default on real path unless --no-overlap-report)
    hard_reject = False
    pin_gap_fail = False
    if args.overlap_report or not args.no_overlap_report:
        ov_path = out / "overlap_vs_leaf19_25_27_30_31_margin_delta.json"
        try:
            ov = write_overlap_report(
                alpha_df,
                ov_path,
                {
                    "leaf19": Path(args.leaf19_alpha),
                    "leaf25": Path(args.leaf25_alpha),
                    "leaf27": Path(args.leaf27_alpha),
                    "leaf30": Path(args.leaf30_alpha),
                    "leaf31": Path(args.leaf31_alpha),
                    "margin_delta": Path(args.margin_delta),
                },
            )
            meta["overlap_report"] = str(ov_path.name)
            meta["overlap_any_jaccard_hard_reject"] = bool(
                ov.get("any_jaccard_hard_reject")
            )
            meta["overlap_any_required_pin_gap"] = bool(ov.get("any_required_pin_gap"))
            hard_reject = bool(ov.get("any_jaccard_hard_reject"))
            pin_gap_fail = bool(ov.get("any_required_pin_gap"))
        except Exception as e:
            meta["overlap_report_error"] = repr(e)
            print(f"STOP: overlap report failed: {e!r}", file=sys.stderr)
            return 3

    # Optional FULLA research (never PRIMARY)
    if args.also_fulla_research:
        try:
            a_f, m_f = build_alpha_for_window(args, universe_label="FULLA")
            fp = out / f"alpha_FULLA_x2_research_{et_ts}.parquet"
            t2 = pa.Table.from_pandas(a_f, preserve_index=False)
            tmp2 = fp.with_suffix(fp.suffix + ".tmp")
            pq.write_table(t2, tmp2, compression="zstd")
            tmp2.replace(fp)
            meta["fulla_research_alpha"] = str(fp.name)
            meta["fulla_research_meta"] = {
                "coverage_median": m_f.get("coverage_median"),
                "coverage_gate_pass": m_f.get("coverage_gate_pass"),
                "n_daily_rows": m_f.get("n_daily_rows"),
                "note": "research only; NOT PRIMARY verdict",
            }
            del a_f, m_f
            gc.collect()
        except Exception as e:
            meta["fulla_research_error"] = repr(e)
            print(
                f"WARN: FULLA research failed (PRIMARY HILIQ kept): {e!r}",
                file=sys.stderr,
            )

    meta_path = out / "run_meta.json"
    meta_path.write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(
        f"OK leaf32_margin_net_flow_resid universe=HILIQ window=x2 final={final_path} "
        f"peak_kb={peak_kb()} overlap_hard_reject={hard_reject} pin_gap={pin_gap_fail}",
        flush=True,
    )
    if pin_gap_fail:
        print(
            "STOP: C3 PIN_GAP missing required overlap target (margin_delta); "
            "see overlap_vs_leaf19_25_27_30_31_margin_delta.json",
            file=sys.stderr,
        )
        return 3
    if hard_reject:
        print(
            "STOP: C3 Jaccard>=0.7 hard reject vs leaf19/25/27/30/31/margin_delta "
            "(see overlap_vs_leaf19_25_27_30_31_margin_delta.json)",
            file=sys.stderr,
        )
        return 4
    if not meta.get("coverage_gate_pass"):
        print(
            f"STOP: coverage median {meta.get('coverage_median')} "
            f"< gate {COVERAGE_MEDIAN_HILIQ}",
            file=sys.stderr,
        )
        return 5
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Leaf32 margin net-flow resid alpha build (HILIQ x x2); "
            "NOT authorized without --allow-real-data + --arch-ok-path"
        )
    )
    ap.add_argument(
        "--universe",
        default="HILIQ",
        choices=("HILIQ", "HI_LIQ", "FULLA"),
        help="PRIMARY must be HILIQ (FULLA as --universe → STOP; use --also-fulla-research)",
    )
    ap.add_argument("--window", default="x2", choices=("x2",))
    ap.add_argument("--x2-end", default=X2_END_TRADE_DATE)
    ap.add_argument("--out", type=Path, default=None, help="Required for real build")
    ap.add_argument("--rss-limit-mb", type=int, default=RSS_LIMIT_MB)
    ap.add_argument("--c4-kb", type=int, default=C4_KB)
    ap.add_argument("--stop-kb", type=int, default=STOP_KB)
    ap.add_argument("--hard-kb", type=int, default=HARD_KB)
    ap.add_argument("--allow-real-data", action="store_true", default=False)
    ap.add_argument(
        "--arch-ok-path",
        type=Path,
        default=None,
        help="Existing Arch .ok (sha8 not in forbid); process gate with Main window",
    )
    ap.add_argument(
        "--execute",
        action="store_true",
        default=False,
        help="Optional; still requires --allow-real-data + --arch-ok-path",
    )
    ap.add_argument("--hi-liq-mask", type=Path, default=HI_LIQ_MASK_DEFAULT)
    ap.add_argument("--fulla-mask", type=Path, default=FULLA_MASK_DEFAULT)
    ap.add_argument("--sw-l1", type=Path, default=SW_L1_DEFAULT)
    ap.add_argument("--float-mktcap", type=Path, default=FLOAT_MKTCAP_DEFAULT)
    ap.add_argument("--daily-dir", type=Path, default=DAILY_DIR_DEFAULT)
    ap.add_argument("--adj-factor", type=Path, default=ADJ_FACTOR_DEFAULT)
    ap.add_argument("--calendar", type=Path, default=CAL_DEFAULT)
    ap.add_argument("--margin-detail", type=Path, default=MARGIN_DEFAULT)
    ap.add_argument("--leaf19-alpha", type=Path, default=LEAF19_ALPHA_DEFAULT)
    ap.add_argument("--leaf25-alpha", type=Path, default=LEAF25_ALPHA_DEFAULT)
    ap.add_argument("--leaf27-alpha", type=Path, default=LEAF27_ALPHA_DEFAULT)
    ap.add_argument("--leaf30-alpha", type=Path, default=LEAF30_ALPHA_DEFAULT)
    ap.add_argument("--leaf31-alpha", type=Path, default=LEAF31_ALPHA_DEFAULT)
    ap.add_argument("--margin-delta", type=Path, default=MARGIN_DELTA_DEFAULT)
    ap.add_argument("--sample-dir", type=Path, default=None)
    ap.add_argument(
        "--also-fulla-research",
        action="store_true",
        default=False,
        help="Optional FULLA research alpha (never PRIMARY verdict)",
    )
    ap.add_argument(
        "--overlap-report",
        action="store_true",
        default=False,
        help="Force write overlap JSON (also default on real path)",
    )
    ap.add_argument(
        "--no-overlap-report",
        action="store_true",
        default=False,
        help="Skip C3 overlap JSON (X2 sign will BAN; dry/dev only)",
    )
    ap.add_argument(
        "--dry-compile-only",
        action="store_true",
        default=False,
        help="Print pins; ZERO big-table load; exit 0",
    )
    args = ap.parse_args(argv)

    if args.dry_compile_only:
        return dry_compile_only_print(args)

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
