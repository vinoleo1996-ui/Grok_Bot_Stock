#!/usr/bin/python3
# -*- coding: utf-8 -*-
# run_backfill_r_v3_1.py 补充自测 c（QuantLab Data，2026-10-18；由 b e3d04311 复制，只改：替身子进程在孙退出后仍存活、断言恰好四个信号、新增 B3b；待 Arch 签 .ok；未运行）。
# 覆盖 v3.1 首次自测未演练的路径：两级子孙（子、孙）存活后才触发停树；断言信号顺序 SIGSTOP nightly → 孙 → 子 → KILL nightly；
# 每个信号前核 cmdline+ppid；不起下一步；全部替身进程消失；orphans_run1 为空；P3-B 反例（cmdline 不含 scripts/acquire/ 被拒）；P3-2 二次打开失败。
# 只在 mkdtemp（前缀取 .ok 的 out_dir_prefix）下工作；不读写项目数据；不起真 nightly；不触网。
# 只对本自测（及其起的替身树）产生的 PID 发信号：os.kill 被包装，PID 不在 SPAWNED 集合即断言失败、不发信号。
# 用法：cd /tmp && PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 /workspace/QuantLab/docs/v2/audit/backfill_1014_1016/selftest_run_backfill_r_v3_1_c.py </dev/null
import datetime, importlib.util, json, os, re, signal, subprocess, sys, tempfile, time

ROOT = "/workspace/QuantLab"
OK = ROOT + "/output/ai_factory/ARCH_SELFTEST_DATA_BACKFILL_R_V3_1_C.ok"
RUNNER = ROOT + "/docs/v2/audit/backfill_1014_1016/run_backfill_r_v3_1.py"
CONFIRM_MAX_S = 30


def enforce(modes):
    if not os.path.isfile(OK):
        sys.exit("SELFTEST_BLOCKED .ok 不存在 %s" % OK)
    kv = {}
    for ln in open(OK, encoding="utf-8"):
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        m = re.match(r"^([A-Za-z0-9_]+)\s*[:=]\s*(.*)$", ln)
        if not m or "#" in m.group(2):
            sys.exit("SELFTEST_BLOCKED .ok 行无法解析或含行内注释：%r" % ln)
        kv[m.group(1)] = m.group(2).strip()
    if kv.get("scope") not in modes:
        sys.exit("SELFTEST_BLOCKED scope=%r" % kv.get("scope"))
    try:
        exp = datetime.datetime.fromisoformat(kv.get("expires_et", ""))
    except Exception:
        sys.exit("SELFTEST_BLOCKED expires_et 无法解析")
    if exp.tzinfo is None or exp <= datetime.datetime.now(exp.tzinfo):
        sys.exit("SELFTEST_BLOCKED expires_et 无时区或已过期")
    if kv.get("allow_selftest", "").lower() != "true" or kv.get("allow_real_data", "").lower() != "false":
        sys.exit("SELFTEST_BLOCKED allow_selftest/allow_real_data 不符")
    for k, v in kv.items():
        if k.startswith("allow_") and k not in ("allow_selftest", "allow_real_data") and v.lower() != "false":
            sys.exit("SELFTEST_BLOCKED %s 不是 false" % k)
    pre = kv.get("out_dir_prefix", "")
    if not pre.startswith("/tmp/") or os.path.realpath(os.path.dirname(pre)) != "/tmp":
        sys.exit("SELFTEST_BLOCKED out_dir_prefix 不在 /tmp 下：%r" % pre)
    return kv


KV = enforce(modes=["selftest"])
spec = importlib.util.spec_from_file_location("rbr31", RUNNER)
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)  # 只定义常量与函数，不调用 main()

PRE = KV["out_dir_prefix"]
W = tempfile.mkdtemp(prefix=os.path.basename(PRE) + "_", dir=os.path.dirname(PRE))
assert W.startswith(PRE + "_"), W
for d in ("snap", "scripts/acquire", "other", "logs/nightly", "pids"):
    os.makedirs(os.path.join(W, d))
