import importlib.util, json, os, sys, time, tempfile, signal, subprocess, datetime, types
sys.dont_write_bytecode = True
DRV, FB, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
spec = importlib.util.spec_from_file_location("drv", DRV)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
RES = dict(driver=DRV, driver_sha256=m.sha256(DRV), fallback=FB, fallback_sha256=m.sha256(FB), started=m.ts(), tests=[], tmp_dirs=[])
def rec(name, ok, **kw):
    RES["tests"].append(dict(name=name, ok=bool(ok), **kw)); print("TEST", name, "PASS" if ok else "FAIL", flush=True)
def mk():
    t = tempfile.mkdtemp(prefix="qd_drv6_"); RES["tmp_dirs"].append(t); return t
def w(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "x").write(t)
def mine(root):
    r = []
    for n in os.listdir("/proc"):
        if n.isdigit() and int(n) != os.getpid():
            try:
                if os.readlink("/proc/%s/cwd" % n) == root:
                    r.append(int(n))
            except OSError:
                pass
    return r
def cleanup(root, tag):
    left = [(p, m.cmdline(p)[:120], m.proc_state(p)) for p in mine(root) if m.alive(p)]
    for p, _, _ in left:
        try:
            if os.readlink("/proc/%d/cwd" % p) == root:
                os.kill(p, signal.SIGKILL)
        except (OSError, ProcessLookupError):
            pass
    time.sleep(1)
    RES.setdefault("cleanup", []).append(dict(tag=tag, killed_by_test=left, after=[p for p in mine(root) if m.alive(p)]))
    return left

TMP = mk()
m.ROOT = TMP; m.D = "20261019"; m.RUN_DIR = TMP + "/run"; m.HERE = TMP + "/here"; m.MARK_DIR = TMP + "/markers"; m.RAW = TMP + "/raw"
for d_ in ("run", "here", "markers", "raw", "logs/nightly", "output"):
    os.makedirs(TMP + "/" + d_)
m.STAMP = "TEST"
m.A = types.SimpleNamespace(ok=None, profile="strict", check_only=False)

# T1 parse_ok
cases = {"good": b"ok_id=X\ndate=20261019\n# whole-line comment ok\n", "inline": b"ok_id=X  # c\n", "dup": b"date=1\ndate=2\n", "colon": b"date: 1\n",
         "draft": b"ok_id=DRAFT\n", "nonascii": "ok_id=\xe4\xb8\xad\n".encode("latin-1"), "cr": b"ok_id=X\r\n", "unknown": b"foo_bar=1\n"}
got = {}
for k, b in cases.items():
    p = TMP + "/t1_%s.ok" % k; open(p, "xb").write(b); got[k] = m.parse_ok(p)[1]
rec("T01_parse_ok_rejects", got["good"] == [] and all(got[k] for k in cases if k != "good"), errors=got)

# T2 check_ok
iss = (m.now() - datetime.timedelta(minutes=5)).isoformat(timespec="seconds"); exp = (m.now() + datetime.timedelta(hours=2)).isoformat(timespec="seconds")
base = {"ok_id": "ARCH_RUN_AUTH_DATA_NIGHTLY_20261019", "ok_type": "run", "date": "20261019", "signed_by": "QuantLab Arch", "issued_at": iss, "expires_et": exp,
        "single_use": "true", "live": "false", "promotion_approved": "false", "interpreter": "/usr/bin/python3", "sha_driver": m.sha256(DRV),
        "pin_trade_cal": m.PIN, "pin_frozen_closure": list(m.FROZEN.values())[0], "daily_pull_max_min": "30", "call_b_budget_min": "75",
        "call_b_latest_finish": "16:00", "rss_stop_kb": "1484800", "rss_hard_kb": "1536000", "blackout_et": "16:40-18:40",
        "allow_kill_scope": "driver_descendants_exact_pid", "allow_trade_cal_step": "false", "allow_sw": "false", "allow_force": "false",
        "allow_delete": "false", "allow_commit": "false", "allow_run_daily_pull_20261019": "true", "allow_run_call_b_20261019": "true",
        "allow_restore_trade_cal_20261019": "true", "allow_write_nightly_marker_20261019": "true"}
for k, (rel, pin) in m.SHA_KEYS.items():
    base[k] = pin
res2 = {}
def try_ok(name, kv, sub=""):
    d = TMP + "/oks/" + sub; os.makedirs(d, exist_ok=True)
    p = d + "/ARCH_%s.ok" % name; open(p, "x").write("".join("%s=%s\n" % x for x in kv.items())); m.A.ok = p; m.R["checks"] = {}
    e = m.check_ok()[1]; res2[name] = e; return e
def var(**ch):
    d = dict(base); d.update(ch); return d
e_full = try_ok("full", base)
e_cons = try_ok("consumed", base, "_consumed")
e_miss = try_ok("missing_sha_relay_health", {k: v for k, v in base.items() if k != "sha_relay_health"})
e_t1 = try_ok("tier1_old_b630", var(sha_tier1_pull="b630bca24fe7c86a656cf375c4aa1f543d98dac86178ba7ae50881cf4dbeb711"))
e_sig = try_ok("signed_by_wrong", var(signed_by="Someone"))
e_iss = try_ok("issued_future", var(issued_at=(m.now() + datetime.timedelta(hours=1)).isoformat(timespec="seconds")))
e_live = try_ok("live_true", var(live="true"))
e_bud = try_ok("budget_bad", var(call_b_budget_min="x"))
e_src = try_ok("source_relay_on", var(source_relay_only="true")); src_on = m.CFG.get("source_relay")
rec("T02_check_ok_required_keys", e_full is None and e_cons and e_miss and e_t1 and e_sig and e_iss and e_live and e_bud and e_src is None and src_on is True,
    results=res2, source_relay_after_on=src_on)
