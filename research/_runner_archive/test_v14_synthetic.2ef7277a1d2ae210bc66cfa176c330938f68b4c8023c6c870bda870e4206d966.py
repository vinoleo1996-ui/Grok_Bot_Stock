#!/usr/bin/env python3
"""Synthetic-data self-test of the Core v1.4 runner functions (Arch review db781708 §6; ARCH_RUN_AUTH_SELFTEST_SPEC_ZH.md 1aa43bdd;
主 Agent E-2 ruling 2026-10-18 01:59 ET). r2 of this file (Arch r2 review f9edf4a3 P2-4, P3-3, P3-9; CLARIFY-2 §8 cases).
live=false, promotion=false. NOT EVIDENCE: passing changes no .ok precondition. New bytes = new sha: the selftest .ok 33ef1df9
(which pins the previous T 7176f974 and R 3df05b4b) no longer applies; a new selftest .ok from Arch is required.

Gate FIRST (before importing anything under test): ok_runner_pin.enforce(modes=["selftest"]) against
  output/strategy_optimizer/core_x2/ARCH_RUN_AUTH_SELFTEST_v1_4.ok   (Arch writes it; Strategy never creates it)
plus the self-checks ok_runner_pin does not do yet (spec §4/§9): scope=selftest, allow_real_data=false, every other allow_*
explicitly false, out_dir = mkdtemp or /tmp/<tag>, signed_et / expires_et tz-aware ISO8601, signed_et not in the future (P3-9),
not expired, no BOM, LF only.

Isolation (P2-4): synthetic data only. After the gate:
  - an audit hook (paths via os.path.realpath, so symlinks cannot bypass it) refuses any open() under data/ or output/, any open
    for writing inside the repo, and os.mkdir / os.rename (incl. os.replace) / os.remove (incl. os.unlink) / os.rmdir / os.link /
    os.symlink / os.truncate / os.chmod / os.chown / shutil.copyfile / copytree / rmtree / make_archive / unpack_archive /
    chown targeting the repo;
  - Arrow native IO (which does NOT raise Python 'open' audit events: pq.read_table, pa.memory_map, ParquetWriter, ...) is wrapped:
    every pyarrow entry point listed in ARROW_WRAPS checks its path argument(s) with the same realpath rule before calling through;
  - C.prepare_day / load_daily_basic_window / load_pool / load_sw_map / month_ends, R._open_days and R.load_v13_eq100 are replaced
    by functions that raise. Never calls R.main / R.run_v14 / R.preflight. All writes go to the .ok's out_dir only.

Run command (Arch §6 / P3-3; qlvenv: py3.12.14, numpy 2.5.3, pyarrow 25.0.1 — the real run uses .venv_opt py3.13.5 / numpy 2.5.4 /
pyarrow 26.0.0, so a pass here says nothing about .venv_opt behaviour; serial, no concurrent research process):
  cd /workspace/QuantLab && PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python \
      -m pytest research/tests_v1_4/test_v14_synthetic.py -q -p no:cacheprovider --noconftest
"""
from __future__ import annotations
import os, re, sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OK_PATH = ROOT / "output/strategy_optimizer/core_x2/ARCH_RUN_AUTH_SELFTEST_v1_4.ok"
DEPS = {   # spec §2: one dep_sha256_<key> per module under test, incl. the project modules it imports
    "runner_v1_4": ROOT / "research/optimizer_core_x2_run_v1_4.py",
    "core_v1_1": ROOT / "research/optimizer_core_v1_1.py",
    "calib_sealed": ROOT / "research/optimizer_lambda_calib_sealed.py",
    "ok_runner_pin": ROOT / "scripts_eng/ok_runner_pin.py",
}
KNOWN_ALLOW_FALSE = ("allow_real_data", "allow_dryrun", "allow_full", "allow_smoke", "allow_diagnostic", "allow_disclosure_only",
                     "allow_equiv_check", "allow_mocktest")

sys.path.insert(0, str(ROOT / "scripts_eng"))
from ok_runner_pin import enforce, parse_ok  # noqa: E402
_G = enforce(__file__, [OK_PATH], modes=["selftest"], deps={k: str(v) for k, v in DEPS.items()})


def _selftest_selfcheck(path):
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"): raise SystemExit("REFUSED (selftest): .ok has a BOM")
    if b"\r" in raw: raise SystemExit("REFUSED (selftest): .ok must use LF line endings")
    kv = parse_ok(path)
    if kv.get("format") != "quantlab_run_auth_v1": raise SystemExit(f"REFUSED (selftest): format={kv.get('format')!r}")
    if kv.get("signed_by", "").lower() != "arch": raise SystemExit("REFUSED (selftest): signed_by must be arch")
    if kv.get("scope") != "selftest": raise SystemExit(f"REFUSED (selftest): scope={kv.get('scope')!r}, must be selftest")
    if kv.get("allow_selftest") != "true": raise SystemExit("REFUSED (selftest): allow_selftest must be exactly true")
    for k in KNOWN_ALLOW_FALSE:
        if kv.get(k) != "false": raise SystemExit(f"REFUSED (selftest): {k} must be explicitly false (found {kv.get(k)!r})")
    for k, v in kv.items():
        if k.startswith("allow_") and k != "allow_selftest" and v != "false":
            raise SystemExit(f"REFUSED (selftest): {k}={v!r}; every allow_* except allow_selftest must be false")
    if kv.get("live") != "false" or kv.get("promotion") != "false": raise SystemExit("REFUSED (selftest): live/promotion must be false")
    ts = {}
    for k in ("signed_et", "expires_et"):
        try:
            t = datetime.fromisoformat(kv.get(k, ""))
        except ValueError:
            raise SystemExit(f"REFUSED (selftest): {k} is not ISO8601")
        if t.tzinfo is None: raise SystemExit(f"REFUSED (selftest): {k} must carry a timezone")
        ts[k] = t
    now = datetime.now().astimezone()
    if ts["signed_et"] > now: raise SystemExit("REFUSED (selftest): signed_et is in the future (Arch P3-9)")
    if now >= ts["expires_et"]: raise SystemExit("REFUSED (selftest): .ok expired")
    od = kv.get("out_dir", "")
    if od == "mkdtemp":
        import tempfile
        out = Path(tempfile.mkdtemp(prefix="v14_selftest_"))
    elif re.fullmatch(r"/tmp/[A-Za-z0-9_.\-]+", od):
        out = Path(od)
        if out.exists() and any(out.iterdir()): raise SystemExit(f"REFUSED (selftest): out_dir {out} not empty")
        out.mkdir(parents=True, exist_ok=True)
    else:
        raise SystemExit(f"REFUSED (selftest): out_dir={od!r}; only mkdtemp or /tmp/<tag> allowed")
    if os.path.realpath(ROOT) in [os.path.realpath(x) for x in [out, *out.resolve().parents]]:
        raise SystemExit("REFUSED (selftest): out_dir inside the repo")
    return kv, Path(os.path.realpath(out))


