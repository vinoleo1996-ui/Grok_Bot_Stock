#!/usr/bin/env python3
"""AMEND-1 §2 bit-equality proof for the Core v1.4 runner: run it twice (pool snapshot ON / OFF) and require every other
output to be byte-identical (sha256). Write-only check of "the snapshot never changes a decision path".

NOT a smoke and NOT a free run: it runs the full v1.4 window twice and is gated exactly like the runner:
  - output/strategy_optimizer/core_x2/ARCH_RUN_AUTH_v1_4.ok must exist (Arch writes it), with allow_equiv_check=true,
    live=false, promotion=false, equiv_script_sha256 == sha256 of this file, the 7 pinned input shas, python_exe, out_dir and
    equiv_root; --auth-sha256 must equal the .ok's sha256 (each sub-run re-checks all of this itself).
  - output/strategy_optimizer/core_x2/v1_4_equiv/ must be absent or empty (no resume / no retry), and no v1.4 lock may exist.
  - this script and both sub-runs must run under the .ok's python_exe and exactly R.DETERMINISM_ENV (single source in R).
Unified exception handling: if equiv_report.json is not produced, VOID.md is written in v1_4_equiv/.

THE .ok IS USED UP BY ANY OUTCOME OTHER THAN PASS (Arch P2-5): a FAIL verdict (exit code 2) consumes the .ok exactly like
a VOID (exit code 1). Neither may be retried; both require Arch re-review and a new .ok. Only PASS (exit 0) lets the full
run start (the runner checks equiv_report.json: verdict=PASS and the same code / .ok / inputs / interpreter / env).
After both sub-runs the pinned input shas are re-checked (Arch P1-2); a change makes the verdict FAIL.
live=false, promotion=false; no returns are computed.

Usage (only after Arch's .ok exists; log outside v1_4_equiv/):
  cd /workspace/QuantLab && PYTHONHASHSEED=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    nohup /workspace/QuantLab/.venv_opt/bin/python research/v1_4_snapshot_equiv_check.py --auth-sha256 <sha of .ok> \
    > output/strategy_optimizer/core_x2/v1_4_equiv_run.log 2>&1 &
"""
from __future__ import annotations
import argparse, hashlib, json, os, signal, subprocess, sys, time, traceback
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "research"))
import optimizer_core_x2_run_v1_4 as R   # import only (no side effects at import); reuses the runner's gate code

EQUIV_ROOT = R.EQUIV_ROOT
RUNNER = ROOT / R.RUNNER_REL
REPORT = R.EQUIV_REPORT
DETERMINISM_ENV = R.DETERMINISM_ENV      # Arch D18: identical to the runner's by construction (same object)
LOCK = R.CORE / R.EQUIV_CHECK_LOCK_NAME
_child = {"p": None}


class EquivAborted(BaseException):
    pass


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""): h.update(ch)
    return h.hexdigest()


def gate(auth_sha):
    """Same checks the runner does for mode=equiv, done up front for both sub-runs; writes nothing."""
    for k, (rel, pin) in R.PINNED_DOCS.items():
        if sha(ROOT / rel) != pin: raise SystemExit(f"equiv blocked: {rel} sha256 != pinned {pin}")
    R.check_input_paths()
    R.check_determinism_env()
    kv = R.parse_run_auth_v14(R.AUTH_PATH)
    R.enforce_run_auth_v14(kv, R.code_sha256_v14(), "equiv", sha(R.AUTH_PATH), auth_sha)   # live/promotion, dirs, 7 input shas
    R.check_interpreter(kv)
    if EQUIV_ROOT.exists() and any(EQUIV_ROOT.iterdir()):
        raise SystemExit(f"equiv blocked: {EQUIV_ROOT} is not empty (no resume / no retry; Arch must archive it)")
    if LOCK.exists(): raise SystemExit(f"equiv blocked: lock {LOCK} exists (Arch must archive it, P2-4)")
    for on in (True, False):
        R.check_out_dir(R.expected_out_dir("equiv", on), "equiv", on)
        R.check_no_lock("equiv", on)
    return kv, R.input_shas()


def run_one(on, auth_sha, python_exe):
    log = EQUIV_ROOT / f"run_snap_{'on' if on else 'off'}.log"
    cmd = [python_exe, str(RUNNER), "--mode", "equiv", "--pool-snapshot", "on" if on else "off", "--auth-sha256", auth_sha]   # P2-2
    env = dict(os.environ); env.update(DETERMINISM_ENV)
    t0 = time.time()
    with open(log, "w", encoding="utf-8") as f:
        p = subprocess.Popen(cmd, cwd=str(ROOT), env=env, stdout=f, stderr=subprocess.STDOUT)
        _child["p"] = p
        rc = p.wait()
        _child["p"] = None
    od = R.expected_out_dir("equiv", on)
    return {"cmd": cmd, "rc": rc, "elapsed_sec": round(time.time() - t0, 1), "log": log.name, "out_dir": str(od.relative_to(ROOT)),
            "summary_present": (od / "summary.json").exists(), "void_present": (od / "VOID.md").exists()}


def listing(od):
    out = {}
    for p in sorted(od.rglob("*")):
        if p.is_file():
            rel = str(p.relative_to(od))
            if rel in R.EXCLUDED_FROM_EQUIV or rel.endswith(".log") or rel.endswith(".tmp"): continue
            out[rel] = sha(p)
    return out


