#!/usr/bin/env python3
"""Sharded balancesheet pull; shard_id/num_shards. Relay-only, short timeout, skip existing."""
import sys, os, time, pathlib, json, warnings
warnings.filterwarnings("ignore")
ROOT = pathlib.Path("/workspace/QuantLab"); sys.path.insert(0, str(ROOT))
import pandas as pd, requests
from quantlab.data_sources import tushare_proxy as tp

RAW = ROOT / "data/v2/tushare_raw"
LOG = ROOT / "data/_acquire_logs"; LOG.mkdir(parents=True, exist_ok=True)
SLEEP = float(os.environ.get("SLEEP", "0.45"))
TO = float(os.environ.get("BS_TIMEOUT", "20"))
RETRIES = int(os.environ.get("BS_RETRIES", "2"))
SHARD = int(sys.argv[1]); N = int(sys.argv[2])

def fetch(ts_code):
    tp._load()
    params = {"ts_code": ts_code, "limit": 5000, "offset": 0}
    err = None
    for i in range(RETRIES):
        try:
            r = requests.get(f"{tp.RELAY}/balancesheet", params=params,
                             headers={"X-API-Key": os.environ["TSPRO_PROXY_KEY"]}, timeout=TO)
            if r.status_code == 429:
                time.sleep(float(r.headers.get("Retry-After", 4))); continue
            d = r.json()
            if r.status_code == 200 and d.get("code") in (0, None) and "data" in d:
                return tp._to_df(d)
            err = (r.status_code, d.get("code"), str(d.get("msg"))[:100])
        except Exception as e:
            err = e
            time.sleep(1.2 * (i + 1))
    raise RuntimeError(str(err)[:180])

def main():
    tp._load()
    codes = []
    for st in ("L", "D"):
        f = RAW / "stock_basic" / f"{st}.parquet"
        if f.exists():
            codes += pd.read_parquet(f).ts_code.astype(str).tolist()
    codes = sorted(set(codes))
    mine = [c for j, c in enumerate(codes) if j % N == SHARD]
    outdir = RAW / "balancesheet"; outdir.mkdir(parents=True, exist_ok=True)
    ok = skip = fail = 0
    t0 = time.time()
    print(f"shard {SHARD}/{N} n={len(mine)} sleep={SLEEP}", flush=True)
    for i, c in enumerate(mine):
        key = c.replace(".", "_")
        f = outdir / f"{key}.parquet"
        if f.exists() and f.stat().st_size > 0:
            skip += 1
            continue
        # claim via exclusive tmp
        claim = outdir / f"{key}.claim"
        try:
            fd = os.open(str(claim), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
        except FileExistsError:
            skip += 1
            continue
        try:
            x = fetch(c).replace("", None)
            tmp = f.with_suffix(".tmp.parquet")
            x.to_parquet(tmp, index=False)
            os.replace(tmp, f)
            ok += 1
            if ok % 10 == 0 or ok <= 2:
                rate = ok / max(1e-6, (time.time() - t0) / 60)
                print(time.strftime("%H:%M:%S"), f"s{SHARD}", f"ok={ok} skip={skip} fail={fail} {rate:.1f}/min {c} n={len(x)}", flush=True)
            time.sleep(SLEEP)
        except Exception as e:
            fail += 1
            if fail <= 15 or fail % 20 == 0:
                print("FAIL", f"s{SHARD}", c, str(e)[:140], flush=True)
            time.sleep(1.5)
        finally:
            try: claim.unlink()
            except Exception: pass
        if (ok + fail) % 40 == 0 and ok + fail:
            (LOG / f"tier1_bs_shard{SHARD}_progress.json").write_text(json.dumps({
                "shard": SHARD, "ok": ok, "skip": skip, "fail": fail, "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S")
            }))
    print("DONE", f"s{SHARD}", {"ok": ok, "skip": skip, "fail": fail}, flush=True)
    (LOG / f"tier1_bs_shard{SHARD}_done.json").write_text(json.dumps({"ok": ok, "skip": skip, "fail": fail}))

if __name__ == "__main__":
    main()