m.CFG["source_relay"] = False

# T3 expiry
m.CFG["expires"] = m.now() - datetime.timedelta(seconds=1); x1 = m.check_expiry("callB")
m.CFG["expires"] = m.now() + datetime.timedelta(hours=1); x2 = m.check_expiry("callB")
rec("T03_expiry_rechecked", x1 and x2 is None, expired=x1, valid=x2)

# T4 解释器不重复
try:
    m.run_tool([m.PY, "x.py"], "dbl.log", "compare"); a1 = False
except AssertionError as e:
    a1 = str(e)
rec("T04_no_double_interpreter", bool(a1), assert_msg=a1)

# T5 日期统一 + last_date 两种格式（post_checks 在假状态文件上）
nd = dict((v, m.norm_date(v)) for v in ["20261019", "2026-10-19", "2026-10-19T05:40:00-04:00", "20261016", None, "bad"])
rbf = dict(start_epoch=time.time() - 60, end_epoch=time.time() + 60)
def status_case(fmt_ld, fmt_tgt):
    for f in ("output/daily_update_status.json", "output/data_freshness_status.json"):
        if os.path.exists(TMP + "/" + f): os.unlink(TMP + "/" + f)
    tabs = dict((t, dict(last_date=fmt_ld, rows=10)) for t in m.REQUIRED_TABLES)
    w(TMP + "/output/daily_update_status.json", json.dumps(dict(status="ok", target_trade_date=fmt_tgt, finished_at=m.ts(), tables=tabs)))
    w(TMP + "/output/data_freshness_status.json", json.dumps(dict(overall="ok", expected_trade_date="20261016", generated_at=m.ts())))
    m.R["fail_reasons"] = []; m.R["checks"]["status_before"] = dict(rows=dict((t, 10) for t in m.REQUIRED_TABLES))
    m.check_summary = lambda steps, rb, tag: ([], {}); m.check_hsgt_log = lambda rb: None
    m.post_checks(rbf); return list(m.R["fail_reasons"])
orig_cs, orig_hs = m.check_summary, m.check_hsgt_log
f_a = status_case("20261019", "20261019"); f_b = status_case("2026-10-19", "2026-10-19"); f_c = status_case("20261016", "2026-10-19")
m.check_summary, m.check_hsgt_log = orig_cs, orig_hs
rec("T05_last_date_two_formats", f_a == [] and f_b == [] and len(f_c) == len(m.REQUIRED_TABLES), norm=nd, yyyymmdd=f_a, iso=f_b, old_20261016=f_c)

# T6 summary 旧记录 / skipped
sh = datetime.timezone(datetime.timedelta(hours=8))
def summ(fin, steps, mt=None):
    p = TMP + "/logs/nightly/20261019_summary.json"
    if os.path.exists(p): os.unlink(p)
    w(p, json.dumps(dict(date="20261019", finished=fin.isoformat(timespec="seconds"), steps=steps)))
    if mt: os.utime(p, (mt, mt))
t_a = time.time(); time.sleep(1.2)
summ(datetime.datetime.now(sh), {"daily_pull": {"status": "ok"}}); time.sleep(1.2)
f_ok = m.check_summary(["daily_pull"], dict(start_epoch=t_a, end_epoch=time.time()), "T6ok")[0]
summ(datetime.datetime.now(sh), {"daily_pull": {"status": "ok", "skipped": "RELAY_DOWN"}})
f_skip = m.check_summary(["daily_pull"], dict(start_epoch=t_a, end_epoch=time.time() + 1), "T6skip")[0]
summ(datetime.datetime.now(sh) - datetime.timedelta(hours=3), {"daily_pull": {"status": "ok"}}, mt=t_a - 7200)
f_old = m.check_summary(["daily_pull"], dict(start_epoch=t_a, end_epoch=time.time() + 1), "T6old")[0]
rec("T06_stale_summary_fails", f_ok == [] and f_skip and len(f_old) >= 2, ok_case=f_ok, skipped=f_skip, stale=f_old)

# T7 hsgt rc=2 视同 partial
def hs(txt):
    p = TMP + "/logs/nightly/20261019_hsgt.log"
    if os.path.exists(p): os.unlink(p)
    w(p, "\n=== %s /usr/bin/python3 scripts/acquire/fill_hsgt_top10_extend.py\n%s\n" % (datetime.datetime.now().isoformat(), txt))
    return m.check_hsgt_log(dict(start_epoch=time.time() - 5))
h0 = hs("CHUNK DONE done=1 fail=0 remaining=0 auth_max=20261019"); h2 = hs("CHUNK DONE done=0 fail=3 remaining=3 auth_max=20261016")
rec("T07_hsgt_rc2_is_partial", h0 is None and h2 is not None, remaining0=h0, remaining3=h2)

# T8 check-only 退出 10
m.A = types.SimpleNamespace(ok=None, profile="strict", check_only=True)
try:
    m.finish(m.CHECK_ONLY_EXIT, True); c8 = None
