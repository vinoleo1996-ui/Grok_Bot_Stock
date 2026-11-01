#!/usr/bin/env python3
"""SD0 parity runner r3 (Eng, 2026-10-18; Arch SD1 review 7f0b4819 §8 + addendum B; r2 review 73cb88ac P2-R1/P3-2/P3-7).

Proves the SD1 side engine quantlab/platform/execution_sd1.py with every SD1 switch at its default (exec_SD0)
reproduces the untouched quantlab/platform/execution.py (373fed30…486c) bit-for-bit on real books: each case is
recomputed twice into scratch and compared two-way:
    pristine : book_smoke with the REAL execution.py loaded as quantlab.platform.execution
    sd0      : book_smoke with execution_sd1.py loaded as quantlab.platform.execution (SD1 switches all default)
Each child loads its engine via importlib.util.spec_from_file_location BEFORE any quantlab import (quantlab/platform/
__init__.py L47 imports execution, so this is the only way the injection holds), executes exactly the bytes it hashed,
asserts run_weight_schedule.__code__.co_filename == the expected file (in-process and as bound in v2_multisleeve_book),
and prints the engine sha256 it actually executed; the parent checks it against the .ok dep pin.

Suites (one at a time; paper FIRST):
    paper     FIXED case list (no glob; Arch P1-8): capacity_adv 20261013 + paper extension 20261014_r2, B4 r2 60w/100w,
              S6 60w/100w — each at its AUM(s), windows X2 + PX (2024-06-03 -> last weight session)
    research  Core v1.3 x4, B4 leg-review 60w/100w, capacity_adv 20261013 x2 AUM (X2)   [Arch: released later]
    unit      the SD1 selftest file (its own in-code gate needs docs/v2/eng_sd1/ARCH_SD1_TEST.ok):
              PYTHONDONTWRITEBYTECODE=1, nice 10, /workspace/qlvenv/bin/python -m pytest ... -q -p no:cacheprovider

Gate: ok_runner_pin.enforce(__file__, [docs/v2/eng_sd1/ARCH_SD1_EXEC.ok], modes=[f"parity_{suite}"], deps=...) with
  module deps execution(=373fed30), execution_sd1, tradability, delist_accounting, platform_init, ok_runner_pin,
  book_smoke, v2_multisleeve_book (+ test_sd1_suspend_delist for unit) and one dep_sha256_w_<name> per weight file;
  plus runner-side checks: allow_smoke=false written explicitly; out_root=output/_sd0_parity; out_tag ends with this
  runner's sha256[:8]; exec_serial=true; exec_nice=10; rss_cap_mb<=1536. Output dir <out_root>/<suite>_<out_tag>
  created with mkdir(exist_ok=False); every report/JSON written with open(..., "x").
Process guards: os.nice(10) at start; one child at a time; parent polls /proc/<pid>/status VmRSS and VmHWM every
  0.2 s and kills a child whose VmRSS or VmHWM exceeds rss_cap_mb (FAIL_RSS); after each child, the child's own
  ru_maxrss (worker JSON) and the parent's RUSAGE_CHILDREN ru_maxrss are checked against the cap too (r3, Arch P3-2:
  over cap -> FAIL_RSS). Refuses within 16:40–18:40 ET (paper routine 17:40 ET ±1h), while another parity runner or a
  Data scripts/fix_sd1 rebuild is running — checked at start AND again before EVERY child process (r3, Arch P2-R1;
  a guard hit stops the run cleanly: case REFUSED_GUARD, report all_pass=false). Start before 14:00 ET.
  r3.1 (Arch 2b8f81c9 P3-1/P3-2): the guard is NOT re-checked while a child runs (a child that crosses 16:40 is not
  stopped; the 14:00 ET start rule covers it), so every case records child_started_et / child_finished_et (ET, with
  offset). Only the DIRECT child is polled; grandchildren are covered only afterwards by RUSAGE_CHILDREN (includes
  reaped grandchildren). SD1 (not SD0) stores TW/AW as float64 (r3): a future full-market SD1 run doubles the weight
  matrices (~2000 d x 5500 codes x 8 B ~ 88 MB each, ~176 MB for both) and must count that in the 1.5 GB budget.
  book_smoke HASH_FILES (full sha256) recorded before and after — a change voids the run. Parquet comparison includes
  the index (values, dtype, names; r3 Arch P3-7). No paper CLI, no writes outside the out dir. live=false; promotion=false.

  python3 scripts_eng/sd0_parity_runner.py --suite paper --out-tag <tag ending in runner sha8>
"""
from __future__ import annotations
import argparse, ast, datetime, hashlib, json, os, re, resource, signal, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OK = ROOT / "docs/v2/eng_sd1/ARCH_SD1_EXEC.ok"
OUT_ROOT = "output/_sd0_parity"
PRISTINE_SHA256 = "373fed309f055888e83572d3fbef8f5b5052ebfcb208307962a272bca6fc486c"
SLEEVES = '{"core":0.0,"stock":1.0,"alpha_event":0.0}'
RSS_CAP_MB = 1536
TEST_FILE = "tests/test_sd1_suspend_delist.py"
UNIT_PY = "/workspace/qlvenv/bin/python"     # system python3 has no pytest
ENGINE_FILES = {"pristine": "quantlab/platform/execution.py", "sd0": "quantlab/platform/execution_sd1.py"}
MODULE_DEPS = {
    "execution": "quantlab/platform/execution.py",
    "execution_sd1": "quantlab/platform/execution_sd1.py",
    "tradability": "quantlab/platform/tradability.py",
    "delist_accounting": "quantlab/platform/delist_accounting.py",
    "platform_init": "quantlab/platform/__init__.py",
    "ok_runner_pin": "scripts_eng/ok_runner_pin.py",
    "book_smoke": "quantlab/portfolio/book_smoke.py",
    "v2_multisleeve_book": "quantlab/portfolio/v2_multisleeve_book.py",
}
# FIXED paper case list (Arch P1-8): path + expected sha256 (also pinned by the .ok as dep_sha256_w_<key>)
PAPER_WEIGHTS = {
    "capadv_20261013": ("output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet",
                        "4348877ef927c85197a0068c219ab5a5f5957c7d11451a3ca68b73fd985d5caf"),
    "capadv_paper_20261014_r2": ("output/ai_factory/g1g5_capacity_adv_daily_weights_paper_20261014_r2.parquet",
                                 "e03028ee04f43aa33bc584a7846134d7e9001659655f49ecaaa3e6e5c1afd44c"),
    "b4_60w": ("output/small_aum_concentration/v2/B_B4_50_25_25_topN_60w_20261014_r2.parquet",
               "efcef7c43f919317baf2106f14c704a0d6d9351c910e8776a1d1f4cabf4f4480"),
    "b4_100w": ("output/small_aum_concentration/v2/B_B4_50_25_25_topN_100w_20261014_r2.parquet",
                "4736c030996fc631ec40ddaff9ae0dfb93c147f6191a346f3c0476edd57debf0"),
    "s6_60w": ("output/strategy_paper_s6/S6_cap50_ee25_eq25_topN_60w_20261014.parquet",
               "6ce63a7939a26e410ff2382d42b58988da4d8ace078f477f85f532c2c344cd9d"),
    "s6_100w": ("output/strategy_paper_s6/S6_cap50_ee25_eq25_topN_100w_20261014.parquet",
                "b1f9ae65483f0ffd161bc5a69e97b905cf634c26e9a58a88058afbd78f363a41"),
}
PAPER_CASES = [  # (name, weight key, AUM, windows, stored reference or None)
    ("paper_capadv_20261013_60w", "capadv_20261013", 600000, ["X2", "PX"], "output/v3/book_smoke_g1g5_capacity_adv_x2"),
    ("paper_capadv_20261013_100w", "capadv_20261013", 1000000, ["X2", "PX"], "output/v3/book_smoke_g1g5_capacity_adv_x2"),
    ("paper_capadv_paper_20261014_r2_60w", "capadv_paper_20261014_r2", 600000, ["X2", "PX"], None),
    ("paper_capadv_paper_20261014_r2_100w", "capadv_paper_20261014_r2", 1000000, ["X2", "PX"], None),
    ("paper_b4_60w", "b4_60w", 600000, ["X2", "PX"], None),
    ("paper_b4_100w", "b4_100w", 1000000, ["X2", "PX"], None),
    ("paper_s6_60w", "s6_60w", 600000, ["X2", "PX"], None),
    ("paper_s6_100w", "s6_100w", 1000000, ["X2", "PX"], None),
]
RESEARCH_WEIGHTS = {   # shas come only from the .ok (dep_sha256_w_<key>); research suite is reviewed after paper
    "core_equity_100_60w": "output/strategy_optimizer/core_x2/core_equity_100_60w.parquet",
    "core_equity_100_100w": "output/strategy_optimizer/core_x2/core_equity_100_100w.parquet",
    "core_equity80_etf20_510300_60w": "output/strategy_optimizer/core_x2/core_equity80_etf20_510300_60w.parquet",
    "core_equity80_etf20_510300_100w": "output/strategy_optimizer/core_x2/core_equity80_etf20_510300_100w.parquet",
    "b4_leg_review_60w": "output/strategy_hiliq/b4_leg_review/weights_B4_50_25_25_60w.parquet",
    "b4_leg_review_100w": "output/strategy_hiliq/b4_leg_review/weights_B4_50_25_25_100w.parquet",
    "capadv_20261013": "output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet",
}
RESEARCH_CASES = [
    *[(f"core_v1_3_{sl}_{a}w", f"core_{sl}_{a}w", a * 10000, ["X2"], f"output/strategy_optimizer/core_x2/book_smoke_v1_3_{sl}_{a}w")
      for sl in ("equity_100", "equity80_etf20_510300") for a in (60, 100)],
    *[(f"b4_leg_review_{a}w", f"b4_leg_review_{a}w", a * 10000, ["X2"], f"output/strategy_hiliq/b4_leg_review/smoke_B4_50_25_25_{a}w")
      for a in (60, 100)],
    *[(f"capadv_x2_{a}w", "capadv_20261013", a * 10000, ["X2"], "output/v3/book_smoke_g1g5_capacity_adv_x2") for a in (60, 100)],
]
SUITES = ("paper", "research", "unit")


