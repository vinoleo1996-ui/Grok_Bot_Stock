#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""1019–1023 专用补跑执行器 run_backfill_1019_1023_dbincr_v3_1.py（QuantLab Eng；方案 A；live=false）。

仿 docs/v2/audit/backfill_1014_1016/run_backfill_r_v3_1.py 的闸门/停树/quiet 形态；
Call A / Call B / 日历恢复链 / 核查对齐 docs/v2/audit/nightly_20261019/run_nightly_v1_dbincr_v3_1.py（sha f1910e8a…，仅作参考钉，本执行器绝不 subprocess 该驱动跑历史日）。

硬约束：
  - 禁止改 run_nightly_v1_dbincr_v3_1.py 加历史日豁免（禁方案 B）。
  - 禁止调用 run_nightly_v1_dbincr_v3_1.py --date <历史日>（驱动强制 ET 日==D）。
  - 本包只调用 scripts/nightly_update.py；date_list 串行，一次一个真实数据进程。
  - 窗口授权 .ok：output/data/ARCH_RUN_AUTH_DATA_BACKFILL_1019_1023.ok（sha 9e4359f9…）；
    须另有 Arch runner 审签的专用 runner .ok（sha_runner==本文件）；requires_dedicated_backfill_runner=true。
  - 叶25 窗 10:00–10:45 ET 硬停/不起跑；BLACKOUT 16:40–18:40；MemAvailable≥2.5GiB。
  - 自测/check-only 不起真实跑；未签 runner .ok 前不跑生产。

流程（每个 D ∈ date_list 串行）：
  P  marker 预检；双 .ok（auth + runner）；全表 SHA_KEYS 钉；guarded；quiet；MemAvailable。
  1  备份 trade_cal → PIN；快照 BEFORE。
  A  nightly_update.py --date D --steps daily_pull（env: PYTHONDONTWRITEBYTECODE=1 TSPRO_RELAY_TIMEOUT=115 TIER1_SKIP_CAL_REFRESH=1；SOURCE=relay 仅 .ok）。
     后：compare → cal_restore_v2 → 双核 pin_trade_cal（失败 P0）。
  B  --steps CALL_B_STEPS（14 步，不含 trade_cal/sw）；后再恢复链 + 核查。
  C  summary / REQUIRED_TABLES / freshness / trade_cal pin / scope compare。