_KV, OUT = _selftest_selfcheck(OK_PATH)
(OUT / "NOT_EVIDENCE.md").write_text("synthetic self-test scratch; not evidence; delete after the run (spec §7)\n", encoding="utf-8")

# ---- isolation (P2-4): realpath everywhere ----
_ROOT_R = os.path.realpath(ROOT)
_BLOCK_ALL = [os.path.realpath(ROOT / "data"), os.path.realpath(ROOT / "output")]   # no read, no write


def _under(rp, base):
    return rp == base or rp.startswith(base + os.sep)


def _check_path(p, write, what):
    """Refuse real data/output (read or write) and any write inside the repo. p: str / bytes / PathLike."""
    if isinstance(p, bytes): p = p.decode(errors="replace")
    rp = os.path.realpath(os.fspath(p))
    for b in _BLOCK_ALL:
        if _under(rp, b): raise PermissionError(f"selftest isolation: {what} of {rp} refused (real data/output)")
    if write and _under(rp, _ROOT_R): raise PermissionError(f"selftest isolation: {what} (write) inside repo refused: {rp}")


def _is_pathlike(x):
    return isinstance(x, (str, bytes, os.PathLike))


# audit event -> (indices of path args that are WRITE targets, indices of path args that are READ sources)
_FS_EVENTS = {"os.mkdir": ((0,), ()), "os.rename": ((0, 1), ()), "os.remove": ((0,), ()), "os.rmdir": ((0,), ()),
              "os.link": ((1,), (0,)), "os.symlink": ((1,), ()), "os.truncate": ((0,), ()), "os.chmod": ((0,), ()),
              "os.chown": ((0,), ()), "os.utime": ((0,), ()), "shutil.copyfile": ((1,), (0,)), "shutil.copymode": ((1,), (0,)),
              "shutil.copystat": ((1,), (0,)), "shutil.copytree": ((1,), (0,)), "shutil.rmtree": ((0,), ()),
              "shutil.chown": ((0,), ()), "shutil.make_archive": ((0,), ()), "shutil.unpack_archive": ((1,), (0,))}


def _audit(event, args):
    if event == "open":
        if not args: return
        p = args[0]
        if not _is_pathlike(p): return
        mode = args[1] if len(args) > 1 and isinstance(args[1], str) else "r"
        flags = args[2] if len(args) > 2 and isinstance(args[2], int) else 0
        writing = any(c in mode for c in "wax+") or bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
        _check_path(p, writing, "open")
        return
    spec = _FS_EVENTS.get(event)
    if spec is None: return
    wr, rd = spec
    for i in wr:
        if i < len(args) and _is_pathlike(args[i]): _check_path(args[i], True, event)
    for i in rd:
        if i < len(args) and _is_pathlike(args[i]): _check_path(args[i], False, event)


sys.addaudithook(_audit)

# ---- Arrow native IO wrappers (Arch r2 §5: these do not raise 'open' audit events) ----
import pyarrow as pa  # noqa: E402
import pyarrow.parquet as pq  # noqa: E402
import pyarrow.dataset as pads  # noqa: E402
import pyarrow.feather as pafeather  # noqa: E402
import pyarrow.csv as pacsv  # noqa: E402
import pyarrow.json as pajson  # noqa: E402
import pyarrow.ipc as paipc  # noqa: E402

# (module, attribute, positional index of the path argument, keyword names, write?)   write may be "mode" = decided by mode arg
ARROW_WRAPS = (
    (pq, "read_table", 0, ("source",), False), (pq, "read_pandas", 0, ("source",), False), (pq, "ParquetFile", 0, ("source",), False),
    (pq, "ParquetDataset", 0, ("path_or_paths",), False), (pq, "read_schema", 0, ("where",), False),
    (pq, "read_metadata", 0, ("where",), False), (pq, "ParquetWriter", 0, ("where",), True), (pq, "write_table", 1, ("where",), True),
    (pq, "write_to_dataset", 1, ("root_path",), True),
    (pa, "memory_map", 0, ("path",), "mode"), (pa, "create_memory_map", 0, ("path",), True), (pa, "OSFile", 0, ("path",), "mode"),
    (pa, "input_stream", 0, ("source",), False), (pa, "output_stream", 0, ("source",), True),
    (pads, "dataset", 0, ("source",), False), (pads, "write_dataset", 1, ("base_dir",), True),
    (pafeather, "read_table", 0, ("source",), False), (pafeather, "read_feather", 0, ("source",), False),
    (pafeather, "write_feather", 1, ("dest",), True),
    (pacsv, "read_csv", 0, ("input_file",), False), (pacsv, "open_csv", 0, ("input_file",), False),
    (pacsv, "write_csv", 1, ("output_file",), True), (pacsv, "CSVWriter", 0, ("sink",), True),
    (pajson, "read_json", 0, ("input_file",), False),
    (paipc, "open_file", 0, ("source",), False), (paipc, "open_stream", 0, ("source",), False),
    (paipc, "new_file", 0, ("sink",), True), (paipc, "new_stream", 0, ("sink",), True),
)


