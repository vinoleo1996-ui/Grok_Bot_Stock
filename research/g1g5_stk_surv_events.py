"""stk_surv event variants (counts only; no prices). Prereg docs/v2/AI_G1G5_STK_SURV_WHO_PAYS_PREREG_ZH.md. promotion=false.
available_at = surv_date + L(=25) trading days 09:00 (Data p95). Event date returned as 'd' = trading day before available_at
so downstream T1 = available_at day, T2 = next session."""
from __future__ import annotations
import glob
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data/v2/events/stk_surv_2018plus.parquet"
L = 25


def _cal() -> pd.DatetimeIndex:
    c = pd.read_parquet(ROOT / "data/v2/tushare_raw/trade_cal.parquet")
    if "exchange" in c: c = c[c.exchange.isin(["SSE", ""]) | c.exchange.isna()] if (c.exchange == "SSE").any() else c
    c = c[c.is_open.astype(int) == 1]
    return pd.DatetimeIndex(sorted(pd.to_datetime(c.cal_date.astype(str).unique(), format="%Y%m%d")))


def load(universe: set[str]) -> pd.DataFrame:
    r = pd.read_parquet(SRC, columns=["ts_code", "surv_date", "rece_org"])
    r = r[r.ts_code.isin(universe) & r.surv_date.notna()].copy()
    r["sd"] = pd.to_datetime(r.surv_date, format="%Y%m%d", errors="coerce")
    return r.dropna(subset=["sd"])


def _avail_minus1(sd: pd.Series, cal: pd.DatetimeIndex) -> pd.Series:
    k = cal.searchsorted(sd.values, side="left")  # surv day (or next session) index
    k = np.minimum(k + L - 1, len(cal) - 1)
    return pd.Series(cal[k], index=sd.index)


def variants(universe: set[str]) -> tuple[dict, dict]:
    cal = _cal(); r = load(universe)
    days = r.groupby(["ts_code", "sd"]).rece_org.nunique().reset_index().sort_values(["ts_code", "sd"])
    out = {}
    # V1: no survey in prior 365 days, but at least one earlier survey
    prev = days.groupby("ts_code").sd.shift(1)
    v1 = days[(days.sd - prev).dt.days >= 365]
    out["gap1y_resurv"] = v1[["ts_code", "sd"]]
    # V2: survey within [actual_date, actual_date+5d] of periodic report; one event per report (first survey day)
    fs = sorted(glob.glob(str(ROOT / "data/v2/tushare_raw/disclosure_date/end_*.parquet")))
    dd = pd.concat([pd.read_parquet(f, columns=["ts_code", "end_date", "actual_date"]) for f in fs], ignore_index=True)
    dd = dd[dd.ts_code.isin(universe) & dd.actual_date.notna() & (dd.actual_date.astype(str).str.len() == 8)].drop_duplicates(["ts_code", "end_date"], keep="last")
    dd["ad"] = pd.to_datetime(dd.actual_date, format="%Y%m%d")
    m = days.merge(dd[["ts_code", "end_date", "ad"]], on="ts_code")
    m = m[(m.sd >= m.ad) & (m.sd <= m.ad + pd.Timedelta(days=5))].sort_values("sd").drop_duplicates(["ts_code", "end_date"])
    out["post_report_5d"] = m[["ts_code", "sd"]]
    # V3: rolling 10 trading days distinct orgs >= 20 (first crossing; next allowed after 60 trading days)
    ci = {d: i for i, d in enumerate(cal)}
    r["ti"] = cal.searchsorted(r.sd.values, side="left")
    ev3, dist = [], []
    for ts, g in r.groupby("ts_code"):
        g = g.sort_values("ti"); last = -10**9
        tis = g.ti.unique()
        for t in tis:
            n = g[(g.ti > t - 10) & (g.ti <= t)].rece_org.nunique(); dist.append(n)
            if n >= 20 and t - last >= 60:
                ev3.append((ts, cal[min(t, len(cal) - 1)])); last = t
    out["dense10d_ge20"] = pd.DataFrame(ev3, columns=["ts_code", "sd"])
    st = {}
    for k, e in out.items():
        e = e.copy(); e["d"] = _avail_minus1(e.sd, cal).values
        x = e[e.sd >= "2023-10-01"]
        st[k] = dict(n=int(len(e)), names=int(e.ts_code.nunique()), by_year=e.groupby(e.sd.dt.year).size().to_dict(),
                     x2_n=int(len(x)), x2_names=int(x.ts_code.nunique()), x2_by_year=x.groupby(x.sd.dt.year).size().to_dict())
        out[k] = e.rename(columns={"ts_code": "instrument"})
    q = np.percentile(dist, [50, 75, 90, 95, 99]) if dist else []
    st["rolling10d_org_count_dist"] = dict(n_obs=len(dist), p50_75_90_95_99=[float(v) for v in q], share_ge20=float(np.mean(np.array(dist) >= 20)))
    return out, st
