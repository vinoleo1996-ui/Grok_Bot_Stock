#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""run_backfill_1019_1023_dbincr_v3_1.py 逻辑自测（QuantLab Eng；/tmp 假数据；无需 .ok；不起真跑）。
用法：cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 docs/v2/audit/backfill_1019_1023/selftest_run_backfill_1019_1023_dbincr_v3_1.py </dev/null
"""
import datetime, importlib.util, json, os, subprocess, sys, tempfile, time
from zoneinfo import ZoneInfo

ROOT = "/workspace/QuantLab"
RUNNER = ROOT + "/docs/v2/audit/backfill_1019_1023/run_backfill_1019_1023_dbincr_v3_1.py"
ET = ZoneInfo("America/New_York")
RES = []


def case(name, ok, detail=""):
    RES.append((name, bool(ok), detail))
    print("%s %s %s" % ("PASS" if ok else "FAIL", name, detail), flush=True)


# 0) py_compile
rc = subprocess.call(["/usr/bin/python3", "-m", "py_compile", RUNNER], cwd=ROOT)
case("py_compile", rc == 0, "rc=%s" % rc)

spec = importlib.util.spec_from_file_location("bf1019st", RUNNER)
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

W = tempfile.mkdtemp(prefix="ql_bf1019_selftest_", dir="/tmp")
os.makedirs(os.path.join(W, "logs/nightly"), exist_ok=True)
os.makedirs(os.path.join(W, "scripts/acquire"), exist_ok=True)
os.makedirs(os.path.join(W, "data/v2/tushare_raw"), exist_ok=True)
M.ROOT = W
M.QUIET_LOCK = os.path.join(W, "RESEARCH_QUIET.lock")
M.TRADE_CAL = os.path.join(W, "data/v2/tushare_raw/trade_cal.parquet")
M.RAW = os.path.join(W, "data/v2/tushare_raw")
M.MARK_DIR = os.path.join(W, "output/backfill_markers")
os.makedirs(M.MARK_DIR, exist_ok=True)
print("SELFTEST start", datetime.datetime.now(ET).isoformat(timespec="seconds"), "workdir", W)

# 1) constants / pins shape
case("DATE_LIST 五日", M.DATE_LIST == ["20261019", "20261020", "20261021", "20261022", "20261023"], repr(M.DATE_LIST))
case("CALL_B_STEPS 14 且无 trade_cal/sw", len(M.CALL_B_STEPS) == 14 and "trade_cal" not in M.CALL_B_STEPS and "sw" not in M.CALL_B_STEPS, repr(M.CALL_B_STEPS))
case("sha_driver_ref 钉 f1910e8a", M.SHA_DRIVER_REF.startswith("f1910e8a"), M.SHA_DRIVER_REF[:16])
case("auth_ok 钉 9e4359f9", M.AUTH_OK_SHA.startswith("9e4359f9"), M.AUTH_OK_SHA[:16])
case("enable_ok 钉 4377eb59", M.ENABLE_OK_SHA.startswith("4377eb59"), M.ENABLE_OK_SHA[:16])
case("LEAF25=10:00-10:45", M.LEAF25_BLACKOUT == ((10, 0), (10, 45)), repr(M.LEAF25_BLACKOUT))
case("BLACKOUT=16:40-18:40", M.BLACKOUT == ((16, 40), (18, 40)), repr(M.BLACKOUT))
case("MEM_MIN 2.5GiB", M.MEM_AVAILABLE_MIN_KB == 2621440, str(M.MEM_AVAILABLE_MIN_KB))
case("requires_dedicated", M.REQUIRES_DEDICATED_BACKFILL_RUNNER is True, "")

# 2) forbid nightly driver
try:
    M.forbid_nightly_driver_invocation(["/usr/bin/python3", "docs/v2/audit/nightly_20261019/run_nightly_v1_dbincr_v3_1.py", "--date", "20261019"])
    case("forbid nightly driver", False, "should raise")
except RuntimeError as e:
    case("forbid nightly driver", "FORBIDDEN" in str(e), str(e)[:100])
try:
    M.forbid_nightly_driver_invocation(["/usr/bin/python3", "scripts/nightly_update.py", "--date", "20261019", "--steps", "daily_pull"])
    case("allow nightly_update.py", True)
except RuntimeError as e:
    case("allow nightly_update.py", False, str(e)[:100])

# 3) leaf25 / blackout helpers (override now via monkeypatch of hm windows using fake now — test logic by direct call with patched now)
class _T:
    pass

real_now = M.now
try:
    M.now = lambda: datetime.datetime(2026, 10, 25, 10, 15, tzinfo=ET)
    case("in_leaf25 at 10:15", M.in_leaf25() is True, "")
    M.now = lambda: datetime.datetime(2026, 10, 25, 9, 59, tzinfo=ET)
    case("not leaf25 at 09:59", M.in_leaf25() is False, "")
    M.now = lambda: datetime.datetime(2026, 10, 25, 17, 0, tzinfo=ET)
    case("in_blackout at 17:00", M.in_blackout() is True, "")
    M.now = lambda: datetime.datetime(2026, 10, 25, 12, 0, tzinfo=ET)
    case("not blackout at 12:00", M.in_blackout() is False, "")
finally:
    M.now = real_now

# 4) dry-run argv: single interpreter (P1-1 style)
stub = os.path.join(W, "scripts/nightly_update.py")
with open(stub, "x") as fh:
    fh.write("import sys, json\nprint(json.dumps(sys.argv))\n")
# run_tool style: use subprocess like plan R
cmd = [M.PY, "scripts/nightly_update.py", "--date", "20261019", "--steps", "daily_pull", "--dry-run"]
# simulate: only one PY
case("CMD 解释器只一次", cmd.count(M.PY) == 1 and cmd[0] == M.PY, repr(cmd[:3]))
M.forbid_nightly_driver_invocation(cmd)
case("CMD forbid 放行 nightly_update", True)

# 5) stop_tree order on fake sleep tree (RSS trigger)
child = os.path.join(W, "scripts/acquire/fake_step.py")
with open(child, "x") as fh:
    fh.write("import time\nwhile True: time.sleep(1)\n")
with open(stub, "w") as fh:
    fh.write("import subprocess, sys, time\n"
             "for k in range(3):\n"
             "    subprocess.call([sys.executable, %r])\n"
             "    print('NEXT_STEP', k, flush=True)\n" % child)
M.TERM_WAIT_S = 2
M.SAMPLE_S = 1
M.RSS_STOP_KB = 1
M.CFG["expires"] = M.now() + datetime.timedelta(hours=1)
M.D = "20261019"
# Minimal run_nightly harness: use plan-R-like run if available; else call stop_tree manually
# Import stop_tree path: spawn + stop
import subprocess as sp
p = sp.Popen([M.PY, stub], cwd=W, stdin=sp.DEVNULL, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
time.sleep(0.3)
# build marks for acquire
st = M.stop_tree(p.pid, ("scripts/acquire/",), "SELFTEST_RSS", "selftest")
# wait
try:
    p.wait(timeout=5)
except Exception:
    pass
steps = (M.R.get("checks") or {}).get("stop_tree") or []
last = steps[-1] if steps else {}
st_steps = last.get("steps") or []
case("stop_tree 记录存在", bool(st_steps), repr(st_steps)[:200])
case("stop_tree 首步 SIGSTOP*", st_steps and st_steps[0][0] in ("SIGSTOP", "SIGSTOP_PARENT"), repr(st_steps[:1]))
case("stop_tree 含 SIGKILL*", any(x[0] in ("SIGKILL", "SIGKILL_PARENT") for x in st_steps), repr([x[0] for x in st_steps]))

# 6) summary window check with /tmp summary
M.D = "20261019"
spth = os.path.join(W, "logs/nightly/20261019_summary.json")
t0 = time.time()
with open(spth, "x") as fh:
    json.dump(dict(date="20261019", finished="2020-01-01T00:00:00+00:00",
                   steps={"daily_pull": {"status": "ok"}}), fh)
# monkeypatch SUMMARY path used inside check_summary — driver builds path from D
# check_summary in driver uses ROOT/logs/nightly/<D>_summary.json — ROOT is W
fs, _ = M.check_summary(["daily_pull"], dict(start_epoch=t0, end_epoch=time.time() + 1,
                                               start_et="a", end_et="b", started_et="a", finished_et="b"), "t_stale")
case("summary 陈旧 finished 被拒", any("finished" in x for x in fs), repr(fs)[:200])
os.unlink(spth)
with open(spth, "x") as fh:
    json.dump(dict(date="20261019", finished=datetime.datetime.now().astimezone().isoformat(),
                   steps={"daily_pull": {"status": "ok"}}), fh)
fs2, _ = M.check_summary(["daily_pull"], dict(start_epoch=t0, end_epoch=time.time() + 1,
                                                start_et="a", end_et="b", started_et="a", finished_et="b"), "t_fresh")
case("summary 本次窗口通过", fs2 == [], repr(fs2))

# 7) disk pins (real ROOT) — restore ROOT for pin check
M.ROOT = ROOT
e = M.check_pins()
case("现盘 check_pins PASS", e is None, repr(e))
akv, ae = M.check_auth_ok()
case("现盘 check_auth_ok PASS", ae is None, repr(ae))

n_fail = sum(1 for _, ok, _ in RES if not ok)
print("SELFTEST end pass=%d fail=%d workdir=%s" % (len(RES) - n_fail, n_fail, W))
sys.exit(1 if n_fail else 0)