def _paths_in(x):
    if _is_pathlike(x): return [x]
    if isinstance(x, (list, tuple)): return [y for y in x if _is_pathlike(y)]
    return []


def _wrap(mod, name, idx, kws, write):
    orig = getattr(mod, name)   # AttributeError here = this pyarrow lacks the entry point -> the self-test refuses to run

    def wrapped(*a, **k):
        target = a[idx] if len(a) > idx else next((k[n] for n in kws if n in k), None)
        if write == "mode":
            mode = a[idx + 1] if len(a) > idx + 1 and isinstance(a[idx + 1], str) else k.get("mode", "r")
            w = mode not in ("r", "rb")
        else:
            w = bool(write)
        for p in _paths_in(target): _check_path(p, w, f"{mod.__name__}.{name}")
        return orig(*a, **k)
    wrapped.__wrapped__ = orig; wrapped.__name__ = name; wrapped.__qualname__ = f"selftest_guard.{name}"
    setattr(mod, name, wrapped)
    return f"{mod.__name__}.{name}"


WRAPPED = [_wrap(*s) for s in ARROW_WRAPS]
(OUT / "arrow_wrapped.txt").write_text("\n".join(WRAPPED) + "\n", encoding="utf-8")   # receipt: which entry points are guarded

# ---- gate passed, isolation installed: only now import the modules under test ----
import shutil  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import pytest  # noqa: E402
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "research"))
import optimizer_core_x2_run_v1_4 as R  # noqa: E402
C, V = R.C, R.V


def _forbidden(name):
    def f(*a, **k): raise RuntimeError(f"selftest isolation: {name} must not be called (real data)")
    return f


for _n in ("prepare_day", "load_daily_basic_window", "load_pool", "load_sw_map", "month_ends"):
    setattr(C, _n, _forbidden(f"C.{_n}"))
R._open_days = _forbidden("R._open_days"); R.load_v13_eq100 = _forbidden("R.load_v13_eq100")

A60, A100 = 600_000, 1_000_000
SV1, SV2 = R.SLEEVES[0][0], R.SLEEVES[1][0]


# ---------------------------------------------------------------- synthetic data
def synth_D(n_main=100, n_star=20, n_ind=5, seed=7):
    rng = np.random.default_rng(seed)
    names = [f"{600000 + i:06d}.SH" for i in range(n_main)] + [f"{688000 + i:06d}.SH" for i in range(n_star)]
    n = len(names)
    wb = pd.Series(rng.uniform(0.5, 1.5, n), index=names); wb = wb / wb.sum()
    D = {"alpha": pd.Series(rng.normal(0, 1, n), index=names), "wb": wb,
         "ln_mcap": pd.Series(rng.normal(23.0, 1.0, n), index=names),
         "industry": {nm: f"IND{k % n_ind}" for k, nm in enumerate(names)},
         "betas": pd.Series(1.0 + 0.2 * rng.normal(0, 1, n), index=names),
         "F": np.eye(n_ind) * 1e-4, "delta": np.full(n, 4e-4), "n": n}
    return D


def synth_px(D, seed=11):
    rng = np.random.default_rng(seed)
    px = {nm: float(np.round(rng.uniform(5.0, 40.0), 2)) for nm in D["alpha"].index}
    nm = list(D["alpha"].index)
    px[nm[0]] = 300.0      # 60万: sleeve ② T=28800 < 30000 <= sleeve ① T=36000 -> sleeve2_only
    px[nm[1]] = 400.0      # 60万: both sleeves excluded
    px[nm[2]] = 1500.0     # both tiers excluded
    px[nm[3]] = float("nan")   # no price: not excluded, cap = c_A
    return px


# ---------------------------------------------------------------- S1 / S5 arithmetic
def test_lot_cap_exact_division():
    assert R.lot_cap_lots_ex(0.06, 1.0, A60, 100, 36.0) == (10, False)


def test_lot_cap_float_noise_kept():
    T = 0.06 * 1.0 * A60; P = T / (100 * (10 - 1e-13))
    assert R.lot_cap_lots_ex(0.06, 1.0, A60, 100, P) == (10, False)


def test_lot_cap_eps_revert():
    T = 0.06 * 1.0 * A60; P = T / (100 * (10 - 1e-7))     # +ε would take a 10th lot beyond T·(1+1e-9) -> revert to 9
    m, rev = R.lot_cap_lots_ex(0.06, 1.0, A60, 100, P)
    assert (m, rev) == (9, True) and m * 100 * P <= T * (1 + R.STRICT_CAP_REL)


def test_lot_cap_too_expensive_is_zero():
    assert R.lot_cap_lots(0.06, 0.8, A60, 100, 400.0) == 0


