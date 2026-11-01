#!/usr/bin/env python3
"""中转宕机补拉守护 (幂等, 轻量). 每 15 分钟探测 pcd.mobcvb.cn; 恢复后排队补拉
output/relay_outage_backfill_queue.json 中 pending 项: events 整步重跑 + hsgt 窗口. 不与重任务并行, MemAvailable<2GB 暂停.
全部完成后写 status=done 并退出. 已有实例在跑则直接退出 (pidfile)."""
import json, os, sys, time, pathlib, subprocess
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT = pathlib.Path("/workspace/QuantLab"); os.chdir(ROOT); sys.path.insert(0, str(ROOT / "scripts/acquire"))
from relay_health import probe
Q = ROOT / "output/relay_outage_backfill_queue.json"; PID = ROOT / "output/relay_outage_backfill.pid"
LOG = ROOT / "logs/relay_outage_backfill.log"; ET = ZoneInfo("America/New_York")
HEAVY = ("queue_chain_20261014", "stk_surv_after_report_rc", "tier1_materialize", "nightly_update", "remaining_after_stk_surv")
def log(m): open(LOG, "a").write(f"{datetime.now(ET).isoformat(timespec='seconds')} {m}\n")
def mem_gb(): return next(int(l.split()[1]) for l in open("/proc/meminfo") if l.startswith("MemAvailable")) / 1e6
def heavy(): 
    out = []
    for d in pathlib.Path("/proc").iterdir():
        if d.name.isdigit() and int(d.name) != os.getpid():
            try: c = (d / "cmdline").read_bytes().replace(b"\0", b" ").decode()
            except Exception: continue
            if "python" in c and any(h in c for h in HEAVY): out.append(c[:80])
    return out
def busy_ok():
    # fund_portfolio/broker 是 datahub 慢翻页, 内存低; 只避让真正的重物化/nightly. remaining_after_stk_surv 视为轻背景但仍要求内存充足
    h = [x for x in heavy() if "remaining_after_stk_surv" not in x]
    return not h and mem_gb() >= 2.0
def latest_td():
    # 2026-10-18 修: 原写死 QL_TODAY=2026-10-14, 会把事件一年窗口表回滚到 10-14. 改为交易日历中 <= 今天(上海) 的最后开市日
    import pandas as pd
    today = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y%m%d")
    c = pd.read_parquet(ROOT / "data/v2/calendar/trade_cal_sse_pit.parquet")
    return max(d for d in c[c.is_open == 1].cal_date.astype(str) if d <= today)
def step_status(summary, step, t0, log_mtime):
    """PURE (no I/O). summary: parsed logs/nightly/<date>_summary.json dict or None (missing/unreadable).
    t0: epoch seconds taken before nightly_update was started; log_mtime: epoch mtime of the step log or None.
    Returns (status, reason, relay_down). status 'ok' only for a fresh entry written by this run."""
    if not isinstance(summary, dict) or not isinstance(summary.get("steps"), dict):
        return "pending", "summary_unreadable", False
    e = summary["steps"].get(step)
    if not isinstance(e, dict) or "status" not in e:
        return "pending", "no_step_entry", False
    st = str(e.get("status")); sk = str(e.get("skipped") or ""); sec = e.get("sec")
    relay_down = "RELAY_DOWN" in sk or (st.startswith("partial") and sec in (0, 0.0))   # P3-1
    try:
        fin = datetime.fromisoformat(str(summary.get("finished"))).timestamp()
    except Exception:
        return "pending", "stale_summary: finished unparsable", relay_down
    if fin < t0:
        return "pending", "stale_summary: finished < t0", relay_down
    # P2-1: entry must be from this run: a fast-fail skip writes no log (sec==0); otherwise the step log must be touched after t0
    if not relay_down and (log_mtime is None or log_mtime < t0):
        return "pending", "stale_summary: step log mtime < t0", relay_down
    if st == "ok": return "ok", "ok", False
    return "pending", f"step_status={st}" + (f" skipped={sk}" if sk else ""), relay_down
