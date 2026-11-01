"""Alpha CMC v1.2 ≡ v1.1 equivalence selftest (Arch→Alpha 2026-10-18 v1.2 spec: memory-only, numerics unchanged). SYNTHETIC DATA ONLY:
pandas.read_parquet is wrapped and refuses any path outside the mkdtemp out_dir; ADG.bench / ADG._close (cache-through, like the real one) and
leaf_selfcheck_common._ret (book nav) are monkeypatched; the SW member table / to_panel_id come from in-memory stub modules
(research.g1g5_nontextbook_weights / research.g1g5_x2_panel_stitch / research.hiliq_v1_universe are NOT imported). The v1.1 selftest file
(tests/test_alpha_v1_1_selftest.py, 6966a5d9) is not modified.

GATE (module top level, at collection time, BEFORE any module under test is imported):
  ok_runner_pin.enforce(__file__, [output/alpha/ARCH_RUN_AUTH_SELFTEST_CMC_V1_2.ok], modes=["selftest"], deps=TEST_DEPS), then
  research/alpha_v1_1_runguard.ok_selfcheck(mode="selftest") (scope=selftest, every known allow_* explicit, only allow_selftest true,
  allow_real_data=false, out_dir = mkdtemp or /tmp/<tag>, not expired). The .ok must pin runner_sha256_test_alpha_v1_2_equiv_selftest and
  dep_sha256_<key> for every TEST_DEPS key. A refusal raises SystemExit (aborts collection); no skip path. Neither script's __main__ gate runs.

Run ALONE (own process; do not collect together with tests/test_alpha_v1_1_selftest.py: both install the same stub modules and each has its
own .ok), serial, nothing else concurrently, RSS ≤ 1.5 GB:
  PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python -m pytest tests/test_alpha_v1_2_equiv_selftest.py -q -p no:cacheprovider

EQUIVALENCE RULE. v1.1 (research/alpha_combo_marginal_v1_1.py) and v1.2 run cmc() on the SAME synthetic files. The output dicts are compared
after removing METADATA_KEYS (tool_version — asserted "v1.1"/"v1.2" separately —, definition_notes = __doc__, and the __main__-only receipt
fields peak_rss_kb, vm_peak_kb, gate, ok_selfcheck, closure, watchdog, env, memory_refactor_of; the last group is not produced by cmc() and is
listed for completeness). Floats are compared bit-for-bit (struct '<d'); NaN == NaN (JSON cannot carry a NaN payload; both serialise "NaN");
types must match exactly (int vs float, bool vs int differ). Final criterion: json.dumps(..., ensure_ascii=False, indent=2, default=str), i.e.
the exact __main__ serialisation, is byte-identical.
±0 HANDLING (explicit). -0.0 and +0.0 compare equal as numbers but serialise differently ("-0.0" vs "0.0"). Value differences and sign-of-zero
differences are collected separately: test_*_values_equal fails only on real value differences (±0 treated as equal there), and
test_*_signed_zero fails if any value differs ONLY in the sign of zero, listing every path — so a pure ±0 effect is visible on its own and
Arch can rule on it. Both must pass for "bit-identical". The synthetic leg file contains explicit -0.0 (and NaN) target_weight rows: v1.2
filters them at read (-0.0 != 0 is False in IEEE), v1.1 sums them in pivot_table (pandas group sum starts at +0.0, so +0.0 + -0.0 = +0.0); the
cell is +0.0 in both after fillna(0.0) — checked bitwise by test_ctx_sig_signed_zero.
Writes only under the mkdtemp out_dir (removed at exit). live=false; promotion=false.
"""
from __future__ import annotations

import atexit
import contextlib
import hashlib
import io
import json
import math
import re
import shutil
import struct
import sys
import tempfile
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST_OK = ROOT / "output/alpha/ARCH_RUN_AUTH_SELFTEST_CMC_V1_2.ok"
TEST_DEPS = {
    "combo_v1_1": "research/alpha_combo_marginal_v1_1.py",
    "combo_v1_2": "research/alpha_combo_marginal_v1_2.py",
    "ok_runner_pin": "scripts_eng/ok_runner_pin.py",
    "runguard": "research/alpha_v1_1_runguard.py",
    "adg": "research/alpha_decay_gate.py",
    "selfcheck_v3": "research/leaf_selfcheck_v3.py",
    "selfcheck_common": "research/leaf_selfcheck_common.py",
    "manifest_v1_1": "docs/v2/ALPHA_V1_1_IMPORT_CLOSURE.manifest",
    "manifest_v1_2": "docs/v2/ALPHA_V1_2_IMPORT_CLOSURE.manifest",
}
TEST_MODULES = {v for v in TEST_DEPS.values() if v.endswith(".py")}

