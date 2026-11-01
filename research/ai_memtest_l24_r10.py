#!/usr/bin/env python3
"""AI leaf 24 r10 memory re-test harness, build only (DRAFT rev 3, 2026-10-18 ET, per Arch 07:02 + Arch static review P2-a/P2-c/P2-d/P3; NOT RUN; needs Arch review + one Arch .ok per re-test).

Re-tests: T1 build_HILIQ (all three years) -> T2 build_FULLA (r10 P2-1 form) -> T3 build_FULLA --win 60 (rev3 P2-a). Nothing else. No eval / merge re-test, no proxy-alpha replica:
the formal eval's own watchdog + five checks are its memory measurement (exit 137 there -> stop, report to Arch, no retry, partial outputs to _void).

What it does: imports research/g1g5_imax_intraday_alpha.py (r10, sha pinned below; file unchanged) and calls its own build() unchanged, so the
measured VmHWM is the r10 build code's own. Differences from a formal run, all outside the measured code path:
  (1) authorisation: its own .ok (format quantlab_memtest_auth_v1, one per re-test); r10's read_ok(), verify_panel() and process_check() are
      called as in authorize(); the r10 RSS watchdog (1 s, VmRSS/VmHWM > 1536000 kB -> exit 137, fail-closed) starts before any data read;
  (2) out_dir = SCRATCH (output/ai_factory/_memtest/leaf24_r10), never the formal OUT_ROOT (output/ai_factory/leaf24_imax_intraday);
  (3) the module global R is rebound to SCRATCH/_ext_root after import (r10's only runtime use of R is evaluate()'s external files; kept as a
      second line of defence), and output/ai_factory/g1g5_imax_intraday_* is checked at start and at end (leak -> STOP);
  (4) evaluate() and merge() are replaced right after import by guards that STOP if called; the guards are re-asserted before and after build();
  (5) the upstream re-test meta (T2 needs T1's) is checked without arch_ok_sha256 (each re-test has its own .ok); leaf 23 completion and the
      tool .cmd are not checked (formal run only).
Re-test build outputs are NOT reused: the formal run (S01-) rebuilds everything in the formal out_dir. Afterwards Arch moves SCRATCH to
output/ai_factory/_void/ (nothing deleted). Metric: VmHWM printed by MEMTEST_END (no +180 margin); > 1300 MiB is not a failure but means stop
rev 3: (P2-a) T3 = build_FULLA with win=60 (sensitivity C window, variant win60), build only, standalone in its own scratch
  output/ai_factory/_memtest/leaf24_r10_win60 (needs no upstream; evaluate()/merge() stay guarded); (P2-c) the memtest .ok must carry explicit
  allow_build=true, allow_evaluate=false, allow_merge=false, allow_sensitivity (true for T3 only, false otherwise) and promotion_approved=false
  as fixed keys (missing / extra / different value -> refused, no exemptions); (P2-d) after build the harness re-reads its own build meta with
  r10 check_meta (outputs sha) and verifies every external_outputs entry by sha (build must list none -> STOP otherwise); the C4 wrapper is
  defined in the step table; (P3) exit 137 (watchdog os._exit, not catchable here): the step-table wrapper moves output/ai_factory/
  g1g5_imax_intraday_* to _void; at the end the harness re-confirms the formal OUT_ROOT is absent or empty.
and report to Arch; the hard line is 1536000 kB."""
import argparse, hashlib, importlib.util
from datetime import datetime
from pathlib import Path

ROOT = Path("/workspace/QuantLab")
TARGET = ROOT/"research/g1g5_imax_intraday_alpha.py"
TARGET_SHA = "53d3f8b1fe0c9906bb7a5b855af09e979f5bfa2075be65132a1878268fff707f"   # leaf 24 r10
SCRATCH = ROOT/"output/ai_factory/_memtest/leaf24_r10"
SCRATCH_T3 = ROOT/"output/ai_factory/_memtest/leaf24_r10_win60"   # rev3 P2-a: T3 own scratch (never shares T1/T2 build files)
TESTS = {"build_HILIQ": ("HILIQ", [], 20), "build_FULLA": ("FULLA", ["build_HILIQ"], 20), "build_FULLA_win60": ("FULLA", [], 60)}   # (uni, upstream, win)
FRESH = ["alpha_{u}_*", "gate_{u}_*", "coverage_{u}.parquet", "build_{u}_meta.json"]
EVAL_ARTEFACTS = ["summary_*", "eval_weights_*", "eval_*meta.json", "B3_carry_mismatch_*"]
TARGET_KB = 1300*1024
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