def sha_file(p) -> str:
    h = hashlib.sha256()
    with open(ROOT / p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _refuse(msg):
    raise SystemExit(f"REFUSED (sd0_parity_runner): {msg}")


def _weights(suite):
    if suite == "paper":
        return {k: v[0] for k, v in PAPER_WEIGHTS.items()}
    if suite == "research":
        return dict(RESEARCH_WEIGHTS)
    return {}


def _gate(suite: str, out_tag: str) -> dict:
    if suite not in SUITES:
        _refuse(f"bad suite {suite}")
    if not OK.exists():
        _refuse(f"{OK.relative_to(ROOT)} missing (every run needs an Arch .ok)")
    sys.path.insert(0, str(ROOT / "scripts_eng"))
    import ok_runner_pin as PIN
    deps = {k: ROOT / v for k, v in MODULE_DEPS.items()}
    if suite == "unit":
        deps["test_sd1_suspend_delist"] = ROOT / TEST_FILE
    deps.update({f"w_{k}": ROOT / v for k, v in _weights(suite).items()})
    pin = PIN.enforce(__file__, [OK], modes=[f"parity_{suite}"], deps=deps)
    if pin.get("status") != "PINNED_MATCH":
        _refuse("ok_runner_pin did not return PINNED_MATCH")
    kv = PIN.parse_ok(OK)
    me = pin["runner_sha256"]
    if pin["deps"]["execution"] != PRISTINE_SHA256:
        _refuse("quantlab/platform/execution.py is not the pristine 373fed30 baseline")
    if suite == "paper":
        for k, (p, want) in PAPER_WEIGHTS.items():
            if pin["deps"][f"w_{k}"] != want:
                _refuse(f"weight {p} sha {pin['deps'][f'w_{k}']} != hardcoded {want}")
    if kv.get("allow_smoke") != "false":
        _refuse("the .ok must state allow_smoke=false explicitly")
    if kv.get("out_root") != OUT_ROOT:
        _refuse(f"out_root must be {OUT_ROOT} (got {kv.get('out_root')!r})")
    tag = kv.get("out_tag", "")
    if tag != out_tag or not re.fullmatch(r"[A-Za-z0-9._-]+", tag) or not tag.endswith(me[:8]):
        _refuse(f"out_tag must equal --out-tag and end with runner sha8 {me[:8]} (ok={tag!r}, argv={out_tag!r})")
    if kv.get("exec_serial") != "true" or kv.get("exec_nice") != "10":
        _refuse("exec_serial=true and exec_nice=10 are required")
    try:
        cap = int(kv.get("rss_cap_mb", ""))
    except ValueError:
        _refuse("rss_cap_mb missing / not an integer")
    if not (0 < cap <= RSS_CAP_MB):
        _refuse(f"rss_cap_mb must be in (0, {RSS_CAP_MB}]")
    return dict(runner_pin=pin, ok=str(OK.relative_to(ROOT)), ok_sha256=sha_file(OK.relative_to(ROOT)), rss_cap_mb=cap,
                out_tag=tag)


def _guard_reason() -> str | None:
    """Why no child may start now (None = OK). Called at start and before every child (Arch P2-R1)."""
    now = datetime.datetime.now()                 # box clock = America/New_York
    if datetime.time(16, 40) <= now.time() <= datetime.time(18, 40):
        return "inside the paper-routine window 16:40–18:40 ET (17:40 ET ± 1h)"
    mine, pid = set(), os.getpid()            # this process and its ancestors (the launching shell) are exempt
    while pid > 1 and pid not in mine:
        mine.add(pid)
        try:
            pid = int(next(l.split()[1] for l in Path(f"/proc/{pid}/status").read_text().splitlines() if l.startswith("PPid:")))
        except (OSError, StopIteration, ValueError):
            break
    for d in Path("/proc").iterdir():
        if not d.name.isdigit() or int(d.name) in mine:
            continue
        try:
            cmd = (d / "cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8", "replace")
        except OSError:
            continue
        if "sd0_parity_runner.py" in cmd and "python" in cmd:
            return f"another parity runner is running (pid {d.name})"
        if "scripts/fix_sd1/" in cmd:
            return f"a Data fix_sd1 rebuild is running (pid {d.name}: {cmd[:120]})"
    return None


def _process_guards():
    why = _guard_reason()
    if why:
        _refuse(why)


def _hash_files() -> dict:
    """book_smoke data HASH_FILES (parsed from the pinned v2_multisleeve_book source; nothing imported), full sha256."""
    tree = ast.parse((ROOT / MODULE_DEPS["v2_multisleeve_book"]).read_text())
    files = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id == "HASH_FILES" for t in n.targets))
    return {f: (sha_file(f) if (ROOT / f).exists() else None) for f in files}