if not sys.flags.dont_write_bytecode:          # checked BEFORE the gate module is imported (no __pycache__ in the repo)
    raise SystemExit("REFUSED (test_alpha_v1_2_equiv): run with PYTHONDONTWRITEBYTECODE=1")
sys.path.insert(0, str(ROOT / "scripts_eng"))
import ok_runner_pin as _PIN  # noqa: E402
_GATE = _PIN.enforce(__file__, [TEST_OK], modes=["selftest"], deps={k: ROOT / v for k, v in TEST_DEPS.items()})
sys.path.insert(0, str(ROOT))
import research.alpha_v1_1_runguard as RG  # noqa: E402  (pinned just above; stdlib only)
_OKREC = RG.ok_selfcheck([TEST_OK], _GATE, "selftest")
OUT_DIR = Path(tempfile.mkdtemp(prefix="alpha_v12_equiv_")).resolve()
if OUT_DIR == ROOT or ROOT in OUT_DIR.parents or "output" in OUT_DIR.parts:
    raise SystemExit(f"REFUSED (test_alpha_v1_2_equiv): out_dir {OUT_DIR} inside the repo / output/")
atexit.register(shutil.rmtree, str(OUT_DIR), True)

# ---- gate passed: only now import numpy/pandas/pytest and the modules under test
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import pytest  # noqa: E402

_REAL_READ_PARQUET = pd.read_parquet
READS: list = []                                            # (resolved path, filters) of every parquet read


def _guarded_read_parquet(path, *a, **k):
    rp = Path(path).resolve()
    if OUT_DIR not in rp.parents:
        raise AssertionError(f"real-data read attempted in synthetic selftest: {path}")
    READS.append((rp, k.get("filters")))
    return _REAL_READ_PARQUET(path, *a, **k)


pd.read_parquet = _guarded_read_parquet


# ---- in-memory stubs (same semantics as the real helpers; no data files) — identical to tests/test_alpha_v1_1_selftest.py
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
import research.leaf_selfcheck_v3 as V3  # noqa: E402
import research.alpha_combo_marginal_v1_1 as CMC1  # noqa: E402
_IMPORT_ERR = io.StringIO()
with contextlib.redirect_stderr(_IMPORT_ERR):                # captures v1.2's 'STAGE imports' line
    import research.alpha_combo_marginal_v1_2 as CMC2  # noqa: E402
LC = V3.LC

START, END, H = CMC2.START, CMC2.END, CMC2.H
assert (CMC1.START, CMC1.END, CMC1.H) == (START, END, H)
CAL = pd.bdate_range("2023-06-01", "2026-11-30")          # 2024-05-31 (Fri) is the last session before START 2024-06-03 (Mon)
WIN = CAL[(CAL >= START) & (CAL <= END)]
SAT = pd.Timestamp("2025-03-08")                            # Saturday in the window: a mask row that is not a session (never looked up)
NAMES = [f"{600000 + k}.SH" for k in range(40)] + [f"{1 + k:06d}.SZ" for k in range(40)]
BAL = "510300.SH"
METADATA_KEYS = ("tool_version", "definition_notes", "peak_rss_kb", "vm_peak_kb", "gate", "ok_selfcheck", "closure", "watchdog", "env",
                 "memory_refactor_of")
STAGES_IN_ORDER = ["mk/mem", "_factors", "P", "beta", "FMC", "IND", "sig:capacity_adv", "sig:earnings_event", "sig:insider_increase", "b0",
                   "sig:leaf", "sig:leaf_style", "tiers:60w", "tiers:100w"]


