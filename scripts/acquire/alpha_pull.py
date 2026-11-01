"""Alpha data requests pulls (research-grade). Usage: python3 alpha_pull.py <job>"""
import sys, pathlib, pandas as pd
src = pathlib.Path(__file__).with_name("tushare_relay_pull.py").read_text().split("\ndef all_codes")[0]
g = {"__file__": str(pathlib.Path(__file__).with_name("tushare_relay_pull.py"))}; exec(src, g)
run, dates, cached, pull, RAW = g["run"], g["dates"], g["cached"], g["pull"], g["RAW"]
job = sys.argv[1]
def months(a="201801", b="202610"):
    m = pd.period_range(pd.Period(a, "M"), pd.Period(b, "M"), freq="M")
    return [(p.start_time.strftime("%Y%m%d"), p.end_time.strftime("%Y%m%d"), p.strftime("%Y%m")) for p in m]
if job == "limit_hist":
    ds = list(reversed(dates("20180101", "20260630")))
    run([(api, d, {"trade_date": d}) for d in ds for api in ["stk_limit", "suspend_d", "daily"]], 4, "limit_hist", preferred="datahub")
elif job == "index_weight":
    run([("index_weight", f"{ix.replace('.','_')}_{k}", {"index_code": ix, "start_date": a, "end_date": b})
         for ix in ["000300.SH", "000905.SH", "000852.SH"] for a, b, k in months()], 3, "idxw", preferred="datahub")
elif job == "share_float":
    run([("share_float", f"ann_{k}", {"start_date": a, "end_date": b}) for a, b, k in months()], 3, "sf", preferred="datahub")
    run([("share_float", f"float_{k}", {"float_date": d}) for d in dates("20180101", "20271231")[:0]], 1, "sf2")
elif job == "toplist":
    ds = list(reversed(dates("20180101", "20261009")))
    run([(api, d, {"trade_date": d}) for d in ds for api in ["top_list", "top_inst"]], 4, "toplist", preferred="datahub")
elif job == "namechange":
    run([("namechange", f"ann_{k}", {"start_date": a, "end_date": b}) for a, b, k in months("200001")], 3, "nc", preferred="relay")
elif job == "share_float_fix":
    import os
    miss=[(a,b,k) for a,b,k in months() if not (RAW/"share_float"/f"ann_{k}.parquet").exists()]
    run([("share_float", f"fday_{d}", {"float_date": d}) for a,b,k in miss for d in pd.date_range(a,b).strftime("%Y%m%d")], 3, "sf_fix", preferred="datahub")
