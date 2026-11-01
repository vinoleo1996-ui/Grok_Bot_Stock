"""tp_rerate event builder (counts only; no prices/returns). Prereg docs/v2/AI_G1G5_TP_RERATE_WHO_PAYS_PREREG_ZH.md.
Target price = report_rc max_price/min_price (NOTE: report_rc 'tp' is 利润总额 total profit, NOT target price; see prereg).
tgt = mean of available (max_price, min_price) > 0. Per (stock, org): one row per report_date (last), compare vs that org's previous tgt
on the same stock (any earlier date, no staleness limit). Raise = tgt/prev - 1 >= 0.20. Event = on the session of a raise, the number of
DISTINCT orgs with a raise in the trailing 10-session window (incl. today) reaches >=3. Event date = that report_date (d).
Cooldown: after an event, no new event on the same stock for 60 sessions. promotion=false; live=false."""
from __future__ import annotations
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]
RC = ROOT / "data/v2/events/report_rc_2018plus.parquet"
UP, MIN_ORGS, WIN, COOL = 0.20, 3, 10, 60


def events(universe: set[str], sessions: pd.DatetimeIndex) -> tuple[pd.DataFrame, dict]:
    r = pd.read_parquet(RC, columns=["ts_code", "report_date", "org_name", "max_price", "min_price"])
    r = r[r.ts_code.isin(universe)]
    mx = r.max_price.where(r.max_price > 0); mn = r.min_price.where(r.min_price > 0)
    r = r.assign(tgt=pd.concat([mx, mn], axis=1).mean(axis=1)).dropna(subset=["tgt"])
    r["org"] = r.org_name.astype(str).str.strip()
    r["rd"] = pd.to_datetime(r.report_date, format="%Y%m%d")
    r = r.reset_index(drop=True).reset_index().rename(columns={"index": "seq"})
    r = r.sort_values(["ts_code", "org", "rd", "seq"]).drop_duplicates(["ts_code", "org", "rd"], keep="last")
    r["prev"] = r.groupby(["ts_code", "org"]).tgt.shift(1)
    r["chg"] = r.tgt / r.prev - 1
    up = r[r.chg >= UP].copy()
    # session index: report on non-trading day maps to next session
    up["si"] = sessions.searchsorted(up.rd, side="left")
    up = up[up.si < len(sessions)]
    out = []
    for code, g in up.groupby("ts_code"):
        g = g.sort_values(["si", "seq"]); last_ev = -10**9
        for si in sorted(g.si.unique()):
            if si - last_ev < COOL:
                continue
            w = g[(g.si > si - WIN) & (g.si <= si)]
            n = w.org.nunique()
            if n >= MIN_ORGS:
                d = g[g.si == si].rd.max()
                out.append(dict(instrument=code, d=d, si=int(si), n_orgs=int(n), med_chg=float(w.chg.median())))
                last_ev = si
    E = pd.DataFrame(out)
    st = dict(n_tgt_rows_pool=int(len(r)), n_raise_rows=int(len(up)), n_events=int(len(E)),
              n_names=int(E.instrument.nunique()) if len(E) else 0,
              by_year={int(k): int(v) for k, v in E.groupby(E.d.dt.year).size().items()} if len(E) else {})
    return E, st
