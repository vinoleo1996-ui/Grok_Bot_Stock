"""Synthetic unit tests for relay_outage_backfill.step_status (pure; no real data, no network, no queue access).
Gated like scripts/fix_sd1/test_sd1_common.py: enforce(modes=["selftest"]) runs BEFORE importing the module under test.
Run (only after a selftest .ok is signed): PYTHONDONTWRITEBYTECODE=1 nice -n 10 python3 scripts/acquire/test_relay_outage_backfill_step_status.py"""
import sys, pathlib, tempfile
REPO = pathlib.Path("/workspace/QuantLab"); HERE = REPO / "scripts/acquire"
OK_PATH = REPO / "output/data/ARCH_RUN_AUTH_SELFTEST_BACKFILL_STEP_STATUS.ok"
sys.path.insert(0, str(REPO / "scripts_eng"))
from ok_runner_pin import enforce, parse_ok
_G = enforce(__file__, [OK_PATH], modes=["selftest"], deps={"relay_outage_backfill": HERE / "relay_outage_backfill.py"})
_KV = parse_ok(OK_PATH)
if _KV.get("scope") != "selftest": raise SystemExit("selftest gate: scope must be selftest")
if _KV.get("allow_real_data", "false").strip().lower() != "false": raise SystemExit("selftest gate: allow_real_data must be false")
_OUT = _KV.get("out_dir", "")
if not (_OUT == "mkdtemp" or _OUT.startswith("/tmp/")): raise SystemExit(f"selftest gate: out_dir {_OUT!r} must be mkdtemp or /tmp/<tag>")
import os
_cwd = os.getcwd()
sys.path.insert(0, str(HERE)); import relay_outage_backfill as B   # import only after gate; module main() is not called
os.chdir(_cwd)
from datetime import datetime, timezone
def iso(t): return datetime.fromtimestamp(t, timezone.utc).isoformat()
def run():
    d = tempfile.mkdtemp(dir=None if _OUT == "mkdtemp" else _OUT)
    t0 = 1_800_000_000.0; f = B.step_status
    S = lambda e, fin=t0 + 60: {"finished": iso(fin), "steps": {"sw": e}}
    # fresh ok
    assert f(S({"status": "ok", "sec": 50}), "sw", t0, t0 + 55) == ("ok", "ok", False)
    # fresh partial (not relay)
    st, r, rd = f(S({"status": "partial", "sec": 12}), "sw", t0, t0 + 30); assert st == "pending" and not rd and "partial" in r, (st, r, rd)
    # fresh fail
    st, r, rd = f(S({"status": "fail rc=-15", "sec": 7314}), "sw", t0, t0 + 30); assert st == "pending" and "fail rc=-15" in r
    # stale summary: finished before t0
    st, r, _ = f(S({"status": "ok", "sec": 50}, fin=t0 - 3600), "sw", t0, t0 + 55); assert st == "pending" and r.startswith("stale_summary"), r
    # stale entry: summary finished after t0 but step log not touched (merged older entry)
    st, r, _ = f(S({"status": "ok", "sec": 50}), "sw", t0, t0 - 100); assert st == "pending" and "log mtime" in r, r
    st, r, _ = f(S({"status": "ok", "sec": 50}), "sw", t0, None); assert st == "pending" and r.startswith("stale_summary"), r
    # unreadable / missing summary / missing entry / bad finished
    assert f(None, "sw", t0, t0 + 1)[:2] == ("pending", "summary_unreadable")
    assert f({"steps": "x"}, "sw", t0, t0 + 1)[:2] == ("pending", "summary_unreadable")
    assert f({"finished": iso(t0 + 1), "steps": {}}, "sw", t0, t0 + 1)[:2] == ("pending", "no_step_entry")
    assert f({"finished": "garbage", "steps": {"sw": {"status": "ok", "sec": 1}}}, "sw", t0, t0 + 1)[0] == "pending"
    # RELAY_DOWN via skipped (no log needed) and via partial + sec 0 (wording changed)
    st, r, rd = f(S({"status": "partial", "skipped": "RELAY_DOWN fast-fail", "sec": 0}), "sw", t0, None); assert st == "pending" and rd, (st, r, rd)
    st, r, rd = f(S({"status": "partial", "skipped": "relay unreachable", "sec": 0}), "sw", t0, None); assert st == "pending" and rd, (st, r, rd)
    st, r, rd = f(S({"status": "partial", "skipped": "RELAY_DOWN (new text)", "sec": 3}), "sw", t0, None); assert rd
    # rc != 0 with a fresh ok entry -> caller must not mark done (done requires rc==0 AND ok)
    st, _, _ = f(S({"status": "ok", "sec": 50}), "sw", t0, t0 + 55); rc = 1
    assert not (rc == 0 and st == "ok")
    import shutil; shutil.rmtree(d)
    print("ALL SYNTHETIC TESTS PASS")
run()
