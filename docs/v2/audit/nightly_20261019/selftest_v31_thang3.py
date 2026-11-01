import importlib.util, os, sys, datetime
sys.dont_write_bytecode = True
DRV, TMP, MODE = sys.argv[1], sys.argv[2], sys.argv[3]
spec = importlib.util.spec_from_file_location("drv", DRV)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
def w(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "x").write(t)
# 假 nightly_update.py：daily_pull → 假 tier1_pull（可写坏假日历、忽略 TERM、永远睡）；callb 模式下 daily_pull 秒成功并写 summary；其余步骤 → 假 tier3 树永远睡
w(TMP + "/scripts/nightly_update.py", """import os, sys, subprocess, time, json, datetime
steps = sys.argv[sys.argv.index("--steps") + 1]; d = sys.argv[sys.argv.index("--date") + 1]
mode = os.environ.get("FAKE_MODE", "hang"); mode2 = os.environ.get("FAKE_MODE2", mode)
os.makedirs("logs/nightly", exist_ok=True)
if steps == "daily_pull":
    log = open("logs/nightly/%s_daily_pull.log" % d, "a")
    log.write("\\n=== %s /usr/bin/python3 scripts/acquire/tier1_pull.py extend %s\\n" % (datetime.datetime.now().isoformat(), d)); log.flush()
    if mode == "callb":
        log.write("cal refresh skipped (TIER1_SKIP_CAL_REFRESH=1)\\n"); log.close()
        sh = datetime.timezone(datetime.timedelta(hours=8))
        json.dump(dict(date=d, overall="ok", steps={"daily_pull": {"status": "ok", "sec": 1}}, finished=datetime.datetime.now(sh).isoformat()),
                  open("logs/nightly/%s_summary.json" % d, "w"))
        sys.exit(0)
    subprocess.Popen([sys.executable, "scripts/acquire/tier1_pull.py", "extend", d], stdout=log, stderr=subprocess.STDOUT)
elif mode2 in ("orphb", "finalcal", "rcb"):
    sh = datetime.timezone(datetime.timedelta(hours=8))
    if mode2 == "orphb":  # 双 fork + setsid：PPID=1、启动晚于本次调用、cmdline 含 scripts/acquire/
        subprocess.Popen([sys.executable, "scripts/acquire/orphan_b.py"]).wait()
    sp = "logs/nightly/%s_summary.json" % d
    prev = json.load(open(sp)).get("steps", {}) if os.path.exists(sp) else {}
    prev.update(dict((k, {"status": "ok", "sec": 1}) for k in steps.split(",")))
    json.dump(dict(date=d, overall="ok", steps=prev, finished=datetime.datetime.now(sh).isoformat()), open(sp + ".tmp", "w")); os.replace(sp + ".tmp", sp)
    sys.exit(1 if mode2 == "rcb" else 0)
else:
    subprocess.Popen([sys.executable, "scripts/acquire/tier3_daily_snapshot.py", "--date", d])
while True:
    time.sleep(3600)
""")
w(TMP + "/scripts/acquire/tier1_pull.py", """import os, signal, sys, time
print("ENV TSPRO_RELAY_TIMEOUT=%s SOURCE=%s TIER1_SKIP_CAL_REFRESH=%s" % (os.environ.get("TSPRO_RELAY_TIMEOUT"), os.environ.get("SOURCE"), os.environ.get("TIER1_SKIP_CAL_REFRESH")), flush=True)
if os.environ.get("TIER1_SKIP_CAL_REFRESH") == "1":
    print("cal refresh skipped (TIER1_SKIP_CAL_REFRESH=1)", flush=True)
if os.environ.get("FAKE_CORRUPT_CAL") == "1":  # 故障注入：模拟非原子重写把假日历写坏
    open("trade_cal.parquet", "w").write("CORRUPTED by fake tier1\\n")
signal.signal(signal.SIGTERM, signal.SIG_IGN)
while True:
    time.sleep(3600)
""")
w(TMP + "/scripts/acquire/tier3_daily_snapshot.py", """import subprocess, sys, time
if "--child" not in sys.argv:
    subprocess.Popen([sys.executable, "scripts/acquire/tier3_daily_snapshot.py", "--child"])
while True:
    time.sleep(3600)
""")
w(TMP + "/scripts/acquire/orphan_b.py", "import os, time\nif os.fork() == 0:\n    os.setsid(); time.sleep(300)\nelse:\n    os._exit(0)\n")
for d_ in ("logs/nightly", "here", "markers", "raw", "output"):
    os.makedirs(TMP + "/" + d_, exist_ok=True)
