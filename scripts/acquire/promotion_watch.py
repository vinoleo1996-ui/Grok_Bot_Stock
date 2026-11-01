#!/usr/bin/env python3
"""Watch pull jobs; rematerialize + extend_panels + acceptance when ready. Single instance."""
import os, sys, time, pathlib, subprocess, json
ROOT = pathlib.Path("/workspace/QuantLab")
LOG = ROOT / "data/_acquire_logs"
LOCK = LOG / "promotion_watch.lock"
if LOCK.exists():
    # stale?
    try:
        old = int(LOCK.read_text().strip())
        os.kill(old, 0)
        print("watch already running", old); sys.exit(0)
    except Exception:
        pass
LOCK.write_text(str(os.getpid()))

def alive(pattern):
    out = subprocess.check_output(["ps","aux"], text=True)
    return any(pattern in ln and "rg " not in ln for ln in out.splitlines())

def run_job(job):
    print(time.strftime("%H:%M:%S"), "RUN", job, flush=True)
    subprocess.check_call([sys.executable, "-u", str(ROOT/"scripts/acquire/tushare_relay_pull.py"), job], cwd=str(ROOT))

def accept():
    print(time.strftime("%H:%M:%S"), "ACCEPT", flush=True)
    subprocess.call([sys.executable, "-u", str(ROOT/"scripts/acquire/promotion_acceptance.py")], cwd=str(ROOT))

def update_eng_ping():
    import datetime as dt
    from zoneinfo import ZoneInfo
    now = dt.datetime.now(ZoneInfo("America/New_York")).isoformat()
    acc = ROOT/"docs/v2/PROMOTION_ACCEPTANCE.json"
    results = json.loads(acc.read_text())["results"] if acc.exists() else {}
    acceptance_all_pass = all(v.get("pass") for v in results.values()) if results else False
    payload = {
        "title": "Eng ping — tushare materialize + acceptance",
        "time": now,
        # Standing rule: overall promotion stays false until Leo explicitly flips it.
        # Acceptance gate PASS is evidence only — never auto-promote.
        "promotion_approved_overall": False,
        "acceptance_all_pass": acceptance_all_pass,
        "acceptance": results,
        "paths": {
            "sw_l1_tushare": str(ROOT/"data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet"),
            "float_mktcap_tushare": str(ROOT/"data/v2/float_mktcap/float_mktcap_daily_tushare.parquet"),
            "asof_extend_tushare_panels": str(ROOT/"data/v2/asof_extend_tushare_202610/panels"),
            "financials_available_at_tushare": str(ROOT/"data/v2/financials_pit/financials_available_at_tushare.parquet"),
            "dividend_tushare": str(ROOT/"data/v2/corporate_actions/dividend_tushare.parquet"),
            "dividend_by_exdate": str(ROOT/"data/v2/corporate_actions/dividend_by_exdate_tushare.parquet"),
            "etf_510300_panel": str(ROOT/"data/v2/etf_510300/panels/sh.510300.parquet"),
            "etf_fund_daily_tushare": str(ROOT/"data/v2/etf_510300/fund_daily_tushare_510300.parquet"),
            "acceptance_md": str(ROOT/"docs/v2/PROMOTION_ACCEPTANCE.md"),
        },
        "jobs_alive": {
            "extend": alive("tushare_relay_pull.py extend"),
            "daily_basic_hist": alive("tushare_relay_pull.py daily_basic_hist"),
            "fin": alive("tushare_relay_pull.py fin"),
            "dividend": alive("tushare_relay_pull.py dividend"),
            "div_ex": alive("tushare_relay_pull.py dividend_by_exdate"),
        },
        "note": "Prefer tushare paths when acceptance.pass=true; else keep research fallbacks. acceptance_all_pass is evidence only; promotion_approved_overall stays false until Leo flips it.",
    }
    out = ROOT/"output/d1/ENG_PING_PATHS.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print("eng ping updated", out, flush=True)

extend_done_panels = False
last_mat = 0
while True:
    try:
        # rematerialize every 10 min or when extend flips done
        extend_alive = alive("tushare_relay_pull.py extend")
        now = time.time()
        if now - last_mat > 600:
            run_job("materialize")
            last_mat = now
            accept()
            update_eng_ping()
        if (not extend_alive) and (not extend_done_panels):
            # ensure raw has days
            n = len(list((ROOT/"data/v2/tushare_raw/daily").glob("*.parquet")))
            print("extend finished, daily days", n, flush=True)
            if n >= 50:
                run_job("extend_panels")
                extend_done_panels = True
                run_job("materialize")
                accept()
                update_eng_ping()
        # exit when all bulk pulls done and acceptance ran after final mat
        still = any([
            alive("tushare_relay_pull.py extend"),
            alive("tushare_relay_pull.py daily_basic_hist"),
            alive("tushare_relay_pull.py fin"),
            alive("tushare_relay_pull.py dividend"),
            alive("tushare_relay_pull.py dividend_by_exdate"),
            alive("tushare_relay_pull.py disclosure_dates"),
        ])
        if not still and extend_done_panels:
            run_job("materialize")
            accept()
            update_eng_ping()
            print("ALL PULLS DONE — watch exit", flush=True)
            break
        time.sleep(60)
    except Exception as e:
        print("WATCH ERR", e, flush=True)
        time.sleep(60)