class Synth:
    """Exercises: union-index alignment (late listings, missing rows), NaN closes, mask rows with in_universe False and on a non-session,
    changing membership, unclassified names + one SW reclassification, a full-grid leg with 0.0 / -0.0 / NaN weights, sparse legs with
    explicit zero rows, (x, 0.0) and (x, y) duplicate keys, days without any row, three date encodings (timestamp, YYYY-MM-DD, YYYYMMDD)."""

    def __init__(self, seed=11):
        rng = np.random.default_rng(seed)
        self.bench = pd.Series(100 * np.exp(np.cumsum(rng.normal(0, .01, len(CAL)))), index=CAL)
        self.close = {}
        for k, i in enumerate(NAMES):
            s = pd.Series(10 * np.exp(np.cumsum(rng.normal(0, .02, len(CAL)))), index=CAL)
            if k < 2: s = s[s.index >= pd.Timestamp("2024-09-02")].copy()          # late listing → shorter index
            elif k < 6: s[rng.random(len(s)) < .03] = np.nan                       # suspensions → NaN closes
            elif k == 6: s = s.drop(s.index[rng.random(len(s)) < .02])              # absent rows
            self.close[i] = s
        late = pd.Timestamp("2024-09-16"); rows = []
        for d in WIN:
            u = rng.random(len(NAMES)) < .85
            rows += [(d, i, bool(u[k] and (k >= 2 or d >= late))) for k, i in enumerate(NAMES)]
        rows += [(SAT, i, True) for i in NAMES]
        self.mask = pd.DataFrame(rows, columns=["date", "instrument", "in_universe"])
        self.mask["adv20_yuan"] = rng.uniform(5e7, 5e8, len(self.mask))
        self.fmc = pd.DataFrame([(_to_panel_id(i), d, float(v)) for i in NAMES
                                 for d, v in zip(CAL, 1e9 * np.exp(np.cumsum(rng.normal(0, .01, len(CAL)))))],
                                columns=["instrument_id", "trade_date", "float_mktcap"])
        sw = [(_to_panel_id(i), pd.Timestamp("2020-01-01"), pd.NaT, f"80{k % 5}") for k, i in enumerate(NAMES) if k not in (10, 70, 71, 72)]
        sw += [(_to_panel_id(NAMES[10]), pd.Timestamp("2020-01-01"), pd.Timestamp("2025-06-30"), "801"),
               (_to_panel_id(NAMES[10]), pd.Timestamp("2025-06-30"), pd.NaT, "809")]
        self.sw = pd.DataFrame(sw, columns=["instrument_id", "in_date", "out_date", "sw_code"])
        # legs
        rows = []
        for d in WIN:
            top = set(np.argsort(-rng.random(len(NAMES)))[:10])
            rows += [(d, i, 0.1 if k in top else 0.0) for k, i in enumerate(NAMES)]
        cap = pd.DataFrame(rows, columns=["date", "instrument", "target_weight"])
        z = np.flatnonzero(cap.target_weight.to_numpy() == 0.0)
        cap.loc[rng.choice(z, 300, replace=False), "target_weight"] = -0.0
        cap.loc[rng.choice(z, 60, replace=False), "target_weight"] = np.nan
        ee = []
        for d in WIN:
            ds = d.strftime("%Y-%m-%d"); ks = rng.choice(len(NAMES), 7, replace=False)
            ee += [(ds, NAMES[k], float(rng.uniform(.05, .3))) for k in ks[:5]]
            ee.append((ds, NAMES[ks[5]], 0.0))                                      # explicit zero row
            if rng.random() < .15: ee.append((ds, NAMES[ks[0]], 0.0))              # duplicate key (x, 0.0)
            if rng.random() < .05: ee.append((ds, NAMES[ks[1]], float(rng.uniform(.01, .05))))   # duplicate key (x, y), no zero
        ins = []
        for d in WIN:
            if rng.random() < .4: continue                                          # day without any row
            ds = d.strftime("%Y%m%d"); ks = rng.choice(len(NAMES), 5, replace=False)
            ins += [(ds, NAMES[k], float(rng.uniform(.1, .3))) for k in ks[:4]] + [(ds, NAMES[ks[4]], 0.0)]
        leaf = []
        for d in WIN:
            ds = d.strftime("%Y-%m-%d"); ks = rng.choice(len(NAMES), 11, replace=False)
            leaf += [(ds, NAMES[k], float(rng.uniform(.05, .2))) for k in ks[:8]] + [(ds, NAMES[k], 0.0) for k in ks[8:]]
            if rng.random() < .2: leaf.append((ds, BAL, 0.05))
        self.legs = {"capacity_adv": cap, "earnings_event": pd.DataFrame(ee, columns=cap.columns),
                     "insider_increase": pd.DataFrame(ins, columns=cap.columns)}
        self.leaf = pd.DataFrame(leaf, columns=cap.columns)
        self.books = {}
        for tier, n in (("60w", 6), ("100w", 10)):
            bk = []
            for d in WIN:
                ds = d.strftime("%Y-%m-%d"); ks = rng.choice(len(NAMES), n, replace=False)
                bk += [(ds, NAMES[k], .95 / n) for k in ks] + [(ds, BAL, .05)]
            self.books[tier] = pd.DataFrame(bk, columns=cap.columns)

    def px(self, i):
        return self.bench if i == ADG.B else self.close[i]