except SystemExit as e:
    c8 = e.code
m.A = types.SimpleNamespace(ok=None, profile="strict", check_only=False)
m.signal.signal(m.signal.SIGTERM, m.signal.SIG_DFL); m.signal.signal(m.signal.SIGINT, m.signal.default_int_handler); m.signal.signal(m.signal.SIGHUP, m.signal.SIG_DFL)
rec("T08_check_only_exit_10", c8 == 10, exit_code=c8)

# T9 受保护 PID：只能 T 或已退出；signal_exact 永不发信号（用本测试自己起的 sleep 代替 94322，绝不碰真实 94322 / 94403）
sp = subprocess.Popen(["/bin/sleep", "300"], cwd=TMP)
m.GUARDED = {sp.pid: "/bin/sleep"}
m.pgrep_lines = (lambda orig: (lambda pat: (1, []) if pat == m.PGREP_WATCHER else orig(pat)))(m.pgrep_lines)
g_run = m.guarded_check()
os.kill(sp.pid, signal.SIGSTOP); time.sleep(0.5)
g_stop = m.guarded_check()
sig_r = m.signal_exact(sp.pid, signal.SIGKILL, ("/bin/sleep",), os.getpid())
alive_after = m.alive(sp.pid)
os.kill(sp.pid, signal.SIGKILL); sp.wait()
m.GUARDED = {94322: "remaining_after_stk_surv.py", 94403: "relay_outage_backfill.py"}
rec("T09_guarded_T_or_exited_never_signaled", g_run and g_stop is None and sig_r == "refused" and alive_after, running=g_run, stopped=g_stop, signal_result=sig_r)

# T10 子工具超时 → ToolTimeout，进程按确切 PID 停
w(TMP + "/faketool_sleep.py", "import time\ntime.sleep(300)\n")
m.TOOL_TIMEOUT_S = dict(m.TOOL_TIMEOUT_S, compare=2)
t0 = time.time()
try:
    m.run_tool([TMP + "/faketool_sleep.py"], "tool_to.log", "compare"); tt = None
except m.ToolTimeout as e:
    tt = str(e)
rec("T10_tool_timeout", tt is not None and not [p for p in mine(TMP) if m.alive(p) and "faketool_sleep" in m.cmdline(p)], msg=tt, elapsed_s=round(time.time() - t0, 1),
    record=m.R["checks"].get("tool_timeouts"))

# T11 停止顺序（假进程树）：假 nightly → 假 tier1_pull（忽略 TERM）→ 孙 + 无标记 /bin/sleep + 自脱离孤儿
w(TMP + "/scripts/nightly_update.py", "import subprocess, sys, time\nsubprocess.Popen([sys.executable, \"scripts/acquire/tier1_pull.py\"])\ntime.sleep(300)\n")
w(TMP + "/scripts/acquire/tier1_pull.py", "import subprocess, sys, time, signal\nsubprocess.Popen([sys.executable, \"scripts/acquire/grand_ignore_term.py\"])\nsubprocess.Popen([\"/bin/sleep\", \"301\"])\nsubprocess.Popen([sys.executable, \"scripts/acquire/orphan_launch.py\"])\ntime.sleep(300)\n")
w(TMP + "/scripts/acquire/grand_ignore_term.py", "import signal, time\nsignal.signal(signal.SIGTERM, signal.SIG_IGN)\ntime.sleep(300)\n")
w(TMP + "/scripts/acquire/orphan_launch.py", "import os, time\nif os.fork() == 0:\n    os.setsid(); time.sleep(300)\nelse:\n    os._exit(0)\n")
m.R["events"] = []; m.R["checks"] = {}
r11 = m.run_nightly("daily_pull", "T11", m.now() + datetime.timedelta(seconds=6), "MAX_RUN", m.CALL_A_MARKS, m.CALL_A_ENV)
st = m.R["checks"]["stop_tree"][0]; steps = st["steps"]; names = [s[0] for s in steps]; idx = [s[1] for s in steps]
ps_b = dict((x["pid"], x) for x in st["ps_before"])
tier = [p for p, x in ps_b.items() if "tier1_pull.py" in x["cmd"]]; grand = [p for p, x in ps_b.items() if "grand_ignore_term" in x["cmd"]]
slp = [p for p, x in ps_b.items() if x["cmd"].startswith("/bin/sleep")]
tk = [s for s in steps if s[0] == "TERM_KILL"]; tkp = [s[1] for s in tk]
order_ok = names[0] == "SIGSTOP_PARENT" and names[-1] == "SIGKILL_PARENT" and all(n == "SIGSTOP" for n in names[1:1 + len(st["tree"])]) \
    and bool(tier and grand) and tkp.index(grand[0]) < tkp.index(tier[0]) and dict((s[1], s[2]) for s in tk).get(grand[0]) == "killed" \
    and dict((s[1], s[2]) for s in tk).get(tier[0]) == "term_ok"
orph = m.R["checks"].get("orphans_T11") or {}
rec("T11_stop_order_freeze_then_deepest_first", order_ok and r11["reason_code"] == "MAX_RUN" and r11["rc"] == -9, steps=steps, tree=st["tree"], rc=r11["rc"],
    reason_code=r11["reason_code"], events=[e for e in m.R["events"] if "SIGNAL" in e])