def test_tier_context_s5_is_m0_and_invariants():
    D = synth_D(); px = synth_px(D); names = list(D["alpha"].index)
    for a in (A60, A100):
        ctx = R.tier_context(D, px, a); cA = C.NAME_CAP[a]
        assert ctx["pool"] == names and set(ctx["eps_revert"]) == {SV1, SV2}
        for i in names:
            r = ctx["rows"][i]
            if not np.isfinite(r["price"]):
                assert r["prefilter"] == "no_price" and r["in_cand"] and r["cap_lot"] == cA
                continue
            assert r["in_cand"] == all(r["m"][sv] > 0 for sv in (SV1, SV2))      # P3-2: S5 excluded <=> some m = 0
            if r["in_cand"]:
                assert cA / 2 - 1e-12 <= r["cap_lot"] <= cA * (1 + R.STRICT_CAP_REL) + 1e-12
            else:
                assert r["cap_lot"] == 0.0
        assert ctx["rows"][names[1]]["prefilter"] == ("both" if a == A60 else "none")
        assert ctx["rows"][names[2]]["prefilter"] == "both"
    assert R.tier_context(D, px, A60)["rows"][names[0]]["prefilter"] == "sleeve2_only"


def test_benchmark_independent_of_prefilter():
    D = synth_D(); px = synth_px(D); low = {k: 10.0 for k in px}
    a, b = R.tier_context(D, px, A60), R.tier_context(D, low, A60)
    assert a["sty"]["bb"] == b["sty"]["bb"] and a["sty"]["zb"] == b["sty"]["zb"] and a["pool"] == b["pool"]
    assert len(a["cand"]) < len(b["cand"])


# ---------------------------------------------------------------- AMEND-1 snapshot checks
def _ctx_book(a=A60, Bs=1.0):
    D = synth_D(); px = synth_px(D); ctx = R.tier_context(D, px, a); ctx["ind_map"] = D["industry"]
    held = [i for i in ctx["cand"] if np.isfinite(ctx["rows"][i]["price"])][:20]
    book = pd.Series({i: 0.04 * Bs for i in held})
    if Bs < 1.0: book[C.BALLAST] = 1.0 - Bs
    return D, ctx, book.sort_index()


@pytest.mark.parametrize("Bs", [1.0, 0.8])
def test_snapshot_passes_and_covers(Bs):
    D, ctx, book = _ctx_book(Bs=Bs)
    bp = R.book_exposures(book, Bs, ctx)["beta_port"]
    rows = R.build_pool_snapshot("2024-06-28", A60, SV1 if Bs == 1.0 else SV2, Bs, D, ctx, book, None, "ksel", 25, 25, bp)
    codes = {r["code"] for r in rows if r["selected"]}
    assert {R._code(i) for i, v in book.items() if v > 0} <= codes
    assert sum(1 for r in rows if r["in_pool"]) == len(ctx["pool"])
    assert abs(sum(r["q_final"] for r in rows) - 1.0) < 1e-9


def test_snapshot_raises_on_tampered_beta_port():
    D, ctx, book = _ctx_book()
    bp = R.book_exposures(book, 1.0, ctx)["beta_port"]
    with pytest.raises(RuntimeError, match="A3"):
        R.build_pool_snapshot("2024-06-28", A60, SV1, 1.0, D, ctx, book, None, "ksel", 25, 25, bp + 1e-3)


def test_snapshot_raises_on_tampered_wb():
    D, ctx, book = _ctx_book()
    bp = R.book_exposures(book, 1.0, ctx)["beta_port"]
    D2 = dict(D); D2["wb"] = D["wb"] * 1.01
    with pytest.raises(RuntimeError, match="A1"):
        R.build_pool_snapshot("2024-06-28", A60, SV1, 1.0, D2, ctx, book, None, "ksel", 25, 25, bp)


def test_snapshot_raises_on_negative_cash():
    D, ctx, book = _ctx_book()
    book = book * 1.5
    bp = R.book_exposures(book, 1.0, ctx)["beta_port"]
    with pytest.raises(RuntimeError, match="A3"):
        R.build_pool_snapshot("2024-06-28", A60, SV1, 1.0, D, ctx, book, None, "ksel", 25, 25, bp)


# ---------------------------------------------------------------- solve_tier (synthetic; structural assertions only)
def test_solve_tier_structure():
    D = synth_D(); px = synth_px(D); ctx = R.tier_context(D, px, A100); ctx["ind_map"] = D["industry"]
    res = R.solve_tier(D, px, A100, R.LAMBDA_RISK_FROZEN, R.LAMBDA_TURN_FROZEN, None, {SV1: None, SV2: None}, ctx)
    assert res["fail_stage"] in (None, "solve", "lot")
    assert (res["adopt"] is None) == (res["fail_stage"] is not None)
    if res["adopt"] is not None:
        assert res["adopt"]["hard_both"]
        for sv in (SV1, SV2):
            li = res["adopt"]["sleeves"][sv]["li"]
            for i, lots in li["q_final"].items():
                assert lots <= ctx["rows"][i]["m"][sv]                         # q_i ≤ m_i lots (S1 / §3.2)
    for att in res["attempts"]:
        if att["w"] is not None:
            assert all(float(att["w"][i]) <= ctx["rows"][i]["cap_lot"] + 1e-6 for i in att["w"].index)
    assert R._RSS["n_samples"] > 0                                            # P3-5 intraday sampling happened


# ---------------------------------------------------------------- run gate (temp .ok files under OUT only)
def _ts(hours):
    return (datetime.now().astimezone() + timedelta(hours=hours)).isoformat(timespec="seconds")


def _ok_text(**over):
    kv = {"format": "quantlab_run_auth_v1", "version": "v1_4", "signed_by": "arch", "signed_et": _ts(-1), "expires_et": _ts(+12),
          "allow_full": "true", "allow_smoke": "false", "allow_equiv_check": "true", "live": "false", "promotion": "false",
          "python_exe": "/workspace/QuantLab/.venv_opt/bin/python", "out_dir": R.OUT_FULL_REL, "equiv_root": R.EQUIV_ROOT_REL}
    for k in R.AUTH_SHA_KEYS_V14: kv[k] = "0" * 64
    kv.update(over)
    return "".join(f"{k}={v}\n" for k, v in kv.items() if v is not None)