def _write(s: Synth, tag: str) -> dict:
    d = OUT_DIR / tag; d.mkdir()
    p = dict(mask=d / "mask.parquet", fmc=d / "fmc.parquet", leaf=d / "g1g5_synthleaf_daily_weights_20261018.parquet",
             legs={k: d / f"leg_{k}.parquet" for k in s.legs}, books={t: d / f"book_{t}.parquet" for t in s.books})
    s.mask.to_parquet(p["mask"]); s.fmc.to_parquet(p["fmc"]); s.leaf.to_parquet(p["leaf"])
    for k, df in s.legs.items(): df.to_parquet(p["legs"][k])
    for t, df in s.books.items(): df.to_parquet(p["books"][t])
    return p


def _make_ret(s: Synth):
    def _ret(W: pd.DataFrame, net: bool = True) -> pd.Series:                      # synthetic stand-in for LC._ret (same for both tools)
        P = W.pivot_table(index="date", columns="instrument", values="target_weight", aggfunc="sum").fillna(0).sort_index()
        P.index = pd.to_datetime(P.index)
        C = pd.DataFrame({i: s.px(i) for i in P.columns}).reindex(P.index)
        cc = C.pct_change(fill_method=None).fillna(0.0); Hh = P.shift(1).fillna(0)
        r = (Hh * cc).sum(axis=1)
        if net: r = r - ADG.COST * Hh.diff().abs().sum(axis=1).fillna(Hh.abs().sum(axis=1))
        return r
    return _ret


def _install(s: Synth, p: dict, mod):
    ADG._cache.clear()
    ADG.bench = lambda: s.bench

    def _close(i):                                                                 # cache-through, like the real ADG._close
        if i == ADG.B: return s.bench
        if i not in ADG._cache: ADG._cache[i] = s.close[i].copy()
        return ADG._cache[i]
    ADG._close = _close
    LC._ret = _make_ret(s)
    SW["df"] = s.sw
    mod.UNIVERSE_MASKS["hiliq"] = p["mask"]; mod.FMC = p["fmc"]
    mod.LEGS_BY_UNIVERSE["hiliq"] = dict(p["legs"])
    mod.CAPADV_BOOK_TRACKS["60w"] = p["books"]["60w"]; mod.CAPADV_BOOK_TRACKS["100w"] = p["books"]["100w"]
    mod.UNIVERSE = "hiliq"; mod.BASE = "capadv"
    mod._CTX.clear(); mod._B0.clear()


# ---- comparison helpers
def _fbits(x: float) -> bytes:
    return struct.pack("<d", x)


def _walk(a, b, path="$", diffs=None, zsign=None):
    """Collect real differences (diffs) and sign-of-zero-only differences (zsign) between two JSON-like objects."""
    diffs = [] if diffs is None else diffs; zsign = [] if zsign is None else zsign
    if type(a) is not type(b):
        diffs.append((path, f"type {type(a).__name__} != {type(b).__name__}", a, b))
    elif isinstance(a, dict):
        if list(a) != list(b): diffs.append((path, "keys/order", list(a), list(b)))
        for k in a:
            if k in b: _walk(a[k], b[k], f"{path}.{k}", diffs, zsign)
    elif isinstance(a, (list, tuple)):
        if len(a) != len(b): diffs.append((path, "len", len(a), len(b)))
        for n, (x, y) in enumerate(zip(a, b)): _walk(x, y, f"{path}[{n}]", diffs, zsign)
    elif isinstance(a, float):
        if math.isnan(a) and math.isnan(b): pass
        elif _fbits(a) == _fbits(b): pass
        elif a == b: zsign.append((path, a, b))                                    # 0.0 vs -0.0
        else: diffs.append((path, "value", a, b))
    elif a != b:
        diffs.append((path, "value", a, b))
    return diffs, zsign


