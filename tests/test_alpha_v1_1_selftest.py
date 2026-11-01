"""Alpha CMC v1.1 / s8 v1.1 synthetic selftest (Arch review docs/v2/ARCH_ALPHA_CMC_S8_V1_1_REVIEW_ZH.md 31b4b8ba §4/§6; run-auth spec
docs/v2/ARCH_RUN_AUTH_SELFTEST_SPEC_ZH.md 1aa43bdd). SYNTHETIC DATA ONLY: no file outside the mkdtemp out_dir is ever read as data
(pandas.read_parquet is wrapped and refuses any path outside it); ADG.bench / ADG._close are monkeypatched; the SW member table,
to_panel_id and industry_on_date come from in-memory stub modules (research.g1g5_nontextbook_weights / research.g1g5_x2_panel_stitch /
research.hiliq_v1_universe are NOT imported).

GATE (module top level, at collection time, BEFORE any module under test is imported):
  ok_runner_pin.enforce(__file__, [output/alpha/ARCH_RUN_AUTH_SELFTEST_CMC_S8_V1_1.ok], modes=["selftest"], deps=TEST_DEPS), then
  research/alpha_v1_1_runguard.ok_selfcheck(mode="selftest") (scope=selftest, every known allow_* explicit, only allow_selftest true,
  allow_real_data=false, out_dir = mkdtemp or /tmp/<tag>, no BOM / CR / inline comments, signed_et + expires_et with offset, not
  expired). A refusal raises SystemExit (aborts collection); there is no skip path. The scripts' own __main__ gates (mode 'full') are
  never executed here: the tests import their functions.

Run (qlvenv), serial, nothing else concurrently, RSS ≤ 1.5 GB:
  PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python -m pytest tests/test_alpha_v1_1_selftest.py -q -p no:cacheprovider
Writes only under the mkdtemp out_dir (removed at exit). live=false; promotion=false.
"""
from __future__ import annotations

import atexit
import datetime as _dt
import hashlib
import json
import os
import shutil
import sys
import tempfile
import time
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST_OK = ROOT / "output/alpha/ARCH_RUN_AUTH_SELFTEST_CMC_S8_V1_1.ok"
# every project module this file imports (directly or transitively; static AST closure with the three stubbed modules excluded)
TEST_DEPS = {
    "combo_v1_1": "research/alpha_combo_marginal_v1_1.py",
    "s8_v1_1": "research/alpha_hiliq_s8_paradigm_v1_1.py",
    "ok_runner_pin": "scripts_eng/ok_runner_pin.py",
    "runguard": "research/alpha_v1_1_runguard.py",
    "adg": "research/alpha_decay_gate.py",
    "selfcheck_v3": "research/leaf_selfcheck_v3.py",
    "selfcheck_common": "research/leaf_selfcheck_common.py",
}

if not sys.flags.dont_write_bytecode:          # checked BEFORE the gate module is imported (no __pycache__ in the repo)
    raise SystemExit("REFUSED (test_alpha_v1_1): run with PYTHONDONTWRITEBYTECODE=1")
sys.path.insert(0, str(ROOT / "scripts_eng"))
import ok_runner_pin as _PIN  # noqa: E402
_GATE = _PIN.enforce(__file__, [TEST_OK], modes=["selftest"], deps={k: ROOT / v for k, v in TEST_DEPS.items()})
sys.path.insert(0, str(ROOT))
import research.alpha_v1_1_runguard as RG  # noqa: E402  (pinned just above; stdlib only)
_OKREC = RG.ok_selfcheck([TEST_OK], _GATE, "selftest")
OUT_DIR = Path(tempfile.mkdtemp(prefix="alpha_v11_selftest_")).resolve()
if OUT_DIR == ROOT or ROOT in OUT_DIR.parents or "output" in OUT_DIR.parts:
    raise SystemExit(f"REFUSED (test_alpha_v1_1): out_dir {OUT_DIR} inside the repo / output/")
atexit.register(shutil.rmtree, str(OUT_DIR), True)

# ---- gate passed: only now import numpy/pandas/pytest and the modules under test
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import pytest  # noqa: E402

_REAL_READ_PARQUET = pd.read_parquet
READS: list = []                                            # (resolved path, filters) of every parquet read (Arch 6ab489c8 P1-1)


