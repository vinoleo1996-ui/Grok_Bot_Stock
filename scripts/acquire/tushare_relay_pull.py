"""Resumable bulk pull — PCD relay + DataHub (via Mac Clash).
Usage: SOURCE=relay|datahub|auto python3 tushare_relay_pull.py <job>
Jobs: cal|ref|sw|extend|daily_basic_hist|fin|dividend|dividend_by_exdate|disclosure_dates|materialize|extend_panels
"""
import sys, os, time, warnings, pathlib, concurrent.futures as cf
warnings.filterwarnings("ignore")
ROOT = pathlib.Path("/workspace/QuantLab"); sys.path.insert(0, str(ROOT))
import pandas as pd, numpy as np
from quantlab.data_sources.tushare_proxy import relay, datahub, _to_df
RAW = ROOT / "data/v2/tushare_raw"
LOG = ROOT / "data/_acquire_logs"; LOG.mkdir(parents=True, exist_ok=True)
SOURCE = os.environ.get("SOURCE", "auto")  # auto: try preferred then fallback

def _call(api, preferred, **p):
    order = []
    if preferred == "datahub":
        order = [("datahub", datahub), ("relay", relay)]
    elif preferred == "relay":
        order = [("relay", relay), ("datahub", datahub)]
    else:
        # SOURCE override
        s = SOURCE
        if s == "datahub": order = [("datahub", datahub)]
        elif s == "relay": order = [("relay", relay)]
        else: order = [("relay", relay), ("datahub", datahub)]
    last = None
    for name, fn in order:
        try:
            s, d = fn(api, **p)
            if s == 200 and d.get("code") in (0, None) and "data" in d:
                return s, d, name
            last = (name, s, d)
        except Exception as e:
            last = (name, e)
    raise RuntimeError(f"{api} all sources failed: {str(last)[:220]}")

def pull(api, preferred="relay", **p):
    out, off = [], 0
    base = {k: v for k, v in p.items() if k != "limit"}
    lim = int(p.get("limit") or 5000)
    src_used = None
    while True:
        for a in range(8):
            try:
                s, d, src_used = _call(api, preferred, limit=lim, offset=off, **base)
                break
            except Exception as e:
                err = e
                time.sleep(2 * (a + 1))
        else:
            raise RuntimeError(f"{api} {base} exhausted: {err}")
        x = _to_df(d); out.append(x)
        if len(x) < lim: break
        off += lim; time.sleep(0.15)
    if not out: return pd.DataFrame()
    df = pd.concat(out, ignore_index=True)
    df.attrs["source"] = src_used
    return df

def cached(api, key, preferred="relay", **p):
    f = RAW / api / f"{key}.parquet"
    if f.exists() and f.stat().st_size > 0: return "skip"
    f.parent.mkdir(parents=True, exist_ok=True)
    x = pull(api, preferred=preferred, **p)
    x = x.replace("", None)
    for c in x.columns:
        if x[c].dtype == object and c not in ("ts_code","trade_date","ann_date","f_ann_date","end_date","ex_date"):
            n = pd.to_numeric(x[c], errors="coerce")
            if n.notna().sum() >= x[c].notna().sum(): x[c] = n
    tmp = f.with_suffix(".tmp.parquet")
    x.to_parquet(tmp, index=False); os.replace(tmp, f)
    return f"ok:{len(x)}"

def dates(a, b):
    f = RAW / "trade_cal.parquet"
    if not f.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        pull("trade_cal", preferred="relay", exchange="SSE", start_date="20000101", end_date="20261231").to_parquet(f)
    c = pd.read_parquet(f); c = c[c.is_open.astype(int) == 1]
    return sorted(d for d in c.cal_date.astype(str) if a <= d <= b)

def run(tasks, workers=4, label="", preferred="relay"):
    # tasks: (api, key, params_dict)
    done = fail = 0; n = len(tasks)
    print(f"START {label} n={n} workers={workers} preferred={preferred} SOURCE={SOURCE}", flush=True)
    W=int(os.environ.get("WORKERS",workers)); SPLIT=os.environ.get("SPLIT")=="1"
    idx={t[1]+t[0]:i for i,t in enumerate(tasks)}
    def one(t):
        api, key, p = t
        pref = (("datahub","relay")[idx[key+api]%2]) if SPLIT else preferred
        return cached(api, key, preferred=pref, **p)
    with cf.ThreadPoolExecutor(W) as ex:
        futs = {ex.submit(one, t): t for t in tasks}
        for fu in cf.as_completed(futs):
            done += 1
            try: fu.result()
            except Exception as e:
                fail += 1
                print("FAIL", futs[fu][0], futs[fu][1], str(e)[:160], flush=True)
            if done % 25 == 0 or done == n:
                print(time.strftime("%H:%M:%S"), label, done, "/", n, "fail", fail, flush=True)
    print("DONE", label, "fail", fail, flush=True)

