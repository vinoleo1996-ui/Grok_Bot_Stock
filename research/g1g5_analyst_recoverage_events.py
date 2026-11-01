"""analyst_recoverage events (no prices). Same org re-covers same stock after >=183d gap. promotion=false."""
from __future__ import annotations
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
RC = ROOT / "data/v2/events/report_rc_2018plus.parquet"
GAP = 183


def events(universe: set[str]):
    r = pd.read_parquet(RC, columns=["ts_code", "report_date", "org_name"])
    r = r[r.ts_code.isin(universe) & r.org_name.notna()].drop_duplicates()
    r["rd"] = pd.to_datetime(r.report_date, format="%Y%m%d")
    r = r.drop_duplicates(["ts_code", "org_name", "rd"]).sort_values(["ts_code", "org_name", "rd"])
    r["gap"] = (r.rd - r.groupby(["ts_code", "org_name"]).rd.shift(1)).dt.days
    e = r[r.gap >= GAP]
    E = e.groupby(["ts_code", "rd"]).org_name.nunique().reset_index().rename(columns={"ts_code": "instrument", "rd": "d", "org_name": "n_orgs"})
    st = dict(n_rows_pool=int(len(r)), n_events=int(len(E)), n_names=int(E.instrument.nunique()),
              by_year=E.groupby(E.d.dt.year).size().to_dict())
    x = E[E.d >= "2023-10-01"]
    st.update(x2_events=int(len(x)), x2_names=int(x.instrument.nunique()), x2_by_year=x.groupby(x.d.dt.year).size().to_dict())
    return E, st
