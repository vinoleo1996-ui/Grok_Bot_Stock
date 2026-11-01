"""Fill northbound hk_hold + hsgt_top10 gaps (research-grade).
Priority: hk_hold (datahub) > hsgt_top10 (relay, yield to anns).
WORKERS default 1. Progress: output/d1/nb_margin_fill_progress.json
Usage:
  python3 scripts/acquire/fill_nb_margin_gaps.py hk_hold
  python3 scripts/acquire/fill_nb_margin_gaps.py hsgt_top10
  python3 scripts/acquire/fill_nb_margin_gaps.py rebuild
"""
from __future__ import annotations
import json, os, sys, time, pathlib
ROOT = pathlib.Path("/workspace/QuantLab")
sys.path.insert(0, str(ROOT))
import pandas as pd
from quantlab.data_sources.tushare_proxy import datahub, relay, _to_df

RAW = ROOT / "data/v2/tushare_raw"
LOG = ROOT / "logs"
OUT = ROOT / "output/d1"
PROG = OUT / "nb_margin_fill_progress.json"
LOG.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)

HK_END = os.environ.get("HK_HOLD_END", "20240830")  # A-share disclosure ends ~2024-08
SLEEP = float(os.environ.get("PULL_SLEEP", "0.8"))
WORKERS = int(os.environ.get("WORKERS", "1"))

def trade_days(a="20180101", b="20261009"):
    c = pd.read_parquet(RAW / "trade_cal.parquet")
    c = c[c.is_open.astype(int) == 1]
    return sorted(d for d in c.cal_date.astype(str) if a <= d <= b)

def _load_prog():
    if PROG.exists():
        try:
            return json.load(open(PROG))
        except Exception:
            return {}
    return {}

def _save_prog(d):
    cur = _load_prog()
    cur.update(d)
    cur["updated"] = pd.Timestamp.now().isoformat()
    tmp = PROG.with_suffix(".tmp")
    json.dump(cur, open(tmp, "w"), ensure_ascii=False, indent=2, default=str)
    os.replace(tmp, PROG)

def pull_page(api, source, **p):
    """Paginate; source in {datahub, relay}."""
    out, off, limit = [], 0, int(p.pop("limit", 5000) or 5000)
    call = datahub if source == "datahub" else relay
    for attempt in range(8):
        try:
            while True:
                params = {**p, "limit": limit, "offset": off}
                s, raw = call(api, **params)
                if s == 429 or (isinstance(raw, dict) and (
                    "pool" in str(raw.get("error") or "").lower()
                    or "exhausted" in str(raw.get("error") or "").lower()
                    or s in (503, 504)
                )):
                    raise RuntimeError(f"rate/pool {s} {raw}")
                if s == 403:
                    raise RuntimeError(f"forbidden {s} {raw}")
                df = _to_df(raw) if isinstance(raw, dict) else pd.DataFrame()
                out.append(df)
                if len(df) < limit:
                    break
                off += limit
                time.sleep(0.15)
            break
        except Exception as e:
            wait = min(180, 6 * (2 ** attempt))
            print(f"  retry {api} attempt={attempt} wait={wait}s err={str(e)[:120]}", flush=True)
            time.sleep(wait)
            out, off = [], 0
    else:
        raise RuntimeError(f"exhausted retries {api} {p}")
    if not out:
        return pd.DataFrame()
    return pd.concat(out, ignore_index=True)

def needs_pull(api, d, min_ok_size=5000):
    f = RAW / api / f"{d}.parquet"
    if not f.exists() or f.stat().st_size == 0:
        return True
    if f.stat().st_size < min_ok_size:
        return True  # empty schema / failed write
    return False

def save_day(api, d, df):
    f = RAW / api / f"{d}.parquet"
    f.parent.mkdir(parents=True, exist_ok=True)
    x = df.replace("", None)
    for c in x.columns:
        if x[c].dtype == object and c not in (
            "ts_code", "trade_date", "name", "code", "exchange", "symbol",
        ):
            n = pd.to_numeric(x[c], errors="coerce")
            if n.notna().sum() >= max(1, x[c].notna().sum()):
                x[c] = n
    tmp = f.with_suffix(".tmp.parquet")
    x.to_parquet(tmp, index=False)
    os.replace(tmp, f)
    return len(x)