M.ROOT = W; M.SNAP_DIR = os.path.join(W, "snap"); M.BK = os.path.join(W, "bk")
M.QUIET_LOCK = os.path.join(W, "RESEARCH_QUIET.lock")
RES = []
ACQ_W = os.path.join(W, "scripts/acquire") + "/"


def case(name, ok, detail=""):
    RES.append((name, bool(ok), detail)); print("%s %s %s" % ("PASS" if ok else "FAIL", name, detail), flush=True)


def wfile(rel, text):
    p = os.path.join(W, rel)
    with open(p, "x") as fh:
        fh.write(text)
    return p


def readpid(name):
    try:
        return int(open(os.path.join(W, "pids", name)).read().strip())
    except Exception:
        return None


# ---------- 信号守卫与调用日志 ----------
SPAWNED = set()
CALLS = []  # ("cmdline"|"ppid"|"kill", pid, sig)
KSTATE = []  # (pid, sig, 发信号前 /proc/<pid>/stat 状态)
_real_kill = os.kill
_real_cmdline = M.cmdline
_real_ppid = M.ppid


def refresh_spawned():
    for n in ("child.pid", "grandchild.pid"):
        p = readpid(n)
        if p:
            SPAWNED.add(p)
    if M.CFG.get("npid"):
        SPAWNED.add(M.CFG["npid"])


def guarded_kill(pid, sig):
    refresh_spawned()
    assert pid in SPAWNED, "拒绝：试图对非本自测产生的 PID %r 发信号 %r（SPAWNED=%r）" % (pid, sig, sorted(SPAWNED))
    CALLS.append(("kill", pid, int(sig)))
    KSTATE.append((pid, int(sig), M.proc_state(pid)))
    return _real_kill(pid, sig)


def log_cmdline(pid):
    CALLS.append(("cmdline", pid, None)); return _real_cmdline(pid)


def log_ppid(pid):
    CALLS.append(("ppid", pid, None)); return _real_ppid(pid)


os.kill = guarded_kill  # runner 与 subprocess 都经由 os.kill
M.cmdline = log_cmdline; M.ppid = log_ppid

print("SELFTEST_B start", datetime.datetime.now().astimezone().isoformat(timespec="seconds"), "actual_dir", W, "out_dir_prefix", PRE, "ok_keys", sorted(KV), flush=True)

# ---------- 替身树：nightly → 子（acquire）→ 孙（acquire） ----------
GC = wfile("scripts/acquire/fake_grandchild.py",
           "import os, time\n"
           "open(%r, \"w\").write(str(os.getpid()))\n"
           "while True: time.sleep(1)\n" % os.path.join(W, "pids/grandchild.pid"))
CH = wfile("scripts/acquire/fake_child.py",
           "import os, subprocess, sys, time\n"
           "open(%r, \"w\").write(str(os.getpid()))\n"
           "p = subprocess.Popen([sys.executable, %r], stdin=subprocess.DEVNULL)\n"
           "while True:\n"
           "    p.poll()  # 非阻塞收尸：孙退出后子进程继续存活，只因 SIGTERM（默认处理）退出\n"
           "    time.sleep(0.2)\n" % (os.path.join(W, "pids/child.pid"), GC))
wfile("scripts/nightly_update.py",
      "import subprocess, sys\n"
      "for k in range(3):\n"
      "    subprocess.call([sys.executable, %r], stdin=subprocess.DEVNULL)\n"
      "    open(%r, \"a\").write(\"NEXT_STEP %%d\\n\" %% k)\n"
      "    print(\"NEXT_STEP\", k, flush=True)\n" % (CH, os.path.join(W, "next_step.log")))

CONF = {"t0": None, "confirmed_at": None, "child": None, "grandchild": None, "timeout": False}


