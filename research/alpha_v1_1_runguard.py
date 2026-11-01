"""Run guard shared by research/alpha_combo_marginal_v1_1.py and research/alpha_hiliq_s8_paradigm_v1_1.py (Alpha, v1.1).
STDLIB ONLY: it is imported right after scripts_eng/ok_runner_pin.enforce (c7805d9a) has pinned it (dep_sha256_runguard) and BEFORE
numpy/pandas/project imports. Implements the .ok self-checks c7805d9a does not do (Arch 31b4b8ba P2-2; spec 1aa43bdd §2–§4, §9; same
pattern as research/g1g5_sue_desens_cs_alpha.py read_ok/not_expired and tests/test_sd1_suspend_delist.py _selftest_selfcheck),
the import-closure manifest check (Arch 31b4b8ba P2-1), output pre-checks (P3-2) and the RSS watchdog + RLIMIT_AS backstop (P3-4).
Research-grade; live=false; promotion=false."""
from __future__ import annotations
import datetime as _dt, hashlib, os, re, resource, sys, threading, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KNOWN_ALLOW = ("selftest", "real_data", "dryrun", "full", "execute", "smoke", "diagnostic", "disclosure_only")
ISO_TZ = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?([+-]\d{2}:\d{2})$")
KEY = re.compile(r"^[A-Za-z0-9_\[\]./-]+$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
RSS_LIMIT_KB = 1536000                       # Arch: single process ≤ 1.5 GB (= 1500 MiB)
RLIMIT_AS_KB_DEFAULT = 6291456              # 6 GiB virtual backstop (not RSS; see docstring of start_watchdog)
RLIMIT_ENV = "ALPHA_V11_RLIMIT_AS_KB"


def refuse(msg: str):
    raise SystemExit(f"REFUSED (alpha_v1_1_runguard): {msg}")


def sha256_file(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()


def read_ok_strict(path) -> dict:
    """quantlab_run_auth_v1 strict parse: no BOM anywhere, LF only (no CR), whole-line '#' comments and blank lines allowed,
    every other line ^key=\\S+$ (no spaces, no inline comment), no duplicate key (even with the same value), no empty value."""
    p = Path(path); raw = p.read_bytes()
    if b"\xef\xbb\xbf" in raw: refuse(f"{p}: contains a UTF-8 BOM")
    if b"\r" in raw: refuse(f"{p}: CR line ending (LF only)")
    kv = {}
    for n, line in enumerate(raw.decode("utf-8").split("\n"), 1):
        if line == "" or line.startswith("#"): continue
        if "=" not in line: refuse(f"{p}: line {n} has no '=': {line[:60]!r}")
        k, v = line.split("=", 1)
        if not KEY.fullmatch(k): refuse(f"{p}: line {n} bad key {k[:40]!r}")
        if v == "" or re.search(r"\s", v) or "#" in v: refuse(f"{p}: line {n} value empty / has whitespace / inline comment: {line[:60]!r}")
        if k in kv: refuse(f"{p}: key {k!r} duplicated (line {n})")
        kv[k] = v
    return kv


def tz_iso(v) -> bool:
    if not isinstance(v, str) or not ISO_TZ.match(v): return False
    try: d = _dt.datetime.fromisoformat(v)
    except ValueError: return False
    return d.tzinfo is not None and d.utcoffset() is not None


def not_expired(v) -> bool:
    return tz_iso(v) and _dt.datetime.fromisoformat(v) > _dt.datetime.now().astimezone()


def ok_selfcheck(ok_paths, gate: dict, mode: str, out_target: Path | None = None) -> dict:
    """After enforce(): every .ok that pins the runner (gate['pins']) must have format/signer, tz-aware signed_et (not in the future)
    and expires_et (not expired, after signed_et), scope == mode, every KNOWN_ALLOW key explicit true|false, allow_<mode>=true and all
    other allow_* false (allow_real_data: selftest → false; full → explicit, either value), live/promotion false; optional out_dir must
    match the actual output location (full) or be mkdtemp / /tmp/<tag> outside the repo (selftest)."""
    if mode not in ("full", "selftest"): refuse(f"unknown mode {mode!r}")
    pinning = [Path(o) for o in (gate or {}).get("pins", {})] or [Path(o) for o in ok_paths]
    now = _dt.datetime.now().astimezone(); rec = {}
    for o in pinning:
        kv = read_ok_strict(o)
        for k, want in (("format", "quantlab_run_auth_v1"), ("signed_by", "arch"), ("scope", mode), ("live", "false"), ("promotion", "false")):
            if kv.get(k) != want: refuse(f"{o}: {k} must be {want!r} (got {kv.get(k)!r})")
        for k in ("signed_et", "expires_et"):
            if not tz_iso(kv.get(k)): refuse(f"{o}: {k}={kv.get(k)!r} is not ISO8601 with a UTC offset")
        se, ex = _dt.datetime.fromisoformat(kv["signed_et"]), _dt.datetime.fromisoformat(kv["expires_et"])
        if ex <= now: refuse(f"{o}: expired at {kv['expires_et']}")
        if ex <= se: refuse(f"{o}: expires_et not after signed_et")
        if se > now + _dt.timedelta(minutes=5): refuse(f"{o}: signed_et in the future")
        for m in KNOWN_ALLOW:
            v = kv.get(f"allow_{m}")
            if v not in ("true", "false"): refuse(f"{o}: allow_{m} must be written explicitly as true|false (got {v!r})")
        if kv[f"allow_{mode}"] != "true": refuse(f"{o}: allow_{mode} must be true")
        for k, v in kv.items():
            if k.startswith("allow_") and k not in (f"allow_{mode}", "allow_real_data") and v != "false":
                refuse(f"{o}: {k}={v}; every allow_* other than allow_{mode}/allow_real_data must be false")
        if mode == "selftest" and kv["allow_real_data"] != "false": refuse(f"{o}: synthetic selftest requires allow_real_data=false")
        od = kv.get("out_dir")
        if mode == "selftest":
            if od != "mkdtemp" and not (od and re.fullmatch(r"/tmp/[A-Za-z0-9._-]+", od)): refuse(f"{o}: out_dir must be mkdtemp or /tmp/<tag> (got {od!r})")
        elif od is not None and out_target is not None and Path(od if Path(od).is_absolute() else ROOT / od).resolve() != Path(out_target).resolve():
            refuse(f"{o}: out_dir {od} != actual output location {out_target}")
        rec[str(o)] = dict(sha256=sha256_file(o), scope=kv["scope"], signed_et=kv["signed_et"], expires_et=kv["expires_et"],
                           allow_real_data=kv["allow_real_data"], out_dir=od)
    return rec


def recheck_expiry(rec: dict, stage: str):
    """Re-check before each stage / before writing outputs: same bytes as at start, and not expired."""
    for o, r in rec.items():
        if sha256_file(o) != r["sha256"]: refuse(f"{o}: .ok changed since start ({stage})")
        if not not_expired(r["expires_et"]): refuse(f"{o}: expired at {r['expires_et']} ({stage})")


def rlimit_as_kb() -> int:
    """RLIMIT_AS value: default 6 GiB; env ALPHA_V11_RLIMIT_AS_KB may override but must be an integer > RSS_LIMIT_KB (0 / negative /
    non-integer / ≤ RSS limit would disable or defeat the backstop → refused, Arch 6ab489c8 P3-1). Recorded in env_snapshot()."""
    v = os.environ.get(RLIMIT_ENV)
    if v is None: return RLIMIT_AS_KB_DEFAULT
    if not re.fullmatch(r"[0-9]+", v.strip()) or int(v) <= RSS_LIMIT_KB:
        refuse(f"{RLIMIT_ENV}={v!r} must be an integer KB > {RSS_LIMIT_KB} (cannot disable the RLIMIT_AS backstop)")
    return int(v)


def vm_peak_kb() -> int | None:
    """VmPeak (peak virtual size, KB) from /proc/self/status, for the receipt (Arch 6ab489c8 P3-3)."""
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmPeak:"): return int(line.split()[1])
    except OSError:
        return None
    return None


def load_manifest(path) -> dict:
    """sha256sum-format manifest '<64hex>  <repo-relative path>' (one per line)."""
    out = {}
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").split("\n"), 1):
        if not line or line.startswith("#"): continue
        m = re.fullmatch(r"([0-9a-f]{64})  (\S+)", line)
        if not m or m.group(2) in out: refuse(f"{path}: bad/duplicate manifest line {n}: {line[:80]!r}")
        out[m.group(2)] = m.group(1)
    return out


def verify_closure(manifest_path, stage: str) -> dict:
    """Arch 31b4b8ba P2-1: every manifest file still has its recorded sha, and every project module loaded in this process (any
    sys.modules entry whose file lies under the repo) is listed in the manifest. Fail closed."""
    man = load_manifest(manifest_path)
    verify_manifest_shas(manifest_path, stage)
    loaded = set()
    for mod in list(sys.modules.values()):
        f = getattr(mod, "__file__", None)
        if not f: continue
        try: rel = str(Path(f).resolve().relative_to(ROOT))
        except ValueError: continue
        if rel.endswith(".py"): loaded.add(rel)
    extra = sorted(loaded - set(man))
    if extra: refuse(f"closure manifest: loaded project modules not in manifest ({stage}): {extra}")
    return dict(manifest=str(Path(manifest_path).resolve().relative_to(ROOT)), n_listed=len(man), n_loaded=len(loaded), stage=stage)


def verify_manifest_shas(manifest_path, stage: str) -> dict:
    """Every manifest file still has its recorded sha (run at startup too, before heavy imports — Arch 6ab489c8 P3-2)."""
    man = load_manifest(manifest_path)
    for rel, h in man.items():
        if sha256_file(ROOT / rel) != h: refuse(f"closure manifest: {rel} sha changed ({stage})")
    return dict(n_listed=len(man), stage=stage, all_sha_match=True)


def precheck_out_file(p) -> Path:
    p = Path(p).resolve()
    if p.exists(): refuse(f"--out {p} already exists (no overwrite; Arch decides cleanup)")
    return p


def precheck_out_dir(p) -> Path:
    p = Path(p).resolve()
    if p.exists() and (not p.is_dir() or any(p.iterdir())): refuse(f"out_dir {p} not empty (no overwrite; Arch decides cleanup)")
    return p


def rss_kb() -> int:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss   # Linux: KB, peak


def set_rlimit_as(kb: int):
    """Hard backstop on VIRTUAL address space (Linux ignores RLIMIT_RSS). Allocation beyond it raises MemoryError instead of growing."""
    b = int(kb) * 1024
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    if hard != resource.RLIM_INFINITY: b = min(b, hard)
    resource.setrlimit(resource.RLIMIT_AS, (b, hard))
    return b


def start_watchdog(limit_kb: int | None = None, poll_s: float = 0.5, rlimit_as_kb: int | None = None, exit_code: int = 3):
    """Primary: poll peak RSS every poll_s; above limit_kb → print STOP and os._exit(exit_code). Backstop: RLIMIT_AS (virtual, so set
    well above the RSS limit; pandas/pyarrow reserve virtual memory they never touch). Disclosed: polling can overshoot within poll_s."""
    lim = RSS_LIMIT_KB if limit_kb is None else int(limit_kb)
    applied = set_rlimit_as(rlimit_as_kb) if rlimit_as_kb else None
    def loop():
        while True:
            if rss_kb() > lim:
                print(f"STOP: peak RSS {rss_kb()} KB > {lim} KB", flush=True); os._exit(exit_code)
            time.sleep(poll_s)
    threading.Thread(target=loop, daemon=True, name="alpha_v11_rss_watchdog").start()
    return dict(rss_limit_kb=lim, poll_s=poll_s, rlimit_as_bytes=applied)


def env_snapshot() -> dict:
    """Arch 31b4b8ba P3-9: research/g1g5_x2_panel_stitch.py lets QL_X2_EXTEND_END override X2_END; v1.1 truncates P/F at END so it
    cannot change results, but its value is recorded in every output."""
    return {"QL_X2_EXTEND_END": os.environ.get("QL_X2_EXTEND_END"), RLIMIT_ENV: os.environ.get(RLIMIT_ENV),
            "rlimit_as_kb_effective": rlimit_as_kb()}