退出码：同驱动；--check-only 通过退出 10（不写文件；可不要求 runner .ok 已签发，只报告状态）。
"""
import argparse, datetime, hashlib, json, os, re, secrets, signal, subprocess, sys, time, traceback
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
ROOT = "/workspace/QuantLab"
PY = "/usr/bin/python3"
HERE = ROOT + "/docs/v2/audit/backfill_1019_1023"
NIGHTLY_HERE = ROOT + "/docs/v2/audit/nightly_20261019"
DATE_LIST = ["20261019", "20261020", "20261021", "20261022", "20261023"]
AUTH_OK_PATH = ROOT + "/output/data/ARCH_RUN_AUTH_DATA_BACKFILL_1019_1023.ok"
AUTH_OK_SHA = "9e4359f9b6521e9d8d2b9578c7031ac6e79d42bd7dc4e3003e34a7c0c3e32714"
RUNNER_OK_PATH = ROOT + "/output/data/ARCH_RUN_AUTH_DATA_BACKFILL_1019_1023_RUNNER.ok"
ENABLE_OK_SHA = "4377eb592c18c3bed067c9a7dc775330a3d78f811adb6f51f550b0fa54ccbd73"
SHA_DRIVER_REF = "f1910e8ab054c30628184f6e451a77db9c7e3487c31023f0761e50e510e87f05"
PATH_DRIVER_REF = "docs/v2/audit/nightly_20261019/run_nightly_v1_dbincr_v3_1.py"
FORBIDDEN_DRIVER_BASENAME = "run_nightly_v1_dbincr_v3_1.py"
MEM_AVAILABLE_MIN_KB = 2621440  # 2.5 GiB
LEAF25_BLACKOUT = ((10, 0), (10, 45))  # 叶25 避让重计算
REQUIRES_DEDICATED_BACKFILL_RUNNER = True
PIN = "141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086"
TRADE_CAL = ROOT + "/data/v2/tushare_raw/trade_cal.parquet"
RAW = ROOT + "/data/v2/tushare_raw"
PIT_CAL = {ROOT + "/data/v2/calendar/trade_cal_sse_pit.parquet": "fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41",
           ROOT + "/data/v2/calendar/manifest.json": "7ccc911e8a3ed2e408f30db1f95f12eb71a6fea18003ba88a31246f941cc89a4"}
FROZEN = {ROOT + "/docs/v2/eng_sd1/paper_import_closure.json": "6919e7afe605cc4d1af48868a06b6550db66e3fd1923a3e61bdcc16c621bae20",  # 必须第一项（.ok pin_frozen_closure）
          ROOT + "/data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet": "89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c",  # Arch P3-4
          ROOT + "/data/v2/sw_l1_pit/industry_members_sw_l1.parquet": "87d769aaca06212186986af489f6507b6f0d98c8937f7a4476f97538562733b3",
          ROOT + "/data/v2/sw_pit/industry_members_sw_l1_pit.parquet": "0b1d3432e30f7cdd907df393299cd2f552e1121899239985a00113c4dfcd89f6"}
GAP_LIST = ROOT + "/output/data_gap_list/nightly_degraded_gaps.jsonl"  # v3.1：WARN 降级日期只追加（O_APPEND），一行一条
SNAP = ROOT + "/docs/v2/audit/nightly_sha_scope_snapshot_v2_20261018.py"
SCOPE = HERE + "/nightly_sha_scope_backfill_1019_1023.txt"
SCOPE_SHA = "c204fd5f8274ae58cf99d936c39409cb4fb5ca6e9f94a6a86bb55e4f7b0e48e8"
# daily_basic incr v3.1 — Arch：incr/transform 进 SHA_KEYS（原模块常量=死钉，已迁入）
# pin_daily_basic_transform：.ok/SHA_KEYS 值为 transform 指纹；check_pins 用 compute_transform_sha 对照（非文件 sha）
PIN_DAILY_BASIC_INCREMENTAL_SHA = "a7ac54b3ecdf33d338710df5c96f447fbec51affdcfbf167fb3e00648f678dd8"
PIN_DAILY_BASIC_TRANSFORM_SHA = "308b5054c39801116fd0eb19b4e4bd10bdccd4b4d40bfb67dd06a58fa67ab974"
PIN_DAILY_BASIC_INCREMENTAL_REL = "scripts/acquire/daily_basic_incremental.py"
COMPARE = NIGHTLY_HERE + "/cal_compare_v1.py"
RESTORE = NIGHTLY_HERE + "/cal_restore_v2.py"
FALLBACK = NIGHTLY_HERE + "/routine_fallback_v1.py"
TIER1_SHA = "5b70dfed08a237034b586ef9738e2c1b81607b20387a62df49a1e6994ba711cf"  # Arch 12:36：code .ok ed56e336 签 b630bca2→5b70dfed（原子写日历 + TIER1_SKIP_CAL_REFRESH）
# .ok 键 → 相对路径 → 钉值（Arch 2dada5ed 第 6 节全表；sha_routine_fallback 在定稿时填入）
SHA_KEYS = {
    "sha_cal_restore": ("docs/v2/audit/nightly_20261019/cal_restore_v2.py", "6686876bdcfc95f11d493b5201f55eb726e69e4894d8c96bfaf46ab1748387a4"),
    "sha_cal_compare": ("docs/v2/audit/nightly_20261019/cal_compare_v1.py", "74093ff3be4c431bab8c469307b207b43b8e1cff707dd0bac1319a7e265cddfc"),
    "sha_snapshot_tool": ("docs/v2/audit/nightly_sha_scope_snapshot_v2_20261018.py", "c930ed5c627bf937e6b5d139c52f18945f045286e78dba66cbe5adfab92ab79a"),
    "sha_scope": ("docs/v2/audit/backfill_1019_1023/nightly_sha_scope_backfill_1019_1023.txt", SCOPE_SHA),
    "sha_nightly_update": ("scripts/nightly_update.py", "2b4704e88a45e8bb173aa8f3375de9d9dc67a13b8c5501292ddf0a0fa3ebfd5b"),
    "sha_tier1_pull": ("scripts/acquire/tier1_pull.py", TIER1_SHA),
    "sha_tushare_proxy": ("quantlab/data_sources/tushare_proxy.py", "ae91f230560d445b4d2321e8e022d01b55773e168d4d842fc6987fa9458fc772"),
    "sha_relay_health": ("scripts/acquire/relay_health.py", "6d3ea9f57f63af8d82d6eeaf140a989aeb09cda941e6711c25f12fd3bbe0e17f"),
    "sha_adj_factor_incr": ("scripts/acquire/adj_factor_incr.py", "723726c5623a1739ee1fb1dcf97a6be6efd4532717a4c4411fb5e24dfd1422ad"),
    "sha_tier1_materialize": ("scripts/acquire/tier1_materialize.py", "7205ba43b4e4dc50c1ca9f546f6f54c359ad8c78f4707c2d2bb161d46829e65c"),
    "sha_etf_daily_adj_incr": ("scripts/acquire/etf_daily_adj_incr.py", "ae670dfc0da14f7aa90bb1d6edd3377b027f69dcb739987dc016388e45b02ae4"),
    "sha_eng_daily_panels": ("scripts/acquire/eng_daily_panels.py", "a754205397d22b6bb1109d92ee4040d65faedec2d37afd575f77e63da642f0be"),
    "sha_mid_large_universe_incr": ("scripts/acquire/mid_large_universe_incr.py", "fe4bbffe1c7c8e0a3f4d38a590acbbcaab61f53b08939722e9b503fa2901d64b"),
    "sha_light_event_windows_pull": ("scripts/acquire/_light_event_windows_pull.py", "f12660b90c01089278f01e22b3bdf53154780802668ed4ea90ea5c38c3fc9d71"),
    "sha_forecast_manifest_declare": ("scripts/acquire/forecast_manifest_declare.py", "f77673811aa2dd05d461cf895476212f52b05abc3f26212cba87ea30578bd731"),
    "sha_fill_hsgt_top10_extend": ("scripts/acquire/fill_hsgt_top10_extend.py", "36cff47c008244ee50f7fb2fcc5f6fd0588d7141901b3a23afe50c48f058e918"),
    "sha_cyq_perf_monthly": ("scripts/acquire/cyq_perf_monthly.py", "6aae6c1b8de7b37752fb5032c22ea65b698f252cc57f8e5af94b1e13d6e09c1f"),
    "sha_tier3_daily_snapshot": ("scripts/acquire/tier3_daily_snapshot.py", "64a71f5607439c5b09ddd92a8dfeffd94e4f5244297f83fbc5c65e3abfcf1067"),
    "sha_data_freshness_status": ("scripts/acquire/data_freshness_status.py", "a759d29788859b43783bac6360014347b2df0e4dce5949302a0908db511f1d50"),
    "sha_routine_fallback": ("docs/v2/audit/nightly_20261019/routine_fallback_v1.py", "559d1e017b1c53b1dd1cdffdc0571fc1d33a6157ea4437735421cc3fab271384"),
    "sha_daily_basic_incremental": ("scripts/acquire/daily_basic_incremental.py", "a7ac54b3ecdf33d338710df5c96f447fbec51affdcfbf167fb3e00648f678dd8"),
    "pin_daily_basic_transform": ("__computed__/daily_basic_transform_sha", "308b5054c39801116fd0eb19b4e4bd10bdccd4b4d40bfb67dd06a58fa67ab974"),
    "sha_driver_ref": ("docs/v2/audit/nightly_20261019/run_nightly_v1_dbincr_v3_1.py", SHA_DRIVER_REF),
}
CALL_B_STEPS = ["index_pull", "adj_factor", "bars", "daily_basic", "index", "etf_daily_adj", "eng_panels", "mid_large_universe",
                "events", "hsgt", "cyq", "tier3", "bundle", "freshness"]  # 不含 daily_pull、trade_cal、sw
RELAY_ONLY = {"hsgt", "cyq", "tier3"}
REQUIRED_TABLES = ("etf_daily_adj", "daily_ohlcv_raw_pit", "daily_basic", "mid_large_universe", "etf510300", "asof_ts")  # research_loop.py L633
GATED_APIS = ["daily", "daily_basic", "adj_factor", "stk_limit"]
ALL_APIS = GATED_APIS + ["suspend_d"]  # tier1_pull.py L102；原始文件 <api>/<D>.parquet（L59），临时文件 <D>.tmp.parquet（L61）
ROW_RATIO = 0.98
RSS_STOP_KB = 1484800   # 树合计停止线
RSS_HARD_KB = 1536000   # 单进程上限
SAMPLE_S = 5
TERM_WAIT_S = 10
WAIT_TIMEOUT_S = 60
CAL_RECHECK_S = 30
TOOL_TIMEOUT_S = {"snap": 900, "compare": 300, "restore": 300}
DAILY_PULL_MAX_MIN = 30
CALL_B_BUDGET_DEFAULT = 75  # 主 Agent 12:32
CALL_B_LATEST = "16:00"
START_NOT_BEFORE = "05:25"
RETRY_WAIT_MIN = 30
BLACKOUT = ((16, 40), (18, 40))
HARD_STOP = (15, 55)  # 对齐 plan R；叶25 另闸
QUIET_LOCK = ROOT + "/output/loop/RESEARCH_QUIET.lock"
HEALTHZ = "http://127.0.0.1:8795/healthz"
PGREP_WEB = r"(^|[ /])([k]line|[e]xport_static|[s]napshot|[g]en)\.py( |$)"          # Arch D-P2-1
PGREP_DATA = r"(^|[ /])([r]emaining_after_stk_surv|[n]ightly_update|[t]ier1_pull|[r]un_backfill_[a-z0-9_]+)\.py( |$)"
PGREP_WATCHER = r"(^|[ /])[r]elay_outage_backfill\.py( |$)"
PGREP_RECORD = "[s]cripts/acquire/|[n]ightly_update"
GUARDED = {94322: "remaining_after_stk_surv.py", 94403: "relay_outage_backfill.py"}  # 只能是 T 或已退出；驱动绝不发信号
MARK_DIR = ROOT + "/output/backfill_markers"
CHILD_ENV = {"PYTHONDONTWRITEBYTECODE": "1", "TSPRO_RELAY_TIMEOUT": "115"}  # Arch 12:36 / 12:38：恒设；SOURCE=relay 仅 .ok source_relay_only=true 时设
CALL_A_ENV = {"TIER1_SKIP_CAL_REFRESH": "1"}
NIGHTLY_MARK = "scripts/nightly_update.py"
CALL_A_MARKS = ("scripts/acquire/",)
CALL_B_MARKS = ("scripts/acquire/tier1_pull.py", "scripts/acquire/adj_factor_incr.py",
                "sys.path.insert(0,\x27scripts/acquire\x27);sys.path.insert(0,\x27.\x27);import tier1_materialize as m",
                "scripts/acquire/etf_daily_adj_incr.py", "scripts/acquire/eng_daily_panels.py", "scripts/acquire/mid_large_universe_incr.py",
                "scripts/acquire/_light_event_windows_pull.py", "scripts/acquire/forecast_manifest_declare.py",
                "scripts/acquire/fill_hsgt_top10_extend.py", "scripts/acquire/cyq_perf_monthly.py",
                "scripts/acquire/tier3_daily_snapshot.py", "scripts/acquire/data_freshness_status.py")  # nightly_update.py L28-43 逐个完整相对路径
ORPHAN_MARKS = ("scripts/acquire/", "import tier1_materialize", NIGHTLY_MARK)
RETRYABLE = {"MAX_RUN"}  # Arch 清单第 4 项：只有 MAX_RUN 可以重试
OK_KEYS_REQUIRED = ["ok_id", "ok_type", "date", "signed_by", "issued_at", "expires_et", "single_use", "live", "promotion_approved", "interpreter",
                    "sha_driver", "pin_trade_cal", "pin_frozen_closure", "daily_pull_max_min", "call_b_budget_min", "call_b_latest_finish",
                    "rss_stop_kb", "rss_hard_kb", "blackout_et", "allow_kill_scope", "allow_trade_cal_step", "allow_sw", "allow_force",
                    "allow_delete", "allow_commit"] + list(SHA_KEYS)
OK_KEYS_OPTIONAL_FMT = ["signed_et", "supersede_failed_marker_sha256", "allow_profile_relaxed_%s", "allow_daily_pull_retry_%s",
                        "allow_run_daily_pull_%s", "allow_run_call_b_%s", "allow_restore_trade_cal_%s", "allow_routine_fallback_restore_%s",
                        "allow_write_nightly_marker_%s", "allow_quarantine_mv_daily_raw_%s", "allow_create_research_quiet_lock_%s",
                        "allow_relay_partial_%s", "allow_hsgt_source_empty_warn_%s"]  # v3.1（主 Agent 13:19 / Arch 13:15），默认 false

R = dict(events=[], alerts=[], fail_reasons=[], prior_attempts=[], invocations=[], checks={}, quiet={}, reason_codes=[], reason_code_counts={}, warnings=[])
CFG = dict(npid=None, marks=None, expires=None, call_started=False, popen=None)
A = None
D = None
RUN_DIR = None
BACKUP = None
STAMP = None


# ---------------- 通用（沿用上一版，逐字） ----------------
def now():
    return datetime.datetime.now(ET)


def ts():
    return now().isoformat(timespec="seconds")


def ev(msg):
    line = "%s %s" % (ts(), msg)
    R["events"].append(line)
    print(line, flush=True)


def alert(level, msg):
    R["alerts"].append(dict(level=level, at=ts(), msg=msg))
    ev("ALERT %s %s" % (level, msg))


def fail(msg):
    R["fail_reasons"].append(msg)
    ev("FAIL " + msg)


def add_code(code):
    """reason_codes 去重（保留首次顺序），原始次数记在 reason_code_counts（Arch P3-2）。"""
    R["reason_code_counts"][code] = R["reason_code_counts"].get(code, 0) + 1
    if code not in R["reason_codes"]:
        R["reason_codes"].append(code)


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def hm(s):
    h, m = s.split(":")
    return now().replace(hour=int(h), minute=int(m), second=0, microsecond=0)


def in_blackout(t=None):
    t = t or now()
    return hm("%02d:%02d" % BLACKOUT[0]) <= t < hm("%02d:%02d" % BLACKOUT[1])


def fsync_dir(d):
    fd = os.open(d, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def write_new(path, text):
    d = os.path.dirname(path)
    tmp = os.path.join(d, ".%s.tmp.%d.%s" % (os.path.basename(path), os.getpid(), secrets.token_hex(4)))
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        os.write(fd, text.encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)
    try:
        os.link(tmp, path)  # 目标已存在即 FileExistsError
    finally:
        os.unlink(tmp)
    fsync_dir(d)


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


def ps_line(pid):
    return dict(pid=pid, state=proc_state(pid), ppid=ppid(pid), rss_kb=vmrss_kb(pid), cmd=cmdline(pid)[:200])


def descendants_pp(pid):
    """深度优先返回 (pid, 期望 PPID)，最深的在前。"""
    res = []
    for c in children(pid):
        res = descendants_pp(c) + [(c, pid)] + res
    return res


def starttime_epoch(pid):
    try:
        s = open("/proc/%d/stat" % pid).read()
        st = int(s[s.rfind(")") + 2:].split()[19])
        bt = None
        for ln in open("/proc/stat"):
            if ln.startswith("btime "):
                bt = int(ln.split()[1])
        return bt + st / os.sysconf("SC_CLK_TCK")
    except Exception:
        return None


def wait_gone(pid, secs):
    t0 = time.time()
    while alive(pid) and time.time() - t0 < secs:
        time.sleep(0.5)
    return not alive(pid)


def healthz():
    import urllib.request
    with urllib.request.urlopen(HEALTHZ, timeout=5) as r:
        return json.loads(r.read().decode("utf-8"))


# ---------------- 停止（Arch 2dada5ed D-P1-3 / 清单第 2 项） ----------------
def mark_ok(cl, marks):
    return any(m_ in cl for m_ in marks)


def signal_exact(pid, sig, marks, parent):
    """只发给确切 PID：发信号前核 cmdline（含任一标记）与 PPID（必须等于期望父）；Z / 不存在视为完成。GUARDED（94322、94403）永不发信号。"""
    if pid in GUARDED or pid == os.getpid() or pid <= 1:
        ev("SIGNAL refuse pid=%d（受保护或非法 PID，永不发信号）" % pid); return "refused"
    if isinstance(marks, str):
        marks = (marks,)
    if not alive(pid):
        ev("SIGNAL skip pid=%d 已退出或 Z" % pid); return "gone"
    cl = cmdline(pid); pp = ppid(pid)
    if not mark_ok(cl, marks) or pp != parent:
        why = ("cmdline 不含 %r" % (marks,)) if not mark_ok(cl, marks) else ("ppid=%s 期望 %s" % (pp, parent))
        ev("SIGNAL refuse pid=%d cmd=%r %s（不发信号）" % (pid, cl[:160], why)); return "refused"
    try:
        os.kill(pid, sig); ev("SIGNAL %s pid=%d ppid=%d" % (signal.Signals(sig).name, pid, pp)); return "sent"
    except ProcessLookupError:
        ev("SIGNAL pid=%d ESRCH" % pid); return "gone"


def stop_tree(npid, marks, reason_code, reason):
    """（1）核父 cmdline + PPID 后 SIGSTOP nightly；（2）重新枚举整棵树；（3）对每个后代 SIGSTOP 冻结；（4）从最深一层起 TERM + CONT，等 10 秒，仍在则 KILL；
    （5）SIGKILL nightly（已 STOP 的进程也会被 KILL）；之后 wait（带超时）与孤儿扫描由调用方做。任何 refused / still_alive 都记入 residual。"""
    me = os.getpid()
    rec = dict(reason_code=reason_code, reason=reason, at=ts(), npid=npid, steps=[], residual=[])
    rec["ps_before"] = [ps_line(x) for x in [npid] + descendants(npid)]
    ev("STOP_TREE npid=%d reason_code=%s reason=%s" % (npid, reason_code, reason))
    rec["steps"].append(("SIGSTOP_PARENT", npid, signal_exact(npid, signal.SIGSTOP, NIGHTLY_MARK, me)))
    tree = descendants_pp(npid)  # 父已冻结，名单不再增长
    rec["tree"] = [dict(pid=c, ppid=p_, cmd=cmdline(c)[:160]) for c, p_ in tree]
    for c, par in tree:
        rec["steps"].append(("SIGSTOP", c, signal_exact(c, signal.SIGSTOP, marks, par)))
    for c, par in tree:  # 最深在前
        r = signal_exact(c, signal.SIGTERM, marks, par)
        if r == "sent":
            signal_exact(c, signal.SIGCONT, marks, par)
            if wait_gone(c, TERM_WAIT_S):
                r = "term_ok"
            else:
                signal_exact(c, signal.SIGKILL, marks, par)
                r = "killed" if wait_gone(c, 5) else "still_alive"
        rec["steps"].append(("TERM_KILL", c, r))
        if r in ("refused", "still_alive"):
            rec["residual"].append(dict(pid=c, result=r, cmd=cmdline(c)[:160], state=proc_state(c)))
    rec["steps"].append(("SIGKILL_PARENT", npid, signal_exact(npid, signal.SIGKILL, NIGHTLY_MARK, me)))
    rec["ps_after"] = [ps_line(x) for x in [npid] + descendants(npid)]
    R["checks"].setdefault("stop_tree", []).append(rec)
    add_code(reason_code)
    return rec


def orphan_scan(seen, t0_epoch, tag, marks):
    """nightly 退出后扫 /proc：只对见过的本次子孙（cmdline 含标记）按确切 PID 停；PPID=1、启动晚于本次调用、cmdline 含 acquire / nightly 但没见过的进程
    只记录不发信号（Arch P3-A）。GUARDED 与驱动自身排除。"""
    me = os.getpid(); acted, logged = [], []
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        pid = int(name)
        if pid == me or pid in GUARDED or not alive(pid):
            continue
        cl = cmdline(pid); pp = ppid(pid)
        if pid in seen and (mark_ok(cl, marks) or NIGHTLY_MARK in cl):
            mk = (NIGHTLY_MARK,) if NIGHTLY_MARK in cl else marks
            r = signal_exact(pid, signal.SIGSTOP, mk, pp)
            r = signal_exact(pid, signal.SIGTERM, mk, pp)
            if r == "sent":
                signal_exact(pid, signal.SIGCONT, mk, pp)
                if not wait_gone(pid, TERM_WAIT_S):
                    signal_exact(pid, signal.SIGKILL, mk, pp)
                    r = "killed" if wait_gone(pid, 5) else "still_alive"
                else:
                    r = "term_ok"
            acted.append(dict(pid=pid, ppid=pp, cmdline=cl[:200], action=r))
        elif pid in seen:
            acted.append(dict(pid=pid, ppid=pp, cmdline=cl[:200], action="unmarked_seen_alive_not_signaled"))
        elif pp == 1 and mark_ok(cl, ORPHAN_MARKS):
            st = starttime_epoch(pid)
            if st is not None and st >= t0_epoch - 1:
                logged.append(dict(pid=pid, ppid=pp, cmdline=cl[:200], action="logged_only"))
    R["checks"]["orphans_" + tag] = dict(acted=acted, logged_only=logged)
    ev("ORPHAN_SCAN %s acted=%d logged_only=%d" % (tag, len(acted), len(logged)))
    if logged:
        alert("P1", "%s 后发现 PPID=1 的可疑进程（只记录，未发信号）%s" % (tag, [x["pid"] for x in logged]))
    return acted, logged


def pgrep_lines(pat):
    pg = subprocess.run(["pgrep", "-af", pat], stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=20)
    lines = [ln for ln in pg.stdout.splitlines() if ln.strip() and not ln.startswith("%d " % os.getpid())]
    return pg.returncode, lines


def pgrep_record(tag):
    """记录 pgrep -af [s]cripts/acquire/|[n]ightly_update（GUARDED 行单列）；只记录，不作闸门。"""
    rc, lines = pgrep_lines(PGREP_RECORD)
    other = [ln for ln in lines if int(ln.split()[0]) not in GUARDED]
    R["checks"].setdefault("pgrep_acquire_nightly", []).append(dict(tag=tag, at=ts(), rc=rc, lines=other,
                                                                    guarded=[ln for ln in lines if int(ln.split()[0]) in GUARDED]))
    if other:
        alert("P1", "pgrep %s 非空：%s" % (tag, other[:5]))
    return other


def guarded_check():
    """94322 / 94403：只能是 T 或已退出（S/R/D/其他 → 前置失败）；PID 被复用（cmdline 不符）视为原进程已退出并记录。另按 cmdline 查全部 relay_outage_backfill 进程。"""
    out, errs = {}, []
    for pid, name in GUARDED.items():
        st = proc_state(pid); cl = cmdline(pid) if st else ""
        if st is None or st == "Z":
            out[pid] = dict(state=st, verdict="exited")
        elif name not in cl:
            out[pid] = dict(state=st, cmd=cl[:120], verdict="pid_reused_original_exited")
        elif st == "T":
            tree = [dict(pid=c, state=proc_state(c), cmd=cmdline(c)[:120]) for c in descendants(pid)]  # 进程级 /proc/<pid>/stat
            bad = [x for x in tree if x["state"] not in (None, "Z", "T")]
            out[pid] = dict(state=st, verdict="stopped_ok" if not bad else "TREE_RUNNING_FAIL", tree=tree)
            for x in bad:
                errs.append("%d（%s）的后代 pid=%d state=%s，整棵树须为 T / Z / 不存在（Arch P1-3）" % (pid, name, x["pid"], x["state"]))
        else:
            out[pid] = dict(state=st, verdict="RUNNING_FAIL"); errs.append("%d（%s）state=%s，须为 T 或已退出" % (pid, name, st))
    rc, lines = pgrep_lines(PGREP_WATCHER)
    w = []
    for ln in lines:
        p_ = int(ln.split()[0]); st = proc_state(p_)
        tree = [dict(pid=c, state=proc_state(c)) for c in descendants(p_)] if st else []
        w.append(dict(pid=p_, state=st, cmd=ln[:160], tree=tree))
        if st not in (None, "Z", "T"):
            errs.append("relay_outage_backfill pid=%d state=%s，须为 T 或已退出" % (p_, st))
        for x in tree:
            if x["state"] not in (None, "Z", "T"):
                errs.append("relay_outage_backfill pid=%d 的后代 pid=%d state=%s" % (p_, x["pid"], x["state"]))
    out["relay_outage_backfill_all"] = w
    R["checks"]["guarded"] = out
    return "；".join(errs) or None


# ---------------- 子进程（全部带超时） ----------------
def child_env(extra=None):
    e = dict(os.environ, **CHILD_ENV)
    if CFG.get("source_relay"):
        e["SOURCE"] = "relay"
    if extra:
        e.update(extra)
    return e


class ToolTimeout(BaseException):
    """子工具超时：走统一收尾（继承 BaseException，不被内部 except Exception 吞掉）。"""


def seconds_left(deadline):
    return max(1, int((deadline - now()).total_seconds())) if deadline is not None else None


def run_tool(args, log_name, kind, phase_deadline=None):
    """审计工具（快照 / 比对 / 恢复）：超时 = min(工具默认, 所在阶段剩余, 距 16:40)；超时按确切 PID 停（核 cmdline + PPID），抛 ToolTimeout。"""
    assert args and args[0] != PY and os.path.basename(args[0]) not in ("python3", "python"), "run_tool 参数不得以解释器开头：%r" % (args[:2],)
    argv = ["nice", "-n", "10", PY] + args
    assert argv.count(PY) == 1
    lim = [TOOL_TIMEOUT_S[kind], seconds_left(hm("%02d:%02d" % BLACKOUT[0]))]
    if phase_deadline is not None:
        lim.append(seconds_left(phase_deadline))
    tmo = max(1, min(x for x in lim if x is not None))
    p = os.path.join(RUN_DIR, log_name)
    with open(p, "x") as fh:
        pr = subprocess.Popen(argv, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=fh, stderr=subprocess.STDOUT, env=child_env())
        try:
            rc = pr.wait(timeout=tmo)
        except subprocess.TimeoutExpired:
            r1 = signal_exact(pr.pid, signal.SIGTERM, args[0], os.getpid())
            if not wait_gone(pr.pid, TERM_WAIT_S):
                signal_exact(pr.pid, signal.SIGKILL, args[0], os.getpid())
            try:
                pr.wait(timeout=10)
            except subprocess.TimeoutExpired:
                pass
            R["checks"].setdefault("tool_timeouts", []).append(dict(tool=args[0], timeout_s=tmo, at=ts(), term=r1))
            raise ToolTimeout("%s 超时 %d 秒" % (os.path.basename(args[0]), tmo))
    return rc, open(p, encoding="utf-8", errors="replace").read()


def run_nightly(steps, tag, box_end, box_code, marks, extra_env=None):
    """起 nightly_update.py（cmd 只含一次解释器）；5 秒轮询；box_end 到（MAX_RUN / CALLB_TIMEOUT）、16:40（BLACKOUT）、RSS 超线即按 stop_tree 停；
    wait 带超时（HANG）；之后孤儿扫描。返回调用记录（含 reason_code）。"""
    cmd = [PY, "scripts/nightly_update.py", "--date", D, "--steps", steps]
    forbid_nightly_driver_invocation(cmd)
    assert cmd[0] == PY and cmd[1] != PY and cmd.count(PY) == 1, "解释器重复：%r" % (cmd[:2],)
    argv = ["nice", "-n", "10"] + cmd
    out = ROOT + "/logs/nightly/nightly_%s_%s_%s.out" % (D, tag, now().strftime("%H%M%S"))
    fh = open(out, "x")
    rss_log = open(os.path.join(RUN_DIR, "rss_%s.log" % tag), "x")
    black0 = hm("%02d:%02d" % BLACKOUT[0])
    t0 = ts(); t0e = time.time()
    CFG.update(call_started=True, marks=marks)
    p = subprocess.Popen(argv, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=fh, stderr=subprocess.STDOUT, env=child_env(extra_env))
    npid = p.pid; CFG.update(npid=npid, popen=p)
    ev("START %s npid=%d box_end=%s cmd=%s" % (tag, npid, box_end.isoformat(timespec="seconds"), " ".join(cmd)))
    seen, stopped, max_sum, max_one = set(), None, 0, 0
    while p.poll() is None:
        pids = [npid] + descendants(npid)
        seen.update(pids)
        rs = [(x, vmrss_kb(x)) for x in pids]
        s = sum(v for _, v in rs); one = max([v for _, v in rs] or [0])
        max_sum = max(max_sum, s); max_one = max(max_one, one)
        rss_log.write("%s\t%s\t%d\n" % (ts(), " ".join("%d:%d" % r for r in rs), s)); rss_log.flush()
        t = now()
        if s >= RSS_STOP_KB or one > RSS_HARD_KB:
            stopped = stop_tree(npid, marks, "RSS", "RSS 合计 %d kB / 单进程最大 %d kB" % (s, one)); break
        if t >= black0:
            stopped = stop_tree(npid, marks, "BLACKOUT", "16:40 禁跑开始"); break
        if in_leaf25():
            stopped = stop_tree(npid, marks, "LEAF25", "10:00–10:45 叶25 窗"); break
        if now() >= hm("%02d:%02d" % HARD_STOP):
            stopped = stop_tree(npid, marks, "HARD_STOP", "15:55 截止"); break
        if t >= box_end:
            stopped = stop_tree(npid, marks, box_code, "%s 时间盒到 %s" % (tag, box_end.isoformat(timespec="seconds"))); break
        time.sleep(SAMPLE_S)
    wait_timeout = False
    try:
        rc = p.wait(timeout=WAIT_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        rc = None; wait_timeout = True
        alert("P0", "%s wait 超时 %d 秒，nightly pid=%d 状态 %s" % (tag, WAIT_TIMEOUT_S, npid, proc_state(npid)))
        add_code("HANG")
    t1e = time.time(); CFG.update(npid=None, popen=None)
    fh.close(); rss_log.close()
    acted, logged = orphan_scan(seen, t0e, tag, marks)
    res_raw = (stopped or {}).get("residual", []) + [a for a in acted if a["action"] not in ("term_ok", "killed", "gone")]
    residual, _pids = [], set()
    for x in res_raw:  # Arch P3-2：同一 PID 只留一条，原始条数另记
        if x.get("pid") not in _pids:
            _pids.add(x.get("pid")); residual.append(x)
    if logged:  # Arch P2-2：PPID=1 可疑孤儿不发信号，但挡住 DONE
        add_code("ORPHAN"); fail("%s 后有 PPID=1 可疑孤儿 %s（只记录、不发信号；判 FAILED）" % (tag, [x["pid"] for x in logged]))
    still = [x for x in seen if alive(x)]
    rec = dict(cmd=" ".join(cmd), argv=argv, env_set=dict(CHILD_ENV, **(extra_env or {}), SOURCE=("relay" if CFG.get("source_relay") else None)),
               rc=rc, pid=npid, pids_seen=sorted(seen), started_et=t0, finished_et=ts(), start_epoch=t0e, end_epoch=t1e, out=out,
               rss_max_sum_kb=max_sum, rss_max_one_kb=max_one, residual_raw_count=len(res_raw), stopped=stopped, reason_code=(stopped or {}).get("reason_code") or ("HANG" if wait_timeout else None),
               wait_timeout=wait_timeout, orphans_acted=acted, orphans_logged_only=logged, residual=residual, seen_alive_after=still)
    if residual or still:
        alert("P0", "%s 停后仍有残留 residual=%s alive=%s" % (tag, [x.get("pid") for x in residual], still))
    ev("END %s rc=%s reason_code=%s" % (tag, rc, rec["reason_code"]))
    return rec


def tree_gone(rec):
    """恢复日历前确认本次调用见过的进程全部不在（Arch 清单第 7 项）。"""
    left = [x for x in rec.get("pids_seen", []) if alive(x)]
    R["checks"].setdefault("tree_gone_before_restore", []).append(dict(at=ts(), call=rec.get("cmd"), alive=left))
    return not left


def norm_date(v):
    """统一成 YYYYMMDD：接受 YYYYMMDD、YYYY-MM-DD、带时间的 ISO；其他返回 None。"""
    if v is None:
        return None
    s = str(v).strip()
    m_ = re.fullmatch(r"(\d{4})-?(\d{2})-?(\d{2})(?:[T ].*)?", s)
    return (m_.group(1) + m_.group(2) + m_.group(3)) if m_ else None


def parse_ts(v):
    try:
        t = datetime.datetime.fromisoformat(str(v))
        return t.timestamp() if t.tzinfo else None
    except Exception:
        return None


def check_summary(steps, rec, tag):
    """当日 summary（logs/nightly/<D>_summary.json；nightly_update.py L130-137 按 --steps 合并后整份重写，只有顶层 finished）：
    date==D；顶层 finished 与 mtime 都落在本次调用窗口内；所需步骤 status==ok 且无 skipped。被停的 nightly 不写 summary，读到的旧内容会因窗口不符而失败。"""
    f = []
    sp = ROOT + "/logs/nightly/%s_summary.json" % D
    try:
        sm = json.load(open(sp, encoding="utf-8")); mt = os.path.getmtime(sp)
    except Exception as e:
        f.append("summary 读不到 %r" % e); R["checks"]["summary_" + tag] = dict(fails=f); return f, {}
    lo, hi = rec["start_epoch"] - 1, rec["end_epoch"] + 1
    if str(sm.get("date")) != D:
        f.append("summary date=%r" % sm.get("date"))
    fin = parse_ts(sm.get("finished"))
    if fin is None or not (lo <= fin <= hi):
        f.append("summary finished=%r 不在 %s 窗口内（旧记录）" % (sm.get("finished"), tag))
    if not (lo <= mt <= hi):
        f.append("summary mtime 不在 %s 窗口内（旧记录）" % tag)
    st = sm.get("steps", {}); got = {}
    for k in steps:
        v = st.get(k) or {}
        got[k] = dict(status=v.get("status"), sec=v.get("sec"))
        if v.get("status") != "ok" or "skipped" in v:
            if tag == "callB" and k in RELAY_ONLY and CFG.get("relay_partial") and v.get("status") == "partial":
                warn_relay_partial(k, v); got[k]["warn"] = True; continue
            f.append("summary steps.%s status=%r（或含中转快速失败）" % (k, v.get("status")))
    R["checks"]["summary_" + tag] = dict(path=sp, sha256=sha256(sp), finished=sm.get("finished"), mtime=mt, window=[lo, hi], steps=got, fails=f)
    return f, got


def step_rows(step):
    """WARN 用的实际行数：cyq 取 tushare_raw/cyq_perf/<D>.parquet；tier3 取 tier3_daily/<kind>/<D>.parquet 合计；hsgt 取 tushare_raw/hsgt_top10/<D>.parquet。缺文件按 0。"""
    if step == "cyq":
        ps = [RAW + "/cyq_perf/%s.parquet" % D]
    elif step == "tier3":
        base = ROOT + "/data/v2/tier3_daily"
        ps = [os.path.join(base, k_, "%s.parquet" % D) for k_ in (sorted(os.listdir(base)) if os.path.isdir(base) else []) if k_ != "manifests"]
    else:
        ps = [RAW + "/hsgt_top10/%s.parquet" % D]
    n = 0
    for p in ps:
        if os.path.isfile(p):
            try:
                n += num_rows(p)
            except Exception:
                pass
    return n


def warn_relay_partial(step, v):
    why = "skipped" if "skipped" in v else "relay_partial"  # Eng 13:24 契约 F1：reason ∈ relay_partial | hsgt_source_empty | skipped
    R["warnings"].append(dict(step=step, date=D, actual_rows=int(step_rows(step)), reason=why))
    CFG.setdefault("warned_steps", set()).add(step)
    CFG.setdefault("warn_detail", {})[step] = dict(reason=why, nightly_status=v.get("status"), skipped=v.get("skipped"))
    alert("WARN", "call B %s partial 记 WARN（.ok allow_relay_partial_%s=true）" % (step, D))


def step_log_section(step, t0_epoch):
    """logs/nightly/<D>_<step>.log 中本次调用写的部分（nightly_update.py L114-118 每条命令前写 \\n=== <本地 ISO 时间> <cmd>）。"""
    lp = ROOT + "/logs/nightly/%s_%s.log" % (D, step)
    if not os.path.isfile(lp):
        return None, lp
    txt = open(lp, encoding="utf-8", errors="replace").read()
    parts = re.split(r"\n=== (\S+) ", "\n" + txt)
    sec = []
    for i in range(1, len(parts) - 1, 2):
        try:
            t = datetime.datetime.fromisoformat(parts[i]).timestamp()  # nightly 写的是本机本地时间（无时区，ET）
        except Exception:
            continue
        if t >= t0_epoch - 1:
            sec.append(parts[i + 1])
    return "\n".join(sec), lp


def check_cal_skip_log(rec):
    """Eng 12:40：TIER1_SKIP_CAL_REFRESH=1 时 tier1_pull 打印 cal refresh skipped (TIER1_SKIP_CAL_REFRESH=1)。缺失记异常（P1），恢复链照做。"""
    sec, lp = step_log_section("daily_pull", rec["start_epoch"])
    found = bool(sec) and "cal refresh skipped (TIER1_SKIP_CAL_REFRESH=1)" in sec
    R["checks"].setdefault("cal_refresh_skip_evidence", []).append(dict(log=lp, found=found, at=ts()))
    if not found:
        alert("P1", "call A 日志 %s 本次段落里没有 cal refresh skipped 行（异常；恢复链照做）" % lp)
    return found


def check_hsgt_log(rec):
    """hsgt 只认 rc=0（Arch D-P1-4(d)）。nightly 把 rc 0/2 都记 ok（nightly_update.py L119-120），rc 不落盘；
    fill_hsgt_top10_extend.py L225 打印 CHUNK DONE ... remaining=N auth_max=YYYYMMDD，L232-237：rc=0 ⇔ remaining==0 且 auth_max ≥ 20250601。"""
    if "hsgt" in CFG.get("warned_steps", set()):
        R["checks"]["hsgt_rc_check"] = dict(skipped_check=False, warned_relay_partial=True)
        return None
    sec, lp = step_log_section("hsgt", rec["start_epoch"])
    ms = re.findall(r"CHUNK DONE done=(\d+) fail=(\d+) remaining=(\d+) auth_max=(\d{8})", sec or "")
    res = dict(log=lp, chunk_done=ms[-1] if ms else None)
    ok = bool(ms) and int(ms[-1][2]) == 0 and ms[-1][3] >= "20250601" and "ABORT " not in (sec or "")
    res["rc0_equivalent"] = ok
    R["checks"]["hsgt_rc_check"] = res
    if not ok and CFG.get("hsgt_empty_warn") and ms and int(ms[-1][1]) == 0 and int(ms[-1][2]) > 0 and ms[-1][3] >= "20250601" and "ABORT " not in (sec or ""):
        empt = hsgt_empty_days(rec["start_epoch"])
        res["source_empty_days"] = empt
        res["log_ok0"] = re.findall(r"last=(\d{8}):ok:0\b", sec or "")
        if len(empt) == int(ms[-1][2]):  # 剩余天数 = 本次写出的 0 行文件数（save_day 只在 pull 成功即 HTTP 200 后写；needs() 700 字节门槛使其仍算 remaining，L46/L217）
            for d_ in empt:
                R["warnings"].append(dict(step="hsgt", date=d_, actual_rows=0, reason="hsgt_source_empty"))
            CFG.setdefault("warned_steps", set()).add("hsgt")
            CFG.setdefault("warn_detail", {})["hsgt"] = dict(reason="hsgt_source_empty", nightly_status="ok", empty_days=empt)
            alert("WARN", "hsgt 源端空日 %s 记 WARN（.ok allow_hsgt_source_empty_warn_%s=true）" % (empt, D))
            res["source_empty_warn"] = True
            return None
    return None if ok else "hsgt 本次日志无 remaining=0 的 CHUNK DONE（rc=2 / partial 视同失败）：%r" % (res["chunk_done"],)


def hsgt_empty_days(t0_epoch):
    """本次 call B 窗口内写出的 tushare_raw/hsgt_top10/<d>.parquet 且 num_rows == 0（fill_hsgt_top10_extend.py save_day L51-63：只有 pull 成功才写）。"""
    d0 = RAW + "/hsgt_top10"; out = []
    for f in (sorted(os.listdir(d0)) if os.path.isdir(d0) else []):
        p = os.path.join(d0, f)
        if re.fullmatch(r"[0-9]{8}[.]parquet", f) and os.path.getmtime(p) >= t0_epoch - 1:
            try:
                if num_rows(p) == 0:
                    out.append(f[:8])
            except Exception:
                pass
    return out


# ---------------- .ok / 钉 sha（Arch 清单 C 组 10–12、第 15 项） ----------------
def ok_known_keys():
    return set(OK_KEYS_REQUIRED) | {k % D if "%s" in k else k for k in OK_KEYS_OPTIONAL_FMT} | {"source_relay_only"}


def parse_ok(p):
    """只接受 key=value；ASCII；LF（拒 CR）；拒无法解析的行、行内注释（值含 #）、重复键、未知键、全文 DRAFT（不分大小写）；整行 # 注释允许。"""
    kv, errs = {}, []
    raw = open(p, "rb").read()
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError:
        errs.append("非 ASCII"); text = raw.decode("utf-8", "replace")
    if "\r" in text:
        errs.append("含 CR（只接受 LF）")
    if "draft" in text.lower():
        errs.append("全文含 DRAFT 字样")
    known = ok_known_keys() if D else None
    for i, ln in enumerate(text.split("\n"), 1):
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        m_ = re.match(r"^([A-Za-z0-9_]+)=(.*)$", s)
        if not m_:
            errs.append("L%d 无法解析（只接受 key=value）" % i); continue
        k, v = m_.group(1), m_.group(2).strip()
        if "#" in v:
            errs.append("L%d %s 含行内注释" % (i, k))
        if k in kv:
            errs.append("L%d %s 重复" % (i, k))
        if known is not None and k not in known:
            errs.append("L%d 未知键 %s" % (i, k))
        kv[k] = v
    return kv, errs