def _strip(o: dict) -> dict:
    return {k: v for k, v in o.items() if k not in METADATA_KEYS}


def _dump(o) -> str:
    return json.dumps(o, ensure_ascii=False, indent=2, default=str)               # == __main__ serialisation


def _cmp_frame(a: pd.DataFrame, b: pd.DataFrame) -> tuple[list, int]:
    """(structural/value problems, number of cells equal in value but differing only in the sign of zero)."""
    prob = []
    if not a.index.equals(b.index): prob.append("index")
    if list(a.columns) != list(b.columns): prob.append("columns")
    if list(map(str, a.dtypes.unique())) != list(map(str, b.dtypes.unique())): prob.append(f"dtypes {a.dtypes.unique()} != {b.dtypes.unique()}")
    if prob: return prob, 0
    x, y = a.to_numpy(dtype=np.float64), b.to_numpy(dtype=np.float64)
    nx, ny = np.isnan(x), np.isnan(y); both = ~nx & ~ny
    nval = int((nx != ny).sum() + (both & (x != y)).sum())
    if nval: prob.append(f"{nval} cells differ in value")
    return prob, int((both & (x == y) & (np.signbit(x) != np.signbit(y))).sum())


def _stage_names(txt: str) -> list:
    out = []
    for line in txt.splitlines():
        m = re.fullmatch(r"STAGE (\S+) ru_maxrss=(\d+)( .*)?", line)
        if m: out.append(m.group(1))
    return out


@pytest.fixture(scope="module")
def RUN():
    s = Synth(); res = {"synth": s}
    for tag, mod in (("v1_1", CMC1), ("v1_2", CMC2)):
        p = _write(s, tag)                                                         # same bytes, separate dir per tool (READS attribution)
        _install(s, p, mod); READS.clear(); buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            c = mod.ctx(); cache_after_ctx = set(ADG._cache)
            out = mod.cmc(str(p["leaf"]))
            sigs = {k: mod.sig(q) for k, q in list(p["legs"].items()) + [("leaf", p["leaf"])]}
        res[tag] = dict(mod=mod, paths=p, ctx=dict(c), cache_after_ctx=cache_after_ctx, out=out, sigs=sigs, stderr=buf.getvalue(), reads=list(READS))
    return res


# ======================= output JSON =======================
def test_tool_versions(RUN):
    assert RUN["v1_1"]["out"]["tool_version"] == "v1.1" and RUN["v1_2"]["out"]["tool_version"] == "v1.2"
    assert CMC2.TOOL_VERSION == "v1.2" and CMC1.TOOL_VERSION == "v1.1"


def test_output_json_values_equal(RUN):
    o1, o2 = _strip(RUN["v1_1"]["out"]), _strip(RUN["v1_2"]["out"])
    diffs, _ = _walk(o1, o2)
    assert not diffs, diffs[:20]
    assert o1["tiers"] and o1["B0_ic"]["n"] > 252 and o1["B1_ic"]["icir_roll252_median"] is not None, "synthetic run must reach every branch"


def test_output_json_signed_zero_and_bytes(RUN):
    o1, o2 = _strip(RUN["v1_1"]["out"]), _strip(RUN["v1_2"]["out"])
    _, zsign = _walk(o1, o2)
    assert not zsign, f"values equal but sign of zero differs (reported separately per spec): {zsign}"
    assert _dump(o1) == _dump(o2), "serialised output JSON (metadata removed) not byte-identical"


# ======================= intermediates (ctx, sig) =======================
CTX_FRAMES = ("R", "beta", "MC", "F")


def test_ctx_sig_values_equal(RUN):
    c1, c2 = RUN["v1_1"]["ctx"], RUN["v1_2"]["ctx"]
    for k in CTX_FRAMES:
        prob, _ = _cmp_frame(c1[k], c2[k]); assert not prob, (k, prob)
    assert c1["IND"].equals(c2["IND"]) and list(c1["IND"].columns) == list(c2["IND"].columns)
    for k in ("U", "ind_coverage", "sw_snapshots", "universe"):
        assert c1[k] == c2[k], k
    assert c1["ev"].equals(c2["ev"])
    r1, r2 = dict(c1["reads"]), dict(c2["reads"]); assert r1 == r2
    for k in RUN["v1_1"]["sigs"]:
        prob, _ = _cmp_frame(RUN["v1_1"]["sigs"][k], RUN["v1_2"]["sigs"][k]); assert not prob, (k, prob)