rec("T12_unmarked_child_is_residual_FAILED", bool(slp) and any(x.get("pid") == slp[0] for x in r11["residual"]), residual=r11["residual"],
    note="无标记的 /bin/sleep 不发信号，记 residual；main 中 residual → 不重试、不起 call B、FAILED")
lg = [x["pid"] for x in orph.get("logged_only", [])]
rec("T13_orphan_ppid1_log_only", lg and all(m.alive(p) for p in lg), orphans=orph)
cleanup(TMP, "T11")

# T14 标记不符 → 拒发 → wait 超时（HANG）
w(TMP + "/plain/scripts/nightly_update.py", "import time\ntime.sleep(300)\n")
m.ROOT = TMP + "/plain"; os.makedirs(m.ROOT + "/logs/nightly")
m.R["checks"] = {}; mark0 = m.NIGHTLY_MARK; m.NIGHTLY_MARK = "__nomatch__"; m.WAIT_TIMEOUT_S = 3
r14 = m.run_nightly("daily_pull", "T14", m.now() + datetime.timedelta(seconds=2), "MAX_RUN", m.CALL_A_MARKS)
s14 = m.R["checks"]["stop_tree"][0]["steps"]
rec("T14_refuse_and_wait_timeout_HANG", r14["wait_timeout"] and r14["rc"] is None and s14[0][2] == "refused" and "HANG" in m.R["reason_codes"], steps=s14)
cleanup(m.ROOT, "T14"); m.NIGHTLY_MARK = mark0; m.WAIT_TIMEOUT_S = 60; m.ROOT = TMP

# T15–T18 端到端假驱动（thang2.py）
def hang_case(name, mode, action=None):
    root = mk(); t0 = time.time()
    hp = subprocess.Popen([m.PY, "/tmp/qd1018/v31/thang3.py", DRV, root, mode], cwd=root, stdin=subprocess.DEVNULL, stdout=open(root + ".out", "x"), stderr=subprocess.STDOUT)
    sent = None
    if action:
        time.sleep(action[1])
        if m.alive(hp.pid) and "thang3.py" in m.cmdline(hp.pid) and m.ppid(hp.pid) == os.getpid():
            os.kill(hp.pid, action[0]); sent = "%s %d" % (signal.Signals(action[0]).name, hp.pid)
    try:
        rc = hp.wait(timeout=120)
    except subprocess.TimeoutExpired:
        rc = "timeout"
    return root, rc, sent, time.time() - t0
def receipt(root):
    rcp = sorted(os.listdir(root + "/here"))
    return (json.load(open(root + "/here/" + rcp[0])) if rcp else {}), rcp
def calsha(root):
    import hashlib
    return hashlib.sha256(open(root + "/trade_cal.parquet", "rb").read()).hexdigest()
def pin_of(root):
    import hashlib
    return hashlib.sha256(b"fake trade_cal v1\n").hexdigest()

root, rc, sent, el = hang_case("cap", "cap")
rj, rcp = receipt(root); mk_ = sorted(os.listdir(root + "/markers")); left = cleanup(root, "T15")
log_txt = open(root + "/logs/nightly/20261019_daily_pull.log").read()
cal = (rj.get("checks") or {}).get("calendar") or [{}]
rec("T15_daily_pull_hang_hard_stop_FAILED_calendar_restored", rc == 1 and mk_ == ["nightly_20261019.FAILED.json"] and "MAX_RUN" in rj.get("reason_codes", [])
    and calsha(root) == pin_of(root) and cal[0].get("changed") is True and not left and "TSPRO_RELAY_TIMEOUT=115 SOURCE=None TIER1_SKIP_CAL_REFRESH=1" in log_txt,
    exit_code=rc, markers=mk_, reason_codes=rj.get("reason_codes"), calendar=cal, fail_reasons=rj.get("fail_reasons"), env_line=[l for l in log_txt.splitlines() if l.startswith("ENV")],
    cal_skip_evidence=(rj.get("checks") or {}).get("cal_refresh_skip_evidence"), elapsed_s=round(el, 1), root=root)

root, rc, sent, el = hang_case("sig", "sig", (signal.SIGTERM, 6))
rj, rcp = receipt(root); mk_ = sorted(os.listdir(root + "/markers")); left = cleanup(root, "T16")
rec("T16_driver_SIGTERM_FAILED_exit11_calendar_restored", rc == 11 and mk_ == ["nightly_20261019.FAILED.json"] and "SIGNAL" in rj.get("reason_codes", [])
    and calsha(root) == pin_of(root) and not left, exit_code=rc, signal=sent, markers=mk_, reason_codes=rj.get("reason_codes"),
    stop=((rj.get("checks") or {}).get("stop_tree") or [{}])[0].get("steps"), elapsed_s=round(el, 1), root=root)

root, rc, sent, el = hang_case("callb", "callb")
rj, rcp = receipt(root); mk_ = sorted(os.listdir(root + "/markers")); left = cleanup(root, "T17")
stb = [s for s in (rj.get("checks") or {}).get("stop_tree", []) if s.get("reason_code") == "CALLB_TIMEOUT"]
rec("T17_callB_timeout_FAILED", rc == 1 and mk_ == ["nightly_20261019.FAILED.json"] and stb and not left and len(rj.get("invocations", [])) == 2,
    exit_code=rc, markers=mk_, reason_codes=rj.get("reason_codes"), callb_stop=stb[0]["steps"] if stb else None, fail_reasons=rj.get("fail_reasons"), elapsed_s=round(el, 1), root=root)