def _guarded_read_parquet(path, *a, **k):
    rp = Path(path).resolve()
    if OUT_DIR not in rp.parents:
        raise AssertionError(f"real-data read attempted in synthetic selftest: {path}")
    READS.append((rp, k.get("filters")))
    return _REAL_READ_PARQUET(path, *a, **k)


pd.read_parquet = _guarded_read_parquet


# ---- in-memory stubs (same semantics as the real helpers; no data files)
def _to_panel_id(instrument: str) -> str:
    a, b = str(instrument).split(".", 1)
    return f"{b.lower()}.{a}"


SW = {"df": None}


def _load_sw_members():
    return SW["df"]


def _sw_code_on(instrument, session, sw):
    sub = sw[sw["instrument_id"] == _to_panel_id(instrument)]
    sess = pd.Timestamp(session).normalize()
    hit = sub[(sub["in_date"] <= sess) & (sub["out_date"].isna() | (sub["out_date"] > sess))]
    return None if hit.empty else str(hit.iloc[-1]["sw_code"])


def _industry_on_date(instruments, session, sw):
    return {i: c for i in instruments if (c := _sw_code_on(i, session, sw)) is not None}


_stubs = {
    "research.g1g5_x2_panel_stitch": dict(to_panel_id=_to_panel_id),
    "research.g1g5_nontextbook_weights": dict(_load_sw_members=_load_sw_members, sw_code_on=_sw_code_on, to_panel_id=_to_panel_id),
    "research.hiliq_v1_universe": dict(industry_on_date=_industry_on_date),
}
for _name, _attrs in _stubs.items():
    _m = types.ModuleType(_name); _m.__dict__.update(_attrs); _m.__file__ = None
    sys.modules[_name] = _m

import research.alpha_decay_gate as ADG  # noqa: E402
import research.alpha_combo_marginal_v1_1 as CMC  # noqa: E402
import research.alpha_hiliq_s8_paradigm_v1_1 as S8  # noqa: E402

START, END, H = CMC.START, CMC.END, CMC.H
CAL = pd.bdate_range("2023-06-01", "2026-11-30")          # 2024-05-31 (Fri) is the last session before START 2024-06-03 (Mon)
NAMES = [f"{600000 + k}.SH" for k in range(40)] + [f"{1 + k:06d}.SZ" for k in range(40)]
D = pd.Timestamp("2025-03-03")                              # probe day d (window session)


class Synth:
    def __init__(self, seed=7):
        rng = np.random.default_rng(seed)
        self.bench = pd.Series(100 * np.exp(np.cumsum(rng.normal(0, .01, len(CAL)))), index=CAL)
        self.close = {i: pd.Series(10 * np.exp(np.cumsum(rng.normal(0, .02, len(CAL)))), index=CAL) for i in NAMES}
        win = CAL[(CAL >= START) & (CAL <= END)]
        self.mask = pd.DataFrame([(d, i, True, float(rng.uniform(5e7, 5e8))) for d in win for i in NAMES],
                                 columns=["date", "instrument", "in_universe", "adv20_yuan"])
        fdays = CAL                                         # from 2023-06-01: pre-window rows exist, so the START filter is exercised
        self.fmc = pd.DataFrame([(_to_panel_id(i), d, float(v)) for i in NAMES
                                 for d, v in zip(fdays, 1e9 * np.exp(np.cumsum(rng.normal(0, .01, len(fdays)))))],
                                columns=["instrument_id", "trade_date", "float_mktcap"])
        self.sw = pd.DataFrame(dict(instrument_id=[_to_panel_id(i) for i in NAMES], in_date=pd.Timestamp("2020-01-01"), out_date=pd.NaT,
                                    sw_code=[f"80{k % 5}" for k in range(len(NAMES))]))

    def copy(self):
        o = Synth.__new__(Synth)
        o.bench = self.bench.copy(); o.close = {k: v.copy() for k, v in self.close.items()}
        o.mask = self.mask.copy(); o.fmc = self.fmc.copy(); o.sw = self.sw.copy()
        return o


