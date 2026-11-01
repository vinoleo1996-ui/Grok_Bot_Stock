"""Shared gate + resume definition for the SD1 data fixes (QuantLab Data). Pinned transitively: each build script
hard-codes this file's sha256 and verifies it BEFORE importing. Pure functions; no market data is read here except
by enforce_inputs() (sha of pinned files, called only after every cheap gate check passed).
Gate copied from research/strategy_tie_sensitivity_prereg_v1.py (parse_run_auth / enforce_run_auth / check_out_dir)."""
from __future__ import annotations
import hashlib, json, os, re, shutil, time
from pathlib import Path

ROOT = Path("/workspace/QuantLab")
VERSION = "cs_panel_resumefix_v1"
SERIAL = ["D1a_fixesnone_check", "D1b_resume_execute", "D2_suspend_flags", "D3D4_stock_delisted"]
YEARS = list(range(2018, 2027))
OUT_KEYS = {"D1a_fixesnone_check": "out_dir_d1a", "D1b_resume_execute": "out_dir_d1b",
            "D2_suspend_flags": "out_dir_d2", "D3D4_stock_delisted": "out_path_d3d4"}
OUT_REL = {"D1a_fixesnone_check": "output/ai_factory/panel_cache_v2_fixesnone",
           "D1b_resume_execute": "output/ai_factory/panel_cache_v2_resumefix",
           "D2_suspend_flags": "data/v2/suspend_flags",
           "D3D4_stock_delisted": "data/v2/ref/stock_delisted_v2.parquet"}
# cheap pins (code + plans) are checked first; data pins afterwards
PIN_CODE = {"plan_cs_panel_sha256": "docs/v2/DATA_CS_PANEL_RESUME_REBUILD_PLAN_ZH.md",
            "plan_sd_fix_sha256": "docs/v2/DATA_SUSPEND_DELIST_FIX_PLAN_ZH.md",
            "script_cs_panel_sha256": "scripts/fix_sd1/build_cs_panel_v2_resumefix.py",
            "script_suspend_flags_sha256": "scripts/fix_sd1/build_suspend_flags_v2.py",
            "script_stock_delisted_sha256": "scripts/fix_sd1/build_stock_delisted_v2.py",
            "common_sha256": "scripts/fix_sd1/sd1_common.py"}
PIN_DATA = {"mask_sha256": "output/strategy_hiliq/universe_mask_hiliq_v1.parquet",
            **{f"v1_cs_panel_{y}_sha256": f"output/ai_factory/panel_cache/cs_panel_{y}.parquet" for y in YEARS},
            "float_mktcap_sha256": "data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet",
            "sw_l1_sha256": "data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet",
            "stock_delisted_v1_sha256": "data/v2/ref/stock_delisted.parquet",
            "namechange_all_sha256": "data/v2/st_events/namechange_all.parquet",
            "delisted_daily_sha256": "data/v2/delisted/delisted_daily_tushare.parquet"}
PINNED = {**PIN_CODE, **PIN_DATA}
FIXED = {"format": "quantlab_run_auth_v1", "version": VERSION, "signed_by": "arch", "live": "false", "promotion": "false",
         "scope": "D1_cs_panel_v2_resumefix_2018_2026_and_D2_suspend_flags_v2_and_D3D4_stock_delisted_v2_new_versioned_outputs_only",
         "serial_order": ",".join(SERIAL), "years": "2018-2026",
         "ruling_leaf_eval_booking": "hiliq_carry_keep_weight_through_halt_book_resume_day_return",
         "ruling_is_resume_day": "disclosure_and_no_new_buy_gate_only",
         "ruling_hiliq_fulla": "v1_mask_definition_unchanged",
         "ruling_carry_cols": "booking_only_not_selection",
         "run_niceness": "10", "run_serial": "true",
         "run_after": "alpha_v41_regen_finished_and_no_other_research_process_in_ps",
         "run_forbid_concurrent": "nightly_daily_pull,tier1_pull,adj_factor,bars_materialize,nightly_update.py,tier3_daily_snapshot.py,relay_outage_backfill_unless_state_T",
         **{OUT_KEYS[s]: OUT_REL[s] for s in SERIAL}}
