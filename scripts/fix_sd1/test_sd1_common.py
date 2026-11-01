"""Synthetic unit tests for sd1_common (no real data read). Gated per docs/v2/ARCH_RUN_AUTH_SELFTEST_SPEC_ZH.md:
enforce(modes=["selftest"]) runs BEFORE importing the module under test. Writes only into a mkdtemp under the .ok out_dir.
Run: PYTHONDONTWRITEBYTECODE=1 nice -n 10 python3 scripts/fix_sd1/test_sd1_common.py"""
import sys, tempfile, pathlib
REPO = pathlib.Path("/workspace/QuantLab"); HERE = REPO / "scripts/fix_sd1"
OK_PATH = REPO / "output/data/ARCH_RUN_AUTH_SELFTEST_SD1_COMMON.ok"
sys.path.insert(0, str(REPO / "scripts_eng"))
from ok_runner_pin import enforce, parse_ok
_G = enforce(__file__, [OK_PATH], modes=["selftest"], deps={"sd1_common": HERE / "sd1_common.py"})
_KV = parse_ok(OK_PATH)
if _KV.get("scope") != "selftest": raise SystemExit("selftest gate: scope must be selftest")
if _KV.get("allow_real_data", "false").strip().lower() != "false": raise SystemExit("selftest gate: this test reads no real data; allow_real_data must be false")
_OUT = _KV.get("out_dir", "")
if not (_OUT == "mkdtemp" or _OUT.startswith("/tmp/")): raise SystemExit(f"selftest gate: out_dir {_OUT!r} must be mkdtemp or /tmp/<tag>")
TMP_BASE = None if _OUT == "mkdtemp" else _OUT
import pandas as pd
sys.path.insert(0, str(HERE)); import sd1_common as C   # imported only after the gate passed
def run():
    s = C.ResumeState(); s.seed_listed({"A", "B", "H"})
    days = pd.bdate_range("2018-01-02", periods=6)
    # d0 first session: A traded after long halt -> forced False
    r, _ = s.step(days[0], {"A", "B"}, {"A", "B"}, set(), {"A"}); assert r == set(), r
    # d1: A full-day S; B trades; N = IPO first day
    r, _ = s.step(days[1], {"B", "N"}, {"B", "N"}, {"A"}, set()); assert r == set(), r
    s.update_pool([("B", True, True)])
    # d2: A resumes (no bar d1) -> resume; N 2nd day normal; B intraday S w/ prev bar, no R -> not resume
    r, info = s.step(days[2], {"A", "B", "N"}, {"A", "B", "N"}, set(), set()); assert r == {"A"}, r
    assert info["A"][1] == 1, info["A"]  # 1 halted session between
    # d3: B has R record even though traded d2 -> resume via R; H never traded before but seeded, no bar d2 -> resume
    r, _ = s.step(days[3], {"B", "H"}, {"B", "H"}, set(), {"B"}); assert r == {"B", "H"}, r
    # d4: full-day S but traded (data error) -> not resume
    r, _ = s.step(days[4], {"A"}, {"A"}, {"A"}, set()); assert r == set(), r
    # amount basis: vol>0 but amount==0 on d4 for X? -> X seeded? not seeded & never traded -> not resume
    r, _ = s.step(days[5], {"X"}, {"X"}, set(), set()); assert r == set(), r
    assert s.carry("B") == (True, True) and s.carry("A") == (None, None)
    # Arch r3 P1-1: seeded code H halted from the first session, resumed d3 -> no carry state, not normal_seen (must NOT abort)
    assert s.carry("H") == (None, None) and not s.normal_seen("H") and s.normal_seen("B")
    s2 = C.ResumeState(); s2.seed_listed({"P"}); dd = pd.bdate_range("2018-01-02", periods=3)
    s2.step(dd[0], set(), set(), {"P"}, set())                       # P full-day S on first session
    r, _ = s2.step(dd[1], {"P"}, {"P"}, set(), {"P"}); assert r == {"P"}   # resumes: is_resume_day True
    lh, lf = s2.carry("P"); assert (lh, lf) == (None, None) and not s2.normal_seen("P")  # -> carry_state unknown_pre_data, not restored
    s2.update_pool([("P", True, False)]); assert s2.normal_seen("P") and s2.carry("P") == (True, False)
    # classify_restore (cs D1b lines ~81-89 branch), Arch r4 P2-1
    cr = C.classify_restore; seed = {"S"}
    assert cr(2018, "A", False, True, False, False, True, False, (True, True), None, seed) == (False, False, "", "")      # not mask-suspended
    assert cr(2018, "A", True, True, True, False, True, False, (True, True), None, seed) == (False, False, "", "")        # kept by v1
    assert cr(2018, "A", True, True, False, True, True, False, (True, True), None, seed) == (False, False, "", "")        # full-day S
    assert cr(2019, "A", True, True, False, False, True, False, (True, False), "2019-01-02", seed) == (True, False, "resume", "known")
    assert cr(2019, "A", True, True, False, False, False, True, (False, True), "2019-01-02", seed) == (False, True, "intraday_halt", "known")
    assert cr(2018, "S", True, True, False, False, True, False, (None, None), None, seed) == (False, False, "", "unknown_pre_data")
    assert cr(2018, "S", True, True, False, False, False, True, (None, None), None, seed) == (False, False, "", "unknown_pre_data")
    assert cr(2019, "B", True, True, False, False, True, False, (None, None), "2018-05-02", seed) == (False, False, "", "unknown_no_normal_session")
    assert cr(2022, "N", True, True, False, False, False, True, (None, None), None, seed) == (False, False, "", "unknown_first_trade_in_data")
    for bad in [(2021, "S", True, True, False, False, True, False, (None, None), None, seed),     # pre_data after 2020
                (2018, "X", True, True, False, False, True, False, (None, None), None, seed)]:    # resume, never traded, not seeded
        try: cr(*bad); raise AssertionError("should raise")
        except ValueError: pass
    # gate parse: duplicate / missing / bad bool
    if TMP_BASE: pathlib.Path(TMP_BASE).mkdir(parents=True, exist_ok=True)
    d = pathlib.Path(tempfile.mkdtemp(dir=TMP_BASE))
    base = {**C.FIXED, "signed_et": "2026-10-18T02:00-04:00", "expires_et": "2099-01-01T00:00-04:00", "allow_full": "true", "allow_smoke": "false", "allow_dryrun": "false",
            "not_authorized": ",".join(sorted(C.NOT_AUTH_REQUIRED)), **{k: "0" * 64 for k in C.PINNED}}
    def w(kv, extra=""):
        p = d / "t.ok"; p.write_text("\n".join(f"{k}={v}" for k, v in kv.items()) + extra); return p
    C.parse_run_auth(w(base))
    for bad, extra in [({**base, "allow_full": "yes"}, ""), ({k: v for k, v in base.items() if k != "years"}, ""), (base, "\nformat=quantlab_run_auth_v1"),
                       ({**base, "version": "x"}, ""), ({**base, "mask_sha256": "abc"}, ""),
                       ({**base, "signed_et": "DRAFT_NOT_SIGNED"}, ""), ({**base, "run_niceness": "0"}, ""), ({**base, "allow_selftest": "maybe"}, ""),
                       ({**base, "not_authorized": "leaf_eval"}, ""),
                       ({k: v for k, v in base.items() if k != "expires_et"}, ""),                 # r6: expires_et required
                       ({**base, "expires_et": "2020-01-01T00:00-04:00"}, ""),                     # r6: expired
                       ({**base, "expires_et": "tomorrow"}, "")]:                                   # r6: not ISO8601
        try: C.parse_run_auth(w(bad, extra)); raise AssertionError("should block")
        except SystemExit: pass
    # r6: check_expiry boundary with injected now
    from datetime import datetime
    C.check_expiry({"expires_et": "2026-10-19T02:07:04-04:00"}, now=datetime.fromisoformat("2026-10-19T02:07:03-04:00"))
    try: C.check_expiry({"expires_et": "2026-10-19T02:07:04-04:00"}, now=datetime.fromisoformat("2026-10-19T02:07:04-04:00")); raise AssertionError("should block")
    except SystemExit: pass
    # r6: forbid list (pure classify_procs)
    P = [(1, "python3 scripts/nightly_update.py --date 20261015 --steps tier3", "T"),          # nightly: refuse in any state
         (2, "/usr/bin/python3 scripts/acquire/tier3_daily_snapshot.py --date 20261015", "S"),
         (3, "python3 scripts/acquire/relay_outage_backfill.py", "S"),
         (4, "python3 scripts/acquire/relay_outage_backfill.py", "T"),                            # stopped -> allowed
         (5, "nice -n 10 python3 scripts/fix_sd1/build_cs_panel_v2_resumefix.py --arch-ok x --fixes resume", "R"),
         (6, "python3 scripts/acquire/remaining_after_stk_surv.py", "S"),
         (7, "python3 research/strategy_x.py", "S"),
         (8, "python3 scripts/fix_sd1/build_x.py --note tier3", "S"),                             # bare word tier3 is not a pattern
         (9, "python3 scripts/acquire/relay_outage_backfill.py", "t")]                            # tracing stop != T -> refuse
    bad, allowed, m = C.classify_procs(P)
    assert [b.split()[0] for b in bad] == ["1", "2", "3", "7", "9"], bad
    assert [a.split()[0] for a in allowed] == ["4"], allowed
    assert {x["pid"]: x["verdict"] for x in m} == {1: "forbid", 2: "forbid", 3: "forbid_not_stopped", 4: "allowed_stopped", 7: "forbid", 9: "forbid_not_stopped"}
    assert all({"pid", "state", "cmd"} <= set(x) for x in m)
    # r6b: D3D4 expectation keys
    pe = C.parse_d3d4_expectations
    assert pe({}, False) == {"face": None, "unknown_count": None}                                   # dry-run: optional
    ok2 = {"expected_face_value_recategorised": "600297.SH, 002509.SZ,000861.SZ,002505.SZ", "expected_unknown_needs_source_count": "56"}
    assert pe(ok2, True) == {"face": ["000861.SZ", "002505.SZ", "002509.SZ", "600297.SH"], "unknown_count": 56}
    for badkv, ex in [({}, True), ({"expected_unknown_needs_source_count": "56"}, True), ({"expected_face_value_recategorised": "600297.SH"}, True),
                      ({**ok2, "expected_unknown_needs_source_count": "5x"}, False), ({**ok2, "expected_face_value_recategorised": "600297"}, False),
                      ({**ok2, "expected_face_value_recategorised": "600297.SH,600297.SH"}, False)]:
        try: pe(badkv, ex); raise AssertionError("should block")
        except SystemExit: pass
    C.parse_run_auth(w({**base, **ok2}))                                                               # keys accepted by the parser
    # r6c Arch P2-2: manual_override row check (pure)
    cm = C.check_manual_override; E = {"002509.SZ": "20200604"}
    good = [("002509.SZ", "manual_override", "20200604", "深证上【2020】442号", True), ("600297.SH", "namechange", "20240801", "", False), ("000001.SZ", "", None, "", False)]
    assert cm(good, E) == [], cm(good, E)
    assert cm(good + [("000002.SZ", "manual_override", "20200101", "x", True)], E)                    # extra code
    assert cm([r for r in good if r[0] != "002509.SZ"], E)                                             # missing code
    assert cm([("002509.SZ", "manual_override", "20200605", "a", True)] + good[1:], E)                 # wrong period_start
    assert cm(good + [("000003.SZ", "namechange", "20190101", "leaked", False)], E)                    # source field on non-override row
    assert cm(good + [("000004.SZ", "", None, "", True)], E)                                           # verified flag on non-override row
    import shutil; shutil.rmtree(d)
    print("ALL SYNTHETIC TESTS PASS")
run()
