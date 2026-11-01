#!/usr/bin/env python3
"""Leaf 25 step -1 r3: 3-stock TTM hand-reconciliation extract (DRAFT, not run; needs its own read-only Arch .ok).

New file per Arch review efb013d8 (S-P2-1, S-P3-1); predecessor research/leaf25_ttm_recon_step_m1_r2.py
(f46e0fb5) is kept unchanged and is superseded (r2 itself followed review fc5fa937; 7edf577f also kept unchanged).

Reads ONLY data/v2/financials_pit/{financials,cashflow,balancesheet}_pit_tushare.parquet and the SSE calendar
(column projection; full-table pass on key columns for the deterministic pick, then ts_code filter to 3 codes;
files have a single row group, so the filter materializes the projected columns first - tens of MB, transient).
No prices, returns, weights, factors or panels. No fina_indicator-sourced columns (eps, roe, bps, profit_dedt, ...:
latest snapshot per (ts_code, end_date), not PIT) are read. Imports: stdlib, pandas, pyarrow only.
Writes only --out/{raw_rows.csv, ttm_script.csv, run_meta.json}.

Rules implemented (leaf 25 prereg r4 s2):
 - versions: per (table, ts_code, end_date), report_type == "1" only; every other value (text labels such as the
   consolidated period-end label, nulls) is never used, never remapped, and counted per value (all rows and
   end_date >= 2018). A row is usable on session d iff its own available_at converted to a Shanghai date < d;
   null available_at never used. Latest usable available_at wins; ties -> update_flag == "0", else earliest file
   row; tie groups counted. Null update_flag = not original (counted). Orphan corrections (groups with no
   update_flag "0" row) counted and disclosed.
 - end_date must be a quarter end (03-31/06-30/09-30/12-31); else ignored and counted. A fiscal-year change is not
   identifiable from end_date (no end_type column) - disclosed, not detected.
 - TTM_E = YTD_E + A_{y-1} - YTD_{E-1y}; E annual -> TTM = A_y. Same E for NI, CFO and TA.
 - fallback: newest E with all components usable on d; E at most one quarter older than the newest published
   income period and E >= d - 15 months; else NaN. avg TA = mean(TA_E, TA_{E-1y}); missing -> NaN.
 - NI = n_income (primary); n_income_attr_p reported alongside (disclosure).
Pick (deterministic, smallest ts_code; the trigger tuple is carried unchanged into phase 2):
 (i)  (ts_code, end_date, table, corr_date): end_date >= 2018 quarter end with >1 distinct available date in exactly
      one table; corr_date = second distinct available date; with d_after = next_open(corr_date) and
      d_before = prev_open(d_after), the availability-only fallback E (same rule as ttm_at: newest E whose components
      all have a usable row, one-quarter and 15-month caps; values not looked at) must exist on BOTH days and end_date
      must be one of that day's component periods for the table (income/cashflow: E, A_{y-1}, YTD_{E-1y};
      balance: TA_E, TA_{E-1y}) on BOTH days.
 (ii) (ts_code, y, a_date, q_date): y >= 2019, first Q1(y) income date <= first annual(y-1) income date.
 (iii)(ts_code, first_period, first_date): first report_type-1 income period >= 2019-03-31.
 rule_exercised per case is written into run_meta; any false -> exit code 4 (outputs still written).
 Case (ii) with Q1 before annual: on the Q1 effective day TTM must be NaN (one-quarter fallback cap), not merely
 "not OK with E = Q1".
"""
from __future__ import annotations