def all_codes():
    parts = []
    for st in "LDP":
        f = RAW / "stock_basic" / f"{st}.parquet"
        if f.exists(): parts.append(pd.read_parquet(f))
    if not parts: raise RuntimeError("stock_basic missing")
    return sorted(set(pd.concat(parts).ts_code.tolist()))

def to_iid(s):
    return s.str.replace(r"(\d+)\.(SH|SZ|BJ)", lambda m: ("sh." if m.group(2)=="SH" else "sz." if m.group(2)=="SZ" else "bj.") + m.group(1), regex=True)

job = sys.argv[1] if len(sys.argv) > 1 else "help"

if job == "cal":
    RAW.mkdir(parents=True, exist_ok=True)
    pull("trade_cal", preferred="relay", exchange="SSE", start_date="20000101", end_date="20261231").to_parquet(RAW/"trade_cal.parquet")
    print("cal", len(pd.read_parquet(RAW/"trade_cal.parquet")))

elif job == "ref":
    for st in "LDP":
        print("stock_basic", st, cached("stock_basic", st, preferred="relay", list_status=st), flush=True)
    # namechange: DataHub unknown; relay may estimate too large — skip for now (ST from namechange deferred)
    print("namechange SKIP (datahub unknown / relay size)", flush=True)
    print("fund_daily", cached("fund_daily", "510300.SH", preferred="relay", ts_code="510300.SH"), flush=True)
    for lv in ["L1","L2","L3"]:
        print("classify", lv, cached("index_classify", f"SW2021_{lv}", preferred="relay", level=lv, src="SW2021"), flush=True)

elif job == "sw":
    cls_f = RAW / "index_classify/SW2021_L1.parquet"
    if not cls_f.exists():
        cached("index_classify", "SW2021_L1", preferred="relay", level="L1", src="SW2021")
    cls = pd.read_parquet(cls_f)
    tasks = []
    for c in cls.index_code:
        for n in ("Y", "N"):
            tasks.append(("index_member", f"{c}_{n}", {"index_code": c, "is_new": n}))
    tasks.append(("index_member_all", "current_Y", {"is_new": "Y"}))
    run(tasks, 3, "sw", preferred="relay")

elif job == "sw_all":
    # DataHub-preferred: index_member_all with l1_code like 801010.SI (NOT 110000)
    cls_f = RAW / "index_classify/SW2021_L1.parquet"
    if not cls_f.exists():
        cached("index_classify", "SW2021_L1", preferred="datahub", level="L1", src="SW2021")
    cls = pd.read_parquet(cls_f)
    tasks = [("index_member_all", f"{c}_Y", {"l1_code": c, "is_new": "Y"}) for c in cls.index_code]
    # historical: is_new=N may 504 on some gateways — try per l1 anyway
    tasks += [("index_member_all", f"{c}_N", {"l1_code": c, "is_new": "N"}) for c in cls.index_code]
    run(tasks, 3, "sw_all", preferred="datahub")

elif job == "extend":
    ds = dates("20260701", "20261009")
    # Prefer datahub for daily panels (Leo RDS fast); fallback relay
    run([(api, d, {"trade_date": d}) for d in ds for api in
         ["daily", "daily_basic", "adj_factor", "stk_limit", "suspend_d"]],
        4, "extend", preferred="datahub")

elif job == "daily_basic_hist":
    run([("daily_basic", d, {"trade_date": d}) for d in reversed(dates("20180101", "20260630"))],
        4, "db_hist", preferred="datahub")

elif job == "fin":
    codes = all_codes()
    run([(api, c.replace(".","_"), {"ts_code": c}) for c in codes for api in ["income", "fina_indicator"]],
        3, "fin", preferred="datahub")

elif job == "dividend":
    codes = all_codes()
    run([("dividend", c.replace(".","_"), {"ts_code": c}) for c in codes],
        3, "div", preferred="datahub")

