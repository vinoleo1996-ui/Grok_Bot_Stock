"""FULLA-speed report_rc_allup events — same definition as g1g5_report_rc_allup_events.py,
vectorized for ~130k triggers. Used only by *_weights_fulla_v1.py."""
from __future__ import annotations
import glob
from pathlib import Path
import numpy as np
import pandas as pd

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
    if T.empty or r.empty:
        E = pd.DataFrame(columns=["instrument", "trig", "d", "end_date", "n_orgs"])
        return E, dict(n_rc_rows_pool_curyear=int(len(r)), n_triggers=int(len(T)), n_events=0, n_names=0, by_year={})

    # Window rows: report in [trig.d, trig.d+5] for same ts_code, year-matched Q4
    T = T.copy()
    T["trig_id"] = np.arange(len(T))
    T["end"] = T["d"] + pd.Timedelta(days=WIN_DAYS)
    T["yr"] = T["d"].dt.year.astype(str) + "Q4"

    # Merge RC onto triggers by ts_code (may be large; filter window after)
    m = r.merge(T, on="ts_code", how="inner")
    # in-window updates
    w = m[(m["rd"] >= m["d"]) & (m["rd"] <= m["end"]) & (m["quarter"] == m["yr"])]
    if w.empty:
        E = pd.DataFrame(columns=["instrument", "trig", "d", "end_date", "n_orgs"])
        return E, dict(n_rc_rows_pool_curyear=int(len(r)), n_triggers=int(len(T)), n_events=0, n_names=0, by_year={})
    # last in-window np per (trig, org)
    w = w.sort_values(["trig_id", "org_name", "rd"])
    w_last = w.groupby(["trig_id", "org_name"], sort=False).tail(1)[["trig_id", "ts_code", "org_name", "np", "d", "end", "end_date", "yr"]]
    w_last = w_last.rename(columns={"np": "new_np"})

    # prior: same org, same year Q4, rd < trig.d — last before d
    # Build prior lookup from r
    prior = r.rename(columns={"np": "old_np"})[["ts_code", "org_name", "quarter", "rd", "old_np"]]
    joined = w_last.merge(prior, left_on=["ts_code", "org_name", "yr"], right_on=["ts_code", "org_name", "quarter"], how="left")
    joined = joined[joined["rd"].notna() & (joined["rd"] < joined["d"])]
    if joined.empty:
        E = pd.DataFrame(columns=["instrument", "trig", "d", "end_date", "n_orgs"])
        return E, dict(n_rc_rows_pool_curyear=int(len(r)), n_triggers=int(len(T)), n_events=0, n_names=0, by_year={})
    joined = joined.sort_values(["trig_id", "org_name", "rd"])
    prior_last = joined.groupby(["trig_id", "org_name"], sort=False).tail(1)
    prior_last["up"] = prior_last["new_np"] > prior_last["old_np"]

    agg = prior_last.groupby("trig_id").agg(n_cmp=("org_name", "size"), n_up=("up", "sum"),
                                            ts_code=("ts_code", "first"), d=("d", "first"),
                                            end=("end", "first"), end_date=("end_date", "first"))
    hit = agg[(agg["n_cmp"] >= MIN_ORGS) & (agg["n_up"] == agg["n_cmp"])]
    if hit.empty:
        E = pd.DataFrame(columns=["instrument", "trig", "d", "end_date", "n_orgs"])
    else:
        E = pd.DataFrame(dict(instrument=hit["ts_code"].values, trig=hit["d"].values,
                              d=hit["end"].values, end_date=hit["end_date"].values,
                              n_orgs=hit["n_cmp"].astype(int).values))
    stats = dict(n_rc_rows_pool_curyear=int(len(r)), n_triggers=int(len(T)), n_events=int(len(E)),
                 n_names=int(E.instrument.nunique()) if len(E) else 0,
                 by_year=E.groupby(pd.to_datetime(E.trig).dt.year).size().to_dict() if len(E) else {})
    return E, stats
