#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""方案 R 补跑执行器 run_backfill_r.py（QuantLab Data，2026-10-18 起草，待 Arch 审；未运行）。只用标准库，判定处只读 parquet 元数据（pyarrow）。

对应：docs/v2/audit/BACKFILL_1014_1016_OK_REQUEST_ZH_r3.md；Arch 审查 ARCH_DATA_TIMELINE_1019_AND_PLAN_R_REVIEW_ZH.md（717c3e7c）§5.4、§9。
强制执行：
  P2-3 严格串行：run1（cyq）退出 → wait 取 rc → 快照 v2 compare 通过 → cyq 判定全过，才起 run2（tier3,bundle,freshness）。
  P2-4 RSS 自动停：每 5 秒读 /proc/<pid>/status VmRSS，对 nightly 进程及其全部子孙求和；> 1484800 kB 即核 cmdline 后按确切 PID
       先子后父 TERM，10 秒后仍存活才 KILL；采样日志写新文件 /tmp/arch1018/backfill_rss_runN.log。
  P2-5 前后快照都用 v2（c930ed5c），范围 579c8605。
  P3-6 run1 前备份含两个 cyq bundle 副本。
不做的事：不 STOP / CONT 94322（操作员按 .ok 执行，执行器只核 /proc/94322/stat 为 T）；不移动 .ok 到 _consumed；不删任何文件。
用法：
  PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 docs/v2/audit/backfill_1014_1016/run_backfill_r.py --quiet-evidence <healthz 证据文件> [--check-only] </dev/null