def _write(name, text):
    p = OUT / name; p.write_text(text, encoding="utf-8"); return p


def test_whitelist_covers_closure_and_v13_keys():
    assert len(R.NT_CLOSURE_FILES) == 11 and len(set(R.NT_CLOSURE_FILES)) == 11
    assert "research/ai_debate_memory_runner.py" in R.NT_CLOSURE_FILES
    for k in list(R.PINNED_INPUTS) + ["expires_et", "clarify2_sha256", "clarify_sha256"]:
        assert k in R.AUTH_ALLOWED_V14 and k in R.AUTH_REQUIRED_V14
    assert set(R.AUTH_ALLOWED_V14) == set(R.AUTH_REQUIRED_V14)


def test_gate_valid_parses():
    kv = R.parse_run_auth_v14(_write("ok_valid.ok", "# comment line\n\n" + _ok_text()))
    assert kv["live"] is False and kv["promotion"] is False and kv["allow_full"] is True


@pytest.mark.parametrize("label,text", [
    ("bom", "\ufeff" + _ok_text()),
    ("crlf", _ok_text().replace("\n", "\r\n")),
    ("dup", _ok_text() + "allow_full=false\n"),
    ("inline_comment", _ok_text(allow_full="true # x")),
    ("trailing_blank", _ok_text(python_exe="/workspace/QuantLab/.venv_opt/bin/python ")),
    ("unknown_key", _ok_text() + "allow_mocktest=false\n"),
    ("unknown_key2", _ok_text() + "note=hello\n"),
    ("malformed_line", _ok_text() + "THIS IS NOT A KEY\n"),
    ("malformed_upper_key", _ok_text() + "Live=false\n"),
    ("indented_key", _ok_text() + " live=false\n"),
    ("missing_live", _ok_text(live=None)),
    ("live_true", _ok_text(live="true")),
    ("promotion_upper", _ok_text(promotion="False")),
    ("signed_by_upper", _ok_text(signed_by="Arch")),
    ("short_sha", _ok_text(daily_basic_sha256="f6bbf9e5")),
    ("missing_dep_key", _ok_text(dep_nontextbook_sha256=None)),
    ("missing_closure_key", _ok_text(nt_ai_debate_memory_runner_sha256=None)),
    ("missing_v13_key", _ok_text(v13_w_eq100_60w_sha256=None)),
    ("missing_clarify2", _ok_text(clarify2_sha256=None)),
    ("missing_expires", _ok_text(expires_et=None)),
    ("expired", _ok_text(expires_et=_ts(-0.5))),
    ("expires_before_signed", _ok_text(signed_et=_ts(-1), expires_et=_ts(-2))),
    ("signed_in_future", _ok_text(signed_et=_ts(+1))),
    ("no_tz", _ok_text(expires_et="2099-01-01T00:00:00")),
    ("not_iso", _ok_text(expires_et="tomorrow")),
    ("relative_python", _ok_text(python_exe=".venv_opt/bin/python")),
    ("version", _ok_text(version="v1_3")),
])
def test_gate_rejects(label, text):
    with pytest.raises(SystemExit):
        R.parse_run_auth_v14(_write(f"ok_{label}.ok", text))


def test_gate_missing_file():
    with pytest.raises(SystemExit):
        R.parse_run_auth_v14(OUT / "does_not_exist.ok")


def _kv(**over):
    return R.parse_run_auth_v14(_write("ok_tmp.ok", _ok_text(**over)))


def test_enforce_rejects_smoke_sha_and_dirs():
    cs = {"files": {R.RUNNER_REL: "0" * 64}, "combined": "0" * 64}
    with pytest.raises(SystemExit):
        R.enforce_run_auth_v14(_kv(allow_smoke="true"), cs, "full", "a" * 64, "a" * 64)
    with pytest.raises(SystemExit):
        R.enforce_run_auth_v14(_kv(), cs, "full", "a" * 64, "b" * 64)            # .ok sha != --auth-sha256
    with pytest.raises(SystemExit):
        R.enforce_run_auth_v14(_kv(), cs, "full", "a" * 64, "a" * 63)
    with pytest.raises(SystemExit):
        R.enforce_run_auth_v14(_kv(out_dir="output/strategy_optimizer/core_x2/v1_3"), cs, "full", "a" * 64, "a" * 64)
    with pytest.raises(SystemExit):
        R.enforce_run_auth_v14(_kv(equiv_root="output/x"), cs, "full", "a" * 64, "a" * 64)


def test_clarify2_unpinned_refuses_before_any_file_access():
    assert R.CLARIFY2_SHA256 == "" or re.fullmatch(r"[0-9a-f]{64}", R.CLARIFY2_SHA256)
    if R.CLARIFY2_SHA256 == "":
        with pytest.raises(SystemExit, match="CLARIFY-2 is not pinned"):
            R.check_clarify2({"clarify2_sha256": "0" * 64}, "v1_4")


def test_determinism_env_and_interpreter():
    R.check_determinism_env(dict(R.DETERMINISM_ENV))
    with pytest.raises(SystemExit):
        R.check_determinism_env({**R.DETERMINISM_ENV, "OMP_NUM_THREADS": "4"})
    with pytest.raises(SystemExit):
        R.check_determinism_env({})
    R.check_interpreter({"python_exe": sys.executable}, environ={})            # qlvenv: pyvenv.cfg present, packages under prefix
    with pytest.raises(SystemExit):
        R.check_interpreter({"python_exe": "/nonexistent/bin/python"}, environ={})
    for k in R.FORBIDDEN_PY_ENV:
        with pytest.raises(SystemExit):
            R.check_interpreter({"python_exe": sys.executable}, environ={k: "/x"})