def _install(s: Synth, tag: str):
    """Write synthetic mask/FMC into a fresh dir under OUT_DIR and point both modules at it."""
    d = OUT_DIR / f"{tag}_{time.time_ns()}"; d.mkdir()
    s.mask.to_parquet(d / "mask.parquet"); s.fmc.to_parquet(d / "fmc.parquet")
    CMC.UNIVERSE_MASKS["hiliq"] = d / "mask.parquet"; CMC.FMC = d / "fmc.parquet"; CMC.UNIVERSE = "hiliq"
    S8.MASK = d / "mask.parquet"; S8.FMC = d / "fmc.parquet"; S8.OUT = d / "s8"; S8.OUT.mkdir()
    ADG.bench = lambda: s.bench
    ADG._close = lambda i: s.bench if i == ADG.B else s.close[i]
    SW["df"] = s.sw
    CMC._CTX.clear(); CMC._B0.clear(); S8._XC.clear()


def cmc_ctx(s, tag="cmc"):
    _install(s, tag); return dict(CMC.ctx())


def s8_ctx(s, tag="s8"):
    _install(s, tag); return S8.build()


def _eq(a, b):
    return np.allclose(np.asarray(a, float), np.asarray(b, float), equal_nan=True)


BASE = Synth()


def _shifted_session(d, k):
    return CAL[CAL.get_loc(d) - k]


# ======================= t−1 property =======================
def test_cmc_exposures_t_minus_1():
    c0 = cmc_ctx(BASE)
    s1 = BASE.copy()                                                  # change ONLY day-d data
    for i in NAMES: s1.close[i].loc[D] *= 1.07
    s1.bench.loc[D] *= 1.03
    s1.fmc.loc[s1.fmc.trade_date == D, "float_mktcap"] *= 1.5
    c1 = cmc_ctx(s1)
    assert _eq(c0["MC"].loc[D], c1["MC"].loc[D]), "mc_{t−1} moved with day-d data"
    assert _eq(c0["beta"].loc[D], c1["beta"].loc[D]), "beta_{t−1} moved with day-d data"
    s2 = BASE.copy(); dm1 = _shifted_session(D, 1)                    # change day d−1 → exposures at d must move
    for i in NAMES: s2.close[i].loc[dm1] *= 1.07
    s2.fmc.loc[s2.fmc.trade_date == dm1, "float_mktcap"] *= 1.5
    c2 = cmc_ctx(s2)
    assert not _eq(c0["MC"].loc[D], c2["MC"].loc[D])
    assert not _eq(c0["beta"].loc[D], c2["beta"].loc[D])


def test_s8_signal_exposures_t_minus_1_and_B_set_unchanged():
    c0 = s8_ctx(BASE)
    s1 = BASE.copy()
    for i in NAMES: s1.close[i].loc[D] *= 1.07
    s1.bench.loc[D] *= 1.03
    s1.fmc.loc[s1.fmc.trade_date == D, "float_mktcap"] *= 1.5
    c1 = s8_ctx(s1)
    for k in ("mc", "beta", "mom", "liq"):
        assert _eq(c0["X_sig"][k].loc[D], c1["X_sig"][k].loc[D]), f"X_sig[{k}] moved with day-d data"
    assert not _eq(c0["X"]["mc"].loc[D], c1["X"]["mc"].loc[D]), "B set X (r−1 anchoring, unchanged) should still use close d"
    s2 = BASE.copy(); dm1 = _shifted_session(D, 1)
    for i in NAMES: s2.close[i].loc[dm1] *= 1.07
    s2.fmc.loc[s2.fmc.trade_date == dm1, "float_mktcap"] *= 1.5
    c2 = s8_ctx(s2)
    assert not _eq(c0["X_sig"]["mc"].loc[D], c2["X_sig"]["mc"].loc[D])
    assert not _eq(c0["X_sig"]["beta"].loc[D], c2["X_sig"]["beta"].loc[D])
    s3 = BASE.copy(); dm21 = _shifted_session(D, 21)                  # mom_{t−1} = C(d−21)/C(d−121) − 1
    for i in NAMES: s3.close[i].loc[dm21] *= 1.07
    c3 = s8_ctx(s3)
    assert not _eq(c0["X_sig"]["mom"].loc[D], c3["X_sig"]["mom"].loc[D])
    m = BASE.close[NAMES[0]]
    assert np.isclose(c0["X_sig"]["mom"].loc[D, NAMES[0]], m.loc[dm21] / m.loc[_shifted_session(D, 121)] - 1)


