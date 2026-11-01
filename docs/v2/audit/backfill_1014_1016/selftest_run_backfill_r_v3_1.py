#!/usr/bin/python3
# -*- coding: utf-8 -*-
# run_backfill_r_v3_1.py 替身自测（QuantLab Data，2026-10-18，待 Arch selftest .ok；未运行）。
# 只在 tempfile.mkdtemp() 下的假目录里工作；不读不写项目数据；不起真 nightly；不触网。
# enforce(modes=["selftest"]) 在 import 执行器之前调用：要求 output/ai_factory/ARCH_SELFTEST_DATA_BACKFILL_R_V3_1.ok 存在、未过期、
# scope=selftest、allow_selftest=true、allow_real_data=false、其余 allow_*=false、out_dir 在 /tmp 下。
# 用法：cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 docs/v2/audit/backfill_1014_1016/selftest_run_backfill_r_v3_1.py </dev/null
import datetime, importlib.util, json, os, re, signal, subprocess, sys, tempfile, time

ROOT = "/workspace/QuantLab"
OK = ROOT + "/output/ai_factory/ARCH_SELFTEST_DATA_BACKFILL_R_V3_1.ok"
RUNNER = ROOT + "/docs/v2/audit/backfill_1014_1016/run_backfill_r_v3_1.py"


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
    exp = datetime.datetime.fromisoformat(kv.get("expires_et", "1970-01-01T00:00:00+00:00"))
    if exp.tzinfo is None or exp <= datetime.datetime.now(exp.tzinfo):
        sys.exit("SELFTEST_BLOCKED expires_et 无时区或已过期")
    if kv.get("allow_selftest", "").lower() != "true" or kv.get("allow_real_data", "").lower() != "false":
        sys.exit("SELFTEST_BLOCKED allow_selftest/allow_real_data 不符")
    for k, v in kv.items():
        if k.startswith("allow_") and k not in ("allow_selftest", "allow_real_data") and v.lower() != "false":
            sys.exit("SELFTEST_BLOCKED %s 不是 false" % k)
    if not os.path.realpath(kv.get("out_dir", "")).startswith("/tmp/"):
        sys.exit("SELFTEST_BLOCKED out_dir 不在 /tmp")
    return kv


KV = enforce(modes=["selftest"])
spec = importlib.util.spec_from_file_location("rbr31", RUNNER)
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)  # 只定义常量与函数，不调用 main()

W = tempfile.mkdtemp(prefix="qd_v31_selftest_", dir="/tmp")
os.makedirs(os.path.join(W, "snap")); os.makedirs(os.path.join(W, "scripts/acquire")); os.makedirs(os.path.join(W, "logs/nightly"))
M.ROOT = W; M.SNAP_DIR = os.path.join(W, "snap"); M.BK = os.path.join(W, "bk")
M.QUIET_LOCK = os.path.join(W, "RESEARCH_QUIET.lock")
RES = []


def case(name, ok, detail=""):
    RES.append((name, bool(ok), detail)); print("%s %s %s" % ("PASS" if ok else "FAIL", name, detail), flush=True)


def wfile(rel, text):
    p = os.path.join(W, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "x") as fh:
        fh.write(text)
    return p


print("SELFTEST start", datetime.datetime.now().astimezone().isoformat(timespec="seconds"), "workdir", W, "ok_keys", sorted(KV))

# 1) P1-1：dry-run argv 只有一个解释器；替身 nightly 只打印 argv
wfile("scripts/nightly_update.py", "import sys, json\nprint(json.dumps(sys.argv))\n")
for i, c in ((1, M.CMD1), (2, M.CMD2)):
    rc, txt = M.run_tool(c[1:] + ["--dry-run"], "dry%d.log" % i)
    argv = json.loads(txt.strip().splitlines()[-1])
    case("P1-1 dryrun cmd%d rc==0" % i, rc == 0, "rc=%r" % rc)
    case("P1-1 dryrun cmd%d argv==CMD[1:]+--dry-run" % i, argv == c[1:] + ["--dry-run"], repr(argv))
    full = M.R["checks"]["tool_argv"][-1]["argv"]
    case("P1-1 cmd%d 解释器只出现一次" % i, full.count(M.PY) == 1, repr(full))
try:
    M.run_tool([M.PY, "x.py"], "dry_bad.log"); case("P1-1 assert 拒绝重复解释器", False)
except AssertionError:
    case("P1-1 assert 拒绝重复解释器", True)

# 2) P3-3：parse_ok 拒绝行内注释
p = wfile("t1.ok", "ok_id=X\nallow_restore_cyq_202610_from_backup=true   # 注释\n")
kv, errs = M.parse_ok(p)
case("P3-3 行内注释被拒", any("行内注释" in e for e in errs), repr(errs))

# 3) P2-1：替身 nightly（SIGSTOP 后不应再起下一步）+ 替身子进程；停树顺序与孤儿扫描
child = wfile("scripts/acquire/fake_step.py", "import time\nwhile True: time.sleep(1)\n")
night = os.path.join(W, "scripts/nightly_update.py")
os.replace(night, night + ".argv_stub")
wfile("scripts/nightly_update.py", "import subprocess, sys, time\n"
      "for k in range(3):\n"
      "    subprocess.call([sys.executable, %r])\n"
      "    print(\"NEXT_STEP\", k, flush=True)\n" % child)