import argparse
import hashlib
import json
import resource
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
FP = ROOT / "data/v2/financials_pit"
INPUTS = {  # full sha256, re-pinned before the .ok is issued (Data rerun 10-14->10-16 may change them)
    "income": (FP / "financials_pit_tushare.parquet", "bc0f4c3d3cd70a11d17f44496861e21268806509656247400c64be2d3ae7fab3"),
    "cashflow": (FP / "cashflow_pit_tushare.parquet", "71d5c3d39fbf2de05064ce7f21334e15c9b1d977c64494ffe699f7eeb0b95d79"),
    "balance": (FP / "balancesheet_pit_tushare.parquet", "9ca054962e850cad7305262e978758c9e9f36613c4cca025efdd99276de8dbb5"),
    "calendar": (ROOT / "data/v2/calendar/trade_cal_sse_pit.parquet", "fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41"),
}
OUT_BASE = ROOT / "output/ai_factory/_leaf25_ttm_recon"
KEY = ["ts_code", "end_date", "ann_date", "f_ann_date", "available_at", "update_flag", "report_type"]
KEY1 = ["ts_code", "end_date", "available_at", "update_flag", "report_type"]  # phase-1 projection (memory)
VAL = {"income": ["n_income", "n_income_attr_p"], "cashflow": ["n_cashflow_act"], "balance": ["total_assets"]}
TABLES = ("income", "cashflow", "balance")
QEND = {"0331", "0630", "0930", "1231"}
SH = ZoneInfo("Asia/Shanghai")
MIN_END = pd.Timestamp("2018-01-01")
NULL = "<NULL>"


def stage(name: str) -> None:
    print(f"STAGE {name} ru_maxrss={resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}", file=sys.stderr, flush=True)


def vmhwm_kb() -> int | None:
    try:
        for line in open("/proc/self/status"):
            if line.startswith("VmHWM:"):
                return int(line.split()[1])
    except OSError:
        return None
    return None


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def die(msg: str, code: int = 3) -> None:
    print(f"STOP: {msg}", file=sys.stderr, flush=True)
    sys.exit(code)