ap = argparse.ArgumentParser(description="AI leaf 24 r10 memory re-test, build only (requires an Arch memtest .ok)")
ap.add_argument("--test", required=True, choices=sorted(TESTS))
ap.add_argument("--panel-dir", required=True)
ap.add_argument("--arch-ok", required=True)
args = ap.parse_args()
uni, need, win = TESTS[args.test]
SCR = SCRATCH_T3 if win != 20 else SCRATCH   # rev3 P2-a

if sha(TARGET) != TARGET_SHA: raise SystemExit(f"refused: {TARGET.name} sha != r10 {TARGET_SHA[:12]}")
spec = importlib.util.spec_from_file_location("l24_r10", TARGET); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
M.rss_watchdog()   # r10 watchdog: 1 s poll of /proc/self/status, VmRSS or VmHWM > M.RSS_LIMIT_KB (1536000) -> RSS_GUARD_KILL, exit 137


def _forbidden(name):
    def guard(*_a, **_k):
        raise SystemExit(f"STOP (Arch 07:02): {name}() must never be called in the memory re-test — report to Arch")
    return guard


M.evaluate, M.merge = _forbidden("evaluate"), _forbidden("merge")   # (4)
GUARDS = (M.evaluate, M.merge)


def guards_intact(when):
    if M.evaluate is not GUARDS[0] or M.merge is not GUARDS[1]: raise SystemExit(f"STOP: evaluate()/merge() guard replaced ({when}) — report to Arch")


def no_leak(when):
    leak = sorted(p.name for p in M.AIF.glob("g1g5_imax_intraday_*"))
    if leak: raise SystemExit(f"STOP: leaf 24 external files in output/ai_factory ({when}) {leak[:5]} — report to Arch")


if M.RSS_LIMIT_KB != 1536000: raise SystemExit("refused: r10 RSS_LIMIT_KB != 1536000")
FIXED = {"format": "quantlab_memtest_auth_v1", "signed_by": "arch", "leaf": "24", "purpose": "memory_retest_build_only", "live": "false", "promotion": "false",
         "research_only": "true", "script_sha256": TARGET_SHA, "prereg_sha256": M.PREREG_SHA, "scratch_dir": str(SCR), "rss_limit_kb": "1536000",
         "run_niceness": "10", "test": args.test,
         "allow_build": "true", "allow_evaluate": "false", "allow_merge": "false", "allow_sensitivity": "true" if win != 20 else "false",
         "promotion_approved": "false"}   # rev3 P2-c: explicit allow_* + promotion_approved=false, exact values, no exemptions
REQ = ("harness_sha256", "cs_panel_dir", "cs_panel_manifest_sha256", "issued_at", "expires_et")
if not Path(args.arch_ok).is_file(): raise SystemExit("refused: Arch memtest .ok required (--arch-ok)")
ok = M.read_ok(args.arch_ok)   # r10 strict parser (no BOM / comments / duplicates / empty values)
allowed = set(FIXED) | set(REQ) | set(M.TOOLS)
if sorted(set(ok) - allowed): raise SystemExit(f"refused: memtest .ok has unknown keys {sorted(set(ok) - allowed)}")
if [k for k in sorted(allowed) if k not in ok]: raise SystemExit(f"refused: memtest .ok lacks keys {[k for k in sorted(allowed) if k not in ok]}")
checks = {k: ok[k] == v for k, v in FIXED.items()}
checks["harness_sha256"] = ok["harness_sha256"] == sha(__file__)
checks["prereg_file"] = sha(M.PREREG) == M.PREREG_SHA
checks["issued_at"] = M.tz_iso(ok["issued_at"])
checks["expires_et"] = M.not_expired(ok["expires_et"]) and checks["issued_at"] and datetime.fromisoformat(ok["expires_et"]) > datetime.fromisoformat(ok["issued_at"])
for k, f in M.TOOLS.items(): checks[k] = len(ok[k]) == 64 and Path(f).is_file() and ok[k] == sha(f)
bad = [k for k, v in checks.items() if not v]
if bad: raise SystemExit(f"refused: memtest .ok check failed {bad}")
panel = Path(args.panel_dir).resolve()
if not panel.is_dir(): raise SystemExit(f"refused: --panel-dir {panel} not found")
if SCR.resolve() == M.OUT_ROOT.resolve() or M.OUT_ROOT.resolve() in SCR.resolve().parents: raise SystemExit("refused: scratch inside formal out_dir")
if M.OUT_ROOT.exists() and any(M.OUT_ROOT.iterdir()): raise SystemExit(f"refused: formal out_dir {M.OUT_ROOT} is not empty (re-tests run before the formal run)")
no_leak("start")
pm = M.verify_panel(panel, ok)   # same panel / manifest / receipt / year-sha / build_version checks as r10 authorize()
proc = M.process_check()         # same: no other research/ python, niceness >= 10, MemAvailable >= 2 GB
tools = {k: sha(f) for k, f in M.TOOLS.items()}; M.AUTH_TOOLS.update(tools)
a = argparse.Namespace(stage="build", uni=uni, panel_dir=str(panel), arch_ok=args.arch_ok, src="intra", k=5, win=win, ex_fin=False, sealed=False)
auth = dict(script_sha256=TARGET_SHA, prereg_sha256=M.PREREG_SHA, arch_ok=str(Path(args.arch_ok).resolve()), arch_ok_sha256=sha(args.arch_ok), cs_panel=pm,
            tools=tools, tool_closure={}, tool_cmds="memtest: none", tool_cmds_sha256="memtest-none", issued_at=ok["issued_at"], expires_et=ok["expires_et"],
            process=proc, variant=M.variant_tag(a), primary=M.is_primary(a), out_dir=str(SCR), memtest=args.test, harness_sha256=ok["harness_sha256"])