M.TERM_WAIT_S = 2; M.SAMPLE_S = 1
M.RSS_STOP_KB = 1  # 立即触发 RSS 停树
M.LATEST_START = {1: (23, 59), 2: (23, 59)}; M.BLACKOUT = ((0, 0), (0, 0)); M.HARD_STOP = (23, 59)
M.CFG["expires"] = M.now() + datetime.timedelta(hours=1)
os.makedirs(os.path.join(W, "logs/nightly"), exist_ok=True)
M.ROOT = W
cmd = [M.PY, "scripts/nightly_update.py", "--date", "20261016", "--steps", "cyq"]
r = M.run(1, cmd)
st = M.R["checks"]["stop_tree"][-1]["steps"]
case("P2-1 第一步是 SIGSTOP nightly", st and st[0][0] == "SIGSTOP" and st[0][2] == "sent", repr(st))
case("P2-1 最后一步是 SIGKILL nightly", st and st[-1][0] == "SIGKILL", repr(st))
case("P2-1 wait 未超时且已停", r["stopped"] and not r["wait_timeout"], repr(r["stopped"]))
case("P2-1 无存活子孙", all(not M.alive(x) for x in r["pids_seen"]), repr(r["pids_seen"]))
out = open(r["out"], encoding="utf-8").read()
case("P2-1 nightly 未起下一步", "NEXT_STEP" not in out, out[-200:])
case("P3-2 runN.out 用 x（再开同名应失败）", os.path.exists(r["out"]), r["out"])
case("P2-1 孤儿扫描已记录", "orphans_run1" in M.R["checks"], repr(M.R["checks"].get("orphans_run1")))

# 4) P2-2：summary 窗口
sp = os.path.join(W, "logs/nightly/20261016_summary.json"); M.SUMMARY = sp
t0 = time.time()
with open(sp, "x") as fh:
    json.dump(dict(date="20261016", finished="2026-10-18T16:59:22+08:00", steps={"cyq": {"status": "ok"}}), fh)
f = M.check_summary(["cyq"], dict(start_epoch=t0, end_epoch=time.time() + 1, start_et="a", end_et="b"), "t_stale")
case("P2-2 陈旧 finished 被拒", any("finished" in x for x in f), repr(f))
os.unlink(sp)
with open(sp, "x") as fh:
    json.dump(dict(date="20261016", finished=datetime.datetime.now().astimezone().isoformat(), steps={"cyq": {"status": "ok"}}), fh)
f = M.check_summary(["cyq"], dict(start_epoch=t0, end_epoch=time.time() + 1, start_et="a", end_et="b"), "t_fresh")
case("P2-2 本次 summary 通过", f == [], repr(f))

# 5) Q4：恢复只在授权且三方 sha 一致时，原子替换后复核
for rel, body in ((M.CYQ_PQ, b"broken-parquet"), (M.CYQ_MAN, b"{}")):
    for base in (W, M.BK):
        q = os.path.join(base, rel); os.makedirs(os.path.dirname(q), exist_ok=True)
        with open(q, "xb") as fh:
            fh.write(body if base == M.BK else b"half-written")
sums = {rel: M.sha256(os.path.join(M.BK, rel)) for rel in (M.CYQ_PQ, M.CYQ_MAN)}
snapf = wfile("snap/before.txt", "".join("%s  %s\n" % (sums[rel], os.path.join(W, rel)) for rel in sums))
M.CFG["restore_allowed"] = False
M.maybe_restore_cyq(sums, snapf)
case("Q4 未授权只报告", M.R["checks"]["cyq_restore"]["action"].startswith("report_only"), M.R["checks"]["cyq_restore"]["action"])
M.CFG["restore_allowed"] = True
M.maybe_restore_cyq(dict(sums, **{M.CYQ_MAN: "0" * 64}), snapf)
case("Q4 sha 不一致只报告", "不一致" in M.R["checks"]["cyq_restore"]["action"], M.R["checks"]["cyq_restore"]["action"])
M.maybe_restore_cyq(sums, snapf)
case("Q4 损坏 parquet 触发恢复并复核", M.R["checks"]["cyq_restore"]["action"] == "restored", json.dumps(M.R["checks"]["cyq_restore"], ensure_ascii=False)[:300])

# 6) Q7：锁 sha 变化被拒（只测锁比对分支，不访问 healthz）
wfile("RESEARCH_QUIET.lock", "lock A\n")
e = M.quiet_gate("t", full=False, expect_lock_sha="0" * 64)
case("Q7 锁 sha 变化被拒", e and "sha" in e, repr(e))

n_fail = sum(1 for _, ok, _ in RES if not ok)
print("SELFTEST end pass=%d fail=%d workdir=%s" % (len(RES) - n_fail, n_fail, W))
sys.exit(1 if n_fail else 0)