def test_ctx_sig_signed_zero(RUN):
    c1, c2 = RUN["v1_1"]["ctx"], RUN["v1_2"]["ctx"]; rep = {}
    for k in CTX_FRAMES:
        rep[k] = _cmp_frame(c1[k], c2[k])[1]
    for k in RUN["v1_1"]["sigs"]:
        rep[f"sig:{k}"] = _cmp_frame(RUN["v1_1"]["sigs"][k], RUN["v1_2"]["sigs"][k])[1]
    assert not any(rep.values()), f"cells equal in value but with opposite zero sign (reported separately per spec): {rep}"
    neg = int(np.signbit(RUN["v1_2"]["sigs"]["capacity_adv"].to_numpy()).sum())
    assert neg == 0, "fillna(0.0)/pivot sum must leave no -0.0 cell"


# ======================= M3: pools =======================
def test_pools_identical_and_non_session_mask_row_ignored(RUN):
    c1, c2 = RUN["v1_1"]["ctx"], RUN["v1_2"]["ctx"]
    assert "mem" in c1 and "mem" not in c2 and c2["mem_mask"].dtype == bool and c2["mem_mask"].shape == (len(c2["ev"]), len(c2["U"]))
    n_diff_days = 0
    for d in c1["ev"]:
        p1 = [i for i in c1["U"] if i in c1["mem"].get(d.strftime("%Y-%m-%d"), set())]
        p2 = CMC2._pool(c2, d)
        assert p1 == p2, d
        n_diff_days += len(p1) != len(c1["U"])
    assert n_diff_days > 0, "membership must vary across days"
    assert SAT.strftime("%Y-%m-%d") in c1["mem"] and SAT not in c2["ev"] and SAT.strftime("%Y-%m-%d") not in c2["ev_pos"]


# ======================= M1: P / ADG._cache =======================
def test_adg_cache_popped_only_in_v1_2(RUN):
    U = set(RUN["v1_1"]["ctx"]["U"])
    assert U <= RUN["v1_1"]["cache_after_ctx"], "v1.1 keeps every close in ADG._cache"
    assert not (U & RUN["v1_2"]["cache_after_ctx"]), "v1.2 must pop every close from ADG._cache after building P"


def test_p_preconditions_refuse_dup_index_and_non_float(RUN):
    s = RUN["synth"]; c = s.close[NAMES[8]]
    s.close[NAMES[8]] = pd.concat([c, c.iloc[:1]])                                  # duplicate index label
    try:
        p = _write(s, "dup_v12"); _install(s, p, CMC2)
        with contextlib.redirect_stderr(io.StringIO()), pytest.raises(RuntimeError, match="not unique"):
            CMC2.ctx()
        p = _write(s, "dup_v11"); _install(s, p, CMC1)
        with pytest.raises(Exception):                                             # v1.1 cannot align it either
            CMC1.ctx()
        s.close[NAMES[8]] = (c * 100).round().astype(np.int64)
        p = _write(s, "int_v12"); _install(s, p, CMC2)
        with contextlib.redirect_stderr(io.StringIO()), pytest.raises(RuntimeError, match="float64"):
            CMC2.ctx()
    finally:
        s.close[NAMES[8]] = c
        CMC1._CTX.clear(); CMC2._CTX.clear()


# ======================= M2: zero filter at read =======================
def test_sig_reads_filter_zero_rows_only_in_v1_2(RUN):
    for tag, want in (("v1_1", None), ("v1_2", [("target_weight", "!=", 0.0)])):
        p = RUN[tag]["paths"]; legs = {Path(q).resolve() for q in p["legs"].values()}
        flts = [f for rp, f in RUN[tag]["reads"] if rp in legs]
        assert len(flts) == 6 and all(f == want for f in flts), (tag, flts)          # b0 (3) + fixture re-read (3)
        lf = [f for rp, f in RUN[tag]["reads"] if rp == Path(p["leaf"]).resolve()]   # sig x2 in cmc + fixture sig + LC._w (unchanged, no filter)
        assert len(lf) == 4 and sum(f == want for f in lf) == (4 if want is None else 3) and lf.count(None) == (4 if want is None else 1), (tag, lf)
    cap = RUN["synth"].legs["capacity_adv"].target_weight
    assert (cap == 0).sum() > 0 and np.signbit(cap[cap == 0]).any() and cap.isna().any(), "fixture must contain 0.0, -0.0 and NaN weights"


