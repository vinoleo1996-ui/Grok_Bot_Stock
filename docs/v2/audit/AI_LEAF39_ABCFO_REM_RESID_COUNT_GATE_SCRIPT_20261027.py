#!/usr/bin/env python3
"""Leaf39 ABCFO REM residual — HI_LIQ lightweight count gate (NOT X2 / NOT LAND).

APPROX residual: after YTD→single-quarter differencing, cross-section OLS within SW L1
  CFO/A = b0 + b1*(1/A) + b2*(S/A) + b3*(dS/A) + e
alpha_raw = -e  (low abnormal CFO = REM suspicion → short/avoid; long high ABCFO)
Hard gate (DRAFT): Jaccard OR rho_excess vs leaf19/25/30 any >0.5 → reject.
Coverage: masked median computable names >=300 AND zero_frac<=0.05.
No PnL/IC/CAGR. live=false. Do not touch fund MDD / leaf38.
"""
from __future__ import annotations

import hashlib
import json
import resource
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = Path("/workspace/QuantLab")
X2_START = pd.Timestamp("2024-06-03")
X2_END = pd.Timestamp("2026-10-09")
REBAL_EVERY = 20
MASK_PATH = ROOT / "output/strategy_hiliq/universe_mask_hiliq_v1.parquet"
CF_PATH = ROOT / "data/v2/financials_pit/cashflow_pit_tushare.parquet"
FIN_PATH = ROOT / "data/v2/financials_pit/financials_pit_tushare.parquet"
BS_PATH = ROOT / "data/v2/financials_pit/bs_cf_pit_tushare.parquet"
SW_PATH = ROOT / "data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet"
L19_ALPHA = ROOT / "output/ai_factory/leaf19_cfacc_rnoa/alpha_HILIQ_20261014_213132.parquet"
L25_ALPHA = ROOT / (
    "output/ai_factory/_leaf25_full_factor/20261026_015610/"
    "alpha_HILIQ_x2_20261026_125138.parquet"
)
L30_ALPHA = ROOT / (
    "output/ai_factory/_leaf30_crr/20261027_003132/"
    "alpha_HILIQ_x2_20261027_010815.parquet"
)
EXCLUDE_SW = {"银行": "801780.SI", "房地产": "801180.SI", "非银金融": "801790.SI"}
OUT_JSON = ROOT / "docs/v2/audit/AI_LEAF39_ABCFO_REM_RESID_COUNT_GATE_20261027.json"
COV_MEDIAN_MIN = 300.0
ZERO_FRAC_MAX = 0.05
HARD_OVERLAP = 0.5


def rss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def sha8(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:8]


def mem_available_gi() -> float:
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) / (1024 * 1024)
    except OSError:
        return float("nan")
    return float("nan")


def to_ts(x) -> str:
    s = str(x)
    if s.startswith(("sh.", "sz.", "bj.")):
        mkt, code = s.split(".", 1)
        return f"{code}.{mkt.upper()}"
    return s


def load_mask() -> tuple[pd.DatetimeIndex, pd.DataFrame]:
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


