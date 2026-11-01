#!/usr/bin/env python3
"""Tier-1 urgent pulls: daily extend to latest, daily_basic 2014+, index_daily, stock_basic, balancesheet.
SOURCE=auto preferred datahub. Rate-limited. Resumable via cached day files.
"""
import sys, os, time, pathlib, json, warnings
warnings.filterwarnings("ignore")
ROOT = pathlib.Path("/workspace/QuantLab"); sys.path.insert(0, str(ROOT))
import pandas as pd, numpy as np
from quantlab.data_sources.tushare_proxy import relay, datahub, _to_df

RAW = ROOT / "data/v2/tushare_raw"
LOG = ROOT / "data/_acquire_logs"; LOG.mkdir(parents=True, exist_ok=True)
PROG = LOG / "tier1_progress.json"
SOURCE = os.environ.get("SOURCE", "auto")
SLEEP = float(os.environ.get("SLEEP", "0.25"))

def _call(api, preferred="datahub", **p):
    order = [("datahub", datahub), ("relay", relay)] if preferred == "datahub" else [("relay", relay), ("datahub", datahub)]
    if SOURCE == "datahub": order = [("datahub", datahub)]
    elif SOURCE == "relay": order = [("relay", relay)]
    last = None
    for name, fn in order:
        try:
            s, d = fn(api, **p)
            if s == 200 and d.get("code") in (0, None) and "data" in d:
                return s, d, name
            last = (name, s, str(d)[:180])
        except Exception as e:
            last = (name, e)
            time.sleep(1.5)
    raise RuntimeError(f"{api} failed: {last}")

def pull(api, preferred="datahub", **p):
    out, off = [], 0
    lim = int(p.pop("limit", 5000) or 5000)
    base = dict(p); src = None
    while True:
        for a in range(8):
            try:
                s, d, src = _call(api, preferred=preferred, limit=lim, offset=off, **base)
                break
            except Exception as e:
                err = e; time.sleep(2 * (a + 1))
        else:
            raise RuntimeError(f"{api} exhausted: {err}")
        x = _to_df(d); out.append(x)
        if len(x) < lim: break
        off += lim; time.sleep(SLEEP)
    df = pd.concat(out, ignore_index=True) if out else pd.DataFrame()
    df.attrs["source"] = src
    return df

def dates(a, b):
    f = RAW / "trade_cal.parquet"
    c = pd.read_parquet(f); c = c[c.is_open.astype(int) == 1]
    return sorted(d for d in c.cal_date.astype(str) if a <= d <= b)

def save(api, key, df):
    f = RAW / api / f"{key}.parquet"; f.parent.mkdir(parents=True, exist_ok=True)
    df = df.replace("", None)
    tmp = f.with_suffix(".tmp.parquet"); df.to_parquet(tmp, index=False); os.replace(tmp, f)
    return len(df)

def cached_day(api, d, preferred="datahub", **extra):
    f = RAW / api / f"{d}.parquet"
    if f.exists() and f.stat().st_size > 0:
        return "skip", 0
    x = pull(api, preferred=preferred, trade_date=d, **extra)
    n = save(api, d, x); time.sleep(SLEEP)
    return "ok", n