WORKER = r'''
import hashlib, importlib.util, json, resource, sys
from pathlib import Path
ROOT = Path(sys.argv[1]); engine_rel, weights, cap, out, windows, px_end = sys.argv[2:8]
if any(m == "quantlab" or m.startswith("quantlab.") for m in sys.modules):
    raise SystemExit("REFUSED: quantlab already imported before engine injection")
sys.path.insert(0, str(ROOT))
eng_path = (ROOT / engine_rel).resolve()
src = eng_path.read_bytes(); eng_sha = hashlib.sha256(src).hexdigest()
spec = importlib.util.spec_from_file_location("quantlab.platform.execution", str(eng_path))
mod = importlib.util.module_from_spec(spec)
sys.modules["quantlab.platform.execution"] = mod            # BEFORE quantlab.platform/__init__ (L47) runs
exec(compile(src, str(eng_path), "exec"), mod.__dict__)     # exactly the hashed bytes
import quantlab.platform
if quantlab.platform.execution is not mod or sys.modules["quantlab.platform.execution"] is not mod:
    raise SystemExit("REFUSED: engine injection did not hold")
import quantlab.portfolio.v2_multisleeve_book as M
def _check():
    for f in (mod.run_weight_schedule, M.run_weight_schedule):
        if f.__code__.co_filename != str(eng_path):
            raise SystemExit(f"REFUSED: run_weight_schedule from {f.__code__.co_filename}, expected {eng_path}")
_check()
if px_end != "-":
    M.WINDOWS["PX"] = ("2024-06-03", px_end); M.WINDOW_LABEL["PX"] = "SD0 parity window (X2 + bridge, scratch only)"
from quantlab.portfolio.book_smoke import run
run(["--stock-path", weights, "--sleeves", %r, "--windows", windows, "--capitals", cap, "--arms", "BOOK,C0",
     "--out", out, "--receipt", out + "/RECEIPT.md"])
_check()
if hashlib.sha256(eng_path.read_bytes()).hexdigest() != eng_sha:
    raise SystemExit("REFUSED: engine file changed during the run")
print("PARITY_WORKER_JSON " + json.dumps(dict(engine_file=str(eng_path), engine_sha256=eng_sha,
      co_filename=mod.run_weight_schedule.__code__.co_filename,
      peak_rss_mb_self=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)))
''' % SLEEVES


