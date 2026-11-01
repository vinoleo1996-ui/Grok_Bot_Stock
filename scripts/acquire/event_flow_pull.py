"""Event-flow / capital-structure research pulls (Leo approved).
Jobs: anns | margin | margin_detail | moneyflow_hsgt | hsgt_top10 | hk_hold | all_except_anns
Usage: python3 scripts/acquire/event_flow_pull.py <job>
promotion_approved=false for all outputs; materialize separately.
"""
from __future__ import annotations
import os, sys, time, pathlib, concurrent.futures as cf
ROOT = pathlib.Path("/workspace/QuantLab"); sys.path.insert(0, str(ROOT))
import pandas as pd
from quantlab.data_sources.tushare_proxy import relay, datahub, _to_df

RAW = ROOT / "data/v2/tushare_raw"
LOG = ROOT / "logs"
LOG.mkdir(parents=True, exist_ok=True)

def dates_trade(a="20180101", b="20261009"):
    f = RAW / "trade_cal.parquet"
    c = pd.read_parquet(f); c = c[c.is_open.astype(int) == 1]
    return sorted(d for d in c.cal_date.astype(str) if a <= d <= b)

def dates_cal(a="2018-01-01", b="2026-10-09"):
    return [d.strftime("%Y-%m-%d") for d in pd.date_range(a, b, freq="D")]

def _is_pool(s, d):
    if s in (503, 504):
        return True
    if isinstance(d, dict):
        err = str(d.get("error") or d.get("msg") or "").lower()
        if "pool" in err or "exhausted" in err or "timeout" in err:
            return True
    return False

def _call_relay(api, **p):
    last = None
    for i in range(10):
        try:
            s, d = relay(api, **p)
            if s == 200 and d.get("code") in (0, None) and "data" in d:
                return s, d
            last = (s, d)
            if s == 429 or _is_pool(s, d):
                time.sleep(min(180, 8 * (2 ** i))); continue
            if s == 200:
                return s, d
        except Exception as e:
            last = e
            time.sleep(min(120, 3 * (2 ** i)))
    raise RuntimeError(f"relay {api}: {str(last)[:200]}")

def _call_datahub(api, **p):
    last = None
    for i in range(10):
        try:
            s, d = datahub(api, **p)
            if s == 200 and d.get("code") in (0, None) and "data" in d:
                return s, d
            last = (s, d)
            if s == 429 or _is_pool(s, d):
                time.sleep(min(180, 8 * (2 ** i))); continue
            if s == 200:
                return s, d
        except Exception as e:
            last = e
            time.sleep(min(120, 3 * (2 ** i)))
    raise RuntimeError(f"datahub {api}: {str(last)[:200]}")

def pull_page(api, source="relay", limit=5000, **p):
    out, off = [], 0
    while True:
        params = {**p, "limit": limit, "offset": off}
        if source == "datahub":
            s, d = _call_datahub(api, **params)
        else:
            s, d = _call_relay(api, **params)
        x = _to_df(d)
        out.append(x)
        if len(x) < limit:
            break
        off += limit
        time.sleep(0.12)
        # anns_d: hard cap observed at 5000 even with offset
        if api == "anns_d" and off >= 5000:
            break
    if not out:
        return pd.DataFrame()
    return pd.concat(out, ignore_index=True)

def cached(api, key, source="relay", **p):
    f = RAW / api / f"{key}.parquet"
    f.parent.mkdir(parents=True, exist_ok=True)
    if f.exists() and f.stat().st_size > 0:
        return "skip"
    x = pull_page(api, source=source, **p)
    # anns_d: date format is flaky — retry alternate form if empty
    if api == "anns_d" and len(x) == 0 and "ann_date" in p:
        alt = p["ann_date"]
        if "-" in alt:
            alt2 = alt.replace("-", "")
        else:
            alt2 = f"{alt[:4]}-{alt[4:6]}-{alt[6:8]}" if len(alt) == 8 else alt
        if alt2 != alt:
            time.sleep(0.3)
            x2 = pull_page(api, source=source, **{**p, "ann_date": alt2})
            if len(x2) > len(x):
                x = x2
    x = x.replace("", None)
    for c in x.columns:
        if x[c].dtype == object and c not in (
            "ts_code", "trade_date", "ann_date", "ann_time", "title", "url",
            "name", "symbol", "ann_type", "exalter", "reason", "side", "code", "exchange",
            "exchange_id",
        ):
            n = pd.to_numeric(x[c], errors="coerce")
            if n.notna().sum() >= max(1, x[c].notna().sum()):
                x[c] = n
    # mark truncation for anns_d
    if api == "anns_d" and len(x) >= 5000:
        x.attrs["truncated"] = True
    tmp = f.with_suffix(".tmp.parquet")
    x.to_parquet(tmp, index=False)
    os.replace(tmp, f)
    flag = f"ok:{len(x)}"
    if api == "anns_d" and len(x) >= 5000:
        flag += ":TRUNC5000"
    return flag