# ======================= no pre-window float mcap; START day skipped (Arch 6ab489c8 P1-1, option b) =======================
def _fmc_lower_bounds(fmc_path):
    out = []
    for rp, flt in READS:
        if rp == Path(fmc_path).resolve():
            lb = [v for (col, op, v) in (flt or []) if col == "trade_date" and op in (">=", ">")]
            assert lb, f"float mcap read without a trade_date lower bound: {flt}"
            out.extend(pd.Timestamp(v) for v in lb)
    return out


def test_fmc_read_from_start_only_and_start_day_skipped():
    assert (BASE.fmc.trade_date < pd.Timestamp(START)).any(), "synthetic FMC must contain pre-window rows"
    READS.clear(); c0 = cmc_ctx(BASE); lbs = _fmc_lower_bounds(CMC.FMC)
    assert lbs and all(x >= pd.Timestamp(START) for x in lbs)
    assert c0["reads"]["fmc_earliest_trade_date"] == START and c0["reads"]["price_start"] == "2023-09-01"
    assert c0["MC"].loc[pd.Timestamp(START)].isna().all(), "START-day mc_{t−1} must be NaN"
    z = CMC.resid_z(pd.DataFrame(1.0, index=c0["ev"][:3], columns=c0["U"]).mul(np.arange(len(c0["U"])), axis=1))
    assert z.loc[pd.Timestamp(START)].isna().all() and z.iloc[1].notna().any(), "START day must be skipped, next day residualised"
    READS.clear(); s0 = s8_ctx(BASE); lbs = _fmc_lower_bounds(S8.FMC)
    assert lbs and all(x >= pd.Timestamp(START) for x in lbs)
    assert s0["reads"]["fmc_earliest_trade_date"] == START and s0["reads"]["price_start"] == "2023-06-01"
    assert s0["X_sig"]["mc"].loc[pd.Timestamp(START)].isna().all() and s0["X"]["mc"].loc[pd.Timestamp(START)].notna().any()
    s1 = BASE.copy()                                                  # perturb ONLY pre-window float mcap → nothing may change
    s1.fmc.loc[s1.fmc.trade_date < pd.Timestamp(START), "float_mktcap"] *= 3.0
    c1, s1c = cmc_ctx(s1), s8_ctx(s1)
    assert _eq(c0["MC"], c1["MC"])
    for k in ("mc",):
        assert _eq(s0["X_sig"][k], s1c["X_sig"][k]) and _eq(s0["X"][k], s1c["X"][k])
    with pytest.raises(RuntimeError, match="before START"):
        CMC.check_fmc_lower_bound(pd.Series(pd.to_datetime(["2024-05-31", "2024-06-03"])))


# ======================= F truncated at END =======================
def test_forward_return_last_H_nan():
    for c in (cmc_ctx(BASE), s8_ctx(BASE)):
        F = c["F"]
        assert F.index.max() <= pd.Timestamp(END)
        assert F.iloc[-H:].isna().all().all(), "F must be NaN for the last H sessions"
        assert F.iloc[-H - 1].notna().any(), "F should have values H+1 sessions before END"


# ======================= SW L1 first month (P2-3 fix) =======================
def test_sw_single_pre_window_snapshot_and_no_all_unk_day():
    for c in (cmc_ctx(BASE), s8_ctx(BASE)):
        assert c["sw_snapshots"][0] == "2024-05-31" and c["sw_snapshots"][1] > "2024-06-02"
        assert sum(x < START for x in c["sw_snapshots"]) == 1, "only ONE snapshot date before START"
        cov = c["ind_coverage"]
        assert cov["n_all_unk_days"] == 0 and cov["min_coverage"] > 0 and cov["first_day"] == START
        IND = c["IND"]
        for d in IND.index:                                           # no window day fully '_UNK'
            assert IND.loc[d].notna().any(), f"all-_UNK day {d.date()}"
        assert IND.loc[pd.Timestamp(START)].notna().all()


def test_sw_snapshot_guards():
    ev = CAL[(CAL >= START) & (CAL <= END)]
    me = CMC.sw_snapshot_dates(CAL[CAL <= END], ev)
    assert list(me[me < pd.Timestamp(START)]) == [pd.Timestamp("2024-05-31")]
    with pytest.raises(RuntimeError):                                 # calendar whose last pre-window session is not 2024-05-31
        CMC.sw_snapshot_dates(CAL[(CAL <= END) & (CAL != pd.Timestamp("2024-05-31"))], ev)
    s = BASE.copy(); s.sw["in_date"] = pd.Timestamp("2024-06-10")    # nobody classified on 2024-05-31 → June 3..27 all '_UNK'
    with pytest.raises(RuntimeError, match="all-_UNK"):
        cmc_ctx(s)
    with pytest.raises(RuntimeError, match="all-_UNK"):
        s8_ctx(s)