def _vm_mb(pid) -> tuple[float | None, float | None]:
    """(VmRSS, VmHWM) in MB from /proc/<pid>/status; VmHWM covers peaks between polls."""
    rss = hwm = None
    try:
        for line in Path(f"/proc/{pid}/status").read_text().splitlines():
            if line.startswith("VmRSS:"):
                rss = int(line.split()[1]) / 1024
            elif line.startswith("VmHWM:"):
                hwm = int(line.split()[1]) / 1024
    except OSError:
        pass
    return rss, hwm


def _run_child(cmd, log: Path, cap_mb: int, env=None) -> dict:
    why = _guard_reason()                         # r3 (Arch P2-R1): re-check before EVERY child process
    if why:
        return dict(exit=None, refused_guard=why, killed_rss=False, over_cap_rusage=False)
    t_start = datetime.datetime.now().astimezone().isoformat(timespec="seconds")   # r3.1 (Arch P3-1)
    with open(log, "x", encoding="utf-8") as fh:
        p = subprocess.Popen(cmd, cwd=ROOT, stdout=fh, stderr=subprocess.STDOUT, env=env)
        peak, hwm_peak, killed = 0.0, 0.0, False
        while p.poll() is None:
            r, h = _vm_mb(p.pid)
            if r is not None:
                peak = max(peak, r)
            if h is not None:
                hwm_peak = max(hwm_peak, h)
            if (r is not None and r > cap_mb) or (h is not None and h > cap_mb):
                p.send_signal(signal.SIGKILL); killed = True; p.wait(); break
            time.sleep(0.2)
    t_end = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    children_maxrss_mb = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024   # cumulative max so far
    info = {}
    for line in reversed(log.read_text(encoding="utf-8", errors="replace").splitlines()):
        if line.startswith("PARITY_WORKER_JSON "):
            info = json.loads(line[len("PARITY_WORKER_JSON "):]); break
    self_mb = info.get("peak_rss_mb_self")
    over = bool((self_mb is not None and self_mb > cap_mb) or children_maxrss_mb > cap_mb)   # r3 (Arch P3-2)
    return dict(exit=p.returncode, child_started_et=t_start, child_finished_et=t_end, killed_rss=killed, over_cap_rusage=over, peak_rss_mb_polled=round(peak, 1),
                peak_vmhwm_mb_polled=round(hwm_peak, 1), parent_children_maxrss_mb_cum=round(children_maxrss_mb, 1),
                **info)