def tree_confirmed():
    npid = M.CFG.get("npid")
    c, g = readpid("child.pid"), readpid("grandchild.pid")
    if not (npid and c and g):
        return False
    ok = (M.alive(c) and M.alive(g) and _real_ppid(c) == npid and _real_ppid(g) == c
          and ACQ_W in _real_cmdline(c) and ACQ_W in _real_cmdline(g))
    if ok and CONF["confirmed_at"] is None:
        CONF.update(confirmed_at=time.time(), child=c, grandchild=g)
        print("TREE_CONFIRMED npid=%d child=%d(stat=%s) grandchild=%d(stat=%s)" % (npid, c, M.proc_state(c), g, M.proc_state(g)), flush=True)
    return ok


_real_vmrss = M.vmrss_kb


def gated_vmrss(pid):
    # 子、孙都经 /proc/<pid>/stat 确认存活前返回 0（不触发停树）；确认后返回真实 RSS（> RSS_STOP_KB=1，触发停树）
    if CONF["t0"] is None:
        CONF["t0"] = time.time()
    if tree_confirmed():
        return max(_real_vmrss(pid), 2)
    if time.time() - CONF["t0"] > CONFIRM_MAX_S:
        CONF["timeout"] = True
        return max(_real_vmrss(pid), 2)
    return 0


M.vmrss_kb = gated_vmrss
M.TERM_WAIT_S = 3; M.SAMPLE_S = 0.5; M.RSS_STOP_KB = 1
M.LATEST_START = {1: (23, 59), 2: (23, 59)}; M.BLACKOUT = ((0, 0), (0, 0)); M.HARD_STOP = (23, 59)
M.CFG["expires"] = M.now() + datetime.timedelta(hours=1)

cmd = [M.PY, "scripts/nightly_update.py", "--date", "20261016", "--steps", "cyq"]
r = M.run(1, cmd)
npid = r["npid"]; c, g = CONF["child"], CONF["grandchild"]
case("B1 子与孙在停树前已确认存活", CONF["confirmed_at"] is not None and not CONF["timeout"], json.dumps(CONF))
st = M.R["checks"]["stop_tree"][-1]["steps"]
want_steps = [("SIGSTOP", npid), ("TERM_KILL", g), ("TERM_KILL", c), ("SIGKILL", npid)]
case("B2 stop_tree 记录顺序 SIGSTOP nightly → 孙 → 子 → SIGKILL nightly", [(a, b) for a, b, _ in st] == want_steps, repr(st))
case("B2 每步结果为 sent/term_ok/killed", all(x[2] in ("sent", "term_ok", "killed") for x in st), repr(st))
kills = [(p, s) for k, p, s in CALLS if k == "kill"]
first = [x for x in kills if x[0] in (npid, c, g)]
seq = [(p, s) for p, s in first if s != signal.SIGKILL or p == npid]
exp_seq = [(npid, int(signal.SIGSTOP)), (g, int(signal.SIGTERM)), (c, int(signal.SIGTERM)), (npid, int(signal.SIGKILL))]
case("B3 恰好四个信号：STOP nightly → TERM 孙 → TERM 子 → KILL nightly", kills == exp_seq, repr(kills))
ks = [x for x in KSTATE if x[0] == c and x[1] == int(signal.SIGTERM)]
case("B3b 子进程收到 TERM 时存活（非 Z）", len(ks) == 1 and ks[0][2] not in (None, "Z"), repr(KSTATE))
# B4：每个 kill 之前（自上一个 kill 之后）必须有对同一 PID 的 cmdline 与 ppid 读取
okb4, prev, det = True, 0, []
for i, (k, p, s) in enumerate(CALLS):
    if k != "kill":
        continue
    seg = CALLS[prev:i]
    has_c = any(x[0] == "cmdline" and x[1] == p for x in seg); has_p = any(x[0] == "ppid" and x[1] == p for x in seg)
    det.append((p, s, has_c, has_p)); okb4 = okb4 and has_c and has_p; prev = i + 1