root, rc, sent, el = hang_case("rss", "rss")
rj, rcp = receipt(root); mk_ = sorted(os.listdir(root + "/markers")); left = cleanup(root, "T18")
rec("T18_RSS_stop_not_retried", rc == 1 and mk_ == ["nightly_20261019.FAILED.json"] and rj.get("reason_codes") == ["RSS"] and len(rj.get("prior_attempts", [])) == 1 and not left,
    exit_code=rc, reason_codes=rj.get("reason_codes"), attempts=len(rj.get("prior_attempts", [])), fail_reasons=rj.get("fail_reasons"), root=root)

# T19 驱动被 SIGKILL → 例程兜底：先 busy（孤儿树仍在）→ 测试按 cwd 清掉自己的假进程 → 兜底原子恢复假日历 + 代写 FAILED driver_killed
root, rc, sent, el = hang_case("kill", "kill", (signal.SIGKILL, 6))
mk0 = sorted(os.listdir(root + "/markers")); cal_bad = calsha(root) != pin_of(root)
okp = root + "/fallback.ok"; open(okp, "x").write("allow_routine_fallback_restore_20261019=true\nissued_at=%s\n" % (m.now() - datetime.timedelta(minutes=10)).isoformat(timespec="seconds"))
fb = [m.PY, FB, "--date", "20261019", "--ok", okp, "--target", root + "/trade_cal.parquet", "--run-root", root + "/_recovery/data/nightly_20261019",
      "--marker-dir", root + "/markers", "--receipt-dir", root + "/here", "--test-pin", pin_of(root)]
f1 = subprocess.run(fb, cwd="/tmp", capture_output=True, text=True, timeout=60)
left = cleanup(root, "T19")
f2 = subprocess.run(fb, cwd="/tmp", capture_output=True, text=True, timeout=60)
mk2 = sorted(os.listdir(root + "/markers"))
mj = json.load(open(root + "/markers/nightly_20261019.FAILED.json")) if mk2 else {}
rec("T19_driver_SIGKILL_routine_fallback", rc == -9 and mk0 == [] and cal_bad and f1.returncode == 6 and f2.returncode == 1 and calsha(root) == pin_of(root)
    and mj.get("writer") == "routine_fallback" and mj.get("reason") == "driver_killed",
    driver_rc=rc, signal=sent, markers_after_kill=mk0, calendar_bad_after_kill=cal_bad, fallback1_rc=f1.returncode, fallback1_pgrep=f1.stdout[-600:],
    orphans_killed_by_test=left, fallback2_rc=f2.returncode, marker=mj, root=root)


# ======== v3.1 新增 T20–T28（只用 /tmp 假进程与假文件） ========
def iso_et(dt):
    return dt.isoformat(timespec="seconds")
def fb_cmd(root, okp, extra=()):
    return [m.PY, FB, "--date", "20261019", "--ok", okp, "--target", root + "/trade_cal.parquet", "--run-root", root + "/_recovery/data/nightly_20261019",
            "--marker-dir", root + "/markers", "--receipt-dir", root + "/here", "--test-pin", pin_of(root)] + list(extra)
def fb_root(run_dirs=()):
    root = mk()
    for d_ in ("markers", "here", "_recovery/data/nightly_20261019"):
        os.makedirs(root + "/" + d_)
    open(root + "/trade_cal.parquet", "x").write("fake trade_cal v1\n")
    for rd in run_dirs:
        os.makedirs(root + "/_recovery/data/nightly_20261019/" + rd)
    return root
def fb_ok(root, issued):
    p = root + "/fb.ok"; open(p, "x").write("allow_routine_fallback_restore_20261019=true\nissued_at=%s\n" % iso_et(issued)); return p

# T20 P1-1：没有晚于 issued_at 的 run_* → 退出 7，不写 marker
nowet = m.now()
r20a = fb_root(); o20a = fb_ok(r20a, nowet - datetime.timedelta(minutes=5))
f20a = subprocess.run(fb_cmd(r20a, o20a), cwd="/tmp", capture_output=True, text=True, timeout=60)
old = (nowet - datetime.timedelta(hours=3)).strftime("run_%Y%m%dT%H%M%S")
r20b = fb_root([old]); o20b = fb_ok(r20b, nowet - datetime.timedelta(minutes=5))
f20b = subprocess.run(fb_cmd(r20b, o20b), cwd="/tmp", capture_output=True, text=True, timeout=60)
newd = (nowet - datetime.timedelta(minutes=1)).strftime("run_%Y%m%dT%H%M%S")
r20c = fb_root([newd]); o20c = fb_ok(r20c, nowet - datetime.timedelta(minutes=5))
f20c = subprocess.run(fb_cmd(r20c, o20c), cwd="/tmp", capture_output=True, text=True, timeout=60)
rec("T20_fallback_no_run_evidence_exit7_no_marker", f20a.returncode == 7 and os.listdir(r20a + "/markers") == [] and f20b.returncode == 7 and os.listdir(r20b + "/markers") == []
    and f20c.returncode == 1 and os.listdir(r20c + "/markers") == ["nightly_20261019.FAILED.json"],
    no_run_dir_rc=f20a.returncode, old_run_dir_rc=f20b.returncode, fresh_run_dir_rc=f20c.returncode, markers_fresh=os.listdir(r20c + "/markers"), out_a=f20a.stdout[-400:])