def progress(upd):
    cur = {}
    if PROG.exists():
        try: cur = json.loads(PROG.read_text())
        except Exception: cur = {}
    cur.update(upd); cur["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    PROG.write_text(json.dumps(cur, indent=2, ensure_ascii=False, default=str))

def job_extend_latest(end=None):
    """Pull daily suite for open days after last raw daily through end (default today CN)."""
    end = end or time.strftime("%Y%m%d")
    # refresh cal lightly (TIER1_SKIP_CAL_REFRESH=1 -> leave pinned trade_cal untouched)
    if os.environ.get("TIER1_SKIP_CAL_REFRESH") == "1":
        print("cal refresh skipped (TIER1_SKIP_CAL_REFRESH=1)", flush=True)
    else:
        try:
            cal = pull("trade_cal", preferred="datahub", exchange="SSE", start_date="20260901", end_date="20261231")
            if len(cal):
                old = pd.read_parquet(RAW/"trade_cal.parquet")
                # merge replace overlapping
                old["cal_date"] = old.cal_date.astype(str)
                cal["cal_date"] = cal.cal_date.astype(str)
                keep = old[~old.cal_date.isin(set(cal.cal_date))]
                _f = RAW/"trade_cal.parquet"; _tmp = _f.with_name(_f.name + f".tmp.{os.getpid()}")
                pd.concat([keep, cal], ignore_index=True).to_parquet(_tmp, index=False)
                with open(_tmp, "rb") as _h: os.fsync(_h.fileno())
                os.replace(_tmp, _f)  # atomic: never leaves a truncated trade_cal
                print("cal refreshed", flush=True)
        except Exception as e:
            print("cal refresh skip", e, flush=True)
    existing = sorted(p.stem for p in (RAW/"daily").glob("*.parquet"))
    start = "20260923"
    if existing:
        # continue from day after last OR ensure from 20260923
        start = min(start, existing[-1])
    ds = [d for d in dates(start, end)]
    apis = ["daily", "daily_basic", "adj_factor", "stk_limit", "suspend_d"]
    print(f"EXTEND days={ds} apis={apis}", flush=True)
    stats = {}
    for d in ds:
        for api in apis:
            st, n = cached_day(api, d, preferred="datahub")
            stats[f"{api}:{d}"] = f"{st}:{n}"
            print(time.strftime("%H:%M:%S"), api, d, st, n, flush=True)
    progress({"daily_extend": {"days": ds, "stats": stats, "end": end}})
    return ds

def job_daily_basic_2014():
    ds = dates("20140101", "20141231")
    print(f"DB2014 n={len(ds)}", flush=True)
    ok = skip = fail = 0
    for i, d in enumerate(ds):
        try:
            st, n = cached_day("daily_basic", d, preferred="datahub")
            if st == "skip": skip += 1
            else: ok += 1
            if (i+1) % 20 == 0 or st == "ok":
                print(time.strftime("%H:%M:%S"), "db2014", d, st, n, f"{i+1}/{len(ds)}", flush=True)
        except Exception as e:
            fail += 1
            print("FAIL db2014", d, str(e)[:160], flush=True)
            time.sleep(3)
    progress({"daily_basic_2014": {"ok": ok, "skip": skip, "fail": fail, "n_days": len(ds)}})

def job_index_daily():
    # 中证2000 on tushare often 932000.CSI; also try CNI / alternate
    codes = ["000300.SH", "000905.SH", "000852.SH", "000985.SH", "932000.CSI", "000922.CSI"]
    outdir = RAW / "index_daily"; outdir.mkdir(parents=True, exist_ok=True)
    results = {}
    for code in codes:
        f = outdir / f"{code.replace('.','_')}.parquet"
        try:
            x = pull("index_daily", preferred="datahub", ts_code=code, start_date="20140101", end_date="20261231")
            if x.empty:
                # try without CSI suffix variants
                print("empty", code, flush=True)
                results[code] = {"rows": 0}
                continue
            save("index_daily", code.replace(".","_"), x)
            results[code] = {"rows": len(x), "min": str(x.trade_date.min()), "max": str(x.trade_date.max())}
            print("index", code, len(x), x.trade_date.min(), x.trade_date.max(), flush=True)
            time.sleep(SLEEP)
        except Exception as e:
            results[code] = {"error": str(e)[:200]}
            print("FAIL index", code, e, flush=True)
    progress({"index_daily": results})

def job_stock_basic():
    parts = []
    for st in ("L", "D", "P"):
        try:
            x = pull("stock_basic", preferred="datahub", list_status=st,
                     fields="ts_code,symbol,name,area,industry,fullname,enname,cnspell,market,exchange,curr_type,list_status,list_date,delist_date,is_hs")
            save("stock_basic", st, x)
            print("stock_basic", st, len(x), flush=True)
            parts.append(x)
            time.sleep(SLEEP)
        except Exception as e:
            print("FAIL stock_basic", st, e, flush=True)
            f = RAW/"stock_basic"/f"{st}.parquet"
            if f.exists(): parts.append(pd.read_parquet(f))
    progress({"stock_basic": {"parts": len(parts)}})

def job_balancesheet():
    # codes from stock_basic L+D
    codes = []
    for st in ("L", "D"):
        f = RAW/"stock_basic"/f"{st}.parquet"
        if f.exists():
            codes += pd.read_parquet(f).ts_code.astype(str).tolist()
    codes = sorted(set(codes))
    print("balancesheet codes", len(codes), flush=True)
    ok = skip = fail = 0
    fields = "ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,update_flag,total_assets,total_liab,total_hldr_eqy_exc_min_int,total_hldr_eqy_inc_min_int,n_cashflow_act"
    # balancesheet doesn't have n_cashflow_act - that's cashflow. Keep BS fields only.
    fields = "ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,update_flag,total_assets,total_liab,total_hldr_eqy_exc_min_int,total_hldr_eqy_inc_min_int"
    for i, c in enumerate(codes):
        key = c.replace(".", "_")
        f = RAW/"balancesheet"/f"{key}.parquet"
        if f.exists() and f.stat().st_size > 0:
            skip += 1
            continue
        try:
            x = pull("balancesheet", preferred="datahub", ts_code=c, fields=fields)
            save("balancesheet", key, x); ok += 1
            if (ok + skip) % 50 == 0:
                print(time.strftime("%H:%M:%S"), "bs", c, len(x), f"{i+1}/{len(codes)} ok={ok} skip={skip} fail={fail}", flush=True)
            time.sleep(SLEEP)
            if ok % 100 == 0:
                progress({"balancesheet": {"ok": ok, "skip": skip, "fail": fail, "done": i+1, "total": len(codes)}})
        except Exception as e:
            fail += 1
            if fail <= 20 or fail % 50 == 0:
                print("FAIL bs", c, str(e)[:160], flush=True)
            time.sleep(2)
    progress({"balancesheet": {"ok": ok, "skip": skip, "fail": fail, "total": len(codes)}})

def job_cashflow_fill():
    """Fill any missing cashflow codes (already mostly present)."""
    codes = []
    for st in ("L", "D"):
        f = RAW/"stock_basic"/f"{st}.parquet"
        if f.exists():
            codes += pd.read_parquet(f).ts_code.astype(str).tolist()
    codes = sorted(set(codes))
    fields = "ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,update_flag,n_cashflow_act,net_profit,im_n_cashflow_act"
    ok = skip = fail = 0
    for i, c in enumerate(codes):
        key = c.replace(".", "_")
        f = RAW/"cashflow"/f"{key}.parquet"
        if f.exists() and f.stat().st_size > 0:
            skip += 1
            continue
        try:
            x = pull("cashflow", preferred="datahub", ts_code=c)
            save("cashflow", key, x); ok += 1
            if ok % 25 == 0:
                print(time.strftime("%H:%M:%S"), "cf fill", c, len(x), f"ok={ok} skip={skip}", flush=True)
            time.sleep(SLEEP)
        except Exception as e:
            fail += 1
            print("FAIL cf", c, str(e)[:120], flush=True)
            time.sleep(2)
    progress({"cashflow_fill": {"ok": ok, "skip": skip, "fail": fail}})

if __name__ == "__main__":
    job = sys.argv[1] if len(sys.argv) > 1 else "help"
    if job == "extend":
        job_extend_latest(sys.argv[2] if len(sys.argv)>2 else None)
    elif job == "db2014":
        job_daily_basic_2014()
    elif job == "index":
        job_index_daily()
    elif job == "stock_basic":
        job_stock_basic()
    elif job == "balancesheet":
        job_balancesheet()
    elif job == "cashflow_fill":
        job_cashflow_fill()
    else:
        print("jobs: extend|db2014|index|stock_basic|balancesheet|cashflow_fill")
