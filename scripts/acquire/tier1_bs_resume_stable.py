#!/usr/bin/env python3
"""Stable balancesheet resume: short timeouts, skip existing, same raw layout as tier1_pull.
Then materialize via tier1_materialize.materialize_bs_cf_pit.
"""
import sys, os, time, pathlib, json, warnings
warnings.filterwarnings("ignore")
ROOT = pathlib.Path("/workspace/QuantLab"); sys.path.insert(0, str(ROOT))
import pandas as pd
import requests
from quantlab.data_sources import tushare_proxy as tp

RAW = ROOT / "data/v2/tushare_raw"
LOG = ROOT / "data/_acquire_logs"; LOG.mkdir(parents=True, exist_ok=True)
SLEEP = float(os.environ.get("SLEEP", "0.55"))
TO = float(os.environ.get("BS_TIMEOUT", "25"))
RETRIES = int(os.environ.get("BS_RETRIES", "2"))

def _get(url, key, params):
    err = None
    for i in range(RETRIES):
        try:
            r = requests.get(url, params={k: v for k, v in params.items() if v is not None},
                             headers={"X-API-Key": key}, timeout=TO)
            if r.status_code == 429:
                time.sleep(float(r.headers.get("Retry-After", 5))); continue
            return r.status_code, r.json()
        except Exception as e:
            err = e
            time.sleep(1.5 * (i + 1))
    raise RuntimeError(str(err)[:200])

def fetch(ts_code):
    params = {"ts_code": ts_code, "limit": 5000, "offset": 0,
              "fields": "ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,update_flag,total_assets,total_liab,total_hldr_eqy_exc_min_int,total_hldr_eqy_inc_min_int"}
    # relay first (worked ~12/min earlier), then datahub HTTPS once
    last = None
    for label, url, key in (
        ("relay", f"{tp.RELAY}/balancesheet", os.environ["TSPRO_PROXY_KEY"]),
        ("datahub", f"{tp.DATAHUB_HTTPS}/balancesheet", os.environ["DATAHUB_API_KEY"]),
    ):
        try:
            s, d = _get(url, key, params)
            if s == 200 and d.get("code") in (0, None) and "data" in d:
                return tp._to_df(d), label
            last = (label, s, str(d)[:120])
        except Exception as e:
            last = (label, e)
            continue
    raise RuntimeError(f"balancesheet fail {ts_code}: {last}")

def main():
    tp._load()
    codes = []
    for st in ("L", "D"):
        f = RAW / "stock_basic" / f"{st}.parquet"
        if f.exists():
            codes += pd.read_parquet(f).ts_code.astype(str).tolist()
    codes = sorted(set(codes))
    outdir = RAW / "balancesheet"; outdir.mkdir(parents=True, exist_ok=True)
    ok = skip = fail = 0
    t0 = time.time()
    print(f"BS resume codes={len(codes)} sleep={SLEEP} timeout={TO}", flush=True)
    for i, c in enumerate(codes):
        key = c.replace(".", "_")
        f = outdir / f"{key}.parquet"
        if f.exists() and f.stat().st_size > 0:
            skip += 1
            continue
        try:
            x, src = fetch(c)
            x = x.replace("", None)
            tmp = f.with_suffix(".tmp.parquet")
            x.to_parquet(tmp, index=False); os.replace(tmp, f)
            ok += 1
            if ok % 10 == 0 or ok <= 3:
                rate = ok / max(1e-6, (time.time() - t0) / 60)
                print(time.strftime("%H:%M:%S"), f"{ok}/{len(codes)-skip} ok={ok} skip={skip} fail={fail} {rate:.1f}/min {c} n={len(x)} src={src}", flush=True)
            time.sleep(SLEEP)
        except Exception as e:
            fail += 1
            if fail <= 30 or fail % 25 == 0:
                print("FAIL", c, str(e)[:160], flush=True)
            time.sleep(2.0)
        if (ok + fail) % 50 == 0 and (ok + fail) > 0:
            (LOG / "tier1_bs_resume_progress.json").write_text(json.dumps({
                "ok": ok, "skip": skip, "fail": fail, "done": i + 1, "total": len(codes),
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S")
            }, indent=2))
    print("DONE", {"ok": ok, "skip": skip, "fail": fail, "total": len(codes)}, flush=True)
    (LOG / "tier1_bs_resume_done.json").write_text(json.dumps({"ok": ok, "skip": skip, "fail": fail, "total": len(codes)}))
    return 0 if fail < max(50, ok * 0.2) else 2

if __name__ == "__main__":
    raise SystemExit(main())