# T21 P1-2：只剩一个孤立的步骤脚本（PPID=1） → 退出 6；94322 替身为 T → 按确切 PID 排除；替身为 S → 退出 6
r21 = fb_root([newd]); o21 = fb_ok(r21, nowet - datetime.timedelta(minutes=5))
w(r21 + "/scripts/acquire/tier3_daily_snapshot.py", "import os, time\nif os.fork() == 0:\n    os.setsid(); time.sleep(300)\nelse:\n    os._exit(0)\n")
subprocess.Popen([m.PY, "scripts/acquire/tier3_daily_snapshot.py"], cwd=r21).wait(); time.sleep(0.5)
orph21 = [p for p in mine(r21) if m.alive(p) and "tier3_daily_snapshot" in m.cmdline(p)]
f21a = subprocess.run(fb_cmd(r21, o21), cwd="/tmp", capture_output=True, text=True, timeout=60)
cleanup(r21, "T21a")
r21b = fb_root([newd]); o21b = fb_ok(r21b, nowet - datetime.timedelta(minutes=5))
w(r21b + "/scripts/acquire/remaining_after_stk_surv.py", "import time\ntime.sleep(300)\n")
gp = subprocess.Popen([m.PY, "scripts/acquire/remaining_after_stk_surv.py"], cwd=r21b); time.sleep(0.5)
f21s = subprocess.run(fb_cmd(r21b, o21b, ["--test-guarded", "%d=remaining_after_stk_surv.py" % gp.pid]), cwd="/tmp", capture_output=True, text=True, timeout=60)
os.kill(gp.pid, signal.SIGSTOP); time.sleep(0.5)
f21t = subprocess.run(fb_cmd(r21b, o21b, ["--test-guarded", "%d=remaining_after_stk_surv.py" % gp.pid]), cwd="/tmp", capture_output=True, text=True, timeout=60)
st21 = m.proc_state(gp.pid)
os.kill(gp.pid, signal.SIGKILL); gp.wait()
try:
    j21t = json.loads(f21t.stdout[f21t.stdout.index("{"):])
except Exception:
    j21t = {}
exc = [x["pid"] for x in (j21t.get("pgrep") or {}).get("excluded", []) if "T" in x.get("why", "") or "受保护" in x.get("why", "")]
rec("T21_fallback_orphan_step_script_exit6_and_guarded_T_excluded", bool(orph21) and m.ppid(orph21[0]) in (1, None) and f21a.returncode == 6
    and f21s.returncode == 6 and f21t.returncode == 1 and gp.pid in exc and st21 == "T",
    orphan_pid=orph21, orphan_rc=f21a.returncode, guarded_S_rc=f21s.returncode, guarded_T_rc=f21t.returncode, guarded_excluded=exc, out_orphan=f21a.stdout[-500:])
cleanup(r21b, "T21b")

# T22 P1-3：GUARDED 替身本身 T，但子进程 S → 前置失败；子进程也 T → 通过
w(TMP + "/t22_parent.py", "import subprocess, time\nsubprocess.Popen(['/bin/sleep', '300'])\ntime.sleep(300)\n")
gpar = subprocess.Popen([m.PY, TMP + "/t22_parent.py"], cwd=TMP); time.sleep(1.0)
kids = m.descendants(gpar.pid)
m.GUARDED = {gpar.pid: "t22_parent.py"}
os.kill(gpar.pid, signal.SIGSTOP); time.sleep(0.5)
g22a = m.guarded_check(); tree22a = (m.R["checks"]["guarded"].get(gpar.pid) or {}).get("tree")
for c in kids:
    os.kill(c, signal.SIGSTOP)
time.sleep(0.5)
g22b = m.guarded_check()
for c in kids:
    os.kill(c, signal.SIGKILL)
os.kill(gpar.pid, signal.SIGKILL); gpar.wait()
m.GUARDED = {94322: "remaining_after_stk_surv.py", 94403: "relay_outage_backfill.py"}
rec("T22_guarded_T_parent_with_S_child_fails", bool(kids) and g22a is not None and "P1-3" in g22a and g22b is None, child=kids, parent_T_child_S=g22a, tree=tree22a, all_T=g22b)
cleanup(TMP, "T22")

# T23 P2-2 / P2-1 端到端（thang3.py）
root, rc, sent, el = hang_case("orphb", "orphb")
rj, rcp = receipt(root); mk_ = sorted(os.listdir(root + "/markers"))
orb = (rj.get("checks") or {}).get("orphans_callB") or {}
left = cleanup(root, "T23a")
rec("T23a_callB_ppid1_orphan_FAILED", rc == 1 and mk_ == ["nightly_20261019.FAILED.json"] and "ORPHAN" in rj.get("reason_codes", []) and orb.get("logged_only")
    and any("PPID=1" in x for x in rj.get("fail_reasons", [])), exit_code=rc, reason_codes=rj.get("reason_codes"), orphans=orb, killed_by_test=left,
    fail_reasons=rj.get("fail_reasons"), root=root)
root, rc, sent, el = hang_case("finalcal", "finalcal")
rj, rcp = receipt(root); mk_ = sorted(os.listdir(root + "/markers")); left = cleanup(root, "T23b")
calf = [c for c in (rj.get("checks") or {}).get("calendar", []) if c.get("tag") == "final"]
rec("T23b_final_sha_mismatch_restore_then_FAILED", rc == 1 and mk_ == ["nightly_20261019.FAILED.json"] and "FINAL_CAL_MISMATCH" in rj.get("reason_codes", [])
    and calsha(root) == pin_of(root) and calf and calf[0].get("changed") is True and calf[0].get("sha_after") == pin_of(root) and "P0" not in rj.get("reason_codes", []),
    exit_code=rc, reason_codes=rj.get("reason_codes"), final_calendar=calf, root=root)