def truthy(v):
    return str(v).strip().lower() == "true"


def check_expiry(tag):
    exp = CFG.get("expires")
    if exp is None or exp <= now():
        return ".ok expires_et 已过期（%s）" % tag
    return None


def check_auth_ok():
    """窗口授权 .ok（Arch 已签 9e4359f9）；不是 nightly ok_type=run。"""
    if not os.path.isfile(AUTH_OK_PATH):
        return None, "窗口授权 .ok 不存在 %s" % AUTH_OK_PATH
    s = sha256(AUTH_OK_PATH)
    if s != AUTH_OK_SHA:
        return None, "窗口授权 .ok sha %s ≠ 钉 %s" % (s, AUTH_OK_SHA)
    kv, errs = {}, []
    for i, ln in enumerate(open(AUTH_OK_PATH, encoding="utf-8"), 1):
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        mm = re.match(r"^([A-Za-z0-9_]+)\s*[:=]\s*(.*)$", ln)
        if not mm:
            errs.append("L%d 无法解析" % i); continue
        k, v = mm.group(1), mm.group(2).strip()
        if "#" in v:
            errs.append("L%d %s 含行内注释" % (i, k))
        if k in kv:
            errs.append("L%d %s 重复" % (i, k))
        kv[k] = v
    if errs:
        return kv, "auth .ok 格式错误：%s" % "；".join(errs)
    if kv.get("ok_id") != "ARCH_RUN_AUTH_DATA_BACKFILL_1019_1023":
        return kv, "auth ok_id 不符：%r" % kv.get("ok_id")
    if kv.get("ok_type") not in ("backfill",) and kv.get("auth_type") != "backfill":
        return kv, "auth 非 backfill：ok_type=%r auth_type=%r" % (kv.get("ok_type"), kv.get("auth_type"))
    if kv.get("date_list") != ",".join(DATE_LIST):
        return kv, "auth date_list=%r 期望 %s" % (kv.get("date_list"), ",".join(DATE_LIST))
    if kv.get("sha_driver") != SHA_DRIVER_REF:
        return kv, "auth sha_driver 不符"
    if kv.get("sha_nightly_update") != SHA_KEYS["sha_nightly_update"][1]:
        return kv, "auth sha_nightly_update 不符"
    if kv.get("sha_daily_basic_incremental") != SHA_KEYS["sha_daily_basic_incremental"][1]:
        return kv, "auth sha_daily_basic_incremental 不符"
    if kv.get("pin_daily_basic_transform") != SHA_KEYS["pin_daily_basic_transform"][1]:
        return kv, "auth pin_daily_basic_transform 不符"
    if kv.get("sha_tier1_materialize") != SHA_KEYS["sha_tier1_materialize"][1]:
        return kv, "auth sha_tier1_materialize 不符"
    if kv.get("pin_trade_cal") != PIN:
        return kv, "auth pin_trade_cal 不符"
    if kv.get("enable_ok_sha256") != ENABLE_OK_SHA:
        return kv, "auth enable_ok_sha256 不符"
    if kv.get("allow_nightly_driver_for_historical_dates") == "true":
        return kv, "auth 不得允许 nightly 驱动跑历史日"
    if kv.get("requires_dedicated_backfill_runner") != "true":
        return kv, "auth requires_dedicated_backfill_runner 必须 true"
    if kv.get("forbid_use_of") and FORBIDDEN_DRIVER_BASENAME not in kv.get("forbid_use_of", ""):
        return kv, "auth forbid_use_of 未点名 nightly 驱动"
    for k in ("live", "promotion", "promotion_approved", "allow_paper", "allow_stream"):
        if truthy(kv.get(k)):
            return kv, "auth %s 必须 false" % k
    try:
        exp = datetime.datetime.fromisoformat(kv.get("expires_et", ""))
    except Exception:
        return kv, "auth expires_et 无法解析"
    if exp.tzinfo is None or exp <= now():
        return kv, "auth expires_et 无时区或已过期"
    CFG["expires"] = exp
    CFG["source_relay"] = kv.get("source_relay_only") == "true"
    CFG["budget"] = CALL_B_BUDGET_DEFAULT
    R["checks"]["auth_ok"] = dict(path=AUTH_OK_PATH, sha256=s, expires_et=kv.get("expires_et"),
                                  source_relay_only=CFG["source_relay"], keys=sorted(kv))
    return kv, None


