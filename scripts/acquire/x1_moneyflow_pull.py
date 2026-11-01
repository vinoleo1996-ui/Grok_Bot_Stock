"""Pull moneyflow_hsgt 2014-11..2017-12 via relay (datahub 403). Low priority; long backoff."""
from __future__ import annotations
import os, sys, time, pathlib
sys.path.insert(0, "/workspace/QuantLab")
import pandas as pd, requests
from quantlab.data_sources.tushare_proxy import RELAY, _to_df

RAW = pathlib.Path("/workspace/QuantLab/data/v2/tushare_raw/moneyflow_hsgt")
RAW.mkdir(parents=True, exist_ok=True)
RL = os.environ["TSPRO_PROXY_KEY"]
chunks = [
    ("20141117", "20141231", "y2014q4"),
    ("20150101", "20151231", "y2015"),
    ("20160101", "20161231", "y2016"),
    ("20170101", "20171231", "y2017"),
]

def pull(a, b, key):
    f = RAW / f"{key}.parquet"
    if f.exists() and f.stat().st_size > 0:
        print("skip", key, flush=True); return True
    for attempt in range(20):
        try:
            r = requests.get(
                f"{RELAY}/moneyflow_hsgt",
                params={"start_date": a, "end_date": b, "limit": 5000, "offset": 0},
                headers={"X-API-Key": RL},
                timeout=60,
            )
            d = r.json()
            if r.status_code == 200 and d.get("code") in (0, None) and "data" in d:
                df = _to_df(d).replace("", None)
                tmp = f.with_suffix(".tmp.parquet"); df.to_parquet(tmp, index=False); os.replace(tmp, f)
                print(f"OK {key} rows={len(df)} {df.trade_date.min() if len(df) else None}..{df.trade_date.max() if len(df) else None}", flush=True)
                return True
            err = d.get("error") or d.get("msg") or d
            print(f"wait {key} a={attempt} status={r.status_code} {err}", flush=True)
            # minute busy → sleep ~65s
            time.sleep(65 if r.status_code in (429, 503, 504) or "busy" in str(err) or "pool" in str(err) else 10)
        except Exception as e:
            print(f"exc {key} a={attempt} {e}", flush=True); time.sleep(30)
    print("FAIL", key, flush=True); return False

def main():
    print("START x1_moneyflow relay-only", flush=True)
    for a,b,k in chunks:
        pull(a,b,k); time.sleep(5)
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