root, rc, sent, el = hang_case("rcb", "rcb")
rj, rcp = receipt(root); mk_ = sorted(os.listdir(root + "/markers")); left = cleanup(root, "T23c")
rec("T23c_F3_callB_rc_nonzero_FAILED", rc == 1 and mk_ == ["nightly_20261019.FAILED.json"] and any("call B rc=1" in x for x in rj.get("fail_reasons", [])),
    exit_code=rc, fail_reasons=rj.get("fail_reasons"), root=root)

# T24 两个新 .ok 键：缺省 / true / false 均可；其余写法拒签
o24 = {}
for nm, v in (("absent", None), ("true", "true"), ("false", "false"), ("True", "True"), ("one", "1"), ("yes", "yes")):
    kv = dict(base)
    if v is not None:
        kv["allow_relay_partial_20261019"] = v; kv["allow_hsgt_source_empty_warn_20261019"] = v
    e = try_ok("newkeys_" + nm, kv)
    o24[nm] = dict(err=e, relay_partial=m.CFG.get("relay_partial"), hsgt_empty_warn=m.CFG.get("hsgt_empty_warn"))
rec("T24_ok_new_keys_bool_strict", o24["absent"]["err"] is None and o24["absent"]["relay_partial"] is False and o24["true"]["err"] is None and o24["true"]["relay_partial"] is True
    and o24["true"]["hsgt_empty_warn"] is True and o24["false"]["err"] is None and o24["false"]["hsgt_empty_warn"] is False
    and all(o24[k]["err"] for k in ("True", "one", "yes")), results=o24)

# T25 summary：白名单步骤 partial / skipped 在键 true 时降 WARN；键 false 照旧 FAILED；非白名单步骤 skipped 永远 FAILED
def t25(flag, steps_ok):
    m.CFG["relay_partial"] = flag; m.CFG["warned_steps"] = set(); m.CFG["warn_detail"] = {}; m.R["warnings"] = []
    t0 = time.time(); time.sleep(1.1)
    summ(datetime.datetime.now(sh), steps_ok); time.sleep(1.1)
    f, g = m.check_summary(list(steps_ok), dict(start_epoch=t0, end_epoch=time.time()), "callB")
    return f, list(m.R["warnings"]), dict(m.CFG["warn_detail"])
S25 = {"daily_basic": {"status": "ok"}, "cyq": {"status": "partial", "skipped": "RELAY_DOWN fast-fail", "sec": 0}, "tier3": {"status": "partial", "sec": 5}}
f25t, w25t, d25t = t25(True, S25)
f25f, w25f, _ = t25(False, S25)
f25n, w25n, _ = t25(True, dict(S25, events={"status": "partial", "skipped": "RELAY_DOWN fast-fail", "sec": 0}))
f25d, _, _ = t25(True, {"daily_basic": {"status": "partial", "sec": 3}})
rec("T25_relay_partial_key_true_false_and_non_whitelisted_skipped_fails", f25t == [] and sorted((x["step"], x["reason"]) for x in w25t) == [("cyq", "skipped"), ("tier3", "relay_partial")]
    and all(set(x) == {"step", "date", "actual_rows", "reason"} and isinstance(x["actual_rows"], int) for x in w25t)
    and len(f25f) == 2 and w25f == [] and len(f25n) == 1 and "events" in f25n[0] and len(f25d) == 1,
    key_true=dict(fails=f25t, warnings=w25t), key_false=dict(fails=f25f), events_skipped_key_true=f25n, daily_basic_partial_key_true=f25d)
m.CFG["relay_partial"] = False

# T26 hsgt 源端空日：键 true 且 fail=0、无 ABORT、remaining == 本次写出的 0 行文件数 → WARN hsgt_source_empty；键 false / fail>0 / 数目不符 → FAILED
import pyarrow as pa, pyarrow.parquet as pq
os.makedirs(m.RAW + "/hsgt_top10", exist_ok=True)
def t26(flag, txt, empty_days):
    m.CFG["hsgt_empty_warn"] = flag; m.CFG["warned_steps"] = set(); m.CFG["warn_detail"] = {}; m.R["warnings"] = []
    for f in os.listdir(m.RAW + "/hsgt_top10"):
        os.unlink(m.RAW + "/hsgt_top10/" + f)
    for d_ in empty_days:
        pq.write_table(pa.table({"trade_date": pa.array([], pa.string())}), m.RAW + "/hsgt_top10/%s.parquet" % d_)
    return hs(txt), list(m.R["warnings"])