_DROP = {"run_id", "timestamp", "generated_at", "started_et", "finished_et"}


def _strip(o):
    if isinstance(o, dict):
        return {k: _strip(v) for k, v in o.items() if k not in _DROP}
    if isinstance(o, list):
        return [_strip(v) for v in o]
    return o


def _compare(a: Path, b: Path) -> dict:
    """Two-way: same file set; csv/other bytes-equal; parquet column-wise (float equal_nan=True); json whole
    after dropping run_id/timestamps; RECEIPT.md only for presence (it embeds run_id)."""
    import numpy as np, pandas as pd
    fa = {str(p.relative_to(a)) for p in a.rglob("*") if p.is_file()}
    fb = {str(p.relative_to(b)) for p in b.rglob("*") if p.is_file()}
    res = [dict(file=f, equal=False, why="only in " + ("pristine" if f in fa else "sd0")) for f in sorted(fa ^ fb)]
    for rel in sorted(fa & fb):
        x, y = a / rel, b / rel
        if x.name == "RECEIPT.md":
            continue
        if x.suffix == ".parquet":
            X, Y = pd.read_parquet(x), pd.read_parquet(y)
            eq = list(X.columns) == list(Y.columns) and X.shape == Y.shape and list(X.dtypes) == list(Y.dtypes)
            # r3 (Arch P3-7): the index too — values (NaN-aware via equals), dtype, names
            eq = eq and X.index.equals(Y.index) and X.index.dtype == Y.index.dtype and list(X.index.names) == list(Y.index.names)
            if eq:
                for c in X.columns:
                    if pd.api.types.is_float_dtype(X[c]):
                        eq &= bool(np.array_equal(X[c].to_numpy(), Y[c].to_numpy(), equal_nan=True))
                    else:
                        eq &= bool(X[c].reset_index(drop=True).equals(Y[c].reset_index(drop=True)))
        elif x.suffix == ".json":
            eq = _strip(json.loads(x.read_text())) == _strip(json.loads(y.read_text()))
        else:
            eq = x.read_bytes() == y.read_bytes()
        res.append(dict(file=rel, equal=bool(eq)))
    return dict(bit_identical=bool(res) and all(r["equal"] for r in res), n_files=len(res), files=res)


