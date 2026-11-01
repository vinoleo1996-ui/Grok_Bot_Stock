"""Fill hsgt_top10 in window priority order with frequent rebuilds."""
from __future__ import annotations
import json, os, sys, time, pathlib
ROOT = pathlib.Path("/workspace/QuantLab")
sys.path.insert(0, str(ROOT))
import pandas as pd
from quantlab.data_sources.tushare_proxy import relay, _to_df

RAW = ROOT / "data/v2/tushare_raw"
LOG = ROOT / "logs" / "event_hsgt_top10_windowed.log"
PROG = ROOT / "output/d1/nb_margin_fill_progress.json"
SLEEP = float(os.environ.get("TOP10_SLEEP", "0.6"))
REBUILD_EVERY = int(os.environ.get("REBUILD_EVERY", "30"))

WINDOWS = [
    ("20240101", "20250630"),  # exploration first
    ("20220601", "20231229"),  # mid gap
    ("20211209", "20220531"),  # early (may already be mostly done)
]

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
    out, off = [], 0
    for attempt in range(10):
        try:
            while True:
                s, raw = relay("hsgt_top10", trade_date=d, limit=5000, offset=off)
                if s == 429 or (isinstance(raw, dict) and (
                    "pool" in str(raw.get("error") or "").lower()
                    or "exhausted" in str(raw.get("error") or "").lower()
                    or s in (503, 504))):
                    raise RuntimeError(f"rate/pool {s} {raw}")
                if s == 403:
                    raise RuntimeError(f"forbidden {s} {raw}")
                df = _to_df(raw) if isinstance(raw, dict) else pd.DataFrame()
                out.append(df)
                if len(df) < 5000:
                    break
                off += 5000
                time.sleep(0.1)
            break
        except Exception as e:
            wait = min(240, 8 * (2 ** attempt))
            print(f"  retry {d} attempt={attempt} wait={wait}s err={str(e)[:140]}", flush=True)
            time.sleep(wait)
            out, off = [], 0
    else:
        raise RuntimeError(f"exhausted retries {d}")
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()

def save_prog(patch):
    cur = {}
    if PROG.exists():
        try: cur = json.load(open(PROG))
        except Exception: cur = {}
    cur.update(patch)
    cur["updated"] = pd.Timestamp.now().isoformat()
    tmp = PROG.with_suffix(".tmp")
    json.dump(cur, open(tmp, "w"), ensure_ascii=False, indent=2, default=str)
    os.replace(tmp, PROG)

def rebuild():
    from scripts.acquire.event_flow_build import build_northbound
    nb = build_northbound()
    save_prog({"northbound_rebuild": nb})
    t = nb.get("hsgt_top10", {})
    print(f"REBUILD top10 days={t.get('days')} range={t.get('range')} rows={t.get('rows')}", flush=True)
    return nb

def fill_window(start, end):
    days = trade_days(start, end)
    todo = [d for d in days if needs(d)]
    print(f"WINDOW {start}→{end} todo={len(todo)}/{len(days)} sleep={SLEEP}", flush=True)
    save_prog({"hsgt_top10": {"status": "running_windowed", "window": [start, end], "todo": len(todo), "done": 0, "fail": 0}})
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
                print(f"{time.strftime('%H:%M:%S')} top10 {i}/{len(todo)} [{start}-{end}] fail={fail} last={d}:ok:{n}", flush=True)
                save_prog({"hsgt_top10": {
                    "status": "running_windowed", "window": [start, end],
                    "todo": len(todo), "done": done, "fail": fail, "last": d, "last_rows": n,
                }})
            if i % REBUILD_EVERY == 0:
                rebuild()
        except Exception as e:
            fail += 1
            print(f"FAIL {d} {str(e)[:180]}", flush=True)
            save_prog({"hsgt_top10": {"status": "running_windowed", "window": [start, end], "todo": len(todo), "done": done, "fail": fail, "last_err": str(e)[:200]}})
            time.sleep(min(300, 25 * min(fail, 8)))
        time.sleep(SLEEP)
    rebuild()
    return done, fail

def main():
    open(LOG, "a").write(f"\n==== START {pd.Timestamp.now()} ====\n")
    total_done = total_fail = 0
    for start, end in WINDOWS:
        d, f = fill_window(start, end)
        total_done += d
        total_fail += f
    save_prog({"hsgt_top10": {"status": "done_windowed", "done": total_done, "fail": total_fail, "end": "20250630"}})
    print(f"ALL DONE done={total_done} fail={total_fail}", flush=True)
    return 0 if total_fail == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