# ======================= output overwrite refusal =======================
def test_out_file_and_out_dir_refuse_overwrite():
    f = OUT_DIR / "exists.json"; f.write_text("{}")
    with pytest.raises(SystemExit):
        RG.precheck_out_file(f)
    assert RG.precheck_out_file(OUT_DIR / "new.json") == (OUT_DIR / "new.json").resolve()
    d = OUT_DIR / "nonempty"; d.mkdir(); (d / "x").write_text("x")
    with pytest.raises(SystemExit):
        RG.precheck_out_dir(d)
    e = OUT_DIR / "empty"; e.mkdir()
    assert RG.precheck_out_dir(e) == e.resolve()
    with open(f, "a"):
        pass
    with pytest.raises(FileExistsError):                              # writers use exclusive create
        open(f, "x")


# ======================= legacy comparison column =======================
def _new_result():
    return dict(universe="hiliq", leaf_file="/x/g1g5_leafA_daily_weights_20261018.parquet", d_ic=0.004, d_icir_full=0.06,
                d_icir_roll252_median=0.05, rho_leaf_resid_vs_B0=0.2,
                tiers={"60w": dict(d_cagr_net=0.01, report_to_leo_eligible=True, base="capadv_hiliq_book_smoke"),
                       "100w": dict(d_cagr_net=0.008, report_to_leo_eligible=True, base="capadv_hiliq_book_smoke")})


def _legacy(tag, **over):
    L = _new_result(); L.pop("tiers"); L["tiers"] = {t: dict(d_cagr_net=0.009, report_to_leo_eligible=True, base="capadv_hiliq_book_smoke")
                                                    for t in ("60w", "100w")}
    L["d_ic"] = 0.003; L.update(over)
    p = OUT_DIR / f"legacy_{tag}.json"; p.write_text(json.dumps(L)); return p, hashlib.sha256(p.read_bytes()).hexdigest()


def test_legacy_column_accepts_matching_and_rejects_bad():
    p, h = _legacy("ok")
    col = CMC.legacy_column(str(p), _new_result(), h)
    assert col["role"].startswith("disclosure_only") and col["legacy_json_sha256"] == h
    assert np.isclose(col["diff_v1_1_minus_legacy"]["d_ic"], 0.001)
    p, h = _legacy("v11", tool_version="v1.1")
    with pytest.raises(SystemExit, match="v1.1 output"):
        CMC.legacy_column(str(p), _new_result(), h)
    p, h = _legacy("uni", universe="fulla")
    with pytest.raises(SystemExit, match="universe"):
        CMC.legacy_column(str(p), _new_result(), h)
    p, h = _legacy("base", tiers={"60w": dict(base="b4_diag"), "100w": dict(base="b4_diag")})
    with pytest.raises(SystemExit, match="base"):
        CMC.legacy_column(str(p), _new_result(), h)
    p, h = _legacy("leaf", leaf_file="/x/g1g5_other_daily_weights_20261018.parquet")
    with pytest.raises(SystemExit, match="leaf_file"):
        CMC.legacy_column(str(p), _new_result(), h)
    p, h = _legacy("sha")
    with pytest.raises(SystemExit, match="gate-pinned"):
        CMC.legacy_column(str(p), _new_result(), "0" * 64)


# ======================= watchdog / RLIMIT (forked child) =======================
def _fork_exit(fn) -> int:
    pid = os.fork()
    if pid == 0:
        try:
            os._exit(fn() or 0)
        except BaseException:
            os._exit(99)
    _, st = os.waitpid(pid, 0)
    return os.WEXITSTATUS(st) if os.WIFEXITED(st) else -1


def test_watchdog_triggers_in_subprocess():
    def child():
        RG.start_watchdog(limit_kb=1, poll_s=0.05)
        time.sleep(10); return 0
    assert _fork_exit(child) == 3