def test_interpreter_requires_pyvenv_cfg():
    fake = OUT / "fakevenv" / "bin"; fake.mkdir(parents=True)
    os.symlink(os.path.realpath(sys.executable), fake / "python")            # same realpath, but no fakevenv/pyvenv.cfg
    with pytest.raises(SystemExit, match="pyvenv.cfg"):
        R.check_interpreter({"python_exe": str(fake / "python")}, environ={})


def test_out_dir_rules():
    with pytest.raises(SystemExit):
        R.check_out_dir(OUT, "full", True)                 # not the code constant
    with pytest.raises(SystemExit):
        R.check_out_dir(R.OUT_FULL, "full", False)         # full run must write the snapshot


def test_lock_o_excl():
    p = OUT / "test.lock"
    R.acquire_lock(p, {"pid": os.getpid()})
    assert '"pid"' in p.read_text(encoding="utf-8")
    with pytest.raises(SystemExit):
        R.acquire_lock(p, {"pid": os.getpid()})


def test_exclusive_writes():
    p = OUT / "x_summary.json"
    R.write_x_atomic(p, "{}\n")
    assert p.read_text(encoding="utf-8") == "{}\n" and not (OUT / "x_summary.json.tmp").exists()
    with pytest.raises(FileExistsError):
        R.write_x_atomic(p, "{\"again\": 1}\n")
    with pytest.raises(FileExistsError):
        R.write_x(p, "overwrite\n")
    assert p.read_text(encoding="utf-8") == "{}\n"


def test_closure_combined_and_loaded_modules():
    fake = {k: f"{n:064x}" for n, k in enumerate(R.PINNED_INPUTS)}
    c1 = R.nt_closure_combined(fake)
    assert re.fullmatch(r"[0-9a-f]{64}", c1) and c1 == R.nt_closure_combined(dict(fake))
    fake2 = dict(fake); fake2["nt_ai_debate_memory_runner_sha256"] = "f" * 64
    assert R.nt_closure_combined(fake2) != c1
    mods = R.loaded_project_modules()
    assert R.RUNNER_REL in mods and "research/g1g5_nontextbook_weights.py" not in mods   # selftest never loads nontextbook


# ---------------------------------------------------------------- writers
def test_writers_roundtrip():
    d = OUT / "writers"; d.mkdir(exist_ok=True)
    W = R.Writers(d)
    row = {f.name: None for f in R.SNAP_SCHEMA}; row.update({"date": "2024-06-28", "tier": A60, "code": "CASH", "q_final": 0.1})
    W.parquet("snap.parquet", R.SNAP_SCHEMA, [row]); W.parquet("snap.parquet", R.SNAP_SCHEMA, [row])
    arow = {f.name: None for f in R.ATT_SCHEMA}; arow.update({"date": "2024-06-28", "aum": A60, "sleeve": "SOLVER"})
    W.parquet("att.parquet", R.ATT_SCHEMA, [arow])
    W.csv("x.csv", [{"a": 1, "b": None}], ["a", "b"]); W.csv("x.csv", [{"a": 2, "b": 3}], ["a", "b"])
    W.jsonl("t.jsonl", [{"k": 1}]); W.close()
    assert pq.read_table(str(d / "snap.parquet")).num_rows == 2 and pq.read_schema(str(d / "snap.parquet")) == R.SNAP_SCHEMA
    assert pq.read_table(str(d / "att.parquet")).num_rows == 1
    lines = (d / "x.csv").read_text().splitlines()
    assert len(lines) == 3 and lines[0] == "a,b"                               # header once, then appended rows


# ---------------------------------------------------------------- §8 CLARIFY-1 + CLARIFY-2, stop rule, rescue
X2_DATES = [str(d.date()) for d in pd.date_range("2024-06-28", periods=29, freq="ME")][:28] + ["2026-10-09"]


def _disc(override):
    rows = []
    for a in (A60, A100):
        for sv in (SV1, SV2):
            for dt in ["2024-01-31", "2024-02-29"] + X2_DATES:
                r = {c: None for c in R.DISC_COLS}
                r.update({"date": dt, "window": "X2" if dt >= R.X2[0] else "SEALED", "aum": a, "sleeve": sv, "status": "OK",
                          "K_sel": 25, "k_final": 25, "s3_used": False, "s3_trigger": "none", "s3_rescued_from_hard": False,
                          "s3_rescued_from_cash": False, "lot_fail_reason": "", "cash": 0.01, "neff_solver": 22.0, "neff_lot": 21.0,
                          "turn_solver_gt40": False, "turn_lot_gt40": False, "clamp_count": 0, "eps_revert_count": 0})
                r.update(override(a, sv, dt) or {})
                rows.append(r)
    return pd.DataFrame(rows, columns=R.DISC_COLS)


def test_x2_dates_29():
    assert len(X2_DATES) == 29 and all(d >= R.X2[0] for d in X2_DATES)


def test_s8_both_same_day_judges_no_exemption():
    cash_days = set(X2_DATES[:6])
    disc = _disc(lambda a, sv, dt: ({"status": "LOT_CASH_GT2", "cash": 0.03} if (a == A100 and sv == SV2 and dt in cash_days) else None))
    s8 = R.post_run_disclosures(disc)["s8"]
    t = s8["per_tier"][str(A100)]
    assert (t["sleeve_A_strict_days"], t["sleeve_B_strict_days"], t["both_strict_same_day_days"], t["denominator"]) == (29, 23, 23, 29)
    assert len(t["daily"]) == 29 and t["n_valid_days"] == 29 and s8["judgeable"] is True
    assert s8["verdict_100w_still_infeasible"] is True and s8["flag_60w_also_below_80"] is False
    assert s8["per_tier"][str(A60)]["both_strict_same_day_days"] == 29
    assert "needs_main_agent_ruling" not in s8 and all("needs_main_agent_ruling" not in v for v in s8["per_tier"].values())