def check_runner_ok(require=True):
    """专用 runner .ok（Arch runner 审后签发）；sha_runner 必须 == 本执行器文件 sha。"""
    me = sha256(os.path.abspath(__file__))
    R["checks"]["runner_self_sha"] = me
    if not os.path.isfile(RUNNER_OK_PATH):
        msg = "专用 runner .ok 不存在 %s（Arch 审包后签发）" % RUNNER_OK_PATH
        R["checks"]["runner_ok"] = dict(path=RUNNER_OK_PATH, present=False, self_sha=me)
        return None, (None if not require else msg)
    s = sha256(RUNNER_OK_PATH)
    kv, errs = {}, []
    for i, ln in enumerate(open(RUNNER_OK_PATH, encoding="utf-8"), 1):
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        mm = re.match(r"^([A-Za-z0-9_]+)\s*[:=]\s*(.*)$", ln)
        if not mm:
            errs.append("L%d 无法解析" % i); continue
        k, v = mm.group(1), mm.group(2).strip()
        if "#" in v:
            errs.append("L%d %s 含行内注释" % (i, k))
        if k in kv:
            errs.append("L%d %s 重复" % (i, k))
        kv[k] = v
    if errs:
        return kv, "runner .ok 格式错误：%s" % "；".join(errs)
    if kv.get("sha_runner", "").lower() != me:
        return kv, "runner .ok sha_runner 与本执行器 %s 不符" % me
    if kv.get("backfill_auth_ok_sha256") != AUTH_OK_SHA:
        return kv, "runner .ok backfill_auth_ok_sha256 须钉窗口授权 9e4359f9…"
    if kv.get("requires_dedicated_backfill_runner") != "true":
        return kv, "runner .ok requires_dedicated_backfill_runner 必须 true"
    for k, (rel, pin) in SHA_KEYS.items():
        if k not in kv:
            return kv, "runner .ok 缺 SHA_KEYS 键 %s" % k
        if kv[k].lower() != pin.lower():
            return kv, "runner .ok %s 与执行器钉不符" % k
    if kv.get("sha_driver_ref", kv.get("sha_driver", "")).lower() != SHA_DRIVER_REF:
        return kv, "runner .ok sha_driver(_ref) 须为 f1910e8a…"
    for k in ("live", "promotion_approved", "allow_paper", "allow_stream"):
        if truthy(kv.get(k)):
            return kv, "runner .ok %s 必须 false" % k
    try:
        exp = datetime.datetime.fromisoformat(kv.get("expires_et", ""))
    except Exception:
        return kv, "runner expires_et 无法解析"
    if exp.tzinfo is None or exp <= now():
        return kv, "runner expires_et 已过期"
    if CFG.get("expires") is None or exp < CFG["expires"]:
        CFG["expires"] = exp  # 取更紧
    if "source_relay_only" in kv:
        CFG["source_relay"] = kv["source_relay_only"] == "true"
    try:
        bud = int(kv.get("call_b_budget_min", str(CALL_B_BUDGET_DEFAULT)))
    except ValueError:
        bud = CALL_B_BUDGET_DEFAULT
    CFG["budget"] = bud
    CFG["relay_partial"] = truthy(kv.get("allow_relay_partial_%s" % D)) if D else False
    CFG["hsgt_empty_warn"] = truthy(kv.get("allow_hsgt_source_empty_warn_%s" % D)) if D else False
    R["checks"]["runner_ok"] = dict(path=RUNNER_OK_PATH, sha256=s, present=True, self_sha=me,
                                    expires_et=kv.get("expires_et"), call_b_budget_min=bud)
    return kv, None