elif job == "materialize":
    out_m = ROOT/"data/v2/float_mktcap"; out_m.mkdir(parents=True, exist_ok=True)
    rows = []
    for f in sorted((RAW/"daily_basic").glob("*.parquet")):
        x = pd.read_parquet(f)
        if x.empty or "circ_mv" not in x.columns: continue
        y = pd.DataFrame({
            "instrument_id": to_iid(x.ts_code.astype(str)),
            "trade_date": pd.to_datetime(x.trade_date.astype(str)),
            "float_mktcap": pd.to_numeric(x.circ_mv, errors="coerce") * 10000.0,
            "total_mv": pd.to_numeric(x["total_mv"], errors="coerce") * 10000.0 if "total_mv" in x.columns else np.nan,
            "turnover_rate": pd.to_numeric(x["turnover_rate"], errors="coerce") if "turnover_rate" in x.columns else np.nan,
            "source": "tushare_leo",
            "schema": "quantlab.v2.float_mktcap.v1",
            "quality_status": "research",
            "promotion_approved": False,
        })
        rows.append(y)
    if rows:
        m = pd.concat(rows, ignore_index=True).dropna(subset=["float_mktcap"])
        dest = out_m/"float_mktcap_daily_tushare.parquet"
        m.to_parquet(dest, index=False)
        print("float_mktcap", len(m), str(m.trade_date.min())[:10], str(m.trade_date.max())[:10], "inst", m.instrument_id.nunique())

    sw_rows = []
    cls_f = RAW/"index_classify/SW2021_L1.parquet"
    # Prefer index_member_all (datahub) then fall back to index_member
    if cls_f.exists() and ((RAW/"index_member_all").exists() or (RAW/"index_member").exists()):
        cls = pd.read_parquet(cls_f)
        name_map = dict(zip(cls.index_code, cls.industry_name))
        src_dir = RAW/"index_member_all" if (RAW/"index_member_all").exists() and any((RAW/"index_member_all").glob("*.parquet")) else RAW/"index_member"
        for f in sorted(src_dir.glob("*.parquet")):
            x = pd.read_parquet(f)
            if x.empty: continue
            x = x.copy()
            code_col = "l1_code" if "l1_code" in x.columns else "index_code"
            con_col = "ts_code" if "ts_code" in x.columns else "con_code"
            x["sw_code"] = x[code_col]
            x["sw_name"] = x[code_col].map(name_map)
            if "l1_name" in x.columns:
                x["sw_name"] = x["sw_name"].fillna(x["l1_name"])
            x["instrument_id"] = to_iid(x[con_col].astype(str))
            x["in_date"] = pd.to_datetime(x.in_date.astype(str), errors="coerce")
            x["out_date"] = pd.to_datetime(x.out_date.astype(str), errors="coerce")
            x["available_at"] = x.in_date + pd.Timedelta(hours=18)
            x["source"] = "tushare_leo.index_member"
            x["revision"] = 1
            x["quality_status"] = "research_tushare_candidate"
            x["schema"] = "quantlab.v2.industry_members_sw_l1.v1"
            sw_rows.append(x[["instrument_id","sw_code","sw_name","in_date","out_date","available_at","source","revision","quality_status","schema","is_new"]])
        if sw_rows:
            sw = pd.concat(sw_rows, ignore_index=True).drop_duplicates(["instrument_id","sw_code","in_date","out_date"])
            dest = ROOT/"data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet"
            dest.parent.mkdir(parents=True, exist_ok=True)
            sw.to_parquet(dest, index=False)
            print("sw_l1", len(sw), "L1", sw.sw_code.nunique(), "inst", sw.instrument_id.nunique())

    f = RAW/"fund_daily"/"510300.SH.parquet"
    if f.exists():
        x = pd.read_parquet(f)
        dest = ROOT/"data/v2/etf_510300/fund_daily_tushare_510300.parquet"
        dest.parent.mkdir(parents=True, exist_ok=True)
        x.to_parquet(dest, index=False)
        print("510300", len(x), x.trade_date.min() if len(x) else None, x.trade_date.max() if len(x) else None)

    # financials available_at from income
    fin_dir = RAW/"income"
    if fin_dir.exists():
        parts = []
        for f in fin_dir.glob("*.parquet"):
            x = pd.read_parquet(f)
            if x.empty: continue
            parts.append(x)
        if parts:
            inc = pd.concat(parts, ignore_index=True)
            # available_at from f_ann_date fallback ann_date @ 18:00
            ad = pd.to_datetime(inc.get("f_ann_date", inc["ann_date"]).astype(str), errors="coerce")
            ad = ad.fillna(pd.to_datetime(inc["ann_date"].astype(str), errors="coerce"))
            out = pd.DataFrame({
                "instrument_id": to_iid(inc.ts_code.astype(str)),
                "end_date": pd.to_datetime(inc.end_date.astype(str), errors="coerce"),
                "ann_date": pd.to_datetime(inc.ann_date.astype(str), errors="coerce"),
                "f_ann_date": pd.to_datetime(inc["f_ann_date"].astype(str), errors="coerce") if "f_ann_date" in inc.columns else pd.NaT,
                "report_type": inc.get("report_type"),
                "update_flag": inc.get("update_flag"),
                "available_at": ad + pd.Timedelta(hours=18),
                "source": "tushare_leo.income",
                "quality_status": "research",
                "promotion_approved": False,
                "schema": "quantlab.v2.financials_available_at.v1",
            })
            dest = ROOT/"data/v2/financials_pit/financials_available_at_tushare.parquet"
            dest.parent.mkdir(parents=True, exist_ok=True)
            out.to_parquet(dest, index=False)
            print("fina_at", len(out), "null_at", out.available_at.isna().sum())

    # dividend ledger
    div_dir = RAW/"dividend"
    if div_dir.exists():
        parts = [pd.read_parquet(f) for f in div_dir.glob("*.parquet") if f.stat().st_size > 0]
        if parts:
            d = pd.concat(parts, ignore_index=True)
            dest = ROOT/"data/v2/corporate_actions/dividend_tushare.parquet"
            dest.parent.mkdir(parents=True, exist_ok=True)
            d.to_parquet(dest, index=False)
            print("dividend", len(d), "codes", d.ts_code.nunique() if len(d) else 0)

    # dividend by ex_date fast path
    dex = RAW/"dividend_by_exdate"
    if dex.exists():
        parts = [pd.read_parquet(f) for f in dex.glob("*.parquet") if f.stat().st_size > 0]
        if parts:
            d = pd.concat(parts, ignore_index=True).drop_duplicates()
            dest = ROOT/"data/v2/corporate_actions/dividend_by_exdate_tushare.parquet"
            dest.parent.mkdir(parents=True, exist_ok=True)
            d.to_parquet(dest, index=False)
            print("dividend_ex", len(d), "codes", d.ts_code.nunique() if len(d) else 0)