def compare():
    on_dir, off_dir = R.expected_out_dir("equiv", True), R.expected_out_dir("equiv", False)
    a, b = listing(on_dir), listing(off_dir)
    files = sorted(set(a) | set(b))
    rows = [{"file": f, "sha_on": a.get(f), "sha_off": b.get(f), "identical": a.get(f) is not None and a.get(f) == b.get(f)} for f in files]
    snap_on = on_dir / "core_v1_4_pool_snapshot.parquet"; snap_off = off_dir / "core_v1_4_pool_snapshot.parquet"
    schema = None
    if snap_on.exists():
        import pyarrow.parquet as pq
        schema = [f"{f.name}:{f.type}" for f in pq.read_schema(str(snap_on))]   # schema only (metadata), no data read
    return {"files": rows, "n_files": len(rows), "n_identical": sum(r["identical"] for r in rows),
            "mismatches": [r["file"] for r in rows if not r["identical"]],
            "snapshot_on_sha256": sha(snap_on) if snap_on.exists() else None, "snapshot_present_in_off_run": snap_off.exists(),
            "snapshot_schema": schema, "snapshot_schema_expected": [f"{f.name}:{f.type}" for f in R.SNAP_SCHEMA]}


def write_void(exc, tb, runs):
    lines = ["# VOID — v1.4 snapshot equivalence check did not produce equiv_report.json", "",
             f"- written: {R.et_now()} (automatic exception handler)", f"- exception: {type(exc).__name__}: {exc}",
             "- rule (Arch P2-r2-1 / P2-5): no report -> the whole check is void; no retry; the .ok is used up; Arch re-review + new .ok required.",
             f"- sub-runs: {json.dumps(runs, ensure_ascii=False, default=str)}", "", "```", tb, "```", ""]
    (EQUIV_ROOT / "VOID.md").write_text("\n".join(lines), encoding="utf-8")


def _sig(signum, frame):
    p = _child.get("p")
    if p is not None and p.poll() is None:
        p.terminate()   # child runner has its own handler -> it writes its own VOID.md
    raise EquivAborted(f"signal {signum}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="AMEND-1 snapshot on/off bit-equality check (Arch .ok required)")
    ap.add_argument("--auth-sha256", required=True)
    args = ap.parse_args(argv)
    kv, inputs_before = gate(args.auth_sha256)   # SystemExit = refused, nothing written
    R.acquire_lock(LOCK, {"pid": os.getpid(), "started_et": R.et_now(), "auth_sha256": args.auth_sha256, "argv": sys.argv})   # P2-4
    EQUIV_ROOT.mkdir(parents=True, exist_ok=True)
    for s in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT): signal.signal(s, _sig)
    runs = {}; rc = 0
    try:
        for on in (True, False):          # sequential: one process at a time (RSS ≤ 1.5 GB each)
            runs["on" if on else "off"] = r = run_one(on, args.auth_sha256, kv["python_exe"])
            if r["rc"] != 0 or not r["summary_present"]:
                raise RuntimeError(f"sub-run snapshot={'on' if on else 'off'} failed: rc={r['rc']} summary_present={r['summary_present']}")
        inputs_after = R.input_shas()     # Arch P1-2 / §7.7: re-check pinned inputs after both sub-runs
        inputs_changed = sorted(k for k in R.DATA_INPUTS if inputs_after[k] != inputs_before[k] or inputs_after[k] != kv[k])
        cmp_ = compare()
        ok = (not cmp_["mismatches"]) and cmp_["snapshot_on_sha256"] is not None and not cmp_["snapshot_present_in_off_run"] \
            and cmp_["snapshot_schema"] == cmp_["snapshot_schema_expected"] and not inputs_changed
        rep = {"verdict": "PASS" if ok else "FAIL", "amend_sha256": R.PINNED_DOCS["amend_sha256"][1], "code_sha256": R.code_sha256_v14(),
               "equiv_script_sha256": sha(Path(__file__).resolve()), "auth_sha256": args.auth_sha256, "auth_signed_et": kv.get("signed_et"),
               "excluded_from_comparison": list(R.EXCLUDED_FROM_EQUIV) + ["*.log", "*.tmp"], "determinism_env": DETERMINISM_ENV,
               "python_exe": kv["python_exe"], "interpreter": R.interpreter_info(),
               "inputs_sha256_before": inputs_before, "inputs_sha256_after": inputs_after, "inputs_changed": inputs_changed,
               "fail_consumes_ok": "FAIL (exit 2) uses up this .ok like a VOID; Arch re-review + new .ok required (Arch P2-5)",
               "runs": runs, "comparison": cmp_, "written_et": R.et_now(), "live": False, "promotion": False}
        tmp = REPORT.with_suffix(".json.tmp"); tmp.write_text(json.dumps(rep, indent=1, ensure_ascii=False, sort_keys=True)); os.replace(tmp, REPORT)
        print("EQUIV", rep["verdict"], "report", sha(REPORT), flush=True)
        rc = 0 if ok else 2
    except BaseException as e:  # noqa: BLE001
        rc = 1
        if not REPORT.exists():
            try: write_void(e, traceback.format_exc(), runs)
            except BaseException as e2: print(f"VOID write failed: {e2!r}", file=sys.stderr)
        print(f"EQUIV_VOID {type(e).__name__}: {e}", file=sys.stderr, flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