def check_ok():
    """双 .ok：窗口授权（必）+ 专用 runner（正式跑必；--check-only 可缺，只报告）。"""
    akv, e = check_auth_ok()
    if e:
        return akv or {}, e
    require_runner = not (A is not None and A.check_only)
    rkv, e2 = check_runner_ok(require=require_runner)
    if e2:
        return rkv or akv or {}, e2
    # merge for downstream allow_* lookups (runner overrides)
    merged = dict(akv or {})
    if rkv:
        merged.update(rkv)
    R["checks"]["ok"] = dict(auth=R["checks"].get("auth_ok"), runner=R["checks"].get("runner_ok"),
                             expires_et=(merged.get("expires_et")), source_relay_only=CFG.get("source_relay"),
                             call_b_budget_min=CFG.get("budget"),
                             allow_relay_partial=CFG.get("relay_partial"),
                             allow_hsgt_source_empty_warn=CFG.get("hsgt_empty_warn"))
    return merged, None


def check_pins():
    got = {}
    for k, (rel, pin) in SHA_KEYS.items():
        if k == "pin_daily_basic_transform" or rel.startswith("__computed__/daily_basic_transform"):
            try:
                import importlib.util as _ilu
                _t1 = os.path.join(ROOT, "scripts/acquire/tier1_materialize.py")
                _inc = os.path.join(ROOT, "scripts/acquire/daily_basic_incremental.py")
                _spec_i = _ilu.spec_from_file_location("_ql_db_incr_pin", _inc)
                _mod_i = _ilu.module_from_spec(_spec_i); _spec_i.loader.exec_module(_mod_i)
                _spec_t = _ilu.spec_from_file_location("_ql_tier1_pin", _t1)
                _mod_t = _ilu.module_from_spec(_spec_t); _spec_t.loader.exec_module(_mod_t)
                s = _mod_i.compute_transform_sha(_mod_t)
            except Exception as e:
                return "transform_sha 复算失败：%s" % e
            got[k] = s
            if s != pin:
                return "钉 transform 不符 %s：%s（期望 %s）" % (k, s, pin)
            continue
        s = sha256(os.path.join(ROOT, rel)); got[rel] = s
        if s != pin:
            return "钉 sha 不符 %s：%s（期望 %s）" % (rel, s, pin)
    R["checks"]["pins"] = got
    if sys.executable != PY:
        return "解释器不是 %s" % PY
    return None


def in_leaf25(t=None):
    t = t or now()
    return hm("%02d:%02d" % LEAF25_BLACKOUT[0]) <= t < hm("%02d:%02d" % LEAF25_BLACKOUT[1])


def mem_available_kb():
    try:
        for ln in open("/proc/meminfo"):
            if ln.startswith("MemAvailable:"):
                return int(ln.split()[1])
    except Exception:
        return -1
    return -1


def start_window_check():
    """补跑窗：不要求 ET 日==D（历史日补跑）；禁叶25 10:00–10:45；禁 16:40–18:40；MemAvailable≥2.5GiB。"""
    t = now()
    if in_leaf25(t):
        return "叶25 窗 10:00–10:45 ET 禁重计算"
    if in_blackout(t):
        return "16:40–18:40 禁跑时段"
    if t >= hm("%02d:%02d" % HARD_STOP):
        return "已过 HARD_STOP %02d:%02d ET" % HARD_STOP
    mb = mem_available_kb()
    R["checks"]["mem_available_kb"] = mb
    if mb < MEM_AVAILABLE_MIN_KB:
        return "MemAvailable %d kB < %d（2.5GiB）" % (mb, MEM_AVAILABLE_MIN_KB)
    return None


def forbid_nightly_driver_invocation(cmd_list):
    """硬拒：任何 argv 含 FORBIDDEN_DRIVER_BASENAME 即失败（禁止用 nightly 驱动跑历史日）。"""
    joined = " ".join(cmd_list)
    if FORBIDDEN_DRIVER_BASENAME in joined:
        raise RuntimeError("FORBIDDEN: 禁止调用 %s 跑历史日：%r" % (FORBIDDEN_DRIVER_BASENAME, joined[:200]))


# ---------------- RESEARCH_QUIET（驱动绝不删除、移动锁） ----------------
LOCK_CREATE_NOT_BEFORE = "05:28"


def lock_text():
    return ("owner=Arch_by_Data\npurpose=backfill_1019_1023_%s\nset_at=%s\nrelease_when=output/backfill_markers/backfill_%s.DONE.json or .FAILED.json exists\nset_by_pid=%d\n"
            % (D, now().isoformat(timespec="seconds"), D, os.getpid()))


def lock_content_check():
    """补跑：purpose 允许 backfill_1019_1023 或 nightly_<D>；set_at 有时区即可（不强制 ==D）。"""
    try:
        kv = {}
        for ln in open(QUIET_LOCK, encoding="ascii").read().split("\n"):
            if "=" in ln:
                k, v = ln.split("=", 1); kv[k.strip()] = v.strip()
    except Exception as e:
        return "锁读不了或非 ASCII %r" % e
    R["quiet"]["lock_kv"] = kv
    pur = kv.get("purpose") or ""
    ok_pur = pur in ("backfill_1019_1023", "backfill_1019_1023_%s" % D, "nightly_%s" % D) or pur.startswith("backfill_1019_1023")
    if not ok_pur:
        return "锁 purpose=%r 不是 backfill_1019_1023* / nightly_%s" % (pur, D)
    if not kv.get("set_at"):
        return "锁缺 set_at"
    return None


def ensure_lock(kv, dry=False):
    q = R["quiet"]; q["lock_path"] = QUIET_LOCK
    if not os.path.isfile(QUIET_LOCK) and not dry:
        t0 = hm(LOCK_CREATE_NOT_BEFORE)
        if now() < t0:
            ev("锁尚未设置，等到 %s ET 再判断" % LOCK_CREATE_NOT_BEFORE)
            while now() < t0 and not os.path.isfile(QUIET_LOCK):
                time.sleep(5)
    if os.path.isfile(QUIET_LOCK):
        q.update(existed_at_check=True, created_by_data=False, lock_sha256=sha256(QUIET_LOCK), checked_at=ts())
        return lock_content_check()
    q["existed_at_check"] = False
    if not truthy(kv.get("allow_create_research_quiet_lock_%s" % D)):
        return "RESEARCH_QUIET.lock 不存在且 .ok 未授权 allow_create_research_quiet_lock_%s" % D
    if dry:
        q["would_create"] = True
        return None
    txt = lock_text()
    try:
        write_new(QUIET_LOCK, txt)  # .tmp + os.link；已存在即 FileExistsError，绝不覆盖
    except FileExistsError:
        q.update(existed_at_check=True, created_by_data=False, race="创建瞬间锁已出现，沿用", lock_sha256=sha256(QUIET_LOCK))
        return lock_content_check()
    q.update(created_by_data=True, created_at_et=ts(), lock_sha256=sha256(QUIET_LOCK), lock_text=txt,
             team_state_note="Data 于 %s 代 Arch 设 RESEARCH_QUIET.lock（owner=Arch_by_Data，pid %d）；释放由 Arch 例程移到 output/loop/_released/" % (ts(), os.getpid()))
    alert("INFO", "05:28 后锁仍不存在：Data 已代设 %s（记入 TEAM_STATE）" % QUIET_LOCK)
    return None


def pgrep_gates(tag):
    """Arch D-P2-1：两条锚定、括号转义的 pgrep 都必须为空；PGREP_DATA 命中的 GUARDED 进程只要是 T 就放行（主 Agent 12:32）。"""
    rc1, l1 = pgrep_lines(PGREP_WEB)
    rc2, l2 = pgrep_lines(PGREP_DATA)
    l2_bad = [ln for ln in l2 if not (int(ln.split()[0]) in GUARDED and proc_state(int(ln.split()[0])) == "T")]
    R["quiet"].setdefault("pgrep", []).append(dict(tag=tag, at=ts(), web=l1, data=l2, data_blocking=l2_bad))
    if l1:
        return "pgrep web 非空（%s）：%s" % (tag, l1[:3])
    if l2_bad:
        return "pgrep 真实数据进程非空（%s）：%s" % (tag, l2_bad[:3])
    return None


def quiet_gate(tag, full=True):
    rec = dict(tag=tag, at=ts())
    R["quiet"].setdefault("gates", []).append(rec)
    if not os.path.isfile(QUIET_LOCK):
        return "锁不存在（%s）" % tag
    if full:
        t0 = time.time(); h = {}
        while time.time() - t0 <= 90:
            try:
                h = healthz()
            except Exception as e:
                h = {"error": repr(e)[:200]}
            if h.get("quiet") is True:
                break
            time.sleep(3)
        rec["first"] = dict(at=ts(), healthz=h, waited_s=round(time.time() - t0, 1))
        if h.get("quiet") is not True:
            return "healthz 90 秒内未 quiet（%s）" % tag
        time.sleep(15)
    try:
        h = healthz()
    except Exception as e:
        return "healthz 复核失败 %r（%s）" % (e, tag)
    rec["recheck"] = dict(at=ts(), healthz=h)
    bad = [k for k in ("gen_running", "snapshot_running", "kline_running") if h.get(k) is not False]
    if h.get("quiet") is not True or bad or h.get("child_pids") != {}:
        return "healthz 复核不通过 %s（%s）" % (json.dumps(h, ensure_ascii=False)[:200], tag)
    return pgrep_gates(tag)


# ---------------- 日历恢复链（Arch 清单 B 组 7–8） ----------------
def cal_info(p):
    import pyarrow.parquet as pq
    t = pq.read_table(p, columns=["cal_date", "is_open"])
    v = sorted(str(x) for x in t.column("cal_date").to_pylist())
    opn = {str(c) for c, o in zip(t.column("cal_date").to_pylist(), t.column("is_open").to_pylist()) if str(o) in ("1", "1.0")}
    return dict(path=p, rows=t.num_rows, sha256=sha256(p), date_range=[v[0], v[-1]] if v else None), opn


def restore_native(tag):
    """cal_restore_v2 失败或超时时的驱动自带恢复：备份 sha==PIN → 同目录 O_EXCL 临时文件 → fsync → os.replace → fsync 目录 → 核 sha。"""
    if sha256(BACKUP) != PIN:
        return dict(ok=False, why="备份 sha 不是 PIN")
    d = os.path.dirname(TRADE_CAL)
    tmp = os.path.join(d, ".trade_cal.parquet.restore.%d.%s" % (os.getpid(), secrets.token_hex(4)))
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with open(BACKUP, "rb") as s:
            for b in iter(lambda: s.read(1 << 20), b""):
                os.write(fd, b)
        os.fsync(fd)
    finally:
        os.close(fd)
    if sha256(tmp) != PIN:
        return dict(ok=False, why="临时文件 sha 不是 PIN", tmp=tmp)
    os.replace(tmp, TRADE_CAL); fsync_dir(d)
    ok = sha256(TRADE_CAL) == PIN
    ev("RESTORE_NATIVE %s ok=%s" % (tag, ok))
    return dict(ok=ok, at=ts())


def compare_restore(tag, rec=None, phase_deadline=None):
    """每次调用后、异常 / 信号路径都做：确认树已不在 → post 副本 → cal_compare_v1 → cal_restore_v2（rc=2 复跑一次）→ 失败则 restore_native → 间隔 CAL_RECHECK_S 双核 sha。
    返回 (ok, changed)：ok=日历 == PIN；changed=恢复前 sha 不是 PIN（call B 后出现即判 FAILED，D-P2-5）。"""
    out = dict(tag=tag, at=ts())
    R["checks"].setdefault("calendar", []).append(out)
    if rec is not None and not tree_gone(rec):
        out["tree_alive"] = True
        alert("P0", "恢复前进程树仍在（%s），不恢复" % tag)
        return False, True
    pre = sha256(TRADE_CAL); out["sha_before_restore"] = pre
    changed = pre != PIN
    post = os.path.join(RUN_DIR, "trade_cal.parquet.post_%s" % tag)
    try:
        with open(TRADE_CAL, "rb") as s, open(post, "xb") as d_:
            d_.write(s.read()); d_.flush(); os.fsync(d_.fileno())
        out["post_copy"] = dict(path=post, sha256=sha256(post))
    except Exception as e:
        out["post_error"] = repr(e)[:200]
    rrc = None
    try:
        crc, _ = run_tool([COMPARE, "--current", post, "--backup", BACKUP, "--out", os.path.join(RUN_DIR, "cal_compare_%s.txt" % tag)],
                          "cal_compare_%s.log" % tag, "compare")
        out["compare_rc"] = crc
        if crc != 0:
            alert("P1", "日历比对 rc=%d（%s）" % (crc, tag))
        args = [RESTORE, "--backup", BACKUP, "--target", TRADE_CAL, "--keep-rewritten-dir", RUN_DIR]
        rrc, _ = run_tool(args, "cal_restore_%s.log" % tag, "restore")
        if rrc == 2:
            alert("P0", "cal_restore_v2 rc=2（%s），立即复跑一次" % tag)
            rrc, _ = run_tool(args, "cal_restore_%s_retry.log" % tag, "restore")
    except ToolTimeout as e:
        out["tool_timeout"] = str(e)
    out["restore_rc"] = rrc
    if rrc not in (0, 3) or sha256(TRADE_CAL) != PIN:
        out["native"] = restore_native(tag)
    s1 = sha256(TRADE_CAL); time.sleep(CAL_RECHECK_S); s2 = sha256(TRADE_CAL)
    out.update(sha_after=s1, sha_after_recheck=s2, recheck_s=CAL_RECHECK_S, changed=changed)
    ok = s1 == PIN and s2 == PIN
    if not ok:
        alert("P0", "纸面日历未恢复到 PIN（%s）：%s / %s" % (tag, s1, s2))
    return ok, changed


