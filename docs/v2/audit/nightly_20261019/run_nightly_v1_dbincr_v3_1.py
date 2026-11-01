#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""10-19 日更驱动 run_nightly_v1.py（QuantLab Data；v3.1，按 Arch 行级审 ec1ac8e1 修 P1-1..3 / P2-1 / P2-2 / P2-4 / P3-1 / P3-2 / P3-4，并加 .ok 键 allow_relay_partial_<D> / allow_hsgt_source_empty_warn_<D>；未对真实数据运行）。只用标准库 + pyarrow（只读 parquet 元数据与少数单列）。

文件名固定 run_nightly_v1.py（Eng pgrep 精确匹配 nightly_update\\.py|tier1_pull\\.py|run_nightly_v1\\.py）。
版本史：a7292a61（作废，Arch 2dada5ed 设计审「不可签」）已 cp -p 归档于 _recovery/data/nightly_20261019/predraft2_20261018T114300/。
本版依据：Arch 设计审 2dada5ed（第 5 节 17 项准入清单）、Arch 12:24 / 12:36 裁定、主 Agent 12:32 决定、Eng 12:34、plan R runner v3_1（c983aed3）停止逻辑。

流程（全部串行，一次一个真实数据进程）：
  P  只读：已有 marker 预检（DONE 在 → 退出 2 不写；FAILED 在 → 仅 .ok supersede_failed_marker_sha256==其全长 sha 才继续）。
  0  .ok（key=value / ASCII / LF / 无行内注释 / 无重复键 / 无未知键 / 无 DRAFT / 不在 _consumed/）；全部钉 sha（驱动 + 4 个审计工具 + nightly_update + tier1_pull 5b70dfed + tushare_proxy + relay_health + 11 个步骤脚本 + routine_fallback）；
     解释器 /usr/bin/python3；ET 日期 == D 且不早于 05:25；不在 16:40–18:40；94322 / 94403 及其整棵进程树每个进程只能是 T / Z / 不存在（驱动绝不对它们发信号）；两条锚定 pgrep 为空；relay_outage_backfill 进程只能是 T。
  Q  RESEARCH_QUIET.lock：存在则核 purpose / set_at 日期；05:28 后仍不存在且 .ok 允许才按 Arch 模板代设；healthz quiet + 15 秒 + 复核 + pgrep。驱动绝不删除、移动锁。
  1  备份 tushare_raw/trade_cal.parquet（两份 sha == PIN 141078fa，chmod 444）；PIN 日历必须含 D 且 is_open=1；PIT 日历 fa4260b8 / manifest 7ccc911e / closure 6919e7af 前 sha；快照 v2 BEFORE。
  A  daily_pull：nightly_update.py --date D --steps daily_pull，子进程环境固定 TIER1_SKIP_CAL_REFRESH=1、TSPRO_RELAY_TIMEOUT=115；SOURCE 默认不设，只有 .ok source_relay_only=true 才设 SOURCE=relay；
     两档都是单次 30 分钟硬停（reason_code=MAX_RUN），另有 RSS（树合计 ≥1484800 kB 或单进程 >1536000 kB）、16:40 禁跑（BLACKOUT）；
     停止顺序：SIGSTOP nightly → 重新枚举 → 冻结全部后代 → 最深先 TERM+CONT → 10 秒 → KILL → SIGKILL nightly → wait(60 秒) → 孤儿扫描；每个信号前核 cmdline + PPID。
     每次尝试后：确认整棵树已不在 → compare → cal_restore_v2（rc=2 复跑一次；仍失败则驱动自带 os.replace 原子恢复）→ 间隔 30 秒双核 sha == PIN，否则 P0 退出 4。
     成功 = rc 0 + 本次窗口内 summary daily_pull ok + 四个原始文件存在、行数门槛、trade_date 实测 min=max=D、无 .tmp。
     只有 relaxed 且 reason_code=MAX_RUN 才可重试（Arch Q-A3 六个条件）；其余一律不重试、不起 call B。
  B  call B：14 步；闸门 = 实际起跑 + call_b_budget_min（.ok，主 Agent 12:32 定 75）≤ 16:00；在 min(起跑 + 预算, 16:00) 硬停（CALLB_TIMEOUT）→ FAILED；call B 后同样走日历恢复链。
  W  v3.1：.ok allow_relay_partial_<D>=true 时 cyq / tier3 / hsgt 的 partial 记 WARN；allow_hsgt_source_empty_warn_<D>=true 时 hsgt 源端空日（本次写出的 0 行文件）记 WARN；
     DONE 仍为 OK 并带 warnings[]，降级日期追加到 GAP_LIST；6 张 REQUIRED 表不全照旧 FAILED。PPID=1 可疑孤儿挡住 DONE（ORPHAN）。
  C  核查（第 3 节，只认本次写入）：summary 14 步 ok 无 skipped 且 finished/mtime 在 call B 窗口内；hsgt 日志本次 remaining=0（rc=2 算 partial）；
     daily_update_status finished_at 晚于 call B 起跑、status=ok、target_trade_date==D、REQUIRED_TABLES last_date==D（统一 YYYYMMDD）且 rows ≥ 跑前；
     freshness generated_at 晚于 call B 起跑、overall=ok；trade_cal == PIN；PIT 日历 / closure 未变；快照 compare 退出 0。
  M  先写回执，再写唯一 marker（DONE 或 FAILED，O_EXCL + 原子），然后退出。
