#!/usr/bin/env python3
"""Leaf 25 step -1: 3-stock TTM hand-reconciliation extract (DRAFT, not run; needs its own read-only Arch .ok).

Reads ONLY data/v2/financials_pit/{financials,cashflow,balancesheet}_pit_tushare.parquet and the SSE calendar
(column projection; full-table pass on key columns for the deterministic stock pick, then pushdown filter to 3 codes).
No prices, returns, weights, factors or panels. Imports: stdlib, pandas, pyarrow only.
Writes only --out/{raw_rows.csv, ttm_script.csv, run_meta.json}.

Rules implemented (leaf 25 prereg r3 §2):
 - versions: per (table, ts_code, end_date), report_type == '1' only; a row is usable on session d iff its own
   available_at (coalesce(f_ann_date, ann_date) 18:00 Asia/Shanghai, file column) converted to Shanghai date < d;
   rows with null available_at are never used. Among usable rows take the latest available_at; ties on the same
   available_at -> update_flag == '0' (original), else the earliest row in file order; tie groups counted.
 - end_date must be a quarter end (03-31/06-30/09-30/12-31); else ignored and counted; two annual rows in one year -> NaN.
 - TTM_E = YTD_E + A_{y-1} - YTD_{E-1y}; E annual -> TTM = A_y. Same E for NI, CFO and TA.
 - fallback: newest E with all components usable on d; E at most one quarter older than the newest published income
   period and E >= d - 15 months; else NaN (counted). avg TA = mean(TA_E, TA_{E-1y}); missing -> NaN.
 - NI = n_income (consolidated, leaf 19); n_income_attr_p reported alongside (disclosure).
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
KEY = ["ts_code", "end_date", "ann_date", "f_ann_date", "available_at", "update_flag", "report_type"]
KEY1 = ["ts_code", "end_date", "available_at", "update_flag", "report_type"]  # phase-1 projection (memory)
VAL = {"income": ["n_income", "n_income_attr_p"], "cashflow": ["n_cashflow_act"], "balance": ["total_assets"]}
QEND = {"0331", "0630", "0930", "1231"}
SH = ZoneInfo("Asia/Shanghai")
MIN_END = pd.Timestamp("2018-01-01")


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
    df["report_type"] = df["report_type"].astype(str).str.strip()
    df["update_flag"] = df["update_flag"].astype(str).str.strip()
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
    t = pq.read_table(path, columns=cols, filters=filt)
    df = t.to_pandas()
    df["row_ord"] = range(len(df))
    df["table"] = name
    return norm(df)


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
        for tb, col in (("income", "n_income"), ("cashflow", "n_cashflow_act")):
            src = T[tb][T[tb]["ts_code"] == code]
            if E.month == 12:
                r = pick(src, E, d, ties)
                ok &= r is not None
                comp[tb] = {"E": r}
            else:
                rs = {k: pick(src, e, d, ties) for k, e in (("E", E), ("A", ann_prev), ("P", y1))}
                ok &= all(v is not None for v in rs.values())
                comp[tb] = rs
        bal = T["balance"][T["balance"]["ts_code"] == code]
        ta = {k: pick(bal, e, d, ties) for k, e in (("E", E), ("P", y1))}
        ok &= all(v is not None for v in ta.values())
        if not ok:
            continue
        res = dict(out, status="OK" if E == newest else "FALLBACK", E=str(E.date()))
        for tb, col in (("income", "n_income"), ("cashflow", "n_cashflow_act")):
            c = comp[tb]
            res[f"{tb}_ttm"] = c["E"][col] if E.month == 12 else c["E"][col] + c["A"][col] - c["P"][col]
            for k, r in c.items():
                res[f"{tb}_{k}_key"] = f"{r['end_s'].date()}|{r['avail_sh_date'].date()}|uf={r['update_flag']}|row={r['row_ord']}"
                res[f"{tb}_{k}_val"] = r[col]
        if E.month != 12:
            c = comp["income"]
            res["n_income_attr_p_ttm"] = c["E"]["n_income_attr_p"] + c["A"]["n_income_attr_p"] - c["P"]["n_income_attr_p"]
        else:
            res["n_income_attr_p_ttm"] = comp["income"]["E"]["n_income_attr_p"]
        res["avg_ta"] = (ta["E"]["total_assets"] + ta["P"]["total_assets"]) / 2
        for k, r in ta.items():
            res[f"balance_{k}_key"] = f"{r['end_s'].date()}|{r['avail_sh_date'].date()}|uf={r['update_flag']}|row={r['row_ord']}"
        res["cfacc"] = (res["income_ttm"] - res["cashflow_ttm"]) / res["avg_ta"] if res["avg_ta"] else float("nan")
        return res
    return {**out, "status": "NaN_no_complete_E_within_caps", "newest_E": str(newest.date())}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    if not str(out.resolve()).startswith(str((ROOT / "output/ai_factory/_leaf25_ttm_recon").resolve())):
        die("--out must be under output/ai_factory/_leaf25_ttm_recon/")
    if out.exists() and any(out.iterdir()):
        die("--out exists and is not empty")
    shas = {}
    for k, (p, pin) in INPUTS.items():
        s = sha256(p)
        shas[k] = s
        if s != pin:
            die(f"sha mismatch {k}: {s} != pinned {pin}")
    stage("sha_ok")
    # phase 1: key columns only, all rows -> deterministic pick
    K = {n: read_keys(n, KEY1) for n in ("income", "cashflow", "balance")}
    stage("phase1_read")
    nonq = {n: int((~df["qend_ok"]).sum()) for n, df in K.items()}
    # (i) correction in exactly one of three tables: per (code,end>=2018,rt1) distinct avail dates; one table >1, others ==1
    nv = {}
    for n, df in K.items():
        g = df[(df["report_type"] == "1") & df["qend_ok"] & (df["end_s"] >= MIN_END) & df["avail_sh_date"].notna()]
        nv[n] = g.groupby(["ts_code", "end_s"])["avail_sh_date"].nunique()
    m = pd.concat(nv, axis=1).dropna()
    one = m[((m > 1).sum(axis=1) == 1)]
    cand_i = sorted(one.index.get_level_values(0).unique())
    # (ii) annual(y-1) and Q1(y) income rows with same original avail date, or Q1 earlier than annual
    inc = K["income"][(K["income"]["report_type"] == "1") & K["income"]["avail_sh_date"].notna() & K["income"]["qend_ok"]]
    first = inc.groupby(["ts_code", "end_s"])["avail_sh_date"].min().reset_index()
    a = first[first["end_s"].dt.strftime("%m%d") == "1231"].assign(y=lambda x: x["end_s"].dt.year + 1)
    q = first[first["end_s"].dt.strftime("%m%d") == "0331"].assign(y=lambda x: x["end_s"].dt.year)
    j = a.merge(q, on=["ts_code", "y"], suffixes=("_a", "_q"))
    j = j[(j["y"] >= 2019) & (j["avail_sh_date_q"] <= j["avail_sh_date_a"])]
    cand_ii = sorted(j["ts_code"].unique())
    n_same_day = int((j["avail_sh_date_q"] == j["avail_sh_date_a"]).sum())
    # (iii) fewer than 4 quarters at some point >= 2019 (first rt1 income period >= 2019-03-31) OR minority share max
    fp = inc.groupby("ts_code")["end_s"].min()
    cand_iii = sorted(fp[fp >= pd.Timestamp("2019-03-31")].index)
    codes, why = [], {}
    for tag, cands in (("i_one_table_correction", cand_i), ("ii_annual_q1_same_day_or_q1_first", cand_ii), ("iii_ipo_lt4q", cand_iii)):
        c = next((x for x in cands if x not in codes), None)
        if c is None:
            die(f"no candidate for rule {tag}")
        codes.append(c)
        why[c] = tag
    del K, inc, first, a, q, j, m, one
    stage("phase1_pick")
    # phase 2: pushdown to 3 codes, all needed columns
    T = {n: read_keys(n, KEY + VAL[n], codes) for n in ("income", "cashflow", "balance")}
    cal = pq.read_table(INPUTS["calendar"][0], columns=["cal_date", "is_open"]).to_pandas()
    cal["d"] = pd.to_datetime(cal["cal_date"].astype(str).str.replace("-", "").str[:8], format="%Y%m%d")
    opens = cal.loc[cal["is_open"].astype(int) == 1, "d"].sort_values().reset_index(drop=True)
    stage("phase2_read")

    def next_open(x: pd.Timestamp) -> pd.Timestamp:
        return opens[opens > x].iloc[0]

    def prev_open(x: pd.Timestamp) -> pd.Timestamp:
        return opens[opens < x].iloc[-1]

    rows, dates = [], {}
    ties: list = []
    for c in codes:
        inc_c = T["income"][(T["income"]["ts_code"] == c) & (T["income"]["report_type"] == "1") & T["income"]["avail_sh_date"].notna()]
        ds = set()
        if why[c].startswith("i_"):
            for n in ("income", "cashflow", "balance"):
                g = T[n][(T[n]["ts_code"] == c) & (T[n]["report_type"] == "1") & (T[n]["end_s"] >= MIN_END) & T[n]["avail_sh_date"].notna()]
                vv = g.groupby("end_s")["avail_sh_date"].agg(["nunique", "min", "max"])
                vv = vv[vv["nunique"] > 1]
                if not vv.empty:
                    corr = vv["max"].iloc[0]
                    ds |= {prev_open(next_open(corr)), next_open(corr)}
                    break
        ann = inc_c[inc_c["end_s"].dt.strftime("%m%d") == "1231"].groupby("end_s")["avail_sh_date"].min()
        ann = ann[ann.index >= MIN_END]
        if not ann.empty:
            ds.add(next_open(ann.iloc[-1]))
            ds.add(prev_open(next_open(ann.iloc[-1])))
        qq = inc_c[inc_c["end_s"].dt.strftime("%m%d").isin({"0630", "0930"})].groupby("end_s")["avail_sh_date"].min()
        qq = qq[qq.index >= MIN_END]
        if not qq.empty:
            ds.add(next_open(qq.iloc[-1]))
        q1 = inc_c[inc_c["end_s"].dt.strftime("%m%d") == "0331"].groupby("end_s")["avail_sh_date"].min()
        q1 = q1[q1.index >= MIN_END]
        if not q1.empty:
            ds.add(next_open(q1.iloc[0]))
        ds = sorted(ds)
        if len(ds) < 4:
            die(f"{c}: only {len(ds)} as-of dates derivable")
        dates[c] = [str(x.date()) for x in ds]
        for d in ds:
            rows.append(ttm_at(c, d, T, ties))
    stage("ttm")
    out.mkdir(parents=True, exist_ok=True)
    raw = pd.concat([T[n] for n in ("income", "cashflow", "balance")], ignore_index=True, sort=False)
    raw.to_csv(out / "raw_rows.csv", index=False)
    pd.DataFrame(rows).to_csv(out / "ttm_script.csv", index=False)
    meta = {
        "script": "research/leaf25_ttm_recon_step_m1.py", "input_sha256": shas, "codes": codes, "pick_rule": why,
        "asof_dates": dates, "n_tie_groups": len(ties), "ties": ties[:200], "nonquarter_end_rows": nonq,
        "n_annual_q1_same_day_all_codes": n_same_day, "n_candidates": {"i": len(cand_i), "ii": len(cand_ii), "iii": len(cand_iii)},
        "rules": __doc__, "peak_rss_kb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, "vmhwm_kb": vmhwm_kb(),
        "finished_et": datetime.now(ZoneInfo("America/New_York")).isoformat(), "rc": 0,
    }
    (out / "run_meta.json").write_text(json.dumps(meta, indent=1, default=str), encoding="utf-8")
    stage("done")
    print(f"peak_check step_m1 rss_kb={meta['peak_rss_kb']} hwm_kb={meta['vmhwm_kb']}", file=sys.stderr, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