m.ROOT = TMP; m.RAW = TMP + "/raw"; m.HERE = TMP + "/here"; m.MARK_DIR = TMP + "/markers"; m.QUIET_LOCK = TMP + "/RESEARCH_QUIET.lock"
w(TMP + "/trade_cal.parquet", "fake trade_cal v1\n"); m.TRADE_CAL = TMP + "/trade_cal.parquet"; m.PIN = m.sha256(m.TRADE_CAL)
w(TMP + "/pit.parquet", "fake pit\n"); m.PIT_CAL = {TMP + "/pit.parquet": m.sha256(TMP + "/pit.parquet")}
w(TMP + "/closure.json", "{}\n"); m.FROZEN = {TMP + "/closure.json": m.sha256(TMP + "/closure.json")}
m.CAL_RECHECK_S = 1
m.DAILY_PULL_MAX_MIN = 0.15   # 测试上限 9 秒（生产 30 分钟）
BUDGET = 0.15                 # call B 测试预算 9 秒（生产 75 分钟）
def fake_ok():
    m.CFG["expires"] = m.now() + datetime.timedelta(hours=1); m.CFG["budget"] = BUDGET; m.CFG["source_relay"] = False
    m.R["checks"]["ok"] = dict(path="fake", sha256="fake")
    return {"allow_daily_pull_retry_20261019": "2", "allow_profile_relaxed_20261019": "true", "allow_quarantine_mv_daily_raw_20261019": "true"}, None
def fake_lock(kv, dry=False):
    w(m.QUIET_LOCK, "purpose=nightly_20261019\n"); m.R["quiet"].update(lock_path=m.QUIET_LOCK, existed_at_check=True, created_by_data=False, lock_sha256=m.sha256(m.QUIET_LOCK)); return None
def fake_tool(args, log_name, kind, phase_deadline=None):
    if args[0] == m.RESTORE:
        return 1, "fake cal_restore_v2 拒绝（迫使驱动走 restore_native）"
    if MODE == "finalcal" and args[0] == m.SNAP and args[1] == "snap" and "snap_after" in args[3]:
        open(m.TRADE_CAL, "w").write("CORRUPTED after call B (fake snap_after)\n")  # 故障注入：收尾前日历被改
    return 0, "fake %s" % kind
def fake_cal_info(p):
    return dict(path=p, rows=1, sha256=m.sha256(p), date_range=["20261019", "20261019"]), {"20261019"}
m.marker_precheck = lambda: None
m.check_ok = fake_ok
m.check_pins = lambda: None
m.guarded_check = lambda: None
m.pgrep_gates = lambda tag: None
m.start_window_check = lambda: None
m.in_blackout = lambda t=None: False
m.ensure_lock = fake_lock
m.quiet_gate = lambda tag, full=True: None
m.run_tool = fake_tool
m.cal_info = fake_cal_info
if MODE in ("callb", "orphb", "finalcal", "rcb"):
    m.raw_check = lambda: ([], [], {"fake": True})
if MODE == "rss":
    m.RSS_STOP_KB = 1
if MODE == "kill":
    m.DAILY_PULL_MAX_MIN = 2   # 让测试先 SIGKILL 驱动，再看例程兜底
os.environ["FAKE_MODE"] = "callb" if MODE in ("orphb", "finalcal", "rcb") else MODE
os.environ["FAKE_MODE2"] = MODE
if MODE in ("cap", "sig", "kill", "rss"):
    os.environ["FAKE_CORRUPT_CAL"] = "1"
prof = "relaxed" if MODE == "rss" else "strict"
sys.argv = [DRV, "--profile", prof]
m.main()