def _earliest_pit(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    df = df.copy()
    df["available_at"] = pd.to_datetime(df["available_at"], utc=True).dt.tz_convert(None)
    df["end_date"] = pd.to_datetime(df["end_date"])
    df["ts_code"] = df["ts_code"].astype(str)
    df = df.sort_values(["ts_code", "end_date", "available_at"])
    df = df.drop_duplicates(["ts_code", "end_date"], keep="first")
    return df[["ts_code", "end_date", "available_at"] + cols]


def ytd_to_qtr(df: pd.DataFrame, value_cols: list[str]) -> pd.DataFrame:
    """Difference YTD within fiscal year; Q1 (month=3) stays as-is."""
    out = df.copy()
    out["year"] = out["end_date"].dt.year
    out["month"] = out["end_date"].dt.month
    out = out.sort_values(["ts_code", "end_date"])
    for c in value_cols:
        prev = out.groupby("ts_code")[c].shift(1)
        prev_year = out.groupby("ts_code")["year"].shift(1)
        prev_month = out.groupby("ts_code")["month"].shift(1)
        same_year = prev_year == out["year"]
        # only diff when prior is earlier quarter same year
        do = same_year & out["month"].isin([6, 9, 12]) & prev_month.isin([3, 6, 9])
        q = out[c].copy()
        q.loc[do] = out.loc[do, c] - prev.loc[do]
        out[c + "_q"] = q
    return out


def build_fundamentals() -> pd.DataFrame:
    cf = pq.read_table(
        CF_PATH, columns=["ts_code", "end_date", "available_at", "n_cashflow_act"]
    ).to_pandas()
    fin = pq.read_table(
        FIN_PATH, columns=["ts_code", "end_date", "available_at", "revenue", "total_revenue"]
    ).to_pandas()
    bs = pq.read_table(
        BS_PATH, columns=["ts_code", "end_date", "available_at", "total_assets"]
    ).to_pandas()
    cf = _earliest_pit(cf, ["n_cashflow_act"])
    fin = _earliest_pit(fin, ["revenue", "total_revenue"])
    bs = _earliest_pit(bs, ["total_assets"])
    fin["sales"] = fin["total_revenue"].fillna(fin["revenue"])
    m = cf.merge(fin[["ts_code", "end_date", "sales"]], on=["ts_code", "end_date"], how="inner")
    m = m.merge(bs[["ts_code", "end_date", "total_assets"]], on=["ts_code", "end_date"], how="inner")
    # assets as-of prior period end for scale A_{t-1}
    m = m.sort_values(["ts_code", "end_date"])
    m["A_lag"] = m.groupby("ts_code")["total_assets"].shift(1)
    m = ytd_to_qtr(m, ["n_cashflow_act", "sales"])
    m["sales_lag_q"] = m.groupby("ts_code")["sales_q"].shift(1)
    m["dS"] = m["sales_q"] - m["sales_lag_q"]
    # valid building blocks
    m["ok_blocks"] = (
        m["n_cashflow_act_q"].notna()
        & m["sales_q"].notna()
        & m["A_lag"].notna()
        & (m["A_lag"] > 0)
        & m["dS"].notna()
        & np.isfinite(m["n_cashflow_act_q"].astype(float))
        & np.isfinite(m["sales_q"].astype(float))
        & np.isfinite(m["dS"].astype(float))
    )
    return m


def load_sw() -> pd.DataFrame:
    sw = pq.read_table(
        SW_PATH,
        columns=["instrument_id", "sw_code", "sw_name", "in_date", "out_date", "available_at"],
    ).to_pandas()
    sw["instrument"] = sw["instrument_id"].map(to_ts)
    sw["in_date"] = pd.to_datetime(sw["in_date"], errors="coerce")
    sw["out_date"] = pd.to_datetime(sw["out_date"], errors="coerce")
    sw["available_at"] = pd.to_datetime(sw["available_at"], errors="coerce")
    return sw


def sw_asof(sw: pd.DataFrame, asof: pd.Timestamp) -> pd.DataFrame:
    asof = pd.Timestamp(asof)
    ok = (sw["in_date"].isna() | (sw["in_date"] <= asof)) & (
        sw["out_date"].isna() | (sw["out_date"] > asof)
    )
    avail_ok = sw["available_at"].isna() | (sw["available_at"] <= asof)
    cur = sw.loc[ok & avail_ok].copy()
    # if multiple, keep latest in_date
    cur = cur.sort_values(["instrument", "in_date"]).drop_duplicates("instrument", keep="last")
    return cur[["instrument", "sw_code", "sw_name"]]


def exclude_set(sw_cur: pd.DataFrame) -> set[str]:
    codes = set(EXCLUDE_SW.values())
    names = set(EXCLUDE_SW.keys())
    m = sw_cur["sw_code"].isin(codes) | sw_cur["sw_name"].isin(names)
    return set(sw_cur.loc[m, "instrument"].astype(str))


def asof_panel(fund: pd.DataFrame, asof: pd.Timestamp) -> pd.DataFrame:
    asof = pd.Timestamp(asof)
    # available_at is naive UTC-stripped Asia/Shanghai wall; compare date-wise
    # treat available_at date <= asof calendar date (PIT: next session after announce — DRAFT uses available_at.date() <= asof)
    sub = fund.loc[fund["available_at"] <= asof].copy()
    if sub.empty:
        return sub
    sub = sub.sort_values(["ts_code", "available_at", "end_date"]).drop_duplicates(
        "ts_code", keep="last"
    )
    return sub


def ols_resid_sw(df: pd.DataFrame) -> pd.Series:
    """Within SW L1 cross-section OLS; fallback market-wide if n<25."""
    y = (df["n_cashflow_act_q"] / df["A_lag"]).astype(float)
    X = np.column_stack(
        [
            np.ones(len(df)),
            (1.0 / df["A_lag"]).astype(float),
            (df["sales_q"] / df["A_lag"]).astype(float),
            (df["dS"] / df["A_lag"]).astype(float),
        ]
    )
    resid = pd.Series(np.nan, index=df.index, dtype=float)

    def _fit(idx):
        if len(idx) < 25:
            return
        yy = y.loc[idx].to_numpy()
        xx = X[df.index.get_indexer(idx)]
        mask = np.isfinite(yy) & np.isfinite(xx).all(axis=1)
        if mask.sum() < 25:
            return
        yy = yy[mask]
        xx = xx[mask]
        try:
            beta, *_ = np.linalg.lstsq(xx, yy, rcond=None)
            e = yy - xx @ beta
            resid.loc[np.array(idx)[mask]] = e
        except np.linalg.LinAlgError:
            return

    for _, g in df.groupby("sw_code"):
        _fit(list(g.index))
    # fallback for NaN: market-wide
    miss = resid.isna() & y.notna()
    if miss.sum() >= 25:
        idx = list(df.index[miss])
        _fit(idx)
    return resid


def load_alpha(path: Path, dates: list[pd.Timestamp]) -> pd.DataFrame:
    schema = pq.read_schema(path)
    names = set(schema.names)
    date_col = "date" if "date" in names else "trade_date"
    inst_col = "instrument" if "instrument" in names else "ts_code"
    field = schema.field(date_col)
    import pyarrow as pa

    is_str = pa.types.is_string(field.type) or pa.types.is_large_string(field.type)
    cols = [date_col, inst_col, "alpha"]
    if is_str:
        dmin, dmax = min(dates).strftime("%Y-%m-%d"), max(dates).strftime("%Y-%m-%d")
        t = pq.read_table(path, columns=cols, filters=[(date_col, ">=", dmin), (date_col, "<=", dmax)])
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
    df = df.rename(columns={date_col: "date", inst_col: "instrument"})
    df["instrument"] = df["instrument"].astype(str).map(to_ts)
    want = set(pd.Timestamp(d) for d in dates)
    df = df[df["date"].isin(want)].copy()
    return df


def spearman(a, b) -> float:
    if len(a) < 5:
        return float("nan")
    ra = pd.Series(a).rank().to_numpy()
    rb = pd.Series(b).rank().to_numpy()
    if np.nanstd(ra) == 0 or np.nanstd(rb) == 0:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def top_jaccard(codes_a, scores_a, codes_b, scores_b, k=20) -> float:
    if len(codes_a) == 0 or len(codes_b) == 0:
        return float("nan")
    sa = pd.Series(scores_a, index=codes_a)
    sb = pd.Series(scores_b, index=codes_b)
    common = sa.index.intersection(sb.index)
    if len(common) < k:
        # still compute on available
        pass
    ta = set(sa.nlargest(min(k, len(sa))).index)
    tb = set(sb.nlargest(min(k, len(sb))).index)
    u = ta | tb
    if not u:
        return float("nan")
    return float(len(ta & tb) / len(u))


def main():
    t0 = time.time()
    mem0 = mem_available_gi()
    peak = rss_mb()
    dates, mask_df = load_mask()
    rebal = pick_rebal(dates)
    peak = max(peak, rss_mb())
    fund = build_fundamentals()
    peak = max(peak, rss_mb())
    sw = load_sw()
    peak = max(peak, rss_mb())

    # sample overlap days: up to 6 evenly
    if len(rebal) <= 6:
        overlap_days = list(rebal)
    else:
        idxs = np.linspace(0, len(rebal) - 1, 6).round().astype(int)
        overlap_days = [rebal[i] for i in sorted(set(idxs))]

    alphas = {}
    for tag, path in [("leaf19", L19_ALPHA), ("leaf25", L25_ALPHA), ("leaf30", L30_ALPHA)]:
        if path.exists():
            alphas[tag] = load_alpha(path, overlap_days)
            peak = max(peak, rss_mb())
        else:
            alphas[tag] = None

    cov_raw = []
    cov_mask = []
    overlap_rows = []
    pin_gaps = []

    mask_by_date = {
        pd.Timestamp(d): set(g["instrument"].astype(str))
        for d, g in mask_df.groupby("date")
    }

    for d in rebal:
        hi = mask_by_date.get(pd.Timestamp(d), set())
        pan = asof_panel(fund, d)
        if pan.empty:
            cov_raw.append(0)
            cov_mask.append(0)
            continue
        pan = pan[pan["ok_blocks"]].copy()
        pan["instrument"] = pan["ts_code"].astype(str)
        pan = pan[pan["instrument"].isin(hi)].copy()
        cov_raw.append(int(pan["instrument"].nunique()))
        sw_cur = sw_asof(sw, d)
        excl = exclude_set(sw_cur)
        pan = pan[~pan["instrument"].isin(excl)].copy()
        pan = pan.merge(sw_cur, on="instrument", how="left")
        # require SW for residual path
        pan_sw = pan[pan["sw_code"].notna()].copy()
        n_mask = int(pan_sw["instrument"].nunique())
        cov_mask.append(n_mask)

        if pd.Timestamp(d) in set(pd.Timestamp(x) for x in overlap_days) and n_mask >= 25:
            resid = ols_resid_sw(pan_sw)
            pan_sw = pan_sw.copy()
            pan_sw["abcfo"] = resid  # abnormal CFO
            pan_sw["alpha"] = -pan_sw["abcfo"]  # long high ABCFO (less REM)
            valid = pan_sw["alpha"].notna()
            codes = pan_sw.loc[valid, "instrument"].tolist()
            scores = pan_sw.loc[valid, "alpha"].to_numpy(dtype=float)
            row = {"date": str(pd.Timestamp(d).date()), "n": int(valid.sum())}
            for tag, adf in alphas.items():
                if adf is None or adf.empty:
                    row[f"rho_{tag}"] = None
                    row[f"j20_{tag}"] = None
                    pin_gaps.append(f"alpha_missing_{tag}")
                    continue
                sub = adf[adf["date"] == pd.Timestamp(d)]
                if sub.empty:
                    row[f"rho_{tag}"] = None
                    row[f"j20_{tag}"] = None
                    continue
                # align
                sb = sub.set_index("instrument")["alpha"]
                common = [c for c in codes if c in sb.index]
                if len(common) < 30:
                    row[f"rho_{tag}"] = None
                    row[f"j20_{tag}"] = None
                    continue
                a = pd.Series(scores, index=codes).loc[common].to_numpy()
                b = sb.loc[common].to_numpy(dtype=float)
                row[f"rho_{tag}"] = spearman(a, b)
                row[f"j20_{tag}"] = top_jaccard(codes, scores, sb.index.tolist(), sb.to_numpy(dtype=float), 20)
            overlap_rows.append(row)
        peak = max(peak, rss_mb())

    def stats(arr):
        a = np.asarray(arr, dtype=float)
        if len(a) == 0:
            return {"median": None, "min": None, "p10": None, "n_days": 0, "zero_frac": None}
        return {
            "median": float(np.median(a)),
            "min": float(np.min(a)),
            "p10": float(np.percentile(a, 10)),
            "n_days": int(len(a)),
            "zero_frac": float(np.mean(a <= 0)),
        }

    st_raw = stats(cov_raw)
    st_mask = stats(cov_mask)

    def agg_overlap(key_prefix):
        out = {}
        for tag in ["leaf19", "leaf25", "leaf30"]:
            vals = [r[f"{key_prefix}_{tag}"] for r in overlap_rows if r.get(f"{key_prefix}_{tag}") is not None]
            vals = [float(v) for v in vals if v == v]
            out[tag] = {
                "mean": float(np.mean(vals)) if vals else None,
                "max": float(np.max(vals)) if vals else None,
                "n": len(vals),
            }
        return out

    rho = agg_overlap("rho")
    j20 = agg_overlap("j20")

    hard_hits = []
    for tag in ["leaf19", "leaf25", "leaf30"]:
        for metric, blob in [("rho", rho[tag]), ("j20", j20[tag])]:
            mx = blob.get("max")
            if mx is not None and mx > HARD_OVERLAP:
                hard_hits.append({"vs": tag, "metric": metric, "max": mx})

    gate_cov = (
        st_mask["median"] is not None
        and st_mask["median"] >= COV_MEDIAN_MIN
        and st_mask["zero_frac"] is not None
        and st_mask["zero_frac"] <= ZERO_FRAC_MAX
    )
    hard_reject = len(hard_hits) > 0
    # if overlap entirely missing → PIN_GAP, coverage can still pass but gate notes
    overlap_ok = all(
        (rho[t]["n"] > 0 and j20[t]["n"] > 0) for t in ["leaf19", "leaf25", "leaf30"]
    )
    if not overlap_ok:
        pin_gaps.append("overlap_partial_or_missing")

    gate_pass = bool(gate_cov and not hard_reject)

    payload = {
        "leaf": 39,
        "mechanism_tag": "g1g5_ashare_abcfo_rem_resid_v1",
        "asof_et": "2026-10-27",
        "window": {"start": str(X2_START.date()), "end": str(X2_END.date()), "rebal_every": REBAL_EVERY},
        "n_rebal": len(rebal),
        "coverage_raw": st_raw,
        "coverage_masked": st_mask,
        "exclude_sw": EXCLUDE_SW,
        "overlap_days": [str(pd.Timestamp(d).date()) for d in overlap_days],
        "overlap_rows": overlap_rows,
        "rho_excess_approx": rho,
        "jaccard_top20": j20,
        "hard_overlap_threshold": HARD_OVERLAP,
        "hard_reject_hits": hard_hits,
        "hard_reject": hard_reject,
        "gate_cov_pass": gate_cov,
        "gate_pass": gate_pass,
        "gate_rule": (
            f"masked_median>={COV_MEDIAN_MIN} AND zero_frac<={ZERO_FRAC_MAX} "
            f"AND NOT (Jaccard_top20 OR rho_excess vs leaf19/25/30 any max >{HARD_OVERLAP})"
        ),
        "approx": [
            "YTD cashflow/sales differenced to single-quarter within fiscal year",
            "cross-section OLS within SW L1 at rebalance (NOT full year×industry historical panel as Northeast Securities may use)",
            "A_lag = prior end_date total_assets; sales=total_revenue fallback revenue",
            "rho/jaccard vs leaf19/25/30 on up to 6 rebal days; rho is rank Spearman on alpha (not excess-return rho)",
            "no style residual beyond SW L1 grouped OLS; size/style residual left to FROZEN/X2",
        ],
        "gaps": sorted(set(pin_gaps)),
        "input_sha8": {
            "hiliq": sha8(MASK_PATH),
            "cashflow": sha8(CF_PATH),
            "financials": sha8(FIN_PATH),
            "bs_cf": sha8(BS_PATH),
            "sw_l1": sha8(SW_PATH),
            "leaf19_alpha": sha8(L19_ALPHA) if L19_ALPHA.exists() else None,
            "leaf25_alpha": sha8(L25_ALPHA) if L25_ALPHA.exists() else None,
            "leaf30_alpha": sha8(L30_ALPHA) if L30_ALPHA.exists() else None,
        },
        "peak_rss_mb": float(peak),
        "mem_available_gi_start": float(mem0),
        "mem_available_gi_end": float(mem_available_gi()),
        "elapsed_sec": float(time.time() - t0),
        "EXECUTED_full_alpha": False,
        "ok_requested": False,
        "live": False,
        "promotion_approved": False,
        "leo_notify": False,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT_JSON.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(OUT_JSON)
    print(json.dumps({
        "gate_pass": gate_pass,
        "gate_cov_pass": gate_cov,
        "hard_reject": hard_reject,
        "masked_median": st_mask["median"],
        "zero_frac": st_mask["zero_frac"],
        "peak_rss_mb": peak,
        "out": str(OUT_JSON),
        "hard_hits": hard_hits,
        "rho": rho,
        "j20": j20,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