elif job == "extend_panels":
    # Build asof_extend_tushare panels (separate from enrich curl dir)
    out = ROOT/"data/v2/asof_extend_tushare_202610/panels"; out.mkdir(parents=True, exist_ok=True)
    days = sorted(f.stem for f in (RAW/"daily").glob("*.parquet"))
    if not days:
        print("no daily raw"); sys.exit(0)
    # load all days into maps
    def load_api(api):
        frames = []
        for d in days:
            f = RAW/api/f"{d}.parquet"
            if f.exists(): frames.append(pd.read_parquet(f))
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    daily = load_api("daily"); print("daily rows", len(daily))
    basic = load_api("daily_basic")
    lim = load_api("stk_limit")
    sus = load_api("suspend_d")
    adj = load_api("adj_factor")
    # namechange ST flags — optional
    daily["instrument_id"] = to_iid(daily.ts_code.astype(str))
    if len(basic):
        basic["instrument_id"] = to_iid(basic.ts_code.astype(str))
        basic = basic.rename(columns={"turnover_rate":"turnover"})
    if len(lim):
        lim["instrument_id"] = to_iid(lim.ts_code.astype(str))
    if len(sus):
        sus["instrument_id"] = to_iid(sus.ts_code.astype(str))
        sus["is_suspend"] = 1
    if len(adj):
        adj["instrument_id"] = to_iid(adj.ts_code.astype(str))
    # merge per instrument
    for iid, g in daily.groupby("instrument_id"):
        g = g.copy()
        g["trade_date"] = pd.to_datetime(g.trade_date.astype(str))
        g = g.sort_values("trade_date")
        # amount in tushare daily is 千元 → CNY *1000
        g["amount"] = pd.to_numeric(g["amount"], errors="coerce") * 1000.0
        g["volume"] = pd.to_numeric(g["vol"], errors="coerce") * 100.0  # 手→股
        for col in ["open","high","low","close","pre_close"]:
            g[col] = pd.to_numeric(g[col], errors="coerce")
        if len(basic):
            b = basic[basic.instrument_id==iid][["trade_date","turnover","circ_mv"]].copy() if "turnover" in basic.columns else pd.DataFrame()
            if len(b):
                b["trade_date"] = pd.to_datetime(b.trade_date.astype(str))
                g = g.merge(b, on="trade_date", how="left")
        else:
            g["turnover"] = np.nan
        if len(lim):
            L = lim[lim.instrument_id==iid][["trade_date","up_limit","down_limit"]].copy()
            if len(L):
                L["trade_date"] = pd.to_datetime(L.trade_date.astype(str))
                L = L.rename(columns={"up_limit":"limit_up","down_limit":"limit_down"})
                g = g.merge(L, on="trade_date", how="left")
        else:
            g["limit_up"] = np.nan; g["limit_down"] = np.nan
        g["tradestatus"] = 1
        if len(sus):
            S = sus[sus.instrument_id==iid][["trade_date","is_suspend"]].copy()
            if len(S):
                S["trade_date"] = pd.to_datetime(S.trade_date.astype(str))
                g = g.merge(S, on="trade_date", how="left")
                g.loc[g.is_suspend==1, "tradestatus"] = 0
        g["available_at"] = g.trade_date + pd.Timedelta(hours=16)
        g["quality_status"] = "research_tushare"
        g["is_st_at_open"] = False  # filled later from namechange if needed
        g["source"] = "tushare_leo"
        cols = ["trade_date","open","high","low","close","volume","amount","turnover","limit_up","limit_down",
                "tradestatus","available_at","quality_status","is_st_at_open","source"]
        for c in cols:
            if c not in g.columns: g[c] = np.nan
        dest = out / f"{iid}.parquet"
        g[cols].to_parquet(dest, index=False)
    print("panels written", len(list(out.glob('*.parquet'))), "days", len(days))