# ======================= M5: STAGE lines =======================
def test_stage_lines(RUN):
    imp = _stage_names(_IMPORT_ERR.getvalue()); assert imp == ["imports"], imp
    got = _stage_names(RUN["v1_2"]["stderr"])
    it = iter(got)
    assert all(n in it for n in STAGES_IN_ORDER), f"STAGE order {got}"
    assert not _stage_names(RUN["v1_1"]["stderr"])
    m = re.search(r"STAGE sig:earnings_event ru_maxrss=\d+ rows_nonzero=(\d+) dup_keys_nonzero=(\d+)", RUN["v1_2"]["stderr"])
    assert m and int(m.group(2)) > 0, "the (x, y) duplicate keys must be reported"


# ======================= legacy column =======================
def test_legacy_column_equal_and_refuses_v1x_outputs(RUN):
    new = _strip(RUN["v1_2"]["out"])
    L = dict(universe="hiliq", leaf_file="/x/" + Path(new["leaf_file"]).name, d_ic=0.001, d_icir_full=0.01, d_icir_roll252_median=0.02,
             rho_leaf_resid_vs_B0=0.1, tiers={t: dict(d_cagr_net=0.0, report_to_leo_eligible=False, base=v["base"]) for t, v in new["tiers"].items()})
    q = OUT_DIR / "legacy_ok.json"; q.write_text(json.dumps(L)); h = hashlib.sha256(q.read_bytes()).hexdigest()
    assert _dump(CMC1.legacy_column(str(q), new, h)) == _dump(CMC2.legacy_column(str(q), new, h))
    for tv in ("v1.1", "v1.2"):
        q = OUT_DIR / f"legacy_{tv}.json"; q.write_text(json.dumps(dict(L, tool_version=tv))); h = hashlib.sha256(q.read_bytes()).hexdigest()
        with pytest.raises(SystemExit, match="not a legacy one"):
            CMC2.legacy_column(str(q), new, h)


# ======================= manifest / runner key / CLI =======================
def test_manifest_v1_2_is_v1_1_plus_one_line():
    m1p, m2p = ROOT / TEST_DEPS["manifest_v1_1"], ROOT / TEST_DEPS["manifest_v1_2"]
    m1, m2 = RG.load_manifest(m1p), RG.load_manifest(m2p)
    me = "research/alpha_combo_marginal_v1_2.py"
    assert m2 == {**m1, me: RG.sha256_file(ROOT / me)}
    l1, l2 = m1p.read_text(encoding="utf-8").split("\n"), m2p.read_text(encoding="utf-8").split("\n")
    extra = [x for x in l2 if x not in l1]; assert len(l2) == len(l1) + 1 and len(extra) == 1 and extra[0].endswith("  " + me)
    assert RG.verify_manifest_shas(m2p, "selftest")["all_sha_match"]
    assert Path(CMC2.MANIFEST).resolve() == m2p.resolve() and Path(CMC2.CODE_DEPS["closure_manifest"]).resolve() == m2p.resolve()
    assert Path(CMC1.MANIFEST).resolve() == m1p.resolve()
    assert m1[TEST_DEPS["combo_v1_1"]] == CMC2.V1_1_SHA == RG.sha256_file(ROOT / TEST_DEPS["combo_v1_1"])
    assert CMC2.CODE_DEPS["runguard"] == CMC1.CODE_DEPS["runguard"]


def test_runner_key_and_arch_ok_mandatory(monkeypatch):
    assert Path(CMC2.__file__).stem == "alpha_combo_marginal_v1_2"                 # → ok key runner_sha256_alpha_combo_marginal_v1_2
    monkeypatch.setattr(sys, "argv", ["alpha_combo_marginal_v1_2.py", "some_leaf"])
    with pytest.raises(SystemExit):
        CMC2._cli()


# ======================= nothing outside the pinned set was loaded =======================
def test_only_pinned_project_modules_loaded():
    allowed = TEST_MODULES | {str(Path(__file__).resolve().relative_to(ROOT))}
    loaded = set()
    for mm in list(sys.modules.values()):
        f = getattr(mm, "__file__", None)
        if not f: continue
        try: loaded.add(str(Path(f).resolve().relative_to(ROOT)))
        except ValueError: pass
    assert loaded <= allowed, sorted(loaded - allowed)