if not need:
    if SCR.exists() and any(SCR.iterdir()): raise SystemExit(f"refused: scratch {SCR} is not empty (Arch voids it first)")
    SCR.mkdir(parents=True, exist_ok=True)
elif not SCR.is_dir(): raise SystemExit(f"refused: scratch {SCR} missing (run --test build_HILIQ first)")
up = {}
for st in need:   # upstream re-test meta: same r10 script / prereg / manifest / variant, outputs sha-checked (arch_ok_sha256 differs per re-test)
    mf = SCR/f"{st}_meta.json"
    M.check_meta(mf, dict(stage=st, script_sha256=TARGET_SHA, prereg_sha256=M.PREREG_SHA, cs_panel_manifest_sha256=pm["manifest_sha256"], variant="primary"))
    up[str(mf.relative_to(M.AIF))] = sha(mf)
M.guard_fresh(SCR, [p.format(u=uni) for p in FRESH])
ext = SCR/"_ext_root"; (ext/"output/ai_factory").mkdir(parents=True, exist_ok=True)
M.R = ext   # (3)
guards_intact("before build")
print(f"MEMTEST_START test={args.test} r10={TARGET_SHA[:12]} harness={ok['harness_sha256'][:12]} ok={auth['arch_ok_sha256'][:12]} scratch={SCR} win={win} variant={auth['variant']}", flush=True)
M.build(a, panel, SCR, auth, up)
guards_intact("after build")
mf_own = SCR/f"build_{uni}_meta.json"   # rev3 P2-d (C2): own build meta re-read; outputs sha via r10 check_meta, external_outputs sha here
m_own = M.check_meta(mf_own, dict(stage=f"build_{uni}", script_sha256=TARGET_SHA, arch_ok_sha256=auth["arch_ok_sha256"], prereg_sha256=M.PREREG_SHA,
                                  cs_panel_manifest_sha256=pm["manifest_sha256"], variant=auth["variant"]))
ext_out = m_own.get("external_outputs", {})
for f, h in ext_out.items():
    p = M.AIF/f if (M.AIF/f).is_file() else ext/"output/ai_factory"/f
    if not p.is_file() or sha(p) != h: raise SystemExit(f"STOP: external output {f} of {mf_own.name} changed or missing — report to Arch")
if ext_out: raise SystemExit(f"STOP: build meta lists external_outputs {sorted(ext_out)[:5]} (build must write none) — report to Arch")
no_leak("end")
ev = sorted(p.name for pat in EVAL_ARTEFACTS for p in SCR.glob(pat)) + sorted(str(p.relative_to(ext)) for p in ext.rglob("*") if p.is_file())
if ev: raise SystemExit(f"STOP: eval artefacts found in scratch {ev[:5]} — report to Arch")
if M.OUT_ROOT.exists() and any(M.OUT_ROOT.iterdir()): raise SystemExit(f"STOP: formal out_dir {M.OUT_ROOT} not empty at end — report to Arch")   # rev3 P3
M.peak_check(f"memtest end {args.test}")
v = M.vm_status()
print(f"MEMTEST_END test={args.test} vmhwm_kb={v['VmHWM']} vmhwm_mib={v['VmHWM']/1024:.1f} vmrss_kb={v['VmRSS']} target_1300mib={'within' if v['VmHWM'] <= TARGET_KB else 'ABOVE_TARGET_STOP_AND_REPORT_TO_ARCH'}", flush=True)
