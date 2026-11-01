"""report_rc_allup event builder (counts only; no prices). Prereg docs/v2/AI_G1G5_REPORT_RC_WHO_PAYS_PREREG_*_ZH.md.
Trigger: disclosure_date actual_date (periodic reports). Window [d, d+5 calendar days] on report_date.
Forecast year = report year (quarter == YYYYQ4). Per org: last in-window np vs that org's latest record before d.
Orgs without prior record ignored. Event: >=3 comparable orgs and all strictly up. promotion=false."""
from __future__ import annotations
import glob
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]
RC = ROOT / "data/v2/events/report_rc_2018plus.parquet"
WIN_DAYS, MIN_ORGS = 5, 3


def triggers(universe: set[str]) -> pd.DataFrame:
    fs = sorted(glob.glob(str(ROOT / "data/v2/tushare_raw/disclosure_date/end_*.parquet")))
    d = pd.concat([pd.read_parquet(f, columns=["ts_code", "end_date", "actual_date"]) for f in fs], ignore_index=True)
    d = d[d.ts_code.isin(universe) & d.actual_date.notna() & (d.actual_date.astype(str).str.len() == 8)]
    d = d.drop_duplicates(["ts_code", "end_date"], keep="last")
    d["d"] = pd.to_datetime(d.actual_date, format="%Y%m%d")
    return d[["ts_code", "end_date", "d"]].drop_duplicates(["ts_code", "d"]).reset_index(drop=True)


def events(universe: set[str]) -> tuple[pd.DataFrame, dict]:
    r = pd.read_parquet(RC, columns=["ts_code", "report_date", "org_name", "quarter", "np"])
    r = r[r.ts_code.isin(universe) & r.np.notna()]
    r = r[r.quarter == r.report_date.str[:4] + "Q4"].copy()
    r["rd"] = pd.to_datetime(r.report_date, format="%Y%m%d")
    r = r.reset_index(drop=True).reset_index().rename(columns={"index": "seq"})
    r = r.sort_values(["ts_code", "org_name", "rd", "seq"]).drop_duplicates(["ts_code", "org_name", "rd"], keep="last")
    T = triggers(universe)
    by = {k: g for k, g in r.groupby("ts_code")}
    out = []
    for t in T.itertuples():
        g = by.get(t.ts_code)
        if g is None:
            continue
        end = t.d + pd.Timedelta(days=WIN_DAYS)
        w = g[(g.rd >= t.d) & (g.rd <= end)]
        if w.empty:
            continue
        yr = str(t.d.year) + "Q4"
        w = w[w.quarter == yr]
        n_cmp, n_up = 0, 0
        for org, wo in w.groupby("org_name"):
            new = wo.sort_values("rd").np.iloc[-1]
            pr = g[(g.org_name == org) & (g.quarter == yr) & (g.rd < t.d)]
            if pr.empty:
                continue
            n_cmp += 1
            n_up += int(new > pr.sort_values("rd").np.iloc[-1])
        if n_cmp >= MIN_ORGS and n_up == n_cmp:
            out.append(dict(instrument=t.ts_code, trig=t.d, d=end, end_date=t.end_date, n_orgs=n_cmp))
    E = pd.DataFrame(out)
    stats = dict(n_rc_rows_pool_curyear=int(len(r)), n_triggers=int(len(T)), n_events=int(len(E)),
                 n_names=int(E.instrument.nunique()) if len(E) else 0,
                 by_year=E.groupby(E.trig.dt.year).size().to_dict() if len(E) else {})
    return E, stats
