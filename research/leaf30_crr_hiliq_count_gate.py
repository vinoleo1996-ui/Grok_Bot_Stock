#!/usr/bin/env python3
"""Leaf30 CRR HI_LIQ lightweight count gate (NOT X2 / NOT selfcheck).

APPROX: uses ocf_to_profit_pit_daily_tushare as CRR proxy (YTD OCF/NP),
not full 16-quarter operate_profit CRR + CFOOE residual vol_pen.
No PnL / IC / CAGR. live=false.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
X2_START = pd.Timestamp("2024-06-03")
X2_END = pd.Timestamp("2026-10-09")
REBAL_EVERY = 20
MASK_PATH = ROOT / "output/strategy_hiliq/universe_mask_hiliq_v1.parquet"
OCF_DAILY = ROOT / "data/v2/financials_pit/ocf_to_profit_pit_daily_tushare.parquet"
SW_PATH = ROOT / "data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet"
L19_ALPHA = ROOT / "output/ai_factory/leaf19_cfacc_rnoa/alpha_HILIQ_20261014_213132.parquet"
L25_ALPHA = ROOT / (
    "output/ai_factory/_leaf25_full_factor/20261026_015610/"
    "alpha_HILIQ_x2_20261026_125138.parquet"
)
EXCLUDE_SW = {
    "银行": "801780.SI",
    "房地产": "801180.SI",
    "非银金融": "801790.SI",
}
OUT_JSON = ROOT / "output/ai_factory/leaf30_crr_hiliq_count_20261026.json"
SAMPLER_DIR = Path("/tmp")


def rss_mb() -> float:
    # Linux ru_maxrss is KB
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def to_ts(x) -> str:
    s = str(x)
    if s.startswith(("sh.", "sz.", "bj.")):
        mkt, code = s.split(".", 1)
        return f"{code}.{mkt.upper()}"
    return s


def mem_available_gi() -> float:
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) / (1024 * 1024)
    except OSError:
        return float("nan")
    return float("nan")


def load_mask_dates() -> tuple[pd.DatetimeIndex, pd.DataFrame]:
    t = pq.read_table(
        MASK_PATH,
        columns=["date", "instrument", "in_universe"],
        filters=[
            ("date", ">=", X2_START.to_datetime64()),
            ("date", "<=", X2_END.to_datetime64()),
            ("in_universe", "==", True),
        ],
    )
    df = t.to_pandas()
    df["date"] = pd.to_datetime(df["date"])
    df["instrument"] = df["instrument"].astype(str)
    dates = pd.DatetimeIndex(sorted(df["date"].unique()))
    return dates, df


def pick_rebal(dates: pd.DatetimeIndex) -> list[pd.Timestamp]:
    if len(dates) == 0:
        return []
    idx = list(range(0, len(dates), REBAL_EVERY))
    if idx[-1] != len(dates) - 1:
        idx.append(len(dates) - 1)
    return [pd.Timestamp(dates[i]) for i in idx]


def load_ocf_on_dates(dates: list[pd.Timestamp]) -> pd.DataFrame:
    # Arrow filter on timestamp list can be large; use min/max then filter
    t = pq.read_table(
        OCF_DAILY,
        columns=[
            "trade_date",
            "ts_code",
            "ocf_to_profit",
            "n_cashflow_act",
            "net_profit",
            "denom_small",
            "np_negative",
            "period_basis",
        ],
        filters=[
            ("trade_date", ">=", min(dates).to_datetime64()),
            ("trade_date", "<=", max(dates).to_datetime64()),
        ],
    )
    df = t.to_pandas()
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    want = set(pd.Timestamp(d) for d in dates)
    df = df[df["trade_date"].isin(want)].copy()
    df["ts_code"] = df["ts_code"].astype(str)
    # valid CRR proxy: finite ocf_to_profit, not denom_small, net_profit>0 preferred
    df["valid"] = (
        df["ocf_to_profit"].notna()
        & np.isfinite(df["ocf_to_profit"].astype(float))
        & (~df["denom_small"].fillna(False))
        & (df["net_profit"].fillna(0) > 0)
    )
    return df


def load_sw_exclude_set(asof: pd.Timestamp) -> set[str]:
    """Instruments in bank / RE / non-bank finance as-of date (PIT-ish)."""
    t = pq.read_table(
        SW_PATH,
        columns=["instrument_id", "sw_code", "sw_name", "in_date", "out_date", "available_at"],
    )
    sw = t.to_pandas()
    sw["in_date"] = pd.to_datetime(sw["in_date"], errors="coerce")
    sw["out_date"] = pd.to_datetime(sw["out_date"], errors="coerce")
    sw["available_at"] = pd.to_datetime(sw["available_at"], errors="coerce")
    codes = set(EXCLUDE_SW.values())
    names = set(EXCLUDE_SW.keys())
    m = sw["sw_code"].isin(codes) | sw["sw_name"].isin(names)
    sw = sw.loc[m].copy()
    asof = pd.Timestamp(asof)
    ok = (sw["in_date"].isna() | (sw["in_date"] <= asof)) & (
        sw["out_date"].isna() | (sw["out_date"] > asof)
    )
    # available_at: if present, require <= asof; if null keep (disclose)
    avail_ok = sw["available_at"].isna() | (sw["available_at"] <= asof)
    sw = sw.loc[ok & avail_ok]
    return set(to_ts(x) for x in sw["instrument_id"].astype(str))


def spearman_rho(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 5:
        return float("nan")
    ra = pd.Series(a).rank().to_numpy()
    rb = pd.Series(b).rank().to_numpy()
    if np.nanstd(ra) == 0 or np.nanstd(rb) == 0:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def top_jaccard(codes_a: list[str], scores_a: np.ndarray, codes_b: list[str], scores_b: np.ndarray, k: int = 20) -> float:
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


def load_alpha_on_dates(path: Path, date_col: str, inst_col: str, dates: list[pd.Timestamp]) -> pd.DataFrame:
    schema = pq.read_schema(path)
    field = schema.field(date_col)
    is_str = pa.types.is_string(field.type) or pa.types.is_large_string(field.type)
    cols = [date_col, inst_col, "alpha"]
    if is_str:
        # leaf25 trade_date is string YYYY-MM-DD
        dmin = min(dates).strftime("%Y-%m-%d")
        dmax = max(dates).strftime("%Y-%m-%d")
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
                (date_col, ">=", min(dates).to_datetime64()),
                (date_col, "<=", max(dates).to_datetime64()),
            ],
        )
    df = t.to_pandas()
    df[date_col] = pd.to_datetime(df[date_col])
    want = set(pd.Timestamp(d) for d in dates)
    df = df[df[date_col].isin(want)].copy()
    df.rename(columns={date_col: "date", inst_col: "instrument"}, inplace=True)
    df["instrument"] = df["instrument"].astype(str)
    return df


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-json", type=Path, default=OUT_JSON)
    args = ap.parse_args()
    t0 = time.time()
    peak = rss_mb()
    mem0 = mem_available_gi()
    gaps: list[str] = []
    approx: list[str] = [
        "CRR proxy = ocf_to_profit from ocf_to_profit_pit_daily_tushare (YTD_cumulative OCF/net_profit), NOT full 16Q operate_profit CRR",
        "vol_pen not computed this count pass (coverage uses CRR proxy validity only; overlap uses rank(ocf_to_profit))",
        "lambda not selected from returns",
    ]

    # preflight mem
    if mem0 < 3.0:
        # A18 avoidance: if Eng may be up and mem tight, HOLD
        print(json.dumps({"hold": True, "reason": "MemAvailable<3Gi", "mem_gi": mem0}, ensure_ascii=False))
        return 2

    dates, mask_df = load_mask_dates()
    peak = max(peak, rss_mb())
    rebal = pick_rebal(dates)
    if len(rebal) < 3:
        gaps.append("too_few_rebal_dates")

    # sample up to 6 uniform rebal dates for overlap
    if len(rebal) <= 6:
        sample_days = list(rebal)
    else:
        idxs = np.linspace(0, len(rebal) - 1, 6)
        sample_days = [rebal[int(round(i))] for i in idxs]
        # unique preserve order
        seen = set()
        uniq = []
        for d in sample_days:
            if d not in seen:
                seen.add(d)
                uniq.append(d)
        sample_days = uniq

    ocf = load_ocf_on_dates(rebal)
    peak = max(peak, rss_mb())
    period_basis_modes = (
        ocf["period_basis"].astype(str).value_counts().head(5).to_dict() if len(ocf) else {}
    )

    # SW exclude: rebuild per asof is heavy; use membership active anytime in X2 union then refine per day via in/out
    sw_all = pq.read_table(
        SW_PATH,
        columns=["instrument_id", "sw_code", "sw_name", "in_date", "out_date", "available_at"],
    ).to_pandas()
    sw_all["in_date"] = pd.to_datetime(sw_all["in_date"], errors="coerce")
    sw_all["out_date"] = pd.to_datetime(sw_all["out_date"], errors="coerce")
    sw_all["available_at"] = pd.to_datetime(sw_all["available_at"], errors="coerce")
    sw_ex = sw_all[
        sw_all["sw_code"].isin(EXCLUDE_SW.values()) | sw_all["sw_name"].isin(EXCLUDE_SW.keys())
    ].copy()
    sw_ex["ts_code"] = sw_ex["instrument_id"].map(to_ts)
    peak = max(peak, rss_mb())

    def excluded_asof(asof: pd.Timestamp) -> set[str]:
        asof = pd.Timestamp(asof)
        m = (sw_ex["in_date"].isna() | (sw_ex["in_date"] <= asof)) & (
            sw_ex["out_date"].isna() | (sw_ex["out_date"] > asof)
        ) & (sw_ex["available_at"].isna() | (sw_ex["available_at"] <= asof))
        return set(sw_ex.loc[m, "ts_code"].astype(str))

    cov_raw = []
    cov_masked = []
    zero_raw = 0
    zero_masked = 0
    n_names_with_any = set()

    mask_by_date = {d: set(g["instrument"].astype(str)) for d, g in mask_df.groupby("date")}

    for d in rebal:
        univ = mask_by_date.get(pd.Timestamp(d), set())
        day = ocf[ocf["trade_date"] == pd.Timestamp(d)]
        day_u = day[day["ts_code"].isin(univ) & day["valid"]]
        n_raw = int(day_u["ts_code"].nunique())
        ex = excluded_asof(d)
        day_m = day_u[~day_u["ts_code"].isin(ex)]
        n_m = int(day_m["ts_code"].nunique())
        cov_raw.append(n_raw)
        cov_masked.append(n_m)
        if n_raw == 0:
            zero_raw += 1
        if n_m == 0:
            zero_masked += 1
        n_names_with_any.update(day_m["ts_code"].tolist())

    cov_raw_a = np.array(cov_raw, dtype=float)
    cov_m_a = np.array(cov_masked, dtype=float)

    def stats(a: np.ndarray) -> dict:
        if len(a) == 0:
            return {"median": None, "min": None, "p10": None, "mean": None, "n_days": 0}
        return {
            "median": float(np.median(a)),
            "min": float(np.min(a)),
            "p10": float(np.percentile(a, 10)),
            "mean": float(np.mean(a)),
            "n_days": int(len(a)),
        }

    # Overlap vs leaf19 / leaf25 on sample_days
    overlaps = {"vs_leaf19": [], "vs_leaf25": []}
    try:
        a19 = load_alpha_on_dates(L19_ALPHA, "date", "instrument", sample_days)
    except Exception as e:
        a19 = pd.DataFrame()
        gaps.append(f"leaf19_alpha_load:{e}")
    try:
        a25 = load_alpha_on_dates(L25_ALPHA, "trade_date", "ts_code", sample_days)
    except Exception as e:
        a25 = pd.DataFrame()
        gaps.append(f"leaf25_alpha_load:{e}")
    peak = max(peak, rss_mb())

    l19_sha = sha256_file(L19_ALPHA) if L19_ALPHA.exists() else None
    l25_sha = sha256_file(L25_ALPHA) if L25_ALPHA.exists() else None
    ocf_sha = sha256_file(OCF_DAILY) if OCF_DAILY.exists() else None

    for d in sample_days:
        univ = mask_by_date.get(pd.Timestamp(d), set())
        ex = excluded_asof(d)
        day = ocf[(ocf["trade_date"] == pd.Timestamp(d)) & ocf["valid"]]
        day = day[day["ts_code"].isin(univ) & ~day["ts_code"].isin(ex)]
        crr = day.set_index("ts_code")["ocf_to_profit"].astype(float)

        def one(vs_name: str, adf: pd.DataFrame):
            if adf is None or len(adf) == 0:
                overlaps[vs_name].append({"date": str(d.date()), "n_common": 0, "rho": None, "jaccard_top20": None})
                return
            sub = adf[adf["date"] == pd.Timestamp(d)].dropna(subset=["alpha"])
            sub = sub[sub["instrument"].isin(crr.index)]
            if len(sub) < 5:
                overlaps[vs_name].append({"date": str(d.date()), "n_common": int(len(sub)), "rho": None, "jaccard_top20": None})
                return
            common = sorted(set(sub["instrument"]) & set(crr.index))
            xa = crr.reindex(common).to_numpy()
            xb = sub.set_index("instrument")["alpha"].reindex(common).astype(float).to_numpy()
            m = np.isfinite(xa) & np.isfinite(xb)
            xa, xb = xa[m], xb[m]
            codes = [c for c, ok in zip(common, m) if ok]
            overlaps[vs_name].append(
                {
                    "date": str(d.date()),
                    "n_common": int(len(codes)),
                    "rho": spearman_rho(xa, xb),
                    "jaccard_top20": top_jaccard(codes, xa, codes, xb, 20),
                }
            )

        one("vs_leaf19", a19)
        one("vs_leaf25", a25)

    def agg_overlap(rows: list[dict]) -> dict:
        rhos = [r["rho"] for r in rows if r.get("rho") is not None and np.isfinite(r["rho"])]
        jacs = [r["jaccard_top20"] for r in rows if r.get("jaccard_top20") is not None and np.isfinite(r["jaccard_top20"])]
        return {
            "n_sample_days": len(rows),
            "rho_mean": float(np.mean(rhos)) if rhos else None,
            "rho_max": float(np.max(rhos)) if rhos else None,
            "jaccard_top20_mean": float(np.mean(jacs)) if jacs else None,
            "jaccard_top20_max": float(np.max(jacs)) if jacs else None,
            "days": rows,
        }

    o19 = agg_overlap(overlaps["vs_leaf19"])
    o25 = agg_overlap(overlaps["vs_leaf25"])

    st_raw = stats(cov_raw_a)
    st_m = stats(cov_m_a)
    zero_frac_m = float(zero_masked / len(rebal)) if rebal else 1.0
    median_m = st_m["median"]
    gate_pass = bool(
        median_m is not None
        and median_m >= 300
        and zero_frac_m <= 0.05
        and (o19["jaccard_top20_max"] is None or o19["jaccard_top20_max"] < 0.7)
        and (o25["jaccard_top20_max"] is None or o25["jaccard_top20_max"] < 0.7)
    )
    # Note: ρ>0.5 is strength filter only — does not alone fail gate_pass
    strength_filter_flags = {
        "leaf19_rho_mean_gt_0_5": bool(o19["rho_mean"] is not None and o19["rho_mean"] > 0.5),
        "leaf25_rho_mean_gt_0_5": bool(o25["rho_mean"] is not None and o25["rho_mean"] > 0.5),
    }

    if "operate_profit" not in pq.read_schema(OCF_DAILY).names:
        gaps.append("ocf_daily_lacks_operate_profit_column_full_CRR_needs_financials_pit")

    peak = max(peak, rss_mb())
    out = {
        "mechanism_tag": "g1g5_ashare_crr_cfooe_volpen_v1",
        "leaf": 30,
        "live": False,
        "promotion_approved": False,
        "approx": True,
        "approx_notes": approx,
        "gaps": gaps,
        "universe": "HI_LIQ_V1.1",
        "mask_path": str(MASK_PATH.relative_to(ROOT)),
        "window": {"start": str(X2_START.date()), "end": str(X2_END.date())},
        "rebalance_every_td": REBAL_EVERY,
        "n_rebal_days": len(rebal),
        "sample_overlap_days": [str(d.date()) for d in sample_days],
        "industry_exclude": EXCLUDE_SW,
        "period_basis_modes": {str(k): int(v) for k, v in period_basis_modes.items()},
        "names_with_valid_crr_proxy_any_rebal_masked": len(n_names_with_any),
        "coverage_raw_hiliq": st_raw,
        "coverage_masked_hiliq": st_m,
        "zero_coverage_days_raw": zero_raw,
        "zero_coverage_days_masked": zero_masked,
        "zero_coverage_frac_masked": zero_frac_m,
        "overlap": {"vs_leaf19": o19, "vs_leaf25": o25},
        "strength_filter_flags": strength_filter_flags,
        "gate_pass": gate_pass,
        "gate_rule": "masked_median>=300 AND zero_frac_masked<=0.05 AND jaccard_top20_max vs leaf19/25 <0.7 (rho>0.5 strength-only)",
        "inputs_sha256": {
            "ocf_daily": ocf_sha,
            "leaf19_alpha": l19_sha,
            "leaf25_alpha": l25_sha,
            "leaf25_alpha_sha8_expected": "8be12024",
            "leaf25_alpha_sha8_actual": (l25_sha[:8] if l25_sha else None),
        },
        "rss_peak_mb": round(peak, 2),
        "mem_available_gi_start": round(mem0, 3),
        "mem_available_gi_end": round(mem_available_gi(), 3),
        "elapsed_sec": round(time.time() - t0, 2),
        "x2_run": False,
        "selfcheck_run": False,
        "book_smoke_run": False,
        "a18_touched": False,
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    tmp = args.out_json.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, args.out_json)
    out_sha = sha256_file(args.out_json)
    summary = {
        "gate_pass": gate_pass,
        "masked_median": median_m,
        "masked_min": st_m["min"],
        "masked_p10": st_m["p10"],
        "zero_frac_masked": zero_frac_m,
        "rho_mean_l19": o19["rho_mean"],
        "rho_mean_l25": o25["rho_mean"],
        "jacc_max_l19": o19["jaccard_top20_max"],
        "jacc_max_l25": o25["jaccard_top20_max"],
        "json": str(args.out_json),
        "json_sha8": out_sha[:8],
        "rss_peak_mb": round(peak, 2),
        "approx": True,
    }
    print(json.dumps(summary, ensure_ascii=False))
    print("FULL_JSON_SHA256", out_sha)
    return 0 if gate_pass else 1


if __name__ == "__main__":
    sys.exit(main())