def cal_shas():
    d = {TRADE_CAL: sha256(TRADE_CAL)}
    for p in list(PIT_CAL) + list(FROZEN):
        d[p] = sha256(p)
    return dict(shas=d, trade_cal_is_pin=d[TRADE_CAL] == PIN, pit_cal_ok=all(d[p] == v for p, v in PIT_CAL.items()),
                frozen_ok=all(d[p] == v for p, v in FROZEN.items()), at=ts())


# ---------------- 原始文件（第 3 节：实测，不硬编码） ----------------
def ref_day(api):
    ds = sorted(f[:8] for f in os.listdir(os.path.join(RAW, api)) if re.fullmatch(r"\d{8}\.parquet", f) and f[:8] < D)
    return ds[-1] if ds else None


def num_rows(p):
    import pyarrow.parquet as pq
    return pq.ParquetFile(p).metadata.num_rows


def trade_date_range(p):
    """只读 trade_date 单列，统一成 YYYYMMDD；返回 [min, max] 或 None。"""
    import pyarrow.parquet as pq
    try:
        col = pq.read_table(p, columns=["trade_date"]).column("trade_date").to_pylist()
    except Exception:
        return None
    v = sorted({norm_date(x) for x in col if x is not None} - {None})
    return [v[0], v[-1]] if v else None


def raw_check():
    """返回 (bad, tmps, rec)。门槛：存在；rows ≥ 0.98 × 同接口上一开市日；daily_basic ≥ 0.98 × daily；trade_date 实测 min=max=D；无 .tmp.parquet。suspend_d 只记录。"""
    rec, bad, tmps = {}, [], []
    for api in ALL_APIS:
        dd = os.path.join(RAW, api)
        for f in (os.listdir(dd) if os.path.isdir(dd) else []):
            if f.endswith(".tmp.parquet"):
                tmps.append(os.path.join(dd, f))
        p = os.path.join(dd, "%s.parquet" % D)
        r = dict(path=p, exists=os.path.exists(p))
        if r["exists"]:
            r.update(rows=num_rows(p), sha256=sha256(p), date_range=trade_date_range(p))
        rd = ref_day(api) if os.path.isdir(dd) else None
        if rd:
            r["ref_day"] = rd; r["ref_rows"] = num_rows(os.path.join(dd, "%s.parquet" % rd))
        rec[api] = r
    for api in GATED_APIS:
        r = rec[api]
        if not r["exists"]:
            bad.append((api, "缺文件")); continue
        if r.get("ref_rows") is None or r["rows"] < ROW_RATIO * r["ref_rows"]:
            bad.append((api, "rows %s < %.2f × %s(%s)" % (r["rows"], ROW_RATIO, r.get("ref_rows"), r.get("ref_day"))))
        elif r.get("date_range") != [D, D]:
            bad.append((api, "trade_date 实测 %r ≠ [%s, %s]" % (r.get("date_range"), D, D)))
    if rec["daily"].get("rows") and rec["daily_basic"].get("exists") and rec["daily_basic"]["rows"] < ROW_RATIO * rec["daily"]["rows"]:
        if not any(a == "daily_basic" for a, _ in bad):
            bad.append(("daily_basic", "rows %d < %.2f × daily %d" % (rec["daily_basic"]["rows"], ROW_RATIO, rec["daily"]["rows"])))
    s = rec["suspend_d"]
    if s.get("rows") == 0:
        s["note"] = "0 行：无法区分无停牌与未发布（P3-5），只记录"
    elif s.get("rows") and s.get("date_range") not in (None, [D, D]):
        s["note"] = "suspend_d trade_date %r ≠ D（只记录，不作门槛）" % (s.get("date_range"),)
    return bad, tmps, rec


def quarantine(paths, allowed, k):
    """同盘 rename 到 RUN_DIR/quarantine/a<k>/<api>/；前后 sha；跨盘或目标已存在不动（不复制再删）。"""
    out = []
    for p in paths:
        if not os.path.exists(p):
            out.append(dict(path=p, done=False, why="不存在")); continue
        if not allowed:
            out.append(dict(path=p, done=False, why=".ok 未授权隔离，只报不动")); continue
        api = os.path.basename(os.path.dirname(p))
        qd = os.path.join(RUN_DIR, "quarantine", "a%d" % k, api); os.makedirs(qd, exist_ok=True)
        dst = os.path.join(qd, os.path.basename(p))
        if os.stat(p).st_dev != os.stat(qd).st_dev or os.path.lexists(dst):
            out.append(dict(path=p, done=False, why="跨盘或目标已存在，未动")); continue
        s0 = sha256(p); os.rename(p, dst); fsync_dir(os.path.dirname(p)); s1 = sha256(dst)
        out.append(dict(path=p, to=dst, sha_before=s0, sha_after=s1, done=s0 == s1 and not os.path.exists(p)))
        ev("QUARANTINE %s → %s" % (p, dst)); alert("P1", "不合格原始文件已隔离 %s → %s" % (p, dst))
    return out


# ---------------- marker ----------------
def marker_paths():
    return (os.path.join(MARK_DIR, "backfill_%s.DONE.json" % D), os.path.join(MARK_DIR, "backfill_%s.FAILED.json" % D))


def ok_path():
    """正式跑读专用 runner .ok；窗口授权另由 check_auth_ok 核。"""
    return A.ok or RUNNER_OK_PATH


def write_marker(ok):
    status = "OK" if ok else "FAILED"
    raw = R["checks"].get("raw_final") or {}
    steps = []
    for api in ALL_APIS:
        r = raw.get(api) or {}
        steps.append(dict(step=api, kind="raw_file", path=r.get("path", os.path.join(RAW, api, "%s.parquet" % D)), exists=r.get("exists"), rows=r.get("rows"),
                          sha256=r.get("sha256"), date_range=r.get("date_range")))  # 最终原位文件的实测值；未测则为 null
    try:
        ci, _ = cal_info(TRADE_CAL); steps.append(dict(ci, step="trade_cal", kind="calendar"))
    except Exception as e:
        steps.append(dict(step="trade_cal", kind="calendar", path=TRADE_CAL, error=repr(e)[:200]))
    dus = R["checks"].get("daily_update_status") or {}
    for t in REQUIRED_TABLES:
        v = (dus.get("tables") or {}).get(t) or {}
        steps.append(dict(step="status_" + t, kind="required_table", path=v.get("path"), rows=v.get("rows"), last_date=v.get("last_date"), sha256=v.get("sha256")))
    wd = CFG.get("warn_detail") or {}
    for k, v in (R["checks"].get("summary_steps") or {}).items():
        if k in RELAY_ONLY and k in wd:  # 降级步骤：status=WARN；只有这里允许出现 skipped（F4）
            e_ = dict(step=k, kind="call_b_step", status="WARN", sec=v.get("sec"), warn_reason=wd[k]["reason"], nightly_status=wd[k].get("nightly_status"))
            if wd[k].get("skipped"):
                e_["skipped"] = wd[k]["skipped"]
            if wd[k].get("empty_days"):
                e_["source_empty_days"] = wd[k]["empty_days"]
            steps.append(e_)
        else:
            steps.append(dict(step=k, kind="call_b_step", status=v.get("status"), sec=v.get("sec")))
    m = dict(schema="quantlab.v2.nightly_marker.v1", status=status, writer="driver", date=D, profile=A.profile,
             reason_codes=R["reason_codes"], reason_code_counts=R["reason_code_counts"], warnings=[dict(step=w_["step"], date=w_["date"], actual_rows=int(w_["actual_rows"]), reason=w_["reason"]) for w_ in R["warnings"]],
             ok_flags={"allow_relay_partial_%s" % D: bool(CFG.get("relay_partial")), "allow_hsgt_source_empty_warn_%s" % D: bool(CFG.get("hsgt_empty_warn"))},
             invocations=R["invocations"], prior_attempts=R["prior_attempts"], steps=steps,
             trade_cal_sha256=sha256(TRADE_CAL), trade_cal_pin=PIN,
             daily_update_status=dict(status=dus.get("status"), target_trade_date=dus.get("target_trade_date"),
                                      finished_at=dus.get("finished_at"), sha256=dus.get("sha256")),
             freshness=R["checks"].get("freshness"), snapshot_compare_rc=R["checks"].get("snapshot_compare_rc"),
             gates=R["checks"].get("gates"), research_quiet=dict((k, v) for k, v in R["quiet"].items() if k != "gates"),
             fail_reasons=R["fail_reasons"], alerts=R["alerts"], driver_sha256=R["checks"].get("driver_sha256"),
             ok_sha256=(R["checks"].get("ok") or {}).get("sha256"), superseded_failed_marker=R.get("supersede"), receipt=R.get("receipt"),
             live=False, promotion_approved=False, written_at_et=ts())
    if skipped_outside_allowed(m):  # Eng 13:24 契约 F4：skipped 只能出现在 cyq/tier3/hsgt 且 status=WARN 的 steps[] 项与 warnings[].reason
        if ok:
            m["status"] = "FAILED"; status = "FAILED"
            R["fail_reasons"].append("marker 白名单之外出现 skipped，降为 FAILED")
            m["fail_reasons"] = R["fail_reasons"]
        m = scrub_skipped(m)
    txt = json.dumps(m, ensure_ascii=False, indent=1)
    os.makedirs(MARK_DIR, exist_ok=True)
    path = os.path.join(MARK_DIR, "nightly_%s.%s.json" % (D, "DONE" if status == "OK" else "FAILED"))
    write_new(path, txt)  # 每次运行只写这一个 marker；已存在即 FileExistsError
    R["marker"] = dict(path=path, sha256=sha256(path), status=status)
    print("%s MARKER %s %s sha256=%s" % (ts(), status, path, R["marker"]["sha256"]), flush=True)
    return status


def _allowed_step(x):
    return isinstance(x, dict) and x.get("step") in RELAY_ONLY and x.get("status") == "WARN"


def skipped_outside_allowed(m):
    """F4：去掉白名单 WARN 步骤项与 warnings[].reason 后，全文（键与值，不分大小写）不得再含 skipped。"""
    t = dict(m)
    t["steps"] = [x for x in m.get("steps", []) if not _allowed_step(x)]
    t["warnings"] = [dict(w_, reason=None) for w_ in m.get("warnings", [])]
    return "skipped" in json.dumps(t, ensure_ascii=False).lower()


def scrub_skipped(m):
    """白名单之外的 skipped 一律改写为 not_run（键与值）；白名单项与 warnings 原样保留。"""
    def sc(o):
        if isinstance(o, dict):
            return dict((re.sub("(?i)skipped", "not_run", k) if isinstance(k, str) else k, sc(v)) for k, v in o.items())
        if isinstance(o, list):
            return [sc(v) for v in o]
        return re.sub("(?i)skipped", "not_run", o) if isinstance(o, str) else o
    keep_w = m.get("warnings", [])
    out = sc(dict((k, v) for k, v in m.items() if k not in ("steps", "warnings")))
    out["steps"] = [x if _allowed_step(x) else sc(x) for x in m.get("steps", [])]
    out["warnings"] = keep_w
    return out


def marker_precheck():
    """只读。DONE 已存在 → 拒绝；FAILED 已存在 → 只有 .ok supersede_failed_marker_sha256 等于其全长 sha 才可继续（稍后移走）。"""
    done, failed = marker_paths()
    if os.path.lexists(done):
        return "DONE marker 已存在 %s" % done
    if not os.path.lexists(failed):
        return None
    want = ""
    if os.path.isfile(ok_path()):
        want = parse_ok(ok_path())[0].get("supersede_failed_marker_sha256", "").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}", want):
        return "FAILED marker 已存在，.ok 没有合法的 supersede_failed_marker_sha256（须为 64 位十六进制全长；true 无效）"
    cur = sha256(failed)
    if cur != want:
        return "FAILED marker sha256 %s 与 .ok supersede_failed_marker_sha256 %s 不符" % (cur, want)
    R["supersede"] = dict(path=failed, sha256=cur, state="pending")
    return None


