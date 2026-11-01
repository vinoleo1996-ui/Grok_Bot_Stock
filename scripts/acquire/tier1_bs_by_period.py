#!/usr/bin/env python3
"""Pull balancesheet by report period (faster than per-ts_code)."""
import sys, os, time, pathlib, json, warnings
warnings.filterwarnings("ignore")
ROOT = pathlib.Path("/workspace/QuantLab"); sys.path.insert(0, str(ROOT))
import pandas as pd
from quantlab.data_sources.tushare_proxy import datahub, relay, _to_df

RAW = ROOT / "data/v2/tushare_raw" / "balancesheet_by_period"
RAW.mkdir(parents=True, exist_ok=True)
LOG = ROOT / "data/_acquire_logs"
SLEEP = float(os.environ.get("SLEEP", "0.4"))

def call(api, **p):
    last = None
    for fn in (datahub, relay):
        try:
            s, d = fn(api, **p)
            if s == 200 and d.get("code") in (0, None) and "data" in d:
                return _to_df(d)
            last = (s, str(d)[:160])
        except Exception as e:
            last = e
            time.sleep(1.5)
    raise RuntimeError(str(last)[:200])

def pull_period(period):
    f = RAW / f"{period}.parquet"
    if f.exists() and f.stat().st_size > 0:
        return "skip", len(pd.read_parquet(f))
    out, off = [], 0
    while True:
        x = call("balancesheet", period=period, limit=5000, offset=off)
        out.append(x)
        if len(x) < 5000:
            break
        off += 5000
        time.sleep(SLEEP)
    df = pd.concat(out, ignore_index=True) if out else pd.DataFrame()
    tmp = f.with_suffix(".tmp.parquet"); df.to_parquet(tmp, index=False); os.replace(tmp, f)
    time.sleep(SLEEP)
    return "ok", len(df)

# quarterly periods 2010-2026
periods = []
for y in range(2010, 2027):
    for md in ("0331", "0630", "0930", "1231"):
        p = f"{y}{md}"
        if p > "20260930":
            continue
        periods.append(p)
print("periods", len(periods), periods[0], periods[-1], flush=True)
ok = skip = fail = 0
for i, p in enumerate(periods):
    try:
        st, n = pull_period(p)
        if st == "skip": skip += 1
        else: ok += 1
        print(time.strftime("%H:%M:%S"), p, st, n, f"{i+1}/{len(periods)}", flush=True)
    except Exception as e:
        fail += 1
        print("FAIL", p, str(e)[:180], flush=True)
        time.sleep(3)
# also try 000985.CSI for index
print("DONE bs_period ok", ok, "skip", skip, "fail", fail, flush=True)
(LOG/"tier1_bs_period_done.json").write_text(json.dumps({"ok":ok,"skip":skip,"fail":fail,"n":len(periods)}))