def run(tasks, workers=3, label="", logname=None):
    # tasks: list of (api, key, source, params)
    done = fail = 0
    n = len(tasks)
    logf = open(LOG / (logname or f"event_{label}.log"), "a")
    def log(msg):
        print(msg, flush=True)
        logf.write(msg + "\n"); logf.flush()
    log(f"START {label} n={n} workers={workers}")
    if n == 0:
        log(f"DONE {label} fail=0 (nothing to do)")
        logf.close()
        return 0
    def one(t):
        api, key, source, p = t
        return cached(api, key, source=source, **p)
    with cf.ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(one, t): t for t in tasks}
        for fu in cf.as_completed(futs):
            done += 1
            t = futs[fu]
            try:
                r = fu.result()
            except Exception as e:
                fail += 1
                log(f"FAIL {t[0]} {t[1]} {str(e)[:180]}")
                r = "FAIL"
            if done % 25 == 0 or done == n or (isinstance(r, str) and r.startswith("ok") and "TRUNC" in r):
                log(f"{time.strftime('%H:%M:%S')} {label} {done}/{n} fail={fail} last={t[1]}:{r}")
    log(f"DONE {label} fail={fail}")
    logf.close()
    return fail

def _anns_have(key, recheck):
    f = RAW / "anns_d" / f"{key}.parquet"
    if not (f.exists() and f.stat().st_size > 0):
        return False
    # 0-row trading days are suspicious (likely swallowed error) -> re-pull once
    if key in recheck:
        return True
    try:
        if len(pd.read_parquet(f, columns=[])) == 0:
            return None
    except Exception:
        return None
    return True

def anns_plan(seal_end="20240531", end="20261009"):
    tdays = set(dates_trade("20180101", end))
    allc = [d.strftime("%Y%m%d") for d in pd.date_range("2018-01-01", end, freq="D")]
    p1 = [d for d in allc if d in tdays and d <= seal_end]
    p2 = [d for d in allc if d in tdays and d > seal_end]
    p3 = [d for d in allc if d not in tdays]
    return p1, p2, p3