h26t, w26t = t26(True, "16:01:02 top10 1/1 fail=0 last=20261019:ok:0\nCHUNK DONE done=1 fail=0 remaining=1 auth_max=20261016", ["20261019"])
h26f, w26f = t26(False, "CHUNK DONE done=1 fail=0 remaining=1 auth_max=20261016", ["20261019"])
h26x, _ = t26(True, "CHUNK DONE done=0 fail=1 remaining=1 auth_max=20261016", ["20261019"])
h26m, _ = t26(True, "CHUNK DONE done=1 fail=0 remaining=2 auth_max=20261016", ["20261019"])
h26a, _ = t26(True, "ABORT 3 consecutive fails\nCHUNK DONE done=1 fail=0 remaining=1 auth_max=20261016", ["20261019"])
rec("T26_hsgt_source_empty_key_true_false", h26t is None and w26t == [dict(step="hsgt", date="20261019", actual_rows=0, reason="hsgt_source_empty")]
    and h26f is not None and w26f == [] and h26x is not None and h26m is not None and h26a is not None,
    key_true=dict(err=h26t, warnings=w26t), key_false=h26f, fail_gt0=h26x, count_mismatch=h26m, abort=h26a)
m.CFG["hsgt_empty_warn"] = False

# T27 marker 契约 F1/F2/F4：DONE 带 warnings[] 与 ok_flags；WARN 步骤项可含 skipped；非白名单步骤含 skipped → 降 FAILED 并改写
m.TRADE_CAL = TMP + "/fake_trade_cal.parquet"; open(m.TRADE_CAL, "w").write("fake\n")
def t27(tag, warnings, wd, summary_steps, flags):
    md = TMP + "/markers_" + tag; os.makedirs(md); m.MARK_DIR = md
    m.R["warnings"] = warnings; m.CFG["warn_detail"] = wd; m.R["checks"]["summary_steps"] = summary_steps; m.R["fail_reasons"] = []
    m.CFG["relay_partial"], m.CFG["hsgt_empty_warn"] = flags
    st = m.write_marker(True); fs = os.listdir(md)
    return st, fs, json.load(open(md + "/" + fs[0]))
W27 = [dict(step="cyq", date="20261019", actual_rows=0, reason="skipped"), dict(step="tier3", date="20261019", actual_rows=12, reason="relay_partial")]
D27 = {"cyq": dict(reason="skipped", nightly_status="partial", skipped="RELAY_DOWN fast-fail"), "tier3": dict(reason="relay_partial", nightly_status="partial")}
SS27 = {"cyq": dict(status="partial", sec=0), "tier3": dict(status="partial", sec=5), "bars": dict(status="ok", sec=9)}
s27a, f27a, j27a = t27("warn", W27, D27, SS27, (True, False))
s27b, f27b, j27b = t27("none", [], {}, {"bars": dict(status="ok", sec=9)}, (False, False))
s27c, f27c, j27c = t27("bad", [], {}, {"bars": dict(status="partial skipped", sec=9)}, (False, False))
def wsteps(j):
    return dict((x["step"], x["status"]) for x in j["steps"] if x.get("kind") == "call_b_step")
def skip_ok(j):
    t = dict(j); t["steps"] = [x for x in j["steps"] if not (x.get("step") in ("cyq", "tier3", "hsgt") and x.get("status") == "WARN")]
    t["warnings"] = [dict(x, reason=None) for x in j["warnings"]]
    return "skipped" not in json.dumps(t, ensure_ascii=False).lower()
rec("T27_marker_schema_F1_F2_F4", s27a == "OK" and f27a == ["nightly_20261019.DONE.json"] and j27a["status"] == "OK" and j27a["warnings"] == W27
    and j27a["ok_flags"] == {"allow_relay_partial_20261019": True, "allow_hsgt_source_empty_warn_20261019": False}
    and wsteps(j27a) == {"cyq": "WARN", "tier3": "WARN", "bars": "ok"} and skip_ok(j27a) and isinstance(j27a["steps"], list)
    and s27b == "OK" and j27b["warnings"] == [] and j27b["ok_flags"] == {"allow_relay_partial_20261019": False, "allow_hsgt_source_empty_warn_20261019": False}
    and s27c == "FAILED" and f27c == ["nightly_20261019.FAILED.json"] and "skipped" not in json.dumps(j27c).lower(),
    warn_marker=dict(status=j27a["status"], warnings=j27a["warnings"], ok_flags=j27a["ok_flags"], call_b_steps=[x for x in j27a["steps"] if x.get("kind") == "call_b_step"]),
    empty_marker=dict(warnings=j27b["warnings"], ok_flags=j27b["ok_flags"]), non_whitelisted_skipped=dict(status=s27c, steps=[x for x in j27c["steps"] if x.get("kind") == "call_b_step"]))
m.MARK_DIR = TMP + "/markers"

# T28 两键都 true 时 REQUIRED 6 表不全照旧 FAILED（post_checks）
m.CFG["relay_partial"] = True; m.CFG["hsgt_empty_warn"] = True
m.check_summary, m.check_hsgt_log = (lambda steps, rb, tag: ([], {})), (lambda rb: None)
f28 = status_case("20261016", "2026-10-19")
m.check_summary, m.check_hsgt_log = orig_cs, orig_hs
m.CFG["relay_partial"] = False; m.CFG["hsgt_empty_warn"] = False
rec("T28_required_incomplete_still_FAILED_with_keys_true", len(f28) == len(m.REQUIRED_TABLES), fails=f28)

RES["all_pass"] = all(t["ok"] for t in RES["tests"])
RES["leftover"] = dict((t, [p for p in mine(t) if m.alive(p)]) for t in RES["tmp_dirs"])
RES["finished"] = m.ts()
open(OUT, "x").write(json.dumps(RES, ensure_ascii=False, indent=1, default=str))
print("ALL_PASS", RES["all_pass"], "leftover", RES["leftover"])