def _vs_ref(run_dir: Path, ref: str | None, cap: int) -> dict:
    if not ref:
        return dict(status="NO_STORED_REFERENCE")
    a = run_dir / f"aum_{cap}" / "X2" / "BOOK" / "nav.csv"
    b = ROOT / ref / f"aum_{cap}" / "X2" / "BOOK" / "nav.csv"
    if not (a.exists() and b.exists()):
        return dict(status="REFERENCE_MISSING", ref=ref)
    return dict(status="BYTES_EQUAL" if a.read_bytes() == b.read_bytes() else "DIFFERS", ref=ref,
                note="informational only (stored run may predate later code/data)")


def _last_session(path) -> str:
    import pandas as pd
    w = pd.read_parquet(ROOT / path)
    c = "session" if "session" in w.columns else "date"
    return str(pd.to_datetime(w[c].astype(str).str[:10]).max().date())


def _xwrite(path: Path, obj):
    with open(path, "x", encoding="utf-8") as fh:
        fh.write(json.dumps(obj, indent=1, ensure_ascii=False, default=str))


def main():
    os.nice(10)
    ap = argparse.ArgumentParser()
    ap.add_argument("--suite", required=True, choices=SUITES)
    ap.add_argument("--out-tag", required=True)
    a = ap.parse_args()
    _process_guards()
    gate = _gate(a.suite, a.out_tag)
    cap = gate["rss_cap_mb"]
    (ROOT / OUT_ROOT).mkdir(parents=True, exist_ok=True)
    root = ROOT / OUT_ROOT / f"{a.suite}_{gate['out_tag']}"
    root.mkdir(exist_ok=False)
    report = dict(suite=a.suite, started_et=datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                  gate=gate, live=False, promotion_approved=False, nice=os.nice(0), cases=[])
    if a.suite == "unit":
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        cmd = [UNIT_PY, "-m", "pytest", str(ROOT / TEST_FILE), "-q", "-p", "no:cacheprovider"]
        r = _run_child(cmd, root / "pytest.log", cap, env=env)
        rss_fail = r["killed_rss"] or r["over_cap_rusage"]
        report.update(cmd=cmd, run=r, all_pass=(r["exit"] == 0 and not rss_fail),
                      status=("REFUSED_GUARD" if r.get("refused_guard") else
                              "FAIL_RSS" if rss_fail else ("PASS" if r["exit"] == 0 else "FAIL")))
        report["finished_et"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        _xwrite(root / "SD1_UNIT_REPORT.json", report)
        print(json.dumps(dict(suite="unit", status=report["status"], out=str(root.relative_to(ROOT)))))
        raise SystemExit(0 if report["all_pass"] else 1)
    report["hash_files_before"] = _hash_files()
    weights = _weights(a.suite)
    cases = PAPER_CASES if a.suite == "paper" else RESEARCH_CASES
    pins = gate["runner_pin"]["deps"]
    aborted = None
    for name, wkey, aum, windows, ref in cases:
        if aborted:
            report["cases"].append(dict(name=name, status="NOT_RUN_ABORTED", why=aborted)); continue
        wpath = weights[wkey]
        w_sha = sha_file(wpath)
        rec = dict(name=name, weights=wpath, weights_sha256=w_sha, aum=aum, windows=windows)
        if w_sha != pins[f"w_{wkey}"]:
            rec["status"] = "REFUSED_WEIGHTS_SHA_MISMATCH"; report["cases"].append(rec); continue
        px_end = _last_session(wpath) if "PX" in windows else "-"
        rec["px_end"] = px_end
        (root / name).mkdir(exist_ok=False); (root / name / "logs").mkdir(exist_ok=False)
        runs = {}
        for engine in ("pristine", "sd0"):
            out = root / name / engine
            out.mkdir(exist_ok=False)
            r = _run_child([sys.executable, "-c", WORKER, str(ROOT), ENGINE_FILES[engine], wpath, str(aum),
                            str(out.relative_to(ROOT)), ",".join(windows), px_end],
                           root / name / "logs" / f"{engine}.log", cap, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
            want = pins["execution" if engine == "pristine" else "execution_sd1"]
            r["engine_sha_ok"] = r.get("engine_sha256") == want
            r["co_filename_ok"] = r.get("co_filename") == str((ROOT / ENGINE_FILES[engine]).resolve())
            runs[engine] = r
            if r.get("refused_guard"):
                aborted = r["refused_guard"]; break
            if r["exit"] != 0 or r["killed_rss"] or r["over_cap_rusage"] or not (r["engine_sha_ok"] and r["co_filename_ok"]):
                break
        rec["runs"] = runs
        if any(r.get("refused_guard") for r in runs.values()):
            rec["status"] = "REFUSED_GUARD"
        elif any(r.get("killed_rss") or r.get("over_cap_rusage") for r in runs.values()):
            rec["status"] = "FAIL_RSS"
        elif len(runs) == 2 and all(r["exit"] == 0 and r["engine_sha_ok"] and r["co_filename_ok"] for r in runs.values()):
            rec["parity"] = _compare(root / name / "pristine", root / name / "sd0")
            rec["vs_stored"] = _vs_ref(root / name / "pristine", ref, aum)
            rec["status"] = "PASS_BIT_IDENTICAL" if rec["parity"]["bit_identical"] else "FAIL_NOT_IDENTICAL"
        elif any(r["exit"] == 0 and not (r["engine_sha_ok"] and r["co_filename_ok"]) for r in runs.values()):
            rec["status"] = "FAIL_ENGINE_IDENTITY"
        else:
            rec["status"] = "RUN_ERROR"
        _xwrite(root / name / "CASE.json", rec)
        report["cases"].append(rec)
    report["hash_files_after"] = _hash_files()
    report["hash_files_stable"] = report["hash_files_before"] == report["hash_files_after"]
    report["finished_et"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    report["aborted"] = aborted
    report["all_pass"] = (bool(report["cases"]) and report["hash_files_stable"] and not aborted
                          and all(c.get("status") == "PASS_BIT_IDENTICAL" for c in report["cases"]))
    _xwrite(root / "SD0_PARITY_REPORT.json", report)
    print(json.dumps(dict(report=str((root / "SD0_PARITY_REPORT.json").relative_to(ROOT)), all_pass=report["all_pass"],
                          statuses={c["name"]: c.get("status") for c in report["cases"]}), ensure_ascii=False))
    raise SystemExit(0 if report["all_pass"] else 1)


if __name__ == "__main__":
    main()