def job_anns():
    """Priority: P1 seal-window trade days -> P2 later trade days -> P3 non-trading days.
    Skips landed days; 0-row trade days re-pulled once; outer rounds w/ cooldown for 503/504/pool."""
    recf = LOG / "anns_empty_rechecked.txt"
    recheck = set(recf.read_text().split()) if recf.exists() else set()
    workers = int(os.environ.get("WORKERS", 3))
    rounds = int(os.environ.get("ANNS_ROUNDS", 6))
    p1, p2, p3 = anns_plan()
    for name, days in (("P1_seal_trade", p1), ("P2_post_trade", p2), ("P3_nontrade", p3)):
        for r in range(1, rounds + 1):
            tasks = []
            for key in days:
                h = _anns_have(key, recheck)
                if h:
                    continue
                if h is None:
                    if name == "P3_nontrade":
                        continue  # empty weekend/holiday is plausible
                    (RAW / "anns_d" / f"{key}.parquet").unlink(missing_ok=True)
                    recheck.add(key)
                    with open(recf, "a") as fh:
                        fh.write(key + "\n")
                tasks.append(("anns_d", key, "relay", {"ann_date": key}))
            print(f"PHASE {name} round={r} miss={len(tasks)}", flush=True)
            if not tasks:
                break
            fail = run(tasks, workers=workers, label=f"anns_{name}", logname="event_anns.log")
            if fail == 0:
                break
            w = workers
            if fail > max(3, len(tasks) // 4):
                workers = max(1, workers - 1)
            time.sleep(min(300, 30 * r))
            workers = w if fail <= max(3, len(tasks) // 4) else workers
        print(f"PHASE_DONE {name}", flush=True)
    return 0

def _margin_detail_tasks():
    fields = "trade_date,ts_code,name,rzye,rzmre,rzche,rqye,rqmcl,rzrqye,rqyl,rqchl"
    ds = dates_trade("20180101", "20261009")
    tasks = [
        ("margin_detail", d, "datahub", {"trade_date": d, "fields": fields})
        for d in ds
        if not (RAW / "margin_detail" / f"{d}.parquet").exists()
        or (RAW / "margin_detail" / f"{d}.parquet").stat().st_size == 0
    ]
    return tasks

def job_margin_detail():
    # datahub + fields= to bypass SH-only cache; outer loop for 504/pool leftovers
    rounds = int(os.environ.get("MARGIN_ROUNDS", 8))
    workers = int(os.environ.get("WORKERS", 2))
    total_fail = 0
    for r in range(1, rounds + 1):
        tasks = _margin_detail_tasks()
        print(f"RESUME margin_detail round={r} miss={len(tasks)} workers={workers}", flush=True)
        if not tasks:
            print("RESUME margin_detail complete miss=0", flush=True)
            return 0
        fail = run(tasks, workers=workers, label="margin_detail", logname="event_margin_detail.log")
        total_fail += fail
        left = len(_margin_detail_tasks())
        if left == 0:
            print("RESUME margin_detail complete miss=0", flush=True)
            return 0
        # cool down then retry remaining; shrink workers on heavy fail
        if fail > max(3, len(tasks) // 4):
            workers = 1
        cool = min(180, 20 * r)
        print(f"RESUME cool {cool}s left={left} fail_round={fail}", flush=True)
        time.sleep(cool)
    left = len(_margin_detail_tasks())
    print(f"RESUME margin_detail stop left={left} total_fail={total_fail}", flush=True)
    return left

def job_margin():
    # exchange-level summary; pull by year via start/end or by day
    years = list(range(2018, 2027))
    tasks = []
    for y in years:
        a, b = f"{y}0101", f"{y}1231"
        if y == 2026:
            b = "20261009"
        key = f"y{y}"
        f = RAW / "margin" / f"{key}.parquet"
        if f.exists() and f.stat().st_size > 0:
            continue
        tasks.append(("margin", key, "datahub", {"start_date": a, "end_date": b}))
    return run(tasks, workers=2, label="margin", logname="event_margin.log")

def job_moneyflow_hsgt():
    years = list(range(2018, 2027))
    tasks = []
    for y in years:
        a, b = f"{y}0101", f"{y}1231"
        if y == 2026:
            b = "20261009"
        key = f"y{y}"
        f = RAW / "moneyflow_hsgt" / f"{key}.parquet"
        if f.exists() and f.stat().st_size > 0:
            continue
        # relay only (datahub unknown api)
        tasks.append(("moneyflow_hsgt", key, "relay", {"start_date": a, "end_date": b}))
    return run(tasks, workers=2, label="moneyflow_hsgt", logname="event_hsgt_flow.log")

def job_hsgt_top10():
    ds = dates_trade("20180101", "20261009")
    tasks = [
        ("hsgt_top10", d, "relay", {"trade_date": d})
        for d in ds
        if not (RAW / "hsgt_top10" / f"{d}.parquet").exists()
        or (RAW / "hsgt_top10" / f"{d}.parquet").stat().st_size == 0
    ]
    return run(tasks, workers=int(os.environ.get("WORKERS", 4)), label="hsgt_top10", logname="event_hsgt_top10.log")

def job_hk_hold():
    ds = dates_trade("20180101", "20261009")
    tasks = [
        ("hk_hold", d, "relay", {"trade_date": d})
        for d in ds
        if not (RAW / "hk_hold" / f"{d}.parquet").exists()
        or (RAW / "hk_hold" / f"{d}.parquet").stat().st_size == 0
    ]
    return run(tasks, workers=int(os.environ.get("WORKERS", 3)), label="hk_hold", logname="event_hk_hold.log")

if __name__ == "__main__":
    job = sys.argv[1] if len(sys.argv) > 1 else "help"
    fns = {
        "anns": job_anns,
        "margin": job_margin,
        "margin_detail": job_margin_detail,
        "moneyflow_hsgt": job_moneyflow_hsgt,
        "hsgt_top10": job_hsgt_top10,
        "hk_hold": job_hk_hold,
    }
    if job == "all_except_anns":
        for k in ["margin", "moneyflow_hsgt", "margin_detail", "hsgt_top10", "hk_hold"]:
            print("===", k, flush=True)
            fns[k]()
    elif job in fns:
        fns[job]()
    else:
        print("jobs:", ", ".join(list(fns) + ["all_except_anns"]))