def test_s8_disjoint_bad_days_count_on_both():
    disc = _disc(lambda a, sv, dt: ({"status": "LOT_CASH_GT2", "cash": 0.03}
                                    if a == A60 and ((sv == SV1 and dt in X2_DATES[0:3]) or (sv == SV2 and dt in X2_DATES[10:13])) else None))
    t = R.post_run_disclosures(disc)["s8"]["per_tier"][str(A60)]
    assert (t["sleeve_A_strict_days"], t["sleeve_B_strict_days"], t["both_strict_same_day_days"]) == (26, 26, 23)
    assert t["both_below_threshold"] is True


def test_s8_k3_triggers_even_above_threshold():
    disc = _disc(lambda a, sv, dt: ({"status": "INFEASIBLE", "fail_stage": "solve"} if a == A100 and dt in X2_DATES[5:8] else None))
    s8 = R.post_run_disclosures(disc)["s8"]
    assert s8["per_tier"][str(A100)]["both_strict_same_day_days"] == 26
    assert s8["per_tier"][str(A100)]["k3_triggered_x2"] and s8["verdict_100w_still_infeasible"] is True


def test_s8_clarify2_nodata_in_denominator_absolute_24():
    nod = set(X2_DATES[10:13])            # 3 no-data days on 100万: both = 26 of 29 -> not below 24; control 0.8*26 = 20.8
    s8 = R.post_run_disclosures(_disc(lambda a, sv, dt: ({"status": "NO_DATA_CARRY"} if a == A100 and dt in nod else None)))["s8"]
    t = s8["per_tier"][str(A100)]
    assert t["denominator"] == 29 and t["n_valid_days"] == 26 and t["both_strict_same_day_days"] == 26
    assert t["n_not_provably_feasible_days"] == 3 and [x["date"] for x in t["not_provably_feasible_days"]] == sorted(nod)
    assert all(x["reasons"] for x in t["not_provably_feasible_days"])
    assert t["both_below_threshold"] is False and t["valid_days_lt_29_disclosure"] is True and s8["judgeable"] is True
    assert abs(t["control_80pct_of_valid_days"]["threshold"] - 20.8) < 1e-12 and t["control_80pct_of_valid_days"]["below"] is False
    assert s8["verdict_100w_still_infeasible"] is False


def test_s8_clarify2_nodata_pushes_below_24():
    nod = set(X2_DATES[0:6])              # 6 no-data days: both = 23 < 24 -> escalate although 23 >= 0.8*23 (control says no)
    s8 = R.post_run_disclosures(_disc(lambda a, sv, dt: ({"status": "NO_DATA_CARRY"} if a == A100 and dt in nod else None)))["s8"]
    t = s8["per_tier"][str(A100)]
    assert t["both_strict_same_day_days"] == 23 and t["both_below_threshold"] is True
    assert t["control_80pct_of_valid_days"]["below"] is False                 # disclosure-only control never changes the verdict
    assert t["valid_days_lt_24_direct_escalation"] is True and s8["verdict_100w_still_infeasible"] is True


def test_s8_missing_row_counts_not_provable_and_still_judged():
    disc = _disc(lambda a, sv, dt: None)
    disc = disc[~((disc["aum"] == A100) & (disc["sleeve"] == SV2) & (disc["date"] == X2_DATES[-1]))]
    s8 = R.post_run_disclosures(disc)["s8"]
    t = s8["per_tier"][str(A100)]
    assert s8["judgeable"] is True and t["both_strict_same_day_days"] == 28 and t["n_valid_days"] == 28
    assert t["not_provably_feasible_days"][0]["date"] == X2_DATES[-1] and s8["verdict_100w_still_infeasible"] is False


def test_stop_rule_monthly_and_nodata():
    def ov(a, sv, dt):
        if a == A60 and dt in X2_DATES[3:5]: return {"status": "NO_DATA_CARRY"}
        if a == A60 and dt in (X2_DATES[2], X2_DATES[5]): return {"status": "LOT_HARD_FAIL", "lot_fail_reason": "beta", "fail_stage": "lot"}
        return None
    rep = R.post_run_disclosures(_disc(ov))
    ps = rep["stop_rule_x2"]["per_sleeve"][f"{A60}|{SV1}"]
    assert ps["n_fail"] == 2 and ps["k3_trigger_date"] is None and len(ps["nodata_runs_ge2_report"]) == 1
    assert ps["lot_fail_reasons"] == {"beta": 2}
    assert rep["s8"]["per_tier"][str(A60)]["n_not_provably_feasible_days"] == 2


def test_rescue_positions_and_counts():
    def ov(a, sv, dt):
        if a == A100 and dt == X2_DATES[1]: return {"s3_used": True, "s3_trigger": "hard", "s3_rescued_from_hard": True, "k_final": 27}
        if a == A100 and dt in (X2_DATES[0], X2_DATES[2]): return {"status": "LOT_HARD_FAIL", "fail_stage": "lot", "lot_fail_reason": "size"}
        if a == A60 and dt == X2_DATES[4]: return {"clamp_count": 2, "eps_revert_count": 1}
        return None
    rep = R.post_run_disclosures(_disc(ov))
    rp = rep["s3_rescue"][f"{A100}|{SV1}"]
    assert rp["n_rescued_hard"] == 1 and rp["s3_rescued_from_hard"][0]["position"] == "mid"
    assert rp["counterfactual_k3_trigger_without_rescue"] == X2_DATES[2]
    assert rep["clamp"][f"{A60}|{SV1}"] == [{"date": X2_DATES[4], "clamp_count": 2}]
    assert rep["eps_revert"][f"{A60}|{SV1}"] == {"total": 1, "days_gt0": 1}