def norm(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ts_code"] = df["ts_code"].astype(str)
    df["end_s"] = pd.to_datetime(df["end_date"].astype(str).str.replace("-", "").str[:8], format="%Y%m%d", errors="coerce")
    for c in ("report_type", "update_flag"):  # nulls kept distinguishable, never mapped to a real value
        df[c] = df[c].astype(object).where(df[c].notna(), NULL).astype(str).str.strip()
    av = pd.to_datetime(df["available_at"], errors="coerce", utc=True)
    df["avail_sh_date"] = av.dt.tz_convert(SH).dt.tz_localize(None).dt.normalize()
    df["qend_ok"] = df["end_s"].dt.strftime("%m%d").isin(QEND)
    return df


def read_keys(name: str, cols: list[str], codes: list[str] | None = None) -> pd.DataFrame:
    path = INPUTS[name][0]
    have = set(pq.read_schema(path).names)
    miss = [c for c in cols if c not in have]
    if miss:
        die(f"{name}: missing columns {miss}")
    filt = [("ts_code", "in", codes)] if codes else None
    df = pq.read_table(path, columns=cols, filters=filt).to_pandas()
    df["row_ord"] = range(len(df))
    df["table"] = name
    return norm(df)


def value_counts(df: pd.DataFrame) -> dict:
    out = {}
    late = df["end_s"] >= MIN_END
    for c in ("report_type", "update_flag"):
        out[c] = {"all": {k: int(v) for k, v in df[c].value_counts(dropna=False).items()},
                  "end_ge_2018": {k: int(v) for k, v in df.loc[late, c].value_counts(dropna=False).items()}}
    n_late = int(late.sum())
    n_other = int((late & (df["report_type"] != "1")).sum())
    out["report_type_not_1_share_end_ge_2018"] = (n_other / n_late) if n_late else None
    return out


def orphan_groups(df: pd.DataFrame) -> dict:
    g = df[(df["report_type"] == "1") & df["avail_sh_date"].notna()]
    has0 = (g["update_flag"] == "0").groupby([g["ts_code"], g["end_s"]]).any()
    late = has0.index.get_level_values(1) >= MIN_END
    return {"all": int((~has0).sum()), "end_ge_2018": int((~has0[late]).sum())}


def pick(df: pd.DataFrame, end: pd.Timestamp, d: pd.Timestamp, ties: list) -> pd.Series | None:
    """version rule: report_type 1, usable (avail_sh_date < d), latest avail; tie -> update_flag 0 else earliest row."""
    g = df[(df["end_s"] == end) & (df["report_type"] == "1") & df["avail_sh_date"].notna() & (df["avail_sh_date"] < d)]
    if g.empty:
        return None
    top = g[g["avail_sh_date"] == g["avail_sh_date"].max()]
    if len(top) > 1:
        ties.append((top["table"].iloc[0], top["ts_code"].iloc[0], str(end.date()), len(top)))
        orig = top[top["update_flag"] == "0"]
        top = orig if not orig.empty else top
        top = top.sort_values("row_ord")
    return top.iloc[0]


def keystr(r: pd.Series) -> str:
    return f"{r['end_s'].date()}|{r['avail_sh_date'].date()}|uf={r['update_flag']}|row={r['row_ord']}"


def ttm_at(code: str, d: pd.Timestamp, T: dict, ties: list) -> dict:
    inc = T["income"][(T["income"]["ts_code"] == code) & T["income"]["qend_ok"]]
    usable = inc[(inc["report_type"] == "1") & inc["avail_sh_date"].notna() & (inc["avail_sh_date"] < d)]
    out = {"ts_code": code, "asof": str(d.date())}
    if usable.empty:
        return {**out, "status": "NaN_no_income"}
    newest = usable["end_s"].max()
    for E in sorted(usable["end_s"].unique(), reverse=True):
        E = pd.Timestamp(E)
        if E < newest - pd.DateOffset(months=3) or E < d - pd.DateOffset(months=15):
            break
        y1 = E - pd.DateOffset(years=1)
        ann_prev = pd.Timestamp(year=E.year - 1, month=12, day=31)
        comp, ok = {}, True
        for tb in ("income", "cashflow"):
            src = T[tb][(T[tb]["ts_code"] == code) & T[tb]["qend_ok"]]
            if E.month == 12:
                r = pick(src, E, d, ties)
                ok &= r is not None
                comp[tb] = {"E": r}
            else:
                rs = {k: pick(src, e, d, ties) for k, e in (("E", E), ("A", ann_prev), ("P", y1))}
                ok &= all(v is not None for v in rs.values())
                comp[tb] = rs
        bal = T["balance"][(T["balance"]["ts_code"] == code) & T["balance"]["qend_ok"]]
        ta = {k: pick(bal, e, d, ties) for k, e in (("E", E), ("P", y1))}
        ok &= all(v is not None for v in ta.values())
        if not ok:
            continue
        res = dict(out, status="OK" if E == newest else "FALLBACK", E=str(E.date()))
        for tb, col in (("income", "n_income"), ("cashflow", "n_cashflow_act")):
            c = comp[tb]
            res[f"{tb}_ttm"] = c["E"][col] if E.month == 12 else c["E"][col] + c["A"][col] - c["P"][col]
            for k, r in c.items():
                res[f"{tb}_{k}_key"] = keystr(r)
                res[f"{tb}_{k}_val"] = r[col]
        c = comp["income"]
        res["n_income_attr_p_ttm"] = (c["E"]["n_income_attr_p"] if E.month == 12
                                      else c["E"]["n_income_attr_p"] + c["A"]["n_income_attr_p"] - c["P"]["n_income_attr_p"])
        res["avg_ta"] = (ta["E"]["total_assets"] + ta["P"]["total_assets"]) / 2
        for k, r in ta.items():
            res[f"balance_{k}_key"] = keystr(r)
            res[f"balance_{k}_val"] = r["total_assets"]
        res["cfacc"] = (res["income_ttm"] - res["cashflow_ttm"]) / res["avg_ta"] if res["avg_ta"] else float("nan")
        return res
    return {**out, "status": "NaN_no_complete_E_within_caps", "newest_E": str(newest.date())}


def component_periods(E: pd.Timestamp, table: str) -> set:
    y1 = E - pd.DateOffset(years=1)
    if table == "balance":
        return {E, y1}
    return {E} if E.month == 12 else {E, pd.Timestamp(year=E.year - 1, month=12, day=31), y1}


def avail_E(code: str, d: pd.Timestamp, G: dict) -> pd.Timestamp | None:
    """availability-only mirror of ttm_at's E choice (no values): newest E with every component row usable before d."""
    def periods(tb: str) -> set:
        try:
            g = G[tb].get_group(code)
        except KeyError:
            return set()
        return set(g.loc[g["avail_sh_date"] < d, "end_s"])
    have = {tb: periods(tb) for tb in TABLES}
    if not have["income"]:
        return None
    newest = max(have["income"])
    for E in sorted(have["income"], reverse=True):
        if E < newest - pd.DateOffset(months=3) or E < d - pd.DateOffset(months=15):
            break
        if all(component_periods(E, tb) <= have[tb] for tb in TABLES):
            return E
    return None


def find_key(row: dict, table: str, end: pd.Timestamp) -> str | None:
    for k in ("E", "A", "P"):
        v = row.get(f"{table}_{k}_key")
        if isinstance(v, str) and v.startswith(str(end.date()) + "|"):
            return v
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out).resolve()
    if OUT_BASE.resolve() not in out.parents:  # N-P3-6: path-component check, not a string prefix
        die("--out must be a directory strictly under output/ai_factory/_leaf25_ttm_recon/")
    if out.exists() and any(out.iterdir()):
        die("--out exists and is not empty")
    shas = {}
    for k, (p, pin) in INPUTS.items():
        s = sha256(p)
        shas[k] = s
        if s != pin:
            die(f"sha mismatch {k}: {s} != pinned {pin}")
    stage("sha_ok")
    cal = pq.read_table(INPUTS["calendar"][0], columns=["cal_date", "is_open"]).to_pandas()
    cal["d"] = pd.to_datetime(cal["cal_date"].astype(str).str.replace("-", "").str[:8], format="%Y%m%d")
    opens = cal.loc[cal["is_open"].astype(int) == 1, "d"].sort_values().reset_index(drop=True)
    del cal

    def next_open(x: pd.Timestamp) -> pd.Timestamp:
        return opens[opens > x].iloc[0]

    def prev_open(x: pd.Timestamp) -> pd.Timestamp:
        return opens[opens < x].iloc[-1]

    # phase 1: key columns only, all rows
    K = {n: read_keys(n, KEY1) for n in TABLES}
    stage("phase1_read")
    counts = {n: value_counts(df) for n, df in K.items()}
    orphans = {n: orphan_groups(df) for n, df in K.items()}
    nonq = {n: int((~df["qend_ok"]).sum()) for n, df in K.items()}
    arch_ruling = {n: c["report_type_not_1_share_end_ge_2018"] for n, c in counts.items()
                   if (c["report_type_not_1_share_end_ge_2018"] or 0) > 0.005}
    U = {n: df[(df["report_type"] == "1") & df["qend_ok"] & df["avail_sh_date"].notna()] for n, df in K.items()}
    del K
    # (i) trigger tuples: >1 distinct avail date in exactly one table, end >= 2018
    nv = {n: U[n][U[n]["end_s"] >= MIN_END].groupby(["ts_code", "end_s"])["avail_sh_date"].nunique() for n in TABLES}
    m = pd.concat(nv, axis=1).dropna()
    one = m[(m > 1).sum(axis=1) == 1]
    trig_raw = sorted((code, end, (one.loc[(code, end)] > 1).idxmax()) for code, end in one.index)
    G = {n: U[n][["ts_code", "end_s", "avail_sh_date"]].groupby("ts_code") for n in TABLES}
    vers = {n: U[n].groupby(["ts_code", "end_s"])["avail_sh_date"] for n in TABLES}
    trig_i, n_i_checked = None, 0
    for code, end, tb in trig_raw:
        n_i_checked += 1
        dd = sorted(vers[tb].get_group((code, end)).unique())
        corr = pd.Timestamp(dd[1])
        d_after = next_open(corr)
        d_before = prev_open(d_after)
        Eb, Ea = avail_E(code, d_before, G), avail_E(code, d_after, G)
        if Eb is None or Ea is None:
            continue
        if end in component_periods(Eb, tb) and end in component_periods(Ea, tb):
            trig_i = {"ts_code": code, "end_date": end, "table": tb, "corr_date": corr, "orig_date": pd.Timestamp(dd[0]),
                      "E_before": Eb, "E_after": Ea}
            break
    if trig_i is None:
        die("no candidate for rule i (TTM-relevant single-table correction)")
    # (ii) trigger tuples
    first = U["income"].groupby(["ts_code", "end_s"])["avail_sh_date"].min().reset_index()
    a = first[first["end_s"].dt.strftime("%m%d") == "1231"].assign(y=lambda x: x["end_s"].dt.year + 1)
    q = first[first["end_s"].dt.strftime("%m%d") == "0331"].assign(y=lambda x: x["end_s"].dt.year)
    j = a.merge(q, on=["ts_code", "y"], suffixes=("_a", "_q"))
    j = j[(j["y"] >= 2019) & (j["avail_sh_date_q"] <= j["avail_sh_date_a"])].sort_values(["ts_code", "y"])
    n_same_day = int((j["avail_sh_date_q"] == j["avail_sh_date_a"]).sum())
    n_q1_first = int((j["avail_sh_date_q"] < j["avail_sh_date_a"]).sum())
    jj = j[j["ts_code"] != trig_i["ts_code"]]
    if jj.empty:
        die("no candidate for rule ii")
    r2 = jj.iloc[0]
    trig_ii = {"ts_code": r2["ts_code"], "y": int(r2["y"]), "a_date": r2["avail_sh_date_a"], "q_date": r2["avail_sh_date_q"],
               "same_day": bool(r2["avail_sh_date_q"] == r2["avail_sh_date_a"])}
    # (iii) trigger tuples
    f3 = first.sort_values(["ts_code", "end_s"]).groupby("ts_code").first()
    f3 = f3[(f3["end_s"] >= pd.Timestamp("2019-03-31")) & ~f3.index.isin([trig_i["ts_code"], trig_ii["ts_code"]])]
    if f3.empty:
        die("no candidate for rule iii")
    trig_iii = {"ts_code": f3.index[0], "first_period": f3["end_s"].iloc[0], "first_date": f3["avail_sh_date"].iloc[0]}
    n_cand = {"i_raw": len(trig_raw), "i_checked_until_hit": n_i_checked, "ii": int(j["ts_code"].nunique()),
              "iii": int((first.groupby("ts_code")["end_s"].min() >= pd.Timestamp("2019-03-31")).sum())}
    del U, G, vers, first, a, q, j, jj, m, one, nv, f3
    codes = [trig_i["ts_code"], trig_ii["ts_code"], trig_iii["ts_code"]]
    stage("phase1_pick")
    # phase 2: 3 codes, all needed columns
    T = {n: read_keys(n, KEY + VAL[n], codes) for n in TABLES}
    stage("phase2_read")
    ties: list = []
    rows, dates, exercised, detail = [], {}, {}, {}

    def run(code: str, ds: set) -> dict:
        ds = sorted(ds)
        dates[code] = [str(x.date()) for x in ds]
        res = {}
        for d in ds:
            r = ttm_at(code, d, T, ties)
            rows.append(r)
            res[d] = r
        return res

    # case i: before/after the correction for the triggering (code, end, table)
    c = trig_i["ts_code"]
    d_after = next_open(trig_i["corr_date"])
    d_before = prev_open(d_after)
    res = run(c, {d_before, d_after, next_open(trig_i["orig_date"])} | extra_dates(T, c, next_open, prev_open))
    kb, ka = find_key(res[d_before], trig_i["table"], trig_i["end_date"]), find_key(res[d_after], trig_i["table"], trig_i["end_date"])
    ok_i = (kb is not None and ka is not None and ka.split("|")[1] == str(trig_i["corr_date"].date())
            and kb.split("|")[1] < str(trig_i["corr_date"].date()))
    exercised["i_one_table_correction"], detail["i"] = bool(ok_i), {"key_before": kb, "key_after": ka}
    # case ii: the trigger year's annual(y-1) / Q1(y) dates
    c = trig_ii["ts_code"]
    dq = next_open(trig_ii["q_date"])
    da = next_open(trig_ii["a_date"])
    res = run(c, {prev_open(dq), dq, da, prev_open(da)} | extra_dates(T, c, next_open, prev_open))
    q1 = pd.Timestamp(year=trig_ii["y"], month=3, day=31)
    rq = res[dq]
    if trig_ii["same_day"]:  # Q1 and annual become usable together: E = Q1(y) using that A_{y-1}, no fallback
        ok_ii = rq.get("status") == "OK" and rq.get("E") == str(q1.date()) and \
            str(rq.get("income_A_key", "")).startswith(f"{trig_ii['y'] - 1}-12-31|")
    else:  # Q1 before annual: one-quarter fallback cap -> TTM must be NaN on dq (S-P3-1)
        ok_ii = str(rq.get("status", "")).startswith("NaN")
    exercised["ii_annual_q1_same_day_or_q1_first"], detail["ii"] = bool(ok_ii), {"row_at_q1_effective": rq}
    # case iii: first report of an IPO name -> NaN (fewer than 4 quarters / no prior-year components)
    c = trig_iii["ts_code"]
    d3 = next_open(trig_iii["first_date"])
    res = run(c, {d3} | extra_dates(T, c, next_open, prev_open))
    ok_iii = str(res[d3].get("status", "")).startswith("NaN")
    exercised["iii_ipo_lt4q"], detail["iii"] = bool(ok_iii), {"row_at_first_report": res[d3]}
    for c in codes:
        if len(dates[c]) < 4:
            die(f"{c}: only {len(dates[c])} as-of dates derivable")
    stage("ttm")
    out.mkdir(parents=True, exist_ok=True)
    raw = pd.concat([T[n] for n in TABLES], ignore_index=True, sort=False)
    raw.to_csv(out / "raw_rows.csv", index=False)
    pd.DataFrame(rows).to_csv(out / "ttm_script.csv", index=False)
    all_ok = all(exercised.values())
    meta = {
        "script": "research/leaf25_ttm_recon_step_m1_r3.py", "input_sha256": shas, "codes": codes,
        "triggers": {"i": trig_i, "ii": trig_ii, "iii": trig_iii}, "rule_exercised": exercised, "rule_detail": detail,
        "asof_dates": dates, "n_tie_groups": len(ties), "ties": ties[:200], "nonquarter_end_rows": nonq,
        "report_type_update_flag_counts": counts, "arch_ruling_required_report_type_share_gt_0_5pct": arch_ruling,
        "orphan_correction_groups": orphans, "n_annual_q1_same_day_all_codes": n_same_day,
        "n_q1_before_annual_all_codes": n_q1_first, "n_candidates": n_cand, "rules": __doc__,
        "peak_rss_kb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, "vmhwm_kb": vmhwm_kb(),
        "finished_et": datetime.now(ZoneInfo("America/New_York")).isoformat(), "rc": 0 if all_ok else 4,
    }
    (out / "run_meta.json").write_text(json.dumps(meta, indent=1, default=str), encoding="utf-8")
    stage("done")
    print(f"peak_check step_m1_r3 rss_kb={meta['peak_rss_kb']} hwm_kb={meta['vmhwm_kb']}", file=sys.stderr, flush=True)
    if not all_ok:
        print(f"STOP: rule_exercised false: {exercised}", file=sys.stderr, flush=True)
        return 4
    return 0


def extra_dates(T: dict, code: str, next_open, prev_open) -> set:
    """context dates: around the latest annual, after the latest H1/Q3, after the earliest Q1 (all >= 2018)."""
    inc = T["income"][(T["income"]["ts_code"] == code) & (T["income"]["report_type"] == "1")
                      & T["income"]["avail_sh_date"].notna() & (T["income"]["end_s"] >= MIN_END)]
    ds = set()
    md = inc["end_s"].dt.strftime("%m%d")
    ann = inc[md == "1231"].groupby("end_s")["avail_sh_date"].min()
    if not ann.empty:
        ds |= {next_open(ann.iloc[-1]), prev_open(next_open(ann.iloc[-1]))}
    qq = inc[md.isin({"0630", "0930"})].groupby("end_s")["avail_sh_date"].min()
    if not qq.empty:
        ds.add(next_open(qq.iloc[-1]))
    q1 = inc[md == "0331"].groupby("end_s")["avail_sh_date"].min()
    if not q1.empty:
        ds.add(next_open(q1.iloc[0]))
    return ds


if __name__ == "__main__":
    sys.exit(main())