case("B4 每个信号前都核了 cmdline 与 ppid", okb4 and det, repr(det))
ev_sig = [e for e in M.R["events"] if " SIGNAL " in e]
case("B4 事件日志带 ppid 与 cmd", all("ppid=" in e for e in ev_sig if "SIGNAL S" in e), "\n".join(ev_sig))
case("B5 停树后未起下一步", not os.path.exists(os.path.join(W, "next_step.log")) and "NEXT_STEP" not in open(r["out"], encoding="utf-8").read(), "")
time.sleep(1)
case("B6 替身进程全部消失（Z 视为退出）", all(not M.alive(x) for x in (npid, c, g) if x), repr([(x, M.proc_state(x)) for x in (npid, c, g) if x]))
case("B7 orphans_run1 为空", M.R["checks"].get("orphans_run1") == [], repr(M.R["checks"].get("orphans_run1")))
case("B8 rc 为 -9 且 wait 未超时", r["rc"] == -9 and not r["wait_timeout"], "rc=%r wait_timeout=%r" % (r["rc"], r["wait_timeout"]))

# ---------- P3-2：二次打开同名 .out 必须失败 ----------
try:
    open(r["out"], "x"); case("P3-2 二次 open(x) 抛 FileExistsError", False, r["out"])
except FileExistsError:
    case("P3-2 二次 open(x) 抛 FileExistsError", True, r["out"])

# ---------- P3-B 反例：cmdline 不含 scripts/acquire/ 的子进程被拒 ----------
NA = wfile("other/fake_not_acquire.py", "import time\nwhile True: time.sleep(1)\n")
q = subprocess.Popen([sys.executable, NA], stdin=subprocess.DEVNULL)
SPAWNED.add(q.pid)
t0 = time.time()
while M.proc_state(q.pid) is None and time.time() - t0 < 5:
    time.sleep(0.1)
nk = len([x for x in CALLS if x[0] == "kill"])
res = M.signal_exact(q.pid, signal.SIGTERM, M.ACQ_MARK, os.getpid())
nk2 = len([x for x in CALLS if x[0] == "kill"])
case("P3-B cmdline 不含 scripts/acquire/ → refused", res == "refused", "res=%r" % res)
case("P3-B 未发任何信号", nk2 == nk, "kills %d→%d" % (nk, nk2))
case("P3-B 拒绝已写日志", any("refuse pid=%d" % q.pid in e for e in M.R["events"]), "")
case("P3-B 进程仍存活", M.alive(q.pid), "stat=%s" % M.proc_state(q.pid))
q.terminate()  # 自测按自己起的确切 PID 清理（经 guarded_kill，PID 在 SPAWNED 中）
try:
    q.wait(timeout=10)
except subprocess.TimeoutExpired:
    q.kill(); q.wait(timeout=10)
case("P3-B 自测清理后已退出", not M.alive(q.pid), "rc=%r" % q.returncode)

# ---------- 守卫自检 ----------
case("G1 所有被发信号的 PID 都在 SPAWNED 中", all(p in SPAWNED for k, p, s in CALLS if k == "kill"), repr(sorted(SPAWNED)))
try:
    os.kill(1, 0); case("G2 守卫拒绝非本自测 PID", False)
except AssertionError:
    case("G2 守卫拒绝非本自测 PID", True, "pid=1 未发信号")

print("STOP_TREE_RECORDS", json.dumps(M.R["checks"].get("stop_tree"), ensure_ascii=False))
print("ORPHANS_RUN1", json.dumps(M.R["checks"].get("orphans_run1"), ensure_ascii=False))
print("KILL_CALLS", json.dumps(kills))
n_fail = sum(1 for _, ok, _ in RES if not ok)
print("SELFTEST_B end pass=%d fail=%d actual_dir=%s" % (len(RES) - n_fail, n_fail, W))
sys.exit(1 if n_fail else 0)