def test_rlimit_as_backstop_in_subprocess():
    def child():
        vm = next(int(x.split()[1]) for x in open("/proc/self/status") if x.startswith("VmSize:"))
        RG.set_rlimit_as(vm + 64 * 1024)
        try:
            b = bytearray(1024 * 1024 * 1024); b[-1] = 1
        except MemoryError:
            return 7
        return 0
    assert _fork_exit(child) == 7


def test_rlimit_env_override_validated_and_vmpeak(monkeypatch):
    monkeypatch.delenv(RG.RLIMIT_ENV, raising=False)
    assert RG.rlimit_as_kb() == RG.RLIMIT_AS_KB_DEFAULT
    for bad in ("0", "-1", "abc", str(RG.RSS_LIMIT_KB)):
        monkeypatch.setenv(RG.RLIMIT_ENV, bad)
        with pytest.raises(SystemExit):
            RG.rlimit_as_kb()
    monkeypatch.setenv(RG.RLIMIT_ENV, "8388608")
    assert RG.rlimit_as_kb() == 8388608 and RG.env_snapshot()[RG.RLIMIT_ENV] == "8388608"
    v = RG.vm_peak_kb()
    assert v is None or v > 0


# ======================= CLI: --arch-ok mandatory =======================
def test_missing_arch_ok_rejected(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["alpha_combo_marginal_v1_1.py", "some_leaf"])
    with pytest.raises(SystemExit):
        CMC._cli()
    monkeypatch.setattr(sys, "argv", ["alpha_hiliq_s8_paradigm_v1_1.py", "--leaf", "a=x.parquet"])
    with pytest.raises(SystemExit):
        S8._cli()


# ======================= run-guard .ok self-check (full mode) =======================
def _full_ok(tag, **over):
    now = _dt.datetime.now().astimezone().replace(microsecond=0)
    kv = dict(format="quantlab_run_auth_v1", signed_by="arch", signed_et=(now - _dt.timedelta(minutes=1)).isoformat(), scope="full",
              allow_selftest="false", allow_real_data="true", allow_dryrun="false", allow_full="true", allow_execute="false",
              allow_smoke="false", allow_diagnostic="false", allow_disclosure_only="false", live="false", promotion="false",
              expires_et=(now + _dt.timedelta(hours=1)).isoformat())
    kv.update(over); kv = {k: v for k, v in kv.items() if v is not None}
    p = OUT_DIR / f"full_{tag}.ok"; p.write_bytes("".join(f"{k}={v}\n" for k, v in kv.items()).encode()); return p


def test_ok_selfcheck_full_mode():
    g = lambda p: {"pins": {str(p): "x"}}
    p = _full_ok("good"); assert str(p) in RG.ok_selfcheck([p], g(p), "full")
    past = (_dt.datetime.now().astimezone() - _dt.timedelta(minutes=1)).replace(microsecond=0).isoformat()
    bad = [_full_ok("expired", expires_et=past), _full_ok("naive", expires_et="2099-01-01T00:00:00"), _full_ok("scope", scope="selftest"),
           _full_ok("missing_allow", allow_smoke=None), _full_ok("extra_true", allow_smoke="true"), _full_ok("inline", allow_full="true#x")]
    b = OUT_DIR / "full_bom.ok"; b.write_bytes(b"\xef\xbb\xbf" + _full_ok("b0").read_bytes()); bad.append(b)
    c = OUT_DIR / "full_crlf.ok"; c.write_bytes(_full_ok("c0").read_bytes().replace(b"\n", b"\r\n")); bad.append(c)
    d = OUT_DIR / "full_dup.ok"; d.write_bytes(_full_ok("d0").read_bytes() + b"live=false\n"); bad.append(d)
    for p in bad:
        with pytest.raises(SystemExit):
            RG.ok_selfcheck([p], g(p), "full")


# ======================= nothing outside the pinned set was loaded =======================
def test_only_pinned_project_modules_loaded():
    allowed = {v for v in TEST_DEPS.values()} | {str(Path(__file__).resolve().relative_to(ROOT))}
    loaded = set()
    for m in list(sys.modules.values()):
        f = getattr(m, "__file__", None)
        if not f: continue
        try: loaded.add(str(Path(f).resolve().relative_to(ROOT)))
        except ValueError: pass
    assert loaded <= allowed, sorted(loaded - allowed)