def job_hk_hold():
    """datahub; A-share window through HK_END."""
    days = trade_days("20180101", HK_END)
    todo = [d for d in days if needs_pull("hk_hold", d)]
    logf = open(LOG / "event_hk_hold_fill.log", "a")
    def log(m):
        print(m, flush=True); logf.write(m + "\n"); logf.flush()
    log(f"START hk_hold todo={len(todo)}/{len(days)} end={HK_END} sleep={SLEEP}")
    _save_prog({"hk_hold": {"status": "running", "todo": len(todo), "done": 0, "fail": 0, "end": HK_END}})
    done = fail = 0
    for i, d in enumerate(todo, 1):
        try:
            # delete tiny empty so we overwrite cleanly
            f = RAW / "hk_hold" / f"{d}.parquet"
            if f.exists() and f.stat().st_size < 5000:
                f.unlink()
            df = pull_page("hk_hold", "datahub", trade_date=d)
            n = save_day("hk_hold", d, df)
            done += 1
            ash = int(df.ts_code.astype(str).str.endswith((".SH", ".SZ")).sum()) if len(df) and "ts_code" in df else 0
            if i % 10 == 0 or i == len(todo) or ash == 0:
                log(f"{time.strftime('%H:%M:%S')} hk_hold {i}/{len(todo)} fail={fail} last={d}:ok:{n}:A={ash}")
                _save_prog({"hk_hold": {
                    "status": "running", "todo": len(todo), "done": done, "fail": fail,
                    "last": d, "last_rows": n, "last_A": ash, "end": HK_END,
                }})
        except Exception as e:
            fail += 1
            log(f"FAIL hk_hold {d} {str(e)[:180]}")
            _save_prog({"hk_hold": {"status": "running", "todo": len(todo), "done": done, "fail": fail, "last_err": str(e)[:200]}})
            time.sleep(min(120, 10 * fail))
        time.sleep(SLEEP)
    log(f"DONE hk_hold done={done} fail={fail}")
    _save_prog({"hk_hold": {"status": "done", "done": done, "fail": fail, "end": HK_END}})
    logf.close()
    return fail

def job_hsgt_top10():
    """relay only (datahub 403 scope). Yield: WORKERS=1, longer sleep."""
    days = trade_days("20180101", "20261009")
    # only miss + tiny; don't force-repull mid-window empties that may be HK holidays
    todo = [d for d in days if needs_pull("hsgt_top10", d, min_ok_size=700)]
    # Prefer forward fill from last ok: skip redoing early empties unless miss
    sleep = float(os.environ.get("TOP10_SLEEP", "1.5"))
    logf = open(LOG / "event_hsgt_top10_fill.log", "a")
    def log(m):
        print(m, flush=True); logf.write(m + "\n"); logf.flush()
    log(f"START hsgt_top10 todo={len(todo)}/{len(days)} sleep={sleep}")
    _save_prog({"hsgt_top10": {"status": "running", "todo": len(todo), "done": 0, "fail": 0}})
    done = fail = 0
    for i, d in enumerate(todo, 1):
        try:
            f = RAW / "hsgt_top10" / f"{d}.parquet"
            if f.exists() and f.stat().st_size < 700:
                f.unlink()
            df = pull_page("hsgt_top10", "relay", trade_date=d)
            n = save_day("hsgt_top10", d, df)
            done += 1
            if i % 10 == 0 or i == len(todo):
                log(f"{time.strftime('%H:%M:%S')} hsgt_top10 {i}/{len(todo)} fail={fail} last={d}:ok:{n}")
                _save_prog({"hsgt_top10": {
                    "status": "running", "todo": len(todo), "done": done, "fail": fail,
                    "last": d, "last_rows": n,
                }})
        except Exception as e:
            fail += 1
            log(f"FAIL hsgt_top10 {d} {str(e)[:180]}")
            _save_prog({"hsgt_top10": {"status": "running", "todo": len(todo), "done": done, "fail": fail, "last_err": str(e)[:200]}})
            # cool down heavily if pool exhausted (anns competing)
            time.sleep(min(300, 20 * min(fail, 8)))
        time.sleep(sleep)
    log(f"DONE hsgt_top10 done={done} fail={fail}")
    _save_prog({"hsgt_top10": {"status": "done", "done": done, "fail": fail}})
    logf.close()
    return fail

def job_rebuild():
    from scripts.acquire.event_flow_build import build_northbound, build_margin
    # margin already rebuilt from rzrq; rebuild northbound only
    nb = build_northbound()
    _save_prog({"northbound_rebuild": nb})
    print(json.dumps(nb, ensure_ascii=False, indent=2, default=str))
    return nb

if __name__ == "__main__":
    job = sys.argv[1] if len(sys.argv) > 1 else "help"
    if job == "hk_hold":
        sys.exit(0 if job_hk_hold() == 0 else 1)
    elif job == "hsgt_top10":
        sys.exit(0 if job_hsgt_top10() == 0 else 1)
    elif job == "rebuild":
        job_rebuild()
    elif job == "all":
        job_hk_hold()
        job_rebuild()
        job_hsgt_top10()
        job_rebuild()
    else:
        print("jobs: hk_hold | hsgt_top10 | rebuild | all")
