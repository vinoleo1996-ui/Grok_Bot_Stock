"""Priority fill hsgt_top10 to >=2025-06 with frequent rebuild checkpoints."""
from __future__ import annotations
import json, os, sys, time, pathlib
ROOT = pathlib.Path("/workspace/QuantLab")
sys.path.insert(0, str(ROOT))
import pandas as pd
from quantlab.data_sources.tushare_proxy import relay, _to_df

RAW = ROOT / "data/v2/tushare_raw"
LOG = ROOT / "logs"
OUT = ROOT / "output/d1"
PROG = OUT / "nb_margin_fill_progress.json"
END = os.environ.get("TOP10_END", "20250630")
START = os.environ.get("TOP10_START", "20211209")
SLEEP = float(os.environ.get("TOP10_SLEEP", "1.2"))
REBUILD_EVERY = int(os.environ.get("REBUILD_EVERY", "40"))

def trade_days(a, b):
    c = pd.read_parquet(RAW / "trade_cal.parquet")
    c = c[c.is_open.astype(int) == 1]
    return sorted(d for d in c.cal_date.astype(str) if a <= d <= b)

def needs(d, min_ok=700):
    f = RAW / "hsgt_top10" / f"{d}.parquet"
    return (not f.exists()) or f.stat().st_size < min_ok

def save_day(d, df):
    f = RAW / "hsgt_top10" / f"{d}.parquet"
    f.parent.mkdir(parents=True, exist_ok=True)
    x = df.replace("", None)
    for c in x.columns:
        if x[c].dtype == object and c not in ("ts_code", "trade_date", "name", "code", "exchange", "symbol"):
            n = pd.to_numeric(x[c], errors="coerce")
            if n.notna().sum() >= max(1, x[c].notna().sum()):
                x[c] = n
    tmp = f.with_suffix(".tmp.parquet")
    x.to_parquet(tmp, index=False)
    os.replace(tmp, f)
    return len(x)

def pull(d):
    out, off, limit = [], 0, 5000
    for attempt in range(8):
        try:
            while True:
                s, raw = relay("hsgt_top10", trade_date=d, limit=limit, offset=off)
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
            print(f"  retry {d} attempt={attempt} wait={wait}s err={str(e)[:120]}", flush=True)
            time.sleep(wait)
            out, off = [], 0
    else:
        raise RuntimeError(f"exhausted retries {d}")
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()

def save_prog(d):
    cur = {}
    if PROG.exists():
        try:
            cur = json.load(open(PROG))
        except Exception:
            cur = {}
    cur.update(d)
    cur["updated"] = pd.Timestamp.now().isoformat()
    tmp = PROG.with_suffix(".tmp")
    json.dump(cur, open(tmp, "w"), ensure_ascii=False, indent=2, default=str)
    os.replace(tmp, PROG)

def rebuild():
    from scripts.acquire.event_flow_build import build_northbound
    nb = build_northbound()
    save_prog({"northbound_rebuild": nb, "hsgt_top10_priority": {"last_rebuild": pd.Timestamp.now().isoformat()}})
    t = nb.get("hsgt_top10", {})
    print(f"REBUILD top10 days={t.get('days')} range={t.get('range')} rows={t.get('rows')}", flush=True)
    return nb

def main():
    days = trade_days(START, END)
    todo = [d for d in days if needs(d)]
    logf = open(LOG / "event_hsgt_top10_priority.log", "a")
    def log(m):
        print(m, flush=True); logf.write(m + "\n"); logf.flush()
    log(f"START priority top10 todo={len(todo)}/{len(days)} {START}→{END} sleep={SLEEP} rebuild_every={REBUILD_EVERY}")
    save_prog({"hsgt_top10": {"status": "running_priority", "todo": len(todo), "done": 0, "fail": 0, "end": END, "start": START}})
    done = fail = 0
    for i, d in enumerate(todo, 1):
        try:
            f = RAW / "hsgt_top10" / f"{d}.parquet"
            if f.exists() and f.stat().st_size < 700:
                f.unlink()
            df = pull(d)
            n = save_day(d, df)
            done += 1
            if i % 10 == 0 or i == len(todo):
                log(f"{time.strftime('%H:%M:%S')} top10 {i}/{len(todo)} fail={fail} last={d}:ok:{n}")
                save_prog({"hsgt_top10": {
                    "status": "running_priority", "todo": len(todo), "done": done, "fail": fail,
                    "last": d, "last_rows": n, "end": END, "start": START,
                }})
            if i % REBUILD_EVERY == 0:
                rebuild()
        except Exception as e:
            fail += 1
            log(f"FAIL top10 {d} {str(e)[:180]}")
            save_prog({"hsgt_top10": {"status": "running_priority", "todo": len(todo), "done": done, "fail": fail, "last_err": str(e)[:200]}})
            time.sleep(min(300, 20 * min(fail, 8)))
        time.sleep(SLEEP)
    log(f"DONE priority top10 done={done} fail={fail}")
    nb = rebuild()
    save_prog({"hsgt_top10": {"status": "done_priority", "done": done, "fail": fail, "end": END}, "northbound_rebuild": nb})
    logf.close()
    return 0 if fail == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
