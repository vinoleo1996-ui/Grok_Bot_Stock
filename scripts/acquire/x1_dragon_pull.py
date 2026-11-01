"""Pull top_list/top_inst for 2015-01..2017-12 via datahub only. Research-grade."""
from __future__ import annotations
import os, sys, time, pathlib, concurrent.futures as cf
sys.path.insert(0, "/workspace/QuantLab")
import pandas as pd
import requests
from quantlab.data_sources.tushare_proxy import DATAHUB_HTTPS, _to_df

ROOT = pathlib.Path("/workspace/QuantLab")
RAW = ROOT / "data/v2/tushare_raw"
DH = os.environ["DATAHUB_API_KEY"]

def dates(a="20150101", b="20171231"):
    c = pd.read_parquet(RAW / "trade_cal.parquet")
    c = c[c.is_open.astype(int) == 1]
    return sorted(d for d in c.cal_date.astype(str) if a <= d <= b)

def pull_one(api: str, d: str) -> str:
    f = RAW / api / f"{d}.parquet"
    if f.exists() and f.stat().st_size > 0:
        return "skip"
    f.parent.mkdir(parents=True, exist_ok=True)
    last = None
    for a in range(6):
        try:
            r = requests.get(
                f"{DATAHUB_HTTPS}/{api}",
                params={"trade_date": d, "limit": 5000, "offset": 0},
                headers={"X-API-Key": DH},
                timeout=30,
            )
            djson = r.json()
            if r.status_code == 200 and djson.get("code") in (0, None) and "data" in djson:
                df = _to_df(djson).replace("", None)
                page_len = len(df)
                off = 5000
                while page_len >= 5000 and off <= 20000:
                    r2 = requests.get(
                        f"{DATAHUB_HTTPS}/{api}",
                        params={"trade_date": d, "limit": 5000, "offset": off},
                        headers={"X-API-Key": DH},
                        timeout=30,
                    )
                    d2 = r2.json()
                    x = _to_df(d2)
                    if len(x) == 0:
                        break
                    df = pd.concat([df, x], ignore_index=True)
                    page_len = len(x)
                    if page_len < 5000:
                        break
                    off += 5000
                    time.sleep(0.12)
                tmp = f.with_suffix(".tmp.parquet")
                df.to_parquet(tmp, index=False)
                os.replace(tmp, f)
                return f"ok:{len(df)}"
            if r.status_code in (429, 503, 504):
                time.sleep(min(60, 4 * (2 ** a)))
                last = (r.status_code, str(djson)[:80])
                continue
            if r.status_code == 200:
                df = _to_df(djson) if isinstance(djson, dict) and "data" in djson else pd.DataFrame()
                tmp = f.with_suffix(".tmp.parquet")
                df.to_parquet(tmp, index=False)
                os.replace(tmp, f)
                return f"empty:{len(df)}"
            last = (r.status_code, str(djson)[:120])
            time.sleep(2)
        except Exception as e:
            last = e
            time.sleep(min(30, 3 * (a + 1)))
    return f"FAIL:{last}"

def main():
    ds = dates()
    tasks = [(api, d) for d in ds for api in ("top_list", "top_inst")]
    print(f"START x1_dragon n={len(tasks)} days={len(ds)} workers=2", flush=True)
    done = fail = 0
    n = len(tasks)
    r = ""
    with cf.ThreadPoolExecutor(2) as ex:
        futs = {ex.submit(pull_one, api, d): (api, d) for api, d in tasks}
        for fu in cf.as_completed(futs):
            done += 1
            api, d = futs[fu]
            try:
                r = fu.result()
                if isinstance(r, str) and r.startswith("FAIL"):
                    fail += 1
                    print("FAIL", api, d, r[:160], flush=True)
            except Exception as e:
                fail += 1
                r = f"EXC:{e}"
                print("EXC", api, d, e, flush=True)
            if done % 50 == 0 or done == n:
                print(f"PROG {done}/{n} fail={fail} last={api}:{d}:{r}", flush=True)
    print(f"DONE fail={fail}", flush=True)

if __name__ == "__main__":
    main()