# ---------------------------------------------------------------- isolation self-checks (P2-4) + RSS
DATA_P = str(ROOT / "data" / "v2" / "_selftest_nonexistent.parquet")       # never exists; refused before any syscall
REPO_W = str(ROOT / "research" / "_selftest_should_not_exist.bin")


def test_isolation_blocks_real_data():
    with pytest.raises(PermissionError):
        open(ROOT / "data" / "v2" / "valuation" / "daily_basic_full_tushare.parquet", "rb")
    with pytest.raises(PermissionError):
        open(REPO_W, "w")
    with pytest.raises(RuntimeError):
        C.prepare_day(pd.Timestamp("2024-06-28"))
    with pytest.raises(RuntimeError):
        R._open_days()


def test_arrow_entry_points_all_wrapped():
    assert len(WRAPPED) == len(ARROW_WRAPS)
    for mod, name, *_ in ARROW_WRAPS:
        assert getattr(getattr(mod, name), "__wrapped__", None) is not None, f"{mod.__name__}.{name} not wrapped"
    assert R.pq is pq and getattr(R.pq.ParquetWriter, "__wrapped__", None) is not None   # R and C see the guarded module


@pytest.mark.parametrize("spec", ARROW_WRAPS, ids=[f"{m.__name__}.{n}" for m, n, *_ in ARROW_WRAPS])
def test_arrow_wrappers_refuse(spec):
    mod, name, idx, kws, write = spec
    f = getattr(mod, name)
    args = [None] * idx
    with pytest.raises(PermissionError):                       # real data: refused for read AND write entry points
        f(*args, DATA_P)
    with pytest.raises(PermissionError):                       # same via keyword
        f(*args, **{kws[0]: DATA_P}) if idx == 0 else f(None, **{kws[0]: DATA_P})
    if write is True:
        with pytest.raises(PermissionError):                   # writes inside the repo refused
            f(*args, REPO_W)
    if write == "mode":
        with pytest.raises(PermissionError):
            f(REPO_W, "w")


def test_arrow_list_of_paths_refused():
    with pytest.raises(PermissionError):
        pq.ParquetDataset([str(OUT / "a.parquet"), DATA_P])
    with pytest.raises(PermissionError):
        pads.dataset([DATA_P])


def test_symlink_cannot_bypass_realpath():
    lnk = OUT / "lnk_data"
    os.symlink(str(ROOT / "data"), lnk)                        # creating the link writes only in OUT (allowed)
    with pytest.raises(PermissionError):
        open(lnk / "v2" / "valuation" / "daily_basic_full_tushare.parquet", "rb")
    with pytest.raises(PermissionError):
        pq.read_table(str(lnk / "v2" / "valuation" / "daily_basic_full_tushare.parquet"))
    with pytest.raises(PermissionError):
        pa.memory_map(str(lnk / "v2" / "valuation" / "daily_basic_full_tushare.parquet"))
    lnk_repo = OUT / "lnk_repo"
    os.symlink(str(ROOT / "research"), lnk_repo)
    with pytest.raises(PermissionError):
        open(lnk_repo / "_selftest_should_not_exist.txt", "w")
    with pytest.raises(PermissionError):
        pq.write_table(pa.table({"a": [1]}), str(lnk_repo / "_selftest_should_not_exist.parquet"))


def test_fs_mutations_in_repo_refused():
    src = OUT / "mv_src.txt"; src.write_text("x\n", encoding="utf-8")
    tgt = ROOT / "research" / "_selftest_should_not_exist"
    cases = [lambda: os.mkdir(tgt), lambda: os.makedirs(tgt / "sub"), lambda: (tgt).mkdir(),
             lambda: os.rename(src, tgt), lambda: os.replace(src, tgt), lambda: shutil.move(str(src), str(tgt)),
             lambda: os.remove(tgt), lambda: os.unlink(tgt), lambda: os.rmdir(tgt), lambda: shutil.rmtree(tgt),
             lambda: shutil.copyfile(src, tgt), lambda: shutil.copy(src, tgt), lambda: shutil.copytree(OUT / "writers", tgt),
             lambda: os.link(src, tgt), lambda: os.symlink(src, tgt), lambda: os.chmod(tgt, 0o644), lambda: os.truncate(tgt, 0),
             lambda: os.rename(src, ROOT / "output" / "_selftest_should_not_exist"),
             lambda: shutil.copyfile(ROOT / "data" / "v2" / "valuation" / "daily_basic_full_tushare.parquet", OUT / "stolen.parquet")]
    for k, fn in enumerate(cases):
        with pytest.raises(PermissionError):
            fn()
        assert src.exists(), f"case {k} moved the source"
    assert not tgt.exists() and not (OUT / "stolen.parquet").exists()


def test_fs_mutations_in_out_allowed():
    d = OUT / "mut"; os.mkdir(d); (d / "a").write_text("1", encoding="utf-8")
    os.replace(d / "a", d / "b"); os.remove(d / "b"); os.rmdir(d)
    assert not d.exists()


def test_zz_rss_budget():
    r = C.rss_mb()   # ru_maxrss high-water mark of this pytest process (/usr/bin/time is not installed on the box)
    (OUT / "peak_rss_mb.txt").write_text(f"{r:.1f}\n", encoding="utf-8")   # read it for the receipt before cleanup (spec §5)
    assert r < R.RSS_LIMIT_MB