def supersede_failed():
    s = R.get("supersede")
    if not s:
        return None
    sd = os.path.join(MARK_DIR, "_superseded"); os.makedirs(sd, exist_ok=True)
    dst = os.path.join(sd, "backfill_%s.FAILED.%s.%s.json" % (D, s["sha256"][:12], STAMP))
    if os.path.lexists(dst) or os.stat(s["path"]).st_dev != os.stat(sd).st_dev:
        return "无法同盘移动旧 FAILED marker 到 %s" % dst
    if sha256(s["path"]) != s["sha256"]:
        return "旧 FAILED marker 在检查后被改动"
    os.rename(s["path"], dst); fsync_dir(MARK_DIR); fsync_dir(sd)
    ok = sha256(dst) == s["sha256"] and not os.path.lexists(s["path"])
    s.update(state="moved" if ok else "move_check_failed", to=dst, at=ts())
    ev("SUPERSEDE %s → %s ok=%s" % (s["path"], dst, ok))
    return None if ok else "移动旧 FAILED marker 后核对失败"


CHECK_ONLY_EXIT = 10
ABNORMAL_EXIT = 11


def finish(code, ok):
    """唯一出口：先忽略 TERM/INT/HUP；记录收尾日历 sha 与 pgrep；先写回执，最后写唯一 marker；锁与 .ok 不删不动。"""
    ignore_signals()
    if A is not None and A.check_only:
        print(json.dumps(dict(check_only=True, exit=code, fail_reasons=R["fail_reasons"], quiet=R["quiet"], guarded=R["checks"].get("guarded"),
                              supersede=R.get("supersede")), ensure_ascii=False, indent=1, default=str))
        sys.exit(code)
    if R.get("no_write"):
        print("%s EXIT 2 未写任何文件：%s" % (ts(), "；".join(R["fail_reasons"])), flush=True)
        sys.exit(2)
    try:
        R["checks"]["cal_sha_post"] = cal_shas()
        if not R["checks"]["cal_sha_post"]["pit_cal_ok"] or not R["checks"]["cal_sha_post"]["frozen_ok"]:
            ok = False; R["fail_reasons"].append("PIT 日历或冻结 closure sha 变化")
    except Exception as e:
        R["checks"]["cal_sha_post"] = dict(error=repr(e)[:200])
    if CFG.get("call_started") and not CFG.get("pgrep_post"):
        CFG["pgrep_post"] = True
        try:
            pgrep_record("post")
        except Exception as e:
            R["checks"]["pgrep_post_error"] = repr(e)[:200]
    R["exit"] = code if (code != 0 or ok) else 1
    if R["warnings"]:
        try:
            os.makedirs(os.path.dirname(GAP_LIST), exist_ok=True)
            fd = os.open(GAP_LIST, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
            try:
                for w_ in R["warnings"]:
                    os.write(fd, (json.dumps(dict(w_, run=STAMP, recorded_et=ts(), source="run_nightly_v1"), ensure_ascii=False) + "\n").encode("utf-8"))
                os.fsync(fd)
            finally:
                os.close(fd)
            R["gap_list"] = dict(path=GAP_LIST, appended=len(R["warnings"]))
        except Exception as e:
            R["gap_list"] = dict(path=GAP_LIST, error=repr(e)[:200])
    R["finished_et"] = ts()
    rp = os.path.join(HERE, "driver_receipt_%s.json" % STAMP)
    try:
        write_new(rp, json.dumps(R, ensure_ascii=False, indent=1, default=str))
        R["receipt"] = dict(path=rp, sha256=sha256(rp))
    except Exception as e:
        R["receipt"] = dict(error=repr(e)[:200])
    try:
        write_marker(ok and R["exit"] == 0)
    except FileExistsError:
        print("%s ALERT P0 marker 已被他人写出，不写第二份" % ts(), flush=True); sys.exit(3)
    except Exception as e:
        print("%s ALERT P0 marker 写入失败 %r" % (ts(), e), flush=True); sys.exit(3)
    sys.exit(R["exit"])


# ---------------- main ----------------
def status_rows(s):
    return {t: ((s.get("tables") or {}).get(t) or {}).get("rows") for t in REQUIRED_TABLES}


def read_json(p):
    try:
        d = json.load(open(p, encoding="utf-8")); d["_sha256"] = sha256(p); return d
    except Exception as e:
        return {"_error": repr(e)[:200]}



def run_one_date(kv, D_arg):
    """对单个历史日 D 执行 Call A → 恢复链 → Call B → 恢复链 → 核查（串行）。"""
    global D, RUN_DIR, BACKUP, STAMP
    D = D_arg
    STAMP = now().strftime("%Y%m%dT%H%M%S")
    R["date"] = D
    R.setdefault("dates_done", [])
    ev("==== BEGIN DATE %s ====" % D)
    sw = start_window_check()
    R["checks"]["start_window_%s" % D] = sw or "ok"
    if sw:
        fail("PRE %s %s" % (D, sw)); return False
    e = pgrep_gates("pre_%s" % D)
    if e:
        fail("PRE %s %s" % (D, e)); return False
    # per-date relay_partial flags from runner/auth merged kv
    CFG["relay_partial"] = truthy(kv.get("allow_relay_partial_%s" % D))
    CFG["hsgt_empty_warn"] = truthy(kv.get("allow_hsgt_source_empty_warn_%s" % D))
    os.makedirs(ROOT + "/_recovery/data/backfill_%s" % D, exist_ok=True)
    RUN_DIR = ROOT + "/_recovery/data/backfill_%s/run_%s" % (D, STAMP)
    os.mkdir(RUN_DIR)

    bk = os.path.join(RUN_DIR, "trade_cal.parquet.141078fa")
    with open(TRADE_CAL, "rb") as s, open(bk, "xb") as d_:
        d_.write(s.read()); d_.flush(); os.fsync(d_.fileno())
    st_ = os.stat(TRADE_CAL); os.utime(bk, ns=(st_.st_atime_ns, st_.st_mtime_ns))
    b1, b2 = sha256(TRADE_CAL), sha256(bk)
    R["checks"]["backup_%s" % D] = dict(path=bk, live_sha=b1, backup_sha=b2, live_inode=st_.st_ino)
    if b1 != PIN or b2 != PIN:
        alert("P0", "跑前 trade_cal 或备份 sha 不是 PIN"); fail("PRE %s trade_cal 不是 PIN" % D); return False
    os.chmod(bk, 0o444); BACKUP = bk
    R["checks"]["cal_sha_pre_%s" % D] = cal_shas()
    precal = R["checks"]["cal_sha_pre_%s" % D]
    if not precal["pit_cal_ok"] or not precal["frozen_ok"]:
        fail("PRE %s PIT 日历或冻结 closure sha 不符" % D); return False
    ci, opn = cal_info(TRADE_CAL)
    R["checks"]["trade_cal_pin_info_%s" % D] = dict(ci, d_is_open=D in opn)
    if D not in opn:
        fail("PRE PIN 日历里 %s 不是开市日" % D); return False
    st0 = read_json(ROOT + "/output/daily_update_status.json")
    R["checks"]["status_before_%s" % D] = R["checks"]["status_before"] = dict(rows=status_rows(st0), sha256=st0.get("_sha256"), finished_at=st0.get("finished_at"))
    rc, _ = run_tool([SNAP, "snap", SCOPE, os.path.join(RUN_DIR, "snap_before.txt"), "--expect-scope-sha", SCOPE_SHA], "snap_before.log", "snap")
    if rc != 0:
        fail("PRE %s 快照 BEFORE rc=%d" % (D, rc)); return False

    budget = CFG.get("budget", CALL_B_BUDGET_DEFAULT)
    max_retry = 0
    if A.profile == "relaxed":
        try:
            max_retry = max(0, min(2, int(kv.get("allow_daily_pull_retry_%s" % D, "0"))))
        except ValueError:
            max_retry = 0
    allow_q = truthy(kv.get("allow_quarantine_mv_daily_raw_%s" % D))
    black0 = hm("%02d:%02d" % BLACKOUT[0]); latest = hm(CALL_B_LATEST)
    k, final, no_more, pending_bad = 0, None, False, []
    pgrep_record("pre_%s" % D)
    while True:
        k += 1
        xe = check_expiry("callA_%s_a%d" % (D, k))
        if xe:
            fail(xe); no_more = True; break
        sw2 = start_window_check()
        if sw2:
            fail(sw2); no_more = True; break
        box_end = min(now() + datetime.timedelta(minutes=DAILY_PULL_MAX_MIN), black0, hm("%02d:%02d" % HARD_STOP))
        # also don't cross into leaf25 if we're before it
        leaf0 = hm("%02d:%02d" % LEAF25_BLACKOUT[0])
        if now() < leaf0 < box_end:
            box_end = min(box_end, leaf0)
        rec = run_nightly("daily_pull", "callA_%s_a%d" % (D, k), box_end, "MAX_RUN", CALL_A_MARKS, CALL_A_ENV)
        rec["attempt"] = k
        check_cal_skip_log(rec)
        cal_ok, changed = compare_restore("a%d_%s" % (k, D), rec)
        rec.update(calendar_restored=cal_ok, calendar_changed_by_call=changed)
        if not cal_ok:
            R["prior_attempts"].append(rec); fail("P0 日历未恢复（%s a%d）" % (D, k)); add_code("P0"); return False
        bad, tmps, raw = raw_check()
        sfs, _ = check_summary(["daily_pull"], rec, "callA_%s_a%d" % (D, k))
        rec.update(raw=raw, bad=bad, tmp_left=tmps, summary_fails=sfs)
        dirty = bool(rec["residual"] or rec["seen_alive_after"] or rec["wait_timeout"] or rec["orphans_logged_only"])
        if rec["rc"] == 0 and not rec["stopped"] and not bad and not tmps and not sfs and not dirty:
            final = rec; R["checks"]["raw_final_%s" % D] = raw; R["checks"]["raw_final"] = raw; break
        code = rec["reason_code"] or "ATTEMPT_FAILED"
        rec["quarantine"] = quarantine(tmps + [os.path.join(RAW, a, "%s.parquet" % D) for a, _ in bad], allow_q, k)
        R["prior_attempts"].append(rec)
        pending_bad = tmps + [os.path.join(RAW, a, "%s.parquet" % D) for a, _ in bad]
        R["checks"]["raw_final_%s" % D] = raw; R["checks"]["raw_final"] = raw
        if dirty:
            no_more = True; fail("daily_pull %s 第 %d 次停后有残留（%s）" % (D, k, code)); break
        if A.profile != "relaxed" or code not in RETRYABLE:
            no_more = True; fail("daily_pull %s 第 %d 次失败 reason_code=%s" % (D, k, code)); break
        if k > max_retry:
            no_more = True; fail("daily_pull %s MAX_RUN 重试用完" % D); break
        orph = R["checks"].get("orphans_callA_%s_a%d" % (D, k)) or {}
        still = [p for p in pending_bad if os.path.exists(p)]
        nxt = now() + datetime.timedelta(minutes=RETRY_WAIT_MIN)
        cond = dict(a_tree_and_orphans_empty=not orph.get("acted") and not orph.get("logged_only"), b_calendar_pin=cal_ok,
                    c_quarantined=not still and all(x.get("done") for x in rec["quarantine"] if x.get("why") != "不存在"),
                    d_count_ok=k <= max_retry,
                    e_time_ok=nxt + datetime.timedelta(minutes=DAILY_PULL_MAX_MIN + budget) <= latest and nxt + datetime.timedelta(minutes=DAILY_PULL_MAX_MIN) <= black0)
        rec["retry_conditions"] = cond
        if not all(cond.values()):
            no_more = True; fail("重试条件不满足 %s" % [c for c, v in cond.items() if not v]); break
        alert("P1", "daily_pull %s 第 %d 次 MAX_RUN；%d 分钟后重试" % (D, k, RETRY_WAIT_MIN))
        time.sleep(RETRY_WAIT_MIN * 60)
        qe = quiet_gate("retry_%s_a%d" % (D, k + 1), full=True)
        if qe:
            no_more = True; fail("重试前 quiet 不通过：%s" % qe); break
    if final:
        R["invocations"].append(dict(name="daily_pull", date=D, cmd=final["cmd"], rc=final["rc"], pid=final["pid"], env_set=final["env_set"],
                                     started_et=final["started_et"], finished_et=final["finished_et"], attempt=final["attempt"]))

    rb = None
    b_cmd = "%s scripts/nightly_update.py --date %s --steps %s" % (PY, D, ",".join(CALL_B_STEPS))
    forbid_nightly_driver_invocation(b_cmd.split())
    if final and not no_more:
        start_b = now()
        g_time = start_b + datetime.timedelta(minutes=budget) <= latest
        g_black = not in_blackout(start_b) and not in_leaf25(start_b) and start_b + datetime.timedelta(minutes=budget) <= black0
        g_sha = sha256(TRADE_CAL) == PIN
        g_exp = check_expiry("callB_%s" % D)
        lk = sha256(QUIET_LOCK) if os.path.isfile(QUIET_LOCK) else None
        g_lock = lk is not None and lk == R["checks"]["lock_sha_call_a"]["baseline"]
        R["checks"]["call_b_gate_%s" % D] = dict(at=start_b.isoformat(timespec="seconds"), budget_min=budget, latest_finish=CALL_B_LATEST,
                                                 time_ok=g_time, blackout_ok=g_black, sha_ok=g_sha, expiry_ok=not g_exp, lock_sha_now=lk, lock_sha_unchanged=g_lock)
        qe = g_exp or (None if g_lock else "RESEARCH_QUIET.lock sha 与 call A 前不同或已不存在") or quiet_gate("pre_call_b_%s" % D, full=False)
        if g_time and g_black and g_sha and not qe:
            box_end = min(start_b + datetime.timedelta(minutes=budget), latest, hm("%02d:%02d" % HARD_STOP))
            leaf0 = hm("%02d:%02d" % LEAF25_BLACKOUT[0])
            if start_b < leaf0 < box_end:
                box_end = min(box_end, leaf0)
            rb = run_nightly(",".join(CALL_B_STEPS), "callB_%s" % D, box_end, "CALLB_TIMEOUT", CALL_B_MARKS)
            R["invocations"].append(dict(name="call_b", date=D, cmd=rb["cmd"], rc=rb["rc"], pid=rb["pid"], env_set=rb["env_set"], started_et=rb["started_et"],
                                         finished_et=rb["finished_et"], box_end=box_end.isoformat(timespec="seconds"), reason_code=rb["reason_code"]))
            if rb["stopped"]:
                fail("call B %s 被停 reason_code=%s" % (D, rb["reason_code"]))
            elif rb["rc"] != 0:
                fail("call B %s rc=%s" % (D, rb["rc"]))
            if rb["residual"] or rb["seen_alive_after"] or rb["wait_timeout"]:
                fail("call B %s 停后有残留或 wait 超时" % D)
            ok_b, changed_b = compare_restore("callB_%s" % D, rb)
            if changed_b:
                fail("call B %s 期间 trade_cal 被改动" % D)
            if not ok_b:
                fail("P0 call B 后日历未恢复"); add_code("P0"); return False
        else:
            why = "time" if not g_time else ("blackout/leaf25" if not g_black else ("trade_cal sha" if not g_sha else qe))
            R["invocations"].append(dict(name="call_b", date=D, cmd=b_cmd, rc=None, not_run_reason=why))
            add_code("CALLB_GATE"); fail("call B %s 未起：%s" % (D, why))
    else:
        R["invocations"].append(dict(name="call_b", date=D, cmd=b_cmd, rc=None, not_run_reason="daily_pull 未成功或被停"))
        fail("call B %s 未起：daily_pull 未成功或被停" % D)

    if rb is not None:
        post_checks(rb)
    rc, out = run_tool([SNAP, "snap", SCOPE, os.path.join(RUN_DIR, "snap_after.txt"), "--expect-scope-sha", SCOPE_SHA], "snap_after.log", "snap")
    crc, cout = run_tool([SNAP, "compare", SCOPE, os.path.join(RUN_DIR, "snap_before.txt"), os.path.join(RUN_DIR, "snap_after.txt"),
                          "--expect-scope-sha", SCOPE_SHA], "snap_compare.log", "snap") if rc == 0 else (rc, "")
    R["checks"]["snapshot_compare_rc_%s" % D] = crc
    if crc != 0 or "META_ONLY_FAIL" in cout:
        fail("快照 compare %s rc=%s" % (D, crc))
    if sha256(TRADE_CAL) != PIN:
        alert("P0", "收尾时 trade_cal 不是 PIN"); fail("收尾时 trade_cal 不是 PIN"); add_code("FINAL_CAL_MISMATCH")
        ok_f, _ = compare_restore("final_%s" % D)
        if not ok_f:
            fail("P0 收尾恢复后日历仍不是 PIN"); add_code("P0"); return False
        return False
    inv_d = [i for i in R["invocations"] if i.get("date") == D]
    date_ok = (len(inv_d) == 2 and all(i.get("rc") == 0 for i in inv_d)
               and all(("--date %s" % D) in (i.get("cmd") or "") for i in inv_d)
               and not any(D in fr for fr in R["fail_reasons"]))
    if date_ok:
        R["dates_done"].append(D)
        ev("==== DATE %s OK ====" % D)
        return True
    ev("==== DATE %s FAIL ====" % D)
    return False


def main_inner():
    global A, D, RUN_DIR, BACKUP, STAMP
    ap = argparse.ArgumentParser(description="1019–1023 专用补跑执行器（daily_basic incr v3.1；方案 A）")
    ap.add_argument("--date", default=None, help="可选：只跑单个 D（须 ∈ DATE_LIST）；默认串行全部")
    ap.add_argument("--profile", choices=["strict", "relaxed"], default="strict")
    ap.add_argument("--ok", default=None, help="兼容占位；实际读 AUTH_OK_PATH + RUNNER_OK_PATH")
    ap.add_argument("--check-only", action="store_true", help="只读预检：不建锁、不写文件；通过退出 10")
    A = ap.parse_args()
    if A.date is not None:
        if A.date not in DATE_LIST:
            print("bad --date（须为 DATE_LIST 之一）"); sys.exit(2)
        dates = [A.date]
    else:
        dates = list(DATE_LIST)
    D = dates[0]  # for early checks that reference D
    STAMP = now().strftime("%Y%m%dT%H%M%S")
    R.update(started_et=ts(), pid=os.getpid(), date_list=dates, profile=A.profile,
             runner="run_backfill_1019_1023_dbincr_v3_1.py",
             forbid_nightly_driver=FORBIDDEN_DRIVER_BASENAME,
             sha_driver_ref=SHA_DRIVER_REF, live=False, promotion=False)
    R["checks"]["env_knobs_inherited"] = dict(SOURCE=os.environ.get("SOURCE"), SLEEP=os.environ.get("SLEEP"),
                                             TSPRO_RELAY_TIMEOUT=os.environ.get("TSPRO_RELAY_TIMEOUT"),
                                             DATAHUB_HTTP_PROXY_set=bool(os.environ.get("DATAHUB_HTTP_PROXY")))

    # P: markers for first date / any existing DONE for list
    e = marker_precheck()
    if e:
        R["no_write"] = True; fail("PRE " + e); finish(2, False)
    kv, e = check_ok()
    budget = CFG.get("budget", CALL_B_BUDGET_DEFAULT)
    R["checks"]["gates"] = dict(profile=A.profile, daily_pull_max_min=DAILY_PULL_MAX_MIN, call_b_budget_min=budget,
                                call_b_latest_finish=CALL_B_LATEST, date_list=dates,
                                leaf25_blackout="10:00-10:45", blackout="16:40-18:40", hard_stop="15:55",
                                mem_available_min_kb=MEM_AVAILABLE_MIN_KB,
                                child_env=dict(CHILD_ENV, SOURCE=("relay" if CFG.get("source_relay") else "未设置")), call_a_env=CALL_A_ENV,
                                forbid=FORBIDDEN_DRIVER_BASENAME)
    blocked_by_failed = bool(R.get("supersede"))
    sw = start_window_check()
    R["checks"]["start_window"] = sw or "ok"
    pre = ([e] if e else []) + ([] if e else [check_pins(), guarded_check(),
                                             "16:40–18:40 禁跑" if in_blackout() else None,
                                             "叶25 窗" if in_leaf25() else None,
                                             None if A.check_only else sw, pgrep_gates("pre")])
    for e2 in pre:
        if e2:
            R["no_write"] = blocked_by_failed or A.check_only; fail("PRE " + e2); finish(2, False)
    if A.check_only:
        e = ensure_lock(kv, dry=True)
        if not e and os.path.isfile(QUIET_LOCK):
            e = quiet_gate("check_only", full=True)
        if e:
            fail("PRE " + e); finish(2, False)
        ev("CHECK_ONLY 通过（未写任何文件；未调用 nightly 驱动；正式运行须 runner .ok）"); finish(CHECK_ONLY_EXIT, True)
    e = supersede_failed()
    if e:
        R["no_write"] = True; fail("PRE " + e); finish(2, False)
    e = ensure_lock(kv) or quiet_gate("pre", full=True)
    if e:
        fail("PRE " + e); finish(2, False)
    q = R["quiet"]
    base = hashlib.sha256(q["lock_text"].encode("ascii")).hexdigest() if q.get("created_by_data") else q.get("lock_sha256")
    R["checks"]["lock_sha_call_a"] = dict(baseline=base, created_by_data=bool(q.get("created_by_data")), now=sha256(QUIET_LOCK), at=ts())
    if base is None or sha256(QUIET_LOCK) != base:
        fail("PRE 锁 sha 与基线不符"); finish(2, False)

    all_ok = True
    for d in dates:
        # clear per-date fail accumulation helper: track fails before
        n_fail_before = len(R["fail_reasons"])
        ok_d = run_one_date(kv, d)
        if not ok_d:
            all_ok = False
            break  # 串行：一日失败即停，不 Continu e
        # between dates: quiet recheck + window
        if d != dates[-1]:
            qe = quiet_gate("between_%s" % d, full=False)
            swb = start_window_check()
            if qe or swb:
                fail("日间闸门失败：%s" % (qe or swb)); all_ok = False; break
    ok = all_ok and set(R.get("dates_done") or []) == set(dates) and not R["fail_reasons"]
    finish(0 if ok else 1, ok)


def post_checks(rb):
    """第 3 节：只认本次 call B 写入；日期统一 YYYYMMDD 并要求等于 D。"""
    t_b = rb["start_epoch"]
    fs, got = check_summary(CALL_B_STEPS, rb, "callB")
    for x in fs:
        fail(x)
    R["checks"]["summary_steps"] = got
    he = check_hsgt_log(rb)
    if he:
        fail(he)
    s = read_json(ROOT + "/output/daily_update_status.json")
    R["checks"]["daily_update_status"] = dict(s, sha256=s.get("_sha256"))
    if "_error" in s:
        fail("daily_update_status 读不到 %s" % s["_error"])
    fa = parse_ts(s.get("finished_at"))
    if fa is None or fa < t_b:
        fail("daily_update_status.finished_at=%r 不晚于 call B 起跑（旧记录）" % s.get("finished_at"))
    if s.get("status") != "ok":
        fail("daily_update_status.status=%r" % s.get("status"))
    if norm_date(s.get("target_trade_date")) != D:
        fail("target_trade_date=%r ≠ %s" % (s.get("target_trade_date"), D))
    before = (R["checks"].get("status_before") or {}).get("rows") or {}
    for t in REQUIRED_TABLES:
        v = (s.get("tables") or {}).get(t) or {}
        if norm_date(v.get("last_date")) != D:
            fail("REQUIRED %s last_date=%r ≠ %s" % (t, v.get("last_date"), D))
        if isinstance(v.get("rows"), int) and isinstance(before.get(t), int) and v["rows"] < before[t]:
            fail("REQUIRED %s rows %d < 跑前 %d" % (t, v["rows"], before[t]))
    f = read_json(ROOT + "/output/data_freshness_status.json")
    R["checks"]["freshness"] = dict(overall=f.get("overall"), expected_trade_date=f.get("expected_trade_date"), generated_at=f.get("generated_at"),
                                    generated_at_et=f.get("generated_at_et"), stale_tables=f.get("stale_tables"), sha256=f.get("_sha256"), error=f.get("_error"))
    ga = parse_ts(f.get("generated_at")) or parse_ts(f.get("generated_at_et"))
    if ga is None or ga < t_b:
        fail("freshness generated_at 不晚于 call B 起跑（旧记录）")
    if f.get("overall") != "ok":
        fail("freshness overall=%r" % f.get("overall"))


class DriverSignal(BaseException):
    """例程 / 人对驱动发 TERM / INT / HUP 时抛出；继承 BaseException，不会被内部 except Exception 吞掉。"""


HANDLED_SIGNALS = (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)


def _on_signal(sig, frm):
    raise DriverSignal("驱动收到信号 %s" % signal.Signals(sig).name)


def ignore_signals():
    for s_ in HANDLED_SIGNALS:
        try:
            signal.signal(s_, signal.SIG_IGN)
        except Exception:
            pass


def main():
    for s_ in HANDLED_SIGNALS:  # 被例程 TERM 时也要停树、恢复日历并写唯一 FAILED；SIGKILL 无法捕获（例程 20 分钟兜底）
        signal.signal(s_, _on_signal)
    try:
        main_inner()
    except SystemExit:
        raise
    except BaseException as e:  # 统一收尾：停活动进程树 → 已备份则走恢复链并双核 → 回执 → 唯一 FAILED → 退出 11
        ignore_signals()
        code_r = "SIGNAL" if isinstance(e, DriverSignal) else ("TOOL_TIMEOUT" if isinstance(e, ToolTimeout) else "EXCEPTION")
        add_code(code_r)
        R["uncaught"] = dict(type=type(e).__name__, reason_code=code_r, msg=str(e)[:400], tb=traceback.format_exc()[-3000:])
        ev("UNCAUGHT %s: %s" % (type(e).__name__, e))
        seen = []
        if CFG.get("npid") and alive(CFG["npid"]):
            seen = [CFG["npid"]] + descendants(CFG["npid"])
            try:
                stop_tree(CFG["npid"], CFG.get("marks") or CALL_A_MARKS, code_r, "统一收尾")
                if CFG.get("popen") is not None:
                    CFG["popen"].wait(timeout=WAIT_TIMEOUT_S)
            except BaseException as e2:
                R["uncaught_stop_error"] = repr(e2)[:300]
        code = ABNORMAL_EXIT if (CFG.get("call_started") or BACKUP) else 2
        try:
            if BACKUP and RUN_DIR:
                ok_c, _ = compare_restore("abnormal", dict(pids_seen=seen, cmd="abnormal"))
                if not ok_c:
                    code = 4
        except BaseException as e3:
            R["uncaught_restore_error"] = repr(e3)[:300]; code = 4
        if A is None or D is None:
            print("UNCAUGHT before args parsed"); sys.exit(2)
        if (R.get("supersede") or {}).get("state") == "pending":
            R["no_write"] = True  # 旧 FAILED 仍在原位，不能再写第二份
        fail("统一收尾 %s（%s）" % (code_r, type(e).__name__))
        finish(code, False)


if __name__ == "__main__":
    main()