elif job == "dividend_by_exdate":
    # Fast CA ledger for 2024+ via ex_date (no conflict with per-code dividend/ writers)
    out = RAW / "dividend_by_exdate"; out.mkdir(parents=True, exist_ok=True)
    # calendar days with possible ex-dates: use trade cal + weekends buffer via all dates
    import datetime as dt
    start = dt.date(2024,1,1); end = dt.date(2026,10,9)
    days = []
    cur = start
    while cur <= end:
        days.append(cur.strftime("%Y%m%d")); cur += dt.timedelta(days=1)
    tasks = [("dividend", f"ex_{d}", {"ex_date": d}) for d in days]
    # write under dividend_by_exdate via custom cache path
    def cached_ex(api, key, preferred="datahub", **p):
        f = out / f"{key}.parquet"
        if f.exists() and f.stat().st_size > 0: return "skip"
        x = pull(api, preferred=preferred, **p)
        tmp = f.with_suffix(".tmp.parquet")
        x.to_parquet(tmp, index=False); os.replace(tmp, f)
        return f"ok:{len(x)}"
    done = fail = 0; n = len(tasks)
    print(f"START div_ex n={n}", flush=True)
    def one(t):
        api, key, p = t
        return cached_ex(api, key, preferred="datahub", **p)
    with cf.ThreadPoolExecutor(6) as ex:
        futs = {ex.submit(one, t): t for t in tasks}
        for fu in cf.as_completed(futs):
            done += 1
            try: fu.result()
            except Exception as e:
                fail += 1
                print("FAIL", futs[fu][1], str(e)[:160], flush=True)
            if done % 50 == 0 or done == n:
                print(time.strftime("%H:%M:%S"), "div_ex", done, "/", n, "fail", fail, flush=True)
    print("DONE div_ex fail", fail, flush=True)

elif job == "disclosure_dates":
    # report periods 2018-2026 quarterly
    periods = []
    for y in range(2018, 2027):
        for md in ("0331","0630","0930","1231"):
            if f"{y}{md}" > "20261009": continue
            periods.append(f"{y}{md}")
    run([("disclosure_date", f"end_{p}", {"end_date": p}) for p in periods], 3, "disclosure", preferred="datahub")

else:
    print("jobs: cal ref sw extend daily_basic_hist fin dividend materialize extend_panels dividend_by_exdate disclosure_dates")