异常 / 信号（TERM、INT、HUP）/ 工具超时：统一收尾 —— 停活动进程树 → 已备份则走恢复链并双核 → 回执 → 唯一 FAILED marker → 退出 11。SIGKILL 无法捕获，由例程 20 分钟兜底（routine_fallback_v1.py）。
退出码：0 OK；1 FAILED；2 前置条件失败（写唯一 FAILED；已有 marker 被拒时什么都不写）；3 marker 写入失败（P0）；4 P0 日历未恢复（仍写 FAILED）；10 --check-only 通过（不写文件）；11 异常 / 信号 / 超时收尾后的 FAILED。
"""
import argparse, datetime, hashlib, json, os, re, secrets, signal, subprocess, sys, time, traceback
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
ROOT = "/workspace/QuantLab"
PY = "/usr/bin/python3"
HERE = ROOT + "/docs/v2/audit/nightly_20261019"
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
SCOPE = HERE + "/nightly_sha_scope_dbincr_v3_1.txt"
SCOPE_SHA = "428a05d4891ab1c37fb272870b4a1c721d98406748d638a100784a898caca0c5"
# daily_basic incr v3.1 — Arch：incr/transform 进 SHA_KEYS（原模块常量=死钉，已迁入）
# pin_daily_basic_transform：.ok/SHA_KEYS 值为 transform 指纹；check_pins 用 compute_transform_sha 对照（非文件 sha）
PIN_DAILY_BASIC_INCREMENTAL_SHA = "a7ac54b3ecdf33d338710df5c96f447fbec51affdcfbf167fb3e00648f678dd8"
PIN_DAILY_BASIC_TRANSFORM_SHA = "308b5054c39801116fd0eb19b4e4bd10bdccd4b4d40bfb67dd06a58fa67ab974"
PIN_DAILY_BASIC_INCREMENTAL_REL = "scripts/acquire/daily_basic_incremental.py"
COMPARE = HERE + "/cal_compare_v1.py"
RESTORE = HERE + "/cal_restore_v2.py"
FALLBACK = HERE + "/routine_fallback_v1.py"
TIER1_SHA = "5b70dfed08a237034b586ef9738e2c1b81607b20387a62df49a1e6994ba711cf"  # Arch 12:36：code .ok ed56e336 签 b630bca2→5b70dfed（原子写日历 + TIER1_SKIP_CAL_REFRESH）
# .ok 键 → 相对路径 → 钉值（Arch 2dada5ed 第 6 节全表；sha_routine_fallback 在定稿时填入）
SHA_KEYS = {
    "sha_cal_restore": ("docs/v2/audit/nightly_20261019/cal_restore_v2.py", "6686876bdcfc95f11d493b5201f55eb726e69e4894d8c96bfaf46ab1748387a4"),
    "sha_cal_compare": ("docs/v2/audit/nightly_20261019/cal_compare_v1.py", "74093ff3be4c431bab8c469307b207b43b8e1cff707dd0bac1319a7e265cddfc"),
    "sha_snapshot_tool": ("docs/v2/audit/nightly_sha_scope_snapshot_v2_20261018.py", "c930ed5c627bf937e6b5d139c52f18945f045286e78dba66cbe5adfab92ab79a"),
    "sha_scope": ("docs/v2/audit/nightly_20261019/nightly_sha_scope_dbincr_v3_1.txt", SCOPE_SHA),
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
QUIET_LOCK = ROOT + "/output/loop/RESEARCH_QUIET.lock"
HEALTHZ = "http://127.0.0.1:8795/healthz"
PGREP_WEB = r"(^|[ /])([k]line|[e]xport_static|[s]napshot|[g]en)\.py( |$)"          # Arch D-P2-1
PGREP_DATA = r"(^|[ /])([r]emaining_after_stk_surv|[n]ightly_update|[t]ier1_pull|[r]un_backfill_[a-z0-9_]+)\.py( |$)"
PGREP_WATCHER = r"(^|[ /])[r]elay_outage_backfill\.py( |$)"
PGREP_RECORD = "[s]cripts/acquire/|[n]ightly_update"
GUARDED = {94322: "remaining_after_stk_surv.py", 94403: "relay_outage_backfill.py"}  # 只能是 T 或已退出；驱动绝不发信号
MARK_DIR = ROOT + "/output/nightly_markers"
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


def check_ok():
    p = os.path.abspath(ok_path())
    if "/_consumed/" in p + "/":
        return None, ".ok 路径含 /_consumed/：%s" % p
    if not os.path.isfile(p):
        return None, "run .ok 不存在 %s" % p
    kv, errs = parse_ok(p)
    R["checks"]["ok"] = dict(path=p, sha256=sha256(p), keys=sorted(kv), parse_errors=errs)
    if errs:
        return kv, ".ok 格式错误：%s" % "；".join(errs)
    miss = [k for k in OK_KEYS_REQUIRED if k not in kv]
    if miss:
        return kv, ".ok 缺必填键 %s" % miss
    want = dict(ok_id="ARCH_RUN_AUTH_DATA_NIGHTLY_%s" % D, ok_type="run", date=D, signed_by="QuantLab Arch", single_use="true", live="false",
                promotion_approved="false", interpreter=PY, pin_trade_cal=PIN, pin_frozen_closure=list(FROZEN.values())[0],
                daily_pull_max_min=str(DAILY_PULL_MAX_MIN), call_b_latest_finish=CALL_B_LATEST, rss_stop_kb=str(RSS_STOP_KB),
                rss_hard_kb=str(RSS_HARD_KB), blackout_et="16:40-18:40", allow_kill_scope="driver_descendants_exact_pid",
                allow_trade_cal_step="false", allow_sw="false", allow_force="false", allow_delete="false", allow_commit="false")
    for k, v in want.items():
        if kv.get(k) != v:
            return kv, ".ok %s=%r，须为 %r" % (k, kv.get(k), v)
    try:
        bud = int(kv["call_b_budget_min"])
    except ValueError:
        return kv, "call_b_budget_min 不是整数"
    if not 1 <= bud <= 120:
        return kv, "call_b_budget_min=%d 超出 1..120" % bud
    CFG["budget"] = bud
    t_iss, t_exp = parse_ts(kv["issued_at"]), parse_ts(kv["expires_et"])
    if t_iss is None or t_iss > time.time():
        return kv, "issued_at 缺时区或晚于当前时刻"
    if t_exp is None or t_exp <= time.time():
        return kv, "expires_et 缺时区或已过期"
    CFG["expires"] = datetime.datetime.fromisoformat(kv["expires_et"])
    for k, (rel, pin) in SHA_KEYS.items():
        if kv[k].lower() != pin:
            return kv, ".ok %s 与钉值 %s 不符" % (k, pin[:12])
    me = sha256(os.path.abspath(__file__))
    R["checks"]["driver_sha256"] = me
    if kv["sha_driver"].lower() != me:
        return kv, ".ok sha_driver 与本驱动 %s 不符" % me
    for k in ("allow_run_daily_pull_%s" % D, "allow_run_call_b_%s" % D, "allow_restore_trade_cal_%s" % D, "allow_write_nightly_marker_%s" % D):
        if not truthy(kv.get(k)):
            return kv, ".ok 未授权 %s" % k
    if "source_relay_only" in kv and kv["source_relay_only"] not in ("true", "false"):
        return kv, "source_relay_only 只能是 true / false"
    CFG["source_relay"] = kv.get("source_relay_only") == "true"  # Arch 12:38：默认关，签发时决定
    for k_ in ("allow_relay_partial_%s" % D, "allow_hsgt_source_empty_warn_%s" % D):
        if k_ in kv and kv[k_] not in ("true", "false"):
            return kv, "%s 只能是 true / false" % k_
    CFG["relay_partial"] = kv.get("allow_relay_partial_%s" % D) == "true"
    CFG["hsgt_empty_warn"] = kv.get("allow_hsgt_source_empty_warn_%s" % D) == "true"
    if A.profile == "relaxed" and not truthy(kv.get("allow_profile_relaxed_%s" % D)):
        return kv, "relaxed 档需要 .ok allow_profile_relaxed_%s=true" % D
    R["checks"]["ok"].update(expires_et=kv["expires_et"], issued_at=kv["issued_at"], call_b_budget_min=bud, source_relay_only=CFG["source_relay"],
                            allow_relay_partial=CFG["relay_partial"], allow_hsgt_source_empty_warn=CFG["hsgt_empty_warn"])
    return kv, None


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


def start_window_check():
    """Arch P3-3：ET 日期必须是 D，时刻不早于 05:25。"""
    t = now()
    if t.strftime("%Y%m%d") != D:
        return "ET 日期 %s 不是 %s" % (t.strftime("%Y%m%d"), D)
    if t < hm(START_NOT_BEFORE):
        return "早于 %s ET" % START_NOT_BEFORE
    return None


# ---------------- RESEARCH_QUIET（驱动绝不删除、移动锁） ----------------
LOCK_CREATE_NOT_BEFORE = "05:28"


def lock_text():
    return ("owner=Arch_by_Data\npurpose=nightly_%s\nset_at=%s\nrelease_when=output/nightly_markers/nightly_%s.DONE.json or .FAILED.json exists\nset_by_pid=%d\n"
            % (D, now().isoformat(timespec="seconds"), D, os.getpid()))


def lock_content_check():
    """Arch D-P3-1：purpose=nightly_<D>，set_at 的日期 == D。"""
    try:
        kv = {}
        for ln in open(QUIET_LOCK, encoding="ascii").read().split("\n"):
            if "=" in ln:
                k, v = ln.split("=", 1); kv[k.strip()] = v.strip()
    except Exception as e:
        return "锁读不了或非 ASCII %r" % e
    R["quiet"]["lock_kv"] = kv
    if kv.get("purpose") != "nightly_%s" % D:
        return "锁 purpose=%r 不是 nightly_%s" % (kv.get("purpose"), D)
    if norm_date(kv.get("set_at")) != D:
        return "锁 set_at=%r 日期不是 %s" % (kv.get("set_at"), D)
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
    return (os.path.join(MARK_DIR, "nightly_%s.DONE.json" % D), os.path.join(MARK_DIR, "nightly_%s.FAILED.json" % D))


def ok_path():
    return A.ok or (ROOT + "/output/ai_factory/ARCH_RUN_AUTH_DATA_NIGHTLY_%s.ok" % D)


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
    dst = os.path.join(sd, "nightly_%s.FAILED.%s.%s.json" % (D, s["sha256"][:12], STAMP))
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


def main_inner():
    global A, D, RUN_DIR, BACKUP, STAMP
    ap = argparse.ArgumentParser(description="10-19 日更驱动（新版）")
    ap.add_argument("--date", default="20261019")
    ap.add_argument("--profile", choices=["strict", "relaxed"], default="strict", help="两档同一时间盒；strict 不重试")
    ap.add_argument("--ok", default=None)
    ap.add_argument("--check-only", action="store_true", help="只读预检：不建锁、不写文件、不消耗 .ok；通过退出 10")
    A = ap.parse_args()
    D = A.date
    if not re.fullmatch(r"\d{8}", D):
        print("bad --date"); sys.exit(2)
    STAMP = now().strftime("%Y%m%dT%H%M%S")
    R.update(started_et=ts(), pid=os.getpid(), date=D, profile=A.profile)
    R["checks"]["env_knobs_inherited"] = dict(SOURCE=os.environ.get("SOURCE"), SLEEP=os.environ.get("SLEEP"), TSPRO_RELAY_TIMEOUT=os.environ.get("TSPRO_RELAY_TIMEOUT"),
                                             DATAHUB_HTTP_PROXY_set=bool(os.environ.get("DATAHUB_HTTP_PROXY")))

    # P / 0 只读前置
    e = marker_precheck()
    if e:
        R["no_write"] = True; fail("PRE " + e); finish(2, False)
    kv, e = check_ok()
    budget = CFG.get("budget", CALL_B_BUDGET_DEFAULT)
    R["checks"]["gates"] = dict(profile=A.profile, daily_pull_max_min=DAILY_PULL_MAX_MIN, call_b_budget_min=budget, call_b_latest_finish=CALL_B_LATEST,
                                call_b_gate="call B 实际起跑 + 预算 ≤ 16:00；在 min(起跑 + 预算, 16:00) 硬停", retries=("relaxed: 仅 MAX_RUN" if A.profile == "relaxed" else "无"),
                                child_env=dict(CHILD_ENV, SOURCE=("relay" if CFG.get("source_relay") else "未设置")), call_a_env=CALL_A_ENV)
    blocked_by_failed = bool(R.get("supersede"))
    sw = start_window_check()
    R["checks"]["start_window"] = sw or "ok"
    pre = ([e] if e else []) + ([] if e else [check_pins(), guarded_check(), "16:40–18:40 禁跑" if in_blackout() else None,
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
        ev("CHECK_ONLY 通过（未写任何文件；正式运行会全部重做）"); finish(CHECK_ONLY_EXIT, True)
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
    os.makedirs(ROOT + "/_recovery/data/nightly_%s" % D, exist_ok=True)
    RUN_DIR = ROOT + "/_recovery/data/nightly_%s/run_%s" % (D, STAMP)
    os.mkdir(RUN_DIR)

    # 1 备份与 BEFORE
    bk = os.path.join(RUN_DIR, "trade_cal.parquet.141078fa")
    with open(TRADE_CAL, "rb") as s, open(bk, "xb") as d_:
        d_.write(s.read()); d_.flush(); os.fsync(d_.fileno())
    st_ = os.stat(TRADE_CAL); os.utime(bk, ns=(st_.st_atime_ns, st_.st_mtime_ns))
    b1, b2 = sha256(TRADE_CAL), sha256(bk)
    R["checks"]["backup"] = dict(path=bk, live_sha=b1, backup_sha=b2, live_inode=st_.st_ino)
    if b1 != PIN or b2 != PIN:
        alert("P0", "跑前 trade_cal 或备份 sha 不是 PIN"); fail("PRE trade_cal 不是 PIN"); finish(2, False)
    os.chmod(bk, 0o444); BACKUP = bk
    R["checks"]["cal_sha_pre"] = cal_shas()
    if not R["checks"]["cal_sha_pre"]["pit_cal_ok"] or not R["checks"]["cal_sha_pre"]["frozen_ok"]:
        fail("PRE PIT 日历或冻结 closure sha 不符"); finish(2, False)
    ci, opn = cal_info(TRADE_CAL)
    R["checks"]["trade_cal_pin_info"] = dict(ci, d_is_open=D in opn)
    if D not in opn:  # Eng 12:34：TIER1_SKIP_CAL_REFRESH=1 时 tier1_pull dates()（L53-56）读的就是这份冻结日历
        fail("PRE PIN 日历里 %s 不是开市日" % D); finish(2, False)
    st0 = read_json(ROOT + "/output/daily_update_status.json")
    R["checks"]["status_before"] = dict(rows=status_rows(st0), sha256=st0.get("_sha256"), finished_at=st0.get("finished_at"))
    rc, _ = run_tool([SNAP, "snap", SCOPE, os.path.join(RUN_DIR, "snap_before.txt"), "--expect-scope-sha", SCOPE_SHA], "snap_before.log", "snap")
    if rc != 0:
        fail("PRE 快照 BEFORE rc=%d" % rc); finish(2, False)

    # A daily_pull（两档 30 分钟硬停；仅 relaxed + MAX_RUN 可重试）
    max_retry = 0
    if A.profile == "relaxed":
        try:
            max_retry = max(0, min(2, int(kv.get("allow_daily_pull_retry_%s" % D, "0"))))
        except ValueError:
            max_retry = 0
    allow_q = truthy(kv.get("allow_quarantine_mv_daily_raw_%s" % D))
    black0 = hm("%02d:%02d" % BLACKOUT[0]); latest = hm(CALL_B_LATEST)
    k, final, no_more, pending_bad = 0, None, False, []
    pgrep_record("pre")
    while True:
        k += 1
        xe = check_expiry("callA_a%d" % k)
        if xe:
            fail(xe); no_more = True; break
        box_end = min(now() + datetime.timedelta(minutes=DAILY_PULL_MAX_MIN), black0)
        rec = run_nightly("daily_pull", "callA_a%d" % k, box_end, "MAX_RUN", CALL_A_MARKS, CALL_A_ENV)
        rec["attempt"] = k
        check_cal_skip_log(rec)
        cal_ok, changed = compare_restore("a%d" % k, rec)
        rec.update(calendar_restored=cal_ok, calendar_changed_by_call=changed)
        if not cal_ok:
            R["prior_attempts"].append(rec); fail("P0 日历未恢复（a%d）" % k); add_code("P0"); finish(4, False)
        bad, tmps, raw = raw_check()
        sfs, _ = check_summary(["daily_pull"], rec, "callA_a%d" % k)
        rec.update(raw=raw, bad=bad, tmp_left=tmps, summary_fails=sfs)
        dirty = bool(rec["residual"] or rec["seen_alive_after"] or rec["wait_timeout"] or rec["orphans_logged_only"])
        if rec["rc"] == 0 and not rec["stopped"] and not bad and not tmps and not sfs and not dirty:
            final = rec; R["checks"]["raw_final"] = raw; break
        code = rec["reason_code"] or "ATTEMPT_FAILED"
        rec["quarantine"] = quarantine(tmps + [os.path.join(RAW, a, "%s.parquet" % D) for a, _ in bad], allow_q, k)
        R["prior_attempts"].append(rec)
        pending_bad = tmps + [os.path.join(RAW, a, "%s.parquet" % D) for a, _ in bad]
        R["checks"]["raw_final"] = raw
        if dirty:
            no_more = True; fail("daily_pull 第 %d 次停后有残留或 wait 超时（%s）；不重试、不起 call B" % (k, code)); break
        if A.profile != "relaxed" or code not in RETRYABLE:
            no_more = True; fail("daily_pull 第 %d 次失败 reason_code=%s（profile=%s；只有 relaxed 的 MAX_RUN 可重试）" % (k, code, A.profile)); break
        if k > max_retry:
            no_more = True; fail("daily_pull MAX_RUN 且重试已用完（max=%d）" % max_retry); break
        # Arch Q-A3 条件 (a)–(f)
        orph = R["checks"].get("orphans_callA_a%d" % k) or {}
        still = [p for p in pending_bad if os.path.exists(p)]
        nxt = now() + datetime.timedelta(minutes=RETRY_WAIT_MIN)
        cond = dict(a_tree_and_orphans_empty=not orph.get("acted") and not orph.get("logged_only"), b_calendar_pin=cal_ok,
                    c_quarantined=not still and all(x.get("done") for x in rec["quarantine"] if x.get("why") != "不存在"),
                    d_count_ok=k <= max_retry,
                    e_time_ok=nxt + datetime.timedelta(minutes=DAILY_PULL_MAX_MIN + budget) <= latest and nxt + datetime.timedelta(minutes=DAILY_PULL_MAX_MIN) <= black0)
        rec["retry_conditions"] = cond
        if not all(cond.values()):
            no_more = True; fail("重试条件不满足 %s" % [c for c, v in cond.items() if not v]); break
        alert("P1", "daily_pull 第 %d 次 MAX_RUN；%d 分钟后重试" % (k, RETRY_WAIT_MIN))
        time.sleep(RETRY_WAIT_MIN * 60)
        qe = quiet_gate("retry_a%d" % (k + 1), full=True)  # 条件 (f)
        if qe:
            no_more = True; fail("重试前 quiet 不通过：%s" % qe); break
    if final:
        R["invocations"].append(dict(name="daily_pull", cmd=final["cmd"], rc=final["rc"], pid=final["pid"], env_set=final["env_set"],
                                     started_et=final["started_et"], finished_et=final["finished_et"], attempt=final["attempt"]))

    # B
    rb = None
    b_cmd = "%s scripts/nightly_update.py --date %s --steps %s" % (PY, D, ",".join(CALL_B_STEPS))
    if final and not no_more:
        start_b = now()
        g_time = start_b + datetime.timedelta(minutes=budget) <= latest
        g_black = not in_blackout(start_b) and start_b + datetime.timedelta(minutes=budget) <= black0
        g_sha = sha256(TRADE_CAL) == PIN
        g_exp = check_expiry("callB")
        lk = sha256(QUIET_LOCK) if os.path.isfile(QUIET_LOCK) else None
        g_lock = lk is not None and lk == R["checks"]["lock_sha_call_a"]["baseline"]
        R["checks"]["call_b_gate"] = dict(at=start_b.isoformat(timespec="seconds"), budget_min=budget, latest_finish=CALL_B_LATEST,
                                         time_ok=g_time, blackout_ok=g_black, sha_ok=g_sha, expiry_ok=not g_exp, lock_sha_now=lk, lock_sha_unchanged=g_lock)
        qe = g_exp or (None if g_lock else "RESEARCH_QUIET.lock sha 与 call A 前不同或已不存在") or quiet_gate("pre_call_b", full=False)
        if g_time and g_black and g_sha and not qe:
            box_end = min(start_b + datetime.timedelta(minutes=budget), latest)
            rb = run_nightly(",".join(CALL_B_STEPS), "callB", box_end, "CALLB_TIMEOUT", CALL_B_MARKS)
            R["invocations"].append(dict(name="call_b", cmd=rb["cmd"], rc=rb["rc"], pid=rb["pid"], env_set=rb["env_set"], started_et=rb["started_et"],
                                         finished_et=rb["finished_et"], box_end=box_end.isoformat(timespec="seconds"), reason_code=rb["reason_code"]))
            if rb["stopped"]:
                fail("call B 被停 reason_code=%s（%s）" % (rb["reason_code"], rb["stopped"]["reason"]))
            elif rb["rc"] != 0:
                fail("call B rc=%s" % rb["rc"])
            if rb["residual"] or rb["seen_alive_after"] or rb["wait_timeout"]:
                fail("call B 停后有残留或 wait 超时")
            ok_b, changed_b = compare_restore("callB", rb)  # D-P2-5
            if changed_b:
                fail("call B 期间 trade_cal 被改动（恢复前 sha 不是 PIN）")
            if not ok_b:
                fail("P0 call B 后日历未恢复"); add_code("P0"); finish(4, False)
        else:
            why = "time" if not g_time else ("blackout" if not g_black else ("trade_cal sha" if not g_sha else qe))
            R["invocations"].append(dict(name="call_b", cmd=b_cmd, rc=None, not_run_reason=why))
            add_code("CALLB_GATE"); fail("call B 未起：%s" % why)
    else:
        R["invocations"].append(dict(name="call_b", cmd=b_cmd, rc=None, not_run_reason="daily_pull 未成功或被停"))
        fail("call B 未起：daily_pull 未成功或被停")

    # C 核查
    if rb is not None:
        post_checks(rb)
    rc, out = run_tool([SNAP, "snap", SCOPE, os.path.join(RUN_DIR, "snap_after.txt"), "--expect-scope-sha", SCOPE_SHA], "snap_after.log", "snap")
    crc, cout = run_tool([SNAP, "compare", SCOPE, os.path.join(RUN_DIR, "snap_before.txt"), os.path.join(RUN_DIR, "snap_after.txt"),
                          "--expect-scope-sha", SCOPE_SHA], "snap_compare.log", "snap") if rc == 0 else (rc, "")
    R["checks"]["snapshot_compare_rc"] = crc
    if crc != 0 or "META_ONLY_FAIL" in cout:
        fail("快照 compare rc=%s" % crc)
    if sha256(TRADE_CAL) != PIN:
        alert("P0", "收尾时 trade_cal 不是 PIN：先走恢复链再判 FAILED（Arch P2-1）"); fail("收尾时 trade_cal 不是 PIN"); add_code("FINAL_CAL_MISMATCH")
        ok_f, _ = compare_restore("final")
        if not ok_f:
            fail("P0 收尾恢复后日历仍不是 PIN"); add_code("P0"); finish(4, False)
        finish(1, False)
    ok = (not R["fail_reasons"]) and len(R["invocations"]) == 2 and all(i.get("rc") == 0 for i in R["invocations"]) \
        and all(("--date %s" % D) in i["cmd"] for i in R["invocations"])
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