退出码：0 全部通过；1 判定 / compare 不过（已按规则中止）；2 前置条件不满足（未起任何运行）；3 RSS 或 15:55 截止触发停进程。
"""
import argparse, datetime, hashlib, json, os, re, shutil, signal, subprocess, sys, time
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
ROOT = "/workspace/QuantLab"
PY = "/usr/bin/python3"
OK_PATH = ROOT + "/output/ai_factory/ARCH_RUN_AUTH_DATA_BACKFILL_1014_1016_PLAN_R.ok"
OK_ID = "ARCH_RUN_AUTH_DATA_BACKFILL_1014_1016_PLAN_R"
PINS = {
    "scripts/nightly_update.py": "ec079d56912aea8a4358a7ae97a73a3ad6ee3df34e83845ad4d655d31d838636",
    "scripts/acquire/relay_health.py": "6d3ea9f57f63af8d82d6eeaf140a989aeb09cda941e6711c25f12fd3bbe0e17f",
    "scripts/acquire/cyq_perf_monthly.py": "6aae6c1b8de7b37752fb5032c22ea65b698f252cc57f8e5af94b1e13d6e09c1f",
    "scripts/acquire/tier3_daily_snapshot.py": "64a71f5607439c5b09ddd92a8dfeffd94e4f5244297f83fbc5c65e3abfcf1067",
    "scripts/acquire/data_freshness_status.py": "a759d29788859b43783bac6360014347b2df0e4dce5949302a0908db511f1d50",
    "quantlab/data_sources/tushare_proxy.py": "ae91f230560d445b4d2321e8e022d01b55773e168d4d842fc6987fa9458fc772",
    "docs/v2/audit/nightly_sha_scope_snapshot_v2_20261018.py": "c930ed5c627bf937e6b5d139c52f18945f045286e78dba66cbe5adfab92ab79a",
    "docs/v2/audit/nightly_sha_scope_backfill_1014_1016.txt": "579c8605266af1724b942fe1f3f2c000e0f97013cb9ff345c184b20c723b54c0",
}
OK_SHA_KEYS = {"sha_nightly_update": "scripts/nightly_update.py", "sha_relay_health": "scripts/acquire/relay_health.py",
               "sha_cyq_perf_monthly": "scripts/acquire/cyq_perf_monthly.py", "sha_tier3_daily_snapshot": "scripts/acquire/tier3_daily_snapshot.py",
               "sha_data_freshness_status": "scripts/acquire/data_freshness_status.py", "sha_tushare_proxy": "quantlab/data_sources/tushare_proxy.py",
               "sha_snapshot_tool": "docs/v2/audit/nightly_sha_scope_snapshot_v2_20261018.py", "scope_sha": "docs/v2/audit/nightly_sha_scope_backfill_1014_1016.txt"}
SNAP = ROOT + "/docs/v2/audit/nightly_sha_scope_snapshot_v2_20261018.py"
SCOPE = ROOT + "/docs/v2/audit/nightly_sha_scope_backfill_1014_1016.txt"
SCOPE_SHA = PINS["docs/v2/audit/nightly_sha_scope_backfill_1014_1016.txt"]
DUS_PIN = "7991455a06b85d7bca09b8c50e2fc1cfe6f421abe33790b90a125097ab2a4850"
TRADE_CAL_PIN = "141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086"
FA_PIN = "fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41"
SW_PIT_PIN = "0b1d3432e30f7cdd907df393299cd2f552e1121899239985a00113c4dfcd89f6"
CMD1 = [PY, "scripts/nightly_update.py", "--date", "20261016", "--steps", "cyq"]
CMD2 = [PY, "scripts/nightly_update.py", "--date", "20261016", "--steps", "tier3,bundle,freshness"]
RSS_STOP_KB = 1484800
SAMPLE_S = 5
TERM_WAIT_S = 10
LATEST_START = {1: (14, 45), 2: (15, 0)}
HARD_STOP = (15, 55)
BLACKOUT = ((16, 40), (18, 40))
P94322 = 94322
BK = ROOT + "/_recovery/data/backfill_1014_1016"
BK_RUN1 = ["data/v2/cyq/cyq_perf_202610.parquet", "data/v2/cyq/manifest.json",
           "logs/nightly/20261014_summary.json", "logs/nightly/20261015_summary.json", "logs/nightly/20261016_summary.json",
           "output/relay_outage_backfill_queue.json", "output/relay_health.json", "output/data_freshness_status.json",
           "output/data_v2_bundle/cyq/manifest.json", "output/data_v2_bundle/cyq/cyq_perf_202610.parquet"]
T3_KINDS = ["concept_dc_index", "concept_dc_member", "anns", "news", "research_report"]
BK_RUN2 = ["data/v2/tier3_daily/%s/%s.parquet" % (k, d) for k in T3_KINDS for d in ("20261014", "20261015")] + \
          ["data/v2/tier3_daily/manifests/20261014.json", "data/v2/tier3_daily/manifests/20261015.json"]
ABSENT_RUN2 = ["data/v2/tier3_daily/%s/20261016.parquet" % k for k in ["concept_dc_index", "concept_dc_member", "concept_ths_index", "anns", "news", "research_report"]] + \
              ["data/v2/tier3_daily/manifests/20261016.json"]
CYQ_BASE_ROWS = 22238
SNAP_DIR = "/tmp/arch1018"
RESULT_DIR = ROOT + "/docs/v2/audit/backfill_1014_1016"

R = {"started_et": None, "events": [], "checks": {}, "runs": {}}


def now():
    return datetime.datetime.now(ET)


def ts():
    return now().isoformat(timespec="seconds")


def ev(msg):
    line = "%s %s" % (ts(), msg)
    R["events"].append(line)
    print(line, flush=True)


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def at(hm):
    n = now()
    return n.replace(hour=hm[0], minute=hm[1], second=0, microsecond=0)


def fsync_dir(d):
    fd = os.open(d, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def write_new(path, text):
    d = os.path.dirname(path)
    tmp = os.path.join(d, ".%s.tmp.%d" % (os.path.basename(path), os.getpid()))
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        os.write(fd, text.encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)
    try:
        os.link(tmp, path)
    finally:
        os.unlink(tmp)
    fsync_dir(d)


# ---------------- /proc ----------------
def proc_state(pid):
    try:
        s = open("/proc/%d/stat" % pid).read()
    except (FileNotFoundError, ProcessLookupError):
        return None
    return s[s.rfind(")") + 2:].split()[0]


def alive(pid):
    st = proc_state(pid)
    return st is not None and st != "Z"


def cmdline(pid):
    try:
        return open("/proc/%d/cmdline" % pid, "rb").read().replace(b"\0", b" ").decode("utf-8", "replace").strip()
    except (FileNotFoundError, ProcessLookupError):
        return ""


def ppid(pid):
    try:
        s = open("/proc/%d/stat" % pid).read()
        return int(s[s.rfind(")") + 2:].split()[1])
    except Exception:
        return None


def children(pid):
    out = []
    try:
        for tid in os.listdir("/proc/%d/task" % pid):
            try:
                out += [int(x) for x in open("/proc/%d/task/%s/children" % (pid, tid)).read().split()]
            except (FileNotFoundError, ProcessLookupError):
                pass
    except (FileNotFoundError, ProcessLookupError):
        pass
    return out


def descendants(pid):
    """深度优先返回子孙 PID，最深的在前（停进程时先子后父）。"""
    res = []
    for c in children(pid):
        res = descendants(c) + [c] + res
    return res


def vmrss_kb(pid):
    try:
        for ln in open("/proc/%d/status" % pid):
            if ln.startswith("VmRSS:"):
                return int(ln.split()[1])
    except (FileNotFoundError, ProcessLookupError):
        pass
    return 0


def signal_exact(pid, sig, must_contain, parent=None):
    """发信号前核 cmdline（与 PPID）；进程已退出（ESRCH）不算错误（P3-4）。"""
    cl = cmdline(pid)
    if not alive(pid):
        ev("SIGNAL skip pid=%d 已退出" % pid); return
    if must_contain not in cl or (parent is not None and ppid(pid) != parent):
        ev("SIGNAL refuse pid=%d cmdline/ppid 不符（%r ppid=%s），不发信号" % (pid, cl[:160], ppid(pid))); return
    try:
        os.kill(pid, sig); ev("SIGNAL %s pid=%d cmd=%r" % (signal.Signals(sig).name, pid, cl[:160]))
    except ProcessLookupError:
        ev("SIGNAL pid=%d ESRCH（已退出）" % pid)


def stop_tree(npid, reason):
    ev("STOP_TREE npid=%d reason=%s" % (npid, reason))
    for c in descendants(npid):  # 截止时刻重读子进程（P3-3）
        signal_exact(c, signal.SIGTERM, "scripts/acquire/")
        t0 = time.time()
        while alive(c) and time.time() - t0 < TERM_WAIT_S:
            time.sleep(0.5)
        if alive(c):
            signal_exact(c, signal.SIGKILL, "scripts/acquire/")
            t0 = time.time()
            while alive(c) and time.time() - t0 < 5:
                time.sleep(0.5)
    t0 = time.time()
    while alive(npid) and time.time() - t0 < TERM_WAIT_S:
        time.sleep(0.5)
    if alive(npid):
        signal_exact(npid, signal.SIGTERM, "scripts/nightly_update.py")
        t0 = time.time()
        while alive(npid) and time.time() - t0 < TERM_WAIT_S:
            time.sleep(0.5)
        if alive(npid):
            signal_exact(npid, signal.SIGKILL, "scripts/nightly_update.py")


# ---------------- 前置 ----------------
def parse_ok(p):
    kv = {}
    for ln in open(p, encoding="utf-8"):
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        m = re.match(r"^([A-Za-z0-9_]+)\s*[:=]\s*(.*)$", ln)
        if m:
            kv[m.group(1)] = m.group(2).strip()
    return kv


def truthy(v):
    return str(v).strip().lower() in ("true", "1", "yes")


def check_ok():
    if not os.path.isfile(OK_PATH):
        return "run .ok 不存在 %s" % OK_PATH
    kv = parse_ok(OK_PATH)
    R["checks"]["ok"] = dict(path=OK_PATH, sha256=sha256(OK_PATH), keys=sorted(kv))
    if kv.get("ok_id") != OK_ID:
        return "ok_id 不符：%r" % kv.get("ok_id")
    if kv.get("ok_type", "run") != "run":
        return "ok_type 不是 run"
    try:
        exp = datetime.datetime.fromisoformat(kv.get("expires_et", ""))
    except Exception:
        return "expires_et 无法解析"
    if exp.tzinfo is None or exp <= now():
        return "expires_et 无时区或已过期：%s" % kv.get("expires_et")
    for k, rel in OK_SHA_KEYS.items():
        if k in kv and kv[k].lower() != PINS[rel]:
            return ".ok %s=%s 与执行器钉值 %s 不符" % (k, kv[k], PINS[rel])
    me = sha256(os.path.abspath(__file__))
    if "sha_runner" in kv and kv["sha_runner"].lower() != me:
        return ".ok sha_runner 与本执行器 sha %s 不符" % me
    if "rss_stop_kb" in kv and kv["rss_stop_kb"] != str(RSS_STOP_KB):
        return ".ok rss_stop_kb 不是 %d" % RSS_STOP_KB
    for k in ("allow_run_nightly_update_cyq", "allow_run_nightly_update_tier3_bundle_freshness"):
        if not truthy(kv.get(k)):
            return ".ok 未授权 %s" % k
    for k in ("allow_daily_pull", "allow_trade_cal", "allow_sw", "allow_force", "allow_delete"):
        if truthy(kv.get(k)):
            return ".ok 意外地把 %s 设为 true，拒绝" % k
    R["checks"]["ok"]["expires_et"] = kv["expires_et"]
    R["checks"]["ok"]["runner_sha256"] = me
    return None


def check_pins():
    got = {}
    for rel, pin in PINS.items():
        s = sha256(os.path.join(ROOT, rel)); got[rel] = s
        if s != pin:
            return "sha 不符 %s：%s != %s" % (rel, s, pin)
    for rel, pin in (("output/daily_update_status.json", DUS_PIN), ("data/v2/tushare_raw/trade_cal.parquet", TRADE_CAL_PIN)):
        s = sha256(os.path.join(ROOT, rel)); got[rel] = s
        if s != pin:
            return "MUST 文件 sha 不符 %s：%s" % (rel, s)
    R["checks"]["pins"] = got
    if sys.executable != PY:
        return "解释器不是 %s（%s）" % (PY, sys.executable)
    return None


def time_gate(n):
    t = now()
    if at(BLACKOUT[0]) <= t < at(BLACKOUT[1]):
        return "16:40–18:40 禁跑时段"
    if t >= at(LATEST_START[n]):
        return "run%d 已过最晚开始时间 %02d:%02d" % (n, LATEST_START[n][0], LATEST_START[n][1])
    return None


def check_94322(tag):
    st = proc_state(P94322)
    cl = cmdline(P94322)
    R["checks"].setdefault("p94322", []).append(dict(at=ts(), tag=tag, state=st, cmdline=cl[:200]))
    if st is None:
        ev("94322 不存在（%s），按 r1 §7 记录后继续" % tag); return None
    if st != "T":
        return "94322 状态 %s，不是 T（%s）" % (st, tag)
    return None


# ---------------- 备份 ----------------
def backup(rels, sums_name, mkdir):
    if mkdir:
        os.mkdir(BK)  # 已存在即抛错停下
    lines = []
    for rel in rels:
        src = os.path.join(ROOT, rel); dst = os.path.join(BK, rel)
        if os.path.lexists(dst):
            raise SystemExit("备份目标已存在 %s" % dst)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        if sha256(dst) != sha256(src):
            raise SystemExit("备份 sha 与源不符 %s" % rel)
        lines.append("%s  %s" % (sha256(dst), rel))
    write_new(os.path.join(BK, sums_name), "\n".join(lines) + "\n")
    ev("BACKUP %s %d 个文件 → %s" % (sums_name, len(rels), BK))
    return {rel: l.split("  ")[0] for rel, l in zip(rels, lines)}


# ---------------- 快照 ----------------
def run_tool(args, logname):
    p = os.path.join(SNAP_DIR, logname)
    with open(p, "x") as fh:
        rc = subprocess.call(["nice", "-n", "10", PY] + args, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=fh, stderr=subprocess.STDOUT,
                             env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    out = open(p, encoding="utf-8", errors="replace").read()
    return rc, out


def snap(name):
    out = os.path.join(SNAP_DIR, "backfill_%s.txt" % name)
    rc, txt = run_tool([SNAP, "snap", SCOPE, out, "--expect-scope-sha", SCOPE_SHA], "backfill_%s.snaplog" % name)
    ev("SNAP %s rc=%d" % (name, rc))
    return rc, out


def compare(before, after, name):
    rc, txt = run_tool([SNAP, "compare", SCOPE, before, after, "--expect-scope-sha", SCOPE_SHA], "backfill_compare_%s.log" % name)
    R["checks"]["compare_" + name] = dict(rc=rc, tail=txt[-2000:])
    ev("COMPARE %s rc=%d" % (name, rc))
    return rc == 0 and "META_ONLY_FAIL" not in txt


# ---------------- 运行 ----------------
def run(n, cmd):
    gate = time_gate(n)
    if gate:
        return dict(rc=None, aborted=gate)
    out_path = ROOT + "/logs/nightly/backfill_20261018_run%d.out" % n
    rss_log = open(os.path.join(SNAP_DIR, "backfill_rss_run%d.log" % n), "x")
    t0 = ts()
    fh = open(out_path, "a")
    p = subprocess.Popen(["nice", "-n", "10"] + cmd, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=fh, stderr=subprocess.STDOUT,
                         env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    npid = p.pid
    ev("RUN%d start npid=%d cmd=%s" % (n, npid, " ".join(cmd)))
    rss_log.write("# ts_et\tnpid\tpid:rss_kb...\tsum_kb\n"); rss_log.flush()
    max_sum, max_one, seen, stopped = 0, 0, set(), None
    while p.poll() is None:
        pids = [npid] + descendants(npid)
        seen.update(pids)
        rs = [(x, vmrss_kb(x)) for x in pids]
        s = sum(v for _, v in rs)
        max_sum = max(max_sum, s); max_one = max([max_one] + [v for _, v in rs])
        rss_log.write("%s\t%d\t%s\t%d\n" % (ts(), npid, " ".join("%d:%d" % r for r in rs), s)); rss_log.flush()
        if s > RSS_STOP_KB:
            stopped = "RSS 采样和 %d kB > %d" % (s, RSS_STOP_KB); stop_tree(npid, stopped); break
        if now() >= at(HARD_STOP):
            stopped = "15:55 ET 截止"; stop_tree(npid, stopped); break
        time.sleep(SAMPLE_S)
    rc = p.wait()
    fh.close(); rss_log.close()
    res = dict(npid=npid, start_et=t0, end_et=ts(), rc=rc, cmd=" ".join(cmd), stopped=stopped, rss_max_sum_kb=max_sum,
               rss_max_single_kb=max_one, pids_seen=sorted(seen), out=out_path, rss_log=os.path.join(SNAP_DIR, "backfill_rss_run%d.log" % n),
               note="RSS 为 5 秒采样峰值，不是真实峰值")
    ev("RUN%d end rc=%s stopped=%s rss_max_sum=%d" % (n, rc, stopped, max_sum))
    return res


# ---------------- 判定 ----------------
def num_rows(p):
    import pyarrow.parquet as pq
    return pq.ParquetFile(p).metadata.num_rows


def jload(p):
    return json.load(open(p, encoding="utf-8"))


def check_cyq(log_off, bk_sums):
    f = []
    sm = jload(ROOT + "/logs/nightly/20261016_summary.json").get("steps", {}).get("cyq", {})
    if sm.get("status") != "ok" or "skipped" in sm:
        f.append("summary steps.cyq=%s" % sm)
    lp = ROOT + "/logs/nightly/20261016_cyq.log"
    seg = ""
    if os.path.exists(lp):
        with open(lp, encoding="utf-8", errors="replace") as fh:
            fh.seek(log_off); seg = fh.read()
    days = {}
    for ln in seg.splitlines():
        m = re.match(r"^(2026101[456]) (\d+)$", ln.strip())
        if m:
            days[m.group(1)] = int(m.group(2))
        if ln.startswith("FAIL"):
            f.append("日志 FAIL：" + ln[:120])
    raw = {}
    for d in ("20261014", "20261015", "20261016"):
        if d not in days:
            f.append("日志缺 %s 行" % d); continue
        if days[d] < 5000:
            f.append("%s 行数 %d < 5000" % (d, days[d]))
        p = ROOT + "/data/v2/tushare_raw/cyq_perf/%s.parquet" % d
        if not os.path.exists(p) or os.path.getsize(p) <= 10000:
            f.append("原始文件缺失或 ≤10000 字节 %s" % d); continue
        raw[d] = num_rows(p)
        if raw[d] != days[d]:
            f.append("%s num_rows %d != 日志 %d" % (d, raw[d], days[d]))
    man = jload(ROOT + "/data/v2/cyq/manifest.json"); bkm = jload(BK + "/data/v2/cyq/manifest.json")
    m10 = man.get("months", {}).get("202610", {}); b10 = bkm.get("months", {}).get("202610", {})
    want_rows = CYQ_BASE_ROWS + sum(days.get(d, 0) for d in ("20261014", "20261015", "20261016"))
    exp = dict(new_days=3, fails=[], days=7, range=["20261008", "20261016"], rows=want_rows)
    for k, v in exp.items():
        if m10.get(k) != v:
            f.append("manifest months.202610.%s=%r（应 %r）" % (k, m10.get(k), v))
    if b10.get("rows") != CYQ_BASE_ROWS:
        f.append("备份 manifest 202610 rows=%r，不是 %d" % (b10.get("rows"), CYQ_BASE_ROWS))
    if (m10.get("codes") or 0) < (b10.get("codes") or 0):
        f.append("codes %r < 跑前 %r" % (m10.get("codes"), b10.get("codes")))
    for mm in ["2026%02d" % i for i in range(1, 10)]:
        if man.get("months", {}).get(mm) != bkm.get("months", {}).get(mm):
            f.append("manifest %s 条目与备份不同" % mm)
    if (man.get("date_range") or [None, None])[1] != "20261016":
        f.append("顶层 date_range=%r" % man.get("date_range"))
    pr = num_rows(ROOT + "/data/v2/cyq/cyq_perf_202610.parquet")
    if pr != m10.get("rows"):
        f.append("cyq_perf_202610 num_rows %d != manifest rows %r" % (pr, m10.get("rows")))
    R["checks"]["cyq"] = dict(log_rows=days, raw_num_rows=raw, manifest_202610=m10, parquet_rows=pr, want_rows=want_rows, fails=f)
    if f and pr < CYQ_BASE_ROWS:
        restore_cyq(bk_sums)
    return not f


def restore_one(rel, want):
    src = os.path.join(BK, rel); dst = os.path.join(ROOT, rel); d = os.path.dirname(dst)
    tmp = os.path.join(d, ".%s.restore_tmp.%d" % (os.path.basename(dst), os.getpid()))
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with open(src, "rb") as fh:
            for b in iter(lambda: fh.read(1 << 20), b""):
                os.write(fd, b)
        os.fsync(fd)
    finally:
        os.close(fd)
    if sha256(tmp) != want:
        os.unlink(tmp); ev("RESTORE %s 临时文件 sha 不符，未替换" % rel); return False
    os.replace(tmp, dst); fsync_dir(d)
    ok = sha256(dst) == want
    ev("RESTORE %s sha_ok=%s" % (rel, ok))
    return ok


def restore_cyq(bk_sums):
    ev("cyq 判 FAIL 且 202610 行数低于 %d：按备份原子恢复" % CYQ_BASE_ROWS)
    R["checks"]["cyq_restore"] = {rel: restore_one(rel, bk_sums[rel]) for rel in ("data/v2/cyq/cyq_perf_202610.parquet", "data/v2/cyq/manifest.json")}


def check_run2(bk2, t_start, t_end):
    f = []
    man = jload(ROOT + "/data/v2/tier3_daily/manifests/20261016.json"); it = man.get("items", {})
    def rows_ok(k, lo, hi):
        v = it.get(k, {})
        if v.get("status") != "ok" or not (lo <= (v.get("rows") or -1) <= hi):
            f.append("tier3 %s=%s（要求 ok 且 %s–%s）" % (k, v, lo, hi))
    rows_ok("concept_dc_index", 900, 1200); rows_ok("concept_dc_member", 80000, 110000); rows_ok("news", 1000, 10 ** 9)
    for k in ("anns", "research_report"):
        if it.get(k, {}).get("status") not in ("ok", "empty"):
            f.append("tier3 %s=%s" % (k, it.get(k)))
    pit = {}
    for k, v in it.items():
        if v.get("status") == "ok":
            p = ROOT + "/data/v2/tier3_daily/%s/20261016.parquet" % k
            n = num_rows(p) if os.path.exists(p) else None
            if n != v.get("rows"):
                f.append("tier3 %s num_rows %r != manifest %r" % (k, n, v.get("rows")))
    if it.get("concept_ths_index", {}).get("status") == "ok":
        pit["concept_ths_index"] = "非 10-16 时点：无日期目录，实为 %s 拉取的目录" % t_start[:10]
    pit["available_at"] = "manifest 写死 %r；实际拉取 %s–%s ET（回补快照）" % (man.get("available_at"), t_start, t_end)
    for rel, s in bk2.items():
        if rel.endswith(".parquet") or rel.endswith(".json"):
            if sha256(os.path.join(ROOT, rel)) != s:
                f.append("10-14/15 文件变化 %s" % rel)
    sm = jload(ROOT + "/logs/nightly/20261016_summary.json").get("steps", {})
    files = (sm.get("bundle") or {}).get("files") or []
    need = ["cyq/cyq_perf_202610.parquet"] + ["tier3_daily/%s/20261016.parquet" % k for k, v in it.items() if v.get("status") == "ok"]
    for x in need:
        src = ROOT + ("/data/v2/" + x)
        if x not in files:
            if os.path.exists(src) and os.path.getsize(src) >= 8e6:
                pit.setdefault("bundle_skip_ge_8mb", []).append(x); continue  # nightly L73/L81：≥8MB 不复制，记录不判失败
            f.append("bundle.files 缺 %s" % x); continue
        dst = ROOT + "/output/data_v2_bundle/" + x
        if not (os.path.exists(src) and os.path.exists(dst) and sha256(src) == sha256(dst)):
            f.append("bundle 副本 sha != 源 %s" % x)
    if sha256(ROOT + "/data/v2/sw_pit/industry_members_sw_l1_pit.parquet") != SW_PIT_PIN:
        f.append("sw_pit L1 源 sha 变化")
    fr = jload(ROOT + "/output/data_freshness_status.json"); fb = jload(BK + "/output/data_freshness_status.json")
    g = fr.get("generated_at_et", "")
    try:
        gd = datetime.datetime.fromisoformat(g)
        in_win = datetime.datetime.fromisoformat(t_start) <= gd <= datetime.datetime.fromisoformat(t_end)
    except Exception:
        in_win = False
    if not in_win:
        f.append("freshness generated_at_et=%s 不在 run2 时段 %s–%s" % (g, t_start, t_end))
    for k, v in (("expected_trade_date", "20261016"), ("overall", "ok"), ("stale_tables", [])):
        if fr.get(k) != v:
            f.append("freshness %s=%r" % (k, fr.get(k)))
    for k, v in (fb.get("tables") or {}).items():
        cur = (fr.get("tables") or {}).get(k) or {}
        if cur.get("last_date") != v.get("last_date") or cur.get("sha256") != v.get("sha256"):
            f.append("freshness tables.%s last_date/sha256 与跑前不同" % k)
    if ((fr.get("tables") or {}).get("trade_cal") or {}).get("sha256") != FA_PIN:
        f.append("freshness trade_cal sha 不是 fa4260b8")
    wt = fr.get("warn_tables") or {}
    c = wt.get("cyq_perf_raw") or {}
    if c.get("last_date") != "20261016" or c.get("lag_trading_days") != 0:
        f.append("warn_tables.cyq_perf_raw=%s" % c)
    for k, v in wt.items():
        if k.startswith("tier3_") and k != "tier3_concept_ths_index" and v.get("last_date") != "20261016":
            f.append("warn_tables.%s.last_date=%r" % (k, v.get("last_date")))
    R["checks"]["run2"] = dict(tier3_items=it, bundle_files_n=len(files), freshness=dict(expected=fr.get("expected_trade_date"), overall=fr.get("overall"),
                               generated_at_et=g), pit_flags=pit, fails=f)
    return not f


def finish(code):
    R["finished_et"] = ts(); R["exit"] = code
    R["operator_reminder"] = "无论结果如何：kill -CONT 94322 并留 ps；.ok 移 _consumed；写 BACKFILL_1014_1016_RECEIPT_ZH.md 与 TEAM_STATE"
    try:
        os.makedirs(RESULT_DIR, exist_ok=True)
        p = os.path.join(RESULT_DIR, "run_backfill_r_result_%s.json" % now().strftime("%Y%m%dT%H%M%S"))
        write_new(p, json.dumps(R, ensure_ascii=False, indent=1))
        print("RESULT_FILE %s sha256=%s" % (p, sha256(p)))
    except Exception as e:
        print("WARN 结果文件写入失败 %s；结果如下" % e); print(json.dumps(R, ensure_ascii=False, indent=1))
    sys.exit(code)


def main():
    ap = argparse.ArgumentParser(description="方案 R 补跑执行器")
    ap.add_argument("--quiet-evidence", required=True, help="RESEARCH_QUIET.lock + 15 秒 + healthz 证据文件（只记 sha）")
    ap.add_argument("--check-only", action="store_true", help="只核 .ok / sha / 时间 / 94322，不起任何运行")
    a = ap.parse_args()
    R["started_et"] = ts(); R["pid"] = os.getpid()
    for chk in (check_ok, check_pins):
        e = chk()
        if e:
            ev("PRECONDITION " + e); finish(2)
    if not os.path.isfile(a.quiet_evidence):
        ev("PRECONDITION quiet 证据文件不存在"); finish(2)
    R["checks"]["quiet_evidence"] = dict(path=a.quiet_evidence, sha256=sha256(a.quiet_evidence))
    for e in (time_gate(1), check_94322("pre")):
        if e:
            ev("PRECONDITION " + e); finish(2)
    if not os.path.isdir(SNAP_DIR):
        ev("PRECONDITION %s 不存在" % SNAP_DIR); finish(2)
    if a.check_only:
        ev("CHECK_ONLY 通过，未起任何运行"); finish(0)

    # 第 0 步 dry-run（nightly L106、L137：不跑子进程、不探测中转、不写 summary）
    for i, c in ((1, CMD1), (2, CMD2)):
        rc, txt = run_tool(c + ["--dry-run"], "backfill_dryrun_cmd%d.log" % i)
        R["checks"]["dryrun_%d" % i] = dict(rc=rc, tail=txt[-800:])
        if rc != 0:
            ev("dry-run cmd%d rc=%d" % (i, rc)); finish(2)

    bk1 = backup(BK_RUN1, "SHA256SUMS_pre_run1", mkdir=True)
    rc, before = snap("before")
    if rc != 0:
        finish(2)
    lp = ROOT + "/logs/nightly/20261016_cyq.log"
    log_off = os.path.getsize(lp) if os.path.exists(lp) else 0

    r1 = run(1, CMD1); R["runs"]["run1"] = r1
    rc, a1 = snap("after_run1")
    ok_cmp = rc == 0 and compare(before, a1, "run1")
    if r1.get("aborted"):
        ev("run1 未起：" + r1["aborted"]); finish(2)
    if r1.get("stopped"):
        finish(3)
    if not ok_cmp:
        ev("run1 后 compare 不过，停"); finish(1)
    if not check_cyq(log_off, bk1):
        ev("run1 cyq 判定不过，不起 run2"); finish(1)
    if sha256(ROOT + "/output/daily_update_status.json") != DUS_PIN:
        ev("daily_update_status 变化"); finish(1)

    e = time_gate(2) or check_94322("pre_run2")
    if e:
        ev("run2 不起：" + e); finish(1)
    present = [x for x in ABSENT_RUN2 if os.path.lexists(os.path.join(ROOT, x))]
    R["checks"]["absent_before_run2"] = dict(checked=ABSENT_RUN2, present=present)
    if present:
        ev("20261016 目标已存在 %s，不起 run2" % present); finish(1)
    bk2 = backup(BK_RUN2, "SHA256SUMS_pre_run2", mkdir=False)
    r2 = run(2, CMD2); R["runs"]["run2"] = r2
    rc, a2 = snap("after_run2")
    ok_cmp = rc == 0 and compare(before, a2, "run2")
    if r2.get("stopped"):
        finish(3)
    if not ok_cmp:
        ev("run2 后 compare 不过"); finish(1)
    if not check_run2(bk2, r2["start_et"], r2["end_et"]):
        finish(1)
    check_94322("post")
    ev("全部通过"); finish(0)


if __name__ == "__main__":
    main()