def read_step_status(item, t0):
    """thin I/O wrapper around step_status."""
    try: d = item["params"]["date"]; k = item["params"]["step"]
    except Exception: return "pending", "summary_unreadable: item has no date/step", False
    try: summ = json.loads((ROOT / f"logs/nightly/{d}_summary.json").read_text())
    except Exception: summ = None
    lp = ROOT / f"logs/nightly/{d}_{k}.log"
    return step_status(summ, k, t0, lp.stat().st_mtime if lp.exists() else None)
def save(q): Q.write_text(json.dumps(q, ensure_ascii=False, indent=1))
def run(name, cmd, env_extra):
    env = dict(os.environ, **env_extra); t = time.time()
    with open(ROOT / f"logs/relay_backfill_{name}.log", "a") as fh:
        rc = subprocess.call(cmd, env=env, stdout=fh, stderr=subprocess.STDOUT)
    log(f"{name} rc={rc} {round(time.time()-t)}s"); return rc
def main():
    if PID.exists():
        try: os.kill(int(PID.read_text()), 0); print("already running"); return
        except Exception: pass
    PID.write_text(str(os.getpid())); log("start")
    while True:
        q = json.loads(Q.read_text())
        pend = [i for i in q["items"] + q.get("extra", []) if i["status"] != "done"]
        if not pend: q["status"] = "done"; save(q); log("all done, exit"); break
        st = probe(); q["last_probe"] = {k: st[k] for k in ("up", "err", "checked_at")}; save(q)
        if not st["up"]: log("relay down"); time.sleep(900); continue
        while not busy_ok(): log("wait heavy/mem"); time.sleep(120)
        q["status"] = "backfilling"; save(q)
        ev = [i for i in q["items"] if i["status"] != "done"]
        if ev:
            rc = run("events", [sys.executable, "scripts/acquire/_light_event_windows_pull.py"], {"QL_TODAY": f"{latest_td()[:4]}-{latest_td()[4:6]}-{latest_td()[6:]}"})
            sm = json.loads((ROOT / "data/v2/events/light_event_windows_summary.json").read_text())
            ok = rc == 0 and not sm.get("n_fails")
            for i in ev: i["status"] = "done" if ok else "retry"; i["last_try"] = datetime.now(ET).isoformat(timespec="seconds")
            q["events_last"] = dict(rc=rc, n_fails=sm.get("n_fails")); save(q)
        for i in [i for i in q.get("extra", []) if i["status"] != "done" and i.get("retry_cmd")]:
            t0 = time.time()   # P2-1: freshness reference taken BEFORE nightly_update starts
            rc = run(i["api"], i["retry_cmd"].split(), {})
            # 2026-10-18 fix v2 (draft): nightly_update exits 0 even when the step failed/was skipped -> judge by fresh summary entry
            status, reason, relay_down = read_step_status(i, t0)
            i["last_rc"] = rc; i["last_step_status"] = status; i["last_try"] = datetime.now(ET).isoformat(timespec="seconds")
            if rc == 0 and status == "ok": i["status"] = "done"; i.pop("false_done_reason", None)
            else: i["status"] = "pending"; i["false_done_reason"] = f"rc={rc} {reason}"
            save(q)
            if relay_down: log(f"relay down ({i['id']}: {reason}), back off"); break   # P3-1: no hammering; outer loop sleeps 900
        hs = [i for i in q.get("extra", []) if i["status"] != "done" and not i.get("retry_cmd")]
        if hs:
            rc = 2
            for _ in range(20):  # 分块, exit 2 = 仍有剩余
                rc = run("hsgt", [sys.executable, "scripts/acquire/fill_hsgt_top10_extend.py"], {"TOP10_START": "20251014", "TOP10_END": latest_td(), "CHUNK_DAYS": "30"})
                if rc != 2: break
            for i in hs: i["status"] = "done" if rc in (0, 2) else "retry"; i["last_rc"] = rc  # rc2 剩余=源头空日(如20251226)
            save(q)
        if any(i["status"] != "done" for i in q["items"] + q.get("extra", [])): time.sleep(900)
    PID.unlink(missing_ok=True)
if __name__ == "__main__": main()