AUTH_REQUIRED = ("format", "version", "signed_by", "signed_et", "allow_full", "allow_smoke", "allow_dryrun", "live", "promotion",
                 "scope", "not_authorized", "serial_order", "years", "out_dir_d1a", "out_dir_d1b", "out_dir_d2", "out_path_d3d4",
                 "ruling_leaf_eval_booking", "ruling_is_resume_day", "ruling_hiliq_fulla", "ruling_carry_cols",
                 "run_niceness", "run_serial", "run_after", "run_forbid_concurrent", "expires_et") + tuple(PINNED)
NOT_AUTH_REQUIRED = {"old_cs_panel_overwrite", "tier1_materialize_change", "paper_mask_change", "v1_panel_overwrite", "mask_rebuild", "leaf_eval", "leaf_ic",
                     "engine_change", "fund_portfolio_merge", "broker_recommend_merge"}

def file_sha256(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def block(msg):  raise SystemExit(f"SD1 gate blocked: {msg}")

def check_expiry(kv, now=None):
    """r6: expires_et must be ISO8601 with offset and strictly later than now (aware datetime); else block."""
    from datetime import datetime, timezone
    e = kv.get("expires_et", "")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?([+-]\d{2}:\d{2})", e):
        block(f"expires_et={e!r} is not ISO8601 with offset")
    exp = datetime.fromisoformat(e); now = now or datetime.now(timezone.utc)
    if now >= exp: block(f"run-auth expired: expires_et={e}, now={now.isoformat(timespec='seconds')}")
    kv["_expires_et"] = e

def parse_run_auth(path) -> dict:
    """Only lines ^[a-z0-9_]+=value$ parsed; missing/empty/duplicate/invalid -> SystemExit."""
    if path is None: block("--arch-ok not given (Arch writes the .ok; Data never creates it)")
    path = Path(path)
    if not path.is_file(): block(f"run-auth file missing: {path}")
    kv = {}
    for ln in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^([a-z0-9_]+)=(.*)$", ln.strip())
        if not m: continue
        k, v = m.group(1), m.group(2).strip()
        if k in kv: block(f"run-auth field '{k}' appears more than once")
        kv[k] = v
    miss = [k for k in AUTH_REQUIRED if not kv.get(k)]
    if miss: block(f"run-auth lacks fields {miss}")
    for k, v in FIXED.items():
        if kv[k] != v: block(f"{k}={kv[k]!r}, expected {v!r}")
    na = set(kv["not_authorized"].split(","))
    if not NOT_AUTH_REQUIRED <= na: block(f"not_authorized lacks {sorted(NOT_AUTH_REQUIRED - na)}")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?([+-]\d{2}:\d{2})", kv["signed_et"]):
        block(f"signed_et={kv['signed_et']!r} is not ISO8601 with offset (e.g. 2026-10-18T02:10:00-04:00)")
    check_expiry(kv)   # r6: Arch r5 P3-2 (expires_et required; expired -> refuse)
    if "allow_selftest" in kv and kv["allow_selftest"] not in ("true", "false"): block("allow_selftest must be exactly true or false")
    kv["allow_selftest"] = kv.get("allow_selftest") == "true"
    for k in ("allow_full", "allow_smoke", "allow_dryrun"):
        if kv[k] not in ("true", "false"): block(f"{k}={kv[k]!r}, must be exactly true or false")
        kv[k] = kv[k] == "true"
    for k in PINNED:
        if not re.fullmatch(r"[0-9a-f]{64}", kv[k]): block(f"{k} is not a 64-hex lowercase sha256")
    kv["_ok_sha256"] = file_sha256(path); kv["_ok_path"] = str(path)
    return kv

D3D4_EXPECT_KEYS = ("expected_face_value_recategorised", "expected_unknown_needs_source_count")   # r6b (Arch 02:25)
def parse_d3d4_expectations(kv, execute: bool) -> dict:
    """r6b: optional .ok keys for D3D4. dry-run: may be absent (print only). execute: both required, else block.
    face set: comma-separated ts_codes, compared as a sorted set; count: non-negative integer."""
    out = {"face": None, "unknown_count": None}
    miss = [k for k in D3D4_EXPECT_KEYS if not kv.get(k, "").strip()]
    if execute and miss: block(f"execute requires .ok keys {miss} (Arch r6b)")
    f = kv.get("expected_face_value_recategorised", "").strip()
    if f:
        codes = [c.strip() for c in f.split(",") if c.strip()]
        if not codes or any(not re.fullmatch(r"\d{6}\.(SH|SZ|BJ)", c) for c in codes): block(f"expected_face_value_recategorised malformed: {f!r}")
        if len(set(codes)) != len(codes): block("expected_face_value_recategorised has duplicates")
        out["face"] = sorted(set(codes))
    u = kv.get("expected_unknown_needs_source_count", "").strip()
    if u:
        if not re.fullmatch(r"\d+", u): block(f"expected_unknown_needs_source_count must be a non-negative integer: {u!r}")
        out["unknown_count"] = int(u)
    return out

def check_mode(kv, execute: bool):
    if kv["allow_smoke"] is not False: block("allow_smoke must be false (no smoke mode exists)")
    if execute and kv["allow_full"] is not True: block("--execute requires allow_full=true")
    if not execute and kv["allow_dryrun"] is not True: block("dry-run requires allow_dryrun=true in the .ok")

def enforce_code(kv, root=ROOT) -> dict:
    got = {}
    for k, rel in PIN_CODE.items():
        p = Path(root) / rel
        if not p.exists(): block(f"pinned file missing: {rel}")
        got[k] = file_sha256(p)
        if got[k] != kv[k]: block(f"sha256 mismatch {rel}: measured {got[k]} != authorized {kv[k]}")
    return got

def out_path(step, root=ROOT) -> Path: return Path(root) / OUT_REL[step]
def receipt_path(step, root=ROOT) -> Path:
    o = out_path(step, root)
    return o.with_name(o.name + ".receipt.json") if step == "D3D4_stock_delisted" else o / f"RECEIPT_{step}.json"

def check_out(step, root=ROOT):
    o = out_path(step, root)
    if step == "D3D4_stock_delisted":
        for p in (o, receipt_path(step, root), o.with_name(o.name + ".manifest.json")):
            if p.exists(): block(f"target exists, refuse to overwrite: {p}")
    elif o.exists() and (not o.is_dir() or any(o.iterdir())):
        block(f"output dir exists and is not empty: {o}")
    for p in o.parent.glob(o.name + ".staging_*"):
        block(f"leftover staging exists (inspect/VOID first): {p}")

def check_order(step, kv, root=ROOT, execute=True):
    if step not in SERIAL: block(f"unknown step {step}")
    i = SERIAL.index(step)
    for later in SERIAL[i + 1:]:  # a later step already produced output -> out of order
        lp = out_path(later, root)
        if lp.exists() and (lp.is_file() or any(lp.iterdir())): block(f"out of order: later step {later} output exists ({lp})")
    if i == 0: return None
    if not execute: return None   # Arch r4 P2-3: dry-run skips predecessor RECEIPT (later-output check above still applies)
    prev = SERIAL[i - 1]; rp = receipt_path(prev, root)
    if not rp.is_file(): block(f"out of order: predecessor receipt missing {rp}")
    try: r = json.loads(rp.read_text(encoding="utf-8"))
    except Exception as e: block(f"predecessor receipt unreadable {rp}: {e}")
    if r.get("step") != prev or r.get("status") != "PASS": block(f"predecessor receipt not PASS for {prev}: {r.get('status')}")
    if r.get("ok_sha256") != kv["_ok_sha256"]: block("predecessor receipt was produced under a different .ok")
    for k in PIN_CODE:
        if r.get("pins", {}).get(k) != kv[k]: block(f"predecessor receipt pin {k} != .ok")
    return file_sha256(rp)

FORBID_PATTERNS = ("research/", "daily_pull", "tier1_pull", "tier1_materialize", "adj_factor", "bars_materialize",
                   "nightly_update.py", "tier3_daily_snapshot.py")   # r6 (Arch 02:21): present in any state -> refuse
STOPPED_OK_PATTERNS = ("relay_outage_backfill",)        # r6: allowed only if /proc/<pid>/stat state == "T"; else refuse
SELF_EXEMPT = "scripts/fix_sd1/"

def proc_state(pid) -> str:
    """state letter from /proc/<pid>/stat (field after the parenthesised comm)."""
    try: st = Path(f"/proc/{pid}/stat").read_text()
    except Exception: return "?"
    return st[st.rindex(")") + 2:].split()[0]

def classify_procs(procs):
    """Pure: procs = [(pid, cmd, state)]. Returns (bad, allowed_stopped, matches). fix_sd1's own processes are exempt
    only when the forbidden word is not elsewhere in the command (e.g. 'tier3' inside a fix_sd1 path is fine)."""
    bad, allowed, matches = [], [], []
    for pid, cmd, state in procs:
        probe = cmd.replace(SELF_EXEMPT, "") if SELF_EXEMPT in cmd else cmd
        hit = [p for p in FORBID_PATTERNS if p in probe]
        soft = [p for p in STOPPED_OK_PATTERNS if p in probe]
        if hit:
            bad.append(f"{pid} [{state}] {cmd[:160]}"); matches.append({"pid": pid, "state": state, "patterns": hit, "verdict": "forbid", "cmd": cmd[:200]})
        elif soft:
            if state == "T":
                allowed.append(f"{pid} [{state}] {cmd[:160]}"); matches.append({"pid": pid, "state": state, "patterns": soft, "verdict": "allowed_stopped", "cmd": cmd[:200]})
            else:
                bad.append(f"{pid} [{state}] {cmd[:160]}"); matches.append({"pid": pid, "state": state, "patterns": soft, "verdict": "forbid_not_stopped", "cmd": cmd[:200]})
    return bad, allowed, matches

def run_conditions(kv, execute=False) -> dict:
    """P2-4 + r6: niceness must equal run_niceness; no research/ process, no raw-writing nightly step, no nightly_update/tier3,
    relay_outage_backfill only if stopped (SIGSTOP). Match details recorded (and printed in execute mode)."""
    me = os.getpid(); par = os.getppid(); nice = os.nice(0); snap = []; procs = []
    for d in Path("/proc").iterdir():
        if not d.name.isdigit() or int(d.name) in (me, par): continue
        try: cmd = (d / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace").strip()
        except Exception: continue
        if not cmd: continue
        if "python" in cmd or "nightly" in cmd: snap.append(f"{d.name} {cmd[:160]}")
        procs.append((int(d.name), cmd, proc_state(d.name)))
    bad, allowed, matches = classify_procs(procs)
    rc = {"niceness": nice, "ps_snapshot": snap, "conflicting": bad, "allowed_stopped": allowed, "forbid_matches": matches,
          "forbid_patterns": list(FORBID_PATTERNS), "stopped_ok_patterns": list(STOPPED_OK_PATTERNS)}
    # r6 (Arch 02:21): every allow/refuse decision (pid, state, cmdline) goes to stdout in all modes and into manifest via rc
    print("RUN_CONDITION_MATCHES " + json.dumps(matches, ensure_ascii=False), flush=True)
    if nice != int(kv["run_niceness"]): block(f"FAIL run condition: niceness {nice} != {kv['run_niceness']} (run with nice -n 10)")
    if bad: block(f"FAIL run condition: conflicting processes {bad[:3]}")
    return rc

def raw_content_sha256(cutoff: str, root=ROOT) -> dict:
    """P2-1: sha over sorted '<rel>:<sha>' of every raw daily + suspend_d file with date <= cutoff."""
    lines = []
    for sub in ("daily", "suspend_d"):
        for p in sorted((Path(root) / "data/v2/tushare_raw" / sub).glob("2*.parquet")):
            if p.stem <= cutoff: lines.append(f"{sub}/{p.name}:{file_sha256(p)}")
    return {"cutoff": cutoff, "n_files": len(lines), "raw_content_sha256": hashlib.sha256("\n".join(lines).encode()).hexdigest()}

def mask_last_date(root=ROOT) -> str:
    import pyarrow.parquet as pq, pyarrow.compute as pc
    t = pq.read_table(Path(root) / PIN_DATA["mask_sha256"], columns=["date"])
    return pc.max(t.column("date")).as_py().strftime("%Y%m%d")

def raw_pin_start(step, cutoff, root=ROOT, execute=True) -> dict:
    """content hash of raw inputs up to cutoff; must equal the predecessor receipt's (D1a->D1b->D2 share one)."""
    r = raw_content_sha256(cutoff, root)
    i = SERIAL.index(step)
    if i > 0 and execute:   # dry-run: no predecessor comparison (Arch r4 P2-3)
        prev = json.loads(receipt_path(SERIAL[i - 1], root).read_text(encoding="utf-8")).get("raw_content")
        if prev is not None and prev != r: raise RuntimeError(f"raw content changed since {SERIAL[i-1]}: {prev} != {r}")
    return r

def enforce_inputs(kv, keys, root=ROOT) -> dict:
    got = {}
    for k in keys:
        rel = PIN_DATA[k]; p = Path(root) / rel
        if not p.exists(): block(f"pinned input missing: {rel}")
        got[k] = file_sha256(p)
        if got[k] != kv[k]: block(f"sha256 mismatch {rel}: measured {got[k]} != authorized {kv[k]}")
    return got

def gate(argv, step, data_keys, execute):
    """Full gate. Order: .ok parse -> mode -> code/plan sha -> out dir -> serial order/receipt -> data sha. Reads no market
    data until every earlier check passed; data sha is the first touch of data files."""
    ok = None
    if "--arch-ok" in argv:
        j = argv.index("--arch-ok"); ok = argv[j + 1] if j + 1 < len(argv) else None
    kv = parse_run_auth(ok)
    check_mode(kv, execute)
    code = enforce_code(kv)
    check_out(step)
    prev_receipt_sha = check_order(step, kv, execute=execute)
    rc = run_conditions(kv, execute=execute)
    data = enforce_inputs(kv, data_keys)
    kv["_run_conditions"] = rc; kv["_execute"] = execute
    print(f"GATE_PASS step={step} mode={'execute' if execute else 'dryrun'} ok_sha256={kv['_ok_sha256']}", flush=True)
    return kv, {**code, **data}, prev_receipt_sha

def memavail_gb():
    for l in open("/proc/meminfo"):
        if l.startswith("MemAvailable"): return int(l.split()[1]) / 1048576
    return 99.0

def rss_mb():
    import resource; return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024

class Staging:
    """Write into <out>.staging_<ts>/; commit() renames atomically; void() removes partials and writes <out>.VOID_<ts>.md."""
    def __init__(self, step, execute, root=ROOT):
        self.step, self.execute = step, execute
        self.final = out_path(step, root); self.ts = time.strftime("%Y%m%dT%H%M%S")
        self.dir = self.final.parent / f"{self.final.name}.staging_{self.ts}"
        if execute: self.dir.mkdir(parents=True, exist_ok=False)
    def path(self, name): return self.dir / name
    def void(self, msg):
        """execute: remove staging + write <out>.VOID_<ts>.md. dry-run: abort only (nothing was written, no VOID file)."""
        if self.execute:
            shutil.rmtree(self.dir, ignore_errors=True)
            (self.final.parent / f"{self.final.name}.VOID_{self.ts}.md").write_text(
                f"# VOID — {self.step}\n\n{msg}\n\nNo partial output kept; nothing may be reported from this run.\n", encoding="utf-8")
        raise SystemExit(f"SD1 VOID {self.step}: {msg}")
    def guard(self, tag=""):
        if memavail_gb() < 2: self.void(f"abort: MemAvailable<2GB at {tag}")
        if rss_mb() > 1500: self.void(f"abort: RSS {rss_mb():.0f}MB>1500MB at {tag}")
    def commit(self, files_to_final=None):
        """dir steps: rename staging dir -> final dir. file step: move listed files to final names."""
        if not self.execute: return
        if files_to_final is None:
            if self.final.exists():
                if any(self.final.iterdir()): self.void("final dir became non-empty during run")
                self.final.rmdir()
            os.rename(self.dir, self.final)
        else:
            for src, dst in files_to_final:
                if Path(dst).exists(): self.void(f"target appeared during run: {dst}")
            for src, dst in files_to_final: os.rename(self.dir / src, dst)
            self.dir.rmdir()

class ResumeState:
    """Single resume definition shared by cs_panel_v2_resumefix and suspend_flags_v2 (Arch P1-5/P2-3/P2-4/P2-5).
    is_resume_day(c,t) = vol(c,t)>0 AND no full-day S(c,t) AND c traded on an earlier session in the data, or was
                         young=False in the mask at the first session (seed_listed) (excludes IPO first day / never-traded codes) AND t is not the first data session (2018-01-02)
                         AND [ amount(c,t-1 session)<=0 (same basis as mask bar_prev)  OR  R record(c,t) ].
    Intraday S with a bar on t-1 and no R is NOT a resume (flag intraday_halt instead).
    State persists across years (no look-back window). available_at of is_resume_day = t 16:00 SH (needs vol)."""
    def __init__(self):
        self.first_done = False; self.prev_amt = set(); self.has_traded = set()
        self.last_traded = {}; self.last_sess_idx = {}; self.sess_idx = -1
        self.last_h = {}; self.last_f = {}; self.seeded = set()
    def step(self, date, vol_pos, amt_pos, fullday_S, R):
        """returns (resume_set, info dict code->(prev_traded_date, halt_sessions)) and advances the traded state."""
        self.sess_idx += 1
        if not self.first_done:
            res = set()
        else:
            cand = (vol_pos - fullday_S) & self.has_traded
            res = {c for c in cand if (c not in self.prev_amt) or (c in R)}
        info = {c: (self.last_traded.get(c), self.sess_idx - self.last_sess_idx[c] - 1 if c in self.last_sess_idx else None)
                for c in (vol_pos & self.has_traded)}
        for c in vol_pos:
            self.last_traded[c] = date; self.last_sess_idx[c] = self.sess_idx
        self.has_traded |= vol_pos; self.prev_amt = set(amt_pos); self.first_done = True
        return res, info
    def seed_listed(self, codes):
        """Before the first data session: codes that the frozen mask marks young=False (listed >=60 sessions) count as
        'traded before', so long halts spanning 2018-01-02 can still resume; IPOs after that start with no history."""
        if self.first_done: raise RuntimeError("seed_listed must precede the first step")
        self.seeded = set(codes); self.has_traded |= set(codes)
    def carry(self, c):  return self.last_h.get(c), self.last_f.get(c)
    def normal_seen(self, c):
        """True iff c had at least one traded & mask-not-suspended session in the data (i.e. carry state exists).
        Seeded codes halted from the first session have none -> carry_state 'unknown_pre_data' (Arch r3 P1-1)."""
        return c in self.last_h
    def update_pool(self, traded_nonresume_rows):
        """rows: iterable of (code, in_universe, fulla_v1) for codes traded on t and not resume/intraday-restored on t."""
        for c, h, f in traded_nonresume_rows:
            self.last_h[c] = bool(h); self.last_f[c] = bool(f)

UNKNOWN_PRE_DATA_LAST_YEAR = 2020   # Arch r4 P2-1: unknown_pre_data must be 0 from 2021 on

def classify_restore(year, code, suspended, traded, keep_v1, fullday_s, is_resume, intraday, carry, prev_traded_date, seeded):
    """Pure decision for one mask row (cs_panel_v2_resumefix D1b). Returns (hiliq_carry, fulla_carry, restore_reason, carry_state).
    candidate = mask suspended & traded & not kept by v1 & no full-day S & (resume or intraday halt).
    carry=(last_h,last_f) from the last traded & mask-not-suspended session (None,None if none).
    carry_state: 'known' | 'unknown_pre_data' (seeded, no vol>0 day in data before t) |
                 'unknown_no_normal_session' (traded before t, but every traded day was mask-suspended) |
                 'unknown_first_trade_in_data' (not seeded, first ever vol>0 day = IPO day with intraday halt) | ''.
    Raises ValueError on invariant breach (caller VOIDs): unknown_pre_data outside the seed set or after 2020."""
    if not (suspended and traded and not keep_v1 and not fullday_s and (is_resume or intraday)):
        return False, False, "", ""
    lh, lf = carry
    if lh is not None:
        return bool(lh), bool(lf), ("resume" if is_resume else "intraday_halt"), "known"
    if prev_traded_date is None:
        if code in seeded:
            if year > UNKNOWN_PRE_DATA_LAST_YEAR:
                raise ValueError(f"unknown_pre_data in {year} for {code} (must be 0 from 2021)")
            return False, False, "", "unknown_pre_data"
        if is_resume:
            raise ValueError(f"resume without prior trade for non-seeded {code} (ResumeState invariant)")
        return False, False, "", "unknown_first_trade_in_data"
    return False, False, "", "unknown_no_normal_session"

def check_manual_override(rows, expected) -> list:
    """r6c Arch P2-2 (pure): assert manual_override on the ACTUAL D3D4 output rows, not on the constant.
    rows: iterable of (ts_code, delist_period_source, delist_period_start, source_ann_no, override_source_verified).
    expected: {ts_code: period_start 'YYYYMMDD'}. Returns a list of violations (empty = pass); caller VOIDs.
    Rules: codes with source=='manual_override' == set(expected); each such row's period_start == expected[code];
    override source fields (source_ann_no non-empty or override_source_verified True) only on manual_override rows."""
    errs, seen = [], set()
    for code, src, start, ann_no, verified in rows:
        is_mo = src == "manual_override"
        if is_mo:
            seen.add(code)
            if code in expected and str(start) != expected[code]:
                errs.append(f"{code} manual_override period_start {start!r} != {expected[code]}")
        elif (isinstance(ann_no, str) and ann_no) or verified is True or str(verified) == "True":
            errs.append(f"{code} carries override source fields but delist_period_source={src!r}")
    if seen != set(expected):
        errs.append(f"manual_override codes {sorted(seen)} != expected {sorted(expected)}")
    return errs
